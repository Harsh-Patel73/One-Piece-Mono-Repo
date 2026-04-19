"""
Effect handlers for triggering card effects.
"""

from typing import TYPE_CHECKING
from ..effects.effect_registry import execute_hardcoded_effect, has_hardcoded_effect

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
    # "main" is an alias for "on_play" on event cards
    timings_to_try = [timing]
    if timing.lower() == "on_play":
        timings_to_try.append("main")

    player = game_state.current_player
    executed = False
    for t in timings_to_try:
        if has_hardcoded_effect(card_id, t):
            executed = execute_hardcoded_effect(game_state, player, card, t) or executed
    return executed
