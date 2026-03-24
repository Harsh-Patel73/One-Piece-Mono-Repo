"""
Hardcoded effects for EB01 cards.
"""

from ..hardcoded import (
    add_don_from_deck, create_mode_choice, draw_cards, get_opponent,
    give_don_to_card, register_effect, search_top_cards, set_active,
    trash_from_hand,
)


# --- EB01-061: Mr.2.Bon.Kurei(Bentham) ---
@register_effect("EB01-061", "ON_PLAY", "Add DON and set active")
def mr2_eb01_on_play(game_state, player, card):
    add_don_from_deck(player, 1, set_active=True)
    return True


@register_effect("EB01-061", "WHEN_ATTACKING", "Copy opponent char's power")
def mr2_eb01_attack(game_state, player, card):
    opponent = get_opponent(game_state, player)
    if opponent.cards_in_play:
        target = opponent.cards_in_play[0]
        card.power = getattr(target, 'power', 0)
        return True
    return False


# --- EB01-038: Oh Come My Way ---
@register_effect("EB01-038", "COUNTER", "DON -1: Change attack target to char")
def oh_come_my_way_effect(game_state, player, card):
    if hasattr(player, 'don_deck'):
        active_don = [d for d in player.don_pool if not d.is_resting]
        if active_don and player.cards_in_play:
            don = active_don[0]
            player.don_pool.remove(don)
            player.don_deck.append(don)
            # Attack target change handled by game
            return True
    return False


# --- EB01-012: Cavendish ---
@register_effect("EB01-012", "ON_PLAY", "If Leader is Supernovas and no other Cavendish, set 2 DON active")
def eb01_012_cavendish_play(game_state, player, card):
    if check_leader_type(player, "Supernovas"):
        other_cavendish = [c for c in player.cards_in_play
                          if c != card and 'Cavendish' in (getattr(c, 'name', '') or '')]
        if not other_cavendish:
            set_active(player.don_pool[:2])
    return True


@register_effect("EB01-012", "WHEN_ATTACKING", "If Leader is Supernovas and no other Cavendish, set 2 DON active")
def eb01_012_cavendish_attack(game_state, player, card):
    if check_leader_type(player, "Supernovas"):
        other_cavendish = [c for c in player.cards_in_play
                          if c != card and 'Cavendish' in (getattr(c, 'name', '') or '')]
        if not other_cavendish:
            set_active(player.don_pool[:2])
    return True


# --- EB01-027: Mr.1 (Daz.Bonez) ---
@register_effect("EB01-027", "ON_PLAY", "Draw 2, trash 1. If Leader is Baroque Works, +power per events in trash")
def eb01_027_mr1(game_state, player, card):
    draw_cards(player, 2)
    trash_from_hand(player, 1, game_state, card)
    # Power boost is passive, handled separately
    return True


# --- EB01-028: Gum-Gum Champion Rifle ---
@register_effect("EB01-028", "COUNTER", "If Leader is Impel Down, +2000 power and return opponent's active char")
def eb01_028_gum_gum_rifle(game_state, player, card):
    if check_leader_type(player, "Impel Down"):
        # +2000 power to leader or character
        if player.leader:
            add_power_modifier(player.leader, 2000)
        # Return opponent's active character
        opponent = get_opponent(game_state, player)
        active_chars = [c for c in opponent.cards_in_play if not getattr(c, 'is_resting', False)]
        if active_chars:
            target = active_chars[0]
            opponent.cards_in_play.remove(target)
            opponent.hand.append(target)
    return True


# =============================================================================
# LIFE CONDITION CARDS
# =============================================================================

# --- EB01-003: Kid & Killer ---
@register_effect("EB01-003", "WHEN_ATTACKING", "If opponent has 2 or less life, +2000 power")
def eb01_003_kid_killer(game_state, player, card):
    opponent = get_opponent(game_state, player)
    if check_life_count(opponent, 2, 'le'):
        add_power_modifier(card, 2000)
    return True


# --- EB01-054: Gan.Fall ---
@register_effect("EB01-054", "ON_PLAY", "If opponent has 1 or less life, KO cost 3 or less")
def eb01_054_ganfall(game_state, player, card):
    opponent = get_opponent(game_state, player)
    if check_life_count(opponent, 1, 'le'):
        return ko_opponent_character(game_state, player, max_cost=3, source_card=card)
    return True


# --- EB01-058: Mont Blanc Cricket ---
@register_effect("EB01-058", "YOUR_TURN", "If you have 2 or less life, +2000 power (DON x1)")
def eb01_058_mont_blanc(game_state, player, card):
    if check_life_count(player, 2, 'le') and getattr(card, 'attached_don', 0) >= 1:
        add_power_modifier(card, 2000)
    return True


# =============================================================================
# TRASH CONDITION CARDS
# =============================================================================

# --- EB01-050: ...I Want to Live!! ---
@register_effect("EB01-050", "COUNTER", "If 30+ cards in trash, add deck card to life")
def eb01_050_i_want_to_live(game_state, player, card):
    if check_trash_count(player, 30, 'ge'):
        if player.deck:
            deck_card = player.deck.pop(0)
            player.life_cards.append(deck_card)
    return True


# --- EB01-021: Hannyabal (Leader) ---
@register_effect("EB01-021", "END_OF_TURN", "Return Impel Down cost 2+ to hand: Add 1 DON active")
def eb01_021_hannyabal(game_state, player, card):
    impel_chars = [c for c in player.cards_in_play
                   if 'Impel Down' in (getattr(c, 'card_origin', '') or '')
                   and (getattr(c, 'cost', 0) or 0) >= 2]
    if impel_chars:
        to_return = impel_chars[0]
        return_to_hand(player, to_return)
        add_don_from_deck(player, 1, set_active=True)
    return True


# =============================================================================
# COMPLEX CHOICE CARDS
# =============================================================================

# --- EB01-052: Viola ---
@register_effect("EB01-052", "ON_PLAY", "Choose: Look at opponent's life OR look at 5 and rearrange")
def eb01_052_viola(game_state, player, card):
    # Player chooses which effect to use
    modes = [
        {"id": "view_life", "label": "View Opponent's Life", "description": "Look at all of your opponent's Life cards"},
        {"id": "view_deck", "label": "View Top 5 & Rearrange", "description": "Look at the top 5 cards of your deck and rearrange them"}
    ]
    return create_mode_choice(game_state, player, modes, source_card=card,
                               prompt="Choose: Look at opponent's Life OR Look at top 5 of your deck and rearrange")


# --- EB01-002: Izo ---
@register_effect("EB01-002", "ON_PLAY", "Give 1 rested DON to Leader or Character")
def eb01_002_izo_play(game_state, player, card):
    give_don_to_card(player, player.leader, 1, rested_only=True)
    return True


@register_effect("EB01-002", "ON_OPPONENT_ATTACK", "Trash 1: If Leader is Land of Wano, +2000 power")
def eb01_002_izo_attack(game_state, player, card):
    if player.hand and check_leader_type(player, "Land of Wano"):
        trash_from_hand(player, 1, game_state, card)
        add_power_modifier(player.leader, 2000)
    return True


# =============================================================================
# LEADER CARD EFFECTS - Extra Boosters and Promos
# =============================================================================

# --- EB01-001: Kouzuki Oden (Leader) ---
@register_effect("EB01-001", "continuous", "Land of Wano chars without Counter gain +1000 Counter")
def eb01_001_oden_continuous(game_state, player, card):
    """All Land of Wano Characters without Counter have +1000 Counter."""
    for char in player.cards_in_play:
        if ('land of wano' in (char.card_origin or '').lower()
            and not getattr(char, 'counter', 0)):
            char.counter = 1000
    return True


# --- EB01-009: Just Shut Up and Come with Us!!!! ---
@register_effect("EB01-009", "counter", "[Counter] Look at 5, play Animal cost 3 or less")
def eb01_009_just_shut_up(game_state, player, card):
    """Counter: Look at top 5, play up to 1 Animal type Character cost 3 or less to field, rest to bottom."""
    def animal_filter(c):
        return ('animal' in (c.card_origin or '').lower()
                and getattr(c, 'card_type', '') == 'CHARACTER'
                and (getattr(c, 'cost', 0) or 0) <= 3)
    return search_top_cards(game_state, player, 5, add_count=1, filter_fn=animal_filter,
                            source_card=card, play_to_field=True,
                            prompt="Look at top 5: choose an Animal Character (cost 3 or less) to play")


@register_effect("EB01-001", "on_attack", "[DON!! x1] If Land of Wano cost 5+ exists, +1000 power")
def eb01_001_oden_attack(game_state, player, card):
    """DON x1, When Attacking: If you have a Land of Wano cost 5+ Character, +1000 power."""
    if getattr(card, 'attached_don', 0) >= 1:
        wano_5_plus = [c for c in player.cards_in_play
                       if 'land of wano' in (c.card_origin or '').lower()
                       and (getattr(c, 'cost', 0) or 0) >= 5]
        if wano_5_plus:
            card.power_modifier = getattr(card, 'power_modifier', 0) + 1000
        return True
    return False


# --- EB01-040: Kyros (Leader) ---
@register_effect("EB01-040", "activate", "[Activate: Main] Turn 1 life face-up: K.O. cost 0")
def eb01_040_kyros_leader(game_state, player, card):
    """Once Per Turn: Turn 1 card from top of Life face-up, K.O. opponent's cost 0 Character."""
    if hasattr(card, 'eb01_040_used') and card.eb01_040_used:
        return False
    if player.life_cards:
        player.life_cards[-1].is_face_up = True
        opponent = get_opponent(game_state, player)
        cost_zero = [c for c in opponent.cards_in_play
                     if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 0]
        if cost_zero:
            target = cost_zero[0]
            opponent.cards_in_play.remove(target)
            opponent.trash.append(target)
        card.eb01_040_used = True
        return True
    return False


# --- EB01-019: Off-White ---
@register_effect("EB01-019", "counter", "[Counter] +4000 power, then look at 3, add Donquixote Pirates Character")
def eb01_019_off_white(game_state, player, card):
    """[Counter] +4000 power, then look at 3, add 1 Donquixote Pirates Character."""
    # Apply +4000 power to leader or character being attacked
    if game_state.pending_attack:
        target = game_state.pending_attack.get('target')
        if target:
            target.power_modifier = getattr(target, 'power_modifier', 0) + 4000
        elif player.leader:
            player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 4000
    return search_top_cards(game_state, player, look_count=3, add_count=1,
        filter_fn=lambda c: ('donquixote pirates' in (c.card_origin or '').lower()
                             and c.card_type == 'CHARACTER'),
        source_card=card,
        prompt="Off-White: Look at top 3, choose 1 Donquixote Pirates Character to add to hand")
