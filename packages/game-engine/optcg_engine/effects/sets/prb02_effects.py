"""
Hardcoded effects for PRB02 cards.
"""

from ..effect_registry import (
    create_target_choice, get_opponent, register_effect, search_top_cards,
)


# --- PRB02-005: Monkey.D.Luffy ---
@register_effect("PRB02-005", "ON_PLAY", "If multicolor Leader and opponent has 7 or less DON, rest their DON")
def luffy_prb02_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    colors = (getattr(player.leader, 'colors', '') or '').lower() if player.leader else ''
    is_multicolor = colors.count('/') > 0 or len([c for c in ['red', 'blue', 'green', 'purple', 'black', 'yellow'] if c in colors]) > 1
    if is_multicolor and len(opponent.don_pool) <= 7:
        active_don = [d for d in opponent.don_pool if not d.is_resting]
        if active_don:
            # Mark to rest at start of next main phase
            opponent.rest_don_at_main_phase = True
            return True
    return False


# --- PRB02-018: Portgas.D.Ace ---
@register_effect("PRB02-018", "ON_PLAY", "If face-up Life, play Sabo/Ace/Luffy cost 2")
def ace_prb02_effect(game_state, player, card):
    # Check for face-up life (simplified)
    targets = [c for c in player.hand + list(player.trash)
              if getattr(c, 'card_type', '') == 'CHARACTER'
              and (getattr(c, 'cost', 0) or 0) == 2
              and any(name in getattr(c, 'name', '') for name in ['Sabo', 'Portgas.D.Ace', 'Monkey.D.Luffy'])]
    if targets:
        return create_target_choice(
            game_state, player, targets,
            callback_action="play_from_hand_or_trash",
            source_card=card,
            prompt="Choose Sabo/Ace/Luffy cost 2 Character to play from hand or trash"
        )
    return False


# --- PRB02-006: Roronoa Zoro ---
@register_effect("PRB02-006", "WOULD_BE_RESTED", "Rest another char instead")
def zoro_prb02_effect(game_state, player, card):
    other_chars = [c for c in player.cards_in_play if c != card and not c.is_resting]
    if other_chars:
        other_chars[0].is_resting = True
        return True  # Prevent this card from being rested
    return False


# --- PRB02-006: Roronoa Zoro ---
@register_effect("PRB02-006", "ON_WOULD_BE_RESTED", "Rest another Character instead")
def zoro_prb02_effect(game_state, player, card):
    # If would be rested by opponent's effect, rest another character
    other_chars = [c for c in player.cards_in_play if c != card and not c.is_resting]
    if other_chars:
        return create_target_choice(
            game_state, player, other_chars,
            callback_action="rest_instead",
            source_card=card,
            prompt="Choose your Character to rest instead of Zoro"
        )
    return False


# =============================================================================
# SEARCHER CARDS
# =============================================================================

# --- PRB02-007: Jinbe ---
@register_effect("PRB02-007", "on_play", "[On Play] Look at 5, add Warlords (not Jinbe) to hand")
def prb02_007_jinbe(game_state, player, card):
    """On Play: Look at top 5, reveal up to 1 Seven Warlords card (not Jinbe) to hand, rest to bottom."""
    def warlords_not_jinbe(c):
        return ('seven warlords of the sea' in (c.card_origin or '').lower()
                and 'jinbe' not in (c.name or '').lower())
    return search_top_cards(game_state, player, 5, add_count=1, filter_fn=warlords_not_jinbe,
                            source_card=card,
                            prompt="Look at top 5: choose a Seven Warlords card (not Jinbe) to add to hand")


# --- PRB02-012: Nami ---
@register_effect("PRB02-012", "on_play", "[On Play] Look at 5, add Straw Hat Crew (not Nami) to hand")
def prb02_012_nami(game_state, player, card):
    """On Play: Look at top 5, reveal up to 1 Straw Hat Crew card (not Nami) to hand, rest to bottom."""
    def shc_not_nami(c):
        return ('straw hat crew' in (c.card_origin or '').lower()
                and 'nami' not in (c.name or '').lower())
    return search_top_cards(game_state, player, 5, add_count=1, filter_fn=shc_not_nami,
                            source_card=card,
                            prompt="Look at top 5: choose a Straw Hat Crew card (not Nami) to add to hand")

