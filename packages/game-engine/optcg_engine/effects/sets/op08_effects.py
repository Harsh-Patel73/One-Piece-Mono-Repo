"""
Hardcoded effects for OP08 cards.
"""

from ..hardcoded import (
    create_add_to_life_choice, create_bottom_deck_choice, create_ko_choice, create_mode_choice,
    create_own_character_choice, create_play_from_hand_choice, create_power_effect_choice, create_return_to_hand_choice,
    create_target_choice, add_power_modifier, check_leader_type, draw_cards, get_opponent, give_don_to_card,
    register_effect, search_top_cards, trash_from_hand,
)


# --- OP08-001: Tony Tony.Chopper (Leader) ---
@register_effect("OP08-001", "MAIN", "Give Animal/Drum Kingdom chars 1 rested DON each")
def chopper_leader_effect(game_state, player, card):
    rested_don = [d for d in player.don_pool if d.is_resting]
    targets = [c for c in player.cards_in_play
              if 'animal' in (c.card_origin or '').lower()
              or 'drum kingdom' in (c.card_origin or '').lower()][:3]
    given = 0
    for target in targets:
        if rested_don:
            give_don_to_card(player, target, 1, rested_only=True)
            given += 1
    return given > 0


# --- OP08-001: Tony Tony.Chopper ---
@register_effect("OP08-001", "ACTIVATE_MAIN", "Give up to 3 Animal/Drum Kingdom Characters 1 rested DON each")
def chopper_op08_effect(game_state, player, card):
    targets = [c for c in player.cards_in_play
               if 'animal' in (c.card_origin or '').lower()
               or 'drum kingdom' in (c.card_origin or '').lower()]
    targets = targets[:3]  # Up to 3
    for target in targets:
        give_don_to_card(player, target, 1, rested_only=True)
    return len(targets) > 0


# --- OP08-038: We Would Never Sell a Comrade to an Enemy!!! ---
@register_effect("OP08-038", "MAIN", "Rest 2 chars: Chars can't be KO'd by effects until opponent's turn end")
def we_would_never_sell_effect(game_state, player, card):
    """Rest 2 characters to protect all characters from effect KO."""
    active_chars = [c for c in player.cards_in_play if not c.is_resting]
    if len(active_chars) >= 2:
        active_chars[0].is_resting = True
        active_chars[1].is_resting = True
        # Mark all characters as protected
        for c in player.cards_in_play:
            c.protected_from_ko_effects_until_opponent_turn_end = True
        return True
    return False


# --- OP08-047: Jozu ---
@register_effect("OP08-047", "ON_PLAY", "Return own character to hand, then return opponent's cost 6 or less")
def op08_047_jozu(game_state, player, card):
    # Cost: You may return 1 of your characters (other than this) to hand
    own_chars = [c for c in player.cards_in_play if c != card]
    if own_chars:
        jozu_card = card
        own_snap = list(own_chars)
        def jozu_cb(selected: list) -> None:
            target_idx = int(selected[0]) if selected else -1
            if not selected or target_idx < 0:
                game_state._log(f"{player.name} chose not to use Jozu's effect")
                return
            if 0 <= target_idx < len(own_snap):
                target = own_snap[target_idx]
                if target in player.cards_in_play:
                    player.cards_in_play.remove(target)
                    player.hand.append(target)
                    game_state._log(f"{player.name} returned {target.name} to hand")
            opponent = get_opponent(game_state, player)
            all_targets = [c for c in player.cards_in_play
                           if (getattr(c, 'cost', 0) or 0) <= 6 and c is not jozu_card]
            all_targets += [c for c in opponent.cards_in_play
                            if (getattr(c, 'cost', 0) or 0) <= 6]
            if all_targets:
                create_return_to_hand_choice(game_state, player, all_targets,
                                             source_card=None,
                                             prompt="Return up to 1 cost 6 or less Character to owner's hand",
                                             optional=True)
        return create_own_character_choice(
            game_state, player, own_chars, source_card=card,
            prompt="You may return one of your Characters to hand (cost for effect)",
            callback=jozu_cb,
            optional=True
        )
    return True


# --- OP08-044: Kingdew ---
@register_effect("OP08-044", "ACTIVATE_MAIN", "Reveal 2 Whitebeard Pirates: +2000 power")
def op08_044_kingdew(game_state, player, card):
    # Check for 2 Whitebeard Pirates cards in hand
    wb_cards = [c for c in player.hand if "Whitebeard Pirates" in (getattr(c, 'card_origin', '') or '')]
    if len(wb_cards) >= 2:
        add_power_modifier(card, 2000)
        return True
    return False


# --- OP08-055: Phoenix Brand ---
@register_effect("OP08-055", "MAIN", "Reveal 2 Whitebeard Pirates: Place cost 6 or less at bottom of deck")
def op08_055_phoenix_brand(game_state, player, card):
    wb_cards = [c for c in player.hand if "Whitebeard Pirates" in (getattr(c, 'card_origin', '') or '')]
    if len(wb_cards) >= 2:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 6]
        if targets:
            return create_bottom_deck_choice(
                game_state, player, targets, source_card=card,
                prompt="Choose opponent's cost 6 or less Character to place at bottom of deck"
            )
    return False


# --- OP08-059: Alber ---
@register_effect("OP08-059", "ACTIVATE_MAIN", "Trash this: If Leader is Animal Kingdom Pirates and 10 DON, play King cost 7 or less")
def op08_059_alber(game_state, player, card):
    if check_leader_type(player, "Animal Kingdom Pirates") and len(player.don_pool) >= 10:
        kings = [c for c in player.hand
                 if 'King' in (getattr(c, 'name', '') or '')
                 and (getattr(c, 'cost', 0) or 0) <= 7]
        if kings:
            # Trash this character
            if card in player.cards_in_play:
                player.cards_in_play.remove(card)
                player.trash.append(card)
            # Play King
            to_play = kings[0]
            player.hand.remove(to_play)
            player.cards_in_play.append(to_play)
            return True
    return False


# =============================================================================
# MORE LEADER CONDITION CARDS - Kuja Pirates
# =============================================================================

# --- OP08-041: Aphelandra ---
@register_effect("OP08-041", "ACTIVATE_MAIN", "Return this: If Leader is Kuja Pirates, place opponent cost 1 at bottom")
def op08_041_aphelandra(game_state, player, card):
    if check_leader_type(player, "Kuja Pirates"):
        if card in player.cards_in_play:
            player.cards_in_play.remove(card)
            player.hand.append(card)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 1]
        if targets:
            return create_bottom_deck_choice(game_state, player, targets, source_card=card,
                                            prompt="Choose opponent's cost 1 or less to place at bottom of deck")
    return True


# --- OP08-095: Iron Body Fang Flash ---
@register_effect("OP08-095", "MAIN", "If 10+ trash, char gains +2000 power until opponent's turn end")
def op08_095_iron_body_fang(game_state, player, card):
    """Main: If 10+ trash, char gains +2000 power until opponent's turn end."""
    if check_trash_count(player, 10) and player.cards_in_play:
        return create_power_effect_choice(
            game_state, player, player.cards_in_play, 2000,
            source_card=card,
            prompt="Choose your Character to give +2000 power"
        )
    return False


# =============================================================================
# LEADER CARD EFFECTS - OP08-OP14
# =============================================================================

# --- OP08-001: Tony Tony.Chopper (Leader) ---
@register_effect("OP08-001", "activate", "[Activate: Main] Give up to 3 Animal/Drum Kingdom chars 1 rested DON each")
def op08_001_chopper_leader(game_state, player, card):
    """Once Per Turn: Give up to 3 Animal or Drum Kingdom Characters up to 1 rested DON each."""
    if hasattr(card, 'op08_001_used') and card.op08_001_used:
        return False
    targets = [c for c in player.cards_in_play
               if 'animal' in (c.card_origin or '').lower()
               or 'drum kingdom' in (c.card_origin or '').lower()]
    rested_don = player.don_pool.count("rested")
    given = 0
    for char in targets[:3]:
        if rested_don and given < len(rested_don):
            char.attached_don = getattr(char, 'attached_don', 0) + 1
            given += 1
    card.op08_001_used = True
    return given > 0


# --- OP08-002: Marco (Leader) ---
@register_effect("OP08-002", "activate", "[DON!! x1] Draw 1, put 1 on top/bottom, give char +1000")
def op08_002_marco_leader(game_state, player, card):
    """DON x1, Once Per Turn: Draw 1, put 1 from hand on top/bottom of deck, give 1 Character +1000."""
    if getattr(card, 'attached_don', 0) >= 1:
        if hasattr(card, 'op08_002_used') and card.op08_002_used:
            return False
        card.op08_002_used = True
        draw_cards(player, 1)
        if player.hand:
            # Put a card from hand on top (simplified - should let player choose)
            to_put = player.hand[0]
            player.hand.remove(to_put)
            player.deck.insert(0, to_put)
        if player.cards_in_play:
            return create_power_effect_choice(
                game_state, player, player.cards_in_play, 1000,
                source_card=card,
                prompt="Choose your Character to give +1000 power"
            )
        return True
    return False


# --- OP08-021: Carrot (Leader) ---
@register_effect("OP08-021", "activate", "[Activate: Main] If Minks char, rest opponent cost 5-")
def op08_021_carrot_leader(game_state, player, card):
    """Once Per Turn: If you have a Minks Character, rest opponent's cost 5 or less Character."""
    if hasattr(card, 'op08_021_used') and card.op08_021_used:
        return False
    minks = [c for c in player.cards_in_play
             if 'minks' in (c.card_origin or '').lower()]
    if minks:
        card.op08_021_used = True
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play
                   if not c.is_resting and (getattr(c, 'cost', 0) or 0) <= 5]
        if targets:
            return create_target_choice(
                game_state, player, targets,
                callback_action="rest_target",
                source_card=card,
                prompt="Choose opponent's cost 5 or less Character to rest"
            )
        return True
    return False


# --- OP08-057: King (Leader) ---
@register_effect("OP08-057", "activate", "[Activate: Main] DON -2: Choose effect")
def op08_057_king_leader(game_state, player, card):
    """Once Per Turn, DON -2: Give char +2000 OR play cost 2 or less from trash rested."""
    if hasattr(card, 'op08_057_used') and card.op08_057_used:
        return False
    if len(player.don_pool) >= 2:
        for _ in range(2):
            if player.don_pool:
                don = player.don_pool.pop()
                if hasattr(player, 'don_deck'):
                    player.don_deck.append(don)
        card.op08_057_used = True

        trash_chars = [c for c in player.trash
                      if getattr(c, 'card_type', '') == 'CHARACTER'
                      and (getattr(c, 'cost', 0) or 0) <= 2]

        modes = []
        if player.cards_in_play:
            modes.append({"id": "power", "label": "Give +2000 power", "description": f"Give 1 of {len(player.cards_in_play)} chars +2000"})
        if trash_chars:
            modes.append({"id": "play_trash", "label": "Play from trash", "description": f"Play 1 of {len(trash_chars)} cost 2 or less rested"})

        if modes:
            return create_mode_choice(
                game_state, player, modes, source_card=card,
                prompt="Choose King Leader effect"
            )
        return True
    return False


# --- OP08-058: Charlotte Pudding (Leader) ---
@register_effect("OP08-058", "on_attack", "[When Attacking] Turn 2 life face-up: Add 1 DON rested")
def op08_058_pudding_leader(game_state, player, card):
    """When Attacking: Turn 2 cards from top of Life face-up, add 1 DON from deck rested."""
    if len(player.life_cards) >= 2:
        for life_card in player.life_cards[-2:]:
            life_card.is_face_up = True
        if hasattr(player, 'don_deck') and player.don_deck:
            don = player.don_deck.pop(0)
            don.is_resting = True
            player.don_pool.append(don)
        return True
    return False


# --- OP08-098: Kalgara (Leader) ---
@register_effect("OP08-098", "on_attack", "[DON!! x1] Play Shandian cost <= DON count")
def op08_098_kalgara_leader(game_state, player, card):
    """DON x1, When Attacking: Play Shandian Warrior from hand with cost <= DON count on field."""
    if getattr(card, 'attached_don', 0) >= 1:
        don_count = len(player.don_pool)
        shandian = [c for c in player.hand
                    if getattr(c, 'card_type', '') == 'CHARACTER'
                    and 'shandian warrior' in (c.card_origin or '').lower()
                    and (getattr(c, 'cost', 0) or 0) <= don_count]
        if shandian:
            return create_play_from_hand_choice(
                game_state, player, shandian, source_card=card,
                prompt=f"Choose Shandian Warrior cost {don_count} or less to play from hand"
            )
    return False


# =============================================================================
# OP08 CHARACTER EFFECTS
# =============================================================================

# --- OP08-003: Twenty Doctors ---
@register_effect("OP08-003", "blocker", "[Blocker]")
def op08_003_twenty_doctors(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


# --- OP08-004: Kuromarimo ---
@register_effect("OP08-004", "on_play", "[On Play] If you have Chess, K.O. opponent's 3000 power or less")
def op08_004_kuromarimo(game_state, player, card):
    """On Play: If you have Chess, K.O. opponent's Character with 3000 power or less."""
    has_chess = any(getattr(c, 'name', '') == 'Chess' for c in player.cards_in_play)
    if has_chess:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'power', 0) or 0) <= 3000]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's 3000 power or less to K.O.")
    return True


# --- OP08-005: Chess ---
@register_effect("OP08-005", "on_play", "[On Play] Give opponent -2000 power, play Kuromarimo if you don't have one")
def op08_005_chess(game_state, player, card):
    """On Play: Give opponent -2000 power, play Kuromarimo from hand if you don't have one."""
    opponent = get_opponent(game_state, player)
    # Play Kuromarimo if you don't have one
    has_kuromarimo = any(getattr(c, 'name', '') == 'Kuromarimo' for c in player.cards_in_play)
    if not has_kuromarimo:
        for c in list(player.hand):
            if getattr(c, 'name', '') == 'Kuromarimo':
                player.hand.remove(c)
                player.cards_in_play.append(c)
                break
    if opponent.cards_in_play:
        return create_power_reduction_choice(game_state, player, list(opponent.cards_in_play), 2000,
                                            source_card=card, prompt="Choose opponent's Character for -2000 power")
    return True


# --- OP08-006: Chessmarimo ---
@register_effect("OP08-006", "your_turn", "[Your Turn] +2000 power if Kuromarimo and Chess in trash")
def op08_006_chessmarimo(game_state, player, card):
    """Your Turn: +2000 power if Kuromarimo and Chess in trash."""
    has_kuromarimo = any(getattr(c, 'name', '') == 'Kuromarimo' for c in player.trash)
    has_chess = any(getattr(c, 'name', '') == 'Chess' for c in player.trash)
    if has_kuromarimo and has_chess:
        card.power_modifier = getattr(card, 'power_modifier', 0) + 2000
    return True


# --- OP08-007: Tony Tony.Chopper ---
@register_effect("OP08-007", "on_play", "[On Play]/[When Attacking] Look at 5, play Animal 4000 power or less rested")
def op08_007_chopper_on_play(game_state, player, card):
    """On Play: Look at 5, play Animal type Character with 4000 power or less rested."""
    looked = player.deck[:5] if len(player.deck) >= 5 else player.deck[:]
    for c in looked:
        if 'Animal' in (c.card_origin or '') and (getattr(c, 'power', 0) or 0) <= 4000:
            if getattr(c, 'card_type', '') == 'CHARACTER':
                player.deck.remove(c)
                c.is_resting = True
                player.cards_in_play.append(c)
                break
    return True


@register_effect("OP08-007", "on_attack", "[When Attacking] Look at 5, play Animal 4000 power or less rested")
def op08_007_chopper_on_attack(game_state, player, card):
    """When Attacking: Look at 5, play Animal type Character with 4000 power or less rested."""
    looked = player.deck[:5] if len(player.deck) >= 5 else player.deck[:]
    for c in looked:
        if 'Animal' in (c.card_origin or '') and (getattr(c, 'power', 0) or 0) <= 4000:
            if getattr(c, 'card_type', '') == 'CHARACTER':
                player.deck.remove(c)
                c.is_resting = True
                player.cards_in_play.append(c)
                break
    return True


# --- OP08-008: Dalton ---
@register_effect("OP08-008", "on_play", "[On Play] Give opponent -1000 power")
def op08_008_dalton_on_play(game_state, player, card):
    """On Play: Give opponent's Character -1000 power."""
    opponent = get_opponent(game_state, player)
    if opponent.cards_in_play:
        return create_power_reduction_choice(game_state, player, list(opponent.cards_in_play), 1000,
                                            source_card=card, prompt="Choose opponent's Character for -1000 power")
    return True


@register_effect("OP08-008", "activate", "[Activate: Main] Add life to hand: Gain Rush")
def op08_008_dalton_activate(game_state, player, card):
    """Activate: With DON, add life to hand to gain Rush."""
    if getattr(card, 'op08_008_used', False):
        return False
    if getattr(card, 'attached_don', 0) >= 1 and player.life_cards:
        life_card = player.life_cards.pop()
        player.hand.append(life_card)
        card.has_rush = True
        card.op08_008_used = True
        return True
    return False


# --- OP08-010: Hiking Bear ---
@register_effect("OP08-010", "activate", "[Activate: Main] Give Animal +1000 power")
def op08_010_hiking_bear(game_state, player, card):
    """Activate: With DON, give Animal Character +1000 power."""
    if getattr(card, 'op08_010_used', False):
        return False
    if getattr(card, 'attached_don', 0) >= 1:
        for c in player.cards_in_play:
            if c != card and 'Animal' in (c.card_origin or ''):
                c.power_modifier = getattr(c, 'power_modifier', 0) + 1000
                break
        card.op08_010_used = True
        return True
    return False


# --- OP08-012: Lapins ---
@register_effect("OP08-012", "on_attack", "[When Attacking] With DON x2 and Drum Kingdom leader, K.O. 4000 power or less")
def op08_012_lapins(game_state, player, card):
    """When Attacking: With DON x2 and Drum Kingdom leader, K.O. opponent's 4000 power or less."""
    if getattr(card, 'attached_don', 0) >= 2:
        if player.leader and 'Drum Kingdom' in (player.leader.card_origin or ''):
            opponent = get_opponent(game_state, player)
            targets = [c for c in opponent.cards_in_play if (getattr(c, 'power', 0) or 0) <= 4000]
            if targets:
                return create_ko_choice(game_state, player, targets, source_card=card,
                                       prompt="Choose opponent's 4000 power or less to K.O.")
    return True


# --- OP08-013: Robson ---
@register_effect("OP08-013", "don_attached", "[DON!! x2] Gain Rush")
def op08_013_robson(game_state, player, card):
    """With DON x2, gain Rush."""
    if getattr(card, 'attached_don', 0) >= 2:
        card.has_rush = True
    return True


# --- OP08-014: Wapol ---
@register_effect("OP08-014", "on_attack", "[When Attacking] With DON, give opponent -2000 power, gain +2000 power")
def op08_014_wapol(game_state, player, card):
    """When Attacking: With DON, give opponent -2000 power and gain +2000 power."""
    if getattr(card, 'attached_don', 0) >= 1:
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            opponent.cards_in_play[0].power_modifier = getattr(opponent.cards_in_play[0], 'power_modifier', 0) - 2000
        card.power_modifier = getattr(card, 'power_modifier', 0) + 2000
    return True


# --- OP08-015: Dr.Kureha ---
@register_effect("OP08-015", "on_play", "[On Play] Look at 4, add Chopper or Drum Kingdom")
def op08_015_kureha(game_state, player, card):
    """On Play: Look at 4, add Tony Tony.Chopper or Drum Kingdom card."""
    def filter_fn(c):
        name = getattr(c, 'name', '') or ''
        types = (c.card_origin or '') or ''
        return (name == 'Tony Tony.Chopper'
                or ('Drum Kingdom' in types and name != 'Dr.Kureha'))
    search_top_cards(game_state, player, 4, add_count=1, filter_fn=filter_fn,
                     source_card=card,
                     prompt="Look at top 4. Choose a Chopper or Drum Kingdom card to add to hand.")
    return True


# --- OP08-016: Dr.Hiriluk ---
@register_effect("OP08-016", "activate", "[Activate: Main] Rest: If Chopper leader, Chopper Characters +2000")
def op08_016_hiriluk(game_state, player, card):
    """Activate: Rest this to give Chopper Characters +2000 if Chopper leader."""
    if card.is_resting:
        return False
    if player.leader and getattr(player.leader, 'name', '') == 'Tony Tony.Chopper':
        card.is_resting = True
        for c in player.cards_in_play:
            if getattr(c, 'name', '') == 'Tony Tony.Chopper':
                c.power_modifier = getattr(c, 'power_modifier', 0) + 2000
        return True
    return False


# --- OP08-022: Inuarashi ---
@register_effect("OP08-022", "on_play", "[On Play] If Minks leader, 2 opponent's rested cost 5 or less don't refresh")
def op08_022_inuarashi(game_state, player, card):
    """On Play: If Minks leader, up to 2 opponent's rested cost 5 or less won't refresh."""
    if player.leader and 'Minks' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        count = 0
        for c in opponent.cards_in_play:
            if c.is_resting and (getattr(c, 'cost', 0) or 0) <= 5 and count < 2:
                c.skip_refresh = True
                count += 1
    return True


# --- OP08-023: Carrot ---
@register_effect("OP08-023", "on_play", "[On Play] Opponent's rested cost 7 or less won't refresh")
def op08_023_carrot_on_play(game_state, player, card):
    """On Play: Opponent's rested cost 7 or less won't refresh."""
    opponent = get_opponent(game_state, player)
    for c in opponent.cards_in_play:
        if c.is_resting and (getattr(c, 'cost', 0) or 0) <= 7:
            c.skip_refresh = True
            break
    return True


@register_effect("OP08-023", "on_attack", "[When Attacking] Opponent's rested cost 7 or less won't refresh")
def op08_023_carrot_on_attack(game_state, player, card):
    """When Attacking: Opponent's rested cost 7 or less won't refresh."""
    opponent = get_opponent(game_state, player)
    for c in opponent.cards_in_play:
        if c.is_resting and (getattr(c, 'cost', 0) or 0) <= 7:
            c.skip_refresh = True
            break
    return True


# --- OP08-024: Concelot ---
@register_effect("OP08-024", "on_attack", "[When Attacking] Opponent's rested cost 4 or less won't refresh")
def op08_024_concelot(game_state, player, card):
    """When Attacking: Opponent's rested cost 4 or less won't refresh."""
    opponent = get_opponent(game_state, player)
    for c in opponent.cards_in_play:
        if c.is_resting and (getattr(c, 'cost', 0) or 0) <= 4:
            c.skip_refresh = True
            break
    return True


# --- OP08-025: Shishilian ---
@register_effect("OP08-025", "on_play", "[On Play] Opponent's rested cost 3 or less won't refresh")
def op08_025_shishilian(game_state, player, card):
    """On Play: Opponent's rested cost 3 or less won't refresh."""
    opponent = get_opponent(game_state, player)
    for c in opponent.cards_in_play:
        if c.is_resting and (getattr(c, 'cost', 0) or 0) <= 3:
            c.skip_refresh = True
            break
    return True


# --- OP08-026: Giovanni ---
@register_effect("OP08-026", "on_attack", "[When Attacking] With DON, opponent's rested cost 1 or less won't refresh")
def op08_026_giovanni(game_state, player, card):
    """When Attacking: With DON, opponent's rested cost 1 or less won't refresh."""
    if getattr(card, 'attached_don', 0) >= 1:
        opponent = get_opponent(game_state, player)
        for c in opponent.cards_in_play:
            if c.is_resting and (getattr(c, 'cost', 0) or 0) <= 1:
                c.skip_refresh = True
                break
    return True


# --- OP08-028: Nekomamushi ---
@register_effect("OP08-028", "on_play", "[On Play] If opponent has 7+ rested cards, gain Rush")
def op08_028_nekomamushi(game_state, player, card):
    """On Play: If opponent has 7+ rested cards, gain Rush."""
    opponent = get_opponent(game_state, player)
    rested_count = sum(1 for c in opponent.cards_in_play if c.is_resting)
    if opponent.leader and getattr(opponent.leader, 'is_resting', False):
        rested_count += 1
    rested_count += sum(1 for d in getattr(opponent, 'don_cards', []) if getattr(d, 'is_resting', False))
    if rested_count >= 7:
        card.has_rush = True
    return True


# --- OP08-029: Pekoms ---
@register_effect("OP08-029", "continuous", "[Continuous] If active, Minks cost 3 or less can't be K.O.'d by effects")
def op08_029_pekoms(game_state, player, card):
    """Continuous: If active, Minks cost 3 or less can't be K.O.'d by effects."""
    if not card.is_resting:
        for c in player.cards_in_play:
            if c != card and 'Minks' in (c.card_origin or '') and (getattr(c, 'cost', 0) or 0) <= 3:
                c.ko_protection = True
    return True


# --- OP08-030: Pedro ---
@register_effect("OP08-030", "blocker", "[Blocker]")
def op08_030_pedro_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP08-030", "on_ko", "[On K.O.] Rest opponent's DON or K.O. rested cost 6 or less")
def op08_030_pedro_on_ko(game_state, player, card):
    """On K.O.: Rest opponent's DON or K.O. rested cost 6 or less."""
    opponent = get_opponent(game_state, player)
    # K.O. rested cost 6 or less
    targets = [c for c in opponent.cards_in_play if c.is_resting and (getattr(c, 'cost', 0) or 0) <= 6]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                               prompt="Choose opponent's rested cost 6 or less to K.O.")
    else:
        # Rest opponent's DON as fallback
        for d in getattr(opponent, 'don_cards', []):
            if not getattr(d, 'is_resting', False):
                d.is_resting = True
                break
    return True


# --- OP08-031: Miyagi ---
@register_effect("OP08-031", "on_play", "[On Play] Set Minks cost 2 or less as active")
def op08_031_miyagi(game_state, player, card):
    """On Play: Set Minks cost 2 or less as active."""
    for c in player.cards_in_play:
        if 'Minks' in (c.card_origin or '') and (getattr(c, 'cost', 0) or 0) <= 2:
            c.is_resting = False
            break
    return True


# --- OP08-032: Milky ---
@register_effect("OP08-032", "activate", "[Activate: Main] Rest: If Minks leader, set DON as active")
def op08_032_milky(game_state, player, card):
    """Activate: Rest this to set DON as active if Minks leader."""
    if card.is_resting:
        return False
    if player.leader and 'Minks' in (player.leader.card_origin or ''):
        card.is_resting = True
        for d in getattr(player, 'don_cards', []):
            if getattr(d, 'is_resting', False):
                d.is_resting = False
                break
        return True
    return False


# --- OP08-033: Roddy ---
@register_effect("OP08-033", "on_play", "[On Play] If Minks leader and 7+ rested, K.O. rested cost 2 or less")
def op08_033_roddy(game_state, player, card):
    """On Play: If Minks leader and opponent has 7+ rested cards, K.O. rested cost 2 or less."""
    if player.leader and 'Minks' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        rested_count = sum(1 for c in opponent.cards_in_play if c.is_resting)
        if rested_count >= 7:
            targets = [c for c in opponent.cards_in_play if c.is_resting and (getattr(c, 'cost', 0) or 0) <= 2]
            if targets:
                return create_ko_choice(game_state, player, targets, source_card=card,
                                       prompt="Choose opponent's rested cost 2 or less to K.O.")
    return True


# --- OP08-034: Wanda ---
@register_effect("OP08-034", "on_play", "[On Play] Look at 5, add Minks card")
def op08_034_wanda(game_state, player, card):
    """On Play: Look at 5, add Minks card other than Wanda."""
    def filter_fn(c):
        return ('Minks' in (c.card_origin or '')
                and getattr(c, 'name', '') != 'Wanda')
    search_top_cards(game_state, player, 5, add_count=1, filter_fn=filter_fn,
                     source_card=card,
                     prompt="Look at top 5. Choose a Minks card to add to hand.")
    return True


# --- OP08-040: Atmos ---
@register_effect("OP08-040", "on_play", "[On Play] Reveal 2 Whitebeard Pirates: Return cost 4 or less to hand")
def op08_040_atmos(game_state, player, card):
    """On Play: Reveal 2 Whitebeard Pirates from hand to return opponent's cost 4 or less to hand."""
    wb_cards = [c for c in player.hand if 'Whitebeard Pirates' in (c.card_origin or '')]
    if len(wb_cards) >= 2 and player.leader and 'Whitebeard Pirates' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
        if targets:
            return create_return_to_hand_choice(game_state, player, targets, source_card=card,
                                               prompt="Choose opponent's cost 4 or less to return to hand")
    return True


# --- OP08-041: Aphelandra ---
@register_effect("OP08-041", "activate", "[Activate: Main] Return to hand: If Kuja leader, bottom deck cost 1 or less")
def op08_041_aphelandra(game_state, player, card):
    """Activate: Return to hand to bottom deck opponent's cost 1 or less if Kuja leader."""
    if player.leader and 'Kuja Pirates' in (player.leader.card_origin or ''):
        if card in player.cards_in_play:
            player.cards_in_play.remove(card)
            player.hand.append(card)
            opponent = get_opponent(game_state, player)
            targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 1]
            if targets:
                return create_bottom_deck_choice(game_state, player, targets, source_card=card,
                                                prompt="Choose opponent's cost 1 or less to place at deck bottom")
            return True
    return False


# --- OP08-042: Edward Weevil ---
@register_effect("OP08-042", "on_attack", "[When Attacking] With DON, return cost 3 or less to hand")
def op08_042_edward_weevil(game_state, player, card):
    """When Attacking: With DON, return Character with cost 3 or less to hand."""
    if getattr(card, 'attached_don', 0) >= 1:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
        if targets:
            return create_return_to_hand_choice(game_state, player, targets, source_card=card,
                                               prompt="Choose opponent's cost 3 or less to return to hand")
    return True


# --- OP08-043: Edward.Newgate ---
@register_effect("OP08-043", "on_play", "[On Play] If Whitebeard leader and 2 or less life, opponent's Characters need to trash 2 to attack")
def op08_043_edward_newgate(game_state, player, card):
    """On Play: If Whitebeard leader and 2 or less life, mark opponent's Characters with attack restriction."""
    if player.leader and 'Whitebeard Pirates' in (player.leader.card_origin or '') and len(player.life_cards) <= 2:
        opponent = get_opponent(game_state, player)
        for c in opponent.cards_in_play:
            c.attack_cost = 2  # Must trash 2 cards to attack
    return True


# --- OP08-044: Kingdew ---
@register_effect("OP08-044", "activate", "[Activate: Main] Reveal 2 Whitebeard Pirates: +2000 power")
def op08_044_kingdew(game_state, player, card):
    """Activate: Reveal 2 Whitebeard Pirates from hand to gain +2000 power."""
    if getattr(card, 'op08_044_used', False):
        return False
    wb_cards = [c for c in player.hand if 'Whitebeard Pirates' in (c.card_origin or '')]
    if len(wb_cards) >= 2:
        card.power_modifier = getattr(card, 'power_modifier', 0) + 2000
        card.op08_044_used = True
        return True
    return False


# --- OP08-045: Thatch ---
@register_effect("OP08-045", "on_removal", "[Continuous] When removed by effect or K.O.'d, trash and draw 1 instead")
def op08_045_thatch(game_state, player, card):
    """When removed by effect or K.O.'d, trash and draw 1 instead."""
    # This is a replacement effect - mark the card
    card.replacement_effect = 'trash_and_draw'
    return True


# --- OP08-046: Shakuyaku ---
@register_effect("OP08-046", "your_turn", "[Your Turn] When Character removed by your effect, opponent puts card at bottom of deck")
def op08_046_shakuyaku(game_state, player, card):
    """Your Turn: When Character removed by your effect, opponent puts card at bottom of deck."""
    if getattr(card, 'op08_046_used', False):
        return False
    # This is a triggered effect that activates when a character is removed
    card.removal_trigger = True
    return True


# --- OP08-049: Speed Jil ---
@register_effect("OP08-049", "on_play", "[On Play] Reveal top, if Whitebeard Pirates gain Rush")
def op08_049_speed_jil(game_state, player, card):
    """On Play: Reveal top card, if Whitebeard Pirates gain Rush."""
    if player.deck:
        top_card = player.deck[0]
        if 'Whitebeard Pirates' in (top_card.card_origin or ''):
            card.has_rush = True
    return True


# --- OP08-050: Namule ---
@register_effect("OP08-050", "blocker", "[Blocker]")
def op08_050_namule_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP08-050", "on_play", "[On Play] Draw 2, place 2 at top or bottom")
def op08_050_namule_on_play(game_state, player, card):
    """On Play: Draw 2 and place 2 from hand at top or bottom of deck."""
    draw_cards(player, 2)
    # Place 2 cards at bottom (simplified)
    for _ in range(min(2, len(player.hand))):
        if player.hand:
            c = player.hand.pop(0)
            player.deck.append(c)
    return True


# --- OP08-051: Buckin ---
@register_effect("OP08-051", "on_play", "[On Play] Edward Weevil +2000 power")
def op08_051_buckin(game_state, player, card):
    """On Play: Edward Weevil gains +2000 power."""
    for c in player.cards_in_play:
        if getattr(c, 'name', '') == 'Edward Weevil':
            c.power_modifier = getattr(c, 'power_modifier', 0) + 2000
            break
    return True


# --- OP08-052: Portgas.D.Ace ---
@register_effect("OP08-052", "on_play", "[On Play] Reveal top, play Whitebeard Pirates cost 4 or less")
def op08_052_ace(game_state, player, card):
    """On Play: Reveal top card and play Whitebeard Pirates cost 4 or less."""
    if player.deck:
        top_card = player.deck[0]
        if 'Whitebeard Pirates' in (top_card.card_origin or '') and (getattr(top_card, 'cost', 0) or 0) <= 4:
            if getattr(top_card, 'card_type', '') == 'CHARACTER':
                player.deck.remove(top_card)
                player.cards_in_play.append(top_card)
    return True


# --- OP08-059: Alber ---
@register_effect("OP08-059", "activate", "[Activate: Main] Trash: If Animal Kingdom leader and 10 DON, play King cost 7 or less")
def op08_059_alber(game_state, player, card):
    """Activate: Trash to play King cost 7 or less if Animal Kingdom leader and 10 DON."""
    if player.leader and 'Animal Kingdom Pirates' in (player.leader.card_origin or ''):
        don_count = len(getattr(player, 'don_cards', []))
        if don_count >= 10 and card in player.cards_in_play:
            player.cards_in_play.remove(card)
            player.trash.append(card)
            for c in list(player.hand):
                if getattr(c, 'name', '') == 'King' and (getattr(c, 'cost', 0) or 0) <= 7:
                    player.hand.remove(c)
                    player.cards_in_play.append(c)
                    break
            return True
    return False


# --- OP08-060: King ---
@register_effect("OP08-060", "on_play", "[On Play] DON -1: If opponent has 5+ DON, gain Rush")
def op08_060_king(game_state, player, card):
    """On Play: Return DON to deck, if opponent has 5+ DON gain Rush."""
    # Return 1 DON to deck
    if getattr(player, 'don_cards', []):
        don = player.don_pool.pop()
        if hasattr(player, 'don_deck'):
            player.don_deck.append(don)
    # Check opponent's DON
    opponent = get_opponent(game_state, player)
    if len(getattr(opponent, 'don_cards', [])) >= 5:
        card.has_rush = True
    return True


# --- OP08-061: Charlotte Oven ---
@register_effect("OP08-061", "on_attack", "[When Attacking] DON -1: K.O. cost 3 or less")
def op08_061_charlotte_oven(game_state, player, card):
    """When Attacking: Return DON to deck to K.O. cost 3 or less."""
    if getattr(player, 'don_cards', []):
        don = player.don_pool.pop()
        if hasattr(player, 'don_deck'):
            player.don_deck.append(don)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's cost 3 or less to K.O.")
    return True


# --- OP08-062: Charlotte Katakuri (2 cost) ---
@register_effect("OP08-062", "activate", "[Activate: Main] Trash: Play Katakuri cost 3+ up to opponent's DON count")
def op08_062_katakuri_2(game_state, player, card):
    """Activate: Trash to play Katakuri cost 3+ up to opponent's DON count."""
    if player.leader and 'Big Mom Pirates' in (player.leader.card_origin or ''):
        if card in player.cards_in_play:
            player.cards_in_play.remove(card)
            player.trash.append(card)
            opponent = get_opponent(game_state, player)
            opponent_don = len(getattr(opponent, 'don_cards', []))
            for c in list(player.hand):
                if getattr(c, 'name', '') == 'Charlotte Katakuri':
                    cost = getattr(c, 'cost', 0) or 0
                    if cost >= 3 and cost <= opponent_don:
                        player.hand.remove(c)
                        player.cards_in_play.append(c)
                        break
            return True
    return False


# --- OP08-063: Charlotte Katakuri (6 cost) ---
@register_effect("OP08-063", "on_play", "[On Play] Turn life face-down: Add DON from deck")
def op08_063_katakuri_6(game_state, player, card):
    """On Play: Turn life face-down to add DON from deck."""
    if player.life_cards and hasattr(player, 'don_deck') and player.don_deck:
        # Turn top life face-down (mark as face-down)
        if player.life_cards:
            player.life_cards[-1].face_down = True
        # Add DON from deck
        don = player.don_deck.pop(0)
        don.is_resting = False
        player.don_pool.append(don)
    return True


# --- OP08-064: Charlotte Cracker ---
@register_effect("OP08-064", "activate", "[Activate: Main] DON -1: Play Biscuit Warrior from hand")
def op08_064_charlotte_cracker(game_state, player, card):
    """Activate: Return DON to deck to play Biscuit Warrior from hand."""
    if getattr(card, 'op08_064_used', False):
        return False
    if getattr(player, 'don_cards', []):
        don = player.don_pool.pop()
        if hasattr(player, 'don_deck'):
            player.don_deck.append(don)
        for c in list(player.hand):
            if getattr(c, 'name', '') == 'Biscuit Warrior':
                player.hand.remove(c)
                player.cards_in_play.append(c)
                break
        card.op08_064_used = True
        return True
    return False


# --- OP08-066: Charlotte Brulee ---
@register_effect("OP08-066", "blocker", "[Blocker]")
def op08_066_brulee_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP08-066", "on_ko", "[On K.O.] Add DON from deck rested")
def op08_066_brulee_on_ko(game_state, player, card):
    """On K.O.: Add DON from deck rested."""
    if hasattr(player, 'don_deck') and player.don_deck:
        don = player.don_deck.pop(0)
        don.is_resting = True
        player.don_pool.append(don)
    return True


# --- OP08-067: Charlotte Pudding ---
@register_effect("OP08-067", "your_turn", "[Your Turn] When DON returned to deck, add DON rested")
def op08_067_charlotte_pudding(game_state, player, card):
    """Your Turn: When DON returned to deck, add DON rested."""
    if getattr(card, 'op08_067_used', False):
        return False
    # This is a triggered effect
    card.don_return_trigger = True
    return True


# --- OP08-068: Charlotte Perospero ---
@register_effect("OP08-068", "on_ko", "[On K.O.] Add DON from deck rested")
def op08_068_perospero_on_ko(game_state, player, card):
    """On K.O.: Add DON from deck rested."""
    if hasattr(player, 'don_deck') and player.don_deck:
        don = player.don_deck.pop(0)
        don.is_resting = True
        player.don_pool.append(don)
    return True


@register_effect("OP08-068", "trigger", "[Trigger] DON -1: Play this card")
def op08_068_perospero_trigger(game_state, player, card):
    """Trigger: Return DON to deck to play this card."""
    if getattr(player, 'don_cards', []):
        don = player.don_pool.pop()
        if hasattr(player, 'don_deck'):
            player.don_deck.append(don)
        player.cards_in_play.append(card)
    return True


# --- OP08-069: Charlotte Linlin ---
@register_effect("OP08-069", "on_play", "[On Play] DON -1, trash 1: Add to life, add opponent's cost 6 or less to their life")
def op08_069_charlotte_linlin(game_state, player, card):
    """On Play: Return DON and trash 1 to add deck to life and opponent's cost 6 or less to their life."""
    if getattr(player, 'don_cards', []) and player.hand:
        # Return DON
        don = player.don_pool.pop()
        if hasattr(player, 'don_deck'):
            player.don_deck.append(don)
        # Trash 1 from hand
        trash_from_hand(player, 1, game_state, card)
        # Add top deck to life
        if player.deck:
            top = player.deck.pop(0)
            player.life_cards.append(top)
        # Add opponent's cost 6 or less to their life (player choice)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 6]
        if targets:
            return create_add_to_life_choice(game_state, player, targets, source_card=card,
                                             prompt="Choose opponent's cost 6 or less Character to add to their life")
    return True


# --- OP08-070: Baron Tamago ---
@register_effect("OP08-070", "blocker", "[Blocker]")
def op08_070_baron_tamago(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


# --- OP08-072: Biscuit Warrior ---
@register_effect("OP08-072", "blocker", "[Blocker]")
def op08_072_biscuit_warrior(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


# --- OP08-074: Black Maria ---
@register_effect("OP08-074", "activate", "[Activate: Main] If no other Black Maria, add 5 DON rested")
def op08_074_black_maria(game_state, player, card):
    """Activate: If no other Black Maria, add 5 DON rested."""
    if getattr(card, 'op08_074_used', False):
        return False
    other_black_maria = [c for c in player.cards_in_play if c != card and getattr(c, 'name', '') == 'Black Maria']
    if not other_black_maria and hasattr(player, 'don_deck'):
        for _ in range(min(5, len(player.don_deck))):
            if player.don_deck:
                don = player.don_deck.pop(0)
                don.is_resting = True
                player.don_pool.append(don)
        card.op08_074_used = True
        return True
    return False


# --- OP08-083: Gecko Moria ---
@register_effect("OP08-083", "on_play", "[On Play] Trash top 2, play Thriller Bark cost 2 or less from trash")
def op08_083_gecko_moria(game_state, player, card):
    """On Play: Trash top 2 of deck, play Thriller Bark cost 2 or less from trash."""
    # Trash top 2
    for _ in range(min(2, len(player.deck))):
        if player.deck:
            c = player.deck.pop(0)
            player.trash.append(c)
    # Play Thriller Bark cost 2 or less from trash
    for c in list(player.trash):
        if 'Thriller Bark Pirates' in (c.card_origin or '') and (getattr(c, 'cost', 0) or 0) <= 2:
            if getattr(c, 'card_type', '') == 'CHARACTER':
                player.trash.remove(c)
                player.cards_in_play.append(c)
                break
    return True


# --- OP08-084: Gismonda ---
@register_effect("OP08-084", "blocker", "[Blocker]")
def op08_084_gismonda_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP08-084", "on_play", "[On Play] If Baroque Works leader, return cost 1 or less to hand")
def op08_084_gismonda_on_play(game_state, player, card):
    """On Play: If Baroque Works leader, return opponent's cost 1 or less to hand."""
    if player.leader and 'Baroque Works' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 1]
        if targets:
            return create_return_to_hand_choice(game_state, player, targets, source_card=card,
                                               prompt="Choose opponent's cost 1 or less to return to hand")
    return True


# --- OP08-085: Stussy ---
@register_effect("OP08-085", "blocker", "[Blocker]")
def op08_085_stussy_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP08-085", "on_play", "[On Play] Play Character cost 1 or less from hand rested")
def op08_085_stussy_on_play(game_state, player, card):
    """On Play: Play Character cost 1 or less from hand rested."""
    for c in list(player.hand):
        if getattr(c, 'card_type', '') == 'CHARACTER' and (getattr(c, 'cost', 0) or 0) <= 1:
            player.hand.remove(c)
            c.is_resting = True
            player.cards_in_play.append(c)
            break
    return True


# --- OP08-086: Spandam ---
@register_effect("OP08-086", "activate", "[Activate: Main] Trash 1: Look at 3, add CP card")
def op08_086_spandam(game_state, player, card):
    """Activate: Trash 1 to look at 3 and add CP card."""
    if getattr(card, 'op08_086_used', False):
        return False
    if player.hand:
        trash_from_hand(player, 1, game_state, card)
        looked = player.deck[:3] if len(player.deck) >= 3 else player.deck[:]
        for c in looked:
            if 'CP' in (c.card_origin or ''):
                player.deck.remove(c)
                player.hand.append(c)
                break
        card.op08_086_used = True
        return True
    return False


# --- OP08-087: Baskerville ---
@register_effect("OP08-087", "blocker", "[Blocker]")
def op08_087_baskerville_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP08-087", "on_attack", "[When Attacking] If CP leader, give opponent -3000 power")
def op08_087_baskerville_on_attack(game_state, player, card):
    """When Attacking: If CP leader, give opponent's Character -3000 power."""
    if player.leader and 'CP' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            opponent.cards_in_play[0].power_modifier = getattr(opponent.cards_in_play[0], 'power_modifier', 0) - 3000
    return True


# --- OP08-088: Hattori ---
@register_effect("OP08-088", "on_play", "[On Play] Look at top 3, rearrange")
def op08_088_hattori(game_state, player, card):
    """On Play: Look at top 3 and rearrange (simplified - just peek)."""
    # In a real implementation, the player would choose the order
    return True


# --- OP08-089: Basil Hawkins ---
# No effect (vanilla)


# --- OP08-090: Morgans ---
@register_effect("OP08-090", "blocker", "[Blocker]")
def op08_090_morgans(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


# --- OP08-091: Monkey.D.Luffy ---
@register_effect("OP08-091", "on_attack", "[When Attacking] If CP leader, give opponent -4000 power")
def op08_091_luffy_on_attack(game_state, player, card):
    """When Attacking: If CP leader, give opponent's Character -4000 power."""
    if player.leader and 'CP' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            opponent.cards_in_play[0].power_modifier = getattr(opponent.cards_in_play[0], 'power_modifier', 0) - 4000
    return True


# --- OP08-092: Joseph ---
@register_effect("OP08-092", "on_play", "[On Play] Place 1 from hand at top or bottom of deck")
def op08_092_joseph(game_state, player, card):
    """On Play: Place 1 from hand at top or bottom of deck."""
    if player.hand:
        c = player.hand.pop(0)
        player.deck.append(c)  # Place at bottom
    return True


# --- OP08-093: Rob Lucci ---
@register_effect("OP08-093", "on_play", "[On Play] Play cost 2 or less CP from hand rested")
def op08_093_rob_lucci_on_play(game_state, player, card):
    """On Play: Play cost 2 or less CP Character from hand rested."""
    for c in list(player.hand):
        if 'CP' in (c.card_origin or '') and (getattr(c, 'cost', 0) or 0) <= 2:
            if getattr(c, 'card_type', '') == 'CHARACTER':
                player.hand.remove(c)
                c.is_resting = True
                player.cards_in_play.append(c)
                break
    return True


@register_effect("OP08-093", "on_attack", "[When Attacking] With DON x2, trash 2: K.O. cost 5 or less")
def op08_093_rob_lucci_on_attack(game_state, player, card):
    """When Attacking: With DON x2, trash 2 to K.O. cost 5 or less."""
    if getattr(card, 'attached_don', 0) >= 2 and len(player.hand) >= 2:
        trash_from_hand(player, 2, game_state, card)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 5]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's cost 5 or less to K.O.")
    return True


# --- OP08-098: Atlas ---
@register_effect("OP08-098", "on_play", "[On Play] K.O. 1 of your rested cost 1 or less: K.O. opponent's cost 5 or less")
def op08_098_atlas(game_state, player, card):
    """On Play: K.O. your rested cost 1 or less to K.O. opponent's cost 5 or less."""
    rested_low = [c for c in player.cards_in_play if c.is_resting and (getattr(c, 'cost', 0) or 0) <= 1]
    if rested_low:
        # TODO: Should let player choose which of their rested cards to KO
        target = rested_low[0]
        player.cards_in_play.remove(target)
        player.trash.append(target)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 5]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's cost 5 or less to K.O.")
    return True


# --- OP08-099: Usopp ---
@register_effect("OP08-099", "on_play", "[On Play] Trash 1: K.O. cost 1 or less")
def op08_099_usopp(game_state, player, card):
    """On Play: Trash 1 to K.O. cost 1 or less."""
    if player.hand:
        trash_from_hand(player, 1, game_state, card)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 1]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's cost 1 or less to K.O.")
    return True


# --- OP08-100: Edison ---
@register_effect("OP08-100", "blocker", "[Blocker]")
def op08_100_edison_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP08-100", "on_play", "[On Play] K.O. your Characters: Draw that many")
def op08_100_edison_on_play(game_state, player, card):
    """On Play: K.O. any number of your Characters and draw that many."""
    # K.O. up to 2 Characters (simplified)
    ko_count = 0
    for c in list(player.cards_in_play):
        if c != card and ko_count < 2:
            player.cards_in_play.remove(c)
            player.trash.append(c)
            ko_count += 1
    draw_cards(player, ko_count)
    return True


# --- OP08-101: Charlotte Angel ---
@register_effect("OP08-101", "activate", "[Activate: Main] Trash life: If Big Mom leader, trash opponent's Character")
def op08_101_charlotte_angel(game_state, player, card):
    """Activate: Trash life to trash opponent's Character if Big Mom leader."""
    if getattr(card, 'op08_101_used', False):
        return False
    if player.leader and 'Big Mom Pirates' in (player.leader.card_origin or ''):
        if player.life_cards:
            player.trash.append(player.life_cards.pop())
            opponent = get_opponent(game_state, player)
            if opponent.cards_in_play:
                target = opponent.cards_in_play[0]
                opponent.cards_in_play.remove(target)
                opponent.trash.append(target)
            card.op08_101_used = True
            return True
    return False


# --- OP08-102: Sanji ---
@register_effect("OP08-102", "on_play", "[On Play] If Straw Hat leader, K.O. cost 3 or less, give Character +3000")
def op08_102_sanji(game_state, player, card):
    """On Play: If Straw Hat leader, K.O. cost 3 or less and give Character +3000."""
    if player.leader and 'Straw Hat Crew' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
        # Give power boost first (will happen either way)
        if player.cards_in_play:
            player.cards_in_play[0].power_modifier = getattr(player.cards_in_play[0], 'power_modifier', 0) + 3000
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's cost 3 or less to K.O.")
    return True


# --- OP08-103: Jinbe ---
@register_effect("OP08-103", "on_play", "[On Play] K.O. your cost 1 or less: K.O. opponent's cost 5 or less")
def op08_103_jinbe(game_state, player, card):
    """On Play: K.O. your cost 1 or less to K.O. opponent's cost 5 or less."""
    low_cost = [c for c in player.cards_in_play if c != card and (getattr(c, 'cost', 0) or 0) <= 1]
    if low_cost:
        # TODO: Should let player choose which of their cards to KO
        target = low_cost[0]
        player.cards_in_play.remove(target)
        player.trash.append(target)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 5]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's cost 5 or less to K.O.")
    return True


# --- OP08-104: Chopper ---
@register_effect("OP08-104", "on_play", "[On Play] Draw 1, give Straw Hat +2000 power")
def op08_104_chopper(game_state, player, card):
    """On Play: Draw 1 and give Straw Hat Character +2000 power."""
    draw_cards(player, 1)
    for c in player.cards_in_play:
        if 'Straw Hat Crew' in (c.card_origin or ''):
            c.power_modifier = getattr(c, 'power_modifier', 0) + 2000
            break
    return True


# --- OP08-105: Nami ---
@register_effect("OP08-105", "on_play", "[On Play] If Straw Hat leader, draw 1 and 2 Characters +1000")
def op08_105_nami(game_state, player, card):
    """On Play: If Straw Hat leader, draw 1 and 2 Characters gain +1000."""
    if player.leader and 'Straw Hat Crew' in (player.leader.card_origin or ''):
        draw_cards(player, 1)
        count = 0
        for c in player.cards_in_play:
            if count < 2:
                c.power_modifier = getattr(c, 'power_modifier', 0) + 1000
                count += 1
    return True


# --- OP08-106: Brook ---
@register_effect("OP08-106", "your_turn", "[Your Turn] Give Straw Hat +2000 power")
def op08_106_brook(game_state, player, card):
    """Your Turn: Give Straw Hat Character +2000 power (once per turn simplified)."""
    for c in player.cards_in_play:
        if c != card and 'Straw Hat Crew' in (c.card_origin or ''):
            c.power_modifier = getattr(c, 'power_modifier', 0) + 2000
            break
    return True


# --- OP08-107: Boa Hancock ---
@register_effect("OP08-107", "on_play", "[On Play] K.O. your rested 1 or less cost: K.O. opponent's 4 or less cost")
def op08_107_boa_hancock(game_state, player, card):
    """On Play: K.O. your rested cost 1 or less to K.O. opponent's cost 4 or less."""
    rested_low = [c for c in player.cards_in_play if c.is_resting and (getattr(c, 'cost', 0) or 0) <= 1]
    if rested_low:
        # TODO: Should let player choose which of their rested cards to KO
        target = rested_low[0]
        player.cards_in_play.remove(target)
        player.trash.append(target)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's cost 4 or less to K.O.")
    return True


# --- OP08-108: Monkey.D.Luffy (SR) ---
@register_effect("OP08-108", "on_play", "[On Play] Give all Straw Hat +1000, if 1 or less life +2000 instead")
def op08_108_luffy_sr(game_state, player, card):
    """On Play: Give all Straw Hat +1000, or +2000 if 1 or less life."""
    bonus = 2000 if len(player.life_cards) <= 1 else 1000
    for c in player.cards_in_play:
        if 'Straw Hat Crew' in (c.card_origin or ''):
            c.power_modifier = getattr(c, 'power_modifier', 0) + bonus
    return True


# --- OP08-109: Nico Robin ---
@register_effect("OP08-109", "on_attack", "[When Attacking] With DON x1, give Character +3000")
def op08_109_robin(game_state, player, card):
    """When Attacking: With DON, give your Character +3000."""
    if getattr(card, 'attached_don', 0) >= 1:
        for c in player.cards_in_play:
            if c != card:
                c.power_modifier = getattr(c, 'power_modifier', 0) + 3000
                break
    return True


# --- OP08-110: Roronoa Zoro ---
@register_effect("OP08-110", "on_attack", "[When Attacking] K.O. your cost 1 or less: K.O. opponent's cost 4 or less")
def op08_110_zoro(game_state, player, card):
    """When Attacking: K.O. your cost 1 or less to K.O. opponent's cost 4 or less."""
    low_cost = [c for c in player.cards_in_play if c != card and (getattr(c, 'cost', 0) or 0) <= 1]
    if low_cost:
        # TODO: Should let player choose which of their cards to KO
        target = low_cost[0]
        player.cards_in_play.remove(target)
        player.trash.append(target)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's cost 4 or less to K.O.")
    return True


# --- OP08-116: Yamato (SEC) ---
@register_effect("OP08-116", "on_play", "[On Play] Trash 2: K.O. cost 7 or less and draw 1")
def op08_116_yamato(game_state, player, card):
    """On Play: Trash 2 to K.O. cost 7 or less and draw 1."""
    if len(player.hand) >= 2:
        trash_from_hand(player, 2, game_state, card)
        draw_cards(player, 1)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 7]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's cost 7 or less to K.O.")
    return True


# --- OP08-118: Luffy (SEC) ---
@register_effect("OP08-118", "on_play", "[On Play] K.O. 2 cost 2 or less yours: K.O. opponent's cost 8 or less")
def op08_118_luffy_sec(game_state, player, card):
    """On Play: K.O. 2 of your cost 2 or less to K.O. opponent's cost 8 or less."""
    low_cost = [c for c in player.cards_in_play if c != card and (getattr(c, 'cost', 0) or 0) <= 2]
    if len(low_cost) >= 2:
        # TODO: Should let player choose which of their cards to KO
        for c in low_cost[:2]:
            player.cards_in_play.remove(c)
            player.trash.append(c)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 8]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's cost 8 or less to K.O.")
    return True


# --- OP08-080: Queen (Character) ---
@register_effect("OP08-080", "on_play", "[On Play] Look at 5: reveal up to 1 {Animal Kingdom Pirates} type card (not Queen) to hand.")
def op08_080_queen(game_state, player, card):
    """[On Play] Look at 5: choose up to 1 Animal Kingdom Pirates type card (not Queen) to add to hand."""
    return search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: 'animal kingdom pirates' in (c.card_origin or '').lower() and c.name != 'Queen',
        source_card=card,
        prompt="Look at top 5: choose up to 1 Animal Kingdom Pirates type card (not Queen) to add to hand")


# --- OP08-053: Thank You...for Loving Me!! ---
@register_effect("OP08-053", "on_play", "[Main] If WB leader, look at 3, add WB or Luffy")
def op08_053_thank_you(game_state, player, card):
    """[Main] If Whitebeard Pirates leader, look at 3, add WB or Monkey.D.Luffy."""
    leader_type = (player.leader.card_origin or '').lower() if player.leader else ''
    if 'whitebeard pirates' not in leader_type:
        return False
    return search_top_cards(game_state, player, look_count=3, add_count=1,
        filter_fn=lambda c: ('whitebeard pirates' in (c.card_origin or '').lower()
                             or 'monkey.d.luffy' in (c.name or '').lower()),
        source_card=card,
        prompt="Look at top 3: choose 1 Whitebeard Pirates or Monkey.D.Luffy card to add to hand")


# --- OP08-110: Wyper ---
@register_effect("OP08-110", "on_play", "[On Play] Look at 5, add Upper Yard, play from hand")
def op08_110_wyper(game_state, player, card):
    """[On Play] Look at 5, add Upper Yard to hand, then play Upper Yard from hand."""
    return search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: 'upper yard' in (c.name or '').lower(),
        source_card=card,
        prompt="Look at top 5: choose 1 [Upper Yard] to add to hand (then you may play it)")
