"""
Hardcoded effects for OP01 cards.
"""

import random

from ..effect_registry import (
    add_don_from_deck, create_add_from_trash_choice, create_bottom_deck_choice, create_ko_choice,
    create_own_character_choice, create_play_from_hand_choice, create_power_effect_choice,
    create_rest_choice, create_return_to_hand_choice, create_set_active_choice, create_target_choice,
    create_trash_choice, draw_cards, get_opponent, register_effect, reorder_top_cards,
    return_don_to_deck, search_top_cards, trash_from_hand,
)


def _play_this_card_from_trigger(game_state, player, card):
    """Move the trigger card to the field if it is not already there."""
    for zone in (player.hand, player.life_cards, player.trash):
        if card in zone:
            zone.remove(card)
            break
    if card not in player.cards_in_play:
        card.is_resting = False
        setattr(card, "played_turn", game_state.turn_count)
        game_state.play_card_to_field_by_effect(player, card)
        game_state._apply_keywords(card)
        game_state._log(f"{player.name} played {card.name} from Trigger")
    return True


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
        prompt=f"Choose up to 1 Leader or Character to give +{amount} power",
        min_selections=0,
    )


@register_effect("OP01-029", "trigger", "[Trigger] Leader/Character +1000 power this turn")
def op01_029_radical_beam_trigger(game_state, player, card):
    targets = ([player.leader] if player.leader else []) + player.cards_in_play
    if not targets:
        return True
    return create_power_effect_choice(
        game_state, player, targets, 1000,
        source_card=card,
        prompt="[Trigger] Choose up to 1 Leader or Character to give +1000 power",
        min_selections=0,
    )


# --- OP01-119: Thunder Bagua ---
@register_effect("OP01-119", "counter", "[Counter] +4000 power. If 2 or fewer Life, add 1 rested DON")
def op01_119_thunder_bagua(game_state, player, card):
    # Card text: [Counter] Up to 1 of your Leader or Character cards gains +4000 power during
    # this battle. Then, if you have 2 or fewer Life cards, add up to 1 DON!! card from your
    # DON!! deck and rest it.
    targets = ([player.leader] if player.leader else []) + player.cards_in_play
    if not targets:
        if len(player.life_cards) <= 2:
            add_don_from_deck(player, 1, set_active=False)
        return True
    target_snapshot = list(targets)

    def after_power(selected):
        for sel in selected:
            idx = int(sel)
            if 0 <= idx < len(target_snapshot):
                target = target_snapshot[idx]
                target.power_modifier = getattr(target, "power_modifier", 0) + 4000
                target._battle_power_modifier = getattr(target, "_battle_power_modifier", 0) + 4000
                game_state._log(f"{target.name} gets +4000 power during this battle")
        if len(player.life_cards) <= 2:
            add_don_from_deck(player, 1, set_active=False)

    return create_power_effect_choice(
        game_state, player, target_snapshot, 4000,
        source_card=card,
        prompt="Choose up to 1 Leader or Character to give +4000 power",
        min_selections=0,
        callback=after_power,
    )


@register_effect("OP01-119", "trigger", "[Trigger] Add up to 1 active DON")
def op01_119_thunder_bagua_trigger(game_state, player, card):
    add_don_from_deck(player, 1, set_active=True)
    return True


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
    targets_snapshot = list(player.cards_in_play)

    def law_leader_return_cb(selected):
        target_idx = int(selected[0]) if selected else -1
        if 0 <= target_idx < len(targets_snapshot):
            returned = targets_snapshot[target_idx]
            returned_colors = {col.lower() for col in (getattr(returned, 'colors', []) or [])}
            if returned in player.cards_in_play:
                player.cards_in_play.remove(returned)
                player.hand.append(returned)
                game_state._log(f"{returned.name} returned to hand")
            playable = [c for c in player.hand
                        if getattr(c, 'card_type', '') == 'CHARACTER'
                        and (getattr(c, 'cost', 0) or 0) <= 5
                        and not any(col.lower() in returned_colors
                                    for col in (getattr(c, 'colors', []) or []))]
            if playable:
                create_play_from_hand_choice(
                    game_state, player, playable,
                    prompt="Choose cost 5 or less Character (different color) to play"
                )

    return create_own_character_choice(
        game_state, player, targets_snapshot,
        source_card=card,
        callback=law_leader_return_cb,
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
    targets_snapshot = list(targets)

    def set_active_power_cb(selected):
        target_idx = int(selected[0]) if selected else -1
        if 0 <= target_idx < len(targets_snapshot):
            target = targets_snapshot[target_idx]
            target.is_resting = False
            target.has_attacked = False
            target.power_modifier = getattr(target, 'power_modifier', 0) + 1000
            target._sticky_power_modifier = getattr(target, '_sticky_power_modifier', 0) + 1000
            target.power_modifier_expires_on_turn = game_state.turn_count
            target._sticky_power_modifier_expires_on_turn = game_state.turn_count
            game_state._log(f"{target.name} set active and gained +1000 power")

    return create_set_active_choice(
        game_state, player, targets_snapshot,
        prompt="Choose your Supernovas/Straw Hat Crew cost 5 or less to set active (+1000 power this turn)",
        source_card=card,
        callback=set_active_power_cb,
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
    wano_snapshot = list(wano_cards)

    def oden_trash_cb(selected):
        chosen_idx = int(selected[0]) if selected else -1
        if 0 <= chosen_idx < len(wano_snapshot):
            chosen = wano_snapshot[chosen_idx]
            if chosen in player.hand:
                player.hand.remove(chosen)
                player.trash.append(chosen)
                game_state._log(f"Kouzuki Oden: Trashed {chosen.name}")
        activated = 0
        for i, don_status in enumerate(player.don_pool):
            if don_status == "rested" and activated < 2:
                player.don_pool[i] = "active"
                activated += 1
        if activated:
            game_state._log(f"Kouzuki Oden: Set {activated} DON!! as active")

    game_state.pending_choice = PendingChoice(
        choice_id=f"oden_trash_wano_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Choose a Land of Wano card from your hand to trash (then set up to 2 DON!! as active)",
        options=options,
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=oden_trash_cb,
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
        revealed_snapshot = revealed  # single card reference

        def doffy_play_cb(selected):
            if selected and selected[0] == "play" and player.deck and player.deck[0] is revealed_snapshot:
                top_card = player.deck.pop(0)
                top_card.is_resting = True
                game_state.play_card_to_field_by_effect(player, top_card)
                game_state._apply_keywords(top_card)
                game_state._log(f"Doflamingo: {top_card.name} played to field rested")
            else:
                game_state._log("Doflamingo: Card left on top of deck")

        game_state.pending_choice = PendingChoice(
            choice_id=f"doffy_reveal_{uuid.uuid4().hex[:8]}",
            choice_type="select_target",
            prompt=f"Doflamingo: Revealed {revealed.name} (Seven Warlords, Cost {revealed.cost or 0}). Play rested?",
            options=options,
            min_selections=1,
            max_selections=1,
            source_card_id=card.id,
            source_card_name=card.name,
            callback=doffy_play_cb,
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
        return create_add_from_trash_choice(
            game_state, player, valid, source_card=card,
            prompt="Choose a red cost 3 or less Character from trash to add to hand",
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
    if not player.life_cards:
        return True
    return create_target_choice(
        game_state, player, [card],
        prompt="You may add 1 Life card to hand to give Cavendish [Rush]",
        source_card=card,
        min_selections=0,
        callback=lambda selected: (
            player.hand.append(player.life_cards.pop()) or setattr(card, "has_rush", True)
        ) if selected and player.life_cards else None,
    )


# --- OP01-009: Carrot ---
@register_effect("OP01-009", "trigger", "[Trigger] Play this card")
def op01_009_carrot(game_state, player, card):
    """Trigger: Play this card."""
    game_state.play_card_to_field_by_effect(player, card)
    return True


# --- OP01-011: Gordon ---
@register_effect("OP01-011", "on_play", "[On Play] Place 1 card from hand at deck bottom, then draw 1")
def op01_011_gordon(game_state, player, card):
    # Card text: [On Play] Place up to 1 card from your hand at the bottom of your deck:
    # Draw 1 card.
    if not player.hand:
        return True  # No cards in hand — effect resolves as no-op
    hand_snapshot = list(player.hand)

    def gordon_bottom_cb(selected):
        target_idx = int(selected[0]) if selected else -1
        placed = False
        if 0 <= target_idx < len(hand_snapshot):
            target = hand_snapshot[target_idx]
            if target in player.hand:
                player.hand.remove(target)
                player.deck.append(target)
                game_state._log(f"{player.name} placed {target.name} at bottom of deck")
                placed = True
        if placed and player.deck:
            drawn = player.deck.pop(0)
            player.hand.append(drawn)
            game_state._log(f"{player.name} drew a card")

    return create_bottom_deck_choice(
        game_state, player, hand_snapshot,
        source_card=card,
        prompt="Choose a card from your hand to place at the bottom of your deck (then draw 1), or skip",
        callback=gordon_bottom_cb,
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
    hand_snapshot = list(player.hand)

    def chopper_trash_cb(selected):
        trashed_cost = False
        if selected:
            target_idx = int(selected[0]) if selected[0].isdigit() else -1
            if 0 <= target_idx < len(hand_snapshot):
                target = hand_snapshot[target_idx]
                if target in player.hand:
                    player.hand.remove(target)
                    player.trash.append(target)
                    trashed_cost = True
                    game_state._log(f"{player.name} trashed {target.name}")
        if not trashed_cost:
            return
        shc = [c for c in player.trash
               if c.card_type == 'CHARACTER'
               and 'straw hat crew' in (c.card_origin or '').lower()
               and (c.cost or 0) <= 4
               and 'tony tony.chopper' not in (c.name or '').lower()]
        if shc:
            shc_snapshot = list(shc)
            shc_opts = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})",
                         "card_id": c.id, "card_name": c.name} for i, c in enumerate(shc_snapshot)]

            def chopper_shc_pick_cb(sel2):
                idx2 = int(sel2[0]) if sel2 else -1
                if 0 <= idx2 < len(shc_snapshot):
                    picked = shc_snapshot[idx2]
                    if picked in player.trash:
                        player.trash.remove(picked)
                        player.hand.append(picked)
                        game_state._log(f"{picked.name} added to hand from trash")

            game_state.pending_choice = PendingChoice(
                choice_id=f"chopper_shc_{uuid.uuid4().hex[:8]}",
                choice_type="select_target",
                prompt="Choose a Straw Hat Crew Character (cost 4 or less) from trash to add to hand",
                options=shc_opts,
                min_selections=0,
                max_selections=1,
                source_card_id=None,
                source_card_name="Tony Tony.Chopper",
                callback=chopper_shc_pick_cb,
            )
        else:
            game_state._log("No Straw Hat Crew characters (cost 4 or less) in trash")

    game_state.pending_choice = PendingChoice(
        choice_id=f"chopper_trash_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="(Optional) Trash 1 card from hand to search your trash for a Straw Hat Crew character",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=chopper_trash_cb,
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
    hand_snapshot = list(player.hand)

    def kanjuro_ko_cb(selected):
        target_idx = int(selected[0]) if selected else -1
        if 0 <= target_idx < len(hand_snapshot):
            target = hand_snapshot[target_idx]
            if target in player.hand:
                player.hand.remove(target)
                player.trash.append(target)
                game_state._log(f"Kanjuro: {opponent.name} chose to trash {target.name} from {player.name}'s hand")

    game_state.pending_choice = PendingChoice(
        choice_id=f"kanjuro_ko_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt=f"Kanjuro's effect: Choose 1 card from {player.name}'s hand to trash (hidden)",
        options=options,
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=kanjuro_ko_cb,
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
            akazaya_snapshot = list(akazaya)

            def kinemon_set_active_cb(selected):
                target_idx = int(selected[0]) if selected else -1
                if 0 <= target_idx < len(akazaya_snapshot):
                    target = akazaya_snapshot[target_idx]
                    target.is_resting = False
                    target.has_attacked = False
                    game_state._log(f"Kinemon: {target.name} set as active")

            game_state.pending_choice = PendingChoice(
                choice_id=f"kinemon_{uuid.uuid4().hex[:8]}",
                choice_type="select_target",
                prompt="Choose an Akazaya Nine cost 3 or less to set as active",
                options=options,
                min_selections=0,
                max_selections=1,
                source_card_id=card.id,
                source_card_name=card.name,
                callback=kinemon_set_active_cb,
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
            wano_snapshot = list(wano)

            def komurasaki_set_active_cb(selected):
                target_idx = int(selected[0]) if selected else -1
                if 0 <= target_idx < len(wano_snapshot):
                    target = wano_snapshot[target_idx]
                    target.is_resting = False
                    target.has_attacked = False
                    game_state._log(f"Komurasaki: {target.name} set as active")

            game_state.pending_choice = PendingChoice(
                choice_id=f"komurasaki_{uuid.uuid4().hex[:8]}",
                choice_type="select_target",
                prompt="Choose a Land of Wano cost 3 or less Character to set as active",
                options=options,
                min_selections=0,
                max_selections=1,
                callback=komurasaki_set_active_cb,
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
        own_snapshot = list(own_chars)

        def law_return_play_cb(selected):
            target_idx = int(selected[0]) if selected else -1
            if 0 <= target_idx < len(own_snapshot):
                returned = own_snapshot[target_idx]
                if returned in player.cards_in_play:
                    player.cards_in_play.remove(returned)
                    player.hand.append(returned)
                    game_state._log(f"Law: {player.name} returned {returned.name} to hand")
            playable = [c for c in player.hand
                        if getattr(c, 'card_type', '') == 'CHARACTER'
                        and (getattr(c, 'cost', 0) or 0) <= 3]
            if playable:
                create_play_from_hand_choice(
                    game_state, player, playable,
                    prompt="Law: Choose a cost 3 or less Character to play from hand"
                )

        return create_own_character_choice(
            game_state, player, own_snapshot,
            source_card=card,
            callback=law_return_play_cb,
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
            def arlong_cb(selected):
                if selected and selected[0] == "yes" and opponent.life_cards:
                    life = opponent.life_cards.pop()
                    opponent.deck.append(life)
                    game_state._log(f"Arlong: Placed 1 of {opponent.name}'s Life at bottom of deck")
                else:
                    game_state._log("Arlong: Player chose not to remove Life")

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
                callback=arlong_cb,
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
    hand_snapshot = list(player.hand)
    return_snapshot = list(targets)

    def alvida_trash_cb(selected):
        target_idx = int(selected[0]) if selected else -1
        trashed_cost = False
        if 0 <= target_idx < len(hand_snapshot):
            trashed = hand_snapshot[target_idx]
            if trashed in player.hand:
                player.hand.remove(trashed)
                player.trash.append(trashed)
                trashed_cost = True
                game_state._log(f"Alvida: {player.name} trashed {trashed.name}")
        if not trashed_cost:
            return
        if return_snapshot:
            rt_opts = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})",
                        "card_id": c.id, "card_name": c.name} for i, c in enumerate(return_snapshot)]

            def alvida_return_cb(sel2):
                idx2 = int(sel2[0]) if sel2 else -1
                if 0 <= idx2 < len(return_snapshot):
                    target = return_snapshot[idx2]
                    for p in [player, opponent]:
                        if target in p.cards_in_play:
                            p.cards_in_play.remove(target)
                            p.hand.append(target)
                            game_state._log(f"{target.name} returned to hand")
                            break

            game_state.pending_choice = PendingChoice(
                choice_id=f"alvida_ret_{uuid.uuid4().hex[:8]}",
                choice_type="select_target",
                prompt="Choose opponent's cost 3 or less Character to return to hand",
                options=rt_opts,
                min_selections=0,
                max_selections=1,
                source_card_id=card.id,
                source_card_name=card.name,
                callback=alvida_return_cb,
            )

    game_state.pending_choice = PendingChoice(
        choice_id=f"alvida_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Choose a card from hand to trash (cost to activate Alvida's effect)",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=alvida_trash_cb,
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
    smileys_snapshot = list(smileys)

    def caesar_play_cb(selected):
        target_idx = int(selected[0]) if selected else -1
        if 0 <= target_idx < len(smileys_snapshot):
            target = smileys_snapshot[target_idx]
            if target in player.deck:
                player.deck.remove(target)
                game_state.play_card_to_field_by_effect(player, target)
                game_state._log(f"{player.name} played {target.name} from deck to field")
        import random
        random.shuffle(player.deck)

    game_state.pending_choice = PendingChoice(
        choice_id=f"caesar_smiley_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Choose a Smiley from your deck to play",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=caesar_play_cb,
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


@register_effect("OP01-071", "trigger", "[Trigger] Play this card")
def op01_071_jinbe_trigger(game_state, player, card):
    return _play_this_card_from_trigger(game_state, player, card)


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
            create_add_from_trash_choice(
                game_state, player, events, source_card=card,
                prompt="Ms. All Sunday: Choose an Event from trash to add to hand",
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
        create_add_from_trash_choice(
            game_state, player, valid, source_card=card,
            prompt="Choose a Fish-Man or Mermaid Character cost 3 or less to add to hand",
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
    def ulti_cb(selected):
        if selected and selected[0] == "yes":
            active_idx = next((i for i, s in enumerate(player.don_pool) if s == "active"), None)
            if active_idx is not None:
                player.don_pool[active_idx] = "rested"
                if len(player.don_pool) < 10:
                    player.don_pool.append("rested")
                    game_state._log(f"Ulti: {player.name} rested 1 DON, gained 1 rested DON")
                else:
                    game_state._log(f"Ulti: {player.name} rested 1 DON but DON pool is full")

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
        callback=ulti_cb,
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
    opponent = get_opponent(game_state, player)

    def _kaido_ko_cb():
        leader_ok = 'animal kingdom pirates' in (player.leader.card_origin or '').lower() if player.leader else False
        if leader_ok:
            for c in opponent.cards_in_play[:]:
                opponent.cards_in_play.remove(c)
                opponent.trash.append(c)
                game_state._log(f"  {c.name} K.O.'d")
            for c in player.cards_in_play[:]:
                if c is not card:
                    player.cards_in_play.remove(c)
                    player.trash.append(c)
                    game_state._log(f"  {c.name} K.O.'d")

    auto = return_don_to_deck(game_state, player, 6, source_card=card, post_callback=_kaido_ko_cb)
    if not auto:
        return True
    _kaido_ko_cb()
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
    opponent = get_opponent(game_state, player)

    def _king_ko_effect():
        from ...game_engine import PendingChoice
        import uuid
        targets_3 = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
        if targets_3:
            targets_3_snap = list(targets_3)

            def king_ko1_cb(selected):
                target_idx = int(selected[0]) if selected else -1
                if 0 <= target_idx < len(targets_3_snap):
                    target = targets_3_snap[target_idx]
                    for p in [player, opponent]:
                        if target in p.cards_in_play:
                            p.cards_in_play.remove(target)
                            p.trash.append(target)
                            game_state._log(f"King: K.O.'d {target.name}")
                            break
                targets_2 = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
                if targets_2:
                    create_ko_choice(game_state, player, targets_2,
                                     prompt="King: Choose opponent's cost 2 or less Character to K.O.")

            game_state.pending_choice = PendingChoice(
                choice_id=f"king_ko1_{uuid.uuid4().hex[:8]}",
                choice_type="select_target",
                prompt="King: Choose opponent's cost 3 or less Character to K.O.",
                options=[{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})",
                          "card_id": c.id, "card_name": c.name} for i, c in enumerate(targets_3)],
                min_selections=0,
                max_selections=1,
                source_card_id=card.id,
                source_card_name=card.name,
                callback=king_ko1_cb,
            )
        else:
            targets_2 = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
            if targets_2:
                create_ko_choice(game_state, player, targets_2, source_card=card,
                                 prompt="King: Choose opponent's cost 2 or less Character to K.O.")

    auto = return_don_to_deck(game_state, player, 2, source_card=card, post_callback=_king_ko_effect)
    if not auto:
        return True
    _king_ko_effect()
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
    opponent = get_opponent(game_state, player)

    def _queen_rush_cb():
        card.has_rush = True
        game_state._log(f"  {card.name} gained [Rush]")
        if opponent.cards_in_play:
            create_power_effect_choice(
                game_state, player, opponent.cards_in_play, -2000,
                source_card=card,
                prompt="Choose opponent's Character to give −2000 power"
            )

    auto = return_don_to_deck(game_state, player, 1, source_card=card, post_callback=_queen_rush_cb)
    if not auto:
        return True
    _queen_rush_cb()
    return True


# --- OP01-098: Kurozumi Orochi ---
@register_effect("OP01-098", "on_play", "[On Play] Reveal Artificial Devil Fruit SMILE from deck, add to hand")
def op01_098_orochi(game_state, player, card):
    # Card text: [On Play] Reveal up to 1 [Artificial Devil Fruit SMILE] from your deck and add
    # it to your hand. Then, shuffle your deck.
    # Search by card_origin (Type field), not name — SMILE is a type, not a card name.
    # The card text uses {Artificial Devil Fruit SMILE} which refers to TYPE containing "SMILE".
    for i, deck_card in enumerate(player.deck):
        if 'smile' in (getattr(deck_card, 'card_origin', '') or '').lower():
            found = player.deck.pop(i)
            player.hand.append(found)
            game_state._log(f"Kurozumi Orochi: Revealed {found.name} and added to hand")
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


# --- OP01-100: Kurozumi Higurashi ---
@register_effect("OP01-100", "blocker", "[Blocker]")
def op01_100_higurashi(game_state, player, card):
    """Blocker: Can redirect attacks."""
    card.is_blocker = True
    card.has_blocker = True
    return True


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
    opponent = get_opponent(game_state, player)

    def jack_cb(selected):
        if selected and selected[0] == "yes":
            if player.don_pool:
                player.don_pool.pop()
                if opponent.hand:
                    import random
                    trashed = random.choice(opponent.hand)
                    opponent.hand.remove(trashed)
                    opponent.trash.append(trashed)
                    game_state._log(f"Jack: {opponent.name} trashed {trashed.name}")
                else:
                    game_state._log(f"Jack: {opponent.name} has no cards to trash")

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
        callback=jack_cb,
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
    game_state.play_card_to_field_by_effect(player, card)
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
    def bao_huang_cb(selected):
        indices = sorted([int(s) for s in selected]) if selected else []
        for idx in indices:
            if 0 <= idx < len(opponent.hand):
                c = opponent.hand[idx]
                game_state._log(f"Bao Huang reveals: {c.name} (Cost: {c.cost or 0}, Type: {c.card_type})")

    game_state.pending_choice = PendingChoice(
        choice_id=f"bao_huang_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt=f"Bao Huang: Choose {count} of opponent's cards to reveal",
        options=options,
        min_selections=count,
        max_selections=count,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=bao_huang_cb,
    )
    return True


# --- OP01-106: Basil Hawkins ---
@register_effect("OP01-106", "on_play", "[On Play] Add 1 DON from deck and rest it")
def op01_106_basil_hawkins(game_state, player, card):
    # Card text: [On Play] Add up to 1 DON!! card from your DON!! deck and rest it.
    add_don_from_deck(player, 1, set_active=False)
    return True


@register_effect("OP01-106", "trigger", "[Trigger] Play this card")
def op01_106_basil_hawkins_trigger(game_state, player, card):
    return _play_this_card_from_trigger(game_state, player, card)


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
    opponent = get_opponent(game_state, player)

    def _kamazo_ko_cb():
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 5]
        if targets:
            create_ko_choice(game_state, player, targets, source_card=card,
                             prompt="Choose opponent's cost 5 or less Character to K.O.")

    auto = return_don_to_deck(game_state, player, 1, source_card=card, post_callback=_kamazo_ko_cb)
    if not auto:
        return True
    _kamazo_ko_cb()
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
    bm_card = card  # captured reference

    def blackmaria_cb(selected):
        if selected and selected[0] == "yes":
            def _bm_power_cb():
                bm_card.power_modifier = getattr(bm_card, 'power_modifier', 0) + 1000
                game_state._log(f"{bm_card.name} gained +1000 power")
            auto = return_don_to_deck(game_state, player, 1, source_card=None, post_callback=_bm_power_cb)
            if auto:
                _bm_power_cb()
        else:
            game_state._log("Black Maria: Declined to use DON!! -1 effect")

    game_state.pending_choice = PendingChoice(
        choice_id=f"blackmaria_opt_{uuid.uuid4().hex[:8]}",
        choice_type="yes_no",
        prompt="Black Maria: Pay DON!! −1 for +1000 power this turn?",
        options=[{"id": "yes", "label": "Yes"}, {"id": "no", "label": "No"}],
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=blackmaria_cb,
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
    def _pageone_active_cb():
        card.can_attack_active = True
        game_state._log(f"  {card.name} can now attack active Characters")

    auto = return_don_to_deck(game_state, player, 1, source_card=card, post_callback=_pageone_active_cb)
    if auto:
        _pageone_active_cb()
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
    xdrake_opponent = get_opponent(game_state, player)

    def xdrake_cb(selected):
        if selected and selected[0] == "yes":
            if player.don_pool:
                player.don_pool.pop()
                if xdrake_opponent.hand:
                    import random
                    trashed = random.choice(xdrake_opponent.hand)
                    xdrake_opponent.hand.remove(trashed)
                    xdrake_opponent.trash.append(trashed)
                    game_state._log(f"X.Drake: {xdrake_opponent.name} trashed {trashed.name}")
                else:
                    game_state._log(f"X.Drake: {xdrake_opponent.name} has no cards to trash")

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
        callback=xdrake_cb,
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


@register_effect("OP01-115", "trigger", "[Trigger] Activate this card's Main effect")
def op01_115_elephants_marchoo_trigger(game_state, player, card):
    return op01_115_elephants_marchoo(game_state, player, card)


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
    opponent = get_opponent(game_state, player)

    def _sheeps_horn_cb():
        targets = [c for c in opponent.cards_in_play
                   if (getattr(c, 'cost', 0) or 0) <= 6 and not getattr(c, 'is_resting', False)]
        if targets:
            create_rest_choice(game_state, player, targets, source_card=card,
                               prompt="Choose opponent's cost 6 or less Character to rest")

    auto = return_don_to_deck(game_state, player, 1, source_card=card, post_callback=_sheeps_horn_cb)
    if not auto:
        return True
    _sheeps_horn_cb()
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
    hand_snapshot = list(player.hand)

    def sasaki_cb(selected):
        target_idx = int(selected[0]) if selected else -1
        if 0 <= target_idx < len(hand_snapshot):
            target = hand_snapshot[target_idx]
            if target in player.hand:
                player.hand.remove(target)
                player.trash.append(target)
                game_state._log(f"Sasaki: {player.name} trashed {target.name}")
                add_don_from_deck(player, 1, set_active=False)
                game_state._log(f"{player.name} added 1 rested DON!! from DON deck")

    game_state.pending_choice = PendingChoice(
        choice_id=f"sasaki_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="(Optional) Trash 1 card from hand to add 1 rested DON!! from DON deck",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=sasaki_cb,
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
    game_state.play_card_to_field_by_effect(player, card)
    return True


# --- OP01-082: Monet ---
@register_effect("OP01-082", "trigger", "[Trigger] Play this card")
def op01_082_monet(game_state, player, card):
    # Card text: [Trigger] Play this card.
    game_state.play_card_to_field_by_effect(player, card)
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
            targets_snapshot = list(targets)

            def mr3_cb(selected):
                target_idx = int(selected[0]) if selected else -1
                if 0 <= target_idx < len(targets_snapshot):
                    target = targets_snapshot[target_idx]
                    if target in opponent.cards_in_play:
                        target.cannot_attack = True
                        target.cannot_attack_until_turn = game_state.turn_count + 1
                        game_state._log(f"Mr.3: {target.name} cannot attack until end of opponent's next turn")

            game_state.pending_choice = PendingChoice(
                choice_id=f"mr3_{uuid.uuid4().hex[:8]}",
                choice_type="select_target",
                prompt="Choose opponent's cost 4 or less Character (cannot attack next turn)",
                options=options,
                min_selections=0,
                max_selections=1,
                source_card_id=card.id,
                source_card_name=card.name,
                callback=mr3_cb,
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


@register_effect("OP01-030", "trigger", "[Trigger] Activate this card's Main effect")
def op01_030_two_years_trigger(game_state, player, card):
    return op01_030_two_years(game_state, player, card)


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
    active_snapshot = list(active_chars)

    def samurai_cb(selected):
        for sel in selected:
            idx = int(sel)
            if 0 <= idx < len(active_snapshot):
                target = active_snapshot[idx]
                if target in player.cards_in_play:
                    target.is_resting = True
                    game_state._log(f"{target.name} was rested")
        if selected:
            draw_cards(player, 2)
            game_state._log(f"{player.name} drew 2 cards")

    game_state.pending_choice = PendingChoice(
        choice_id=f"samurai_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Choose 2 of your Characters to rest (then draw 2 cards)",
        options=options,
        min_selections=2,
        max_selections=2,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=samurai_cb,
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
    targets_snapshot = list(targets)

    def demon_face_cb(selected):
        for sel in selected:
            idx = int(sel)
            if 0 <= idx < len(targets_snapshot):
                target = targets_snapshot[idx]
                for p in [player, opponent]:
                    if target in p.cards_in_play:
                        p.cards_in_play.remove(target)
                        p.trash.append(target)
                        game_state._log(f"{target.name} was K.O.'d")
                        break

    game_state.pending_choice = PendingChoice(
        choice_id=f"demon_face_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Choose up to 2 opponent's rested cost 5 or less Characters to K.O.",
        options=options,
        min_selections=0,
        max_selections=min(2, len(targets_snapshot)),
        source_card_id=card.id,
        source_card_name=card.name,
        callback=demon_face_cb,
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
    wano_hand_snapshot = list(wano_hand)
    wano_field_snapshot = list(wano_field)

    def bebeng_trash_cb(selected):
        target_idx = int(selected[0]) if selected else -1
        trashed_cost = False
        if 0 <= target_idx < len(wano_hand_snapshot):
            trashed = wano_hand_snapshot[target_idx]
            if trashed in player.hand:
                player.hand.remove(trashed)
                player.trash.append(trashed)
                trashed_cost = True
                game_state._log(f"BE-BENG!!: {player.name} trashed {trashed.name}")
        if not trashed_cost:
            return
        current_wano_field = [c for c in player.cards_in_play
                              if 'land of wano' in (c.card_origin or '').lower()
                              and (getattr(c, 'cost', 0) or 0) <= 3
                              and getattr(c, 'is_resting', False)]
        if current_wano_field:
            field_opts = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})",
                           "card_id": c.id, "card_name": c.name}
                          for i, c in enumerate(current_wano_field)]
            field_snapshot = list(current_wano_field)

            def bebeng_activate_cb(sel2):
                idx2 = int(sel2[0]) if sel2 else -1
                if 0 <= idx2 < len(field_snapshot):
                    target = field_snapshot[idx2]
                    if target in player.cards_in_play:
                        target.is_resting = False
                        game_state._log(f"BE-BENG!!: {target.name} set as active")

            game_state.pending_choice = PendingChoice(
                choice_id=f"bebeng_act_{uuid.uuid4().hex[:8]}",
                choice_type="select_target",
                prompt="Choose a Land of Wano cost 3 or less Character to set as active",
                options=field_opts,
                min_selections=0,
                max_selections=1,
                callback=bebeng_activate_cb,
            )

    game_state.pending_choice = PendingChoice(
        choice_id=f"bebeng_trash_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Choose a Land of Wano card from hand to trash (then set a Wano Character active)",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=bebeng_trash_cb,
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
    # Uses search_top_cards so the player always sees the top 5 cards, even when no SMILE match.
    from ...effects.effect_registry import search_top_cards
    def smile_char_filter(c):
        return (getattr(c, 'card_type', '') == 'CHARACTER'
                and 'smile' in (getattr(c, 'card_origin', '') or '').lower()
                and (getattr(c, 'cost', 0) or 0) <= 3)
    return search_top_cards(game_state, player, 5, add_count=1,
                            filter_fn=smile_char_filter,
                            source_card=card, play_to_field=True,
                            prompt="SMILE: Choose a SMILE Character (cost 3 or less) to play from top 5")


@register_effect("OP01-116", "trigger", "[Trigger] Activate this card's Main effect")
def op01_116_smile_event_trigger(game_state, player, card):
    return op01_116_smile_event(game_state, player, card)


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
    power_snap = list(power_targets)
    ko_snap = list(ko_targets)
    options = [{"id": str(i), "label": f"{c.name} (Power: {c.power or 0})",
                "card_id": c.id, "card_name": c.name} for i, c in enumerate(power_snap)]

    def red_hawk_cb(selected):
        target_idx = int(selected[0]) if selected else -1
        if 0 <= target_idx < len(power_snap):
            target = power_snap[target_idx]
            target.power_modifier = getattr(target, 'power_modifier', 0) + 4000
            game_state._log(f"Red Hawk: {target.name} gains +4000 power")
        live_ko = [c for c in opponent.cards_in_play
                   if (getattr(c, 'power', 0) or 0) + getattr(c, 'power_modifier', 0) <= 4000]
        if live_ko:
            create_ko_choice(game_state, player, live_ko, source_card=None,
                             prompt="Choose opponent's 4000 power or less Character to K.O.")

    game_state.pending_choice = PendingChoice(
        choice_id=f"red_hawk_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Red Hawk: Choose your Leader or Character to give +4000 power",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=red_hawk_cb,
    )
    return True


@register_effect("OP01-026", "trigger", "[Trigger] Opponent Leader/Character -10000 power")
def op01_026_red_hawk_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = ([opponent.leader] if opponent.leader else []) + opponent.cards_in_play
    if not targets:
        return True
    return create_power_effect_choice(
        game_state, player, targets, -10000,
        source_card=card,
        prompt="[Trigger] Choose up to 1 opponent Leader or Character to give -10000 power",
        min_selections=0,
    )


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


@register_effect("OP01-028", "trigger", "[Trigger] Activate this card's Counter effect")
def op01_028_rafflesia_trigger(game_state, player, card):
    return op01_028_rafflesia(game_state, player, card)


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
    power_snap = list(power_targets)
    rested_snap = list(rested)
    options = [{"id": str(i), "label": f"{c.name} (Power: {c.power or 0})",
                "card_id": c.id, "card_name": c.name} for i, c in enumerate(power_snap)]

    def paradise_cb(selected):
        target_idx = int(selected[0]) if selected else -1
        if 0 <= target_idx < len(power_snap):
            target = power_snap[target_idx]
            target.power_modifier = getattr(target, 'power_modifier', 0) + 2000
            game_state._log(f"Paradise Waterfall: {target.name} gains +2000 power")
        current_rested = [c for c in player.cards_in_play if getattr(c, 'is_resting', False)]
        if current_rested:
            create_set_active_choice(game_state, player, current_rested,
                                     prompt="Choose 1 of your Characters to set as active")

    game_state.pending_choice = PendingChoice(
        choice_id=f"paradise_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Choose your Leader or Character to give +2000 power (then set 1 Character active)",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=paradise_cb,
    )
    return True


@register_effect("OP01-057", "trigger", "[Trigger] K.O. rested opponent cost 4 or less Character")
def op01_057_paradise_waterfall_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if getattr(c, "is_resting", False) and (getattr(c, "cost", 0) or 0) <= 4]
    if targets:
        return create_ko_choice(
            game_state, player, targets, source_card=card,
            prompt="[Trigger] K.O. up to 1 opponent rested Character cost 4 or less",
            min_selections=0,
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
    power_snap = list(power_targets)
    rest_snap = list(rest_targets)
    options = [{"id": str(i), "label": f"{c.name} (Power: {c.power or 0})",
                "card_id": c.id, "card_name": c.name} for i, c in enumerate(power_snap)]

    def punk_gibson_cb(selected):
        target_idx = int(selected[0]) if selected else -1
        if 0 <= target_idx < len(power_snap):
            target = power_snap[target_idx]
            target.power_modifier = getattr(target, 'power_modifier', 0) + 4000
            game_state._log(f"Punk Gibson: {target.name} gains +4000 power")
        current_rest = [c for c in opponent.cards_in_play
                        if (getattr(c, 'cost', 0) or 0) <= 4 and not getattr(c, 'is_resting', False)]
        if current_rest:
            create_rest_choice(game_state, player, current_rest, source_card=None,
                               prompt="Choose opponent's cost 4 or less Character to rest")

    game_state.pending_choice = PendingChoice(
        choice_id=f"punk_gibson_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Punk Gibson: Choose your Leader or Character to give +4000 power",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=punk_gibson_cb,
    )
    return True


@register_effect("OP01-058", "trigger", "[Trigger] Rest up to 1 opponent Character")
def op01_058_punk_gibson_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if not getattr(c, "is_resting", False)]
    if targets:
        return create_rest_choice(
            game_state, player, targets, source_card=card,
            prompt="[Trigger] Rest up to 1 opponent Character",
            min_selections=0,
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
    power_snap = list(power_targets)
    options = [{"id": str(i), "label": f"{c.name} (Power: {c.power or 0})",
                "card_id": c.id, "card_name": c.name} for i, c in enumerate(power_snap)]

    def overheat_cb(selected):
        target_idx = int(selected[0]) if selected else -1
        if 0 <= target_idx < len(power_snap):
            target = power_snap[target_idx]
            target.power_modifier = getattr(target, 'power_modifier', 0) + 4000
            game_state._log(f"Overheat: {target.name} gains +4000 power")
        current_return = [c for c in (opponent.cards_in_play + player.cards_in_play)
                          if (getattr(c, 'cost', 0) or 0) <= 3 and not getattr(c, 'is_resting', False)]
        if current_return:
            create_return_to_hand_choice(game_state, player, current_return, source_card=None,
                                         prompt="Choose active cost 3 or less Character to return to hand")

    game_state.pending_choice = PendingChoice(
        choice_id=f"overheat_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Choose your Leader or Character to give +4000 power (then return active cost 3 or less to hand)",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=overheat_cb,
    )
    return True


@register_effect("OP01-086", "trigger", "[Trigger] Return Character cost 4 or less to owner's hand")
def op01_086_overheat_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in player.cards_in_play + opponent.cards_in_play
               if (getattr(c, "cost", 0) or 0) <= 4]
    if targets:
        return create_return_to_hand_choice(
            game_state, player, targets, source_card=card,
            prompt="[Trigger] Return up to 1 Character cost 4 or less to hand",
            optional=True,
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


@register_effect("OP01-087", "trigger", "[Trigger] Activate this card's Counter effect")
def op01_087_officer_agents_trigger(game_state, player, card):
    return op01_087_officer_agents(game_state, player, card)


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
        targets_snap = list(targets)

        def desert_spada_cb(selected):
            target_idx = int(selected[0]) if selected else -1
            if 0 <= target_idx < len(targets_snap):
                target = targets_snap[target_idx]
                target.power_modifier = getattr(target, 'power_modifier', 0) + 2000
                game_state._log(f"Desert Spada: {target.name} gets +2000 power")
            reorder_top_cards(game_state, player, 3, allow_top=True)

        game_state.pending_choice = PendingChoice(
            choice_id=f"desert_spada_{uuid.uuid4().hex[:8]}",
            choice_type="select_target",
            prompt="Desert Spada: Choose Leader or Character to give +2000 power",
            options=options,
            min_selections=1,
            max_selections=1,
            source_card_id=card.id,
            source_card_name=card.name,
            callback=desert_spada_cb,
        )
    return True


@register_effect("OP01-088", "trigger", "[Trigger] Draw 2, then trash 1 from hand")
def op01_088_desert_spada_trigger(game_state, player, card):
    draw_cards(player, 2)
    if player.hand:
        trash_from_hand(player, 1, game_state, card)
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
    def _ulti_mortar_cb():
        draw_cards(player, 1)
        game_state._log(f"Ulti-Mortar: {player.name} draws 1 card")
        targets = ([player.leader] if player.leader else []) + player.cards_in_play
        if targets:
            create_power_effect_choice(
                game_state, player, targets, 2000,
                source_card=card,
                prompt="Choose Leader or Character to give +2000 power"
            )

    auto = return_don_to_deck(game_state, player, 2, source_card=card, post_callback=_ulti_mortar_cb)
    if not auto:
        return True
    _ulti_mortar_cb()
    return True


@register_effect("OP01-118", "trigger", "[Trigger] Add up to 1 active DON")
def op01_118_ulti_mortar_trigger(game_state, player, card):
    add_don_from_deck(player, 1, set_active=True)
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
