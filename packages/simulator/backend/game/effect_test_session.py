"""
Effect Test Session — manages per-user test state for the web-based effect tester.

Each connected socket gets its own EffectTestSession that tracks which card
is currently being tested and builds the appropriate game state.
"""

import copy
import html as html_module
import io
import json
import re
import sys
import traceback
from contextlib import redirect_stdout
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Ensure game-engine is on sys.path (manager.py already adds it; be safe)
_engine_path = Path(__file__).parent.parent.parent.parent / "game-engine"
if str(_engine_path) not in sys.path:
    sys.path.insert(0, str(_engine_path))

from optcg_engine.game_engine import GameState, Player
from optcg_engine.models.cards import Card
from optcg_engine.models.enums import GamePhase
from optcg_engine.effects.effect_registry import execute_hardcoded_effect, _hardcoded_effects

STATUS_FILE = _engine_path / "optcg_engine" / "effects" / "CARD_STATUS.md"
CARDS_JSON   = Path(__file__).parent.parent / "data" / "cards.json"


# ─────────────────────────────────────────────────────────────────
# Card factories (mirror CLI script helpers)
# ─────────────────────────────────────────────────────────────────

def _to_int(val) -> Optional[int]:
    if val is None:
        return None
    try:
        return int(val)
    except (TypeError, ValueError):
        return None


def _card(id, name, card_type, cost, power, colors, card_origin, *, rested=False) -> Card:
    c = Card(
        id=id, id_normal=id, name=name, card_type=card_type,
        cost=cost, power=power, counter=1000, colors=colors,
        life=None, effect="", image_link=None,
        attribute="Strike", card_origin=card_origin, trigger=None,
    )
    c.is_resting = rested
    c.attached_don = 0
    c.power_modifier = 0
    return c


def _seed_attached_don(player: Player, card: Card, count: int) -> None:
    """Seed attached DON while keeping the free DON pool/count consistent."""
    actual = min(max(count, 0), len(player.don_pool))
    card.attached_don = actual
    for _ in range(actual):
        if "active" in player.don_pool:
            idx = player.don_pool.index("active")
        elif player.don_pool:
            idx = len(player.don_pool) - 1
        else:
            break
        player.don_pool.pop(idx)
        player.don_pool.append("rested")


def _cost_area_don_pool(player: Player) -> List[str]:
    """Return only the free DON pool, excluding trailing attached DON."""
    attached_total = sum(getattr(c, "attached_don", 0) for c in player.cards_in_play)
    if getattr(player, "leader", None):
        attached_total += getattr(player.leader, "attached_don", 0)
    attached_total = min(attached_total, len(player.don_pool))
    if attached_total <= 0:
        return list(player.don_pool)
    return list(player.don_pool[:-attached_total])


def _dummy(index: int, *, rested=False) -> Card:
    c = _card(f"DUMMY-{index:03d}", f"Generic Char {index}", "CHARACTER",
              3, 4000, ["Red"], "Straw Hat Crew", rested=rested)
    return c


def _straw_hat(index: int, cost: int = 3, *, rested=False) -> Card:
    c = _card(f"SHC-{index:03d}", f"Straw Hat Ally {index}", "CHARACTER",
              cost, 4000 + cost * 1000, ["Red"], "Straw Hat Crew", rested=rested)
    return c


def _wano(index: int) -> Card:
    return _card(f"WANO-{index:03d}", f"Wano Warrior {index}", "CHARACTER",
                 3, 4000, ["Purple"], "Land of Wano")


def _smile(index: int) -> Card:
    return _card(f"SMILE-{index:03d}", f"Artificial Devil Fruit SMILE", "CHARACTER",
                 2, 3000, ["Purple"], "SMILE")


def _leader(life=4) -> Card:
    c = _card("DUMMY-LEADER", "Test Leader", "LEADER",
              None, 5000, ["Red"], "Straw Hat Crew")
    c.life = life
    c.counter = None
    return c


def _wb_leader(life=4) -> Card:
    """Whitebeard Pirates leader (Edward Newgate) for cards requiring that type."""
    c = _card("OP02-001", "Edward.Newgate", "LEADER",
              None, 5000, ["Red"], "Whitebeard Pirates")
    c.life = life
    c.counter = None
    return c


def _eb_leader(life=4) -> Card:
    """East Blue leader (Kuro) for OP03 East Blue cards."""
    c = _card("OP03-021", "Kuro", "LEADER",
              None, 5000, ["Green"], "East Blue/Black Cat Pirates")
    c.life = life
    c.counter = None
    return c


def _cp_leader(life=4) -> Card:
    """CP9 leader (Rob Lucci) for OP03 CP cards."""
    c = _card("OP03-076", "Rob Lucci", "LEADER",
              None, 5000, ["Black"], "CP9")
    c.life = life
    c.counter = None
    return c


def _impel_down_leader(life=4) -> Card:
    """Impel Down leader for OP03 prison cards."""
    c = _card("OP02-081", "Magellan", "LEADER",
              None, 5000, ["Purple"], "Impel Down")
    c.life = life
    c.counter = None
    return c


def _ace_leader(life=4) -> Card:
    """Ace leader for OP03 Whitebeard/Ace cards."""
    c = _card("OP03-001", "Portgas.D.Ace", "LEADER",
              None, 5000, ["Red"], "Whitebeard Pirates")
    c.life = life
    c.counter = None
    return c


def _bm_leader(life=4) -> Card:
    """Big Mom Pirates leader (Charlotte Katakuri) for OP03 Big Mom cards."""
    c = _card("OP03-099", "Charlotte Katakuri", "LEADER",
              None, 5000, ["Yellow"], "Big Mom Pirates")
    c.life = life
    c.counter = None
    return c


def _nami_blue_leader(life=4) -> Card:
    """Blue Nami leader for OP03 blue East Blue cards."""
    c = _card("OP03-040", "Nami", "LEADER",
              None, 5000, ["Blue"], "East Blue")
    c.life = life
    c.counter = None
    return c


def _iceburg_leader(life=4) -> Card:
    """Iceburg leader for OP03 Galley-La/Water Seven cards."""
    c = _card("OP03-058", "Iceburg", "LEADER",
              None, 5000, ["Purple"], "Water Seven/Galley-La Company")
    c.life = life
    c.counter = None
    return c


def _animal_kingdom_leader(life=4) -> Card:
    """Animal Kingdom Pirates leader for OP04 test setup."""
    c = _card("OP04-040", "Queen", "LEADER",
              None, 5000, ["Blue"], "Animal Kingdom Pirates")
    c.life = life
    c.counter = None
    return c


def _make_test_card(card_data: dict) -> Card:
    id_ = card_data.get("id") or card_data.get("id_normal", "UNKNOWN")
    id_norm = card_data.get("id_normal") or id_
    colors = [x.strip() for x in (card_data.get("Color") or "").split("/") if x.strip()]
    c = Card(
        id=id_, id_normal=id_norm,
        name=card_data.get("name", "?"),
        card_type=card_data.get("cardType", "CHARACTER"),
        cost=_to_int(card_data.get("Cost")),
        power=_to_int(card_data.get("Power")),
        counter=_to_int(card_data.get("Counter")),
        colors=colors,
        life=_to_int(card_data.get("Life")),
        effect=card_data.get("Effect") or "",
        image_link=card_data.get("image_link"),
        attribute=card_data.get("Attribute") or "",
        card_origin=card_data.get("Type") or "",
        trigger=card_data.get("Trigger") or "",
    )
    c.attached_don = 0
    c.power_modifier = 0
    c.is_resting = False
    return c


# ─────────────────────────────────────────────────────────────────
# Game state setup
# ─────────────────────────────────────────────────────────────────

def build_game_state(card_data: dict, timing: str) -> Tuple[GameState, Player, Card]:
    """Build a minimal real GameState configured for a specific timing."""
    deck1 = [_dummy(i) for i in range(30)]
    deck2 = [_dummy(i + 100) for i in range(30)]
    p1 = Player(name="You", deck=deck1, leader=_leader(4), player_id="p1")
    p2 = Player(name="Opponent", deck=deck2, leader=_leader(4), player_id="p2")

    gs = GameState(p1, p2)
    gs.phase = GamePhase.MAIN

    # Override DON after GameState.__init__ resets it to STARTING_DON values
    p1.don_pool = ["active"] * 10
    p2.don_pool = ["active"] * 5 + ["rested"] * 2

    # Opponent field: 2 rested chars with different cost/power
    opp_a = _dummy(200, rested=True); opp_a.name = "Opp-A (4000)"; opp_a.power = 4000; opp_a.cost = 3
    opp_b = _dummy(201, rested=True); opp_b.name = "Opp-B (3000)"; opp_b.power = 3000; opp_b.cost = 2
    p2.cards_in_play.extend([opp_a, opp_b])

    # Red Straw Hat chars in trash (for Uta on_play etc.)
    for i in range(3):
        tc = _straw_hat(400 + i, cost=i + 2)
        tc.name = f"Trash Red-{i + 2}cost"
        p1.trash.append(tc)

    # Build the test card
    test_card = _make_test_card(card_data)
    tc = copy.copy(test_card)
    tc.attached_don = 0; tc.is_resting = False; tc.has_attacked = False; tc.power_modifier = 0

    t = timing.lower()

    if t == "continuous":
        _seed_attached_don(p1, tc, 2)
        if tc.card_type == "LEADER":
            p1.leader = tc
        else:
            p1.cards_in_play.append(tc)
        for i in range(3):
            p1.cards_in_play.append(_straw_hat(300 + i, cost=i + 2))

    elif t == "on_play":
        p1.cards_in_play.append(tc)
        for i in range(2):
            p1.cards_in_play.append(_straw_hat(300 + i, cost=i + 2))

    elif t in ("on_attack", "when_attacking"):
        tc.is_resting = False
        if tc.card_type == "LEADER":
            p1.leader = tc
            _seed_attached_don(p1, tc, 2)
        else:
            p1.cards_in_play.append(tc)
            _seed_attached_don(p1, tc, 2)
        opp_c = _dummy(202, rested=False); opp_c.name = "Opp-C active (5000)"; opp_c.power = 5000; opp_c.cost = 4
        p2.cards_in_play.append(opp_c)

    elif t == "on_ko":
        pass  # card is KO'd — not on field; pass directly

    elif t == "activate":
        tc.is_resting = False
        if tc.card_type == "LEADER":
            p1.leader = tc
            for i in range(5):
                p1.cards_in_play.append(_straw_hat(300 + i, cost=i + 2, rested=True))
            p1.hand.insert(0, _wano(500))
            while len(p1.hand) > 4:
                p1.hand.pop(-1)
        else:
            p1.cards_in_play.append(tc)
            for i in range(3):
                p1.cards_in_play.append(_straw_hat(300 + i, cost=i + 2))

    elif t == "counter":
        p1.hand.append(tc)

    elif t == "trigger":
        p2.life_cards.append(tc)

    elif t == "on_block":
        tc.is_resting = False
        p1.cards_in_play.append(tc)

    elif t == "on_event":
        p1.leader = tc
        _seed_attached_don(p1, tc, 1)
        while len(p1.hand) > 3:
            p1.hand.pop(-1)

    elif t == "on_opponent_ko":
        p1.leader = tc
        _seed_attached_don(p1, tc, 1)

    elif t == "on_event_activated":
        p1.cards_in_play.append(tc)
        _seed_attached_don(p1, tc, 1)

    elif t == "blocker":
        p1.cards_in_play.append(tc)

    else:
        p1.cards_in_play.append(tc)

    # ── Card-specific test seeding ────────────────────────────────
    card_id = card_data.get("id", "")

    # OP01-098/116: Need SMILE cards in deck top 5
    if card_id in ("OP01-098", "OP01-116"):
        for i in range(3):
            p1.deck.insert(i, _smile(900 + i))

    # OP01-099: Need Kurozumi Clan characters on field to test protection
    if card_id == "OP01-099":
        kuro1 = _card("KURO-001", "Kurozumi Higurashi", "CHARACTER",
                       2, 3000, ["Purple"], "Land of Wano/Kurozumi Clan")
        kuro2 = _card("KURO-002", "Kurozumi Kanjuro", "CHARACTER",
                       3, 4000, ["Purple"], "Land of Wano/Kurozumi Clan")
        p1.cards_in_play.extend([kuro1, kuro2])

    # Cards requiring Whitebeard Pirates leader to activate their conditions
    WB_LEADER_CARDS = {
        "OP02-001", "OP02-002", "OP02-003", "OP02-004", "OP02-005",
        "OP02-008", "OP02-009", "OP02-013", "OP02-018", "OP02-021",
        "OP02-023", "OP02-024", "OP02-047",
    }
    if card_id in WB_LEADER_CARDS and tc.card_type != "LEADER":
        p1.leader = _wb_leader(4)
        p2.leader = _wb_leader(4)

    # OP02-031: Needs a Kouzuki Oden character on the field for conditional Blocker
    if card_id == "OP02-031":
        oden = _card("ODEN-001", "Kouzuki Oden", "CHARACTER",
                      5, 6000, ["Green"], "Land of Wano")
        p1.cards_in_play.append(oden)

    # OP02-030: Seed green Land of Wano cost 3 or less characters in deck for on_ko effect
    if card_id == "OP02-030":
        wano1 = _card("WANO-KO-001", "Kiku", "CHARACTER", 2, 3000, ["Green"], "Land of Wano")
        wano2 = _card("WANO-KO-002", "Okiku", "CHARACTER", 3, 4000, ["Green"], "Land of Wano")
        p1.deck.insert(0, wano1)
        p1.deck.insert(1, wano2)

    # OP02-035: Seed a cost 3 or less character in hand for Law's activate effect
    if card_id == "OP02-035":
        low_cost = _card("LC-001", "Cost-2 Character", "CHARACTER", 2, 3000, ["Green"], "Land of Wano")
        p1.hand.insert(0, low_cost)

    # OP02-032: Seed a resting Minks character for Shishilian's optional DON effect
    if card_id == "OP02-032":
        minks1 = _card("MINKS-001", "Pedro (Minks)", "CHARACTER",
                        4, 5000, ["Green"], "Minks", rested=True)
        minks2 = _card("MINKS-002", "Wanda (Minks)", "CHARACTER",
                        3, 4000, ["Green"], "Minks", rested=True)
        p1.cards_in_play.extend([minks1, minks2])

    # OP02-044: Seed a resting Minks character in hand for Wanda's on_play effect
    if card_id == "OP02-044":
        minks_hand = _card("MINKS-003", "Carrot (Minks)", "CHARACTER",
                            2, 3000, ["Green"], "Minks")
        p1.hand.insert(0, minks_hand)

    # OP02-058: Seed Impel Down characters in deck for search testing
    if card_id == "OP02-058":
        id_char1 = _card("ID-001", "Impel Down Guard", "CHARACTER",
                          3, 4000, ["Blue"], "Impel Down")
        id_char2 = _card("ID-002", "Impel Down Jailer", "CHARACTER",
                          2, 3000, ["Blue"], "Impel Down")
        id_char3 = _card("ID-003", "Impel Down Warden", "CHARACTER",
                          4, 5000, ["Blue"], "Impel Down")
        for i, c in enumerate([id_char1, id_char2, id_char3]):
            p1.deck.insert(i, c)

    # OP02-063: Seed a blue Event cost 1 in trash for testing
    if card_id == "OP02-063":
        blue_event = _card("BE-001", "Blue Counter Event", "EVENT",
                            1, None, ["Blue"], "Impel Down")
        p1.trash.append(blue_event)

    # ── OP03 Card-specific test seeding ────────────────────────────

    # Cards requiring East Blue leader
    EB_LEADER_CARDS = {
        "OP03-024", "OP03-026", "OP03-027", "OP03-028", "OP03-029",
        "OP03-033", "OP03-034", "OP03-036", "OP03-037",
    }
    if card_id in EB_LEADER_CARDS and tc.card_type != "LEADER":
        p1.leader = _eb_leader(4)

    # Cards requiring Ace leader
    ACE_LEADER_CARDS = {"OP03-016", "OP03-020"}
    if card_id in ACE_LEADER_CARDS and tc.card_type != "LEADER":
        p1.leader = _ace_leader(4)

    # Cards requiring CP leader
    CP_LEADER_CARDS = {
        "OP03-080", "OP03-086", "OP03-093", "OP03-094", "OP03-096", "OP03-098",
    }
    if card_id in CP_LEADER_CARDS and tc.card_type != "LEADER":
        p1.leader = _cp_leader(4)

    if card_id in ("OP03-068", "OP03-069") and tc.card_type != "LEADER":
        p1.leader = _impel_down_leader(4)

    # Cards requiring Iceburg leader
    ICEBURG_LEADER_CARDS = {"OP03-075"}
    if card_id in ICEBURG_LEADER_CARDS and tc.card_type != "LEADER":
        p1.leader = _iceburg_leader(4)

    # Cards requiring Big Mom Pirates leader
    BM_LEADER_CARDS = {"OP03-114", "OP03-119", "OP03-120"}
    if card_id in BM_LEADER_CARDS and tc.card_type != "LEADER":
        p1.leader = _bm_leader(4)

    # Cards requiring Nami (Blue) leader
    NAMI_LEADER_CARDS = {"OP03-048"}
    if card_id in NAMI_LEADER_CARDS and tc.card_type != "LEADER":
        p1.leader = _nami_blue_leader(4)

    if card_id == "OP03-033":
        p2.leader = _eb_leader(4)

    if card_id == "OP03-040":
        while len(p1.deck) > 4:
            p1.trash.append(p1.deck.pop())

    if card_id in {"OP03-045", "OP03-049", "OP03-053"}:
        while len(p1.deck) > 20:
            p1.trash.append(p1.deck.pop())

    # OP03-080, OP03-092: Need CP cards in trash for "place 2 CP from trash at bottom"
    if card_id in ("OP03-080", "OP03-092"):
        cp1 = _card("CP-T01", "CP9 Agent", "CHARACTER", 3, 4000, ["Black"], "CP9")
        cp2 = _card("CP-T02", "CP9 Operative", "CHARACTER", 2, 3000, ["Black"], "CP9")
        cp3 = _card("CP-T03", "CP9 Assassin", "CHARACTER", 4, 5000, ["Black"], "CP9")
        p1.trash.extend([cp1, cp2, cp3])

    # OP03-090: Need CP cards in trash for on_ko play from trash
    if card_id == "OP03-090":
        cp_trash = _card("CP-T04", "CP9 Rookie", "CHARACTER", 3, 4000, ["Black"], "CP9")
        p1.trash.append(cp_trash)

    # OP03-105, OP03-115: Need Trigger cards in hand for trash-Trigger effects
    if card_id in ("OP03-105", "OP03-115"):
        trigger_card = _card("TRIG-001", "Trigger Card", "CHARACTER",
                              2, 3000, ["Yellow"], "Big Mom Pirates")
        trigger_card.trigger = "Play this card"
        p1.hand.insert(0, trigger_card)

    # OP03-018: Need Event cards in hand for Fire Fist
    if card_id == "OP03-018":
        evt = _card("EVT-001", "Red Event Card", "EVENT",
                     2, None, ["Red"], "Whitebeard Pirates")
        p1.hand.insert(0, evt)

    # OP03-070: Need cost 5 Characters in hand for Luffy's trash-for-Rush
    if card_id == "OP03-070":
        cost5 = _card("C5-001", "Cost 5 Character", "CHARACTER",
                        5, 6000, ["Purple"], "Water Seven/Straw Hat Crew")
        p1.hand.insert(0, cost5)

    # OP03-036: Leader must be Kuro (East Blue) and resting; add East Blue chars and a resting Kuro char
    if card_id == "OP03-036":
        p1.leader = _eb_leader(4)
        p1.leader.is_resting = True  # Kuro leader is resting — can be chosen to activate
        for i in range(2):
            eb = _card(f"EB-036-{i}", f"East Blue Char {i+1}", "CHARACTER",
                       3, 4000, ["Green"], "East Blue")
            eb.is_resting = False
            p1.cards_in_play.append(eb)
        # Add a resting Kuro character so the player can choose between char and leader
        kuro_char = _card("KURO-C01", "Kuro", "CHARACTER", 4, 5000, ["Green"], "East Blue/Black Cat Pirates")
        kuro_char.is_resting = True
        p1.cards_in_play.append(kuro_char)

    if card_id == "OP03-021":
        # Add 3 EB chars so the player has a real choice of WHICH 2 to rest
        for i in range(3):
            east_blue = _card(f"EB-{i}", f"East Blue Test {i+1}", "CHARACTER",
                               3, 4000, ["Green"], "East Blue")
            east_blue.is_resting = False
            p1.cards_in_play.append(east_blue)

    # OP03-042: Need a blue Usopp in trash
    if card_id == "OP03-042":
        usopp_trash = _card("USP-001", "Usopp", "CHARACTER",
                             4, 5000, ["Blue"], "East Blue")
        p1.trash.append(usopp_trash)

    # OP03-064, OP03-067: Need Galley-La Company leader
    if card_id in ("OP03-064", "OP03-067"):
        p1.leader = _iceburg_leader(4)

    if card_id == "OP03-075":
        # Reduce DON pool below max so the +1 rested DON effect can be demonstrated
        p1.don_pool = ["active"] * 9

    if card_id == "OP03-094":
        # Seed 3 CP cards at top of deck to guarantee coverage in top 5
        cp_seeds = [
            ("OP03-093", "Wanze", 3, 3000),
            ("CP-S001", "CP9 Spy", 4, 4000),
            ("CP-S002", "CP9 Agent", 2, 3000),
        ]
        for i, (cid, cname, cost, power) in enumerate(cp_seeds):
            c = _card(cid, cname, "CHARACTER", cost, power, ["Black"], "CP9")
            p1.deck.insert(i, c)

    # ── OP04 Card-specific test seeding ────────────────────────────

    if card_id == "OP04-046":
        p1.leader = _animal_kingdom_leader(4)
        op04_seeds = [
            _card("OP04-055", "Plague Rounds", "EVENT", 2, None, ["Blue"], "Animal Kingdom Pirates"),
            _card("OP04-055-SEED-2", "Plague Rounds", "EVENT", 2, None, ["Blue"], "Animal Kingdom Pirates"),
            _card("OP04-047", "Ice Oni", "CHARACTER", 4, 5000, ["Blue"], "Animal Kingdom Pirates"),
            _card("OP04-047-SEED-2", "Ice Oni", "CHARACTER", 4, 5000, ["Blue"], "Animal Kingdom Pirates"),
            _card("AKP-046-001", "Animal Kingdom Filler 1", "CHARACTER", 3, 4000, ["Blue"], "Animal Kingdom Pirates"),
            _card("AKP-046-002", "Animal Kingdom Filler 2", "CHARACTER", 3, 4000, ["Blue"], "Animal Kingdom Pirates"),
            _card("AKP-046-003", "Animal Kingdom Filler 3", "CHARACTER", 3, 4000, ["Blue"], "Animal Kingdom Pirates"),
        ]
        for i, seed in enumerate(op04_seeds):
            p1.deck.insert(i, seed)

    if card_id == "OP04-066":
        p1.life_cards = [life_card for life_card in p1.life_cards if getattr(life_card, "id", "") != tc.id]
        p1.life_cards.append(copy.copy(tc))
        p2.life_cards = [life_card for life_card in p2.life_cards if getattr(life_card, "id", "") != tc.id]
        p2.life_cards.append(copy.copy(tc))

    if card_id == "OP04-084":
        top_three = [
            _card("CP-OP04-084-F1", "Black Filler 1", "CHARACTER", 4, 5000, ["Black"], "Navy"),
            _card("CP-OP04-084-F2", "Black Filler 2", "CHARACTER", 3, 4000, ["Black"], "Cipher Pol"),
            _card("CP-OP04-084", "CP Test Agent", "CHARACTER", 2, 3000, ["Black"], "CP"),
        ]
        for i, seed in enumerate(top_three):
            p1.deck.insert(i, seed)

    if card_id == "OP04-093":
        dressrosa = _card("DRESSROSA-093", "Dressrosa Test Target", "CHARACTER", 5, 6000, ["Black"], "Dressrosa")
        p1.cards_in_play.append(dressrosa)
        while len(p1.trash) < 14:
            idx = len(p1.trash) + 1
            p1.trash.append(_card(f"TRASH-093-{idx:02d}", f"Trash Seed {idx}", "CHARACTER", 2, 3000, ["Black"], "Dressrosa"))

    if card_id == "OP04-111":
        other_homie = _card("HOMIES-111", "Other Homie", "CHARACTER", 3, 3000, ["Yellow"], "Homies")
        linlin = _card("LINLIN-111", "Charlotte Linlin", "CHARACTER", 10, 12000, ["Yellow"], "Big Mom Pirates")
        linlin.is_resting = True
        linlin.has_attacked = True
        p1.cards_in_play.append(other_homie)
        p1.cards_in_play.append(linlin)

    if card_id == "OP04-115":
        p1.cards_in_play.append(_card("WANO-115", "Wano Test Target", "CHARACTER", 3, 4000, ["Purple"], "Land of Wano"))
        while len(p1.life_cards) < 2 and p1.deck:
            p1.life_cards.append(p1.deck.pop(0))

    if card_id == "OP04-119":
        green_five = _card("GREEN-119", "Green Five Test", "CHARACTER", 5, 6000, ["Green"], "Donquixote Pirates")
        p1.hand.insert(0, green_five)

    # ── OP05 Card-specific test seeding ────────────────────────────
    if card_id in {"OP05-002", "OP05-018", "OP05-020", "OP05-095"} and tc.card_type != "LEADER":
        p1.leader = _card("OP05-002", "Belo Betty", "LEADER", None, 5000, ["Red", "Yellow"], "Revolutionary Army")
        p1.leader.life = 4

    if card_id in {"OP05-041", "OP05-043", "OP05-059"} and tc.card_type != "LEADER":
        p1.leader = _card("OP05-041", "Sakazuki", "LEADER", None, 5000, ["Blue", "Black"], "Navy")
        p1.leader.life = 4

    if card_id in {"OP05-077", "OP05-078"} and tc.card_type != "LEADER":
        p1.don_pool = ["active"] * 8 + ["rested"] * 2

    if card_id == "OP05-078" and tc.card_type != "LEADER":
        p1.leader = _card("KID-LEADER", "Kid Pirates Leader", "LEADER", None, 5000, ["Purple"], "Kid Pirates")
        p1.leader.life = 4
        p1.cards_in_play.append(_card("KID-ALLY", "Kid Pirates Ally", "CHARACTER", 4, 5000, ["Purple"], "Kid Pirates"))

    if card_id in {"OP05-099", "OP05-114", "OP05-115", "OP05-116"} and tc.card_type != "LEADER":
        p1.leader = _card("OP05-098", "Enel", "LEADER", None, 5000, ["Yellow"], "Sky Island")
        p1.leader.life = 4

    if card_id == "OP05-018":
        p1.hand.insert(0, _card("REV-018", "Rev Army Recruit", "CHARACTER", 4, 5000, ["Red"], "Revolutionary Army"))

    if card_id == "OP05-020":
        low_power = _card("OPP-020", "Low Power Target", "CHARACTER", 2, 2000, ["Blue"], "Navy")
        p2.cards_in_play.append(low_power)

    if card_id in {"OP05-037", "OP05-038"}:
        p1.hand.insert(0, _card(f"HAND-{card_id}", "Discard Fodder", "CHARACTER", 2, 3000, ["Green"], "Donquixote Pirates"))

    if card_id == "OP05-038":
        p1.don_pool = ["active"] * 7 + ["rested"] * 3

    if card_id == "OP05-039":
        p2.cards_in_play.append(_card("OPP-039", "Rested Small Target", "CHARACTER", 3, 4000, ["Green"], "Donquixote Pirates", rested=True))

    if card_id == "OP05-056":
        p1.cards_in_play.append(_card("ALLY-056", "Blue Ally", "CHARACTER", 3, 4000, ["Blue"], "Former Navy"))

    if card_id == "OP05-057":
        p1.cards_in_play.append(_card("ALLY-057", "Own Small Character", "CHARACTER", 2, 3000, ["Blue"], "Navy"))

    if card_id == "OP05-058":
        p1.cards_in_play.append(_card("SMALL-058-A", "Your Small Character", "CHARACTER", 3, 4000, ["Blue"], "Navy"))
        p2.cards_in_play.append(_card("SMALL-058-B", "Opp Small Character", "CHARACTER", 2, 3000, ["Blue"], "Navy"))
        while len(p1.hand) < 7:
            p1.hand.append(_dummy(700 + len(p1.hand)))
        while len(p2.hand) < 7:
            p2.hand.append(_dummy(800 + len(p2.hand)))

    if card_id == "OP05-081":
        p2.cards_in_play.append(_card("OPP-081", "Cost Target", "CHARACTER", 4, 5000, ["Black"], "Dressrosa"))

    if card_id == "OP05-082":
        while len(p1.trash) < 2:
            p1.trash.append(_card(f"TRASH-082-{len(p1.trash)}", "Trash Seed", "CHARACTER", 2, 3000, ["Black"], "Dressrosa"))
        while len(p2.hand) < 6:
            p2.hand.append(_dummy(820 + len(p2.hand)))

    if card_id == "OP05-084":
        p1.cards_in_play = [c for c in p1.cards_in_play if c == tc]
        p1.cards_in_play.append(_card("CD-084", "Celestial Ally", "CHARACTER", 2, 3000, ["Black"], "Celestial Dragons"))

    if card_id == "OP05-087":
        p1.cards_in_play.append(_card("ALLY-087", "Dressrosa Ally", "CHARACTER", 3, 4000, ["Black"], "Dressrosa"))
        p2.cards_in_play.append(_card("OPP-087", "Cost Five Target", "CHARACTER", 5, 6000, ["Black"], "Dressrosa"))

    if card_id == "OP05-088":
        while len(p1.trash) < 2:
            p1.trash.append(_card(f"TRASH-088-{len(p1.trash)}", "Trash Seed", "CHARACTER", 2, 3000, ["Black"], "Dressrosa"))
        p1.trash.append(_card("BLACK-088", "Recoverable Black 4", "CHARACTER", 4, 5000, ["Black"], "Dressrosa"))

    if card_id == "OP05-089":
        p1.cards_in_play.append(_card("ALLY-089", "Black Ally", "CHARACTER", 2, 3000, ["Black"], "Celestial Dragons"))
        p1.trash.append(_card("BLACK-089", "Recoverable Black 1", "CHARACTER", 1, 2000, ["Black"], "Celestial Dragons"))

    if card_id == "OP05-090":
        p1.cards_in_play.append(_card("DRESS-090", "Dressrosa Target", "CHARACTER", 4, 5000, ["Black"], "Dressrosa"))

    if card_id == "OP05-093":
        while len(p1.trash) < 3:
            p1.trash.append(_card(f"TRASH-093-OP05-{len(p1.trash)}", "Trash Seed", "CHARACTER", 2, 3000, ["Black"], "CP0"))
        p2.cards_in_play.append(_card("KO2-093", "Cost 2 Target", "CHARACTER", 2, 3000, ["Black"], "CP0"))
        p2.cards_in_play.append(_card("KO1-093", "Cost 1 Target", "CHARACTER", 1, 2000, ["Black"], "CP0"))

    if card_id == "OP05-094":
        p2.cards_in_play.append(_card("PATCH-094", "Cost 3 Target", "CHARACTER", 3, 4000, ["Black"], "Dressrosa"))

    if card_id == "OP05-096":
        p1.cards_in_play.append(_card("CD-096", "Celestial Noble", "CHARACTER", 2, 3000, ["Black"], "Celestial Dragons"))
        p2.cards_in_play.append(_card("LOW-096", "Cost 1 Target", "CHARACTER", 1, 2000, ["Black"], "Navy"))

    if card_id == "OP05-097":
        p1.hand.insert(0, _card("CD-HAND-097", "Celestial Dragons Hand Card", "CHARACTER", 3, 4000, ["Black"], "Celestial Dragons"))

    if card_id == "OP05-099":
        if not p2.life_cards and p2.deck:
            p2.life_cards.append(p2.deck.pop(0))

    if card_id == "OP05-115":
        p1.life_cards = p1.life_cards[:1]
        while len(p1.hand) < 3:
            p1.hand.append(_dummy(1150 + len(p1.hand)))

    if card_id == "OP05-116":
        p2.life_cards = p2.life_cards[:2]
        p2.cards_in_play.append(_card("ZAP-116", "Life-Count Target", "CHARACTER", 2, 3000, ["Yellow"], "Sky Island"))

    if card_id == "OP05-119":
        p1.cards_in_play.append(_card("ALLY-119-A", "Bottom Deck Ally A", "CHARACTER", 4, 5000, ["Purple"], "Straw Hat Crew"))
        p1.cards_in_play.append(_card("ALLY-119-B", "Bottom Deck Ally B", "CHARACTER", 3, 4000, ["Purple"], "Straw Hat Crew"))

    if card_id == "OP05-009":
        p2.leader.power = 0

    if card_id == "OP05-026":
        p1.cards_in_play.append(_card("ALLY-026", "Baroque Works Ally", "CHARACTER", 3, 4000, ["Red", "Black"], "Baroque Works"))

    if card_id in {"OP05-069", "OP05-071"}:
        p2.don_pool = ["active"] * 8

    if card_id == "OP05-079":
        while len(p2.trash) < 3:
            p2.trash.append(_card(f"P2TRASH-079-{len(p2.trash)}", "Opponent Trash Seed", "CHARACTER", 2, 3000, ["Green"], "Baroque Works"))

    if card_id == "OP05-080":
        while len(p1.trash) < 20:
            p1.trash.append(_card(f"TRASH-080-{len(p1.trash)}", "Trash Seed", "CHARACTER", 2, 3000, ["Black"], "Dressrosa"))

    if card_id == "OP05-091":
        p1.trash.append(_card("BLACK-091-A", "Black Cost 5 Char A", "CHARACTER", 5, 6000, ["Black"], "Dressrosa"))
        p1.trash.append(_card("BLACK-091-B", "Black Cost 4 Char B", "CHARACTER", 4, 5000, ["Black"], "Dressrosa"))
        p1.hand.insert(0, _card("HAND-091", "Black Cost 3 Char", "CHARACTER", 3, 4000, ["Black"], "Dressrosa"))

    if card_id == "OP05-095":
        while len(p1.trash) < 15:
            p1.trash.append(_card(f"TRASH-095-{len(p1.trash)}", "Trash Seed", "CHARACTER", 2, 3000, ["Black"], "CP0"))

    if card_id == "OP05-098" and tc.card_type == "LEADER":
        p1.life_cards = p1.life_cards[:1]

    return gs, p1, tc


# ─────────────────────────────────────────────────────────────────
# Snapshot / diff helpers
# ─────────────────────────────────────────────────────────────────

def _snapshot(player: Player, opponent: Player) -> dict:
    def field_repr(cards):
        return [
            f"{c.name} pow={c.power or 0}+{getattr(c,'power_modifier',0)} "
            f"don={getattr(c,'attached_don',0)} rest={c.is_resting}"
            for c in cards
        ]
    cost_area_don = _cost_area_don_pool(player)
    return {
        "hand":       len(player.hand),
        "field":      field_repr(player.cards_in_play),
        "trash":      len(player.trash),
        "life":       len(player.life_cards),
        "don_active": cost_area_don.count("active"),
        "don_rested": cost_area_don.count("rested"),
        "opp_field":  field_repr(opponent.cards_in_play),
        "opp_life":   len(opponent.life_cards),
        "opp_hand":   len(opponent.hand),
    }


def _diff(before: dict, after: dict) -> List[str]:
    labels = {
        "hand":       "Your hand",
        "field":      "Your field",
        "trash":      "Your trash",
        "life":       "Your life",
        "don_active": "Active DON",
        "don_rested": "Rested DON",
        "opp_field":  "Opp field",
        "opp_life":   "Opp life",
        "opp_hand":   "Opp hand",
    }
    return [f"{labels[k]}: {before[k]}  →  {after[k]}"
            for k in labels if before[k] != after[k]]


# ─────────────────────────────────────────────────────────────────
# CARD_STATUS.md helpers
# ─────────────────────────────────────────────────────────────────

def load_status_entries(set_code: str) -> List[dict]:
    """Load card status entries for a set (or all sets if set_code is 'ALL')."""
    if not STATUS_FILE.exists():
        return []
    entries = []
    for line in STATUS_FILE.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| "):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 5:
            continue
        card_id = parts[1]
        # Skip header rows
        if not re.match(r"[A-Z0-9]+-\d+", card_id):
            continue
        # Filter by set code (or include all)
        if set_code != "ALL" and not card_id.startswith(set_code):
            continue
        # Actual column order: | ID | Status | Type | Notes... |
        entries.append({
            "id": card_id,
            "name": card_id,  # real name populated from card_db later
            "type": parts[3] if len(parts) > 3 else "",
            "status": parts[2],
            "effect": parts[5] if len(parts) > 5 else "",
            "notes": parts[4] if len(parts) > 4 else "",
        })
    return entries


def update_card_status(card_id: str, new_status: str, notes: str = None):
    if not STATUS_FILE.exists():
        return
    text  = STATUS_FILE.read_text(encoding="utf-8")
    lines = text.splitlines()
    new_lines = []
    for line in lines:
        if line.startswith(f"| {card_id} |"):
            parts = line.split("|")
            # Actual column order: | ID | Status | Type | Notes... |
            if len(parts) >= 4:
                parts[2] = f" {new_status} "
                if notes is not None:
                    parts[4] = f" {notes} " if len(parts) > 4 else f" {notes} "
                line = "|".join(parts)
        new_lines.append(line)
    result = "\n".join(new_lines)
    result = re.sub(r"\*\*Verified:\*\*.*",       f"**Verified:** {result.count('✅ Verified')}", result)
    result = re.sub(r"\*\*Missing:\*\*.*",         f"**Missing:** {result.count('❌ Missing')}", result)
    result = re.sub(r"\*\*To Do \(audit\):\*\*.*", f"**To Do (audit):** {result.count('🔲 To Do')}", result)
    STATUS_FILE.write_text(result, encoding="utf-8")


def get_timings(card_id: str) -> List[str]:
    base_id = card_id.split("_")[0] if ("_p" in card_id or "_r" in card_id) else card_id
    effects = _hardcoded_effects.get(card_id, [])
    if base_id != card_id:
        effects = effects + _hardcoded_effects.get(base_id, [])
    return list(dict.fromkeys(e.timing for e in effects))


# ─────────────────────────────────────────────────────────────────
# EffectTestSession
# ─────────────────────────────────────────────────────────────────

class EffectTestSession:
    """Tracks one user's effect-testing session."""

    def __init__(self, entries: List[dict], card_db: dict):
        self.entries  = entries   # filtered list of {id, name, type, status, effect, notes}
        self.card_db  = card_db
        self.index    = 0
        # Skip to first testable card
        if not self._is_testable(self.index):
            self._advance_to_testable(1)

    # ── Navigation ────────────────────────────────────────────────

    def _is_testable(self, idx: int) -> bool:
        if idx < 0 or idx >= len(self.entries):
            return False
        e = self.entries[idx]
        return bool(self.card_db.get(e["id"])) and bool(get_timings(e["id"]))

    def _advance_to_testable(self, direction: int):
        """Move index in direction (+1/-1) until a testable card is found."""
        self.index += direction
        while 0 <= self.index < len(self.entries):
            if self._is_testable(self.index):
                return
            self.index += direction

    def advance(self):
        self._advance_to_testable(+1)

    def go_back(self):
        self._advance_to_testable(-1)

    @property
    def current_entry(self) -> Optional[dict]:
        if 0 <= self.index < len(self.entries):
            return self.entries[self.index]
        return None

    # ── Build payload ─────────────────────────────────────────────

    def build_payload(self) -> Optional[dict]:
        """Build the full effect_test_update payload for the current card."""
        entry = self.current_entry
        if not entry:
            return {"done": True, "total": len(self.entries)}

        card_data = self.card_db.get(entry["id"])
        if not card_data:
            return None

        timings = get_timings(entry["id"])
        if not timings:
            return None

        timing_results = []
        first_gs_dict  = None

        for timing in timings:
            try:
                gs, player, tc = build_game_state(card_data, timing)
                before = _snapshot(player, gs.opponent_player)

                captured  = io.StringIO()
                exc_info  = None
                with redirect_stdout(captured):
                    try:
                        result = execute_hardcoded_effect(gs, player, tc, timing)
                    except Exception:
                        result    = None
                        exc_info  = traceback.format_exc()

                after   = _snapshot(player, gs.opponent_player)
                changes = _diff(before, after)
                stdout_lines = [
                    l for l in captured.getvalue().splitlines()
                    if l.strip() and not l.startswith("[DEBUG]")
                ]

                timing_results.append({
                    "timing":        timing,
                    "returned":      result,
                    "exception":     exc_info,
                    "stdout_lines":  stdout_lines[:10],
                    "action_logs":   getattr(gs, "action_logs", [])[-8:],
                    "state_changes": changes,
                    "pending_choice": gs.pending_choice.to_dict() if gs.pending_choice else None,
                })

                if first_gs_dict is None:
                    first_gs_dict = gs.to_dict(for_player="p1")

            except Exception:
                timing_results.append({
                    "timing":        timing,
                    "returned":      None,
                    "exception":     traceback.format_exc(),
                    "stdout_lines":  [],
                    "action_logs":   [],
                    "state_changes": [],
                    "pending_choice": None,
                })

        effect_text  = html_module.unescape(re.sub(r"<[^>]+>", " ", card_data.get("Effect") or "")).strip()
        trigger_text = html_module.unescape(re.sub(r"<[^>]+>", " ", card_data.get("Trigger") or "")).strip()

        return {
            "done":           False,
            "card_id":        entry["id"],
            "card_name":      entry["name"],
            "card_type":      entry["type"],
            "current_status": entry["status"],
            "notes":          entry["notes"],
            "effect_text":    effect_text,
            "trigger_text":   trigger_text,
            "timings":        timings,
            "index":          self.index,
            "total":          len(self.entries),
            "timing_results": timing_results,
            "game_state":     first_gs_dict,
        }
