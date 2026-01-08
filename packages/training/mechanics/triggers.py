"""
Trigger mechanics for One Piece TCG.

Trigger Rules:
1. When your Leader takes damage, flip the top card of your Life pile face-up.
2. If that card has a [Trigger] effect, you may activate it.
3. The trigger effect is resolved, then the card goes to trash (or hand, depending).
4. Triggers are free to activate (no DON cost).
5. Cards with [Banish] skip the trigger check - life card goes directly to trash.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple, TYPE_CHECKING
from enum import Enum, auto

if TYPE_CHECKING:
    from models.cards import Card


class TriggerType(Enum):
    """Types of trigger effects."""
    DRAW = auto()           # Draw card(s)
    PLAY = auto()           # Play this card for free
    PLAY_CHARACTER = auto() # Play a character from hand
    POWER_BOOST = auto()    # Give power to a card
    REST = auto()            # Rest opponent's cards
    RETURN = auto()          # Return to hand
    TRASH = auto()           # Trash cards
    BLOCKER = auto()         # Gain Blocker
    COUNTER = auto()         # Counter boost
    SPECIAL = auto()         # Special/complex effect


@dataclass
class TriggerInfo:
    """Information about a trigger effect."""
    card: 'Card'
    trigger_text: str
    trigger_type: TriggerType
    can_activate: bool
    effect_data: dict  # Parsed effect data


class TriggerSystem:
    """Handles trigger mechanics during life damage."""

    @staticmethod
    def has_trigger(card: 'Card') -> bool:
        """Check if a card has a trigger effect."""
        trigger_text = card.trigger or ''
        return bool(trigger_text.strip())

    @staticmethod
    def parse_trigger(card: 'Card') -> Optional[TriggerInfo]:
        """
        Parse a card's trigger effect.

        Args:
            card: The life card with potential trigger

        Returns:
            TriggerInfo if card has trigger, None otherwise
        """
        trigger_text = card.trigger or ''
        if not trigger_text.strip():
            return None

        trigger_type, effect_data = TriggerSystem._parse_trigger_text(trigger_text)

        return TriggerInfo(
            card=card,
            trigger_text=trigger_text,
            trigger_type=trigger_type,
            can_activate=True,  # May have conditions
            effect_data=effect_data
        )

    @staticmethod
    def _parse_trigger_text(text: str) -> Tuple[TriggerType, dict]:
        """
        Parse trigger text to determine type and parameters.

        Common trigger patterns:
        - "[Trigger] Draw 1 card."
        - "[Trigger] Play this card."
        - "[Trigger] Rest 1 of your opponent's Characters."
        - "[Trigger] K.O. 1 of your opponent's Characters with 3000 or less power."
        """
        text_lower = text.lower()
        effect_data = {}

        # Draw triggers
        if 'draw' in text_lower:
            import re
            match = re.search(r'draw\s*(\d+)\s*card', text_lower)
            count = int(match.group(1)) if match else 1
            effect_data['count'] = count
            return TriggerType.DRAW, effect_data

        # Play this card triggers
        if 'play this card' in text_lower:
            return TriggerType.PLAY, effect_data

        # Play character triggers
        if 'play' in text_lower and 'character' in text_lower:
            import re
            # Find cost restriction
            match = re.search(r'(\d+)\s*or\s*less', text_lower)
            if match:
                effect_data['max_cost'] = int(match.group(1))
            return TriggerType.PLAY_CHARACTER, effect_data

        # Power boost triggers
        if 'power' in text_lower and ('+' in text or 'give' in text_lower):
            import re
            match = re.search(r'\+?(\d+)', text)
            if match:
                effect_data['power'] = int(match.group(1))
            return TriggerType.POWER_BOOST, effect_data

        # Rest triggers
        if 'rest' in text_lower:
            import re
            match = re.search(r'rest\s*(\d+)', text_lower)
            count = int(match.group(1)) if match else 1
            effect_data['count'] = count
            return TriggerType.REST, effect_data

        # Return to hand triggers
        if 'return' in text_lower:
            return TriggerType.RETURN, effect_data

        # Blocker triggers
        if 'blocker' in text_lower:
            return TriggerType.BLOCKER, effect_data

        # Default to special for complex triggers
        return TriggerType.SPECIAL, effect_data

    @staticmethod
    def resolve_trigger(
        game_state,
        trigger_info: TriggerInfo,
        player_index: int
    ) -> 'GameState':
        """
        Resolve a trigger effect.

        Args:
            game_state: Current game state
            trigger_info: The trigger to resolve
            player_index: Index of the player whose trigger is resolving

        Returns:
            Updated game state after trigger resolution
        """
        # This will integrate with the effect system
        # For now, handle common trigger types

        trigger_type = trigger_info.trigger_type
        effect_data = trigger_info.effect_data

        if trigger_type == TriggerType.DRAW:
            count = effect_data.get('count', 1)
            # Draw cards
            for _ in range(count):
                game_state = TriggerSystem._draw_card(game_state, player_index)

        elif trigger_type == TriggerType.PLAY:
            # Play the trigger card for free
            card = trigger_info.card
            game_state = TriggerSystem._play_card_free(game_state, player_index, card)

        elif trigger_type == TriggerType.POWER_BOOST:
            power = effect_data.get('power', 0)
            # This would need target selection - simplified for now
            pass

        # Send the card to trash (unless it was played)
        if trigger_type != TriggerType.PLAY:
            game_state = TriggerSystem._send_to_trash(
                game_state, player_index, trigger_info.card
            )

        return game_state

    @staticmethod
    def process_life_damage(
        game_state,
        defending_player_index: int,
        has_banish: bool = False
    ) -> Tuple['GameState', Optional[TriggerInfo]]:
        """
        Process life damage to a player.

        Args:
            game_state: Current game state
            defending_player_index: Player taking damage
            has_banish: If True, skip trigger activation

        Returns:
            Tuple of (updated game state, trigger info if applicable)
        """
        player = game_state.players[defending_player_index]

        if not player.life_cards:
            # No life cards - game should end
            return game_state, None

        # Flip top life card
        life_card = player.life_cards[-1]

        # Remove from life pile
        new_life = list(player.life_cards[:-1])

        # Update player state
        # (Actual implementation would create new immutable state)

        trigger_info = None

        if not has_banish and TriggerSystem.has_trigger(life_card):
            trigger_info = TriggerSystem.parse_trigger(life_card)
            # Player can choose to activate or not
            # For AI, always activate (can be refined)

        return game_state, trigger_info

    @staticmethod
    def _draw_card(game_state, player_index: int) -> 'GameState':
        """Helper to draw a card. Placeholder for immutable state version."""
        # Will be implemented with proper immutable state
        return game_state

    @staticmethod
    def _play_card_free(game_state, player_index: int, card: 'Card') -> 'GameState':
        """Helper to play a card for free. Placeholder for immutable state version."""
        # Will be implemented with proper immutable state
        return game_state

    @staticmethod
    def _send_to_trash(game_state, player_index: int, card: 'Card') -> 'GameState':
        """Helper to send a card to trash. Placeholder for immutable state version."""
        # Will be implemented with proper immutable state
        return game_state


def check_game_over(game_state, defending_player_index: int) -> Tuple[bool, Optional[int]]:
    """
    Check if the game is over after damage.

    Win condition: Reduce opponent's life to 0, then deal 1 more damage.

    Args:
        game_state: Current game state
        defending_player_index: Player who just took damage

    Returns:
        Tuple of (is_game_over, winner_index)
    """
    player = game_state.players[defending_player_index]

    if len(player.life_cards) == 0:
        # Player has 0 life - they lose
        # (The damage that reduced them to 0 is the winning hit)
        winner = 1 - defending_player_index
        return True, winner

    return False, None
