"""
Game phase definitions for One Piece TCG.

Turn structure:
1. Refresh Phase  - Unrest all cards, return attached DON to DON pool
2. Draw Phase     - Draw 1 card (skip for P1 on turn 1)
3. DON!! Phase    - Add 2 DON from DON deck (max 10)
4. Main Phase     - Play cards, attach DON, activate effects
5. End Phase      - Discard to hand limit (7 cards)
"""

from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .game_state import GameState


class GamePhase(Enum):
    """Phases of a turn in One Piece TCG."""

    # Pre-game phases
    MULLIGAN = auto()           # Initial hand redraw decision

    # Turn phases (in order)
    REFRESH = auto()            # Unrest cards, refresh DON
    DRAW = auto()               # Draw 1 card
    DON = auto()                # Add 2 DON (max 10)
    MAIN = auto()               # Play cards, attach DON, use effects
    END = auto()                # End of turn cleanup, hand limit

    # Combat sub-phases (during Main phase attacks)
    ATTACK_DECLARATION = auto() # Attacker chooses target
    BLOCKER_STEP = auto()       # Defender may activate blocker
    COUNTER_STEP = auto()       # Counter cards and effects
    DAMAGE_STEP = auto()        # Resolve damage

    # Game over
    GAME_OVER = auto()


class PhaseHandler:
    """Handles phase transitions and phase-specific logic."""

    # Order of main phases
    MAIN_PHASE_ORDER = [
        GamePhase.REFRESH,
        GamePhase.DRAW,
        GamePhase.DON,
        GamePhase.MAIN,
        GamePhase.END,
    ]

    # Combat sub-phase order
    COMBAT_PHASE_ORDER = [
        GamePhase.ATTACK_DECLARATION,
        GamePhase.BLOCKER_STEP,
        GamePhase.COUNTER_STEP,
        GamePhase.DAMAGE_STEP,
    ]

    @staticmethod
    def get_next_phase(current: GamePhase, in_combat: bool = False) -> GamePhase:
        """Get the next phase after the current one."""
        if in_combat:
            if current in PhaseHandler.COMBAT_PHASE_ORDER:
                idx = PhaseHandler.COMBAT_PHASE_ORDER.index(current)
                if idx + 1 < len(PhaseHandler.COMBAT_PHASE_ORDER):
                    return PhaseHandler.COMBAT_PHASE_ORDER[idx + 1]
                # Combat resolved, return to MAIN
                return GamePhase.MAIN

        if current in PhaseHandler.MAIN_PHASE_ORDER:
            idx = PhaseHandler.MAIN_PHASE_ORDER.index(current)
            if idx + 1 < len(PhaseHandler.MAIN_PHASE_ORDER):
                return PhaseHandler.MAIN_PHASE_ORDER[idx + 1]
            # End of turn, next turn starts with REFRESH
            return GamePhase.REFRESH

        return GamePhase.MAIN

    @staticmethod
    def can_perform_action_in_phase(phase: GamePhase, action_type: str) -> bool:
        """Check if an action type is valid in the current phase."""
        phase_actions = {
            GamePhase.MULLIGAN: ['mulligan', 'keep_hand'],
            GamePhase.REFRESH: [],  # Automatic
            GamePhase.DRAW: [],     # Automatic
            GamePhase.DON: [],      # Automatic
            GamePhase.MAIN: ['play_card', 'attach_don', 'attack', 'activate_effect', 'pass'],
            GamePhase.END: ['discard'],
            GamePhase.ATTACK_DECLARATION: ['select_target'],
            GamePhase.BLOCKER_STEP: ['activate_blocker', 'decline_blocker'],
            GamePhase.COUNTER_STEP: ['use_counter', 'pass_counter'],
            GamePhase.DAMAGE_STEP: [],  # Automatic
        }

        allowed = phase_actions.get(phase, [])
        return action_type in allowed


# Hand size limit
HAND_LIMIT = 7

# Maximum DON pool size
MAX_DON = 10

# Starting DON amounts
STARTING_DON_P1 = 1
STARTING_DON_P2 = 2

# DON gained per turn
DON_PER_TURN = 2
