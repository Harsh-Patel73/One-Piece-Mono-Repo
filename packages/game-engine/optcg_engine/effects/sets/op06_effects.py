"""
Hardcoded effects for OP06 cards — Wings of the Captain.
Complete rewrite: all cards implemented with correct logic, player prompts, and helpers.
"""

import random

from ..effect_registry import (
    add_don_from_deck,
    create_add_from_trash_choice,
    create_add_to_life_choice,
    create_bottom_deck_choice,
    create_cost_reduction_choice,
    create_hand_discard_choice,
    create_ko_choice,
    create_mode_choice,
    create_own_character_choice,
    create_play_from_hand_choice,
    create_play_from_trash_choice,
    create_power_effect_choice,
    create_rest_choice,
    create_return_to_hand_choice,
    create_set_active_choice,
    create_target_choice,
    draw_cards,
    filter_by_max_cost,
    get_opponent,
    register_effect,
    return_don_to_deck,
    reorder_top_cards,
    search_top_cards,
    trash_from_hand,
    _player_index,
)


# ---------------------------------------------------------------------------
# Local helpers
# ---------------------------------------------------------------------------

def _free_don_count(player):
    """Number of DON in the pool that are not attached to cards."""
    attached = sum(getattr(c, "attached_don", 0) for c in player.cards_in_play)
    if getattr(player, "leader", None):
        attached += getattr(player.leader, "attached_don", 0)
    return max(0, len(player.don_pool) - attached)


def _rest_active_don(player, count=1):
    """Set `count` active DON to rested. Returns True if successful."""
    if player.don_pool.count("active") < count:
        return False
    rested = 0
    for idx in range(len(player.don_pool)):
        if player.don_pool[idx] == "active":
            player.don_pool[idx] = "rested"
            rested += 1
            if rested == count:
                return True
    return False


def _set_rested_don_active(player, count=1):
    """Set `count` rested free DON to active. Returns number changed."""
    changed = 0
    for idx in range(_free_don_count(player)):
        if player.don_pool[idx] == "rested":
            player.don_pool[idx] = "active"
            changed += 1
            if changed == count:
                break
    return changed


def _assign_rested_don_choice(game_state, player, targets, max_don, source_card=None, prompt=None):
    """Prompt for a Character and an amount, then attach rested DON from the free DON pool."""
    rested_free = sum(1 for i in range(_free_don_count(player)) if player.don_pool[i] == "rested")
    max_count = min(max_don, rested_free)
    if max_count <= 0 or not targets:
        return False

    import uuid
    from ...game_engine import PendingChoice

    snapshot = list(targets)
    options = []
    for card_idx, target in enumerate(snapshot):
        for count in range(1, max_count + 1):
            options.append({
                "id": f"{card_idx}:{count}",
                "label": f"{target.name}: give {count} rested DON!!",
                "card_id": target.id,
                "card_name": target.name,
            })

    def do_assign(selected):
        if not selected:
            return
        try:
            card_idx_str, count_str = selected[0].split(":", 1)
            card_idx = int(card_idx_str)
            count = int(count_str)
        except (ValueError, IndexError):
            return
        if not (0 <= card_idx < len(snapshot)):
            return
        target = snapshot[card_idx]
        assigned = 0
        while assigned < count:
            free_count = _free_don_count(player)
            rested_idx = next((i for i in range(free_count) if player.don_pool[i] == "rested"), None)
            if rested_idx is None:
                break
            player.don_pool.pop(rested_idx)
            player.don_pool.append("rested")
            target.attached_don = getattr(target, "attached_don", 0) + 1
            assigned += 1
        if assigned:
            game_state._log(f"{target.name} was given {assigned} rested DON!!")

    game_state.pending_choice = PendingChoice(
        choice_id=f"op06_assign_don_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt=prompt or f"Choose a Character to give up to {max_count} rested DON!!",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=source_card.id if source_card else "",
        source_card_name=source_card.name if source_card else "",
        callback=do_assign,
    )
    return True


def _opponent_rest_active_don(opponent, count=1):
    """Rest `count` active DON from opponent's pool."""
    rested = 0
    for idx in range(len(opponent.don_pool)):
        if opponent.don_pool[idx] == "active":
            opponent.don_pool[idx] = "rested"
            rested += 1
            if rested == count:
                return True
    return rested > 0


def _own_leader_and_chars(player):
    result = []
    if player.leader:
        result.append(player.leader)
    result.extend(player.cards_in_play)
    return result


def _add_battle_power(game_state, target, amount):
    target.power_modifier = getattr(target, "power_modifier", 0) + amount
    target._battle_power_modifier = getattr(target, "_battle_power_modifier", 0) + amount
    sign = "+" if amount >= 0 else ""
    game_state._log(f"{target.name} gets {sign}{amount} power during this battle")


def _owner_of_card(game_state, card):
    for player in (game_state.current_player, game_state.opponent_player):
        if card in player.cards_in_play:
            return player
    return None


def _queue_bottom_deck_choice(game_state, player, targets, source_card=None,
                              prompt=None, min_selections=0, max_selections=1):
    """Place up to N selected Characters at the bottom of their owners' decks."""
    if not targets:
        return False

    import uuid
    from ...game_engine import PendingChoice

    snapshot = list(targets)
    options = []
    for i, target in enumerate(snapshot):
        owner = _owner_of_card(game_state, target)
        owner_label = "Your" if owner is player else "Opponent's"
        options.append({
            "id": str(i),
            "label": f"{owner_label} {target.name} (Cost: {getattr(target, 'cost', 0) or 0})",
            "card_id": target.id,
            "card_name": target.name,
        })

    def do_bottom(selected):
        for idx_str in selected:
            idx = int(idx_str)
            if 0 <= idx < len(snapshot):
                target = snapshot[idx]
                owner = _owner_of_card(game_state, target)
                if owner and target in owner.cards_in_play:
                    owner.cards_in_play.remove(target)
                    owner.deck.append(target)
                    game_state._log(f"{target.name} was placed at the bottom of {owner.name}'s deck")

    game_state.pending_choice = PendingChoice(
        choice_id=f"op06_bottom_multi_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt=prompt or "Choose Character(s) to place at the bottom of the owner's deck",
        options=options,
        min_selections=min_selections,
        max_selections=min(max_selections, len(snapshot)),
        source_card_id=source_card.id if source_card else "",
        source_card_name=source_card.name if source_card else "",
        callback=do_bottom,
    )
    return True


def _trash_from_hand_choice(game_state, player, count, source_card=None, prompt=None, optional=False,
                            on_complete=None):
    if count <= 0:
        if on_complete:
            on_complete([])
        return True
    if len(player.hand) < count:
        return False

    import uuid
    from ...game_engine import PendingChoice

    snapshot = list(player.hand)
    options = [{"id": str(i), "label": f"{c.name} (Cost: {getattr(c, 'cost', 0) or 0})",
                "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

    def do_trash(selected):
        trashed = []
        for idx_str in selected:
            idx = int(idx_str)
            if 0 <= idx < len(snapshot):
                chosen = snapshot[idx]
                if chosen in player.hand:
                    player.hand.remove(chosen)
                    player.trash.append(chosen)
                    trashed.append(chosen)
                    game_state._log(f"{player.name} trashed {chosen.name}")
        if on_complete:
            on_complete(trashed)

    game_state.pending_choice = PendingChoice(
        choice_id=f"op06_trash_hand_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt=prompt or f"Choose {count} card(s) from hand to trash",
        options=options,
        min_selections=0 if optional else count,
        max_selections=count,
        source_card_id=source_card.id if source_card else "",
        source_card_name=source_card.name if source_card else "",
        callback=do_trash,
    )
    return True


# =============================================================================
# LEADER EFFECTS
# =============================================================================

# --- OP06-001: Uta (Leader) ---
@register_effect("OP06-001", "on_attack", "[When Attacking] Trash 1 FILM: Opponent's Character -2000 power, add 1 DON rested")
def op06_001_uta_leader(game_state, player, card):
    """When Attacking: You may trash 1 FILM card from hand → opponent Character -2000, add 1 DON rested."""
    film_cards = [c for c in player.hand if "film" in (getattr(c, "card_origin", "") or "").lower()]
    if not film_cards:
        return False

    opponent = get_opponent(game_state, player)
    targets = list(opponent.cards_in_play)

    snap = list(film_cards)

    def after_film_trash(selected):
        idx = int(selected[0]) if selected else -1
        trashed = False
        if 0 <= idx < len(snap):
            chosen = snap[idx]
            if chosen in player.hand:
                player.hand.remove(chosen)
                player.trash.append(chosen)
                trashed = True
                game_state._log(f"{player.name} trashed {chosen.name} (FILM)")
        if not trashed:
            return
        # Add 1 DON from deck rested
        add_don_from_deck(player, 1, set_active=False)
        # Now prompt -2000 target choice
        opp_targets = list(get_opponent(game_state, player).cards_in_play)
        if opp_targets:
            create_power_effect_choice(
                game_state, player, opp_targets, -2000,
                source_card=card,
                prompt="Choose opponent's Character to give −2000 power",
                min_selections=0,
            )

    return create_own_character_choice(
        game_state, player, snap, source_card=card,
        prompt="You may choose a FILM card from hand to trash",
        callback=after_film_trash,
        optional=True,
    )


# --- OP06-020: Hody Jones (Leader) ---
@register_effect("OP06-020", "activate", "[Activate: Main] Rest this Leader: Rest opponent DON or cost 3 or less Character. Cannot add Life this turn.")
def op06_020_hody_leader(game_state, player, card):
    """Activate: Rest this Leader → rest opponent's DON!! or cost 3 or less Character. No life-to-hand this turn."""
    if card.is_resting:
        return False
    card.is_resting = True
    player.cannot_add_life_to_hand_this_turn = True

    opponent = get_opponent(game_state, player)
    char_targets = [c for c in opponent.cards_in_play if (getattr(c, "cost", 0) or 0) <= 3]
    has_active_don = any(d == "active" for d in opponent.don_pool)

    modes = []
    if has_active_don:
        modes.append({"id": "don", "label": "Rest opponent's DON!!", "description": "Rest 1 active DON from opponent's pool"})
    if char_targets:
        modes.append({"id": "char", "label": "Rest cost 3 or less Character", "description": f"{len(char_targets)} valid targets"})
    modes.append({"id": "none", "label": "Do not rest a DON!! or Character", "description": "Choose zero targets"})

    if not modes:
        return True

    def callback(selected):
        mode = selected[0] if selected else None
        opp = get_opponent(game_state, player)
        if mode == "don":
            _opponent_rest_active_don(opp, 1)
            game_state._log(f"{opp.name}'s DON!! was rested")
        elif mode == "char":
            targets = [c for c in opp.cards_in_play if (getattr(c, "cost", 0) or 0) <= 3]
            if targets:
                create_rest_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose up to 1 opponent's cost 3 or less Character to rest",
                                   min_selections=0)

    return create_mode_choice(game_state, player, modes, source_card=card, callback=callback,
                              prompt="Choose Hody Jones Leader effect")


# --- OP06-021: Perona (Leader) ---
@register_effect("OP06-021", "activate", "[Activate: Main] [Once Per Turn] Rest cost 4 or less OR give -1 cost")
def op06_021_perona_leader(game_state, player, card):
    """Once Per Turn: Rest opponent's cost 4 or less OR give opponent's Character -1 cost."""
    if getattr(card, "op06_021_used", False):
        return False

    opponent = get_opponent(game_state, player)
    rest_targets = [c for c in opponent.cards_in_play if not c.is_resting and (getattr(c, "cost", 0) or 0) <= 4]
    cost_targets = list(opponent.cards_in_play)

    modes = []
    if rest_targets:
        modes.append({"id": "rest", "label": "Rest cost 4 or less Character", "description": f"{len(rest_targets)} targets"})
    if cost_targets:
        modes.append({"id": "cost", "label": "Give opponent's Character −1 cost", "description": f"{len(cost_targets)} targets"})

    if not modes:
        return False

    card.op06_021_used = True

    def callback(selected):
        mode = selected[0] if selected else None
        opp = get_opponent(game_state, player)
        if mode == "rest":
            targets = [c for c in opp.cards_in_play if not c.is_resting and (getattr(c, "cost", 0) or 0) <= 4]
            if targets:
                create_rest_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose up to 1 opponent's cost 4 or less Character to rest",
                                   min_selections=0)
        elif mode == "cost":
            targets = list(opp.cards_in_play)
            if targets:
                create_cost_reduction_choice(game_state, player, targets, -1, source_card=card,
                                             prompt="Choose up to 1 opponent's Character to give -1 cost",
                                             min_selections=0)

    return create_mode_choice(game_state, player, modes, source_card=card, callback=callback,
                              prompt="Choose Perona Leader effect")


# --- OP06-022: Yamato (Leader) ---
@register_effect("OP06-022", "continuous", "[Double Attack]")
def op06_022_yamato_continuous(game_state, player, card):
    card.has_doubleattack = True
    card.has_double_attack = True
    return True


@register_effect("OP06-022", "activate", "[Activate: Main] [Once Per Turn] If opponent 3 or less Life, give up to 2 rested DON to 1 Character")
def op06_022_yamato_activate(game_state, player, card):
    """Once Per Turn: If opponent has 3 or less Life, give up to 2 rested DON to 1 Character."""
    if getattr(card, "op06_022_used", False):
        return False
    opponent = get_opponent(game_state, player)
    if len(opponent.life_cards) > 3:
        return False
    rested_free = sum(1 for i in range(_free_don_count(player)) if player.don_pool[i] == "rested")
    if rested_free <= 0 or not player.cards_in_play:
        return False
    card.op06_022_used = True
    return _assign_rested_don_choice(
        game_state, player, player.cards_in_play, 2,
        source_card=card,
        prompt="Choose your Character to give up to 2 rested DON!!"
    )


# --- OP06-042: Vinsmoke Reiju (Leader) ---
@register_effect("OP06-042", "on_don_return", "[Your Turn] [Once Per Turn] When a DON!! is returned to DON deck, draw 1")
def op06_042_reiju_leader(game_state, player, card):
    """Your Turn, Once Per Turn: When a DON!! is returned to DON deck, draw 1 card."""
    if getattr(card, "op06_042_used", False):
        return False
    draw_cards(player, 1)
    card.op06_042_used = True
    return True


# --- OP06-080: Gecko Moria (Leader) ---
@register_effect("OP06-080", "on_attack", "[DON!! x1] [When Attacking] Rest 2 DON, trash 1: Trash 2 from deck, play Thriller Bark Pirates cost 4 or less from trash")
def op06_080_moria_leader(game_state, player, card):
    """DON!! x1, When Attacking, Rest 2 active DON, trash 1 from hand: Trash 2 from top of deck, play Thriller Bark Pirates cost 4 or less from trash."""
    if getattr(card, "attached_don", 0) < 1:
        return False
    active_free = sum(1 for i in range(_free_don_count(player)) if player.don_pool[i] == "active")
    if active_free < 2:
        return False
    if not player.hand:
        return False

    _rest_active_don(player, 2)

    def after_discard(trashed):
        if not trashed:
            return
        for _ in range(min(2, len(player.deck))):
            player.trash.append(player.deck.pop(0))

        tb_targets = [c for c in player.trash
                      if "Thriller Bark Pirates" in (getattr(c, "card_origin", "") or "")
                      and getattr(c, "card_type", "") == "CHARACTER"
                      and (getattr(c, "cost", 0) or 0) <= 4]
        if tb_targets:
            create_play_from_trash_choice(
                game_state, player, tb_targets, source_card=card, rest_on_play=False,
                prompt="Choose a Thriller Bark Pirates Character with cost 4 or less from trash to play"
            )

    return _trash_from_hand_choice(
        game_state, player, 1, source_card=card,
        prompt="Trash 1 card from hand for Gecko Moria Leader",
        on_complete=after_discard,
    )


# =============================================================================
# CHARACTER EFFECTS
# =============================================================================

# --- OP06-002: Inazuma ---
@register_effect("OP06-002", "continuous", "If 7000+ power, gains [Banish]")
def op06_002_inazuma(game_state, player, card):
    total = (getattr(card, "power", 0) or 0) + getattr(card, "power_modifier", 0)
    card.has_banish = total >= 7000
    return True


# --- OP06-003: Emporio.Ivankov ---
@register_effect("OP06-003", "on_play", "[On Play] Look at 3, play Revolutionary Army 5000 or less")
def op06_003_ivankov(game_state, player, card):
    """On Play: Look at 3 from deck, play up to 1 Revolutionary Army CHARACTER with 5000 power or less. Place rest at bottom."""
    return search_top_cards(
        game_state, player, look_count=3, add_count=1,
        filter_fn=lambda c: (getattr(c, "card_type", "") == "CHARACTER"
                             and "Revolutionary Army" in (getattr(c, "card_origin", "") or "")
                             and (getattr(c, "power", 0) or 0) <= 5000),
        source_card=card,
        play_to_field=True,
        prompt="Look at top 3: choose up to 1 Revolutionary Army Character (5000 power or less) to play",
    )


# --- OP06-004: Baron Omatsuri ---
@register_effect("OP06-004", "on_play", "[On Play] Play up to 1 [Lily Carnation] from hand")
def op06_004_baron(game_state, player, card):
    targets = [c for c in player.hand if getattr(c, "name", "") == "Lily Carnation"]
    if targets:
        return create_play_from_hand_choice(
            game_state, player, targets, source_card=card,
            prompt="Choose [Lily Carnation] from hand to play"
        )
    return True


# --- OP06-006: Saga ---
@register_effect("OP06-006", "on_attack", "[DON!! x1] [When Attacking] +1000 until next turn, trash 1 FILM Character at end of turn")
def op06_006_saga(game_state, player, card):
    """When Attacking with 1 DON attached: +1000 power until next turn, trash 1 FILM type Character at end of this turn."""
    if getattr(card, "attached_don", 0) < 1:
        return False
    card.power_modifier = getattr(card, "power_modifier", 0) + 1000
    card._sticky_power_modifier = getattr(card, "_sticky_power_modifier", 0) + 1000
    card.power_modifier_expires_on_turn = game_state.turn_count + 1
    card._sticky_power_modifier_expires_on_turn = game_state.turn_count + 1
    # Mark to trash a FILM Character at end of turn
    player.trash_film_character_eot = True
    return True


@register_effect("OP06-006", "end_of_turn", "Trash 1 FILM Character from hand at end of turn")
def op06_006_saga_eot(game_state, player, card):
    """End of Turn: If effect was used, trash 1 FILM Character from hand (mandatory if available)."""
    if not getattr(player, "trash_film_character_eot", False):
        return False
    player.trash_film_character_eot = False
    film_chars = [c for c in player.hand
                  if "FILM" in (getattr(c, "card_origin", "") or "")
                  and getattr(c, "card_type", "") == "CHARACTER"]
    if not film_chars:
        return True  # No FILM Characters in hand — skip
    import uuid
    from ...game_engine import PendingChoice
    snap = list(film_chars)
    opts = [{"id": str(i), "label": c.name, "card_id": c.id, "card_name": c.name}
            for i, c in enumerate(snap)]

    def do_trash(selected):
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(snap) and snap[idx] in player.hand:
            player.hand.remove(snap[idx])
            player.trash.append(snap[idx])
            game_state._log(f"{player.name} trashed {snap[idx].name} (Saga end of turn)")

    game_state.pending_choice = PendingChoice(
        choice_id=f"op06_006_eot_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="[Saga] You must trash 1 FILM type Character from your hand",
        options=opts, min_selections=1, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=do_trash,
    )
    return True


# --- OP06-007: Shanks ---
@register_effect("OP06-007", "on_play", "[On Play] K.O. up to 1 opponent's Characters with 10000 power or less")
def op06_007_shanks(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, "power", 0) or 0) <= 10000]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                                prompt="Choose opponent's Character with 10000 power or less to K.O.")
    return True


# --- OP06-009: Shuraiya ---
@register_effect("OP06-009", "blocker", "[Blocker]")
def op06_009_shuraiya_blocker(game_state, player, card):
    card.has_blocker = True
    return True


@register_effect("OP06-009", "on_attack", "[When Attacking]/[On Block] [Once Per Turn] Match opponent Leader's power until next turn")
def op06_009_shuraiya_attack(game_state, player, card):
    """When Attacking or On Block (Once Per Turn): Match opponent Leader's power until next turn."""
    if getattr(card, "op06_009_used", False):
        return False
    opponent = get_opponent(game_state, player)
    if not opponent.leader:
        return False
    opp_power = (getattr(opponent.leader, "power", 0) or 0) + getattr(opponent.leader, "power_modifier", 0)
    base = getattr(card, "power", 0) or 0
    delta = opp_power - base
    card.power_modifier = getattr(card, "power_modifier", 0) + delta
    card.power_modifier_expires_on_turn = game_state.turn_count + 1
    card.op06_009_used = True
    game_state._log(f"{card.name} matches opponent Leader power: {opp_power}")
    return True


@register_effect("OP06-009", "on_block", "[When Attacking]/[On Block] [Once Per Turn] Match opponent Leader's power until next turn")
def op06_009_shuraiya_block(game_state, player, card):
    return op06_009_shuraiya_attack(game_state, player, card)


# --- OP06-010: Douglas Bullet ---
@register_effect("OP06-010", "continuous", "If FILM Leader, gains [Blocker]")
def op06_010_bullet(game_state, player, card):
    card.has_blocker = "FILM" in (getattr(player.leader, "card_origin", "") or "") if player.leader else False
    return True


# --- OP06-011: Tot Musica ---
@register_effect("OP06-011", "activate", "[Activate: Main] [Once Per Turn] Rest 1 [Uta]: This Character +5000 power this turn")
def op06_011_tot_musica(game_state, player, card):
    if getattr(card, "op06_011_used", False):
        return False
    uta_targets = [c for c in player.cards_in_play if "Uta" in getattr(c, "name", "") and not c.is_resting]
    if not uta_targets:
        return False
    card.op06_011_used = True
    snap = list(uta_targets)
    tot_ref = card

    def callback(selected):
        idx = int(selected[0]) if selected else -1
        if 0 <= idx < len(snap):
            snap[idx].is_resting = True
            game_state._log(f"{snap[idx].name} was rested")
        tot_ref.power_modifier = getattr(tot_ref, "power_modifier", 0) + 5000
        game_state._log(f"{tot_ref.name} gains +5000 power this turn")

    return create_rest_choice(game_state, player, uta_targets, source_card=card,
                              prompt="Choose an [Uta] to rest (Tot Musica gains +5000 power)",
                              callback=callback)


# --- OP06-012: Bear.King ---
@register_effect("OP06-012", "continuous", "If opponent has 6000+ base power Leader or Character, cannot be K.O.'d in battle")
def op06_012_bearking(game_state, player, card):
    opponent = get_opponent(game_state, player)
    has_6k = (opponent.leader and (getattr(opponent.leader, "power", 0) or 0) >= 6000) or \
             any((getattr(c, "power", 0) or 0) >= 6000 for c in opponent.cards_in_play)
    card.cannot_be_ko_in_battle = has_6k
    return True


# --- OP06-013: Monkey.D.Luffy ---
@register_effect("OP06-013", "on_play", "[On Play] Look at 3, reveal up to 1 FILM card and add to hand")
def op06_013_luffy_play(game_state, player, card):
    return search_top_cards(
        game_state, player, look_count=3, add_count=1,
        filter_fn=lambda c: "FILM" in (getattr(c, "card_origin", "") or ""),
        source_card=card,
        prompt="Look at top 3: choose up to 1 FILM type card to add to hand",
    )


@register_effect("OP06-013", "trigger", "[Trigger] Activate this card's [On Play] effect")
def op06_013_luffy_trigger(game_state, player, card):
    return op06_013_luffy_play(game_state, player, card)


# --- OP06-014: Ratchet ---
@register_effect("OP06-014", "on_opponent_attack", "[On Opponent's Attack] Trash any number of FILM cards: Leader or Character +1000 per card")
def op06_014_ratchet(game_state, player, card):
    """On Opponent's Attack: Trash any FILM cards from hand. Leader or Character gains +1000 per card trashed."""
    film_cards = [c for c in player.hand if "FILM" in (getattr(c, "card_origin", "") or "")]
    if not film_cards:
        return False
    import uuid
    from ...game_engine import PendingChoice

    snap = list(film_cards)
    options = [{"id": str(i), "label": f"{c.name} (Cost: {getattr(c, 'cost', 0) or 0})",
                "card_id": c.id, "card_name": c.name} for i, c in enumerate(snap)]

    def after_trash(selected):
        count = 0
        for idx_str in selected:
            idx = int(idx_str)
            if 0 <= idx < len(snap) and snap[idx] in player.hand:
                player.hand.remove(snap[idx])
                player.trash.append(snap[idx])
                count += 1
        if count > 0:
            attack = getattr(game_state, "pending_attack", None) or {}
            attacked = attack.get("current_target")
            if attacked in _own_leader_and_chars(player):
                _add_battle_power(game_state, attacked, count * 1000)

    game_state.pending_choice = PendingChoice(
        choice_id=f"op06_014_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Choose any number of FILM cards from hand to trash",
        options=options,
        min_selections=0,
        max_selections=len(options),
        source_card_id=card.id,
        source_card_name=card.name,
        callback=after_trash,
    )
    return True


# --- OP06-015: Lily Carnation ---
@register_effect("OP06-015", "activate", "[Activate: Main] [Once Per Turn] Trash 6000+ power Character: Play FILM 2000-5000 from trash rested")
def op06_015_lily_carnation(game_state, player, card):
    if getattr(card, "op06_015_used", False):
        return False
    big_chars = [c for c in player.cards_in_play if c != card and (getattr(c, "power", 0) or 0) >= 6000]
    if not big_chars:
        return False
    card.op06_015_used = True
    snap = list(big_chars)

    def after_ko(selected):
        idx = int(selected[0]) if selected else -1
        if 0 <= idx < len(snap):
            target = snap[idx]
            if target in player.cards_in_play:
                player.cards_in_play.remove(target)
                player.trash.append(target)
                game_state._log(f"{target.name} was trashed")
        film_targets = [c for c in player.trash
                        if "film" in (getattr(c, "card_origin", "") or "").lower()
                        and getattr(c, "card_type", "") == "CHARACTER"
                        and 2000 <= (getattr(c, "power", 0) or 0) <= 5000]
        if film_targets:
            create_play_from_trash_choice(
                game_state, player, film_targets, source_card=card, rest_on_play=True,
                prompt="Choose FILM Character (2000-5000 power) from trash to play rested"
            )

    return create_ko_choice(game_state, player, big_chars, source_card=card,
                            prompt="Choose your 6000+ power Character to trash",
                            callback=after_ko)


# --- OP06-016: Raise Max ---
@register_effect("OP06-016", "activate", "[Activate: Main] Place this at bottom of deck: Opponent's Character -3000 power")
def op06_016_raise_max(game_state, player, card):
    if card not in player.cards_in_play:
        return False
    player.cards_in_play.remove(card)
    player.deck.append(card)
    opponent = get_opponent(game_state, player)
    targets = list(opponent.cards_in_play)
    if targets:
        return create_power_effect_choice(
            game_state, player, targets, -3000, source_card=card,
            prompt="Choose opponent's Character to give −3000 power",
            min_selections=0,
        )
    return True


# --- OP06-023: Arlong ---
@register_effect("OP06-023", "on_play", "[On Play] Trash 1: Opponent's rested Leader cannot attack until end of opponent's next turn")
def op06_023_arlong_play(game_state, player, card):
    if not player.hand:
        return True

    def after_discard(trashed):
        if not trashed:
            return
        opponent = get_opponent(game_state, player)
        if opponent.leader and opponent.leader.is_resting:
            opponent.leader.cannot_attack = True
            opponent.leader.cannot_attack_until_turn = game_state.turn_count + 1
            game_state._log(f"{opponent.leader.name} cannot attack until end of next turn")

    return _trash_from_hand_choice(
        game_state, player, 1, source_card=card,
        prompt="You may trash 1 card from hand for Arlong",
        optional=True,
        on_complete=after_discard,
    )


@register_effect("OP06-023", "trigger", "[Trigger] Rest opponent's cost 4 or less Character")
def op06_023_arlong_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, "cost", 0) or 0) <= 4]
    if targets:
        return create_rest_choice(game_state, player, targets, source_card=card,
                                  prompt="Choose opponent's cost 4 or less Character to rest")
    return True


# --- OP06-024: Ikaros Much ---
@register_effect("OP06-024", "on_play", "[On Play] If New Fish-Man Pirates Leader, play Fish-Man cost 4 or less from hand, add 1 Life to hand")
def op06_024_ikaros_much(game_state, player, card):
    if not (player.leader and "New Fish-Man Pirates" in (getattr(player.leader, "card_origin", "") or "")):
        return True
    targets = [c for c in player.hand
               if "Fish-Man" in (getattr(c, "card_origin", "") or "")
               and (getattr(c, "cost", 0) or 0) <= 4]

    def add_life_to_hand():
        if player.life_cards:
            life_card = player.life_cards.pop()
            player.hand.append(life_card)
            game_state._log(f"{player.name} added 1 Life card to hand")

    def play_then_add_life(selected):
        if selected:
            idx = int(selected[0])
            if 0 <= idx < len(targets):
                target = targets[idx]
                if target in player.hand:
                    player.hand.remove(target)
                    target.is_resting = False
                    setattr(target, "played_turn", game_state.turn_count)
                    player.cards_in_play.append(target)
                    game_state._apply_keywords(target)
                    game_state._log(f"{player.name} played {target.name} from hand")
                    if target.effect and "[On Play]" in target.effect:
                        game_state._trigger_on_play_effects(target)
        add_life_to_hand()

    if targets:
        return create_play_from_hand_choice(
            game_state, player, targets, source_card=card,
            prompt="Choose a Fish-Man type Character with cost 4 or less from hand to play",
            callback=play_then_add_life,
        )
    add_life_to_hand()
    return True


# --- OP06-025: Camie ---
@register_effect("OP06-025", "on_play", "[On Play] Look at 4, reveal up to 1 Fish-Man or Merfolk card (not Camie) to hand")
def op06_025_camie(game_state, player, card):
    return search_top_cards(
        game_state, player, look_count=4, add_count=1,
        filter_fn=lambda c: (("Fish-Man" in (getattr(c, "card_origin", "") or "")
                              or "Merfolk" in (getattr(c, "card_origin", "") or ""))
                             and getattr(c, "name", "") != "Camie"),
        source_card=card,
        prompt="Look at top 4: choose up to 1 Fish-Man or Merfolk card (not Camie) to add to hand",
    )


# --- OP06-026: Koushirou ---
@register_effect("OP06-026", "on_play", "[On Play] Set Slash cost 4 or less as active. Cannot attack Leader this turn.")
def op06_026_koushirou(game_state, player, card):
    slash_targets = [c for c in player.cards_in_play
                     if getattr(c, "attribute", "") == "Slash" and (getattr(c, "cost", 0) or 0) <= 4]
    player.cannot_attack_opponent_leader = True
    player.cannot_attack_opponent_leader_until_turn = game_state.turn_count
    if slash_targets:
        return create_set_active_choice(
            game_state, player, slash_targets, source_card=card,
            prompt="Choose your Slash attribute cost 4 or less Character to set active"
        )
    return True


# --- OP06-027: Gyro ---
@register_effect("OP06-027", "on_ko", "[On K.O.] Rest opponent's cost 3 or less Character")
def op06_027_gyro(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, "cost", 0) or 0) <= 3]
    if targets:
        return create_rest_choice(game_state, player, targets, source_card=card,
                                  prompt="Choose opponent's cost 3 or less Character to rest")
    return True


# --- OP06-028: Zeo ---
@register_effect("OP06-028", "on_attack", "[DON!! x1] [When Attacking] If New Fish-Man Pirates Leader, set 1 DON active, +1000, add 1 Life to hand")
def op06_028_zeo(game_state, player, card):
    if getattr(card, "attached_don", 0) < 1:
        return False
    if not (player.leader and "New Fish-Man Pirates" in (getattr(player.leader, "card_origin", "") or "")):
        return False
    import uuid
    from ...game_engine import PendingChoice

    free_count = _free_don_count(player)
    rested_indices = [idx for idx in range(free_count) if player.don_pool[idx] == "rested"]
    if not rested_indices:
        return True  # No rested DON to set active

    def after_don_choice(selected):
        if not selected:
            return
        try:
            don_idx = int(selected[0])
        except (TypeError, ValueError):
            return
        if 0 <= don_idx < len(player.don_pool) and player.don_pool[don_idx] == "rested":
            player.don_pool[don_idx] = "active"
        else:
            return
        card.power_modifier = getattr(card, "power_modifier", 0) + 1000
        card._sticky_power_modifier = getattr(card, "_sticky_power_modifier", 0) + 1000
        card.power_modifier_expires_on_turn = game_state.turn_count
        card._sticky_power_modifier_expires_on_turn = game_state.turn_count
        if player.life_cards:
            player.hand.append(player.life_cards.pop())
        game_state._log(f"{card.name}: Set DON!! #{don_idx + 1} active, +1000 power, added 1 Life to hand")

    game_state.pending_choice = PendingChoice(
        choice_id=f"op06_028_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt="Choose a rested DON!! to set active",
        options=[{"id": str(idx), "label": f"DON!! #{idx + 1} (rested)"} for idx in rested_indices],
        min_selections=1,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=after_don_choice,
    )
    return True


# --- OP06-029: Daruma ---
@register_effect("OP06-029", "on_attack", "[DON!! x1] [When Attacking] [Once Per Turn] If New Fish-Man Pirates Leader, set this active, +1000, add 1 Life to hand")
def op06_029_daruma(game_state, player, card):
    if getattr(card, "op06_029_used", False):
        return False
    if getattr(card, "attached_don", 0) < 1:
        return False
    if not (player.leader and "New Fish-Man Pirates" in (getattr(player.leader, "card_origin", "") or "")):
        return False
    card._set_active_after_battle_resolution = True
    card.power_modifier = getattr(card, "power_modifier", 0) + 1000
    card._sticky_power_modifier = getattr(card, "_sticky_power_modifier", 0) + 1000
    card.power_modifier_expires_on_turn = game_state.turn_count
    card._sticky_power_modifier_expires_on_turn = game_state.turn_count
    if player.life_cards:
        player.hand.append(player.life_cards.pop())
    card.op06_029_used = True
    return True


# --- OP06-030: Dosun ---
@register_effect("OP06-030", "on_attack", "[When Attacking] If New Fish-Man Pirates Leader, cannot be K.O.'d, +2000 until next turn, add 1 Life to hand")
def op06_030_dosun(game_state, player, card):
    if not (player.leader and "New Fish-Man Pirates" in (getattr(player.leader, "card_origin", "") or "")):
        return False
    card.cannot_be_ko_in_battle = True
    card.power_modifier = getattr(card, "power_modifier", 0) + 2000
    card._sticky_power_modifier = getattr(card, "_sticky_power_modifier", 0) + 2000
    card.power_modifier_expires_on_turn = game_state.turn_count + 1
    card._sticky_power_modifier_expires_on_turn = game_state.turn_count + 1
    if player.life_cards:
        player.hand.append(player.life_cards.pop())
    return True


# --- OP06-031: Hatchan ---
@register_effect("OP06-031", "trigger", "[Trigger] Play Fish-Man or Merfolk cost 3 or less from hand")
def op06_031_hatchan(game_state, player, card):
    targets = [c for c in player.hand
               if (("Fish-Man" in (getattr(c, "card_origin", "") or "")
                    or "Merfolk" in (getattr(c, "card_origin", "") or ""))
                   and (getattr(c, "cost", 0) or 0) <= 3)]
    if targets:
        return create_play_from_hand_choice(
            game_state, player, targets, source_card=card,
            prompt="Choose a Fish-Man or Merfolk type Character with cost 3 or less to play"
        )
    return True


# --- OP06-032: Hammond ---
@register_effect("OP06-032", "blocker", "[Blocker]")
def op06_032_hammond(game_state, player, card):
    card.has_blocker = True
    return True


# --- OP06-033: Vander Decken IX ---
@register_effect("OP06-033", "on_play", "[On Play] Trash Fish-Man from hand or Ark Noah from hand/field: K.O. opponent's rested Character")
def op06_033_vander_decken(game_state, player, card):
    cost_cards = []
    for c in player.hand:
        if "Fish-Man" in (getattr(c, "card_origin", "") or "") or getattr(c, "name", "") == "The Ark Noah":
            cost_cards.append(("hand", c))
    for c in player.cards_in_play:
        if getattr(c, "name", "") == "The Ark Noah":
            cost_cards.append(("field", c))
    if not cost_cards:
        return True

    snap = list(cost_cards)
    opts = [
        {"id": str(i), "label": f"{zone}: {c.name}", "card_id": c.id, "card_name": c.name}
        for i, (zone, c) in enumerate(snap)
    ]

    def after_cost(selected):
        if not selected:
            return
        idx = int(selected[0])
        if not (0 <= idx < len(snap)):
            return
        zone, cost_card = snap[idx]
        if zone == "hand" and cost_card in player.hand:
            player.hand.remove(cost_card)
            player.trash.append(cost_card)
        elif zone == "field" and cost_card in player.cards_in_play:
            player.cards_in_play.remove(cost_card)
            player.trash.append(cost_card)
        else:
            return
        game_state._log(f"{player.name} trashed {cost_card.name} for Vander Decken IX")
        opponent = get_opponent(game_state, player)
        rested = [c for c in opponent.cards_in_play if c.is_resting]
        if rested:
            create_ko_choice(game_state, player, rested, source_card=card,
                             prompt="Choose up to 1 opponent's rested Character to K.O.",
                             min_selections=0)

    from ...game_engine import PendingChoice
    import uuid
    game_state.pending_choice = PendingChoice(
        choice_id=f"op06_033_{uuid.uuid4().hex[:6]}",
        choice_type="select_cards",
        prompt="You may trash 1 Fish-Man from hand or The Ark Noah from hand/field",
        options=opts,
        min_selections=0,
        max_selections=1,
        source_card_id=card.id,
        source_card_name=card.name,
        callback=after_cost,
    )
    return True


# --- OP06-034: Hyouzou ---
@register_effect("OP06-034", "activate", "[Activate: Main] [Once Per Turn] Rest opponent cost 4 or less, +1000 power, add 1 Life to hand")
def op06_034_hyouzou(game_state, player, card):
    if getattr(card, "op06_034_used", False):
        return False
    card.op06_034_used = True
    card.power_modifier = getattr(card, "power_modifier", 0) + 1000
    card._sticky_power_modifier = getattr(card, "_sticky_power_modifier", 0) + 1000
    card.power_modifier_expires_on_turn = game_state.turn_count
    card._sticky_power_modifier_expires_on_turn = game_state.turn_count
    if player.life_cards:
        player.hand.append(player.life_cards.pop())
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, "cost", 0) or 0) <= 4]
    if targets:
        return create_rest_choice(game_state, player, targets, source_card=card,
                                  prompt="Choose opponent's cost 4 or less Character to rest")
    return True


# --- OP06-035: Hody Jones ---
@register_effect("OP06-035", "continuous", "[Rush]")
def op06_035_hody_rush(game_state, player, card):
    card.has_rush = True
    return True


@register_effect("OP06-035", "on_play", "[On Play] Rest up to total 2 opponent's Characters or DON!!, add 1 Life to hand")
def op06_035_hody_play(game_state, player, card):
    """On Play: Rest up to total 2 of opponent's Characters or DON!! cards. Add 1 Life to hand."""
    if player.life_cards:
        player.hand.append(player.life_cards.pop())

    opponent = get_opponent(game_state, player)
    char_targets = list(opponent.cards_in_play)
    has_active_don = any(d == "active" for d in opponent.don_pool)

    modes = []
    if char_targets:
        modes.append({"id": "chars2", "label": "Rest up to 2 Characters", "description": f"{len(char_targets)} targets"})
    if char_targets and has_active_don:
        modes.append({"id": "char1don1", "label": "Rest 1 Character + 1 DON!!", "description": "Rest 1 of each"})
    if has_active_don:
        modes.append({"id": "don2", "label": "Rest up to 2 DON!!", "description": "Rest up to 2 active DON from opponent"})

    if not modes:
        return True

    def callback(selected):
        mode = selected[0] if selected else None
        opp = get_opponent(game_state, player)
        if mode == "chars2":
            targets = list(opp.cards_in_play)
            if targets:
                create_rest_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose up to 2 opponent's Characters to rest",
                                   max_selections=2, min_selections=0)
        elif mode == "char1don1":
            _opponent_rest_active_don(opp, 1)
            targets = list(opp.cards_in_play)
            if targets:
                create_rest_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose 1 opponent's Character to rest",
                                   max_selections=1, min_selections=0)
        elif mode == "don2":
            _opponent_rest_active_don(opp, 2)
            game_state._log(f"{opp.name}'s DON!! rested")

    return create_mode_choice(game_state, player, modes, source_card=card, callback=callback,
                              prompt="Choose which to rest (up to 2 total)")


# --- OP06-036: Ryuma ---
@register_effect("OP06-036", "on_play", "[On Play] K.O. opponent's rested cost 4 or less")
def op06_036_ryuma_play(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if c.is_resting and (getattr(c, "cost", 0) or 0) <= 4]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                                prompt="Choose opponent's rested cost 4 or less Character to K.O.")
    return True


@register_effect("OP06-036", "on_ko", "[On K.O.] K.O. opponent's rested cost 4 or less")
def op06_036_ryuma_ko(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if c.is_resting and (getattr(c, "cost", 0) or 0) <= 4]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                                prompt="Choose opponent's rested cost 4 or less Character to K.O.")
    return True


# --- OP06-037: Wadatsumi ---
# No effect (vanilla 8000 power)


# --- OP06-043: Aramaki ---
@register_effect("OP06-043", "blocker", "[Blocker]")
def op06_043_aramaki_blocker(game_state, player, card):
    card.has_blocker = True
    return True


@register_effect("OP06-043", "activate", "[Activate: Main] [Once Per Turn] Trash 1, place opponent cost 2 or less at bottom: +3000 power")
def op06_043_aramaki_activate(game_state, player, card):
    if getattr(card, "op06_043_used", False):
        return False
    if not player.hand:
        return False

    def after_discard(trashed):
        if not trashed:
            return
        opponent = get_opponent(game_state, player)
        targets = [c for c in player.cards_in_play + opponent.cards_in_play
                   if c is not card and (getattr(c, "cost", 0) or 0) <= 2]

        def after_bottom(selected):
            if not selected:
                return
            idx = int(selected[0])
            if not (0 <= idx < len(targets)):
                return
            target = targets[idx]
            owner = _owner_of_card(game_state, target)
            if owner and target in owner.cards_in_play:
                owner.cards_in_play.remove(target)
                owner.deck.append(target)
                game_state._log(f"{target.name} was placed at the bottom of {owner.name}'s deck")
            else:
                return
            card.power_modifier = getattr(card, "power_modifier", 0) + 3000
            card._sticky_power_modifier = getattr(card, "_sticky_power_modifier", 0) + 3000
            card.power_modifier_expires_on_turn = game_state.turn_count
            card._sticky_power_modifier_expires_on_turn = game_state.turn_count
            game_state._log(f"{card.name} gets +3000 power this turn")

        if targets:
            create_bottom_deck_choice(game_state, player, targets, source_card=card,
                                      prompt="Choose Character with cost 2 or less to place at bottom of deck",
                                      callback=after_bottom)

    card.op06_043_used = True
    return _trash_from_hand_choice(
        game_state, player, 1, source_card=card,
        prompt="You may trash 1 card from hand for Aramaki",
        optional=True,
        on_complete=after_discard,
    )


# --- OP06-044: Gion ---
@register_effect("OP06-044", "on_opponent_event", "[Your Turn] When opponent activates Event, they place 1 card from hand at bottom of deck")
def op06_044_gion(game_state, player, card):
    """On Opponent Event: They must place 1 card from hand at bottom of deck."""
    event_player = get_opponent(game_state, player)  # The one who played the event
    if not event_player.hand:
        return True
    return _queue_bottom_from_hand(game_state, event_player, list(event_player.hand), 1, source_card=card)


# --- OP06-045: Kuzan ---
@register_effect("OP06-045", "on_play", "[On Play] Draw 2, place 2 at bottom of deck in any order")
def op06_045_kuzan(game_state, player, card):
    draw_cards(player, 2)
    if player.hand:
        return _queue_bottom_from_hand(game_state, player, list(player.hand), 2, source_card=card)
    return True


def _queue_bottom_from_hand(game_state, player, cards, count, source_card=None):
    """Prompt player to place `count` cards from hand to bottom of deck, one at a time."""
    import uuid
    from ...game_engine import PendingChoice
    source_name = source_card.name if source_card else ""
    source_id = source_card.id if source_card else ""
    exact_count = min(count, len(cards))
    if exact_count <= 0:
        return True

    def queue_next(remaining, ordered):
        if len(ordered) >= exact_count or not remaining:
            for chosen in ordered:
                if chosen in player.hand:
                    player.hand.remove(chosen)
                player.deck.append(chosen)
                game_state._log(f"{chosen.name} placed at the bottom of deck")
            return
        snapshot = list(remaining)
        options = [{"id": str(i), "label": f"{c.name} (Cost: {getattr(c,'cost',0) or 0})",
                    "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]
        def choose_cb(selected):
            idx = int(selected[0]) if selected else -1
            if 0 <= idx < len(snapshot):
                chosen = snapshot.pop(idx)
                queue_next(snapshot, ordered + [chosen])
        game_state.pending_choice = PendingChoice(
            choice_id=f"op06_bottom_{uuid.uuid4().hex[:8]}",
            choice_type="select_target",
            prompt=f"{source_name}: Choose card {len(ordered)+1} of {exact_count} to place at deck bottom",
            options=options, min_selections=1, max_selections=1,
            source_card_id=source_id, source_card_name=source_name, callback=choose_cb,
        )
    queue_next(list(cards), [])
    return True


# --- OP06-046: Sakazuki ---
@register_effect("OP06-046", "on_play", "[On Play] Place opponent's cost 2 or less Character at bottom of deck")
def op06_046_sakazuki(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in player.cards_in_play + opponent.cards_in_play
               if c is not card and (getattr(c, "cost", 0) or 0) <= 2]
    if targets:
        return create_bottom_deck_choice(game_state, player, targets, source_card=card,
                                         prompt="Choose Character with cost 2 or less to place at bottom of deck",
                                         min_selections=0)
    return True


# --- OP06-047: Charlotte Pudding ---
@register_effect("OP06-047", "on_play", "[On Play] Opponent returns hand to deck, shuffles, draws 5")
def op06_047_charlotte_pudding(game_state, player, card):
    opponent = get_opponent(game_state, player)
    while opponent.hand:
        opponent.deck.append(opponent.hand.pop())
    random.shuffle(opponent.deck)
    draw_cards(opponent, 5)
    return True


# --- OP06-048: Zeff ---
@register_effect("OP06-048", "on_opponent_event", "[Your Turn] When opponent activates Event, if East Blue Leader, may trash 4 from deck")
def op06_048_zeff(game_state, player, card):
    """On Opponent Event: If East Blue leader, may trash 4 cards from top of deck."""
    if not (player.leader and "East Blue" in (getattr(player.leader, "card_origin", "") or "")):
        return False
    if len(player.deck) < 4:
        return True

    modes = [
        {"id": "yes", "label": "Trash 4 cards from top of your deck"},
        {"id": "no", "label": "Do not use this effect"},
    ]

    def after_choice(selected):
        if not selected or selected[0] != "yes":
            return
        trashed = []
        for _ in range(4):
            if player.deck:
                trashed.append(player.deck.pop(0))
        for c in trashed:
            player.trash.append(c)
        game_state._log(f"{player.name} trashed {len(trashed)} cards from top of deck (Zeff)")

    return create_mode_choice(
        game_state, player, modes, source_card=card,
        callback=after_choice,
        prompt="[Zeff] Opponent used an Event — trash 4 cards from top of deck?",
    )


# --- OP06-049: Sengoku ---
# No effect (vanilla 7000 power)


# --- OP06-050: Tashigi ---
@register_effect("OP06-050", "on_play", "[On Play] Look at 5, reveal up to 1 Navy card (not Tashigi) to hand")
def op06_050_tashigi(game_state, player, card):
    return search_top_cards(
        game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: ("Navy" in (getattr(c, "card_origin", "") or "")
                             and getattr(c, "name", "") != "Tashigi"),
        source_card=card,
        prompt="Look at top 5: choose up to 1 Navy card (not Tashigi) to add to hand",
    )


# --- OP06-051: Tsuru ---
@register_effect("OP06-051", "on_play", "[On Play] Trash 2 from hand: Opponent returns 1 Character to hand")
def op06_051_tsuru(game_state, player, card):
    if len(player.hand) < 2:
        return True

    def after_discard(trashed):
        if len(trashed) < 2:
            return
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            create_return_to_hand_choice(
                game_state, player, list(opponent.cards_in_play), source_card=card,
                prompt="Choose up to 1 opponent's Character to return to their hand",
                optional=True,
            )

    return _trash_from_hand_choice(
        game_state, player, 2, source_card=card,
        prompt="You may trash 2 cards from hand for Tsuru",
        optional=True,
        on_complete=after_discard,
    )


# --- OP06-052: Tokikake ---
@register_effect("OP06-052", "continuous", "[DON!! x1] If 4 or less in hand, cannot be K.O.'d in battle")
def op06_052_tokikake(game_state, player, card):
    if getattr(card, "attached_don", 0) >= 1 and len(player.hand) <= 4:
        card.cannot_be_ko_in_battle = True
    return True


# --- OP06-053: Jaguar.D.Saul ---
@register_effect("OP06-053", "on_ko", "[On K.O.] Place opponent's cost 2 or less at bottom of deck")
def op06_053_jaguar_saul(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in player.cards_in_play + opponent.cards_in_play
               if (getattr(c, "cost", 0) or 0) <= 2]
    if targets:
        return create_bottom_deck_choice(game_state, player, targets, source_card=card,
                                         prompt="Choose Character with cost 2 or less to place at bottom of deck",
                                         min_selections=0)
    return True


# --- OP06-054: Borsalino ---
@register_effect("OP06-054", "continuous", "If 5 or less in hand, gains [Blocker]")
def op06_054_borsalino(game_state, player, card):
    card._continuous_blocker = True  # Reset on each recalc cycle
    has_blocker = len(player.hand) <= 5
    card.has_blocker = has_blocker
    card.is_blocker = has_blocker
    return True


# --- OP06-055: Monkey.D.Garp ---
@register_effect("OP06-055", "on_attack", "[DON!! x2] [When Attacking] If 4 or less in hand, opponent cannot use Blocker")
def op06_055_garp(game_state, player, card):
    if getattr(card, "attached_don", 0) >= 2 and len(player.hand) <= 4:
        opponent = get_opponent(game_state, player)
        for c in opponent.cards_in_play:
            c.blocker_disabled = True
        game_state._log("Opponent cannot activate Blocker during this battle")
    return True


# =============================================================================
# EVENTS (OP06-017 through OP06-041)
# =============================================================================

# --- OP06-017: Meteor-Strike of Love ---
@register_effect("OP06-017", "on_play", "[Main]/[Counter] Add 1 Life to hand: Leader/Character +3000 power")
def op06_017_meteor_love(game_state, player, card):
    targets = _own_leader_and_chars(player)
    if not targets or not player.life_cards:
        return True

    modes = [
        {"id": "pay", "label": "Add 1 Life card to hand"},
        {"id": "skip", "label": "Do not use this effect"},
    ]

    def after_choice(selected):
        if not selected or selected[0] != "pay":
            return
        if player.life_cards:
            taken = player.life_cards.pop(0)
            player.hand.append(taken)
            game_state._log(f"{player.name} added a Life card to hand")
        create_power_effect_choice(
            game_state, player, targets, 3000,
            source_card=card,
            prompt="Choose up to 1 of your Leader or Character to give +3000 power",
            min_selections=0,
        )

    return create_mode_choice(
        game_state, player, modes, source_card=card,
        callback=after_choice,
        prompt="You may add 1 Life card to hand for Meteor-Strike of Love",
    )


@register_effect("OP06-017", "counter", "[Counter] Add 1 Life to hand: Leader/Character +3000 power")
def op06_017_meteor_love_counter(game_state, player, card):
    return op06_017_meteor_love(game_state, player, card)


# --- OP06-018: Gum-Gum King Kong Gatling ---
@register_effect("OP06-018", "on_play", "[Main] Leader/Character +3000; if opponent has 7000+ power char, +1000 more")
def op06_018_king_kong(game_state, player, card):
    opponent = get_opponent(game_state, player)
    opp_has_big = any((getattr(c, "power", 0) or 0) + (getattr(c, "power_modifier", 0) or 0) >= 7000
                      for c in opponent.cards_in_play)
    targets = _own_leader_and_chars(player)
    amount = 4000 if opp_has_big else 3000
    return create_power_effect_choice(
        game_state, player, targets, amount,
        source_card=card,
        prompt=f"Choose your Leader or Character to give +{amount} power",
        min_selections=0,
    )


@register_effect("OP06-018", "trigger", "[Trigger] K.O. opponent Character 5000 power or less")
def op06_018_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if (getattr(c, "power", 0) or 0) + (getattr(c, "power_modifier", 0) or 0) <= 5000]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                                prompt="[Trigger] K.O. opponent Character with 5000 power or less")
    return True


# --- OP06-019: Blue Dragon Seal Water Stream ---
@register_effect("OP06-019", "on_play", "[Main] K.O. opponent Character 5000 power or less")
def op06_019_water_stream(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if (getattr(c, "power", 0) or 0) + (getattr(c, "power_modifier", 0) or 0) <= 5000]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                                prompt="K.O. opponent Character with 5000 power or less")
    return True


@register_effect("OP06-019", "trigger", "[Trigger] K.O. opponent Character 4000 power or less")
def op06_019_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if (getattr(c, "power", 0) or 0) + (getattr(c, "power_modifier", 0) or 0) <= 4000]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                                prompt="[Trigger] K.O. opponent Character with 4000 power or less")
    return True


# --- OP06-038: The Billion-fold World Trichiliocosm ---
@register_effect("OP06-038", "counter", "[Counter] +2000; if 8+ rested cards +2000 more")
def op06_038_trichiliocosm(game_state, player, card):
    rested_count = sum(1 for c in player.cards_in_play if c.is_resting)
    if player.leader and player.leader.is_resting:
        rested_count += 1
    rested_don = player.don_pool.count("rested")
    total_rested = rested_count + rested_don
    amount = 4000 if total_rested >= 8 else 2000
    targets = _own_leader_and_chars(player)
    if not targets:
        return True
    snap = list(targets)

    def apply_battle_power(selected):
        for sel in selected:
            idx = int(sel)
            if 0 <= idx < len(snap):
                _add_battle_power(game_state, snap[idx], amount)

    return create_power_effect_choice(
        game_state, player, targets, amount,
        source_card=card,
        prompt=f"Choose your Leader or Character to give +{amount} power during this battle",
        min_selections=0,
        callback=apply_battle_power,
    )


@register_effect("OP06-038", "trigger", "[Trigger] K.O. rested opponent Character cost 3 or less")
def op06_038_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if c.is_resting and (getattr(c, "cost", 0) or 0) <= 3]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                                prompt="[Trigger] K.O. opponent rested Character cost 3 or less")
    return True


# --- OP06-039: You Ain't Even Worth Killing Time!! ---
@register_effect("OP06-039", "on_play", "[Main] Choose: rest cost 6 or less OR K.O. rested cost 6 or less")
def op06_039_not_worth(game_state, player, card):
    opponent = get_opponent(game_state, player)
    rest_targets = [c for c in opponent.cards_in_play if not c.is_resting and (getattr(c, "cost", 0) or 0) <= 6]
    ko_targets = [c for c in opponent.cards_in_play if c.is_resting and (getattr(c, "cost", 0) or 0) <= 6]
    modes = []
    if rest_targets:
        modes.append({"id": "rest", "label": "Rest opponent cost 6 or less Character",
                      "description": f"{len(rest_targets)} targets"})
    if ko_targets:
        modes.append({"id": "ko", "label": "K.O. opponent rested cost 6 or less Character",
                      "description": f"{len(ko_targets)} targets"})
    if not modes:
        return True

    def callback(selected):
        mode = selected[0] if selected else None
        opp = get_opponent(game_state, player)
        if mode == "rest":
            t = [c for c in opp.cards_in_play if not c.is_resting and (getattr(c, "cost", 0) or 0) <= 6]
            if t:
                create_rest_choice(game_state, player, t, source_card=card,
                                   prompt="Choose opponent cost 6 or less Character to rest")
        elif mode == "ko":
            t = [c for c in opp.cards_in_play if c.is_resting and (getattr(c, "cost", 0) or 0) <= 6]
            if t:
                create_ko_choice(game_state, player, t, source_card=card,
                                 prompt="K.O. opponent rested cost 6 or less Character")

    return create_mode_choice(game_state, player, modes, source_card=card, callback=callback,
                              prompt="Choose one effect")


@register_effect("OP06-039", "trigger", "[Trigger] Activate this card Main effect")
def op06_039_trigger(game_state, player, card):
    return op06_039_not_worth(game_state, player, card)


# --- OP06-040: Shark Arrows ---
@register_effect("OP06-040", "on_play", "[Main] K.O. up to 2 rested opponent Characters cost 3 or less")
def op06_040_shark_arrows(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if c.is_resting and (getattr(c, "cost", 0) or 0) <= 3]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                                prompt="K.O. up to 2 rested opponent Characters cost 3 or less",
                                max_selections=2, min_selections=0)
    return True


@register_effect("OP06-040", "trigger", "[Trigger] Activate this card Main effect")
def op06_040_trigger(game_state, player, card):
    return op06_040_shark_arrows(game_state, player, card)


# --- OP06-041: The Ark Noah (STAGE) ---
@register_effect("OP06-041", "on_play", "[On Play] Rest all opponent Characters")
def op06_041_ark_noah_play(game_state, player, card):
    opponent = get_opponent(game_state, player)
    for c in opponent.cards_in_play:
        c.is_resting = True
    game_state._log("All opponent Characters are rested")
    return True


@register_effect("OP06-041", "trigger", "[Trigger] Play this card")
def op06_041_ark_noah_trigger(game_state, player, card):
    card.is_resting = False
    player.cards_in_play.append(card)
    game_state._apply_keywords(card)
    game_state._log(f"{player.name} played {card.name} from Trigger")
    # Fire on-play effect: rest all opponent characters
    return op06_041_ark_noah_play(game_state, player, card)


# =============================================================================
# CHARACTERS OP06-060 through OP06-079
# =============================================================================

# --- OP06-056: Ama no Murakumo Sword (Event) ---
@register_effect("OP06-056", "on_play", "[Main] Place up to 1 opp cost 2 or less AND up to 1 opp cost 1 or less at bottom of deck")
def op06_056_murakumo(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets_2 = [c for c in opponent.cards_in_play if (getattr(c, "cost", 0) or 0) <= 2]
    targets_1 = [c for c in opponent.cards_in_play if (getattr(c, "cost", 0) or 0) <= 1]
    # First pick cost <=2, then cost <=1 (different card)
    if not targets_2 and not targets_1:
        return True

    picked = []

    def second_pick():
        from ...game_engine import PendingChoice
        import uuid
        remaining = [c for c in get_opponent(game_state, player).cards_in_play
                     if (getattr(c, "cost", 0) or 0) <= 1 and c not in picked]
        if not remaining:
            return

        def do_second(selected2):
            if selected2:
                idx2 = int(selected2[0])
                if 0 <= idx2 < len(remaining):
                    t = remaining[idx2]
                    opp = get_opponent(game_state, player)
                    if t in opp.cards_in_play:
                        opp.cards_in_play.remove(t)
                        opp.deck.append(t)
                        game_state._log(f"{t.name} placed at bottom of deck")

        opts = [{"id": str(i), "label": f"{c.name} (Cost:{c.cost or 0})",
                 "card_id": c.id, "card_name": c.name} for i, c in enumerate(remaining)]
        game_state.pending_choice = PendingChoice(
            choice_id=f"op06_056b_{uuid.uuid4().hex[:6]}",
            choice_type="select_cards",
            prompt="Choose up to 1 opponent cost 1 or less Character to place at bottom of deck (skip if none)",
            options=opts, min_selections=0, max_selections=1,
            source_card_id=card.id, source_card_name=card.name,
            callback=do_second,
        )

    if targets_2:
        snap2 = list(targets_2)

        def first_pick(selected):
            if selected:
                idx = int(selected[0])
                if 0 <= idx < len(snap2):
                    t = snap2[idx]
                    opp = get_opponent(game_state, player)
                    if t in opp.cards_in_play:
                        opp.cards_in_play.remove(t)
                        opp.deck.append(t)
                        picked.append(t)
                        game_state._log(f"{t.name} placed at bottom of deck")
            second_pick()

        return create_bottom_deck_choice(game_state, player, snap2, source_card=card,
                                         prompt="Choose opponent cost 2 or less Character to place at bottom of deck",
                                         min_selections=0,
                                         callback=first_pick)
    else:
        second_pick()
        return True


@register_effect("OP06-056", "trigger", "[Trigger] Activate this card Main effect")
def op06_056_trigger(game_state, player, card):
    return op06_056_murakumo(game_state, player, card)


# --- OP06-057: But I Will Never Doubt a Woman's Tears!!!! (Event) ---
@register_effect("OP06-057", "on_play", "[Main] +1000 own, reveal top 1, play cost 2 char, place rest top/bottom")
def op06_057_tears(game_state, player, card):
    targets = _own_leader_and_chars(player)

    snap_targets = list(_own_leader_and_chars(player))

    def after_power(selected):
        # Apply +1000 to the chosen target
        for sel in selected:
            idx = int(sel)
            if 0 <= idx < len(snap_targets):
                snap_targets[idx].power_modifier = getattr(snap_targets[idx], "power_modifier", 0) + 1000
                snap_targets[idx]._sticky_power_modifier = getattr(snap_targets[idx], "_sticky_power_modifier", 0) + 1000
                game_state._log(f"{snap_targets[idx].name} gets +1000 power")
        if not player.deck:
            return
        search_top_cards(
            game_state, player, 1, add_count=1,
            filter_fn=lambda c: c.card_type == "CHARACTER" and (getattr(c, "cost", 0) or 0) == 2,
            source_card=card,
            play_to_field=True,
            prompt="Reveal top 1 card: if cost 2 Character, play it; otherwise place at top/bottom",
        )

    if targets:
        return create_power_effect_choice(
            game_state, player, targets, 1000,
            source_card=card,
            prompt="Choose your Leader or Character to give +1000 power",
            min_selections=0,
            callback=after_power,
        )
    else:
        if player.deck:
            return search_top_cards(
                game_state, player, 1, add_count=1,
                filter_fn=lambda c: c.card_type == "CHARACTER" and (getattr(c, "cost", 0) or 0) == 2,
                source_card=card,
                play_to_field=True,
                prompt="Reveal top 1 card: play cost 2 Character or place at top/bottom",
            )
    return True


@register_effect("OP06-057", "trigger", "[Trigger] Play cost 2 Character from hand")
def op06_057_trigger(game_state, player, card):
    targets = [c for c in player.hand if c.card_type == "CHARACTER" and (getattr(c, "cost", 0) or 0) == 2]
    if targets:
        return create_play_from_hand_choice(game_state, player, targets, source_card=card,
                                             prompt="[Trigger] Play a cost 2 Character from hand")
    return True


# --- OP06-058: Gravity Blade Raging Tiger (Event) ---
@register_effect("OP06-058", "on_play", "[Main] Place up to 2 Characters cost 6 or less at bottom of deck")
def op06_058_gravity_blade(game_state, player, card):
    opponent = get_opponent(game_state, player)
    own = [c for c in player.cards_in_play if (getattr(c, "cost", 0) or 0) <= 6]
    opp = [c for c in opponent.cards_in_play if (getattr(c, "cost", 0) or 0) <= 6]
    targets = own + opp
    if targets:
        return _queue_bottom_deck_choice(
            game_state, player, targets, source_card=card,
            prompt="Choose up to 2 Characters with cost 6 or less to place at bottom of deck",
            max_selections=2, min_selections=0,
        )
    return True


@register_effect("OP06-058", "trigger", "[Trigger] Place up to 1 Character cost 5 or less at bottom of deck")
def op06_058_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    own = [c for c in player.cards_in_play if (getattr(c, "cost", 0) or 0) <= 5]
    opp = [c for c in opponent.cards_in_play if (getattr(c, "cost", 0) or 0) <= 5]
    targets = own + opp
    if targets:
        return _queue_bottom_deck_choice(
            game_state, player, targets, source_card=card,
            prompt="[Trigger] Place up to 1 Character cost 5 or less at bottom of deck",
            max_selections=1, min_selections=0,
        )
    return True


# --- OP06-059: White Snake (Event) ---
@register_effect("OP06-059", "counter", "[Counter] Leader/Character +1000 power and draw 1 card")
def op06_059_white_snake(game_state, player, card):
    draw_cards(player, 1)
    targets = _own_leader_and_chars(player)
    if targets:
        return create_power_effect_choice(
            game_state, player, targets, 1000,
            source_card=card,
            prompt="Choose your Leader or Character to give +1000 power during this battle",
            min_selections=0,
        )
    return True


@register_effect("OP06-059", "trigger", "[Trigger] Look at 5 top cards and place at top or bottom in any order")
def op06_059_trigger(game_state, player, card):
    if player.deck:
        return reorder_top_cards(game_state, player, 5, source_card=card, allow_top=True)
    return True


# --- OP06-060: Vinsmoke Ichiji (cost 4) ---
@register_effect("OP06-060", "activate", "[Activate: Main] DON!! -1, trash self: if GERMA 66 leader, play Ichiji cost 7 from hand/trash")
def op06_060_ichiji_4(game_state, player, card):
    if _free_don_count(player) < 1:
        return False
    leader_type = getattr(player.leader, "card_origin", "") or "" if player.leader else ""
    if "GERMA 66" not in leader_type:
        return False

    def resolve_effect():
        if card in player.cards_in_play:
            player.cards_in_play.remove(card)
            player.trash.append(card)
            game_state._log(f"{player.name} trashed {card.name}")
        targets = [c for c in player.hand + player.trash
                   if c.name == "Vinsmoke Ichiji" and (getattr(c, "cost", 0) or 0) == 7]
        if not targets:
            return
        snap = list(targets)
        opts = [{"id": str(i), "label": f"{c.name} (Cost:{c.cost or 0}) from {'hand' if c in player.hand else 'trash'}",
                 "card_id": c.id, "card_name": c.name} for i, c in enumerate(snap)]

        def do_play(selected):
            if not selected:
                return
            idx = int(selected[0])
            if 0 <= idx < len(snap):
                t = snap[idx]
                for zone in (player.hand, player.trash):
                    if t in zone:
                        zone.remove(t)
                        break
                t.is_resting = False
                player.cards_in_play.append(t)
                game_state._log(f"{player.name} played {t.name} from hand/trash")

        from ...game_engine import PendingChoice
        import uuid
        game_state.pending_choice = PendingChoice(
            choice_id=f"op06_060_{uuid.uuid4().hex[:6]}",
            choice_type="select_cards",
            prompt="Play Vinsmoke Ichiji cost 7 from hand or trash",
            options=opts, min_selections=0, max_selections=1,
            source_card_id=card.id, source_card_name=card.name,
            callback=do_play,
        )

    returned = return_don_to_deck(game_state, player, 1, source_card=card, post_callback=resolve_effect)
    if game_state.pending_choice is not None:
        return True
    if returned:
        resolve_effect()
    return True


# --- OP06-061: Vinsmoke Ichiji (cost 7) ---
@register_effect("OP06-061", "on_play", "[On Play] If own DON <= opp DON: give opp char -2000 power, this gains Rush")
def op06_061_ichiji_7(game_state, player, card):
    own_don = len(player.don_pool)
    opp_don = len(get_opponent(game_state, player).don_pool)
    if own_don > opp_don:
        return True
    card.has_rush = True
    card.is_rush = True
    card._temporary_rush_until_turn = game_state.turn_count  # Persists through _recalc this turn
    game_state._log(f"{card.name} gains [Rush]")
    opponent = get_opponent(game_state, player)
    targets = list(opponent.cards_in_play)
    if targets:
        return create_power_effect_choice(
            game_state, player, targets, -2000,
            source_card=card,
            prompt="Choose opponent's Character to give -2000 power",
            min_selections=0,
        )
    return True


# --- OP06-062: Vinsmoke Judge ---
@register_effect("OP06-062", "on_play", "[On Play] DON!! -1, trash 2 from hand: play up to 4 GERMA 66 cost 4000 or less from trash")
def op06_062_judge_play(game_state, player, card):
    if _free_don_count(player) < 1 or len(player.hand) < 2:
        return True

    def after_don_return():
        if len(player.hand) < 2:
            return
        hand_snap = list(player.hand)
        opts = [{"id": str(i), "label": c.name, "card_id": c.id, "card_name": c.name}
                for i, c in enumerate(hand_snap)]

        def after_discard(selected):
            for idx_str in selected:
                idx = int(idx_str)
                if 0 <= idx < len(hand_snap):
                    c = hand_snap[idx]
                    if c in player.hand:
                        player.hand.remove(c)
                        player.trash.append(c)
            game_state._log(f"{player.name} trashed 2 cards from hand")
            targets = [c for c in player.trash
                       if c.card_type == "CHARACTER"
                       and "GERMA 66" in (getattr(c, "card_origin", "") or "")
                       and (getattr(c, "power", 0) or 0) <= 4000]
            seen_names = set()
            unique = []
            for c in targets:
                if c.name not in seen_names:
                    seen_names.add(c.name)
                    unique.append(c)
            if unique:
                snap = list(unique)
                play_opts = [{"id": str(i), "label": f"{c.name} (Cost:{c.cost or 0})",
                              "card_id": c.id, "card_name": c.name} for i, c in enumerate(snap)]

                def do_play(selected2):
                    for idx_str in selected2:
                        idx = int(idx_str)
                        if 0 <= idx < len(snap):
                            t = snap[idx]
                            if t in player.trash:
                                player.trash.remove(t)
                                t.is_resting = False
                                player.cards_in_play.append(t)
                                game_state._log(f"{player.name} played {t.name} from trash (Judge)")

                from ...game_engine import PendingChoice
                import uuid
                game_state.pending_choice = PendingChoice(
                    choice_id=f"op06_062p_{uuid.uuid4().hex[:6]}",
                    choice_type="select_cards",
                    prompt="Play up to 4 GERMA 66 Characters with 4000 power or less from trash (different names)",
                    options=play_opts, min_selections=0, max_selections=4,
                    source_card_id=card.id, source_card_name=card.name,
                    callback=do_play,
                )

        from ...game_engine import PendingChoice
        import uuid
        game_state.pending_choice = PendingChoice(
            choice_id=f"op06_062d_{uuid.uuid4().hex[:6]}",
            choice_type="select_cards",
            prompt="Trash 2 cards from hand for Judge's effect",
            options=opts, min_selections=2, max_selections=2,
            source_card_id=card.id, source_card_name=card.name,
            callback=after_discard,
        )

    returned = return_don_to_deck(game_state, player, 1, source_card=card, post_callback=after_don_return)
    if game_state.pending_choice is not None:
        return True
    if returned:
        after_don_return()
    return True


@register_effect("OP06-062", "activate", "[Activate: Main] [Once Per Turn] DON!! -1: Rest 1 opponent DON!!")
def op06_062_judge_activate(game_state, player, card):
    if getattr(card, "op06_062_used", False):
        return False
    if _free_don_count(player) < 1:
        return False
    card.op06_062_used = True

    def after_don():
        opponent = get_opponent(game_state, player)
        if any(d == "active" for d in opponent.don_pool):
            _opponent_rest_active_don(opponent, 1)
            game_state._log(f"{opponent.name} DON!! rested")

    returned = return_don_to_deck(game_state, player, 1, source_card=card, post_callback=after_don)
    if game_state.pending_choice is not None:
        return True
    if returned:
        after_don()
    return True


# --- OP06-063: Vinsmoke Sora ---
@register_effect("OP06-063", "on_play", "[On Play] Trash 1 from hand: if own DON <= opp DON, add Vinsmoke Family <=4000 from trash to hand")
def op06_063_sora(game_state, player, card):
    if not player.hand:
        return True
    own_don = len(player.don_pool)
    opp_don = len(get_opponent(game_state, player).don_pool)
    if own_don > opp_don:
        return True
    trash_targets = [c for c in player.trash
                     if c.card_type == "CHARACTER"
                     and "The Vinsmoke Family" in (getattr(c, "card_origin", "") or "")
                     and (getattr(c, "power", 0) or 0) <= 4000]
    if not trash_targets:
        return True
    snap_trash = list(trash_targets)

    def after_discard(selected):
        if not selected:
            return
        idx = int(selected[0])
        hand_snap = list(player.hand)
        if 0 <= idx < len(hand_snap):
            c = hand_snap[idx]
            if c in player.hand:
                player.hand.remove(c)
                player.trash.append(c)
                game_state._log(f"{player.name} trashed {c.name}")
        fresh = [c for c in player.trash
                 if c.card_type == "CHARACTER"
                 and "The Vinsmoke Family" in (getattr(c, "card_origin", "") or "")
                 and (getattr(c, "power", 0) or 0) <= 4000]
        if fresh:
            create_add_from_trash_choice(game_state, player, fresh, source_card=card,
                                         prompt="Add Vinsmoke Family Character with 4000 power or less from trash to hand")

    hand_snap = list(player.hand)
    opts = [{"id": str(i), "label": c.name, "card_id": c.id, "card_name": c.name}
            for i, c in enumerate(hand_snap)]
    from ...game_engine import PendingChoice
    import uuid
    game_state.pending_choice = PendingChoice(
        choice_id=f"op06_063_{uuid.uuid4().hex[:6]}",
        choice_type="select_cards",
        prompt="Trash 1 card from hand for Sora's effect",
        options=opts, min_selections=1, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=after_discard,
    )
    return True


# --- OP06-064: Vinsmoke Niji (cost 3) ---
@register_effect("OP06-064", "activate", "[Activate: Main] DON!! -1, trash self: if GERMA 66 leader, play Niji cost 5 from hand/trash")
def op06_064_niji_3(game_state, player, card):
    if _free_don_count(player) < 1:
        return False
    leader_type = getattr(player.leader, "card_origin", "") or "" if player.leader else ""
    if "GERMA 66" not in leader_type:
        return False

    def resolve_effect():
        if card in player.cards_in_play:
            player.cards_in_play.remove(card)
            player.trash.append(card)
        targets = [c for c in player.hand + player.trash
                   if c.name == "Vinsmoke Niji" and (getattr(c, "cost", 0) or 0) == 5]
        if not targets:
            return
        snap = list(targets)
        opts = [{"id": str(i), "label": f"{c.name} (from {'hand' if c in player.hand else 'trash'})",
                 "card_id": c.id, "card_name": c.name} for i, c in enumerate(snap)]

        def do_play(selected):
            if not selected:
                return
            idx = int(selected[0])
            if 0 <= idx < len(snap):
                t = snap[idx]
                for zone in (player.hand, player.trash):
                    if t in zone:
                        zone.remove(t)
                        break
                t.is_resting = False
                player.cards_in_play.append(t)
                game_state._log(f"{player.name} played {t.name} from hand/trash")

        from ...game_engine import PendingChoice
        import uuid
        game_state.pending_choice = PendingChoice(
            choice_id=f"op06_064_{uuid.uuid4().hex[:6]}",
            choice_type="select_cards",
            prompt="Play Vinsmoke Niji cost 5 from hand or trash",
            options=opts, min_selections=0, max_selections=1,
            source_card_id=card.id, source_card_name=card.name,
            callback=do_play,
        )

    returned = return_don_to_deck(game_state, player, 1, source_card=card, post_callback=resolve_effect)
    if game_state.pending_choice is not None:
        return True
    if returned:
        resolve_effect()
    return True


# --- OP06-065: Vinsmoke Niji (cost 5) ---
@register_effect("OP06-065", "on_play", "[On Play] If own DON <= opp DON: choose KO <=2 cost OR return <=4 cost to hand")
def op06_065_niji_5(game_state, player, card):
    own_don = len(player.don_pool)
    opp_don = len(get_opponent(game_state, player).don_pool)
    if own_don > opp_don:
        return True
    opponent = get_opponent(game_state, player)
    ko_targets = [c for c in opponent.cards_in_play if (getattr(c, "cost", 0) or 0) <= 2]
    rth_targets = [c for c in opponent.cards_in_play if (getattr(c, "cost", 0) or 0) <= 4]
    modes = []
    if ko_targets:
        modes.append({"id": "ko", "label": "K.O. opponent cost 2 or less Character",
                      "description": f"{len(ko_targets)} targets"})
    if rth_targets:
        modes.append({"id": "rth", "label": "Return opponent cost 4 or less Character to hand",
                      "description": f"{len(rth_targets)} targets"})
    if not modes:
        return True

    def callback(selected):
        mode = selected[0] if selected else None
        opp = get_opponent(game_state, player)
        if mode == "ko":
            t = [c for c in opp.cards_in_play if (getattr(c, "cost", 0) or 0) <= 2]
            if t:
                create_ko_choice(game_state, player, t, source_card=card,
                                 prompt="K.O. opponent cost 2 or less Character")
        elif mode == "rth":
            t = [c for c in opp.cards_in_play if (getattr(c, "cost", 0) or 0) <= 4]
            if t:
                create_return_to_hand_choice(game_state, player, t, source_card=card,
                                             prompt="Return opponent cost 4 or less Character to hand")

    return create_mode_choice(game_state, player, modes, source_card=card, callback=callback,
                              prompt="Choose one effect (Niji)")


# --- OP06-066: Vinsmoke Yonji (cost 2) ---
@register_effect("OP06-066", "activate", "[Activate: Main] DON!! -1, trash self: if GERMA 66 leader, play Yonji cost 4 from hand/trash")
def op06_066_yonji_2(game_state, player, card):
    if _free_don_count(player) < 1:
        return False
    leader_type = getattr(player.leader, "card_origin", "") or "" if player.leader else ""
    if "GERMA 66" not in leader_type:
        return False

    def resolve_effect():
        if card in player.cards_in_play:
            player.cards_in_play.remove(card)
            player.trash.append(card)
        targets = [c for c in player.hand + player.trash
                   if c.name == "Vinsmoke Yonji" and (getattr(c, "cost", 0) or 0) == 4]
        if not targets:
            return
        snap = list(targets)
        opts = [{"id": str(i), "label": f"{c.name} (from {'hand' if c in player.hand else 'trash'})",
                 "card_id": c.id, "card_name": c.name} for i, c in enumerate(snap)]

        def do_play(selected):
            if not selected:
                return
            idx = int(selected[0])
            if 0 <= idx < len(snap):
                t = snap[idx]
                for zone in (player.hand, player.trash):
                    if t in zone:
                        zone.remove(t)
                        break
                t.is_resting = False
                player.cards_in_play.append(t)
                game_state._log(f"{player.name} played {t.name} from hand/trash")

        from ...game_engine import PendingChoice
        import uuid
        game_state.pending_choice = PendingChoice(
            choice_id=f"op06_066_{uuid.uuid4().hex[:6]}",
            choice_type="select_cards",
            prompt="Play Vinsmoke Yonji cost 4 from hand or trash",
            options=opts, min_selections=0, max_selections=1,
            source_card_id=card.id, source_card_name=card.name,
            callback=do_play,
        )

    returned = return_don_to_deck(game_state, player, 1, source_card=card, post_callback=resolve_effect)
    if game_state.pending_choice is not None:
        return True
    if returned:
        resolve_effect()
    return True


# --- OP06-067: Vinsmoke Yonji (cost 4) ---
@register_effect("OP06-067", "continuous", "[Continuous] If own DON <= opp DON, +1000 power. [Blocker]")
def op06_067_yonji_4(game_state, player, card):
    own_don = len(player.don_pool)
    opp_don = len(get_opponent(game_state, player).don_pool)
    if own_don <= opp_don:
        card.power_modifier = getattr(card, "power_modifier", 0) + 1000
    card.has_blocker = True
    return True


# --- OP06-068: Vinsmoke Reiju (cost 2) ---
@register_effect("OP06-068", "activate", "[Activate: Main] DON!! -1, trash self: if GERMA 66 leader, play Reiju cost 4 from hand/trash")
def op06_068_reiju_2(game_state, player, card):
    if _free_don_count(player) < 1:
        return False
    leader_type = getattr(player.leader, "card_origin", "") or "" if player.leader else ""
    if "GERMA 66" not in leader_type:
        return False

    def resolve_effect():
        if card in player.cards_in_play:
            player.cards_in_play.remove(card)
            player.trash.append(card)
        targets = [c for c in player.hand + player.trash
                   if c.name == "Vinsmoke Reiju" and (getattr(c, "cost", 0) or 0) == 4]
        if not targets:
            return
        snap = list(targets)
        opts = [{"id": str(i), "label": f"{c.name} (from {'hand' if c in player.hand else 'trash'})",
                 "card_id": c.id, "card_name": c.name} for i, c in enumerate(snap)]

        def do_play(selected):
            if not selected:
                return
            idx = int(selected[0])
            if 0 <= idx < len(snap):
                t = snap[idx]
                for zone in (player.hand, player.trash):
                    if t in zone:
                        zone.remove(t)
                        break
                t.is_resting = False
                player.cards_in_play.append(t)
                game_state._log(f"{player.name} played {t.name} from hand/trash")

        from ...game_engine import PendingChoice
        import uuid
        game_state.pending_choice = PendingChoice(
            choice_id=f"op06_068_{uuid.uuid4().hex[:6]}",
            choice_type="select_cards",
            prompt="Play Vinsmoke Reiju cost 4 from hand or trash",
            options=opts, min_selections=0, max_selections=1,
            source_card_id=card.id, source_card_name=card.name,
            callback=do_play,
        )

    returned = return_don_to_deck(game_state, player, 1, source_card=card, post_callback=resolve_effect)
    if game_state.pending_choice is not None:
        return True
    if returned:
        resolve_effect()
    return True


# --- OP06-069: Vinsmoke Reiju (cost 4) ---
@register_effect("OP06-069", "on_play", "[On Play] If own DON <= opp DON and <=5 hand, draw 2")
def op06_069_reiju_4(game_state, player, card):
    own_don = len(player.don_pool)
    opp_don = len(get_opponent(game_state, player).don_pool)
    if own_don <= opp_don and len(player.hand) <= 5:
        draw_cards(player, 2)
    return True


# --- OP06-070: Eldoraggo --- (no effect)

# --- OP06-071: Gild Tesoro ---
@register_effect("OP06-071", "on_play", "[On Play] DON!! -1: if FILM leader, add 2 FILM Characters cost 4 or less from trash to hand")
def op06_071_tesoro(game_state, player, card):
    if _free_don_count(player) < 1:
        return True
    leader_type = getattr(player.leader, "card_origin", "") or "" if player.leader else ""
    if "FILM" not in leader_type:
        return True

    def after_don():
        targets = [c for c in player.trash
                   if c.card_type == "CHARACTER"
                   and "FILM" in (getattr(c, "card_origin", "") or "")
                   and (getattr(c, "cost", 0) or 0) <= 4]
        if targets:
            snap = list(targets)
            opts = [{"id": str(i), "label": f"{c.name} (Cost:{c.cost or 0})",
                     "card_id": c.id, "card_name": c.name} for i, c in enumerate(snap)]

            def do_add(selected):
                for idx_str in selected:
                    idx = int(idx_str)
                    if 0 <= idx < len(snap):
                        t = snap[idx]
                        if t in player.trash:
                            player.trash.remove(t)
                            player.hand.append(t)
                            game_state._log(f"{t.name} added to hand from trash")

            from ...game_engine import PendingChoice
            import uuid
            game_state.pending_choice = PendingChoice(
                choice_id=f"op06_071_{uuid.uuid4().hex[:6]}",
                choice_type="select_cards",
                prompt="Add up to 2 FILM Characters cost 4 or less from trash to hand",
                options=opts, min_selections=0, max_selections=2,
                source_card_id=card.id, source_card_name=card.name,
                callback=do_add,
            )

    returned = return_don_to_deck(game_state, player, 1, source_card=card, post_callback=after_don)
    if game_state.pending_choice is not None:
        return True
    if returned:
        after_don()
    return True


# --- OP06-072: Cosette ---
@register_effect("OP06-072", "continuous", "[Continuous] If GERMA 66 leader and own DON is 2+ less than opp DON, gains Blocker")
def op06_072_cosette(game_state, player, card):
    leader_type = getattr(player.leader, "card_origin", "") or "" if player.leader else ""
    if "GERMA 66" not in leader_type:
        return True
    own_don = len(player.don_pool)
    opp_don = len(get_opponent(game_state, player).don_pool)
    if opp_don - own_don >= 2:
        card.has_blocker = True
    return True


# --- OP06-073: Shiki ---
@register_effect("OP06-073", "blocker", "[Blocker]")
def op06_073_shiki_blocker(game_state, player, card):
    card.has_blocker = True
    return True


@register_effect("OP06-073", "on_play", "[On Play] If 8+ DON on field, draw 1 and trash 1 from hand")
def op06_073_shiki_play(game_state, player, card):
    if len(player.don_pool) >= 8:
        draw_cards(player, 1)
        if player.hand:
            return _trash_from_hand_choice(
                game_state, player, 1, source_card=card,
                prompt="Trash 1 card from hand (Shiki)",
            )
    return True


# --- OP06-074: Zephyr ---
@register_effect("OP06-074", "on_play", "[On Play] DON!! -1: Negate effect of opp char; if 5000 power or less, K.O. it")
def op06_074_zephyr(game_state, player, card):
    if _free_don_count(player) < 1:
        return True
    opponent = get_opponent(game_state, player)
    targets = list(opponent.cards_in_play)
    if not targets:
        return True

    def after_don():
        opp = get_opponent(game_state, player)
        t2 = list(opp.cards_in_play)
        if not t2:
            return
        snap = list(t2)
        opts = [{"id": str(i), "label": f"{c.name} (Power:{(c.power or 0) + (c.power_modifier or 0)})",
                 "card_id": c.id, "card_name": c.name} for i, c in enumerate(snap)]

        def do_negate(selected):
            if not selected:
                return
            idx = int(selected[0])
            if 0 <= idx < len(snap):
                t = snap[idx]
                t.effects_negated = True
                t.effects_negated_this_turn = True
                game_state._log(f"{t.name} effect negated")
                power = (getattr(t, "power", 0) or 0) + (getattr(t, "power_modifier", 0) or 0)
                if power <= 5000:
                    opp2 = get_opponent(game_state, player)
                    if t in opp2.cards_in_play:
                        opp2.cards_in_play.remove(t)
                        opp2.trash.append(t)
                        game_state._log(f"{t.name} K.O.'d (5000 power or less)")

        from ...game_engine import PendingChoice
        import uuid
        game_state.pending_choice = PendingChoice(
            choice_id=f"op06_074_{uuid.uuid4().hex[:6]}",
            choice_type="select_cards",
            prompt="Choose opponent's Character to negate effect (K.O. if 5000 or less power)",
            options=opts, min_selections=0, max_selections=1,
            source_card_id=card.id, source_card_name=card.name,
            callback=do_negate,
        )

    returned = return_don_to_deck(game_state, player, 1, source_card=card, post_callback=after_don)
    if game_state.pending_choice is not None:
        return True
    if returned:
        after_don()
    return True


# --- OP06-075: Count Battler ---
@register_effect("OP06-075", "on_play", "[On Play] DON!! -1: Rest up to 2 opponent Characters cost 2 or less")
def op06_075_count_battler(game_state, player, card):
    if _free_don_count(player) < 1:
        return True

    def after_don():
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if not c.is_resting and (getattr(c, "cost", 0) or 0) <= 2]
        if targets:
            create_rest_choice(game_state, player, targets, source_card=card,
                               prompt="Rest up to 2 opponent Characters cost 2 or less",
                               max_selections=2, min_selections=0)

    returned = return_don_to_deck(game_state, player, 1, source_card=card, post_callback=after_don)
    if game_state.pending_choice is not None:
        return True
    if returned:
        after_don()
    return True


# --- OP06-076: Hitokiri Kamazo ---
@register_effect("OP06-076", "on_don_return", "[Your Turn] [Once Per Turn] When DON returned: K.O. opp char cost 2 or less")
def op06_076_kamazo_don_return(game_state, player, card):
    if game_state.current_player is not player:
        return False
    if getattr(card, "op06_076_used", False):
        return False
    card.op06_076_used = True
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, "cost", 0) or 0) <= 2]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                                prompt="K.O. opponent's Character cost 2 or less (Kamazo)")
    return True


# --- OP06-077: Black Bug (Event) ---
@register_effect("OP06-077", "on_play", "[Main] If own DON <= opp DON: place opp char cost 5 or less at bottom")
def op06_077_black_bug(game_state, player, card):
    own_don = len(player.don_pool)
    opp_don = len(get_opponent(game_state, player).don_pool)
    if own_don > opp_don:
        return True
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, "cost", 0) or 0) <= 5]
    if targets:
        return create_bottom_deck_choice(game_state, player, targets, source_card=card,
                                         prompt="Place opponent's Character cost 5 or less at bottom of deck",
                                         min_selections=0)
    return True


@register_effect("OP06-077", "trigger", "[Trigger] Place opponent's Character cost 4 or less at bottom of deck")
def op06_077_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, "cost", 0) or 0) <= 4]
    if targets:
        return create_bottom_deck_choice(game_state, player, targets, source_card=card,
                                         prompt="[Trigger] Place opponent's Character cost 4 or less at bottom of deck",
                                         min_selections=0)
    return True


# --- OP06-078: GERMA 66 (Event) ---
@register_effect("OP06-078", "on_play", "[Main] Look at 5 top, reveal up to 1 GERMA type card (not GERMA 66), add to hand")
def op06_078_germa66_event(game_state, player, card):
    return search_top_cards(
        game_state, player, 5, add_count=1,
        filter_fn=lambda c: "GERMA" in (getattr(c, "card_origin", "") or "") and c.name != "GERMA 66",
        source_card=card,
        prompt="Look at top 5: reveal up to 1 GERMA type card (not GERMA 66) to add to hand",
    )


@register_effect("OP06-078", "trigger", "[Trigger] Draw 1 card")
def op06_078_trigger(game_state, player, card):
    draw_cards(player, 1)
    return True


# --- OP06-079: Kingdom of GERMA (STAGE) ---
@register_effect("OP06-079", "activate", "[Activate: Main] Trash 1 from hand, rest Stage: look at 3 top, reveal up to 1 GERMA type to hand")
def op06_079_germa_kingdom(game_state, player, card):
    if card.is_resting:
        return False
    if not player.hand:
        return False
    hand_snap = list(player.hand)
    opts = [{"id": str(i), "label": c.name, "card_id": c.id, "card_name": c.name}
            for i, c in enumerate(hand_snap)]

    def after_discard(selected):
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(hand_snap):
            c = hand_snap[idx]
            if c in player.hand:
                player.hand.remove(c)
                player.trash.append(c)
                game_state._log(f"{player.name} trashed {c.name}")
        card.is_resting = True
        search_top_cards(
            game_state, player, 3, add_count=1,
            filter_fn=lambda c2: "GERMA" in (getattr(c2, "card_origin", "") or ""),
            source_card=card,
            prompt="Look at top 3: reveal up to 1 GERMA type card to add to hand",
        )

    from ...game_engine import PendingChoice
    import uuid
    game_state.pending_choice = PendingChoice(
        choice_id=f"op06_079_{uuid.uuid4().hex[:6]}",
        choice_type="select_cards",
        prompt="Trash 1 card from hand (Kingdom of GERMA)",
        options=opts, min_selections=1, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=after_discard,
    )
    return True


# =============================================================================
# CHARACTERS OP06-081 through OP06-098
# =============================================================================

# --- OP06-081: Absalom ---
@register_effect("OP06-081", "on_play", "[On Play] Return 2 from trash to bottom: K.O. char cost 2 or less")
def op06_081_absalom(game_state, player, card):
    if len(player.trash) < 2:
        return True
    snap = list(player.trash)
    opts = [{"id": str(i), "label": c.name, "card_id": c.id, "card_name": c.name}
            for i, c in enumerate(snap)]

    def after_return(selected):
        if len(selected) < 2:
            return
        for idx_str in selected:
            idx = int(idx_str)
            if 0 <= idx < len(snap):
                c = snap[idx]
                if c in player.trash:
                    player.trash.remove(c)
                    player.deck.append(c)
                    game_state._log(f"{c.name} returned to bottom of deck")
        opponent = get_opponent(game_state, player)
        own_targets = [c for c in player.cards_in_play if (getattr(c, "cost", 0) or 0) <= 2]
        opp_targets = [c for c in opponent.cards_in_play if (getattr(c, "cost", 0) or 0) <= 2]
        targets = own_targets + opp_targets
        if targets:
            create_ko_choice(game_state, player, targets, source_card=card,
                             prompt="K.O. Character with cost 2 or less (Absalom)")

    from ...game_engine import PendingChoice
    import uuid
    game_state.pending_choice = PendingChoice(
        choice_id=f"op06_081_{uuid.uuid4().hex[:6]}",
        choice_type="select_cards",
        prompt="Choose 2 cards from trash to return to bottom of deck",
        options=opts, min_selections=2, max_selections=2,
        source_card_id=card.id, source_card_name=card.name,
        callback=after_return,
    )
    return True


# --- OP06-082: Inuppe ---
@register_effect("OP06-082", "on_play", "[On Play]/[On K.O.] If Thriller Bark leader, draw 2 and trash 2")
def op06_082_inuppe_play(game_state, player, card):
    leader_type = getattr(player.leader, "card_origin", "") or "" if player.leader else ""
    if "Thriller Bark Pirates" not in leader_type:
        return True
    draw_cards(player, 2)
    if len(player.hand) >= 2:
        return _trash_from_hand_choice(
            game_state, player, 2, source_card=card,
            prompt="Trash 2 cards from hand (Inuppe)",
        )
    return True


@register_effect("OP06-082", "on_ko", "[On Play]/[On K.O.] If Thriller Bark leader, draw 2 and trash 2")
def op06_082_inuppe_ko(game_state, player, card):
    leader_type = getattr(player.leader, "card_origin", "") or "" if player.leader else ""
    if "Thriller Bark Pirates" not in leader_type:
        return True
    draw_cards(player, 2)
    if len(player.hand) >= 2:
        return _trash_from_hand_choice(
            game_state, player, 2, source_card=card,
            prompt="Trash 2 cards from hand (Inuppe)",
        )
    return True


# --- OP06-083: Oars ---
@register_effect("OP06-083", "continuous", "[Continuous] This Character cannot attack")
def op06_083_oars_passive(game_state, player, card):
    card.cannot_attack = True
    return True


@register_effect("OP06-083", "activate", "[Activate: Main] K.O. 1 own Thriller Bark Character: negate this Character effect this turn")
def op06_083_oars_activate(game_state, player, card):
    tb_chars = [c for c in player.cards_in_play
                if c is not card and "Thriller Bark Pirates" in (getattr(c, "card_origin", "") or "")]
    if not tb_chars:
        return False
    snap = list(tb_chars)
    opts = [{"id": str(i), "label": c.name, "card_id": c.id, "card_name": c.name}
            for i, c in enumerate(snap)]

    def do_ko(selected):
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(snap):
            t = snap[idx]
            if t in player.cards_in_play:
                player.cards_in_play.remove(t)
                player.trash.append(t)
                game_state._log(f"{t.name} K.O.'d for Oars effect")
        card.effects_negated = True
        card.effects_negated_this_turn = True
        card.cannot_attack = False
        game_state._log(f"{card.name} effect negated this turn")

    from ...game_engine import PendingChoice
    import uuid
    game_state.pending_choice = PendingChoice(
        choice_id=f"op06_083_{uuid.uuid4().hex[:6]}",
        choice_type="select_cards",
        prompt="K.O. one of your Thriller Bark Pirates Characters to negate Oars' effect this turn",
        options=opts, min_selections=1, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=do_ko,
    )
    return True


# --- OP06-084: Jigoro of the Wind ---
@register_effect("OP06-084", "on_ko", "[On K.O.] Up to 1 own Leader or Character +1000 power this turn")
def op06_084_jigoro(game_state, player, card):
    targets = _own_leader_and_chars(player)
    if targets:
        return create_power_effect_choice(
            game_state, player, targets, 1000,
            source_card=card,
            prompt="Choose your Leader or Character to give +1000 power (Jigoro K.O.)",
            min_selections=0,
        )
    return True


# --- OP06-085: Kumacy ---
@register_effect("OP06-085", "continuous", "[DON!! x2][Your Turn] +1000 power per 5 cards in trash")
def op06_085_kumacy(game_state, player, card):
    if game_state.current_player is not player:
        return True
    if getattr(card, "attached_don", 0) >= 2:
        bonus = (len(player.trash) // 5) * 1000
        if bonus > 0:
            card.power_modifier = getattr(card, "power_modifier", 0) + bonus
    return True


# --- OP06-086: Gecko Moria (cost 8) ---
@register_effect("OP06-086", "on_play", "[On Play] Choose up to 1 char cost 4 or less and up to 1 char cost 2 or less from trash; play 1, play other rested")
def op06_086_moria_char(game_state, player, card):
    cost4_targets = [c for c in player.trash if c.card_type == "CHARACTER" and (getattr(c, "cost", 0) or 0) <= 4]
    if not cost4_targets:
        return True
    snap4 = list(cost4_targets)
    opts4 = [{"id": str(i), "label": f"{c.name} (Cost:{c.cost or 0})",
              "card_id": c.id, "card_name": c.name} for i, c in enumerate(snap4)]

    def after_first(selected):
        card_a = None
        if selected:
            idx = int(selected[0])
            if 0 <= idx < len(snap4):
                card_a = snap4[idx]
                if card_a in player.trash:
                    player.trash.remove(card_a)
        cost2_targets = [c for c in player.trash if c.card_type == "CHARACTER" and (getattr(c, "cost", 0) or 0) <= 2]
        if not cost2_targets:
            if card_a:
                card_a.is_resting = False
                player.cards_in_play.append(card_a)
                game_state._log(f"{player.name} played {card_a.name} from trash")
            return

        snap2 = list(cost2_targets)
        opts2 = [{"id": str(i), "label": f"{c.name} (Cost:{c.cost or 0})",
                  "card_id": c.id, "card_name": c.name} for i, c in enumerate(snap2)]

        def after_second(selected2):
            card_b = None
            if selected2:
                idx2 = int(selected2[0])
                if 0 <= idx2 < len(snap2):
                    card_b = snap2[idx2]
                    if card_b in player.trash:
                        player.trash.remove(card_b)
            if card_a and card_b:
                card_a.is_resting = False
                player.cards_in_play.append(card_a)
                card_b.is_resting = True
                player.cards_in_play.append(card_b)
                game_state._log(f"{player.name} played {card_a.name} (active) and {card_b.name} (rested) from trash")
            elif card_a:
                card_a.is_resting = False
                player.cards_in_play.append(card_a)
                game_state._log(f"{player.name} played {card_a.name} from trash")
            elif card_b:
                card_b.is_resting = False
                player.cards_in_play.append(card_b)
                game_state._log(f"{player.name} played {card_b.name} from trash")

        from ...game_engine import PendingChoice
        import uuid
        game_state.pending_choice = PendingChoice(
            choice_id=f"op06_086b_{uuid.uuid4().hex[:6]}",
            choice_type="select_cards",
            prompt="Choose up to 1 Character cost 2 or less from trash (will be played rested)",
            options=opts2, min_selections=0, max_selections=1,
            source_card_id=card.id, source_card_name=card.name,
            callback=after_second,
        )

    from ...game_engine import PendingChoice
    import uuid
    game_state.pending_choice = PendingChoice(
        choice_id=f"op06_086a_{uuid.uuid4().hex[:6]}",
        choice_type="select_cards",
        prompt="Choose up to 1 Character cost 4 or less from trash (will be played active)",
        options=opts4, min_selections=0, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=after_first,
    )
    return True


# --- OP06-087: Cerberus ---
@register_effect("OP06-087", "blocker", "[Blocker]")
def op06_087_cerberus(game_state, player, card):
    card.has_blocker = True
    return True


# --- OP06-088: Sai ---
@register_effect("OP06-088", "continuous", "[Continuous] If Dressrosa leader is active, +2000 power")
def op06_088_sai(game_state, player, card):
    if player.leader:
        leader_type = getattr(player.leader, "card_origin", "") or ""
        if "Dressrosa" in leader_type and not player.leader.is_resting:
            card.power_modifier = getattr(card, "power_modifier", 0) + 2000
    return True


# --- OP06-089: Taralan ---
@register_effect("OP06-089", "on_play", "[On Play]/[On K.O.] Trash 3 cards from top of deck")
def op06_089_taralan_play(game_state, player, card):
    for _ in range(3):
        if player.deck:
            trashed = player.deck.pop(0)
            player.trash.append(trashed)
    game_state._log(f"{player.name} trashed 3 cards from top of deck (Taralan)")
    return True


@register_effect("OP06-089", "on_ko", "[On Play]/[On K.O.] Trash 3 cards from top of deck")
def op06_089_taralan_ko(game_state, player, card):
    for _ in range(3):
        if player.deck:
            trashed = player.deck.pop(0)
            player.trash.append(trashed)
    game_state._log(f"{player.name} trashed 3 cards from top of deck (Taralan K.O.)")
    return True


# --- OP06-090: Dr. Hogback ---
@register_effect("OP06-090", "on_play", "[On Play] Return 2 from trash to bottom: add Thriller Bark card (not Hogback) from trash to hand")
def op06_090_hogback(game_state, player, card):
    if len(player.trash) < 2:
        return True
    snap = list(player.trash)
    opts = [{"id": str(i), "label": c.name, "card_id": c.id, "card_name": c.name}
            for i, c in enumerate(snap)]

    def after_return(selected):
        if len(selected) < 2:
            return
        for idx_str in selected:
            idx = int(idx_str)
            if 0 <= idx < len(snap):
                c = snap[idx]
                if c in player.trash:
                    player.trash.remove(c)
                    player.deck.append(c)
        game_state._log(f"{player.name} returned 2 cards to bottom of deck")
        targets = [c for c in player.trash
                   if "Thriller Bark Pirates" in (getattr(c, "card_origin", "") or "")
                   and c.name != "Dr. Hogback"]
        if targets:
            create_add_from_trash_choice(game_state, player, targets, source_card=card,
                                         prompt="Add Thriller Bark Pirates card (not Hogback) from trash to hand")

    from ...game_engine import PendingChoice
    import uuid
    game_state.pending_choice = PendingChoice(
        choice_id=f"op06_090_{uuid.uuid4().hex[:6]}",
        choice_type="select_cards",
        prompt="Choose 2 cards from trash to return to bottom of deck (Hogback)",
        options=opts, min_selections=2, max_selections=2,
        source_card_id=card.id, source_card_name=card.name,
        callback=after_return,
    )
    return True


# --- OP06-091: Victoria Cindry ---
@register_effect("OP06-091", "on_play", "[On Play] If Thriller Bark leader, trash 5 from top of deck")
def op06_091_cindry(game_state, player, card):
    leader_type = getattr(player.leader, "card_origin", "") or "" if player.leader else ""
    if "Thriller Bark Pirates" not in leader_type:
        return True
    for _ in range(5):
        if player.deck:
            player.trash.append(player.deck.pop(0))
    game_state._log(f"{player.name} trashed 5 cards from top of deck (Cindry)")
    return True


# --- OP06-092: Brook ---
@register_effect("OP06-092", "on_play", "[On Play] Choose: K.O. opp char cost 4 or less OR opp places 3 from trash to bottom")
def op06_092_brook(game_state, player, card):
    opponent = get_opponent(game_state, player)
    trash_targets = [c for c in opponent.cards_in_play if (getattr(c, "cost", 0) or 0) <= 4]
    modes = []
    if trash_targets:
        modes.append({"id": "trash_char", "label": "Trash opponent cost 4 or less Character",
                      "description": f"{len(trash_targets)} targets"})
    if opponent.trash:
        modes.append({"id": "trash_bottom", "label": "Opponent places 3 from trash at bottom of deck",
                      "description": f"Opponent has {len(opponent.trash)} in trash"})
    if not modes:
        return True

    def callback(selected):
        mode = selected[0] if selected else None
        opp = get_opponent(game_state, player)
        if mode == "trash_char":
            t = [c for c in opp.cards_in_play if (getattr(c, "cost", 0) or 0) <= 4]
            if t:
                def do_trash_char(sel):
                    if not sel:
                        return
                    idx = int(sel[0])
                    if 0 <= idx < len(t):
                        target = t[idx]
                        if target in opp.cards_in_play:
                            opp.cards_in_play.remove(target)
                            opp.trash.append(target)
                            game_state._log(f"{target.name} was trashed by Brook")

                create_target_choice(
                    game_state, player, t,
                    prompt="Trash up to 1 opponent cost 4 or less Character (Brook)",
                    source_card=card,
                    min_selections=0,
                    callback=do_trash_char,
                )
        elif mode == "trash_bottom":
            if opp.trash:
                snap = list(opp.trash)
                n = min(3, len(snap))
                opts = [{"id": str(i), "label": c.name, "card_id": c.id, "card_name": c.name}
                        for i, c in enumerate(snap)]

                def do_bottom(sel):
                    for idx_str in sel:
                        idx = int(idx_str)
                        if 0 <= idx < len(snap):
                            c = snap[idx]
                            if c in opp.trash:
                                opp.trash.remove(c)
                                opp.deck.append(c)
                    game_state._log(f"{opp.name} placed cards from trash to bottom of deck")

                from ...game_engine import PendingChoice
                import uuid
                game_state.pending_choice = PendingChoice(
                    choice_id=f"op06_092_{uuid.uuid4().hex[:6]}",
                    choice_type="select_cards",
                    prompt="Choose 3 cards from trash to place at bottom of deck (Brook)",
                    options=opts, min_selections=min(n, len(snap)), max_selections=n,
                    source_card_id=card.id, source_card_name=card.name,
                    callback=do_bottom,
                )

    return create_mode_choice(game_state, player, modes, source_card=card, callback=callback,
                              prompt="Choose one effect (Brook)")


# --- OP06-093: Perona (character) ---
@register_effect("OP06-093", "on_play", "[On Play] If opponent has 5+ hand: choose opp trashes 1 OR give opp char -3 cost")
def op06_093_perona_char(game_state, player, card):
    opponent = get_opponent(game_state, player)
    if len(opponent.hand) < 5:
        return True
    modes = []
    if opponent.hand:
        modes.append({"id": "discard", "label": "Opponent trashes 1 card from hand",
                      "description": f"Opponent has {len(opponent.hand)} cards"})
    if opponent.cards_in_play:
        modes.append({"id": "cost", "label": "Give opponent Character -3 cost this turn",
                      "description": f"{len(opponent.cards_in_play)} targets"})
    if not modes:
        return True

    def callback(selected):
        mode = selected[0] if selected else None
        opp = get_opponent(game_state, player)
        if mode == "discard":
            if opp.hand:
                snap = list(opp.hand)
                opts = [{"id": str(i), "label": c.name, "card_id": c.id, "card_name": c.name}
                        for i, c in enumerate(snap)]

                def do_discard(sel):
                    if sel:
                        idx = int(sel[0])
                        if 0 <= idx < len(snap):
                            c = snap[idx]
                            if c in opp.hand:
                                opp.hand.remove(c)
                                opp.trash.append(c)
                                game_state._log(f"{opp.name} trashed {c.name} from hand")

                from ...game_engine import PendingChoice
                import uuid
                game_state.pending_choice = PendingChoice(
                    choice_id=f"op06_093d_{uuid.uuid4().hex[:6]}",
                    choice_type="select_cards",
                    prompt="Choose 1 card from your hand to trash (Perona)",
                    options=opts, min_selections=1, max_selections=1,
                    source_card_id=card.id, source_card_name=card.name,
                    callback=do_discard,
                )
        elif mode == "cost":
            targets = list(opp.cards_in_play)
            if targets:
                create_cost_reduction_choice(game_state, player, targets, -3, source_card=card,
                                             prompt="Give opponent's Character -3 cost this turn (Perona)")

    return create_mode_choice(game_state, player, modes, source_card=card, callback=callback,
                              prompt="Choose one effect (Perona)")


# --- OP06-094: Lola --- (no effect)

# --- OP06-095: Shadows Asgard (Event) ---
@register_effect("OP06-095", "on_play", "[Main]/[Counter] Leader +1000; K.O. Thriller Bark chars cost 2 or less; +1000 per K.O.")
def op06_095_shadows_asgard(game_state, player, card):
    if player.leader:
        player.leader.power_modifier = getattr(player.leader, "power_modifier", 0) + 1000
        game_state._log(f"{player.leader.name} gains +1000 power")
    tb_chars = [c for c in player.cards_in_play
                if "Thriller Bark Pirates" in (getattr(c, "card_origin", "") or "")
                and (getattr(c, "cost", 0) or 0) <= 2]
    if not tb_chars:
        return True

    import uuid
    from ...game_engine import PendingChoice

    snapshot = list(tb_chars)
    options = [{"id": str(i), "label": f"{c.name} (Cost: {getattr(c, 'cost', 0) or 0})",
                "card_id": c.id, "card_name": c.name} for i, c in enumerate(snapshot)]

    def do_ko(selected):
        ko_count = 0
        for idx_str in selected:
            idx = int(idx_str)
            if 0 <= idx < len(snapshot):
                target = snapshot[idx]
                if target in player.cards_in_play:
                    player.cards_in_play.remove(target)
                    player.trash.append(target)
                    ko_count += 1
                    game_state._log(f"{target.name} K.O.'d (Shadows Asgard)")
        if ko_count > 0 and player.leader:
            player.leader.power_modifier = getattr(player.leader, "power_modifier", 0) + (ko_count * 1000)
            game_state._log(f"{player.leader.name} gains +{ko_count * 1000} more power ({ko_count} K.O.'d)")

    game_state.pending_choice = PendingChoice(
        choice_id=f"op06_095_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt="Choose any number of your Thriller Bark Pirates Characters cost 2 or less to K.O.",
        options=options,
        min_selections=0,
        max_selections=len(snapshot),
        source_card_id=card.id,
        source_card_name=card.name,
        callback=do_ko,
    )
    return True


@register_effect("OP06-095", "counter", "[Counter] Leader +1000; K.O. Thriller Bark chars cost 2 or less; +1000 per K.O.")
def op06_095_shadows_asgard_counter(game_state, player, card):
    return op06_095_shadows_asgard(game_state, player, card)


@register_effect("OP06-095", "trigger", "[Trigger] Draw 2 and trash 1 from hand")
def op06_095_trigger(game_state, player, card):
    draw_cards(player, 2)
    if player.hand:
        return _trash_from_hand_choice(
            game_state, player, 1, source_card=card,
            prompt="[Trigger] Trash 1 card from hand (Shadows Asgard)",
        )
    return True


# --- OP06-096: ...Nothing...at All!!! (Event) ---
@register_effect("OP06-096", "counter", "[Counter] Add 1 life to hand: own chars cost 7 or less cannot be K.O.'d in battle this turn")
def op06_096_nothing_at_all(game_state, player, card):
    if not player.life_cards:
        return True

    modes = [
        {"id": "pay", "label": "Add 1 Life card to hand"},
        {"id": "skip", "label": "Do not use this effect"},
    ]

    def after_choice(selected):
        if not selected or selected[0] != "pay":
            return
        if player.life_cards:
            taken = player.life_cards.pop(0)
            player.hand.append(taken)
            game_state._log(f"{player.name} added Life card to hand")
        for c in player.cards_in_play:
            if (getattr(c, "cost", 0) or 0) <= 7:
                c.cannot_be_ko_in_battle = True
        game_state._log("Own Characters cost 7 or less cannot be K.O.'d in battle this turn")

    return create_mode_choice(
        game_state, player, modes, source_card=card,
        callback=after_choice,
        prompt="You may add 1 Life card to hand for Nothing at All!!!",
    )


@register_effect("OP06-096", "trigger", "[Trigger] Activate this card Counter effect")
def op06_096_trigger(game_state, player, card):
    return op06_096_nothing_at_all(game_state, player, card)


# --- OP06-097: Negative Hollow (Event) ---
@register_effect("OP06-097", "on_play", "[Main] Trash 1 card from opponent's hand")
def op06_097_negative_hollow(game_state, player, card):
    opponent = get_opponent(game_state, player)
    if not opponent.hand:
        return True
    snap = list(opponent.hand)
    opts = [{"id": str(i), "label": c.name, "card_id": c.id, "card_name": c.name}
            for i, c in enumerate(snap)]

    def do_trash(selected):
        if selected:
            idx = int(selected[0])
            if 0 <= idx < len(snap):
                c = snap[idx]
                if c in opponent.hand:
                    opponent.hand.remove(c)
                    opponent.trash.append(c)
                    game_state._log(f"{opponent.name} trashed {c.name} from hand (Negative Hollow)")

    from ...game_engine import PendingChoice
    import uuid
    game_state.pending_choice = PendingChoice(
        choice_id=f"op06_097_{uuid.uuid4().hex[:6]}",
        choice_type="select_cards",
        prompt="Choose 1 card from opponent's hand to trash (Negative Hollow)",
        options=opts, min_selections=1, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=do_trash,
    )
    return True


@register_effect("OP06-097", "trigger", "[Trigger] Activate this card Main effect")
def op06_097_trigger(game_state, player, card):
    return op06_097_negative_hollow(game_state, player, card)


# --- OP06-098: Thriller Bark (STAGE) ---
@register_effect("OP06-098", "activate", "[Activate: Main] DON ①, rest Stage: if Thriller Bark leader, play Thriller Bark char cost 2 or less from trash rested")
def op06_098_thriller_bark(game_state, player, card):
    if card.is_resting:
        return False
    leader_type = getattr(player.leader, "card_origin", "") or "" if player.leader else ""
    if "Thriller Bark Pirates" not in leader_type:
        return False
    if not _rest_active_don(player, 1):
        return False
    card.is_resting = True
    targets = [c for c in player.trash
               if c.card_type == "CHARACTER"
               and "Thriller Bark Pirates" in (getattr(c, "card_origin", "") or "")
               and (getattr(c, "cost", 0) or 0) <= 2]
    if targets:
        return create_play_from_trash_choice(game_state, player, targets, source_card=card,
                                              rest_on_play=True,
                                              prompt="Play Thriller Bark Character cost 2 or less from trash (rested)")
    return True


# =============================================================================
# CHARACTERS OP06-099 through OP06-119
# =============================================================================

# --- OP06-099: Aisa ---
@register_effect("OP06-099", "on_play", "[On Play] Look at top 1 of own or opponent life, place top or bottom")
def op06_099_aisa(game_state, player, card):
    opponent = get_opponent(game_state, player)
    modes = []
    if player.life_cards:
        modes.append({"id": "own", "label": "Look at own top Life card",
                      "description": f"Own life: {len(player.life_cards)}"})
    if opponent.life_cards:
        modes.append({"id": "opp", "label": "Look at opponent top Life card",
                      "description": f"Opponent life: {len(opponent.life_cards)}"})
    if not modes:
        return True

    def callback(selected):
        mode = selected[0] if selected else None
        opp = get_opponent(game_state, player)
        target_player = player if mode == "own" else opp
        if not target_player.life_cards:
            return
        life_card = target_player.life_cards[0]
        game_state._log(f"Top Life card revealed: {life_card.name}")
        pos_modes = [
            {"id": "top", "label": "Place at top of Life cards"},
            {"id": "bottom", "label": "Place at bottom of Life cards"},
        ]

        def place_callback(pos_sel):
            pos = pos_sel[0] if pos_sel else "top"
            if life_card in target_player.life_cards:
                target_player.life_cards.remove(life_card)
                if pos == "top":
                    target_player.life_cards.insert(0, life_card)
                else:
                    target_player.life_cards.append(life_card)
                game_state._log(f"{life_card.name} placed at {pos} of Life cards")

        create_mode_choice(game_state, player, pos_modes, source_card=card,
                           callback=place_callback,
                           prompt=f"Place {life_card.name} at top or bottom of Life?")

    return create_mode_choice(game_state, player, modes, source_card=card, callback=callback,
                              prompt="Choose whose Life cards to look at (Aisa)")


# --- OP06-100: Inuarashi ---
@register_effect("OP06-100", "on_attack", "[DON!! x2][When Attacking] Trash 1 from hand: K.O. opp char with cost <= opp life count")
def op06_100_inuarashi(game_state, player, card):
    if getattr(card, "attached_don", 0) < 2:
        return True
    if not player.hand:
        return True
    opponent = get_opponent(game_state, player)
    opp_life_count = len(opponent.life_cards)
    ko_targets = [c for c in opponent.cards_in_play if (getattr(c, "cost", 0) or 0) <= opp_life_count]
    if not ko_targets:
        return True
    def after_discard(trashed):
        if not trashed:
            return
        opp = get_opponent(game_state, player)
        opp_life = len(opp.life_cards)
        t = [c for c in opp.cards_in_play if (getattr(c, "cost", 0) or 0) <= opp_life]
        if t:
            create_ko_choice(game_state, player, t, source_card=card,
                             prompt=f"K.O. up to 1 opponent Character with cost {opp_life} or less (Inuarashi)",
                             min_selections=0)

    return _trash_from_hand_choice(
        game_state, player, 1, source_card=card,
        prompt="You may trash 1 card from hand for Inuarashi",
        optional=True,
        on_complete=after_discard,
    )


@register_effect("OP06-100", "trigger", "[Trigger] If opponent has 3 or less Life cards, play this card")
def op06_100_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    if len(opponent.life_cards) <= 3:
        card.is_resting = False
        player.cards_in_play.append(card)
        game_state._log(f"{player.name} played {card.name} from Trigger")
    return True


# --- OP06-101: O-Nami ---
@register_effect("OP06-101", "on_play", "[On Play] Own leader or character gains [Banish] this turn")
def op06_101_onami(game_state, player, card):
    targets = _own_leader_and_chars(player)
    if not targets:
        return True
    snap = list(targets)
    opts = [{"id": str(i), "label": c.name, "card_id": c.id, "card_name": c.name}
            for i, c in enumerate(snap)]

    def do_banish(selected):
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(snap):
            t = snap[idx]
            t.has_banish = True
            game_state._log(f"{t.name} gains [Banish] this turn")

    from ...game_engine import PendingChoice
    import uuid
    game_state.pending_choice = PendingChoice(
        choice_id=f"op06_101_{uuid.uuid4().hex[:6]}",
        choice_type="select_cards",
        prompt="Choose your Leader or Character to give [Banish] this turn (O-Nami)",
        options=opts, min_selections=0, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=do_banish,
    )
    return True


@register_effect("OP06-101", "trigger", "[Trigger] K.O. opponent Character cost 5 or less")
def op06_101_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, "cost", 0) or 0) <= 5]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                                prompt="[Trigger] K.O. opponent Character cost 5 or less (O-Nami)")
    return True


# --- OP06-102: Kamakiri ---
@register_effect("OP06-102", "activate", "[Activate: Main] [Once Per Turn] Place Stage cost 1 at bottom: K.O. opp char cost 2 or less")
def op06_102_kamakiri(game_state, player, card):
    if getattr(card, "op06_102_used", False):
        return False
    stage_targets = [c for c in player.cards_in_play if c.card_type == "STAGE" and (getattr(c, "cost", 0) or 0) <= 1]
    if not stage_targets:
        return False
    card.op06_102_used = True
    snap = list(stage_targets)
    opts = [{"id": str(i), "label": c.name, "card_id": c.id, "card_name": c.name}
            for i, c in enumerate(snap)]

    def after_stage(selected):
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(snap):
            s = snap[idx]
            owner = player
            if s in owner.cards_in_play:
                owner.cards_in_play.remove(s)
                owner.deck.append(s)
                game_state._log(f"{s.name} placed at bottom of deck")
        opp = get_opponent(game_state, player)
        t = [c for c in opp.cards_in_play if (getattr(c, "cost", 0) or 0) <= 2]
        if t:
            create_ko_choice(game_state, player, t, source_card=card,
                             prompt="K.O. opponent Character cost 2 or less (Kamakiri)")

    from ...game_engine import PendingChoice
    import uuid
    game_state.pending_choice = PendingChoice(
        choice_id=f"op06_102_{uuid.uuid4().hex[:6]}",
        choice_type="select_cards",
        prompt="Choose Stage cost 1 to place at bottom of deck (Kamakiri)",
        options=opts, min_selections=1, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=after_stage,
    )
    return True


@register_effect("OP06-102", "trigger", "[Trigger] If own 2 or less Life cards, play this card")
def op06_102_trigger(game_state, player, card):
    if len(player.life_cards) <= 2:
        card.is_resting = False
        player.cards_in_play.append(card)
        game_state._log(f"{player.name} played {card.name} from Trigger")
    return True


# --- OP06-103: Kawamatsu ---
@register_effect("OP06-103", "on_attack", "[When Attacking] Trash 2 from hand: add own 0-power char to top or bottom of life")
def op06_103_kawamatsu(game_state, player, card):
    if len(player.hand) < 2:
        return True
    zero_chars = [c for c in player.cards_in_play
                  if c is not card and (getattr(c, "power", 0) or 0) == 0]
    if not zero_chars:
        return True
    def after_discard(trashed):
        if len(trashed) < 2:
            return
        fresh_zero = [c for c in player.cards_in_play if (getattr(c, "power", 0) or 0) == 0]
        if not fresh_zero:
            return
        snap2 = list(fresh_zero)
        opts2 = [{"id": str(i), "label": c.name, "card_id": c.id, "card_name": c.name}
                 for i, c in enumerate(snap2)]

        def pick_char(sel2):
            if not sel2:
                return
            idx2 = int(sel2[0])
            if 0 <= idx2 < len(snap2):
                t = snap2[idx2]
                pos_modes = [
                    {"id": "top", "label": "Add to top of Life cards"},
                    {"id": "bottom", "label": "Add to bottom of Life cards"},
                ]

                def place(pos_sel):
                    pos = pos_sel[0] if pos_sel else "top"
                    if t in player.cards_in_play:
                        player.cards_in_play.remove(t)
                    t.is_face_up = True
                    if pos == "top":
                        player.life_cards.insert(0, t)
                    else:
                        player.life_cards.append(t)
                    game_state._log(f"{t.name} added to {pos} of Life cards (face-up)")

                create_mode_choice(game_state, player, pos_modes, source_card=card,
                                   callback=place,
                                   prompt=f"Add {t.name} to top or bottom of Life cards?")

        from ...game_engine import PendingChoice
        import uuid
        game_state.pending_choice = PendingChoice(
            choice_id=f"op06_103b_{uuid.uuid4().hex[:6]}",
            choice_type="select_cards",
            prompt="Choose your 0-power Character to add to Life cards (Kawamatsu)",
            options=opts2, min_selections=0, max_selections=1,
            source_card_id=card.id, source_card_name=card.name,
            callback=pick_char,
        )

    return _trash_from_hand_choice(
        game_state, player, 2, source_card=card,
        prompt="You may trash 2 cards from hand for Kawamatsu",
        optional=True,
        on_complete=after_discard,
    )


@register_effect("OP06-103", "trigger", "[Trigger] If opponent has 3 or less Life cards, play this card")
def op06_103_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    if len(opponent.life_cards) <= 3:
        card.is_resting = False
        player.cards_in_play.append(card)
        game_state._log(f"{player.name} played {card.name} from Trigger")
    return True


# --- OP06-104: Kikunojo ---
@register_effect("OP06-104", "on_ko", "[On K.O.] If opponent 3 or less Life, add top of deck to top of own Life")
def op06_104_kikunojo(game_state, player, card):
    opponent = get_opponent(game_state, player)
    if len(opponent.life_cards) <= 3 and player.deck:
        top = player.deck.pop(0)
        player.life_cards.insert(0, top)
        game_state._log(f"{player.name} added {top.name} to top of Life cards (Kikunojo)")
    return True


@register_effect("OP06-104", "trigger", "[Trigger] If opponent has 3 or less Life cards, play this card")
def op06_104_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    if len(opponent.life_cards) <= 3:
        card.is_resting = False
        player.cards_in_play.append(card)
        game_state._log(f"{player.name} played {card.name} from Trigger")
    return True


# --- OP06-105: Genbo --- (no effect)

# --- OP06-106: Kouzuki Hiyori ---
@register_effect("OP06-106", "on_play", "[On Play] Add life top/bottom to hand: add hand card to top of own life")
def op06_106_hiyori(game_state, player, card):
    if not player.life_cards:
        return True
    pos_modes = [
        {"id": "top", "label": "Take top Life card", "description": ""},
        {"id": "bottom", "label": "Take bottom Life card", "description": ""},
    ]

    def take_life(selected):
        pos = selected[0] if selected else "top"
        if not player.life_cards:
            return
        if pos == "top":
            taken = player.life_cards.pop(0)
        else:
            taken = player.life_cards.pop()
        player.hand.append(taken)
        game_state._log(f"{player.name} added Life card to hand (Hiyori)")
        if player.hand:
            hand_snap = list(player.hand)
            opts = [{"id": str(i), "label": c.name, "card_id": c.id, "card_name": c.name}
                    for i, c in enumerate(hand_snap)]

            def put_life(sel2):
                if not sel2:
                    return
                idx = int(sel2[0])
                if 0 <= idx < len(hand_snap):
                    c = hand_snap[idx]
                    if c in player.hand:
                        player.hand.remove(c)
                        player.life_cards.insert(0, c)
                        game_state._log(f"{c.name} added to top of Life cards (Hiyori)")

            from ...game_engine import PendingChoice
            import uuid
            game_state.pending_choice = PendingChoice(
                choice_id=f"op06_106b_{uuid.uuid4().hex[:6]}",
                choice_type="select_cards",
                prompt="Choose a card from hand to add to top of Life cards (Hiyori)",
                options=opts, min_selections=0, max_selections=1,
                source_card_id=card.id, source_card_name=card.name,
                callback=put_life,
            )

    return create_mode_choice(game_state, player, pos_modes, source_card=card,
                              callback=take_life,
                              prompt="Take top or bottom Life card to hand (Hiyori)")


# --- OP06-107: Kouzuki Momonosuke ---
@register_effect("OP06-107", "blocker", "[Blocker]")
def op06_107_momo_blocker(game_state, player, card):
    card.has_blocker = True
    return True


@register_effect("OP06-107", "on_play", "[On Play] Add Land of Wano Character (not Momo) to top or bottom of Life cards face-up")
def op06_107_momo_play(game_state, player, card):
    targets = [c for c in player.cards_in_play
               if c is not card and "Land of Wano" in (getattr(c, "card_origin", "") or "")]
    if not targets:
        return True
    snap = list(targets)
    opts = [{"id": str(i), "label": c.name, "card_id": c.id, "card_name": c.name}
            for i, c in enumerate(snap)]

    def pick_char(selected):
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(snap):
            t = snap[idx]
            pos_modes = [
                {"id": "top", "label": "Add to top of Life cards"},
                {"id": "bottom", "label": "Add to bottom of Life cards"},
            ]

            def place(pos_sel):
                pos = pos_sel[0] if pos_sel else "top"
                if t in player.cards_in_play:
                    player.cards_in_play.remove(t)
                t.is_face_up = True
                if pos == "top":
                    player.life_cards.insert(0, t)
                else:
                    player.life_cards.append(t)
                game_state._log(f"{t.name} added to {pos} of Life cards face-up (Momonosuke)")

            create_mode_choice(game_state, player, pos_modes, source_card=card,
                               callback=place,
                               prompt=f"Add {t.name} to top or bottom of Life cards?")

    from ...game_engine import PendingChoice
    import uuid
    game_state.pending_choice = PendingChoice(
        choice_id=f"op06_107_{uuid.uuid4().hex[:6]}",
        choice_type="select_cards",
        prompt="Choose Land of Wano Character (not Momonosuke) to add to Life cards (Momonosuke)",
        options=opts, min_selections=0, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=pick_char,
    )
    return True


# --- OP06-108: Tenguyama Hitetsu --- (trigger only)
@register_effect("OP06-108", "trigger", "[Trigger] Land of Wano Leader or Character +2000 power this turn")
def op06_108_hitetsu_trigger(game_state, player, card):
    targets = [c for c in _own_leader_and_chars(player)
               if "Land of Wano" in (getattr(c, "card_origin", "") or "")]
    if not targets:
        return True
    snap = list(targets)
    opts = [{"id": str(i), "label": c.name, "card_id": c.id, "card_name": c.name}
            for i, c in enumerate(snap)]

    def do_power(selected):
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(snap):
            t = snap[idx]
            t.power_modifier = getattr(t, "power_modifier", 0) + 2000
            game_state._log(f"{t.name} gains +2000 power (Hitetsu Trigger)")

    from ...game_engine import PendingChoice
    import uuid
    game_state.pending_choice = PendingChoice(
        choice_id=f"op06_108_{uuid.uuid4().hex[:6]}",
        choice_type="select_cards",
        prompt="[Trigger] Choose Land of Wano Leader or Character to give +2000 power",
        options=opts, min_selections=0, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=do_power,
    )
    return True


# --- OP06-109: Denjiro ---
@register_effect("OP06-109", "continuous", "[DON!! x2] If opponent has 3 or less Life, cannot be K.O.'d by effects")
def op06_109_denjiro(game_state, player, card):
    if getattr(card, "attached_don", 0) >= 2:
        opponent = get_opponent(game_state, player)
        if len(opponent.life_cards) <= 3:
            card.cannot_be_ko_by_effects = True
    return True


@register_effect("OP06-109", "trigger", "[Trigger] If opponent has 3 or less Life, play this card")
def op06_109_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    if len(opponent.life_cards) <= 3:
        card.is_resting = False
        player.cards_in_play.append(card)
        game_state._log(f"{player.name} played {card.name} from Trigger")
    return True


# --- OP06-110: Nekomamushi ---
@register_effect("OP06-110", "continuous", "[DON!! x2] Can attack opponent's active Characters")
def op06_110_nekomamushi(game_state, player, card):
    if getattr(card, "attached_don", 0) >= 2:
        card.can_attack_active = True
    return True


@register_effect("OP06-110", "trigger", "[Trigger] If opponent has 3 or less Life, play this card")
def op06_110_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    if len(opponent.life_cards) <= 3:
        card.is_resting = False
        player.cards_in_play.append(card)
        game_state._log(f"{player.name} played {card.name} from Trigger")
    return True


# --- OP06-111: Braham ---
@register_effect("OP06-111", "activate", "[Activate: Main] [Once Per Turn] Place Stage cost 1 at bottom: Rest opp char cost 4 or less")
def op06_111_braham(game_state, player, card):
    if getattr(card, "op06_111_used", False):
        return False
    stage_targets = [c for c in player.cards_in_play if c.card_type == "STAGE" and (getattr(c, "cost", 0) or 0) <= 1]
    if not stage_targets:
        return False
    card.op06_111_used = True
    snap = list(stage_targets)
    opts = [{"id": str(i), "label": c.name, "card_id": c.id, "card_name": c.name}
            for i, c in enumerate(snap)]

    def after_stage(selected):
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(snap):
            s = snap[idx]
            if s in player.cards_in_play:
                player.cards_in_play.remove(s)
                player.deck.append(s)
                game_state._log(f"{s.name} placed at bottom of deck")
        opp = get_opponent(game_state, player)
        t = [c for c in opp.cards_in_play if not c.is_resting and (getattr(c, "cost", 0) or 0) <= 4]
        if t:
            create_rest_choice(game_state, player, t, source_card=card,
                               prompt="Rest opponent's Character cost 4 or less (Braham)")

    from ...game_engine import PendingChoice
    import uuid
    game_state.pending_choice = PendingChoice(
        choice_id=f"op06_111_{uuid.uuid4().hex[:6]}",
        choice_type="select_cards",
        prompt="Choose Stage cost 1 to place at bottom of deck (Braham)",
        options=opts, min_selections=1, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=after_stage,
    )
    return True


@register_effect("OP06-111", "trigger", "[Trigger] If own 2 or less Life cards, play this card")
def op06_111_trigger(game_state, player, card):
    if len(player.life_cards) <= 2:
        card.is_resting = False
        player.cards_in_play.append(card)
        game_state._log(f"{player.name} played {card.name} from Trigger")
    return True


# --- OP06-112: Raizo ---
@register_effect("OP06-112", "on_attack", "[When Attacking] Trash 1 from hand: Rest 1 opponent DON!!")
def op06_112_raizo(game_state, player, card):
    if not player.hand:
        return True
    opponent = get_opponent(game_state, player)
    if not any(d == "active" for d in opponent.don_pool):
        return True
    def after_discard(trashed):
        if not trashed:
            return
        opp = get_opponent(game_state, player)
        _opponent_rest_active_don(opp, 1)
        game_state._log(f"{opp.name} DON!! rested (Raizo)")

    return _trash_from_hand_choice(
        game_state, player, 1, source_card=card,
        prompt="You may trash 1 card from hand for Raizo",
        optional=True,
        on_complete=after_discard,
    )


@register_effect("OP06-112", "trigger", "[Trigger] If opponent has 3 or less Life, play this card")
def op06_112_trigger(game_state, player, card):
    opponent = get_opponent(game_state, player)
    if len(opponent.life_cards) <= 3:
        card.is_resting = False
        player.cards_in_play.append(card)
        game_state._log(f"{player.name} played {card.name} from Trigger")
    return True


# --- OP06-113: Raki ---
@register_effect("OP06-113", "continuous", "[Continuous] If own Shandian Warrior Character (not Raki), gains Blocker")
def op06_113_raki(game_state, player, card):
    has_shandian = any(
        c is not card and "Shandian Warrior" in (getattr(c, "card_origin", "") or "")
        for c in player.cards_in_play
    )
    if has_shandian:
        card.has_blocker = True
    return True


# --- OP06-114: Wyper ---
@register_effect("OP06-114", "on_play", "[On Play] Place Stage cost 1 at bottom: look at 5 top, reveal Upper Yard or Shandian Warrior card")
def op06_114_wyper(game_state, player, card):
    stage_targets = [c for c in player.cards_in_play if c.card_type == "STAGE" and (getattr(c, "cost", 0) or 0) <= 1]
    if not stage_targets:
        return True
    snap = list(stage_targets)
    opts = [{"id": str(i), "label": c.name, "card_id": c.id, "card_name": c.name}
            for i, c in enumerate(snap)]

    def after_stage(selected):
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(snap):
            s = snap[idx]
            if s in player.cards_in_play:
                player.cards_in_play.remove(s)
                player.deck.append(s)
                game_state._log(f"{s.name} placed at bottom of deck (Wyper)")
        search_top_cards(
            game_state, player, 5, add_count=1,
            filter_fn=lambda c2: ("Upper Yard" in (getattr(c2, "card_origin", "") or "")
                                  or "Shandian Warrior" in (getattr(c2, "card_origin", "") or "")),
            source_card=card,
            prompt="Look at top 5: reveal Upper Yard or Shandian Warrior card to hand",
        )

    from ...game_engine import PendingChoice
    import uuid
    game_state.pending_choice = PendingChoice(
        choice_id=f"op06_114_{uuid.uuid4().hex[:6]}",
        choice_type="select_cards",
        prompt="Choose Stage cost 1 to place at bottom of deck (Wyper)",
        options=opts, min_selections=1, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=after_stage,
    )
    return True


# --- OP06-115: You're the One Who Should Disappear. (Event) ---
@register_effect("OP06-115", "counter", "[Counter] Trash 1 from hand: Leader/Character +3000 power this battle")
def op06_115_disappear(game_state, player, card):
    if not player.hand:
        return True

    def after_discard(trashed):
        if not trashed:
            return
        targets = _own_leader_and_chars(player)
        if targets:
            snap = list(targets)

            def apply_battle_power(selected):
                for sel in selected:
                    idx = int(sel)
                    if 0 <= idx < len(snap):
                        _add_battle_power(game_state, snap[idx], 3000)

            create_power_effect_choice(
                game_state, player, targets, 3000,
                source_card=card,
                prompt="Choose your Leader or Character to give +3000 power during this battle",
                min_selections=0,
                callback=apply_battle_power,
            )

    return _trash_from_hand_choice(
        game_state, player, 1, source_card=card,
        prompt="You may trash 1 card from hand for +3000 power",
        optional=True,
        on_complete=after_discard,
    )


@register_effect("OP06-115", "trigger", "[Trigger] If 0 Life cards, add top of deck to Life, then trash 1 from hand")
def op06_115_trigger(game_state, player, card):
    def trash_after_life():
        if player.hand:
            _trash_from_hand_choice(
                game_state, player, 1, source_card=card,
                prompt="[Trigger] Trash 1 card from hand",
            )

    if len(player.life_cards) == 0 and player.deck:
        modes = [
            {"id": "add", "label": "Add top deck card to Life"},
            {"id": "skip", "label": "Do not add a Life card"},
        ]

        def after_choice(selected):
            if selected and selected[0] == "add" and player.deck:
                top = player.deck.pop(0)
                player.life_cards.insert(0, top)
                game_state._log(f"{player.name} added {top.name} to top of Life cards (Trigger)")
            trash_after_life()

        return create_mode_choice(
            game_state, player, modes, source_card=card,
            callback=after_choice,
            prompt="[Trigger] You may add up to 1 card from deck to Life",
        )
    trash_after_life()
    return True


# --- OP06-116: Reject (Event) ---
@register_effect("OP06-116", "on_play", "[Main] Choose: K.O. opp char cost 5 or less OR if opp 1 Life: deal 1 damage + add life to hand")
def op06_116_reject(game_state, player, card):
    opponent = get_opponent(game_state, player)
    ko_targets = [c for c in opponent.cards_in_play if (getattr(c, "cost", 0) or 0) <= 5]
    opp_one_life = len(opponent.life_cards) == 1
    modes = []
    if ko_targets:
        modes.append({"id": "ko", "label": "K.O. opponent Character cost 5 or less",
                      "description": f"{len(ko_targets)} targets"})
    if opp_one_life:
        modes.append({"id": "damage", "label": "Deal 1 damage to opponent, add Life card to hand",
                      "description": "Opponent has 1 Life card"})
    if not modes:
        return True

    def callback(selected):
        mode = selected[0] if selected else None
        opp = get_opponent(game_state, player)
        if mode == "ko":
            t = [c for c in opp.cards_in_play if (getattr(c, "cost", 0) or 0) <= 5]
            if t:
                create_ko_choice(game_state, player, t, source_card=card,
                                 prompt="K.O. opponent Character cost 5 or less (Reject)")
        elif mode == "damage":
            game_state._deal_damage(opponent, 1)
            if player.life_cards:
                taken = player.life_cards.pop(0)
                player.hand.append(taken)
                game_state._log(f"{player.name} added Life card to hand (Reject)")

    return create_mode_choice(game_state, player, modes, source_card=card, callback=callback,
                              prompt="Choose one effect (Reject)")


@register_effect("OP06-116", "trigger", "[Trigger] Draw 1 card")
def op06_116_trigger(game_state, player, card):
    draw_cards(player, 1)
    return True


# --- OP06-117: The Ark Maxim (STAGE) ---
@register_effect("OP06-117", "activate", "[Activate: Main] [Once Per Turn] Rest this + 1 Enel char: K.O. all opp chars cost 2 or less")
def op06_117_ark_maxim(game_state, player, card):
    if getattr(card, "op06_117_used", False):
        return False
    if card.is_resting:
        return False
    enel_chars = [c for c in player.cards_in_play if c.name == "Enel" and not c.is_resting]
    if not enel_chars:
        return False
    card.op06_117_used = True
    snap = list(enel_chars)
    opts = [{"id": str(i), "label": c.name, "card_id": c.id, "card_name": c.name}
            for i, c in enumerate(snap)]

    def after_enel(selected):
        if not selected:
            return
        idx = int(selected[0])
        if 0 <= idx < len(snap):
            e = snap[idx]
            e.is_resting = True
            game_state._log(f"{e.name} rested for Ark Maxim effect")
        card.is_resting = True
        opp = get_opponent(game_state, player)
        to_ko = [c for c in opp.cards_in_play if (getattr(c, "cost", 0) or 0) <= 2]
        for c in to_ko:
            opp.cards_in_play.remove(c)
            opp.trash.append(c)
            game_state._log(f"{c.name} K.O.'d (Ark Maxim)")

    from ...game_engine import PendingChoice
    import uuid
    game_state.pending_choice = PendingChoice(
        choice_id=f"op06_117_{uuid.uuid4().hex[:6]}",
        choice_type="select_cards",
        prompt="Choose 1 Enel Character to rest for Ark Maxim effect",
        options=opts, min_selections=1, max_selections=1,
        source_card_id=card.id, source_card_name=card.name,
        callback=after_enel,
    )
    return True


# --- OP06-118: Roronoa Zoro (SEC) ---
@register_effect("OP06-118", "on_attack", "[When Attacking] [Once Per Turn] DON ①: Set this Character active")
def op06_118_zoro_attack(game_state, player, card):
    if getattr(card, "op06_118_atk_used", False):
        return False
    if not _rest_active_don(player, 1):
        return False
    card.op06_118_atk_used = True
    card.is_resting = False
    card.has_attacked = False
    game_state._log(f"{card.name} set to active (When Attacking DON ①)")
    return True


@register_effect("OP06-118", "activate", "[Activate: Main] [Once Per Turn] DON ②: Set this Character active")
def op06_118_zoro_activate(game_state, player, card):
    if getattr(card, "op06_118_act_used", False):
        return False
    if player.don_pool.count("active") < 2:
        return False
    _rest_active_don(player, 2)
    card.op06_118_act_used = True
    card.is_resting = False
    card.has_attacked = False
    game_state._log(f"{card.name} set to active (Activate: Main DON ②)")
    return True


# --- OP06-119: Sanji (SEC) ---
@register_effect("OP06-119", "on_play", "[On Play] Reveal top 1 of deck, play Character cost 9 or less (not Sanji), place rest at bottom")
def op06_119_sanji_sec(game_state, player, card):
    return search_top_cards(
        game_state, player, 1, add_count=1,
        filter_fn=lambda c: c.card_type == "CHARACTER" and (getattr(c, "cost", 0) or 0) <= 9 and c.name != "Sanji",
        source_card=card,
        play_to_field=True,
        prompt="Reveal top 1 card: play Character cost 9 or less (not Sanji) or place at bottom",
    )
