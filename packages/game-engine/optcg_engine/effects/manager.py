"""
Card Effect Manager for One Piece TCG.

This module provides the integration layer between the game engine/MCTS
and the effect parsing/resolution system. It handles:
- Parsing effects on demand with caching
- Resolving effects at appropriate timings
- Managing effect state and duration
"""

from typing import Dict, List, Optional, Tuple, TYPE_CHECKING
from dataclasses import dataclass, field
import copy

from .effects import Effect, EffectType, EffectTiming, Duration, ParsedCard
from .parser import EffectParser
from .resolver import EffectResolver, EffectContext, EffectResult, get_resolver
from .hardcoded import has_hardcoded_effect, execute_hardcoded_effect

if TYPE_CHECKING:
    from game_engine import GameState, Player
    from models.cards import Card


# Global cache for parsed card effects
_effect_cache: Dict[str, List[Effect]] = {}
_parser: Optional[EffectParser] = None


def get_parser() -> EffectParser:
    """Get the singleton parser instance."""
    global _parser
    if _parser is None:
        _parser = EffectParser()
    return _parser


def parse_card_effects(card: 'Card') -> List[Effect]:
    """
    Parse and cache a card's effects.

    Args:
        card: The card to parse effects for

    Returns:
        List of parsed Effect objects
    """
    # Check cache first
    if card.id in _effect_cache:
        return _effect_cache[card.id]

    parser = get_parser()
    effects = []

    # Parse main effect text
    if card.effect:
        try:
            parsed = parser.parse(card.effect)
            # parse() returns List[Effect] directly
            if parsed:
                effects.extend(parsed)
        except Exception as e:
            pass  # Many effects won't parse cleanly, that's OK

    # Parse trigger text (separate from main effect)
    # Note: Most cards have trigger="Trigger" which just means "has a trigger"
    # The actual trigger effect is usually in the main effect text after [Trigger]
    if card.trigger and card.trigger.strip() and card.trigger.lower() != 'trigger':
        try:
            parsed = parser.parse(card.trigger)
            if parsed:
                # Mark all parsed effects with TRIGGER timing
                for eff in parsed:
                    if eff.timing == EffectTiming.CONTINUOUS:
                        eff.timing = EffectTiming.TRIGGER
                effects.extend(parsed)
        except Exception:
            pass  # Trigger text is often just "Trigger" which won't parse

    # Cache and return
    _effect_cache[card.id] = effects
    return effects


def get_effects_by_timing(card: 'Card', timing: EffectTiming) -> List[Effect]:
    """
    Get all effects for a card with a specific timing.

    Args:
        card: The card to get effects for
        timing: The timing to filter by

    Returns:
        List of effects with matching timing
    """
    all_effects = parse_card_effects(card)
    return [e for e in all_effects if e.timing == timing]


def check_don_requirement(card: 'Card', effect: Effect) -> bool:
    """Check if DON requirement is met for an effect."""
    if effect.don_requirement <= 0:
        return True
    attached = getattr(card, 'attached_don', 0)
    return attached >= effect.don_requirement


class CardEffectManager:
    """
    Manages effect resolution for a game.

    This class handles the integration between game events and effect resolution.
    It tracks effect state and ensures effects are resolved at appropriate times.
    """

    def __init__(self):
        self.resolver = get_resolver()
        # Track temporary effects that expire
        self.temporary_effects: List[Tuple['Card', Effect, int]] = []  # (card, effect, expires_turn)
        # Track once-per-turn effects that have been used
        self.used_once_per_turn: Dict[str, List[str]] = {}  # card_id -> [effect_ids used]

    def on_turn_start(self, game_state: 'GameState', player: 'Player'):
        """Called at the start of each turn to reset state."""
        # Clear once-per-turn usage
        self.used_once_per_turn.clear()

        # Check for expired temporary effects
        turn = game_state.turn_count
        expired = []
        for card, effect, expires in self.temporary_effects:
            if turn > expires:
                # Revert the effect
                self._revert_effect(card, effect)
                expired.append((card, effect, expires))

        for item in expired:
            self.temporary_effects.remove(item)

        # Resolve START_OF_TURN effects
        self._resolve_timing_effects(
            game_state, player, EffectTiming.START_OF_TURN
        )

    def on_turn_end(self, game_state: 'GameState', player: 'Player'):
        """Called at the end of each turn."""
        # Resolve END_OF_TURN effects
        self._resolve_timing_effects(
            game_state, player, EffectTiming.END_OF_TURN
        )

        # Clear THIS_TURN duration effects
        self._clear_turn_effects(player)

    def on_card_play(
        self,
        game_state: 'GameState',
        player: 'Player',
        card: 'Card'
    ) -> List[EffectResult]:
        """
        Called when a card is played. Resolves ON_PLAY effects.

        Args:
            game_state: Current game state
            player: Player who played the card
            card: The card being played

        Returns:
            List of effect results
        """
        results = []

        # Check for hardcoded effects first
        executed = False
        if has_hardcoded_effect(card.id, 'ON_PLAY'):
            executed = execute_hardcoded_effect(game_state, player, card, 'ON_PLAY')

        # ONLY run parsed effects if hardcoded didn't execute
        # This prevents duplicate execution (e.g., "Draw 2" happening twice)
        if not executed:
            effects = get_effects_by_timing(card, EffectTiming.ON_PLAY)
        else:
            effects = []

        for effect in effects:
            # Check DON requirement
            if not check_don_requirement(card, effect):
                continue

            # Check once-per-turn
            if effect.once_per_turn:
                effect_id = f"{card.id}_{effect.effect_type.name}"
                used = self.used_once_per_turn.get(card.id, [])
                if effect_id in used:
                    continue
                used.append(effect_id)
                self.used_once_per_turn[card.id] = used

            # Resolve the effect
            result = self._resolve_effect(game_state, player, card, effect)
            results.append(result)

            # Track temporary effects
            if effect.duration == Duration.THIS_TURN:
                self.temporary_effects.append(
                    (card, effect, game_state.turn_count)
                )

        return results

    def on_attack_declare(
        self,
        game_state: 'GameState',
        player: 'Player',
        attacker: 'Card',
        target: 'Card'
    ) -> List[EffectResult]:
        """
        Called when an attack is declared. Resolves WHEN_ATTACKING effects.
        Checks hardcoded effects first, falls back to parser.
        """
        results = []

        # Check hardcoded [When Attacking] effects first
        if has_hardcoded_effect(attacker.id, 'on_attack'):
            execute_hardcoded_effect(game_state, player, attacker, 'on_attack')
            return results  # Hardcoded takes over entirely

        # Parser-based WHEN_ATTACKING effects
        effects = get_effects_by_timing(attacker, EffectTiming.WHEN_ATTACKING)
        for effect in effects:
            if not check_don_requirement(attacker, effect):
                continue
            result = self._resolve_effect(game_state, player, attacker, effect)
            results.append(result)

        return results

    def on_opponent_attack(
        self,
        game_state: 'GameState',
        attacking_player: 'Player',
        defending_player: 'Player',
        attacker: 'Card',
        target: 'Card'
    ) -> List[EffectResult]:
        """
        Called when an opponent declares an attack. Resolves ON_OPPONENT_ATTACK effects.

        This triggers effects on the DEFENDING player's cards that have
        "[On Your Opponent's Attack]" timing (e.g., Izo EB01-002).

        Args:
            game_state: Current game state
            attacking_player: Player who is attacking
            defending_player: Player being attacked (whose effects trigger)
            attacker: The attacking card
            target: The target of the attack

        Returns:
            List of effect results
        """
        results = []

        # Check hardcoded effects first on defending player's leader
        if defending_player.leader:
            if has_hardcoded_effect(defending_player.leader.id, 'ON_OPPONENT_ATTACK'):
                execute_hardcoded_effect(
                    game_state, defending_player, defending_player.leader, 'ON_OPPONENT_ATTACK'
                )

        # Check hardcoded effects on defending player's characters
        for card in defending_player.cards_in_play:
            if has_hardcoded_effect(card.id, 'ON_OPPONENT_ATTACK'):
                execute_hardcoded_effect(game_state, defending_player, card, 'ON_OPPONENT_ATTACK')

        # Check parsed effects on leader
        if defending_player.leader:
            effects = get_effects_by_timing(defending_player.leader, EffectTiming.ON_OPPONENT_ATTACK)
            for effect in effects:
                if not check_don_requirement(defending_player.leader, effect):
                    continue

                # Check once-per-turn
                if effect.once_per_turn:
                    effect_id = f"{defending_player.leader.id}_ON_OPPONENT_ATTACK"
                    used = self.used_once_per_turn.get(defending_player.leader.id, [])
                    if effect_id in used:
                        continue
                    used.append(effect_id)
                    self.used_once_per_turn[defending_player.leader.id] = used

                result = self._resolve_effect(
                    game_state, defending_player, defending_player.leader, effect
                )
                results.append(result)

        # Check parsed effects on defending player's characters
        for card in defending_player.cards_in_play:
            effects = get_effects_by_timing(card, EffectTiming.ON_OPPONENT_ATTACK)
            for effect in effects:
                if not check_don_requirement(card, effect):
                    continue

                # Check once-per-turn
                if effect.once_per_turn:
                    effect_id = f"{card.id}_ON_OPPONENT_ATTACK"
                    used = self.used_once_per_turn.get(card.id, [])
                    if effect_id in used:
                        continue
                    used.append(effect_id)
                    self.used_once_per_turn[card.id] = used

                result = self._resolve_effect(game_state, defending_player, card, effect)
                results.append(result)

        return results

    def activate_main(
        self,
        game_state: 'GameState',
        player: 'Player',
        card: 'Card'
    ) -> List[EffectResult]:
        """
        Parser-based fallback for [Activate: Main] effects on a specific card.
        Called by game_engine.activate_main_effect after hardcoded check fails.
        """
        results = []
        effects = get_effects_by_timing(card, EffectTiming.MAIN)
        for effect in effects:
            if not check_don_requirement(card, effect):
                continue
            resolver = get_resolver()
            context = EffectContext(
                game_state=game_state,
                source_card=card,
                source_player=player,
                opponent=None,
            )
            if resolver.can_resolve(effect, context):
                result = resolver.resolve(effect, context)
                results.append(result)
        return results

    def on_block_declare(
        self,
        game_state: 'GameState',
        player: 'Player',
        blocker: 'Card',
        attacker: 'Card'
    ) -> List[EffectResult]:
        """
        Called when a block is declared. Resolves ON_BLOCK effects.
        """
        results = []
        effects = get_effects_by_timing(blocker, EffectTiming.ON_BLOCK)

        for effect in effects:
            if not check_don_requirement(blocker, effect):
                continue

            result = self._resolve_effect(game_state, player, blocker, effect)
            results.append(result)

        return results

    def on_ko(
        self,
        game_state: 'GameState',
        player: 'Player',
        ko_card: 'Card'
    ) -> List[EffectResult]:
        """
        Called when a card is K.O.'d. Resolves ON_KO effects.
        Checks hardcoded effects first, falls back to parser.
        Also checks for ON_YOUR_CHARACTER_KO effects on other cards (like Ace's leader).
        """
        results = []

        # Check hardcoded ON_KO effects first
        if has_hardcoded_effect(ko_card.id, 'on_ko'):
            execute_hardcoded_effect(game_state, player, ko_card, 'on_ko')
        else:
            # Parser-based ON_KO effects
            effects = get_effects_by_timing(ko_card, EffectTiming.ON_KO)
            for effect in effects:
                if not check_don_requirement(ko_card, effect):
                    continue
                result = self._resolve_effect(game_state, player, ko_card, effect)
                results.append(result)

        # Resolve ON_YOUR_CHARACTER_KO effects on player's leader and other characters
        # This handles effects like Ace's "When your Character with 6000 base power or more is K.O.'d"
        self._resolve_on_character_ko_effects(game_state, player, ko_card)

        return results

    def _resolve_on_character_ko_effects(
        self,
        game_state: 'GameState',
        owner: 'Player',
        ko_card: 'Card'
    ):
        """
        Resolve effects that trigger when one of YOUR characters is K.O.'d.

        This handles effects like Ace's:
        "[DON!! x1] [Once Per Turn] When your Character with 6000 base power or more is K.O.'d, draw 1 card"
        """
        # Check if the KO'd card meets power requirements (for effects that specify power)
        # Get base power of the KO'd card
        ko_base_power = getattr(ko_card, 'power', 0)

        # Check leader for ON_YOUR_CHARACTER_KO effects
        if owner.leader:
            effects = get_effects_by_timing(owner.leader, EffectTiming.ON_TAKE_DAMAGE)  # Combined trigger
            effects.extend(get_effects_by_timing(owner.leader, EffectTiming.ON_YOUR_CHARACTER_KO))

            for effect in effects:
                # Check DON requirement
                if not check_don_requirement(owner.leader, effect):
                    continue

                # Check if effect requires specific power threshold
                # The raw_text will contain "6000 base power or more"
                if effect.raw_text and '6000' in effect.raw_text:
                    if ko_base_power < 6000:
                        continue

                # Check once-per-turn (share with ON_TAKE_DAMAGE since it's the same effect)
                if effect.once_per_turn:
                    effect_id = f"{owner.leader.id}_ON_TAKE_DAMAGE"  # Same effect ID for combined trigger
                    used = self.used_once_per_turn.get(owner.leader.id, [])
                    if effect_id in used:
                        continue
                    used.append(effect_id)
                    self.used_once_per_turn[owner.leader.id] = used

                self._resolve_effect(game_state, owner, owner.leader, effect)

    def on_life_damage(
        self,
        game_state: 'GameState',
        damaged_player: 'Player',
        life_card: 'Card',
        has_banish: bool = False
    ) -> Tuple[bool, Optional[EffectResult]]:
        """
        Called when a player takes life damage.

        Args:
            game_state: Current game state
            damaged_player: Player taking damage
            life_card: The life card being lost
            has_banish: If True, skip trigger activation

        Returns:
            Tuple of (has_trigger, trigger_result)
        """
        # Resolve ON_TAKE_DAMAGE effects (like Ace's draw effect)
        self._resolve_on_take_damage_effects(game_state, damaged_player)

        if has_banish:
            return False, None

        # Check for trigger
        effects = get_effects_by_timing(life_card, EffectTiming.TRIGGER)
        if not effects:
            return False, None

        # Resolve trigger effects
        for effect in effects:
            result = self._resolve_effect(
                game_state, damaged_player, life_card, effect
            )
            return True, result

        return False, None

    def _resolve_on_take_damage_effects(
        self,
        game_state: 'GameState',
        damaged_player: 'Player'
    ):
        """
        Resolve effects that trigger when a player takes life damage.

        This handles effects like Ace's:
        "[DON!! x1] [Once Per Turn] When you take damage, draw 1 card"
        """
        # Check leader for ON_TAKE_DAMAGE effects
        if damaged_player.leader:
            effects = get_effects_by_timing(damaged_player.leader, EffectTiming.ON_TAKE_DAMAGE)
            for effect in effects:
                # Check DON requirement
                if not check_don_requirement(damaged_player.leader, effect):
                    continue

                # Check once-per-turn
                if effect.once_per_turn:
                    effect_id = f"{damaged_player.leader.id}_ON_TAKE_DAMAGE"
                    used = self.used_once_per_turn.get(damaged_player.leader.id, [])
                    if effect_id in used:
                        continue
                    used.append(effect_id)
                    self.used_once_per_turn[damaged_player.leader.id] = used

                self._resolve_effect(game_state, damaged_player, damaged_player.leader, effect)

        # Also check characters for ON_TAKE_DAMAGE effects (rare but possible)
        for card in damaged_player.cards_in_play:
            effects = get_effects_by_timing(card, EffectTiming.ON_TAKE_DAMAGE)
            for effect in effects:
                if check_don_requirement(card, effect):
                    self._resolve_effect(game_state, damaged_player, card, effect)

    def on_counter(
        self,
        game_state: 'GameState',
        player: 'Player',
        counter_card: 'Card'
    ) -> List[EffectResult]:
        """
        Called when a counter card is used. Resolves COUNTER effects.
        """
        results = []
        effects = get_effects_by_timing(counter_card, EffectTiming.COUNTER)

        for effect in effects:
            result = self._resolve_effect(game_state, player, counter_card, effect)
            results.append(result)

        return results

    def activate_main_effect(
        self,
        game_state: 'GameState',
        player: 'Player',
        card: 'Card'
    ) -> List[EffectResult]:
        """
        Activate a card's [Activate: Main] effect.
        """
        results = []
        effects = get_effects_by_timing(card, EffectTiming.MAIN)

        for effect in effects:
            if not check_don_requirement(card, effect):
                continue

            # Check once-per-turn
            if effect.once_per_turn:
                effect_id = f"{card.id}_{effect.effect_type.name}_main"
                used = self.used_once_per_turn.get(card.id, [])
                if effect_id in used:
                    continue
                used.append(effect_id)
                self.used_once_per_turn[card.id] = used

            result = self._resolve_effect(game_state, player, card, effect)
            results.append(result)

        return results

    def get_continuous_power_bonus(self, card: 'Card', game_state: 'GameState') -> int:
        """
        Calculate continuous power bonuses for a card.

        This handles effects like "If you have 2+ rested characters, +1000 power"
        """
        bonus = 0
        effects = get_effects_by_timing(card, EffectTiming.CONTINUOUS)

        for effect in effects:
            if effect.effect_type == EffectType.POWER_BOOST:
                # Check DON requirement
                if not check_don_requirement(card, effect):
                    continue

                # Check conditions (simplified for now)
                if effect.condition:
                    # TODO: Evaluate complex conditions
                    pass
                else:
                    bonus += effect.value

        return bonus

    def _resolve_effect(
        self,
        game_state: 'GameState',
        player: 'Player',
        card: 'Card',
        effect: Effect
    ) -> EffectResult:
        """Resolve a single effect."""
        # Determine opponent
        if game_state.current_player == player:
            opponent = game_state.opponent_player
        else:
            opponent = game_state.current_player

        context = EffectContext(
            game_state=game_state,
            source_card=card,
            source_player=player,
            opponent=opponent,
        )

        return self.resolver.resolve(effect, context)

    def _resolve_timing_effects(
        self,
        game_state: 'GameState',
        player: 'Player',
        timing: EffectTiming
    ):
        """Resolve all effects of a specific timing for a player's cards."""
        # Leader effects
        if player.leader:
            effects = get_effects_by_timing(player.leader, timing)
            for effect in effects:
                if check_don_requirement(player.leader, effect):
                    self._resolve_effect(game_state, player, player.leader, effect)

        # Field effects
        for card in player.cards_in_play:
            effects = get_effects_by_timing(card, timing)
            for effect in effects:
                if check_don_requirement(card, effect):
                    self._resolve_effect(game_state, player, card, effect)

    def _revert_effect(self, card: 'Card', effect: Effect):
        """Revert a temporary effect."""
        if effect.effect_type == EffectType.POWER_BOOST:
            current = getattr(card, 'power_modifier', 0)
            card.power_modifier = current - effect.value
        elif effect.effect_type == EffectType.GRANT_RUSH:
            card.has_rush = False
        elif effect.effect_type == EffectType.GRANT_BLOCKER:
            card.has_blocker = False
        elif effect.effect_type == EffectType.GRANT_BANISH:
            card.has_banish = False
        elif effect.effect_type == EffectType.GRANT_DOUBLE_ATTACK:
            card.has_doubleattack = False

    def on_opponent_event_play(
        self,
        game_state: 'GameState',
        attacker_player: 'Player',
        event_card: 'Card'
    ) -> List[EffectResult]:
        """Called when a player plays/activates an Event during combat (counter step).

        Fires `on_event_activated` on every card belonging to the *attacker_player*
        (the one whose turn it is) so effects like Usopp OP01-004 can react.
        """
        results = []
        # Fire hardcoded on_event_activated for leader
        if attacker_player.leader:
            if has_hardcoded_effect(attacker_player.leader.id, 'on_event_activated'):
                execute_hardcoded_effect(game_state, attacker_player, attacker_player.leader, 'on_event_activated')
        # Fire for each character on the attacker's field
        for card in list(attacker_player.cards_in_play):
            if has_hardcoded_effect(card.id, 'on_event_activated'):
                execute_hardcoded_effect(game_state, attacker_player, card, 'on_event_activated')
        return results

    def _clear_turn_effects(self, player: 'Player'):
        """Clear effects that last only this turn."""
        # Reset power modifiers for all cards
        if player.leader:
            player.leader.power_modifier = 0

        for card in player.cards_in_play:
            card.power_modifier = 0


# Singleton manager
_manager: Optional[CardEffectManager] = None


def get_effect_manager() -> CardEffectManager:
    """Get the singleton effect manager."""
    global _manager
    if _manager is None:
        _manager = CardEffectManager()
    return _manager


def clear_effect_cache():
    """Clear the effect cache (useful for testing)."""
    global _effect_cache
    _effect_cache.clear()
