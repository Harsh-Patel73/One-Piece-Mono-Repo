"""
Hardcoded effects for ST27 cards.
"""

from ..effect_registry import (
    create_rest_choice, register_effect,
)


# --- ST27-001: Avalo Pizarro ---
@register_effect("ST27-001", "ACTIVATE_MAIN", "Rest Fullalead: If Leader is Blackbeard Pirates, +4000 power")
def st27_001_pizarro(game_state, player, card):
    if check_leader_type(player, "Blackbeard Pirates"):
        # Find Fullalead to rest
        fullalead = [c for c in player.cards_in_play
                     if 'Fullalead' in (getattr(c, 'name', '') or '')
                     and not getattr(c, 'is_resting', False)]
        if fullalead:
            add_power_modifier(card, 4000)
            return create_rest_choice(game_state, player, fullalead, source_card=card,
                                     prompt="Choose Fullalead to rest")
    return True

