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
    optional_don_return, reorder_top_cards, return_don_to_deck, search_top_cards, trash_from_hand,
)


# --- OP02-023: You May Be a Fool...but I Still Love You ---
@register_effect("OP02-023", "on_play", "[Main] If Whitebeard Pirates Leader and 3 or less Life, add 1 Life to hand; opponent can't add Life this turn")
def you_may_be_a_fool_effect(game_state, player, card):
    """Main Event: If Leader is Whitebeard Pirates and you have 3 or fewer Life cards,
    add 1 Life to hand. Then, opponent cannot add Life cards to their hand this turn."""
    if player.leader and 'Whitebeard Pirates' in (player.leader.card_origin or ''):
        if len(player.life_cards) <= 3 and player.life_cards:
            life_card = player.life_cards.pop()
            player.hand.append(life_card)
            game_state._log(f"{player.name} adds 1 Life to hand via You May Be a Fool")
        opponent = get_opponent(game_state, player)
        opponent.cannot_add_life_to_hand_this_turn = True
        return True
    return True


# Stale uppercase handlers removed (duplicates of lowercase handlers below)


# =============================================================================
# LEADER CARD EFFECTS - OP02 (Paramount War)
# =============================================================================

# --- OP02-001: Edward.Newgate (Leader) ---
@register_effect("OP02-001", "end_of_turn", "[End of Your Turn] Add 1 Life to hand")
def op02_001_whitebeard_leader(game_state, player, card):
    """End of Your Turn: Add 1 card from the top of your Life cards to your hand."""
    if getattr(player, 'cannot_add_life', False) or getattr(player, 'cannot_add_life_to_hand_this_turn', False):
        game_state._log(f"{card.name}'s effect could not add a Life card to hand this turn")
        return False
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


# --- OP02-024: Moby Dick ---
@register_effect("OP02-024", "continuous", "[Your Turn] If you have 1 or less Life, your Edward.Newgate and all Whitebeard Pirates gain +2000")
def op02_024_moby_dick(game_state, player, card):
    """Your Turn: If you have 1 or less Life, Edward.Newgate and all Whitebeard Pirates gain +2000 power."""
    if game_state.current_player is not player or len(player.life_cards) > 1:
        return True
    if player.leader and getattr(player.leader, 'name', '') == 'Edward.Newgate':
        player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 2000
    for char in player.cards_in_play:
        if 'Whitebeard Pirates' in (getattr(char, 'card_origin', '') or ''):
            char.power_modifier = getattr(char, 'power_modifier', 0) + 2000
    return True


# --- OP02-025: Kin'emon (Leader) ---
@register_effect("OP02-025", "activate", "[Activate: Main] If 1- chars, next Land of Wano cost 3+ costs -1")
def op02_025_kinemon_leader(game_state, player, card):
    """Once Per Turn: If 1 or less Characters, next Land of Wano cost 3+ from hand costs -1."""
    if hasattr(card, 'op02_025_used') and card.op02_025_used:
        return False
    char_count = sum(1 for c in player.cards_in_play if getattr(c, 'card_type', '') == 'CHARACTER')
    if char_count <= 1:
        player.next_wano_discount = True
        card.op02_025_used = True
        return True
    return False


# --- OP02-026: Sanji (Leader) ---
@register_effect("OP02-026", "on_play_character", "[Once Per Turn] When play no-effect char, if 3- chars, set 2 DON active")
def op02_026_sanji_leader(game_state, player, card):
    """Once Per Turn: When you play a Character with no base effect, if 3 or less Characters, set 2 DON active."""
    from ...game_engine import PendingChoice
    import uuid as _uuid

    if hasattr(card, 'op02_026_used') and card.op02_026_used:
        return False
    played_card = getattr(game_state, 'last_played_character', None)
    if not played_card or getattr(played_card, 'effect', ''):
        return False

    char_count = sum(1 for c in player.cards_in_play if getattr(c, 'card_type', '') == 'CHARACTER')
    if char_count > 3:
        return False

    rested_don = [i for i, d in enumerate(player.don_pool) if d == "rested"]
    if not rested_don:
        card.op02_026_used = True
        return True

    options = [
        {
            "id": str(i),
            "label": f"Rested DON!! #{idx + 1}",
            "card_id": f"don_{idx}",
            "card_name": "DON!!",
        }
        for i, idx in enumerate(rested_don)
    ]
    game_state.pending_choice = PendingChoice(
        choice_id=f"sanji_don_{_uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Sanji: Set up to 2 of your DON!! cards as active (or skip)",
        options=options,
        min_selections=0,
        max_selections=min(2, len(rested_don)),
        source_card_id=card.id,
        source_card_name=card.name,
        callback_action="op02_026_set_don_active",
        callback_data={
            "player_id": player.player_id,
            "player_index": 0 if player is game_state.player1 else 1,
            "rested_indices": rested_don,
            "leader_id": card.id,
        }
    )
    card.op02_026_used = True
    return True


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
    result = optional_don_return(game_state, player, 4, source_card=card,
                                 after_callback="op02_072_zephyr_effect",
                                 after_callback_data={"source_card_id": card.id})
    if not result:
        return True  # Pending choice
    return True  # Can't pay, fizzled


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
@register_effect("OP02-004", "on_play", "[On Play] Optionally give Leader +2000 power until end of next turn, cannot add Life this turn")
def op02_004_newgate_play(game_state, player, card):
    """On Play: Optionally give Leader +2000 power until end of next turn. Cannot add Life cards this turn."""
    player.cannot_add_life = True
    if player.leader:
        from ...game_engine import PendingChoice
        import uuid as _uuid
        game_state.pending_choice = PendingChoice(
            choice_id=f"newgate_play_{_uuid.uuid4().hex[:8]}",
            choice_type="select_target",
            prompt="Give your Leader +2000 power until end of your next turn? (Select to apply, skip to decline)",
            options=[{"id": "0", "label": f"{player.leader.name} (Leader)", "card_id": player.leader.id, "card_name": player.leader.name}],
            min_selections=0,
            max_selections=1,
            source_card_id=card.id,
            source_card_name=card.name,
            callback_action="apply_power_until_next_turn",
            callback_data={
                "player_id": player.player_id,
                "power_amount": 2000,
                "target_cards": [{"id": player.leader.id, "name": player.leader.name}],
            }
        )
        return True
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
    if (getattr(card, 'attached_don', 0) >= 1
            and len(player.life_cards) <= 2
            and player.leader and 'Whitebeard Pirates' in (player.leader.card_origin or '')):
        card.has_rush = True
    else:
        card.has_rush = False
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
        card._temporary_rush_until_turn = game_state.turn_count
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if c]
    if targets:
        return create_power_effect_choice(
            game_state, player, targets, -3000,
            source_card=card,
            prompt="Choose up to 2 opponent Characters to give -3000 power",
            min_selections=0,
            max_selections=min(2, len(targets))
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
    from ...game_engine import PendingChoice
    import uuid as _uuid
    if len(player.life_cards) <= 2:
        wb_cards = [c for c in player.hand if 'Whitebeard Pirates' in (c.card_origin or '')]
        if wb_cards and card in player.trash:
            options = []
            for i, hc in enumerate(wb_cards):
                options.append({
                    "id": str(i),
                    "label": f"{hc.name} (Cost: {hc.cost or 0})",
                    "card_id": hc.id,
                    "card_name": hc.name,
                })
            game_state.pending_choice = PendingChoice(
                choice_id=f"marco_ko_{_uuid.uuid4().hex[:8]}",
                choice_type="select_cards",
                prompt="Choose a Whitebeard Pirates card from hand to trash (to revive Marco)",
                options=options,
                min_selections=0,
                max_selections=1,
                source_card_id=card.id,
                source_card_name=card.name,
                callback_action="marco_trash_wb_then_revive",
                callback_data={
                    "player_id": player.player_id,
                    "player_index": 0 if player is game_state.player1 else 1,
                    "target_cards": [{"id": hc.id, "name": hc.name} for hc in wb_cards],
                    "marco_card_id": card.id,
                }
            )
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
        all_rested = all(d == "rested" for d in player.don_pool)
        if all_rested:
            card.cannot_be_removed = True
    return True


# --- OP02-029: Carrot ---
@register_effect("OP02-029", "end_of_turn", "[End of Your Turn] Set 1 DON as active")
def op02_029_carrot(game_state, player, card):
    """End of Turn: Set up to 1 DON as active."""
    from ...game_engine import PendingChoice
    import uuid as _uuid

    rested_don = [i for i, d in enumerate(player.don_pool) if d == "rested"]
    if not rested_don:
        return True

    options = [
        {
            "id": str(i),
            "label": f"Rested DON!! #{idx + 1}",
            "card_id": f"don_{idx}",
            "card_name": "DON!!",
        }
        for i, idx in enumerate(rested_don)
    ]
    game_state.pending_choice = PendingChoice(
        choice_id=f"carrot_don_{_uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Carrot: Set up to 1 of your DON!! cards as active (or skip)",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback_action="op02_029_set_don_active",
        callback_data={
            "player_id": player.player_id,
            "player_index": 0 if player is game_state.player1 else 1,
            "rested_indices": rested_don,
        }
    )
    return True


# --- OP02-030: Kouzuki Oden ---
@register_effect("OP02-030", "activate", "[Activate: Main] [Once Per Turn] Rest 3 DON: Set this active, can attack again")
def op02_030_oden_activate(game_state, player, card):
    """Activate: Rest 3 DON to set this Character as active."""
    if getattr(card, 'op02_030_used', False):
        return False
    active_count = player.don_pool.count("active")
    if active_count >= 3:
        rested = 0
        for i in range(len(player.don_pool)):
            if rested >= 3:
                break
            if player.don_pool[i] == "active":
                player.don_pool[i] = "rested"
                rested += 1
        card.is_resting = False
        card.has_attacked = False  # Can attack again after being set active
        card.op02_030_used = True
        return True
    return False


@register_effect("OP02-030", "on_ko", "[On K.O.] Play green Land of Wano cost 3 or less Character from deck")
def op02_030_oden_ko(game_state, player, card):
    """On K.O.: Play a green Land of Wano cost 3 or less Character from deck."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    targets = [c for c in player.deck
               if (getattr(c, 'card_type', '') == 'CHARACTER'
                   and 'Green' in (getattr(c, 'colors', None) or [])
                   and 'Land of Wano' in (c.card_origin or '')
                   and (getattr(c, 'cost', 0) or 0) == 3)]
    if not targets:
        return True
    options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})",
                "card_id": c.id, "card_name": c.name}
               for i, c in enumerate(targets)]
    game_state.pending_choice = PendingChoice(
        choice_id=f"oden_ko_{_uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Kouzuki Oden: Choose a green Land of Wano cost 3 or less Character to play from deck",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback_action="search_play_to_field",
        callback_data={
            "player_id": player.player_id,
            "player_index": 0 if player is game_state.player1 else 1,
            "target_cards": [{"id": c.id, "name": c.name} for c in targets],
            "shuffle_after": True,
        }
    )
    return True


# --- OP02-031: Kouzuki Toki ---
@register_effect("OP02-031", "continuous", "If you have Kouzuki Oden Character, gain Blocker")
def op02_031_toki(game_state, player, card):
    """If you have a Kouzuki Oden Character, gain Blocker."""
    has_oden = any(
        getattr(c, 'name', '') in ('Kouzuki Oden', 'Kozuki Oden')
        or getattr(c, 'alt_name', '') in ('Kouzuki Oden', 'Kozuki Oden')
        or c.id_normal == 'OP02-042'
        for c in player.cards_in_play if c is not card
    )
    if has_oden:
        card.has_blocker = True
        card._continuous_blocker = True
    else:
        card.has_blocker = False
        card._continuous_blocker = False
    return True


# --- OP02-032: Shishilian ---
@register_effect("OP02-032", "on_play", "[On Play] You may rest 2 DON: Set Minks cost 5 or less as active")
def op02_032_shishilian(game_state, player, card):
    """On Play: You may rest 2 DON to set a Minks cost 5 or less Character as active."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    active_count = player.don_pool.count("active")
    if active_count < 2:
        return True  # Can't pay cost; skip
    targets = [c for c in player.cards_in_play
               if 'Minks' in (c.card_origin or '') and
               (getattr(c, 'cost', 0) or 0) <= 5 and
               getattr(c, 'is_resting', False)]
    if not targets:
        return True  # No valid targets to activate
    options = [
        {"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})",
         "card_id": c.id, "card_name": c.name}
        for i, c in enumerate(targets)
    ]
    game_state.pending_choice = PendingChoice(
        choice_id=f"shishilian_{_uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="You may rest 2 DON!! to set a Minks cost 5 or less as active (select 0 to skip)",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback_action="op02_032_pay_don_set_active",
        callback_data={
            "player_id": player.player_id,
            "player_index": 0 if player is game_state.player1 else 1,
            "target_cards": [{"id": c.id, "name": c.name} for c in targets],
        }
    )
    return True


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
@register_effect("OP02-035", "activate", "[Activate: Main] Rest 1 DON, return to hand: Play cost 3 or less from hand")
def op02_035_law(game_state, player, card):
    """Activate: Rest 1 DON and return this to hand to play a cost 3 or less Character from hand."""
    active_count = player.don_pool.count("active")
    if active_count >= 1:
        # Rest 1 active DON
        for i in range(len(player.don_pool)):
            if player.don_pool[i] == "active":
                player.don_pool[i] = "rested"
                break
        # Return this card to hand
        if card in player.cards_in_play:
            player.cards_in_play.remove(card)
            player.hand.append(card)
        # Play a cost 3 or less character from hand
        playable = [c for c in player.hand
                    if (getattr(c, 'card_type', '') == 'CHARACTER' and
                        (getattr(c, 'cost', 0) or 0) <= 3 and c is not card)]
        if playable:
            return create_play_from_hand_choice(
                game_state, player, playable,
                source_card=card,
                prompt="Choose cost 3 or less Character to play from hand"
            )
        return True
    return False


# --- OP02-036: Nami ---
@register_effect("OP02-036", "on_play", "[On Play] You may rest 1 DON: Look at 3, reveal FILM card (not Nami) to hand")
@register_effect("OP02-036", "on_attack", "[When Attacking] You may rest 1 DON: Look at 3, reveal FILM card (not Nami) to hand")
def op02_036_nami(game_state, player, card):
    """On Play: You may rest 1 DON to look at top 3 cards, reveal a FILM card (not Nami) to hand."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    active_count = player.don_pool.count("active")
    if active_count < 1:
        return True  # No active DON available to pay cost
    # Prompt player to decide whether to rest 1 DON for the search effect
    game_state.pending_choice = PendingChoice(
        choice_id=f"nami_don_{_uuid.uuid4().hex[:8]}",
        choice_type="select_mode",
        prompt="You may rest 1 DON!! to look at the top 3 cards and add a FILM card to hand. Do you want to?",
        options=[
            {"id": "yes", "label": "Yes — rest 1 DON and search top 3"},
            {"id": "no",  "label": "No — skip the effect"},
        ],
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback_action="nami_don_search",
        callback_data={
            "player_id": player.player_id,
            "player_index": 0 if player is game_state.player1 else 1,
        }
    )
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
@register_effect("OP02-044", "on_play", "[On Play] Play up to 1 Minks cost 3 or less from hand")
def op02_044_wanda(game_state, player, card):
    """On Play: Play up to 1 Minks cost 3 or less Character from hand."""
    playable = [c for c in player.hand
                if (getattr(c, 'card_type', '') == 'CHARACTER' and
                    'Minks' in (c.card_origin or '') and
                    (getattr(c, 'cost', 0) or 0) <= 3 and
                    getattr(c, 'name', '') != 'Wanda')]
    if playable:
        return create_play_from_hand_choice(
            game_state, player, playable,
            source_card=card,
            prompt="Choose up to 1 Minks cost 3 or less to play from hand (or skip)"
        )
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
    """On Play: Look at top 3 cards; place them at top or bottom of deck in any order."""
    return reorder_top_cards(game_state, player, 3, source_card=card, allow_top=True)


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
    from ...game_engine import PendingChoice
    import uuid as _uuid
    draw_cards(player, 1)
    if not player.hand:
        return True

    if len(player.hand) == 1:
        trashed = player.hand.pop()
        player.trash.append(trashed)
        game_state._log(f"{player.name} trashed {trashed.name}")
        if player.hand:
            options = []
            for i, hc in enumerate(player.hand):
                options.append({
                    "id": str(i),
                    "label": f"{hc.name} (Cost: {hc.cost or 0})",
                    "card_id": hc.id,
                    "card_name": hc.name,
                })
            game_state.pending_choice = PendingChoice(
                choice_id=f"hancock_trash_{_uuid.uuid4().hex[:8]}",
                choice_type="select_cards",
                prompt="You may trash up to 3 more cards from hand (select 0 to skip)",
                options=options,
                min_selections=0,
                max_selections=min(3, len(player.hand)),
                source_card_id=card.id,
                source_card_name=card.name,
                callback_action="op02_059_optional_trash",
                callback_data={
                    "player_id": player.player_id,
                    "player_index": 0 if player is game_state.player1 else 1,
                }
            )
        return True

    options = []
    for i, hc in enumerate(player.hand):
        options.append({
            "id": str(i),
            "label": f"{hc.name} (Cost: {hc.cost or 0})",
            "card_id": hc.id,
            "card_name": hc.name,
        })
    game_state.pending_choice = PendingChoice(
        choice_id=f"hancock_req_{_uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Choose 1 card from hand to trash, then you may trash up to 3 more",
        options=options,
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback_action="op02_059_required_then_optional",
        callback_data={
            "player_id": player.player_id,
            "player_index": 0 if player is game_state.player1 else 1,
            "source_card_id": card.id,
            "source_card_name": card.name,
        }
    )
    return True


# --- OP02-061: Morley ---
@register_effect("OP02-061", "on_attack", "[When Attacking] If 1 or less cards in hand, opponent can't use Blocker cost 5 or less")
def op02_061_morley(game_state, player, card):
    """When Attacking: If 1 or less cards in hand, opponent can't use Blocker cost 5 or less."""
    if len(player.hand) <= 1:
        # Set on game_state so blocker filtering in initiate_attack and respond_blocker respects it
        game_state.blocker_cost_limit = 5
    return True


# --- OP02-062: Monkey.D.Luffy ---
@register_effect("OP02-062", "on_play", "[On Play] Trash 2: Return cost 4 or less, gain Double Attack")
@register_effect("OP02-062", "on_attack", "[When Attacking] Trash 2: Return cost 4 or less, gain Double Attack")
def op02_062_luffy(game_state, player, card):
    """On Play: Trash 2 cards to return cost 4 or less Character and gain Double Attack."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    if len(player.hand) >= 2:
        options = []
        for i, hc in enumerate(player.hand):
            options.append({
                "id": str(i),
                "label": f"{hc.name} (Cost: {hc.cost or 0})",
                "card_id": hc.id,
                "card_name": hc.name,
            })
        game_state.pending_choice = PendingChoice(
            choice_id=f"luffy_trash_{_uuid.uuid4().hex[:8]}",
            choice_type="select_cards",
            prompt="Choose 2 cards from hand to trash (for Double Attack + return effect)",
            options=options,
            min_selections=2,
            max_selections=2,
            source_card_id=card.id,
            source_card_name=card.name,
            callback_action="op02_062_trash_then_return",
            callback_data={
                "player_id": player.player_id,
                "player_index": 0 if player is game_state.player1 else 1,
                "source_card_id": card.id,
                "source_card_name": card.name,
            }
        )
        return True
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
    from ...game_engine import PendingChoice
    import uuid as _uuid
    if getattr(card, 'attached_don', 0) >= 1 and player.hand:
        options = []
        for i, hc in enumerate(player.hand):
            options.append({
                "id": str(i),
                "label": f"{hc.name} (Cost: {hc.cost or 0})",
                "card_id": hc.id,
                "card_name": hc.name,
            })
        game_state.pending_choice = PendingChoice(
            choice_id=f"mr2_trash_{_uuid.uuid4().hex[:8]}",
            choice_type="select_cards",
            prompt="Choose 1 card from hand to trash (Mr.2 effect)",
            options=options,
            min_selections=1,
            max_selections=1,
            source_card_id=card.id,
            source_card_name=card.name,
            callback_action="op02_064_trash_then_bottom",
            callback_data={
                "player_id": player.player_id,
                "player_index": 0 if player is game_state.player1 else 1,
                "attacker_card_id": card.id,
            }
        )
        return True
    return False


# --- OP02-065: Mr.3(Galdino) ---
@register_effect("OP02-065", "blocker", "[Blocker]")
def op02_065_mr3_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP02-065", "end_of_turn", "[End of Turn] You may trash 1 from hand: Set this active")
def op02_065_mr3_eot(game_state, player, card):
    """End of Turn: You may trash 1 card from hand to set this active."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    if player.hand and card.is_resting:
        options = []
        for i, hc in enumerate(player.hand):
            options.append({
                "id": str(i),
                "label": f"{hc.name} (Cost: {hc.cost or 0})",
                "card_id": hc.id,
                "card_name": hc.name,
            })
        game_state.pending_choice = PendingChoice(
            choice_id=f"mr3_eot_{_uuid.uuid4().hex[:8]}",
            choice_type="select_cards",
            prompt="Trash 1 card from hand to set Mr.3 active? (select 0 to skip)",
            options=options,
            min_selections=0,
            max_selections=1,
            source_card_id=card.id,
            source_card_name=card.name,
            callback_action="op02_065_optional_trash_set_active",
            callback_data={
                "player_id": player.player_id,
                "player_index": 0 if player is game_state.player1 else 1,
                "mr3_card_id": card.id,
            }
        )
        return True
    return False


# --- OP02-066: Impel Down All Stars ---
@register_effect("OP02-066", "on_play", "[Main] Trash 2 from hand: If Impel Down Leader, draw 2")
def op02_066_impel_down_all_stars(game_state, player, card):
    """[Main] Event: Trash 2 cards from hand. If Leader is Impel Down, draw 2."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    if len(player.hand) >= 2:
        options = []
        for i, hc in enumerate(player.hand):
            options.append({
                "id": str(i),
                "label": f"{hc.name} (Cost: {hc.cost or 0})",
                "card_id": hc.id,
                "card_name": hc.name,
            })
        game_state.pending_choice = PendingChoice(
            choice_id=f"idas_trash_{_uuid.uuid4().hex[:8]}",
            choice_type="select_cards",
            prompt="Choose 2 cards from hand to trash (Impel Down All Stars)",
            options=options,
            min_selections=2,
            max_selections=2,
            source_card_id=card.id,
            source_card_name=card.name,
            callback_action="op02_066_trash_then_draw",
            callback_data={
                "player_id": player.player_id,
                "player_index": 0 if player is game_state.player1 else 1,
            }
        )
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
    card.has_blocker = False
    for c in player.cards_in_play:
        if getattr(c, 'name', '') == 'Blugori':
            c.has_blocker = True
            c._continuous_blocker = True
    return True


# --- OP02-076: Shiryu ---
@register_effect("OP02-076", "on_play", "[On Play] DON!! -1: K.O. opponent's cost 1 or less")
def op02_076_shiryu(game_state, player, card):
    """On Play: Return 1 DON to DON deck to K.O. opponent's cost 1 or less Character."""
    result = optional_don_return(game_state, player, 1, source_card=card,
                                 after_callback="op02_076_shiryu_effect",
                                 after_callback_data={"source_card_id": card.id})
    if not result:
        return True  # Pending choice
    return True  # Can't pay, fizzled


# --- OP02-078: Daifugo ---
@register_effect("OP02-078", "on_play", "[On Play] DON!! -2: Play SMILE cost 3 or less from hand")
def op02_078_daifugo(game_state, player, card):
    """On Play: Return 2 DON to play a SMILE cost 3 or less from hand."""
    result = optional_don_return(game_state, player, 2, source_card=card,
                                 after_callback="op02_078_daifugo_effect",
                                 after_callback_data={"source_card_id": card.id})
    if not result:
        return True  # Pending choice
    return True  # Can't pay, fizzled


# --- OP02-079: Douglas Bullet ---
@register_effect("OP02-079", "on_play", "[On Play] DON!! -1: Rest opponent's cost 4 or less")
def op02_079_bullet(game_state, player, card):
    """On Play: Return 1 DON to rest opponent's cost 4 or less Character."""
    result = optional_don_return(game_state, player, 1, source_card=card,
                                 after_callback="op02_079_bullet_effect",
                                 after_callback_data={"source_card_id": card.id})
    if not result:
        return True  # Pending choice
    return True  # Can't pay, fizzled


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
    result = optional_don_return(game_state, player, 8, source_card=card,
                                 after_callback="op02_082_world_effect",
                                 after_callback_data={"source_card_id": card.id})
    if not result:
        return True  # Pending choice
    return True  # Can't pay, fizzled


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
    result = optional_don_return(game_state, player, 1, source_card=card,
                                 after_callback="op02_085_magellan_effect",
                                 after_callback_data={"source_card_id": card.id})
    if not result:
        return True  # Pending choice
    return True  # Can't pay, fizzled


@register_effect("OP02-085", "on_ko", "[Opponent's Turn] [On K.O.] Opponent returns 2 DON")
def op02_085_magellan_ko(game_state, player, card):
    """On K.O. during opponent's turn: Opponent returns 2 DON."""
    opponent = get_opponent(game_state, player)
    for _ in range(min(2, len(opponent.don_pool))):
        if opponent.don_pool:
            opponent.don_pool.pop()
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
        add_don_from_deck(player, 1)
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
        add_don_from_deck(player, 1)
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
    result = optional_don_return(game_state, player, 2, source_card=card,
                                 after_callback="op02_120_uta_effect",
                                 after_callback_data={"source_card_id": card.id})
    if not result:
        return True  # Pending choice
    return True  # Can't pay, fizzled


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


# =============================================================================
# MISSING EVENT & STAGE EFFECTS — OP02
# =============================================================================

# --- OP02-021: Seaquake (Red Event) ---
@register_effect("OP02-021", "on_play", "[Main] If Whitebeard Pirates leader, K.O. opponent's 3000 power or less")
def op02_021_seaquake(game_state, player, card):
    """[Main] If your Leader has the Whitebeard Pirates type, K.O. up to 1 opponent
    Character with 3000 power or less."""
    if not (player.leader and 'whitebeard pirates' in (player.leader.card_origin or '').lower()):
        return False
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (c.power or 0) + getattr(c, 'power_modifier', 0) <= 3000]
    if not targets:
        return True
    return create_ko_choice(game_state, player, targets, source_card=card,
                             prompt="Seaquake: K.O. opponent's Character with 3000 power or less")


# --- OP02-045: Three Sword Style Oni Giri (Green Counter Event) ---
@register_effect("OP02-045", "counter", "[Counter] Leader/Char gains +6000; play vanilla cost 3 or less from hand")
def op02_045_oni_giri(game_state, player, card):
    """[Counter] Up to 1 of your Leader or Character cards gains +6000 power during this
    battle. Then, play up to 1 Character card with a cost of 3 or less and no base
    effect from your hand."""
    # Apply +6000 to leader (most common counter target); avoids needing a choice
    # so the single pending choice can be used for the play-character step
    if player.leader:
        player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 6000
        game_state._log(f"Oni Giri: {player.leader.name} gains +6000 power")
    # Find vanilla characters (no effect text) with cost ≤ 3 in hand
    vanilla_targets = [
        c for c in player.hand
        if c.card_type == 'CHARACTER'
        and not (c.effect or '').strip()
        and (c.cost or 0) <= 3
    ]
    if vanilla_targets:
        return create_play_from_hand_choice(
            game_state, player, vanilla_targets, source_card=card,
            prompt="Oni Giri: Play a vanilla Character (no base effect, cost 3 or less) from hand"
        )
    return True


# --- OP02-046: Diable Jambe Venaison Shoot (Green Main Event) ---
@register_effect("OP02-046", "on_play", "[Main] K.O. opponent's rested Character with cost 4 or less")
def op02_046_diable_jambe(game_state, player, card):
    """[Main] K.O. up to 1 of your opponent's rested Characters with a cost of 4 or less."""
    opponent = get_opponent(game_state, player)
    targets = [
        c for c in opponent.cards_in_play
        if c.is_resting and (c.cost or 0) <= 4
    ]
    if not targets:
        return True
    return create_ko_choice(game_state, player, targets, source_card=card,
                             prompt="Diable Jambe: K.O. opponent's rested Character with cost 4 or less")


# --- OP02-047: Paradise Totsuka (Green Main Event) ---
@register_effect("OP02-047", "on_play", "[Main] Rest opponent's Character with cost 4 or less")
def op02_047_paradise_totsuka(game_state, player, card):
    """[Main] Rest up to 1 of your opponent's Characters with a cost of 4 or less."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (c.cost or 0) <= 4 and not c.is_resting]
    if not targets:
        return True
    return create_rest_choice(game_state, player, targets, source_card=card,
                               prompt="Paradise Totsuka: Rest opponent's Character with cost 4 or less")


# --- OP02-048: Land of Wano (Green Stage) ---
@register_effect("OP02-048", "activate", "[Activate: Main] Trash Land of Wano card from hand, rest Stage: set 1 DON active")
def op02_048_land_of_wano_stage(game_state, player, card):
    """[Activate: Main] You may trash 1 {Land of Wano} type card from your hand and
    rest this Stage: Set up to 1 of your DON!! cards as active."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    if card.is_resting:
        return False
    if getattr(card, 'main_activated_this_turn', False):
        return False
    # Need a Land of Wano card in hand to pay cost
    wano_cards = [
        c for c in player.hand
        if 'land of wano' in (getattr(c, 'card_origin', '') or '').lower()
    ]
    if not wano_cards:
        return False
    # Prompt player to choose which Land of Wano card to trash
    options = []
    for i, hc in enumerate(wano_cards):
        options.append({
            "id": str(i),
            "label": f"{hc.name} (Cost: {hc.cost or 0})",
            "card_id": hc.id,
            "card_name": hc.name,
        })
    game_state.pending_choice = PendingChoice(
        choice_id=f"wano_stage_{_uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Choose a Land of Wano card from hand to trash (to set 1 DON active)",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback_action="op02_048_trash_wano",
        callback_data={
            "player_id": player.player_id,
            "player_index": 0 if player is game_state.player1 else 1,
            "target_cards": [{"id": hc.id, "name": hc.name} for hc in wano_cards],
            "stage_card_id": card.id,
        }
    )
    return True


# --- OP02-067: Arabesque Brick Fist (Blue Main Event) ---
@register_effect("OP02-067", "on_play", "[Main] Return a Character with cost 4 or less to owner's hand")
def op02_067_arabesque(game_state, player, card):
    """[Main] Return up to 1 Character with a cost of 4 or less to the owner's hand."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (c.cost or 0) <= 4]
    if not targets:
        return True
    return create_return_to_hand_choice(game_state, player, targets, source_card=card,
                                        prompt="Arabesque Brick Fist: Return opponent's cost 4 or less Character to hand")


# --- OP02-068: Gum-Gum Rain (Blue Counter Event) ---
@register_effect("OP02-068", "counter", "[Counter] May trash 1 from hand: Leader/Char gains +3000 power")
def op02_068_gum_gum_rain(game_state, player, card):
    """[Counter] You may trash 1 card from your hand: Up to 1 of your Leader or
    Character cards gains +3000 power during this battle."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    if not player.hand:
        return True  # No hand cards — optional cost can't be paid, effect fizzles
    # Prompt player to select 1 card to trash
    options = []
    for i, hc in enumerate(player.hand):
        options.append({
            "id": str(i),
            "label": f"{hc.name} (Cost: {hc.cost or 0})",
            "card_id": hc.id,
            "card_name": hc.name,
        })
    game_state.pending_choice = PendingChoice(
        choice_id=f"ggrain_trash_{_uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Trash 1 card from hand to give +3000 power (select 0 to skip)",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback_action="op02_068_trash_then_power",
        callback_data={
            "player_id": player.player_id,
            "player_index": 0 if player is game_state.player1 else 1,
        }
    )
    return True


# --- OP02-069: DEATH WINK (Blue Counter Event) ---
@register_effect("OP02-069", "counter", "[Counter] Leader/Char gains +6000; draw to 2 cards in hand")
def op02_069_death_wink(game_state, player, card):
    """[Counter] Up to 1 of your Leader or Character cards gains +6000 power during
    this battle. Then, draw cards so that you have 2 cards in your hand."""
    # Apply +6000 to leader directly (avoid PendingChoice so drawing can happen inline)
    if player.leader:
        player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 6000
        game_state._log(f"DEATH WINK: {player.leader.name} gains +6000 power")
    # Draw to 2 cards in hand
    current = len(player.hand)
    if current < 2:
        draw_cards(player, 2 - current)
        game_state._log(f"DEATH WINK: drew {2 - current} card(s) to reach 2 in hand")
    return True


# --- OP02-070: New Kama Land (Blue Stage) ---
@register_effect("OP02-070", "activate", "[Activate: Main] Rest stage: if Ivankov leader, draw 1, trash 1, may trash 3 more")
def op02_070_new_kama_land(game_state, player, card):
    """[Activate: Main] You may rest this Stage: If your Leader is [Emporio.Ivankov],
    draw 1 card and trash 1 card from your hand. Then, trash up to 3 cards from hand."""
    if card.is_resting:
        return False
    if getattr(card, 'main_activated_this_turn', False):
        return False
    if not (player.leader and 'ivankov' in player.leader.name.lower()):
        return False
    # Pay cost: rest this Stage
    card.is_resting = True
    card.main_activated_this_turn = True
    # Draw 1, then trash 1 (required), then trash up to 3 more (optional)
    draw_cards(player, 1)
    from ...game_engine import PendingChoice
    import uuid as _uuid
    if not player.hand:
        game_state._log("New Kama Land: drew 1 card")
        return True

    if len(player.hand) == 1:
        trashed = player.hand.pop()
        player.trash.append(trashed)
        game_state._log(f"{player.name} trashed {trashed.name}")
        return True

    options = []
    for i, hc in enumerate(player.hand):
        options.append({
            "id": str(i),
            "label": f"{hc.name} (Cost: {hc.cost or 0})",
            "card_id": hc.id,
            "card_name": hc.name,
        })
    game_state.pending_choice = PendingChoice(
        choice_id=f"new_kama_{_uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Choose 1 card from hand to trash, then you may trash up to 3 more",
        options=options,
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback_action="op02_070_required_then_optional",
        callback_data={
            "player_id": player.player_id,
            "player_index": 0 if player is game_state.player1 else 1,
            "source_card_id": card.id,
            "source_card_name": card.name,
        }
    )
    return True


# --- OP02-089: Judgment of Hell (Purple Counter Event) ---
@register_effect("OP02-089", "counter", "[Counter] DON!! -1: Give up to 2 opponent leader/chars -2000 power each")
def op02_089_judgment_of_hell(game_state, player, card):
    """[Counter] DON!! −1: Give up to a total of 2 of your opponent's Leader or
    Characters −2000 power each during this battle."""
    result = optional_don_return(game_state, player, 1, source_card=card,
                                 after_callback="op02_089_judgment_effect",
                                 after_callback_data={"source_card_id": card.id})
    if not result:
        return True  # Pending choice
    return True  # Can't pay, fizzled


# --- OP02-090: Hydra (Purple Main Event) ---
@register_effect("OP02-090", "on_play", "[Main] DON!! -1: Give opponent char -3000 power; return it to owner's hand")
def op02_090_hydra(game_state, player, card):
    """[Main] DON!! −1: Give up to 1 of your opponent's Characters −3000 power during
    this turn. Then, return that Character to the owner's hand."""
    result = optional_don_return(game_state, player, 1, source_card=card,
                                 after_callback="op02_090_hydra_effect",
                                 after_callback_data={"source_card_id": card.id})
    if not result:
        return True  # Pending choice
    return True  # Can't pay, fizzled


# --- OP02-091: Venom Road (Purple Main Event) ---
@register_effect("OP02-091", "on_play", "[Main] Add 1 DON!! from deck and set as active")
def op02_091_venom_road(game_state, player, card):
    """[Main] Add up to 1 DON!! card from your DON!! deck and set it as active."""
    add_don_from_deck(player, 1, set_active=True)
    game_state._log("Venom Road: added 1 DON from deck (active)")
    return True


# --- OP02-117: Ice Age (Black Main Event) ---
@register_effect("OP02-117", "on_play", "[Main] Give opponent's Character -5 cost this turn")
def op02_117_ice_age(game_state, player, card):
    """[Main] Give up to 1 of your opponent's Characters −5 cost during this turn."""
    opponent = get_opponent(game_state, player)
    targets = opponent.cards_in_play[:]
    if not targets:
        return True
    return create_cost_reduction_choice(
        game_state, player, targets, -5,
        source_card=card,
        prompt="Ice Age: Choose opponent's Character to give -5 cost this turn"
    )


# --- OP02-118: Yasakani Sacred Jewel (Black Counter Event) ---
@register_effect("OP02-118", "counter", "[Counter] May trash 1 from hand: chosen Character cannot be K.O.'d this battle")
def op02_118_yasakani(game_state, player, card):
    """[Counter] You may trash 1 card from your hand: Select up to 1 of your Characters.
    The selected Character cannot be K.O.'d during this battle."""
    # Optional: "you may trash 1" — only protect if there are characters to protect
    if not player.cards_in_play:
        return True
    # Auto-trash 1 from hand if available (pays the optional cost)
    if player.hand:
        trash_from_hand(player, 1, game_state, card)
    # Create choice for which own character to protect
    return create_set_active_choice(
        game_state, player, player.cards_in_play[:],
        source_card=card,
        callback_action="protect_from_ko_in_battle",
        prompt="Yasakani Sacred Jewel: Choose your Character that cannot be K.O.'d this battle"
    )


# --- OP02-119: Meteor Volcano (Black Main Event) ---
@register_effect("OP02-119", "on_play", "[Main] K.O. opponent's Character with cost 1 or less")
def op02_119_meteor_volcano(game_state, player, card):
    """[Main] K.O. up to 1 of your opponent's Characters with a cost of 1 or less."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (c.cost or 0) <= 1]
    if not targets:
        return True
    return create_ko_choice(game_state, player, targets, source_card=card,
                             prompt="Meteor Volcano: K.O. opponent's Character with cost 1 or less")
