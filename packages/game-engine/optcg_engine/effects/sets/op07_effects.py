"""
Hardcoded effects for OP07 cards — 500 Years in the Future.
"""

from ..effect_registry import (
    add_don_from_deck, add_power_modifier, check_leader_type, check_life_count,
    check_trash_count, create_bottom_deck_choice, create_cannot_attack_choice,
    create_cost_reduction_choice, create_don_assignment_choice, create_ko_choice,
    create_own_character_choice, create_play_from_hand_choice, create_play_from_trash_choice,
    create_power_effect_choice, create_rest_choice, create_return_to_hand_choice,
    create_set_active_choice, create_target_choice, create_trash_choice,
    draw_cards, get_opponent, optional_don_return, _player_index, _remove_card_instance,
    register_effect, reorder_top_cards, return_don_to_deck, search_top_cards, trash_from_hand,
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
        player.cards_in_play.append(card)
        game_state._apply_keywords(card)
        game_state._log(f"{player.name} played {card.name} from Trigger")
    return True


def _bottom_cards_from_hand(game_state, player, count, source_card, prompt):
    from ...game_engine import PendingChoice
    import uuid as _uuid
    if len(player.hand) <= count:
        moved = list(player.hand)
        player.hand.clear()
        player.deck.extend(moved)
        for moved_card in moved:
            game_state._log(f"{moved_card.name} was placed at the bottom of deck")
        return True
    snapshot = list(player.hand)

    def _bottom_cb(selected):
        indices = sorted([int(s) for s in selected], reverse=True)
        for idx in indices:
            if 0 <= idx < len(player.hand):
                moved_card = player.hand.pop(idx)
                player.deck.append(moved_card)
                game_state._log(f"{moved_card.name} was placed at the bottom of deck")

    game_state.pending_choice = PendingChoice(
        choice_id=f"op07_bottom_hand_{_uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt=prompt,
        options=[{
            "id": str(i),
            "label": f"{c.name} (Cost: {getattr(c, 'cost', 0) or 0})",
            "card_id": c.id,
            "card_name": c.name,
        } for i, c in enumerate(snapshot)],
        min_selections=count,
        max_selections=count,
        source_card_id=source_card.id if source_card else None,
        source_card_name=source_card.name if source_card else None,
        callback=_bottom_cb,
    )
    return True


# =============================================================================
# LEADER EFFECTS
# =============================================================================

# --- OP07-001: Monkey.D.Dragon (Leader) ---
@register_effect("OP07-001", "activate", "[Activate: Main] [Once Per Turn] Give up to 2 attached DON to 1 Character")
def op07_001_dragon_leader(game_state, player, card):
    """Once Per Turn: Give up to 2 of your currently attached DON to 1 of your Characters."""
    if getattr(card, 'op07_001_used', False):
        return False
    # Find cards with attached DON
    cards_with_don = [c for c in [player.leader] + list(player.cards_in_play)
                      if getattr(c, 'attached_don', 0) > 0 and c is not card]
    if cards_with_don and player.cards_in_play:
        source = cards_with_don[0]
        transfer = min(2, getattr(source, 'attached_don', 0))
        if transfer > 0:
            source.attached_don = getattr(source, 'attached_don', 0) - transfer
            card.op07_001_used = True
            return create_don_assignment_choice(game_state, player, list(player.cards_in_play),
                                                transfer, source_card=card, rested_only=False,
                                                prompt="Choose a Character to give DON")
    card.op07_001_used = True
    return False


# --- OP07-019: Jewelry Bonney (Leader) ---
@register_effect("OP07-019", "on_opponent_attack", "[On Opponent's Attack] [Once Per Turn] Rest 1 DON: Rest opponent cost 5 or less")
def op07_019_bonney_leader(game_state, player, card):
    """Once Per Turn, Rest 1 DON: Rest opponent's cost 5 or less Character."""
    if getattr(card, 'op07_019_used', False):
        return False
    active_count = player.don_pool.count('active')
    if active_count >= 1:
        # Rest 1 active DON
        for i in range(len(player.don_pool)):
            if player.don_pool[i] == 'active':
                player.don_pool[i] = 'rested'
                break
        card.op07_019_used = True
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 5]
        if targets:
            return create_rest_choice(game_state, player, targets, source_card=card,
                                      prompt="Choose opponent's cost 5 or less to rest")
        return True
    return False


# --- OP07-038: Boa Hancock (Leader) ---
@register_effect("OP07-038", "on_character_removed", "[Your Turn] [Once Per Turn] When char removed, if 5 or less hand, draw 1")
def op07_038_hancock_leader(game_state, player, card):
    """Your Turn, Once Per Turn: When a Character is removed by your effect, if 5 or less hand, draw 1."""
    if getattr(card, 'op07_038_used', False):
        return False
    if len(player.hand) <= 5:
        draw_cards(player, 1)
        card.op07_038_used = True
        return True
    return False


# --- OP07-059: Foxy (Leader) ---
@register_effect("OP07-059", "on_attack", "[When Attacking] DON -3: If 3+ Foxy Pirates, draw 2")
def op07_059_foxy_leader(game_state, player, card):
    """When Attacking, DON -3: If you have 3 or more Foxy Pirates Characters, draw 2 cards."""
    foxy_chars = [c for c in player.cards_in_play
                  if 'Foxy Pirates' in (c.card_origin or '')]
    if len(foxy_chars) < 3:
        return False

    def post_draw():
        draw_cards(player, 2)
        game_state._log("Foxy Leader: Drew 2 cards")

    auto = return_don_to_deck(game_state, player, 3, source_card=card, post_callback=post_draw)
    if auto:
        post_draw()
    return True


# --- OP07-079: Rob Lucci (Leader) ---
@register_effect("OP07-079", "on_attack", "[When Attacking] Trash 2 from deck: Opponent char -1 cost")
def op07_079_lucci_leader(game_state, player, card):
    """When Attacking: Trash 2 from top of deck, give opponent's Character -1 cost this turn."""
    for _ in range(min(2, len(player.deck))):
        if player.deck:
            trashed = player.deck.pop(0)
            player.trash.append(trashed)
    opponent = get_opponent(game_state, player)
    targets = list(opponent.cards_in_play)
    if targets:
        return create_cost_reduction_choice(game_state, player, targets, -1, source_card=card,
                                            prompt="Choose opponent's Character to give -1 cost this turn")
    return True


# --- OP07-097: Vegapunk (Leader) --- continuous
@register_effect("OP07-097", "continuous", "[Continuous] This Leader cannot attack")
def op07_097_vegapunk_continuous(game_state, player, card):
    """Continuous: This Leader cannot attack."""
    card.cannot_attack = True
    return True


# --- OP07-097: Vegapunk (Leader) --- activate
@register_effect("OP07-097", "activate", "[Activate: Main] [Once Per Turn] Rest 1 DON: Play/return Egghead cost 5 or less from hand")
def op07_097_vegapunk_activate(game_state, player, card):
    """Once Per Turn, Rest 1 DON: Play Egghead cost 5 or less from hand, or return Egghead cost 5 or less to hand."""
    if getattr(card, 'op07_097_used', False):
        return False
    active_count = player.don_pool.count('active')
    if active_count >= 1:
        # Rest 1 active DON
        for i in range(len(player.don_pool)):
            if player.don_pool[i] == 'active':
                player.don_pool[i] = 'rested'
                break
        egghead = [c for c in player.hand
                   if 'Egghead' in (getattr(c, 'card_origin', '') or '')
                   and (getattr(c, 'cost', 0) or 0) <= 5]
        card.op07_097_used = True
        if egghead:
            return create_play_from_hand_choice(game_state, player, egghead, source_card=card,
                                                prompt="Choose Egghead cost 5 or less to play from hand")
        return True
    return False


# =============================================================================
# OP07 — RED CHARACTER EFFECTS
# =============================================================================

# --- OP07-002: Ain ---
@register_effect("OP07-002", "on_play", "[On Play] Set opponent's Character power to 0 this turn")
def op07_002_ain(game_state, player, card):
    """On Play: Set up to 1 opponent's Character power to 0 this turn."""
    opponent = get_opponent(game_state, player)
    targets = list(opponent.cards_in_play)
    if not targets:
        return True

    snapshot = targets
    def zero_power_cb(selected):
        idx = int(selected[0]) if selected else -1
        if 0 <= idx < len(snapshot):
            t = snapshot[idx]
            current = (getattr(t, 'power', 0) or 0) + (getattr(t, 'power_modifier', 0) or 0)
            # Apply a negative modifier to bring effective power to 0
            add_power_modifier(t, -current)
            game_state._log(f"{t.name} power set to 0 this turn")

    return create_target_choice(game_state, player, targets,
                                prompt="Choose opponent's Character to set power to 0 this turn",
                                source_card=card, min_selections=0, max_selections=1,
                                callback=zero_power_cb)


# --- OP07-003: Outlook III ---
@register_effect("OP07-003", "activate", "[Activate: Main] Trash this: Give -2000 to up to 2 opponents")
def op07_003_outlook(game_state, player, card):
    """Activate: Trash this to give -2000 to up to 2 opponent's Characters."""
    if card not in player.cards_in_play:
        return False
    player.cards_in_play.remove(card)
    player.trash.append(card)
    opponent = get_opponent(game_state, player)
    targets = list(opponent.cards_in_play)
    if targets:
        return create_power_effect_choice(game_state, player, targets, -2000,
                                          source_card=card,
                                          prompt="Choose up to 2 opponent Characters for -2000 power",
                                          min_selections=0, max_selections=2)
    return True


# --- OP07-004: Curly.Dadan ---
@register_effect("OP07-004", "on_play", "[On Play] May trash 1 from hand: Look at top 5, add Character 2000 power or less")
def op07_004_dadan(game_state, player, card):
    """On Play: May trash 1 from hand, look at top 5 and add Character 2000 power or less."""
    if not player.hand:
        return True

    from ...game_engine import PendingChoice
    import uuid

    hand_opts = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})",
                  "card_id": c.id, "card_name": c.name} for i, c in enumerate(player.hand)]

    def trash_cb(selected):
        if selected:
            idx = int(selected[0])
            if 0 <= idx < len(player.hand):
                c = player.hand.pop(idx)
                player.trash.append(c)
                game_state._log(f"{player.name} trashed {c.name} for Dadan's effect")
        # Regardless, search top 5
        search_top_cards(
            game_state, player, look_count=5, add_count=1,
            filter_fn=lambda c: getattr(c, 'card_type', '') == 'CHARACTER'
                                and (getattr(c, 'power', 0) or 0) <= 2000,
            source_card=card,
            prompt="Look at top 5: choose up to 1 Character with 2000 power or less to add to hand"
        )

    game_state.pending_choice = PendingChoice(
        choice_id=f"trash_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="May trash 1 card from hand for Curly.Dadan's effect (select 0 to skip)",
        options=hand_opts,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=trash_cb,
        callback_action="trash_from_hand",
        callback_data={"player_id": player.player_id, "count": 1}
    )
    return True


# --- OP07-005: Carina ---
@register_effect("OP07-005", "blocker", "[Blocker]")
def op07_005_carina_blocker(game_state, player, card):
    card.has_blocker = True
    return True


@register_effect("OP07-005", "on_play", "[On Play] Give -2000 power to opponent's Character this turn")
def op07_005_carina_play(game_state, player, card):
    """On Play: Give up to 1 opponent's Character -2000 power this turn."""
    opponent = get_opponent(game_state, player)
    targets = list(opponent.cards_in_play)
    if targets:
        return create_power_effect_choice(game_state, player, targets, -2000,
                                          source_card=card,
                                          prompt="Choose opponent's Character for -2000 power this turn",
                                          min_selections=0, max_selections=1)
    return True


# --- OP07-006: Sterry ---
@register_effect("OP07-006", "on_play", "[On Play] May give active Leader -5000 power this turn: Draw 1, trash 1")
def op07_006_sterry(game_state, player, card):
    """On Play: You may give your 1 active Leader -5000 power this turn: Draw 1 and trash 1 from hand."""
    if not (player.leader and not getattr(player.leader, 'is_resting', False)):
        return True

    from ...game_engine import PendingChoice
    import uuid

    leader_ref = player.leader

    def sterry_cb(selected):
        choice = selected[0] if selected else 'no'
        if choice == 'yes':
            add_power_modifier(leader_ref, -5000)
            draw_cards(player, 1)
            if player.hand:
                trash_from_hand(player, 1, game_state, card)

    game_state.pending_choice = PendingChoice(
        choice_id=f"sterry_{uuid.uuid4().hex[:8]}",
        choice_type="yes_no",
        prompt="Give your active Leader -5000 power this turn to Draw 1 and trash 1?",
        options=[{"id": "yes", "label": "Yes"}, {"id": "no", "label": "No"}],
        min_selections=1, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=sterry_cb, callback_action="yes_no_choice",
        callback_data={"player_id": player.player_id}
    )
    return True


# --- OP07-008: Mr. Tanaka ---
@register_effect("OP07-008", "blocker", "[Blocker]")
def op07_008_tanaka_blocker(game_state, player, card):
    card.has_blocker = True
    return True


@register_effect("OP07-008", "trigger", "[Trigger] Play this card")
def op07_008_tanaka_trigger(game_state, player, card):
    """Trigger: Play this card."""
    player.cards_in_play.append(card)
    return True


# --- OP07-009: Dogura & Magura ---
@register_effect("OP07-009", "on_play", "[On Play] Give red cost 1 Character Double Attack this turn")
def op07_009_dogura_magura(game_state, player, card):
    """On Play: Up to 1 red cost 1 Character gains Double Attack this turn."""
    targets = [c for c in player.cards_in_play
               if 'Red' in (getattr(c, 'color', '') or getattr(c, 'colors', '') or '')
               and (getattr(c, 'cost', 0) or 0) == 1]
    if not targets:
        return True
    snapshot = list(targets)

    def give_double_attack(selected):
        idx = int(selected[0]) if selected else -1
        if 0 <= idx < len(snapshot):
            snapshot[idx].has_double_attack = True
            game_state._log(f"{snapshot[idx].name} gains Double Attack this turn")

    return create_target_choice(game_state, player, targets,
                                prompt="Choose your red cost 1 Character to give Double Attack",
                                source_card=card, min_selections=0, max_selections=1,
                                callback=give_double_attack)


# --- OP07-010: Baccarat ---
@register_effect("OP07-010", "blocker", "[Blocker]")
def op07_010_baccarat_blocker(game_state, player, card):
    card.has_blocker = True
    return True


@register_effect("OP07-010", "on_opponent_attack", "[On Opponent's Attack] [Once Per Turn] May trash 1: Leader or Character +2000 power this battle")
def op07_010_baccarat_attack(game_state, player, card):
    """On Opponent's Attack, Once Per Turn: Trash 1 for +2000 power to Leader or Character this battle."""
    if getattr(card, 'op07_010_used', False):
        return False
    if not player.hand:
        return False

    # Targets: leader + all characters
    targets = []
    if player.leader:
        targets.append(player.leader)
    targets.extend(player.cards_in_play)

    snap_targets = list(targets)

    def after_trash_cb():
        # Give +2000 to chosen target — create another choice
        def power_cb(selected):
            idx = int(selected[0]) if selected else -1
            if 0 <= idx < len(snap_targets):
                add_power_modifier(snap_targets[idx], 2000)
                game_state._log(f"{snap_targets[idx].name} gains +2000 power this battle")

        create_target_choice(game_state, player, snap_targets,
                             prompt="Choose your Leader or Character to give +2000 power this battle",
                             source_card=card, min_selections=1, max_selections=1,
                             callback=power_cb)

    card.op07_010_used = True
    # First: trash 1 from hand, then power up a target
    trash_from_hand(player, 1, game_state, card)
    # If pending choice was created (hand > 1), we need to chain; for now give +2000 to leader as fallback
    if game_state.pending_choice is not None:
        # Wrap the trash callback to chain the power choice
        original_cb = game_state.pending_choice.callback

        def chained_trash_cb(selected):
            if original_cb:
                original_cb(selected)
            elif selected:
                idx = int(selected[0]) if selected else -1
                if 0 <= idx < len(player.hand):
                    c = player.hand.pop(idx)
                    player.trash.append(c)
            after_trash_cb()

        game_state.pending_choice.callback = chained_trash_cb
    else:
        # Auto-trashed, now give power bonus
        after_trash_cb()
    return True


# --- OP07-011: Bluejam ---
@register_effect("OP07-011", "on_attack", "[DON!! x1] [When Attacking] K.O. opponent's Character with 2000 power or less")
def op07_011_bluejam(game_state, player, card):
    """When Attacking with DON x1: K.O. opponent's 2000 power or less."""
    if getattr(card, 'attached_don', 0) >= 1:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play
                   if (getattr(c, 'power', 0) or 0) + (getattr(c, 'power_modifier', 0) or 0) <= 2000]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                    prompt="Choose opponent's 2000 power or less Character to K.O.",
                                    min_selections=0, max_selections=1)
    return True


# --- OP07-012: Porchemy ---
@register_effect("OP07-012", "on_play", "[On Play] Give -1000 power to opponent's Character this turn")
def op07_012_porchemy(game_state, player, card):
    """On Play: Give up to 1 opponent's Character -1000 power this turn."""
    opponent = get_opponent(game_state, player)
    targets = list(opponent.cards_in_play)
    if targets:
        return create_power_effect_choice(game_state, player, targets, -1000,
                                          source_card=card,
                                          prompt="Choose opponent's Character for -1000 power this turn",
                                          min_selections=0, max_selections=1)
    return True


# --- OP07-013: Masked Deuce ---
@register_effect("OP07-013", "on_play", "[On Play] If Portgas.D.Ace leader, look at top 5, add Ace or red Event")
def op07_013_masked_deuce(game_state, player, card):
    """On Play: If Ace leader, look at top 5 and add Portgas.D.Ace or red Event."""
    if not (player.leader and getattr(player.leader, 'name', '') == 'Portgas.D.Ace'):
        return True

    def filter_fn(c):
        name = getattr(c, 'name', '')
        card_type = getattr(c, 'card_type', '')
        colors = getattr(c, 'color', '') or getattr(c, 'colors', '') or ''
        return name == 'Portgas.D.Ace' or (card_type == 'EVENT' and 'Red' in colors)

    return search_top_cards(game_state, player, look_count=5, add_count=1,
                            filter_fn=filter_fn, source_card=card,
                            prompt="Look at top 5: choose up to 1 Portgas.D.Ace or red Event to add to hand")


# --- OP07-014: Moda ---
@register_effect("OP07-014", "on_play", "[On Play] Up to 1 Portgas.D.Ace gains +2000 power this turn")
def op07_014_moda(game_state, player, card):
    """On Play: Give +2000 power to up to 1 Portgas.D.Ace card this turn."""
    # Check characters in play first
    for c in player.cards_in_play:
        if getattr(c, 'name', '') == 'Portgas.D.Ace':
            add_power_modifier(c, 2000)
            return True
    # Check leader
    if player.leader and getattr(player.leader, 'name', '') == 'Portgas.D.Ace':
        add_power_modifier(player.leader, 2000)
    return True


# --- OP07-015: Monkey.D.Dragon (Character) ---
@register_effect("OP07-015", "continuous", "[Rush] Can attack Characters on play turn")
def op07_015_dragon_rush(game_state, player, card):
    """Continuous: Rush — can attack Characters on play turn."""
    card.has_rush = True
    return True


@register_effect("OP07-015", "on_play", "[On Play] Give up to 2 rested DON to Leader or 1 Character")
def op07_015_dragon_play(game_state, player, card):
    """On Play: Give up to 2 rested DON to Leader or 1 Character."""
    rested_count = player.don_pool.count('rested')
    if rested_count <= 0:
        return True
    targets = []
    if player.leader:
        targets.append(player.leader)
    targets.extend(list(player.cards_in_play))
    targets = [t for t in targets if t is not None]
    if not targets:
        return True
    don_to_give = min(2, rested_count)
    return create_don_assignment_choice(game_state, player, targets, don_to_give,
                                        source_card=card, rested_only=True,
                                        prompt=f"Choose target to receive up to {don_to_give} rested DON")


# =============================================================================
# OP07 — GREEN CHARACTER EFFECTS
# =============================================================================

# --- OP07-020: Aladine ---
@register_effect("OP07-020", "blocker", "[Blocker]")
def op07_020_aladine_blocker(game_state, player, card):
    card.has_blocker = True
    return True


@register_effect("OP07-020", "on_ko", "[On K.O.] If Fish-Man leader, play Fish-Man/Merfolk cost 3 or less from hand")
def op07_020_aladine_ko(game_state, player, card):
    """On K.O.: If Fish-Man leader, play Fish-Man/Merfolk cost 3 or less from hand."""
    leader_origin = (getattr(player.leader, 'card_origin', '') or '') if player.leader else ''
    if 'Fish-Man' in leader_origin or 'Merfolk' in leader_origin:
        targets = [c for c in player.hand
                   if ('Fish-Man' in (c.card_origin or '') or 'Merfolk' in (c.card_origin or ''))
                   and (getattr(c, 'cost', 0) or 0) <= 3]
        if targets:
            return create_play_from_hand_choice(game_state, player, targets, source_card=card,
                                                prompt="Choose Fish-Man/Merfolk cost 3 or less to play from hand")
    return True


# --- OP07-021: Urouge ---
@register_effect("OP07-021", "blocker", "[Blocker]")
def op07_021_urouge_blocker(game_state, player, card):
    card.has_blocker = True
    return True


@register_effect("OP07-021", "end_of_turn", "[End of Your Turn] Set up to 1 DON active")
def op07_021_urouge_end(game_state, player, card):
    """End of Turn: Set up to 1 rested DON active."""
    for i, d in enumerate(player.don_pool):
        if d == 'rested':
            player.don_pool[i] = 'active'
            game_state._log("Urouge: Set 1 DON active")
            break
    return True


# --- OP07-022: Otama ---
@register_effect("OP07-022", "on_play", "[On Play] Look at top 5, add green Land of Wano card (not Otama)")
def op07_022_otama(game_state, player, card):
    """On Play: Look at top 5, reveal up to 1 green Land of Wano card (not Otama) to hand."""
    def is_green_wano(c):
        colors = getattr(c, 'color', '') or getattr(c, 'colors', '') or ''
        origin = c.card_origin or ''
        name = getattr(c, 'name', '')
        return ('Green' in colors) and 'Land of Wano' in origin and name != 'Otama'

    return search_top_cards(game_state, player, look_count=5, add_count=1,
                            filter_fn=is_green_wano, source_card=card,
                            prompt="Look at top 5: choose up to 1 green Land of Wano card (not Otama) to add to hand")


# --- OP07-023: Caribou ---
@register_effect("OP07-023", "continuous", "If 6+ rested DON, +1000 power")
def op07_023_caribou_power(game_state, player, card):
    """Continuous: If 6+ rested DON, +1000 power."""
    rested = player.don_pool.count('rested')
    if rested >= 6:
        add_power_modifier(card, 1000)
    return True


@register_effect("OP07-023", "blocker", "[Blocker]")
def op07_023_caribou_blocker(game_state, player, card):
    card.has_blocker = True
    return True


# --- OP07-024: Koala ---
@register_effect("OP07-024", "on_opponent_attack", "[On Opponent's Attack] May rest this: Fish-Man cost 5 or less gains Blocker this turn")
def op07_024_koala(game_state, player, card):
    """On Opponent's Attack: May rest Koala to give Fish-Man cost 5 or less Blocker this turn."""
    if getattr(card, 'is_resting', False):
        return False
    targets = [c for c in player.cards_in_play
               if 'Fish-Man' in (c.card_origin or '') and (getattr(c, 'cost', 0) or 0) <= 5
               and c is not card]
    if not targets:
        return False

    snapshot = list(targets)

    def grant_blocker_cb(selected):
        card.is_resting = True
        game_state._log("Koala rested to activate effect")
        idx = int(selected[0]) if selected else -1
        if 0 <= idx < len(snapshot):
            snapshot[idx].has_blocker = True
            game_state._log(f"{snapshot[idx].name} gains Blocker this turn")

    return create_target_choice(game_state, player, targets,
                                prompt="Rest Koala: Choose Fish-Man cost 5 or less to give Blocker this turn",
                                source_card=card, min_selections=0, max_selections=1,
                                callback=grant_blocker_cb)


# --- OP07-025: Coribou ---
@register_effect("OP07-025", "on_play", "[On Play] Play Caribou cost 4 or less from hand rested")
def op07_025_coribou(game_state, player, card):
    """On Play: Play Caribou cost 4 or less from hand rested."""
    targets = [c for c in player.hand
               if getattr(c, 'name', '') == 'Caribou' and (getattr(c, 'cost', 0) or 0) <= 4]
    if targets:
        return create_play_from_hand_choice(game_state, player, targets, source_card=card,
                                            rest_on_play=True,
                                            prompt="Choose Caribou cost 4 or less to play from hand rested")
    return True


# --- OP07-026: Jewelry Bonney (Character) ---
@register_effect("OP07-026", "on_play", "[On Play] Opponent's rested Character/DON won't become active next Refresh Phase")
def op07_026_bonney(game_state, player, card):
    """On Play: Choose opponent's rested Character to prevent from refreshing next Refresh Phase."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if getattr(c, 'is_resting', False)]
    if not targets:
        return True

    snapshot = list(targets)

    def skip_refresh_cb(selected):
        idx = int(selected[0]) if selected else -1
        if 0 <= idx < len(snapshot):
            snapshot[idx].skip_next_refresh = True
            game_state._log(f"{snapshot[idx].name} will not become active next Refresh Phase")

    return create_target_choice(game_state, player, targets,
                                prompt="Choose opponent's rested Character to prevent from refreshing",
                                source_card=card, min_selections=0, max_selections=1,
                                callback=skip_refresh_cb)


# --- OP07-029: Basil Hawkins ---
@register_effect("OP07-029", "continuous", "[Continuous] If Supernovas leader, gains Blocker")
def op07_029_hawkins_blocker(game_state, player, card):
    """Continuous: If Supernovas leader, gains Blocker."""
    if check_leader_type(player, 'Supernovas'):
        card.has_blocker = True
    return True


@register_effect("OP07-029", "on_leave_prevention", "[Once Per Turn] When removed by opponent effect, rest 1 opponent Character instead")
def op07_029_hawkins_prevention(game_state, player, card):
    """Once Per Turn: When removed by opponent effect, may rest 1 opponent Character instead."""
    if not getattr(card, 'op07_029_used', False):
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if not getattr(c, 'is_resting', False)]
        if targets:
            card.op07_029_used = True
            return create_rest_choice(game_state, player, targets, source_card=card,
                                      prompt="Choose opponent's Character to rest instead of removing Hawkins")
    return False


# --- OP07-030: Pappag ---
@register_effect("OP07-030", "continuous", "[Continuous] If have Camie Character, gains Blocker")
def op07_030_pappag(game_state, player, card):
    """Continuous: If have Camie Character, gains Blocker."""
    has_camie = any(getattr(c, 'name', '') == 'Camie' for c in player.cards_in_play)
    if has_camie:
        card.has_blocker = True
    return True


# --- OP07-031: Bartolomeo ---
@register_effect("OP07-031", "blocker", "[Blocker]")
def op07_031_bartolomeo_blocker(game_state, player, card):
    card.has_blocker = True
    return True


@register_effect("OP07-031", "continuous", "[Your Turn] [Once Per Turn] When Character rested by your effect, draw 1 and trash 1")
def op07_031_bartolomeo_draw(game_state, player, card):
    """Continuous: On your turn, when a Character is rested by your effect (once per turn), draw 1 and trash 1."""
    # Flag for engine to check — actual trigger is handled by game engine hooks
    card.bartolomeo_effect = True
    return True


# --- OP07-032: Fisher Tiger ---
@register_effect("OP07-032", "continuous", "[Rush] Can attack Characters on play turn")
def op07_032_fisher_tiger_rush(game_state, player, card):
    """Rush: Can attack Characters on play turn."""
    card.has_rush = True
    return True


@register_effect("OP07-032", "on_play", "[On Play] If Fish-Man/Merfolk leader, rest opponent's cost 6 or less")
def op07_032_fisher_tiger_play(game_state, player, card):
    """On Play: If Fish-Man or Merfolk leader, rest opponent's cost 6 or less."""
    leader_origin = (getattr(player.leader, 'card_origin', '') or '') if player.leader else ''
    if 'Fish-Man' in leader_origin or 'Merfolk' in leader_origin:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 6]
        if targets:
            return create_rest_choice(game_state, player, targets, source_card=card,
                                      min_selections=0, max_selections=1,
                                      prompt="Choose opponent's cost 6 or less to rest")
    return True


# --- OP07-033: Monkey.D.Luffy (Green) ---
@register_effect("OP07-033", "continuous", "[Continuous] If 3+ Characters, cost 3 or less Characters (not Luffy) cannot be K.O.'d by effects")
def op07_033_luffy(game_state, player, card):
    """Continuous: If 3+ Characters, your cost 3 or less Characters (not Luffy) cannot be K.O.'d by opponent effects."""
    if len(player.cards_in_play) >= 3:
        for c in player.cards_in_play:
            if (getattr(c, 'cost', 0) or 0) <= 3 and getattr(c, 'name', '') != 'Monkey.D.Luffy':
                c.cannot_be_ko_by_effects = True
    return True


# --- OP07-034: Roronoa Zoro (Green) ---
@register_effect("OP07-034", "on_attack", "[When Attacking] If 3+ Characters, +2000 power this turn")
def op07_034_zoro(game_state, player, card):
    """When Attacking: If 3+ Characters, +2000 power this turn."""
    if len(player.cards_in_play) >= 3:
        add_power_modifier(card, 2000)
    return True


# =============================================================================
# OP07 — BLUE CHARACTER EFFECTS
# =============================================================================

# --- OP07-039: Edward Weevil ---
@register_effect("OP07-039", "on_attack", "[DON!! x1] [When Attacking] Look at top 3, place at top or bottom in any order")
def op07_039_weevil(game_state, player, card):
    """When Attacking with DON x1: Look at top 3, place at top or bottom in any order."""
    if getattr(card, 'attached_don', 0) >= 1:
        return reorder_top_cards(game_state, player, 3, source_card=card, allow_top=True)
    return True


# --- OP07-040: Crocodile ---
@register_effect("OP07-040", "on_play", "[On Play] ① (Rest 1 DON): Return cost 2 or less to owner's hand")
def op07_040_crocodile(game_state, player, card):
    """On Play: Rest 1 DON to return opponent's cost 2 or less Character to hand."""
    active_idx = next((i for i, d in enumerate(player.don_pool) if d == 'active'), -1)
    if active_idx < 0:
        return True
    player.don_pool[active_idx] = 'rested'
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
    if targets:
        return create_return_to_hand_choice(game_state, player, targets, source_card=card,
                                            optional=True,
                                            prompt="Choose opponent's cost 2 or less to return to hand")
    return True


# --- OP07-041: Gloriosa ---
@register_effect("OP07-041", "on_play", "[On Play] Look at top 5, add Amazon Lily or Kuja Pirates card (not Gloriosa)")
def op07_041_gloriosa(game_state, player, card):
    """On Play: Look at top 5 and add Amazon Lily or Kuja Pirates card (not Gloriosa)."""
    def filter_fn(c):
        origin = c.card_origin or ''
        name = getattr(c, 'name', '')
        return ('Amazon Lily' in origin or 'Kuja Pirates' in origin) and 'Gloriosa' not in name

    return search_top_cards(game_state, player, look_count=5, add_count=1,
                            filter_fn=filter_fn, source_card=card,
                            prompt="Look at top 5: choose up to 1 Amazon Lily or Kuja Pirates card (not Gloriosa) to add to hand")


# --- OP07-042: Gecko Moria (Blue) ---
@register_effect("OP07-042", "on_leave_prevention", "[Once Per Turn] If Seven Warlords leader, when removed by opponent effect, place another Character at deck bottom instead")
def op07_042_gecko_moria_blue(game_state, player, card):
    """Once Per Turn: If Seven Warlords leader, when removed by opponent effect, bottom another Character instead."""
    if getattr(card, 'op07_042_used', False):
        return False
    if not check_leader_type(player, 'The Seven Warlords of the Sea'):
        return False
    other_chars = [c for c in player.cards_in_play
                   if c is not card and getattr(c, 'name', '') != 'Gecko Moria']
    if not other_chars:
        return False

    card.op07_042_used = True
    snapshot = list(other_chars)

    def bottom_cb(selected):
        idx = int(selected[0]) if selected else -1
        if 0 <= idx < len(snapshot):
            t = snapshot[idx]
            if _remove_card_instance(player.cards_in_play, t):
                player.deck.append(t)
                game_state._log(f"{t.name} placed at deck bottom instead of Gecko Moria being removed")

    return create_own_character_choice(game_state, player, other_chars, source_card=card,
                                       prompt="Choose your Character to place at deck bottom instead",
                                       callback=bottom_cb)


# --- OP07-043: Salome ---
@register_effect("OP07-043", "on_play", "[On Play] Up to 1 Boa Hancock card gains +2000 power this turn")
def op07_043_salome(game_state, player, card):
    """On Play: Give +2000 power to up to 1 Boa Hancock card this turn."""
    for c in player.cards_in_play:
        if getattr(c, 'name', '') == 'Boa Hancock':
            add_power_modifier(c, 2000)
            return True
    if player.leader and getattr(player.leader, 'name', '') == 'Boa Hancock':
        add_power_modifier(player.leader, 2000)
    return True


# --- OP07-044: Dracule Mihawk ---
@register_effect("OP07-044", "on_play", "[On Play] Draw 1 card")
def op07_044_mihawk(game_state, player, card):
    """On Play: Draw 1 card."""
    draw_cards(player, 1)
    return True


# --- OP07-045: Jinbe (Blue) ---
@register_effect("OP07-045", "on_play", "[On Play] Play Seven Warlords cost 4 or less (not Jinbe) from hand")
def op07_045_jinbe_blue(game_state, player, card):
    """On Play: Play Seven Warlords cost 4 or less (not Jinbe) from hand."""
    targets = [c for c in player.hand
               if 'The Seven Warlords of the Sea' in (c.card_origin or '')
               and (getattr(c, 'cost', 0) or 0) <= 4
               and getattr(c, 'name', '') != 'Jinbe']
    if targets:
        return create_play_from_hand_choice(game_state, player, targets, source_card=card,
                                            prompt="Choose Seven Warlords cost 4 or less (not Jinbe) to play from hand")
    return True


# --- OP07-046: Sengoku ---
@register_effect("OP07-046", "on_play", "[On Play] Look at top 5, add Seven Warlords card to hand")
def op07_046_sengoku(game_state, player, card):
    """On Play: Look at top 5 and add Seven Warlords card to hand."""
    return search_top_cards(game_state, player, look_count=5, add_count=1,
                            filter_fn=lambda c: 'The Seven Warlords of the Sea' in (c.card_origin or ''),
                            source_card=card,
                            prompt="Look at top 5: choose up to 1 Seven Warlords card to add to hand")


# --- OP07-047: Trafalgar Law ---
@register_effect("OP07-047", "activate", "[Activate: Main] Return this to hand: If opponent has 6+ hand cards, opponent places 1 at deck bottom")
def op07_047_law(game_state, player, card):
    """Activate: Return this to hand, if opponent has 6+ cards they place 1 at deck bottom."""
    if card not in player.cards_in_play:
        return False
    _remove_card_instance(player.cards_in_play, card)
    player.hand.append(card)
    game_state._log("Trafalgar Law returned to hand")
    opponent = get_opponent(game_state, player)
    if len(opponent.hand) >= 6 and opponent.hand:
        from ...game_engine import PendingChoice
        import uuid
        opp_snap = list(opponent.hand)
        opts = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})",
                 "card_id": c.id, "card_name": c.name} for i, c in enumerate(opp_snap)]

        def opp_bottom_cb(selected):
            idx = int(selected[0]) if selected else -1
            if 0 <= idx < len(opp_snap):
                c = opp_snap[idx]
                if c in opponent.hand:
                    opponent.hand.remove(c)
                    opponent.deck.append(c)
                    game_state._log(f"Opponent placed {c.name} at deck bottom")

        game_state.pending_choice = PendingChoice(
            choice_id=f"law_{uuid.uuid4().hex[:8]}",
            choice_type="select_cards",
            prompt="Trafalgar Law: Opponent places 1 card from their hand at bottom of deck",
            options=opts,
            min_selections=1, max_selections=1,
            source_card_id=card.id, source_card_name=card.name,
            callback=opp_bottom_cb, callback_action="place_at_bottom",
            callback_data={"player_id": opponent.player_id}
        )
    return True


# --- OP07-048: Donquixote Doflamingo ---
@register_effect("OP07-048", "activate", "[Activate: Main] [Once Per Turn] ② (Rest 2 DON): Reveal top card; if Warlords cost 4 or less, may play rested. Else bottom.")
def op07_048_doflamingo(game_state, player, card):
    """Activate, Once Per Turn, Rest 2 DON: Reveal top card; if Seven Warlords cost 4 or less Character, you may play it rested. Then place rest at bottom."""
    if getattr(card, 'op07_048_used', False):
        return False
    active_count = player.don_pool.count('active')
    if active_count < 2:
        return False
    rested = 0
    for i in range(len(player.don_pool)):
        if player.don_pool[i] == 'active' and rested < 2:
            player.don_pool[i] = 'rested'
            rested += 1
    card.op07_048_used = True
    if not player.deck:
        return True
    revealed = player.deck.pop(0)
    is_warlord = 'The Seven Warlords of the Sea' in (getattr(revealed, 'card_origin', '') or '')
    is_char = getattr(revealed, 'card_type', '') == 'CHARACTER'
    cost_ok = (getattr(revealed, 'cost', 0) or 0) <= 4
    game_state._log(f"Doflamingo revealed: {revealed.name}")
    if is_warlord and is_char and cost_ok:
        from ...game_engine import PendingChoice
        import uuid

        def play_cb(selected):
            choice = selected[0] if selected else 'no'
            if choice == 'yes':
                revealed.is_resting = True
                player.cards_in_play.append(revealed)
                game_state._log(f"Doflamingo: Played {revealed.name} rested")
            else:
                player.deck.append(revealed)
                game_state._log(f"Doflamingo: Placed {revealed.name} at deck bottom")

        game_state.pending_choice = PendingChoice(
            choice_id=f"doffy_{uuid.uuid4().hex[:8]}",
            choice_type="yes_no",
            prompt=f"Doflamingo: Play {revealed.name} (cost {revealed.cost or 0}) rested?",
            options=[{"id": "yes", "label": "Yes — play rested"}, {"id": "no", "label": "No — place at bottom"}],
            min_selections=1, max_selections=1,
            source_card_id=card.id, source_card_name=card.name,
            callback=play_cb, callback_action="yes_no_choice",
            callback_data={"player_id": player.player_id}
        )
    else:
        player.deck.append(revealed)
        game_state._log(f"Doflamingo: {revealed.name} not eligible, placed at bottom")
    return True


# --- OP07-049: Buckin ---
@register_effect("OP07-049", "on_play", "[On Play] Play Edward Weevil cost 4 or less from hand rested")
def op07_049_buckin(game_state, player, card):
    """On Play: Play Edward Weevil cost 4 or less from hand rested."""
    targets = [c for c in player.hand
               if getattr(c, 'name', '') == 'Edward Weevil' and (getattr(c, 'cost', 0) or 0) <= 4]
    if targets:
        return create_play_from_hand_choice(game_state, player, targets, source_card=card,
                                            rest_on_play=True,
                                            prompt="Choose Edward Weevil cost 4 or less to play from hand rested")
    return True


# --- OP07-050: Boa Sandersonia ---
@register_effect("OP07-050", "on_play", "[On Play] If 2+ Amazon Lily/Kuja Characters, return opponent's cost 3 or less to hand")
def op07_050_sandersonia(game_state, player, card):
    """On Play: If 2+ Amazon Lily or Kuja Pirates Characters, return opponent's cost 3 or less to hand."""
    count = sum(1 for c in player.cards_in_play
                if 'Amazon Lily' in (c.card_origin or '') or 'Kuja Pirates' in (c.card_origin or ''))
    if count >= 2:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
        if targets:
            return create_return_to_hand_choice(game_state, player, targets, source_card=card,
                                                optional=True,
                                                prompt="Choose opponent's cost 3 or less to return to hand")
    return True


# --- OP07-051: Boa Hancock (Blue) ---
@register_effect("OP07-051", "on_play", "[On Play] Opponent Character (not Luffy) cannot attack next turn. THEN place cost 1 or less at deck bottom.")
def op07_051_hancock_blue(game_state, player, card):
    """On Play: Up to 1 opponent Character (not Luffy) cannot attack until end of opponent's next turn.
    Then place up to 1 Character cost 1 or less at deck bottom."""
    opponent = get_opponent(game_state, player)
    cannot_attack_targets = [c for c in opponent.cards_in_play
                              if getattr(c, 'name', '') != 'Monkey.D.Luffy']
    # All characters (both players) cost 1 or less for bottom effect
    all_chars = list(player.cards_in_play) + list(opponent.cards_in_play)
    bottom_targets = [c for c in all_chars if (getattr(c, 'cost', 0) or 0) <= 1]

    cannot_attack_snapshot = list(cannot_attack_targets)
    bottom_snapshot = list(bottom_targets)

    def second_choice_cb(selected2):
        idx2 = int(selected2[0]) if selected2 else -1
        if 0 <= idx2 < len(bottom_snapshot):
            t = bottom_snapshot[idx2]
            for p in [player, opponent]:
                if _remove_card_instance(p.cards_in_play, t):
                    p.deck.append(t)
                    game_state._log(f"{t.name} placed at deck bottom")
                    break

    def first_choice_cb(selected):
        idx = int(selected[0]) if selected else -1
        if 0 <= idx < len(cannot_attack_snapshot):
            cannot_attack_snapshot[idx].cannot_attack_next_turn = True
            game_state._log(f"{cannot_attack_snapshot[idx].name} cannot attack next turn")
        # Chain second choice
        if bottom_snapshot:
            create_bottom_deck_choice(game_state, player, bottom_snapshot, source_card=card,
                                      prompt="Choose Character cost 1 or less to place at deck bottom",
                                      min_selections=0, callback=second_choice_cb)

    if cannot_attack_targets:
        return create_target_choice(game_state, player, cannot_attack_targets,
                                    prompt="Choose opponent's Character (not Luffy) — cannot attack until end of next turn",
                                    source_card=card, min_selections=0, max_selections=1,
                                    callback=first_choice_cb)
    elif bottom_targets:
        return create_bottom_deck_choice(game_state, player, bottom_targets, source_card=card,
                                         prompt="Choose Character cost 1 or less to place at deck bottom",
                                         min_selections=0, callback=second_choice_cb)
    return True


# --- OP07-052: Boa Marigold ---
@register_effect("OP07-052", "on_play", "[On Play] If 2+ Amazon Lily/Kuja Characters, place cost 2 or less at deck bottom")
def op07_052_marigold(game_state, player, card):
    """On Play: If 2+ Amazon Lily or Kuja Pirates Characters, place cost 2 or less at deck bottom."""
    count = sum(1 for c in player.cards_in_play
                if 'Amazon Lily' in (c.card_origin or '') or 'Kuja Pirates' in (c.card_origin or ''))
    if count >= 2:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
        if targets:
            return create_bottom_deck_choice(game_state, player, targets, source_card=card,
                                             min_selections=0,
                                             prompt="Choose opponent's cost 2 or less to place at deck bottom")
    return True


# --- OP07-053: Portgas.D.Ace (Blue) ---
@register_effect("OP07-053", "blocker", "[Blocker]")
def op07_053_ace_blocker(game_state, player, card):
    card.has_blocker = True
    return True


@register_effect("OP07-053", "on_play", "[On Play] Draw 2, place 2 from hand at top or bottom of deck in any order")
def op07_053_ace_play(game_state, player, card):
    """On Play: Draw 2 cards, then place 2 cards from hand at top or bottom of deck in any order."""
    draw_cards(player, 2)
    if not player.hand:
        return True

    from ...game_engine import PendingChoice
    import uuid

    hand_snap_ref = [list(player.hand)]  # mutable ref for closure

    def select_cards_cb(selected):
        indices = sorted([int(s) for s in selected], reverse=True)
        placed = []
        for idx in indices:
            if 0 <= idx < len(player.hand):
                placed.append(player.hand.pop(idx))
        if not placed:
            return
        placed_ref = placed

        def top_bottom_cb(sel):
            choice = sel[0] if sel else 'bottom'
            if choice == 'top':
                for c in reversed(placed_ref):
                    player.deck.insert(0, c)
                    game_state._log(f"{player.name} placed {c.name} at deck top")
            else:
                for c in placed_ref:
                    player.deck.append(c)
                    game_state._log(f"{player.name} placed {c.name} at deck bottom")

        game_state.pending_choice = PendingChoice(
            choice_id=f"ace_tb_{uuid.uuid4().hex[:8]}",
            choice_type="yes_no",
            prompt="Place 2 cards at top or bottom of deck?",
            options=[{"id": "top", "label": "Top of deck"}, {"id": "bottom", "label": "Bottom of deck"}],
            min_selections=1, max_selections=1,
            source_card_id=card.id, source_card_name=card.name,
            callback=top_bottom_cb, callback_action="yes_no_choice",
            callback_data={"player_id": player.player_id}
        )

    count = min(2, len(player.hand))
    hand_opts = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})",
                  "card_id": c.id, "card_name": c.name} for i, c in enumerate(player.hand)]
    game_state.pending_choice = PendingChoice(
        choice_id=f"ace_sel_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt=f"Choose {count} card(s) from hand to place at top or bottom of deck",
        options=hand_opts,
        min_selections=count, max_selections=count,
        source_card_id=card.id, source_card_name=card.name,
        callback=select_cards_cb, callback_action="place_at_bottom",
        callback_data={"player_id": player.player_id, "count": count}
    )
    return True


# --- OP07-054: Marguerite ---
@register_effect("OP07-054", "blocker", "[Blocker]")
def op07_054_marguerite_blocker(game_state, player, card):
    card.has_blocker = True
    return True


@register_effect("OP07-054", "on_play", "[On Play] Draw 1 card")
def op07_054_marguerite_play(game_state, player, card):
    """On Play: Draw 1 card."""
    draw_cards(player, 1)
    return True


# =============================================================================
# OP07 — PURPLE CHARACTER EFFECTS
# =============================================================================

# --- OP07-060: Itomimizu ---
@register_effect("OP07-060", "activate", "[Activate: Main] [Once Per Turn] If Foxy leader and no other Itomimizu, add 1 DON rested")
def op07_060_itomimizu(game_state, player, card):
    """Activate, Once Per Turn: If Foxy leader and no other Itomimizu, add 1 DON rested."""
    if getattr(card, 'op07_060_used', False):
        return False
    if not check_leader_type(player, 'Foxy Pirates'):
        return False
    other_itomimizu = sum(1 for c in player.cards_in_play
                          if getattr(c, 'name', '') == 'Itomimizu' and c is not card)
    if other_itomimizu == 0:
        add_don_from_deck(player, 1, set_active=False)
        game_state._log("Itomimizu: Added 1 DON rested")
        card.op07_060_used = True
        return True
    return False


# --- OP07-061: Vinsmoke Sanji ---
@register_effect("OP07-061", "on_play", "[On Play] DON -1: If Vinsmoke Family leader, draw 1")
def op07_061_sanji(game_state, player, card):
    """On Play: DON -1, if Vinsmoke Family leader draw 1 card."""
    if not check_leader_type(player, 'The Vinsmoke Family'):
        return True

    def do_draw():
        draw_cards(player, 1)
        game_state._log("Vinsmoke Sanji: Drew 1 card")

    auto = return_don_to_deck(game_state, player, 1, source_card=card, post_callback=do_draw)
    if auto:
        do_draw()
    return True


# --- OP07-062: Vinsmoke Reiju ---
@register_effect("OP07-062", "on_play", "[On Play] If your DON <= opponent DON, return Vinsmoke Family cost 1 Character to hand")
def op07_062_reiju(game_state, player, card):
    """On Play: If your DON <= opponent DON, return up to 1 Vinsmoke Family cost 1 Character to hand."""
    opponent = get_opponent(game_state, player)
    if len(player.don_pool) <= len(opponent.don_pool):
        targets = [c for c in player.cards_in_play
                   if 'The Vinsmoke Family' in (c.card_origin or '') and (getattr(c, 'cost', 0) or 0) == 1]
        if targets:
            return create_own_character_choice(game_state, player, targets, source_card=card,
                                               optional=True,
                                               prompt="Choose your Vinsmoke Family cost 1 Character to return to hand")
    return True


# --- OP07-063: Capote ---
@register_effect("OP07-063", "on_play", "[On Play] DON -1: If Foxy leader, opponent's cost 6 or less cannot attack until end of opponent's next turn")
def op07_063_capote(game_state, player, card):
    """On Play: DON -1, if Foxy leader opponent's cost 6 or less cannot attack until end of next turn."""
    if not check_leader_type(player, 'Foxy Pirates'):
        return True

    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 6]
    target_snapshot = list(targets)

    def do_cannot_attack():
        if target_snapshot:
            def set_cb(selected):
                idx = int(selected[0]) if selected else -1
                if 0 <= idx < len(target_snapshot):
                    target_snapshot[idx].cannot_attack_next_turn = True
                    game_state._log(f"{target_snapshot[idx].name} cannot attack until end of next turn")
            create_cannot_attack_choice(game_state, player, target_snapshot, source_card=card,
                                        prompt="Choose opponent's cost 6 or less — cannot attack until end of next turn",
                                        callback=set_cb)

    auto = return_don_to_deck(game_state, player, 1, source_card=card, post_callback=do_cannot_attack)
    if auto:
        do_cannot_attack()
    return True


# --- OP07-064: Sanji (Purple) ---
@register_effect("OP07-064", "continuous", "[Continuous] If your DON is 2+ less than opponent, -3 cost in hand")
def op07_064_sanji_cost(game_state, player, card):
    """Continuous: If your DON is 2+ less than opponent, this card costs -3 while in hand."""
    opponent = get_opponent(game_state, player)
    if len(player.don_pool) <= len(opponent.don_pool) - 2:
        card.cost_modifier = getattr(card, 'cost_modifier', 0) - 3
    return True


@register_effect("OP07-064", "blocker", "[Blocker]")
def op07_064_sanji_blocker(game_state, player, card):
    card.has_blocker = True
    return True


# --- OP07-065: Gina ---
@register_effect("OP07-065", "on_play", "[On Play] If Foxy leader and DON <= opponent DON, add 1 DON active")
def op07_065_gina(game_state, player, card):
    """On Play: If Foxy leader and your DON <= opponent DON, add 1 DON active."""
    opponent = get_opponent(game_state, player)
    if check_leader_type(player, 'Foxy Pirates') and len(player.don_pool) <= len(opponent.don_pool):
        add_don_from_deck(player, 1, set_active=True)
        game_state._log("Gina: Added 1 DON active")
    return True


# --- OP07-066: Tony Tony.Chopper (Purple) ---
@register_effect("OP07-066", "blocker", "[Blocker]")
def op07_066_chopper_blocker(game_state, player, card):
    card.has_blocker = True
    return True


@register_effect("OP07-066", "on_play", "[On Play] If your DON <= opponent DON, add 1 DON rested")
def op07_066_chopper_play(game_state, player, card):
    """On Play: If your DON <= opponent DON, add 1 DON rested."""
    opponent = get_opponent(game_state, player)
    if len(player.don_pool) <= len(opponent.don_pool):
        add_don_from_deck(player, 1, set_active=False)
        game_state._log("Tony Tony.Chopper: Added 1 DON rested")
    return True


# --- OP07-068: Hamburg ---
@register_effect("OP07-068", "on_attack", "[DON!! x1] [When Attacking] If your DON <= opponent DON, add 1 DON rested")
def op07_068_hamburg(game_state, player, card):
    """When Attacking with DON x1: If your DON <= opponent DON, add 1 DON rested."""
    if getattr(card, 'attached_don', 0) >= 1:
        opponent = get_opponent(game_state, player)
        if len(player.don_pool) <= len(opponent.don_pool):
            add_don_from_deck(player, 1, set_active=False)
            game_state._log("Hamburg: Added 1 DON rested")
    return True


# --- OP07-069: Pickles ---
@register_effect("OP07-069", "continuous", "[Continuous] If your DON <= opponent DON, Foxy Pirates (not Pickles) cannot be K.O.'d by opponent effects")
def op07_069_pickles(game_state, player, card):
    """Continuous: If your DON <= opponent DON, Foxy Pirates (not Pickles) cannot be K.O.'d by effects."""
    opponent = get_opponent(game_state, player)
    if len(player.don_pool) <= len(opponent.don_pool):
        for c in player.cards_in_play:
            if 'Foxy Pirates' in (c.card_origin or '') and getattr(c, 'name', '') != 'Pickles':
                c.cannot_be_ko_by_effects = True
    return True


# --- OP07-070: Big Bun ---
@register_effect("OP07-070", "on_play", "[On Play] If your DON <= opponent DON, play Foxy Pirates cost 4 or less from hand")
def op07_070_big_bun(game_state, player, card):
    """On Play: If your DON <= opponent DON, play Foxy Pirates cost 4 or less from hand."""
    opponent = get_opponent(game_state, player)
    if len(player.don_pool) <= len(opponent.don_pool):
        targets = [c for c in player.hand
                   if 'Foxy Pirates' in (c.card_origin or '') and (getattr(c, 'cost', 0) or 0) <= 4]
        if targets:
            return create_play_from_hand_choice(game_state, player, targets, source_card=card,
                                                prompt="Choose Foxy Pirates cost 4 or less to play from hand")
    return True


# --- OP07-071: Foxy (Character) ---
@register_effect("OP07-071", "continuous", "[Opponent's Turn] If Foxy leader, all opponent's Characters -1000 power")
def op07_071_foxy_debuff(game_state, player, card):
    """Continuous (opponent's turn): If Foxy leader, all opponent Characters -1000 power."""
    if check_leader_type(player, 'Foxy Pirates'):
        opponent = get_opponent(game_state, player)
        for c in opponent.cards_in_play:
            add_power_modifier(c, -1000)
    return True


@register_effect("OP07-071", "activate", "[Activate: Main] [Once Per Turn] Add 1 DON rested")
def op07_071_foxy_activate(game_state, player, card):
    """Activate, Once Per Turn: Add 1 DON rested."""
    if getattr(card, 'op07_071_used', False):
        return False
    add_don_from_deck(player, 1, set_active=False)
    game_state._log("Foxy: Added 1 DON rested")
    card.op07_071_used = True
    return True


# --- OP07-072: Porche ---
@register_effect("OP07-072", "on_play", "[On Play] DON -1: Look at top 5, add Foxy Pirates to hand. Play purple Character 4000 power or less from hand.")
def op07_072_porche(game_state, player, card):
    """On Play: DON -1 to look at top 5 and add Foxy Pirates to hand, then play purple Character 4000 power or less."""
    def do_search_and_play():
        # First search top 5 for Foxy Pirates
        foxy_snap = None

        def after_search():
            # Play purple 4000 power or less from hand
            targets = [c for c in player.hand
                       if 'Purple' in (getattr(c, 'color', '') or getattr(c, 'colors', '') or '')
                       and (getattr(c, 'power', 0) or 0) <= 4000]
            if targets:
                create_play_from_hand_choice(game_state, player, targets, source_card=card,
                                             prompt="Choose purple Character with 4000 power or less to play from hand")

        return search_top_cards(
            game_state, player, look_count=5, add_count=1,
            filter_fn=lambda c: 'Foxy Pirates' in (c.card_origin or ''),
            source_card=card,
            prompt="Look at top 5: choose up to 1 Foxy Pirates card to add to hand",
            callback=lambda sel: (
                [player.hand.append(player.deck.pop(int(s))) for s in sel if 0 <= int(s) < len(player.deck)] or True,
                after_search()
            ) if sel else after_search()
        )

    auto = return_don_to_deck(game_state, player, 1, source_card=card, post_callback=do_search_and_play)
    if auto:
        do_search_and_play()
    return True


# --- OP07-073: Monkey.D.Luffy (Purple) ---
@register_effect("OP07-073", "activate", "[Activate: Main] [Once Per Turn] DON -3: If opponent has 3+ Characters, set this active")
def op07_073_luffy_purple(game_state, player, card):
    """Activate, Once Per Turn: DON -3, if opponent has 3+ Characters, set this card active."""
    if getattr(card, 'op07_073_used', False):
        return False
    opponent = get_opponent(game_state, player)
    if len(opponent.cards_in_play) < 3:
        return False

    def do_set_active():
        card.is_resting = False
        card.has_attacked = False
        card.op07_073_used = True
        game_state._log("Monkey.D.Luffy (Purple): Set active")

    auto = return_don_to_deck(game_state, player, 3, source_card=card, post_callback=do_set_active)
    if auto:
        do_set_active()
    return True


# --- OP07-074: Monda ---
@register_effect("OP07-074", "activate", "[Activate: Main] May trash this: If Foxy leader, add 1 DON rested")
def op07_074_monda(game_state, player, card):
    """Activate: May trash this to add 1 DON rested if Foxy leader."""
    if card not in player.cards_in_play:
        return False
    _remove_card_instance(player.cards_in_play, card)
    player.trash.append(card)
    if check_leader_type(player, 'Foxy Pirates'):
        add_don_from_deck(player, 1, set_active=False)
        game_state._log("Monda: Added 1 DON rested")
    return True


# =============================================================================
# OP07 — BLACK CHARACTER EFFECTS
# =============================================================================

# --- OP07-080: Kaku ---
@register_effect("OP07-080", "on_play", "[On Play] May place 2 CP-type cards from trash at deck bottom: Give opponent Character -3 cost this turn")
def op07_080_kaku(game_state, player, card):
    """On Play: You may place 2 CP-type cards from trash at deck bottom to give opponent Character -3 cost."""
    cp_cards = [c for c in player.trash if 'CP' in (c.card_origin or '')]
    if len(cp_cards) < 2:
        return True

    from ...game_engine import PendingChoice
    import uuid
    opponent = get_opponent(game_state, player)
    cp_snap = cp_cards[:2]

    def kaku_cb(selected):
        choice = selected[0] if selected else 'no'
        if choice == 'yes':
            for c in cp_snap:
                _remove_card_instance(player.trash, c)
                player.deck.append(c)
                game_state._log(f"Kaku: Placed {c.name} at deck bottom")
            targets = list(opponent.cards_in_play)
            if targets:
                create_cost_reduction_choice(game_state, player, targets, -3, source_card=card,
                                             min_selections=0, max_selections=1,
                                             prompt="Choose opponent's Character to give -3 cost this turn")

    game_state.pending_choice = PendingChoice(
        choice_id=f"kaku_{uuid.uuid4().hex[:8]}",
        choice_type="yes_no",
        prompt="Place 2 CP cards from trash at deck bottom to give opponent's Character -3 cost?",
        options=[{"id": "yes", "label": "Yes"}, {"id": "no", "label": "No"}],
        min_selections=1, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=kaku_cb, callback_action="yes_no_choice",
        callback_data={"player_id": player.player_id}
    )
    return True


# --- OP07-081: Kalifa ---
@register_effect("OP07-081", "continuous", "[DON!! x1] [Your Turn] All opponent's Characters -1 cost")
def op07_081_kalifa(game_state, player, card):
    """Continuous (your turn, DON x1): All opponent's Characters -1 cost."""
    if getattr(card, 'attached_don', 0) >= 1:
        opponent = get_opponent(game_state, player)
        for c in opponent.cards_in_play:
            c.cost_modifier = getattr(c, 'cost_modifier', 0) - 1
    return True


# --- OP07-082: Captain John ---
@register_effect("OP07-082", "on_play", "[On Play] Trash 2 from top of deck, give opponent Character -1 cost this turn")
def op07_082_captain_john(game_state, player, card):
    """On Play: Trash 2 from top of deck and give opponent's Character -1 cost."""
    for _ in range(min(2, len(player.deck))):
        if player.deck:
            c = player.deck.pop(0)
            player.trash.append(c)
    opponent = get_opponent(game_state, player)
    targets = list(opponent.cards_in_play)
    if targets:
        return create_cost_reduction_choice(game_state, player, targets, -1, source_card=card,
                                            min_selections=0, max_selections=1,
                                            prompt="Choose opponent's Character to give -1 cost this turn")
    return True


# --- OP07-083: Gecko Moria (Black) ---
@register_effect("OP07-083", "activate", "[Activate: Main] May place 4 Thriller Bark Pirates from trash at deck bottom: Gain Banish and +1000 power this turn")
def op07_083_gecko_moria_black(game_state, player, card):
    """Activate: You may place 4 Thriller Bark Pirates from trash at deck bottom to gain Banish and +1000 power."""
    tb_cards = [c for c in player.trash if 'Thriller Bark Pirates' in (c.card_origin or '')]
    if len(tb_cards) < 4:
        return False

    from ...game_engine import PendingChoice
    import uuid
    tb_snap = tb_cards[:4]

    def moria_cb(selected):
        choice = selected[0] if selected else 'no'
        if choice == 'yes':
            for c in tb_snap:
                _remove_card_instance(player.trash, c)
                player.deck.append(c)
            card.has_banish = True
            add_power_modifier(card, 1000)
            game_state._log("Gecko Moria (Black): Gains Banish and +1000 power this turn")

    game_state.pending_choice = PendingChoice(
        choice_id=f"moria_{uuid.uuid4().hex[:8]}",
        choice_type="yes_no",
        prompt="Place 4 Thriller Bark Pirates from trash at deck bottom to gain Banish and +1000 power?",
        options=[{"id": "yes", "label": "Yes"}, {"id": "no", "label": "No"}],
        min_selections=1, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=moria_cb, callback_action="yes_no_choice",
        callback_data={"player_id": player.player_id}
    )
    return True


# --- OP07-084: Gismonda ---
@register_effect("OP07-084", "blocker", "[Blocker]")
def op07_084_gismonda(game_state, player, card):
    card.has_blocker = True
    return True


# --- OP07-085: Stussy ---
@register_effect("OP07-085", "on_play", "[On Play] May trash 1 of your Characters: K.O. up to 1 opponent Character")
def op07_085_stussy(game_state, player, card):
    """On Play: May trash 1 of your Characters to K.O. up to 1 opponent Character."""
    own_chars = [c for c in player.cards_in_play if c is not card]
    if not own_chars:
        return True

    opponent = get_opponent(game_state, player)
    opp_targets = list(opponent.cards_in_play)

    own_snapshot = list(own_chars)
    opp_snapshot = list(opp_targets)

    def after_own_trash_cb(selected):
        idx = int(selected[0]) if selected else -1
        if 0 <= idx < len(own_snapshot):
            t = own_snapshot[idx]
            if _remove_card_instance(player.cards_in_play, t):
                player.trash.append(t)
                game_state._log(f"Stussy: Trashed {t.name}")
        # Now choose opponent's character to KO
        if opp_snapshot:
            create_ko_choice(game_state, player, opp_snapshot, source_card=card,
                             prompt="Choose opponent's Character to K.O.",
                             min_selections=0, max_selections=1)

    return create_own_character_choice(game_state, player, own_chars, source_card=card,
                                       optional=True,
                                       prompt="May trash 1 of your Characters (Stussy effect)",
                                       callback=after_own_trash_cb)


# --- OP07-086: Spandam ---
@register_effect("OP07-086", "on_play", "[On Play] Trash 2 from top of deck, give opponent Character -2 cost this turn")
def op07_086_spandam(game_state, player, card):
    """On Play: Trash 2 from top of deck and give opponent's Character -2 cost."""
    for _ in range(min(2, len(player.deck))):
        if player.deck:
            c = player.deck.pop(0)
            player.trash.append(c)
    opponent = get_opponent(game_state, player)
    targets = list(opponent.cards_in_play)
    if targets:
        return create_cost_reduction_choice(game_state, player, targets, -2, source_card=card,
                                            min_selections=0, max_selections=1,
                                            prompt="Choose opponent's Character to give -2 cost this turn")
    return True


# --- OP07-087: Baskerville ---
@register_effect("OP07-087", "continuous", "[Your Turn] If opponent has cost 0 Character, +3000 power")
def op07_087_baskerville(game_state, player, card):
    """Continuous (your turn): If opponent has a cost 0 Character, +3000 power."""
    opponent = get_opponent(game_state, player)
    has_cost_0 = any(
        (getattr(c, 'cost', 0) or 0) + (getattr(c, 'cost_modifier', 0) or 0) == 0
        for c in opponent.cards_in_play
    )
    if has_cost_0:
        add_power_modifier(card, 3000)
    return True


# --- OP07-088: Hattori ---
@register_effect("OP07-088", "on_play", "[On Play] Up to 1 Rob Lucci card gains +2000 power this turn")
def op07_088_hattori(game_state, player, card):
    """On Play: Give +2000 power to up to 1 Rob Lucci card this turn."""
    for c in player.cards_in_play:
        if getattr(c, 'name', '') == 'Rob Lucci':
            add_power_modifier(c, 2000)
            return True
    if player.leader and getattr(player.leader, 'name', '') == 'Rob Lucci':
        add_power_modifier(player.leader, 2000)
    return True


# --- OP07-090: Morgans ---
@register_effect("OP07-090", "on_play", "[On Play] Opponent trashes 1 from hand (reveals hand). Then opponent draws 1.")
def op07_090_morgans(game_state, player, card):
    """On Play: Opponent trashes 1 from hand (reveals), then opponent draws 1."""
    opponent = get_opponent(game_state, player)
    if opponent.hand:
        trash_from_hand(opponent, 1, game_state, card)
    draw_cards(opponent, 1)
    return True


# --- OP07-091: Monkey.D.Luffy (Black) ---
@register_effect("OP07-091", "on_attack", "[When Attacking] Trash opponent's cost 2 or less. Then place any number of cost 4+ from trash at deck bottom. +1000 per 3 placed.")
def op07_091_luffy_black(game_state, player, card):
    """When Attacking: Trash opponent's cost 2 or less. Then place any number of cost 4+ Characters from trash at deck bottom. +1000 per 3 placed."""
    opponent = get_opponent(game_state, player)
    opp_targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
    cost_4_plus = [c for c in player.trash if (getattr(c, 'cost', 0) or 0) >= 4]

    def do_bottom_choice():
        if not cost_4_plus:
            return
        from ...game_engine import PendingChoice
        import uuid
        snap = list(cost_4_plus)
        opts = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})",
                 "card_id": c.id, "card_name": c.name} for i, c in enumerate(snap)]

        def bottom_cb(selected):
            placed = []
            indices = sorted([int(s) for s in selected], reverse=True)
            for idx in indices:
                if 0 <= idx < len(snap):
                    c = snap[idx]
                    if _remove_card_instance(player.trash, c):
                        player.deck.append(c)
                        placed.append(c)
            bonus = (len(placed) // 3) * 1000
            if bonus > 0:
                add_power_modifier(card, bonus)
                game_state._log(f"Luffy (Black): +{bonus} power from {len(placed)} cards placed")

        game_state.pending_choice = PendingChoice(
            choice_id=f"luffy_b_{uuid.uuid4().hex[:8]}",
            choice_type="select_cards",
            prompt="Choose any number of cost 4+ Characters from trash to place at deck bottom (+1000 power per 3)",
            options=opts,
            min_selections=0, max_selections=len(snap),
            source_card_id=card.id, source_card_name=card.name,
            callback=bottom_cb, callback_action="place_at_bottom",
            callback_data={"player_id": player.player_id}
        )

    if opp_targets:
        opp_snap = list(opp_targets)

        def ko_then_bottom_cb(selected):
            idx = int(selected[0]) if selected else -1
            if 0 <= idx < len(opp_snap):
                game_state._attempt_character_ko(opp_snap[idx], by_effect=True)
            do_bottom_choice()

        return create_ko_choice(game_state, player, opp_targets, source_card=card,
                                prompt="Choose opponent's cost 2 or less Character to trash",
                                min_selections=0, max_selections=1,
                                callback=ko_then_bottom_cb)
    else:
        do_bottom_choice()
    return True


# --- OP07-092: Joseph ---
@register_effect("OP07-092", "on_play", "[On Play] May place 2 CP-type cards from trash at deck bottom: K.O. cost 1 or less")
def op07_092_joseph(game_state, player, card):
    """On Play: You may place 2 CP-type cards from trash at deck bottom to K.O. up to 1 opponent cost 1 or less."""
    cp_cards = [c for c in player.trash if 'CP' in (c.card_origin or '')]
    if len(cp_cards) < 2:
        return True

    from ...game_engine import PendingChoice
    import uuid
    opponent = get_opponent(game_state, player)
    cp_snap = cp_cards[:2]

    def joseph_cb(selected):
        choice = selected[0] if selected else 'no'
        if choice == 'yes':
            for c in cp_snap:
                _remove_card_instance(player.trash, c)
                player.deck.append(c)
                game_state._log(f"Joseph: Placed {c.name} at deck bottom")
            targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 1]
            if targets:
                create_ko_choice(game_state, player, targets, source_card=card,
                                 prompt="Choose opponent's cost 1 or less to K.O.",
                                 min_selections=0, max_selections=1)

    game_state.pending_choice = PendingChoice(
        choice_id=f"joseph_{uuid.uuid4().hex[:8]}",
        choice_type="yes_no",
        prompt="Place 2 CP cards from trash at deck bottom to K.O. opponent's cost 1 or less?",
        options=[{"id": "yes", "label": "Yes"}, {"id": "no", "label": "No"}],
        min_selections=1, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=joseph_cb, callback_action="yes_no_choice",
        callback_data={"player_id": player.player_id}
    )
    return True


# --- OP07-093: Rob Lucci ---
@register_effect("OP07-093", "on_play", "[On Play] May place 3 from trash at deck bottom: Opponent trashes 1. Then may place 1 from opponent's trash at deck bottom.")
def op07_093_rob_lucci(game_state, player, card):
    """On Play: You may place 3 from trash at deck bottom; opponent trashes 1; then may place 1 from opponent's trash at deck bottom."""
    opponent = get_opponent(game_state, player)

    def after_opp_trash():
        if opponent.trash:
            opp_trash_snap = list(opponent.trash)

            def place_opp_trash_cb(selected):
                idx = int(selected[0]) if selected else -1
                if 0 <= idx < len(opp_trash_snap):
                    t = opp_trash_snap[idx]
                    if _remove_card_instance(opponent.trash, t):
                        opponent.deck.append(t)
                        game_state._log(f"Rob Lucci: Placed {t.name} from opponent's trash at deck bottom")

            create_bottom_deck_choice(game_state, player, opp_trash_snap, source_card=card,
                                      min_selections=0, callback=place_opp_trash_cb,
                                      prompt="Choose 1 card from opponent's trash to place at deck bottom (optional)")

    def do_opp_trash():
        if opponent.hand:
            trash_from_hand(opponent, 1, game_state, card)
            if game_state.pending_choice is not None:
                orig_cb = game_state.pending_choice.callback

                def chained_cb(selected):
                    if orig_cb:
                        orig_cb(selected)
                    after_opp_trash()

                game_state.pending_choice.callback = chained_cb
            else:
                after_opp_trash()
        else:
            after_opp_trash()

    if len(player.trash) < 3:
        do_opp_trash()
        return True

    from ...game_engine import PendingChoice
    import uuid
    trash_snap = list(player.trash)
    opts = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})",
             "card_id": c.id, "card_name": c.name} for i, c in enumerate(trash_snap)]

    def lucci_own_cb(selected):
        choice = selected[0] if selected else 'no'
        if choice == 'yes':
            # Player selects 3 cards from trash to bottom
            sel_opts = opts[:len(trash_snap)]

            def pick3_cb(picked):
                indices = sorted([int(s) for s in picked], reverse=True)
                for idx in indices:
                    if 0 <= idx < len(trash_snap):
                        c = trash_snap[idx]
                        if _remove_card_instance(player.trash, c):
                            player.deck.append(c)
                            game_state._log(f"Rob Lucci: Placed {c.name} at deck bottom")
                do_opp_trash()

            game_state.pending_choice = PendingChoice(
                choice_id=f"lucci_pick_{uuid.uuid4().hex[:8]}",
                choice_type="select_cards",
                prompt="Choose 3 cards from your trash to place at deck bottom",
                options=sel_opts,
                min_selections=3, max_selections=3,
                source_card_id=card.id, source_card_name=card.name,
                callback=pick3_cb, callback_action="place_at_bottom",
                callback_data={"player_id": player.player_id}
            )
        else:
            do_opp_trash()

    game_state.pending_choice = PendingChoice(
        choice_id=f"lucci_yn_{uuid.uuid4().hex[:8]}",
        choice_type="yes_no",
        prompt="Place 3 cards from your trash at deck bottom (then opponent trashes 1)?",
        options=[{"id": "yes", "label": "Yes"}, {"id": "no", "label": "No"}],
        min_selections=1, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=lucci_own_cb, callback_action="yes_no_choice",
        callback_data={"player_id": player.player_id}
    )
    return True


# =============================================================================
# OP07 — YELLOW CHARACTER EFFECTS
# =============================================================================

# --- OP07-098: Atlas ---
@register_effect("OP07-098", "continuous", "[Continuous] If fewer life than opponent, cannot be K.O.'d in battle")
def op07_098_atlas_continuous(game_state, player, card):
    """Continuous: If fewer life cards than opponent, cannot be K.O.'d in battle."""
    opponent = get_opponent(game_state, player)
    if len(player.life_cards) < len(opponent.life_cards):
        card.cannot_be_ko_in_battle = True
    return True


@register_effect("OP07-098", "trigger", "[Trigger] If Leader is Vegapunk, play this card")
def op07_098_atlas_trigger(game_state, player, card):
    """Trigger: If Leader is Vegapunk, play this card."""
    if player.leader and getattr(player.leader, 'name', '') == 'Vegapunk':
        player.cards_in_play.append(card)
        game_state._log("Atlas: Played to field via trigger")
    return True


# --- OP07-099: Usopp (Yellow) ---
@register_effect("OP07-099", "trigger", "[Trigger] Up to 1 Egghead Leader or Character gains +2000 power until end of next turn")
def op07_099_usopp(game_state, player, card):
    """Trigger: Up to 1 Egghead Leader or Character gains +2000 power until end of next turn."""
    targets = []
    if player.leader and 'Egghead' in (getattr(player.leader, 'card_origin', '') or ''):
        targets.append(player.leader)
    targets.extend([c for c in player.cards_in_play
                    if 'Egghead' in (c.card_origin or '')])
    if targets:
        snapshot = list(targets)

        def power_cb(selected):
            idx = int(selected[0]) if selected else -1
            if 0 <= idx < len(snapshot):
                add_power_modifier(snapshot[idx], 2000)
                game_state._log(f"{snapshot[idx].name} gains +2000 power until end of next turn")

        return create_target_choice(game_state, player, targets,
                                    prompt="Choose Egghead Leader or Character to give +2000 power",
                                    source_card=card, min_selections=0, max_selections=1,
                                    callback=power_cb)
    return True


# --- OP07-100: Edison ---
@register_effect("OP07-100", "on_play", "[On Play] If 2 or less life, draw 2 and trash 2")
def op07_100_edison(game_state, player, card):
    """On Play: If 2 or less life, draw 2 and trash 2."""
    if check_life_count(player, 2):
        draw_cards(player, 2)
        trash_from_hand(player, 2, game_state, card)
    return True


@register_effect("OP07-100", "trigger", "[Trigger] If Leader is Vegapunk, play this card")
def op07_100_edison_trigger(game_state, player, card):
    """Trigger: If Leader is Vegapunk, play this card."""
    if player.leader and getattr(player.leader, 'name', '') == 'Vegapunk':
        player.cards_in_play.append(card)
        game_state._log("Edison: Played to field via trigger")
    return True


# --- OP07-101: Shaka ---
@register_effect("OP07-101", "blocker", "[Blocker]")
def op07_101_shaka_blocker(game_state, player, card):
    card.has_blocker = True
    return True


@register_effect("OP07-101", "trigger", "[Trigger] If Leader is Vegapunk, play this card")
def op07_101_shaka_trigger(game_state, player, card):
    """Trigger: If Leader is Vegapunk, play this card."""
    if check_leader_type(player, 'Egghead'):
        player.cards_in_play.append(card)
        game_state._log(f"Shaka: Played to field via trigger")
    return True


# --- OP07-102: Jinbe (Yellow) ---
@register_effect("OP07-102", "trigger", "[Trigger] Return opponent's cost 4 or less to hand AND add this to hand")
def op07_102_jinbe_yellow(game_state, player, card):
    """Trigger: Return opponent's cost 4 or less to hand, add this to hand."""
    player.hand.append(card)
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
    if targets:
        return create_return_to_hand_choice(game_state, player, targets, source_card=card,
                                            optional=True,
                                            prompt="Choose opponent's cost 4 or less to return to hand")
    return True


# --- OP07-103: Tony Tony.Chopper (Yellow) ---
@register_effect("OP07-103", "trigger", "[Trigger] Up to 1 Egghead Character gains Blocker this turn. Then add this to hand.")
def op07_103_chopper_yellow(game_state, player, card):
    """Trigger: Up to 1 Egghead Character gains Blocker this turn. Then add this to hand."""
    player.hand.append(card)
    targets = [c for c in player.cards_in_play if 'Egghead' in (c.card_origin or '')]
    if targets:
        snapshot = list(targets)

        def blocker_cb(selected):
            idx = int(selected[0]) if selected else -1
            if 0 <= idx < len(snapshot):
                snapshot[idx].has_blocker = True
                game_state._log(f"{snapshot[idx].name} gains Blocker this turn")

        return create_target_choice(game_state, player, targets,
                                    prompt="Choose your Egghead Character to give Blocker this turn",
                                    source_card=card, min_selections=0, max_selections=1,
                                    callback=blocker_cb)
    return True


# --- OP07-104: Nico Robin (Yellow) ---
@register_effect("OP07-104", "trigger", "[Trigger] If Egghead leader, draw 2")
def op07_104_robin_yellow(game_state, player, card):
    """Trigger: If Egghead leader, draw 2."""
    if check_leader_type(player, 'Egghead'):
        draw_cards(player, 2)
    return True


# --- OP07-105: Pythagoras ---
@register_effect("OP07-105", "on_ko", "[On K.O.] If 2 or less life, play Egghead cost 4 or less from trash rested")
def op07_105_pythagoras_ko(game_state, player, card):
    """On K.O.: If 2 or less life, play Egghead cost 4 or less from trash rested."""
    if check_life_count(player, 2):
        targets = [c for c in player.trash
                   if 'Egghead' in (getattr(c, 'card_origin', '') or '')
                   and (getattr(c, 'cost', 0) or 0) <= 4]
        if targets:
            return create_play_from_trash_choice(game_state, player, targets, source_card=card,
                                                  rest_on_play=True,
                                                  prompt="Choose Egghead cost 4 or less to play from trash rested")
    return True


@register_effect("OP07-105", "trigger", "[Trigger] If Leader is Vegapunk, play this card")
def op07_105_pythagoras_trigger(game_state, player, card):
    """Trigger: If Leader is Vegapunk, play this card."""
    if check_leader_type(player, 'Egghead'):
        player.cards_in_play.append(card)
        game_state._log(f"Pythagoras: Played to field via trigger")
    return True


# --- OP07-106: Fuza ---
@register_effect("OP07-106", "on_attack", "[DON!! x1] [When Attacking] If 1 or less life, K.O. opponent's cost 3 or less")
def op07_106_fuza(game_state, player, card):
    """When Attacking with DON x1: If 1 or less life, K.O. opponent's cost 3 or less."""
    if getattr(card, 'attached_don', 0) >= 1 and check_life_count(player, 1):
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                    prompt="Choose opponent's cost 3 or less to K.O.",
                                    min_selections=0, max_selections=1)
    return True


# --- OP07-107: Franky (Yellow) ---
@register_effect("OP07-107", "trigger", "[Trigger] Draw 1. Then if 1 or less life, play this card.")
def op07_107_franky_yellow(game_state, player, card):
    """Trigger: Draw 1. If 1 or less life, play this card."""
    draw_cards(player, 1)
    if check_life_count(player, 1):
        player.cards_in_play.append(card)
        game_state._log(f"Franky: Played to field via trigger")
    return True


# --- OP07-109: Monkey.D.Luffy (Yellow) ---
@register_effect("OP07-109", "activate", "[Activate: Main] May trash this: If 2 or less life, K.O. cost 4 or less and draw 1")
def op07_109_luffy_yellow_activate(game_state, player, card):
    """Activate: Trash this card, if 2 or less life K.O. cost 4 or less and draw 1."""
    if card not in player.cards_in_play:
        return False
    _remove_card_instance(player.cards_in_play, card)
    player.trash.append(card)
    draw_cards(player, 1)
    if check_life_count(player, 2):
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                    prompt="Choose opponent's cost 4 or less to K.O.",
                                    min_selections=0, max_selections=1)
    return True


@register_effect("OP07-109", "trigger", "[Trigger] K.O. up to 1 opponent cost 4 or less")
def op07_109_luffy_yellow_trigger(game_state, player, card):
    """Trigger: K.O. up to 1 opponent cost 4 or less."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                                prompt="Choose opponent's cost 4 or less to K.O.",
                                min_selections=0, max_selections=1)
    return True


# --- OP07-110: York ---
@register_effect("OP07-110", "on_play", "[On Play] May add 1 from life to hand: K.O. up to 1 opponent cost 2 or less")
def op07_110_york(game_state, player, card):
    """On Play: May add 1 card from top or bottom of life to hand, then K.O. up to 1 opponent cost 2 or less."""
    if player.life_cards:
        life_card = player.life_cards.pop()
        player.hand.append(life_card)
        game_state._log(f"York: Added {life_card.name} from life to hand")
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                                prompt="Choose opponent's cost 2 or less to K.O.",
                                min_selections=0, max_selections=1)
    return True


@register_effect("OP07-110", "trigger", "[Trigger] If Leader is Vegapunk, play this card")
def op07_110_york_trigger(game_state, player, card):
    """Trigger: If Leader is Vegapunk, play this card."""
    if check_leader_type(player, 'Egghead'):
        player.cards_in_play.append(card)
        game_state._log(f"York: Played to field via trigger")
    return True


# --- OP07-111: Lilith ---
@register_effect("OP07-111", "on_play", "[On Play] Look at top 5, add up to 1 Egghead card (not Lilith) to hand")
def op07_111_lilith(game_state, player, card):
    """On Play: Look at top 5 and add up to 1 Egghead card (not Lilith)."""
    return search_top_cards(game_state, player, look_count=5, add_count=1,
                            filter_fn=lambda c: 'Egghead' in (c.card_origin or '') and getattr(c, 'name', '') != 'Lilith',
                            source_card=card,
                            prompt="Look at top 5: choose up to 1 Egghead card (not Lilith) to add to hand")


@register_effect("OP07-111", "trigger", "[Trigger] If Leader is Vegapunk, play this card")
def op07_111_lilith_trigger(game_state, player, card):
    """Trigger: If Leader is Vegapunk, play this card."""
    if check_leader_type(player, 'Egghead'):
        player.cards_in_play.append(card)
        game_state._log(f"Lilith: Played to field via trigger")
    return True


# --- OP07-112: Lucy ---
@register_effect("OP07-112", "on_attack", "[When Attacking] [Once Per Turn] May add life to hand: May rest cost 4 or less. Then if 1 or less life, add top deck to top of life.")
def op07_112_lucy(game_state, player, card):
    """When Attacking, Once Per Turn: May add life to hand, may rest opponent's cost 4 or less. If 1 or less life, add top of deck to life."""
    if getattr(card, 'op07_112_used', False):
        return False
    card.op07_112_used = True

    if player.life_cards:
        life_card = player.life_cards.pop()
        player.hand.append(life_card)
        game_state._log(f"Lucy: Added {life_card.name} from life to hand")

    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]

    def after_rest_cb(selected=None):
        if check_life_count(player, 1) and player.deck:
            top_card = player.deck.pop(0)
            player.life_cards.append(top_card)
            game_state._log(f"Lucy: Added {top_card.name} to top of life")

    if targets:
        snapshot = list(targets)

        def rest_cb(selected):
            idx = int(selected[0]) if selected else -1
            if 0 <= idx < len(snapshot):
                snapshot[idx].is_resting = True
                game_state._log(f"{snapshot[idx].name} was rested")
            after_rest_cb()

        return create_rest_choice(game_state, player, targets, source_card=card,
                                  min_selections=0, max_selections=1,
                                  prompt="Choose opponent's cost 4 or less to rest (optional)",
                                  callback=rest_cb)
    else:
        after_rest_cb()
    return True


# --- OP07-113: Roronoa Zoro (Yellow) ---
@register_effect("OP07-113", "trigger", "[Trigger] If Egghead leader, rest up to 1 opponent Leader or Character")
def op07_113_zoro_yellow(game_state, player, card):
    """Trigger: If Egghead leader, rest up to 1 opponent Leader or Character."""
    if not check_leader_type(player, 'Egghead'):
        return True
    opponent = get_opponent(game_state, player)
    targets = []
    if opponent.leader:
        targets.append(opponent.leader)
    targets.extend(list(opponent.cards_in_play))
    if targets:
        return create_rest_choice(game_state, player, targets, source_card=card,
                                  min_selections=0, max_selections=1,
                                  prompt="Choose opponent's Leader or Character to rest")
    return True


# =============================================================================
# OP07 — SECRET RARE EFFECTS
# =============================================================================

# --- OP07-118: Sabo (SEC) ---
@register_effect("OP07-118", "on_play", "[On Play] May trash 1 from hand: K.O. up to 1 opponent cost 5 or less AND up to 1 opponent cost 3 or less")
def op07_118_sabo(game_state, player, card):
    """On Play: May trash 1 from hand to K.O. up to 1 opponent cost 5 or less AND up to 1 opponent cost 3 or less."""
    if not player.hand:
        return True

    opponent = get_opponent(game_state, player)

    def do_ko_chain():
        targets5 = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 5]
        targets3_snap = None  # Will be built after first KO

        def ko5_cb(selected):
            idx = int(selected[0]) if selected else -1
            if 0 <= idx < len(targets5_snap):
                game_state._attempt_character_ko(targets5_snap[idx], by_effect=True)
            # Second KO: cost 3 or less (re-evaluate field after first KO)
            targets3 = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
            if targets3:
                create_ko_choice(game_state, player, targets3, source_card=card,
                                 prompt="Choose 2nd opponent's cost 3 or less to K.O. (optional)",
                                 min_selections=0, max_selections=1)

        targets5_snap = list(targets5)
        if targets5_snap:
            create_ko_choice(game_state, player, targets5_snap, source_card=card,
                             prompt="Choose opponent's cost 5 or less to K.O. (optional)",
                             min_selections=0, max_selections=1,
                             callback=ko5_cb)
        else:
            # No cost 5 target, still try cost 3
            targets3 = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
            if targets3:
                create_ko_choice(game_state, player, targets3, source_card=card,
                                 prompt="Choose opponent's cost 3 or less to K.O. (optional)",
                                 min_selections=0, max_selections=1)

    def trash_cb(selected):
        if selected:
            idx = int(selected[0])
            if 0 <= idx < len(player.hand):
                c = player.hand.pop(idx)
                player.trash.append(c)
                game_state._log(f"{player.name} trashed {c.name} for Sabo's effect")
        do_ko_chain()

    from ...game_engine import PendingChoice
    import uuid
    hand_opts = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})",
                  "card_id": c.id, "card_name": c.name} for i, c in enumerate(player.hand)]

    game_state.pending_choice = PendingChoice(
        choice_id=f"sabo_trash_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="May trash 1 card from hand for Sabo's effect (select 0 to skip)",
        options=hand_opts,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=trash_cb,
        callback_action="trash_from_hand",
        callback_data={"player_id": player.player_id, "count": 1}
    )
    return True


# --- OP07-119: Portgas.D.Ace (SEC Yellow) ---
@register_effect("OP07-119", "on_play", "[On Play] Add top of deck to top of life. If 2 or less life, gain Rush this turn.")
def op07_119_ace_sec(game_state, player, card):
    """On Play: Add top of deck to top of life. If 2 or less life, gain Rush this turn."""
    if player.deck:
        top_card = player.deck.pop(0)
        player.life_cards.append(top_card)
        game_state._log(f"Portgas.D.Ace (SEC): Added {top_card.name} to top of life")
    if check_life_count(player, 2):
        card.has_rush = True
        game_state._log("Portgas.D.Ace (SEC): Gains Rush this turn")
    return True


# =============================================================================
# OP07 — EVENT EFFECTS
# =============================================================================

# --- OP07-037: More Pizza!! ---
@register_effect("OP07-037", "on_play", "[Main] Look at top 5, reveal up to 1 Supernovas card to hand")
def op07_037_more_pizza(game_state, player, card):
    """Main: Look at top 5, choose up to 1 Supernovas type card (not More Pizza!!) to add to hand."""
    return search_top_cards(game_state, player, look_count=5, add_count=1,
                            filter_fn=lambda c: 'Supernovas' in (c.card_origin or '')
                                                and getattr(c, 'name', '') != 'More Pizza!!',
                            source_card=card,
                            prompt="Look at top 5: choose up to 1 Supernovas card (not More Pizza!!) to add to hand")


# --- OP07-056: Slave Arrow ---
@register_effect("OP07-056", "counter", "[Counter] Return cost 2+ Character to hand: +4000 power")
def op07_056_slave_arrow(game_state, player, card):
    """Counter: Return cost 2+ Character to hand, gain +4000 power."""
    targets = [c for c in player.cards_in_play if (getattr(c, 'cost', 0) or 0) >= 2]
    if not targets:
        return False
    snapshot = list(targets)

    def slave_arrow_cb(selected):
        idx = int(selected[0]) if selected else -1
        if 0 <= idx < len(snapshot):
            target = snapshot[idx]
            if _remove_card_instance(player.cards_in_play, target):
                player.hand.append(target)
                game_state._log(f"{target.name} returned to hand")
        # Apply +4000 to leader or defending card
        if player.leader:
            add_power_modifier(player.leader, 4000)
            game_state._log("Leader gained +4000 power")

    return create_own_character_choice(game_state, player, targets, source_card=card,
                                       callback=slave_arrow_cb,
                                       prompt="Choose your cost 2+ Character to return to hand (Leader gains +4000 power)")


# --- OP07-077: We're Going to Claim the One Piece!!! ---
@register_effect("OP07-077", "on_play", "[Main] If Animal Kingdom Pirates/Big Mom Pirates leader, look at top 5, add 1 AK/BM card")
def op07_077_one_piece(game_state, player, card):
    """Main: If Animal Kingdom/Big Mom Pirates leader, look at top 5 and add 1 AK/BM card."""
    leader_origin = (getattr(player.leader, 'card_origin', '') or '').lower() if player.leader else ''
    if 'animal kingdom pirates' not in leader_origin and 'big mom pirates' not in leader_origin:
        return False
    return search_top_cards(game_state, player, look_count=5, add_count=1,
                            filter_fn=lambda c: ('Animal Kingdom Pirates' in (c.card_origin or '')
                                                  or 'Big Mom Pirates' in (c.card_origin or '')),
                            source_card=card,
                            prompt="Look at top 5: choose 1 Animal Kingdom Pirates or Big Mom Pirates card to add to hand")


# --- OP07-094: Shave ---
@register_effect("OP07-094", "counter", "[Counter] +2000 power. If 10+ trash, return CP Character to hand.")
def op07_094_shave(game_state, player, card):
    """Counter: +2000 power. If 10+ trash, return CP Character to hand."""
    if player.leader:
        add_power_modifier(player.leader, 2000)
    if check_trash_count(player, 10):
        cp_chars = [c for c in player.cards_in_play if 'CP' in (c.card_origin or '')]
        if cp_chars:
            snapshot = list(cp_chars)

            def cp_return_cb(selected):
                idx = int(selected[0]) if selected else -1
                if 0 <= idx < len(snapshot):
                    t = snapshot[idx]
                    if _remove_card_instance(player.cards_in_play, t):
                        player.hand.append(t)
                        game_state._log(f"{t.name} returned to hand from Shave effect")

            return create_own_character_choice(game_state, player, cp_chars, source_card=card,
                                               optional=True,
                                               prompt="Choose your CP Character to return to hand",
                                               callback=cp_return_cb)
    return True


# --- OP07-095: Iron Body ---
@register_effect("OP07-095", "counter", "[Counter] +4000 power. If 10+ trash, +2000 more.")
def op07_095_iron_body(game_state, player, card):
    """Counter: +4000 power. If 10+ trash, additional +2000 power."""
    if player.leader:
        add_power_modifier(player.leader, 4000)
        if check_trash_count(player, 10):
            add_power_modifier(player.leader, 2000)
    return True


# --- OP07-096: Tempest Kick ---
@register_effect("OP07-096", "on_play", "[Main] Draw 1. If 10+ trash, give opponent Character -3 cost this turn.")
def op07_096_tempest_kick(game_state, player, card):
    """Main: Draw 1. If 10+ trash, give opponent's Character -3 cost this turn."""
    draw_cards(player, 1)
    if check_trash_count(player, 10):
        opponent = get_opponent(game_state, player)
        targets = list(opponent.cards_in_play)
        if targets:
            return create_cost_reduction_choice(game_state, player, targets, -3, source_card=card,
                                                min_selections=0, max_selections=1,
                                                prompt="Choose opponent's Character to give -3 cost this turn")
    return True


# --- OP07-114: He Possesses the World's Most Brilliant Mind ---
@register_effect("OP07-114", "on_play", "[Main] Look at top 5, reveal up to 1 Egghead card to hand")
def op07_114_brilliant_mind(game_state, player, card):
    """Main: Look at top 5, choose up to 1 Egghead card to add to hand."""
    return search_top_cards(game_state, player, look_count=5, add_count=1,
                            filter_fn=lambda c: 'Egghead' in (c.card_origin or '')
                                                and c.name != "He Possesses the World's Most Brilliant Mind",
                            source_card=card,
                            prompt="Look at top 5: choose up to 1 Egghead card to add to hand")


# --- OP07-115: I Re-Quasar Helllp!! ---
@register_effect("OP07-115", "counter", "[Counter] If 2 or less life, +3000 power")
def op07_115_requasar(game_state, player, card):
    """Counter: If 2 or less life, +3000 power."""
    if check_life_count(player, 2):
        target = player.leader if player.leader else (player.cards_in_play[0] if player.cards_in_play else None)
        if target:
            add_power_modifier(target, 3000)
            return True
    return False


# --- OP07-116: Blaze Slice ---
@register_effect("OP07-116", "on_play", "[Main] +1000 power to target. If opponent has 2 or less life, rest opponent cost 3 or less.")
def op07_116_blaze_slice(game_state, player, card):
    """Main: +1000 power to target. If opponent has 2 or less life, rest opponent cost 3 or less."""
    # +1000 to your leader or a character
    if player.leader:
        add_power_modifier(player.leader, 1000)
    opponent = get_opponent(game_state, player)
    if check_life_count(opponent, 2):
        targets = [c for c in opponent.cards_in_play
                   if not getattr(c, 'is_resting', False) and (getattr(c, 'cost', 0) or 0) <= 3]
        if targets:
            return create_rest_choice(game_state, player, targets, source_card=card,
                                      min_selections=0, max_selections=1,
                                      prompt="Choose opponent's cost 3 or less to rest")
    return True


# --- OP07-117: Egghead Stage ---
@register_effect("OP07-117", "end_of_turn", "[End of Turn] If 3 or less life, set Egghead cost 5 or less active")
def op07_117_egghead_stage(game_state, player, card):
    """End of Turn: If 3 or less life, set Egghead cost 5 or less Characters active."""
    if check_life_count(player, 3):
        egghead = [c for c in player.cards_in_play
                   if 'Egghead' in (c.card_origin or '').lower()
                   and (getattr(c, 'cost', 0) or 0) <= 5
                   and getattr(c, 'is_resting', False)]
        for c in egghead:
            c.is_resting = False
            game_state._log(f"Egghead Stage: {c.name} set active")
    return True


# =============================================================================
# OP07 MISSING EVENT / STAGE EFFECTS AND PRINTED TRIGGERS
# =============================================================================

@register_effect("OP07-016", "on_play", "[Main] Revolutionary Army Character +2000, then opponent Character -1000")
def op07_016_galaxy_wink(game_state, player, card):
    targets = [c for c in player.cards_in_play if 'Revolutionary Army' in (getattr(c, 'card_origin', '') or '')]
    opponent = get_opponent(game_state, player)

    def _after_buff(_selected):
        opp_targets = list(opponent.cards_in_play)
        if opp_targets:
            create_power_effect_choice(game_state, player, opp_targets, -1000, source_card=card,
                                       prompt="Galaxy Wink: Give up to 1 opponent Character -1000 power",
                                       min_selections=0)

    if targets:
        return create_power_effect_choice(game_state, player, targets, 2000, source_card=card,
                                          prompt="Galaxy Wink: Give up to 1 Revolutionary Army Character +2000 power",
                                          min_selections=0, callback=_after_buff)
    _after_buff([])
    return True


@register_effect("OP07-016", "trigger", "[Trigger] Activate this card's Main effect")
def op07_016_galaxy_wink_trigger(game_state, player, card):
    return op07_016_galaxy_wink(game_state, player, card)


@register_effect("OP07-017", "on_play", "[Main] K.O. opponent Character 3000 power or less and Stage cost 1 or less")
def op07_017_dragon_breath(game_state, player, card):
    opponent = get_opponent(game_state, player)
    char_targets = [
        c for c in opponent.cards_in_play
        if getattr(c, 'card_type', '') == 'CHARACTER'
        and (getattr(c, 'power', 0) or 0) + getattr(c, 'power_modifier', 0) <= 3000
    ]
    stage_targets = [
        c for c in opponent.cards_in_play
        if getattr(c, 'card_type', '') == 'STAGE' and (getattr(c, 'cost', 0) or 0) <= 1
    ]

    def _ko_stage_after(_selected):
        if stage_targets:
            create_ko_choice(game_state, player, stage_targets, source_card=card,
                             prompt="Dragon Breath: K.O. up to 1 opponent Stage cost 1 or less",
                             min_selections=0)

    if char_targets:
        return create_ko_choice(game_state, player, char_targets, source_card=card,
                                prompt="Dragon Breath: K.O. up to 1 opponent Character with 3000 power or less",
                                min_selections=0, callback=_ko_stage_after)
    _ko_stage_after([])
    return True


@register_effect("OP07-017", "trigger", "[Trigger] Activate this card's Main effect")
def op07_017_dragon_breath_trigger(game_state, player, card):
    return op07_017_dragon_breath(game_state, player, card)


@register_effect("OP07-018", "counter", "[Counter] Revolutionary Army Character +2000 until end of next turn")
def op07_018_keep_out(game_state, player, card):
    targets = [c for c in player.cards_in_play if 'Revolutionary Army' in (getattr(c, 'card_origin', '') or '')]
    if not targets:
        return True
    return create_power_effect_choice(game_state, player, targets, 2000, source_card=card,
                                      prompt="KEEP OUT: Choose up to 1 Revolutionary Army Character to give +2000 power",
                                      min_selections=0)


@register_effect("OP07-018", "trigger", "[Trigger] Activate this card's Counter effect")
def op07_018_keep_out_trigger(game_state, player, card):
    return op07_018_keep_out(game_state, player, card)


@register_effect("OP07-035", "counter", "[Counter] +2000 power, +1000 more if 3+ Characters")
def op07_035_karmic_punishment(game_state, player, card):
    amount = 3000 if len(player.cards_in_play) >= 3 else 2000
    targets = [player.leader] if player.leader else []
    targets += list(player.cards_in_play)
    if not targets:
        return True
    return create_power_effect_choice(game_state, player, targets, amount, source_card=card,
                                      prompt=f"Karmic Punishment: Choose up to 1 Leader/Character to give +{amount} power",
                                      min_selections=0)


@register_effect("OP07-035", "trigger", "[Trigger] K.O. up to 1 opponent rested Character cost 4 or less")
def op07_035_karmic_punishment_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if c.is_resting and (getattr(c, 'cost', 0) or 0) <= 4]
    if not targets:
        return True
    return create_ko_choice(game_state, player, targets, source_card=card,
                            prompt="[Trigger] Karmic Punishment: K.O. up to 1 opponent rested Character cost 4 or less",
                            min_selections=0)


@register_effect("OP07-036", "on_play", "[Main] Leader/Character +3000; may rest own cost 3+ to rest opponent cost 5-")
def op07_036_asura_demon(game_state, player, card):
    from ...game_engine import PendingChoice
    import uuid as _uuid
    power_targets = ([player.leader] if player.leader else []) + list(player.cards_in_play)

    def _after_power(_selected):
        own_rest_targets = [c for c in player.cards_in_play if not c.is_resting and (getattr(c, 'cost', 0) or 0) >= 3]
        opponent = get_opponent(game_state, player)
        opp_targets = [c for c in opponent.cards_in_play if not c.is_resting and (getattr(c, 'cost', 0) or 0) <= 5]
        if not own_rest_targets or not opp_targets:
            return

        def _rest_own_then_opponent(selected):
            if selected:
                idx = int(selected[0])
                if 0 <= idx < len(own_rest_targets):
                    own_rest_targets[idx].is_resting = True
                    create_rest_choice(game_state, player, opp_targets, source_card=card,
                                       prompt="Asura Demon: Rest up to 1 opponent Character cost 5 or less",
                                       min_selections=0)

        game_state.pending_choice = PendingChoice(
            choice_id=f"op07_036_{_uuid.uuid4().hex[:8]}",
            choice_type="select_cards",
            prompt="Asura Demon: You may rest 1 of your cost 3+ Characters",
            options=[{"id": str(i), "label": f"{c.name} (Cost: {getattr(c, 'cost', 0) or 0})",
                      "card_id": c.id, "card_name": c.name} for i, c in enumerate(own_rest_targets)],
            min_selections=0,
            max_selections=1,
            source_card_id=card.id,
            source_card_name=card.name,
            callback=_rest_own_then_opponent,
        )

    if power_targets:
        return create_power_effect_choice(game_state, player, power_targets, 3000, source_card=card,
                                          prompt="Asura Demon: Give up to 1 Leader/Character +3000 power",
                                          min_selections=0, callback=_after_power)
    _after_power([])
    return True


@register_effect("OP07-036", "trigger", "[Trigger] Rest up to 1 opponent Character cost 4 or less")
def op07_036_asura_demon_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if not c.is_resting and (getattr(c, 'cost', 0) or 0) <= 4]
    if not targets:
        return True
    return create_rest_choice(game_state, player, targets, source_card=card,
                              prompt="[Trigger] Asura Demon: Rest up to 1 opponent Character cost 4 or less",
                              min_selections=0)


@register_effect("OP07-055", "counter", "[Counter] +4000 power, then return up to 1 own Character to hand")
def op07_055_snake_dance(game_state, player, card):
    own_targets = [player.leader] if player.leader else []
    own_targets += list(player.cards_in_play)

    def _after_power(_selected):
        if player.cards_in_play:
            create_return_to_hand_choice(game_state, player, list(player.cards_in_play), source_card=card,
                                         prompt="Snake Dance: Return up to 1 of your Characters to hand",
                                         optional=True)

    if own_targets:
        return create_power_effect_choice(game_state, player, own_targets, 4000, source_card=card,
                                          prompt="Snake Dance: Choose up to 1 Leader/Character to give +4000 power",
                                          min_selections=0, callback=_after_power)
    _after_power([])
    return True


@register_effect("OP07-055", "trigger", "[Trigger] You may return own Character: return opponent cost 5 or less")
def op07_055_snake_dance_trigger(game_state, player, card):
    if not player.cards_in_play:
        return True
    opponent = get_opponent(game_state, player)
    opp_targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 5]

    def _return_opp_after_own(_selected):
        if opp_targets:
            create_return_to_hand_choice(game_state, player, opp_targets, source_card=card,
                                         prompt="Snake Dance Trigger: Return up to 1 opponent Character cost 5 or less",
                                         optional=True)

    return create_return_to_hand_choice(game_state, player, list(player.cards_in_play), source_card=card,
                                        prompt="Snake Dance Trigger: You may return 1 of your Characters to hand",
                                        optional=True, callback=_return_opp_after_own)


@register_effect("OP07-057", "on_play", "[Main] Seven Warlords Leader/Character +2000 and cannot be blocked this turn")
def op07_057_perfume_femur(game_state, player, card):
    targets = []
    if player.leader and 'The Seven Warlords of the Sea' in (getattr(player.leader, 'card_origin', '') or ''):
        targets.append(player.leader)
    targets.extend(c for c in player.cards_in_play if 'The Seven Warlords of the Sea' in (getattr(c, 'card_origin', '') or ''))
    if not targets:
        return True

    def _perfume_cb(selected):
        for sel in selected:
            idx = int(sel)
            if 0 <= idx < len(targets):
                target = targets[idx]
                add_power_modifier(target, 2000)
                target.opponent_cannot_activate_blocker = True
                game_state._log(f"{target.name} gets +2000 power and cannot be blocked this turn")

    return create_target_choice(game_state, player, targets,
                                "Perfume Femur: Choose up to 1 Seven Warlords Leader/Character",
                                source_card=card, min_selections=0, max_selections=1, callback=_perfume_cb)


@register_effect("OP07-057", "trigger", "[Trigger] Draw 1 card")
def op07_057_perfume_femur_trigger(game_state, player, card):
    draw_cards(player, 1)
    return True


@register_effect("OP07-058", "activate", "[Activate: Main] Trash 1 and rest Stage: return own Amazon Lily/Kuja")
def op07_058_island_of_women(game_state, player, card):
    from ...game_engine import PendingChoice
    import uuid as _uuid
    if card.is_resting or not player.hand:
        return False
    if not (player.leader and 'Kuja Pirates' in (getattr(player.leader, 'card_origin', '') or '')):
        return False
    snapshot = list(player.hand)

    def _trash_then_return(selected):
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(snapshot) and snapshot[idx] in player.hand:
            trashed = snapshot[idx]
            player.hand.remove(trashed)
            player.trash.append(trashed)
            card.is_resting = True
            game_state._log(f"Island of Women: trashed {trashed.name} and rested this Stage")
            targets = [c for c in player.cards_in_play if 'Amazon Lily' in (getattr(c, 'card_origin', '') or '') or 'Kuja Pirates' in (getattr(c, 'card_origin', '') or '')]
            if targets:
                create_return_to_hand_choice(game_state, player, targets, source_card=card,
                                             prompt="Island of Women: Return up to 1 Amazon Lily/Kuja Pirates Character",
                                             optional=True)

    game_state.pending_choice = PendingChoice(
        choice_id=f"op07_058_{_uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Island of Women: You may trash 1 card from hand and rest this Stage",
        options=[{"id": str(i), "label": f"{c.name} (Cost: {getattr(c, 'cost', 0) or 0})",
                  "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)],
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=_trash_then_return,
    )
    return True


@register_effect("OP07-075", "counter", "[Counter] DON -1: opponent Leader and Character -2000 each")
def op07_075_slow_slow_beam(game_state, player, card):
    def _slow_cb():
        opponent = get_opponent(game_state, player)
        targets = []
        if opponent.leader:
            targets.append(opponent.leader)
        targets += list(opponent.cards_in_play)
        if targets:
            create_power_effect_choice(game_state, player, targets, -2000, source_card=card,
                                       prompt="Slow-Slow Beam: Give up to 1 each opponent Leader/Character -2000 power",
                                       min_selections=0, max_selections=2)
    result = optional_don_return(game_state, player, 1, source_card=card, post_callback=_slow_cb)
    return True if not result else True


@register_effect("OP07-076", "counter", "[Counter] DON -1: +2000 power, then rest opponent Character")
def op07_076_slow_slow_beam_sword(game_state, player, card):
    def _beam_sword_cb():
        own_targets = ([player.leader] if player.leader else []) + list(player.cards_in_play)

        def _rest_after_power(_selected):
            opponent = get_opponent(game_state, player)
            if opponent.cards_in_play:
                create_rest_choice(game_state, player, list(opponent.cards_in_play), source_card=card,
                                   prompt="Slow-Slow Beam Sword: Rest up to 1 opponent Character",
                                   min_selections=0)

        if own_targets:
            create_power_effect_choice(game_state, player, own_targets, 2000, source_card=card,
                                       prompt="Slow-Slow Beam Sword: Choose up to 1 Leader/Character to give +2000 power",
                                       min_selections=0, callback=_rest_after_power)
        else:
            _rest_after_power([])
    result = optional_don_return(game_state, player, 1, source_card=card, post_callback=_beam_sword_cb)
    return True if not result else True


@register_effect("OP07-076", "trigger", "[Trigger] Add up to 1 DON from DON deck as active")
def op07_076_slow_slow_beam_sword_trigger(game_state, player, card):
    add_don_from_deck(player, 1, set_active=True)
    return True


@register_effect("OP07-078", "on_play", "[Main] If DON <= opponent DON, set up to 1 Foxy active")
def op07_078_megaton_rush(game_state, player, card):
    opponent = get_opponent(game_state, player)
    if len(player.don_pool) > len(opponent.don_pool):
        return True
    targets = [c for c in player.cards_in_play if getattr(c, 'is_resting', False) and getattr(c, 'name', '') == 'Foxy']
    if not targets:
        return True
    return create_set_active_choice(game_state, player, targets, source_card=card,
                                    prompt="Megaton Nine-Tails Rush: Set up to 1 Foxy as active")


@register_effect("OP07-078", "trigger", "[Trigger] Add up to 1 DON from DON deck as active")
def op07_078_megaton_rush_trigger(game_state, player, card):
    add_don_from_deck(player, 1, set_active=True)
    return True


@register_effect("OP07-037", "trigger", "[Trigger] Draw 1 card")
def op07_037_more_pizza_trigger(game_state, player, card):
    draw_cards(player, 1)
    return True


@register_effect("OP07-056", "trigger", "[Trigger] Draw 2, bottom 2 cards from hand")
def op07_056_slave_arrow_trigger(game_state, player, card):
    draw_cards(player, 2)
    return _bottom_cards_from_hand(game_state, player, 2, card,
                                   "Slave Arrow Trigger: Place 2 cards from hand at bottom of deck")


@register_effect("OP07-077", "trigger", "[Trigger] Activate this card's Main effect")
def op07_077_one_piece_trigger(game_state, player, card):
    return op07_077_one_piece(game_state, player, card)


@register_effect("OP07-094", "trigger", "[Trigger] Return up to 1 of your Characters to hand")
def op07_094_shave_trigger(game_state, player, card):
    if not player.cards_in_play:
        return True
    return create_return_to_hand_choice(game_state, player, list(player.cards_in_play), source_card=card,
                                        prompt="[Trigger] Shave: Return up to 1 of your Characters to hand",
                                        optional=True)


@register_effect("OP07-095", "trigger", "[Trigger] Leader/Character +1000 power this turn")
def op07_095_iron_body_trigger(game_state, player, card):
    targets = ([player.leader] if player.leader else []) + list(player.cards_in_play)
    if not targets:
        return True
    return create_power_effect_choice(game_state, player, targets, 1000, source_card=card,
                                      prompt="[Trigger] Iron Body: Choose up to 1 Leader/Character to give +1000 power",
                                      min_selections=0)


@register_effect("OP07-096", "trigger", "[Trigger] K.O. up to 1 opponent Character cost 3 or less")
def op07_096_tempest_kick_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
    if not targets:
        return True
    return create_ko_choice(game_state, player, targets, source_card=card,
                            prompt="[Trigger] Tempest Kick: K.O. up to 1 opponent Character cost 3 or less",
                            min_selections=0)


@register_effect("OP07-114", "trigger", "[Trigger] Draw 1 card")
def op07_114_brilliant_mind_trigger(game_state, player, card):
    draw_cards(player, 1)
    return True


@register_effect("OP07-115", "trigger", "[Trigger] Play up to 1 Egghead Character cost 5 or less from trash")
def op07_115_requasar_trigger(game_state, player, card):
    targets = [
        c for c in player.trash
        if getattr(c, 'card_type', '') == 'CHARACTER'
        and 'Egghead' in (getattr(c, 'card_origin', '') or '')
        and (getattr(c, 'cost', 0) or 0) <= 5
    ]
    if not targets:
        return True
    return create_play_from_trash_choice(game_state, player, targets, source_card=card, rest_on_play=False,
                                         prompt="[Trigger] I Re-Quasar Helllp!!: Play up to 1 Egghead Character cost 5 or less from trash")


@register_effect("OP07-116", "trigger", "[Trigger] Rest up to 1 opponent Character cost 4 or less")
def op07_116_blaze_slice_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if not c.is_resting and (getattr(c, 'cost', 0) or 0) <= 4]
    if not targets:
        return True
    return create_rest_choice(game_state, player, targets, source_card=card,
                              prompt="[Trigger] Blaze Slice: Rest up to 1 opponent Character cost 4 or less",
                              min_selections=0)


@register_effect("OP07-117", "trigger", "[Trigger] Play this card")
def op07_117_egghead_stage_trigger(game_state, player, card):
    return _play_this_card_from_trigger(game_state, player, card)
