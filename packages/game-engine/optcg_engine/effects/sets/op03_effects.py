"""
Hardcoded effects for OP03 cards.
"""

from ..hardcoded import (
    _player_index,
    add_don_from_deck, add_power_modifier, check_leader_type, check_life_count,
    create_add_to_life_choice, create_bottom_deck_choice, create_cost_reduction_choice,
    create_hand_discard_choice,
    create_ko_choice, create_own_character_choice, create_play_from_hand_choice,
    create_play_from_trash_choice, create_power_effect_choice,
    create_rest_choice, create_return_to_hand_choice, create_set_active_choice, create_target_choice,
    draw_cards, get_opponent, optional_don_return, register_effect, return_don_to_deck,
    search_top_cards, set_active, trash_from_hand,
)


# --- OP03-036: Out-of-the-Bag ---
@register_effect("OP03-036", "on_play", "[Main] Rest East Blue char: Choose Kuro card to set active")
def out_of_bag_effect(game_state, player, card):
    """Rest an East Blue Character to set a Kuro Character or Leader active."""
    # Gather all resting Kuro cards (characters on field + leader)
    resting_kuro = [c for c in player.cards_in_play
                    if 'Kuro' in (c.name or '') and c.is_resting]
    if player.leader and 'Kuro' in (player.leader.name or '') and player.leader.is_resting:
        resting_kuro.append(player.leader)
    if not resting_kuro:
        return True
    east_blue = [c for c in player.cards_in_play
                 if 'East Blue' in (c.card_origin or '') and not c.is_resting]
    if not east_blue:
        return True
    eb_snap = list(east_blue)

    def op03_036_rest_eb_cb(selected: list) -> None:
        import uuid as _uuid2
        from ...game_engine import PendingChoice as PC
        target_idx = int(selected[0]) if selected else -1
        if 0 <= target_idx < len(eb_snap):
            target = eb_snap[target_idx]
            target.is_resting = True
            game_state._log(f"{target.name} was rested")
        kuro_now = [c for c in player.cards_in_play if 'Kuro' in (c.name or '') and c.is_resting]
        if player.leader and 'Kuro' in (player.leader.name or '') and player.leader.is_resting:
            kuro_now.append(player.leader)
        kuro_snap2 = list(kuro_now)
        if not kuro_snap2:
            return
        def op03_036_activate_kuro_cb(sel2: list) -> None:
            k_idx = int(sel2[0]) if sel2 else -1
            if 0 <= k_idx < len(kuro_snap2):
                k = kuro_snap2[k_idx]
                k.is_resting = False
                k.has_attacked = False
                game_state._log(f"{k.name} was set active")
        opts = [{"id": str(i), "label": f"{c.name} ({'Leader' if c is player.leader else 'Character'})",
                 "card_id": c.id, "card_name": c.name}
                for i, c in enumerate(kuro_snap2)]
        game_state.pending_choice = PC(
            choice_id=f"op03_036_activate_{_uuid2.uuid4().hex[:8]}",
            choice_type="select_target",
            prompt="Out-of-the-Bag: Choose a Kuro Character or Leader to set active",
            options=opts,
            min_selections=1,
            max_selections=1,
            callback=op03_036_activate_kuro_cb,
        )

    return create_rest_choice(game_state, player, east_blue, source_card=card,
                              callback=op03_036_rest_eb_cb,
                              prompt="Choose an East Blue Character to rest")


# --- OP03-074: Top Knot ---
@register_effect("OP03-074", "on_play", "[Main] DON!! -2: Place opponent's cost 4 or less at bottom")
def top_knot_effect(game_state, player, card):
    """Return 2 DON to deck, place opponent's cost 4 or less at bottom."""
    def _top_knot_cb():
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
        if targets:
            create_bottom_deck_choice(game_state, player, targets, source_card=None,
                                      prompt="Top Knot: Choose opponent's cost 4 or less to place at bottom of deck")

    result = optional_don_return(game_state, player, 2, source_card=card, post_callback=_top_knot_cb)
    if not result:
        return True  # Pending choice
    return True  # Can't pay, fizzled


# --- OP03-094: Air Door ---
@register_effect("OP03-094", "on_play", "[Main] If Leader is CP, look at 5, play CP cost 5 or less")
def op03_094_air_door(game_state, player, card):
    """If Leader is CP, look at top 5, play a CP cost 5 or less Character."""
    if not check_leader_type(player, "CP"):
        return True
    def filter_fn(c):
        return ('CP' in (getattr(c, 'card_origin', '') or '')
                and getattr(c, 'card_type', '') == 'CHARACTER'
                and (getattr(c, 'cost', 0) or 0) <= 5)
    return search_top_cards(game_state, player, look_count=5, add_count=1,
                            filter_fn=filter_fn, source_card=card,
                            prompt="Air Door: Choose a CP cost 5 or less Character to play")


# --- OP03-077: Charlotte Linlin (Leader) ---
@register_effect("OP03-077", "on_attack", "[DON!! x2] [When Attacking] Rest 2 DON: Trash 1, if 1 or less life add to life")
def op03_077_linlin_leader(game_state, player, card):
    """DON x2, When Attacking: REST 2 active DON. Trash 1 from hand. If 1 or less life, optionally add from deck."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    if getattr(card, 'attached_don', 0) < 2:
        return True
    if player.don_pool.count("active") < 2:
        return True
    def op03_077_linlin_yesno_cb(selected: list) -> None:
        import uuid as _uuid2
        from ...game_engine import PendingChoice as PC
        if "yes" not in selected:
            return
        rested = 0
        for i in range(len(player.don_pool)):
            if player.don_pool[i] == "active" and rested < 2:
                player.don_pool[i] = "rested"
                rested += 1
        game_state._log(f"{player.name} rested 2 DON!!")
        if not player.hand:
            return
        hand_snap = list(player.hand)
        def op03_077_trash_cb(sel2: list) -> None:
            target_idx = int(sel2[0]) if sel2 else -1
            card_trashed = False
            if 0 <= target_idx < len(hand_snap):
                target = hand_snap[target_idx]
                if target in player.hand:
                    player.hand.remove(target)
                    player.trash.append(target)
                    game_state._log(f"{player.name} trashed {target.name} from hand")
                    card_trashed = True
            if card_trashed and len(player.life_cards) <= 1 and player.deck:
                deck_card = player.deck.pop(0)
                player.life_cards.append(deck_card)
                game_state._log("Charlotte Linlin: Added 1 card from deck to Life")

        opts = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})",
                 "card_id": c.id, "card_name": c.name}
                for i, c in enumerate(hand_snap)]
        game_state.pending_choice = PC(
            choice_id=f"op03_077_trash_{_uuid2.uuid4().hex[:8]}",
            choice_type="select_cards",
            prompt="Charlotte Linlin: Choose 1 card to trash from hand (optional; if ≤1 Life, top deck card added to Life)",
            options=opts,
            min_selections=0,
            max_selections=1,
            callback=op03_077_trash_cb,
        )

    game_state.pending_choice = PendingChoice(
        choice_id=f"op03_077_{_uuid.uuid4().hex[:8]}",
        choice_type="yes_no",
        prompt="Charlotte Linlin: Rest 2 active DON!! (then trash 1 from hand; if ≤1 Life, optionally add from deck)?",
        options=[
            {"id": "yes", "label": "Yes", "card_id": card.id, "card_name": card.name},
            {"id": "no", "label": "No", "card_id": card.id, "card_name": card.name},
        ],
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=op03_077_linlin_yesno_cb,
    )
    return True


# =============================================================================
# LEADER CARD EFFECTS - OP03 (Pillars of Strength)
# =============================================================================

# --- OP03-001: Portgas.D.Ace (Leader) ---
@register_effect("OP03-001", "on_attack", "[When Attack/Attacked] Trash Events/Stages: +1000 per card")
@register_effect("OP03-001", "on_opponent_attack", "[When Attack/Attacked] Trash Events/Stages: +1000 per card")
def op03_001_ace_leader(game_state, player, card):
    """When attacking or attacked: Trash any number of Event/Stage cards from hand, +1000 power per card."""
    from ..hardcoded import _player_index
    from ...game_engine import PendingChoice
    import uuid as _uuid

    events_stages = [c for c in player.hand
                     if getattr(c, 'card_type', '') in ['EVENT', 'STAGE']]
    if not events_stages:
        return False

    options = []
    for i, c in enumerate(events_stages):
        options.append({
            "id": str(i),
            "label": f"{c.name} ({c.card_type}, Cost: {c.cost or 0})",
            "card_id": c.id,
            "card_name": c.name,
        })

    es_snap = list(events_stages)
    card_snap = card

    def op03_001_ace_trash_cb(selected: list) -> None:
        power_gained = 0
        for sel in selected:
            target_idx = int(sel)
            if 0 <= target_idx < len(es_snap):
                target = es_snap[target_idx]
                if target in player.hand:
                    player.hand.remove(target)
                    player.trash.append(target)
                    power_gained += 1000
                    game_state._log(f"{player.name} trashed {target.name} for +1000 power")
        if power_gained > 0:
            card_snap.power_modifier = getattr(card_snap, 'power_modifier', 0) + power_gained
            card_snap._sticky_power_modifier = getattr(card_snap, '_sticky_power_modifier', 0) + power_gained
            game_state._log(f"{card_snap.name} gains +{power_gained} power this turn")

    game_state.pending_choice = PendingChoice(
        choice_id=f"ace_trash_{_uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Choose Event/Stage cards to trash for +1000 power each (select any number)",
        options=options,
        min_selections=0,
        max_selections=len(es_snap),
        source_card_id=card.id,
        source_card_name=card.name,
        callback=op03_001_ace_trash_cb,
    )
    return True


# --- OP03-021: Kuro (Leader) ---
@register_effect("OP03-021", "activate", "[Activate: Main] Rest 3 DON, rest 2 East Blue: Leader active, rest opp cost 5-")
def op03_021_kuro_leader(game_state, player, card):
    """Rest 3 DON (prompted), rest 2 East Blue Characters (prompted): Set Leader active, rest opp cost 5 or less."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    if getattr(card, 'main_activated_this_turn', False):
        return False
    active_count = player.don_pool.count("active")
    east_blue_chars = [c for c in player.cards_in_play
                       if not c.is_resting and 'East Blue' in (c.card_origin or '')]
    if active_count < 3 or len(east_blue_chars) < 2:
        return False
    leader_snap = card

    def op03_021_kuro_yesno_cb(selected: list) -> None:
        import uuid as _uuid2
        from ...game_engine import PendingChoice as PC
        if "yes" not in selected:
            return
        # Rest 3 active DON
        rested = 0
        for i in range(len(player.don_pool)):
            if player.don_pool[i] == "active" and rested < 3:
                player.don_pool[i] = "rested"
                rested += 1
        live_eb = [c for c in player.cards_in_play
                   if not c.is_resting and 'East Blue' in (getattr(c, 'card_origin', '') or '')]
        if len(live_eb) < 2:
            leader_snap.is_resting = False
            leader_snap.main_activated_this_turn = True
            return
        live_eb_snap = list(live_eb)

        def op03_021_pick_eb_cb(sel2: list) -> None:
            for s in sel2:
                idx = int(s)
                if 0 <= idx < len(live_eb_snap):
                    c = live_eb_snap[idx]
                    c.is_resting = True
                    game_state._log(f"{c.name} was rested")
            leader_snap.is_resting = False
            leader_snap.has_attacked = False
            leader_snap.main_activated_this_turn = True
            game_state._log(f"{leader_snap.name} was set active")
            opponent_ref = get_opponent(game_state, player)
            opp_targets = [c for c in opponent_ref.cards_in_play
                           if not c.is_resting and (getattr(c, 'cost', 0) or 0) <= 5]
            if opp_targets:
                create_rest_choice(game_state, player, opp_targets,
                                   prompt="Kuro: Choose opponent's cost 5 or less Character to rest")

        opts = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})",
                 "card_id": c.id, "card_name": c.name}
                for i, c in enumerate(live_eb_snap)]
        game_state.pending_choice = PC(
            choice_id=f"op03_021_eb_{_uuid2.uuid4().hex[:8]}",
            choice_type="select_cards",
            prompt="Kuro: Choose exactly 2 East Blue Characters to rest",
            options=opts,
            min_selections=2,
            max_selections=2,
            callback=op03_021_pick_eb_cb,
        )

    game_state.pending_choice = PendingChoice(
        choice_id=f"op03_021_{_uuid.uuid4().hex[:8]}",
        choice_type="yes_no",
        prompt="Kuro: Rest 3 active DON!! and rest 2 East Blue Characters to set Leader active?",
        options=[
            {"id": "yes", "label": "Yes", "card_id": card.id, "card_name": card.name},
            {"id": "no", "label": "No", "card_id": card.id, "card_name": card.name},
        ],
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=op03_021_kuro_yesno_cb,
    )
    return True


# --- OP03-022: Arlong (Leader) ---
@register_effect("OP03-022", "on_attack", "[DON!! x2] Rest 1: Play cost 4 or less with Trigger from hand")
def op03_022_arlong_leader(game_state, player, card):
    """DON x2, When Attacking: You may rest 1 DON to play a cost 4 or less Character with Trigger from hand."""
    if getattr(card, 'attached_don', 0) < 2:
        return True
    from ...game_engine import PendingChoice
    import uuid as _uuid
    if player.don_pool.count("active") < 1:
        return True
    source_card_id = card.id

    def op03_022_arlong_cb(selected: list) -> None:
        if "yes" in selected:
            active_idx = next((i for i, s in enumerate(player.don_pool) if s == "active"), None)
            if active_idx is not None:
                player.don_pool[active_idx] = "rested"
                game_state._log(f"{player.name} rested 1 DON!!")
                playable = [c for c in player.hand
                            if getattr(c, 'card_type', '') == 'CHARACTER'
                            and (getattr(c, 'cost', 0) or 0) <= 4
                            and getattr(c, 'trigger', '')]
                if playable:
                    create_play_from_hand_choice(game_state, player, playable, source_card=None,
                                                 prompt="Arlong: Choose a cost 4 or less Character with Trigger to play")

    game_state.pending_choice = PendingChoice(
        choice_id=f"op03_022_{_uuid.uuid4().hex[:8]}",
        choice_type="yes_no",
        prompt="Arlong: Rest 1 active DON!! to play a cost 4 or less Character with Trigger from hand?",
        options=[
            {"id": "yes", "label": "Yes", "card_id": card.id, "card_name": card.name},
            {"id": "no", "label": "No", "card_id": card.id, "card_name": card.name},
        ],
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=op03_022_arlong_cb,
    )
    return True


# --- OP03-040: Nami (Leader) ---
@register_effect("OP03-040", "continuous", "When deck is 0, you win instead of losing")
def op03_040_nami_continuous(game_state, player, card):
    """When your deck is reduced to 0, you win the game instead of losing."""
    player.win_on_deck_out = True
    return True


@register_effect("OP03-040", "on_damage_dealt", "[DON!! x1] When damage dealt to Life, trash 1 from deck")
def op03_040_nami_damage(game_state, player, card):
    """DON x1: When this Leader's attack deals damage to opponent's Life, trash 1 from top of your deck."""
    if getattr(card, 'attached_don', 0) >= 1:
        if player.deck:
            trashed = player.deck.pop(0)
            player.trash.append(trashed)
            return True
    return False


# --- OP03-058: Iceburg (Leader) ---
@register_effect("OP03-058", "continuous", "This Leader cannot attack")
def op03_058_iceburg_continuous(game_state, player, card):
    """This Leader cannot attack."""
    card.cannot_attack = True
    return True


@register_effect("OP03-058", "activate", "[Activate: Main] DON -1, rest Leader: Play Galley-La cost 5 or less")
def op03_058_iceburg_activate(game_state, player, card):
    """DON -1, rest this Leader: Play a Galley-La Company cost 5 or less from hand."""
    if card.is_resting:
        return False
    card.is_resting = True
    def _iceburg_play_cb():
        galley_la = [c for c in player.hand
                     if getattr(c, 'card_type', '') == 'CHARACTER'
                     and 'Galley-La Company' in (c.card_origin or '')
                     and (getattr(c, 'cost', 0) or 0) <= 5]
        if galley_la:
            create_play_from_hand_choice(game_state, player, galley_la, source_card=None,
                                         prompt="Iceburg: Choose a Galley-La cost 5 or less Character to play")

    result = optional_don_return(game_state, player, 1, source_card=card, post_callback=_iceburg_play_cb)
    if not result:
        return True  # Pending choice
    return True


# --- OP03-076: Rob Lucci (Leader) ---
@register_effect("OP03-076", "on_opponent_ko", "[Your Turn] Trash 2 from hand: When opp char K.O.'d, set Leader active")
def op03_076_lucci_leader(game_state, player, card):
    """Your Turn, Once Per Turn: Trash 2 from hand when opponent's Character is K.O.'d, set Leader active."""
    if hasattr(card, 'op03_076_used') and card.op03_076_used:
        return False
    if len(player.hand) >= 2:
        from ...game_engine import PendingChoice
        import uuid as _uuid
        hand_snap = list(player.hand)
        card_snap = card

        def op03_076_lucci_cb(selected: list) -> None:
            for idx in sorted([int(s) for s in selected], reverse=True):
                if 0 <= idx < len(hand_snap):
                    target = hand_snap[idx]
                    if target in player.hand:
                        player.hand.remove(target)
                        player.trash.append(target)
                        game_state._log(f"{player.name} trashed {target.name} from hand")
            card_snap.is_resting = False
            card_snap.has_attacked = False
            card_snap.op03_076_used = True
            game_state._log(f"{card_snap.name} was set active")

        options = [{
            "id": str(i),
            "label": f"{c.name} (Cost: {c.cost or 0})",
            "card_id": c.id,
            "card_name": c.name,
        } for i, c in enumerate(hand_snap)]
        game_state.pending_choice = PendingChoice(
            choice_id=f"op03_076_{_uuid.uuid4().hex[:8]}",
            choice_type="select_cards",
            prompt="Rob Lucci: Choose 2 cards to trash from hand to set your Leader active",
            options=options,
            min_selections=2,
            max_selections=2,
            source_card_id=card.id,
            source_card_name=card.name,
            callback=op03_076_lucci_cb,
        )
        return True
    return False


# --- OP03-099: Charlotte Katakuri (Leader) ---
@register_effect("OP03-099", "on_attack", "[DON!! x1] Look at top Life, place top/bottom, +1000 power")
def op03_099_katakuri_leader(game_state, player, card):
    """DON x1, When Attacking: Look at top of opponent's Life, choose top/bottom, then +1000 power."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    if getattr(card, 'attached_don', 0) < 1:
        return False
    opponent = get_opponent(game_state, player)
    if not opponent.life_cards:
        # No life cards to peek — still gain +1000 power
        card.power_modifier = getattr(card, 'power_modifier', 0) + 1000
        card._sticky_power_modifier = getattr(card, '_sticky_power_modifier', 0) + 1000
        return True
    top_life = opponent.life_cards[-1]  # peek without removing
    card_info = (f"{top_life.name}"
                 f" (Cost:{top_life.cost or '?'}, Power:{top_life.power or '?'})")
    opponent_snap = opponent
    leader_snap = player.leader

    def op03_099_life_peek_cb(selected: list) -> None:
        if opponent_snap.life_cards:
            choice = selected[0] if selected else "top"
            if choice == "bottom":
                moved = opponent_snap.life_cards.pop()
                opponent_snap.life_cards.insert(0, moved)
                game_state._log("Katakuri: Moved opponent's top Life card to bottom")
            else:
                game_state._log("Katakuri: Opponent's top Life card stays at top")
        if leader_snap:
            leader_snap.power_modifier = getattr(leader_snap, 'power_modifier', 0) + 1000
            leader_snap._sticky_power_modifier = getattr(leader_snap, '_sticky_power_modifier', 0) + 1000
            game_state._log("Katakuri: +1000 power this battle")

    game_state.pending_choice = PendingChoice(
        choice_id=f"op03_099_{_uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt=f"Katakuri: Top Life is [{card_info}]. Place at top or bottom? (+1000 power after)",
        options=[
            {"id": "top", "label": "Leave at top", "card_id": top_life.id, "card_name": top_life.name},
            {"id": "bottom", "label": "Move to bottom", "card_id": top_life.id, "card_name": top_life.name},
        ],
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=op03_099_life_peek_cb,
    )
    return True


# =============================================================================
# OP03 CHARACTER EFFECTS
# =============================================================================

# --- OP03-002: Adio ---
@register_effect("OP03-002", "on_attack", "[DON!! x1] Opponent can't use Blocker with 2000 or less power")
def op03_002_adio(game_state, player, card):
    """DON x1: Opponent can't activate Blocker with 2000 or less power."""
    if getattr(card, 'attached_don', 0) >= 1:
        opponent = get_opponent(game_state, player)
        for c in opponent.cards_in_play:
            if (getattr(c, 'power', 0) or 0) + getattr(c, 'power_modifier', 0) <= 2000:
                c.blocker_disabled = True
        return True
    return False


# --- OP03-003: Izo ---
@register_effect("OP03-003", "on_play", "[On Play] Look at 5, reveal Whitebeard Pirates card to hand")
def op03_003_izo(game_state, player, card):
    """On Play: Look at top 5, reveal a Whitebeard Pirates card to hand."""
    def filter_fn(c):
        return ('whitebeard pirates' in (c.card_origin or '').lower()
                and getattr(c, 'name', '') != 'Izo')
    return search_top_cards(
        game_state, player, look_count=5, add_count=1,
        filter_fn=filter_fn, source_card=card,
        prompt="Look at top 5: choose 1 Whitebeard Pirates card (not Izo) to add to hand")


# --- OP03-004: Curiel ---
@register_effect("OP03-004", "continuous", "Cannot attack Leader on turn played. [DON!! x1] Rush")
def op03_004_curiel(game_state, player, card):
    """Cannot attack Leader on turn played. DON x1: Gain Rush."""
    # Flag checked in attack_with_card against played_turn == turn_count
    card.cannot_attack_leader_on_play_turn = True
    if getattr(card, 'attached_don', 0) >= 1:
        card.has_rush = True
    return True


# --- OP03-005: Thatch ---
@register_effect("OP03-005", "activate", "[Activate: Main] [Once Per Turn] Gain +2000, trash at end of turn")
def op03_005_thatch(game_state, player, card):
    """Activate: Once per turn, gain +2000 power but trash at end of turn."""
    if not getattr(card, 'op03_005_used', False):
        card.op03_005_used = True
        card.power_modifier = getattr(card, 'power_modifier', 0) + 2000
        card.trash_at_end_of_turn = True
        return True
    return False


# --- OP03-008: Buggy ---
@register_effect("OP03-008", "continuous", "Cannot be K.O.'d in battle by Slash attribute")
def op03_008_buggy_cont(game_state, player, card):
    """Cannot be K.O.'d in battle by Slash attribute cards."""
    card.immune_to_slash_ko = True
    return True


@register_effect("OP03-008", "on_play", "[On Play] Look at 5, reveal red Event to hand")
def op03_008_buggy_play(game_state, player, card):
    """On Play: Look at top 5, reveal a red Event to hand."""
    def filter_fn(c):
        return (getattr(c, 'card_type', '') == 'EVENT'
                and 'Red' in (getattr(c, 'colors', None) or []))
    return search_top_cards(game_state, player, look_count=5, add_count=1,
                            filter_fn=filter_fn, source_card=card,
                            prompt="Look at top 5: choose 1 red Event to add to hand")


# --- OP03-009: Haruta ---
@register_effect("OP03-009", "activate", "[Activate: Main] [Once Per Turn] Give 1 rested DON to Leader/Character")
def op03_009_haruta(game_state, player, card):
    """Activate: Once per turn, give 1 rested DON to Leader or Character."""
    if getattr(card, 'op03_009_used', False):
        return False
    rested_count = player.don_pool.count("rested")
    if rested_count == 0:
        return False
    card.op03_009_used = True
    # Remove 1 rested DON from pool
    idx = player.don_pool.index("rested")
    player.don_pool.pop(idx)
    # Let player choose which Leader/Character to attach it to
    targets = list(player.cards_in_play)
    if player.leader:
        targets.append(player.leader)
    if targets:
        targets_snap = list(targets)
        def op03_009_haruta_cb(selected: list) -> None:
            target_idx = int(selected[0]) if selected else -1
            if 0 <= target_idx < len(targets_snap):
                target = targets_snap[target_idx]
                target.attached_don = getattr(target, 'attached_don', 0) + 1
                game_state._log(f"  Attached 1 DON to {target.name}")
                game_state._recalc_continuous_effects()
        return create_target_choice(game_state, player, targets,
                                    callback=op03_009_haruta_cb,
                                    source_card=card,
                                    prompt="Choose a Leader or Character to attach 1 DON to")
    return True


# --- OP03-010: Fossa ---
@register_effect("OP03-010", "blocker", "[Blocker]")
def op03_010_fossa(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


# --- OP03-011: Blamenco ---
@register_effect("OP03-011", "on_attack", "[DON!! x1] Give opponent's Character -2000 power")
def op03_011_blamenco(game_state, player, card):
    """DON x1: Give opponent's Character -2000 power."""
    if getattr(card, 'attached_don', 0) >= 1:
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            return create_power_effect_choice(game_state, player, list(opponent.cards_in_play), -2000,
                                              source_card=card,
                                              prompt="Blamenco: Choose opponent's Character to give -2000 power")
        return True
    return False


# --- OP03-012: Marshall.D.Teach ---
@register_effect("OP03-012", "on_attack", "[When Attacking] Trash red 4000+ power Character from hand/field: +1000 power, draw 1")
def op03_012_teach(game_state, player, card):
    """When Attacking: Trash a red 4000+ power Character from hand or field to gain +1000 and draw 1."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    from ..hardcoded import _player_index

    # Include both hand and field characters
    hand_targets = [c for c in player.hand
                    if getattr(c, 'card_type', '') == 'CHARACTER' and
                    'Red' in getattr(c, 'colors', []) and
                    (getattr(c, 'power', 0) or 0) >= 4000]
    field_targets = [c for c in player.cards_in_play
                     if c != card and 'Red' in getattr(c, 'colors', []) and
                     (getattr(c, 'power', 0) or 0) >= 4000]
    targets = hand_targets + field_targets
    if not targets:
        return True

    options = []
    for i, c in enumerate(targets):
        loc = "Hand" if c in player.hand else "Field"
        options.append({
            "id": str(i),
            "label": f"[{loc}] {c.name} (Power: {c.power or 0})",
            "card_id": c.id,
            "card_name": c.name,
        })

    targets_snap = list(targets)
    card_snap = card

    def op03_012_teach_cb(selected: list) -> None:
        target_idx = int(selected[0]) if selected else -1
        trashed = False
        if 0 <= target_idx < len(targets_snap):
            target = targets_snap[target_idx]
            if target in player.hand:
                player.hand.remove(target)
                player.trash.append(target)
                game_state._log(f"{player.name} trashed {target.name} from hand")
                trashed = True
            elif target in player.cards_in_play:
                player.cards_in_play.remove(target)
                player.trash.append(target)
                game_state._log(f"{player.name} trashed {target.name} from field")
                trashed = True
        if trashed:
            draw_cards(player, 1)
            card_snap.power_modifier = getattr(card_snap, 'power_modifier', 0) + 1000
            card_snap._sticky_power_modifier = getattr(card_snap, '_sticky_power_modifier', 0) + 1000
            game_state._log(f"{card_snap.name} gains +1000 power")

    game_state.pending_choice = PendingChoice(
        choice_id=f"teach_{_uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Blackbeard: Choose a red 4000+ power Character from hand or field to trash",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=op03_012_teach_cb,
    )
    return True


# --- OP03-013: Marco ---
@register_effect("OP03-013", "on_play", "[On Play] [Your Turn] K.O. opponent's 3000 power or less")
def op03_013_marco_play(game_state, player, card):
    """On Play during your turn: K.O. opponent's 3000 power or less Character."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if (getattr(c, 'power', 0) or 0) + getattr(c, 'power_modifier', 0) <= 3000]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                               prompt="Choose opponent's 3000 power or less to KO")
    return True


@register_effect("OP03-013", "on_ko", "[On K.O.] Trash Event from hand: Play this from trash rested")
def op03_013_marco_ko(game_state, player, card):
    """On K.O.: Trash an Event from hand to play this from trash rested."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    events_in_hand = [c for c in player.hand if getattr(c, 'card_type', '') == 'EVENT']
    if not events_in_hand:
        return False

    options = [{
        "id": str(i),
        "label": f"{c.name} (Cost: {c.cost or 0})",
        "card_id": c.id,
        "card_name": c.name,
    } for i, c in enumerate(events_in_hand)]
    events_snap = list(events_in_hand)
    marco_snap = card

    def op03_013_marco_ko_cb(selected: list) -> None:
        for idx in sorted([int(s) for s in selected], reverse=True):
            if 0 <= idx < len(events_snap):
                target = events_snap[idx]
                if target in player.hand:
                    player.hand.remove(target)
                    player.trash.append(target)
                    game_state._log(f"{player.name} trashed {target.name} from hand")
        for c in player.trash[:]:
            if c is marco_snap:
                player.trash.remove(c)
                player.cards_in_play.append(c)
                c.is_resting = True
                game_state._log(f"{c.name} returns to field rested")
                break

    game_state.pending_choice = PendingChoice(
        choice_id=f"op03_013_{_uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Marco: Choose an Event from hand to trash to return to play rested",
        options=options,
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=op03_013_marco_ko_cb,
    )
    return True


# --- OP03-014: Monkey.D.Garp ---
@register_effect("OP03-014", "on_attack", "[When Attacking] Play red cost 1 Character from hand")
def op03_014_garp(game_state, player, card):
    """When Attacking: Play a red cost 1 Character from hand."""
    playable = [c for c in player.hand
                if (getattr(c, 'card_type', '') == 'CHARACTER' and
                    'Red' in getattr(c, 'colors', []) and
                    (getattr(c, 'cost', 0) or 0) == 1)]
    if playable:
        return create_play_from_hand_choice(
            game_state, player, playable,
            source_card=card,
            prompt="Choose red cost 1 Character to play"
        )
    return True


# --- OP03-015: Lim ---
@register_effect("OP03-015", "blocker", "[Blocker]")
def op03_015_lim_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP03-015", "on_ko", "[Opponent's Turn] [On K.O.] Give opponent -2000 power")
def op03_015_lim_ko(game_state, player, card):
    """On K.O. during opponent's turn: Give opponent's card -2000 power."""
    if game_state.current_player == player:
        return False  # Only fires on opponent's turn
    opponent = get_opponent(game_state, player)
    targets = list(opponent.cards_in_play)
    if opponent.leader:
        targets.append(opponent.leader)
    if targets:
        return create_power_effect_choice(game_state, player, targets, -2000, source_card=card,
                                         prompt="Choose opponent's card to give -2000 power")
    return True


# --- OP03-024: Gin ---
@register_effect("OP03-024", "on_play", "[On Play] If East Blue Leader, rest 2 opponent's cost 4 or less")
def op03_024_gin(game_state, player, card):
    """On Play: If Leader is East Blue, rest up to 2 opponent's cost 4 or less Characters."""
    if player.leader and 'East Blue' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play
                   if (getattr(c, 'cost', 0) or 0) <= 4 and not getattr(c, 'is_resting', False)]
        if targets:
            return create_rest_choice(
                game_state, player, targets, source_card=card,
                prompt="Gin: Choose up to 2 opponent's cost 4 or less Characters to rest",
                min_selections=0, max_selections=2
            )
    return True


# --- OP03-025: Krieg ---
@register_effect("OP03-025", "on_play", "[On Play] Trash 1: K.O. 2 rested cost 4 or less. [DON!! x1] Double Attack")
def op03_025_krieg(game_state, player, card):
    """On Play: Trash 1 to K.O. 2 rested cost 4 or less. DON x1: Double Attack."""
    if player.hand:
        hand_snap = list(player.hand)

        def op03_025_krieg_cb(selected: list) -> None:
            import uuid as _uuid2
            from ...game_engine import PendingChoice as PC
            for idx in sorted([int(s) for s in selected], reverse=True):
                if 0 <= idx < len(hand_snap):
                    target = hand_snap[idx]
                    if target in player.hand:
                        player.hand.remove(target)
                        player.trash.append(target)
                        game_state._log(f"{player.name} trashed {target.name} from hand")
            opponent_ref = get_opponent(game_state, player)
            ko_targets = [c for c in opponent_ref.cards_in_play
                          if (getattr(c, 'cost', 0) or 0) <= 4 and getattr(c, 'is_resting', False)]
            if ko_targets:
                ko_snap = list(ko_targets)
                def ko_multi_cb(sel2: list) -> None:
                    for s in sel2:
                        ki = int(s)
                        if 0 <= ki < len(ko_snap):
                            target = ko_snap[ki]
                            if getattr(target, 'cannot_be_ko_by_effects', False):
                                game_state._log(f"{target.name} cannot be K.O.'d by effects")
                                continue
                            if target in opponent_ref.cards_in_play:
                                opponent_ref.cards_in_play.remove(target)
                                opponent_ref.trash.append(target)
                                game_state._log(f"{target.name} was K.O.'d")
                opts = [{"id": str(i), "label": f"{c.name} (Cost {c.cost or 0})",
                         "card_id": c.id, "card_name": c.name}
                        for i, c in enumerate(ko_snap)]
                game_state.pending_choice = PC(
                    choice_id=f"krieg_ko_{_uuid2.uuid4().hex[:8]}",
                    choice_type="select_target",
                    prompt="Krieg: Choose up to 2 rested cost 4 or less Characters to K.O.",
                    options=opts, min_selections=0, max_selections=2,
                    callback=ko_multi_cb,
                )

        return create_hand_discard_choice(
            game_state, player, hand_snap, source_card=card,
            callback=op03_025_krieg_cb,
            prompt="Krieg: Choose 1 card to trash from hand to K.O. up to 2 rested cost 4 or less Characters"
        )
    if getattr(card, 'attached_don', 0) >= 1:
        card.has_double_attack = True
    return True


@register_effect("OP03-025", "continuous", "[DON!! x1] Double Attack")
def op03_025_krieg_cont(game_state, player, card):
    """DON x1: Gain Double Attack."""
    if getattr(card, 'attached_don', 0) >= 1:
        card.has_doubleattack = True
        card.has_double_attack = True
    return True


# --- OP03-026: Kuroobi ---
@register_effect("OP03-026", "on_play", "[On Play] If East Blue Leader, rest opponent's Character")
def op03_026_kuroobi(game_state, player, card):
    """On Play: If Leader is East Blue, rest opponent's Character."""
    if player.leader and 'East Blue' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if not getattr(c, 'is_resting', False)]
        if targets:
            return create_rest_choice(game_state, player, targets, source_card=card,
                                     prompt="Choose opponent's Character to rest")
    return True


@register_effect("OP03-026", "trigger", "[Trigger] Play this card")
def op03_026_kuroobi_trigger(game_state, player, card):
    """Trigger: Play this card."""
    player.cards_in_play.append(card)
    return True


# --- OP03-027: Sham ---
@register_effect("OP03-027", "on_play", "[On Play] If East Blue Leader, rest cost 2 or less, play Buchi if none")
def op03_027_sham(game_state, player, card):
    """On Play: If East Blue Leader, rest cost 2 or less. If no Buchi, play one from hand."""
    if player.leader and 'East Blue' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play
                   if (getattr(c, 'cost', 0) or 0) <= 2 and not getattr(c, 'is_resting', False)]
        if targets:
            targets_snap = list(targets)

            def op03_027_sham_rest_cb(selected: list) -> None:
                target_idx = int(selected[0]) if selected else -1
                if 0 <= target_idx < len(targets_snap):
                    target = targets_snap[target_idx]
                    target.is_resting = True
                    game_state._log(f"{target.name} was rested")
                has_buchi = any(getattr(c, 'name', '') == 'Buchi' for c in player.cards_in_play)
                hand_buchi = [c for c in player.hand if getattr(c, 'name', '') == 'Buchi']
                if hand_buchi and not has_buchi:
                    create_play_from_hand_choice(
                        game_state, player, hand_buchi, source_card=None,
                        prompt="Sham: You may play 1 Buchi from your hand"
                    )

            return create_rest_choice(
                game_state, player, targets, source_card=card,
                prompt="Sham: Choose opponent's cost 2 or less Character to rest",
                callback=op03_027_sham_rest_cb,
            )
        hand_buchi = [c for c in player.hand if getattr(c, 'name', '') == 'Buchi']
        has_buchi = any(getattr(c, 'name', '') == 'Buchi' for c in player.cards_in_play)
        if hand_buchi and not has_buchi:
            from ..hardcoded import create_play_from_hand_choice
            return create_play_from_hand_choice(
                game_state, player, hand_buchi, source_card=card,
                prompt="Sham: You may play 1 Buchi from your hand"
            )
    return True


# --- OP03-028: Jango ---
@register_effect("OP03-028", "on_play", "[On Play] Choose: Set East Blue cost 6 or less active OR rest this and opponent's Character")
def op03_028_jango(game_state, player, card):
    """On Play: Choose between setting East Blue cost 6 or less active OR rest this + opponent's Character."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    card_snap = card

    def op03_028_jango_cb(selected: list) -> None:
        selected_mode = selected[0] if selected else None
        opponent = get_opponent(game_state, player)
        if selected_mode == "set_active":
            east_blue = [c for c in player.cards_in_play
                         if 'East Blue' in (c.card_origin or '')
                         and (getattr(c, 'cost', 0) or 0) <= 6
                         and getattr(c, 'is_resting', False)]
            if east_blue:
                create_set_active_choice(
                    game_state, player, east_blue, source_card=card_snap,
                    prompt="Jango: Choose an East Blue cost 6 or less Character to set active"
                )
        elif selected_mode == "rest_this":
            card_snap.is_resting = True
            game_state._log(f"{card_snap.name} was rested")
            opp_targets = [c for c in opponent.cards_in_play if not getattr(c, 'is_resting', False)]
            if opp_targets:
                create_rest_choice(
                    game_state, player, opp_targets, source_card=card_snap,
                    prompt="Jango: Choose an opponent's Character to rest"
                )

    game_state.pending_choice = PendingChoice(
        choice_id=f"op03_028_{_uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Jango: Choose an effect to activate",
        options=[
            {"id": "set_active", "label": "Set 1 East Blue cost 6 or less Character active"},
            {"id": "rest_this", "label": "Rest this Character and 1 opponent's Character"},
        ],
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=op03_028_jango_cb,
    )
    return True


# --- OP03-029: Chew ---
@register_effect("OP03-029", "on_play", "[On Play] K.O. rested cost 4 or less")
def op03_029_chew(game_state, player, card):
    """On Play: K.O. opponent's rested cost 4 or less Character."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if (getattr(c, 'cost', 0) or 0) <= 4 and getattr(c, 'is_resting', False)]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                               prompt="Choose opponent's rested cost 4 or less Character to K.O.")
    return True


@register_effect("OP03-029", "trigger", "[Trigger] Play this card")
def op03_029_chew_trigger(game_state, player, card):
    """Trigger: Play this card."""
    player.cards_in_play.append(card)
    return True


# --- OP03-030: Nami ---
@register_effect("OP03-030", "on_play", "[On Play] Look at 5, reveal green East Blue card to hand")
def op03_030_nami(game_state, player, card):
    """On Play: Look at top 5, reveal a green East Blue card to hand."""
    def filter_fn(c):
        return ('Green' in (getattr(c, 'colors', None) or [])
                and 'East Blue' in (c.card_origin or '')
                and getattr(c, 'name', '') != 'Nami')
    search_top_cards(game_state, player, 5, add_count=1, filter_fn=filter_fn,
                     source_card=card,
                     prompt="Look at top 5. Choose a green East Blue card to add to hand.")
    return True


@register_effect("OP03-030", "trigger", "[Trigger] Play this card")
def op03_030_nami_trigger(game_state, player, card):
    """Trigger: Play this card."""
    player.cards_in_play.append(card)
    return True


# --- OP03-031: Pearl ---
@register_effect("OP03-031", "blocker", "[Blocker]")
def op03_031_pearl(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


# --- OP03-032: Buggy ---
@register_effect("OP03-032", "continuous", "Cannot be K.O.'d in battle by Slash attribute")
def op03_032_buggy(game_state, player, card):
    """Cannot be K.O.'d in battle by Slash attribute cards."""
    card.immune_to_slash_ko = True
    return True


# --- OP03-034: Buchi ---
@register_effect("OP03-034", "on_play", "[On Play] K.O. rested cost 2 or less")
def op03_034_buchi(game_state, player, card):
    """On Play: K.O. opponent's rested cost 2 or less Character."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if (getattr(c, 'cost', 0) or 0) <= 2 and getattr(c, 'is_resting', False)]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                               prompt="Choose opponent's rested cost 2 or less Character to K.O.")
    return True


# --- OP03-041: Usopp ---
@register_effect("OP03-041", "continuous", "[Rush]. [DON!! x1] On damage to Life, may trash 7 from deck")
def op03_041_usopp(game_state, player, card):
    """Rush. DON x1: When dealing Life damage, may trash 7 from deck."""
    card.has_rush = True
    return True


@register_effect("OP03-041", "on_damage_dealt", "[DON!! x1] On damage to Life, may trash 7 from deck")
def op03_041_usopp_damage(game_state, player, card):
    """When this card deals Life damage with DON attached, you may trash 7 from the top of your deck."""
    if getattr(card, 'attached_don', 0) < 1:
        return True
    from ...game_engine import PendingChoice
    import uuid as _uuid
    def op03_041_usopp_trash_cb(selected: list) -> None:
        if "yes" in selected:
            count = min(7, len(player.deck))
            for _ in range(count):
                if player.deck:
                    player.trash.append(player.deck.pop(0))
            game_state._log(f"Usopp: Trashed {count} card(s) from top of deck")

    game_state.pending_choice = PendingChoice(
        choice_id=f"op03_041_{_uuid.uuid4().hex[:8]}",
        choice_type="yes_no",
        prompt="Usopp: Trash 7 cards from the top of your deck?",
        options=[
            {"id": "yes", "label": "Yes", "card_id": card.id, "card_name": card.name},
            {"id": "no", "label": "No", "card_id": card.id, "card_name": card.name},
        ],
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=op03_041_usopp_trash_cb,
    )
    return True


# --- OP03-042: Usopp's Pirate Crew ---
@register_effect("OP03-042", "on_play", "[On Play] Add blue Usopp from trash to hand")
def op03_042_usopp_crew(game_state, player, card):
    """On Play: Add a blue Usopp from trash to hand."""
    usopp_targets = [trash_card for trash_card in player.trash
                     if (getattr(trash_card, 'name', '') == 'Usopp' and
                         'Blue' in getattr(trash_card, 'colors', []))]
    if usopp_targets:
        usopp_snap = list(usopp_targets)
        def op03_042_usopp_crew_cb(selected: list) -> None:
            target_idx = int(selected[0]) if selected else -1
            if 0 <= target_idx < len(usopp_snap):
                target = usopp_snap[target_idx]
                if target in player.trash:
                    player.trash.remove(target)
                    player.hand.append(target)
                    game_state._log(f"{target.name} was added to hand from trash")
        return create_target_choice(
            game_state, player, usopp_targets,
            source_card=card,
            prompt="Usopp's Pirate Crew: Choose a blue Usopp in your trash to add to hand",
            callback=op03_042_usopp_crew_cb
        )
    return True


# --- OP03-043: Gaimon ---
@register_effect("OP03-043", "continuous", "When dealing Life damage, may trash 3 from deck then trash this")
def op03_043_gaimon(game_state, player, card):
    """When dealing Life damage, may trash 3 from deck, then trash this Character."""
    return True


@register_effect("OP03-043", "on_damage_dealt", "When dealing Life damage, may trash 3 from deck then trash this")
def op03_043_gaimon_damage(game_state, player, card):
    """When any of your cards deals Life damage, you may trash 3 cards and then trash Gaimon."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    card_snap = card

    def op03_043_gaimon_trash_cb(selected: list) -> None:
        if "yes" in selected:
            count = min(3, len(player.deck))
            for _ in range(count):
                if player.deck:
                    player.trash.append(player.deck.pop(0))
            game_state._log(f"Gaimon: Trashed {count} card(s) from top of deck")
            for c in player.cards_in_play[:]:
                if c is card_snap or getattr(c, 'name', '') == 'Gaimon':
                    player.cards_in_play.remove(c)
                    player.trash.append(c)
                    game_state._log(f"{c.name} is trashed")
                    break

    game_state.pending_choice = PendingChoice(
        choice_id=f"op03_043_{_uuid.uuid4().hex[:8]}",
        choice_type="yes_no",
        prompt="Gaimon: Trash 3 cards from the top of your deck and trash Gaimon?",
        options=[
            {"id": "yes", "label": "Yes", "card_id": card.id, "card_name": card.name},
            {"id": "no", "label": "No", "card_id": card.id, "card_name": card.name},
        ],
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=op03_043_gaimon_trash_cb,
    )
    return True


# --- OP03-044: Kaya ---
@register_effect("OP03-044", "on_play", "[On Play] Draw 2, trash 2")
def op03_044_kaya(game_state, player, card):
    """On Play: Draw 2 cards and trash 2 cards."""
    draw_cards(player, 2)
    trash_from_hand(player, 2, game_state, card)
    return True


# --- OP03-045: Carne ---
@register_effect("OP03-045", "blocker", "[Blocker]")
def op03_045_carne_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP03-045", "continuous", "[Opponent's Turn] If 20 or less cards in deck, gain +3000 power")
def op03_045_carne_cont(game_state, player, card):
    """Opponent's Turn: If 20 or less cards in deck, gain +3000 power."""
    if game_state.current_player != player and len(player.deck) <= 20:
        card.power_modifier = getattr(card, 'power_modifier', 0) + 3000
    return True


# --- OP03-047: Zeff ---
@register_effect("OP03-047", "on_play", "[On Play] Return cost 3 or less to hand, may trash 2 from deck")
def op03_047_zeff(game_state, player, card):
    """On Play: Return cost 3 or less Character to hand, may trash 2 from deck."""
    opponent = get_opponent(game_state, player)
    all_chars = list(player.cards_in_play) + list(opponent.cards_in_play)
    targets = [c for c in all_chars if (getattr(c, 'cost', 0) or 0) <= 3 and c != card]
    from ...game_engine import PendingChoice
    import uuid as _uuid

    options = []
    for i, target in enumerate(targets):
        owner = "Your" if target in player.cards_in_play else "Opponent's"
        options.append({
            "id": str(i),
            "label": f"{owner} {target.name} (Cost: {target.cost or 0})",
            "card_id": target.id,
            "card_name": target.name,
        })

    if not targets:
        def zeff_opt_trash_cb(selected: list) -> None:
            if "yes" in selected:
                for _ in range(min(2, len(player.deck))):
                    if player.deck:
                        player.trash.append(player.deck.pop(0))
                game_state._log(f"{player.name} trashed 2 card(s) from top of deck")

        game_state.pending_choice = PendingChoice(
            choice_id=f"op03_047_trash_{_uuid.uuid4().hex[:8]}",
            choice_type="yes_no",
            prompt="Zeff: Trash 2 cards from the top of your deck?",
            options=[
                {"id": "yes", "label": "Yes", "card_id": card.id, "card_name": card.name},
                {"id": "no", "label": "No", "card_id": card.id, "card_name": card.name},
            ],
            min_selections=1,
            max_selections=1,
            source_card_id=card.id,
            source_card_name=card.name,
            callback=zeff_opt_trash_cb,
        )
        return True

    targets_snap = list(targets)

    def op03_047_zeff_return_cb(selected: list) -> None:
        import uuid as _uuid2
        from ...game_engine import PendingChoice as PC
        target_idx = int(selected[0]) if selected else -1
        if 0 <= target_idx < len(targets_snap):
            target = targets_snap[target_idx]
            opponent_ref = get_opponent(game_state, player)
            for p in [player, opponent_ref]:
                if target in p.cards_in_play:
                    p.cards_in_play.remove(target)
                    p.hand.append(target)
                    game_state._log(f"{target.name} was returned to hand")
                    break
        def zeff_opt_trash2_cb(sel2: list) -> None:
            if "yes" in sel2:
                for _ in range(min(2, len(player.deck))):
                    if player.deck:
                        player.trash.append(player.deck.pop(0))
                game_state._log(f"{player.name} trashed 2 card(s) from top of deck")

        game_state.pending_choice = PC(
            choice_id=f"op03_047_trash_{_uuid2.uuid4().hex[:8]}",
            choice_type="yes_no",
            prompt="Zeff: Trash 2 cards from the top of your deck?",
            options=[
                {"id": "yes", "label": "Yes", "card_id": card.id, "card_name": card.name},
                {"id": "no", "label": "No", "card_id": card.id, "card_name": card.name},
            ],
            min_selections=1,
            max_selections=1,
            source_card_id=card.id,
            source_card_name=card.name,
            callback=zeff_opt_trash2_cb,
        )

    game_state.pending_choice = PendingChoice(
        choice_id=f"op03_047_{_uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Zeff: Choose up to 1 cost 3 or less Character to return to hand",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=op03_047_zeff_return_cb,
    )
    return True


# --- OP03-048: Nojiko ---
@register_effect("OP03-048", "on_play", "[On Play] If Leader is Nami, return opponent's cost 5 or less to hand")
def op03_048_nojiko(game_state, player, card):
    """On Play: If Leader is Nami, return opponent's cost 5 or less Character to hand."""
    if player.leader and getattr(player.leader, 'name', '') == 'Nami':
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 5]
        if targets:
            return create_return_to_hand_choice(game_state, player, targets, source_card=card,
                                               prompt="Choose opponent's cost 5 or less Character to return to hand")
    return True


# --- OP03-049: Patty ---
@register_effect("OP03-049", "on_play", "[On Play] If 20 or less in deck, return cost 3 or less to hand")
def op03_049_patty(game_state, player, card):
    """On Play: If 20 or less cards in deck, return cost 3 or less Character to hand."""
    if len(player.deck) <= 20:
        opponent = get_opponent(game_state, player)
        all_chars = list(player.cards_in_play) + list(opponent.cards_in_play)
        targets = [c for c in all_chars if (getattr(c, 'cost', 0) or 0) <= 3 and c != card]
        if targets:
            return create_return_to_hand_choice(game_state, player, targets, source_card=card,
                                               prompt="Choose cost 3 or less Character to return to hand")
    return True


# --- OP03-050: Boodle ---
@register_effect("OP03-050", "blocker", "[Blocker]")
def op03_050_boodle_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP03-050", "on_ko", "[On K.O.] May trash 1 from top of deck")
def op03_050_boodle_ko(game_state, player, card):
    """On K.O.: May trash 1 card from top of deck."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    def boodle_opt_trash_cb(selected: list) -> None:
        if "yes" in selected:
            if player.deck:
                player.trash.append(player.deck.pop(0))
            game_state._log(f"{player.name} trashed 1 card from top of deck")

    game_state.pending_choice = PendingChoice(
        choice_id=f"op03_050_{_uuid.uuid4().hex[:8]}",
        choice_type="yes_no",
        prompt="Boodle: Trash 1 card from the top of your deck?",
        options=[
            {"id": "yes", "label": "Yes", "card_id": card.id, "card_name": card.name},
            {"id": "no", "label": "No", "card_id": card.id, "card_name": card.name},
        ],
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=boodle_opt_trash_cb,
    )
    return True


# --- OP03-051: Bell-mère ---
@register_effect("OP03-051", "on_ko", "[On K.O.] May trash 3 from top of deck")
def op03_051_bellmere(game_state, player, card):
    """On K.O.: May trash 3 cards from top of deck."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    def bellmere_ko_trash_cb(selected: list) -> None:
        if "yes" in selected:
            for _ in range(min(3, len(player.deck))):
                if player.deck:
                    player.trash.append(player.deck.pop(0))
            game_state._log(f"{player.name} trashed 3 card(s) from top of deck")

    game_state.pending_choice = PendingChoice(
        choice_id=f"op03_051_{_uuid.uuid4().hex[:8]}",
        choice_type="yes_no",
        prompt="Bell-mère: Trash 3 cards from the top of your deck?",
        options=[
            {"id": "yes", "label": "Yes", "card_id": card.id, "card_name": card.name},
            {"id": "no", "label": "No", "card_id": card.id, "card_name": card.name},
        ],
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=bellmere_ko_trash_cb,
    )
    return True


@register_effect("OP03-051", "on_damage_dealt", "[DON!! x1] On damage to Life, may trash 7 from deck")
def op03_051_bellmere_damage(game_state, player, card):
    """When this card deals Life damage with DON attached, you may trash 7 cards from the top of your deck."""
    if getattr(card, 'attached_don', 0) < 1:
        return True
    from ...game_engine import PendingChoice
    import uuid as _uuid
    def op03_051_bellmere_trash_cb(selected: list) -> None:
        if "yes" in selected:
            count = min(7, len(player.deck))
            for _ in range(count):
                if player.deck:
                    player.trash.append(player.deck.pop(0))
            game_state._log(f"Bell-mère: Trashed {count} card(s) from top of deck")

    game_state.pending_choice = PendingChoice(
        choice_id=f"op03_051_{_uuid.uuid4().hex[:8]}",
        choice_type="yes_no",
        prompt="Bell-mere: Trash 7 cards from the top of your deck?",
        options=[
            {"id": "yes", "label": "Yes", "card_id": card.id, "card_name": card.name},
            {"id": "no", "label": "No", "card_id": card.id, "card_name": card.name},
        ],
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=op03_051_bellmere_trash_cb,
    )
    return True


# --- OP03-053: Yosaku & Johnny ---
@register_effect("OP03-053", "continuous", "[DON!! x1] If 20 or less in deck, gain +2000 power")
def op03_053_yosaku_johnny(game_state, player, card):
    """DON x1: If 20 or less cards in deck, gain +2000 power."""
    if getattr(card, 'attached_don', 0) >= 1 and len(player.deck) <= 20:
        card.power_modifier = getattr(card, 'power_modifier', 0) + 2000
    return True


# --- OP03-059: Kaku ---
@register_effect("OP03-059", "on_attack", "[When Attacking] DON!! -1: Gain Banish")
def op03_059_kaku(game_state, player, card):
    """When Attacking: Return 1 DON to gain Banish."""
    def _kaku_banish_cb():
        card.has_banish = True
        game_state._log(f"  {card.name} gained [Banish]")

    result = optional_don_return(game_state, player, 1, source_card=card, post_callback=_kaku_banish_cb)
    if not result:
        return True  # Pending choice
    return True


# --- OP03-060: Kalifa ---
@register_effect("OP03-060", "on_attack", "[When Attacking] DON!! -1: Draw 2, trash 1")
def op03_060_kalifa(game_state, player, card):
    """When Attacking: Return 1 DON to draw 2 and trash 1."""
    def _kalifa_draw_trash_cb():
        draw_cards(player, 2)
        trash_from_hand(player, 1, game_state, None)
        game_state._log(f"  Kalifa: Draw 2, trash 1")

    result = optional_don_return(game_state, player, 1, source_card=card, post_callback=_kalifa_draw_trash_cb)
    if not result:
        return True  # Pending choice
    return True


# --- OP03-062: Kokoro ---
@register_effect("OP03-062", "on_play", "[On Play] Look at 5, reveal Water Seven card to hand")
def op03_062_kokoro(game_state, player, card):
    """On Play: Look at top 5, reveal a Water Seven card to hand."""
    def filter_fn(c):
        return ('Water Seven' in (c.card_origin or '')
                and getattr(c, 'name', '') != 'Kokoro')
    search_top_cards(game_state, player, 5, add_count=1, filter_fn=filter_fn,
                     source_card=card,
                     prompt="Look at top 5. Choose a Water Seven card to add to hand.")
    return True


# --- OP03-063: Zambai ---
@register_effect("OP03-063", "blocker", "[Blocker]")
def op03_063_zambai_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP03-063", "on_play", "[On Play] DON!! -1: If Water Seven Leader, draw 1")
def op03_063_zambai_play(game_state, player, card):
    """On Play: Return 1 DON. If Water Seven Leader, draw 1."""
    def _zambai_draw_cb():
        if player.leader and 'Water Seven' in (player.leader.card_origin or ''):
            draw_cards(player, 1)
            game_state._log(f"  Zambai: Draw 1")

    result = optional_don_return(game_state, player, 1, source_card=card, post_callback=_zambai_draw_cb)
    if not result:
        return True  # Pending choice
    return True


# --- OP03-064: Tilestone ---
@register_effect("OP03-064", "on_ko", "[On K.O.] If Galley-La Leader, add 1 DON rested")
def op03_064_tilestone(game_state, player, card):
    """On K.O.: If Leader is Galley-La Company, you may add 1 DON rested."""
    if not (player.leader and 'Galley-La Company' in (player.leader.card_origin or '')):
        return True
    from ...game_engine import PendingChoice
    import uuid as _uuid
    def tilestone_add_don_cb(selected: list) -> None:
        if "yes" in selected:
            add_don_from_deck(player, 1)
            game_state._log(f"{player.name} added 1 rested DON!! from DON deck")

    game_state.pending_choice = PendingChoice(
        choice_id=f"op03_064_{_uuid.uuid4().hex[:8]}",
        choice_type="yes_no",
        prompt="Tilestone: Add 1 DON!! card from your DON!! deck (rested)?",
        options=[
            {"id": "yes", "label": "Yes", "card_id": card.id, "card_name": card.name},
            {"id": "no", "label": "No", "card_id": card.id, "card_name": card.name},
        ],
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=tilestone_add_don_cb,
    )
    return True


# --- OP03-065: Chimney & Gonbe ---
@register_effect("OP03-065", "blocker", "[Blocker]")
def op03_065_chimney(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


# --- OP03-066: Paulie ---
@register_effect("OP03-066", "on_play", "[On Play] Rest 2 DON: Add 1 DON active. If 8+ DON, K.O. cost 4 or less")
def op03_066_paulie(game_state, player, card):
    """On Play: You may rest 2 DON to add 1 active DON. If you then have 8+ DON, you may K.O. cost 4 or less."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    if player.don_pool.count("active") < 2:
        return True
    def op03_066_paulie_cb(selected: list) -> None:
        import uuid as _uuid2
        from ...game_engine import PendingChoice as PC
        if "yes" not in selected:
            return
        rested = 0
        for i in range(len(player.don_pool)):
            if player.don_pool[i] == "active" and rested < 2:
                player.don_pool[i] = "rested"
                rested += 1
        add_don_from_deck(player, 1, set_active=True)
        game_state._log(f"{player.name} rested 2 DON!! and added 1 active DON!! from DON deck")
        if len(player.don_pool) >= 8:
            def paulie_ko_cb(sel2: list) -> None:
                if "yes" not in sel2:
                    return
                opponent_ref = get_opponent(game_state, player)
                ko_targets = [c for c in opponent_ref.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
                if ko_targets:
                    create_ko_choice(game_state, player, ko_targets, source_card=None,
                                     prompt="Paulie: Choose opponent's cost 4 or less Character to K.O.")
            game_state.pending_choice = PC(
                choice_id=f"op03_066_follow_{_uuid2.uuid4().hex[:8]}",
                choice_type="yes_no",
                prompt="Paulie: K.O. an opponent's cost 4 or less Character?",
                options=[
                    {"id": "yes", "label": "Yes", "card_id": "op03_066", "card_name": "Paulie"},
                    {"id": "no", "label": "No", "card_id": "op03_066", "card_name": "Paulie"},
                ],
                min_selections=1,
                max_selections=1,
                callback=paulie_ko_cb,
            )

    game_state.pending_choice = PendingChoice(
        choice_id=f"op03_066_{_uuid.uuid4().hex[:8]}",
        choice_type="yes_no",
        prompt="Paulie: Rest 2 active DON!! to add 1 active DON!! from your DON!! deck?",
        options=[
            {"id": "yes", "label": "Yes", "card_id": card.id, "card_name": card.name},
            {"id": "no", "label": "No", "card_id": card.id, "card_name": card.name},
        ],
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=op03_066_paulie_cb,
    )
    return True


@register_effect("OP03-047", "on_damage_dealt", "[DON!! x1] On damage to Life, may trash 7 from deck")
def op03_047_zeff_damage(game_state, player, card):
    """When this card deals Life damage with DON attached, you may trash 7 cards from the top of your deck."""
    if getattr(card, 'attached_don', 0) < 1:
        return True
    from ...game_engine import PendingChoice
    import uuid as _uuid
    def op03_047_zeff_trash_cb(selected: list) -> None:
        if "yes" in selected:
            count = min(7, len(player.deck))
            for _ in range(count):
                if player.deck:
                    player.trash.append(player.deck.pop(0))
            game_state._log(f"Zeff: Trashed {count} card(s) from top of deck")

    game_state.pending_choice = PendingChoice(
        choice_id=f"op03_047_damage_{_uuid.uuid4().hex[:8]}",
        choice_type="yes_no",
        prompt="Zeff: Trash 7 cards from the top of your deck?",
        options=[
            {"id": "yes", "label": "Yes", "card_id": card.id, "card_name": card.name},
            {"id": "no", "label": "No", "card_id": card.id, "card_name": card.name},
        ],
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=op03_047_zeff_trash_cb,
    )
    return True


# --- OP03-067: Peepley Lulu ---
@register_effect("OP03-067", "on_attack", "[DON!! x1] If Galley-La Leader, add 1 DON rested")
def op03_067_lulu(game_state, player, card):
    """DON x1: If Galley-La Leader, you may add 1 DON rested."""
    if getattr(card, 'attached_don', 0) < 1:
        return False
    if not (player.leader and 'Galley-La Company' in (player.leader.card_origin or '')):
        return True
    from ...game_engine import PendingChoice
    import uuid as _uuid
    def lulu_add_don_cb(selected: list) -> None:
        if "yes" in selected:
            add_don_from_deck(player, 1)
            game_state._log(f"{player.name} added 1 rested DON!! from DON deck")

    game_state.pending_choice = PendingChoice(
        choice_id=f"op03_067_{_uuid.uuid4().hex[:8]}",
        choice_type="yes_no",
        prompt="Peepley Lulu: Add 1 DON!! card from your DON!! deck (rested)?",
        options=[
            {"id": "yes", "label": "Yes", "card_id": card.id, "card_name": card.name},
            {"id": "no", "label": "No", "card_id": card.id, "card_name": card.name},
        ],
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=lulu_add_don_cb,
    )
    return True


# --- OP03-068: Minozebra ---
@register_effect("OP03-068", "continuous", "[Banish]")
def op03_068_minozebra_banish(game_state, player, card):
    """Banish."""
    card.has_banish = True
    return True


@register_effect("OP03-068", "on_ko", "[On K.O.] If Impel Down Leader, add 1 DON rested")
def op03_068_minozebra_ko(game_state, player, card):
    """On K.O.: If Impel Down Leader, you may add 1 DON rested."""
    if not (player.leader and 'Impel Down' in (player.leader.card_origin or '')):
        return True
    from ...game_engine import PendingChoice
    import uuid as _uuid
    def minozebra_add_don_cb(selected: list) -> None:
        if "yes" in selected:
            add_don_from_deck(player, 1)
            game_state._log(f"{player.name} added 1 rested DON!! from DON deck")

    game_state.pending_choice = PendingChoice(
        choice_id=f"op03_068_{_uuid.uuid4().hex[:8]}",
        choice_type="yes_no",
        prompt="Minozebra: Add 1 DON!! card from your DON!! deck (rested)?",
        options=[
            {"id": "yes", "label": "Yes", "card_id": card.id, "card_name": card.name},
            {"id": "no", "label": "No", "card_id": card.id, "card_name": card.name},
        ],
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=minozebra_add_don_cb,
    )
    return True


# --- OP03-069: Minorhinoceros ---
@register_effect("OP03-069", "on_ko", "[On K.O.] If Impel Down Leader, draw 2 trash 1")
def op03_069_minorhinoceros(game_state, player, card):
    """On K.O.: If Impel Down Leader, draw 2 and trash 1."""
    if player.leader and 'Impel Down' in (player.leader.card_origin or ''):
        draw_cards(player, 2)
        trash_from_hand(player, 1, game_state, card)
    return True


# --- OP03-070: Monkey.D.Luffy ---
@register_effect("OP03-070", "on_play", "[On Play] DON!! -1, trash cost 5 Character: Gain Rush")
def op03_070_luffy(game_state, player, card):
    """On Play: Return 1 DON and trash a cost 5 Character from hand to gain Rush."""
    cost5_cards = [c for c in player.hand
                   if getattr(c, 'card_type', '') == 'CHARACTER' and
                   (getattr(c, 'cost', 0) or 0) == 5]
    if not cost5_cards:
        return True

    def _luffy_rush_cb():
        cost5_now = [c for c in player.hand
                     if getattr(c, 'card_type', '') == 'CHARACTER' and
                     (getattr(c, 'cost', 0) or 0) == 5]
        if not cost5_now:
            card.has_rush = True
            game_state._log(f"  {card.name} gained [Rush]")
            return
        cost5_snap = list(cost5_now)
        from ...game_engine import PendingChoice
        import uuid as _uuid

        def _trash_cb(selected: list) -> None:
            target_idx = int(selected[0]) if selected else -1
            if 0 <= target_idx < len(cost5_snap):
                target = cost5_snap[target_idx]
                if target in player.hand:
                    player.hand.remove(target)
                    player.trash.append(target)
                    game_state._log(f"Luffy: Trashed {target.name}")
            card.has_rush = True
            game_state._log(f"  {card.name} gained [Rush]")

        game_state.pending_choice = PendingChoice(
            choice_id=f"op03_070_{_uuid.uuid4().hex[:8]}",
            choice_type="select_cards",
            prompt="Luffy: Choose a cost 5 Character to trash for Rush",
            options=[{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})",
                      "card_id": c.id, "card_name": c.name}
                     for i, c in enumerate(cost5_snap)],
            min_selections=1,
            max_selections=1,
            source_card_id=card.id,
            source_card_name=card.name,
            callback=_trash_cb,
        )

    result = optional_don_return(game_state, player, 1, source_card=card, post_callback=_luffy_rush_cb)
    if not result:
        return True  # Pending choice
    return True


# --- OP03-071: Rob Lucci ---
@register_effect("OP03-071", "on_attack", "[When Attacking] DON!! -1: Rest opponent's cost 5 or less")
def op03_071_lucci(game_state, player, card):
    """When Attacking: Return 1 DON to rest opponent's cost 5 or less."""
    def _lucci_rest_cb():
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play
                   if (getattr(c, 'cost', 0) or 0) <= 5 and not getattr(c, 'is_resting', False)]
        if targets:
            create_rest_choice(game_state, player, targets, source_card=None,
                               prompt="Rob Lucci: Choose opponent's cost 5 or less to rest")

    result = optional_don_return(game_state, player, 1, source_card=card, post_callback=_lucci_rest_cb)
    if not result:
        return True  # Pending choice
    return True


# --- OP03-078: Issho ---
@register_effect("OP03-078", "continuous", "[DON!! x1] [Your Turn] All opponent's Characters get -3 cost")
def op03_078_issho_cont(game_state, player, card):
    """DON x1: During YOUR turn only, all opponent's Characters get -3 cost."""
    if getattr(card, 'attached_don', 0) >= 1 and game_state.current_player == player:
        opponent = get_opponent(game_state, player)
        for c in opponent.cards_in_play:
            c.cost_modifier = getattr(c, 'cost_modifier', 0) - 3
    return True


@register_effect("OP03-078", "on_play", "[On Play] If opponent has 6+ cards in hand, trash 2 from their hand")
def op03_078_issho_play(game_state, player, card):
    """On Play: If opponent has 6+ cards in hand, trash 2 from their hand (blind selection)."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    opponent = get_opponent(game_state, player)
    if len(opponent.hand) < 6:
        return True
    # Blind selection: show "Card 1, Card 2, ..." without revealing names
    options = [
        {"id": str(i), "label": f"Card {i + 1}", "card_id": None, "card_name": f"Card {i + 1}"}
        for i in range(len(opponent.hand))
    ]
    opponent_snap = opponent

    def op03_078_issho_cb(selected: list) -> None:
        for idx in sorted([int(s) for s in selected], reverse=True):
            if 0 <= idx < len(opponent_snap.hand):
                trashed = opponent_snap.hand.pop(idx)
                opponent_snap.trash.append(trashed)
                game_state._log(f"Issho: {opponent_snap.name} trashed 1 card from hand")

    game_state.pending_choice = PendingChoice(
        choice_id=f"op03_078_{_uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Issho: Choose 2 cards from opponent's hand to trash (you cannot see their hand)",
        options=options,
        min_selections=2,
        max_selections=2,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=op03_078_issho_cb,
    )
    return True


# --- OP03-079: Vergo ---
@register_effect("OP03-079", "continuous", "[DON!! x1] Cannot be K.O.'d in battle")
def op03_079_vergo(game_state, player, card):
    """DON x1: Cannot be K.O.'d in battle."""
    if getattr(card, 'attached_don', 0) >= 1:
        card.cannot_be_ko_in_battle = True
    return True


# --- OP03-080: Kaku ---
@register_effect("OP03-080", "on_play", "[On Play] Place 2 CP cards from trash at bottom of deck: K.O. cost 3 or less")
def op03_080_kaku(game_state, player, card):
    """On Play: Choose 2 CP cards from trash to return to deck bottom, then K.O. cost 3 or less."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    cp_cards = [c for c in player.trash if 'CP' in (getattr(c, 'card_origin', '') or '')]
    if len(cp_cards) < 2:
        return False
    options = [{
        "id": str(i),
        "label": f"{c.name} (Cost: {c.cost or 0})",
        "card_id": c.id,
        "card_name": c.name,
    } for i, c in enumerate(cp_cards)]
    cp_snap = list(cp_cards)

    def _kaku_ko_after_order(ordered_cards: list) -> None:
        for c in ordered_cards:
            if c in player.trash:
                player.trash.remove(c)
                player.deck.append(c)
                game_state._log(f"{c.name} returned to deck bottom")
        opponent_ref = get_opponent(game_state, player)
        ko_targets = [c for c in opponent_ref.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
        if ko_targets:
            create_ko_choice(game_state, player, ko_targets, source_card=None,
                             prompt="Kaku: Choose opponent's cost 3 or less Character to K.O.")

    def op03_080_kaku_cb(selected: list) -> None:
        import uuid as _uuid2
        from ...game_engine import PendingChoice as PC
        chosen = []
        for sel in selected:
            idx = int(sel)
            if 0 <= idx < len(cp_snap):
                chosen.append(cp_snap[idx])
        if len(chosen) < 2:
            _kaku_ko_after_order(chosen)
            return
        chosen_snap = list(chosen)
        def op03_080_order_cb(sel2: list) -> None:
            first_idx = int(sel2[0]) if sel2 else 0
            ordered = list(chosen_snap)
            if 0 <= first_idx < len(ordered):
                first = ordered.pop(first_idx)
                ordered.insert(0, first)
            _kaku_ko_after_order(ordered)
        opts = [{"id": str(i), "label": f"{c.name} (goes deeper first)",
                 "card_id": c.id, "card_name": c.name}
                for i, c in enumerate(chosen_snap)]
        game_state.pending_choice = PC(
            choice_id=f"op03_080_order_{_uuid2.uuid4().hex[:8]}",
            choice_type="select_target",
            prompt="Kaku: Choose which CP card goes to the bottom FIRST (goes deeper in deck)",
            options=opts,
            min_selections=1,
            max_selections=1,
            callback=op03_080_order_cb,
        )

    game_state.pending_choice = PendingChoice(
        choice_id=f"op03_080_{_uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Kaku: Choose exactly 2 CP type cards from your trash to return to bottom of deck (then K.O. cost 3 or less)",
        options=options,
        min_selections=2,
        max_selections=2,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=op03_080_kaku_cb,
    )
    return True


# --- OP03-081: Kalifa ---
@register_effect("OP03-081", "on_play", "[On Play] Draw 2, trash 2, give opponent -2 cost")
def op03_081_kalifa(game_state, player, card):
    """On Play: Draw 2, trash 2 (prompted), then give opponent's Character -2 cost."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    draw_cards(player, 2)
    if player.hand:
        options = [{
            "id": str(i),
            "label": f"{c.name} (Cost: {c.cost or 0})",
            "card_id": c.id,
            "card_name": c.name,
        } for i, c in enumerate(player.hand)]
        hand_snap = list(player.hand)

        def op03_081_kalifa_cb(selected: list) -> None:
            for idx in sorted([int(s) for s in selected], reverse=True):
                if 0 <= idx < len(hand_snap):
                    target = hand_snap[idx]
                    if target in player.hand:
                        player.hand.remove(target)
                        player.trash.append(target)
                        game_state._log(f"{player.name} trashed {target.name} from hand")
            opponent_ref = get_opponent(game_state, player)
            if opponent_ref.cards_in_play:
                create_cost_reduction_choice(
                    game_state, player, list(opponent_ref.cards_in_play), -2, source_card=None,
                    prompt="Kalifa: Choose opponent's Character to give -2 cost"
                )

        game_state.pending_choice = PendingChoice(
            choice_id=f"op03_081_{_uuid.uuid4().hex[:8]}",
            choice_type="select_cards",
            prompt="Kalifa: Choose 2 cards to trash from your hand (then give opponent -2 cost)",
            options=options,
            min_selections=min(2, len(hand_snap)),
            max_selections=min(2, len(hand_snap)),
            source_card_id=card.id,
            source_card_name=card.name,
            callback=op03_081_kalifa_cb,
        )
        return True
    opponent = get_opponent(game_state, player)
    if opponent.cards_in_play:
        return create_cost_reduction_choice(game_state, player, list(opponent.cards_in_play), -2, source_card=card,
                                           prompt="Choose opponent's Character to give -2 cost")
    return True


# --- OP03-083: Corgy ---
@register_effect("OP03-083", "on_play", "[On Play] Look at 5, trash up to 2, rest at bottom")
def op03_083_corgy(game_state, player, card):
    """On Play: Look at top 5 cards, trash up to 2, place rest at bottom in any order."""
    from ..hardcoded import _player_index
    from ...game_engine import PendingChoice
    import uuid

    if not player.deck:
        return True

    actual_look = min(5, len(player.deck))
    top_cards = player.deck[:actual_look]
    if not top_cards:
        return True

    # All cards are selectable for trashing
    options = []
    for i, c in enumerate(top_cards):
        options.append({
            "id": str(i),
            "label": f"{c.name} (Cost: {c.cost or 0})",
            "card_id": c.id,
            "card_name": c.name,
            "selectable": True,
        })

    source_name = card.name
    source_id = card.id
    actual_look_snap = actual_look

    def op03_083_corgy_cb(selected: list) -> None:
        chosen_indices = sorted([int(s) for s in selected], reverse=True) if selected else []
        trashed_cards = []
        for idx in chosen_indices:
            if 0 <= idx < len(player.deck):
                trashed_card = player.deck.pop(idx)
                trashed_cards.append(trashed_card)
                player.trash.append(trashed_card)
        if trashed_cards:
            game_state._log(f"{source_name}: Trashed {', '.join(c.name for c in trashed_cards)}")
        remaining_count = actual_look_snap - len(trashed_cards)
        remaining = player.deck[:remaining_count]
        for _ in range(remaining_count):
            if player.deck:
                player.deck.pop(0)
        if len(remaining) <= 1:
            player.deck.extend(remaining)
            if remaining:
                game_state._log(f"{source_name}: Remaining card placed at bottom of deck")
        elif remaining:
            game_state._create_deck_order_choice(
                player, remaining, [],
                source_name=source_name,
                source_id=source_id,
            )

    game_state.pending_choice = PendingChoice(
        choice_id=f"corgy_trash_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Look at top 5 cards: choose up to 2 to trash. Rest go to bottom.",
        options=options,
        min_selections=0,
        max_selections=min(2, actual_look),
        source_card_id=card.id,
        source_card_name=card.name,
        callback=op03_083_corgy_cb,
    )
    return True


# --- OP03-086: Spandam ---
@register_effect("OP03-086", "on_play", "[On Play] If CP Leader, look at 3, reveal CP card to hand")
def op03_086_spandam(game_state, player, card):
    """On Play: If CP Leader, look at top 3, reveal a CP card to hand."""
    if not check_leader_type(player, "CP"):
        return True
    def filter_fn(c):
        return 'CP' in (getattr(c, 'card_origin', '') or '') and getattr(c, 'name', '') != 'Spandam'
    return search_top_cards(game_state, player, look_count=3, add_count=1,
                            filter_fn=filter_fn, source_card=card, trash_rest=True,
                            prompt="Spandam: Choose 1 CP card to add to hand")


# --- OP03-088: Fukurou ---
@register_effect("OP03-088", "continuous", "Cannot be K.O.'d by effects")
def op03_088_fukurou_cont(game_state, player, card):
    """Cannot be K.O.'d by effects."""
    card.cannot_be_ko_by_effects = True
    return True


@register_effect("OP03-088", "blocker", "[Blocker]")
def op03_088_fukurou_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


# --- OP03-089: Brannew ---
@register_effect("OP03-089", "on_play", "[On Play] Look at 3, reveal Navy card to hand")
def op03_089_brannew(game_state, player, card):
    """On Play: Look at top 3, reveal a Navy card to hand."""
    def filter_fn(c):
        return 'Navy' in (getattr(c, 'card_origin', '') or '') and getattr(c, 'name', '') != 'Brannew'
    return search_top_cards(game_state, player, look_count=3, add_count=1,
                            filter_fn=filter_fn, source_card=card, trash_rest=True,
                            prompt="Brannew: Choose 1 Navy card to add to hand")


# --- OP03-090: Blueno ---
@register_effect("OP03-090", "continuous", "[DON!! x1] Gain Blocker")
def op03_090_blueno_cont(game_state, player, card):
    """DON x1: Gain Blocker."""
    if getattr(card, 'attached_don', 0) >= 1:
        card.has_blocker = True
    return True


@register_effect("OP03-090", "on_ko", "[On K.O.] Play CP cost 4 or less from trash rested")
def op03_090_blueno_ko(game_state, player, card):
    """On K.O.: Play a CP cost 4 or less Character from trash rested."""
    targets = [c for c in player.trash
               if getattr(c, 'card_type', '') == 'CHARACTER'
               and 'CP' in (c.card_origin or '')
               and (getattr(c, 'cost', 0) or 0) <= 4]
    if targets:
        return create_play_from_trash_choice(game_state, player, targets,
                                            rest_on_play=True, source_card=card,
                                            prompt="Choose a CP cost 4 or less Character to play from trash (rested)")
    return True


# --- OP03-091: Helmeppo ---
@register_effect("OP03-091", "on_play", "[On Play] Set opponent's no-effect Character cost to 0")
def op03_091_helmeppo(game_state, player, card):
    """On Play: Set opponent's Character with no base effect cost to 0."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if not getattr(c, 'effect', None) or getattr(c, 'effect', '') == '']
    if not targets:
        return True
    options = [{
        "id": str(i),
        "label": f"{c.name} (Cost: {(c.cost or 0) + getattr(c, 'cost_modifier', 0)})",
        "card_id": c.id,
        "card_name": c.name,
    } for i, c in enumerate(targets)]
    targets_snap = list(targets)

    def op03_091_helmeppo_cb(selected: list) -> None:
        target_idx = int(selected[0]) if selected else -1
        opponent_ref = get_opponent(game_state, player)
        if 0 <= target_idx < len(targets_snap):
            target = targets_snap[target_idx]
            for p in [opponent_ref, player]:
                for c in p.cards_in_play:
                    if c is target:
                        current_cost = max(0, (c.cost or 0) + getattr(c, 'cost_modifier', 0))
                        c.cost_modifier = getattr(c, 'cost_modifier', 0) - current_cost
                        game_state._log(f"{c.name}'s cost set to 0 this turn")
                        return

    game_state.pending_choice = PendingChoice(
        choice_id=f"op03_091_{_uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Helmeppo: Choose opponent's no-effect Character to set cost to 0",
        options=options,
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=op03_091_helmeppo_cb,
    )
    return True


# --- OP03-092: Rob Lucci ---
@register_effect("OP03-092", "on_play", "[On Play] Place 2 CP cards from trash at bottom: Gain Rush")
def op03_092_lucci(game_state, player, card):
    """On Play: Choose 2 CP cards from trash to return to deck bottom, then gain Rush."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    cp_cards = [c for c in player.trash if 'CP' in (getattr(c, 'card_origin', '') or '')]
    if len(cp_cards) < 2:
        return False
    options = [{
        "id": str(i),
        "label": f"{c.name} (Cost: {c.cost or 0})",
        "card_id": c.id,
        "card_name": c.name,
    } for i, c in enumerate(cp_cards)]
    cp_snap = list(cp_cards)
    card_snap = card

    def op03_092_lucci_play_cb(selected: list) -> None:
        for sel in selected:
            idx = int(sel)
            if 0 <= idx < len(cp_snap):
                c = cp_snap[idx]
                if c in player.trash:
                    player.trash.remove(c)
                    player.deck.append(c)
                    game_state._log(f"{c.name} was returned to the bottom of the deck")
        if card_snap in player.cards_in_play:
            card_snap.has_rush = True
            game_state._log(f"{card_snap.name} gained [Rush]")

    game_state.pending_choice = PendingChoice(
        choice_id=f"op03_092_{_uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Rob Lucci: Choose 2 CP type cards from your trash to return to bottom of deck (then gain Rush)",
        options=options,
        min_selections=2,
        max_selections=2,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=op03_092_lucci_play_cb,
    )
    return True


# --- OP03-093: Wanze ---
@register_effect("OP03-093", "on_play", "[On Play] Trash 1: If CP Leader, K.O. cost 1 or less")
def op03_093_wanze(game_state, player, card):
    """On Play: Trash 1 card (prompted). If CP Leader, K.O. opponent's cost 1 or less."""
    if not player.hand:
        return True
    hand_snap = list(player.hand)

    def op03_093_wanze_cb(selected: list) -> None:
        target_idx = int(selected[0]) if selected else -1
        if 0 <= target_idx < len(hand_snap):
            target = hand_snap[target_idx]
            if target in player.hand:
                player.hand.remove(target)
                player.trash.append(target)
                game_state._log(f"{player.name} trashed {target.name} from hand")
        if player.leader and 'CP' in (player.leader.card_origin or ''):
            opponent_ref = get_opponent(game_state, player)
            ko_targets = [c for c in opponent_ref.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 1]
            if ko_targets:
                create_ko_choice(game_state, player, ko_targets, source_card=None,
                                 prompt="Wanze: Choose opponent's cost 1 or less Character to K.O.")

    return create_hand_discard_choice(
        game_state, player, hand_snap, source_card=card,
        callback=op03_093_wanze_cb,
        prompt="Wanze: Choose 1 card to trash from hand (may K.O. cost 1 or less if CP Leader)",
    )


# --- OP03-102: Sanji ---
@register_effect("OP03-102", "on_attack", "[DON!! x2] Add top/bottom Life to hand: Add top deck to Life")
def op03_102_sanji(game_state, player, card):
    """DON x2: Choose top or bottom Life to add to hand, then add top deck card to Life."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    if getattr(card, 'attached_don', 0) < 2:
        return False
    if not player.life_cards:
        return True
    def op03_102_sanji_cb(selected: list) -> None:
        choice = selected[0] if selected else "top"
        if player.life_cards:
            life_card = player.life_cards.pop() if choice == "top" else player.life_cards.pop(0)
            player.hand.append(life_card)
            game_state._log(f"{player.name} added Life card to hand")
        if player.deck:
            new_life = player.deck.pop(0)
            player.life_cards.append(new_life)
            game_state._log(f"{player.name} added top deck card to top of Life")

    game_state.pending_choice = PendingChoice(
        choice_id=f"op03_102_{_uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Sanji: Choose which Life card to add to hand (then top deck card added to Life)",
        options=[
            {"id": "top", "label": "Top of Life", "card_id": card.id, "card_name": card.name},
            {"id": "bottom", "label": "Bottom of Life", "card_id": card.id, "card_name": card.name},
        ],
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=op03_102_sanji_cb,
    )
    return True


# --- OP03-104: Shirley ---
@register_effect("OP03-104", "blocker", "[Blocker]")
def op03_104_shirley_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP03-104", "on_play", "[On Play] Look at top of opponent's Life, place at top or bottom")
def op03_104_shirley_play(game_state, player, card):
    """On Play: Look at top of opponent's Life, then choose to leave at top or move to bottom."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    opponent = get_opponent(game_state, player)
    if not opponent.life_cards:
        return True
    top_life = opponent.life_cards[-1]  # peek without removing
    opponent_snap = opponent

    def op03_104_shirley_cb(selected: list) -> None:
        if opponent_snap.life_cards:
            choice = selected[0] if selected else "top"
            if choice == "bottom":
                moved = opponent_snap.life_cards.pop()
                opponent_snap.life_cards.insert(0, moved)
                game_state._log("Shirley: Moved opponent's top Life card to bottom")
            else:
                game_state._log("Shirley: Opponent's top Life card stays at top")

    game_state.pending_choice = PendingChoice(
        choice_id=f"op03_104_{_uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt=f"Shirley: Opponent's top Life is [{top_life.name}]. Leave at top or move to bottom?",
        options=[
            {"id": "top", "label": "Leave at top", "card_id": top_life.id, "card_name": top_life.name},
            {"id": "bottom", "label": "Move to bottom", "card_id": top_life.id, "card_name": top_life.name},
        ],
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=op03_104_shirley_cb,
    )
    return True


# --- OP03-105: Charlotte Oven ---
@register_effect("OP03-105", "on_attack", "[DON!! x1] Trash Trigger card: Gain +3000 power")
def op03_105_oven(game_state, player, card):
    """DON x1: Trash a Trigger card from hand (prompted) to gain +3000 power."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    if getattr(card, 'attached_don', 0) < 1:
        return False
    trigger_cards = [c for c in player.hand
                     if c != card and bool(str(getattr(c, 'trigger', '') or '').strip())]
    if not trigger_cards:
        return False
    options = [{
        "id": str(i),
        "label": f"{c.name} (Cost: {c.cost or 0})",
        "card_id": c.id,
        "card_name": c.name,
    } for i, c in enumerate(trigger_cards)]
    trigger_snap = list(trigger_cards)
    card_snap = card

    def op03_105_oven_cb(selected: list) -> None:
        target_idx = int(selected[0]) if selected else -1
        if 0 <= target_idx < len(trigger_snap):
            target = trigger_snap[target_idx]
            if target in player.hand:
                player.hand.remove(target)
                player.trash.append(target)
                game_state._log(f"{player.name} trashed {target.name} from hand")
        # Battle-only: use power_modifier only (no _sticky), cleared after battle
        card_snap.power_modifier = getattr(card_snap, 'power_modifier', 0) + 3000
        game_state._log(f"{card_snap.name} gains +3000 power this battle")

    game_state.pending_choice = PendingChoice(
        choice_id=f"op03_105_{_uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Charlotte Oven: Choose 1 Trigger card from hand to trash (gain +3000 power)",
        options=options,
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=op03_105_oven_cb,
    )
    return True


# --- OP03-107: Charlotte Galette ---
@register_effect("OP03-107", "blocker", "[Blocker]")
def op03_107_galette(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


# --- OP03-108: Charlotte Cracker ---
@register_effect("OP03-108", "continuous", "[DON!! x1] If less Life than opponent, gain Double Attack and +1000")
def op03_108_cracker(game_state, player, card):
    """DON x1: If less Life than opponent, gain Double Attack and +1000."""
    if getattr(card, 'attached_don', 0) >= 1:
        opponent = get_opponent(game_state, player)
        if len(player.life_cards) < len(opponent.life_cards):
            card.has_doubleattack = True
            card.has_double_attack = True
            card.power_modifier = getattr(card, 'power_modifier', 0) + 1000
    return True


@register_effect("OP03-108", "trigger", "[Trigger] Trash 1 from hand: Play this card")
def op03_108_cracker_trigger(game_state, player, card):
    """Trigger: You may trash 1 card from hand to play this card."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    if not player.hand:
        return True
    options = [{
        "id": str(i),
        "label": f"{c.name} (Cost: {c.cost or 0})",
        "card_id": c.id,
        "card_name": c.name,
    } for i, c in enumerate(player.hand)]
    hand_snap = list(player.hand)
    card_snap = card

    def op03_108_cracker_trigger_cb(selected: list) -> None:
        if selected:
            target_idx = int(selected[0])
            if 0 <= target_idx < len(hand_snap):
                target = hand_snap[target_idx]
                if target in player.hand:
                    player.hand.remove(target)
                    player.trash.append(target)
                    game_state._log(f"{player.name} trashed {target.name} from hand")
        # Play Cracker: check hand first (trigger flow), then trash
        src = None
        for c in player.hand[:]:
            if c is card_snap:
                player.hand.remove(c)
                src = c
                break
        if src is None:
            for c in player.trash[:]:
                if c is card_snap:
                    player.trash.remove(c)
                    src = c
                    break
        if src is not None:
            player.cards_in_play.append(src)
            game_state._apply_keywords(src)
            game_state._log(f"{player.name} played {src.name}")

    game_state.pending_choice = PendingChoice(
        choice_id=f"op03_108_{_uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Charlotte Cracker [Trigger]: Choose 1 card from hand to trash (to play this card to field)",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=op03_108_cracker_trigger_cb,
    )
    return True


# --- OP03-109: Charlotte Chiffon ---
@register_effect("OP03-109", "on_play", "[On Play] Trash top/bottom Life: Optionally add top deck card to Life")
def op03_109_chiffon(game_state, player, card):
    """On Play: Choose top or bottom Life to trash (prompted), then optionally add up to 1 from deck to Life."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    if not player.life_cards:
        return True
    def op03_109_chiffon_cb(selected: list) -> None:
        import uuid as _uuid2
        from ...game_engine import PendingChoice as PC
        choice = selected[0] if selected else "top"
        if player.life_cards:
            life_card = player.life_cards.pop() if choice == "top" else player.life_cards.pop(0)
            player.trash.append(life_card)
            game_state._log(f"{player.name} trashed 1 Life card")
        if player.deck:
            def op03_109_add_to_life_cb(sel2: list) -> None:
                if "1" in sel2 and player.deck:
                    deck_card = player.deck.pop(0)
                    player.life_cards.append(deck_card)
                    game_state._log(f"{player.name} added 1 card from top of deck to top of Life")

            game_state.pending_choice = PC(
                choice_id=f"op03_109_deck_{_uuid2.uuid4().hex[:8]}",
                choice_type="select_target",
                prompt="Charlotte Chiffon: Add 0 or 1 cards from top of deck to top of Life?",
                options=[
                    {"id": "1", "label": "Add 1 card to top of Life", "card_id": "chiffon", "card_name": "Charlotte Chiffon"},
                    {"id": "0", "label": "Skip (add 0)", "card_id": "chiffon", "card_name": "Charlotte Chiffon"},
                ],
                min_selections=1,
                max_selections=1,
                callback=op03_109_add_to_life_cb,
            )

    game_state.pending_choice = PendingChoice(
        choice_id=f"op03_109_{_uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Charlotte Chiffon: Choose which Life card to trash",
        options=[
            {"id": "top", "label": "Top of Life", "card_id": card.id, "card_name": card.name},
            {"id": "bottom", "label": "Bottom of Life", "card_id": card.id, "card_name": card.name},
        ],
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=op03_109_chiffon_cb,
    )
    return True


# --- OP03-110: Charlotte Smoothie ---
@register_effect("OP03-110", "on_attack", "[When Attacking] Add 1 Life (top/bottom/none) to hand: Gain +2000 power")
def op03_110_smoothie(game_state, player, card):
    """When Attacking: Choose top, bottom, or none of Life to add to hand (gain +2000 if chosen)."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    options = [
        {"id": "top", "label": "Top of Life", "card_id": card.id, "card_name": card.name},
        {"id": "bottom", "label": "Bottom of Life", "card_id": card.id, "card_name": card.name},
        {"id": "none", "label": "None (skip +2000)", "card_id": card.id, "card_name": card.name},
    ]
    if not player.life_cards:
        options = [options[2]]  # Only "None" if no life cards
    card_snap = card

    def op03_110_smoothie_cb(selected: list) -> None:
        choice_pick = selected[0] if selected else "none"
        if choice_pick != "none" and player.life_cards:
            life_card = player.life_cards.pop() if choice_pick == "top" else player.life_cards.pop(0)
            player.hand.append(life_card)
            game_state._log(f"{player.name} added 1 Life card to hand")
            card_snap.power_modifier = getattr(card_snap, 'power_modifier', 0) + 2000
            card_snap._sticky_power_modifier = getattr(card_snap, '_sticky_power_modifier', 0) + 2000
            game_state._log(f"{card_snap.name} gains +2000 power")

    game_state.pending_choice = PendingChoice(
        choice_id=f"op03_110_{_uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Charlotte Smoothie: Choose which Life card to add to hand (gain +2000 power) or None",
        options=options,
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=op03_110_smoothie_cb,
    )
    return True


@register_effect("OP03-110", "trigger", "[Trigger] Trash 1 from hand: Play this card")
def op03_110_smoothie_trigger(game_state, player, card):
    """Trigger: The player who took damage may trash 1 card from hand to play this card to field."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    if not player.hand:
        return True
    options = [{
        "id": str(i),
        "label": f"{c.name} (Cost: {c.cost or 0})",
        "card_id": c.id,
        "card_name": c.name,
    } for i, c in enumerate(player.hand)]
    hand_snap = list(player.hand)
    card_snap = card

    def op03_110_smoothie_trigger_cb(selected: list) -> None:
        if selected:
            target_idx = int(selected[0])
            if 0 <= target_idx < len(hand_snap):
                target = hand_snap[target_idx]
                if target in player.hand:
                    player.hand.remove(target)
                    player.trash.append(target)
                    game_state._log(f"{player.name} trashed {target.name} from hand")
        src = None
        for c in player.hand[:]:
            if c is card_snap:
                player.hand.remove(c)
                src = c
                break
        if src is None:
            for c in player.trash[:]:
                if c is card_snap:
                    player.trash.remove(c)
                    src = c
                    break
        if src is not None:
            player.cards_in_play.append(src)
            game_state._apply_keywords(src)
            game_state._log(f"{player.name} played {src.name}")

    game_state.pending_choice = PendingChoice(
        choice_id=f"op03_110t_{_uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Charlotte Smoothie [Trigger]: Trash 1 card from hand to play this card to field?",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=op03_110_smoothie_trigger_cb,
    )
    return True


# --- OP03-112: Charlotte Pudding ---
@register_effect("OP03-112", "on_play", "[On Play] Look at 4, reveal Sanji or Big Mom Pirates card to hand")
def op03_112_pudding(game_state, player, card):
    """On Play: Look at top 4, reveal a Sanji or Big Mom Pirates card to hand."""
    def filter_fn(c):
        return ((getattr(c, 'name', '') == 'Sanji' or 'Big Mom Pirates' in (c.card_origin or ''))
                and getattr(c, 'name', '') != 'Charlotte Pudding')
    return search_top_cards(game_state, player, look_count=4, add_count=1,
                            filter_fn=filter_fn, source_card=card,
                            prompt="Choose 1 Sanji or Big Mom Pirates card to add to hand")


# --- OP03-113: Charlotte Perospero ---
@register_effect("OP03-113", "on_ko", "[On K.O.] Look at 3, reveal Big Mom Pirates card to hand")
def op03_113_perospero(game_state, player, card):
    """On K.O.: Look at top 3, reveal a Big Mom Pirates card to hand."""
    def filter_fn(c):
        return 'Big Mom Pirates' in (getattr(c, 'card_origin', '') or '')
    return search_top_cards(game_state, player, look_count=3, add_count=1,
                            filter_fn=filter_fn, source_card=card,
                            prompt="Choose 1 Big Mom Pirates card to add to hand")


# --- OP03-114: Charlotte Linlin ---
@register_effect("OP03-114", "on_play", "[On Play] If Big Mom Pirates Leader, add deck card to Life, trash opponent's Life")
def op03_114_linlin(game_state, player, card):
    """On Play: If Big Mom Pirates Leader, add deck card to Life, trash opponent's top Life."""
    if player.leader and 'Big Mom Pirates' in (player.leader.card_origin or ''):
        if player.deck:
            player.life_cards.append(player.deck.pop(0))
        opponent = get_opponent(game_state, player)
        if opponent.life_cards:
            opponent.trash.append(opponent.life_cards.pop())
    return True


# --- OP03-115: Streusen ---
@register_effect("OP03-115", "on_play", "[On Play] Trash Trigger card (optional): K.O. cost 1 or less")
def op03_115_streusen(game_state, player, card):
    """On Play: Optionally trash a Trigger card from hand (prompted) to K.O. opponent's cost 1 or less."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    trigger_cards = [c for c in player.hand
                     if c != card and bool(str(getattr(c, 'trigger', '') or '').strip())]
    if not trigger_cards:
        return False
    options = [{
        "id": str(i),
        "label": f"{c.name} (Cost: {c.cost or 0})",
        "card_id": c.id,
        "card_name": c.name,
    } for i, c in enumerate(trigger_cards)]
    trigger_snap = list(trigger_cards)

    def op03_115_streusen_cb(selected: list) -> None:
        if selected:
            target_idx = int(selected[0])
            if 0 <= target_idx < len(trigger_snap):
                target = trigger_snap[target_idx]
                if target in player.hand:
                    player.hand.remove(target)
                    player.trash.append(target)
                    game_state._log(f"{player.name} trashed {target.name} from hand")
            opponent_ref = get_opponent(game_state, player)
            ko_targets = [c for c in opponent_ref.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 1]
            if ko_targets:
                create_ko_choice(game_state, player, ko_targets, source_card=None,
                                 prompt="Streusen: Choose opponent's cost 1 or less Character to K.O.")

    game_state.pending_choice = PendingChoice(
        choice_id=f"op03_115_{_uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Streusen: Optionally choose 1 Trigger card from hand to trash (then K.O. cost 1 or less)",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=op03_115_streusen_cb,
    )
    return True


# --- OP03-116: Shirahoshi ---
@register_effect("OP03-116", "on_play", "[On Play] Draw 3, trash 2")
def op03_116_shirahoshi(game_state, player, card):
    """On Play: Draw 3 cards and trash 2."""
    draw_cards(player, 3)
    trash_from_hand(player, 2, game_state, card)
    return True


# --- OP03-020: Striker ---
@register_effect("OP03-020", "activate", "[Activate: Main] DON-2, rest Stage: If Ace leader, look at 5, add Event")
def op03_020_striker(game_state, player, card):
    """[Activate: Main] Rest 2 DON and this Stage: If Ace leader, look at 5, add 1 Event."""
    if card.is_resting or getattr(card, 'main_activated_this_turn', False):
        return False
    if not player.leader or 'portgas.d.ace' not in (player.leader.name or '').lower():
        return False
    if player.don_pool.count('active') < 2:
        return False
    # Pay DON-2 cost
    for _ in range(2):
        idx = player.don_pool.index('active')
        player.don_pool[idx] = 'rested'
    card.is_resting = True
    card.main_activated_this_turn = True
    return search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: c.card_type == 'EVENT',
        source_card=card,
        prompt="Striker: Look at top 5, choose up to 1 Event to add to hand")


@register_effect("OP03-116", "trigger", "[Trigger] Play this card")
def op03_116_shirahoshi_trigger(game_state, player, card):
    """Trigger: Play this card."""
    player.cards_in_play.append(card)
    return True


# --- OP03-117: Napoleon ---
@register_effect("OP03-117", "activate", "[Activate: Main] Rest: Choose Charlotte Linlin to gain +1000 until next turn")
def op03_117_napoleon(game_state, player, card):
    """Activate: Rest to give a chosen Charlotte Linlin +1000 until next turn."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    if getattr(card, 'is_resting', False):
        return False
    card.is_resting = True
    linlin_cards = [c for c in player.cards_in_play if getattr(c, 'name', '') == 'Charlotte Linlin']
    if player.leader and getattr(player.leader, 'name', '') == 'Charlotte Linlin':
        linlin_cards.append(player.leader)
    if not linlin_cards:
        return True
    options = [{
        "id": str(i),
        "label": f"{c.name} ({c.id})",
        "card_id": c.id,
        "card_name": c.name,
    } for i, c in enumerate(linlin_cards)]
    linlin_snap = list(linlin_cards)

    def op03_117_napoleon_cb(selected: list) -> None:
        target_idx = int(selected[0]) if selected else -1
        if 0 <= target_idx < len(linlin_snap):
            target = linlin_snap[target_idx]
            target.power_modifier = getattr(target, 'power_modifier', 0) + 1000
            target._sticky_power_modifier = getattr(target, '_sticky_power_modifier', 0) + 1000
            target.power_modifier_expires_on_turn = game_state.turn_count + 1
            target._sticky_power_modifier_expires_on_turn = game_state.turn_count + 1
            game_state._log(f"{target.name} gets +1000 power until end of your next turn")

    game_state.pending_choice = PendingChoice(
        choice_id=f"op03_117_{_uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Napoleon: Optionally choose 1 Charlotte Linlin to give +1000 power until end of your next turn",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=op03_117_napoleon_cb,
    )
    return True


@register_effect("OP03-117", "trigger", "[Trigger] Play this card")
def op03_117_napoleon_trigger(game_state, player, card):
    """Trigger: Play this card."""
    player.cards_in_play.append(card)
    return True


# --- OP03-122: Sogeking ---
@register_effect("OP03-122", "on_play", "[On Play] Return cost 6 or less to hand, draw 2 trash 2")
def op03_122_sogeking(game_state, player, card):
    """On Play: Return cost 6 or less Character to hand FIRST, then draw 2 and trash 2."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    card.alt_name = 'Usopp'
    opponent = get_opponent(game_state, player)
    all_chars = list(player.cards_in_play) + list(opponent.cards_in_play)
    targets = [c for c in all_chars if (getattr(c, 'cost', 0) or 0) <= 6 and c != card]
    if targets:
        options = [{
            "id": str(i),
            "label": f"{c.name} (Cost: {c.cost or 0})",
            "card_id": c.id,
            "card_name": c.name,
        } for i, c in enumerate(targets)]
        targets_snap = list(targets)
        opponent_ref = opponent

        def _sogeking_trash_two(player_hand_snap: list) -> None:
            """Create a choice to trash 2 cards from hand (with snapshot)."""
            import uuid as _uuid2
            from ...game_engine import PendingChoice as PC
            if not player.hand:
                return
            h_snap = list(player.hand)
            def sogeking_trash_cb(sel2: list) -> None:
                for idx in sorted([int(s) for s in sel2], reverse=True):
                    if 0 <= idx < len(h_snap):
                        target = h_snap[idx]
                        if target in player.hand:
                            player.hand.remove(target)
                            player.trash.append(target)
                            game_state._log(f"{player.name} trashed {target.name} from hand")
                # After trashing, optionally return cost 6 or less
                all_chars = [c for c in player.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 6]
                all_chars.extend([c for c in opponent_ref.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 6])
                if all_chars:
                    create_return_to_hand_choice(
                        game_state, player, all_chars, source_card=None,
                        prompt="Sogeking: Choose a cost 6 or less Character to return to hand",
                        optional=True
                    )
            opts2 = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})",
                      "card_id": c.id, "card_name": c.name}
                     for i, c in enumerate(h_snap)]
            game_state.pending_choice = PC(
                choice_id=f"op03_122_trash_{_uuid2.uuid4().hex[:8]}",
                choice_type="select_cards",
                prompt="Sogeking: Choose 2 cards to trash from hand",
                options=opts2,
                min_selections=min(2, len(h_snap)),
                max_selections=min(2, len(h_snap)),
                callback=sogeking_trash_cb,
            )

        def op03_122_return_cb(selected: list) -> None:
            target_idx = int(selected[0]) if selected else -1
            if 0 <= target_idx < len(targets_snap):
                target = targets_snap[target_idx]
                for p in [player, opponent_ref]:
                    if target in p.cards_in_play:
                        p.cards_in_play.remove(target)
                        player.hand.append(target)
                        game_state._log(f"{target.name} was returned to {player.name}'s hand")
                        break
            draw_cards(player, 2)
            _sogeking_trash_two(list(player.hand))

        game_state.pending_choice = PendingChoice(
            choice_id=f"op03_122_{_uuid.uuid4().hex[:8]}",
            choice_type="select_target",
            prompt="Sogeking: Choose a cost 6 or less Character to return to hand (then draw 2 and trash 2)",
            options=options,
            min_selections=1,
            max_selections=1,
            source_card_id=card.id,
            source_card_name=card.name,
            callback=op03_122_return_cb,
        )
        return True
    # No return targets — just draw 2 and trash 2
    from ...game_engine import PendingChoice
    import uuid as _uuid
    draw_cards(player, 2)
    if player.hand:
        hand_snap = list(player.hand)
        def sogeking_direct_trash_cb(selected: list) -> None:
            for idx in sorted([int(s) for s in selected], reverse=True):
                if 0 <= idx < len(hand_snap):
                    target = hand_snap[idx]
                    if target in player.hand:
                        player.hand.remove(target)
                        player.trash.append(target)
                        game_state._log(f"{player.name} trashed {target.name} from hand")
        options2 = [{
            "id": str(i),
            "label": f"{c.name} (Cost: {c.cost or 0})",
            "card_id": c.id,
            "card_name": c.name,
        } for i, c in enumerate(hand_snap)]
        game_state.pending_choice = PendingChoice(
            choice_id=f"op03_122_{_uuid.uuid4().hex[:8]}",
            choice_type="select_cards",
            prompt="Sogeking: Choose 2 cards to trash from hand",
            options=options2,
            min_selections=min(2, len(hand_snap)),
            max_selections=min(2, len(hand_snap)),
            source_card_id=card.id,
            source_card_name=card.name,
            callback=sogeking_direct_trash_cb,
        )
    return True


# --- OP03-123: Charlotte Katakuri ---
@register_effect("OP03-123", "on_play", "[On Play] Add cost 8 or less Character to top/bottom of Life")
def op03_123_katakuri(game_state, player, card):
    """On Play: Add cost 8 or less Character to top or bottom of owner's Life face-up."""
    opponent = get_opponent(game_state, player)
    all_chars = list(player.cards_in_play) + list(opponent.cards_in_play)
    targets = [c for c in all_chars if (getattr(c, 'cost', 0) or 0) <= 8 and c != card]
    if targets:
        targets_snap = list(targets)
        def op03_123_katakuri_cb(selected: list) -> None:
            target_idx = int(selected[0]) if selected else -1
            if 0 <= target_idx < len(targets_snap):
                target = targets_snap[target_idx]
                for p in [player, opponent]:
                    if target in p.cards_in_play:
                        p.cards_in_play.remove(target)
                        p.life_cards.append(target)
                        game_state._log(f"{target.name} was added to {p.name}'s Life")
                        return
        return create_add_to_life_choice(game_state, player, targets, source_card=card,
                                        prompt="Choose cost 8 or less Character to add to Life",
                                        callback=op03_123_katakuri_cb)
    return True


# =============================================================================
# MISSING OP03 CARDS — NEW IMPLEMENTATIONS
# =============================================================================

# --- OP03-033: Hatchan ---
@register_effect("OP03-033", "trigger", "[Trigger] If East Blue Leader, play this card")
def op03_033_hatchan_trigger(game_state, player, card):
    """Trigger: If Leader is East Blue, play this card."""
    if player.leader and 'East Blue' in (player.leader.card_origin or ''):
        player.cards_in_play.append(card)
    return True


# --- OP03-100: Kingbaum ---
@register_effect("OP03-100", "trigger", "[Trigger] Trash 1 Life (top or bottom): Play this card")
def op03_100_kingbaum_trigger(game_state, player, card):
    """Trigger: Choose to trash top or bottom Life card to play this card."""
    if not player.life_cards:
        return True
    from ...game_engine import PendingChoice
    import uuid as _uuid
    card_snap = card

    def op03_100_kingbaum_cb(selected: list) -> None:
        choice_pick = selected[0] if selected else None
        if player.life_cards:
            life_card = player.life_cards.pop() if choice_pick == "top" else player.life_cards.pop(0)
            player.trash.append(life_card)
            game_state._log(f"{player.name} trashed 1 Life card")
        card_found = False
        for zone in [player.trash, player.hand]:
            for c in zone[:]:
                if c is card_snap:
                    zone.remove(c)
                    player.cards_in_play.append(c)
                    game_state._log(f"{player.name} played {c.name}")
                    card_found = True
                    break
            if card_found:
                break

    game_state.pending_choice = PendingChoice(
        choice_id=f"op03_100_{_uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Kingbaum: Choose which Life card to trash to play this card",
        options=[
            {"id": "top", "label": "Top of Life", "card_id": card.id, "card_name": card.name},
            {"id": "bottom", "label": "Bottom of Life", "card_id": card.id, "card_name": card.name},
        ],
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=op03_100_kingbaum_cb,
    )
    return True


# --- OP03-016: Flame Emperor ---
@register_effect("OP03-016", "on_play", "[Main] If Ace Leader, K.O. opponent's 8000+ power Character")
def op03_016_flame_emperor(game_state, player, card):
    """If Leader is Ace, K.O. up to 1 opponent's Character with 8000 or less power, then buff your Leader."""
    if not (player.leader and 'portgas.d.ace' in (player.leader.name or '').lower()):
        return True
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if (getattr(c, 'power', 0) or 0) + getattr(c, 'power_modifier', 0) <= 8000]
    from ...game_engine import PendingChoice
    import uuid as _uuid
    options = [{
        "id": str(i),
        "label": f"{target.name} (Power: {(target.power or 0) + getattr(target, 'power_modifier', 0)})",
        "card_id": target.id,
        "card_name": target.name,
    } for i, target in enumerate(targets)]
    if not targets:
        if player.leader:
            player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 3000
            player.leader._sticky_power_modifier = getattr(player.leader, '_sticky_power_modifier', 0) + 3000
            player.leader.has_doubleattack = True
            player.leader.has_double_attack = True
            player.leader._temp_doubleattack = True
        return True

    targets_snap = list(targets)

    def op03_016_flame_emperor_cb(selected: list) -> None:
        target_idx = int(selected[0]) if selected else -1
        opponent_ref = get_opponent(game_state, player)
        if 0 <= target_idx < len(targets_snap):
            target = targets_snap[target_idx]
            if target in opponent_ref.cards_in_play:
                opponent_ref.cards_in_play.remove(target)
                opponent_ref.trash.append(target)
                game_state._log(f"{target.name} was K.O.'d by Flame Emperor")
        if player.leader:
            player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 3000
            player.leader._sticky_power_modifier = getattr(player.leader, '_sticky_power_modifier', 0) + 3000
            player.leader.has_doubleattack = True
            player.leader.has_double_attack = True
            player.leader._temp_doubleattack = True
            game_state._log(f"{player.leader.name} gains +3000 power and [Double Attack] this turn")

    game_state.pending_choice = PendingChoice(
        choice_id=f"op03_016_{_uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Flame Emperor: Choose up to 1 opponent's 8000 power or less Character to K.O.",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=op03_016_flame_emperor_cb,
    )
    return True


# --- OP03-017: Cross Fire ---
@register_effect("OP03-017", "on_play", "[Main] If Whitebeard Pirates Leader, give opponent's card -2000 power")
def op03_017_cross_fire_main(game_state, player, card):
    """If Leader has Whitebeard Pirates, give opponent's Character -4000 power."""
    if not check_leader_type(player, "Whitebeard Pirates"):
        return True
    opponent = get_opponent(game_state, player)
    targets = list(opponent.cards_in_play)
    if targets:
        return create_power_effect_choice(game_state, player, targets, -4000, source_card=card,
                                         prompt="Cross Fire: Choose opponent's Character to give -4000 power")
    return True


@register_effect("OP03-017", "counter", "[Counter] If Whitebeard Pirates Leader, give opponent's card -2000 power")
def op03_017_cross_fire_counter(game_state, player, card):
    """Counter: If Leader has Whitebeard Pirates, give opponent's Leader/Character -4000 power."""
    if not check_leader_type(player, "Whitebeard Pirates"):
        return True
    opponent = get_opponent(game_state, player)
    targets = list(opponent.cards_in_play)
    if opponent.leader:
        targets.append(opponent.leader)
    if targets:
        return create_power_effect_choice(game_state, player, targets, -4000, source_card=card,
                                         prompt="Cross Fire: Choose opponent's card to give -4000 power")
    return True


# --- OP03-018: Fire Fist ---
@register_effect("OP03-018", "on_play", "[Main] Trash 1 Event from hand: K.O. opponent's 5000 power or less")
def op03_018_fire_fist(game_state, player, card):
    """Trash 1 Event from hand to K.O. opponent's 5000 power or less Character."""
    events_in_hand = [c for c in player.hand
                      if getattr(c, 'card_type', '') == 'EVENT']
    if not events_in_hand:
        return True
    # First, player chooses which Event to trash
    events_snap = list(events_in_hand)

    def op03_018_fire_fist_cb(selected: list) -> None:
        for idx in sorted([int(s) for s in selected], reverse=True):
            if 0 <= idx < len(events_snap):
                target = events_snap[idx]
                if target in player.hand:
                    player.hand.remove(target)
                    player.trash.append(target)
                    game_state._log(f"{player.name} trashed {target.name}")
        opponent_ref = get_opponent(game_state, player)
        targets5 = [c for c in opponent_ref.cards_in_play
                    if (getattr(c, 'power', 0) or 0) + getattr(c, 'power_modifier', 0) <= 5000]
        if targets5:
            t5_snap = list(targets5)
            def after_ko5_cb(sel2: list) -> None:
                target_idx = int(sel2[0]) if sel2 else -1
                if 0 <= target_idx < len(t5_snap):
                    target = t5_snap[target_idx]
                    if target in opponent_ref.cards_in_play:
                        opponent_ref.cards_in_play.remove(target)
                        opponent_ref.trash.append(target)
                        game_state._log(f"{target.name} was K.O.'d by Fire Fist (5000 or less)")
                remaining4 = [c for c in opponent_ref.cards_in_play
                              if (getattr(c, 'power', 0) or 0) + getattr(c, 'power_modifier', 0) <= 4000]
                if remaining4:
                    create_ko_choice(game_state, player, remaining4, source_card=None,
                                     prompt="Fire Fist: Choose opponent's 4000 power or less Character to K.O.")
            create_ko_choice(game_state, player, t5_snap, source_card=None,
                             callback=after_ko5_cb,
                             prompt="Fire Fist: Choose opponent's 5000 power or less Character to K.O.")
        else:
            targets4 = [c for c in opponent_ref.cards_in_play
                        if (getattr(c, 'power', 0) or 0) + getattr(c, 'power_modifier', 0) <= 4000]
            if targets4:
                create_ko_choice(game_state, player, targets4, source_card=None,
                                 prompt="Fire Fist: Choose opponent's 4000 power or less Character to K.O.")

    return create_hand_discard_choice(game_state, player, events_snap, source_card=card,
                                      callback=op03_018_fire_fist_cb,
                                      prompt="Fire Fist: Choose an Event to trash to K.O. opponent's 5000 power or less")


# --- OP03-019: Fiery Doll ---
@register_effect("OP03-019", "on_play", "[Main] Your Leader gains +4000 power during this turn")
def op03_019_fiery_doll(game_state, player, card):
    """Your Leader gains +4000 power during this turn."""
    if player.leader:
        player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 4000
        player.leader._sticky_power_modifier = getattr(player.leader, '_sticky_power_modifier', 0) + 4000
    return True


# --- OP03-037: Tooth Attack ---
@register_effect("OP03-037", "on_play", "[Main] Rest East Blue Character (chosen): K.O. rested cost 4 or less")
def op03_037_tooth_attack(game_state, player, card):
    """Rest a chosen East Blue Character to K.O. opponent's rested cost 4 or less."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    east_blue = [c for c in player.cards_in_play
                 if 'East Blue' in (c.card_origin or '') and not c.is_resting]
    if not east_blue:
        return True
    opponent = get_opponent(game_state, player)
    rested_targets = [c for c in opponent.cards_in_play
                      if (getattr(c, 'cost', 0) or 0) <= 4 and getattr(c, 'is_resting', False)]
    if not rested_targets:
        return True
    options = [{
        "id": str(i),
        "label": f"{c.name} (Cost: {c.cost or 0})",
        "card_id": c.id,
        "card_name": c.name,
    } for i, c in enumerate(east_blue)]
    eb_snap = list(east_blue)

    def op03_037_tooth_attack_cb(selected: list) -> None:
        target_idx = int(selected[0]) if selected else -1
        if 0 <= target_idx < len(eb_snap):
            target = eb_snap[target_idx]
            target.is_resting = True
            game_state._log(f"{target.name} was rested")
        opponent_ref = get_opponent(game_state, player)
        ko_targets = [c for c in opponent_ref.cards_in_play
                      if (getattr(c, 'cost', 0) or 0) <= 4 and getattr(c, 'is_resting', False)]
        if ko_targets:
            create_ko_choice(game_state, player, ko_targets, source_card=None,
                             prompt="Tooth Attack: Choose opponent's rested cost 4 or less Character to K.O.")

    game_state.pending_choice = PendingChoice(
        choice_id=f"op03_037_{_uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Tooth Attack: Choose which East Blue Character to rest (then K.O. opponent's rested cost 4 or less)",
        options=options,
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=op03_037_tooth_attack_cb,
    )
    return True


# --- OP03-038: Deathly Poison Gas Bomb MH5 ---
@register_effect("OP03-038", "on_play", "[Main] Rest up to 2 opponent's cost 2 or less Characters")
def op03_038_mh5(game_state, player, card):
    """Rest up to 2 of opponent's cost 2 or less Characters."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if (getattr(c, 'cost', 0) or 0) <= 2 and not getattr(c, 'is_resting', False)]
    if targets:
        return create_rest_choice(game_state, player, targets, source_card=card,
                                 prompt="MH5: Choose up to 2 opponent's cost 2 or less to rest",
                                 min_selections=0, max_selections=2)
    return True


# --- OP03-039: One, Two, Jango ---
@register_effect("OP03-039", "on_play", "[Main] Rest opponent's cost 1 or less, set 1 of your Characters active")
def op03_039_one_two_jango(game_state, player, card):
    """Rest up to 1 opponent's cost 1 or less Character, then give +1000 power to your Leader or Character."""
    opponent = get_opponent(game_state, player)
    opp_targets = [c for c in opponent.cards_in_play
                   if (getattr(c, 'cost', 0) or 0) <= 1 and not getattr(c, 'is_resting', False)]
    if not opp_targets:
        own_chars = list(player.cards_in_play)
        if own_chars:
            return create_power_effect_choice(
                game_state, player, own_chars, 1000, source_card=card,
                prompt="One, Two, Jango: Choose up to 1 of your Characters to give +1000 power",
                min_selections=0, max_selections=1
            )
        return True
    opp_snap = list(opp_targets)

    def op03_039_jango_cb(selected: list) -> None:
        for sel in selected:
            target_idx = int(sel)
            if 0 <= target_idx < len(opp_snap):
                opp_snap[target_idx].is_resting = True
                game_state._log(f"{opp_snap[target_idx].name} was rested")
        own_chars = list(player.cards_in_play)
        if player.leader:
            own_chars.append(player.leader)
        if own_chars:
            create_power_effect_choice(game_state, player, own_chars, 1000, source_card=None,
                                       prompt="One, Two, Jango: Choose 1 of your cards to give +1000 power",
                                       min_selections=0, max_selections=1)

    return create_target_choice(
        game_state, player, opp_targets, source_card=card,
        prompt="One, Two, Jango: Choose up to 1 opponent's cost 1 or less Character to rest",
        min_selections=0, max_selections=1,
        callback=op03_039_jango_cb,
    )


# --- OP03-054: Usopp's Rubber Band of Doom!!! ---
@register_effect("OP03-054", "counter", "[Counter] +2000 power, trash 1 card from top of deck")
def op03_054_rubber_band(game_state, player, card):
    """Counter: Give Leader or Character +2000 power. Trash 1 from top of deck."""
    from ...game_engine import PendingChoice
    import uuid as _uuid

    targets = list(player.cards_in_play)
    if player.leader:
        targets.append(player.leader)
    options = [{
        "id": str(i),
        "label": f"{target.name} (Power: {target.power or 0})",
        "card_id": target.id,
        "card_name": target.name,
    } for i, target in enumerate(targets)]
    targets_snap = list(targets)

    def op03_054_rubber_band_cb(selected: list) -> None:
        import uuid as _uuid2
        from ...game_engine import PendingChoice as PC
        target_idx = int(selected[0]) if selected else -1
        if 0 <= target_idx < len(targets_snap):
            target = targets_snap[target_idx]
            target.power_modifier = getattr(target, 'power_modifier', 0) + 2000
            target._sticky_power_modifier = getattr(target, '_sticky_power_modifier', 0) + 2000
            game_state._log(f"{target.name} gets +2000 power")
        def rubber_band_opt_trash_cb(sel2: list) -> None:
            if "yes" in sel2:
                if player.deck:
                    player.trash.append(player.deck.pop(0))
                game_state._log(f"{player.name} trashed 1 card from top of deck")

        game_state.pending_choice = PC(
            choice_id=f"op03_054_trash_{_uuid2.uuid4().hex[:8]}",
            choice_type="yes_no",
            prompt="Usopp's Rubber Band of Doom!!!: Trash 1 card from the top of your deck?",
            options=[
                {"id": "yes", "label": "Yes", "card_id": "op03_054", "card_name": "Usopp's Rubber Band of Doom!!!"},
                {"id": "no", "label": "No", "card_id": "op03_054", "card_name": "Usopp's Rubber Band of Doom!!!"},
            ],
            min_selections=1,
            max_selections=1,
            callback=rubber_band_opt_trash_cb,
        )

    game_state.pending_choice = PendingChoice(
        choice_id=f"op03_054_{_uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Usopp's Rubber Band of Doom!!!: Choose your Leader or Character to give +2000 power",
        options=options,
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=op03_054_rubber_band_cb,
    )
    return True


# --- OP03-055: Gum-Gum Giant Gavel ---
@register_effect("OP03-055", "counter", "[Counter] Trash 1 from hand: Leader +4000 power, may trash 2 from deck")
def op03_055_gum_gum_gavel(game_state, player, card):
    """Counter: Trash 1 from hand to give Leader +4000 power, then may trash 2 from top of deck."""
    from ...game_engine import PendingChoice
    import uuid as _uuid
    if player.hand and player.leader:
        trash_from_hand(player, 1, game_state, card)
        add_power_modifier(player.leader, 4000)
        def gavel_opt_trash_cb(selected: list) -> None:
            if "yes" in selected:
                for _ in range(min(2, len(player.deck))):
                    if player.deck:
                        player.trash.append(player.deck.pop(0))
                game_state._log(f"{player.name} trashed 2 card(s) from top of deck")

        game_state.pending_choice = PendingChoice(
            choice_id=f"op03_055_{_uuid.uuid4().hex[:8]}",
            choice_type="yes_no",
            prompt="Gum-Gum Giant Gavel: Trash 2 cards from the top of your deck?",
            options=[
                {"id": "yes", "label": "Yes", "card_id": card.id, "card_name": card.name},
                {"id": "no", "label": "No", "card_id": card.id, "card_name": card.name},
            ],
            min_selections=1,
            max_selections=1,
            source_card_id=card.id,
            source_card_name=card.name,
            callback=gavel_opt_trash_cb,
        )
    return True


# --- OP03-056: Sanji's Pilaf ---
@register_effect("OP03-056", "on_play", "[Main] Draw 2 cards")
def op03_056_sanjis_pilaf(game_state, player, card):
    """Draw 2 cards."""
    draw_cards(player, 2)
    return True


# --- OP03-057: Three Thousand Worlds ---
@register_effect("OP03-057", "on_play", "[Main] Place cost 5 or less Character at bottom of deck")
def op03_057_three_thousand_worlds(game_state, player, card):
    """Place up to 1 Character with cost 5 or less at the bottom of the owner's deck."""
    opponent = get_opponent(game_state, player)
    all_chars = list(player.cards_in_play) + list(opponent.cards_in_play)
    targets = [c for c in all_chars if (getattr(c, 'cost', 0) or 0) <= 5]
    if targets:
        return create_bottom_deck_choice(game_state, player, targets, source_card=card,
                                        prompt="Three Thousand Worlds: Choose cost 5 or less Character to place at bottom of deck")
    return True


# --- OP03-072: Gum-Gum Jet Gatling ---
@register_effect("OP03-072", "counter", "[Counter] Trash 1 from hand: +3000 power")
def op03_072_jet_gatling(game_state, player, card):
    """Counter: Trash 1 from hand to give +3000 power."""
    if player.hand and player.leader:
        trash_from_hand(player, 1, game_state, card)
        add_power_modifier(player.leader, 3000)
    return True


# --- OP03-073: Hull Dismantler Slash ---
@register_effect("OP03-073", "on_play", "[Main] DON!! -1: Draw 1 card")
def op03_073_hull_dismantler(game_state, player, card):
    """Return 1 DON to draw 1 card."""
    def _hull_dismantler_cb():
        draw_cards(player, 1)
        game_state._log(f"  Hull Dismantler Slash: Draw 1")
        opponent = get_opponent(game_state, player)
        ko_targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
        if ko_targets:
            create_ko_choice(game_state, player, ko_targets, source_card=None,
                             prompt="Hull Dismantler Slash: Choose opponent's cost 2 or less Character to K.O.")

    result = optional_don_return(game_state, player, 1, source_card=card, post_callback=_hull_dismantler_cb)
    if not result:
        return True  # Pending choice
    return True


# --- OP03-075: Galley-La Company ---
@register_effect("OP03-075", "activate", "[Activate: Main] Rest this Stage: If Iceburg Leader, add 1 DON")
def op03_075_galley_la(game_state, player, card):
    """Rest this Stage: If Iceburg Leader, add 1 DON from DON deck."""
    if card.is_resting:
        return False
    if not (player.leader and 'iceburg' in (player.leader.name or '').lower()):
        return False
    card.is_resting = True
    add_don_from_deck(player, 1)  # rested by default
    return True


# --- OP03-095: Soap Sheep ---
@register_effect("OP03-095", "on_play", "[Main] Give up to 2 opponent's Characters -2 cost")
def op03_095_soap_sheep(game_state, player, card):
    """Give up to 2 of opponent's Characters -2 cost during this turn."""
    opponent = get_opponent(game_state, player)
    if opponent.cards_in_play:
        return create_cost_reduction_choice(game_state, player, list(opponent.cards_in_play), -2,
                                           source_card=card,
                                           prompt="Soap Sheep: Choose up to 2 opponent's Characters to give -2 cost",
                                           max_selections=2)
    return True


# --- OP03-096: Tempest Kick Sky Slicer ---
@register_effect("OP03-096", "on_play", "[Main] K.O. opponent's cost 0 Character or Stage")
def op03_096_tempest_kick(game_state, player, card):
    """K.O. opponent's Character with cost 0 or a Stage."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 0
               or getattr(c, 'card_type', '') == 'STAGE']
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                               prompt="Tempest Kick: Choose opponent's cost 0 Character or Stage to K.O.")
    return True


# --- OP03-097: Six King Pistol ---
@register_effect("OP03-097", "counter", "[Counter] Trash 1 from hand: +3000 power")
def op03_097_six_king_pistol(game_state, player, card):
    """Counter: Trash 1 from hand to give +3000 power."""
    if player.hand and player.leader:
        trash_from_hand(player, 1, game_state, card)
        add_power_modifier(player.leader, 3000)
    return True


# --- OP03-098: Enies Lobby ---
@register_effect("OP03-098", "activate", "[Activate: Main] Rest: If CP Leader, give opponent's Character -2 cost")
def op03_098_enies_lobby(game_state, player, card):
    """Rest this Stage: If CP Leader, give opponent's Character -2 cost."""
    if card.is_resting:
        return False
    if not check_leader_type(player, "CP"):
        return False
    card.is_resting = True
    opponent = get_opponent(game_state, player)
    if opponent.cards_in_play:
        return create_cost_reduction_choice(game_state, player, list(opponent.cards_in_play), -2,
                                           source_card=card,
                                           prompt="Enies Lobby: Choose opponent's Character to give -2 cost")
    return True


# --- OP03-118: Ikoku Sovereignty ---
@register_effect("OP03-118", "counter", "[Counter] +5000 power")
def op03_118_ikoku(game_state, player, card):
    """Counter: Give your Leader or Character +5000 power."""
    if player.leader:
        add_power_modifier(player.leader, 5000)
    return True


# --- OP03-119: Buzz Cut Mochi ---
@register_effect("OP03-119", "on_play", "[Main] If you have fewer Life than opponent, K.O. opponent's cost 6 or less")
def op03_119_buzz_cut_mochi(game_state, player, card):
    """If you have fewer Life than opponent, K.O. opponent's cost 6 or less Character."""
    opponent = get_opponent(game_state, player)
    if len(player.life_cards) >= len(opponent.life_cards):
        return True
    targets = [c for c in opponent.cards_in_play
               if (getattr(c, 'cost', 0) or 0) <= 4]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                               prompt="Buzz Cut Mochi: Choose opponent's cost 4 or less Character to K.O.")
    return True


# --- OP03-120: Tropical Torment ---
@register_effect("OP03-120", "on_play", "[Main] If opponent has 4+ Life, trash 1 of opponent's Life")
def op03_120_tropical_torment(game_state, player, card):
    """If opponent has 4 or more Life cards, trash 1 of opponent's Life."""
    opponent = get_opponent(game_state, player)
    if len(opponent.life_cards) >= 4 and opponent.life_cards:
        opponent.trash.append(opponent.life_cards.pop())
    return True


# --- OP03-121: Thunder Bolt ---
@register_effect("OP03-121", "on_play", "[Main] Trash 1 of your Life: K.O. opponent's cost 5 or less")
def op03_121_thunder_bolt(game_state, player, card):
    """Trash 1 of your Life cards to K.O. opponent's cost 5 or less Character."""
    if not player.life_cards:
        return True
    player.trash.append(player.life_cards.pop())
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if (getattr(c, 'cost', 0) or 0) <= 5]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                               prompt="Thunder Bolt: Choose opponent's cost 5 or less Character to K.O.")
    return True

