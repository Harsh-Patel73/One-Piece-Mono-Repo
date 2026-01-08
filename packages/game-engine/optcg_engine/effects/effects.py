"""
Effect class definitions for One Piece TCG.

This module defines all the effect types and their parameters.
Effects are parsed from card text and executed by the resolver.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, List, Dict, Any, Union


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
    ON_KO = auto()              # [On K.O.] - when THIS card is K.O.'d
    ON_YOUR_CHARACTER_KO = auto()  # When YOUR character is K.O.'d (observer effect)
    ON_TAKE_DAMAGE = auto()     # When you take life damage
    ON_OPPONENT_ATTACK = auto() # [On Your Opponent's Attack]
    CONTINUOUS = auto()         # Always active (no timing keyword)
    DON_CONDITION = auto()      # [DON!! x1], [DON!! x2]


class EffectType(Enum):
    """Types of effects."""
    # Card manipulation
    DRAW = auto()               # Draw cards
    DISCARD = auto()            # Discard cards
    TRASH = auto()              # Send to trash
    RETURN_TO_HAND = auto()     # Return card to hand
    RETURN_TO_DECK = auto()     # Return card to deck
    SEARCH = auto()             # Search deck for card
    PLAY = auto()               # Play a card (for free or reduced cost)

    # Power/stat modification
    POWER_BOOST = auto()        # +X000 power
    POWER_REDUCE = auto()       # -X000 power or set to 0
    COST_REDUCE = auto()        # Reduce cost to play

    # Card state changes
    REST = auto()               # Rest a card
    ACTIVATE = auto()           # Set card as active (unrest)
    KO = auto()                 # K.O. a character
    PROTECT = auto()            # Cannot be K.O.'d / targeted

    # DON manipulation
    DON_ADD = auto()            # Add DON from DON deck
    DON_REST = auto()           # Rest DON
    DON_ACTIVATE = auto()       # Set DON as active
    DON_ATTACH = auto()         # Attach DON to card

    # Life manipulation
    LIFE_ADD = auto()           # Add to life
    LIFE_DAMAGE = auto()        # Deal life damage

    # Keywords
    GRANT_RUSH = auto()         # Give Rush
    GRANT_BLOCKER = auto()      # Give Blocker
    GRANT_BANISH = auto()       # Give Banish
    GRANT_DOUBLE_ATTACK = auto() # Give Double Attack
    REMOVE_BLOCKER = auto()     # Prevent blocker activation

    # Conditional/special
    NEGATE = auto()             # Negate an effect
    COPY = auto()               # Copy an effect
    LOOK = auto()               # Look at cards (deck, life, etc.)
    REVEAL = auto()             # Reveal cards
    CHOOSE = auto()             # Player makes a choice
    EXTRA_TURN = auto()         # Take an extra turn


class TargetType(Enum):
    """Who/what can be targeted."""
    SELF = auto()               # This card
    YOUR_LEADER = auto()
    YOUR_CHARACTER = auto()
    YOUR_CHARACTERS = auto()    # All your characters
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
    INSTANT = auto()            # Immediate, one-time
    THIS_TURN = auto()          # Until end of turn
    THIS_BATTLE = auto()        # Until end of battle
    NEXT_TURN = auto()          # Until end of next turn
    PERMANENT = auto()          # Permanent (until card leaves play)


@dataclass
class TargetRestriction:
    """Restrictions on valid targets."""
    cost_max: Optional[int] = None      # "cost of X or less"
    cost_min: Optional[int] = None      # "cost of X or more"
    cost_exact: Optional[int] = None    # "cost of exactly X"
    power_max: Optional[int] = None     # "X or less power"
    power_min: Optional[int] = None     # "X or more power"
    colors: Optional[List[str]] = None  # Specific colors
    types: Optional[List[str]] = None   # Card types (e.g., "Straw Hat Crew")
    attributes: Optional[List[str]] = None  # Attributes (Slash, Strike, etc.)
    is_resting: Optional[bool] = None   # Resting state
    name_contains: Optional[str] = None # Name includes specific text
    # Life condition restrictions
    your_life_max: Optional[int] = None      # "If you have X or less Life cards"
    your_life_min: Optional[int] = None      # "If you have X or more Life cards"
    opponent_life_max: Optional[int] = None  # "If opponent has X or less Life cards"
    opponent_life_min: Optional[int] = None  # "If opponent has X or more Life cards"


@dataclass
class EffectCost:
    """Cost to activate an effect."""
    don_rest: int = 0           # Rest X DON
    don_return: int = 0         # Return X DON to pool
    discard: int = 0            # Discard X cards
    trash_from_hand: int = 0    # Trash X cards from hand
    life_to_hand: int = 0       # Move X life to hand
    return_to_deck: int = 0     # Return X cards to deck
    trash_return: int = 0       # Return X cards from trash to deck


@dataclass
class Effect:
    """
    A parsed effect that can be executed.

    This is the main data structure produced by the parser.
    """
    effect_type: EffectType
    timing: EffectTiming

    # Target specification
    target_type: Optional[TargetType] = None
    target_count: int = 1               # "up to X"
    target_count_exact: bool = False    # True if exactly X, False if "up to X"
    target_restriction: Optional[TargetRestriction] = None

    # Effect parameters
    value: int = 0                      # Power amount, draw count, etc.
    duration: Duration = Duration.INSTANT

    # DON condition (e.g., [DON!! x2])
    don_requirement: int = 0

    # Activation cost
    cost: Optional[EffectCost] = None

    # Condition for activation
    condition: Optional[str] = None     # Raw condition text for complex parsing

    # Usage limits
    once_per_turn: bool = False

    # For multi-part effects
    sub_effects: List['Effect'] = field(default_factory=list)

    # Raw text for debugging
    raw_text: str = ""

    def __repr__(self) -> str:
        parts = [f"{self.effect_type.name}"]
        if self.timing != EffectTiming.CONTINUOUS:
            parts.append(f"@{self.timing.name}")
        if self.value:
            parts.append(f"value={self.value}")
        if self.target_type:
            parts.append(f"target={self.target_type.name}")
        return f"Effect({', '.join(parts)})"


@dataclass
class ParsedCard:
    """A card with all its effects parsed."""
    card_id: str
    name: str
    effects: List[Effect]
    keywords: List[str]  # Rush, Blocker, etc.


# Common keyword effects
KEYWORD_RUSH = Effect(
    effect_type=EffectType.GRANT_RUSH,
    timing=EffectTiming.CONTINUOUS,
    target_type=TargetType.SELF,
    duration=Duration.PERMANENT,
)

KEYWORD_BLOCKER = Effect(
    effect_type=EffectType.GRANT_BLOCKER,
    timing=EffectTiming.CONTINUOUS,
    target_type=TargetType.SELF,
    duration=Duration.PERMANENT,
)

KEYWORD_BANISH = Effect(
    effect_type=EffectType.GRANT_BANISH,
    timing=EffectTiming.CONTINUOUS,
    target_type=TargetType.SELF,
    duration=Duration.PERMANENT,
)

KEYWORD_DOUBLE_ATTACK = Effect(
    effect_type=EffectType.GRANT_DOUBLE_ATTACK,
    timing=EffectTiming.CONTINUOUS,
    target_type=TargetType.SELF,
    duration=Duration.PERMANENT,
)
