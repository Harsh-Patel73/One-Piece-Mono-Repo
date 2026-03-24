"""
Hardcoded effects for ST20 cards.
"""

from ..hardcoded import (
    get_opponent, register_effect, trash_from_hand,
)


# --- ST20-005: Charlotte Linlin ---
@register_effect("ST20-005", "ON_PLAY", "Trash 1: Opponent chooses discard 2 or lose life")
def charlotte_linlin_st20_effect(game_state, player, card):
    if player.hand:
        trash_from_hand(player, 1, game_state, card)
        opponent = get_opponent(game_state, player)
        # AI opponent chooses: discard 2 is usually better than losing life
        if len(opponent.hand) >= 2:
            trash_from_hand(opponent, 2)
        elif opponent.life_cards:
            life = opponent.life_cards.pop()
            opponent.trash.append(life)
        return True
    return False


# --- ST20-004: Charlotte Pudding ---
@register_effect("ST20-004", "ON_PLAY", "Add Life to hand, set Big Mom Pirates cost 3 or less active")
def charlotte_pudding_st20_effect(game_state, player, card):
    if player.life_cards:
        life = player.life_cards.pop()
        player.hand.append(life)
        bigmom = [c for c in player.cards_in_play
                 if 'big mom pirates' in (c.card_origin or '').lower()
                 and (getattr(c, 'cost', 0) or 0) <= 3]
        if bigmom:
            bigmom[0].is_resting = False
        return True
    return False

