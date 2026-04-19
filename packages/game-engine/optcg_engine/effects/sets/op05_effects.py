"""
Hardcoded effects for OP05 cards.
"""

import random
import uuid

from ..effect_registry import (
    add_don_from_deck, add_power_modifier, check_life_count, check_leader_type,
    check_trash_count, create_add_from_trash_choice, create_add_to_life_choice,
    create_bottom_deck_choice, create_cannot_attack_choice, create_cost_reduction_choice,
    create_hand_discard_choice, create_ko_choice, create_mode_choice, create_own_character_choice,
    create_play_from_hand_choice, create_power_effect_choice, create_rest_choice,
    create_return_to_hand_choice, create_set_active_choice, create_target_choice,
    draw_cards, filter_by_max_cost, get_opponent, ko_opponent_character, register_effect,
    reorder_top_cards, return_don_to_deck, search_top_cards, trash_from_hand,
)

create_power_reduction_choice = create_power_effect_choice


def _is_character(card):
    return getattr(card, "card_type", "") == "CHARACTER"


def _has_type(card, type_name):
    return type_name.lower() in (getattr(card, "card_origin", "") or "").lower()


def _effective_cost(card):
    return max(0, (getattr(card, "cost", 0) or 0) + getattr(card, "cost_modifier", 0))


def _effective_power(card):
    return max(
        0,
        (getattr(card, "power", 0) or 0)
        + getattr(card, "power_modifier", 0)
        + (getattr(card, "attached_don", 0) or 0) * 1000,
    )


def _add_battle_power(game_state, target, amount):
    target.power_modifier = getattr(target, "power_modifier", 0) + amount
    target._battle_power_modifier = getattr(target, "_battle_power_modifier", 0) + amount
    sign = "+" if amount >= 0 else ""
    game_state._log(f"{target.name} gets {sign}{amount} power during this battle")


def _queue_top_or_bottom_any_order(game_state, player, cards, source_card=None):
    from ...game_engine import PendingChoice

    source_name = source_card.name if source_card else ""
    source_id = source_card.id if source_card else ""

    def queue_next(cards_left):
        snapshot = list(cards_left)
        if not snapshot:
            return

        options = []
        for i, pending_card in enumerate(snapshot):
            options.append({
                "id": str(i),
                "label": f"{pending_card.name} (Cost: {getattr(pending_card, 'cost', 0) or 0})",
                "card_id": pending_card.id,
                "card_name": pending_card.name,
            })

        def choose_card_cb(selected):
            card_idx = int(selected[0]) if selected else -1
            if not (0 <= card_idx < len(snapshot)):
                return
            chosen = snapshot.pop(card_idx)

            def place_cb(mode_selected):
                placement = mode_selected[0] if mode_selected else "bottom"
                if placement == "top":
                    player.deck.insert(0, chosen)
                    game_state._log(f"{source_name}: {chosen.name} placed on TOP of deck")
                else:
                    player.deck.append(chosen)
                    game_state._log(f"{source_name}: {chosen.name} placed at BOTTOM of deck")
                queue_next(snapshot)

            create_mode_choice(
                game_state,
                player,
                modes=[
                    {"id": "top", "label": "Top", "description": f"Place {chosen.name} on top of your deck"},
                    {"id": "bottom", "label": "Bottom", "description": f"Place {chosen.name} at the bottom of your deck"},
                ],
                source_card=source_card,
                prompt=f"{source_name}: Choose where to place {chosen.name}",
                callback=place_cb,
            )

        game_state.pending_choice = PendingChoice(
            choice_id=f"op05_top_bottom_{uuid.uuid4().hex[:8]}",
            choice_type="select_target",
            prompt=f"{source_name}: Choose the next card to place at the top or bottom of your deck",
            options=options,
            min_selections=1,
            max_selections=1,
            source_card_id=source_id,
            source_card_name=source_name,
            callback=choose_card_cb,
        )

    queue_next(list(cards))
    return True


def _queue_bottom_from_hand_any_order(game_state, player, cards, count, source_card=None):
    from ...game_engine import PendingChoice

    source_name = source_card.name if source_card else ""
    source_id = source_card.id if source_card else ""
    exact_count = min(count, len(cards))
    if exact_count <= 0:
        return True

    def queue_next(remaining, ordered):
        if len(ordered) >= exact_count or not remaining:
            for chosen in reversed(ordered):
                player.deck.append(chosen)
                game_state._log(f"{chosen.name} was placed at the bottom of your deck")
            return

        snapshot = list(remaining)
        options = []
        for i, hand_card in enumerate(snapshot):
            options.append({
                "id": str(i),
                "label": f"{hand_card.name} (Cost: {getattr(hand_card, 'cost', 0) or 0})",
                "card_id": hand_card.id,
                "card_name": hand_card.name,
            })

        def choose_cb(selected):
            idx = int(selected[0]) if selected else -1
            if not (0 <= idx < len(snapshot)):
                return
            chosen = snapshot.pop(idx)
            if chosen in player.hand:
                player.hand.remove(chosen)
            queue_next(snapshot, ordered + [chosen])

        game_state.pending_choice = PendingChoice(
            choice_id=f"op05_hand_bottom_{uuid.uuid4().hex[:8]}",
            choice_type="select_target",
            prompt=f"{source_name}: Choose card {len(ordered) + 1} of {exact_count} to place at the bottom of your deck (first chosen = deepest)",
            options=options,
            min_selections=1,
            max_selections=1,
            source_card_id=source_id,
            source_card_name=source_name,
            callback=choose_cb,
        )

    queue_next(list(cards), [])
    return True


def _queue_bottom_from_trash_any_order(game_state, player, count, source_card=None, on_complete=None):
    from ...game_engine import PendingChoice

    source_name = source_card.name if source_card else ""
    source_id = source_card.id if source_card else ""
    exact_count = min(count, len(player.trash))
    if exact_count <= 0:
        if on_complete:
            on_complete()
        return True

    def queue_next(remaining, ordered):
        if len(ordered) >= exact_count or not remaining:
            for chosen in reversed(ordered):
                if chosen in player.trash:
                    player.trash.remove(chosen)
                    player.deck.append(chosen)
                    game_state._log(f"{chosen.name} was placed at the bottom of {player.name}'s deck")
            if on_complete:
                on_complete()
            return

        snapshot = list(remaining)
        options = []
        for i, trash_card in enumerate(snapshot):
            options.append({
                "id": str(i),
                "label": f"{trash_card.name} (Cost: {getattr(trash_card, 'cost', 0) or 0})",
                "card_id": trash_card.id,
                "card_name": trash_card.name,
            })

        def choose_cb(selected):
            idx = int(selected[0]) if selected else -1
            if not (0 <= idx < len(snapshot)):
                return
            chosen = snapshot.pop(idx)
            queue_next(snapshot, ordered + [chosen])

        game_state.pending_choice = PendingChoice(
            choice_id=f"op05_trash_bottom_{uuid.uuid4().hex[:8]}",
            choice_type="select_target",
            prompt=f"{source_name}: Choose card {len(ordered) + 1} of {exact_count} from {player.name}'s trash to place at the bottom of the deck (first chosen = deepest)",
            options=options,
            min_selections=1,
            max_selections=1,
            source_card_id=source_id,
            source_card_name=source_name,
            callback=choose_cb,
        )

    queue_next(list(player.trash), [])
    return True


def _queue_bottom_from_field_any_order(game_state, player, cards, source_card=None, on_complete=None):
    from ...game_engine import PendingChoice

    source_name = source_card.name if source_card else ""
    source_id = source_card.id if source_card else ""
    exact_cards = list(cards)
    if not exact_cards:
        if on_complete:
            on_complete()
        return True

    def queue_next(remaining, ordered):
        if not remaining:
            for chosen in reversed(ordered):
                if chosen in player.cards_in_play:
                    player.cards_in_play.remove(chosen)
                    player.deck.append(chosen)
                    game_state._log(f"{chosen.name} was placed at the bottom of your deck")
            if on_complete:
                on_complete()
            return

        snapshot = list(remaining)
        options = []
        for i, field_card in enumerate(snapshot):
            options.append({
                "id": str(i),
                "label": f"{field_card.name} (Cost: {getattr(field_card, 'cost', 0) or 0})",
                "card_id": field_card.id,
                "card_name": field_card.name,
            })

        def choose_cb(selected):
            idx = int(selected[0]) if selected else -1
            if not (0 <= idx < len(snapshot)):
                return
            chosen = snapshot.pop(idx)
            queue_next(snapshot, ordered + [chosen])

        game_state.pending_choice = PendingChoice(
            choice_id=f"op05_field_bottom_{uuid.uuid4().hex[:8]}",
            choice_type="select_target",
            prompt=f"{source_name}: Choose card {len(ordered) + 1} of {len(exact_cards)} to place at the bottom of your deck (first chosen = deepest)",
            options=options,
            min_selections=1,
            max_selections=1,
            source_card_id=source_id,
            source_card_name=source_name,
            callback=choose_cb,
        )

    queue_next(exact_cards, [])
    return True


def _add_turn_power(game_state, target, amount):
    add_power_modifier(target, amount)
    target.power_modifier_expires_on_turn = game_state.turn_count
    target._sticky_power_modifier_expires_on_turn = game_state.turn_count
    sign = "+" if amount >= 0 else ""
    game_state._log(f"{target.name} gets {sign}{amount} power during this turn")


def _prompt_exact_hand_trash_local(game_state, player, count, source_card, prompt, after_callback=None):
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
            "label": f"{temp_card.name} (Cost: {temp_card.cost or 0})",
            "card_id": temp_card.id,
            "card_name": temp_card.name,
        }
        for i, temp_card in enumerate(hand_snapshot)
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
        choice_id=f"op05_trash_{uuid.uuid4().hex[:8]}",
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


def _own_leader_and_characters(player):
    targets = []
    if getattr(player, "leader", None):
        targets.append(player.leader)
    targets.extend([c for c in player.cards_in_play if _is_character(c)])
    return targets


def _opponent_leader_and_characters(game_state, player):
    opponent = get_opponent(game_state, player)
    targets = []
    if getattr(opponent, "leader", None):
        targets.append(opponent.leader)
    targets.extend([c for c in opponent.cards_in_play if _is_character(c)])
    return targets


def _free_don_count(player):
    attached_total = sum(getattr(c, "attached_don", 0) for c in player.cards_in_play)
    if getattr(player, "leader", None):
        attached_total += getattr(player.leader, "attached_don", 0)
    return max(0, len(player.don_pool) - attached_total)


def _rest_active_don(player, count=1):
    indices = []
    for idx in range(_free_don_count(player)):
        if player.don_pool[idx] == "active":
            indices.append(idx)
            if len(indices) == count:
                break
    if len(indices) < count:
        return False
    for idx in indices:
        player.don_pool[idx] = "rested"
    return True


def _set_rested_don_active(player, count=1):
    changed = 0
    for idx in range(_free_don_count(player)):
        if player.don_pool[idx] == "rested":
            player.don_pool[idx] = "active"
            changed += 1
            if changed == count:
                break
    return changed


def _attach_rested_don(player, target, count):
    moved = 0
    while moved < count:
        free_count = _free_don_count(player)
        rest_idx = next((i for i in range(free_count) if player.don_pool[i] == "rested"), None)
        if rest_idx is None:
            break
        player.don_pool.pop(rest_idx)
        player.don_pool.append("rested")
        target.attached_don = getattr(target, "attached_don", 0) + 1
        moved += 1
    return moved


def _create_rested_don_attach_choice(game_state, player, targets, don_count, source_card=None, prompt=None):
    snapshot = list(targets)
    available = sum(1 for i in range(_free_don_count(player)) if player.don_pool[i] == "rested")
    if not snapshot or available <= 0:
        return False

    def callback(selected):
        target_idx = int(selected[0]) if selected else -1
        if 0 <= target_idx < len(snapshot):
            target = snapshot[target_idx]
            attached = _attach_rested_don(player, target, min(don_count, available))
            if attached:
                game_state._log(f"{attached} rested DON!! were attached to {target.name}")

    return create_target_choice(
        game_state, player, snapshot,
        prompt=prompt or f"Choose a Leader or Character to give up to {don_count} rested DON!!",
        source_card=source_card,
        callback=callback,
    )


def _bottom_trash_to_deck(player, count):
    if len(player.trash) < count:
        return False
    moved = player.trash[-count:]
    del player.trash[-count:]
    player.deck.extend(moved)
    return True


def _is_multicolor_leader(player):
    return len(getattr(getattr(player, "leader", None), "colors", [])) > 1


def _only_celestial_dragons(player):
    characters = [c for c in player.cards_in_play if _is_character(c)]
    return all(_has_type(c, "Celestial Dragons") for c in characters)


def _queue_multicolor_trigger_play(game_state, player, card):
    """Trigger helper for cards that can be played by trashing 1 card with a multicolored Leader."""
    if not _is_multicolor_leader(player) or not player.hand:
        return False

    hand_snapshot = list(player.hand)

    def discard_callback(selected):
        target_idx = int(selected[0]) if selected else -1
        if 0 <= target_idx < len(hand_snapshot):
            discarded = hand_snapshot[target_idx]
            if discarded in player.hand:
                player.hand.remove(discarded)
                player.trash.append(discarded)
                game_state._log(f"{player.name} trashed {discarded.name}")
        card.is_resting = False
        setattr(card, "played_turn", game_state.turn_count)
        player.cards_in_play.append(card)
        game_state._apply_keywords(card)
        game_state._log(f"{card.name} is played from trigger")
        game_state._complete_trigger_followup(played=True)

    def mode_callback(selected):
        if selected and selected[0] == "use":
            create_hand_discard_choice(
                game_state,
                player,
                hand_snapshot,
                source_card=card,
                prompt="Choose 1 card from your hand to trash to play this card",
                callback=discard_callback,
            )
            return
        game_state._complete_trigger_followup()

    return create_mode_choice(
        game_state,
        player,
        modes=[
            {"id": "use", "label": "Trash 1", "description": "Trash 1 card from your hand and play this card"},
            {"id": "skip", "label": "Skip", "description": "Do not use this trigger"},
        ],
        source_card=card,
        prompt="Trash 1 card from your hand to play this card?",
        callback=mode_callback,
    )


# --- OP05-040: Birdcage ---
@register_effect("OP05-040", "continuous", "If your Leader is Donquixote Doflamingo, cost 5 or less Characters do not become active")
def op05_040_birdcage_continuous(game_state, player, card):
    if getattr(getattr(player, "leader", None), "name", "") != "Donquixote Doflamingo":
        return False
    for p_ in [player, get_opponent(game_state, player)]:
        for char in p_.cards_in_play:
            if _is_character(char) and _effective_cost(char) <= 5:
                char.birdcage_lock = True
    return True


@register_effect("OP05-040", "END_OF_TURN", "If 10 DON, KO all rested cost 5 or less Characters")
def birdcage_effect(game_state, player, card):
    if len(player.don_pool) >= 10:
        opponent = get_opponent(game_state, player)
        queue = [
            c for p_ in [player, opponent]
            for c in p_.cards_in_play
            if c is not card and _is_character(c) and getattr(c, 'is_resting', False) and _effective_cost(c) <= 5
        ]

        def finish():
            if card in player.cards_in_play:
                player.cards_in_play.remove(card)
                player.trash.append(card)
                game_state._log(f"{card.name} was trashed")

        def ko_next(pending):
            if not pending:
                finish()
                return
            target = pending.pop(0)
            if target not in player.cards_in_play and target not in opponent.cards_in_play:
                ko_next(pending)
                return
            game_state._attempt_character_ko(
                target,
                by_effect=True,
                controller=player,
                after_resolve=lambda *_args: ko_next(pending),
            )

        if queue:
            ko_next(list(queue))
        else:
            finish()
        return True
    return False


# --- OP05-031: Buffalo ---
@register_effect("OP05-031", "WHEN_ATTACKING", "If 2+ rested chars, set 1 cost 1 rested char active")
def buffalo_effect(game_state, player, card):
    rested = [c for c in player.cards_in_play if _is_character(c) and getattr(c, "is_resting", False)]
    if len(rested) < 2:
        return False
    targets = [c for c in rested if (getattr(c, "cost", 0) or 0) == 1]
    if not targets:
        return False

    def callback(selected):
        if not selected:
            return
        target_idx = int(selected[0]) if selected[0] is not None else -1
        if 0 <= target_idx < len(targets):
            target = targets[target_idx]
            target.is_resting = False
            target.has_attacked = False
            game_state._log(f"{target.name} was set active")
            card.op05_031_used = True

    return create_set_active_choice(
        game_state,
        player,
        targets,
        source_card=card,
        prompt="Choose up to 1 of your rested cost 1 Characters to set active",
        callback=callback,
        min_selections=0,
        max_selections=1,
    )


# =============================================================================
# EXTRA TURN EFFECTS
# =============================================================================

@register_effect("OP05-119", "ACTIVATE_MAIN", "Add 1 DON from DON deck and set active")
def luffy_gear5_activate(game_state, player, card):
    """Legacy activate timing hook for the same effect."""
    if getattr(card, 'luffy_activate_used', False):
        return False
    if not _rest_active_don(player, 1):
        return False
    add_don_from_deck(player, 1, set_active=True)
    card.luffy_activate_used = True
    return True


# --- OP05-086: Nefeltari Vivi ---
@register_effect("OP05-086", "PASSIVE", "If 10+ cards in trash, gains Blocker")
def op05_086_vivi(game_state, player, card):
    if check_trash_count(player, 10, 'ge'):
        card.has_blocker = True
    return True


# --- OP05-096: I Bid 500 Million!! ---
@register_effect("OP05-096", "MAIN", "Choose: KO cost 1 OR return cost 1 to hand OR place cost 1 at bottom of deck")
def op05_096_500_million(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if _is_character(c) and _effective_cost(c) <= 1]
    if targets:
        def draw_if_celestial_dragons():
            if any(_has_type(c, "Celestial Dragons") for c in player.cards_in_play if _is_character(c)):
                draw_cards(player, 1, game_state=game_state)

        def return_target_to_hand(target):
            for owner in [player, get_opponent(game_state, player)]:
                if target in owner.cards_in_play:
                    owner.cards_in_play.remove(target)
                    owner.hand.append(target)
                    game_state._log(f"{target.name} returned to hand")
                    return

        def place_target_in_life(target, position):
            target_owner = get_opponent(game_state, player)
            if target in target_owner.cards_in_play:
                target_owner.cards_in_play.remove(target)
                target.is_face_up = True
                if position == "bottom":
                    target_owner.life_cards.insert(0, target)
                else:
                    target_owner.life_cards.append(target)
                game_state._log(f"{target.name} was added to {target_owner.name}'s Life face-up at the {position}")

        modes = [
            {"id": "ko", "label": "KO Character", "description": "KO opponent's cost 1 or less Character"},
            {"id": "return", "label": "Return to Hand", "description": "Return opponent's cost 1 or less Character to hand"},
            {"id": "life_top", "label": "Top Life", "description": "Place opponent's cost 1 or less Character at the top of their Life cards face-up"},
            {"id": "life_bottom", "label": "Bottom Life", "description": "Place opponent's cost 1 or less Character at the bottom of their Life cards face-up"},
        ]

        def callback(selected: list[str]) -> None:
            selected_mode = selected[0] if selected else None
            mode_targets = [c for c in get_opponent(game_state, player).cards_in_play if _is_character(c) and _effective_cost(c) <= 1]
            if not mode_targets:
                draw_if_celestial_dragons()
                return
            if selected_mode == "ko":
                def ko_callback(chosen):
                    for sel in chosen:
                        idx = int(sel)
                        if 0 <= idx < len(mode_targets):
                            game_state._attempt_character_ko(mode_targets[idx], by_effect=True)
                    draw_if_celestial_dragons()

                create_ko_choice(
                    game_state,
                    player,
                    mode_targets,
                    source_card=card,
                    min_selections=0,
                    max_selections=1,
                    prompt="Choose up to 1 opponent Character with cost 1 or less to K.O.",
                    callback=ko_callback,
                )
            elif selected_mode == "return":
                def return_callback(chosen):
                    if chosen:
                        idx = int(chosen[0])
                        if 0 <= idx < len(mode_targets):
                            return_target_to_hand(mode_targets[idx])
                    draw_if_celestial_dragons()

                create_return_to_hand_choice(
                    game_state,
                    player,
                    mode_targets,
                    source_card=card,
                    optional=True,
                    prompt="Choose up to 1 opponent Character with cost 1 or less to return to hand",
                    callback=return_callback,
                )
            elif selected_mode == "life_top":
                def top_life_callback(chosen):
                    if chosen:
                        idx = int(chosen[0])
                        if 0 <= idx < len(mode_targets):
                            place_target_in_life(mode_targets[idx], "top")
                    draw_if_celestial_dragons()

                create_add_to_life_choice(
                    game_state,
                    player,
                    mode_targets,
                    source_card=card,
                    owner="opponent",
                    position="top",
                    face_up=True,
                    prompt="Choose up to 1 opponent Character with cost 1 or less to place at the top of their Life cards face-up",
                    callback=top_life_callback,
                )
            elif selected_mode == "life_bottom":
                def bottom_life_callback(chosen):
                    if chosen:
                        idx = int(chosen[0])
                        if 0 <= idx < len(mode_targets):
                            place_target_in_life(mode_targets[idx], "bottom")
                    draw_if_celestial_dragons()

                create_add_to_life_choice(
                    game_state,
                    player,
                    mode_targets,
                    source_card=card,
                    owner="opponent",
                    position="bottom",
                    face_up=True,
                    prompt="Choose up to 1 opponent Character with cost 1 or less to place at the bottom of their Life cards face-up",
                    callback=bottom_life_callback,
                )
            else:
                draw_if_celestial_dragons()

        return create_mode_choice(game_state, player, modes, source_card=card, callback=callback,
                                   prompt="Choose one effect for I Bid 500 Million!!")
    return True


@register_effect("OP05-096", "trigger", "[Trigger] K.O. cost 6 or less or return it to hand")
def op05_096_500_million_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if _is_character(c) and _effective_cost(c) <= 6]
    if not targets:
        return True

    def callback(selected):
        mode = selected[0] if selected else None
        fresh_targets = [c for c in get_opponent(game_state, player).cards_in_play if _is_character(c) and _effective_cost(c) <= 6]
        if not fresh_targets:
            return
        if mode == "ko":
            create_ko_choice(
                game_state, player, fresh_targets, source_card=card,
                min_selections=0, max_selections=1,
                prompt="Choose up to 1 opponent Character with cost 6 or less to K.O."
            )
        elif mode == "return":
            create_return_to_hand_choice(
                game_state, player, fresh_targets, source_card=card,
                optional=True,
                prompt="Choose up to 1 opponent Character with cost 6 or less to return to hand"
            )

    return create_mode_choice(
        game_state, player,
        modes=[
            {"id": "ko", "label": "KO", "description": "K.O. an opponent Character with cost 6 or less"},
            {"id": "return", "label": "Return", "description": "Return an opponent Character with cost 6 or less to hand"},
        ],
        source_card=card,
        prompt="Choose the trigger effect for I Bid 500 Million!!",
        callback=callback,
    )


# --- OP05-019: Fire Fist ---
@register_effect("OP05-019", "MAIN", "-4000 power, KO 0 power if 2 or less life")
def op05_019_fire_fist(game_state, player, card):
    """Main: -4000 power to up to 1 opponent Character, then maybe K.O. 0 power Characters."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if _is_character(c)]

    def queue_ko_choice():
        if not check_life_count(player, 2):
            return
        ko_targets = [c for c in opponent.cards_in_play if _is_character(c) and _effective_power(c) <= 0]
        if not ko_targets:
            return

        snapshot = list(ko_targets)

        def ko_callback(selected):
            target_idx = int(selected[0]) if selected else -1
            if 0 <= target_idx < len(snapshot):
                game_state._attempt_character_ko(snapshot[target_idx], by_effect=True, controller=player)

        create_ko_choice(
            game_state,
            player,
            snapshot,
            source_card=card,
            min_selections=0,
            max_selections=1,
            prompt="Choose up to 1 opponent Character with 0 power or less to K.O.",
            callback=ko_callback,
        )

    def callback(selected):
        if selected:
            target = targets[int(selected[0])]
            add_power_modifier(target, -4000)
        queue_ko_choice()

    if targets:
        return create_target_choice(
            game_state, player, targets,
            prompt="Choose up to 1 opponent Character to give -4000 power",
            source_card=card,
            min_selections=0,
            max_selections=1,
            callback=callback,
        )
    callback([])
    return True


@register_effect("OP05-019", "trigger", "[Trigger] Activate this card's Main effect")
def op05_019_fire_fist_trigger(game_state, player, card):
    """Trigger: activate this card's Main effect."""
    return op05_019_fire_fist(game_state, player, card)


# --- OP05-114: El Thor ---
@register_effect("OP05-114", "COUNTER", "+2000 power, +2000 more if opponent has 2 or less life")
def op05_114_el_thor(game_state, player, card):
    """Counter: +2000 power, then possibly +2000 more."""
    opponent = get_opponent(game_state, player)
    targets = _own_leader_and_characters(player)

    def callback(selected):
        if not selected:
            return
        target = targets[int(selected[0])]
        _add_battle_power(game_state, target, 2000)
        if len(opponent.life_cards) <= 2:
            _add_battle_power(game_state, target, 2000)

    return create_target_choice(
        game_state, player, targets,
        prompt="Choose up to 1 of your Leader or Character cards to gain +2000 power",
        source_card=card,
        min_selections=0,
        max_selections=1,
        callback=callback,
    )


@register_effect("OP05-114", "trigger", "[Trigger] K.O. cost equal to or less than opponent's Life")
def op05_114_el_thor_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    max_cost = len(opponent.life_cards)
    targets = [c for c in opponent.cards_in_play if _is_character(c) and _effective_cost(c) <= max_cost]
    if not targets:
        return True
    return create_ko_choice(
        game_state, player, targets, source_card=card,
        prompt=f"Choose up to 1 opponent Character with cost {max_cost} or less to K.O."
    )


# --- OP05-115: Two-Hundred Million Volts Amaru ---
@register_effect("OP05-115", "MAIN", "+3000 power, rest opponent's cost 4 or less if 1 or less life")
def op05_115_amaru(game_state, player, card):
    """Main: +3000 power, then maybe rest a cost 4 or less Character."""
    own_targets = _own_leader_and_characters(player)

    def callback(selected):
        if selected:
            _add_turn_power(game_state, own_targets[int(selected[0])], 3000)
        if check_life_count(player, 1):
            opponent = get_opponent(game_state, player)
            rest_targets = [c for c in opponent.cards_in_play if _is_character(c) and not c.is_resting and _effective_cost(c) <= 4]
            if rest_targets:
                create_rest_choice(
                    game_state, player, rest_targets, source_card=card,
                    min_selections=0,
                    max_selections=1,
                    prompt="Choose up to 1 opponent Character with cost 4 or less to rest"
                )

    return create_target_choice(
        game_state, player, own_targets,
        prompt="Choose up to 1 of your Leader or Character cards to gain +3000 power",
        source_card=card,
        min_selections=0,
        max_selections=1,
        callback=callback,
    )


@register_effect("OP05-115", "trigger", "[Trigger] Trash 2 to add top card of deck to Life")
def op05_115_amaru_trigger(game_state, player, card):
    if len(player.hand) < 2 or not player.deck:
        return False

    def finish_trigger(_trashed_cards):
        if player.deck:
            life_card = player.deck.pop(0)
            setattr(life_card, "is_face_up", False)
            player.life_cards.append(life_card)
            game_state._log(f"{player.name} added a card from the top of the deck to Life")

    return create_mode_choice(
        game_state, player,
        modes=[
            {"id": "pay", "label": "Trash 2", "description": "Trash 2 cards from hand and add the top card of your deck to Life"},
            {"id": "skip", "label": "Skip", "description": "Do not use the trigger effect"},
        ],
        source_card=card,
        prompt="Choose whether to trash 2 cards from hand for this trigger",
        callback=lambda selected: _prompt_exact_hand_trash_local(
            game_state,
            player,
            2,
            card,
            "Choose 2 cards from your hand to trash",
            after_callback=finish_trigger,
        ) if selected and selected[0] == "pay" else None,
    )


# --- OP05-095: Dragon Claw ---
@register_effect("OP05-095", "COUNTER", "+4000 power, KO cost 4 or less if 15+ trash")
def op05_095_dragon_claw(game_state, player, card):
    """Counter: +4000 power, then maybe K.O. a cost 4 or less Character."""
    targets = _own_leader_and_characters(player)

    def callback(selected):
        if selected:
            _add_battle_power(game_state, targets[int(selected[0])], 4000)
        if check_trash_count(player, 15):
            opponent = get_opponent(game_state, player)
            ko_targets = [c for c in opponent.cards_in_play if _is_character(c) and _effective_cost(c) <= 4]
            if ko_targets:
                create_ko_choice(
                    game_state, player, ko_targets, source_card=card,
                    min_selections=0,
                    max_selections=1,
                    prompt="Choose up to 1 opponent Character with cost 4 or less to K.O."
                )

    return create_target_choice(
        game_state, player, targets,
        prompt="Choose up to 1 of your Leader or Character cards to gain +4000 power",
        source_card=card,
        min_selections=0,
        max_selections=1,
        callback=callback,
    )


# =============================================================================
# LEADER CARD EFFECTS - OP05 (Awakening of New Era)
# =============================================================================

# --- OP05-001: Sabo (Leader) ---
@register_effect("OP05-001", "on_ko_prevention", "[DON!! x1] [Opponent's Turn] 5000+ power char survives at -1000")
def op05_001_sabo_leader(game_state, player, card):
    """DON x1, Opponent's Turn, Once Per Turn: When 5000+ power char would be K.O.'d, it survives at -1000 power."""
    context = getattr(game_state, "_pending_ko_context", None)
    if not context or game_state.current_player is player:
        return False
    if getattr(card, "attached_don", 0) < 1 or getattr(card, "op05_001_used", False):
        return False

    target = game_state._find_in_play_card_by_id(context.get("target_id"))
    if not target or target not in player.cards_in_play or not _is_character(target):
        return False
    if _effective_power(target) < 5000:
        return False

    def callback(selected):
        if selected and selected[0] == "use":
            add_power_modifier(target, -1000)
            card.op05_001_used = True
            game_state._log(f"{target.name} gets -1000 power instead of being K.O.'d")
            game_state._resolve_ko_prevention_choice(True)
            return
        game_state._resolve_ko_prevention_choice(False)

    return create_mode_choice(
        game_state,
        player,
        modes=[
            {"id": "use", "label": "Use effect", "description": f"Give {target.name} -1000 power and prevent the K.O."},
            {"id": "skip", "label": "Skip", "description": "Do not use Sabo's replacement effect"},
        ],
        source_card=card,
        prompt=f"Use {card.name} to give {target.name} -1000 power instead of being K.O.'d?",
        callback=callback,
    )


# --- OP05-002: Belo Betty (Leader) ---
@register_effect("OP05-002", "activate", "[Activate: Main] Trash Rev Army: Up to 3 Rev Army +1000")
def op05_002_betty_leader(game_state, player, card):
    """Once Per Turn: You may trash 1 Revolutionary Army card to buff up to 3 targets."""
    if getattr(card, 'op05_002_used', False):
        return False
    valid_cost_cards = [c for c in player.hand if _has_type(c, 'Revolutionary Army')]
    if not valid_cost_cards:
        return False

    def trash_cb(selected):
        target_idx = int(selected[0]) if selected else -1
        if 0 <= target_idx < len(valid_cost_cards):
            trashed = valid_cost_cards[target_idx]
            if trashed in player.hand:
                player.hand.remove(trashed)
                player.trash.append(trashed)
                game_state._log(f"{player.name} trashed {trashed.name}")
        buff_targets = [
            c for c in player.cards_in_play
            if _is_character(c) and (_has_type(c, 'Revolutionary Army') or bool(getattr(c, 'trigger', '')))
        ]
        if buff_targets:
            create_target_choice(
                game_state,
                player,
                buff_targets,
                source_card=card,
                min_selections=0,
                max_selections=min(3, len(buff_targets)),
                prompt="Choose up to 3 of your {Revolutionary Army} Characters or Characters with a [Trigger] to gain +3000 power during this turn",
                callback=lambda chosen: [
                    _add_turn_power(game_state, buff_targets[int(sel)], 3000)
                    for sel in chosen
                    if 0 <= int(sel) < len(buff_targets)
                ],
            )
        card.op05_002_used = True

    return create_mode_choice(
        game_state, player,
        modes=[
            {"id": "pay", "label": "Trash 1", "description": "Trash a Revolutionary Army card from hand to use the effect"},
            {"id": "skip", "label": "Skip", "description": "Do not use this effect"},
        ],
        source_card=card,
        prompt="Choose whether to trash a Revolutionary Army card from hand",
        callback=lambda selected: create_hand_discard_choice(
            game_state, player, valid_cost_cards,
            source_card=card,
            prompt="Choose a Revolutionary Army card to trash",
            callback=trash_cb,
        ) if selected and selected[0] == "pay" else None,
    )


# --- OP05-022: Donquixote Rosinante (Leader) ---
@register_effect("OP05-022", "blocker", "[Blocker] This Leader has Blocker")
def op05_022_rosinante_blocker(game_state, player, card):
    """This Leader has Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP05-022", "end_of_turn", "[End of Your Turn] If 2+ Donquixote Pirates, draw 2 trash 2")
def op05_022_rosinante_eot(game_state, player, card):
    """End of Your Turn: If you have 6 or fewer cards in hand, set this Leader active."""
    if len(player.hand) <= 6:
        card.is_resting = False
        return True
    return False


# --- OP05-041: Sakazuki (Leader) ---
@register_effect("OP05-041", "activate", "[Activate: Main] Trash 1: Draw 1")
def op05_041_sakazuki_activate(game_state, player, card):
    """Once Per Turn: Trash 1 from hand, draw 1."""
    if hasattr(card, 'op05_041_used') and card.op05_041_used:
        return False
    if not player.hand:
        return False

    hand_snapshot = list(player.hand)

    def discard_cb(selected):
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(hand_snapshot):
            trashed = hand_snapshot[idx]
            if trashed in player.hand:
                player.hand.remove(trashed)
                player.trash.append(trashed)
                game_state._log(f"{player.name} trashed {trashed.name}")
                draw_cards(player, 1, game_state=game_state)
                card.op05_041_used = True

    return create_mode_choice(
        game_state,
        player,
        modes=[
            {"id": "use", "label": "Use effect", "description": "Trash 1 card from your hand to draw 1 card"},
            {"id": "skip", "label": "Skip", "description": "Do not use Sakazuki's effect"},
        ],
        source_card=card,
        prompt="Trash 1 card from your hand to draw 1 card?",
        callback=lambda selected: create_hand_discard_choice(
            game_state,
            player,
            hand_snapshot,
            source_card=card,
            prompt="Choose 1 card from your hand to trash",
            callback=discard_cb,
        ) if selected and selected[0] == "use" else None,
    )


@register_effect("OP05-041", "on_attack", "[When Attacking] Opponent char -1 cost")
def op05_041_sakazuki_attack(game_state, player, card):
    """When Attacking: Give up to 1 opponent's Character -1 cost."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if _is_character(c)]
    if not targets:
        return True
    return create_cost_reduction_choice(
        game_state, player, targets, -1,
        source_card=card,
        min_selections=0,
        max_selections=1,
        prompt="Choose up to 1 opponent Character to give -1 cost"
    )


# --- OP05-060: Monkey.D.Luffy (Leader) ---
@register_effect("OP05-060", "activate", "[Activate: Main] Add life to hand: If 0 or 3+ DON, add 2 DON")
def op05_060_luffy_leader(game_state, player, card):
    """Once Per Turn: You may add 1 Life to hand. If 0 or 3+ DON on field, add 1 active DON."""
    if getattr(card, 'op05_060_used', False):
        return False
    if not player.life_cards:
        return False

    def mode_callback(selected):
        if not selected or selected[0] != "use" or not player.life_cards:
            return
        life = player.life_cards.pop()
        player.hand.append(life)
        don_count = len(player.don_pool)
        if don_count == 0 or don_count >= 3:
            add_don_from_deck(player, 1, set_active=True)
        card.op05_060_used = True

    return create_mode_choice(
        game_state,
        player,
        modes=[
            {"id": "use", "label": "Add 1 Life", "description": "Add the top card of your Life to your hand to use the effect"},
            {"id": "skip", "label": "Skip", "description": "Do not use Monkey.D.Luffy's effect"},
        ],
        source_card=card,
        prompt="Add 1 card from the top of your Life cards to your hand?",
        callback=mode_callback,
    )


# --- OP05-098: Enel (Leader) ---
@register_effect("OP05-098", "on_life_zero", "[Opponent's Turn] When Life becomes 0, add 1 to Life, trash 1 from hand")
def op05_098_enel_leader(game_state, player, card):
    """Opponent's Turn, Once Per Turn: When Life becomes 0, add 1 from deck to Life, then trash 1 from hand."""
    if hasattr(card, 'op05_098_used') and card.op05_098_used:
        return False
    if game_state.current_player is not player and player.deck:
        top_card = player.deck.pop(0)
        player.life_cards.append(top_card)
        if player.hand:
            trash_from_hand(player, 1, game_state, card)
        card.op05_098_used = True
        return True
    return False


# =============================================================================
# OP05 CHARACTER EFFECTS - Awakening of the New Era
# =============================================================================

# --- OP05-003: Inazuma ---
@register_effect("OP05-003", "continuous", "Gains Rush if you have 7000+ power Character")
def op05_003_inazuma(game_state, player, card):
    """Continuous: Gains Rush if you have another Character with 7000+ power."""
    has_7k = any(_effective_power(c) >= 7000 for c in player.cards_in_play if c != card and _is_character(c))
    card.has_rush = has_7k
    return True


# --- OP05-004: Emporio.Ivankov ---
@register_effect("OP05-004", "activate", "[Activate: Main] [Once Per Turn] If 7000+ power, play Revolutionary Army 5000 or less")
def op05_004_ivankov(game_state, player, card):
    """Activate: If this has 7000+ power, play Revolutionary Army with 5000 or less power."""
    if getattr(card, "op05_004_used", False) or _effective_power(card) < 7000:
        return False

    targets = [
        c for c in player.hand
        if _is_character(c)
        and _has_type(c, "Revolutionary Army")
        and getattr(c, "name", "") != "Emporio.Ivankov"
        and (getattr(c, "power", 0) or 0) <= 5000
    ]
    if targets:
        card.op05_004_used = True
        return create_play_from_hand_choice(
            game_state,
            player,
            targets,
            source_card=card,
            rest_on_play=False,
            prompt="Choose up to 1 Revolutionary Army Character with 5000 power or less to play from hand",
        )
    return False


# --- OP05-005: Karasu ---
@register_effect("OP05-005", "on_play", "[On Play] If Revolutionary Army Leader, -1000 power")
def op05_005_karasu_play(game_state, player, card):
    """On Play: If Revolutionary Army Leader, give -1000 power."""
    if player.leader and 'Revolutionary Army' in (player.leader.card_origin or ''):
        targets = _opponent_leader_and_characters(game_state, player)
        if targets:
            return create_power_reduction_choice(
                game_state,
                player,
                targets,
                -1000,
                source_card=card,
                min_selections=0,
                max_selections=1,
                prompt="Choose up to 1 opponent Leader or Character to give -1000 power",
            )
    return True


@register_effect("OP05-005", "on_attack", "[When Attacking] If 7000+ power, -1000 power")
def op05_005_karasu_attack(game_state, player, card):
    """When Attacking: If 7000+ power, give -1000 power."""
    if _effective_power(card) >= 7000:
        targets = _opponent_leader_and_characters(game_state, player)
        if targets:
            return create_power_reduction_choice(
                game_state,
                player,
                targets,
                -1000,
                source_card=card,
                min_selections=0,
                max_selections=1,
                prompt="Choose up to 1 opponent Leader or Character to give -1000 power",
            )
    return True


# --- OP05-006: Koala ---
@register_effect("OP05-006", "on_play", "[On Play] If Revolutionary Army Leader, -3000 power to Character")
def op05_006_koala(game_state, player, card):
    """On Play: If Revolutionary Army Leader, give Character -3000 power."""
    if player.leader and 'Revolutionary Army' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if _is_character(c)]
        if targets:
            return create_target_choice(
                game_state,
                player,
                targets,
                source_card=card,
                min_selections=0,
                max_selections=1,
                prompt="Choose up to 1 opponent Character to give -3000 power during this turn",
                callback=lambda chosen: _add_turn_power(game_state, targets[int(chosen[0])], -3000) if chosen else None,
            )
    return True


# --- OP05-007: Sabo ---
@register_effect("OP05-007", "on_play", "[On Play] K.O. up to 2 Characters with total 4000 power or less")
def op05_007_sabo(game_state, player, card):
    """On Play: K.O. up to 2 Characters with total 4000 power or less."""
    opponent = get_opponent(game_state, player)
    targets = sorted([c for c in opponent.cards_in_play if _is_character(c)], key=_effective_power)
    if not targets:
        return True

    snapshot = list(targets)

    def recreate_choice():
        return create_target_choice(
            game_state,
            player,
            snapshot,
            prompt="Choose up to 2 opponent Characters with a total power of 4000 or less to K.O.",
            source_card=card,
            min_selections=0,
            max_selections=min(2, len(snapshot)),
            callback=callback,
        )

    def ko_next(queue):
        if not queue:
            return
        target = queue.pop(0)
        game_state._attempt_character_ko(
            target,
            by_effect=True,
            controller=player,
            after_resolve=lambda *_args: ko_next(queue),
        )

    def callback(selected):
        chosen = []
        total_power = 0
        for sel in selected:
            idx = int(sel)
            if 0 <= idx < len(snapshot):
                target = snapshot[idx]
                if target not in chosen:
                    chosen.append(target)
                    total_power += _effective_power(target)
        if len(chosen) > 2 or total_power > 4000:
            game_state._log("Selected targets must total 4000 power or less.")
            recreate_choice()
            return
        ko_next(list(chosen))

    return recreate_choice()


# --- OP05-008: Chaka ---
@register_effect("OP05-008", "activate", "[DON!! x1] [Activate: Main] [Once Per Turn] Give 2 rested DON to Leader or Character")
def op05_008_chaka(game_state, player, card):
    """With 1 DON: Give up to 2 rested DON to Leader or Character."""
    attached = getattr(card, 'attached_don', 0)
    if attached >= 1 and not getattr(card, 'op05_008_used', False):
        available = sum(1 for i in range(_free_don_count(player)) if player.don_pool[i] == "rested")
        targets = _own_leader_and_characters(player)
        if targets and available:
            card.op05_008_used = True
            return _create_rested_don_attach_choice(
                game_state, player, targets, min(2, available), source_card=card,
                prompt="Choose a Leader or Character to give up to 2 rested DON!!"
            )
    return False


# --- OP05-009: Toh-Toh ---
@register_effect("OP05-009", "on_play", "[On Play] Draw 1 if Leader has 0 or less power")
def op05_009_tohtoh(game_state, player, card):
    """On Play: Draw 1 if Leader has 0 or less power."""
    if player.leader:
        if _effective_power(player.leader) <= 0:
            draw_cards(player, 1, game_state=game_state)
    return True


# --- OP05-010: Nico Robin ---
@register_effect("OP05-010", "on_play", "[On Play] K.O. Character with 1000 power or less")
def op05_010_robin(game_state, player, card):
    """On Play: K.O. Character with 1000 power or less."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if _is_character(c) and _effective_power(c) <= 1000]
    if targets:
        return create_ko_choice(
            game_state,
            player,
            targets,
            source_card=card,
            min_selections=0,
            max_selections=1,
            prompt="Choose up to 1 opponent Character with 1000 power or less to K.O.",
        )
    return True


# --- OP05-011: Bartholomew Kuma ---
@register_effect("OP05-011", "on_play", "[On Play] K.O. Character with 2000 power or less")
def op05_011_kuma_play(game_state, player, card):
    """On Play: K.O. Character with 2000 power or less."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if _is_character(c) and _effective_power(c) <= 2000]
    if targets:
        return create_ko_choice(
            game_state,
            player,
            targets,
            source_card=card,
            min_selections=0,
            max_selections=1,
            prompt="Choose up to 1 opponent Character with 2000 power or less to K.O.",
        )
    return True


@register_effect("OP05-011", "trigger", "[Trigger] If multicolored Leader, play this card")
def op05_011_kuma_trigger(game_state, player, card):
    """Trigger: Play this card if multicolored Leader."""
    if player.leader and len(getattr(player.leader, 'colors', [])) > 1:
        card.is_resting = False
        player.cards_in_play.append(card)
        setattr(card, 'played_turn', game_state.turn_count)
        game_state._apply_keywords(card)
        return True
    return False


# --- OP05-013: Bunny Joe ---
@register_effect("OP05-013", "blocker", "[Blocker]")
def op05_013_bunny_joe(game_state, player, card):
    """Blocker ability."""
    card.has_blocker = True
    return True


# --- OP05-014: Pell ---
@register_effect("OP05-014", "on_attack", "[DON!! x1] [When Attacking] -2000 power to Character")
def op05_014_pell(game_state, player, card):
    """When Attacking with 1 DON: Give Character -2000 power."""
    attached = getattr(card, 'attached_don', 0)
    if attached >= 1:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if _is_character(c)]
        if targets:
            return create_target_choice(
                game_state,
                player,
                targets,
                source_card=card,
                min_selections=0,
                max_selections=1,
                prompt="Choose up to 1 opponent Character to give -2000 power during this turn",
                callback=lambda chosen: _add_turn_power(game_state, targets[int(chosen[0])], -2000) if chosen else None,
            )
    return True


# --- OP05-015: Belo Betty ---
@register_effect("OP05-015", "on_play", "[On Play] Look at 5, add Revolutionary Army card")
def op05_015_betty(game_state, player, card):
    """On Play: Look at 5 and add Revolutionary Army card."""
    return search_top_cards(
        game_state,
        player,
        look_count=5,
        add_count=1,
        filter_fn=lambda c: _has_type(c, 'Revolutionary Army') and getattr(c, 'name', '') != 'Belo Betty',
        source_card=card,
        prompt="Look at the top 5 cards of your deck. Reveal up to 1 Revolutionary Army card other than Belo Betty and add it to your hand",
    )


# --- OP05-016: Morley ---
@register_effect("OP05-016", "on_attack", "[When Attacking] If 7000+ power, opponent cannot activate Blocker")
def op05_016_morley(game_state, player, card):
    """When Attacking: If 7000+ power, opponent cannot activate Blocker."""
    if _effective_power(card) >= 7000:
        opponent = get_opponent(game_state, player)
        for c in opponent.cards_in_play:
            c.blocker_disabled = True
    return True


@register_effect("OP05-016", "trigger", "[Trigger] Trash 1: If multicolored Leader, play this card")
def op05_016_morley_trigger(game_state, player, card):
    """Trigger: Trash 1 to play if multicolored Leader."""
    return _queue_multicolor_trigger_play(game_state, player, card)


# --- OP05-017: Lindbergh ---
@register_effect("OP05-017", "on_attack", "[When Attacking] If 7000+ power, K.O. 3000 power or less")
def op05_017_lindbergh(game_state, player, card):
    """When Attacking: If 7000+ power, K.O. 3000 power or less."""
    if _effective_power(card) >= 7000:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if _is_character(c) and _effective_power(c) <= 3000]
        if targets:
            snapshot = list(targets)

            def callback(selected):
                target_idx = int(selected[0]) if selected else -1
                if 0 <= target_idx < len(snapshot):
                    game_state._attempt_character_ko(snapshot[target_idx], by_effect=True, controller=player)

            return create_ko_choice(
                game_state,
                player,
                snapshot,
                source_card=card,
                min_selections=0,
                max_selections=1,
                prompt="Choose up to 1 opponent Character with 3000 power or less to K.O.",
                callback=callback,
            )
    return True


@register_effect("OP05-017", "trigger", "[Trigger] Trash 1: If multicolored Leader, play this card")
def op05_017_lindbergh_trigger(game_state, player, card):
    """Trigger: Trash 1 to play if multicolored Leader."""
    return _queue_multicolor_trigger_play(game_state, player, card)


# --- OP05-023: Vergo ---
@register_effect("OP05-023", "on_attack", "[DON!! x1] [When Attacking] K.O. rested cost 3 or less")
def op05_023_vergo(game_state, player, card):
    """When Attacking with 1 DON: K.O. rested cost 3 or less."""
    attached = getattr(card, 'attached_don', 0)
    if attached >= 1:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if getattr(c, 'is_resting', False) and (getattr(c, 'cost', 0) or 0) <= 3]
        if targets:
            snapshot = list(targets)

            def callback(selected):
                target_idx = int(selected[0]) if selected else -1
                if 0 <= target_idx < len(snapshot):
                    game_state._attempt_character_ko(snapshot[target_idx], by_effect=True, controller=player)

            return create_ko_choice(
                game_state,
                player,
                snapshot,
                source_card=card,
                min_selections=0,
                max_selections=1,
                prompt="Choose up to 1 opponent rested cost 3 or less Character to K.O.",
                callback=callback,
            )
    return True


# --- OP05-024: Kuween ---
@register_effect("OP05-024", "blocker", "[Blocker]")
def op05_024_kuween(game_state, player, card):
    """Blocker ability."""
    card.has_blocker = True
    return True


# --- OP05-025: Gladius ---
@register_effect("OP05-025", "activate", "[Activate: Main] Rest: Rest cost 3 or less")
def op05_025_gladius(game_state, player, card):
    """Activate: Rest to rest cost 3 or less."""
    if getattr(card, "is_resting", False):
        return False
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if _is_character(c) and _effective_cost(c) <= 3]

    def callback(selected):
        if not selected or selected[0] != "use":
            return
        card.is_resting = True
        game_state._log(f"{card.name} was rested")
        if targets:
            create_rest_choice(
                game_state,
                player,
                targets,
                source_card=card,
                prompt="Choose up to 1 of your opponent's cost 3 or less Characters to rest",
                min_selections=0,
                max_selections=1,
            )

    return create_mode_choice(
        game_state,
        player,
        modes=[
            {"id": "use", "label": "Use effect", "description": "Rest this Character and rest up to 1 of your opponent's cost 3 or less Characters"},
            {"id": "skip", "label": "Skip", "description": "Do not use Gladius's effect"},
        ],
        source_card=card,
        prompt="Rest this Character to rest up to 1 of your opponent's cost 3 or less Characters?",
        callback=callback,
    )


# --- OP05-026: Sarquiss ---
@register_effect("OP05-026", "on_attack", "[DON!! x1] [When Attacking] [Once Per Turn] Rest cost 3+ to set active")
def op05_026_sarquiss(game_state, player, card):
    """When Attacking with 1 DON: Rest cost 3+ to set this active."""
    attached = getattr(card, 'attached_don', 0)
    if attached >= 1 and not getattr(card, 'op05_026_used', False):
        chars_to_rest = [c for c in player.cards_in_play if (getattr(c, 'cost', 0) or 0) >= 3 and c != card and not getattr(c, 'is_resting', False)]
        if chars_to_rest:
            rest_snap = list(chars_to_rest)

            def yes_no_callback(selected):
                if not selected or selected[0] != "use":
                    return

                def sarquiss_cb(rest_selected: list) -> None:
                    target_idx = int(rest_selected[0]) if rest_selected else -1
                    if 0 <= target_idx < len(rest_snap):
                        target = rest_snap[target_idx]
                        target.is_resting = True
                        game_state._log(f"{target.name} was rested")
                        card._set_active_after_battle_resolution = True
                        card.op05_026_used = True
                        game_state._log(f"{card.name} will be set active after battle resolves")

                create_rest_choice(
                    game_state,
                    player,
                    rest_snap,
                    source_card=card,
                    prompt="Choose 1 of your cost 3 or more Characters to rest",
                    callback=sarquiss_cb,
                )

            return create_mode_choice(
                game_state,
                player,
                modes=[
                    {"id": "use", "label": "Use effect", "description": "Rest 1 of your cost 3 or more Characters to set this Character active"},
                    {"id": "skip", "label": "Skip", "description": "Do not use Sarquiss's effect"},
                ],
                source_card=card,
                prompt="Use Sarquiss's effect to rest one of your Characters and set Sarquiss active?",
                callback=yes_no_callback,
            )
    return False


# --- OP05-027: Trafalgar Law ---
@register_effect("OP05-027", "activate", "[Activate: Main] Trash this: Rest cost 3 or less")
def op05_027_law(game_state, player, card):
    """Activate: Trash this to rest cost 3 or less."""
    if card not in player.cards_in_play:
        return False
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if _is_character(c) and _effective_cost(c) <= 3]

    def callback(selected):
        if not selected or selected[0] != "use":
            return
        if card in player.cards_in_play:
            player.cards_in_play.remove(card)
            player.trash.append(card)
            game_state._log(f"{player.name} trashed {card.name}")
        if targets:
            create_rest_choice(
                game_state,
                player,
                targets,
                source_card=card,
                prompt="Choose up to 1 of your opponent's cost 3 or less Characters to rest",
                min_selections=0,
                max_selections=1,
            )

    return create_mode_choice(
        game_state,
        player,
        modes=[
            {"id": "use", "label": "Use effect", "description": "Trash this Character and rest up to 1 of your opponent's cost 3 or less Characters"},
            {"id": "skip", "label": "Skip", "description": "Do not use Trafalgar Law's effect"},
        ],
        source_card=card,
        prompt="Trash this Character to rest up to 1 of your opponent's cost 3 or less Characters?",
        callback=callback,
    )


# --- OP05-028: Donquixote Doflamingo ---
@register_effect("OP05-028", "activate", "[Activate: Main] Trash this: K.O. rested cost 2 or less")
def op05_028_doflamingo(game_state, player, card):
    """Activate: Trash this to K.O. rested cost 2 or less."""
    if card not in player.cards_in_play:
        return False
    opponent = get_opponent(game_state, player)
    targets = [
        c for c in opponent.cards_in_play
        if _is_character(c) and getattr(c, "is_resting", False) and _effective_cost(c) <= 2
    ]

    def callback(selected):
        if not selected or selected[0] != "use":
            return
        if card in player.cards_in_play:
            player.cards_in_play.remove(card)
            player.trash.append(card)
            game_state._log(f"{player.name} trashed {card.name}")
        if targets:
            create_ko_choice(
                game_state,
                player,
                targets,
                source_card=card,
                prompt="Choose up to 1 of your opponent's rested cost 2 or less Characters to K.O.",
                min_selections=0,
                max_selections=1,
            )

    return create_mode_choice(
        game_state,
        player,
        modes=[
            {"id": "use", "label": "Use effect", "description": "Trash this Character and K.O. up to 1 of your opponent's rested cost 2 or less Characters"},
            {"id": "skip", "label": "Skip", "description": "Do not use Donquixote Doflamingo's effect"},
        ],
        source_card=card,
        prompt="Trash this Character to K.O. up to 1 of your opponent's rested cost 2 or less Characters?",
        callback=callback,
    )


# --- OP05-029: Donquixote Doflamingo ---
@register_effect("OP05-029", "on_opponent_attack", "[On Opponent's Attack] [Once Per Turn] DON -1: Rest cost 6 or less")
def op05_029_doflamingo(game_state, player, card):
    """On Opponent's Attack: Rest 1 DON to rest cost 6 or less."""
    if getattr(card, 'op05_029_used', False):
        return False
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if _is_character(c) and _effective_cost(c) <= 6]
    if not any(state == "active" for state in player.don_pool[:_free_don_count(player)]):
        return False

    def mode_callback(selected):
        if not selected or selected[0] != "use":
            return
        if not _rest_active_don(player, 1):
            return
        card.op05_029_used = True
        if targets:
            create_rest_choice(
                game_state,
                player,
                list(targets),
                source_card=card,
                min_selections=0,
                max_selections=1,
                prompt="Choose up to 1 opponent Character with cost 6 or less to rest",
            )

    return create_mode_choice(
        game_state,
        player,
        modes=[
            {"id": "use", "label": "Use effect", "description": "Rest 1 DON!! to rest up to 1 opponent Character with cost 6 or less"},
            {"id": "skip", "label": "Skip", "description": "Do not use Donquixote Doflamingo's effect"},
        ],
        source_card=card,
        prompt="Rest 1 DON!! to rest up to 1 opponent Character with cost 6 or less?",
        callback=mode_callback,
    )


# --- OP05-030: Donquixote Rosinante ---
@register_effect("OP05-030", "blocker", "[Blocker]")
def op05_030_rosinante_blocker(game_state, player, card):
    """Blocker ability."""
    card.has_blocker = True
    return True


@register_effect("OP05-030", "on_ko_prevention", "[Opponent's Turn] If rested Character would be K.O.'d, trash this instead")
def op05_030_rosinante_protection(game_state, player, card):
    """Opponent's Turn: Trash this to save rested Character from K.O."""
    context = getattr(game_state, "_pending_ko_context", None)
    if not context or game_state.current_player is player or card not in player.cards_in_play:
        return False

    target = game_state._find_in_play_card_by_id(context.get("target_id"))
    if not target or target is card or target not in player.cards_in_play or not getattr(target, "is_resting", False):
        return False

    def callback(selected):
        if selected and selected[0] == "use":
            if card in player.cards_in_play:
                player.cards_in_play.remove(card)
                player.trash.append(card)
                game_state._log(f"{card.name} was trashed instead of {target.name}")
            game_state._resolve_ko_prevention_choice(True)
            return
        game_state._resolve_ko_prevention_choice(False)

    return create_mode_choice(
        game_state,
        player,
        modes=[
            {"id": "use", "label": "Trash Rosinante", "description": f"Trash {card.name} instead of {target.name} being K.O.'d"},
            {"id": "skip", "label": "Skip", "description": "Do not use Rosinante's replacement effect"},
        ],
        source_card=card,
        prompt=f"Trash {card.name} instead of {target.name} being K.O.'d?",
        callback=callback,
    )
    return False


# --- OP05-031: Buffalo ---
@register_effect("OP05-031", "on_attack", "[When Attacking] [Once Per Turn] If 2+ rested Characters, set cost 1 active")
def op05_031_buffalo(game_state, player, card):
    """When Attacking: If 2+ rested Characters, set cost 1 active."""
    if getattr(card, "op05_031_used", False):
        return True
    rested_chars = [c for c in player.cards_in_play if _is_character(c) and getattr(c, "is_resting", False)]
    if len(rested_chars) < 2:
        return True
    targets = [c for c in rested_chars if (getattr(c, "cost", 0) or 0) == 1]
    if not targets:
        return True

    def callback(selected):
        if not selected:
            return
        target_idx = int(selected[0]) if selected[0] is not None else -1
        if 0 <= target_idx < len(targets):
            target = targets[target_idx]
            target.is_resting = False
            target.has_attacked = False
            card.op05_031_used = True
            game_state._log(f"{target.name} was set active")

    return create_set_active_choice(
        game_state,
        player,
        targets,
        source_card=card,
        prompt="Choose up to 1 of your rested cost 1 Characters to set active",
        callback=callback,
        min_selections=0,
        max_selections=1,
    )


# --- OP05-032: Pica ---
@register_effect("OP05-032", "end_of_turn", "[End of Turn] DON -1: Set this active")
def op05_032_pica_eot(game_state, player, card):
    """End of Turn: Rest 1 DON to set this active."""
    if not getattr(card, 'is_resting', False):
        return False
    if not any(state == "active" for state in player.don_pool[:_free_don_count(player)]):
        return False

    def mode_callback(selected):
        if selected and selected[0] == "use" and _rest_active_don(player, 1):
            card.is_resting = False
            game_state._log(f"{card.name} was set active")

    return create_mode_choice(
        game_state,
        player,
        modes=[
            {"id": "use", "label": "Use effect", "description": "Rest 1 DON!! to set this Character active"},
            {"id": "skip", "label": "Skip", "description": "Leave this Character rested"},
        ],
        source_card=card,
        prompt="Rest 1 DON!! to set this Character active?",
        callback=mode_callback,
    )
    return False
    return False


@register_effect("OP05-032", "on_ko_prevention", "[Once Per Turn] Rest cost 3+ instead of being K.O.'d")
def op05_032_pica_protection(game_state, player, card):
    """Once Per Turn: Rest cost 3+ instead of being K.O.'d."""
    context = getattr(game_state, "_pending_ko_context", None)
    if not context or context.get("target_id") != card.id or getattr(card, "op05_032_ko_used", False):
        return False

    chars_to_rest = [
        c for c in player.cards_in_play
        if _is_character(c)
        and (getattr(c, 'cost', 0) or 0) >= 3
        and c != card
        and not getattr(c, 'is_resting', False)
    ]
    if chars_to_rest:
        snapshot = list(chars_to_rest)

        def rest_callback(selected):
            target_idx = int(selected[0]) if selected else -1
            if 0 <= target_idx < len(snapshot):
                target = snapshot[target_idx]
                target.is_resting = True
                card.op05_032_ko_used = True
                game_state._log(f"{target.name} was rested instead")
                game_state._resolve_ko_prevention_choice(True)

        def mode_callback(selected):
            if selected and selected[0] == "use":
                create_rest_choice(
                    game_state,
                    player,
                    snapshot,
                    source_card=card,
                    prompt="Choose 1 of your cost 3 or more Characters other than Pica to rest",
                    callback=rest_callback,
                )
                return
            game_state._resolve_ko_prevention_choice(False)

        return create_mode_choice(
            game_state,
            player,
            modes=[
                {"id": "use", "label": "Use effect", "description": "Rest 1 of your cost 3 or more Characters instead of Pica being K.O.'d"},
                {"id": "skip", "label": "Skip", "description": "Do not use Pica's replacement effect"},
            ],
            source_card=card,
            prompt="Rest 1 of your cost 3 or more Characters other than Pica instead of this Character being K.O.'d?",
            callback=mode_callback,
        )
    return False


# --- OP05-033: Baby 5 ---
@register_effect("OP05-033", "activate", "[Activate: Main] DON -1, rest: Play Donquixote Pirates cost 2 or less")
def op05_033_baby5(game_state, player, card):
    """Activate: Rest 1 DON and this to play Donquixote Pirates cost 2 or less."""
    if getattr(card, 'is_resting', False):
        return False
    targets = [c for c in player.hand if _is_character(c) and _has_type(c, 'Donquixote Pirates') and (getattr(c, 'cost', 0) or 0) <= 2]
    if not targets or not any(state == "active" for state in player.don_pool[:_free_don_count(player)]):
        return False

    def mode_callback(selected):
        if selected and selected[0] == "use" and _rest_active_don(player, 1):
            card.is_resting = True
            create_play_from_hand_choice(
                game_state,
                player,
                list(targets),
                source_card=card,
                prompt="Choose up to 1 Donquixote Pirates type Character with cost 2 or less to play from hand",
            )

    return create_mode_choice(
        game_state,
        player,
        modes=[
            {"id": "use", "label": "Use effect", "description": "Rest 1 DON!! and this Character to play up to 1 Donquixote Pirates Character with cost 2 or less"},
            {"id": "skip", "label": "Skip", "description": "Do not use Baby 5's effect"},
        ],
        source_card=card,
        prompt="Rest 1 DON!! and this Character to play up to 1 Donquixote Pirates Character with cost 2 or less?",
        callback=mode_callback,
    )
    return False


# --- OP05-034: Baby 5 ---
@register_effect("OP05-034", "activate", "[Activate: Main] DON -1, rest: Look at 5, add Donquixote Pirates card")
def op05_034_baby5(game_state, player, card):
    """Activate: Rest 1 DON and this to look at 5 and add Donquixote Pirates card."""
    if getattr(card, 'is_resting', False):
        return False
    if not any(state == "active" for state in player.don_pool[:_free_don_count(player)]):
        return False

    def mode_callback(selected):
        if selected and selected[0] == "use" and _rest_active_don(player, 1):
            card.is_resting = True
            search_top_cards(
                game_state,
                player,
                look_count=5,
                add_count=1,
                filter_fn=lambda c: _has_type(c, 'Donquixote Pirates'),
                source_card=card,
                prompt="Look at the top 5 cards of your deck and add up to 1 Donquixote Pirates card to your hand",
            )

    return create_mode_choice(
        game_state,
        player,
        modes=[
            {"id": "use", "label": "Use effect", "description": "Rest 1 DON!! and this Character to look at the top 5 cards of your deck"},
            {"id": "skip", "label": "Skip", "description": "Do not use Baby 5's effect"},
        ],
        source_card=card,
        prompt="Rest 1 DON!! and this Character to look at 5 cards from the top of your deck?",
        callback=mode_callback,
    )
    return False


# --- OP05-036: Monet ---
@register_effect("OP05-036", "blocker", "[Blocker]")
def op05_036_monet_blocker(game_state, player, card):
    """Blocker ability."""
    card.has_blocker = True
    return True


@register_effect("OP05-036", "on_block", "[On Block] Rest cost 4 or less")
def op05_036_monet_block(game_state, player, card):
    """On Block: Rest cost 4 or less."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if _is_character(c) and _effective_cost(c) <= 4]
    if targets:
        return create_rest_choice(
            game_state,
            player,
            targets,
            source_card=card,
            prompt="Choose up to 1 of your opponent's cost 4 or less Characters to rest",
            min_selections=0,
            max_selections=1,
        )
    return True


# --- OP05-042: Issho ---
@register_effect("OP05-042", "on_play", "[On Play] Cost 7 or less cannot attack until next turn")
def op05_042_issho(game_state, player, card):
    """On Play: Cost 7 or less cannot attack until next turn."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if _is_character(c) and _effective_cost(c) <= 7]
    if targets:
        snapshot = list(targets)

        def callback(selected):
            target_idx = int(selected[0]) if selected else -1
            if 0 <= target_idx < len(snapshot):
                target = snapshot[target_idx]
                target.cannot_attack = True
                target.cannot_attack_until_turn = game_state.turn_count + 1
                game_state._log(f"{target.name} cannot attack until the start of your next turn")

        return create_target_choice(
            game_state,
            player,
            snapshot,
            prompt="Choose up to 1 opponent Character with cost 7 or less that cannot attack until the start of your next turn",
            source_card=card,
            min_selections=0,
            max_selections=1,
            callback=callback,
        )
    return True


# --- OP05-043: Ulti ---
@register_effect("OP05-043", "on_play", "[On Play] If multicolored Leader, look at 3 and add 1")
def op05_043_ulti(game_state, player, card):
    """On Play: If multicolored Leader, look at 3 and add 1."""
    from ...game_engine import PendingChoice

    if player.leader and len(getattr(player.leader, 'colors', [])) > 1 and player.deck:
        looked_at = []
        for _ in range(min(3, len(player.deck))):
            looked_at.append(player.deck.pop(0))
        if not looked_at:
            return True

        options = []
        for i, looked_card in enumerate(looked_at):
            options.append({
                "id": str(i),
                "label": f"{looked_card.name} (Cost: {getattr(looked_card, 'cost', 0) or 0})",
                "card_id": looked_card.id,
                "card_name": looked_card.name,
            })

        def add_cb(selected):
            remaining = list(looked_at)
            chosen_idx = int(selected[0]) if selected else -1
            if 0 <= chosen_idx < len(looked_at):
                chosen = looked_at[chosen_idx]
                if chosen in remaining:
                    remaining.remove(chosen)
                player.hand.append(chosen)
                game_state._log(f"{card.name}: Added {chosen.name} to hand")
            _queue_top_or_bottom_any_order(game_state, player, remaining, source_card=card)

        game_state.pending_choice = PendingChoice(
            choice_id=f"op05_043_add_{uuid.uuid4().hex[:8]}",
            choice_type="select_target",
            prompt="Look at the top 3 cards of your deck and add up to 1 card to your hand",
            options=options,
            min_selections=0,
            max_selections=1,
            source_card_id=card.id,
            source_card_name=card.name,
            callback=add_cb,
        )
    return True


# --- OP05-045: Stainless ---
@register_effect("OP05-045", "activate", "[Activate: Main] Trash 1, rest: Bottom cost 2 or less")
def op05_045_stainless(game_state, player, card):
    """Activate: Trash 1 and rest to place cost 2 or less at deck bottom."""
    if getattr(card, 'is_resting', False) or not player.hand:
        return False

    hand_snapshot = list(player.hand)
    opponent = get_opponent(game_state, player)

    def discard_cb(selected):
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(hand_snapshot):
            trashed = hand_snapshot[idx]
            if trashed in player.hand:
                player.hand.remove(trashed)
                player.trash.append(trashed)
                game_state._log(f"{player.name} trashed {trashed.name}")
        card.is_resting = True
        targets = [
            c for c in player.cards_in_play + opponent.cards_in_play
            if _is_character(c) and _effective_cost(c) <= 2
        ]
        if targets:
            create_bottom_deck_choice(
                game_state,
                player,
                targets,
                source_card=card,
                prompt="Choose up to 1 Character with cost 2 or less to place at the bottom of the owner's deck",
                min_selections=0,
            )

    return create_mode_choice(
        game_state,
        player,
        modes=[
            {"id": "use", "label": "Use effect", "description": "Trash 1 card from your hand and rest this Character"},
            {"id": "skip", "label": "Skip", "description": "Do not use Stainless's effect"},
        ],
        source_card=card,
        prompt="Trash 1 card from your hand and rest this Character to place up to 1 cost 2 or less Character at the bottom of the owner's deck?",
        callback=lambda selected: create_hand_discard_choice(
            game_state,
            player,
            hand_snapshot,
            source_card=card,
            prompt="Choose 1 card from your hand to trash",
            callback=discard_cb,
        ) if selected and selected[0] == "use" else None,
    )


# --- OP05-046: Dalmatian ---
@register_effect("OP05-046", "on_ko", "[On K.O.] Draw 1, bottom 1")
def op05_046_dalmatian(game_state, player, card):
    """On K.O.: Draw 1 and place 1 at deck bottom."""
    draw_cards(player, 1, game_state=game_state)
    if player.hand:
        hand_snapshot = list(player.hand)

        def bottom_cb(selected):
            idx = int(selected[0]) if selected else -1
            if 0 <= idx < len(hand_snapshot):
                chosen = hand_snapshot[idx]
                if chosen in player.hand:
                    player.hand.remove(chosen)
                    player.deck.append(chosen)
                    game_state._log(f"{chosen.name} was placed at the bottom of your deck")

        return create_hand_discard_choice(
            game_state,
            player,
            hand_snapshot,
            source_card=card,
            prompt="Choose 1 card from your hand to place at the bottom of your deck",
            callback=bottom_cb,
        )
    return True


# --- OP05-047: Basil Hawkins ---
@register_effect("OP05-047", "blocker", "[Blocker]")
def op05_047_hawkins_blocker(game_state, player, card):
    """Blocker ability."""
    card.has_blocker = True
    return True


@register_effect("OP05-047", "on_block", "[On Block] Draw 1 if 3 or less hand, +1000 power")
def op05_047_hawkins_block(game_state, player, card):
    """On Block: Draw 1 if 3 or less hand, +1000 power."""
    if len(player.hand) <= 3:
        draw_cards(player, 1, game_state=game_state)
    _add_battle_power(game_state, card, 1000)
    return True


# --- OP05-048: Bastille ---
@register_effect("OP05-048", "on_attack", "[DON!! x1] [When Attacking] Bottom cost 2 or less")
def op05_048_bastille(game_state, player, card):
    """When Attacking with 1 DON: Place cost 2 or less at deck bottom."""
    attached = getattr(card, 'attached_don', 0)
    if attached >= 1:
        targets = [
            c for c in player.cards_in_play + get_opponent(game_state, player).cards_in_play
            if _is_character(c) and _effective_cost(c) <= 2
        ]
        if targets:
            return create_bottom_deck_choice(
                game_state,
                player,
                targets,
                source_card=card,
                prompt="Choose up to 1 Character with cost 2 or less to place at the bottom of the owner's deck",
                min_selections=0,
            )
    return True


# --- OP05-049: Haccha ---
@register_effect("OP05-049", "on_attack", "[DON!! x1] [When Attacking] Return cost 3 or less to hand")
def op05_049_haccha(game_state, player, card):
    """When Attacking with 1 DON: Return cost 3 or less to hand."""
    attached = getattr(card, 'attached_don', 0)
    if attached >= 1:
        targets = [
            c for c in player.cards_in_play + get_opponent(game_state, player).cards_in_play
            if _is_character(c) and _effective_cost(c) <= 3
        ]
        if targets:
            return create_return_to_hand_choice(
                game_state,
                player,
                targets,
                source_card=card,
                optional=True,
                prompt="Choose up to 1 Character with cost 3 or less to return to the owner's hand",
            )
    return True


# --- OP05-050: Hina ---
@register_effect("OP05-050", "on_play", "[On Play] Draw 1 if 5 or less hand")
def op05_050_hina(game_state, player, card):
    """On Play: Draw 1 if 5 or less hand."""
    if len(player.hand) <= 5:
        draw_cards(player, 1, game_state=game_state)
    return True


# --- OP05-051: Borsalino ---
@register_effect("OP05-051", "on_play", "[On Play] Bottom cost 4 or less")
def op05_051_borsalino(game_state, player, card):
    """On Play: Place cost 4 or less at deck bottom."""
    targets = [
        c for c in player.cards_in_play + get_opponent(game_state, player).cards_in_play
        if _is_character(c) and _effective_cost(c) <= 4
    ]
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


# --- OP05-052: Maynard ---
@register_effect("OP05-052", "blocker", "[Blocker]")
def op05_052_maynard(game_state, player, card):
    """Blocker ability."""
    card.has_blocker = True
    return True


# --- OP05-053: Mozambia ---
@register_effect("OP05-053", "on_draw", "[Your Turn] [Once Per Turn] When you draw outside Draw Phase, +2000")
def op05_053_mozambia(game_state, player, card):
    """Your Turn: When drawing outside Draw Phase, +2000 power."""
    from ...game_engine import GamePhase

    if game_state.current_player is not player or getattr(game_state, "phase", None) == GamePhase.DRAW:
        return False
    if not getattr(card, 'op05_053_used', False):
        add_power_modifier(card, 2000)
        card.power_modifier_expires_on_turn = game_state.turn_count
        card._sticky_power_modifier_expires_on_turn = game_state.turn_count
        card.op05_053_used = True
        game_state._log(f"{card.name} gets +2000 power during this turn")
        return True
    return True


# --- OP05-054: Monkey.D.Garp ---
@register_effect("OP05-054", "on_play", "[On Play] Draw 2, bottom 2")
def op05_054_garp(game_state, player, card):
    """On Play: Draw 2 and place 2 at deck bottom."""
    draw_cards(player, 2, game_state=game_state)
    if player.hand:
        return _queue_bottom_from_hand_any_order(game_state, player, list(player.hand), 2, source_card=card)
    return True


# --- OP05-055: X.Drake ---
@register_effect("OP05-055", "blocker", "[Blocker]")
def op05_055_drake_blocker(game_state, player, card):
    """Blocker ability."""
    card.has_blocker = True
    return True


@register_effect("OP05-055", "on_play", "[On Play] Look at 5 and reorder top/bottom")
def op05_055_drake_play(game_state, player, card):
    """On Play: Look at 5 and reorder at top/bottom."""
    return reorder_top_cards(game_state, player, 5, source_card=card, allow_top=True)


# --- OP05-056: X.Barrels ---
@register_effect("OP05-056", "on_play", "[On Play] Bottom own Character: Draw 1")
def op05_056_barrels(game_state, player, card):
    """On Play: Place own Character at deck bottom to draw 1."""
    other_chars = [c for c in player.cards_in_play if c != card and _is_character(c)]
    if not other_chars:
        return True

    def callback(selected):
        if not selected:
            return
        target = other_chars[int(selected[0])]
        if target in player.cards_in_play:
            player.cards_in_play.remove(target)
            player.deck.append(target)
            game_state._log(f"{target.name} was placed at the bottom of the deck")
            draw_cards(player, 1, game_state=game_state)

    return create_target_choice(
        game_state, player, other_chars,
        prompt="You may choose 1 of your Characters other than this Character to place at the bottom of your deck",
        source_card=card,
        min_selections=0,
        max_selections=1,
        callback=callback,
    )


# --- OP05-061: Uso-Hachi ---
@register_effect("OP05-061", "on_attack", "[DON!! x1] [When Attacking] If 8+ DON, rest cost 4 or less")
def op05_061_usohachi(game_state, player, card):
    """When Attacking with 1 DON: If 8+ DON, rest cost 4 or less."""
    attached = getattr(card, 'attached_don', 0)
    if attached >= 1 and len(player.don_pool) >= 8:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if _is_character(c) and _effective_cost(c) <= 4]
        if targets:
            return create_rest_choice(
                game_state,
                player,
                targets,
                source_card=card,
                min_selections=0,
                max_selections=1,
                prompt="Choose up to 1 opponent Character with cost 4 or less to rest",
            )
    return True


# --- OP05-062: O-Nami ---
@register_effect("OP05-062", "continuous", "If 10 DON, gains Blocker")
def op05_062_onami(game_state, player, card):
    """Continuous: Gains Blocker if 10 DON."""
    has_blocker = len(player.don_pool) >= 10
    card._continuous_blocker = has_blocker
    card.has_blocker = has_blocker or getattr(card, "_innate_blocker", False)
    return True


# --- OP05-063: O-Robi ---
@register_effect("OP05-063", "on_play", "[On Play] If 8+ DON, K.O. cost 3 or less")
def op05_063_orobi(game_state, player, card):
    """On Play: If 8+ DON, K.O. cost 3 or less."""
    if len(player.don_pool) >= 8:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if _is_character(c) and _effective_cost(c) <= 3]
        if targets:
            return create_ko_choice(
                game_state,
                player,
                targets,
                source_card=card,
                min_selections=0,
                max_selections=1,
                prompt="Choose up to 1 opponent Character with cost 3 or less to K.O.",
            )
    return True


# --- OP05-064: Killer ---
@register_effect("OP05-064", "on_play", "[On Play] Look at 5, add Kid Pirates card")
def op05_064_killer(game_state, player, card):
    """On Play: Look at 5, reveal up to 1 Kid Pirates card other than Killer, then bottom the rest in any order."""
    return search_top_cards(
        game_state,
        player,
        5,
        add_count=1,
        filter_fn=lambda c: _has_type(c, "Kid Pirates") and getattr(c, "name", "") != "Killer",
        source_card=card,
        prompt="Look at the top 5 cards of your deck and reveal up to 1 {Kid Pirates} card other than [Killer] to add to your hand",
    )


# --- OP05-066: Jinbe ---
@register_effect("OP05-066", "blocker", "[Blocker]")
def op05_066_jinbe_blocker(game_state, player, card):
    """Blocker ability."""
    card.has_blocker = True
    return True


@register_effect("OP05-066", "continuous", "[Opponent's Turn] If 10 DON, +1000")
def op05_066_jinbe_continuous(game_state, player, card):
    """Opponent's Turn: If 10 DON, +1000 power."""
    sticky = getattr(card, "_sticky_power_modifier", 0)
    if game_state.current_player is not player and len(player.don_pool) >= 10:
        card.power_modifier = sticky + 1000
    else:
        card.power_modifier = sticky
    return True


# --- OP05-067: Zoro-Juurou ---
@register_effect("OP05-067", "on_attack", "[When Attacking] If 3 or less Life, add active DON")
def op05_067_zorojuurou(game_state, player, card):
    """When Attacking: If 3 or less Life, add active DON."""
    if len(player.life_cards) <= 3:
        add_don_from_deck(player, 1, set_active=True)
    return True


# --- OP05-068: Chopa-Emon ---
@register_effect("OP05-068", "on_play", "[On Play] If 8+ DON, set purple Straw Hat 6000 or less active")
def op05_068_chopaemon(game_state, player, card):
    """On Play: If 8+ DON, set purple Straw Hat 6000 or less active."""
    if len(player.don_pool) >= 8:
        targets = [
            c for c in player.cards_in_play
            if _is_character(c)
            and 'Purple' in getattr(c, 'colors', [])
            and _has_type(c, 'Straw Hat Crew')
            and (getattr(c, 'power', 0) or 0) <= 6000
            and getattr(c, 'is_resting', False)
        ]
        if targets:
            return create_set_active_choice(
                game_state,
                player,
                targets,
                source_card=card,
                min_selections=0,
                max_selections=1,
                prompt="Choose up to 1 of your rested purple {Straw Hat Crew} Characters with 6000 power or less to set active",
            )
    return True


# --- OP05-069: Trafalgar Law ---
@register_effect("OP05-069", "on_attack", "[When Attacking] If opponent has more DON, look at 5 and add Heart Pirates")
def op05_069_law(game_state, player, card):
    """When Attacking: If opponent has more DON, look at 5 and add Heart Pirates."""
    opponent = get_opponent(game_state, player)
    if len(opponent.don_pool) > len(player.don_pool):
        return search_top_cards(
            game_state,
            player,
            5,
            add_count=1,
            filter_fn=lambda c: _has_type(c, "Heart Pirates"),
            source_card=card,
            prompt="Look at the top 5 cards of your deck and reveal up to 1 {Heart Pirates} card to add to your hand",
        )
    return True


# --- OP05-070: Fra-Nosuke ---
@register_effect("OP05-070", "continuous", "[DON!! x1] If 8+ DON, gains Rush")
def op05_070_franosuke(game_state, player, card):
    """With 1 DON: If 8+ DON, gains Rush."""
    attached = getattr(card, 'attached_don', 0)
    card.has_rush = (attached >= 1 and len(player.don_pool) >= 8) or getattr(card, "_innate_rush", False)
    return True


# --- OP05-071: Bepo ---
@register_effect("OP05-071", "on_attack", "[When Attacking] If opponent has more DON, -2000 power")
def op05_071_bepo(game_state, player, card):
    """When Attacking: If opponent has more DON, give -2000 power."""
    opponent = get_opponent(game_state, player)
    if len(opponent.don_pool) > len(player.don_pool):
        targets = [c for c in opponent.cards_in_play if _is_character(c)]
        if targets:
            def callback(selected):
                if selected:
                    _add_turn_power(game_state, targets[int(selected[0])], -2000)

            return create_target_choice(
                game_state,
                player,
                targets,
                prompt="Choose up to 1 opponent Character to give -2000 power during this turn",
                source_card=card,
                min_selections=0,
                max_selections=1,
                callback=callback,
            )
    return True


# --- OP05-072: Hone-Kichi ---
@register_effect("OP05-072", "on_play", "[On Play] If 8+ DON, -2000 to 2 Characters")
def op05_072_honekichi(game_state, player, card):
    """On Play: If 8+ DON, give -2000 to 2 Characters."""
    if len(player.don_pool) >= 8:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if _is_character(c)]
        if targets:
            def callback(selected):
                for sel in selected:
                    idx = int(sel) if sel is not None else -1
                    if 0 <= idx < len(targets):
                        _add_turn_power(game_state, targets[idx], -2000)

            return create_target_choice(
                game_state,
                player,
                targets,
                prompt="Choose up to 2 opponent Characters to give -2000 power during this turn",
                source_card=card,
                min_selections=0,
                max_selections=2,
                callback=callback,
            )
    return True


# --- OP05-073: Miss Doublefinger ---
@register_effect("OP05-073", "on_play", "[On Play] Trash 1: Add rested DON")
def op05_073_doublefinger_play(game_state, player, card):
    """On Play: Trash 1 to add rested DON."""
    if not player.hand:
        return True

    hand_snapshot = list(player.hand)

    def discard_cb(selected):
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(hand_snapshot):
            trashed = hand_snapshot[idx]
            if trashed in player.hand:
                player.hand.remove(trashed)
                player.trash.append(trashed)
                game_state._log(f"{player.name} trashed {trashed.name}")
                add_don_from_deck(player, 1, set_active=False)

    return create_mode_choice(
        game_state,
        player,
        modes=[
            {"id": "use", "label": "Trash 1", "description": "Trash 1 card from your hand to add up to 1 rested DON!!"},
            {"id": "skip", "label": "Skip", "description": "Do not use Miss Doublefinger's effect"},
        ],
        source_card=card,
        prompt="Trash 1 card from your hand to add up to 1 DON!! card from your DON!! deck rested?",
        callback=lambda selected: create_hand_discard_choice(
            game_state,
            player,
            hand_snapshot,
            source_card=card,
            prompt="Choose 1 card from your hand to trash",
            callback=discard_cb,
        ) if selected and selected[0] == "use" else None,
    )


@register_effect("OP05-073", "trigger", "[Trigger] DON -1: Play this card")
def op05_073_doublefinger_trigger(game_state, player, card):
    """Trigger: Return 1 DON to play this card."""
    if len(player.don_pool) < 1:
        return False

    def resolve_effect():
        card.is_resting = False
        player.cards_in_play.append(card)
        setattr(card, "played_turn", game_state.turn_count)
        game_state._apply_keywords(card)
        game_state._log(f"{player.name} played {card.name} from trigger")

    returned = return_don_to_deck(game_state, player, 1, source_card=card, post_callback=resolve_effect)
    if game_state.pending_choice is not None:
        return True
    if returned:
        resolve_effect()
    return True


# --- OP05-074: Eustass"Captain"Kid ---
@register_effect("OP05-074", "blocker", "[Blocker]")
def op05_074_kid_blocker(game_state, player, card):
    """Blocker ability."""
    card.has_blocker = True
    return True


@register_effect("OP05-074", "on_don_return", "[Your Turn] [Once Per Turn] When DON returns to deck, add active DON")
def op05_074_kid_don_return(game_state, player, card):
    """Your Turn: When DON returns to deck, add active DON."""
    if game_state.current_player is player and not getattr(card, 'op05_074_used', False):
        add_don_from_deck(player, 1, set_active=True)
        card.op05_074_used = True
    return True


# --- OP05-075: Mr.1 ---
@register_effect("OP05-075", "on_opponent_attack", "[On Opponent's Attack] [Once Per Turn] DON -1: Play Baroque Works cost 3 or less")
def op05_075_mr1(game_state, player, card):
    """On Opponent's Attack: Return 1 DON to play Baroque Works cost 3 or less."""
    if getattr(card, 'op05_075_used', False):
        return False
    targets = [c for c in player.hand if _is_character(c) and _has_type(c, 'Baroque Works') and (getattr(c, 'cost', 0) or 0) <= 3]
    if len(player.don_pool) < 1:
        return False

    def resolve_effect():
        card.op05_075_used = True
        current_targets = [c for c in player.hand if _is_character(c) and _has_type(c, 'Baroque Works') and (getattr(c, 'cost', 0) or 0) <= 3]
        if current_targets:
            create_play_from_hand_choice(
                game_state, player, current_targets, source_card=card,
                prompt="Choose up to 1 {Baroque Works} Character with cost 3 or less to play from your hand"
            )

    def mode_cb(selected):
        if not selected or selected[0] != "use":
            return
        returned = return_don_to_deck(game_state, player, 1, source_card=card, post_callback=resolve_effect)
        if game_state.pending_choice is not None:
            return
        if returned:
            resolve_effect()

    return create_mode_choice(
        game_state, player,
        modes=[
            {"id": "use", "label": "DON -1", "description": "Return 1 DON!! to your DON!! deck to play up to 1 card"},
            {"id": "skip", "label": "Skip", "description": "Do not use Mr.1's effect"},
        ],
        source_card=card,
        prompt="Return 1 DON!! card from your field to your DON!! deck to play up to 1 {Baroque Works} Character with cost 3 or less?",
        callback=mode_cb,
    )


# --- OP05-079: Viola ---
@register_effect("OP05-079", "on_play", "[On Play] Opponent bottoms 3 cards from trash")
def op05_079_viola(game_state, player, card):
    """On Play: Opponent places 3 cards from trash at deck bottom."""
    opponent = get_opponent(game_state, player)
    if opponent.trash:
        return _queue_bottom_from_trash_any_order(game_state, opponent, 3, source_card=card)
    return True


# --- OP05-080: Elizabello II ---
@register_effect("OP05-080", "on_attack", "[When Attacking] [Once Per Turn] Return 20 trash to deck: Double Attack +10000")
def op05_080_elizabello(game_state, player, card):
    """When Attacking: Return 20 trash to deck for Double Attack +10000."""
    if getattr(card, 'op05_080_used', False) or len(player.trash) < 20:
        return False

    def callback(selected):
        if not selected or selected[0] != "use":
            return
        for _ in range(20):
            player.deck.append(player.trash.pop())
        random.shuffle(player.deck)
        card.has_doubleattack = True
        card.has_double_attack = True
        card._temp_doubleattack = True
        _add_battle_power(game_state, card, 10000)
        card.op05_080_used = True

    return create_mode_choice(
        game_state, player,
        modes=[
            {"id": "use", "label": "Return 20", "description": "Return 20 cards from your trash to your deck and shuffle it"},
            {"id": "skip", "label": "Skip", "description": "Do not use Elizabello II's effect"},
        ],
        source_card=card,
        prompt="Return 20 cards from your trash to your deck and shuffle it to give this Character [Double Attack] and +10000 power during this battle?",
        callback=callback,
    )


# --- OP05-081: One-Legged Toy Soldier ---
@register_effect("OP05-081", "activate", "[Activate: Main] Trash this: -3 cost")
def op05_081_toy_soldier(game_state, player, card):
    """Activate: Trash this to give -3 cost."""
    if card not in player.cards_in_play:
        return False

    def use_effect(selected):
        if not selected or selected[0] != "trash":
            return
        if card in player.cards_in_play:
            player.cards_in_play.remove(card)
            player.trash.append(card)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if _is_character(c)]
        if targets:
            create_cost_reduction_choice(
                game_state, player, targets, -3,
                source_card=card,
                min_selections=0,
                max_selections=1,
                prompt="Choose up to 1 opponent Character to give -3 cost"
            )

    return create_mode_choice(
        game_state, player,
        modes=[
            {"id": "trash", "label": "Trash This", "description": "Trash this Character to use the effect"},
            {"id": "skip", "label": "Skip", "description": "Do not use this effect"},
        ],
        source_card=card,
        prompt="Choose whether to trash this Character",
        callback=use_effect,
    )


# --- OP05-082: Shirahoshi ---
@register_effect("OP05-082", "activate", "[Activate: Main] Rest, bottom 2 trash: If opponent has 6+ hand, they trash 1")
def op05_082_shirahoshi(game_state, player, card):
    """Activate: Rest and bottom 2 trash to make opponent trash 1 if 6+ hand."""
    if not getattr(card, 'is_resting', False) and len(player.trash) >= 2:
        def finish_effect():
            opponent = get_opponent(game_state, player)
            if len(opponent.hand) >= 6 and opponent.hand:
                trash_from_hand(opponent, 1, game_state, card)

        def callback(selected):
            if not selected or selected[0] != "use":
                return
            card.is_resting = True
            _queue_bottom_from_trash_any_order(game_state, player, 2, source_card=card, on_complete=finish_effect)

        return create_mode_choice(
            game_state, player,
            modes=[
                {"id": "use", "label": "Use Effect", "description": "Rest this Character and place 2 cards from your trash at the bottom of your deck"},
                {"id": "skip", "label": "Skip", "description": "Do not use this effect"},
            ],
            source_card=card,
            prompt="Choose whether to use Shirahoshi's effect",
            callback=callback,
        )
    return False


# --- OP05-085: Nefeltari Cobra ---
@register_effect("OP05-085", "blocker", "[Blocker]")
def op05_085_cobra_blocker(game_state, player, card):
    """Blocker ability."""
    card.has_blocker = True
    return True


@register_effect("OP05-085", "on_play", "[On Play] Trash 1 from deck")
def op05_085_cobra_play(game_state, player, card):
    """On Play: Trash 1 from deck."""
    if player.deck:
        player.trash.append(player.deck.pop(0))
    return True


# --- OP05-086: Nefeltari Vivi ---
@register_effect("OP05-086", "continuous", "If 10+ trash, gains Blocker")
def op05_086_vivi(game_state, player, card):
    """Continuous: Gains Blocker if 10+ trash."""
    has_blocker = len(player.trash) >= 10
    card._continuous_blocker = has_blocker
    card.has_blocker = has_blocker or getattr(card, "_innate_blocker", False)
    return True


# --- OP05-087: Hakuba ---
@register_effect("OP05-087", "on_attack", "[DON!! x1] [When Attacking] K.O. own Character: -5 cost")
def op05_087_hakuba(game_state, player, card):
    """When Attacking with 1 DON: K.O. own Character to give -5 cost."""
    attached = getattr(card, 'attached_don', 0)
    if attached >= 1:
        other_chars = [c for c in player.cards_in_play if c != card and _is_character(c)]
        if not other_chars:
            return True

        def callback(selected):
            if not selected:
                return
            target = other_chars[int(selected[0])]
            if target in player.cards_in_play:
                player.cards_in_play.remove(target)
                player.trash.append(target)
                game_state._log(f"{target.name} was K.O.'d")
            opponent = get_opponent(game_state, player)
            reduce_targets = [c for c in opponent.cards_in_play if _is_character(c)]
            if reduce_targets:
                create_cost_reduction_choice(
                    game_state, player, reduce_targets, -5,
                    source_card=card,
                    min_selections=0,
                    max_selections=1,
                    prompt="Choose up to 1 opponent Character to give -5 cost"
                )

        return create_target_choice(
            game_state, player, other_chars,
            prompt="You may choose 1 of your Characters other than this Character to K.O.",
            source_card=card,
            min_selections=0,
            max_selections=1,
            callback=callback,
        )
    return True


# --- OP05-088: Mansherry ---
@register_effect("OP05-088", "activate", "[Activate: Main] DON -1, rest, bottom 2 trash: Add black cost 3-5 from trash")
def op05_088_mansherry(game_state, player, card):
    """Activate: Rest, DON -1, bottom 2 trash to add black cost 3-5 from trash."""
    if not getattr(card, 'is_resting', False) and len(player.trash) >= 2 and any(state == "active" for state in player.don_pool[:_free_don_count(player)]):
        valid_targets = [c for c in player.trash if _is_character(c) and 'Black' in getattr(c, 'colors', []) and 3 <= (getattr(c, 'cost', 0) or 0) <= 5]
        if not valid_targets:
            return False

        def choose_mode(selected):
            if not selected or selected[0] != "use" or not _rest_active_don(player, 1):
                return
            card.is_resting = True

            def retrieve_from_trash():
                create_add_from_trash_choice(
                    game_state, player,
                    [c for c in player.trash if _is_character(c) and 'Black' in getattr(c, 'colors', []) and 3 <= (getattr(c, 'cost', 0) or 0) <= 5],
                    source_card=card,
                    prompt="Choose up to 1 black Character card with cost 3 to 5 from your trash to add to your hand"
                )

            _queue_bottom_from_trash_any_order(game_state, player, 2, source_card=card, on_complete=retrieve_from_trash)

        return create_mode_choice(
            game_state, player,
            modes=[
                {"id": "use", "label": "Use Effect", "description": "Rest 1 DON!!, rest this Character, and place 2 cards from your trash at the bottom of your deck"},
                {"id": "skip", "label": "Skip", "description": "Do not continue the effect"},
            ],
            source_card=card,
            prompt="Use Mansherry's effect?",
            callback=choose_mode,
        )
    return False


# --- OP05-089: Saint Mjosgard ---
@register_effect("OP05-089", "activate", "[Activate: Main] DON -1, rest this and Character: Add black cost 1 from trash")
def op05_089_mjosgard(game_state, player, card):
    """Activate: Rest DON, this and Character to add black cost 1 from trash."""
    if not getattr(card, 'is_resting', False) and any(state == "active" for state in player.don_pool[:_free_don_count(player)]):
        other_chars = [c for c in player.cards_in_play if c != card and _is_character(c) and not getattr(c, 'is_resting', False)]
        valid_targets = [c for c in player.trash if _is_character(c) and 'Black' in getattr(c, 'colors', []) and (getattr(c, 'cost', 0) or 0) == 1]
        if other_chars and valid_targets:
            def callback(selected):
                if not selected:
                    return
                if not _rest_active_don(player, 1):
                    return
                target = other_chars[int(selected[0])]
                card.is_resting = True
                target.is_resting = True
                create_add_from_trash_choice(
                    game_state, player, valid_targets, source_card=card,
                    prompt="Choose up to 1 black Character card with cost 1 from your trash to add to your hand"
                )

            return create_target_choice(
                game_state, player, other_chars,
                prompt="Choose 1 of your Characters to rest with Saint Mjosgard",
                source_card=card,
                callback=callback,
            )
    return False


# --- OP05-090: Riku Doldo III ---
@register_effect("OP05-090", "blocker", "[Blocker]")
def op05_090_riku_blocker(game_state, player, card):
    """Blocker ability."""
    card.has_blocker = True
    return True


@register_effect("OP05-090", "on_play", "[On Play]/[On K.O.] Dressrosa +2000")
def op05_090_riku_play(game_state, player, card):
    """On Play: Dressrosa gains +2000."""
    dressrosa = [c for c in player.cards_in_play if _is_character(c) and _has_type(c, 'Dressrosa')]
    if dressrosa:
        return create_target_choice(
            game_state, player, dressrosa,
            source_card=card,
            min_selections=0,
            max_selections=1,
            prompt="Choose up to 1 of your {Dressrosa} Characters to gain +2000 power during this turn",
            callback=lambda selected: _add_turn_power(game_state, dressrosa[int(selected[0])], 2000) if selected else None,
        )
    return True


@register_effect("OP05-090", "on_ko", "[On K.O.] Dressrosa +2000")
def op05_090_riku_ko(game_state, player, card):
    """On K.O.: Dressrosa gains +2000."""
    dressrosa = [c for c in player.cards_in_play if _is_character(c) and _has_type(c, 'Dressrosa')]
    if dressrosa:
        return create_target_choice(
            game_state, player, dressrosa,
            source_card=card,
            min_selections=0,
            max_selections=1,
            prompt="Choose up to 1 of your {Dressrosa} Characters to gain +2000 power during this turn",
            callback=lambda selected: _add_turn_power(game_state, dressrosa[int(selected[0])], 2000) if selected else None,
        )
    return True


# --- OP05-091: Rebecca ---
@register_effect("OP05-091", "blocker", "[Blocker]")
def op05_091_rebecca_blocker(game_state, player, card):
    """Blocker ability."""
    card.has_blocker = True
    return True


@register_effect("OP05-091", "on_play", "[On Play] Add black cost 3-7 from trash, play black cost 3 or less rested")
def op05_091_rebecca_play(game_state, player, card):
    """On Play: Add black cost 3-7 from trash, play black cost 3 or less rested."""
    add_targets = [
        c for c in player.trash
        if _is_character(c) and 'Black' in getattr(c, 'colors', []) and 3 <= (getattr(c, 'cost', 0) or 0) <= 7 and getattr(c, 'name', '') != 'Rebecca'
    ]

    def queue_play():
        play_targets = [
            c for c in player.hand
            if _is_character(c) and 'Black' in getattr(c, 'colors', []) and (getattr(c, 'cost', 0) or 0) <= 3
        ]
        if play_targets:
            create_play_from_hand_choice(
                game_state, player, play_targets, source_card=card,
                rest_on_play=True,
                prompt="Choose up to 1 black Character card with cost 3 or less to play rested from your hand"
            )

    if add_targets:
        def add_callback(selected):
            if selected:
                idx = int(selected[0])
                if 0 <= idx < len(add_targets):
                    target = add_targets[idx]
                    if target in player.trash:
                        player.trash.remove(target)
                        player.hand.append(target)
                        game_state._log(f"{target.name} was added to hand from trash")
            queue_play()

        return create_add_from_trash_choice(
            game_state, player, add_targets, source_card=card,
            prompt="Choose up to 1 black Character card with cost 3 to 7 other than [Rebecca] from your trash to add to your hand",
            callback=add_callback,
        )
    queue_play()
    return True


# --- OP05-092: Saint Rosward ---
@register_effect("OP05-092", "continuous", "[Your Turn] If only Celestial Dragons, opponent Characters -6 cost")
def op05_092_rosward(game_state, player, card):
    """Your Turn: If only Celestial Dragons, opponent Characters -6 cost."""
    all_celestial = all('Celestial Dragons' in (c.card_origin or '') for c in player.cards_in_play)
    if game_state.current_player is player and all_celestial:
        opponent = get_opponent(game_state, player)
        for c in opponent.cards_in_play:
            c.cost_modifier = getattr(c, 'cost_modifier', 0) - 6
    return True


# --- OP05-093: Rob Lucci ---
@register_effect("OP05-093", "on_play", "[On Play] Bottom 3 trash: K.O. cost 2 or less and cost 1 or less")
def op05_093_lucci(game_state, player, card):
    """On Play: Bottom 3 trash to K.O. cost 2 or less and cost 1 or less."""
    if len(player.trash) < 3:
        return True

    def resolve_effect():
        opponent = get_opponent(game_state, player)
        targets2 = [c for c in opponent.cards_in_play if _is_character(c) and _effective_cost(c) <= 2]

        def second_ko():
            targets1 = [c for c in opponent.cards_in_play if _is_character(c) and _effective_cost(c) <= 1]
            if targets1:
                create_ko_choice(
                    game_state, player, targets1, source_card=card,
                    min_selections=0,
                    max_selections=1,
                    prompt="Choose up to 1 opponent Character with cost 1 or less to K.O."
                )

        if not targets2:
            second_ko()
            return

        def first_callback(selected):
            if selected:
                target = targets2[int(selected[0])]
                game_state._attempt_character_ko(target, by_effect=True)
            second_ko()

        create_ko_choice(
            game_state, player, targets2, source_card=card,
            min_selections=0,
            max_selections=1,
            prompt="Choose up to 1 opponent Character with cost 2 or less to K.O.",
            callback=first_callback,
        )

    def mode_cb(selected):
        if not selected or selected[0] != "use":
            return
        _queue_bottom_from_trash_any_order(game_state, player, 3, source_card=card, on_complete=resolve_effect)

    return create_mode_choice(
        game_state, player,
        modes=[
            {"id": "use", "label": "Bottom 3", "description": "Place 3 cards from your trash at the bottom of your deck to use the effect"},
            {"id": "skip", "label": "Skip", "description": "Do not use the bottom-deck cost"},
        ],
        source_card=card,
        prompt="Choose whether to place 3 cards from your trash at the bottom of your deck",
        callback=mode_cb,
    )


# --- OP05-099: Amazon ---
@register_effect("OP05-099", "on_opponent_attack", "[On Opponent's Attack] Rest: Opponent trashes Life or -2000 power")
def op05_099_amazon(game_state, player, card):
    """On Opponent's Attack: Rest to make opponent choose trash Life or -2000 power."""
    if not getattr(card, 'is_resting', False):
        opponent = get_opponent(game_state, player)

        def after_rest(selected):
            if not selected or selected[0] != "use":
                return
            card.is_resting = True
            options = [{"id": "trash_life", "label": "Trash Top Life", "description": "Trash the top card of the attacker's Life cards"}]
            options.append({"id": "power_down", "label": "-2000 Power", "description": "Do not trash Life and instead give -2000 power"})

            def resolve_mode(mode_selected):
                if not mode_selected:
                    return
                if mode_selected[0] == "trash_life" and opponent.life_cards:
                    trashed = opponent.life_cards.pop()
                    opponent.trash.append(trashed)
                    game_state._log(f"{opponent.name} trashed the top card of their Life")
                    return
                targets = _opponent_leader_and_characters(game_state, player)
                if targets:
                    create_target_choice(
                        game_state, player, targets,
                        source_card=card,
                        min_selections=0,
                        max_selections=1,
                        prompt="Choose up to 1 opponent Leader or Character to give -2000 power during this turn",
                        callback=lambda chosen: _add_turn_power(game_state, targets[int(chosen[0])], -2000) if chosen else None,
                    )

            create_mode_choice(
                game_state, opponent, modes=options, source_card=card,
                prompt="Choose whether to trash the top card of your Life cards or let Amazon give -2000 power",
                callback=resolve_mode,
            )

        return create_mode_choice(
            game_state, player,
            modes=[
                {"id": "use", "label": "Rest Amazon", "description": "Rest this Character to use its attack trigger"},
                {"id": "skip", "label": "Skip", "description": "Do not use the effect"},
            ],
            source_card=card,
            prompt="Choose whether to rest Amazon",
            callback=after_rest,
        )
    return False


# --- OP05-100: Enel ---
@register_effect("OP05-100", "continuous", "[Rush]")
def op05_100_enel_rush(game_state, player, card):
    """Continuous: Rush."""
    card.has_rush = True
    return True


@register_effect("OP05-100", "on_leave_prevention", "[Once Per Turn] Trash Life instead of leaving field (negated by Luffy)")
def op05_100_enel_protection(game_state, player, card):
    """Once Per Turn: Trash Life instead of leaving field."""
    if getattr(card, 'op05_100_used', False) or not player.life_cards:
        return False

    all_field_cards = list(player.cards_in_play) + list(get_opponent(game_state, player).cards_in_play)
    has_luffy = any(getattr(c, 'name', '') == 'Monkey.D.Luffy' for c in all_field_cards)
    if has_luffy:
        return False

    def callback(selected):
        if not selected or selected[0] != "use" or not player.life_cards:
            return
        life_card = player.life_cards.pop()
        player.trash.append(life_card)
        card.op05_100_used = True
        game_state._log(f"{player.name} trashed the top card of their Life instead of {card.name} leaving the field")
        return True

    return create_mode_choice(
        game_state,
        player,
        modes=[
            {"id": "use", "label": "Trash Life", "description": "Trash the top card of your Life instead of this Character leaving the field"},
            {"id": "skip", "label": "Skip", "description": "Let this Character leave the field"},
        ],
        source_card=card,
        prompt="Trash 1 card from the top of your Life cards instead of this Character leaving the field?",
        callback=callback,
    )
    return False


# --- OP05-101: Ohm ---
@register_effect("OP05-101", "continuous", "If 2 or less Life, +1000")
def op05_101_ohm_continuous(game_state, player, card):
    """Continuous: +1000 if 2 or less Life."""
    sticky = getattr(card, "_sticky_power_modifier", 0)
    if len(player.life_cards) <= 2:
        card.power_modifier = sticky + 1000
    else:
        card.power_modifier = sticky
    return True


@register_effect("OP05-101", "on_play", "[On Play] Look at 5, add Holly and play it")
def op05_101_ohm_play(game_state, player, card):
    """On Play: Look at 5, add Holly, then play up to 1 Holly from hand."""
    from ...game_engine import PendingChoice

    if not player.deck:
        return True

    look_count = min(5, len(player.deck))
    top_cards = player.deck[:look_count]
    valid_indices = [i for i, c in enumerate(top_cards) if getattr(c, "name", "") == "Holly"]

    def queue_play_holly():
        holly_targets = [c for c in player.hand if getattr(c, "name", "") == "Holly"]
        if holly_targets:
            create_play_from_hand_choice(
                game_state,
                player,
                holly_targets,
                source_card=card,
                prompt="Choose up to 1 [Holly] from your hand to play",
            )

    def resolve_search(selected):
        chosen_indices = sorted([int(s) for s in selected], reverse=True) if selected else []
        chosen_indices = [i for i in chosen_indices if i in valid_indices]
        chosen_cards = []
        for idx in chosen_indices:
            if 0 <= idx < len(player.deck):
                chosen_cards.append(player.deck.pop(idx))
        for chosen_card in chosen_cards:
            player.hand.append(chosen_card)
            game_state._log(f"{card.name}: Added {chosen_card.name} to hand")

        remaining_count = look_count - len(chosen_cards)
        remaining = []
        for _ in range(remaining_count):
            if player.deck:
                remaining.append(player.deck.pop(0))

        if len(remaining) <= 1:
            for pending_card in remaining:
                player.deck.append(pending_card)
                game_state._log(f"{card.name}: Remaining card placed at bottom of deck")
            queue_play_holly()
            return

        game_state._create_deck_order_choice(
            player,
            remaining,
            [],
            source_name=card.name,
            source_id=card.id,
        )
        previous_choice = game_state.pending_choice
        if previous_choice:
            original_cb = previous_choice.callback

            def chained_cb(chosen):
                if original_cb:
                    original_cb(chosen)
                queue_play_holly()

            previous_choice.callback = chained_cb

    options = []
    for i, search_card in enumerate(top_cards):
        options.append({
            "id": str(i),
            "label": f"{search_card.name} (Cost: {getattr(search_card, 'cost', 0) or 0})",
            "card_id": search_card.id,
            "card_name": search_card.name,
            "selectable": i in valid_indices,
        })

    game_state.pending_choice = PendingChoice(
        choice_id=f"op05_101_search_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Look at the top 5 cards of your deck and reveal up to 1 [Holly] to add to your hand",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=resolve_search,
    )
    return True


# --- OP05-102: Gedatsu ---
@register_effect("OP05-102", "on_play", "[On Play] K.O. cost equal to opponent's Life count")
def op05_102_gedatsu(game_state, player, card):
    """On Play: K.O. cost equal to or less than opponent's Life count."""
    opponent = get_opponent(game_state, player)
    life_count = len(opponent.life_cards)
    targets = [c for c in opponent.cards_in_play if _is_character(c) and _effective_cost(c) <= life_count]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                               min_selections=0, max_selections=1,
                               prompt=f"Choose up to 1 opponent Character with cost {life_count} or less to K.O.")
    return True


# --- OP05-103: Kotori ---
@register_effect("OP05-103", "on_play", "[On Play] If Hotori, K.O. cost equal to opponent's Life count")
def op05_103_kotori(game_state, player, card):
    """On Play: If Hotori, K.O. cost equal to opponent's Life count."""
    has_hotori = any(getattr(c, 'name', '') == 'Hotori' for c in player.cards_in_play)
    if has_hotori:
        opponent = get_opponent(game_state, player)
        life_count = len(opponent.life_cards)
        targets = [c for c in opponent.cards_in_play if _is_character(c) and _effective_cost(c) <= life_count]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   min_selections=0, max_selections=1,
                                   prompt=f"Choose up to 1 opponent Character with cost {life_count} or less to K.O.")
    return True


# --- OP05-104: Conis ---
@register_effect("OP05-104", "on_play", "[On Play] Bottom Stage: Draw 1, trash 1")
def op05_104_conis(game_state, player, card):
    """On Play: Bottom Stage to draw 1 and trash 1."""
    if player.stage:
        def callback(selected):
            if not selected or selected[0] != "use":
                return
            stage = player.stage
            player.stage = None
            player.deck.append(stage)
            draw_cards(player, 1, game_state=game_state)
            if player.hand:
                trash_from_hand(player, 1, game_state, card)

        return create_mode_choice(
            game_state, player,
            modes=[
                {"id": "use", "label": "Bottom Stage", "description": "Place 1 of your Stages at the bottom of your deck to draw 1 and trash 1"},
                {"id": "skip", "label": "Skip", "description": "Do not use Conis's effect"},
            ],
            source_card=card,
            prompt="Place 1 of your Stages at the bottom of your deck to draw 1 card and trash 1 card from your hand?",
            callback=callback,
        )
    return True


# --- OP05-105: Satori ---
@register_effect("OP05-105", "trigger", "[Trigger] Trash 1: Play this card")
def op05_105_satori(game_state, player, card):
    """Trigger: Trash 1 to play this card."""
    if not player.hand:
        return False

    hand_snapshot = list(player.hand)

    def discard_cb(selected):
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(hand_snapshot):
            trashed = hand_snapshot[idx]
            if trashed in player.hand:
                player.hand.remove(trashed)
                player.trash.append(trashed)
                game_state._log(f"{player.name} trashed {trashed.name}")
                player.cards_in_play.append(card)
                setattr(card, 'played_turn', game_state.turn_count)
                game_state._apply_keywords(card)
                game_state._log(f"{player.name} played {card.name} from trigger")

    return create_mode_choice(
        game_state, player,
        modes=[
            {"id": "use", "label": "Trash 1", "description": "Trash 1 card from your hand and play this card"},
            {"id": "skip", "label": "Skip", "description": "Do not use the trigger"},
        ],
        source_card=card,
        prompt="Trash 1 card from your hand to play this card?",
        callback=lambda selected: create_hand_discard_choice(
            game_state, player, hand_snapshot, source_card=card,
            prompt="Choose 1 card from your hand to trash",
            callback=discard_cb,
        ) if selected and selected[0] == "use" else None,
    )


# --- OP05-106: Shura ---
@register_effect("OP05-106", "on_play", "[On Play] Look at 5, add Sky Island card")
def op05_106_shura_play(game_state, player, card):
    """On Play: Look at 5 and add Sky Island card."""
    return search_top_cards(
        game_state,
        player,
        5,
        add_count=1,
        filter_fn=lambda c: _has_type(c, "Sky Island") and getattr(c, "name", "") != "Shura",
        source_card=card,
        prompt="Look at the top 5 cards of your deck and reveal up to 1 {Sky Island} card other than [Shura] to add to your hand",
    )


@register_effect("OP05-106", "trigger", "[Trigger] Play this card")
def op05_106_shura_trigger(game_state, player, card):
    """Trigger: Play this card."""
    card.is_resting = False
    player.cards_in_play.append(card)
    setattr(card, 'played_turn', game_state.turn_count)
    game_state._apply_keywords(card)
    return True


# --- OP05-107: Lieutenant Spacey ---
@register_effect("OP05-107", "on_life_add", "[Your Turn] [Once Per Turn] When card added from Life, +2000")
def op05_107_spacey(game_state, player, card):
    """Your Turn: When card added from Life, +2000."""
    if game_state.current_player is player and not getattr(card, 'op05_107_used', False):
        _add_turn_power(game_state, card, 2000)
        card.op05_107_used = True
    return True


# --- OP05-109: Pagaya ---
@register_effect("OP05-109", "on_trigger", "[Once Per Turn] When Trigger activates, draw 2 trash 2")
def op05_109_pagaya(game_state, player, card):
    """Once Per Turn: When Trigger activates, draw 2 trash 2."""
    if not getattr(card, 'op05_109_used', False):
        draw_cards(player, 2, game_state=game_state)
        card.op05_109_used = True
        if player.hand:
            trash_from_hand(player, min(2, len(player.hand)), game_state, card)
    return True


# --- OP05-111: Hotori ---
@register_effect("OP05-111", "on_play", "[On Play] Play Kotori: Add opponent's cost 3 or less to their Life")
def op05_111_hotori(game_state, player, card):
    """On Play: Play Kotori to add opponent's cost 3 or less to their Life."""
    kotori_targets = [c for c in player.hand if getattr(c, 'name', '') == 'Kotori']
    if not kotori_targets:
        return True

    def use_cb(selected):
        if not selected or selected[0] != "use":
            return
        kotori = kotori_targets[0]
        if kotori in player.hand:
            player.hand.remove(kotori)
            player.cards_in_play.append(kotori)
            setattr(kotori, 'played_turn', game_state.turn_count)
            game_state._apply_keywords(kotori)
        opponent = get_opponent(game_state, player)
        targets = [char for char in opponent.cards_in_play if _is_character(char) and _effective_cost(char) <= 3]
        if not targets:
            return

        def position_cb(position_selected):
            position = position_selected[0] if position_selected else "top"
            create_add_to_life_choice(
                game_state,
                player,
                targets,
                source_card=card,
                owner="opponent",
                position=position,
                face_up=True,
                prompt=f"Choose up to 1 opponent Character with cost 3 or less to place at the {position} of their Life cards face-up",
            )

        create_mode_choice(
            game_state,
            player,
            modes=[
                {"id": "top", "label": "Top Life", "description": "Place the chosen Character at the top of your opponent's Life cards face-up"},
                {"id": "bottom", "label": "Bottom Life", "description": "Place the chosen Character at the bottom of your opponent's Life cards face-up"},
            ],
            source_card=card,
            prompt="Choose where to place the chosen opponent Character in Life",
            callback=position_cb,
        )

    return create_mode_choice(
        game_state,
        player,
        modes=[
            {"id": "use", "label": "Play Kotori", "description": "Play 1 [Kotori] from your hand to use this effect"},
            {"id": "skip", "label": "Skip", "description": "Do not play [Kotori] from your hand"},
        ],
        source_card=card,
        prompt="Play 1 [Kotori] from your hand?",
        callback=use_cb,
    )
    return True


# --- OP05-112: Captain McKinley ---
@register_effect("OP05-112", "blocker", "[Blocker]")
def op05_112_mckinley_blocker(game_state, player, card):
    """Blocker ability."""
    card.has_blocker = True
    return True


@register_effect("OP05-112", "on_ko", "[On K.O.] Play Sky Island cost 1")
def op05_112_mckinley_ko(game_state, player, card):
    """On K.O.: Play Sky Island cost 1 from hand."""
    targets = [c for c in player.hand if _is_character(c) and _has_type(c, 'Sky Island') and (getattr(c, 'cost', 0) or 0) == 1]
    if targets:
        return create_play_from_hand_choice(
            game_state,
            player,
            targets,
            source_card=card,
            prompt="Choose up to 1 {Sky Island} Character card with a cost of 1 to play from your hand",
        )
    return True


# --- OP05-113: Yama ---
@register_effect("OP05-113", "blocker", "[Blocker]")
def op05_113_yama(game_state, player, card):
    """Blocker ability."""
    card.has_blocker = True
    return True


# --- OP05-118: Kaido ---
@register_effect("OP05-118", "on_play", "[On Play] Draw 4 if opponent has 3 or less Life")
def op05_118_kaido(game_state, player, card):
    """On Play: Draw 4 if opponent has 3 or less Life."""
    opponent = get_opponent(game_state, player)
    if len(opponent.life_cards) <= 3:
        draw_cards(player, 4, game_state=game_state)
    return True


# --- OP05-119: Monkey.D.Luffy ---
@register_effect("OP05-119", "on_play", "[On Play] DON -10: Bottom all Characters except this, take extra turn")
def op05_119_luffy_play(game_state, player, card):
    """On Play: Return 10 DON to bottom all Characters and take extra turn."""
    if len(player.don_pool) < 10:
        return True

    def resolve_effect():
        other_characters = [c for c in player.cards_in_play if c != card and _is_character(c)]

        def finish_effect():
            player.extra_turn = True
            game_state._log(f"{player.name} will take an extra turn after this one")

        if other_characters:
            _queue_bottom_from_field_any_order(
                game_state,
                player,
                other_characters,
                source_card=card,
                on_complete=finish_effect,
            )
            return
        finish_effect()

    returned = return_don_to_deck(game_state, player, 10, source_card=card, post_callback=resolve_effect)
    if game_state.pending_choice is not None:
        return True
    if returned:
        resolve_effect()
    return True


@register_effect("OP05-119", "activate", "[Activate: Main] [Once Per Turn] DON -1: Add active DON")
def op05_119_luffy_activate(game_state, player, card):
    """Activate: Rest 1 DON to add active DON."""
    if not getattr(card, 'op05_119_used', False) and _rest_active_don(player, 1):
        add_don_from_deck(player, 1, set_active=True)
        card.op05_119_used = True
        return True
    return False


# --- OP05-021: Revolutionary Army HQ (Stage) ---
@register_effect("OP05-021", "activate", "[Activate: Main] Trash 1, rest this Stage: Look at 3, reveal Revolutionary Army card to hand")
def op05_021_revolutionary_army_hq(game_state, player, card):
    """[Activate: Main] You may trash 1 card from hand and rest this Stage:
    Look at 3 from top; reveal up to 1 Revolutionary Army type card and add to hand.
    Rest at bottom."""
    if card.is_resting:
        return False
    if getattr(card, 'main_activated_this_turn', False):
        return False
    if not player.hand:
        return False

    hand_snap = list(player.hand)

    def mode_callback(selected):
        if not selected or selected[0] != "use":
            return

        def rev_army_hq_cb(discard_selected: list) -> None:
            target_idx = int(discard_selected[0]) if discard_selected else -1
            if 0 <= target_idx < len(hand_snap):
                target = hand_snap[target_idx]
                if target in player.hand:
                    player.hand.remove(target)
                    player.trash.append(target)
                    game_state._log(f"{player.name} trashed {target.name}")
            card.is_resting = True
            card.main_activated_this_turn = True
            search_top_cards(
                game_state,
                player,
                look_count=3,
                add_count=1,
                filter_fn=lambda c: 'revolutionary army' in (c.card_origin or '').lower(),
                source_card=card,
                prompt="Look at top 3 cards and reveal up to 1 Revolutionary Army card to add to your hand",
            )

        create_hand_discard_choice(
            game_state,
            player,
            list(player.hand),
            callback=rev_army_hq_cb,
            source_card=card,
            prompt="Choose 1 card from your hand to trash for Revolutionary Army HQ",
        )

    return create_mode_choice(
        game_state,
        player,
        modes=[
            {"id": "use", "label": "Use effect", "description": "Trash 1 card from your hand and rest this Stage to look at the top 3 cards of your deck"},
            {"id": "skip", "label": "Skip", "description": "Do not use Revolutionary Army HQ"},
        ],
        source_card=card,
        prompt="Trash 1 card from your hand and rest this Stage to use Revolutionary Army HQ?",
        callback=mode_callback,
    )


# --- OP05-076: When You're at Sea... (Event) ---
@register_effect("OP05-076", "MAIN", "[Main] Look at 3, reveal SHC/Kid/Heart Pirates card to hand")
def op05_076_when_youre_at_sea(game_state, player, card):
    """[Main] Look at 3 cards from top of deck; reveal up to 1 Straw Hat Crew,
    Kid Pirates, or Heart Pirates type card and add to hand. Rest at bottom."""
    def filter_fn(c):
        origin = (c.card_origin or '').lower()
        return ('straw hat crew' in origin
                or 'kid pirates' in origin
                or 'heart pirates' in origin)
    return search_top_cards(
        game_state, player, look_count=3, add_count=1,
        filter_fn=filter_fn, source_card=card,
        prompt="Look at top 3: choose 1 Straw Hat Crew, Kid Pirates, or Heart Pirates card to add to hand")


@register_effect("OP05-076", "trigger", "[Trigger] Activate this card's [Main] effect")
def op05_076_when_youre_at_sea_trigger(game_state, player, card):
    """Trigger: Activate this card's [Main] effect."""
    return op05_076_when_youre_at_sea(game_state, player, card)


# --- OP05-117: Upper Yard (Stage) ---
@register_effect("OP05-117", "on_play", "[On Play] Look at 5, reveal Sky Island card to hand")
def op05_117_upper_yard(game_state, player, card):
    """[On Play] Look at 5 cards from top of deck; reveal up to 1 Sky Island type
    card and add to hand. Rest at bottom."""
    def filter_fn(c):
        return 'sky island' in (c.card_origin or '').lower()
    return search_top_cards(
        game_state, player, look_count=5, add_count=1,
        filter_fn=filter_fn, source_card=card,
        prompt="Look at top 5: choose 1 Sky Island card to add to hand")


# --- Missing / corrected OP05 registrations appended here ---

@register_effect("OP05-018", "counter", "[Counter] +3000, then play Revolutionary Army 5000 or less")
def op05_018_emporio_energy_hormone(game_state, player, card):
    own_targets = _own_leader_and_characters(player)
    playable = [c for c in player.hand if _is_character(c) and _has_type(c, "Revolutionary Army") and (getattr(c, "power", 0) or 0) <= 5000]

    def callback(selected):
        if selected:
            _add_battle_power(game_state, own_targets[int(selected[0])], 3000)
        if playable:
            create_play_from_hand_choice(
                game_state, player, playable, source_card=card,
                prompt="Choose up to 1 Revolutionary Army type Character card with 5000 power or less to play from hand"
            )

    return create_target_choice(
        game_state, player, own_targets,
        prompt="Choose up to 1 of your Leader or Character cards to gain +3000 power",
        source_card=card,
        min_selections=0,
        max_selections=1,
        callback=callback,
    )


@register_effect("OP05-018", "trigger", "[Trigger] Play Revolutionary Army 5000 or less")
def op05_018_emporio_energy_hormone_trigger(game_state, player, card):
    playable = [c for c in player.hand if _is_character(c) and _has_type(c, "Revolutionary Army") and (getattr(c, "power", 0) or 0) <= 5000]
    if not playable:
        return True
    return create_play_from_hand_choice(
        game_state, player, playable, source_card=card,
        prompt="Choose up to 1 Revolutionary Army type Character card with 5000 power or less to play from hand"
    )


@register_effect("OP05-020", "main", "[Main] +2000 then K.O. 2000 power or less")
def op05_020_four_thousand_brick_fist(game_state, player, card):
    own_targets = _own_leader_and_characters(player)

    def callback(selected):
        if selected:
            add_power_modifier(own_targets[int(selected[0])], 2000)
        opponent = get_opponent(game_state, player)
        ko_targets = [c for c in opponent.cards_in_play if _is_character(c) and _effective_power(c) <= 2000]
        if ko_targets:
            create_ko_choice(
                game_state, player, ko_targets, source_card=card,
                min_selections=0, max_selections=1,
                prompt="Choose up to 1 opponent Character with 2000 power or less to K.O."
            )

    return create_target_choice(
        game_state, player, own_targets,
        prompt="Choose up to 1 of your Leader or Character cards to gain +2000 power",
        source_card=card,
        min_selections=0,
        max_selections=1,
        callback=callback,
    )


@register_effect("OP05-020", "trigger", "[Trigger] +1000 to Leader or Character")
def op05_020_four_thousand_brick_fist_trigger(game_state, player, card):
    own_targets = _own_leader_and_characters(player)
    return create_power_effect_choice(
        game_state, player, own_targets, 1000,
        source_card=card,
        min_selections=0,
        max_selections=1,
        prompt="Choose up to 1 of your Leader or Character cards to gain +1000 power"
    )


@register_effect("OP05-037", "counter", "[Counter] You may trash 1 to give +3000")
def op05_037_because_justice(game_state, player, card):
    if not player.hand:
        return True
    hand_snapshot = list(player.hand)
    targets = _own_leader_and_characters(player)

    def discard_cb(selected):
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(hand_snapshot):
            trashed = hand_snapshot[idx]
            if trashed in player.hand:
                player.hand.remove(trashed)
                player.trash.append(trashed)
                game_state._log(f"{player.name} trashed {trashed.name}")

        def power_callback(power_selected):
            target_idx = int(power_selected[0]) if power_selected else -1
            if 0 <= target_idx < len(targets):
                _add_battle_power(game_state, targets[target_idx], 3000)

        if targets:
            create_target_choice(
                game_state,
                player,
                targets,
                "Choose up to 1 of your Leader or Character cards to gain +3000 power during this battle",
                source_card=card,
                min_selections=0,
                max_selections=1,
                callback=power_callback,
            )

    return create_mode_choice(
        game_state, player,
        modes=[
            {"id": "pay", "label": "Trash 1", "description": "Trash 1 card from your hand to use the effect"},
            {"id": "skip", "label": "Skip", "description": "Do not use the effect"},
        ],
        source_card=card,
        prompt="Choose whether to trash 1 card from your hand",
        callback=lambda selected: create_hand_discard_choice(
            game_state, player, hand_snapshot,
            source_card=card,
            prompt="Choose 1 card from your hand to trash",
            callback=discard_cb,
        ) if selected and selected[0] == "pay" else None,
    )


@register_effect("OP05-037", "trigger", "[Trigger] Rest cost 4 or less")
def op05_037_because_justice_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if _is_character(c) and _effective_cost(c) <= 4]
    if not targets:
        return True
    return create_rest_choice(
        game_state, player, targets, source_card=card,
        min_selections=0, max_selections=1,
        prompt="Choose up to 1 opponent Character with cost 4 or less to rest"
    )


@register_effect("OP05-038", "counter", "[Counter] +4000 then may trash 1 to set 3 DON active")
def op05_038_charlestone(game_state, player, card):
    own_targets = _own_leader_and_characters(player)

    def after_buff(selected):
        if selected:
            _add_battle_power(game_state, own_targets[int(selected[0])], 4000)
        if not player.hand:
            return
        hand_snapshot = list(player.hand)

        def discard_cb(discard_selected):
            if not discard_selected:
                return
            idx = int(discard_selected[0])
            if 0 <= idx < len(hand_snapshot):
                trashed = hand_snapshot[idx]
                if trashed in player.hand:
                    player.hand.remove(trashed)
                    player.trash.append(trashed)
                    game_state._log(f"{player.name} trashed {trashed.name}")
            activated = _set_rested_don_active(player, 3)
            if activated:
                game_state._log(f"{activated} DON!! cards were set as active")

        create_mode_choice(
            game_state, player,
            modes=[
                {"id": "pay", "label": "Trash 1", "description": "Trash 1 card from hand to set up to 3 DON!! as active"},
                {"id": "skip", "label": "Skip", "description": "Do not trash a card"},
            ],
            source_card=card,
            prompt="Choose whether to trash 1 card from your hand",
            callback=lambda mode_selected: create_hand_discard_choice(
                game_state, player, hand_snapshot,
                source_card=card,
                prompt="Choose 1 card from your hand to trash",
                callback=discard_cb,
            ) if mode_selected and mode_selected[0] == "pay" else None,
        )

    return create_target_choice(
        game_state, player, own_targets,
        prompt="Choose up to 1 of your Leader or Character cards to gain +4000 power",
        source_card=card,
        min_selections=0,
        max_selections=1,
        callback=after_buff,
    )


@register_effect("OP05-038", "trigger", "[Trigger] Rest leader or cost 3 or less")
def op05_038_charlestone_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = []
    if opponent.leader:
        targets.append(opponent.leader)
    targets.extend([c for c in opponent.cards_in_play if _is_character(c) and _effective_cost(c) <= 3])
    if not targets:
        return True
    snapshot = list(targets)

    def callback(selected):
        target_idx = int(selected[0]) if selected else -1
        if 0 <= target_idx < len(snapshot):
            target = snapshot[target_idx]
            target.is_resting = True
            game_state._log(f"{target.name} was rested")

    return create_target_choice(
        game_state, player, snapshot,
        prompt="Choose up to 1 opponent Leader or Character card with cost 3 or less to rest",
        source_card=card,
        min_selections=0, max_selections=1,
        callback=callback,
    )


@register_effect("OP05-039", "counter", "[Counter] +4000 then K.O. rested cost 3 or less")
def op05_039_stick_stickem_meteora(game_state, player, card):
    own_targets = _own_leader_and_characters(player)

    def callback(selected):
        if selected:
            _add_battle_power(game_state, own_targets[int(selected[0])], 4000)
        opponent = get_opponent(game_state, player)
        ko_targets = [c for c in opponent.cards_in_play if _is_character(c) and c.is_resting and _effective_cost(c) <= 3]
        if ko_targets:
            create_ko_choice(
                game_state, player, ko_targets, source_card=card,
                min_selections=0, max_selections=1,
                prompt="Choose up to 1 opponent rested Character with cost 3 or less to K.O."
            )

    return create_target_choice(
        game_state, player, own_targets,
        prompt="Choose up to 1 of your Leader or Character cards to gain +4000 power",
        source_card=card,
        min_selections=0,
        max_selections=1,
        callback=callback,
    )


@register_effect("OP05-039", "trigger", "[Trigger] K.O. rested cost 5 or less")
def op05_039_stick_stickem_meteora_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    ko_targets = [c for c in opponent.cards_in_play if _is_character(c) and c.is_resting and _effective_cost(c) <= 5]
    if not ko_targets:
        return True
    return create_ko_choice(
        game_state, player, ko_targets, source_card=card,
        min_selections=0, max_selections=1,
        prompt="Choose up to 1 opponent rested Character with cost 5 or less to K.O."
    )


@register_effect("OP05-057", "main", "[Main] +3000 then bottom cost 2 or less")
def op05_057_hound_blaze(game_state, player, card):
    own_targets = _own_leader_and_characters(player)

    def callback(selected):
        if selected:
            _add_turn_power(game_state, own_targets[int(selected[0])], 3000)
        all_characters = [
            c for c in player.cards_in_play + get_opponent(game_state, player).cards_in_play
            if _is_character(c) and _effective_cost(c) <= 2
        ]
        if all_characters:
            create_bottom_deck_choice(
                game_state, player, all_characters, source_card=card,
                min_selections=0,
                prompt="Choose up to 1 Character with cost 2 or less to place at the bottom of the owner's deck"
            )

    return create_target_choice(
        game_state, player, own_targets,
        prompt="Choose up to 1 of your Leader or Character cards to gain +3000 power during this turn",
        source_card=card,
        min_selections=0,
        max_selections=1,
        callback=callback,
    )


@register_effect("OP05-057", "trigger", "[Trigger] Return cost 3 or less to hand")
def op05_057_hound_blaze_trigger(game_state, player, card):
    targets = [
        c for c in player.cards_in_play + get_opponent(game_state, player).cards_in_play
        if _is_character(c) and _effective_cost(c) <= 3
    ]
    if not targets:
        return True
    return create_return_to_hand_choice(
        game_state, player, targets, source_card=card,
        optional=True,
        prompt="Choose up to 1 Character with cost 3 or less to return to the owner's hand"
    )


@register_effect("OP05-058", "main", "[Main] Bottom all cost 3 or less, then both trash to 5")
def op05_058_waste_of_human_life(game_state, player, card):
    for owner in [player, get_opponent(game_state, player)]:
        for target in [c for c in list(owner.cards_in_play) if _is_character(c) and _effective_cost(c) <= 3]:
            owner.cards_in_play.remove(target)
            owner.deck.append(target)
            game_state._log(f"{target.name} was placed at the bottom of the owner's deck")

    participants = [player, get_opponent(game_state, player)]

    def prompt_next(index):
        if index >= len(participants):
            return
        owner = participants[index]
        excess = max(0, len(owner.hand) - 5)
        if excess <= 0:
            prompt_next(index + 1)
            return
        _prompt_exact_hand_trash_local(
            game_state,
            owner,
            excess,
            card,
            f"{owner.name}: Choose {excess} card(s) from your hand to trash until you have 5 cards in hand",
            after_callback=lambda _trashed: prompt_next(index + 1),
        )

    prompt_next(0)
    return True


@register_effect("OP05-058", "trigger", "[Trigger] Bottom all cost 2 or less")
def op05_058_waste_of_human_life_trigger(game_state, player, card):
    for owner in [player, get_opponent(game_state, player)]:
        for target in [c for c in list(owner.cards_in_play) if _is_character(c) and _effective_cost(c) <= 2]:
            owner.cards_in_play.remove(target)
            owner.deck.append(target)
            game_state._log(f"{target.name} was placed at the bottom of the owner's deck")
    return True


@register_effect("OP05-059", "main", "[Main] If multicolored Leader, draw 1 then return cost 5 or less")
def op05_059_world_of_violence(game_state, player, card):
    if _is_multicolor_leader(player):
        draw_cards(player, 1, game_state=game_state)
    targets = [
        c for c in player.cards_in_play + get_opponent(game_state, player).cards_in_play
        if _is_character(c) and _effective_cost(c) <= 5
    ]
    if not targets:
        return True
    return create_return_to_hand_choice(
        game_state, player, targets, source_card=card,
        optional=True,
        prompt="Choose up to 1 Character with cost 5 or less to return to the owner's hand"
    )


@register_effect("OP05-059", "trigger", "[Trigger] If multicolored Leader, draw 2")
def op05_059_world_of_violence_trigger(game_state, player, card):
    if _is_multicolor_leader(player):
        draw_cards(player, 2, game_state=game_state)
    return True


@register_effect("OP05-077", "main", "[Main] DON -1: -5000 power")
def op05_077_gamma_knife(game_state, player, card):
    if len(player.don_pool) < 1:
        return False

    def resolve_effect():
        targets = [c for c in get_opponent(game_state, player).cards_in_play if _is_character(c)]
        if targets:
            create_target_choice(
                game_state, player, targets,
                source_card=card,
                min_selections=0,
                max_selections=1,
                prompt="Choose up to 1 opponent Character to give -5000 power during this turn",
                callback=lambda selected: _add_turn_power(game_state, targets[int(selected[0])], -5000) if selected else None,
            )

    returned = return_don_to_deck(game_state, player, 1, source_card=card, post_callback=resolve_effect)
    if game_state.pending_choice is not None:
        return True
    if returned:
        resolve_effect()
    return True


@register_effect("OP05-077", "trigger", "[Trigger] Add 1 active DON")
def op05_077_gamma_knife_trigger(game_state, player, card):
    add_don_from_deck(player, 1, set_active=True)
    return True


@register_effect("OP05-078", "main", "[Main] DON -1: Kid Pirates +5000")
def op05_078_punk_rotten(game_state, player, card):
    if len(player.don_pool) < 1:
        return False

    def resolve_effect():
        targets = []
        if player.leader and _has_type(player.leader, "Kid Pirates"):
            targets.append(player.leader)
        targets.extend([c for c in player.cards_in_play if _is_character(c) and _has_type(c, "Kid Pirates")])
        if targets:
            create_target_choice(
                game_state, player, targets,
                source_card=card,
                min_selections=0,
                max_selections=1,
                prompt="Choose up to 1 of your {Kid Pirates} Leader or Character cards to gain +5000 power during this turn",
                callback=lambda selected: _add_turn_power(game_state, targets[int(selected[0])], 5000) if selected else None,
            )

    returned = return_don_to_deck(game_state, player, 1, source_card=card, post_callback=resolve_effect)
    if game_state.pending_choice is not None:
        return True
    if returned:
        resolve_effect()
    return True


@register_effect("OP05-078", "trigger", "[Trigger] Add 1 active DON")
def op05_078_punk_rotten_trigger(game_state, player, card):
    add_don_from_deck(player, 1, set_active=True)
    return True


@register_effect("OP05-084", "continuous", "[Your Turn] If only Celestial Dragons, opponent gets -4 cost")
def op05_084_saint_charlos(game_state, player, card):
    if game_state.current_player is not player:
        return True
    if _only_celestial_dragons(player):
        opponent = get_opponent(game_state, player)
        for target in opponent.cards_in_play:
            if _is_character(target):
                target.cost_modifier = getattr(target, "cost_modifier", 0) - 4
    return True


@register_effect("OP05-094", "main", "[Main] -3 cost then cost 0 cannot unrest")
def op05_094_patch_work(game_state, player, card):
    opponent = get_opponent(game_state, player)
    reduce_targets = [c for c in opponent.cards_in_play if _is_character(c)]

    def after_reduce(selected):
        if selected:
            target = reduce_targets[int(selected[0])]
            target.cost_modifier = getattr(target, "cost_modifier", 0) - 3
            game_state._log(f"{target.name} gets -3 cost this turn")
        cannot_unrest_targets = [c for c in opponent.cards_in_play if _is_character(c) and _effective_cost(c) == 0]
        if not cannot_unrest_targets:
            return

        def unrest_cb(rest_selected):
            if not rest_selected:
                return
            target = cannot_unrest_targets[int(rest_selected[0])]
            target.cannot_unrest = True
            game_state._log(f"{target.name} will not become active in the next Refresh Phase")

        create_target_choice(
            game_state, player, cannot_unrest_targets,
            prompt="Choose up to 1 opponent Character with cost 0 that will not become active in the next Refresh Phase",
            source_card=card,
            min_selections=0,
            max_selections=1,
            callback=unrest_cb,
        )

    if not reduce_targets:
        return True
    return create_target_choice(
        game_state, player, reduce_targets,
        prompt="Choose up to 1 opponent Character to give -3 cost",
        source_card=card,
        min_selections=0,
        max_selections=1,
        callback=after_reduce,
    )


@register_effect("OP05-094", "trigger", "[Trigger] Draw 2 and trash 1")
def op05_094_patch_work_trigger(game_state, player, card):
    draw_cards(player, 2, game_state=game_state)
    if player.hand:
        trash_from_hand(player, 1, game_state, card)
    return True


@register_effect("OP05-097", "continuous", "[Your Turn] Celestial Dragons in hand cost 1 less")
def op05_097_mary_geoise(game_state, player, card):
    if game_state.current_player is not player:
        return True
    for hand_card in player.hand:
        if _is_character(hand_card) and _has_type(hand_card, "Celestial Dragons") and (getattr(hand_card, "cost", 0) or 0) >= 2:
            hand_card.cost_modifier = getattr(hand_card, "cost_modifier", 0) - 1
    return True


@register_effect("OP05-116", "main", "[Main] K.O. up to opponent Life count")
def op05_116_hino_bird_zap(game_state, player, card):
    opponent = get_opponent(game_state, player)
    max_cost = len(opponent.life_cards)
    targets = [c for c in opponent.cards_in_play if _is_character(c) and _effective_cost(c) <= max_cost]
    if not targets:
        return True
    return create_ko_choice(
        game_state, player, targets, source_card=card,
        min_selections=0,
        max_selections=1,
        prompt=f"Choose up to 1 opponent Character with cost {max_cost} or less to K.O."
    )


@register_effect("OP05-116", "trigger", "[Trigger] Activate this card's [Main] effect")
def op05_116_hino_bird_zap_trigger(game_state, player, card):
    return op05_116_hino_bird_zap(game_state, player, card)
