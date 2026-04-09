"""
Hardcoded effects for ST22 cards.
"""

from ..hardcoded import (
    create_mode_choice, create_play_from_hand_choice, create_power_effect_choice, draw_cards,
    get_opponent, register_effect, search_top_cards, trash_from_hand,
)


# --- ST22-001: Ace & Newgate (Leader) ---
@register_effect("ST22-001", "activate", "[Activate: Main] Reveal WB Pirates: draw 1, put revealed on top")
def st22_001_ace_newgate_leader(game_state, player, card):
    """Once Per Turn: Reveal a Whitebeard Pirates card from hand, draw 1, put revealed on top of deck."""
    if hasattr(card, 'st22_001_used') and card.st22_001_used:
        return False
    wb_cards = [c for c in player.hand
                if 'whitebeard pirates' in (c.card_origin or '').lower()]
    if wb_cards:
        revealed = wb_cards[0]
        draw_cards(player, 1)
        player.hand.remove(revealed)
        player.deck.insert(0, revealed)
        card.st22_001_used = True
        return True
    return False


# --- ST22-002: Izo ---
@register_effect("ST22-002", "on_play", "[On Play] Look at 5, reveal Whitebeard Pirates card to hand")
def st22_002_izo_play(game_state, player, card):
    """On Play: Look at top 5, reveal a Whitebeard Pirates card (not Izo) to hand, rest to bottom."""
    def wb_filter(c):
        traits = (c.card_origin or '').lower()
        return ('whitebeard pirates' in traits
                and 'izo' not in (c.name or '').lower())
    return search_top_cards(game_state, player, 5, add_count=1, filter_fn=wb_filter,
                            source_card=card,
                            prompt="Look at top 5 cards. Choose a Whitebeard Pirates card to add to hand.")


# --- ST22-003: Edward.Newgate ---
@register_effect("ST22-003", "double_attack", "[Double Attack]")
def st22_003_newgate_double(game_state, player, card):
    """Double Attack: Deals 2 damage."""
    card.has_double_attack = True
    return True


@register_effect("ST22-003", "on_play", "[On Play] If 2- life, draw 2, K.O. this at end of turn")
def st22_003_newgate_play(game_state, player, card):
    """On Play: If you have 2 or less life, draw 2 cards but K.O. this at end of turn."""
    if len(player.life_cards) <= 2:
        draw_cards(player, 2)
        card.ko_at_end_of_turn = True
        return True
    return False


# --- ST22-005: Kouzuki Oden ---
@register_effect("ST22-005", "continuous", "Cannot be removed except by battle")
def st22_005_oden(game_state, player, card):
    """If this Character would be removed from the field by an effect, it isn't."""
    card.cannot_be_removed_by_effect = True
    return True


# --- ST22-006: Jozu ---
@register_effect("ST22-006", "on_play", "[On Play] Reveal top, if WB Pirates add to hand")
def st22_006_jozu(game_state, player, card):
    """On Play: Reveal top card, if Whitebeard Pirates add to hand."""
    if player.deck:
        top = player.deck[0]
        if 'whitebeard pirates' in (top.card_origin or '').lower():
            player.deck.remove(top)
            player.hand.append(top)
        return True
    return False


# --- ST22-007: Squard ---
@register_effect("ST22-007", "activate", "[Activate: Main] Reveal top, if WB draw 1 trash 1")
def st22_007_squard(game_state, player, card):
    """Once Per Turn: Reveal top card, if Whitebeard Pirates draw 1 and trash 1."""
    if hasattr(card, 'st22_007_used') and card.st22_007_used:
        return False
    if player.deck:
        top = player.deck[0]
        if 'whitebeard pirates' in (top.card_origin or '').lower():
            draw_cards(player, 1)
            if player.hand:
                trash_from_hand(player, 1, game_state, card)
        card.st22_007_used = True
        return True
    return False


# --- ST22-009: Vista ---
@register_effect("ST22-009", "blocker", "[Blocker]")
def st22_009_vista(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


# --- ST22-011: Whitey Bay ---
@register_effect("ST22-011", "on_play", "[On Play] Reveal 2 WB Pirates from hand to rest DON")
def st22_011_whitey_bay(game_state, player, card):
    """Your Turn, On Play: Reveal 2 WB Pirates from hand, rest up to 1 of opponent's active DON."""
    wb_cards = [c for c in player.hand
                if 'whitebeard pirates' in (c.card_origin or '').lower()
                and c != card]
    if len(wb_cards) >= 2:
        opponent = get_opponent(game_state, player)
        active_don = opponent.don_pool.count("active")
        if active_don:
            active_don[0].is_resting = True
        return True
    return False


# --- ST22-012: Marco ---
@register_effect("ST22-012", "continuous", "[Once Per Turn] Would be KO'd, return to hand instead")
def st22_012_marco(game_state, player, card):
    """Once Per Turn: If this Character would be K.O.'d, return to hand instead."""
    if not getattr(card, 'st22_012_used', False):
        card.ko_returns_to_hand = True
    return True


# --- ST22-015: I Am Whitebeard!! ---
@register_effect("ST22-015", "main", "[Main] If WB Leader, play Edward.Newgate from hand, life to hand, +2000")
def st22_015_i_am_whitebeard(game_state, player, card):
    """Main: If WB Leader, play Edward.Newgate from hand. Then add life to hand for +2000 to Leader."""
    if player.leader and 'whitebeard pirates' in (player.leader.card_origin or '').lower():
        # Step 1: Find Edward.Newgate cards in hand
        newgate_cards = [c for c in player.hand
                         if 'edward' in (getattr(c, 'name', '') or '').lower()
                         and 'newgate' in (getattr(c, 'name', '') or '').lower()
                         and getattr(c, 'card_type', '') == 'CHARACTER']
        if newgate_cards:
            # Play Edward.Newgate from hand
            return create_play_from_hand_choice(game_state, player, newgate_cards,
                                                source_card=card,
                                                prompt="Choose an Edward.Newgate to play from hand")
        # Step 2: Even without Newgate, offer life choice
        if player.life_cards:
            def callback(selected: list[str]) -> None:
                selected_mode = selected[0] if selected else None
                if selected_mode == "top_life" and player.life_cards:
                    life_card = player.life_cards.pop(0)
                    player.hand.append(life_card)
                    game_state._log(f"{player.name} added top life card to hand")
                    if player.leader:
                        player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 2000
                        game_state._log(f"{player.leader.name} gains +2000 power until end of opponent's next turn")
                elif selected_mode == "bottom_life" and player.life_cards:
                    life_card = player.life_cards.pop()
                    player.hand.append(life_card)
                    game_state._log(f"{player.name} added bottom life card to hand")
                    if player.leader:
                        player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 2000
                        game_state._log(f"{player.leader.name} gains +2000 power until end of opponent's next turn")
                elif selected_mode == "skip":
                    game_state._log(f"{player.name} chose not to add a life card to hand")

            return create_mode_choice(game_state, player, [
                {"id": "top_life", "label": "Take Top Life", "description": "Add top life card to hand, Leader gains +2000"},
                {"id": "bottom_life", "label": "Take Bottom Life", "description": "Add bottom life card to hand, Leader gains +2000"},
                {"id": "skip", "label": "Don't Take Life", "description": "Skip the life effect"}
            ], source_card=card, callback=callback, prompt="Add a Life card to hand? (Leader gains +2000 if you do)")
    return False


# --- ST22-016: Take That Back!! ---
@register_effect("ST22-016", "counter", "[Counter] Reveal top, +X000 power where X is cost")
def st22_016_take_that_back(game_state, player, card):
    """Counter: Reveal top card, give your Leader or Character +X000 power where X is its cost."""
    if player.deck:
        top = player.deck[0]
        cost = getattr(top, 'cost', 0) or 0
        power_boost = cost * 1000
        # Apply to battling character
        if game_state.pending_attack and game_state.pending_attack.get('target'):
            target_idx = game_state.pending_attack['target']
            if target_idx == -1 and player.leader:
                player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + power_boost
            elif 0 <= target_idx < len(player.cards_in_play):
                player.cards_in_play[target_idx].power_modifier = getattr(player.cards_in_play[target_idx], 'power_modifier', 0) + power_boost
        return True
    return False


# --- ST22-017: Fire Fist ---
@register_effect("ST22-017", "main", "[Main] Reveal 2 WB cards, give opponent's char -5000 power")
def st22_017_fire_fist(game_state, player, card):
    """Reveal 2 Whitebeard Pirates cards from hand, give opponent's Character -5000 power this turn."""
    wb_cards = [c for c in player.hand
                if 'whitebeard pirates' in (c.card_origin or '').lower()
                and c != card]
    if len(wb_cards) >= 2:
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            return create_power_effect_choice(game_state, player, opponent.cards_in_play,
                                              -5000, source_card=card,
                                              prompt="Choose opponent's Character to give -5000 power")
    return False

