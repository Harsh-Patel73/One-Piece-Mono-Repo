"""
Hardcoded effects for PRB01 cards.
"""

from ..hardcoded import (
    create_target_choice, register_effect,
)


# --- PRB01-001: Sanji (Leader) ---
@register_effect("PRB01-001", "MAIN", "Give char without On Play Rush")
def sanji_leader_effect(game_state, player, card):
    chars = [c for c in player.cards_in_play
            if (getattr(c, 'cost', 0) or 0) <= 8
            and '[On Play]' not in (getattr(c, 'effect', '') or '')]
    if chars:
        return create_target_choice(
            game_state, player, chars,
            callback_action="give_rush",
            source_card=card,
            prompt="Choose your Character without [On Play] to give Rush"
        )
    return False


# --- PRB01-001: Sanji ---
@register_effect("PRB01-001", "ACTIVATE_MAIN", "Give Rush to Character without On Play, cost 8 or less")
def sanji_prb01_effect(game_state, player, card):
    # Find characters without On Play effect and cost 8 or less
    targets = [c for c in player.cards_in_play
               if getattr(c, 'cost', 0) <= 8
               and not c.has_keyword('rush')]
    if targets:
        return create_target_choice(
            game_state, player, targets,
            callback_action="give_rush",
            source_card=card,
            prompt="Choose your Character cost 8 or less to give Rush"
        )
    return False

