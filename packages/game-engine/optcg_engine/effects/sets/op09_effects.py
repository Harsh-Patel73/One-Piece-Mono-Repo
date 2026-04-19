"""
Hardcoded effects for OP09 cards — Emperors in the New World.
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

# --- OP09-001: Shanks (Leader) ---
@register_effect("OP09-001", "on_opponent_attack", "[Once Per Turn] When opponent attacks, give opponent's Leader/Character -1000 power")
def op09_001_shanks_leader(game_state, player, card):
    if getattr(card, '_op09_001_used', None) == game_state.turn_count:
        return False
    card._op09_001_used = game_state.turn_count

    opponent = get_opponent(game_state, player)
    targets = []
    if opponent.leader:
        targets.append(opponent.leader)
    targets.extend(opponent.cards_in_play)
    if targets:
        return create_power_effect_choice(game_state, player, targets, -1000, source_card=card,
                                          prompt="Choose opponent's Leader or Character to give -1000 power",
                                          min_selections=0, max_selections=1)
    return False


# --- OP09-022: Lim (Leader) ---
@register_effect("OP09-022", "continuous", "[Continuous] Your Characters are played rested")
def op09_022_lim_continuous(game_state, player, card):
    player.chars_played_rested = True
    return True


@register_effect("OP09-022", "activate", "[Activate: Main] [Once Per Turn] Rest 3 DON: Add 1 DON rested + play ODYSSEY cost 5 or less from hand")
def op09_022_lim_activate(game_state, player, card):
    if getattr(card, '_op09_022_used', None) == game_state.turn_count:
        return False
    active_count = player.don_pool.count('active')
    if active_count < 3:
        return False

    # Rest 3 DON
    rested = 0
    for i in range(len(player.don_pool)):
        if rested >= 3:
            break
        if player.don_pool[i] == 'active':
            player.don_pool[i] = 'rested'
            rested += 1

    card._op09_022_used = game_state.turn_count

    # Add 1 DON rested
    add_don_from_deck(player, 1, set_active=False)
    game_state._log(f"{player.name} rested 3 DON, added 1 DON rested (Lim)")

    # Play ODYSSEY cost 5 or less from hand
    targets = [c for c in player.hand
               if c.card_type == 'CHARACTER'
               and 'ODYSSEY' in (c.card_origin or '')
               and (c.cost or 0) <= 5]
    if targets:
        return create_play_from_hand_choice(game_state, player, targets, source_card=card,
                                             rest_on_play=True,
                                             prompt="Play an ODYSSEY Character (cost 5 or less) from hand")
    return True


# --- OP09-042: Buggy (Leader) ---
@register_effect("OP09-042", "activate", "[Activate: Main] Rest 5 DON, trash 1 from hand: Play Cross Guild Character from hand")
def op09_042_buggy_leader(game_state, player, card):
    active_count = player.don_pool.count('active')
    if active_count < 5:
        return False
    if not player.hand:
        return False

    # Rest 5 DON
    rested = 0
    for i in range(len(player.don_pool)):
        if rested >= 5:
            break
        if player.don_pool[i] == 'active':
            player.don_pool[i] = 'rested'
            rested += 1

    game_state._log(f"{player.name} rested 5 DON (Buggy)")

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

        cg_chars = [c for c in player.hand
                    if c.card_type == 'CHARACTER'
                    and 'Cross Guild' in (c.card_origin or '')]
        if cg_chars:
            create_play_from_hand_choice(game_state, player, cg_chars, source_card=card,
                                          rest_on_play=False,
                                          prompt="Play a Cross Guild Character from hand")

    game_state.pending_choice = PendingChoice(
        choice_id=f"buggy_trash_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Trash 1 card from your hand for Buggy's effect",
        options=options,
        min_selections=1, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=_after_trash,
        callback_action="buggy_trash",
        callback_data={"player_id": player.player_id, "target_cards": _serialize_card_refs(snapshot)},
    )
    return True


# --- OP09-061: Monkey.D.Luffy (Leader) ---
@register_effect("OP09-061", "continuous", "[DON!! x1] All of your Characters gain +1 cost")
def op09_061_luffy_continuous(game_state, player, card):
    if getattr(card, 'attached_don', 0) >= 1:
        for char in player.cards_in_play:
            char.cost_modifier = getattr(char, 'cost_modifier', 0) + 1
        return True
    return False


@register_effect("OP09-061", "on_don_return", "[Your Turn] [Once Per Turn] When 2+ DON returned, add 1 DON active + 1 DON rested")
def op09_061_luffy_don_return(game_state, player, card):
    if getattr(card, '_op09_061_used', None) == game_state.turn_count:
        return False
    if game_state.current_player_index != _player_index(game_state, player):
        return False
    card._op09_061_used = game_state.turn_count
    add_don_from_deck(player, 1, set_active=True)
    add_don_from_deck(player, 1, set_active=False)
    game_state._log(f"{player.name} added 1 active DON + 1 rested DON (Luffy)")
    return True


# --- OP09-062: Nico Robin (Leader) ---
@register_effect("OP09-062", "continuous", "[Banish] This Leader has Banish")
def op09_062_robin_continuous(game_state, player, card):
    card.has_banish = True
    return True


@register_effect("OP09-062", "on_attack", "[When Attacking] Trash Trigger card from hand: Add 1 DON rested")
def op09_062_robin_attack(game_state, player, card):
    trigger_cards = [c for c in player.hand
                     if (getattr(c, 'trigger', '') or getattr(c, 'Trigger', '') or '').strip()]
    if not trigger_cards:
        # Also check Effect field for [Trigger]
        trigger_cards = [c for c in player.hand
                         if '[Trigger]' in (getattr(c, 'effect', '') or getattr(c, 'Effect', '') or '')]
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
                game_state._log(f"{player.name} trashed {t.name} (Trigger card)")
                add_don_from_deck(player, 1, set_active=False)
                game_state._log(f"{player.name} added 1 DON rested (Nico Robin)")

    game_state.pending_choice = PendingChoice(
        choice_id=f"robin_trash_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="You may trash a card with [Trigger] from hand to add 1 DON rested",
        options=options,
        min_selections=0, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=_after_trash,
        callback_action="robin_trigger_trash",
        callback_data={"player_id": player.player_id},
    )
    return True


# --- OP09-081: Marshall.D.Teach (Leader) ---
@register_effect("OP09-081", "continuous", "[Continuous] Your [On Play] effects are negated")
def op09_081_teach_continuous(game_state, player, card):
    player.on_play_negated = True
    return True


@register_effect("OP09-081", "activate", "[Activate: Main] Trash 1 from hand: Opponent's [On Play] negated until opponent's next turn end")
def op09_081_teach_activate(game_state, player, card):
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
        opponent.on_play_negated = True
        game_state._log(f"Opponent's [On Play] effects are negated (Teach)")

    game_state.pending_choice = PendingChoice(
        choice_id=f"teach_trash_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Trash 1 card from hand to negate opponent's [On Play] effects",
        options=options,
        min_selections=1, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=_after_trash,
        callback_action="teach_trash",
        callback_data={"player_id": player.player_id},
    )
    return True


# =============================================================================
# RED-HAIRED PIRATES (OP09-002 to OP09-021)
# =============================================================================

# --- OP09-002: Uta ---
@register_effect("OP09-002", "on_play", "[On Play] Look at 5, add Red-Haired Pirates")
def op09_002_uta(game_state, player, card):
    return search_top_cards(game_state, player, 5, add_count=1,
                            filter_fn=lambda c: 'Red-Haired Pirates' in (c.card_origin or ''),
                            source_card=card,
                            prompt="Look at top 5. Choose a Red-Haired Pirates card to add to hand.")


# --- OP09-003: Shachi & Penguin ---
@register_effect("OP09-003", "on_attack", "[When Attacking] Opponent's Character -2000 power")
def op09_003_shachi_penguin(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = list(opponent.cards_in_play)
    if targets:
        return create_power_effect_choice(game_state, player, targets, -2000, source_card=card,
                                          prompt="Choose opponent's Character to give -2000 power",
                                          min_selections=0, max_selections=1)
    return False


# --- OP09-004: Shanks (Character) ---
@register_effect("OP09-004", "continuous", "[Continuous] All opponent's Characters -1000 power; [Rush]")
def op09_004_shanks(game_state, player, card):
    opponent = get_opponent(game_state, player)
    for c in opponent.cards_in_play:
        c.power_modifier = getattr(c, 'power_modifier', 0) - 1000
    card.has_rush = True
    return True


# --- OP09-005: Silvers Rayleigh ---
@register_effect("OP09-005", "blocker", "[Blocker]")
def op09_005_rayleigh_blocker(game_state, player, card):
    card.has_blocker = True
    return True


@register_effect("OP09-005", "on_play", "[On Play] If opponent has 2+ base 5000 power Characters, draw 2 trash 1")
def op09_005_rayleigh_on_play(game_state, player, card):
    opponent = get_opponent(game_state, player)
    high_power = [c for c in opponent.cards_in_play if (c.power or 0) >= 5000]
    if len(high_power) >= 2:
        draw_cards(player, 2, game_state)
        if player.hand:
            trash_from_hand(player, 1, game_state, source_card=card)
        return True
    return False


# OP09-006: Howling Gab — vanilla

# --- OP09-007: Heat ---
@register_effect("OP09-007", "blocker", "[Blocker]")
def op09_007_heat_blocker(game_state, player, card):
    card.has_blocker = True
    return True


@register_effect("OP09-007", "on_play", "[On Play] Leader with 4000 power or less gains +1000")
def op09_007_heat_on_play(game_state, player, card):
    if player.leader:
        leader_power = (player.leader.power or 0) + getattr(player.leader, 'power_modifier', 0)
        if leader_power <= 4000:
            add_power_modifier(player.leader, 1000)
            game_state._log(f"{player.leader.name} gains +1000 power (Heat)")
            return True
    return False


# --- OP09-008: Building Snake ---
@register_effect("OP09-008", "activate", "[Activate: Main] Place this at bottom of deck: Opponent's Character -3000 power")
def op09_008_building_snake(game_state, player, card):
    if card not in player.cards_in_play:
        return False

    _remove_card_instance(player.cards_in_play, card)
    player.deck.insert(0, card)
    game_state._log(f"{player.name} placed {card.name} at bottom of deck")

    opponent = get_opponent(game_state, player)
    targets = list(opponent.cards_in_play)
    if targets:
        return create_power_effect_choice(game_state, player, targets, -3000, source_card=card,
                                          prompt="Choose opponent's Character to give -3000 power",
                                          min_selections=0, max_selections=1)
    return True


# --- OP09-009: Benn.Beckman ---
@register_effect("OP09-009", "on_play", "[On Play] Trash opponent's Character with 6000 power or less")
def op09_009_beckman(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if (c.power or 0) + getattr(c, 'power_modifier', 0) <= 6000]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                                prompt="Choose opponent's Character with 6000 power or less to trash",
                                min_selections=0, max_selections=1)
    return False


# --- OP09-010: Bonk Punch ---
@register_effect("OP09-010", "on_play", "[On Play] Play [Monster] from hand")
def op09_010_bonk_punch_on_play(game_state, player, card):
    monsters = [c for c in player.hand
                if c.name == 'Monster' and c.card_type == 'CHARACTER']
    if monsters:
        return create_play_from_hand_choice(game_state, player, monsters, source_card=card,
                                             rest_on_play=False,
                                             prompt="Play [Monster] from hand")
    return False


@register_effect("OP09-010", "on_attack", "[DON!! x1] [When Attacking] +2000 power this turn")
def op09_010_bonk_punch_on_attack(game_state, player, card):
    if getattr(card, 'attached_don', 0) >= 1:
        add_power_modifier(card, 2000)
        game_state._log(f"{card.name} gains +2000 power")
        return True
    return False


# --- OP09-011: Hongo ---
@register_effect("OP09-011", "activate", "[Activate: Main] Rest this: If Red-Haired Pirates leader, opponent's Character -2000")
def op09_011_hongo(game_state, player, card):
    if getattr(card, 'is_resting', False):
        return False
    if not check_leader_type(player, 'Red-Haired Pirates'):
        return False

    card.is_resting = True
    opponent = get_opponent(game_state, player)
    targets = list(opponent.cards_in_play)
    if targets:
        return create_power_effect_choice(game_state, player, targets, -2000, source_card=card,
                                          prompt="Choose opponent's Character to give -2000 power",
                                          min_selections=0, max_selections=1)
    return True


# --- OP09-012: Monster ---
@register_effect("OP09-012", "continuous", "[Continuous] If Bonk Punch would be KO'd by effect, may trash this instead")
def op09_012_monster(game_state, player, card):
    card._protects_bonk_punch = True
    return True


# --- OP09-013: Yasopp ---
@register_effect("OP09-013", "on_play", "[On Play] Leader +1000 until opponent's next turn end")
def op09_013_yasopp_on_play(game_state, player, card):
    if player.leader:
        player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 1000
        player.leader._sticky_power_modifier = getattr(player.leader, '_sticky_power_modifier', 0) + 1000
        player.leader.power_modifier_expires_on_turn = game_state.turn_count + 1
        game_state._log(f"{player.leader.name} gains +1000 power until opponent's next turn end")
    return True


@register_effect("OP09-013", "on_attack", "[DON!! x1] [When Attacking] Opponent's Character -1000 power")
def op09_013_yasopp_on_attack(game_state, player, card):
    if getattr(card, 'attached_don', 0) < 1:
        return False
    opponent = get_opponent(game_state, player)
    targets = list(opponent.cards_in_play)
    if targets:
        return create_power_effect_choice(game_state, player, targets, -1000, source_card=card,
                                          prompt="Choose opponent's Character to give -1000 power",
                                          min_selections=0, max_selections=1)
    return False


# --- OP09-014: Limejuice ---
@register_effect("OP09-014", "on_play", "[On Play] Opponent cannot activate 1 Blocker with 4000 power or less this turn")
def op09_014_limejuice(game_state, player, card):
    opponent = get_opponent(game_state, player)
    blockers = [c for c in opponent.cards_in_play
                if getattr(c, 'has_blocker', False)
                and (c.power or 0) + getattr(c, 'power_modifier', 0) <= 4000]
    if not blockers:
        return False

    from ..game_engine import PendingChoice

    snapshot = list(blockers)
    options = [{"id": str(i), "label": f"{c.name} (Power: {(c.power or 0) + getattr(c, 'power_modifier', 0)})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

    def _callback(selected):
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(snapshot):
            t = snapshot[idx]
            t.blocker_disabled = True
            game_state._log(f"{t.name}'s [Blocker] is disabled this turn")

    game_state.pending_choice = PendingChoice(
        choice_id=f"limejuice_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Choose opponent's Blocker with 4000 power or less to disable",
        options=options,
        min_selections=0, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=_callback,
        callback_action="limejuice_disable",
        callback_data={"player_id": player.player_id},
    )
    return True


# --- OP09-015: Lucky.Roux ---
@register_effect("OP09-015", "blocker", "[Blocker]")
def op09_015_lucky_roux_blocker(game_state, player, card):
    card.has_blocker = True
    return True


@register_effect("OP09-015", "on_ko", "[On K.O.] If Red-Haired Pirates leader, K.O. opponent's base 6000 power or less")
def op09_015_lucky_roux_on_ko(game_state, player, card):
    if not check_leader_type(player, 'Red-Haired Pirates'):
        return False
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (c.power or 0) <= 6000]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                                prompt="K.O. opponent's Character with base 6000 power or less",
                                min_selections=0, max_selections=1)
    return False


# OP09-016: Rockstar — vanilla

# --- OP09-017: Wire ---
@register_effect("OP09-017", "continuous", "[DON!! x1] If Kid Pirates leader with 7000+ power, gain Rush")
def op09_017_wire(game_state, player, card):
    if getattr(card, 'attached_don', 0) < 1:
        return False
    if not check_leader_type(player, 'Kid Pirates'):
        return False
    leader_power = (player.leader.power or 0) + getattr(player.leader, 'power_modifier', 0)
    if leader_power >= 7000:
        card.has_rush = True
    return True


# --- OP09-018: Get Out of Here! (Event) ---
@register_effect("OP09-018", "on_play", "[Main] K.O. up to 2 opponent's Characters with total power 4000 or less")
def op09_018_get_out(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = list(opponent.cards_in_play)
    if not targets:
        return False

    from ..game_engine import PendingChoice

    snapshot = list(targets)
    options = [{"id": str(i), "label": f"{c.name} (Power: {(c.power or 0) + getattr(c, 'power_modifier', 0)})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

    def _callback(selected):
        if not selected:
            return
        total_power = 0
        to_ko = []
        for sel in selected:
            idx = int(sel)
            if 0 <= idx < len(snapshot):
                t = snapshot[idx]
                tp = (t.power or 0) + getattr(t, 'power_modifier', 0)
                total_power += tp
                to_ko.append(t)
        if total_power <= 4000:
            for t in to_ko:
                game_state._attempt_character_ko(t, by_effect=True)
        else:
            game_state._log(f"Total power {total_power} exceeds 4000 — cannot K.O.")

    game_state.pending_choice = PendingChoice(
        choice_id=f"get_out_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="K.O. up to 2 opponent's Characters with total power 4000 or less",
        options=options,
        min_selections=0, max_selections=2,
        source_card_id=card.id, source_card_name=card.name,
        callback=_callback,
        callback_action="get_out_ko",
        callback_data={"player_id": player.player_id},
    )
    return True


# --- OP09-019: Nobody Hurts a Friend of Mine!!!! (Event) ---
@register_effect("OP09-019", "on_play", "[Main] If RHP leader, opponent's Character -3000; if opponent has 5000+ power, draw 1")
def op09_019_nobody_hurts(game_state, player, card):
    if not check_leader_type(player, 'Red-Haired Pirates'):
        return False

    opponent = get_opponent(game_state, player)
    targets = list(opponent.cards_in_play)

    from ..game_engine import PendingChoice

    if targets:
        snapshot = list(targets)
        options = [{"id": str(i), "label": f"{c.name} (Power: {(c.power or 0) + getattr(c, 'power_modifier', 0)})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

        def _callback(selected):
            if selected:
                idx = int(selected[0])
                if 0 <= idx < len(snapshot):
                    t = snapshot[idx]
                    add_power_modifier(t, -3000)
                    game_state._log(f"{t.name} gets -3000 power")
            # Check if opponent has 5000+ power character
            has_big = any((c.power or 0) + getattr(c, 'power_modifier', 0) >= 5000
                          for c in opponent.cards_in_play)
            if has_big:
                draw_cards(player, 1, game_state)
                game_state._log(f"{player.name} drew 1 card (opponent has 5000+ power)")

        game_state.pending_choice = PendingChoice(
            choice_id=f"nobody_hurts_{uuid.uuid4().hex[:8]}",
            choice_type="select_target",
            prompt="Choose opponent's Character to give -3000 power",
            options=options,
            min_selections=0, max_selections=1,
            source_card_id=card.id, source_card_name=card.name,
            callback=_callback,
            callback_action="nobody_hurts_power",
            callback_data={"player_id": player.player_id},
        )
        return True
    return False


@register_effect("OP09-019", "trigger", "[Trigger] Draw 1 card")
def op09_019_nobody_hurts_trigger(game_state, player, card):
    draw_cards(player, 1, game_state)
    return True


# --- OP09-020: Come On!! We'll Fight You!! (Event) ---
@register_effect("OP09-020", "on_play", "[Main] Look at 5, add Red-Haired Pirates (not self)")
def op09_020_come_on(game_state, player, card):
    return search_top_cards(game_state, player, 5, add_count=1,
                            filter_fn=lambda c: 'Red-Haired Pirates' in (c.card_origin or '')
                                                and c.name != "Come On!! We'll Fight You!!",
                            source_card=card,
                            prompt="Look at top 5. Choose a Red-Haired Pirates card to add to hand.")


@register_effect("OP09-020", "trigger", "[Trigger] Draw 1 card")
def op09_020_come_on_trigger(game_state, player, card):
    draw_cards(player, 1, game_state)
    return True


# --- OP09-021: Red Force (Stage) ---
@register_effect("OP09-021", "activate", "[Activate: Main] Rest this: If RHP leader, opponent's Character -1000")
def op09_021_red_force(game_state, player, card):
    if getattr(card, 'is_resting', False):
        return False
    if not check_leader_type(player, 'Red-Haired Pirates'):
        return False

    card.is_resting = True
    opponent = get_opponent(game_state, player)
    targets = list(opponent.cards_in_play)
    if targets:
        return create_power_effect_choice(game_state, player, targets, -1000, source_card=card,
                                          prompt="Choose opponent's Character to give -1000 power",
                                          min_selections=0, max_selections=1)
    return True


# =============================================================================
# ODYSSEY CHARACTERS + EVENTS (OP09-023 to OP09-041)
# =============================================================================

# --- OP09-023: Adio ---
@register_effect("OP09-023", "on_play", "[On Play] If ODYSSEY leader, set up to 3 DON active")
def op09_023_adio_on_play(game_state, player, card):
    if not check_leader_type(player, 'ODYSSEY'):
        return False
    activated = 0
    for i in range(len(player.don_pool)):
        if activated >= 3:
            break
        if player.don_pool[i] == 'rested':
            player.don_pool[i] = 'active'
            activated += 1
    if activated > 0:
        game_state._log(f"{player.name} set {activated} DON active (Adio)")
    return True


@register_effect("OP09-023", "on_opponent_attack", "[On Opponent's Attack] [Once Per Turn] Rest 1 DON: Leader/Character +2000 during battle")
def op09_023_adio_defense(game_state, player, card):
    if getattr(card, '_op09_023_used', None) == game_state.turn_count:
        return False
    active_don = player.don_pool.count('active')
    if active_don < 1:
        return False

    # Rest 1 DON
    for i in range(len(player.don_pool)):
        if player.don_pool[i] == 'active':
            player.don_pool[i] = 'rested'
            break

    card._op09_023_used = game_state.turn_count

    targets = []
    if player.leader:
        targets.append(player.leader)
    targets.extend(player.cards_in_play)
    if targets:
        return create_power_effect_choice(game_state, player, targets, 2000, source_card=card,
                                          prompt="Choose Leader or Character to give +2000 power during battle",
                                          min_selections=0, max_selections=1)
    return True


# --- OP09-024: Usopp ---
@register_effect("OP09-024", "on_play", "[On Play] If 2+ rested Characters, draw 2 trash 2")
def op09_024_usopp(game_state, player, card):
    rested = sum(1 for c in player.cards_in_play if getattr(c, 'is_resting', False))
    if rested >= 2:
        draw_cards(player, 2, game_state)
        if player.hand:
            trash_from_hand(player, 2, game_state, source_card=card)
        return True
    return False


# --- OP09-025: Crocodile ---
@register_effect("OP09-025", "continuous", "[Continuous] If ODYSSEY leader, can't be KO'd in battle by Leaders")
def op09_025_crocodile(game_state, player, card):
    if check_leader_type(player, 'ODYSSEY'):
        card.leader_battle_protection = True
    return True


# --- OP09-026: Sakazuki ---
@register_effect("OP09-026", "on_play", "[On Play] If 2+ rested Characters, K.O. cost 5 or less")
def op09_026_sakazuki(game_state, player, card):
    rested = sum(1 for c in player.cards_in_play if getattr(c, 'is_resting', False))
    if rested < 2:
        return False
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 5]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                                prompt="K.O. opponent's Character with cost 5 or less",
                                min_selections=0, max_selections=1)
    return False


# --- OP09-027: Sabo ---
@register_effect("OP09-027", "on_attack", "[When Attacking] [Once Per Turn] If 3+ rested Characters, draw 1")
def op09_027_sabo(game_state, player, card):
    if getattr(card, '_op09_027_used', None) == game_state.turn_count:
        return False
    rested = sum(1 for c in player.cards_in_play if getattr(c, 'is_resting', False) and c is not card)
    if rested >= 3:
        card._op09_027_used = game_state.turn_count
        draw_cards(player, 1, game_state)
        game_state._log(f"{player.name} drew 1 card (Sabo)")
        return True
    return False


# --- OP09-028: Sanji ---
@register_effect("OP09-028", "on_ko", "[On K.O.] Add life to hand: Play ODYSSEY/SHC cost 4 or less from trash rested")
def op09_028_sanji(game_state, player, card):
    if not player.life_cards:
        return False

    from ..game_engine import PendingChoice

    def _after_life_pick(selected):
        if not selected or selected[0] == 'skip':
            return
        if selected[0] == 'top' and player.life_cards:
            lc = player.life_cards.pop()
            player.hand.append(lc)
            game_state._log(f"{player.name} added top Life to hand")
        elif selected[0] == 'bottom' and player.life_cards:
            lc = player.life_cards.pop(0)
            player.hand.append(lc)
            game_state._log(f"{player.name} added bottom Life to hand")
        else:
            return

        # Play ODYSSEY or SHC cost 4 or less from trash rested
        targets = [c for c in player.trash
                   if c.card_type == 'CHARACTER'
                   and (c.cost or 0) <= 4
                   and ('ODYSSEY' in (c.card_origin or '') or 'Straw Hat Crew' in (c.card_origin or ''))]
        if targets:
            create_play_from_trash_choice(game_state, player, targets, source_card=card,
                                          rest_on_play=True,
                                          prompt="Play ODYSSEY or Straw Hat Crew cost 4 or less from trash rested")

    game_state.pending_choice = PendingChoice(
        choice_id=f"sanji_life_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Add a Life card to your hand? (top or bottom)",
        options=[{"id": "top", "label": "Add top Life to hand"},
                 {"id": "bottom", "label": "Add bottom Life to hand"},
                 {"id": "skip", "label": "Skip"}],
        min_selections=1, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=_after_life_pick,
        callback_action="sanji_life_pick",
        callback_data={"player_id": player.player_id},
    )
    return True


# --- OP09-029: Tony Tony.Chopper ---
@register_effect("OP09-029", "end_of_turn", "[End of Your Turn] Set ODYSSEY cost 4 or less active")
def op09_029_chopper(game_state, player, card):
    targets = [c for c in player.cards_in_play
               if 'ODYSSEY' in (c.card_origin or '')
               and (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 4
               and getattr(c, 'is_resting', False)
               and c is not card]
    if targets:
        return create_set_active_choice(game_state, player, targets, source_card=card,
                                         prompt="Choose ODYSSEY cost 4 or less to set active")
    return False


# --- OP09-030: Trafalgar Law ---
@register_effect("OP09-030", "on_play", "[On Play] Return own Character to hand: Play ODYSSEY cost 3 or less (not Law) from hand")
def op09_030_law(game_state, player, card):
    own_chars = [c for c in player.cards_in_play if c is not card]
    if not own_chars:
        return False

    from ..game_engine import PendingChoice

    snapshot = list(own_chars)
    options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

    def _after_return(selected):
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(snapshot):
            t = snapshot[idx]
            if _remove_card_instance(player.cards_in_play, t):
                player.hand.append(t)
                game_state._log(f"{player.name} returned {t.name} to hand")

        play_targets = [c for c in player.hand
                        if c.card_type == 'CHARACTER'
                        and 'ODYSSEY' in (c.card_origin or '')
                        and (c.cost or 0) <= 3
                        and 'Trafalgar Law' not in (c.name or '')]
        if play_targets:
            create_play_from_hand_choice(game_state, player, play_targets, source_card=card,
                                          rest_on_play=False,
                                          prompt="Play ODYSSEY cost 3 or less (not Law) from hand")

    game_state.pending_choice = PendingChoice(
        choice_id=f"law_return_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="You may return 1 of your Characters to hand",
        options=options,
        min_selections=0, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=_after_return,
        callback_action="law_return",
        callback_data={"player_id": player.player_id},
    )
    return True


# --- OP09-031: Donquixote Doflamingo ---
@register_effect("OP09-031", "blocker", "[Blocker]")
def op09_031_doflamingo_blocker(game_state, player, card):
    card.has_blocker = True
    return True


@register_effect("OP09-031", "end_of_turn", "[End of Your Turn] If 2+ rested Characters, set this active")
def op09_031_doflamingo_eot(game_state, player, card):
    rested = sum(1 for c in player.cards_in_play if getattr(c, 'is_resting', False) and c is not card)
    if rested >= 2:
        card.is_resting = False
        game_state._log(f"{card.name} set active (End of Turn)")
        return True
    return False


# --- OP09-032: Donquixote Rosinante ---
@register_effect("OP09-032", "blocker", "[Blocker]")
def op09_032_rosinante_blocker(game_state, player, card):
    card.has_blocker = True
    return True


@register_effect("OP09-032", "on_opponent_attack", "[On Opponent's Attack] [Once Per Turn] Set this active")
def op09_032_rosinante_defense(game_state, player, card):
    if getattr(card, '_op09_032_used', None) == game_state.turn_count:
        return False
    card._op09_032_used = game_state.turn_count
    card.is_resting = False
    game_state._log(f"{card.name} set active (Rosinante)")
    return True


# --- OP09-033: Nico Robin ---
@register_effect("OP09-033", "on_play", "[On Play] If 2+ rested, ODYSSEY/SHC can't be KO'd by effects until opponent's next turn end")
def op09_033_robin(game_state, player, card):
    rested = sum(1 for c in player.cards_in_play if getattr(c, 'is_resting', False))
    if rested < 2:
        return False
    for c in player.cards_in_play:
        if 'ODYSSEY' in (c.card_origin or '') or 'Straw Hat Crew' in (c.card_origin or ''):
            c._ko_immune_effects = True
            c._ko_immune_expires = game_state.turn_count + 1
    game_state._log(f"ODYSSEY/Straw Hat Crew Characters can't be KO'd by effects")
    return True


# --- OP09-034: Perona ---
@register_effect("OP09-034", "on_play", "[On Play] Look at 5, add Mihawk or Thriller Bark Pirates, trash 1")
def op09_034_perona(game_state, player, card):
    result = search_top_cards(game_state, player, 5, add_count=1,
                              filter_fn=lambda c: c.name == 'Dracule Mihawk'
                                                  or 'Thriller Bark Pirates' in (c.card_origin or ''),
                              source_card=card,
                              prompt="Look at top 5. Choose Mihawk or Thriller Bark Pirates card to add.")
    if player.hand:
        trash_from_hand(player, 1, game_state, source_card=card)
    return result


# --- OP09-035: Portgas.D.Ace ---
@register_effect("OP09-035", "on_play", "[On Play] If 2+ rested Characters, rest opponent's cost 5 or less")
def op09_035_ace(game_state, player, card):
    rested = sum(1 for c in player.cards_in_play if getattr(c, 'is_resting', False))
    if rested < 2:
        return False
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 5
               and not getattr(c, 'is_resting', False)]
    if targets:
        return create_rest_choice(game_state, player, targets, source_card=card,
                                   prompt="Rest opponent's Character with cost 5 or less")
    return False


# --- OP09-036: Monkey.D.Luffy ---
@register_effect("OP09-036", "on_play", "[On Play] If 2+ rested, rest opponent's DON or Character cost 6 or less")
def op09_036_luffy(game_state, player, card):
    rested = sum(1 for c in player.cards_in_play if getattr(c, 'is_resting', False))
    if rested < 2:
        return False
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 6
               and not getattr(c, 'is_resting', False)]
    # TODO: Also allow resting DON — for now target Characters only
    if targets:
        return create_rest_choice(game_state, player, targets, source_card=card,
                                   prompt="Rest opponent's Character with cost 6 or less")
    return False


# --- OP09-037: Lim ---
@register_effect("OP09-037", "on_play", "[On Play] Look at 5, add ODYSSEY (not Lim)")
def op09_037_lim(game_state, player, card):
    return search_top_cards(game_state, player, 5, add_count=1,
                            filter_fn=lambda c: 'ODYSSEY' in (c.card_origin or '') and c.name != 'Lim',
                            source_card=card,
                            prompt="Look at top 5. Choose an ODYSSEY card (not Lim) to add to hand.")


@register_effect("OP09-037", "end_of_turn", "[End of Your Turn] If 3+ rested Characters, set this active")
def op09_037_lim_eot(game_state, player, card):
    rested = sum(1 for c in player.cards_in_play if getattr(c, 'is_resting', False) and c is not card)
    if rested >= 3:
        card.is_resting = False
        game_state._log(f"{card.name} set active (Lim End of Turn)")
        return True
    return False


# OP09-038: Rob Lucci — vanilla

# --- OP09-039: Gum-Gum Cuatro... (Event) ---
@register_effect("OP09-039", "counter", "[Counter] If ODYSSEY leader + 2+ rested, Leader/Character +2000 this turn")
def op09_039_gum_gum_cuatro(game_state, player, card):
    if not check_leader_type(player, 'ODYSSEY'):
        return False
    rested = sum(1 for c in player.cards_in_play if getattr(c, 'is_resting', False))
    if rested < 2:
        return False
    targets = []
    if player.leader:
        targets.append(player.leader)
    targets.extend(player.cards_in_play)
    if targets:
        return create_power_effect_choice(game_state, player, targets, 2000, source_card=card,
                                          prompt="Choose Leader or Character to give +2000 power",
                                          min_selections=0, max_selections=1)
    return False


@register_effect("OP09-039", "trigger", "[Trigger] K.O. opponent's rested cost 4 or less")
def op09_039_gum_gum_cuatro_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if getattr(c, 'is_resting', False)
               and (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 4]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                                prompt="K.O. opponent's rested Character with cost 4 or less",
                                min_selections=0, max_selections=1)
    return False


# --- OP09-040: Thunder Lance... (Event) ---
@register_effect("OP09-040", "on_play", "[Main] If 2+ rested Characters, K.O. cost 4 or less")
def op09_040_thunder_lance(game_state, player, card):
    rested = sum(1 for c in player.cards_in_play if getattr(c, 'is_resting', False))
    if rested < 2:
        return False
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 4]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                                prompt="K.O. opponent's Character with cost 4 or less",
                                min_selections=0, max_selections=1)
    return False


@register_effect("OP09-040", "trigger", "[Trigger] Rest opponent's cost 4 or less")
def op09_040_thunder_lance_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 4
               and not getattr(c, 'is_resting', False)]
    if targets:
        return create_rest_choice(game_state, player, targets, source_card=card,
                                   prompt="Rest opponent's Character with cost 4 or less")
    return False


# --- OP09-041: Soul Franky... (Event) ---
@register_effect("OP09-041", "counter", "[Counter] +2000 during battle; if ODYSSEY leader + 2+ rested, set 2 Characters active")
def op09_041_soul_franky(game_state, player, card):
    targets = []
    if player.leader:
        targets.append(player.leader)
    targets.extend(player.cards_in_play)

    from ..game_engine import PendingChoice

    snapshot = list(targets)
    options = [{"id": str(i), "label": f"{c.name} (Power: {(c.power or 0) + getattr(c, 'power_modifier', 0)})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

    def _after_power(selected):
        if selected:
            idx = int(selected[0])
            if 0 <= idx < len(snapshot):
                t = snapshot[idx]
                add_power_modifier(t, 2000)
                game_state._log(f"{t.name} gains +2000 power during battle")

        # If ODYSSEY leader + 2+ rested, set 2 active
        if check_leader_type(player, 'ODYSSEY'):
            rested_chars = [c for c in player.cards_in_play if getattr(c, 'is_resting', False)]
            if len(rested_chars) >= 2:
                create_set_active_choice(game_state, player, rested_chars, source_card=card,
                                          prompt="Choose up to 2 Characters to set active")

    if targets:
        game_state.pending_choice = PendingChoice(
            choice_id=f"soul_franky_{uuid.uuid4().hex[:8]}",
            choice_type="select_target",
            prompt="Choose Leader or Character to give +2000 power during battle",
            options=options,
            min_selections=0, max_selections=1,
            source_card_id=card.id, source_card_name=card.name,
            callback=_after_power,
            callback_action="soul_franky_power",
            callback_data={"player_id": player.player_id},
        )
    return True


@register_effect("OP09-041", "trigger", "[Trigger] Rest opponent's cost 4 or less")
def op09_041_soul_franky_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 4
               and not getattr(c, 'is_resting', False)]
    if targets:
        return create_rest_choice(game_state, player, targets, source_card=card,
                                   prompt="Rest opponent's Character with cost 4 or less")
    return False


# =============================================================================
# CROSS GUILD + MISC (OP09-043 to OP09-060)
# =============================================================================

# --- OP09-043: Alvida ---
@register_effect("OP09-043", "on_ko", "[On K.O.] If Cross Guild leader, play cost 5 or less (not Alvida) from hand")
def op09_043_alvida(game_state, player, card):
    if not check_leader_type(player, 'Cross Guild'):
        return False
    chars = [c for c in player.hand
             if c.card_type == 'CHARACTER'
             and (c.cost or 0) <= 5
             and c.name != 'Alvida']
    if chars:
        return create_play_from_hand_choice(game_state, player, chars, source_card=card,
                                             rest_on_play=False,
                                             prompt="Play a Character cost 5 or less (not Alvida) from hand")
    return False


# --- OP09-044: Izo ---
@register_effect("OP09-044", "on_attack", "[When Attacking] Look at 5, add Wano or Whitebeard Pirates, trash 1")
def op09_044_izo(game_state, player, card):
    result = search_top_cards(game_state, player, 5, add_count=1,
                              filter_fn=lambda c: 'Land of Wano' in (c.card_origin or '')
                                                  or 'Whitebeard Pirates' in (c.card_origin or ''),
                              source_card=card,
                              prompt="Look at top 5. Choose a Wano or Whitebeard Pirates card to add.")
    if player.hand:
        trash_from_hand(player, 1, game_state, source_card=card)
    return result


# --- OP09-045: Cabaji ---
@register_effect("OP09-045", "continuous", "[Continuous] If you have Buggy or Mohji Character, can't be KO'd in battle")
def op09_045_cabaji(game_state, player, card):
    has_protector = any(c.name in ('Buggy', 'Mohji') for c in player.cards_in_play if c is not card)
    if has_protector:
        card._battle_ko_immune = True
    return True


# --- OP09-046: Crocodile ---
@register_effect("OP09-046", "on_play", "[On Play] Play Cross Guild or Baroque Works cost 5 or less from hand")
def op09_046_crocodile(game_state, player, card):
    targets = [c for c in player.hand
               if c.card_type == 'CHARACTER'
               and (c.cost or 0) <= 5
               and ('Cross Guild' in (c.card_origin or '') or 'Baroque Works' in (c.card_origin or ''))]
    if targets:
        return create_play_from_hand_choice(game_state, player, targets, source_card=card,
                                             rest_on_play=False,
                                             prompt="Play Cross Guild or Baroque Works Character cost 5 or less from hand")
    return False


# --- OP09-047: Kouzuki Oden ---
@register_effect("OP09-047", "continuous", "[Double Attack]")
def op09_047_oden_double(game_state, player, card):
    card.has_double_attack = True
    return True


@register_effect("OP09-047", "on_ko", "[On K.O.] Draw 2, trash 1")
def op09_047_oden_on_ko(game_state, player, card):
    draw_cards(player, 2, game_state)
    if player.hand:
        trash_from_hand(player, 1, game_state, source_card=card)
    return True


# --- OP09-048: Dracule Mihawk ---
@register_effect("OP09-048", "blocker", "[Blocker]")
def op09_048_mihawk_blocker(game_state, player, card):
    card.has_blocker = True
    return True


@register_effect("OP09-048", "on_play", "[On Play] Draw 2, trash 1")
def op09_048_mihawk_on_play(game_state, player, card):
    draw_cards(player, 2, game_state)
    if player.hand:
        trash_from_hand(player, 1, game_state, source_card=card)
    return True


# OP09-049: Jozu — vanilla

# --- OP09-050: Nami ---
@register_effect("OP09-050", "on_attack", "[When Attacking] Look at 5, add blue Event")
def op09_050_nami(game_state, player, card):
    return search_top_cards(game_state, player, 5, add_count=1,
                            filter_fn=lambda c: c.card_type == 'EVENT'
                                                and 'blue' in (getattr(c, 'color', '') or getattr(c, 'Color', '') or '').lower(),
                            source_card=card,
                            prompt="Look at top 5. Choose a blue Event to add to hand.")


# --- OP09-051: Buggy (Character) ---
@register_effect("OP09-051", "on_play", "[On Play] Bottom deck opponent's Character; if you don't have 5 cost 5+ Characters, bottom deck this")
def op09_051_buggy_char(game_state, player, card):
    opponent = get_opponent(game_state, player)

    from ..game_engine import PendingChoice

    if opponent.cards_in_play:
        snapshot = list(opponent.cards_in_play)
        options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

        def _after_bottom(selected):
            did_bottom = False
            if selected:
                idx = int(selected[0])
                if 0 <= idx < len(snapshot):
                    t = snapshot[idx]
                    if _remove_card_instance(opponent.cards_in_play, t):
                        opponent.deck.insert(0, t)
                        game_state._log(f"{t.name} placed at bottom of opponent's deck")
                        did_bottom = True

            if did_bottom:
                # Check if we have 5 Characters cost 5+
                big_chars = [c for c in player.cards_in_play
                             if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) >= 5]
                if len(big_chars) < 5:
                    if _remove_card_instance(player.cards_in_play, card):
                        player.deck.insert(0, card)
                        game_state._log(f"{card.name} placed at bottom of own deck (not enough cost 5+ Characters)")

        game_state.pending_choice = PendingChoice(
            choice_id=f"buggy_char_{uuid.uuid4().hex[:8]}",
            choice_type="select_target",
            prompt="Place opponent's Character at bottom of deck",
            options=options,
            min_selections=0, max_selections=1,
            source_card_id=card.id, source_card_name=card.name,
            callback=_after_bottom,
            callback_action="buggy_char_bottom",
            callback_data={"player_id": player.player_id},
        )
        return True
    return False


# --- OP09-052: Marco ---
@register_effect("OP09-052", "continuous", "[Opponent's Turn] Trash from hand: When KO'd by opponent's effect, play from trash rested")
def op09_052_marco(game_state, player, card):
    # Mark this card as having the Marco replacement effect
    card._marco_replacement = True
    return True


# --- OP09-053: Mohji ---
@register_effect("OP09-053", "on_play", "[On Play] Look at 5, add Richie, play Richie from hand")
def op09_053_mohji(game_state, player, card):
    result = search_top_cards(game_state, player, 5, add_count=1,
                              filter_fn=lambda c: c.name == 'Richie',
                              source_card=card,
                              prompt="Look at top 5. Choose [Richie] to add to hand.")
    richie = [c for c in player.hand if c.name == 'Richie' and c.card_type == 'CHARACTER']
    if richie:
        return create_play_from_hand_choice(game_state, player, richie, source_card=card,
                                             rest_on_play=False,
                                             prompt="Play [Richie] from hand")
    return result


# --- OP09-054: Richie ---
@register_effect("OP09-054", "blocker", "[Blocker]")
def op09_054_richie_blocker(game_state, player, card):
    card.has_blocker = True
    return True


# OP09-055: Mr.1(Daz.Bonez) — vanilla

# --- OP09-056: Mr.3(Galdino) ---
@register_effect("OP09-056", "on_play", "[On Play] Look at 4, add Cross Guild or Baroque Works (not self)")
def op09_056_mr3(game_state, player, card):
    return search_top_cards(game_state, player, 4, add_count=1,
                            filter_fn=lambda c: ('Cross Guild' in (c.card_origin or '')
                                                 or 'Baroque Works' in (c.card_origin or ''))
                                                and c.name != 'Mr.3(Galdino)',
                            source_card=card,
                            prompt="Look at top 4. Choose Cross Guild or Baroque Works card (not Mr.3) to add.")


# --- OP09-057: Cross Guild (Event) ---
@register_effect("OP09-057", "on_play", "[Main] Look at 4, add Cross Guild")
def op09_057_cross_guild(game_state, player, card):
    return search_top_cards(game_state, player, 4, add_count=1,
                            filter_fn=lambda c: 'Cross Guild' in (c.card_origin or ''),
                            source_card=card,
                            prompt="Look at top 4. Choose a Cross Guild card to add to hand.")


@register_effect("OP09-057", "trigger", "[Trigger] Activate Main effect")
def op09_057_cross_guild_trigger(game_state, player, card):
    return op09_057_cross_guild(game_state, player, card)


# --- OP09-058: Special Muggy Ball (Event) ---
@register_effect("OP09-058", "on_play", "[Main] Return opponent's cost 6 or less to hand")
def op09_058_muggy_ball(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 6]
    if targets:
        return create_return_to_hand_choice(game_state, player, targets, source_card=card,
                                             prompt="Return opponent's Character cost 6 or less to hand",
                                             optional=True)
    return False


@register_effect("OP09-058", "trigger", "[Trigger] Return cost 3 or less to hand")
def op09_058_muggy_ball_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    all_chars = list(player.cards_in_play) + list(opponent.cards_in_play)
    targets = [c for c in all_chars
               if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 3]
    if targets:
        return create_return_to_hand_choice(game_state, player, targets, source_card=card,
                                             prompt="Return Character cost 3 or less to owner's hand",
                                             optional=True)
    return False


# --- OP09-059: Murder at the Steam Bath (Event) ---
@register_effect("OP09-059", "counter", "[Counter] +3000 during battle; trash up to 2 from hand, same number from deck")
def op09_059_murder(game_state, player, card):
    targets = []
    if player.leader:
        targets.append(player.leader)
    targets.extend(player.cards_in_play)

    from ..game_engine import PendingChoice

    snapshot = list(targets)
    options = [{"id": str(i), "label": f"{c.name} (Power: {(c.power or 0) + getattr(c, 'power_modifier', 0)})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

    def _after_power(selected):
        if selected:
            idx = int(selected[0])
            if 0 <= idx < len(snapshot):
                t = snapshot[idx]
                add_power_modifier(t, 3000)
                game_state._log(f"{t.name} gains +3000 power during battle")

        # Trash up to 2 from hand, then same from deck
        if player.hand:
            hand_snap = list(player.hand)
            hand_opts = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(hand_snap)]

            def _after_hand_trash(selected2):
                trashed_count = 0
                if selected2:
                    for sel in selected2:
                        idx2 = int(sel)
                        if 0 <= idx2 < len(hand_snap):
                            t2 = hand_snap[idx2]
                            if _remove_card_instance(player.hand, t2):
                                player.trash.append(t2)
                                trashed_count += 1
                    game_state._log(f"{player.name} trashed {trashed_count} cards from hand")
                # Trash same number from deck top
                for _ in range(trashed_count):
                    if player.deck:
                        top = player.deck.pop()
                        player.trash.append(top)
                if trashed_count > 0:
                    game_state._log(f"{player.name} trashed {trashed_count} cards from deck top")

            game_state.pending_choice = PendingChoice(
                choice_id=f"murder_hand_{uuid.uuid4().hex[:8]}",
                choice_type="select_cards",
                prompt="Trash up to 2 cards from hand (same number trashed from deck top)",
                options=hand_opts,
                min_selections=0, max_selections=2,
                source_card_id=card.id, source_card_name=card.name,
                callback=_after_hand_trash,
                callback_action="murder_hand_trash",
                callback_data={"player_id": player.player_id},
            )

    if targets:
        game_state.pending_choice = PendingChoice(
            choice_id=f"murder_{uuid.uuid4().hex[:8]}",
            choice_type="select_target",
            prompt="Choose Leader or Character to give +3000 power during battle",
            options=options,
            min_selections=0, max_selections=1,
            source_card_id=card.id, source_card_name=card.name,
            callback=_after_power,
            callback_action="murder_power",
            callback_data={"player_id": player.player_id},
        )
    return True


@register_effect("OP09-059", "trigger", "[Trigger] Draw 1")
def op09_059_murder_trigger(game_state, player, card):
    draw_cards(player, 1, game_state)
    return True


# --- OP09-060: Emptee Bluffs Island (Stage) ---
@register_effect("OP09-060", "activate", "[Activate: Main] Place 2 from hand at bottom + rest this: If Cross Guild leader, draw 2")
def op09_060_emptee_bluffs(game_state, player, card):
    if getattr(card, 'is_resting', False):
        return False
    if not check_leader_type(player, 'Cross Guild'):
        return False
    if len(player.hand) < 2:
        return False

    from ..game_engine import PendingChoice

    snapshot = list(player.hand)
    options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

    def _after_bottom(selected):
        if len(selected) < 2:
            return
        for sel in selected:
            idx = int(sel)
            if 0 <= idx < len(snapshot):
                t = snapshot[idx]
                if _remove_card_instance(player.hand, t):
                    player.deck.insert(0, t)
        card.is_resting = True
        game_state._log(f"{player.name} placed 2 cards at bottom and rested Emptee Bluffs Island")
        draw_cards(player, 2, game_state)

    game_state.pending_choice = PendingChoice(
        choice_id=f"emptee_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Choose 2 cards from hand to place at bottom of deck",
        options=options,
        min_selections=2, max_selections=2,
        source_card_id=card.id, source_card_name=card.name,
        callback=_after_bottom,
        callback_action="emptee_bottom",
        callback_data={"player_id": player.player_id},
    )
    return True


# =============================================================================
# LUFFY / STRAW HAT CREW / KID PIRATES (OP09-063 to OP09-080)
# =============================================================================

# OP09-063: Usopp — vanilla

# --- OP09-064: Killer ---
@register_effect("OP09-064", "on_play", "[On Play] DON -1: Set Kid Pirates Leader active")
def op09_064_killer(game_state, player, card):
    def _after_don():
        if player.leader and 'Kid Pirates' in (player.leader.card_origin or ''):
            player.leader.is_resting = False
            game_state._log(f"{player.leader.name} set active (Killer)")

    auto = optional_don_return(game_state, player, 1, source_card=card, post_callback=_after_don)
    if auto:
        _after_don()
    return True


# --- OP09-065: Sanji ---
@register_effect("OP09-065", "on_play", "[On Play] Return 1+ DON: Gain Rush + rest opponent's cost 6 or less")
def op09_065_sanji(game_state, player, card):
    if not player.don_pool:
        return False

    def _after_don():
        card.has_rush = True
        game_state._log(f"{card.name} gains Rush")

        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play
                   if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 6
                   and not getattr(c, 'is_resting', False)]
        if targets:
            create_rest_choice(game_state, player, targets, source_card=card,
                                prompt="Rest opponent's Character cost 6 or less")

    auto = optional_don_return(game_state, player, 1, source_card=card, post_callback=_after_don)
    if auto:
        _after_don()
    return True


# --- OP09-066: Jean Bart ---
@register_effect("OP09-066", "on_play", "[On Play] If opponent has more DON, K.O. cost 3 or less")
def op09_066_jean_bart(game_state, player, card):
    opponent = get_opponent(game_state, player)
    if len(opponent.don_pool) <= len(player.don_pool):
        return False

    targets = [c for c in opponent.cards_in_play
               if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 3]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                                prompt="K.O. opponent's Character with cost 3 or less",
                                min_selections=0, max_selections=1)
    return False


# OP09-067: Jinbe — vanilla

# --- OP09-068: Tony Tony.Chopper ---
@register_effect("OP09-068", "end_of_turn", "[End of Turn] Return 1+ DON: Set active + gain Blocker until opponent's next turn end")
def op09_068_chopper(game_state, player, card):
    if not player.don_pool:
        return False

    def _after_don():
        card.is_resting = False
        card.has_blocker = True
        card._blocker_expires = game_state.turn_count + 1
        game_state._log(f"{card.name} set active, gains Blocker until opponent's next turn end")

    auto = optional_don_return(game_state, player, 1, source_card=card, post_callback=_after_don)
    if auto:
        _after_don()
    return True


# --- OP09-069: Trafalgar Law ---
@register_effect("OP09-069", "on_play", "[On Play] Look at 4, add Straw Hat Crew or Heart Pirates cost 2+")
def op09_069_law(game_state, player, card):
    return search_top_cards(game_state, player, 4, add_count=1,
                            filter_fn=lambda c: (c.cost or 0) >= 2
                                                and ('Straw Hat Crew' in (c.card_origin or '')
                                                     or 'Heart Pirates' in (c.card_origin or '')),
                            source_card=card,
                            prompt="Look at top 4. Choose SHC or Heart Pirates card (cost 2+) to add.")


# --- OP09-070: Nami ---
@register_effect("OP09-070", "on_play", "[On Play] Return 1+ DON: Give 2 rested DON to Leader or Character")
def op09_070_nami(game_state, player, card):
    if not player.don_pool:
        return False

    def _after_don():
        # Give up to 2 rested DON to a target
        rested_don_count = player.don_pool.count('rested')
        if rested_don_count < 2:
            return
        targets = []
        if player.leader:
            targets.append(player.leader)
        targets.extend(player.cards_in_play)
        if targets:
            from ..game_engine import PendingChoice
            snapshot = list(targets)
            options = [{"id": str(i), "label": f"{c.name}", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

            def _give_don(selected):
                if not selected:
                    return
                idx = int(selected[0])
                if 0 <= idx < len(snapshot):
                    t = snapshot[idx]
                    given = 0
                    for i in range(len(player.don_pool)):
                        if given >= 2:
                            break
                        if player.don_pool[i] == 'rested':
                            t.attached_don = getattr(t, 'attached_don', 0) + 1
                            player.don_pool.pop(i - given)
                            given += 1
                    game_state._log(f"Gave {given} rested DON to {t.name}")

            game_state.pending_choice = PendingChoice(
                choice_id=f"nami_don_{uuid.uuid4().hex[:8]}",
                choice_type="select_target",
                prompt="Choose Leader or Character to give 2 rested DON",
                options=options,
                min_selections=0, max_selections=1,
                source_card_id=card.id, source_card_name=card.name,
                callback=_give_don,
                callback_action="nami_give_don",
                callback_data={"player_id": player.player_id},
            )

    auto = optional_don_return(game_state, player, 1, source_card=card, post_callback=_after_don)
    if auto:
        _after_don()
    return True


# --- OP09-071: Nico Robin ---
@register_effect("OP09-071", "blocker", "[Blocker]")
def op09_071_robin_blocker(game_state, player, card):
    card.has_blocker = True
    return True


# --- OP09-072: Franky ---
@register_effect("OP09-072", "blocker", "[Blocker]")
def op09_072_franky_blocker(game_state, player, card):
    card.has_blocker = True
    return True


@register_effect("OP09-072", "on_play", "[On Play] DON -2, trash 1 from hand: Draw 2")
def op09_072_franky_on_play(game_state, player, card):
    if len(player.don_pool) < 2 or not player.hand:
        return False

    from ..game_engine import PendingChoice

    def _after_don():
        if not player.hand:
            return
        snap = list(player.hand)
        opts = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snap)]

        def _after_trash(selected):
            if not selected:
                return
            idx = int(selected[0])
            if 0 <= idx < len(snap):
                t = snap[idx]
                if _remove_card_instance(player.hand, t):
                    player.trash.append(t)
                    game_state._log(f"{player.name} trashed {t.name}")
            draw_cards(player, 2, game_state)

        game_state.pending_choice = PendingChoice(
            choice_id=f"franky_trash_{uuid.uuid4().hex[:8]}",
            choice_type="select_cards",
            prompt="Trash 1 from hand to draw 2",
            options=opts,
            min_selections=1, max_selections=1,
            source_card_id=card.id, source_card_name=card.name,
            callback=_after_trash,
            callback_action="franky_trash",
            callback_data={"player_id": player.player_id},
        )

    auto = return_don_to_deck(game_state, player, 2, source_card=card, post_callback=_after_don)
    if auto:
        _after_don()
    return True


# --- OP09-073: Brook ---
@register_effect("OP09-073", "on_attack", "[When Attacking] Return 1+ DON: Opponent's 2 Characters -2000")
def op09_073_brook(game_state, player, card):
    if not player.don_pool:
        return False

    def _after_don():
        opponent = get_opponent(game_state, player)
        targets = list(opponent.cards_in_play)
        if targets:
            create_power_effect_choice(game_state, player, targets, -2000, source_card=card,
                                       prompt="Choose up to 2 opponent's Characters to give -2000 power",
                                       min_selections=0, max_selections=2)

    auto = optional_don_return(game_state, player, 1, source_card=card, post_callback=_after_don)
    if auto:
        _after_don()
    return True


# --- OP09-074: Bepo ---
@register_effect("OP09-074", "continuous", "[Your Turn] [Once Per Turn] When DON returned to deck, Leader/Character +1000")
def op09_074_bepo(game_state, player, card):
    # Reactive/event-based continuous — flag for DON return hook
    if game_state.current_player_index != _player_index(game_state, player):
        return False
    card._bepo_active = True
    return True


# --- OP09-075: Eustass"Captain"Kid ---
@register_effect("OP09-075", "on_play", "[On Play] Add life to hand: If Kid Pirates leader, add 1 DON active")
def op09_075_kid(game_state, player, card):
    if not player.life_cards:
        return False

    from ..game_engine import PendingChoice

    def _after_confirm(selected):
        if not selected or selected[0] == 'no':
            return
        if player.life_cards:
            lc = player.life_cards.pop()
            player.hand.append(lc)
            game_state._log(f"{player.name} added Life to hand")
            if check_leader_type(player, 'Kid Pirates'):
                add_don_from_deck(player, 1, set_active=True)
                game_state._log(f"{player.name} added 1 active DON (Kid)")

    game_state.pending_choice = PendingChoice(
        choice_id=f"kid_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Add top Life to hand? (If Kid Pirates leader, gain 1 active DON)",
        options=[{"id": "yes", "label": "Yes"}, {"id": "no", "label": "No"}],
        min_selections=1, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=_after_confirm,
        callback_action="kid_life",
        callback_data={"player_id": player.player_id},
    )
    return True


# --- OP09-076: Roronoa Zoro ---
@register_effect("OP09-076", "on_play", "[On Play] Return 1+ DON: Add 1 DON active")
def op09_076_zoro(game_state, player, card):
    if not player.don_pool:
        return False

    def _after_don():
        add_don_from_deck(player, 1, set_active=True)
        game_state._log(f"{player.name} added 1 active DON (Zoro)")

    auto = optional_don_return(game_state, player, 1, source_card=card, post_callback=_after_don)
    if auto:
        _after_don()
    return True


# --- OP09-077: Gum-Gum Lightning (Event) ---
@register_effect("OP09-077", "on_play", "[Main] DON -2: K.O. 6000 power or less")
def op09_077_gum_gum_lightning(game_state, player, card):
    if len(player.don_pool) < 2:
        return False

    def _after_don():
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play
                   if (c.power or 0) + getattr(c, 'power_modifier', 0) <= 6000]
        if targets:
            create_ko_choice(game_state, player, targets, source_card=card,
                             prompt="K.O. opponent's Character with 6000 power or less",
                             min_selections=0, max_selections=1)

    auto = return_don_to_deck(game_state, player, 2, source_card=card, post_callback=_after_don)
    if auto:
        _after_don()
    return True


@register_effect("OP09-077", "trigger", "[Trigger] Add 1 DON active")
def op09_077_gum_gum_lightning_trigger(game_state, player, card):
    add_don_from_deck(player, 1, set_active=True)
    return True


# --- OP09-078: Gum-Gum Giant (Event) ---
@register_effect("OP09-078", "counter", "[Counter] DON -2, trash 1 from hand: If SHC leader, +4000 during battle, draw 2")
def op09_078_gum_gum_giant(game_state, player, card):
    if len(player.don_pool) < 2:
        return False
    if not check_leader_type(player, 'Straw Hat Crew'):
        return False
    if not player.hand:
        return False

    from ..game_engine import PendingChoice

    def _after_don():
        snap = list(player.hand)
        opts = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snap)]

        def _after_trash(selected):
            if not selected:
                return
            idx = int(selected[0])
            if 0 <= idx < len(snap):
                t = snap[idx]
                if _remove_card_instance(player.hand, t):
                    player.trash.append(t)
                    game_state._log(f"{player.name} trashed {t.name}")

            targets = []
            if player.leader:
                targets.append(player.leader)
            targets.extend(player.cards_in_play)
            if targets:
                def _after_power(sel2):
                    if sel2:
                        pidx = int(sel2[0])
                        if 0 <= pidx < len(targets):
                            add_power_modifier(targets[pidx], 4000)
                            game_state._log(f"{targets[pidx].name} gains +4000 power")
                    draw_cards(player, 2, game_state)

                game_state.pending_choice = PendingChoice(
                    choice_id=f"giant_power_{uuid.uuid4().hex[:8]}",
                    choice_type="select_target",
                    prompt="Choose Leader or Character to give +4000 power during battle",
                    options=[{"id": str(i), "label": f"{c.name}", "card_id": c.id, "card_name": c.name} for i, c in enumerate(targets)],
                    min_selections=0, max_selections=1,
                    source_card_id=card.id, source_card_name=card.name,
                    callback=_after_power,
                    callback_action="giant_power",
                    callback_data={"player_id": player.player_id},
                )
            else:
                draw_cards(player, 2, game_state)

        game_state.pending_choice = PendingChoice(
            choice_id=f"giant_trash_{uuid.uuid4().hex[:8]}",
            choice_type="select_cards",
            prompt="Trash 1 from hand",
            options=opts,
            min_selections=1, max_selections=1,
            source_card_id=card.id, source_card_name=card.name,
            callback=_after_trash,
            callback_action="giant_trash",
            callback_data={"player_id": player.player_id},
        )

    auto = return_don_to_deck(game_state, player, 2, source_card=card, post_callback=_after_don)
    if auto:
        _after_don()
    return True


# --- OP09-079: Gum-Gum Jump Rope (Event) ---
@register_effect("OP09-079", "on_play", "[Main] DON -2: Rest cost 5 or less, draw 1")
def op09_079_gum_gum_jump_rope(game_state, player, card):
    if len(player.don_pool) < 2:
        return False

    def _after_don():
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play
                   if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 5
                   and not getattr(c, 'is_resting', False)]

        def _after_rest_done():
            draw_cards(player, 1, game_state)

        if targets:
            from ..game_engine import PendingChoice
            snapshot = list(targets)
            options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

            def _rest_cb(selected):
                if selected:
                    idx = int(selected[0])
                    if 0 <= idx < len(snapshot):
                        snapshot[idx].is_resting = True
                        game_state._log(f"{snapshot[idx].name} rested")
                draw_cards(player, 1, game_state)

            game_state.pending_choice = PendingChoice(
                choice_id=f"jump_rope_{uuid.uuid4().hex[:8]}",
                choice_type="select_target",
                prompt="Rest opponent's Character cost 5 or less",
                options=options,
                min_selections=0, max_selections=1,
                source_card_id=card.id, source_card_name=card.name,
                callback=_rest_cb,
                callback_action="jump_rope_rest",
                callback_data={"player_id": player.player_id},
            )
        else:
            draw_cards(player, 1, game_state)

    auto = return_don_to_deck(game_state, player, 2, source_card=card, post_callback=_after_don)
    if auto:
        _after_don()
    return True


@register_effect("OP09-079", "trigger", "[Trigger] Add 1 DON active")
def op09_079_jump_rope_trigger(game_state, player, card):
    add_don_from_deck(player, 1, set_active=True)
    return True


# --- OP09-080: Thousand Sunny (Stage) ---
@register_effect("OP09-080", "continuous", "[Opponent's Turn] Rest this: When SHC Character removed by opponent's effect, add 1 DON rested")
def op09_080_thousand_sunny(game_state, player, card):
    # Reactive hook — flag for engine
    card._sunny_active = True
    return True


# =============================================================================
# BLACKBEARD PIRATES (OP09-083 to OP09-099)
# =============================================================================

# OP09-082: Avalo Pizarro — vanilla

# --- OP09-083: Van Augur ---
@register_effect("OP09-083", "activate", "[Activate: Main] Rest this: If BB leader, opponent's Character -3 cost")
def op09_083_van_augur(game_state, player, card):
    if getattr(card, 'is_resting', False):
        return False
    if not check_leader_type(player, 'Blackbeard Pirates'):
        return False

    card.is_resting = True
    opponent = get_opponent(game_state, player)
    targets = list(opponent.cards_in_play)
    if targets:
        return create_cost_reduction_choice(game_state, player, targets, -3, source_card=card,
                                            prompt="Choose opponent's Character to give -3 cost")
    return True


@register_effect("OP09-083", "on_ko", "[On K.O.] Draw 1")
def op09_083_van_augur_ko(game_state, player, card):
    draw_cards(player, 1, game_state)
    return True


# --- OP09-084: Catarina Devon ---
@register_effect("OP09-084", "activate", "[Activate: Main] [Once Per Turn] If BB leader, gain Double Attack, Banish, or Blocker")
def op09_084_catarina_devon(game_state, player, card):
    if getattr(card, '_op09_084_used', None) == game_state.turn_count:
        return False
    if not check_leader_type(player, 'Blackbeard Pirates'):
        return False

    card._op09_084_used = game_state.turn_count

    from ..game_engine import PendingChoice

    game_state.pending_choice = PendingChoice(
        choice_id=f"devon_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Choose ability for Catarina Devon (until opponent's next turn end)",
        options=[
            {"id": "double_attack", "label": "Double Attack"},
            {"id": "banish", "label": "Banish"},
            {"id": "blocker", "label": "Blocker"},
        ],
        min_selections=1, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=lambda selected: _devon_apply(selected, card, game_state),
        callback_action="devon_ability",
        callback_data={"player_id": player.player_id},
    )
    return True


def _devon_apply(selected, card, game_state):
    if not selected:
        return
    choice = selected[0]
    if choice == 'double_attack':
        card.has_double_attack = True
        game_state._log(f"{card.name} gains [Double Attack]")
    elif choice == 'banish':
        card.has_banish = True
        game_state._log(f"{card.name} gains [Banish]")
    elif choice == 'blocker':
        card.has_blocker = True
        game_state._log(f"{card.name} gains [Blocker]")


# --- OP09-085: Gecko Moria ---
@register_effect("OP09-085", "on_play", "[On Play] Play Thriller Bark cost 2 or less from trash rested")
def op09_085_moria(game_state, player, card):
    targets = [c for c in player.trash
               if c.card_type == 'CHARACTER'
               and 'Thriller Bark Pirates' in (c.card_origin or '')
               and (c.cost or 0) <= 2]
    if targets:
        return create_play_from_trash_choice(game_state, player, targets, source_card=card,
                                              rest_on_play=True,
                                              prompt="Play Thriller Bark Pirates cost 2 or less from trash rested")
    return False


# --- OP09-086: Jesus Burgess ---
@register_effect("OP09-086", "continuous", "[Continuous] Can't be KO'd by effects; if BB leader, +1000 per 4 cards in trash")
def op09_086_burgess(game_state, player, card):
    card._ko_immune_effects = True
    if check_leader_type(player, 'Blackbeard Pirates'):
        trash_count = len(player.trash)
        bonus = (trash_count // 4) * 1000
        if bonus > 0:
            card.power_modifier = getattr(card, 'power_modifier', 0) + bonus
    return True


# --- OP09-087: Charlotte Pudding ---
@register_effect("OP09-087", "on_play", "[On Play] If opponent has 5+ hand, opponent trashes 1")
def op09_087_pudding(game_state, player, card):
    opponent = get_opponent(game_state, player)
    if len(opponent.hand) >= 5:
        trash_from_hand(opponent, 1, game_state, source_card=card)
        return True
    return False


# --- OP09-088: Shiryu ---
@register_effect("OP09-088", "on_attack", "[DON!! x1] [When Attacking] Trash 2 from hand: Draw 2")
def op09_088_shiryu(game_state, player, card):
    if getattr(card, 'attached_don', 0) < 1:
        return False
    if len(player.hand) < 2:
        return False

    from ..game_engine import PendingChoice

    snapshot = list(player.hand)
    options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

    def _after_trash(selected):
        if len(selected) < 2:
            return
        for sel in selected:
            idx = int(sel)
            if 0 <= idx < len(snapshot):
                t = snapshot[idx]
                if _remove_card_instance(player.hand, t):
                    player.trash.append(t)
        game_state._log(f"{player.name} trashed 2 cards from hand (Shiryu)")
        draw_cards(player, 2, game_state)

    game_state.pending_choice = PendingChoice(
        choice_id=f"shiryu_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="You may trash 2 cards from hand to draw 2",
        options=options,
        min_selections=0, max_selections=2,
        source_card_id=card.id, source_card_name=card.name,
        callback=_after_trash,
        callback_action="shiryu_trash",
        callback_data={"player_id": player.player_id},
    )
    return True


# --- OP09-089: Stronger ---
@register_effect("OP09-089", "activate", "[Activate: Main] Trash 1 from hand + trash this: If BB leader, draw 1 + opponent's Character -2 cost")
def op09_089_stronger(game_state, player, card):
    if not check_leader_type(player, 'Blackbeard Pirates'):
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
                game_state._log(f"{player.name} trashed {t.name}")

        # Trash this character
        if _remove_card_instance(player.cards_in_play, card):
            player.trash.append(card)
            game_state._log(f"{card.name} trashed itself")

        draw_cards(player, 1, game_state)

        opponent = get_opponent(game_state, player)
        targets = list(opponent.cards_in_play)
        if targets:
            create_cost_reduction_choice(game_state, player, targets, -2, source_card=card,
                                         prompt="Choose opponent's Character to give -2 cost")

    game_state.pending_choice = PendingChoice(
        choice_id=f"stronger_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Trash 1 from hand (and this Character) to draw 1 and give -2 cost",
        options=options,
        min_selections=1, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=_after_trash,
        callback_action="stronger_trash",
        callback_data={"player_id": player.player_id},
    )
    return True


# --- OP09-090: Doc Q ---
@register_effect("OP09-090", "activate", "[Activate: Main] Rest this: If BB leader, K.O. cost 1 or less")
def op09_090_doc_q(game_state, player, card):
    if getattr(card, 'is_resting', False):
        return False
    if not check_leader_type(player, 'Blackbeard Pirates'):
        return False

    card.is_resting = True
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 1]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                                prompt="K.O. opponent's Character with cost 1 or less",
                                min_selections=0, max_selections=1)
    return True


@register_effect("OP09-090", "on_ko", "[On K.O.] Draw 1")
def op09_090_doc_q_ko(game_state, player, card):
    draw_cards(player, 1, game_state)
    return True


# --- OP09-091: Vasco Shot ---
@register_effect("OP09-091", "blocker", "[Blocker]")
def op09_091_vasco_shot(game_state, player, card):
    card.has_blocker = True
    return True


# --- OP09-092: Marshall.D.Teach (Character, cost 3) ---
@register_effect("OP09-092", "activate", "[Activate: Main] Rest this: If hand 3+ less than opponent's, draw 2 trash 1")
def op09_092_teach_char(game_state, player, card):
    if getattr(card, 'is_resting', False):
        return False
    opponent = get_opponent(game_state, player)
    if len(player.hand) + 3 > len(opponent.hand):
        return False

    card.is_resting = True
    draw_cards(player, 2, game_state)
    if player.hand:
        trash_from_hand(player, 1, game_state, source_card=card)
    game_state._log(f"{player.name} drew 2, trashed 1 (Teach)")
    return True


# --- OP09-093: Marshall.D.Teach (Character, cost 10) ---
@register_effect("OP09-093", "blocker", "[Blocker]")
def op09_093_teach_10_blocker(game_state, player, card):
    card.has_blocker = True
    return True


@register_effect("OP09-093", "activate", "[Activate: Main] [Once Per Turn] If BB leader + played this turn, negate Leader + negate Character + can't attack")
def op09_093_teach_10_activate(game_state, player, card):
    if getattr(card, '_op09_093_used', None) == game_state.turn_count:
        return False
    if not check_leader_type(player, 'Blackbeard Pirates'):
        return False
    if getattr(card, 'played_turn', -1) != game_state.turn_count:
        return False

    card._op09_093_used = game_state.turn_count

    opponent = get_opponent(game_state, player)
    # Negate opponent's leader effect
    if opponent.leader:
        opponent.leader.effect_negated = True
        game_state._log(f"{opponent.leader.name}'s effect negated this turn")

    # Negate a Character's effect and it can't attack
    if opponent.cards_in_play:
        targets = list(opponent.cards_in_play)

        from ..game_engine import PendingChoice

        snapshot = list(targets)
        options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

        def _callback(selected):
            if not selected:
                return
            idx = int(selected[0])
            if 0 <= idx < len(snapshot):
                t = snapshot[idx]
                t.effect_negated = True
                t.cannot_attack = True
                t._cannot_attack_expires = game_state.turn_count + 1
                game_state._log(f"{t.name}'s effect negated and cannot attack (Teach)")

        game_state.pending_choice = PendingChoice(
            choice_id=f"teach10_{uuid.uuid4().hex[:8]}",
            choice_type="select_target",
            prompt="Choose opponent's Character to negate effect and prevent from attacking",
            options=options,
            min_selections=0, max_selections=1,
            source_card_id=card.id, source_card_name=card.name,
            callback=_callback,
            callback_action="teach10_negate",
            callback_data={"player_id": player.player_id},
        )
    return True


# OP09-094: Peachbeard — vanilla

# --- OP09-095: Laffitte ---
@register_effect("OP09-095", "activate", "[Activate: Main] Rest DON + this: Look at 5, add Blackbeard Pirates")
def op09_095_laffitte(game_state, player, card):
    if getattr(card, 'is_resting', False):
        return False
    if player.don_pool.count('active') < 1:
        return False

    for i in range(len(player.don_pool)):
        if player.don_pool[i] == 'active':
            player.don_pool[i] = 'rested'
            break
    card.is_resting = True

    return search_top_cards(game_state, player, 5, add_count=1,
                            filter_fn=lambda c: 'Blackbeard Pirates' in (c.card_origin or ''),
                            source_card=card,
                            prompt="Look at top 5. Choose a Blackbeard Pirates card to add to hand.")


# --- OP09-096: My Era...Begins!! (Event) ---
@register_effect("OP09-096", "on_play", "[Main] Look at 3, add Blackbeard Pirates (not self), trash rest")
def op09_096_my_era(game_state, player, card):
    return search_top_cards(game_state, player, 3, add_count=1,
                            filter_fn=lambda c: 'Blackbeard Pirates' in (c.card_origin or '')
                                                and c.name != "My Era...Begins!!",
                            source_card=card, trash_rest=True,
                            prompt="Look at top 3. Choose Blackbeard Pirates card to add (rest trashed).")


@register_effect("OP09-096", "trigger", "[Trigger] Activate Main effect")
def op09_096_my_era_trigger(game_state, player, card):
    return op09_096_my_era(game_state, player, card)


# --- OP09-097: Black Vortex (Event) ---
@register_effect("OP09-097", "counter", "[Counter] Negate opponent's Leader/Character effect and -4000 power")
def op09_097_black_vortex(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = []
    if opponent.leader:
        targets.append(opponent.leader)
    targets.extend(opponent.cards_in_play)
    if not targets:
        return False

    from ..game_engine import PendingChoice

    snapshot = list(targets)
    options = [{"id": str(i), "label": f"{c.name} (Power: {(c.power or 0) + getattr(c, 'power_modifier', 0)})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

    def _callback(selected):
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(snapshot):
            t = snapshot[idx]
            t.effect_negated = True
            add_power_modifier(t, -4000)
            game_state._log(f"{t.name}'s effect negated and gets -4000 power")

    game_state.pending_choice = PendingChoice(
        choice_id=f"vortex_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Negate opponent's Leader or Character effect and give -4000 power",
        options=options,
        min_selections=0, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=_callback,
        callback_action="vortex_negate",
        callback_data={"player_id": player.player_id},
    )
    return True


@register_effect("OP09-097", "trigger", "[Trigger] Negate opponent's Leader/Character effect")
def op09_097_black_vortex_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = []
    if opponent.leader:
        targets.append(opponent.leader)
    targets.extend(opponent.cards_in_play)
    if not targets:
        return False

    from ..game_engine import PendingChoice

    snapshot = list(targets)
    options = [{"id": str(i), "label": f"{c.name}", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

    def _callback(selected):
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(snapshot):
            snapshot[idx].effect_negated = True
            game_state._log(f"{snapshot[idx].name}'s effect negated")

    game_state.pending_choice = PendingChoice(
        choice_id=f"vortex_trig_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Negate opponent's Leader or Character effect",
        options=options,
        min_selections=0, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=_callback,
        callback_action="vortex_trig_negate",
        callback_data={"player_id": player.player_id},
    )
    return True


# --- OP09-098: Black Hole (Event) ---
@register_effect("OP09-098", "on_play", "[Main] If BB leader, negate opponent's Character effect; if cost 4 or less, K.O. it")
def op09_098_black_hole(game_state, player, card):
    if not check_leader_type(player, 'Blackbeard Pirates'):
        return False
    opponent = get_opponent(game_state, player)
    if not opponent.cards_in_play:
        return False

    from ..game_engine import PendingChoice

    snapshot = list(opponent.cards_in_play)
    options = [{"id": str(i), "label": f"{c.name} (Cost: {(c.cost or 0) + getattr(c, 'cost_modifier', 0)})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

    def _callback(selected):
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(snapshot):
            t = snapshot[idx]
            t.effect_negated = True
            game_state._log(f"{t.name}'s effect negated (Black Hole)")
            effective_cost = (t.cost or 0) + getattr(t, 'cost_modifier', 0)
            if effective_cost <= 4:
                game_state._attempt_character_ko(t, by_effect=True)

    game_state.pending_choice = PendingChoice(
        choice_id=f"black_hole_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Negate opponent's Character effect (if cost 4 or less, K.O. it)",
        options=options,
        min_selections=0, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=_callback,
        callback_action="black_hole_negate",
        callback_data={"player_id": player.player_id},
    )
    return True


@register_effect("OP09-098", "trigger", "[Trigger] Negate opponent's Leader/Character effect")
def op09_098_black_hole_trigger(game_state, player, card):
    return op09_097_black_vortex_trigger(game_state, player, card)


# --- OP09-099: Fullalead (Stage) ---
@register_effect("OP09-099", "activate", "[Activate: Main] Trash 1 from hand + rest this: Look at 3, add Blackbeard Pirates")
def op09_099_fullalead(game_state, player, card):
    if getattr(card, 'is_resting', False):
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
                game_state._log(f"{player.name} trashed {t.name}")
        card.is_resting = True
        search_top_cards(game_state, player, 3, add_count=1,
                         filter_fn=lambda c: 'Blackbeard Pirates' in (c.card_origin or ''),
                         source_card=card,
                         prompt="Look at top 3. Choose a Blackbeard Pirates card to add to hand.")

    game_state.pending_choice = PendingChoice(
        choice_id=f"fullalead_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Trash 1 from hand to activate Fullalead",
        options=options,
        min_selections=1, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=_after_trash,
        callback_action="fullalead_trash",
        callback_data={"player_id": player.player_id},
    )
    return True


# =============================================================================
# REVOLUTIONARY ARMY / ROBIN / EGGHEAD / SEC (OP09-100 to OP09-119)
# =============================================================================

# --- OP09-100: Karasu ---
@register_effect("OP09-100", "blocker", "[Blocker]")
def op09_100_karasu_blocker(game_state, player, card):
    card.has_blocker = True
    return True


@register_effect("OP09-100", "trigger", "[Trigger] If Rev Army leader + total life <= 5, play this")
def op09_100_karasu_trigger(game_state, player, card):
    if not check_leader_type(player, 'Revolutionary Army'):
        return False
    opponent = get_opponent(game_state, player)
    total_life = len(player.life_cards) + len(opponent.life_cards)
    if total_life > 5:
        return False
    if _remove_card_instance(player.trash, card):
        player.cards_in_play.append(card)
        card.is_resting = False
        setattr(card, 'played_turn', game_state.turn_count)
        game_state._log(f"{player.name} played {card.name} from trigger")
    return True


# --- OP09-101: Kuzan ---
@register_effect("OP09-101", "on_play", "[On Play] Place opponent's cost 3 or less at top/bottom of their life face-up: Opponent trashes 1")
def op09_101_kuzan(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 3]
    if not targets:
        return False

    from ..game_engine import PendingChoice

    snapshot = list(targets)
    options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

    def _after_select(selected):
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(snapshot):
            t = snapshot[idx]
            if _remove_card_instance(opponent.cards_in_play, t):
                setattr(t, 'is_face_up', True)
                opponent.life_cards.append(t)
                game_state._log(f"{t.name} placed at top of opponent's Life face-up")

        if opponent.hand:
            trash_from_hand(opponent, 1, game_state, source_card=card)

    game_state.pending_choice = PendingChoice(
        choice_id=f"kuzan_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Place opponent's cost 3 or less Character at top of their Life face-up",
        options=options,
        min_selections=1, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=_after_select,
        callback_action="kuzan_life",
        callback_data={"player_id": player.player_id},
    )
    return True


# --- OP09-102: Professor Clover ---
@register_effect("OP09-102", "on_play", "[On Play] If Robin leader, look at 3, add Trigger card")
def op09_102_clover(game_state, player, card):
    if not (player.leader and 'Nico Robin' in (player.leader.name or '')):
        return False
    return search_top_cards(game_state, player, 3, add_count=1,
                            filter_fn=lambda c: (getattr(c, 'trigger', '') or getattr(c, 'Trigger', '') or '').strip() != ''
                                                or '[Trigger]' in (getattr(c, 'effect', '') or getattr(c, 'Effect', '') or ''),
                            source_card=card,
                            prompt="Look at top 3. Choose a card with [Trigger] to add to hand.")


@register_effect("OP09-102", "trigger", "[Trigger] Activate On Play effect")
def op09_102_clover_trigger(game_state, player, card):
    return op09_102_clover(game_state, player, card)


# --- OP09-103: Koala ---
@register_effect("OP09-103", "blocker", "[Blocker]")
def op09_103_koala_blocker(game_state, player, card):
    card.has_blocker = True
    return True


@register_effect("OP09-103", "on_play", "[On Play] Add life to hand: Play Rev Army cost 4 or less from hand, draw 1")
def op09_103_koala(game_state, player, card):
    if not player.life_cards:
        return False

    from ..game_engine import PendingChoice

    def _after_life(selected):
        if not selected or selected[0] == 'skip':
            return
        if selected[0] == 'top' and player.life_cards:
            lc = player.life_cards.pop()
            player.hand.append(lc)
            game_state._log(f"{player.name} added top Life to hand")
        elif selected[0] == 'bottom' and player.life_cards:
            lc = player.life_cards.pop(0)
            player.hand.append(lc)
            game_state._log(f"{player.name} added bottom Life to hand")
        else:
            return

        rev_chars = [c for c in player.hand
                     if c.card_type == 'CHARACTER'
                     and 'Revolutionary Army' in (c.card_origin or '')
                     and (c.cost or 0) <= 4]
        if rev_chars:
            def _play_callback(selected2):
                if selected2:
                    pidx = int(selected2[0])
                    if 0 <= pidx < len(rev_chars):
                        t = rev_chars[pidx]
                        if _remove_card_instance(player.hand, t):
                            player.cards_in_play.append(t)
                            t.is_resting = False
                            setattr(t, 'played_turn', game_state.turn_count)
                            game_state._log(f"{player.name} played {t.name} from hand")
                    draw_cards(player, 1, game_state)
                    game_state._log(f"{player.name} drew 1 card (Koala)")

            game_state.pending_choice = PendingChoice(
                choice_id=f"koala_play_{uuid.uuid4().hex[:8]}",
                choice_type="select_cards",
                prompt="Play Revolutionary Army cost 4 or less from hand (then draw 1)",
                options=[{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(rev_chars)],
                min_selections=0, max_selections=1,
                source_card_id=card.id, source_card_name=card.name,
                callback=_play_callback,
                callback_action="koala_play",
                callback_data={"player_id": player.player_id},
            )

    game_state.pending_choice = PendingChoice(
        choice_id=f"koala_life_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Add Life card to hand? (top or bottom)",
        options=[{"id": "top", "label": "Add top Life"},
                 {"id": "bottom", "label": "Add bottom Life"},
                 {"id": "skip", "label": "Skip"}],
        min_selections=1, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=_after_life,
        callback_action="koala_life",
        callback_data={"player_id": player.player_id},
    )
    return True


# --- OP09-104: Sabo ---
@register_effect("OP09-104", "on_play", "[On Play] Add Rev Army from hand to life face-up; if 2+ life, add life to hand")
def op09_104_sabo(game_state, player, card):
    rev_chars = [c for c in player.hand
                 if c.card_type == 'CHARACTER'
                 and 'Revolutionary Army' in (c.card_origin or '')]
    if not rev_chars:
        # Still check if we can do the second part
        if len(player.life_cards) >= 2:
            lc = player.life_cards.pop()
            player.hand.append(lc)
            game_state._log(f"{player.name} added Life to hand (Sabo)")
        return True

    from ..game_engine import PendingChoice

    snapshot = list(rev_chars)
    options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})", "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

    def _after_place(selected):
        if selected:
            idx = int(selected[0])
            if 0 <= idx < len(snapshot):
                t = snapshot[idx]
                if _remove_card_instance(player.hand, t):
                    setattr(t, 'is_face_up', True)
                    player.life_cards.append(t)
                    game_state._log(f"{player.name} added {t.name} to Life face-up")

        if len(player.life_cards) >= 2:
            # Add life (top or bottom) to hand
            def _life_pick(sel2):
                if not sel2 or sel2[0] == 'skip':
                    return
                if sel2[0] == 'top' and player.life_cards:
                    lc = player.life_cards.pop()
                    player.hand.append(lc)
                    game_state._log(f"{player.name} added top Life to hand")
                elif sel2[0] == 'bottom' and player.life_cards:
                    lc = player.life_cards.pop(0)
                    player.hand.append(lc)
                    game_state._log(f"{player.name} added bottom Life to hand")

            game_state.pending_choice = PendingChoice(
                choice_id=f"sabo_life_{uuid.uuid4().hex[:8]}",
                choice_type="select_target",
                prompt="Add Life to hand? (top or bottom)",
                options=[{"id": "top", "label": "Top"}, {"id": "bottom", "label": "Bottom"}, {"id": "skip", "label": "Skip"}],
                min_selections=1, max_selections=1,
                source_card_id=card.id, source_card_name=card.name,
                callback=_life_pick,
                callback_action="sabo_life_pick",
                callback_data={"player_id": player.player_id},
            )

    game_state.pending_choice = PendingChoice(
        choice_id=f"sabo_place_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Choose Revolutionary Army Character from hand to add to Life face-up",
        options=options,
        min_selections=0, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=_after_place,
        callback_action="sabo_place",
        callback_data={"player_id": player.player_id},
    )
    return True


@register_effect("OP09-104", "trigger", "[Trigger] If Leader is multicolored, draw 2")
def op09_104_sabo_trigger(game_state, player, card):
    # Check if leader is multicolored
    if player.leader:
        color = getattr(player.leader, 'color', '') or getattr(player.leader, 'Color', '') or ''
        if '/' in color:
            draw_cards(player, 2, game_state)
            return True
    return False


# --- OP09-105: Sanji (Egghead) ---
@register_effect("OP09-105", "trigger", "[Trigger] If Egghead leader, add deck top to life, trash 2 from hand")
def op09_105_sanji_trigger(game_state, player, card):
    if not check_leader_type(player, 'Egghead'):
        return False
    if player.deck:
        top = player.deck.pop()
        player.life_cards.append(top)
        game_state._log(f"{player.name} added deck top to Life")
    if player.hand:
        trash_from_hand(player, 2, game_state, source_card=card)
    return True


# --- OP09-106: Nico Olvia ---
@register_effect("OP09-106", "on_play", "[On Play] Nico Robin Leader +3000 power this turn")
def op09_106_olvia(game_state, player, card):
    if player.leader and 'Nico Robin' in (player.leader.name or ''):
        add_power_modifier(player.leader, 3000)
        game_state._log(f"{player.leader.name} gains +3000 power (Nico Olvia)")
        return True
    return False


@register_effect("OP09-106", "trigger", "[Trigger] If Robin leader, draw 3 trash 2")
def op09_106_olvia_trigger(game_state, player, card):
    if not (player.leader and 'Nico Robin' in (player.leader.name or '')):
        return False
    draw_cards(player, 3, game_state)
    if player.hand:
        trash_from_hand(player, 2, game_state, source_card=card)
    return True


# --- OP09-107: Nico Robin (Character) ---
@register_effect("OP09-107", "on_play", "[On Play] If opponent has 3+ life, trash top of opponent's life")
def op09_107_robin_char(game_state, player, card):
    opponent = get_opponent(game_state, player)
    if len(opponent.life_cards) >= 3:
        trashed = opponent.life_cards.pop()
        opponent.trash.append(trashed)
        game_state._log(f"Trashed top of {opponent.name}'s Life")
        return True
    return False


@register_effect("OP09-107", "trigger", "[Trigger] Play yellow cost 3 or less from hand")
def op09_107_robin_trigger(game_state, player, card):
    targets = [c for c in player.hand
               if c.card_type == 'CHARACTER'
               and (c.cost or 0) <= 3
               and 'yellow' in (getattr(c, 'color', '') or getattr(c, 'Color', '') or '').lower()]
    if targets:
        return create_play_from_hand_choice(game_state, player, targets, source_card=card,
                                             rest_on_play=False,
                                             prompt="Play a yellow Character cost 3 or less from hand")
    return False


# --- OP09-108: Bartholomew Kuma ---
@register_effect("OP09-108", "trigger", "[Trigger] If Rev Army leader + total life <= 5, play this")
def op09_108_kuma_trigger(game_state, player, card):
    if not check_leader_type(player, 'Revolutionary Army'):
        return False
    opponent = get_opponent(game_state, player)
    total_life = len(player.life_cards) + len(opponent.life_cards)
    if total_life > 5:
        return False
    if _remove_card_instance(player.trash, card):
        player.cards_in_play.append(card)
        card.is_resting = False
        setattr(card, 'played_turn', game_state.turn_count)
        game_state._log(f"{player.name} played {card.name} from trigger")
    return True


# --- OP09-109: Jaguar.D.Saul ---
@register_effect("OP09-109", "blocker", "[Blocker]")
def op09_109_saul_blocker(game_state, player, card):
    card.has_blocker = True
    return True


@register_effect("OP09-109", "trigger", "[Trigger] If Robin leader, play this")
def op09_109_saul_trigger(game_state, player, card):
    if not (player.leader and 'Nico Robin' in (player.leader.name or '')):
        return False
    if _remove_card_instance(player.trash, card):
        player.cards_in_play.append(card)
        card.is_resting = False
        setattr(card, 'played_turn', game_state.turn_count)
        game_state._log(f"{player.name} played {card.name} from trigger")
    return True


# --- OP09-110: Pierre ---
@register_effect("OP09-110", "on_play", "[On Play] Draw 2, trash 2")
def op09_110_pierre(game_state, player, card):
    draw_cards(player, 2, game_state)
    if player.hand:
        trash_from_hand(player, 2, game_state, source_card=card)
    return True


@register_effect("OP09-110", "trigger", "[Trigger] Play this card")
def op09_110_pierre_trigger(game_state, player, card):
    if _remove_card_instance(player.trash, card):
        player.cards_in_play.append(card)
        card.is_resting = False
        setattr(card, 'played_turn', game_state.turn_count)
        game_state._log(f"{player.name} played {card.name} from trigger")
    return True


# --- OP09-111: Brook (Egghead) ---
@register_effect("OP09-111", "trigger", "[Trigger] If Egghead leader + opponent has 6+ hand, opponent trashes 2")
def op09_111_brook_trigger(game_state, player, card):
    if not check_leader_type(player, 'Egghead'):
        return False
    opponent = get_opponent(game_state, player)
    if len(opponent.hand) >= 6:
        trash_from_hand(opponent, 2, game_state, source_card=card)
        return True
    return False


# --- OP09-112: Belo Betty ---
@register_effect("OP09-112", "on_play", "[On Play] If 2 or less life, draw 1")
def op09_112_belo_betty(game_state, player, card):
    if len(player.life_cards) <= 2:
        draw_cards(player, 1, game_state)
        return True
    return False


@register_effect("OP09-112", "trigger", "[Trigger] If Rev Army leader + total life <= 5, play this")
def op09_112_betty_trigger(game_state, player, card):
    if not check_leader_type(player, 'Revolutionary Army'):
        return False
    opponent = get_opponent(game_state, player)
    total_life = len(player.life_cards) + len(opponent.life_cards)
    if total_life > 5:
        return False
    if _remove_card_instance(player.trash, card):
        player.cards_in_play.append(card)
        card.is_resting = False
        setattr(card, 'played_turn', game_state.turn_count)
        game_state._log(f"{player.name} played {card.name} from trigger")
    return True


# OP09-113: Morley — vanilla

# --- OP09-114: Lindbergh ---
@register_effect("OP09-114", "on_play", "[On Play] If total life <= 5, K.O. opponent's 2000 power or less")
def op09_114_lindbergh(game_state, player, card):
    opponent = get_opponent(game_state, player)
    total_life = len(player.life_cards) + len(opponent.life_cards)
    if total_life > 5:
        return False
    targets = [c for c in opponent.cards_in_play
               if (c.power or 0) + getattr(c, 'power_modifier', 0) <= 2000]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                                prompt="K.O. opponent's Character with 2000 power or less",
                                min_selections=0, max_selections=1)
    return False


@register_effect("OP09-114", "trigger", "[Trigger] If total life <= 5, play this")
def op09_114_lindbergh_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    total_life = len(player.life_cards) + len(opponent.life_cards)
    if total_life > 5:
        return False
    if _remove_card_instance(player.trash, card):
        player.cards_in_play.append(card)
        card.is_resting = False
        setattr(card, 'played_turn', game_state.turn_count)
        game_state._log(f"{player.name} played {card.name} from trigger")
    return True


# --- OP09-115: Ice Block Partisan (Event) ---
@register_effect("OP09-115", "on_play", "[Main] K.O. opponent's cost 3 or less with [Trigger]")
def op09_115_ice_block(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 3
               and ((getattr(c, 'trigger', '') or getattr(c, 'Trigger', '') or '').strip() != ''
                    or '[Trigger]' in (getattr(c, 'effect', '') or getattr(c, 'Effect', '') or ''))]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                                prompt="K.O. opponent's cost 3 or less Character with [Trigger]",
                                min_selections=0, max_selections=1)
    return False


@register_effect("OP09-115", "trigger", "[Trigger] Draw 1")
def op09_115_ice_block_trigger(game_state, player, card):
    draw_cards(player, 1, game_state)
    return True


# --- OP09-116: Never Underestimate... (Event) ---
@register_effect("OP09-116", "counter", "[Counter] Leader/Character +2000 power")
def op09_116_never_underestimate(game_state, player, card):
    targets = []
    if player.leader:
        targets.append(player.leader)
    targets.extend(player.cards_in_play)
    if targets:
        return create_power_effect_choice(game_state, player, targets, 2000, source_card=card,
                                          prompt="Choose Leader or Character to give +2000 power",
                                          min_selections=0, max_selections=1)
    return False


@register_effect("OP09-116", "trigger", "[Trigger] Play Rev Army cost 4 or less from hand")
def op09_116_never_underestimate_trigger(game_state, player, card):
    targets = [c for c in player.hand
               if c.card_type == 'CHARACTER'
               and 'Revolutionary Army' in (c.card_origin or '')
               and (c.cost or 0) <= 4]
    if targets:
        return create_play_from_hand_choice(game_state, player, targets, source_card=card,
                                             rest_on_play=False,
                                             prompt="Play Revolutionary Army cost 4 or less from hand")
    return False


# --- OP09-117: Dereshi! (Event) ---
@register_effect("OP09-117", "on_play", "[Main] Look at 5, add up to 2 Trigger cards (not Dereshi!)")
def op09_117_dereshi(game_state, player, card):
    return search_top_cards(game_state, player, 5, add_count=2,
                            filter_fn=lambda c: ((getattr(c, 'trigger', '') or getattr(c, 'Trigger', '') or '').strip() != ''
                                                 or '[Trigger]' in (getattr(c, 'effect', '') or getattr(c, 'Effect', '') or ''))
                                                and c.name != 'Dereshi!',
                            source_card=card,
                            prompt="Look at top 5. Choose up to 2 cards with [Trigger] to add to hand.")


@register_effect("OP09-117", "trigger", "[Trigger] Draw 1")
def op09_117_dereshi_trigger(game_state, player, card):
    draw_cards(player, 1, game_state)
    return True


# --- OP09-118: Gol.D.Roger (SEC) ---
@register_effect("OP09-118", "continuous", "[Rush]; When opponent activates Blocker and either player has 0 life, you win")
def op09_118_roger(game_state, player, card):
    card.has_rush = True
    # The win condition is checked in the blocker activation flow in the engine
    card._roger_win_condition = True
    return True


# --- OP09-119: Monkey.D.Luffy (SEC) ---
@register_effect("OP09-119", "on_play", "[On Play] Return 1+ DON: Draw 1 + gain Rush")
def op09_119_luffy(game_state, player, card):
    if not player.don_pool:
        return False

    def _after_don():
        draw_cards(player, 1, game_state)
        card.has_rush = True
        game_state._log(f"{card.name} drew 1 card and gains Rush")

    auto = optional_don_return(game_state, player, 1, source_card=card, post_callback=_after_don)
    if auto:
        _after_don()
    return True
