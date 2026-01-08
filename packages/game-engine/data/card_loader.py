import json
from pathlib import Path
from models.cards import Card as ModelCard

def load_card_database(filepath: str) -> dict[str, ModelCard]:
    # Get the path for the json file
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Card DB not found at {filepath}")

    # Read the content of the file
    raw = json.loads(path.read_text(encoding="utf-8"))
    
    # raw is already a list, so we directly assign it to cards_list
    cards_list = raw

    # Debugging info
    print(f"[INFO] Starting to load {len(cards_list)} raw card entries...")
    
    # Dictionary to store the cards, key is the card ID
    card_db: dict[str, ModelCard] = {}
    dropped = []

    # Iterate over the cards and load them
    for entry in cards_list:
        cid = entry.get("id_normal") or entry.get("id") or "<no-id>"
        try:
            # Create the card object using the `from_json` method of the Card class
            card = ModelCard.from_json(entry)
            # Save the card in the dictionary
            card_db[card.id_normal] = card
        except Exception as e:
            # If there is an error, track the card that caused the issue
            print(f"Error loading card {cid}: {e}")
            dropped.append(cid)

    # If some cards were dropped, log them
    if dropped:
        print(f"[WARN] Dropped {len(dropped)} cards:")
        for cid in dropped:
            print("   ", cid)
    else:
        print("[OK] No cards were dropped.")

    # Print the total number of valid cards loaded
    print(f"[OK] Loaded {len(card_db)} valid cards.")
    
    return card_db
