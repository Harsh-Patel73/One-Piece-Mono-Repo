"""
Monte Carlo Tree Search for One Piece TCG.

Uses neural network for:
- Prior probabilities (to guide exploration)
- Value estimation (for leaf evaluation)
"""

import math
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from copy import deepcopy

from core.game_state import GameState
from core.actions import Action, ActionValidator


@dataclass
class MCTSNode:
    """A node in the MCTS tree."""

    state: GameState
    parent: Optional['MCTSNode'] = None
    action: Optional[Action] = None  # Action that led to this node

    # Statistics
    visit_count: int = 0
    total_value: float = 0.0
    prior_prob: float = 0.0

    # Children
    children: Dict[int, 'MCTSNode'] = field(default_factory=dict)  # action_index -> node
    is_expanded: bool = False

    @property
    def q_value(self) -> float:
        """Average value of this node."""
        if self.visit_count == 0:
            return 0.0
        return self.total_value / self.visit_count

    @property
    def ucb_score(self) -> float:
        """UCB score for selection (from parent's perspective)."""
        if self.parent is None:
            return 0.0

        c_puct = 1.5  # Exploration constant

        # Exploration bonus
        exploration = c_puct * self.prior_prob * math.sqrt(self.parent.visit_count) / (1 + self.visit_count)

        return self.q_value + exploration


class MCTS:
    """
    Monte Carlo Tree Search with neural network guidance.

    Uses the network to:
    1. Get prior probabilities for action selection
    2. Evaluate leaf nodes
    """

    def __init__(
        self,
        agent,  # OPTCGAgent
        num_simulations: int = 100,
        c_puct: float = 1.5,
        dirichlet_alpha: float = 0.3,
        dirichlet_epsilon: float = 0.25,
    ):
        self.agent = agent
        self.num_simulations = num_simulations
        self.c_puct = c_puct
        self.dirichlet_alpha = dirichlet_alpha
        self.dirichlet_epsilon = dirichlet_epsilon

        # Game simulator for rollouts
        self.simulator = GameSimulator()

    def search(self, root_state: GameState) -> Tuple[np.ndarray, Action]:
        """
        Run MCTS from the given state.

        Returns:
            policy: Visit count distribution over actions
            action: Selected action
        """
        # Create root node
        root = MCTSNode(state=root_state)

        # Get valid actions
        valid_actions = ActionValidator.get_valid_actions(root_state, root_state.active_player)
        if len(valid_actions) == 0:
            return np.zeros(self.agent.encoder.action_space_size), None

        if len(valid_actions) == 1:
            # Only one action - no need for search
            action_idx = self.agent.encoder._action_to_index(valid_actions[0])
            policy = np.zeros(self.agent.encoder.action_space_size)
            policy[action_idx] = 1.0
            return policy, valid_actions[0]

        # Expand root with prior probabilities
        self._expand(root, valid_actions)

        # Add Dirichlet noise to root priors for exploration
        self._add_dirichlet_noise(root)

        # Run simulations
        for _ in range(self.num_simulations):
            node = root
            search_path = [node]

            # Selection: traverse tree until we reach a leaf
            while node.is_expanded and not node.state.is_terminal:
                node = self._select_child(node)
                search_path.append(node)

            # Expansion and evaluation
            if not node.state.is_terminal:
                leaf_actions = ActionValidator.get_valid_actions(
                    node.state, node.state.active_player
                )
                if len(leaf_actions) > 0:
                    self._expand(node, leaf_actions)
                    # Evaluate using neural network
                    value = self.agent.get_value(node.state)
                else:
                    value = 0.0
            else:
                # Terminal node - use actual game outcome
                if node.state.winner == root_state.active_player:
                    value = 1.0
                elif node.state.winner is not None:
                    value = -1.0
                else:
                    value = 0.0

            # Backpropagation
            self._backpropagate(search_path, value, root_state.active_player)

        # Extract policy from visit counts
        policy = self._get_policy(root)

        # Select action (proportional to visit count)
        action = self._select_action(root, valid_actions)

        return policy, action

    def _expand(self, node: MCTSNode, valid_actions: List[Action]):
        """Expand a node with all valid actions."""
        # Get prior probabilities from network
        policy, _ = self.agent.get_policy_and_value(node.state)

        for action in valid_actions:
            action_idx = self.agent.encoder._action_to_index(action)
            prior = policy[action_idx].item() if action_idx < len(policy) else 0.0

            # Create child node (state will be computed on first visit)
            child = MCTSNode(
                state=None,  # Lazy state computation
                parent=node,
                action=action,
                prior_prob=prior,
            )
            node.children[action_idx] = child

        node.is_expanded = True

    def _add_dirichlet_noise(self, node: MCTSNode):
        """Add Dirichlet noise to root node priors for exploration."""
        if len(node.children) == 0:
            return

        noise = np.random.dirichlet([self.dirichlet_alpha] * len(node.children))

        for i, child in enumerate(node.children.values()):
            child.prior_prob = (
                (1 - self.dirichlet_epsilon) * child.prior_prob +
                self.dirichlet_epsilon * noise[i]
            )

    def _select_child(self, node: MCTSNode) -> MCTSNode:
        """Select the best child using UCB."""
        best_score = float('-inf')
        best_child = None

        for child in node.children.values():
            # UCB formula
            if child.visit_count == 0:
                # Unvisited nodes get high priority
                score = float('inf') if child.prior_prob > 0 else 0
            else:
                q = child.q_value
                # Flip Q value for opponent's perspective
                if node.state.active_player != child.state.active_player if child.state else True:
                    q = -q

                exploration = (
                    self.c_puct * child.prior_prob *
                    math.sqrt(node.visit_count) / (1 + child.visit_count)
                )
                score = q + exploration

            if score > best_score:
                best_score = score
                best_child = child

        # Compute state if not yet done
        if best_child is not None and best_child.state is None:
            best_child.state = self.simulator.apply_action(
                node.state, best_child.action
            )

        return best_child

    def _backpropagate(
        self,
        search_path: List[MCTSNode],
        value: float,
        root_player: int,
    ):
        """Backpropagate value through the search path."""
        for node in reversed(search_path):
            node.visit_count += 1

            # Value from root player's perspective
            if node.state and node.state.active_player == root_player:
                node.total_value += value
            else:
                node.total_value -= value

    def _get_policy(self, root: MCTSNode) -> np.ndarray:
        """Extract policy from visit counts."""
        policy = np.zeros(self.agent.encoder.action_space_size)

        total_visits = sum(child.visit_count for child in root.children.values())
        if total_visits == 0:
            return policy

        for action_idx, child in root.children.items():
            policy[action_idx] = child.visit_count / total_visits

        return policy

    def _select_action(
        self,
        root: MCTSNode,
        valid_actions: List[Action],
    ) -> Action:
        """Select action based on visit counts."""
        best_visits = -1
        best_action = None

        for action in valid_actions:
            action_idx = self.agent.encoder._action_to_index(action)
            if action_idx in root.children:
                visits = root.children[action_idx].visit_count
                if visits > best_visits:
                    best_visits = visits
                    best_action = action

        return best_action or valid_actions[0]


class GameSimulator:
    """
    Simulates game state transitions.

    Wraps the game engine to provide state transitions for MCTS.
    """

    def __init__(self):
        # We'll use a simplified simulation for now
        pass

    def apply_action(self, state: GameState, action: Action) -> GameState:
        """
        Apply an action to a state and return the new state.

        This is a simplified version - the full implementation would
        integrate with the game engine.
        """
        from core.actions import ActionType

        # Create a deep copy of the state
        new_state = self._copy_state(state)

        # Apply action based on type
        if action.action_type == ActionType.PASS:
            return self._handle_pass(new_state)
        elif action.action_type == ActionType.PASS_TURN:
            return self._handle_pass_turn(new_state)
        elif action.action_type == ActionType.PLAY_CARD:
            return self._handle_play_card(new_state, action)
        elif action.action_type == ActionType.ATTACK:
            return self._handle_attack(new_state, action)
        elif action.action_type == ActionType.ATTACH_DON:
            return self._handle_attach_don(new_state, action)
        elif action.action_type == ActionType.KEEP_HAND:
            return self._handle_keep_hand(new_state)
        elif action.action_type == ActionType.DECLINE_BLOCK:
            return self._handle_decline_block(new_state)
        elif action.action_type == ActionType.ACTIVATE_BLOCKER:
            return self._handle_blocker(new_state, action)
        elif action.action_type == ActionType.USE_COUNTER:
            return self._handle_counter(new_state, action)
        elif action.action_type == ActionType.MULLIGAN:
            return self._handle_mulligan(new_state, action)
        elif action.action_type == ActionType.ACTIVATE_EFFECT:
            return self._handle_activate_effect(new_state, action)

        return new_state

    def _copy_state(self, state: GameState) -> GameState:
        """Create a deep copy of the game state."""
        # Use the immutable copy method
        return state.copy()

    def _handle_pass(self, state: GameState) -> GameState:
        """Handle pass action."""
        from models.enums import GamePhase

        # Move to next phase or resolve combat
        if state.phase == GamePhase.COUNTER_STEP:
            # Resolve combat
            return self._resolve_combat(state)
        return state

    def _handle_pass_turn(self, state: GameState) -> GameState:
        """Handle end turn."""
        from core.game_state import end_turn, start_new_turn

        # End current turn and start opponent's turn
        new_state = end_turn(state)
        return start_new_turn(new_state)

    def _handle_play_card(self, state: GameState, action: Action) -> GameState:
        """Handle playing a card from hand."""
        player = state.current_player
        card_idx = action.card_index

        if card_idx is None or card_idx >= len(player.hand):
            return state

        card = player.hand[card_idx]
        cost = card.cost or 0

        # Check if can afford
        if player.don_active < cost:
            return state

        # Remove card from hand
        new_hand = tuple(c for i, c in enumerate(player.hand) if i != card_idx)

        # Add to field (mark as played this turn)
        played_card = card.copy(played_turn=state.turn)
        new_field = player.field + (played_card,)

        # Spend DON
        new_don = player.don_active - cost

        new_player = player.copy(
            hand=new_hand,
            field=new_field,
            don_active=new_don,
        )

        return state.with_player(state.active_player, new_player)

    def _handle_attack(self, state: GameState, action: Action) -> GameState:
        """Handle attack declaration."""
        from models.enums import GamePhase
        from core.game_state import CombatContext
        from core.actions import LEADER_TARGET

        player = state.current_player

        # Get attacker
        attacker_idx = action.card_index
        if attacker_idx == LEADER_TARGET:
            attacker = player.leader
        else:
            if attacker_idx >= len(player.field):
                return state
            attacker = player.field[attacker_idx]

        # Mark as attacked
        if attacker_idx == LEADER_TARGET:
            new_leader = attacker.copy(has_attacked=True, is_resting=True)
            new_player = player.copy(leader=new_leader)
        else:
            new_field = tuple(
                c.copy(has_attacked=True, is_resting=True) if i == attacker_idx else c
                for i, c in enumerate(player.field)
            )
            new_player = player.copy(field=new_field)

        # Create combat context
        combat = CombatContext(
            attacker_player=state.active_player,
            attacker_index=attacker_idx,
            target_index=action.target_index,
            attacker_power=attacker.total_power,
            original_target_index=action.target_index,
        )

        return state.with_player(state.active_player, new_player).copy(
            phase=GamePhase.BLOCKER_STEP,
            combat=combat,
        )

    def _handle_attach_don(self, state: GameState, action: Action) -> GameState:
        """Handle attaching DON to a card."""
        from core.actions import LEADER_TARGET

        player = state.current_player
        amount = action.don_amount or 1
        target_idx = action.card_index

        if player.don_active < amount:
            return state

        if target_idx == LEADER_TARGET:
            new_leader = player.leader.copy(
                attached_don=player.leader.attached_don + amount
            )
            new_player = player.copy(
                leader=new_leader,
                don_active=player.don_active - amount,
            )
        else:
            if target_idx >= len(player.field):
                return state
            new_field = tuple(
                c.copy(attached_don=c.attached_don + amount) if i == target_idx else c
                for i, c in enumerate(player.field)
            )
            new_player = player.copy(
                field=new_field,
                don_active=player.don_active - amount,
            )

        return state.with_player(state.active_player, new_player)

    def _handle_keep_hand(self, state: GameState) -> GameState:
        """Handle keeping hand (end mulligan)."""
        from core.game_state import advance_to_turn_1

        # Check if both players have decided
        # For simplicity, just advance to turn 1
        return advance_to_turn_1(state)

    def _handle_decline_block(self, state: GameState) -> GameState:
        """Handle declining to block."""
        from models.enums import GamePhase

        return state.copy(phase=GamePhase.COUNTER_STEP)

    def _handle_blocker(self, state: GameState, action: Action) -> GameState:
        """Handle activating a blocker."""
        from models.enums import GamePhase
        from core.game_state import CombatContext

        opponent = state.opponent_player
        blocker_idx = action.card_index

        if blocker_idx >= len(opponent.field):
            return state

        blocker = opponent.field[blocker_idx]

        # Rest the blocker
        new_field = tuple(
            c.copy(is_resting=True) if i == blocker_idx else c
            for i, c in enumerate(opponent.field)
        )
        new_opponent = opponent.copy(field=new_field)

        # Update combat context
        new_combat = CombatContext(
            attacker_player=state.combat.attacker_player,
            attacker_index=state.combat.attacker_index,
            target_index=blocker_idx,  # Redirect to blocker
            attacker_power=state.combat.attacker_power,
            original_target_index=state.combat.original_target_index,
            blocker_index=blocker_idx,
        )

        return state.with_player(1 - state.active_player, new_opponent).copy(
            phase=GamePhase.COUNTER_STEP,
            combat=new_combat,
        )

    def _handle_counter(self, state: GameState, action: Action) -> GameState:
        """Handle using a counter card."""
        from core.game_state import CombatContext

        opponent = state.opponent_player
        card_idx = action.card_index

        if card_idx >= len(opponent.hand):
            return state

        card = opponent.hand[card_idx]
        counter_value = card.counter or 0

        # Remove card from hand, add to trash
        new_hand = tuple(c for i, c in enumerate(opponent.hand) if i != card_idx)
        new_trash = opponent.trash + (card,)

        # Update combat context with counter total
        new_combat = CombatContext(
            attacker_player=state.combat.attacker_player,
            attacker_index=state.combat.attacker_index,
            target_index=state.combat.target_index,
            attacker_power=state.combat.attacker_power,
            original_target_index=state.combat.original_target_index,
            blocker_index=state.combat.blocker_index,
            counter_total=state.combat.counter_total + counter_value,
            counters_used=state.combat.counters_used + (card_idx,),
        )

        new_opponent = opponent.copy(hand=new_hand, trash=new_trash)

        return state.with_player(1 - state.active_player, new_opponent).copy(
            combat=new_combat,
        )

    def _handle_mulligan(self, state: GameState, action: Action) -> GameState:
        """Handle mulligan action (simplified - just keep hand for now)."""
        return self._handle_keep_hand(state)

    def _handle_activate_effect(self, state: GameState, action: Action) -> GameState:
        """Handle activating a card's [Activate: Main] effect."""
        from core.actions import LEADER_TARGET
        from effects.parser import parse_effect
        from effects.resolver import EffectResolver

        player = state.current_player
        card_idx = action.card_index

        # Get the card (leader or character)
        if card_idx == LEADER_TARGET:
            card = player.leader
        elif card_idx is not None and card_idx < len(player.field):
            card = player.field[card_idx]
        else:
            return state

        # Get the card's effect text
        if hasattr(card, 'card'):
            effect_text = getattr(card.card, 'effect', '') or ''
        else:
            effect_text = getattr(card, 'effect', '') or ''

        # Parse and try to resolve the effect
        try:
            effects = parse_effect(effect_text)
            # Find [Activate: Main] effects
            from effects.effects import EffectTiming
            for effect in effects:
                if effect.timing == EffectTiming.MAIN:
                    # Try to resolve - simplified for now
                    resolver = EffectResolver()
                    result = resolver.resolve(effect, state, state.active_player, card)
                    if result and result.new_state:
                        state = result.new_state
                    break
        except Exception:
            # If effect resolution fails, just continue
            pass

        # Mark effect as activated this turn (for [Once Per Turn])
        card_id = getattr(card, 'instance_id', None)
        if card_id is None:
            card_id = id(card)
        activated = tuple(list(state.activated_effects_this_turn) + [card_id])

        return state.copy(activated_effects_this_turn=activated)

    def _resolve_combat(self, state: GameState) -> GameState:
        """Resolve combat after counter step."""
        from models.enums import GamePhase
        from core.game_state import check_game_over
        from core.actions import LEADER_TARGET

        if state.combat is None:
            return state.copy(phase=GamePhase.MAIN)

        combat = state.combat
        attacker_power = combat.attacker_power
        defender_power = combat.counter_total

        # Get target
        opponent = state.players[1 - combat.attacker_player]
        target_idx = combat.target_index

        if target_idx == LEADER_TARGET:
            target = opponent.leader
            # Defender's DON is NOT active during opponent's turn
            defender_power += target.get_power(is_active_turn=False)
        else:
            if target_idx < len(opponent.field):
                target = opponent.field[target_idx]
                # Defender's DON is NOT active during opponent's turn
                defender_power += target.get_power(is_active_turn=False)
            else:
                return state.copy(phase=GamePhase.MAIN, combat=None)

        # Check if attack succeeds
        if attacker_power > defender_power:
            # Attack succeeds
            if target_idx == LEADER_TARGET:
                # Deal life damage
                if len(opponent.life_cards) > 0:
                    # Move top life card to hand (trigger might occur)
                    life_card = opponent.life_cards[0]
                    new_life = opponent.life_cards[1:]
                    new_hand = opponent.hand + (life_card,)
                    new_opponent = opponent.copy(
                        life_cards=new_life,
                        hand=new_hand,
                    )
                    new_state = state.with_player(1 - combat.attacker_player, new_opponent)
                    new_state = check_game_over(new_state, 1 - combat.attacker_player)
                    return new_state.copy(phase=GamePhase.MAIN, combat=None)
            else:
                # KO the character
                new_field = tuple(
                    c for i, c in enumerate(opponent.field) if i != target_idx
                )
                new_trash = opponent.trash + (target,)
                new_opponent = opponent.copy(field=new_field, trash=new_trash)
                return state.with_player(1 - combat.attacker_player, new_opponent).copy(
                    phase=GamePhase.MAIN, combat=None
                )

        # Attack blocked/failed
        return state.copy(phase=GamePhase.MAIN, combat=None)
