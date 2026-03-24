"""
Hardcoded effects for ST15 cards.
"""

from ..hardcoded import (
    add_don_from_deck, create_power_effect_choice, get_opponent, register_effect,
)


# =============================================================================
# HARDCODED EFFECT IMPLEMENTATIONS - Alphabetically by card name
# =============================================================================

# --- ST15-001: Atmos ---
@register_effect("ST15-001", "WHEN_ATTACKING", "Cannot add Life to hand if Leader is Edward.Newgate")
def atmos_effect(game_state, player, card):
    if player.leader and 'Edward.Newgate' in getattr(player.leader, 'name', ''):
        player.cannot_add_life_this_turn = True
    return True


# =============================================================================
# LEADER CONDITION CARDS - Whitebeard Pirates
# =============================================================================

# --- ST15-004: Thatch ---
@register_effect("ST15-004", "ON_PLAY", "If Leader is Whitebeard Pirates, -2000 power to opponent + add life to hand")
def st15_004_thatch(game_state, player, card):
    if check_leader_type(player, "Whitebeard Pirates"):
        # Add life to hand (automatic, no choice needed)
        add_life_to_hand(player)
        # Give opponent's character -2000 power (requires choice)
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            return create_power_effect_choice(
                game_state, player, opponent.cards_in_play, -2000,
                source_card=card,
                prompt="Choose an opponent's Character to give -2000 power"
            )
    return True


# --- ST15-002: Edward.Newgate (Leader) ---
@register_effect("ST15-002", "END_OF_TURN", "If Leader is Whitebeard Pirates, add DON and set active")
def st15_002_newgate_leader(game_state, player, card):
    # This is a leader effect - adds DON at end of turn
    if check_leader_type(player, "Whitebeard Pirates"):
        add_don_from_deck(player, 1, set_active=True)
    return True

