"""
Hardcoded effects for ST23 cards.
"""

from ..effect_registry import (
    create_ko_choice, get_opponent, register_effect, trash_from_hand,
)


# =============================================================================
# MORE LEADER CONDITION CARDS - Red-Haired Pirates
# =============================================================================

# --- ST23-003: Benn.Beckman ---
@register_effect("ST23-003", "ON_PLAY", "Trash 1: If Leader is Red-Haired Pirates, KO 4000 power or less")
def st23_003_beckman(game_state, player, card):
    if player.hand:
        trash_from_hand(player, 1, game_state, card)
        if check_leader_type(player, "Red-Haired Pirates"):
            opponent = get_opponent(game_state, player)
            targets = [c for c in opponent.cards_in_play if (getattr(c, 'power', 0) or 0) <= 4000]
            if targets:
                return create_ko_choice(game_state, player, targets, source_card=card,
                                       prompt="Choose opponent's 4000 power or less to KO")
    return True

