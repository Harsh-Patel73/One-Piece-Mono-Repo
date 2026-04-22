"""
One Piece TCG Game Engine

This module provides the main game logic for simulating One Piece TCG matches.
It integrates with the mechanics module for combat, blockers, and triggers.
"""

import random
import uuid
import re
from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Dict, Any, Callable
from .models.cards import Card
from .models.enums import GamePhase
from .handlers.effect_handlers import trigger_effect
from .effects.parser import parse_effect
from .effects.resolver import resolve_effect, EffectContext, get_resolver
from .effects.effects import EffectTiming, EffectType
from .effects.tokenizer import extract_keywords
from .effects.manager import get_effect_manager, parse_card_effects, get_effects_by_timing

# Constants
MAX_DON = 10
DON_PER_TURN = 2
# HAND_LIMIT removed - players can have unlimited cards in hand
STARTING_DON_P1 = 1
STARTING_DON_P2 = 2


@dataclass
class PendingChoice:
    """Represents a choice that requires player input before the effect can continue."""
    choice_id: str  # Unique ID for this choice
    choice_type: str  # "select_cards", "choose_option", "select_target"
    prompt: str  # "Choose 1 card from your hand to trash"
    options: List[Dict[str, Any]] = field(default_factory=list)  # [{id: "0", label: "Otama", card_id: "OP01-006"}, ...]
    min_selections: int = 1
    max_selections: int = 1
    source_card_id: Optional[str] = None  # Card that triggered this choice
    source_card_name: Optional[str] = None  # Name for display
    callback: Optional[Callable[['List[str]'], None]] = None  # Callable closure — preferred over string dispatch
    callback_action: Optional[str] = None  # DEPRECATED: use callback instead
    callback_data: Dict[str, Any] = field(default_factory=dict)  # DEPRECATED: use closure captures instead

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for sending to frontend."""
        return {
            "choice_id": self.choice_id,
            "choice_type": self.choice_type,
            "prompt": self.prompt,
            "options": self.options,
            "min_selections": self.min_selections,
            "max_selections": self.max_selections,
            "source_card_id": self.source_card_id,
            "source_card_name": self.source_card_name,
        }


class Player:
    """Represents a player in the game."""

    def __init__(self, name: str, deck: list[Card], leader: Card, player_id: str = None):
        self.name = name
        self.player_id = player_id  # Socket ID for network games
        self.deck = list(deck)
        self.hand: list[Card] = []
        self.cards_in_play: list[Card] = []
        self.leader = leader
        self.life_cards = self._build_life_pile(leader)
        self.don_pool: list[str] = []  # "active" or "rested"
        self.trash: list[Card] = []
        self.card_don_assignments: dict[Card, int] = {}
        self.has_mulliganed: bool = False
        self.draw_initial_hand()

    def _build_life_pile(self, leader: Card) -> list[Card]:
        """Build the life pile from the deck based on leader's life value."""
        count = int(leader.life or 0)
        life_cards = []
        for _ in range(count):
            if self.deck:
                card = self.deck.pop(0)
                setattr(card, 'is_face_up', False)
                life_cards.append(card)
        return life_cards

    def draw_initial_hand(self):
        """Draw the initial 5-card hand."""
        random.shuffle(self.deck)
        self.hand = self.deck[:5]
        self.deck = self.deck[5:]

    def mulligan(self, card_indices: List[int]):
        """
        Mulligan selected cards.

        Args:
            card_indices: Indices of cards in hand to replace
        """
        if self.has_mulliganed:
            print(f"{self.name} has already mulliganed.")
            return

        # Put selected cards back into deck
        cards_to_replace = [self.hand[i] for i in sorted(card_indices, reverse=True)]
        for card in cards_to_replace:
            self.hand.remove(card)
            self.deck.append(card)

        # Shuffle deck
        random.shuffle(self.deck)

        # Draw new cards
        for _ in range(len(cards_to_replace)):
            if self.deck:
                self.hand.append(self.deck.pop(0))

        self.has_mulliganed = True
        print(f"{self.name} mulligans {len(cards_to_replace)} cards.")

    def draw_card(self) -> Optional[Card]:
        """Draw a card from the deck."""
        if self.deck:
            c = self.deck.pop(0)
            self.hand.append(c)
            print(f"{self.name} draws {c.name}.")
            return c
        else:
            print(f"{self.name} has no cards to draw.")
            return None

    def add_card_to_play(self, card: Card, played_turn: int):
        """Play a card from hand to the field."""
        if card in self.hand:
            self.hand.remove(card)
        self.cards_in_play.append(card)
        setattr(card, 'played_turn', played_turn)

    def get_available_blockers(self) -> List[Tuple[int, Card]]:
        """Get all characters that can currently block."""
        blockers = []
        for i, card in enumerate(self.cards_in_play):
            if self._can_block(card):
                blockers.append((i, card))
        return blockers

    def _can_block(self, card: Card) -> bool:
        """Check if a card can be used as a blocker."""
        has_blocker = getattr(card, 'has_blocker', False) or getattr(card, 'is_blocker', False)
        if not has_blocker:
            return False
        if getattr(card, 'blocker_disabled', False):
            return False
        # Must not be resting
        return not card.is_resting

    def activate_blocker(self, blocker_index: int) -> Optional[Card]:
        """
        Activate a blocker to redirect an attack.

        Returns the blocker card, or None if invalid.
        """
        if blocker_index >= len(self.cards_in_play):
            return None

        blocker = self.cards_in_play[blocker_index]
        if not self._can_block(blocker):
            return None

        # Rest the blocker
        blocker.is_resting = True
        print(f"{self.name} activates {blocker.name} as a blocker!")
        return blocker

    def _parse_counter_event_power(self, effect: str) -> int:
        """
        Parse power boost from a Counter EVENT effect.

        Examples:
        - "[Counter] ... gains +5000 power" -> 5000
        - "[Counter] ... +4000 power" -> 4000
        """
        import re
        # Look for +XXXX power pattern
        match = re.search(r'\+(\d+)\s*power', effect, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 0

    def choose_counters_for_defense(self, target: Card, attacker_power: int) -> Tuple[int, List[Tuple[Card, int, bool]]]:
        """
        Choose and use counter cards to defend.

        Two types of counters:
        1. Counter VALUES on CHARACTER cards - FREE to use (no DON required)
        2. Counter EVENT cards with [Counter] effects - REQUIRE DON to play

        Returns:
            Tuple of (total counter value, list of (card, counter_value, is_event) used)
        """
        base = (target.power or 0) + getattr(target, 'power_modifier', 0)
        used: List[Tuple[Card, int, bool]] = []
        total = 0

        # First, check Counter EVENT cards (require DON)
        counter_events = [c for c in self.hand
                         if c.card_type == "EVENT"
                         and c.effect
                         and '[Counter]' in c.effect]

        for event in counter_events:
            cost = event.cost or 0
            power_boost = self._parse_counter_event_power(event.effect)

            # Only use if we have enough DON and it provides value
            if power_boost > 0 and cost <= self.available_don():
                # Check if using this would help defend (need > to beat attacker, ties go to attacker)
                if base + total + power_boost > attacker_power:
                    # Pay DON cost
                    paid = 0
                    for i in range(len(self.don_pool)):
                        if self.don_pool[i] == "active" and paid < cost:
                            self.don_pool[i] = "rested"
                            paid += 1

                    # Use the counter event
                    self.hand.remove(event)
                    self.trash.append(event)
                    used.append((event, power_boost, True))
                    total += power_boost

                    if base + total > attacker_power:
                        return total, used

        # Then use free counter VALUES from CHARACTER cards
        potential = [c for c in self.hand
                     if c.counter and c.counter > 0 and c.card_type == "CHARACTER"]

        for c in potential:
            if base + total > attacker_power:
                break
            used.append((c, c.counter, False))
            total += c.counter

        if base + total > attacker_power:
            # Only trash CHARACTER cards (EVENT cards already trashed above)
            for card, _, is_event in used:
                if not is_event and card in self.hand:
                    self.hand.remove(card)
                    self.trash.append(card)
            return total, used

        # Defense failed - don't use any counters
        # Undo EVENT card usage (already trashed, can't undo easily)
        # For now, just return what we have
        return 0, []

    def assign_don_to_card(self, card: Card, amount: int) -> int:
        """Attach DON to a card."""
        don_available = self.don_pool.count("active")
        actual_amount = min(amount, don_available)

        card.attached_don = getattr(card, 'attached_don', 0) + actual_amount

        for _ in range(actual_amount):
            idx = self.don_pool.index("active")
            self.don_pool[idx] = "rested"

        # Check DON conditions
        if card.effect:
            if '[DON!! x1]' in card.effect and card.attached_don >= 1:
                card.don_condition_met = True
            if '[DON!! x2]' in card.effect and card.attached_don >= 2:
                card.don_condition_met = True

        print(f"{self.name} assigns {actual_amount} DON to {card.name}")
        return actual_amount

    def available_don(self) -> int:
        """Get the number of active DON available."""
        return self.don_pool.count("active")

    def reset_for_new_turn(self):
        """Reset cards and DON for a new turn (Refresh Phase)."""
        # Unrest leader (unless prevented by an effect)
        if not getattr(self.leader, 'cannot_unrest', False) and not getattr(self.leader, 'birdcage_lock', False):
            self.leader.is_resting = False
        else:
            # Clear the one-time prevention flag after it takes effect
            self.leader.cannot_unrest = False
            self.leader.birdcage_lock = False
            print(f"{self.leader.name} cannot be set to Active this turn")
        self.leader.has_attacked = False
        for attr in list(vars(self.leader).keys()):
            if attr.endswith('_used'):
                setattr(self.leader, attr, False)

        # Unrest all characters and return attached DON
        for c in self.cards_in_play:
            # Check if this card is prevented from unresting
            if not getattr(c, 'cannot_unrest', False) and not getattr(c, 'birdcage_lock', False):
                c.is_resting = False
            else:
                # Clear the one-time prevention flag after it takes effect
                c.cannot_unrest = False
                c.birdcage_lock = False
                print(f"{c.name} cannot be set to Active this turn")
            c.has_attacked = False
            # Return attached DON to pool
            attached = getattr(c, 'attached_don', 0)
            c.attached_don = 0
            c.don_condition_met = False
            for attr in list(vars(c).keys()):
                if attr.endswith('_used'):
                    setattr(c, attr, False)

        # Return leader's attached DON
        leader_don = getattr(self.leader, 'attached_don', 0)
        self.leader.attached_don = 0
        self.leader.don_condition_met = False

        # Refresh all DON in pool to active
        self.don_pool = ["active"] * len(self.don_pool)
        self.card_don_assignments.clear()

        print(f"{self.name}'s cards have been reset and DON!! refreshed.")

    def discard_to_hand_limit(self, card_indices: List[int]):
        """Discard cards to meet hand limit."""
        # Sort indices in reverse to remove from end first
        for i in sorted(card_indices, reverse=True):
            if i < len(self.hand):
                card = self.hand.pop(i)
                self.trash.append(card)
                print(f"{self.name} discards {card.name}.")

    def take_life_damage(self) -> Tuple[Optional[Card], bool]:
        """
        Take damage to life.

        Per OPTCG rules:
        1. Reveal top card of life pile
        2. If it has [Trigger], you MAY activate the effect
        3. After trigger resolution (or declining), card goes to HAND

        Note: The card is NOT added to hand here - that happens after
        trigger resolution in the combat resolution code.

        Returns:
            Tuple of (life card flipped, has_trigger)
        """
        if not self.life_cards:
            return None, False

        life_card = self.life_cards.pop()
        has_trigger = bool(
            (life_card.trigger and life_card.trigger.strip())
            or (life_card.effect and '[Trigger]' in life_card.effect)
        )
        trigger_text = life_card.trigger or ''
        if not trigger_text.strip() and life_card.effect and '[Trigger]' in life_card.effect:
            # Extract trigger portion from effect text
            import re
            m = re.search(r'\[Trigger\]\s*(.*?)(?:<br>|$)', life_card.effect)
            trigger_text = m.group(0) if m else life_card.effect

        print(f"{self.name} loses a life card! ({len(self.life_cards)} remaining)")

        if has_trigger:
            print(f"  Trigger: {trigger_text}")

        # Card will be added to hand after trigger resolution (in combat code)
        # Do NOT add to hand or trash here - that's handled by the caller
        return life_card, has_trigger

class GameState:
    """
    Manages the game state and turn flow.

    This class handles:
    - Turn phases (Refresh, Draw, DON, Main, End)
    - Combat resolution with blocker and counter steps
    - Win condition checking
    """

    def __init__(self, p1: Player, p2: Player):
        self.player1 = p1
        self.player2 = p2
        self.current_player = p1
        self.opponent_player = p2
        self.turn_count = 1
        self.phase = GamePhase.MAIN  # Start in main phase for turn 1
        self.card_don_assignments = {}
        self.game_over = False
        self.winner: Optional[Player] = None
        self.action_logs: List[str] = []  # Collect logs for frontend
        self.pending_choice: Optional[PendingChoice] = None  # For effects requiring player input
        self.pending_attack: Optional[Dict[str, Any]] = None  # For combat resolution
        self.awaiting_response: Optional[str] = None  # "blocker" or "counter"

        # Initial DON setup
        p1.don_pool = ["active"] * STARTING_DON_P1
        p2.don_pool = ["active"] * STARTING_DON_P2

        self._log(f"=== Turn {self.turn_count}: {self.current_player.name} (DON: {len(self.current_player.don_pool)}) ===")

    def _log(self, message: str):
        """Add a log entry and print it."""
        self.action_logs.append(message)
        print(message)

    def get_and_clear_logs(self) -> List[str]:
        """Get all logs and clear the list."""
        logs = self.action_logs.copy()
        self.action_logs = []
        return logs

    def get_logs(self) -> List[str]:
        """Get all logs without clearing."""
        return self.action_logs.copy()

    def _create_deck_order_choice(self, player, remaining_cards, ordered_so_far,
                                    source_name="", source_id="",
                                    remaining_cards_data=None, placement="bottom"):
        """Create a PendingChoice for the player to pick the next card to place.

        Sequential ordering: pick one card at a time, all go to the specified placement.
        placement: 'bottom' or 'top'
        """
        if remaining_cards_data is None:
            remaining_cards_data = [
                {"id": c.id, "name": c.name, "cost": c.cost or 0, "unique_id": id(c)}
                for c in remaining_cards
            ]
            # Store the actual card objects in a temporary holding area
            if not hasattr(self, '_deck_order_holding'):
                self._deck_order_holding = {}
            for c in remaining_cards:
                self._deck_order_holding[id(c)] = c

        total = len(remaining_cards_data) + len(ordered_so_far)
        current_pos = len(ordered_so_far) + 1
        dest = "TOP" if placement == "top" else "BOTTOM"
        options = []
        for i, card_info in enumerate(remaining_cards_data):
            options.append({
                "id": str(i),
                "label": f"{card_info['name']} (Cost: {card_info.get('cost', 0)})",
                "card_id": card_info["id"],
                "card_name": card_info["name"],
            })

        self.pending_choice = PendingChoice(
            choice_id=f"deck_order_{uuid.uuid4().hex[:8]}",
            choice_type="select_target",
            prompt=f"{source_name}: Choose card {current_pos} of {total} for {dest} of deck (first chosen = {'on top' if placement == 'top' else 'deepest'})",
            options=options,
            min_selections=1,
            max_selections=1,
            source_card_id=source_id,
            source_card_name=source_name,
            callback_action="nami_deck_order",
            callback_data={
                "player_id": player.player_id,
                "player_index": 0 if player is self.player1 else 1,
                "remaining_cards": remaining_cards_data,
                "ordered_so_far": ordered_so_far,
                "source_name": source_name,
                "source_id": source_id,
                "placement": placement,
            },
        )

    def _create_top_or_bottom_choice(self, player, cards,
                                      source_name="", source_id=""):
        """Single choice: place ALL looked-at cards at top or bottom of deck."""
        if not hasattr(self, '_deck_order_holding'):
            self._deck_order_holding = {}
        cards_data = []
        for c in cards:
            info = {"id": c.id, "name": c.name, "cost": c.cost or 0, "unique_id": id(c)}
            cards_data.append(info)
            self._deck_order_holding[id(c)] = c

        card_names = ", ".join(c.name for c in cards)
        self.pending_choice = PendingChoice(
            choice_id=f"deck_topbot_{uuid.uuid4().hex[:8]}",
            choice_type="select_target",
            prompt=f"{source_name}: Looked at {len(cards)} card(s): {card_names}. Place all at top or bottom?",
            options=[
                {"id": "top", "label": f"Place all {len(cards)} cards on TOP of deck"},
                {"id": "bottom", "label": f"Place all {len(cards)} cards at BOTTOM of deck"},
            ],
            min_selections=1,
            max_selections=1,
            source_card_id=source_id,
            source_card_name=source_name,
            callback_action="deck_top_or_bottom_all",
            callback_data={
                "player_id": player.player_id,
                "player_index": 0 if player is self.player1 else 1,
                "cards_data": cards_data,
                "source_name": source_name,
            },
        )

    def _find_card_by_info(self, card_info):
        """Find a Card object from the deck_order_holding area by unique_id."""
        if not hasattr(self, '_deck_order_holding'):
            return None
        unique_id = card_info.get("unique_id")
        if unique_id and unique_id in self._deck_order_holding:
            return self._deck_order_holding.pop(unique_id)
        return None

    def _find_card_owner(self, card: Card) -> Optional[Player]:
        """Find the player that currently owns the provided leader or in-play card."""
        if card is self.player1.leader or card in self.player1.cards_in_play:
            return self.player1
        if card is self.player2.leader or card in self.player2.cards_in_play:
            return self.player2
        return None

    def _find_in_play_card_by_id(self, card_id: str) -> Optional[Card]:
        """Find a leader or in-play card by id."""
        for card in [self.player1.leader, *self.player1.cards_in_play, self.player2.leader, *self.player2.cards_in_play]:
            if card and card.id == card_id:
                return card
        return None

    def _resolve_ko_prevention_choice(self, prevented: bool) -> str:
        """Continue a pending K.O. prevention flow after the player chooses to use or decline it."""
        context = getattr(self, "_pending_ko_context", None)
        if not context:
            return "ko"

        if prevented:
            target = self._find_in_play_card_by_id(context["target_id"])
            if target:
                self._log(f"{target.name} was saved from being K.O.'d")
            return self._finalize_character_ko(context, "prevented")

        context["candidate_index"] += 1
        return self._continue_character_ko_attempt()

    def _finalize_character_ko(self, context: Dict[str, Any], result: str) -> str:
        """Finalize a character K.O. attempt and run any completion callback."""
        target = self._find_in_play_card_by_id(context["target_id"])
        owner = self.player1 if context["owner_index"] == 0 else self.player2
        controller = self.player1 if context.get("controller_index") == 0 else self.player2 if context.get("controller_index") == 1 else None
        attacker = self._find_in_play_card_by_id(context["attacker_id"]) if context.get("attacker_id") else None
        callback = context.get("after_resolve")
        self._pending_ko_context = None

        if result == "ko" and target and target in owner.cards_in_play:
            owner.cards_in_play.remove(target)
            owner.trash.append(target)
            self._log(f"{target.name} was K.O.'d")

            effect_manager = get_effect_manager()
            effect_manager.on_ko(self, owner, target)

            if controller and controller.leader:
                from .effects.effect_registry import has_hardcoded_effect, execute_hardcoded_effect
                if has_hardcoded_effect(controller.leader.id, 'on_opponent_ko'):
                    execute_hardcoded_effect(self, controller, controller.leader, 'on_opponent_ko')

        if callback:
            callback(result, owner, target, attacker)

        return result

    def _continue_character_ko_attempt(self) -> str:
        """Run the next K.O. prevention candidate, or finish the K.O. if none prevent it."""
        context = getattr(self, "_pending_ko_context", None)
        if not context:
            return "ko"

        owner = self.player1 if context["owner_index"] == 0 else self.player2
        target = self._find_in_play_card_by_id(context["target_id"])
        if not target or target not in owner.cards_in_play:
            return self._finalize_character_ko(context, "prevented")

        from .effects.effect_registry import execute_hardcoded_effect, has_hardcoded_effect

        candidates = context["candidates"]
        while context["candidate_index"] < len(candidates):
            candidate_id = candidates[context["candidate_index"]]
            candidate = self._find_in_play_card_by_id(candidate_id)
            if not candidate or not has_hardcoded_effect(candidate.id, "on_ko_prevention"):
                context["candidate_index"] += 1
                continue

            result = execute_hardcoded_effect(self, owner, candidate, "on_ko_prevention")
            if self.pending_choice:
                return "pending"
            if result:
                return self._finalize_character_ko(context, "prevented")
            context["candidate_index"] += 1

        return self._finalize_character_ko(context, "ko")

    def _queue_kyros_ko_prevention(self, player: Player, card: Card, on_decline: Optional[Callable[[], None]] = None) -> bool:
        """Prompt for Kyros's Rebecca/Corrida Coliseum K.O. replacement."""
        context = getattr(self, "_pending_ko_context", None)
        if not context or context.get("target_id") != card.id:
            return False

        options: List[Dict[str, str]] = []
        replacements: List[Card] = []
        leader = getattr(player, "leader", None)
        if leader and not getattr(leader, "is_resting", False):
            replacements.append(leader)
            options.append({"id": str(len(options)), "label": f"Rest {leader.name}"})
        for field_card in player.cards_in_play:
            if field_card is card:
                continue
            if getattr(field_card, "name", "") == "Corrida Coliseum" and not getattr(field_card, "is_resting", False):
                replacements.append(field_card)
                options.append({"id": str(len(options)), "label": f"Rest {field_card.name}"})

        if not replacements:
            return False

        choice = PendingChoice(
            choice_id=f"kyros_prevent_{uuid.uuid4().hex[:8]}",
            choice_type="select_target",
            prompt="Choose a card to rest instead of this Character being K.O.'d",
            options=options,
            min_selections=1,
            max_selections=1,
            source_card_id=card.id,
            source_card_name=card.name,
        )

        def callback(selected: List[str]) -> None:
            target_idx = int(selected[0]) if selected else -1
            if 0 <= target_idx < len(replacements):
                replacement = replacements[target_idx]
                replacement.is_resting = True
                self._log(f"{replacement.name} was rested instead")
                self._resolve_ko_prevention_choice(True)
                return
            if on_decline:
                on_decline()
            self._resolve_ko_prevention_choice(False)

        choice.callback = callback
        self.pending_choice = choice
        return True

    def _attempt_character_ko(self, target: Card, by_effect: bool = False,
                               attacker: Optional[Card] = None, controller: Optional[Player] = None,
                               after_resolve: Optional[Callable[[str, Player, Optional[Card], Optional[Card]], None]] = None) -> str:
        """Attempt to K.O. a character, honoring hardcoded prevention effects when present."""
        owner = self._find_card_owner(target)
        if owner is None or target not in owner.cards_in_play:
            return "prevented"

        if by_effect and getattr(target, 'cannot_be_ko_by_effects', False):
            self._log(f"{target.name} cannot be K.O.'d by effects")
            if after_resolve:
                after_resolve("prevented", owner, target, attacker)
            return "prevented"

        from .effects.effect_registry import has_hardcoded_effect

        candidates: List[str] = []
        if has_hardcoded_effect(target.id, "on_ko_prevention"):
            candidates.append(target.id)
        for field_card in owner.cards_in_play:
            if field_card is target:
                continue
            if has_hardcoded_effect(field_card.id, "on_ko_prevention"):
                candidates.append(field_card.id)
        if owner.leader and has_hardcoded_effect(owner.leader.id, "on_ko_prevention"):
            candidates.append(owner.leader.id)

        self._pending_ko_context = {
            "target_id": target.id,
            "owner_index": 0 if owner is self.player1 else 1,
            "controller_index": None if controller is None else (0 if controller is self.player1 else 1),
            "attacker_id": getattr(attacker, "id", None),
            "by_effect": by_effect,
            "candidate_index": 0,
            "candidates": candidates,
            "after_resolve": after_resolve,
        }
        return self._continue_character_ko_attempt()

    def next_turn(self):
        """Advance to the next turn."""
        # End phase: check hand limit
        self._end_phase()

        self.turn_count += 1
        self.current_player, self.opponent_player = self.opponent_player, self.current_player

        # Refresh phase
        self.phase = GamePhase.REFRESH
        self.current_player.reset_for_new_turn()

        # Draw phase (P1 doesn't draw on their first turn back)
        # Some leaders have special abilities to draw more than 1 card
        self.phase = GamePhase.DRAW
        if not (self.turn_count == 2 and self.current_player is self.player1):
            # Deck-out check: if deck is empty when a draw is required, game ends
            if not self.current_player.deck:
                if getattr(self.current_player, 'win_on_deck_out', False):
                    # Nami-style: player with empty deck wins
                    self._log(f"{self.current_player.name}'s deck is empty — {self.current_player.name} wins!")
                    self.game_over = True
                    self.winner = self.current_player
                else:
                    # Standard rule: player who can't draw loses
                    self._log(f"{self.current_player.name} cannot draw — {self.opponent_player.name} wins!")
                    self.game_over = True
                    self.winner = self.opponent_player
                self.phase = GamePhase.GAME_OVER
                return
            # Check if leader has a special draw count (e.g., some leaders draw 2)
            draw_count = getattr(self.current_player.leader, 'draw_phase_count', 1)
            for _ in range(draw_count):
                self.current_player.draw_card()

        # DON phase: add 2 DON (max 10)
        # Note: Turn 1 (P1) doesn't call next_turn() - they start directly in Main phase with 1 DON
        # All subsequent turns (including P2's first turn at turn_count=2) gain 2 DON
        self.phase = GamePhase.DON
        current_don = len(self.current_player.don_pool)
        new_don = min(current_don + DON_PER_TURN, MAX_DON)
        additional = new_don - current_don
        self.current_player.don_pool.extend(["active"] * additional)

        # Main phase
        self.phase = GamePhase.MAIN
        self._apply_continuous_effects()
        self._log(f"=== Turn {self.turn_count}: {self.current_player.name} (DON: {len(self.current_player.don_pool)}) ===")

    def _end_phase(self):
        """Handle end of turn cleanup."""
        self.phase = GamePhase.END

        # Fire end_of_turn hardcoded effects for current player's leader and cards
        from .effects.effect_registry import has_hardcoded_effect, execute_hardcoded_effect
        if self.current_player.leader and has_hardcoded_effect(self.current_player.leader.id, "end_of_turn"):
            execute_hardcoded_effect(self, self.current_player, self.current_player.leader, "end_of_turn")
        for card in list(self.current_player.cards_in_play):
            if has_hardcoded_effect(card.id, "end_of_turn"):
                execute_hardcoded_effect(self, self.current_player, card, "end_of_turn")

        # Trash any cards with trash_at_end_of_turn flag (e.g. OP03-005 Thatch)
        for card in list(self.current_player.cards_in_play):
            if getattr(card, 'trash_at_end_of_turn', False):
                self.current_player.cards_in_play.remove(card)
                self.current_player.trash.append(card)
                card.trash_at_end_of_turn = False
                self._log(f"{card.name} is sent to trash at end of turn")

        # If an end-of-turn effect created a pending_choice, keep it for the player to resolve.
        # Only clear truly stale leftover choices from before end_of_turn effects.
        # (Stale choices are already cleared before end_of_turn fires above.)

        # Clear "until end of turn" effects for both players
        self._clear_temporary_effects(self.current_player)
        self._clear_temporary_effects(self.opponent_player)
        self.current_player.cannot_add_life = False
        self.current_player.cannot_add_life_to_hand_this_turn = False
        self.current_player.cannot_attack_opponent_leader = False
        self.opponent_player.cannot_add_life = False
        self.opponent_player.cannot_add_life_to_hand_this_turn = False
        self.opponent_player.cannot_attack_opponent_leader = False

        # Hand limit removed - players can have unlimited cards in hand

    def _apply_continuous_effects(self):
        """Apply continuous/passive effects at the start of the Main phase.

        Called once per turn after clearing. Both players' cards are checked:
        handlers use `game_state.current_player is player` to determine
        whether it's 'Your Turn' or 'Opponent's Turn'.
        """
        from .effects.effect_registry import has_hardcoded_effect, execute_hardcoded_effect
        for player in [self.current_player, self.opponent_player]:
            if player.leader and has_hardcoded_effect(player.leader.id, "continuous"):
                execute_hardcoded_effect(self, player, player.leader, "continuous")
            for card in list(player.cards_in_play):
                if has_hardcoded_effect(card.id, "continuous"):
                    execute_hardcoded_effect(self, player, card, "continuous")

    def _recalc_continuous_effects(self):
        """Clear power_modifiers and reapply continuous effects mid-turn.

        Called after any state change that may change a continuous effect's condition
        (e.g. attaching DON to a leader that has a DON!!-gated continuous effect).

        Preserves one-time (sticky) power modifiers applied by effects like
        -3000 from OP02-013 or +2000-until-next-turn from OP02-004.
        """
        for player in [self.current_player, self.opponent_player]:
            if player.leader and hasattr(player.leader, 'power_modifier'):
                # Preserve sticky (one-time) portion; reset only continuous
                player.leader.power_modifier = getattr(player.leader, '_sticky_power_modifier', 0)
            if player.leader and hasattr(player.leader, 'has_doubleattack'):
                leader_effect_text = player.leader.effect or ''
                leader_has_innate = '[Double Attack]' in leader_effect_text
                leader_has_temp = getattr(player.leader, '_temp_doubleattack', False)
                player.leader.has_doubleattack = leader_has_innate or leader_has_temp
                player.leader.has_double_attack = player.leader.has_doubleattack
            if hasattr(player.leader, 'birdcage_lock'):
                player.leader.birdcage_lock = False
            for card in player.cards_in_play:
                if hasattr(card, 'power_modifier'):
                    card.power_modifier = getattr(card, '_sticky_power_modifier', 0)
                # Reset DON-gated continuous flags so they're re-evaluated
                if hasattr(card, 'can_attack_active'):
                    card.can_attack_active = False
                if hasattr(card, 'has_taunt'):
                    card.has_taunt = False
                if hasattr(card, 'cannot_be_ko_by_strike'):
                    card.cannot_be_ko_by_strike = False
                if hasattr(card, 'cannot_be_ko_in_battle'):
                    card.cannot_be_ko_in_battle = False
                if hasattr(card, 'has_banish'):
                    card.has_banish = getattr(card, '_innate_banish', False)
                if hasattr(card, 'blocker_disabled'):
                    card.blocker_disabled = False
                if hasattr(card, 'birdcage_lock'):
                    card.birdcage_lock = False
                # Reset conditional Rush (continuous effects re-set if conditions met)
                if hasattr(card, 'has_rush') and not getattr(card, '_innate_rush', False):
                    card.has_rush = getattr(card, '_temporary_rush_until_turn', -1) >= self.turn_count
                # Reset conditional Blocker from continuous effects
                if hasattr(card, '_continuous_blocker'):
                    card.has_blocker = False
                    card._continuous_blocker = False
                if hasattr(card, 'has_doubleattack'):
                    # Reset to False; continuous effects will re-set if conditions met.
                    # Cards with innate Double Attack get it re-applied via _apply_keywords-style check below.
                    import re as _re
                    effect_text = card.effect or ''
                    has_innate = ('[Double Attack]' in effect_text
                                  and not _re.search(r'gains?\s+\[Double Attack\]', effect_text, _re.IGNORECASE))
                    has_temp = getattr(card, '_temp_doubleattack', False)
                    card.has_doubleattack = has_innate or has_temp
                    card.has_double_attack = card.has_doubleattack
            # Clear cost_modifier on cards in play (e.g. Issho OP03-078 -3 cost)
            for card in player.cards_in_play:
                if hasattr(card, 'cost_modifier'):
                    card.cost_modifier = 0
            # Clear hand cost modifiers (e.g. Crocodile -1 cost for blue events)
            for card in player.hand:
                if hasattr(card, 'cost_modifier'):
                    card.cost_modifier = 0
        self._apply_continuous_effects()

    def _clear_temporary_effects(self, player: Player):
        """Clear temporary effects that expire at end of turn."""
        # Clear leader temporary effects
        if player.leader:
            if hasattr(player.leader, 'power_modifier'):
                expire_turn = getattr(player.leader, 'power_modifier_expires_on_turn', -1)
                if expire_turn < 0 or self.turn_count >= expire_turn:
                    player.leader.power_modifier = 0
                    player.leader._sticky_power_modifier = 0
                    if hasattr(player.leader, 'power_modifier_expires_on_turn'):
                        del player.leader.power_modifier_expires_on_turn
                    if hasattr(player.leader, '_sticky_power_modifier_expires_on_turn'):
                        del player.leader._sticky_power_modifier_expires_on_turn
            if hasattr(player.leader, 'cannot_attack') and player.leader.cannot_attack:
                expire = getattr(player.leader, 'cannot_attack_until_turn', -1)
                if expire < 0 or self.turn_count >= expire:
                    player.leader.cannot_attack = False
                    if hasattr(player.leader, 'cannot_attack_until_turn'):
                        del player.leader.cannot_attack_until_turn
            # Clear temporary double attack granted to leader (e.g. OP03-016 Flame Emperor)
            if getattr(player.leader, '_temp_doubleattack', False):
                player.leader.has_doubleattack = False
                player.leader.has_double_attack = False
                player.leader._temp_doubleattack = False

        # Clear character temporary effects
        for card in player.cards_in_play:
            if hasattr(card, 'power_modifier'):
                expire_turn = getattr(card, 'power_modifier_expires_on_turn', -1)
                if expire_turn < 0 or self.turn_count >= expire_turn:
                    card.power_modifier = 0
                    card._sticky_power_modifier = 0
                    if hasattr(card, 'power_modifier_expires_on_turn'):
                        del card.power_modifier_expires_on_turn
                    if hasattr(card, '_sticky_power_modifier_expires_on_turn'):
                        del card._sticky_power_modifier_expires_on_turn
            if hasattr(card, 'cannot_attack') and card.cannot_attack:
                expire = getattr(card, 'cannot_attack_until_turn', -1)
                if expire < 0 or self.turn_count >= expire:
                    card.cannot_attack = False
                    if hasattr(card, 'cannot_attack_until_turn'):
                        del card.cannot_attack_until_turn
            if hasattr(card, 'cannot_be_rested'):
                card.cannot_be_rested = False
            if hasattr(card, 'cost_modifier'):
                card.cost_modifier = 0
            if hasattr(card, 'can_attack_active'):
                card.can_attack_active = False
            if hasattr(card, 'has_taunt'):
                card.has_taunt = False
            if hasattr(card, 'has_banish'):
                card.has_banish = getattr(card, '_innate_banish', False)
            if hasattr(card, 'blocker_disabled'):
                card.blocker_disabled = False
            if hasattr(card, '_temporary_rush_until_turn') and card._temporary_rush_until_turn < self.turn_count:
                card.has_rush = False
            if getattr(card, '_temp_doubleattack', False):
                card.has_doubleattack = False
                card.has_double_attack = False
                card._temp_doubleattack = False
        # Clear cost_modifier on hand cards (e.g. Crocodile -1 cost for blue events)
        for card in player.hand:
            if hasattr(card, 'cost_modifier'):
                card.cost_modifier = 0

    def can_attack_with_leader(self) -> bool:
        """Check if the current player's leader can attack."""
        if self.current_player is self.player1:
            return self.turn_count >= 3
        return self.turn_count >= 4

    def get_valid_attack_targets(self) -> List[Tuple[int, Card]]:
        """
        Get valid attack targets for the current player.

        Valid targets:
        - Opponent's Leader (always, unless taunt)
        - Opponent's rested Characters

        Returns:
            List of (index, card) tuples. Index -1 means leader.
        """
        # Check for taunt: if opponent has a character with has_taunt, only that card can be attacked
        taunt_cards = [(i, c) for i, c in enumerate(self.opponent_player.cards_in_play)
                       if getattr(c, 'has_taunt', False)]
        if taunt_cards:
            return taunt_cards

        targets = []

        # Leader is always a valid target
        targets.append((-1, self.opponent_player.leader))

        # Rested characters are valid targets (Stage cards cannot be targeted)
        for i, card in enumerate(self.opponent_player.cards_in_play):
            if card.is_resting and getattr(card, 'card_type', '') != 'STAGE':
                targets.append((i, card))

        return targets

    def choose_card_to_play(self) -> Card | None:
        """AI logic to choose a card to play."""
        for c in self.current_player.hand:
            # Skip leaders in hand (shouldn't happen)
            if c.card_type == 'LEADER':
                continue
            # Skip Counter EVENT cards - they can only be played during counter step
            if c.card_type == 'EVENT' and c.effect and '[Counter]' in c.effect:
                continue
            # Check if we can afford it
            if c.cost is not None and c.cost <= self.available_don():
                return c
        return None

    def available_don(self) -> int:
        """Get available DON for the current player."""
        return self.current_player.don_pool.count("active")

    def _apply_keywords(self, card: Card):
        """Apply keyword effects from a card's effect text."""
        if not card.effect:
            return

        lines = []
        for raw in re.sub(r'<br\s*/?>', '\n', card.effect, flags=re.IGNORECASE).splitlines():
            line = raw.strip()
            if line:
                lines.append(line)
        for line in lines:
            if line.startswith('[Rush]'):
                card.has_rush = True
                card._innate_rush = True
            elif line.startswith('[Blocker]'):
                card.has_blocker = True
                card._innate_blocker = True
            elif line.startswith('[Banish]'):
                card.has_banish = True
                card._innate_banish = True
            elif line.startswith('[Double Attack]'):
                card.has_doubleattack = True
                card._innate_doubleattack = True

    def _trigger_on_play_effects(self, card: Card, player: Optional[Player] = None):
        """Trigger On Play effects for a card using the effect system."""
        print(f"[DEBUG] _trigger_on_play_effects: {card.id} - {card.name}")

        effect_player = player or self._find_card_owner(card) or self.current_player
        previous_current = self.current_player
        previous_opponent = self.opponent_player
        if effect_player is self.player1:
            effect_opponent = self.player2
        elif effect_player is self.player2:
            effect_opponent = self.player1
        else:
            effect_opponent = self.opponent_player

        self.current_player = effect_player
        self.opponent_player = effect_opponent
        try:
            # First try hardcoded handlers (for cards with complex effects)
            executed = trigger_effect(card.id, self, card)
            print(f"[DEBUG] Hardcoded executed: {executed}")

            # ONLY parse and resolve effects if hardcoded handler didn't execute
            # This prevents duplicate execution (e.g., "Draw 2" happening twice)
            if not executed and card.effect:
                print(f"[DEBUG] Running parser for {card.id}")
                effects = parse_effect(card.effect)
                for effect in effects:
                    if effect.timing == EffectTiming.ON_PLAY:
                        print(f"[DEBUG] Parsed effect: {effect.effect_type}, timing: {effect.timing}")
                        # Create context and resolve
                        context = EffectContext(
                            game_state=self,
                            source_card=card,
                            source_player=effect_player,
                            opponent=effect_opponent,
                        )
                        resolver = get_resolver()
                        if resolver.can_resolve(effect, context):
                            result = resolver.resolve(effect, context)
                            print(f"[DEBUG] Resolved effect: {result.success}, {result.message}")
                            if result.success and result.message:
                                self._log(f"  [EFFECT] {result.message}")
            else:
                print(f"[DEBUG] Skipping parser - hardcoded already executed")
        finally:
            self.current_player = previous_current
            self.opponent_player = previous_opponent

    def play_card_to_field_by_effect(
        self,
        player: Player,
        card: Card,
        *,
        rest_on_play: Optional[bool] = None,
        trigger_on_play: bool = True,
        log_message: Optional[str] = None,
    ) -> None:
        """Put a card into play from an effect and run play-time hooks."""
        if rest_on_play is not None:
            card.is_resting = rest_on_play
        if not any(in_play is card for in_play in player.cards_in_play):
            player.cards_in_play.append(card)
        setattr(card, 'played_turn', self.turn_count)
        card_type = str(getattr(card, "card_type", "")).upper()
        if card_type == "CHARACTER":
            self.last_played_character = card
        self._apply_keywords(card)
        if log_message:
            self._log(log_message)
        if trigger_on_play:
            self._trigger_on_play_effects(card, player=player)
            from .effects.effect_registry import has_hardcoded_effect, execute_hardcoded_effect
            if (
                card_type == "CHARACTER"
                and player.leader
                and has_hardcoded_effect(player.leader.id, 'on_play_character')
            ):
                execute_hardcoded_effect(self, player, player.leader, 'on_play_character')

    def play_card(self, card: Card):
        """Play a card from hand."""
        cost = max(0, (card.cost or 0) + getattr(card, 'cost_modifier', 0))
        available = self.available_don()
        print(f"[DEBUG] play_card: {card.name}, cost={cost}, available_don={available}, don_pool={self.current_player.don_pool}")

        # Check field limit (max 5 characters) — prompt to replace if full
        if card.card_type == "CHARACTER":
            char_count = sum(1 for c in self.current_player.cards_in_play if c.card_type == "CHARACTER")
            if char_count >= 5:
                # Must also be able to afford the card
                if cost > available:
                    self._log(f"Cannot play {card.name}: needs {cost} DON, has {available}.")
                    return False
                # Prompt player to choose which character to trash to make room
                options = []
                for i, c in enumerate(self.current_player.cards_in_play):
                    if c.card_type == "CHARACTER":
                        options.append({
                            "id": str(i),
                            "label": f"{c.name} (Cost {c.cost or 0}, Power {c.power or 0})",
                            "card_id": c.id,
                            "card_name": c.name,
                        })
                self.pending_choice = PendingChoice(
                    choice_id=f"replace_field_{uuid.uuid4().hex[:8]}",
                    choice_type="select_target",
                    prompt=f"Field is full. Choose a character to trash to play {card.name}.",
                    options=options,
                    min_selections=1,
                    max_selections=1,
                    source_card_id=card.id,
                    source_card_name=card.name,
                    callback_action="replace_field_card",
                    callback_data={
                        "player_id": self.current_player.player_id,
                        "card_to_play_id": card.id,
                    }
                )
                return True  # Choice created; will resolve via resolve_pending_choice

        if cost <= available:
            # Spend DON — guard against cost=0 (e.g. Crocodile OP01-067 -1 modifier reducing
            # an event to 0): without the guard the loop never breaks and rests ALL active DON.
            used = 0
            for i in range(len(self.current_player.don_pool)):
                if used >= cost:
                    break
                if self.current_player.don_pool[i] == "active":
                    self.current_player.don_pool[i] = "rested"
                    used += 1

            # Remove from hand
            if card in self.current_player.hand:
                self.current_player.hand.remove(card)

            # EVENT cards go directly to trash after resolving
            if card.card_type == "EVENT":
                self.current_player.trash.append(card)
                self._log(f"{self.current_player.name} plays {card.name} (Event, Cost {cost}), Remaining Active DON: {self.available_don()}")
                # Trigger effect
                self._trigger_on_play_effects(card)
                # Fire on_event triggers (e.g. Crocodile leader: draw 1 when you activate Event)
                from .effects.effect_registry import has_hardcoded_effect, execute_hardcoded_effect
                if self.current_player.leader and has_hardcoded_effect(self.current_player.leader.id, 'on_event'):
                    execute_hardcoded_effect(self, self.current_player, self.current_player.leader, 'on_event')
                # Fire on_opponent_event for cards on the opposing player's field (e.g. Gion OP06-044, Zeff OP06-048)
                for opp_card in list(self.opponent_player.cards_in_play):
                    if has_hardcoded_effect(opp_card.id, 'on_opponent_event'):
                        execute_hardcoded_effect(self, self.opponent_player, opp_card, 'on_opponent_event')
            else:
                # CHARACTER and STAGE cards go to field
                self.play_card_to_field_by_effect(
                    self.current_player,
                    card,
                    log_message=f"{self.current_player.name} plays {card.name} (Cost {cost}), Remaining Active DON: {self.available_don()}",
                )
        else:
            self._log(f"Cannot play {card.name}: needs {cost} DON, has {self.available_don()}.")
            return False
        # Recalculate continuous effects (hand size changed, DON changed, etc.)
        self._recalc_continuous_effects()
        return True

    def play_card_by_index(self, card_index: int) -> bool:
        """Play a card from hand by index. Used by socket handlers."""
        print(f"[DEBUG] play_card_by_index: index={card_index}, hand_size={len(self.current_player.hand)}")
        if card_index < 0 or card_index >= len(self.current_player.hand):
            print(f"[DEBUG] Invalid card index")
            return False
        card = self.current_player.hand[card_index]
        print(f"[DEBUG] Playing card: {card.name}, cost={card.cost}, available_don={self.available_don()}")
        return self.play_card(card)

    def declare_attack(self, attacker_index: int, target_index: int) -> bool:
        """Declare an attack. Used by socket handlers.

        Args:
            attacker_index: -1 for leader, 0+ for field card index
            target_index: -1 for leader, 0+ for field card index
        """
        # Cannot declare a new attack while one is already in progress
        if self.pending_attack:
            self._log("Cannot declare a new attack while one is in progress.")
            return False

        # Get attacker
        if attacker_index == -1:
            attacker = self.current_player.leader
        elif 0 <= attacker_index < len(self.current_player.cards_in_play):
            attacker = self.current_player.cards_in_play[attacker_index]
        else:
            return False

        # Check if can attack
        if getattr(attacker, 'is_resting', False):
            self._log(f"{attacker.name} is rested and cannot attack.")
            return False
        if getattr(attacker, 'has_attacked', False):
            self._log(f"{attacker.name} has already attacked this turn.")
            return False
        if getattr(attacker, 'cannot_attack', False):
            self._log(f"{attacker.name} cannot attack (effect active).")
            return False

        # For leader, check turn restriction
        if attacker_index == -1 and not self.can_attack_with_leader():
            self._log(f"Leader cannot attack yet.")
            return False

        # For characters without Rush, check if played this turn
        if attacker_index >= 0:
            played_turn = getattr(attacker, 'played_turn', 0)
            has_rush = getattr(attacker, 'has_rush', False)
            if played_turn == self.turn_count and not has_rush:
                self._log(f"{attacker.name} was just played and doesn't have Rush.")
                return False

        self.attack_with_card(attacker, target_index)
        return True

    def respond_leader_effect(self, use_effect: bool) -> bool:
        """Respond to the leader effect step (use or decline the leader's combat ability).

        Args:
            use_effect: True to activate the defending leader's on_opponent_attack effect
        """
        if not self.pending_attack or self.awaiting_response != "leader_effect":
            return False

        attack = self.pending_attack
        o = attack['defender_player']
        p = attack['attacker_player']
        attacker = attack['attacker']
        defender = attack['current_target']

        if use_effect and o.leader and attack.get('leader_has_effect'):
            effect_manager = get_effect_manager()
            results = effect_manager.on_opponent_attack(self, p, o, attacker, defender)
            for result in results:
                if result.success and result.message:
                    self._log(f"  [LEADER EFFECT] {result.message}")
        else:
            self._log("  [LEADER EFFECT] Declined.")

        # Advance to blocker step
        self.phase = GamePhase.BLOCKER_STEP
        self.awaiting_response = "blocker"
        return True

    def respond_blocker(self, blocker_index: Optional[int]) -> bool:
        """Respond with a blocker or pass. Used by socket handlers.

        Args:
            blocker_index: Index of character to block with, or None to pass
        """
        if not self.pending_attack or self.awaiting_response != "blocker":
            return False

        attack = self.pending_attack
        defender_player = attack['defender_player']

        if blocker_index is not None:
            # Validate blocker
            if blocker_index < 0 or blocker_index >= len(defender_player.cards_in_play):
                return False

            blocker = defender_player.cards_in_play[blocker_index]

            # Check if blocker is valid (use same logic as _can_block)
            if not defender_player._can_block(blocker):
                return False
            # Check blocker_power_minimum (e.g. Shanks prevents blockers ≤2000)
            bpm = getattr(self, 'blocker_power_minimum', 0)
            if bpm and (blocker.power or 0) + getattr(blocker, 'power_modifier', 0) < bpm:
                self._log(f"{blocker.name} cannot block (power too low).")
                return False
            # Check blocker_cost_limit (e.g. OP02-061 Morley: cost 5 or less can't block)
            bcl = getattr(self, 'blocker_cost_limit', None)
            if bcl is not None and (getattr(blocker, 'cost', 0) or 0) <= bcl:
                self._log(f"{blocker.name} cannot block (cost {blocker.cost} ≤ {bcl}).")
                return False

            # Redirect attack to blocker
            attack['current_target'] = blocker
            attack['current_target_index'] = blocker_index
            blocker.is_resting = True  # Blocker becomes rested
            self._log(f"  [BLOCKER] {blocker.name} intercepts the attack!")

            # Trigger [On Block] effects
            from .effects.effect_registry import has_hardcoded_effect, execute_hardcoded_effect
            if has_hardcoded_effect(blocker.id, 'on_block'):
                execute_hardcoded_effect(self, defender_player, blocker, 'on_block')

        # Move to counter step
        self.phase = GamePhase.COUNTER_STEP
        self.awaiting_response = "counter"
        return True

    def respond_counter(self, counter_indices: List[int]) -> bool:
        """Use counter cards or pass. Used by socket handlers.

        Args:
            counter_indices: List of hand indices for counter cards to use
        """
        if not self.pending_attack or self.awaiting_response != "counter":
            return False

        attack = self.pending_attack
        defender_player = attack['defender_player']
        total_counter = 0

        # Sort indices in reverse to remove from end first
        for idx in sorted(counter_indices, reverse=True):
            if idx < 0 or idx >= len(defender_player.hand):
                continue

            card = defender_player.hand[idx]

            # Check for counter value on character cards (free to use, card goes to trash)
            counter_value = getattr(card, 'counter', None)
            if counter_value and counter_value > 0 and card.card_type != 'EVENT':
                total_counter += counter_value
                attack['counters_used'].append((card, counter_value, False))
                self._log(f"  [COUNTER] {defender_player.name} uses {card.name} (+{counter_value})")
                # Character counter cards go to trash after use
                defender_player.hand.remove(card)
                defender_player.trash.append(card)
                continue

            # Check for counter events (require DON)
            if card.card_type == 'EVENT' and card.effect and '[Counter]' in card.effect:
                cost = max(0, (card.cost or 0) + getattr(card, 'cost_modifier', 0))
                active_don = sum(1 for d in defender_player.don_pool if d == "active")
                if active_don < cost:
                    self._log(f"  [COUNTER] Not enough DON for {card.name} (needs {cost}, have {active_don})")
                    continue
                if active_don >= cost:
                    # Spend DON
                    spent = 0
                    for i, d in enumerate(defender_player.don_pool):
                        if d == "active" and spent < cost:
                            defender_player.don_pool[i] = "rested"
                            spent += 1

                    # Move event to trash
                    defender_player.hand.remove(card)
                    defender_player.trash.append(card)

                    # Fire on_event_activated for attacker's cards (e.g. Usopp OP01-004)
                    attacker_player = attack.get('attacker_player')
                    if attacker_player:
                        effect_manager = get_effect_manager()
                        effect_manager.on_opponent_event_play(self, attacker_player, card)
                        from .effects.effect_registry import has_hardcoded_effect as _has_opp_event, execute_hardcoded_effect as _exec_opp_event
                        for opp_event_card in list(attacker_player.cards_in_play):
                            if _has_opp_event(opp_event_card.id, 'on_opponent_event'):
                                _exec_opp_event(self, attacker_player, opp_event_card, 'on_opponent_event')

                    # Fire on_event for defender's leader (e.g. Crocodile OP01-062: draw 1 when you activate Event)
                    from .effects.effect_registry import has_hardcoded_effect as _has_he, execute_hardcoded_effect as _exec_he
                    if defender_player.leader and _has_he(defender_player.leader.id, 'on_event'):
                        _exec_he(self, defender_player, defender_player.leader, 'on_event')

                    # Check if card has a hardcoded counter effect
                    from .effects.effect_registry import has_hardcoded_effect
                    has_hardcoded = has_hardcoded_effect(card.id, 'counter')

                    if has_hardcoded:
                        # Hardcoded effect handles ALL power changes via power_modifier.
                        # Don't also add parsed counter value to avoid double-counting.
                        attack['counters_used'].append((card, 0, True))
                        self._log(f"  [COUNTER EVENT] {defender_player.name} plays {card.name} (Cost {cost} DON)")
                        if 'counter_events_with_effects' not in attack:
                            attack['counter_events_with_effects'] = []
                        attack['counter_events_with_effects'].append(card)
                    else:
                        # No hardcoded effect — use parsed counter value
                        counter_value = self._parse_counter_value(card)
                        total_counter += counter_value
                        attack['counters_used'].append((card, counter_value, True))
                        self._log(f"  [COUNTER EVENT] {defender_player.name} plays {card.name} (Cost {cost} DON, +{counter_value})")

        attack['counter_power'] = total_counter

        # Trigger counter event hardcoded effects BEFORE attack resolution
        # so power mods (-2000, +4000) affect the combat outcome.
        counter_effect_cards = attack.get('counter_events_with_effects', [])
        if counter_effect_cards:
            self._trigger_pre_resolution_counter_effects(defender_player, counter_effect_cards)
            if self.pending_choice:
                # A counter effect needs player input (target selection for power mod).
                # Attack resolution is deferred until the choice is resolved.
                attack['_needs_attack_resolution'] = True
                return True

        # Resolve the attack damage
        self._resolve_attack_damage()

        return True

    def _trigger_pre_resolution_counter_effects(self, defender_player, counter_event_cards):
        """Trigger hardcoded counter event effects BEFORE attack resolution.

        Counter events like Rafflesia (-2000 to attacker) and Radical Beam (+4000)
        modify power and must resolve before the damage comparison.
        Effects that need PendingChoice (target selection) pause here;
        attack resolution resumes after the choice via _needs_attack_resolution flag.
        """
        from .effects.effect_registry import execute_hardcoded_effect
        for card in counter_event_cards:
            if self.pending_choice:
                if not hasattr(self, '_queued_counter_effects'):
                    self._queued_counter_effects = []
                self._queued_counter_effects.append((defender_player, card))
                continue
            execute_hardcoded_effect(self, defender_player, card, 'counter')

    def attach_don(self, card_index: int, amount: int = 1) -> bool:
        """Attach DON to a card. Used by socket handlers.

        Args:
            card_index: -1 for leader, 0+ for field card index
            amount: Number of DON to attach
        """
        # Get target card
        if card_index == -1:
            target = self.current_player.leader
        elif 0 <= card_index < len(self.current_player.cards_in_play):
            target = self.current_player.cards_in_play[card_index]
        else:
            return False

        # Check if we have enough active DON
        active_don = self.current_player.don_pool.count("active")
        if active_don < amount:
            return False

        # Attach DON
        attached = self.current_player.assign_don_to_card(target, amount)
        if attached > 0:
            self._log(f"{self.current_player.name} attaches {attached} DON to {target.name}.")
            # DON count changed — recheck continuous effects (e.g. Zoro: DON!!x1 grants +1000)
            self._recalc_continuous_effects()
            # Fire on_don_attached effects for leader (e.g. Garp OP02-002)
            from .effects.effect_registry import has_hardcoded_effect, execute_hardcoded_effect
            if self.current_player.leader and has_hardcoded_effect(self.current_player.leader.id, "on_don_attached"):
                execute_hardcoded_effect(self, self.current_player, self.current_player.leader, "on_don_attached")
            return True
        return False

    def start_game(self):
        """Start the game after mulligan phase. Used by socket handlers."""
        # Game is already initialized in __init__, this is just a signal
        self._log("Both players ready. Game starting!")

    def activate_main_effect(self, card_index: int) -> bool:
        """Activate a card's [Activate: Main] effect. Used by socket handlers.
        card_index == -1 means the leader card.
        """
        if card_index == -1:
            card = self.current_player.leader
        elif 0 <= card_index < len(self.current_player.cards_in_play):
            card = self.current_player.cards_in_play[card_index]
        else:
            return False

        if not card:
            return False

        # Hardcoded activate handlers are authoritative for cards that define them.
        from .effects.effect_registry import has_hardcoded_effect
        from .handlers.effect_handlers import trigger_effect
        if has_hardcoded_effect(card.id, "activate"):
            return bool(trigger_effect(card.id, self, card, timing="activate"))
        result = trigger_effect(card.id, self, card, timing="activate")
        if result:
            return True

        if not card.effect or '[Activate: Main]' not in card.effect:
            return False

        # Fall back to parser-based activation (for non-hardcoded cards)
        from .effects.manager import get_effect_manager
        effect_manager = get_effect_manager()
        results = effect_manager.activate_main(self, self.current_player, card)
        return any(r.success for r in results)

    def _try_activate_main_effects(self) -> bool:
        """
        Try to activate [Activate: Main] effects on cards in play.

        Returns True if any effect was activated, False otherwise.
        """
        activated_any = False

        # Check all cards in play for Activate: Main effects
        for card in list(self.current_player.cards_in_play):
            if not card.effect or '[Activate: Main]' not in card.effect:
                continue

            # Check once-per-turn restriction
            already_activated = getattr(card, 'main_activated_this_turn', False)
            if already_activated:
                continue

            # Parse the effects
            effects = parse_effect(card.effect)
            for effect in effects:
                if effect.timing != EffectTiming.MAIN:
                    continue

                # Create context
                context = EffectContext(
                    game_state=self,
                    source_card=card,
                    source_player=self.current_player,
                    opponent=self.opponent_player,
                )

                # Check if we can pay the cost and resolve
                resolver = get_resolver()
                if resolver.can_resolve(effect, context):
                    result = resolver.resolve(effect, context)
                    if result.success:
                        self._log(f"  [ACTIVATE] {card.name}: {result.message}")
                        # Mark as activated this turn (for once-per-turn effects)
                        if effect.once_per_turn:
                            card.main_activated_this_turn = True
                        activated_any = True

        return activated_any

    def assign_don_to_attackers(self):
        """Record DON assignments for power calculation."""
        for card in self.current_player.cards_in_play:
            if not card.is_resting:
                self.card_don_assignments[card] = getattr(card, 'attached_don', 0)
        # Also record leader's DON
        self.card_don_assignments[self.current_player.leader] = getattr(
            self.current_player.leader, 'attached_don', 0
        )

    def attack_with_card(self, attacker: Card, target_index: int = -1):
        """
        Initiate an attack. Sets up pending_attack and waits for blocker response.

        Args:
            attacker: The attacking card
            target_index: Target index (-1 for leader, >= 0 for character)
        """
        p, o = self.current_player, self.opponent_player

        # Stage cards cannot attack
        if getattr(attacker, 'card_type', '') == 'STAGE':
            self._log(f"Stage cards cannot attack.")
            return

        # Validate attacker can attack
        if attacker.card_type == 'CHARACTER':
            if not getattr(attacker, 'has_rush', False):
                if getattr(attacker, 'played_turn', None) == self.turn_count:
                    self._log(f"{attacker.name} can't attack on the turn it was played.")
                    return

        if attacker.card_type == 'LEADER' and not self.can_attack_with_leader():
            req = 3 if p is self.player1 else 4
            self._log(f"{p.name}'s leader cannot attack until turn {req}.")
            return

        if attacker.is_resting:
            self._log(f"{attacker.name} is resting; cannot attack.")
            return

        # Get target
        if target_index == -1:
            defender = o.leader
        else:
            if target_index >= len(o.cards_in_play):
                defender = o.leader
                target_index = -1
            else:
                defender = o.cards_in_play[target_index]
                # Validate target is rested (can only attack rested characters)
                # Exception: attacker with can_attack_active may target active characters
                if not defender.is_resting and not getattr(attacker, 'can_attack_active', False):
                    self._log(f"Cannot attack {defender.name} - only rested characters can be attacked.")
                    return

        # Block attacking the leader on the turn the card was played (e.g. OP03-004 Curiel)
        if target_index == -1 and getattr(attacker, 'cannot_attack_leader_on_play_turn', False):
            if getattr(attacker, 'played_turn', None) == self.turn_count:
                self._log(f"{attacker.name} cannot attack the Leader on the turn it was played.")
                return

        # Block attacking opponent's leader when player has the restriction (e.g. OP06-026 Koushirou)
        if target_index == -1 and getattr(p, 'cannot_attack_opponent_leader', False):
            self._log(f"Cannot attack opponent's Leader this turn (effect restriction).")
            return

        # Enforce taunt: if opponent has a character with has_taunt, must attack that character
        taunt_cards = [c for c in o.cards_in_play if getattr(c, 'has_taunt', False)]
        if taunt_cards:
            if defender not in taunt_cards:
                taunt_names = ', '.join(c.name for c in taunt_cards)
                self._log(f"Must attack {taunt_names} (taunt effect active).")
                return

        # Rest attacker immediately on declaration (so triggers can target it as rested)
        attacker.is_resting = True
        # Recalc continuous effects now that attacker is rested (e.g. Ashura Doji +2000)
        self._recalc_continuous_effects()

        # Calculate attacker power (base + DON + power_modifier from effects)
        don = self.card_don_assignments.get(attacker, getattr(attacker, 'attached_don', 0))
        attacker_power = (attacker.power or 0) + don * 1000 + getattr(attacker, 'power_modifier', 0)

        self._log(f"{p.name}'s {attacker.name} (Power: {attacker_power}) attacks {defender.name}!")

        # Trigger [When Attacking] effects on the attacker's side
        effect_manager = get_effect_manager()
        attack_effects = effect_manager.on_attack_declare(self, p, attacker, defender)
        for result in attack_effects:
            if result.success and result.message:
                self._log(f"  [WHEN ATTACKING] {result.message}")
        attacker_power = (attacker.power or 0) + don * 1000 + getattr(attacker, 'power_modifier', 0)

        # Check if defending leader has an [On Opponent's Attack] / leader effect
        # (fires interactively during LEADER_EFFECT_STEP before blockers)
        from .effects.effect_registry import has_hardcoded_effect as _has_hce
        leader_has_effect = bool(
            (o.leader and _has_hce(o.leader.id, 'on_opponent_attack'))
            or any(_has_hce(c.id, 'on_opponent_attack') for c in o.cards_in_play)
        )

        # Get available blockers for defender
        available_blockers = o.get_available_blockers()
        # Filter by blocker_power_minimum (e.g. Shanks prevents blockers ≤2000)
        bpm = getattr(self, 'blocker_power_minimum', 0)
        if bpm:
            available_blockers = [(i, b) for i, b in available_blockers
                                  if (b.power or 0) + getattr(b, 'power_modifier', 0) > bpm - 1]
        # Filter by blocker_cost_limit (e.g. OP02-061 Morley: cost 5 or less can't block)
        bcl = getattr(self, 'blocker_cost_limit', None)
        if bcl is not None:
            available_blockers = [(i, b) for i, b in available_blockers
                                  if (getattr(b, 'cost', 0) or 0) > bcl]
        print(f"[DEBUG BLOCKER] Defender={o.name}, cards_in_play={len(o.cards_in_play)}")
        for ci, cc in enumerate(o.cards_in_play):
            can_blk = o._can_block(cc)
            print(f"  [{ci}] {cc.name} resting={cc.is_resting} has_blocker={getattr(cc, 'has_blocker', 'N/A')} is_blocker={getattr(cc, 'is_blocker', 'N/A')} can_block={can_blk}")
        print(f"[DEBUG BLOCKER] available_blockers tuples: {[(i, b.name) for i, b in available_blockers]}")

        # Get available counter cards for defender
        available_counters = self._get_available_counters(o)

        # Store pending attack state
        attacker_index = -1 if attacker == p.leader else p.cards_in_play.index(attacker) if attacker in p.cards_in_play else -1
        self.pending_attack = {
            'attacker': attacker,
            'attacker_index': attacker_index,
            'attacker_name': attacker.name,
            'attacker_power': attacker_power,
            'original_target': defender,
            'original_target_index': target_index,
            'current_target': defender,
            'current_target_index': target_index,
            'defender_player': o,
            'attacker_player': p,
            'available_blockers': [
                {'index': i, 'name': b.name, 'power': (b.power or 0) + getattr(b, 'power_modifier', 0)}
                for i, b in available_blockers
            ],
            'available_counters': available_counters,
            'counter_power': 0,
            'counters_used': [],
            'leader_has_effect': leader_has_effect,
        }

        # Enter leader effect step if defender's leader has a combat ability;
        # otherwise skip straight to the blocker step.
        if leader_has_effect:
            self.phase = GamePhase.LEADER_EFFECT_STEP
            self.awaiting_response = "leader_effect"
        else:
            self.phase = GamePhase.BLOCKER_STEP
            self.awaiting_response = "blocker"
        # Attack flow pauses here - will continue when respond_leader_effect() or
        # respond_blocker() is called.

    def _get_available_counters(self, player: Player) -> List[Dict]:
        """Get available counter cards for a player."""
        counters = []
        for i, card in enumerate(player.hand):
            # Check for counter value on character cards
            counter_value = getattr(card, 'counter', None)
            if counter_value and counter_value > 0:
                counters.append({
                    'index': i,
                    'name': card.name,
                    'counter_value': counter_value,
                    'cost': 0,  # Character counter values are free
                    'is_event': False,
                })
            # Check for counter events
            elif card.card_type == 'EVENT' and card.effect and '[Counter]' in card.effect:
                counters.append({
                    'index': i,
                    'name': card.name,
                    'counter_value': self._parse_counter_value(card),
                    'cost': card.cost or 0,
                    'is_event': True,
                })
        return counters

    def _parse_counter_value(self, card: Card) -> int:
        """Parse counter value from event card effect text."""
        import re
        effect = card.effect or ''
        # Look for patterns like "+4000 power" or "gains +2000 power"
        match = re.search(r'\+(\d+)\s*power', effect, re.IGNORECASE)
        if match:
            return int(match.group(1))
        # Fallback: bare "+4000" (not preceded by minus context)
        match = re.search(r'gains?\s*\+(\d+)', effect, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 0

    def _resolve_attack_damage(self):
        """Resolve damage after blocker and counter steps."""
        if not self.pending_attack:
            return

        attack = self.pending_attack
        attacker = attack['attacker']
        defender = attack['current_target']
        counter_power = attack['counter_power']
        p = attack['attacker_player']
        o = attack['defender_player']

        # Re-calculate attacker power at resolution time so counter effects
        # (e.g. Rafflesia -2000 applied to attacker's power_modifier) are included.
        don = self.card_don_assignments.get(attacker, getattr(attacker, 'attached_don', 0))
        attacker_power = (attacker.power or 0) + don * 1000 + getattr(attacker, 'power_modifier', 0)

        # Calculate total defense (base + counter + power_modifier from effects)
        # DON only gives power on the card owner's turn — defender is being
        # attacked during the attacker's turn, so defender's DON does NOT
        # add power here.
        defender_power = (defender.power or 0) + counter_power + getattr(defender, 'power_modifier', 0)
        total_defense = defender_power

        self.phase = GamePhase.DAMAGE_STEP
        self._log(f"  [DAMAGE] {attacker.name} ({attacker_power}) vs {defender.name} ({total_defense})")

        if attacker_power >= total_defense:
            if defender.card_type == 'LEADER':
                # Check for Banish
                has_banish = getattr(attacker, 'has_banish', False)
                if not has_banish and attacker.effect:
                    has_banish = '[Banish]' in attacker.effect

                # Take life damage
                life_card, has_trigger = o.take_life_damage()

                # Trigger on_damage_dealt effects for the attacker (e.g. OP03-041 Usopp, OP03-043 Gaimon, OP03-051 Bell-mère)
                if life_card is not None:
                    from .effects.effect_registry import has_hardcoded_effect, execute_hardcoded_effect
                    if has_hardcoded_effect(attacker.id, 'on_damage_dealt'):
                        execute_hardcoded_effect(self, p, attacker, 'on_damage_dealt')
                    # Also check all of the attacker's player's field cards for leader-side on_damage_dealt
                    if p.leader and has_hardcoded_effect(p.leader.id, 'on_damage_dealt') and attacker == p.leader:
                        execute_hardcoded_effect(self, p, p.leader, 'on_damage_dealt')
                    # Fire on_damage_dealt for all field characters with the flag (Gaimon-style global trigger)
                    for fc in list(p.cards_in_play):
                        if fc != attacker and has_hardcoded_effect(fc.id, 'on_damage_dealt'):
                            execute_hardcoded_effect(self, p, fc, 'on_damage_dealt')

                # Game over only when a player at 0 life takes ANOTHER hit
                # (take_life_damage returns None when life_cards was already empty)
                if life_card is None:
                    self._log(f"{o.name} has no life remaining — {p.name} wins!")
                    self.game_over = True
                    self.winner = p
                    self.phase = GamePhase.GAME_OVER
                    self._finish_attack()
                    return

                # Check for Double Attack (need to know if there's a second hit coming)
                has_double_attack = getattr(attacker, 'has_doubleattack', False)

                # Store double attack info in pending_attack for later
                attack['has_double_attack'] = has_double_attack
                attack['double_attack_processed'] = False
                attack['has_banish'] = has_banish

                # Fire on_life_zero for defender leader when life drops to 0
                if len(o.life_cards) == 0 and o.leader:
                    from .effects.effect_registry import has_hardcoded_effect as _hlz_has, execute_hardcoded_effect as _hlz_exec
                    if _hlz_has(o.leader.id, 'on_life_zero'):
                        _hlz_exec(self, o, o.leader, 'on_life_zero')
                        if self.pending_choice:
                            attack['life_zero_pending'] = True
                            attack['life_zero_lc'] = life_card
                            attack['life_zero_ht'] = has_trigger
                            return

                # Handle life card (may prompt for trigger)
                paused = self._handle_life_card(o, life_card, has_trigger, has_banish, attacker)
                if paused:
                    return  # Waiting for trigger response

                # If no trigger prompt, continue to double attack or finish
                self._continue_after_life_card()
            else:
                # Check for KO immunity (e.g. OP01-024 cannot be KO'd by Strike)
                ko_immune = False
                self._log(f"  [DEBUG KO] {defender.name}: cannot_be_ko_by_strike={getattr(defender, 'cannot_be_ko_by_strike', False)}, attached_don={getattr(defender, 'attached_don', 0)}, attacker.attribute={getattr(attacker, 'attribute', '')}")
                if getattr(defender, 'cannot_be_ko_by_strike', False):
                    attacker_attr = (getattr(attacker, 'attribute', '') or '').lower()
                    if 'strike' in attacker_attr:
                        ko_immune = True
                        self._log(f"{defender.name} cannot be K.O.'d by Strike attribute — survives!")
                if getattr(defender, 'immune_to_slash_ko', False):
                    attacker_attr = (getattr(attacker, 'attribute', '') or '').lower()
                    if 'slash' in attacker_attr:
                        ko_immune = True
                        self._log(f"{defender.name} cannot be K.O.'d by Slash attribute — survives!")
                if getattr(defender, 'cannot_be_ko_in_battle', False) or getattr(defender, '_ko_protected_for_attack', False):
                    ko_immune = True
                    self._log(f"{defender.name} cannot be K.O.'d in battle — survives!")

                if ko_immune:
                    self._finish_attack()
                    return

                def after_battle_ko(result: str, _owner: Player, target: Optional[Card], _attacker: Optional[Card]) -> None:
                    if result == "ko" and target:
                        self._log(f"{attacker.name} KO's {target.name}!")
                        if getattr(attacker, 'set_active_on_ko', False) and not getattr(attacker, 'op02_094_used', False):
                            attacker._set_active_after_battle_resolution = True
                            attacker.op02_094_used = True
                    self._finish_attack()

                result = self._attempt_character_ko(
                    defender,
                    by_effect=False,
                    attacker=attacker,
                    controller=p,
                    after_resolve=after_battle_ko,
                )
                if result == "pending":
                    return
        else:
            self._log(f"{attacker.name}'s attack is defended (Defense: {total_defense}).")
            self._finish_attack()

    def _continue_after_life_card(self):
        """Continue combat after a life card's trigger has been resolved or declined.
        Handles Double Attack second hit, then finishes the attack."""
        if not self.pending_attack:
            return

        attack = self.pending_attack
        has_double_attack = attack.get('has_double_attack', False)
        double_processed = attack.get('double_attack_processed', False)
        has_banish = attack.get('has_banish', False)
        p = attack['attacker_player']
        o = attack['defender_player']
        attacker = attack['attacker']

        if has_double_attack and not double_processed:
            attack['double_attack_processed'] = True
            # Double Attack second hit only fires if opponent still has life cards.
            # If the first hit took their last life card (now at 0), skip the second hit.
            if len(o.life_cards) == 0:
                self._log(f"{attacker.name} has Double Attack but {o.name} has 0 life — second hit skipped")
            else:
                self._log(f"{attacker.name} has Double Attack - dealing additional damage!")
                life_card2, has_trigger2 = o.take_life_damage()
                # Game over only if take_life_damage returned None (was already at 0)
                if life_card2 is None:
                    self._log(f"{o.name} has no life remaining — {p.name} wins!")
                    self.game_over = True
                    self.winner = p
                    self.phase = GamePhase.GAME_OVER
                    self._finish_attack()
                    return

                paused = self._handle_life_card(o, life_card2, has_trigger2, has_banish, attacker)
                if paused:
                    return  # Waiting for trigger response on second life card

        self._finish_attack()

    def _handle_life_card(self, player: Player, life_card: Card, has_trigger: bool,
                          has_banish: bool, attacker: Card) -> bool:
        """Handle a life card's trigger and destination.

        Returns True if combat is paused waiting for trigger response (player must choose).
        Returns False if life card was handled immediately (no trigger prompt needed).
        """
        if not life_card:
            return False

        # If banished, card goes straight to trash — no trigger
        if has_banish:
            player.trash.append(life_card)
            self._log(f"  {life_card.name} is banished to trash")
            return False

        # If card has a trigger, prompt the player to activate or decline
        if has_trigger and not has_banish:
            # Get trigger text from either dedicated trigger field or effect text
            trigger_text = life_card.trigger or ''
            if not trigger_text.strip() and life_card.effect and '[Trigger]' in life_card.effect:
                import re
                m = re.search(r'\[Trigger\]\s*(.*?)(?:<br>|$)', life_card.effect)
                trigger_text = m.group(0) if m else life_card.effect
            self._log(f"  [TRIGGER] {life_card.name} has a Trigger: {trigger_text}")
            # Store trigger info in pending_attack so frontend can show prompt
            self.pending_attack['pending_trigger'] = {
                'life_card': life_card,
                'life_card_id': life_card.id,
                'life_card_name': life_card.name,
                'trigger_text': trigger_text,
                'player_id': player.player_id,
                'player_index': 0 if player is self.player1 else 1,
            }
            self.awaiting_response = "trigger"
            return True  # Combat paused — waiting for respond_trigger()

        # No trigger — card goes to hand
        player.hand.append(life_card)
        self._log(f"  {life_card.name} added to hand")
        return False

    def _defer_trigger_followup(self, player: Player, life_card: Card) -> None:
        """Remember a trigger-played life card while a follow-up pending choice resolves."""
        self._pending_trigger_followup = {
            "player_index": 0 if player is self.player1 else 1,
            "life_card": life_card,
        }

    def _complete_trigger_followup(self, *, played: bool = False, to_hand: bool = False) -> None:
        """Finalize a deferred trigger resolution after a pending choice finishes."""
        followup = getattr(self, "_pending_trigger_followup", None)
        if not followup:
            return

        player = self.player1 if followup["player_index"] == 0 else self.player2
        life_card = followup["life_card"]
        del self._pending_trigger_followup

        if played:
            pass
        elif to_hand:
            if life_card not in player.hand:
                player.hand.append(life_card)
                self._log(f"  {life_card.name} added to hand")
        else:
            if life_card not in player.trash:
                player.trash.append(life_card)
                self._log(f"  {life_card.name} sent to trash (trigger used)")

        if self.pending_attack and self.awaiting_response != "trigger" and not self.pending_choice:
            self._continue_after_life_card()

    def respond_trigger(self, activate: bool) -> bool:
        """Respond to a trigger prompt — activate the trigger or decline.

        Args:
            activate: True to activate the trigger effect, False to add card to hand.

        Returns:
            True if response was processed successfully.
        """
        if not self.pending_attack or self.awaiting_response != "trigger":
            return False

        attack = self.pending_attack
        trigger_info = attack.get('pending_trigger')
        if not trigger_info:
            return False

        life_card = trigger_info['life_card']
        # Use player_index (reliable) over player_id (both players share SID in PLAYTEST)
        if 'player_index' in trigger_info:
            player = self.player1 if trigger_info['player_index'] == 0 else self.player2
        else:
            player_id = trigger_info['player_id']
            player = self.player1 if self.player1.player_id == player_id else self.player2

        # Clear trigger info
        del attack['pending_trigger']
        self.awaiting_response = None

        if activate:
            trigger_text = trigger_info.get('trigger_text', life_card.trigger or '')
            self._log(f"  [TRIGGER] {life_card.name}: Activating trigger — {trigger_text}")

            # Try hardcoded trigger effects first (e.g. OP01-009 Carrot "Play this card")
            from .effects.effect_registry import has_hardcoded_effect, execute_hardcoded_effect
            card_was_played = False
            hardcoded_ran = False
            if has_hardcoded_effect(life_card.id, "trigger"):
                hardcoded_ran = execute_hardcoded_effect(self, player, life_card, "trigger")
                if any(card is life_card for card in player.cards_in_play):
                    card_was_played = True
                if self.pending_choice:
                    self._defer_trigger_followup(player, life_card)
                    return True

            # Fall back to parser-based trigger effects if no hardcoded handler
            if not hardcoded_ran:
                effect_manager = get_effect_manager()
                trigger_result = effect_manager.on_life_damage(self, player, life_card, False)
                if trigger_result[0] and trigger_result[1]:
                    if trigger_result[1].success and trigger_result[1].message:
                        self._log(f"    {trigger_result[1].message}")
                    if any(card is life_card for card in player.cards_in_play):
                        card_was_played = True

            # Card destination: if trigger played it to field, it stays; otherwise trash
            if not card_was_played:
                player.trash.append(life_card)
                self._log(f"  {life_card.name} sent to trash (trigger used)")
        else:
            # Declined — card goes to hand
            self._log(f"  [TRIGGER] {life_card.name}: Trigger declined — added to hand")
            player.hand.append(life_card)

        # Continue combat (double attack or finish)
        self._continue_after_life_card()
        return True

    def _finish_attack(self):
        """Clean up after attack resolution."""
        if self.pending_attack:
            attacker = self.pending_attack['attacker']
            attacker_player = self.pending_attack['attacker_player']
            # attacker.is_resting already set at attack declaration
            attacker.has_attacked = True
            if getattr(attacker, '_set_active_after_battle_resolution', False):
                attacker.is_resting = False
                attacker.has_attacked = False
                attacker._set_active_after_battle_resolution = False
                self._log(f"{attacker.name} is set active by its effect")
            if hasattr(attacker, 'set_active_on_ko'):
                attacker.set_active_on_ko = False
            # Handle return_to_bottom_after_battle (e.g. OP02-064 Mr.2)
            if getattr(attacker, 'return_to_bottom_after_battle', False):
                if attacker in attacker_player.cards_in_play:
                    attacker_player.cards_in_play.remove(attacker)
                    attacker_player.deck.append(attacker)
                    self._log(f"{attacker.name} returns to bottom of deck after battle")
                attacker.return_to_bottom_after_battle = False

        self.pending_attack = None
        self.awaiting_response = None
        for p in [self.player1, self.player2]:
            battle_targets = list(p.cards_in_play)
            if p.leader:
                battle_targets.append(p.leader)
            for c in battle_targets:
                battle_modifier = getattr(c, '_battle_power_modifier', 0)
                if battle_modifier:
                    c.power_modifier = getattr(c, 'power_modifier', 0) - battle_modifier
                    c._battle_power_modifier = 0
            for c in p.cards_in_play:
                if hasattr(c, '_ko_protected_for_attack'):
                    c._ko_protected_for_attack = False
        # Clear per-battle blocker restrictions
        self.blocker_power_minimum = 0
        self.blocker_cost_limit = None

        if not self.game_over:
            self.phase = GamePhase.MAIN
            # Recalculate continuous effects — attacks change resting state which
            # may activate/deactivate power bonuses (e.g. Ashura Doji OP01-032).
            self._recalc_continuous_effects()

    def run_turn(self):
        """Execute a full turn (for simulation/testing)."""
        if self.game_over:
            return

        player = self.current_player
        opponent = self.opponent_player

        # Reset [Activate: Main] / once-per-turn flags at start of turn
        if player.leader and hasattr(player.leader, 'main_activated_this_turn'):
            player.leader.main_activated_this_turn = False
        for card in player.cards_in_play:
            if hasattr(card, 'main_activated_this_turn'):
                card.main_activated_this_turn = False

        # Log turn start with game state
        self._log(f"{'='*50}")
        self._log(f"TURN {self.turn_count}: {player.name}")
        self._log(f"{'='*50}")
        self._log(f"DON: {self.available_don()}/{len(player.don_pool)} | Hand: {len(player.hand)} | Field: {len([c for c in player.cards_in_play if c.card_type == 'CHARACTER'])}/5 | Life: {len(player.life_cards)} vs {len(opponent.life_cards)}")

        # Main phase: play cards and activate effects
        self._log(f"[MAIN PHASE]")
        cards_played = 0
        while cards_played < 3:  # Limit to prevent infinite loops
            card_to_play = self.choose_card_to_play()
            if card_to_play:
                self._log(f"  [PLAY] {card_to_play.name} ({card_to_play.card_type}, Cost {card_to_play.cost})")
                self.play_card(card_to_play)
                cards_played += 1
            else:
                if cards_played == 0:
                    self._log(f"  No playable cards")
                break

        # Try to activate [Activate: Main] effects on cards in play
        self._try_activate_main_effects()

        # Assign DON to attackers
        self.assign_don_to_attackers()

        # Attack phase
        self._log(f"[ATTACK PHASE]")
        attacks_made = 0

        def choose_attack_target(attacker: Card) -> tuple[int, Card]:
            """
            Choose the best attack target for an attacker.

            Strategy:
            1. Target rested characters with Blocker first (remove blocking threats)
            2. Target rested characters we can KO (attacker power >= target power)
            3. Default to attacking the leader

            Returns (target_index, target_card) where -1 = leader
            """
            attacker_power = (attacker.power or 0) + getattr(attacker, 'attached_don', 0) * 1000

            # Get all valid targets (leader + rested characters)
            targets = self.get_valid_attack_targets()

            # Filter to just rested characters (exclude leader at index -1)
            rested_chars = [(idx, card) for idx, card in targets if idx >= 0]

            if rested_chars:
                # Priority 1: Target characters with Blocker (remove blocking threats)
                blockers = [(idx, card) for idx, card in rested_chars
                           if card.effect and '[Blocker]' in card.effect]
                if blockers:
                    # Attack the blocker we can most likely KO
                    for idx, card in sorted(blockers, key=lambda x: (x[1].power or 0) + getattr(x[1], 'power_modifier', 0)):
                        if attacker_power >= (card.power or 0) + getattr(card, 'power_modifier', 0):
                            return (idx, card)
                    # If we can't KO any blocker, still attack one to remove threat
                    return blockers[0]

                # Priority 2: Attack characters we can KO (clean removal)
                ko_targets = [(idx, card) for idx, card in rested_chars
                             if attacker_power >= (card.power or 0) + getattr(card, 'power_modifier', 0)]
                if ko_targets:
                    # Attack the highest power character we can KO
                    return max(ko_targets, key=lambda x: (x[1].power or 0) + getattr(x[1], 'power_modifier', 0))

            # Default: attack the leader
            return (-1, opponent.leader)

        # Attack with characters
        for card in list(self.current_player.cards_in_play):
            if self.game_over:
                return
            if not card.is_resting and not card.has_attacked:
                # Check if can attack (summoning sickness)
                played_turn = getattr(card, 'played_turn', None)
                has_rush = getattr(card, 'has_rush', False)
                if played_turn == self.turn_count and not has_rush:
                    self._log(f"  [WAIT] {card.name} has summoning sickness")
                    continue

                # Choose strategic target
                target_idx, target = choose_attack_target(card)
                self._log(f"  [ATK] {card.name} ({card.power or 0}) -> {target.name}")
                self.attack_with_card(card, target_idx)
                attacks_made += 1

        # Attack with leader
        if not self.game_over and self.can_attack_with_leader():
            if not self.current_player.leader.is_resting:
                # Choose strategic target for leader too
                target_idx, target = choose_attack_target(player.leader)
                self._log(f"  [ATK] {player.leader.name} ({player.leader.power or 0}) -> {target.name}")
                self.attack_with_card(self.current_player.leader, target_idx)
                attacks_made += 1
        elif not self.can_attack_with_leader():
            self._log(f"  [WAIT] Leader cannot attack yet")

        if attacks_made == 0:
            self._log(f"  No attacks this turn")

        # End phase
        self._log(f"[END PHASE] Hand: {len(player.hand)}/7")

        if not self.game_over:
            self.next_turn()

    def is_game_over(self) -> bool:
        """Check if the game has ended."""
        return self.game_over

    def get_winner(self) -> Optional[Player]:
        """Get the winning player, if any."""
        return self.winner

    def _card_to_dict(self, card: Card) -> dict:
        """Serialize a card to a dictionary."""
        return {
            'id': card.id,
            'name': card.name,
            'card_type': card.card_type,
            'cost': max(0, (card.cost or 0) + getattr(card, 'cost_modifier', 0)),
            'base_cost': card.cost or 0,
            'power': (card.power or 0) + getattr(card, 'power_modifier', 0),
            'base_power': card.power or 0,
            'counter': card.counter,
            'effect': card.effect,
            'trigger': card.trigger,
            'attribute': card.attribute,
            'image_url': getattr(card, 'image_url', None) or getattr(card, 'image_link', None),
            'image_link': getattr(card, 'image_link', None),
            'is_resting': getattr(card, 'is_resting', False),
            'attached_don': getattr(card, 'attached_don', 0),
            'has_attacked': getattr(card, 'has_attacked', False),
            'can_attack_active': getattr(card, 'can_attack_active', False),
            'has_double_attack': getattr(card, 'has_doubleattack', False) or getattr(card, 'has_double_attack', False),
            'has_taunt': getattr(card, 'has_taunt', False),
            'is_face_up': getattr(card, 'is_face_up', False),
        }

    def _life_card_to_dict(self, card: Card) -> dict:
        """Serialize a life card, hiding face-down cards from the frontend."""
        if getattr(card, 'is_face_up', False):
            return self._card_to_dict(card)
        return {
            'id': 'hidden',
            'name': 'Life Card',
            'card_type': 'HIDDEN',
            'cost': None,
            'base_cost': None,
            'power': None,
            'base_power': None,
            'counter': None,
            'effect': None,
            'trigger': None,
            'attribute': None,
            'image_url': None,
            'image_link': None,
            'is_resting': False,
            'attached_don': 0,
            'has_attacked': False,
            'can_attack_active': False,
            'has_double_attack': False,
            'has_taunt': False,
            'is_face_up': False,
        }


    def _trigger_on_don_return_effects(self, player: Player):
        """Fire leader effects that care about DON!! returning to the DON!! deck."""
        from .effects.effect_registry import has_hardcoded_effect, execute_hardcoded_effect
        if player.leader and has_hardcoded_effect(player.leader.id, 'on_don_return'):
            execute_hardcoded_effect(self, player, player.leader, 'on_don_return')

    def _player_to_dict(self, player: Player, is_viewer: bool = False) -> dict:
        """Serialize a player to a dictionary.

        Args:
            player: The player to serialize
            is_viewer: If True, include full hand info (player is viewing their own state)
        """
        return {
            'player_id': player.player_id or '',
            'name': player.name,
            'leader': self._card_to_dict(player.leader) if player.leader else None,
            'life_count': len(player.life_cards),
            'life_cards': [self._life_card_to_dict(c) for c in player.life_cards],
            'hand_count': len(player.hand),
            'hand': [self._card_to_dict(c) for c in player.hand] if is_viewer else [],
            'deck_count': len(player.deck),
            'field': [self._card_to_dict(c) for c in player.cards_in_play],
            'trash_count': len(player.trash),
            'trash': [self._card_to_dict(c) for c in player.trash],
            'don_active': player.don_pool.count('active'),
            'don_total': len(player.don_pool),
            'don_pool': list(player.don_pool),
            'has_mulliganed': player.has_mulliganed,
        }

    def to_dict(self, for_player: str = None) -> dict:
        """Serialize the game state to a dictionary.

        Args:
            for_player: The player_id viewing the state (to show their hand)
        """
        # Determine which player is viewing
        p1_is_viewer = for_player == self.player1.player_id
        p2_is_viewer = for_player == self.player2.player_id

        # Get current player index
        active_player = 0 if self.current_player == self.player1 else 1

        # Get winner index
        winner_idx = None
        if self.winner:
            winner_idx = 0 if self.winner == self.player1 else 1

        # Serialize pending attack for frontend
        pending_attack_dict = None
        if self.pending_attack:
            attack = self.pending_attack
            defender = attack['current_target']
            trigger_info = attack.get('pending_trigger')
            pending_attack_dict = {
                'attacker_name': attack['attacker_name'],
                'attacker_power': attack['attacker_power'],
                'attacker_index': attack['attacker_index'],
                'target_name': defender.name if defender else None,
                'target_power': (defender.power or 0) + getattr(defender, 'power_modifier', 0) if defender else 0,
                'target_index': attack['current_target_index'],
                'is_leader': defender.card_type == 'LEADER' if defender else True,
                'available_blockers': attack.get('available_blockers', []),
                'available_counters': attack.get('available_counters', []),
                'counter_power': attack.get('counter_power', 0),
                'leader_has_effect': attack.get('leader_has_effect', False),
                'pending_trigger': {
                    'card_id': trigger_info['life_card_id'],
                    'card_name': trigger_info['life_card_name'],
                    'trigger_text': trigger_info['trigger_text'],
                    'player_id': trigger_info['player_id'],
                } if trigger_info else None,
            }

        return {
            'turn': self.turn_count,
            'phase': self.phase.value if hasattr(self.phase, 'value') else str(self.phase),
            'active_player': active_player,
            'players': [
                self._player_to_dict(self.player1, is_viewer=p1_is_viewer),
                self._player_to_dict(self.player2, is_viewer=p2_is_viewer),
            ],
            'is_terminal': self.game_over,
            'winner': winner_idx,
            'awaiting_response': self.awaiting_response,
            'pending_attack': pending_attack_dict,
            'pending_choice': self.pending_choice.to_dict() if self.pending_choice else None,
        }

    def resolve_pending_choice(self, selected: List[str]) -> bool:
        """
        Resolve a pending choice with the player's selection.

        Args:
            selected: List of selected option IDs

        Returns:
            True if the choice was resolved successfully
        """
        if not self.pending_choice:
            return False

        choice = self.pending_choice
        action = choice.callback_action
        data = choice.callback_data

        # Get the player who needs to make this choice
        # Use player_index (reliable) over player_id (both players share SID in PLAYTEST)
        if "player_index" in data:
            player = self.player1 if data["player_index"] == 0 else self.player2
        else:
            player_id = data.get("player_id")
            player = self.player1 if self.player1.player_id == player_id else self.player2

        try:
            # Preferred path: callable closure — avoids string dispatch entirely
            if choice.callback is not None:
                choice.callback(selected)
            elif action == "trash_from_hand":
                # selected contains indices of cards to trash
                indices = [int(s) for s in selected]
                # Sort in reverse so we remove from end first
                for idx in sorted(indices, reverse=True):
                    if 0 <= idx < len(player.hand):
                        card = player.hand.pop(idx)
                        player.trash.append(card)
                        self._log(f"{player.name} trashed {card.name}")

            elif action == "select_target":
                # Handle target selection for effects
                target_idx = int(selected[0]) if selected else -1
                # Store selected target for effect continuation
                data["selected_target"] = target_idx

            elif action == "choose_option":
                # Handle option selection
                selected_option = selected[0] if selected else None
                data["selected_option"] = selected_option

            elif action == "search_add_to_hand":
                # Search effect: add selected cards to hand/field, order rest to bottom
                look_count = data.get("look_count", 0)
                # Backward compat: old callers passed top_card_indices instead of look_count
                if not look_count:
                    look_count = len(data.get("top_card_indices", []))
                valid_indices = data.get("valid_indices", None)
                source_name = data.get("source_name", player.name)
                source_id = data.get("source_id", "")
                trash_rest = data.get("trash_rest", False)
                play_to_field = data.get("play_to_field", False)
                play_rested = data.get("play_rested", False)

                chosen_indices = sorted([int(s) for s in selected], reverse=True) if selected else []

                # Validate against valid_indices if provided
                if valid_indices is not None:
                    chosen_indices = [i for i in chosen_indices if i in valid_indices]

                # Pop chosen cards from deck by position (descending to preserve indices)
                chosen_cards = []
                for idx in chosen_indices:
                    if 0 <= idx < len(player.deck):
                        chosen_card = player.deck.pop(idx)
                        chosen_cards.append(chosen_card)

                # Place chosen cards in hand or on field
                for chosen_card in chosen_cards:
                    if play_to_field:
                        self.play_card_to_field_by_effect(
                            player,
                            chosen_card,
                            rest_on_play=play_rested,
                            log_message=f"{source_name}: Played {chosen_card.name} to field",
                        )
                    else:
                        player.hand.append(chosen_card)
                        self._log(f"{source_name}: Added {chosen_card.name} to hand")

                # Pull remaining top cards out of deck
                remaining_count = look_count - len(chosen_cards)
                remaining = player.deck[:remaining_count]
                for _ in range(remaining_count):
                    if player.deck:
                        player.deck.pop(0)

                # Handle remaining cards
                if trash_rest:
                    for c in remaining:
                        player.trash.append(c)
                    if remaining:
                        self._log(f"{source_name}: Trashed {len(remaining)} remaining cards")
                elif len(remaining) <= 1:
                    player.deck.extend(remaining)
                    if remaining:
                        self._log(f"{source_name}: Remaining card placed at bottom of deck")
                else:
                    # Let player order remaining cards to bottom
                    self._create_deck_order_choice(
                        player, remaining, [],
                        source_name=source_name,
                        source_id=source_id,
                    )

            elif action == "assign_don":
                # Assign DON to selected character
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])
                don_count = data.get("don_count", 1)
                rested_only = data.get("rested_only", True)

                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    # Find the actual card
                    target = None
                    for c in player.cards_in_play + ([player.leader] if player.leader else []):
                        if c and c.id == target_info["id"]:
                            target = c
                            break

                    if target:
                        # Give DON to target
                        given = 0
                        for don in player.don_cards[:]:
                            if given >= don_count:
                                break
                            if rested_only and not don.is_resting:
                                continue
                            target.attached_don = getattr(target, 'attached_don', 0) + 1
                            given += 1
                        self._log(f"{player.name} attached {given} DON to {target.name}")

            elif action == "apply_power":
                # Apply power modifier to selected character(s)
                target_cards = data.get("target_cards", [])
                power_amount = data.get("power_amount", 0)
                opponent = self.player2 if player == self.player1 else self.player1
                all_cards = player.cards_in_play + opponent.cards_in_play + [player.leader, opponent.leader]

                for sel in selected:
                    target_idx = int(sel) if sel is not None else -1
                    if 0 <= target_idx < len(target_cards):
                        target_info = target_cards[target_idx]
                        target = None
                        for c in all_cards:
                            if c and c.id == target_info["id"]:
                                target = c
                                break
                        if target:
                            target.power_modifier = getattr(target, 'power_modifier', 0) + power_amount
                            target._sticky_power_modifier = getattr(target, '_sticky_power_modifier', 0) + power_amount
                            sign = "+" if power_amount >= 0 else ""
                            self._log(f"{target.name} gets {sign}{power_amount} power")

            elif action == "apply_power_until_next_turn":
                # Apply power modifier that persists until end of NEXT turn
                target_cards = data.get("target_cards", [])
                power_amount = data.get("power_amount", 0)
                opponent = self.player2 if player == self.player1 else self.player1
                all_cards = player.cards_in_play + opponent.cards_in_play + [player.leader, opponent.leader]

                for sel in selected:
                    target_idx = int(sel) if sel is not None else -1
                    if 0 <= target_idx < len(target_cards):
                        target_info = target_cards[target_idx]
                        target = None
                        for c in all_cards:
                            if c and c.id == target_info["id"]:
                                target = c
                                break
                        if target:
                            target.power_modifier = getattr(target, 'power_modifier', 0) + power_amount
                            target._sticky_power_modifier = getattr(target, '_sticky_power_modifier', 0) + power_amount
                            target.power_modifier_expires_on_turn = self.turn_count + 1
                            target._sticky_power_modifier_expires_on_turn = self.turn_count + 1
                            sign = "+" if power_amount >= 0 else ""
                            self._log(f"{target.name} gets {sign}{power_amount} power until end of next turn")

            elif action == "ko_target":
                # KO selected character
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])

                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    opponent = self.player2 if player == self.player1 else self.player1

                    # Find and KO the target
                    for p in [player, opponent]:
                        for c in p.cards_in_play[:]:
                            if c.id == target_info["id"]:
                                if getattr(c, 'cannot_be_ko_by_effects', False):
                                    self._log(f"{c.name} cannot be K.O.'d by effects")
                                    break
                                p.cards_in_play.remove(c)
                                p.trash.append(c)
                                self._log(f"{c.name} was KO'd")
                                break


            elif action == "trash_own_character":
                # Trash a selected character from hand or field (e.g. OP03-012 Blackbeard)
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])
                draw_after = data.get("draw_after", 0)
                power_boost_card_id = data.get("power_boost_card_id", "")
                power_boost_amount = data.get("power_boost_amount", 0)
                trashed = False
                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    # Search hand first, then field
                    found = False
                    for c in player.hand[:]:
                        if c.id == target_info["id"]:
                            player.hand.remove(c)
                            player.trash.append(c)
                            self._log(f"{player.name} trashed {c.name} from hand")
                            found = True
                            trashed = True
                            break
                    if not found:
                        for c in player.cards_in_play[:]:
                            if c.id == target_info["id"]:
                                player.cards_in_play.remove(c)
                                player.trash.append(c)
                                self._log(f"{player.name} trashed {c.name} from field")
                                trashed = True
                                break
                if trashed:
                    if draw_after > 0:
                        from .effects.effect_registry import draw_cards
                        draw_cards(player, draw_after)
                    if power_boost_card_id and power_boost_amount:
                        boost_card = (next((c for c in player.cards_in_play if c.id == power_boost_card_id), None)
                                      or (player.leader if player.leader and player.leader.id == power_boost_card_id else None))
                        if boost_card:
                            boost_card.power_modifier = getattr(boost_card, 'power_modifier', 0) + power_boost_amount
                            boost_card._sticky_power_modifier = getattr(boost_card, '_sticky_power_modifier', 0) + power_boost_amount
                            self._log(f"{boost_card.name} gains +{power_boost_amount} power")







            elif action == "ko_multi_targets":
                # KO multiple selected targets (e.g. OP03-025 Krieg)
                target_cards = data.get("target_cards", [])
                opponent = self.player2 if player == self.player1 else self.player1
                for sel in selected:
                    target_idx = int(sel)
                    if 0 <= target_idx < len(target_cards):
                        target_info = target_cards[target_idx]
                        for c in opponent.cards_in_play[:]:
                            if c.id == target_info["id"]:
                                if getattr(c, 'cannot_be_ko_by_effects', False):
                                    self._log(f"{c.name} cannot be K.O.'d by effects")
                                    break
                                opponent.cards_in_play.remove(c)
                                opponent.trash.append(c)
                                self._log(f"{c.name} was K.O.'d")
                                break


            elif action == "rest_targets_multi":
                # Rest multiple selected targets (e.g. OP03-024 Gin, OP03-038 MH5)
                target_cards = data.get("target_cards", [])
                opponent = self.player2 if player == self.player1 else self.player1
                for sel in selected:
                    target_idx = int(sel)
                    if 0 <= target_idx < len(target_cards):
                        target_info = target_cards[target_idx]
                        for p_ in [player, opponent]:
                            for c in p_.cards_in_play:
                                if c.id == target_info["id"]:
                                    c.is_resting = True
                                    self._log(f"{c.name} was rested")
                                    break



































            elif action == "return_from_trash_to_hand":
                # Move selected card from player's trash to hand (e.g. Uta)
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])
                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    for c in player.trash[:]:
                        if c.id == target_info["id"]:
                            player.trash.remove(c)
                            player.hand.append(c)
                            self._log(f"{c.name} added to hand from trash")
                            break

            elif action == "return_to_hand":
                # Return selected character to owner's hand
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])

                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    opponent = self.player2 if player == self.player1 else self.player1

                    for p in [player, opponent]:
                        for c in p.cards_in_play[:]:
                            if c.id == target_info["id"]:
                                p.cards_in_play.remove(c)
                                p.hand.append(c)
                                self._log(f"{c.name} returned to hand")
                                break

            elif action == "play_from_trash":
                # Play selected card from trash
                if not selected:
                    pass  # Player chose not to play anything
                else:
                    target_idx = int(selected[0])
                    target_cards = data.get("target_cards", [])
                    rest_on_play = data.get("rest_on_play", True)

                    if 0 <= target_idx < len(target_cards):
                        target_info = target_cards[target_idx]
                        for c in player.trash[:]:
                            if c.id == target_info["id"]:
                                player.trash.remove(c)
                                self.play_card_to_field_by_effect(
                                    player,
                                    c,
                                    rest_on_play=rest_on_play,
                                    log_message=f"{player.name} played {c.name} from trash",
                                )
                                break

            elif action == "select_mode":
                # Handle mode selection for multi-choice effects
                selected_mode = selected[0] if selected else None
                card_id = data.get("card_id") or data.get("source_card_id")
                modes = data.get("modes", [])

                # Find the source card to continue the effect
                source_card = None
                for c in player.cards_in_play + player.hand + player.trash:
                    if c and c.id == card_id:
                        source_card = c
                        break

                opponent = self.player2 if player == self.player1 else self.player1

                # Handle different card-specific mode effects
                if selected_mode == "return":
                    # Return opponent's character to hand
                    from .effects.effect_registry import return_opponent_to_hand
                    # Determine max_cost based on the card
                    if card_id and "OP12-060" in card_id:  # Boeuf Burst
                        self.pending_choice = None
                        return return_opponent_to_hand(self, player, max_cost=4, source_card=source_card)
                    elif card_id and "OP06-065" in card_id:  # Niji
                        self.pending_choice = None
                        return return_opponent_to_hand(self, player, max_cost=3, source_card=source_card)
                    elif card_id and "OP05-096" in card_id:  # 500 Million
                        self.pending_choice = None
                        return return_opponent_to_hand(self, player, max_cost=1, source_card=source_card)

                elif selected_mode == "draw":
                    # Draw cards
                    from .effects.effect_registry import draw_cards
                    if card_id and "OP12-060" in card_id:  # Boeuf Burst
                        draw_cards(player, 2)
                        self._log(f"{player.name} drew 2 cards")
                    elif card_id and "EB02-045" in card_id:  # Law
                        draw_cards(player, 1)
                        self._log(f"{player.name} drew 1 card")

                elif selected_mode == "ko":
                    # KO opponent's character
                    from .effects.effect_registry import ko_opponent_character
                    if card_id and "OP06-065" in card_id:  # Niji
                        self.pending_choice = None
                        return ko_opponent_character(self, player, max_cost=2, source_card=source_card)
                    elif card_id and "EB02-051" in card_id:  # Three-Pace
                        self.pending_choice = None
                        return ko_opponent_character(self, player, max_cost=2, source_card=source_card)
                    elif card_id and "OP05-096" in card_id:  # 500 Million
                        self.pending_choice = None
                        return ko_opponent_character(self, player, max_cost=1, source_card=source_card)

                elif selected_mode == "discard":
                    # Opponent discards
                    if opponent.hand:
                        from .effects.effect_registry import trash_from_hand
                        trash_from_hand(opponent, 1, self, source_card)
                        self._log(f"{opponent.name} must discard 1 card")

                elif selected_mode == "cost_reduce":
                    # Apply -4 cost to opponent's character
                    from .effects.effect_registry import create_power_effect_choice
                    if opponent.cards_in_play:
                        self.pending_choice = None
                        # Create a choice for target selection
                        return create_power_effect_choice(
                            self, player, opponent.cards_in_play, -4000,
                            source_card=source_card,
                            prompt="Choose opponent's Character to give -4 cost"
                        )

                elif selected_mode == "bottom":
                    # Place at bottom of deck (500 Million)
                    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 1]
                    if targets:
                        target = targets[0]  # Will need a choice here too
                        opponent.cards_in_play.remove(target)
                        opponent.deck.append(target)
                        self._log(f"{target.name} placed at bottom of deck")

                elif selected_mode == "trash_life":
                    # Charlotte Linlin - opponent loses life
                    if opponent.life_cards:
                        life = opponent.life_cards.pop(0)
                        opponent.trash.append(life)
                        self._log(f"{opponent.name}'s top life was trashed")

                elif selected_mode == "add_life":
                    # Charlotte Linlin - player gains life
                    actual_player = self.player2 if player == self.player1 else self.player1
                    if actual_player.deck:
                        actual_player.life_cards.append(actual_player.deck.pop(0))
                        self._log(f"{actual_player.name} added a card to life")

                elif selected_mode == "view_life":
                    # Viola - look at opponent's life (informational)
                    self._log(f"{player.name} looked at {opponent.name}'s life cards")

                elif selected_mode == "view_deck":
                    # Viola - look at top 5 and rearrange (informational for now)
                    self._log(f"{player.name} looked at top 5 cards of deck")

                elif selected_mode == "top_life":
                    # ST22-015 I AM WHITEBEARD!! - take top life card to hand, Leader gains +2000
                    if player.life_cards:
                        life_card = player.life_cards.pop(0)
                        player.hand.append(life_card)
                        self._log(f"{player.name} added top life card to hand")
                        if player.leader:
                            # +2000 until end of opponent's next turn
                            player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 2000
                            self._log(f"{player.leader.name} gains +2000 power until end of opponent's next turn")

                elif selected_mode == "bottom_life":
                    # ST22-015 I AM WHITEBEARD!! - take bottom life card to hand, Leader gains +2000
                    if player.life_cards:
                        life_card = player.life_cards.pop()
                        player.hand.append(life_card)
                        self._log(f"{player.name} added bottom life card to hand")
                        if player.leader:
                            # +2000 until end of opponent's next turn
                            player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 2000
                            self._log(f"{player.leader.name} gains +2000 power until end of opponent's next turn")

                elif selected_mode == "skip":
                    # Skip the optional effect
                    self._log(f"{player.name} chose not to add a life card to hand")




            elif action == "return_own_to_hand":
                # Generic return own character to hand
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])

                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    for c in player.cards_in_play[:]:
                        if c.id == target_info["id"]:
                            player.cards_in_play.remove(c)
                            player.hand.append(c)
                            self._log(f"{player.name} returned {c.name} to hand")
                            break


            elif action == "apply_cost_reduction":
                # Apply cost reduction to selected character
                target_cards = data.get("target_cards", [])
                cost_reduction = data.get("cost_reduction", 0)
                opponent = self.player2 if player == self.player1 else self.player1
                for sel in selected:
                    target_idx = int(sel)
                    if 0 <= target_idx < len(target_cards):
                        target_info = target_cards[target_idx]
                        for p in [opponent, player]:
                            for c in p.cards_in_play:
                                if c.id == target_info["id"]:
                                    if cost_reduction == "zero":
                                        # Set cost to 0 by applying enough negative modifier
                                        current_cost = max(0, (c.cost or 0) + getattr(c, 'cost_modifier', 0))
                                        c.cost_modifier = getattr(c, 'cost_modifier', 0) - current_cost
                                        self._log(f"{c.name}'s cost set to 0 this turn")
                                    else:
                                        c.cost_modifier = getattr(c, 'cost_modifier', 0) + cost_reduction
                                        self._log(f"{c.name} gets {cost_reduction} cost this turn")
                                    break

            elif action == "play_from_hand":
                # Play selected card from hand
                if not selected:
                    pass  # Player chose not to play anything
                else:
                    target_idx = int(selected[0])
                    target_cards = data.get("target_cards", [])
                    rest_on_play = data.get("rest_on_play", False)

                    if 0 <= target_idx < len(target_cards):
                        target_info = target_cards[target_idx]
                        for c in player.hand[:]:
                            if c.id == target_info["id"]:
                                player.hand.remove(c)
                                self.play_card_to_field_by_effect(
                                    player,
                                    c,
                                    rest_on_play=rest_on_play,
                                    log_message=f"{player.name} played {c.name} from hand",
                                )
                                break

            elif action == "place_at_bottom":
                # Place selected card at bottom of owner's deck
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])

                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    opponent = self.player2 if player == self.player1 else self.player1

                    # Find and place at bottom
                    for p in [player, opponent]:
                        for c in p.cards_in_play[:]:
                            if c.id == target_info["id"]:
                                p.cards_in_play.remove(c)
                                p.deck.append(c)
                                self._log(f"{c.name} was placed at the bottom of deck")
                                break





            elif action == "nami_deck_order":
                # Sequential deck ordering: player picks one card at a time
                remaining_cards_data = data.get("remaining_cards", [])
                ordered_so_far = data.get("ordered_so_far", [])
                source_name = data.get("source_name", "Nami")
                source_id = data.get("source_id", "OP01-016")
                placement = data.get("placement", "bottom")

                chosen_idx = int(selected[0]) if selected else 0
                if 0 <= chosen_idx < len(remaining_cards_data):
                    chosen_info = remaining_cards_data.pop(chosen_idx)
                    ordered_so_far.append(chosen_info)

                if len(remaining_cards_data) <= 1:
                    # Last card auto-placed
                    if remaining_cards_data:
                        ordered_so_far.append(remaining_cards_data[0])
                    # Place all ordered cards at the chosen location
                    if placement == "top":
                        # Insert in reverse so first chosen = on top
                        for card_info in reversed(ordered_so_far):
                            card_obj = self._find_card_by_info(card_info)
                            if card_obj:
                                player.deck.insert(0, card_obj)
                        self._log(f"{source_name}: Cards placed on TOP of deck")
                    else:
                        for card_info in ordered_so_far:
                            card_obj = self._find_card_by_info(card_info)
                            if card_obj:
                                player.deck.append(card_obj)
                        self._log(f"{source_name}: Cards placed at BOTTOM of deck")
                else:
                    # More cards to order — chain another choice
                    self._create_deck_order_choice(
                        player,
                        None,
                        ordered_so_far,
                        source_name=source_name,
                        source_id=source_id,
                        remaining_cards_data=remaining_cards_data,
                        placement=placement,
                    )

            elif action == "deck_top_or_bottom_all":
                # Single choice: place ALL cards at top or bottom, then order them
                cards_data = data.get("cards_data", [])
                source_name = data.get("source_name", "")
                placement = selected[0] if selected else "bottom"
                if len(cards_data) <= 1:
                    # Only 1 card — place directly, no ordering needed
                    card_obj = self._find_card_by_info(cards_data[0]) if cards_data else None
                    if card_obj:
                        if placement == "top":
                            player.deck.insert(0, card_obj)
                            self._log(f"{source_name}: {card_obj.name} placed on TOP of deck")
                        else:
                            player.deck.append(card_obj)
                            self._log(f"{source_name}: {card_obj.name} placed at BOTTOM of deck")
                else:
                    # Multiple cards — chain to ordering step
                    self._create_deck_order_choice(
                        player, None, [],
                        source_name=source_name,
                        source_id=data.get("source_id", ""),
                        remaining_cards_data=cards_data,
                        placement=placement,
                    )



            elif action == "cannot_attack_target":
                # Target cannot attack until end of phase
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])
                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    opponent = self.player2 if player == self.player1 else self.player1
                    for c in opponent.cards_in_play:
                        if c.id == target_info["id"]:
                            c.cannot_attack = True
                            c.cannot_attack_until_turn = self.turn_count + 1
                            self._log(f"{c.name} cannot attack this turn")
                            break

            elif action == "give_double_attack":
                # Give double attack to selected character
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])
                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    for c in player.cards_in_play:
                        if c.id == target_info["id"]:
                            c.has_doubleattack = True
                            c.has_double_attack = True
                            self._log(f"{c.name} gains Double Attack")
                            break

            elif action == "give_banish":
                # Give banish to selected character
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])
                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    for c in player.cards_in_play:
                        if c.id == target_info["id"]:
                            c.has_banish = True
                            self._log(f"{c.name} gains Banish")
                            break

            elif action == "add_to_opponent_life":
                # Add opponent's character to their life
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])
                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    owner_key = data.get("owner", "opponent")
                    target_owner = player if owner_key == "player" else (self.player2 if player == self.player1 else self.player1)
                    position = data.get("position", "top")
                    face_up = bool(data.get("face_up", False))
                    for c in target_owner.cards_in_play[:]:
                        if c.id == target_info["id"]:
                            target_owner.cards_in_play.remove(c)
                            c.is_face_up = face_up
                            if position == "bottom":
                                target_owner.life_cards.insert(0, c)
                            else:
                                target_owner.life_cards.append(c)
                            face_label = " face-up" if face_up else ""
                            self._log(f"{c.name} was added to {target_owner.name}'s Life{face_label} at the {position}")
                            break

            elif action == "replace_field_card":
                # Field was full — trash the selected character, then play the new card from hand
                target_idx = int(selected[0]) if selected else -1
                if 0 <= target_idx < len(player.cards_in_play):
                    removed = player.cards_in_play[target_idx]
                    player.cards_in_play.remove(removed)
                    player.trash.append(removed)
                    self._log(f"{removed.name} was trashed to make room")

                    # Now play the queued card from hand
                    card_to_play_id = data.get("card_to_play_id")
                    card_to_play = None
                    for c in player.hand:
                        if c.id == card_to_play_id:
                            card_to_play = c
                            break
                    if card_to_play:
                        self.play_card(card_to_play)
                    else:
                        self._log(f"Card {card_to_play_id} no longer in hand")

            elif action == "perona_cannot_rest":
                # Mark selected characters as cannot be rested
                target_cards = data.get("target_cards", [])
                opponent = self.player2 if player == self.player1 else self.player1
                for idx_str in selected[:2]:  # Max 2
                    idx = int(idx_str)
                    if 0 <= idx < len(target_cards):
                        target_info = target_cards[idx]
                        for c in opponent.cards_in_play:
                            if c.id == target_info["id"]:
                                c.cannot_be_rested = True
                                self._log(f"{c.name} cannot be rested")
                                break

            elif action == "play_from_hand_or_trash":
                # Play selected card from hand or trash
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])
                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    for c in player.hand[:]:
                        if c.id == target_info["id"]:
                            player.hand.remove(c)
                            self.play_card_to_field_by_effect(
                                player,
                                c,
                                log_message=f"{c.name} was played from hand",
                            )
                            break
                    else:
                        for c in list(player.trash):
                            if c.id == target_info["id"]:
                                player.trash.remove(c)
                                self.play_card_to_field_by_effect(
                                    player,
                                    c,
                                    log_message=f"{c.name} was played from trash",
                                )
                                break

            elif action == "give_rush":
                # Give Rush to selected character
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])
                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    for c in player.cards_in_play:
                        if c.id == target_info["id"]:
                            c.has_rush = True
                            self._log(f"{c.name} gains Rush")
                            break

            elif action == "set_active":
                # Set selected character active
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])
                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    for c in player.cards_in_play:
                        if c.id == target_info["id"]:
                            c.is_resting = False
                            c.has_attacked = False  # Reset so card can attack again this turn
                            self._log(f"{c.name} was set active")
                            break

            elif action == "rest_instead":
                # Rest selected character instead of another
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])
                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    for c in player.cards_in_play:
                        if c.id == target_info["id"]:
                            c.is_resting = True
                            self._log(f"{c.name} was rested instead")
                            break

            elif action == "rest_target":
                # Rest selected target
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])
                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    opponent = self.player2 if player == self.player1 else self.player1
                    for p_ in [player, opponent]:
                        for c in p_.cards_in_play:
                            if c.id == target_info["id"]:
                                c.is_resting = True
                                self._log(f"{c.name} was rested")
                                break

            elif action == "add_to_hand_from_trash" or action == "add_from_trash_to_hand":
                # Add selected card from trash to hand
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])
                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    for c in list(player.trash):
                        if c.id == target_info["id"]:
                            player.trash.remove(c)
                            player.hand.append(c)
                            self._log(f"{c.name} was added to hand from trash")
                            break

            elif action == "negate_effects":
                # Negate effects of selected target
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])
                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    opponent = self.player2 if player == self.player1 else self.player1
                    for c in opponent.cards_in_play:
                        if c.id == target_info["id"]:
                            c.effects_negated_this_turn = True
                            self._log(f"{c.name}'s effects were negated")
                            break

            # If a new pending choice was set during action processing (chained effects,
            # e.g. Law returns a character then immediately prompts to play one),
            # preserve it. Otherwise clear to None.
            if self.pending_choice is choice:
                # Nothing new was set — clear normally
                self.pending_choice = None

                # If there are queued counter effects, process the next one
                queued = getattr(self, '_queued_counter_effects', [])
                if queued:
                    defender_player, counter_card = queued.pop(0)
                    from .effects.effect_registry import execute_hardcoded_effect
                    execute_hardcoded_effect(self, defender_player, counter_card, 'counter')

                # If all counter effects resolved and attack resolution was deferred, do it now
                if (not self.pending_choice
                        and self.pending_attack
                        and self.pending_attack.get('_needs_attack_resolution')):
                    self.pending_attack.pop('_needs_attack_resolution', None)
                    self._resolve_attack_damage()

                # Resume combat paused for on_life_zero pending choice
                if (not self.pending_choice
                        and self.pending_attack
                        and self.pending_attack.get('life_zero_pending')):
                    self.pending_attack.pop('life_zero_pending')
                    lz_life_card = self.pending_attack.pop('life_zero_lc')
                    lz_has_trigger = self.pending_attack.pop('life_zero_ht')
                    lz_attack = self.pending_attack
                    lz_o = lz_attack['defender_player']
                    lz_attacker = lz_attack['attacker']
                    lz_has_banish = lz_attack.get('has_banish', False)
                    lz_paused = self._handle_life_card(lz_o, lz_life_card, lz_has_trigger, lz_has_banish, lz_attacker)
                    if not lz_paused:
                        self._continue_after_life_card()

            # else: a new choice was set during processing — leave it in place
            return True

        except Exception as e:
            import traceback
            print(f"Error resolving choice: {e}")
            traceback.print_exc()
            self.pending_choice = None
            return False
