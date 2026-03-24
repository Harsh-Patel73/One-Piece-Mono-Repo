"""
Hardcoded effects for OP04 cards.
"""

import random

from ..hardcoded import (
    add_don_from_deck, create_bottom_deck_choice, create_cost_reduction_choice, create_dual_target_choice,
    create_hand_discard_choice, create_ko_choice, create_rest_choice, create_return_to_hand_choice,
    create_target_choice, draw_cards, get_characters_by_cost, get_characters_by_type,
    get_opponent, register_effect, search_top_cards, trash_from_hand,
)


# --- OP04-081: Cavendish ---
@register_effect("OP04-081", "WHEN_ATTACKING", "Rest Leader to KO cost 1 or less, trash 2 from deck")
def cavendish_effect(game_state, player, card):
    if player.leader and not player.leader.is_resting:
        player.leader.is_resting = True
        opponent = get_opponent(game_state, player)
        # Trash 2 from deck first (not a choice)
        for _ in range(2):
            if player.deck:
                player.trash.append(player.deck.pop(0))
        # Then KO cost 1 or less with choice
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 1]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                     prompt="Choose opponent's cost 1 or less Character to KO")
        return True
    return False


# --- OP04-080: Gyats ---
@register_effect("OP04-080", "ON_PLAY", "Dressrosa char can attack active this turn")
def gyats_effect(game_state, player, card):
    dressrosa = get_characters_by_type(player, 'dressrosa')
    if dressrosa:
        dressrosa[0].can_attack_active = True
        return True
    return False


# --- OP04-020: Issho (Leader) ---
@register_effect("OP04-020", "END_OF_TURN", "Rest 1 DON: Set cost 5 or less char active")
def issho_leader_effect(game_state, player, card):
    active_don = [d for d in player.don_pool if not d.is_resting]
    if active_don:
        active_don[0].is_resting = True
        chars = get_characters_by_cost(player, max_cost=5)
        rested = [c for c in chars if c.is_resting]
        if rested:
            rested[0].is_resting = False
            return True
    return False


# --- OP04-069: Mr.2.Bon.Kurei(Bentham) ---
@register_effect("OP04-069", "ON_OPPONENT_ATTACK", "DON -1: Copy attacker's power")
def mr2_op04_effect(game_state, player, card):
    if hasattr(game_state, 'current_attacker'):
        card.power = getattr(game_state.current_attacker, 'power', 0)
        # Return DON
        active_don = [d for d in player.don_pool if not d.is_resting]
        if active_don and hasattr(player, 'don_deck'):
            don = active_don[0]
            player.don_pool.remove(don)
            player.don_deck.append(don)
            return True
    return False


# --- OP04-097: Otama ---
@register_effect("OP04-097", "ON_PLAY", "Add opponent's Animal/SMILE cost 3 or less to their Life")
def otama_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
              if ('animal' in (c.card_origin or '').lower()
                  or 'smile' in (c.card_origin or '').lower())
              and (getattr(c, 'cost', 0) or 0) <= 3]
    if targets:
        return create_target_choice(
            game_state, player, targets,
            callback_action="add_to_opponent_life",
            source_card=card,
            prompt="Choose opponent's Animal/SMILE cost 3 or less Character to add to their Life"
        )
    return False


# --- OP04-048: Sasaki ---
@register_effect("OP04-048", "ON_PLAY", "Return hand to deck, shuffle, draw same number")
def sasaki_effect(game_state, player, card):
    hand_count = len(player.hand)
    player.deck.extend(player.hand)
    player.hand.clear()
    random.shuffle(player.deck)
    draw_cards(player, hand_count)
    return True


# --- OP04-047: Ice Oni ---
@register_effect("OP04-047", "END_OF_BATTLE", "Place battled character at bottom if cost 5 or less")
def ice_oni_effect(game_state, player, card):
    """At end of battle, place opponent's battled character at bottom if cost 5 or less."""
    opponent = get_opponent(game_state, player)
    if hasattr(game_state, 'last_battle_target'):
        target = game_state.last_battle_target
        if target and target in opponent.cards_in_play:
            if (getattr(target, 'cost', 0) or 0) <= 5:
                opponent.cards_in_play.remove(target)
                opponent.deck.append(target)
                return True
    return False


# --- OP04-099: Olin ---
@register_effect("OP04-099", "CONTINUOUS", "Also treat name as Charlotte Linlin")
def olin_name_effect(game_state, player, card):
    """Card name is also treated as Charlotte Linlin."""
    card.alternate_names = ['Charlotte Linlin']
    return True


# --- OP04-094: Trueno Bastardo ---
@register_effect("OP04-094", "MAIN", "KO cost 4 or less (cost 6 if 15+ trash)")
def trueno_bastardo_effect(game_state, player, card):
    """KO opponent's character with cost based on trash count."""
    opponent = get_opponent(game_state, player)
    max_cost = 6 if len(player.trash) >= 15 else 4
    targets = [c for c in opponent.cards_in_play
              if (getattr(c, 'cost', 0) or 0) <= max_cost]
    if targets:
        return create_ko_choice(
            game_state, player, targets, source_card=card,
            prompt=f"Choose opponent's cost {max_cost} or less to KO"
        )
    return False


# --- OP04-093: Gum-Gum King Kong Gun ---
@register_effect("OP04-093", "MAIN", "Dressrosa char +6000, if 15+ trash gains Double Attack")
def op04_093_king_kong_gun(game_state, player, card):
    dressrosa_chars = [c for c in player.cards_in_play
                       if 'Dressrosa' in (getattr(c, 'card_origin', '') or '')]
    if dressrosa_chars:
        target = dressrosa_chars[0]
        add_power_modifier(target, 6000)
        if check_trash_count(player, 15, 'ge'):
            target.double_attack = True
    return True


# --- OP04-111: Hera ---
@register_effect("OP04-111", "ACTIVATE_MAIN", "Trash Homies char and rest this: Set Charlotte Linlin active")
def op04_111_hera(game_state, player, card):
    homies = [c for c in player.cards_in_play
              if c != card and 'Homies' in (getattr(c, 'card_origin', '') or '')]
    if homies:
        to_trash = homies[0]
        player.cards_in_play.remove(to_trash)
        player.trash.append(to_trash)
        card.is_resting = True
        # Set Charlotte Linlin active
        linlins = [c for c in player.cards_in_play
                   if 'Charlotte Linlin' in (getattr(c, 'name', '') or '') and c.is_resting]
        if linlins:
            linlins[0].is_resting = False
    return True


# --- OP04-075: Nez-Palm Cannon ---
@register_effect("OP04-075", "COUNTER", "+6000 power, add DON if 2 or less life")
def op04_075_nez_palm(game_state, player, card):
    """Counter: +6000 power, add 1 DON if 2 or less life."""
    target = player.leader if player.leader else (player.cards_in_play[0] if player.cards_in_play else None)
    if target:
        add_power_modifier(target, 6000)
        if check_life_count(player, 2):
            add_don_from_deck(player, 1, set_active=False)
        return True
    return False


# --- OP04-098: Toko ---
@register_effect("OP04-098", "ON_PLAY", "Trash 2 Wano cards: If 1 or less life, add deck to life")
def op04_098_toko(game_state, player, card):
    """On Play: Trash 2 Land of Wano cards, if 1 or less life add deck card to life."""
    wano_cards = [c for c in player.hand
                  if 'land of wano' in (c.card_origin or '').lower()]
    if len(wano_cards) >= 2:
        for i in range(2):
            c = wano_cards[i]
            player.hand.remove(c)
            player.trash.append(c)
        if check_life_count(player, 1) and player.deck:
            deck_card = player.deck.pop(0)
            player.life_cards.append(deck_card)
        return True
    return False


# =============================================================================
# TRASH CONDITION CARDS - "If you have X or more cards in trash..."
# =============================================================================

# --- OP04-095: Barrier!! ---
@register_effect("OP04-095", "COUNTER", "+2000 power, +2000 more if 15+ trash")
def op04_095_barrier(game_state, player, card):
    """Counter: +2000 power, additional +2000 if 15+ cards in trash."""
    target = player.leader if player.leader else (player.cards_in_play[0] if player.cards_in_play else None)
    if target:
        add_power_modifier(target, 2000)
        if check_trash_count(player, 15):
            add_power_modifier(target, 2000)
        return True
    return False


# --- OP04-094: Trueno Bastardo ---
@register_effect("OP04-094", "MAIN", "KO cost 4 or less (cost 6 if 15+ trash)")
def op04_094_trueno(game_state, player, card):
    """Main: KO cost 4 or less (cost 6 or less if 15+ trash)."""
    max_cost = 6 if check_trash_count(player, 15) else 4
    return ko_opponent_character(game_state, player, max_cost=max_cost, source_card=card)


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
    """Once Per Turn, Rest 2: Draw 1 card. If you have 0 Characters, opponent trashes 1 from hand."""
    if hasattr(card, 'op04_001_used') and card.op04_001_used:
        return False
    active_don = player.don_pool.count("active")
    if len(active_don) >= 2:
        for don in active_don[:2]:
            don.is_resting = True
        draw_cards(player, 1)
        if len(player.cards_in_play) == 0:
            opponent = get_opponent(game_state, player)
            trash_from_hand(opponent, 1)
        card.op04_001_used = True
        return True
    return False


# --- OP04-019: Donquixote Doflamingo (Leader) ---
@register_effect("OP04-019", "end_of_turn", "[End of Your Turn] Set up to 2 DON active")
def op04_019_doffy_leader(game_state, player, card):
    """End of Your Turn: Set up to 2 of your DON cards as active."""
    rested_don = player.don_pool.count("rested")
    for don in rested_don[:2]:
        don.is_resting = False
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


@register_effect("OP04-020", "end_of_turn", "[End of Your Turn] Rest 1: K.O. cost 0")
def op04_020_issho_eot(game_state, player, card):
    """End of Your Turn, Rest 1: K.O. opponent's cost 0 Character."""
    active_don = player.don_pool.count("active")
    if active_don:
        active_don[0].is_resting = True
        opponent = get_opponent(game_state, player)
        cost_zero = [c for c in opponent.cards_in_play
                     if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 0]
        if cost_zero:
            target = cost_zero[0]
            opponent.cards_in_play.remove(target)
            opponent.trash.append(target)
        return True
    return False


# --- OP04-039: Rebecca (Leader) ---
@register_effect("OP04-039", "continuous", "This Leader cannot attack")
def op04_039_rebecca_continuous(game_state, player, card):
    """This Leader cannot attack."""
    card.cannot_attack = True
    return True


@register_effect("OP04-039", "activate", "[Activate: Main] Rest 1: If 6+ chars, draw 2")
def op04_039_rebecca_activate(game_state, player, card):
    """Once Per Turn, Rest 1: If you have 6 or more Characters, draw 2 cards."""
    if hasattr(card, 'op04_039_used') and card.op04_039_used:
        return False
    active_don = player.don_pool.count("active")
    if active_don and len(player.cards_in_play) >= 6:
        active_don[0].is_resting = True
        draw_cards(player, 2)
        card.op04_039_used = True
        return True
    return False


# --- OP04-040: Queen (Leader) ---
@register_effect("OP04-040", "on_attack", "[DON!! x1] If 4- life+hand, draw 1. If cost 8+ char, +1000")
def op04_040_queen_leader(game_state, player, card):
    """DON x1, When Attacking: If 4 or less life+hand, draw 1. If cost 8+ Character, +1000 power."""
    if getattr(card, 'attached_don', 0) >= 1:
        total = len(player.life_cards) + len(player.hand)
        if total <= 4:
            draw_cards(player, 1)
        cost_8_plus = [c for c in player.cards_in_play
                       if (getattr(c, 'cost', 0) or 0) >= 8]
        if cost_8_plus:
            card.power_modifier = getattr(card, 'power_modifier', 0) + 1000
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
        if player.deck:
            # Look at 5 cards and add Alabasta card
            top_cards = player.deck[:5]
            for c in top_cards:
                if 'Alabasta' in (c.card_origin or ''):
                    player.hand.append(c)
                    player.deck.remove(c)
                    break
        return True
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
            if player.don_pool:
                rested_don = player.don_pool.count("rested")
                if rested_don:
                    don = rested_don[0]
                    player.don_pool.remove(don)
                    if not hasattr(char, 'attached_don'):
                        char.attached_don = 0
                    char.attached_don.append(don)
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
            return create_power_reduction_choice(game_state, player, list(opponent.cards_in_play), -3000, source_card=card,
                                                prompt="Choose opponent's Character to give -3000 power")
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
        if getattr(revealed, 'card_type', '') == 'CHARACTER' and (getattr(revealed, 'power', 0) or 0) >= 6000:
            card.power_modifier = getattr(card, 'power_modifier', 0) + 3000
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
    rested = 0
    for don in player.don_pool:
        if not getattr(don, 'is_resting', False) and rested < 1:
            don.is_resting = True
            rested += 1
    if rested >= 1:
        opponent = get_opponent(game_state, player)
        for don in opponent.don_pool:
            if not getattr(don, 'is_resting', False):
                don.is_resting = True
                break
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


# --- OP04-026: Senor Pink ---
@register_effect("OP04-026", "on_attack", "[When Attacking] DON -1: Rest cost 4 or less, active 1 DON at end")
def op04_026_senor_pink(game_state, player, card):
    """When Attacking: Rest 1 DON to rest cost 4 or less and activate 1 DON at end."""
    rested = 0
    for don in player.don_pool:
        if not getattr(don, 'is_resting', False) and rested < 1:
            don.is_resting = True
            rested += 1
    if rested >= 1 and player.leader and 'Donquixote Pirates' in (player.leader.card_origin or ''):
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
    active_don = len([d for d in player.don_pool if not getattr(d, 'is_resting', False)])
    if attached >= 1 and active_don >= 2:
        card.is_resting = False
        return True
    return False


# --- OP04-029: Dellinger ---
@register_effect("OP04-029", "end_of_turn", "[End of Turn] Set 1 DON active")
def op04_029_dellinger(game_state, player, card):
    """End of Turn: Set 1 DON active."""
    for don in player.don_pool:
        if getattr(don, 'is_resting', False):
            don.is_resting = False
            break
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
    targets = [c for c in opponent.cards_in_play if getattr(c, 'is_resting', False)][:3]
    for target in targets:
        target.skip_next_refresh = True
    if opponent.leader and getattr(opponent.leader, 'is_resting', False):
        opponent.leader.skip_next_refresh = True
    return True


# --- OP04-032: Baby 5 ---
@register_effect("OP04-032", "end_of_turn", "[End of Turn] Trash this: Set 2 DON active")
def op04_032_baby5(game_state, player, card):
    """End of Turn: Trash this to set 2 DON active."""
    if card in player.cards_in_play:
        player.cards_in_play.remove(card)
        player.trash.append(card)
        activated = 0
        for don in player.don_pool:
            if getattr(don, 'is_resting', False) and activated < 2:
                don.is_resting = False
                activated += 1
        return True
    return False


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
    active_don = len([d for d in player.don_pool if not getattr(d, 'is_resting', False)])
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
    if len(player.hand) >= 2:
        trash_from_hand(player, 2, game_state, card)
        if player.deck:
            top_cards = player.deck[:5]
            for c in top_cards:
                if 'East Blue' in (c.card_origin or ''):
                    player.hand.append(c)
                    player.deck.remove(c)
                    break
        return True
    return False


# --- OP04-042: Ipponmatsu ---
@register_effect("OP04-042", "on_play", "[On Play] Slash attribute gains +3000, trash 1 from deck")
def op04_042_ipponmatsu(game_state, player, card):
    """On Play: Slash attribute character gains +3000, trash 1 from deck."""
    for c in player.cards_in_play:
        if getattr(c, 'attribute', '') == 'Slash':
            c.power_modifier = getattr(c, 'power_modifier', 0) + 3000
            break
    if player.deck:
        player.trash.append(player.deck.pop(0))
    return True


# --- OP04-043: Ulti ---
@register_effect("OP04-043", "on_attack", "[DON!! x1] [When Attacking] Return cost 2 or less to hand/deck")
def op04_043_ulti(game_state, player, card):
    """When Attacking with 1 DON: Return cost 2 or less to hand or deck."""
    attached = getattr(card, 'attached_don', 0)
    if attached >= 1:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
        if targets:
            return create_return_to_hand_choice(game_state, player, targets, source_card=card,
                                               prompt="Choose opponent's cost 2 or less Character to return to hand")
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
        return create_dual_target_choice(game_state, player, targets8, [], source_card=card,
                                        prompt1="Choose cost 8 or less Character to return to hand",
                                        prompt2="Choose cost 3 or less Character to return to hand",
                                        callback_action="kaido_return")
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
        if player.deck:
            top_cards = player.deck[:7]
            found = 0
            for c in list(top_cards):
                name = getattr(c, 'name', '')
                if ('Plague Rounds' in name or 'Ice Oni' in name) and found < 2:
                    player.hand.append(c)
                    player.deck.remove(c)
                    found += 1
    return True


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
        trash_from_hand(player, 1, game_state, card)
        draw_cards(player, 1)
        return True
    return False


# --- OP04-051: Who's Who ---
@register_effect("OP04-051", "on_play", "[On Play] Look at 5, add Animal Kingdom card")
def op04_051_whos_who(game_state, player, card):
    """On Play: Look at 5 and add Animal Kingdom card."""
    if player.deck:
        top_cards = player.deck[:5]
        for c in top_cards:
            if 'Animal Kingdom Pirates' in (c.card_origin or '') and getattr(c, 'name', '') != "Who's Who":
                player.hand.append(c)
                player.deck.remove(c)
                break
    return True


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
            card_to_bottom = player.hand.pop()
            player.deck.append(card_to_bottom)
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
            player.cards_in_play.remove(card)
            player.trash.append(card)
            add_don_from_deck(player, 1, rested=True)
            return True
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
                if player.cards_in_play:
                    return create_power_boost_choice(game_state, player, list(player.cards_in_play), 1000, source_card=card,
                                                    prompt="Choose your Character to give +1000 power")
                return True
    return False


# --- OP04-064: Ms. All Sunday ---
@register_effect("OP04-064", "on_play", "[On Play] Add 1 DON (rested), draw 1 if 6+ DON")
def op04_064_ms_all_sunday(game_state, player, card):
    """On Play: Add 1 DON rested. Draw 1 if 6+ DON."""
    add_don_from_deck(player, 1, rested=True)
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
    if player.deck:
        top_cards = player.deck[:5]
        for c in top_cards:
            if 'Baroque Works' in (c.card_origin or ''):
                player.hand.append(c)
                player.deck.remove(c)
                break
    return True


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
        # Would need to get attacker's power - simplified
        card.power_modifier = getattr(card, 'power_modifier', 0) + 4000
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
        card.power_modifier = getattr(card, 'power_modifier', 0) + 1000
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
        # Player chooses which Baroque Works character to trash
        return create_ko_choice(game_state, player, bw_chars, source_card=card,
                               prompt="Choose your Baroque Works Character to trash",
                               callback_action="trash_bw_add_don")
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
            return create_cost_reduction_choice(game_state, player, list(opponent.cards_in_play), -4, source_card=card,
                                               prompt="Choose opponent's Character to give -4 cost",
                                               callback_action="orlumbus_cost_then_ko")
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
        if player.deck:
            player.trash.append(player.deck.pop(0))
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 1]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's cost 1 or less Character to K.O.")
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
    if player.deck:
        top_cards = player.deck[:3]
        for c in list(top_cards):
            types = (c.card_origin or '')
            if 'CP' in types and getattr(c, 'name', '') != 'Stussy' and (getattr(c, 'cost', 0) or 0) <= 2:
                player.deck.remove(c)
                player.cards_in_play.append(c)
                break
        # Trash the rest
        remaining = [c for c in player.deck[:3] if c in player.deck]
        for c in remaining:
            player.deck.remove(c)
            player.trash.append(c)
    return True


# --- OP04-085: Suleiman ---
@register_effect("OP04-085", "on_play", "[On Play] If Dressrosa Leader, -2 cost, trash 1")
def op04_085_suleiman_play(game_state, player, card):
    """On Play: If Dressrosa Leader, give -2 cost and trash 1 from deck."""
    if player.leader and 'Dressrosa' in (player.leader.card_origin or ''):
        if player.deck:
            player.trash.append(player.deck.pop(0))
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            return create_cost_reduction_choice(game_state, player, list(opponent.cards_in_play), -2, source_card=card,
                                               prompt="Choose opponent's Character to give -2 cost")
        return True
    return False


@register_effect("OP04-085", "on_attack", "[When Attacking] If Dressrosa Leader, -2 cost, trash 1")
def op04_085_suleiman_attack(game_state, player, card):
    """When Attacking: If Dressrosa Leader, give -2 cost and trash 1 from deck."""
    if player.leader and 'Dressrosa' in (player.leader.card_origin or ''):
        if player.deck:
            player.trash.append(player.deck.pop(0))
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            return create_cost_reduction_choice(game_state, player, list(opponent.cards_in_play), -2, source_card=card,
                                               prompt="Choose opponent's Character to give -2 cost")
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
        for _ in range(7):
            card_to_return = player.trash.pop()
            player.deck.append(card_to_return)
        card.is_resting = False
        card.skip_next_refresh = True
        card.op04_090_used = True
        return True
    return False


# --- OP04-091: Leo ---
@register_effect("OP04-091", "on_play", "[On Play] Rest Leader: If Dressrosa Leader, K.O. cost 1 or less, trash 2")
def op04_091_leo(game_state, player, card):
    """On Play: Rest Leader to K.O. cost 1 or less and trash 2 if Dressrosa Leader."""
    if player.leader and 'Dressrosa' in (player.leader.card_origin or ''):
        if not getattr(player.leader, 'is_resting', False):
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


# --- OP04-092: Rebecca ---
@register_effect("OP04-092", "on_play", "[On Play] Look at 3, add Dressrosa card")
def op04_092_rebecca(game_state, player, card):
    """On Play: Look at 3 and add Dressrosa card."""
    if player.deck:
        top_cards = player.deck[:3]
        for c in list(top_cards):
            if 'Dressrosa' in (c.card_origin or '') and getattr(c, 'name', '') != 'Rebecca':
                player.hand.append(c)
                player.deck.remove(c)
                break
        # Trash the rest
        remaining = player.deck[:3]
        for c in list(remaining):
            player.deck.remove(c)
            player.trash.append(c)
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
        for _ in range(2):
            wano = wano_cards.pop()
            player.hand.remove(wano)
            player.trash.append(wano)
        if player.deck:
            player.life_cards.append(player.deck.pop(0))
        return True
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
            # Player chooses which trigger card to trash, then which to rest
            return create_hand_discard_choice(game_state, player, trigger_cards, source_card=card,
                                             prompt="Choose a Trigger card to trash",
                                             callback_action="amande_trash_then_rest")
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
        return create_bottom_deck_choice(game_state, player, targets, source_card=card,
                                        prompt="Choose opponent's cost 3 or less to add to their Life",
                                        callback_action="add_to_opponent_life")
    return True


# --- OP04-111: Hera ---
@register_effect("OP04-111", "activate", "[Activate: Main] Trash Homies and rest: Set Charlotte Linlin active")
def op04_111_hera(game_state, player, card):
    """Activate: Trash Homies and rest to set Charlotte Linlin active."""
    homies = [c for c in player.cards_in_play if 'Homies' in (c.card_origin or '') and c != card]
    if homies and not getattr(card, 'is_resting', False):
        card.is_resting = True
        # Player chooses which Homies to trash
        return create_ko_choice(game_state, player, homies, source_card=card,
                               prompt="Choose Homies Character to trash",
                               callback_action="hera_trash_homies")
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
        if c != card and 'Red' in getattr(c, 'colors', []) and (getattr(c, 'cost', 0) or 0) >= 3:
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
    card.is_resting = True
    for c in list(player.hand):
        if 'Green' in getattr(c, 'colors', []) and (getattr(c, 'cost', 0) or 0) == 5:
            player.hand.remove(c)
            player.cards_in_play.append(c)
            break
    return True


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

