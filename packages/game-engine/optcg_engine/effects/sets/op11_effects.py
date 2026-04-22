"""
Hardcoded effects for OP11 cards.
"""

from ..effect_registry import (
    create_bottom_deck_choice, create_ko_choice, create_play_from_hand_choice, create_return_to_hand_choice,
    create_target_choice, add_power_modifier, check_leader_type, check_life_count,
    draw_cards, get_opponent, register_effect,
    reorder_top_cards, search_top_cards,
)


# --- OP11-091: Berry Good ---
@register_effect("OP11-091", "ON_PLAY", "Opponent places 3 Events from trash at bottom of deck")
def berry_good_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    events = [c for c in opponent.trash if getattr(c, 'card_type', '') == 'EVENT'][:3]
    for event in events:
        opponent.trash.remove(event)
        opponent.deck.append(event)
    return len(events) > 0


# --- OP11-102: Camie ---
@register_effect("OP11-102", "ON_EVENT_TRIGGER", "Trash 1 from top of each Life if opponent has 2+")
def camie_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    if len(opponent.life_cards) >= 2:
        if player.life_cards:
            life = player.life_cards.pop()
            player.trash.append(life)
        if opponent.life_cards:
            life = opponent.life_cards.pop()
            opponent.trash.append(life)
        return True
    return False


# --- OP11-012: Franky ---
@register_effect("OP11-012", "ON_EVENT_ACTIVATE", "All chars gain +2000 power")
def franky_op11_effect(game_state, player, card):
    for c in player.cards_in_play:
        c.power_modifier = getattr(c, 'power_modifier', 0) + 2000
    return True


# --- OP11-119: Koby ---
@register_effect("OP11-119", "ON_PLAY", "1 char can attack active this turn")
def koby_op11_on_play(game_state, player, card):
    if player.cards_in_play:
        player.cards_in_play[0].can_attack_active = True
        return True
    return False


@register_effect("OP11-119", "WHEN_ATTACKING", "Place 2 from trash at bottom: +1000 power")
def koby_op11_attack(game_state, player, card):
    if len(player.trash) >= 2:
        for _ in range(2):
            if player.trash:
                card_to_place = player.trash.pop(0)
                player.deck.append(card_to_place)
        # Give +1000 power to a card
        if player.cards_in_play:
            player.cards_in_play[0].power_modifier = getattr(player.cards_in_play[0], 'power_modifier', 0) + 1000
        return True
    return False


# --- OP11-084: Kuzan ---
@register_effect("OP11-084", "ON_PLAY", "Trash 3 from deck")
def kuzan_on_play(game_state, player, card):
    for _ in range(3):
        if player.deck:
            player.trash.append(player.deck.pop(0))
    return True


@register_effect("OP11-084", "WHEN_ATTACKING", "Navy Leader/char can attack active")
def kuzan_attack(game_state, player, card):
    navy = [c for c in player.cards_in_play
           if 'navy' in (c.card_origin or '').lower()]
    if navy:
        navy[0].can_attack_active = True
        return True
    if player.leader and 'navy' in (player.leader.card_origin or '').lower():
        player.leader.can_attack_active = True
        return True
    return False


# --- OP11-051: Sanji ---
@register_effect("OP11-051", "ON_KO_BY_EFFECT", "Look at 5, play Straw Hat cost 5 or less")
def sanji_op11_ko(game_state, player, card):
    if len(player.deck) >= 5:
        top_5 = player.deck[:5]
        player.deck = player.deck[5:]
        straw_hat = [c for c in top_5
                    if 'straw hat crew' in (c.card_origin or '').lower()
                    and (getattr(c, 'cost', 0) or 0) <= 5
                    and getattr(c, 'card_type', '') == 'CHARACTER']
        if straw_hat:
            player.cards_in_play.append(straw_hat[0])
            top_5.remove(straw_hat[0])
        player.deck.extend(top_5)
        return True
    return False


@register_effect("OP11-051", "ON_PLAY", "Return 5000 base power char to hand")
def sanji_op11_on_play(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'power', 0) or 0) == 5000]
    if targets:
        return create_return_to_hand_choice(
            game_state, player, targets, source_card=card,
            prompt="Choose opponent's 5000 base power Character to return to hand"
        )
    return False


# --- OP11-102: Camie ---
@register_effect("OP11-102", "ON_OPPONENT_EVENT", "Trash top card from both decks")
def camie_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    if len(opponent.life_cards) >= 2:
        # Trash 1 from top of each deck
        if player.deck:
            trashed = player.deck.pop(0)
            player.trash.append(trashed)
        if opponent.deck:
            trashed = opponent.deck.pop(0)
            opponent.trash.append(trashed)
        return True
    return False


# --- OP11-012: Franky ---
@register_effect("OP11-012", "ON_OPPONENT_EVENT", "All Characters +2000 power")
def franky_op11_effect(game_state, player, card):
    for c in player.cards_in_play:
        c.power = getattr(c, 'power', 0) + 2000
    return True


# =============================================================================
# MORE LEADER CONDITION CARDS - Fish-Man
# =============================================================================

# --- OP11-023: Arlong ---
@register_effect("OP11-023", "IN_HAND", "If Leader is Fish-Man, 3 or less life, opponent 5+ rested, -3 cost")
def op11_023_arlong(game_state, player, card):
    # This is a cost reduction effect in hand
    if check_leader_type(player, "Fish-Man"):
        opponent = get_opponent(game_state, player)
        rested_count = len([c for c in opponent.cards_in_play if getattr(c, 'is_resting', False)])
        rested_count += len([d for d in opponent.don_pool if getattr(d, 'is_resting', False)])
        if check_life_count(player, 3, 'le') and rested_count >= 5:
            card.cost_modifier = getattr(card, 'cost_modifier', 0) - 3
    return True


# =============================================================================
# MORE LEADER CONDITION CARDS - Navy
# =============================================================================

# --- OP11-082: Aramaki ---
@register_effect("OP11-082", "ACTIVATE_MAIN", "Trash this: If Leader is Navy, chars can attack active, trash 2 from deck")
def op11_082_aramaki(game_state, player, card):
    if check_leader_type(player, "Navy"):
        if card in player.cards_in_play:
            player.cards_in_play.remove(card)
            player.trash.append(card)
        # Navy chars can attack active this turn
        for c in player.cards_in_play:
            if 'Navy' in (getattr(c, 'card_origin', '') or ''):
                c.can_attack_active = True
        # Trash 2 from deck
        for _ in range(2):
            if player.deck:
                player.trash.append(player.deck.pop(0))
    return True


# --- OP11-097: After All These Years I'm Losing My Edge!!! ---
@register_effect("OP11-097", "COUNTER", "+1000 power, add black cost 3 or less from trash if 10+ trash")
def op11_097_losing_edge(game_state, player, card):
    """Counter: +1000 power, add black cost 3 or less from trash if 10+ trash."""
    target = player.leader if player.leader else (player.cards_in_play[0] if player.cards_in_play else None)
    if target:
        add_power_modifier(target, 1000)
        if check_trash_count(player, 10):
            black_chars = [c for c in player.trash
                          if 'black' in (getattr(c, 'colors', '') or '').lower()
                          and (getattr(c, 'cost', 0) or 0) <= 3
                          and getattr(c, 'card_type', '') == 'CHARACTER']
            if black_chars:
                return create_target_choice(
                    game_state, player, black_chars,
                    callback_action="add_to_hand_from_trash",
                    source_card=card,
                    prompt="Choose black cost 3 or less Character from trash to add to hand"
                )
        return True
    return False


# --- OP11-001: Koby (Leader) ---
@register_effect("OP11-001", "continuous", "SWORD chars can attack chars on play turn")
def op11_001_koby_continuous(game_state, player, card):
    """Your SWORD type Characters can attack Characters on the turn they are played."""
    for char in player.cards_in_play:
        if 'sword' in (char.card_origin or '').lower():
            char.can_attack_chars_on_play = True
    return True


# --- OP11-021: Jinbe (Leader) ---
@register_effect("OP11-021", "end_of_turn", "[End of Turn] If 6- hand, set Fish-Man/Merfolk and 1 DON active")
def op11_021_jinbe_leader(game_state, player, card):
    """End of Your Turn: If 6 or less hand, set 1 Fish-Man/Merfolk and 1 DON active."""
    if len(player.hand) <= 6:
        fish_chars = [c for c in player.cards_in_play
                      if c.is_resting
                      and ('fish-man' in (c.card_origin or '').lower()
                           or 'merfolk' in (c.card_origin or '').lower())]
        rested_don = player.don_pool.count("rested")
        if rested_don:
            rested_don[0].is_resting = False
        if fish_chars:
            return create_target_choice(
                game_state, player, fish_chars,
                callback_action="set_active",
                source_card=card,
                prompt="Choose your Fish-Man/Merfolk Character to set active"
            )
        return True
    return False


# --- OP11-022: Shirahoshi (Leader) ---
@register_effect("OP11-022", "continuous", "This Leader cannot attack")
def op11_022_shirahoshi_continuous(game_state, player, card):
    """This Leader cannot attack."""
    card.cannot_attack = True
    return True


@register_effect("OP11-022", "activate", "[Activate: Main] Rest 1 DON, turn life face-up: Play cost 4 or less")
def op11_022_shirahoshi_activate(game_state, player, card):
    """Once Per Turn, Rest 1 DON, turn 1 Life face-up: Play Fish-Man/Merfolk cost 4 or less from hand."""
    if hasattr(card, 'op11_022_used') and card.op11_022_used:
        return False
    active_don = player.don_pool.count("active")
    if active_don and player.life_cards:
        active_don[0].is_resting = True
        player.life_cards[-1].is_face_up = True
        card.op11_022_used = True
        fish_chars = [c for c in player.hand
                      if getattr(c, 'card_type', '') == 'CHARACTER'
                      and (getattr(c, 'cost', 0) or 0) <= 4
                      and ('fish-man' in (c.card_origin or '').lower()
                           or 'merfolk' in (c.card_origin or '').lower())]
        if fish_chars:
            return create_play_from_hand_choice(
                game_state, player, fish_chars, source_card=card,
                prompt="Choose Fish-Man/Merfolk cost 4 or less to play from hand"
            )
        return True
    return False


# --- OP11-040: Monkey.D.Luffy (Leader) ---
@register_effect("OP11-040", "start_of_turn", "[Start of Turn] If 8+ DON, look 5 reveal Event play it")
def op11_040_luffy_leader(game_state, player, card):
    """Start of Turn: If 8+ DON, look at top 5, reveal an Event, play it without cost."""
    if len(player.don_pool) >= 8 and len(player.deck) >= 5:
        top_5 = player.deck[:5]
        events = [c for c in top_5 if getattr(c, 'card_type', '') == 'EVENT']
        if events:
            event = events[0]
            player.deck.remove(event)
            player.trash.append(event)  # Event played and trashed
        return True
    return False


# --- OP11-041: Nami (Leader) ---
@register_effect("OP11-041", "on_life_change", "[Your Turn] When card removed from Life, if 7- hand draw 1")
def op11_041_nami_leader(game_state, player, card):
    """Your Turn, Once Per Turn: When a card is removed from Life, if 7 or less hand, draw 1."""
    if hasattr(card, 'op11_041_used') and card.op11_041_used:
        return False
    if len(player.hand) <= 7:
        draw_cards(player, 1)
        card.op11_041_used = True
        return True
    return False


# --- OP11-003: Luffy ---
@register_effect("OP11-003", "on_play", "[On Play] K.O. cost 3 or less")
def op11_003_luffy(game_state, player, card):
    """On Play: K.O. opponent's cost 3 or less."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
    if targets:
        return create_ko_choice(game_state, player, targets, source_card=card,
                               prompt="Choose opponent's cost 3 or less to K.O.")
    return True


# --- OP11-004: Bonney ---
@register_effect("OP11-004", "on_play", "[On Play] Look at 5, add BONNEY")
def op11_004_bonney(game_state, player, card):
    """On Play: Look at 5, add BONNEY card."""
    looked = player.deck[:5] if len(player.deck) >= 5 else player.deck[:]
    for c in looked:
        if 'BONNEY' in (c.card_origin or ''):
            player.deck.remove(c)
            player.hand.append(c)
            break
    return True


# --- OP11-022: Koby ---
@register_effect("OP11-022", "on_play", "[On Play] If Navy leader, draw 1")
def op11_022_koby(game_state, player, card):
    """On Play: If Navy leader, draw 1."""
    if player.leader and 'Navy' in (player.leader.card_origin or ''):
        draw_cards(player, 1)
    return True


# --- OP11-040: Kaido ---
@register_effect("OP11-040", "on_play", "[On Play] K.O. cost 6 or less if Animal Kingdom leader")
def op11_040_kaido(game_state, player, card):
    """On Play: If Animal Kingdom leader, K.O. cost 6 or less."""
    if player.leader and 'Animal Kingdom Pirates' in (player.leader.card_origin or ''):
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 6]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's cost 6 or less to K.O.")
    return True


# --- OP11-060: Boa Hancock ---
@register_effect("OP11-060", "on_play", "[On Play] Bottom deck cost 3 or less")
def op11_060_hancock(game_state, player, card):
    """On Play: Bottom deck opponent's cost 3 or less."""
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
    if targets:
        return create_bottom_deck_choice(game_state, player, targets, source_card=card,
                                        prompt="Choose opponent's cost 3 or less to place at deck bottom")
    return True


# --- OP11-030: Shirahoshi ---
@register_effect("OP11-030", "activate", "[Activate: Main] Rest 1 DON + this: Look at 5, add Neptunian/Fish-Man Island")
def op11_030_shirahoshi(game_state, player, card):
    if card.is_resting or getattr(card, 'main_activated_this_turn', False):
        return False
    if player.don_pool.count("active") < 1:
        return False
    idx = player.don_pool.index("active")
    player.don_pool[idx] = "rested"
    card.is_resting = True
    card.main_activated_this_turn = True
    return search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: ('neptunian' in (c.card_origin or '').lower()
                             or 'fish-man island' in (c.card_origin or '').lower()),
        source_card=card,
        prompt="Look at top 5: choose 1 Neptunian or Fish-Man Island card to add to hand")


# --- OP11-037: Ancient Weapon Poseidon ---
@register_effect("OP11-037", "on_play", "[Main] Look at 4, add Neptunian/Fish-Man Island Character")
def op11_037_poseidon(game_state, player, card):
    return search_top_cards(game_state, player, look_count=4, add_count=1,
        filter_fn=lambda c: (c.card_type == 'CHARACTER'
                             and ('neptunian' in (c.card_origin or '').lower()
                                  or 'fish-man island' in (c.card_origin or '').lower())),
        source_card=card,
        prompt="Look at top 4: choose 1 Neptunian or Fish-Man Island Character to add to hand")


# --- OP11-048: Capone"Gang"Bege ---
@register_effect("OP11-048", "on_play", "[On Play] Look at 4, add Firetank Pirates/SHC cost 2+")
def op11_048_capone(game_state, player, card):
    return search_top_cards(game_state, player, look_count=4, add_count=1,
        filter_fn=lambda c: (('firetank pirates' in (c.card_origin or '').lower()
                              or 'straw hat crew' in (c.card_origin or '').lower())
                             and (c.cost or 0) >= 2),
        source_card=card,
        prompt="Look at top 4: choose 1 Firetank Pirates or Straw Hat Crew (cost 2+) to add to hand")


# --- OP11-049: Carrot ---
@register_effect("OP11-049", "on_play", "[On Play] Look at 3, reorder to bottom")
def op11_049_carrot(game_state, player, card):
    return reorder_top_cards(game_state, player, look_count=3, source_card=card)


# --- OP11-062: Charlotte Katakuri (Leader) ---
@register_effect("OP11-062", "on_attack", "[When Attacking] DON -1: Look at opponent's top 1, gain +1000")
def op11_062_katakuri_attack(game_state, player, card):
    if getattr(card, 'main_activated_this_turn', False):
        return True
    if player.don_pool.count("active") < 1 and player.don_pool.count("rested") < 1:
        return True
    # Pay DON -1 cost
    if player.don_pool:
        player.don_pool.pop()
    card.main_activated_this_turn = True
    # Look at opponent's top 1
    opponent = get_opponent(game_state, player)
    if opponent.deck:
        top_card = opponent.deck[0]
        game_state._log(f"Katakuri: Looked at opponent's top card: {top_card.name}")
    # Gain +1000 power
    card.power_modifier = getattr(card, 'power_modifier', 0) + 1000
    game_state._log(f"Katakuri gains +1000 power this battle")
    return True


# --- OP11-070: Charlotte Pudding ---
@register_effect("OP11-070", "on_play", "[On Play] Look at 5, add Big Mom Pirates cost 2+")
def op11_070_pudding(game_state, player, card):
    return search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: ('big mom pirates' in (c.card_origin or '').lower()
                             and (c.cost or 0) >= 2),
        source_card=card,
        prompt="Look at top 5: choose 1 Big Mom Pirates (cost 2+) to add to hand")


# --- OP11-099: I'm Gonna Be a Navy Officer!!! ---
@register_effect("OP11-099", "on_play", "[Main] Look at 3, add Navy (not self), trash rest")
def op11_099_navy_officer(game_state, player, card):
    return search_top_cards(game_state, player, look_count=3, add_count=1,
        filter_fn=lambda c: ('navy' in (c.card_origin or '').lower()
                             and c.name != "I'm Gonna Be a Navy Officer!!!"),
        source_card=card, trash_rest=True,
        prompt="Look at top 3: choose 1 Navy card to add to hand (rest trashed)")


# --- OP11-104: Shirley ---
@register_effect("OP11-104", "on_play", "[On Play] Look at 3, add Fish-Man Island")
def op11_104_shirley(game_state, player, card):
    # Optional life-manipulation cost skipped for now
    return search_top_cards(game_state, player, look_count=3, add_count=1,
        filter_fn=lambda c: 'fish-man island' in (c.card_origin or '').lower(),
        source_card=card,
        prompt="Look at top 3: choose 1 Fish-Man Island card to add to hand")


# --- OP11-036: Spotted Neptunian ---
@register_effect("OP11-036", "on_play", "[On Play] If Shirahoshi leader, look at 5, add Neptunian/Shirahoshi")
def op11_036_spotted_neptunian(game_state, player, card):
    """[On Play] If Shirahoshi leader, look at 5, add 1 Neptunian or Shirahoshi."""
    if not player.leader or 'shirahoshi' not in (player.leader.name or '').lower():
        return False
    return search_top_cards(game_state, player, look_count=5, add_count=1,
        filter_fn=lambda c: ('neptunian' in (c.card_origin or '').lower()
                             or 'shirahoshi' in (c.name or '').lower()),
        source_card=card,
        prompt="Look at top 5: choose 1 Neptunian or [Shirahoshi] to add to hand")


# =============================================================================
# OP11 GENERIC FALLBACK REGISTRATIONS
# =============================================================================

from .generic_fallback import register_generic_set_fallback


_OP11_GENERIC_TIMINGS = {
    "OP11-002": ['on_play'],
    "OP11-005": ['blocker'],
    "OP11-006": ['on_attack'],
    "OP11-007": ['activate'],
    "OP11-008": ['on_play', 'blocker'],
    "OP11-009": ['on_attack'],
    "OP11-010": ['on_play', 'on_attack'],
    "OP11-013": ['on_attack', 'blocker'],
    "OP11-014": ['activate', 'blocker'],
    "OP11-016": ['activate'],
    "OP11-018": ['on_play', 'trigger'],
    "OP11-019": ['counter', 'trigger'],
    "OP11-020": ['counter', 'trigger'],
    "OP11-023": ['trigger'],
    "OP11-024": ['continuous'],
    "OP11-025": ['on_opponent_attack'],
    "OP11-027": ['continuous'],
    "OP11-028": ['on_play', 'trigger'],
    "OP11-029": ['on_play', 'blocker'],
    "OP11-031": ['on_play', 'activate'],
    "OP11-034": ['activate'],
    "OP11-035": ['on_play'],
    "OP11-037": ['trigger'],
    "OP11-038": ['counter', 'on_play'],
    "OP11-039": ['counter', 'trigger'],
    "OP11-042": ['on_play'],
    "OP11-043": ['on_opponent_attack', 'blocker'],
    "OP11-044": ['activate'],
    "OP11-046": ['blocker'],
    "OP11-047": ['on_play'],
    "OP11-050": ['on_attack'],
    "OP11-054": ['on_play', 'blocker'],
    "OP11-056": ['on_play', 'blocker'],
    "OP11-057": ['blocker'],
    "OP11-058": ['blocker'],
    "OP11-059": ['counter', 'trigger'],
    "OP11-060": ['trigger'],
    "OP11-061": ['on_play', 'trigger'],
    "OP11-063": ['on_play'],
    "OP11-065": ['blocker'],
    "OP11-066": ['activate'],
    "OP11-067": ['end_of_turn', 'blocker'],
    "OP11-069": ['on_play'],
    "OP11-071": ['activate'],
    "OP11-072": ['activate'],
    "OP11-073": ['on_opponent_attack'],
    "OP11-074": ['activate'],
    "OP11-075": ['on_play', 'trigger'],
    "OP11-076": ['on_play', 'blocker'],
    "OP11-077": ['continuous'],
    "OP11-079": ['counter', 'trigger'],
    "OP11-080": ['counter', 'on_play'],
    "OP11-081": ['on_play', 'trigger'],
    "OP11-083": ['on_play', 'blocker'],
    "OP11-085": ['on_play'],
    "OP11-086": ['on_play', 'activate'],
    "OP11-088": ['blocker'],
    "OP11-090": ['blocker'],
    "OP11-092": ['on_play'],
    "OP11-095": ['on_play'],
    "OP11-096": ['blocker'],
    "OP11-098": ['on_play', 'trigger'],
    "OP11-099": ['trigger'],
    "OP11-100": ['on_play'],
    "OP11-101": ['blocker'],
    "OP11-103": ['activate'],
    "OP11-106": ['on_play'],
    "OP11-107": ['activate', 'blocker'],
    "OP11-108": ['on_play'],
    "OP11-109": ['on_play'],
    "OP11-110": ['on_play'],
    "OP11-112": ['blocker'],
    "OP11-114": ['counter', 'on_play'],
    "OP11-115": ['counter', 'trigger'],
    "OP11-116": ['on_play', 'trigger'],
    "OP11-117": ['activate'],
    "OP11-118": ['on_attack'],
}


register_generic_set_fallback(_OP11_GENERIC_TIMINGS, "OP11")
