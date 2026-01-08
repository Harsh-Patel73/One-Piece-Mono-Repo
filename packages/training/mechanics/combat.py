"""
Combat resolution for One Piece TCG.

Combat Flow:
1. Attack Declaration - Attacker chooses target (Leader or rested Character)
2. Blocker Step - Defender may activate Blocker to redirect attack
3. Counter Step - Defender uses Counter cards to boost defense
4. Damage Step - Compare power and resolve damage
"""

from dataclasses import dataclass
from typing import Optional, List, Tuple, TYPE_CHECKING
from enum import Enum, auto

if TYPE_CHECKING:
    from models.cards import Card


class CombatResult(Enum):
    """Possible results of combat resolution."""
    ATTACKER_WINS = auto()      # Attacker power > defender power
    DEFENDER_WINS = auto()      # Defender power >= attacker power
    LEADER_DAMAGED = auto()     # Defender was leader, takes life damage
    CHARACTER_KO = auto()       # Defender character is KO'd


@dataclass
class CombatState:
    """Tracks the current state of combat."""
    attacker: 'Card'
    attacker_index: int         # -1 for leader
    attacker_player: int        # 0 or 1
    attacker_power: int

    original_target: 'Card'
    original_target_index: int  # -1 for leader

    current_target: 'Card'      # May change if blocker activates
    current_target_index: int
    defender_player: int

    base_defense: int
    counter_bonus: int = 0
    total_defense: int = 0

    blocker_activated: bool = False
    blocker_card: Optional['Card'] = None

    counters_used: List['Card'] = None

    def __post_init__(self):
        if self.counters_used is None:
            self.counters_used = []
        self.total_defense = self.base_defense + self.counter_bonus


class CombatResolver:
    """Handles combat resolution."""

    @staticmethod
    def create_combat(
        attacker: 'Card',
        attacker_index: int,
        attacker_player: int,
        target: 'Card',
        target_index: int,
        don_assignments: dict
    ) -> CombatState:
        """
        Initialize combat state when an attack is declared.

        Args:
            attacker: The attacking card
            attacker_index: Index in field (-1 for leader)
            attacker_player: Player index of attacker
            target: The target card
            target_index: Index in field (-1 for leader)
            don_assignments: Dict of card -> DON attached

        Returns:
            Initial CombatState
        """
        # Calculate attacker power
        # DON is active for attacker (it's their turn)
        base_power = attacker.power or 0
        attached_don = don_assignments.get(attacker, 0)
        if attached_don == 0:
            attached_don = getattr(attacker, 'attached_don', 0)
        attacker_power = base_power + (attached_don * 1000)

        # Calculate initial defense
        # DON is NOT active for defender (it's not their turn)
        base_defense = target.power or 0
        # DON bonus NOT added to defender - inactive during opponent's turn

        return CombatState(
            attacker=attacker,
            attacker_index=attacker_index,
            attacker_player=attacker_player,
            attacker_power=attacker_power,
            original_target=target,
            original_target_index=target_index,
            current_target=target,
            current_target_index=target_index,
            defender_player=1 - attacker_player,
            base_defense=base_defense,
        )

    @staticmethod
    def apply_blocker(
        combat: CombatState,
        blocker: 'Card',
        blocker_index: int,
        don_assignments: dict
    ) -> CombatState:
        """
        Apply blocker to redirect the attack.

        Args:
            combat: Current combat state
            blocker: The blocking card
            blocker_index: Index of blocker in field
            don_assignments: DON assignments for power calc

        Returns:
            Updated CombatState with new target
        """
        # Rest the blocker
        blocker.is_resting = True

        # Calculate blocker's defense
        # DON is NOT active for blocker (it's the attacker's turn, not the blocker's)
        base_defense = blocker.power or 0
        # DON bonus NOT added to blocker - inactive during opponent's turn

        return CombatState(
            attacker=combat.attacker,
            attacker_index=combat.attacker_index,
            attacker_player=combat.attacker_player,
            attacker_power=combat.attacker_power,
            original_target=combat.original_target,
            original_target_index=combat.original_target_index,
            current_target=blocker,
            current_target_index=blocker_index,
            defender_player=combat.defender_player,
            base_defense=base_defense,
            counter_bonus=0,
            blocker_activated=True,
            blocker_card=blocker,
        )

    @staticmethod
    def apply_counter(
        combat: CombatState,
        counter_card: 'Card'
    ) -> CombatState:
        """
        Apply a counter card to boost defense.

        Args:
            combat: Current combat state
            counter_card: The counter card being used

        Returns:
            Updated CombatState with increased defense
        """
        counter_value = counter_card.counter or 0

        new_counters = list(combat.counters_used)
        new_counters.append(counter_card)

        return CombatState(
            attacker=combat.attacker,
            attacker_index=combat.attacker_index,
            attacker_player=combat.attacker_player,
            attacker_power=combat.attacker_power,
            original_target=combat.original_target,
            original_target_index=combat.original_target_index,
            current_target=combat.current_target,
            current_target_index=combat.current_target_index,
            defender_player=combat.defender_player,
            base_defense=combat.base_defense,
            counter_bonus=combat.counter_bonus + counter_value,
            blocker_activated=combat.blocker_activated,
            blocker_card=combat.blocker_card,
            counters_used=new_counters,
        )

    @staticmethod
    def resolve_damage(combat: CombatState) -> Tuple[CombatResult, dict]:
        """
        Resolve combat damage.

        Args:
            combat: Final combat state after counters

        Returns:
            Tuple of (CombatResult, result_data)
        """
        total_defense = combat.base_defense + combat.counter_bonus
        attacker_power = combat.attacker_power

        result_data = {
            'attacker_power': attacker_power,
            'total_defense': total_defense,
            'target_card': combat.current_target,
            'counters_used': combat.counters_used,
        }

        if attacker_power >= total_defense:
            # Attacker wins (ties go to attacker)
            if combat.current_target.card_type == 'LEADER':
                result_data['is_leader'] = True
                return CombatResult.LEADER_DAMAGED, result_data
            else:
                result_data['is_leader'] = False
                result_data['ko_card'] = combat.current_target
                return CombatResult.CHARACTER_KO, result_data
        else:
            # Defender wins (blocked/survived)
            return CombatResult.DEFENDER_WINS, result_data

    @staticmethod
    def can_attack_target(
        attacker: 'Card',
        target: 'Card',
        target_is_leader: bool
    ) -> Tuple[bool, str]:
        """
        Check if an attack on a target is valid.

        Rules:
        - Can always attack the opponent's Leader
        - Can only attack Characters that are resting (tapped)

        Args:
            attacker: The attacking card
            target: The potential target
            target_is_leader: True if target is leader

        Returns:
            Tuple of (is_valid, reason)
        """
        if target_is_leader:
            return True, ""

        # Can only attack rested characters
        if not target.is_resting:
            return False, "Can only attack rested Characters"

        return True, ""

    @staticmethod
    def rest_attacker(attacker: 'Card') -> 'Card':
        """
        Rest the attacking card after attack.

        Args:
            attacker: The card that attacked

        Returns:
            The modified card (rested, marked as attacked)
        """
        attacker.is_resting = True
        attacker.has_attacked = True
        return attacker

    @staticmethod
    def calculate_power(card: 'Card', don_attached: int = 0) -> int:
        """
        Calculate total power of a card.

        Args:
            card: The card
            don_attached: Number of DON attached

        Returns:
            Total power (base + DON bonus)
        """
        base = card.power or 0
        don_bonus = don_attached * 1000
        return base + don_bonus


def execute_attack(
    game_state,
    attacker_index: int,
    target_index: int,
    attacker_player: int
) -> Tuple['GameState', CombatState]:
    """
    Execute an attack action, initializing combat.

    This starts the combat flow:
    1. Creates CombatState
    2. Rests the attacker
    3. Transitions to BLOCKER_STEP phase

    Args:
        game_state: Current game state
        attacker_index: Index of attacker (-1 for leader)
        target_index: Index of target (-1 for leader)
        attacker_player: Player index of attacker

    Returns:
        Tuple of (updated game state, combat state)
    """
    from .blocker import BlockerSystem

    # Get attacker
    if attacker_index == -1:
        attacker = game_state.players[attacker_player].leader
    else:
        attacker = game_state.players[attacker_player].field[attacker_index]

    # Get target
    defender_player = 1 - attacker_player
    if target_index == -1:
        target = game_state.players[defender_player].leader
    else:
        target = game_state.players[defender_player].field[target_index]

    # Create combat state
    combat = CombatResolver.create_combat(
        attacker=attacker,
        attacker_index=attacker_index,
        attacker_player=attacker_player,
        target=target,
        target_index=target_index,
        don_assignments={}  # Will get from game state
    )

    # Rest the attacker
    attacker.is_resting = True
    attacker.has_attacked = True

    return game_state, combat
