"""
Hardcoded effects for ST09 cards.
"""

from ..hardcoded import (
    create_play_from_hand_choice, create_target_choice, get_opponent, register_effect,
    trash_from_hand,
)


# --- ST09-008: Shimotsuki Ushimaru ---
@register_effect("ST09-008", "WHEN_ATTACKING", "Add Life to hand: Play yellow Land of Wano cost 4 or less")
def ushimaru_effect(game_state, player, card):
    if getattr(card, 'attached_don', 0) >= 1 and player.life_cards:
        life = player.life_cards.pop()
        player.hand.append(life)
        wano = [c for c in player.hand
               if 'yellow' in (getattr(c, 'colors', '') or '').lower()
               and 'land of wano' in (c.card_origin or '').lower()
               and (getattr(c, 'cost', 0) or 0) <= 4
               and getattr(c, 'card_type', '') == 'CHARACTER']
        if wano:
            char = wano[0]
            player.hand.remove(char)
            player.cards_in_play.append(char)
            return True
    return False


# --- ST09-004: Kaido ---
@register_effect("ST09-004", "CONTINUOUS", "If DONx1 and 2 or less life, cannot be KO'd in battle")
def st09_004_kaido(game_state, player, card):
    """Continuous: If DONx1 and 2 or less life, cannot be KO'd in battle."""
    if getattr(card, 'attached_don', 0) >= 1 and check_life_count(player, 2):
        card.protected_from_battle_ko = True
        return True
    return False


# --- ST09-014: Narikabura Arrow ---
@register_effect("ST09-014", "COUNTER", "If 2 or less life, -3000 power to opponent")
def st09_014_narikabura(game_state, player, card):
    """Counter: If 2 or less life, give opponent's card -3000 power."""
    if check_life_count(player, 2):
        opponent = get_opponent(game_state, player)
        target = opponent.leader if opponent.leader else (opponent.cards_in_play[0] if opponent.cards_in_play else None)
        if target:
            add_power_modifier(target, -3000)
            return True
    return False


# --- ST09-015: Thunder Bagua (Land of Wano) ---
@register_effect("ST09-015", "COUNTER", "+4000 power, add opponent's cost 3 or less to their life if 2 or less life")
def st09_015_thunder_bagua(game_state, player, card):
    """Counter: +4000 power, add opponent's cost 3 or less to their life if 2 or less life."""
    target = player.leader if player.leader else (player.cards_in_play[0] if player.cards_in_play else None)
    if target:
        add_power_modifier(target, 4000)
        if check_life_count(player, 2):
            opponent = get_opponent(game_state, player)
            targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
            if targets:
                return create_target_choice(
                    game_state, player, targets,
                    callback_action="add_to_opponent_life",
                    source_card=card,
                    prompt="Choose opponent's cost 3 or less Character to add to their Life"
                )
        return True
    return False


# --- ST09-001: Yamato (Leader) ---
@register_effect("ST09-001", "opponent_turn", "[DON!! x1] [Opponent's Turn] If 2- life, +1000 power")
def st09_001_yamato_leader(game_state, player, card):
    """DON x1, Opponent's Turn: If you have 2 or less Life, this Leader gains +1000 power."""
    if getattr(card, 'attached_don', 0) >= 1:
        if len(player.life_cards) <= 2:
            card.power_modifier = getattr(card, 'power_modifier', 0) + 1000
            return True
    return False


# --- ST09-004: Kaido ---
@register_effect("ST09-004", "continuous", "[DON!! x1] If 2 or less Life, cannot be K.O.'d in battle")
def st09_004_kaido(game_state, player, card):
    """DON x1: If you have 2 or less Life cards, cannot be K.O.'d in battle."""
    if getattr(card, 'attached_don', 0) >= 1:
        if len(player.life_cards) <= 2:
            card.cannot_be_ko_in_battle = True
            return True
    return False


# --- ST09-005: Kouzuki Oden ---
@register_effect("ST09-005", "continuous", "[DON!! x1] Double Attack")
def st09_005_oden_continuous(game_state, player, card):
    """DON x1: This Character gains Double Attack."""
    if getattr(card, 'attached_don', 0) >= 1:
        card.has_double_attack = True
    return True


@register_effect("ST09-005", "on_ko", "[On K.O.] Trash 2: Add 1 card to Life")
def st09_005_oden_ko(game_state, player, card):
    """On K.O.: Trash 2 from hand: Add 1 card from deck to top of Life."""
    if len(player.hand) >= 2:
        trash_from_hand(player, 2, game_state, card)
        if player.deck:
            new_life = player.deck.pop(0)
            player.life_cards.append(new_life)
        return True
    return False


# --- ST09-007: Shinobu ---
@register_effect("ST09-007", "blocker", "[Blocker]")
def st09_007_shinobu_blocker(game_state, player, card):
    """Blocker: Can redirect attacks."""
    card.is_blocker = True
    return True


@register_effect("ST09-007", "on_block", "[On Block] Add Life to hand: +4000 power")
def st09_007_shinobu_block(game_state, player, card):
    """Add 1 Life to hand: This Character gains +4000 power during this battle."""
    if player.life_cards:
        life = player.life_cards.pop()
        player.hand.append(life)
        card.power_modifier = getattr(card, 'power_modifier', 0) + 4000
        return True
    return False


# --- ST09-008: Shimotsuki Ushimaru ---
@register_effect("ST09-008", "on_attack", "[DON!! x1] Add Life to hand: Play yellow Wano cost 4 or less")
def st09_008_ushimaru(game_state, player, card):
    """DON x1: Add 1 Life to hand: Play yellow Wano Character cost 4 or less from hand."""
    if getattr(card, 'attached_don', 0) >= 1:
        if player.life_cards:
            life = player.life_cards.pop()
            player.hand.append(life)
            wano = [c for c in player.hand
                    if 'wano' in (c.card_origin or '').lower()
                    and 'yellow' in (getattr(c, 'colors', '') or '').lower()
                    and (getattr(c, 'cost', 0) or 0) <= 4
                    and getattr(c, 'card_type', '') == 'CHARACTER']
            if wano:
                return create_play_from_hand_choice(
                    game_state, player, wano, source_card=card,
                    prompt="Choose yellow Land of Wano cost 4 or less Character to play"
                )
            return True
    return False


# --- ST09-010: Portgas.D.Ace ---
@register_effect("ST09-010", "on_ko_prevention", "[Once Per Turn] Trash 1 Life instead of K.O.")
def st09_010_ace(game_state, player, card):
    """Once Per Turn: If this Character would be K.O.'d, trash 1 from Life instead."""
    if hasattr(card, 'st09_010_used') and card.st09_010_used:
        return False
    if player.life_cards:
        life = player.life_cards.pop()
        player.trash.append(life)
        card.st09_010_used = True
        return True  # Prevents K.O.
    return False


# --- ST09-012: Yamato ---
@register_effect("ST09-012", "on_attack", "[When Attacking] Add Life to hand: +2000 power until next turn")
def st09_012_yamato(game_state, player, card):
    """Add 1 Life to hand: This Character gains +2000 power until start of next turn."""
    if player.life_cards:
        life = player.life_cards.pop()
        player.hand.append(life)
        card.power_modifier = getattr(card, 'power_modifier', 0) + 2000
        return True
    return False

