"""
Neural network model for One Piece TCG AI.

AlphaZero-style architecture with:
- Shared encoder backbone
- Policy head (action probabilities)
- Value head (expected outcome)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Optional
import os

from .state_encoder import StateEncoder, get_encoder


class ResidualBlock(nn.Module):
    """Residual block with skip connection."""

    def __init__(self, hidden_size: int, dropout: float = 0.1):
        super().__init__()
        self.fc1 = nn.Linear(hidden_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.ln1 = nn.LayerNorm(hidden_size)
        self.ln2 = nn.LayerNorm(hidden_size)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = x
        x = self.ln1(x)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.ln2(x)
        x = self.fc2(x)
        x = self.dropout(x)
        return F.relu(x + residual)


class OPTCGNet(nn.Module):
    """
    Neural network for One Piece TCG.

    Architecture:
    - Input: Encoded game state
    - Backbone: MLP with residual connections
    - Policy head: Action probabilities (softmax)
    - Value head: Expected outcome [-1, 1]
    """

    def __init__(
        self,
        state_size: int = 512,
        action_size: int = 150,
        hidden_size: int = 256,
        num_residual_blocks: int = 4,
        dropout: float = 0.1,
    ):
        super().__init__()

        self.state_size = state_size
        self.action_size = action_size
        self.hidden_size = hidden_size

        # Input projection
        self.input_proj = nn.Sequential(
            nn.Linear(state_size, hidden_size),
            nn.LayerNorm(hidden_size),
            nn.ReLU(),
            nn.Dropout(dropout),
        )

        # Residual backbone
        self.residual_blocks = nn.ModuleList([
            ResidualBlock(hidden_size, dropout)
            for _ in range(num_residual_blocks)
        ])

        # Policy head
        self.policy_head = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.LayerNorm(hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, action_size),
        )

        # Value head
        self.value_head = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.LayerNorm(hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, 1),
            nn.Tanh(),
        )

    def forward(
        self,
        state: torch.Tensor,
        action_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass.

        Args:
            state: Encoded game state [batch, state_size]
            action_mask: Valid action mask [batch, action_size] (1=valid, 0=invalid)

        Returns:
            policy: Action probabilities [batch, action_size]
            value: Expected outcome [batch, 1]
        """
        # Backbone
        x = self.input_proj(state)

        for block in self.residual_blocks:
            x = block(x)

        # Policy head
        policy_logits = self.policy_head(x)

        # Apply action mask (set invalid actions to -inf before softmax)
        if action_mask is not None:
            # Where mask is 0 (invalid), set logits to -inf
            policy_logits = policy_logits.masked_fill(action_mask == 0, float('-inf'))

        policy = F.softmax(policy_logits, dim=-1)

        # Value head
        value = self.value_head(x)

        return policy, value

    def get_action_probs(
        self,
        state: torch.Tensor,
        action_mask: torch.Tensor,
        temperature: float = 1.0,
    ) -> torch.Tensor:
        """
        Get action probabilities with temperature scaling.

        Higher temperature = more exploration
        Lower temperature = more exploitation
        """
        with torch.no_grad():
            x = self.input_proj(state)
            for block in self.residual_blocks:
                x = block(x)

            policy_logits = self.policy_head(x)

            # Apply temperature
            policy_logits = policy_logits / temperature

            # Apply action mask
            policy_logits = policy_logits.masked_fill(action_mask == 0, float('-inf'))

            return F.softmax(policy_logits, dim=-1)

    def evaluate(
        self,
        state: torch.Tensor,
    ) -> torch.Tensor:
        """Get just the value estimate."""
        with torch.no_grad():
            x = self.input_proj(state)
            for block in self.residual_blocks:
                x = block(x)
            return self.value_head(x)


class OPTCGAgent:
    """
    Agent wrapper that combines the network with the state encoder.

    Provides a clean interface for:
    - Getting actions from game states
    - Training the network
    - Saving/loading models
    """

    def __init__(
        self,
        device: str = 'cpu',
        hidden_size: int = 256,
        num_residual_blocks: int = 4,
    ):
        self.device = device
        self.encoder = get_encoder(device)

        # Calculate actual state size from encoder
        # This is approximate - we'll pad/truncate as needed
        self.state_size = 512  # Fixed size for consistency

        self.network = OPTCGNet(
            state_size=self.state_size,
            action_size=self.encoder.action_space_size,
            hidden_size=hidden_size,
            num_residual_blocks=num_residual_blocks,
        ).to(device)

        self.optimizer = torch.optim.Adam(self.network.parameters(), lr=1e-4)

    def get_action(
        self,
        state,  # GameState
        temperature: float = 1.0,
        return_probs: bool = False,
    ):
        """
        Get an action for the given game state.

        Args:
            state: GameState object
            temperature: Exploration temperature
            return_probs: If True, also return action probabilities

        Returns:
            action: Selected Action object
            probs: (optional) Action probabilities
        """
        from core.actions import ActionValidator

        # Encode state
        encoded = self.encoder.encode(state)

        # Pad/truncate state tensor
        state_tensor = self._prepare_state_tensor(encoded.state_tensor)

        # Get action probabilities
        probs = self.network.get_action_probs(
            state_tensor.unsqueeze(0),
            encoded.valid_actions_mask.unsqueeze(0),
            temperature=temperature,
        )
        probs = probs.squeeze(0)

        # Sample action
        valid_actions = ActionValidator.get_valid_actions(state, state.active_player)

        if len(valid_actions) == 0:
            return None if not return_probs else (None, None)

        # Get probabilities for valid actions
        valid_probs = []
        for action in valid_actions:
            idx = self.encoder._action_to_index(action)
            if idx < len(probs):
                valid_probs.append(probs[idx].item())
            else:
                valid_probs.append(0.0)

        # Normalize
        total = sum(valid_probs)
        if total > 0:
            valid_probs = [p / total for p in valid_probs]
        else:
            valid_probs = [1.0 / len(valid_actions)] * len(valid_actions)

        # Sample
        import random
        action_idx = random.choices(range(len(valid_actions)), weights=valid_probs)[0]
        action = valid_actions[action_idx]

        if return_probs:
            return action, probs
        return action

    def get_value(self, state) -> float:
        """Get value estimate for a state."""
        encoded = self.encoder.encode(state)
        state_tensor = self._prepare_state_tensor(encoded.state_tensor)
        value = self.network.evaluate(state_tensor.unsqueeze(0))
        return value.item()

    def get_policy_and_value(self, state):
        """Get both policy and value for a state."""
        encoded = self.encoder.encode(state)
        state_tensor = self._prepare_state_tensor(encoded.state_tensor)

        policy, value = self.network(
            state_tensor.unsqueeze(0),
            encoded.valid_actions_mask.unsqueeze(0),
        )

        return policy.squeeze(0), value.item()

    def _prepare_state_tensor(self, state_tensor: torch.Tensor) -> torch.Tensor:
        """Pad or truncate state tensor to expected size."""
        current_size = state_tensor.shape[0]

        if current_size == self.state_size:
            return state_tensor
        elif current_size < self.state_size:
            # Pad with zeros
            padding = torch.zeros(self.state_size - current_size, device=self.device)
            return torch.cat([state_tensor, padding])
        else:
            # Truncate
            return state_tensor[:self.state_size]

    def train_step(
        self,
        states: torch.Tensor,
        action_masks: torch.Tensor,
        target_policies: torch.Tensor,
        target_values: torch.Tensor,
    ) -> dict:
        """
        Perform one training step.

        Args:
            states: Batch of state tensors [batch, state_size]
            action_masks: Batch of action masks [batch, action_size]
            target_policies: MCTS policy targets [batch, action_size]
            target_values: Game outcome targets [batch, 1]

        Returns:
            dict with loss values
        """
        self.network.train()
        self.optimizer.zero_grad()

        # Forward pass
        policy, value = self.network(states, action_masks)

        # Policy loss (cross-entropy)
        # Only compute loss for valid actions
        policy_loss = -torch.sum(target_policies * torch.log(policy + 1e-8)) / states.shape[0]

        # Value loss (MSE)
        value_loss = F.mse_loss(value, target_values)

        # Total loss
        total_loss = policy_loss + value_loss

        # Backward pass
        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.network.parameters(), 1.0)
        self.optimizer.step()

        return {
            'total_loss': total_loss.item(),
            'policy_loss': policy_loss.item(),
            'value_loss': value_loss.item(),
        }

    def save(self, path: str):
        """Save model checkpoint."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        torch.save({
            'network_state_dict': self.network.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
        }, path)
        print(f"Model saved to {path}")

    def load(self, path: str):
        """Load model checkpoint."""
        checkpoint = torch.load(path, map_location=self.device)
        self.network.load_state_dict(checkpoint['network_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        print(f"Model loaded from {path}")


def create_agent(device: str = 'cpu') -> OPTCGAgent:
    """Create a new agent."""
    return OPTCGAgent(device=device)
