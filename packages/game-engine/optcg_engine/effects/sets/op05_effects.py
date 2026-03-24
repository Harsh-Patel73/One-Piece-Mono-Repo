"""
Hardcoded effects for OP05 cards.
"""

import random

from ..hardcoded import (
    add_don_from_deck, create_bottom_deck_choice, create_hand_discard_choice, create_ko_choice,
    create_mode_choice, create_rest_choice, create_return_to_hand_choice, create_set_active_choice,
    create_target_choice, draw_cards, get_opponent, register_effect,
    search_top_cards, trash_from_hand,
)


# --- OP05-040: Birdcage ---
@register_effect("OP05-040", "END_OF_TURN", "If 10 DON, KO all rested cost 5 or less Characters")
def birdcage_effect(game_state, player, card):
    if len(player.don_pool) >= 10:
        opponent = get_opponent(game_state, player)
        for p in [player, opponent]:
            to_ko = [c for c in p.cards_in_play
                    if c.is_resting and (getattr(c, 'cost', 0) or 0) <= 5]
            for c in to_ko:
                p.cards_in_play.remove(c)
                p.trash.append(c)
        # Trash this Stage
        if card in player.cards_in_play:
            player.cards_in_play.remove(card)
            player.trash.append(card)
        return True
    return False


# --- OP05-031: Buffalo ---
@register_effect("OP05-031", "WHEN_ATTACKING", "If 2+ rested chars, set 1 cost 1 rested char active")
def buffalo_effect(game_state, player, card):
    rested = [c for c in player.cards_in_play if c.is_resting]
    if len(rested) >= 2:
        cost_1_rested = [c for c in rested if (getattr(c, 'cost', 0) or 0) == 1]
        if cost_1_rested:
            cost_1_rested[0].is_resting = False
            return True
    return False


# --- OP05-079: Viola ---
@register_effect("OP05-079", "ON_PLAY", "Opponent places 3 from trash at bottom of deck")
def viola_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    for _ in range(min(3, len(opponent.trash))):
        if opponent.trash:
            card_to_place = opponent.trash.pop(0)
            opponent.deck.append(card_to_place)
    return True


# =============================================================================
# EXTRA TURN EFFECTS
# =============================================================================

# --- OP05-119: Monkey.D.Luffy (Gear 5) ---
@register_effect("OP05-119", "ON_PLAY", "DON -10: Place all chars at bottom, take extra turn")
def luffy_gear5_on_play(game_state, player, card):
    """Place all characters at bottom, take an extra turn."""
    # This is a costly effect - requires 10 DON
    don_count = len([d for d in player.don_pool if not d.is_resting])
    if don_count < 10:
        return False

    # Return 10 DON to deck
    returned = 0
    for don in list(player.don_pool):
        if returned >= 10:
            break
        if not don.is_resting:
            player.don_pool.remove(don)
            if hasattr(player, 'don_deck'):
                player.don_deck.append(don)
            returned += 1

    # Place all characters except this one at bottom of deck
    chars_to_move = [c for c in player.cards_in_play if c.id != card.id]
    for char in chars_to_move:
        player.cards_in_play.remove(char)
        player.deck.append(char)

    # Grant extra turn
    game_state.extra_turn_pending = True
    game_state.extra_turn_player = player

    return True


@register_effect("OP05-119", "ACTIVATE_MAIN", "Add 1 DON from DON deck and set active")
def luffy_gear5_activate(game_state, player, card):
    """Add 1 DON from DON deck and set it as active."""
    # Check once per turn
    if hasattr(card, 'luffy_activate_used') and card.luffy_activate_used:
        return False

    # Rest 1 DON as cost
    active_don = [d for d in player.don_pool if not d.is_resting]
    if not active_don:
        return False

    active_don[0].is_resting = True

    # Add DON from don_deck if available
    if hasattr(player, 'don_deck') and player.don_deck and len(player.don_pool) < 10:
        don = player.don_deck.pop(0)
        don.is_resting = False  # Set as active
        player.don_pool.append(don)

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
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 1]
    if targets:
        # Player chooses how to remove the target
        modes = [
            {"id": "ko", "label": "KO Character", "description": "KO opponent's cost 1 or less Character"},
            {"id": "return", "label": "Return to Hand", "description": "Return opponent's cost 1 or less Character to hand"},
            {"id": "bottom", "label": "Place at Bottom", "description": "Place opponent's cost 1 or less Character at bottom of deck"}
        ]
        return create_mode_choice(game_state, player, modes, source_card=card,
                                   prompt="Choose: KO, Return to hand, OR Place at bottom of deck")
    return True


# --- OP05-019: Fire Fist ---
@register_effect("OP05-019", "MAIN", "-4000 power, KO 0 power if 2 or less life")
def op05_019_fire_fist(game_state, player, card):
    """Main: -4000 power to opponent's char, KO 0 power chars if 2 or less life."""
    opponent = get_opponent(game_state, player)
    if opponent.cards_in_play:
        target = opponent.cards_in_play[0]
        add_power_modifier(target, -4000)
        if check_life_count(player, 2):
            # KO chars with 0 or less power
            for c in opponent.cards_in_play[:]:
                effective_power = (getattr(c, 'power', 0) or 0) + (getattr(c, 'power_modifier', 0))
                if effective_power <= 0:
                    opponent.cards_in_play.remove(c)
                    opponent.trash.append(c)
        return True
    return False


# --- OP05-101: Ohm ---
@register_effect("OP05-101", "CONTINUOUS", "If 2 or less life, gain +1000 power")
def op05_101_ohm(game_state, player, card):
    """Continuous: If 2 or less life, this card gains +1000 power."""
    if check_life_count(player, 2):
        add_power_modifier(card, 1000)
        return True
    return False


@register_effect("OP05-101", "ON_PLAY", "Look at 5, add Holly to hand")
def op05_101_ohm_play(game_state, player, card):
    """On Play: Look at 5, reveal Holly and add to hand."""
    if len(player.deck) >= 5:
        top_5 = player.deck[:5]
        player.deck = player.deck[5:]
        holly = [c for c in top_5 if 'Holly' in getattr(c, 'name', '')]
        if holly:
            player.hand.append(holly[0])
            top_5.remove(holly[0])
        player.deck.extend(top_5)
        return True
    return False


# --- OP05-114: El Thor ---
@register_effect("OP05-114", "COUNTER", "+2000 power, +2000 more if opponent has 2 or less life")
def op05_114_el_thor(game_state, player, card):
    """Counter: +2000 power, additional +2000 if opponent has 2 or less life."""
    opponent = get_opponent(game_state, player)
    target = player.leader if player.leader else (player.cards_in_play[0] if player.cards_in_play else None)
    if target:
        add_power_modifier(target, 2000)
        if len(opponent.life_cards) <= 2:
            add_power_modifier(target, 2000)
        return True
    return False


# --- OP05-115: Two-Hundred Million Volts Amaru ---
@register_effect("OP05-115", "MAIN", "+3000 power, rest opponent's cost 4 or less if 1 or less life")
def op05_115_amaru(game_state, player, card):
    """Main: +3000 power, rest opponent's cost 4 or less if 1 or less life."""
    target = player.leader if player.leader else (player.cards_in_play[0] if player.cards_in_play else None)
    if target:
        add_power_modifier(target, 3000)
        if check_life_count(player, 1):
            opponent = get_opponent(game_state, player)
            targets = [c for c in opponent.cards_in_play
                      if not c.is_resting and (getattr(c, 'cost', 0) or 0) <= 4]
            if targets:
                return create_target_choice(
                    game_state, player, targets,
                    callback_action="rest_target",
                    source_card=card,
                    prompt="Choose opponent's cost 4 or less Character to rest"
                )
        return True
    return False


# --- OP05-118: Kaido ---
@register_effect("OP05-118", "ON_PLAY", "Draw 4 if opponent has 3 or less life")
def op05_118_kaido(game_state, player, card):
    """On Play: Draw 4 cards if opponent has 3 or less life."""
    opponent = get_opponent(game_state, player)
    if len(opponent.life_cards) <= 3:
        draw_cards(player, 4)
        return True
    return False


# --- OP05-095: Dragon Claw ---
@register_effect("OP05-095", "COUNTER", "+4000 power, KO cost 4 or less if 15+ trash")
def op05_095_dragon_claw(game_state, player, card):
    """Counter: +4000 power, KO cost 4 or less if 15+ trash."""
    target = player.leader if player.leader else (player.cards_in_play[0] if player.cards_in_play else None)
    if target:
        add_power_modifier(target, 4000)
        if check_trash_count(player, 15):
            return ko_opponent_character(game_state, player, max_cost=4, source_card=card)
        return True
    return False


# =============================================================================
# LEADER CARD EFFECTS - OP05 (Awakening of New Era)
# =============================================================================

# --- OP05-001: Sabo (Leader) ---
@register_effect("OP05-001", "on_ko_prevention", "[DON!! x1] [Opponent's Turn] 5000+ power char survives at -1000")
def op05_001_sabo_leader(game_state, player, card):
    """DON x1, Opponent's Turn, Once Per Turn: When 5000+ power char would be K.O.'d, it survives at -1000 power."""
    if getattr(card, 'attached_don', 0) >= 1:
        if hasattr(card, 'op05_001_used') and card.op05_001_used:
            return False
        card.op05_001_used = True
        return True  # Effect handled by combat system
    return False


# --- OP05-002: Belo Betty (Leader) ---
@register_effect("OP05-002", "activate", "[Activate: Main] Trash Rev Army: Up to 3 Rev Army +1000")
def op05_002_betty_leader(game_state, player, card):
    """Once Per Turn: Trash a Revolutionary Army card from hand, up to 3 Rev Army Characters +1000."""
    if hasattr(card, 'op05_002_used') and card.op05_002_used:
        return False
    rev_army = [c for c in player.hand
                if 'revolutionary army' in (c.card_origin or '').lower()]
    if rev_army:
        to_trash = rev_army[0]
        player.hand.remove(to_trash)
        player.trash.append(to_trash)
        rev_chars = [c for c in player.cards_in_play
                     if 'revolutionary army' in (c.card_origin or '').lower()]
        for char in rev_chars[:3]:
            char.power_modifier = getattr(char, 'power_modifier', 0) + 1000
        card.op05_002_used = True
        return True
    return False


# --- OP05-022: Donquixote Rosinante (Leader) ---
@register_effect("OP05-022", "blocker", "[Blocker] This Leader has Blocker")
def op05_022_rosinante_blocker(game_state, player, card):
    """This Leader has Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP05-022", "end_of_turn", "[End of Your Turn] If 2+ Donquixote Pirates, draw 2 trash 2")
def op05_022_rosinante_eot(game_state, player, card):
    """End of Your Turn: If you have 2 or more Donquixote Pirates Characters, draw 2 and trash 2."""
    donquixote_chars = [c for c in player.cards_in_play
                        if 'donquixote pirates' in (c.card_origin or '').lower()]
    if len(donquixote_chars) >= 2:
        draw_cards(player, 2)
        trash_from_hand(player, 2, game_state, card)
        return True
    return False


# --- OP05-041: Sakazuki (Leader) ---
@register_effect("OP05-041", "activate", "[Activate: Main] Trash 1: Draw 1")
def op05_041_sakazuki_activate(game_state, player, card):
    """Once Per Turn: Trash 1 from hand, draw 1."""
    if hasattr(card, 'op05_041_used') and card.op05_041_used:
        return False
    if player.hand:
        trash_from_hand(player, 1, game_state, card)
        draw_cards(player, 1)
        card.op05_041_used = True
        return True
    return False


@register_effect("OP05-041", "on_attack", "[When Attacking] Opponent char -1 cost")
def op05_041_sakazuki_attack(game_state, player, card):
    """When Attacking: Give up to 1 opponent's Character -1 cost."""
    opponent = get_opponent(game_state, player)
    if opponent.cards_in_play:
        target = opponent.cards_in_play[0]
        target.cost_modifier = getattr(target, 'cost_modifier', 0) - 1
        return True
    return False


# --- OP05-060: Monkey.D.Luffy (Leader) ---
@register_effect("OP05-060", "activate", "[Activate: Main] Add life to hand: If 0 or 3+ DON, add 2 DON")
def op05_060_luffy_leader(game_state, player, card):
    """Once Per Turn: Add 1 Life to hand. If 0 or 3+ DON on field, add up to 2 DON from deck."""
    if hasattr(card, 'op05_060_used') and card.op05_060_used:
        return False
    if player.life_cards:
        life = player.life_cards.pop()
        player.hand.append(life)
        don_count = len(player.don_pool)
        if don_count == 0 or don_count >= 3:
            if hasattr(player, 'don_deck'):
                for _ in range(min(2, len(player.don_deck))):
                    don = player.don_deck.pop(0)
                    player.don_pool.append(don)
        card.op05_060_used = True
        return True
    return False


# --- OP05-098: Enel (Leader) ---
@register_effect("OP05-098", "on_life_zero", "[Opponent's Turn] When Life becomes 0, add 1 to Life, trash 1 from hand")
def op05_098_enel_leader(game_state, player, card):
    """Opponent's Turn, Once Per Turn: When Life becomes 0, add 1 from deck to Life, then trash 1 from hand."""
    if hasattr(card, 'op05_098_used') and card.op05_098_used:
        return False
    if player.deck:
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
    has_7k = any((getattr(c, 'power', 0) or 0) >= 7000 for c in player.cards_in_play if c != card)
    card.has_rush = has_7k
    return True


# --- OP05-004: Emporio.Ivankov ---
@register_effect("OP05-004", "activate", "[Activate: Main] [Once Per Turn] If 7000+ power, play Revolutionary Army 5000 or less")
def op05_004_ivankov(game_state, player, card):
    """Activate: If this has 7000+ power, play Revolutionary Army with 5000 or less power."""
    if not getattr(card, 'op05_004_used', False):
        total_power = (getattr(card, 'power', 0) or 0) + getattr(card, 'power_modifier', 0)
        if total_power >= 7000:
            for c in list(player.hand):
                if 'Revolutionary Army' in (c.card_origin or '') and (getattr(c, 'power', 0) or 0) <= 5000:
                    if getattr(c, 'name', '') != 'Emporio.Ivankov':
                        player.hand.remove(c)
                        player.cards_in_play.append(c)
                        card.op05_004_used = True
                        return True
    return False


# --- OP05-005: Karasu ---
@register_effect("OP05-005", "on_play", "[On Play] If Revolutionary Army Leader, -1000 power")
def op05_005_karasu_play(game_state, player, card):
    """On Play: If Revolutionary Army Leader, give -1000 power."""
    if player.leader and 'Revolutionary Army' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            return create_power_reduction_choice(game_state, player, list(opponent.cards_in_play), -1000, source_card=card,
                                                prompt="Choose opponent's Character to give -1000 power")
    return True


@register_effect("OP05-005", "on_attack", "[When Attacking] If 7000+ power, -1000 power")
def op05_005_karasu_attack(game_state, player, card):
    """When Attacking: If 7000+ power, give -1000 power."""
    total_power = (getattr(card, 'power', 0) or 0) + getattr(card, 'power_modifier', 0)
    if total_power >= 7000:
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            return create_power_reduction_choice(game_state, player, list(opponent.cards_in_play), -1000, source_card=card,
                                                prompt="Choose opponent's Character to give -1000 power")
    return True


# --- OP05-006: Koala ---
@register_effect("OP05-006", "on_play", "[On Play] If Revolutionary Army Leader, -3000 power to Character")
def op05_006_koala(game_state, player, card):
    """On Play: If Revolutionary Army Leader, give Character -3000 power."""
    if player.leader and 'Revolutionary Army' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            return create_power_reduction_choice(game_state, player, list(opponent.cards_in_play), -3000, source_card=card,
                                                prompt="Choose opponent's Character to give -3000 power")
    return True


# --- OP05-007: Sabo ---
@register_effect("OP05-007", "on_play", "[On Play] K.O. up to 2 Characters with total 4000 power or less")
def op05_007_sabo(game_state, player, card):
    """On Play: K.O. up to 2 Characters with total 4000 power or less."""
    opponent = get_opponent(game_state, player)
    targets = sorted([c for c in opponent.cards_in_play], key=lambda c: getattr(c, 'power', 0) or 0)
    total = 0
    ko_targets = []
    for c in targets:
        power = getattr(c, 'power', 0) or 0
        if total + power <= 4000 and len(ko_targets) < 2:
            ko_targets.append(c)
            total += power
    for target in ko_targets:
        opponent.cards_in_play.remove(target)
        opponent.trash.append(target)
    return True


# --- OP05-008: Chaka ---
@register_effect("OP05-008", "activate", "[DON!! x1] [Activate: Main] [Once Per Turn] Give 2 rested DON to Leader or Character")
def op05_008_chaka(game_state, player, card):
    """With 1 DON: Give up to 2 rested DON to Leader or Character."""
    attached = getattr(card, 'attached_don', 0)
    if attached >= 1 and not getattr(card, 'op05_008_used', False):
        rested_don = player.don_pool.count("rested")[:2]
        targets = list(player.cards_in_play)
        if player.leader:
            targets.append(player.leader)
        if targets and rested_don:
            card.op05_008_used = True
            return create_don_attach_choice(game_state, player, targets, source_card=card,
                                           prompt="Choose Leader or Character to give up to 2 rested DON")
    return False


# --- OP05-009: Toh-Toh ---
@register_effect("OP05-009", "on_play", "[On Play] Draw 1 if Leader has 0 or less power")
def op05_009_tohtoh(game_state, player, card):
    """On Play: Draw 1 if Leader has 0 or less power."""
    if player.leader:
        total_power = (getattr(player.leader, 'power', 0) or 0) + getattr(player.leader, 'power_modifier', 0)
        if total_power <= 0:
            draw_cards(player, 1)
    return True


# --- OP05-010: Nico Robin ---
@register_effect("OP05-010", "on_play", "[On Play] K.O. Character with 1000 power or less")
def op05_010_robin(game_state, player, card):
    """On Play: K.O. Character with 1000 power or less."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'power', 0) or 0) <= 1000]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                               prompt="Choose Character with 1000 power or less to K.O.")
    return True


# --- OP05-011: Bartholomew Kuma ---
@register_effect("OP05-011", "on_play", "[On Play] K.O. Character with 2000 power or less")
def op05_011_kuma_play(game_state, player, card):
    """On Play: K.O. Character with 2000 power or less."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'power', 0) or 0) <= 2000]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                               prompt="Choose Character with 2000 power or less to K.O.")
    return True


@register_effect("OP05-011", "trigger", "[Trigger] If multicolored Leader, play this card")
def op05_011_kuma_trigger(game_state, player, card):
    """Trigger: Play this card if multicolored Leader."""
    if player.leader and len(getattr(player.leader, 'colors', [])) > 1:
        player.cards_in_play.append(card)
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
        if opponent.cards_in_play:
            return create_power_reduction_choice(game_state, player, list(opponent.cards_in_play), -2000, source_card=card,
                                                prompt="Choose opponent's Character to give -2000 power")
    return True


# --- OP05-015: Belo Betty ---
@register_effect("OP05-015", "on_play", "[On Play] Look at 5, add Revolutionary Army card")
def op05_015_betty(game_state, player, card):
    """On Play: Look at 5 and add Revolutionary Army card."""
    if player.deck:
        top_cards = player.deck[:5]
        for c in top_cards:
            if 'Revolutionary Army' in (c.card_origin or '') and getattr(c, 'name', '') != 'Belo Betty':
                player.hand.append(c)
                player.deck.remove(c)
                break
    return True


# --- OP05-016: Morley ---
@register_effect("OP05-016", "on_attack", "[When Attacking] If 7000+ power, opponent cannot activate Blocker")
def op05_016_morley(game_state, player, card):
    """When Attacking: If 7000+ power, opponent cannot activate Blocker."""
    total_power = (getattr(card, 'power', 0) or 0) + getattr(card, 'power_modifier', 0)
    if total_power >= 7000:
        opponent = get_opponent(game_state, player)
        for c in opponent.cards_in_play:
            c.blocker_disabled = True
    return True


@register_effect("OP05-016", "trigger", "[Trigger] Trash 1: If multicolored Leader, play this card")
def op05_016_morley_trigger(game_state, player, card):
    """Trigger: Trash 1 to play if multicolored Leader."""
    if player.leader and len(getattr(player.leader, 'colors', [])) > 1 and player.hand:
        trash_from_hand(player, 1, game_state, card)
        player.cards_in_play.append(card)
        return True
    return False


# --- OP05-017: Lindbergh ---
@register_effect("OP05-017", "on_attack", "[When Attacking] If 7000+ power, K.O. 3000 power or less")
def op05_017_lindbergh(game_state, player, card):
    """When Attacking: If 7000+ power, K.O. 3000 power or less."""
    total_power = (getattr(card, 'power', 0) or 0) + getattr(card, 'power_modifier', 0)
    if total_power >= 7000:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'power', 0) or 0) <= 3000]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose Character with 3000 power or less to K.O.")
    return True


@register_effect("OP05-017", "trigger", "[Trigger] Trash 1: If multicolored Leader, play this card")
def op05_017_lindbergh_trigger(game_state, player, card):
    """Trigger: Trash 1 to play if multicolored Leader."""
    if player.leader and len(getattr(player.leader, 'colors', [])) > 1 and player.hand:
        trash_from_hand(player, 1, game_state, card)
        player.cards_in_play.append(card)
        return True
    return False


# --- OP05-023: Vergo ---
@register_effect("OP05-023", "on_attack", "[DON!! x1] [When Attacking] K.O. rested cost 3 or less")
def op05_023_vergo(game_state, player, card):
    """When Attacking with 1 DON: K.O. rested cost 3 or less."""
    attached = getattr(card, 'attached_don', 0)
    if attached >= 1:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if getattr(c, 'is_resting', False) and (getattr(c, 'cost', 0) or 0) <= 3]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's rested cost 3 or less Character to K.O.")
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
    if not getattr(card, 'is_resting', False):
        card.is_resting = True
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
        if targets:
            return create_rest_choice(game_state, player, targets, source_card=card,
                                     prompt="Choose opponent's cost 3 or less Character to rest")
        return True
    return False


# --- OP05-026: Sarquiss ---
@register_effect("OP05-026", "on_attack", "[DON!! x1] [When Attacking] [Once Per Turn] Rest cost 3+ to set active")
def op05_026_sarquiss(game_state, player, card):
    """When Attacking with 1 DON: Rest cost 3+ to set this active."""
    attached = getattr(card, 'attached_don', 0)
    if attached >= 1 and not getattr(card, 'op05_026_used', False):
        chars_to_rest = [c for c in player.cards_in_play if (getattr(c, 'cost', 0) or 0) >= 3 and c != card and not getattr(c, 'is_resting', False)]
        if chars_to_rest:
            card.op05_026_used = True
            return create_rest_choice(game_state, player, chars_to_rest, source_card=card,
                                     prompt="Choose your cost 3+ Character to rest (this becomes active)",
                                     callback_action="sarquiss_rest_then_active")
    return False


# --- OP05-027: Trafalgar Law ---
@register_effect("OP05-027", "activate", "[Activate: Main] Trash this: Rest cost 3 or less")
def op05_027_law(game_state, player, card):
    """Activate: Trash this to rest cost 3 or less."""
    if card in player.cards_in_play:
        player.cards_in_play.remove(card)
        player.trash.append(card)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
        if targets:
            return create_rest_choice(game_state, player, targets, source_card=card,
                                     prompt="Choose opponent's cost 3 or less Character to rest")
        return True
    return False


# --- OP05-028: Donquixote Doflamingo ---
@register_effect("OP05-028", "activate", "[Activate: Main] Trash this: K.O. rested cost 2 or less")
def op05_028_doflamingo(game_state, player, card):
    """Activate: Trash this to K.O. rested cost 2 or less."""
    if card in player.cards_in_play:
        player.cards_in_play.remove(card)
        player.trash.append(card)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if getattr(c, 'is_resting', False) and (getattr(c, 'cost', 0) or 0) <= 2]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's rested cost 2 or less Character to K.O.")
        return True
    return False


# --- OP05-029: Donquixote Doflamingo ---
@register_effect("OP05-029", "on_opponent_attack", "[On Opponent's Attack] [Once Per Turn] DON -1: Rest cost 6 or less")
def op05_029_doflamingo(game_state, player, card):
    """On Opponent's Attack: Rest 1 DON to rest cost 6 or less."""
    if not getattr(card, 'op05_029_used', False):
        rested = 0
        for don in player.don_pool:
            if not getattr(don, 'is_resting', False) and rested < 1:
                don.is_resting = True
                rested += 1
        if rested >= 1:
            card.op05_029_used = True
            opponent = get_opponent(game_state, player)
            targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 6]
            if targets:
                return create_rest_choice(game_state, player, targets, source_card=card,
                                         prompt="Choose opponent's cost 6 or less Character to rest")
            return True
    return False


# --- OP05-030: Donquixote Rosinante ---
@register_effect("OP05-030", "blocker", "[Blocker]")
def op05_030_rosinante_blocker(game_state, player, card):
    """Blocker ability."""
    card.has_blocker = True
    return True


@register_effect("OP05-030", "on_ko_prevention", "[Opponent's Turn] If rested Character would be K.O.'d, trash this instead")
def op05_030_rosinante_protection(game_state, player, card):
    """Opponent's Turn: Trash this to save rested Character from K.O."""
    if card in player.cards_in_play:
        player.cards_in_play.remove(card)
        player.trash.append(card)
        return True
    return False


# --- OP05-031: Buffalo ---
@register_effect("OP05-031", "on_attack", "[When Attacking] [Once Per Turn] If 2+ rested Characters, set cost 1 active")
def op05_031_buffalo(game_state, player, card):
    """When Attacking: If 2+ rested Characters, set cost 1 active."""
    if not getattr(card, 'op05_031_used', False):
        rested_chars = [c for c in player.cards_in_play if getattr(c, 'is_resting', False)]
        if len(rested_chars) >= 2:
            cost1_rested = [c for c in rested_chars if (getattr(c, 'cost', 0) or 0) == 1]
            card.op05_031_used = True
            if cost1_rested:
                return create_set_active_choice(game_state, player, cost1_rested, source_card=card,
                                               prompt="Choose your rested cost 1 Character to set active")
    return True


# --- OP05-032: Pica ---
@register_effect("OP05-032", "end_of_turn", "[End of Turn] DON -1: Set this active")
def op05_032_pica_eot(game_state, player, card):
    """End of Turn: Rest 1 DON to set this active."""
    rested = 0
    for don in player.don_pool:
        if not getattr(don, 'is_resting', False) and rested < 1:
            don.is_resting = True
            rested += 1
    if rested >= 1:
        card.is_resting = False
        return True
    return False


@register_effect("OP05-032", "on_ko_prevention", "[Once Per Turn] Rest cost 3+ instead of being K.O.'d")
def op05_032_pica_protection(game_state, player, card):
    """Once Per Turn: Rest cost 3+ instead of being K.O.'d."""
    if not getattr(card, 'op05_032_ko_used', False):
        chars_to_rest = [c for c in player.cards_in_play if (getattr(c, 'cost', 0) or 0) >= 3 and c != card and not getattr(c, 'is_resting', False)]
        if chars_to_rest:
            card.op05_032_ko_used = True
            return create_rest_choice(game_state, player, chars_to_rest, source_card=card,
                                     prompt="Choose your cost 3+ Character to rest (to prevent K.O.)")
    return False


# --- OP05-033: Baby 5 ---
@register_effect("OP05-033", "activate", "[Activate: Main] DON -1, rest: Play Donquixote Pirates cost 2 or less")
def op05_033_baby5(game_state, player, card):
    """Activate: Rest 1 DON and this to play Donquixote Pirates cost 2 or less."""
    if not getattr(card, 'is_resting', False):
        rested = 0
        for don in player.don_pool:
            if not getattr(don, 'is_resting', False) and rested < 1:
                don.is_resting = True
                rested += 1
        if rested >= 1:
            card.is_resting = True
            for c in list(player.hand):
                if 'Donquixote Pirates' in (c.card_origin or '') and (getattr(c, 'cost', 0) or 0) <= 2:
                    player.hand.remove(c)
                    player.cards_in_play.append(c)
                    break
            return True
    return False


# --- OP05-034: Baby 5 ---
@register_effect("OP05-034", "activate", "[Activate: Main] DON -1, rest: Look at 5, add Donquixote Pirates card")
def op05_034_baby5(game_state, player, card):
    """Activate: Rest 1 DON and this to look at 5 and add Donquixote Pirates card."""
    if not getattr(card, 'is_resting', False):
        rested = 0
        for don in player.don_pool:
            if not getattr(don, 'is_resting', False) and rested < 1:
                don.is_resting = True
                rested += 1
        if rested >= 1:
            card.is_resting = True
            if player.deck:
                top_cards = player.deck[:5]
                for c in top_cards:
                    if 'Donquixote Pirates' in (c.card_origin or ''):
                        player.hand.append(c)
                        player.deck.remove(c)
                        break
            return True
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
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
    if targets:
        return create_rest_choice(game_state, player, targets, source_card=card,
                                 prompt="Choose opponent's cost 4 or less Character to rest")
    return True


# --- OP05-042: Issho ---
@register_effect("OP05-042", "on_play", "[On Play] Cost 7 or less cannot attack until next turn")
def op05_042_issho(game_state, player, card):
    """On Play: Cost 7 or less cannot attack until next turn."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 7]
    if targets:
        return create_cannot_attack_choice(game_state, player, targets, source_card=card,
                                          prompt="Choose opponent's cost 7 or less Character that cannot attack")
    return True


# --- OP05-043: Ulti ---
@register_effect("OP05-043", "on_play", "[On Play] If multicolored Leader, look at 3 and add 1")
def op05_043_ulti(game_state, player, card):
    """On Play: If multicolored Leader, look at 3 and add 1."""
    if player.leader and len(getattr(player.leader, 'colors', [])) > 1:
        if player.deck:
            top_cards = player.deck[:3]
            if top_cards:
                player.hand.append(top_cards[0])
                player.deck.remove(top_cards[0])
    return True


# --- OP05-045: Stainless ---
@register_effect("OP05-045", "activate", "[Activate: Main] Trash 1, rest: Bottom cost 2 or less")
def op05_045_stainless(game_state, player, card):
    """Activate: Trash 1 and rest to place cost 2 or less at deck bottom."""
    if not getattr(card, 'is_resting', False) and player.hand:
        trash_from_hand(player, 1, game_state, card)
        card.is_resting = True
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
        if targets:
            return create_bottom_deck_choice(game_state, player, targets, source_card=card,
                                            prompt="Choose opponent's cost 2 or less to place at deck bottom")
        return True
    return False


# --- OP05-046: Dalmatian ---
@register_effect("OP05-046", "on_ko", "[On K.O.] Draw 1, bottom 1")
def op05_046_dalmatian(game_state, player, card):
    """On K.O.: Draw 1 and place 1 at deck bottom."""
    draw_cards(player, 1)
    if player.hand:
        card_to_bottom = player.hand.pop()
        player.deck.append(card_to_bottom)
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
        draw_cards(player, 1)
    card.power_modifier = getattr(card, 'power_modifier', 0) + 1000
    return True


# --- OP05-048: Bastille ---
@register_effect("OP05-048", "on_attack", "[DON!! x1] [When Attacking] Bottom cost 2 or less")
def op05_048_bastille(game_state, player, card):
    """When Attacking with 1 DON: Place cost 2 or less at deck bottom."""
    attached = getattr(card, 'attached_don', 0)
    if attached >= 1:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
        if targets:
            return create_bottom_deck_choice(game_state, player, targets, source_card=card,
                                            prompt="Choose opponent's cost 2 or less to place at deck bottom")
    return True


# --- OP05-049: Haccha ---
@register_effect("OP05-049", "on_attack", "[DON!! x1] [When Attacking] Return cost 3 or less to hand")
def op05_049_haccha(game_state, player, card):
    """When Attacking with 1 DON: Return cost 3 or less to hand."""
    attached = getattr(card, 'attached_don', 0)
    if attached >= 1:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
        if targets:
            return create_return_to_hand_choice(game_state, player, targets, source_card=card,
                                               prompt="Choose opponent's cost 3 or less to return to hand")
    return True


# --- OP05-050: Hina ---
@register_effect("OP05-050", "on_play", "[On Play] Draw 1 if 5 or less hand")
def op05_050_hina(game_state, player, card):
    """On Play: Draw 1 if 5 or less hand."""
    if len(player.hand) <= 5:
        draw_cards(player, 1)
    return True


# --- OP05-051: Borsalino ---
@register_effect("OP05-051", "on_play", "[On Play] Bottom cost 4 or less")
def op05_051_borsalino(game_state, player, card):
    """On Play: Place cost 4 or less at deck bottom."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
    if targets:
        return create_bottom_deck_choice(game_state, player, targets, source_card=card,
                                        prompt="Choose opponent's cost 4 or less to place at deck bottom")
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
    if not getattr(card, 'op05_053_used', False):
        card.power_modifier = getattr(card, 'power_modifier', 0) + 2000
        card.op05_053_used = True
    return True


# --- OP05-054: Monkey.D.Garp ---
@register_effect("OP05-054", "on_play", "[On Play] Draw 2, bottom 2")
def op05_054_garp(game_state, player, card):
    """On Play: Draw 2 and place 2 at deck bottom."""
    draw_cards(player, 2)
    for _ in range(min(2, len(player.hand))):
        card_to_bottom = player.hand.pop()
        player.deck.append(card_to_bottom)
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
    # Simplified: just shuffle top 5
    if len(player.deck) >= 5:
        import random
        top5 = player.deck[:5]
        random.shuffle(top5)
        player.deck[:5] = top5
    return True


# --- OP05-056: X.Barrels ---
@register_effect("OP05-056", "on_play", "[On Play] Bottom own Character: Draw 1")
def op05_056_barrels(game_state, player, card):
    """On Play: Place own Character at deck bottom to draw 1."""
    other_chars = [c for c in player.cards_in_play if c != card]
    if other_chars:
        target = other_chars[0]
        player.cards_in_play.remove(target)
        player.deck.append(target)
        draw_cards(player, 1)
    return True


# --- OP05-061: Uso-Hachi ---
@register_effect("OP05-061", "on_attack", "[DON!! x1] [When Attacking] If 8+ DON, rest cost 4 or less")
def op05_061_usohachi(game_state, player, card):
    """When Attacking with 1 DON: If 8+ DON, rest cost 4 or less."""
    attached = getattr(card, 'attached_don', 0)
    if attached >= 1 and len(player.don_pool) >= 8:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
        if targets:
            return create_rest_choice(game_state, player, targets, source_card=card,
                                     prompt="Choose opponent's cost 4 or less Character to rest")
    return True


# --- OP05-062: O-Nami ---
@register_effect("OP05-062", "continuous", "If 10 DON, gains Blocker")
def op05_062_onami(game_state, player, card):
    """Continuous: Gains Blocker if 10 DON."""
    card.has_blocker = len(player.don_pool) >= 10
    return True


# --- OP05-063: O-Robi ---
@register_effect("OP05-063", "on_play", "[On Play] If 8+ DON, K.O. cost 3 or less")
def op05_063_orobi(game_state, player, card):
    """On Play: If 8+ DON, K.O. cost 3 or less."""
    if len(player.don_pool) >= 8:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's cost 3 or less Character to K.O.")
    return True


# --- OP05-064: Killer ---
@register_effect("OP05-064", "on_play", "[On Play] Look at 5, add Kid Pirates card")
def op05_064_killer(game_state, player, card):
    """On Play: Look at 5 and add Kid Pirates card."""
    if player.deck:
        top_cards = player.deck[:5]
        for c in top_cards:
            if 'Kid Pirates' in (c.card_origin or '') and getattr(c, 'name', '') != 'Killer':
                player.hand.append(c)
                player.deck.remove(c)
                break
    return True


# --- OP05-066: Jinbe ---
@register_effect("OP05-066", "blocker", "[Blocker]")
def op05_066_jinbe_blocker(game_state, player, card):
    """Blocker ability."""
    card.has_blocker = True
    return True


@register_effect("OP05-066", "continuous", "[Opponent's Turn] If 10 DON, +1000")
def op05_066_jinbe_continuous(game_state, player, card):
    """Opponent's Turn: If 10 DON, +1000 power."""
    if len(player.don_pool) >= 10:
        card.power_modifier = getattr(card, 'power_modifier', 0) + 1000
    return True


# --- OP05-067: Zoro-Juurou ---
@register_effect("OP05-067", "on_attack", "[When Attacking] If 3 or less Life, add active DON")
def op05_067_zorojuurou(game_state, player, card):
    """When Attacking: If 3 or less Life, add active DON."""
    if len(player.life_cards) <= 3:
        add_don_from_deck(player, 1, rested=False)
    return True


# --- OP05-068: Chopa-Emon ---
@register_effect("OP05-068", "on_play", "[On Play] If 8+ DON, set purple Straw Hat 6000 or less active")
def op05_068_chopaemon(game_state, player, card):
    """On Play: If 8+ DON, set purple Straw Hat 6000 or less active."""
    if len(player.don_pool) >= 8:
        targets = [c for c in player.cards_in_play
                   if 'Purple' in getattr(c, 'colors', [])
                   and 'Straw Hat Crew' in (c.card_origin or '')
                   and (getattr(c, 'power', 0) or 0) <= 6000
                   and getattr(c, 'is_resting', False)]
        if targets:
            return create_set_active_choice(game_state, player, targets, source_card=card,
                                           prompt="Choose purple Straw Hat 6000 power or less to set active")
    return True


# --- OP05-069: Trafalgar Law ---
@register_effect("OP05-069", "on_attack", "[When Attacking] If opponent has more DON, look at 5 and add Heart Pirates")
def op05_069_law(game_state, player, card):
    """When Attacking: If opponent has more DON, look at 5 and add Heart Pirates."""
    opponent = get_opponent(game_state, player)
    if len(opponent.don_pool) > len(player.don_pool):
        if player.deck:
            top_cards = player.deck[:5]
            for c in top_cards:
                if 'Heart Pirates' in (c.card_origin or ''):
                    player.hand.append(c)
                    player.deck.remove(c)
                    break
    return True


# --- OP05-070: Fra-Nosuke ---
@register_effect("OP05-070", "continuous", "[DON!! x1] If 8+ DON, gains Rush")
def op05_070_franosuke(game_state, player, card):
    """With 1 DON: If 8+ DON, gains Rush."""
    attached = getattr(card, 'attached_don', 0)
    if attached >= 1 and len(player.don_pool) >= 8:
        card.has_rush = True
    return True


# --- OP05-071: Bepo ---
@register_effect("OP05-071", "on_attack", "[When Attacking] If opponent has more DON, -2000 power")
def op05_071_bepo(game_state, player, card):
    """When Attacking: If opponent has more DON, give -2000 power."""
    opponent = get_opponent(game_state, player)
    if len(opponent.don_pool) > len(player.don_pool):
        if opponent.cards_in_play:
            return create_power_reduction_choice(game_state, player, list(opponent.cards_in_play), -2000, source_card=card,
                                                prompt="Choose opponent's Character to give -2000 power")
    return True


# --- OP05-072: Hone-Kichi ---
@register_effect("OP05-072", "on_play", "[On Play] If 8+ DON, -2000 to 2 Characters")
def op05_072_honekichi(game_state, player, card):
    """On Play: If 8+ DON, give -2000 to 2 Characters."""
    if len(player.don_pool) >= 8:
        opponent = get_opponent(game_state, player)
        for i, c in enumerate(opponent.cards_in_play[:2]):
            c.power_modifier = getattr(c, 'power_modifier', 0) - 2000
    return True


# --- OP05-073: Miss Doublefinger ---
@register_effect("OP05-073", "on_play", "[On Play] Trash 1: Add rested DON")
def op05_073_doublefinger_play(game_state, player, card):
    """On Play: Trash 1 to add rested DON."""
    if player.hand:
        trash_from_hand(player, 1, game_state, card)
        add_don_from_deck(player, 1, rested=True)
    return True


@register_effect("OP05-073", "trigger", "[Trigger] DON -1: Play this card")
def op05_073_doublefinger_trigger(game_state, player, card):
    """Trigger: Return 1 DON to play this card."""
    if player.don_pool:
        don = player.don_pool.pop()
        player.don_deck.append(don)
        player.cards_in_play.append(card)
        return True
    return False


# --- OP05-074: Eustass"Captain"Kid ---
@register_effect("OP05-074", "blocker", "[Blocker]")
def op05_074_kid_blocker(game_state, player, card):
    """Blocker ability."""
    card.has_blocker = True
    return True


@register_effect("OP05-074", "on_don_return", "[Your Turn] [Once Per Turn] When DON returns to deck, add active DON")
def op05_074_kid_don_return(game_state, player, card):
    """Your Turn: When DON returns to deck, add active DON."""
    if not getattr(card, 'op05_074_used', False):
        add_don_from_deck(player, 1, rested=False)
        card.op05_074_used = True
    return True


# --- OP05-075: Mr.1 ---
@register_effect("OP05-075", "on_opponent_attack", "[On Opponent's Attack] [Once Per Turn] DON -1: Play Baroque Works cost 3 or less")
def op05_075_mr1(game_state, player, card):
    """On Opponent's Attack: Return 1 DON to play Baroque Works cost 3 or less."""
    if not getattr(card, 'op05_075_used', False) and player.don_pool:
        don = player.don_pool.pop()
        player.don_deck.append(don)
        for c in list(player.hand):
            if 'Baroque Works' in (c.card_origin or '') and (getattr(c, 'cost', 0) or 0) <= 3:
                player.hand.remove(c)
                player.cards_in_play.append(c)
                break
        card.op05_075_used = True
        return True
    return False


# --- OP05-079: Viola ---
@register_effect("OP05-079", "on_play", "[On Play] Opponent bottoms 3 cards from trash")
def op05_079_viola(game_state, player, card):
    """On Play: Opponent places 3 cards from trash at deck bottom."""
    opponent = get_opponent(game_state, player)
    for _ in range(min(3, len(opponent.trash))):
        card_to_bottom = opponent.trash.pop()
        opponent.deck.append(card_to_bottom)
    return True


# --- OP05-080: Elizabello II ---
@register_effect("OP05-080", "on_attack", "[When Attacking] [Once Per Turn] Return 20 trash to deck: Double Attack +10000")
def op05_080_elizabello(game_state, player, card):
    """When Attacking: Return 20 trash to deck for Double Attack +10000."""
    if not getattr(card, 'op05_080_used', False) and len(player.trash) >= 20:
        for _ in range(20):
            card_to_return = player.trash.pop()
            player.deck.append(card_to_return)
        import random
        random.shuffle(player.deck)
        card.has_double_attack = True
        card.power_modifier = getattr(card, 'power_modifier', 0) + 10000
        card.op05_080_used = True
        return True
    return False


# --- OP05-081: One-Legged Toy Soldier ---
@register_effect("OP05-081", "activate", "[Activate: Main] Trash this: -3 cost")
def op05_081_toy_soldier(game_state, player, card):
    """Activate: Trash this to give -3 cost."""
    if card in player.cards_in_play:
        player.cards_in_play.remove(card)
        player.trash.append(card)
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            opponent.cards_in_play[0].cost_modifier = getattr(opponent.cards_in_play[0], 'cost_modifier', 0) - 3
        return True
    return False


# --- OP05-082: Shirahoshi ---
@register_effect("OP05-082", "activate", "[Activate: Main] Rest, bottom 2 trash: If opponent has 6+ hand, they trash 1")
def op05_082_shirahoshi(game_state, player, card):
    """Activate: Rest and bottom 2 trash to make opponent trash 1 if 6+ hand."""
    if not getattr(card, 'is_resting', False) and len(player.trash) >= 2:
        card.is_resting = True
        for _ in range(2):
            card_to_bottom = player.trash.pop()
            player.deck.append(card_to_bottom)
        opponent = get_opponent(game_state, player)
        if len(opponent.hand) >= 6 and opponent.hand:
            opponent.trash.append(opponent.hand.pop())
        return True
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
    card.has_blocker = len(player.trash) >= 10
    return True


# --- OP05-087: Hakuba ---
@register_effect("OP05-087", "on_attack", "[DON!! x1] [When Attacking] K.O. own Character: -5 cost")
def op05_087_hakuba(game_state, player, card):
    """When Attacking with 1 DON: K.O. own Character to give -5 cost."""
    attached = getattr(card, 'attached_don', 0)
    if attached >= 1:
        other_chars = [c for c in player.cards_in_play if c != card]
        if other_chars:
            target = other_chars[0]
            player.cards_in_play.remove(target)
            player.trash.append(target)
            opponent = get_opponent(game_state, player)
            if opponent.cards_in_play:
                opponent.cards_in_play[0].cost_modifier = getattr(opponent.cards_in_play[0], 'cost_modifier', 0) - 5
    return True


# --- OP05-088: Mansherry ---
@register_effect("OP05-088", "activate", "[Activate: Main] DON -1, rest, bottom 2 trash: Add black cost 3-5 from trash")
def op05_088_mansherry(game_state, player, card):
    """Activate: Rest, DON -1, bottom 2 trash to add black cost 3-5 from trash."""
    if not getattr(card, 'is_resting', False) and len(player.trash) >= 2:
        rested = 0
        for don in player.don_pool:
            if not getattr(don, 'is_resting', False) and rested < 1:
                don.is_resting = True
                rested += 1
        if rested >= 1:
            card.is_resting = True
            for _ in range(2):
                card_to_bottom = player.trash.pop()
                player.deck.append(card_to_bottom)
            for c in list(player.trash):
                if 'Black' in getattr(c, 'colors', []) and 3 <= (getattr(c, 'cost', 0) or 0) <= 5:
                    player.trash.remove(c)
                    player.hand.append(c)
                    break
            return True
    return False


# --- OP05-089: Saint Mjosgard ---
@register_effect("OP05-089", "activate", "[Activate: Main] DON -1, rest this and Character: Add black cost 1 from trash")
def op05_089_mjosgard(game_state, player, card):
    """Activate: Rest DON, this and Character to add black cost 1 from trash."""
    if not getattr(card, 'is_resting', False):
        rested = 0
        for don in player.don_pool:
            if not getattr(don, 'is_resting', False) and rested < 1:
                don.is_resting = True
                rested += 1
        if rested >= 1:
            other_chars = [c for c in player.cards_in_play if c != card and not getattr(c, 'is_resting', False)]
            if other_chars:
                card.is_resting = True
                other_chars[0].is_resting = True
                for c in list(player.trash):
                    if 'Black' in getattr(c, 'colors', []) and (getattr(c, 'cost', 0) or 0) == 1:
                        player.trash.remove(c)
                        player.hand.append(c)
                        break
                return True
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
    dressrosa = [c for c in player.cards_in_play if 'Dressrosa' in (c.card_origin or '')]
    if dressrosa:
        dressrosa[0].power_modifier = getattr(dressrosa[0], 'power_modifier', 0) + 2000
    return True


@register_effect("OP05-090", "on_ko", "[On K.O.] Dressrosa +2000")
def op05_090_riku_ko(game_state, player, card):
    """On K.O.: Dressrosa gains +2000."""
    dressrosa = [c for c in player.cards_in_play if 'Dressrosa' in (c.card_origin or '')]
    if dressrosa:
        dressrosa[0].power_modifier = getattr(dressrosa[0], 'power_modifier', 0) + 2000
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
    # Add from trash
    for c in list(player.trash):
        if 'Black' in getattr(c, 'colors', []) and 3 <= (getattr(c, 'cost', 0) or 0) <= 7 and getattr(c, 'name', '') != 'Rebecca':
            player.trash.remove(c)
            player.hand.append(c)
            break
    # Play from hand rested
    for c in list(player.hand):
        if 'Black' in getattr(c, 'colors', []) and (getattr(c, 'cost', 0) or 0) <= 3:
            player.hand.remove(c)
            c.is_resting = True
            player.cards_in_play.append(c)
            break
    return True


# --- OP05-092: Saint Rosward ---
@register_effect("OP05-092", "continuous", "[Your Turn] If only Celestial Dragons, opponent Characters -6 cost")
def op05_092_rosward(game_state, player, card):
    """Your Turn: If only Celestial Dragons, opponent Characters -6 cost."""
    all_celestial = all('Celestial Dragons' in (c.card_origin or '') for c in player.cards_in_play)
    if all_celestial:
        opponent = get_opponent(game_state, player)
        for c in opponent.cards_in_play:
            c.cost_modifier = getattr(c, 'cost_modifier', 0) - 6
    return True


# --- OP05-093: Rob Lucci ---
@register_effect("OP05-093", "on_play", "[On Play] Bottom 3 trash: K.O. cost 2 or less and cost 1 or less")
def op05_093_lucci(game_state, player, card):
    """On Play: Bottom 3 trash to K.O. cost 2 or less and cost 1 or less."""
    if len(player.trash) >= 3:
        for _ in range(3):
            card_to_bottom = player.trash.pop()
            player.deck.append(card_to_bottom)
        opponent = get_opponent(game_state, player)
        # K.O. cost 2 or less
        targets2 = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
        if targets2:
            target = targets2[0]
            opponent.cards_in_play.remove(target)
            opponent.trash.append(target)
        # K.O. cost 1 or less
        targets1 = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 1]
        if targets1:
            target = targets1[0]
            opponent.cards_in_play.remove(target)
            opponent.trash.append(target)
    return True


# --- OP05-099: Amazon ---
@register_effect("OP05-099", "on_opponent_attack", "[On Opponent's Attack] Rest: Opponent trashes Life or -2000 power")
def op05_099_amazon(game_state, player, card):
    """On Opponent's Attack: Rest to make opponent choose trash Life or -2000 power."""
    if not getattr(card, 'is_resting', False):
        card.is_resting = True
        opponent = get_opponent(game_state, player)
        # Simplified: give -2000 power
        if opponent.cards_in_play:
            opponent.cards_in_play[0].power_modifier = getattr(opponent.cards_in_play[0], 'power_modifier', 0) - 2000
        return True
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
    if not getattr(card, 'op05_100_used', False) and player.life_cards:
        # Check for Luffy
        opponent = get_opponent(game_state, player)
        has_luffy = any('Monkey.D.Luffy' in getattr(c, 'name', '') for c in opponent.cards_in_play)
        if not has_luffy:
            player.trash.append(player.life_cards.pop())
            card.op05_100_used = True
            return True
    return False


# --- OP05-101: Ohm ---
@register_effect("OP05-101", "continuous", "If 2 or less Life, +1000")
def op05_101_ohm_continuous(game_state, player, card):
    """Continuous: +1000 if 2 or less Life."""
    if len(player.life_cards) <= 2:
        card.power_modifier = getattr(card, 'power_modifier', 0) + 1000
    return True


@register_effect("OP05-101", "on_play", "[On Play] Look at 5, add Holly and play it")
def op05_101_ohm_play(game_state, player, card):
    """On Play: Look at 5, add Holly and play it."""
    if player.deck:
        top_cards = player.deck[:5]
        for c in top_cards:
            if getattr(c, 'name', '') == 'Holly':
                player.deck.remove(c)
                player.cards_in_play.append(c)
                break
    return True


# --- OP05-102: Gedatsu ---
@register_effect("OP05-102", "on_play", "[On Play] K.O. cost equal to opponent's Life count")
def op05_102_gedatsu(game_state, player, card):
    """On Play: K.O. cost equal to or less than opponent's Life count."""
    opponent = get_opponent(game_state, player)
    life_count = len(opponent.life_cards)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= life_count]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                               prompt=f"Choose opponent's cost {life_count} or less Character to K.O.")
    return True


# --- OP05-103: Kotori ---
@register_effect("OP05-103", "on_play", "[On Play] If Hotori, K.O. cost equal to opponent's Life count")
def op05_103_kotori(game_state, player, card):
    """On Play: If Hotori, K.O. cost equal to opponent's Life count."""
    has_hotori = any(getattr(c, 'name', '') == 'Hotori' for c in player.cards_in_play)
    if has_hotori:
        opponent = get_opponent(game_state, player)
        life_count = len(opponent.life_cards)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= life_count]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt=f"Choose opponent's cost {life_count} or less Character to K.O.")
    return True


# --- OP05-104: Conis ---
@register_effect("OP05-104", "on_play", "[On Play] Bottom Stage: Draw 1, trash 1")
def op05_104_conis(game_state, player, card):
    """On Play: Bottom Stage to draw 1 and trash 1."""
    if player.stage:
        stage = player.stage
        player.stage = None
        player.deck.append(stage)
        draw_cards(player, 1)
        trash_from_hand(player, 1, game_state, card)
    return True


# --- OP05-105: Satori ---
@register_effect("OP05-105", "trigger", "[Trigger] Trash 1: Play this card")
def op05_105_satori(game_state, player, card):
    """Trigger: Trash 1 to play this card."""
    if player.hand:
        trash_from_hand(player, 1, game_state, card)
        player.cards_in_play.append(card)
        return True
    return False


# --- OP05-106: Shura ---
@register_effect("OP05-106", "on_play", "[On Play] Look at 5, add Sky Island card")
def op05_106_shura_play(game_state, player, card):
    """On Play: Look at 5 and add Sky Island card."""
    if player.deck:
        top_cards = player.deck[:5]
        for c in top_cards:
            if 'Sky Island' in (c.card_origin or '') and getattr(c, 'name', '') != 'Shura':
                player.hand.append(c)
                player.deck.remove(c)
                break
    return True


@register_effect("OP05-106", "trigger", "[Trigger] Play this card")
def op05_106_shura_trigger(game_state, player, card):
    """Trigger: Play this card."""
    player.cards_in_play.append(card)
    return True


# --- OP05-107: Lieutenant Spacey ---
@register_effect("OP05-107", "on_life_add", "[Your Turn] [Once Per Turn] When card added from Life, +2000")
def op05_107_spacey(game_state, player, card):
    """Your Turn: When card added from Life, +2000."""
    if not getattr(card, 'op05_107_used', False):
        card.power_modifier = getattr(card, 'power_modifier', 0) + 2000
        card.op05_107_used = True
    return True


# --- OP05-109: Pagaya ---
@register_effect("OP05-109", "on_trigger", "[Once Per Turn] When Trigger activates, draw 2 trash 2")
def op05_109_pagaya(game_state, player, card):
    """Once Per Turn: When Trigger activates, draw 2 trash 2."""
    if not getattr(card, 'op05_109_used', False):
        draw_cards(player, 2)
        trash_from_hand(player, 2, game_state, card)
        card.op05_109_used = True
    return True


# --- OP05-111: Hotori ---
@register_effect("OP05-111", "on_play", "[On Play] Play Kotori: Add opponent's cost 3 or less to their Life")
def op05_111_hotori(game_state, player, card):
    """On Play: Play Kotori to add opponent's cost 3 or less to their Life."""
    for c in list(player.hand):
        if getattr(c, 'name', '') == 'Kotori':
            player.hand.remove(c)
            player.cards_in_play.append(c)
            opponent = get_opponent(game_state, player)
            targets = [char for char in opponent.cards_in_play if (getattr(char, 'cost', 0) or 0) <= 3]
            if targets:
                return create_bottom_deck_choice(game_state, player, targets, source_card=card,
                                                prompt="Choose opponent's cost 3 or less to add to Life",
                                                callback_action="add_to_opponent_life")
            break
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
    for c in list(player.hand):
        if 'Sky Island' in (c.card_origin or '') and (getattr(c, 'cost', 0) or 0) == 1:
            player.hand.remove(c)
            player.cards_in_play.append(c)
            break
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
        draw_cards(player, 4)
    return True


# --- OP05-119: Monkey.D.Luffy ---
@register_effect("OP05-119", "on_play", "[On Play] DON -10: Bottom all Characters except this, take extra turn")
def op05_119_luffy_play(game_state, player, card):
    """On Play: Return 10 DON to bottom all Characters and take extra turn."""
    if len(player.don_pool) >= 10:
        for _ in range(10):
            don = player.don_pool.pop()
            player.don_deck.append(don)
        for c in list(player.cards_in_play):
            if c != card:
                player.cards_in_play.remove(c)
                player.deck.append(c)
        player.extra_turn = True
    return True


@register_effect("OP05-119", "activate", "[Activate: Main] [Once Per Turn] DON -1: Add active DON")
def op05_119_luffy_activate(game_state, player, card):
    """Activate: Rest 1 DON to add active DON."""
    if not getattr(card, 'op05_119_used', False):
        rested = 0
        for don in player.don_pool:
            if not getattr(don, 'is_resting', False) and rested < 1:
                don.is_resting = True
                rested += 1
        if rested >= 1:
            add_don_from_deck(player, 1, rested=False)
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

    # Pay cost: rest this stage
    card.is_resting = True
    card.main_activated_this_turn = True

    # Create trash-from-hand choice, then chain to search
    return create_hand_discard_choice(
        game_state, player, list(player.hand),
        callback_action="rev_army_hq_trash_then_search",
        source_card=card,
        prompt="Choose 1 card from hand to trash (cost for Revolutionary Army HQ search)")


# --- OP05-076: When You're at Sea... (Event) ---
@register_effect("OP05-076", "on_play", "[Main] Look at 3, reveal SHC/Kid/Heart Pirates card to hand")
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

