"""
Effect handlers for triggering card effects.
"""

from typing import TYPE_CHECKING
from ..effects.hardcoded import execute_hardcoded_effect, has_hardcoded_effect

if TYPE_CHECKING:
    from ..game_engine import GameState
    from ..models.cards import Card


def trigger_effect(card_id: str, game_state: 'GameState', card: 'Card', timing: str = "ON_PLAY") -> bool:
    """
    Trigger hardcoded effects for a card.

    Args:
        card_id: The card ID
        game_state: Current game state
        card: The card triggering the effect
        timing: Effect timing (ON_PLAY, WHEN_ATTACKING, etc.)

    Returns:
        True if any effect was executed
    """
    if not has_hardcoded_effect(card_id, timing):
        return False

    player = game_state.current_player
    return execute_hardcoded_effect(game_state, player, card, timing)
