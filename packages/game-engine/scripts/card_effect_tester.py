#!/usr/bin/env python3
"""
Interactive Card Effect Tester

Builds a minimal real GameState and runs each card's hardcoded effect,
then lets you mark it as Pass / Fail / Skip and updates CARD_STATUS.md.

Usage:
  python card_effect_tester.py                      # Test all "To Do" OP01 cards
  python card_effect_tester.py OP02                 # Test all "To Do" OP02 cards
  python card_effect_tester.py OP01-006             # Test one specific card
  python card_effect_tester.py OP01 --from OP01-010 # Resume from a card
  python card_effect_tester.py OP01 --status all    # Include already-verified cards

Controls (at the prompt):
  P  — Pass: mark as ✅ Verified
  F  — Fail: mark as ⚠ Needs Fix (optionally add a note)
  S  — Skip: leave status unchanged
  N  — Add / edit note without changing status
  R  — Rerun: re-execute the effect
  Q  — Quit: show session summary and exit
"""

import argparse
import copy
import io
import json
import os
import re
import sys
import traceback
from contextlib import redirect_stdout
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Fix Windows console encoding
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── Path setup ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(Path(__file__).parent.parent))

from optcg_engine.game_engine import GameState, PendingChoice, Player  # noqa: E402
from optcg_engine.models.cards import Card  # noqa: E402
from optcg_engine.models.enums import GamePhase  # noqa: E402

# Importing hardcoded also auto-imports all set effect files (triggers registration)
from optcg_engine.effects.effect_registry import (  # noqa: E402
    _hardcoded_effects,
    execute_hardcoded_effect,
)

# ── Paths ────────────────────────────────────────────────────────────────────
CARDS_JSON = ROOT / "packages" / "simulator" / "backend" / "data" / "cards.json"
STATUS_FILE = (
    ROOT / "packages" / "game-engine" / "optcg_engine" / "effects" / "CARD_STATUS.md"
)

# ── ANSI colours (disabled if not a TTY) ────────────────────────────────────
if sys.stdout.isatty():
    BOLD  = "\033[1m"
    DIM   = "\033[2m"
    GREEN = "\033[92m"
    RED   = "\033[91m"
    YLW   = "\033[93m"
    CYAN  = "\033[96m"
    RST   = "\033[0m"
else:
    BOLD = DIM = GREEN = RED = YLW = CYAN = RST = ""

SEP = "═" * 62


# ═══════════════════════════════════════════════════════════════════
# Card / GameState helpers
# ═══════════════════════════════════════════════════════════════════

def _to_int(val) -> Optional[int]:
    if val is None:
        return None
    try:
        return int(val)
    except (TypeError, ValueError):
        return None


def _make_dummy_card(index: int, *, rested: bool = False) -> Card:
    """Generic filler card (CHARACTER, cost 3, power 4000)."""
    c = Card(
        id=f"DUMMY-{index:03d}",
        id_normal=f"DUMMY-{index:03d}",
        name=f"Generic Char {index}",
        card_type="CHARACTER",
        cost=3,
        power=4000,
        counter=1000,
        colors=["Red"],
        life=None,
        effect="",
        image_link=None,
        attribute="Strike",
        card_origin="Straw Hat Crew",
        trigger=None,
    )
    c.is_resting = rested
    c.attached_don = 0
    c.power_modifier = 0
    return c


def _make_straw_hat_char(index: int, cost: int = 3, *, rested: bool = False) -> Card:
    """Red Straw Hat Crew CHARACTER — satisfies type/color filters."""
    c = Card(
        id=f"SHC-{index:03d}",
        id_normal=f"SHC-{index:03d}",
        name=f"Straw Hat Ally {index}",
        card_type="CHARACTER",
        cost=cost,
        power=4000 + cost * 1000,
        counter=1000,
        colors=["Red"],
        life=None,
        effect="",
        image_link=None,
        attribute="Strike",
        card_origin="Straw Hat Crew",
        trigger=None,
    )
    c.is_resting = rested
    c.attached_don = 0
    c.power_modifier = 0
    return c


def _make_wano_char(index: int) -> Card:
    """Land of Wano CHARACTER — satisfies Oden's hand-trash cost."""
    c = Card(
        id=f"WANO-{index:03d}",
        id_normal=f"WANO-{index:03d}",
        name=f"Wano Warrior {index}",
        card_type="CHARACTER",
        cost=3,
        power=4000,
        counter=1000,
        colors=["Purple"],
        life=None,
        effect="",
        image_link=None,
        attribute="Strike",
        card_origin="Land of Wano",
        trigger=None,
    )
    c.is_resting = False
    c.attached_don = 0
    c.power_modifier = 0
    return c


def _make_seed_card(card_id: str, name: str, card_type: str, cost: int, power: int,
                    colors: List[str], origin: str, *, rested: bool = False) -> Card:
    c = Card(
        id=card_id,
        id_normal=card_id,
        name=name,
        card_type=card_type,
        cost=cost,
        power=power,
        counter=1000 if card_type == "CHARACTER" else None,
        colors=colors,
        life=None,
        effect="",
        image_link=None,
        attribute="Strike",
        card_origin=origin,
        trigger=None,
    )
    c.is_resting = rested
    c.attached_don = 0
    c.power_modifier = 0
    return c


def _make_dummy_leader(life: int = 4) -> Card:
    c = Card(
        id="DUMMY-LEADER",
        id_normal="DUMMY-LEADER",
        name="Test Leader",
        card_type="LEADER",
        cost=None,
        power=5000,
        counter=None,
        colors=["Red"],
        life=life,
        effect="",
        image_link=None,
        attribute="Strike",
        card_origin="Straw Hat Crew",
        trigger=None,
    )
    c.attached_don = 0
    c.power_modifier = 0
    return c


def make_test_card(card_data: dict) -> Card:
    """Construct a real Card from a cards.json entry."""
    id_ = card_data.get("id") or card_data.get("id_normal", "UNKNOWN")
    id_norm = card_data.get("id_normal") or id_
    c = Card(
        id=id_,
        id_normal=id_norm,
        name=card_data.get("name", "?"),
        card_type=card_data.get("cardType", "CHARACTER"),
        cost=_to_int(card_data.get("Cost")),
        power=_to_int(card_data.get("Power")),
        counter=_to_int(card_data.get("Counter")),
        colors=[x.strip() for x in (card_data.get("Color") or "").split("/") if x.strip()],
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


def build_game_state(test_card: Card, timing: str) -> Tuple[GameState, Player, Card]:
    """
    Build a minimal but real GameState and return (game_state, active_player, test_card_instance).

    Each timing branch sets up the richest plausible conditions so effects
    actually fire rather than returning False due to missing prerequisites.
    """
    deck1 = [_make_dummy_card(i) for i in range(30)]
    deck2 = [_make_dummy_card(i + 100) for i in range(30)]

    leader1 = _make_dummy_leader(life=4)
    leader2 = _make_dummy_leader(life=4)

    p1 = Player(name="You", deck=deck1, leader=leader1, player_id="p1")
    p2 = Player(name="Opponent", deck=deck2, leader=leader2, player_id="p2")

    gs = GameState(p1, p2)
    gs.phase = GamePhase.MAIN

    # Override DON AFTER GameState.__init__ (which resets to STARTING_DON_P1/P2=1/2)
    # 10 active DON — satisfies any DON!! cost including King leader (needs 10 total)
    p1.don_pool = ["active"] * 10
    p2.don_pool = ["active"] * 5 + ["rested"] * 2

    # Opponent field: 2 rested chars at common cost/power values
    opp_a = _make_dummy_card(200, rested=True)
    opp_a.name = "Opp-A (4000)"
    opp_a.power = 4000
    opp_a.cost = 3
    opp_b = _make_dummy_card(201, rested=True)
    opp_b.name = "Opp-B (3000)"
    opp_b.power = 3000
    opp_b.cost = 2
    p2.cards_in_play.extend([opp_a, opp_b])

    # Red Straw Hat Crew chars in trash (for Uta on_play)
    for i in range(3):
        t_card = _make_straw_hat_char(400 + i, cost=i + 2)
        t_card.name = f"Trash Red-{i + 2}cost"
        p1.trash.append(t_card)

    # ── Copy the card under test ──────────────────────────────────
    tc = copy.copy(test_card)
    tc.attached_don = 0
    tc.is_resting = False
    tc.has_attacked = False
    tc.power_modifier = 0

    t = timing.lower()

    if t == "continuous":
        # Attach 2 DON (satisfies DON!! x1 and x2 conditions)
        tc.attached_don = 2
        if tc.card_type == "LEADER":
            p1.leader = tc
        else:
            p1.cards_in_play.append(tc)
        # 3 allies on field so power-buff effects have targets
        for i in range(3):
            ally = _make_straw_hat_char(300 + i, cost=i + 2)
            p1.cards_in_play.append(ally)

    elif t == "on_play":
        p1.cards_in_play.append(tc)
        # 2 allies for effects that check own field
        for i in range(2):
            p1.cards_in_play.append(_make_straw_hat_char(300 + i, cost=i + 2))

    elif t in ("on_attack", "when_attacking"):
        tc.attached_don = 2  # satisfies DON!! x2 (Doffy leader)
        tc.is_resting = False
        if tc.card_type == "LEADER":
            p1.leader = tc
        else:
            p1.cards_in_play.append(tc)
        # Add an active opp char as well (some effects target active chars)
        opp_c = _make_dummy_card(202, rested=False)
        opp_c.name = "Opp-C active (5000)"
        opp_c.power = 5000
        opp_c.cost = 4
        p2.cards_in_play.append(opp_c)

    elif t == "on_ko":
        # Card was just KO'd — NOT on field; passed as arg directly
        pass

    elif t == "activate":
        tc.is_resting = False
        if tc.card_type == "LEADER":
            p1.leader = tc
            # 5 rested Straw Hat / Supernovas chars at cost 2-6 (Law, Luffy preconditions)
            for i in range(5):
                ally = _make_straw_hat_char(300 + i, cost=i + 2, rested=True)
                p1.cards_in_play.append(ally)
            # Land of Wano card in hand (Oden precondition)
            p1.hand.insert(0, _make_wano_char(500))
            # Keep hand ≤ 3 other cards so Croc leader draw fires (needs hand ≤ 4)
            while len(p1.hand) > 4:
                p1.hand.pop(-1)
        else:
            p1.cards_in_play.append(tc)
            # 3 allies for effects that check/target own field
            for i in range(3):
                p1.cards_in_play.append(_make_straw_hat_char(300 + i, cost=i + 2))

    elif t in ("counter", "trigger"):
        p1.hand.append(tc)

    elif t == "on_block":
        tc.is_resting = False
        p1.cards_in_play.append(tc)

    elif t == "on_event":
        # Leader fires when you play an Event (Crocodile)
        tc.attached_don = 1
        p1.leader = tc
        # Hand ≤ 4 so Croc's draw condition is met
        while len(p1.hand) > 3:
            p1.hand.pop(-1)

    elif t == "on_opponent_ko":
        # Leader fires when opponent's char is KO'd (Kaido)
        tc.attached_don = 1
        p1.leader = tc

    elif t == "on_event_activated":
        # CHARACTER fires when opponent activates an Event (Usopp)
        tc.attached_don = 1
        p1.cards_in_play.append(tc)

    elif t == "blocker":
        p1.cards_in_play.append(tc)

    else:
        p1.cards_in_play.append(tc)

    card_id = test_card.id

    if card_id in {"OP05-002", "OP05-018", "OP05-020", "OP05-095"} and tc.card_type != "LEADER":
        p1.leader = _make_seed_card("OP05-002", "Belo Betty", "LEADER", None, 5000, ["Red", "Yellow"], "Revolutionary Army")
        p1.leader.life = 4

    if card_id in {"OP05-041", "OP05-059"} and tc.card_type != "LEADER":
        p1.leader = _make_seed_card("OP05-041", "Sakazuki", "LEADER", None, 5000, ["Blue", "Black"], "Navy")
        p1.leader.life = 4

    if card_id in {"OP05-077", "OP05-078"} and tc.card_type != "LEADER":
        p1.don_pool = ["active"] * 8 + ["rested"] * 2

    if card_id == "OP05-078" and tc.card_type != "LEADER":
        p1.leader = _make_seed_card("KID-LEADER", "Kid Pirates Leader", "LEADER", None, 5000, ["Purple"], "Kid Pirates")
        p1.leader.life = 4
        p1.cards_in_play.append(_make_seed_card("KID-ALLY", "Kid Pirates Ally", "CHARACTER", 4, 5000, ["Purple"], "Kid Pirates"))

    if card_id in {"OP05-099", "OP05-114", "OP05-115", "OP05-116"} and tc.card_type != "LEADER":
        p1.leader = _make_seed_card("OP05-098", "Enel", "LEADER", None, 5000, ["Yellow"], "Sky Island")
        p1.leader.life = 4

    if card_id == "OP05-018":
        p1.hand.insert(0, _make_seed_card("REV-018", "Rev Army Recruit", "CHARACTER", 4, 5000, ["Red"], "Revolutionary Army"))

    if card_id == "OP05-020":
        p2.cards_in_play.append(_make_seed_card("OPP-020", "Low Power Target", "CHARACTER", 2, 2000, ["Blue"], "Navy"))

    if card_id in {"OP05-037", "OP05-038"}:
        p1.hand.insert(0, _make_seed_card(f"HAND-{card_id}", "Discard Fodder", "CHARACTER", 2, 3000, ["Green"], "Donquixote Pirates"))

    if card_id == "OP05-039":
        p2.cards_in_play.append(_make_seed_card("OPP-039", "Rested Small Target", "CHARACTER", 3, 4000, ["Green"], "Donquixote Pirates", rested=True))

    if card_id == "OP05-056":
        p1.cards_in_play.append(_make_seed_card("ALLY-056", "Blue Ally", "CHARACTER", 3, 4000, ["Blue"], "Former Navy"))

    if card_id == "OP05-057":
        p1.cards_in_play.append(_make_seed_card("ALLY-057", "Own Small Character", "CHARACTER", 2, 3000, ["Blue"], "Navy"))

    if card_id == "OP05-058":
        p1.cards_in_play.append(_make_seed_card("SMALL-058-A", "Your Small Character", "CHARACTER", 3, 4000, ["Blue"], "Navy"))
        p2.cards_in_play.append(_make_seed_card("SMALL-058-B", "Opp Small Character", "CHARACTER", 2, 3000, ["Blue"], "Navy"))
        while len(p1.hand) < 7:
            p1.hand.append(_make_dummy_card(700 + len(p1.hand)))
        while len(p2.hand) < 7:
            p2.hand.append(_make_dummy_card(800 + len(p2.hand)))

    if card_id == "OP05-081":
        p2.cards_in_play.append(_make_seed_card("OPP-081", "Cost Target", "CHARACTER", 4, 5000, ["Black"], "Dressrosa"))

    if card_id == "OP05-082":
        while len(p1.trash) < 2:
            p1.trash.append(_make_seed_card(f"TRASH-082-{len(p1.trash)}", "Trash Seed", "CHARACTER", 2, 3000, ["Black"], "Dressrosa"))
        while len(p2.hand) < 6:
            p2.hand.append(_make_dummy_card(820 + len(p2.hand)))

    if card_id == "OP05-084":
        p1.cards_in_play = [c for c in p1.cards_in_play if c == tc]
        p1.cards_in_play.append(_make_seed_card("CD-084", "Celestial Ally", "CHARACTER", 2, 3000, ["Black"], "Celestial Dragons"))

    if card_id == "OP05-087":
        p1.cards_in_play.append(_make_seed_card("ALLY-087", "Dressrosa Ally", "CHARACTER", 3, 4000, ["Black"], "Dressrosa"))
        p2.cards_in_play.append(_make_seed_card("OPP-087", "Cost Five Target", "CHARACTER", 5, 6000, ["Black"], "Dressrosa"))

    if card_id == "OP05-088":
        while len(p1.trash) < 2:
            p1.trash.append(_make_seed_card(f"TRASH-088-{len(p1.trash)}", "Trash Seed", "CHARACTER", 2, 3000, ["Black"], "Dressrosa"))
        p1.trash.append(_make_seed_card("BLACK-088", "Recoverable Black 4", "CHARACTER", 4, 5000, ["Black"], "Dressrosa"))

    if card_id == "OP05-089":
        p1.cards_in_play.append(_make_seed_card("ALLY-089", "Black Ally", "CHARACTER", 2, 3000, ["Black"], "Celestial Dragons"))
        p1.trash.append(_make_seed_card("BLACK-089", "Recoverable Black 1", "CHARACTER", 1, 2000, ["Black"], "Celestial Dragons"))

    if card_id == "OP05-090":
        p1.cards_in_play.append(_make_seed_card("DRESS-090", "Dressrosa Target", "CHARACTER", 4, 5000, ["Black"], "Dressrosa"))

    if card_id == "OP05-093":
        while len(p1.trash) < 3:
            p1.trash.append(_make_seed_card(f"TRASH-093-OP05-{len(p1.trash)}", "Trash Seed", "CHARACTER", 2, 3000, ["Black"], "CP0"))
        p2.cards_in_play.append(_make_seed_card("KO2-093", "Cost 2 Target", "CHARACTER", 2, 3000, ["Black"], "CP0"))
        p2.cards_in_play.append(_make_seed_card("KO1-093", "Cost 1 Target", "CHARACTER", 1, 2000, ["Black"], "CP0"))

    if card_id == "OP05-094":
        p2.cards_in_play.append(_make_seed_card("PATCH-094", "Cost 3 Target", "CHARACTER", 3, 4000, ["Black"], "Dressrosa"))

    if card_id == "OP05-096":
        p1.cards_in_play.append(_make_seed_card("CD-096", "Celestial Noble", "CHARACTER", 2, 3000, ["Black"], "Celestial Dragons"))
        p2.cards_in_play.append(_make_seed_card("LOW-096", "Cost 1 Target", "CHARACTER", 1, 2000, ["Black"], "Navy"))

    if card_id == "OP05-097":
        p1.hand.insert(0, _make_seed_card("CD-HAND-097", "Celestial Dragons Hand Card", "CHARACTER", 3, 4000, ["Black"], "Celestial Dragons"))

    if card_id == "OP05-099":
        if not p2.life_cards and p2.deck:
            p2.life_cards.append(p2.deck.pop(0))

    if card_id == "OP05-115":
        p1.life_cards = p1.life_cards[:1]
        while len(p1.hand) < 3:
            p1.hand.append(_make_dummy_card(1150 + len(p1.hand)))

    if card_id == "OP05-116":
        p2.life_cards = p2.life_cards[:2]
        p2.cards_in_play.append(_make_seed_card("ZAP-116", "Life-Count Target", "CHARACTER", 2, 3000, ["Yellow"], "Sky Island"))

    if card_id == "OP05-119":
        p1.cards_in_play.append(_make_seed_card("ALLY-119-A", "Bottom Deck Ally A", "CHARACTER", 4, 5000, ["Purple"], "Straw Hat Crew"))
        p1.cards_in_play.append(_make_seed_card("ALLY-119-B", "Bottom Deck Ally B", "CHARACTER", 3, 4000, ["Purple"], "Straw Hat Crew"))

    return gs, p1, tc


# ═══════════════════════════════════════════════════════════════════
# State snapshot / diff
# ═══════════════════════════════════════════════════════════════════

def _snapshot(player: Player, opponent: Player) -> dict:
    def _field_repr(cards):
        return [
            f"{c.name} pow={c.power or 0}+{getattr(c,'power_modifier',0)} "
            f"don={getattr(c,'attached_don',0)} rest={c.is_resting}"
            for c in cards
        ]
    return {
        "hand":        len(player.hand),
        "field":       _field_repr(player.cards_in_play),
        "trash":       len(player.trash),
        "life":        len(player.life_cards),
        "don_active":  player.don_pool.count("active"),
        "don_rested":  player.don_pool.count("rested"),
        "opp_field":   _field_repr(opponent.cards_in_play),
        "opp_life":    len(opponent.life_cards),
        "opp_hand":    len(opponent.hand),
    }


def _diff(before: dict, after: dict) -> List[str]:
    labels = {
        "hand":       "Your hand count",
        "field":      "Your field",
        "trash":      "Your trash count",
        "life":       "Your life count",
        "don_active": "Your active DON",
        "don_rested": "Your rested DON",
        "opp_field":  "Opp field",
        "opp_life":   "Opp life count",
        "opp_hand":   "Opp hand count",
    }
    out = []
    for key, label in labels.items():
        b, a = before[key], after[key]
        if b != a:
            out.append(f"  {GREEN}{label}:{RST}  {DIM}{b}{RST}  →  {a}")
    return out


# ═══════════════════════════════════════════════════════════════════
# Data loading
# ═══════════════════════════════════════════════════════════════════

def load_card_db() -> Dict[str, dict]:
    with open(CARDS_JSON, encoding="utf-8") as f:
        raw = json.load(f)
    db: Dict[str, dict] = {}
    for entry in raw:
        cid = entry.get("id_normal") or entry.get("id", "")
        if cid and cid not in db:
            db[cid] = entry
    return db


def parse_status_entries(set_code: str) -> List[dict]:
    if not STATUS_FILE.exists():
        return []
    out = []
    for line in STATUS_FILE.read_text(encoding="utf-8").splitlines():
        if not line.startswith(f"| {set_code}"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 7:
            continue
        out.append({
            "id":     parts[1],
            "name":   parts[2],
            "type":   parts[3],
            "status": parts[4],
            "effect": parts[5],
            "notes":  parts[6],
        })
    return out


def update_status(card_id: str, new_status: str, notes: str = None):
    if not STATUS_FILE.exists():
        return
    text = STATUS_FILE.read_text(encoding="utf-8")
    lines = text.splitlines()
    new_lines = []
    for line in lines:
        if line.startswith(f"| {card_id} |"):
            parts = line.split("|")
            if len(parts) >= 7:
                parts[4] = f" {new_status} "
                if notes is not None:
                    parts[6] = f" {notes} "
                line = "|".join(parts)
        new_lines.append(line)
    result = "\n".join(new_lines)
    # Refresh footer counts
    result = re.sub(r"\*\*Verified:\*\*.*",       f"**Verified:** {result.count('✅ Verified')}", result)
    result = re.sub(r"\*\*Missing:\*\*.*",         f"**Missing:** {result.count('❌ Missing')}", result)
    result = re.sub(r"\*\*To Do \(audit\):\*\*.*", f"**To Do (audit):** {result.count('🔲 To Do')}", result)
    STATUS_FILE.write_text(result, encoding="utf-8")


def get_timings(card_id: str) -> List[str]:
    base_id = card_id.split("_")[0] if ("_p" in card_id or "_r" in card_id) else card_id
    effects = _hardcoded_effects.get(card_id, [])
    if base_id != card_id:
        effects = effects + _hardcoded_effects.get(base_id, [])
    return list(dict.fromkeys(e.timing for e in effects))  # preserve order, deduplicate


# ═══════════════════════════════════════════════════════════════════
# Main tester loop
# ═══════════════════════════════════════════════════════════════════

def run_tester(
    set_code: str = "OP01",
    start_from: str = None,
    filter_status: str = "todo",
    single_card: str = None,
):
    print(f"\n{BOLD}Loading card data…{RST}")
    card_db = load_card_db()

    entries = parse_status_entries(set_code)
    if not entries:
        print(f"{RED}No entries for {set_code} in CARD_STATUS.md{RST}")
        print(f"Run:  python gen_card_status.py {set_code}")
        return

    # Filter
    if single_card:
        entries = [e for e in entries if e["id"] == single_card]
    elif filter_status == "todo":
        entries = [e for e in entries if e["status"] == "🔲 To Do"]
    elif filter_status == "needsfix":
        entries = [e for e in entries if e["status"] in ("🔲 To Do", "⚠ Needs Fix")]
    else:  # all
        entries = [e for e in entries if e["status"] not in ("⬜ No Effect", "⬜ Keywords")]

    # Resume from
    if start_from:
        idx = next((i for i, e in enumerate(entries) if e["id"] == start_from), None)
        if idx is not None:
            entries = entries[idx:]
        else:
            print(f"{YLW}Warning: --from {start_from} not found, starting from beginning{RST}")

    if not entries:
        print(f"{YLW}No cards to test with current filters.{RST}")
        return

    total = len(entries)
    print(f"\n{BOLD}Testing {total} card(s) in {set_code}{RST}  "
          f"{DIM}(ctrl+c or Q to quit){RST}")
    print(f"{DIM}Commands: [P]ass  [F]ail  [S]kip  [N]ote  [R]erun  [Q]uit{RST}\n")

    results = {"pass": 0, "fail": 0, "skip": 0}

    for idx, entry in enumerate(entries, 1):
        card_id = entry["id"]
        card_data = card_db.get(card_id)
        if not card_data:
            print(f"{YLW}⚠ {card_id} not in cards.json — skipping{RST}")
            continue

        timings = get_timings(card_id)
        if not timings:
            print(f"{YLW}⚠ {card_id} has no registered effects — skipping{RST}")
            continue

        # ── Card header ──────────────────────────────────────────
        print(f"\n{BOLD}{SEP}{RST}")
        print(f"{BOLD}[{idx}/{total}]  {card_id} — {entry['name']}  ({entry['type']}){RST}")
        print(f"Timings: {CYAN}{', '.join(timings)}{RST}")
        print(f"{DIM}{SEP}{RST}")

        effect_text = re.sub(r"<[^>]+>", " ", card_data.get("Effect") or "").strip()
        trigger_text = re.sub(r"<[^>]+>", " ", card_data.get("Trigger") or "").strip()
        if effect_text:
            print(f"{BOLD}Effect:{RST}  {effect_text}")
        if trigger_text:
            print(f"{BOLD}Trigger:{RST} {trigger_text}")
        if entry["notes"]:
            print(f"{DIM}Notes:   {entry['notes']}{RST}")

        while True:  # allow R to rerun
            # ── Run each timing ───────────────────────────────────
            for timing in timings:
                print(f"\n  {CYAN}▸ timing: {timing}{RST}")
                try:
                    test_card = make_test_card(card_data)
                    gs, player, tc = build_game_state(test_card, timing)
                    opponent = gs.opponent_player

                    # Print setup summary
                    print(f"  {DIM}You:  "
                          f"DON {player.don_pool.count('active')}A/{player.don_pool.count('rested')}R  "
                          f"hand={len(player.hand)}  "
                          f"field=[{', '.join(c.name for c in player.cards_in_play) or '—'}]  "
                          f"life={len(player.life_cards)}{RST}")
                    print(f"  {DIM}Opp:  "
                          f"field=[{', '.join(c.name for c in opponent.cards_in_play) or '—'}]  "
                          f"life={len(opponent.life_cards)}{RST}")

                    before = _snapshot(player, opponent)

                    # Execute with captured stdout
                    captured = io.StringIO()
                    exc_info = None
                    with redirect_stdout(captured):
                        try:
                            result = execute_hardcoded_effect(gs, player, tc, timing)
                        except Exception:
                            result = None
                            exc_info = traceback.format_exc()

                    after = _snapshot(player, opponent)
                    changes = _diff(before, after)
                    stdout_lines = [l for l in captured.getvalue().splitlines() if l.strip()]

                    # ── Results ───────────────────────────────────
                    print(f"\n  {BOLD}Returned:{RST} {result}")

                    if exc_info:
                        print(f"\n  {RED}EXCEPTION:{RST}")
                        for line in exc_info.splitlines():
                            print(f"    {RED}{line}{RST}")

                    if stdout_lines:
                        print(f"\n  {BOLD}Print output:{RST}")
                        for line in stdout_lines[:30]:
                            print(f"    {DIM}{line}{RST}")
                        if len(stdout_lines) > 30:
                            print(f"    {DIM}… ({len(stdout_lines) - 30} more lines){RST}")

                    if gs.action_logs:
                        print(f"\n  {BOLD}Action logs:{RST}")
                        for log in gs.action_logs[-15:]:
                            print(f"    {log}")

                    if changes:
                        print(f"\n  {BOLD}State changes:{RST}")
                        for ch in changes:
                            print(ch)
                    else:
                        print(f"\n  {DIM}(no measurable state changes){RST}")

                    if gs.pending_choice:
                        pc = gs.pending_choice
                        print(f"\n  {BOLD}Pending choice:{RST}  {YLW}{pc.prompt}{RST}")
                        print(f"    type={pc.choice_type}  action={pc.callback_action}  "
                              f"min={pc.min_selections}  max={pc.max_selections}")
                        for opt in pc.options[:6]:
                            print(f"    • {opt.get('label', opt.get('id', '?'))}")
                        if len(pc.options) > 6:
                            print(f"    … +{len(pc.options) - 6} more options")

                except Exception:
                    print(f"\n  {RED}ERROR in test setup:{RST}")
                    traceback.print_exc()

            # ── Verdict prompt ────────────────────────────────────
            print(f"\n{BOLD}Mark as:{RST}  "
                  f"[{GREEN}P{RST}]ass  "
                  f"[{RED}F{RST}]ail  "
                  f"[{YLW}S{RST}]kip  "
                  f"[N]ote  [R]erun  [Q]uit  > ", end="", flush=True)
            try:
                choice = input().strip().lower()
            except (EOFError, KeyboardInterrupt):
                print(f"\n{YLW}Interrupted.{RST}")
                _print_summary(results)
                return

            if choice == "q":
                _print_summary(results)
                return

            elif choice == "r":
                print(f"  {DIM}Re-running…{RST}")
                continue  # while True

            elif choice == "p":
                update_status(card_id, "✅ Verified")
                results["pass"] += 1
                print(f"  {GREEN}✅ Verified{RST}")
                break

            elif choice == "f":
                print(f"  Note (leave blank if none): ", end="", flush=True)
                try:
                    note = input().strip()
                except (EOFError, KeyboardInterrupt):
                    note = ""
                update_status(card_id, "⚠ Needs Fix", note or None)
                results["fail"] += 1
                print(f"  {RED}⚠ Marked as Needs Fix{RST}")
                break

            elif choice == "n":
                print(f"  Note text: ", end="", flush=True)
                try:
                    note = input().strip()
                except (EOFError, KeyboardInterrupt):
                    note = ""
                if note:
                    update_status(card_id, entry["status"], note)
                    entry["notes"] = note
                    print(f"  {CYAN}Note saved (status unchanged){RST}")
                # Show verdict prompt again
                continue

            else:  # S, enter, anything else = skip
                results["skip"] += 1
                print(f"  {YLW}Skipped{RST}")
                break

    _print_summary(results)


def _print_summary(results: dict):
    print(f"\n{BOLD}{'═' * 30} Session Summary {'═' * 30}{RST}")
    print(f"  {GREEN}✅ Passed:  {results['pass']}{RST}")
    print(f"  {RED}⚠  Failed:  {results['fail']}{RST}")
    print(f"  {YLW}⬜ Skipped: {results['skip']}{RST}")
    print()


# ═══════════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    epilog_text = (
        "Controls at the prompt:\n"
        "  P  -- Pass: mark as Verified\n"
        "  F  -- Fail: mark as Needs Fix (optionally add a note)\n"
        "  S  -- Skip: leave status unchanged\n"
        "  N  -- Add / edit note without changing status\n"
        "  R  -- Rerun: re-execute the effect\n"
        "  Q  -- Quit: show session summary and exit\n"
    )
    parser = argparse.ArgumentParser(
        description="Interactive card effect tester",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog_text,
    )
    parser.add_argument(
        "target", nargs="?", default="OP01",
        help="Set code (OP01) or specific card ID (OP01-006). Default: OP01",
    )
    parser.add_argument(
        "--from", dest="start_from", metavar="CARD_ID",
        help="Resume testing from a specific card ID",
    )
    parser.add_argument(
        "--status", choices=["todo", "needsfix", "all"], default="todo",
        help="Which cards to test: todo (default), needsfix, all",
    )
    args = parser.parse_args()

    target = args.target
    if re.match(r"^[A-Za-z]{2}\d{2}-\d+$", target):
        # Specific card — derive set code from prefix
        set_code = re.match(r"^([A-Za-z]{2}\d{2})", target).group(1).upper()
        run_tester(set_code=set_code, single_card=target.upper())
    else:
        run_tester(
            set_code=target.upper(),
            start_from=args.start_from,
            filter_status=args.status,
        )
