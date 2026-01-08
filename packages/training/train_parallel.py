"""
Parallel self-play training for One Piece TCG AI.

Uses multiple processes to generate games in parallel,
dramatically increasing throughput.

Usage:
    python train_parallel.py --workers 4
    python train_parallel.py --resume --workers 8
"""

import os
import sys
import time
import json
import random
import argparse
import torch
import numpy as np
from datetime import datetime
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import Manager, cpu_count
from collections import deque
from dataclasses import dataclass
from typing import List, Optional, Tuple

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))


@dataclass
class GameResult:
    """Result from a single self-play game."""
    experiences: List[dict]
    winner: Optional[int]
    turns: int
    error: Optional[str] = None


def play_single_game(
    game_id: int,
    mcts_sims: int,
    model_path: Optional[str],
    max_turns: int = 100,
    deck1_name: Optional[str] = None,
    deck2_name: Optional[str] = None,
) -> GameResult:
    """
    Play a single self-play game.

    This runs in a separate process.
    """
    try:
        # Import inside process to avoid CUDA issues
        from core.game_state import create_initial_state
        from core.actions import ActionValidator
        from models.cards import Card
        from data.card_loader import load_card_database
        from decks.deck_loader import load_deck
        from ai.network import create_agent
        from ai.mcts import MCTS

        # Create agent
        agent = create_agent(device='cpu')  # Use CPU in workers

        # Load model if available
        if model_path and os.path.exists(model_path):
            try:
                agent.load(model_path)
            except:
                pass

        # Create MCTS
        mcts = MCTS(agent=agent, num_simulations=mcts_sims)

        # Load game data
        db_path = Path(__file__).parent / "data" / "english_cards.json"
        card_db = load_card_database(str(db_path))

        decks_dir = Path(__file__).parent / "decks"
        deck_files = list(decks_dir.glob("*.json"))

        if len(deck_files) >= 1:
            # Use specific decks if provided, otherwise random
            if deck1_name:
                deck1_path = decks_dir / f"{deck1_name}.json"
                if not deck1_path.exists():
                    deck1_path = random.choice(deck_files)
            else:
                deck1_path = random.choice(deck_files)

            if deck2_name:
                deck2_path = decks_dir / f"{deck2_name}.json"
                if not deck2_path.exists():
                    deck2_path = random.choice(deck_files)
            else:
                deck2_path = random.choice(deck_files)

            deck1, leader1 = load_deck(str(deck1_path), card_db)
            deck2, leader2 = load_deck(str(deck2_path), card_db)

            if leader1 is None or leader2 is None:
                raise ValueError("Could not load leaders")

            state = create_initial_state(
                "P1", leader1, deck1,
                "P2", leader2, deck2
            )
        else:
            # Create dummy game
            leader = Card(
                id="L-001", id_normal="L-001", name="Leader",
                card_type="Leader", cost=0, power=5000, counter=None,
                colors=["Red"], life=5, effect="", image_link="",
                attribute="", card_origin="", trigger=""
            )
            deck = [Card(
                id=f"C-{i}", id_normal=f"C-{i}", name=f"Char {i}",
                card_type="Character", cost=2, power=4000, counter=1000,
                colors=["Red"], life=None, effect="", image_link="",
                attribute="", card_origin="", trigger=""
            ) for i in range(50)]

            state = create_initial_state("P1", leader, deck, "P2", leader, deck.copy())

        # Play game
        experiences = {0: [], 1: []}
        turn = 0

        while not state.is_terminal and turn < max_turns:
            current_player = state.active_player

            valid_actions = ActionValidator.get_valid_actions(state, current_player)
            if len(valid_actions) == 0:
                break

            # Run MCTS
            policy, action = mcts.search(state)
            if action is None:
                break

            # Store experience
            encoded = agent.encoder.encode(state)
            experiences[current_player].append({
                'state': encoded.state_tensor.cpu().numpy(),
                'mask': encoded.valid_actions_mask.cpu().numpy(),
                'policy': policy.copy(),
            })

            # Apply action
            state = mcts.simulator.apply_action(state, action)
            turn += 1

        # Determine outcome
        winner = state.winner
        final_experiences = []

        for player_idx in [0, 1]:
            value = 0.0
            if winner is not None:
                value = 1.0 if winner == player_idx else -1.0

            for exp in experiences[player_idx]:
                final_experiences.append({
                    'state': exp['state'],
                    'mask': exp['mask'],
                    'policy': exp['policy'],
                    'value': value,
                })

        return GameResult(
            experiences=final_experiences,
            winner=winner,
            turns=turn,
        )

    except Exception as e:
        return GameResult(
            experiences=[],
            winner=None,
            turns=0,
            error=str(e),
        )


class ParallelTrainer:
    """
    Parallel self-play trainer.

    Uses multiple processes to generate games while
    training on a central GPU.
    """

    def __init__(
        self,
        num_workers: int = 4,
        mcts_simulations: int = 5,
        batch_size: int = 128,
        buffer_size: int = 100_000,
        checkpoint_dir: str = "checkpoints",
        deck1_name: Optional[str] = None,
        deck2_name: Optional[str] = None,
    ):
        self.num_workers = num_workers
        self.mcts_simulations = mcts_simulations
        self.batch_size = batch_size
        self.checkpoint_dir = checkpoint_dir
        self.deck1_name = deck1_name
        self.deck2_name = deck2_name

        # Replay buffer
        self.buffer = deque(maxlen=buffer_size)

        # Create central agent for training (GPU)
        from ai.network import create_agent
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.agent = create_agent(device=device)
        self.device = device

        # Stats
        self.total_games = 0
        self.total_experiences = 0

        # Load checkpoint if exists
        self._load_checkpoint()

    def _load_checkpoint(self):
        """Load latest checkpoint."""
        latest = Path(self.checkpoint_dir) / "latest.pt"
        if latest.exists():
            try:
                self.agent.load(str(latest))
                print(f"Loaded checkpoint from {latest}")
            except Exception as e:
                print(f"Could not load checkpoint: {e}")

    def _save_checkpoint(self):
        """Save checkpoint."""
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        path = Path(self.checkpoint_dir) / f"parallel_{self.total_games}_{timestamp}.pt"
        self.agent.save(str(path))

        latest = Path(self.checkpoint_dir) / "latest.pt"
        self.agent.save(str(latest))

    def generate_games(self, num_games: int, progress_callback=None) -> Tuple[int, int]:
        """Generate games in parallel."""
        model_path = str(Path(self.checkpoint_dir) / "latest.pt")

        games_completed = 0
        experiences_collected = 0
        errors = 0

        with ProcessPoolExecutor(max_workers=self.num_workers) as executor:
            futures = []
            for i in range(num_games):
                future = executor.submit(
                    play_single_game,
                    game_id=i,
                    mcts_sims=self.mcts_simulations,
                    model_path=model_path if os.path.exists(model_path) else None,
                    deck1_name=self.deck1_name,
                    deck2_name=self.deck2_name,
                )
                futures.append(future)

            for future in as_completed(futures):
                result = future.result()
                if result.error:
                    errors += 1
                else:
                    games_completed += 1
                    experiences_collected += len(result.experiences)

                    # Add to buffer
                    for exp in result.experiences:
                        self.buffer.append(exp)

                    # Update progress every 10 games
                    if progress_callback and games_completed % 10 == 0:
                        progress_callback(games_completed)

        return games_completed, experiences_collected

    def train(self, epochs: int = 5) -> dict:
        """Train on buffered experiences."""
        if len(self.buffer) < self.batch_size:
            return {'total_loss': 0, 'policy_loss': 0, 'value_loss': 0}

        total_loss = 0
        policy_loss = 0
        value_loss = 0
        num_batches = 0

        for _ in range(epochs):
            # Sample batch
            batch = random.sample(list(self.buffer), self.batch_size)

            # Prepare tensors
            states = torch.tensor(
                np.stack([exp['state'] for exp in batch]),
                dtype=torch.float32,
                device=self.device,
            )
            masks = torch.tensor(
                np.stack([exp['mask'] for exp in batch]),
                dtype=torch.float32,
                device=self.device,
            )
            policies = torch.tensor(
                np.stack([exp['policy'] for exp in batch]),
                dtype=torch.float32,
                device=self.device,
            )
            values = torch.tensor(
                [[exp['value']] for exp in batch],
                dtype=torch.float32,
                device=self.device,
            )

            # Pad states if needed
            if states.shape[1] < self.agent.state_size:
                padding = torch.zeros(
                    states.shape[0],
                    self.agent.state_size - states.shape[1],
                    device=self.device,
                )
                states = torch.cat([states, padding], dim=1)
            elif states.shape[1] > self.agent.state_size:
                states = states[:, :self.agent.state_size]

            # Training step
            losses = self.agent.train_step(
                states=states,
                action_masks=masks,
                target_policies=policies,
                target_values=values,
            )

            total_loss += losses['total_loss']
            policy_loss += losses['policy_loss']
            value_loss += losses['value_loss']
            num_batches += 1

        if num_batches > 0:
            return {
                'total_loss': total_loss / num_batches,
                'policy_loss': policy_loss / num_batches,
                'value_loss': value_loss / num_batches,
            }
        return {'total_loss': 0, 'policy_loss': 0, 'value_loss': 0}


def format_time(seconds: float) -> str:
    """Format seconds as human-readable time."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    elif seconds < 86400:
        return f"{seconds/3600:.1f}h"
    else:
        return f"{seconds/86400:.1f}d"


def run_training():
    """Main training loop."""
    parser = argparse.ArgumentParser(description="Parallel training")
    parser.add_argument("--workers", type=int, default=4, help="Number of workers")
    parser.add_argument("--target", type=int, default=1_000_000, help="Target games")
    parser.add_argument("--mcts", type=int, default=5, help="MCTS simulations")
    parser.add_argument("--games-per-iter", type=int, default=50, help="Games per iteration")
    parser.add_argument("--resume", action="store_true", help="Resume training")
    parser.add_argument("--deck1", type=str, default=None, help="Player 1 deck name (without .json)")
    parser.add_argument("--deck2", type=str, default=None, help="Player 2 deck name (without .json)")
    args = parser.parse_args()

    print("=" * 60)
    print("  VINSMOKE ENGINE - Parallel Training")
    print(f"  Target: {args.target:,} games")
    print(f"  Workers: {args.workers}")
    print(f"  MCTS Simulations: {args.mcts}")
    if args.deck1 or args.deck2:
        print(f"  Deck 1: {args.deck1 or 'random'}")
        print(f"  Deck 2: {args.deck2 or 'random'}")
    print("=" * 60)
    print()

    # Load progress
    progress_file = "training_progress.json"
    progress = {"total_games": 0, "start_time": time.time()}

    if args.resume and os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            progress = json.load(f)
        print(f"Resuming from {progress['total_games']:,} games")

    # Create trainer
    trainer = ParallelTrainer(
        num_workers=args.workers,
        mcts_simulations=args.mcts,
        deck1_name=args.deck1,
        deck2_name=args.deck2,
    )

    total_games = progress["total_games"]
    start_time = time.time()
    iteration = 0

    # Use a mutable container for the callback to access current total
    progress_state = {"base_games": total_games, "losses": {}}

    def update_progress(games_in_iter):
        current_total = progress_state["base_games"] + games_in_iter
        progress["total_games"] = current_total
        progress["workers"] = args.workers
        progress["buffer_size"] = len(trainer.buffer)
        # Include losses if available
        if progress_state["losses"]:
            progress["loss"] = progress_state["losses"].get("total_loss", 0.0)
            progress["policy_loss"] = progress_state["losses"].get("policy_loss", 0.0)
            progress["value_loss"] = progress_state["losses"].get("value_loss", 0.0)
        with open(progress_file, 'w') as f:
            json.dump(progress, f)

    while total_games < args.target:
        iteration += 1
        iter_start = time.time()

        # Update base for this iteration
        progress_state["base_games"] = total_games

        # Generate games in parallel
        print(f"\nIteration {iteration}: Generating {args.games_per_iter} games...")
        games, experiences = trainer.generate_games(args.games_per_iter, progress_callback=update_progress)
        total_games += games
        trainer.total_games = total_games

        gen_time = time.time() - iter_start

        # Train
        print(f"Training on {len(trainer.buffer)} experiences...")
        losses = trainer.train(epochs=5)

        # Store losses for progress updates
        progress_state["losses"] = losses

        iter_time = time.time() - iter_start

        # Calculate stats
        elapsed = time.time() - start_time
        rate = total_games / elapsed if elapsed > 0 else 0
        remaining = (args.target - total_games) / rate if rate > 0 else float('inf')
        pct = (total_games / args.target) * 100

        print(f"\n{'='*60}")
        print(f"  Progress: {total_games:,} / {args.target:,} ({pct:.1f}%)")
        print(f"  This iter: {games} games in {gen_time:.1f}s ({games/gen_time:.2f} g/s)")
        print(f"  Overall rate: {rate:.2f} games/sec")
        print(f"  ETA: {format_time(remaining)}")
        print(f"  Loss: {losses['total_loss']:.4f}")
        print(f"{'='*60}")

        # Save progress with all metrics
        progress["total_games"] = total_games
        progress["workers"] = args.workers
        progress["buffer_size"] = len(trainer.buffer)
        progress["loss"] = losses.get("total_loss", 0.0)
        progress["policy_loss"] = losses.get("policy_loss", 0.0)
        progress["value_loss"] = losses.get("value_loss", 0.0)
        with open(progress_file, 'w') as f:
            json.dump(progress, f)

        # Checkpoint every 10 iterations
        if iteration % 10 == 0:
            trainer._save_checkpoint()
            print("Checkpoint saved!")

    # Final save
    trainer._save_checkpoint()

    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print("  TRAINING COMPLETE!")
    print(f"  Total games: {total_games:,}")
    print(f"  Total time: {format_time(elapsed)}")
    print(f"  Average rate: {total_games / elapsed:.2f} games/sec")
    print("=" * 60)


if __name__ == "__main__":
    # Required for Windows multiprocessing
    import multiprocessing
    multiprocessing.freeze_support()
    run_training()
