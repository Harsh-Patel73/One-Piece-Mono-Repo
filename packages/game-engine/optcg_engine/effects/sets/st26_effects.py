"""
Hardcoded effects for ST26 cards.
"""

from ..effect_registry import (
    get_opponent, register_effect,
)


# --- ST26-005: Monkey.D.Luffy ---
@register_effect("ST26-005", "ON_PLAY", "DON -2: If multicolor Leader and opponent has 5+ DON, Leader becomes 7000")
def luffy_st26_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    colors = (getattr(player.leader, 'colors', '') or '').lower() if player.leader else ''
    is_multicolor = colors.count('/') > 0
    if is_multicolor and len(opponent.don_pool) >= 5:
        # Return 2 DON
        active_don = [d for d in player.don_pool if not d.is_resting]
        if len(active_don) >= 2 and hasattr(player, 'don_deck'):
            for don in active_don[:2]:
                player.don_pool.remove(don)
                player.don_deck.append(don)
            player.leader.base_power_override = 7000
            return True
    return False


# --- ST26-001: Soba Mask ---
@register_effect("ST26-001", "ON_PLAY", "Return all San-Gorou and Sanji to hand")
def soba_mask_effect(game_state, player, card):
    to_return = [c for c in player.cards_in_play
                if 'San-Gorou' in getattr(c, 'name', '') or 'Sanji' in getattr(c, 'name', '')]
    for c in to_return:
        player.cards_in_play.remove(c)
        player.hand.append(c)
    return len(to_return) > 0

