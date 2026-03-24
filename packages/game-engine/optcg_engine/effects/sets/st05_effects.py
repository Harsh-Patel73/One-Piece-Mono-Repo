"""
Hardcoded effects for ST05 cards.
"""

import random

from ..hardcoded import (
    add_don_from_deck, create_target_choice, draw_cards, get_characters_by_type,
    get_opponent, register_effect,
)


# --- ST05-001: Shanks (Leader) ---
@register_effect("ST05-001", "activate", "[Activate: Main] DON -3: FILM characters +2000")
def st05_001_shanks_leader(game_state, player, card):
    """Once Per Turn, DON -3: All FILM type Characters gain +2000 power during this turn."""
    if hasattr(card, 'st05_001_used') and card.st05_001_used:
        return False
    if len(player.don_pool) >= 3:
        for _ in range(3):
            if player.don_pool:
                don = player.don_pool.pop()
                if hasattr(player, 'don_deck'):
                    player.don_deck.append(don)
        film_chars = get_characters_by_type(player, 'FILM')
        for char in film_chars:
            char.power_modifier = getattr(char, 'power_modifier', 0) + 2000
        card.st05_001_used = True
        return True
    return False


# --- ST05-002: Ain ---
@register_effect("ST05-002", "on_play", "[On Play] Add 1 rested DON from deck")
def st05_002_ain(game_state, player, card):
    """Add up to 1 DON from deck and rest it."""
    add_don_from_deck(player, 1, set_active=False)
    return True


# --- ST05-003: Ann ---
@register_effect("ST05-003", "blocker", "[Blocker]")
def st05_003_ann(game_state, player, card):
    """Blocker: Can redirect attacks."""
    card.is_blocker = True
    return True


# --- ST05-004: Uta ---
@register_effect("ST05-004", "blocker", "[Blocker]")
def st05_004_uta_blocker(game_state, player, card):
    """Blocker: Can redirect attacks."""
    card.is_blocker = True
    return True


@register_effect("ST05-004", "on_block", "[On Block] DON -1: Rest opponent's cost 5 or less Character")
def st05_004_uta_block(game_state, player, card):
    """DON -1: Rest up to 1 of opponent's Characters with cost 5 or less."""
    if player.don_pool:
        don = player.don_pool.pop()
        if hasattr(player, 'don_deck'):
            player.don_deck.append(don)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play
                   if (getattr(c, 'cost', 0) or 0) <= 5 and not getattr(c, 'is_resting', False)]
        if targets:
            return create_target_choice(
                game_state, player, targets,
                callback_action="rest_target",
                source_card=card,
                prompt="Choose opponent's cost 5 or less Character to rest"
            )
        return True
    return False


# --- ST05-005: Carina ---
@register_effect("ST05-005", "activate", "[Activate: Main] Rest this and trash FILM: Add 2 rested DON")
def st05_005_carina(game_state, player, card):
    """Once Per Turn: Rest this and trash FILM card: If opponent has more DON, add 2 rested DON."""
    if hasattr(card, 'st05_005_used') and card.st05_005_used:
        return False
    if getattr(card, 'is_resting', False):
        return False
    film_cards = [c for c in player.hand if 'film' in (c.card_origin or '').lower()]
    opponent = get_opponent(game_state, player)
    if film_cards and len(opponent.don_pool) > len(player.don_pool):
        player.hand.remove(film_cards[0])
        player.trash.append(film_cards[0])
        card.is_resting = True
        add_don_from_deck(player, 2, set_active=False)
        card.st05_005_used = True
        return True
    return False


# --- ST05-006: Gild Tesoro ---
@register_effect("ST05-006", "on_attack", "[When Attacking] DON -2: Draw 2")
def st05_006_tesoro(game_state, player, card):
    """DON -2: Draw 2 cards."""
    if len(player.don_pool) >= 2:
        for _ in range(2):
            if player.don_pool:
                don = player.don_pool.pop()
                if hasattr(player, 'don_deck'):
                    player.don_deck.append(don)
        draw_cards(player, 2)
        return True
    return False


# --- ST05-008: Shiki ---
@register_effect("ST05-008", "continuous", "If 8+ DON, cannot be K.O.'d in battle")
def st05_008_shiki(game_state, player, card):
    """If you have 8+ DON on field, this Character cannot be K.O.'d in battle."""
    if len(player.don_pool) >= 8:
        card.cannot_be_ko_in_battle = True
        return True
    return False


# --- ST05-010: Zephyr ---
@register_effect("ST05-010", "continuous", "+3000 power when battling Strike attribute")
def st05_010_zephyr_strike(game_state, player, card):
    """When battling Strike attribute Characters, gain +3000 power."""
    # This is tracked during battle resolution
    card.bonus_vs_strike = 3000
    return True


@register_effect("ST05-010", "activate", "[Activate: Main] DON -1: +2000 power")
def st05_010_zephyr_activate(game_state, player, card):
    """Once Per Turn, DON -1: This Character gains +2000 power."""
    if hasattr(card, 'st05_010_used') and card.st05_010_used:
        return False
    if player.don_pool:
        don = player.don_pool.pop()
        if hasattr(player, 'don_deck'):
            player.don_deck.append(don)
        card.power_modifier = getattr(card, 'power_modifier', 0) + 2000
        card.st05_010_used = True
        return True
    return False


# --- ST05-011: Douglas Bullet ---
@register_effect("ST05-011", "activate", "[Activate: Main] DON -4: Rest 2 cost 6 or less, gain Double Attack")
def st05_011_bullet(game_state, player, card):
    """Once Per Turn, DON -4: Rest up to 2 opponent's cost 6 or less Characters. Gain Double Attack."""
    if hasattr(card, 'st05_011_used') and card.st05_011_used:
        return False
    if len(player.don_pool) >= 4:
        for _ in range(4):
            if player.don_pool:
                don = player.don_pool.pop()
                if hasattr(player, 'don_deck'):
                    player.don_deck.append(don)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play
                   if (getattr(c, 'cost', 0) or 0) <= 6 and not getattr(c, 'is_resting', False)]
        for t in targets[:2]:
            t.is_resting = True
        card.has_double_attack = True
        card.st05_011_used = True
        return True
    return False


# --- ST05-014: Buena Festa ---
@register_effect("ST05-014", "on_play", "[On Play] Search deck for FILM card")
def st05_014_festa(game_state, player, card):
    """Look at 5 cards, add 1 FILM card to hand."""
    if player.deck:
        top5 = player.deck[:5]
        film = [c for c in top5
                if 'film' in (c.card_origin or '').lower()
                and 'buena festa' not in (getattr(c, 'name', '') or '').lower()]
        if film:
            player.deck.remove(film[0])
            player.hand.append(film[0])
        random.shuffle(player.deck)
        return True
    return False

