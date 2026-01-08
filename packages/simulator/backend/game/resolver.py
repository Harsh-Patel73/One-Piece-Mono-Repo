"""
Effect resolver for One Piece TCG.
"""

from typing import List, Optional, TYPE_CHECKING
from dataclasses import dataclass

from .effects import (
    Effect, EffectType, TargetType, TargetRestriction
)

if TYPE_CHECKING:
    from .engine import GameState, Player
    from .models.cards import Card


@dataclass
class EffectContext:
    """Context for effect resolution."""
    game_state: 'GameState'
    source_card: 'Card'
    source_player: 'Player'
    opponent: 'Player'
    targets: List['Card'] = None

    def __post_init__(self):
        if self.targets is None:
            self.targets = []


@dataclass
class EffectResult:
    """Result of effect resolution."""
    success: bool
    message: str = ""
    state_changed: bool = False
    targets_affected: List['Card'] = None

    def __post_init__(self):
        if self.targets_affected is None:
            self.targets_affected = []


class EffectResolver:
    """Resolves (executes) parsed effects against the game state."""

    def __init__(self):
        self.handlers = {
            EffectType.DRAW: self._resolve_draw,
            # Add other handlers here as needed
        }

    def resolve(
        self,
        effect: Effect,
        context: EffectContext,
        chosen_targets: List['Card'] = None
    ) -> EffectResult:
        if chosen_targets:
            context.targets = chosen_targets
        
        handler = self.handlers.get(effect.effect_type)
        if handler:
            return handler(effect, context)
        return EffectResult(success=False, message="No handler")

    def _resolve_draw(self, effect: Effect, context: EffectContext) -> EffectResult:
        player = context.source_player
        count = effect.value
        drawn = []
        for _ in range(count):
            card = player.draw_card()
            if card:
                drawn.append(card)
        return EffectResult(success=True, message=f"Drew {len(drawn)} cards")


# Singleton resolver
_resolver: Optional[EffectResolver] = None


def get_resolver() -> EffectResolver:
    global _resolver
    if _resolver is None:
        _resolver = EffectResolver()
    return _resolver


def resolve_effect(
    effect: Effect,
    game_state: 'GameState',
    source_card: 'Card',
    source_player: 'Player',
    targets: List['Card'] = None
) -> EffectResult:
    if game_state.current_player == source_player:
        opponent = game_state.opponent_player
    else:
        opponent = game_state.current_player

    context = EffectContext(
        game_state=game_state, source_card=source_card,
        source_player=source_player, opponent=opponent, targets=targets
    )
    return get_resolver().resolve(effect, context, targets)