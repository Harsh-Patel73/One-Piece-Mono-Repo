"""
Hardcoded effects for OP02 cards.
"""

import random

from ..hardcoded import (
    add_don_from_deck, create_add_from_trash_choice, create_bottom_deck_choice, create_cost_reduction_choice,
    create_dual_target_choice, create_hand_discard_choice, create_ko_choice, create_multi_target_choice,
    create_play_from_hand_choice, create_power_effect_choice, create_rest_choice,
    create_return_to_hand_choice, create_set_active_choice,
    create_target_choice, draw_cards, get_opponent, register_effect,
    search_top_cards, trash_from_hand,
)


# --- OP02-005: Curly.Dadan ---
@register_effect("OP02-005", "ON_PLAY", "Look at 5, reveal cost 1 red char, add to hand")
def curly_dadan_effect(game_state, player, card):
    def is_red_cost_1_char(c):
        colors = getattr(c, 'colors', '') or ''
        cost = getattr(c, 'cost', 0) or 0
        card_type = getattr(c, 'card_type', '')
        return 'red' in colors.lower() and cost == 1 and card_type == 'CHARACTER'

    return search_top_cards(
        game_state, player,
        look_count=5,
        add_count=1,
        filter_fn=is_red_cost_1_char,
        source_card=card,
        prompt="Look at top 5 cards. Choose 1 red cost 1 Character to add to hand."
    )


# --- OP02-056: Donquixote Doflamingo ---
@register_effect("OP02-056", "ON_PLAY", "Look at 3, place at top or bottom in any order")
def doflamingo_op02_on_play(game_state, player, card):
    # Just deck manipulation - AI places all at bottom
    return True


@register_effect("OP02-056", "WHEN_ATTACKING", "Trash 1: Place opponent's cost 1 or less at bottom")
def doflamingo_op02_attack(game_state, player, card):
    if player.hand:
        trash_from_hand(player, 1, game_state, card)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 1]
        if targets:
            return create_bottom_deck_choice(game_state, player, targets, source_card=card,
                                              prompt="Choose opponent's cost 1 or less to place at bottom of deck")
    return False


# --- OP02-030: Kouzuki Oden ---
@register_effect("OP02-030", "MAIN", "Rest 3 DON: Set this char active")
def oden_main(game_state, player, card):
    active_don = [d for d in player.don_pool if not d.is_resting]
    if len(active_don) >= 3:
        for don in active_don[:3]:
            don.is_resting = True
        card.is_resting = False
        return True
    return False


@register_effect("OP02-030", "ON_KO", "Play green Land of Wano cost 3 from deck")
def oden_ko(game_state, player, card):
    for i, deck_card in enumerate(player.deck):
        if ('green' in (getattr(deck_card, 'colors', '') or '').lower()
            and 'land of wano' in (deck_card.card_origin or '').lower()
            and (getattr(deck_card, 'cost', 0) or 0) == 3
            and getattr(deck_card, 'card_type', '') == 'CHARACTER'):
            char = player.deck.pop(i)
            player.cards_in_play.append(char)
            random.shuffle(player.deck)
            return True
    return False


# --- OP02-032: Shishilian ---
@register_effect("OP02-032", "ON_PLAY", "Rest 2 DON: Set Minks cost 5 or less active")
def shishilian_effect(game_state, player, card):
    active_don = [d for d in player.don_pool if not d.is_resting]
    if len(active_don) >= 2:
        for don in active_don[:2]:
            don.is_resting = True
        minks = [c for c in player.cards_in_play
                if 'minks' in (c.card_origin or '').lower()
                and (getattr(c, 'cost', 0) or 0) <= 5
                and c.is_resting]
        if minks:
            minks[0].is_resting = False
            return True
    return False


# --- OP02-101: Strawberry ---
@register_effect("OP02-101", "WHEN_ATTACKING", "If cost 0 char exists, opponent can't use Blocker cost 5 or less")
def strawberry_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    has_cost_0 = any((getattr(c, 'cost', 0) or 0) == 0 for c in opponent.cards_in_play)
    if has_cost_0:
        for c in opponent.cards_in_play:
            if (getattr(c, 'cost', 0) or 0) <= 5:
                c.blocker_disabled_this_battle = True
        return True
    return False


# --- OP02-066: Impel Down All Stars ---
@register_effect("OP02-066", "MAIN", "Trash 2 from hand: If Impel Down Leader, draw 2")
def impel_down_all_stars_effect(game_state, player, card):
    """Trash 2 cards from hand, if Leader has Impel Down type, draw 2."""
    if len(player.hand) >= 2:
        trash_from_hand(player, 2, game_state, card)
        if player.leader and 'impel down' in (player.leader.card_origin or '').lower():
            draw_cards(player, 2)
            return True
    return False


# --- OP02-023: You May Be a Fool...but I Still Love You ---
@register_effect("OP02-023", "MAIN", "If 3 or less Life, can't add Life to hand this turn")
def you_may_be_a_fool_effect(game_state, player, card):
    """If you have 3 or less Life, you cannot add Life to hand using your effects."""
    if len(player.life_cards) <= 3:
        player.cannot_add_life_to_hand_this_turn = True
        return True
    return False


# --- OP02-085: Kaido ---
@register_effect("OP02-085", "YOUR_TURN", "If opponent has 1 or less life, +1000 power")
def op02_085_kaido(game_state, player, card):
    opponent = get_opponent(game_state, player)
    if check_life_count(opponent, 1, 'le'):
        add_power_modifier(card, 1000)
    return True


# --- OP02-018: Marco (Whitebeard Pirates) ---
@register_effect("OP02-018", "ON_KO", "If 2 or less life, trash WB card to return this to play rested")
def op02_018_marco(game_state, player, card):
    """On KO: If 2 or less life, trash WB card from hand to return this to play rested."""
    if check_life_count(player, 2):
        wb_cards = [c for c in player.hand
                    if 'whitebeard pirates' in (c.card_origin or '').lower()]
        if wb_cards:
            trash_card = wb_cards[0]
            player.hand.remove(trash_card)
            player.trash.append(trash_card)
            # Return Marco to play rested
            if card in player.trash:
                player.trash.remove(card)
            card.is_resting = True
            player.cards_in_play.append(card)
            return True
    return False


# --- OP02-024: Moby Dick ---
@register_effect("OP02-024", "CONTINUOUS", "If 1 or less life, WB chars gain +2000 power")
def op02_024_moby_dick(game_state, player, card):
    """Continuous: If 1 or less life, Whitebeard characters gain +2000 power."""
    if check_life_count(player, 1):
        if player.leader and 'Edward.Newgate' in getattr(player.leader, 'name', ''):
            add_power_modifier(player.leader, 2000)
        for c in player.cards_in_play:
            if 'whitebeard pirates' in (c.card_origin or '').lower():
                add_power_modifier(c, 2000)
        return True
    return False


# =============================================================================
# LEADER CARD EFFECTS - OP02 (Paramount War)
# =============================================================================

# --- OP02-001: Edward.Newgate (Leader) ---
@register_effect("OP02-001", "end_of_turn", "[End of Your Turn] Add 1 Life to hand")
def op02_001_whitebeard_leader(game_state, player, card):
    """End of Your Turn: Add 1 card from the top of your Life cards to your hand."""
    if player.life_cards:
        life = player.life_cards.pop()
        player.hand.append(life)
        return True
    return False


# --- OP02-002: Monkey.D.Garp (Leader) ---
@register_effect("OP02-002", "on_don_attached", "[Your Turn] When DON given, opponent char cost 7- gets -1 cost")
def op02_002_garp_leader(game_state, player, card):
    """Your Turn: When this Leader or a Character is given DON, opponent's cost 7 or less char gets -1 cost."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 7]
    if targets:
        return create_cost_reduction_choice(game_state, player, targets, -1, source_card=card,
                                           prompt="Choose opponent's cost 7 or less Character to give -1 cost")
    return False


# --- OP02-025: Kin'emon (Leader) ---
@register_effect("OP02-025", "activate", "[Activate: Main] If 1- chars, next Land of Wano cost 3+ costs -1")
def op02_025_kinemon_leader(game_state, player, card):
    """Once Per Turn: If 1 or less Characters, next Land of Wano cost 3+ from hand costs -1."""
    if hasattr(card, 'op02_025_used') and card.op02_025_used:
        return False
    if len(player.cards_in_play) <= 1:
        player.next_wano_discount = True
        card.op02_025_used = True
        return True
    return False


# --- OP02-026: Sanji (Leader) ---
@register_effect("OP02-026", "on_play_character", "[Once Per Turn] When play no-effect char, if 3- chars, set 2 DON active")
def op02_026_sanji_leader(game_state, player, card):
    """Once Per Turn: When you play a Character with no base effect, if 3 or less Characters, set 2 DON active."""
    if hasattr(card, 'op02_026_used') and card.op02_026_used:
        return False
    if len(player.cards_in_play) <= 3:
        rested_don = player.don_pool.count("rested")
        for don in rested_don[:2]:
            don.is_resting = False
        card.op02_026_used = True
        return True
    return False


# --- OP02-049: Emporio.Ivankov (Leader) ---
@register_effect("OP02-049", "end_of_turn", "[End of Your Turn] If 0 hand, draw 2")
def op02_049_ivankov_leader(game_state, player, card):
    """End of Your Turn: If you have 0 cards in hand, draw 2 cards."""
    if len(player.hand) == 0:
        draw_cards(player, 2)
        return True
    return False


# --- OP02-071: Magellan (Leader) ---
@register_effect("OP02-071", "on_don_return", "[Your Turn] When DON returned to deck, +1000 power")
def op02_071_magellan_leader(game_state, player, card):
    """Your Turn, Once Per Turn: When a DON is returned to DON deck, this Leader gains +1000 power."""
    if hasattr(card, 'op02_071_used') and card.op02_071_used:
        return False
    card.power_modifier = getattr(card, 'power_modifier', 0) + 1000
    card.op02_071_used = True
    return True


# --- OP02-072: Zephyr (Leader) ---
@register_effect("OP02-072", "on_attack", "[When Attacking] DON -4: K.O. cost 3 or less, +1000 power")
def op02_072_zephyr_leader(game_state, player, card):
    """When Attacking, DON -4: K.O. opponent's cost 3 or less Character, Leader +1000 power."""
    if len(player.don_pool) >= 4:
        for _ in range(4):
            if player.don_pool:
                don = player.don_pool.pop()
                if hasattr(player, 'don_deck'):
                    player.don_deck.append(don)
        card.power_modifier = getattr(card, 'power_modifier', 0) + 1000
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
        if targets:
            return create_ko_choice(
                game_state, player, targets, source_card=card,
                prompt="Choose opponent's cost 3 or less Character to KO"
            )
        return True
    return False


# --- OP02-093: Smoker (Leader) ---
@register_effect("OP02-093", "activate", "[DON!! x1] Give opponent char -1 cost, if cost 0 exists +1000")
def op02_093_smoker_leader(game_state, player, card):
    """DON x1, Once Per Turn: Give opponent's char -1 cost. If any cost 0 exists, Leader +1000."""
    if getattr(card, 'attached_don', 0) >= 1:
        if hasattr(card, 'op02_093_used') and card.op02_093_used:
            return False
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            card.op02_093_used = True
            return create_cost_reduction_choice(
                game_state, player, opponent.cards_in_play, -1,
                source_card=card,
                prompt="Choose opponent's Character to give -1 cost"
            )
        card.op02_093_used = True
        return True
    return False


# =============================================================================
# OP02 CHARACTER EFFECTS
# =============================================================================

# --- OP02-004: Edward.Newgate ---
@register_effect("OP02-004", "on_play", "[On Play] Leader +2000 power until next turn, cannot add Life this turn")
def op02_004_newgate_play(game_state, player, card):
    """On Play: Leader gains +2000 power until next turn. Cannot add Life cards this turn."""
    if player.leader:
        player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 2000
    player.cannot_add_life = True
    return True


@register_effect("OP02-004", "on_attack", "[DON!! x2] K.O. opponent's 3000 power or less Character")
def op02_004_newgate_attack(game_state, player, card):
    """DON x2: K.O. up to 1 of opponent's Characters with 3000 power or less."""
    if getattr(card, 'attached_don', 0) >= 2:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play
                   if (getattr(c, 'power', 0) or 0) + getattr(c, 'power_modifier', 0) <= 3000]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's 3000 power or less to KO")
        return True
    return False


# --- OP02-005: Curly.Dadan ---
@register_effect("OP02-005", "on_play", "[On Play] Look at 5, reveal red cost 1 Character, add to hand")
def op02_005_dadan(game_state, player, card):
    """On Play: Look at top 5, reveal up to 1 red cost 1 Character to hand."""
    def filter_fn(c):
        return (getattr(c, 'card_type', '') == 'CHARACTER'
                and 'Red' in (getattr(c, 'colors', None) or [])
                and (getattr(c, 'cost', 0) or 0) == 1)
    search_top_cards(game_state, player, 5, add_count=1, filter_fn=filter_fn,
                     source_card=card,
                     prompt="Look at top 5. Choose a red cost 1 Character to add to hand.")
    return True


# --- OP02-008: Jozu ---
@register_effect("OP02-008", "continuous", "[DON!! x1] If 2 or less Life and Whitebeard Pirates Leader, gain Rush")
def op02_008_jozu(game_state, player, card):
    """DON x1: If 2 or less Life and Leader is Whitebeard Pirates, gain Rush."""
    if getattr(card, 'attached_don', 0) >= 1:
        if len(player.life_cards) <= 2:
            if player.leader and 'Whitebeard Pirates' in (player.leader.card_origin or ''):
                card.has_rush = True
    return True


# --- OP02-009: Squard ---
@register_effect("OP02-009", "on_play", "[On Play] If Whitebeard Pirates Leader, -4000 to opponent + add Life to hand")
def op02_009_squard(game_state, player, card):
    """On Play: If Leader is Whitebeard Pirates, give -4000 to opponent's Character and add 1 Life to hand."""
    if player.leader and 'Whitebeard Pirates' in (player.leader.card_origin or ''):
        # Add Life to hand first
        if player.life_cards:
            life_card = player.life_cards.pop()
            player.hand.append(life_card)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if c]
        if targets:
            return create_power_effect_choice(game_state, player, targets, -4000, source_card=card,
                                             prompt="Choose opponent's Character to give -4000 power")
    return True


# --- OP02-010: Dogura ---
@register_effect("OP02-010", "activate", "[Activate: Main] Rest: Play red cost 1 Character from hand")
def op02_010_dogura(game_state, player, card):
    """Activate: Rest this Character to play a red cost 1 Character from hand."""
    if not getattr(card, 'is_resting', False):
        card.is_resting = True
        playable = [c for c in player.hand
                    if (getattr(c, 'card_type', '') == 'CHARACTER' and
                        'Red' in getattr(c, 'colors', []) and
                        (getattr(c, 'cost', 0) or 0) == 1 and
                        getattr(c, 'name', '') != 'Dogura')]
        if playable:
            return create_play_from_hand_choice(
                game_state, player, playable,
                source_card=card,
                prompt="Choose red cost 1 Character to play"
            )
        return True
    return False


# --- OP02-011: Vista ---
@register_effect("OP02-011", "on_play", "[On Play] K.O. opponent's 3000 power or less Character")
def op02_011_vista(game_state, player, card):
    """On Play: K.O. up to 1 of opponent's Characters with 3000 power or less."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if (getattr(c, 'power', 0) or 0) + getattr(c, 'power_modifier', 0) <= 3000]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                               prompt="Choose opponent's 3000 power or less to KO")
    return True


# --- OP02-012: Blenheim ---
@register_effect("OP02-012", "blocker", "[Blocker]")
def op02_012_blenheim(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


# --- OP02-013: Portgas.D.Ace ---
@register_effect("OP02-013", "on_play", "[On Play] Give -3000 to 2 opponent Characters, Rush if Whitebeard Pirates Leader")
def op02_013_ace(game_state, player, card):
    """On Play: Give -3000 power to up to 2 opponent Characters. Rush if Leader is Whitebeard Pirates."""
    if player.leader and 'Whitebeard Pirates' in (player.leader.card_origin or ''):
        card.has_rush = True
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if c]
    if targets:
        return create_multi_target_choice(
            game_state, player, targets, count=min(2, len(targets)),
            callback_action="give_minus_3000_power",
            source_card=card,
            prompt="Choose up to 2 opponent Characters to give -3000 power"
        )
    return True


# --- OP02-014: Whitey Bay ---
@register_effect("OP02-014", "continuous", "[DON!! x1] Can attack active Characters")
def op02_014_whitey_bay(game_state, player, card):
    """DON x1: Can attack opponent's active Characters."""
    if getattr(card, 'attached_don', 0) >= 1:
        card.can_attack_active = True
    return True


# --- OP02-015: Makino ---
@register_effect("OP02-015", "activate", "[Activate: Main] Rest: Red cost 1 Character gains +3000")
def op02_015_makino(game_state, player, card):
    """Activate: Rest to give red cost 1 Character +3000 power."""
    if not getattr(card, 'is_resting', False):
        card.is_resting = True
        targets = [c for c in player.cards_in_play
                   if 'Red' in getattr(c, 'colors', []) and (getattr(c, 'cost', 0) or 0) == 1]
        if targets:
            return create_power_effect_choice(game_state, player, targets, 3000, source_card=card,
                                             prompt="Choose red cost 1 Character to give +3000 power")
        return True
    return False


# --- OP02-016: Magura ---
@register_effect("OP02-016", "on_play", "[On Play] Red cost 1 Character gains +3000")
def op02_016_magura(game_state, player, card):
    """On Play: Red cost 1 Character gains +3000 power."""
    targets = [c for c in player.cards_in_play
               if 'Red' in getattr(c, 'colors', []) and (getattr(c, 'cost', 0) or 0) == 1]
    if targets:
        return create_power_effect_choice(game_state, player, targets, 3000, source_card=card,
                                         prompt="Choose red cost 1 Character to give +3000 power")
    return True


# --- OP02-017: Masked Deuce ---
@register_effect("OP02-017", "on_attack", "[DON!! x2] K.O. opponent's 2000 power or less Character")
def op02_017_masked_deuce(game_state, player, card):
    """DON x2: K.O. up to 1 of opponent's Characters with 2000 power or less."""
    if getattr(card, 'attached_don', 0) >= 2:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play
                   if (getattr(c, 'power', 0) or 0) + getattr(c, 'power_modifier', 0) <= 2000]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's 2000 power or less to KO")
        return True
    return False


# --- OP02-018: Marco ---
@register_effect("OP02-018", "blocker", "[Blocker]")
def op02_018_marco_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP02-018", "on_ko", "[On K.O.] Trash Whitebeard Pirates card: If 2 or less Life, play from trash rested")
def op02_018_marco_ko(game_state, player, card):
    """On K.O.: Trash a Whitebeard Pirates card from hand to play this from trash if 2 or less Life."""
    if len(player.life_cards) <= 2:
        for hand_card in player.hand:
            if 'Whitebeard Pirates' in (hand_card.card_origin or ''):
                player.hand.remove(hand_card)
                player.trash.append(hand_card)
                if card in player.trash:
                    player.trash.remove(card)
                    player.cards_in_play.append(card)
                    card.is_resting = True
                return True
    return False


# --- OP02-019: Rakuyo ---
@register_effect("OP02-019", "continuous", "[DON!! x1] [Your Turn] All Whitebeard Pirates Characters gain +1000")
def op02_019_rakuyo(game_state, player, card):
    """DON x1: During your turn, all Whitebeard Pirates Characters gain +1000."""
    if getattr(card, 'attached_don', 0) >= 1:
        for c in player.cards_in_play:
            if 'Whitebeard Pirates' in (c.card_origin or ''):
                c.power_modifier = getattr(c, 'power_modifier', 0) + 1000
    return True


# --- OP02-027: Inuarashi ---
@register_effect("OP02-027", "continuous", "If all DON rested, cannot be removed by opponent's effects")
def op02_027_inuarashi(game_state, player, card):
    """If all DON cards are rested, cannot be removed by opponent's effects."""
    if player.don_pool:
        all_rested = all(getattr(d, 'is_resting', False) for d in player.don_pool)
        if all_rested:
            card.cannot_be_removed = True
    return True


# --- OP02-029: Carrot ---
@register_effect("OP02-029", "end_of_turn", "[End of Your Turn] Set 1 DON as active")
def op02_029_carrot(game_state, player, card):
    """End of Turn: Set up to 1 DON as active."""
    for don in player.don_pool:
        if getattr(don, 'is_resting', False):
            don.is_resting = False
            break
    return True


# --- OP02-030: Kouzuki Oden ---
@register_effect("OP02-030", "activate", "[Activate: Main] [Once Per Turn] Rest 3 DON: Set this active")
def op02_030_oden_activate(game_state, player, card):
    """Activate: Rest 3 DON to set this Character as active."""
    if getattr(card, 'op02_030_used', False):
        return False
    active_don = player.don_pool.count("active")
    if len(active_don) >= 3:
        for i in range(3):
            active_don[i].is_resting = True
        card.is_resting = False
        card.op02_030_used = True
        return True
    return False


@register_effect("OP02-030", "on_ko", "[On K.O.] Play green Land of Wano cost 3 Character from deck")
def op02_030_oden_ko(game_state, player, card):
    """On K.O.: Play a green Land of Wano cost 3 Character from deck."""
    for deck_card in player.deck:
        if (getattr(deck_card, 'card_type', '') == 'CHARACTER' and
            'Green' in getattr(deck_card, 'colors', []) and
            'Land of Wano' in (deck_card.card_origin or '') and
            (getattr(deck_card, 'cost', 0) or 0) == 3):
            player.deck.remove(deck_card)
            player.cards_in_play.append(deck_card)
            break
    return True


# --- OP02-031: Kouzuki Toki ---
@register_effect("OP02-031", "continuous", "If you have Kouzuki Oden Character, gain Blocker")
def op02_031_toki(game_state, player, card):
    """If you have a Kouzuki Oden Character, gain Blocker."""
    for c in player.cards_in_play:
        if getattr(c, 'name', '') == 'Kouzuki Oden':
            card.has_blocker = True
            return True
    return False


# --- OP02-032: Shishilian ---
@register_effect("OP02-032", "on_play", "[On Play] Rest 2 DON: Set Minks cost 5 or less as active")
def op02_032_shishilian(game_state, player, card):
    """On Play: Rest 2 DON to set a Minks cost 5 or less Character as active."""
    active_don = player.don_pool.count("active")
    if len(active_don) >= 2:
        for i in range(2):
            active_don[i].is_resting = True
        targets = [c for c in player.cards_in_play
                   if 'Minks' in (c.card_origin or '') and
                   (getattr(c, 'cost', 0) or 0) <= 5 and
                   getattr(c, 'is_resting', False)]
        if targets:
            return create_set_active_choice(game_state, player, targets, source_card=card,
                                           prompt="Choose Minks cost 5 or less to set active")
        return True
    return False


# --- OP02-034: Tony Tony.Chopper ---
@register_effect("OP02-034", "on_attack", "[DON!! x1] Rest opponent's cost 2 or less Character")
def op02_034_chopper(game_state, player, card):
    """DON x1: Rest up to 1 of opponent's Characters with cost 2 or less."""
    if getattr(card, 'attached_don', 0) >= 1:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play
                   if (getattr(c, 'cost', 0) or 0) <= 2 and not getattr(c, 'is_resting', False)]
        if targets:
            return create_rest_choice(game_state, player, targets, source_card=card,
                                     prompt="Choose opponent's cost 2 or less to rest")
        return True
    return False


# --- OP02-035: Trafalgar Law ---
@register_effect("OP02-035", "activate", "[Activate: Main] Rest 1 DON, return to hand: Play cost 3 from hand")
def op02_035_law(game_state, player, card):
    """Activate: Rest 1 DON and return this to hand to play a cost 3 Character from hand."""
    active_don = player.don_pool.count("active")
    if active_don:
        active_don[0].is_resting = True
        if card in player.cards_in_play:
            player.cards_in_play.remove(card)
            player.hand.append(card)
        playable = [c for c in player.hand
                    if (getattr(c, 'card_type', '') == 'CHARACTER' and
                        (getattr(c, 'cost', 0) or 0) == 3 and c != card)]
        if playable:
            return create_play_from_hand_choice(
                game_state, player, playable,
                source_card=card,
                prompt="Choose cost 3 Character to play"
            )
    return False


# --- OP02-036: Nami ---
@register_effect("OP02-036", "on_play", "[On Play] Rest 1 DON: Look at 3, reveal FILM card to hand")
def op02_036_nami(game_state, player, card):
    """On Play: Rest 1 DON to look at top 3 cards, reveal a FILM card to hand."""
    active_don = player.don_pool.count("active")
    if active_don:
        active_don[0].is_resting = True
        def filter_fn(c):
            return ('FILM' in (c.card_origin or '')
                    and getattr(c, 'name', '') != 'Nami')
        search_top_cards(game_state, player, 3, add_count=1, filter_fn=filter_fn,
                         source_card=card,
                         prompt="Look at top 3. Choose a FILM card to add to hand.")
    return True


# --- OP02-037: Nico Robin ---
@register_effect("OP02-037", "on_play", "[On Play] Play FILM/Straw Hat Crew cost 2 or less from hand")
def op02_037_robin(game_state, player, card):
    """On Play: Play a FILM or Straw Hat Crew cost 2 or less Character from hand."""
    playable = [c for c in player.hand
                if (getattr(c, 'card_type', '') == 'CHARACTER' and
                    (getattr(c, 'cost', 0) or 0) <= 2 and
                    ('FILM' in (c.card_origin or '') or 'Straw Hat Crew' in (c.card_origin or '')))]
    if playable:
        return create_play_from_hand_choice(
            game_state, player, playable,
            source_card=card,
            prompt="Choose FILM/Straw Hat Crew cost 2 or less to play"
        )
    return True


# --- OP02-038: Nekomamushi ---
@register_effect("OP02-038", "blocker", "[Blocker]")
def op02_038_nekomamushi(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


# --- OP02-040: Brook ---
@register_effect("OP02-040", "on_play", "[On Play] Play FILM/Straw Hat Crew cost 3 or less from hand")
def op02_040_brook(game_state, player, card):
    """On Play: Play a FILM or Straw Hat Crew cost 3 or less Character from hand."""
    playable = [c for c in player.hand
                if (getattr(c, 'card_type', '') == 'CHARACTER' and
                    (getattr(c, 'cost', 0) or 0) <= 3 and
                    ('FILM' in (c.card_origin or '') or 'Straw Hat Crew' in (c.card_origin or '')))]
    if playable:
        return create_play_from_hand_choice(
            game_state, player, playable,
            source_card=card,
            prompt="Choose FILM/Straw Hat Crew cost 3 or less to play"
        )
    return True


# --- OP02-041: Monkey.D.Luffy ---
@register_effect("OP02-041", "blocker", "[Blocker]")
def op02_041_luffy_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP02-041", "on_play", "[On Play] Play FILM/Straw Hat Crew cost 4 or less from hand")
def op02_041_luffy_play(game_state, player, card):
    """On Play: Play a FILM or Straw Hat Crew cost 4 or less Character from hand."""
    playable = [c for c in player.hand
                if (getattr(c, 'card_type', '') == 'CHARACTER' and
                    (getattr(c, 'cost', 0) or 0) <= 4 and
                    ('FILM' in (c.card_origin or '') or 'Straw Hat Crew' in (c.card_origin or '')))]
    if playable:
        return create_play_from_hand_choice(
            game_state, player, playable,
            source_card=card,
            prompt="Choose FILM/Straw Hat Crew cost 4 or less to play"
        )
    return True


# --- OP02-042: Yamato ---
@register_effect("OP02-042", "on_play", "[On Play] Rest opponent's cost 6 or less Character")
def op02_042_yamato(game_state, player, card):
    """On Play: Rest up to 1 of opponent's Characters with cost 6 or less."""
    card.alt_name = 'Kouzuki Oden'
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if (getattr(c, 'cost', 0) or 0) <= 6 and not getattr(c, 'is_resting', False)]
    if targets:
        return create_rest_choice(game_state, player, targets, source_card=card,
                                 prompt="Choose opponent's cost 6 or less to rest")
    return True


# --- OP02-044: Wanda ---
@register_effect("OP02-044", "on_play", "[On Play] Play Minks cost 3 or less from hand")
def op02_044_wanda(game_state, player, card):
    """On Play: Play a Minks cost 3 or less Character from hand."""
    for hand_card in player.hand:
        if (getattr(hand_card, 'card_type', '') == 'CHARACTER' and
            'Minks' in (hand_card.card_origin or '') and
            (getattr(hand_card, 'cost', 0) or 0) <= 3 and
            getattr(hand_card, 'name', '') != 'Wanda'):
            player.hand.remove(hand_card)
            player.cards_in_play.append(hand_card)
            return True
    return True


# --- OP02-050: Inazuma ---
@register_effect("OP02-050", "continuous", "If 1 or less cards in hand, gain +2000 power")
def op02_050_inazuma_cont(game_state, player, card):
    """If you have 1 or less cards in hand, gain +2000 power."""
    if len(player.hand) <= 1:
        card.power_modifier = getattr(card, 'power_modifier', 0) + 2000
    return True


@register_effect("OP02-050", "blocker", "[Blocker]")
def op02_050_inazuma_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


# --- OP02-051: Emporio.Ivankov ---
@register_effect("OP02-051", "on_play", "[On Play] Draw to 3 cards, play blue Impel Down cost 6 or less")
def op02_051_ivankov(game_state, player, card):
    """On Play: Draw until you have 3 cards, then play blue Impel Down cost 6 or less."""
    while len(player.hand) < 3 and player.deck:
        player.hand.append(player.deck.pop(0))
    playable = [c for c in player.hand
                if (getattr(c, 'card_type', '') == 'CHARACTER' and
                    'Blue' in getattr(c, 'colors', []) and
                    'Impel Down' in (c.card_origin or '') and
                    (getattr(c, 'cost', 0) or 0) <= 6)]
    if playable:
        return create_play_from_hand_choice(
            game_state, player, playable,
            source_card=card,
            prompt="Choose blue Impel Down cost 6 or less to play"
        )
    return True


# --- OP02-052: Cabaji ---
@register_effect("OP02-052", "on_play", "[On Play] If you have Mohji, draw 2 trash 1")
def op02_052_cabaji(game_state, player, card):
    """On Play: If you have Mohji, draw 2 and trash 1."""
    has_mohji = any(getattr(c, 'name', '') == 'Mohji' for c in player.cards_in_play)
    if has_mohji:
        draw_cards(player, 2)
        trash_from_hand(player, 1, game_state, card)
    return True


# --- OP02-056: Donquixote Doflamingo ---
@register_effect("OP02-056", "on_play", "[On Play] Look at top 3, arrange at top or bottom")
def op02_056_doffy_play(game_state, player, card):
    """On Play: Look at top 3 cards and place at top or bottom."""
    return True


@register_effect("OP02-056", "on_attack", "[DON!! x1] Trash 1: Place opponent's cost 1 or less at bottom of deck")
def op02_056_doffy_attack(game_state, player, card):
    """DON x1: Trash 1 card to place opponent's cost 1 or less Character at bottom of deck."""
    if getattr(card, 'attached_don', 0) >= 1 and player.hand:
        trash_from_hand(player, 1, game_state, card)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 1]
        if targets:
            return create_bottom_deck_choice(game_state, player, targets, source_card=card,
                                            prompt="Choose opponent's cost 1 or less to place at deck bottom")
        return True
    return False


# --- OP02-057: Bartholomew Kuma ---
@register_effect("OP02-057", "on_play", "[On Play] Look at 2, reveal Seven Warlords card to hand")
def op02_057_kuma(game_state, player, card):
    """On Play: Look at top 2 cards, reveal a Seven Warlords card to hand."""
    def filter_fn(c):
        return 'The Seven Warlords of the Sea' in (c.card_origin or '')
    search_top_cards(game_state, player, 2, add_count=1, filter_fn=filter_fn,
                     source_card=card,
                     prompt="Look at top 2. Choose a Seven Warlords card to add to hand.")
    return True


# --- OP02-058: Buggy ---
@register_effect("OP02-058", "on_play", "[On Play] Look at 5, reveal blue Impel Down card to hand")
def op02_058_buggy(game_state, player, card):
    """On Play: Look at top 5, reveal a blue Impel Down card to hand."""
    def filter_fn(c):
        return ('Blue' in (getattr(c, 'colors', None) or [])
                and 'Impel Down' in (c.card_origin or '')
                and getattr(c, 'name', '') != 'Buggy')
    search_top_cards(game_state, player, 5, add_count=1, filter_fn=filter_fn,
                     source_card=card,
                     prompt="Look at top 5. Choose a blue Impel Down card to add to hand.")
    return True


# --- OP02-059: Boa Hancock ---
@register_effect("OP02-059", "on_attack", "[When Attacking] Draw 1, trash 1, then may trash up to 3 more")
def op02_059_hancock(game_state, player, card):
    """When Attacking: Draw 1, trash 1, then may trash up to 3 more."""
    draw_cards(player, 1)
    trash_from_hand(player, 1, game_state, card)
    trash_from_hand(player, min(3, len(player.hand)))
    return True


# --- OP02-061: Morley ---
@register_effect("OP02-061", "on_attack", "[When Attacking] If 1 or less cards in hand, opponent can't use Blocker cost 5 or less")
def op02_061_morley(game_state, player, card):
    """When Attacking: If 1 or less cards in hand, opponent can't use Blocker cost 5 or less."""
    if len(player.hand) <= 1:
        opponent = get_opponent(game_state, player)
        for c in opponent.cards_in_play:
            if (getattr(c, 'cost', 0) or 0) <= 5:
                c.blocker_disabled = True
    return True


# --- OP02-062: Monkey.D.Luffy ---
@register_effect("OP02-062", "on_play", "[On Play/Attack] Trash 2: Return cost 4 or less, gain Double Attack")
def op02_062_luffy(game_state, player, card):
    """On Play/Attack: Trash 2 cards to return cost 4 or less Character and gain Double Attack."""
    if len(player.hand) >= 2:
        trash_from_hand(player, 2, game_state, card)
        card.has_double_attack = True
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
        if targets:
            return create_return_to_hand_choice(game_state, player, targets, source_card=card,
                                               prompt="Choose opponent's cost 4 or less to return to hand")
    return True


# --- OP02-063: Mr.1(Daz.Bonez) ---
@register_effect("OP02-063", "on_play", "[On Play] Add blue Event cost 1 from trash to hand")
def op02_063_mr1(game_state, player, card):
    """On Play: Add a blue Event cost 1 from trash to hand."""
    targets = [c for c in player.trash
               if (getattr(c, 'card_type', '') == 'EVENT' and
                   'Blue' in getattr(c, 'colors', []) and
                   (getattr(c, 'cost', 0) or 0) == 1)]
    if targets:
        return create_add_from_trash_choice(game_state, player, targets, source_card=card,
                                           prompt="Choose blue Event cost 1 from trash to add to hand")
    return True


# --- OP02-064: Mr.2.Bon.Kurei ---
@register_effect("OP02-064", "on_attack", "[DON!! x1] Trash 1: Place cost 2 or less at bottom, then this goes to bottom")
def op02_064_mr2(game_state, player, card):
    """DON x1: Trash 1 to place opponent's cost 2 or less at bottom. This goes to bottom at end of battle."""
    if getattr(card, 'attached_don', 0) >= 1 and player.hand:
        trash_from_hand(player, 1, game_state, card)
        card.return_to_bottom_after_battle = True
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
        if targets:
            return create_bottom_deck_choice(game_state, player, targets, source_card=card,
                                            prompt="Choose opponent's cost 2 or less to place at deck bottom")
        return True
    return False


# --- OP02-065: Mr.3(Galdino) ---
@register_effect("OP02-065", "blocker", "[Blocker]")
def op02_065_mr3_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP02-065", "end_of_turn", "[End of Turn] Trash 1: Set this active")
def op02_065_mr3_eot(game_state, player, card):
    """End of Turn: Trash 1 card from hand to set this active."""
    if player.hand:
        trash_from_hand(player, 1, game_state, card)
        card.is_resting = False
        return True
    return False


# --- OP02-073: Little Sadi ---
@register_effect("OP02-073", "on_play", "[On Play] Play Jailer Beast from hand")
def op02_073_sadi(game_state, player, card):
    """On Play: Play a Jailer Beast Character from hand."""
    playable = [c for c in player.hand
                if (getattr(c, 'card_type', '') == 'CHARACTER' and
                    'Jailer Beast' in (c.card_origin or ''))]
    if playable:
        return create_play_from_hand_choice(
            game_state, player, playable,
            source_card=card,
            prompt="Choose Jailer Beast to play"
        )
    return True


# --- OP02-074: Saldeath ---
@register_effect("OP02-074", "continuous", "Your Blugori gains Blocker")
def op02_074_saldeath(game_state, player, card):
    """Your Blugori gains Blocker."""
    for c in player.cards_in_play:
        if getattr(c, 'name', '') == 'Blugori':
            c.has_blocker = True
    return True


# --- OP02-076: Shiryu ---
@register_effect("OP02-076", "on_play", "[On Play] DON!! -1: K.O. opponent's cost 1 or less")
def op02_076_shiryu(game_state, player, card):
    """On Play: Return 1 DON to DON deck to K.O. opponent's cost 1 or less Character."""
    if player.don_pool:
        don = player.don_pool.pop()
        player.don_deck.append(don)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 1]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's cost 1 or less to KO")
        return True
    return False


# --- OP02-078: Daifugo ---
@register_effect("OP02-078", "on_play", "[On Play] DON!! -2: Play SMILE cost 3 or less from hand")
def op02_078_daifugo(game_state, player, card):
    """On Play: Return 2 DON to play a SMILE cost 3 or less from hand."""
    if len(player.don_pool) >= 2:
        for _ in range(2):
            don = player.don_pool.pop()
            player.don_deck.append(don)
        playable = [c for c in player.hand
                    if (getattr(c, 'card_type', '') == 'CHARACTER' and
                        'SMILE' in (c.card_origin or '') and
                        (getattr(c, 'cost', 0) or 0) <= 3 and
                        getattr(c, 'name', '') != 'Daifugo')]
        if playable:
            return create_play_from_hand_choice(
                game_state, player, playable,
                source_card=card,
                prompt="Choose SMILE cost 3 or less to play"
            )
        return True
    return False


# --- OP02-079: Douglas Bullet ---
@register_effect("OP02-079", "on_play", "[On Play] DON!! -1: Rest opponent's cost 4 or less")
def op02_079_bullet(game_state, player, card):
    """On Play: Return 1 DON to rest opponent's cost 4 or less Character."""
    if player.don_pool:
        don = player.don_pool.pop()
        player.don_deck.append(don)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play
                   if (getattr(c, 'cost', 0) or 0) <= 4 and not getattr(c, 'is_resting', False)]
        if targets:
            return create_rest_choice(game_state, player, targets, source_card=card,
                                     prompt="Choose opponent's cost 4 or less to rest")
        return True
    return False


# --- OP02-081: Domino ---
@register_effect("OP02-081", "blocker", "[Blocker]")
def op02_081_domino(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


# --- OP02-082: Byrnndi World ---
@register_effect("OP02-082", "activate", "[Activate: Main] DON!! -8: Gain +792000 power")
def op02_082_world(game_state, player, card):
    """Activate: Return 8 DON to gain +792000 power."""
    if len(player.don_pool) >= 8:
        for _ in range(8):
            don = player.don_pool.pop()
            player.don_deck.append(don)
        card.power_modifier = getattr(card, 'power_modifier', 0) + 792000
        return True
    return False


# --- OP02-083: Hannyabal ---
@register_effect("OP02-083", "on_play", "[On Play] Look at 5, reveal purple Impel Down to hand")
def op02_083_hannyabal(game_state, player, card):
    """On Play: Look at top 5, reveal a purple Impel Down card to hand."""
    def filter_fn(c):
        return ('Purple' in (getattr(c, 'colors', None) or [])
                and 'Impel Down' in (c.card_origin or '')
                and getattr(c, 'name', '') != 'Hannyabal')
    search_top_cards(game_state, player, 5, add_count=1, filter_fn=filter_fn,
                     source_card=card,
                     prompt="Look at top 5. Choose a purple Impel Down card to add to hand.")
    return True


# --- OP02-085: Magellan ---
@register_effect("OP02-085", "on_play", "[On Play] DON!! -1: Opponent returns 1 DON")
def op02_085_magellan_play(game_state, player, card):
    """On Play: Return 1 DON to make opponent return 1 DON."""
    if player.don_pool:
        don = player.don_pool.pop()
        player.don_deck.append(don)
        opponent = get_opponent(game_state, player)
        if opponent.don_pool:
            opp_don = opponent.don_pool.pop()
            opponent.don_deck.append(opp_don)
        return True
    return False


@register_effect("OP02-085", "on_ko", "[Opponent's Turn] [On K.O.] Opponent returns 2 DON")
def op02_085_magellan_ko(game_state, player, card):
    """On K.O. during opponent's turn: Opponent returns 2 DON."""
    opponent = get_opponent(game_state, player)
    for _ in range(min(2, len(opponent.don_pool))):
        if opponent.don_pool:
            opp_don = opponent.don_pool.pop()
            opponent.don_deck.append(opp_don)
    return True


# --- OP02-086: Minokoala ---
@register_effect("OP02-086", "blocker", "[Blocker]")
def op02_086_minokoala_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP02-086", "on_ko", "[On K.O.] If Impel Down Leader, add 1 DON rested")
def op02_086_minokoala_ko(game_state, player, card):
    """On K.O.: If Leader is Impel Down, add 1 DON from DON deck rested."""
    if player.leader and 'Impel Down' in (player.leader.card_origin or ''):
        add_don_from_deck(player, 1, rested=True)
    return True


# --- OP02-087: Minotaur ---
@register_effect("OP02-087", "continuous", "[Double Attack]")
def op02_087_minotaur_da(game_state, player, card):
    """Double Attack."""
    card.has_double_attack = True
    return True


@register_effect("OP02-087", "on_ko", "[On K.O.] If Impel Down Leader, add 1 DON rested")
def op02_087_minotaur_ko(game_state, player, card):
    """On K.O.: If Leader is Impel Down, add 1 DON from DON deck rested."""
    if player.leader and 'Impel Down' in (player.leader.card_origin or ''):
        add_don_from_deck(player, 1, rested=True)
    return True


# --- OP02-094: Isuka ---
@register_effect("OP02-094", "on_attack", "[DON!! x1] [Once Per Turn] When K.O. opponent in battle, set active")
def op02_094_isuka(game_state, player, card):
    """DON x1: Once per turn, when this K.O.s opponent's Character in battle, set active."""
    if getattr(card, 'attached_don', 0) >= 1:
        if not getattr(card, 'op02_094_used', False):
            card.set_active_on_ko = True
    return True


# --- OP02-095: Onigumo ---
@register_effect("OP02-095", "continuous", "If there's a cost 0 Character, gain Banish")
def op02_095_onigumo(game_state, player, card):
    """If there's a cost 0 Character, gain Banish."""
    opponent = get_opponent(game_state, player)
    all_chars = player.cards_in_play + opponent.cards_in_play
    if any((getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) == 0 for c in all_chars):
        card.has_banish = True
    return True


# --- OP02-096: Kuzan ---
@register_effect("OP02-096", "on_play", "[On Play] Draw 1 card")
def op02_096_kuzan_play(game_state, player, card):
    """On Play: Draw 1 card."""
    draw_cards(player, 1)
    return True


@register_effect("OP02-096", "on_attack", "[When Attacking] Give opponent's Character -4 cost")
def op02_096_kuzan_attack(game_state, player, card):
    """When Attacking: Give opponent's Character -4 cost."""
    opponent = get_opponent(game_state, player)
    if opponent.cards_in_play:
        return create_cost_reduction_choice(game_state, player, opponent.cards_in_play, -4, source_card=card,
                                           prompt="Choose opponent's Character to give -4 cost")
    return True


# --- OP02-098: Koby ---
@register_effect("OP02-098", "on_play", "[On Play] Trash 1: K.O. opponent's cost 3 or less")
def op02_098_koby(game_state, player, card):
    """On Play: Trash 1 card to K.O. opponent's cost 3 or less Character."""
    if player.hand:
        trash_from_hand(player, 1, game_state, card)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's cost 3 or less to KO")
    return True


# --- OP02-099: Sakazuki ---
@register_effect("OP02-099", "on_play", "[On Play] Trash 1: K.O. opponent's cost 5 or less")
def op02_099_sakazuki(game_state, player, card):
    """On Play: Trash 1 card to K.O. opponent's cost 5 or less Character."""
    if player.hand:
        trash_from_hand(player, 1, game_state, card)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 5]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's cost 5 or less to KO")
    return True


# --- OP02-100: Jango ---
@register_effect("OP02-100", "continuous", "If you have Fullbody, cannot be K.O.'d in battle")
def op02_100_jango(game_state, player, card):
    """If you have Fullbody, cannot be K.O.'d in battle."""
    if any(getattr(c, 'name', '') == 'Fullbody' for c in player.cards_in_play):
        card.cannot_be_ko_in_battle = True
    return True


# --- OP02-101: Strawberry ---
@register_effect("OP02-101", "on_attack", "[When Attacking] If cost 0 exists, opponent can't use Blocker cost 5 or less")
def op02_101_strawberry(game_state, player, card):
    """When Attacking: If cost 0 Character exists, opponent can't use Blocker cost 5 or less."""
    opponent = get_opponent(game_state, player)
    all_chars = player.cards_in_play + opponent.cards_in_play
    if any((getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) == 0 for c in all_chars):
        for c in opponent.cards_in_play:
            if (getattr(c, 'cost', 0) or 0) <= 5:
                c.blocker_disabled = True
    return True


# --- OP02-102: Smoker ---
@register_effect("OP02-102", "continuous", "Cannot be K.O.'d by effects")
def op02_102_smoker_cont(game_state, player, card):
    """Cannot be K.O.'d by effects."""
    card.cannot_be_ko_by_effects = True
    return True


@register_effect("OP02-102", "on_attack", "[When Attacking] If cost 0 exists, gain +2000 power")
def op02_102_smoker_attack(game_state, player, card):
    """When Attacking: If cost 0 Character exists, gain +2000 power."""
    opponent = get_opponent(game_state, player)
    all_chars = player.cards_in_play + opponent.cards_in_play
    if any((getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) == 0 for c in all_chars):
        card.power_modifier = getattr(card, 'power_modifier', 0) + 2000
    return True


# --- OP02-103: Sengoku ---
@register_effect("OP02-103", "on_attack", "[DON!! x1] Give opponent's Character -2 cost")
def op02_103_sengoku(game_state, player, card):
    """DON x1: Give opponent's Character -2 cost."""
    if getattr(card, 'attached_don', 0) >= 1:
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            return create_cost_reduction_choice(game_state, player, opponent.cards_in_play, -2, source_card=card,
                                               prompt="Choose opponent's Character to give -2 cost")
        return True
    return False


# --- OP02-105: Tashigi ---
@register_effect("OP02-105", "on_attack", "[DON!! x1] Give opponent's Character -3 cost")
def op02_105_tashigi(game_state, player, card):
    """DON x1: Give opponent's Character -3 cost."""
    if getattr(card, 'attached_don', 0) >= 1:
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            return create_cost_reduction_choice(game_state, player, opponent.cards_in_play, -3, source_card=card,
                                               prompt="Choose opponent's Character to give -3 cost")
        return True
    return False


# --- OP02-106: Tsuru ---
@register_effect("OP02-106", "on_play", "[On Play] Give opponent's Character -2 cost")
def op02_106_tsuru(game_state, player, card):
    """On Play: Give opponent's Character -2 cost."""
    opponent = get_opponent(game_state, player)
    if opponent.cards_in_play:
        return create_cost_reduction_choice(game_state, player, opponent.cards_in_play, -2, source_card=card,
                                           prompt="Choose opponent's Character to give -2 cost")
    return True


# --- OP02-108: Donquixote Rosinante ---
@register_effect("OP02-108", "blocker", "[Blocker]")
def op02_108_rosinante(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


# --- OP02-110: Hina ---
@register_effect("OP02-110", "blocker", "[Blocker]")
def op02_110_hina_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP02-110", "on_block", "[On Block] Opponent's cost 6 or less can't attack this turn")
def op02_110_hina_block(game_state, player, card):
    """On Block: Select opponent's cost 6 or less, it can't attack this turn."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 6]
    if targets:
        return create_target_choice(
            game_state, player, targets,
            callback_action="cannot_attack_target",
            source_card=card,
            prompt="Choose opponent's cost 6 or less that can't attack this turn"
        )
    return True


# --- OP02-111: Fullbody ---
@register_effect("OP02-111", "on_attack", "[When Attacking] If you have Jango, gain +3000 power")
def op02_111_fullbody(game_state, player, card):
    """When Attacking: If you have Jango, gain +3000 power."""
    if any(getattr(c, 'name', '') == 'Jango' for c in player.cards_in_play):
        card.power_modifier = getattr(card, 'power_modifier', 0) + 3000
    return True


# --- OP02-112: Bell-mère ---
@register_effect("OP02-112", "activate", "[Activate: Main] Rest: Give opponent -1 cost, your card gains +1000")
def op02_112_bellmere(game_state, player, card):
    """Activate: Rest to give opponent's Character -1 cost and your card +1000 power."""
    if not getattr(card, 'is_resting', False):
        card.is_resting = True
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            return create_dual_target_choice(
                game_state, player,
                targets1=opponent.cards_in_play, callback1="cost_reduction_minus1",
                targets2=player.cards_in_play, callback2="power_plus1000",
                source_card=card,
                prompt="Choose opponent's Character for -1 cost, then your Character for +1000"
            )
        return True
    return False


# --- OP02-113: Helmeppo ---
@register_effect("OP02-113", "on_attack", "[When Attacking] Give -2 cost, if cost 0 exists, gain +2000")
def op02_113_helmeppo(game_state, player, card):
    """When Attacking: Give opponent -2 cost. If cost 0 exists, gain +2000."""
    opponent = get_opponent(game_state, player)
    all_chars = player.cards_in_play + opponent.cards_in_play
    if any((getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) == 0 for c in all_chars):
        card.power_modifier = getattr(card, 'power_modifier', 0) + 2000
    if opponent.cards_in_play:
        return create_cost_reduction_choice(game_state, player, opponent.cards_in_play, -2, source_card=card,
                                           prompt="Choose opponent's Character to give -2 cost")
    return True


@register_effect("OP02-113", "trigger", "[Trigger] Play this card")
def op02_113_helmeppo_trigger(game_state, player, card):
    """Trigger: Play this card."""
    player.cards_in_play.append(card)
    return True


# --- OP02-114: Borsalino ---
@register_effect("OP02-114", "continuous", "[Opponent's Turn] Gain +1000 power, cannot be K.O.'d by effects")
def op02_114_borsalino_cont(game_state, player, card):
    """Opponent's Turn: Gain +1000 power and cannot be K.O.'d by effects."""
    card.power_modifier = getattr(card, 'power_modifier', 0) + 1000
    card.cannot_be_ko_by_effects = True
    return True


@register_effect("OP02-114", "blocker", "[Blocker]")
def op02_114_borsalino_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


# --- OP02-115: Monkey.D.Garp ---
@register_effect("OP02-115", "on_attack", "[DON!! x2] K.O. opponent's cost 0 Character")
def op02_115_garp(game_state, player, card):
    """DON x2: K.O. opponent's cost 0 Character."""
    if getattr(card, 'attached_don', 0) >= 2:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play
                   if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) == 0]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's cost 0 Character to KO")
        return True
    return False


# --- OP02-120: Uta ---
@register_effect("OP02-120", "on_play", "[On Play] DON!! -2: Leader and all Characters gain +1000 until next turn")
def op02_120_uta(game_state, player, card):
    """On Play: Return 2 DON to give Leader and all Characters +1000 until next turn."""
    if len(player.don_pool) >= 2:
        for _ in range(2):
            don = player.don_pool.pop()
            player.don_deck.append(don)
        if player.leader:
            player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 1000
        for c in player.cards_in_play:
            c.power_modifier = getattr(c, 'power_modifier', 0) + 1000
        return True
    return False


# --- OP02-121: Kuzan (SEC) ---
@register_effect("OP02-121", "continuous", "[Your Turn] All opponent's Characters get -5 cost")
def op02_121_kuzan_cont(game_state, player, card):
    """Your Turn: All opponent's Characters get -5 cost."""
    opponent = get_opponent(game_state, player)
    for c in opponent.cards_in_play:
        c.cost_modifier = getattr(c, 'cost_modifier', 0) - 5
    return True


@register_effect("OP02-121", "on_play", "[On Play] K.O. opponent's cost 0 Character")
def op02_121_kuzan_play(game_state, player, card):
    """On Play: K.O. opponent's cost 0 Character."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) == 0]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                               prompt="Choose opponent's cost 0 Character to KO")
    return True


# --- OP02-022: Whitebeard Pirates (Event) ---
@register_effect("OP02-022", "on_play", "[Main] Look at 5, reveal Whitebeard Pirates Character to hand")
def op02_022_whitebeard_pirates(game_state, player, card):
    """[Main] Look at 5 cards from top of deck; reveal up to 1 Character card with
    type including 'Whitebeard Pirates' and add it to hand. Rest at bottom."""
    def filter_fn(c):
        return (c.card_type == 'CHARACTER'
                and 'whitebeard pirates' in (c.card_origin or '').lower())
    return search_top_cards(
        game_state, player, look_count=5, add_count=1,
        filter_fn=filter_fn, source_card=card,
        prompt="Look at top 5: choose 1 Whitebeard Pirates Character to add to hand")


@register_effect("OP02-022", "trigger", "[Trigger] Activate this card's [Main] effect")
def op02_022_whitebeard_pirates_trigger(game_state, player, card):
    """Trigger: Activate this card's [Main] effect."""
    return op02_022_whitebeard_pirates(game_state, player, card)


# --- OP02-092: Impel Down (Stage) ---
@register_effect("OP02-092", "activate", "[Activate: Main] Trash 1, rest this Stage: Look at 3, reveal Impel Down card to hand")
def op02_092_impel_down(game_state, player, card):
    """[Activate: Main] You may trash 1 card from your hand and rest this Stage:
    Look at 3 from top; reveal up to 1 Impel Down type card and add to hand.
    Rest at bottom."""
    if card.is_resting:
        return False
    if getattr(card, 'main_activated_this_turn', False):
        return False
    if not player.hand:
        return False

    # Pay cost: rest this stage
    card.is_resting = True
    card.main_activated_this_turn = True

    # Create trash-from-hand choice, then chain to search
    from ..hardcoded import create_hand_discard_choice
    return create_hand_discard_choice(
        game_state, player, list(player.hand),
        callback_action="impel_down_trash_then_search",
        source_card=card,
        prompt="Choose 1 card from hand to trash (cost for Impel Down search)")


