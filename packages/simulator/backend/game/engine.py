"""
OPTCG Game Engine - Core game logic for One Piece TCG Simulator.
"""

from __future__ import annotations
import random
import uuid
import re
from typing import Optional, List, Tuple, Dict, Any
from .models.cards import Card
from .models.enums import GamePhase

# Constants
MAX_DON = 10
DON_PER_TURN = 2
STARTING_DON_P1 = 1
STARTING_DON_P2 = 2
MAX_FIELD_CHARACTERS = 5


class Player:
    """Represents a player in the game."""

    def __init__(self, name: str, deck: List[Card], leader: Card, player_id: str = None):
        self.player_id = player_id or str(uuid.uuid4())[:8]
        self.name = name
        self.deck = list(deck)
        self.hand: List[Card] = []
        self.cards_in_play: List[Card] = []
        self.leader = leader
        self.life_cards = self._build_life_pile(leader)
        self.don_pool: List[str] = []  # "active" or "rested"
        self.trash: List[Card] = []
        self.has_mulliganed: bool = False
        self._draw_initial_hand()

    def _build_life_pile(self, leader: Card) -> List[Card]:
        """Build life pile from deck based on leader's life value."""
        count = int(leader.life or 0)
        life_cards = []
        for _ in range(count):
            if self.deck:
                life_cards.append(self.deck.pop(0))
        return life_cards

    def _draw_initial_hand(self):
        """Draw initial 5-card hand."""
        random.shuffle(self.deck)
        self.hand = self.deck[:5]
        self.deck = self.deck[5:]

    def mulligan(self, card_indices: List[int]):
        """Mulligan selected cards."""
        if self.has_mulliganed:
            return

        cards_to_replace = [self.hand[i] for i in sorted(card_indices, reverse=True)]
        for card in cards_to_replace:
            self.hand.remove(card)
            self.deck.append(card)

        random.shuffle(self.deck)
        for _ in range(len(cards_to_replace)):
            if self.deck:
                self.hand.append(self.deck.pop(0))

        self.has_mulliganed = True

    def draw_card(self) -> Optional[Card]:
        """Draw a card from deck."""
        if self.deck:
            card = self.deck.pop(0)
            self.hand.append(card)
            return card
        return None

    def get_available_blockers(self) -> List[Tuple[int, Card]]:
        """Get characters that can block."""
        blockers = []
        for i, card in enumerate(self.cards_in_play):
            if self._can_block(card):
                blockers.append((i, card))
        return blockers

    def _can_block(self, card: Card) -> bool:
        """Check if card can block."""
        if not card.effect or '[Blocker]' not in card.effect:
            return False
        return not card.is_resting

    def activate_blocker(self, blocker_index: int) -> Optional[Card]:
        """Activate a blocker."""
        if blocker_index >= len(self.cards_in_play):
            return None
        blocker = self.cards_in_play[blocker_index]
        if not self._can_block(blocker):
            return None
        blocker.is_resting = True
        return blocker

    def available_don(self) -> int:
        """Get active DON count."""
        return self.don_pool.count("active")

    def spend_don(self, amount: int) -> bool:
        """Spend DON from pool."""
        if self.available_don() < amount:
            return False
        spent = 0
        for i in range(len(self.don_pool)):
            if self.don_pool[i] == "active" and spent < amount:
                self.don_pool[i] = "rested"
                spent += 1
        return True

    def attach_don_to_card(self, card: Card, amount: int) -> int:
        """Attach DON to a card."""
        available = self.available_don()
        actual = min(amount, available)
        card.attached_don = getattr(card, 'attached_don', 0) + actual
        self.spend_don(actual)
        return actual

    def reset_for_turn(self):
        """Reset cards for new turn (Refresh Phase)."""
        self.leader.is_resting = False
        self.leader.has_attacked = False
        self.leader.attached_don = 0

        # Reset turn-based flags
        if hasattr(self.leader, 'main_activated_this_turn'):
            self.leader.main_activated_this_turn = False

        for card in self.cards_in_play:
            card.is_resting = False
            card.has_attacked = False
            card.attached_don = 0
            card.main_activated_this_turn = False

        self.don_pool = ["active"] * len(self.don_pool)

    def take_life_damage(self) -> Tuple[Optional[Card], bool]:
        """
        Take life damage.

        Per OPTCG rules:
        1. Reveal top card of life pile
        2. If it has [Trigger], you MAY activate the effect
        3. After trigger resolution:
           - If trigger activated: card goes to trash
           - If trigger not used (or no trigger): card goes to hand

        Note: The card is NOT added to hand/trash here - that happens after
        trigger resolution in the combat resolution code.

        Returns (life_card, has_trigger)
        """
        if not self.life_cards:
            return None, False
        life_card = self.life_cards.pop()
        has_trigger = bool(life_card.trigger and life_card.trigger.strip())
        # Card destination handled by caller after trigger resolution
        return life_card, has_trigger

    def to_dict(self, hide_hand: bool = False) -> Dict[str, Any]:
        """Serialize player state."""
        return {
            "player_id": self.player_id,
            "name": self.name,
            "leader": self.leader.to_dict(),
            "life_count": len(self.life_cards),
            "hand_count": len(self.hand),
            "hand": [] if hide_hand else [c.to_dict() for c in self.hand],
            "deck_count": len(self.deck),
            "field": [c.to_dict() for c in self.cards_in_play],
            "trash_count": len(self.trash),
            "don_active": self.don_pool.count("active"),
            "don_total": len(self.don_pool),
            "has_mulliganed": self.has_mulliganed,
        }


class GameState:
    """Manages game state and turn flow."""

    def __init__(self, p1: Player, p2: Player, game_id: str = None):
        self.game_id = game_id or str(uuid.uuid4())[:8]
        self.player1 = p1
        self.player2 = p2
        self.current_player = p1
        self.opponent_player = p2
        self.turn_count = 1
        self.phase = GamePhase.MULLIGAN
        self.game_over = False
        self.winner: Optional[Player] = None
        self.action_logs: List[str] = []

        # Combat state
        self.pending_attack: Optional[Dict] = None
        self.awaiting_response: Optional[str] = None  # "blocker", "counter"

        # Initial DON
        p1.don_pool = ["active"] * STARTING_DON_P1
        p2.don_pool = ["active"] * STARTING_DON_P2

    def _log(self, message: str):
        """Add log entry."""
        self.action_logs.append(message)

    def get_logs(self) -> List[str]:
        """Get and clear logs."""
        logs = self.action_logs.copy()
        self.action_logs = []
        return logs

    def start_game(self):
        """Start the game after mulligan."""
        self.phase = GamePhase.MAIN
        self._log(f"Game started! Turn 1: {self.current_player.name}")

    def next_turn(self):
        """Advance to next turn."""
        self.turn_count += 1
        self.current_player, self.opponent_player = self.opponent_player, self.current_player

        # Refresh phase
        self.phase = GamePhase.REFRESH
        self.current_player.reset_for_turn()

        # Draw phase
        self.phase = GamePhase.DRAW
        if not (self.turn_count == 2 and self.current_player is self.player1):
            drawn = self.current_player.draw_card()
            if drawn:
                self._log(f"{self.current_player.name} draws a card")

        # DON phase
        self.phase = GamePhase.DON
        if self.turn_count > 2:
            current_don = len(self.current_player.don_pool)
            new_don = min(current_don + DON_PER_TURN, MAX_DON)
            additional = new_don - current_don
            self.current_player.don_pool.extend(["active"] * additional)

        # Main phase
        self.phase = GamePhase.MAIN
        self._log(f"Turn {self.turn_count}: {self.current_player.name}")

    def _apply_keywords(self, card: Card):
        """Parse and apply keyword effects from card text."""
        if not card.effect:
            return

        # Simple keyword parsing
        if '[Rush]' in card.effect:
            card.has_rush = True
        if '[Blocker]' in card.effect:
            card.has_blocker = True
        if '[Banish]' in card.effect:
            card.has_banish = True
        if '[Double Attack]' in card.effect:
            card.has_doubleattack = True

    def can_play_card(self, card: Card) -> bool:
        """Check if a card can be played."""
        cost = card.cost or 0
        if cost > self.current_player.available_don():
            return False
        if card.card_type == "CHARACTER":
            char_count = sum(1 for c in self.current_player.cards_in_play if c.card_type == "CHARACTER")
            if char_count >= MAX_FIELD_CHARACTERS:
                return False
        return True

    def play_card(self, card_index: int) -> bool:
        """Play a card from hand."""
        from .hardcoded import execute_hardcoded_effect
        from .resolver import resolve_effect
        from .effects import EffectTiming
        if card_index >= len(self.current_player.hand):
            return False

        card = self.current_player.hand[card_index]
        if not self.can_play_card(card):
            return False

        cost = card.cost or 0
        self.current_player.spend_don(cost)
        self.current_player.hand.remove(card)

        if card.card_type == "EVENT":
            self.current_player.trash.append(card)
            self._log(f"{self.current_player.name} plays {card.name} (Event)")
        else:
            self.current_player.cards_in_play.append(card)
            card.played_turn = self.turn_count
            # Apply keywords like Rush, Blocker, etc.
            self._apply_keywords(card)
            self._log(f"{self.current_player.name} plays {card.name}")
            
            # Trigger On Play effects
            # 1. Try Hardcoded Script (Priority for complex logic)
            if execute_hardcoded_effect(self, self.current_player, card, "ON_PLAY"):
                self._log(f"  [EFFECT] {card.name} effect activated")
            # 2. Try Parsed Effects (Standard logic)
            elif hasattr(card, 'effects') and card.effects:
                for effect in card.effects:
                    if effect.timing == EffectTiming.ON_PLAY:
                        result = resolve_effect(effect, self, card, self.current_player)
                        if result.success:
                            self._log(f"  [EFFECT] {result.message}")

        return True

    def can_attack_with_leader(self) -> bool:
        """Check if leader can attack."""
        if self.current_player is self.player1:
            return self.turn_count >= 3
        return self.turn_count >= 4

    def can_attack(self, attacker: Card) -> bool:
        """Check if a card can attack."""
        if attacker.is_resting or attacker.has_attacked:
            return False
        if attacker == self.current_player.leader:
            return self.can_attack_with_leader()
        if attacker.card_type == 'CHARACTER':
            has_rush = getattr(attacker, 'has_rush', False)
            if not has_rush and getattr(attacker, 'played_turn', 0) == self.turn_count:
                return False
        return True

    def get_valid_targets(self) -> List[Dict]:
        """Get valid attack targets."""
        targets = [{"index": -1, "card": self.opponent_player.leader, "type": "leader"}]
        for i, card in enumerate(self.opponent_player.cards_in_play):
            if card.is_resting:
                targets.append({"index": i, "card": card, "type": "character"})
        return targets

    def declare_attack(self, attacker_index: int, target_index: int) -> bool:
        """Declare an attack."""
        from .hardcoded import execute_hardcoded_effect
        from .resolver import resolve_effect
        from .effects import EffectTiming
        # Get attacker
        if attacker_index == -1:
            attacker = self.current_player.leader
        elif attacker_index < len(self.current_player.cards_in_play):
            attacker = self.current_player.cards_in_play[attacker_index]
        else:
            return False

        if not self.can_attack(attacker):
            return False

        # Get target
        if target_index == -1:
            target = self.opponent_player.leader
        elif target_index < len(self.opponent_player.cards_in_play):
            target = self.opponent_player.cards_in_play[target_index]
            if not target.is_resting:
                return False
        else:
            return False

        # Calculate attacker power
        don_boost = getattr(attacker, 'attached_don', 0) * 1000
        attacker_power = (attacker.power or 0) + don_boost

        self.pending_attack = {
            "attacker": attacker,
            "attacker_index": attacker_index,
            "target": target,
            "target_index": target_index,
            "attacker_power": attacker_power,
            "counter_power": 0,
            "blocker": None,
        }

        self.phase = GamePhase.BLOCKER_STEP
        self.awaiting_response = "blocker"

        self._log(f"{attacker.name} ({attacker_power}) attacks {target.name}!")
        
        # Trigger When Attacking effects
        if execute_hardcoded_effect(self, self.current_player, attacker, "WHEN_ATTACKING"):
            self._log(f"  [EFFECT] {attacker.name} effect activated")
        elif hasattr(attacker, 'effects') and attacker.effects:
            for effect in attacker.effects:
                if effect.timing == EffectTiming.WHEN_ATTACKING:
                    result = resolve_effect(effect, self, attacker, self.current_player)
                    if result.success:
                        self._log(f"  [EFFECT] {result.message}")
        return True

    def respond_blocker(self, blocker_index: Optional[int] = None) -> bool:
        """Respond with blocker or pass."""
        if not self.pending_attack or self.awaiting_response != "blocker":
            return False

        if blocker_index is not None:
            blocker = self.opponent_player.activate_blocker(blocker_index)
            if blocker:
                self.pending_attack["target"] = blocker
                self.pending_attack["blocker"] = blocker
                self._log(f"{blocker.name} blocks!")

        self.phase = GamePhase.COUNTER_STEP
        self.awaiting_response = "counter"
        return True

    def respond_counter(self, counter_indices: List[int] = None) -> bool:
        """Use counter cards or pass."""
        if not self.pending_attack or self.awaiting_response != "counter":
            return False

        counter_power = 0
        if counter_indices:
            for idx in sorted(counter_indices, reverse=True):
                if idx < len(self.opponent_player.hand):
                    card = self.opponent_player.hand[idx]
                    if card.counter and card.counter > 0:
                        counter_power += card.counter
                        self.opponent_player.hand.remove(card)
                        self.opponent_player.trash.append(card)
                        self._log(f"{self.opponent_player.name} uses {card.name} (+{card.counter})")

        self.pending_attack["counter_power"] = counter_power
        self._resolve_attack()
        return True

    def _resolve_attack(self):
        """Resolve the pending attack."""
        if not self.pending_attack:
            return

        attack = self.pending_attack
        attacker = attack["attacker"]
        target = attack["target"]
        attacker_power = attack["attacker_power"]
        counter_power = attack["counter_power"]

        target_power = (target.power or 0) + counter_power
        target_don = getattr(target, 'attached_don', 0) * 1000
        total_defense = target_power + target_don

        self.phase = GamePhase.DAMAGE_STEP

        if attacker_power >= total_defense:
            if target.card_type == 'LEADER' or target == self.opponent_player.leader:
                # Check for Banish
                has_banish = getattr(attacker, 'has_banish', False)
                # Fallback check if keyword wasn't applied yet
                if not has_banish and attacker.effect and '[Banish]' in attacker.effect: has_banish = True

                # Deal life damage
                life_card, has_trigger = self.opponent_player.take_life_damage()
                self._log(f"{self.opponent_player.name} takes damage! ({len(self.opponent_player.life_cards)} life remaining)")

                if len(self.opponent_player.life_cards) == 0:
                    self.game_over = True
                    self.winner = self.current_player
                    self.phase = GamePhase.GAME_OVER
                    self._log(f"{self.current_player.name} wins!")
                elif life_card:
                    # Handle trigger and life card destination
                    trigger_activated = False
                    card_was_played = False

                    if has_trigger and not has_banish:
                        self._log(f"  [TRIGGER] {life_card.name}: {life_card.trigger}")
                        trigger_activated = True
                        # TODO: Resolve actual trigger effects here
                        # For now, check if it's a "Play this card" trigger
                        if life_card.trigger and 'play this card' in life_card.trigger.lower():
                            # Play the card for free
                            char_count = sum(1 for c in self.opponent_player.cards_in_play if c.card_type == 'CHARACTER')
                            if life_card.card_type != 'CHARACTER' or char_count < MAX_FIELD_CHARACTERS:
                                self.opponent_player.cards_in_play.append(life_card)
                                card_was_played = True
                                self._log(f"    {life_card.name} played from trigger!")

                    # Life card destination:
                    # - If played by trigger: already on field
                    # - If trigger activated: goes to trash
                    # - If no trigger (or banished): goes to hand
                    if not card_was_played:
                        if has_banish or trigger_activated:
                            self.opponent_player.trash.append(life_card)
                            if has_banish:
                                self._log(f"  {life_card.name} banished to trash")
                            else:
                                self._log(f"  {life_card.name} sent to trash (trigger used)")
                        else:
                            self.opponent_player.hand.append(life_card)
                            self._log(f"  {life_card.name} added to hand")

                # Check for Double Attack
                has_double = getattr(attacker, 'has_doubleattack', False)
                if not has_double and attacker.effect and '[Double Attack]' in attacker.effect: has_double = True

                if has_double and not self.game_over and len(self.opponent_player.life_cards) > 0:
                    self._log(f"{attacker.name} has Double Attack!")
                    life_card2, has_trigger2 = self.opponent_player.take_life_damage()
                    
                    if len(self.opponent_player.life_cards) == 0:
                        self.game_over = True
                        self.winner = self.current_player
                        self.phase = GamePhase.GAME_OVER
                        self._log(f"{self.current_player.name} wins!")
                    elif life_card2:
                        # Handle second card logic (simplified for now)
                        trigger2_activated = False
                        if has_trigger2 and not has_banish:
                             self._log(f"  [TRIGGER] {life_card2.name}: {life_card2.trigger}")
                             trigger2_activated = True
                             # TODO: Resolve trigger
                        
                        if has_banish or trigger2_activated:
                            self.opponent_player.trash.append(life_card2)
                            if has_banish: self._log(f"  {life_card2.name} banished")
                            else: self._log(f"  {life_card2.name} sent to trash")
                        else:
                            self.opponent_player.hand.append(life_card2)
                            self._log(f"  {life_card2.name} added to hand")

            else:
                # KO character
                self.opponent_player.cards_in_play.remove(target)
                self.opponent_player.trash.append(target)
                self._log(f"{target.name} is KO'd!")
        else:
            self._log(f"Attack defended! (Defense: {total_defense})")

        # Rest attacker
        attacker.is_resting = True
        attacker.has_attacked = True

        # Clear attack state
        self.pending_attack = None
        self.awaiting_response = None
        self.phase = GamePhase.MAIN

    def attach_don(self, card_index: int, amount: int = 1) -> bool:
        """Attach DON to a card."""
        if card_index == -1:
            card = self.current_player.leader
        elif card_index < len(self.current_player.cards_in_play):
            card = self.current_player.cards_in_play[card_index]
        else:
            return False

        attached = self.current_player.attach_don_to_card(card, amount)
        if attached > 0:
            self._log(f"Attached {attached} DON to {card.name}")
            return True
        return False

    def to_dict(self, for_player: Optional[str] = None) -> Dict[str, Any]:
        """Serialize game state."""
        hide_p1 = for_player and for_player != self.player1.player_id
        hide_p2 = for_player and for_player != self.player2.player_id

        current_idx = 0 if self.current_player == self.player1 else 1

        return {
            "game_id": self.game_id,
            "turn": self.turn_count,
            "phase": self.phase.name,
            "active_player": current_idx,
            "players": [
                self.player1.to_dict(hide_hand=hide_p1),
                self.player2.to_dict(hide_hand=hide_p2),
            ],
            "is_terminal": self.game_over,
            "winner": (0 if self.winner == self.player1 else 1) if self.winner else None,
            "awaiting_response": self.awaiting_response,
            "pending_attack": {
                "attacker_power": self.pending_attack["attacker_power"],
                "target_name": self.pending_attack["target"].name,
            } if self.pending_attack else None,
        }
