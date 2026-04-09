"""
Hardcoded effects for OP10 cards.
"""

from ..hardcoded import (
    add_don_from_deck, add_power_modifier,
    create_bottom_deck_choice, create_ko_choice, create_own_character_choice,
    create_play_from_hand_choice, create_rest_choice, create_return_to_hand_choice,
    create_target_choice, draw_cards, get_opponent, register_effect, search_top_cards,
    trash_from_hand,
)


# --- OP10-103: Capone Bege ---
@register_effect("OP10-103", "ON_PLAY", "Swap Life card with Supernovas Character from hand")
def capone_bege_effect(game_state, player, card):
    if player.life_cards:
        supernovas = [c for c in player.hand
                     if 'supernovas' in (c.card_origin or '').lower()
                     and getattr(c, 'card_type', '') == 'CHARACTER']
        if supernovas:
            # Add life to hand
            life = player.life_cards.pop()
            player.hand.append(life)
            # Add character to life
            char = supernovas[0]
            player.hand.remove(char)
            player.life_cards.append(char)
            return True
    return False


# --- OP10-029: Dracule Mihawk ---
@register_effect("OP10-029", "ON_PLAY", "If 2+ rested chars, set ODYSSEY cost 5 or less active")
def mihawk_op10_effect(game_state, player, card):
    rested = [c for c in player.cards_in_play if c.is_resting]
    if len(rested) >= 2:
        odyssey = [c for c in rested
                  if 'odyssey' in (c.card_origin or '').lower()
                  and (getattr(c, 'cost', 0) or 0) <= 5]
        if odyssey:
            odyssey[0].is_resting = False
            return True
    return False


# --- OP10-107: Jewelry Bonney ---
@register_effect("OP10-107", "ON_PLAY", "Swap Life with Supernovas cost 5 from hand")
def jewelry_bonney_effect(game_state, player, card):
    if player.life_cards:
        supernovas = [c for c in player.hand
                     if 'supernovas' in (c.card_origin or '').lower()
                     and (getattr(c, 'cost', 0) or 0) == 5
                     and getattr(c, 'card_type', '') == 'CHARACTER']
        if supernovas:
            life = player.life_cards.pop()
            player.hand.append(life)
            char = supernovas[0]
            player.hand.remove(char)
            player.life_cards.append(char)
            return True
    return False


# --- OP10-074: Pica ---
@register_effect("OP10-074", "ON_WOULD_BE_KO", "If would be KO'd by effect, rest 2 DON instead")
def pica_protect_effect(game_state, player, card):
    """Prevent KO by resting 2 active DON instead."""
    active_don = [d for d in player.don_pool if not d.is_resting]
    if len(active_don) >= 2:
        active_don[0].is_resting = True
        active_don[1].is_resting = True
        return True  # Prevents the KO
    return False


# --- OP10-096: There's No Longer Any Need for the Seven Warlords of the Sea!!! ---
@register_effect("OP10-096", "MAIN", "KO opponent's Seven Warlords cost 8 or less")
def seven_warlords_ko_effect(game_state, player, card):
    """KO up to 1 opponent's Seven Warlords character with cost 8 or less."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
              if 'seven warlords' in (c.card_origin or '').lower()
              and (getattr(c, 'cost', 0) or 0) <= 8]
    if targets:
        return create_ko_choice(
            game_state, player, targets, source_card=card,
            prompt="Choose opponent's Seven Warlords cost 8 or less to KO"
        )
    return False


# =============================================================================
# MORE LEADER CONDITION CARDS - Donquixote Pirates
# =============================================================================

# --- OP10-076: Baby 5 ---
@register_effect("OP10-076", "ON_PLAY", "Trash 1: If Leader is Donquixote Pirates, add DON active")
def op10_076_baby5(game_state, player, card):
    if player.hand:
        trash_from_hand(player, 1, game_state, card)
        if check_leader_type(player, "Donquixote Pirates"):
            add_don_from_deck(player, 1, set_active=True)
    return True


# --- OP10-020: Gum-Gum UFO ---
@register_effect("OP10-020", "MAIN", "-4000 power, +1000 power if 2 or less life")
def op10_020_gum_gum_ufo(game_state, player, card):
    """Main: -4000 power to opponent, +1000 to self if 2 or less life."""
    opponent = get_opponent(game_state, player)
    if opponent.cards_in_play:
        add_power_modifier(opponent.cards_in_play[0], -4000)
    if check_life_count(player, 2):
        target = player.leader if player.leader else (player.cards_in_play[0] if player.cards_in_play else None)
        if target:
            add_power_modifier(target, 1000)
    return True


# --- OP10-112: Eustass"Captain"Kid ---
@register_effect("OP10-112", "ON_PLAY", "Rest this to trash opponent's top life")
def op10_112_kid_on_play(game_state, player, card):
    """On Play: Rest this to trash opponent's top life."""
    card.is_resting = True
    opponent = get_opponent(game_state, player)
    if opponent.life_cards:
        life = opponent.life_cards.pop()
        opponent.trash.append(life)
    return True


@register_effect("OP10-112", "END_OF_TURN", "If opponent has 2 or less life, draw 1 trash 1")
def op10_112_kid_end(game_state, player, card):
    """End of Turn: If opponent has 2 or less life, draw 1 and trash 1."""
    opponent = get_opponent(game_state, player)
    if len(opponent.life_cards) <= 2:
        draw_cards(player, 1)
        trash_from_hand(player, 1, game_state, card)
        return True
    return False


# --- OP10-117: ROOM ---
@register_effect("OP10-117", "COUNTER", "If 1 or less life, +3000 power and set cost 5 or less active")
def op10_117_room(game_state, player, card):
    """Counter: If 1 or less life, +3000 power and set cost 5 or less active."""
    if check_life_count(player, 1):
        target = player.leader if player.leader else (player.cards_in_play[0] if player.cards_in_play else None)
        if target:
            add_power_modifier(target, 3000)
        # Set cost 5 or less active
        rested = [c for c in player.cards_in_play
                 if c.is_resting and (getattr(c, 'cost', 0) or 0) <= 5]
        if rested:
            rested[0].is_resting = False
        return True
    return False


# --- OP10-085: Jesus Burgess ---
@register_effect("OP10-085", "CONTINUOUS", "If DONx1 and 8+ trash, gain Rush")
def op10_085_burgess(game_state, player, card):
    """Continuous: If DONx1 and 8+ trash, this gains Rush."""
    if getattr(card, 'attached_don', 0) >= 1 and len(player.trash) >= 8:
        card.has_rush = True
        return True
    return False


# --- OP10-097: Gum-Gum Rhino Schneider ---
@register_effect("OP10-097", "MAIN", "Dressrosa +2000 power, gain Banish if 10+ trash")
def op10_097_rhino_schneider(game_state, player, card):
    """Main: Dressrosa char +2000 power, gain Banish if 10+ trash."""
    dressrosa = [c for c in player.cards_in_play
                 if 'dressrosa' in (c.card_origin or '').lower()]
    if dressrosa:
        banish = len(player.trash) >= 10
        dressrosa_snap = list(dressrosa)
        def rhino_cb(selected: list) -> None:
            target_idx = int(selected[0]) if selected else -1
            if 0 <= target_idx < len(dressrosa_snap):
                target = dressrosa_snap[target_idx]
                target.power_modifier = getattr(target, 'power_modifier', 0) + 2000
                game_state._log(f"{target.name} gains +2000 power")
                if banish:
                    target.has_banish = True
                    game_state._log(f"{target.name} gains Banish this turn")
        return create_target_choice(
            game_state, player, dressrosa,
            callback=rhino_cb,
            source_card=card,
            prompt="Choose your Dressrosa Character to give +2000 power" + (" and Banish" if banish else "")
        )
    return False


# --- OP10-002: Caesar Clown (Leader) ---
@register_effect("OP10-002", "WHEN_ATTACKING", "Return Punk Hazard cost 2+ to hand: KO 4000 power or less")
def op10_002_caesar(game_state, player, card):
    """When Attacking (DONx2): Return Punk Hazard cost 2+ to hand, KO 4000 power or less."""
    if getattr(card, 'attached_don', 0) >= 2:
        punk_hazard = [c for c in player.cards_in_play
                      if 'punk hazard' in (c.card_origin or '').lower()
                      and (getattr(c, 'cost', 0) or 0) >= 2]
        if punk_hazard:
            ph_snap = list(punk_hazard)
            def caesar_cb(selected: list) -> None:
                target_idx = int(selected[0]) if selected else -1
                if 0 <= target_idx < len(ph_snap):
                    target = ph_snap[target_idx]
                    if target in player.cards_in_play:
                        player.cards_in_play.remove(target)
                        player.hand.append(target)
                        game_state._log(f"{target.name} returned to hand")
                opponent = get_opponent(game_state, player)
                ko_targets = [c for c in opponent.cards_in_play
                              if (getattr(c, 'power', 0) or 0) + getattr(c, 'power_modifier', 0) <= 4000]
                if ko_targets:
                    create_ko_choice(game_state, player, ko_targets, source_card=None,
                                     prompt="Choose opponent's 4000 power or less Character to KO")
            return create_own_character_choice(
                game_state, player, punk_hazard,
                source_card=card,
                callback=caesar_cb,
                prompt="Choose Punk Hazard cost 2+ to return to hand (then KO 4000 power or less)"
            )
    return False


# --- OP10-047: Koala ---
@register_effect("OP10-047", "WHEN_ATTACKING", "Return Rev Army cost 3+ to hand: +3000 power")
def op10_047_koala(game_state, player, card):
    """When Attacking: Return Revolutionary Army cost 3+ to hand, +3000 power."""
    rev_army = [c for c in player.cards_in_play
                if 'revolutionary army' in (c.card_origin or '').lower()
                and (getattr(c, 'cost', 0) or 0) >= 3
                and c != card]
    if rev_army:
        add_power_modifier(card, 3000)
        return create_own_character_choice(
            game_state, player, rev_army,
            source_card=card,
            callback_action="return_to_hand",
            prompt="Choose Revolutionary Army cost 3+ to return to hand"
        )
    return False


# --- OP10-001: Smoker (Leader) ---
@register_effect("OP10-001", "opponent_turn", "[Opponent's Turn] Navy/Punk Hazard chars +1000")
def op10_001_smoker_opp_turn(game_state, player, card):
    """Opponent's Turn: All Navy or Punk Hazard Characters gain +1000 power."""
    for char in player.cards_in_play:
        types = (char.card_origin or '').lower()
        if 'navy' in types or 'punk hazard' in types:
            char.power_modifier = getattr(char, 'power_modifier', 0) + 1000
    return True


@register_effect("OP10-001", "activate", "[Activate: Main] If char with counter, rest opponent cost 3-")
def op10_001_smoker_activate(game_state, player, card):
    """Once Per Turn: If you have a Character with Counter, rest opponent's cost 3 or less."""
    if hasattr(card, 'op10_001_used') and card.op10_001_used:
        return False
    chars_with_counter = [c for c in player.cards_in_play if getattr(c, 'counter', 0)]
    if chars_with_counter:
        card.op10_001_used = True
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play
                   if not c.is_resting and (getattr(c, 'cost', 0) or 0) <= 3]
        if targets:
            return create_rest_choice(game_state, player, targets, source_card=card,
                                     prompt="Choose opponent's cost 3 or less to rest")
        return True
    return False


# --- OP10-002: Caesar Clown (Leader) - already exists, skip ---

# --- OP10-003: Sugar (Leader) ---
@register_effect("OP10-003", "end_of_turn", "[End of Turn] If Donquixote 6000+ power, set 1 DON active")
def op10_003_sugar_eot(game_state, player, card):
    """End of Your Turn: If you have a Donquixote Pirates Character with 6000+ power, set 1 DON active."""
    donquixote_6000 = [c for c in player.cards_in_play
                        if 'donquixote pirates' in (c.card_origin or '').lower()
                        and (getattr(c, 'power', 0) or 0) + getattr(c, 'power_modifier', 0) >= 6000]
    if donquixote_6000:
        rested_don = player.don_pool.count("rested")
        if rested_don:
            rested_don[0].is_resting = False
        return True
    return False


# --- OP10-022: Trafalgar Law (Leader) ---
@register_effect("OP10-022", "activate", "[DON!! x1] If chars cost 5+, return 1 char: Play cost 4 or less")
def op10_022_law_leader(game_state, player, card):
    """DON x1, Once Per Turn: If total character cost 5+, return 1 char to hand, play cost 4 or less from hand."""
    if getattr(card, 'attached_don', 0) >= 1:
        if hasattr(card, 'op10_022_used') and card.op10_022_used:
            return False
        total_cost = sum((getattr(c, 'cost', 0) or 0) for c in player.cards_in_play)
        if total_cost >= 5 and player.cards_in_play:
            to_return = player.cards_in_play[0]
            player.cards_in_play.remove(to_return)
            player.hand.append(to_return)
            playable = [c for c in player.hand
                        if getattr(c, 'card_type', '') == 'CHARACTER'
                        and (getattr(c, 'cost', 0) or 0) <= 4]
            if playable:
                to_play = playable[0]
                player.hand.remove(to_play)
                player.cards_in_play.append(to_play)
            card.op10_022_used = True
            return True
    return False


# --- OP10-042: Usopp (Leader) ---
@register_effect("OP10-042", "continuous", "Dressrosa cost 2+ chars gain +1 cost")
def op10_042_usopp_continuous(game_state, player, card):
    """All Dressrosa Characters with cost 2 or more gain +1 cost."""
    for char in player.cards_in_play:
        if ('dressrosa' in (char.card_origin or '').lower()
            and (getattr(char, 'cost', 0) or 0) >= 2):
            char.cost_modifier = getattr(char, 'cost_modifier', 0) + 1
    return True


# --- OP10-099: Eustass"Captain"Kid (Leader) ---
@register_effect("OP10-099", "end_of_turn", "[End of Turn] Turn 1 life face-up: Set Supernova cost 3-8 active")
def op10_099_kid_leader(game_state, player, card):
    """End of Your Turn: Turn 1 Life face-up, set Supernova Character cost 3-8 as active."""
    if player.life_cards:
        player.life_cards[-1].is_face_up = True
        supernovas = [c for c in player.cards_in_play
                      if c.is_resting
                      and 'supernovas' in (c.card_origin or '').lower()
                      and 3 <= (getattr(c, 'cost', 0) or 0) <= 8]
        if supernovas:
            supernovas[0].is_resting = False
        return True
    return False


# =============================================================================
# OP10-OP14 CHARACTER EFFECTS (Key Cards)
# =============================================================================

# --- OP10-003: Gecko Moria ---
@register_effect("OP10-003", "on_play", "[On Play] Trash 2 from deck, play Thriller Bark cost 4 or less from trash")
def op10_003_gecko_moria(game_state, player, card):
    """On Play: Trash 2 from deck, play Thriller Bark cost 4 or less from trash."""
    for _ in range(min(2, len(player.deck))):
        if player.deck:
            c = player.deck.pop(0)
            player.trash.append(c)
    for c in list(player.trash):
        if 'Thriller Bark Pirates' in (c.card_origin or '') and (getattr(c, 'cost', 0) or 0) <= 4:
            if getattr(c, 'card_type', '') == 'CHARACTER':
                player.trash.remove(c)
                player.cards_in_play.append(c)
                break
    return True


# --- OP10-004: Shanks ---
@register_effect("OP10-004", "on_play", "[On Play] If Four Emperors leader, K.O. cost 4 or less")
def op10_004_shanks(game_state, player, card):
    """On Play: If Four Emperors leader, K.O. cost 4 or less."""
    if player.leader and 'The Four Emperors' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's cost 4 or less to K.O.")
    return True


# --- OP10-005: Squard ---
@register_effect("OP10-005", "on_play", "[On Play] If Whitebeard leader, K.O. cost 2 or less")
def op10_005_squard(game_state, player, card):
    """On Play: If Whitebeard leader, K.O. cost 2 or less."""
    if player.leader and 'Whitebeard Pirates' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's cost 2 or less to K.O.")
    return True


# --- OP10-007: Charlotte Linlin ---
@register_effect("OP10-007", "on_play", "[On Play] Play Big Mom cost 4 or less from hand rested")
def op10_007_charlotte_linlin(game_state, player, card):
    """On Play: Play Big Mom Pirates cost 4 or less from hand rested."""
    for c in list(player.hand):
        if 'Big Mom Pirates' in (c.card_origin or '') and (getattr(c, 'cost', 0) or 0) <= 4:
            if getattr(c, 'card_type', '') == 'CHARACTER':
                player.hand.remove(c)
                c.is_resting = True
                player.cards_in_play.append(c)
                break
    return True


# --- OP10-008: Edward.Newgate ---
@register_effect("OP10-008", "on_play", "[On Play] K.O. opponent's cost 5 or less if Whitebeard leader")
def op10_008_whitebeard(game_state, player, card):
    """On Play: If Whitebeard leader, K.O. cost 5 or less."""
    if player.leader and 'Whitebeard Pirates' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 5]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's cost 5 or less to K.O.")
    return True


# --- OP10-022: Jewelry Bonney ---
@register_effect("OP10-022", "on_play", "[On Play] If Egghead leader, rest opponent's cost 5 or less")
def op10_022_bonney(game_state, player, card):
    """On Play: If Egghead leader, rest opponent's cost 5 or less."""
    if player.leader and 'Egghead' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        for c in opponent.cards_in_play:
            if (getattr(c, 'cost', 0) or 0) <= 5:
                c.is_resting = True
                break
    return True


# --- OP10-024: Vegapunk ---
@register_effect("OP10-024", "on_play", "[On Play] If Egghead leader, draw 2 and trash 2")
def op10_024_vegapunk(game_state, player, card):
    """On Play: If Egghead leader, draw 2 and trash 2."""
    if player.leader and 'Egghead' in (player.leader.card_origin or ''):
        draw_cards(player, 2)
        trash_from_hand(player, 2, game_state, card)
    return True


# --- OP10-040: Issho ---
@register_effect("OP10-040", "on_play", "[On Play] If Navy leader, return cost 7 or less to hand")
def op10_040_issho(game_state, player, card):
    """On Play: If Navy leader, return opponent's cost 7 or less to hand."""
    if player.leader and 'Navy' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 7]
        if targets:
            return create_return_to_hand_choice(game_state, player, targets, source_card=card,
                                               prompt="Choose opponent's cost 7 or less to return to hand")
    return True


# --- OP10-041: Kizaru ---
@register_effect("OP10-041", "on_play", "[On Play] If Navy leader, opponent puts hand card on bottom of deck")
def op10_041_kizaru(game_state, player, card):
    """On Play: If Navy leader, opponent puts hand card on bottom of deck."""
    if player.leader and 'Navy' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        if opponent.hand:
            c = opponent.hand.pop(0)
            opponent.deck.append(c)
    return True


# --- OP10-043: Smoker ---
@register_effect("OP10-043", "blocker", "[Blocker]")
def op10_043_smoker_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP10-043", "on_play", "[On Play] If Navy leader, look at 5 and add Navy")
def op10_043_smoker_on_play(game_state, player, card):
    """On Play: If Navy leader, look at 5 and add Navy card."""
    if player.leader and 'Navy' in (player.leader.card_origin or ''):
        looked = player.deck[:5] if len(player.deck) >= 5 else player.deck[:]
        for c in looked:
            if 'Navy' in (c.card_origin or ''):
                player.deck.remove(c)
                player.hand.append(c)
                break
    return True


# --- OP10-047: Hina ---
@register_effect("OP10-047", "blocker", "[Blocker]")
def op10_047_hina_blocker(game_state, player, card):
    """Blocker."""
    card.has_blocker = True
    return True


@register_effect("OP10-047", "on_play", "[On Play] Draw 1, then bottom deck 1")
def op10_047_hina_on_play(game_state, player, card):
    """On Play: Draw 1, then place 1 at bottom of deck."""
    draw_cards(player, 1)
    if player.hand:
        c = player.hand.pop(0)
        player.deck.append(c)
    return True


# --- OP10-060: Charlotte Katakuri ---
@register_effect("OP10-060", "on_play", "[On Play] If Big Mom leader, bottom deck cost 2 or less")
def op10_060_katakuri(game_state, player, card):
    """On Play: If Big Mom leader, bottom deck opponent's cost 2 or less."""
    if player.leader and 'Big Mom Pirates' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
        if targets:
            return create_bottom_deck_choice(game_state, player, targets, source_card=card,
                                            prompt="Choose opponent's cost 2 or less to place at deck bottom")
    return True


# --- OP10-061: Charlotte Linlin ---
@register_effect("OP10-061", "on_play", "[On Play] If Big Mom leader, play cost 4 or less from trash rested")
def op10_061_linlin(game_state, player, card):
    """On Play: If Big Mom leader, play cost 4 or less from trash rested."""
    if player.leader and 'Big Mom Pirates' in (player.leader.card_origin or ''):
        for c in list(player.trash):
            if (getattr(c, 'cost', 0) or 0) <= 4:
                if getattr(c, 'card_type', '') == 'CHARACTER':
                    player.trash.remove(c)
                    c.is_resting = True
                    player.cards_in_play.append(c)
                    break
    return True


# =============================================================================
# OP10 SEARCHER CARDS
# =============================================================================

# --- OP10-006: Caesar Clown ---
@register_effect("OP10-006", "on_play", "[On Play] Look at 5, add Smiley, then play Smiley from hand")
def op10_006_caesar(game_state, player, card):
    """[On Play] Look at 5 cards from the top of your deck; reveal up to 1
    [Smiley] and add it to your hand. Then, place the rest at the bottom of
    your deck in any order and play up to 1 [Smiley] from your hand."""
    result = search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: c.name == 'Smiley',
        source_card=card,
        prompt="Look at top 5: choose 1 [Smiley] to add to hand")
    # Play a Smiley from hand if available
    smiley_in_hand = [c for c in player.hand
                      if c.name == 'Smiley'
                      and getattr(c, 'card_type', '') == 'CHARACTER']
    if smiley_in_hand:
        return create_play_from_hand_choice(
            game_state, player, smiley_in_hand, source_card=card,
            rest_on_play=False,
            prompt="Choose a [Smiley] from your hand to play")
    return result


# --- OP10-028: Kouzuki Momonosuke ---
@register_effect("OP10-028", "activate", "[Activate: Main] Rest 2 DON, trash this: Look at 5, add up to 2 Akazaya Nine")
def op10_028_momonosuke(game_state, player, card):
    """[Activate: Main] You may rest 2 of your DON!! cards and trash this Character:
    Look at 5 cards from the top of your deck; reveal up to 2 {The Akazaya Nine}
    type cards and add them to your hand. Then, place the rest at the bottom of
    your deck in any order."""
    if card.is_resting:
        return False
    if getattr(card, 'main_activated_this_turn', False):
        return False
    # Check for 2 active DON
    active_don = [d for d in getattr(player, 'don_cards', []) if not getattr(d, 'is_resting', False)]
    if len(active_don) < 2:
        return False
    # Rest 2 DON
    for d in active_don[:2]:
        d.is_resting = True
    # Trash this character
    if card in player.cards_in_play:
        player.cards_in_play.remove(card)
        player.trash.append(card)
    card.main_activated_this_turn = True
    # Search top 5 for up to 2 Akazaya Nine
    return search_top_cards(game_state, player, look_count=5, add_count=2,
        filter_fn=lambda c: 'The Akazaya Nine' in (c.card_origin or ''),
        source_card=card,
        prompt="Look at top 5: choose up to 2 {The Akazaya Nine} cards to add to hand")


# --- OP10-051: Hack ---
@register_effect("OP10-051", "on_attack", "[DON!! x1] [When Attacking] Look at 3, add Revolutionary Army Character")
def op10_051_hack(game_state, player, card):
    """[DON!! x1] [When Attacking] Look at 3 cards from the top of your deck;
    reveal up to 1 {Revolutionary Army} type Character card and add it to your hand.
    Then, place the rest at the bottom of your deck in any order."""
    if getattr(card, 'attached_don', 0) < 1:
        return False
    return search_top_cards(game_state, player, look_count=3, add_count=1,
        filter_fn=lambda c: 'Revolutionary Army' in (c.card_origin or '')
                            and getattr(c, 'card_type', '') == 'CHARACTER',
        source_card=card,
        prompt="Look at top 3: choose 1 {Revolutionary Army} Character to add to hand")


# --- OP10-059: Fo...llow...Me... (Event) ---
@register_effect("OP10-059", "on_play", "[Main] Look at 5, add Dressrosa Character")
def op10_059_follow_me(game_state, player, card):
    """[Main] Look at 5 cards from the top of your deck; reveal up to 1
    {Dressrosa} type Character card and add it to your hand.
    Then, place the rest at the bottom of your deck in any order."""
    return search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: 'Dressrosa' in (c.card_origin or '')
                            and getattr(c, 'card_type', '') == 'CHARACTER',
        source_card=card,
        prompt="Look at top 5: choose 1 {Dressrosa} Character to add to hand")


@register_effect("OP10-059", "trigger", "[Trigger] Activate this card's [Main] effect")
def op10_059_follow_me_trigger(game_state, player, card):
    """[Trigger] Activate this card's [Main] effect."""
    return op10_059_follow_me(game_state, player, card)


# --- OP10-065: Sugar ---
@register_effect("OP10-065", "activate", "[Activate: Main] Rest 1 DON and this: Look at 5, add Donquixote Pirates")
def op10_065_sugar(game_state, player, card):
    """[Activate: Main] You may rest 1 of your DON!! cards and this Character:
    Look at 5 cards from the top of your deck; reveal up to 1 {Donquixote Pirates}
    type card and add it to your hand. Then, place the rest at the bottom of
    your deck in any order."""
    if card.is_resting:
        return False
    if getattr(card, 'main_activated_this_turn', False):
        return False
    # Check for 1 active DON
    active_don = [d for d in getattr(player, 'don_cards', []) if not getattr(d, 'is_resting', False)]
    if len(active_don) < 1:
        return False
    # Rest 1 DON
    active_don[0].is_resting = True
    # Rest this character
    card.is_resting = True
    card.main_activated_this_turn = True
    return search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: 'Donquixote Pirates' in (c.card_origin or ''),
        source_card=card,
        prompt="Look at top 5: choose 1 {Donquixote Pirates} card to add to hand")


# --- OP10-078: I Do Not Forgive Those Who Laugh at My Family!!! (Event) ---
@register_effect("OP10-078", "on_play", "[Main] Look at 3, add Donquixote Pirates (not self)")
def op10_078_i_do_not_forgive(game_state, player, card):
    """[Main]/[Counter] Look at 3 cards from the top of your deck; reveal up to 1
    {Donquixote Pirates} type card other than
    [I Do Not Forgive Those Who Laugh at My Family!!!] and add it to your hand.
    Then, place the rest at the bottom of your deck in any order."""
    return search_top_cards(game_state, player, look_count=3, add_count=1,
        filter_fn=lambda c: 'Donquixote Pirates' in (c.card_origin or '')
                            and c.name != 'I Do Not Forgive Those Who Laugh at My Family!!!',
        source_card=card,
        prompt="Look at top 3: choose 1 {Donquixote Pirates} card to add to hand")


@register_effect("OP10-078", "counter", "[Counter] Look at 3, add Donquixote Pirates (not self)")
def op10_078_i_do_not_forgive_counter(game_state, player, card):
    """[Counter] Activate the [Main] effect."""
    return op10_078_i_do_not_forgive(game_state, player, card)


# --- OP10-111: Monkey.D.Luffy ---
@register_effect("OP10-111", "on_play", "[On Play] Look at 5, add Supernovas (not self)")
def op10_111_luffy(game_state, player, card):
    """[On Play] Look at 5 cards from the top of your deck; reveal up to 1
    {Supernovas} type card other than [Monkey.D.Luffy] and add it to your hand.
    Then, place the rest at the bottom of your deck in any order."""
    return search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: 'Supernovas' in (c.card_origin or '')
                            and c.name != 'Monkey.D.Luffy',
        source_card=card,
        prompt="Look at top 5: choose 1 {Supernovas} card (not Monkey.D.Luffy) to add to hand")


# --- OP10-039: Gum-Gum Dragon Fire Pistol Twister Star ---
@register_effect("OP10-039", "on_play", "[Main] If ODYSSEY leader, look at 5, add up to 2 ODYSSEY Characters")
def op10_039_gum_gum(game_state, player, card):
    """[Main] If ODYSSEY leader, look at 5, add up to 2 ODYSSEY type Characters."""
    leader_type = (player.leader.card_origin or '').lower() if player.leader else ''
    if 'odyssey' not in leader_type:
        return False
    return search_top_cards(game_state, player, look_count=5, add_count=2,
        filter_fn=lambda c: ('odyssey' in (c.card_origin or '').lower()
                             and c.card_type == 'CHARACTER'),
        source_card=card,
        prompt="Look at top 5: choose up to 2 ODYSSEY type Characters to add to hand")


# --- OP10-057: Leo ---
@register_effect("OP10-057", "on_play", "[On Play] Rest leader/stage: If Usopp, look at 5, add 2 Dressrosa (not self), trash 1")
def op10_057_leo(game_state, player, card):
    """[On Play] Rest Leader or Stage: If Usopp leader, look at 5, add up to 2 Dressrosa (not Leo), trash 1."""
    if not player.leader or 'usopp' not in (player.leader.name or '').lower():
        return False
    # Rest leader or stage as cost (auto-rest leader for simplicity)
    if player.leader and not player.leader.is_resting:
        player.leader.is_resting = True
    else:
        stages = [c for c in player.cards_in_play
                  if getattr(c, 'card_type', '') == 'STAGE' and not c.is_resting]
        if stages:
            stages[0].is_resting = True
        else:
            return False
    result = search_top_cards(game_state, player, look_count=5, add_count=2,
        filter_fn=lambda c: ('dressrosa' in (c.card_origin or '').lower()
                             and 'leo' not in (c.name or '').lower()),
        source_card=card,
        prompt="Leo: Look at top 5, choose up to 2 Dressrosa cards (not Leo) to add to hand")
    # Note: trash 1 from hand after should be handled via callback
    return result


# --- OP10-106: Killer ---
@register_effect("OP10-106", "on_ko", "[On K.O.] If Supernovas leader, look at 3, add Supernovas/Kid Pirates")
def op10_106_killer(game_state, player, card):
    """[On K.O.] If Supernovas leader, look at 3, add 1 Supernovas or Kid Pirates card."""
    leader_type = (player.leader.card_origin or '').lower() if player.leader else ''
    if 'supernovas' not in leader_type:
        return False
    return search_top_cards(game_state, player, look_count=3, add_count=1,
        filter_fn=lambda c: ('supernovas' in (c.card_origin or '').lower()
                             or 'kid pirates' in (c.card_origin or '').lower()),
        source_card=card,
        prompt="Killer: Look at top 3, choose 1 Supernovas or Kid Pirates card to add to hand")
