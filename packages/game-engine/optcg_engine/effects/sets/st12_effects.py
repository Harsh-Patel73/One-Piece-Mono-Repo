"""
Hardcoded effects for ST12 cards.
"""

from ..hardcoded import (
    create_ko_choice, create_mode_choice, create_play_from_hand_choice, create_rest_choice,
    draw_cards, get_opponent, register_effect,
)


# --- ST12-007: Rika ---
@register_effect("ST12-007", "ON_PLAY", "Rest 2 DON: If opponent has 3+ Life, set Slash cost 4 or less active")
def rika_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    active_don = [d for d in player.don_pool if not d.is_resting]
    if len(active_don) >= 2 and len(opponent.life_cards) >= 3:
        for don in active_don[:2]:
            don.is_resting = True
        slash = [c for c in player.cards_in_play
                if 'slash' in (getattr(c, 'attributes', '') or '').lower()
                and (getattr(c, 'cost', 0) or 0) <= 4
                and c.is_resting]
        if slash:
            slash[0].is_resting = False
            return True
    return False


# --- ST12-006: Yosaku & Johnny ---
@register_effect("ST12-006", "WHEN_ATTACKING", "Choose: Rest cost 2 or less OR KO rested cost 2 or less")
def yosaku_johnny_effect(game_state, player, card):
    """Choose: Rest OR KO rested cost 2 or less."""
    if getattr(card, 'attached_don', 0) < 1:
        return False

    opponent = get_opponent(game_state, player)

    # Check what options are available
    rested_targets = [c for c in opponent.cards_in_play
                     if c.is_resting and (getattr(c, 'cost', 0) or 0) <= 2]
    active_targets = [c for c in opponent.cards_in_play
                     if not c.is_resting and (getattr(c, 'cost', 0) or 0) <= 2]

    options = []
    if rested_targets:
        options.append(("ko", "KO rested cost 2 or less"))
    if active_targets:
        options.append(("rest", "Rest cost 2 or less"))

    if not options:
        return False

    if len(options) == 1:
        # Only one option available
        if options[0][0] == "ko":
            return create_ko_choice(game_state, player, rested_targets, source_card=card,
                                   prompt="Choose rested cost 2 or less to KO")
        else:
            return create_rest_choice(game_state, player, active_targets, source_card=card,
                                     prompt="Choose cost 2 or less to rest")

    # Both options available - mode choice
    return create_mode_choice(
        game_state, player,
        modes=[
            {"id": "ko", "label": "KO rested cost 2 or less", "targets": rested_targets},
            {"id": "rest", "label": "Rest cost 2 or less", "targets": active_targets}
        ],
        callback="yosaku_johnny_mode",
        source_card=card,
        prompt="Choose effect mode"
    )


# --- ST12-001: Roronoa Zoro & Sanji (Leader) ---
@register_effect("ST12-001", "WHEN_ATTACKING", "Return cost 2+ to hand: Set 7000 power or less active")
def st12_001_zoro_sanji(game_state, player, card):
    """When Attacking (DONx1, Once Per Turn): Return cost 2+ to hand, set 7000 power or less active."""
    if getattr(card, 'attached_don', 0) >= 1:
        if hasattr(card, 'st12_001_used') and card.st12_001_used:
            return False
        chars = [c for c in player.cards_in_play if (getattr(c, 'cost', 0) or 0) >= 2]
        if chars:
            to_return = chars[0]
            player.cards_in_play.remove(to_return)
            player.hand.append(to_return)
            # Set 7000 power or less active
            rested = [c for c in player.cards_in_play
                     if c.is_resting
                     and (getattr(c, 'power', 0) or 0) + (getattr(c, 'power_modifier', 0)) <= 7000]
            if rested:
                rested[0].is_resting = False
            card.st12_001_used = True
            return True
    return False


# --- ST12-002: Kuina ---
@register_effect("ST12-002", "activate", "[Activate: Main] Rest this: Rest opponent's cost 4 or less Character")
def st12_002_kuina(game_state, player, card):
    """Rest this Character: Rest up to 1 of opponent's Characters with cost 4 or less."""
    if not getattr(card, 'is_resting', False):
        card.is_resting = True
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play
                   if (getattr(c, 'cost', 0) or 0) <= 4 and not getattr(c, 'is_resting', False)]
        if targets:
            return create_rest_choice(game_state, player, targets, source_card=card,
                                     prompt="Choose opponent's cost 4 or less to rest")
        return True
    return False


# --- ST12-003: Dracule Mihawk ---
@register_effect("ST12-003", "on_play", "[On Play] If 2 or less Characters, play Slash cost 4 or less rested")
def st12_003_mihawk(game_state, player, card):
    """If you have 2 or less Characters, play Slash Character cost 4 or less from hand rested."""
    if len(player.cards_in_play) <= 2:
        slash_chars = [c for c in player.hand
                       if 'slash' in (getattr(c, 'attribute', '') or '').lower()
                       and (getattr(c, 'cost', 0) or 0) <= 4
                       and getattr(c, 'card_type', '') == 'CHARACTER'
                       and 'dracule mihawk' not in (getattr(c, 'name', '') or '').lower()]
        if slash_chars:
            return create_play_from_hand_choice(
                game_state, player, slash_chars,
                source_card=card, play_rested=True,
                prompt="Choose Slash cost 4 or less Character to play rested"
            )
    return False


# --- ST12-006: Yosaku & Johnny ---
@register_effect("ST12-006", "on_attack", "[DON!! x1] Rest or K.O. cost 2 or less")
def st12_006_yosaku_johnny(game_state, player, card):
    """DON x1: Choose - Rest cost 2 or less OR K.O. rested cost 2 or less."""
    if getattr(card, 'attached_don', 0) >= 1:
        opponent = get_opponent(game_state, player)
        # Prefer K.O. if rested target exists
        rested = [c for c in opponent.cards_in_play
                  if getattr(c, 'is_resting', False) and (getattr(c, 'cost', 0) or 0) <= 2]
        if rested:
            target = rested[0]
            opponent.cards_in_play.remove(target)
            opponent.trash.append(target)
            return True
        # Otherwise rest a target
        active = [c for c in opponent.cards_in_play
                  if not getattr(c, 'is_resting', False) and (getattr(c, 'cost', 0) or 0) <= 2]
        if active:
            active[0].is_resting = True
            return True
    return False


# --- ST12-007: Rika ---
@register_effect("ST12-007", "on_play", "[On Play] Rest 2 DON: If opponent has 3+ Life, set Slash cost 4 or less as active")
def st12_007_rika(game_state, player, card):
    """Rest 2 DON: If opponent has 3+ Life, set Slash Character cost 4 or less as active."""
    active_don = player.don_pool.count("active")
    opponent = get_opponent(game_state, player)
    if len(active_don) >= 2 and len(opponent.life_cards) >= 3:
        active_don[0].is_resting = True
        active_don[1].is_resting = True
        rested_slash = [c for c in player.cards_in_play
                        if getattr(c, 'is_resting', False)
                        and 'slash' in (getattr(c, 'attribute', '') or '').lower()
                        and (getattr(c, 'cost', 0) or 0) <= 4]
        if rested_slash:
            rested_slash[0].is_resting = False
        return True
    return False


# --- ST12-008: Roronoa Zoro ---
@register_effect("ST12-008", "on_attack", "[DON!! x1] Rest opponent's cost 6 or less Character")
def st12_008_zoro(game_state, player, card):
    """DON x1: Rest up to 1 of opponent's Characters with cost 6 or less."""
    if getattr(card, 'attached_don', 0) >= 1:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play
                   if (getattr(c, 'cost', 0) or 0) <= 6 and not getattr(c, 'is_resting', False)]
        if targets:
            return create_rest_choice(game_state, player, targets, source_card=card,
                                      prompt="Choose opponent's cost 6 or less Character to rest")
    return False


# --- ST12-010: Emporio.Ivankov ---
@register_effect("ST12-010", "on_play", "[On Play] Reveal top card, play cost 2 Character")
def st12_010_ivankov_play(game_state, player, card):
    """Reveal 1 card from deck and play cost 2 Character."""
    if player.deck:
        top_card = player.deck[0]
        if getattr(top_card, 'card_type', '') == 'CHARACTER' and (getattr(top_card, 'cost', 0) or 0) == 2:
            player.deck.pop(0)
            player.cards_in_play.append(top_card)
        return True
    return False


@register_effect("ST12-010", "on_attack", "[When Attacking] [Once Per Turn] Draw 1 if 6 or less cards in hand")
def st12_010_ivankov_attack(game_state, player, card):
    """Once Per Turn: Draw 1 card if you have 6 or less cards in hand."""
    if hasattr(card, 'st12_010_used') and card.st12_010_used:
        return False
    if len(player.hand) <= 6:
        draw_cards(player, 1)
        card.st12_010_used = True
        return True
    return False


# --- ST12-011: Sanji ---
@register_effect("ST12-011", "on_attack", "[DON!! x1] If 5 or less cards in hand, +2000 power")
def st12_011_sanji(game_state, player, card):
    """DON x1: If you have 5 or less cards in hand, this Character gains +2000 power."""
    if getattr(card, 'attached_don', 0) >= 1:
        if len(player.hand) <= 5:
            card.power_modifier = getattr(card, 'power_modifier', 0) + 2000
            return True
    return False


# --- ST12-012: Charlotte Pudding ---
@register_effect("ST12-012", "activate", "[Activate: Main] Return this to hand")
def st12_012_pudding(game_state, player, card):
    """Return this Character to owner's hand."""
    if card in player.cards_in_play:
        player.cards_in_play.remove(card)
        player.hand.append(card)
        return True
    return False


# --- ST12-013: Zeff ---
@register_effect("ST12-013", "on_play", "[On Play] Look at 3 cards from deck, reorder")
def st12_013_zeff_play(game_state, player, card):
    """Look at 3 cards from top of deck and place them at top or bottom in any order."""
    # Simplified
    return True


@register_effect("ST12-013", "on_attack", "[When Attacking] Reveal top card, play cost 2 Character rested")
def st12_013_zeff_attack(game_state, player, card):
    """Reveal 1 card from deck and play cost 2 Character rested."""
    if player.deck:
        top_card = player.deck[0]
        if getattr(top_card, 'card_type', '') == 'CHARACTER' and (getattr(top_card, 'cost', 0) or 0) == 2:
            player.deck.pop(0)
            top_card.is_resting = True
            player.cards_in_play.append(top_card)
        return True
    return False


# --- ST12-014: Duval ---
@register_effect("ST12-014", "blocker", "[Blocker]")
def st12_014_duval_blocker(game_state, player, card):
    """Blocker: Can redirect attacks."""
    card.is_blocker = True
    return True


@register_effect("ST12-014", "on_play", "[On Play] Look at 3 cards from deck, reorder")
def st12_014_duval_play(game_state, player, card):
    """Look at 3 cards from top of deck and place them at top or bottom in any order."""
    # Simplified
    return True

