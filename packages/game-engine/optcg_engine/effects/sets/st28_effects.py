"""
Hardcoded effects for ST28 cards.
"""

from ..effect_registry import (
    create_ko_choice, get_opponent, register_effect, search_top_cards,
)


# =============================================================================
# MORE LEADER CONDITION CARDS - Land of Wano
# =============================================================================

# --- ST28-001: Ashura Doji ---
@register_effect("ST28-001", "ON_PLAY", "If Leader is Land of Wano and opponent 3+ life, KO base cost 5 or less")
def st28_001_ashura(game_state, player, card):
    if check_leader_type(player, "Land of Wano"):
        opponent = get_opponent(game_state, player)
        if len(opponent.life_cards) >= 3:
            targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 5]
            if targets:
                return create_ko_choice(game_state, player, targets, source_card=card,
                                       prompt="Choose opponent's base cost 5 or less to KO")
    return True


# --- ST28-004: Kouzuki Momonosuke ---
@register_effect("ST28-004", "CONTINUOUS", "If 2 or less life, Leader +1000 power")
def st28_004_momonosuke_continuous(game_state, player, card):
    """Continuous: If 2 or less life, Leader gains +1000 power."""
    if check_life_count(player, 2) and player.leader:
        add_power_modifier(player.leader, 1000)
        return True
    return False


@register_effect("ST28-004", "ACTIVATE_MAIN", "Return 2 DON to rest: This gains +2000 power")
def st28_004_momonosuke_main(game_state, player, card):
    """Activate Main: Return 2 given DON to rest, this gains +2000 power."""
    # Return DON to cost area rested
    if getattr(card, 'attached_don', 0) >= 2:
        card.attached_don = card.attached_don - 2
        add_power_modifier(card, 2000)
        return True
    return False


# --- ST28-005: Yamato ---
@register_effect("ST28-005", "continuous", "[DON!! x2] [Your Turn] +3000 power")
def st28_005_yamato_continuous(game_state, player, card):
    """DON!! x2, Your Turn: This Character gains +3000 power."""
    if getattr(card, 'attached_don', 0) >= 2:
        card.power_modifier = getattr(card, 'power_modifier', 0) + 3000
    return True


@register_effect("ST28-005", "on_play", "[On Play] Look at 5, add Land of Wano cost 2+ to hand")
def st28_005_yamato_play(game_state, player, card):
    """On Play: Look at top 5, reveal up to 1 Land of Wano card cost 2+ to hand, rest to bottom."""
    def wano_cost2_filter(c):
        return ('land of wano' in (c.card_origin or '').lower()
                and (getattr(c, 'cost', 0) or 0) >= 2)
    return search_top_cards(game_state, player, 5, add_count=1, filter_fn=wano_cost2_filter,
                            source_card=card,
                            prompt="Look at top 5: choose a Land of Wano card (cost 2+) to add to hand")

