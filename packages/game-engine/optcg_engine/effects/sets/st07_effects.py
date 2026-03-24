"""
Hardcoded effects for ST07 cards.
"""

from ..hardcoded import (
    create_ko_choice, create_mode_choice, create_target_choice, get_opponent,
    register_effect,
)


# --- ST07-010: Charlotte Linlin ---
@register_effect("ST07-010", "ON_PLAY", "Opponent chooses: trash top life OR add deck to life")
def charlotte_linlin_st07_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    # Opponent chooses between losing life or giving you extra life
    modes = [
        {"id": "trash_life", "label": "Trash Top Life", "description": "Trash the top card of your Life (opponent loses 1 life)"},
        {"id": "add_life", "label": "Add to Life", "description": "Add the top card of deck to opponent's Life (opponent gains 1 life)"}
    ]
    # This is opponent's choice, so we pass opponent as the player making the decision
    return create_mode_choice(game_state, opponent, modes, source_card=card,
                               prompt="Charlotte Linlin: Choose your fate - Trash top Life OR let opponent add deck to Life")


# --- ST07-008: Charlotte Pudding ---
@register_effect("ST07-008", "ON_PLAY", "Look at top Life and place at top or bottom")
def charlotte_pudding_st07_effect(game_state, player, card):
    # Just a look effect - no actual change needed for AI
    return True


# --- ST07-001: Charlotte Linlin (Leader) ---
@register_effect("ST07-001", "WHEN_ATTACKING", "Add life to hand, if 2 or less add hand to life")
def st07_001_linlin_leader(game_state, player, card):
    """When Attacking (DONx2): Add life to hand, if 2 or less life add hand card to life."""
    if getattr(card, 'attached_don', 0) >= 2 and player.life_cards:
        life = player.life_cards.pop()
        player.hand.append(life)
        if check_life_count(player, 2) and player.hand:
            hand_card = player.hand[0]  # AI picks first
            player.hand.remove(hand_card)
            player.life_cards.append(hand_card)
        return True
    return False


# --- ST07-001: Charlotte Linlin (Leader) ---
@register_effect("ST07-001", "on_attack", "[DON!! x2] Add from life to hand, if 2- life add to life")
def st07_001_linlin_leader(game_state, player, card):
    """When Attacking (DON x2): Add 1 from top/bottom of Life to hand. If 2 or less Life, add 1 to Life."""
    if getattr(card, 'attached_don', 0) >= 2:
        if player.life_cards:
            life = player.life_cards.pop()
            player.hand.append(life)
        if len(player.life_cards) <= 2 and player.hand:
            # Add a card from hand to top of life
            card_to_add = player.hand[-1]
            player.hand.remove(card_to_add)
            player.life_cards.append(card_to_add)
        return True
    return False


# --- ST07-003: Charlotte Katakuri ---
@register_effect("ST07-003", "on_play", "[On Play] Look at Life, gain Rush if fewer Life than opponent")
def st07_003_katakuri(game_state, player, card):
    """Look at 1 Life card (top or bottom). If fewer Life than opponent, gain Rush."""
    opponent = get_opponent(game_state, player)
    if len(player.life_cards) < len(opponent.life_cards):
        card.has_rush = True
    return True


# --- ST07-004: Charlotte Snack ---
@register_effect("ST07-004", "on_attack", "[DON!! x1] Add Life to hand: Gain Banish and +1000")
def st07_004_snack(game_state, player, card):
    """DON x1: Add 1 Life to hand: Gain Banish and +1000 power."""
    if getattr(card, 'attached_don', 0) >= 1:
        if player.life_cards:
            life = player.life_cards.pop()
            player.hand.append(life)
            card.has_banish = True
            card.power_modifier = getattr(card, 'power_modifier', 0) + 1000
            return True
    return False


# --- ST07-005: Charlotte Daifuku ---
@register_effect("ST07-005", "on_attack", "[DON!! x1] Add Life to hand: Add card to Life")
def st07_005_daifuku(game_state, player, card):
    """DON x1: Add 1 Life to hand: Add 1 card from deck to top of Life."""
    if getattr(card, 'attached_don', 0) >= 1:
        if player.life_cards:
            life = player.life_cards.pop()
            player.hand.append(life)
            if player.deck:
                new_life = player.deck.pop(0)
                player.life_cards.append(new_life)
            return True
    return False


# --- ST07-007: Charlotte Brulee ---
@register_effect("ST07-007", "blocker", "[Blocker]")
def st07_007_brulee(game_state, player, card):
    """Blocker: Can redirect attacks."""
    card.is_blocker = True
    return True


# --- ST07-008: Charlotte Pudding ---
@register_effect("ST07-008", "on_play", "[On Play] Look at Life, reorder")
def st07_008_pudding(game_state, player, card):
    """Look at 1 card from top of Life and place it at top or bottom."""
    # Simplified: can look at life
    return True


# --- ST07-009: Charlotte Mont-d'or ---
@register_effect("ST07-009", "activate", "[Activate: Main] Rest this and add Life to hand: K.O. cost 3 or less")
def st07_009_montdor(game_state, player, card):
    """Rest this and add 1 Life to hand: K.O. opponent's cost 3 or less Character."""
    if not getattr(card, 'is_resting', False) and player.life_cards:
        card.is_resting = True
        life = player.life_cards.pop()
        player.hand.append(life)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
        if targets:
            return create_ko_choice(
                game_state, player, targets, source_card=card,
                prompt="Choose opponent's cost 3 or less Character to KO"
            )
        return True
    return False


# --- ST07-010: Charlotte Linlin ---
@register_effect("ST07-010", "on_play", "[On Play] Opponent chooses: Trash 1 Life or you gain 1 Life")
def st07_010_linlin(game_state, player, card):
    """Opponent chooses: Trash 1 from their Life OR you add 1 card to your Life."""
    opponent = get_opponent(game_state, player)
    # AI: add to player's life (better for player)
    if player.deck:
        new_life = player.deck.pop(0)
        player.life_cards.append(new_life)
    return True


# --- ST07-011: Zeus ---
@register_effect("ST07-011", "activate", "[Activate: Main] Rest this: Charlotte Linlin gains Banish")
def st07_011_zeus(game_state, player, card):
    """Rest this: Up to 1 Charlotte Linlin gains Banish."""
    if not getattr(card, 'is_resting', False):
        card.is_resting = True
        linlins = [c for c in player.cards_in_play
                   if 'charlotte linlin' in (getattr(c, 'name', '') or '').lower()]
        if linlins:
            return create_target_choice(
                game_state, player, linlins,
                callback_action="give_banish",
                source_card=card,
                prompt="Choose Charlotte Linlin to give Banish"
            )
        return True
    return False


# --- ST07-013: Prometheus ---
@register_effect("ST07-013", "activate", "[Activate: Main] Rest this: Charlotte Linlin gains Double Attack")
def st07_013_prometheus(game_state, player, card):
    """Rest this: Up to 1 Charlotte Linlin gains Double Attack."""
    if not getattr(card, 'is_resting', False):
        card.is_resting = True
        linlins = [c for c in player.cards_in_play
                   if 'charlotte linlin' in (getattr(c, 'name', '') or '').lower()]
        if linlins:
            return create_target_choice(
                game_state, player, linlins,
                callback_action="give_double_attack",
                source_card=card,
                prompt="Choose Charlotte Linlin to give Double Attack"
            )
        return True
    return False

