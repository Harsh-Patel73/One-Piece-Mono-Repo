"""
Hardcoded effects for OP06 cards.
"""

import random

from ..hardcoded import (
    create_add_to_life_choice, create_bottom_deck_choice, create_don_assignment_choice, create_ko_choice,
    create_cost_reduction_choice, create_mode_choice, create_play_from_trash_choice,
    create_power_effect_choice, create_rest_choice, create_return_to_hand_choice,
    create_target_choice, check_leader_type, draw_cards, filter_by_max_cost, get_opponent, register_effect,
    search_top_cards, trash_from_hand,
)


# --- OP06-044: Gion ---
@register_effect("OP06-044", "ON_EVENT_ACTIVATE", "Opponent places 1 card from hand at bottom")
def gion_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    if opponent.hand:
        # Opponent picks lowest cost
        sorted_hand = sorted(opponent.hand, key=lambda c: getattr(c, 'cost', 0) or 0)
        card_to_place = sorted_hand[0]
        opponent.hand.remove(card_to_place)
        opponent.deck.append(card_to_place)
        return True
    return False


# --- OP06-009: Shuraiya ---
@register_effect("OP06-009", "WHEN_ATTACKING", "Become same power as opponent's Leader")
def shuraiya_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    if opponent.leader:
        card.power = getattr(opponent.leader, 'power', 5000)
        return True
    return False


# --- OP06-117: The Ark Maxim ---
@register_effect("OP06-117", "MAIN", "Rest this and Enel: KO all cost 2 or less")
def ark_maxim_effect(game_state, player, card):
    enel = [c for c in player.cards_in_play if 'Enel' in getattr(c, 'name', '') and not c.is_resting]
    if enel and not card.is_resting:
        card.is_resting = True
        enel[0].is_resting = True
        opponent = get_opponent(game_state, player)
        to_ko = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
        for c in to_ko:
            opponent.cards_in_play.remove(c)
            opponent.trash.append(c)
        return True
    return False


# --- OP06-041: The Ark Noah ---
@register_effect("OP06-041", "ON_PLAY", "Rest all opponent's Characters")
def ark_noah_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    for c in opponent.cards_in_play:
        c.is_resting = True
    return True


# --- OP06-044: Gion ---
@register_effect("OP06-044", "ON_OPPONENT_EVENT", "Opponent places 1 card from hand at bottom")
def gion_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    if opponent.hand:
        card_to_place = opponent.hand.pop(0)
        opponent.deck.append(card_to_place)
        return True
    return False


# --- OP06-117: The Ark Maxim ---
@register_effect("OP06-117", "ACTIVATE_MAIN", "Rest this and Enel to KO all opponent's cost 2 or less")
def ark_maxim_effect(game_state, player, card):
    enel_cards = [c for c in player.cards_in_play if 'enel' in getattr(c, 'name', '').lower()]
    if enel_cards and not card.is_resting:
        card.is_resting = True
        enel_cards[0].is_resting = True
        opponent = get_opponent(game_state, player)
        to_ko = [c for c in opponent.cards_in_play if getattr(c, 'cost', 0) <= 2]
        for c in to_ko:
            opponent.cards_in_play.remove(c)
            opponent.trash.append(c)
        return True
    return False


# --- OP06-039: You Ain't Even Worth Killing Time!! ---
@register_effect("OP06-039", "MAIN", "Choose: Rest cost 6 or less OR KO rested cost 6 or less")
def you_aint_worth_effect(game_state, player, card):
    """Choose: Rest OR KO rested cost 6 or less."""
    opponent = get_opponent(game_state, player)
    rested_targets = [c for c in opponent.cards_in_play
                     if c.is_resting and (getattr(c, 'cost', 0) or 0) <= 6]
    active_targets = [c for c in opponent.cards_in_play
                     if not c.is_resting and (getattr(c, 'cost', 0) or 0) <= 6]

    modes = []
    if active_targets:
        modes.append({"id": "rest", "label": "Rest cost 6 or less", "description": f"Rest 1 of {len(active_targets)} targets"})
    if rested_targets:
        modes.append({"id": "ko", "label": "KO rested cost 6 or less", "description": f"KO 1 of {len(rested_targets)} rested targets"})

    if modes:
        def callback(selected: list[str]) -> None:
            selected_mode = selected[0] if selected else None
            if selected_mode == "rest" and active_targets:
                create_rest_choice(game_state, player, active_targets, source_card=card,
                                   prompt="Choose opponent's cost 6 or less Character to rest")
            elif selected_mode == "ko" and rested_targets:
                create_ko_choice(game_state, player, rested_targets, source_card=card,
                                 prompt="Choose opponent's rested cost 6 or less Character to K.O.")

        return create_mode_choice(
            game_state, player, modes, source_card=card, callback=callback,
            prompt="Choose effect"
        )
    return False


# --- OP06-116: Reject ---
@register_effect("OP06-116", "MAIN", "Choose: KO cost 5 or less OR deal 1 damage if opponent has 1 life")
def reject_effect(game_state, player, card):
    """Choose: KO cost 5 or less OR deal 1 damage (if opponent has 1 life)."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
              if (getattr(c, 'cost', 0) or 0) <= 5]

    modes = []
    if targets:
        modes.append({"id": "ko", "label": "KO cost 5 or less", "description": f"KO 1 of {len(targets)} targets"})
    if len(opponent.life_cards) == 1:
        modes.append({"id": "damage", "label": "Deal 1 damage", "description": "Deal 1 damage to opponent (they have 1 life!)"})

    if modes:
        def callback(selected: list[str]) -> None:
            selected_mode = selected[0] if selected else None
            if selected_mode == "ko" and targets:
                create_ko_choice(game_state, player, targets, source_card=card,
                                 prompt="Choose opponent's cost 5 or less Character to K.O.")
            elif selected_mode == "damage":
                opponent_ref = get_opponent(game_state, player)
                if opponent_ref.life_cards:
                    opponent_ref.trash.append(opponent_ref.life_cards.pop(0))
                    game_state._log(f"{opponent_ref.name} took 1 damage")

        return create_mode_choice(
            game_state, player, modes, source_card=card, callback=callback,
            prompt="Choose Reject effect"
        )
    return False


# --- OP06-021: Perona ---
@register_effect("OP06-021", "ACTIVATE_MAIN", "Choose: Rest cost 4 or less OR give -1 cost")
def perona_activate_effect(game_state, player, card):
    """Choose: Rest cost 4 or less OR give -1 cost."""
    opponent = get_opponent(game_state, player)
    rest_targets = [c for c in opponent.cards_in_play
              if not c.is_resting and (getattr(c, 'cost', 0) or 0) <= 4]

    modes = []
    if rest_targets:
        modes.append({"id": "rest", "label": "Rest cost 4 or less", "description": f"Rest 1 of {len(rest_targets)} targets"})
    if opponent.cards_in_play:
        modes.append({"id": "cost_reduce", "label": "Give -1 cost", "description": f"Give -1 cost to 1 of {len(opponent.cards_in_play)} characters"})

    if modes:
        def callback(selected: list[str]) -> None:
            selected_mode = selected[0] if selected else None
            opponent_ref = get_opponent(game_state, player)
            if selected_mode == "rest" and rest_targets:
                create_rest_choice(game_state, player, rest_targets, source_card=card,
                                   prompt="Choose opponent's cost 4 or less Character to rest")
            elif selected_mode == "cost_reduce" and opponent_ref.cards_in_play:
                create_cost_reduction_choice(
                    game_state, player, list(opponent_ref.cards_in_play), -1, source_card=card,
                    prompt="Choose opponent's Character to give -1 cost"
                )

        return create_mode_choice(
            game_state, player, modes, source_card=card, callback=callback,
            prompt="Choose Perona effect"
        )
    return False


# --- OP06-015: Lily Carnation ---
@register_effect("OP06-015", "ACTIVATE_MAIN", "Trash 6000+ power char: Play FILM 2000-5000 from trash rested")
def op06_015_lily(game_state, player, card):
    chars_6k = [c for c in player.cards_in_play
                if (getattr(c, 'power', 0) or 0) >= 6000]
    if chars_6k:
        to_trash = chars_6k[0]
        player.cards_in_play.remove(to_trash)
        player.trash.append(to_trash)
        # Play FILM from trash
        film_chars = [c for c in player.trash
                      if 'FILM' in (getattr(c, 'card_origin', '') or '')
                      and getattr(c, 'card_type', '') == 'CHARACTER'
                      and 2000 <= (getattr(c, 'power', 0) or 0) <= 5000]
        if film_chars:
            to_play = film_chars[0]
            player.trash.remove(to_play)
            to_play.is_resting = True
            player.cards_in_play.append(to_play)
    return True


# =============================================================================
# MORE COMPLEX CHOICE CARDS
# =============================================================================

# =============================================================================
# LEADER CARD EFFECTS - OP06 (Wings of the Captain)
# =============================================================================

# --- OP06-001: Uta (Leader) ---
@register_effect("OP06-001", "on_attack", "[When Attacking] Trash FILM: Opponent -2000, add 1 DON")
def op06_001_uta_leader(game_state, player, card):
    """When Attacking: Trash a FILM card from hand, opponent's Character -2000, add 1 DON from deck."""
    film_cards = [c for c in player.hand
                  if 'film' in (c.card_origin or '').lower()]
    if film_cards:
        to_trash = film_cards[0]
        player.hand.remove(to_trash)
        player.trash.append(to_trash)
        if hasattr(player, 'don_deck') and player.don_deck:
            don = player.don_deck.pop(0)
            player.don_pool.append(don)
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            return create_power_effect_choice(
                game_state, player, opponent.cards_in_play, -2000,
                source_card=card,
                prompt="Choose opponent's Character to give -2000 power"
            )
        return True
    return False


# --- OP06-020: Hody Jones (Leader) ---
@register_effect("OP06-020", "activate", "[Activate: Main] Rest Leader: Rest opponent DON or cost 3- char")
def op06_020_hody_leader(game_state, player, card):
    """Rest this Leader: Rest opponent's DON or cost 3 or less Character. Cannot add Life this turn."""
    if not card.is_resting:
        card.is_resting = True
        player.cannot_add_life_this_turn = True
        opponent = get_opponent(game_state, player)
        # Rest opponent's character with cost 3 or less
        targets = [c for c in opponent.cards_in_play
                   if not c.is_resting and (getattr(c, 'cost', 0) or 0) <= 3]
        if targets:
            return create_target_choice(
                game_state, player, targets,
                callback_action="rest_target",
                source_card=card,
                prompt="Choose opponent's cost 3 or less Character to rest"
            )
        return True
    return False


# --- OP06-021: Perona (Leader) ---
@register_effect("OP06-021", "activate", "[Activate: Main] Rest cost 4- OR give opponent char -2 cost")
def op06_021_perona_leader(game_state, player, card):
    """Once Per Turn: Rest opponent's cost 4 or less Character OR give opponent's Character -2 cost."""
    if hasattr(card, 'op06_021_used') and card.op06_021_used:
        return False
    opponent = get_opponent(game_state, player)
    rest_targets = [c for c in opponent.cards_in_play
               if not c.is_resting and (getattr(c, 'cost', 0) or 0) <= 4]

    modes = []
    if rest_targets:
        modes.append({"id": "rest", "label": "Rest cost 4 or less", "description": f"Rest 1 of {len(rest_targets)} targets"})
    if opponent.cards_in_play:
        modes.append({"id": "cost_reduce", "label": "Give -2 cost", "description": f"Give -2 cost to 1 of {len(opponent.cards_in_play)} characters"})

    if modes:
        card.op06_021_used = True
        def callback(selected: list[str]) -> None:
            selected_mode = selected[0] if selected else None
            opponent_ref = get_opponent(game_state, player)
            if selected_mode == "rest" and rest_targets:
                create_rest_choice(game_state, player, rest_targets, source_card=card,
                                   prompt="Choose opponent's cost 4 or less Character to rest")
            elif selected_mode == "cost_reduce" and opponent_ref.cards_in_play:
                create_cost_reduction_choice(
                    game_state, player, list(opponent_ref.cards_in_play), -2, source_card=card,
                    prompt="Choose opponent's Character to give -2 cost"
                )

        return create_mode_choice(
            game_state, player, modes, source_card=card, callback=callback,
            prompt="Choose Perona Leader effect"
        )
    return False


# --- OP06-022: Yamato (Leader) ---
@register_effect("OP06-022", "continuous", "[Double Attack] This Leader deals 2 damage")
def op06_022_yamato_continuous(game_state, player, card):
    """This Leader has Double Attack - deals 2 damage."""
    card.has_double_attack = True
    return True


@register_effect("OP06-022", "activate", "[Activate: Main] If opponent 3- life, give 2 DON to char")
def op06_022_yamato_activate(game_state, player, card):
    """Once Per Turn: If opponent has 3 or less Life, give up to 2 rested DON to 1 Character."""
    if hasattr(card, 'op06_022_used') and card.op06_022_used:
        return False
    opponent = get_opponent(game_state, player)
    if len(opponent.life_cards) <= 3:
        rested_don = player.don_pool.count("rested")
        if rested_don and player.cards_in_play:
            card.op06_022_used = True
            return create_don_assignment_choice(
                game_state, player, player.cards_in_play,
                source_card=card,
                prompt="Choose your Character to give up to 2 rested DON"
            )
    return False


# --- OP06-042: Vinsmoke Reiju (Leader) ---
@register_effect("OP06-042", "on_don_return", "[Your Turn] When DON returned to deck, draw 1")
def op06_042_reiju_leader(game_state, player, card):
    """Your Turn, Once Per Turn: When a DON is returned to DON deck, draw 1 card."""
    if hasattr(card, 'op06_042_used') and card.op06_042_used:
        return False
    draw_cards(player, 1)
    card.op06_042_used = True
    return True


# --- OP06-080: Gecko Moria (Leader) ---
@register_effect("OP06-080", "on_attack", "[DON!! x1] Rest 2, trash 1: Trash 2 from opponent deck")
def op06_080_moria_leader(game_state, player, card):
    """DON x1, When Attacking, Rest 2, Trash 1: Trash 2 cards from top of opponent's deck."""
    if getattr(card, 'attached_don', 0) >= 1:
        active_don = player.don_pool.count("active")
        if len(active_don) >= 2 and player.hand:
            for don in active_don[:2]:
                don.is_resting = True
            trash_from_hand(player, 1, game_state, card)
            opponent = get_opponent(game_state, player)
            for _ in range(min(2, len(opponent.deck))):
                if opponent.deck:
                    trashed = opponent.deck.pop(0)
                    opponent.trash.append(trashed)
            return True
    return False


# =============================================================================
# OP06 CHARACTER EFFECTS - Wings of the Captain
# =============================================================================

# --- OP06-002: Inazuma ---
@register_effect("OP06-002", "continuous", "If 7000+ power, gains Banish")
def op06_002_inazuma(game_state, player, card):
    """Continuous: Gains Banish if 7000+ power."""
    total_power = (getattr(card, 'power', 0) or 0) + getattr(card, 'power_modifier', 0)
    card.has_banish = total_power >= 7000
    return True


# --- OP06-003: Emporio.Ivankov ---
@register_effect("OP06-003", "on_play", "[On Play] Look at 3, play Revolutionary Army 5000 or less")
def op06_003_ivankov(game_state, player, card):
    """On Play: Look at 3 and play Revolutionary Army 5000 or less."""
    if player.deck:
        top_cards = player.deck[:3]
        for c in list(top_cards):
            if 'Revolutionary Army' in (c.card_origin or '') and (getattr(c, 'power', 0) or 0) <= 5000:
                player.deck.remove(c)
                player.cards_in_play.append(c)
                break
    return True


# --- OP06-004: Baron Omatsuri ---
@register_effect("OP06-004", "on_play", "[On Play] Play Lily Carnation from hand")
def op06_004_baron(game_state, player, card):
    """On Play: Play Lily Carnation from hand."""
    for c in list(player.hand):
        if getattr(c, 'name', '') == 'Lily Carnation':
            player.hand.remove(c)
            player.cards_in_play.append(c)
            break
    return True


# --- OP06-006: Saga ---
@register_effect("OP06-006", "on_attack", "[DON!! x1] [When Attacking] +1000 until next turn, trash FILM at end")
def op06_006_saga(game_state, player, card):
    """When Attacking with 1 DON: +1000 until next turn, trash FILM at end."""
    attached = getattr(card, 'attached_don', 0)
    if attached >= 1:
        card.power_modifier = getattr(card, 'power_modifier', 0) + 1000
        player.trash_film_eot = True
    return True


# --- OP06-007: Shanks ---
@register_effect("OP06-007", "on_play", "[On Play] K.O. 10000 power or less")
def op06_007_shanks(game_state, player, card):
    """On Play: K.O. 10000 power or less."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'power', 0) or 0) <= 10000]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                               prompt="Choose opponent's 10000 power or less Character to K.O.")
    return True


# --- OP06-009: Shuraiya ---
@register_effect("OP06-009", "blocker", "[Blocker]")
def op06_009_shuraiya_blocker(game_state, player, card):
    """Blocker ability."""
    card.has_blocker = True
    return True


@register_effect("OP06-009", "on_attack", "[When Attacking]/[On Block] [Once Per Turn] Match opponent's Leader power")
def op06_009_shuraiya_power(game_state, player, card):
    """When Attacking/On Block: Match opponent's Leader power."""
    if not getattr(card, 'op06_009_used', False):
        opponent = get_opponent(game_state, player)
        if opponent.leader:
            opp_power = (getattr(opponent.leader, 'power', 0) or 0) + getattr(opponent.leader, 'power_modifier', 0)
            current_power = (getattr(card, 'power', 0) or 0) + getattr(card, 'power_modifier', 0)
            card.power_modifier = getattr(card, 'power_modifier', 0) + (opp_power - current_power)
            card.op06_009_used = True
    return True


# --- OP06-010: Douglas Bullet ---
@register_effect("OP06-010", "continuous", "If FILM Leader, gains Blocker")
def op06_010_bullet(game_state, player, card):
    """Continuous: Gains Blocker if FILM Leader."""
    card.has_blocker = player.leader and 'FILM' in (player.leader.card_origin or '')
    return True


# --- OP06-011: Tot Musica ---
@register_effect("OP06-011", "activate", "[Activate: Main] [Once Per Turn] Rest Uta: +5000")
def op06_011_tot_musica(game_state, player, card):
    """Activate: Rest Uta to gain +5000."""
    if not getattr(card, 'op06_011_used', False):
        uta = [c for c in player.cards_in_play if 'Uta' in getattr(c, 'name', '') and not getattr(c, 'is_resting', False)]
        if uta:
            card.op06_011_used = True
            tot_ref = card
            uta_snap = list(uta)
            def tot_musica_cb(selected: list) -> None:
                target_idx = int(selected[0]) if selected else -1
                if 0 <= target_idx < len(uta_snap):
                    target = uta_snap[target_idx]
                    target.is_resting = True
                    game_state._log(f"{target.name} was rested")
                tot_ref.power_modifier = getattr(tot_ref, 'power_modifier', 0) + 5000
                game_state._log(f"{tot_ref.name} gains +5000 power")
            return create_rest_choice(game_state, player, uta, source_card=card,
                                     prompt="Choose Uta to rest (this gains +5000)",
                                     callback=tot_musica_cb)
    return False


# --- OP06-012: Bear.King ---
@register_effect("OP06-012", "continuous", "Cannot be K.O.'d in battle if opponent has 6000+ base power")
def op06_012_bearking(game_state, player, card):
    """Continuous: Cannot be K.O.'d in battle if opponent has 6000+ base power."""
    opponent = get_opponent(game_state, player)
    has_6k = (opponent.leader and (getattr(opponent.leader, 'power', 0) or 0) >= 6000) or any((getattr(c, 'power', 0) or 0) >= 6000 for c in opponent.cards_in_play)
    card.cannot_be_ko_in_battle = has_6k
    return True


# --- OP06-013: Monkey.D.Luffy ---
@register_effect("OP06-013", "on_play", "[On Play] Look at 3, add FILM card")
def op06_013_luffy_play(game_state, player, card):
    """On Play: Look at 3 and add FILM card."""
    if player.deck:
        top_cards = player.deck[:3]
        for c in top_cards:
            if 'FILM' in (c.card_origin or ''):
                player.hand.append(c)
                player.deck.remove(c)
                break
    return True


@register_effect("OP06-013", "trigger", "[Trigger] Activate On Play effect")
def op06_013_luffy_trigger(game_state, player, card):
    """Trigger: Activate On Play effect."""
    if player.deck:
        top_cards = player.deck[:3]
        for c in top_cards:
            if 'FILM' in (c.card_origin or ''):
                player.hand.append(c)
                player.deck.remove(c)
                break
    return True


# --- OP06-014: Ratchet ---
@register_effect("OP06-014", "on_opponent_attack", "[On Opponent's Attack] Trash FILM cards: +1000 per card")
def op06_014_ratchet(game_state, player, card):
    """On Opponent's Attack: Trash FILM cards for +1000 each."""
    film_cards = [c for c in player.hand if 'FILM' in (c.card_origin or '')]
    count = len(film_cards)
    for c in film_cards:
        player.hand.remove(c)
        player.trash.append(c)
    if player.leader:
        player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + (1000 * count)
    return True


# --- OP06-015: Lily Carnation ---
@register_effect("OP06-015", "activate", "[Activate: Main] [Once Per Turn] Trash 6000+ power: Play FILM 2000-5000 from trash rested")
def op06_015_lily_carnation(game_state, player, card):
    """Activate: Trash 6000+ power to play FILM 2000-5000 from trash rested."""
    if not getattr(card, 'op06_015_used', False):
        big_chars = [c for c in player.cards_in_play if (getattr(c, 'power', 0) or 0) >= 6000 and c != card]
        if big_chars:
            card.op06_015_used = True
            big_snap = list(big_chars)
            def lily_carnation_cb(selected: list) -> None:
                target_idx = int(selected[0]) if selected else -1
                if 0 <= target_idx < len(big_snap):
                    target = big_snap[target_idx]
                    if target in player.cards_in_play:
                        player.cards_in_play.remove(target)
                        player.trash.append(target)
                        game_state._log(f"{target.name} was trashed")
                film_targets = [c for c in player.trash
                               if 'film' in (c.card_origin or '').lower()
                               and getattr(c, 'card_type', '') == 'CHARACTER'
                               and 2000 <= (getattr(c, 'power', 0) or 0) <= 5000]
                if film_targets:
                    create_play_from_trash_choice(game_state, player, film_targets,
                                                  source_card=None,
                                                  rest_on_play=True,
                                                  prompt="Choose FILM Character (2000-5000 power) from trash to play rested")
            return create_ko_choice(game_state, player, big_chars, source_card=card,
                                   prompt="Choose your 6000+ power Character to trash",
                                   callback=lily_carnation_cb)
    return False


# --- OP06-016: Raise Max ---
@register_effect("OP06-016", "activate", "[Activate: Main] Bottom this: -3000 power")
def op06_016_raise_max(game_state, player, card):
    """Activate: Place this at deck bottom to give -3000 power."""
    if card in player.cards_in_play:
        player.cards_in_play.remove(card)
        player.deck.append(card)
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            return create_power_reduction_choice(game_state, player, list(opponent.cards_in_play), -3000, source_card=card,
                                                prompt="Choose opponent's Character to give -3000 power")
        return True
    return False


# --- OP06-023: Arlong ---
@register_effect("OP06-023", "on_play", "[On Play] Trash 1: Opponent's rested Leader cannot attack")
def op06_023_arlong_play(game_state, player, card):
    """On Play: Trash 1 to prevent opponent's rested Leader from attacking."""
    if player.hand:
        trash_from_hand(player, 1, game_state, card)
        opponent = get_opponent(game_state, player)
        if opponent.leader and getattr(opponent.leader, 'is_resting', False):
            opponent.leader.cannot_attack = True
    return True


@register_effect("OP06-023", "trigger", "[Trigger] Rest cost 4 or less")
def op06_023_arlong_trigger(game_state, player, card):
    """Trigger: Rest cost 4 or less."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
    if targets:
        return create_rest_choice(game_state, player, targets, source_card=card,
                                 prompt="Choose opponent's cost 4 or less Character to rest")
    return True


# --- OP06-024: Ikaros Much ---
@register_effect("OP06-024", "on_play", "[On Play] If New Fish-Man Pirates leader, play Fish-Man cost 4 or less, add 1 life to hand")
def op06_024_ikaros_much(game_state, player, card):
    """On Play: If Leader has New Fish-Man Pirates type, play Fish-Man cost 4 or less from hand."""
    if player.leader and 'New Fish-Man Pirates' in (player.leader.card_origin or ''):
        # Play Fish-Man cost 4 or less from hand
        for c in list(player.hand):
            if 'Fish-Man' in (c.card_origin or '') and (getattr(c, 'cost', 0) or 0) <= 4:
                player.hand.remove(c)
                player.cards_in_play.append(c)
                break
        # Add 1 life to hand
        if player.life_cards:
            life_card = player.life_cards.pop()
            player.hand.append(life_card)
    return True


# --- OP06-025: Camie ---
@register_effect("OP06-025", "on_play", "[On Play] Look at 4 cards, add Fish-Man or Merfolk to hand")
def op06_025_camie(game_state, player, card):
    """On Play: Look at 4 cards from deck, add Fish-Man or Merfolk to hand."""
    looked = player.deck[:4] if len(player.deck) >= 4 else player.deck[:]
    for c in looked:
        types = (c.card_origin or '')
        if ('Fish-Man' in types or 'Merfolk' in types) and getattr(c, 'name', '') != 'Camie':
            player.deck.remove(c)
            player.hand.append(c)
            break
    return True


# --- OP06-026: Koushirou ---
@register_effect("OP06-026", "on_play", "[On Play] Set Slash cost 4 or less active, cannot attack Leader this turn")
def op06_026_koushirou(game_state, player, card):
    """On Play: Set Slash attribute cost 4 or less as active, cannot attack Leader this turn."""
    for c in player.cards_in_play:
        if getattr(c, 'attribute', '') == 'Slash' and (getattr(c, 'cost', 0) or 0) <= 4:
            c.is_resting = False
            break
    player.cannot_attack_leader = True
    return True


# --- OP06-027: Gyro ---
@register_effect("OP06-027", "on_ko", "[On K.O.] Rest opponent's cost 3 or less")
def op06_027_gyro(game_state, player, card):
    """On K.O.: Rest opponent's Character cost 3 or less."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
    if targets:
        return create_rest_choice(game_state, player, targets, source_card=card,
                                 prompt="Choose opponent's cost 3 or less Character to rest")
    return True


# --- OP06-028: Zeo ---
@register_effect("OP06-028", "on_attack", "[DON!! x1] [When Attacking] If New Fish-Man Pirates leader, set DON active, +1000, add life to hand")
def op06_028_zeo(game_state, player, card):
    """When Attacking: With DON, set DON active, +1000 power, add life to hand."""
    if getattr(card, 'attached_don', 0) >= 1:
        if player.leader and 'New Fish-Man Pirates' in (player.leader.card_origin or ''):
            # Set DON active
            for don in player.don_pool:
                if getattr(don, 'is_resting', False):
                    don.is_resting = False
                    break
            card.power_modifier = getattr(card, 'power_modifier', 0) + 1000
            # Add life to hand
            if player.life_cards:
                life_card = player.life_cards.pop()
                player.hand.append(life_card)
    return True


# --- OP06-029: Daruma ---
@register_effect("OP06-029", "on_attack", "[DON!! x1] [When Attacking] [Once Per Turn] If New Fish-Man Pirates leader, set active, +1000, add life")
def op06_029_daruma(game_state, player, card):
    """When Attacking: Once per turn with DON, set self active, +1000, add life."""
    if getattr(card, 'op06_029_used', False):
        return False
    if getattr(card, 'attached_don', 0) >= 1:
        if player.leader and 'New Fish-Man Pirates' in (player.leader.card_origin or ''):
            card.is_resting = False
            card.power_modifier = getattr(card, 'power_modifier', 0) + 1000
            if player.life_cards:
                life_card = player.life_cards.pop()
                player.hand.append(life_card)
            card.op06_029_used = True
            return True
    return False


# --- OP06-030: Dosun ---
@register_effect("OP06-030", "on_attack", "[When Attacking] If New Fish-Man Pirates leader, cannot be K.O.'d, +2000 until next turn, add life")
def op06_030_dosun(game_state, player, card):
    """When Attacking: Cannot be K.O.'d in battle, +2000 until next turn, add life."""
    if player.leader and 'New Fish-Man Pirates' in (player.leader.card_origin or ''):
        card.cannot_be_ko_in_battle = True
        card.power_modifier = getattr(card, 'power_modifier', 0) + 2000
        if player.life_cards:
            life_card = player.life_cards.pop()
            player.hand.append(life_card)
    return True


# --- OP06-031: Hatchan ---
@register_effect("OP06-031", "trigger", "[Trigger] Play Fish-Man or Merfolk cost 3 or less from hand")
def op06_031_hatchan(game_state, player, card):
    """Trigger: Play Fish-Man or Merfolk cost 3 or less from hand."""
    for c in list(player.hand):
        types = (c.card_origin or '')
        if ('Fish-Man' in types or 'Merfolk' in types) and (getattr(c, 'cost', 0) or 0) <= 3:
            player.hand.remove(c)
            player.cards_in_play.append(c)
            break
    return True


# --- OP06-032: Hammond ---
@register_effect("OP06-032", "blocker", "[Blocker]")
def op06_032_hammond(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


# --- OP06-033: Vander Decken IX ---
@register_effect("OP06-033", "on_play", "[On Play] Trash Fish-Man from hand/Ark Noah: K.O. opponent's rested Character")
def op06_033_vander_decken(game_state, player, card):
    """On Play: Trash Fish-Man or Ark Noah to K.O. opponent's rested Character."""
    trashed = False
    for c in list(player.hand):
        if 'Fish-Man' in (c.card_origin or '') or getattr(c, 'name', '') == 'The Ark Noah':
            player.hand.remove(c)
            player.trash.append(c)
            trashed = True
            break
    if not trashed:
        for c in list(player.cards_in_play):
            if getattr(c, 'name', '') == 'The Ark Noah':
                player.cards_in_play.remove(c)
                player.trash.append(c)
                trashed = True
                break
    if trashed:
        opponent = get_opponent(game_state, player)
        rested = [c for c in opponent.cards_in_play if getattr(c, 'is_resting', False)]
        if rested:
            return create_ko_choice(game_state, player, rested, source_card=card,
                                   prompt="Choose opponent's rested Character to K.O.")
    return True


# --- OP06-034: Hyouzou ---
@register_effect("OP06-034", "activate", "[Activate: Main] [Once Per Turn] Rest opponent's cost 4 or less, +1000, add life")
def op06_034_hyouzou(game_state, player, card):
    """Activate: Rest opponent's cost 4 or less, gain +1000, add life to hand."""
    if getattr(card, 'op06_034_used', False):
        return False
    card.power_modifier = getattr(card, 'power_modifier', 0) + 1000
    if player.life_cards:
        life_card = player.life_cards.pop()
        player.hand.append(life_card)
    card.op06_034_used = True
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
    if targets:
        return create_rest_choice(game_state, player, targets, source_card=card,
                                 prompt="Choose opponent's cost 4 or less Character to rest")
    return True


# --- OP06-035: Hody Jones ---
@register_effect("OP06-035", "continuous", "[Rush]")
def op06_035_hody_rush(game_state, player, card):
    """Rush."""
    card.has_rush = True
    return True


@register_effect("OP06-035", "on_play", "[On Play] Rest up to 2 Characters or DON, add life to hand")
def op06_035_hody_play(game_state, player, card):
    """On Play: Rest up to 2 Characters or DON, add life to hand."""
    opponent = get_opponent(game_state, player)
    targets = opponent.cards_in_play + opponent.don_pool
    rested = 0
    for t in targets:
        if rested >= 2:
            break
        if not getattr(t, 'is_resting', False):
            t.is_resting = True
            rested += 1
    if player.life_cards:
        life_card = player.life_cards.pop()
        player.hand.append(life_card)
    return True


# --- OP06-036: Ryuma ---
@register_effect("OP06-036", "on_play", "[On Play]/[On K.O.] K.O. opponent's rested cost 4 or less")
def op06_036_ryuma_play(game_state, player, card):
    """On Play: K.O. opponent's rested cost 4 or less."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if getattr(c, 'is_resting', False) and (getattr(c, 'cost', 0) or 0) <= 4]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                               prompt="Choose opponent's rested cost 4 or less Character to K.O.")
    return True


@register_effect("OP06-036", "on_ko", "[On K.O.] K.O. opponent's rested cost 4 or less")
def op06_036_ryuma_ko(game_state, player, card):
    """On K.O.: K.O. opponent's rested cost 4 or less."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if getattr(c, 'is_resting', False) and (getattr(c, 'cost', 0) or 0) <= 4]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                               prompt="Choose opponent's rested cost 4 or less Character to K.O.")
    return True


# --- OP06-037: Wadatsumi ---
# No effect (vanilla 8000 power)


# --- OP06-043: Aramaki ---
@register_effect("OP06-043", "blocker", "[Blocker]")
def op06_043_aramaki_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP06-043", "activate", "[Activate: Main] [Once Per Turn] Trash 1, bottom cost 2 or less: +3000")
def op06_043_aramaki_activate(game_state, player, card):
    """Activate: Trash 1 and bottom a cost 2 or less for +3000."""
    if getattr(card, 'op06_043_used', False):
        return False
    if player.hand:
        trash_from_hand(player, 1, game_state, card)
        card.power_modifier = getattr(card, 'power_modifier', 0) + 3000
        card.op06_043_used = True
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
        if targets:
            return create_bottom_deck_choice(game_state, player, targets, source_card=card,
                                            prompt="Choose opponent's cost 2 or less to place at deck bottom")
        return True
    return False


# --- OP06-044: Gion ---
@register_effect("OP06-044", "continuous", "[Your Turn] When opponent activates Event, they bottom 1 card")
def op06_044_gion(game_state, player, card):
    """Continuous: When opponent activates Event, they bottom 1 card."""
    card.gion_effect = True
    return True


# --- OP06-045: Kuzan ---
@register_effect("OP06-045", "on_play", "[On Play] Draw 2, place 2 at bottom")
def op06_045_kuzan(game_state, player, card):
    """On Play: Draw 2 cards, place 2 at deck bottom."""
    draw_cards(player, 2)
    for _ in range(min(2, len(player.hand))):
        if player.hand:
            c = player.hand.pop()
            player.deck.append(c)
    return True


# --- OP06-046: Sakazuki ---
@register_effect("OP06-046", "on_play", "[On Play] Place cost 2 or less at deck bottom")
def op06_046_sakazuki(game_state, player, card):
    """On Play: Place a cost 2 or less at deck bottom."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
    if targets:
        return create_bottom_deck_choice(game_state, player, targets, source_card=card,
                                        prompt="Choose opponent's cost 2 or less to place at deck bottom")
    return True


# --- OP06-047: Charlotte Pudding ---
@register_effect("OP06-047", "on_play", "[On Play] Opponent returns hand to deck, shuffles, draws 5")
def op06_047_charlotte_pudding(game_state, player, card):
    """On Play: Opponent returns hand to deck, shuffles, draws 5."""
    opponent = get_opponent(game_state, player)
    while opponent.hand:
        c = opponent.hand.pop()
        opponent.deck.append(c)
    import random
    random.shuffle(opponent.deck)
    draw_cards(opponent, 5)
    return True


# --- OP06-048: Zeff ---
@register_effect("OP06-048", "continuous", "[Your Turn] When opponent uses Blocker/Event, if East Blue leader, trash 4 from deck")
def op06_048_zeff(game_state, player, card):
    """Continuous: When opponent activates Blocker/Event, trash 4 from deck."""
    if player.leader and 'East Blue' in (player.leader.card_origin or ''):
        card.zeff_effect = True
    return True


# --- OP06-049: Sengoku ---
# No effect (vanilla 7000 power)


# --- OP06-050: Tashigi ---
@register_effect("OP06-050", "on_play", "[On Play] Look at 5 cards, add Navy to hand")
def op06_050_tashigi(game_state, player, card):
    """On Play: Look at 5 cards from deck, add Navy to hand."""
    looked = player.deck[:5] if len(player.deck) >= 5 else player.deck[:]
    for c in looked:
        if 'Navy' in (c.card_origin or '') and getattr(c, 'name', '') != 'Tashigi':
            player.deck.remove(c)
            player.hand.append(c)
            break
    return True


# --- OP06-051: Tsuru ---
@register_effect("OP06-051", "on_play", "[On Play] Trash 2 from hand: Opponent returns 1 Character to hand")
def op06_051_tsuru(game_state, player, card):
    """On Play: Trash 2 to make opponent return a Character to hand."""
    if len(player.hand) >= 2:
        trash_from_hand(player, 2, game_state, card)
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            target = opponent.cards_in_play.pop()
            opponent.hand.append(target)
    return True


# --- OP06-052: Tokikake ---
@register_effect("OP06-052", "continuous", "[DON!! x1] If 4 or less cards in hand, cannot be K.O.'d in battle")
def op06_052_tokikake(game_state, player, card):
    """Continuous: With DON, if 4 or less in hand, cannot be K.O.'d in battle."""
    if getattr(card, 'attached_don', 0) >= 1 and len(player.hand) <= 4:
        card.cannot_be_ko_in_battle = True
    return True


# --- OP06-053: Jaguar.D.Saul ---
@register_effect("OP06-053", "on_ko", "[On K.O.] Place cost 2 or less at deck bottom")
def op06_053_jaguar_d_saul(game_state, player, card):
    """On K.O.: Place cost 2 or less at deck bottom."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
    if targets:
        return create_bottom_deck_choice(game_state, player, targets, source_card=card,
                                        prompt="Choose opponent's cost 2 or less to place at deck bottom")
    return True


# --- OP06-054: Borsalino ---
@register_effect("OP06-054", "continuous", "If 5 or less cards in hand, gains [Blocker]")
def op06_054_borsalino(game_state, player, card):
    """Continuous: If 5 or less cards in hand, has Blocker."""
    if len(player.hand) <= 5:
        card.has_blocker = True
    return True


# --- OP06-055: Monkey.D.Garp ---
@register_effect("OP06-055", "on_attack", "[DON!! x2] [When Attacking] If 4 or less in hand, opponent cannot use Blocker")
def op06_055_garp(game_state, player, card):
    """When Attacking: With 2 DON, if 4 or less in hand, opponent cannot Blocker."""
    if getattr(card, 'attached_don', 0) >= 2 and len(player.hand) <= 4:
        opponent = get_opponent(game_state, player)
        for c in opponent.cards_in_play:
            c.blocker_disabled = True
    return True


# --- OP06-060: Vinsmoke Ichiji (4-cost) ---
@register_effect("OP06-060", "activate", "[Activate: Main] DON -1, trash this: Play 7-cost Ichiji from hand/trash")
def op06_060_ichiji(game_state, player, card):
    """Activate: DON -1, trash this to play 7-cost Ichiji."""
    if player.don_pool:
        don = player.don_pool.pop()
        player.don_deck.append(don)
        if card in player.cards_in_play:
            player.cards_in_play.remove(card)
            player.trash.append(card)
        if player.leader and 'GERMA 66' in (player.leader.card_origin or ''):
            # Check hand for 7-cost Ichiji
            for c in list(player.hand):
                if getattr(c, 'name', '') == 'Vinsmoke Ichiji' and (getattr(c, 'cost', 0) or 0) == 7:
                    player.hand.remove(c)
                    player.cards_in_play.append(c)
                    return True
            # Check trash for 7-cost Ichiji
            for c in list(player.trash):
                if getattr(c, 'name', '') == 'Vinsmoke Ichiji' and (getattr(c, 'cost', 0) or 0) == 7:
                    player.trash.remove(c)
                    player.cards_in_play.append(c)
                    return True
    return False


# --- OP06-061: Vinsmoke Ichiji (7-cost) ---
@register_effect("OP06-061", "on_play", "[On Play] If DON <= opponent's DON, -2000 to opponent, gain Rush")
def op06_061_ichiji(game_state, player, card):
    """On Play: If less DON than opponent, -2000 to opponent's Character, gain Rush."""
    opponent = get_opponent(game_state, player)
    player_don = len(player.don_pool)
    opponent_don = len(opponent.don_pool)
    if player_don <= opponent_don:
        card.has_rush = True
        if opponent.cards_in_play:
            return create_power_reduction_choice(game_state, player, list(opponent.cards_in_play), 2000,
                                                source_card=card, prompt="Choose opponent's Character for -2000 power")
    return True


# --- OP06-062: Vinsmoke Judge ---
@register_effect("OP06-062", "on_play", "[On Play] DON -1, trash 2: Play up to 4 GERMA 66 4000 power from trash")
def op06_062_judge_play(game_state, player, card):
    """On Play: DON -1, trash 2 to play up to 4 GERMA 66 4000 power from trash."""
    if player.don_pool and len(player.hand) >= 2:
        don = player.don_pool.pop()
        player.don_deck.append(don)
        trash_from_hand(player, 2, game_state, card)
        # Play up to 4 GERMA 66 with different names and 4000 power or less
        played_names = []
        for c in list(player.trash):
            if len(played_names) >= 4:
                break
            if 'GERMA 66' in (c.card_origin or ''):
                power = getattr(c, 'power', 0) or 0
                name = getattr(c, 'name', '')
                if power <= 4000 and name not in played_names:
                    player.trash.remove(c)
                    player.cards_in_play.append(c)
                    played_names.append(name)
    return True


@register_effect("OP06-062", "activate", "[Activate: Main] [Once Per Turn] DON -1: Rest opponent's DON")
def op06_062_judge_activate(game_state, player, card):
    """Activate: DON -1 to rest opponent's DON."""
    if getattr(card, 'op06_062_used', False):
        return False
    if player.don_pool:
        don = player.don_pool.pop()
        player.don_deck.append(don)
        opponent = get_opponent(game_state, player)
        for opp_don in opponent.don_pool:
            if not getattr(opp_don, 'is_resting', False):
                opp_don.is_resting = True
                break
        card.op06_062_used = True
        return True
    return False


# --- OP06-063: Vinsmoke Sora ---
@register_effect("OP06-063", "on_play", "[On Play] Trash 1: If DON <= opponent, add Vinsmoke 4000 power from trash")
def op06_063_sora(game_state, player, card):
    """On Play: Trash 1, if DON <= opponent, add Vinsmoke 4000 power from trash to hand."""
    if player.hand:
        trash_from_hand(player, 1, game_state, card)
        opponent = get_opponent(game_state, player)
        if len(player.don_pool) <= len(opponent.don_pool):
            for c in list(player.trash):
                if 'The Vinsmoke Family' in (c.card_origin or ''):
                    power = getattr(c, 'power', 0) or 0
                    if power <= 4000:
                        player.trash.remove(c)
                        player.hand.append(c)
                        break
    return True


# --- OP06-064: Vinsmoke Niji (3-cost) ---
@register_effect("OP06-064", "activate", "[Activate: Main] DON -1, trash this: Play 5-cost Niji from hand/trash")
def op06_064_niji(game_state, player, card):
    """Activate: DON -1, trash this to play 5-cost Niji."""
    if player.don_pool:
        don = player.don_pool.pop()
        player.don_deck.append(don)
        if card in player.cards_in_play:
            player.cards_in_play.remove(card)
            player.trash.append(card)
        if player.leader and 'GERMA 66' in (player.leader.card_origin or ''):
            for c in list(player.hand):
                if getattr(c, 'name', '') == 'Vinsmoke Niji' and (getattr(c, 'cost', 0) or 0) == 5:
                    player.hand.remove(c)
                    player.cards_in_play.append(c)
                    return True
            for c in list(player.trash):
                if getattr(c, 'name', '') == 'Vinsmoke Niji' and (getattr(c, 'cost', 0) or 0) == 5:
                    player.trash.remove(c)
                    player.cards_in_play.append(c)
                    return True
    return False


# --- OP06-065: Vinsmoke Niji (5-cost) ---
@register_effect("OP06-065", "on_play", "[On Play] If DON <= opponent, K.O. cost 2 or return cost 4 to hand")
def op06_065_niji(game_state, player, card):
    """On Play: If DON <= opponent, K.O. cost 2 or less OR return cost 4 or less to hand."""
    opponent = get_opponent(game_state, player)
    if len(player.don_pool) <= len(opponent.don_pool):
        ko_targets = filter_by_max_cost(opponent.cards_in_play, 2)
        return_targets = filter_by_max_cost(opponent.cards_in_play, 4)
        if ko_targets or return_targets:
            def callback(selected: list[str]) -> None:
                selected_mode = selected[0] if selected else None
                if selected_mode == "ko" and ko_targets:
                    create_ko_choice(game_state, player, ko_targets, source_card=card,
                                     prompt="Choose opponent's cost 2 or less Character to K.O.")
                elif selected_mode == "return" and return_targets:
                    create_return_to_hand_choice(game_state, player, return_targets, source_card=card,
                                                 prompt="Choose opponent's cost 4 or less Character to return to hand")

            return create_mode_choice(game_state, player, source_card=card,
                                     options=[
                                         ("ko", "K.O. cost 2 or less", ko_targets),
                                         ("return", "Return cost 4 or less to hand", return_targets)
                                     ],
                                     callback=callback,
                                     prompt="Choose effect mode for Vinsmoke Niji")
    return True


# --- OP06-066: Vinsmoke Yonji (2-cost) ---
@register_effect("OP06-066", "activate", "[Activate: Main] DON -1, trash this: Play 4-cost Yonji from hand/trash")
def op06_066_yonji(game_state, player, card):
    """Activate: DON -1, trash this to play 4-cost Yonji."""
    if player.don_pool:
        don = player.don_pool.pop()
        player.don_deck.append(don)
        if card in player.cards_in_play:
            player.cards_in_play.remove(card)
            player.trash.append(card)
        if player.leader and 'GERMA 66' in (player.leader.card_origin or ''):
            for c in list(player.hand):
                if getattr(c, 'name', '') == 'Vinsmoke Yonji' and (getattr(c, 'cost', 0) or 0) == 4:
                    player.hand.remove(c)
                    player.cards_in_play.append(c)
                    return True
            for c in list(player.trash):
                if getattr(c, 'name', '') == 'Vinsmoke Yonji' and (getattr(c, 'cost', 0) or 0) == 4:
                    player.trash.remove(c)
                    player.cards_in_play.append(c)
                    return True
    return False


# --- OP06-067: Vinsmoke Yonji (4-cost) ---
@register_effect("OP06-067", "continuous", "If DON <= opponent, +1000 power")
def op06_067_yonji_power(game_state, player, card):
    """Continuous: If DON <= opponent, +1000 power."""
    opponent = get_opponent(game_state, player)
    if len(player.don_pool) <= len(opponent.don_pool):
        card.power_modifier = getattr(card, 'power_modifier', 0) + 1000
    return True


@register_effect("OP06-067", "blocker", "[Blocker]")
def op06_067_yonji_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


# --- OP06-068: Vinsmoke Reiju (2-cost) ---
@register_effect("OP06-068", "activate", "[Activate: Main] DON -1, trash this: Play 4-cost Reiju from hand/trash")
def op06_068_reiju(game_state, player, card):
    """Activate: DON -1, trash this to play 4-cost Reiju."""
    if player.don_pool:
        don = player.don_pool.pop()
        player.don_deck.append(don)
        if card in player.cards_in_play:
            player.cards_in_play.remove(card)
            player.trash.append(card)
        if player.leader and 'GERMA 66' in (player.leader.card_origin or ''):
            for c in list(player.hand):
                if getattr(c, 'name', '') == 'Vinsmoke Reiju' and (getattr(c, 'cost', 0) or 0) == 4:
                    player.hand.remove(c)
                    player.cards_in_play.append(c)
                    return True
            for c in list(player.trash):
                if getattr(c, 'name', '') == 'Vinsmoke Reiju' and (getattr(c, 'cost', 0) or 0) == 4:
                    player.trash.remove(c)
                    player.cards_in_play.append(c)
                    return True
    return False


# --- OP06-069: Vinsmoke Reiju (4-cost) ---
@register_effect("OP06-069", "on_play", "[On Play] If DON <= opponent and 5 or less in hand, draw 2")
def op06_069_reiju(game_state, player, card):
    """On Play: If DON <= opponent and 5 or less in hand, draw 2."""
    opponent = get_opponent(game_state, player)
    if len(player.don_pool) <= len(opponent.don_pool) and len(player.hand) <= 5:
        draw_cards(player, 2)
    return True


# --- OP06-070: Eldoraggo ---
# No effect (vanilla 7000 power)


# --- OP06-071: Gild Tesoro ---
@register_effect("OP06-071", "on_play", "[On Play] DON -1: If FILM leader, add 2 FILM cost 4 or less from trash")
def op06_071_tesoro(game_state, player, card):
    """On Play: DON -1 to add 2 FILM cost 4 or less from trash to hand."""
    if player.don_pool:
        don = player.don_pool.pop()
        player.don_deck.append(don)
        if player.leader and 'FILM' in (player.leader.card_origin or ''):
            added = 0
            for c in list(player.trash):
                if added >= 2:
                    break
                if 'FILM' in (c.card_origin or '') and (getattr(c, 'cost', 0) or 0) <= 4:
                    player.trash.remove(c)
                    player.hand.append(c)
                    added += 1
            return True
    return False


# --- OP06-072: Cosette ---
@register_effect("OP06-072", "continuous", "If GERMA 66 leader and DON at least 2 less than opponent, gains Blocker")
def op06_072_cosette(game_state, player, card):
    """Continuous: If GERMA leader and DON 2+ less than opponent, has Blocker."""
    if player.leader and 'GERMA 66' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        if len(player.don_pool) <= len(opponent.don_pool) - 2:
            card.has_blocker = True
    return True


# --- OP06-073: Shiki ---
@register_effect("OP06-073", "blocker", "[Blocker]")
def op06_073_shiki_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP06-073", "on_play", "[On Play] If 8+ DON on field, draw 1, trash 1")
def op06_073_shiki_play(game_state, player, card):
    """On Play: If 8+ DON on field, draw 1 and trash 1."""
    if len(player.don_pool) >= 8:
        draw_cards(player, 1)
        if player.hand:
            trash_from_hand(player, 1, game_state, card)
    return True


# --- OP06-074: Zephyr ---
@register_effect("OP06-074", "on_play", "[On Play] DON -1: Negate opponent's Character effect, if 5000 or less K.O.")
def op06_074_zephyr(game_state, player, card):
    """On Play: DON -1 to negate effect and K.O. if 5000 or less."""
    if player.don_pool:
        don = player.don_pool.pop()
        player.don_deck.append(don)
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            return create_negate_and_ko_choice(game_state, player, list(opponent.cards_in_play), 5000,
                                              source_card=card, prompt="Choose opponent's Character to negate effect (K.O. if 5000 or less)")
        return True
    return False


# --- OP06-075: Count Battler ---
@register_effect("OP06-075", "on_play", "[On Play] DON -1: Rest up to 2 opponent's cost 2 or less")
def op06_075_count_battler(game_state, player, card):
    """On Play: DON -1 to rest up to 2 opponent's cost 2 or less."""
    if player.don_pool:
        don = player.don_pool.pop()
        player.don_deck.append(don)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
        if targets:
            return create_multi_rest_choice(game_state, player, targets, max_targets=2,
                                           source_card=card, prompt="Choose up to 2 cost 2 or less to rest")
        return True
    return False


# --- OP06-076: Hitokiri Kamazo ---
@register_effect("OP06-076", "continuous", "[Your Turn] [Once Per Turn] When DON returned to deck, K.O. cost 2 or less")
def op06_076_kamazo(game_state, player, card):
    """Continuous: When DON returned to deck, K.O. cost 2 or less."""
    card.kamazo_effect = True
    return True


# --- OP06-081: Absalom ---
@register_effect("OP06-081", "on_play", "[On Play] Return 2 from trash to deck: K.O. cost 2 or less")
def op06_081_absalom(game_state, player, card):
    """On Play: Return 2 from trash to deck to K.O. cost 2 or less."""
    if len(player.trash) >= 2:
        for _ in range(2):
            c = player.trash.pop()
            player.deck.append(c)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's cost 2 or less to K.O.")
    return True


# --- OP06-082: Inuppe ---
@register_effect("OP06-082", "on_play", "[On Play]/[On K.O.] If Thriller Bark Pirates leader, draw 2, trash 2")
def op06_082_inuppe_play(game_state, player, card):
    """On Play: If Thriller Bark Pirates leader, draw 2 and trash 2."""
    if player.leader and 'Thriller Bark Pirates' in (player.leader.card_origin or ''):
        draw_cards(player, 2)
        trash_from_hand(player, 2, game_state, card)
    return True


@register_effect("OP06-082", "on_ko", "[On K.O.] If Thriller Bark Pirates leader, draw 2, trash 2")
def op06_082_inuppe_ko(game_state, player, card):
    """On K.O.: If Thriller Bark Pirates leader, draw 2 and trash 2."""
    if player.leader and 'Thriller Bark Pirates' in (player.leader.card_origin or ''):
        draw_cards(player, 2)
        trash_from_hand(player, 2, game_state, card)
    return True


# --- OP06-083: Oars ---
@register_effect("OP06-083", "continuous", "Cannot attack")
def op06_083_oars_cant_attack(game_state, player, card):
    """Continuous: Cannot attack."""
    card.cannot_attack = True
    return True


@register_effect("OP06-083", "activate", "[Activate: Main] K.O. Thriller Bark Pirates: Negate own effect this turn")
def op06_083_oars_activate(game_state, player, card):
    """Activate: K.O. Thriller Bark Pirates to negate own effect this turn."""
    targets = [c for c in player.cards_in_play if c != card and 'Thriller Bark Pirates' in (c.card_origin or '')]
    if targets:
        def oars_ko_callback(game_state, player, selected):
            if selected and selected in player.cards_in_play:
                player.cards_in_play.remove(selected)
                player.trash.append(selected)
                card.effects_negated = True
                card.cannot_attack = False
            return True
        return create_target_choice(game_state, player, targets, oars_ko_callback, source_card=card,
                                   prompt="Choose your Thriller Bark Pirates to K.O.")
    return False


# --- OP06-084: Jigoro of the Wind ---
@register_effect("OP06-084", "on_ko", "[On K.O.] +1000 power to Leader or Character")
def op06_084_jigoro(game_state, player, card):
    """On K.O.: Give +1000 power to Leader or Character."""
    if player.leader:
        player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 1000
    return True


# --- OP06-085: Kumacy ---
@register_effect("OP06-085", "continuous", "[DON!! x2] [Your Turn] +1000 power for every 5 cards in trash")
def op06_085_kumacy(game_state, player, card):
    """Continuous: With 2 DON, +1000 power per 5 cards in trash."""
    if getattr(card, 'attached_don', 0) >= 2:
        trash_count = len(player.trash)
        bonus = (trash_count // 5) * 1000
        card.power_modifier = getattr(card, 'power_modifier', 0) + bonus
    return True


# --- OP06-086: Gecko Moria ---
@register_effect("OP06-086", "on_play", "[On Play] Play cost 4 or less and cost 2 or less from trash")
def op06_086_gecko_moria(game_state, player, card):
    """On Play: Play cost 4 or less and cost 2 or less from trash."""
    cost4_target = None
    cost2_target = None
    for c in list(player.trash):
        cost = getattr(c, 'cost', 0) or 0
        if cost <= 4 and cost4_target is None:
            cost4_target = c
        elif cost <= 2 and cost2_target is None:
            cost2_target = c
    if cost4_target:
        player.trash.remove(cost4_target)
        player.cards_in_play.append(cost4_target)
    if cost2_target:
        player.trash.remove(cost2_target)
        cost2_target.is_resting = True
        player.cards_in_play.append(cost2_target)
    return True


# --- OP06-087: Cerberus ---
@register_effect("OP06-087", "blocker", "[Blocker]")
def op06_087_cerberus(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


# --- OP06-088: Sai ---
@register_effect("OP06-088", "continuous", "If Dressrosa leader is active, +2000 power")
def op06_088_sai(game_state, player, card):
    """Continuous: If Dressrosa leader is active, +2000 power."""
    if player.leader and 'Dressrosa' in (player.leader.card_origin or ''):
        if not getattr(player.leader, 'is_resting', False):
            card.power_modifier = getattr(card, 'power_modifier', 0) + 2000
    return True


# --- OP06-089: Taralan ---
@register_effect("OP06-089", "on_play", "[On Play]/[On K.O.] Trash 3 from top of deck")
def op06_089_taralan_play(game_state, player, card):
    """On Play: Trash 3 from top of deck."""
    for _ in range(min(3, len(player.deck))):
        c = player.deck.pop(0)
        player.trash.append(c)
    return True


@register_effect("OP06-089", "on_ko", "[On K.O.] Trash 3 from top of deck")
def op06_089_taralan_ko(game_state, player, card):
    """On K.O.: Trash 3 from top of deck."""
    for _ in range(min(3, len(player.deck))):
        c = player.deck.pop(0)
        player.trash.append(c)
    return True


# --- OP06-090: Dr. Hogback ---
@register_effect("OP06-090", "on_play", "[On Play] Return 2 from trash to deck: Add Thriller Bark Pirates from trash")
def op06_090_hogback(game_state, player, card):
    """On Play: Return 2 from trash to deck to add Thriller Bark Pirates from trash to hand."""
    if len(player.trash) >= 2:
        for _ in range(2):
            c = player.trash.pop()
            player.deck.append(c)
        for c in list(player.trash):
            if 'Thriller Bark Pirates' in (c.card_origin or '') and getattr(c, 'name', '') != 'Dr. Hogback':
                player.trash.remove(c)
                player.hand.append(c)
                break
    return True


# --- OP06-091: Victoria Cindry ---
@register_effect("OP06-091", "on_play", "[On Play] If Thriller Bark Pirates leader, trash 5 from deck")
def op06_091_victoria_cindry(game_state, player, card):
    """On Play: If Thriller Bark Pirates leader, trash 5 from deck."""
    if player.leader and 'Thriller Bark Pirates' in (player.leader.card_origin or ''):
        for _ in range(min(5, len(player.deck))):
            c = player.deck.pop(0)
            player.trash.append(c)
    return True


# --- OP06-092: Brook ---
@register_effect("OP06-092", "on_play", "[On Play] Trash opponent's cost 4 or less OR opponent bottoms 3 from trash")
def op06_092_brook(game_state, player, card):
    """On Play: Trash opponent's cost 4 or less OR opponent bottoms 3 from trash."""
    opponent = get_opponent(game_state, player)
    ko_targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
    def callback(selected: list[str]) -> None:
        selected_mode = selected[0] if selected else None
        opponent_ref = get_opponent(game_state, player)
        if selected_mode == "ko" and ko_targets:
            create_ko_choice(game_state, player, ko_targets, source_card=card,
                             prompt="Choose opponent's cost 4 or less Character to K.O.")
        elif selected_mode == "bottom":
            moved = 0
            for trashed in list(opponent_ref.trash):
                if moved >= 3:
                    break
                opponent_ref.trash.remove(trashed)
                opponent_ref.deck.append(trashed)
                moved += 1
            if moved:
                game_state._log(f"{opponent_ref.name} placed {moved} card(s) from trash at the bottom of deck")

    return create_mode_choice(game_state, player, source_card=card,
                             options=[
                                 ("ko", "Trash cost 4 or less", ko_targets),
                                 ("bottom", "Opponent bottoms 3 from trash", [])
                             ],
                             callback=callback,
                             prompt="Choose effect mode for Brook")


# --- OP06-093: Perona ---
@register_effect("OP06-093", "on_play", "[On Play] If opponent has 5+ cards, they trash 1 OR -3 cost to Character")
def op06_093_perona(game_state, player, card):
    """On Play: If opponent has 5+ in hand, they trash 1 OR give -3 cost."""
    opponent = get_opponent(game_state, player)
    if len(opponent.hand) >= 5:
        # Default: Opponent trashes 1
        if opponent.hand:
            trash_from_hand(opponent, 1)
    return True


# --- OP06-094: Lola ---
# No effect (vanilla 6000 power)


# --- OP06-099: Aisa ---
@register_effect("OP06-099", "on_play", "[On Play] Look at 1 life, place at top or bottom")
def op06_099_aisa(game_state, player, card):
    """On Play: Look at 1 life and place at top or bottom."""
    # Can look at own or opponent's life - default to own
    if player.life_cards:
        # Already at top, can stay or move to bottom
        pass
    return True


# --- OP06-100: Inuarashi ---
@register_effect("OP06-100", "on_attack", "[DON!! x2] [When Attacking] Trash 1: K.O. cost <= opponent's life count")
def op06_100_inuarashi_attack(game_state, player, card):
    """When Attacking: With 2 DON, trash 1 to K.O. cost <= opponent's life count."""
    if getattr(card, 'attached_don', 0) >= 2 and player.hand:
        trash_from_hand(player, 1, game_state, card)
        opponent = get_opponent(game_state, player)
        life_count = len(opponent.life_cards)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= life_count]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt=f"Choose opponent's cost {life_count} or less to K.O.")
    return True


@register_effect("OP06-100", "trigger", "[Trigger] If opponent has 3 or less life, play this card")
def op06_100_inuarashi_trigger(game_state, player, card):
    """Trigger: If opponent has 3 or less life, play this card."""
    opponent = get_opponent(game_state, player)
    if len(opponent.life_cards) <= 3:
        player.cards_in_play.append(card)
    return True


# --- OP06-101: O-Nami ---
@register_effect("OP06-101", "on_play", "[On Play] Give Banish to Leader or Character")
def op06_101_onami_play(game_state, player, card):
    """On Play: Give Banish to Leader or Character."""
    if player.leader:
        player.leader.has_banish = True
    return True


@register_effect("OP06-101", "trigger", "[Trigger] K.O. opponent's cost 5 or less")
def op06_101_onami_trigger(game_state, player, card):
    """Trigger: K.O. opponent's cost 5 or less."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 5]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                               prompt="Choose opponent's cost 5 or less to K.O.")
    return True


# --- OP06-102: Kamakiri ---
@register_effect("OP06-102", "activate", "[Activate: Main] [Once Per Turn] Bottom Stage cost 1: K.O. cost 2 or less")
def op06_102_kamakiri(game_state, player, card):
    """Activate: Bottom Stage cost 1 to K.O. cost 2 or less."""
    if getattr(card, 'op06_102_used', False):
        return False
    # Look for Stage cost 1
    for c in list(player.cards_in_play):
        if getattr(c, 'card_type', '') == 'STAGE' and (getattr(c, 'cost', 0) or 0) == 1:
            player.cards_in_play.remove(c)
            player.deck.append(c)
            opponent = get_opponent(game_state, player)
            targets = [t for t in opponent.cards_in_play if (getattr(t, 'cost', 0) or 0) <= 2]
            card.op06_102_used = True
            if targets:
                return create_ko_choice(game_state, player, targets, source_card=card,
                                       prompt="Choose opponent's cost 2 or less to K.O.")
            return True
    return False


# --- OP06-103: Kawamatsu ---
@register_effect("OP06-103", "on_attack", "[When Attacking] Trash 2: Add 0 power Character to life")
def op06_103_kawamatsu(game_state, player, card):
    """When Attacking: Trash 2 to add 0 power Character to life."""
    if len(player.hand) >= 2:
        trash_from_hand(player, 2, game_state, card)
        for c in list(player.cards_in_play):
            power = getattr(c, 'power', 0) or 0
            if power == 0:
                player.cards_in_play.remove(c)
                player.life_cards.append(c)
                break
    return True


# --- OP06-104: Kikunojo ---
@register_effect("OP06-104", "on_ko", "[On K.O.] If opponent has 3 or less life, add top deck to life")
def op06_104_kikunojo(game_state, player, card):
    """On K.O.: If opponent has 3 or less life, add top deck to life."""
    opponent = get_opponent(game_state, player)
    if len(opponent.life_cards) <= 3 and player.deck:
        top_card = player.deck.pop(0)
        player.life_cards.append(top_card)
    return True


# --- OP06-105: Genbo ---
# No effect (vanilla 5000 power)


# --- OP06-106: Kouzuki Hiyori ---
@register_effect("OP06-106", "on_play", "[On Play] Add 1 life to hand: Add 1 from hand to life")
def op06_106_hiyori(game_state, player, card):
    """On Play: Add 1 life to hand, then add 1 from hand to life."""
    if player.life_cards and player.hand:
        life_card = player.life_cards.pop()
        player.hand.append(life_card)
        hand_card = player.hand.pop()
        player.life_cards.append(hand_card)
    return True


# --- OP06-107: Kouzuki Momonosuke ---
@register_effect("OP06-107", "blocker", "[Blocker]")
def op06_107_momonosuke_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP06-107", "on_play", "[On Play] Add Land of Wano Character to life")
def op06_107_momonosuke_play(game_state, player, card):
    """On Play: Add Land of Wano Character to life."""
    targets = [c for c in player.cards_in_play if 'Land of Wano' in (c.card_origin or '') and getattr(c, 'name', '') != 'Kouzuki Momonosuke']
    if targets:
        return create_add_to_life_choice(game_state, player, targets, source_card=card,
                                        prompt="Choose your Land of Wano Character to add to life")
    return True


# --- OP06-108: Tenguyama Hitetsu ---
@register_effect("OP06-108", "trigger", "[Trigger] +2000 power to Land of Wano Leader or Character")
def op06_108_hitetsu(game_state, player, card):
    """Trigger: +2000 power to Land of Wano Leader or Character."""
    if player.leader and 'Land of Wano' in (player.leader.card_origin or ''):
        player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 2000
    return True


# --- OP06-109: Denjiro ---
@register_effect("OP06-109", "continuous", "[DON!! x2] If opponent has 3 or less life, cannot be K.O.'d by effects")
def op06_109_denjiro(game_state, player, card):
    """Continuous: With 2 DON, if opponent has 3 or less life, cannot be K.O.'d by effects."""
    opponent = get_opponent(game_state, player)
    if getattr(card, 'attached_don', 0) >= 2 and len(opponent.life_cards) <= 3:
        card.cannot_be_ko_by_effects = True
    return True


# --- OP06-110: Nekomamushi ---
@register_effect("OP06-110", "continuous", "[DON!! x2] Can attack active Characters")
def op06_110_nekomamushi(game_state, player, card):
    """Continuous: With 2 DON, can attack active Characters."""
    if getattr(card, 'attached_don', 0) >= 2:
        card.can_attack_active = True
    return True


# --- OP06-111: Braham ---
@register_effect("OP06-111", "activate", "[Activate: Main] [Once Per Turn] Bottom Stage cost 1: Rest cost 4 or less")
def op06_111_braham(game_state, player, card):
    """Activate: Bottom Stage cost 1 to rest cost 4 or less."""
    if getattr(card, 'op06_111_used', False):
        return False
    for c in list(player.cards_in_play):
        if getattr(c, 'card_type', '') == 'STAGE' and (getattr(c, 'cost', 0) or 0) == 1:
            player.cards_in_play.remove(c)
            player.deck.append(c)
            opponent = get_opponent(game_state, player)
            targets = [t for t in opponent.cards_in_play if (getattr(t, 'cost', 0) or 0) <= 4]
            card.op06_111_used = True
            if targets:
                return create_rest_choice(game_state, player, targets, source_card=card,
                                         prompt="Choose opponent's cost 4 or less to rest")
            return True
    return False


# --- OP06-112: Raizo ---
@register_effect("OP06-112", "on_attack", "[When Attacking] Trash 1: Rest opponent's DON")
def op06_112_raizo(game_state, player, card):
    """When Attacking: Trash 1 to rest opponent's DON."""
    if player.hand:
        trash_from_hand(player, 1, game_state, card)
        opponent = get_opponent(game_state, player)
        for don in opponent.don_pool:
            if not getattr(don, 'is_resting', False):
                don.is_resting = True
                break
    return True


# --- OP06-113: Raki ---
@register_effect("OP06-113", "continuous", "If have other Shandian Warrior, gains Blocker")
def op06_113_raki(game_state, player, card):
    """Continuous: If have other Shandian Warrior, gains Blocker."""
    for c in player.cards_in_play:
        if c != card and 'Shandian Warrior' in (c.card_origin or ''):
            card.has_blocker = True
            break
    return True


# --- OP06-114: Wyper ---
@register_effect("OP06-114", "on_play", "[On Play] Bottom Stage cost 1: Look at 5, add Upper Yard or Shandian Warrior")
def op06_114_wyper(game_state, player, card):
    """On Play: Bottom Stage cost 1 to look at 5 and add Upper Yard or Shandian Warrior."""
    for c in list(player.cards_in_play):
        if getattr(c, 'card_type', '') == 'STAGE' and (getattr(c, 'cost', 0) or 0) == 1:
            player.cards_in_play.remove(c)
            player.deck.append(c)
            looked = player.deck[:5] if len(player.deck) >= 5 else player.deck[:]
            for lc in looked:
                name = getattr(lc, 'name', '')
                types = (lc.card_origin or '')
                if name == 'Upper Yard' or 'Shandian Warrior' in types:
                    player.deck.remove(lc)
                    player.hand.append(lc)
                    break
            break
    return True


# --- OP06-118: Roronoa Zoro (SEC) ---
@register_effect("OP06-118", "on_attack", "[When Attacking] [Once Per Turn] Rest 1 DON: Set active")
def op06_118_zoro_attack(game_state, player, card):
    """When Attacking: Rest 1 DON to set active."""
    if getattr(card, 'op06_118_attack_used', False):
        return False
    for don in player.don_pool:
        if not getattr(don, 'is_resting', False):
            don.is_resting = True
            card.is_resting = False
            card.op06_118_attack_used = True
            return True
    return False


@register_effect("OP06-118", "activate", "[Activate: Main] [Once Per Turn] Rest 2 DON: Set active")
def op06_118_zoro_activate(game_state, player, card):
    """Activate: Rest 2 DON to set active."""
    if getattr(card, 'op06_118_activate_used', False):
        return False
    active_don = player.don_pool.count("active")
    if len(active_don) >= 2:
        active_don[0].is_resting = True
        active_don[1].is_resting = True
        card.is_resting = False
        card.op06_118_activate_used = True
        return True
    return False


# --- OP06-119: Sanji (SEC) ---
@register_effect("OP06-119", "on_play", "[On Play] Reveal 1 from deck, play cost 9 or less (not Sanji)")
def op06_119_sanji(game_state, player, card):
    """On Play: Reveal 1 from deck and play cost 9 or less (not Sanji)."""
    if player.deck:
        revealed = player.deck.pop(0)
        cost = getattr(revealed, 'cost', 0) or 0
        name = getattr(revealed, 'name', '')
        card_type = getattr(revealed, 'card_type', '')
        if card_type == 'CHARACTER' and cost <= 9 and name != 'Sanji':
            player.cards_in_play.append(revealed)
        else:
            player.deck.append(revealed)
    return True


# --- OP06-078: GERMA 66 (Event) ---
@register_effect("OP06-078", "on_play", "[Main] Look at 5 cards from the top of your deck; reveal up to 1 card with type including 'GERMA' other than [GERMA 66] and add it to your hand.")
def op06_078_germa_66(game_state, player, card):
    """[Main] Look at 5: choose up to 1 GERMA type card (not GERMA 66) to add to hand."""
    return search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: 'germa' in (c.card_origin or '').lower() and c.name != 'GERMA 66',
        source_card=card,
        prompt="Look at top 5: choose up to 1 GERMA type card (not GERMA 66) to add to hand")


# --- OP06-079: Kingdom of GERMA (Stage) ---
@register_effect("OP06-079", "activate", "[Activate: Main] Trash 1 from hand and rest this Stage: Look at 3, reveal up to 1 GERMA type card to hand.")
def op06_079_kingdom_of_germa(game_state, player, card):
    """Activate: Trash 1 from hand, rest this Stage: Look at 3, choose up to 1 GERMA type to hand."""
    if card.is_resting:
        return False
    if getattr(card, 'main_activated_this_turn', False):
        return False
    if not player.hand:
        return False
    card.is_resting = True
    card.main_activated_this_turn = True
    trash_from_hand(player, 1, game_state, card)
    return search_top_cards(game_state, player, look_count=3, add_count=1,
        filter_fn=lambda c: 'germa' in (c.card_origin or '').lower(),
        source_card=card,
        prompt="Look at top 3: choose up to 1 GERMA type card to add to hand")

