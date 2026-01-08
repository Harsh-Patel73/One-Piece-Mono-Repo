import json

# Path to your english_cards.json file
with open("backend/data/english_cards.json", "r", encoding="utf-8") as f:
    cards = json.load(f)

# Store seen ids to avoid duplicates
seen_ids = set()

# Header for the effect_handlers.py script
lines = [
    "from game_engine import GameState, Player, Card\n",
    "from typing import Optional\n",
    "\n",
    "# One Play Effect Handlers\n",
    "effect_handlers = {}\n",
]

# Loop through each card
for card in cards:
    card_id = card.get("id_normal")
    if not card_id or card_id in seen_ids:
        continue
    seen_ids.add(card_id)

    effect_text = card.get("Effect")
    if not isinstance(effect_text, str):
        effect_text = ""
    else:
        effect_text = effect_text.strip().replace("\n", " ")


    # Build handler stub
    handler = f"""
# {effect_text or "No effect text available."}
def {card_id}_on_play(game_state: GameState, player: Player, card: Card):
    # TODO: Implement effect for {card.get('name', 'Unknown')} ({card_id})
    pass

effect_handlers["{card_id}"] = {card_id}_on_play
"""
    lines.append(handler)

# Save to effect_handlers.py
with open("backend/handlers/effect_handlers.py", "w", encoding="utf-8") as f:
    f.writelines(lines)

print("✅ effect_handlers.py generated successfully.")
