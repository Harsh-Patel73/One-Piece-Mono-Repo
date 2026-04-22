"""
Hardcoded effects for OP08 cards — Two Legends.
"""

import random
import uuid

from ..effect_registry import (
    _player_index, _remove_card_instance, _serialize_card_refs,
    add_don_from_deck, add_power_modifier,
    check_leader_type, check_life_count, check_trash_count,
    create_add_to_life_choice, create_bottom_deck_choice,
    create_cannot_attack_choice, create_cost_reduction_choice,
    create_hand_discard_choice, create_ko_choice,
    create_mode_choice, create_own_character_choice,
    create_play_from_hand_choice, create_play_from_trash_choice,
    create_power_effect_choice, create_rest_choice,
    create_return_to_hand_choice, create_set_active_choice,
    create_target_choice, create_trash_choice,
    draw_cards, filter_by_max_cost, get_opponent, optional_don_return,
    register_effect, reorder_top_cards, return_don_to_deck,
    search_top_cards, trash_from_hand,
)


# =============================================================================
# LEADER EFFECTS
# =============================================================================

# --- OP08-001: Tony Tony.Chopper (Leader) ---
@register_effect("OP08-001", "activate", "[Activate: Main] [Once Per Turn] Give up to 3 Animal/Drum Kingdom Characters 1 rested DON!! each")
def op08_001_chopper_leader(game_state, player, card):
    """Once Per Turn: Give up to 3 of your Animal or Drum Kingdom Characters up to 1 rested DON!! each."""
    if getattr(card, 'op08_001_used', False):
        return False

    targets = [c for c in player.cards_in_play
               if 'animal' in (getattr(c, 'card_origin', '') or '').lower()
               or 'drum kingdom' in (getattr(c, 'card_origin', '') or '').lower()]
    if not targets:
        return False

    rested_count = player.don_pool.count('rested')
    card.op08_001_used = True

    # Give 1 rested DON to up to 3 eligible characters (auto, up to available rested DON)
    given = 0
    for t in targets[:3]:
        if given >= rested_count:
            break
        # Find a rested DON in the pool and move it to attached
        for i in range(len(player.don_pool)):
            if player.don_pool[i] == 'rested':
                player.don_pool.pop(i)
                player.don_pool.append('rested')  # attached position
                t.attached_don = getattr(t, 'attached_don', 0) + 1
                given += 1
                game_state._log(f"Chopper Leader: gave 1 rested DON to {t.name}")
                break

    return given > 0


# --- OP08-002: Marco (Leader) ---
@register_effect("OP08-002", "activate", "[DON!! x1] [Activate: Main] [Once Per Turn] Draw 1, place 1 on deck, give opponent's char -2000")
def op08_002_marco_leader(game_state, player, card):
    """DON x1, Once Per Turn: Draw 1, place 1 from hand at top/bottom of deck, give opponent's Character -2000."""
    if getattr(card, 'op08_002_used', False):
        return False
    if getattr(card, 'attached_don', 0) < 1:
        return False

    card.op08_002_used = True
    draw_cards(player, 1)

    # Place 1 card from hand at bottom of deck (simplified — no top/bottom choice needed here)
    if player.hand:
        snap_hand = list(player.hand)

        def _after_place():
            opponent = get_opponent(game_state, player)
            opp_targets = list(opponent.cards_in_play)
            if opp_targets:
                create_power_effect_choice(
                    game_state, player, opp_targets, -2000,
                    source_card=card,
                    prompt="Choose opponent's Character to give -2000 power this turn",
                    min_selections=0,
                )

        def _place_cb(selected):
            idx = int(selected[0]) if selected else 0
            if 0 <= idx < len(snap_hand):
                c = snap_hand[idx]
                _remove_card_instance(player.hand, c)
                player.deck.append(c)
                game_state._log(f"Marco Leader: placed {c.name} at bottom of deck")
            _after_place()

        return create_own_character_choice(
            game_state, player, snap_hand, source_card=card,
            prompt="Choose a card from your hand to place at bottom of deck",
            callback=_place_cb,
        )

    # No cards in hand — still give -2000 if possible
    opponent = get_opponent(game_state, player)
    opp_targets = list(opponent.cards_in_play)
    if opp_targets:
        return create_power_effect_choice(
            game_state, player, opp_targets, -2000,
            source_card=card,
            prompt="Choose opponent's Character to give -2000 power this turn",
            min_selections=0,
        )
    return True


# --- OP08-021: Carrot (Leader) ---
@register_effect("OP08-021", "activate", "[Activate: Main] [Once Per Turn] If Minks Character, rest opponent's cost 5 or less")
def op08_021_carrot_leader(game_state, player, card):
    """Once Per Turn: If you have a Minks type Character, rest opponent's cost 5 or less Character."""
    if getattr(card, 'op08_021_used', False):
        return False

    has_minks = any('minks' in (getattr(c, 'card_origin', '') or '').lower()
                    for c in player.cards_in_play)
    if not has_minks:
        return False

    card.op08_021_used = True
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if not c.is_resting and (getattr(c, 'cost', 0) or 0) <= 5]
    if targets:
        return create_rest_choice(
            game_state, player, targets, source_card=card,
            prompt="Choose opponent's cost 5 or less Character to rest",
            min_selections=0,
        )
    return True


# --- OP08-057: King (Leader) ---
@register_effect("OP08-057", "activate", "[Activate: Main] [Once Per Turn] DON!! -2: Draw 1 (if ≤5 hand) OR give opponent's char -2 cost")
def op08_057_king_leader(game_state, player, card):
    """Once Per Turn, DON!! -2: Choose — draw 1 if 5 or less hand, OR give opponent's Character -2 cost."""
    if getattr(card, 'op08_057_used', False):
        return False
    if len(player.don_pool) < 2:
        return False

    def _after_don():
        card.op08_057_used = True
        opponent = get_opponent(game_state, player)
        opp_targets = list(opponent.cards_in_play)

        modes = []
        if len(player.hand) <= 5:
            modes.append({"id": "draw", "label": "Draw 1 card", "description": "Draw 1 card (you have 5 or less cards in hand)"})
        if opp_targets:
            modes.append({"id": "cost_reduce", "label": "Give opponent's Character -2 cost", "description": f"Choose 1 of {len(opp_targets)} opponent's Characters to give -2 cost this turn"})

        if not modes:
            return

        def _mode_cb(selected):
            mode = selected[0] if selected else None
            if mode == "draw":
                draw_cards(player, 1)
                game_state._log("King Leader: drew 1 card")
            elif mode == "cost_reduce" and opp_targets:
                create_cost_reduction_choice(
                    game_state, player, opp_targets, -2,
                    source_card=card,
                    prompt="Choose opponent's Character to give -2 cost this turn",
                )

        if len(modes) == 1:
            _mode_cb([modes[0]["id"]])
        else:
            create_mode_choice(game_state, player, modes, source_card=card,
                               prompt="King Leader: Choose one effect", callback=_mode_cb)

    auto = return_don_to_deck(game_state, player, 2, source_card=card, post_callback=_after_don)
    if auto:
        _after_don()
    return True


# --- OP08-058: Charlotte Pudding (Leader) ---
@register_effect("OP08-058", "on_attack", "[When Attacking] You may turn 2 Life face-up: Add 1 DON!! rested")
def op08_058_pudding_leader(game_state, player, card):
    """When Attacking: You may turn 2 cards from top of Life face-up to add 1 DON!! from deck rested."""
    if len(player.life_cards) < 2:
        return True

    def _yes_cb(selected):
        if "yes" in selected:
            # Turn top 2 life cards face-up
            for lc in player.life_cards[-2:]:
                lc.is_face_up = True
            added = add_don_from_deck(player, 1, set_active=False)
            if added:
                game_state._log("Charlotte Pudding Leader: added 1 rested DON")

    from ..game_engine import PendingChoice
    game_state.pending_choice = PendingChoice(
        choice_id=f"pudding_leader_{uuid.uuid4().hex[:8]}",
        choice_type="yes_no",
        prompt="Turn 2 Life cards face-up to add 1 DON!! rested?",
        options=[
            {"id": "yes", "label": "Yes — turn 2 Life face-up, add 1 DON rested", "card_id": "don_opt", "card_name": "DON!!"},
            {"id": "no", "label": "No", "card_id": "don_opt", "card_name": "DON!!"},
        ],
        min_selections=1, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=_yes_cb,
        callback_action="yes_no_choice",
        callback_data={"player_id": player.player_id},
    )
    return True


# --- OP08-098: Kalgara (Leader) ---
@register_effect("OP08-098", "on_attack", "[DON!! x1] [When Attacking] Play Shandian Warrior from hand cost ≤ DON count; if so add life to hand")
def op08_098_kalgara_leader(game_state, player, card):
    """DON x1, When Attacking: Play a Shandian Warrior from hand with cost ≤ DON count on field. If you do, add 1 life to hand."""
    if getattr(card, 'attached_don', 0) < 1:
        return False

    don_count = len(player.don_pool)
    shandians = [c for c in player.hand
                 if getattr(c, 'card_type', '') == 'CHARACTER'
                 and 'shandian warrior' in (getattr(c, 'card_origin', '') or '').lower()
                 and (getattr(c, 'cost', 0) or 0) <= don_count]
    if not shandians:
        return False

    def _play_cb(selected):
        if not selected:
            return
        idx = int(selected[0])
        snap = shandians
        if 0 <= idx < len(snap):
            target = snap[idx]
            if _remove_card_instance(player.hand, target):
                setattr(target, 'played_turn', game_state.turn_count)
                game_state.play_card_to_field_by_effect(player, target)
                game_state._apply_keywords(target)
                game_state._log(f"Kalgara Leader: played {target.name}")
                # Add 1 life to hand
                if player.life_cards:
                    life_card = player.life_cards.pop()
                    player.hand.append(life_card)
                    game_state._log("Kalgara Leader: added 1 life card to hand")

    return create_play_from_hand_choice(
        game_state, player, shandians, source_card=card,
        prompt=f"Choose a Shandian Warrior (cost ≤ {don_count}) to play from hand",
        callback=_play_cb,
    )


# =============================================================================
# DRUM KINGDOM BLOCK — OP08-003 to OP08-020
# =============================================================================

# --- OP08-003: Twenty Doctors ---
@register_effect("OP08-003", "blocker", "[Blocker]")
def op08_003_twenty_doctors(game_state, player, card):
    card.has_blocker = True
    return True


# --- OP08-004: Kuromarimo ---
@register_effect("OP08-004", "on_play", "[On Play] If you have [Chess], K.O. opponent's 3000 power or less")
def op08_004_kuromarimo(game_state, player, card):
    has_chess = any(getattr(c, 'name', '') == 'Chess' for c in player.cards_in_play)
    if not has_chess:
        return True
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'power', 0) or 0) <= 3000]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                                prompt="Choose opponent's 3000 power or less Character to K.O.")
    return True


# --- OP08-005: Chess ---
@register_effect("OP08-005", "on_play", "[On Play] Opponent's char -2000 power; if no Kuromarimo, play Kuromarimo from hand")
def op08_005_chess(game_state, player, card):
    opponent = get_opponent(game_state, player)
    opp_targets = list(opponent.cards_in_play)

    def _after_power(selected):
        # Apply power reduction
        snap = opp_targets
        if selected:
            idx = int(selected[0])
            if 0 <= idx < len(snap):
                snap[idx].power_modifier = getattr(snap[idx], 'power_modifier', 0) - 2000
                snap[idx]._sticky_power_modifier = getattr(snap[idx], '_sticky_power_modifier', 0) - 2000
                game_state._log(f"{snap[idx].name} gets -2000 power")
        # Then play Kuromarimo if needed
        has_kuromarimo = any(getattr(c, 'name', '') == 'Kuromarimo' for c in player.cards_in_play)
        if not has_kuromarimo:
            kuros = [c for c in player.hand if getattr(c, 'name', '') == 'Kuromarimo']
            if kuros:
                create_play_from_hand_choice(game_state, player, kuros, source_card=card,
                                             prompt="Play [Kuromarimo] from your hand?")

    if opp_targets:
        return create_power_effect_choice(
            game_state, player, opp_targets, -2000, source_card=card,
            prompt="Choose opponent's Character to give -2000 power this turn",
            min_selections=0,
            callback=_after_power,
        )
    # No targets: still offer Kuromarimo
    has_kuromarimo = any(getattr(c, 'name', '') == 'Kuromarimo' for c in player.cards_in_play)
    if not has_kuromarimo:
        kuros = [c for c in player.hand if getattr(c, 'name', '') == 'Kuromarimo']
        if kuros:
            return create_play_from_hand_choice(game_state, player, kuros, source_card=card,
                                                prompt="Play [Kuromarimo] from your hand?")
    return True


# --- OP08-006: Chessmarimo ---
@register_effect("OP08-006", "continuous", "[Your Turn] +2000 power if Kuromarimo and Chess in trash")
def op08_006_chessmarimo(game_state, player, card):
    has_kuromarimo = any(getattr(c, 'name', '') == 'Kuromarimo' for c in player.trash)
    has_chess = any(getattr(c, 'name', '') == 'Chess' for c in player.trash)
    if has_kuromarimo and has_chess:
        add_power_modifier(card, 2000)
    return True


# --- OP08-007: Tony Tony.Chopper (Character) ---
@register_effect("OP08-007", "on_play", "[On Play] Look at 5, play Animal 4000 power or less rested")
def op08_007_chopper_on_play(game_state, player, card):
    return search_top_cards(
        game_state, player, 5, add_count=1,
        filter_fn=lambda c: (
            'animal' in (getattr(c, 'card_origin', '') or '').lower()
            and getattr(c, 'card_type', '') == 'CHARACTER'
            and (getattr(c, 'power', 0) or 0) <= 4000
        ),
        source_card=card,
        play_to_field=True, play_rested=True,
        prompt="Look at top 5. Choose up to 1 Animal Character (4000 power or less) to play rested.",
    )


@register_effect("OP08-007", "on_attack", "[When Attacking] Look at 5, play Animal 4000 power or less rested")
def op08_007_chopper_on_attack(game_state, player, card):
    return search_top_cards(
        game_state, player, 5, add_count=1,
        filter_fn=lambda c: (
            'animal' in (getattr(c, 'card_origin', '') or '').lower()
            and getattr(c, 'card_type', '') == 'CHARACTER'
            and (getattr(c, 'power', 0) or 0) <= 4000
        ),
        source_card=card,
        play_to_field=True, play_rested=True,
        prompt="Look at top 5. Choose up to 1 Animal Character (4000 power or less) to play rested.",
    )


# --- OP08-008: Dalton ---
@register_effect("OP08-008", "on_play", "[On Play] Give opponent's Character -1000 power this turn")
def op08_008_dalton_on_play(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = list(opponent.cards_in_play)
    if targets:
        return create_power_effect_choice(
            game_state, player, targets, -1000, source_card=card,
            prompt="Choose opponent's Character to give -1000 power this turn",
            min_selections=0,
        )
    return True


@register_effect("OP08-008", "activate", "[DON!! x1] [Activate: Main] [Once Per Turn] Add life to hand: gain Rush")
def op08_008_dalton_activate(game_state, player, card):
    if getattr(card, 'op08_008_used', False):
        return False
    if getattr(card, 'attached_don', 0) < 1:
        return False
    if not player.life_cards:
        return False
    life_card = player.life_cards.pop()
    player.hand.append(life_card)
    card.has_rush = True
    card.has_attacked = False
    card.op08_008_used = True
    game_state._log(f"Dalton: added life card {life_card.name} to hand, gained Rush")
    return True


# --- OP08-010: Hiking Bear ---
@register_effect("OP08-010", "activate", "[DON!! x1] [Activate: Main] [Once Per Turn] Animal Character other than this +1000 power")
def op08_010_hiking_bear(game_state, player, card):
    if getattr(card, 'op08_010_used', False):
        return False
    if getattr(card, 'attached_don', 0) < 1:
        return False
    targets = [c for c in player.cards_in_play
               if c is not card and 'animal' in (getattr(c, 'card_origin', '') or '').lower()]
    if not targets:
        return False
    card.op08_010_used = True
    return create_power_effect_choice(
        game_state, player, targets, 1000, source_card=card,
        prompt="Choose your Animal Character (other than Hiking Bear) to give +1000 power this turn",
    )


# --- OP08-012: Lapins ---
@register_effect("OP08-012", "on_attack", "[DON!! x2] [When Attacking] If Drum Kingdom leader, K.O. opponent's 4000 power or less")
def op08_012_lapins(game_state, player, card):
    if getattr(card, 'attached_don', 0) < 2:
        return False
    if not check_leader_type(player, 'Drum Kingdom'):
        return False
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'power', 0) or 0) <= 4000]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                                prompt="Choose opponent's 4000 power or less Character to K.O.")
    return True


# --- OP08-013: Robson ---
@register_effect("OP08-013", "continuous", "[DON!! x2] Gain Rush")
def op08_013_robson(game_state, player, card):
    if getattr(card, 'attached_don', 0) >= 2:
        card.has_rush = True
    return True


# --- OP08-014: Wapol ---
@register_effect("OP08-014", "on_attack", "[DON!! x1] [When Attacking] Opponent's char -2000; this char +2000 until opponent's turn end")
def op08_014_wapol(game_state, player, card):
    if getattr(card, 'attached_don', 0) < 1:
        return False
    opponent = get_opponent(game_state, player)
    targets = list(opponent.cards_in_play)

    def _after_opp_debuff(selected):
        if selected:
            idx = int(selected[0])
            snap = targets
            if 0 <= idx < len(snap):
                snap[idx].power_modifier = getattr(snap[idx], 'power_modifier', 0) - 2000
                snap[idx]._sticky_power_modifier = getattr(snap[idx], '_sticky_power_modifier', 0) - 2000
                game_state._log(f"{snap[idx].name} gets -2000 power")
        # Wapol gains +2000 until end of opponent's next turn
        card.power_modifier = getattr(card, 'power_modifier', 0) + 2000
        card._sticky_power_modifier = getattr(card, '_sticky_power_modifier', 0) + 2000
        card.power_modifier_expires_on_turn = game_state.turn_count + 1
        game_state._log("Wapol: gains +2000 power until end of opponent's next turn")

    if targets:
        return create_power_effect_choice(
            game_state, player, targets, -2000, source_card=card,
            prompt="Choose opponent's Character to give -2000 power this turn",
            min_selections=0,
            callback=_after_opp_debuff,
        )
    # No targets: still give Wapol the buff
    _after_opp_debuff([])
    return True


# --- OP08-015: Dr.Kureha ---
@register_effect("OP08-015", "on_play", "[On Play] Look at 4, add Tony Tony.Chopper or Drum Kingdom card (not Dr.Kureha)")
def op08_015_kureha(game_state, player, card):
    return search_top_cards(
        game_state, player, 4, add_count=1,
        filter_fn=lambda c: (
            getattr(c, 'name', '') == 'Tony Tony.Chopper'
            or ('drum kingdom' in (getattr(c, 'card_origin', '') or '').lower()
                and getattr(c, 'name', '') != 'Dr.Kureha')
        ),
        source_card=card,
        prompt="Look at top 4. Choose up to 1 [Tony Tony.Chopper] or Drum Kingdom card to add to hand.",
    )


# --- OP08-016: Dr.Hiriluk ---
@register_effect("OP08-016", "activate", "[Activate: Main] Rest this: If leader is Tony Tony.Chopper, all Chopper Characters +2000")
def op08_016_hiriluk(game_state, player, card):
    if card.is_resting:
        return False
    if not (player.leader and getattr(player.leader, 'name', '') == 'Tony Tony.Chopper'):
        return False
    card.is_resting = True
    for c in player.cards_in_play:
        if getattr(c, 'name', '') == 'Tony Tony.Chopper':
            add_power_modifier(c, 2000)
            game_state._log(f"Dr.Hiriluk: {c.name} gains +2000 power")
    return True


# --- OP08-017: I'd Never Shoot You!!!! (Event) ---
@register_effect("OP08-017", "counter", "[Counter] Leader/Character +4000; opponent's Leader/Character -1000")
def op08_017_never_shoot_counter(game_state, player, card):
    own_targets = [player.leader] + list(player.cards_in_play) if player.leader else list(player.cards_in_play)
    own_targets = [c for c in own_targets if c is not None]

    def _after_buff(selected):
        if selected:
            idx = int(selected[0])
            if 0 <= idx < len(own_targets):
                add_power_modifier(own_targets[idx], 4000)
                game_state._log(f"{own_targets[idx].name} gains +4000 power")
        opponent = get_opponent(game_state, player)
        opp_all = [opponent.leader] + list(opponent.cards_in_play) if opponent.leader else list(opponent.cards_in_play)
        opp_all = [c for c in opp_all if c is not None]
        if opp_all:
            create_power_effect_choice(
                game_state, player, opp_all, -1000, source_card=card,
                prompt="Choose opponent's Leader or Character to give -1000 power this turn",
                min_selections=0,
            )

    if own_targets:
        return create_power_effect_choice(
            game_state, player, own_targets, 4000, source_card=card,
            prompt="Choose your Leader or Character to give +4000 power this battle",
            callback=_after_buff,
        )
    return True


@register_effect("OP08-017", "trigger", "[Trigger] Leader/Character +1000 power this turn")
def op08_017_never_shoot_trigger(game_state, player, card):
    own_targets = [player.leader] + list(player.cards_in_play) if player.leader else list(player.cards_in_play)
    own_targets = [c for c in own_targets if c is not None]
    if own_targets:
        return create_power_effect_choice(
            game_state, player, own_targets, 1000, source_card=card,
            prompt="Trigger: Choose your Leader or Character to give +1000 power this turn",
            min_selections=0,
        )
    return True


# --- OP08-018: Cloven Rose (Event) ---
@register_effect("OP08-018", "on_play", "[Main] Up to 3 Characters +1000; opponent's Character -2000")
def op08_018_cloven_rose(game_state, player, card):
    own_chars = list(player.cards_in_play)

    def _after_buffs(selected):
        for sel in selected:
            idx = int(sel)
            if 0 <= idx < len(own_chars):
                add_power_modifier(own_chars[idx], 1000)
                game_state._log(f"{own_chars[idx].name} gains +1000 power")
        opponent = get_opponent(game_state, player)
        opp_targets = list(opponent.cards_in_play)
        if opp_targets:
            create_power_effect_choice(
                game_state, player, opp_targets, -2000, source_card=card,
                prompt="Choose opponent's Character to give -2000 power this turn",
                min_selections=0,
            )

    if own_chars:
        return create_power_effect_choice(
            game_state, player, own_chars, 1000, source_card=card,
            prompt="Choose up to 3 of your Characters to give +1000 power this turn",
            min_selections=0, max_selections=3,
            callback=_after_buffs,
        )
    # No own chars: just debuff
    opponent = get_opponent(game_state, player)
    opp_targets = list(opponent.cards_in_play)
    if opp_targets:
        return create_power_effect_choice(
            game_state, player, opp_targets, -2000, source_card=card,
            prompt="Choose opponent's Character to give -2000 power this turn",
            min_selections=0,
        )
    return True


@register_effect("OP08-018", "trigger", "[Trigger] Opponent's Leader or Character -3000 power this turn")
def op08_018_cloven_rose_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    opp_all = [opponent.leader] + list(opponent.cards_in_play) if opponent.leader else list(opponent.cards_in_play)
    opp_all = [c for c in opp_all if c is not None]
    if opp_all:
        return create_power_effect_choice(
            game_state, player, opp_all, -3000, source_card=card,
            prompt="Trigger: Choose opponent's Leader or Character to give -3000 power this turn",
            min_selections=0,
        )
    return True


# --- OP08-019: Munch-Munch Mutation (Event) ---
@register_effect("OP08-019", "on_play", "[Main]/[Counter] Opponent's char -3000; own char +3000")
def op08_019_munch_munch(game_state, player, card):
    opponent = get_opponent(game_state, player)
    opp_targets = list(opponent.cards_in_play)

    def _after_debuff(selected):
        if selected:
            idx = int(selected[0])
            if 0 <= idx < len(opp_targets):
                add_power_modifier(opp_targets[idx], -3000)
                game_state._log(f"{opp_targets[idx].name} gets -3000 power")
        own_chars = list(player.cards_in_play)
        if own_chars:
            create_power_effect_choice(
                game_state, player, own_chars, 3000, source_card=card,
                prompt="Choose your Character to give +3000 power this turn",
                min_selections=0,
            )

    if opp_targets:
        return create_power_effect_choice(
            game_state, player, opp_targets, -3000, source_card=card,
            prompt="Choose opponent's Character to give -3000 power this turn",
            min_selections=0,
            callback=_after_debuff,
        )
    own_chars = list(player.cards_in_play)
    if own_chars:
        return create_power_effect_choice(
            game_state, player, own_chars, 3000, source_card=card,
            prompt="Choose your Character to give +3000 power this turn",
            min_selections=0,
        )
    return True


@register_effect("OP08-019", "counter", "[Counter] Opponent's char -3000; own char +3000")
def op08_019_munch_munch_counter(game_state, player, card):
    return op08_019_munch_munch(game_state, player, card)


@register_effect("OP08-019", "trigger", "[Trigger] K.O. opponent's 5000 power or less")
def op08_019_munch_munch_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'power', 0) or 0) <= 5000]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                                prompt="Trigger: K.O. opponent's 5000 power or less Character")
    return True


# --- OP08-020: Drum Kingdom (Stage) ---
@register_effect("OP08-020", "continuous", "[Opponent's Turn] All Drum Kingdom Characters +1000 power")
def op08_020_drum_kingdom_stage(game_state, player, card):
    """Continuous: During opponent's turn, Drum Kingdom Characters gain +1000 power.
    Since continuous effects re-fire every recalc, this always applies (approximation)."""
    for c in player.cards_in_play:
        if 'drum kingdom' in (getattr(c, 'card_origin', '') or '').lower():
            add_power_modifier(c, 1000)
    return True


# =============================================================================
# MINKS BLOCK — OP08-022 to OP08-039
# =============================================================================

def _skip_refresh_callback(snap):
    """Return a callback that sets skip_refresh on selected cards."""
    def cb(selected):
        for sel in selected:
            idx = int(sel)
            if 0 <= idx < len(snap):
                snap[idx].skip_refresh = True
    return cb


# --- OP08-022: Inuarashi ---
@register_effect("OP08-022", "on_play", "[On Play] If Minks leader, up to 2 opponent's rested cost 5 or less won't refresh")
def op08_022_inuarashi(game_state, player, card):
    if not check_leader_type(player, 'Minks'):
        return True
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if c.is_resting and (getattr(c, 'cost', 0) or 0) <= 5]
    if not targets:
        return True
    snap = list(targets)
    options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})",
                "card_id": c.id, "card_name": c.name} for i, c in enumerate(snap)]
    from ..game_engine import PendingChoice
    game_state.pending_choice = PendingChoice(
        choice_id=f"skip_refresh_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Choose up to 2 opponent's rested cost 5 or less Characters that won't refresh",
        options=options,
        min_selections=0, max_selections=2,
        source_card_id=card.id, source_card_name=card.name,
        callback=_skip_refresh_callback(snap),
        callback_action="skip_refresh_multi",
        callback_data={"player_id": player.player_id, "player_index": _player_index(game_state, player)},
    )
    return True


# --- OP08-023: Carrot (Character) ---
@register_effect("OP08-023", "on_play", "[On Play] Opponent's rested cost 7 or less won't refresh")
def op08_023_carrot_on_play(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if c.is_resting and (getattr(c, 'cost', 0) or 0) <= 7]
    if not targets:
        return True
    snap = list(targets)
    return create_target_choice(
        game_state, player, targets, source_card=card,
        prompt="Choose opponent's rested cost 7 or less Character that won't refresh next phase",
        min_selections=0, max_selections=1,
        callback=_skip_refresh_callback(snap),
    )


@register_effect("OP08-023", "on_attack", "[When Attacking] Opponent's rested cost 7 or less won't refresh")
def op08_023_carrot_on_attack(game_state, player, card):
    return op08_023_carrot_on_play(game_state, player, card)


# --- OP08-024: Concelot ---
@register_effect("OP08-024", "on_attack", "[When Attacking] Opponent's rested cost 4 or less won't refresh")
def op08_024_concelot(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if c.is_resting and (getattr(c, 'cost', 0) or 0) <= 4]
    if not targets:
        return True
    snap = list(targets)
    return create_target_choice(
        game_state, player, targets, source_card=card,
        prompt="Choose opponent's rested cost 4 or less Character that won't refresh next phase",
        min_selections=0, max_selections=1,
        callback=_skip_refresh_callback(snap),
    )


# --- OP08-025: Shishilian ---
@register_effect("OP08-025", "on_play", "[On Play] Opponent's rested cost 3 or less won't refresh")
def op08_025_shishilian(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if c.is_resting and (getattr(c, 'cost', 0) or 0) <= 3]
    if not targets:
        return True
    snap = list(targets)
    return create_target_choice(
        game_state, player, targets, source_card=card,
        prompt="Choose opponent's rested cost 3 or less Character that won't refresh next phase",
        min_selections=0, max_selections=1,
        callback=_skip_refresh_callback(snap),
    )


# --- OP08-026: Giovanni ---
@register_effect("OP08-026", "on_attack", "[DON!! x1] [When Attacking] Opponent's rested cost 1 or less won't refresh")
def op08_026_giovanni(game_state, player, card):
    if getattr(card, 'attached_don', 0) < 1:
        return False
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if c.is_resting and (getattr(c, 'cost', 0) or 0) <= 1]
    if not targets:
        return True
    snap = list(targets)
    return create_target_choice(
        game_state, player, targets, source_card=card,
        prompt="Choose opponent's rested cost 1 or less Character that won't refresh next phase",
        min_selections=0, max_selections=1,
        callback=_skip_refresh_callback(snap),
    )


# --- OP08-028: Nekomamushi ---
@register_effect("OP08-028", "on_play", "[On Play] If opponent has 7+ rested cards, gain Rush")
def op08_028_nekomamushi(game_state, player, card):
    opponent = get_opponent(game_state, player)
    rested_count = sum(1 for c in opponent.cards_in_play if c.is_resting)
    # Count rested DON
    rested_count += opponent.don_pool.count('rested')
    if opponent.leader and getattr(opponent.leader, 'is_resting', False):
        rested_count += 1
    if rested_count >= 7:
        card.has_rush = True
        card.has_attacked = False
        game_state._log("Nekomamushi: gained Rush")
    return True


# --- OP08-029: Pekoms ---
@register_effect("OP08-029", "continuous", "[Continuous] If active, Minks cost 3 or less can't be K.O.'d by effects")
def op08_029_pekoms(game_state, player, card):
    if not card.is_resting:
        for c in player.cards_in_play:
            if (c is not card
                    and 'minks' in (getattr(c, 'card_origin', '') or '').lower()
                    and (getattr(c, 'cost', 0) or 0) <= 3):
                c.ko_protection = True
    return True


# --- OP08-030: Pedro ---
@register_effect("OP08-030", "blocker", "[Blocker]")
def op08_030_pedro_blocker(game_state, player, card):
    card.has_blocker = True
    return True


@register_effect("OP08-030", "on_ko", "[On K.O.] Choose: Rest opponent's DON OR K.O. opponent's rested cost 6 or less")
def op08_030_pedro_on_ko(game_state, player, card):
    opponent = get_opponent(game_state, player)
    rested_ko_targets = [c for c in opponent.cards_in_play
                         if c.is_resting and (getattr(c, 'cost', 0) or 0) <= 6]
    active_don = opponent.don_pool.count('active')

    modes = []
    if active_don > 0:
        modes.append({"id": "rest_don", "label": "Rest 1 of opponent's DON!! cards",
                      "description": f"Opponent has {active_don} active DON"})
    if rested_ko_targets:
        modes.append({"id": "ko_char", "label": "K.O. opponent's rested cost 6 or less",
                      "description": f"Choose from {len(rested_ko_targets)} targets"})

    if not modes:
        return True

    def _mode_cb(selected):
        mode = selected[0] if selected else None
        if mode == "rest_don":
            for i in range(len(opponent.don_pool)):
                if opponent.don_pool[i] == 'active':
                    opponent.don_pool[i] = 'rested'
                    game_state._log("Pedro: rested 1 opponent DON")
                    break
        elif mode == "ko_char" and rested_ko_targets:
            create_ko_choice(game_state, player, rested_ko_targets, source_card=card,
                             prompt="K.O. opponent's rested cost 6 or less Character")

    if len(modes) == 1:
        _mode_cb([modes[0]["id"]])
        return True
    return create_mode_choice(game_state, player, modes, source_card=card,
                              prompt="Pedro On K.O.: Choose one effect", callback=_mode_cb)


# --- OP08-031: Miyagi ---
@register_effect("OP08-031", "on_play", "[On Play] Set Minks cost 2 or less Character as active")
def op08_031_miyagi(game_state, player, card):
    targets = [c for c in player.cards_in_play
               if c.is_resting
               and 'minks' in (getattr(c, 'card_origin', '') or '').lower()
               and (getattr(c, 'cost', 0) or 0) <= 2]
    if targets:
        return create_set_active_choice(
            game_state, player, targets, source_card=card,
            prompt="Choose your rested Minks cost 2 or less Character to set active",
            min_selections=0,
        )
    return True


# --- OP08-032: Milky ---
@register_effect("OP08-032", "activate", "[Activate: Main] Rest this: If Minks leader, set 1 DON!! as active")
def op08_032_milky(game_state, player, card):
    if card.is_resting:
        return False
    if not check_leader_type(player, 'Minks'):
        return False
    card.is_resting = True
    # Set 1 rested DON as active
    for i in range(len(player.don_pool)):
        if player.don_pool[i] == 'rested':
            player.don_pool[i] = 'active'
            game_state._log("Milky: set 1 DON active")
            break
    return True


# --- OP08-033: Roddy ---
@register_effect("OP08-033", "on_play", "[On Play] If Minks leader and opponent has 7+ rested, K.O. rested cost 2 or less")
def op08_033_roddy(game_state, player, card):
    if not check_leader_type(player, 'Minks'):
        return True
    opponent = get_opponent(game_state, player)
    rested_count = sum(1 for c in opponent.cards_in_play if c.is_resting)
    rested_count += opponent.don_pool.count('rested')
    if rested_count < 7:
        return True
    targets = [c for c in opponent.cards_in_play
               if c.is_resting and (getattr(c, 'cost', 0) or 0) <= 2]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                                prompt="Choose opponent's rested cost 2 or less Character to K.O.")
    return True


# --- OP08-034: Wanda ---
@register_effect("OP08-034", "on_play", "[On Play] Look at 5, add Minks card other than Wanda")
def op08_034_wanda(game_state, player, card):
    return search_top_cards(
        game_state, player, 5, add_count=1,
        filter_fn=lambda c: (
            'minks' in (getattr(c, 'card_origin', '') or '').lower()
            and getattr(c, 'name', '') != 'Wanda'
        ),
        source_card=card,
        prompt="Look at top 5. Choose up to 1 Minks type card (not Wanda) to add to hand.",
    )


# --- OP08-036: Electrical Luna (Event) ---
@register_effect("OP08-036", "on_play", "[Main] All opponent's rested cost 7 or less won't refresh")
def op08_036_electrical_luna(game_state, player, card):
    opponent = get_opponent(game_state, player)
    count = 0
    for c in opponent.cards_in_play:
        if c.is_resting and (getattr(c, 'cost', 0) or 0) <= 7:
            c.skip_refresh = True
            count += 1
    game_state._log(f"Electrical Luna: {count} opponent's Characters won't refresh")
    return True


@register_effect("OP08-036", "trigger", "[Trigger] Rest opponent's Character")
def op08_036_electrical_luna_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if not c.is_resting]
    if targets:
        return create_rest_choice(game_state, player, targets, source_card=card,
                                  prompt="Trigger: Choose opponent's Character to rest",
                                  min_selections=0)
    return True


# --- OP08-037: Garchu (Event) ---
@register_effect("OP08-037", "on_play", "[Main] Rest 1 Minks Character: Rest opponent's Character")
def op08_037_garchu(game_state, player, card):
    minks_active = [c for c in player.cards_in_play
                    if not c.is_resting and 'minks' in (getattr(c, 'card_origin', '') or '').lower()]
    if not minks_active:
        return True

    def _after_rest_own(selected):
        if not selected:
            return
        snap = minks_active
        idx = int(selected[0])
        if 0 <= idx < len(snap):
            snap[idx].is_resting = True
            game_state._log(f"Garchu: rested {snap[idx].name}")
        opponent = get_opponent(game_state, player)
        opp_targets = list(opponent.cards_in_play)
        if opp_targets:
            create_rest_choice(game_state, player, opp_targets, source_card=card,
                               prompt="Choose opponent's Character to rest",
                               min_selections=0)

    return create_own_character_choice(
        game_state, player, minks_active, source_card=card,
        prompt="You may rest 1 of your Minks Characters to rest an opponent's Character",
        optional=True,
        callback=_after_rest_own,
    )


@register_effect("OP08-037", "trigger", "[Trigger] Draw 1 card")
def op08_037_garchu_trigger(game_state, player, card):
    draw_cards(player, 1)
    return True


# --- OP08-038: We Would Never Sell a Comrade to an Enemy!!! (Event) ---
@register_effect("OP08-038", "on_play", "[Main] Rest 2 Characters: Characters can't be K.O.'d by effects until opponent's turn end")
def op08_038_we_would_never(game_state, player, card):
    active_chars = [c for c in player.cards_in_play if not c.is_resting]
    if len(active_chars) < 2:
        return True

    snap = list(active_chars)
    options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})",
                "card_id": c.id, "card_name": c.name} for i, c in enumerate(snap)]

    def _rest_cb(selected):
        if len(selected) < 2:
            return
        for sel in selected[:2]:
            idx = int(sel)
            if 0 <= idx < len(snap):
                snap[idx].is_resting = True
                game_state._log(f"We Would Never: rested {snap[idx].name}")
        # Protect all characters from KO effects
        for c in player.cards_in_play:
            c.protected_from_ko_effects_until_opponent_turn_end = True
        game_state._log("We Would Never: Characters protected from KO effects until opponent's turn end")

    from ..game_engine import PendingChoice
    game_state.pending_choice = PendingChoice(
        choice_id=f"we_would_never_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Choose 2 of your Characters to rest to protect all Characters from K.O. effects",
        options=options,
        min_selections=2, max_selections=2,
        source_card_id=card.id, source_card_name=card.name,
        callback=_rest_cb,
        callback_action="rest_for_protection",
        callback_data={"player_id": player.player_id, "player_index": _player_index(game_state, player)},
    )
    return True


@register_effect("OP08-038", "trigger", "[Trigger] Rest opponent's cost 3 or less Character")
def op08_038_we_would_never_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if not c.is_resting and (getattr(c, 'cost', 0) or 0) <= 3]
    if targets:
        return create_rest_choice(game_state, player, targets, source_card=card,
                                  prompt="Trigger: Choose opponent's cost 3 or less Character to rest",
                                  min_selections=0)
    return True


# --- OP08-039: Zou (Stage) ---
@register_effect("OP08-039", "activate", "[Activate: Main] Rest this Stage: If Minks leader, set 1 DON!! as active")
def op08_039_zou_activate(game_state, player, card):
    if card.is_resting:
        return False
    if not check_leader_type(player, 'Minks'):
        return False
    card.is_resting = True
    for i in range(len(player.don_pool)):
        if player.don_pool[i] == 'rested':
            player.don_pool[i] = 'active'
            game_state._log("Zou: set 1 DON active")
            break
    return True


@register_effect("OP08-039", "end_of_turn", "[End of Your Turn] Set 1 Minks Character as active")
def op08_039_zou_end_of_turn(game_state, player, card):
    targets = [c for c in player.cards_in_play
               if c.is_resting and 'minks' in (getattr(c, 'card_origin', '') or '').lower()]
    if targets:
        return create_set_active_choice(
            game_state, player, targets, source_card=card,
            prompt="End of Turn — Zou: Choose a rested Minks Character to set active",
            min_selections=0,
        )
    return True


# =============================================================================
# WHITEBEARD PIRATES BLOCK — OP08-040 to OP08-056
# =============================================================================

# --- OP08-040: Atmos ---
@register_effect("OP08-040", "on_play", "[On Play] Reveal 2 Whitebeard Pirates from hand + WB leader: Return opponent's cost 4 or less")
def op08_040_atmos(game_state, player, card):
    if not check_leader_type(player, 'Whitebeard Pirates'):
        return True
    wb_cards = [c for c in player.hand
                if 'whitebeard pirates' in (getattr(c, 'card_origin', '') or '').lower()]
    if len(wb_cards) < 2:
        return True
    # Reveal 2 (auto — both conditions met)
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
    if targets:
        return create_return_to_hand_choice(
            game_state, player, targets, source_card=card,
            prompt="Choose opponent's cost 4 or less Character to return to hand",
            optional=True,
        )
    return True


# --- OP08-041: Aphelandra ---
@register_effect("OP08-041", "activate", "[Activate: Main] Return this to hand: If Kuja Pirates leader, place opponent's cost 1 or less at bottom of deck")
def op08_041_aphelandra(game_state, player, card):
    if not check_leader_type(player, 'Kuja Pirates'):
        return False
    # Return this card to hand
    if card in player.cards_in_play:
        player.cards_in_play.remove(card)
        player.hand.append(card)
        game_state._log(f"Aphelandra: returned to hand")
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 1]
    if targets:
        return create_bottom_deck_choice(
            game_state, player, targets, source_card=card,
            prompt="Choose opponent's cost 1 or less Character to place at bottom of deck",
            min_selections=0,
        )
    return True


# --- OP08-042: Edward Weevil ---
@register_effect("OP08-042", "on_attack", "[DON!! x1] [When Attacking] Return cost 3 or less Character to owner's hand")
def op08_042_edward_weevil(game_state, player, card):
    if getattr(card, 'attached_don', 0) < 1:
        return False
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
    if targets:
        return create_return_to_hand_choice(
            game_state, player, targets, source_card=card,
            prompt="Choose a cost 3 or less Character to return to owner's hand",
            optional=True,
        )
    return True


# --- OP08-043: Edward.Newgate ---
@register_effect("OP08-043", "on_play", "[On Play] If WB leader and ≤2 life, opponent's Characters must trash 2 to attack")
def op08_043_edward_newgate(game_state, player, card):
    if not check_leader_type(player, 'Whitebeard Pirates'):
        return True
    if len(player.life_cards) > 2:
        return True
    opponent = get_opponent(game_state, player)
    for c in opponent.cards_in_play:
        c.attack_trash_cost = getattr(c, 'attack_trash_cost', 0) + 2
        c.attack_trash_cost_expires_on_turn = game_state.turn_count + 1
    game_state._log("Edward.Newgate: opponent's Characters must trash 2 to attack until your turn end")
    return True


# --- OP08-044: Kingdew ---
@register_effect("OP08-044", "activate", "[Activate: Main] [Once Per Turn] Reveal 2 Whitebeard Pirates from hand: +2000 power this turn")
def op08_044_kingdew(game_state, player, card):
    if getattr(card, 'op08_044_used', False):
        return False
    wb_cards = [c for c in player.hand
                if 'whitebeard pirates' in (getattr(c, 'card_origin', '') or '').lower()]
    if len(wb_cards) < 2:
        return False
    add_power_modifier(card, 2000)
    card.op08_044_used = True
    game_state._log("Kingdew: revealed 2 Whitebeard Pirates, gains +2000 power this turn")
    return True


# --- OP08-045: Thatch ---
@register_effect("OP08-045", "continuous", "[Continuous] If removed by opponent's effect or K.O.'d, trash and draw 1 instead")
def op08_045_thatch(game_state, player, card):
    """Set replacement flag — game engine checks this on KO/removal."""
    card.replacement_on_ko = 'trash_and_draw'
    return True


# --- OP08-046: Shakuyaku ---
@register_effect("OP08-046", "continuous", "[Your Turn] [Once Per Turn] When Character removed by your effect, if opponent has 5+ hand, opponent places 1 at bottom")
def op08_046_shakuyaku(game_state, player, card):
    """Set trigger flag — game engine fires when player removes a character by effect."""
    card.shakuyaku_trigger_active = True
    return True


# --- OP08-047: Jozu ---
@register_effect("OP08-047", "on_play", "[On Play] Return own Character to hand: Return cost 6 or less Character to owner's hand")
def op08_047_jozu(game_state, player, card):
    own_chars = [c for c in player.cards_in_play if c is not card]

    if not own_chars:
        # No cost to pay, but still can return an opponent's
        opponent = get_opponent(game_state, player)
        all_targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 6]
        if all_targets:
            return create_return_to_hand_choice(
                game_state, player, all_targets, source_card=card,
                prompt="Return up to 1 cost 6 or less Character to owner's hand",
                optional=True,
            )
        return True

    snap_own = list(own_chars)

    def _after_return_own(selected):
        if selected:
            idx = int(selected[0])
            if 0 <= idx < len(snap_own):
                t = snap_own[idx]
                _remove_card_instance(player.cards_in_play, t)
                player.hand.append(t)
                game_state._log(f"Jozu: returned {t.name} to hand")
        # Now return up to 1 cost 6 or less from any field
        opponent = get_opponent(game_state, player)
        all_targets = ([c for c in player.cards_in_play if c is not card and (getattr(c, 'cost', 0) or 0) <= 6]
                       + [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 6])
        if all_targets:
            create_return_to_hand_choice(
                game_state, player, all_targets, source_card=card,
                prompt="Return up to 1 cost 6 or less Character to owner's hand",
                optional=True,
            )

    return create_own_character_choice(
        game_state, player, own_chars, source_card=card,
        prompt="You may return 1 of your Characters (other than Jozu) to hand as a cost",
        optional=True,
        callback=_after_return_own,
    )


# --- OP08-049: Speed Jil ---
@register_effect("OP08-049", "on_play", "[On Play] Reveal top card, place top/bottom; if Whitebeard Pirates, gain Rush")
def op08_049_speed_jil(game_state, player, card):
    if not player.deck:
        return True
    top_card = player.deck[0]
    is_wb = 'whitebeard pirates' in (getattr(top_card, 'card_origin', '') or '').lower()
    game_state._log(f"Speed Jil: revealed {top_card.name}" + (" — Whitebeard Pirates!" if is_wb else ""))
    if is_wb:
        card.has_rush = True
        card.has_attacked = False
    # Let player place revealed card at top or bottom
    return reorder_top_cards(game_state, player, 1, source_card=card, allow_top=True)


# --- OP08-050: Namule ---
@register_effect("OP08-050", "blocker", "[Blocker]")
def op08_050_namule_blocker(game_state, player, card):
    card.has_blocker = True
    return True


@register_effect("OP08-050", "on_play", "[On Play] Draw 2, place 2 from hand at top or bottom of deck")
def op08_050_namule_on_play(game_state, player, card):
    draw_cards(player, 2)
    # Player chooses 2 cards from hand to place at top or bottom
    if len(player.hand) >= 2:
        snap = list(player.hand)
        options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})",
                    "card_id": c.id, "card_name": c.name} for i, c in enumerate(snap)]

        def _place_cb(selected):
            # Place selected cards at bottom (top/bottom choice simplified to bottom)
            for sel in sorted([int(s) for s in selected], reverse=True):
                if 0 <= sel < len(snap):
                    c = snap[sel]
                    _remove_card_instance(player.hand, c)
                    player.deck.append(c)
            game_state._log(f"Namule: placed {len(selected)} card(s) at bottom of deck")

        from ..game_engine import PendingChoice
        game_state.pending_choice = PendingChoice(
            choice_id=f"namule_{uuid.uuid4().hex[:8]}",
            choice_type="select_cards",
            prompt="Choose 2 cards from your hand to place at the bottom of your deck",
            options=options,
            min_selections=2, max_selections=2,
            source_card_id=card.id, source_card_name=card.name,
            callback=_place_cb,
            callback_action="place_at_bottom_from_hand",
            callback_data={"player_id": player.player_id, "player_index": _player_index(game_state, player)},
        )
    return True


# --- OP08-051: Buckin ---
@register_effect("OP08-051", "on_play", "[On Play] Edward Weevil gains +2000 power this turn")
def op08_051_buckin(game_state, player, card):
    for c in player.cards_in_play:
        if getattr(c, 'name', '') == 'Edward Weevil':
            add_power_modifier(c, 2000)
            game_state._log(f"Buckin: {c.name} gains +2000 power")
    return True


# --- OP08-052: Portgas.D.Ace ---
@register_effect("OP08-052", "on_play", "[On Play] Reveal top, play Whitebeard Pirates cost 4 or less; place rest top/bottom")
def op08_052_ace(game_state, player, card):
    if not player.deck:
        return True
    top_card = player.deck[0]
    is_wb = 'whitebeard pirates' in (getattr(top_card, 'card_origin', '') or '').lower()
    is_char = getattr(top_card, 'card_type', '') == 'CHARACTER'
    cost_ok = (getattr(top_card, 'cost', 0) or 0) <= 4
    game_state._log(f"Portgas.D.Ace: revealed {top_card.name}")

    if is_wb and is_char and cost_ok:
        # Offer to play it
        targets = [top_card]

        def _play_cb(selected):
            if selected:
                if _remove_card_instance(player.deck, top_card):
                    setattr(top_card, 'played_turn', game_state.turn_count)
                    game_state.play_card_to_field_by_effect(player, top_card)
                    game_state._apply_keywords(top_card)
                    game_state._log(f"Ace: played {top_card.name} from deck")
            else:
                # Place at top or bottom
                reorder_top_cards(game_state, player, 1, source_card=card, allow_top=True)

        return create_play_from_hand_choice(
            game_state, player, targets, source_card=card,
            prompt=f"Play {top_card.name} (Whitebeard Pirates, cost {top_card.cost or 0}) from top of deck?",
            callback=_play_cb,
        )
    # No valid play — place at top or bottom
    return reorder_top_cards(game_state, player, 1, source_card=card, allow_top=True)


# --- OP08-053: Thank You...for Loving Me!! (Event) ---
@register_effect("OP08-053", "on_play", "[Main] If WB leader, look at 3, add Whitebeard Pirates or Monkey.D.Luffy card")
def op08_053_thank_you(game_state, player, card):
    if not check_leader_type(player, 'Whitebeard Pirates'):
        return False
    return search_top_cards(
        game_state, player, 3, add_count=1,
        filter_fn=lambda c: (
            'whitebeard pirates' in (getattr(c, 'card_origin', '') or '').lower()
            or 'monkey.d.luffy' in (getattr(c, 'name', '') or '').lower()
        ),
        source_card=card,
        prompt="Look at top 3. Choose up to 1 Whitebeard Pirates or [Monkey.D.Luffy] to add to hand.",
    )


@register_effect("OP08-053", "trigger", "[Trigger] Draw 1 card")
def op08_053_thank_you_trigger(game_state, player, card):
    draw_cards(player, 1)
    return True


# --- OP08-054: You Can't Take Our King This Early in the Game. (Event) ---
@register_effect("OP08-054", "counter", "[Counter] Leader/Character +3000; reveal top, play WB cost 3 or less; place rest top/bottom")
def op08_054_you_cant_take(game_state, player, card):
    own_all = [player.leader] + list(player.cards_in_play) if player.leader else list(player.cards_in_play)
    own_all = [c for c in own_all if c is not None]

    def _after_buff(selected):
        if selected:
            idx = int(selected[0])
            if 0 <= idx < len(own_all):
                add_power_modifier(own_all[idx], 3000)
                game_state._log(f"{own_all[idx].name} gains +3000 power")
        # Reveal top card and optionally play WB cost 3 or less
        if not player.deck:
            return
        top_card = player.deck[0]
        is_wb = 'whitebeard pirates' in (getattr(top_card, 'card_origin', '') or '').lower()
        is_char = getattr(top_card, 'card_type', '') == 'CHARACTER'
        cost_ok = (getattr(top_card, 'cost', 0) or 0) <= 3
        game_state._log(f"You Can't Take: revealed {top_card.name}")
        if is_wb and is_char and cost_ok:
            def _play_cb(sel):
                if sel:
                    if _remove_card_instance(player.deck, top_card):
                        setattr(top_card, 'played_turn', game_state.turn_count)
                        game_state.play_card_to_field_by_effect(player, top_card)
                        game_state._apply_keywords(top_card)
                        game_state._log(f"You Can't Take: played {top_card.name}")
                else:
                    reorder_top_cards(game_state, player, 1, source_card=card, allow_top=True)
            create_play_from_hand_choice(
                game_state, player, [top_card], source_card=card,
                prompt=f"Play {top_card.name} (WB, cost {top_card.cost or 0}) from deck?",
                callback=_play_cb,
            )
        else:
            reorder_top_cards(game_state, player, 1, source_card=card, allow_top=True)

    if own_all:
        return create_power_effect_choice(
            game_state, player, own_all, 3000, source_card=card,
            prompt="Choose your Leader or Character to give +3000 power this battle",
            callback=_after_buff,
        )
    _after_buff([])
    return True


# --- OP08-055: Phoenix Brand (Event) ---
@register_effect("OP08-055", "on_play", "[Main] Reveal 2 Whitebeard Pirates from hand: Place opponent's cost 6 or less at bottom of deck")
def op08_055_phoenix_brand(game_state, player, card):
    wb_cards = [c for c in player.hand
                if 'whitebeard pirates' in (getattr(c, 'card_origin', '') or '').lower()]
    if len(wb_cards) < 2:
        return False
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 6]
    if targets:
        return create_bottom_deck_choice(
            game_state, player, targets, source_card=card,
            prompt="Choose opponent's cost 6 or less Character to place at bottom of deck",
            min_selections=0,
        )
    return True


# --- OP08-056: Moby Dick (Stage) ---
@register_effect("OP08-056", "trigger", "[Trigger] Play this card")
def op08_056_moby_dick_trigger(game_state, player, card):
    """Trigger: Play Moby Dick from life to field."""
    game_state.play_card_to_field_by_effect(player, card)
    setattr(card, 'played_turn', game_state.turn_count)
    game_state._log("Moby Dick: played from Life to field via Trigger")
    return True


# =============================================================================
# ANIMAL KINGDOM PIRATES + BIG MOM PIRATES — OP08-059 to OP08-077
# =============================================================================

# --- OP08-059: Alber ---
@register_effect("OP08-059", "activate", "[Activate: Main] Trash this: If AKP leader and 10 DON, play King cost 7 or less")
def op08_059_alber(game_state, player, card):
    if not check_leader_type(player, 'Animal Kingdom Pirates'):
        return False
    if len(player.don_pool) < 10:
        return False
    kings = [c for c in player.hand
             if 'king' in (getattr(c, 'name', '') or '').lower()
             and (getattr(c, 'cost', 0) or 0) <= 7
             and getattr(c, 'card_type', '') == 'CHARACTER']
    if not kings:
        return False
    # Trash this character
    _remove_card_instance(player.cards_in_play, card)
    player.trash.append(card)
    game_state._log("Alber: trashed self")
    return create_play_from_hand_choice(
        game_state, player, kings, source_card=card,
        prompt="Choose [King] (cost 7 or less) to play from hand",
    )


# --- OP08-060: King (Character) ---
@register_effect("OP08-060", "on_play", "[On Play] DON!! -1: If opponent has 5+ DON, gain Rush")
def op08_060_king_char(game_state, player, card):
    if len(player.don_pool) < 1:
        return True

    def _after_don():
        opponent = get_opponent(game_state, player)
        if len(opponent.don_pool) >= 5:
            card.has_rush = True
            card.has_attacked = False
            game_state._log("King: gained Rush")

    auto = return_don_to_deck(game_state, player, 1, source_card=card, post_callback=_after_don)
    if auto:
        _after_don()
    return True


# --- OP08-061: Charlotte Oven ---
@register_effect("OP08-061", "on_attack", "[When Attacking] DON!! -1: K.O. opponent's cost 3 or less")
def op08_061_charlotte_oven(game_state, player, card):
    if len(player.don_pool) < 1:
        return False

    def _after_don():
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
        if targets:
            create_ko_choice(game_state, player, targets, source_card=card,
                             prompt="Choose opponent's cost 3 or less Character to K.O.")

    auto = return_don_to_deck(game_state, player, 1, source_card=card, post_callback=_after_don)
    if auto:
        _after_don()
    return True


# --- OP08-062: Charlotte Katakuri (cost 2) ---
@register_effect("OP08-062", "activate", "[Activate: Main] Trash this: If Big Mom leader, play Katakuri cost 3+ ≤ opponent's DON count")
def op08_062_katakuri_2(game_state, player, card):
    if not check_leader_type(player, 'Big Mom Pirates'):
        return False
    opponent = get_opponent(game_state, player)
    opp_don = len(opponent.don_pool)
    katakuris = [c for c in player.hand
                 if getattr(c, 'name', '') == 'Charlotte Katakuri'
                 and (getattr(c, 'cost', 0) or 0) >= 3
                 and (getattr(c, 'cost', 0) or 0) <= opp_don]
    if not katakuris:
        return False
    _remove_card_instance(player.cards_in_play, card)
    player.trash.append(card)
    game_state._log("Charlotte Katakuri (2): trashed self")
    return create_play_from_hand_choice(
        game_state, player, katakuris, source_card=card,
        prompt=f"Choose [Charlotte Katakuri] (cost 3+ and ≤ {opp_don}) to play from hand",
    )


# --- OP08-063: Charlotte Katakuri (cost 6) ---
@register_effect("OP08-063", "on_play", "[On Play] You may turn 1 Life face-down: Add 1 DON!! from deck as active")
def op08_063_katakuri_6(game_state, player, card):
    if not player.life_cards:
        return True

    def _yes_cb(selected):
        if "yes" in selected:
            player.life_cards[-1].is_face_up = False
            game_state._log("Charlotte Katakuri: turned top life card face-down")
            add_don_from_deck(player, 1, set_active=True)
            game_state._log("Charlotte Katakuri: added 1 active DON from deck")

    from ..game_engine import PendingChoice
    game_state.pending_choice = PendingChoice(
        choice_id=f"katakuri6_{uuid.uuid4().hex[:8]}",
        choice_type="yes_no",
        prompt="Turn top Life card face-down to add 1 active DON from deck?",
        options=[
            {"id": "yes", "label": "Yes — turn Life face-down, add 1 active DON", "card_id": "don_opt", "card_name": "DON!!"},
            {"id": "no", "label": "No", "card_id": "don_opt", "card_name": "DON!!"},
        ],
        min_selections=1, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=_yes_cb,
        callback_action="yes_no_choice",
        callback_data={"player_id": player.player_id},
    )
    return True


# --- OP08-064: Charlotte Cracker ---
@register_effect("OP08-064", "activate", "[Activate: Main] [Once Per Turn] DON!! -1: Play Biscuit Warrior from hand")
def op08_064_charlotte_cracker(game_state, player, card):
    if getattr(card, 'op08_064_used', False):
        return False
    biscuits = [c for c in player.hand if getattr(c, 'name', '') == 'Biscuit Warrior']
    if not biscuits or len(player.don_pool) < 1:
        return False

    def _after_don():
        card.op08_064_used = True
        create_play_from_hand_choice(
            game_state, player, biscuits, source_card=card,
            prompt="Choose [Biscuit Warrior] to play from hand",
        )

    auto = return_don_to_deck(game_state, player, 1, source_card=card, post_callback=_after_don)
    if auto:
        _after_don()
    return True


# --- OP08-066: Charlotte Brulee ---
@register_effect("OP08-066", "blocker", "[Blocker]")
def op08_066_brulee_blocker(game_state, player, card):
    card.has_blocker = True
    return True


@register_effect("OP08-066", "on_ko", "[On K.O.] Add 1 DON!! from deck rested")
def op08_066_brulee_on_ko(game_state, player, card):
    added = add_don_from_deck(player, 1, set_active=False)
    if added:
        game_state._log("Charlotte Brulee: added 1 rested DON on K.O.")
    return True


# --- OP08-067: Charlotte Pudding (Character) ---
@register_effect("OP08-067", "continuous", "[Your Turn] [Once Per Turn] When DON returned to deck, add 1 DON rested")
def op08_067_charlotte_pudding_char(game_state, player, card):
    """Sets trigger flag; game engine fires _trigger_on_don_return_effects to check this."""
    card.don_return_trigger_active = True
    return True


# --- OP08-068: Charlotte Perospero ---
@register_effect("OP08-068", "on_ko", "[On K.O.] Add 1 DON!! from deck rested")
def op08_068_perospero_on_ko(game_state, player, card):
    added = add_don_from_deck(player, 1, set_active=False)
    if added:
        game_state._log("Charlotte Perospero: added 1 rested DON on K.O.")
    return True


@register_effect("OP08-068", "trigger", "[Trigger] DON!! -1: Play this card")
def op08_068_perospero_trigger(game_state, player, card):
    """Trigger: Return 1 DON then play this card."""
    if len(player.don_pool) < 1:
        # Play without cost
        if card in player.trash:
            player.trash.remove(card)
        game_state.play_card_to_field_by_effect(player, card)
        setattr(card, 'played_turn', game_state.turn_count)
        game_state._log("Charlotte Perospero: played from Life (no DON cost)")
        return True

    def _after_don():
        if card in player.trash:
            player.trash.remove(card)
        game_state.play_card_to_field_by_effect(player, card)
        setattr(card, 'played_turn', game_state.turn_count)
        game_state._apply_keywords(card)
        game_state._log("Charlotte Perospero: played from Life via Trigger")

    auto = optional_don_return(game_state, player, 1, source_card=card, post_callback=_after_don)
    if auto:
        _after_don()
    return True


# --- OP08-069: Charlotte Linlin (Character) ---
@register_effect("OP08-069", "on_play", "[On Play] DON!! -1, Trash 1: Add life from deck; add opponent's cost 6 or less to their life face-up")
def op08_069_charlotte_linlin(game_state, player, card):
    if len(player.don_pool) < 1:
        return True

    def _after_don():
        # Optionally trash 1 from hand
        if not player.hand:
            _do_effects()
            return
        def _after_trash(selected):
            if selected:
                idx = int(selected[0])
                if 0 <= idx < len(snap_hand):
                    c = snap_hand[idx]
                    _remove_card_instance(player.hand, c)
                    player.trash.append(c)
                    game_state._log(f"Charlotte Linlin: trashed {c.name}")
            _do_effects()

        snap_hand = list(player.hand)
        create_trash_choice(game_state, player, 1, source_card=card,
                            prompt="You may trash 1 card from hand (optional)",
                            callback=_after_trash)

    def _do_effects():
        # Add top deck card to life
        if player.deck:
            top = player.deck.pop(0)
            player.life_cards.append(top)
            game_state._log(f"Charlotte Linlin: added {top.name} to top of life")
        # Add opponent's cost 6 or less to their life face-up
        opponent = get_opponent(game_state, player)
        opp_targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 6]
        if opp_targets:
            create_add_to_life_choice(
                game_state, player, opp_targets, source_card=card,
                prompt="Choose opponent's cost 6 or less Character to add to top/bottom of their life face-up",
                owner="opponent", position="top", face_up=True,
            )

    auto = return_don_to_deck(game_state, player, 1, source_card=card, post_callback=_after_don)
    if auto:
        _after_don()
    return True


# --- OP08-070: Baron Tamago ---
@register_effect("OP08-070", "blocker", "[Blocker]")
def op08_070_baron_tamago_blocker(game_state, player, card):
    card.has_blocker = True
    return True


@register_effect("OP08-070", "on_ko", "[On K.O.] DON!! -1: Play [Viscount Hiyoko] cost 5 or less from hand")
def op08_070_baron_tamago_on_ko(game_state, player, card):
    hiyokos = [c for c in player.hand
               if getattr(c, 'name', '') == 'Viscount Hiyoko'
               and (getattr(c, 'cost', 0) or 0) <= 5]
    if not hiyokos or len(player.don_pool) < 1:
        return True

    def _after_don():
        create_play_from_hand_choice(
            game_state, player, hiyokos, source_card=card,
            prompt="Choose [Viscount Hiyoko] (cost 5 or less) to play from hand",
        )

    auto = optional_don_return(game_state, player, 1, source_card=card, post_callback=_after_don)
    if auto:
        _after_don()
    return True


# --- OP08-071: Count Niwatori ---
@register_effect("OP08-071", "on_ko", "[On K.O.] DON!! -1: Play [Baron Tamago] cost 4 or less from deck")
def op08_071_count_niwatori(game_state, player, card):
    tamagos = [c for c in player.deck
               if getattr(c, 'name', '') == 'Baron Tamago'
               and (getattr(c, 'cost', 0) or 0) <= 4]
    if not tamagos or len(player.don_pool) < 1:
        return True

    def _after_don():
        target = tamagos[0]
        _remove_card_instance(player.deck, target)
        setattr(target, 'played_turn', game_state.turn_count)
        game_state.play_card_to_field_by_effect(player, target)
        game_state._apply_keywords(target)
        random.shuffle(player.deck)
        game_state._log(f"Count Niwatori: played {target.name} from deck")

    auto = optional_don_return(game_state, player, 1, source_card=card, post_callback=_after_don)
    if auto:
        _after_don()
    return True


# --- OP08-072: Biscuit Warrior ---
@register_effect("OP08-072", "blocker", "[Blocker]")
def op08_072_biscuit_warrior(game_state, player, card):
    card.has_blocker = True
    return True


# --- OP08-073: Viscount Hiyoko ---
@register_effect("OP08-073", "on_ko", "[On K.O.] DON!! -1: Play [Count Niwatori] cost 6 or less from deck")
def op08_073_viscount_hiyoko(game_state, player, card):
    niwatoris = [c for c in player.deck
                 if getattr(c, 'name', '') == 'Count Niwatori'
                 and (getattr(c, 'cost', 0) or 0) <= 6]
    if not niwatoris or len(player.don_pool) < 1:
        return True

    def _after_don():
        target = niwatoris[0]
        _remove_card_instance(player.deck, target)
        setattr(target, 'played_turn', game_state.turn_count)
        game_state.play_card_to_field_by_effect(player, target)
        game_state._apply_keywords(target)
        random.shuffle(player.deck)
        game_state._log(f"Viscount Hiyoko: played {target.name} from deck")

    auto = optional_don_return(game_state, player, 1, source_card=card, post_callback=_after_don)
    if auto:
        _after_don()
    return True


# --- OP08-074: Black Maria ---
@register_effect("OP08-074", "activate", "[Activate: Main] [Once Per Turn] If no other Black Maria, add 5 DON rested; equalize at end of turn")
def op08_074_black_maria(game_state, player, card):
    if getattr(card, 'op08_074_used', False):
        return False
    other_bm = [c for c in player.cards_in_play
                if c is not card and getattr(c, 'name', '') == 'Black Maria']
    if other_bm:
        return False
    added = add_don_from_deck(player, 5, set_active=False)
    card.op08_074_used = True
    # Mark for end-of-turn DON equalization
    card.black_maria_equalize = True
    game_state._log(f"Black Maria: added {added} rested DON (will equalize at end of turn)")
    return True


# --- OP08-075: Candy Maiden (Event) ---
@register_effect("OP08-075", "on_play", "[Main] DON!! -1: Rest opponent's cost 2 or less; turn all Life face-down")
def op08_075_candy_maiden(game_state, player, card):
    if len(player.don_pool) < 1:
        return False

    def _after_don():
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play
                   if not c.is_resting and (getattr(c, 'cost', 0) or 0) <= 2]

        def _after_rest(selected):
            if selected:
                idx = int(selected[0])
                snap = targets
                if 0 <= idx < len(snap):
                    snap[idx].is_resting = True
                    game_state._log(f"Candy Maiden: rested {snap[idx].name}")
            # Turn all life face-down
            for lc in player.life_cards:
                lc.is_face_up = False
            game_state._log("Candy Maiden: turned all Life cards face-down")

        if targets:
            create_rest_choice(game_state, player, targets, source_card=card,
                               prompt="Choose opponent's cost 2 or less Character to rest",
                               callback=_after_rest, min_selections=0)
        else:
            _after_rest([])

    auto = return_don_to_deck(game_state, player, 1, source_card=card, post_callback=_after_don)
    if auto:
        _after_don()
    return True


@register_effect("OP08-075", "trigger", "[Trigger] Add 1 DON!! from deck as active")
def op08_075_candy_maiden_trigger(game_state, player, card):
    added = add_don_from_deck(player, 1, set_active=True)
    if added:
        game_state._log("Candy Maiden Trigger: added 1 active DON")
    return True


# --- OP08-076: It's to Die For... (Event) ---
@register_effect("OP08-076", "on_play", "[Main] Add 1 active DON; if opponent has 6000+ power Character, add another active DON")
def op08_076_its_to_die(game_state, player, card):
    add_don_from_deck(player, 1, set_active=True)
    game_state._log("It's to Die For: added 1 active DON")
    opponent = get_opponent(game_state, player)
    has_big = any((getattr(c, 'power', 0) or 0) >= 6000 for c in opponent.cards_in_play)
    if has_big:
        add_don_from_deck(player, 1, set_active=True)
        game_state._log("It's to Die For: opponent has 6000+ power Character — added another active DON")
    return True


@register_effect("OP08-076", "trigger", "[Trigger] Add 1 DON!! from deck as active")
def op08_076_its_to_die_trigger(game_state, player, card):
    added = add_don_from_deck(player, 1, set_active=True)
    if added:
        game_state._log("It's to Die For Trigger: added 1 active DON")
    return True


# --- OP08-077: Conquest of the Sea (Event) ---
@register_effect("OP08-077", "on_play", "[Main] DON!! -2: If AKP or Big Mom leader, K.O. up to 2 opponent's cost 6 or less")
def op08_077_conquest_of_the_sea(game_state, player, card):
    leader_ok = (check_leader_type(player, 'Animal Kingdom Pirates')
                 or check_leader_type(player, 'Big Mom Pirates'))
    if not leader_ok or len(player.don_pool) < 2:
        return False

    def _after_don():
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 6]
        if targets:
            create_ko_choice(game_state, player, targets, source_card=card,
                             prompt="Choose up to 2 of opponent's cost 6 or less Characters to K.O.",
                             min_selections=0, max_selections=2)

    auto = return_don_to_deck(game_state, player, 2, source_card=card, post_callback=_after_don)
    if auto:
        _after_don()
    return True


# =============================================================================
# AKP CHARACTERS + EVENTS (OP08-078 to OP08-097)
# =============================================================================

# OP08-078: Ulti — vanilla (no effect)

# --- OP08-079: Kaido (Character) ---
@register_effect("OP08-079", "activate", "[Activate: Main] [Once Per Turn] Trash 1 from hand: If played this turn, trash opponent's cost 7 or less; opponent trashes 1")
def op08_079_kaido(game_state, player, card):
    if getattr(card, '_op08_079_used', None) == game_state.turn_count:
        return False
    if getattr(card, 'played_turn', -1) != game_state.turn_count:
        return False
    if not player.hand:
        return False

    from ..game_engine import PendingChoice

    snapshot_hand = list(player.hand)
    options = []
    for i, c in enumerate(snapshot_hand):
        options.append({"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})", "card_id": c.id, "card_name": c.name})

    def _after_trash(selected):
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(snapshot_hand):
            target = snapshot_hand[idx]
            if _remove_card_instance(player.hand, target):
                player.trash.append(target)
                game_state._log(f"{player.name} trashed {target.name} from hand")

        card._op08_079_used = game_state.turn_count

        # Trash opponent's cost 7 or less
        opponent = get_opponent(game_state, player)
        opp_targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 7]
        if opp_targets:
            def _after_ko(selected2):
                if selected2:
                    t_idx = int(selected2[0])
                    if 0 <= t_idx < len(opp_targets):
                        t = opp_targets[t_idx]
                        if _remove_card_instance(opponent.cards_in_play, t):
                            opponent.trash.append(t)
                            game_state._log(f"{t.name} was trashed by Kaido's effect")
                # Opponent trashes 1 from hand
                if opponent.hand:
                    trash_from_hand(opponent, 1, game_state, source_card=card)

            game_state.pending_choice = PendingChoice(
                choice_id=f"kaido_trash_{uuid.uuid4().hex[:8]}",
                choice_type="select_target",
                prompt="Choose opponent's Character with cost 7 or less to trash",
                options=[{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(opp_targets)],
                min_selections=0, max_selections=1,
                source_card_id=card.id, source_card_name=card.name,
                callback=_after_ko,
                callback_action="kaido_trash_opp",
                callback_data={"player_id": player.player_id, "target_cards": _serialize_card_refs(opp_targets)},
            )
        else:
            # No valid targets to trash, but opponent still trashes from hand
            if opponent.hand:
                trash_from_hand(opponent, 1, game_state, source_card=card)

    game_state.pending_choice = PendingChoice(
        choice_id=f"kaido_hand_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Trash 1 card from your hand for Kaido's effect",
        options=options,
        min_selections=1, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=_after_trash,
        callback_action="kaido_self_trash",
        callback_data={"player_id": player.player_id, "target_cards": _serialize_card_refs(snapshot_hand)},
    )
    return True


# --- OP08-080: Queen (Character) ---
@register_effect("OP08-080", "on_play", "[On Play] Look at 5, add AKP card other than Queen")
def op08_080_queen(game_state, player, card):
    return search_top_cards(game_state, player, 5, add_count=1,
                            filter_fn=lambda c: 'Animal Kingdom Pirates' in (c.card_origin or '') and c.name != 'Queen',
                            source_card=card,
                            prompt="Look at top 5. Choose an Animal Kingdom Pirates card (not Queen) to add to hand.")


# --- OP08-081: Guernica (Character) ---
@register_effect("OP08-081", "on_attack", "[When Attacking] Place 3 CP cards from trash at bottom: K.O. cost 0")
def op08_081_guernica(game_state, player, card):
    cp_in_trash = [c for c in player.trash if 'CP' in (c.card_origin or '')]
    if len(cp_in_trash) < 3:
        return False

    from ..game_engine import PendingChoice

    snapshot = list(cp_in_trash)
    options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

    def _after_select(selected):
        if len(selected) < 3:
            return
        for sel in selected:
            idx = int(sel)
            if 0 <= idx < len(snapshot):
                t = snapshot[idx]
                if _remove_card_instance(player.trash, t):
                    player.deck.insert(0, t)
        random.shuffle(player.deck[:3])
        game_state._log(f"{player.name} placed 3 CP cards from trash at bottom of deck")

        opponent = get_opponent(game_state, player)
        opp_cost0 = [c for c in opponent.cards_in_play
                     if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 0]
        if opp_cost0:
            create_ko_choice(game_state, player, opp_cost0, source_card=card,
                             prompt="K.O. opponent's Character with cost 0",
                             min_selections=0, max_selections=1)

    game_state.pending_choice = PendingChoice(
        choice_id=f"guernica_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Choose 3 CP cards from trash to place at bottom of deck",
        options=options,
        min_selections=3, max_selections=3,
        source_card_id=card.id, source_card_name=card.name,
        callback=_after_select,
        callback_action="guernica_cp_return",
        callback_data={"player_id": player.player_id},
    )
    return True


# --- OP08-082: Sasaki (Character) ---
@register_effect("OP08-082", "activate", "[Activate: Main] Rest DON and rest this: Opponent's Character -2 cost")
def op08_082_sasaki(game_state, player, card):
    if getattr(card, 'is_resting', False):
        return False
    active_don = [d for d in player.don_pool if d == 'active']
    if not active_don:
        return False

    # Rest 1 DON and rest this character
    for i, d in enumerate(player.don_pool):
        if d == 'active':
            player.don_pool[i] = 'rested'
            break
    card.is_resting = True
    game_state._log(f"{player.name} rested DON!! and {card.name}")

    opponent = get_opponent(game_state, player)
    targets = list(opponent.cards_in_play)
    if targets:
        return create_cost_reduction_choice(game_state, player, targets, -2, source_card=card,
                                            prompt="Choose opponent's Character to give -2 cost")
    return True


# --- OP08-083: Sheepshead (Character) ---
@register_effect("OP08-083", "continuous", "[DON!! x1] [Your Turn] All opponent's Characters -1 cost")
def op08_083_sheepshead(game_state, player, card):
    if getattr(card, 'attached_don', 0) < 1:
        return False
    if game_state.current_player_index != _player_index(game_state, player):
        return False
    opponent = get_opponent(game_state, player)
    for c in opponent.cards_in_play:
        c.cost_modifier = getattr(c, 'cost_modifier', 0) - 1
    return True


# --- OP08-084: Jack (Character) ---
@register_effect("OP08-084", "continuous", "[Continuous] This Character gains +4 cost")
def op08_084_jack_cost(game_state, player, card):
    if not getattr(card, '_jack_cost_applied', False):
        card.cost_modifier = getattr(card, 'cost_modifier', 0) + 4
        card._jack_cost_applied = True
    return True


@register_effect("OP08-084", "activate", "[Activate: Main] Rest this: Draw 1, trash 1, K.O. cost 3 or less")
def op08_084_jack_activate(game_state, player, card):
    if getattr(card, 'is_resting', False):
        return False

    card.is_resting = True
    draw_cards(player, 1, game_state)
    game_state._log(f"{player.name} rested {card.name}, drew 1 card")

    if player.hand:
        from ..game_engine import PendingChoice

        snapshot = list(player.hand)
        options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

        def _after_trash(selected):
            if not selected:
                return
            idx = int(selected[0])
            if 0 <= idx < len(snapshot):
                t = snapshot[idx]
                if _remove_card_instance(player.hand, t):
                    player.trash.append(t)
                    game_state._log(f"{player.name} trashed {t.name} from hand")

            opponent = get_opponent(game_state, player)
            opp_targets = [c for c in opponent.cards_in_play
                           if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 3]
            if opp_targets:
                create_ko_choice(game_state, player, opp_targets, source_card=card,
                                 prompt="K.O. opponent's Character with cost 3 or less",
                                 min_selections=0, max_selections=1)

        game_state.pending_choice = PendingChoice(
            choice_id=f"jack_trash_{uuid.uuid4().hex[:8]}",
            choice_type="select_cards",
            prompt="Trash 1 card from your hand",
            options=options,
            min_selections=1, max_selections=1,
            source_card_id=card.id, source_card_name=card.name,
            callback=_after_trash,
            callback_action="jack_trash",
            callback_data={"player_id": player.player_id},
        )
    return True


# --- OP08-085: Jinbe (Character) ---
@register_effect("OP08-085", "on_attack", "[DON!! x1] [When Attacking] If you have cost 8+ Character, K.O. cost 4 or less")
def op08_085_jinbe(game_state, player, card):
    if getattr(card, 'attached_don', 0) < 1:
        return False
    has_big = any((getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) >= 8
                  for c in player.cards_in_play if c is not card)
    if not has_big:
        return False

    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 4]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                                prompt="K.O. opponent's Character with cost 4 or less",
                                min_selections=0, max_selections=1)
    return False


# --- OP08-086: Ginrummy (Character) ---
@register_effect("OP08-086", "on_play", "[On Play] If opponent has cost 0 Character, draw 2 trash 2")
def op08_086_ginrummy(game_state, player, card):
    opponent = get_opponent(game_state, player)
    has_cost0 = any((getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 0
                    for c in opponent.cards_in_play)
    if not has_cost0:
        return False

    draw_cards(player, 2, game_state)
    game_state._log(f"{player.name} drew 2 cards (Ginrummy)")
    if player.hand:
        trash_from_hand(player, 2, game_state, source_card=card)
    return True


# --- OP08-087: Scratchmen Apoo (Character) ---
@register_effect("OP08-087", "blocker", "[Blocker]")
def op08_087_apoo_blocker(game_state, player, card):
    card.has_blocker = True
    return True


@register_effect("OP08-087", "activate", "[Activate: Main] [Once Per Turn] Opponent's Character -1 cost")
def op08_087_apoo_activate(game_state, player, card):
    if getattr(card, '_op08_087_used', None) == game_state.turn_count:
        return False
    card._op08_087_used = game_state.turn_count

    opponent = get_opponent(game_state, player)
    targets = list(opponent.cards_in_play)
    if targets:
        return create_cost_reduction_choice(game_state, player, targets, -1, source_card=card,
                                            prompt="Choose opponent's Character to give -1 cost",
                                            min_selections=0, max_selections=1)
    return True


# --- OP08-088: Duval (Character) ---
@register_effect("OP08-088", "on_play", "[On Play] Your Character +1 cost until opponent's next turn end")
def op08_088_duval(game_state, player, card):
    targets = [c for c in player.cards_in_play if c is not card]
    if not targets:
        return False

    from ..game_engine import PendingChoice

    snapshot = list(targets)
    options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

    def _callback(selected):
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(snapshot):
            t = snapshot[idx]
            t.cost_modifier = getattr(t, 'cost_modifier', 0) + 1
            t.cost_modifier_expires_on_turn = game_state.turn_count + 1
            game_state._log(f"{t.name} gains +1 cost until end of opponent's next turn")

    game_state.pending_choice = PendingChoice(
        choice_id=f"duval_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Choose your Character to give +1 cost",
        options=options,
        min_selections=0, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=_callback,
        callback_action="duval_cost_up",
        callback_data={"player_id": player.player_id},
    )
    return True


# OP08-089: Basil Hawkins — vanilla (no effect)

# --- OP08-090: Hamlet (Character) ---
@register_effect("OP08-090", "on_play", "[On Play] Play SMILE cost 2 or less from trash")
def op08_090_hamlet(game_state, player, card):
    targets = [c for c in player.trash
               if c.card_type == 'CHARACTER'
               and 'SMILE' in (c.card_origin or '')
               and (c.cost or 0) <= 2]
    if targets:
        return create_play_from_trash_choice(game_state, player, targets, source_card=card,
                                             rest_on_play=False,
                                             prompt="Play a SMILE Character with cost 2 or less from trash")
    return False


# --- OP08-091: Who's.Who (Character) ---
@register_effect("OP08-091", "on_play", "[On Play] Trash 1 from hand: K.O. cost 3 or less")
def op08_091_whos_who(game_state, player, card):
    if not player.hand:
        return False

    from ..game_engine import PendingChoice

    snapshot = list(player.hand)
    options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

    def _after_trash(selected):
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(snapshot):
            t = snapshot[idx]
            if _remove_card_instance(player.hand, t):
                player.trash.append(t)
                game_state._log(f"{player.name} trashed {t.name} from hand")

        opponent = get_opponent(game_state, player)
        opp_targets = [c for c in opponent.cards_in_play
                       if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 3]
        if opp_targets:
            create_ko_choice(game_state, player, opp_targets, source_card=card,
                             prompt="K.O. opponent's Character with cost 3 or less",
                             min_selections=0, max_selections=1)

    game_state.pending_choice = PendingChoice(
        choice_id=f"whos_who_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="You may trash 1 card from hand for Who's.Who's effect",
        options=options,
        min_selections=0, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=_after_trash,
        callback_action="whos_who_trash",
        callback_data={"player_id": player.player_id},
    )
    return True


@register_effect("OP08-091", "trigger", "[Trigger] K.O. opponent's cost 3 or less")
def op08_091_whos_who_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 3]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                                prompt="K.O. opponent's Character with cost 3 or less",
                                min_selections=0, max_selections=1)
    return False


# --- OP08-092: Page One (Character) ---
@register_effect("OP08-092", "on_play", "[On Play] Play Ulti cost 4 or less from trash")
def op08_092_page_one(game_state, player, card):
    targets = [c for c in player.trash
               if c.card_type == 'CHARACTER'
               and c.name == 'Ulti'
               and (c.cost or 0) <= 4]
    if targets:
        return create_play_from_trash_choice(game_state, player, targets, source_card=card,
                                             rest_on_play=False,
                                             prompt="Play [Ulti] with cost 4 or less from trash")
    return False


# --- OP08-093: X.Drake (Character) ---
@register_effect("OP08-093", "continuous", "[DON!! x1] This Character gains +2 cost")
def op08_093_xdrake(game_state, player, card):
    if getattr(card, 'attached_don', 0) >= 1:
        card.cost_modifier = getattr(card, 'cost_modifier', 0) + 2
    return True


# --- OP08-094: Imperial Flame (Event) ---
@register_effect("OP08-094", "on_play", "[Main]/[Counter] Place 3 from trash at bottom: K.O. cost 2 or less")
def op08_094_imperial_flame(game_state, player, card):
    if len(player.trash) < 3:
        return False

    from ..game_engine import PendingChoice

    snapshot = list(player.trash)
    options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

    def _after_select(selected):
        if len(selected) < 3:
            return
        for sel in selected:
            idx = int(sel)
            if 0 <= idx < len(snapshot):
                t = snapshot[idx]
                if _remove_card_instance(player.trash, t):
                    player.deck.insert(0, t)
        game_state._log(f"{player.name} placed 3 cards from trash at bottom of deck")

        opponent = get_opponent(game_state, player)
        opp_targets = [c for c in opponent.cards_in_play
                       if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 2]
        if opp_targets:
            create_ko_choice(game_state, player, opp_targets, source_card=card,
                             prompt="K.O. opponent's Character with cost 2 or less",
                             min_selections=0, max_selections=1)

    game_state.pending_choice = PendingChoice(
        choice_id=f"imperial_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="You may choose 3 cards from trash to place at bottom of deck",
        options=options,
        min_selections=0, max_selections=3,
        source_card_id=card.id, source_card_name=card.name,
        callback=_after_select,
        callback_action="imperial_flame_return",
        callback_data={"player_id": player.player_id},
    )
    return True


@register_effect("OP08-094", "counter", "[Counter] Place 3 from trash at bottom: K.O. cost 2 or less")
def op08_094_imperial_flame_counter(game_state, player, card):
    return op08_094_imperial_flame(game_state, player, card)


@register_effect("OP08-094", "trigger", "[Trigger] Activate this card's Main effect")
def op08_094_imperial_flame_trigger(game_state, player, card):
    return op08_094_imperial_flame(game_state, player, card)


# --- OP08-095: Iron Body Fang Flash (Event) ---
@register_effect("OP08-095", "on_play", "[Main] If 10+ trash, your Character +2000 until opponent's next turn end")
def op08_095_iron_body(game_state, player, card):
    if len(player.trash) < 10:
        return False

    targets = list(player.cards_in_play)
    if not targets:
        return False

    from ..game_engine import PendingChoice

    snapshot = list(targets)
    options = [{"id": str(i), "label": f"{c.name} (Power: {c.power or 0})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

    def _callback(selected):
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(snapshot):
            t = snapshot[idx]
            t.power_modifier = getattr(t, 'power_modifier', 0) + 2000
            t._sticky_power_modifier = getattr(t, '_sticky_power_modifier', 0) + 2000
            t.power_modifier_expires_on_turn = game_state.turn_count + 1
            game_state._log(f"{t.name} gains +2000 power until end of opponent's next turn")

    game_state.pending_choice = PendingChoice(
        choice_id=f"iron_body_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Choose your Character to give +2000 power until opponent's next turn end",
        options=options,
        min_selections=0, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=_callback,
        callback_action="iron_body_power",
        callback_data={"player_id": player.player_id},
    )
    return True


@register_effect("OP08-095", "trigger", "[Trigger] Leader/Character +2000 power this turn")
def op08_095_iron_body_trigger(game_state, player, card):
    targets = [player.leader] + list(player.cards_in_play) if player.leader else list(player.cards_in_play)
    targets = [t for t in targets if t is not None]
    if targets:
        return create_power_effect_choice(game_state, player, targets, 2000, source_card=card,
                                          prompt="Choose Leader or Character to give +2000 power",
                                          min_selections=0, max_selections=1)
    return False


# --- OP08-096: People's Dreams Don't Ever End!! (Event) ---
@register_effect("OP08-096", "counter", "[Counter] Trash deck top; if cost 6+, Leader/Character +5000 during battle")
def op08_096_peoples_dreams(game_state, player, card):
    if not player.deck:
        return False

    trashed = player.deck.pop()
    player.trash.append(trashed)
    game_state._log(f"{player.name} trashed {trashed.name} from top of deck")

    if (getattr(trashed, 'cost', 0) or 0) >= 6:
        targets = [player.leader] + list(player.cards_in_play) if player.leader else list(player.cards_in_play)
        targets = [t for t in targets if t is not None]
        if targets:
            return create_power_effect_choice(game_state, player, targets, 5000, source_card=card,
                                              prompt="Choose Leader or Character to give +5000 power",
                                              min_selections=0, max_selections=1)
    return True


@register_effect("OP08-096", "trigger", "[Trigger] Play black Character cost 3 or less from trash")
def op08_096_peoples_dreams_trigger(game_state, player, card):
    targets = [c for c in player.trash
               if c.card_type == 'CHARACTER'
               and (c.cost or 0) <= 3
               and 'black' in (getattr(c, 'color', '') or '').lower()]
    # Fallback: check card_origin or color field patterns
    if not targets:
        targets = [c for c in player.trash
                   if c.card_type == 'CHARACTER' and (c.cost or 0) <= 3]
    if targets:
        return create_play_from_trash_choice(game_state, player, targets, source_card=card,
                                             prompt="Play a black Character with cost 3 or less from trash")
    return False


# --- OP08-097: Heliceratops (Event) ---
@register_effect("OP08-097", "on_play", "[Main] If AKP leader, opponent's Character -2 cost, then K.O. cost 0")
def op08_097_heliceratops(game_state, player, card):
    if not check_leader_type(player, 'Animal Kingdom Pirates'):
        return False

    opponent = get_opponent(game_state, player)
    targets = list(opponent.cards_in_play)
    if not targets:
        return False

    from ..game_engine import PendingChoice

    snapshot = list(targets)
    options = [{"id": str(i), "label": f"{c.name} (Cost: {(c.cost or 0) + getattr(c, 'cost_modifier', 0)})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

    def _after_cost_reduce(selected):
        if selected:
            idx = int(selected[0])
            if 0 <= idx < len(snapshot):
                t = snapshot[idx]
                t.cost_modifier = getattr(t, 'cost_modifier', 0) - 2
                game_state._log(f"{t.name} gets -2 cost this turn")

        # Then K.O. cost 0
        opp_cost0 = [c for c in opponent.cards_in_play
                     if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 0]
        if opp_cost0:
            create_ko_choice(game_state, player, opp_cost0, source_card=card,
                             prompt="K.O. opponent's Character with cost 0",
                             min_selections=0, max_selections=1)

    game_state.pending_choice = PendingChoice(
        choice_id=f"heliceratops_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Choose opponent's Character to give -2 cost",
        options=options,
        min_selections=0, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=_after_cost_reduce,
        callback_action="heliceratops_cost",
        callback_data={"player_id": player.player_id},
    )
    return True


@register_effect("OP08-097", "trigger", "[Trigger] K.O. opponent's cost 3 or less")
def op08_097_heliceratops_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 3]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                                prompt="K.O. opponent's Character with cost 3 or less",
                                min_selections=0, max_selections=1)
    return False


# =============================================================================
# SHANDIAN / BIG MOM / EGGHEAD / SEC BLOCK (OP08-099 to OP08-119)
# =============================================================================

# OP08-099: Kalgara (Character) — vanilla (cost 6, power 8000)

# --- OP08-100: South Bird (Character) ---
@register_effect("OP08-100", "on_play", "[On Play] Look at 7, play Upper Yard stage")
def op08_100_south_bird(game_state, player, card):
    return search_top_cards(game_state, player, 7, add_count=1,
                            filter_fn=lambda c: c.name == 'Upper Yard' and c.card_type == 'STAGE',
                            source_card=card, play_to_field=True,
                            prompt="Look at top 7. Choose [Upper Yard] to play.")


# --- OP08-101: Charlotte Angel (Character) ---
@register_effect("OP08-101", "activate", "[Activate: Main] [Once Per Turn] Trash life top: If BM leader, add deck top to life at end of turn")
def op08_101_charlotte_angel(game_state, player, card):
    if getattr(card, '_op08_101_used', None) == game_state.turn_count:
        return False
    if not check_leader_type(player, 'Big Mom Pirates'):
        return False
    if not player.life_cards:
        return False

    card._op08_101_used = game_state.turn_count
    trashed = player.life_cards.pop()
    player.trash.append(trashed)
    game_state._log(f"{player.name} trashed top life card")

    # Register end-of-turn effect to add deck top to life
    if not hasattr(game_state, '_end_of_turn_hooks'):
        game_state._end_of_turn_hooks = []

    def _add_to_life():
        if player.deck:
            top = player.deck.pop()
            player.life_cards.append(top)
            game_state._log(f"{player.name} added a card from deck to Life (Charlotte Angel)")

    game_state._end_of_turn_hooks.append(_add_to_life)
    return True


# --- OP08-102: Charlotte Opera (Character) ---
@register_effect("OP08-102", "on_play", "[On Play] Trash from hand: K.O. cost <= life count")
def op08_102_charlotte_opera(game_state, player, card):
    if not player.hand:
        return False

    from ..game_engine import PendingChoice

    snapshot = list(player.hand)
    options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

    def _after_trash(selected):
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(snapshot):
            t = snapshot[idx]
            if _remove_card_instance(player.hand, t):
                player.trash.append(t)
                game_state._log(f"{player.name} trashed {t.name} from hand")

        life_count = len(player.life_cards)
        opponent = get_opponent(game_state, player)
        opp_targets = [c for c in opponent.cards_in_play
                       if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= life_count]
        if opp_targets:
            create_ko_choice(game_state, player, opp_targets, source_card=card,
                             prompt=f"K.O. opponent's Character with cost {life_count} or less",
                             min_selections=0, max_selections=1)

    game_state.pending_choice = PendingChoice(
        choice_id=f"opera_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="You may trash 1 card from hand for Charlotte Opera's effect",
        options=options,
        min_selections=0, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=_after_trash,
        callback_action="opera_trash",
        callback_data={"player_id": player.player_id},
    )
    return True


# --- OP08-103: Charlotte Custard (Character) ---
@register_effect("OP08-103", "activate", "[Activate: Main] [Once Per Turn] Add life to hand: Character +1000 until opponent's next turn end")
def op08_103_charlotte_custard(game_state, player, card):
    if getattr(card, '_op08_103_used', None) == game_state.turn_count:
        return False
    if not player.life_cards:
        return False

    card._op08_103_used = game_state.turn_count

    # Add top life to hand
    life_card = player.life_cards.pop()
    player.hand.append(life_card)
    game_state._log(f"{player.name} added life card to hand (Charlotte Custard)")

    targets = list(player.cards_in_play)
    if targets:
        from ..game_engine import PendingChoice

        snapshot = list(targets)
        options = [{"id": str(i), "label": f"{c.name} (Power: {c.power or 0})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

        def _callback(selected):
            if not selected:
                return
            idx = int(selected[0])
            if 0 <= idx < len(snapshot):
                t = snapshot[idx]
                t.power_modifier = getattr(t, 'power_modifier', 0) + 1000
                t._sticky_power_modifier = getattr(t, '_sticky_power_modifier', 0) + 1000
                t.power_modifier_expires_on_turn = game_state.turn_count + 1
                game_state._log(f"{t.name} gains +1000 power until end of opponent's next turn")

        game_state.pending_choice = PendingChoice(
            choice_id=f"custard_{uuid.uuid4().hex[:8]}",
            choice_type="select_target",
            prompt="Choose your Character to give +1000 power until opponent's next turn end",
            options=options,
            min_selections=0, max_selections=1,
            source_card_id=card.id, source_card_name=card.name,
            callback=_callback,
            callback_action="custard_power",
            callback_data={"player_id": player.player_id},
        )
    return True


# --- OP08-104: Charlotte Poire (Character) ---
@register_effect("OP08-104", "trigger", "[Trigger] Trash from hand: Play this card, draw 1")
def op08_104_charlotte_poire(game_state, player, card):
    if not player.hand:
        return False

    from ..game_engine import PendingChoice

    snapshot = list(player.hand)
    options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

    def _after_trash(selected):
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(snapshot):
            t = snapshot[idx]
            if _remove_card_instance(player.hand, t):
                player.trash.append(t)
                game_state._log(f"{player.name} trashed {t.name} from hand")

        # Play this card (it's a trigger card, so it's in trash after trigger)
        if _remove_card_instance(player.trash, card):
            game_state.play_card_to_field_by_effect(player, card)
            card.is_resting = False
            setattr(card, 'played_turn', game_state.turn_count)
            game_state._log(f"{player.name} played {card.name} from trigger")

        draw_cards(player, 1, game_state)

    game_state.pending_choice = PendingChoice(
        choice_id=f"poire_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="You may trash 1 card from hand to play Charlotte Poire and draw 1",
        options=options,
        min_selections=0, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=_after_trash,
        callback_action="poire_trigger",
        callback_data={"player_id": player.player_id},
    )
    return True


# --- OP08-105: Jewelry Bonney (Character) ---
@register_effect("OP08-105", "continuous", "[DON!! x1] [Your Turn] [Once Per Turn] When card removed from opponent's Life, draw 2 trash 1")
def op08_105_jewelry_bonney(game_state, player, card):
    # This is a reactive/event-based effect. We register it as continuous but it
    # only fires via a hook when opponent's life is removed. Mark as placeholder.
    if getattr(card, 'attached_don', 0) < 1:
        return False
    if game_state.current_player_index != _player_index(game_state, player):
        return False
    # Mark as having the bonney effect active
    card._bonney_active = True
    return True


@register_effect("OP08-105", "trigger", "[Trigger] Draw 2, trash 1")
def op08_105_bonney_trigger(game_state, player, card):
    draw_cards(player, 2, game_state)
    if player.hand:
        trash_from_hand(player, 1, game_state, source_card=card)
    return True


# --- OP08-106: Nami (Character) ---
@register_effect("OP08-106", "on_play", "[On Play] Trash Trigger card from hand: K.O. cost 5 or less; if 3 or less hand, draw 1")
def op08_106_nami(game_state, player, card):
    trigger_cards = [c for c in player.hand if c.effect and '[Trigger]' in c.effect]
    if not trigger_cards:
        return False

    from ..game_engine import PendingChoice

    snapshot = list(trigger_cards)
    options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

    def _after_trash(selected):
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(snapshot):
            t = snapshot[idx]
            if _remove_card_instance(player.hand, t):
                player.trash.append(t)
                game_state._log(f"{player.name} trashed {t.name} (Trigger card) from hand")

        opponent = get_opponent(game_state, player)
        opp_targets = [c for c in opponent.cards_in_play
                       if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 5]

        def _after_ko(selected2):
            if selected2:
                t_idx = int(selected2[0])
                if 0 <= t_idx < len(opp_targets):
                    game_state._attempt_character_ko(opp_targets[t_idx], by_effect=True)
            if len(player.hand) <= 3:
                draw_cards(player, 1, game_state)
                game_state._log(f"{player.name} drew 1 card (Nami, ≤3 hand)")

        if opp_targets:
            game_state.pending_choice = PendingChoice(
                choice_id=f"nami_ko_{uuid.uuid4().hex[:8]}",
                choice_type="select_target",
                prompt="K.O. opponent's Character with cost 5 or less",
                options=[{"id": str(i), "label": f"{c.name} (Cost: {(c.cost or 0) + getattr(c, 'cost_modifier', 0)})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(opp_targets)],
                min_selections=0, max_selections=1,
                source_card_id=card.id, source_card_name=card.name,
                callback=_after_ko,
                callback_action="nami_ko",
                callback_data={"player_id": player.player_id, "target_cards": _serialize_card_refs(opp_targets)},
            )
        else:
            if len(player.hand) <= 3:
                draw_cards(player, 1, game_state)

    game_state.pending_choice = PendingChoice(
        choice_id=f"nami_trash_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="You may trash 1 card with [Trigger] from hand for Nami's effect",
        options=options,
        min_selections=0, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=_after_trash,
        callback_action="nami_trash",
        callback_data={"player_id": player.player_id},
    )
    return True


@register_effect("OP08-106", "trigger", "[Trigger] Activate On Play effect")
def op08_106_nami_trigger(game_state, player, card):
    return op08_106_nami(game_state, player, card)


# --- OP08-107: Nitro (Character) ---
@register_effect("OP08-107", "activate", "[Activate: Main] Rest this: Charlotte Pudding +2000 power")
def op08_107_nitro(game_state, player, card):
    if getattr(card, 'is_resting', False):
        return False

    puddings = [c for c in player.cards_in_play if c.name == 'Charlotte Pudding']
    leader_pudding = player.leader if player.leader and player.leader.name == 'Charlotte Pudding' else None
    targets = puddings + ([leader_pudding] if leader_pudding else [])
    if not targets:
        return False

    card.is_resting = True

    if len(targets) == 1:
        t = targets[0]
        add_power_modifier(t, 2000)
        game_state._log(f"{t.name} gains +2000 power (Nitro)")
        return True

    return create_power_effect_choice(game_state, player, targets, 2000, source_card=card,
                                      prompt="Choose [Charlotte Pudding] to give +2000 power",
                                      min_selections=1, max_selections=1)


# OP08-108: Mont Blanc Cricket — vanilla (no effect)

# --- OP08-109: Mont Blanc Noland (Character) ---
@register_effect("OP08-109", "on_play", "[On Play] If Shandian Warrior leader and Kalgara Character, add deck top to life")
def op08_109_noland(game_state, player, card):
    if not check_leader_type(player, 'Shandian Warrior'):
        return False
    has_kalgara = any(c.name == 'Kalgara' for c in player.cards_in_play)
    if not has_kalgara:
        return False
    if player.deck:
        top = player.deck.pop()
        player.life_cards.append(top)
        game_state._log(f"{player.name} added a card from deck to Life (Mont Blanc Noland)")
    return True


# --- OP08-110: Wyper (Character) ---
@register_effect("OP08-110", "on_play", "[On Play] Look at 5, add Upper Yard to hand, play Upper Yard from hand")
def op08_110_wyper(game_state, player, card):
    from ..game_engine import PendingChoice

    def _after_search():
        # After searching, let player play Upper Yard from hand
        upper_yards = [c for c in player.hand if c.name == 'Upper Yard' and c.card_type == 'STAGE']
        if upper_yards:
            create_play_from_hand_choice(game_state, player, upper_yards, source_card=card,
                                          prompt="Play [Upper Yard] from your hand")

    return search_top_cards(game_state, player, 5, add_count=1,
                            filter_fn=lambda c: c.name == 'Upper Yard',
                            source_card=card, callback=_after_search,
                            prompt="Look at top 5. Choose [Upper Yard] to add to hand.")


# --- OP08-111: S-Shark (Character) ---
@register_effect("OP08-111", "on_attack", "[DON!! x1] [When Attacking] Opponent cannot activate Blocker during this battle")
def op08_111_s_shark(game_state, player, card):
    if getattr(card, 'attached_don', 0) < 1:
        return False
    # Set flag on the pending attack to disable blockers
    if hasattr(game_state, 'pending_attack') and game_state.pending_attack:
        game_state.pending_attack['blocker_disabled'] = True
    game_state._log(f"S-Shark: Opponent cannot activate [Blocker] during this battle")
    return True


@register_effect("OP08-111", "trigger", "[Trigger] Trash from hand: If 2 or less life, play this card")
def op08_111_s_shark_trigger(game_state, player, card):
    if len(player.life_cards) > 2:
        return False
    if not player.hand:
        return False

    from ..game_engine import PendingChoice

    snapshot = list(player.hand)
    options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

    def _after_trash(selected):
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(snapshot):
            t = snapshot[idx]
            if _remove_card_instance(player.hand, t):
                player.trash.append(t)
                game_state._log(f"{player.name} trashed {t.name} from hand")
        if _remove_card_instance(player.trash, card):
            game_state.play_card_to_field_by_effect(player, card)
            card.is_resting = False
            setattr(card, 'played_turn', game_state.turn_count)
            game_state._log(f"{player.name} played {card.name} from trigger")

    game_state.pending_choice = PendingChoice(
        choice_id=f"s_shark_trig_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="You may trash 1 from hand to play S-Shark",
        options=options,
        min_selections=0, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=_after_trash,
        callback_action="s_shark_trigger",
        callback_data={"player_id": player.player_id},
    )
    return True


# --- OP08-112: S-Snake (Character) ---
@register_effect("OP08-112", "on_play", "[On Play] Opponent's cost 6 or less (not Luffy) can't attack until opponent's next turn end")
def op08_112_s_snake(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 6
               and 'Monkey.D.Luffy' not in (c.name or '')]
    if targets:
        return create_cannot_attack_choice(game_state, player, targets, source_card=card,
                                            prompt="Choose opponent's cost 6 or less Character (not Luffy) that can't attack")
    return False


@register_effect("OP08-112", "trigger", "[Trigger] Activate On Play effect")
def op08_112_s_snake_trigger(game_state, player, card):
    return op08_112_s_snake(game_state, player, card)


# --- OP08-113: S-Bear (Character) ---
@register_effect("OP08-113", "trigger", "[Trigger] Trash from hand: If 2 or less life, play this and K.O. cost 3 or less")
def op08_113_s_bear(game_state, player, card):
    if len(player.life_cards) > 2:
        return False
    if not player.hand:
        return False

    from ..game_engine import PendingChoice

    snapshot = list(player.hand)
    options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

    def _after_trash(selected):
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(snapshot):
            t = snapshot[idx]
            if _remove_card_instance(player.hand, t):
                player.trash.append(t)
                game_state._log(f"{player.name} trashed {t.name} from hand")

        if _remove_card_instance(player.trash, card):
            game_state.play_card_to_field_by_effect(player, card)
            card.is_resting = False
            setattr(card, 'played_turn', game_state.turn_count)
            game_state._log(f"{player.name} played {card.name} from trigger")

        opponent = get_opponent(game_state, player)
        opp_targets = [c for c in opponent.cards_in_play
                       if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 3]
        if opp_targets:
            create_ko_choice(game_state, player, opp_targets, source_card=card,
                             prompt="K.O. opponent's Character with cost 3 or less",
                             min_selections=0, max_selections=1)

    game_state.pending_choice = PendingChoice(
        choice_id=f"s_bear_trig_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="You may trash 1 from hand to play S-Bear and K.O. cost 3 or less",
        options=options,
        min_selections=0, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=_after_trash,
        callback_action="s_bear_trigger",
        callback_data={"player_id": player.player_id},
    )
    return True


# --- OP08-114: S-Hawk (Character) ---
@register_effect("OP08-114", "continuous", "[DON!! x1] If less life than opponent, can't be KO'd in battle by Slash, +2000")
def op08_114_s_hawk(game_state, player, card):
    if getattr(card, 'attached_don', 0) < 1:
        return False
    opponent = get_opponent(game_state, player)
    if len(player.life_cards) < len(opponent.life_cards):
        card.power_modifier = getattr(card, 'power_modifier', 0) + 2000
        card._ko_immune_slash = True
    return True


@register_effect("OP08-114", "trigger", "[Trigger] Trash from hand: If 2 or less life, play this card")
def op08_114_s_hawk_trigger(game_state, player, card):
    if len(player.life_cards) > 2:
        return False
    if not player.hand:
        return False

    from ..game_engine import PendingChoice

    snapshot = list(player.hand)
    options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

    def _after_trash(selected):
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(snapshot):
            t = snapshot[idx]
            if _remove_card_instance(player.hand, t):
                player.trash.append(t)
                game_state._log(f"{player.name} trashed {t.name} from hand")
        if _remove_card_instance(player.trash, card):
            game_state.play_card_to_field_by_effect(player, card)
            card.is_resting = False
            setattr(card, 'played_turn', game_state.turn_count)
            game_state._log(f"{player.name} played {card.name} from trigger")

    game_state.pending_choice = PendingChoice(
        choice_id=f"s_hawk_trig_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="You may trash 1 from hand to play S-Hawk",
        options=options,
        min_selections=0, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=_after_trash,
        callback_action="s_hawk_trigger",
        callback_data={"player_id": player.player_id},
    )
    return True


# --- OP08-115: The Earth Will Not Lose! (Event) ---
@register_effect("OP08-115", "counter", "[Counter] If Shandian Warrior leader, +3000 during battle; play Upper Yard from hand")
def op08_115_earth(game_state, player, card):
    if not check_leader_type(player, 'Shandian Warrior'):
        return False

    targets = [player.leader] + list(player.cards_in_play) if player.leader else list(player.cards_in_play)
    targets = [t for t in targets if t is not None]

    from ..game_engine import PendingChoice

    snapshot = list(targets)
    options = [{"id": str(i), "label": f"{c.name} (Power: {c.power or 0})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

    def _after_power(selected):
        if selected:
            idx = int(selected[0])
            if 0 <= idx < len(snapshot):
                t = snapshot[idx]
                add_power_modifier(t, 3000)
                game_state._log(f"{t.name} gains +3000 power during this battle")

        upper_yards = [c for c in player.hand if c.name == 'Upper Yard' and c.card_type == 'STAGE']
        if upper_yards:
            create_play_from_hand_choice(game_state, player, upper_yards, source_card=card,
                                          prompt="Play [Upper Yard] from your hand")

    if targets:
        game_state.pending_choice = PendingChoice(
            choice_id=f"earth_{uuid.uuid4().hex[:8]}",
            choice_type="select_target",
            prompt="Choose Leader or Character to give +3000 power during this battle",
            options=options,
            min_selections=0, max_selections=1,
            source_card_id=card.id, source_card_name=card.name,
            callback=_after_power,
            callback_action="earth_power",
            callback_data={"player_id": player.player_id},
        )
    return True


@register_effect("OP08-115", "trigger", "[Trigger] Draw 2, trash 1")
def op08_115_earth_trigger(game_state, player, card):
    draw_cards(player, 2, game_state)
    if player.hand:
        trash_from_hand(player, 1, game_state, source_card=card)
    return True


# --- OP08-116: Burn Bazooka (Event) ---
@register_effect("OP08-116", "counter", "[Counter] +4000; add life top/bottom to hand, add Shandian Warrior from hand to life face-up")
def op08_116_burn_bazooka(game_state, player, card):
    targets = [player.leader] + list(player.cards_in_play) if player.leader else list(player.cards_in_play)
    targets = [t for t in targets if t is not None]

    from ..game_engine import PendingChoice

    snapshot = list(targets)
    options = [{"id": str(i), "label": f"{c.name} (Power: {c.power or 0})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

    def _after_power(selected):
        if selected:
            idx = int(selected[0])
            if 0 <= idx < len(snapshot):
                t = snapshot[idx]
                add_power_modifier(t, 4000)
                game_state._log(f"{t.name} gains +4000 power during this battle")

        # May add life from top or bottom to hand
        if player.life_cards:
            life_opts = [{"id": "top", "label": "Add top Life card to hand"},
                         {"id": "bottom", "label": "Add bottom Life card to hand"},
                         {"id": "skip", "label": "Don't add Life to hand"}]

            def _after_life_pick(selected2):
                if not selected2 or selected2[0] == 'skip':
                    return
                if selected2[0] == 'top' and player.life_cards:
                    lc = player.life_cards.pop()
                    player.hand.append(lc)
                    game_state._log(f"{player.name} added top Life to hand")
                elif selected2[0] == 'bottom' and player.life_cards:
                    lc = player.life_cards.pop(0)
                    player.hand.append(lc)
                    game_state._log(f"{player.name} added bottom Life to hand")

                # Add Shandian Warrior from hand to life face-up
                sw_cards = [c for c in player.hand if 'Shandian Warrior' in (c.card_origin or '')]
                if sw_cards:
                    sw_snapshot = list(sw_cards)
                    sw_options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(sw_snapshot)]

                    def _after_sw(selected3):
                        if not selected3:
                            return
                        sidx = int(selected3[0])
                        if 0 <= sidx < len(sw_snapshot):
                            sw = sw_snapshot[sidx]
                            if _remove_card_instance(player.hand, sw):
                                setattr(sw, 'is_face_up', True)
                                player.life_cards.append(sw)
                                game_state._log(f"{player.name} added {sw.name} to Life face-up")

                    game_state.pending_choice = PendingChoice(
                        choice_id=f"burn_sw_{uuid.uuid4().hex[:8]}",
                        choice_type="select_cards",
                        prompt="Choose a Shandian Warrior card from hand to add to Life face-up",
                        options=sw_options,
                        min_selections=0, max_selections=1,
                        source_card_id=card.id, source_card_name=card.name,
                        callback=_after_sw,
                        callback_action="burn_bazooka_sw",
                        callback_data={"player_id": player.player_id},
                    )

            game_state.pending_choice = PendingChoice(
                choice_id=f"burn_life_{uuid.uuid4().hex[:8]}",
                choice_type="select_target",
                prompt="Add a Life card to your hand?",
                options=life_opts,
                min_selections=1, max_selections=1,
                source_card_id=card.id, source_card_name=card.name,
                callback=_after_life_pick,
                callback_action="burn_bazooka_life",
                callback_data={"player_id": player.player_id},
            )

    if targets:
        game_state.pending_choice = PendingChoice(
            choice_id=f"burn_{uuid.uuid4().hex[:8]}",
            choice_type="select_target",
            prompt="Choose Leader or Character to give +4000 power during this battle",
            options=options,
            min_selections=0, max_selections=1,
            source_card_id=card.id, source_card_name=card.name,
            callback=_after_power,
            callback_action="burn_bazooka_power",
            callback_data={"player_id": player.player_id},
        )
    return True


# --- OP08-117: Burn Blade (Event) ---
@register_effect("OP08-117", "on_play", "[Main] Trash life top: K.O. cost 7 or less")
def op08_117_burn_blade(game_state, player, card):
    if not player.life_cards:
        return False

    from ..game_engine import PendingChoice

    def _after_confirm(selected):
        if not selected or selected[0] == 'no':
            return
        trashed = player.life_cards.pop()
        player.trash.append(trashed)
        game_state._log(f"{player.name} trashed top Life card (Burn Blade)")

        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play
                   if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 7]
        if targets:
            create_ko_choice(game_state, player, targets, source_card=card,
                             prompt="K.O. opponent's Character with cost 7 or less",
                             min_selections=0, max_selections=1)

    game_state.pending_choice = PendingChoice(
        choice_id=f"burn_blade_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Trash top Life card to K.O. opponent's cost 7 or less?",
        options=[{"id": "yes", "label": "Yes, trash Life"}, {"id": "no", "label": "No, skip"}],
        min_selections=1, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=_after_confirm,
        callback_action="burn_blade_confirm",
        callback_data={"player_id": player.player_id},
    )
    return True


@register_effect("OP08-117", "trigger", "[Trigger] Add life top to hand; add hand card to life top")
def op08_117_burn_blade_trigger(game_state, player, card):
    if not player.life_cards:
        return False

    from ..game_engine import PendingChoice

    def _after_confirm(selected):
        if not selected or selected[0] == 'no':
            return
        lc = player.life_cards.pop()
        player.hand.append(lc)
        game_state._log(f"{player.name} added top Life to hand (Burn Blade trigger)")

        if player.hand:
            snap = list(player.hand)
            opts = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snap)]

            def _after_place(sel2):
                if not sel2:
                    return
                idx2 = int(sel2[0])
                if 0 <= idx2 < len(snap):
                    placed = snap[idx2]
                    if _remove_card_instance(player.hand, placed):
                        player.life_cards.append(placed)
                        game_state._log(f"{player.name} added {placed.name} to top of Life")

            game_state.pending_choice = PendingChoice(
                choice_id=f"burn_blade_place_{uuid.uuid4().hex[:8]}",
                choice_type="select_cards",
                prompt="Choose a card from hand to add to top of Life",
                options=opts,
                min_selections=0, max_selections=1,
                source_card_id=card.id, source_card_name=card.name,
                callback=_after_place,
                callback_action="burn_blade_place",
                callback_data={"player_id": player.player_id},
            )

    game_state.pending_choice = PendingChoice(
        choice_id=f"burn_blade_trig_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Add top Life to hand? (Then add a card from hand to Life)",
        options=[{"id": "yes", "label": "Yes"}, {"id": "no", "label": "No"}],
        min_selections=1, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=_after_confirm,
        callback_action="burn_blade_trig_confirm",
        callback_data={"player_id": player.player_id},
    )
    return True


# --- OP08-118: Silvers Rayleigh (Character, SEC) ---
@register_effect("OP08-118", "on_play", "[On Play] Select 2 opponent's chars: -3000 and -2000 until opponent's turn end; K.O. 3000 or less")
def op08_118_rayleigh(game_state, player, card):
    opponent = get_opponent(game_state, player)
    if not opponent.cards_in_play:
        return False

    from ..game_engine import PendingChoice

    snapshot = list(opponent.cards_in_play)
    options = [{"id": str(i), "label": f"{c.name} (Power: {(c.power or 0) + getattr(c, 'power_modifier', 0)})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

    def _after_select(selected):
        if not selected:
            return

        # First target gets -3000, second gets -2000
        if len(selected) >= 1:
            idx1 = int(selected[0])
            if 0 <= idx1 < len(snapshot):
                t1 = snapshot[idx1]
                t1.power_modifier = getattr(t1, 'power_modifier', 0) - 3000
                t1._sticky_power_modifier = getattr(t1, '_sticky_power_modifier', 0) - 3000
                t1.power_modifier_expires_on_turn = game_state.turn_count + 1
                game_state._log(f"{t1.name} gets -3000 power until end of opponent's next turn")

        if len(selected) >= 2:
            idx2 = int(selected[1])
            if 0 <= idx2 < len(snapshot):
                t2 = snapshot[idx2]
                t2.power_modifier = getattr(t2, 'power_modifier', 0) - 2000
                t2._sticky_power_modifier = getattr(t2, '_sticky_power_modifier', 0) - 2000
                t2.power_modifier_expires_on_turn = game_state.turn_count + 1
                game_state._log(f"{t2.name} gets -2000 power until end of opponent's next turn")

        # K.O. opponent's 3000 power or less
        ko_targets = [c for c in opponent.cards_in_play
                      if (c.power or 0) + getattr(c, 'power_modifier', 0) <= 3000
                      and c.card_type == 'CHARACTER']
        if ko_targets:
            create_ko_choice(game_state, player, ko_targets, source_card=card,
                             prompt="K.O. opponent's Character with 3000 power or less",
                             min_selections=0, max_selections=1)

    game_state.pending_choice = PendingChoice(
        choice_id=f"rayleigh_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Select up to 2 of opponent's Characters (1st gets -3000, 2nd gets -2000)",
        options=options,
        min_selections=0, max_selections=2,
        source_card_id=card.id, source_card_name=card.name,
        callback=_after_select,
        callback_action="rayleigh_debuff",
        callback_data={"player_id": player.player_id, "target_cards": _serialize_card_refs(snapshot)},
    )
    return True


# --- OP08-119: Kaido & Linlin (Character, SEC) ---
@register_effect("OP08-119", "on_attack", "[When Attacking] DON!! -10: K.O. all Characters except this; add deck to life; trash opponent's life")
def op08_119_kaido_linlin(game_state, player, card):
    if len(player.don_pool) < 10:
        return False

    from ..game_engine import PendingChoice

    def _after_confirm(selected):
        if not selected or selected[0] == 'no':
            return

        # Return 10 DON to deck
        returned = 0
        for i in range(len(player.don_pool)):
            if returned >= 10:
                break
            if i < len(player.don_pool):
                player.don_pool.pop(i - returned)
                returned += 1
        game_state._log(f"{player.name} returned 10 DON!! to deck")

        # K.O. all Characters other than this
        opponent = get_opponent(game_state, player)
        for c in list(player.cards_in_play):
            if c is not card:
                _remove_card_instance(player.cards_in_play, c)
                player.trash.append(c)
                game_state._log(f"{c.name} was K.O.'d by Kaido & Linlin's effect")
        for c in list(opponent.cards_in_play):
            _remove_card_instance(opponent.cards_in_play, c)
            opponent.trash.append(c)
            game_state._log(f"{c.name} was K.O.'d by Kaido & Linlin's effect")

        # Add deck top to life
        if player.deck:
            top = player.deck.pop()
            player.life_cards.append(top)
            game_state._log(f"{player.name} added a card from deck to Life")

        # Trash opponent's top life
        if opponent.life_cards:
            trashed = opponent.life_cards.pop()
            opponent.trash.append(trashed)
            game_state._log(f"Trashed top card from {opponent.name}'s Life")

    game_state.pending_choice = PendingChoice(
        choice_id=f"kaido_linlin_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Return 10 DON!! to K.O. all other Characters, add Life, trash opponent's Life?",
        options=[{"id": "yes", "label": "Yes, activate"}, {"id": "no", "label": "No, skip"}],
        min_selections=1, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=_after_confirm,
        callback_action="kaido_linlin_nuke",
        callback_data={"player_id": player.player_id},
    )
    return True
