"""
Self-play training for One Piece TCG AI.

Implements the AlphaZero-style training loop:
1. Self-play to generate games
2. Train network on game data
3. Evaluate and checkpoint
"""

import os
import time
import random
import torch
import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass, field
from collections import deque
from datetime import datetime

from core.game_state import GameState, create_initial_state
from core.actions import ActionValidator
from models.cards import Card
from data.card_loader import load_card_database
from decks.deck_loader import load_deck

from .network import OPTCGAgent, create_agent
from .mcts import MCTS


@dataclass
class GameExperience:
    """Experience from a single game position."""
    state_tensor: torch.Tensor
    action_mask: torch.Tensor
    policy: np.ndarray  # MCTS policy
    value: float  # Final game outcome from this player's perspective


@dataclass
class TrainingConfig:
    """Configuration for training."""
    # Self-play
    num_games_per_iteration: int = 100
    mcts_simulations: int = 50
    temperature: float = 1.0
    temperature_drop_turn: int = 10
    max_turns: int = 100

    # Training
    batch_size: int = 64
    epochs_per_iteration: int = 5
    learning_rate: float = 1e-4
    replay_buffer_size: int = 50000

    # Checkpointing
    checkpoint_interval: int = 10
    checkpoint_dir: str = "checkpoints"

    # Device
    device: str = "cuda" if torch.cuda.is_available() else "cpu"


class ReplayBuffer:
    """Experience replay buffer for training."""

    def __init__(self, max_size: int = 50000):
        self.buffer = deque(maxlen=max_size)

    def add(self, experience: GameExperience):
        """Add an experience to the buffer."""
        self.buffer.append(experience)

    def add_game(self, experiences: List[GameExperience]):
        """Add all experiences from a game."""
        for exp in experiences:
            self.add(exp)

    def sample(self, batch_size: int) -> List[GameExperience]:
        """Sample a batch of experiences."""
        if len(self.buffer) < batch_size:
            return list(self.buffer)
        return random.sample(list(self.buffer), batch_size)

    def __len__(self):
        return len(self.buffer)


class SelfPlayTrainer:
    """
    Main training class for self-play learning.

    Training loop:
    1. Generate games through self-play with MCTS
    2. Store experiences in replay buffer
    3. Train network on sampled experiences
    4. Periodically checkpoint the model
    """

    def __init__(self, config: TrainingConfig = None):
        self.config = config or TrainingConfig()

        # Create agent
        self.agent = create_agent(device=self.config.device)

        # Create MCTS
        self.mcts = MCTS(
            agent=self.agent,
            num_simulations=self.config.mcts_simulations,
        )

        # Replay buffer
        self.replay_buffer = ReplayBuffer(max_size=self.config.replay_buffer_size)

        # Training stats
        self.iteration = 0
        self.total_games = 0
        self.win_rates = []

        # Load card data
        self._load_game_data()

    def _load_game_data(self):
        """Load card database and available decks."""
        import os
        from pathlib import Path

        try:
            # Load card database
            db_path = Path(__file__).parent.parent / "data" / "english_cards.json"
            self.card_db = load_card_database(str(db_path))

            # Find available deck files
            decks_dir = Path(__file__).parent.parent / "decks"
            self.deck_files = []
            for f in decks_dir.glob("*.json"):
                if f.name != "deck_loader.py":  # Skip non-deck files
                    self.deck_files.append(str(f))

            print(f"Loaded {len(self.card_db)} cards")
            print(f"Available decks: {[Path(d).stem for d in self.deck_files]}")
        except Exception as e:
            print(f"Warning: Could not load card data: {e}")
            self.card_db = {}
            self.deck_files = []

    def train(self, num_iterations: int = 100):
        """
        Run the training loop.

        Args:
            num_iterations: Number of training iterations
        """
        print(f"Starting training for {num_iterations} iterations")
        print(f"Device: {self.config.device}")
        print(f"Games per iteration: {self.config.num_games_per_iteration}")
        print(f"MCTS simulations: {self.config.mcts_simulations}")
        print()

        for i in range(num_iterations):
            self.iteration = i + 1
            start_time = time.time()

            # Self-play phase
            print(f"Iteration {self.iteration}: Self-play...")
            games_played, experiences = self._run_self_play()
            self.total_games += games_played

            # Training phase
            print(f"Iteration {self.iteration}: Training on {len(self.replay_buffer)} experiences...")
            losses = self._train()

            # Stats
            elapsed = time.time() - start_time
            print(f"Iteration {self.iteration} complete:")
            print(f"  Games: {games_played}, Total games: {self.total_games}")
            print(f"  Buffer size: {len(self.replay_buffer)}")
            print(f"  Loss: {losses['total_loss']:.4f} (policy: {losses['policy_loss']:.4f}, value: {losses['value_loss']:.4f})")
            print(f"  Time: {elapsed:.1f}s")
            print()

            # Checkpoint
            if self.iteration % self.config.checkpoint_interval == 0:
                self._save_checkpoint()

        # Final checkpoint
        self._save_checkpoint()
        print("Training complete!")

    def _run_self_play(self) -> Tuple[int, int]:
        """
        Run self-play games to generate training data.

        Returns:
            (games_played, total_experiences)
        """
        games_played = 0
        total_experiences = 0

        for _ in range(self.config.num_games_per_iteration):
            try:
                experiences = self._play_game()
                self.replay_buffer.add_game(experiences)
                games_played += 1
                total_experiences += len(experiences)
            except Exception as e:
                print(f"  Game error: {e}")
                continue

        return games_played, total_experiences

    def _play_game(self) -> List[GameExperience]:
        """
        Play a single self-play game.

        Returns:
            List of experiences from the game
        """
        # Create game state
        state = self._create_game()
        if state is None:
            return []

        experiences = {0: [], 1: []}  # Experiences for each player
        turn = 0

        while not state.is_terminal and turn < self.config.max_turns:
            # Get current player
            current_player = state.active_player

            # Get valid actions
            valid_actions = ActionValidator.get_valid_actions(state, current_player)
            if len(valid_actions) == 0:
                break

            # Temperature scheduling
            temp = self.config.temperature if turn < self.config.temperature_drop_turn else 0.1

            # Run MCTS
            policy, action = self.mcts.search(state)

            if action is None:
                break

            # Store experience
            encoded = self.agent.encoder.encode(state)
            experiences[current_player].append({
                'state_tensor': encoded.state_tensor.clone(),
                'action_mask': encoded.valid_actions_mask.clone(),
                'policy': policy.copy(),
            })

            # Apply action
            state = self.mcts.simulator.apply_action(state, action)
            turn += 1

        # Determine outcome and create final experiences
        final_experiences = []
        winner = state.winner

        for player_idx in [0, 1]:
            if winner is not None:
                value = 1.0 if winner == player_idx else -1.0
            else:
                value = 0.0  # Draw

            for exp in experiences[player_idx]:
                final_experiences.append(GameExperience(
                    state_tensor=exp['state_tensor'],
                    action_mask=exp['action_mask'],
                    policy=exp['policy'],
                    value=value,
                ))

        return final_experiences

    def _create_game(self) -> Optional[GameState]:
        """Create a new game state."""
        if not self.deck_files or len(self.deck_files) < 1:
            return self._create_dummy_game()

        try:
            # Select random decks for each player
            deck1_path = random.choice(self.deck_files)
            deck2_path = random.choice(self.deck_files)

            deck1_cards, leader1 = load_deck(deck1_path, self.card_db)
            deck2_cards, leader2 = load_deck(deck2_path, self.card_db)

            if leader1 is None or leader2 is None:
                return self._create_dummy_game()

            return create_initial_state(
                player1_name="Player1",
                player1_leader=leader1,
                player1_deck=deck1_cards,
                player2_name="Player2",
                player2_leader=leader2,
                player2_deck=deck2_cards,
            )
        except Exception as e:
            print(f"  Could not create game: {e}")
            return self._create_dummy_game()

    def _create_dummy_game(self) -> Optional[GameState]:
        """Create a minimal game for testing when deck data isn't available."""
        try:
            # Create dummy leader
            leader = Card(
                id="LEADER-001",
                id_normal="LEADER-001",
                name="Dummy Leader",
                card_type="Leader",
                cost=0,
                power=5000,
                counter=None,
                colors=["Red"],
                life=5,
                effect="",
                image_link="",
                attribute="",
                card_origin="",
                trigger="",
            )

            # Create dummy deck (50 cards)
            deck = []
            for i in range(50):
                card = Card(
                    id=f"CHAR-{i:03d}",
                    id_normal=f"CHAR-{i:03d}",
                    name=f"Character {i}",
                    card_type="Character",
                    cost=i % 5 + 1,
                    power=(i % 4 + 2) * 1000,
                    counter=1000 if i % 3 == 0 else None,
                    colors=["Red"],
                    life=None,
                    effect="",
                    image_link="",
                    attribute="",
                    card_origin="",
                    trigger="",
                )
                deck.append(card)

            return create_initial_state(
                player1_name="Player1",
                player1_leader=leader,
                player1_deck=deck.copy(),
                player2_name="Player2",
                player2_leader=leader,
                player2_deck=deck.copy(),
            )
        except Exception as e:
            print(f"  Could not create dummy game: {e}")
            return None

    def _train(self) -> dict:
        """
        Train the network on sampled experiences.

        Returns:
            Dictionary of loss values
        """
        if len(self.replay_buffer) < self.config.batch_size:
            return {'total_loss': 0, 'policy_loss': 0, 'value_loss': 0}

        total_loss = 0
        policy_loss = 0
        value_loss = 0
        num_batches = 0

        for _ in range(self.config.epochs_per_iteration):
            # Sample batch
            batch = self.replay_buffer.sample(self.config.batch_size)

            # Prepare tensors
            states = torch.stack([exp.state_tensor for exp in batch])
            action_masks = torch.stack([exp.action_mask for exp in batch])
            target_policies = torch.tensor(
                np.stack([exp.policy for exp in batch]),
                dtype=torch.float32,
                device=self.config.device,
            )
            target_values = torch.tensor(
                [[exp.value] for exp in batch],
                dtype=torch.float32,
                device=self.config.device,
            )

            # Pad states to expected size
            states = self._pad_states(states)

            # Training step
            losses = self.agent.train_step(
                states=states.to(self.config.device),
                action_masks=action_masks.to(self.config.device),
                target_policies=target_policies,
                target_values=target_values,
            )

            total_loss += losses['total_loss']
            policy_loss += losses['policy_loss']
            value_loss += losses['value_loss']
            num_batches += 1

        if num_batches > 0:
            total_loss /= num_batches
            policy_loss /= num_batches
            value_loss /= num_batches

        return {
            'total_loss': total_loss,
            'policy_loss': policy_loss,
            'value_loss': value_loss,
        }

    def _pad_states(self, states: torch.Tensor) -> torch.Tensor:
        """Pad states to the expected size."""
        current_size = states.shape[1]
        target_size = self.agent.state_size

        if current_size == target_size:
            return states
        elif current_size < target_size:
            padding = torch.zeros(
                states.shape[0],
                target_size - current_size,
                device=states.device,
            )
            return torch.cat([states, padding], dim=1)
        else:
            return states[:, :target_size]

    def _save_checkpoint(self):
        """Save a training checkpoint."""
        os.makedirs(self.config.checkpoint_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"optcg_iter{self.iteration}_{timestamp}.pt"
        path = os.path.join(self.config.checkpoint_dir, filename)

        self.agent.save(path)
        print(f"Checkpoint saved: {path}")

        # Also save as 'latest'
        latest_path = os.path.join(self.config.checkpoint_dir, "latest.pt")
        self.agent.save(latest_path)


def train_model(
    num_iterations: int = 100,
    games_per_iteration: int = 10,
    mcts_simulations: int = 50,
    checkpoint_dir: str = "checkpoints",
):
    """
    Main entry point for training.

    Args:
        num_iterations: Number of training iterations
        games_per_iteration: Games to play per iteration
        mcts_simulations: MCTS simulations per move
        checkpoint_dir: Directory to save checkpoints
    """
    config = TrainingConfig(
        num_games_per_iteration=games_per_iteration,
        mcts_simulations=mcts_simulations,
        checkpoint_dir=checkpoint_dir,
    )

    trainer = SelfPlayTrainer(config)
    trainer.train(num_iterations)


if __name__ == "__main__":
    # Quick test
    print("Starting training test...")
    train_model(
        num_iterations=2,
        games_per_iteration=2,
        mcts_simulations=10,
    )
