"""
Hardcoded effects for ST29 cards.
"""

from ..hardcoded import (
    draw_cards, get_opponent, give_don_to_card, register_effect,
    search_top_cards, trash_from_hand,
)


# --- ST29-012: Monkey.D.Luffy ---
@register_effect("ST29-012", "MAIN", "Give 1 rested DON to Monkey.D.Luffy")
def luffy_st29_effect(game_state, player, card):
    rested_don = [d for d in player.don_pool if d.is_resting]
    luffy_cards = [c for c in player.cards_in_play if 'Monkey.D.Luffy' in getattr(c, 'name', '')]
    if rested_don and luffy_cards:
        give_don_to_card(player, luffy_cards[0], 1, rested_only=True)
        return True
    return False


# --- ST29-012: Monkey.D.Luffy ---
@register_effect("ST29-012", "ACTIVATE_MAIN", "Give 1 rested DON to Luffy card")
def luffy_st29_effect(game_state, player, card):
    luffy_cards = [c for c in player.cards_in_play if 'Monkey.D.Luffy' in getattr(c, 'name', '')]
    if luffy_cards:
        give_don_to_card(player, luffy_cards[0], 1, rested_only=True)
        return True
    # Also check leader
    if player.leader and 'Monkey.D.Luffy' in getattr(player.leader, 'name', ''):
        give_don_to_card(player, player.leader, 1, rested_only=True)
        return True
    return False


# --- ST29-008: Nami (Egghead protection) ---
@register_effect("ST29-008", "ON_WOULD_BE_KO", "If Egghead char would be KO'd by effect, turn Life face-up instead")
def nami_egghead_protect(game_state, player, card):
    """Protect Egghead characters from effect KO by turning Life face-up."""
    # This effect triggers when an Egghead char would be KO'd
    if player.life_cards:
        # Turn top life face-up (mark it)
        top_life = player.life_cards[-1]
        top_life.is_face_up = True
        return True  # Prevents the KO
    return False


# --- ST29-001: Monkey.D.Luffy (Leader) ---
@register_effect("ST29-001", "WHEN_ATTACKING", "If 2 or less life, draw 1 and trash 1")
def st29_001_luffy_leader(game_state, player, card):
    """When Attacking: If 2 or less life, draw 1 and trash 1 from hand."""
    if check_life_count(player, 2):
        draw_cards(player, 1)
        trash_from_hand(player, 1, game_state, card)
        return True
    return False


# --- ST29-015: Raw Heat Strike ---
@register_effect("ST29-015", "COUNTER", "+2000 power, -2000 to opponent if 1 or less life")
def st29_015_raw_heat(game_state, player, card):
    """Counter: +2000 power, -2000 to opponent's card if 1 or less life."""
    target = player.leader if player.leader else (player.cards_in_play[0] if player.cards_in_play else None)
    if target:
        add_power_modifier(target, 2000)
        if check_life_count(player, 1):
            opponent = get_opponent(game_state, player)
            opp_target = opponent.leader if opponent.leader else (opponent.cards_in_play[0] if opponent.cards_in_play else None)
            if opp_target:
                add_power_modifier(opp_target, -2000)
        return True
    return False


# --- ST29-017: Iai Death Lion Song ---
@register_effect("ST29-017", "COUNTER", "+4000 power, KO cost 3 or less if 2 or less life")
def st29_017_iai_death(game_state, player, card):
    """Counter: +4000 power, KO cost 3 or less if 2 or less life."""
    target = player.leader if player.leader else (player.cards_in_play[0] if player.cards_in_play else None)
    if target:
        add_power_modifier(target, 4000)
        if check_life_count(player, 2):
            return ko_opponent_character(game_state, player, max_cost=3, source_card=card)
        return True
    return False


# --- ST29-001: Monkey.D.Luffy (Leader) ---
@register_effect("ST29-001", "on_attack", "[When Attacking] If 2- life, draw 1 trash 1")
def st29_001_luffy_leader_attack(game_state, player, card):
    """When Attacking: If you have 2 or less Life, draw 1 card and trash 1 card from hand."""
    if len(player.life_cards) <= 2:
        draw_cards(player, 1)
        if player.hand:
            trash_from_hand(player, 1, game_state, card)
        return True
    return False


# --- ST29-004: Sanji ---
@register_effect("ST29-004", "on_play", "[On Play] Look at 4, add Straw Hat Crew to hand")
def st29_004_sanji(game_state, player, card):
    """On Play: Look at top 4, reveal up to 1 Straw Hat Crew card to hand, rest to bottom."""
    def shc_filter(c):
        return 'straw hat crew' in (c.card_origin or '').lower()
    return search_top_cards(game_state, player, 4, add_count=1, filter_fn=shc_filter,
                            source_card=card,
                            prompt="Look at top 4: choose a Straw Hat Crew card to add to hand")

