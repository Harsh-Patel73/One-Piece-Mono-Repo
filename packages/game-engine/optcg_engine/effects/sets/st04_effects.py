"""
Hardcoded effects for ST04 cards.
"""

from ..hardcoded import (
    add_don_from_deck, create_ko_choice, create_play_from_hand_choice, draw_cards,
    get_opponent, register_effect, trash_from_hand,
)


# --- ST04-001: Kaido (Leader) ---
@register_effect("ST04-001", "activate", "[Activate: Main] DON -7: Trash opponent's Life")
def st04_001_kaido_leader(game_state, player, card):
    """Once Per Turn, DON -7: Trash up to 1 of opponent's Life cards."""
    if hasattr(card, 'st04_001_used') and card.st04_001_used:
        return False
    if len(player.don_pool) >= 7:
        for _ in range(7):
            if player.don_pool:
                don = player.don_pool.pop()
                if hasattr(player, 'don_deck'):
                    player.don_deck.append(don)
        opponent = get_opponent(game_state, player)
        if opponent.life_cards:
            life = opponent.life_cards.pop()
            opponent.trash.append(life)
        card.st04_001_used = True
        return True
    return False


# --- ST04-002: Ulti ---
@register_effect("ST04-002", "on_play", "[On Play] DON -1: Play Page One cost 4 or less from hand")
def st04_002_ulti(game_state, player, card):
    """DON -1: Play Page One cost 4 or less from hand."""
    if player.don_pool:
        don = player.don_pool.pop()
        if hasattr(player, 'don_deck'):
            player.don_deck.append(don)
        page_ones = [c for c in player.hand
                     if 'page one' in (getattr(c, 'name', '') or '').lower()
                     and (getattr(c, 'cost', 0) or 0) <= 4]
        if page_ones:
            return create_play_from_hand_choice(
                game_state, player, page_ones, source_card=card,
                prompt="Choose Page One cost 4 or less to play from hand"
            )
        return True
    return False


# --- ST04-003: Kaido ---
@register_effect("ST04-003", "on_play", "[On Play] DON -5: K.O. cost 6 or less, gain Rush")
def st04_003_kaido(game_state, player, card):
    """DON -5: K.O. opponent's cost 6 or less Character. Gain Rush this turn."""
    if len(player.don_pool) >= 5:
        for _ in range(5):
            if player.don_pool:
                don = player.don_pool.pop()
                if hasattr(player, 'don_deck'):
                    player.don_deck.append(don)
        card.has_rush = True
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 6]
        if targets:
            return create_ko_choice(
                game_state, player, targets, source_card=card,
                prompt="Choose opponent's cost 6 or less Character to KO"
            )
        return True
    return False


# --- ST04-004: King ---
@register_effect("ST04-004", "on_play", "[On Play] DON -1: K.O. cost 4 or less Character")
def st04_004_king(game_state, player, card):
    """DON -1: K.O. opponent's cost 4 or less Character."""
    if player.don_pool:
        don = player.don_pool.pop()
        if hasattr(player, 'don_deck'):
            player.don_deck.append(don)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
        if targets:
            return create_ko_choice(
                game_state, player, targets, source_card=card,
                prompt="Choose opponent's cost 4 or less Character to KO"
            )
        return True
    return False


# --- ST04-005: Queen ---
@register_effect("ST04-005", "blocker", "[Blocker]")
def st04_005_queen_blocker(game_state, player, card):
    """Blocker: Can redirect attacks."""
    card.is_blocker = True
    return True


@register_effect("ST04-005", "on_play", "[On Play] DON -1: Draw 2, trash 1")
def st04_005_queen_play(game_state, player, card):
    """DON -1: Draw 2 cards and trash 1 from hand."""
    if player.don_pool:
        don = player.don_pool.pop()
        if hasattr(player, 'don_deck'):
            player.don_deck.append(don)
        draw_cards(player, 2)
        trash_from_hand(player, 1, game_state, card)
        return True
    return False


# --- ST04-006: Sasaki ---
@register_effect("ST04-006", "on_play", "[On Play] DON -1: Draw 1 card")
def st04_006_sasaki(game_state, player, card):
    """DON -1: Draw 1 card."""
    if player.don_pool:
        don = player.don_pool.pop()
        if hasattr(player, 'don_deck'):
            player.don_deck.append(don)
        draw_cards(player, 1)
        return True
    return False


# --- ST04-008: Jack ---
@register_effect("ST04-008", "on_play", "[On Play] Trash 1: Add 1 active DON from deck")
def st04_008_jack(game_state, player, card):
    """Trash 1 from hand: Add 1 DON from deck and set it as active."""
    if player.hand:
        trash_from_hand(player, 1, game_state, card)
        add_don_from_deck(player, 1, set_active=True)
        return True
    return False


# --- ST04-010: Who's.Who ---
@register_effect("ST04-010", "on_play", "[On Play] DON -1: K.O. cost 3 or less Character")
def st04_010_whoswho(game_state, player, card):
    """DON -1: K.O. opponent's cost 3 or less Character."""
    if player.don_pool:
        don = player.don_pool.pop()
        if hasattr(player, 'don_deck'):
            player.don_deck.append(don)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
        if targets:
            return create_ko_choice(
                game_state, player, targets, source_card=card,
                prompt="Choose opponent's cost 3 or less Character to KO"
            )
        return True
    return False


# --- ST04-011: Black Maria ---
@register_effect("ST04-011", "blocker", "[Blocker]")
def st04_011_maria(game_state, player, card):
    """Blocker: Can redirect attacks."""
    card.is_blocker = True
    return True

