"""
Hardcoded effects for OP04 cards.
"""

import random

from ..effect_registry import (
    add_don_from_deck, create_bottom_deck_choice, create_cost_reduction_choice,
    create_hand_discard_choice, create_ko_choice, create_rest_choice, create_return_to_hand_choice,
    create_mode_choice, create_play_from_trash_choice, create_power_effect_choice, create_trash_choice,
    create_set_active_choice, create_target_choice, add_power_modifier, check_life_count,
    draw_cards, get_characters_by_cost, get_characters_by_type, get_opponent, register_effect,
    search_top_cards, trash_from_hand,
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


def create_power_reduction_choice(game_state, player, targets, amount, source_card=None, prompt=None, callback=None):
    return create_power_effect_choice(
        game_state, player, targets, amount, source_card=source_card, prompt=prompt, callback=callback
    )


def create_power_boost_choice(game_state, player, targets, amount, source_card=None, prompt=None, callback=None):
    return create_power_effect_choice(
        game_state, player, targets, amount, source_card=source_card, prompt=prompt, callback=callback
    )


def create_attack_active_choice(game_state, player, targets, source_card=None, prompt=None):
    snapshot = list(targets)

    def callback(selected):
        target_idx = int(selected[0]) if selected else -1
        if 0 <= target_idx < len(snapshot):
            snapshot[target_idx].can_attack_active = True
            game_state._log(f"{snapshot[target_idx].name} can attack active Characters this turn")

    return create_target_choice(
        game_state, player, snapshot, prompt or "Choose a Character to attack active Characters",
        source_card=source_card, callback=callback
    )


def create_cannot_attack_choice(game_state, player, targets, source_card=None, prompt=None):
    snapshot = list(targets)

    def callback(selected):
        target_idx = int(selected[0]) if selected else -1
        if 0 <= target_idx < len(snapshot):
            snapshot[target_idx].cannot_attack = True
            game_state._log(f"{snapshot[target_idx].name} cannot attack until the start of your next turn")

    return create_target_choice(
        game_state, player, snapshot, prompt or "Choose a Character that cannot attack",
        source_card=source_card, callback=callback
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
    if _rest_active_don(player, 2):
        draw_cards(player, 1)
        targets = list(player.cards_in_play)

        def callback(selected):
            target_idx = int(selected[0]) if selected else -1
            if 0 <= target_idx < len(targets):
                target = targets[target_idx]
                target.has_rush = True
                target._temporary_rush_until_turn = game_state.turn_count
                game_state._log(f"{target.name} gains Rush during this turn")

        card.op04_001_used = True
        if targets:
            return create_target_choice(
                game_state, player, targets,
                "Choose up to 1 of your Characters to gain Rush during this turn",
                source_card=card, min_selections=0, max_selections=1, callback=callback
            )
        return True
    return False


# --- OP04-019: Donquixote Doflamingo (Leader) ---
@register_effect("OP04-019", "end_of_turn", "[End of Your Turn] Set up to 2 DON active")
def op04_019_doffy_leader(game_state, player, card):
    """End of Your Turn: Set up to 2 of your DON cards as active."""
    _set_rested_don_active(player, 2)
    return True


# --- OP04-020: Issho (Leader) ---
@register_effect("OP04-020", "continuous", "[DON!! x1] [Your Turn] Opponent chars -1 cost")
def op04_020_issho_continuous(game_state, player, card):
    """DON x1, Your Turn: Give all opponent's Characters -1 cost."""
    if getattr(card, 'attached_don', 0) >= 1:
        opponent = get_opponent(game_state, player)
        for char in opponent.cards_in_play:
            char.cost_modifier = getattr(char, 'cost_modifier', 0) - 1
        return True
    return False


@register_effect("OP04-020", "end_of_turn", "[End of Your Turn] Rest 1: Set active cost 5 or less")
def op04_020_issho_eot(game_state, player, card):
    """End of Your Turn, Rest 1: Set up to 1 of your Characters with cost 5 or less as active."""
    if _rest_active_don(player, 1):
        targets = [
            c for c in player.cards_in_play
            if getattr(c, 'is_resting', False) and (getattr(c, 'cost', 0) or 0) <= 5
        ]
        if targets:
            return create_set_active_choice(
                game_state, player, targets, source_card=card,
                prompt="Choose up to 1 of your cost 5 or less Characters to set active"
            )
        return True
    return False


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
        if has_cost_8_plus and player.deck:
            def callback(selected):
                mode = selected[0] if selected else "draw"
                if mode == "life" and player.deck:
                    life_card = player.deck.pop(0)
                    player.life_cards.append(life_card)
                    game_state._log(f"{player.name} added {life_card.name} from the top of deck to Life")
                else:
                    draw_cards(player, 1)

            return create_mode_choice(
                game_state, player,
                modes=[
                    {"id": "draw", "label": "Draw 1 card"},
                    {"id": "life", "label": "Add top card to Life"},
                ],
                source_card=card,
                prompt="Choose Queen's effect",
                callback=callback,
            )
        draw_cards(player, 1)
        return True
    return False


# --- OP04-058: Crocodile (Leader) ---
@register_effect("OP04-058", "on_don_return", "[Opponent's Turn] When DON returned, add 1 DON active")
def op04_058_croc_leader(game_state, player, card):
    """Opponent's Turn, Once Per Turn: When DON returned to deck by your effect, add 1 DON active."""
    if hasattr(card, 'op04_058_used') and card.op04_058_used:
        return False
    if hasattr(player, 'don_deck') and player.don_deck:
        don = player.don_deck.pop(0)
        don.is_resting = False
        player.don_pool.append(don)
        card.op04_058_used = True
        return True
    return False


# =============================================================================
# OP04 CHARACTER EFFECTS - Kingdoms of Intrigue
# =============================================================================

# --- OP04-002: Igaram ---
@register_effect("OP04-002", "activate", "[Activate: Main] Rest, Leader -5000: Search for Alabasta card")
def op04_002_igaram(game_state, player, card):
    """Activate: Rest this and give Leader -5000 to search for Alabasta card."""
    if not getattr(card, 'is_resting', False) and player.leader:
        card.is_resting = True
        player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) - 5000
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
        return create_ko_choice(game_state, player, targets, source_card=card,
                               prompt="Choose opponent's Character with 5000 base power or less to K.O.")
    return True


# --- OP04-004: Karoo ---
@register_effect("OP04-004", "activate", "[Activate: Main] Rest: Attach DON to Alabasta characters")
def op04_004_karoo(game_state, player, card):
    """Activate: Rest to give rested DON to each Alabasta character."""
    if not getattr(card, 'is_resting', False):
        card.is_resting = True
        alabasta_chars = [c for c in player.cards_in_play if 'Alabasta' in (c.card_origin or '')]
        for char in alabasta_chars:
            if "rested" in player.don_pool:
                player.don_pool.remove("rested")
                char.attached_don = getattr(char, 'attached_don', 0) + 1
        return True
    return False


# --- OP04-005: Kung Fu Jugon ---
@register_effect("OP04-005", "continuous", "Gains Blocker if you have another Kung Fu Jugon")
def op04_005_kungfu_jugon(game_state, player, card):
    """Continuous: Gains Blocker if you have another Kung Fu Jugon."""
    others = [c for c in player.cards_in_play if getattr(c, 'name', '') == 'Kung Fu Jugon' and c != card]
    card.has_blocker = len(others) > 0
    return True


# --- OP04-006: Koza ---
@register_effect("OP04-006", "on_attack", "[When Attacking] Leader -5000: This gains +2000 until next turn")
def op04_006_koza(game_state, player, card):
    """When Attacking: Leader -5000 to gain +2000 until next turn."""
    if player.leader:
        player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) - 5000
        card.power_modifier = getattr(card, 'power_modifier', 0) + 2000
        return True
    return False


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
                        prompt="Choose up to 1 Character with 0 power or less to K.O."
                    )

            return create_power_reduction_choice(
                game_state, player, snapshot, -3000, source_card=card,
                prompt="Choose up to 1 opponent's Character to give -3000 power", callback=callback
            )
        return True
    return False


# --- OP04-009: Super Spot-Billed Duck Troops ---
@register_effect("OP04-009", "on_attack", "[When Attacking] Leader -5000: Return to hand at end of turn")
def op04_009_duck_troops(game_state, player, card):
    """When Attacking: Leader -5000 to return to hand at end of turn."""
    if player.leader:
        player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) - 5000
        card.return_to_hand_eot = True
        return True
    return False


# --- OP04-010: Tony Tony Chopper ---
@register_effect("OP04-010", "on_play", "[On Play] Play Animal Character with 3000 power or less")
def op04_010_chopper(game_state, player, card):
    """On Play: Play Animal character with 3000 power or less from hand."""
    for c in list(player.hand):
        if 'Animal' in (c.card_origin or '') and (getattr(c, 'power', 0) or 0) <= 3000:
            player.hand.remove(c)
            player.cards_in_play.append(c)
            return True
    return True


# --- OP04-011: Nami ---
@register_effect("OP04-011", "on_attack", "[When Attacking] Reveal top card, +3000 if 6000+ power Character")
def op04_011_nami(game_state, player, card):
    """When Attacking: Reveal top card, +3000 if 6000+ power Character."""
    if player.deck:
        revealed = player.deck[0]
        player.deck.remove(revealed)
        game_state._log(f"{card.name} revealed {revealed.name}")
        if getattr(revealed, 'card_type', '') == 'CHARACTER' and (getattr(revealed, 'power', 0) or 0) >= 6000:
            add_power_modifier(card, 3000)
        player.deck.append(revealed)  # Bottom of deck
    return True


# --- OP04-012: Nefeltari Cobra ---
@register_effect("OP04-012", "continuous", "[Your Turn] Alabasta Characters gain +1000")
def op04_012_cobra(game_state, player, card):
    """Your Turn: Alabasta characters other than this gain +1000."""
    for c in player.cards_in_play:
        if c != card and 'Alabasta' in (c.card_origin or ''):
            c.power_modifier = getattr(c, 'power_modifier', 0) + 1000
    return True


# --- OP04-013: Pell ---
@register_effect("OP04-013", "on_attack", "[DON!! x1] [When Attacking] K.O. 4000 power or less")
def op04_013_pell(game_state, player, card):
    """When Attacking with 1 DON: K.O. opponent's 4000 power or less character."""
    attached = getattr(card, 'attached_don', 0)
    if attached >= 1:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'power', 0) or 0) <= 4000]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's 4000 power or less Character to K.O.")
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
        return create_power_reduction_choice(game_state, player, list(opponent.cards_in_play), -2000, source_card=card,
                                            prompt="Choose opponent's Character to give -2000 power")
    return True


# --- OP04-021: Viola ---
@register_effect("OP04-021", "on_opponent_attack", "[On Opponent's Attack] DON -1: Rest opponent's DON")
def op04_021_viola(game_state, player, card):
    """On Opponent's Attack: Rest 1 DON to rest opponent's DON."""
    if _rest_active_don(player, 2):
        _rest_one_opponent_active_don(game_state, player)
        return True
    return False


# --- OP04-022: Eric ---
@register_effect("OP04-022", "activate", "[Activate: Main] Rest: Rest opponent's cost 1 or less Character")
def op04_022_eric(game_state, player, card):
    """Activate: Rest to rest opponent's cost 1 or less character."""
    if not getattr(card, 'is_resting', False):
        card.is_resting = True
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 1]
        if targets:
            return create_rest_choice(game_state, player, targets, source_card=card,
                                     prompt="Choose opponent's cost 1 or less Character to rest")
        return True
    return False


# --- OP04-024: Sugar ---
@register_effect("OP04-024", "on_play", "[On Play] Rest opponent's cost 4 or less Character")
def op04_024_sugar_play(game_state, player, card):
    """On Play: Rest opponent's cost 4 or less character."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
    if targets:
        return create_rest_choice(game_state, player, targets, source_card=card,
                                 prompt="Choose opponent's cost 4 or less Character to rest")
    return True


@register_effect("OP04-024", "on_opponent_play", "[Opponent's Turn] When opponent plays Character, rest one and this")
def op04_024_sugar_opp_turn(game_state, player, card):
    """Opponent's Turn: When opponent plays character, rest one and this."""
    if not getattr(card, 'op04_024_used', False):
        if player.leader and 'Donquixote Pirates' in (player.leader.card_origin or ''):
            opponent = get_opponent(game_state, player)
            card.is_resting = True
            card.op04_024_used = True
            if opponent.cards_in_play:
                return create_rest_choice(game_state, player, list(opponent.cards_in_play), source_card=card,
                                         prompt="Choose opponent's Character to rest")
            return True
    return False


# --- OP04-025: Giolla ---
@register_effect("OP04-025", "on_opponent_attack", "[On Opponent's Attack] DON -2: Rest opponent's cost 4 or less")
def op04_025_giolla(game_state, player, card):
    """On Opponent's Attack: Rest 2 DON to rest opponent's cost 4 or less character."""
    if _rest_active_don(player, 2):
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
        if targets:
            return create_rest_choice(game_state, player, targets, source_card=card,
                                     prompt="Choose opponent's cost 4 or less Character to rest")
        return True
    return False


# --- OP04-026: Senor Pink ---
@register_effect("OP04-026", "on_attack", "[When Attacking] DON -1: Rest cost 4 or less, active 1 DON at end")
def op04_026_senor_pink(game_state, player, card):
    """When Attacking: Rest 1 DON to rest cost 4 or less and activate 1 DON at end."""
    if _rest_active_don(player, 1) and player.leader and 'Donquixote Pirates' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
        # Mark DON to activate at end of turn
        player.activate_don_eot = True
        if targets:
            return create_rest_choice(game_state, player, targets, source_card=card,
                                     prompt="Choose opponent's cost 4 or less Character to rest")
        return True
    return False


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
    _set_rested_don_active(player, 1)
    return True


# --- OP04-030: Trebol ---
@register_effect("OP04-030", "on_play", "[On Play] K.O. opponent's rested cost 5 or less")
def op04_030_trebol_play(game_state, player, card):
    """On Play: K.O. opponent's rested character with cost 5 or less."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if getattr(c, 'is_resting', False) and (getattr(c, 'cost', 0) or 0) <= 5]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                               prompt="Choose opponent's rested cost 5 or less Character to K.O.")
    return True


@register_effect("OP04-030", "on_opponent_attack", "[On Opponent's Attack] DON -2: Rest cost 4 or less")
def op04_030_trebol_defense(game_state, player, card):
    """On Opponent's Attack: Rest 2 DON to rest cost 4 or less character."""
    rested = 0
    for don in player.don_pool:
        if not getattr(don, 'is_resting', False) and rested < 2:
            don.is_resting = True
            rested += 1
    if rested >= 2:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
        if targets:
            return create_rest_choice(game_state, player, targets, source_card=card,
                                     prompt="Choose opponent's cost 4 or less Character to rest")
        return True
    return False


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
            _set_rested_don_active(player, 2)
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
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 5]
        player.activate_don_eot = True
        if targets:
            return create_rest_choice(game_state, player, targets, source_card=card,
                                     prompt="Choose opponent's cost 5 or less Character to rest")
        return True
    return False


# --- OP04-034: Lao.G ---
@register_effect("OP04-034", "end_of_turn", "[End of Turn] If 3+ active DON, K.O. rested cost 3 or less")
def op04_034_lao_g(game_state, player, card):
    """End of Turn: If 3+ active DON, K.O. opponent's rested cost 3 or less."""
    active_don = _active_don_count(player)
    if active_don >= 3:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if getattr(c, 'is_resting', False) and (getattr(c, 'cost', 0) or 0) <= 3]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's rested cost 3 or less Character to K.O.")
        return True
    return False


# --- OP04-041: Apis ---
@register_effect("OP04-041", "on_play", "[On Play] Trash 2: Look at 5, add East Blue card")
def op04_041_apis(game_state, player, card):
    """On Play: Trash 2 cards to look at 5 and add East Blue card."""
    if len(player.hand) < 2:
        return False

    def resolve_search():
        return search_top_cards(
            game_state, player, look_count=5, add_count=1,
            filter_fn=lambda c: 'east blue' in (c.card_origin or '').lower(),
            source_card=card,
            prompt="Look at top 5: choose up to 1 East Blue card to add to hand"
        )

    if len(player.hand) == 2:
        trash_from_hand(player, 2)
        return resolve_search()

    hand_snapshot = list(player.hand)

    def callback(selected):
        for idx in sorted((int(sel) for sel in selected), reverse=True):
            if 0 <= idx < len(hand_snapshot):
                discarded = hand_snapshot[idx]
                if discarded in player.hand:
                    player.hand.remove(discarded)
                    player.trash.append(discarded)
                    game_state._log(f"{player.name} trashed {discarded.name}")
        resolve_search()

    return create_trash_choice(
        game_state, player, 2, source_card=card,
        prompt="Choose 2 cards from your hand to trash",
        callback=callback
    )
    return False


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
            callback=callback
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
    all_chars = list(player.cards_in_play) + list(opponent.cards_in_play)
    # Return cost 8 or less first
    targets8 = [c for c in all_chars if (getattr(c, 'cost', 0) or 0) <= 8 and c != card]
    if targets8:
        t8_snap = list(targets8)
        def kaido_step1_cb(selected: list) -> None:
            target_idx = int(selected[0]) if selected else -1
            if 0 <= target_idx < len(t8_snap):
                target = t8_snap[target_idx]
                for p in [player, get_opponent(game_state, player)]:
                    if target in p.cards_in_play:
                        p.cards_in_play.remove(target)
                        p.hand.append(target)
                        game_state._log(f"{target.name} returned to hand")
                        break
            all_chars2 = list(player.cards_in_play) + list(get_opponent(game_state, player).cards_in_play)
            targets3 = [c for c in all_chars2 if (getattr(c, 'cost', 0) or 0) <= 3]
            if targets3:
                create_return_to_hand_choice(game_state, player, targets3, source_card=None,
                                             prompt="Choose cost 3 or less Character to return to hand")
        return create_return_to_hand_choice(game_state, player, targets8, source_card=card,
                                            prompt="Choose cost 8 or less Character to return to hand",
                                            callback=kaido_step1_cb)
    return True


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
    return False


# --- OP04-047: Ice Oni ---
@register_effect("OP04-047", "continuous", "[Your Turn] After battle with cost 5 or less, place at deck bottom")
def op04_047_ice_oni(game_state, player, card):
    """Your Turn: After battle with cost 5 or less, place them at deck bottom."""
    card.ice_oni_effect = True
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
    if not getattr(card, 'is_resting', False):
        rested = 0
        for don in player.don_pool:
            if not getattr(don, 'is_resting', False) and rested < 2:
                don.is_resting = True
                rested += 1
        if rested >= 2:
            card.is_resting = True
            draw_cards(player, 1)
            return True
    return False


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


# --- OP04-059: Iceburg ---
@register_effect("OP04-059", "on_opponent_attack", "[On Opponent's Attack] DON -1: Gains Blocker if Water Seven Leader")
def op04_059_iceburg(game_state, player, card):
    """On Opponent's Attack: Return 1 DON to gain Blocker if Water Seven Leader."""
    if player.leader and 'Water Seven' in (player.leader.card_origin or ''):
        if player.don_pool:
            don = player.don_pool.pop()
            player.don_deck.append(don)
            card.has_blocker = True
            card._temporary_blocker_until_turn = game_state.turn_count
            return True
    return False


# --- OP04-060: Crocodile ---
@register_effect("OP04-060", "on_play", "[On Play] DON -2: If Baroque Works Leader, add deck to Life")
def op04_060_crocodile_play(game_state, player, card):
    """On Play: Return 2 DON to add deck card to Life if Baroque Works Leader."""
    if player.leader and 'Baroque Works' in (player.leader.card_origin or ''):
        if len(player.don_pool) >= 2:
            for _ in range(2):
                don = player.don_pool.pop()
                player.don_deck.append(don)
            if player.deck:
                player.life_cards.append(player.deck.pop(0))
            return True
    return False


@register_effect("OP04-060", "on_opponent_attack", "[On Opponent's Attack] [Once Per Turn] DON -1: Draw 1, trash 1")
def op04_060_crocodile_defense(game_state, player, card):
    """On Opponent's Attack: Return 1 DON to draw 1 and trash 1."""
    if not getattr(card, 'op04_060_used', False) and player.don_pool:
        don = player.don_pool.pop()
        player.don_deck.append(don)
        draw_cards(player, 1)
        trash_from_hand(player, 1, game_state, card)
        card.op04_060_used = True
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
            if player.don_pool:
                don = player.don_pool.pop()
                player.don_deck.append(don)
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

                    return create_target_choice(
                        game_state, player, snapshot,
                        "Choose up to 1 of your Leader or Characters to give +1000 power during this battle",
                        source_card=card, min_selections=0, max_selections=1, callback=callback
                    )
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
    if len(player.don_pool) >= 2:
        for _ in range(2):
            don = player.don_pool.pop()
            player.don_deck.append(don)
        player.cards_in_play.append(card)
        return True
    return False


# --- OP04-065: Miss Goldenweek ---
@register_effect("OP04-065", "on_play", "[On Play] If Baroque Works Leader, cost 5 or less cannot attack")
def op04_065_goldenweek(game_state, player, card):
    """On Play: If Baroque Works Leader, opponent's cost 5 or less cannot attack."""
    if player.leader and 'Baroque Works' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 5]
        if targets:
            return create_cannot_attack_choice(game_state, player, targets, source_card=card,
                                              prompt="Choose opponent's cost 5 or less Character that cannot attack")
    return True


@register_effect("OP04-065", "trigger", "[Trigger] DON -1: Play this card")
def op04_065_goldenweek_trigger(game_state, player, card):
    """Trigger: Return 1 DON to play this card."""
    if player.don_pool:
        don = player.don_pool.pop()
        player.don_deck.append(don)
        player.cards_in_play.append(card)
        return True
    return False


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
    if player.don_pool:
        don = player.don_pool.pop()
        player.don_deck.append(don)
        player.cards_in_play.append(card)
        return True
    return False


# --- OP04-067: Miss Merry Christmas ---
@register_effect("OP04-067", "blocker", "[Blocker]")
def op04_067_merry_christmas_blocker(game_state, player, card):
    """Blocker ability."""
    card.has_blocker = True
    return True


@register_effect("OP04-067", "trigger", "[Trigger] DON -1: Play this card")
def op04_067_merry_christmas_trigger(game_state, player, card):
    """Trigger: Return 1 DON to play this card."""
    if player.don_pool:
        don = player.don_pool.pop()
        player.don_deck.append(don)
        player.cards_in_play.append(card)
        return True
    return False


# --- OP04-068: Yokozuna ---
@register_effect("OP04-068", "blocker", "[Blocker]")
def op04_068_yokozuna_blocker(game_state, player, card):
    """Blocker ability."""
    card.has_blocker = True
    return True


@register_effect("OP04-068", "on_opponent_attack", "[On Opponent's Attack] DON -1: Return cost 2 or less to hand")
def op04_068_yokozuna_defense(game_state, player, card):
    """On Opponent's Attack: Return 1 DON to return cost 2 or less to hand."""
    if player.don_pool:
        don = player.don_pool.pop()
        player.don_deck.append(don)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
        if targets:
            return create_return_to_hand_choice(game_state, player, targets, source_card=card,
                                               prompt="Choose opponent's cost 2 or less Character to return to hand")
        return True
    return False


# --- OP04-069: Mr. 2 Bon Kurei ---
@register_effect("OP04-069", "on_opponent_attack", "[On Opponent's Attack] DON -1: Match attacker's power")
def op04_069_bon_kurei(game_state, player, card):
    """On Opponent's Attack: Return 1 DON to match attacker's power."""
    if player.don_pool:
        don = player.don_pool.pop()
        player.don_deck.append(don)
        attacker = (getattr(game_state, 'pending_attack', {}) or {}).get('attacker')
        if attacker is not None:
            attacker_power = (getattr(attacker, 'power', 0) or 0) + getattr(attacker, 'power_modifier', 0)
            own_power = (getattr(card, 'power', 0) or 0) + getattr(card, 'power_modifier', 0)
            delta = attacker_power - own_power
            if delta:
                add_power_modifier(card, delta)
                card.power_modifier_expires_on_turn = game_state.turn_count
                card._sticky_power_modifier_expires_on_turn = game_state.turn_count
        return True
    return False


@register_effect("OP04-069", "trigger", "[Trigger] DON -1: Play this card")
def op04_069_bon_kurei_trigger(game_state, player, card):
    """Trigger: Return 1 DON to play this card."""
    if player.don_pool:
        don = player.don_pool.pop()
        player.don_deck.append(don)
        player.cards_in_play.append(card)
        return True
    return False


# --- OP04-070: Mr. 3 ---
@register_effect("OP04-070", "on_opponent_attack", "[On Opponent's Attack] [Once Per Turn] DON -1: -1000 power")
def op04_070_mr3(game_state, player, card):
    """On Opponent's Attack: Return 1 DON to give -1000 power."""
    if not getattr(card, 'op04_070_used', False) and player.don_pool:
        don = player.don_pool.pop()
        player.don_deck.append(don)
        opponent = get_opponent(game_state, player)
        card.op04_070_used = True
        if opponent.cards_in_play:
            return create_power_reduction_choice(game_state, player, list(opponent.cards_in_play), -1000, source_card=card,
                                                prompt="Choose opponent's Character to give -1000 power")
        return True
    return False


# --- OP04-071: Mr. 4 ---
@register_effect("OP04-071", "on_opponent_attack", "[On Opponent's Attack] DON -1: Gains Blocker +1000")
def op04_071_mr4(game_state, player, card):
    """On Opponent's Attack: Return 1 DON to gain Blocker and +1000."""
    if player.don_pool:
        don = player.don_pool.pop()
        player.don_deck.append(don)
        card.has_blocker = True
        card._temporary_blocker_for_battle = True
        card.power_modifier = getattr(card, 'power_modifier', 0) + 1000
        card._battle_power_modifier = getattr(card, '_battle_power_modifier', 0) + 1000
        return True
    return False


# --- OP04-072: Mr. 5 ---
@register_effect("OP04-072", "on_opponent_attack", "[On Opponent's Attack] [Once Per Turn] DON -2 and rest: K.O. cost 4 or less")
def op04_072_mr5(game_state, player, card):
    """On Opponent's Attack: Return 2 DON and rest to K.O. cost 4 or less."""
    if not getattr(card, 'op04_072_used', False) and len(player.don_pool) >= 2:
        for _ in range(2):
            don = player.don_pool.pop()
            player.don_deck.append(don)
        card.is_resting = True
        card.op04_072_used = True
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's cost 4 or less Character to K.O.")
        return True
    return False


# --- OP04-073: Mr.13 & Ms.Friday ---
@register_effect("OP04-073", "activate", "[Activate: Main] Trash this and Baroque Works: Add 1 active DON")
def op04_073_mr13_friday(game_state, player, card):
    """Activate: Trash this and Baroque Works character to add 1 active DON."""
    bw_chars = [c for c in player.cards_in_play if 'Baroque Works' in (c.card_origin or '') and c != card]
    if bw_chars and card in player.cards_in_play:
        player.cards_in_play.remove(card)
        player.trash.append(card)
        bw_snap = list(bw_chars)
        def mr13_friday_cb(selected: list) -> None:
            target_idx = int(selected[0]) if selected else -1
            if 0 <= target_idx < len(bw_snap):
                target = bw_snap[target_idx]
                if target in player.cards_in_play:
                    player.cards_in_play.remove(target)
                    player.trash.append(target)
                    game_state._log(f"{target.name} was trashed")
            add_don_from_deck(player, 1, set_active=True)
            game_state._log(f"{player.name} gained 1 active DON")
        return create_ko_choice(game_state, player, bw_chars, source_card=card,
                               prompt="Choose your Baroque Works Character to trash",
                               callback=mr13_friday_cb)
    return False


@register_effect("OP04-073", "trigger", "[Trigger] Play this card")
def op04_073_mr13_friday_trigger(game_state, player, card):
    """Trigger: Play this card."""
    player.cards_in_play.append(card)
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
        if opponent.cards_in_play:
            opp_snap = list(opponent.cards_in_play)
            def orlumbus_cb(selected: list) -> None:
                for sel in selected:
                    target_idx = int(sel)
                    if 0 <= target_idx < len(opp_snap):
                        target = opp_snap[target_idx]
                        target.cost_modifier = getattr(target, 'cost_modifier', 0) - 4
                        game_state._log(f"{target.name} gets -4 cost this turn")
                dressrosa = [c for c in player.cards_in_play if 'Dressrosa' in (c.card_origin or '')]
                if dressrosa:
                    create_ko_choice(game_state, player, list(dressrosa), source_card=None,
                                    prompt="Choose your Dressrosa Character to K.O.")
            return create_cost_reduction_choice(game_state, player, list(opponent.cards_in_play), -4, source_card=card,
                                               prompt="Choose opponent's Character to give -4 cost",
                                               callback=orlumbus_cb)
        return True
    return False


# --- OP04-080: Gyats ---
@register_effect("OP04-080", "on_play", "[On Play] Dressrosa can attack active")
def op04_080_gyats(game_state, player, card):
    """On Play: Dressrosa character can attack active characters."""
    dressrosa = [c for c in player.cards_in_play if 'Dressrosa' in (c.card_origin or '')]
    if dressrosa:
        return create_attack_active_choice(game_state, player, dressrosa, source_card=card,
                                          prompt="Choose Dressrosa Character to gain attack active")
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
        player.leader.is_resting = True
        for _ in range(min(2, len(player.deck))):
            player.trash.append(player.deck.pop(0))
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 1]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's cost 1 or less Character to K.O.")
        return True
    return False


# --- OP04-082: Kyros ---
@register_effect("OP04-082", "on_ko_prevention", "If would be K.O.'d, rest Leader or Corrida Coliseum instead")
def op04_082_kyros_prevention(game_state, player, card):
    """K.O. Prevention: Rest Leader or Corrida Coliseum instead."""
    if player.leader and not getattr(player.leader, 'is_resting', False):
        player.leader.is_resting = True
        return True
    corrida = [c for c in player.cards_in_play if getattr(c, 'name', '') == 'Corrida Coliseum']
    if corrida:
        corrida[0].is_resting = True
        return True
    return False


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
                prompt="Choose up to 1 opponent's cost 1 or less Character to K.O.", callback=callback
            )
        _trash_top_cards(player, 1)
        return True
    return False


# --- OP04-083: Sabo ---
@register_effect("OP04-083", "blocker", "[Blocker]")
def op04_083_sabo_blocker(game_state, player, card):
    """Blocker ability."""
    card.has_blocker = True
    return True


@register_effect("OP04-083", "on_play", "[On Play] Characters cannot be K.O.'d by effects, draw 2 trash 2")
def op04_083_sabo_play(game_state, player, card):
    """On Play: Characters cannot be K.O.'d by effects until next turn. Draw 2, trash 2."""
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
                prompt="Choose up to 1 opponent's Character to give -2 cost", callback=callback
            )
        _trash_top_cards(player, 1)
        return True
    return False


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
                prompt="Choose up to 1 opponent's Character to give -2 cost", callback=callback
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
        trash_from_hand(player, 2, game_state, card)
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
            return create_cost_reduction_choice(game_state, player, list(opponent.cards_in_play), -4, source_card=card,
                                               prompt="Choose opponent's Character to give -4 cost")
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
            player.leader.is_resting = True
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
                    _trash_top_cards(player, 2)

                return create_ko_choice(
                    game_state, player, targets, source_card=card,
                    prompt="Choose up to 1 opponent's cost 1 or less Character to K.O.", callback=callback
                )
            _trash_top_cards(player, 2)
            return True
    return False


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


# --- OP04-097: Otama ---
@register_effect("OP04-097", "on_play", "[On Play] Add opponent's Animal/SMILE cost 3 or less to their Life")
def op04_097_otama(game_state, player, card):
    """On Play: Add opponent's Animal/SMILE cost 3 or less to their Life."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
               if ('Animal' in (c.card_origin or '') or 'SMILE' in (c.card_origin or ''))
               and (getattr(c, 'cost', 0) or 0) <= 3]
    if targets:
        return create_bottom_deck_choice(game_state, player, targets, source_card=card,
                                        prompt="Choose Animal/SMILE cost 3 or less to add to opponent's Life",
                                        callback_action="add_to_opponent_life")
    return True


# --- OP04-098: Toko ---
@register_effect("OP04-098", "on_play", "[On Play] Trash 2 Wano: If 1 or less Life, add deck to Life")
def op04_098_toko(game_state, player, card):
    """On Play: Trash 2 Wano cards to add deck to Life if 1 or less Life."""
    wano_cards = [c for c in player.hand if 'Land of Wano' in (c.card_origin or '')]
    if len(wano_cards) >= 2 and len(player.life_cards) <= 1:
        snapshot = list(wano_cards)

        def callback(selected):
            if len(selected) != 2:
                return
            for idx in sorted((int(sel) for sel in selected), reverse=True):
                if 0 <= idx < len(snapshot):
                    target = snapshot[idx]
                    if target in player.hand:
                        player.hand.remove(target)
                        player.trash.append(target)
                        game_state._log(f"{player.name} trashed {target.name}")
            if player.deck:
                player.life_cards.append(player.deck.pop(0))
                game_state._log(f"{player.name} added 1 card from the top of deck to Life")

        return create_target_choice(
            game_state, player, snapshot,
            "Choose 2 Land of Wano cards from your hand to trash",
            source_card=card, min_selections=2, max_selections=2, callback=callback
        )
    return False


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
    if opponent.leader:
        opponent.leader.cannot_attack = True
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
        return create_ko_choice(game_state, player, targets, source_card=card,
                               prompt="Choose opponent's cost 2 or less Character to K.O.")
    return True


# --- OP04-102: Kin'emon ---
@register_effect("OP04-102", "activate", "[Activate: Main] [Once Per Turn] DON -1, take Life: Set active")
def op04_102_kinemon(game_state, player, card):
    """Activate: Rest 1 DON and take Life to set this active."""
    if not getattr(card, 'op04_102_used', False):
        rested = 0
        for don in player.don_pool:
            if not getattr(don, 'is_resting', False) and rested < 1:
                don.is_resting = True
                rested += 1
        if rested >= 1 and player.life_cards:
            life_card = player.life_cards.pop()
            player.hand.append(life_card)
            card.is_resting = False
            card.op04_102_used = True
            return True
    return False


# --- OP04-103: Kouzuki Hiyori ---
@register_effect("OP04-103", "on_play", "[On Play] Wano Leader/Character gains +1000")
def op04_103_hiyori(game_state, player, card):
    """On Play: Wano Leader or Character gains +1000."""
    wano = [c for c in player.cards_in_play if 'Land of Wano' in (c.card_origin or '')]
    if player.leader and 'Land of Wano' in (player.leader.card_origin or ''):
        wano.append(player.leader)
    if wano:
        return create_power_boost_choice(game_state, player, wano, 1000, source_card=card,
                                        prompt="Choose Wano Leader or Character to give +1000 power")
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
        trash_from_hand(player, 1, game_state, card)
        player.cards_in_play.append(card)
        return True
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
                                      prompt="Choose opponent's cost 2 or less Character to rest")
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
        trash_from_hand(player, 1, game_state, card)
        player.cards_in_play.append(card)
        return True
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
        trash_from_hand(player, 1, game_state, card)
        player.cards_in_play.append(card)
        return True
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
            return create_power_boost_choice(game_state, player, wano, 3000, source_card=card,
                                            prompt="Choose Wano Leader or Character to give +3000 power")
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
    if homies and not getattr(card, 'is_resting', False):
        card.is_resting = True
        homies_snap = list(homies)
        def hera_cb(selected: list) -> None:
            target_idx = int(selected[0]) if selected else -1
            if 0 <= target_idx < len(homies_snap):
                target = homies_snap[target_idx]
                if target in player.cards_in_play:
                    player.cards_in_play.remove(target)
                    player.trash.append(target)
                    game_state._log(f"{target.name} was trashed")
            for c in player.cards_in_play:
                if 'Charlotte Linlin' in (getattr(c, 'name', '') or ''):
                    c.is_resting = False
                    c.has_attacked = False
                    game_state._log(f"{c.name} set active")
                    break
        return create_ko_choice(game_state, player, homies, source_card=card,
                               prompt="Choose Homies Character to trash",
                               callback=hera_cb)
    return False


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
    if len(player.life_cards) <= 1 and player.deck:
        player.life_cards.append(player.deck.pop(0))
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                               prompt=f"Choose opponent's cost {total_life} or less Character to K.O.")
    return True


# --- OP04-113: Rabiyan ---
@register_effect("OP04-113", "trigger", "[Trigger] Play this card")
def op04_113_rabiyan(game_state, player, card):
    """Trigger: Play this card."""
    player.cards_in_play.append(card)
    return True


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
    if getattr(card, 'is_resting', False):
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
                player.cards_in_play.append(chosen)
                setattr(chosen, 'played_turn', game_state.turn_count)
                game_state._apply_keywords(chosen)
                game_state._log(f"{player.name} played {chosen.name} from hand")

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
