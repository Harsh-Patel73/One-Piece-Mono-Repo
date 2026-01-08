"""
Blocker mechanics for One Piece TCG.

Blocker Rules:
1. When your Leader or one of your Characters is attacked, you may rest
   one of your Characters with [Blocker] to make that Character the new
   target of the attack.
2. The blocker must be active (not rested) to activate.
3. Activating Blocker rests the blocking Character.
4. Blocker can only be activated during the Blocker Step of combat.
"""

from dataclasses import dataclass
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from models.cards import Card


@dataclass
class BlockerInfo:
    """Information about an available blocker."""
    card_index: int
    card: 'Card'
    power: int


class BlockerSystem:
    """Handles blocker mechanics during combat."""

    @staticmethod
    def has_blocker_keyword(card: 'Card') -> bool:
        """Check if a card has the Blocker keyword."""
        # Check explicit flag
        if getattr(card, 'has_blocker', False):
            return True

        # Check effect text
        effect = card.effect or ''
        return '[Blocker]' in effect

    @staticmethod
    def can_activate_blocker(card: 'Card') -> bool:
        """
        Check if a card can activate its Blocker ability.

        Requirements:
        - Card must have [Blocker] keyword
        - Card must be active (not rested)
        """
        if not BlockerSystem.has_blocker_keyword(card):
            return False

        if card.is_resting:
            return False

        return True

    @staticmethod
    def get_available_blockers(
        field: List['Card'],
        attacker: Optional['Card'] = None
    ) -> List[BlockerInfo]:
        """
        Get all characters that can currently block.

        Args:
            field: List of characters in play for the defending player
            attacker: The attacking card (for potential blocker restrictions)

        Returns:
            List of BlockerInfo for available blockers
        """
        blockers = []

        for i, card in enumerate(field):
            if BlockerSystem.can_activate_blocker(card):
                # Check for attacker-specific restrictions
                # Some cards have effects that prevent blocking
                if attacker and BlockerSystem._is_block_restricted(card, attacker):
                    continue

                power = card.power or 0
                # Add attached DON power bonus
                power += getattr(card, 'attached_don', 0) * 1000

                blockers.append(BlockerInfo(
                    card_index=i,
                    card=card,
                    power=power
                ))

        return blockers

    @staticmethod
    def activate_blocker(blocker: 'Card') -> 'Card':
        """
        Activate a blocker card.

        This rests the blocker and makes it the new target.

        Args:
            blocker: The card activating its Blocker ability

        Returns:
            The modified blocker card (rested)
        """
        blocker.is_resting = True
        return blocker

    @staticmethod
    def _is_block_restricted(blocker: 'Card', attacker: 'Card') -> bool:
        """
        Check if the blocker is restricted from blocking this attacker.

        Some cards have effects like:
        - "This character cannot be blocked"
        - "Characters with power X or less cannot block this attack"

        Args:
            blocker: The potential blocking card
            attacker: The attacking card

        Returns:
            True if blocker is restricted from blocking
        """
        attacker_effect = attacker.effect or ''

        # Check for "cannot be blocked" effect
        if 'cannot be blocked' in attacker_effect.lower():
            return True

        # Check for power-based blocking restrictions
        # Example: "Characters with 5000 or less power cannot block this attack"
        blocker_power = blocker.power or 0
        blocker_power += getattr(blocker, 'attached_don', 0) * 1000

        # Parse power restriction from effect text
        import re
        pattern = r'(\d+)\s*or\s*less\s*power\s*cannot\s*block'
        match = re.search(pattern, attacker_effect.lower())
        if match:
            power_limit = int(match.group(1))
            if blocker_power <= power_limit:
                return True

        return False

    @staticmethod
    def calculate_blocker_power(blocker: 'Card') -> int:
        """
        Calculate the total power of a blocker.

        NOTE: DON is NOT included because the blocker is defending during
        the opponent's turn, and DON is only active during the controller's turn.
        """
        base_power = blocker.power or 0
        # DON bonus NOT added - blocker is defending during opponent's turn
        return base_power


@dataclass
class BlockerDecision:
    """Represents a blocker activation decision."""
    activate: bool
    blocker_index: Optional[int] = None
    blocker_card: Optional['Card'] = None


def get_ai_blocker_decision(
    game_state,
    available_blockers: List[BlockerInfo],
    attacker: 'Card',
    original_target: 'Card',
    attacker_power: int
) -> BlockerDecision:
    """
    Simple AI logic to decide whether to use a blocker.

    This is a basic heuristic - the trained RL agent will learn better strategies.

    Args:
        game_state: Current game state
        available_blockers: List of available blockers
        attacker: The attacking card
        original_target: The original attack target
        attacker_power: Total power of the attacker (including DON)

    Returns:
        BlockerDecision indicating whether to block and with which card
    """
    if not available_blockers:
        return BlockerDecision(activate=False)

    original_power = original_target.power or 0
    is_leader = original_target.card_type == 'LEADER'

    # If attacking leader and we have life, usually don't block
    # (Life cards can trigger effects)
    if is_leader:
        # But if at low life, consider blocking
        # This is simplified - RL will learn better
        return BlockerDecision(activate=False)

    # If attacking a valuable character, consider blocking
    # Find a blocker with power >= attacker to trade favorably
    for blocker_info in available_blockers:
        if blocker_info.power >= attacker_power:
            return BlockerDecision(
                activate=True,
                blocker_index=blocker_info.card_index,
                blocker_card=blocker_info.card
            )

    # If the original target would be KO'd, sacrifice a weaker blocker
    if attacker_power > original_power:
        # Sort by power, sacrifice weakest
        weakest = min(available_blockers, key=lambda b: b.power)
        return BlockerDecision(
            activate=True,
            blocker_index=weakest.card_index,
            blocker_card=weakest.card
        )

    return BlockerDecision(activate=False)
