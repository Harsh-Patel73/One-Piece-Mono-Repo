"""
Hardcoded effects for OP12 cards.
"""

from ..hardcoded import (
    add_power_modifier, check_leader_type, check_life_count,
    create_bottom_deck_choice, create_ko_choice, create_mode_choice, create_return_to_hand_choice,
    draw_cards, filter_by_max_cost, get_opponent, register_effect, search_top_cards, trash_from_hand,
)


# --- OP12-054: Marshall.D.Teach ---
@register_effect("OP12-054", "ON_PLAY", "If Seven Warlords Leader, return cost 1 or less to hand")
def teach_op12_effect(game_state, player, card):
    if player.leader and 'seven warlords' in (player.leader.card_origin or '').lower():
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play
                  if c != card and (getattr(c, 'cost', 0) or 0) <= 1]
        if targets:
            return create_return_to_hand_choice(game_state, player, targets, source_card=card,
                                                 prompt="Choose opponent's cost 1 or less to return to hand")
    return False


# --- OP12-056: Monkey.D.Garp ---
@register_effect("OP12-056", "ON_PLAY", "Trash 1: Play blue Navy 8000 power or less")
def garp_op12_effect(game_state, player, card):
    if player.hand:
        trash_from_hand(player, 1, game_state, card)
        for i, hand_card in enumerate(player.hand):
            if ('blue' in (getattr(hand_card, 'colors', '') or '').lower()
                and 'navy' in (hand_card.card_origin or '').lower()
                and (getattr(hand_card, 'power', 0) or 0) <= 8000
                and getattr(hand_card, 'card_type', '') == 'CHARACTER'
                and 'Monkey.D.Garp' not in getattr(hand_card, 'name', '')):
                char = player.hand.pop(i)
                player.cards_in_play.append(char)
                return True
    return False


# --- OP12-116: We'll Ring the Bell Waiting for You!! ---
@register_effect("OP12-116", "MAIN", "Look at 5, add up to 2 Shandian/Noland to hand")
def well_ring_the_bell_effect(game_state, player, card):
    """Look at 5 cards, add up to 2 Shandian Warrior or Mont Blanc Noland to hand."""
    if len(player.deck) >= 5:
        top_5 = player.deck[:5]
        player.deck = player.deck[5:]

        matches = [c for c in top_5
                  if 'shandian warrior' in (c.card_origin or '').lower()
                  or 'Mont Blanc Noland' in getattr(c, 'name', '')]

        # Add up to 2 to hand
        added = 0
        for match in matches[:2]:
            player.hand.append(match)
            top_5.remove(match)
            added += 1

        # Place rest at bottom
        player.deck.extend(top_5)
        return added > 0
    return False


# =============================================================================
# REVEAL COST CARDS
# =============================================================================

# --- OP12-003: Crocus ---
@register_effect("OP12-003", "ON_KO", "Reveal 2 Events: Play red char 3000 power or less")
def op12_003_crocus(game_state, player, card):
    events = [c for c in player.hand if getattr(c, 'card_type', '') == 'EVENT']
    if len(events) >= 2:
        red_chars = [c for c in player.hand
                     if getattr(c, 'card_type', '') == 'CHARACTER'
                     and 'Red' in (getattr(c, 'colors', []) or [])
                     and (getattr(c, 'power', 0) or 0) <= 3000]
        if red_chars:
            to_play = red_chars[0]
            player.hand.remove(to_play)
            player.cards_in_play.append(to_play)
    return True


# --- OP12-009: Jinbe ---
@register_effect("OP12-009", "ON_PLAY", "Reveal 2 Events: Gain Rush and +1000 power")
def op12_009_jinbe(game_state, player, card):
    events = [c for c in player.hand if getattr(c, 'card_type', '') == 'EVENT']
    if len(events) >= 2:
        card.has_rush = True
        add_power_modifier(card, 1000)
    return True


# --- OP12-015: Monkey.D.Luffy ---
@register_effect("OP12-015", "ON_PLAY", "Reveal 2 Events: Play red char 3000 power or less")
def op12_015_luffy(game_state, player, card):
    events = [c for c in player.hand if getattr(c, 'card_type', '') == 'EVENT']
    if len(events) >= 2:
        red_chars = [c for c in player.hand
                     if getattr(c, 'card_type', '') == 'CHARACTER'
                     and (getattr(c, 'power', 0) or 0) <= 3000]
        if red_chars:
            to_play = red_chars[0]
            player.hand.remove(to_play)
            player.cards_in_play.append(to_play)
    return True


# --- OP12-053: Borsalino ---
@register_effect("OP12-053", "OPPONENTS_TURN", "If Leader is Navy, +2000 power")
def op12_053_borsalino(game_state, player, card):
    if check_leader_type(player, "Navy"):
        add_power_modifier(card, 2000)
    return True


# --- OP12-080: Baratie ---
@register_effect("OP12-080", "ACTIVATE_MAIN", "Place at bottom: If Leader is Sanji, look at 3, add Event to hand")
def op12_080_baratie(game_state, player, card):
    if check_leader_name(player, "Sanji"):
        if card in player.cards_in_play:
            player.cards_in_play.remove(card)
            player.deck.append(card)
        top3 = player.deck[:3]
        events = [c for c in top3 if getattr(c, 'card_type', '') == 'EVENT']
        if events:
            to_add = events[0]
            player.deck.remove(to_add)
            player.hand.append(to_add)
        for c in top3:
            if c in player.deck:
                player.deck.remove(c)
                player.deck.append(c)
    return True


# --- OP12-060: Boeuf Burst ---
@register_effect("OP12-060", "MAIN", "If Leader is multicolored, choose: return cost 4 or draw 2")
def op12_060_boeuf_burst(game_state, player, card):
    is_multicolor = player.leader and len(getattr(player.leader, 'colors', []) or []) > 1
    if is_multicolor:
        # Player chooses between returning opponent's character or drawing
        modes = [
            {"id": "return", "label": "Return to Hand", "description": "Return opponent's cost 4 or less Character to hand"},
            {"id": "draw", "label": "Draw 2", "description": "Draw 2 cards"}
        ]
        def callback(selected: list[str]) -> None:
            selected_mode = selected[0] if selected else None
            if selected_mode == "return":
                opponent = get_opponent(game_state, player)
                targets = filter_by_max_cost(opponent.cards_in_play, 4)
                if targets:
                    create_return_to_hand_choice(game_state, player, targets, source_card=card,
                                                 prompt="Choose opponent's cost 4 or less Character to return to hand")
            elif selected_mode == "draw":
                draw_cards(player, 2)
                game_state._log(f"{player.name} drew 2 cards")

        return create_mode_choice(game_state, player, modes, source_card=card, callback=callback,
                                   prompt="Choose an effect: Return opponent's cost 4 or less to hand, OR Draw 2 cards")
    return True


# --- OP12-107: Donquixote Doflamingo ---
@register_effect("OP12-107", "CONTINUOUS", "If 2 or less life, gain Rush")
def op12_107_doflamingo_continuous(game_state, player, card):
    """Continuous: If 2 or less life, this gains Rush."""
    if check_life_count(player, 2):
        card.has_rush = True
        return True
    return False


@register_effect("OP12-107", "ON_KO", "Add deck to life")
def op12_107_doflamingo_ko(game_state, player, card):
    """On KO (Opponent's Turn): Add deck card to life."""
    if player.deck:
        deck_card = player.deck.pop(0)
        player.life_cards.append(deck_card)
        return True
    return False


# --- OP12-115: I Love You!! ---
@register_effect("OP12-115", "COUNTER", "+2000 power, add Law from trash if 2 or less life")
def op12_115_i_love_you(game_state, player, card):
    """Counter: +2000 power, add Trafalgar Law from trash if 2 or less life."""
    target = player.leader if player.leader else (player.cards_in_play[0] if player.cards_in_play else None)
    if target:
        add_power_modifier(target, 2000)
        if check_life_count(player, 2):
            laws = [c for c in player.trash if 'Trafalgar Law' in getattr(c, 'name', '')]
            if laws:
                law = laws[0]
                player.trash.remove(law)
                player.hand.append(law)
        return True
    return False


# --- OP12-100: Sabo ---
@register_effect("OP12-100", "CONTINUOUS", "If 3 or less life, gain Blocker and +3 cost")
def op12_100_sabo_continuous(game_state, player, card):
    """Continuous: If 3 or less life, gain Blocker and +3 cost."""
    if check_life_count(player, 3):
        card.has_blocker = True
        card.cost_modifier = getattr(card, 'cost_modifier', 0) + 3
        return True
    return False


@register_effect("OP12-100", "ON_PLAY", "Add life to hand: Draw 2 and trash 1")
def op12_100_sabo_on_play(game_state, player, card):
    """On Play: Add life to hand, draw 2 and trash 1."""
    if player.life_cards:
        life = player.life_cards.pop()
        player.hand.append(life)
        draw_cards(player, 2)
        trash_from_hand(player, 1, game_state, card)
        return True
    return False


# --- OP12-001: Silvers Rayleigh (Leader) ---
@register_effect("OP12-001", "activate", "[Activate: Main] Reveal 2 Events: K.O. cost 3 or less")
def op12_001_rayleigh_leader(game_state, player, card):
    """Once Per Turn: Reveal 2 Events from hand, K.O. opponent's cost 3 or less Character."""
    if hasattr(card, 'op12_001_used') and card.op12_001_used:
        return False
    events = [c for c in player.hand if getattr(c, 'card_type', '') == 'EVENT']
    if len(events) >= 2:
        card.op12_001_used = True
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
        if targets:
            return create_ko_choice(
                game_state, player, targets, source_card=card,
                prompt="Choose opponent's cost 3 or less Character to KO"
            )
        return True
    return False


# --- OP12-020: Roronoa Zoro (Leader) ---
@register_effect("OP12-020", "activate", "[DON!! x3] If Leader battles char, set Leader active, +2000")
def op12_020_zoro_leader(game_state, player, card):
    """DON x3, Once Per Turn: If this Leader battles opponent's Character during this turn, set Leader active, +2000."""
    if getattr(card, 'attached_don', 0) >= 3:
        if hasattr(card, 'op12_020_used') and card.op12_020_used:
            return False
        card.is_resting = False
        card.power_modifier = getattr(card, 'power_modifier', 0) + 2000
        card.op12_020_used = True
        return True
    return False


# --- OP12-040: Kuzan (Leader) ---
@register_effect("OP12-040", "on_trash_from_hand", "When card trashed by Navy effect, draw that many")
def op12_040_kuzan_leader(game_state, player, card):
    """When a card is trashed from hand by Navy effect, draw cards equal to number trashed."""
    if hasattr(player, 'cards_trashed_by_navy') and player.cards_trashed_by_navy > 0:
        draw_cards(player, player.cards_trashed_by_navy)
        player.cards_trashed_by_navy = 0
        return True
    return False


# --- OP12-041: Sanji (Leader) ---
@register_effect("OP12-041", "activate", "[Activate: Main] DON -1: Activate SHC Event cost 3 or less")
def op12_041_sanji_activate(game_state, player, card):
    """Once Per Turn, DON -1: Activate Straw Hat Crew Event cost 3 or less from hand."""
    if hasattr(card, 'op12_041_used') and card.op12_041_used:
        return False
    if len(player.don_pool) >= 1:
        shc_events = [c for c in player.hand
                      if getattr(c, 'card_type', '') == 'EVENT'
                      and 'straw hat crew' in (c.card_origin or '').lower()
                      and (getattr(c, 'cost', 0) or 0) <= 3]
        if shc_events:
            don = player.don_pool.pop()
            if hasattr(player, 'don_deck'):
                player.don_deck.append(don)
            event = shc_events[0]
            player.hand.remove(event)
            player.trash.append(event)
            card.op12_041_used = True
            return True
    return False


# --- OP12-061: Donquixote Rosinante (Leader) ---
@register_effect("OP12-061", "on_ko_prevention", "[Once Per Turn] If Trafalgar Law would be K.O.'d, add life to hand instead")
def op12_061_rosinante_leader(game_state, player, card):
    """Once Per Turn: If your Trafalgar Law would be K.O.'d, add 1 Life to hand instead."""
    if hasattr(card, 'op12_061_used') and card.op12_061_used:
        return False
    if player.life_cards:
        life = player.life_cards.pop()
        player.hand.append(life)
        card.op12_061_used = True
        return True
    return False


# --- OP12-081: Koala (Leader) ---
@register_effect("OP12-081", "on_attack", "When attacking Leader, if 2+ cost 8+ chars, draw 1")
def op12_081_koala_leader(game_state, player, card):
    """When this Leader attacks opponent's Leader, if 2+ cost 8+ Characters, draw 1."""
    cost_8_chars = [c for c in player.cards_in_play if (getattr(c, 'cost', 0) or 0) >= 8]
    if len(cost_8_chars) >= 2:
        draw_cards(player, 1)
        return True
    return False


# --- OP12-004: Luffy ---
@register_effect("OP12-004", "on_play", "[On Play] K.O. cost 5 or less")
def op12_004_luffy(game_state, player, card):
    """On Play: K.O. opponent's cost 5 or less."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 5]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                               prompt="Choose opponent's cost 5 or less to K.O.")
    return True


# --- OP12-022: Sengoku ---
@register_effect("OP12-022", "on_play", "[On Play] If Navy leader, bottom deck cost 5 or less")
def op12_022_sengoku(game_state, player, card):
    """On Play: If Navy leader, bottom deck opponent's cost 5 or less."""
    if player.leader and 'Navy' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 5]
        if targets:
            return create_bottom_deck_choice(game_state, player, targets, source_card=card,
                                            prompt="Choose opponent's cost 5 or less to place at deck bottom")
    return True


# --- OP12-040: Law ---
@register_effect("OP12-040", "on_play", "[On Play] Return cost 5 or less to hand")
def op12_040_law(game_state, player, card):
    """On Play: Return opponent's cost 5 or less to hand."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 5]
    if targets:
        return create_return_to_hand_choice(game_state, player, targets, source_card=card,
                                           prompt="Choose opponent's cost 5 or less to return to hand")
    return True


# --- OP12-060: Franky ---
@register_effect("OP12-060", "on_play", "[On Play] Draw 2, trash 1")
def op12_060_franky(game_state, player, card):
    """On Play: Draw 2 and trash 1."""
    draw_cards(player, 2)
    trash_from_hand(player, 1, game_state, card)
    return True


# --- OP12-006: Shakuyaku ---
@register_effect("OP12-006", "on_play", "[On Play] Look at 5, add Monkey.D.Luffy or red Event")
def op12_006_shakuyaku(game_state, player, card):
    return search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: ('monkey.d.luffy' in (c.name or '').lower()
                             or (c.card_type == 'EVENT' and 'Red' in (c.colors or []))),
        source_card=card,
        prompt="Look at top 5: choose 1 Monkey.D.Luffy or red Event to add to hand")


# --- OP12-014: Boa Hancock ---
@register_effect("OP12-014", "on_play", "[On Play] Look at 5, add Monkey.D.Luffy or red Event")
def op12_014_hancock(game_state, player, card):
    return search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: ('monkey.d.luffy' in (c.name or '').lower()
                             or (c.card_type == 'EVENT' and 'Red' in (c.colors or []))),
        source_card=card,
        prompt="Look at top 5: choose 1 Monkey.D.Luffy or red Event to add to hand")


# --- OP12-017: Color of Observation Haki ---
@register_effect("OP12-017", "on_play", "[Main] Look at 4, add red Event or Character cost 3+")
def op12_017_observation_haki(game_state, player, card):
    # Optional DON give to Silvers Rayleigh skipped for now
    return search_top_cards(game_state, player, look_count=4, add_count=1,
        filter_fn=lambda c: ((c.card_type == 'EVENT' and 'Red' in (c.colors or []))
                             or (c.card_type == 'CHARACTER' and (c.cost or 0) >= 3)),
        source_card=card,
        prompt="Look at top 4: choose 1 red Event or Character (cost 3+) to add to hand")


# --- OP12-047: Sengoku ---
@register_effect("OP12-047", "on_play", "[On Play] Optional trash 1: Look at 5, add up to 2 Navy (not Sengoku)")
def op12_047_sengoku(game_state, player, card):
    # Optional trash 1 from hand (skip for now, just do the search)
    return search_top_cards(game_state, player, look_count=5, add_count=2,
        filter_fn=lambda c: ('navy' in (c.card_origin or '').lower()
                             and 'sengoku' not in (c.name or '').lower()),
        source_card=card,
        prompt="Look at top 5: choose up to 2 Navy cards (not Sengoku) to add to hand")


# --- OP12-071: Charlotte Pudding ---
@register_effect("OP12-071", "on_play", "[On Play] Look at 4, add Sanji or Event")
def op12_071_pudding(game_state, player, card):
    return search_top_cards(game_state, player, look_count=4, add_count=1,
        filter_fn=lambda c: ('sanji' in (c.name or '').lower()
                             or c.card_type == 'EVENT'),
        source_card=card,
        prompt="Look at top 4: choose 1 Sanji or Event to add to hand")


# --- OP12-097: Captains Assembled ---
@register_effect("OP12-097", "on_play", "[Main] Look at 3, add Revolutionary Army (not self), trash rest")
def op12_097_captains(game_state, player, card):
    return search_top_cards(game_state, player, look_count=3, add_count=1,
        filter_fn=lambda c: ('revolutionary army' in (c.card_origin or '').lower()
                             and 'captains assembled' not in (c.name or '').lower()),
        source_card=card, trash_rest=True,
        prompt="Look at top 3: choose 1 Revolutionary Army card to add to hand (rest trashed)")


# --- OP12-108: Donquixote Rosinante ---
@register_effect("OP12-108", "on_play", "[On Play] Look at 5, add Trafalgar Law")
def op12_108_rosinante(game_state, player, card):
    return search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: 'trafalgar law' in (c.name or '').lower(),
        source_card=card,
        prompt="Look at top 5: choose 1 Trafalgar Law to add to hand")


# --- OP12-116: We'll Ring the Bell Waiting for You!! ---
@register_effect("OP12-116", "on_play", "[Main] Look at 5, add up to 2 Shandian Warrior chars or Mont Blanc Noland")
def op12_116_ring_bell(game_state, player, card):
    return search_top_cards(game_state, player, look_count=5, add_count=2,
        filter_fn=lambda c: (('shandian warrior' in (c.card_origin or '').lower() and c.card_type == 'CHARACTER')
                             or 'mont blanc noland' in (c.name or '').lower()),
        source_card=card,
        prompt="Look at top 5: choose up to 2 Shandian Warrior Characters or Mont Blanc Noland")


# --- OP12-028: Kouzuki Hiyori ---
@register_effect("OP12-028", "activate", "[Activate: Main] Rest DON + this: If Zoro leader, look at 5, add Slash/green Event")
def op12_028_hiyori(game_state, player, card):
    """[Activate: Main] Rest 1 DON and this: If Roronoa Zoro leader, look at 5, add Slash attr or green Event."""
    if card.is_resting or getattr(card, 'main_activated_this_turn', False):
        return False
    if not player.leader or 'roronoa zoro' not in (player.leader.name or '').lower():
        return False
    if player.don_pool.count('active') < 1:
        return False
    idx = player.don_pool.index('active')
    player.don_pool[idx] = 'rested'
    card.is_resting = True
    card.main_activated_this_turn = True
    return search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: ((getattr(c, 'attribute', '') or '').lower() == 'slash'
                             or (c.card_type == 'EVENT'
                                 and 'Green' in (c.colors if isinstance(c.colors, list) else [c.colors or '']))),
        source_card=card,
        prompt="Hiyori: Look at top 5, choose 1 Slash attribute card or green Event to add to hand")


# --- OP12-034: Perona ---
@register_effect("OP12-034", "on_play", "[On Play] If Slash leader, look at 5, add Slash/green Event")
def op12_034_perona(game_state, player, card):
    """[On Play] If Slash attribute leader, look at 5, add 1 Slash attr or green Event."""
    leader_attr = (getattr(player.leader, 'attribute', '') or '').lower() if player.leader else ''
    if leader_attr != 'slash':
        return False
    return search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: ((getattr(c, 'attribute', '') or '').lower() == 'slash'
                             or (c.card_type == 'EVENT'
                                 and 'Green' in (c.colors if isinstance(c.colors, list) else [c.colors or '']))),
        source_card=card,
        prompt="Perona: Look at top 5, choose 1 Slash attribute card or green Event to add to hand")


# --- OP12-079: Luffy Is the Man Who Will Be King of the Pirates!!! ---
@register_effect("OP12-079", "on_play", "[Main] If Sanji leader, look at 3, add any 1 card")
def op12_079_luffy_king(game_state, player, card):
    """[Main] If Sanji leader, look at 3, add up to 1 card (no filter)."""
    if not player.leader or 'sanji' not in (player.leader.name or '').lower():
        return False
    return search_top_cards(game_state, player, look_count=3, add_count=1,
        filter_fn=None,
        source_card=card,
        prompt="Look at top 3: choose up to 1 card to add to hand")


# --- OP12-086: Koala ---
@register_effect("OP12-086", "on_play", "[On Play] If RevArmy leader, look at 3, add RevArmy (not self) or Nico Robin, trash rest")
def op12_086_koala(game_state, player, card):
    """[On Play] If Revolutionary Army leader, look at 3, add RevArmy (not Koala) or Nico Robin, trash rest."""
    leader_type = (player.leader.card_origin or '').lower() if player.leader else ''
    if 'revolutionary army' not in leader_type:
        return False
    return search_top_cards(game_state, player, look_count=3, add_count=1,
        filter_fn=lambda c: (('revolutionary army' in (c.card_origin or '').lower()
                              and 'koala' not in (c.name or '').lower())
                             or 'nico robin' in (c.name or '').lower()),
        source_card=card, trash_rest=True,
        prompt="Koala: Look at top 3, choose 1 Revolutionary Army (not Koala) or Nico Robin to add to hand (rest trashed)")
