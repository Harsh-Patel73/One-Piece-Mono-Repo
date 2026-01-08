from collections import Counter

def validate_deck(deck):
    if not deck or len(deck) < 51:
        return False, "Deck must contain exactly 1 Leader and 50 non-Leader cards."

    leaders = [card for card in deck if card.type == "LEADER"]
    if len(leaders) != 1:
        return False, "Deck must contain exactly 1 Leader card."

    non_leaders = [card for card in deck if card.type in ["CHARACTER", "EVENT", "STAGE"]]
    if len(non_leaders) != 50:
        return False, f"Deck must contain exactly 50 Character/Event/Stage cards. Found {len(non_leaders)}."

    # Check for duplicates (max 4 copies)
    counts = Counter(card.id for card in non_leaders)
    for card_id, count in counts.items():
        if count > 4:
            return False, f"Card {card_id} appears {count} times (max 4 allowed)."

    # Check color consistency
    leader_color = leaders[0].attribute
    allowed_colors = set(c.strip() for c in leader_color.split('/'))

    for card in non_leaders:
        if card.attribute is None:
            continue
        card_colors = set(c.strip() for c in card.attribute.split('/'))
        if not card_colors.issubset(allowed_colors):
            return False, f"Card {card.name} has color(s) {card.attribute}, which do not match Leader color(s) {leader_color}."

    return True, "Deck is valid."
