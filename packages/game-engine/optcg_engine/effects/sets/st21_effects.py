"""
Hardcoded effects for ST21 cards.
"""

from ..hardcoded import (
    create_don_assignment_choice, register_effect,
)


# --- ST21-001: Monkey.D.Luffy (Leader) ---
@register_effect("ST21-001", "MAIN", "Give up to 2 rested DON to 1 char")
def luffy_st21_leader_effect(game_state, player, card):
    rested_don = [d for d in player.don_pool if d.is_resting]
    if len(rested_don) >= 2 and player.cards_in_play:
        # Let player choose which character gets DON
        targets = player.cards_in_play + ([player.leader] if player.leader else [])
        return create_don_assignment_choice(
            game_state, player, targets, don_count=2,
            source_card=card, rested_only=True,
            prompt="Choose a Character to give 2 rested DON"
        )
    return False


# --- ST21-001: Monkey.D.Luffy ---
@register_effect("ST21-001", "ACTIVATE_MAIN", "Give up to 2 rested DON to 1 Character")
def luffy_st21_effect(game_state, player, card):
    if getattr(card, 'attached_don', 0) >= 1 and player.cards_in_play:
        # Player chooses which character receives DON
        return create_don_assignment_choice(
            game_state, player, player.cards_in_play, don_count=2,
            source_card=card, rested_only=True,
            prompt="Choose a Character to give up to 2 rested DON"
        )
    return False


# --- ST21-001: Monkey.D.Luffy (Leader) ---
@register_effect("ST21-001", "activate", "[DON!! x1] Give up to 2 rested DON to 1 Character")
def st21_001_luffy_leader(game_state, player, card):
    """DON x1, Once Per Turn: Give up to 2 rested DON cards to 1 of your Characters."""
    if getattr(card, 'attached_don', 0) >= 1:
        if hasattr(card, 'st21_001_used') and card.st21_001_used:
            return False
        rested_don = player.don_pool.count("rested")
        if rested_don and player.cards_in_play:
            given = min(2, len(rested_don))
            card.st21_001_used = True
            return create_don_assignment_choice(game_state, player, player.cards_in_play,
                                                given, source_card=card,
                                                prompt="Choose a Character to give rested DON")
    return False

