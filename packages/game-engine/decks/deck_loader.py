import json
import copy
from pathlib import Path
from models.cards import Card

def load_deck(deck_filepath: str, card_db: dict[str, Card]) -> tuple[list[Card], Card]:
    """
    Load a deck from a JSON file.

    Args:
        deck_filepath: Path to the deck JSON file
        card_db: Dictionary of card ID -> Card

    Returns:
        Tuple of (deck cards list, leader card)
    """
    path = Path(deck_filepath)
    if not path.exists():
        raise FileNotFoundError(f"Deck file not found at {deck_filepath}")

    # Load the deck JSON
    raw_deck = json.loads(path.read_text(encoding="utf-8"))
    deck = []

    # Get the leader card (create a copy so it's a separate instance)
    leader_card = card_db.get(raw_deck["leader"])
    if leader_card:
        leader = copy.deepcopy(leader_card)
    else:
        print(f"[WARN] Leader card {raw_deck['leader']} not found in the database.")
        leader = None

    # Add the other cards to the deck
    # IMPORTANT: Create deep copies so each card in deck is a separate instance
    for card_id, count in raw_deck["cards"].items():
        card = card_db.get(card_id)
        if card:
            for _ in range(count):
                deck.append(copy.deepcopy(card))
        else:
            print(f"[WARN] Card ID {card_id} not found in the database.")

    return deck, leader

