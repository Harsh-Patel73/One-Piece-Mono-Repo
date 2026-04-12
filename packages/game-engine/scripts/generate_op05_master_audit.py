#!/usr/bin/env python3
"""
Generate a repo-tracked OP05 master audit from the card database, effect file,
and current CARD_STATUS tracker.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CARDS_JSON = ROOT / "packages" / "game-engine" / "data" / "english_cards.json"
STATUS_MD = ROOT / "packages" / "game-engine" / "optcg_engine" / "effects" / "CARD_STATUS.md"
OP05_EFFECTS = ROOT / "packages" / "game-engine" / "optcg_engine" / "effects" / "sets" / "op05_effects.py"
OUTPUT_MD = ROOT / "packages" / "game-engine" / "optcg_engine" / "effects" / "OP05_MASTER_AUDIT.md"


def normalize_text(text: str) -> str:
    text = html.unescape(text or "")
    text = text.replace("<br>", " / ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def short_summary(effect: str, trigger: str) -> str:
    pieces = []
    if effect:
        pieces.append(effect)
    if trigger:
        pieces.append(trigger)
    summary = " Trigger: ".join(pieces)
    return summary if len(summary) <= 180 else f"{summary[:177]}..."


def parse_status_rows() -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    for line in STATUS_MD.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| OP05-"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 7:
            continue
        rows[parts[1]] = {
            "name": parts[2],
            "type": parts[3],
            "status": parts[4],
            "summary": parts[5],
            "notes": parts[6],
        }
    return rows


def parse_registered_timings() -> dict[str, list[str]]:
    text = OP05_EFFECTS.read_text(encoding="utf-8")
    timings: dict[str, list[str]] = {}
    for card_id, timing in re.findall(r'@register_effect\("((?:OP05-\d{3}))",\s*"([^"]+)"', text):
        timings.setdefault(card_id, []).append(timing)
    return timings


def infer_expected_timings(effect: str, trigger: str) -> set[str]:
    expected: set[str] = set()
    source = effect
    if "[Activate: Main]" in source:
        expected.add("activate")
    if "[On Play]" in source:
        expected.add("on_play")
    if "[On K.O.]" in source:
        expected.add("on_ko")
    if "[When Attacking]" in source:
        expected.add("on_attack")
    if "[On Your Opponent's Attack]" in source or "[On Opponent's Attack]" in source:
        expected.add("on_opponent_attack")
    if "[On Block]" in source:
        expected.add("on_block")
    if "[End of Your Turn]" in source:
        expected.add("end_of_turn")
    if "[Your Turn]" in source or "[Opponent's Turn]" in source:
        if "would be K.O.'d" in source:
            expected.add("on_ko_prevention")
        else:
            expected.add("continuous")
    if "[Once Per Turn] When a [Trigger] activates" in source:
        expected.add("on_trigger")
    if "When a card is added to your hand from your Life" in source:
        expected.add("on_life_add")
    if "When your number of Life cards becomes 0" in source:
        expected.add("on_life_zero")
    if "[Trigger]" in trigger:
        expected.add("trigger")
    return expected


def classify_state(card: dict, status_row: dict[str, str] | None, timings: list[str]) -> tuple[str, str]:
    effect = normalize_text(card.get("Effect") or "")
    trigger = normalize_text(card.get("Trigger") or "")
    notes = (status_row or {}).get("notes", "")
    status = (status_row or {}).get("status", "")

    if "Needs Fix" in status:
        return ("existing handler and mismatch", notes or "Existing implementation is known to diverge from printed text.")

    if not effect and not trigger:
        if timings:
            return (
                "existing handler, but printed custom text is absent",
                "Verify this card only needs keyword / baseline handling and remove stale hardcoded logic if unnecessary.",
            )
        return ("no custom code actually needed", "Add tracker coverage and verify the simulator does not need card-specific logic.")

    if not timings:
        return ("missing handler", "Implement the printed effect and trigger from scratch with exact prompts, costs, and duration.")

    expected = infer_expected_timings(effect, trigger)
    normalized_timings = {t.lower() for t in timings}
    missing_timings = [t for t in sorted(expected) if t.lower() not in normalized_timings]
    if missing_timings:
        return (
            "partial handler",
            f"Add the missing timing hook(s): {', '.join(missing_timings)}. Then audit the full printed branches against the current code.",
        )

    return (
        "existing handler, untracked",
        "Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.",
    )


def helper_note(effect: str, trigger: str, current_state: str) -> str:
    source = f"{effect} {trigger}"
    notes: list[str] = []
    if "Leader or Character" in source:
        notes.append("Leader-or-Character target prompt")
    if "up to 2" in source or "up to 3" in source or "total power" in source:
        notes.append("multi-target selection helper")
    if "total power" in source:
        notes.append("sum-constrained KO selection")
    if "DON!!" in source or "rested DON!!" in source or "➀" in source:
        notes.append("DON cost / DON state helper")
    if "would be K.O.'d" in source or "instead" in source:
        notes.append("KO replacement / prevention hook")
    if "top of your deck" in source or "Look at 5 cards" in source or "Look at 3 cards" in source:
        notes.append("search / reorder helper")
    if "Life" in source:
        notes.append("Life-area helper")
    if current_state == "no custom code actually needed":
        return "None expected."
    return "; ".join(notes) if notes else "None expected beyond the existing effect helpers."


def seed_note(effect: str, trigger: str) -> str:
    source = f"{effect} {trigger}"
    seeds: list[str] = []
    if "{Revolutionary Army}" in source:
        seeds.append("Revolutionary Army leader / hand / field")
    if "{Donquixote Pirates}" in source:
        seeds.append("Donquixote Pirates field / hand")
    if "{Kid Pirates}" in source:
        seeds.append("Kid Pirates leader / field")
    if "{Celestial Dragons}" in source:
        seeds.append("Celestial Dragons field / hand")
    if "{Sky Island}" in source:
        seeds.append("Sky Island deck / field")
    if "multicolored" in source:
        seeds.append("multicolor leader")
    if "7000 power" in source:
        seeds.append("7000+ power setup")
    if "8 or more DON!!" in source or "10 DON!!" in source or "DON!! −" in source or "➀" in source:
        seeds.append("specific DON threshold")
    if "trash" in source:
        seeds.append("trash count / trash contents")
    if "Life" in source:
        seeds.append("life count / life pile setup")
    if "rested" in source:
        seeds.append("rested targets")
    if "cost of" in source or "power or less" in source:
        seeds.append("exact cost / power breakpoints")
    return "; ".join(seeds) if seeds else "Default board state is likely enough."


def acceptance_line(effect: str, trigger: str, current_state: str) -> str:
    if current_state == "no custom code actually needed":
        return "Tracker row exists and the card plays correctly with baseline keyword / core engine behavior only."
    if trigger:
        return "Printed main / trigger text resolves with the correct timing, prompts, costs, zone moves, and no exceptions."
    return "Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions."


def main() -> None:
    cards = json.loads(CARDS_JSON.read_text(encoding="utf-8"))
    base_cards = {
        c["id"]: c
        for c in cards
        if re.fullmatch(r"OP05-\d{3}", c.get("id", ""))
    }
    status_rows = parse_status_rows()
    reg = parse_registered_timings()

    verified_ids = {
        cid for cid, row in status_rows.items()
        if "Verified" in row.get("status", "")
    }
    worklist = [base_cards[cid] for cid in sorted(base_cards) if cid not in verified_ids]

    lines: list[str] = []
    lines.append("# OP05 Master Audit")
    lines.append("")
    lines.append("Generated from `english_cards.json`, `op05_effects.py`, and the current OP05 rows in `CARD_STATUS.md`.")
    lines.append("")
    lines.append("## Queue Summary")
    lines.append("")
    lines.append(f"- OP05 base cards: {len(base_cards)}")
    lines.append(f"- Currently verified: {len(verified_ids)}")
    needs_fix_ids = [cid for cid, row in status_rows.items() if "Needs Fix" in row.get("status", "")]
    lines.append(f"- Already marked Needs Fix: {len(needs_fix_ids)}")
    lines.append(f"- Untracked base cards: {len(worklist) - len(needs_fix_ids)}")
    lines.append(f"- Implementation queue: {len(worklist)}")
    lines.append("")
    lines.append("## First Lane")
    lines.append("")
    for cid in sorted(needs_fix_ids):
        row = status_rows[cid]
        lines.append(f"- `{cid}` {row['name']}")
    lines.append("")
    lines.append("## Master Worklist")
    lines.append("")

    for card in worklist:
        cid = card["id"]
        status_row = status_rows.get(cid)
        effect = normalize_text(card.get("Effect") or "")
        trigger = normalize_text(card.get("Trigger") or "")
        timings = reg.get(cid, [])
        current_state, missing = classify_state(card, status_row, timings)
        lines.append(f"### {cid} {card['name']}")
        lines.append(f"- Printed: {short_summary(effect, trigger) if effect or trigger else 'No printed custom effect or trigger text.'}")
        lines.append(f"- Current state: {current_state}. Registered timings: `{', '.join(timings) if timings else 'none'}`.")
        lines.append(f"- Missing behavior: {missing}")
        lines.append(f"- Required engine/helper support: {helper_note(effect, trigger, current_state)}")
        lines.append(f"- Required test seeding: {seed_note(effect, trigger)}")
        lines.append(f"- Acceptance: {acceptance_line(effect, trigger, current_state)}")
        lines.append("")

    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUTPUT_MD}")


if __name__ == "__main__":
    main()
