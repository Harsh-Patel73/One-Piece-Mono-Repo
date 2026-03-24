"""
Hardcoded effects for ST06 cards.
"""

from ..hardcoded import (
    create_cost_reduction_choice, create_ko_choice, get_opponent, register_effect,
    trash_from_hand,
)


# --- ST06-001: Sakazuki (Leader) ---
@register_effect("ST06-001", "activate", "[Activate: Main] Rest 3 DON, trash 1: K.O. cost 0")
def st06_001_sakazuki_leader(game_state, player, card):
    """Once Per Turn, Rest 3 DON, trash 1 from hand: K.O. opponent's Character with cost 0."""
    if hasattr(card, 'st06_001_used') and card.st06_001_used:
        return False
    active_don = player.don_pool.count("active")
    if len(active_don) >= 3 and player.hand:
        for don in active_don[:3]:
            don.is_resting = True
        trash_from_hand(player, 1, game_state, card)
        opponent = get_opponent(game_state, player)
        cost_zero = [c for c in opponent.cards_in_play
                     if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 0]
        if cost_zero:
            target = cost_zero[0]
            opponent.cards_in_play.remove(target)
            opponent.trash.append(target)
        card.st06_001_used = True
        return True
    return False


# --- ST06-002: Koby ---
@register_effect("ST06-002", "on_play", "[On Play] Trash 1: K.O. cost 0 Character")
def st06_002_koby(game_state, player, card):
    """Trash 1 from hand: K.O. opponent's cost 0 Character."""
    if player.hand:
        trash_from_hand(player, 1, game_state, card)
        opponent = get_opponent(game_state, player)
        cost_zero = [c for c in opponent.cards_in_play
                     if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 0]
        if cost_zero:
            target = cost_zero[0]
            opponent.cards_in_play.remove(target)
            opponent.trash.append(target)
        return True
    return False


# --- ST06-004: Smoker ---
@register_effect("ST06-004", "continuous", "Cannot be K.O.'d by effects; [DON!! x1] Double Attack if cost 0 exists")
def st06_004_smoker(game_state, player, card):
    """Cannot be K.O.'d by effects. DON x1: If cost 0 Character exists, gain Double Attack."""
    card.cannot_be_ko_by_effects = True
    if getattr(card, 'attached_don', 0) >= 1:
        opponent = get_opponent(game_state, player)
        all_chars = player.cards_in_play + opponent.cards_in_play
        cost_zero = [c for c in all_chars
                     if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 0]
        if cost_zero:
            card.has_double_attack = True
    return True


# --- ST06-005: Sengoku ---
@register_effect("ST06-005", "on_attack", "[When Attacking] Give opponent's Character -4 cost")
def st06_005_sengoku(game_state, player, card):
    """Give up to 1 of opponent's Characters -4 cost during this turn."""
    opponent = get_opponent(game_state, player)
    if opponent.cards_in_play:
        return create_cost_reduction_choice(
            game_state, player, opponent.cards_in_play, -4,
            source_card=card,
            prompt="Choose opponent's Character to give -4 cost"
        )
    return False


# --- ST06-006: Tashigi ---
@register_effect("ST06-006", "activate", "[Activate: Main] Rest this: Give opponent's Character -2 cost")
def st06_006_tashigi(game_state, player, card):
    """Rest this Character: Give opponent's Character -2 cost."""
    if not getattr(card, 'is_resting', False):
        card.is_resting = True
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            return create_cost_reduction_choice(
                game_state, player, opponent.cards_in_play, -2,
                source_card=card,
                prompt="Choose opponent's Character to give -2 cost"
            )
        return True
    return False


# --- ST06-007: Tsuru ---
@register_effect("ST06-007", "blocker", "[Blocker]")
def st06_007_tsuru(game_state, player, card):
    """Blocker: Can redirect attacks."""
    card.is_blocker = True
    return True


# --- ST06-008: Hina ---
@register_effect("ST06-008", "on_play", "[On Play] Give opponent's Character -4 cost")
def st06_008_hina(game_state, player, card):
    """Give up to 1 of opponent's Characters -4 cost."""
    opponent = get_opponent(game_state, player)
    if opponent.cards_in_play:
        return create_cost_reduction_choice(
            game_state, player, opponent.cards_in_play, -4,
            source_card=card,
            prompt="Choose opponent's Character to give -4 cost"
        )
    return False


# --- ST06-010: Helmeppo ---
@register_effect("ST06-010", "on_play", "[On Play] Give opponent's Character -3 cost")
def st06_010_helmeppo(game_state, player, card):
    """Give up to 1 of opponent's Characters -3 cost."""
    opponent = get_opponent(game_state, player)
    if opponent.cards_in_play:
        return create_cost_reduction_choice(
            game_state, player, opponent.cards_in_play, -3,
            source_card=card,
            prompt="Choose opponent's Character to give -3 cost"
        )
    return False


# --- ST06-012: Monkey.D.Garp ---
@register_effect("ST06-012", "activate", "[Activate: Main] Trash 1 and rest this: K.O. cost 4 or less")
def st06_012_garp(game_state, player, card):
    """Trash 1 from hand and rest this: K.O. opponent's cost 4 or less Character."""
    if not getattr(card, 'is_resting', False) and player.hand:
        trash_from_hand(player, 1, game_state, card)
        card.is_resting = True
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                     prompt="Choose opponent's cost 4 or less Character to KO")
        return True
    return False

