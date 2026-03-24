"""
Script to identify all cards with non-working effects.

Categorizes cards into:
1. Leader condition cards - "If your Leader..."
2. Sacrifice cost cards - "You may return X of your Characters"
3. Complex choice cards - Multiple options
4. Other unparseable effects
"""

import json
import re
from pathlib import Path
from collections import defaultdict

# Load card database
cards_path = Path(__file__).parent.parent.parent / "simulator" / "backend" / "data" / "cards.json"

with open(cards_path, 'r', encoding='utf-8') as f:
    cards_data = json.load(f)

# Load hardcoded effects to know which cards are already covered
hardcoded_path = Path(__file__).parent.parent / "optcg_engine" / "effects" / "hardcoded.py"
hardcoded_content = hardcoded_path.read_text(encoding='utf-8')

# Extract hardcoded card IDs using regex
hardcoded_card_ids = set(re.findall(r'@register_effect\(["\']([A-Z0-9-]+)["\']', hardcoded_content))

print(f"Found {len(hardcoded_card_ids)} cards with hardcoded effects")

# Categories for non-working cards
leader_condition_cards = []
sacrifice_cost_cards = []
complex_choice_cards = []
reveal_cost_cards = []
life_condition_cards = []
trash_condition_cards = []
other_unparseable = []

# Patterns that indicate problematic effects
LEADER_CONDITION_PATTERNS = [
    r"if your leader['\u2019]?s? type includes",
    r"if your leader is",
    r"if your leader has",
    r"your leader['\u2019]?s? type includes",
]

SACRIFICE_COST_PATTERNS = [
    r"you may return \d+ of your",
    r"you may trash \d+ of your",
    r"by returning",
    r"by trashing.*from your",
]

REVEAL_COST_PATTERNS = [
    r"you may reveal.*from your hand:",
    r"reveal \d+ cards? with",
]

LIFE_CONDITION_PATTERNS = [
    r"if you have \d+ or less life",
    r"if you have \d+ or more life",
    r"if your opponent has \d+ or less life",
]

TRASH_CONDITION_PATTERNS = [
    r"if you have \d+ or more cards? in your trash",
    r"if there are \d+ or more cards? in your trash",
]

COMPLEX_CHOICE_PATTERNS = [
    r"choose one:",
    r"choose up to \d+ of the following",
    r"do one of the following",
]

def categorize_card(card_id, effect_text):
    """Categorize a card based on its effect text patterns."""
    if not effect_text:
        return None

    effect_lower = effect_text.lower()

    # Check leader conditions
    for pattern in LEADER_CONDITION_PATTERNS:
        if re.search(pattern, effect_lower):
            return "leader_condition"

    # Check sacrifice costs
    for pattern in SACRIFICE_COST_PATTERNS:
        if re.search(pattern, effect_lower):
            return "sacrifice_cost"

    # Check reveal costs
    for pattern in REVEAL_COST_PATTERNS:
        if re.search(pattern, effect_lower):
            return "reveal_cost"

    # Check life conditions
    for pattern in LIFE_CONDITION_PATTERNS:
        if re.search(pattern, effect_lower):
            return "life_condition"

    # Check trash conditions
    for pattern in TRASH_CONDITION_PATTERNS:
        if re.search(pattern, effect_lower):
            return "trash_condition"

    # Check complex choices
    for pattern in COMPLEX_CHOICE_PATTERNS:
        if re.search(pattern, effect_lower):
            return "complex_choice"

    return None

# Process all cards
cards_with_effects = 0
cards_already_hardcoded = 0
working_parsed_cards = 0

for card in cards_data:
    card_id = card.get('id', '')
    effect = card.get('Effect', '') or card.get('effect', '') or ''
    card_type = card.get('cardType', '') or card.get('card_type', '')
    name = card.get('name', '')

    # Skip cards without effects
    if not effect or effect.strip() == '':
        continue

    cards_with_effects += 1

    # Skip cards already hardcoded
    base_id = card_id.split('_')[0] if '_' in card_id else card_id
    if card_id in hardcoded_card_ids or base_id in hardcoded_card_ids:
        cards_already_hardcoded += 1
        continue

    # Categorize the card
    category = categorize_card(card_id, effect)

    card_info = {
        'id': card_id,
        'name': name,
        'type': card_type,
        'effect': effect[:200] + '...' if len(effect) > 200 else effect
    }

    if category == "leader_condition":
        leader_condition_cards.append(card_info)
    elif category == "sacrifice_cost":
        sacrifice_cost_cards.append(card_info)
    elif category == "reveal_cost":
        reveal_cost_cards.append(card_info)
    elif category == "life_condition":
        life_condition_cards.append(card_info)
    elif category == "trash_condition":
        trash_condition_cards.append(card_info)
    elif category == "complex_choice":
        complex_choice_cards.append(card_info)
    else:
        # Card should work with parser
        working_parsed_cards += 1

# Print results
print("\n" + "="*80)
print("OPTCG CARD EFFECT COVERAGE ANALYSIS")
print("="*80)

print(f"\nTotal cards in database: {len(cards_data)}")
print(f"Cards with effects: {cards_with_effects}")
print(f"Cards already hardcoded: {cards_already_hardcoded}")
print(f"Cards likely working (parsed): {working_parsed_cards}")

total_non_working = (len(leader_condition_cards) + len(sacrifice_cost_cards) +
                     len(reveal_cost_cards) + len(life_condition_cards) +
                     len(trash_condition_cards) + len(complex_choice_cards))

print(f"\nNON-WORKING CARDS BREAKDOWN:")
print(f"  Leader Condition cards: {len(leader_condition_cards)}")
print(f"  Sacrifice Cost cards: {len(sacrifice_cost_cards)}")
print(f"  Reveal Cost cards: {len(reveal_cost_cards)}")
print(f"  Life Condition cards: {len(life_condition_cards)}")
print(f"  Trash Condition cards: {len(trash_condition_cards)}")
print(f"  Complex Choice cards: {len(complex_choice_cards)}")
print(f"  TOTAL NON-WORKING: {total_non_working}")

# Print detailed lists
def print_category(name, cards):
    if not cards:
        return
    print(f"\n{'='*80}")
    print(f"{name} ({len(cards)} cards)")
    print("="*80)
    for card in sorted(cards, key=lambda x: x['id'])[:10]:  # Only show first 10
        effect_text = card['effect'].encode('ascii', 'replace').decode('ascii')
        print(f"\n{card['id']} - {card['name']} ({card['type']})")
        print(f"  Effect: {effect_text}")

print_category("LEADER CONDITION CARDS", leader_condition_cards)
print_category("SACRIFICE COST CARDS", sacrifice_cost_cards)
print_category("REVEAL COST CARDS", reveal_cost_cards)
print_category("LIFE CONDITION CARDS", life_condition_cards)
print_category("TRASH CONDITION CARDS", trash_condition_cards)
print_category("COMPLEX CHOICE CARDS", complex_choice_cards)

# Save to JSON for processing
output = {
    'summary': {
        'total_cards': len(cards_data),
        'cards_with_effects': cards_with_effects,
        'already_hardcoded': cards_already_hardcoded,
        'working_parsed': working_parsed_cards,
        'non_working_total': total_non_working,
    },
    'leader_condition_cards': leader_condition_cards,
    'sacrifice_cost_cards': sacrifice_cost_cards,
    'reveal_cost_cards': reveal_cost_cards,
    'life_condition_cards': life_condition_cards,
    'trash_condition_cards': trash_condition_cards,
    'complex_choice_cards': complex_choice_cards,
}

output_path = Path(__file__).parent / "non_working_cards.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\n\nDetailed output saved to: {output_path}")
