"""Card database loader for OPTCG Simulator."""

import json
from pathlib import Path
from typing import Dict
from .models.cards import Card


def load_card_database(filepath: str) -> Dict[str, Card]:
    """Load all cards from a JSON file."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Card DB not found at {filepath}")

    raw = json.loads(path.read_text(encoding="utf-8"))
    cards_list = raw

    card_db: Dict[str, Card] = {}
    dropped = []

    for entry in cards_list:
        cid = entry.get("id_normal") or entry.get("id") or "<no-id>"
        try:
            card = Card.from_json(entry)
            card_db[card.id_normal] = card
        except Exception as e:
            dropped.append((cid, str(e)))

    if dropped:
        print(f"[WARN] Dropped {len(dropped)} cards during load")

    print(f"[OK] Loaded {len(card_db)} cards from {filepath}")
    return card_db


def get_card_by_id(card_db: Dict[str, Card], card_id: str) -> Card:
    """Get a card by ID, returns a copy for game use."""
    card = card_db.get(card_id)
    if card:
        # Return a fresh copy for game use
        return Card.from_json({
            "id": card.id,
            "id_normal": card.id_normal,
            "name": card.name,
            "cardType": card.card_type,
            "Cost": card.cost,
            "Power": card.power,
            "Counter": card.counter,
            "Color": "/".join(card.colors),
            "Life": card.life,
            "Effect": card.effect,
            "image_link": card.image_link,
            "Attribute": card.attribute,
            "Type": card.card_origin,
            "Trigger": card.trigger,
        })
    return None
