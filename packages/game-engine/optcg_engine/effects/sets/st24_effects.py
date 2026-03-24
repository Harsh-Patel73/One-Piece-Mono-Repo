"""
Hardcoded effects for ST24 cards.
"""

from ..hardcoded import register_effect, search_top_cards


# --- ST24-002: Kid & Killer ---
@register_effect("ST24-002", "on_play", "[On Play] Look at 5, add Supernovas to hand")
def st24_002_kid_killer(game_state, player, card):
    """On Play: Look at top 5, reveal up to 1 Supernovas card to hand, rest to bottom."""
    def supernovas_filter(c):
        return 'supernovas' in (c.card_origin or '').lower()
    return search_top_cards(game_state, player, 5, add_count=1, filter_fn=supernovas_filter,
                            source_card=card,
                            prompt="Look at top 5: choose a Supernovas card to add to hand")
