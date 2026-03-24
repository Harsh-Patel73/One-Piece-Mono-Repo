"""
Hardcoded effects for ST25 cards.
"""

from ..hardcoded import (
    draw_cards, register_effect, trash_from_hand,
)


# --- ST25-001: Alvida (Buggy Leader) ---
@register_effect("ST25-001", "ON_PLAY", "If Leader is Buggy, draw 3 trash 2")
def st25_001_alvida(game_state, player, card):
    if check_leader_name(player, "Buggy"):
        draw_cards(player, 3)
        trash_from_hand(player, 2, game_state, card)
    return True

