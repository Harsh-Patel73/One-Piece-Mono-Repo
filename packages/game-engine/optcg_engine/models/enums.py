from enum import Enum, auto


class CardType(Enum):
    """Types of cards in One Piece TCG."""
    LEADER    = auto()
    CHARACTER = auto()
    EVENT     = auto()
    STAGE     = auto()


class GamePhase(Enum):
    """Phases of a turn in One Piece TCG."""
    # Pre-game
    MULLIGAN = auto()

    # Turn phases
    REFRESH = auto()
    DRAW = auto()
    DON = auto()
    MAIN = auto()
    END = auto()

    # Combat sub-phases
    ATTACK_DECLARATION = auto()
    BLOCKER_STEP = auto()
    COUNTER_STEP = auto()
    DAMAGE_STEP = auto()

    # Game end
    GAME_OVER = auto()

class Color(Enum):
    RED    = "RED"
    GREEN  = "GREEN"
    BLUE   = "BLUE"
    PURPLE = "PURPLE"
    BLACK  = "BLACK"
    YELLOW = "YELLOW"

    @classmethod
    def get_color(cls, s: str) -> 'Color':
        """Map a string like 'Red' or 'Red/Black' into one of our enums (or multi)."""
        try:
            return cls[s.upper()]
        except KeyError:
            # fallback in case of hybrid/missing
            return None
