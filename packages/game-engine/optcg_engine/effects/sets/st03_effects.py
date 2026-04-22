"""
Hardcoded effects for ST03 cards.
"""

import random

from ..effect_registry import (
    create_return_to_hand_choice, draw_cards, get_opponent, register_effect,
    trash_from_hand,
)


# --- ST03-001: Crocodile (Leader) ---
@register_effect("ST03-001", "activate", "[Activate: Main] DON -4: Return cost 5 or less to hand")
def st03_001_croc_leader(game_state, player, card):
    """Once Per Turn, DON -4: Return up to 1 Character with cost 5 or less to owner's hand."""
    if hasattr(card, 'st03_001_used') and card.st03_001_used:
        return False
    if len(player.don_pool) >= 4:
        # Return 4 DON to DON deck
        for _ in range(4):
            if player.don_pool:
                don = player.don_pool.pop()
                if hasattr(player, 'don_deck'):
                    player.don_deck.append(don)
        # Return opponent's character (player choice)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 5]
        card.st03_001_used = True
        if targets:
            return create_return_to_hand_choice(game_state, player, targets, source_card=card,
                                                prompt="Choose opponent's cost 5 or less Character to return")
        return True
    return False


# --- ST03-003: Crocodile ---
@register_effect("ST03-003", "blocker", "[Blocker]")
def st03_003_croc_blocker(game_state, player, card):
    """Blocker: Can redirect attacks."""
    card.is_blocker = True
    return True


@register_effect("ST03-003", "on_block", "[DON!! x1] [On Block] Return cost 2 or less Character to deck")
def st03_003_croc_block(game_state, player, card):
    """DON x1: On block, return cost 2 or less Character to bottom of deck."""
    if getattr(card, 'attached_don', 0) >= 1:
        opponent = get_opponent(game_state, player)
        low_cost = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
        if low_cost:
            target = low_cost[0]
            opponent.cards_in_play.remove(target)
            opponent.deck.append(target)
            return True
    return False


# --- ST03-004: Gecko Moria ---
@register_effect("ST03-004", "on_play", "[On Play] Add Character from trash to hand")
def st03_004_moria(game_state, player, card):
    """Add Seven Warlords/Thriller Bark Character cost 4 or less from trash to hand."""
    valid = [c for c in player.trash
             if getattr(c, 'card_type', '') == 'CHARACTER'
             and (getattr(c, 'cost', 0) or 0) <= 4
             and ('seven warlords' in (c.card_origin or '').lower()
                  or 'thriller bark' in (c.card_origin or '').lower())
             and 'gecko moria' not in (getattr(c, 'name', '') or '').lower()]
    if valid:
        target = valid[0]
        player.trash.remove(target)
        player.hand.append(target)
        return True
    return False


# --- ST03-005: Dracule Mihawk ---
@register_effect("ST03-005", "on_attack", "[DON!! x1] Draw 2, trash 2")
def st03_005_mihawk(game_state, player, card):
    """DON x1: Draw 2 cards and trash 2 cards from hand."""
    if getattr(card, 'attached_don', 0) >= 1:
        draw_cards(player, 2)
        trash_from_hand(player, 2, game_state, card)
        return True
    return False


# --- ST03-007: Sentomaru ---
@register_effect("ST03-007", "activate", "[DON!! x1] [Activate: Main] Play Pacifista cost 4 or less from deck")
def st03_007_sentomaru(game_state, player, card):
    """DON x1, Once Per Turn, Rest 2 DON: Play Pacifista cost 4 or less from deck."""
    if hasattr(card, 'st03_007_used') and card.st03_007_used:
        return False
    if getattr(card, 'attached_don', 0) >= 1:
        active_don = player.don_pool.count("active")
        if len(active_don) >= 2:
            active_don[0].is_resting = True
            active_don[1].is_resting = True
            pacifistas = [c for c in player.deck
                          if 'pacifista' in (getattr(c, 'name', '') or '').lower()
                          and (getattr(c, 'cost', 0) or 0) <= 4]
            if pacifistas:
                target = pacifistas[0]
                player.deck.remove(target)
                game_state.play_card_to_field_by_effect(player, target)
                random.shuffle(player.deck)
            card.st03_007_used = True
            return True
    return False


# --- ST03-008: Trafalgar Law ---
@register_effect("ST03-008", "blocker", "[Blocker]")
def st03_008_law(game_state, player, card):
    """Blocker: Can redirect attacks."""
    card.is_blocker = True
    return True


# --- ST03-009: Donquixote Doflamingo ---
@register_effect("ST03-009", "on_play", "[On Play] Return cost 7 or less Character to hand")
def st03_009_doffy(game_state, player, card):
    """Return up to 1 Character with cost 7 or less to owner's hand."""
    opponent = get_opponent(game_state, player)
    opp_valid = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 7]
    if opp_valid:
        return create_return_to_hand_choice(game_state, player, opp_valid, source_card=card,
                                            prompt="Choose opponent's cost 7 or less Character to return")
    return False


# --- ST03-010: Bartholomew Kuma ---
@register_effect("ST03-010", "on_play", "[On Play] Look at 3 cards from deck, reorder")
def st03_010_kuma(game_state, player, card):
    """Look at 3 cards from top of deck and return them to top or bottom in any order."""
    # Simplified: just shuffle top 3
    if len(player.deck) >= 3:
        top3 = player.deck[:3]
        player.deck = player.deck[3:]
        random.shuffle(top3)
        player.deck = top3 + player.deck
        return True
    return False


# --- ST03-013: Boa Hancock ---
@register_effect("ST03-013", "blocker", "[Blocker]")
def st03_013_hancock(game_state, player, card):
    """Blocker: Can redirect attacks."""
    card.is_blocker = True
    return True


# --- ST03-014: Marshall.D.Teach ---
@register_effect("ST03-014", "on_play", "[On Play] Return cost 3 or less Character to hand")
def st03_014_teach(game_state, player, card):
    """Return up to 1 Character with cost 3 or less to owner's hand."""
    opponent = get_opponent(game_state, player)
    opp_valid = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
    if opp_valid:
        target = opp_valid[0]
        opponent.cards_in_play.remove(target)
        opponent.hand.append(target)
        return True
    return False

