"""
Hardcoded effects for ST14 cards.
"""

from ..effect_registry import (
    create_cost_reduction_choice, create_ko_choice, draw_cards, get_opponent,
    register_effect, trash_from_hand,
)


# --- ST14-001: Monkey.D.Luffy (Leader) ---
@register_effect("ST14-001", "continuous", "[DON!! x1] All chars +1 cost, if cost 8+ char Leader +1000")
def st14_001_luffy_leader(game_state, player, card):
    """DON x1: All Characters gain +1 cost. If you have a cost 8 or more Character, Leader +1000."""
    if getattr(card, 'attached_don', 0) >= 1:
        for char in player.cards_in_play:
            char.cost_modifier = getattr(char, 'cost_modifier', 0) + 1
        high_cost = [c for c in player.cards_in_play
                     if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) >= 8]
        if high_cost:
            card.power_modifier = getattr(card, 'power_modifier', 0) + 1000
        return True
    return False


# --- ST14-002: Usopp ---
@register_effect("ST14-002", "on_attack", "[DON!! x1] If you have cost 8+ Character, K.O. cost 4 or less")
def st14_002_usopp(game_state, player, card):
    """DON x1: If you have a cost 8+ Character, K.O. opponent's cost 4 or less Character."""
    if getattr(card, 'attached_don', 0) >= 1:
        high_cost = [c for c in player.cards_in_play if (getattr(c, 'cost', 0) or 0) >= 8]
        if high_cost:
            opponent = get_opponent(game_state, player)
            targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
            if targets:
                return create_ko_choice(
                    game_state, player, targets, source_card=card,
                    prompt="Choose opponent's cost 4 or less Character to KO"
                )
    return False


# --- ST14-003: Sanji ---
@register_effect("ST14-003", "on_play", "[On Play] If you have cost 6+ Character, K.O. cost 5 or less")
def st14_003_sanji(game_state, player, card):
    """If you have a cost 6+ Character, K.O. opponent's cost 5 or less Character."""
    high_cost = [c for c in player.cards_in_play if (getattr(c, 'cost', 0) or 0) >= 6 and c != card]
    if high_cost:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 5]
        if targets:
            return create_ko_choice(
                game_state, player, targets, source_card=card,
                prompt="Choose opponent's cost 5 or less Character to KO"
            )
    return False


# --- ST14-004: Jinbe ---
@register_effect("ST14-004", "activate", "[Activate: Main] [Once Per Turn] SHC Character gains +2 cost")
def st14_004_jinbe(game_state, player, card):
    """Once Per Turn: Up to 1 black Straw Hat Crew Character gains +2 cost."""
    if hasattr(card, 'st14_004_used') and card.st14_004_used:
        return False
    shc = [c for c in player.cards_in_play
           if 'straw hat crew' in (c.card_origin or '').lower()
           and 'black' in (getattr(c, 'colors', '') or '').lower()]
    if shc:
        shc[0].cost_modifier = getattr(shc[0], 'cost_modifier', 0) + 2
        card.st14_004_used = True
        return True
    return False


# --- ST14-006: Nami ---
@register_effect("ST14-006", "blocker", "[Blocker]")
def st14_006_nami_blocker(game_state, player, card):
    """Blocker: Can redirect attacks."""
    card.is_blocker = True
    return True


@register_effect("ST14-006", "on_play", "[On Play] If 6 or less cards and cost 8+ Character, draw 1")
def st14_006_nami_play(game_state, player, card):
    """If you have 6 or less cards in hand and a cost 8+ Character, draw 1."""
    if len(player.hand) <= 6:
        high_cost = [c for c in player.cards_in_play if (getattr(c, 'cost', 0) or 0) >= 8]
        if high_cost:
            draw_cards(player, 1)
            return True
    return False


# --- ST14-007: Nico Robin ---
@register_effect("ST14-007", "on_play", "[On Play] If cost 8+ Character, give opponent's Character -5 cost")
def st14_007_robin_play(game_state, player, card):
    """If you have a cost 8+ Character, give opponent's Character -5 cost."""
    high_cost = [c for c in player.cards_in_play if (getattr(c, 'cost', 0) or 0) >= 8]
    if high_cost:
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            return create_cost_reduction_choice(game_state, player, opponent.cards_in_play,
                                                -5, source_card=card,
                                                prompt="Choose opponent's Character to give -5 cost")
    return False


@register_effect("ST14-007", "on_attack", "[When Attacking] If cost 8+ Character, give opponent's Character -5 cost")
def st14_007_robin_attack(game_state, player, card):
    """If you have a cost 8+ Character, give opponent's Character -5 cost."""
    high_cost = [c for c in player.cards_in_play if (getattr(c, 'cost', 0) or 0) >= 8]
    if high_cost:
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            return create_cost_reduction_choice(game_state, player, opponent.cards_in_play,
                                                -5, source_card=card,
                                                prompt="Choose opponent's Character to give -5 cost")
    return False


# --- ST14-008: Haredas ---
@register_effect("ST14-008", "activate", "[Activate: Main] Rest this: SHC +2 cost, if cost 8+ draw 1 trash 1")
def st14_008_haredas(game_state, player, card):
    """Rest this: SHC Character gains +2 cost. If cost 8+ Character exists, draw 1 and trash 1."""
    if not getattr(card, 'is_resting', False):
        card.is_resting = True
        shc = [c for c in player.cards_in_play
               if 'straw hat crew' in (c.card_origin or '').lower()
               and 'black' in (getattr(c, 'colors', '') or '').lower()]
        if shc:
            shc[0].cost_modifier = getattr(shc[0], 'cost_modifier', 0) + 2
        high_cost = [c for c in player.cards_in_play if (getattr(c, 'cost', 0) or 0) >= 8]
        if high_cost:
            draw_cards(player, 1)
            trash_from_hand(player, 1, game_state, card)
        return True
    return False


# --- ST14-009: Franky ---
@register_effect("ST14-009", "continuous", "[DON!! x1] [Opponent's Turn] If cost 6+ Character, cannot be K.O.'d and +2000")
def st14_009_franky(game_state, player, card):
    """DON x1: If you have a cost 6+ Character, this Character cannot be K.O.'d by effects and gains +2000."""
    if getattr(card, 'attached_don', 0) >= 1:
        high_cost = [c for c in player.cards_in_play if (getattr(c, 'cost', 0) or 0) >= 6]
        if high_cost:
            card.cannot_be_ko_by_effects = True
            card.power_modifier = getattr(card, 'power_modifier', 0) + 2000
            return True
    return False


# --- ST14-011: Heracles ---
@register_effect("ST14-011", "activate", "[Activate: Main] Rest this: SHC Character gains +2 cost")
def st14_011_heracles(game_state, player, card):
    """Rest this: Up to 1 black Straw Hat Crew Character gains +2 cost."""
    if not getattr(card, 'is_resting', False):
        card.is_resting = True
        shc = [c for c in player.cards_in_play
               if 'straw hat crew' in (c.card_origin or '').lower()
               and 'black' in (getattr(c, 'colors', '') or '').lower()]
        if shc:
            shc[0].cost_modifier = getattr(shc[0], 'cost_modifier', 0) + 2
        return True
    return False


# --- ST14-012: Monkey.D.Luffy ---
@register_effect("ST14-012", "continuous", "If cost 10+ Character, gain Rush")
def st14_012_luffy(game_state, player, card):
    """If you have a cost 10+ Character, this Character gains Rush."""
    high_cost = [c for c in player.cards_in_play if (getattr(c, 'cost', 0) or 0) >= 10 and c != card]
    if high_cost:
        card.has_rush = True
    return True

