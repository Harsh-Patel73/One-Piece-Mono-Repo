"""Mutable wrapper around immutable GameState for API compatibility."""

from typing import Optional, Dict, Any, List
from ..core.game_state import GameState, PlayerState


class MutableGameState:
    """
    Wrapper for API-compatible mutable access to the game state.

    This adapter allows the simulator backend to work with the immutable
    game state from the training engine while providing a mutable interface
    for WebSocket-based game updates.
    """

    def __init__(self, state: Optional[GameState] = None):
        self._state = state
        self._action_log: List[Dict[str, Any]] = []

    @property
    def state(self) -> Optional[GameState]:
        """Get the underlying immutable state."""
        return self._state

    @state.setter
    def state(self, new_state: GameState):
        """Set a new immutable state."""
        self._state = new_state

    def to_dict(self, hide_opponent_hand: bool = False, perspective: int = 0) -> Dict[str, Any]:
        """
        Serialize game state to dictionary for API responses.

        Args:
            hide_opponent_hand: If True, hide the opponent's hand cards
            perspective: Player perspective (0 or 1)

        Returns:
            Dictionary representation of game state
        """
        if self._state is None:
            return {}

        return {
            "current_player": self._state.current_player,
            "phase": self._state.phase.value if hasattr(self._state.phase, 'value') else str(self._state.phase),
            "turn": self._state.turn,
            "player1": self._serialize_player(self._state.player1, hide_hand=(hide_opponent_hand and perspective == 1)),
            "player2": self._serialize_player(self._state.player2, hide_hand=(hide_opponent_hand and perspective == 0)),
            "action_log": self._action_log[-10:],  # Last 10 actions
        }

    def _serialize_player(self, player: PlayerState, hide_hand: bool = False) -> Dict[str, Any]:
        """Serialize player state to dictionary."""
        return {
            "hand": [] if hide_hand else [self._serialize_card(c) for c in player.hand],
            "hand_count": len(player.hand),
            "field": [self._serialize_card(c) for c in player.field],
            "leader": self._serialize_card(player.leader) if player.leader else None,
            "life_count": len(player.life_cards),
            "deck_count": len(player.deck),
            "trash": [self._serialize_card(c) for c in player.trash],
            "don_pool": player.don_pool,
            "active_don": player.don_pool.count("active") if isinstance(player.don_pool, list) else player.active_don,
        }

    def _serialize_card(self, card) -> Dict[str, Any]:
        """Serialize a card to dictionary."""
        if card is None:
            return None

        return {
            "id": card.id if hasattr(card, 'id') else card.card_id,
            "name": card.name,
            "type": card.card_type.value if hasattr(card.card_type, 'value') else str(card.card_type),
            "cost": card.cost,
            "power": card.power,
            "is_resting": getattr(card, 'is_resting', False),
            "attached_don": getattr(card, 'attached_don', 0),
        }

    def log_action(self, action_type: str, player: int, details: Dict[str, Any]):
        """Log an action for history tracking."""
        self._action_log.append({
            "type": action_type,
            "player": player,
            "details": details,
        })
