"""
Hardcoded effects for OP03 cards.
"""

from ..hardcoded import (
    add_don_from_deck, add_power_modifier, check_leader_type, check_life_count,
    create_bottom_deck_choice, create_cost_reduction_choice, create_hand_discard_choice,
    create_ko_choice, create_own_character_choice, create_play_from_hand_choice,
    create_play_from_trash_choice, create_power_effect_choice,
    create_rest_choice, create_return_to_hand_choice, create_set_active_choice, create_target_choice,
    draw_cards, get_opponent, optional_don_return, register_effect, return_don_to_deck,
    search_top_cards, set_active, trash_from_hand,
)


# --- OP03-036: Out-of-the-Bag ---
@register_effect("OP03-036", "on_play", "[Main] Rest East Blue char: Set Kuro as active")
def out_of_bag_effect(game_state, player, card):
    """Rest an East Blue character to set a Kuro card as active."""
    east_blue = [c for c in player.cards_in_play
                if 'East Blue' in (c.card_origin or '')
                and not c.is_resting]
    kuro = [c for c in player.cards_in_play
           if 'Kuro' in getattr(c, 'name', '')
           and c.is_resting]
    if not east_blue or not kuro:
        return True
    # Player chooses which East Blue to rest, then which Kuro to set active
    return create_rest_choice(game_state, player, east_blue, source_card=card,
                              prompt="Choose an East Blue Character to rest (to set Kuro active)")


# --- OP03-074: Top Knot ---
@register_effect("OP03-074", "on_play", "[Main] DON!! -2: Place opponent's cost 4 or less at bottom")
def top_knot_effect(game_state, player, card):
    """Return 2 DON to deck, place opponent's cost 4 or less at bottom."""
    result = optional_don_return(game_state, player, 2, source_card=card,
                                 after_callback="op03_074_bottom_deck",
                                 after_callback_data={"source_card_id": card.id})
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
@register_effect("OP03-077", "on_attack", "[DON!! x2] [When Attacking] DON -1: If 1 or less life, add deck card to life")
def op03_077_linlin_leader(game_state, player, card):
    """DON x2, When Attacking: Return 1 DON. If 1 or less life, add deck card to life."""
    if getattr(card, 'attached_don', 0) < 2:
        return True
    result = optional_don_return(game_state, player, 1, source_card=card,
                                 after_callback="op03_077_life",
                                 after_callback_data={"source_card_id": card.id})
    if not result:
        return True  # Pending choice
    return True
    return False


# =============================================================================
# LEADER CARD EFFECTS - OP03 (Pillars of Strength)
# =============================================================================

# --- OP03-001: Portgas.D.Ace (Leader) ---
@register_effect("OP03-001", "on_attack", "[When Attack/Attacked] Trash Events/Stages: +1000 per card")
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

    game_state.pending_choice = PendingChoice(
        choice_id=f"ace_trash_{_uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Choose Event/Stage cards to trash for +1000 power each (select any number)",
        options=options,
        min_selections=0,
        max_selections=len(events_stages),
        source_card_id=card.id,
        source_card_name=card.name,
        callback_action="op03_001_trash_for_power",
        callback_data={
            "player_id": player.player_id,
            "player_index": _player_index(game_state, player),
            "source_card_id": card.id,
            "target_cards": [{"id": c.id, "name": c.name} for c in events_stages],
        }
    )
    return True


# --- OP03-021: Kuro (Leader) ---
@register_effect("OP03-021", "activate", "[Activate: Main] Rest 3 DON, rest 2 East Blue: Leader active, rest opp cost 5-")
def op03_021_kuro_leader(game_state, player, card):
    """Rest 3 DON, rest 2 East Blue Characters: Set Leader active, rest opponent's cost 5 or less."""
    active_count = player.don_pool.count("active")
    east_blue_chars = [c for c in player.cards_in_play
                       if not c.is_resting
                       and 'East Blue' in (c.card_origin or '')]
    if active_count >= 3 and len(east_blue_chars) >= 2:
        # Rest 3 DON
        rested = 0
        for i in range(len(player.don_pool)):
            if player.don_pool[i] == "active" and rested < 3:
                player.don_pool[i] = "rested"
                rested += 1
        # Rest 2 East Blue chars
        for char in east_blue_chars[:2]:
            char.is_resting = True
        card.is_resting = False
        opponent = get_opponent(game_state, player)
        opp_targets = [c for c in opponent.cards_in_play
                       if not c.is_resting and (getattr(c, 'cost', 0) or 0) <= 5]
        if opp_targets:
            return create_rest_choice(
                game_state, player, opp_targets, source_card=card,
                prompt="Choose opponent's cost 5 or less Character to rest"
            )
        return True
    return False


# --- OP03-022: Arlong (Leader) ---
@register_effect("OP03-022", "on_attack", "[DON!! x2] Rest 1: Play cost 4 or less with Trigger from hand")
def op03_022_arlong_leader(game_state, player, card):
    """DON x2, When Attacking: Return 1 DON, play cost 4 or less Character with [Trigger] from hand."""
    if getattr(card, 'attached_don', 0) < 2:
        return True
    result = optional_don_return(game_state, player, 1, source_card=card,
                                 after_callback="op03_022_play_trigger",
                                 after_callback_data={"source_card_id": card.id})
    if not result:
        return True  # Pending choice
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
    result = optional_don_return(game_state, player, 1, source_card=card,
                                 after_callback="op03_058_play_galley_la",
                                 after_callback_data={"source_card_id": card.id})
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
        trash_from_hand(player, 2, game_state, card)
        card.is_resting = False
        card.op03_076_used = True
        return True
    return False


# --- OP03-099: Charlotte Katakuri (Leader) ---
@register_effect("OP03-099", "on_attack", "[DON!! x1] Look at top Life, place top/bottom, +1000 power")
def op03_099_katakuri_leader(game_state, player, card):
    """DON x1, When Attacking: Look at top 1 of your/opponent's Life, place top/bottom, +1000 power."""
    if getattr(card, 'attached_don', 0) >= 1:
        opponent = get_opponent(game_state, player)
        # Look at opponent's life (AI always puts it at bottom)
        if opponent.life_cards:
            top_life = opponent.life_cards.pop()
            opponent.life_cards.insert(0, top_life)  # Put at bottom
        card.power_modifier = getattr(card, 'power_modifier', 0) + 1000
        return True
    return False


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
        return create_target_choice(game_state, player, targets,
                                    callback_action="attach_don_to_target",
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

    game_state.pending_choice = PendingChoice(
        choice_id=f"teach_{_uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Blackbeard: Choose a red 4000+ power Character from hand or field to trash",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback_action="trash_own_character",
        callback_data={
            "player_id": player.player_id,
            "player_index": _player_index(game_state, player),
            "source_card_id": card.id,
            "draw_after": 1,
            "power_boost_card_id": card.id,
            "power_boost_amount": 1000,
            "target_cards": [{"id": c.id, "name": c.name} for c in targets],
        }
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
    events_in_hand = [c for c in player.hand if getattr(c, 'card_type', '') == 'EVENT']
    if not events_in_hand:
        return False
    # Prompt player to select which Event to trash
    return create_hand_discard_choice(
        game_state, player, events_in_hand, source_card=card,
        callback_action="op03_013_ko_after_trash",
        prompt="Marco: Choose an Event from hand to trash to return to play rested"
    )


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
                   if (getattr(c, 'cost', 0) or 0) <= 4 and not getattr(c, 'is_resting', False)][:2]
        for t in targets:
            t.is_resting = True
    return True


# --- OP03-025: Krieg ---
@register_effect("OP03-025", "on_play", "[On Play] Trash 1: K.O. 2 rested cost 4 or less. [DON!! x1] Double Attack")
def op03_025_krieg(game_state, player, card):
    """On Play: Trash 1 to K.O. 2 rested cost 4 or less. DON x1: Double Attack."""
    if player.hand:
        trash_from_hand(player, 1, game_state, card)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play
                   if (getattr(c, 'cost', 0) or 0) <= 4 and getattr(c, 'is_resting', False)][:2]
        for t in targets:
            opponent.cards_in_play.remove(t)
            opponent.trash.append(t)
    if getattr(card, 'attached_don', 0) >= 1:
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
        # Play Buchi from hand if none in play
        has_buchi = any(getattr(c, 'name', '') == 'Buchi' for c in player.cards_in_play)
        if not has_buchi:
            for hand_card in player.hand:
                if getattr(hand_card, 'name', '') == 'Buchi':
                    player.hand.remove(hand_card)
                    player.cards_in_play.append(hand_card)
                    break
        # Rest opponent cost 2 or less
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play
                   if (getattr(c, 'cost', 0) or 0) <= 2 and not getattr(c, 'is_resting', False)]
        if targets:
            return create_rest_choice(game_state, player, targets, source_card=card,
                                     prompt="Choose opponent's cost 2 or less to rest")
    return True


# --- OP03-028: Jango ---
@register_effect("OP03-028", "on_play", "[On Play] Choose: Set East Blue cost 6 or less active OR rest this and opponent's Character")
def op03_028_jango(game_state, player, card):
    """On Play: Set East Blue cost 6 or less active OR rest this and opponent's Character."""
    targets = [c for c in player.cards_in_play
               if 'East Blue' in (c.card_origin or '') and
               (getattr(c, 'cost', 0) or 0) <= 6 and
               getattr(c, 'is_resting', False)]
    if targets:
        return create_set_active_choice(game_state, player, targets, source_card=card,
                                       prompt="Choose East Blue cost 6 or less to set active")
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


# --- OP03-042: Usopp's Pirate Crew ---
@register_effect("OP03-042", "on_play", "[On Play] Add blue Usopp from trash to hand")
def op03_042_usopp_crew(game_state, player, card):
    """On Play: Add a blue Usopp from trash to hand."""
    for trash_card in player.trash:
        if (getattr(trash_card, 'name', '') == 'Usopp' and
            'Blue' in getattr(trash_card, 'colors', [])):
            player.trash.remove(trash_card)
            player.hand.append(trash_card)
            break
    return True


# --- OP03-043: Gaimon ---
@register_effect("OP03-043", "continuous", "When dealing Life damage, may trash 3 from deck then trash this")
def op03_043_gaimon(game_state, player, card):
    """When dealing Life damage, may trash 3 from deck, then trash this Character."""
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
    if len(player.deck) <= 20:
        card.power_modifier = getattr(card, 'power_modifier', 0) + 3000
    return True


# --- OP03-047: Zeff ---
@register_effect("OP03-047", "on_play", "[On Play] Return cost 3 or less to hand, may trash 2 from deck")
def op03_047_zeff(game_state, player, card):
    """On Play: Return cost 3 or less Character to hand, may trash 2 from deck."""
    opponent = get_opponent(game_state, player)
    all_chars = list(player.cards_in_play) + list(opponent.cards_in_play)
    targets = [c for c in all_chars if (getattr(c, 'cost', 0) or 0) <= 3 and c != card]
    # Trash 2 from deck first
    for _ in range(min(2, len(player.deck))):
        if player.deck:
            player.trash.append(player.deck.pop(0))
    if targets:
        return create_return_to_hand_choice(game_state, player, targets, source_card=card,
                                           prompt="Choose cost 3 or less Character to return to hand")
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
    if player.deck:
        player.trash.append(player.deck.pop(0))
    return True


# --- OP03-051: Bell-mère ---
@register_effect("OP03-051", "on_ko", "[On K.O.] May trash 3 from top of deck")
def op03_051_bellmere(game_state, player, card):
    """On K.O.: May trash 3 cards from top of deck."""
    for _ in range(min(3, len(player.deck))):
        if player.deck:
            player.trash.append(player.deck.pop(0))
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
    result = optional_don_return(game_state, player, 1, source_card=card,
                                 after_callback="op03_059_banish",
                                 after_callback_data={"source_card_id": card.id})
    if not result:
        return True  # Pending choice
    return True


# --- OP03-060: Kalifa ---
@register_effect("OP03-060", "on_attack", "[When Attacking] DON!! -1: Draw 2, trash 1")
def op03_060_kalifa(game_state, player, card):
    """When Attacking: Return 1 DON to draw 2 and trash 1."""
    result = optional_don_return(game_state, player, 1, source_card=card,
                                 after_callback="op03_060_draw_trash",
                                 after_callback_data={"source_card_id": card.id})
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
    result = optional_don_return(game_state, player, 1, source_card=card,
                                 after_callback="op03_063_draw",
                                 after_callback_data={"source_card_id": card.id})
    if not result:
        return True  # Pending choice
    return True


# --- OP03-064: Tilestone ---
@register_effect("OP03-064", "on_ko", "[On K.O.] If Galley-La Leader, add 1 DON rested")
def op03_064_tilestone(game_state, player, card):
    """On K.O.: If Leader is Galley-La Company, add 1 DON rested."""
    if player.leader and 'Galley-La Company' in (player.leader.card_origin or ''):
        add_don_from_deck(player, 1, rested=True)
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
    """On Play: Rest 2 DON to add 1 DON active. If 8+ DON, K.O. cost 4 or less."""
    active_count = player.don_pool.count("active")
    if active_count < 2:
        return True
    # Rest 2 active DON
    rested = 0
    for i in range(len(player.don_pool)):
        if player.don_pool[i] == "active" and rested < 2:
            player.don_pool[i] = "rested"
            rested += 1
    add_don_from_deck(player, 1, rested=False)
    if len(player.don_pool) >= 8:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's cost 4 or less Character to K.O.")
    return True


# --- OP03-067: Peepley Lulu ---
@register_effect("OP03-067", "on_attack", "[DON!! x1] If Galley-La Leader, add 1 DON rested")
def op03_067_lulu(game_state, player, card):
    """DON x1: If Galley-La Leader, add 1 DON rested."""
    if getattr(card, 'attached_don', 0) >= 1:
        if player.leader and 'Galley-La Company' in (player.leader.card_origin or ''):
            add_don_from_deck(player, 1, rested=True)
        return True
    return False


# --- OP03-068: Minozebra ---
@register_effect("OP03-068", "continuous", "[Banish]")
def op03_068_minozebra_banish(game_state, player, card):
    """Banish."""
    card.has_banish = True
    return True


@register_effect("OP03-068", "on_ko", "[On K.O.] If Impel Down Leader, add 1 DON rested")
def op03_068_minozebra_ko(game_state, player, card):
    """On K.O.: If Impel Down Leader, add 1 DON rested."""
    if player.leader and 'Impel Down' in (player.leader.card_origin or ''):
        add_don_from_deck(player, 1, rested=True)
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
    result = optional_don_return(game_state, player, 1, source_card=card,
                                 after_callback="op03_070_rush",
                                 after_callback_data={"source_card_id": card.id})
    if not result:
        return True  # Pending choice
    return True


# --- OP03-071: Rob Lucci ---
@register_effect("OP03-071", "on_attack", "[When Attacking] DON!! -1: Rest opponent's cost 5 or less")
def op03_071_lucci(game_state, player, card):
    """When Attacking: Return 1 DON to rest opponent's cost 5 or less."""
    result = optional_don_return(game_state, player, 1, source_card=card,
                                 after_callback="op03_071_rest",
                                 after_callback_data={"source_card_id": card.id})
    if not result:
        return True  # Pending choice
    return True


# --- OP03-078: Issho ---
@register_effect("OP03-078", "continuous", "[DON!! x1] [Your Turn] All opponent's Characters get -3 cost")
def op03_078_issho_cont(game_state, player, card):
    """DON x1: During your turn, all opponent's Characters get -3 cost."""
    if getattr(card, 'attached_don', 0) >= 1:
        opponent = get_opponent(game_state, player)
        for c in opponent.cards_in_play:
            c.cost_modifier = getattr(c, 'cost_modifier', 0) - 3
    return True


@register_effect("OP03-078", "on_play", "[On Play] If opponent has 6+ cards in hand, trash 2 from their hand")
def op03_078_issho_play(game_state, player, card):
    """On Play: If opponent has 6+ cards in hand, trash 2 from their hand."""
    opponent = get_opponent(game_state, player)
    if len(opponent.hand) >= 6:
        for _ in range(min(2, len(opponent.hand))):
            if opponent.hand:
                card_to_trash = opponent.hand.pop()
                opponent.trash.append(card_to_trash)
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
    """On Play: Place 2 CP cards from trash at bottom of deck to K.O. cost 3 or less."""
    cp_cards = [c for c in player.trash if 'CP' in (c.card_origin or '')]
    if len(cp_cards) >= 2:
        for i in range(2):
            player.trash.remove(cp_cards[i])
            player.deck.append(cp_cards[i])
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's cost 3 or less Character to K.O.")
        return True
    return False


# --- OP03-081: Kalifa ---
@register_effect("OP03-081", "on_play", "[On Play] Draw 2, trash 2, give opponent -2 cost")
def op03_081_kalifa(game_state, player, card):
    """On Play: Draw 2, trash 2, give opponent's Character -2 cost."""
    draw_cards(player, 2)
    trash_from_hand(player, 2, game_state, card)
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

    game_state.pending_choice = PendingChoice(
        choice_id=f"corgy_trash_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Look at top 5 cards: choose up to 2 to trash. Rest go to bottom.",
        options=options,
        min_selections=0,
        max_selections=min(2, actual_look),
        source_card_id=card.id,
        source_card_name=card.name,
        callback_action="search_trash_from_top",
        callback_data={
            "player_id": player.player_id,
            "player_index": _player_index(game_state, player),
            "look_count": actual_look,
            "source_name": card.name,
            "source_id": card.id,
        }
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
                            filter_fn=filter_fn, source_card=card,
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
                            filter_fn=filter_fn, source_card=card,
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
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if not getattr(c, 'effect', None) or getattr(c, 'effect', '') == '']
    if targets:
        return create_cost_reduction_choice(game_state, player, targets, "zero", source_card=card,
                                           prompt="Choose opponent's no-effect Character to set cost to 0")
    return True


# --- OP03-092: Rob Lucci ---
@register_effect("OP03-092", "on_play", "[On Play] Place 2 CP cards from trash at bottom: Gain Rush")
def op03_092_lucci(game_state, player, card):
    """On Play: Place 2 CP cards from trash at bottom of deck to gain Rush."""
    cp_cards = [c for c in player.trash if 'CP' in (c.card_origin or '')]
    if len(cp_cards) >= 2:
        for i in range(2):
            player.trash.remove(cp_cards[i])
            player.deck.append(cp_cards[i])
        card.has_rush = True
        return True
    return False


# --- OP03-093: Wanze ---
@register_effect("OP03-093", "on_play", "[On Play] Trash 1: If CP Leader, K.O. cost 1 or less")
def op03_093_wanze(game_state, player, card):
    """On Play: Trash 1 card. If CP Leader, K.O. opponent's cost 1 or less."""
    if player.hand:
        trash_from_hand(player, 1, game_state, card)
        if player.leader and 'CP' in (player.leader.card_origin or ''):
            opponent = get_opponent(game_state, player)
            targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 1]
            if targets:
                return create_ko_choice(game_state, player, targets, source_card=card,
                                       prompt="Choose opponent's cost 1 or less Character to K.O.")
    return True


# --- OP03-102: Sanji ---
@register_effect("OP03-102", "on_attack", "[DON!! x2] Add 1 Life to hand: Add top card to Life")
def op03_102_sanji(game_state, player, card):
    """DON x2: Add 1 Life to hand, then add top deck card to Life."""
    if getattr(card, 'attached_don', 0) >= 2:
        if player.life_cards:
            life_card = player.life_cards.pop()
            player.hand.append(life_card)
        if player.deck:
            player.life_cards.append(player.deck.pop(0))
        return True
    return False


# --- OP03-104: Shirley ---
@register_effect("OP03-104", "blocker", "[Blocker]")
def op03_104_shirley_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP03-104", "on_play", "[On Play] Look at top Life, place at top or bottom")
def op03_104_shirley_play(game_state, player, card):
    """On Play: Look at top of your or opponent's Life, place at top or bottom."""
    return True


# --- OP03-105: Charlotte Oven ---
@register_effect("OP03-105", "on_attack", "[DON!! x1] Trash Trigger card: Gain +3000 power")
def op03_105_oven(game_state, player, card):
    """DON x1: Trash a Trigger card from hand to gain +3000 power."""
    if getattr(card, 'attached_don', 0) >= 1:
        for hand_card in player.hand:
            if getattr(hand_card, 'trigger', None):
                player.hand.remove(hand_card)
                player.trash.append(hand_card)
                card.power_modifier = getattr(card, 'power_modifier', 0) + 3000
                return True
    return False


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
            card.has_double_attack = True
            card.power_modifier = getattr(card, 'power_modifier', 0) + 1000
    return True


# --- OP03-109: Charlotte Chiffon ---
@register_effect("OP03-109", "on_play", "[On Play] Trash 1 Life: Add top deck card to Life")
def op03_109_chiffon(game_state, player, card):
    """On Play: May trash 1 Life to add top deck card to Life."""
    if player.life_cards:
        player.trash.append(player.life_cards.pop())
        if player.deck:
            player.life_cards.append(player.deck.pop(0))
    return True


# --- OP03-110: Charlotte Smoothie ---
@register_effect("OP03-110", "on_attack", "[When Attacking] Add 1 Life to hand: Gain +2000 power")
def op03_110_smoothie(game_state, player, card):
    """When Attacking: Add 1 Life to hand to gain +2000 power."""
    if player.life_cards:
        life_card = player.life_cards.pop()
        player.hand.append(life_card)
        card.power_modifier = getattr(card, 'power_modifier', 0) + 2000
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
@register_effect("OP03-115", "on_play", "[On Play] Trash Trigger card: K.O. cost 1 or less")
def op03_115_streusen(game_state, player, card):
    """On Play: Trash a Trigger card from hand to K.O. opponent's cost 1 or less."""
    for hand_card in player.hand:
        if getattr(hand_card, 'trigger', None):
            player.hand.remove(hand_card)
            player.trash.append(hand_card)
            opponent = get_opponent(game_state, player)
            targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 1]
            if targets:
                return create_ko_choice(game_state, player, targets, source_card=card,
                                       prompt="Choose opponent's cost 1 or less Character to K.O.")
            return True
    return False


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
@register_effect("OP03-117", "activate", "[Activate: Main] Rest: Charlotte Linlin gains +1000 until next turn")
def op03_117_napoleon(game_state, player, card):
    """Activate: Rest to give Charlotte Linlin +1000 until next turn."""
    if not getattr(card, 'is_resting', False):
        card.is_resting = True
        for c in player.cards_in_play:
            if getattr(c, 'name', '') == 'Charlotte Linlin':
                c.power_modifier = getattr(c, 'power_modifier', 0) + 1000
        if player.leader and getattr(player.leader, 'name', '') == 'Charlotte Linlin':
            player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 1000
        return True
    return False


@register_effect("OP03-117", "trigger", "[Trigger] Play this card")
def op03_117_napoleon_trigger(game_state, player, card):
    """Trigger: Play this card."""
    player.cards_in_play.append(card)
    return True


# --- OP03-122: Sogeking ---
@register_effect("OP03-122", "on_play", "[On Play] Return cost 6 or less to hand, draw 2 trash 2")
def op03_122_sogeking(game_state, player, card):
    """On Play: Return cost 6 or less Character to hand, draw 2 and trash 2."""
    card.alt_name = 'Usopp'
    opponent = get_opponent(game_state, player)
    all_chars = list(player.cards_in_play) + list(opponent.cards_in_play)
    targets = [c for c in all_chars if (getattr(c, 'cost', 0) or 0) <= 6 and c != card]
    draw_cards(player, 2)
    trash_from_hand(player, 2, game_state, card)
    if targets:
        return create_return_to_hand_choice(game_state, player, targets, source_card=card,
                                           prompt="Choose cost 6 or less Character to return to hand")
    return True


# --- OP03-123: Charlotte Katakuri ---
@register_effect("OP03-123", "on_play", "[On Play] Add cost 8 or less Character to top/bottom of Life")
def op03_123_katakuri(game_state, player, card):
    """On Play: Add cost 8 or less Character to top or bottom of owner's Life face-up."""
    opponent = get_opponent(game_state, player)
    all_chars = list(player.cards_in_play) + list(opponent.cards_in_play)
    targets = [c for c in all_chars if (getattr(c, 'cost', 0) or 0) <= 8 and c != card]
    if targets:
        return create_bottom_deck_choice(game_state, player, targets, source_card=card,
                                        prompt="Choose cost 8 or less Character to add to Life",
                                        callback_action="add_to_life")
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
@register_effect("OP03-100", "trigger", "[Trigger] Trash 1 Life: Play this card")
def op03_100_kingbaum_trigger(game_state, player, card):
    """Trigger: Trash 1 card from your Life to play this card."""
    if player.life_cards:
        player.trash.append(player.life_cards.pop())
        player.cards_in_play.append(card)
    return True


# --- OP03-016: Flame Emperor ---
@register_effect("OP03-016", "on_play", "[Main] If Ace Leader, K.O. opponent's 8000+ power Character")
def op03_016_flame_emperor(game_state, player, card):
    """If Leader is Ace, K.O. opponent's Character with 8000 or more power."""
    if not (player.leader and 'portgas.d.ace' in (player.leader.name or '').lower()):
        return True
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if (getattr(c, 'power', 0) or 0) + getattr(c, 'power_modifier', 0) >= 8000]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                               prompt="Flame Emperor: Choose opponent's 8000+ power Character to K.O.")
    return True


# --- OP03-017: Cross Fire ---
@register_effect("OP03-017", "on_play", "[Main] If Whitebeard Pirates Leader, give opponent's card -2000 power")
def op03_017_cross_fire_main(game_state, player, card):
    """If Leader has Whitebeard Pirates, give opponent's Leader/Character -2000 power."""
    if not check_leader_type(player, "Whitebeard Pirates"):
        return True
    opponent = get_opponent(game_state, player)
    targets = list(opponent.cards_in_play)
    if opponent.leader:
        targets.append(opponent.leader)
    if targets:
        return create_power_effect_choice(game_state, player, targets, -2000, source_card=card,
                                         prompt="Cross Fire: Choose opponent's card to give -2000 power")
    return True


@register_effect("OP03-017", "counter", "[Counter] If Whitebeard Pirates Leader, give opponent's card -2000 power")
def op03_017_cross_fire_counter(game_state, player, card):
    """Counter: If Leader has Whitebeard Pirates, give opponent's Leader/Character -2000 power."""
    if not check_leader_type(player, "Whitebeard Pirates"):
        return True
    opponent = get_opponent(game_state, player)
    targets = list(opponent.cards_in_play)
    if opponent.leader:
        targets.append(opponent.leader)
    if targets:
        return create_power_effect_choice(game_state, player, targets, -2000, source_card=card,
                                         prompt="Cross Fire: Choose opponent's card to give -2000 power")
    return True


# --- OP03-018: Fire Fist ---
@register_effect("OP03-018", "on_play", "[Main] Trash 1 Event from hand: K.O. opponent's 5000 power or less")
def op03_018_fire_fist(game_state, player, card):
    """Trash 1 Event from hand to K.O. opponent's 5000 power or less Character."""
    events_in_hand = [c for c in player.hand
                      if getattr(c, 'card_type', '') == 'EVENT' and c != card]
    if not events_in_hand:
        return True
    # First, player chooses which Event to trash
    return create_hand_discard_choice(game_state, player, events_in_hand, source_card=card,
                                     callback_action="op03_018_ko_after_trash",
                                     prompt="Fire Fist: Choose an Event to trash to K.O. opponent's 5000 power or less")


# --- OP03-019: Fiery Doll ---
@register_effect("OP03-019", "on_play", "[Main] Your Leader gains +4000 power during this turn")
def op03_019_fiery_doll(game_state, player, card):
    """Your Leader gains +4000 power during this turn."""
    if player.leader:
        add_power_modifier(player.leader, 4000)
    return True


# --- OP03-037: Tooth Attack ---
@register_effect("OP03-037", "on_play", "[Main] Rest East Blue Character: K.O. rested cost 4 or less")
def op03_037_tooth_attack(game_state, player, card):
    """Rest your East Blue Character to K.O. opponent's rested cost 4 or less."""
    east_blue = [c for c in player.cards_in_play
                 if 'East Blue' in (c.card_origin or '') and not c.is_resting]
    if not east_blue:
        return True
    opponent = get_opponent(game_state, player)
    rested_targets = [c for c in opponent.cards_in_play
                      if (getattr(c, 'cost', 0) or 0) <= 4 and getattr(c, 'is_resting', False)]
    if not rested_targets:
        return True
    # Rest first East Blue char, then KO choice
    east_blue[0].is_resting = True
    return create_ko_choice(game_state, player, rested_targets, source_card=card,
                           prompt="Tooth Attack: Choose opponent's rested cost 4 or less to K.O.")


# --- OP03-038: Deathly Poison Gas Bomb MH5 ---
@register_effect("OP03-038", "on_play", "[Main] Rest up to 2 opponent's cost 2 or less Characters")
def op03_038_mh5(game_state, player, card):
    """Rest up to 2 of opponent's cost 2 or less Characters."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if (getattr(c, 'cost', 0) or 0) <= 2 and not getattr(c, 'is_resting', False)]
    if targets:
        return create_rest_choice(game_state, player, targets, source_card=card,
                                 prompt="MH5: Choose up to 2 opponent's cost 2 or less to rest")
    return True


# --- OP03-039: One, Two, Jango ---
@register_effect("OP03-039", "on_play", "[Main] Rest opponent's cost 1 or less, set 1 of your Characters active")
def op03_039_one_two_jango(game_state, player, card):
    """Rest opponent's cost 1 or less Character, set 1 of your Characters as active."""
    opponent = get_opponent(game_state, player)
    opp_targets = [c for c in opponent.cards_in_play
                   if (getattr(c, 'cost', 0) or 0) <= 1 and not getattr(c, 'is_resting', False)]
    for t in opp_targets[:1]:
        t.is_resting = True
    own_rested = [c for c in player.cards_in_play if getattr(c, 'is_resting', False)]
    if own_rested:
        return create_set_active_choice(game_state, player, own_rested, source_card=card,
                                       prompt="One, Two, Jango: Choose 1 of your Characters to set active")
    return True


# --- OP03-054: Usopp's Rubber Band of Doom!!! ---
@register_effect("OP03-054", "counter", "[Counter] +2000 power, trash 1 card from top of deck")
def op03_054_rubber_band(game_state, player, card):
    """Counter: Give Leader or Character +2000 power. Trash 1 from top of deck."""
    if player.leader:
        add_power_modifier(player.leader, 2000)
    if player.deck:
        player.trash.append(player.deck.pop(0))
    return True


# --- OP03-055: Gum-Gum Giant Gavel ---
@register_effect("OP03-055", "counter", "[Counter] Trash 1 from hand: Leader +4000 power")
def op03_055_gum_gum_gavel(game_state, player, card):
    """Counter: Trash 1 from hand to give Leader +4000 power."""
    if player.hand and player.leader:
        trash_from_hand(player, 1, game_state, card)
        add_power_modifier(player.leader, 4000)
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
    result = optional_don_return(game_state, player, 1, source_card=card,
                                 after_callback="op03_073_draw",
                                 after_callback_data={"source_card_id": card.id})
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
    add_don_from_deck(player, 1, rested=False)
    return True


# --- OP03-095: Soap Sheep ---
@register_effect("OP03-095", "on_play", "[Main] Give up to 2 opponent's Characters -2 cost")
def op03_095_soap_sheep(game_state, player, card):
    """Give up to 2 of opponent's Characters -2 cost during this turn."""
    opponent = get_opponent(game_state, player)
    if opponent.cards_in_play:
        return create_cost_reduction_choice(game_state, player, list(opponent.cards_in_play), -2,
                                           source_card=card,
                                           prompt="Soap Sheep: Choose up to 2 opponent's Characters to give -2 cost")
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
               if (getattr(c, 'cost', 0) or 0) <= 6]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                               prompt="Buzz Cut Mochi: Choose opponent's cost 6 or less Character to K.O.")
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

