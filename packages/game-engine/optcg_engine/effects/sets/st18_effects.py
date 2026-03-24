"""
Hardcoded effects for ST18 cards.
"""

from ..hardcoded import register_effect, search_top_cards


# --- ST18-004: Zoro-Juurou ---
@register_effect("ST18-004", "on_play", "[On Play] Look at 5, add purple Straw Hat Crew to hand")
def st18_004_zoro_juurou(game_state, player, card):
    """On Play: Look at top 5, reveal up to 1 purple Straw Hat Crew card to hand, rest to bottom."""
    def purple_shc_filter(c):
        colors = getattr(c, 'colors', []) or []
        if isinstance(colors, str):
            colors = [colors]
        return ('straw hat crew' in (c.card_origin or '').lower()
                and any('purple' in col.lower() for col in colors))
    return search_top_cards(game_state, player, 5, add_count=1, filter_fn=purple_shc_filter,
                            source_card=card,
                            prompt="Look at top 5: choose a purple Straw Hat Crew card to add to hand")
