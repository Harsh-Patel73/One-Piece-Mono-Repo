"""
Hardcoded effects for OP09 cards.
"""

from ..hardcoded import (
    create_bottom_deck_choice, create_ko_choice, create_own_character_choice, create_play_from_hand_choice,
    create_return_to_hand_choice, create_target_choice, draw_cards, get_opponent,
    register_effect, search_top_cards, set_active, trash_from_hand,
)


# --- OP09-014: Limejuice ---
@register_effect("OP09-014", "ON_PLAY", "Opponent cannot activate Blocker with 4000 or less power")
def limejuice_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    for c in opponent.cards_in_play:
        if (getattr(c, 'power', 0) or 0) <= 4000:
            c.blocker_disabled_this_turn = True
    return True


# --- OP09-033: Nico Robin ---
@register_effect("OP09-033", "ON_PLAY", "If 2+ rested chars, ODYSSEY/Straw Hat can't be KO'd by effects")
def robin_op09_effect(game_state, player, card):
    rested = [c for c in player.cards_in_play if c.is_resting]
    if len(rested) >= 2:
        for c in player.cards_in_play:
            types = (c.card_origin or '').lower()
            if 'odyssey' in types or 'straw hat crew' in types:
                c.protected_from_ko = True
        return True
    return False


# --- OP09-029: Tony Tony.Chopper ---
@register_effect("OP09-029", "END_OF_TURN", "Set ODYSSEY cost 4 or less active")
def chopper_op09_effect(game_state, player, card):
    odyssey = [c for c in player.cards_in_play
              if 'odyssey' in (c.card_origin or '').lower()
              and (getattr(c, 'cost', 0) or 0) <= 4
              and c.is_resting]
    if odyssey:
        return create_target_choice(
            game_state, player, odyssey,
            callback_action="set_active",
            source_card=card,
            prompt="Choose your ODYSSEY cost 4 or less Character to set active"
        )
    return False


# =============================================================================
# LEADER CONDITION CARDS - Other Types
# =============================================================================

# --- OP09-023: Adio ---
@register_effect("OP09-023", "ON_PLAY", "If Leader is ODYSSEY, set 3 DON active")
def op09_023_adio(game_state, player, card):
    if check_leader_type(player, "ODYSSEY"):
        set_active(player.don_pool[:3])
    return True


# --- OP09-043: Alvida ---
@register_effect("OP09-043", "ON_KO", "If Leader is Cross Guild, play cost 5 or less from hand")
def op09_043_alvida(game_state, player, card):
    if check_leader_type(player, "Cross Guild"):
        chars = [c for c in player.hand
                 if getattr(c, 'card_type', '') == 'CHARACTER'
                 and (getattr(c, 'cost', 0) or 0) <= 5
                 and 'Alvida' not in (getattr(c, 'name', '') or '')]
        if chars:
            return create_play_from_hand_choice(
                game_state, player, chars, source_card=card,
                rest_on_play=False,
                prompt="Choose a cost 5 or less Character to play from hand"
            )
    return False


# =============================================================================
# MORE LEADER CONDITION CARDS - Blackbeard Pirates
# =============================================================================

# --- OP09-098: Black Hole ---
@register_effect("OP09-098", "MAIN", "If Leader is Blackbeard Pirates, negate effect and KO cost 4 or less")
def op09_098_black_hole(game_state, player, card):
    if check_leader_type(player, "Blackbeard Pirates"):
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            target = opponent.cards_in_play[0]
            target.effect_negated = True
            if (getattr(target, 'cost', 0) or 0) <= 4:
                opponent.cards_in_play.remove(target)
                opponent.trash.append(target)
    return True


# --- OP09-112: Belo Betty ---
@register_effect("OP09-112", "ON_PLAY", "If 2 or less life, draw 1")
def op09_112_belo_betty(game_state, player, card):
    """On Play: If 2 or less life, draw 1 card."""
    if check_life_count(player, 2):
        draw_cards(player, 1)
        return True
    return False


# --- OP09-030: Trafalgar Law ---
@register_effect("OP09-030", "ON_PLAY", "Return char to hand: Play ODYSSEY cost 3 or less")
def op09_030_law(game_state, player, card):
    """On Play: Return char to hand, play ODYSSEY cost 3 or less from hand."""
    chars = [c for c in player.cards_in_play if c != card]
    if chars:
        return create_own_character_choice(
            game_state, player, chars,
            source_card=card,
            callback_action="law_return_then_play_odyssey",
            prompt="Choose your Character to return to hand (then play ODYSSEY cost 3 or less)"
        )
    return False


# --- OP09-104: Sabo ---
@register_effect("OP09-104", "ON_PLAY", "Add Rev Army to life face-up, then add life to hand if 2+ life")
def op09_104_sabo(game_state, player, card):
    """On Play: Add Rev Army from hand to life face-up, if 2+ life add life to hand."""
    rev_army = [c for c in player.hand
                if 'revolutionary army' in (c.card_origin or '').lower()
                and getattr(c, 'card_type', '') == 'CHARACTER']
    if rev_army:
        char = rev_army[0]
        player.hand.remove(char)
        char.is_face_up = True
        player.life_cards.append(char)
    if len(player.life_cards) >= 2:
        life = player.life_cards.pop()
        player.hand.append(life)
    return True


# --- OP09-001: Shanks (Leader) ---
@register_effect("OP09-001", "on_opponent_attack", "[Once Per Turn] When opponent attacks, give -1000 power")
def op09_001_shanks_leader(game_state, player, card):
    """Once Per Turn: When opponent attacks, give opponent's Leader or Character -1000 power."""
    if hasattr(card, 'op09_001_used') and card.op09_001_used:
        return False
    opponent = get_opponent(game_state, player)
    if opponent.cards_in_play:
        target = opponent.cards_in_play[0]
        target.power_modifier = getattr(target, 'power_modifier', 0) - 1000
    elif opponent.leader:
        opponent.leader.power_modifier = getattr(opponent.leader, 'power_modifier', 0) - 1000
    card.op09_001_used = True
    return True


# --- OP09-022: Lim (Leader) ---
@register_effect("OP09-022", "continuous", "Your Characters are played rested")
def op09_022_lim_continuous(game_state, player, card):
    """Your Character cards are played rested."""
    player.chars_played_rested = True
    return True


@register_effect("OP09-022", "activate", "[Activate: Main] Rest 3 DON: Add 1 DON active")
def op09_022_lim_activate(game_state, player, card):
    """Once Per Turn, Rest 3 DON: Add 1 DON from deck and set it active."""
    if hasattr(card, 'op09_022_used') and card.op09_022_used:
        return False
    active_don = player.don_pool.count("active")
    if len(active_don) >= 3:
        for don in active_don[:3]:
            don.is_resting = True
        if hasattr(player, 'don_deck') and player.don_deck:
            new_don = player.don_deck.pop(0)
            new_don.is_resting = False
            player.don_pool.append(new_don)
        card.op09_022_used = True
        return True
    return False


# --- OP09-042: Buggy (Leader) ---
@register_effect("OP09-042", "activate", "[Activate: Main] Rest 5 DON, trash 1: Play Cross Guild from hand")
def op09_042_buggy_leader(game_state, player, card):
    """Rest 5 DON, trash 1 from hand: Play Cross Guild Character from hand."""
    active_don = player.don_pool.count("active")
    if len(active_don) >= 5 and player.hand:
        for don in active_don[:5]:
            don.is_resting = True
        trash_from_hand(player, 1, game_state, card)
        cross_guild = [c for c in player.hand
                       if getattr(c, 'card_type', '') == 'CHARACTER'
                       and 'cross guild' in (c.card_origin or '').lower()]
        if cross_guild:
            to_play = cross_guild[0]
            player.hand.remove(to_play)
            player.cards_in_play.append(to_play)
        return True
    return False


# --- OP09-061: Monkey.D.Luffy (Leader) ---
@register_effect("OP09-061", "continuous", "[DON!! x1] All chars +1 cost")
def op09_061_luffy_continuous(game_state, player, card):
    """DON x1: All of your Characters gain +1 cost."""
    if getattr(card, 'attached_don', 0) >= 1:
        for char in player.cards_in_play:
            char.cost_modifier = getattr(char, 'cost_modifier', 0) + 1
        return True
    return False


@register_effect("OP09-061", "on_don_return", "[Your Turn] When 2+ DON returned, draw 1")
def op09_061_luffy_don_return(game_state, player, card):
    """Your Turn, Once Per Turn: When 2+ DON returned to deck, draw 1."""
    if hasattr(card, 'op09_061_used') and card.op09_061_used:
        return False
    draw_cards(player, 1)
    card.op09_061_used = True
    return True


# --- OP09-062: Nico Robin (Leader) ---
@register_effect("OP09-062", "continuous", "[Banish] This Leader has Banish")
def op09_062_robin_continuous(game_state, player, card):
    """This Leader has Banish - damage cards are trashed without activating Trigger."""
    card.has_banish = True
    return True


@register_effect("OP09-062", "on_attack", "[When Attacking] Trash Trigger card: Give char Rush or +2000")
def op09_062_robin_attack(game_state, player, card):
    """When Attacking: Trash a card with Trigger from hand, give Character Rush or +2000."""
    trigger_cards = [c for c in player.hand if getattr(c, 'trigger', '')]
    if trigger_cards:
        to_trash = trigger_cards[0]
        player.hand.remove(to_trash)
        player.trash.append(to_trash)
        if player.cards_in_play:
            target = player.cards_in_play[0]
            target.power_modifier = getattr(target, 'power_modifier', 0) + 2000
        return True
    return False


# --- OP09-081: Marshall.D.Teach (Leader) ---
@register_effect("OP09-081", "continuous", "Your [On Play] effects are negated")
def op09_081_teach_continuous(game_state, player, card):
    """Your [On Play] effects are negated."""
    player.on_play_negated = True
    return True


@register_effect("OP09-081", "activate", "[Activate: Main] Trash 1: Opponent's [On Play] negated")
def op09_081_teach_activate(game_state, player, card):
    """Trash 1 from hand: Opponent's [On Play] effects are negated until end of turn."""
    if player.hand:
        trash_from_hand(player, 1, game_state, card)
        opponent = get_opponent(game_state, player)
        opponent.on_play_negated = True
        return True
    return False


# =============================================================================
# OP09 CHARACTER EFFECTS
# =============================================================================

# --- OP09-002: Uta ---
@register_effect("OP09-002", "on_play", "[On Play] Look at 5, add Red-Haired Pirates")
def op09_002_uta(game_state, player, card):
    """On Play: Look at 5, add Red-Haired Pirates card."""
    looked = player.deck[:5] if len(player.deck) >= 5 else player.deck[:]
    for c in looked:
        if 'Red-Haired Pirates' in (c.card_origin or ''):
            player.deck.remove(c)
            player.hand.append(c)
            break
    return True


# --- OP09-003: Shachi & Penguin ---
@register_effect("OP09-003", "on_attack", "[When Attacking] Give opponent -2000 power")
def op09_003_shachi_penguin(game_state, player, card):
    """When Attacking: Give opponent's Character -2000 power."""
    opponent = get_opponent(game_state, player)
    if opponent.cards_in_play:
        opponent.cards_in_play[0].power_modifier = getattr(opponent.cards_in_play[0], 'power_modifier', 0) - 2000
    return True


# --- OP09-004: Shanks ---
@register_effect("OP09-004", "continuous", "[Continuous] Give all opponent's Characters -1000 power")
def op09_004_shanks_continuous(game_state, player, card):
    """Continuous: Give all opponent's Characters -1000 power."""
    opponent = get_opponent(game_state, player)
    for c in opponent.cards_in_play:
        c.power_modifier = getattr(c, 'power_modifier', 0) - 1000
    return True


@register_effect("OP09-004", "rush", "[Rush]")
def op09_004_shanks_rush(game_state, player, card):
    """Rush."""
    card.has_rush = True
    return True


# --- OP09-005: Silvers Rayleigh ---
@register_effect("OP09-005", "blocker", "[Blocker]")
def op09_005_rayleigh_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP09-005", "on_play", "[On Play] If opponent has 2+ base 5000 power, draw 2 trash 1")
def op09_005_rayleigh_on_play(game_state, player, card):
    """On Play: If opponent has 2+ Characters with base 5000+ power, draw 2 trash 1."""
    opponent = get_opponent(game_state, player)
    high_power = [c for c in opponent.cards_in_play if (getattr(c, 'power', 0) or 0) >= 5000]
    if len(high_power) >= 2:
        draw_cards(player, 2)
        trash_from_hand(player, 1, game_state, card)
    return True


# --- OP09-007: Heat ---
@register_effect("OP09-007", "blocker", "[Blocker]")
def op09_007_heat_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP09-007", "on_play", "[On Play] Leader with 4000 power or less +1000")
def op09_007_heat_on_play(game_state, player, card):
    """On Play: Leader with 4000 or less gains +1000."""
    if player.leader and (getattr(player.leader, 'power', 0) or 0) <= 4000:
        player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 1000
    return True


# --- OP09-008: Building Snake ---
@register_effect("OP09-008", "activate", "[Activate: Main] Bottom deck this: Opponent -3000 power")
def op09_008_building_snake(game_state, player, card):
    """Activate: Bottom deck this to give opponent -3000 power."""
    if card in player.cards_in_play:
        player.cards_in_play.remove(card)
        player.deck.append(card)
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            opponent.cards_in_play[0].power_modifier = getattr(opponent.cards_in_play[0], 'power_modifier', 0) - 3000
        return True
    return False


# --- OP09-009: Benn.Beckman ---
@register_effect("OP09-009", "on_play", "[On Play] Trash opponent's 6000 power or less")
def op09_009_beckman(game_state, player, card):
    """On Play: Trash opponent's Character with 6000 power or less."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'power', 0) or 0) <= 6000]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                               prompt="Choose opponent's 6000 power or less to trash")
    return True


# --- OP09-010: Bonk Punch ---
@register_effect("OP09-010", "on_play", "[On Play] Play Monster from hand")
def op09_010_bonk_punch_on_play(game_state, player, card):
    """On Play: Play Monster from hand."""
    for c in list(player.hand):
        if getattr(c, 'name', '') == 'Monster':
            player.hand.remove(c)
            player.cards_in_play.append(c)
            break
    return True


@register_effect("OP09-010", "on_attack", "[When Attacking] With DON x1, +2000 power")
def op09_010_bonk_punch_on_attack(game_state, player, card):
    """When Attacking: With DON, +2000 power."""
    if getattr(card, 'attached_don', 0) >= 1:
        card.power_modifier = getattr(card, 'power_modifier', 0) + 2000
    return True


# --- OP09-011: Hongo ---
@register_effect("OP09-011", "activate", "[Activate: Main] Rest: If Red-Haired leader, opponent -2000")
def op09_011_hongo(game_state, player, card):
    """Activate: Rest to give opponent -2000 if Red-Haired leader."""
    if card.is_resting:
        return False
    if player.leader and 'Red-Haired Pirates' in (player.leader.card_origin or ''):
        card.is_resting = True
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            opponent.cards_in_play[0].power_modifier = getattr(opponent.cards_in_play[0], 'power_modifier', 0) - 2000
        return True
    return False


# --- OP09-012: Monster ---
@register_effect("OP09-012", "replacement", "[Replacement] If Bonk Punch would be K.O.'d, trash this instead")
def op09_012_monster(game_state, player, card):
    """Replacement: Can be trashed to prevent Bonk Punch K.O."""
    card.protects = 'Bonk Punch'
    return True


# --- OP09-013: Yasopp ---
@register_effect("OP09-013", "on_play", "[On Play] Leader +1000 until opponent's next turn")
def op09_013_yasopp_on_play(game_state, player, card):
    """On Play: Leader +1000 until opponent's next turn."""
    if player.leader:
        player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 1000
    return True


@register_effect("OP09-013", "on_attack", "[When Attacking] With DON x1, opponent -1000")
def op09_013_yasopp_on_attack(game_state, player, card):
    """When Attacking: With DON, opponent -1000."""
    if getattr(card, 'attached_don', 0) >= 1:
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            opponent.cards_in_play[0].power_modifier = getattr(opponent.cards_in_play[0], 'power_modifier', 0) - 1000
    return True


# --- OP09-014: Limejuice ---
@register_effect("OP09-014", "on_play", "[On Play] Disable Blocker 4000 power or less this turn")
def op09_014_limejuice(game_state, player, card):
    """On Play: Opponent's Blocker 4000 power or less can't block this turn."""
    opponent = get_opponent(game_state, player)
    for c in opponent.cards_in_play:
        if getattr(c, 'has_blocker', False) and (getattr(c, 'power', 0) or 0) <= 4000:
            c.blocker_disabled = True
            break
    return True


# --- OP09-015: Lucky.Roux ---
@register_effect("OP09-015", "blocker", "[Blocker]")
def op09_015_lucky_roux_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP09-015", "on_ko", "[On K.O.] If Red-Haired leader, K.O. base 6000 power or less")
def op09_015_lucky_roux_on_ko(game_state, player, card):
    """On K.O.: If Red-Haired leader, K.O. opponent's base 6000 power or less."""
    if player.leader and 'Red-Haired Pirates' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'power', 0) or 0) <= 6000]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's 6000 power or less to K.O.")
    return True


# --- OP09-017: Wire ---
@register_effect("OP09-017", "don_attached", "[DON!! x1] If Kid Pirates leader 7000+ power, gain Rush")
def op09_017_wire(game_state, player, card):
    """With DON, if Kid Pirates leader has 7000+ power, gain Rush."""
    if getattr(card, 'attached_don', 0) >= 1:
        if player.leader and 'Kid Pirates' in (player.leader.card_origin or ''):
            leader_power = (getattr(player.leader, 'power', 0) or 0) + getattr(player.leader, 'power_modifier', 0)
            if leader_power >= 7000:
                card.has_rush = True
    return True


# --- OP09-023: Adio ---
@register_effect("OP09-023", "on_play", "[On Play] If ODYSSEY leader, set 3 DON active")
def op09_023_adio_on_play(game_state, player, card):
    """On Play: If ODYSSEY leader, set 3 DON active."""
    if player.leader and 'ODYSSEY' in (player.leader.card_origin or ''):
        count = 0
        for d in getattr(player, 'don_cards', []):
            if getattr(d, 'is_resting', False) and count < 3:
                d.is_resting = False
                count += 1
    return True


@register_effect("OP09-023", "on_opponent_attack", "[On Opponent's Attack] Rest DON: +2000 power")
def op09_023_adio_defense(game_state, player, card):
    """On Opponent's Attack: Rest DON to give +2000 power."""
    if getattr(card, 'op09_023_used', False):
        return False
    for d in getattr(player, 'don_cards', []):
        if not getattr(d, 'is_resting', False):
            d.is_resting = True
            card.power_modifier = getattr(card, 'power_modifier', 0) + 2000
            card.op09_023_used = True
            return True
    return False


# --- OP09-024: Usopp ---
@register_effect("OP09-024", "on_play", "[On Play] If 2+ rested Characters, draw 2 trash 2")
def op09_024_usopp(game_state, player, card):
    """On Play: If 2+ rested Characters, draw 2 and trash 2."""
    rested = sum(1 for c in player.cards_in_play if c.is_resting)
    if rested >= 2:
        draw_cards(player, 2)
        trash_from_hand(player, 2, game_state, card)
    return True


# --- OP09-025: Crocodile ---
@register_effect("OP09-025", "continuous", "[Continuous] If ODYSSEY leader, can't be K.O.'d in battle by Leaders")
def op09_025_crocodile(game_state, player, card):
    """Continuous: If ODYSSEY leader, can't be K.O.'d by Leader battle."""
    if player.leader and 'ODYSSEY' in (player.leader.card_origin or ''):
        card.leader_battle_protection = True
    return True


# --- OP09-026: Sakazuki ---
@register_effect("OP09-026", "on_play", "[On Play] If 2+ rested Characters, K.O. cost 5 or less")
def op09_026_sakazuki(game_state, player, card):
    """On Play: If 2+ rested Characters, K.O. opponent's cost 5 or less."""
    rested = sum(1 for c in player.cards_in_play if c.is_resting)
    if rested >= 2:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 5]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's cost 5 or less to K.O.")
    return True


# --- OP09-027: Sabo ---
@register_effect("OP09-027", "on_attack", "[When Attacking] If 3+ rested Characters, draw 1")
def op09_027_sabo(game_state, player, card):
    """When Attacking: If 3+ rested Characters, draw 1."""
    if getattr(card, 'op09_027_used', False):
        return False
    rested = sum(1 for c in player.cards_in_play if c.is_resting)
    if rested >= 3:
        draw_cards(player, 1)
        card.op09_027_used = True
        return True
    return False


# --- OP09-028: Jinbe ---
@register_effect("OP09-028", "blocker", "[Blocker]")
def op09_028_jinbe_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP09-028", "on_play", "[On Play] Draw 1, then bottom deck 1")
def op09_028_jinbe_on_play(game_state, player, card):
    """On Play: Draw 1, then place 1 at bottom of deck."""
    draw_cards(player, 1)
    if player.hand:
        c = player.hand.pop(0)
        player.deck.append(c)
    return True


# --- OP09-029: Trafalgar Law ---
@register_effect("OP09-029", "on_attack", "[When Attacking] If ODYSSEY leader, return cost 3 or less to hand")
def op09_029_law(game_state, player, card):
    """When Attacking: If ODYSSEY leader, return opponent's cost 3 or less to hand."""
    if player.leader and 'ODYSSEY' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
        if targets:
            return create_return_to_hand_choice(game_state, player, targets, source_card=card,
                                               prompt="Choose opponent's cost 3 or less to return to hand")
    return True


# --- OP09-030: Nami ---
@register_effect("OP09-030", "on_play", "[On Play] If ODYSSEY leader, draw 2 trash 1")
def op09_030_nami(game_state, player, card):
    """On Play: If ODYSSEY leader, draw 2 and trash 1."""
    if player.leader and 'ODYSSEY' in (player.leader.card_origin or ''):
        draw_cards(player, 2)
        trash_from_hand(player, 1, game_state, card)
    return True


# --- OP09-031: Boa Hancock ---
@register_effect("OP09-031", "on_play", "[On Play] Give your rested Character +4000 power")
def op09_031_hancock(game_state, player, card):
    """On Play: Give your rested Character +4000 power."""
    for c in player.cards_in_play:
        if c.is_resting and c != card:
            c.power_modifier = getattr(c, 'power_modifier', 0) + 4000
            break
    return True


# --- OP09-032: Monkey.D.Luffy ---
@register_effect("OP09-032", "on_play", "[On Play] If ODYSSEY leader and 3+ rested, K.O. cost 6 or less")
def op09_032_luffy_on_play(game_state, player, card):
    """On Play: If ODYSSEY leader and 3+ rested, K.O. cost 6 or less."""
    if player.leader and 'ODYSSEY' in (player.leader.card_origin or ''):
        rested = sum(1 for c in player.cards_in_play if c.is_resting)
        if rested >= 3:
            opponent = get_opponent(game_state, player)
            targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 6]
            if targets:
                return create_ko_choice(game_state, player, targets, source_card=card,
                                       prompt="Choose opponent's cost 6 or less to K.O.")
    return True


@register_effect("OP09-032", "on_attack", "[When Attacking] This and one rested Character +2000")
def op09_032_luffy_on_attack(game_state, player, card):
    """When Attacking: This Character and one rested Character +2000."""
    card.power_modifier = getattr(card, 'power_modifier', 0) + 2000
    for c in player.cards_in_play:
        if c.is_resting and c != card:
            c.power_modifier = getattr(c, 'power_modifier', 0) + 2000
            break
    return True


# --- OP09-033: Roronoa Zoro ---
@register_effect("OP09-033", "on_play", "[On Play] If ODYSSEY leader and 2+ rested, play cost 3 or less from hand rested")
def op09_033_zoro(game_state, player, card):
    """On Play: If ODYSSEY leader and 2+ rested, play cost 3 or less from hand rested."""
    if player.leader and 'ODYSSEY' in (player.leader.card_origin or ''):
        rested = sum(1 for c in player.cards_in_play if c.is_resting)
        if rested >= 2:
            for c in list(player.hand):
                if getattr(c, 'card_type', '') == 'CHARACTER' and (getattr(c, 'cost', 0) or 0) <= 3:
                    player.hand.remove(c)
                    c.is_resting = True
                    player.cards_in_play.append(c)
                    break
    return True


# --- OP09-040: Izou ---
@register_effect("OP09-040", "on_play", "[On Play] Look at 5, add Whitebeard Pirates")
def op09_040_izou(game_state, player, card):
    """On Play: Look at 5, add Whitebeard Pirates card."""
    def filter_fn(c):
        return 'Whitebeard Pirates' in (c.card_origin or '')
    search_top_cards(game_state, player, 5, add_count=1, filter_fn=filter_fn,
                     source_card=card,
                     prompt="Look at top 5. Choose a Whitebeard Pirates card to add to hand.")
    return True


# --- OP09-041: Crocodile ---
@register_effect("OP09-041", "blocker", "[Blocker]")
def op09_041_crocodile_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP09-041", "on_play", "[On Play] Return your Character to hand: Bottom deck cost 2 or less")
def op09_041_crocodile_on_play(game_state, player, card):
    """On Play: Return your Character to bottom deck opponent's cost 2 or less."""
    other_chars = [c for c in player.cards_in_play if c != card]
    if other_chars:
        # TODO: Should let player choose which of their characters to bounce
        bounce = other_chars[0]
        player.cards_in_play.remove(bounce)
        player.hand.append(bounce)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
        if targets:
            return create_bottom_deck_choice(game_state, player, targets, source_card=card,
                                            prompt="Choose opponent's cost 2 or less to place at deck bottom")
    return True


# --- OP09-042: Sengoku ---
@register_effect("OP09-042", "on_play", "[On Play] If Navy leader and 3+ life, bottom deck cost 4 or less")
def op09_042_sengoku(game_state, player, card):
    """On Play: If Navy leader and 3+ life, bottom deck opponent's cost 4 or less."""
    if player.leader and 'Navy' in (player.leader.card_origin or ''):
        if len(player.life_cards) >= 3:
            opponent = get_opponent(game_state, player)
            targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
            if targets:
                return create_bottom_deck_choice(game_state, player, targets, source_card=card,
                                                prompt="Choose opponent's cost 4 or less to place at deck bottom")
    return True


# --- OP09-043: Emporio.Ivankov ---
@register_effect("OP09-043", "on_play", "[On Play] Place 1 from hand at bottom of deck: Bottom deck cost 3 or less")
def op09_043_ivankov(game_state, player, card):
    """On Play: Bottom deck 1 from hand to bottom deck opponent's cost 3 or less."""
    if player.hand:
        # TODO: Should let player choose which card from hand to bottom deck
        c = player.hand.pop(0)
        player.deck.append(c)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
        if targets:
            return create_bottom_deck_choice(game_state, player, targets, source_card=card,
                                            prompt="Choose opponent's cost 3 or less to place at deck bottom")
    return True


# --- OP09-044: Tsuru ---
@register_effect("OP09-044", "blocker", "[Blocker]")
def op09_044_tsuru_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP09-044", "on_play", "[On Play] Rest: If Navy leader, bottom deck cost 1 or less")
def op09_044_tsuru_on_play(game_state, player, card):
    """On Play: Rest this to bottom deck cost 1 or less if Navy leader."""
    if player.leader and 'Navy' in (player.leader.card_origin or ''):
        card.is_resting = True
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 1]
        if targets:
            return create_bottom_deck_choice(game_state, player, targets, source_card=card,
                                            prompt="Choose opponent's cost 1 or less to place at deck bottom")
    return True


# --- OP09-045: Donquixote Doflamingo ---
@register_effect("OP09-045", "on_play", "[On Play] If Navy leader, return 2 cost 3 or less to hand")
def op09_045_doflamingo(game_state, player, card):
    """On Play: If Navy leader, return 2 opponent's cost 3 or less to hand."""
    if player.leader and 'Navy' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
        for target in targets[:2]:
            opponent.cards_in_play.remove(target)
            opponent.hand.append(target)
    return True


# --- OP09-046: Hina ---
@register_effect("OP09-046", "on_play", "[On Play] If Navy leader, draw 2")
def op09_046_hina(game_state, player, card):
    """On Play: If Navy leader, draw 2."""
    if player.leader and 'Navy' in (player.leader.card_origin or ''):
        draw_cards(player, 2)
    return True


# --- OP09-047: Portgas.D.Ace ---
@register_effect("OP09-047", "on_play", "[On Play] Look at 5, reveal Whitebeard Pirates cost 3 or less and play rested")
def op09_047_ace(game_state, player, card):
    """On Play: Look at 5, play Whitebeard Pirates cost 3 or less rested."""
    looked = player.deck[:5] if len(player.deck) >= 5 else player.deck[:]
    for c in looked:
        if 'Whitebeard Pirates' in (c.card_origin or '') and (getattr(c, 'cost', 0) or 0) <= 3:
            if getattr(c, 'card_type', '') == 'CHARACTER':
                player.deck.remove(c)
                c.is_resting = True
                player.cards_in_play.append(c)
                break
    return True


# --- OP09-048: Marco ---
@register_effect("OP09-048", "on_play", "[On Play] If Whitebeard leader and 0 life, add life from deck")
def op09_048_marco(game_state, player, card):
    """On Play: If Whitebeard leader and 0 life, add deck to life."""
    if player.leader and 'Whitebeard Pirates' in (player.leader.card_origin or ''):
        if len(player.life_cards) == 0 and player.deck:
            top = player.deck.pop(0)
            player.life_cards.append(top)
    return True


# --- OP09-050: Garp ---
@register_effect("OP09-050", "on_play", "[On Play] If Navy leader, this Character gains Banish")
def op09_050_garp(game_state, player, card):
    """On Play: If Navy leader, gain Banish."""
    if player.leader and 'Navy' in (player.leader.card_origin or ''):
        card.has_banish = True
    return True


# =============================================================================
# OP09 SEARCHER CARDS
# =============================================================================

# --- OP09-020: Come On!! We'll Fight You!! (Event) ---
@register_effect("OP09-020", "on_play", "[Main] Look at 5, add Red-Haired Pirates (not self)")
def op09_020_come_on(game_state, player, card):
    """[Main] Look at 5 cards from the top of your deck; reveal up to 1
    {Red-Haired Pirates} type card other than [Come On!! We'll Fight You!!]
    and add it to your hand. Then, place the rest at the bottom of your deck in any order."""
    return search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: 'Red-Haired Pirates' in (c.card_origin or '')
                            and c.name != "Come On!! We'll Fight You!!",
        source_card=card,
        prompt="Look at top 5: choose 1 {Red-Haired Pirates} card (not Come On!! We'll Fight You!!) to add to hand")


# --- OP09-034: Perona ---
@register_effect("OP09-034", "on_play", "[On Play] Look at 5, add Mihawk or Thriller Bark Pirates, trash 1")
def op09_034_perona(game_state, player, card):
    """[On Play] Look at 5 cards from the top of your deck; reveal up to 1
    [Dracule Mihawk] or {Thriller Bark Pirates} type card and add it to your hand.
    Then, place the rest at the bottom of your deck in any order and trash 1 card from your hand."""
    result = search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: c.name == 'Dracule Mihawk'
                            or 'Thriller Bark Pirates' in (c.card_origin or ''),
        source_card=card,
        prompt="Look at top 5: choose 1 [Dracule Mihawk] or {Thriller Bark Pirates} card to add to hand")
    # Trash 1 from hand after search resolves
    trash_from_hand(player, 1, game_state, card)
    return result


# --- OP09-037: Lim ---
@register_effect("OP09-037", "on_play", "[On Play] Look at 5, add ODYSSEY (not self)")
def op09_037_lim(game_state, player, card):
    """[On Play] Look at 5 cards from the top of your deck; reveal up to 1
    {ODYSSEY} type card other than [Lim] and add it to your hand.
    Then, place the rest at the bottom of your deck in any order."""
    return search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: 'ODYSSEY' in (c.card_origin or '') and c.name != 'Lim',
        source_card=card,
        prompt="Look at top 5: choose 1 {ODYSSEY} card (not Lim) to add to hand")


@register_effect("OP09-037", "end_of_turn", "[End of Your Turn] If 3+ rested Characters, set this active")
def op09_037_lim_eot(game_state, player, card):
    """[End of Your Turn] If you have 3 or more rested Characters, set this Character as active."""
    rested = sum(1 for c in player.cards_in_play if c.is_resting and c != card)
    if rested >= 3:
        card.is_resting = False
        return True
    return False


# --- OP09-053: Mohji ---
@register_effect("OP09-053", "on_play", "[On Play] Look at 5, add Richie, then play Richie from hand")
def op09_053_mohji(game_state, player, card):
    """[On Play] Look at 5 cards from the top of your deck; reveal up to 1
    [Richie] and add it to your hand. Then, place the rest at the bottom of
    your deck in any order and play up to 1 [Richie] from your hand."""
    # Search for Richie first; after search resolves, play Richie from hand
    result = search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: c.name == 'Richie',
        source_card=card,
        prompt="Look at top 5: choose 1 [Richie] to add to hand")
    # Play a Richie from hand if available
    richie_in_hand = [c for c in player.hand
                      if c.name == 'Richie'
                      and getattr(c, 'card_type', '') == 'CHARACTER']
    if richie_in_hand:
        return create_play_from_hand_choice(
            game_state, player, richie_in_hand, source_card=card,
            rest_on_play=False,
            prompt="Choose a [Richie] from your hand to play")
    return result


# --- OP09-056: Mr.3(Galdino) ---
@register_effect("OP09-056", "on_play", "[On Play] Look at 4, add Cross Guild or Baroque Works (not self)")
def op09_056_mr3(game_state, player, card):
    """[On Play] Look at 4 cards from the top of your deck; reveal up to 1
    {Cross Guild} type card or card with a type including 'Baroque Works'
    other than [Mr.3(Galdino)] and add it to your hand.
    Then, place the rest at the bottom of your deck in any order."""
    return search_top_cards(game_state, player, look_count=4, add_count=1,
        filter_fn=lambda c: ('Cross Guild' in (c.card_origin or '')
                             or 'Baroque Works' in (c.card_origin or ''))
                            and c.name != 'Mr.3(Galdino)',
        source_card=card,
        prompt="Look at top 4: choose 1 {Cross Guild} or {Baroque Works} card (not Mr.3(Galdino)) to add to hand")


# --- OP09-057: Cross Guild (Event) ---
@register_effect("OP09-057", "on_play", "[Main] Look at 4, add Cross Guild")
def op09_057_cross_guild(game_state, player, card):
    """[Main] Look at 4 cards from the top of your deck; reveal up to 1
    {Cross Guild} type card and add it to your hand.
    Then, place the rest at the bottom of your deck in any order."""
    return search_top_cards(game_state, player, look_count=4, add_count=1,
        filter_fn=lambda c: 'Cross Guild' in (c.card_origin or ''),
        source_card=card,
        prompt="Look at top 4: choose 1 {Cross Guild} card to add to hand")


@register_effect("OP09-057", "trigger", "[Trigger] Activate this card's [Main] effect")
def op09_057_cross_guild_trigger(game_state, player, card):
    """[Trigger] Activate this card's [Main] effect."""
    return op09_057_cross_guild(game_state, player, card)


# --- OP09-095: Laffitte ---
@register_effect("OP09-095", "activate", "[Activate: Main] Rest DON + this: Look at 5, add Blackbeard Pirates")
def op09_095_laffitte(game_state, player, card):
    """[Activate: Main] Rest 1 DON and this Character: Look at 5, add 1 Blackbeard Pirates card."""
    if card.is_resting or getattr(card, 'main_activated_this_turn', False):
        return False
    if player.don_pool.count('active') < 1:
        return False
    idx = player.don_pool.index('active')
    player.don_pool[idx] = 'rested'
    card.is_resting = True
    card.main_activated_this_turn = True
    return search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: 'blackbeard pirates' in (c.card_origin or '').lower(),
        source_card=card,
        prompt="Laffitte: Look at top 5, choose 1 Blackbeard Pirates card to add to hand")


# --- OP09-096: My Era...Begins!! ---
@register_effect("OP09-096", "on_play", "[Main] Look at 3, add Blackbeard Pirates (not self), trash rest")
def op09_096_my_era(game_state, player, card):
    """[Main] Look at 3, add 1 Blackbeard Pirates (not self), trash rest."""
    return search_top_cards(game_state, player, look_count=3, add_count=1,
        filter_fn=lambda c: ('blackbeard pirates' in (c.card_origin or '').lower()
                             and 'my era' not in (c.name or '').lower()),
        source_card=card, trash_rest=True,
        prompt="Look at top 3: choose 1 Blackbeard Pirates card to add to hand (rest trashed)")


# --- OP09-099: Fullalead ---
@register_effect("OP09-099", "activate", "[Activate: Main] Trash 1, rest Stage: Look at 3, add Blackbeard Pirates")
def op09_099_fullalead(game_state, player, card):
    """[Activate: Main] Trash 1 from hand, rest Stage: Look at 3, add 1 Blackbeard Pirates card."""
    if card.is_resting or getattr(card, 'main_activated_this_turn', False):
        return False
    if not player.hand:
        return False
    card.is_resting = True
    card.main_activated_this_turn = True
    # Trash 1 from hand (auto for now, could be PendingChoice)
    if player.hand:
        trashed = player.hand.pop(0)
        player.trash.append(trashed)
    return search_top_cards(game_state, player, look_count=3, add_count=1,
        filter_fn=lambda c: 'blackbeard pirates' in (c.card_origin or '').lower(),
        source_card=card,
        prompt="Fullalead: Look at top 3, choose 1 Blackbeard Pirates card to add to hand")


# --- OP09-102: Professor Clover ---
@register_effect("OP09-102", "on_play", "[On Play] If Robin leader, look at 3, add Trigger card")
def op09_102_clover(game_state, player, card):
    """[On Play] If Nico Robin leader, look at 3, add 1 card with [Trigger]."""
    if not player.leader or 'nico robin' not in (player.leader.name or '').lower():
        return False
    return search_top_cards(game_state, player, look_count=3, add_count=1,
        filter_fn=lambda c: c.trigger and c.trigger.strip() != '',
        source_card=card,
        prompt="Professor Clover: Look at top 3, choose 1 card with [Trigger] to add to hand")


# --- OP09-117: Dereshi! ---
@register_effect("OP09-117", "on_play", "[Main] Look at 5, add up to 2 Trigger cards (not self)")
def op09_117_dereshi(game_state, player, card):
    """[Main] Look at 5, add up to 2 cards with [Trigger] (not Dereshi!)."""
    return search_top_cards(game_state, player, look_count=5, add_count=2,
        filter_fn=lambda c: (c.trigger and c.trigger.strip() != ''
                             and 'dereshi' not in (c.name or '').lower()),
        source_card=card,
        prompt="Dereshi!: Look at top 5, choose up to 2 cards with [Trigger] to add to hand")
