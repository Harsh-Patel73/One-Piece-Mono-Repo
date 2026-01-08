"""
AI module for One Piece TCG.

Deep reinforcement learning using AlphaZero-style self-play:
- Neural network for policy and value prediction
- Monte Carlo Tree Search for action selection
- Self-play training loop

Usage:
    from ai import train_model, create_agent

    # Train a new model
    train_model(num_iterations=100)

    # Use a trained model
    agent = create_agent()
    agent.load("checkpoints/latest.pt")
    action = agent.get_action(game_state)
"""

from .state_encoder import StateEncoder, get_encoder
from .network import OPTCGNet, OPTCGAgent, create_agent
from .mcts import MCTS, MCTSNode
from .trainer import SelfPlayTrainer, TrainingConfig, train_model

__all__ = [
    # State encoding
    'StateEncoder',
    'get_encoder',

    # Neural network
    'OPTCGNet',
    'OPTCGAgent',
    'create_agent',

    # MCTS
    'MCTS',
    'MCTSNode',

    # Training
    'SelfPlayTrainer',
    'TrainingConfig',
    'train_model',
]
