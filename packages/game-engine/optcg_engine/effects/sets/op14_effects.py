"""
Hardcoded effects for OP14 cards.
"""

from ..effect_registry import (
    add_don_from_deck, add_power_modifier, check_leader_type,
    create_ko_choice, create_multi_target_choice, create_own_character_choice,
    create_power_effect_choice, create_target_choice, draw_cards, get_opponent, give_don_to_card,
    register_effect, search_top_cards, trash_from_hand,
)


# --- OP14-041: Boa Hancock (Leader) ---
@register_effect("OP14-041", "ON_CHARACTER_PLAY", "Draw 1 when you play a Character")
def boa_hancock_leader_play(game_state, player, card):
    draw_cards(player, 1)
    return True


# --- OP14-120: Crocodile ---
@register_effect("OP14-120", "ON_PLAY", "Opponent's cost 9 or less cannot attack, draw if condition")
def crocodile_op14_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 9]
    # Check for cost 0 or cost 8+ character (draw regardless of target choice)
    has_condition = any((getattr(c, 'cost', 0) or 0) == 0 or (getattr(c, 'cost', 0) or 0) >= 8
                       for c in opponent.cards_in_play)
    if has_condition:
        draw_cards(player, 1)
    if targets:
        return create_target_choice(
            game_state, player, targets,
            callback_action="cannot_attack_target",
            source_card=card,
            prompt="Choose opponent's cost 9 or less Character that cannot attack this turn"
        )
    return True


# --- OP14-060: Donquixote Doflamingo (Leader) ---
@register_effect("OP14-060", "ON_OPPONENT_ATTACK", "DON -1: Change attack target")
def doflamingo_leader_effect(game_state, player, card):
    # Return DON to deck as cost
    active_don = [d for d in player.don_pool if not d.is_resting]
    if active_don and hasattr(player, 'don_deck'):
        don = active_don[0]
        player.don_pool.remove(don)
        player.don_deck.append(don)
        # Change attack target logic would be handled by game engine
        return True
    return False


# --- OP14-054: Fisher Tiger ---
@register_effect("OP14-054", "ON_PLAY", "If Leader is Fish-Man, draw 3")
def fisher_tiger_on_play(game_state, player, card):
    if player.leader and 'fish-man' in (player.leader.card_origin or '').lower():
        draw_cards(player, 3)
        return True
    return False


@register_effect("OP14-054", "END_OF_TURN", "Trash until 5 cards in hand")
def fisher_tiger_end(game_state, player, card):
    while len(player.hand) > 5:
        trash_from_hand(player, 1, game_state, card)
    return True


# --- OP14-104: Gecko Moria ---
@register_effect("OP14-104", "ON_PLAY", "Play Thriller Bark cost 4 or less from trash or add to Life")
def gecko_moria_effect(game_state, player, card):
    thriller = [c for c in player.trash
               if 'thriller bark pirates' in (c.card_origin or '').lower()
               and (getattr(c, 'cost', 0) or 0) <= 4
               and getattr(c, 'card_type', '') == 'CHARACTER']
    if thriller:
        char = thriller[0]
        player.trash.remove(char)
        # Play it
        game_state.play_card_to_field_by_effect(player, char)
        return True
    return False


# --- OP14-105: Gorgon Sisters ---
@register_effect("OP14-105", "MAIN", "Reveal 3 Amazon Lily/Kuja cards: Give DON to all chars")
def gorgon_sisters_effect(game_state, player, card):
    amazon_kuja = [c for c in player.hand
                  if 'amazon lily' in (c.card_origin or '').lower()
                  or 'kuja pirates' in (c.card_origin or '').lower()]
    if len(amazon_kuja) >= 3:
        rested_don = [d for d in player.don_pool if d.is_resting]
        for char in player.cards_in_play:
            if rested_don:
                give_don_to_card(player, char, 1, rested_only=True)
        if player.leader and rested_don:
            give_don_to_card(player, player.leader, 1, rested_only=True)
        return True
    return False


# --- OP14-024: Kin'emon ---
@register_effect("OP14-024", "ON_PLAY", "Set 3 DON active, cannot play chars this turn")
def kinemon_on_play(game_state, player, card):
    rested_don = [d for d in player.don_pool if d.is_resting][:3]
    for don in rested_don:
        don.is_resting = False
    player.cannot_play_chars_this_turn = True
    return True


@register_effect("OP14-024", "ON_KO", "Rest 1 opponent's card")
def kinemon_ko(game_state, player, card):
    opponent = get_opponent(game_state, player)
    active = [c for c in opponent.cards_in_play if not c.is_resting]
    if active:
        active[0].is_resting = True
        return True
    return False


# --- OP14-092: Mr.3(Galdino) ---
@register_effect("OP14-092", "WOULD_BE_KO", "Place 3 from trash at bottom instead of KO")
def mr3_effect(game_state, player, card):
    if len(player.trash) >= 3:
        for _ in range(3):
            if player.trash:
                card_to_place = player.trash.pop(0)
                player.deck.append(card_to_place)
        return True  # Prevent KO
    return False


# --- OP14-033: Perona ---
@register_effect("OP14-033", "ON_PLAY", "2 opponent's cost 5 or less cannot be rested")
def perona_on_play(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 5]
    if targets:
        return create_target_choice(
            game_state, player, targets,
            callback_action="perona_cannot_rest",
            source_card=card,
            prompt="Choose up to 2 opponent's cost 5 or less Characters that cannot be rested",
            multi_select=True,
            max_select=2
        )
    return False


@register_effect("OP14-033", "ON_KO", "Rest 1: Play green cost 5 or less from hand")
def perona_ko(game_state, player, card):
    active = [c for c in player.cards_in_play if not c.is_resting]
    green_chars = [c for c in player.hand
                  if 'green' in (getattr(c, 'colors', '') or '').lower()
                  and (getattr(c, 'cost', 0) or 0) <= 5
                  and getattr(c, 'card_type', '') == 'CHARACTER']
    if active and green_chars:
        active_snap = list(active)
        def perona_ko_cb(selected: list) -> None:
            from ..effect_registry import create_play_from_hand_choice
            target_idx = int(selected[0]) if selected else -1
            if 0 <= target_idx < len(active_snap):
                target = active_snap[target_idx]
                target.is_resting = True
                game_state._log(f"{target.name} was rested")
            playable = [c for c in player.hand
                        if 'green' in (getattr(c, 'colors', '') or '').lower()
                        and (getattr(c, 'cost', 0) or 0) <= 5
                        and getattr(c, 'card_type', '') == 'CHARACTER']
            if playable:
                create_play_from_hand_choice(game_state, player, playable, source_card=None,
                                             prompt="Choose green cost 5 or less Character to play")
        return create_target_choice(
            game_state, player, active,
            callback=perona_ko_cb,
            source_card=card,
            prompt="Choose your Character to rest (then play green cost 5 or less from hand)"
        )
    return False


# =============================================================================
# ADDITIONAL PLACEHOLDER CARDS (18 remaining)
# =============================================================================

# --- OP14-041: Boa Hancock ---
@register_effect("OP14-041", "ON_OPPONENT_PLAY", "Draw 1 card when you play a Character on opponent's turn")
def boa_hancock_op14_effect(game_state, player, card):
    # Draw on opponent's turn when playing a character
    draw_cards(player, 1)
    return True


@register_effect("OP14-041", "ON_YOUR_CHARACTER_KO", "Add to life when 5000+ power character KO'd")
def boa_hancock_op14_ko_effect(game_state, player, card):
    if getattr(card, 'attached_don', 0) >= 1:
        # When 5000+ power character KO'd, this triggers
        draw_cards(player, 1)
        return True
    return False


# --- OP14-105: Gorgon Sisters ---
@register_effect("OP14-105", "ACTIVATE_MAIN", "Give Leader and Characters rested DON each")
def gorgon_sisters_effect(game_state, player, card):
    # Check for 3 Amazon Lily/Kuja Pirates cards in hand (simplified)
    type_cards = [c for c in player.hand if 'amazon lily' in (c.card_origin or '').lower() or 'kuja pirates' in (c.card_origin or '').lower()]
    if len(type_cards) >= 3:
        # Give rested DON to each character
        rested_don = [d for d in player.don_pool if d.is_resting]
        targets = [player.leader] + player.cards_in_play
        for target in targets[:len(rested_don)]:
            if rested_don:
                don = rested_don.pop(0)
                target.attached_don = getattr(target, 'attached_don', 0) + 1
        return True
    return False


# --- OP14-092: Mr.3(Galdino) ---
@register_effect("OP14-092", "ON_WOULD_BE_KO", "Place 3 cards from trash at bottom instead of being KO'd")
def mr3_effect(game_state, player, card):
    if len(player.trash) >= 3:
        # Place 3 cards from trash at bottom of deck
        for _ in range(3):
            if player.trash:
                card_to_place = player.trash.pop(0)
                player.deck.append(card_to_place)
        # Prevent KO by returning True
        return True  # Signals KO prevention
    return False


# --- OP14-042: Arlong ---
@register_effect("OP14-042", "ON_PLAY", "If Leader is Fish-Man, look at 4, add cost 2+ to hand")
def op14_042_arlong(game_state, player, card):
    if check_leader_type(player, "Fish-Man"):
        top4 = player.deck[:4]
        valid = [c for c in top4 if (getattr(c, 'cost', 0) or 0) >= 2]
        if valid:
            to_add = valid[0]
            player.deck.remove(to_add)
            player.hand.append(to_add)
        # Place rest at bottom
        for c in top4:
            if c in player.deck:
                player.deck.remove(c)
                player.deck.append(c)
    return True


# =============================================================================
# MORE LEADER CONDITION CARDS - The Seven Warlords
# =============================================================================

# --- OP14-112: Boa Hancock ---
@register_effect("OP14-112", "ON_PLAY", "If Leader is Seven Warlords, add to life, add opponent's to life too")
def op14_112_hancock(game_state, player, card):
    if check_leader_type(player, "The Seven Warlords of the Sea"):
        # Add to your life
        if player.deck:
            player.life_cards.append(player.deck.pop(0))
        # Add to opponent's life (defensive)
        opponent = get_opponent(game_state, player)
        if opponent.deck:
            opponent.life_cards.append(opponent.deck.pop(0))
    return True


# --- OP14-107: Shakuyaku ---
@register_effect("OP14-107", "ON_PLAY", "If opponent has 3 or less life, draw 2 and trash 2")
def op14_107_shakuyaku(game_state, player, card):
    """On Play: If opponent has 3 or less life, draw 2 and trash 2."""
    opponent = get_opponent(game_state, player)
    if len(opponent.life_cards) <= 3:
        draw_cards(player, 2)
        trash_from_hand(player, 2, game_state, card)
        return True
    return False


# --- OP14-096: Ground Death ---
@register_effect("OP14-096", "MAIN", "Rest 2 DON: Negate opponent's cost 5 or less effects")
def op14_096_ground_death_main(game_state, player, card):
    """Main: Rest 2 DON, negate opponent's cost 5 or less char effects."""
    active_don = [d for d in player.don_pool if not d.is_resting]
    if len(active_don) >= 2:
        active_don[0].is_resting = True
        active_don[1].is_resting = True
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 5]
        if targets:
            return create_target_choice(
                game_state, player, targets,
                callback_action="negate_effects",
                source_card=card,
                prompt="Choose opponent's cost 5 or less Character to negate effects"
            )
        return True
    return False


@register_effect("OP14-096", "COUNTER", "If 10+ trash, +4000 power")
def op14_096_ground_death_counter(game_state, player, card):
    """Counter: If 10+ trash, +4000 power."""
    if check_trash_count(player, 10):
        target = player.leader if player.leader else (player.cards_in_play[0] if player.cards_in_play else None)
        if target:
            add_power_modifier(target, 4000)
            return True
    return False


# --- OP14-001: Trafalgar Law (Leader) ---
@register_effect("OP14-001", "activate", "[Activate: Main] Swap base power of 2 Supernova/Heart Pirates chars")
def op14_001_law_leader(game_state, player, card):
    """Once Per Turn: Select 2 Supernovas or Heart Pirates Characters, swap their base power."""
    if hasattr(card, 'op14_001_used') and card.op14_001_used:
        return False
    targets = [c for c in player.cards_in_play
               if 'supernovas' in (c.card_origin or '').lower()
               or 'heart pirates' in (c.card_origin or '').lower()]
    if len(targets) >= 2:
        card.op14_001_used = True
        targets_snap = list(targets)
        def swap_power_cb(selected: list) -> None:
            indices = [int(s) for s in selected if s.isdigit()][:2]
            if len(indices) == 2:
                a = targets_snap[indices[0]] if 0 <= indices[0] < len(targets_snap) else None
                b = targets_snap[indices[1]] if 0 <= indices[1] < len(targets_snap) else None
                if a and b:
                    a_base = getattr(a, 'base_power', a.power or 0)
                    b_base = getattr(b, 'base_power', b.power or 0)
                    a.power = b_base + getattr(a, 'power_modifier', 0)
                    b.power = a_base + getattr(b, 'power_modifier', 0)
                    a.base_power = b_base
                    b.base_power = a_base
                    game_state._log(f"Swapped base power: {a.name} ↔ {b.name}")
        return create_multi_target_choice(
            game_state, player, targets, count=2,
            callback=swap_power_cb,
            source_card=card,
            prompt="Choose 2 Supernovas/Heart Pirates Characters to swap base power"
        )
    return False


# --- OP14-020: Dracule Mihawk (Leader) ---
@register_effect("OP14-020", "continuous", "If opponent Leader has Slash, +1000 power")
def op14_020_mihawk_continuous(game_state, player, card):
    """If opponent's Leader has Slash attribute, this Leader gains +1000 power."""
    opponent = get_opponent(game_state, player)
    if opponent.leader and 'slash' in (getattr(opponent.leader, 'attribute', '') or '').lower():
        card.power_modifier = getattr(card, 'power_modifier', 0) + 1000
    return True


@register_effect("OP14-020", "activate", "[Activate: Main] Rest 1 card: Give char +2000 until end of opponent's turn")
def op14_020_mihawk_activate(game_state, player, card):
    """Once Per Turn, Rest 1 of your cards: Give 1 Character +2000 until end of opponent's turn."""
    if hasattr(card, 'op14_020_used') and card.op14_020_used:
        return False
    active_cards = [c for c in player.cards_in_play if not c.is_resting]
    if active_cards and player.cards_in_play:
        active_cards[0].is_resting = True
        card.op14_020_used = True
        return create_power_effect_choice(game_state, player, player.cards_in_play,
                                          2000, source_card=card,
                                          prompt="Choose a Character to give +2000 power")
    return False


# --- OP14-040: Jinbe (Leader) ---
@register_effect("OP14-040", "activate", "[Activate: Main] Trash 1: Give 2 rested DON to Fish-Man/Merfolk")
def op14_040_jinbe_leader(game_state, player, card):
    """Trash 1 from hand: Give up to 2 rested DON to 1 Fish-Man or Merfolk Leader or Character."""
    if player.hand:
        trash_from_hand(player, 1, game_state, card)
        rested_don = player.don_pool.count("rested")
        fish_chars = [c for c in player.cards_in_play
                      if 'fish-man' in (c.card_origin or '').lower()
                      or 'merfolk' in (c.card_origin or '').lower()]
        if fish_chars and rested_don:
            target = fish_chars[0]
            given = min(2, len(rested_don))
            target.attached_don = getattr(target, 'attached_don', 0) + given
        return True
    return False


# --- OP14-041: Boa Hancock (Leader) - already exists, skip ---

# --- OP14-060: Donquixote Doflamingo (Leader) - already exists, skip ---

# --- OP14-079: Crocodile (Leader) ---
@register_effect("OP14-079", "continuous", "Opponent chars cannot be removed by your effects")
def op14_079_croc_continuous(game_state, player, card):
    """All opponent's Characters cannot be removed from the field by your effects."""
    player.cannot_remove_opponent_chars = True
    return True


@register_effect("OP14-079", "activate", "[Activate: Main] K.O. your char: K.O. opponent char same cost or less")
def op14_079_croc_activate(game_state, player, card):
    """Once Per Turn: K.O. 1 of your Characters, K.O. opponent's Character with same or less cost."""
    if hasattr(card, 'op14_079_used') and card.op14_079_used:
        return False
    if player.cards_in_play:
        card.op14_079_used = True
        own_snap = list(player.cards_in_play)
        def croc_cb(selected: list) -> None:
            target_idx = int(selected[0]) if selected else -1
            ko_cost = 0
            if 0 <= target_idx < len(own_snap):
                target = own_snap[target_idx]
                ko_cost = getattr(target, 'cost', 0) or 0
                if target in player.cards_in_play:
                    player.cards_in_play.remove(target)
                    player.trash.append(target)
                    game_state._log(f"{target.name} was K.O.'d (cost {ko_cost})")
            opponent = get_opponent(game_state, player)
            opp_targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= ko_cost]
            if opp_targets:
                create_ko_choice(game_state, player, opp_targets, source_card=None,
                                prompt=f"Choose opponent's cost {ko_cost} or less Character to K.O.")
        return create_own_character_choice(game_state, player, player.cards_in_play,
                                           callback=croc_cb, source_card=card,
                                           prompt="Choose your Character to K.O.")
    return False


# --- OP14-080: Gecko Moria (Leader) ---
@register_effect("OP14-080", "activate", "[Activate: Main] K.O. Thriller Bark char: All +1000 power")
def op14_080_moria_leader(game_state, player, card):
    """Once Per Turn: K.O. 1 Thriller Bark Pirates Character, Leader and all Characters gain +1000 power."""
    if hasattr(card, 'op14_080_used') and card.op14_080_used:
        return False
    thriller_chars = [c for c in player.cards_in_play
                      if 'thriller bark pirates' in (c.card_origin or '').lower()]
    if thriller_chars:
        to_ko = thriller_chars[0]
        player.cards_in_play.remove(to_ko)
        player.trash.append(to_ko)
        if player.leader:
            player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 1000
        for char in player.cards_in_play:
            char.power_modifier = getattr(char, 'power_modifier', 0) + 1000
        card.op14_080_used = True
        return True
    return False


# --- OP14-003: Luffy ---
@register_effect("OP14-003", "on_play", "[On Play] K.O. cost 6 or less")
def op14_003_luffy(game_state, player, card):
    """On Play: K.O. opponent's cost 6 or less."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 6]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                               prompt="Choose opponent's cost 6 or less to K.O.")
    return True


# --- OP14-022: Garp ---
@register_effect("OP14-022", "on_play", "[On Play] If Navy leader, K.O. cost 5 or less")
def op14_022_garp(game_state, player, card):
    """On Play: If Navy leader, K.O. cost 5 or less."""
    if player.leader and 'Navy' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 5]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's cost 5 or less to K.O.")
    return True


# --- OP14-040: Sanji ---
@register_effect("OP14-040", "on_play", "[On Play] If Straw Hat leader, K.O. cost 4 or less")
def op14_040_sanji(game_state, player, card):
    """On Play: If Straw Hat leader, K.O. cost 4 or less."""
    if player.leader and 'Straw Hat Crew' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's cost 4 or less to K.O.")
    return True


# --- OP14-060: Nami ---
@register_effect("OP14-060", "on_play", "[On Play] If Straw Hat leader, draw 2")
def op14_060_nami(game_state, player, card):
    """On Play: If Straw Hat leader, draw 2."""
    if player.leader and 'Straw Hat Crew' in (player.leader.card_origin or ''):
        draw_cards(player, 2)
    return True


# --- OP14-010: Basil Hawkins ---
@register_effect("OP14-010", "on_ko", "[On K.O.] Look at 5, play Supernovas power 2000 or less (not self)")
def op14_010_hawkins(game_state, player, card):
    return search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: ('supernovas' in (c.card_origin or '').lower()
                             and c.card_type == 'CHARACTER'
                             and (c.power or 0) <= 2000
                             and 'basil hawkins' not in (c.name or '').lower()),
        source_card=card, play_to_field=True,
        prompt="Look at top 5: choose 1 Supernovas Character (power 2000 or less) to play")


# --- OP14-013: Monkey.D.Luffy ---
@register_effect("OP14-013", "on_play", "[On Play] Look at 5, add Supernovas (not Luffy)")
def op14_013_luffy(game_state, player, card):
    return search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: ('supernovas' in (c.card_origin or '').lower()
                             and 'monkey.d.luffy' not in (c.name or '').lower()),
        source_card=card,
        prompt="Look at top 5: choose 1 Supernovas card (not Luffy) to add to hand")


# --- OP14-019: I Have a Plan to Take Down One of the Four Emperors!! ---
@register_effect("OP14-019", "on_play", "[Main] Look at 4, add Supernovas/SHC Character")
def op14_019_plan(game_state, player, card):
    return search_top_cards(game_state, player, look_count=4, add_count=1,
        filter_fn=lambda c: (c.card_type == 'CHARACTER'
                             and ('supernovas' in (c.card_origin or '').lower()
                                  or 'straw hat crew' in (c.card_origin or '').lower())),
        source_card=card,
        prompt="Look at top 4: choose 1 Supernovas or Straw Hat Crew Character to add to hand")


# --- OP14-097: Hurry Up and Make Me the Pirate King! ---
@register_effect("OP14-097", "on_play", "[Main] Look at 3, add Thriller Bark Pirates (not self), trash rest")
def op14_097_hurry(game_state, player, card):
    return search_top_cards(game_state, player, look_count=3, add_count=1,
        filter_fn=lambda c: ('thriller bark pirates' in (c.card_origin or '').lower()
                             and 'hurry up and make me the pirate king' not in (c.name or '').lower()),
        source_card=card, trash_rest=True,
        prompt="Look at top 3: choose 1 Thriller Bark Pirates card to add to hand (rest trashed)")


# --- OP14-099: Disappointed? ---
@register_effect("OP14-099", "on_play", "[Main] Look at 3, add Baroque Works (not self), trash rest")
def op14_099_disappointed(game_state, player, card):
    return search_top_cards(game_state, player, look_count=3, add_count=1,
        filter_fn=lambda c: ('baroque works' in (c.card_origin or '').lower()
                             and 'disappointed' not in (c.name or '').lower()),
        source_card=card, trash_rest=True,
        prompt="Look at top 3: choose 1 Baroque Works card to add to hand (rest trashed)")


# --- OP14-100: Absalom ---
@register_effect("OP14-100", "on_ko", "[On K.O.] Look at 3, add Thriller Bark Pirates")
def op14_100_absalom(game_state, player, card):
    return search_top_cards(game_state, player, look_count=3, add_count=1,
        filter_fn=lambda c: 'thriller bark pirates' in (c.card_origin or '').lower(),
        source_card=card,
        prompt="Look at top 3: choose 1 Thriller Bark Pirates card to add to hand")


# --- OP14-113: Marguerite ---
@register_effect("OP14-113", "on_play", "[On Play] Look at 5, add Amazon Lily/Kuja Pirates")
def op14_113_marguerite(game_state, player, card):
    return search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: ('amazon lily' in (c.card_origin or '').lower()
                             or 'kuja pirates' in (c.card_origin or '').lower()),
        source_card=card,
        prompt="Look at top 5: choose 1 Amazon Lily or Kuja Pirates card to add to hand")


# --- OP14-067: Dellinger ---
@register_effect("OP14-067", "on_ko", "[On K.O.] Add DON rested, look at 5, add Donquixote Pirates")
def op14_067_dellinger(game_state, player, card):
    """[On K.O.] Add up to 1 DON from DON deck (rested), then look at 5, add 1 Donquixote Pirates card."""
    # Add 1 DON rested
    if hasattr(player, 'don_deck') and player.don_deck:
        don = player.don_deck.pop(0)
        don.is_resting = True
        player.don_pool.append(don)
    return search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: 'donquixote pirates' in (c.card_origin or '').lower(),
        source_card=card,
        prompt="Dellinger: Look at top 5, choose 1 Donquixote Pirates card to add to hand")


# --- OP14-087: Miss.Valentine(Mikita) ---
@register_effect("OP14-087", "on_play", "[On Play] If BW leader, look at 4, add Baroque Works (not self), trash rest")
def op14_087_miss_valentine(game_state, player, card):
    """[On Play] If Baroque Works leader, look at 4, add 1 BW (not self), trash rest."""
    leader_type = (player.leader.card_origin or '').lower() if player.leader else ''
    if 'baroque works' not in leader_type:
        return False
    return search_top_cards(game_state, player, look_count=4, add_count=1,
        filter_fn=lambda c: ('baroque works' in (c.card_origin or '').lower()
                             and 'miss.valentine' not in (c.name or '').lower()),
        source_card=card, trash_rest=True,
        prompt="Miss.Valentine: Look at top 4, choose 1 Baroque Works card to add to hand (rest trashed)")
