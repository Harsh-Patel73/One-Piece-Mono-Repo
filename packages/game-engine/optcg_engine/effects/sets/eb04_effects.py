"""
Hardcoded effects for EB04 cards.
"""

from ..hardcoded import (
    create_bottom_deck_choice, draw_cards, get_characters_by_type, get_opponent,
    register_effect, search_top_cards, set_active, trash_from_hand,
)


# --- EB04-026: Bluegrass ---
@register_effect("EB04-026", "ON_PLAY", "Place opponent's cost 1 or less at bottom of deck")
def bluegrass_on_play(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 1]
    if targets:
        return create_bottom_deck_choice(game_state, player, targets, source_card=card,
                                          prompt="Choose opponent's cost 1 or less to place at bottom of deck")
    return False


@register_effect("EB04-026", "WHEN_ATTACKING", "Draw 1 card and trash 1")
def bluegrass_attack(game_state, player, card):
    draw_cards(player, 1)
    trash_from_hand(player, 1, game_state, card)
    return True


# --- EB04-013: Carrot ---
@register_effect("EB04-013", "ON_PLAY", "If Leader is Minks type, set 2 Minks chars and Leader active")
def carrot_effect(game_state, player, card):
    if player.leader and 'minks' in (player.leader.card_origin or '').lower():
        minks = get_characters_by_type(player, 'minks')[:2]
        set_active(minks)
        if player.leader:
            player.leader.is_resting = False
        return True
    return False


# --- EB04-012: Kikunojo ---
@register_effect("EB04-012", "MAIN", "If played this turn, set Land of Wano Leader active")
def kikunojo_effect(game_state, player, card):
    if getattr(card, 'played_this_turn', False):
        if player.leader and 'land of wano' in (player.leader.card_origin or '').lower():
            player.leader.is_resting = False
            return True
    return False


# --- EB04-011: Scaled Neptunian ---
@register_effect("EB04-011", "ON_PLAY", "Draw for each Neptunian char, trash same number")
def neptunian_effect(game_state, player, card):
    neptunian_count = len([c for c in player.cards_in_play
                          if 'neptunian' in (c.card_origin or '').lower()])
    if neptunian_count > 0:
        draw_cards(player, neptunian_count)
        trash_from_hand(player, neptunian_count)
        return True
    return False


# --- EB04-012: Kikunojo ---
@register_effect("EB04-012", "ACTIVATE_MAIN", "Set Land of Wano leader as active if played this turn")
def kikunojo_effect(game_state, player, card):
    if getattr(card, 'played_this_turn', False):
        leader = player.leader
        if leader and 'land of wano' in (leader.card_origin or '').lower():
            leader.is_resting = False
            return True
    return False


# --- EB04-029: I Heard the Sound...of a Lady's Teardrops Falling ---
@register_effect("EB04-029", "on_play", "[Main] If Sanji leader, look at 3, add Sanji or Event, trash rest")
def eb04_029_teardrops(game_state, player, card):
    """[Main] If Sanji leader, look at 3, add 1 [Sanji] or Event, trash rest."""
    if not player.leader or 'sanji' not in (player.leader.name or '').lower():
        return False
    return search_top_cards(game_state, player, look_count=3, add_count=1,
        filter_fn=lambda c: ('sanji' in (c.name or '').lower()
                             or c.card_type == 'EVENT'),
        source_card=card, trash_rest=True,
        prompt="Look at top 3: choose 1 [Sanji] or Event card to add to hand (rest trashed)")


# --- EB04-037: Porche ---
@register_effect("EB04-037", "on_play", "[On Play] If Foxy leader, look at 5, add Foxy Pirates")
def eb04_037_porche(game_state, player, card):
    """[On Play] If Foxy Pirates leader, look at 5, add 1 Foxy Pirates card."""
    leader_type = (player.leader.card_origin or '').lower() if player.leader else ''
    if 'foxy pirates' not in leader_type:
        return False
    return search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: 'foxy pirates' in (c.card_origin or '').lower(),
        source_card=card,
        prompt="Porche: Look at top 5, choose 1 Foxy Pirates card to add to hand")
