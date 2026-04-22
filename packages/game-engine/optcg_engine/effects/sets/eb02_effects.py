"""
Hardcoded effects for EB02 cards.
"""

from ..effect_registry import (
    create_cost_reduction_choice, create_mode_choice, create_ko_choice, draw_cards, filter_by_max_cost, get_opponent,
    give_don_to_card, register_effect, search_top_cards, trash_from_hand,
)


# --- EB02-009: Thousand Sunny ---
@register_effect("EB02-009", "MAIN", "Rest this: Give 1 given DON to Straw Hat char")
def thousand_sunny_effect(game_state, player, card):
    if not card.is_resting:
        card.is_resting = True
        straw_hat = [c for c in player.cards_in_play
                    if 'straw hat crew' in (c.card_origin or '').lower()]
        if straw_hat:
            # Redistribute DON logic
            return True
    return False


# --- EB02-009: Thousand Sunny ---
@register_effect("EB02-009", "ACTIVATE_MAIN", "Give DON to Straw Hat Crew Character")
def thousand_sunny_effect(game_state, player, card):
    if not card.is_resting:
        card.is_resting = True
        straw_hat = [c for c in player.cards_in_play if 'straw hat crew' in (c.card_origin or '').lower()]
        if straw_hat:
            give_don_to_card(player, straw_hat[0], 1)
            return True
    return False


# --- EB02-054: Sanji ---
@register_effect("EB02-054", "ON_PLAY", "If you have 2 or less life, draw 2 trash 1")
def eb02_054_sanji(game_state, player, card):
    if check_life_count(player, 2, 'le'):
        draw_cards(player, 2)
        trash_from_hand(player, 1, game_state, card)
    return True


# --- EB02-011: Arlong ---
@register_effect("EB02-011", "ON_PLAY", "If Leader is Fish-Man or East Blue, give DON to leader, opponent cost 5 cannot rest")
def eb02_011_arlong(game_state, player, card):
    if check_leader_type(player, "Fish-Man") or check_leader_type(player, "East Blue"):
        # Give 1 rested DON to leader
        give_don_to_card(player, player.leader, 1, rested_only=True)
        # Mark opponent's cost 5 or less chars as cannot rest active (simplified)
    return True


# --- EB02-045: Trafalgar Law ---
@register_effect("EB02-045", "ON_PLAY", "Place 2 from trash at bottom: Choose draw 1 or opponent discards")
def eb02_045_law(game_state, player, card):
    if len(player.trash) >= 2:
        for _ in range(2):
            if player.trash:
                c = player.trash.pop(0)
                player.deck.append(c)
        # Player chooses between draw or opponent discard
        modes = [
            {"id": "draw", "label": "Draw 1", "description": "Draw 1 card"},
            {"id": "discard", "label": "Opponent Discards", "description": "Opponent discards 1 card from hand"}
        ]
        def callback(selected: list[str]) -> None:
            selected_mode = selected[0] if selected else None
            if selected_mode == "draw":
                draw_cards(player, 1)
                game_state._log(f"{player.name} drew 1 card")
            elif selected_mode == "discard":
                opponent = get_opponent(game_state, player)
                if opponent.hand:
                    trash_from_hand(opponent, 1, game_state, card)
                    game_state._log(f"{opponent.name} must discard 1 card")

        return create_mode_choice(game_state, player, modes, source_card=card, callback=callback,
                                   prompt="Choose: Draw 1 card, OR Opponent discards 1 card")
    return True


# --- EB02-051: Three-Pace Hum ---
@register_effect("EB02-051", "MAIN", "Choose: KO cost 2 or less OR give -4 cost")
def eb02_051_three_pace(game_state, player, card):
    opponent = get_opponent(game_state, player)
    # Player chooses between KO or -4 cost
    modes = [
        {"id": "ko", "label": "KO Character", "description": "KO opponent's cost 2 or less Character"},
        {"id": "cost_reduce", "label": "Give -4 Cost", "description": "Give opponent's Character -4 cost this turn"}
    ]
    def callback(selected: list[str]) -> None:
        selected_mode = selected[0] if selected else None
        opponent = get_opponent(game_state, player)
        if selected_mode == "ko":
            targets = filter_by_max_cost(opponent.cards_in_play, 2)
            if targets:
                create_ko_choice(game_state, player, targets, source_card=card,
                                 prompt="Choose opponent's cost 2 or less Character to K.O.")
        elif selected_mode == "cost_reduce" and opponent.cards_in_play:
            create_cost_reduction_choice(
                game_state, player, list(opponent.cards_in_play), -4, source_card=card,
                prompt="Choose opponent's Character to give -4 cost"
            )

    return create_mode_choice(game_state, player, modes, source_card=card, callback=callback,
                               prompt="Choose: KO opponent's cost 2 or less, OR Give -4 cost to a Character")


# --- EB02-059: Without Your Help I Can't Become the King of the Pirates!!!! ---
@register_effect("EB02-059", "COUNTER", "+1000 power, play Straw Hat if 1 or less life")
def eb02_059_without_help(game_state, player, card):
    """Counter: +1000 power, play yellow Straw Hat or Trafalgar Law if 1 or less life."""
    target = player.leader if player.leader else (player.cards_in_play[0] if player.cards_in_play else None)
    if target:
        add_power_modifier(target, 1000)
        if check_life_count(player, 1):
            # Play from trash
            straw_hats = [c for c in player.trash
                         if ('straw hat crew' in (c.card_origin or '').lower()
                             or 'Trafalgar Law' in getattr(c, 'name', ''))
                         and 'yellow' in (getattr(c, 'colors', '') or '').lower()
                         and getattr(c, 'card_type', '') == 'CHARACTER']
            if straw_hats:
                char = straw_hats[0]
                player.trash.remove(char)
                game_state.play_card_to_field_by_effect(player, char)
        return True
    return False


# --- EB02-010: Monkey.D.Luffy (Leader) ---
@register_effect("EB02-010", "activate", "[Activate: Main] DON -2: If only SHC chars, set 2 DON active, +1000")
def eb02_010_luffy_leader(game_state, player, card):
    """Once Per Turn, DON -2: If only Straw Hat Crew Characters, set 2 DON active, Leader +1000."""
    if hasattr(card, 'eb02_010_used') and card.eb02_010_used:
        return False
    if len(player.don_pool) >= 2:
        non_shc = [c for c in player.cards_in_play
                   if 'straw hat crew' not in (c.card_origin or '').lower()]
        if not non_shc and player.cards_in_play:
            for _ in range(2):
                if player.don_pool:
                    don = player.don_pool.pop()
                    if hasattr(player, 'don_deck'):
                        player.don_deck.append(don)
            rested_don = player.don_pool.count("rested")
            for don in rested_don[:2]:
                don.is_resting = False
            card.power_modifier = getattr(card, 'power_modifier', 0) + 1000
            card.eb02_010_used = True
            return True
    return False


# =============================================================================
# SEARCHER CARDS
# =============================================================================

# --- EB02-008: The Peak ---
@register_effect("EB02-008", "main", "[Main] Look at 4, add cost 4+ to hand")
def eb02_008_the_peak(game_state, player, card):
    """Main: Look at top 4, reveal up to 1 card with cost 4+ and add to hand, rest to bottom."""
    def cost4_filter(c):
        return (getattr(c, 'cost', 0) or 0) >= 4
    return search_top_cards(game_state, player, 4, add_count=1, filter_fn=cost4_filter,
                            source_card=card,
                            prompt="Look at top 4: choose a card with cost 4 or more to add to hand")


# --- EB02-017: Nami ---
@register_effect("EB02-017", "on_play", "[On Play] Look at 5, add Straw Hat Crew (not Nami) to hand")
def eb02_017_nami(game_state, player, card):
    """On Play: Look at top 5, reveal up to 1 Straw Hat Crew card (not Nami) to hand, rest to bottom."""
    def shc_not_nami(c):
        return ('straw hat crew' in (c.card_origin or '').lower()
                and 'nami' not in (c.name or '').lower())
    return search_top_cards(game_state, player, 5, add_count=1, filter_fn=shc_not_nami,
                            source_card=card,
                            prompt="Look at top 5: choose a Straw Hat Crew card (not Nami) to add to hand")


# --- EB02-020: We Are! ---
@register_effect("EB02-020", "main", "[Main] Look at 4, add cost 4+ to hand")
def eb02_020_we_are(game_state, player, card):
    """Main: Look at top 4, reveal up to 1 card with cost 4+ and add to hand, rest to bottom."""
    def cost4_filter(c):
        return (getattr(c, 'cost', 0) or 0) >= 4
    return search_top_cards(game_state, player, 4, add_count=1, filter_fn=cost4_filter,
                            source_card=card,
                            prompt="Look at top 4: choose a card with cost 4 or more to add to hand")


# --- EB02-031: Hope ---
@register_effect("EB02-031", "main", "[Main] Look at 4, add cost 4+ to hand")
def eb02_031_hope(game_state, player, card):
    """Main: Look at top 4, reveal up to 1 card with cost 4+ and add to hand, rest to bottom."""
    def cost4_filter(c):
        return (getattr(c, 'cost', 0) or 0) >= 4
    return search_top_cards(game_state, player, 4, add_count=1, filter_fn=cost4_filter,
                            source_card=card,
                            prompt="Look at top 4: choose a card with cost 4 or more to add to hand")


# --- EB02-036: Nico Robin ---
@register_effect("EB02-036", "blocker", "[Blocker]")
def eb02_036_robin_blocker(game_state, player, card):
    """Blocker."""
    card.is_blocker = True
    return True


@register_effect("EB02-036", "on_ko", "[On K.O.] DON!! -1: Look at 3, add Straw Hat Crew to hand")
def eb02_036_robin_ko(game_state, player, card):
    """On K.O., DON!! -1: Look at top 3, reveal up to 1 Straw Hat Crew card to hand, rest to bottom."""
    if player.don_pool:
        player.don_pool.pop()
        def shc_filter(c):
            return 'straw hat crew' in (c.card_origin or '').lower()
        return search_top_cards(game_state, player, 3, add_count=1, filter_fn=shc_filter,
                                source_card=card,
                                prompt="Look at top 3: choose a Straw Hat Crew card to add to hand")
    return False


# --- EB02-040: BRAND NEW WORLD ---
@register_effect("EB02-040", "main", "[Main] Look at 4, add cost 4+ to hand")
def eb02_040_brand_new_world(game_state, player, card):
    """Main: Look at top 4, reveal up to 1 card with cost 4+ and add to hand, rest to bottom."""
    def cost4_filter(c):
        return (getattr(c, 'cost', 0) or 0) >= 4
    return search_top_cards(game_state, player, 4, add_count=1, filter_fn=cost4_filter,
                            source_card=card,
                            prompt="Look at top 4: choose a card with cost 4 or more to add to hand")


# --- EB02-050: Kokoro no Chizu ---
@register_effect("EB02-050", "main", "[Main] Look at 4, add cost 4+ to hand")
def eb02_050_kokoro_no_chizu(game_state, player, card):
    """Main: Look at top 4, reveal up to 1 card with cost 4+ and add to hand, rest to bottom."""
    def cost4_filter(c):
        return (getattr(c, 'cost', 0) or 0) >= 4
    return search_top_cards(game_state, player, 4, add_count=1, filter_fn=cost4_filter,
                            source_card=card,
                            prompt="Look at top 4: choose a card with cost 4 or more to add to hand")


# --- EB02-056: Vegapunk ---
@register_effect("EB02-056", "blocker", "[Blocker]")
def eb02_056_vegapunk_blocker(game_state, player, card):
    """Blocker."""
    card.is_blocker = True
    return True


@register_effect("EB02-056", "on_play", "[On Play] Look at 5, play Scientist cost 5 or less (not Vegapunk)")
def eb02_056_vegapunk_play(game_state, player, card):
    """On Play: Look at top 5, play up to 1 Scientist Character cost 5 or less (not Vegapunk) to field, rest to bottom."""
    def scientist_filter(c):
        return ('scientist' in (c.card_origin or '').lower()
                and getattr(c, 'card_type', '') == 'CHARACTER'
                and (getattr(c, 'cost', 0) or 0) <= 5
                and 'vegapunk' not in (c.name or '').lower())
    return search_top_cards(game_state, player, 5, add_count=1, filter_fn=scientist_filter,
                            source_card=card, play_to_field=True,
                            prompt="Look at top 5: choose a Scientist Character (cost 5 or less, not Vegapunk) to play")


# --- EB02-058: UUUUUS! ---
@register_effect("EB02-058", "main", "[Main] Look at 4, add cost 4+ to hand")
def eb02_058_uuuuus(game_state, player, card):
    """Main: Look at top 4, reveal up to 1 card with cost 4+ and add to hand, rest to bottom."""
    def cost4_filter(c):
        return (getattr(c, 'cost', 0) or 0) >= 4
    return search_top_cards(game_state, player, 4, add_count=1, filter_fn=cost4_filter,
                            source_card=card,
                            prompt="Look at top 4: choose a card with cost 4 or more to add to hand")


# --- EB02-013: Carrot ---
@register_effect("EB02-013", "on_play", "[On Play] If 3+ DON, look at 7, add Zou, play Zou from hand")
def eb02_013_carrot(game_state, player, card):
    """[On Play] If 3+ DON on field, look at 7, add 1 [Zou], then play 1 [Zou] from hand."""
    total_don = len(getattr(player, 'don_pool', []))
    if total_don < 3:
        return False
    return search_top_cards(game_state, player, look_count=7, add_count=1,
        filter_fn=lambda c: 'zou' in (c.name or '').lower(),
        source_card=card,
        prompt="Carrot: Look at top 7, choose 1 [Zou] to add to hand (then you may play it)")


# --- EB02-025: Donquixote Rosinante ---
@register_effect("EB02-025", "activate", "[Activate: Main] Rest DON + this: If Rosinante leader, look at 5, play cost 2 or less rested")
def eb02_025_rosinante(game_state, player, card):
    """[Activate: Main] Rest DON and this: If Rosinante leader, look at 5, play 1 Character cost 2 or less rested."""
    if card.is_resting or getattr(card, 'main_activated_this_turn', False):
        return False
    if not player.leader or 'donquixote rosinante' not in (player.leader.name or '').lower():
        return False
    if player.don_pool.count('active') < 1:
        return False
    idx = player.don_pool.index('active')
    player.don_pool[idx] = 'rested'
    card.is_resting = True
    card.main_activated_this_turn = True
    return search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: (c.card_type == 'CHARACTER' and (c.cost or 0) <= 2),
        source_card=card, play_to_field=True, play_rested=True,
        prompt="Rosinante: Look at top 5, choose 1 Character (cost 2 or less) to play rested")


# --- EB02-028: Portgas.D.Ace ---
@register_effect("EB02-028", "on_play", "[On Play] If WB leader, look at 5, add cost 2 Character, play cost 2 from hand rested")
def eb02_028_ace(game_state, player, card):
    """[On Play] If Whitebeard Pirates leader, look at 5, add 1 cost 2 Character."""
    leader_type = (player.leader.card_origin or '').lower() if player.leader else ''
    if 'whitebeard pirates' not in leader_type:
        return False
    return search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: (c.card_type == 'CHARACTER' and (c.cost or 0) == 2),
        source_card=card,
        prompt="Ace: Look at top 5, choose 1 Character with cost 2 to add to hand (then you may play it rested)")


# --- EB02-032: Iceburg ---
@register_effect("EB02-032", "on_play", "[On Play] If 3+ DON, look at 7, add Galley-La, play from hand")
def eb02_032_iceburg(game_state, player, card):
    """[On Play] If 3+ DON on field, look at 7, add 1 [Galley-La Company], then play from hand."""
    total_don = len(getattr(player, 'don_pool', []))
    if total_don < 3:
        return False
    return search_top_cards(game_state, player, look_count=7, add_count=1,
        filter_fn=lambda c: 'galley-la company' in (c.name or '').lower(),
        source_card=card,
        prompt="Iceburg: Look at top 7, choose 1 [Galley-La Company] to add to hand (then you may play it)")
