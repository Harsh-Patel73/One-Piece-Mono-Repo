"""
Hardcoded Effect Handlers for Complex Cards.

This module provides direct implementations for cards with effects too complex
for pattern-based parsing. Each card is implemented with its exact game logic.
"""

from typing import TYPE_CHECKING, Callable, Dict, Optional, List, Any, Tuple
from dataclasses import dataclass
import random
import uuid

if TYPE_CHECKING:
    from game_engine import GameState, Player, PendingChoice
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
    timing_lower = timing.lower() if timing else None
    if card_id in _hardcoded_effects:
        if timing_lower is None:
            return True
        return any(e.timing.lower() == timing_lower for e in _hardcoded_effects[card_id])
    if base_id in _hardcoded_effects:
        if timing_lower is None:
            return True
        return any(e.timing.lower() == timing_lower for e in _hardcoded_effects[base_id])
    return False


def execute_hardcoded_effect(game_state: 'GameState', player: 'Player', card: 'Card', timing: str) -> bool:
    """Execute hardcoded effects for a card at a specific timing."""
    card_id = card.id
    base_id = card_id.split('_')[0] if '_p' in card_id or '_r' in card_id else card_id

    # Avoid duplicate effects when card_id == base_id
    if card_id == base_id:
        effects = _hardcoded_effects.get(card_id, [])
    else:
        effects = _hardcoded_effects.get(card_id, []) + _hardcoded_effects.get(base_id, [])

    executed = False
    timing_lower = timing.lower()  # Case-insensitive comparison
    for effect in effects:
        if effect.timing.lower() == timing_lower:
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


def add_power_modifier(card, amount: int):
    """Add (or subtract) power to a card's temporary power modifier."""
    card.power_modifier = getattr(card, 'power_modifier', 0) + amount


def check_leader_type(player, type_str: str) -> bool:
    """Check if the player's leader has the given type/origin string."""
    return player.leader is not None and type_str in (getattr(player.leader, 'card_origin', '') or '')


def check_life_count(player, count: int, op: str = 'le') -> bool:
    """Check player's life card count against a threshold."""
    life = len(player.life_cards)
    if op == 'le': return life <= count
    if op == 'lt': return life < count
    if op == 'ge': return life >= count
    if op == 'eq': return life == count
    return life <= count


def draw_cards(player: 'Player', count: int) -> List['Card']:
    """Draw cards from deck."""
    import traceback
    print(f"[DEBUG] draw_cards called: count={count}")
    print(f"[DEBUG] Call stack: {''.join(traceback.format_stack()[-5:-1])}")
    drawn = []
    for _ in range(count):
        if player.deck:
            card = player.deck.pop(0)
            player.hand.append(card)
            drawn.append(card)
    print(f"[DEBUG] drew {len(drawn)} cards: {[c.name for c in drawn]}")
    return drawn


def _player_index(game_state: 'GameState', player: 'Player') -> int:
    """Get the player index (0 or 1) for reliable player resolution in PLAYTEST mode."""
    return 0 if player is game_state.player1 else 1


def trash_from_hand(player: 'Player', count: int, game_state: 'GameState' = None, source_card: 'Card' = None) -> List['Card']:
    """Trash cards from hand.

    If game_state is provided, creates a player choice for selection.
    Otherwise, auto-selects using AI logic (lowest cost first).
    """
    from ..game_engine import PendingChoice

    if not player.hand or count <= 0:
        return []

    # If game_state provided and player has more cards than needed, create choice
    if game_state and len(player.hand) > count:
        options = []
        for i, card in enumerate(player.hand):
            options.append({
                "id": str(i),
                "label": f"{card.name} (Cost: {card.cost or 0})",
                "card_id": card.id,
                "card_name": card.name,
            })

        game_state.pending_choice = PendingChoice(
            choice_id=f"trash_{uuid.uuid4().hex[:8]}",
            choice_type="select_cards",
            prompt=f"Choose {count} card(s) from your hand to trash",
            options=options,
            min_selections=count,
            max_selections=count,
            source_card_id=source_card.id if source_card else None,
            source_card_name=source_card.name if source_card else None,
            callback_action="trash_from_hand",
            callback_data={"player_id": player.player_id, "player_index": _player_index(game_state, player), "count": count}
        )
        return []  # Choice created, will be resolved later

    # Auto-trash (AI logic or when hand size <= count)
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


def create_trash_choice(game_state: 'GameState', player: 'Player', count: int,
                        source_card: 'Card' = None, prompt: str = None) -> bool:
    """Create a pending choice for player to select cards to trash.

    Returns True if a choice was created, False if auto-trashed (no choices available).
    """
    from ..game_engine import PendingChoice

    if not player.hand:
        return False

    # If player has exactly 'count' cards, auto-trash them (no choice needed)
    if len(player.hand) <= count:
        trash_from_hand(player, count)
        return False

    # Create options from hand
    options = []
    for i, card in enumerate(player.hand):
        options.append({
            "id": str(i),
            "label": f"{card.name} (Cost: {card.cost or 0})",
            "card_id": card.id,
            "card_name": card.name,
        })

    # Set up the pending choice
    game_state.pending_choice = PendingChoice(
        choice_id=f"trash_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt=prompt or f"Choose {count} card(s) from your hand to trash",
        options=options,
        min_selections=count,
        max_selections=count,
        source_card_id=source_card.id if source_card else None,
        source_card_name=source_card.name if source_card else None,
        callback_action="trash_from_hand",
        callback_data={"player_id": player.player_id, "count": count}
    )
    return True


def create_target_choice(game_state: 'GameState', player: 'Player',
                         targets: List['Card'], prompt: str,
                         source_card: 'Card' = None,
                         min_selections: int = 1, max_selections: int = 1,
                         callback_action: str = None,
                         callback_data: dict = None) -> bool:
    """Create a pending choice for player to select a target.

    Returns True if a choice was created.
    """
    from ..game_engine import PendingChoice

    if not targets:
        return False

    # Create options from targets
    options = []
    for i, card in enumerate(targets):
        options.append({
            "id": str(i),
            "label": f"{card.name} (Power: {card.power or 0})",
            "card_id": card.id,
            "card_name": card.name,
        })

    action = callback_action or "select_target"
    data = {
        "player_id": player.player_id,
        "player_index": 0 if player is game_state.player1 else 1,
        "target_cards": [{"id": card.id, "name": card.name} for card in targets],
    }
    if callback_data:
        data.update(callback_data)

    game_state.pending_choice = PendingChoice(
        choice_id=f"target_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt=prompt,
        options=options,
        min_selections=min_selections,
        max_selections=max_selections,
        source_card_id=source_card.id if source_card else None,
        source_card_name=source_card.name if source_card else None,
        callback_action=action,
        callback_data=data
    )
    return True


def search_top_cards(game_state: 'GameState', player: 'Player', look_count: int,
                     add_count: int = 1, filter_fn=None, source_card: 'Card' = None,
                     prompt: str = None, trash_rest: bool = False,
                     play_to_field: bool = False, play_rested: bool = False) -> bool:
    """Look at top X cards, let player choose Y to add to hand (or play to field).
    Remaining cards go to bottom of deck in player-chosen order (or trash).

    Args:
        game_state: The game state
        player: The player searching
        look_count: Number of cards to look at from top of deck
        add_count: Number of cards player can add to hand (0 = optional)
        filter_fn: Optional function to filter which cards can be selected
        source_card: The card that triggered this search
        prompt: Custom prompt text
        trash_rest: If True, trash remaining cards instead of putting at bottom
        play_to_field: If True, play selected card to field instead of hand
        play_rested: If True and play_to_field, play the card rested

    Returns True if a choice was created or effect resolved.
    """
    from ..game_engine import PendingChoice

    if not player.deck:
        return True

    actual_look = min(look_count, len(player.deck))
    top_cards = player.deck[:actual_look]
    if not top_cards:
        return True

    source_name = source_card.name if source_card else ""
    source_id = source_card.id if source_card else ""

    # Apply filter if provided
    selectable = top_cards if not filter_fn else [c for c in top_cards if filter_fn(c)]

    # Valid selection indices
    valid_indices = [i for i, c in enumerate(top_cards) if c in selectable]

    if not valid_indices:
        # No valid targets — still need to order remaining to bottom (or trash)
        remaining = player.deck[:actual_look]
        for _ in range(actual_look):
            player.deck.pop(0)
        if trash_rest:
            for c in remaining:
                player.trash.append(c)
            game_state._log(f"{source_name}: No valid targets; trashed {len(remaining)} cards")
        elif len(remaining) <= 1:
            player.deck.extend(remaining)
            game_state._log(f"{source_name}: No valid targets; remaining placed at bottom")
        else:
            game_state._log(f"{source_name}: No valid targets in top {actual_look}")
            game_state._create_deck_order_choice(
                player, remaining, [],
                source_name=source_name,
                source_id=source_id,
            )
        return True

    # Build options showing all cards; non-valid marked [Cannot select]
    options = []
    for i, card in enumerate(top_cards):
        is_valid = i in valid_indices
        options.append({
            "id": str(i),
            "label": f"{card.name} (Cost: {card.cost or 0})" + ("" if is_valid else " [Cannot select]"),
            "card_id": card.id,
            "card_name": card.name,
            "selectable": is_valid,
        })

    max_sel = min(add_count if add_count > 0 else len(valid_indices), len(valid_indices))

    game_state.pending_choice = PendingChoice(
        choice_id=f"search_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt=prompt or f"Look at top {actual_look} cards. Choose up to {max_sel} to add to hand.",
        options=options,
        min_selections=0,
        max_selections=max_sel,
        source_card_id=source_id or None,
        source_card_name=source_name or None,
        callback_action="search_add_to_hand",
        callback_data={
            "player_id": player.player_id,
            "player_index": _player_index(game_state, player),
            "look_count": actual_look,
            "valid_indices": valid_indices,
            "source_name": source_name,
            "source_id": source_id,
            "trash_rest": trash_rest,
            "play_to_field": play_to_field,
            "play_rested": play_rested,
        }
    )
    return True


def reorder_top_cards(game_state: 'GameState', player: 'Player', look_count: int,
                      source_card: 'Card' = None, allow_top: bool = False) -> bool:
    """Look at top X cards of deck and place them.

    allow_top=False (default): Sequential ordering, all go to bottom of deck.
        For cards that say 'place them at the bottom of your deck in any order.'
    allow_top=True: Single choice — all go to top OR all go to bottom.
        For cards that say 'place them at the top or bottom of your deck in any order.'
    """
    if not player.deck:
        return True

    actual_look = min(look_count, len(player.deck))
    remaining = player.deck[:actual_look]
    for _ in range(actual_look):
        player.deck.pop(0)

    source_name = source_card.name if source_card else ""
    source_id = source_card.id if source_card else ""

    if len(remaining) == 0:
        return True

    if allow_top:
        # Single choice: all to top or all to bottom
        game_state._create_top_or_bottom_choice(
            player, remaining,
            source_name=source_name,
            source_id=source_id,
        )
    else:
        # Sequential ordering, all to bottom
        game_state._create_deck_order_choice(
            player, remaining, [],
            source_name=source_name,
            source_id=source_id,
        )
    return True


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
    """Add DON from DON deck (don_pool is a list of 'active'/'rested' strings, max 10)."""
    added = 0
    for _ in range(count):
        if len(player.don_pool) < 10:
            player.don_pool.append("active" if set_active else "rested")
            added += 1
    return added


def return_don_to_deck(game_state: 'GameState', player: 'Player', count: int,
                       source_card: 'Card' = None,
                       after_callback: str = None,
                       after_callback_data: dict = None) -> bool:
    """Return DON!! cards from field to DON deck, prompting player if DON is attached to characters.

    If all available DON are in the pool (none attached to characters),
    auto-removes from pool — no choice needed.  Otherwise prompts the player
    to choose which DON to return (from pool and/or detached from characters).

    Returns True if DON was auto-returned (caller should continue with the effect).
    Returns False if a PendingChoice was created (caller should ``return True``
    from its handler — the rest of the effect will run in the callback).
    """
    from ..game_engine import PendingChoice

    total_pool = len(player.don_pool)
    attached_total = sum(getattr(c, 'attached_don', 0) for c in player.cards_in_play)
    if getattr(player, 'leader', None):
        attached_total += getattr(player.leader, 'attached_don', 0)

    if total_pool + attached_total < count:
        return True  # Not enough DON to pay — effect fizzles

    # If only 1 DON total and we need 1, auto-return (no real choice)
    if total_pool + attached_total == count and total_pool == count and attached_total == 0:
        for _ in range(count):
            player.don_pool.pop()
        return True

    # Build options: pool DON + DON attached to characters/leader
    options = []
    for i in range(total_pool):
        state = player.don_pool[i]
        options.append({
            "id": f"pool_{i}",
            "label": f"DON!! from cost area ({state})",
            "card_id": "don_pool",
            "card_name": f"DON ({state})",
        })
    if getattr(player, 'leader', None) and getattr(player.leader, 'attached_don', 0) > 0:
        for d in range(player.leader.attached_don):
            options.append({
                "id": f"leader_{d}",
                "label": f"DON!! from {player.leader.name} (Leader)",
                "card_id": player.leader.id,
                "card_name": player.leader.name,
            })
    for ci, c in enumerate(player.cards_in_play):
        for d in range(getattr(c, 'attached_don', 0)):
            options.append({
                "id": f"char_{ci}_{d}",
                "label": f"DON!! from {c.name}",
                "card_id": c.id,
                "card_name": c.name,
            })

    game_state.pending_choice = PendingChoice(
        choice_id=f"don_return_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt=f"Choose {count} DON!! card{'s' if count > 1 else ''} to return to DON deck",
        options=options,
        min_selections=count,
        max_selections=count,
        source_card_id=source_card.id if source_card else None,
        source_card_name=source_card.name if source_card else None,
        callback_action="don_return",
        callback_data={
            "player_id": player.player_id,
            "count": count,
            "after_callback": after_callback,
            "after_callback_data": after_callback_data or {},
        },
    )
    return False  # Pending — caller should return True


def optional_don_return(game_state: 'GameState', player: 'Player', count: int,
                        source_card: 'Card' = None,
                        after_callback: str = None,
                        after_callback_data: dict = None) -> bool:
    """Prompt the player whether they want to pay an optional DON!! -X cost.

    In OPTCG, bolded DON!! -X costs are optional.  This creates a yes/no
    choice first.  If the player says yes, it chains into ``return_don_to_deck``
    so they can choose *which* DON to return.

    Returns True  → cost cannot be paid (not enough DON) — caller should
                    treat the effect as fizzled and ``return True``.
    Returns False → a PendingChoice was created — caller should ``return True``
                    and let the callback system handle the rest.
    """
    from ..game_engine import PendingChoice

    total_don = len(player.don_pool) + sum(getattr(c, 'attached_don', 0) for c in player.cards_in_play)
    if getattr(player, 'leader', None):
        total_don += getattr(player.leader, 'attached_don', 0)
    if total_don < count:
        return True  # Can't pay — fizzle silently

    game_state.pending_choice = PendingChoice(
        choice_id=f"don_opt_{uuid.uuid4().hex[:8]}",
        choice_type="yes_no",
        prompt=f"Return {count} DON!! to DON deck to activate {source_card.name}'s effect?" if source_card else f"Return {count} DON!! to DON deck?",
        options=[
            {"id": "yes", "label": f"Yes, return {count} DON!!", "card_id": "don_opt", "card_name": "DON!!"},
            {"id": "no", "label": "No, skip this effect", "card_id": "don_opt", "card_name": "DON!!"},
        ],
        min_selections=1,
        max_selections=1,
        source_card_id=source_card.id if source_card else None,
        source_card_name=source_card.name if source_card else None,
        callback_action="don_optional",
        callback_data={
            "player_id": player.player_id,
            "count": count,
            "after_callback": after_callback,
            "after_callback_data": after_callback_data or {},
        },
    )
    return False  # Pending


def give_don_to_card(player: 'Player', target: 'Card', count: int, rested_only: bool = False) -> int:
    """Give DON from pool to a card (increments attached_don, removes from pool)."""
    given = 0
    for i in range(len(player.don_pool) - 1, -1, -1):
        if given >= count:
            break
        if rested_only and player.don_pool[i] != "rested":
            continue
        player.don_pool.pop(i)
        target.attached_don = getattr(target, 'attached_don', 0) + 1
        given += 1
    return given


# =============================================================================
# PLAYER CHOICE HELPERS - Create pending choices for player decisions
# =============================================================================

def create_don_assignment_choice(game_state: 'GameState', player: 'Player',
                                  targets: List['Card'], don_count: int,
                                  source_card: 'Card' = None,
                                  rested_only: bool = True,
                                  prompt: str = None) -> bool:
    """Create a pending choice for assigning DON to a character.

    Args:
        game_state: The game state
        player: Player assigning DON
        targets: Valid targets for DON assignment
        don_count: Number of DON to assign
        source_card: Card that triggered this effect
        rested_only: Only use rested DON
        prompt: Custom prompt text

    Returns True if choice was created.
    """
    from ..game_engine import PendingChoice

    if not targets:
        return False

    # Check if player has enough DON
    available_don = [d for d in player.don_cards if not rested_only or d.is_resting]
    if len(available_don) < don_count:
        return False

    options = []
    for i, card in enumerate(targets):
        options.append({
            "id": str(i),
            "label": f"{card.name} (Power: {card.power or 0}, DON: {getattr(card, 'attached_don', 0)})",
            "card_id": card.id,
            "card_name": card.name,
        })

    game_state.pending_choice = PendingChoice(
        choice_id=f"don_assign_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt=prompt or f"Choose a Character to give {don_count} rested DON",
        options=options,
        min_selections=1,
        max_selections=1,
        source_card_id=source_card.id if source_card else None,
        source_card_name=source_card.name if source_card else None,
        callback_action="assign_don",
        callback_data={
            "player_id": player.player_id,
            "don_count": don_count,
            "rested_only": rested_only,
            "target_cards": [{"id": c.id, "name": c.name} for c in targets],
        }
    )
    return True


def create_power_effect_choice(game_state: 'GameState', player: 'Player',
                                targets: List['Card'], power_amount: int,
                                source_card: 'Card' = None,
                                prompt: str = None,
                                min_selections: int = 1,
                                max_selections: int = 1) -> bool:
    """Create a pending choice for applying power modifier to one or more targets.

    Args:
        game_state: The game state
        player: Player making the choice
        targets: Valid targets for power effect
        power_amount: Power modifier (positive or negative)
        source_card: Card that triggered this effect
        prompt: Custom prompt text
        min_selections: Minimum number of targets to select (0 = optional)
        max_selections: Maximum number of targets to select

    Returns True if choice was created.
    """
    from ..game_engine import PendingChoice

    if not targets:
        return False

    options = []
    for i, card in enumerate(targets):
        options.append({
            "id": str(i),
            "label": f"{card.name} (Power: {card.power or 0})",
            "card_id": card.id,
            "card_name": card.name,
        })

    sign = "+" if power_amount >= 0 else ""
    game_state.pending_choice = PendingChoice(
        choice_id=f"power_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt=prompt or f"Choose up to {max_selections} Character(s) to give {sign}{power_amount} power",
        options=options,
        min_selections=min_selections,
        max_selections=max_selections,
        source_card_id=source_card.id if source_card else None,
        source_card_name=source_card.name if source_card else None,
        callback_action="apply_power",
        callback_data={
            "player_id": player.player_id,
            "power_amount": power_amount,
            "target_cards": [{"id": c.id, "name": c.name} for c in targets],
        }
    )
    return True


def create_ko_choice(game_state: 'GameState', player: 'Player',
                      targets: List['Card'], source_card: 'Card' = None,
                      prompt: str = None, callback_action: str = None,
                      callback_data: dict = None) -> bool:
    """Create a pending choice for KO'ing a target.

    Returns True if choice was created.
    If callback_action is provided, it overrides the default 'ko_target' action
    so the KO happens inside that custom handler instead.
    """
    from ..game_engine import PendingChoice

    if not targets:
        return False

    options = []
    for i, card in enumerate(targets):
        owner = "Your" if card in player.cards_in_play else "Opponent's"
        options.append({
            "id": str(i),
            "label": f"{owner} {card.name} (Power: {card.power or 0})",
            "card_id": card.id,
            "card_name": card.name,
        })

    cb_data = {
        "player_id": player.player_id,
        "target_cards": [{"id": c.id, "name": c.name} for c in targets],
    }
    if callback_data:
        cb_data.update(callback_data)

    game_state.pending_choice = PendingChoice(
        choice_id=f"ko_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt=prompt or "Choose a Character to KO",
        options=options,
        min_selections=1,
        max_selections=1,
        source_card_id=source_card.id if source_card else None,
        source_card_name=source_card.name if source_card else None,
        callback_action=callback_action or "ko_target",
        callback_data=cb_data,
    )
    return True


def create_return_to_hand_choice(game_state: 'GameState', player: 'Player',
                                  targets: List['Card'], source_card: 'Card' = None,
                                  prompt: str = None, optional: bool = False) -> bool:
    """Create a pending choice for returning a card to hand.

    Returns True if choice was created.
    """
    from ..game_engine import PendingChoice

    if not targets:
        return False

    options = []
    for i, card in enumerate(targets):
        options.append({
            "id": str(i),
            "label": f"{card.name} (Cost: {card.cost or 0})",
            "card_id": card.id,
            "card_name": card.name,
        })

    game_state.pending_choice = PendingChoice(
        choice_id=f"return_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt=prompt or "Choose a Character to return to hand",
        options=options,
        min_selections=0 if optional else 1,
        max_selections=1,
        source_card_id=source_card.id if source_card else None,
        source_card_name=source_card.name if source_card else None,
        callback_action="return_to_hand",
        callback_data={
            "player_id": player.player_id,
            "target_cards": [{"id": c.id, "name": c.name} for c in targets],
        }
    )
    return True


def create_play_from_trash_choice(game_state: 'GameState', player: 'Player',
                                   targets: List['Card'], source_card: 'Card' = None,
                                   rest_on_play: bool = True,
                                   prompt: str = None) -> bool:
    """Create a pending choice for playing a card from trash.

    Returns True if choice was created.
    """
    from ..game_engine import PendingChoice

    if not targets:
        return False

    options = []
    for i, card in enumerate(targets):
        options.append({
            "id": str(i),
            "label": f"{card.name} (Cost: {card.cost or 0})",
            "card_id": card.id,
            "card_name": card.name,
        })

    game_state.pending_choice = PendingChoice(
        choice_id=f"play_trash_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt=prompt or "Choose a card to play from trash",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=source_card.id if source_card else None,
        source_card_name=source_card.name if source_card else None,
        callback_action="play_from_trash",
        callback_data={
            "player_id": player.player_id,
            "rest_on_play": rest_on_play,
            "target_cards": [{"id": c.id, "name": c.name} for c in targets],
        }
    )
    return True


def create_mode_choice(game_state: 'GameState', player: 'Player',
                       modes: List[Dict[str, str]], source_card: 'Card' = None,
                       prompt: str = None) -> bool:
    """Create a pending choice for selecting between effect modes.

    Args:
        game_state: The game state
        player: Player making the choice
        modes: List of mode options, each with 'id', 'label', and 'description'
        source_card: Card that triggered this effect
        prompt: Custom prompt text

    Returns True if choice was created.
    """
    from ..game_engine import PendingChoice

    if not modes or len(modes) < 2:
        return False

    options = []
    for mode in modes:
        options.append({
            "id": mode.get("id", str(len(options))),
            "label": mode.get("label", f"Mode {len(options) + 1}"),
            "description": mode.get("description", ""),
        })

    game_state.pending_choice = PendingChoice(
        choice_id=f"mode_{uuid.uuid4().hex[:8]}",
        choice_type="select_mode",
        prompt=prompt or "Choose an effect mode",
        options=options,
        min_selections=1,
        max_selections=1,
        source_card_id=source_card.id if source_card else None,
        source_card_name=source_card.name if source_card else None,
        callback_action="select_mode",
        callback_data={
            "player_id": player.player_id,
            "card_id": source_card.id if source_card else None,
            "modes": modes,
        }
    )
    return True


def create_own_character_choice(game_state: 'GameState', player: 'Player',
                                 targets: List['Card'], source_card: 'Card' = None,
                                 prompt: str = None, callback_action: str = "return_own_to_hand",
                                 optional: bool = False) -> bool:
    """Create a pending choice for selecting own character (for return/trash costs).

    Returns True if choice was created.
    """
    from ..game_engine import PendingChoice

    if not targets:
        return False

    options = []
    for i, card in enumerate(targets):
        options.append({
            "id": str(i),
            "label": f"{card.name} (Cost: {card.cost or 0})",
            "card_id": card.id,
            "card_name": card.name,
        })

    game_state.pending_choice = PendingChoice(
        choice_id=f"own_char_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt=prompt or "Choose one of your Characters",
        options=options,
        min_selections=0 if optional else 1,
        max_selections=1,
        source_card_id=source_card.id if source_card else None,
        source_card_name=source_card.name if source_card else None,
        callback_action=callback_action,
        callback_data={
            "player_id": player.player_id,
            "target_cards": [{"id": c.id, "name": c.name} for c in targets],
        }
    )
    return True


def create_cost_reduction_choice(game_state: 'GameState', player: 'Player',
                                  targets: List['Card'], cost_reduction: int,
                                  source_card: 'Card' = None,
                                  prompt: str = None) -> bool:
    """Create a pending choice for applying cost reduction to opponent's character.

    Args:
        game_state: The game state
        player: Player making the choice
        targets: Valid targets for cost reduction
        cost_reduction: Amount of cost reduction (negative number)
        source_card: Card that triggered this effect
        prompt: Custom prompt text

    Returns True if choice was created.
    """
    from ..game_engine import PendingChoice

    if not targets:
        return False

    options = []
    for i, card in enumerate(targets):
        current_cost = (getattr(card, 'cost', 0) or 0) + getattr(card, 'cost_modifier', 0)
        options.append({
            "id": str(i),
            "label": f"{card.name} (Cost: {current_cost})",
            "card_id": card.id,
            "card_name": card.name,
        })

    game_state.pending_choice = PendingChoice(
        choice_id=f"cost_reduce_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt=prompt or f"Choose a Character to give {cost_reduction} cost",
        options=options,
        min_selections=1,
        max_selections=1,
        source_card_id=source_card.id if source_card else None,
        source_card_name=source_card.name if source_card else None,
        callback_action="apply_cost_reduction",
        callback_data={
            "player_id": player.player_id,
            "cost_reduction": cost_reduction,
            "target_cards": [{"id": c.id, "name": c.name} for c in targets],
        }
    )
    return True


def create_play_from_hand_choice(game_state: 'GameState', player: 'Player',
                                  targets: List['Card'], source_card: 'Card' = None,
                                  rest_on_play: bool = False,
                                  prompt: str = None) -> bool:
    """Create a pending choice for playing a card from hand.

    Returns True if choice was created.
    """
    from ..game_engine import PendingChoice

    if not targets:
        return False

    options = []
    for i, card in enumerate(targets):
        options.append({
            "id": str(i),
            "label": f"{card.name} (Cost: {card.cost or 0})",
            "card_id": card.id,
            "card_name": card.name,
        })

    game_state.pending_choice = PendingChoice(
        choice_id=f"play_hand_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt=prompt or "Choose a card to play from hand",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=source_card.id if source_card else None,
        source_card_name=source_card.name if source_card else None,
        callback_action="play_from_hand",
        callback_data={
            "player_id": player.player_id,
            "rest_on_play": rest_on_play,
            "target_cards": [{"id": c.id, "name": c.name} for c in targets],
        }
    )
    return True


def create_bottom_deck_choice(game_state: 'GameState', player: 'Player',
                               targets: List['Card'], source_card: 'Card' = None,
                               prompt: str = None, callback_action: str = None,
                               min_selections: int = 1) -> bool:
    """Create a pending choice for placing a card at bottom of deck.

    Returns True if choice was created.
    """
    from ..game_engine import PendingChoice

    if not targets:
        return False

    options = []
    for i, card in enumerate(targets):
        options.append({
            "id": str(i),
            "label": f"{card.name} (Cost: {card.cost or 0})",
            "card_id": card.id,
            "card_name": card.name,
        })

    game_state.pending_choice = PendingChoice(
        choice_id=f"bottom_deck_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt=prompt or "Choose a card to place at bottom of deck",
        options=options,
        min_selections=min_selections,
        max_selections=1,
        source_card_id=source_card.id if source_card else None,
        source_card_name=source_card.name if source_card else None,
        callback_action=callback_action or "place_at_bottom",
        callback_data={
            "player_id": player.player_id,
            "target_cards": [{"id": c.id, "name": c.name} for c in targets],
        }
    )
    return True


def create_rest_choice(game_state: 'GameState', player: 'Player',
                        targets: List['Card'], source_card: 'Card' = None,
                        prompt: str = None, max_selections: int = 1,
                        min_selections: int = 1,
                        callback_action: str = None) -> bool:
    """Create a pending choice for resting target(s).

    Returns True if choice was created.
    max_selections > 1 uses rest_targets_multi callback to handle multiple rests.
    """
    from ..game_engine import PendingChoice

    if not targets:
        return False

    options = []
    for i, card in enumerate(targets):
        owner = "Your" if card in player.cards_in_play else "Opponent's"
        options.append({
            "id": str(i),
            "label": f"{owner} {card.name} (Cost: {card.cost or 0})",
            "card_id": card.id,
            "card_name": card.name,
        })

    # Use multi-rest callback when selecting more than 1 target
    cb_action = callback_action or ("rest_targets_multi" if max_selections > 1 else "rest_target")

    game_state.pending_choice = PendingChoice(
        choice_id=f"rest_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt=prompt or f"Choose up to {max_selections} Character(s) to rest",
        options=options,
        min_selections=min_selections,
        max_selections=max_selections,
        source_card_id=source_card.id if source_card else None,
        source_card_name=source_card.name if source_card else None,
        callback_action=cb_action,
        callback_data={
            "player_id": player.player_id,
            "target_cards": [{"id": c.id, "name": c.name} for c in targets],
        }
    )
    return True


def create_set_active_choice(game_state: 'GameState', player: 'Player',
                              targets: List['Card'], source_card: 'Card' = None,
                              prompt: str = None, callback_action: str = "set_active",
                              extra_data: dict = None) -> bool:
    """Create a pending choice for setting a card active.

    Returns True if choice was created.
    """
    from ..game_engine import PendingChoice

    if not targets:
        return False

    options = []
    for i, card in enumerate(targets):
        options.append({
            "id": str(i),
            "label": f"{card.name} (Cost: {card.cost or 0})",
            "card_id": card.id,
            "card_name": card.name,
        })

    cb_data = {
        "player_id": player.player_id,
        "target_cards": [{"id": c.id, "name": c.name} for c in targets],
    }
    if extra_data:
        cb_data.update(extra_data)

    game_state.pending_choice = PendingChoice(
        choice_id=f"set_active_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt=prompt or "Choose a Character to set active",
        options=options,
        min_selections=1,
        max_selections=1,
        source_card_id=source_card.id if source_card else None,
        source_card_name=source_card.name if source_card else None,
        callback_action=callback_action,
        callback_data=cb_data,
    )
    return True


def create_multi_target_choice(game_state: 'GameState', player: 'Player',
                                targets: List['Card'], count: int,
                                callback_action: str,
                                source_card: 'Card' = None,
                                prompt: str = None) -> bool:
    """Create a pending choice for selecting multiple targets.

    Returns True if choice was created.
    """
    from ..game_engine import PendingChoice

    if not targets:
        return False

    options = []
    for i, card in enumerate(targets):
        options.append({
            "id": str(i),
            "label": f"{card.name} (Cost: {card.cost or 0})",
            "card_id": card.id,
            "card_name": card.name,
        })

    game_state.pending_choice = PendingChoice(
        choice_id=f"multi_{uuid.uuid4().hex[:8]}",
        choice_type="select_targets",
        prompt=prompt or f"Choose up to {count} targets",
        options=options,
        min_selections=1,
        max_selections=count,
        source_card_id=source_card.id if source_card else None,
        source_card_name=source_card.name if source_card else None,
        callback_action=callback_action,
        callback_data={
            "player_id": player.player_id,
            "target_cards": [{"id": c.id, "name": c.name} for c in targets],
        }
    )
    return True


def create_add_from_trash_choice(game_state: 'GameState', player: 'Player',
                                  targets: List['Card'], source_card: 'Card' = None,
                                  prompt: str = None) -> bool:
    """Create a pending choice for adding a card from trash to hand.

    Returns True if choice was created.
    """
    from ..game_engine import PendingChoice

    if not targets:
        return False

    options = []
    for i, card in enumerate(targets):
        options.append({
            "id": str(i),
            "label": f"{card.name} (Cost: {card.cost or 0})",
            "card_id": card.id,
            "card_name": card.name,
        })

    game_state.pending_choice = PendingChoice(
        choice_id=f"add_trash_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt=prompt or "Choose a card to add from trash to hand",
        options=options,
        min_selections=0,
        max_selections=1,
        source_card_id=source_card.id if source_card else None,
        source_card_name=source_card.name if source_card else None,
        callback_action="add_from_trash_to_hand",
        callback_data={
            "player_id": player.player_id,
            "target_cards": [{"id": c.id, "name": c.name} for c in targets],
        }
    )
    return True


def create_hand_discard_choice(game_state: 'GameState', player: 'Player',
                                targets: List['Card'], callback_action: str,
                                source_card: 'Card' = None,
                                prompt: str = None) -> bool:
    """Create a pending choice for discarding a card from hand.

    Returns True if choice was created.
    """
    from ..game_engine import PendingChoice

    if not targets:
        return False

    options = []
    for i, card in enumerate(targets):
        options.append({
            "id": str(i),
            "label": f"{card.name} (Cost: {card.cost or 0})",
            "card_id": card.id,
            "card_name": card.name,
        })

    game_state.pending_choice = PendingChoice(
        choice_id=f"discard_{uuid.uuid4().hex[:8]}",
        choice_type="select_cards",
        prompt=prompt or "Choose a card to discard",
        options=options,
        min_selections=1,
        max_selections=1,
        source_card_id=source_card.id if source_card else None,
        source_card_name=source_card.name if source_card else None,
        callback_action=callback_action,
        callback_data={
            "player_id": player.player_id,
            "target_cards": [{"id": c.id, "name": c.name} for c in targets],
        }
    )
    return True


def create_add_to_life_choice(game_state: 'GameState', player: 'Player',
                               targets: List['Card'], source_card: 'Card' = None,
                               prompt: str = None) -> bool:
    """Create a pending choice for adding a character to life.

    Args:
        game_state: The game state
        player: Player making the choice
        targets: Valid targets to add to life
        source_card: Card that triggered this effect
        prompt: Custom prompt text

    Returns True if choice was created.
    """
    from ..game_engine import PendingChoice

    if not targets:
        return False

    options = []
    for i, card in enumerate(targets):
        options.append({
            "id": str(i),
            "label": f"{card.name} (Cost: {getattr(card, 'cost', 0) or 0})",
            "card_id": card.id,
            "card_name": card.name,
        })

    game_state.pending_choice = PendingChoice(
        choice_id=f"add_life_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt=prompt or "Choose a Character to add to life",
        options=options,
        min_selections=1,
        max_selections=1,
        source_card_id=source_card.id if source_card else None,
        source_card_name=source_card.name if source_card else None,
        callback_action="add_to_opponent_life",
        callback_data={
            "player_id": player.player_id,
            "target_cards": [{"id": c.id, "name": c.name} for c in targets],
        }
    )
    return True


def create_dual_target_choice(game_state: 'GameState', player: 'Player',
                               targets1: List['Card'], callback1: str,
                               targets2: List['Card'], callback2: str,
                               source_card: 'Card' = None,
                               prompt: str = None) -> bool:
    """Create a choice for effects that target two different groups.

    For simplicity, this creates the first choice and stores data for the second.
    Returns True if choice was created.
    """
    from ..game_engine import PendingChoice

    if not targets1:
        return False

    options = []
    for i, card in enumerate(targets1):
        owner = "Your" if card in player.cards_in_play else "Opponent's"
        options.append({
            "id": str(i),
            "label": f"{owner} {card.name}",
            "card_id": card.id,
            "card_name": card.name,
        })

    game_state.pending_choice = PendingChoice(
        choice_id=f"dual_{uuid.uuid4().hex[:8]}",
        choice_type="select_target",
        prompt=prompt or "Choose first target",
        options=options,
        min_selections=1,
        max_selections=1,
        source_card_id=source_card.id if source_card else None,
        source_card_name=source_card.name if source_card else None,
        callback_action=callback1,
        callback_data={
            "player_id": player.player_id,
            "target_cards": [{"id": c.id, "name": c.name} for c in targets1],
            "second_targets": [{"id": c.id, "name": c.name} for c in targets2],
            "second_callback": callback2,
        }
    )
    return True




# =============================================================================
# REGISTRY QUERY FUNCTIONS
# =============================================================================

def get_all_hardcoded_cards() -> List[str]:
    """Get list of all card IDs with hardcoded effects."""
    return list(_hardcoded_effects.keys())


def get_hardcoded_effect_count() -> int:
    """Get total number of registered hardcoded effects."""
    return sum(len(effects) for effects in _hardcoded_effects.values())


# Import all set-specific effects to register them
from . import sets  # noqa: F401
