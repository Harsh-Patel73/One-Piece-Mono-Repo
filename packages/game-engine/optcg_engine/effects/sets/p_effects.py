"""
Hardcoded effects for P cards.
"""

import random

from ..hardcoded import (
    create_power_effect_choice, draw_cards, get_opponent, register_effect,
    reorder_top_cards,
)


# --- P-092: Koby ---
@register_effect("P-092", "WHEN_ATTACKING", "If Navy Leader, Leader base power becomes 7000")
def koby_p092_effect(game_state, player, card):
    if player.leader and 'navy' in (player.leader.card_origin or '').lower():
        player.leader.base_power_override = 7000
        return True
    return False


# --- P-071: Marco ---
@register_effect("P-071", "ON_KO", "Return this card to hand")
def marco_p071_effect(game_state, player, card):
    if card in player.trash:
        player.trash.remove(card)
        player.hand.append(card)
        return True
    return False


# --- P-009: Trafalgar Law ---
@register_effect("P-009", "ON_PLAY", "If opponent has 6+ hand, they add 1 Life to hand")
def law_p009_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    if len(opponent.hand) >= 6 and opponent.life_cards:
        life = opponent.life_cards.pop()
        opponent.hand.append(life)
        return True
    return False


# --- P-017: Trafalgar Law ---
@register_effect("P-017", "ON_PLAY", "Give opponent's char -2000 power")
def law_p017_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    if opponent.cards_in_play:
        return create_power_effect_choice(
            game_state, player, opponent.cards_in_play, -2000,
            source_card=card,
            prompt="Choose opponent's Character to give -2000 power"
        )
    return False


# --- P-046: Yamato ---
@register_effect("P-046", "ON_PLAY", "Place all hand at bottom, draw same number")
def yamato_p046_effect(game_state, player, card):
    hand_count = len(player.hand)
    player.deck.extend(player.hand)
    player.hand.clear()
    draw_cards(player, hand_count)
    return True


# =============================================================================
# UNCOVERED CARDS - Added from coverage analysis
# =============================================================================

# --- P-002: I Smell Adventure!!! ---
@register_effect("P-002", "MAIN", "Return all cards in hand to deck, shuffle, draw same number")
def i_smell_adventure_effect(game_state, player, card):
    """Return all cards in hand to deck and draw equal number."""
    hand_count = len(player.hand)
    if hand_count > 0:
        player.deck.extend(player.hand)
        player.hand.clear()
        random.shuffle(player.deck)
        draw_cards(player, hand_count)
        return True
    return False


# --- P-058: Where the Wind Blows ---
@register_effect("P-058", "MAIN", "If Leader is Uta, set FILM chars active at end of turn")
def where_wind_blows_effect(game_state, player, card):
    """If Leader is Uta, set all FILM characters active at end of turn."""
    if player.leader and 'Uta' in getattr(player.leader, 'name', ''):
        # Mark to set active at end of turn
        for c in player.cards_in_play:
            if 'film' in (c.card_origin or '').lower():
                c.set_active_at_end_of_turn = True
        return True
    return False


# --- P-034: Sanji ---
@register_effect("P-034", "CONTINUOUS", "If DONx1 and 2 or less life, +2000 power (your turn)")
def p_034_sanji(game_state, player, card):
    """Continuous (Your Turn): If DONx1 and 2 or less life, +2000 power."""
    if getattr(card, 'attached_don', 0) >= 1 and check_life_count(player, 2):
        add_power_modifier(card, 2000)
        return True
    return False


# --- P-048: Arlong ---
@register_effect("P-048", "WHEN_ATTACKING", "If DONx1 and 4+ life, opponent places hand at deck bottom")
def p_048_arlong(game_state, player, card):
    """When Attacking (DONx1): If 4+ life, opponent places 1 hand card at bottom."""
    if getattr(card, 'attached_don', 0) >= 1 and len(player.life_cards) >= 4:
        opponent = get_opponent(game_state, player)
        if opponent.hand:
            # Opponent picks lowest cost
            sorted_hand = sorted(opponent.hand, key=lambda c: getattr(c, 'cost', 0) or 0)
            card_to_place = sorted_hand[0]
            opponent.hand.remove(card_to_place)
            opponent.deck.append(card_to_place)
            return True
    return False


# --- P-011: Uta (Leader) ---
@register_effect("P-011", "activate", "[Activate: Main] Rest 1: Char with no effect +2000")
def p_011_uta_leader(game_state, player, card):
    """Once Per Turn, Rest 1 DON: Up to 1 Character with no base effect gains +2000 power."""
    if hasattr(card, 'p_011_used') and card.p_011_used:
        return False
    active_don = player.don_pool.count("active")
    if active_don:
        active_don[0].is_resting = True
        no_effect_chars = [c for c in player.cards_in_play if not getattr(c, 'effect', '')]
        if no_effect_chars:
            no_effect_chars[0].power_modifier = getattr(no_effect_chars[0], 'power_modifier', 0) + 2000
        card.p_011_used = True
        return True
    return False


# --- P-047: Monkey.D.Luffy (Leader) ---
@register_effect("P-047", "on_attack", "[DON!! x1] [When Attacking] If 3 or less hand, draw 1")
def p_047_luffy_leader(game_state, player, card):
    """DON x1, When Attacking: Draw 1 card if you have 3 or less cards in hand."""
    if getattr(card, 'attached_don', 0) >= 1:
        if len(player.hand) <= 3:
            draw_cards(player, 1)
            return True
    return False


# --- P-076: Sakazuki (Leader) ---
@register_effect("P-076", "activate", "[Activate: Main] Trash Navy card: Opponent char -1 cost")
def p_076_sakazuki_leader(game_state, player, card):
    """Once Per Turn: Trash a Navy card from hand, give opponent's Character -1 cost."""
    if hasattr(card, 'p_076_used') and card.p_076_used:
        return False
    navy_cards = [c for c in player.hand if 'navy' in (c.card_origin or '').lower()]
    if navy_cards:
        to_trash = navy_cards[0]
        player.hand.remove(to_trash)
        player.trash.append(to_trash)
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            opponent.cards_in_play[0].cost_modifier = getattr(opponent.cards_in_play[0], 'cost_modifier', 0) - 1
        card.p_076_used = True
        return True
    return False


# --- P-117: Nami (Leader) ---
@register_effect("P-117", "continuous", "Win when deck is 0 (only East Blue cards in deck)")
def p_117_nami_continuous(game_state, player, card):
    """When deck is reduced to 0, you win instead of losing. Can only include East Blue cards."""
    player.win_on_deck_out = True
    return True


@register_effect("P-117", "on_damage_dealt", "[DON!! x1] When damage dealt, trash 1 from deck")
def p_117_nami_damage(game_state, player, card):
    """DON x1: When this Leader's attack deals damage to opponent's Life, trash 1 from deck."""
    if getattr(card, 'attached_don', 0) >= 1:
        if player.deck:
            trashed = player.deck.pop(0)
            player.trash.append(trashed)
            return True
    return False


# =============================================================================
# SEARCHER / SCRY CARDS
# =============================================================================

# --- P-049: Usopp ---
@register_effect("P-049", "on_play", "[On Play] Look at 5, place at top/bottom in any order")
def p_049_usopp(game_state, player, card):
    """On Play: Look at top 5 cards and place them at the top or bottom of the deck in any order."""
    return reorder_top_cards(game_state, player, 5, source_card=card, allow_top=True)


# --- P-068: Sanji ---
@register_effect("P-068", "activate", "[Activate: Main] Trash this: Look at 5, place at top/bottom")
def p_068_sanji(game_state, player, card):
    """Activate: Main: Trash this Character. Look at top 5 and place at top/bottom in any order."""
    if card in player.cards_in_play:
        player.cards_in_play.remove(card)
        player.trash.append(card)
        return reorder_top_cards(game_state, player, 5, source_card=card, allow_top=True)
    return False


# --- P-074: Portgas.D.Ace ---
@register_effect("P-074", "activate", "[Activate: Main] Return to hand: Look at 5, place at top/bottom")
def p_074_ace(game_state, player, card):
    """Activate: Main: Return this Character to hand. Look at top 5 and place at top/bottom in any order."""
    if card in player.cards_in_play:
        player.cards_in_play.remove(card)
        player.hand.append(card)
        return reorder_top_cards(game_state, player, 5, source_card=card, allow_top=True)
    return False

