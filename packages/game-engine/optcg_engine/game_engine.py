"""
One Piece TCG Game Engine

This module provides the main game logic for simulating One Piece TCG matches.
It integrates with the mechanics module for combat, blockers, and triggers.
"""

import random
from typing import Optional, List, Tuple
from models.cards import Card
from models.enums import GamePhase
from handlers.effect_handlers import trigger_effect
from effects.parser import parse_effect
from effects.resolver import resolve_effect, EffectContext, get_resolver
from effects.effects import EffectTiming, EffectType
from effects.tokenizer import extract_keywords
from effects.manager import get_effect_manager, parse_card_effects, get_effects_by_timing

# Constants
MAX_DON = 10
DON_PER_TURN = 2
HAND_LIMIT = 7
STARTING_DON_P1 = 1
STARTING_DON_P2 = 2


class Player:
    """Represents a player in the game."""

    def __init__(self, name: str, deck: list[Card], leader: Card):
        self.name = name
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
        # Must have Blocker keyword
        effect = card.effect or ''
        if '[Blocker]' not in effect:
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
        base = target.power or 0
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
        # Unrest leader
        self.leader.is_resting = False
        self.leader.has_attacked = False

        # Unrest all characters and return attached DON
        for c in self.cards_in_play:
            c.is_resting = False
            c.has_attacked = False
            # Return attached DON to pool
            attached = getattr(c, 'attached_don', 0)
            c.attached_don = 0
            c.don_condition_met = False

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
        has_trigger = bool(life_card.trigger and life_card.trigger.strip())

        print(f"{self.name} loses a life card! ({len(self.life_cards)} remaining)")

        if has_trigger:
            print(f"  Trigger: {life_card.trigger}")

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
        self.phase = GamePhase.DRAW
        if not (self.turn_count == 2 and self.current_player is self.player1):
            self.current_player.draw_card()

        # DON phase: add 2 DON (max 10)
        self.phase = GamePhase.DON
        if self.turn_count > 2:
            current_don = len(self.current_player.don_pool)
            new_don = min(current_don + DON_PER_TURN, MAX_DON)
            additional = new_don - current_don
            self.current_player.don_pool.extend(["active"] * additional)

        # Main phase
        self.phase = GamePhase.MAIN
        self._log(f"=== Turn {self.turn_count}: {self.current_player.name} (DON: {len(self.current_player.don_pool)}) ===")

    def _end_phase(self):
        """Handle end of turn cleanup."""
        self.phase = GamePhase.END

        # Check hand limit
        if len(self.current_player.hand) > HAND_LIMIT:
            excess = len(self.current_player.hand) - HAND_LIMIT
            # Auto-discard last cards (AI will learn better strategies)
            indices = list(range(len(self.current_player.hand) - excess, len(self.current_player.hand)))
            self.current_player.discard_to_hand_limit(indices)

    def can_attack_with_leader(self) -> bool:
        """Check if the current player's leader can attack."""
        if self.current_player is self.player1:
            return self.turn_count >= 3
        return self.turn_count >= 4

    def get_valid_attack_targets(self) -> List[Tuple[int, Card]]:
        """
        Get valid attack targets for the current player.

        Valid targets:
        - Opponent's Leader (always)
        - Opponent's rested Characters

        Returns:
            List of (index, card) tuples. Index -1 means leader.
        """
        targets = []

        # Leader is always a valid target
        targets.append((-1, self.opponent_player.leader))

        # Rested characters are valid targets
        for i, card in enumerate(self.opponent_player.cards_in_play):
            if card.is_resting:
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

        keywords = extract_keywords(card.effect)
        for keyword in keywords:
            if keyword == 'RUSH':
                card.has_rush = True
            elif keyword == 'BLOCKER':
                card.has_blocker = True
            elif keyword == 'BANISH':
                card.has_banish = True
            elif keyword == 'DOUBLE_ATTACK':
                card.has_doubleattack = True

    def _trigger_on_play_effects(self, card: Card):
        """Trigger On Play effects for a card using the effect system."""
        if not card.effect:
            return

        # First try hardcoded handlers (for cards with complex effects)
        trigger_effect(card.id, self, card)

        # Then parse and resolve any additional On Play effects
        effects = parse_effect(card.effect)
        for effect in effects:
            if effect.timing == EffectTiming.ON_PLAY:
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
                    if result.success and result.message:
                        self._log(f"  [EFFECT] {result.message}")

    def play_card(self, card: Card):
        """Play a card from hand."""
        cost = card.cost or 0

        # Check field limit (max 5 characters)
        if card.card_type == "CHARACTER":
            char_count = sum(1 for c in self.current_player.cards_in_play if c.card_type == "CHARACTER")
            if char_count >= 5:
                self._log(f"Cannot play {card.name}: field is full (5 characters max).")
                return

        if cost <= self.available_don():
            # Spend DON
            used = 0
            for i in range(len(self.current_player.don_pool)):
                if self.current_player.don_pool[i] == "active":
                    self.current_player.don_pool[i] = "rested"
                    used += 1
                    if used == cost:
                        break

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
            else:
                # CHARACTER and STAGE cards go to field
                self.current_player.cards_in_play.append(card)
                setattr(card, 'played_turn', self.turn_count)

                # Apply keyword effects (Rush, Blocker, etc.)
                self._apply_keywords(card)

                self._log(f"{self.current_player.name} plays {card.name} (Cost {cost}), Remaining Active DON: {self.available_don()}")

                # Trigger On Play effects
                if card.effect and '[On Play]' in card.effect:
                    self._trigger_on_play_effects(card)
        else:
            self._log(f"Cannot play {card.name}: needs {cost} DON, has {self.available_don()}.")

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
        Execute an attack with proper combat flow.

        Args:
            attacker: The attacking card
            target_index: Target index (-1 for leader, >= 0 for character)
        """
        p, o = self.current_player, self.opponent_player

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
                if not defender.is_resting:
                    self._log(f"Cannot attack {defender.name} - only rested characters can be attacked.")
                    return

        # Calculate attacker power
        don = self.card_don_assignments.get(attacker, getattr(attacker, 'attached_don', 0))
        attacker_power = (attacker.power or 0) + don * 1000

        self._log(f"{p.name}'s {attacker.name} (Power: {attacker_power}) attacks {defender.name}!")

        # Trigger [When Attacking] effects
        effect_manager = get_effect_manager()
        attack_effects = effect_manager.on_attack_declare(self, p, attacker, defender)
        for result in attack_effects:
            if result.success and result.message:
                self._log(f"  [WHEN ATTACKING] {result.message}")

        # BLOCKER STEP
        self.phase = GamePhase.BLOCKER_STEP
        available_blockers = o.get_available_blockers()

        actual_defender = defender
        if available_blockers:
            # For now, AI doesn't use blockers strategically
            # The RL agent will learn when to block
            pass

        # COUNTER STEP
        self.phase = GamePhase.COUNTER_STEP
        counter, counters_used = o.choose_counters_for_defense(actual_defender, attacker_power)

        # Log counter usage
        for card, value, is_event in counters_used:
            if is_event:
                # Counter EVENT cards require DON
                self._log(f"  [COUNTER EVENT] {o.name} plays {card.name} (Cost {card.cost} DON, +{value})")
            else:
                # Counter VALUES are free
                self._log(f"  [COUNTER] {o.name} uses {card.name} (+{value})")

        # DAMAGE STEP
        self.phase = GamePhase.DAMAGE_STEP
        defender_power = (actual_defender.power or 0) + counter
        defender_don = getattr(actual_defender, 'attached_don', 0)
        total_defense = defender_power + (defender_don * 1000)

        if attacker_power >= total_defense:
            if actual_defender.card_type == 'LEADER':
                # Check for Banish
                has_banish = getattr(attacker, 'has_banish', False)
                if not has_banish and attacker.effect:
                    has_banish = '[Banish]' in attacker.effect

                # Take life damage
                life_card, has_trigger = o.take_life_damage()

                if len(o.life_cards) == 0:
                    self._log(f"{p.name} wins!")
                    self.game_over = True
                    self.winner = p
                    self.phase = GamePhase.GAME_OVER
                    return

                # Handle life card destination
                card_was_played = False
                trigger_activated = False

                # Handle trigger (if not banished)
                if has_trigger and not has_banish and life_card:
                    self._log(f"  [TRIGGER] {life_card.name}: {life_card.trigger}")
                    trigger_activated = True
                    # Resolve trigger effects
                    trigger_result = effect_manager.on_life_damage(self, o, life_card, has_banish)
                    if trigger_result[0] and trigger_result[1]:
                        if trigger_result[1].success and trigger_result[1].message:
                            self._log(f"    {trigger_result[1].message}")
                        # Check if card was played by trigger (e.g., "Play this card")
                        if life_card in o.cards_in_play:
                            card_was_played = True

                # Life card destination:
                # - If played by trigger: already on field, do nothing
                # - If trigger activated: goes to trash
                # - If no trigger (or banished): goes to hand
                # - If banished: goes to trash
                if life_card and not card_was_played:
                    if has_banish or trigger_activated:
                        o.trash.append(life_card)
                        if has_banish:
                            self._log(f"  {life_card.name} is banished to trash")
                        else:
                            self._log(f"  {life_card.name} sent to trash (trigger used)")
                    else:
                        o.hand.append(life_card)
                        self._log(f"  {life_card.name} added to hand")

                # Double Attack - deal another damage
                has_double_attack = getattr(attacker, 'has_doubleattack', False)
                if not has_double_attack and attacker.effect:
                    has_double_attack = '[Double Attack]' in attacker.effect

                if has_double_attack:
                    self._log(f"{attacker.name} has Double Attack - dealing additional damage!")
                    life_card2, has_trigger2 = o.take_life_damage()
                    if len(o.life_cards) == 0:
                        self._log(f"{p.name} wins!")
                        self.game_over = True
                        self.winner = p
                        self.phase = GamePhase.GAME_OVER
                        return

                    # Handle second life card trigger and destination
                    card2_was_played = False
                    trigger2_activated = False
                    if has_trigger2 and not has_banish and life_card2:
                        self._log(f"  [TRIGGER] {life_card2.name}: {life_card2.trigger}")
                        trigger2_activated = True
                        trigger_result2 = effect_manager.on_life_damage(self, o, life_card2, has_banish)
                        if trigger_result2[0] and trigger_result2[1]:
                            if trigger_result2[1].success and trigger_result2[1].message:
                                self._log(f"    {trigger_result2[1].message}")
                            if life_card2 in o.cards_in_play:
                                card2_was_played = True

                    # Second life card destination (same rules as first)
                    if life_card2 and not card2_was_played:
                        if has_banish or trigger2_activated:
                            o.trash.append(life_card2)
                            if has_banish:
                                self._log(f"  {life_card2.name} is banished to trash")
                            else:
                                self._log(f"  {life_card2.name} sent to trash (trigger used)")
                        else:
                            o.hand.append(life_card2)
                            self._log(f"  {life_card2.name} added to hand")
            else:
                # KO character
                o.cards_in_play.remove(actual_defender)
                o.trash.append(actual_defender)
                self._log(f"{attacker.name} KO's {actual_defender.name}!")

                # Trigger ON_KO and ON_YOUR_CHARACTER_KO effects
                effect_manager = get_effect_manager()
                effect_manager.on_ko(self, o, actual_defender)
        else:
            self._log(f"{attacker.name}'s attack is defended (Defense: {total_defense}).")

        # Rest the attacker
        attacker.is_resting = True
        attacker.has_attacked = True

        # Return to main phase
        self.phase = GamePhase.MAIN

    def run_turn(self):
        """Execute a full turn (for simulation/testing)."""
        if self.game_over:
            return

        player = self.current_player
        opponent = self.opponent_player

        # Reset [Activate: Main] flags at start of turn
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
                    for idx, card in sorted(blockers, key=lambda x: x[1].power or 0):
                        if attacker_power >= (card.power or 0):
                            return (idx, card)
                    # If we can't KO any blocker, still attack one to remove threat
                    return blockers[0]

                # Priority 2: Attack characters we can KO (clean removal)
                ko_targets = [(idx, card) for idx, card in rested_chars
                             if attacker_power >= (card.power or 0)]
                if ko_targets:
                    # Attack the highest power character we can KO
                    return max(ko_targets, key=lambda x: x[1].power or 0)

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
