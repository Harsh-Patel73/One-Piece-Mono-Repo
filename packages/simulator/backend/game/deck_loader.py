"""Deck loader for OPTCG Simulator."""

import json
import copy
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from .models.cards import Card


def load_deck(deck_filepath: str, card_db: Dict[str, Card]) -> Tuple[List[Card], Optional[Card]]:
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

    raw_deck = json.loads(path.read_text(encoding="utf-8"))
    deck = []

    # Get the leader card
    leader_id = raw_deck.get("leader")
    leader_card = card_db.get(leader_id)
    if leader_card:
        leader = copy.deepcopy(leader_card)
    else:
        print(f"[WARN] Leader card {leader_id} not found in database")
        leader = None

    # Add cards to deck (with deep copies)
    for card_id, count in raw_deck.get("cards", {}).items():
        card = card_db.get(card_id)
        if card:
            for _ in range(count):
                deck.append(copy.deepcopy(card))
        else:
            print(f"[WARN] Card {card_id} not found in database")

    return deck, leader


def get_available_decks(decks_path: str) -> List[Dict]:
    """Get list of available decks."""
    path = Path(decks_path)
    if not path.exists():
        return []

    decks = []
    for deck_file in path.glob("*.json"):
        try:
            raw = json.loads(deck_file.read_text(encoding="utf-8"))
            decks.append({
                "id": deck_file.stem,
                "name": raw.get("name", deck_file.stem),
                "leader": raw.get("leader"),
                "card_count": sum(raw.get("cards", {}).values()),
            })
        except:
            pass

    return decks
