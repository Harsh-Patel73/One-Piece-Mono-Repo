import json
from pathlib import Path
from urllib.request import Request, urlopen

API_URL = "https://api.dotgg.gg/cgfw/getcards?game=onepiece&mode=indexed&cache=4021"
SCRIPT_DIR = Path(__file__).resolve().parent
GAME_ENGINE_CARDS = SCRIPT_DIR / "english_cards.json"
SIMULATOR_CARDS = SCRIPT_DIR.parent.parent / "simulator" / "backend" / "data" / "cards.json"

def fetch_card_data():
    request = Request(API_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=30) as response:
        return json.load(response)

def main():
    data = fetch_card_data()

    headers = data["names"]  # Field names
    all_cards = data["data"]  # List of cards

    # Find language field index dynamically
    lang_index = headers.index("language") if "language" in headers else -1
    print(f"Language field at index: {lang_index}")

    english_cards = []

    for card in all_cards:
        # Check language field (index 24) for "en"
        lang = card[lang_index] if lang_index >= 0 and lang_index < len(card) else None
        if lang == "en":
            # Keep only the fields we want (first 16)
            cleaned_card = card[:16]
            card_dict = dict(zip(headers[:16], cleaned_card))

            # Add image_link using the card ID
            card_id = card[0]  # First field is the 'id'
            card_dict["image_link"] = f"https://static.dotgg.gg/onepiece/card/{card_id}.webp"

            english_cards.append(card_dict)

    GAME_ENGINE_CARDS.write_text(
        json.dumps(english_cards, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    SIMULATOR_CARDS.write_text(
        json.dumps(english_cards, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Saved {len(english_cards)} English cards to '{GAME_ENGINE_CARDS}'.")
    print(f"Synchronized simulator cards to '{SIMULATOR_CARDS}'.")

if __name__ == "__main__":
    main()
