"""
Hardcoded effects for ST11 cards.
"""

from ..hardcoded import (
    create_hand_discard_choice, create_mode_choice, get_opponent, register_effect,
    search_top_cards, set_active,
)


# --- ST11-001: Uta (Leader) ---
@register_effect("ST11-001", "WHEN_ATTACKING", "Reveal top, add FILM to hand")
def uta_leader_effect(game_state, player, card):
    if getattr(card, 'attached_don', 0) >= 1 and player.deck:
        top = player.deck[0]
        if 'film' in (top.card_origin or '').lower():
            player.deck.pop(0)
            player.hand.append(top)
        else:
            # Place at bottom
            player.deck.pop(0)
            player.deck.append(top)
        return True
    return False


# =============================================================================
# CHOOSE EFFECTS - Cards with "choose one:" options
# =============================================================================

# --- ST11-003: Backlight ---
@register_effect("ST11-003", "MAIN", "Choose: Rest cost 5 or less OR KO rested cost 5 or less")
def backlight_choose_effect(game_state, player, card):
    """Choose: Rest OR KO rested character."""
    if player.leader and 'Uta' not in getattr(player.leader, 'name', ''):
        return False

    opponent = get_opponent(game_state, player)
    rested_targets = [c for c in opponent.cards_in_play
                     if c.is_resting and (getattr(c, 'cost', 0) or 0) <= 5]
    active_targets = [c for c in opponent.cards_in_play
                     if not c.is_resting and (getattr(c, 'cost', 0) or 0) <= 5]

    modes = []
    if active_targets:
        modes.append({"id": "rest", "label": "Rest cost 5 or less", "description": f"Rest 1 of {len(active_targets)} targets"})
    if rested_targets:
        modes.append({"id": "ko", "label": "KO rested cost 5 or less", "description": f"KO 1 of {len(rested_targets)} rested targets"})

    if modes:
        return create_mode_choice(
            game_state, player, modes, source_card=card,
            prompt="Choose Backlight effect"
        )
    return False


# --- ST11-001: Uta (Leader) ---
@register_effect("ST11-001", "on_attack", "[DON!! x1] [When Attacking] Reveal top, add FILM to hand")
def st11_001_uta_leader(game_state, player, card):
    """DON x1, When Attacking, Once Per Turn: Reveal top of deck, add FILM to hand, rest to bottom."""
    if getattr(card, 'attached_don', 0) >= 1:
        if hasattr(card, 'st11_001_used') and card.st11_001_used:
            return False
        if player.deck:
            revealed = player.deck.pop(0)
            types = (revealed.card_origin or '').lower()
            if 'film' in types:
                player.hand.append(revealed)
            else:
                player.deck.append(revealed)
            card.st11_001_used = True
            return True
    return False


# --- ST11-002: Uta ---
@register_effect("ST11-002", "blocker", "[Blocker]")
def st11_002_uta_blocker(game_state, player, card):
    """Blocker: Can redirect attacks."""
    card.is_blocker = True
    return True


@register_effect("ST11-002", "end_of_turn", "[End of Your Turn] Trash 1 Event: Set FILM Character as active")
def st11_002_uta_eot(game_state, player, card):
    """Trash 1 Event from hand: Set up to 1 FILM type Character as active."""
    events = [c for c in player.hand if getattr(c, 'card_type', '') == 'EVENT']
    if events:
        return create_hand_discard_choice(
            game_state, player, events,
            callback_action="uta_trash_event_then_set_active",
            source_card=card,
            prompt="Choose Event to trash (then set FILM Character active)"
        )
    return False


# --- ST11-004: New Genesis ---
@register_effect("ST11-004", "on_play", "[Main] If Uta leader, look at 3, add FILM (not self), set 1 DON active")
def st11_004_new_genesis(game_state, player, card):
    """[Main] If Uta leader, look at 3, add 1 FILM (not New Genesis), then set 1 DON active."""
    if not player.leader or 'uta' not in (player.leader.name or '').lower():
        return False
    # Set 1 DON active as part of the effect (happens regardless of search result)
    for i, state in enumerate(player.don_pool):
        if state == 'rested':
            player.don_pool[i] = 'active'
            break
    return search_top_cards(game_state, player, look_count=3, add_count=1,
        filter_fn=lambda c: ('film' in (c.card_origin or '').lower()
                             and 'new genesis' not in (c.name or '').lower()),
        source_card=card,
        prompt="New Genesis: Look at top 3, choose 1 FILM card (not New Genesis) to add to hand")
