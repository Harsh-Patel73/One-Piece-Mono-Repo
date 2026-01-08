"""OPTCG Engine - One Piece TCG Game Engine

Shared game logic for AI training and web simulation.
"""

from .game_engine import GameEngine, Player
from .game_rules import GameRules

__version__ = "1.0.0"
__all__ = ["GameEngine", "Player", "GameRules"]
