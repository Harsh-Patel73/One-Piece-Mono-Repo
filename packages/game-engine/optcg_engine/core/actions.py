"""
Action definitions for One Piece TCG.

All possible actions a player can take during a game.
Used for both human input and AI action space.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, List, Tuple


class ActionType(Enum):
    """Types of actions a player can take."""

    # Phase actions
    PASS = auto()               # End current phase/action opportunity
    PASS_TURN = auto()          # End entire turn (go to End phase)

    # Mulligan
    MULLIGAN = auto()           # Redraw selected cards
    KEEP_HAND = auto()          # Keep current hand

    # Main phase actions
    PLAY_CARD = auto()          # Play a card from hand
    ATTACH_DON = auto()         # Attach DON to a card
    DETACH_DON = auto()         # Remove DON from a card (return to pool)
    ACTIVATE_EFFECT = auto()    # Activate a card effect

    # Combat actions
    ATTACK = auto()             # Declare an attack
    ACTIVATE_BLOCKER = auto()   # Redirect attack with blocker
    USE_COUNTER = auto()        # Use counter card/effect
    DECLINE_BLOCK = auto()      # Choose not to block

    # End phase
    DISCARD = auto()            # Discard to hand limit


@dataclass(frozen=True)
class Action:
    """
    Represents a game action.

    This is an immutable action that can be applied to a GameState.
    """

    action_type: ActionType
    player_index: int           # 0 or 1

    # Card indices (context-dependent)
    card_index: Optional[int] = None          # Card in hand or field
    target_index: Optional[int] = None        # Target card or player
    don_amount: Optional[int] = None          # Amount of DON to attach
    card_indices: Optional[Tuple[int, ...]] = None  # Multiple cards (mulligan, discard)

    # Effect-specific
    effect_index: Optional[int] = None        # Which effect on the card
    target_indices: Optional[Tuple[int, ...]] = None  # Multiple targets

    def __repr__(self) -> str:
        parts = [f"{self.action_type.name}"]
        if self.card_index is not None:
            parts.append(f"card={self.card_index}")
        if self.target_index is not None:
            parts.append(f"target={self.target_index}")
        if self.don_amount is not None:
            parts.append(f"don={self.don_amount}")
        return f"Action({', '.join(parts)})"


# Pre-defined common actions
PASS_ACTION = lambda player: Action(ActionType.PASS, player)
PASS_TURN_ACTION = lambda player: Action(ActionType.PASS_TURN, player)
KEEP_HAND_ACTION = lambda player: Action(ActionType.KEEP_HAND, player)
DECLINE_BLOCK_ACTION = lambda player: Action(ActionType.DECLINE_BLOCK, player)


def create_play_card_action(player: int, card_index: int) -> Action:
    """Create an action to play a card from hand."""
    return Action(
        action_type=ActionType.PLAY_CARD,
        player_index=player,
        card_index=card_index,
    )


def create_attack_action(
    player: int,
    attacker_index: int,
    target_index: int,
    is_leader_attack: bool = False
) -> Action:
    """
    Create an attack action.

    Args:
        player: Player index (0 or 1)
        attacker_index: Index of attacking card in field (-1 for leader)
        target_index: Index of target (-1 for opponent's leader)
        is_leader_attack: True if leader is attacking
    """
    return Action(
        action_type=ActionType.ATTACK,
        player_index=player,
        card_index=attacker_index,
        target_index=target_index,
    )


def create_attach_don_action(player: int, card_index: int, don_amount: int) -> Action:
    """Create an action to attach DON to a card."""
    return Action(
        action_type=ActionType.ATTACH_DON,
        player_index=player,
        card_index=card_index,
        don_amount=don_amount,
    )


def create_use_counter_action(player: int, card_index: int) -> Action:
    """Create an action to use a counter card."""
    return Action(
        action_type=ActionType.USE_COUNTER,
        player_index=player,
        card_index=card_index,
    )


def create_activate_blocker_action(player: int, blocker_index: int) -> Action:
    """Create an action to activate a blocker."""
    return Action(
        action_type=ActionType.ACTIVATE_BLOCKER,
        player_index=player,
        card_index=blocker_index,
    )


def create_mulligan_action(player: int, card_indices: Tuple[int, ...]) -> Action:
    """Create an action to mulligan specific cards."""
    return Action(
        action_type=ActionType.MULLIGAN,
        player_index=player,
        card_indices=card_indices,
    )


def create_discard_action(player: int, card_indices: Tuple[int, ...]) -> Action:
    """Create an action to discard cards to hand limit."""
    return Action(
        action_type=ActionType.DISCARD,
        player_index=player,
        card_indices=card_indices,
    )


def create_activate_effect_action(
    player: int,
    card_index: int,
    effect_index: int = 0,
    target_indices: Optional[Tuple[int, ...]] = None
) -> Action:
    """Create an action to activate a card effect."""
    return Action(
        action_type=ActionType.ACTIVATE_EFFECT,
        player_index=player,
        card_index=card_index,
        effect_index=effect_index,
        target_indices=target_indices,
    )


# Target constants
LEADER_TARGET = -1  # Use -1 to indicate leader as target


class ActionValidator:
    """Validates actions against game state."""

    @staticmethod
    def get_valid_actions(game_state: 'GameState', player_index: int) -> List[Action]:
        """
        Get all valid actions for a player in the current game state.

        This is the primary method used by the AI for action masking.
        """
        from models.enums import GamePhase

        valid_actions = []
        phase = game_state.phase

        if phase == GamePhase.MULLIGAN:
            valid_actions.extend(
                ActionValidator._get_mulligan_actions(game_state, player_index)
            )

        elif phase == GamePhase.MAIN:
            valid_actions.extend(
                ActionValidator._get_main_phase_actions(game_state, player_index)
            )

        elif phase == GamePhase.BLOCKER_STEP:
            valid_actions.extend(
                ActionValidator._get_blocker_actions(game_state, player_index)
            )

        elif phase == GamePhase.COUNTER_STEP:
            valid_actions.extend(
                ActionValidator._get_counter_actions(game_state, player_index)
            )

        elif phase == GamePhase.END:
            valid_actions.extend(
                ActionValidator._get_end_phase_actions(game_state, player_index)
            )

        return valid_actions

    @staticmethod
    def _get_mulligan_actions(game_state, player_index: int) -> List[Action]:
        """Get valid mulligan actions."""
        actions = [KEEP_HAND_ACTION(player_index)]

        # Can mulligan any subset of hand
        hand_size = len(game_state.players[player_index].hand)
        for i in range(hand_size):
            # Single card mulligan
            actions.append(create_mulligan_action(player_index, (i,)))

        return actions

    @staticmethod
    def _get_main_phase_actions(game_state, player_index: int) -> List[Action]:
        """Get valid main phase actions."""
        actions = [PASS_TURN_ACTION(player_index)]
        player = game_state.players[player_index]

        # Play card actions
        for i, card in enumerate(player.hand):
            if ActionValidator._can_play_card(game_state, player_index, card):
                actions.append(create_play_card_action(player_index, i))

        # Attach DON actions
        available_don = player.available_don()
        if available_don > 0:
            # Can attach to leader
            for amount in range(1, min(available_don + 1, 11)):
                actions.append(
                    create_attach_don_action(player_index, LEADER_TARGET, amount)
                )
            # Can attach to characters
            for i, card in enumerate(player.field):
                for amount in range(1, min(available_don + 1, 11)):
                    actions.append(
                        create_attach_don_action(player_index, i, amount)
                    )

        # Effect activation actions (leader and characters)
        effect_actions = ActionValidator._get_effect_actions(game_state, player_index)
        actions.extend(effect_actions)

        # Attack actions
        attack_actions = ActionValidator._get_attack_actions(game_state, player_index)
        actions.extend(attack_actions)

        return actions

    @staticmethod
    def _get_effect_actions(game_state, player_index: int) -> List[Action]:
        """Get valid effect activation actions for leader and characters."""
        actions = []
        player = game_state.players[player_index]

        # Check leader effect
        leader = player.leader
        if ActionValidator._can_activate_effect(game_state, player_index, leader, is_leader=True):
            actions.append(create_activate_effect_action(player_index, LEADER_TARGET, 0))

        # Check character effects on field
        for i, card in enumerate(player.field):
            if ActionValidator._can_activate_effect(game_state, player_index, card, is_leader=False):
                actions.append(create_activate_effect_action(player_index, i, 0))

        return actions

    @staticmethod
    def _can_activate_effect(game_state, player_index: int, card, is_leader: bool = False) -> bool:
        """Check if a card's [Activate: Main] effect can be used."""
        # Get the effect text
        if hasattr(card, 'card'):
            # CardInstance - get underlying card
            effect_text = getattr(card.card, 'effect', '') or ''
        else:
            effect_text = getattr(card, 'effect', '') or ''

        if not effect_text:
            return False

        # Check for [Activate: Main] timing
        if '[Activate: Main]' not in effect_text:
            return False

        # Check [Once Per Turn] - if already activated this turn, can't activate again
        if '[Once Per Turn]' in effect_text:
            activated_effects = getattr(game_state, 'activated_effects_this_turn', ())
            card_id = getattr(card, 'instance_id', None)
            if card_id is None:
                card_id = id(card)
            if card_id in activated_effects:
                return False

        # Check DON requirements (e.g., [DON!! x2])
        import re
        don_match = re.search(r'\[DON!!\s*[x×](\d+)\]', effect_text)
        if don_match:
            required_don = int(don_match.group(1))
            attached_don = getattr(card, 'attached_don', 0)
            if attached_don < required_don:
                return False

        return True

    @staticmethod
    def _get_attack_actions(game_state, player_index: int) -> List[Action]:
        """Get valid attack actions."""
        from .phases import GamePhase

        actions = []
        player = game_state.players[player_index]
        opponent = game_state.players[1 - player_index]

        # Check if can attack with leader
        if ActionValidator._can_leader_attack(game_state, player_index):
            # Can attack opponent's leader
            actions.append(
                create_attack_action(player_index, LEADER_TARGET, LEADER_TARGET)
            )
            # Can attack rested opponent characters
            for i, card in enumerate(opponent.field):
                if card.is_resting:
                    actions.append(
                        create_attack_action(player_index, LEADER_TARGET, i)
                    )

        # Check character attacks
        for attacker_idx, attacker in enumerate(player.field):
            if ActionValidator._can_character_attack(game_state, player_index, attacker):
                # Can attack opponent's leader
                actions.append(
                    create_attack_action(player_index, attacker_idx, LEADER_TARGET)
                )
                # Can attack rested opponent characters
                for target_idx, target in enumerate(opponent.field):
                    if target.is_resting:
                        actions.append(
                            create_attack_action(player_index, attacker_idx, target_idx)
                        )

        return actions

    @staticmethod
    def _get_blocker_actions(game_state, player_index: int) -> List[Action]:
        """Get valid blocker actions during blocker step."""
        actions = [DECLINE_BLOCK_ACTION(player_index)]

        player = game_state.players[player_index]

        for i, card in enumerate(player.field):
            if ActionValidator._can_use_as_blocker(game_state, player_index, card):
                actions.append(create_activate_blocker_action(player_index, i))

        return actions

    @staticmethod
    def _get_counter_actions(game_state, player_index: int) -> List[Action]:
        """Get valid counter actions during counter step."""
        actions = [PASS_ACTION(player_index)]

        player = game_state.players[player_index]

        for i, card in enumerate(player.hand):
            if card.counter and card.counter > 0:
                actions.append(create_use_counter_action(player_index, i))

        return actions

    @staticmethod
    def _get_end_phase_actions(game_state, player_index: int) -> List[Action]:
        """Get valid end phase actions (discard to hand limit)."""
        from .phases import HAND_LIMIT

        player = game_state.players[player_index]
        hand_size = len(player.hand)

        if hand_size <= HAND_LIMIT:
            return [PASS_ACTION(player_index)]

        # Must discard down to 7
        discard_count = hand_size - HAND_LIMIT
        actions = []

        # Generate all combinations of cards to discard
        from itertools import combinations
        for combo in combinations(range(hand_size), discard_count):
            actions.append(create_discard_action(player_index, combo))

        return actions

    @staticmethod
    def _can_play_card(game_state, player_index: int, card) -> bool:
        """Check if a card can be played."""
        player = game_state.players[player_index]
        cost = card.cost or 0
        return player.available_don() >= cost

    @staticmethod
    def _can_leader_attack(game_state, player_index: int) -> bool:
        """Check if leader can attack."""
        leader = game_state.players[player_index].leader
        if leader.is_resting or leader.has_attacked:
            return False

        # P1 cannot attack until turn 3, P2 cannot attack until turn 4
        if player_index == 0:
            return game_state.turn >= 3
        else:
            return game_state.turn >= 4

    @staticmethod
    def _can_character_attack(game_state, player_index: int, character) -> bool:
        """Check if a character can attack."""
        if character.is_resting or character.has_attacked:
            return False

        # Cannot attack the turn played unless has Rush
        if getattr(character, 'played_turn', None) == game_state.turn:
            return getattr(character, 'has_rush', False)

        return True

    @staticmethod
    def _can_use_as_blocker(game_state, player_index: int, card) -> bool:
        """Check if a card can be used as a blocker."""
        # Must have Blocker keyword (CardInstance has has_blocker parsed from card.effect)
        if not getattr(card, 'has_blocker', False):
            # Fallback: check effect text on underlying Card
            underlying_card = getattr(card, 'card', card)
            effect = getattr(underlying_card, 'effect', '') or ''
            if '[Blocker]' not in effect:
                return False

        # Must not be resting
        return not card.is_resting
