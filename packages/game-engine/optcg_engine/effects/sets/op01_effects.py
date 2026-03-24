"""
Hardcoded effects for OP01 cards.
"""

import random

from ..hardcoded import (
    add_don_from_deck, create_bottom_deck_choice, create_ko_choice, create_own_character_choice,
    create_play_from_hand_choice, create_power_effect_choice, create_rest_choice, create_return_to_hand_choice,
    create_set_active_choice, create_target_choice, create_trash_choice, draw_cards, get_opponent,
    register_effect, reorder_top_cards, return_don_to_deck, search_top_cards, trash_from_hand,
)


# --- OP01-029: Radical Beam!! ---
@register_effect("OP01-029", "counter", "[Counter] +2000 power. If 2 or fewer Life, +4000 total")
def op01_029_radical_beam(game_state, player, card):
    # Card text: [Counter] Up to 1 of your Leader or Character cards gains +2000 power during
    # this battle. If you have 2 or fewer Life cards, it gains an additional +2000 power.
    amount = 4000 if len(player.life_cards) <= 2 else 2000
    targets = ([player.leader] if player.leader else []) + player.cards_in_play
    if not targets:
        return True
    return create_power_effect_choice(
        game_state, player, targets, amount,
        source_card=card,
        prompt=f"Choose Leader or Character to give +{amount} power"
    )


# --- OP01-119: Thunder Bagua ---
@register_effect("OP01-119", "counter", "[Counter] +4000 power. If 2 or fewer Life, add 1 active DON instead")
def op01_119_thunder_bagua(game_state, player, card):
    # Card text: [Counter] Up to 1 of your Leader or Character cards gains +4000 power during
    # this battle. If you have 2 or fewer Life cards, instead add 1 DON!! card from your DON!!
    # deck and set it as active.
    if len(player.life_cards) <= 2:
        player.don_pool.append("active")
        return True
    targets = ([player.leader] if player.leader else []) + player.cards_in_play
    if not targets:
        return True
    return create_power_effect_choice(
        game_state, player, targets, 4000,
        source_card=card,
        prompt="Choose Leader or Character to give +4000 power"
    )


# =============================================================================
# LEADER CARD EFFECTS - OP01 (Romance Dawn)
# =============================================================================

# --- OP01-001: Roronoa Zoro (Leader) ---
# --- OP01-001: Roronoa Zoro (Leader) ---
@register_effect("OP01-001", "continuous", "[DON!! x1] [Your Turn] All Characters +1000 power")
def op01_001_zoro_leader(game_state, player, card):
    # Card text: [DON!! x1] [Your Turn] All of your Characters gain +1000 power.
    if game_state.current_player is not player:
        return True  # Not your turn
    if getattr(card, 'attached_don', 0) >= 1:
        for char in player.cards_in_play:
            char.power_modifier = getattr(char, 'power_modifier', 0) + 1000
    return True


# --- OP01-002: Trafalgar Law (Leader) ---
@register_effect("OP01-002", "activate", "[Activate: Main] Rest 2 DON: If 5 Characters, return 1, play different color cost 5")
def op01_002_law_leader(game_state, player, card):
    # Card text: [Activate: Main] [Once Per Turn] ➁: If you have 5 Characters,
    # return 1 of your Characters to hand. Then play up to 1 Character cost 5 or less
    # from hand that is a different color than the returned Character.
    if getattr(card, 'main_activated_this_turn', False):
        return False
    active_count = player.don_pool.count("active")
    if active_count < 2:
        return False
    if len(player.cards_in_play) < 5:
        return False
    # Rest 2 active DON
    rested = 0
    for i in range(len(player.don_pool)):
        if player.don_pool[i] == "active" and rested < 2:
            player.don_pool[i] = "rested"
            rested += 1
    card.main_activated_this_turn = True
    return create_own_character_choice(
        game_state, player, player.cards_in_play,
        source_card=card,
        callback_action="law_leader_return_then_play",
        prompt="Choose your Character to return to hand (then play cost 5 or less different color)"
    )


# --- OP01-003: Monkey.D.Luffy (Leader) ---
@register_effect("OP01-003", "activate", "[Activate: Main] Rest 4 DON: Set Supernovas/Straw Hat Crew cost 5 active +1000")
def op01_003_luffy_leader(game_state, player, card):
    # Card text: [Activate: Main] [Once Per Turn] ➃: Set up to 1 of your {Supernovas}
    # or {Straw Hat Crew} type Character cards with cost 5 or less as active.
    # It gains +1000 power during this turn.
    if getattr(card, 'main_activated_this_turn', False):
        return False
    active_count = player.don_pool.count("active")
    if active_count < 4:
        return False
    # Rest 4 active DON
    rested = 0
    for i in range(len(player.don_pool)):
        if player.don_pool[i] == "active" and rested < 4:
            player.don_pool[i] = "rested"
            rested += 1
    card.main_activated_this_turn = True
    targets = [c for c in player.cards_in_play
               if c.is_resting
               and (c.cost or 0) <= 5
               and ('supernovas' in (c.card_origin or '').lower()
                    or 'straw hat crew' in (c.card_origin or '').lower())]
    if not targets:
        return True  # Cost paid, no valid targets — effect resolves as no-op
    return create_set_active_choice(
        game_state, player, targets,
        prompt="Choose your Supernovas/Straw Hat Crew cost 5 or less to set active (+1000 power this turn)",
        source_card=card,
        callback_action="set_active_with_power",
        extra_data={"power": 1000},
    )


# --- OP01-031: Kouzuki Oden (Leader) ---
@register_effect("OP01-031", "activate", "[Activate: Main] Trash Land of Wano: Set up to 2 DON as active")
def op01_031_oden_leader(game_state, player, card):
    # Card text: [Activate: Main] [Once Per Turn] You can trash 1 {Land of Wano} type card
    # from your hand: Set up to 2 of your DON!! cards as active.
    if getattr(card, 'main_activated_this_turn', False):
        return False
    wano_cards = [c for c in player.hand
                  if 'land of wano' in (c.card_origin or '').lower()]
    if not wano_cards:
        return False
    from ...game_engine import PendingChoice
    import uuid
    options = []
    for i, c in enumerate(wano_cards):
        options.append({"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})",
                        "card_id": c.id, "card_name": c.name})
    game_state.pending_choice = PendingChoice(
        choice_id=f"oden_trash_wano_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Choose a Land of Wano card from your hand to trash (then set up to 2 DON!! as active)",
        options=options,
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback_action="oden_trash_wano",
        callback_data={"player_id": player.player_id,
                       "leader_id": card.id,
                       "wano_cards": [{"id": c.id, "name": c.name} for c in wano_cards]},
    )
    card.main_activated_this_turn = True
    return True


# --- OP01-060: Donquixote Doflamingo (Leader) ---
@register_effect("OP01-060", "on_attack", "[DON!! x2] [When Attacking] Rest 1 DON: Reveal top, play Warlord cost 4 rested")
def op01_060_doffy_leader(game_state, player, card):
    # Card text: [DON!! x2] [When Attacking] ➀: Reveal 1 card from top of deck.
    # If it is a {The Seven Warlords of the Sea} type Character card with cost 4 or less,
    # you may play that card rested.
    if getattr(card, 'attached_don', 0) < 2:
        return False
    active_count = player.don_pool.count("active")
    if active_count < 1:
        return False
    # Rest 1 DON (the ➀ cost)
    for i in range(len(player.don_pool)):
        if player.don_pool[i] == "active":
            player.don_pool[i] = "rested"
            break
    if not player.deck:
        return True
    revealed = player.deck[0]  # Peek, don't remove
    origin = (revealed.card_origin or '').lower()
    is_eligible = ('seven warlords' in origin
                   and getattr(revealed, 'card_type', '') == 'CHARACTER'
                   and (revealed.cost or 0) <= 4)
    game_state._log(f"Doflamingo reveals: {revealed.name} ({revealed.card_type}, Cost {revealed.cost or 0})")
    if is_eligible:
        # Let player choose whether to play it
        from ...game_engine import PendingChoice
        import uuid
        options = [
            {"id": "play", "label": f"Play {revealed.name} rested"},
            {"id": "skip", "label": "Leave on top of deck"},
        ]
        game_state.pending_choice = PendingChoice(
            choice_id=f"doffy_reveal_{uuid.uuid4().hex[:8]}",
            choice_type="select_target",
            prompt=f"Doflamingo: Revealed {revealed.name} (Seven Warlords, Cost {revealed.cost or 0}). Play rested?",
            options=options,
            min_selections=1,
            max_selections=1,
            source_card_id=card.id,
            source_card_name=card.name,
            callback_action="doffy_reveal_play",
            callback_data={"player_id": player.player_id,
                           "player_index": 0 if game_state.current_player is player else 1},
        )
    else:
        game_state._log(f"Doflamingo: {revealed.name} is not eligible, remains on top of deck")
    return True


# --- OP01-061: Kaido (Leader) ---
@register_effect("OP01-061", "on_opponent_ko", "[DON!! x1] [Your Turn] When opponent Character K.O.'d, add 1 active DON")
def op01_061_kaido_leader(game_state, player, card):
    # Card text: [DON!! x1] [Your Turn] [Once Per Turn] When your opponent's Character is K.O.'d,
    # add up to 1 DON!! card from your DON!! deck and set it as active.
    if getattr(card, 'attached_don', 0) < 1:
        return False
    if game_state.current_player is not player:
        return False  # Your Turn only
    if getattr(card, 'main_activated_this_turn', False):
        return False  # Once Per Turn
    if len(player.don_pool) < 10:
        player.don_pool.append("active")
        game_state._log(f"Kaido: {player.name} adds 1 active DON!! from DON deck")
    card.main_activated_this_turn = True
    return True


# --- OP01-062: Crocodile (Leader) ---
@register_effect("OP01-062", "on_event", "[DON!! x1] When you activate Event, draw 1 if 4 or less hand")
def op01_062_croc_leader(game_state, player, card):
    # Card text: [DON!! x1] When you activate an Event, you may draw 1 card if you have
    # 4 or less cards in your hand.
    if getattr(card, 'attached_don', 0) < 1:
        return False
    if getattr(card, 'main_activated_this_turn', False):
        return False  # Once Per Turn
    if len(player.hand) <= 4:
        draw_cards(player, 1)
        game_state._log(f"Crocodile: {player.name} draws 1 card (on_event)")
        card.main_activated_this_turn = True
        return True
    return False


# --- OP01-091: King (Leader) ---
@register_effect("OP01-091", "continuous", "[Your Turn] If 10 DON!! on field, opponent Characters −1000 power")
def op01_091_king_leader(game_state, player, card):
    # Card text: [Your Turn] If you have 10 DON!! cards on your field,
    # give all of your opponent's Characters −1000 power.
    if game_state.current_player is not player:
        return True  # Not your turn
    if len(player.don_pool) >= 10:
        opponent = get_opponent(game_state, player)
        for char in opponent.cards_in_play:
            char.power_modifier = getattr(char, 'power_modifier', 0) - 1000
        return True
    return False


# =============================================================================
# CHARACTER EFFECTS - OP01 (ROMANCE DAWN)
# =============================================================================

# --- OP01-004: Usopp ---
@register_effect("OP01-004", "on_event_activated", "[DON!! x1] [Your Turn] [Once Per Turn] Draw 1 when opponent activates Event")
def op01_004_usopp(game_state, player, card):
    # Card text: [DON!! x1] [Your Turn] [Once Per Turn] Draw 1 card when your opponent activates an Event.
    if game_state.current_player is not player:
        return True  # Only fires on your turn
    if getattr(card, 'main_activated_this_turn', False):
        return True  # Once per turn
    if getattr(card, 'attached_don', 0) >= 1:
        draw_cards(player, 1)
        card.main_activated_this_turn = True
        return True
    return True


# --- OP01-005: Uta ---
@register_effect("OP01-005", "on_play", "[On Play] Add red cost 3 or less Character from trash to hand")
def op01_005_uta(game_state, player, card):
    # Card text: [On Play] Add up to 1 red Character card other than [Uta] with a cost of 3 or less
    # from your trash to your hand.
    valid = [c for c in player.trash
             if getattr(c, 'card_type', '') == 'CHARACTER'
             and any('red' == col.lower() for col in (getattr(c, 'colors', []) or []))
             and (getattr(c, 'cost', 0) or 0) <= 3
             and 'uta' not in (getattr(c, 'name', '') or '').lower()]
    if valid:
        return create_target_choice(
            game_state, player, valid, source_card=card,
            prompt="Choose a red cost 3 or less Character from trash to add to hand",
            callback_action="return_from_trash_to_hand",
        )
    return True


# --- OP01-006: Otama ---
@register_effect("OP01-006", "on_play", "[On Play] Give opponent's Character -2000 power")
def op01_006_otama(game_state, player, card):
    """Give up to 1 of opponent's Characters -2000 power during this turn."""
    opponent = get_opponent(game_state, player)
    if opponent.cards_in_play:
        return create_power_effect_choice(
            game_state, player, opponent.cards_in_play, -2000,
            source_card=card,
            prompt="Choose an opponent's Character to give -2000 power"
        )
    return False


# --- OP01-007: Caribou ---
@register_effect("OP01-007", "on_ko", "[On K.O.] K.O. opponent's Character with 4000 or less power")
def op01_007_caribou(game_state, player, card):
    """On K.O.: K.O. up to 1 of opponent's Characters with 4000 power or less."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if (getattr(c, 'power', 0) or 0) + getattr(c, 'power_modifier', 0) <= 4000]
    if targets:
        return create_ko_choice(
            game_state, player, targets, source_card=card,
            prompt="Choose opponent's 4000 power or less Character to KO"
        )
    return False


# --- OP01-008: Cavendish ---
@register_effect("OP01-008", "on_play", "[On Play] Add Life to hand: Gain Rush")
def op01_008_cavendish(game_state, player, card):
    """Add 1 card from Life to hand: This Character gains Rush this turn."""
    if player.life_cards:
        life = player.life_cards.pop()
        player.hand.append(life)
        card.has_rush = True
        return True
    return False


# --- OP01-009: Carrot ---
@register_effect("OP01-009", "trigger", "[Trigger] Play this card")
def op01_009_carrot(game_state, player, card):
    """Trigger: Play this card."""
    player.cards_in_play.append(card)
    return True


# --- OP01-011: Gordon ---
@register_effect("OP01-011", "on_play", "[On Play] Place 1 card from hand at deck bottom, then draw 1")
def op01_011_gordon(game_state, player, card):
    # Card text: [On Play] Place up to 1 card from your hand at the bottom of your deck:
    # Draw 1 card.
    if not player.hand:
        return True  # No cards in hand — effect resolves as no-op
    return create_bottom_deck_choice(
        game_state, player, player.hand,
        source_card=card,
        prompt="Choose a card from your hand to place at the bottom of your deck (then draw 1), or skip",
        callback_action="bottom_deck_then_draw",
        min_selections=0,
    )


# --- OP01-013: Sanji ---
@register_effect("OP01-013", "activate", "[Activate: Main] [Once Per Turn] Add Life: +2000 and gain 2 rested DON")
def op01_013_sanji(game_state, player, card):
    """Once Per Turn: Add 1 Life to hand: This Character gains +2000 power and up to 2 rested DON."""
    if hasattr(card, 'op01_013_used') and card.op01_013_used:
        return False
    if player.life_cards:
        life = player.life_cards.pop()
        player.hand.append(life)
        card.power_modifier = getattr(card, 'power_modifier', 0) + 2000
        # Attach up to 2 rested DON to this character (set them active by attaching)
        activated = 0
        for i, status in enumerate(player.don_pool):
            if status == "rested" and activated < 2:
                player.don_pool[i] = "active"
                activated += 1
        card.attached_don = getattr(card, 'attached_don', 0) + activated
        card.main_activated_this_turn = True
        return True
    return False


# --- OP01-014: Jinbe ---
@register_effect("OP01-014", "blocker", "[Blocker]")
def op01_014_jinbe_blocker(game_state, player, card):
    """Blocker: Can redirect attacks."""
    card.is_blocker = True
    return True


@register_effect("OP01-014", "on_block", "[DON!! x1] [On Block] Play red cost 2 or less Character from hand")
def op01_014_jinbe_block(game_state, player, card):
    """DON x1: On block, play red Character cost 2 or less from hand."""
    if getattr(card, 'attached_don', 0) >= 1:
        red_chars = [c for c in player.hand
                     if getattr(c, 'card_type', '') == 'CHARACTER'
                     and any('red' == col.lower() for col in (getattr(c, 'colors', []) or []))
                     and (getattr(c, 'cost', 0) or 0) <= 2]
        if red_chars:
            return create_play_from_hand_choice(
                game_state, player, red_chars,
                source_card=card,
                prompt="Choose a red cost 2 or less Character to play"
            )
    return False


# --- OP01-015: Tony Tony.Chopper ---
@register_effect("OP01-015", "on_attack", "[DON!! x1] [When Attacking] You may trash 1 card from hand: add SHC cost 4 or less from trash to hand")
def op01_015_chopper(game_state, player, card):
    # Card text: [DON!! x1] [When Attacking] You may trash 1 card from your hand:
    # Add up to 1 {Straw Hat Crew} type Character other than [Tony Tony.Chopper] with
    # cost 4 or less from your trash to your hand.
    if getattr(card, 'attached_don', 0) < 1:
        return True
    if not player.hand:
        return True
    from ...game_engine import PendingChoice
    import uuid
    options = []
    for i, c in enumerate(player.hand):
        options.append({"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})",
                        "card_id": c.id, "card_name": c.name})
    game_state.pending_choice = PendingChoice(
        choice_id=f"chopper_trash_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="(Optional) Trash 1 card from hand to search your trash for a Straw Hat Crew character",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback_action="chopper_trash_then_pick_shc",
        callback_data={"player_id": player.player_id,
                       "hand_cards": [{"id": c.id, "name": c.name} for c in player.hand]},
    )
    return True


# --- OP01-016: Nami ---
@register_effect("OP01-016", "on_play", "[On Play] Look at top 5: add up to 1 SHC card other than Nami to hand")
def op01_016_nami(game_state, player, card):
    """On Play: Look at top 5, reveal up to 1 Straw Hat Crew card (not Nami) to hand, rest to bottom."""
    def shc_not_nami(c):
        return ('straw hat crew' in (c.card_origin or '').lower()
                and 'nami' not in (c.name or '').lower())
    return search_top_cards(game_state, player, 5, add_count=1, filter_fn=shc_not_nami,
                            source_card=card,
                            prompt="Nami: Choose up to 1 Straw Hat Crew card (not Nami) from top 5 to add to hand")


# --- OP01-017: Nico Robin ---
@register_effect("OP01-017", "on_attack", "[DON!! x1] K.O. opponent's 3000 power or less Character")
def op01_017_robin(game_state, player, card):
    """DON x1: K.O. up to 1 of opponent's Characters with 3000 power or less."""
    if getattr(card, 'attached_don', 0) >= 1:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play
                   if (getattr(c, 'power', 0) or 0) + getattr(c, 'power_modifier', 0) <= 3000]
        if targets:
            return create_ko_choice(
                game_state, player, targets, source_card=card,
                prompt="Choose opponent's 3000 power or less Character to KO"
            )
    return False


# --- OP01-019: Bartolomeo ---
@register_effect("OP01-019", "blocker", "[Blocker]")
def op01_019_barto_blocker(game_state, player, card):
    """Blocker: Can redirect attacks."""
    card.is_blocker = True
    return True


@register_effect("OP01-019", "continuous", "[DON!! x2] [Opponent's Turn] +3000 power")
def op01_019_barto_power(game_state, player, card):
    # Card text: [DON!! x2] [Opponent's Turn] This Character gains +3000 power.
    if game_state.current_player is player:
        return True  # Not opponent's turn — effect doesn't apply
    if getattr(card, 'attached_don', 0) >= 2:
        card.power_modifier = 3000  # SET, not accumulate — prevents double-application on recalc
    return True


# --- OP01-020: Hyogoro ---
@register_effect("OP01-020", "activate", "[Activate: Main] Rest this: Leader or Character +2000 power")
def op01_020_hyogoro(game_state, player, card):
    """Rest this Character: Up to 1 Leader or Character gains +2000 power."""
    if not getattr(card, 'is_resting', False):
        card.is_resting = True
        targets = [player.leader] + player.cards_in_play if player.leader else player.cards_in_play
        if targets:
            return create_power_effect_choice(
                game_state, player, targets, 2000,
                source_card=card,
                prompt="Choose Leader or Character to give +2000 power"
            )
        return True
    return False


# --- OP01-021: Franky ---
@register_effect("OP01-021", "continuous", "[DON!! x1] Can attack active Characters")
def op01_021_franky(game_state, player, card):
    """DON x1: This Character can attack opponent's active Characters."""
    if getattr(card, 'attached_don', 0) >= 1:
        card.can_attack_active = True
        return True
    return False


# --- OP01-022: Brook ---
@register_effect("OP01-022", "on_attack", "[DON!! x1] Give up to 2 opponent's Characters -2000 power")
def op01_022_brook(game_state, player, card):
    """DON x1: Give up to 2 of opponent's Characters -2000 power during this turn."""
    if getattr(card, 'attached_don', 0) < 1:
        return False
    opponent = get_opponent(game_state, player)
    targets = opponent.cards_in_play[:]
    if not targets:
        return True
    count = min(2, len(targets))
    return create_power_effect_choice(
        game_state, player, targets, -2000,
        source_card=card,
        prompt=f"Choose up to {count} of opponent's Characters to give -2000 power",
        min_selections=0,
        max_selections=count,
    )


# --- OP01-024: Monkey.D.Luffy ---
@register_effect("OP01-024", "continuous", "[DON!! x2] Cannot be K.O.'d in battle by Strike attribute")
def op01_024_luffy_strike(game_state, player, card):
    """DON x2: This Character cannot be K.O.'d in battle by Strike attribute Characters."""
    if getattr(card, 'attached_don', 0) >= 2:
        card.cannot_be_ko_by_strike = True
    return True


@register_effect("OP01-024", "activate", "[Activate: Main] [Once Per Turn] Gain up to 2 rested DON")
def op01_024_luffy_don(game_state, player, card):
    """Once Per Turn: Give this Character up to 2 rested DON cards."""
    if getattr(card, 'main_activated_this_turn', False):
        return False
    # Attach up to 2 rested DON from pool to this card
    attached = 0
    for i in range(len(player.don_pool)):
        if player.don_pool[i] == "rested" and attached < 2:
            card.attached_don = getattr(card, 'attached_don', 0) + 1
            attached += 1
    if attached > 0:
        card.main_activated_this_turn = True
        game_state._log(f"Luffy attaches {attached} rested DON to himself (now {card.attached_don} DON)")
        game_state._recalc_continuous_effects()
        return True
    return False


# --- OP01-025: Roronoa Zoro ---
@register_effect("OP01-025", "continuous", "[Rush]")
def op01_025_zoro(game_state, player, card):
    """Rush: Can attack on the turn played."""
    card.has_rush = True
    return True


# --- OP01-032: Ashura Doji ---
@register_effect("OP01-032", "continuous", "[DON!! x1] If opponent has 2+ rested Characters, +2000 power")
def op01_032_ashura(game_state, player, card):
    """DON x1: If opponent has 2+ rested Characters, this Character gains +2000 power."""
    if getattr(card, 'attached_don', 0) >= 1:
        opponent = get_opponent(game_state, player)
        rested = [c for c in opponent.cards_in_play if getattr(c, 'is_resting', False)]
        if len(rested) >= 2:
            card.power_modifier = 2000
            return True
    return False


# --- OP01-033: Izo ---
@register_effect("OP01-033", "on_play", "[On Play] Rest opponent's cost 4 or less Character")
def op01_033_izo(game_state, player, card):
    """Rest up to 1 of opponent's Characters with cost 4 or less."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if (getattr(c, 'cost', 0) or 0) <= 4 and not getattr(c, 'is_resting', False)]
    if targets:
        return create_rest_choice(game_state, player, targets, source_card=card,
                                 prompt="Choose opponent's cost 4 or less to rest")
    return False


# --- OP01-034: Inuarashi ---
@register_effect("OP01-034", "on_attack", "[DON!! x2] Set 1 DON as active")
def op01_034_inuarashi(game_state, player, card):
    """DON x2: Set up to 1 of your DON cards as active."""
    if getattr(card, 'attached_don', 0) >= 2:
        for i, status in enumerate(player.don_pool):
            if status == "rested":
                player.don_pool[i] = "active"
                return True
    return False


# --- OP01-035: Okiku ---
@register_effect("OP01-035", "on_attack", "[DON!! x1] [Once Per Turn] Rest opponent's cost 5 or less Character")
def op01_035_okiku(game_state, player, card):
    """DON x1, Once Per Turn: Rest up to 1 of opponent's Characters with cost 5 or less."""
    if hasattr(card, 'op01_035_used') and card.op01_035_used:
        return False
    if getattr(card, 'attached_don', 0) >= 1:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play
                   if (getattr(c, 'cost', 0) or 0) <= 5 and not getattr(c, 'is_resting', False)]
        if targets:
            card.op01_035_used = True
            return create_rest_choice(game_state, player, targets, source_card=card,
                                     prompt="Choose opponent's cost 5 or less to rest")
    return False


# --- OP01-038: Kanjuro ---
@register_effect("OP01-038", "on_attack", "[DON!! x1] K.O. opponent's rested cost 2 or less Character")
def op01_038_kanjuro_attack(game_state, player, card):
    """DON x1: K.O. up to 1 of opponent's rested Characters with cost 2 or less."""
    if getattr(card, 'attached_don', 0) >= 1:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play
                   if getattr(c, 'is_resting', False) and (getattr(c, 'cost', 0) or 0) <= 2]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's rested cost 2 or less to KO")
    return False


@register_effect("OP01-038", "on_ko", "[On K.O.] Opponent chooses 1 card from your hand; trash it")
def op01_038_kanjuro_ko(game_state, player, card):
    # Card text: [On K.O.] Your opponent looks at your hand and chooses 1 card to trash.
    if not player.hand:
        return True
    opponent = get_opponent(game_state, player)
    from ...game_engine import PendingChoice
    import uuid
    # Opponent picks blindly — show only card positions, not names
    options = [{"id": str(i), "label": f"Card #{i + 1}"}
               for i in range(len(player.hand))]
    game_state.pending_choice = PendingChoice(
        choice_id=f"kanjuro_ko_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt=f"Kanjuro's effect: Choose 1 card from {player.name}'s hand to trash (hidden)",
        options=options,
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback_action="kanjuro_opponent_trash",
        callback_data={"player_id": opponent.player_id,
                       "target_player_id": player.player_id,
                       "hand_cards": [{"id": c.id, "name": c.name} for c in player.hand]},
    )
    return True


# --- OP01-039: Killer ---
@register_effect("OP01-039", "blocker", "[Blocker]")
def op01_039_killer_blocker(game_state, player, card):
    """Blocker: Can redirect attacks."""
    card.is_blocker = True
    return True


@register_effect("OP01-039", "on_block", "[DON!! x1] [On Block] If 3+ Characters, draw 1")
def op01_039_killer_block(game_state, player, card):
    """DON x1: On block, if you have 3+ Characters, draw 1 card."""
    if getattr(card, 'attached_don', 0) >= 1:
        if len(player.cards_in_play) >= 3:
            draw_cards(player, 1)
            return True
    return False


# --- OP01-040: Kin'emon ---
@register_effect("OP01-040", "on_play", "[On Play] If Leader is Kouzuki Oden, play Akazaya Nine cost 3 or less")
def op01_040_kinemon_play(game_state, player, card):
    """If Leader is Kouzuki Oden, play Akazaya Nine Character cost 3 or less from hand."""
    if player.leader and 'kouzuki oden' in (getattr(player.leader, 'name', '') or '').lower():
        akazaya = [c for c in player.hand
                   if getattr(c, 'card_type', '') == 'CHARACTER'
                   and 'akazaya nine' in (c.card_origin or '').lower()
                   and (getattr(c, 'cost', 0) or 0) <= 3]
        if akazaya:
            return create_play_from_hand_choice(
                game_state, player, akazaya,
                source_card=card,
                prompt="Choose an Akazaya Nine cost 3 or less to play"
            )
    return True


@register_effect("OP01-040", "on_attack", "[DON!! x1] [Once Per Turn] Set Akazaya Nine cost 3 or less as active")
def op01_040_kinemon_attack(game_state, player, card):
    """DON x1, Once Per Turn: Set Akazaya Nine Character cost 3 or less as active."""
    if hasattr(card, 'op01_040_used') and card.op01_040_used:
        return False
    if getattr(card, 'attached_don', 0) >= 1:
        akazaya = [c for c in player.cards_in_play
                   if 'akazaya nine' in (c.card_origin or '').lower()
                   and (getattr(c, 'cost', 0) or 0) <= 3
                   and getattr(c, 'is_resting', False)]
        if akazaya:
            card.op01_040_used = True
            from ...game_engine import PendingChoice
            import uuid
            options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})",
                        "card_id": c.id, "card_name": c.name} for i, c in enumerate(akazaya)]
            game_state.pending_choice = PendingChoice(
                choice_id=f"kinemon_{uuid.uuid4().hex[:8]}",
                choice_type="select_target",
                prompt="Choose an Akazaya Nine cost 3 or less to set as active",
                options=options,
                min_selections=0,
                max_selections=1,
                source_card_id=card.id,
                source_card_name=card.name,
                callback_action="set_active",
                callback_data={"player_id": player.player_id,
                               "target_cards": [{"id": c.id, "name": c.name} for c in akazaya]},
            )
            return True
    return False


# --- OP01-041: Kouzuki Momonosuke ---
@register_effect("OP01-041", "activate", "[Activate: Main] Rest 1 DON and this: Search for Wano card")
def op01_041_momonosuke(game_state, player, card):
    """Rest 1 DON and this Character: Look at 5 cards, add 1 Land of Wano card to hand."""
    if getattr(card, 'is_resting', False):
        return False
    active_idx = next((i for i, s in enumerate(player.don_pool) if s == "active"), None)
    if active_idx is None:
        return False
    player.don_pool[active_idx] = "rested"
    card.is_resting = True
    return search_top_cards(
        game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: 'land of wano' in (c.card_origin or '').lower(),
        source_card=card,
        prompt="Look at top 5: choose 1 Land of Wano card to add to hand",
    )


# --- OP01-042: Komurasaki ---
@register_effect("OP01-042", "on_play", "[On Play] Rest 3 DON: If Leader is Oden, set Wano cost 3 or less as active")
def op01_042_komurasaki(game_state, player, card):
    """Rest 3 DON: If Leader is Kouzuki Oden, set Land of Wano Character cost 3 or less as active."""
    active_count = player.don_pool.count("active")
    if active_count >= 3 and player.leader and 'kouzuki oden' in (getattr(player.leader, 'name', '') or '').lower():
        rested = 0
        for i, status in enumerate(player.don_pool):
            if status == "active" and rested < 3:
                player.don_pool[i] = "rested"
                rested += 1
        wano = [c for c in player.cards_in_play
                if 'land of wano' in (c.card_origin or '').lower()
                and (getattr(c, 'cost', 0) or 0) <= 3
                and getattr(c, 'is_resting', False)]
        if wano:
            from ...game_engine import PendingChoice
            import uuid
            options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})",
                        "card_id": c.id, "card_name": c.name} for i, c in enumerate(wano)]
            game_state.pending_choice = PendingChoice(
                choice_id=f"komurasaki_{uuid.uuid4().hex[:8]}",
                choice_type="select_target",
                prompt="Choose a Land of Wano cost 3 or less Character to set as active",
                options=options,
                min_selections=0,
                max_selections=1,
                callback_action="set_active",
                callback_data={"player_id": player.player_id,
                               "target_cards": [{"id": c.id, "name": c.name} for c in wano]},
            )
        return True
    return False


# --- OP01-044: Shachi ---
@register_effect("OP01-044", "blocker", "[Blocker]")
def op01_044_shachi_blocker(game_state, player, card):
    """Blocker: Can redirect attacks."""
    card.is_blocker = True
    return True


@register_effect("OP01-044", "on_play", "[On Play] If you don't have Penguin, play Penguin from hand")
def op01_044_shachi_play(game_state, player, card):
    """If you don't have Penguin in play, play up to 1 Penguin from hand."""
    has_penguin = any('penguin' in (getattr(c, 'name', '') or '').lower() for c in player.cards_in_play)
    if not has_penguin:
        penguins = [c for c in player.hand if 'penguin' in (getattr(c, 'name', '') or '').lower()]
        if penguins:
            return create_play_from_hand_choice(
                game_state, player, penguins,
                source_card=card,
                prompt="Choose Penguin to play from hand"
            )
    return True


# --- OP01-046: Denjiro ---
@register_effect("OP01-046", "on_attack", "[DON!! x1] If Leader is Oden, set 2 DON as active")
def op01_046_denjiro(game_state, player, card):
    """DON x1: If Leader is Kouzuki Oden, set up to 2 DON cards as active."""
    if getattr(card, 'attached_don', 0) >= 1:
        if player.leader and 'kouzuki oden' in (getattr(player.leader, 'name', '') or '').lower():
            activated = 0
            for i, status in enumerate(player.don_pool):
                if status == "rested" and activated < 2:
                    player.don_pool[i] = "active"
                    activated += 1
            return True
    return False


# --- OP01-047: Trafalgar Law ---
@register_effect("OP01-047", "blocker", "[Blocker]")
def op01_047_law_blocker(game_state, player, card):
    """Blocker: Can redirect attacks."""
    card.is_blocker = True
    return True


@register_effect("OP01-047", "on_play", "[On Play] Return 1 Character to hand: Play cost 3 or less Character")
def op01_047_law_play(game_state, player, card):
    """Return 1 Character to hand: Play up to 1 Character with cost 3 or less from hand."""
    own_chars = [c for c in player.cards_in_play if c != card]
    if own_chars:
        return create_own_character_choice(
            game_state, player, own_chars,
            source_card=card,
            callback_action="law_return_then_play_cost3",
            prompt="Choose Character to return to hand (then play cost 3 or less)"
        )
    return False


# --- OP01-048: Nekomamushi ---
@register_effect("OP01-048", "on_play", "[On Play] Rest opponent's cost 3 or less Character")
def op01_048_nekomamushi(game_state, player, card):
    """Rest up to 1 of opponent's Characters with cost 3 or less."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if (getattr(c, 'cost', 0) or 0) <= 3 and not getattr(c, 'is_resting', False)]
    if targets:
        return create_rest_choice(game_state, player, targets, source_card=card,
                                 prompt="Choose opponent's cost 3 or less to rest")
    return False


# --- OP01-049: Bepo ---
@register_effect("OP01-049", "on_attack", "[DON!! x1] Play Heart Pirates cost 4 or less from hand")
def op01_049_bepo(game_state, player, card):
    """DON x1: Play up to 1 Heart Pirates Character other than Bepo cost 4 or less from hand."""
    if getattr(card, 'attached_don', 0) >= 1:
        heart_pirates = [c for c in player.hand
                         if getattr(c, 'card_type', '') == 'CHARACTER'
                         and 'heart pirates' in (c.card_origin or '').lower()
                         and (getattr(c, 'cost', 0) or 0) <= 4
                         and 'bepo' not in (getattr(c, 'name', '') or '').lower()]
        if heart_pirates:
            return create_play_from_hand_choice(
                game_state, player, heart_pirates,
                source_card=card,
                prompt="Choose Heart Pirates cost 4 or less to play"
            )
    return False


# --- OP01-050: Penguin ---
@register_effect("OP01-050", "blocker", "[Blocker]")
def op01_050_penguin_blocker(game_state, player, card):
    """Blocker: Can redirect attacks."""
    card.is_blocker = True
    return True


@register_effect("OP01-050", "on_play", "[On Play] If you don't have Shachi, play Shachi from hand")
def op01_050_penguin_play(game_state, player, card):
    """If you don't have Shachi in play, play up to 1 Shachi from hand."""
    has_shachi = any('shachi' in (getattr(c, 'name', '') or '').lower() for c in player.cards_in_play)
    if not has_shachi:
        shachis = [c for c in player.hand if 'shachi' in (getattr(c, 'name', '') or '').lower()]
        if shachis:
            return create_play_from_hand_choice(
                game_state, player, shachis,
                source_card=card,
                prompt="Choose Shachi to play"
            )
    return True


# --- OP01-051: Eustass"Captain"Kid ---
@register_effect("OP01-051", "continuous", "[DON!! x1] [Opponent's Turn] If rested, opponent must attack this card")
def op01_051_kid_taunt(game_state, player, card):
    # Card text: [DON!! x1] [Opponent's Turn] If this Character is rested, your opponent cannot
    # attack any of your other Characters or your Leader.
    if game_state.current_player is player:
        return True  # Not opponent's turn
    if getattr(card, 'attached_don', 0) >= 1 and getattr(card, 'is_resting', False):
        card.has_taunt = True
    return True


@register_effect("OP01-051", "activate", "[Activate: Main] [Once Per Turn] Rest this: Play cost 3 or less Character")
def op01_051_kid_activate(game_state, player, card):
    """Once Per Turn: Rest this Character: Play up to 1 Character cost 3 or less from hand."""
    if hasattr(card, 'op01_051_used') and card.op01_051_used:
        return False
    if not getattr(card, 'is_resting', False):
        card.is_resting = True
        playable = [c for c in player.hand
                    if getattr(c, 'card_type', '') == 'CHARACTER'
                    and (getattr(c, 'cost', 0) or 0) <= 3]
        card.op01_051_used = True
        if playable:
            return create_play_from_hand_choice(
                game_state, player, playable,
                source_card=card,
                prompt="Choose a cost 3 or less Character to play"
            )
        return True
    return False


# --- OP01-052: Raizo ---
@register_effect("OP01-052", "on_attack", "[When Attacking] [Once Per Turn] If 2+ rested Characters, draw 1")
def op01_052_raizo(game_state, player, card):
    """Once Per Turn: If you have 2+ rested Characters, draw 1 card."""
    if hasattr(card, 'op01_052_used') and card.op01_052_used:
        return False
    rested = [c for c in player.cards_in_play if getattr(c, 'is_resting', False)]
    if len(rested) >= 2:
        draw_cards(player, 1)
        card.op01_052_used = True
        return True
    return False


# --- OP01-054: X.Drake ---
@register_effect("OP01-054", "on_play", "[On Play] K.O. opponent's rested cost 4 or less Character")
def op01_054_drake(game_state, player, card):
    """K.O. up to 1 of opponent's rested Characters with cost 4 or less."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if getattr(c, 'is_resting', False) and (getattr(c, 'cost', 0) or 0) <= 4]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                                prompt="Choose opponent's rested cost 4 or less Character to K.O.")
    return False


# --- OP01-063: Arlong ---
@register_effect("OP01-063", "activate", "[DON!! x1] [Activate: Main] Rest this: If revealed Event, remove 1 Life")
def op01_063_arlong(game_state, player, card):
    """DON x1: Rest this: Opponent reveals 1 random card. If Event, may place 1 of opponent's Life at deck bottom."""
    if getattr(card, 'attached_don', 0) >= 1 and not getattr(card, 'is_resting', False):
        if getattr(card, 'main_activated_this_turn', False):
            return False
        card.is_resting = True
        card.main_activated_this_turn = True
        opponent = get_opponent(game_state, player)
        if not opponent.hand:
            game_state._log(f"Arlong: Opponent has no cards in hand.")
            return True
        import random
        revealed = random.choice(opponent.hand)
        game_state._log(f"Arlong: Opponent reveals {revealed.name} ({getattr(revealed, 'card_type', '?')})")
        if getattr(revealed, 'card_type', '') == 'EVENT' and opponent.life_cards:
            from ...game_engine import PendingChoice
            import uuid
            game_state.pending_choice = PendingChoice(
                choice_id=f"arlong_{uuid.uuid4().hex[:8]}",
                choice_type="select_target",
                prompt=f"Arlong: Revealed {revealed.name} (Event). Place 1 of opponent's Life at bottom of deck?",
                options=[
                    {"id": "yes", "label": "Yes - remove 1 Life"},
                    {"id": "no", "label": "No - skip"},
                ],
                min_selections=1,
                max_selections=1,
                source_card_id=card.id,
                source_card_name=card.name,
                callback_action="arlong_remove_life",
                callback_data={"player_id": player.player_id,
                               "player_index": 0 if game_state.current_player is player else 1},
            )
        else:
            game_state._log(f"Arlong: Revealed card is not an Event — no effect.")
        return True
    return False


# --- OP01-064: Alvida ---
@register_effect("OP01-064", "on_attack", "[DON!! x1] Trash 1: Return opponent's cost 3 or less Character to hand")
def op01_064_alvida(game_state, player, card):
    """DON x1: Trash 1 from hand: Return opponent's Character cost 3 or less to owner's hand."""
    if getattr(card, 'attached_don', 0) < 1 or not player.hand:
        return False
    from ...game_engine import PendingChoice
    import uuid
    options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})",
                "card_id": c.id, "card_name": c.name} for i, c in enumerate(player.hand)]
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
    game_state.pending_choice = PendingChoice(
        choice_id=f"alvida_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Choose a card from hand to trash (cost to activate Alvida's effect)",
        options=options,
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback_action="alvida_trash_then_return",
        callback_data={"player_id": player.player_id,
                       "hand_cards": [{"id": c.id, "name": c.name} for c in player.hand],
                       "return_targets": [{"id": c.id, "name": c.name} for c in targets]},
    )
    return True


# --- OP01-067: Crocodile ---
@register_effect("OP01-067", "continuous", "[Banish] and [DON!! x1] Blue Events -1 cost")
def op01_067_crocodile(game_state, player, card):
    """Banish effect. DON x1: Blue Events in your hand get -1 cost."""
    card.has_banish = True
    if getattr(card, 'attached_don', 0) >= 1:
        for c in player.hand:
            if (getattr(c, 'card_type', '') == 'EVENT'
                    and any('blue' == col.lower() for col in (getattr(c, 'colors', []) or []))):
                c.cost_modifier = -1
    return True


# --- OP01-068: Gecko Moria ---
@register_effect("OP01-068", "continuous", "[Your Turn] If 5+ cards in hand, gain Double Attack")
def op01_068_moria(game_state, player, card):
    # Card text: [Your Turn] This Character gains [Double Attack] if you have 5 or more cards in hand.
    # Double Attack is CONDITIONAL (not innate) — always set explicitly based on conditions.
    if game_state.current_player is player and len(player.hand) >= 5:
        card.has_doubleattack = True
    else:
        card.has_doubleattack = False
    return True


# --- OP01-069: Caesar Clown ---
@register_effect("OP01-069", "on_ko", "[On K.O.] Play Smiley from deck")
def op01_069_caesar(game_state, player, card):
    # Card text: [On K.O.] Play up to 1 [Smiley] from your deck. Then, shuffle your deck.
    smileys = [c for c in player.deck if 'smiley' in (getattr(c, 'name', '') or '').lower()]
    if not smileys:
        return True
    from ...game_engine import PendingChoice
    import uuid
    options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})",
                "card_id": c.id, "card_name": c.name} for i, c in enumerate(smileys)]
    game_state.pending_choice = PendingChoice(
        choice_id=f"caesar_smiley_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Choose a Smiley from your deck to play",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback_action="search_play_to_field",
        callback_data={"player_id": player.player_id,
                       "target_cards": [{"id": c.id, "name": c.name} for c in smileys],
                       "shuffle_after": True},
    )
    return True


# --- OP01-070: Dracule Mihawk ---
@register_effect("OP01-070", "on_play", "[On Play] Place cost 7 or less Character at deck bottom")
def op01_070_mihawk(game_state, player, card):
    """Place up to 1 Character with cost 7 or less at the bottom of the owner's deck."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 7]
    if targets:
        return create_bottom_deck_choice(game_state, player, targets, source_card=card,
                                        prompt="Choose opponent's cost 7 or less to place at deck bottom")
    return False


# --- OP01-071: Jinbe ---
@register_effect("OP01-071", "on_play", "[On Play] Place cost 3 or less Character at deck bottom")
def op01_071_jinbe(game_state, player, card):
    """Place up to 1 Character with cost 3 or less at the bottom of the owner's deck."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
    if targets:
        return create_bottom_deck_choice(game_state, player, targets, source_card=card,
                                        prompt="Choose opponent's cost 3 or less to place at deck bottom")
    return False


# --- OP01-072: Smiley ---
@register_effect("OP01-072", "continuous", "[DON!! x1] [Your Turn] +1000 power per card in hand")
def op01_072_smiley(game_state, player, card):
    # Card text: [DON!! x1] [Your Turn] This Character gains +1000 power for every card in your hand.
    if game_state.current_player is not player:
        return True  # Not your turn
    if getattr(card, 'attached_don', 0) >= 1:
        card.power_modifier = 1000 * len(player.hand)
    return True


# --- OP01-073: Donquixote Doflamingo ---
@register_effect("OP01-073", "blocker", "[Blocker]")
def op01_073_doffy_blocker(game_state, player, card):
    """Blocker: Can redirect attacks."""
    card.is_blocker = True
    return True


@register_effect("OP01-073", "on_play", "[On Play] Look at 5 cards from deck, place at top or bottom")
def op01_073_doffy_play(game_state, player, card):
    """Look at 5 cards from top of deck and place them at top or bottom in any order."""
    return reorder_top_cards(game_state, player, 5, source_card=card, allow_top=True)


# --- OP01-074: Bartholomew Kuma ---
@register_effect("OP01-074", "blocker", "[Blocker]")
def op01_074_kuma_blocker(game_state, player, card):
    """Blocker: Can redirect attacks."""
    card.is_blocker = True
    return True


@register_effect("OP01-074", "on_ko", "[On K.O.] Play Pacifista cost 4 or less from hand")
def op01_074_kuma_ko(game_state, player, card):
    """On K.O.: Play up to 1 Pacifista with cost 4 or less from hand."""
    pacifistas = [c for c in player.hand
                  if 'pacifista' in (getattr(c, 'name', '') or '').lower()
                  and (getattr(c, 'cost', 0) or 0) <= 4]
    if pacifistas:
        return create_play_from_hand_choice(
            game_state, player, pacifistas,
            source_card=card,
            prompt="Choose a Pacifista cost 4 or less to play"
        )
    return True


# --- OP01-075: Pacifista ---
@register_effect("OP01-075", "blocker", "[Blocker]")
def op01_075_pacifista(game_state, player, card):
    """Blocker: Can redirect attacks."""
    card.is_blocker = True
    return True


# --- OP01-077: Buggy ---
@register_effect("OP01-077", "on_play", "[On Play] Look at 5 cards from deck, place at top or bottom")
def op01_077_perona(game_state, player, card):
    """Look at 5 cards from top of deck and place them at top or bottom in any order."""
    return reorder_top_cards(game_state, player, 5, source_card=card, allow_top=True)


# --- OP01-078: Boa Hancock ---
@register_effect("OP01-078", "blocker", "[Blocker]")
def op01_078_hancock_blocker(game_state, player, card):
    """Blocker."""
    card.is_blocker = True
    return True


@register_effect("OP01-078", "on_attack", "[DON!! x1] [When Attacking] Draw 1 if 5 or less in hand")
def op01_078_hancock_attack(game_state, player, card):
    """DON x1: Draw 1 card if you have 5 or less cards in hand."""
    if getattr(card, 'attached_don', 0) >= 1 and len(player.hand) <= 5:
        draw_cards(player, 1)
        game_state._log(f"Boa Hancock: {player.name} draws 1 card")
    return True


@register_effect("OP01-078", "on_block", "[DON!! x1] [On Block] Draw 1 if 5 or less in hand")
def op01_078_hancock_block(game_state, player, card):
    """DON x1: Draw 1 card if you have 5 or less cards in hand."""
    if getattr(card, 'attached_don', 0) >= 1 and len(player.hand) <= 5:
        draw_cards(player, 1)
        game_state._log(f"Boa Hancock: {player.name} draws 1 card")
    return True


# --- OP01-079: Ms. All Sunday ---
@register_effect("OP01-079", "blocker", "[Blocker]")
def op01_079_allsunday_blocker(game_state, player, card):
    """Blocker."""
    card.is_blocker = True
    return True


@register_effect("OP01-079", "on_ko", "[On K.O.] If Baroque Works leader, add 1 Event from trash to hand")
def op01_079_allsunday_ko(game_state, player, card):
    """[On K.O.] If Baroque Works leader, add 1 Event from trash to hand."""
    leader_origin = (player.leader.card_origin or '').lower() if player.leader else ''
    if 'baroque works' in leader_origin:
        events = [c for c in player.trash if getattr(c, 'card_type', '') == 'EVENT']
        if events:
            from ...game_engine import PendingChoice
            import uuid
            options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})",
                        "card_id": c.id, "card_name": c.name} for i, c in enumerate(events)]
            game_state.pending_choice = PendingChoice(
                choice_id=f"allsunday_{uuid.uuid4().hex[:8]}",
                choice_type="select_target",
                prompt="Ms. All Sunday: Choose an Event from trash to add to hand",
                options=options,
                min_selections=0,
                max_selections=1,
                source_card_id=card.id,
                source_card_name=card.name,
                callback_action="return_from_trash_to_hand",
                callback_data={"player_id": player.player_id,
                               "target_cards": [{"id": c.id, "name": c.name} for c in events]},
            )
    return True


@register_effect("OP01-079", "on_block", "[On Block] Draw 2 and trash 2 from hand")
def op01_079_hancock_block(game_state, player, card):
    """On block, draw 2 cards and trash 2 cards from hand."""
    draw_cards(player, 2)
    trash_from_hand(player, 2, game_state, card)
    return True


# --- OP01-080: Miss Doublefinger(Zala) ---
@register_effect("OP01-080", "on_ko", "[On K.O.] Draw 1 card")
def op01_080_doublefinger(game_state, player, card):
    # Card text: [On K.O.] Draw 1 card.
    draw_cards(player, 1)
    return True


# --- OP01-092: Otohime ---
@register_effect("OP01-092", "on_play", "[On Play] Add Fish-Man/Mermaid cost 3 or less from trash to hand")
def op01_092_otohime(game_state, player, card):
    """Add up to 1 Fish-Man or Mermaid Character cost 3 or less from trash to hand."""
    valid = [c for c in player.trash
             if getattr(c, 'card_type', '') == 'CHARACTER'
             and (getattr(c, 'cost', 0) or 0) <= 3
             and ('fish-man' in (c.card_origin or '').lower()
                  or 'mermaid' in (c.card_origin or '').lower())]
    if valid:
        from ...game_engine import PendingChoice
        import uuid
        options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})",
                    "card_id": c.id, "card_name": c.name} for i, c in enumerate(valid)]
        game_state.pending_choice = PendingChoice(
            choice_id=f"otohime_{uuid.uuid4().hex[:8]}",
            choice_type="select_target",
            prompt="Choose a Fish-Man or Mermaid Character cost 3 or less to add to hand",
            options=options,
            min_selections=0,
            max_selections=1,
            source_card_id=card.id,
            source_card_name=card.name,
            callback_action="return_from_trash_to_hand",
            callback_data={"player_id": player.player_id,
                           "target_cards": [{"id": c.id, "name": c.name} for c in valid]},
        )
    return True


# --- OP01-093: Ulti ---
@register_effect("OP01-093", "on_play", "[On Play] ①: Add 1 rested DON from DON deck")
def op01_093_ulti(game_state, player, card):
    # Card text: [On Play] ① (You may rest the specified number of DON!! cards in your cost area.):
    # Add up to 1 DON!! card from your DON!! deck and rest it.
    active_count = player.don_pool.count("active")
    if active_count < 1 or len(player.don_pool) >= 10:
        return True  # Can't pay or DON pool full
    from ...game_engine import PendingChoice
    import uuid
    game_state.pending_choice = PendingChoice(
        choice_id=f"ulti_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Ulti: Rest 1 DON to add 1 rested DON from DON deck?",
        options=[
            {"id": "yes", "label": "Yes - rest 1 DON, gain 1 rested DON"},
            {"id": "no", "label": "No - skip"},
        ],
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback_action="ulti_rest_don_add",
        callback_data={"player_id": player.player_id},
    )
    return True


# --- OP01-094: Kaido (Character) ---
@register_effect("OP01-094", "on_play", "[On Play] DON!! −6: If Animal Kingdom Pirates leader, K.O. all Characters except this")
def op01_094_kaido_char(game_state, player, card):
    # Card text: [On Play] DON!! −6: If your Leader has the {Animal Kingdom Pirates} type,
    # K.O. all Characters other than this Character.
    total_don = len(player.don_pool) + sum(getattr(c, 'attached_don', 0) for c in player.cards_in_play)
    if getattr(player.leader, 'attached_don', 0):
        total_don += player.leader.attached_don
    if total_don < 6:
        return True  # Can't pay cost — effect doesn't fire
    auto = return_don_to_deck(game_state, player, 6, source_card=card,
                              after_callback="op01_094_kaido_ko_all",
                              after_callback_data={"source_card_id": card.id})
    if not auto:
        return True  # Pending choice — callback handles the rest
    # DON auto-paid, apply effect immediately
    leader_origin = (player.leader.card_origin or '').lower() if player.leader else ''
    if 'animal kingdom pirates' in leader_origin:
        opponent = get_opponent(game_state, player)
        for c in opponent.cards_in_play[:]:
            opponent.cards_in_play.remove(c)
            opponent.trash.append(c)
        for c in player.cards_in_play[:]:
            if c != card:
                player.cards_in_play.remove(c)
                player.trash.append(c)
    return True


# --- OP01-095: Kyoshirou ---
@register_effect("OP01-095", "on_play", "[On Play] Draw 1 if 8 or more DON on field")
def op01_095_kyoshirou(game_state, player, card):
    # Card text: [On Play] Draw 1 card if you have 8 or more DON!! cards on your field.
    if len(player.don_pool) >= 8:
        draw_cards(player, 1)
    return True


# --- OP01-096: King (Character) ---
@register_effect("OP01-096", "on_play", "[On Play] DON!! −2: K.O. opponent's cost 3 or less AND cost 2 or less")
def op01_096_king_char(game_state, player, card):
    # Card text: [On Play] DON!! −2: K.O. up to 1 of your opponent's Characters with a cost of
    # 3 or less and up to 1 of your opponent's Characters with a cost of 2 or less.
    total_don = len(player.don_pool) + sum(getattr(c, 'attached_don', 0) for c in player.cards_in_play)
    if getattr(player.leader, 'attached_don', 0):
        total_don += player.leader.attached_don
    if total_don < 2:
        return True  # Can't pay cost
    auto = return_don_to_deck(game_state, player, 2, source_card=card,
                              after_callback="op01_096_king_ko",
                              after_callback_data={"player_id": player.player_id})
    if not auto:
        return True  # Pending choice
    # DON auto-paid, apply effect — first KO cost 3 or less
    opponent = get_opponent(game_state, player)
    targets_3 = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
    if targets_3:
        from ...game_engine import PendingChoice
        import uuid
        options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})",
                    "card_id": c.id, "card_name": c.name} for i, c in enumerate(targets_3)]
        game_state.pending_choice = PendingChoice(
            choice_id=f"king_ko1_{uuid.uuid4().hex[:8]}",
            choice_type="select_target",
            prompt="King: Choose opponent's cost 3 or less Character to K.O.",
            options=options,
            min_selections=0,
            max_selections=1,
            source_card_id=card.id,
            source_card_name=card.name,
            callback_action="king_ko_then_ko2",
            callback_data={"player_id": player.player_id,
                           "target_cards": [{"id": c.id, "name": c.name} for c in targets_3]},
        )
    else:
        # No cost 3 targets, try cost 2 directly
        targets_2 = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
        if targets_2:
            return create_ko_choice(game_state, player, targets_2, source_card=card,
                                   prompt="King: Choose opponent's cost 2 or less Character to K.O.")
    return True


# --- OP01-097: Queen (Character) ---
@register_effect("OP01-097", "on_play", "[On Play] DON!! −1: Gain Rush, give opponent's Character −2000 power")
def op01_097_queen_char(game_state, player, card):
    # Card text: [On Play] DON!! −1: This Character gains [Rush] during this turn. Then, give
    # up to 1 of your opponent's Characters −2000 power during this turn.
    total_don = len(player.don_pool) + sum(getattr(c, 'attached_don', 0) for c in player.cards_in_play)
    if getattr(player.leader, 'attached_don', 0):
        total_don += player.leader.attached_don
    if total_don < 1:
        return True  # Can't pay cost
    auto = return_don_to_deck(game_state, player, 1, source_card=card,
                              after_callback="op01_097_queen_rush_power",
                              after_callback_data={"source_card_id": card.id})
    if not auto:
        return True  # Pending choice
    # DON auto-paid, apply effect
    card.has_rush = True
    opponent = get_opponent(game_state, player)
    if opponent.cards_in_play:
        return create_power_effect_choice(
            game_state, player, opponent.cards_in_play, -2000,
            source_card=card,
            prompt="Choose opponent's Character to give −2000 power"
        )
    return True


# --- OP01-098: Kurozumi Orochi ---
@register_effect("OP01-098", "on_play", "[On Play] Reveal Artificial Devil Fruit SMILE from deck, add to hand")
def op01_098_orochi(game_state, player, card):
    # Card text: [On Play] Reveal up to 1 [Artificial Devil Fruit SMILE] from your deck and add
    # it to your hand. Then, shuffle your deck.
    for i, deck_card in enumerate(player.deck):
        if 'artificial devil fruit smile' in (getattr(deck_card, 'name', '') or '').lower():
            found = player.deck.pop(i)
            player.hand.append(found)
            break
    random.shuffle(player.deck)
    return True


# --- OP01-099: Kurozumi Semimaru ---
@register_effect("OP01-099", "continuous", "[Continuous] Kurozumi Clan Characters cannot be K.O.'d in battle")
def op01_099_semimaru(game_state, player, card):
    """Kurozumi Clan type Characters other than Kurozumi Semimaru cannot be K.O.'d in battle."""
    for c in player.cards_in_play:
        if c is card:
            continue  # Semimaru himself is not protected
        origin = (c.card_origin or '').lower()
        if 'kurozumi clan' in origin:
            c.cannot_be_ko_in_battle = True
    return True


# --- OP01-100: Nefeltari Vivi ---
@register_effect("OP01-100", "on_attack", "[DON!! x2] Cannot be blocked by cost 5 or less Characters")
def op01_100_vivi(game_state, player, card):
    """DON x2: This attack cannot be blocked by Characters with cost 5 or less."""
    if getattr(card, 'attached_don', 0) >= 2:
        game_state.blocker_cost_limit = 5
        return True
    return False


# --- OP01-102: Jack ---
@register_effect("OP01-102", "on_attack", "[When Attacking] DON!! −1: Opponent trashes 1 from hand")
def op01_102_jack(game_state, player, card):
    """[When Attacking] DON!! −1: Your opponent trashes 1 card from their hand."""
    total_don = len(player.don_pool) + sum(getattr(c, 'attached_don', 0) for c in player.cards_in_play)
    if getattr(player.leader, 'attached_don', 0):
        total_don += player.leader.attached_don
    if total_don < 1:
        return True
    from ...game_engine import PendingChoice
    import uuid
    game_state.pending_choice = PendingChoice(
        choice_id=f"jack_don_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Jack: Pay DON!! −1 to force opponent to trash 1 from hand?",
        options=[
            {"id": "yes", "label": "Yes - pay DON!! −1"},
            {"id": "no", "label": "No - skip"},
        ],
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback_action="jack_don_then_trash",
        callback_data={"player_id": player.player_id},
    )
    return True


# --- OP01-104: Marco ---
@register_effect("OP01-104", "blocker", "[Blocker]")
def op01_104_marco_blocker(game_state, player, card):
    """Blocker: Can redirect attacks."""
    card.is_blocker = True
    return True


# --- OP01-104: Speed (Trigger) ---
@register_effect("OP01-104", "trigger", "[Trigger] Play this card")
def op01_104_speed_trigger(game_state, player, card):
    """[Trigger] Play this card."""
    player.cards_in_play.append(card)
    game_state._log(f"Trigger: {card.name} played to field")
    return True


# --- OP01-105: Bao Huang ---
@register_effect("OP01-105", "on_play", "[On Play] Opponent reveals 2 cards from hand")
def op01_105_bao_huang(game_state, player, card):
    """[On Play] Choose 2 cards from opponent's hand; opponent reveals those cards."""
    opponent = get_opponent(game_state, player)
    if len(opponent.hand) < 1:
        return True
    from ...game_engine import PendingChoice
    import uuid
    # Opponent chooses which 2 to reveal (blind pick by index)
    count = min(2, len(opponent.hand))
    options = [{"id": str(i), "label": f"Card #{i+1}"} for i in range(len(opponent.hand))]
    game_state.pending_choice = PendingChoice(
        choice_id=f"bao_huang_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt=f"Bao Huang: Choose {count} of opponent's cards to reveal",
        options=options,
        min_selections=count,
        max_selections=count,
        source_card_id=card.id,
        source_card_name=card.name,
        callback_action="bao_huang_reveal",
        callback_data={"player_index": 0 if game_state.player1 is player else 1},
    )
    return True


# --- OP01-106: Basil Hawkins ---
@register_effect("OP01-106", "on_play", "[On Play] Add 1 DON from deck and rest it")
def op01_106_basil_hawkins(game_state, player, card):
    # Card text: [On Play] Add up to 1 DON!! card from your DON!! deck and rest it.
    add_don_from_deck(player, 1, set_active=False)
    return True


# OP01-107: Babanuki — No effect (handled by parser keywords)


# --- OP01-108: Hitokiri Kamazo ---
@register_effect("OP01-108", "on_ko", "[On K.O.] DON!! −1: K.O. opponent's cost 5 or less Character")
def op01_108_kamazo(game_state, player, card):
    # Card text: [On K.O.] DON!! −1: K.O. up to 1 of your opponent's Characters with a cost of 5 or less.
    total_pool = len(player.don_pool)
    attached = sum(getattr(c, 'attached_don', 0) for c in player.cards_in_play)
    if getattr(player, 'leader', None):
        attached += getattr(player.leader, 'attached_don', 0)
    if total_pool + attached < 1:
        return True  # Can't pay DON cost
    auto = return_don_to_deck(game_state, player, 1, source_card=card,
                              after_callback="op01_108_kamazo_ko",
                              after_callback_data={"player_id": player.player_id})
    if auto:
        # DON auto-returned, proceed with KO choice inline
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 5]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's cost 5 or less Character to K.O.")
    return True


# --- OP01-109: Who's.Who ---
@register_effect("OP01-109", "blocker", "[Blocker]")
def op01_109_whoswho_blocker(game_state, player, card):
    # Card text: [Blocker]
    card.is_blocker = True
    return True


@register_effect("OP01-109", "continuous", "[DON!! x1] [Your Turn] If 8 or more DON, +1000 power")
def op01_109_whoswho_power(game_state, player, card):
    # Card text: [DON!! x1] [Your Turn] If you have 8 or more DON!! cards on your field,
    # this Character gains +1000 power.
    if game_state.current_player is not player:
        return True  # Not your turn
    if getattr(card, 'attached_don', 0) >= 1 and len(player.don_pool) >= 8:
        card.power_modifier = 1000
    return True


# --- OP01-111: Black Maria ---
@register_effect("OP01-111", "blocker", "[Blocker]")
def op01_111_blackmaria_blocker(game_state, player, card):
    # Card text: [Blocker]
    card.is_blocker = True
    return True


@register_effect("OP01-111", "on_block", "[On Block] DON!! −1: +1000 power this turn")
def op01_111_blackmaria_block(game_state, player, card):
    # Card text: [On Block] DON!! −1: This Character gains +1000 power during this turn.
    total_pool = len(player.don_pool)
    attached = sum(getattr(c, 'attached_don', 0) for c in player.cards_in_play)
    if getattr(player, 'leader', None):
        attached += getattr(player.leader, 'attached_don', 0)
    if total_pool + attached < 1:
        return False  # Can't pay DON cost
    # Prompt player to choose whether to use the effect
    from ...game_engine import PendingChoice
    import uuid
    game_state.pending_choice = PendingChoice(
        choice_id=f"blackmaria_opt_{uuid.uuid4().hex[:8]}",
        choice_type="yes_no",
        prompt="Black Maria: Pay DON!! −1 for +1000 power this turn?",
        options=[{"id": "yes", "label": "Yes"}, {"id": "no", "label": "No"}],
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback_action="blackmaria_optional_don",
        callback_data={"source_card_id": card.id,
                       "player_index": 0 if game_state.player1 is player else 1},
    )
    return True


# --- OP01-112: Page One (Character) ---
@register_effect("OP01-112", "activate", "[Activate: Main] [Once Per Turn] DON!! −1: Can attack active Characters")
def op01_112_pageone_char(game_state, player, card):
    # Card text: [Activate: Main] [Once Per Turn] DON!! −1: This Character can also attack your
    # opponent's active Characters during this turn.
    if getattr(card, 'main_activated_this_turn', False):
        return False
    total_pool = len(player.don_pool)
    attached = sum(getattr(c, 'attached_don', 0) for c in player.cards_in_play)
    if getattr(player, 'leader', None):
        attached += getattr(player.leader, 'attached_don', 0)
    if total_pool + attached < 1:
        return False  # Can't pay DON cost
    auto = return_don_to_deck(game_state, player, 1, source_card=card,
                              after_callback="op01_112_pageone_active",
                              after_callback_data={"source_card_id": card.id,
                                                   "player_id": player.player_id})
    if auto:
        # DON auto-returned, apply effect inline
        card.can_attack_active = True
    card.main_activated_this_turn = True
    return True


# --- OP01-114: X.Drake ---
@register_effect("OP01-114", "on_play", "[On Play] DON!! −1: Opponent trashes 1 from hand")
def op01_114_xdrake(game_state, player, card):
    """[On Play] DON!! −1: Your opponent trashes 1 card from their hand."""
    total_don = len(player.don_pool) + sum(getattr(c, 'attached_don', 0) for c in player.cards_in_play)
    if getattr(player.leader, 'attached_don', 0):
        total_don += player.leader.attached_don
    if total_don < 1:
        return True
    from ...game_engine import PendingChoice
    import uuid
    game_state.pending_choice = PendingChoice(
        choice_id=f"xdrake_don_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="X.Drake: Pay DON!! −1 to force opponent to trash 1 from hand?",
        options=[
            {"id": "yes", "label": "Yes - pay DON!! −1"},
            {"id": "no", "label": "No - skip"},
        ],
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback_action="xdrake_don_then_trash",
        callback_data={"player_id": player.player_id},
    )
    return True


# --- OP01-115: Elephant's Marchoo (EVENT) ---
@register_effect("OP01-115", "on_play", "[Main] K.O. opponent's cost 2 or less Character, then add 1 active DON")
def op01_115_elephants_marchoo(game_state, player, card):
    # Card text: [Main] K.O. up to 1 of your opponent's Characters with a cost of 2 or less,
    # then add up to 1 DON!! card from your DON!! deck and set it as active.
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
    add_don_from_deck(player, 1, set_active=True)
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                               prompt="Choose opponent's cost 2 or less Character to K.O.")
    return True


# --- OP01-117: Sheep's Horn (EVENT) ---
@register_effect("OP01-117", "on_play", "[Main] DON!! −1: Rest opponent's cost 6 or less Character")
def op01_117_sheeps_horn(game_state, player, card):
    # Card text: [Main] DON!! −1: Rest up to 1 of your opponent's Characters with a cost of 6 or less.
    total_pool = len(player.don_pool)
    attached = sum(getattr(c, 'attached_don', 0) for c in player.cards_in_play)
    if getattr(player, 'leader', None):
        attached += getattr(player.leader, 'attached_don', 0)
    if total_pool + attached < 1:
        return False  # Can't pay DON cost
    auto = return_don_to_deck(game_state, player, 1, source_card=card,
                              after_callback="op01_117_sheeps_horn_rest",
                              after_callback_data={"player_id": player.player_id})
    if auto:
        # DON auto-returned, proceed with rest choice inline
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play
                   if (getattr(c, 'cost', 0) or 0) <= 6 and not getattr(c, 'is_resting', False)]
        if targets:
            return create_rest_choice(game_state, player, targets, source_card=card,
                                     prompt="Choose opponent's cost 6 or less Character to rest")
    return True


# =============================================================================
# MISSING CARD IMPLEMENTATIONS
# =============================================================================

# --- OP01-101: Sasaki ---
@register_effect("OP01-101", "on_attack", "[DON!! x1] [When Attacking] Trash 1: Add 1 rested DON from DON deck")
def op01_101_sasaki(game_state, player, card):
    # Card text: [DON!! x1] [When Attacking] You may trash 1 card from your hand:
    # Add up to 1 DON!! card from your DON!! deck and rest it.
    if getattr(card, 'attached_don', 0) < 1 or not player.hand:
        return False
    from ...game_engine import PendingChoice
    import uuid
    options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})",
                "card_id": c.id, "card_name": c.name} for i, c in enumerate(player.hand)]
    game_state.pending_choice = PendingChoice(
        choice_id=f"sasaki_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="(Optional) Trash 1 card from hand to add 1 rested DON!! from DON deck",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback_action="sasaki_optional_trash_then_don",
        callback_data={"player_id": player.player_id,
                       "hand_cards": [{"id": c.id, "name": c.name} for c in player.hand]},
    )
    return True


# --- OP01-113: Holedem ---
@register_effect("OP01-113", "on_ko", "[On K.O.] Add 1 rested DON from DON deck")
def op01_113_holedem(game_state, player, card):
    # Card text: [On K.O.] Add up to 1 DON!! card from your DON!! deck and rest it.
    add_don_from_deck(player, 1, set_active=False)
    return True


# --- OP01-120: Shanks ---
@register_effect("OP01-120", "on_attack", "[Rush] [When Attacking] Opponent cannot activate Blocker with 2000 or less power")
def op01_120_shanks(game_state, player, card):
    # Card text: [Rush] [When Attacking] Your opponent cannot activate a [Blocker] Character
    # that has 2000 or less power during this battle.
    game_state.blocker_power_minimum = 2001
    return True


# --- OP01-037: Kawamatsu ---
@register_effect("OP01-037", "trigger", "[Trigger] Play this card")
def op01_037_kawamatsu(game_state, player, card):
    # Card text: [Trigger] Play this card.
    player.cards_in_play.append(card)
    return True


# --- OP01-082: Monet ---
@register_effect("OP01-082", "trigger", "[Trigger] Play this card")
def op01_082_monet(game_state, player, card):
    # Card text: [Trigger] Play this card.
    player.cards_in_play.append(card)
    return True


# --- OP01-083: Mr.1(Daz.Bonez) ---
@register_effect("OP01-083", "continuous", "[DON!! x1] [Your Turn] If Baroque Works leader, +1000 per 2 Events in trash")
def op01_083_mr1(game_state, player, card):
    # Card text: [DON!! x1] [Your Turn] If your Leader has the {Baroque Works} type, this
    # Character gains +1000 power for every 2 Events in your trash.
    if game_state.current_player is not player:
        return True  # Not your turn
    if getattr(card, 'attached_don', 0) >= 1:
        leader_origin = (player.leader.card_origin or '').lower() if player.leader else ''
        if 'baroque works' in leader_origin:
            event_count = sum(1 for c in player.trash if getattr(c, 'card_type', '') == 'EVENT')
            power_gain = (event_count // 2) * 1000
            if power_gain > 0:
                card.power_modifier = power_gain
    return True


# --- OP01-084: Mr.2.Bon.Kurei(Bentham) ---
@register_effect("OP01-084", "on_attack", "[DON!! x1] [When Attacking] Look at 5 top cards, add Baroque Works Event to hand")
def op01_084_mr2(game_state, player, card):
    # Card text: [DON!! x1] [When Attacking] Look at 5 cards from the top of your deck; reveal
    # up to 1 {Baroque Works} type Event card and add it to your hand. Then, place the rest at
    # the bottom of your deck in any order.
    if getattr(card, 'attached_don', 0) >= 1 and player.deck:
        return search_top_cards(
            game_state, player, look_count=5, add_count=1,
            filter_fn=lambda c: (getattr(c, 'card_type', '') == 'EVENT'
                                  and 'baroque works' in (c.card_origin or '').lower()),
            source_card=card,
            prompt="Look at top 5: choose 1 Baroque Works Event to add to hand",
        )
    return True


# --- OP01-085: Mr.3(Galdino) ---
@register_effect("OP01-085", "on_play", "[On Play] If Baroque Works leader, opponent's Character cost 4 or less cannot attack")
def op01_085_mr3(game_state, player, card):
    # Card text: [On Play] If your Leader has the {Baroque Works} type, select up to 1 of your
    # opponent's Characters with a cost of 4 or less. The selected Character cannot attack until
    # the end of your opponent's next turn.
    leader_origin = (player.leader.card_origin or '').lower() if player.leader else ''
    if 'baroque works' in leader_origin:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
        if targets:
            from ...game_engine import PendingChoice
            import uuid
            options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})",
                        "card_id": c.id, "card_name": c.name} for i, c in enumerate(targets)]
            game_state.pending_choice = PendingChoice(
                choice_id=f"mr3_{uuid.uuid4().hex[:8]}",
                choice_type="select_target",
                prompt="Choose opponent's cost 4 or less Character (cannot attack next turn)",
                options=options,
                min_selections=0,
                max_selections=1,
                source_card_id=card.id,
                source_card_name=card.name,
                callback_action="mr3_cannot_attack",
                callback_data={"player_id": player.player_id,
                               "target_cards": [{"id": c.id, "name": c.name} for c in targets]},
            )
    return True


# =============================================================================
# EVENT CARDS — MAIN EFFECTS
# =============================================================================

# --- OP01-027: Round Table ---
@register_effect("OP01-027", "on_play", "[Main] Give opponent's Character −10000 power")
def op01_027_round_table(game_state, player, card):
    # Card text: [Main] Give up to 1 of your opponent's Characters −10000 power during this turn.
    opponent = get_opponent(game_state, player)
    if opponent.cards_in_play:
        return create_power_effect_choice(
            game_state, player, opponent.cards_in_play, -10000,
            source_card=card,
            prompt="Choose an opponent's Character to give −10000 power"
        )
    return True


# --- OP01-030: In Two Years!! At the Sabaody Archipelago!! ---
@register_effect("OP01-030", "on_play", "[Main] Look top 5: add up to 1 SHC Character to hand")
def op01_030_two_years(game_state, player, card):
    # Card text: [Main] Look at 5 cards from the top of your deck; reveal up to 1 {Straw Hat
    # Crew} type Character card and add it to your hand. Then, place the rest at the bottom of
    # your deck in any order.
    def shc_char(c):
        return (c.card_type == 'CHARACTER'
                and 'straw hat crew' in (c.card_origin or '').lower())
    return search_top_cards(game_state, player, 5, add_count=1, filter_fn=shc_char,
                            source_card=card,
                            prompt="In Two Years!!: Choose up to 1 Straw Hat Crew Character from top 5 to add to hand")


# --- OP01-055: You Can Be My Samurai!! ---
@register_effect("OP01-055", "on_play", "[Main] Rest 2 Characters: Draw 2 cards")
def op01_055_samurai(game_state, player, card):
    # Card text: [Main] You may rest 2 of your Characters: Draw 2 cards.
    active_chars = [c for c in player.cards_in_play if not getattr(c, 'is_resting', False)]
    if len(active_chars) < 2:
        return True
    from ...game_engine import PendingChoice
    import uuid
    options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})",
                "card_id": c.id, "card_name": c.name} for i, c in enumerate(active_chars)]
    game_state.pending_choice = PendingChoice(
        choice_id=f"samurai_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Choose 2 of your Characters to rest (then draw 2 cards)",
        options=options,
        min_selections=2,
        max_selections=2,
        source_card_id=card.id,
        source_card_name=card.name,
        callback_action="samurai_rest_and_draw",
        callback_data={"player_id": player.player_id,
                       "active_cards": [{"id": c.id, "name": c.name} for c in active_chars]},
    )
    return True


# --- OP01-056: Demon Face ---
@register_effect("OP01-056", "on_play", "[Main] K.O. up to 2 opponent's rested Characters cost 5 or less")
def op01_056_demon_face(game_state, player, card):
    # Card text: [Main] K.O. up to 2 of your opponent's rested Characters with a cost of 5 or less.
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if getattr(c, 'is_resting', False) and (getattr(c, 'cost', 0) or 0) <= 5]
    if not targets:
        return True
    from ...game_engine import PendingChoice
    import uuid
    options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})",
                "card_id": c.id, "card_name": c.name} for i, c in enumerate(targets)]
    game_state.pending_choice = PendingChoice(
        choice_id=f"demon_face_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Choose up to 2 opponent's rested cost 5 or less Characters to K.O.",
        options=options,
        min_selections=0,
        max_selections=min(2, len(targets)),
        source_card_id=card.id,
        source_card_name=card.name,
        callback_action="ko_multiple_targets",
        callback_data={"player_id": player.player_id,
                       "target_cards": [{"id": c.id, "name": c.name} for c in targets]},
    )
    return True


# --- OP01-059: BE-BENG!! ---
@register_effect("OP01-059", "on_play", "[Main] Trash Land of Wano: Set Land of Wano cost 3 or less as active")
def op01_059_bebeng(game_state, player, card):
    # Card text: [Main] You may trash 1 {Land of Wano} type card from your hand: Set up to 1 of
    # your {Land of Wano} type Character cards with a cost of 3 or less as active.
    wano_hand = [c for c in player.hand if 'land of wano' in (c.card_origin or '').lower()]
    if not wano_hand:
        return True
    from ...game_engine import PendingChoice
    import uuid
    options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})",
                "card_id": c.id, "card_name": c.name} for i, c in enumerate(wano_hand)]
    wano_field = [c for c in player.cards_in_play
                  if 'land of wano' in (c.card_origin or '').lower()
                  and (getattr(c, 'cost', 0) or 0) <= 3
                  and getattr(c, 'is_resting', False)]
    game_state.pending_choice = PendingChoice(
        choice_id=f"bebeng_trash_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Choose a Land of Wano card from hand to trash (then set a Wano Character active)",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback_action="bebeng_trash_then_activate",
        callback_data={"player_id": player.player_id,
                       "wano_hand": [{"id": c.id, "name": c.name} for c in wano_hand],
                       "wano_field": [{"id": c.id, "name": c.name} for c in wano_field]},
    )
    return True


# --- OP01-090: Baroque Works (Event) ---
@register_effect("OP01-090", "on_play", "[Main] Search deck for Baroque Works card")
def op01_090_baroque_works(game_state, player, card):
    # Card text: [Main] Look at 5 cards from the top of your deck; reveal up to 1 {Baroque Works}
    # type card other than [Baroque Works] and add it to your hand. Then, place the rest at the
    # bottom of your deck in any order.
    if player.deck:
        return search_top_cards(
            game_state, player, look_count=5, add_count=1,
            filter_fn=lambda c: ('baroque works' in (c.card_origin or '').lower()
                                  and 'baroque works' not in (getattr(c, 'name', '') or '').lower()),
            source_card=card,
            prompt="Look at top 5: choose 1 Baroque Works card (not Baroque Works) to add to hand",
        )
    return True


# --- OP01-116: Artificial Devil Fruit SMILE (Event) ---
@register_effect("OP01-116", "on_play", "[Main] Search deck for SMILE Character cost 3 or less to play")
def op01_116_smile_event(game_state, player, card):
    # Card text: [Main] Look at 5 cards from the top of your deck; play up to 1 {SMILE} type
    # Character card with a cost of 3 or less. Then, place the rest at the bottom of your deck.
    if not player.deck:
        return True
    top5 = player.deck[:5]
    smiles = [c for c in top5
              if getattr(c, 'card_type', '') == 'CHARACTER'
              and 'smile' in (c.card_origin or '').lower()
              and (getattr(c, 'cost', 0) or 0) <= 3]
    # Move top5 to bottom; callback will pick one to play to field
    for c in top5:
        if c in player.deck:
            player.deck.remove(c)
    for c in top5:
        player.deck.append(c)
    if not smiles:
        game_state._log("[EFFECT] SMILE: No SMILE Characters in top 5, all placed at bottom")
        return True
    from ...game_engine import PendingChoice
    import uuid
    options = [{"id": c.id, "label": f"{c.name} (Cost: {c.cost or 0})",
                "card_id": c.id, "card_name": c.name} for c in smiles]
    game_state.pending_choice = PendingChoice(
        choice_id=f"smile_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Choose a SMILE Character cost 3 or less to play from top 5",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback_action="smile_play_to_field",
        callback_data={"player_id": player.player_id,
                       "top5_ids": [c.id for c in top5],
                       "smile_cards": [{"id": c.id, "name": c.name} for c in smiles]},
    )
    return True


# =============================================================================
# EVENT CARDS — COUNTER EFFECTS
# =============================================================================

# --- OP01-026: Gum-Gum Fire-Fist Pistol Red Hawk ---
@register_effect("OP01-026", "counter", "[Counter] +4000 power. Then K.O. opponent's 4000 power or less Character")
def op01_026_red_hawk(game_state, player, card):
    # Card text: [Counter] Up to 1 of your Leader or Character cards gains +4000 power during
    # this battle. Then, K.O. up to 1 of your opponent's Characters with 4000 power or less.
    opponent = get_opponent(game_state, player)
    power_targets = ([player.leader] if player.leader else []) + player.cards_in_play
    ko_targets = [c for c in opponent.cards_in_play
                  if (getattr(c, 'power', 0) or 0) + getattr(c, 'power_modifier', 0) <= 4000]

    if not power_targets:
        # No targets for +4000, just do KO
        if ko_targets:
            return create_ko_choice(
                game_state, player, ko_targets, source_card=card,
                prompt="Red Hawk: Choose opponent's 4000 power or less Character to K.O."
            )
        return True

    # Power choice first, then KO via callback
    from ...game_engine import PendingChoice
    import uuid
    options = [{"id": str(i), "label": f"{c.name} (Power: {c.power or 0})",
                "card_id": c.id, "card_name": c.name} for i, c in enumerate(power_targets)]
    game_state.pending_choice = PendingChoice(
        choice_id=f"red_hawk_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Red Hawk: Choose your Leader or Character to give +4000 power",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback_action="red_hawk_power_then_ko",
        callback_data={"player_id": player.player_id,
                       "power_targets": [{"id": c.id, "name": c.name} for c in power_targets],
                       "ko_targets": [{"id": c.id, "name": c.name} for c in ko_targets]},
    )
    return True


# --- OP01-028: Green Star Rafflesia ---
@register_effect("OP01-028", "counter", "[Counter] Give opponent's Leader or Character −2000 power")
def op01_028_rafflesia(game_state, player, card):
    # Card text: [Counter] Give up to 1 of your opponent's Leader or Character cards −2000 power
    # during this turn.
    opponent = get_opponent(game_state, player)
    targets = ([opponent.leader] if opponent.leader else []) + opponent.cards_in_play
    if targets:
        return create_power_effect_choice(
            game_state, player, targets, -2000,
            source_card=card,
            prompt="Choose opponent's Leader or Character to give −2000 power"
        )
    return True


# --- OP01-057: Paradise Waterfall ---
@register_effect("OP01-057", "counter", "[Counter] +2000 power. Then set 1 of your Characters as active")
def op01_057_paradise_waterfall(game_state, player, card):
    # Card text: [Counter] Up to 1 of your Leader or Character cards gains +2000 power during
    # this battle. Then, set up to 1 of your Characters as active.
    power_targets = ([player.leader] if player.leader else []) + player.cards_in_play
    rested = [c for c in player.cards_in_play if getattr(c, 'is_resting', False)]
    if not power_targets:
        return True
    from ...game_engine import PendingChoice
    import uuid
    options = [{"id": str(i), "label": f"{c.name} (Power: {c.power or 0})",
                "card_id": c.id, "card_name": c.name} for i, c in enumerate(power_targets)]
    game_state.pending_choice = PendingChoice(
        choice_id=f"paradise_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Choose your Leader or Character to give +2000 power (then set 1 Character active)",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback_action="paradise_power_then_set_active",
        callback_data={"player_id": player.player_id,
                       "power_targets": [{"id": c.id, "name": c.name} for c in power_targets],
                       "rested_chars": [{"id": c.id, "name": c.name} for c in rested]},
    )
    return True


# --- OP01-058: Punk Gibson ---
@register_effect("OP01-058", "counter", "[Counter] +4000 power. Then rest opponent's cost 4 or less Character")
def op01_058_punk_gibson(game_state, player, card):
    # Card text: [Counter] Up to 1 of your Leader or Character cards gains +4000 power during
    # this battle. Then, rest up to 1 of your opponent's Characters with a cost of 4 or less.
    opponent = get_opponent(game_state, player)
    power_targets = ([player.leader] if player.leader else []) + player.cards_in_play
    rest_targets = [c for c in opponent.cards_in_play
                    if (getattr(c, 'cost', 0) or 0) <= 4 and not getattr(c, 'is_resting', False)]
    if not power_targets:
        if rest_targets:
            return create_rest_choice(game_state, player, rest_targets, source_card=card,
                                      prompt="Punk Gibson: Choose opponent's cost 4 or less Character to rest")
        return True

    from ...game_engine import PendingChoice
    import uuid
    options = [{"id": str(i), "label": f"{c.name} (Power: {c.power or 0})",
                "card_id": c.id, "card_name": c.name} for i, c in enumerate(power_targets)]
    game_state.pending_choice = PendingChoice(
        choice_id=f"punk_gibson_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Punk Gibson: Choose your Leader or Character to give +4000 power",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback_action="punk_gibson_power_then_rest",
        callback_data={"player_id": player.player_id,
                       "power_targets": [{"id": c.id, "name": c.name} for c in power_targets],
                       "rest_targets": [{"id": c.id, "name": c.name} for c in rest_targets]},
    )
    return True


# --- OP01-086: Overheat ---
@register_effect("OP01-086", "counter", "[Counter] +4000 power. Then return active cost 3 or less Character to hand")
def op01_086_overheat(game_state, player, card):
    # Card text: [Counter] Up to 1 of your Leader or Character cards gains +4000 power during
    # this battle. Then, return up to 1 active Character with a cost of 3 or less to the owner's hand.
    opponent = get_opponent(game_state, player)
    # Can return ANY active cost 3 or less character (own or opponent's)
    all_chars = [(c, opponent) for c in opponent.cards_in_play] + [(c, player) for c in player.cards_in_play]
    return_targets = [c for c, _ in all_chars
                      if (getattr(c, 'cost', 0) or 0) <= 3 and not getattr(c, 'is_resting', False)]
    power_targets = ([player.leader] if player.leader else []) + player.cards_in_play
    if not power_targets:
        return True
    from ...game_engine import PendingChoice
    import uuid
    options = [{"id": str(i), "label": f"{c.name} (Power: {c.power or 0})",
                "card_id": c.id, "card_name": c.name} for i, c in enumerate(power_targets)]
    game_state.pending_choice = PendingChoice(
        choice_id=f"overheat_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Choose your Leader or Character to give +4000 power (then return active cost 3 or less to hand)",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback_action="overheat_power_then_return",
        callback_data={"player_id": player.player_id,
                       "power_targets": [{"id": c.id, "name": c.name} for c in power_targets],
                       "return_targets": [{"id": c.id, "name": c.name} for c in return_targets]},
    )
    return True


# --- OP01-087: Officer Agents ---
@register_effect("OP01-087", "counter", "[Counter] Play Baroque Works Character cost 3 or less from hand")
def op01_087_officer_agents(game_state, player, card):
    # Card text: [Counter] Play up to 1 {Baroque Works} type Character card with a cost of 3 or
    # less from your hand.
    baroque_chars = [c for c in player.hand
                     if getattr(c, 'card_type', '') == 'CHARACTER'
                     and 'baroque works' in (c.card_origin or '').lower()
                     and (getattr(c, 'cost', 0) or 0) <= 3]
    if baroque_chars:
        return create_play_from_hand_choice(
            game_state, player, baroque_chars,
            source_card=card,
            prompt="Choose Baroque Works cost 3 or less Character to play"
        )
    return True


# --- OP01-088: Desert Spada ---
@register_effect("OP01-088", "counter", "[Counter] +2000 power. Then look at 3 top deck cards")
def op01_088_desert_spada(game_state, player, card):
    # Card text: [Counter] Up to 1 of your Leader or Character cards gains +2000 power during
    # this battle. Then, look at 3 cards from the top of your deck and place them at the top or
    # bottom of your deck in any order.
    targets = ([player.leader] if player.leader else []) + player.cards_in_play
    if targets:
        from ...game_engine import PendingChoice
        import uuid
        options = []
        for i, c in enumerate(targets):
            options.append({
                "id": str(i),
                "label": f"{c.name} (Power: {c.power or 0})",
                "card_id": c.id,
                "card_name": c.name,
            })
        game_state.pending_choice = PendingChoice(
            choice_id=f"desert_spada_{uuid.uuid4().hex[:8]}",
            choice_type="select_target",
            prompt="Desert Spada: Choose Leader or Character to give +2000 power",
            options=options,
            min_selections=1,
            max_selections=1,
            source_card_id=card.id,
            source_card_name=card.name,
            callback_action="desert_spada_power_then_reorder",
            callback_data={
                "player_id": player.player_id,
                "target_cards": [{"id": c.id, "name": c.name} for c in targets],
            },
        )
    return True


# --- OP01-089: Crescent Cutlass ---
@register_effect("OP01-089", "counter", "[Counter] If Seven Warlords leader, return Character cost 5 or less to hand")
def op01_089_crescent_cutlass(game_state, player, card):
    # Card text: [Counter] If your Leader has the {The Seven Warlords of the Sea} type, return
    # up to 1 Character with a cost of 5 or less to the owner's hand.
    leader_origin = (player.leader.card_origin or '').lower() if player.leader else ''
    if 'seven warlords' in leader_origin or 'warlords of the sea' in leader_origin:
        opponent = get_opponent(game_state, player)
        all_chars = opponent.cards_in_play + player.cards_in_play
        targets = [c for c in all_chars if (getattr(c, 'cost', 0) or 0) <= 5]
        if targets:
            return create_return_to_hand_choice(game_state, player, targets, source_card=card,
                                               prompt="Choose a Character cost 5 or less to return to hand")
    return True


# --- OP01-118: Ulti-Mortar ---
@register_effect("OP01-118", "counter", "[Counter] DON!! −2: +2000 power to Leader or Character, then draw 1")
def op01_118_ulti_mortar(game_state, player, card):
    # Card text: [Counter] DON!! −2: Up to 1 of your Leader or Character cards gains +2000 power
    # during this battle. Then, draw 1 card.
    total_pool = len(player.don_pool)
    attached = sum(getattr(c, 'attached_don', 0) for c in player.cards_in_play)
    if getattr(player, 'leader', None):
        attached += getattr(player.leader, 'attached_don', 0)
    if total_pool + attached < 2:
        return True  # Can't pay DON cost
    auto = return_don_to_deck(game_state, player, 2, source_card=card,
                              after_callback="op01_118_ulti_mortar_power",
                              after_callback_data={"player_id": player.player_id})
    if auto:
        # DON auto-returned, proceed with power choice inline + draw 1
        draw_cards(player, 1)
        game_state._log(f"Ulti-Mortar: {player.name} draws 1 card")
        targets = ([player.leader] if player.leader else []) + player.cards_in_play
        if targets:
            return create_power_effect_choice(
                game_state, player, targets, 2000,
                source_card=card,
                prompt="Choose Leader or Character to give +2000 power"
            )
    return True


# --- OP01-121: Yamato ---
@register_effect("OP01-121", "continuous", "[Name alias] Also treated as Kouzuki Oden; [Double Attack] [Banish]")
def op01_121_yamato(game_state, player, card):
    # Card text: Also treat this card's name as [Kouzuki Oden] according to the rules.
    # [Double Attack] [Banish] — keywords handled by parser.
    # Name alias: mark card so engine can treat this as Kouzuki Oden for effect checks.
    card.also_named = "Kouzuki Oden"
    card.has_double_attack = True
    card.has_banish = True
    return True

