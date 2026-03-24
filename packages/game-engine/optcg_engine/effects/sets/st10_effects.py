"""
Hardcoded effects for ST10 cards.
"""

from ..hardcoded import (
    add_don_from_deck, create_bottom_deck_choice, create_ko_choice, create_play_from_hand_choice,
    create_power_effect_choice, draw_cards, get_opponent, register_effect,
    trash_from_hand,
)


# --- ST10-003: Eustass"Captain"Kid (Leader) ---
@register_effect("ST10-003", "CONTINUOUS", "If 4+ life, Leader -1000 power")
def st10_003_kid_continuous(game_state, player, card):
    """Continuous: If 4+ life, Leader loses 1000 power."""
    if len(player.life_cards) >= 4:
        add_power_modifier(card, -1000)
    return True


@register_effect("ST10-003", "WHEN_ATTACKING", "DON -1: Leader can attack active characters")
def st10_003_kid_attack(game_state, player, card):
    """When Attacking: DON -1 to attack active characters."""
    if hasattr(player, 'don_deck'):
        active_don = [d for d in player.don_pool if not d.is_resting]
        if active_don:
            don = active_don[0]
            player.don_pool.remove(don)
            player.don_deck.append(don)
            card.can_attack_active = True
            return True
    return False


# --- ST10-001: Trafalgar Law (Leader) ---
@register_effect("ST10-001", "activate", "[Activate: Main] DON -3: Bottom deck 3000 power, play cost 4")
def st10_001_law_leader(game_state, player, card):
    """Once Per Turn, DON -3: Bottom deck opponent's 3000 power or less, play cost 4 or less from hand."""
    if hasattr(card, 'st10_001_used') and card.st10_001_used:
        return False
    if len(player.don_pool) >= 3:
        for _ in range(3):
            if player.don_pool:
                don = player.don_pool.pop()
                if hasattr(player, 'don_deck'):
                    player.don_deck.append(don)
        card.st10_001_used = True
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play
                   if (getattr(c, 'power', 0) or 0) + getattr(c, 'power_modifier', 0) <= 3000]
        if targets:
            return create_bottom_deck_choice(
                game_state, player, targets, source_card=card,
                prompt="Choose opponent's 3000 power or less to place at bottom (then play cost 4 or less)"
            )
        # No targets to bottom deck, still allow play from hand
        playable = [c for c in player.hand
                    if getattr(c, 'card_type', '') == 'CHARACTER'
                    and (getattr(c, 'cost', 0) or 0) <= 4]
        if playable:
            return create_play_from_hand_choice(
                game_state, player, playable, source_card=card,
                prompt="Choose cost 4 or less Character to play from hand"
            )
        return True
    return False


# --- ST10-002: Monkey.D.Luffy (Leader) ---
@register_effect("ST10-002", "activate", "[Activate: Main] If 0 or 8+ DON, add 1 active DON")
def st10_002_luffy_leader(game_state, player, card):
    """Once Per Turn: If 0 DON or 8+ DON on field, add 1 DON from deck and set it active."""
    if hasattr(card, 'st10_002_used') and card.st10_002_used:
        return False
    don_count = len(player.don_pool)
    if don_count == 0 or don_count >= 8:
        if hasattr(player, 'don_deck') and player.don_deck:
            don = player.don_deck.pop(0)
            don.is_resting = False
            player.don_pool.append(don)
            card.st10_002_used = True
            return True
    return False


# --- ST10-003: Eustass"Captain"Kid (Leader) ---
@register_effect("ST10-003", "continuous", "[Your Turn] If 4+ life, this Leader -1000 power")
def st10_003_kid_leader_continuous(game_state, player, card):
    """Your Turn: If you have 4 or more Life cards, give this Leader -1000 power."""
    if len(player.life_cards) >= 4:
        card.power_modifier = getattr(card, 'power_modifier', 0) - 1000
        return True
    return False


@register_effect("ST10-003", "on_attack", "[When Attacking] DON -1: +2000 power")
def st10_003_kid_leader_attack(game_state, player, card):
    """When Attacking, DON -1: This Leader gains +2000 power during this turn."""
    if len(player.don_pool) >= 1:
        don = player.don_pool.pop()
        if hasattr(player, 'don_deck'):
            player.don_deck.append(don)
        card.power_modifier = getattr(card, 'power_modifier', 0) + 2000
        return True
    return False


# --- ST10-004: Sanji ---
@register_effect("ST10-004", "on_play", "[On Play] If opponent has 5000+ power Character, gain Rush")
def st10_004_sanji(game_state, player, card):
    """If opponent has a Character with 5000+ power, this Character gains Rush."""
    opponent = get_opponent(game_state, player)
    high_power = [c for c in opponent.cards_in_play if (getattr(c, 'power', 0) or 0) >= 5000]
    if high_power:
        card.has_rush = True
    return True


# --- ST10-005: Jinbe ---
@register_effect("ST10-005", "on_attack", "[DON!! x1] Give opponent's Character -2000 power")
def st10_005_jinbe(game_state, player, card):
    """DON x1: Give up to 1 of opponent's Characters -2000 power."""
    if getattr(card, 'attached_don', 0) >= 1:
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            return create_power_effect_choice(
                game_state, player, opponent.cards_in_play, -2000,
                source_card=card,
                prompt="Choose an opponent's Character to give -2000 power"
            )
    return False


# --- ST10-006: Monkey.D.Luffy ---
@register_effect("ST10-006", "continuous", "[Rush]")
def st10_006_luffy_rush(game_state, player, card):
    """Rush: Can attack on the turn played."""
    card.has_rush = True
    return True


@register_effect("ST10-006", "on_blocker_activated", "[Once Per Turn] When Blocker activated, K.O. 8000 or less")
def st10_006_luffy_blocker(game_state, player, card):
    """Once Per Turn: When opponent activates Blocker, K.O. Character with 8000 or less power."""
    if hasattr(card, 'st10_006_used') and card.st10_006_used:
        return False
    card.st10_006_used = True
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'power', 0) or 0) <= 8000]
    if targets:
        return create_ko_choice(
            game_state, player, targets, source_card=card,
            prompt="Choose opponent's 8000 power or less Character to KO"
        )
    return False


# --- ST10-007: Killer ---
@register_effect("ST10-007", "on_don_return", "[Your Turn] [Once Per Turn] When DON returned, K.O. rested cost 3 or less")
def st10_007_killer(game_state, player, card):
    """Once Per Turn: When DON returned to deck, K.O. opponent's rested cost 3 or less."""
    if hasattr(card, 'st10_007_used') and card.st10_007_used:
        return False
    card.st10_007_used = True
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if getattr(c, 'is_resting', False) and (getattr(c, 'cost', 0) or 0) <= 3]
    if targets:
        return create_ko_choice(
            game_state, player, targets, source_card=card,
            prompt="Choose opponent's rested cost 3 or less Character to KO"
        )
    return False


# --- ST10-008: Shachi & Penguin ---
@register_effect("ST10-008", "on_play", "[On Play] If 3 or less DON, add 2 rested DON")
def st10_008_shachi_penguin(game_state, player, card):
    """If you have 3 or less DON on field, add up to 2 DON and rest them."""
    if len(player.don_pool) <= 3:
        add_don_from_deck(player, 2, set_active=False)
        return True
    return False


# --- ST10-009: Jean Bart ---
@register_effect("ST10-009", "on_play", "[On Play] Rest 1 DON: Add 1 active DON from deck")
def st10_009_jean(game_state, player, card):
    """Rest 1 DON: Add 1 DON from deck and set it as active."""
    active_don = player.don_pool.count("active")
    if active_don:
        active_don[0].is_resting = True
        add_don_from_deck(player, 1, set_active=True)
        return True
    return False


# --- ST10-010: Trafalgar Law ---
@register_effect("ST10-010", "blocker", "[Blocker]")
def st10_010_law_blocker(game_state, player, card):
    """Blocker: Can redirect attacks."""
    card.is_blocker = True
    return True


@register_effect("ST10-010", "on_play", "[On Play] DON -1: If opponent has 7+ cards, trash 2 from their hand")
def st10_010_law_play(game_state, player, card):
    """DON -1: If opponent has 7+ cards in hand, trash 2 from their hand."""
    if player.don_pool:
        don = player.don_pool.pop()
        if hasattr(player, 'don_deck'):
            player.don_deck.append(don)
        opponent = get_opponent(game_state, player)
        if len(opponent.hand) >= 7:
            trash_from_hand(opponent, 2)
        return True
    return False


# --- ST10-011: Heat ---
@register_effect("ST10-011", "on_don_return", "[Your Turn] [Once Per Turn] When DON returned, +2000 power")
def st10_011_heat(game_state, player, card):
    """Once Per Turn: When DON returned to deck, this Character gains +2000 power."""
    if hasattr(card, 'st10_011_used') and card.st10_011_used:
        return False
    card.power_modifier = getattr(card, 'power_modifier', 0) + 2000
    card.st10_011_used = True
    return True


# --- ST10-012: Bepo ---
@register_effect("ST10-012", "on_play", "[On Play]/[When Attacking] If opponent has more DON, add 1 rested DON")
def st10_012_bepo_play(game_state, player, card):
    """If opponent has more DON, add 1 DON and rest it."""
    opponent = get_opponent(game_state, player)
    if len(opponent.don_pool) > len(player.don_pool):
        add_don_from_deck(player, 1, set_active=False)
        return True
    return False


@register_effect("ST10-012", "on_attack", "[On Play]/[When Attacking] If opponent has more DON, add 1 rested DON")
def st10_012_bepo_attack(game_state, player, card):
    """If opponent has more DON, add 1 DON and rest it."""
    opponent = get_opponent(game_state, player)
    if len(opponent.don_pool) > len(player.don_pool):
        add_don_from_deck(player, 1, set_active=False)
        return True
    return False


# --- ST10-013: Eustass"Captain"Kid ---
@register_effect("ST10-013", "on_play", "[On Play]/[When Attacking] DON -1: Leader +1000 power")
def st10_013_kid_play(game_state, player, card):
    """DON -1: Up to 1 Leader gains +1000 power until start of next turn."""
    if player.don_pool:
        don = player.don_pool.pop()
        if hasattr(player, 'don_deck'):
            player.don_deck.append(don)
        if player.leader:
            player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 1000
        return True
    return False


@register_effect("ST10-013", "on_attack", "[On Play]/[When Attacking] DON -1: Leader +1000 power")
def st10_013_kid_attack(game_state, player, card):
    """DON -1: Up to 1 Leader gains +1000 power until start of next turn."""
    if player.don_pool:
        don = player.don_pool.pop()
        if hasattr(player, 'don_deck'):
            player.don_deck.append(don)
        if player.leader:
            player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 1000
        return True
    return False


# --- ST10-014: Wire ---
@register_effect("ST10-014", "blocker", "[Blocker]")
def st10_014_wire_blocker(game_state, player, card):
    """Blocker: Can redirect attacks."""
    card.is_blocker = True
    return True


@register_effect("ST10-014", "on_don_return", "[Once Per Turn] When DON returned, draw 1 and trash 1")
def st10_014_wire_don(game_state, player, card):
    """Once Per Turn: When DON returned, draw 1 and trash 1."""
    if hasattr(card, 'st10_014_used') and card.st10_014_used:
        return False
    draw_cards(player, 1)
    trash_from_hand(player, 1, game_state, card)
    card.st10_014_used = True
    return True

