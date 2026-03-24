"""OPTCG Engine - One Piece TCG Game Engine

Shared game logic for AI training and web simulation.
"""

__version__ = "1.0.0"

# Import effects module (the main API for effect handling)
from .effects import (
    EffectTiming, EffectType, Effect,
    get_effect_manager, CardEffectManager,
    has_hardcoded_effect, execute_hardcoded_effect,
)

# Game rules functions available at optcg_engine.game_rules.validate_deck
# Note: GameEngine import is skipped due to missing handlers module
# The effects module is the primary API for simulator integration

__all__ = [
    "EffectTiming", "EffectType", "Effect",
    "get_effect_manager", "CardEffectManager",
    "has_hardcoded_effect", "execute_hardcoded_effect",
]
