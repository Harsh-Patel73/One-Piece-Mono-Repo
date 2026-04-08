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
from optcg_engine.effects.hardcoded import execute_hardcoded_effect, _hardcoded_effects

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
        tc.attached_don = 2
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
        tc.attached_don = 2; tc.is_resting = False
        if tc.card_type == "LEADER":
            p1.leader = tc
        else:
            p1.cards_in_play.append(tc)
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
        tc.attached_don = 1; p1.leader = tc
        while len(p1.hand) > 3:
            p1.hand.pop(-1)

    elif t == "on_opponent_ko":
        tc.attached_don = 1; p1.leader = tc

    elif t == "on_event_activated":
        tc.attached_don = 1; p1.cards_in_play.append(tc)

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

    # OP03-036: Need a Kuro character on field (rested) and East Blue chars
    if card_id == "OP03-036":
        kuro_char = _card("KURO-001", "Kuro", "CHARACTER",
                           3, 4000, ["Green"], "East Blue/Black Cat Pirates")
        kuro_char.is_resting = True
        kuro_char.attached_don = 0
        kuro_char.power_modifier = 0
        p1.cards_in_play.append(kuro_char)

    # OP03-042: Need a blue Usopp in trash
    if card_id == "OP03-042":
        usopp_trash = _card("USP-001", "Usopp", "CHARACTER",
                             4, 5000, ["Blue"], "East Blue")
        p1.trash.append(usopp_trash)

    # OP03-064, OP03-067: Need Galley-La Company leader
    if card_id in ("OP03-064", "OP03-067"):
        p1.leader = _iceburg_leader(4)

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
    return {
        "hand":       len(player.hand),
        "field":      field_repr(player.cards_in_play),
        "trash":      len(player.trash),
        "life":       len(player.life_cards),
        "don_active": player.don_pool.count("active"),
        "don_rested": player.don_pool.count("rested"),
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
