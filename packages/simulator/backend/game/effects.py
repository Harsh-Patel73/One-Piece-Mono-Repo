"""
Effect class definitions for One Piece TCG.

This module defines all the effect types and their parameters.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, List


class EffectTiming(Enum):
    """When an effect can be activated."""
    ON_PLAY = auto()            # [On Play]
    WHEN_ATTACKING = auto()     # [When Attacking]
    ON_BLOCK = auto()           # [On Block]
    COUNTER = auto()            # [Counter]
    TRIGGER = auto()            # [Trigger]
    MAIN = auto()               # [Activate: Main]
    END_OF_TURN = auto()        # [End of Your Turn]
    START_OF_TURN = auto()      # [Start of Your Turn]
    ON_KO = auto()              # [On K.O.]
    ON_YOUR_CHARACTER_KO = auto()
    ON_TAKE_DAMAGE = auto()
    ON_OPPONENT_ATTACK = auto()
    CONTINUOUS = auto()
    DON_CONDITION = auto()


class EffectType(Enum):
    """Types of effects."""
    DRAW = auto()
    DISCARD = auto()
    TRASH = auto()
    RETURN_TO_HAND = auto()
    RETURN_TO_DECK = auto()
    SEARCH = auto()
    PLAY = auto()
    POWER_BOOST = auto()
    POWER_REDUCE = auto()
    COST_REDUCE = auto()
    REST = auto()
    ACTIVATE = auto()
    KO = auto()
    PROTECT = auto()
    DON_ADD = auto()
    DON_REST = auto()
    DON_ACTIVATE = auto()
    DON_ATTACH = auto()
    LIFE_ADD = auto()
    LIFE_DAMAGE = auto()
    GRANT_RUSH = auto()
    GRANT_BLOCKER = auto()
    GRANT_BANISH = auto()
    GRANT_DOUBLE_ATTACK = auto()
    REMOVE_BLOCKER = auto()
    NEGATE = auto()
    COPY = auto()
    LOOK = auto()
    REVEAL = auto()
    CHOOSE = auto()
    EXTRA_TURN = auto()


class TargetType(Enum):
    """Who/what can be targeted."""
    SELF = auto()
    YOUR_LEADER = auto()
    YOUR_CHARACTER = auto()
    YOUR_CHARACTERS = auto()
    OPPONENT_LEADER = auto()
    OPPONENT_CHARACTER = auto()
    OPPONENT_CHARACTERS = auto()
    ANY_CHARACTER = auto()
    YOUR_HAND = auto()
    YOUR_DECK = auto()
    YOUR_TRASH = auto()
    YOUR_LIFE = auto()
    OPPONENT_HAND = auto()
    OPPONENT_DECK = auto()
    OPPONENT_TRASH = auto()
    YOUR_DON = auto()
    OPPONENT_DON = auto()


class Duration(Enum):
    """How long an effect lasts."""
    INSTANT = auto()
    THIS_TURN = auto()
    THIS_BATTLE = auto()
    NEXT_TURN = auto()
    PERMANENT = auto()


@dataclass
class TargetRestriction:
    """Restrictions on valid targets."""
    cost_max: Optional[int] = None
    cost_min: Optional[int] = None
    cost_exact: Optional[int] = None
    power_max: Optional[int] = None
    power_min: Optional[int] = None
    colors: Optional[List[str]] = None
    types: Optional[List[str]] = None
    attributes: Optional[List[str]] = None
    is_resting: Optional[bool] = None
    name_contains: Optional[str] = None
    your_life_max: Optional[int] = None
    your_life_min: Optional[int] = None
    opponent_life_max: Optional[int] = None
    opponent_life_min: Optional[int] = None


@dataclass
class EffectCost:
    """Cost to activate an effect."""
    don_rest: int = 0
    don_return: int = 0
    discard: int = 0
    trash_from_hand: int = 0
    life_to_hand: int = 0
    return_to_deck: int = 0
    trash_return: int = 0


@dataclass
class Effect:
    """A parsed effect that can be executed."""
    effect_type: EffectType
    timing: EffectTiming
    target_type: Optional[TargetType] = None
    target_count: int = 1
    target_count_exact: bool = False
    target_restriction: Optional[TargetRestriction] = None
    value: int = 0
    duration: Duration = Duration.INSTANT
    don_requirement: int = 0
    cost: Optional[EffectCost] = None
    condition: Optional[str] = None
    once_per_turn: bool = False
    sub_effects: List['Effect'] = field(default_factory=list)
    raw_text: str = ""