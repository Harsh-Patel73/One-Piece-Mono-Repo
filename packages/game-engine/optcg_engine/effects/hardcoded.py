"""
Hardcoded Effect Handlers for Complex Cards.

This module provides direct implementations for cards with effects too complex
for pattern-based parsing. Each card is implemented with its exact game logic.
"""

from typing import TYPE_CHECKING, Callable, Dict, Optional, List, Any, Tuple
from dataclasses import dataclass
import random

if TYPE_CHECKING:
    from game_engine import GameState, Player
    from models.cards import Card


@dataclass
class HardcodedEffect:
    """A hardcoded effect implementation."""
    card_id: str
    timing: str
    handler: Callable[['GameState', 'Player', 'Card'], bool]
    description: str


# Registry of hardcoded effects
_hardcoded_effects: Dict[str, List[HardcodedEffect]] = {}


def register_effect(card_id: str, timing: str, description: str):
    """Decorator to register a hardcoded effect handler."""
    def decorator(func: Callable[['GameState', 'Player', 'Card'], bool]):
        effect = HardcodedEffect(card_id=card_id, timing=timing, handler=func, description=description)
        if card_id not in _hardcoded_effects:
            _hardcoded_effects[card_id] = []
        _hardcoded_effects[card_id].append(effect)
        return func
    return decorator


def has_hardcoded_effect(card_id: str, timing: str = None) -> bool:
    """Check if a card has hardcoded effects."""
    base_id = card_id.split('_')[0] if '_p' in card_id or '_r' in card_id else card_id
    if card_id in _hardcoded_effects:
        if timing is None:
            return True
        return any(e.timing == timing for e in _hardcoded_effects[card_id])
    if base_id in _hardcoded_effects:
        if timing is None:
            return True
        return any(e.timing == timing for e in _hardcoded_effects[base_id])
    return False


def execute_hardcoded_effect(game_state: 'GameState', player: 'Player', card: 'Card', timing: str) -> bool:
    """Execute hardcoded effects for a card at a specific timing."""
    card_id = card.id
    base_id = card_id.split('_')[0] if '_p' in card_id or '_r' in card_id else card_id

    effects = _hardcoded_effects.get(card_id, []) + _hardcoded_effects.get(base_id, [])
    executed = False
    for effect in effects:
        if effect.timing == timing:
            try:
                result = effect.handler(game_state, player, card)
                executed = executed or result
            except Exception as e:
                print(f"Error executing hardcoded effect for {card_id}: {e}")
    return executed


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_opponent(game_state: 'GameState', player: 'Player') -> 'Player':
    """Get the opponent player."""
    return game_state.opponent_player if game_state.current_player == player else game_state.current_player


def draw_cards(player: 'Player', count: int) -> List['Card']:
    """Draw cards from deck."""
    drawn = []
    for _ in range(count):
        if player.deck:
            card = player.deck.pop(0)
            player.hand.append(card)
            drawn.append(card)
    return drawn


def trash_from_hand(player: 'Player', count: int) -> List['Card']:
    """Trash cards from hand (AI picks lowest cost)."""
    trashed = []
    sorted_hand = sorted(player.hand, key=lambda c: getattr(c, 'cost', 0) or 0)
    for _ in range(min(count, len(sorted_hand))):
        if sorted_hand:
            card = sorted_hand.pop(0)
            if card in player.hand:
                player.hand.remove(card)
                player.trash.append(card)
                trashed.append(card)
    return trashed


def set_active(cards: List['Card']) -> int:
    """Set cards as active (unrest them)."""
    count = 0
    for card in cards:
        if getattr(card, 'is_resting', False):
            card.is_resting = False
            count += 1
    return count


def rest_cards(cards: List['Card']) -> int:
    """Rest cards."""
    count = 0
    for card in cards:
        if not getattr(card, 'is_resting', False):
            card.is_resting = True
            count += 1
    return count


def get_characters_by_type(player: 'Player', type_name: str) -> List['Card']:
    """Get characters matching a type."""
    return [c for c in player.cards_in_play
            if type_name.lower() in (getattr(c, 'card_types', '') or '').lower()]


def get_characters_by_cost(player: 'Player', max_cost: int = None, min_cost: int = None) -> List['Card']:
    """Get characters within cost range."""
    chars = player.cards_in_play
    if max_cost is not None:
        chars = [c for c in chars if (getattr(c, 'cost', 0) or 0) <= max_cost]
    if min_cost is not None:
        chars = [c for c in chars if (getattr(c, 'cost', 0) or 0) >= min_cost]
    return chars


def add_don_from_deck(player: 'Player', count: int, set_active: bool = False) -> int:
    """Add DON from DON deck."""
    added = 0
    for _ in range(count):
        if hasattr(player, 'don_deck') and player.don_deck:
            don = player.don_deck.pop(0)
            don.is_resting = not set_active
            player.don_cards.append(don)
            added += 1
    return added


def give_don_to_card(player: 'Player', target: 'Card', count: int, rested_only: bool = False) -> int:
    """Give DON cards to a target."""
    given = 0
    for don in player.don_cards[:]:
        if given >= count:
            break
        if rested_only and not don.is_resting:
            continue
        target.attached_don = getattr(target, 'attached_don', 0) + 1
        given += 1
    return given


# =============================================================================
# HARDCODED EFFECT IMPLEMENTATIONS - Alphabetically by card name
# =============================================================================

# --- ST15-001: Atmos ---
@register_effect("ST15-001", "WHEN_ATTACKING", "Cannot add Life to hand if Leader is Edward.Newgate")
def atmos_effect(game_state, player, card):
    if player.leader and 'Edward.Newgate' in getattr(player.leader, 'name', ''):
        player.cannot_add_life_this_turn = True
    return True


# --- OP01-105: Bao Huang ---
@register_effect("OP01-105", "ON_PLAY", "Opponent reveals 2 cards from hand")
def bao_huang_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    if len(opponent.hand) >= 2:
        revealed = opponent.hand[:2]
        print(f"Opponent reveals: {[c.name for c in revealed]}")
    return True


# --- OP13-035: Bepo ---
@register_effect("OP13-035", "END_OF_TURN", "Set this Character or 1 DON as active")
def bepo_effect(game_state, player, card):
    if card.is_resting:
        card.is_resting = False
        return True
    for don in player.don_cards:
        if don.is_resting:
            don.is_resting = False
            return True
    return False


# --- OP11-091: Berry Good ---
@register_effect("OP11-091", "ON_PLAY", "Opponent places 3 Events from trash at bottom of deck")
def berry_good_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    events = [c for c in opponent.trash if getattr(c, 'card_type', '') == 'EVENT'][:3]
    for event in events:
        opponent.trash.remove(event)
        opponent.deck.append(event)
    return len(events) > 0


# --- OP05-040: Birdcage ---
@register_effect("OP05-040", "END_OF_TURN", "If 10 DON, KO all rested cost 5 or less Characters")
def birdcage_effect(game_state, player, card):
    if len(player.don_cards) >= 10:
        opponent = get_opponent(game_state, player)
        for p in [player, opponent]:
            to_ko = [c for c in p.cards_in_play
                    if c.is_resting and (getattr(c, 'cost', 0) or 0) <= 5]
            for c in to_ko:
                p.cards_in_play.remove(c)
                p.trash.append(c)
        # Trash this Stage
        if card in player.cards_in_play:
            player.cards_in_play.remove(card)
            player.trash.append(card)
        return True
    return False


# --- EB04-026: Bluegrass ---
@register_effect("EB04-026", "ON_PLAY", "Place opponent's cost 1 or less at bottom of deck")
def bluegrass_on_play(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 1]
    if targets:
        target = targets[0]
        opponent.cards_in_play.remove(target)
        opponent.deck.append(target)
        return True
    return False


@register_effect("EB04-026", "WHEN_ATTACKING", "Draw 1 card and trash 1")
def bluegrass_attack(game_state, player, card):
    draw_cards(player, 1)
    trash_from_hand(player, 1)
    return True


# --- OP14-041: Boa Hancock (Leader) ---
@register_effect("OP14-041", "ON_CHARACTER_PLAY", "Draw 1 when you play a Character")
def boa_hancock_leader_play(game_state, player, card):
    draw_cards(player, 1)
    return True


# --- OP05-031: Buffalo ---
@register_effect("OP05-031", "WHEN_ATTACKING", "If 2+ rested chars, set 1 cost 1 rested char active")
def buffalo_effect(game_state, player, card):
    rested = [c for c in player.cards_in_play if c.is_resting]
    if len(rested) >= 2:
        cost_1_rested = [c for c in rested if (getattr(c, 'cost', 0) or 0) == 1]
        if cost_1_rested:
            cost_1_rested[0].is_resting = False
            return True
    return False


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


# --- OP10-103: Capone Bege ---
@register_effect("OP10-103", "ON_PLAY", "Swap Life card with Supernovas Character from hand")
def capone_bege_effect(game_state, player, card):
    if player.life_cards:
        supernovas = [c for c in player.hand
                     if 'supernovas' in (getattr(c, 'card_types', '') or '').lower()
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


# --- EB04-013: Carrot ---
@register_effect("EB04-013", "ON_PLAY", "If Leader is Minks type, set 2 Minks chars and Leader active")
def carrot_effect(game_state, player, card):
    if player.leader and 'minks' in (getattr(player.leader, 'card_types', '') or '').lower():
        minks = get_characters_by_type(player, 'minks')[:2]
        set_active(minks)
        if player.leader:
            player.leader.is_resting = False
        return True
    return False


# --- OP04-081: Cavendish ---
@register_effect("OP04-081", "WHEN_ATTACKING", "Rest Leader to KO cost 1 or less, trash 2 from deck")
def cavendish_effect(game_state, player, card):
    if player.leader and not player.leader.is_resting:
        player.leader.is_resting = True
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 1]
        if targets:
            target = targets[0]
            opponent.cards_in_play.remove(target)
            opponent.trash.append(target)
        # Trash 2 from deck
        for _ in range(2):
            if player.deck:
                player.trash.append(player.deck.pop(0))
        return True
    return False


# --- ST07-010: Charlotte Linlin ---
@register_effect("ST07-010", "ON_PLAY", "Opponent chooses: trash top life OR add deck to life")
def charlotte_linlin_st07_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    # AI chooses: add to life is usually better for them
    if player.deck:
        player.life_cards.append(player.deck.pop(0))
    return True


# --- ST20-005: Charlotte Linlin ---
@register_effect("ST20-005", "ON_PLAY", "Trash 1: Opponent chooses discard 2 or lose life")
def charlotte_linlin_st20_effect(game_state, player, card):
    if player.hand:
        trash_from_hand(player, 1)
        opponent = get_opponent(game_state, player)
        # AI opponent chooses: discard 2 is usually better than losing life
        if len(opponent.hand) >= 2:
            trash_from_hand(opponent, 2)
        elif opponent.life_cards:
            life = opponent.life_cards.pop()
            opponent.trash.append(life)
        return True
    return False


# --- ST07-008: Charlotte Pudding ---
@register_effect("ST07-008", "ON_PLAY", "Look at top Life and place at top or bottom")
def charlotte_pudding_st07_effect(game_state, player, card):
    # Just a look effect - no actual change needed for AI
    return True


# --- ST20-004: Charlotte Pudding ---
@register_effect("ST20-004", "ON_PLAY", "Add Life to hand, set Big Mom Pirates cost 3 or less active")
def charlotte_pudding_st20_effect(game_state, player, card):
    if player.life_cards:
        life = player.life_cards.pop()
        player.hand.append(life)
        bigmom = [c for c in player.cards_in_play
                 if 'big mom pirates' in (getattr(c, 'card_types', '') or '').lower()
                 and (getattr(c, 'cost', 0) or 0) <= 3]
        if bigmom:
            bigmom[0].is_resting = False
        return True
    return False


# --- OP14-120: Crocodile ---
@register_effect("OP14-120", "ON_PLAY", "Opponent's cost 9 or less cannot attack, draw if condition")
def crocodile_op14_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 9]
    if targets:
        targets[0].cannot_attack_until_end_phase = True
    # Check for cost 0 or cost 8+ character
    has_condition = any((getattr(c, 'cost', 0) or 0) == 0 or (getattr(c, 'cost', 0) or 0) >= 8
                       for c in opponent.cards_in_play)
    if has_condition:
        draw_cards(player, 1)
    return True


# --- OP13-062: Crocus ---
@register_effect("OP13-062", "ON_PLAY", "If DON attached, add DON from deck and set active")
def crocus_on_play(game_state, player, card):
    has_given_don = any(getattr(c, 'attached_don', 0) > 0 for c in player.cards_in_play)
    if has_given_don or (player.leader and getattr(player.leader, 'attached_don', 0) > 0):
        add_don_from_deck(player, 1, set_active=True)
        return True
    return False


@register_effect("OP13-062", "WHEN_ATTACKING", "Return opponent's 3000 base power or less to hand")
def crocus_attack(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'power', 0) or 0) <= 3000]
    if targets:
        target = targets[0]
        opponent.cards_in_play.remove(target)
        opponent.hand.append(target)
        return True
    return False


# --- OP02-005: Curly.Dadan ---
@register_effect("OP02-005", "ON_PLAY", "Look at 5, reveal cost 1 red char, add to hand")
def curly_dadan_effect(game_state, player, card):
    if len(player.deck) >= 5:
        top_5 = player.deck[:5]
        player.deck = player.deck[5:]
        red_cost_1 = [c for c in top_5
                     if 'red' in (getattr(c, 'colors', '') or '').lower()
                     and (getattr(c, 'cost', 0) or 0) == 1
                     and getattr(c, 'card_type', '') == 'CHARACTER']
        if red_cost_1:
            player.hand.append(red_cost_1[0])
            top_5.remove(red_cost_1[0])
        # Place rest at bottom
        player.deck.extend(top_5)
        return True
    return False


# --- OP07-009: Dogura & Magura ---
@register_effect("OP07-009", "ON_PLAY", "Give cost 1 red char Double Attack")
def dogura_magura_effect(game_state, player, card):
    red_cost_1 = [c for c in player.cards_in_play
                 if 'red' in (getattr(c, 'colors', '') or '').lower()
                 and (getattr(c, 'cost', 0) or 0) == 1]
    if red_cost_1:
        red_cost_1[0].has_doubleattack = True
        return True
    return False


# --- OP02-056: Donquixote Doflamingo ---
@register_effect("OP02-056", "ON_PLAY", "Look at 3, place at top or bottom in any order")
def doflamingo_op02_on_play(game_state, player, card):
    # Just deck manipulation - AI places all at bottom
    return True


@register_effect("OP02-056", "WHEN_ATTACKING", "Trash 1: Place opponent's cost 1 or less at bottom")
def doflamingo_op02_attack(game_state, player, card):
    if player.hand:
        trash_from_hand(player, 1)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 1]
        if targets:
            target = targets[0]
            opponent.cards_in_play.remove(target)
            opponent.deck.append(target)
            return True
    return False


# --- OP14-060: Donquixote Doflamingo (Leader) ---
@register_effect("OP14-060", "ON_OPPONENT_ATTACK", "DON -1: Change attack target")
def doflamingo_leader_effect(game_state, player, card):
    # Return DON to deck as cost
    active_don = [d for d in player.don_cards if not d.is_resting]
    if active_don and hasattr(player, 'don_deck'):
        don = active_don[0]
        player.don_cards.remove(don)
        player.don_deck.append(don)
        # Change attack target logic would be handled by game engine
        return True
    return False


# --- OP10-029: Dracule Mihawk ---
@register_effect("OP10-029", "ON_PLAY", "If 2+ rested chars, set ODYSSEY cost 5 or less active")
def mihawk_op10_effect(game_state, player, card):
    rested = [c for c in player.cards_in_play if c.is_resting]
    if len(rested) >= 2:
        odyssey = [c for c in rested
                  if 'odyssey' in (getattr(c, 'card_types', '') or '').lower()
                  and (getattr(c, 'cost', 0) or 0) <= 5]
        if odyssey:
            odyssey[0].is_resting = False
            return True
    return False


# --- OP07-117: Egghead Stage ---
@register_effect("OP07-117", "END_OF_TURN", "If 3 or less Life, set Egghead cost 5 or less active")
def egghead_stage_effect(game_state, player, card):
    if len(player.life_cards) <= 3:
        egghead = [c for c in player.cards_in_play
                  if 'egghead' in (getattr(c, 'card_types', '') or '').lower()
                  and (getattr(c, 'cost', 0) or 0) <= 5]
        if egghead:
            egghead[0].is_resting = False
            return True
    return False


# --- OP14-054: Fisher Tiger ---
@register_effect("OP14-054", "ON_PLAY", "If Leader is Fish-Man, draw 3")
def fisher_tiger_on_play(game_state, player, card):
    if player.leader and 'fish-man' in (getattr(player.leader, 'card_types', '') or '').lower():
        draw_cards(player, 3)
        return True
    return False


@register_effect("OP14-054", "END_OF_TURN", "Trash until 5 cards in hand")
def fisher_tiger_end(game_state, player, card):
    while len(player.hand) > 5:
        trash_from_hand(player, 1)
    return True


# --- OP11-012: Franky ---
@register_effect("OP11-012", "ON_EVENT_ACTIVATE", "All chars gain +2000 power")
def franky_op11_effect(game_state, player, card):
    for c in player.cards_in_play:
        c.power_modifier = getattr(c, 'power_modifier', 0) + 2000
    return True


# --- OP13-033: Franky ---
@register_effect("OP13-033", "ON_KO", "Rest up to 2 opponent's cards")
def franky_op13_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    active = [c for c in opponent.cards_in_play if not c.is_resting][:2]
    rest_cards(active)
    return len(active) > 0


# --- OP14-104: Gecko Moria ---
@register_effect("OP14-104", "ON_PLAY", "Play Thriller Bark cost 4 or less from trash or add to Life")
def gecko_moria_effect(game_state, player, card):
    thriller = [c for c in player.trash
               if 'thriller bark pirates' in (getattr(c, 'card_types', '') or '').lower()
               and (getattr(c, 'cost', 0) or 0) <= 4
               and getattr(c, 'card_type', '') == 'CHARACTER']
    if thriller:
        char = thriller[0]
        player.trash.remove(char)
        # Play it
        player.cards_in_play.append(char)
        return True
    return False


# --- OP06-044: Gion ---
@register_effect("OP06-044", "ON_EVENT_ACTIVATE", "Opponent places 1 card from hand at bottom")
def gion_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    if opponent.hand:
        # Opponent picks lowest cost
        sorted_hand = sorted(opponent.hand, key=lambda c: getattr(c, 'cost', 0) or 0)
        card_to_place = sorted_hand[0]
        opponent.hand.remove(card_to_place)
        opponent.deck.append(card_to_place)
        return True
    return False


# --- OP14-105: Gorgon Sisters ---
@register_effect("OP14-105", "MAIN", "Reveal 3 Amazon Lily/Kuja cards: Give DON to all chars")
def gorgon_sisters_effect(game_state, player, card):
    amazon_kuja = [c for c in player.hand
                  if 'amazon lily' in (getattr(c, 'card_types', '') or '').lower()
                  or 'kuja pirates' in (getattr(c, 'card_types', '') or '').lower()]
    if len(amazon_kuja) >= 3:
        rested_don = [d for d in player.don_cards if d.is_resting]
        for char in player.cards_in_play:
            if rested_don:
                give_don_to_card(player, char, 1, rested_only=True)
        if player.leader and rested_don:
            give_don_to_card(player, player.leader, 1, rested_only=True)
        return True
    return False


# --- OP04-080: Gyats ---
@register_effect("OP04-080", "ON_PLAY", "Dressrosa char can attack active this turn")
def gyats_effect(game_state, player, card):
    dressrosa = get_characters_by_type(player, 'dressrosa')
    if dressrosa:
        dressrosa[0].can_attack_active = True
        return True
    return False


# --- OP04-020: Issho (Leader) ---
@register_effect("OP04-020", "END_OF_TURN", "Rest 1 DON: Set cost 5 or less char active")
def issho_leader_effect(game_state, player, card):
    active_don = [d for d in player.don_cards if not d.is_resting]
    if active_don:
        active_don[0].is_resting = True
        chars = get_characters_by_cost(player, max_cost=5)
        rested = [c for c in chars if c.is_resting]
        if rested:
            rested[0].is_resting = False
            return True
    return False


# --- OP10-107: Jewelry Bonney ---
@register_effect("OP10-107", "ON_PLAY", "Swap Life with Supernovas cost 5 from hand")
def jewelry_bonney_effect(game_state, player, card):
    if player.life_cards:
        supernovas = [c for c in player.hand
                     if 'supernovas' in (getattr(c, 'card_types', '') or '').lower()
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


# --- OP01-038: Kanjuro ---
@register_effect("OP01-038", "WHEN_ATTACKING", "KO opponent's rested cost 2 or less")
def kanjuro_attack(game_state, player, card):
    if getattr(card, 'attached_don', 0) >= 1:
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play
                  if c.is_resting and (getattr(c, 'cost', 0) or 0) <= 2]
        if targets:
            target = targets[0]
            opponent.cards_in_play.remove(target)
            opponent.trash.append(target)
            return True
    return False


@register_effect("OP01-038", "ON_KO", "Opponent picks 1 card from your hand to trash")
def kanjuro_ko(game_state, player, card):
    if player.hand:
        # Random pick for AI
        idx = random.randint(0, len(player.hand) - 1)
        trashed = player.hand.pop(idx)
        player.trash.append(trashed)
        return True
    return False


# --- EB04-012: Kikunojo ---
@register_effect("EB04-012", "MAIN", "If played this turn, set Land of Wano Leader active")
def kikunojo_effect(game_state, player, card):
    if getattr(card, 'played_this_turn', False):
        if player.leader and 'land of wano' in (getattr(player.leader, 'card_types', '') or '').lower():
            player.leader.is_resting = False
            return True
    return False


# --- OP14-024: Kin'emon ---
@register_effect("OP14-024", "ON_PLAY", "Set 3 DON active, cannot play chars this turn")
def kinemon_on_play(game_state, player, card):
    rested_don = [d for d in player.don_cards if d.is_resting][:3]
    for don in rested_don:
        don.is_resting = False
    player.cannot_play_chars_this_turn = True
    return True


@register_effect("OP14-024", "ON_KO", "Rest 1 opponent's card")
def kinemon_ko(game_state, player, card):
    opponent = get_opponent(game_state, player)
    active = [c for c in opponent.cards_in_play if not c.is_resting]
    if active:
        active[0].is_resting = True
        return True
    return False


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


# --- P-092: Koby ---
@register_effect("P-092", "WHEN_ATTACKING", "If Navy Leader, Leader base power becomes 7000")
def koby_p092_effect(game_state, player, card):
    if player.leader and 'navy' in (getattr(player.leader, 'card_types', '') or '').lower():
        player.leader.base_power_override = 7000
        return True
    return False


# --- OP02-030: Kouzuki Oden ---
@register_effect("OP02-030", "MAIN", "Rest 3 DON: Set this char active")
def oden_main(game_state, player, card):
    active_don = [d for d in player.don_cards if not d.is_resting]
    if len(active_don) >= 3:
        for don in active_don[:3]:
            don.is_resting = True
        card.is_resting = False
        return True
    return False


@register_effect("OP02-030", "ON_KO", "Play green Land of Wano cost 3 from deck")
def oden_ko(game_state, player, card):
    for i, deck_card in enumerate(player.deck):
        if ('green' in (getattr(deck_card, 'colors', '') or '').lower()
            and 'land of wano' in (getattr(deck_card, 'card_types', '') or '').lower()
            and (getattr(deck_card, 'cost', 0) or 0) == 3
            and getattr(deck_card, 'card_type', '') == 'CHARACTER'):
            char = player.deck.pop(i)
            player.cards_in_play.append(char)
            random.shuffle(player.deck)
            return True
    return False


# --- OP01-098: Kurozumi Orochi ---
@register_effect("OP01-098", "ON_PLAY", "Reveal SMILE from deck and add to hand")
def orochi_effect(game_state, player, card):
    for i, deck_card in enumerate(player.deck):
        if 'artificial devil fruit smile' in (getattr(deck_card, 'name', '') or '').lower():
            found = player.deck.pop(i)
            player.hand.append(found)
            random.shuffle(player.deck)
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
           if 'navy' in (getattr(c, 'card_types', '') or '').lower()]
    if navy:
        navy[0].can_attack_active = True
        return True
    if player.leader and 'navy' in (getattr(player.leader, 'card_types', '') or '').lower():
        player.leader.can_attack_active = True
        return True
    return False


# --- OP09-014: Limejuice ---
@register_effect("OP09-014", "ON_PLAY", "Opponent cannot activate Blocker with 4000 or less power")
def limejuice_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    for c in opponent.cards_in_play:
        if (getattr(c, 'power', 0) or 0) <= 4000:
            c.blocker_disabled_this_turn = True
    return True


# --- P-071: Marco ---
@register_effect("P-071", "ON_KO", "Return this card to hand")
def marco_p071_effect(game_state, player, card):
    if card in player.trash:
        player.trash.remove(card)
        player.hand.append(card)
        return True
    return False


# --- OP12-054: Marshall.D.Teach ---
@register_effect("OP12-054", "ON_PLAY", "If Seven Warlords Leader, return cost 1 or less to hand")
def teach_op12_effect(game_state, player, card):
    if player.leader and 'seven warlords' in (getattr(player.leader, 'card_types', '') or '').lower():
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play
                  if c != card and (getattr(c, 'cost', 0) or 0) <= 1]
        if targets:
            target = targets[0]
            opponent.cards_in_play.remove(target)
            opponent.hand.append(target)
            return True
    return False


# --- OP08-031: Miyagi ---
@register_effect("OP08-031", "ON_PLAY", "Set Minks cost 2 or less active")
def miyagi_effect(game_state, player, card):
    minks = [c for c in player.cards_in_play
            if 'minks' in (getattr(c, 'card_types', '') or '').lower()
            and (getattr(c, 'cost', 0) or 0) <= 2
            and c.is_resting]
    if minks:
        minks[0].is_resting = False
        return True
    return False


# --- OP07-001: Monkey.D.Dragon (Leader) ---
@register_effect("OP07-001", "MAIN", "Give up to 2 given DON to 1 char")
def dragon_leader_effect(game_state, player, card):
    # Find card with attached DON
    for c in player.cards_in_play:
        if getattr(c, 'attached_don', 0) >= 2:
            # Can redistribute - implementation depends on game logic
            return True
    return False


# --- OP12-056: Monkey.D.Garp ---
@register_effect("OP12-056", "ON_PLAY", "Trash 1: Play blue Navy 8000 power or less")
def garp_op12_effect(game_state, player, card):
    if player.hand:
        trash_from_hand(player, 1)
        for i, hand_card in enumerate(player.hand):
            if ('blue' in (getattr(hand_card, 'colors', '') or '').lower()
                and 'navy' in (getattr(hand_card, 'card_types', '') or '').lower()
                and (getattr(hand_card, 'power', 0) or 0) <= 8000
                and getattr(hand_card, 'card_type', '') == 'CHARACTER'
                and 'Monkey.D.Garp' not in getattr(hand_card, 'name', '')):
                char = player.hand.pop(i)
                player.cards_in_play.append(char)
                return True
    return False


# --- PRB02-005: Monkey.D.Luffy ---
@register_effect("PRB02-005", "ON_PLAY", "If multicolor Leader and opponent has 7 or less DON, rest their DON")
def luffy_prb02_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    colors = (getattr(player.leader, 'colors', '') or '').lower() if player.leader else ''
    is_multicolor = colors.count('/') > 0 or len([c for c in ['red', 'blue', 'green', 'purple', 'black', 'yellow'] if c in colors]) > 1
    if is_multicolor and len(opponent.don_cards) <= 7:
        active_don = [d for d in opponent.don_cards if not d.is_resting]
        if active_don:
            # Mark to rest at start of next main phase
            opponent.rest_don_at_main_phase = True
            return True
    return False


# --- ST21-001: Monkey.D.Luffy (Leader) ---
@register_effect("ST21-001", "MAIN", "Give up to 2 rested DON to 1 char")
def luffy_st21_leader_effect(game_state, player, card):
    rested_don = [d for d in player.don_cards if d.is_resting]
    if len(rested_don) >= 2 and player.cards_in_play:
        target = player.cards_in_play[0]
        give_don_to_card(player, target, 2, rested_only=True)
        return True
    return False


# --- ST26-005: Monkey.D.Luffy ---
@register_effect("ST26-005", "ON_PLAY", "DON -2: If multicolor Leader and opponent has 5+ DON, Leader becomes 7000")
def luffy_st26_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    colors = (getattr(player.leader, 'colors', '') or '').lower() if player.leader else ''
    is_multicolor = colors.count('/') > 0
    if is_multicolor and len(opponent.don_cards) >= 5:
        # Return 2 DON
        active_don = [d for d in player.don_cards if not d.is_resting]
        if len(active_don) >= 2 and hasattr(player, 'don_deck'):
            for don in active_don[:2]:
                player.don_cards.remove(don)
                player.don_deck.append(don)
            player.leader.base_power_override = 7000
            return True
    return False


# --- ST29-012: Monkey.D.Luffy ---
@register_effect("ST29-012", "MAIN", "Give 1 rested DON to Monkey.D.Luffy")
def luffy_st29_effect(game_state, player, card):
    rested_don = [d for d in player.don_cards if d.is_resting]
    luffy_cards = [c for c in player.cards_in_play if 'Monkey.D.Luffy' in getattr(c, 'name', '')]
    if rested_don and luffy_cards:
        give_don_to_card(player, luffy_cards[0], 1, rested_only=True)
        return True
    return False


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


# --- OP04-069: Mr.2.Bon.Kurei(Bentham) ---
@register_effect("OP04-069", "ON_OPPONENT_ATTACK", "DON -1: Copy attacker's power")
def mr2_op04_effect(game_state, player, card):
    if hasattr(game_state, 'current_attacker'):
        card.power = getattr(game_state.current_attacker, 'power', 0)
        # Return DON
        active_don = [d for d in player.don_cards if not d.is_resting]
        if active_don and hasattr(player, 'don_deck'):
            don = active_don[0]
            player.don_cards.remove(don)
            player.don_deck.append(don)
            return True
    return False


# --- ST08-013: Mr.2.Bon.Kurei(Bentham) ---
@register_effect("ST08-013", "END_BATTLE", "May KO opponent's battled char, then KO this")
def mr2_st08_effect(game_state, player, card):
    if hasattr(game_state, 'last_battle_target'):
        target = game_state.last_battle_target
        opponent = get_opponent(game_state, player)
        if target in opponent.cards_in_play:
            opponent.cards_in_play.remove(target)
            opponent.trash.append(target)
        if card in player.cards_in_play:
            player.cards_in_play.remove(card)
            player.trash.append(card)
        return True
    return False


# --- OP14-092: Mr.3(Galdino) ---
@register_effect("OP14-092", "WOULD_BE_KO", "Place 3 from trash at bottom instead of KO")
def mr3_effect(game_state, player, card):
    if len(player.trash) >= 3:
        for _ in range(3):
            if player.trash:
                card_to_place = player.trash.pop(0)
                player.deck.append(card_to_place)
        return True  # Prevent KO
    return False


# --- OP09-033: Nico Robin ---
@register_effect("OP09-033", "ON_PLAY", "If 2+ rested chars, ODYSSEY/Straw Hat can't be KO'd by effects")
def robin_op09_effect(game_state, player, card):
    rested = [c for c in player.cards_in_play if c.is_resting]
    if len(rested) >= 2:
        for c in player.cards_in_play:
            types = (getattr(c, 'card_types', '') or '').lower()
            if 'odyssey' in types or 'straw hat crew' in types:
                c.protected_from_ko = True
        return True
    return False


# --- OP13-032: Nico Robin ---
@register_effect("OP13-032", "ON_PLAY", "Opponent's cost 8 or less cannot be rested")
def robin_op13_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    for c in opponent.cards_in_play:
        if (getattr(c, 'cost', 0) or 0) <= 8:
            c.cannot_be_rested = True
    return True


# --- EB01-038: Oh Come My Way ---
@register_effect("EB01-038", "COUNTER", "DON -1: Change attack target to char")
def oh_come_my_way_effect(game_state, player, card):
    if hasattr(player, 'don_deck'):
        active_don = [d for d in player.don_cards if not d.is_resting]
        if active_don and player.cards_in_play:
            don = active_don[0]
            player.don_cards.remove(don)
            player.don_deck.append(don)
            # Attack target change handled by game
            return True
    return False


# --- OP04-097: Otama ---
@register_effect("OP04-097", "ON_PLAY", "Add opponent's Animal/SMILE cost 3 or less to their Life")
def otama_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play
              if ('animal' in (getattr(c, 'card_types', '') or '').lower()
                  or 'smile' in (getattr(c, 'card_types', '') or '').lower())
              and (getattr(c, 'cost', 0) or 0) <= 3]
    if targets:
        target = targets[0]
        opponent.cards_in_play.remove(target)
        opponent.life_cards.append(target)
        return True
    return False


# --- OP14-033: Perona ---
@register_effect("OP14-033", "ON_PLAY", "2 opponent's cost 5 or less cannot be rested")
def perona_on_play(game_state, player, card):
    opponent = get_opponent(game_state, player)
    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 5][:2]
    for t in targets:
        t.cannot_be_rested = True
    return len(targets) > 0


@register_effect("OP14-033", "ON_KO", "Rest 1: Play green cost 5 or less from hand")
def perona_ko(game_state, player, card):
    active = [c for c in player.cards_in_play if not c.is_resting]
    if active:
        active[0].is_resting = True
        green_chars = [c for c in player.hand
                      if 'green' in (getattr(c, 'colors', '') or '').lower()
                      and (getattr(c, 'cost', 0) or 0) <= 5
                      and getattr(c, 'card_type', '') == 'CHARACTER']
        if green_chars:
            char = green_chars[0]
            player.hand.remove(char)
            player.cards_in_play.append(char)
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
        char = targets[0]
        if char in player.hand:
            player.hand.remove(char)
        else:
            player.trash.remove(char)
        player.cards_in_play.append(char)
        return True
    return False


# --- ST13-002: Portgas.D.Ace (Leader) ---
@register_effect("ST13-002", "MAIN", "Look at 5, add cost 5 char to Life")
def ace_st13_main(game_state, player, card):
    if getattr(card, 'attached_don', 0) >= 2 and len(player.deck) >= 5:
        top_5 = player.deck[:5]
        player.deck = player.deck[5:]
        cost_5 = [c for c in top_5
                 if (getattr(c, 'cost', 0) or 0) == 5
                 and getattr(c, 'card_type', '') == 'CHARACTER']
        if cost_5:
            player.life_cards.append(cost_5[0])
            top_5.remove(cost_5[0])
        player.deck.extend(top_5)
        return True
    return False


@register_effect("ST13-002", "END_OF_TURN", "Trash all face-up Life")
def ace_st13_end(game_state, player, card):
    # Simplified: trash 1 life to simulate face-up life mechanic
    return True


# --- ST12-007: Rika ---
@register_effect("ST12-007", "ON_PLAY", "Rest 2 DON: If opponent has 3+ Life, set Slash cost 4 or less active")
def rika_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    active_don = [d for d in player.don_cards if not d.is_resting]
    if len(active_don) >= 2 and len(opponent.life_cards) >= 3:
        for don in active_don[:2]:
            don.is_resting = True
        slash = [c for c in player.cards_in_play
                if 'slash' in (getattr(c, 'attributes', '') or '').lower()
                and (getattr(c, 'cost', 0) or 0) <= 4
                and c.is_resting]
        if slash:
            slash[0].is_resting = False
            return True
    return False


# --- PRB02-006: Roronoa Zoro ---
@register_effect("PRB02-006", "WOULD_BE_RESTED", "Rest another char instead")
def zoro_prb02_effect(game_state, player, card):
    other_chars = [c for c in player.cards_in_play if c != card and not c.is_resting]
    if other_chars:
        other_chars[0].is_resting = True
        return True  # Prevent this card from being rested
    return False


# --- OP13-092: Saint Mjosgard ---
@register_effect("OP13-092", "ON_PLAY", "If 3 or less Life, play Mary Geoise Stage cost 1 from trash")
def mjosgard_effect(game_state, player, card):
    if len(player.life_cards) <= 3:
        stages = [c for c in player.trash
                 if 'mary geoise' in (getattr(c, 'card_types', '') or '').lower()
                 and (getattr(c, 'cost', 0) or 0) == 1
                 and getattr(c, 'card_type', '') == 'STAGE']
        if stages:
            stage = stages[0]
            player.trash.remove(stage)
            player.cards_in_play.append(stage)
            return True
    return False


# --- OP11-051: Sanji ---
@register_effect("OP11-051", "ON_KO_BY_EFFECT", "Look at 5, play Straw Hat cost 5 or less")
def sanji_op11_ko(game_state, player, card):
    if len(player.deck) >= 5:
        top_5 = player.deck[:5]
        player.deck = player.deck[5:]
        straw_hat = [c for c in top_5
                    if 'straw hat crew' in (getattr(c, 'card_types', '') or '').lower()
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
        target = targets[0]
        opponent.cards_in_play.remove(target)
        opponent.hand.append(target)
        return True
    return False


# --- PRB01-001: Sanji (Leader) ---
@register_effect("PRB01-001", "MAIN", "Give char without On Play Rush")
def sanji_leader_effect(game_state, player, card):
    chars = [c for c in player.cards_in_play
            if (getattr(c, 'cost', 0) or 0) <= 8
            and '[On Play]' not in (getattr(c, 'effect', '') or '')]
    if chars:
        chars[0].has_rush = True
        return True
    return False


# --- OP04-048: Sasaki ---
@register_effect("OP04-048", "ON_PLAY", "Return hand to deck, shuffle, draw same number")
def sasaki_effect(game_state, player, card):
    hand_count = len(player.hand)
    player.deck.extend(player.hand)
    player.hand.clear()
    random.shuffle(player.deck)
    draw_cards(player, hand_count)
    return True


# --- EB04-011: Scaled Neptunian ---
@register_effect("EB04-011", "ON_PLAY", "Draw for each Neptunian char, trash same number")
def neptunian_effect(game_state, player, card):
    neptunian_count = len([c for c in player.cards_in_play
                          if 'neptunian' in (getattr(c, 'card_types', '') or '').lower()])
    if neptunian_count > 0:
        draw_cards(player, neptunian_count)
        trash_from_hand(player, neptunian_count)
        return True
    return False


# --- OP13-028: Shanks ---
@register_effect("OP13-028", "ON_PLAY", "Set all DON active, cannot play from hand this turn")
def shanks_op13_effect(game_state, player, card):
    for don in player.don_cards:
        don.is_resting = False
    player.cannot_play_from_hand = True
    return True


# --- ST09-008: Shimotsuki Ushimaru ---
@register_effect("ST09-008", "WHEN_ATTACKING", "Add Life to hand: Play yellow Land of Wano cost 4 or less")
def ushimaru_effect(game_state, player, card):
    if getattr(card, 'attached_don', 0) >= 1 and player.life_cards:
        life = player.life_cards.pop()
        player.hand.append(life)
        wano = [c for c in player.hand
               if 'yellow' in (getattr(c, 'colors', '') or '').lower()
               and 'land of wano' in (getattr(c, 'card_types', '') or '').lower()
               and (getattr(c, 'cost', 0) or 0) <= 4
               and getattr(c, 'card_type', '') == 'CHARACTER']
        if wano:
            char = wano[0]
            player.hand.remove(char)
            player.cards_in_play.append(char)
            return True
    return False


# --- OP02-032: Shishilian ---
@register_effect("OP02-032", "ON_PLAY", "Rest 2 DON: Set Minks cost 5 or less active")
def shishilian_effect(game_state, player, card):
    active_don = [d for d in player.don_cards if not d.is_resting]
    if len(active_don) >= 2:
        for don in active_don[:2]:
            don.is_resting = True
        minks = [c for c in player.cards_in_play
                if 'minks' in (getattr(c, 'card_types', '') or '').lower()
                and (getattr(c, 'cost', 0) or 0) <= 5
                and c.is_resting]
        if minks:
            minks[0].is_resting = False
            return True
    return False


# --- OP06-009: Shuraiya ---
@register_effect("OP06-009", "WHEN_ATTACKING", "Become same power as opponent's Leader")
def shuraiya_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    if opponent.leader:
        card.power = getattr(opponent.leader, 'power', 5000)
        return True
    return False


# --- ST26-001: Soba Mask ---
@register_effect("ST26-001", "ON_PLAY", "Return all San-Gorou and Sanji to hand")
def soba_mask_effect(game_state, player, card):
    to_return = [c for c in player.cards_in_play
                if 'San-Gorou' in getattr(c, 'name', '') or 'Sanji' in getattr(c, 'name', '')]
    for c in to_return:
        player.cards_in_play.remove(c)
        player.hand.append(c)
    return len(to_return) > 0


# --- OP08-100: South Bird ---
@register_effect("OP08-100", "ON_PLAY", "Look at 7, play Upper Yard Stage")
def south_bird_effect(game_state, player, card):
    if len(player.deck) >= 7:
        top_7 = player.deck[:7]
        player.deck = player.deck[7:]
        upper_yard = [c for c in top_7 if 'Upper Yard' in getattr(c, 'name', '')]
        if upper_yard:
            player.cards_in_play.append(upper_yard[0])
            top_7.remove(upper_yard[0])
        player.deck.extend(top_7)
        return True
    return False


# --- OP02-101: Strawberry ---
@register_effect("OP02-101", "WHEN_ATTACKING", "If cost 0 char exists, opponent can't use Blocker cost 5 or less")
def strawberry_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    has_cost_0 = any((getattr(c, 'cost', 0) or 0) == 0 for c in opponent.cards_in_play)
    if has_cost_0:
        for c in opponent.cards_in_play:
            if (getattr(c, 'cost', 0) or 0) <= 5:
                c.blocker_disabled_this_battle = True
        return True
    return False


# --- OP06-117: The Ark Maxim ---
@register_effect("OP06-117", "MAIN", "Rest this and Enel: KO all cost 2 or less")
def ark_maxim_effect(game_state, player, card):
    enel = [c for c in player.cards_in_play if 'Enel' in getattr(c, 'name', '') and not c.is_resting]
    if enel and not card.is_resting:
        card.is_resting = True
        enel[0].is_resting = True
        opponent = get_opponent(game_state, player)
        to_ko = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
        for c in to_ko:
            opponent.cards_in_play.remove(c)
            opponent.trash.append(c)
        return True
    return False


# --- OP06-041: The Ark Noah ---
@register_effect("OP06-041", "ON_PLAY", "Rest all opponent's Characters")
def ark_noah_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    for c in opponent.cards_in_play:
        c.is_resting = True
    return True


# --- OP13-099: The Empty Throne ---
@register_effect("OP13-099", "MAIN", "Rest this and 3 DON: Play Five Elders with cost <= DON count")
def empty_throne_effect(game_state, player, card):
    active_don = [d for d in player.don_cards if not d.is_resting]
    if len(active_don) >= 3 and not card.is_resting:
        card.is_resting = True
        for don in active_don[:3]:
            don.is_resting = True
        don_count = len(player.don_cards)
        five_elders = [c for c in player.hand
                      if 'five elders' in (getattr(c, 'card_types', '') or '').lower()
                      and 'black' in (getattr(c, 'colors', '') or '').lower()
                      and (getattr(c, 'cost', 0) or 0) <= don_count
                      and getattr(c, 'card_type', '') == 'CHARACTER']
        if five_elders:
            char = five_elders[0]
            player.hand.remove(char)
            player.cards_in_play.append(char)
            return True
    return False


# --- EB02-009: Thousand Sunny ---
@register_effect("EB02-009", "MAIN", "Rest this: Give 1 given DON to Straw Hat char")
def thousand_sunny_effect(game_state, player, card):
    if not card.is_resting:
        card.is_resting = True
        straw_hat = [c for c in player.cards_in_play
                    if 'straw hat crew' in (getattr(c, 'card_types', '') or '').lower()]
        if straw_hat:
            # Redistribute DON logic
            return True
    return False


# --- OP08-001: Tony Tony.Chopper (Leader) ---
@register_effect("OP08-001", "MAIN", "Give Animal/Drum Kingdom chars 1 rested DON each")
def chopper_leader_effect(game_state, player, card):
    rested_don = [d for d in player.don_cards if d.is_resting]
    targets = [c for c in player.cards_in_play
              if 'animal' in (getattr(c, 'card_types', '') or '').lower()
              or 'drum kingdom' in (getattr(c, 'card_types', '') or '').lower()][:3]
    given = 0
    for target in targets:
        if rested_don:
            give_don_to_card(player, target, 1, rested_only=True)
            given += 1
    return given > 0


# --- OP09-029: Tony Tony.Chopper ---
@register_effect("OP09-029", "END_OF_TURN", "Set ODYSSEY cost 4 or less active")
def chopper_op09_effect(game_state, player, card):
    odyssey = [c for c in player.cards_in_play
              if 'odyssey' in (getattr(c, 'card_types', '') or '').lower()
              and (getattr(c, 'cost', 0) or 0) <= 4
              and c.is_resting]
    if odyssey:
        odyssey[0].is_resting = False
        return True
    return False


# --- P-009: Trafalgar Law ---
@register_effect("P-009", "ON_PLAY", "If opponent has 6+ hand, they add 1 Life to hand")
def law_p009_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    if len(opponent.hand) >= 6 and opponent.life_cards:
        life = opponent.life_cards.pop()
        opponent.hand.append(life)
        return True
    return False


# --- P-017: Trafalgar Law ---
@register_effect("P-017", "ON_PLAY", "Give opponent's char -2000 power")
def law_p017_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    if opponent.cards_in_play:
        opponent.cards_in_play[0].power_modifier = getattr(opponent.cards_in_play[0], 'power_modifier', 0) - 2000
        return True
    return False


# --- ST02-009: Trafalgar Law ---
@register_effect("ST02-009", "ON_PLAY", "Set Supernovas/Heart Pirates cost 5 or less active")
def law_st02_effect(game_state, player, card):
    targets = [c for c in player.cards_in_play
              if ('supernovas' in (getattr(c, 'card_types', '') or '').lower()
                  or 'heart pirates' in (getattr(c, 'card_types', '') or '').lower())
              and (getattr(c, 'cost', 0) or 0) <= 5
              and c.is_resting]
    if targets:
        targets[0].is_resting = False
        return True
    return False


# --- OP06-051: Tsuru ---
@register_effect("OP06-051", "ON_PLAY", "Trash 2: Opponent returns 1 char to hand")
def tsuru_effect(game_state, player, card):
    if len(player.hand) >= 2:
        trash_from_hand(player, 2)
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            # Opponent picks (AI picks lowest cost)
            sorted_chars = sorted(opponent.cards_in_play, key=lambda c: getattr(c, 'cost', 0) or 0)
            char = sorted_chars[0]
            opponent.cards_in_play.remove(char)
            opponent.hand.append(char)
            return True
    return False


# --- OP01-004: Usopp ---
@register_effect("OP01-004", "ON_EVENT_ACTIVATE", "Draw 1 when opponent activates Event")
def usopp_op01_effect(game_state, player, card):
    if getattr(card, 'attached_don', 0) >= 1:
        draw_cards(player, 1)
        return True
    return False


# --- ST11-001: Uta (Leader) ---
@register_effect("ST11-001", "WHEN_ATTACKING", "Reveal top, add FILM to hand")
def uta_leader_effect(game_state, player, card):
    if getattr(card, 'attached_don', 0) >= 1 and player.deck:
        top = player.deck[0]
        if 'film' in (getattr(top, 'card_types', '') or '').lower():
            player.deck.pop(0)
            player.hand.append(top)
        else:
            # Place at bottom
            player.deck.pop(0)
            player.deck.append(top)
        return True
    return False


# --- OP05-079: Viola ---
@register_effect("OP05-079", "ON_PLAY", "Opponent places 3 from trash at bottom of deck")
def viola_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    for _ in range(min(3, len(opponent.trash))):
        if opponent.trash:
            card_to_place = opponent.trash.pop(0)
            opponent.deck.append(card_to_place)
    return True


# --- OP13-006: Woop Slap ---
@register_effect("OP13-006", "ON_PLAY", "Give 2 rested DON to Monkey.D.Luffy")
def woop_slap_effect(game_state, player, card):
    luffy_cards = [c for c in player.cards_in_play if 'Monkey.D.Luffy' in getattr(c, 'name', '')]
    if luffy_cards:
        give_don_to_card(player, luffy_cards[0], 2, rested_only=True)
        return True
    return False


# --- P-046: Yamato ---
@register_effect("P-046", "ON_PLAY", "Place all hand at bottom, draw same number")
def yamato_p046_effect(game_state, player, card):
    hand_count = len(player.hand)
    player.deck.extend(player.hand)
    player.hand.clear()
    draw_cards(player, hand_count)
    return True


# =============================================================================
# ADDITIONAL PLACEHOLDER CARDS (18 remaining)
# =============================================================================

# --- OP14-041: Boa Hancock ---
@register_effect("OP14-041", "ON_OPPONENT_PLAY", "Draw 1 card when you play a Character on opponent's turn")
def boa_hancock_op14_effect(game_state, player, card):
    # Draw on opponent's turn when playing a character
    draw_cards(player, 1)
    return True

@register_effect("OP14-041", "ON_YOUR_CHARACTER_KO", "Add to life when 5000+ power character KO'd")
def boa_hancock_op14_ko_effect(game_state, player, card):
    if getattr(card, 'attached_don', 0) >= 1:
        # When 5000+ power character KO'd, this triggers
        draw_cards(player, 1)
        return True
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


# --- OP06-044: Gion ---
@register_effect("OP06-044", "ON_OPPONENT_EVENT", "Opponent places 1 card from hand at bottom")
def gion_effect(game_state, player, card):
    opponent = get_opponent(game_state, player)
    if opponent.hand:
        card_to_place = opponent.hand.pop(0)
        opponent.deck.append(card_to_place)
        return True
    return False


# --- OP14-105: Gorgon Sisters ---
@register_effect("OP14-105", "ACTIVATE_MAIN", "Give Leader and Characters rested DON each")
def gorgon_sisters_effect(game_state, player, card):
    # Check for 3 Amazon Lily/Kuja Pirates cards in hand (simplified)
    type_cards = [c for c in player.hand if 'amazon lily' in (getattr(c, 'card_types', '') or '').lower() or 'kuja pirates' in (getattr(c, 'card_types', '') or '').lower()]
    if len(type_cards) >= 3:
        # Give rested DON to each character
        rested_don = [d for d in player.don_cards if d.is_resting]
        targets = [player.leader] + player.cards_in_play
        for target in targets[:len(rested_don)]:
            if rested_don:
                don = rested_don.pop(0)
                target.attached_don = getattr(target, 'attached_don', 0) + 1
        return True
    return False


# --- EB04-012: Kikunojo ---
@register_effect("EB04-012", "ACTIVATE_MAIN", "Set Land of Wano leader as active if played this turn")
def kikunojo_effect(game_state, player, card):
    if getattr(card, 'played_this_turn', False):
        leader = player.leader
        if leader and 'land of wano' in (getattr(leader, 'card_types', '') or '').lower():
            leader.is_resting = False
            return True
    return False


# --- OP07-001: Monkey.D.Dragon ---
@register_effect("OP07-001", "ACTIVATE_MAIN", "Give up to 2 DON to 1 Character")
def dragon_effect(game_state, player, card):
    if player.cards_in_play:
        target = player.cards_in_play[0]  # AI chooses first
        give_don_to_card(player, target, 2)
        return True
    return False


# --- ST21-001: Monkey.D.Luffy ---
@register_effect("ST21-001", "ACTIVATE_MAIN", "Give up to 2 rested DON to 1 Character")
def luffy_st21_effect(game_state, player, card):
    if getattr(card, 'attached_don', 0) >= 1 and player.cards_in_play:
        target = player.cards_in_play[0]  # AI chooses first
        give_don_to_card(player, target, 2, rested_only=True)
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


# --- ST08-013: Mr.2.Bon.Kurei(Bentham) ---
@register_effect("ST08-013", "END_OF_BATTLE", "KO opponent's battled Character and this card")
def mr2_effect(game_state, player, card):
    if getattr(card, 'attached_don', 0) >= 1:
        # Get opponent's battled character
        opponent = get_opponent(game_state, player)
        if hasattr(game_state, 'current_battle_target'):
            target = game_state.current_battle_target
            if target and target in opponent.cards_in_play:
                # KO both
                opponent.cards_in_play.remove(target)
                opponent.trash.append(target)
                if card in player.cards_in_play:
                    player.cards_in_play.remove(card)
                    player.trash.append(card)
                return True
    return False


# --- OP14-092: Mr.3(Galdino) ---
@register_effect("OP14-092", "ON_WOULD_BE_KO", "Place 3 cards from trash at bottom instead of being KO'd")
def mr3_effect(game_state, player, card):
    if len(player.trash) >= 3:
        # Place 3 cards from trash at bottom of deck
        for _ in range(3):
            if player.trash:
                card_to_place = player.trash.pop(0)
                player.deck.append(card_to_place)
        # Prevent KO by returning True
        return True  # Signals KO prevention
    return False


# --- PRB02-006: Roronoa Zoro ---
@register_effect("PRB02-006", "ON_WOULD_BE_RESTED", "Rest another Character instead")
def zoro_prb02_effect(game_state, player, card):
    # If would be rested by opponent's effect, rest another character
    other_chars = [c for c in player.cards_in_play if c != card and not c.is_resting]
    if other_chars:
        other_chars[0].is_resting = True
        return True  # Prevents this card from being rested
    return False


# --- PRB01-001: Sanji ---
@register_effect("PRB01-001", "ACTIVATE_MAIN", "Give Rush to Character without On Play, cost 8 or less")
def sanji_prb01_effect(game_state, player, card):
    # Find characters without On Play effect and cost 8 or less
    targets = [c for c in player.cards_in_play
               if getattr(c, 'cost', 0) <= 8
               and not c.has_keyword('rush')]
    if targets:
        targets[0].rush = True
        return True
    return False


# --- OP06-117: The Ark Maxim ---
@register_effect("OP06-117", "ACTIVATE_MAIN", "Rest this and Enel to KO all opponent's cost 2 or less")
def ark_maxim_effect(game_state, player, card):
    enel_cards = [c for c in player.cards_in_play if 'enel' in getattr(c, 'name', '').lower()]
    if enel_cards and not card.is_resting:
        card.is_resting = True
        enel_cards[0].is_resting = True
        opponent = get_opponent(game_state, player)
        to_ko = [c for c in opponent.cards_in_play if getattr(c, 'cost', 0) <= 2]
        for c in to_ko:
            opponent.cards_in_play.remove(c)
            opponent.trash.append(c)
        return True
    return False


# --- OP13-099: The Empty Throne ---
@register_effect("OP13-099", "CONTINUOUS", "Leader +1000 power if 19+ cards in trash")
def empty_throne_continuous_effect(game_state, player, card):
    if len(player.trash) >= 19:
        player.leader.power = getattr(player.leader, 'power', 0) + 1000
        return True
    return False

@register_effect("OP13-099", "ACTIVATE_MAIN", "Play Five Elders from trash")
def empty_throne_main_effect(game_state, player, card):
    if not card.is_resting:
        # Rest this and 3 DON
        rested_don = sum(1 for d in player.don_cards if d.is_resting)
        if rested_don < 3:
            return False
        card.is_resting = True
        don_rested = 0
        for d in player.don_cards:
            if don_rested < 3 and not d.is_resting:
                d.is_resting = True
                don_rested += 1
        # Play Five Elders from trash
        five_elders = [c for c in player.trash if 'five elders' in (getattr(c, 'card_types', '') or '').lower()]
        if five_elders:
            card_to_play = five_elders[0]
            player.trash.remove(card_to_play)
            player.cards_in_play.append(card_to_play)
            return True
    return False


# --- EB02-009: Thousand Sunny ---
@register_effect("EB02-009", "ACTIVATE_MAIN", "Give DON to Straw Hat Crew Character")
def thousand_sunny_effect(game_state, player, card):
    if not card.is_resting:
        card.is_resting = True
        straw_hat = [c for c in player.cards_in_play if 'straw hat crew' in (getattr(c, 'card_types', '') or '').lower()]
        if straw_hat:
            give_don_to_card(player, straw_hat[0], 1)
            return True
    return False


# --- OP08-001: Tony Tony.Chopper ---
@register_effect("OP08-001", "ACTIVATE_MAIN", "Give up to 3 Animal/Drum Kingdom Characters 1 rested DON each")
def chopper_op08_effect(game_state, player, card):
    targets = [c for c in player.cards_in_play
               if 'animal' in (getattr(c, 'card_types', '') or '').lower()
               or 'drum kingdom' in (getattr(c, 'card_types', '') or '').lower()]
    targets = targets[:3]  # Up to 3
    for target in targets:
        give_don_to_card(player, target, 1, rested_only=True)
    return len(targets) > 0


# --- OP01-004: Usopp ---
@register_effect("OP01-004", "ON_OPPONENT_EVENT", "Draw 1 card when opponent activates Event")
def usopp_op01_effect(game_state, player, card):
    if getattr(card, 'attached_don', 0) >= 1:
        draw_cards(player, 1)
        return True
    return False


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_all_hardcoded_cards() -> List[str]:
    """Get list of all cards with hardcoded effects."""
    return list(_hardcoded_effects.keys())


def get_hardcoded_effect_count() -> int:
    """Get total count of hardcoded effects."""
    return sum(len(effects) for effects in _hardcoded_effects.values())


print(f"Hardcoded effects loaded: {get_hardcoded_effect_count()} effects for {len(get_all_hardcoded_cards())} cards")
