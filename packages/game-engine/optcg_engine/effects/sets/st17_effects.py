"""
Hardcoded effects for ST17 cards.
"""

from ..effect_registry import (
    give_don_to_card, register_effect, reorder_top_cards,
)


# --- ST17-003: Buggy ---
@register_effect("ST17-003", "on_play", "[On Play] Look at 3, place at top in any order")
def st17_003_buggy(game_state, player, card):
    """On Play: Look at top 3 cards and place them at the top of your deck in any order."""
    # Simplified: reorder to bottom (top-ordering not yet supported in UI)
    return reorder_top_cards(game_state, player, 3, source_card=card)


# --- ST17-004: Boa Hancock ---
@register_effect("ST17-004", "blocker", "[Blocker]")
def st17_004_hancock_blocker(game_state, player, card):
    """Blocker."""
    card.is_blocker = True
    return True


@register_effect("ST17-004", "on_play", "[On Play] Look at 3, place at top/bottom, give DON to Warlords")
def st17_004_hancock_play(game_state, player, card):
    """On Play: Look at top 3, place at top/bottom in any order. Give 1 rested DON to Warlords."""
    reorder_top_cards(game_state, player, 3, source_card=card, allow_top=True)
    # Give 1 rested DON to a Seven Warlords of the Sea Leader or Character
    warlord_targets = [c for c in player.cards_in_play
                       if 'seven warlords of the sea' in (c.card_origin or '').lower()]
    if player.leader and 'seven warlords of the sea' in (player.leader.card_origin or '').lower():
        warlord_targets.insert(0, player.leader)
    if warlord_targets:
        give_don_to_card(player, warlord_targets[0], 1, rested_only=True)
    return True
