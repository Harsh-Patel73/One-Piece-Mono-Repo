"""
State encoder for neural network input.

Converts GameState to tensor representation for the neural network.
Encodes from the perspective of the current player.
"""

import torch
import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass

from core.game_state import GameState, PlayerState, CardInstance, CombatContext
from models.enums import GamePhase


# Feature dimensions
MAX_HAND_SIZE = 10
MAX_FIELD_SIZE = 5
MAX_LIFE_SIZE = 5
MAX_DON = 10
MAX_COST = 10
MAX_POWER = 12000
MAX_COUNTER = 2000

# Card feature size
CARD_FEATURES = 12  # cost, power, counter, type, keywords, etc.

# Total state size
GLOBAL_FEATURES = 20  # Turn, phase, DON, life counts, etc.
PLAYER_CARD_FEATURES = (MAX_HAND_SIZE + MAX_FIELD_SIZE + 1 + MAX_LIFE_SIZE) * CARD_FEATURES  # hand + field + leader + life
STATE_SIZE = GLOBAL_FEATURES + 2 * PLAYER_CARD_FEATURES  # Both players


@dataclass
class EncodedState:
    """Encoded game state as tensors."""
    state_tensor: torch.Tensor      # Main state encoding
    valid_actions_mask: torch.Tensor  # Binary mask of valid actions
    action_indices: List[int]       # Mapping from mask index to action


class StateEncoder:
    """
    Encodes GameState into tensor format for neural network.

    The encoding is always from the perspective of the current player,
    meaning their information comes first in the tensor.
    """

    def __init__(self, device: str = 'cpu'):
        self.device = device

        # Action space size (simplified for now)
        # We'll use a fixed action space and mask invalid actions
        self.action_space_size = self._calculate_action_space_size()

    def _calculate_action_space_size(self) -> int:
        """
        Calculate total action space size.

        Actions:
        - PASS: 1
        - PASS_TURN: 1
        - KEEP_HAND: 1
        - DECLINE_BLOCK: 1
        - PLAY_CARD: MAX_HAND_SIZE (10)
        - ATTACH_DON: (1 + MAX_FIELD_SIZE) * MAX_DON = 60 (leader + 5 chars, up to 10 DON each)
        - ATTACK: (1 + MAX_FIELD_SIZE) * (1 + MAX_FIELD_SIZE) = 36 (6 attackers x 6 targets)
        - USE_COUNTER: MAX_HAND_SIZE (10)
        - ACTIVATE_BLOCKER: MAX_FIELD_SIZE (5)
        - MULLIGAN: MAX_HAND_SIZE (10, simplified single card)
        - DISCARD: MAX_HAND_SIZE (10, simplified single card)

        Total: ~145 actions
        """
        return 150  # Padded for safety

    def encode(self, state: GameState) -> EncodedState:
        """
        Encode a game state into tensor format.

        Returns an EncodedState with:
        - state_tensor: The full state encoding
        - valid_actions_mask: Binary mask of valid actions
        - action_indices: List mapping mask indices to actual actions
        """
        # Encode state
        state_tensor = self._encode_state(state)

        # Get valid actions and create mask
        from core.actions import ActionValidator
        valid_actions = ActionValidator.get_valid_actions(state, state.active_player)

        # Create action mask and index mapping
        action_mask = torch.zeros(self.action_space_size, device=self.device)
        action_indices = []

        for i, action in enumerate(valid_actions):
            action_idx = self._action_to_index(action)
            if action_idx < self.action_space_size:
                action_mask[action_idx] = 1.0
                action_indices.append(action_idx)

        return EncodedState(
            state_tensor=state_tensor,
            valid_actions_mask=action_mask,
            action_indices=action_indices,
        )

    def _encode_state(self, state: GameState) -> torch.Tensor:
        """Encode the full game state."""
        features = []

        # Global features
        features.extend(self._encode_global(state))

        # Current player (from their perspective)
        features.extend(self._encode_player(state.current_player, is_current=True))

        # Opponent
        features.extend(self._encode_player(state.opponent_player, is_current=False))

        return torch.tensor(features, dtype=torch.float32, device=self.device)

    def _encode_global(self, state: GameState) -> List[float]:
        """Encode global game features."""
        features = []

        # Turn number (normalized)
        features.append(min(state.turn / 20.0, 1.0))

        # Phase (one-hot)
        phase_encoding = [0.0] * 10
        phase_idx = min(state.phase.value, 9)
        phase_encoding[phase_idx] = 1.0
        features.extend(phase_encoding)

        # Is in combat
        features.append(1.0 if state.combat else 0.0)

        # Combat context (if applicable)
        if state.combat:
            features.append(state.combat.attacker_power / MAX_POWER)
            features.append(state.combat.counter_total / MAX_POWER)
            features.append(1.0 if state.combat.blocker_index is not None else 0.0)
        else:
            features.extend([0.0, 0.0, 0.0])

        # Is terminal
        features.append(1.0 if state.is_terminal else 0.0)

        # Winner (from current player perspective)
        if state.winner is not None:
            features.append(1.0 if state.winner == state.active_player else -1.0)
        else:
            features.append(0.0)

        # Padding to GLOBAL_FEATURES
        while len(features) < GLOBAL_FEATURES:
            features.append(0.0)

        return features[:GLOBAL_FEATURES]

    def _encode_player(self, player: PlayerState, is_current: bool) -> List[float]:
        """Encode a player's state."""
        features = []

        # Player indicator
        features.append(1.0 if is_current else 0.0)

        # DON (normalized)
        features.append(player.don_active / MAX_DON)
        features.append(player.don_rested / MAX_DON)
        features.append(player.total_don / MAX_DON)

        # Life count
        features.append(player.life_count / MAX_LIFE_SIZE)

        # Hand size (opponent hand is hidden but we know size)
        features.append(len(player.hand) / MAX_HAND_SIZE)

        # Deck size (normalized)
        features.append(min(player.deck_size / 50.0, 1.0))

        # Field size
        features.append(len(player.field) / MAX_FIELD_SIZE)

        # Leader
        features.extend(self._encode_card(player.leader))

        # Hand cards (pad to MAX_HAND_SIZE)
        for i in range(MAX_HAND_SIZE):
            if i < len(player.hand):
                if is_current:
                    # Current player sees their own hand
                    features.extend(self._encode_card(player.hand[i]))
                else:
                    # Opponent hand is hidden - just mark as present
                    features.extend(self._encode_hidden_card())
            else:
                features.extend(self._encode_empty_slot())

        # Field cards (pad to MAX_FIELD_SIZE)
        for i in range(MAX_FIELD_SIZE):
            if i < len(player.field):
                features.extend(self._encode_card(player.field[i]))
            else:
                features.extend(self._encode_empty_slot())

        # Life cards (hidden information - just encode count)
        for i in range(MAX_LIFE_SIZE):
            if i < len(player.life_cards):
                features.extend(self._encode_hidden_card())
            else:
                features.extend(self._encode_empty_slot())

        return features

    def _encode_card(self, card: CardInstance) -> List[float]:
        """Encode a single card's features."""
        features = []

        # Exists
        features.append(1.0)

        # Cost (normalized)
        cost = card.cost if card.cost is not None else 0
        features.append(min(cost / MAX_COST, 1.0))

        # Power (normalized)
        power = card.card.power if card.card.power else 0
        features.append(power / MAX_POWER)

        # Total power with modifiers
        features.append(card.total_power / MAX_POWER)

        # Counter value
        counter = card.counter if card.counter else 0
        features.append(counter / MAX_COUNTER)

        # Card type (one-hot: Leader=0, Character=1, Event=2, Stage=3)
        type_encoding = [0.0, 0.0, 0.0, 0.0]
        card_type = card.card_type.lower() if card.card_type else 'character'
        if card_type == 'leader':
            type_encoding[0] = 1.0
        elif card_type == 'character':
            type_encoding[1] = 1.0
        elif card_type == 'event':
            type_encoding[2] = 1.0
        elif card_type == 'stage':
            type_encoding[3] = 1.0
        features.extend(type_encoding)

        # Keywords
        features.append(1.0 if card.has_rush else 0.0)
        features.append(1.0 if card.has_blocker else 0.0)
        features.append(1.0 if card.has_banish else 0.0)

        # State
        features.append(1.0 if card.is_resting else 0.0)
        features.append(1.0 if card.has_attacked else 0.0)

        # Attached DON
        features.append(card.attached_don / MAX_DON)

        # Ensure exactly CARD_FEATURES
        return features[:CARD_FEATURES]

    def _encode_hidden_card(self) -> List[float]:
        """Encode a hidden card (opponent's hand, life cards)."""
        features = [1.0]  # Exists
        features.extend([0.0] * (CARD_FEATURES - 1))  # Unknown features
        return features

    def _encode_empty_slot(self) -> List[float]:
        """Encode an empty card slot."""
        return [0.0] * CARD_FEATURES

    def _action_to_index(self, action) -> int:
        """
        Convert an action to an index in the action space.

        This creates a fixed mapping from actions to indices.
        """
        from core.actions import ActionType, LEADER_TARGET

        base = 0

        if action.action_type == ActionType.PASS:
            return 0
        base += 1

        if action.action_type == ActionType.PASS_TURN:
            return base
        base += 1

        if action.action_type == ActionType.KEEP_HAND:
            return base
        base += 1

        if action.action_type == ActionType.DECLINE_BLOCK:
            return base
        base += 1

        # PLAY_CARD: indices 4-13 (hand positions 0-9)
        if action.action_type == ActionType.PLAY_CARD:
            return base + (action.card_index or 0)
        base += MAX_HAND_SIZE

        # ATTACH_DON: indices 14-73
        # Layout: 6 targets (leader + 5 field) x 10 DON amounts
        if action.action_type == ActionType.ATTACH_DON:
            target = action.card_index if action.card_index != LEADER_TARGET else -1
            target_idx = target + 1  # -1 becomes 0, 0 becomes 1, etc.
            don_idx = (action.don_amount or 1) - 1
            return base + target_idx * MAX_DON + don_idx
        base += 6 * MAX_DON

        # ATTACK: indices 74-109
        # Layout: 6 attackers x 6 targets
        if action.action_type == ActionType.ATTACK:
            attacker = action.card_index if action.card_index != LEADER_TARGET else -1
            target = action.target_index if action.target_index != LEADER_TARGET else -1
            attacker_idx = attacker + 1
            target_idx = target + 1
            return base + attacker_idx * 6 + target_idx
        base += 36

        # USE_COUNTER: indices 110-119
        if action.action_type == ActionType.USE_COUNTER:
            return base + (action.card_index or 0)
        base += MAX_HAND_SIZE

        # ACTIVATE_BLOCKER: indices 120-124
        if action.action_type == ActionType.ACTIVATE_BLOCKER:
            return base + (action.card_index or 0)
        base += MAX_FIELD_SIZE

        # MULLIGAN: indices 125-134 (single card)
        if action.action_type == ActionType.MULLIGAN:
            if action.card_indices:
                return base + action.card_indices[0]
            return base
        base += MAX_HAND_SIZE

        # DISCARD: indices 135-144 (single card)
        if action.action_type == ActionType.DISCARD:
            if action.card_indices:
                return base + action.card_indices[0]
            return base
        base += MAX_HAND_SIZE

        # Default
        return min(base, self.action_space_size - 1)

    def index_to_action(self, index: int, state: GameState, valid_actions: List) -> Optional:
        """
        Convert an action index back to an Action object.

        Uses the valid_actions list to find the matching action.
        """
        for action in valid_actions:
            if self._action_to_index(action) == index:
                return action
        return None

    def get_state_size(self) -> int:
        """Get the size of the state tensor."""
        return GLOBAL_FEATURES + 2 * (8 + CARD_FEATURES * (1 + MAX_HAND_SIZE + MAX_FIELD_SIZE + MAX_LIFE_SIZE))


# Singleton instance
_encoder = None

def get_encoder(device: str = 'cpu') -> StateEncoder:
    """Get or create the state encoder singleton."""
    global _encoder
    if _encoder is None:
        _encoder = StateEncoder(device)
    return _encoder
