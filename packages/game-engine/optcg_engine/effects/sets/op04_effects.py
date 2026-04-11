"""
Hardcoded effects for OP04 cards.
"""

import random

from ..effect_registry import (
    add_don_from_deck, create_bottom_deck_choice, create_cost_reduction_choice,
    create_hand_discard_choice, create_ko_choice, create_rest_choice, create_return_to_hand_choice,
    create_mode_choice, create_play_from_trash_choice, create_power_effect_choice, create_trash_choice,
    create_set_active_choice, create_target_choice, add_power_modifier, check_life_count, give_don_to_card,
    draw_cards, get_characters_by_cost, get_characters_by_type, get_opponent, optional_don_return,
    register_effect, search_top_cards, trash_from_hand,
)


def _own_leader_and_characters(player):
    targets = list(player.cards_in_play)
    if player.leader:
        targets.insert(0, player.leader)
    return targets


def _opponent_leader_and_characters(game_state, player):
    opponent = get_opponent(game_state, player)
    targets = list(opponent.cards_in_play)
    if opponent.leader:
        targets.insert(0, opponent.leader)
    return targets


def _all_characters(game_state):
    return list(game_state.player1.cards_in_play) + list(game_state.player2.cards_in_play)


def _rested_don_cards(player):
    return [d for d in getattr(player, 'don_pool', []) if hasattr(d, 'is_resting') and d.is_resting]


def _return_active_don_to_deck(player):
    for don in list(getattr(player, 'don_pool', [])):
        if hasattr(don, 'is_resting') and not don.is_resting:
            player.don_pool.remove(don)
            if hasattr(player, 'don_deck'):
                player.don_deck.append(don)
            return True
    return False


def _rest_active_don(player, count):
    if player.don_pool.count("active") < count:
        return False
    rested = 0
    for idx, don in enumerate(list(player.don_pool)):
        if don == "active":
            player.don_pool[idx] = "rested"
            rested += 1
            if rested == count:
                return True
    return False


def _set_rested_don_active(player, count):
    activated = 0
    for idx, don in enumerate(list(player.don_pool)):
        if don == "rested":
            player.don_pool[idx] = "active"
            activated += 1
            if activated == count:
                break
    return activated


def _active_don_count(player):
    return sum(1 for don in getattr(player, 'don_pool', []) if don == "active")


def _rest_one_opponent_active_don(game_state, player):
    opponent = get_opponent(game_state, player)
    for idx, don in enumerate(list(getattr(opponent, 'don_pool', []))):
        if don == "active":
            opponent.don_pool[idx] = "rested"
            return True
    return False


def _choose_own_don_by_state(game_state, player, state, count, prompt, callback, source_card=None, min_selections=None):
    from ...game_engine import PendingChoice

    indices = [idx for idx, don in enumerate(getattr(player, 'don_pool', [])) if don == state]
    if len(indices) < count:
        return False

    options = [{"id": str(idx), "label": f"DON!! {idx + 1} ({state})"} for idx in indices]
    game_state.pending_choice = PendingChoice(
        choice_id=f"don_{state}_{len(indices)}_{count}",
        choice_type="select_cards",
        prompt=prompt,
        options=options,
        min_selections=count if min_selections is None else min_selections,
        max_selections=count,
        source_card_id=source_card.id if source_card else None,
        source_card_name=source_card.name if source_card else None,
        callback=callback,
    )
    return True


def _choose_player_don_by_state(
    game_state,
    acting_player,
    target_player,
    state,
    prompt,
    callback,
    source_card=None,
    min_selections=1,
    max_selections=1,
    owner_label="Your",
):
    from ...game_engine import PendingChoice

    indices = [idx for idx, don in enumerate(getattr(target_player, 'don_pool', [])) if don == state]
    if len(indices) < min_selections or not indices:
        return False

    allowed = min(max_selections, len(indices))
    options = [{"id": str(idx), "label": f"{owner_label} DON!! {idx + 1} ({state})"} for idx in indices]
    game_state.pending_choice = PendingChoice(
        choice_id=f"don_{state}_{len(indices)}_{allowed}",
        choice_type="select_cards",
        prompt=prompt,
        options=options,
        min_selections=min_selections,
        max_selections=allowed,
        source_card_id=source_card.id if source_card else None,
        source_card_name=source_card.name if source_card else None,
        callback=callback,
    )
    return True


def _set_selected_don_state(player, selected, expected_state, new_state):
    changed = 0
    for sel in selected:
        idx = int(sel) if sel is not None else -1
        if 0 <= idx < len(getattr(player, 'don_pool', [])) and player.don_pool[idx] == expected_state:
            player.don_pool[idx] = new_state
            changed += 1
    return changed


def _create_option_prompt(
    game_state,
    player,
    options,
    prompt,
    callback,
    source_card=None,
    choice_type="select_mode",
    min_selections=1,
    max_selections=1,
):
    from ...game_engine import PendingChoice

    if not options:
        return False

    game_state.pending_choice = PendingChoice(
        choice_id=f"option_{random.randint(1000, 999999)}",
        choice_type=choice_type,
        prompt=prompt,
        options=options,
        min_selections=min_selections,
        max_selections=max_selections,
        source_card_id=source_card.id if source_card else None,
        source_card_name=source_card.name if source_card else None,
        callback=callback,
    )
    return True


def _prompt_optional_yes_no(game_state, player, card, prompt, yes_label, callback):
    return create_mode_choice(
        game_state,
        player,
        modes=[
            {"id": "yes", "label": yes_label},
            {"id": "no", "label": "Do not use effect"},
        ],
        source_card=card,
        prompt=prompt,
        callback=callback,
    )


def _active_opponent_characters_by_cost(game_state, player, max_cost):
    opponent = get_opponent(game_state, player)
    return [
        c for c in opponent.cards_in_play
        if (getattr(c, 'cost', 0) or 0) <= max_cost and not getattr(c, 'is_resting', False)
    ]


def _rest_selected_targets(game_state, targets, selected):
    rested_any = False
    for sel in selected:
        idx = int(sel) if sel is not None else -1
        if 0 <= idx < len(targets):
            targets[idx].is_resting = True
            rested_any = True
            game_state._log(f"{targets[idx].name} was rested")
    return rested_any


def _rest_selected_don_with_optional_followup(
    game_state,
    player,
    card,
    don_count,
    next_step,
    prompt,
):
    if player.don_pool.count("active") < don_count:
        return False

    def pay_cost(selected):
        if not selected or selected[0] != "yes":
            return

        def rest_don(chosen_don):
            if _set_selected_don_state(player, chosen_don, "active", "rested") == don_count:
                next_step()

        _choose_own_don_by_state(
            game_state,
            player,
            "active",
            don_count,
            f"Choose {don_count} of your active DON!! cards to rest",
            rest_don,
            source_card=card,
        )

    return _prompt_optional_yes_no(game_state, player, card, prompt, f"Rest {don_count} DON!!", pay_cost)


def _sync_kung_fu_jugon_blockers(player):
    jugons = [c for c in player.cards_in_play if getattr(c, 'name', '') == 'Kung Fu Jugon']
    has_pair = len(jugons) >= 2
    for jugon in jugons:
        jugon._continuous_blocker = has_pair
        jugon.has_blocker = has_pair or getattr(jugon, '_innate_blocker', False)


def _trash_top_cards(player, count):
    for _ in range(min(count, len(player.deck))):
        player.trash.append(player.deck.pop(0))


def _card_colors(card):
    colors = getattr(card, 'colors', None)
    if isinstance(colors, str):
        return [colors]
    if isinstance(colors, (list, tuple, set)):
        return list(colors)
    color = getattr(card, 'color', None)
    return [color] if color else []


def check_trash_count(player, count: int, op: str = 'ge') -> bool:
    trash_count = len(getattr(player, 'trash', []))
    if op == 'ge':
        return trash_count >= count
    if op == 'gt':
        return trash_count > count
    if op == 'eq':
        return trash_count == count
    if op == 'lt':
        return trash_count < count
    return trash_count <= count


def ko_opponent_character(game_state, player, max_cost: int, source_card=None):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= max_cost]
    if targets:
        return create_ko_choice(
            game_state, player, targets, source_card=source_card,
            prompt=f"Choose opponent's cost {max_cost} or less Character to K.O."
        )
    return True


def create_power_reduction_choice(
    game_state, player, targets, amount, source_card=None, prompt=None,
    callback=None, min_selections=1, max_selections=1
):
    return create_power_effect_choice(
        game_state, player, targets, amount, source_card=source_card, prompt=prompt,
        callback=callback, min_selections=min_selections, max_selections=max_selections
    )


def create_power_boost_choice(
    game_state, player, targets, amount, source_card=None, prompt=None,
    callback=None, min_selections=1, max_selections=1
):
    return create_power_effect_choice(
        game_state, player, targets, amount, source_card=source_card, prompt=prompt,
        callback=callback, min_selections=min_selections, max_selections=max_selections
    )


def create_attack_active_choice(game_state, player, targets, source_card=None, prompt=None, min_selections=1, max_selections=1):
    snapshot = list(targets)

    def callback(selected):
        for sel in selected:
            target_idx = int(sel) if sel is not None else -1
            if 0 <= target_idx < len(snapshot):
                snapshot[target_idx].can_attack_active = True
                game_state._log(f"{snapshot[target_idx].name} can attack active Characters this turn")

    return create_target_choice(
        game_state, player, snapshot, prompt or "Choose a Character to attack active Characters",
        source_card=source_card, callback=callback,
        min_selections=min_selections, max_selections=max_selections
    )


def create_cannot_attack_choice(game_state, player, targets, source_card=None, prompt=None, min_selections=1, max_selections=1):
    snapshot = list(targets)

    def callback(selected):
        for sel in selected:
            target_idx = int(sel) if sel is not None else -1
            if 0 <= target_idx < len(snapshot):
                snapshot[target_idx].cannot_attack = True
                snapshot[target_idx].cannot_attack_until_turn = game_state.turn_count + 1
                game_state._log(f"{snapshot[target_idx].name} cannot attack until the start of your next turn")

    return create_target_choice(
        game_state, player, snapshot, prompt or "Choose a Character that cannot attack",
        source_card=source_card, callback=callback,
        min_selections=min_selections, max_selections=max_selections
    )


def _pay_active_leader_power_cost(game_state, player, amount=5000):
    leader = getattr(player, 'leader', None)
    if leader is None or getattr(leader, 'is_resting', False):
        return False
    add_power_modifier(leader, -amount)
    leader.power_modifier_expires_on_turn = game_state.turn_count
    leader._sticky_power_modifier_expires_on_turn = game_state.turn_count
    game_state._log(f"{leader.name} gets -{amount} power during this turn")
    return True


def _field_card_owner(game_state, target):
    for participant in (game_state.player1, game_state.player2):
        if target in participant.cards_in_play:
            return participant
    return None


def _move_field_card_to_bottom_of_owner_deck(game_state, target):
    owner = _field_card_owner(game_state, target)
    if owner and target in owner.cards_in_play:
        owner.cards_in_play.remove(target)
        owner.deck.append(target)
        game_state._log(f"{target.name} was placed at the bottom of the deck")
        return True
    return False


def _return_field_card_to_owner_hand(game_state, target):
    owner = _field_card_owner(game_state, target)
    if owner and target in owner.cards_in_play:
        owner.cards_in_play.remove(target)
        owner.hand.append(target)
        game_state._log(f"{target.name} returned to hand")
        return True
    return False


def _play_card_from_trash(game_state, player, target, rest_on_play=False):
    if target not in player.trash:
        return False
    player.trash.remove(target)
    target.is_resting = rest_on_play
    setattr(target, 'played_turn', game_state.turn_count)
    player.cards_in_play.append(target)
    game_state._apply_keywords(target)
    game_state._recalc_continuous_effects()
    game_state._log(f"{player.name} played {target.name} from trash")
    return True


def _prompt_exact_hand_trash(game_state, player, count, source_card, prompt, after_callback=None):
    from ...game_engine import PendingChoice

    required = min(count, len(player.hand))
    if required <= 0:
        if after_callback:
            after_callback([])
        return True

    hand_snapshot = list(player.hand)
    options = [
        {
            "id": str(i),
            "label": f"{card.name} (Cost: {card.cost or 0})",
            "card_id": card.id,
            "card_name": card.name,
        }
        for i, card in enumerate(hand_snapshot)
    ]

    def callback(selected):
        trashed = []
        for idx in sorted((int(sel) for sel in selected), reverse=True):
            if 0 <= idx < len(hand_snapshot):
                target = hand_snapshot[idx]
                if target in player.hand:
                    player.hand.remove(target)
                    player.trash.append(target)
                    trashed.append(target)
                    game_state._log(f"{player.name} trashed {target.name}")
        if after_callback:
            after_callback(list(reversed(trashed)))

    game_state.pending_choice = PendingChoice(
        choice_id=f"trash_{random.randint(1000, 999999)}",
        choice_type="select_cards",
        prompt=prompt,
        options=options,
        min_selections=required,
        max_selections=required,
        source_card_id=source_card.id if source_card else None,
        source_card_name=source_card.name if source_card else None,
        callback=callback,
    )
    return True


def _add_top_deck_to_life(game_state, player, *, log_card_name=False):
    if not player.deck:
        return None
    life_card = player.deck.pop(0)
    player.life_cards.append(life_card)
    if log_card_name:
        game_state._log(f"{player.name} added {life_card.name} from the top of deck to Life")
    else:
        game_state._log(f"{player.name} added a card from the top of deck to Life")
    return life_card


def _grant_double_attack_for_turn(game_state, target):
    target.has_doubleattack = True
    target.has_double_attack = True
    target._temp_doubleattack = True
    game_state._log(f"{target.name} gains Double Attack during this turn")


def _prompt_take_life_top_or_bottom_to_hand(
    game_state,
    player,
    source_card,
    prompt,
    after_callback,
    *,
    reveal_card_names=True,
):
    life_cards = list(player.life_cards)
    if not life_cards:
        after_callback(False, None)
        return True

    top_label = "Top of Life"
    bottom_label = "Bottom of Life"
    if reveal_card_names:
        top_label = f"{top_label} ({life_cards[-1].name})"
        if len(life_cards) > 1:
            bottom_label = f"{bottom_label} ({life_cards[0].name})"

    options = [{"id": "top", "label": top_label}]
    if len(life_cards) > 1:
        options.append({"id": "bottom", "label": bottom_label})

    def callback(selected):
        choice = selected[0] if selected else None
        if choice == "bottom" and len(player.life_cards) > 1:
            chosen = player.life_cards.pop(0)
        else:
            chosen = player.life_cards.pop() if player.life_cards else None
        if chosen is None:
            after_callback(False, None)
            return
        player.hand.append(chosen)
        game_state._log(f"{player.name} added {chosen.name} from Life to hand")
        after_callback(True, chosen)

    return _create_option_prompt(
        game_state,
        player,
        options,
        prompt,
        callback,
        source_card=source_card,
    )


# =============================================================================
# LEADER CARD EFFECTS - OP04 (Kingdoms of Intrigue)
# =============================================================================

# --- OP04-001: Nefeltari Vivi (Leader) ---
@register_effect("OP04-001", "continuous", "This Leader cannot attack")
def op04_001_vivi_continuous(game_state, player, card):
    """This Leader cannot attack."""
    card.cannot_attack = True
    return True


@register_effect("OP04-001", "activate", "[Activate: Main] Rest 2: Draw 1, if 0 chars opponent trashes")
def op04_001_vivi_activate(game_state, player, card):
    """Once Per Turn, Rest 2: Draw 1 card and up to 1 of your Characters gains Rush this turn."""
    if hasattr(card, 'op04_001_used') and card.op04_001_used:
        return False
    targets = list(player.cards_in_play)

    def rush_callback(selected):
        target_idx = int(selected[0]) if selected else -1
        if 0 <= target_idx < len(targets):
            target = targets[target_idx]
            target.has_rush = True
            target._temporary_rush_until_turn = game_state.turn_count
            game_state._log(f"{target.name} gains Rush during this turn")

    def don_callback(selected):
        chosen = sorted((int(sel) for sel in selected), reverse=True)
        if len(chosen) != 2:
            return
        for idx in chosen:
            if 0 <= idx < len(player.don_pool) and player.don_pool[idx] == "active":
                player.don_pool[idx] = "rested"
        draw_cards(player, 1)
        card.op04_001_used = True
        if targets:
            create_target_choice(
                game_state, player, targets,
                "Choose up to 1 of your Characters to gain Rush during this turn",
                source_card=card, min_selections=0, max_selections=1, callback=rush_callback
            )

    return _choose_own_don_by_state(
        game_state, player, "active", 2,
        "Choose 2 of your active DON!! cards to rest",
        don_callback, source_card=card
    )


# --- OP04-019: Donquixote Doflamingo (Leader) ---
@register_effect("OP04-019", "end_of_turn", "[End of Your Turn] Set up to 2 DON active")
def op04_019_doffy_leader(game_state, player, card):
    """End of Your Turn: Set up to 2 of your DON cards as active."""
    rested_indices = [idx for idx, don in enumerate(player.don_pool) if don == "rested"]
    if not rested_indices:
        return True

    def callback(selected):
        for sel in selected:
            idx = int(sel)
            if 0 <= idx < len(player.don_pool) and player.don_pool[idx] == "rested":
                player.don_pool[idx] = "active"

    return _choose_own_don_by_state(
        game_state, player, "rested", min(2, len(rested_indices)),
        "Choose up to 2 of your rested DON!! cards to set as active",
        callback, source_card=card, min_selections=0
    )


# --- OP04-020: Issho (Leader) ---
@register_effect("OP04-020", "continuous", "[DON!! x1] [Your Turn] Opponent chars -1 cost")
def op04_020_issho_continuous(game_state, player, card):
    """DON x1, Your Turn: Give all opponent's Characters -1 cost."""
    if game_state.current_player is player and getattr(card, 'attached_don', 0) >= 1:
        opponent = get_opponent(game_state, player)
        for char in opponent.cards_in_play:
            char.cost_modifier = getattr(char, 'cost_modifier', 0) - 1
        return True
    return False


@register_effect("OP04-020", "end_of_turn", "[End of Your Turn] Rest 1: Set active cost 5 or less")
def op04_020_issho_eot(game_state, player, card):
    """End of Your Turn, Rest 1: Set up to 1 of your Characters with cost 5 or less as active."""
    def don_callback(selected):
        if not selected:
            return
        don_idx = int(selected[0])
        if 0 <= don_idx < len(player.don_pool) and player.don_pool[don_idx] == "active":
            player.don_pool[don_idx] = "rested"
        targets = [
            c for c in player.cards_in_play
            if getattr(c, 'is_resting', False) and (getattr(c, 'cost', 0) or 0) <= 5
        ]
        if targets:
            create_set_active_choice(
                game_state, player, targets, source_card=card,
                prompt="Choose up to 1 of your cost 5 or less Characters to set active",
                min_selections=0,
            )

    return _choose_own_don_by_state(
        game_state, player, "active", 1,
        "Choose 1 of your active DON!! cards to rest",
        don_callback, source_card=card
    )


# --- OP04-039: Rebecca (Leader) ---
@register_effect("OP04-039", "continuous", "This Leader cannot attack")
def op04_039_rebecca_continuous(game_state, player, card):
    """This Leader cannot attack."""
    card.cannot_attack = True
    return True


@register_effect("OP04-039", "activate", "[Activate: Main] Rest 1: If 6 or less hand, look at 2")
def op04_039_rebecca_activate(game_state, player, card):
    """Once Per Turn, Rest 1: If you have 6 or less cards in hand, look at 2 and add 1 Dressrosa, trash rest."""
    if hasattr(card, 'op04_039_used') and card.op04_039_used:
        return False
    if len(player.hand) <= 6 and _rest_active_don(player, 1):
        card.op04_039_used = True
        return search_top_cards(
            game_state, player, look_count=2, add_count=1,
            filter_fn=lambda c: 'dressrosa' in (c.card_origin or '').lower(),
            source_card=card,
            prompt="Look at the top 2 cards: reveal up to 1 Dressrosa card to add to hand",
            trash_rest=True,
        )
    return False


# --- OP04-040: Queen (Leader) ---
@register_effect("OP04-040", "on_attack", "[DON!! x1] If 4- life+hand, draw 1. If cost 8+ char, +1000")
def op04_040_queen_leader(game_state, player, card):
    """DON x1, When Attacking: If 4 or less life+hand, draw 1 or add top deck to Life if you have a cost 8+ Character."""
    if getattr(card, 'attached_don', 0) >= 1:
        total = len(player.life_cards) + len(player.hand)
        if total > 4:
            return False
        has_cost_8_plus = any((getattr(c, 'cost', 0) or 0) >= 8 for c in player.cards_in_play)
        if not player.deck:
            return True
        if not has_cost_8_plus:
            draw_cards(player, 1)
            return True

        def callback(selected):
            mode = selected[0] if selected else "draw"
            if mode == "life" and has_cost_8_plus and player.deck:
                _add_top_deck_to_life(game_state, player, log_card_name=False)
                return
            draw_cards(player, 1)

        options = [{"id": "draw", "label": "Draw 1 card"}]
        if has_cost_8_plus and player.deck:
            options.append({"id": "life", "label": "Add top card to Life"})
        return _create_option_prompt(
            game_state,
            player,
            options=options,
            prompt="Choose Queen's effect",
            callback=callback,
            source_card=card,
        )
    return False


# --- OP04-058: Crocodile (Leader) ---
@register_effect("OP04-058", "on_don_return", "[Opponent's Turn] When DON returned, add 1 DON active")
def op04_058_croc_leader(game_state, player, card):
    """Opponent's Turn, Once Per Turn: When DON returned to deck by your effect, add 1 DON active."""
    if game_state.current_player is player or getattr(card, 'op04_058_used', False):
        return False
    if add_don_from_deck(player, 1, set_active=True):
        card.op04_058_used = True
        game_state._log(f"{card.name}: Added up to 1 DON!! card and set it as active")
        return True
    return False


# =============================================================================
# OP04 CHARACTER EFFECTS - Kingdoms of Intrigue
# =============================================================================

# --- OP04-002: Igaram ---
@register_effect("OP04-002", "activate", "[Activate: Main] Rest, Leader -5000: Search for Alabasta card")
def op04_002_igaram(game_state, player, card):
    """Activate: Rest this and give Leader -5000 to search for Alabasta card."""
    if not getattr(card, 'is_resting', False) and _pay_active_leader_power_cost(game_state, player, 5000):
        card.is_resting = True
        return search_top_cards(
            game_state, player, look_count=5, add_count=1,
            filter_fn=lambda c: 'alabasta' in (c.card_origin or '').lower(),
            source_card=card,
            prompt="Look at top 5: choose up to 1 Alabasta card to add to hand"
        )
    return False


# --- OP04-003: Usopp ---
@register_effect("OP04-003", "on_ko", "[On K.O.] K.O. opponent's Character with 5000 base power or less")
def op04_003_usopp(game_state, player, card):
    """On K.O.: K.O. opponent's Character with 5000 base power or less."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'power', 0) or 0) <= 5000]
    if targets:
        return create_ko_choice(
            game_state, player, targets, source_card=card,
            prompt="Choose up to 1 opponent's Character with 5000 base power or less to K.O.",
            min_selections=0,
        )
    return True


# --- OP04-004: Karoo ---
@register_effect("OP04-004", "activate", "[Activate: Main] Rest: Attach DON to Alabasta characters")
def op04_004_karoo(game_state, player, card):
    """Activate: Rest to give rested DON to each Alabasta character."""
    if not getattr(card, 'is_resting', False):
        card.is_resting = True
        alabasta_chars = [c for c in player.cards_in_play if 'Alabasta' in (c.card_origin or '')]
        max_targets = min(len(alabasta_chars), player.don_pool.count("rested"))
        if max_targets <= 0:
            return True

        def callback(selected):
            for sel in selected:
                idx = int(sel)
                if 0 <= idx < len(alabasta_chars):
                    target = alabasta_chars[idx]
                    if give_don_to_card(player, target, 1, rested_only=True):
                        game_state._log(f"{target.name} received 1 rested DON!!")

        return create_target_choice(
            game_state, player, alabasta_chars,
            "Choose any number of your Alabasta Characters to give 1 rested DON!! to",
            source_card=card, min_selections=0, max_selections=max_targets, callback=callback
        )
    return False


# --- OP04-005: Kung Fu Jugon ---
@register_effect("OP04-005", "continuous", "Gains Blocker if you have another Kung Fu Jugon")
def op04_005_kungfu_jugon(game_state, player, card):
    """Continuous: Gains Blocker if you have another Kung Fu Jugon."""
    _sync_kung_fu_jugon_blockers(player)
    return getattr(card, 'has_blocker', False)


# --- OP04-006: Koza ---
@register_effect("OP04-006", "on_attack", "[When Attacking] Leader -5000: This gains +2000 until next turn")
def op04_006_koza(game_state, player, card):
    """When Attacking: Leader -5000 to gain +2000 until next turn."""
    if not player.leader or getattr(player.leader, 'is_resting', False):
        return False

    def callback(selected):
        if not selected or selected[0] != "yes":
            return
        if _pay_active_leader_power_cost(game_state, player, 5000):
            add_power_modifier(card, 2000)
            card.power_modifier_expires_on_turn = game_state.turn_count + 1
            card._sticky_power_modifier_expires_on_turn = game_state.turn_count + 1

    return _prompt_optional_yes_no(
        game_state,
        player,
        card,
        "Use Koza's effect by giving your active Leader -5000 power?",
        "Leader gets -5000",
        callback,
    )


# --- OP04-008: Chaka ---
@register_effect("OP04-008", "on_attack", "[DON!! x1] [When Attacking] If Vivi Leader, -3000 then K.O. 0 power")
def op04_008_chaka(game_state, player, card):
    """When Attacking with 1 DON: If Vivi Leader, give -3000 and K.O. 0 power characters."""
    attached = getattr(card, 'attached_don', 0)
    if attached >= 1 and player.leader and 'Vivi' in getattr(player.leader, 'name', ''):
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            snapshot = list(opponent.cards_in_play)

            def callback(selected):
                target_idx = int(selected[0]) if selected else -1
                if 0 <= target_idx < len(snapshot):
                    target = snapshot[target_idx]
                    add_power_modifier(target, -3000)
                    game_state._log(f"{target.name} gets -3000 power")
                ko_targets = [
                    c for c in get_opponent(game_state, player).cards_in_play
                    if (getattr(c, 'power', 0) or 0) + getattr(c, 'power_modifier', 0) <= 0
                ]
                if ko_targets:
                    create_ko_choice(
                        game_state, player, ko_targets, source_card=card,
                        prompt="Choose up to 1 Character with 0 power or less to K.O.",
                        min_selections=0,
                    )

            return create_target_choice(
                game_state, player, snapshot,
                "Choose up to 1 opponent's Character to give -3000 power",
                source_card=card, min_selections=0, max_selections=1, callback=callback
            )
        return True
    return False


# --- OP04-009: Super Spot-Billed Duck Troops ---
@register_effect("OP04-009", "on_attack", "[When Attacking] Leader -5000: Return to hand at end of turn")
def op04_009_duck_troops(game_state, player, card):
    """When Attacking: Leader -5000 to return to hand at end of turn."""
    if not player.leader or getattr(player.leader, 'is_resting', False):
        return False

    def callback(selected):
        if not selected or selected[0] != "yes":
            return
        if _pay_active_leader_power_cost(game_state, player, 5000):
            card.return_to_hand_eot = True

    return _prompt_optional_yes_no(
        game_state,
        player,
        card,
        "Use Super Spot-Billed Duck Troops's effect by giving your active Leader -5000 power?",
        "Leader gets -5000",
        callback,
    )


# --- OP04-010: Tony Tony Chopper ---
@register_effect("OP04-010", "on_play", "[On Play] Play Animal Character with 3000 power or less")
def op04_010_chopper(game_state, player, card):
    """On Play: Play Animal character with 3000 power or less from hand."""
    targets = [c for c in player.hand if 'Animal' in (c.card_origin or '') and (getattr(c, 'power', 0) or 0) <= 3000]
    if targets:
        return create_target_choice(
            game_state, player, targets,
            "Choose up to 1 Animal type Character with 3000 power or less to play",
            source_card=card, min_selections=0, max_selections=1,
            callback=lambda selected: (
                None if not selected else (
                    player.hand.remove(targets[int(selected[0])]),
                    player.cards_in_play.append(targets[int(selected[0])]),
                    setattr(targets[int(selected[0])], 'played_turn', game_state.turn_count),
                    game_state._apply_keywords(targets[int(selected[0])]),
                    game_state._log(f"{player.name} played {targets[int(selected[0])].name} from hand")
                )
            )
        )
    return True


# --- OP04-011: Nami ---
@register_effect("OP04-011", "on_attack", "[When Attacking] Reveal top card, +3000 if 6000+ power Character")
def op04_011_nami(game_state, player, card):
    """When Attacking: Reveal top card, +3000 if 6000+ power Character."""
    if not player.deck:
        return True

    revealed = player.deck.pop(0)

    def callback(_selected):
        game_state._log(f"{card.name} revealed {revealed.name}")
        if getattr(revealed, 'card_type', '').upper() == 'CHARACTER' and (getattr(revealed, 'power', 0) or 0) >= 6000:
            add_power_modifier(card, 3000)
        player.deck.append(revealed)

    return _create_option_prompt(
        game_state,
        player,
        options=[{
            "id": "0",
            "label": revealed.name,
            "card_id": revealed.id,
            "card_name": revealed.name,
        }],
        prompt="Reveal the top card of your deck",
        callback=callback,
        source_card=card,
        choice_type="select_cards",
    )


# --- OP04-012: Nefeltari Cobra ---
@register_effect("OP04-012", "continuous", "[Your Turn] Alabasta Characters gain +1000")
def op04_012_cobra(game_state, player, card):
    """Your Turn: Alabasta characters other than this gain +1000."""
    if game_state.current_player is player:
        for c in player.cards_in_play:
            if c != card and 'Alabasta' in (c.card_origin or ''):
                c.power_modifier = getattr(c, 'power_modifier', 0) + 1000
        return True
    return False


# --- OP04-013: Pell ---
@register_effect("OP04-013", "on_attack", "[DON!! x1] [When Attacking] K.O. 4000 power or less")
def op04_013_pell(game_state, player, card):
    """When Attacking with 1 DON: K.O. opponent's 4000 power or less character."""
    attached = getattr(card, 'attached_don', 0)
    if attached >= 1:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'power', 0) or 0) <= 4000]
        if targets:
            return create_ko_choice(
                game_state, player, targets, source_card=card,
                prompt="Choose up to 1 opponent's 4000 power or less Character to K.O.",
                min_selections=0,
            )
        return True
    return False


# --- OP04-014: Monkey.D.Luffy ---
@register_effect("OP04-014", "continuous", "[Banish]")
def op04_014_luffy(game_state, player, card):
    """Continuous: This character has Banish."""
    card.has_banish = True
    return True


# --- OP04-015: Roronoa Zoro ---
@register_effect("OP04-015", "on_play", "[On Play] Opponent's Character -2000 power")
def op04_015_zoro(game_state, player, card):
    """On Play: Give opponent's character -2000 power."""
    opponent = get_opponent(game_state, player)
    if opponent.cards_in_play:
        return create_power_reduction_choice(
            game_state, player, list(opponent.cards_in_play), -2000, source_card=card,
            prompt="Choose up to 1 opponent's Character to give -2000 power",
            min_selections=0,
        )
    return True


# --- OP04-016: Bad Manners Kick Course ---
@register_effect("OP04-016", "counter", "[Counter] Trash 1: Leader/Character +3000 during battle")
def op04_016_bad_manners(game_state, player, card):
    """Counter: Trash 1 card, then up to 1 Leader or Character gains +3000 during this battle."""
    if not player.hand:
        return False

    hand_snapshot = list(player.hand)
    targets = _own_leader_and_characters(player)

    def power_callback(selected):
        target_idx = int(selected[0]) if selected else -1
        if 0 <= target_idx < len(targets):
            target = targets[target_idx]
            target.power_modifier = getattr(target, 'power_modifier', 0) + 3000
            target._battle_power_modifier = getattr(target, '_battle_power_modifier', 0) + 3000
            game_state._log(f"{target.name} gets +3000 power during this battle")

    def discard_callback(selected):
        idx = int(selected[0]) if selected else -1
        if 0 <= idx < len(hand_snapshot):
            discarded = hand_snapshot[idx]
            if discarded in player.hand:
                player.hand.remove(discarded)
                player.trash.append(discarded)
                game_state._log(f"{player.name} trashed {discarded.name}")
        if targets:
            create_target_choice(
                game_state, player, targets,
                "Choose up to 1 of your Leader or Characters to gain +3000 power during this battle",
                source_card=card, min_selections=0, max_selections=1, callback=power_callback
            )

    return create_hand_discard_choice(
        game_state, player, hand_snapshot, source_card=card,
        prompt="Choose 1 card from your hand to trash",
        callback=discard_callback
    )


# --- OP04-017: Happiness Punch ---
@register_effect("OP04-017", "counter", "[Counter] Up to 1 gets -2000, then maybe another gets -1000")
def op04_017_happiness_punch(game_state, player, card):
    """Counter: Give up to 1 opponent Leader/Character -2000, then if your Leader is active give up to 1 -1000."""
    targets = _opponent_leader_and_characters(game_state, player)
    if not targets:
        return True

    snapshot = list(targets)

    def second_callback(selected):
        target_idx = int(selected[0]) if selected else -1
        if 0 <= target_idx < len(snapshot):
            add_power_modifier(snapshot[target_idx], -1000)
            game_state._log(f"{snapshot[target_idx].name} gets -1000 power during this turn")

    def first_callback(selected):
        target_idx = int(selected[0]) if selected else -1
        if 0 <= target_idx < len(snapshot):
            add_power_modifier(snapshot[target_idx], -2000)
            game_state._log(f"{snapshot[target_idx].name} gets -2000 power during this turn")
        if player.leader and not getattr(player.leader, 'is_resting', False):
            create_target_choice(
                game_state, player, snapshot,
                "Choose up to 1 opponent Leader or Character to give -1000 power during this turn",
                source_card=card, min_selections=0, max_selections=1, callback=second_callback
            )

    return create_target_choice(
        game_state, player, snapshot,
        "Choose up to 1 opponent Leader or Character to give -2000 power during this turn",
        source_card=card, min_selections=0, max_selections=1, callback=first_callback
    )


# --- OP04-018: Enchanting Vertigo Dance ---
@register_effect("OP04-018", "on_play", "[Main] If Alabasta Leader, up to 2 chars get -2000")
def op04_018_vertigo_dance(game_state, player, card):
    """Main: If your Leader has Alabasta type, give up to 2 opponent Characters -2000 during this turn."""
    if not (player.leader and 'Alabasta' in (player.leader.card_origin or '')):
        return True
    opponent = get_opponent(game_state, player)
    targets = list(opponent.cards_in_play)
    if not targets:
        return True

    def callback(selected):
        for sel in selected:
            idx = int(sel)
            if 0 <= idx < len(targets):
                add_power_modifier(targets[idx], -2000)
                game_state._log(f"{targets[idx].name} gets -2000 power during this turn")

    return create_target_choice(
        game_state, player, targets,
        "Choose up to 2 opponent Characters to give -2000 power during this turn",
        source_card=card, min_selections=0, max_selections=min(2, len(targets)), callback=callback
    )


@register_effect("OP04-016", "trigger", "[Trigger] Give up to 1 opponent Leader/Character -3000")
def op04_016_bad_manners_trigger(game_state, player, card):
    """Trigger: Give up to 1 of your opponent's Leader or Character cards -3000 power during this turn."""
    targets = _opponent_leader_and_characters(game_state, player)
    if not targets:
        return True
    return create_power_reduction_choice(
        game_state, player, targets, -3000, source_card=card,
        prompt="Choose up to 1 opponent Leader or Character to give -3000 power during this turn",
        min_selections=0,
    )


@register_effect("OP04-018", "trigger", "[Trigger] Activate this card's [Main] effect")
def op04_018_vertigo_dance_trigger(game_state, player, card):
    """Trigger: Activate this card's main effect."""
    return op04_018_vertigo_dance(game_state, player, card)


# --- OP04-021: Viola ---
@register_effect("OP04-021", "on_opponent_attack", "[On Opponent's Attack] DON -1: Rest opponent's DON")
def op04_021_viola(game_state, player, card):
    """On Opponent's Attack: Rest 1 DON to rest opponent's DON."""
    opponent = get_opponent(game_state, player)

    def next_step():
        def rest_opponent_don(selected):
            rested = _set_selected_don_state(opponent, selected, "active", "rested")
            if rested:
                game_state._log(f"{opponent.name} rested {rested} DON!! card(s)")

        if not _choose_player_don_by_state(
            game_state,
            player,
            opponent,
            "active",
            "Choose up to 1 of your opponent's active DON!! cards to rest",
            rest_opponent_don,
            source_card=card,
            min_selections=0,
            max_selections=1,
            owner_label="Opponent's",
        ):
            game_state._log(f"{card.name}'s effect resolved with no opponent DON!! to rest")

    return _rest_selected_don_with_optional_followup(
        game_state,
        player,
        card,
        2,
        next_step,
        "Use Viola's effect by resting 2 DON!!?",
    )


# --- OP04-022: Eric ---
@register_effect("OP04-022", "activate", "[Activate: Main] Rest: Rest opponent's cost 1 or less Character")
def op04_022_eric(game_state, player, card):
    """Activate: Rest to rest opponent's cost 1 or less character."""
    if not getattr(card, 'is_resting', False):
        card.is_resting = True
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 1]
        if targets:
            return create_rest_choice(
                game_state, player, targets, source_card=card,
                prompt="Choose up to 1 opponent's cost 1 or less Character to rest",
                min_selections=0,
            )
        return True
    return False


# --- OP04-024: Sugar ---
@register_effect("OP04-024", "on_play", "[On Play] Rest opponent's cost 4 or less Character")
def op04_024_sugar_play(game_state, player, card):
    """On Play: Rest opponent's cost 4 or less character."""
    targets = _active_opponent_characters_by_cost(game_state, player, 4)
    if targets:
        return create_rest_choice(
            game_state, player, targets, source_card=card,
            prompt="Choose up to 1 opponent's cost 4 or less Character to rest",
            min_selections=0,
        )
    return True


@register_effect("OP04-024", "on_opponent_play", "[Opponent's Turn] When opponent plays Character, rest one and this")
def op04_024_sugar_opp_turn(game_state, player, card):
    """Opponent's Turn: When opponent plays character, rest one and this."""
    if not getattr(card, 'op04_024_used', False):
        if player.leader and 'Donquixote Pirates' in (player.leader.card_origin or ''):
            card.op04_024_used = True
            targets = _active_opponent_characters_by_cost(game_state, player, 99)
            if targets:
                snapshot = list(targets)

                def callback(selected):
                    _rest_selected_targets(game_state, snapshot, selected)
                    card.is_resting = True
                    game_state._log(f"{card.name} was rested")

                return create_rest_choice(
                    game_state, player, snapshot, source_card=card,
                    prompt="Choose up to 1 opponent's Character to rest",
                    min_selections=0, callback=callback
                )
            card.is_resting = True
            game_state._log(f"{card.name} was rested")
            return True
    return False


# --- OP04-025: Giolla ---
@register_effect("OP04-025", "on_opponent_attack", "[On Opponent's Attack] DON -2: Rest opponent's cost 4 or less")
def op04_025_giolla(game_state, player, card):
    """On Opponent's Attack: Rest 2 DON to rest opponent's cost 4 or less character."""
    def next_step():
        targets = _active_opponent_characters_by_cost(game_state, player, 4)
        if targets:
            create_rest_choice(
                game_state, player, targets, source_card=card,
                prompt="Choose up to 1 opponent's cost 4 or less Character to rest",
                min_selections=0,
            )

    return _rest_selected_don_with_optional_followup(
        game_state,
        player,
        card,
        2,
        next_step,
        "Use Giolla's effect by resting 2 DON!!?",
    )


# --- OP04-026: Senor Pink ---
@register_effect("OP04-026", "on_attack", "[When Attacking] DON -1: Rest cost 4 or less, active 1 DON at end")
def op04_026_senor_pink(game_state, player, card):
    """When Attacking: Rest 1 DON to rest cost 4 or less and activate 1 DON at end."""
    if not (player.leader and 'Donquixote Pirates' in (player.leader.card_origin or '')):
        return False

    def next_step():
        player.activate_don_eot_count = getattr(player, 'activate_don_eot_count', 0) + 1
        targets = _active_opponent_characters_by_cost(game_state, player, 4)
        if targets:
            create_rest_choice(
                game_state, player, targets, source_card=card,
                prompt="Choose up to 1 opponent's cost 4 or less Character to rest",
                min_selections=0,
            )

    return _rest_selected_don_with_optional_followup(
        game_state,
        player,
        card,
        1,
        next_step,
        "Use Senor Pink's effect by resting 1 DON!!?",
    )


# --- OP04-027: Daddy Masterson ---
@register_effect("OP04-027", "end_of_turn", "[DON!! x1] [End of Turn] Set active")
def op04_027_daddy_masterson(game_state, player, card):
    """End of Turn with 1 DON: Set this character active."""
    attached = getattr(card, 'attached_don', 0)
    if attached >= 1:
        card.is_resting = False
        return True
    return False


# --- OP04-028: Diamante ---
@register_effect("OP04-028", "blocker", "[Blocker]")
def op04_028_diamante_blocker(game_state, player, card):
    """Blocker ability."""
    card.has_blocker = True
    return True


@register_effect("OP04-028", "end_of_turn", "[DON!! x1] [End of Turn] If 2+ active DON, set active")
def op04_028_diamante_eot(game_state, player, card):
    """End of Turn with 1 DON: If 2+ active DON, set this active."""
    attached = getattr(card, 'attached_don', 0)
    active_don = _active_don_count(player)
    if attached >= 1 and active_don >= 2:
        card.is_resting = False
        return True
    return False


# --- OP04-029: Dellinger ---
@register_effect("OP04-029", "end_of_turn", "[End of Turn] Set 1 DON active")
def op04_029_dellinger(game_state, player, card):
    """End of Turn: Set 1 DON active."""
    player.activate_don_eot_count = getattr(player, 'activate_don_eot_count', 0) + 1
    return True


# --- OP04-030: Trebol ---
@register_effect("OP04-030", "on_play", "[On Play] K.O. opponent's rested cost 5 or less")
def op04_030_trebol_play(game_state, player, card):
    """On Play: K.O. opponent's rested character with cost 5 or less."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if getattr(c, 'is_resting', False) and (getattr(c, 'cost', 0) or 0) <= 5]
    if targets:
        return create_ko_choice(
            game_state, player, targets, source_card=card,
            prompt="Choose up to 1 opponent's rested cost 5 or less Character to K.O.",
            min_selections=0,
        )
    return True


@register_effect("OP04-030", "on_opponent_attack", "[On Opponent's Attack] DON -2: Rest cost 4 or less")
def op04_030_trebol_defense(game_state, player, card):
    """On Opponent's Attack: Rest 2 DON to rest cost 4 or less character."""
    def next_step():
        targets = _active_opponent_characters_by_cost(game_state, player, 4)
        if targets:
            create_rest_choice(
                game_state, player, targets, source_card=card,
                prompt="Choose up to 1 opponent's cost 4 or less Character to rest",
                min_selections=0,
            )

    return _rest_selected_don_with_optional_followup(
        game_state,
        player,
        card,
        2,
        next_step,
        "Use Trebol's effect by resting 2 DON!!?",
    )


# --- OP04-031: Donquixote Doflamingo ---
@register_effect("OP04-031", "on_play", "[On Play] Up to 3 opponent's rested cards skip next Refresh")
def op04_031_doflamingo(game_state, player, card):
    """On Play: Up to 3 opponent's rested cards won't refresh next turn."""
    opponent = get_opponent(game_state, player)
    rested_targets = [c for c in opponent.cards_in_play if getattr(c, 'is_resting', False)]
    if opponent.leader and getattr(opponent.leader, 'is_resting', False):
        rested_targets.insert(0, opponent.leader)
    if not rested_targets:
        return True

    snapshot = list(rested_targets)

    def callback(selected):
        for sel in selected:
            target_idx = int(sel)
            if 0 <= target_idx < len(snapshot):
                snapshot[target_idx].skip_next_refresh = True
                game_state._log(f"{snapshot[target_idx].name} will not become active next Refresh Phase")

    return create_target_choice(
        game_state, player, snapshot,
        prompt="Choose up to 3 rested Leader/Character cards that will not become active next Refresh Phase",
        source_card=card, min_selections=0, max_selections=min(3, len(snapshot)), callback=callback
    )


# --- OP04-032: Baby 5 ---
@register_effect("OP04-032", "end_of_turn", "[End of Turn] Trash this: Set 2 DON active")
def op04_032_baby5(game_state, player, card):
    """End of Turn: Trash this to set 2 DON active."""
    if card not in player.cards_in_play:
        return False

    def callback(selected):
        if not selected or selected[0] != "yes":
            return
        if card in player.cards_in_play:
            player.cards_in_play.remove(card)
            player.trash.append(card)
            player.activate_don_eot_count = getattr(player, 'activate_don_eot_count', 0) + 2
            game_state._log(f"{card.name} was trashed to set up to 2 DON!! cards as active")

    return create_mode_choice(
        game_state, player,
        modes=[
            {"id": "yes", "label": "Trash this Character"},
            {"id": "no", "label": "Do not use effect"},
        ],
        source_card=card,
        prompt="Use Baby 5's end of turn effect?",
        callback=callback,
    )


# --- OP04-033: Machvise ---
@register_effect("OP04-033", "on_play", "[On Play] If Donquixote Leader, rest cost 5 or less, activate DON at end")
def op04_033_machvise(game_state, player, card):
    """On Play: If Donquixote Leader, rest cost 5 or less and activate DON at end."""
    if player.leader and 'Donquixote Pirates' in (player.leader.card_origin or ''):
        targets = _active_opponent_characters_by_cost(game_state, player, 5)
        player.activate_don_eot_count = getattr(player, 'activate_don_eot_count', 0) + 1
        if targets:
            return create_rest_choice(
                game_state, player, targets, source_card=card,
                prompt="Choose up to 1 opponent's cost 5 or less Character to rest",
                min_selections=0,
            )
        return True
    return True


# --- OP04-034: Lao.G ---
@register_effect("OP04-034", "end_of_turn", "[End of Turn] If 3+ active DON, K.O. rested cost 3 or less")
def op04_034_lao_g(game_state, player, card):
    """End of Turn: If 3+ active DON, K.O. opponent's rested cost 3 or less."""
    active_don = _active_don_count(player)
    if active_don >= 3:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if getattr(c, 'is_resting', False) and (getattr(c, 'cost', 0) or 0) <= 3]
        if targets:
            return create_ko_choice(
                game_state, player, targets, source_card=card,
                prompt="Choose up to 1 opponent's rested cost 3 or less Character to K.O.",
                min_selections=0,
            )
        return True
    return False


# --- OP04-035: Spiderweb ---
@register_effect("OP04-035", "counter", "[Counter] +4000 power, then set up to 1 of your cards as active")
def op04_035_spiderweb_counter(game_state, player, card):
    """Counter: Give +4000 during battle, then set up to 1 of your Characters as active."""
    power_targets = _own_leader_and_characters(player)

    def set_active_step():
        ready_targets = [c for c in player.cards_in_play if getattr(c, 'is_resting', False)]
        if ready_targets:
            create_set_active_choice(
                game_state,
                player,
                ready_targets,
                source_card=card,
                prompt="Choose up to 1 of your Characters to set as active",
                min_selections=0,
            )

    def power_callback(selected):
        target_idx = int(selected[0]) if selected else -1
        if 0 <= target_idx < len(power_targets):
            target = power_targets[target_idx]
            target.power_modifier = getattr(target, 'power_modifier', 0) + 4000
            target._battle_power_modifier = getattr(target, '_battle_power_modifier', 0) + 4000
            game_state._log(f"{target.name} gets +4000 power during this battle")
        set_active_step()

    if power_targets:
        return create_target_choice(
            game_state,
            player,
            power_targets,
            "Choose up to 1 of your Leader or Character cards to gain +4000 power during this battle",
            source_card=card,
            min_selections=0,
            max_selections=1,
            callback=power_callback,
        )
    set_active_step()
    return True


@register_effect("OP04-035", "trigger", "[Trigger] Up to 1 of your Leader gains +2000 power during this turn")
def op04_035_spiderweb_trigger(game_state, player, card):
    """Trigger: Up to 1 of your Leader gains +2000 power during this turn."""
    if player.leader:
        def callback(selected):
            if not selected or selected[0] != "0":
                return
            add_power_modifier(player.leader, 2000)
            player.leader.power_modifier_expires_on_turn = game_state.turn_count
            player.leader._sticky_power_modifier_expires_on_turn = game_state.turn_count
            game_state._log(f"{player.leader.name} gets +2000 power during this turn")

        return create_target_choice(
            game_state,
            player,
            [player.leader],
            source_card=card,
            prompt="Choose up to 1 of your Leaders to gain +2000 power during this turn",
            min_selections=0,
            max_selections=1,
            callback=callback,
        )
    return True


# --- OP04-041: Apis ---
@register_effect("OP04-041", "on_play", "[On Play] Trash 2: Look at 5, add East Blue card")
def op04_041_apis(game_state, player, card):
    """On Play: Trash 2 cards to look at 5 and add East Blue card."""
    if len(player.hand) < 2:
        return True

    def resolve_search():
        return search_top_cards(
            game_state, player, look_count=5, add_count=1,
            filter_fn=lambda c: 'east blue' in (c.card_origin or '').lower(),
            source_card=card,
            prompt="Look at top 5: choose up to 1 East Blue card to add to hand"
        )

    def pay_cost_callback(selected):
        if not selected or selected[0] != "yes":
            return
        hand_snapshot = list(player.hand)

        def callback(discard_selected):
            for idx in sorted((int(sel) for sel in discard_selected), reverse=True):
                if 0 <= idx < len(hand_snapshot):
                    discarded = hand_snapshot[idx]
                    if discarded in player.hand:
                        player.hand.remove(discarded)
                        player.trash.append(discarded)
                        game_state._log(f"{player.name} trashed {discarded.name}")
            resolve_search()

        _create_option_prompt(
            game_state,
            player,
            options=[
                {
                    "id": str(i),
                    "label": f"{hand_card.name} (Cost: {hand_card.cost or 0})",
                    "card_id": hand_card.id,
                    "card_name": hand_card.name,
                }
                for i, hand_card in enumerate(hand_snapshot)
            ],
            prompt="Choose 2 cards from your hand to trash",
            callback=callback,
            source_card=card,
            choice_type="select_cards",
            min_selections=2,
            max_selections=2,
        )

    return create_mode_choice(
        game_state, player,
        modes=[
            {"id": "yes", "label": "Trash 2 cards"},
            {"id": "no", "label": "Do not use effect"},
        ],
        source_card=card,
        prompt="Use Apis's effect?",
        callback=pay_cost_callback,
    )


# --- OP04-042: Ipponmatsu ---
@register_effect("OP04-042", "on_play", "[On Play] Slash attribute gains +3000, trash 1 from deck")
def op04_042_ipponmatsu(game_state, player, card):
    """On Play: Slash attribute character gains +3000, trash 1 from deck."""
    targets = [c for c in player.cards_in_play if getattr(c, 'attribute', '') == 'Slash']

    def callback(selected):
        target_idx = int(selected[0]) if selected else -1
        if 0 <= target_idx < len(targets):
            add_power_modifier(targets[target_idx], 3000)
            game_state._log(f"{targets[target_idx].name} gets +3000 power")
        _trash_top_cards(player, 1)

    if targets:
        return create_power_boost_choice(
            game_state, player, targets, 3000, source_card=card,
            prompt="Choose up to 1 of your Slash attribute Characters to give +3000 power",
            callback=callback, min_selections=0,
        )
    _trash_top_cards(player, 1)
    return True


# --- OP04-043: Ulti ---
@register_effect("OP04-043", "on_attack", "[DON!! x1] [When Attacking] Return cost 2 or less to hand/deck")
def op04_043_ulti(game_state, player, card):
    """When Attacking with 1 DON: Return cost 2 or less to hand or deck."""
    attached = getattr(card, 'attached_don', 0)
    if attached >= 1:
        targets = [c for c in _all_characters(game_state) if (getattr(c, 'cost', 0) or 0) <= 2]
        if targets:
            snapshot = list(targets)

            def target_callback(selected):
                target_idx = int(selected[0]) if selected else -1
                if not (0 <= target_idx < len(snapshot)):
                    return
                target = snapshot[target_idx]

                def mode_callback(mode_selected):
                    mode = mode_selected[0] if mode_selected else "hand"
                    for participant in [game_state.player1, game_state.player2]:
                        if target in participant.cards_in_play:
                            participant.cards_in_play.remove(target)
                            if mode == "bottom":
                                participant.deck.append(target)
                                game_state._log(f"{target.name} was placed at the bottom of deck")
                            else:
                                participant.hand.append(target)
                                game_state._log(f"{target.name} returned to hand")
                            break

                create_mode_choice(
                    game_state, player,
                    modes=[
                        {"id": "hand", "label": "Return to hand"},
                        {"id": "bottom", "label": "Place at deck bottom"},
                    ],
                    source_card=card,
                    prompt=f"Choose where to return {target.name}",
                    callback=mode_callback,
                )

            return create_target_choice(
                game_state, player, snapshot,
                "Choose up to 1 Character with cost 2 or less",
                source_card=card, min_selections=0, max_selections=1, callback=target_callback
            )
        return True
    return False


# --- OP04-044: Kaido ---
@register_effect("OP04-044", "on_play", "[On Play] Return cost 8 or less and cost 3 or less to hand")
def op04_044_kaido(game_state, player, card):
    """On Play: Return cost 8 or less and cost 3 or less characters to hand."""
    opponent = get_opponent(game_state, player)
    def step_two():
        all_chars2 = list(player.cards_in_play) + list(opponent.cards_in_play)
        targets3 = [c for c in all_chars2 if c != card and (getattr(c, 'cost', 0) or 0) <= 3]
        if targets3:
            create_return_to_hand_choice(
                game_state, player, targets3, source_card=card,
                prompt="Choose up to 1 Character with cost 3 or less to return to hand",
                optional=True,
            )

    all_chars = list(player.cards_in_play) + list(opponent.cards_in_play)
    targets8 = [c for c in all_chars if c != card and (getattr(c, 'cost', 0) or 0) <= 8]
    if not targets8:
        step_two()
        return True

    snapshot = list(targets8)

    def step_one_callback(selected):
        target_idx = int(selected[0]) if selected else -1
        if 0 <= target_idx < len(snapshot):
            target = snapshot[target_idx]
            for participant in [player, opponent]:
                if target in participant.cards_in_play:
                    participant.cards_in_play.remove(target)
                    participant.hand.append(target)
                    game_state._log(f"{target.name} returned to hand")
                    break
        step_two()

    return create_return_to_hand_choice(
        game_state, player, snapshot, source_card=card,
        prompt="Choose up to 1 Character with cost 8 or less to return to hand",
        optional=True, callback=step_one_callback
    )


# --- OP04-045: King ---
@register_effect("OP04-045", "on_play", "[On Play] Draw 1 card")
def op04_045_king(game_state, player, card):
    """On Play: Draw 1 card."""
    draw_cards(player, 1)
    return True


# --- OP04-046: Queen ---
@register_effect("OP04-046", "on_play", "[On Play] If Animal Kingdom Leader, search for Plague Rounds/Ice Oni")
def op04_046_queen(game_state, player, card):
    """On Play: If Animal Kingdom Leader, look at 7 and add Plague Rounds/Ice Oni."""
    if player.leader and 'Animal Kingdom Pirates' in (player.leader.card_origin or ''):
        return search_top_cards(
            game_state, player, look_count=7, add_count=2,
            filter_fn=lambda c: getattr(c, 'name', '') in {'Plague Rounds', 'Ice Oni'},
            source_card=card,
            prompt="Look at top 7: choose up to 2 Plague Rounds or Ice Oni cards to add to hand"
        )
    return True


# --- OP04-047: Ice Oni ---
@register_effect("OP04-047", "continuous", "[Your Turn] After battle with cost 5 or less, place at deck bottom")
def op04_047_ice_oni(game_state, player, card):
    """Your Turn: After battle with cost 5 or less, place them at deck bottom."""
    card.ice_oni_effect = game_state.current_player is player
    return True


# --- OP04-048: Sasaki ---
@register_effect("OP04-048", "on_play", "[On Play] Return hand to deck and shuffle, draw equal amount")
def op04_048_sasaki(game_state, player, card):
    """On Play: Return hand to deck, shuffle, draw equal amount."""
    hand_count = len(player.hand)
    player.deck.extend(player.hand)
    player.hand = []
    import random
    random.shuffle(player.deck)
    draw_cards(player, hand_count)
    return True


# --- OP04-049: Jack ---
@register_effect("OP04-049", "on_ko", "[On K.O.] Draw 1 card")
def op04_049_jack(game_state, player, card):
    """On K.O.: Draw 1 card."""
    draw_cards(player, 1)
    return True


# --- OP04-050: Hanger ---
@register_effect("OP04-050", "activate", "[Activate: Main] Trash 1 and rest: Draw 1")
def op04_050_hanger(game_state, player, card):
    """Activate: Trash 1 from hand and rest to draw 1."""
    if not getattr(card, 'is_resting', False) and player.hand:
        card.is_resting = True
        hand_snapshot = list(player.hand)

        def callback(selected):
            target_idx = int(selected[0]) if selected else -1
            if 0 <= target_idx < len(hand_snapshot):
                discarded = hand_snapshot[target_idx]
                if discarded in player.hand:
                    player.hand.remove(discarded)
                    player.trash.append(discarded)
                    game_state._log(f"{player.name} trashed {discarded.name}")
            draw_cards(player, 1)

        create_hand_discard_choice(
            game_state, player, hand_snapshot, source_card=card,
            prompt="Choose 1 card from your hand to trash", callback=callback
        )
        return True
    return False


# --- OP04-051: Who's Who ---
@register_effect("OP04-051", "on_play", "[On Play] Look at 5, add Animal Kingdom card")
def op04_051_whos_who(game_state, player, card):
    """On Play: Look at 5 and add Animal Kingdom card."""
    return search_top_cards(
        game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: 'animal kingdom pirates' in (c.card_origin or '').lower()
        and getattr(c, 'name', '') != "Who's Who",
        source_card=card,
        prompt="Look at top 5: choose up to 1 Animal Kingdom Pirates card other than Who's Who to add to hand"
    )


# --- OP04-052: Black Maria ---
@register_effect("OP04-052", "activate", "[Activate: Main] DON -2 and rest: Draw 1")
def op04_052_black_maria(game_state, player, card):
    """Activate: Rest 2 DON and this to draw 1."""
    if getattr(card, 'is_resting', False):
        return False

    def callback(selected):
        chosen = sorted((int(sel) for sel in selected), reverse=True)
        if len(chosen) != 2:
            return
        for idx in chosen:
            if 0 <= idx < len(player.don_pool) and player.don_pool[idx] == "active":
                player.don_pool[idx] = "rested"
        card.is_resting = True
        draw_cards(player, 1)

    return _choose_own_don_by_state(
        game_state, player, "active", 2,
        "Choose 2 of your active DON!! cards to rest",
        callback, source_card=card
    )


@register_effect("OP04-052", "trigger", "[Trigger] Play this card")
def op04_052_black_maria_trigger(game_state, player, card):
    """Trigger: Play this card."""
    player.cards_in_play.append(card)
    return True


# --- OP04-053: Page One ---
@register_effect("OP04-053", "on_event", "[DON!! x1] [Once Per Turn] When activating Event, draw 1 then bottom 1")
def op04_053_page_one(game_state, player, card):
    """With 1 DON: When activating Event, draw 1 then place 1 at deck bottom."""
    attached = getattr(card, 'attached_don', 0)
    if attached >= 1 and not getattr(card, 'op04_053_used', False):
        card.op04_053_used = True
        draw_cards(player, 1)
        if player.hand:
            hand_snapshot = list(player.hand)

            def callback(selected):
                target_idx = int(selected[0]) if selected else -1
                if 0 <= target_idx < len(hand_snapshot):
                    chosen = hand_snapshot[target_idx]
                    if chosen in player.hand:
                        player.hand.remove(chosen)
                        player.deck.append(chosen)
                        game_state._log(f"{chosen.name} was placed at the bottom of the deck")

            return create_hand_discard_choice(
                game_state, player, hand_snapshot, source_card=card,
                prompt="Choose 1 card from your hand to place at the bottom of your deck",
                callback=callback
            )
        return True
    return False


# --- OP04-055: Plague Rounds ---
@register_effect("OP04-055", "on_play", "[Main] Trash Ice Oni and bottom-deck cost 4 or less to play Ice Oni from trash")
def op04_055_plague_rounds(game_state, player, card):
    """Main: Trash 1 Ice Oni from hand and bottom-deck a cost 4 or less Character to play Ice Oni from trash."""
    ice_oni_in_hand = [c for c in player.hand if getattr(c, 'name', '') == 'Ice Oni']
    bottom_targets = [c for c in _all_characters(game_state) if (getattr(c, 'cost', 0) or 0) <= 4]
    if not ice_oni_in_hand or not bottom_targets:
        return True

    def yes_no_callback(selected):
        if not selected or selected[0] != "yes":
            return
        hand_snapshot = list(ice_oni_in_hand)

        def trash_callback(discarded):
            idx = int(discarded[0]) if discarded else -1
            if not (0 <= idx < len(hand_snapshot)):
                return
            chosen = hand_snapshot[idx]
            if chosen not in player.hand:
                return
            player.hand.remove(chosen)
            player.trash.append(chosen)
            game_state._log(f"{player.name} trashed {chosen.name}")

            live_targets = [c for c in _all_characters(game_state) if (getattr(c, 'cost', 0) or 0) <= 4]
            if not live_targets:
                return
            target_snapshot = list(live_targets)

            def bottom_callback(bottom_selected):
                target_idx = int(bottom_selected[0]) if bottom_selected else -1
                if not (0 <= target_idx < len(target_snapshot)):
                    return
                if not _move_field_card_to_bottom_of_owner_deck(game_state, target_snapshot[target_idx]):
                    return
                ice_oni_in_trash = [c for c in player.trash if getattr(c, 'name', '') == 'Ice Oni']
                if not ice_oni_in_trash:
                    return
                trash_snapshot = list(ice_oni_in_trash)

                def play_callback(play_selected):
                    play_idx = int(play_selected[0]) if play_selected else -1
                    if 0 <= play_idx < len(trash_snapshot):
                        _play_card_from_trash(game_state, player, trash_snapshot[play_idx], rest_on_play=False)

                create_target_choice(
                    game_state,
                    player,
                    trash_snapshot,
                    "Choose 1 Ice Oni from your trash to play",
                    source_card=card,
                    min_selections=1,
                    max_selections=1,
                    callback=play_callback,
                )

            create_bottom_deck_choice(
                game_state,
                player,
                target_snapshot,
                source_card=card,
                prompt="Choose 1 Character with cost 4 or less to place at the bottom of the owner's deck",
                min_selections=1,
                callback=bottom_callback,
            )

        create_hand_discard_choice(
            game_state,
            player,
            hand_snapshot,
            source_card=card,
            prompt="Choose 1 Ice Oni from your hand to trash",
            callback=trash_callback,
        )

    return _prompt_optional_yes_no(
        game_state,
        player,
        card,
        "Use Plague Rounds by trashing 1 Ice Oni from hand and bottom-decking 1 cost 4 or less Character?",
        "Use effect",
        yes_no_callback,
    )


@register_effect("OP04-055", "trigger", "[Trigger] Activate this card's [Main] effect")
def op04_055_plague_rounds_trigger(game_state, player, card):
    """Trigger: Activate this card's Main effect."""
    return op04_055_plague_rounds(game_state, player, card)


# --- OP04-056: Gum-Gum Red Roc ---
@register_effect("OP04-056", "on_play", "[Main] Place up to 1 Character at the bottom of the owner's deck")
def op04_056_red_roc(game_state, player, card):
    """Main: Place up to 1 Character at the bottom of the owner's deck."""
    targets = list(_all_characters(game_state))
    if targets:
        return create_bottom_deck_choice(
            game_state,
            player,
            targets,
            source_card=card,
            prompt="Choose up to 1 Character to place at the bottom of the owner's deck",
            min_selections=0,
        )
    return True


@register_effect("OP04-056", "trigger", "[Trigger] Place up to 1 Character with a cost of 4 or less at the bottom of the owner's deck")
def op04_056_red_roc_trigger(game_state, player, card):
    """Trigger: Place up to 1 cost 4 or less Character at the bottom of the owner's deck."""
    targets = [c for c in _all_characters(game_state) if (getattr(c, 'cost', 0) or 0) <= 4]
    if targets:
        return create_bottom_deck_choice(
            game_state,
            player,
            targets,
            source_card=card,
            prompt="Choose up to 1 Character with cost 4 or less to place at the bottom of the owner's deck",
            min_selections=0,
        )
    return True


# --- OP04-057: Dragon Twister Demolition Breath ---
@register_effect("OP04-057", "counter", "[Counter] +4000 power, then bottom-deck up to 1 cost 1 or less Character")
def op04_057_dragon_twister_counter(game_state, player, card):
    """Counter: Give +4000 during this battle, then bottom-deck up to 1 cost 1 or less Character."""
    power_targets = _own_leader_and_characters(player)

    def bottom_deck_step():
        targets = [c for c in _all_characters(game_state) if (getattr(c, 'cost', 0) or 0) <= 1]
        if targets:
            create_bottom_deck_choice(
                game_state,
                player,
                targets,
                source_card=card,
                prompt="Choose up to 1 Character with cost 1 or less to place at the bottom of the owner's deck",
                min_selections=0,
            )

    def power_callback(selected):
        if selected:
            idx = int(selected[0])
            if 0 <= idx < len(power_targets):
                target = power_targets[idx]
                target.power_modifier = getattr(target, 'power_modifier', 0) + 4000
                target._battle_power_modifier = getattr(target, '_battle_power_modifier', 0) + 4000
                game_state._log(f"{target.name} gets +4000 power during this battle")
        bottom_deck_step()

    if power_targets:
        return create_target_choice(
            game_state,
            player,
            power_targets,
            "Choose up to 1 of your Leader or Character cards to gain +4000 power during this battle",
            source_card=card,
            min_selections=0,
            max_selections=1,
            callback=power_callback,
        )
    bottom_deck_step()
    return True


@register_effect("OP04-057", "trigger", "[Trigger] Return up to 1 Character with a cost of 6 or less to the owner's hand")
def op04_057_dragon_twister_trigger(game_state, player, card):
    """Trigger: Return up to 1 cost 6 or less Character to the owner's hand."""
    targets = [c for c in _all_characters(game_state) if (getattr(c, 'cost', 0) or 0) <= 6]
    if targets:
        return create_return_to_hand_choice(
            game_state,
            player,
            targets,
            source_card=card,
            prompt="Choose up to 1 Character with cost 6 or less to return to the owner's hand",
            optional=True,
        )
    return True


# --- OP04-059: Iceburg ---
@register_effect("OP04-059", "on_opponent_attack", "[On Opponent's Attack] DON -1: Gains Blocker if Water Seven Leader")
def op04_059_iceburg(game_state, player, card):
    """On Opponent's Attack: Return 1 DON to gain Blocker if Water Seven Leader."""
    if player.leader and 'Water Seven' in (player.leader.card_origin or ''):
        def callback():
            card.has_blocker = True
            card._temporary_blocker_until_turn = game_state.turn_count
        result = optional_don_return(game_state, player, 1, source_card=card, post_callback=callback)
        if not result:
            return True
        return True
    return False


# --- OP04-060: Crocodile ---
@register_effect("OP04-060", "on_play", "[On Play] DON -2: If Baroque Works Leader, add deck to Life")
def op04_060_crocodile_play(game_state, player, card):
    """On Play: Return 2 DON to add deck card to Life if Baroque Works Leader."""
    if player.leader and 'Baroque Works' in (player.leader.card_origin or ''):
        def callback():
            if player.deck:
                life_card = player.deck.pop(0)
                player.life_cards.append(life_card)
                game_state._log(f"{player.name} added {life_card.name} from the top of deck to Life")
        result = optional_don_return(game_state, player, 2, source_card=card, post_callback=callback)
        if not result:
            return True
        return True
    return True


@register_effect("OP04-060", "on_opponent_attack", "[On Opponent's Attack] [Once Per Turn] DON -1: Draw 1, trash 1")
def op04_060_crocodile_defense(game_state, player, card):
    """On Opponent's Attack: Return 1 DON to draw 1 and trash 1."""
    if not getattr(card, 'op04_060_used', False):
        def callback():
            draw_cards(player, 1)
            trash_from_hand(player, 1, game_state, card)
            card.op04_060_used = True

        result = optional_don_return(game_state, player, 1, source_card=card, post_callback=callback)
        if not result:
            return True
        return True
    return False


# --- OP04-061: Tom ---
@register_effect("OP04-061", "activate", "[Activate: Main] Trash this: Add 1 DON if Water Seven Leader")
def op04_061_tom(game_state, player, card):
    """Activate: Trash this to add 1 DON if Water Seven Leader."""
    if player.leader and 'Water Seven' in (player.leader.card_origin or ''):
        if card in player.cards_in_play:
            def callback(selected):
                if not selected or selected[0] != "yes":
                    return
                if card in player.cards_in_play:
                    player.cards_in_play.remove(card)
                    player.trash.append(card)
                    add_don_from_deck(player, 1, set_active=False)
                    game_state._log(f"{player.name} added up to 1 rested DON!! card")

            return create_mode_choice(
                game_state, player,
                modes=[
                    {"id": "yes", "label": "Trash Tom"},
                    {"id": "no", "label": "Do not use effect"},
                ],
                source_card=card,
                prompt="Use Tom's effect?",
                callback=callback,
            )
    return False


# --- OP04-063: Franky ---
@register_effect("OP04-063", "on_opponent_attack", "[On Opponent's Attack] [Once Per Turn] DON -1: +1000 if Water Seven Leader")
def op04_063_franky(game_state, player, card):
    """On Opponent's Attack: Return 1 DON to give +1000 if Water Seven Leader."""
    if not getattr(card, 'op04_063_used', False):
        if player.leader and 'Water Seven' in (player.leader.card_origin or ''):
            def resolve_effect():
                card.op04_063_used = True
                targets = list(player.cards_in_play)
                if player.leader:
                    targets.insert(0, player.leader)
                if targets:
                    snapshot = list(targets)

                    def callback(selected):
                        target_idx = int(selected[0]) if selected else -1
                        if 0 <= target_idx < len(snapshot):
                            target = snapshot[target_idx]
                            target.power_modifier = getattr(target, 'power_modifier', 0) + 1000
                            target._battle_power_modifier = getattr(target, '_battle_power_modifier', 0) + 1000
                            game_state._log(f"{target.name} gets +1000 power during this battle")

                    create_target_choice(
                        game_state, player, snapshot,
                        "Choose up to 1 of your Leader or Characters to give +1000 power during this battle",
                        source_card=card, min_selections=0, max_selections=1, callback=callback
                    )
            result = optional_don_return(game_state, player, 1, source_card=card, post_callback=resolve_effect)
            if not result:
                return True
            return True
    return False


# --- OP04-064: Ms. All Sunday ---
@register_effect("OP04-064", "on_play", "[On Play] Add 1 DON (rested), draw 1 if 6+ DON")
def op04_064_ms_all_sunday(game_state, player, card):
    """On Play: Add 1 DON rested. Draw 1 if 6+ DON."""
    add_don_from_deck(player, 1, set_active=False)
    if len(player.don_pool) >= 6:
        draw_cards(player, 1)
    return True


@register_effect("OP04-064", "trigger", "[Trigger] DON -2: Play this card")
def op04_064_ms_all_sunday_trigger(game_state, player, card):
    """Trigger: Return 2 DON to play this card."""
    def callback():
        player.cards_in_play.append(card)
        setattr(card, 'played_turn', game_state.turn_count)
        game_state._apply_keywords(card)
        game_state._log(f"{player.name} played {card.name} from Trigger")

    result = optional_don_return(game_state, player, 2, source_card=card, post_callback=callback)
    if not result:
        return True
    return True


# --- OP04-065: Miss Goldenweek ---
@register_effect("OP04-065", "on_play", "[On Play] If Baroque Works Leader, cost 5 or less cannot attack")
def op04_065_goldenweek(game_state, player, card):
    """On Play: If Baroque Works Leader, opponent's cost 5 or less cannot attack."""
    if player.leader and 'Baroque Works' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 5]
        if targets:
            return create_cannot_attack_choice(
                game_state, player, targets, source_card=card,
                prompt="Choose up to 1 opponent's cost 5 or less Character that cannot attack",
                min_selections=0,
            )
    return True


@register_effect("OP04-065", "trigger", "[Trigger] DON -1: Play this card")
def op04_065_goldenweek_trigger(game_state, player, card):
    """Trigger: Return 1 DON to play this card."""
    def callback():
        player.cards_in_play.append(card)
        setattr(card, 'played_turn', game_state.turn_count)
        game_state._apply_keywords(card)
        game_state._log(f"{player.name} played {card.name} from Trigger")

    result = optional_don_return(game_state, player, 1, source_card=card, post_callback=callback)
    if not result:
        return True
    return True


# --- OP04-066: Miss Valentine ---
@register_effect("OP04-066", "on_play", "[On Play] Look at 5, add Baroque Works card")
def op04_066_valentine(game_state, player, card):
    """On Play: Look at 5 and add Baroque Works card."""
    return search_top_cards(
        game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: 'baroque works' in (c.card_origin or '').lower(),
        source_card=card,
        prompt="Look at the top 5 cards: reveal up to 1 Baroque Works card to add to hand"
    )


@register_effect("OP04-066", "trigger", "[Trigger] DON -1: Play this card")
def op04_066_valentine_trigger(game_state, player, card):
    """Trigger: Return 1 DON to play this card."""
    def callback():
        player.cards_in_play.append(card)
        setattr(card, 'played_turn', game_state.turn_count)
        game_state._apply_keywords(card)
        game_state._log(f"{player.name} played {card.name} from Trigger")

    result = optional_don_return(game_state, player, 1, source_card=card, post_callback=callback)
    if not result:
        return True
    return True


# --- OP04-067: Miss Merry Christmas ---
@register_effect("OP04-067", "blocker", "[Blocker]")
def op04_067_merry_christmas_blocker(game_state, player, card):
    """Blocker ability."""
    card.has_blocker = True
    return True


@register_effect("OP04-067", "trigger", "[Trigger] DON -1: Play this card")
def op04_067_merry_christmas_trigger(game_state, player, card):
    """Trigger: Return 1 DON to play this card."""
    def callback():
        player.cards_in_play.append(card)
        setattr(card, 'played_turn', game_state.turn_count)
        game_state._apply_keywords(card)
        game_state._log(f"{player.name} played {card.name} from Trigger")

    result = optional_don_return(game_state, player, 1, source_card=card, post_callback=callback)
    if not result:
        return True
    return True


# --- OP04-068: Yokozuna ---
@register_effect("OP04-068", "blocker", "[Blocker]")
def op04_068_yokozuna_blocker(game_state, player, card):
    """Blocker ability."""
    card.has_blocker = True
    return True


@register_effect("OP04-068", "on_opponent_attack", "[On Opponent's Attack] DON -1: Return cost 2 or less to hand")
def op04_068_yokozuna_defense(game_state, player, card):
    """On Opponent's Attack: Return 1 DON to return cost 2 or less to hand."""
    def callback():
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
        if targets:
            create_return_to_hand_choice(
                game_state, player, targets, source_card=card,
                prompt="Choose up to 1 opponent's cost 2 or less Character to return to hand",
                optional=True,
            )

    result = optional_don_return(game_state, player, 1, source_card=card, post_callback=callback)
    if not result:
        return True
    return True


# --- OP04-069: Mr. 2 Bon Kurei ---
@register_effect("OP04-069", "on_opponent_attack", "[On Opponent's Attack] DON -1: Match attacker's power")
def op04_069_bon_kurei(game_state, player, card):
    """On Opponent's Attack: Return 1 DON to match attacker's power."""
    def callback():
        attacker = (getattr(game_state, 'pending_attack', {}) or {}).get('attacker')
        if attacker is not None:
            attacker_power = (getattr(attacker, 'power', 0) or 0) + getattr(attacker, 'power_modifier', 0)
            own_power = (getattr(card, 'power', 0) or 0) + getattr(card, 'power_modifier', 0)
            delta = attacker_power - own_power
            if delta:
                add_power_modifier(card, delta)
                card.power_modifier_expires_on_turn = game_state.turn_count
                card._sticky_power_modifier_expires_on_turn = game_state.turn_count
    result = optional_don_return(game_state, player, 1, source_card=card, post_callback=callback)
    if not result:
        return True
    return True


@register_effect("OP04-069", "trigger", "[Trigger] DON -1: Play this card")
def op04_069_bon_kurei_trigger(game_state, player, card):
    """Trigger: Return 1 DON to play this card."""
    def callback():
        player.cards_in_play.append(card)
        setattr(card, 'played_turn', game_state.turn_count)
        game_state._apply_keywords(card)
        game_state._log(f"{player.name} played {card.name} from Trigger")

    result = optional_don_return(game_state, player, 1, source_card=card, post_callback=callback)
    if not result:
        return True
    return True


# --- OP04-070: Mr. 3 ---
@register_effect("OP04-070", "on_opponent_attack", "[On Opponent's Attack] [Once Per Turn] DON -1: -1000 power")
def op04_070_mr3(game_state, player, card):
    """On Opponent's Attack: Return 1 DON to give -1000 power."""
    if not getattr(card, 'op04_070_used', False):
        def callback():
            opponent = get_opponent(game_state, player)
            card.op04_070_used = True
            if opponent.cards_in_play:
                create_power_reduction_choice(
                    game_state, player, list(opponent.cards_in_play), -1000, source_card=card,
                    prompt="Choose up to 1 opponent's Character to give -1000 power",
                    min_selections=0,
                )

        result = optional_don_return(game_state, player, 1, source_card=card, post_callback=callback)
        if not result:
            return True
        return True
    return False


# --- OP04-071: Mr. 4 ---
@register_effect("OP04-071", "on_opponent_attack", "[On Opponent's Attack] DON -1: Gains Blocker +1000")
def op04_071_mr4(game_state, player, card):
    """On Opponent's Attack: Return 1 DON to gain Blocker and +1000."""
    def callback():
        card.has_blocker = True
        card._temporary_blocker_for_battle = True
        card.power_modifier = getattr(card, 'power_modifier', 0) + 1000
        card._battle_power_modifier = getattr(card, '_battle_power_modifier', 0) + 1000
    result = optional_don_return(game_state, player, 1, source_card=card, post_callback=callback)
    if not result:
        return True
    return True


# --- OP04-072: Mr. 5 ---
@register_effect("OP04-072", "on_opponent_attack", "[On Opponent's Attack] [Once Per Turn] DON -2 and rest: K.O. cost 4 or less")
def op04_072_mr5(game_state, player, card):
    """On Opponent's Attack: Return 2 DON and rest to K.O. cost 4 or less."""
    if not getattr(card, 'op04_072_used', False):
        def callback():
            def rest_callback(selected):
                if not selected or selected[0] != "yes":
                    return
                card.is_resting = True
                card.op04_072_used = True
                opponent = get_opponent(game_state, player)
                targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
                if targets:
                    create_ko_choice(
                        game_state, player, targets, source_card=card,
                        prompt="Choose up to 1 opponent's cost 4 or less Character to K.O.",
                        min_selections=0,
                    )

            create_mode_choice(
                game_state, player,
                modes=[
                    {"id": "yes", "label": "Rest this Character"},
                    {"id": "no", "label": "Do not rest this Character"},
                ],
                source_card=card,
                prompt="Rest Mr. 5 to K.O. up to 1 opponent's cost 4 or less Character?",
                callback=rest_callback,
            )

        result = optional_don_return(game_state, player, 2, source_card=card, post_callback=callback)
        if not result:
            return True
        return True
    return False


# --- OP04-073: Mr.13 & Ms.Friday ---
@register_effect("OP04-073", "activate", "[Activate: Main] Trash this and Baroque Works: Add 1 active DON")
def op04_073_mr13_friday(game_state, player, card):
    """Activate: Trash this and Baroque Works character to add 1 active DON."""
    bw_chars = [c for c in player.cards_in_play if 'Baroque Works' in (c.card_origin or '') and c != card]
    if card not in player.cards_in_play or not bw_chars:
        return False

    bw_snap = list(bw_chars)

    def mr13_friday_cb(selected: list) -> None:
        target_idx = int(selected[0]) if selected else -1
        if not (0 <= target_idx < len(bw_snap)):
            return
        target = bw_snap[target_idx]
        if target not in player.cards_in_play or card not in player.cards_in_play:
            return
        player.cards_in_play.remove(target)
        player.trash.append(target)
        player.cards_in_play.remove(card)
        player.trash.append(card)
        game_state._log(f"{target.name} was trashed")
        game_state._log(f"{card.name} was trashed")
        add_don_from_deck(player, 1, set_active=True)
        game_state._log(f"{player.name} gained 1 active DON")

    return create_target_choice(
        game_state,
        player,
        bw_snap,
        "Choose 1 of your other Baroque Works type Characters to trash",
        source_card=card,
        callback=mr13_friday_cb,
    )


@register_effect("OP04-073", "trigger", "[Trigger] Play this card")
def op04_073_mr13_friday_trigger(game_state, player, card):
    """Trigger: Play this card."""
    player.cards_in_play.append(card)
    return True


# --- OP04-074: Colors Trap ---
@register_effect("OP04-074", "counter", "[Counter] DON -1: +1000 power, then rest up to 1 opponent's cost 4 or less Character")
def op04_074_colors_trap(game_state, player, card):
    """Counter: Return 1 DON, then give +1000 during this battle and rest up to 1 opponent cost 4 or less Character."""
    power_targets = _own_leader_and_characters(player)

    def resolve_effect():
        def rest_step():
            targets = _active_opponent_characters_by_cost(game_state, player, 4)
            if targets:
                create_rest_choice(
                    game_state,
                    player,
                    targets,
                    source_card=card,
                    prompt="Choose up to 1 opponent's cost 4 or less Character to rest",
                    min_selections=0,
                )

        def power_callback(selected):
            if selected:
                idx = int(selected[0])
                if 0 <= idx < len(power_targets):
                    target = power_targets[idx]
                    target.power_modifier = getattr(target, 'power_modifier', 0) + 1000
                    target._battle_power_modifier = getattr(target, '_battle_power_modifier', 0) + 1000
                    game_state._log(f"{target.name} gets +1000 power during this battle")
            rest_step()

        if power_targets:
            create_target_choice(
                game_state,
                player,
                power_targets,
                "Choose up to 1 of your Leader or Character cards to gain +1000 power during this battle",
                source_card=card,
                min_selections=0,
                max_selections=1,
                callback=power_callback,
            )
        else:
            rest_step()

    result = optional_don_return(game_state, player, 1, source_card=card, post_callback=resolve_effect)
    if not result:
        return True
    return True


@register_effect("OP04-074", "trigger", "[Trigger] Add up to 1 DON!! card from your DON!! deck and set it as active")
def op04_074_colors_trap_trigger(game_state, player, card):
    """Trigger: Add up to 1 DON!! card from deck and set it active."""
    add_don_from_deck(player, 1, set_active=True)
    return True


# --- OP04-075: Nez-Palm Cannon ---
@register_effect("OP04-075", "counter", "[Counter] +6000 power, then add up to 1 rested DON if you have 2 or less Life")
def op04_075_nez_palm_cannon(game_state, player, card):
    """Counter: Give +6000 during this battle, then add 1 rested DON if you have 2 or less Life."""
    power_targets = _own_leader_and_characters(player)

    def callback(selected):
        if selected:
            idx = int(selected[0])
            if 0 <= idx < len(power_targets):
                target = power_targets[idx]
                target.power_modifier = getattr(target, 'power_modifier', 0) + 6000
                target._battle_power_modifier = getattr(target, '_battle_power_modifier', 0) + 6000
                game_state._log(f"{target.name} gets +6000 power during this battle")
        if len(player.life_cards) <= 2:
            add_don_from_deck(player, 1, set_active=False)

    if power_targets:
        return create_target_choice(
            game_state,
            player,
            power_targets,
            "Choose up to 1 of your Leader or Character cards to gain +6000 power during this battle",
            source_card=card,
            min_selections=0,
            max_selections=1,
            callback=callback,
        )
    if len(player.life_cards) <= 2:
        add_don_from_deck(player, 1, set_active=False)
    return True


@register_effect("OP04-075", "trigger", "[Trigger] Add up to 1 DON!! card from your DON!! deck and set it as active")
def op04_075_nez_palm_cannon_trigger(game_state, player, card):
    """Trigger: Add up to 1 DON!! card from deck and set it active."""
    add_don_from_deck(player, 1, set_active=True)
    return True


# --- OP04-076: Weakness...Is an Unforgivable Sin. ---
@register_effect("OP04-076", "counter", "[Counter] DON -1: +1000 power during this turn")
def op04_076_weakness_unforgivable(game_state, player, card):
    """Counter: Return 1 DON, then give +1000 power during this turn."""
    power_targets = _own_leader_and_characters(player)

    def resolve_effect():
        def callback(selected):
            if not selected:
                return
            idx = int(selected[0])
            if 0 <= idx < len(power_targets):
                target = power_targets[idx]
                add_power_modifier(target, 1000)
                target.power_modifier_expires_on_turn = game_state.turn_count
                target._sticky_power_modifier_expires_on_turn = game_state.turn_count
                game_state._log(f"{target.name} gets +1000 power during this turn")

        if power_targets:
            create_target_choice(
                game_state,
                player,
                power_targets,
                "Choose up to 1 of your Leader or Character cards to gain +1000 power during this turn",
                source_card=card,
                min_selections=0,
                max_selections=1,
                callback=callback,
            )

    result = optional_don_return(game_state, player, 1, source_card=card, post_callback=resolve_effect)
    if not result:
        return True
    return True


@register_effect("OP04-076", "trigger", "[Trigger] Add up to 1 DON!! card from your DON!! deck and set it as active")
def op04_076_weakness_unforgivable_trigger(game_state, player, card):
    """Trigger: Add up to 1 DON!! card from deck and set it active."""
    add_don_from_deck(player, 1, set_active=True)
    return True


# --- OP04-077: Ideo ---
@register_effect("OP04-077", "blocker", "[Blocker]")
def op04_077_ideo(game_state, player, card):
    """Blocker ability."""
    card.has_blocker = True
    return True


# --- OP04-079: Orlumbus ---
@register_effect("OP04-079", "activate", "[Activate: Main] [Once Per Turn] -4 cost, trash 2, K.O. Dressrosa")
def op04_079_orlumbus(game_state, player, card):
    """Activate: Give -4 cost, trash 2 from deck, K.O. own Dressrosa character."""
    if not getattr(card, 'op04_079_used', False):
        for _ in range(min(2, len(player.deck))):
            player.trash.append(player.deck.pop(0))
        card.op04_079_used = True
        opponent = get_opponent(game_state, player)

        def ko_dressrosa():
            dressrosa = [c for c in player.cards_in_play if 'Dressrosa' in (c.card_origin or '')]
            if dressrosa:
                create_ko_choice(
                    game_state, player, list(dressrosa), source_card=card,
                    prompt="Choose 1 of your Dressrosa Characters to K.O."
                )

        if opponent.cards_in_play:
            opp_snap = list(opponent.cards_in_play)

            def orlumbus_cb(selected: list) -> None:
                for sel in selected:
                    target_idx = int(sel)
                    if 0 <= target_idx < len(opp_snap):
                        target = opp_snap[target_idx]
                        target.cost_modifier = getattr(target, 'cost_modifier', 0) - 4
                        game_state._log(f"{target.name} gets -4 cost this turn")
                ko_dressrosa()

            return create_cost_reduction_choice(
                game_state, player, list(opponent.cards_in_play), -4, source_card=card,
                prompt="Choose up to 1 opponent's Character to give -4 cost",
                min_selections=0, callback=orlumbus_cb
            )
        ko_dressrosa()
        return True
    return False


# --- OP04-080: Gyats ---
@register_effect("OP04-080", "on_play", "[On Play] Dressrosa can attack active")
def op04_080_gyats(game_state, player, card):
    """On Play: Dressrosa character can attack active characters."""
    dressrosa = [c for c in player.cards_in_play if 'Dressrosa' in (c.card_origin or '')]
    if dressrosa:
        return create_attack_active_choice(
            game_state, player, dressrosa, source_card=card,
            prompt="Choose up to 1 Dressrosa Character to gain attack active",
            min_selections=0,
        )
    return True


# --- OP04-081: Cavendish ---
@register_effect("OP04-081", "continuous", "[DON!! x1] Can attack active Characters")
def op04_081_cavendish_continuous(game_state, player, card):
    """With 1 DON: Can attack active characters."""
    attached = getattr(card, 'attached_don', 0)
    if attached >= 1:
        card.can_attack_active = True
    return True


@register_effect("OP04-081", "on_attack", "[When Attacking] Rest Leader: K.O. cost 1 or less, trash 2")
def op04_081_cavendish_attack(game_state, player, card):
    """When Attacking: Rest Leader to K.O. cost 1 or less and trash 2."""
    if player.leader and not getattr(player.leader, 'is_resting', False):
        def yes_no_callback(selected):
            if not selected or selected[0] != "yes":
                return
            player.leader.is_resting = True
            opponent = get_opponent(game_state, player)
            targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 1]

            def finish():
                for _ in range(min(2, len(player.deck))):
                    player.trash.append(player.deck.pop(0))

            if targets:
                snapshot = list(targets)

                def callback(chosen):
                    for sel in chosen:
                        idx = int(sel)
                        if 0 <= idx < len(snapshot):
                            target = snapshot[idx]
                            if target in opponent.cards_in_play:
                                opponent.cards_in_play.remove(target)
                                opponent.trash.append(target)
                                game_state._log(f"{target.name} was KO'd")
                    finish()

                create_ko_choice(
                    game_state, player, snapshot, source_card=card,
                    prompt="Choose up to 1 opponent's cost 1 or less Character to K.O.",
                    min_selections=0, callback=callback
                )
            else:
                finish()

        return create_mode_choice(
            game_state, player,
            modes=[
                {"id": "yes", "label": "Rest your Leader"},
                {"id": "no", "label": "Do not use effect"},
            ],
            source_card=card,
            prompt="Rest your Leader to use Cavendish's effect?",
            callback=yes_no_callback,
        )
    return False


# --- OP04-082: Kyros ---
@register_effect("OP04-082", "on_ko_prevention", "If would be K.O.'d, rest Leader or Corrida Coliseum instead")
def op04_082_kyros_prevention(game_state, player, card):
    """K.O. Prevention: Rest Leader or Corrida Coliseum instead."""
    return game_state._queue_kyros_ko_prevention(
        player,
        card,
        on_decline=lambda: None,
    )


@register_effect("OP04-082", "on_play", "[On Play] If Rebecca Leader, K.O. cost 1 or less, trash 1")
def op04_082_kyros_play(game_state, player, card):
    """On Play: If Rebecca Leader, K.O. cost 1 or less and trash 1."""
    if player.leader and 'Rebecca' in getattr(player.leader, 'name', ''):
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 1]
        if targets:
            def callback(selected):
                target_idx = int(selected[0]) if selected else -1
                if 0 <= target_idx < len(targets):
                    target = targets[target_idx]
                    if target in opponent.cards_in_play:
                        opponent.cards_in_play.remove(target)
                        opponent.trash.append(target)
                        game_state._log(f"{target.name} was K.O.'d")
                _trash_top_cards(player, 1)

            return create_ko_choice(
                game_state, player, targets, source_card=card,
                prompt="Choose up to 1 opponent's cost 1 or less Character to K.O.",
                callback=callback, min_selections=0
            )
        _trash_top_cards(player, 1)
        return True
    return True


# --- OP04-083: Sabo ---
@register_effect("OP04-083", "blocker", "[Blocker]")
def op04_083_sabo_blocker(game_state, player, card):
    """Blocker ability."""
    card.has_blocker = True
    return True


@register_effect("OP04-083", "on_play", "[On Play] Characters cannot be K.O.'d by effects, draw 2 trash 2")
def op04_083_sabo_play(game_state, player, card):
    """On Play: Characters cannot be K.O.'d by effects until next turn. Draw 2, trash 2."""
    player.characters_cannot_be_ko_by_effects_until_turn = game_state.turn_count + 1
    for c in player.cards_in_play:
        c.cannot_be_ko_by_effects = True
    draw_cards(player, 2)
    trash_from_hand(player, 2, game_state, card)
    return True


# --- OP04-084: Stussy ---
@register_effect("OP04-084", "on_play", "[On Play] Look at 3, play CP cost 2 or less")
def op04_084_stussy(game_state, player, card):
    """On Play: Look at 3 and play CP cost 2 or less character."""
    return search_top_cards(
        game_state, player, look_count=3, add_count=1,
        filter_fn=lambda c: 'CP' in (c.card_origin or '') and getattr(c, 'name', '') != 'Stussy'
        and (getattr(c, 'cost', 0) or 0) <= 2,
        source_card=card,
        prompt="Look at the top 3 cards: play up to 1 CP Character with cost 2 or less",
        trash_rest=True,
        play_to_field=True,
    )


# --- OP04-085: Suleiman ---
@register_effect("OP04-085", "on_play", "[On Play] If Dressrosa Leader, -2 cost, trash 1")
def op04_085_suleiman_play(game_state, player, card):
    """On Play: If Dressrosa Leader, give -2 cost and trash 1 from deck."""
    if player.leader and 'Dressrosa' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            snapshot = list(opponent.cards_in_play)

            def callback(selected):
                target_idx = int(selected[0]) if selected else -1
                if 0 <= target_idx < len(snapshot):
                    snapshot[target_idx].cost_modifier = getattr(snapshot[target_idx], 'cost_modifier', 0) - 2
                    game_state._log(f"{snapshot[target_idx].name} gets -2 cost this turn")
                _trash_top_cards(player, 1)

            return create_cost_reduction_choice(
                game_state, player, snapshot, -2, source_card=card,
                prompt="Choose up to 1 opponent's Character to give -2 cost",
                callback=callback, min_selections=0
            )
        _trash_top_cards(player, 1)
        return True
    return True


@register_effect("OP04-085", "on_attack", "[When Attacking] If Dressrosa Leader, -2 cost, trash 1")
def op04_085_suleiman_attack(game_state, player, card):
    """When Attacking: If Dressrosa Leader, give -2 cost and trash 1 from deck."""
    if player.leader and 'Dressrosa' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            snapshot = list(opponent.cards_in_play)

            def callback(selected):
                target_idx = int(selected[0]) if selected else -1
                if 0 <= target_idx < len(snapshot):
                    snapshot[target_idx].cost_modifier = getattr(snapshot[target_idx], 'cost_modifier', 0) - 2
                    game_state._log(f"{snapshot[target_idx].name} gets -2 cost this turn")
                _trash_top_cards(player, 1)

            return create_cost_reduction_choice(
                game_state, player, snapshot, -2, source_card=card,
                prompt="Choose up to 1 opponent's Character to give -2 cost",
                callback=callback, min_selections=0
            )
        _trash_top_cards(player, 1)
        return True
    return False


# --- OP04-086: Chinjao ---
@register_effect("OP04-086", "on_ko_opponent", "[DON!! x1] When this K.O.'s opponent, draw 2 trash 2")
def op04_086_chinjao(game_state, player, card):
    """With 1 DON: When this K.O.'s opponent in battle, draw 2 trash 2."""
    attached = getattr(card, 'attached_don', 0)
    if attached >= 1:
        draw_cards(player, 2)
        _prompt_exact_hand_trash(
            game_state,
            player,
            2,
            card,
            "Choose 2 cards from your hand to trash",
        )
        return True
    return False


# --- OP04-088: Hajrudin ---
@register_effect("OP04-088", "activate", "[Activate: Main] Rest Leader: -4 cost")
def op04_088_hajrudin(game_state, player, card):
    """Activate: Rest Leader to give -4 cost."""
    if player.leader and not getattr(player.leader, 'is_resting', False):
        player.leader.is_resting = True
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            return create_cost_reduction_choice(
                game_state, player, list(opponent.cards_in_play), -4, source_card=card,
                prompt="Choose up to 1 opponent's Character to give -4 cost",
                min_selections=0,
            )
        return True
    return False


# --- OP04-089: Bartolomeo ---
@register_effect("OP04-089", "blocker", "[Blocker]")
def op04_089_bartolomeo(game_state, player, card):
    """Blocker ability."""
    card.has_blocker = True
    return True


# --- OP04-090: Monkey.D.Luffy ---
@register_effect("OP04-090", "continuous", "Can attack active Characters")
def op04_090_luffy_continuous(game_state, player, card):
    """Continuous: Can attack active characters."""
    card.can_attack_active = True
    return True


@register_effect("OP04-090", "activate", "[Activate: Main] [Once Per Turn] Return 7 trash to deck: Set active, skip next Refresh")
def op04_090_luffy_activate(game_state, player, card):
    """Activate: Return 7 trash to deck to set active but skip next Refresh."""
    if not getattr(card, 'op04_090_used', False) and len(player.trash) >= 7:
        trash_snapshot = list(player.trash)

        def callback(selected):
            if len(selected) != 7:
                return
            chosen_cards = []
            for sel in selected:
                idx = int(sel)
                if 0 <= idx < len(trash_snapshot):
                    chosen = trash_snapshot[idx]
                    if chosen in player.trash and chosen not in chosen_cards:
                        player.trash.remove(chosen)
                        chosen_cards.append(chosen)
            if len(chosen_cards) != 7:
                return
            for chosen in chosen_cards:
                player.deck.append(chosen)
            card.is_resting = False
            card.has_attacked = False
            card.skip_next_refresh = True
            card.op04_090_used = True
            game_state._log(f"{player.name} returned 7 cards from trash to the bottom of the deck")

        return create_target_choice(
            game_state, player, trash_snapshot,
            "Choose exactly 7 cards from your trash to return to the bottom of your deck",
            source_card=card, min_selections=7, max_selections=7, callback=callback
        )
    return False


# --- OP04-091: Leo ---
@register_effect("OP04-091", "on_play", "[On Play] Rest Leader: If Dressrosa Leader, K.O. cost 1 or less, trash 2")
def op04_091_leo(game_state, player, card):
    """On Play: Rest Leader to K.O. cost 1 or less and trash 2 if Dressrosa Leader."""
    if player.leader and 'Dressrosa' in (player.leader.card_origin or ''):
        if not getattr(player.leader, 'is_resting', False):
            def yes_no_callback(selected):
                if not selected or selected[0] != "yes":
                    return
                player.leader.is_resting = True
                opponent = get_opponent(game_state, player)
                targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 1]

                def finish():
                    _trash_top_cards(player, 2)

                if targets:
                    snapshot = list(targets)

                    def callback(chosen):
                        for sel in chosen:
                            idx = int(sel)
                            if 0 <= idx < len(snapshot):
                                target = snapshot[idx]
                                if target in opponent.cards_in_play:
                                    opponent.cards_in_play.remove(target)
                                    opponent.trash.append(target)
                                    game_state._log(f"{target.name} was K.O.'d")
                        finish()

                    create_ko_choice(
                        game_state, player, snapshot, source_card=card,
                        prompt="Choose up to 1 opponent's cost 1 or less Character to K.O.",
                        callback=callback, min_selections=0
                    )
                else:
                    finish()

            return create_mode_choice(
                game_state, player,
                modes=[
                    {"id": "yes", "label": "Rest your Leader"},
                    {"id": "no", "label": "Do not use effect"},
                ],
                source_card=card,
                prompt="Rest your Leader to use Leo's effect?",
                callback=yes_no_callback,
            )
    return True


# --- OP04-092: Rebecca ---
@register_effect("OP04-092", "on_play", "[On Play] Look at 3, add Dressrosa card")
def op04_092_rebecca(game_state, player, card):
    """On Play: Look at 3 and add Dressrosa card."""
    return search_top_cards(
        game_state, player, look_count=3, add_count=1,
        filter_fn=lambda c: 'dressrosa' in (c.card_origin or '').lower() and getattr(c, 'name', '') != 'Rebecca',
        source_card=card,
        prompt="Look at the top 3 cards: reveal up to 1 Dressrosa card other than Rebecca and add it to hand",
        trash_rest=True,
    )


# --- OP04-093: Gum-Gum King Kong Gun ---
@register_effect("OP04-093", "on_play", "[Main] Dressrosa character gains +6000, and Double Attack if 15+ trash")
def op04_093_king_kong_gun(game_state, player, card):
    """Main: Up to 1 Dressrosa Character gains +6000 this turn, then Double Attack if you have 15+ trash."""
    targets = [c for c in player.cards_in_play if 'dressrosa' in (getattr(c, 'card_origin', '') or '').lower()]
    if not targets:
        return True

    has_large_trash = len(player.trash) >= 15

    def callback(selected):
        if not selected:
            return
        idx = int(selected[0])
        if not (0 <= idx < len(targets)):
            return
        target = targets[idx]
        add_power_modifier(target, 6000)
        target.power_modifier_expires_on_turn = game_state.turn_count
        target._sticky_power_modifier_expires_on_turn = game_state.turn_count
        game_state._log(f"{target.name} gets +6000 power during this turn")
        if has_large_trash:
            _grant_double_attack_for_turn(game_state, target)

    return create_target_choice(
        game_state,
        player,
        targets,
        "Choose up to 1 of your Dressrosa type Characters to gain +6000 power during this turn",
        source_card=card,
        min_selections=0,
        max_selections=1,
        callback=callback,
    )


@register_effect("OP04-093", "trigger", "[Trigger] Draw 3 cards and trash 2 cards from your hand")
def op04_093_king_kong_gun_trigger(game_state, player, card):
    """Trigger: Draw 3 cards, then trash 2 cards from hand."""
    draw_cards(player, 3)
    return _prompt_exact_hand_trash(
        game_state,
        player,
        2,
        card,
        "Choose 2 cards from your hand to trash",
    )


# --- OP04-094: Trueno Bastardo ---
@register_effect("OP04-094", "on_play", "[Main] K.O. up to 1 opponent's Character with cost 4 or less, or 6 or less with 15+ trash")
def op04_094_trueno_bastardo(game_state, player, card):
    """Main: K.O. up to 1 opponent Character with cost 4 or less, or 6 or less if you have 15+ trash."""
    opponent = get_opponent(game_state, player)
    max_cost = 6 if len(player.trash) >= 15 else 4
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= max_cost]
    if targets:
        return create_ko_choice(
            game_state,
            player,
            targets,
            source_card=card,
            prompt=f"Choose up to 1 opponent's cost {max_cost} or less Character to K.O.",
            min_selections=0,
        )
    return True


@register_effect("OP04-094", "trigger", "[Trigger] You may rest your Leader: K.O. up to 1 opponent's cost 5 or less Character")
def op04_094_trueno_bastardo_trigger(game_state, player, card):
    """Trigger: You may rest your Leader to K.O. up to 1 opponent's cost 5 or less Character."""
    if not player.leader or getattr(player.leader, 'is_resting', False):
        return True

    def callback(selected):
        if not selected or selected[0] != "yes":
            return
        player.leader.is_resting = True
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 5]
        if targets:
            create_ko_choice(
                game_state,
                player,
                targets,
                source_card=card,
                prompt="Choose up to 1 opponent's cost 5 or less Character to K.O.",
                min_selections=0,
            )

    return _prompt_optional_yes_no(
        game_state,
        player,
        card,
        "Rest your Leader to use Trueno Bastardo's trigger?",
        "Rest your Leader",
        callback,
    )


# --- OP04-095: Barrier!! ---
@register_effect("OP04-095", "counter", "[Counter] +2000 power, then an additional +2000 if 15+ trash")
def op04_095_barrier_counter(game_state, player, card):
    """Counter: Up to 1 of your Leader or Characters gains +2000, or +4000 with 15+ trash."""
    amount = 4000 if len(player.trash) >= 15 else 2000
    targets = _own_leader_and_characters(player)
    if not targets:
        return True

    def callback(selected):
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(targets):
            target = targets[idx]
            target.power_modifier = getattr(target, 'power_modifier', 0) + amount
            target._battle_power_modifier = getattr(target, '_battle_power_modifier', 0) + amount
            game_state._log(f"{target.name} gets +{amount} power during this battle")

    return create_target_choice(
        game_state,
        player,
        targets,
        f"Choose up to 1 of your Leader or Character cards to gain +{amount} power during this battle",
        source_card=card,
        min_selections=0,
        max_selections=1,
        callback=callback,
    )


@register_effect("OP04-095", "trigger", "[Trigger] Draw 2 cards and trash 1 card from your hand")
def op04_095_barrier_trigger(game_state, player, card):
    """Trigger: Draw 2 cards, then trash 1 card from hand."""
    draw_cards(player, 2)
    return _prompt_exact_hand_trash(
        game_state,
        player,
        1,
        card,
        "Choose 1 card from your hand to trash",
    )


# --- OP04-096: Corrida Coliseum ---
@register_effect("OP04-096", "continuous", "Dressrosa Characters can attack Characters on the turn they are played")
def op04_096_corrida_coliseum(game_state, player, card):
    """Continuous: Your Dressrosa Characters can attack Characters on the turn they are played."""
    if player.leader and 'dressrosa' in (getattr(player.leader, 'card_origin', '') or '').lower():
        for target in player.cards_in_play:
            if 'dressrosa' in (getattr(target, 'card_origin', '') or '').lower():
                target.can_attack_characters_on_play_turn = True
    return True


# --- OP04-097: Otama ---
@register_effect("OP04-097", "on_play", "[On Play] Add opponent's Animal/SMILE cost 3 or less to their Life")
def op04_097_otama(game_state, player, card):
    """On Play: Add opponent's Animal/SMILE cost 3 or less to their Life."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if ('Animal' in (c.card_origin or '') or 'SMILE' in (c.card_origin or ''))
               and (getattr(c, 'cost', 0) or 0) <= 3]
    if targets:
        return create_bottom_deck_choice(
            game_state, player, targets, source_card=card,
            prompt="Choose up to 1 Animal/SMILE cost 3 or less Character to add to opponent's Life",
            callback_action="add_to_opponent_life",
            min_selections=0,
        )
    return True


# --- OP04-098: Toko ---
@register_effect("OP04-098", "on_play", "[On Play] Trash 2 Wano: If 1 or less Life, add deck to Life")
def op04_098_toko(game_state, player, card):
    """On Play: Trash 2 Wano cards to add deck to Life if 1 or less Life."""
    wano_cards = [c for c in player.hand if 'Land of Wano' in (c.card_origin or '')]
    if len(player.life_cards) > 1 or len(wano_cards) < 2:
        return True

    snapshot = list(wano_cards)

    def confirm_callback(selected):
        if not selected or selected[0] != "yes":
            return

        def trash_callback(trash_selected):
            if len(trash_selected) != 2:
                return
            for idx in sorted((int(sel) for sel in trash_selected), reverse=True):
                if 0 <= idx < len(snapshot):
                    target = snapshot[idx]
                    if target in player.hand:
                        player.hand.remove(target)
                        player.trash.append(target)
                        game_state._log(f"{player.name} trashed {target.name}")
            if player.deck:
                player.life_cards.append(player.deck.pop(0))
                game_state._log(f"{player.name} added 1 card from the top of deck to Life")

        create_target_choice(
            game_state, player, snapshot,
            "Choose 2 Land of Wano cards from your hand to trash",
            source_card=card, min_selections=2, max_selections=2, callback=trash_callback
        )

    return create_mode_choice(
        game_state, player,
        modes=[
            {"id": "yes", "label": "Trash 2 cards"},
            {"id": "no", "label": "Do not use effect"},
        ],
        source_card=card,
        prompt="Trash 2 Land of Wano cards from your hand to add 1 card from the top of your deck to Life?",
        callback=confirm_callback,
    )


# --- OP04-099: Olin ---
@register_effect("OP04-099", "continuous", "Also treat as Charlotte Linlin")
def op04_099_olin(game_state, player, card):
    """Continuous: Also treat as Charlotte Linlin."""
    card.alt_name = 'Charlotte Linlin'
    return True


@register_effect("OP04-099", "trigger", "[Trigger] If 1 or less Life, play this card")
def op04_099_olin_trigger(game_state, player, card):
    """Trigger: If 1 or less Life, play this card."""
    if len(player.life_cards) <= 1:
        player.cards_in_play.append(card)
        return True
    return False


# --- OP04-100: Capone Bege ---
@register_effect("OP04-100", "trigger", "[Trigger] Opponent cannot attack this turn")
def op04_100_bege(game_state, player, card):
    """Trigger: Opponent's Leader or Character cannot attack this turn."""
    opponent = get_opponent(game_state, player)
    targets = list(opponent.cards_in_play)
    if opponent.leader:
        targets.insert(0, opponent.leader)
    if targets:
        return create_target_choice(
            game_state, player, targets,
            "Choose up to 1 opponent's Leader or Character that cannot attack during this turn",
            source_card=card, min_selections=0, max_selections=1,
            callback=lambda selected: [
                (
                    setattr(targets[int(sel)], 'cannot_attack', True),
                    setattr(targets[int(sel)], 'cannot_attack_until_turn', game_state.turn_count),
                    game_state._log(f"{targets[int(sel)].name} cannot attack during this turn")
                )
                for sel in selected if 0 <= int(sel) < len(targets)
            ],
        )
    return True


# --- OP04-101: Carmel ---
@register_effect("OP04-101", "on_play", "[On Play] Draw 1")
def op04_101_carmel(game_state, player, card):
    """On Play: Draw 1 card."""
    draw_cards(player, 1)
    return True


@register_effect("OP04-101", "trigger", "[Trigger] Play this card, K.O. cost 2 or less")
def op04_101_carmel_trigger(game_state, player, card):
    """Trigger: Play this card and K.O. cost 2 or less."""
    player.cards_in_play.append(card)
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
    if targets:
        return create_ko_choice(
            game_state, player, targets, source_card=card,
            prompt="Choose up to 1 opponent's cost 2 or less Character to K.O.",
            min_selections=0,
        )
    return True


# --- OP04-102: Kin'emon ---
@register_effect("OP04-102", "activate", "[Activate: Main] [Once Per Turn] DON -1, take Life: Set active")
def op04_102_kinemon(game_state, player, card):
    """Activate: Rest 1 DON and take Life to set this active."""
    if getattr(card, 'op04_102_used', False) or not player.life_cards:
        return False

    def resolve_life(mode):
        if not player.life_cards:
            return
        life_card = player.life_cards.pop(0) if mode == "bottom" else player.life_cards.pop()
        player.hand.append(life_card)
        card.is_resting = False
        card.has_attacked = False
        card.op04_102_used = True
        game_state._log(f"{player.name} added {life_card.name} from Life to hand")
        game_state._log(f"{card.name} was set active")

    def don_callback(selected):
        if not selected:
            return
        don_idx = int(selected[0])
        if 0 <= don_idx < len(player.don_pool) and player.don_pool[don_idx] == "active":
            player.don_pool[don_idx] = "rested"
        if len(player.life_cards) == 1:
            resolve_life("top")
            return
        create_mode_choice(
            game_state, player,
            modes=[
                {"id": "top", "label": "Take top Life card"},
                {"id": "bottom", "label": "Take bottom Life card"},
            ],
            source_card=card,
            prompt="Choose which Life card to add to your hand",
            callback=lambda chosen: resolve_life((chosen or ["top"])[0]),
        )

    return _choose_own_don_by_state(
        game_state, player, "active", 1,
        "Choose 1 of your active DON!! cards to rest",
        don_callback, source_card=card
    )


# --- OP04-103: Kouzuki Hiyori ---
@register_effect("OP04-103", "on_play", "[On Play] Wano Leader/Character gains +1000")
def op04_103_hiyori(game_state, player, card):
    """On Play: Wano Leader or Character gains +1000."""
    wano = [c for c in player.cards_in_play if 'Land of Wano' in (c.card_origin or '')]
    if player.leader and 'Land of Wano' in (player.leader.card_origin or ''):
        wano.append(player.leader)
    if wano:
        return create_power_boost_choice(
            game_state, player, wano, 1000, source_card=card,
            prompt="Choose up to 1 Wano Leader or Character to give +1000 power",
            min_selections=0,
        )
    return True


@register_effect("OP04-103", "trigger", "[Trigger] Play this card")
def op04_103_hiyori_trigger(game_state, player, card):
    """Trigger: Play this card."""
    player.cards_in_play.append(card)
    return True


# --- OP04-104: Sanji ---
@register_effect("OP04-104", "blocker", "[Blocker]")
def op04_104_sanji_blocker(game_state, player, card):
    """Blocker ability."""
    card.has_blocker = True
    return True


@register_effect("OP04-104", "trigger", "[Trigger] Trash 1: Play this card")
def op04_104_sanji_trigger(game_state, player, card):
    """Trigger: Trash 1 to play this card."""
    if player.hand:
        hand_snapshot = list(player.hand)

        def callback(selected):
            target_idx = int(selected[0]) if selected else -1
            if 0 <= target_idx < len(hand_snapshot):
                discarded = hand_snapshot[target_idx]
                if discarded in player.hand:
                    player.hand.remove(discarded)
                    player.trash.append(discarded)
                    game_state._log(f"{player.name} trashed {discarded.name}")
            player.cards_in_play.append(card)
            setattr(card, 'played_turn', game_state.turn_count)
            game_state._apply_keywords(card)
            game_state._log(f"{player.name} played {card.name} from Trigger")

        return create_hand_discard_choice(
            game_state, player, hand_snapshot, source_card=card,
            prompt="Choose 1 card from your hand to trash",
            callback=callback
        )
    return False


# --- OP04-105: Charlotte Amande ---
@register_effect("OP04-105", "activate", "[Activate: Main] [Once Per Turn] Trash Trigger card: Rest cost 2 or less")
def op04_105_amande(game_state, player, card):
    """Activate: Trash Trigger card to rest cost 2 or less."""
    if not getattr(card, 'op04_105_used', False):
        trigger_cards = [c for c in player.hand if getattr(c, 'trigger', None)]
        if trigger_cards:
            card.op04_105_used = True
            trigger_snap = list(trigger_cards)
            def amande_cb(selected: list) -> None:
                target_idx = int(selected[0]) if selected else -1
                if 0 <= target_idx < len(trigger_snap):
                    target = trigger_snap[target_idx]
                    if target in player.hand:
                        player.hand.remove(target)
                        player.trash.append(target)
                        game_state._log(f"{target.name} was trashed")
                opponent = get_opponent(game_state, player)
                rest_targets = [c for c in opponent.cards_in_play
                               if not c.is_resting and (getattr(c, 'cost', 0) or 0) <= 2]
                if rest_targets:
                    create_rest_choice(game_state, player, rest_targets, source_card=card,
                                      prompt="Choose up to 1 opponent's cost 2 or less Character to rest",
                                      min_selections=0)
            return create_hand_discard_choice(game_state, player, trigger_cards, source_card=card,
                                             prompt="Choose a Trigger card to trash",
                                             callback=amande_cb)
    return False


# --- OP04-106: Charlotte Bavarois ---
@register_effect("OP04-106", "continuous", "[DON!! x1] If less Life, +1000 power")
def op04_106_bavarois(game_state, player, card):
    """With 1 DON: +1000 power if less Life than opponent."""
    attached = getattr(card, 'attached_don', 0)
    opponent = get_opponent(game_state, player)
    if attached >= 1 and len(player.life_cards) < len(opponent.life_cards):
        card.power_modifier = getattr(card, 'power_modifier', 0) + 1000
    return True


@register_effect("OP04-106", "trigger", "[Trigger] Trash 1: Play this card")
def op04_106_bavarois_trigger(game_state, player, card):
    """Trigger: Trash 1 to play this card."""
    if player.hand:
        hand_snapshot = list(player.hand)

        def callback(selected):
            target_idx = int(selected[0]) if selected else -1
            if 0 <= target_idx < len(hand_snapshot):
                discarded = hand_snapshot[target_idx]
                if discarded in player.hand:
                    player.hand.remove(discarded)
                    player.trash.append(discarded)
                    game_state._log(f"{player.name} trashed {discarded.name}")
            player.cards_in_play.append(card)
            setattr(card, 'played_turn', game_state.turn_count)
            game_state._apply_keywords(card)
            game_state._log(f"{player.name} played {card.name} from Trigger")

        return create_hand_discard_choice(
            game_state, player, hand_snapshot, source_card=card,
            prompt="Choose 1 card from your hand to trash",
            callback=callback
        )
    return False


# --- OP04-108: Charlotte Moscato ---
@register_effect("OP04-108", "continuous", "[DON!! x1] Gains Banish")
def op04_108_moscato(game_state, player, card):
    """With 1 DON: Gains Banish."""
    attached = getattr(card, 'attached_don', 0)
    if attached >= 1:
        card.has_banish = True
    return True


@register_effect("OP04-108", "trigger", "[Trigger] Trash 1: Play this card")
def op04_108_moscato_trigger(game_state, player, card):
    """Trigger: Trash 1 to play this card."""
    if player.hand:
        hand_snapshot = list(player.hand)

        def callback(selected):
            target_idx = int(selected[0]) if selected else -1
            if 0 <= target_idx < len(hand_snapshot):
                discarded = hand_snapshot[target_idx]
                if discarded in player.hand:
                    player.hand.remove(discarded)
                    player.trash.append(discarded)
                    game_state._log(f"{player.name} trashed {discarded.name}")
            player.cards_in_play.append(card)
            setattr(card, 'played_turn', game_state.turn_count)
            game_state._apply_keywords(card)
            game_state._log(f"{player.name} played {card.name} from Trigger")

        return create_hand_discard_choice(
            game_state, player, hand_snapshot, source_card=card,
            prompt="Choose 1 card from your hand to trash",
            callback=callback
        )
    return False


# --- OP04-109: Tonoyasu ---
@register_effect("OP04-109", "activate", "[Activate: Main] Trash this: Wano gains +3000")
def op04_109_tonoyasu(game_state, player, card):
    """Activate: Trash this to give Wano +3000."""
    if card in player.cards_in_play:
        player.cards_in_play.remove(card)
        player.trash.append(card)
        wano = [c for c in player.cards_in_play if 'Land of Wano' in (c.card_origin or '')]
        if player.leader and 'Land of Wano' in (player.leader.card_origin or ''):
            wano.append(player.leader)
        if wano:
            return create_power_boost_choice(
                game_state, player, wano, 3000, source_card=card,
                prompt="Choose up to 1 Wano Leader or Character to give +3000 power",
                min_selections=0,
            )
        return True
    return False


# --- OP04-110: Pound ---
@register_effect("OP04-110", "blocker", "[Blocker]")
def op04_110_pound_blocker(game_state, player, card):
    """Blocker ability."""
    card.has_blocker = True
    return True


@register_effect("OP04-110", "on_ko", "[On K.O.] Add opponent's cost 3 or less to their Life")
def op04_110_pound_ko(game_state, player, card):
    """On K.O.: Add opponent's cost 3 or less to their Life."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
    if targets:
        snapshot = list(targets)

        def target_callback(selected):
            target_idx = int(selected[0]) if selected else -1
            if not (0 <= target_idx < len(snapshot)):
                return
            target = snapshot[target_idx]

            def mode_callback(mode_selected):
                mode = mode_selected[0] if mode_selected else "top"
                if target in opponent.cards_in_play:
                    opponent.cards_in_play.remove(target)
                    if mode == "bottom":
                        opponent.life_cards.insert(0, target)
                    else:
                        opponent.life_cards.append(target)
                    game_state._log(f"{target.name} was added to {mode} of opponent's Life")

            create_mode_choice(
                game_state, player,
                modes=[
                    {"id": "top", "label": "Top of Life"},
                    {"id": "bottom", "label": "Bottom of Life"},
                ],
                source_card=card,
                prompt=f"Choose where to add {target.name} to opponent's Life",
                callback=mode_callback,
            )

        return create_target_choice(
            game_state, player, snapshot,
            "Choose up to 1 opponent's cost 3 or less Character to add to Life",
            source_card=card, min_selections=0, max_selections=1, callback=target_callback
        )
    return True


# --- OP04-111: Hera ---
@register_effect("OP04-111", "activate", "[Activate: Main] Trash Homies and rest: Set Charlotte Linlin active")
def op04_111_hera(game_state, player, card):
    """Activate: Trash Homies and rest to set Charlotte Linlin active."""
    homies = [c for c in player.cards_in_play if 'Homies' in (c.card_origin or '') and c != card]
    if getattr(card, 'is_resting', False) or not homies:
        return False

    homies_snap = list(homies)

    def hera_cb(selected: list) -> None:
        target_idx = int(selected[0]) if selected else -1
        if not (0 <= target_idx < len(homies_snap)):
            return
        target = homies_snap[target_idx]
        if target not in player.cards_in_play or card not in player.cards_in_play:
            return
        player.cards_in_play.remove(target)
        player.trash.append(target)
        card.is_resting = True
        game_state._log(f"{target.name} was trashed")
        linlins = [
            c for c in player.cards_in_play
            if 'Charlotte Linlin' in (getattr(c, 'name', '') or '')
            or getattr(c, 'alt_name', '') == 'Charlotte Linlin'
        ]
        if linlins:
            create_set_active_choice(
                game_state, player, linlins, source_card=card,
                prompt="Choose up to 1 of your Charlotte Linlin Characters to set active",
                min_selections=0,
            )

    return create_target_choice(
        game_state,
        player,
        homies_snap,
        "Choose 1 of your other Homies type Characters to trash",
        source_card=card,
        callback=hera_cb,
    )


@register_effect("OP04-111", "trigger", "[Trigger] Play this card")
def op04_111_hera_trigger(game_state, player, card):
    """Trigger: Play this card."""
    player.cards_in_play.append(card)
    return True


# --- OP04-112: Yamato ---
@register_effect("OP04-112", "on_play", "[On Play] K.O. cost equal to total Life, add deck to Life if 1 or less")
def op04_112_yamato(game_state, player, card):
    """On Play: K.O. cost equal to total Life, add deck to Life if 1 or less."""
    opponent = get_opponent(game_state, player)
    total_life = len(player.life_cards) + len(opponent.life_cards)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= total_life]

    def finish():
        if len(player.life_cards) > 1 or not player.deck:
            return

        def callback(selected):
            if not selected or selected[0] != "yes" or not player.deck:
                return
            _add_top_deck_to_life(game_state, player, log_card_name=False)

        _prompt_optional_yes_no(
            game_state,
            player,
            card,
            "Add the top card of your deck to the top of your Life cards?",
            "Add 1 card to Life",
            callback,
        )

    if targets:
        snapshot = list(targets)

        def callback(selected):
            for sel in selected:
                idx = int(sel)
                if 0 <= idx < len(snapshot):
                    target = snapshot[idx]
                    if target in opponent.cards_in_play:
                        opponent.cards_in_play.remove(target)
                        opponent.trash.append(target)
                        game_state._log(f"{target.name} was KO'd")
            finish()

        return create_ko_choice(
            game_state, player, snapshot, source_card=card,
            prompt=f"Choose up to 1 opponent's cost {total_life} or less Character to K.O.",
            min_selections=0, callback=callback
        )
    finish()
    return True


# --- OP04-113: Rabiyan ---
@register_effect("OP04-113", "trigger", "[Trigger] Play this card")
def op04_113_rabiyan(game_state, player, card):
    """Trigger: Play this card."""
    player.cards_in_play.append(card)
    return True


# --- OP04-115: Gun Modoki ---
@register_effect("OP04-115", "on_play", "[Main] You may add 1 card from the top or bottom of your Life to hand: Wano Character gains Double Attack")
def op04_115_gun_modoki(game_state, player, card):
    """Main: You may take top or bottom Life to hand, then up to 1 Wano Character gains Double Attack."""
    if not player.life_cards:
        return True

    def after_life(added, _life_card):
        if not added:
            return
        targets = [c for c in player.cards_in_play if 'land of wano' in (getattr(c, 'card_origin', '') or '').lower()]
        if not targets:
            return

        def target_callback(selected):
            if not selected:
                return
            idx = int(selected[0])
            if 0 <= idx < len(targets):
                target = targets[idx]
                _grant_double_attack_for_turn(game_state, target)

        create_target_choice(
            game_state,
            player,
            targets,
            "Choose up to 1 of your Land of Wano type Characters to gain Double Attack during this turn",
            source_card=card,
            min_selections=0,
            max_selections=1,
            callback=target_callback,
        )

    def use_callback(selected):
        if not selected or selected[0] != "yes":
            return
        _prompt_take_life_top_or_bottom_to_hand(
            game_state,
            player,
            card,
            "Choose the top or bottom card of your Life cards to add to your hand",
            after_life,
            reveal_card_names=False,
        )

    return _prompt_optional_yes_no(
        game_state,
        player,
        card,
        "Add 1 card from the top or bottom of your Life cards to your hand?",
        "Add 1 card from Life",
        use_callback,
    )


@register_effect("OP04-115", "trigger", "[Trigger] Up to 1 of your Leader or Character cards gains +1000 power during this turn")
def op04_115_gun_modoki_trigger(game_state, player, card):
    """Trigger: Up to 1 of your Leader or Character cards gains +1000 power during this turn."""
    targets = _own_leader_and_characters(player)
    if targets:
        return create_power_boost_choice(
            game_state,
            player,
            targets,
            1000,
            source_card=card,
            prompt="Choose up to 1 of your Leader or Character cards to gain +1000 power during this turn",
            min_selections=0,
        )
    return True


# --- OP04-116: Diable Jambe Joue Shot ---
@register_effect("OP04-116", "counter", "[Counter] +6000 power, then K.O. up to 1 cost 2 or less Character if total Life is 4 or less")
def op04_116_diable_jambe_counter(game_state, player, card):
    """Counter: Give +6000 power during battle, then K.O. up to 1 opponent cost 2 or less if total Life is 4 or less."""
    power_targets = _own_leader_and_characters(player)

    def ko_step():
        opponent = get_opponent(game_state, player)
        if len(player.life_cards) + len(opponent.life_cards) > 4:
            return
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
        if targets:
            create_ko_choice(
                game_state,
                player,
                targets,
                source_card=card,
                prompt="Choose up to 1 opponent's cost 2 or less Character to K.O.",
                min_selections=0,
            )

    def power_callback(selected):
        if selected:
            idx = int(selected[0])
            if 0 <= idx < len(power_targets):
                target = power_targets[idx]
                target.power_modifier = getattr(target, 'power_modifier', 0) + 6000
                target._battle_power_modifier = getattr(target, '_battle_power_modifier', 0) + 6000
                game_state._log(f"{target.name} gets +6000 power during this battle")
        ko_step()

    if power_targets:
        return create_target_choice(
            game_state,
            player,
            power_targets,
            "Choose up to 1 of your Leader or Character cards to gain +6000 power during this battle",
            source_card=card,
            min_selections=0,
            max_selections=1,
            callback=power_callback,
        )
    ko_step()
    return True


@register_effect("OP04-116", "trigger", "[Trigger] Draw 1 card")
def op04_116_diable_jambe_trigger(game_state, player, card):
    """Trigger: Draw 1 card."""
    draw_cards(player, 1)
    return True


# --- OP04-117: Heavenly Fire ---
@register_effect("OP04-117", "on_play", "[Main] Add up to 1 opponent's cost 3 or less Character to the top or bottom of their Life cards face-up")
def op04_117_heavenly_fire(game_state, player, card):
    """Main: Add up to 1 opponent cost 3 or less Character to the top or bottom of opponent's Life face-up."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
    if not targets:
        return True
    snapshot = list(targets)

    def target_callback(selected):
        target_idx = int(selected[0]) if selected else -1
        if not (0 <= target_idx < len(snapshot)):
            return
        target = snapshot[target_idx]

        def mode_callback(mode_selected):
            mode = mode_selected[0] if mode_selected else "top"
            if target not in opponent.cards_in_play:
                return
            opponent.cards_in_play.remove(target)
            target.is_face_up = True
            if mode == "bottom":
                opponent.life_cards.insert(0, target)
            else:
                opponent.life_cards.append(target)
            game_state._log(f"{target.name} was added to the {mode} of opponent's Life face-up")

        create_mode_choice(
            game_state,
            player,
            modes=[
                {"id": "top", "label": "Top of Life"},
                {"id": "bottom", "label": "Bottom of Life"},
            ],
            source_card=card,
            prompt=f"Choose where to add {target.name} to opponent's Life",
            callback=mode_callback,
        )

    return create_target_choice(
        game_state,
        player,
        snapshot,
        "Choose up to 1 opponent's cost 3 or less Character to add to their Life face-up",
        source_card=card,
        min_selections=0,
        max_selections=1,
        callback=target_callback,
    )


@register_effect("OP04-117", "trigger", "[Trigger] You may add 1 card from the top or bottom of your Life cards to your hand: Add up to 1 card from your hand to the top of your Life cards")
def op04_117_heavenly_fire_trigger(game_state, player, card):
    """Trigger: You may take top or bottom Life to hand, then add up to 1 hand card to the top of your Life."""
    if not player.life_cards:
        return True

    def use_callback(selected):
        if not selected or selected[0] != "yes":
            return

        def after_life(added, _life_card):
            if not added or not player.hand:
                return
            hand_snapshot = list(player.hand)

            def hand_callback(hand_selected):
                idx = int(hand_selected[0]) if hand_selected else -1
                if 0 <= idx < len(hand_snapshot):
                    chosen = hand_snapshot[idx]
                    if chosen in player.hand:
                        player.hand.remove(chosen)
                        chosen.is_face_up = False
                        player.life_cards.append(chosen)
                        game_state._log(f"{player.name} added {chosen.name} from hand to the top of Life")

            create_target_choice(
                game_state,
                player,
                hand_snapshot,
                "Choose up to 1 card from your hand to add to the top of your Life",
                source_card=card,
                min_selections=0,
                max_selections=1,
                callback=hand_callback,
            )

        _prompt_take_life_top_or_bottom_to_hand(
            game_state,
            player,
            card,
            "Choose the top or bottom card of your Life cards to add to your hand",
            after_life,
            reveal_card_names=False,
        )

    return _prompt_optional_yes_no(
        game_state,
        player,
        card,
        "Use Heavenly Fire's trigger?",
        "Use trigger",
        use_callback,
    )


# --- OP04-118: Nefeltari Vivi ---
@register_effect("OP04-118", "continuous", "Red Characters cost 3+ gain Rush")
def op04_118_vivi(game_state, player, card):
    """Continuous: Red characters with cost 3+ other than this gain Rush."""
    for c in player.cards_in_play:
        if c != card and 'Red' in _card_colors(c) and (getattr(c, 'cost', 0) or 0) >= 3:
            c.has_rush = True
    return True


# --- OP04-119: Donquixote Rosinante ---
@register_effect("OP04-119", "continuous", "[Opponent's Turn] If rested, cost 5 Characters cannot be K.O.'d by effects")
def op04_119_rosinante_continuous(game_state, player, card):
    """Opponent's Turn: If rested, active cost 5 characters cannot be K.O.'d by effects."""
    if game_state.current_player is get_opponent(game_state, player) and getattr(card, 'is_resting', False):
        for c in player.cards_in_play:
            if not getattr(c, 'is_resting', False) and (getattr(c, 'cost', 0) or 0) == 5:
                c.cannot_be_ko_by_effects = True
    return True


@register_effect("OP04-119", "on_play", "[On Play] Rest to play cost 5 green Character")
def op04_119_rosinante_play(game_state, player, card):
    """On Play: Rest this to play cost 5 green Character from hand."""
    targets = [
        c for c in player.hand
        if 'Green' in _card_colors(c) and (getattr(c, 'cost', 0) or 0) == 5
    ]
    if not targets:
        return True

    def callback(selected):
        if not selected:
            return
        card.is_resting = True
        target_idx = int(selected[0]) if selected else -1
        if 0 <= target_idx < len(targets):
            chosen = targets[target_idx]
            if chosen in player.hand:
                player.hand.remove(chosen)
                setattr(chosen, 'played_turn', game_state.turn_count)
                player.cards_in_play.append(chosen)
                game_state._apply_keywords(chosen)
                game_state._recalc_continuous_effects()
                game_state._log(f"{player.name} played {chosen.name} from hand")
                if chosen.effect and '[On Play]' in chosen.effect:
                    game_state._trigger_on_play_effects(chosen)

    return create_target_choice(
        game_state, player, targets,
        "Choose up to 1 green Character with cost 5 to play from hand",
        source_card=card, min_selections=0, max_selections=1, callback=callback
    )


# --- OP04-036: Donquixote Family (Event) ---
@register_effect("OP04-036", "counter", "[Counter] Look at 5, reveal Donquixote Pirates card to hand")
def op04_036_donquixote_family(game_state, player, card):
    """[Counter] Look at 5 cards from top of deck; reveal up to 1 Donquixote Pirates
    type card and add to hand. Rest at bottom."""
    def filter_fn(c):
        return 'donquixote pirates' in (c.card_origin or '').lower()
    return search_top_cards(
        game_state, player, look_count=5, add_count=1,
        filter_fn=filter_fn, source_card=card,
        prompt="Look at top 5: choose 1 Donquixote Pirates card to add to hand")


@register_effect("OP04-036", "trigger", "[Trigger] Activate this card's [Counter] effect")
def op04_036_donquixote_family_trigger(game_state, player, card):
    """Trigger: Activate this card's [Counter] effect."""
    return op04_036_donquixote_family(game_state, player, card)


# --- OP04-037: Flapping Thread ---
@register_effect("OP04-037", "counter", "[Counter] If your Leader has Donquixote Pirates, up to 1 gains +2000 for the turn")
def op04_037_flapping_thread(game_state, player, card):
    """Counter: If your Leader is Donquixote Pirates, choose up to 1 Leader or Character to gain +2000 this turn."""
    if not (player.leader and 'Donquixote Pirates' in (player.leader.card_origin or '')):
        return True

    targets = _own_leader_and_characters(player)

    def callback(selected):
        target_idx = int(selected[0]) if selected else -1
        if 0 <= target_idx < len(targets):
            target = targets[target_idx]
            add_power_modifier(target, 2000)
            target.power_modifier_expires_on_turn = game_state.turn_count
            target._sticky_power_modifier_expires_on_turn = game_state.turn_count
            game_state._log(f"{target.name} gets +2000 power during this turn")

    if targets:
        return create_target_choice(
            game_state,
            player,
            targets,
            "Choose up to 1 of your Leader or Character cards to gain +2000 power during this turn",
            source_card=card,
            min_selections=0,
            max_selections=1,
            callback=callback,
        )
    return True


# --- OP04-038: The Weak Do Not Have the Right to Choose How They Die!!! ---
def _op04_038_resolve(game_state, player, card):
    targets = [c for c in _opponent_leader_and_characters(game_state, player) if not getattr(c, 'is_resting', False)]

    def rest_callback(selected):
        if not _rest_selected_targets(game_state, targets, selected):
            return
        opponent = get_opponent(game_state, player)
        ko_targets = [
            c for c in opponent.cards_in_play
            if getattr(c, 'is_resting', False) and (getattr(c, 'cost', 0) or 0) <= 6
        ]
        if ko_targets:
            create_ko_choice(
                game_state,
                player,
                ko_targets,
                source_card=card,
                prompt="Choose up to 1 opponent's rested cost 6 or less Character to K.O.",
                min_selections=0,
            )

    if targets:
        return create_target_choice(
            game_state,
            player,
            targets,
            "Choose up to 1 opponent's Leader or Character card to rest",
            source_card=card,
            min_selections=0,
            max_selections=1,
            callback=rest_callback,
        )
    return True


@register_effect("OP04-038", "on_play", "[Main] Rest up to 1 opponent Leader or Character, then K.O. rested cost 6 or less")
def op04_038_the_weak_main(game_state, player, card):
    """Main: Rest up to 1 opponent Leader or Character, then K.O. a rested cost 6 or less Character."""
    return _op04_038_resolve(game_state, player, card)


@register_effect("OP04-038", "counter", "[Counter] Rest up to 1 opponent Leader or Character, then K.O. rested cost 6 or less")
def op04_038_the_weak_counter(game_state, player, card):
    """Counter: Rest up to 1 opponent Leader or Character, then K.O. a rested cost 6 or less Character."""
    return _op04_038_resolve(game_state, player, card)


@register_effect("OP04-038", "trigger", "[Trigger] Set up to 5 of your DON!! cards as active")
def op04_038_the_weak_trigger(game_state, player, card):
    """Trigger: Set up to 5 of your rested DON!! cards as active."""
    rested_indices = [idx for idx, don in enumerate(getattr(player, 'don_pool', [])) if don == "rested"]
    if not rested_indices:
        return True

    def callback(selected):
        activated = _set_selected_don_state(player, selected, "rested", "active")
        if activated:
            game_state._log(f"{player.name} set {activated} DON!! card(s) as active")

    return _choose_player_don_by_state(
        game_state,
        player,
        player,
        "rested",
        "Choose up to 5 of your rested DON!! cards to set as active",
        callback,
        source_card=card,
        min_selections=0,
        max_selections=min(5, len(rested_indices)),
    )
