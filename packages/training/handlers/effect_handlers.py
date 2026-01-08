from __future__ import annotations
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game_engine import GameState, Player
    from models.cards import Card

# One Play Effect Handlers

effect_handlers = {}

def EB01_050_on_play(game_state: 'GameState', player: 'Player', card: 'Card'):
    if len(player.trash) >= 30:
        if player.deck:
            player.life_cards.append(player.deck.pop(0))

effect_handlers["EB01-050"] = EB01_050_on_play


def OP06_096_on_play(game_state: GameState, player: Player, card: Card):
    if player.life_cards:
        player.hand.append(player.life_cards.pop(0))
    for c in player.cards_in_play:
        if c.cost is not None and c.cost <= 7:
            c.cannot_be_KOd_in_battle = True

effect_handlers["OP06-096"] = OP06_096_on_play


def OP06_081_on_play(game_state: GameState, player: Player, card: Card):
    if len(player.trash) >= 2:
        returned_cards = [player.trash.pop(0), player.trash.pop(0)]
        player.deck.extend(returned_cards)

    ko_candidates = [c for c in game_state.opponent_player.cards_in_play if c.cost is not None and c.cost <= 2]
    if ko_candidates:
        to_ko = ko_candidates[0]
        game_state.opponent_player.cards_in_play.remove(to_ko)
        game_state.opponent_player.trash.append(to_ko)
        print(f"{player.name} KO'd {to_ko.name} on opponent's field.")

effect_handlers["OP06-081"] = OP06_081_on_play

# [DON!! x1] [When Attacking] Your opponent cannot activate a [Blocker] Character that has 2000 or less power during this battle.
def OP03_002_on_play(game_state: GameState, player: Player, card: Card):
    # TODO: Implement effect for Adio (OP03-002)
        if card.attached_don == 1:
            pass

effect_handlers["OP03-002"] = OP03_002_on_play

# [On Play] If your Leader has the {ODYSSEY} type, set up to 3 of your DON!! cards as active.<br>[On Your Opponent's Attack] [Once Per Turn] You may rest 1 of your DON!! cards: Up to 1 of your Leader or Character cards gains +2000 power during this battle.
def OP09_023_on_play(game_state: GameState, player: Player, card: Card):
    # TODO: Implement effect for Adio (OP09-023)
        if player.leader.card_type == 'ODYSSEY':
            pass

effect_handlers["OP09-023"] = OP09_023_on_play

# If you have 2 or more rested {ODYSSEY} type Characters, this Character gains +1000 power.
def P_078_on_play(game_state: GameState, player: Player, card: Card):
    rested = 0
    for card in player.cards_in_play:
        if card.is_resting == True:
            rested+=1
    if rested >= 2:
        card.power += 1000

effect_handlers["P-078"] = P_078_on_play

def OP07_002_on_play(game_state: GameState, player: Player, card: Card):
    candidate = game_state.opponent_player.cards_in_play
    candidate[0].power = 0

effect_handlers["OP07-002"] = OP07_002_on_play

def ST05_002_on_play(game_state: GameState, player: Player, card: Card):
    player.don_pool.append("rested")

effect_handlers["ST05-002"] = ST05_002_on_play

def OP03_094_on_play(game_state: GameState, player: Player, card: Card):
    if "CP" in (player.leader.card_origin or ""):
            # Check field limit (max 5 characters)
            char_count = sum(1 for c in player.cards_in_play if c.card_type == "CHARACTER")
            if char_count >= 5:
                print("Field is full. Cannot play additional characters.")
                return

            top_five = player.deck[:5]
            valid_choices = [
                c for c in top_five
                if c.card_type == "CHARACTER" and "CP" in (c.card_origin or "") and (c.cost or 0) <= 5
            ]

            if valid_choices:
                print("Choose a CP Character (cost ≤ 5) to play:")
                for i, c in enumerate(valid_choices):
                    print(f"{i}: {c.name} (Cost {c.cost})")
                try:
                    idx = int(input("Enter index: "))
                    selected_card = valid_choices[idx]
                    player.add_card_to_play(selected_card, game_state.turn_count)
                    top_five.remove(selected_card)
                except (ValueError, IndexError):
                    print("Invalid selection. No card played.")
            else:
                print("No valid CP Character (cost ≤ 5) to play.")

            # Trash the rest
            for c in top_five:
                player.trash.append(c)
            # Remove the 5 cards from the top of the deck
            player.deck = player.deck[5:]


effect_handlers["OP03-094"] = OP03_094_on_play


def trigger_effect(card_id: str, game_state, card):
    """
    Trigger the effect handler for a card.

    Args:
        card_id: ID of the card
        game_state: Current game state
        card: The card triggering the effect
    """
    handler = effect_handlers.get(card_id)
    if handler:
        try:
            # Determine which player owns the card
            if card in game_state.current_player.cards_in_play or card == game_state.current_player.leader:
                player = game_state.current_player
            else:
                player = game_state.opponent_player

            handler(game_state, player, card)
        except Exception as e:
            print(f"Error triggering effect for {card_id}: {e}")