"""
Hardcoded effects for OP07 cards.
"""

from ..hardcoded import (
    create_bottom_deck_choice, create_don_assignment_choice, create_ko_choice, create_own_character_choice,
    create_play_from_hand_choice, create_play_from_trash_choice, create_rest_choice, create_return_to_hand_choice,
    create_target_choice, add_power_modifier, check_leader_type, check_life_count,
    draw_cards, get_opponent, register_effect,
    search_top_cards, trash_from_hand,
)


# --- OP07-117: Egghead Stage ---
@register_effect("OP07-117", "END_OF_TURN", "If 3 or less Life, set Egghead cost 5 or less active")
def egghead_stage_effect(game_state, player, card):
    if len(player.life_cards) <= 3:
        egghead = [c for c in player.cards_in_play
                  if 'egghead' in (c.card_origin or '').lower()
                  and (getattr(c, 'cost', 0) or 0) <= 5]
        if egghead:
            egghead[0].is_resting = False
            return True
    return False


# --- OP07-001: Monkey.D.Dragon (Leader) ---
@register_effect("OP07-001", "MAIN", "Give up to 2 given DON to 1 char")
def dragon_leader_effect(game_state, player, card):
    # Find card with attached DON
    for c in player.cards_in_play:
        if getattr(c, 'attached_don', 0) >= 2:
            # Can redistribute - implementation depends on game logic
            return True
    return False


# --- OP07-001: Monkey.D.Dragon ---
@register_effect("OP07-001", "ACTIVATE_MAIN", "Give up to 2 DON to 1 Character")
def dragon_effect(game_state, player, card):
    if player.cards_in_play:
        return create_don_assignment_choice(
            game_state, player, player.cards_in_play, don_count=2,
            source_card=card, rested_only=False,
            prompt="Choose a Character to give 2 DON"
        )
    return False


# =============================================================================
# MORE LEADER CONDITION CARDS - Supernovas
# =============================================================================

# --- OP07-029: Basil Hawkins ---
@register_effect("OP07-029", "PASSIVE", "If Leader is Supernovas, gains Blocker")
def op07_029_hawkins(game_state, player, card):
    if check_leader_type(player, "Supernovas"):
        card.has_blocker = True
    return True


# --- OP07-030: Captain Kid ---
@register_effect("OP07-030", "WHEN_ATTACKING", "If opponent has 2 or less life, +3000 power")
def op07_030_kid(game_state, player, card):
    opponent = get_opponent(game_state, player)
    if check_life_count(opponent, 2, 'le'):
        add_power_modifier(card, 3000)
    return True


# --- OP07-106: Fuza ---
@register_effect("OP07-106", "WHEN_ATTACKING", "If DONx1 and 1 or less life, KO cost 3 or less")
def op07_106_fuza(game_state, player, card):
    """When Attacking (DONx1): If 1 or less life, KO cost 3 or less."""
    if getattr(card, 'attached_don', 0) >= 1 and check_life_count(player, 1):
        return ko_opponent_character(game_state, player, max_cost=3, source_card=card)
    return False


# --- OP07-109: Monkey.D.Luffy ---
@register_effect("OP07-109", "ACTIVATE_MAIN", "Trash this: If 2 or less life, KO cost 4 or less and draw")
def op07_109_luffy(game_state, player, card):
    """Activate Main: Trash this, if 2 or less life KO cost 4 or less and draw."""
    if card in player.cards_in_play:
        player.cards_in_play.remove(card)
        player.trash.append(card)
        draw_cards(player, 1)  # Draw happens regardless
        if check_life_count(player, 2):
            return ko_opponent_character(game_state, player, max_cost=4, source_card=card)
        return True
    return False


# --- OP07-112: Lucy ---
@register_effect("OP07-112", "WHEN_ATTACKING", "Add life to hand, rest cost 4 or less, if 1 or less life draw")
def op07_112_lucy(game_state, player, card):
    """When Attacking: Add life to hand, rest cost 4 or less, if 1 or less life draw."""
    if player.life_cards:
        life = player.life_cards.pop()
        player.hand.append(life)
        if check_life_count(player, 1):
            draw_cards(player, 1)
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


# --- OP07-115: I Re-Quasar Helllp!! ---
@register_effect("OP07-115", "COUNTER", "If 2 or less life, +3000 power")
def op07_115_requasar(game_state, player, card):
    """Counter: If 2 or less life, +3000 power."""
    if check_life_count(player, 2):
        target = player.leader if player.leader else (player.cards_in_play[0] if player.cards_in_play else None)
        if target:
            add_power_modifier(target, 3000)
            return True
    return False


# --- OP07-116: Blaze Slice ---
@register_effect("OP07-116", "MAIN", "+1000 power, rest opponent's cost 3 or less if opponent has 2 or less life")
def op07_116_blaze_slice(game_state, player, card):
    """Main/Counter: +1000 power, rest cost 3 or less if opponent has 2 or less life."""
    target = player.leader if player.leader else (player.cards_in_play[0] if player.cards_in_play else None)
    if target:
        add_power_modifier(target, 1000)
        opponent = get_opponent(game_state, player)
        if len(opponent.life_cards) <= 2:
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


# --- OP07-094: Shave ---
@register_effect("OP07-094", "COUNTER", "+2000 power, return CP char to hand if 10+ trash")
def op07_094_shave(game_state, player, card):
    """Counter: +2000 power, return CP char to hand if 10+ trash."""
    target = player.leader if player.leader else (player.cards_in_play[0] if player.cards_in_play else None)
    if target:
        add_power_modifier(target, 2000)
        if check_trash_count(player, 10):
            cp_chars = [c for c in player.cards_in_play
                       if 'cp' in (c.card_origin or '').lower()]
            if cp_chars:
                c = cp_chars[0]
                player.cards_in_play.remove(c)
                player.hand.append(c)
        return True
    return False


# --- OP07-095: Iron Body ---
@register_effect("OP07-095", "COUNTER", "+4000 power, +2000 more if 10+ trash")
def op07_095_iron_body(game_state, player, card):
    """Counter: +4000 power, additional +2000 if 10+ trash."""
    target = player.leader if player.leader else (player.cards_in_play[0] if player.cards_in_play else None)
    if target:
        add_power_modifier(target, 4000)
        if check_trash_count(player, 10):
            add_power_modifier(target, 2000)
        return True
    return False


# --- OP07-096: Tempest Kick ---
@register_effect("OP07-096", "MAIN", "Draw 1, -3 cost to opponent's char if 10+ trash")
def op07_096_tempest_kick(game_state, player, card):
    """Main: Draw 1, give opponent's char -3 cost if 10+ trash."""
    draw_cards(player, 1)
    if check_trash_count(player, 10):
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            opponent.cards_in_play[0].cost_modifier = getattr(opponent.cards_in_play[0], 'cost_modifier', 0) - 3
    return True


# =============================================================================
# SACRIFICE COST CARDS - "Return/Trash X of your Characters..."
# =============================================================================

# --- OP07-056: Slave Arrow ---
@register_effect("OP07-056", "COUNTER", "Return cost 2+ char to hand: +4000 power")
def op07_056_slave_arrow(game_state, player, card):
    """Counter: Return cost 2+ char to hand, +4000 power."""
    targets = [c for c in player.cards_in_play if (getattr(c, 'cost', 0) or 0) >= 2]
    if targets:
        targets_snap = list(targets)
        def slave_arrow_cb(selected: list) -> None:
            target_idx = int(selected[0]) if selected else -1
            if 0 <= target_idx < len(targets_snap):
                target = targets_snap[target_idx]
                if target in player.cards_in_play:
                    player.cards_in_play.remove(target)
                    player.hand.append(target)
                    game_state._log(f"{target.name} returned to hand")
                    if player.leader:
                        player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 4000
                        game_state._log(f"Leader gained +4000 power")
        return create_own_character_choice(
            game_state, player, targets,
            source_card=card,
            callback=slave_arrow_cb,
            prompt="Choose your cost 2+ Character to return to hand (Leader gains +4000 power)"
        )
    return False


# =============================================================================
# LEADER CARD EFFECTS - OP07 (500 Years in the Future)
# =============================================================================

# --- OP07-001: Monkey.D.Dragon (Leader) ---
@register_effect("OP07-001", "activate", "[Activate: Main] Give up to 2 attached DON to 1 Character")
def op07_001_dragon_leader(game_state, player, card):
    """Once Per Turn: Give up to 2 of your currently attached DON cards to 1 of your Characters."""
    if hasattr(card, 'op07_001_used') and card.op07_001_used:
        return False
    # Find cards with attached DON
    cards_with_don = [c for c in [player.leader] + player.cards_in_play
                      if getattr(c, 'attached_don', 0) > 0 and c != card]
    if cards_with_don and player.cards_in_play:
        source = cards_with_don[0]
        transfer = min(2, getattr(source, 'attached_don', 0))
        source.attached_don = getattr(source, 'attached_don', 0) - transfer
        card.op07_001_used = True
        # Player chooses which character receives the DON
        return create_don_assignment_choice(game_state, player, player.cards_in_play,
                                            transfer, source_card=card, rested_only=False,
                                            prompt="Choose a Character to give DON")
    return False


# --- OP07-019: Jewelry Bonney (Leader) ---
@register_effect("OP07-019", "on_opponent_attack", "[On Opponent's Attack] Rest 1: Rest opponent cost 5-")
def op07_019_bonney_leader(game_state, player, card):
    """Once Per Turn, Rest 1: Rest opponent's Leader or cost 5 or less Character."""
    if hasattr(card, 'op07_019_used') and card.op07_019_used:
        return False
    active_don = player.don_pool.count("active")
    if active_don:
        active_don[0].is_resting = True
        card.op07_019_used = True
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play
                   if not c.is_resting and (getattr(c, 'cost', 0) or 0) <= 5]
        if targets:
            return create_rest_choice(game_state, player, targets, source_card=card,
                                     prompt="Choose opponent's cost 5 or less to rest")
        return True
    return False


# --- OP07-038: Boa Hancock (Leader) ---
@register_effect("OP07-038", "on_character_removed", "[Your Turn] When char removed, if 5- hand, draw 1")
def op07_038_hancock_leader(game_state, player, card):
    """Your Turn, Once Per Turn: When a Character is removed by your effect, if 5 or less hand, draw 1."""
    if hasattr(card, 'op07_038_used') and card.op07_038_used:
        return False
    if len(player.hand) <= 5:
        draw_cards(player, 1)
        card.op07_038_used = True
        return True
    return False


# --- OP07-059: Foxy (Leader) ---
@register_effect("OP07-059", "on_attack", "[When Attacking] DON -3: If 3+ Foxy Pirates, draw 2")
def op07_059_foxy_leader(game_state, player, card):
    """When Attacking, DON -3: If you have 3 or more Foxy Pirates Characters, draw 2 cards."""
    if len(player.don_pool) >= 3:
        foxy_chars = [c for c in player.cards_in_play
                      if 'foxy pirates' in (c.card_origin or '').lower()]
        if len(foxy_chars) >= 3:
            for _ in range(3):
                if player.don_pool:
                    don = player.don_pool.pop()
                    if hasattr(player, 'don_deck'):
                        player.don_deck.append(don)
            draw_cards(player, 2)
            return True
    return False


# --- OP07-079: Rob Lucci (Leader) ---
@register_effect("OP07-079", "on_attack", "[When Attacking] Trash 2 from deck: Opponent char -1 cost")
def op07_079_lucci_leader(game_state, player, card):
    """When Attacking: Trash 2 cards from top of your deck, give opponent's Character -1 cost."""
    if len(player.deck) >= 2:
        for _ in range(2):
            if player.deck:
                trashed = player.deck.pop(0)
                player.trash.append(trashed)
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            target = opponent.cards_in_play[0]
            target.cost_modifier = getattr(target, 'cost_modifier', 0) - 1
        return True
    return False


# --- OP07-097: Vegapunk (Leader) ---
@register_effect("OP07-097", "continuous", "This Leader cannot attack")
def op07_097_vegapunk_continuous(game_state, player, card):
    """This Leader cannot attack."""
    card.cannot_attack = True
    return True


@register_effect("OP07-097", "activate", "[Activate: Main] Rest 1: Play or return Egghead cost 5-")
def op07_097_vegapunk_activate(game_state, player, card):
    """Once Per Turn, Rest 1: Play Egghead cost 5 or less from hand, or return Egghead cost 5 or less to hand."""
    if hasattr(card, 'op07_097_used') and card.op07_097_used:
        return False
    active_don = player.don_pool.count("active")
    if active_don:
        active_don[0].is_resting = True
        # Play from hand
        egghead = [c for c in player.hand
                   if getattr(c, 'card_type', '') == 'CHARACTER'
                   and 'egghead' in (c.card_origin or '').lower()
                   and (getattr(c, 'cost', 0) or 0) <= 5]
        if egghead:
            to_play = egghead[0]
            player.hand.remove(to_play)
            player.cards_in_play.append(to_play)
        card.op07_097_used = True
        return True
    return False


# =============================================================================
# OP07 CHARACTER EFFECTS
# =============================================================================

# --- OP07-002: Ain ---
@register_effect("OP07-002", "on_play", "[On Play] Set opponent's Character power to 0 this turn")
def op07_002_ain(game_state, player, card):
    """On Play: Set opponent's Character power to 0 this turn."""
    opponent = get_opponent(game_state, player)
    if opponent.cards_in_play:
        return create_set_power_zero_choice(game_state, player, list(opponent.cards_in_play), source_card=card,
                                           prompt="Choose opponent's Character to set power to 0")
    return True


# --- OP07-003: Outlook III ---
@register_effect("OP07-003", "activate", "[Activate: Main] Trash this: Give -2000 to up to 2 opponents")
def op07_003_outlook(game_state, player, card):
    """Activate: Trash this to give -2000 to up to 2 opponent's Characters."""
    if card in player.cards_in_play:
        player.cards_in_play.remove(card)
        player.trash.append(card)
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            return create_multi_power_reduction_choice(game_state, player, list(opponent.cards_in_play), 2000, max_targets=2,
                                                      source_card=card, prompt="Choose up to 2 Characters for -2000 power")
        return True
    return False


# --- OP07-004: Curly.Dadan ---
@register_effect("OP07-004", "on_play", "[On Play] Trash 1: Look at 5, add 2000 power or less Character")
def op07_004_dadan(game_state, player, card):
    """On Play: Trash 1 to look at 5 and add 2000 power or less Character."""
    if player.hand:
        trash_from_hand(player, 1, game_state, card)
        looked = player.deck[:5] if len(player.deck) >= 5 else player.deck[:]
        for c in looked:
            card_type = getattr(c, 'card_type', '')
            power = getattr(c, 'power', 0) or 0
            if card_type == 'CHARACTER' and power <= 2000:
                player.deck.remove(c)
                player.hand.append(c)
                break
    return True


# --- OP07-005: Carina ---
@register_effect("OP07-005", "blocker", "[Blocker]")
def op07_005_carina_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP07-005", "on_play", "[On Play] Give -2000 power to opponent's Character")
def op07_005_carina_play(game_state, player, card):
    """On Play: Give -2000 power to opponent's Character."""
    opponent = get_opponent(game_state, player)
    if opponent.cards_in_play:
        return create_power_reduction_choice(game_state, player, list(opponent.cards_in_play), 2000,
                                            source_card=card, prompt="Choose opponent's Character for -2000 power")
    return True


# --- OP07-006: Sterry ---
@register_effect("OP07-006", "on_play", "[On Play] Give Leader -5000: Draw 1, trash 1")
def op07_006_sterry(game_state, player, card):
    """On Play: Give active Leader -5000 to draw 1 and trash 1."""
    if player.leader and not getattr(player.leader, 'is_resting', False):
        player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) - 5000
        draw_cards(player, 1)
        if player.hand:
            trash_from_hand(player, 1, game_state, card)
    return True


# --- OP07-007: Dice ---
# No effect (vanilla 6000 power)


# --- OP07-008: Mr. Tanaka ---
@register_effect("OP07-008", "blocker", "[Blocker]")
def op07_008_tanaka_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP07-008", "trigger", "[Trigger] Play this card")
def op07_008_tanaka_trigger(game_state, player, card):
    """Trigger: Play this card."""
    player.cards_in_play.append(card)
    return True


# --- OP07-009: Dogura & Magura ---
@register_effect("OP07-009", "on_play", "[On Play] Give red cost 1 Character Double Attack")
def op07_009_dogura_magura(game_state, player, card):
    """On Play: Give red cost 1 Character Double Attack."""
    targets = [c for c in player.cards_in_play if 'Red' in getattr(c, 'colors', '') and (getattr(c, 'cost', 0) or 0) == 1]
    if targets:
        return create_double_attack_choice(game_state, player, targets, source_card=card,
                                          prompt="Choose your red cost 1 Character to give Double Attack")
    return True


# --- OP07-010: Baccarat ---
@register_effect("OP07-010", "blocker", "[Blocker]")
def op07_010_baccarat_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP07-010", "on_opponent_attack", "[On Opponent's Attack] [Once Per Turn] Trash 1: +2000 power")
def op07_010_baccarat_attack(game_state, player, card):
    """On Opponent's Attack: Trash 1 for +2000 power."""
    if getattr(card, 'op07_010_used', False):
        return False
    if player.hand:
        trash_from_hand(player, 1, game_state, card)
        if player.leader:
            player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 2000
        card.op07_010_used = True
        return True
    return False


# --- OP07-011: Bluejam ---
@register_effect("OP07-011", "on_attack", "[DON!! x1] [When Attacking] K.O. opponent's 2000 power or less")
def op07_011_bluejam(game_state, player, card):
    """When Attacking: With DON, K.O. opponent's 2000 power or less."""
    if getattr(card, 'attached_don', 0) >= 1:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'power', 0) or 0) + (getattr(c, 'power_modifier', 0) or 0) <= 2000]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's 2000 power or less to K.O.")
    return True


# --- OP07-012: Porchemy ---
@register_effect("OP07-012", "on_play", "[On Play] Give -1000 power to opponent's Character")
def op07_012_porchemy(game_state, player, card):
    """On Play: Give -1000 power to opponent's Character."""
    opponent = get_opponent(game_state, player)
    if opponent.cards_in_play:
        return create_power_reduction_choice(game_state, player, list(opponent.cards_in_play), 1000,
                                            source_card=card, prompt="Choose opponent's Character for -1000 power")
    return True


# --- OP07-013: Masked Deuce ---
@register_effect("OP07-013", "on_play", "[On Play] If Ace leader, look at 5, add Ace or red Event")
def op07_013_masked_deuce(game_state, player, card):
    """On Play: If Ace leader, look at 5 and add Ace or red Event."""
    if player.leader and getattr(player.leader, 'name', '') == 'Portgas.D.Ace':
        looked = player.deck[:5] if len(player.deck) >= 5 else player.deck[:]
        for c in looked:
            name = getattr(c, 'name', '')
            card_type = getattr(c, 'card_type', '')
            colors = getattr(c, 'colors', '')
            if name == 'Portgas.D.Ace' or (card_type == 'EVENT' and 'Red' in colors):
                player.deck.remove(c)
                player.hand.append(c)
                break
    return True


# --- OP07-014: Moda ---
@register_effect("OP07-014", "on_play", "[On Play] Give Ace +2000 power")
def op07_014_moda(game_state, player, card):
    """On Play: Give Ace +2000 power."""
    for c in player.cards_in_play:
        if getattr(c, 'name', '') == 'Portgas.D.Ace':
            c.power_modifier = getattr(c, 'power_modifier', 0) + 2000
            break
    if player.leader and getattr(player.leader, 'name', '') == 'Portgas.D.Ace':
        player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 2000
    return True


# --- OP07-015: Monkey.D.Dragon ---
@register_effect("OP07-015", "continuous", "[Rush]")
def op07_015_dragon_rush(game_state, player, card):
    """Rush."""
    card.has_rush = True
    return True


@register_effect("OP07-015", "on_play", "[On Play] Give up to 2 rested DON to Leader or Character")
def op07_015_dragon_play(game_state, player, card):
    """On Play: Give up to 2 rested DON to Leader or Character."""
    rested_don = player.don_pool.count("rested")
    if rested_don:
        targets = list(player.cards_in_play)
        if player.leader:
            targets = [player.leader] + targets
        if targets:
            don_count = min(2, len(rested_don))
            return create_don_attachment_choice(game_state, player, targets, don_count,
                                               source_card=card, prompt=f"Choose target for up to {don_count} rested DON")
    return True


# --- OP07-020: Aladine ---
@register_effect("OP07-020", "blocker", "[Blocker]")
def op07_020_aladine_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP07-020", "on_ko", "[On K.O.] If Fish-Man leader, play Fish-Man/Merfolk cost 3 or less from hand")
def op07_020_aladine_ko(game_state, player, card):
    """On K.O.: If Fish-Man leader, play Fish-Man/Merfolk cost 3 or less from hand."""
    if player.leader and 'Fish-Man' in (player.leader.card_origin or ''):
        targets = [c for c in player.hand if ('Fish-Man' in (c.card_origin or '') or 'Merfolk' in (c.card_origin or '')) and (getattr(c, 'cost', 0) or 0) <= 3]
        if targets:
            return create_play_from_hand_choice(game_state, player, targets, source_card=card,
                                               prompt="Choose Fish-Man/Merfolk cost 3 or less to play from hand")
    return True


# --- OP07-021: Urouge ---
@register_effect("OP07-021", "blocker", "[Blocker]")
def op07_021_urouge_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP07-021", "end_of_turn", "[End of Your Turn] Set DON active")
def op07_021_urouge_end(game_state, player, card):
    """End of Turn: Set DON active."""
    for don in player.don_pool:
        if getattr(don, 'is_resting', False):
            don.is_resting = False
            break
    return True


# --- OP07-022: Otama ---
@register_effect("OP07-022", "on_play", "[On Play] Look at 5, add green Land of Wano")
def op07_022_otama(game_state, player, card):
    """On Play: Look at 5, reveal up to 1 green Land of Wano card to hand, rest to bottom."""
    def is_green_land_of_wano(c):
        colors = getattr(c, 'colors', '') or getattr(c, 'color', '') or ''
        types = (c.card_origin or '')
        name = getattr(c, 'name', '')
        return ('Green' in colors or 'green' in colors.lower()) and 'Land of Wano' in types and name != 'Otama'

    return search_top_cards(
        game_state, player,
        look_count=5,
        add_count=1,
        filter_fn=is_green_land_of_wano,
        source_card=card,
        prompt="Look at top 5 cards. Choose up to 1 green Land of Wano card to add to hand."
    )


# --- OP07-023: Caribou ---
@register_effect("OP07-023", "continuous", "If 6+ rested DON, +1000 power")
def op07_023_caribou_power(game_state, player, card):
    """Continuous: If 6+ rested DON, +1000 power."""
    rested = sum(1 for d in player.don_pool if getattr(d, 'is_resting', False))
    if rested >= 6:
        card.power_modifier = getattr(card, 'power_modifier', 0) + 1000
    return True


@register_effect("OP07-023", "blocker", "[Blocker]")
def op07_023_caribou_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


# --- OP07-024: Koala ---
@register_effect("OP07-024", "on_opponent_attack", "[On Opponent's Attack] Rest this: Fish-Man cost 5 or less gains Blocker")
def op07_024_koala(game_state, player, card):
    """On Opponent's Attack: Rest this to give Fish-Man cost 5 or less Blocker."""
    if not getattr(card, 'is_resting', False):
        card.is_resting = True
        targets = [c for c in player.cards_in_play if 'Fish-Man' in (c.card_origin or '') and (getattr(c, 'cost', 0) or 0) <= 5]
        if targets:
            return create_grant_blocker_choice(game_state, player, targets, source_card=card,
                                              prompt="Choose Fish-Man cost 5 or less to give Blocker")
    return True


# --- OP07-025: Coribou ---
@register_effect("OP07-025", "on_play", "[On Play] Play Caribou cost 4 or less from hand rested")
def op07_025_coribou(game_state, player, card):
    """On Play: Play Caribou cost 4 or less from hand rested."""
    for c in list(player.hand):
        if getattr(c, 'name', '') == 'Caribou' and (getattr(c, 'cost', 0) or 0) <= 4:
            player.hand.remove(c)
            c.is_resting = True
            player.cards_in_play.append(c)
            break
    return True


# --- OP07-026: Jewelry Bonney ---
@register_effect("OP07-026", "on_play", "[On Play] Opponent's rested card won't become active next Refresh")
def op07_026_bonney(game_state, player, card):
    """On Play: Opponent's rested card won't become active next Refresh."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play + opponent.don_pool if getattr(c, 'is_resting', False)]
    if targets:
        return create_skip_refresh_choice(game_state, player, targets, source_card=card,
                                         prompt="Choose opponent's rested card to prevent refresh")
    return True


# --- OP07-027: Jinbe ---
# No effect (vanilla 6000 power)


# --- OP07-028: Scratchmen Apoo ---
# No effect (vanilla 8000 power)


# --- OP07-029: Basil Hawkins ---
@register_effect("OP07-029", "continuous", "If Supernovas leader, gains Blocker")
def op07_029_hawkins_blocker(game_state, player, card):
    """Continuous: If Supernovas leader, gains Blocker."""
    if player.leader and 'Supernovas' in (player.leader.card_origin or ''):
        card.has_blocker = True
    return True


@register_effect("OP07-029", "on_leave_prevention", "[Once Per Turn] When removed by effect, rest opponent's Character instead")
def op07_029_hawkins_prevention(game_state, player, card):
    """Once per turn: When removed by effect, rest opponent's Character instead."""
    if not getattr(card, 'op07_029_used', False):
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if not getattr(c, 'is_resting', False)]
        if targets:
            card.op07_029_used = True
            return create_rest_choice(game_state, player, targets, source_card=card,
                                     prompt="Choose opponent's Character to rest instead")
    return False


# --- OP07-030: Pappag ---
@register_effect("OP07-030", "continuous", "If have Camie, gains Blocker")
def op07_030_pappag(game_state, player, card):
    """Continuous: If have Camie, gains Blocker."""
    for c in player.cards_in_play:
        if getattr(c, 'name', '') == 'Camie':
            card.has_blocker = True
            break
    return True


# --- OP07-031: Bartolomeo ---
@register_effect("OP07-031", "blocker", "[Blocker]")
def op07_031_bartolomeo_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP07-031", "continuous", "[Your Turn] [Once Per Turn] When Character rested by effect, draw 1, trash 1")
def op07_031_bartolomeo_draw(game_state, player, card):
    """Continuous: When Character rested by effect, draw 1 and trash 1."""
    card.bartolomeo_effect = True
    return True


# --- OP07-032: Fisher Tiger ---
@register_effect("OP07-032", "continuous", "Can attack Characters on play turn")
def op07_032_fisher_tiger_rush(game_state, player, card):
    """Continuous: Can attack Characters on play turn."""
    card.can_attack_characters_on_play = True
    return True


@register_effect("OP07-032", "on_play", "[On Play] If Fish-Man/Merfolk leader, rest opponent's cost 6 or less")
def op07_032_fisher_tiger_play(game_state, player, card):
    """On Play: If Fish-Man/Merfolk leader, rest opponent's cost 6 or less."""
    leader_types = (player.leader.card_origin or '') if player.leader else ''
    if 'Fish-Man' in leader_types or 'Merfolk' in leader_types:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 6]
        if targets:
            return create_rest_choice(game_state, player, targets, source_card=card,
                                     prompt="Choose opponent's cost 6 or less to rest")
    return True


# --- OP07-033: Monkey.D.Luffy ---
@register_effect("OP07-033", "continuous", "If 3+ Characters, cost 3 or less cannot be K.O.'d by effects")
def op07_033_luffy(game_state, player, card):
    """Continuous: If 3+ Characters, cost 3 or less cannot be K.O.'d by effects."""
    if len(player.cards_in_play) >= 3:
        for c in player.cards_in_play:
            if (getattr(c, 'cost', 0) or 0) <= 3 and getattr(c, 'name', '') != 'Monkey.D.Luffy':
                c.cannot_be_ko_by_effects = True
    return True


# --- OP07-034: Roronoa Zoro ---
@register_effect("OP07-034", "on_attack", "[When Attacking] If 3+ Characters, +2000 power")
def op07_034_zoro(game_state, player, card):
    """When Attacking: If 3+ Characters, +2000 power."""
    if len(player.cards_in_play) >= 3:
        card.power_modifier = getattr(card, 'power_modifier', 0) + 2000
    return True


# --- OP07-039: Edward Weevil ---
@register_effect("OP07-039", "on_attack", "[DON!! x1] [When Attacking] Look at 3 cards, reorder top/bottom")
def op07_039_weevil(game_state, player, card):
    """When Attacking: With DON, look at 3 cards and reorder."""
    if getattr(card, 'attached_don', 0) >= 1:
        # Just keep cards in current order for simplicity
        pass
    return True


# --- OP07-040: Crocodile ---
@register_effect("OP07-040", "on_play", "[On Play] Rest 1 DON: Return cost 2 or less to hand")
def op07_040_crocodile(game_state, player, card):
    """On Play: Rest 1 DON to return cost 2 or less to hand."""
    for don in player.don_pool:
        if not getattr(don, 'is_resting', False):
            don.is_resting = True
            opponent = get_opponent(game_state, player)
            targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
            if targets:
                return create_return_to_hand_choice(game_state, player, targets, source_card=card,
                                                   prompt="Choose opponent's cost 2 or less to return to hand")
            break
    return True


# --- OP07-041: Gloriosa ---
@register_effect("OP07-041", "on_play", "[On Play] Look at 5, add Amazon Lily or Kuja Pirates")
def op07_041_gloriosa(game_state, player, card):
    """On Play: Look at 5 and add Amazon Lily or Kuja Pirates."""
    looked = player.deck[:5] if len(player.deck) >= 5 else player.deck[:]
    for c in looked:
        types = (c.card_origin or '')
        name = getattr(c, 'name', '')
        if ('Amazon Lily' in types or 'Kuja Pirates' in types) and 'Gloriosa' not in name:
            player.deck.remove(c)
            player.hand.append(c)
            break
    return True


# --- OP07-042: Gecko Moria ---
@register_effect("OP07-042", "on_leave_prevention", "[Once Per Turn] When removed by effect, bottom another Character instead")
def op07_042_gecko_moria(game_state, player, card):
    """Once per turn: When removed by effect, bottom another Character instead."""
    if not getattr(card, 'op07_042_used', False):
        if player.leader and 'The Seven Warlords of the Sea' in (player.leader.card_origin or ''):
            targets = [c for c in player.cards_in_play if c != card and getattr(c, 'name', '') != 'Gecko Moria']
            if targets:
                card.op07_042_used = True
                return create_bottom_deck_own_choice(game_state, player, targets, source_card=card,
                                                    prompt="Choose your Character to place at deck bottom instead")
    return False


# --- OP07-043: Salome ---
@register_effect("OP07-043", "on_play", "[On Play] Give Boa Hancock +2000 power")
def op07_043_salome(game_state, player, card):
    """On Play: Give Boa Hancock +2000 power."""
    for c in player.cards_in_play:
        if getattr(c, 'name', '') == 'Boa Hancock':
            c.power_modifier = getattr(c, 'power_modifier', 0) + 2000
            break
    if player.leader and getattr(player.leader, 'name', '') == 'Boa Hancock':
        player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 2000
    return True


# --- OP07-044: Dracule Mihawk ---
@register_effect("OP07-044", "on_play", "[On Play] Draw 1 card")
def op07_044_mihawk(game_state, player, card):
    """On Play: Draw 1 card."""
    draw_cards(player, 1)
    return True


# --- OP07-045: Jinbe ---
@register_effect("OP07-045", "on_play", "[On Play] Play Seven Warlords cost 4 or less from hand")
def op07_045_jinbe(game_state, player, card):
    """On Play: Play Seven Warlords cost 4 or less from hand."""
    targets = [c for c in player.hand if 'The Seven Warlords of the Sea' in (c.card_origin or '') and (getattr(c, 'cost', 0) or 0) <= 4 and getattr(c, 'name', '') != 'Jinbe']
    if targets:
        return create_play_from_hand_choice(game_state, player, targets, source_card=card,
                                           prompt="Choose Seven Warlords cost 4 or less to play from hand")
    return True


# --- OP07-046: Sengoku ---
@register_effect("OP07-046", "on_play", "[On Play] Look at 5, add Seven Warlords")
def op07_046_sengoku(game_state, player, card):
    """On Play: Look at 5 and add Seven Warlords."""
    looked = player.deck[:5] if len(player.deck) >= 5 else player.deck[:]
    for c in looked:
        if 'The Seven Warlords of the Sea' in (c.card_origin or ''):
            player.deck.remove(c)
            player.hand.append(c)
            break
    return True


# --- OP07-047: Trafalgar Law ---
@register_effect("OP07-047", "activate", "[Activate: Main] Return to hand: If opponent has 6+ cards, they bottom 1")
def op07_047_law(game_state, player, card):
    """Activate: Return to hand, if opponent has 6+ cards they bottom 1."""
    if card in player.cards_in_play:
        player.cards_in_play.remove(card)
        player.hand.append(card)
        opponent = get_opponent(game_state, player)
        if len(opponent.hand) >= 6 and opponent.hand:
            bottom_card = opponent.hand.pop()
            opponent.deck.append(bottom_card)
        return True
    return False


# --- OP07-048: Donquixote Doflamingo ---
@register_effect("OP07-048", "activate", "[Activate: Main] [Once Per Turn] Rest 2 DON: Play Warlords cost 4 from deck rested")
def op07_048_doflamingo(game_state, player, card):
    """Activate: Rest 2 DON to play Warlords cost 4 or less from deck rested."""
    if getattr(card, 'op07_048_used', False):
        return False
    active_don = player.don_pool.count("active")
    if len(active_don) >= 2:
        active_don[0].is_resting = True
        active_don[1].is_resting = True
        if player.deck:
            revealed = player.deck.pop(0)
            if 'The Seven Warlords of the Sea' in (revealed.card_origin or ''):
                if (getattr(revealed, 'cost', 0) or 0) <= 4:
                    revealed.is_resting = True
                    player.cards_in_play.append(revealed)
                else:
                    player.deck.append(revealed)
            else:
                player.deck.append(revealed)
        card.op07_048_used = True
        return True
    return False


# --- OP07-049: Buckin ---
@register_effect("OP07-049", "on_play", "[On Play] Play Edward Weevil cost 4 or less from hand rested")
def op07_049_buckin(game_state, player, card):
    """On Play: Play Edward Weevil cost 4 or less from hand rested."""
    for c in list(player.hand):
        if getattr(c, 'name', '') == 'Edward Weevil' and (getattr(c, 'cost', 0) or 0) <= 4:
            player.hand.remove(c)
            c.is_resting = True
            player.cards_in_play.append(c)
            break
    return True


# --- OP07-050: Boa Sandersonia ---
@register_effect("OP07-050", "on_play", "[On Play] If 2+ Amazon Lily/Kuja, return cost 3 or less to hand")
def op07_050_sandersonia(game_state, player, card):
    """On Play: If 2+ Amazon Lily/Kuja, return cost 3 or less to hand."""
    count = sum(1 for c in player.cards_in_play
                if 'Amazon Lily' in (c.card_origin or '') or 'Kuja Pirates' in (c.card_origin or ''))
    if count >= 2:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
        if targets:
            return create_return_to_hand_choice(game_state, player, targets, source_card=card,
                                               prompt="Choose opponent's cost 3 or less to return to hand")
    return True


# --- OP07-051: Boa Hancock ---
@register_effect("OP07-051", "on_play", "[On Play] Character can't attack next turn, bottom cost 1 or less")
def op07_051_hancock(game_state, player, card):
    """On Play: Character can't attack next turn, bottom cost 1 or less."""
    opponent = get_opponent(game_state, player)
    cannot_attack_targets = [c for c in opponent.cards_in_play if getattr(c, 'name', '') != 'Monkey.D.Luffy']
    bottom_targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 1]
    if cannot_attack_targets or bottom_targets:
        return create_hancock_dual_choice(game_state, player, cannot_attack_targets, bottom_targets, source_card=card,
                                         prompt="Choose targets for Boa Hancock's effects")
    return True


# --- OP07-052: Boa Marigold ---
@register_effect("OP07-052", "on_play", "[On Play] If 2+ Amazon Lily/Kuja, bottom cost 2 or less")
def op07_052_marigold(game_state, player, card):
    """On Play: If 2+ Amazon Lily/Kuja, bottom cost 2 or less."""
    count = sum(1 for c in player.cards_in_play
                if 'Amazon Lily' in (c.card_origin or '') or 'Kuja Pirates' in (c.card_origin or ''))
    if count >= 2:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
        if targets:
            return create_bottom_deck_choice(game_state, player, targets, source_card=card,
                                            prompt="Choose opponent's cost 2 or less to place at deck bottom")
    return True


# --- OP07-053: Portgas.D.Ace ---
@register_effect("OP07-053", "blocker", "[Blocker]")
def op07_053_ace_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP07-053", "on_play", "[On Play] Draw 2, place 2 at top/bottom")
def op07_053_ace_play(game_state, player, card):
    """On Play: Draw 2, place 2 at top/bottom."""
    draw_cards(player, 2)
    for _ in range(min(2, len(player.hand))):
        if player.hand:
            c = player.hand.pop()
            player.deck.append(c)
    return True


# --- OP07-054: Marguerite ---
@register_effect("OP07-054", "blocker", "[Blocker]")
def op07_054_marguerite_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP07-054", "on_play", "[On Play] Draw 1 card")
def op07_054_marguerite_play(game_state, player, card):
    """On Play: Draw 1 card."""
    draw_cards(player, 1)
    return True


# --- OP07-060: Itomimizu ---
@register_effect("OP07-060", "activate", "[Activate: Main] [Once Per Turn] If Foxy leader and no other Itomimizu, add DON rested")
def op07_060_itomimizu(game_state, player, card):
    """Activate: If Foxy leader and no other Itomimizu, add DON rested."""
    if getattr(card, 'op07_060_used', False):
        return False
    if player.leader and 'Foxy Pirates' in (player.leader.card_origin or ''):
        other_itomimizu = sum(1 for c in player.cards_in_play if getattr(c, 'name', '') == 'Itomimizu' and c != card)
        if other_itomimizu == 0 and player.don_deck:
            don = player.don_deck.pop()
            don.is_resting = True
            player.don_pool.append(don)
            card.op07_060_used = True
            return True
    return False


# --- OP07-061: Vinsmoke Sanji ---
@register_effect("OP07-061", "on_play", "[On Play] DON -1: If Vinsmoke leader, draw 1")
def op07_061_sanji(game_state, player, card):
    """On Play: DON -1 to draw 1 if Vinsmoke leader."""
    if player.don_pool and player.leader and 'The Vinsmoke Family' in (player.leader.card_origin or ''):
        don = player.don_pool.pop()
        player.don_deck.append(don)
        draw_cards(player, 1)
        return True
    return False


# --- OP07-062: Vinsmoke Reiju ---
@register_effect("OP07-062", "on_play", "[On Play] If DON <= opponent, return Vinsmoke cost 1 to hand")
def op07_062_reiju(game_state, player, card):
    """On Play: If DON <= opponent, return Vinsmoke cost 1 to hand."""
    opponent = get_opponent(game_state, player)
    if len(player.don_pool) <= len(opponent.don_pool):
        for c in list(player.cards_in_play):
            if 'The Vinsmoke Family' in (c.card_origin or '') and (getattr(c, 'cost', 0) or 0) == 1:
                player.cards_in_play.remove(c)
                player.hand.append(c)
                break
    return True


# --- OP07-063: Capote ---
@register_effect("OP07-063", "on_play", "[On Play] DON -1: If Foxy leader, cost 6 or less cannot attack next turn")
def op07_063_capote(game_state, player, card):
    """On Play: DON -1, if Foxy leader opponent's cost 6 or less cannot attack next turn."""
    if player.don_pool and player.leader and 'Foxy Pirates' in (player.leader.card_origin or ''):
        don = player.don_pool.pop()
        player.don_deck.append(don)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 6]
        if targets:
            return create_cannot_attack_choice(game_state, player, targets, source_card=card,
                                              prompt="Choose opponent's cost 6 or less - cannot attack next turn")
        return True
    return False


# --- OP07-064: Sanji ---
@register_effect("OP07-064", "continuous", "If DON 2+ less than opponent, -3 cost in hand")
def op07_064_sanji_cost(game_state, player, card):
    """Continuous: If DON 2+ less than opponent, -3 cost in hand."""
    opponent = get_opponent(game_state, player)
    if len(player.don_pool) <= len(opponent.don_pool) - 2:
        card.cost_modifier = getattr(card, 'cost_modifier', 0) - 3
    return True


@register_effect("OP07-064", "blocker", "[Blocker]")
def op07_064_sanji_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


# --- OP07-065: Gina ---
@register_effect("OP07-065", "on_play", "[On Play] If Foxy leader and DON <= opponent, add DON active")
def op07_065_gina(game_state, player, card):
    """On Play: If Foxy leader and DON <= opponent, add DON active."""
    opponent = get_opponent(game_state, player)
    if player.leader and 'Foxy Pirates' in (player.leader.card_origin or ''):
        if len(player.don_pool) <= len(opponent.don_pool) and player.don_deck:
            don = player.don_deck.pop()
            don.is_resting = False
            player.don_pool.append(don)
    return True


# --- OP07-066: Tony Tony.Chopper ---
@register_effect("OP07-066", "blocker", "[Blocker]")
def op07_066_chopper_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP07-066", "on_play", "[On Play] If DON <= opponent, add DON rested")
def op07_066_chopper_play(game_state, player, card):
    """On Play: If DON <= opponent, add DON rested."""
    opponent = get_opponent(game_state, player)
    if len(player.don_pool) <= len(opponent.don_pool) and player.don_deck:
        don = player.don_deck.pop()
        don.is_resting = True
        player.don_pool.append(don)
    return True


# --- OP07-067: Tonjit ---
# No effect (vanilla 3000 power)


# --- OP07-068: Hamburg ---
@register_effect("OP07-068", "on_attack", "[DON!! x1] [When Attacking] If DON <= opponent, add DON rested")
def op07_068_hamburg(game_state, player, card):
    """When Attacking: With DON, if DON <= opponent, add DON rested."""
    if getattr(card, 'attached_don', 0) >= 1:
        opponent = get_opponent(game_state, player)
        if len(player.don_pool) <= len(opponent.don_pool) and player.don_deck:
            don = player.don_deck.pop()
            don.is_resting = True
            player.don_pool.append(don)
    return True


# --- OP07-069: Pickles ---
@register_effect("OP07-069", "continuous", "If DON <= opponent, Foxy Pirates cannot be K.O.'d by effects")
def op07_069_pickles(game_state, player, card):
    """Continuous: If DON <= opponent, Foxy Pirates cannot be K.O.'d by effects."""
    opponent = get_opponent(game_state, player)
    if len(player.don_pool) <= len(opponent.don_pool):
        for c in player.cards_in_play:
            if 'Foxy Pirates' in (c.card_origin or '') and getattr(c, 'name', '') != 'Pickles':
                c.cannot_be_ko_by_effects = True
    return True


# --- OP07-070: Big Bun ---
@register_effect("OP07-070", "on_play", "[On Play] If DON <= opponent, play Foxy Pirates cost 4 or less from hand")
def op07_070_big_bun(game_state, player, card):
    """On Play: If DON <= opponent, play Foxy Pirates cost 4 or less from hand."""
    opponent = get_opponent(game_state, player)
    if len(player.don_pool) <= len(opponent.don_pool):
        targets = [c for c in player.hand if 'Foxy Pirates' in (c.card_origin or '') and (getattr(c, 'cost', 0) or 0) <= 4]
        if targets:
            return create_play_from_hand_choice(game_state, player, targets, source_card=card,
                                               prompt="Choose Foxy Pirates cost 4 or less to play from hand")
    return True


# --- OP07-071: Foxy ---
@register_effect("OP07-071", "continuous", "[Opponent's Turn] If Foxy leader, all opponent's Characters -1000")
def op07_071_foxy_debuff(game_state, player, card):
    """Continuous: On Opponent's Turn, all opponent's Characters -1000."""
    if player.leader and 'Foxy Pirates' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        for c in opponent.cards_in_play:
            c.power_modifier = getattr(c, 'power_modifier', 0) - 1000
    return True


@register_effect("OP07-071", "activate", "[Activate: Main] [Once Per Turn] Add DON rested")
def op07_071_foxy_activate(game_state, player, card):
    """Activate: Add DON rested."""
    if getattr(card, 'op07_071_used', False):
        return False
    if player.don_deck:
        don = player.don_deck.pop()
        don.is_resting = True
        player.don_pool.append(don)
        card.op07_071_used = True
        return True
    return False


# --- OP07-072: Porche ---
@register_effect("OP07-072", "on_play", "[On Play] DON -1: Look at 5, add Foxy Pirates, play purple 4000 power")
def op07_072_porche(game_state, player, card):
    """On Play: DON -1 to look at 5, add Foxy Pirates, play purple 4000 power."""
    if player.don_pool:
        don = player.don_pool.pop()
        player.don_deck.append(don)
        looked = player.deck[:5] if len(player.deck) >= 5 else player.deck[:]
        for c in looked:
            if 'Foxy Pirates' in (c.card_origin or ''):
                player.deck.remove(c)
                player.hand.append(c)
                break
        # Play purple 4000 power from hand
        for c in list(player.hand):
            colors = getattr(c, 'colors', '')
            power = getattr(c, 'power', 0) or 0
            if 'Purple' in colors and power <= 4000:
                player.hand.remove(c)
                player.cards_in_play.append(c)
                break
        return True
    return False


# --- OP07-073: Monkey.D.Luffy ---
@register_effect("OP07-073", "activate", "[Activate: Main] [Once Per Turn] DON -3: If opponent has 3+ Characters, set active")
def op07_073_luffy(game_state, player, card):
    """Activate: DON -3 to set active if opponent has 3+ Characters."""
    if getattr(card, 'op07_073_used', False):
        return False
    if len(player.don_pool) >= 3:
        opponent = get_opponent(game_state, player)
        if len(opponent.cards_in_play) >= 3:
            for _ in range(3):
                don = player.don_pool.pop()
                player.don_deck.append(don)
            card.is_resting = False
            card.op07_073_used = True
            return True
    return False


# --- OP07-074: Monda ---
@register_effect("OP07-074", "activate", "[Activate: Main] Trash this: If Foxy leader, add DON rested")
def op07_074_monda(game_state, player, card):
    """Activate: Trash this to add DON rested if Foxy leader."""
    if player.leader and 'Foxy Pirates' in (player.leader.card_origin or ''):
        if card in player.cards_in_play:
            player.cards_in_play.remove(card)
            player.trash.append(card)
            if player.don_deck:
                don = player.don_deck.pop()
                don.is_resting = True
                player.don_pool.append(don)
            return True
    return False


# --- OP07-080: Kaku ---
@register_effect("OP07-080", "on_play", "[On Play] Bottom 2 CP from trash: Give opponent -3 cost")
def op07_080_kaku(game_state, player, card):
    """On Play: Bottom 2 CP from trash to give opponent -3 cost."""
    cp_cards = [c for c in player.trash if 'CP' in (c.card_origin or '')]
    if len(cp_cards) >= 2:
        for c in cp_cards[:2]:
            player.trash.remove(c)
            player.deck.append(c)
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            opponent.cards_in_play[0].cost_modifier = getattr(opponent.cards_in_play[0], 'cost_modifier', 0) - 3
    return True


# --- OP07-081: Kalifa ---
@register_effect("OP07-081", "continuous", "[DON!! x1] [Your Turn] All opponent's Characters -1 cost")
def op07_081_kalifa(game_state, player, card):
    """Continuous: With DON, all opponent's Characters -1 cost."""
    if getattr(card, 'attached_don', 0) >= 1:
        opponent = get_opponent(game_state, player)
        for c in opponent.cards_in_play:
            c.cost_modifier = getattr(c, 'cost_modifier', 0) - 1
    return True


# --- OP07-082: Captain John ---
@register_effect("OP07-082", "on_play", "[On Play] Trash 2 from deck, give opponent -1 cost")
def op07_082_captain_john(game_state, player, card):
    """On Play: Trash 2 from deck and give opponent -1 cost."""
    for _ in range(min(2, len(player.deck))):
        c = player.deck.pop(0)
        player.trash.append(c)
    opponent = get_opponent(game_state, player)
    if opponent.cards_in_play:
        opponent.cards_in_play[0].cost_modifier = getattr(opponent.cards_in_play[0], 'cost_modifier', 0) - 1
    return True


# --- OP07-083: Gecko Moria ---
@register_effect("OP07-083", "activate", "[Activate: Main] Bottom 4 Thriller Bark: Gain Banish and +1000")
def op07_083_gecko_moria(game_state, player, card):
    """Activate: Bottom 4 Thriller Bark to gain Banish and +1000."""
    tb_cards = [c for c in player.trash if 'Thriller Bark Pirates' in (c.card_origin or '')]
    if len(tb_cards) >= 4:
        for c in tb_cards[:4]:
            player.trash.remove(c)
            player.deck.append(c)
        card.has_banish = True
        card.power_modifier = getattr(card, 'power_modifier', 0) + 1000
        return True
    return False


# --- OP07-084: Gismonda ---
@register_effect("OP07-084", "blocker", "[Blocker]")
def op07_084_gismonda(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


# --- OP07-085: Stussy ---
@register_effect("OP07-085", "on_play", "[On Play] Trash 1 Character: K.O. opponent's Character")
def op07_085_stussy(game_state, player, card):
    """On Play: Trash 1 Character to K.O. opponent's Character."""
    other_chars = [c for c in player.cards_in_play if c != card]
    if other_chars:
        target = other_chars[0]
        player.cards_in_play.remove(target)
        player.trash.append(target)
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            opp_target = opponent.cards_in_play[0]
            opponent.cards_in_play.remove(opp_target)
            opponent.trash.append(opp_target)
    return True


# --- OP07-086: Spandam ---
@register_effect("OP07-086", "on_play", "[On Play] Trash 2 from deck, give opponent -2 cost")
def op07_086_spandam(game_state, player, card):
    """On Play: Trash 2 from deck and give opponent -2 cost."""
    for _ in range(min(2, len(player.deck))):
        c = player.deck.pop(0)
        player.trash.append(c)
    opponent = get_opponent(game_state, player)
    if opponent.cards_in_play:
        opponent.cards_in_play[0].cost_modifier = getattr(opponent.cards_in_play[0], 'cost_modifier', 0) - 2
    return True


# --- OP07-087: Baskerville ---
@register_effect("OP07-087", "continuous", "[Your Turn] If opponent has cost 0 Character, +3000 power")
def op07_087_baskerville(game_state, player, card):
    """Continuous: If opponent has cost 0 Character, +3000 power."""
    opponent = get_opponent(game_state, player)
    has_cost_0 = any((getattr(c, 'cost', 0) or 0) + (getattr(c, 'cost_modifier', 0) or 0) == 0
                     for c in opponent.cards_in_play)
    if has_cost_0:
        card.power_modifier = getattr(card, 'power_modifier', 0) + 3000
    return True


# --- OP07-088: Hattori ---
@register_effect("OP07-088", "on_play", "[On Play] Give Rob Lucci +2000 power")
def op07_088_hattori(game_state, player, card):
    """On Play: Give Rob Lucci +2000 power."""
    for c in player.cards_in_play:
        if getattr(c, 'name', '') == 'Rob Lucci':
            c.power_modifier = getattr(c, 'power_modifier', 0) + 2000
            break
    if player.leader and getattr(player.leader, 'name', '') == 'Rob Lucci':
        player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 2000
    return True


# --- OP07-089: Maha ---
# No effect (vanilla 8000 power)


# --- OP07-090: Morgans ---
@register_effect("OP07-090", "on_play", "[On Play] Opponent trashes 1, then draws 1")
def op07_090_morgans(game_state, player, card):
    """On Play: Opponent trashes 1 from hand, then draws 1."""
    opponent = get_opponent(game_state, player)
    if opponent.hand:
        trash_from_hand(opponent, 1)
    draw_cards(opponent, 1)
    return True


# --- OP07-091: Monkey.D.Luffy ---
@register_effect("OP07-091", "on_attack", "[When Attacking] Trash opponent's cost 2 or less, bottom cost 4+ from trash for +1000 per 3")
def op07_091_luffy(game_state, player, card):
    """When Attacking: Trash opponent's cost 2 or less, bottom cost 4+ for +1000 per 3."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
    # Bottom cost 4+ cards from trash
    cost_4_plus = [c for c in player.trash if (getattr(c, 'cost', 0) or 0) >= 4]
    for c in cost_4_plus:
        player.trash.remove(c)
        player.deck.append(c)
    bonus = (len(cost_4_plus) // 3) * 1000
    card.power_modifier = getattr(card, 'power_modifier', 0) + bonus
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                               prompt="Choose opponent's cost 2 or less to trash")
    return True


# --- OP07-092: Joseph ---
@register_effect("OP07-092", "on_play", "[On Play] Bottom 2 CP from trash: K.O. cost 1 or less")
def op07_092_joseph(game_state, player, card):
    """On Play: Bottom 2 CP from trash to K.O. cost 1 or less."""
    cp_cards = [c for c in player.trash if 'CP' in (c.card_origin or '')]
    if len(cp_cards) >= 2:
        for c in cp_cards[:2]:
            player.trash.remove(c)
            player.deck.append(c)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 1]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's cost 1 or less to K.O.")
    return True


# --- OP07-093: Rob Lucci ---
@register_effect("OP07-093", "on_play", "[On Play] Bottom 3 from trash: Opponent trashes 1, bottom opponent's trash")
def op07_093_rob_lucci(game_state, player, card):
    """On Play: Bottom 3 from trash, opponent trashes 1, bottom their trash."""
    if len(player.trash) >= 3:
        for _ in range(3):
            c = player.trash.pop()
            player.deck.append(c)
        opponent = get_opponent(game_state, player)
        if opponent.hand:
            trash_from_hand(opponent, 1)
        if opponent.trash:
            c = opponent.trash.pop()
            opponent.deck.append(c)
    return True


# --- OP07-098: Atlas ---
@register_effect("OP07-098", "continuous", "If less life than opponent, cannot be K.O.'d in battle")
def op07_098_atlas(game_state, player, card):
    """Continuous: If less life than opponent, cannot be K.O.'d in battle."""
    opponent = get_opponent(game_state, player)
    if len(player.life_cards) < len(opponent.life_cards):
        card.cannot_be_ko_in_battle = True
    return True


# --- OP07-099: Usopp ---
@register_effect("OP07-099", "trigger", "[Trigger] +2000 power to Egghead until end of next turn")
def op07_099_usopp(game_state, player, card):
    """Trigger: +2000 power to Egghead Leader/Character."""
    if player.leader and 'Egghead' in (player.leader.card_origin or ''):
        player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 2000
    return True


# --- OP07-100: Edison ---
@register_effect("OP07-100", "on_play", "[On Play] If 2 or less life, draw 2, trash 2")
def op07_100_edison(game_state, player, card):
    """On Play: If 2 or less life, draw 2 and trash 2."""
    if len(player.life_cards) <= 2:
        draw_cards(player, 2)
        trash_from_hand(player, 2, game_state, card)
    return True


# --- OP07-101: Shaka ---
@register_effect("OP07-101", "blocker", "[Blocker]")
def op07_101_shaka(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


# --- OP07-102: Jinbe ---
@register_effect("OP07-102", "trigger", "[Trigger] Return opponent's cost 4 or less to hand, add this to hand")
def op07_102_jinbe(game_state, player, card):
    """Trigger: Return opponent's cost 4 or less to hand, add this to hand."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
    player.hand.append(card)
    if targets:
        return create_return_to_hand_choice(game_state, player, targets, source_card=card,
                                           prompt="Choose opponent's cost 4 or less to return to hand")
    return True


# --- OP07-103: Tony Tony.Chopper ---
@register_effect("OP07-103", "trigger", "[Trigger] Give Egghead Blocker, add this to hand")
def op07_103_chopper(game_state, player, card):
    """Trigger: Give Egghead Character Blocker, add this to hand."""
    targets = [c for c in player.cards_in_play if 'Egghead' in (c.card_origin or '')]
    player.hand.append(card)
    if targets:
        return create_grant_blocker_choice(game_state, player, targets, source_card=card,
                                          prompt="Choose your Egghead Character to give Blocker")
    return True


# --- OP07-104: Nico Robin ---
@register_effect("OP07-104", "trigger", "[Trigger] If Egghead leader, draw 2")
def op07_104_robin(game_state, player, card):
    """Trigger: If Egghead leader, draw 2."""
    if player.leader and 'Egghead' in (player.leader.card_origin or ''):
        draw_cards(player, 2)
    return True


# --- OP07-105: Pythagoras ---
@register_effect("OP07-105", "on_ko", "[On K.O.] If 2 or less life, play Egghead cost 4 or less from trash rested")
def op07_105_pythagoras(game_state, player, card):
    """On K.O.: If 2 or less life, play Egghead cost 4 or less from trash rested."""
    if len(player.life_cards) <= 2:
        targets = [c for c in player.trash if 'Egghead' in (c.card_origin or '') and (getattr(c, 'cost', 0) or 0) <= 4]
        if targets:
            return create_play_from_trash_rested_choice(game_state, player, targets, source_card=card,
                                                       prompt="Choose Egghead cost 4 or less to play from trash rested")
    return True


# --- OP07-106: Fuza ---
@register_effect("OP07-106", "on_attack", "[DON!! x1] [When Attacking] If 1 or less life, K.O. cost 3 or less")
def op07_106_fuza(game_state, player, card):
    """When Attacking: With DON, if 1 or less life, K.O. cost 3 or less."""
    if getattr(card, 'attached_don', 0) >= 1 and len(player.life_cards) <= 1:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's cost 3 or less to K.O.")
    return True


# --- OP07-107: Franky ---
@register_effect("OP07-107", "trigger", "[Trigger] Draw 1. If 1 or less life, play this card")
def op07_107_franky(game_state, player, card):
    """Trigger: Draw 1. If 1 or less life, play this card."""
    draw_cards(player, 1)
    if len(player.life_cards) <= 1:
        player.cards_in_play.append(card)
    return True


# --- OP07-108: Vega Force 01 ---
# No effect (vanilla 6000 power)


# --- OP07-109: Monkey.D.Luffy ---
@register_effect("OP07-109", "activate", "[Activate: Main] Trash this: If 2 or less life, K.O. cost 4 or less, draw 1")
def op07_109_luffy_activate(game_state, player, card):
    """Activate: Trash this to K.O. cost 4 or less and draw 1 if 2 or less life."""
    if len(player.life_cards) <= 2 and card in player.cards_in_play:
        player.cards_in_play.remove(card)
        player.trash.append(card)
        draw_cards(player, 1)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's cost 4 or less to K.O.")
        return True
    return False


@register_effect("OP07-109", "trigger", "[Trigger] K.O. opponent's cost 4 or less")
def op07_109_luffy_trigger(game_state, player, card):
    """Trigger: K.O. opponent's cost 4 or less."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                               prompt="Choose opponent's cost 4 or less to K.O.")
    return True


# --- OP07-110: York ---
@register_effect("OP07-110", "on_play", "[On Play] Add 1 life to hand: K.O. cost 2 or less")
def op07_110_york(game_state, player, card):
    """On Play: Add 1 life to hand to K.O. cost 2 or less."""
    if player.life_cards:
        life_card = player.life_cards.pop()
        player.hand.append(life_card)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's cost 2 or less to K.O.")
    return True


# --- OP07-111: Lilith ---
@register_effect("OP07-111", "on_play", "[On Play] Look at 5, add Egghead card")
def op07_111_lilith(game_state, player, card):
    """On Play: Look at 5 and add Egghead card."""
    looked = player.deck[:5] if len(player.deck) >= 5 else player.deck[:]
    for c in looked:
        if 'Egghead' in (c.card_origin or '') and getattr(c, 'name', '') != 'Lilith':
            player.deck.remove(c)
            player.hand.append(c)
            break
    return True


# --- OP07-112: Lucy ---
@register_effect("OP07-112", "on_attack", "[When Attacking] [Once Per Turn] Add life to hand: Rest cost 4 or less, if 1 or less life add to life")
def op07_112_lucy(game_state, player, card):
    """When Attacking: Add life to hand, rest cost 4 or less, if 1 or less life add to life."""
    if getattr(card, 'op07_112_used', False):
        return False
    if player.life_cards:
        life_card = player.life_cards.pop()
        player.hand.append(life_card)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
        if len(player.life_cards) <= 1 and player.deck:
            top_card = player.deck.pop(0)
            player.life_cards.append(top_card)
        card.op07_112_used = True
        if targets:
            return create_rest_choice(game_state, player, targets, source_card=card,
                                     prompt="Choose opponent's cost 4 or less to rest")
        return True
    return False


# --- OP07-113: Roronoa Zoro ---
@register_effect("OP07-113", "trigger", "[Trigger] If Egghead leader, rest opponent's Leader or Character")
def op07_113_zoro(game_state, player, card):
    """Trigger: If Egghead leader, rest opponent's Leader or Character."""
    if player.leader and 'Egghead' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        if opponent.leader:
            opponent.leader.is_resting = True
    return True


# --- OP07-118: Sabo (SEC) ---
@register_effect("OP07-118", "on_play", "[On Play] Trash 1: K.O. cost 5 or less and cost 3 or less")
def op07_118_sabo(game_state, player, card):
    """On Play: Trash 1 to K.O. cost 5 or less and cost 3 or less."""
    if player.hand:
        trash_from_hand(player, 1, game_state, card)
        opponent = get_opponent(game_state, player)
        targets5 = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 5]
        targets3 = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
        if targets5 or targets3:
            return create_dual_ko_choice(game_state, player, targets5, targets3, source_card=card,
                                        prompt="Choose targets for Sabo's K.O. effect (cost 5 or less AND cost 3 or less)")
    return True


# --- OP07-119: Portgas.D.Ace (SEC) ---
@register_effect("OP07-119", "on_play", "[On Play] Add top deck to life. If 2 or less life, gain Rush")
def op07_119_ace(game_state, player, card):
    """On Play: Add top deck to life. If 2 or less life, gain Rush."""
    if player.deck:
        top_card = player.deck.pop(0)
        player.life_cards.append(top_card)
    if len(player.life_cards) <= 2:
        card.has_rush = True
    return True


# --- OP07-037: More Pizza!! (Event) ---
@register_effect("OP07-037", "on_play", "[Main] Look at 5: reveal up to 1 {Supernovas} type card (not More Pizza!!) to hand.")
def op07_037_more_pizza(game_state, player, card):
    """[Main] Look at 5: choose up to 1 Supernovas type card (not More Pizza!!) to add to hand."""
    return search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: 'supernovas' in (c.card_origin or '').lower() and c.name != 'More Pizza!!',
        source_card=card,
        prompt="Look at top 5: choose up to 1 Supernovas type card (not More Pizza!!) to add to hand")


# --- OP07-114: He Possesses the World's Most Brilliant Mind (Event) ---
@register_effect("OP07-114", "on_play", "[Main] Look at 5: reveal up to 1 {Egghead} type card (not this card) to hand.")
def op07_114_brilliant_mind(game_state, player, card):
    """[Main] Look at 5: choose up to 1 Egghead type card (not this card) to add to hand."""
    return search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: 'egghead' in (c.card_origin or '').lower() and c.name != "He Possesses the World's Most Brilliant Mind",
        source_card=card,
        prompt="Look at top 5: choose up to 1 Egghead type card to add to hand")


# --- OP07-077: We're Going to Claim the One Piece!!! ---
@register_effect("OP07-077", "on_play", "[Main] If AK/BM leader, look at 5, add Animal Kingdom/Big Mom Pirates card")
def op07_077_one_piece(game_state, player, card):
    """[Main] If Animal Kingdom/Big Mom Pirates leader, look at 5, add 1 AK/BM card."""
    leader_type = (player.leader.card_origin or '').lower() if player.leader else ''
    if 'animal kingdom pirates' not in leader_type and 'big mom pirates' not in leader_type:
        return False
    return search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: ('animal kingdom pirates' in (c.card_origin or '').lower()
                             or 'big mom pirates' in (c.card_origin or '').lower()),
        source_card=card,
        prompt="Look at top 5: choose 1 Animal Kingdom Pirates or Big Mom Pirates card to add to hand")
