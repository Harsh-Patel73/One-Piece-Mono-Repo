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
    callback_action: Optional[str] = None  # Action to perform: "trash", "play", "return_to_hand", etc.
    callback_data: Dict[str, Any] = field(default_factory=dict)  # Additional data for the callback

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
        if not getattr(self.leader, 'cannot_unrest', False):
            self.leader.is_resting = False
        else:
            # Clear the one-time prevention flag after it takes effect
            self.leader.cannot_unrest = False
            print(f"{self.leader.name} cannot be set to Active this turn")
        self.leader.has_attacked = False
        for attr in list(vars(self.leader).keys()):
            if attr.endswith('_used'):
                setattr(self.leader, attr, False)

        # Unrest all characters and return attached DON
        for c in self.cards_in_play:
            # Check if this card is prevented from unresting
            if not getattr(c, 'cannot_unrest', False):
                c.is_resting = False
            else:
                # Clear the one-time prevention flag after it takes effect
                c.cannot_unrest = False
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
        from .effects.hardcoded import has_hardcoded_effect, execute_hardcoded_effect
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
        self.opponent_player.cannot_add_life = False
        self.opponent_player.cannot_add_life_to_hand_this_turn = False

        # Hand limit removed - players can have unlimited cards in hand

    def _apply_continuous_effects(self):
        """Apply continuous/passive effects at the start of the Main phase.

        Called once per turn after clearing. Both players' cards are checked:
        handlers use `game_state.current_player is player` to determine
        whether it's 'Your Turn' or 'Opponent's Turn'.
        """
        from .effects.hardcoded import has_hardcoded_effect, execute_hardcoded_effect
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
                    card.has_doubleattack = has_innate
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

    def _trigger_on_play_effects(self, card: Card):
        """Trigger On Play effects for a card using the effect system."""
        if not card.effect:
            return

        print(f"[DEBUG] _trigger_on_play_effects: {card.id} - {card.name}")

        # First try hardcoded handlers (for cards with complex effects)
        executed = trigger_effect(card.id, self, card)
        print(f"[DEBUG] Hardcoded executed: {executed}")

        # ONLY parse and resolve effects if hardcoded handler didn't execute
        # This prevents duplicate execution (e.g., "Draw 2" happening twice)
        if not executed:
            print(f"[DEBUG] Running parser for {card.id}")
            effects = parse_effect(card.effect)
            for effect in effects:
                if effect.timing == EffectTiming.ON_PLAY:
                    print(f"[DEBUG] Parsed effect: {effect.effect_type}, timing: {effect.timing}")
                    # Create context and resolve
                    context = EffectContext(
                        game_state=self,
                        source_card=card,
                        source_player=self.current_player,
                        opponent=self.opponent_player,
                    )
                    resolver = get_resolver()
                    if resolver.can_resolve(effect, context):
                        result = resolver.resolve(effect, context)
                        print(f"[DEBUG] Resolved effect: {result.success}, {result.message}")
                        if result.success and result.message:
                            self._log(f"  [EFFECT] {result.message}")
        else:
            print(f"[DEBUG] Skipping parser - hardcoded already executed")

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
                if card.effect:
                    self._trigger_on_play_effects(card)
                # Fire on_event triggers (e.g. Crocodile leader: draw 1 when you activate Event)
                from .effects.hardcoded import has_hardcoded_effect, execute_hardcoded_effect
                if self.current_player.leader and has_hardcoded_effect(self.current_player.leader.id, 'on_event'):
                    execute_hardcoded_effect(self, self.current_player, self.current_player.leader, 'on_event')
            else:
                # CHARACTER and STAGE cards go to field
                self.current_player.cards_in_play.append(card)
                setattr(card, 'played_turn', self.turn_count)
                if card.card_type == "CHARACTER":
                    self.last_played_character = card

                # Apply keyword effects (Rush, Blocker, etc.)
                self._apply_keywords(card)

                self._log(f"{self.current_player.name} plays {card.name} (Cost {cost}), Remaining Active DON: {self.available_don()}")

                # Trigger On Play effects
                if card.effect and '[On Play]' in card.effect:
                    self._trigger_on_play_effects(card)
                from .effects.hardcoded import has_hardcoded_effect, execute_hardcoded_effect
                if card.card_type == "CHARACTER" and self.current_player.leader and has_hardcoded_effect(self.current_player.leader.id, 'on_play_character'):
                    execute_hardcoded_effect(self, self.current_player, self.current_player.leader, 'on_play_character')
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
            from .effects.hardcoded import has_hardcoded_effect, execute_hardcoded_effect
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

                    # Fire on_event for defender's leader (e.g. Crocodile OP01-062: draw 1 when you activate Event)
                    from .effects.hardcoded import has_hardcoded_effect as _has_he, execute_hardcoded_effect as _exec_he
                    if defender_player.leader and _has_he(defender_player.leader.id, 'on_event'):
                        _exec_he(self, defender_player, defender_player.leader, 'on_event')

                    # Check if card has a hardcoded counter effect
                    from .effects.hardcoded import has_hardcoded_effect
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
        from .effects.hardcoded import execute_hardcoded_effect
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
            from .effects.hardcoded import has_hardcoded_effect, execute_hardcoded_effect
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

        # Try hardcoded handler first (correct timing: "activate")
        from .handlers.effect_handlers import trigger_effect
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
        from .effects.hardcoded import has_hardcoded_effect as _has_hce
        leader_has_effect = bool(
            o.leader and _has_hce(o.leader.id, 'on_opponent_attack')
        )
        # Also capture any on_opponent_attack effects for fields cards — used in
        # the leader_effect step for now to keep things simple.

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
                    from .effects.hardcoded import has_hardcoded_effect, execute_hardcoded_effect
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

                # KO character
                o.cards_in_play.remove(defender)
                o.trash.append(defender)
                self._log(f"{attacker.name} KO's {defender.name}!")
                if getattr(attacker, 'set_active_on_ko', False) and not getattr(attacker, 'op02_094_used', False):
                    attacker._set_active_after_battle_resolution = True
                    attacker.op02_094_used = True

                # Trigger ON_KO effects
                effect_manager = get_effect_manager()
                effect_manager.on_ko(self, o, defender)

                # Trigger on_opponent_ko for the attacking player's leader (e.g. Kaido)
                from .effects.hardcoded import has_hardcoded_effect, execute_hardcoded_effect
                if p.leader and has_hardcoded_effect(p.leader.id, 'on_opponent_ko'):
                    execute_hardcoded_effect(self, p, p.leader, 'on_opponent_ko')

                self._finish_attack()
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
            from .effects.hardcoded import has_hardcoded_effect, execute_hardcoded_effect
            card_was_played = False
            hardcoded_ran = False
            if has_hardcoded_effect(life_card.id, "trigger"):
                hardcoded_ran = execute_hardcoded_effect(self, player, life_card, "trigger")
                if life_card in player.cards_in_play:
                    card_was_played = True

            # Fall back to parser-based trigger effects if no hardcoded handler
            if not hardcoded_ran:
                effect_manager = get_effect_manager()
                trigger_result = effect_manager.on_life_damage(self, player, life_card, False)
                if trigger_result[0] and trigger_result[1]:
                    if trigger_result[1].success and trigger_result[1].message:
                        self._log(f"    {trigger_result[1].message}")
                    if life_card in player.cards_in_play:
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
            'has_taunt': getattr(card, 'has_taunt', False),
        }

    # -----------------------------------------------------------------
    # DON return after-callback dispatch
    # -----------------------------------------------------------------
    def _dispatch_don_after_callback(self, player, after, after_data):
        """Run the card-specific follow-up after DON has been returned to deck."""
        if not after:
            return
        opponent = self.player2 if player == self.player1 else self.player1

        # --- OP01 callbacks ---
        if after == "op01_094_kaido_ko_all":
            src_id = after_data.get("source_card_id")
            leader_ok = 'animal kingdom pirates' in (player.leader.card_origin or '').lower() if player.leader else False
            if leader_ok:
                for c in opponent.cards_in_play[:]:
                    opponent.cards_in_play.remove(c)
                    opponent.trash.append(c)
                    self._log(f"  {c.name} K.O.'d")
                for c in player.cards_in_play[:]:
                    if c.id != src_id:
                        player.cards_in_play.remove(c)
                        player.trash.append(c)
                        self._log(f"  {c.name} K.O.'d")

        elif after == "op01_096_king_ko":
            from .effects.hardcoded import create_ko_choice
            targets_3 = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
            if targets_3:
                create_ko_choice(
                    self, player, targets_3, source_card=None,
                    prompt="Choose opponent's cost 3 or less Character to K.O.",
                    callback_action="king_ko_then_2",
                    callback_data={"player_id": player.player_id},
                )

        elif after == "op01_097_queen_rush_power":
            src_id = after_data.get("source_card_id")
            src = next((c for c in player.cards_in_play if c.id == src_id), None)
            if src:
                src.has_rush = True
                self._log(f"  {src.name} gained [Rush]")
            targets = [c for c in opponent.cards_in_play]
            if targets:
                from .effects.hardcoded import create_power_effect_choice
                create_power_effect_choice(
                    self, player, targets, -2000,
                    source_card=src, prompt="Choose opponent's Character to give -2000 power"
                )

        elif after == "op01_108_kamazo_ko":
            from .effects.hardcoded import create_ko_choice
            targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 5]
            if targets:
                create_ko_choice(
                    self, player, targets, source_card=None,
                    prompt="Choose opponent's cost 5 or less Character to K.O.",
                )

        elif after == "op01_111_blackmaria_power":
            src_id = after_data.get("source_card_id")
            src = next((c for c in player.cards_in_play if c.id == src_id), None)
            if src:
                src.power_modifier = getattr(src, 'power_modifier', 0) + 1000
                self._log(f"  {src.name} gained +1000 power")

        elif after == "op01_112_pageone_active":
            src_id = after_data.get("source_card_id")
            src = next((c for c in player.cards_in_play if c.id == src_id), None)
            if src:
                src.can_attack_active = True
                self._log(f"  {src.name} can now attack active Characters")

        elif after == "op01_117_sheeps_horn_rest":
            from .effects.hardcoded import create_rest_choice
            targets = [c for c in opponent.cards_in_play
                       if (getattr(c, 'cost', 0) or 0) <= 6 and not getattr(c, 'is_resting', False)]
            if targets:
                create_rest_choice(
                    self, player, targets, source_card=None,
                    prompt="Choose opponent's cost 6 or less Character to rest",
                )

        elif after == "op01_118_ulti_mortar_power":
            from .effects.hardcoded import create_power_effect_choice, draw_cards
            draw_cards(player, 1)
            self._log(f"Ulti-Mortar: {player.name} draws 1 card")
            targets = ([player.leader] if player.leader else []) + player.cards_in_play
            if targets:
                create_power_effect_choice(
                    self, player, targets, 2000,
                    source_card=None,
                    prompt="Choose Leader or Character to give +2000 power",
                )

        # --- OP02 callbacks ---
        elif after == "op02_072_zephyr_effect":
            # OP02-072: +1000 power to leader, KO opponent's cost 3 or less
            src_id = after_data.get("source_card_id")
            src = next((c for c in ([player.leader] if player.leader else []) + player.cards_in_play
                        if c.id == src_id), None)
            if src:
                src.power_modifier = getattr(src, 'power_modifier', 0) + 1000
                self._log(f"  {src.name} gained +1000 power")
            from .effects.hardcoded import create_ko_choice
            targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
            if targets:
                create_ko_choice(
                    self, player, targets, source_card=src,
                    prompt="Choose opponent's cost 3 or less Character to KO",
                )

        elif after == "op02_076_shiryu_effect":
            # OP02-076: KO opponent's cost 1 or less
            from .effects.hardcoded import create_ko_choice
            targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 1]
            if targets:
                create_ko_choice(
                    self, player, targets, source_card=None,
                    prompt="Choose opponent's cost 1 or less to KO",
                )

        elif after == "op02_078_daifugo_effect":
            # OP02-078: Play SMILE cost 3 or less from hand
            from .effects.hardcoded import create_play_from_hand_choice
            playable = [c for c in player.hand
                        if (getattr(c, 'card_type', '') == 'CHARACTER' and
                            'SMILE' in (c.card_origin or '') and
                            (getattr(c, 'cost', 0) or 0) <= 3 and
                            getattr(c, 'name', '') != 'Daifugo')]
            if playable:
                create_play_from_hand_choice(
                    self, player, playable,
                    source_card=None,
                    prompt="Choose SMILE cost 3 or less to play",
                )

        elif after == "op02_079_bullet_effect":
            # OP02-079: Rest opponent's cost 4 or less
            from .effects.hardcoded import create_rest_choice
            targets = [c for c in opponent.cards_in_play
                       if (getattr(c, 'cost', 0) or 0) <= 4 and not getattr(c, 'is_resting', False)]
            if targets:
                create_rest_choice(
                    self, player, targets, source_card=None,
                    prompt="Choose opponent's cost 4 or less to rest",
                )

        elif after == "op02_082_world_effect":
            # OP02-082: +792000 power
            src_id = after_data.get("source_card_id")
            src = next((c for c in player.cards_in_play if c.id == src_id), None)
            if src:
                src.power_modifier = getattr(src, 'power_modifier', 0) + 792000
                src._sticky_power_modifier = getattr(src, '_sticky_power_modifier', 0) + 792000
                self._log(f"  {src.name} gained +792000 power")

        elif after == "op02_085_magellan_effect":
            # OP02-085: Opponent returns 1 DON
            if opponent.don_pool:
                opponent.don_pool.pop()
                self._log(f"  Opponent returned 1 DON!! to DON deck")

        elif after == "op02_089_judgment_effect":
            # OP02-089: Give up to 2 opponent leader/chars -3000 power each
            from .effects.hardcoded import create_power_effect_choice
            targets = ([opponent.leader] if opponent.leader else []) + opponent.cards_in_play
            if targets:
                create_power_effect_choice(
                    self, player, targets, -3000,
                    source_card=None,
                    prompt="Judgment of Hell: Choose up to 2 opponent Leader/Characters to give -3000 power",
                    min_selections=0, max_selections=2,
                )

        elif after == "op02_090_hydra_effect":
            # OP02-090: Give up to 1 opponent's character -3000 power
            from .effects.hardcoded import create_power_effect_choice
            targets = opponent.cards_in_play[:]
            if targets:
                create_power_effect_choice(
                    self, player, targets, -3000, source_card=None,
                    prompt="Hydra: Choose up to 1 opponent Character to give -3000 power",
                    min_selections=0, max_selections=1,
                )

        elif after == "op02_120_uta_effect":
            # OP02-120: Leader and all Characters +1000 until next turn
            expire_turn = self.turn_count + 1
            if player.leader:
                player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 1000
                player.leader._sticky_power_modifier = getattr(player.leader, '_sticky_power_modifier', 0) + 1000
                player.leader.power_modifier_expires_on_turn = expire_turn
                player.leader._sticky_power_modifier_expires_on_turn = expire_turn
            for c in player.cards_in_play:
                c.power_modifier = getattr(c, 'power_modifier', 0) + 1000
                c._sticky_power_modifier = getattr(c, '_sticky_power_modifier', 0) + 1000
                c.power_modifier_expires_on_turn = expire_turn
                c._sticky_power_modifier_expires_on_turn = expire_turn
            self._log(f"  Leader and all Characters gained +1000 power")

        # --- OP03 callbacks ---
        elif after == "op03_022_play_trigger":
            # OP03-022 Arlong: Play cost 4 or less Character with Trigger from hand
            from .effects.hardcoded import create_play_from_hand_choice
            playable = [c for c in player.hand
                        if getattr(c, 'card_type', '') == 'CHARACTER'
                        and (getattr(c, 'cost', 0) or 0) <= 4
                        and getattr(c, 'trigger', '')]
            if playable:
                create_play_from_hand_choice(
                    self, player, playable, source_card=None,
                    prompt="Arlong: Choose a cost 4 or less Character with Trigger to play")

        elif after == "op03_058_play_galley_la":
            # OP03-058 Iceburg: Play Galley-La cost 5 or less from hand
            from .effects.hardcoded import create_play_from_hand_choice
            galley_la = [c for c in player.hand
                         if getattr(c, 'card_type', '') == 'CHARACTER'
                         and 'Galley-La Company' in (c.card_origin or '')
                         and (getattr(c, 'cost', 0) or 0) <= 5]
            if galley_la:
                create_play_from_hand_choice(
                    self, player, galley_la, source_card=None,
                    prompt="Iceburg: Choose a Galley-La cost 5 or less Character to play")

        elif after == "op03_059_banish":
            # OP03-059 Kaku: Gain Banish
            src_id = after_data.get("source_card_id")
            src = next((c for c in player.cards_in_play if c.id == src_id), None)
            if src:
                src.has_banish = True
                self._log(f"  {src.name} gained [Banish]")

        elif after == "op03_060_draw_trash":
            # OP03-060 Kalifa: Draw 2, trash 1
            from .effects.hardcoded import draw_cards, trash_from_hand
            draw_cards(player, 2)
            trash_from_hand(player, 1, self, None)
            self._log(f"  Kalifa: Draw 2, trash 1")

        elif after == "op03_063_draw":
            # OP03-063 Zambai: If Water Seven leader, draw 1
            if player.leader and 'Water Seven' in (player.leader.card_origin or ''):
                from .effects.hardcoded import draw_cards
                draw_cards(player, 1)
                self._log(f"  Zambai: Draw 1")

        elif after == "op03_070_rush":
            # OP03-070 Luffy: Trash cost 5 Character from hand, gain Rush
            src_id = after_data.get("source_card_id")
            src = next((c for c in player.cards_in_play if c.id == src_id), None)
            cost5 = [c for c in player.hand
                     if getattr(c, 'card_type', '') == 'CHARACTER'
                     and (getattr(c, 'cost', 0) or 0) == 5]
            if cost5 and src:
                from .effects.hardcoded import create_hand_discard_choice
                create_hand_discard_choice(
                    self, player, cost5, source_card=src,
                    callback_action="op03_070_grant_rush",
                    prompt="Luffy: Choose a cost 5 Character to trash for Rush")

        elif after == "op03_071_rest":
            # OP03-071 Rob Lucci: Rest opponent's cost 5 or less
            from .effects.hardcoded import create_rest_choice
            targets = [c for c in opponent.cards_in_play
                       if (getattr(c, 'cost', 0) or 0) <= 5
                       and not getattr(c, 'is_resting', False)]
            if targets:
                create_rest_choice(
                    self, player, targets, source_card=None,
                    prompt="Rob Lucci: Choose opponent's cost 5 or less to rest")

        elif after == "op03_073_draw":
            # OP03-073 Hull Dismantler Slash: Draw 1
            from .effects.hardcoded import draw_cards
            draw_cards(player, 1)
            self._log(f"  Hull Dismantler Slash: Draw 1")

        elif after == "op03_074_bottom_deck":
            # OP03-074 Top Knot: Place opponent's cost 4 or less at bottom
            from .effects.hardcoded import create_bottom_deck_choice
            targets = [c for c in opponent.cards_in_play
                       if (getattr(c, 'cost', 0) or 0) <= 4]
            if targets:
                create_bottom_deck_choice(
                    self, player, targets, source_card=None,
                    prompt="Top Knot: Choose opponent's cost 4 or less to place at bottom of deck")

        elif after == "op03_077_life":
            # OP03-077 Charlotte Linlin: If 1 or less life, add deck card to life
            if len(player.life_cards) <= 1 and player.deck:
                deck_card = player.deck.pop(0)
                player.life_cards.append(deck_card)
                self._log(f"  Charlotte Linlin: Added 1 card from deck to Life")

    def _trigger_on_don_return_effects(self, player: Player):
        """Fire leader effects that care about DON!! returning to the DON!! deck."""
        from .effects.hardcoded import has_hardcoded_effect, execute_hardcoded_effect
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
            if action == "trash_from_hand":
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
                        player.cards_in_play.append(chosen_card)
                        setattr(chosen_card, 'played_turn', self.turn_count)
                        if play_rested:
                            chosen_card.is_resting = True
                        self._apply_keywords(chosen_card)
                        self._log(f"{source_name}: Played {chosen_card.name} to field")
                        # Trigger on-play effects for the played card
                        if chosen_card.effect and '[On Play]' in chosen_card.effect:
                            self._trigger_on_play_effects(chosen_card)
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
                                p.cards_in_play.remove(c)
                                p.trash.append(c)
                                self._log(f"{c.name} was KO'd")
                                break

            elif action == "op03_001_trash_for_power":
                # OP03-001 Ace Leader: Trash selected Event/Stage cards, gain +1000 per card
                target_cards = data.get("target_cards", [])
                src_id = data.get("source_card_id", "")
                src_card = (player.leader if player.leader and player.leader.id == src_id
                            else next((c for c in player.cards_in_play if c.id == src_id), None))
                power_gained = 0
                for sel in selected:
                    target_idx = int(sel)
                    if 0 <= target_idx < len(target_cards):
                        target_info = target_cards[target_idx]
                        for c in player.hand[:]:
                            if c.id == target_info["id"]:
                                player.hand.remove(c)
                                player.trash.append(c)
                                power_gained += 1000
                                self._log(f"{player.name} trashed {c.name} for +1000 power")
                                break
                if src_card and power_gained > 0:
                    src_card.power_modifier = getattr(src_card, 'power_modifier', 0) + power_gained
                    src_card._sticky_power_modifier = getattr(src_card, '_sticky_power_modifier', 0) + power_gained
                    self._log(f"{src_card.name} gains +{power_gained} power this turn")

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
                        from .effects.hardcoded import draw_cards
                        draw_cards(player, draw_after)
                    if power_boost_card_id and power_boost_amount:
                        boost_card = (next((c for c in player.cards_in_play if c.id == power_boost_card_id), None)
                                      or (player.leader if player.leader and player.leader.id == power_boost_card_id else None))
                        if boost_card:
                            boost_card.power_modifier = getattr(boost_card, 'power_modifier', 0) + power_boost_amount
                            boost_card._sticky_power_modifier = getattr(boost_card, '_sticky_power_modifier', 0) + power_boost_amount
                            self._log(f"{boost_card.name} gains +{power_boost_amount} power")

            elif action == "op03_013_ko_after_trash":
                # OP03-013 Marco on_play: Player trashed an Event from hand, now KO opponent's 3000 or less
                indices = sorted([int(s) for s in selected], reverse=True) if selected else []
                target_cards = data.get("target_cards", [])
                for idx in indices:
                    if 0 <= idx < len(target_cards):
                        target_info = target_cards[idx]
                        for c in player.hand[:]:
                            if c.id == target_info["id"]:
                                player.hand.remove(c)
                                player.trash.append(c)
                                self._log(f"{player.name} trashed {c.name} from hand")
                                break
                opponent = self.player2 if player == self.player1 else self.player1
                ko_targets = [c for c in opponent.cards_in_play
                              if (getattr(c, 'power', 0) or 0) + getattr(c, 'power_modifier', 0) <= 3000]
                if ko_targets:
                    from .effects.hardcoded import create_ko_choice
                    create_ko_choice(self, player, ko_targets, source_card=None,
                                    prompt="Marco: Choose opponent's 3000 power or less Character to K.O.")

            elif action == "op03_013_return_after_trash":
                # OP03-013 Marco on_ko: Player trashed an Event, now return Marco to play rested
                target_cards = data.get("target_cards", [])
                marco_id = data.get("marco_id", "")
                indices = sorted([int(s) for s in selected], reverse=True) if selected else []
                for idx in indices:
                    if 0 <= idx < len(target_cards):
                        target_info = target_cards[idx]
                        for c in player.hand[:]:
                            if c.id == target_info["id"]:
                                player.hand.remove(c)
                                player.trash.append(c)
                                self._log(f"{player.name} trashed {c.name} from hand")
                                break
                # Find and return Marco from trash to field
                for c in player.trash[:]:
                    if c.id == marco_id:
                        player.trash.remove(c)
                        player.cards_in_play.append(c)
                        c.is_resting = True
                        self._log(f"{c.name} returns to field rested")
                        break

            elif action == "op03_016_ko_then_boost":
                # OP03-016 Flame Emperor: KO target then boost leader +3000 and double attack
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])
                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    opponent = self.player2 if player == self.player1 else self.player1
                    for c in opponent.cards_in_play[:]:
                        if c.id == target_info["id"]:
                            opponent.cards_in_play.remove(c)
                            opponent.trash.append(c)
                            self._log(f"{c.name} was K.O.'d by Flame Emperor")
                            break
                # Give leader +3000 and Double Attack for this turn
                if player.leader:
                    player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 3000
                    player.leader._sticky_power_modifier = getattr(player.leader, '_sticky_power_modifier', 0) + 3000
                    player.leader.has_doubleattack = True
                    player.leader._temp_doubleattack = True
                    self._log(f"{player.leader.name} gains +3000 power and [Double Attack] this turn")

            elif action == "op03_018_ko_4000_after":
                # OP03-018 Fire Fist: After KO'ing 5000 or less, now prompt to KO 4000 or less
                # First do the KO of the selected 5000-or-less target
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])
                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    opponent = self.player2 if player == self.player1 else self.player1
                    for c in opponent.cards_in_play[:]:
                        if c.id == target_info["id"]:
                            opponent.cards_in_play.remove(c)
                            opponent.trash.append(c)
                            self._log(f"{c.name} was K.O.'d by Fire Fist (5000 or less)")
                            break
                # Now prompt for 4000 or less
                opponent = self.player2 if player == self.player1 else self.player1
                ko_targets2 = [c for c in opponent.cards_in_play
                               if (getattr(c, 'power', 0) or 0) + getattr(c, 'power_modifier', 0) <= 4000]
                if ko_targets2:
                    from .effects.hardcoded import create_ko_choice
                    create_ko_choice(self, player, ko_targets2, source_card=None,
                                    prompt="Fire Fist: Choose opponent's 4000 power or less Character to K.O.")

            elif action == "op03_025_ko_after_trash":
                # OP03-025 Krieg: Player trashed a card, now KO up to 2 rested cost 4 or less
                indices = sorted([int(s) for s in selected], reverse=True) if selected else []
                target_cards = data.get("target_cards", [])
                for idx in indices:
                    if 0 <= idx < len(target_cards):
                        target_info = target_cards[idx]
                        for c in player.hand[:]:
                            if c.id == target_info["id"]:
                                player.hand.remove(c)
                                player.trash.append(c)
                                self._log(f"{player.name} trashed {c.name} from hand")
                                break
                opponent = self.player2 if player == self.player1 else self.player1
                ko_targets = [c for c in opponent.cards_in_play
                              if (getattr(c, 'cost', 0) or 0) <= 4 and getattr(c, 'is_resting', False)]
                if ko_targets:
                    from .effects.hardcoded import create_ko_choice, PendingChoice as _PC
                    import uuid as _uuid
                    opts = []
                    for i, c in enumerate(ko_targets):
                        opts.append({"id": str(i), "label": f"{c.name} (Cost {c.cost or 0})",
                                     "card_id": c.id, "card_name": c.name})
                    self.pending_choice = _PC(
                        choice_id=f"krieg_ko_{_uuid.uuid4().hex[:8]}",
                        choice_type="select_target",
                        prompt="Krieg: Choose up to 2 rested cost 4 or less Characters to K.O.",
                        options=opts, min_selections=0, max_selections=2,
                        callback_action="ko_multi_targets",
                        callback_data={"player_id": player.player_id,
                                       "target_cards": [{"id": c.id, "name": c.name} for c in ko_targets]},
                    )

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

            elif action == "op03_039_power_after_rest":
                # OP03-039 One Two Jango: After resting opponent's cost 1 or less, give own char +1000
                target_cards = data.get("target_cards", [])
                opponent = self.player2 if player == self.player1 else self.player1
                for sel in selected:
                    target_idx = int(sel)
                    if 0 <= target_idx < len(target_cards):
                        target_info = target_cards[target_idx]
                        for c in opponent.cards_in_play:
                            if c.id == target_info["id"]:
                                c.is_resting = True
                                self._log(f"{c.name} was rested")
                                break
                # Now prompt to give +1000 to an own character
                own_chars = list(player.cards_in_play)
                if player.leader:
                    own_chars.append(player.leader)
                if own_chars:
                    from .effects.hardcoded import create_power_effect_choice
                    create_power_effect_choice(game_state=self, player=player, targets=own_chars, power_amount=1000,
                                              source_card=None, prompt="One, Two, Jango: Choose 1 of your cards to give +1000 power",
                                              min_selections=0, max_selections=1)

            elif action == "king_ko_then_2":
                # OP01-096 King: KO the selected cost-3-or-less target, then prompt for cost 2 or less
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])
                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    opponent = self.player2 if player == self.player1 else self.player1
                    for p in [player, opponent]:
                        for c in p.cards_in_play[:]:
                            if c.id == target_info["id"]:
                                p.cards_in_play.remove(c)
                                p.trash.append(c)
                                self._log(f"{c.name} was KO'd")
                                break
                # Now prompt for cost 2 or less
                opponent = self.player2 if player == self.player1 else self.player1
                targets_2 = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
                if targets_2:
                    from .effects.hardcoded import create_ko_choice
                    create_ko_choice(
                        self, player, targets_2, source_card=None,
                        prompt="Choose opponent's cost 2 or less Character to K.O.",
                    )

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
                                c.is_resting = rest_on_play
                                player.cards_in_play.append(c)
                                self._log(f"{player.name} played {c.name} from trash")
                                break

            elif action == "select_mode":
                # Handle mode selection for multi-choice effects
                selected_mode = selected[0] if selected else None
                card_id = data.get("card_id")
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
                    from .effects.hardcoded import return_opponent_to_hand
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
                    from .effects.hardcoded import draw_cards
                    if card_id and "OP12-060" in card_id:  # Boeuf Burst
                        draw_cards(player, 2)
                        self._log(f"{player.name} drew 2 cards")
                    elif card_id and "EB02-045" in card_id:  # Law
                        draw_cards(player, 1)
                        self._log(f"{player.name} drew 1 card")

                elif selected_mode == "ko":
                    # KO opponent's character
                    from .effects.hardcoded import ko_opponent_character
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
                        from .effects.hardcoded import trash_from_hand
                        trash_from_hand(opponent, 1, self, source_card)
                        self._log(f"{opponent.name} must discard 1 card")

                elif selected_mode == "cost_reduce":
                    # Apply -4 cost to opponent's character
                    from .effects.hardcoded import create_power_effect_choice
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

            elif action == "jozu_return_own":
                # Jozu: You may return own character, then return up to 1 cost 6 or less
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])
                jozu_card_id = choice.source_card_id  # Track Jozu to exclude from step 2

                if not selected or target_idx < 0:
                    # Player chose to skip - no cost paid, no second effect
                    self._log(f"{player.name} chose not to use Jozu's effect")
                elif 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    # Find and return the character
                    for c in player.cards_in_play[:]:
                        if c.id == target_info["id"]:
                            player.cards_in_play.remove(c)
                            player.hand.append(c)
                            self._log(f"{player.name} returned {c.name} to hand")
                            break

                    # Now trigger the second part: return up to 1 cost 6 or less to owner's hand
                    from .effects.hardcoded import create_return_to_hand_choice
                    self.pending_choice = None
                    opponent = self.player2 if player == self.player1 else self.player1
                    # Combine both players' characters (cost 6 or less), exclude Jozu
                    all_targets = []
                    for c in player.cards_in_play:
                        if (getattr(c, 'cost', 0) or 0) <= 6 and c.id != jozu_card_id:
                            all_targets.append(c)
                    for c in opponent.cards_in_play:
                        if (getattr(c, 'cost', 0) or 0) <= 6:
                            all_targets.append(c)
                    if all_targets:
                        return create_return_to_hand_choice(
                            self, player, all_targets, source_card=None,
                            prompt="Return up to 1 cost 6 or less Character to owner's hand",
                            optional=True
                        )

            elif action == "brilliant_punk_return":
                # Brilliant Punk: Return own character, then return opponent's cost 6 or less
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])

                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    # Find and return the character
                    for c in player.cards_in_play[:]:
                        if c.id == target_info["id"]:
                            player.cards_in_play.remove(c)
                            player.hand.append(c)
                            self._log(f"{player.name} returned {c.name} to hand")
                            break

                    # Now trigger the second part: return opponent's cost 6 or less
                    from .effects.hardcoded import return_opponent_to_hand
                    self.pending_choice = None
                    return return_opponent_to_hand(self, player, max_cost=6, source_card=None)

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

            elif action == "law_return_then_play_cost3":
                # Law OP01-047: return a character to hand, then play cost 3 or less
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])
                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    for c in player.cards_in_play[:]:
                        if c.id == target_info["id"]:
                            player.cards_in_play.remove(c)
                            player.hand.append(c)
                            self._log(f"Law: {player.name} returned {c.name} to hand")
                            break
                # Now offer to play a cost 3 or less Character from hand
                from .effects.hardcoded import create_play_from_hand_choice
                playable = [c for c in player.hand
                            if getattr(c, 'card_type', '') == 'CHARACTER'
                            and (getattr(c, 'cost', 0) or 0) <= 3]
                if playable:
                    create_play_from_hand_choice(
                        self, player, playable,
                        prompt="Law: Choose a cost 3 or less Character to play from hand"
                    )

            elif action == "apply_cost_reduction":
                # Apply cost reduction to selected character
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])
                cost_reduction = data.get("cost_reduction", 0)

                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    opponent = self.player2 if player == self.player1 else self.player1

                    # Find the target (usually opponent's character)
                    for p in [opponent, player]:
                        for c in p.cards_in_play:
                            if c.id == target_info["id"]:
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
                                c.is_resting = rest_on_play
                                setattr(c, 'played_turn', self.turn_count)
                                player.cards_in_play.append(c)
                                self._apply_keywords(c)
                                self._log(f"{player.name} played {c.name} from hand")
                                # Trigger on_play effects for the played card
                                if c.effect and '[On Play]' in c.effect:
                                    self._trigger_on_play_effects(c)
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

            elif action == "bottom_deck_then_draw":
                # Move selected card from player's hand to bottom of deck, then draw 1.
                # If player skipped (empty selection), neither placement nor draw occurs.
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])
                placed = False
                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    for c in player.hand[:]:
                        if c.id == target_info["id"]:
                            player.hand.remove(c)
                            player.deck.append(c)
                            self._log(f"{player.name} placed {c.name} at bottom of deck")
                            placed = True
                            break
                if placed and player.deck:
                    drawn = player.deck.pop(0)
                    player.hand.append(drawn)
                    self._log(f"{player.name} drew a card")

            elif action == "chopper_trash_then_pick_shc":
                # Step 1: trash chosen hand card (optional — empty selected = skip)
                hand_cards = data.get("hand_cards", [])
                if selected:
                    target_idx = int(selected[0]) if selected[0].isdigit() else -1
                    if 0 <= target_idx < len(hand_cards):
                        target_info = hand_cards[target_idx]
                        for c in player.hand[:]:
                            if c.id == target_info["id"]:
                                player.hand.remove(c)
                                player.trash.append(c)
                                self._log(f"{player.name} trashed {c.name}")
                                break
                # Step 2: offer SHC cost 4 or less from trash (excluding Chopper itself)
                shc = [c for c in player.trash
                       if c.card_type == 'CHARACTER'
                       and 'straw hat crew' in (c.card_origin or '').lower()
                       and (c.cost or 0) <= 4
                       and 'tony tony.chopper' not in (c.name or '').lower()]
                if shc:
                    options = [{"id": str(i), "label": f"{c.name} (Cost: {c.cost or 0})",
                                "card_id": c.id, "card_name": c.name} for i, c in enumerate(shc)]
                    self.pending_choice = PendingChoice(
                        choice_id=f"chopper_shc_{__import__('uuid').uuid4().hex[:8]}",
                        choice_type="select_target",
                        prompt="Choose a Straw Hat Crew Character (cost 4 or less) from trash to add to hand",
                        options=options,
                        min_selections=0,
                        max_selections=1,
                        source_card_id=None,
                        source_card_name="Tony Tony.Chopper",
                        callback_action="return_from_trash_to_hand",
                        callback_data={"player_id": player.player_id,
                                       "target_cards": [{"id": c.id, "name": c.name} for c in shc]},
                    )
                else:
                    self._log("No Straw Hat Crew characters (cost 4 or less) in trash")

            elif action == "nami_pick_shc":
                # Legacy handler — redirect to nami_shc_add logic for backward compat
                pass

            elif action == "nami_shc_add":
                # Nami on-play: top5_count cards are at the top of the deck.
                # Move chosen valid card (if any) to hand; then let player order remaining to bottom.
                top5_count = data.get("top5_count", 5)
                valid_indices = data.get("valid_indices", [])

                chosen_idx = int(selected[0]) if selected else -1

                # Remove chosen card from deck to hand (by position, avoids duplicate-id issues)
                chosen_card = None
                if chosen_idx >= 0 and chosen_idx in valid_indices and chosen_idx < len(player.deck):
                    chosen_card = player.deck.pop(chosen_idx)
                    player.hand.append(chosen_card)
                    self._log(f"Nami: Added {chosen_card.name} to hand")

                # Pull remaining top cards out of deck for ordering
                remaining_count = top5_count - (1 if chosen_card else 0)
                remaining = player.deck[:remaining_count]
                for _ in range(remaining_count):
                    player.deck.pop(0)

                # If 0-1 cards, just place directly; otherwise let player choose order
                if len(remaining) <= 1:
                    player.deck.extend(remaining)
                    self._log("Nami: Remaining cards placed at bottom of deck")
                else:
                    # Start sequential ordering choice
                    self._create_deck_order_choice(
                        player, remaining, [],
                        source_name="Nami",
                        source_id="OP01-016",
                    )

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

            elif action == "two_years_pick_shc":
                # Same deck manipulation pattern as nami_pick_shc.
                # Top-5 cards were appended to END of deck; move chosen SHC Character to hand.
                top5_ids = data.get("top5_ids", [])
                chosen_id = selected[0] if selected else None
                if chosen_id:
                    for c in player.deck[::-1]:
                        if c.id == chosen_id and c.id in top5_ids:
                            player.deck.remove(c)
                            player.hand.append(c)
                            self._log(f"In Two Years!!: Added {c.name} to hand")
                            break
                self._log("In Two Years!!: Remaining cards placed at bottom of deck")

            elif action == "oden_trash_wano":
                # Trash the selected Land of Wano card, then set up to 2 rested DON active.
                wano_cards_data = data.get("wano_cards", [])
                chosen_idx = int(selected[0]) if selected else -1
                if 0 <= chosen_idx < len(wano_cards_data):
                    chosen_info = wano_cards_data[chosen_idx]
                    # Find card in hand by ID
                    for c in player.hand:
                        if c.id == chosen_info["id"]:
                            player.hand.remove(c)
                            player.trash.append(c)
                            self._log(f"Kouzuki Oden: Trashed {c.name}")
                            break
                # Set up to 2 rested DON as active
                activated = 0
                for i, don_status in enumerate(player.don_pool):
                    if don_status == "rested" and activated < 2:
                        player.don_pool[i] = "active"
                        activated += 1
                if activated:
                    self._log(f"Kouzuki Oden: Set {activated} DON!! as active")

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
                    opponent = self.player2 if player == self.player1 else self.player1
                    for c in opponent.cards_in_play[:]:
                        if c.id == target_info["id"]:
                            opponent.cards_in_play.remove(c)
                            opponent.life_cards.append(c)
                            self._log(f"{c.name} was added to opponent's Life")
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
                            player.cards_in_play.append(c)
                            self._log(f"{c.name} was played from hand")
                            break
                    else:
                        for c in list(player.trash):
                            if c.id == target_info["id"]:
                                player.trash.remove(c)
                                player.cards_in_play.append(c)
                                self._log(f"{c.name} was played from trash")
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
                    for c in opponent.cards_in_play:
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

            elif action == "set_active_with_power":
                # Set active and give power boost
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])
                power = data.get("power", 1000)
                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    for c in player.cards_in_play:
                        if c.id == target_info["id"]:
                            c.is_resting = False
                            c.has_attacked = False  # Reset so card can attack again this turn
                            c.power_modifier = getattr(c, 'power_modifier', 0) + power
                            self._log(f"{c.name} was set active and gained +{power} power")
                            break

            elif action == "protect_from_ko_in_battle":
                # Set cannot_be_ko_in_battle on selected own character (Yasakani Sacred Jewel)
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])
                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    for c in player.cards_in_play:
                        if c.id == target_info["id"]:
                            c.cannot_be_ko_in_battle = True
                            c._ko_protected_for_attack = True
                            self._log(f"{c.name} cannot be K.O.'d in battle this turn")
                            break

            elif action == "slave_arrow_return":
                # Return own character to hand, then give leader +4000 power
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])
                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    for c in player.cards_in_play[:]:
                        if c.id == target_info["id"]:
                            player.cards_in_play.remove(c)
                            player.hand.append(c)
                            self._log(f"{c.name} returned to hand")
                            if player.leader:
                                player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 4000
                                self._log(f"Leader gained +4000 power")
                            break

            elif action == "stussy_trash_then_ko":
                # Trash own character, then KO opponent's character
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])
                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    for c in player.cards_in_play[:]:
                        if c.id == target_info["id"]:
                            player.cards_in_play.remove(c)
                            player.trash.append(c)
                            self._log(f"{c.name} was trashed")
                            break
                    # Now trigger KO choice for opponent
                    opponent = self.player2 if player == self.player1 else self.player1
                    if opponent.cards_in_play:
                        from .effects.hardcoded import create_ko_choice
                        source_card_id = data.get("source_card_id")
                        source = None
                        for c in player.cards_in_play:
                            if c.id == source_card_id:
                                source = c
                                break
                        create_ko_choice(
                            self, player, opponent.cards_in_play, source_card=source,
                            prompt="Choose opponent's Character to KO"
                        )

            elif action == "ace_trash_for_power":
                # OP13-002 Ace Leader: Trash from hand, then give -2000 to opponent's Leader or Character
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])
                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    # Trash the selected card from hand
                    for c in player.hand[:]:
                        if c.id == target_info["id"]:
                            player.hand.remove(c)
                            player.trash.append(c)
                            self._log(f"{c.name} was trashed from hand")
                            break
                    # Mark Ace effect as used this turn
                    source_card_id = data.get("source_card_id")
                    if source_card_id and player.leader and player.leader.id == source_card_id:
                        player.leader.op13_002_used = True
                    # Now create choice for -2000 power target (Leader or Characters)
                    opponent = self.player2 if player == self.player1 else self.player1
                    power_targets = []
                    if opponent.leader:
                        power_targets.append(opponent.leader)
                    power_targets.extend(opponent.cards_in_play)
                    if power_targets:
                        from .effects.hardcoded import create_power_effect_choice
                        self.pending_choice = None
                        create_power_effect_choice(
                            self, player, power_targets, -2000,
                            source_card=None,
                            prompt="Choose opponent's Leader or Character to give -2000 power"
                        )

            elif action == "law_return_then_play_odyssey":
                # Return own character, then play ODYSSEY cost 3 or less
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])
                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    for c in player.cards_in_play[:]:
                        if c.id == target_info["id"]:
                            player.cards_in_play.remove(c)
                            player.hand.append(c)
                            self._log(f"{c.name} returned to hand")
                            break
                    # Now trigger play ODYSSEY choice
                    odyssey = [c for c in player.hand
                               if 'odyssey' in (getattr(c, 'card_types', '') or '').lower()
                               and (getattr(c, 'cost', 0) or 0) <= 3
                               and getattr(c, 'card_type', '') == 'CHARACTER'
                               and 'Trafalgar Law' not in getattr(c, 'name', '')]
                    if odyssey:
                        from .effects.hardcoded import create_play_from_hand_choice
                        create_play_from_hand_choice(
                            self, player, odyssey, source_card=None,
                            prompt="Choose ODYSSEY cost 3 or less Character to play"
                        )

            elif action == "law_leader_return_then_play":
                # Return own character, then play different color cost 5 or less
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])
                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    returned_colors: set = set()
                    for c in player.cards_in_play[:]:
                        if c.id == target_info["id"]:
                            returned_colors = {col.lower() for col in (getattr(c, 'colors', []) or [])}
                            player.cards_in_play.remove(c)
                            player.hand.append(c)
                            self._log(f"{c.name} returned to hand")
                            break
                    # Now trigger play different color choice
                    playable = [c for c in player.hand
                                if getattr(c, 'card_type', '') == 'CHARACTER'
                                and (getattr(c, 'cost', 0) or 0) <= 5
                                and not any(col.lower() in returned_colors
                                            for col in (getattr(c, 'colors', []) or []))]
                    if playable:
                        from .effects.hardcoded import create_play_from_hand_choice
                        create_play_from_hand_choice(
                            self, player, playable, source_card=None,
                            prompt="Choose cost 5 or less Character (different color) to play"
                        )

            elif action == "perona_rest_then_play":
                # Rest own character, then play green cost 5 or less from hand
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])
                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    for c in player.cards_in_play:
                        if c.id == target_info["id"]:
                            c.is_resting = True
                            self._log(f"{c.name} was rested")
                            break
                    # Now trigger play green cost 5 or less
                    green_chars = [c for c in player.hand
                                  if 'green' in (getattr(c, 'colors', '') or '').lower()
                                  and (getattr(c, 'cost', 0) or 0) <= 5
                                  and getattr(c, 'card_type', '') == 'CHARACTER']
                    if green_chars:
                        from .effects.hardcoded import create_play_from_hand_choice
                        create_play_from_hand_choice(
                            self, player, green_chars, source_card=None,
                            prompt="Choose green cost 5 or less Character to play"
                        )

            elif action == "arlong_remove_life":
                # Opponent is whichever player is NOT the Arlong owner
                opponent = self.player2 if player is self.player1 else self.player1
                if selected and selected[0] == "yes" and opponent.life_cards:
                    life = opponent.life_cards.pop()
                    opponent.deck.append(life)
                    self._log(f"Arlong: Placed 1 of {opponent.name}'s Life at bottom of deck")
                else:
                    self._log(f"Arlong: Player chose not to remove Life")

            elif action == "kanjuro_opponent_trash":
                # Opponent chose which card to trash from player's hand
                target_player_id = data.get("target_player_id")
                target_player = self.player1 if self.player1.player_id == target_player_id else self.player2
                hand_cards = data.get("hand_cards", [])
                target_idx = int(selected[0]) if selected else -1
                if 0 <= target_idx < len(hand_cards):
                    target_info = hand_cards[target_idx]
                    for c in target_player.hand[:]:
                        if c.id == target_info["id"]:
                            target_player.hand.remove(c)
                            target_player.trash.append(c)
                            self._log(f"Kanjuro: {player.name} chose to trash {c.name} from {target_player.name}'s hand")
                            break

            elif action == "samurai_rest_and_draw":
                # Rest selected characters, then draw 2
                active_cards = data.get("active_cards", [])
                for sel in selected:
                    idx = int(sel)
                    if 0 <= idx < len(active_cards):
                        card_info = active_cards[idx]
                        for c in player.cards_in_play:
                            if c.id == card_info["id"]:
                                c.is_resting = True
                                self._log(f"{c.name} was rested")
                                break
                if selected:
                    from .effects.hardcoded import draw_cards
                    draw_cards(player, 2)
                    self._log(f"{player.name} drew 2 cards")

            elif action == "ko_multiple_targets":
                # KO multiple selected targets
                target_cards = data.get("target_cards", [])
                opponent = self.player2 if player == self.player1 else self.player1
                for sel in selected:
                    idx = int(sel)
                    if 0 <= idx < len(target_cards):
                        target_info = target_cards[idx]
                        for p in [player, opponent]:
                            for c in p.cards_in_play[:]:
                                if c.id == target_info["id"]:
                                    p.cards_in_play.remove(c)
                                    p.trash.append(c)
                                    self._log(f"{c.name} was K.O.'d")
                                    break

            elif action == "bebeng_trash_then_activate":
                # Trash chosen Wano card, then prompt to set a Wano char active
                wano_hand = data.get("wano_hand", [])
                wano_field = data.get("wano_field", [])
                target_idx = int(selected[0]) if selected else -1
                if 0 <= target_idx < len(wano_hand):
                    card_info = wano_hand[target_idx]
                    for c in player.hand[:]:
                        if c.id == card_info["id"]:
                            player.hand.remove(c)
                            player.trash.append(c)
                            self._log(f"BE-BENG!!: {player.name} trashed {c.name}")
                            break
                # Now prompt to set a Wano field char active
                if wano_field:
                    field_options = [{"id": str(i), "label": f"{info['name']}",
                                      "card_id": info["id"], "card_name": info["name"]}
                                     for i, info in enumerate(wano_field)]
                    self.pending_choice = PendingChoice(
                        choice_id=f"bebeng_act_{uuid.uuid4().hex[:8]}",
                        choice_type="select_target",
                        prompt="Choose a Land of Wano cost 3 or less Character to set as active",
                        options=field_options,
                        min_selections=0,
                        max_selections=1,
                        callback_action="bebeng_set_active",
                        callback_data={"player_id": player.player_id,
                                       "wano_field": wano_field},
                    )

            elif action == "bebeng_set_active":
                # Set chosen Wano char as active
                wano_field = data.get("wano_field", [])
                target_idx = int(selected[0]) if selected else -1
                if 0 <= target_idx < len(wano_field):
                    card_info = wano_field[target_idx]
                    for c in player.cards_in_play:
                        if c.id == card_info["id"]:
                            c.is_resting = False
                            self._log(f"BE-BENG!!: {c.name} set as active")
                            break

            elif action == "alvida_trash_then_return":
                # Trash chosen card, then prompt to return opponent's char to hand
                hand_cards = data.get("hand_cards", [])
                return_targets = data.get("return_targets", [])
                target_idx = int(selected[0]) if selected else -1
                if 0 <= target_idx < len(hand_cards):
                    card_info = hand_cards[target_idx]
                    for c in player.hand[:]:
                        if c.id == card_info["id"]:
                            player.hand.remove(c)
                            player.trash.append(c)
                            self._log(f"Alvida: {player.name} trashed {c.name}")
                            break
                # Now prompt to return opponent's char
                if return_targets:
                    rt_options = [{"id": str(i), "label": f"{info['name']}",
                                   "card_id": info["id"], "card_name": info["name"]}
                                  for i, info in enumerate(return_targets)]
                    self.pending_choice = PendingChoice(
                        choice_id=f"alvida_ret_{uuid.uuid4().hex[:8]}",
                        choice_type="select_target",
                        prompt="Choose opponent's cost 3 or less Character to return to hand",
                        options=rt_options,
                        min_selections=0,
                        max_selections=1,
                        callback_action="return_to_hand",
                        callback_data={"player_id": player.player_id,
                                       "target_cards": return_targets},
                    )

            elif action == "sasaki_optional_trash_then_don":
                # Optionally trash a card, then add 1 rested DON
                hand_cards = data.get("hand_cards", [])
                target_idx = int(selected[0]) if selected else -1
                if 0 <= target_idx < len(hand_cards):
                    card_info = hand_cards[target_idx]
                    for c in player.hand[:]:
                        if c.id == card_info["id"]:
                            player.hand.remove(c)
                            player.trash.append(c)
                            self._log(f"Sasaki: {player.name} trashed {c.name}")
                            # Add 1 rested DON
                            from .effects.hardcoded import add_don_from_deck
                            add_don_from_deck(player, 1, set_active=False)
                            self._log(f"{player.name} added 1 rested DON!! from DON deck")
                            break

            elif action == "search_play_to_field":
                # Pick from candidates in deck, move to field, optionally shuffle
                target_cards = data.get("target_cards", [])
                shuffle_after = data.get("shuffle_after", False)
                target_idx = int(selected[0]) if selected else -1
                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    for c in player.deck[:]:
                        if c.id == target_info["id"]:
                            player.deck.remove(c)
                            player.cards_in_play.append(c)
                            self._log(f"{player.name} played {c.name} from deck to field")
                            break
                if shuffle_after:
                    import random
                    random.shuffle(player.deck)

            elif action == "smile_play_to_field":
                # Pick from top-5 SMILE chars, move to field, rest of top5 go to bottom
                top5_ids = data.get("top5_ids", [])
                smile_cards = data.get("smile_cards", [])
                chosen_id = selected[0] if selected else None
                for c in player.deck[::-1]:
                    if c.id in top5_ids and c not in player.cards_in_play:
                        pass  # will handle below
                # Move top5 from bottom of deck to field or stay at bottom
                if chosen_id:
                    for c in player.deck[::-1]:
                        if c.id == chosen_id:
                            player.deck.remove(c)
                            player.cards_in_play.append(c)
                            self._log(f"{player.name} played {c.name} to field from SMILE effect")
                            break

            elif action == "red_hawk_power_then_ko":
                # Apply +4000 to selected card, then create KO choice
                power_targets = data.get("power_targets", [])
                ko_targets_data = data.get("ko_targets", [])
                target_idx = int(selected[0]) if selected else -1
                if 0 <= target_idx < len(power_targets):
                    target_info = power_targets[target_idx]
                    opponent = self.player2 if player == self.player1 else self.player1
                    all_cards = player.cards_in_play + ([player.leader] if player.leader else []) + \
                                opponent.cards_in_play + ([opponent.leader] if opponent.leader else [])
                    for c in all_cards:
                        if c and c.id == target_info["id"]:
                            c.power_modifier = getattr(c, 'power_modifier', 0) + 4000
                            self._log(f"Red Hawk: {c.name} gains +4000 power")
                            break
                # Now create KO choice if there are targets
                if ko_targets_data:
                    opponent = self.player2 if player == self.player1 else self.player1
                    # Refresh targets with updated power
                    live_ko_targets = [c for c in opponent.cards_in_play
                                       if (getattr(c, 'power', 0) or 0) + getattr(c, 'power_modifier', 0) <= 4000]
                    if live_ko_targets:
                        from .effects.hardcoded import create_ko_choice
                        create_ko_choice(self, player, live_ko_targets, source_card=None,
                                         prompt="Choose opponent's 4000 power or less Character to K.O.")

            elif action == "paradise_power_then_set_active":
                # Apply +2000 to selected card, then prompt to set a rested char active
                power_targets = data.get("power_targets", [])
                rested_chars = data.get("rested_chars", [])
                target_idx = int(selected[0]) if selected else -1
                if 0 <= target_idx < len(power_targets):
                    target_info = power_targets[target_idx]
                    opponent = self.player2 if player == self.player1 else self.player1
                    for c in player.cards_in_play + ([player.leader] if player.leader else []) + \
                             opponent.cards_in_play + ([opponent.leader] if opponent.leader else []):
                        if c and c.id == target_info["id"]:
                            c.power_modifier = getattr(c, 'power_modifier', 0) + 2000
                            self._log(f"Paradise Waterfall: {c.name} gains +2000 power")
                            break
                if rested_chars:
                    rc_options = [{"id": str(i), "label": info["name"],
                                   "card_id": info["id"], "card_name": info["name"]}
                                  for i, info in enumerate(rested_chars)]
                    self.pending_choice = PendingChoice(
                        choice_id=f"paradise_act_{uuid.uuid4().hex[:8]}",
                        choice_type="select_target",
                        prompt="Choose 1 of your Characters to set as active",
                        options=rc_options,
                        min_selections=0,
                        max_selections=1,
                        callback_action="set_active",
                        callback_data={"player_id": player.player_id,
                                       "target_cards": rested_chars},
                    )

            elif action == "desert_spada_power_then_reorder":
                # OP01-088: Apply +2000 power, then reorder top 3 cards of deck
                target_cards = data.get("target_cards", [])
                target_idx = int(selected[0]) if selected else -1
                opponent = self.player2 if player == self.player1 else self.player1
                all_cards = player.cards_in_play + opponent.cards_in_play + \
                            ([player.leader] if player.leader else []) + \
                            ([opponent.leader] if opponent.leader else [])
                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    for c in all_cards:
                        if c and c.id == target_info["id"]:
                            c.power_modifier = getattr(c, 'power_modifier', 0) + 2000
                            self._log(f"Desert Spada: {c.name} gets +2000 power")
                            break
                # Chain: reorder top 3 of deck (top or bottom choice)
                from .effects.hardcoded import reorder_top_cards
                reorder_top_cards(self, player, 3, allow_top=True)

            elif action == "buggy_top_or_bottom":
                # OP01-077 Buggy: keep top card on top or move to bottom
                pick = selected[0] if selected else "top"
                if player.deck:
                    if pick == "bottom":
                        top_card = player.deck.pop(0)
                        player.deck.append(top_card)
                        self._log(f"Buggy: Placed {top_card.name} at bottom of deck")
                    else:
                        self._log(f"Buggy: Kept {player.deck[0].name} on top of deck")

            elif action == "doffy_reveal_play":
                # Doflamingo leader: player chose to play or skip revealed card
                player_choice = selected[0] if selected else "skip"
                if player.deck and player_choice == "play":
                    revealed = player.deck.pop(0)
                    revealed.is_resting = True
                    player.cards_in_play.append(revealed)
                    self._apply_keywords(revealed)
                    self._log(f"Doflamingo: {revealed.name} played to field rested")
                else:
                    self._log(f"Doflamingo: Card left on top of deck")

            elif action == "punk_gibson_power_then_rest":
                # Apply +4000 to selected card, then prompt to rest opponent's cost 4 or less
                power_targets = data.get("power_targets", [])
                rest_targets = data.get("rest_targets", [])
                target_idx = int(selected[0]) if selected else -1
                if 0 <= target_idx < len(power_targets):
                    target_info = power_targets[target_idx]
                    opponent = self.player2 if player == self.player1 else self.player1
                    for c in player.cards_in_play + ([player.leader] if player.leader else []) + \
                             opponent.cards_in_play + ([opponent.leader] if opponent.leader else []):
                        if c and c.id == target_info["id"]:
                            c.power_modifier = getattr(c, 'power_modifier', 0) + 4000
                            self._log(f"Punk Gibson: {c.name} gains +4000 power")
                            break
                if rest_targets:
                    rt_options = [{"id": str(i), "label": info["name"],
                                   "card_id": info["id"], "card_name": info["name"]}
                                  for i, info in enumerate(rest_targets)]
                    self.pending_choice = PendingChoice(
                        choice_id=f"punk_rest_{uuid.uuid4().hex[:8]}",
                        choice_type="select_target",
                        prompt="Choose opponent's cost 4 or less Character to rest",
                        options=rt_options,
                        min_selections=0,
                        max_selections=1,
                        callback_action="rest_target",
                        callback_data={"player_id": player.player_id,
                                       "target_cards": rest_targets},
                    )

            elif action == "overheat_power_then_return":
                # Apply +4000 to selected card, then prompt to return opponent's cost 3 or less active
                power_targets = data.get("power_targets", [])
                return_targets = data.get("return_targets", [])
                target_idx = int(selected[0]) if selected else -1
                if 0 <= target_idx < len(power_targets):
                    target_info = power_targets[target_idx]
                    opponent = self.player2 if player == self.player1 else self.player1
                    for c in player.cards_in_play + ([player.leader] if player.leader else []) + \
                             opponent.cards_in_play + ([opponent.leader] if opponent.leader else []):
                        if c and c.id == target_info["id"]:
                            c.power_modifier = getattr(c, 'power_modifier', 0) + 4000
                            self._log(f"Overheat: {c.name} gains +4000 power")
                            break
                if return_targets:
                    rt_options = [{"id": str(i), "label": info["name"],
                                   "card_id": info["id"], "card_name": info["name"]}
                                  for i, info in enumerate(return_targets)]
                    self.pending_choice = PendingChoice(
                        choice_id=f"overheat_ret_{uuid.uuid4().hex[:8]}",
                        choice_type="select_target",
                        prompt="Choose opponent's active cost 3 or less Character to return to hand",
                        options=rt_options,
                        min_selections=0,
                        max_selections=1,
                        callback_action="return_to_hand",
                        callback_data={"player_id": player.player_id,
                                       "target_cards": return_targets},
                    )

            elif action == "don_return":
                # Generic DON return callback — player chose which DON to return.
                # Process pool removals and character detachments, then dispatch
                # the card-specific follow-up via after_callback.
                pool_removals = []
                char_detach = {}  # card_index -> count
                leader_detach = 0
                for sel_id in selected:
                    if sel_id.startswith("pool_"):
                        pool_removals.append(int(sel_id.split("_")[1]))
                    elif sel_id.startswith("leader_"):
                        leader_detach += 1
                    elif sel_id.startswith("char_"):
                        ci = int(sel_id.split("_")[1])
                        char_detach[ci] = char_detach.get(ci, 0) + 1
                # Remove from pool (highest index first to avoid shifting)
                for idx in sorted(pool_removals, reverse=True):
                    if idx < len(player.don_pool):
                        player.don_pool.pop(idx)
                # Detach from leader
                if leader_detach > 0 and player.leader:
                    player.leader.attached_don = max(0, getattr(player.leader, 'attached_don', 0) - leader_detach)
                # Detach from characters
                for ci, cnt in char_detach.items():
                    if ci < len(player.cards_in_play):
                        c = player.cards_in_play[ci]
                        c.attached_don = max(0, getattr(c, 'attached_don', 0) - cnt)
                self._log(f"Returned {len(selected)} DON!! to DON deck")
                self._trigger_on_don_return_effects(player)

                # Dispatch card-specific follow-up
                after = data.get("after_callback")
                after_data = data.get("after_callback_data", {})
                self._dispatch_don_after_callback(player, after, after_data)

            elif action == "optional_trash_from_deck":
                # Optional: trash N cards from top of deck (e.g. OP03-050 Boodle, OP03-054)
                if "yes" in selected:
                    count = data.get("count", 1)
                    for _ in range(min(count, len(player.deck))):
                        if player.deck:
                            player.trash.append(player.deck.pop(0))
                    self._log(f"{player.name} trashed {count} card(s) from top of deck")

            elif action == "op03_041_damage_trash":
                # OP03-041 Usopp: When dealing damage with DON, trash 7 from top of deck
                if "yes" in selected:
                    count = min(7, len(player.deck))
                    for _ in range(count):
                        if player.deck:
                            player.trash.append(player.deck.pop(0))
                    self._log(f"Usopp: Trashed {count} card(s) from top of deck")

            elif action == "op03_043_damage_trash":
                # OP03-043 Gaimon: When dealing damage, trash 3 from deck then trash Gaimon
                if "yes" in selected:
                    count = min(3, len(player.deck))
                    for _ in range(count):
                        if player.deck:
                            player.trash.append(player.deck.pop(0))
                    self._log(f"Gaimon: Trashed {count} card(s) from top of deck")
                    # Find and trash Gaimon from field
                    src_id = data.get("source_card_id", "")
                    for c in player.cards_in_play[:]:
                        if c.id == src_id or (getattr(c, 'name', '') == 'Gaimon'):
                            player.cards_in_play.remove(c)
                            player.trash.append(c)
                            self._log(f"{c.name} is trashed")
                            break

            elif action == "op03_051_damage_trash":
                # OP03-051 Bell-mère: When dealing damage with DON, trash 7 from top of deck
                if "yes" in selected:
                    count = min(7, len(player.deck))
                    for _ in range(count):
                        if player.deck:
                            player.trash.append(player.deck.pop(0))
                    self._log(f"Bell-mère: Trashed {count} card(s) from top of deck")

            elif action == "don_optional":
                # Player was asked whether to pay an optional DON!! -X cost.
                if "yes" in selected:
                    count = data.get("count", 1)
                    after_cb = data.get("after_callback")
                    after_data = data.get("after_callback_data", {})
                    src_id = after_data.get("source_card_id")
                    src_card = None
                    if src_id:
                        src_card = next((c for c in player.cards_in_play if c.id == src_id), None)
                        if not src_card and player.leader and player.leader.id == src_id:
                            src_card = player.leader
                    from .effects.hardcoded import return_don_to_deck
                    auto = return_don_to_deck(
                        self, player, count,
                        source_card=src_card,
                        after_callback=after_cb,
                        after_callback_data=after_data,
                    )
                    if auto:
                        # DON auto-returned (all from pool, no real choice).
                        # Dispatch the card-specific follow-up inline.
                        self._log(f"Returned {count} DON!! to DON deck")
                        self._trigger_on_don_return_effects(player)
                        self._dispatch_don_after_callback(player, after_cb, after_data)
                else:
                    self._log(f"Player chose not to return DON!!")

            elif action == "ko_for_op14_079":
                # OP14-079 Crocodile: K.O. own character, then K.O. opponent's with same or less cost
                target_idx = int(selected[0]) if selected else -1
                target_cards = data.get("target_cards", [])
                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    ko_cost = 0
                    for c in player.cards_in_play[:]:
                        if c.id == target_info["id"]:
                            ko_cost = getattr(c, 'cost', 0) or 0
                            player.cards_in_play.remove(c)
                            player.trash.append(c)
                            self._log(f"{c.name} was K.O.'d (cost {ko_cost})")
                            break
                    # Now trigger K.O. choice for opponent's character with same or less cost
                    opponent = self.player2 if player == self.player1 else self.player1
                    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= ko_cost]
                    if targets:
                        from .effects.hardcoded import create_ko_choice
                        create_ko_choice(
                            self, player, targets, source_card=None,
                            prompt=f"Choose opponent's cost {ko_cost} or less Character to K.O."
                        )

            elif action == "impel_down_trash_then_search":
                # OP02-092 Impel Down: Trash chosen hand card, then search top 3 for Impel Down type
                target_cards = data.get("target_cards", [])
                if selected:
                    target_idx = int(selected[0]) if selected[0].isdigit() else -1
                    if 0 <= target_idx < len(target_cards):
                        target_info = target_cards[target_idx]
                        for c in player.hand[:]:
                            if c.id == target_info["id"]:
                                player.hand.remove(c)
                                player.trash.append(c)
                                self._log(f"{player.name} trashed {c.name} for Impel Down")
                                break
                # Now search top 3 for Impel Down type
                from .effects.hardcoded import search_top_cards
                search_top_cards(
                    self, player, look_count=3, add_count=1,
                    filter_fn=lambda c: 'impel down' in (c.card_origin or '').lower(),
                    source_card=None,
                    prompt="Look at top 3: choose 1 Impel Down card to add to hand")

            elif action == "rev_army_hq_trash_then_search":
                # OP05-021 Revolutionary Army HQ: Trash chosen hand card, then search top 3
                target_cards = data.get("target_cards", [])
                if selected:
                    target_idx = int(selected[0]) if selected[0].isdigit() else -1
                    if 0 <= target_idx < len(target_cards):
                        target_info = target_cards[target_idx]
                        for c in player.hand[:]:
                            if c.id == target_info["id"]:
                                player.hand.remove(c)
                                player.trash.append(c)
                                self._log(f"{player.name} trashed {c.name} for Revolutionary Army HQ")
                                break
                # Now search top 3 for Revolutionary Army type
                from .effects.hardcoded import search_top_cards
                search_top_cards(
                    self, player, look_count=3, add_count=1,
                    filter_fn=lambda c: 'revolutionary army' in (c.card_origin or '').lower(),
                    source_card=None,
                    prompt="Look at top 3: choose 1 Revolutionary Army card to add to hand")

            elif action == "search_trash_from_top":
                # OP03-083 Corgy: Trash selected cards from top, place rest at bottom
                look_count = data.get("look_count", 0)
                source_name = data.get("source_name", "")
                source_id = data.get("source_id", "")

                chosen_indices = sorted([int(s) for s in selected], reverse=True) if selected else []

                # Pop chosen cards from deck by position (descending to preserve indices)
                trashed_cards = []
                for idx in chosen_indices:
                    if 0 <= idx < len(player.deck):
                        trashed_card = player.deck.pop(idx)
                        trashed_cards.append(trashed_card)
                        player.trash.append(trashed_card)

                if trashed_cards:
                    names = ", ".join(c.name for c in trashed_cards)
                    self._log(f"{source_name}: Trashed {names}")

                # Pull remaining top cards out of deck and place at bottom
                remaining_count = look_count - len(trashed_cards)
                remaining = player.deck[:remaining_count]
                for _ in range(remaining_count):
                    if player.deck:
                        player.deck.pop(0)

                if len(remaining) <= 1:
                    player.deck.extend(remaining)
                    if remaining:
                        self._log(f"{source_name}: Remaining card placed at bottom of deck")
                elif remaining:
                    self._create_deck_order_choice(
                        player, remaining, [],
                        source_name=source_name,
                        source_id=source_id,
                    )

            elif action == "blackmaria_optional_don":
                # OP01-111: Player chose whether to pay DON!! -1 for +1000 power
                if selected and selected[0] == "yes":
                    pi = data.get("player_index", 0)
                    bm_player = self.player1 if pi == 0 else self.player2
                    src_id = data.get("source_card_id")
                    from .effects.hardcoded import return_don_to_deck
                    auto = return_don_to_deck(self, bm_player, 1, source_card=None,
                                              after_callback="op01_111_blackmaria_power",
                                              after_callback_data={"source_card_id": src_id,
                                                                   "player_index": pi})
                    if auto:
                        src = next((c for c in bm_player.cards_in_play if c.id == src_id), None)
                        if src:
                            src.power_modifier = getattr(src, 'power_modifier', 0) + 1000
                            self._log(f"  {src.name} gained +1000 power")
                else:
                    self._log("Black Maria: Declined to use DON!! -1 effect")

            elif action == "mr3_cannot_attack":
                # Mr.3: Set selected opponent's character to cannot_attack
                # Persists until end of opponent's next turn (turn_count + 1)
                target_cards = data.get("target_cards", [])
                target_idx = int(selected[0]) if selected else -1
                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    opponent = self.player2 if player == self.player1 else self.player1
                    for c in opponent.cards_in_play:
                        if c.id == target_info["id"]:
                            c.cannot_attack = True
                            c.cannot_attack_until_turn = self.turn_count + 1
                            self._log(f"Mr.3: {c.name} cannot attack until end of opponent's next turn")
                            break

            elif action == "ulti_rest_don_add":
                # Ulti: If yes, rest 1 DON and add 1 rested DON from deck
                if selected and selected[0] == "yes":
                    active_idx = next((i for i, s in enumerate(player.don_pool) if s == "active"), None)
                    if active_idx is not None:
                        player.don_pool[active_idx] = "rested"
                        if len(player.don_pool) < 10:
                            player.don_pool.append("rested")
                            self._log(f"Ulti: {player.name} rested 1 DON, gained 1 rested DON")
                        else:
                            self._log(f"Ulti: {player.name} rested 1 DON but DON pool is full")

            elif action == "king_ko_then_ko2":
                # King: KO first target (cost 3), then prompt for second KO (cost 2)
                target_cards = data.get("target_cards", [])
                target_idx = int(selected[0]) if selected else -1
                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    opponent = self.player2 if player == self.player1 else self.player1
                    for c in opponent.cards_in_play[:]:
                        if c.id == target_info["id"]:
                            opponent.cards_in_play.remove(c)
                            opponent.trash.append(c)
                            self._log(f"King: K.O.'d {c.name}")
                            break
                # Now prompt for cost 2 or less KO
                opponent = self.player2 if player == self.player1 else self.player1
                targets_2 = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
                if targets_2:
                    from .effects.hardcoded import create_ko_choice
                    create_ko_choice(self, player, targets_2,
                                    prompt="King: Choose opponent's cost 2 or less Character to K.O.")

            elif action == "jack_don_then_trash":
                # Jack: Pay DON-1, opponent trashes 1 from hand
                if selected and selected[0] == "yes":
                    if player.don_pool:
                        player.don_pool.pop()
                        opponent = self.player2 if player == self.player1 else self.player1
                        if opponent.hand:
                            import random
                            trashed = random.choice(opponent.hand)
                            opponent.hand.remove(trashed)
                            opponent.trash.append(trashed)
                            self._log(f"Jack: {opponent.name} trashed {trashed.name}")
                        else:
                            self._log(f"Jack: {opponent.name} has no cards to trash")

            elif action == "xdrake_don_then_trash":
                # X.Drake: Pay DON-1, opponent trashes 1 from hand
                if selected and selected[0] == "yes":
                    if player.don_pool:
                        player.don_pool.pop()
                        opponent = self.player2 if player == self.player1 else self.player1
                        if opponent.hand:
                            import random
                            trashed = random.choice(opponent.hand)
                            opponent.hand.remove(trashed)
                            opponent.trash.append(trashed)
                            self._log(f"X.Drake: {opponent.name} trashed {trashed.name}")
                        else:
                            self._log(f"X.Drake: {opponent.name} has no cards to trash")

            elif action == "bao_huang_reveal":
                # Bao Huang: Reveal selected cards from opponent's hand
                pi = data.get("player_index", 0)
                opponent = self.player2 if pi == 0 else self.player1
                indices = sorted([int(s) for s in selected]) if selected else []
                for idx in indices:
                    if 0 <= idx < len(opponent.hand):
                        c = opponent.hand[idx]
                        self._log(f"Bao Huang reveals: {c.name} (Cost: {c.cost or 0}, Type: {c.card_type})")

            elif action == "marco_trash_wb_then_revive":
                # OP02-018: Player selected a WB card to trash; now revive Marco from trash
                wb_targets = data.get("target_cards", [])
                marco_card_id = data.get("marco_card_id")
                if selected:
                    idx = int(selected[0])
                    if 0 <= idx < len(wb_targets):
                        wb_info = wb_targets[idx]
                        # Find and trash the WB card from hand
                        for hc in player.hand[:]:
                            if hc.id == wb_info["id"]:
                                player.hand.remove(hc)
                                player.trash.append(hc)
                                self._log(f"{player.name} trashed {hc.name} from hand")
                                break
                        # Revive Marco from trash
                        for tc in player.trash[:]:
                            if tc.id == marco_card_id:
                                player.trash.remove(tc)
                                player.cards_in_play.append(tc)
                                tc.is_resting = True
                                self._log(f"{tc.name} returns to play rested from trash")
                                break

            elif action == "op02_062_choose_trash":
                # OP02-062: Optional yes/no before paying the trash-2 cost
                if selected and selected[0] == "yes" and len(player.hand) >= 2:
                    options = []
                    for i, hc in enumerate(player.hand):
                        options.append({
                            "id": str(i),
                            "label": f"{hc.name} (Cost: {hc.cost or 0})",
                            "card_id": hc.id,
                            "card_name": hc.name,
                        })
                    self.pending_choice = PendingChoice(
                        choice_id=f"luffy_trash_{uuid.uuid4().hex[:8]}",
                        choice_type="select_cards",
                        prompt="Choose 2 cards from hand to trash",
                        options=options,
                        min_selections=2,
                        max_selections=2,
                        source_card_id=data.get("source_card_id"),
                        source_card_name=data.get("source_card_name"),
                        callback_action="op02_062_trash_then_return",
                        callback_data={
                            "player_id": player.player_id,
                            "player_index": 0 if player is self.player1 else 1,
                            "source_card_id": data.get("source_card_id"),
                            "source_card_name": data.get("source_card_name"),
                        }
                    )

            elif action == "op02_062_trash_then_return":
                # OP02-062: Player selected 2 cards to trash; then optionally return cost 4 or less and gain Double Attack
                indices = sorted([int(s) for s in selected], reverse=True) if selected else []
                for idx in indices:
                    if 0 <= idx < len(player.hand):
                        card = player.hand.pop(idx)
                        player.trash.append(card)
                        self._log(f"{player.name} trashed {card.name}")
                if indices:
                    source_id = data.get("source_card_id")
                    for c in player.cards_in_play:
                        if c.id == source_id:
                            c.has_doubleattack = True
                            c.has_double_attack = True
                            break
                    opponent = self.player2 if player == self.player1 else self.player1
                    targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 4]
                    if targets:
                        from .effects.hardcoded import create_return_to_hand_choice
                        create_return_to_hand_choice(self, player, targets,
                                                     prompt="Choose opponent's cost 4 or less to return to hand")

            elif action == "op02_065_optional_trash_set_active":
                # OP02-065: Player optionally trashes 1 card to set Mr.3 active
                card_id = data.get("mr3_card_id")
                if selected:
                    idx = int(selected[0])
                    if 0 <= idx < len(player.hand):
                        card = player.hand.pop(idx)
                        player.trash.append(card)
                        self._log(f"{player.name} trashed {card.name}")
                        # Set Mr.3 active
                        for c in player.cards_in_play:
                            if c.id == card_id:
                                c.is_resting = False
                                self._log(f"{c.name} set active")
                                break

            elif action == "op02_066_trash_then_draw":
                # OP02-066: Player selected 2 cards to trash; if Impel Down leader, draw 2
                indices = sorted([int(s) for s in selected], reverse=True) if selected else []
                for idx in indices:
                    if 0 <= idx < len(player.hand):
                        card = player.hand.pop(idx)
                        player.trash.append(card)
                        self._log(f"{player.name} trashed {card.name}")
                if len(indices) >= 2:
                    if player.leader and 'impel down' in (player.leader.card_origin or '').lower():
                        from .effects.hardcoded import draw_cards
                        draw_cards(player, 2)
                        self._log("Impel Down All Stars: drew 2 cards")

            elif action == "op02_068_trash_then_power":
                # OP02-068: Player selected 1 card to trash; now give +3000 power
                if selected:
                    idx = int(selected[0])
                    if 0 <= idx < len(player.hand):
                        card = player.hand.pop(idx)
                        player.trash.append(card)
                        self._log(f"{player.name} trashed {card.name}")
                    # Now prompt for power target
                    targets = ([player.leader] if player.leader else []) + player.cards_in_play
                    if targets:
                        from .effects.hardcoded import create_power_effect_choice
                        create_power_effect_choice(
                            self, player, targets, 3000,
                            prompt="Gum-Gum Rain: Choose Leader or Character to give +3000 power"
                        )

            elif action == "op02_064_trash_then_bottom":
                # OP02-064: Player selected 1 card to trash; now place cost 2 or less at bottom
                if selected:
                    idx = int(selected[0])
                    if 0 <= idx < len(player.hand):
                        card = player.hand.pop(idx)
                        player.trash.append(card)
                        self._log(f"{player.name} trashed {card.name}")
                # Set return_to_bottom_after_battle on attacker
                attacker_id = data.get("attacker_card_id")
                for c in player.cards_in_play:
                    if c.id == attacker_id:
                        c.return_to_bottom_after_battle = True
                        break
                # Prompt for opponent's cost 2 or less
                opponent = self.player2 if player == self.player1 else self.player1
                targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
                if targets:
                    from .effects.hardcoded import create_bottom_deck_choice
                    create_bottom_deck_choice(self, player, targets,
                                              prompt="Choose opponent's cost 2 or less to place at deck bottom")

            elif action == "op02_059_optional_trash":
                # OP02-059: Player selected 0-3 cards to trash
                indices = sorted([int(s) for s in selected], reverse=True) if selected else []
                for idx in indices:
                    if 0 <= idx < len(player.hand):
                        card = player.hand.pop(idx)
                        player.trash.append(card)
                        self._log(f"{player.name} trashed {card.name}")

            elif action == "op02_059_required_then_optional":
                # OP02-059: Trash 1 required, then optionally trash up to 3 more
                indices = sorted([int(s) for s in selected], reverse=True) if selected else []
                for idx in indices:
                    if 0 <= idx < len(player.hand):
                        card = player.hand.pop(idx)
                        player.trash.append(card)
                        self._log(f"{player.name} trashed {card.name}")
                if player.hand:
                    options = []
                    for i, hc in enumerate(player.hand):
                        options.append({
                            "id": str(i),
                            "label": f"{hc.name} (Cost: {hc.cost or 0})",
                            "card_id": hc.id,
                            "card_name": hc.name,
                        })
                    self.pending_choice = PendingChoice(
                        choice_id=f"hancock_trash_{uuid.uuid4().hex[:8]}",
                        choice_type="select_cards",
                        prompt="You may trash up to 3 more cards from hand (select 0 to skip)",
                        options=options,
                        min_selections=0,
                        max_selections=min(3, len(player.hand)),
                        source_card_id=data.get("source_card_id"),
                        source_card_name=data.get("source_card_name"),
                        callback_action="op02_059_optional_trash",
                        callback_data={
                            "player_id": player.player_id,
                            "player_index": 0 if player is self.player1 else 1,
                        }
                    )

            elif action == "op02_032_pay_don_set_active":
                # OP02-032: Player selected a Minks target; rest 2 DON and set it active
                target_cards = data.get("target_cards", [])
                if selected:
                    idx = int(selected[0])
                    if 0 <= idx < len(target_cards):
                        # Rest 2 active DON
                        rested_count = 0
                        for i in range(len(player.don_pool)):
                            if rested_count >= 2:
                                break
                            if player.don_pool[i] == "active":
                                player.don_pool[i] = "rested"
                                rested_count += 1
                        # Set target as active
                        target_info = target_cards[idx]
                        for c in player.cards_in_play:
                            if c.id == target_info["id"]:
                                c.is_resting = False
                                self._log(f"Shishilian: set {c.name} active")
                                break

            elif action == "op02_026_set_don_active":
                # OP02-026: Set up to 2 rested DON active
                rested_indices = data.get("rested_indices", [])
                chosen_positions = sorted({int(s) for s in selected}, reverse=True) if selected else []
                for pos in chosen_positions:
                    if 0 <= pos < len(rested_indices):
                        pool_idx = rested_indices[pos]
                        if 0 <= pool_idx < len(player.don_pool) and player.don_pool[pool_idx] == "rested":
                            player.don_pool[pool_idx] = "active"
                if chosen_positions:
                    self._log(f"Sanji: set {len(chosen_positions)} DON!! card(s) as active")

            elif action == "op02_029_set_don_active":
                # OP02-029: Set up to 1 rested DON active
                rested_indices = data.get("rested_indices", [])
                if selected:
                    pos = int(selected[0])
                    if 0 <= pos < len(rested_indices):
                        pool_idx = rested_indices[pos]
                        if 0 <= pool_idx < len(player.don_pool) and player.don_pool[pool_idx] == "rested":
                            player.don_pool[pool_idx] = "active"
                            self._log("Carrot: set 1 DON!! active")

            elif action == "op02_086_optional_add_don":
                if selected and selected[0] == "yes":
                    if len(player.don_pool) < 10:
                        player.don_pool.append("rested")
                        self._log("Minokoala: added 1 rested DON!! from DON!! deck")

            elif action == "op02_087_optional_add_don":
                if selected and selected[0] == "yes":
                    if len(player.don_pool) < 10:
                        player.don_pool.append("rested")
                        self._log("Minotaur: added 1 rested DON!! from DON!! deck")

            elif action == "op02_093_cost_then_power":
                target_cards = data.get("target_cards", [])
                if selected:
                    target_idx = int(selected[0])
                    if 0 <= target_idx < len(target_cards):
                        target_info = target_cards[target_idx]
                        opponent = self.player2 if player == self.player1 else self.player1
                        for p in [opponent, player]:
                            for c in p.cards_in_play:
                                if c.id == target_info["id"]:
                                    c.cost_modifier = getattr(c, 'cost_modifier', 0) - 1
                                    self._log(f"{c.name} gets -1 cost this turn")
                                    break
                all_chars = player.cards_in_play + (self.player2 if player == self.player1 else self.player1).cards_in_play
                if any((getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) == 0 for c in all_chars):
                    if player.leader:
                        player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 1000
                        player.leader._sticky_power_modifier = getattr(player.leader, '_sticky_power_modifier', 0) + 1000
                        self._log(f"{player.leader.name} gets +1000 power")

            elif action == "op02_098_optional_trash_then_ko":
                if selected and selected[0] == "yes" and player.hand:
                    options = []
                    for i, hc in enumerate(player.hand):
                        options.append({
                            "id": str(i),
                            "label": f"{hc.name} (Cost: {hc.cost or 0})",
                            "card_id": hc.id,
                            "card_name": hc.name,
                        })
                    self.pending_choice = PendingChoice(
                        choice_id=f"koby_trash_{uuid.uuid4().hex[:8]}",
                        choice_type="select_cards",
                        prompt="Choose 1 card from hand to trash for Koby",
                        options=options,
                        min_selections=1,
                        max_selections=1,
                        source_card_id=data.get("source_card_id"),
                        callback_action="op02_098_pay_trash_then_ko",
                        callback_data={"player_id": player.player_id, "source_card_id": data.get("source_card_id")}
                    )

            elif action == "op02_098_pay_trash_then_ko":
                if selected:
                    idx = int(selected[0])
                    if 0 <= idx < len(player.hand):
                        trashed = player.hand.pop(idx)
                        player.trash.append(trashed)
                        self._log(f"{player.name} trashed {trashed.name}")
                        opponent = self.player2 if player == self.player1 else self.player1
                        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 3]
                        if targets:
                            from .effects.hardcoded import create_ko_choice
                            create_ko_choice(self, player, targets, prompt="Choose opponent's cost 3 or less to KO")

            elif action == "op02_099_optional_trash_then_ko":
                if selected and selected[0] == "yes" and player.hand:
                    options = []
                    for i, hc in enumerate(player.hand):
                        options.append({
                            "id": str(i),
                            "label": f"{hc.name} (Cost: {hc.cost or 0})",
                            "card_id": hc.id,
                            "card_name": hc.name,
                        })
                    self.pending_choice = PendingChoice(
                        choice_id=f"sakazuki_trash_{uuid.uuid4().hex[:8]}",
                        choice_type="select_cards",
                        prompt="Choose 1 card from hand to trash for Sakazuki",
                        options=options,
                        min_selections=1,
                        max_selections=1,
                        source_card_id=data.get("source_card_id"),
                        callback_action="op02_099_pay_trash_then_ko",
                        callback_data={"player_id": player.player_id, "source_card_id": data.get("source_card_id")}
                    )

            elif action == "op02_099_pay_trash_then_ko":
                if selected:
                    idx = int(selected[0])
                    if 0 <= idx < len(player.hand):
                        trashed = player.hand.pop(idx)
                        player.trash.append(trashed)
                        self._log(f"{player.name} trashed {trashed.name}")
                        opponent = self.player2 if player == self.player1 else self.player1
                        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 5]
                        if targets:
                            from .effects.hardcoded import create_ko_choice
                            create_ko_choice(self, player, targets, prompt="Choose opponent's cost 5 or less to KO")

            elif action == "op02_112_cost_then_power":
                target_cards = data.get("target_cards", [])
                buff_targets = data.get("buff_targets", [])
                if selected:
                    target_idx = int(selected[0])
                    if 0 <= target_idx < len(target_cards):
                        target_info = target_cards[target_idx]
                        opponent = self.player2 if player == self.player1 else self.player1
                        for c in opponent.cards_in_play:
                            if c.id == target_info["id"]:
                                c.cost_modifier = getattr(c, 'cost_modifier', 0) - 1
                                self._log(f"{c.name} gets -1 cost this turn")
                                break
                if buff_targets:
                    options = []
                    for i, t in enumerate(buff_targets):
                        options.append({
                            "id": str(i),
                            "label": t["name"],
                            "card_id": t["id"],
                            "card_name": t["name"],
                        })
                    self.pending_choice = PendingChoice(
                        choice_id=f"bellmere_buff_{uuid.uuid4().hex[:8]}",
                        choice_type="select_target",
                        prompt="Choose your Leader or Character to give +1000 power",
                        options=options,
                        min_selections=1,
                        max_selections=1,
                        callback_action="op02_112_apply_power",
                        callback_data={"player_id": player.player_id, "target_cards": buff_targets}
                    )

            elif action == "op02_112_apply_power":
                target_cards = data.get("target_cards", [])
                all_cards = player.cards_in_play + [player.leader]
                if selected:
                    target_idx = int(selected[0])
                    if 0 <= target_idx < len(target_cards):
                        target_info = target_cards[target_idx]
                        for c in all_cards:
                            if c and c.id == target_info["id"]:
                                c.power_modifier = getattr(c, 'power_modifier', 0) + 1000
                                c._sticky_power_modifier = getattr(c, '_sticky_power_modifier', 0) + 1000
                                self._log(f"{c.name} gets +1000 power")
                                break

            elif action == "op02_113_cost_then_power":
                target_cards = data.get("target_cards", [])
                if selected:
                    target_idx = int(selected[0])
                    if 0 <= target_idx < len(target_cards):
                        target_info = target_cards[target_idx]
                        opponent = self.player2 if player == self.player1 else self.player1
                        for c in opponent.cards_in_play:
                            if c.id == target_info["id"]:
                                c.cost_modifier = getattr(c, 'cost_modifier', 0) - 2
                                self._log(f"{c.name} gets -2 cost this turn")
                                break
                opponent = self.player2 if player == self.player1 else self.player1
                all_chars = player.cards_in_play + opponent.cards_in_play
                source_id = data.get("source_card_id")
                if any((getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 0 for c in all_chars):
                    for c in player.cards_in_play:
                        if c.id == source_id:
                            c.power_modifier = getattr(c, 'power_modifier', 0) + 2000
                            c._sticky_power_modifier = getattr(c, '_sticky_power_modifier', 0) + 2000
                            self._log(f"{c.name} gets +2000 power")
                            break

            elif action == "op02_048_trash_wano":
                # OP02-048: Player selected a Land of Wano card to trash; rest stage, set 1 DON active
                stage_card_id = data.get("stage_card_id")
                wano_targets = data.get("target_cards", [])
                if selected:
                    idx = int(selected[0])
                    if 0 <= idx < len(wano_targets):
                        wano_info = wano_targets[idx]
                        for hc in player.hand[:]:
                            if hc.id == wano_info["id"]:
                                player.hand.remove(hc)
                                player.trash.append(hc)
                                self._log(f"Land of Wano Stage: trashed {hc.name}")
                                break
                        # Rest the stage
                        for c in player.cards_in_play:
                            if c.id == stage_card_id:
                                c.is_resting = True
                                c.main_activated_this_turn = True
                                break
                        # Set 1 rested DON active
                        for i, d in enumerate(player.don_pool):
                            if d == "rested":
                                player.don_pool[i] = "active"
                                self._log("Land of Wano Stage: set 1 DON active")
                                break

            elif action == "op02_070_required_then_optional":
                # OP02-070: Trash 1 required, then optionally trash up to 3 more
                indices = sorted([int(s) for s in selected], reverse=True) if selected else []
                for idx in indices:
                    if 0 <= idx < len(player.hand):
                        card = player.hand.pop(idx)
                        player.trash.append(card)
                        self._log(f"{player.name} trashed {card.name}")
                if player.hand:
                    options = []
                    for i, hc in enumerate(player.hand):
                        options.append({
                            "id": str(i),
                            "label": f"{hc.name} (Cost: {hc.cost or 0})",
                            "card_id": hc.id,
                            "card_name": hc.name,
                        })
                    self.pending_choice = PendingChoice(
                        choice_id=f"new_kama_opt_{uuid.uuid4().hex[:8]}",
                        choice_type="select_cards",
                        prompt="You may trash up to 3 more cards from hand (select 0 to skip)",
                        options=options,
                        min_selections=0,
                        max_selections=min(3, len(player.hand)),
                        source_card_id=data.get("source_card_id"),
                        source_card_name=data.get("source_card_name"),
                        callback_action="op02_059_optional_trash",
                        callback_data={
                            "player_id": player.player_id,
                            "player_index": 0 if player is self.player1 else 1,
                        }
                    )
                else:
                    self._log("New Kama Land: finished draw 1, trash 1")

            elif action == "nami_don_search":
                # OP02-036 Nami: player chose yes/no to rest 1 DON and search top 3 for FILM card
                chosen = selected[0] if selected else "no"
                if chosen == "yes":
                    # Rest 1 active DON
                    for i in range(len(player.don_pool)):
                        if player.don_pool[i] == "active":
                            player.don_pool[i] = "rested"
                            break
                    # Search top 3 for FILM card (not Nami)
                    from .effects.hardcoded import search_top_cards
                    def _nami_filter(c):
                        return ('FILM' in (c.card_origin or '')
                                and getattr(c, 'name', '') != 'Nami')
                    search_top_cards(self, player, 3, add_count=1, filter_fn=_nami_filter,
                                     prompt="Look at top 3. Choose a FILM card (not Nami) to add to hand.")

            # --- OP03 custom callbacks ---
            elif action == "op03_070_grant_rush":
                # OP03-070 Luffy: Player chose a cost 5 char to trash, now grant Rush
                src_id = data.get("source_card_id") or after_data.get("source_card_id", "") if 'after_data' in dir() else data.get("source_card_id", "")
                indices = sorted([int(s) for s in selected], reverse=True) if selected else []
                for idx in indices:
                    if 0 <= idx < len(player.hand):
                        trashed = player.hand.pop(idx)
                        player.trash.append(trashed)
                        self._log(f"{player.name} trashed {trashed.name}")
                # Grant Rush to the source card
                card_id = data.get("source_card_id")
                if card_id:
                    src = next((c for c in player.cards_in_play if c.id == card_id), None)
                    if src:
                        src.has_rush = True
                        self._log(f"  {src.name} gained [Rush]")

            elif action == "op03_018_ko_after_trash":
                # OP03-018 Fire Fist: Player trashed an Event, now KO opponent's 5000 or less
                # (then chain to KO 4000 or less)
                indices = sorted([int(s) for s in selected], reverse=True) if selected else []
                target_cards = data.get("target_cards", [])
                for idx in indices:
                    if 0 <= idx < len(target_cards):
                        target_info = target_cards[idx]
                        for c in player.hand[:]:
                            if c.id == target_info["id"]:
                                player.hand.remove(c)
                                player.trash.append(c)
                                self._log(f"{player.name} trashed {c.name}")
                                break
                opponent = self.player2 if player == self.player1 else self.player1
                targets = [c for c in opponent.cards_in_play
                           if (getattr(c, 'power', 0) or 0) + getattr(c, 'power_modifier', 0) <= 5000]
                if targets:
                    from .effects.hardcoded import create_ko_choice
                    create_ko_choice(self, player, targets, source_card=None,
                                    callback_action="op03_018_ko_4000_after",
                                    prompt="Fire Fist: Choose opponent's 5000 power or less Character to K.O.")
                else:
                    # No 5000-or-less targets, still offer 4000-or-less
                    targets4 = [c for c in opponent.cards_in_play
                                if (getattr(c, 'power', 0) or 0) + getattr(c, 'power_modifier', 0) <= 4000]
                    if targets4:
                        from .effects.hardcoded import create_ko_choice
                        create_ko_choice(self, player, targets4, source_card=None,
                                        prompt="Fire Fist: Choose opponent's 4000 power or less Character to K.O.")

            elif action == "attach_don_to_target":
                # OP03-009 Haruta: Attach 1 DON to chosen target
                target_cards = data.get("target_cards", [])
                target_idx = int(selected[0]) if selected else -1
                if 0 <= target_idx < len(target_cards):
                    target_info = target_cards[target_idx]
                    tid = target_info.get("card_id", "")
                    target = None
                    for c in player.cards_in_play:
                        if c.id == tid:
                            target = c
                            break
                    if not target and player.leader and player.leader.id == tid:
                        target = player.leader
                    if target:
                        target.attached_don = getattr(target, 'attached_don', 0) + 1
                        self._log(f"  Attached 1 DON to {target.name}")
                        # Recalculate continuous effects so DON-gated effects activate
                        self._recalc_continuous_effects()

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
                    from .effects.hardcoded import execute_hardcoded_effect
                    execute_hardcoded_effect(self, defender_player, counter_card, 'counter')

                # If all counter effects resolved and attack resolution was deferred, do it now
                if (not self.pending_choice
                        and self.pending_attack
                        and self.pending_attack.get('_needs_attack_resolution')):
                    self.pending_attack.pop('_needs_attack_resolution', None)
                    self._resolve_attack_damage()
            # else: a new choice was set during processing — leave it in place
            return True

        except Exception as e:
            import traceback
            print(f"Error resolving choice: {e}")
            traceback.print_exc()
            self.pending_choice = None
            return False
