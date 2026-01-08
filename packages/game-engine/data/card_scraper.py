import requests
import json

API_URL = "https://api.dotgg.gg/cgfw/getcards?game=onepiece&mode=indexed&cache=4021"

def fetch_card_data():
    response = requests.get(API_URL)
    response.raise_for_status()
    return response.json()

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

    with open("english_cards.json", "w", encoding="utf-8") as f:
        json.dump(english_cards, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(english_cards)} English cards with image links to 'english_cards.json'.")

if __name__ == "__main__":
    main()
