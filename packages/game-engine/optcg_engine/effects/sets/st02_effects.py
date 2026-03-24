"""
Hardcoded effects for ST02 cards.
"""

import random

from ..hardcoded import (
    create_target_choice, get_opponent, register_effect, trash_from_hand,
)


# --- ST02-009: Trafalgar Law ---
@register_effect("ST02-009", "ON_PLAY", "Set Supernovas/Heart Pirates cost 5 or less active")
def law_st02_effect(game_state, player, card):
    targets = [c for c in player.cards_in_play
              if ('supernovas' in (c.card_origin or '').lower()
                  or 'heart pirates' in (c.card_origin or '').lower())
              and (getattr(c, 'cost', 0) or 0) <= 5
              and c.is_resting]
    if targets:
        return create_target_choice(
            game_state, player, targets,
            callback_action="set_active",
            source_card=card,
            prompt="Choose your Supernovas/Heart Pirates cost 5 or less Character to set active"
        )
    return False


# --- ST02-001: Eustass"Captain"Kid (Leader) ---
@register_effect("ST02-001", "activate", "[Activate: Main] Rest 3 DON, trash 1: Set Leader active")
def st02_001_kid_leader(game_state, player, card):
    """Once Per Turn, Rest 3 DON, trash 1 from hand: Set this Leader as active."""
    if hasattr(card, 'st02_001_used') and card.st02_001_used:
        return False
    active_don = player.don_pool.count("active")
    if len(active_don) >= 3 and player.hand:
        for i, don in enumerate(active_don[:3]):
            don.is_resting = True
        trash_from_hand(player, 1, game_state, card)
        card.is_resting = False
        card.st02_001_used = True
        return True
    return False


# --- ST02-003: Urouge ---
@register_effect("ST02-003", "continuous", "[DON!! x1] If 3+ Characters, +2000 power")
def st02_003_urouge(game_state, player, card):
    """DON x1: If you have 3+ Characters, this card gains +2000 power."""
    if getattr(card, 'attached_don', 0) >= 1:
        if len(player.cards_in_play) >= 3:
            card.power_modifier = getattr(card, 'power_modifier', 0) + 2000
            return True
    return False


# --- ST02-004: Capone"Gang"Bege ---
@register_effect("ST02-004", "blocker", "[Blocker]")
def st02_004_bege(game_state, player, card):
    """Blocker: Can redirect attacks."""
    card.is_blocker = True
    return True


# --- ST02-005: Killer ---
@register_effect("ST02-005", "on_play", "[On Play] K.O. opponent's rested Character with cost 3 or less")
def st02_005_killer(game_state, player, card):
    """K.O. up to 1 of opponent's rested Characters with cost 3 or less."""
    opponent = get_opponent(game_state, player)
    rested_low_cost = [c for c in opponent.cards_in_play
                       if getattr(c, 'is_resting', False) and (getattr(c, 'cost', 0) or 0) <= 3]
    if rested_low_cost:
        target = rested_low_cost[0]
        opponent.cards_in_play.remove(target)
        opponent.trash.append(target)
        return True
    return False


# --- ST02-007: Jewelry Bonney ---
@register_effect("ST02-007", "activate", "[Activate: Main] Rest DON and this: Search for Supernovas")
def st02_007_bonney(game_state, player, card):
    """Rest 1 DON and this Character: Look at 5 cards, add 1 Supernovas to hand."""
    if getattr(card, 'is_resting', False):
        return False
    active_don = player.don_pool.count("active")
    if active_don:
        active_don[0].is_resting = True
        card.is_resting = True
        # Look at top 5 cards
        if player.deck:
            top_cards = player.deck[:5]
            supernovas = [c for c in top_cards if 'supernova' in (c.card_origin or '').lower()]
            if supernovas:
                player.deck.remove(supernovas[0])
                player.hand.append(supernovas[0])
            random.shuffle(player.deck)
        return True
    return False


# --- ST02-008: Scratchmen Apoo ---
@register_effect("ST02-008", "on_attack", "[DON!! x1] Rest up to 1 opponent's DON")
def st02_008_apoo(game_state, player, card):
    """DON x1: Rest up to 1 of opponent's DON cards."""
    if getattr(card, 'attached_don', 0) >= 1:
        opponent = get_opponent(game_state, player)
        active_don = opponent.don_pool.count("active")
        if active_don:
            active_don[0].is_resting = True
            return True
    return False


# --- ST02-009: Trafalgar Law ---
@register_effect("ST02-009", "on_play", "[On Play] Set Supernovas/Heart Pirates Character as active")
def st02_009_law(game_state, player, card):
    """Set up to 1 Supernovas or Heart Pirates Character with cost 5 or less as active."""
    rested = [c for c in player.cards_in_play
              if getattr(c, 'is_resting', False)
              and (getattr(c, 'cost', 0) or 0) <= 5
              and ('supernova' in (c.card_origin or '').lower()
                   or 'heart pirates' in (c.card_origin or '').lower())]
    if rested:
        rested[0].is_resting = False
        return True
    return False


# --- ST02-010: Basil Hawkins ---
@register_effect("ST02-010", "on_battle", "[DON!! x1] [Once Per Turn] Set active after battling Character")
def st02_010_hawkins(game_state, player, card):
    """DON x1, Once Per Turn: If this battles a Character, set this card as active."""
    if hasattr(card, 'st02_010_used') and card.st02_010_used:
        return False
    if getattr(card, 'attached_don', 0) >= 1:
        card.is_resting = False
        card.st02_010_used = True
        return True
    return False


# --- ST02-013: Eustass"Captain"Kid ---
@register_effect("ST02-013", "blocker", "[Blocker]")
def st02_013_kid_blocker(game_state, player, card):
    """Blocker: Can redirect attacks."""
    card.is_blocker = True
    return True


@register_effect("ST02-013", "end_of_turn", "[DON!! x1] [End of Your Turn] Set this Character as active")
def st02_013_kid_eot(game_state, player, card):
    """DON x1: At end of turn, set this Character as active."""
    if getattr(card, 'attached_don', 0) >= 1:
        card.is_resting = False
        return True
    return False


# --- ST02-014: X.Drake ---
@register_effect("ST02-014", "continuous", "[DON!! x1] If rested, Supernovas/Navy gain +1000 power")
def st02_014_drake(game_state, player, card):
    """DON x1: If this Character is rested, Supernovas/Navy Leaders and Characters gain +1000."""
    if getattr(card, 'attached_don', 0) >= 1 and getattr(card, 'is_resting', False):
        targets = [c for c in player.cards_in_play
                   if ('supernova' in (c.card_origin or '').lower()
                       or 'navy' in (c.card_origin or '').lower())]
        if player.leader and ('supernova' in (player.leader.card_origin or '').lower()
                              or 'navy' in (player.leader.card_origin or '').lower()):
            player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 1000
        for t in targets:
            t.power_modifier = getattr(t, 'power_modifier', 0) + 1000
        return True
    return False

