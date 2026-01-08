"""
Hardcoded Effect Handlers for Complex Cards.
"""

from typing import TYPE_CHECKING, Callable, Dict, List, Optional
from dataclasses import dataclass
import random

if TYPE_CHECKING:
    from .engine import GameState, Player
    from .models.cards import Card


@dataclass
class HardcodedEffect:
    card_id: str
    timing: str
    handler: Callable[['GameState', 'Player', 'Card'], bool]
    description: str


_hardcoded_effects: Dict[str, List[HardcodedEffect]] = {}


def register_effect(card_id: str, timing: str, description: str):
    def decorator(func):
        effect = HardcodedEffect(card_id, timing, func, description)
        if card_id not in _hardcoded_effects:
            _hardcoded_effects[card_id] = []
        _hardcoded_effects[card_id].append(effect)
        return func
    return decorator


def execute_hardcoded_effect(game_state: 'GameState', player: 'Player', card: 'Card', timing: str) -> bool:
    """Execute hardcoded effects for a card at a specific timing."""
    # Handle base IDs for alternate arts (e.g., OP01-001_p1 -> OP01-001)
    card_id = card.id
    base_id = card_id.split('_')[0]

    effects = _hardcoded_effects.get(card_id, []) + _hardcoded_effects.get(base_id, [])
    executed = False
    
    for effect in effects:
        if effect.timing == timing:
            try:
                result = effect.handler(game_state, player, card)
                executed = executed or result
            except Exception as e:
                print(f"Error executing effect for {card_id}: {e}")
                
    return executed


# --- UTILITIES ---

def get_opponent(game_state: 'GameState', player: 'Player') -> 'Player':
    return game_state.opponent_player if game_state.current_player == player else game_state.current_player

def draw_cards(player: 'Player', count: int):
    for _ in range(count):
        player.draw_card()


# --- CARD IMPLEMENTATIONS ---

# Example: OP01-016 Nami (Searcher)
@register_effect("OP01-016", "ON_PLAY", "Look at top 5, reveal Straw Hat, add to hand")
def nami_effect(game_state, player, card):
    # In a real implementation, this would trigger a UI state change
    # For now, we simulate the logic or log it
    if len(player.deck) >= 5:
        print(f"{player.name} looks at top 5 cards")
        # Logic to reveal and add would go here
        return True
    return False

@register_effect("ST01-012", "ON_PLAY", "Give +2000 Power to Leader or Character")
def luffy_starter_effect(game_state, player, card):
    # Logic for ST01 Luffy
    return True