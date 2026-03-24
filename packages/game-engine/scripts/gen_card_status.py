"""
Generate CARD_STATUS.md for effect tracking.
Usage: python gen_card_status.py [SET_PREFIX]
  e.g. python gen_card_status.py OP01
"""

import json
import re
import sys
from pathlib import Path

SET_PREFIX = sys.argv[1] if len(sys.argv) > 1 else "OP01"

# Paths
ROOT = Path(__file__).parent.parent.parent.parent
CARDS_JSON = ROOT / "packages" / "simulator" / "backend" / "data" / "cards.json"
EFFECTS_DIR = ROOT / "packages" / "game-engine" / "optcg_engine" / "effects" / "sets"
STATUS_FILE = ROOT / "packages" / "game-engine" / "optcg_engine" / "effects" / "CARD_STATUS.md"

# Load cards
with open(CARDS_JSON, encoding="utf-8") as f:
    all_cards = json.load(f)

# Filter to this set, deduplicate by id_normal (skip _p1, _alt variants)
set_cards = []
seen_ids = set()
for c in all_cards:
    card_id = c.get("id_normal") or c.get("id", "")
    if not card_id.startswith(SET_PREFIX):
        continue
    if card_id in seen_ids:
        continue
    seen_ids.add(card_id)
    set_cards.append(c)

set_cards.sort(key=lambda c: c.get("id_normal") or c.get("id", ""))

# Check which IDs have hardcoded implementations
effects_file = EFFECTS_DIR / f"{SET_PREFIX.lower()}_effects.py"
hardcoded_ids = set()
timings_by_id = {}
if effects_file.exists():
    content = effects_file.read_text(encoding="utf-8")
    for m in re.finditer(r'@register_effect\("([^"]+)",\s*"([^"]+)"', content):
        cid, timing = m.group(1), m.group(2)
        hardcoded_ids.add(cid)
        timings_by_id.setdefault(cid, []).append(timing)

# Keywords handled by parser (no hardcoded needed)
KEYWORD_ONLY_PATTERNS = [
    r'^\[Rush\]$',
    r'^\[Blocker\]$',
    r'^\[Banish\]$',
    r'^\[Double Attack\]$',
]

def is_keyword_only(effect_text):
    if not effect_text:
        return False
    # Strip HTML
    text = re.sub(r'<[^>]+>', ' ', effect_text).strip()
    parts = re.split(r'\s*\n\s*|\s*<br\s*/?>\s*', text)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if not any(re.match(p, part) for p in KEYWORD_ONLY_PATTERNS):
            return False
    return True

# Build status table
rows = []
for c in set_cards:
    card_id = c.get("id_normal") or c.get("id", "")
    name = c.get("name", "?")
    card_type = c.get("cardType", "?")
    effect = c.get("Effect") or ""
    trigger = c.get("Trigger") or ""
    has_effect = bool(effect or trigger)

    if not has_effect:
        status = "⬜ No Effect"
        notes = ""
    elif is_keyword_only(effect):
        status = "⬜ Keywords"
        notes = "Handled by parser"
    elif card_id in hardcoded_ids:
        timings = ", ".join(timings_by_id.get(card_id, []))
        status = "🔲 To Do"
        notes = f"Impl exists: {timings}"
    else:
        status = "❌ Missing"
        notes = ""

    # Summarize effect text (first 60 chars, no HTML)
    effect_summary = re.sub(r'<[^>]+>', ' ', effect).strip()
    effect_summary = re.sub(r'\s+', ' ', effect_summary)[:70]
    if len(effect) > 70:
        effect_summary += "…"

    rows.append((card_id, name, card_type, status, effect_summary, notes))

# Write markdown
lines = [
    f"# Card Effect Status — {SET_PREFIX}",
    "",
    "## Status Legend",
    "- `✅ Verified` — Implemented and confirmed correct in simulator",
    "- `⚠ Needs Fix` — Implementation exists but has a bug or mismatch",
    "- `🔲 To Do` — Hardcoded impl exists, needs audit/verification",
    "- `❌ Missing` — No implementation, needs writing",
    "- `⬜ No Effect` / `⬜ Keywords` — No custom code needed",
    "",
    f"| ID | Name | Type | Status | Effect (summary) | Notes |",
    f"|----|----|------|--------|-----------------|-------|",
]

for card_id, name, card_type, status, effect_summary, notes in rows:
    lines.append(f"| {card_id} | {name} | {card_type} | {status} | {effect_summary} | {notes} |")

lines.append("")
lines.append(f"**Total:** {len(rows)} cards")
lines.append(f"**Missing:** {sum(1 for r in rows if r[3] == '❌ Missing')}")
lines.append(f"**To Do (audit):** {sum(1 for r in rows if r[3] == '🔲 To Do')}")
lines.append(f"**Verified:** {sum(1 for r in rows if r[3] == '✅ Verified')}")

# If status file exists, read it to preserve existing verified/needs-fix entries
if STATUS_FILE.exists():
    existing = STATUS_FILE.read_text(encoding="utf-8")
    # Find verified or needs-fix IDs
    preserved = {}
    for m in re.finditer(r'\| (OP\d+-\d+) \|[^|]+\|[^|]+\| (✅ Verified|⚠ Needs Fix) \| ([^|]*) \| ([^|]*) \|', existing):
        cid, st, eff, note = m.group(1), m.group(2), m.group(3), m.group(4)
        preserved[cid] = (st, note)
    if preserved:
        # Re-apply preserved statuses
        new_lines = []
        for line in lines:
            updated = False
            for cid, (st, note) in preserved.items():
                if line.startswith(f"| {cid} |"):
                    parts = line.split("|")
                    parts[4] = f" {st} "
                    parts[6] = f" {note.strip()} "
                    line = "|".join(parts)
                    updated = True
                    break
            new_lines.append(line)
        lines = new_lines

STATUS_FILE.write_text("\n".join(lines), encoding="utf-8")
print(f"Written {len(rows)} {SET_PREFIX} cards to {STATUS_FILE}")
print(f"  Missing implementations: {sum(1 for r in rows if r[3] == '❌ Missing')}")
print(f"  Existing impl (to audit): {sum(1 for r in rows if r[3] == '🔲 To Do')}")
