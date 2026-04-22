"""
Hardcoded effects for OP13 cards.
"""

from ..effect_registry import (
    add_don_from_deck, add_power_modifier, check_leader_type, check_life_count,
    create_don_assignment_choice, create_hand_discard_choice, create_ko_choice,
    create_own_character_choice, create_power_effect_choice, create_return_to_hand_choice,
    draw_cards, get_opponent, give_don_to_card, register_effect, rest_cards, search_top_cards,
    set_active, trash_from_hand,
)


# --- OP13-035: Bepo ---
@register_effect("OP13-035", "END_OF_TURN", "Set this Character or 1 DON as active")
def bepo_effect(game_state, player, card):
    if card.is_resting:
        card.is_resting = False
        return True
    for don in player.don_pool:
        if don.is_resting:
            don.is_resting = False
            return True
    return False


# --- OP13-062: Crocus ---
@register_effect("OP13-062", "ON_PLAY", "If DON attached, add DON from deck and set active")
def crocus_on_play(game_state, player, card):
    has_given_don = any(getattr(c, 'attached_don', 0) > 0 for c in player.cards_in_play)
    if has_given_don or (player.leader and getattr(player.leader, 'attached_don', 0) > 0):
        add_don_from_deck(player, 1, set_active=True)
        return True
    return False


@register_effect("OP13-062", "WHEN_ATTACKING", "Return opponent's 3000 base power or less to hand")
def crocus_attack(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'power', 0) or 0) <= 3000]
    if targets:
        return create_return_to_hand_choice(
            game_state, player, targets, source_card=card,
            prompt="Choose opponent's 3000 power or less Character to return to hand"
        )
    return False


# --- OP13-033: Franky ---
@register_effect("OP13-033", "ON_KO", "Rest up to 2 opponent's cards")
def franky_op13_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    active = [c for c in opponent.cards_in_play if not c.is_resting][:2]
    rest_cards(active)
    return len(active) > 0


# --- OP13-032: Nico Robin ---
@register_effect("OP13-032", "ON_PLAY", "Opponent's cost 8 or less cannot be rested")
def robin_op13_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    for c in opponent.cards_in_play:
        if (getattr(c, 'cost', 0) or 0) <= 8:
            c.cannot_be_rested = True
    return True


# --- OP13-092: Saint Mjosgard ---
@register_effect("OP13-092", "ON_PLAY", "If 3 or less Life, play Mary Geoise Stage cost 1 from trash")
def mjosgard_effect(game_state, player, card):
    if len(player.life_cards) <= 3:
        stages = [c for c in player.trash
                 if 'mary geoise' in (c.card_origin or '').lower()
                 and (getattr(c, 'cost', 0) or 0) == 1
                 and getattr(c, 'card_type', '') == 'STAGE']
        if stages:
            stage = stages[0]
            player.trash.remove(stage)
            player.cards_in_play.append(stage)
            return True
    return False


# --- OP13-028: Shanks ---
@register_effect("OP13-028", "ON_PLAY", "Set all DON active, cannot play from hand this turn")
def shanks_op13_effect(game_state, player, card):
    for don in player.don_pool:
        don.is_resting = False
    player.cannot_play_from_hand = True
    return True


# --- OP13-099: The Empty Throne ---
@register_effect("OP13-099", "MAIN", "Rest this and 3 DON: Play Five Elders with cost <= DON count")
def empty_throne_effect(game_state, player, card):
    active_don = [d for d in player.don_pool if not d.is_resting]
    if len(active_don) >= 3 and not card.is_resting:
        card.is_resting = True
        for don in active_don[:3]:
            don.is_resting = True
        don_count = len(player.don_pool)
        five_elders = [c for c in player.hand
                      if 'five elders' in (c.card_origin or '').lower()
                      and 'black' in (getattr(c, 'colors', '') or '').lower()
                      and (getattr(c, 'cost', 0) or 0) <= don_count
                      and getattr(c, 'card_type', '') == 'CHARACTER']
        if five_elders:
            char = five_elders[0]
            player.hand.remove(char)
            player.cards_in_play.append(char)
            return True
    return False


# --- OP13-006: Woop Slap ---
@register_effect("OP13-006", "ON_PLAY", "Give 2 rested DON to Monkey.D.Luffy")
def woop_slap_effect(game_state, player, card):
    luffy_cards = [c for c in player.cards_in_play if 'Monkey.D.Luffy' in getattr(c, 'name', '')]
    if luffy_cards:
        give_don_to_card(player, luffy_cards[0], 2, rested_only=True)
        return True
    return False


# --- OP13-099: The Empty Throne ---
@register_effect("OP13-099", "CONTINUOUS", "Leader +1000 power if 19+ cards in trash")
def empty_throne_continuous_effect(game_state, player, card):
    if len(player.trash) >= 19:
        player.leader.power = getattr(player.leader, 'power', 0) + 1000
        return True
    return False


@register_effect("OP13-099", "ACTIVATE_MAIN", "Play Five Elders from trash")
def empty_throne_main_effect(game_state, player, card):
    if not card.is_resting:
        # Rest this and 3 DON
        rested_don = sum(1 for d in player.don_pool if d.is_resting)
        if rested_don < 3:
            return False
        card.is_resting = True
        don_rested = 0
        for d in player.don_pool:
            if don_rested < 3 and not d.is_resting:
                d.is_resting = True
                don_rested += 1
        # Play Five Elders from trash
        five_elders = [c for c in player.trash if 'five elders' in (c.card_origin or '').lower()]
        if five_elders:
            card_to_play = five_elders[0]
            player.trash.remove(card_to_play)
            player.cards_in_play.append(card_to_play)
            return True
    return False


# =============================================================================
# MORE LEADER CONDITION CARDS - FILM / Straw Hat Crew
# =============================================================================

# --- OP13-034: Brook ---
@register_effect("OP13-034", "ON_PLAY", "If Leader is FILM or Straw Hat Crew, set 1 DON active")
def op13_034_brook(game_state, player, card):
    if check_leader_type(player, "FILM") or check_leader_type(player, "Straw Hat Crew"):
        set_active(player.don_pool[:1])
    return True


# =============================================================================
# MORE LEADER CONDITION CARDS - Roger Pirates
# =============================================================================

# --- OP13-072: Buggy ---
@register_effect("OP13-072", "ON_PLAY", "If Leader is Roger Pirates and DON given, add DON rested")
def op13_072_buggy(game_state, player, card):
    if check_leader_type(player, "Roger Pirates"):
        # Check if any DON is given (attached to cards)
        has_given_don = any(getattr(c, 'attached_don', 0) > 0 for c in player.cards_in_play)
        if has_given_don or (player.leader and getattr(player.leader, 'attached_don', 0) > 0):
            add_don_from_deck(player, 1, set_active=False)
    return True


# =============================================================================
# LEADER NAME CONDITION CARDS
# =============================================================================

# --- OP13-050: Boa Sandersonia ---
@register_effect("OP13-050", "ON_PLAY", "If Leader is Boa Hancock, play Boa Hancock cost 3 or less from hand")
def op13_050_sandersonia(game_state, player, card):
    if check_leader_name(player, "Boa Hancock"):
        hancocks = [c for c in player.hand
                    if 'Boa Hancock' in (getattr(c, 'name', '') or '')
                    and (getattr(c, 'cost', 0) or 0) <= 3]
        if hancocks:
            to_play = hancocks[0]
            player.hand.remove(to_play)
            player.cards_in_play.append(to_play)
    return True


# --- OP13-051: Boa Hancock ---
@register_effect("OP13-051", "ON_KO", "If Leader is Boa Hancock or multicolored, draw 2")
def op13_051_hancock(game_state, player, card):
    is_hancock = check_leader_name(player, "Boa Hancock")
    is_multicolor = player.leader and len(getattr(player.leader, 'colors', []) or []) > 1
    if is_hancock or is_multicolor:
        draw_cards(player, 2)
    return True


# --- OP13-052: Boa Marigold ---
@register_effect("OP13-052", "ON_PLAY", "If Leader is Boa Hancock, play Boa Hancock cost 6 or less from hand")
def op13_052_marigold(game_state, player, card):
    if check_leader_name(player, "Boa Hancock"):
        hancocks = [c for c in player.hand
                    if 'Boa Hancock' in (getattr(c, 'name', '') or '')
                    and (getattr(c, 'cost', 0) or 0) <= 6]
        if hancocks:
            to_play = hancocks[0]
            player.hand.remove(to_play)
            player.cards_in_play.append(to_play)
    return True


# --- OP13-004: Sabo (Leader) ---
@register_effect("OP13-004", "CONTINUOUS", "If 4+ life, -1000 power; if DONx1 and cost 8+ char, all +1000")
def op13_004_sabo_leader(game_state, player, card):
    """Continuous: -1000 power if 4+ life; +1000 to all if DONx1 and cost 8+ char."""
    if len(player.life_cards) >= 4:
        add_power_modifier(card, -1000)
    if getattr(card, 'attached_don', 0) >= 1:
        cost_8_chars = [c for c in player.cards_in_play if (getattr(c, 'cost', 0) or 0) >= 8]
        if cost_8_chars:
            add_power_modifier(card, 1000)
            for c in player.cards_in_play:
                add_power_modifier(c, 1000)
    return True


# --- OP13-042: Edward.Newgate ---
@register_effect("OP13-042", "ON_PLAY", "Draw 2, trash 1, give Leader and 1 Character up to 2 rested DON each")
def op13_042_edward_newgate(game_state, player, card):
    """On Play: Draw 2 cards and trash 1 from hand. Then give Leader and 1 Character up to 2 rested DON each."""
    # Draw 2 cards
    draw_cards(player, 2)
    # Trash 1 from hand (creates PendingChoice for player)
    trash_from_hand(player, 1, game_state, card)
    # Give Leader up to 2 rested DON
    rested_don = player.don_pool.count("rested")
    don_to_leader = min(2, rested_don)
    player.leader.attached_don = getattr(player.leader, 'attached_don', 0) + don_to_leader
    # Give a Character up to 2 rested DON (player choice)
    remaining_rested = rested_don - don_to_leader
    don_to_char = min(2, remaining_rested)
    if player.cards_in_play and don_to_char > 0:
        return create_don_assignment_choice(game_state, player, player.cards_in_play,
                                            don_to_char, source_card=card,
                                            prompt="Choose a Character to give rested DON")
    return True


# --- OP13-043: Otama ---
@register_effect("OP13-043", "ON_PLAY", "If 3 or less life, draw 2 and trash 1")
def op13_043_otama(game_state, player, card):
    """On Play: If 3 or less life, draw 2 and trash 1."""
    if check_life_count(player, 3):
        draw_cards(player, 2)
        trash_from_hand(player, 1, game_state, card)
        return True
    return False


# --- OP13-057: If I Bowed Down to Power ---
@register_effect("OP13-057", "MAIN", "Rest 1 DON: If 1 or less life, opponent can't block Leader")
def op13_057_bowed_down(game_state, player, card):
    """Main: Rest DON, if 1 or less life opponent can't use Blocker against Leader."""
    active_don = [d for d in player.don_pool if not d.is_resting]
    if active_don:
        active_don[0].is_resting = True
        if check_life_count(player, 1):
            player.opponent_cannot_block_leader_this_turn = True
        return True
    return False


@register_effect("OP13-057", "COUNTER", "Leader +3000 power")
def op13_057_bowed_down_counter(game_state, player, card):
    """Counter: Leader gains +3000 power."""
    if player.leader:
        add_power_modifier(player.leader, 3000)
        return True
    return False


# --- OP13-115: Paper Art Afterimage ---
@register_effect("OP13-115", "COUNTER", "+3000 power, +1000 if opponent has 2 or less life")
def op13_115_paper_art(game_state, player, card):
    """Counter: +3000 power, +1000 more if opponent has 2 or less life."""
    target = player.leader if player.leader else (player.cards_in_play[0] if player.cards_in_play else None)
    if target:
        add_power_modifier(target, 3000)
        opponent = get_opponent(game_state, player)
        if len(opponent.life_cards) <= 2:
            add_power_modifier(target, 1000)
        return True
    return False


# --- OP13-119: Portgas.D.Ace ---
@register_effect("OP13-119", "CONTINUOUS", "If 3 or less life, gain Rush")
def op13_119_ace_continuous(game_state, player, card):
    """Continuous: If 3 or less life, this gains Rush."""
    if check_life_count(player, 3):
        card.has_rush = True
        return True
    return False


@register_effect("OP13-119", "ON_PLAY", "Give DON to Leader, return opponent's cost 5 or less to hand")
def op13_119_ace_on_play(game_state, player, card):
    """On Play: Give rested DON to Leader, return opponent's cost 5 or less to hand."""
    rested_don = [d for d in player.don_pool if d.is_resting]
    if rested_don and player.leader:
        give_don_to_card(player, player.leader, 1, rested_only=True)
    return return_opponent_to_hand(game_state, player, max_cost=5, source_card=card)


# --- OP13-053: Marshall.D.Teach ---
@register_effect("OP13-053", "WHEN_ATTACKING", "Trash WB char: Draw 1 and gain Banish")
def op13_053_teach(game_state, player, card):
    """When Attacking: Trash WB char, draw 1 and gain Banish."""
    wb_chars = [c for c in player.cards_in_play
                if 'whitebeard pirates' in (c.card_origin or '').lower()
                and c != card]
    if wb_chars:
        draw_cards(player, 1)
        card.has_banish = True
        return create_own_character_choice(
            game_state, player, wb_chars,
            source_card=card,
            callback_action="trash_own_character",
            prompt="Choose Whitebeard Pirates Character to trash"
        )
    return False


# --- OP13-054: Yamato ---
@register_effect("OP13-054", "on_play", "[On Play] If 3- life, draw 2, give 1 rested DON to Leader")
def op13_054_yamato(game_state, player, card):
    """On Play: If you have 3 or less Life cards, draw 2. Then, give up to 1 rested DON to your Leader."""
    # Check life condition for draw
    if len(player.life_cards) <= 3:
        draw_cards(player, 2)
    # Give up to 1 rested DON to Leader (optional)
    rested_don = player.don_pool.count("rested")
    if rested_don and player.leader:
        # Give 1 rested DON to leader
        player.leader.attached_don = getattr(player.leader, 'attached_don', 0) + 1
    return True


# --- OP13-059: Brilliant Punk ---
@register_effect("OP13-059", "MAIN", "Return char to hand: Return opponent's cost 6 or less to hand")
def op13_059_brilliant_punk(game_state, player, card):
    """Main: Return char to hand, return opponent's cost 6 or less to hand."""
    if player.cards_in_play:
        own_snap = list(player.cards_in_play)
        def brilliant_punk_cb(selected: list) -> None:
            target_idx = int(selected[0]) if selected else -1
            if 0 <= target_idx < len(own_snap):
                target = own_snap[target_idx]
                if target in player.cards_in_play:
                    player.cards_in_play.remove(target)
                    player.hand.append(target)
                    game_state._log(f"{player.name} returned {target.name} to hand")
            opponent = get_opponent(game_state, player)
            opp_targets = [c for c in opponent.cards_in_play
                           if (getattr(c, 'cost', 0) or 0) <= 6]
            if opp_targets:
                create_return_to_hand_choice(game_state, player, opp_targets,
                                             source_card=None,
                                             prompt="Choose opponent's cost 6 or less Character to return to hand")
        return create_own_character_choice(
            game_state, player, player.cards_in_play, source_card=card,
            prompt="Choose one of your Characters to return to hand (cost)",
            callback=brilliant_punk_cb
        )
    return False


# --- OP13-001: Monkey.D.Luffy (Leader) ---
@register_effect("OP13-001", "on_opponent_attack", "[DON!! x1] If 5- active DON, rest DON to give -1000 each")
def op13_001_luffy_leader(game_state, player, card):
    """DON x1, On Opponent's Attack: If 5 or less active DON, rest any DON, give -1000 per DON rested."""
    if getattr(card, 'attached_don', 0) >= 1:
        active_don = player.don_pool.count("active")
        if len(active_don) <= 5 and active_don:
            power_reduction = len(active_don) * 1000
            for don in active_don:
                don.is_resting = True
            opponent = get_opponent(game_state, player)
            if opponent.leader:
                opponent.leader.power_modifier = getattr(opponent.leader, 'power_modifier', 0) - power_reduction
            return True
    return False


# --- OP13-002: Portgas.D.Ace (Leader) ---
@register_effect("OP13-002", "on_opponent_attack", "[On Opponent's Attack] Trash 1: Give -2000 power")
def op13_002_ace_leader(game_state, player, card):
    """On Opponent's Attack, Once Per Turn: Trash 1 from hand, give opponent's Leader or Character -2000 power."""
    if hasattr(card, 'op13_002_used') and card.op13_002_used:
        return False
    if player.hand:
        card.op13_002_used = True
        hand_snap = list(player.hand)
        def ace_cb(selected: list) -> None:
            target_idx = int(selected[0]) if selected else -1
            if 0 <= target_idx < len(hand_snap):
                target = hand_snap[target_idx]
                if target in player.hand:
                    player.hand.remove(target)
                    player.trash.append(target)
                    game_state._log(f"{target.name} was trashed from hand")
            opponent = get_opponent(game_state, player)
            power_targets = []
            if opponent.leader:
                power_targets.append(opponent.leader)
            power_targets.extend(opponent.cards_in_play)
            if power_targets:
                create_power_effect_choice(game_state, player, power_targets, -2000,
                                           source_card=None,
                                           prompt="Choose opponent's Leader or Character to give -2000 power")
        return create_hand_discard_choice(game_state, player, player.hand,
            callback=ace_cb, source_card=card,
            prompt="Trash a card to give opponent's Leader or Character -2000 power")
    return False


# --- OP13-003: Gol.D.Roger (Leader) ---
@register_effect("OP13-003", "continuous", "1 DON during DON phase goes to Leader")
def op13_003_roger_continuous(game_state, player, card):
    """If you have DON on field, 1 DON placed during DON Phase is given to your Leader."""
    if player.don_pool:
        card.don_phase_to_leader = True
    return True


# --- OP13-004: Sabo (Leader) - already exists, skip ---

# --- OP13-079: Imu (Leader) ---
@register_effect("OP13-079", "continuous", "Cannot include Events cost 2+ in deck")
def op13_079_imu_continuous(game_state, player, card):
    """Cannot include Events cost 2 or more in deck. At start play Mary Geoise Stage."""
    # Deck building restriction handled elsewhere
    return True


# --- OP13-100: Jewelry Bonney (Leader) ---
@register_effect("OP13-100", "on_play_character", "[Your Turn] When play Trigger char, give 2 rested DON to Leader/char")
def op13_100_bonney_leader(game_state, player, card):
    """Your Turn, Once Per Turn: When you play a Character with Trigger, give 2 rested DON to Leader/Character."""
    if hasattr(card, 'op13_100_used') and card.op13_100_used:
        return False
    rested_don = player.don_pool.count("rested")
    if len(rested_don) >= 2:
        targets = [player.leader] + player.cards_in_play if player.leader else player.cards_in_play
        if targets:
            card.op13_100_used = True
            return create_don_assignment_choice(
                game_state, player, targets, don_count=2,
                source_card=card, rested_only=True,
                prompt="Choose Leader or Character to give 2 rested DON"
            )
    return False


# --- OP13-003: Luffy ---
@register_effect("OP13-003", "on_play", "[On Play] K.O. cost 4 or less")
def op13_003_luffy(game_state, player, card):
    """On Play: K.O. opponent's cost 4 or less."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                               prompt="Choose opponent's cost 4 or less to K.O.")
    return True


# --- OP13-022: Koby ---
@register_effect("OP13-022", "blocker", "[Blocker]")
def op13_022_koby_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP13-022", "on_play", "[On Play] If Navy leader, draw 2")
def op13_022_koby_on_play(game_state, player, card):
    """On Play: If Navy leader, draw 2."""
    if player.leader and 'Navy' in (player.leader.card_origin or ''):
        draw_cards(player, 2)
    return True


# --- OP13-040: Zoro ---
@register_effect("OP13-040", "on_play", "[On Play] Give your Characters +2000 power")
def op13_040_zoro(game_state, player, card):
    """On Play: Give your Characters +2000 power."""
    for c in player.cards_in_play:
        c.power_modifier = getattr(c, 'power_modifier', 0) + 2000
    return True


# --- OP13-060: Robin ---
@register_effect("OP13-060", "on_play", "[On Play] Look at 5, add Revolutionary Army")
def op13_060_robin(game_state, player, card):
    """On Play: Look at 5, add Revolutionary Army card."""
    return search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: 'revolutionary army' in (c.card_origin or '').lower(),
        source_card=card,
        prompt="Look at top 5: choose 1 Revolutionary Army card to add to hand")


# --- OP13-012: Nefeltari Vivi ---
@register_effect("OP13-012", "on_play", "[On Play] Look at 4, add Alabasta/SHC cost 2+")
def op13_012_vivi(game_state, player, card):
    return search_top_cards(game_state, player, look_count=4, add_count=1,
        filter_fn=lambda c: (('alabasta' in (c.card_origin or '').lower()
                              or 'straw hat crew' in (c.card_origin or '').lower())
                             and (c.cost or 0) >= 2),
        source_card=card,
        prompt="Look at top 4: choose 1 Alabasta or Straw Hat Crew (cost 2+) to add to hand")


# --- OP13-065: Shanks ---
@register_effect("OP13-065", "on_play", "[On Play] Look at 5, add Roger Pirates (not Shanks)")
def op13_065_shanks(game_state, player, card):
    return search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: ('roger pirates' in (c.card_origin or '').lower()
                             and 'shanks' not in (c.name or '').lower()),
        source_card=card,
        prompt="Look at top 5: choose 1 Roger Pirates card (not Shanks) to add to hand")


# --- OP13-083: St. Jaygarcia Saturn ---
@register_effect("OP13-083", "on_play", "[On Play] Look at 5, add Five Elders")
def op13_083_saturn(game_state, player, card):
    return search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: 'five elders' in (c.card_origin or '').lower(),
        source_card=card,
        prompt="Look at top 5: choose 1 Five Elders card to add to hand")


# --- OP13-086: Saint Shalria ---
@register_effect("OP13-086", "on_play", "[On Play] Look at 3, add Celestial Dragons (not self), trash rest")
def op13_086_shalria(game_state, player, card):
    return search_top_cards(game_state, player, look_count=3, add_count=1,
        filter_fn=lambda c: ('celestial dragons' in (c.card_origin or '').lower()
                             and 'saint shalria' not in (c.name or '').lower()),
        source_card=card, trash_rest=True,
        prompt="Look at top 3: choose 1 Celestial Dragons card to add to hand (rest trashed)")


# --- OP13-096: The Five Elders Are at Your Service!!! ---
@register_effect("OP13-096", "on_play", "[Main] Look at 3, add Celestial Dragons (not self), trash rest")
def op13_096_five_elders(game_state, player, card):
    return search_top_cards(game_state, player, look_count=3, add_count=1,
        filter_fn=lambda c: ('celestial dragons' in (c.card_origin or '').lower()
                             and 'the five elders are at your service' not in (c.name or '').lower()),
        source_card=card, trash_rest=True,
        prompt="Look at top 3: choose 1 Celestial Dragons card to add to hand (rest trashed)")


# --- OP13-113: Lilith ---
@register_effect("OP13-113", "on_play", "[On Play] Look at 4, add card with Trigger (not Lilith)")
def op13_113_lilith(game_state, player, card):
    return search_top_cards(game_state, player, look_count=4, add_count=1,
        filter_fn=lambda c: (c.trigger and c.trigger.strip() != ''
                             and 'lilith' not in (c.name or '').lower()),
        source_card=card,
        prompt="Look at top 4: choose 1 card with [Trigger] (not Lilith) to add to hand")


# --- OP13-116: The One Who Is the Most Free Is the Pirate King!!! ---
@register_effect("OP13-116", "on_play", "[Main] Look at 5, add Supernovas Character")
def op13_116_pirate_king(game_state, player, card):
    return search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: ('supernovas' in (c.card_origin or '').lower()
                             and c.card_type == 'CHARACTER'),
        source_card=card,
        prompt="Look at top 5: choose 1 Supernovas Character to add to hand")


# --- OP13-016: Monkey.D.Garp ---
@register_effect("OP13-016", "on_play", "[On Play] If Sabo/Ace/Luffy leader, look at 4, add cost 3+")
def op13_016_garp(game_state, player, card):
    """[On Play] If leader is Sabo, Portgas.D.Ace, or Monkey.D.Luffy, look at 4, add 1 cost 3+."""
    if not player.leader:
        return False
    leader_name = (player.leader.name or '').lower()
    if ('sabo' not in leader_name
            and 'portgas.d.ace' not in leader_name
            and 'monkey.d.luffy' not in leader_name):
        return False
    return search_top_cards(game_state, player, look_count=4, add_count=1,
        filter_fn=lambda c: (c.cost or 0) >= 3,
        source_card=card,
        prompt="Garp: Look at top 4, choose 1 card with cost 3 or more to add to hand")


# ---------------------------------------------------------------------------
# OP13 GENERIC FALLBACK REGISTRATIONS
# ---------------------------------------------------------------------------
# These registrations cover cards/timings that do not yet have bespoke OP13
# implementations. The shared fallback provides safe prompted behavior for the
# common printed patterns and the MasterAudit marks these as Partial when exact
# text still needs a bespoke resolver.
from .generic_fallback import register_generic_set_fallback


_OP13_GENERIC_TIMINGS = {
    "OP13-005": ["on_play"],
    "OP13-007": ["activate"],
    "OP13-008": ["continuous"],
    "OP13-009": ["continuous"],
    "OP13-013": ["on_play"],
    "OP13-014": ["trigger"],
    "OP13-015": ["activate"],
    "OP13-017": ["continuous"],
    "OP13-019": ["counter", "on_play"],
    "OP13-020": ["on_play", "trigger"],
    "OP13-021": ["on_play", "trigger"],
    "OP13-023": ["on_play", "on_ko"],
    "OP13-024": ["on_play"],
    "OP13-025": ["on_play", "blocker"],
    "OP13-026": ["activate"],
    "OP13-027": ["on_play", "end_of_turn"],
    "OP13-030": ["on_play"],
    "OP13-031": ["on_play", "blocker"],
    "OP13-037": ["on_play", "end_of_turn"],
    "OP13-038": ["on_play", "trigger"],
    "OP13-039": ["counter", "trigger"],
    "OP13-041": ["on_play"],
    "OP13-044": ["on_attack", "on_ko"],
    "OP13-045": ["on_attack"],
    "OP13-046": ["continuous"],
    "OP13-047": ["continuous"],
    "OP13-055": ["on_attack"],
    "OP13-056": ["on_attack"],
    "OP13-058": ["counter", "on_play"],
    "OP13-059": ["trigger"],
    "OP13-061": ["on_play"],
    "OP13-063": ["on_play", "blocker"],
    "OP13-064": ["on_play"],
    "OP13-066": ["on_play"],
    "OP13-067": ["on_play"],
    "OP13-068": ["on_play"],
    "OP13-069": ["on_play"],
    "OP13-071": ["on_play"],
    "OP13-074": ["on_play"],
    "OP13-075": ["counter", "on_play"],
    "OP13-076": ["counter", "on_play"],
    "OP13-077": ["counter", "on_play"],
    "OP13-078": ["continuous"],
    "OP13-080": ["on_attack"],
    "OP13-081": ["activate"],
    "OP13-082": ["activate"],
    "OP13-084": ["continuous"],
    "OP13-087": ["on_play", "blocker"],
    "OP13-089": ["on_ko", "blocker"],
    "OP13-091": ["on_play", "blocker"],
    "OP13-093": ["on_play", "blocker"],
    "OP13-094": ["on_play"],
    "OP13-095": ["on_play"],
    "OP13-096": ["trigger"],
    "OP13-097": ["counter", "on_play"],
    "OP13-098": ["counter", "on_play"],
    "OP13-102": ["activate", "trigger"],
    "OP13-104": ["on_ko", "blocker"],
    "OP13-105": ["on_play"],
    "OP13-106": ["blocker", "trigger"],
    "OP13-108": ["on_play", "trigger"],
    "OP13-109": ["continuous", "trigger"],
    "OP13-110": ["on_play", "blocker"],
    "OP13-112": ["blocker"],
    "OP13-113": ["trigger"],
    "OP13-114": ["on_play", "on_attack", "trigger"],
    "OP13-115": ["trigger"],
    "OP13-116": ["trigger"],
    "OP13-117": ["on_play", "trigger"],
    "OP13-118": ["on_play"],
    "OP13-120": ["activate", "blocker"],
}


register_generic_set_fallback(_OP13_GENERIC_TIMINGS, "OP13")
