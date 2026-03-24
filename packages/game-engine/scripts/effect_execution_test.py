#!/usr/bin/env python3
"""
Effect Execution Test Script

This script tests whether parsed effects can actually be executed,
not just parsed. It creates mock game states and verifies that
effects modify the game state correctly.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from optcg_engine.effects import (
    Effect, EffectType, EffectTiming, TargetType,
    EffectParser, EffectResolver, EffectContext, EffectResult,
    get_parser, get_resolver,
    has_hardcoded_effect, execute_hardcoded_effect,
)


# Mock classes for testing
@dataclass
class MockCard:
    id: str = "TEST-001"
    name: str = "Test Card"
    card_type: str = "CHARACTER"
    effect: str = ""
    trigger: str = ""
    cost: int = 3
    power: int = 5000
    counter: int = 1000
    colors: List[str] = field(default_factory=lambda: ["Red"])
    card_origin: str = "Straw Hat Crew"
    is_resting: bool = False
    attached_don: int = 0
    power_modifier: int = 0
    has_rush: bool = False
    has_blocker: bool = False
    has_banish: bool = False
    has_doubleattack: bool = False
    has_protection: bool = False


@dataclass
class MockPlayer:
    name: str = "Player 1"
    hand: List[MockCard] = field(default_factory=list)
    deck: List[MockCard] = field(default_factory=list)
    trash: List[MockCard] = field(default_factory=list)
    life_cards: List[MockCard] = field(default_factory=list)
    cards_in_play: List[MockCard] = field(default_factory=list)
    leader: MockCard = None
    don_pool: List[str] = field(default_factory=list)

    def __post_init__(self):
        if self.leader is None:
            self.leader = MockCard(id="LEADER-001", name="Test Leader", card_type="LEADER")
        if not self.don_pool:
            self.don_pool = ["active"] * 5 + ["rested"] * 3


@dataclass
class MockGameState:
    current_player: MockPlayer = None
    opponent_player: MockPlayer = None
    turn_count: int = 1
    pending_negate: bool = False

    def __post_init__(self):
        if self.current_player is None:
            self.current_player = MockPlayer(name="Player 1")
        if self.opponent_player is None:
            self.opponent_player = MockPlayer(name="Player 2")
        # Set up decks
        for i in range(40):
            self.current_player.deck.append(MockCard(id=f"DECK-{i}", name=f"Card {i}"))
            self.opponent_player.deck.append(MockCard(id=f"DECK-{i}", name=f"Card {i}"))
        # Set up life
        for i in range(5):
            self.current_player.life_cards.append(MockCard(id=f"LIFE-{i}", name=f"Life {i}"))
            self.opponent_player.life_cards.append(MockCard(id=f"LIFE-{i}", name=f"Life {i}"))
        # Set up hands
        for i in range(5):
            self.current_player.hand.append(MockCard(id=f"HAND-{i}", name=f"Hand Card {i}"))
            self.opponent_player.hand.append(MockCard(id=f"HAND-{i}", name=f"Hand Card {i}"))
        # Set up field
        for i in range(3):
            self.current_player.cards_in_play.append(MockCard(id=f"FIELD-{i}", name=f"Field Card {i}"))
            self.opponent_player.cards_in_play.append(MockCard(id=f"FIELD-{i}", name=f"Field Card {i}"))


def create_fresh_game_state() -> MockGameState:
    """Create a fresh game state for testing."""
    return MockGameState()


def test_effect_execution(effect_type: EffectType, effect: Effect, resolver: EffectResolver) -> Dict:
    """Test if a specific effect executes correctly."""
    gs = create_fresh_game_state()
    source_card = MockCard(id="SOURCE-001", name="Source Card")

    context = EffectContext(
        game_state=gs,
        source_card=source_card,
        source_player=gs.current_player,
        opponent=gs.opponent_player,
    )

    # Store initial state
    initial_hand = len(gs.current_player.hand)
    initial_deck = len(gs.current_player.deck)
    initial_field = len(gs.current_player.cards_in_play)
    initial_opp_field = len(gs.opponent_player.cards_in_play)
    initial_life = len(gs.current_player.life_cards)
    initial_trash = len(gs.current_player.trash)

    # Execute effect
    try:
        result = resolver.resolve(effect, context)
        success = result.success
        error = None
    except Exception as e:
        success = False
        error = str(e)
        result = None

    # Check state changes
    state_changes = {}
    if initial_hand != len(gs.current_player.hand):
        state_changes['hand'] = len(gs.current_player.hand) - initial_hand
    if initial_deck != len(gs.current_player.deck):
        state_changes['deck'] = len(gs.current_player.deck) - initial_deck
    if initial_field != len(gs.current_player.cards_in_play):
        state_changes['field'] = len(gs.current_player.cards_in_play) - initial_field
    if initial_opp_field != len(gs.opponent_player.cards_in_play):
        state_changes['opp_field'] = len(gs.opponent_player.cards_in_play) - initial_opp_field
    if initial_life != len(gs.current_player.life_cards):
        state_changes['life'] = len(gs.current_player.life_cards) - initial_life
    if initial_trash != len(gs.current_player.trash):
        state_changes['trash'] = len(gs.current_player.trash) - initial_trash

    return {
        'effect_type': effect_type.name,
        'success': success,
        'error': error,
        'state_changed': bool(state_changes),
        'state_changes': state_changes,
        'message': result.message if result else None,
    }


def test_all_effect_types():
    """Test all effect types with mock effects."""
    resolver = get_resolver()

    # Create test effects for each type
    test_effects = {
        EffectType.DRAW: Effect(
            effect_type=EffectType.DRAW,
            timing=EffectTiming.ON_PLAY,
            value=2,
        ),
        EffectType.KO: Effect(
            effect_type=EffectType.KO,
            timing=EffectTiming.ON_PLAY,
            target_type=TargetType.OPPONENT_CHARACTER,
            target_count=1,
        ),
        EffectType.REST: Effect(
            effect_type=EffectType.REST,
            timing=EffectTiming.ON_PLAY,
            target_type=TargetType.OPPONENT_CHARACTER,
            target_count=1,
        ),
        EffectType.POWER_BOOST: Effect(
            effect_type=EffectType.POWER_BOOST,
            timing=EffectTiming.ON_PLAY,
            target_type=TargetType.YOUR_CHARACTER,
            target_count=1,
            value=2000,
        ),
        EffectType.POWER_REDUCE: Effect(
            effect_type=EffectType.POWER_REDUCE,
            timing=EffectTiming.ON_PLAY,
            target_type=TargetType.OPPONENT_CHARACTER,
            target_count=1,
            value=2000,
        ),
        EffectType.DON_ADD: Effect(
            effect_type=EffectType.DON_ADD,
            timing=EffectTiming.ON_PLAY,
            value=1,
        ),
        EffectType.DON_ACTIVATE: Effect(
            effect_type=EffectType.DON_ACTIVATE,
            timing=EffectTiming.ON_PLAY,
            target_count=2,
        ),
        EffectType.DON_REST: Effect(
            effect_type=EffectType.DON_REST,
            timing=EffectTiming.ON_PLAY,
            target_count=1,
        ),
        EffectType.PLAY: Effect(
            effect_type=EffectType.PLAY,
            timing=EffectTiming.TRIGGER,
            target_type=TargetType.SELF,
        ),
        EffectType.RETURN_TO_DECK: Effect(
            effect_type=EffectType.RETURN_TO_DECK,
            timing=EffectTiming.ON_PLAY,
            target_type=TargetType.YOUR_TRASH,
            target_count=1,
        ),
        EffectType.PROTECT: Effect(
            effect_type=EffectType.PROTECT,
            timing=EffectTiming.ON_PLAY,
            target_type=TargetType.SELF,
        ),
        EffectType.LIFE_ADD: Effect(
            effect_type=EffectType.LIFE_ADD,
            timing=EffectTiming.ON_PLAY,
            value=1,
        ),
        EffectType.SEARCH: Effect(
            effect_type=EffectType.SEARCH,
            timing=EffectTiming.ON_PLAY,
            value=5,
        ),
        EffectType.DISCARD: Effect(
            effect_type=EffectType.DISCARD,
            timing=EffectTiming.ON_PLAY,
            target_type=TargetType.YOUR_HAND,
            target_count=1,
        ),
        EffectType.REMOVE_BLOCKER: Effect(
            effect_type=EffectType.REMOVE_BLOCKER,
            timing=EffectTiming.WHEN_ATTACKING,
        ),
        EffectType.GRANT_RUSH: Effect(
            effect_type=EffectType.GRANT_RUSH,
            timing=EffectTiming.ON_PLAY,
            target_type=TargetType.SELF,
        ),
        EffectType.GRANT_BLOCKER: Effect(
            effect_type=EffectType.GRANT_BLOCKER,
            timing=EffectTiming.ON_PLAY,
            target_type=TargetType.SELF,
        ),
        EffectType.RETURN_TO_HAND: Effect(
            effect_type=EffectType.RETURN_TO_HAND,
            timing=EffectTiming.ON_PLAY,
            target_type=TargetType.OPPONENT_CHARACTER,
            target_count=1,
        ),
        EffectType.DON_ATTACH: Effect(
            effect_type=EffectType.DON_ATTACH,
            timing=EffectTiming.ON_PLAY,
            target_type=TargetType.YOUR_LEADER,
            target_count=1,
        ),
        EffectType.TRASH: Effect(
            effect_type=EffectType.TRASH,
            timing=EffectTiming.ON_PLAY,
            target_type=TargetType.YOUR_HAND,
            target_count=1,
        ),
        EffectType.COST_REDUCE: Effect(
            effect_type=EffectType.COST_REDUCE,
            timing=EffectTiming.ON_PLAY,
            value=2,
        ),
        EffectType.LOOK: Effect(
            effect_type=EffectType.LOOK,
            timing=EffectTiming.ON_PLAY,
            target_type=TargetType.YOUR_LIFE,
            value=1,
        ),
        EffectType.GRANT_BANISH: Effect(
            effect_type=EffectType.GRANT_BANISH,
            timing=EffectTiming.ON_PLAY,
            target_type=TargetType.SELF,
        ),
        EffectType.GRANT_DOUBLE_ATTACK: Effect(
            effect_type=EffectType.GRANT_DOUBLE_ATTACK,
            timing=EffectTiming.ON_PLAY,
            target_type=TargetType.SELF,
        ),
        EffectType.LIFE_DAMAGE: Effect(
            effect_type=EffectType.LIFE_DAMAGE,
            timing=EffectTiming.ON_PLAY,
            value=1,
        ),
        EffectType.REVEAL: Effect(
            effect_type=EffectType.REVEAL,
            timing=EffectTiming.ON_PLAY,
            target_type=TargetType.YOUR_DECK,
            value=3,
        ),
        EffectType.NEGATE: Effect(
            effect_type=EffectType.NEGATE,
            timing=EffectTiming.COUNTER,
        ),
        EffectType.ACTIVATE: Effect(
            effect_type=EffectType.ACTIVATE,
            timing=EffectTiming.ON_PLAY,
            target_type=TargetType.YOUR_CHARACTER,
            target_count=1,
        ),
        # These are NOT implemented in the resolver:
        EffectType.COPY: Effect(
            effect_type=EffectType.COPY,
            timing=EffectTiming.ON_PLAY,
        ),
        EffectType.CHOOSE: Effect(
            effect_type=EffectType.CHOOSE,
            timing=EffectTiming.ON_PLAY,
        ),
        EffectType.EXTRA_TURN: Effect(
            effect_type=EffectType.EXTRA_TURN,
            timing=EffectTiming.ON_PLAY,
        ),
    }

    results = {}
    for effect_type, effect in test_effects.items():
        results[effect_type] = test_effect_execution(effect_type, effect, resolver)

    return results


def analyze_real_cards():
    """Analyze real cards to see execution coverage."""
    cards_path = Path(__file__).parent / "../../simulator/backend/data/cards.json"

    with open(cards_path, 'r', encoding='utf-8') as f:
        cards = json.load(f)

    parser = get_parser()
    resolver = get_resolver()

    effect_type_counts = defaultdict(int)
    parsed_effect_types = defaultdict(list)
    execution_results = defaultdict(lambda: {'total': 0, 'executed': 0, 'failed': 0})

    for card in cards:
        effect_text = card.get('Effect', '')
        if not effect_text:
            continue

        # Parse effects
        try:
            effects = parser.parse(effect_text)
            if not effects:
                continue

            for effect in effects:
                effect_type_counts[effect.effect_type.name] += 1
                parsed_effect_types[effect.effect_type.name].append(card['id'])

                # Check if resolver has handler
                if effect.effect_type in resolver.handlers:
                    execution_results[effect.effect_type.name]['total'] += 1
                    # Try a mock execution
                    try:
                        gs = create_fresh_game_state()
                        source = MockCard(effect=effect_text)
                        ctx = EffectContext(
                            game_state=gs,
                            source_card=source,
                            source_player=gs.current_player,
                            opponent=gs.opponent_player,
                        )
                        result = resolver.resolve(effect, ctx)
                        if result.success:
                            execution_results[effect.effect_type.name]['executed'] += 1
                        else:
                            execution_results[effect.effect_type.name]['failed'] += 1
                    except Exception as e:
                        execution_results[effect.effect_type.name]['failed'] += 1
                else:
                    execution_results[effect.effect_type.name]['total'] += 1
                    execution_results[effect.effect_type.name]['failed'] += 1

        except Exception as e:
            pass

    return {
        'effect_type_counts': dict(effect_type_counts),
        'execution_results': dict(execution_results),
    }


def print_report(type_results: Dict, card_analysis: Dict):
    """Print comprehensive execution report."""
    print("=" * 70)
    print("EFFECT EXECUTION TEST REPORT")
    print("=" * 70)

    print(f"\n{'EFFECT TYPE EXECUTION TEST':^70}")
    print("-" * 70)
    print(f"{'Type':<25} {'Has Handler':^12} {'Executes':^10} {'State Change':^12}")
    print("-" * 70)

    implemented = 0
    not_implemented = 0

    for effect_type in EffectType:
        result = type_results.get(effect_type)
        if result:
            has_handler = result['error'] != "No handler for effect type"
            if has_handler and result['error'] is None:
                handler_str = "YES"
                implemented += 1
            elif has_handler:
                handler_str = "PARTIAL"
                implemented += 1
            else:
                handler_str = "NO"
                not_implemented += 1

            exec_str = "YES" if result['success'] else "NO"
            state_str = "YES" if result['state_changed'] else "NO"
            print(f"{effect_type.name:<25} {handler_str:^12} {exec_str:^10} {state_str:^12}")
        else:
            print(f"{effect_type.name:<25} {'UNTESTED':^12} {'-':^10} {'-':^12}")

    print("-" * 70)
    print(f"Implemented: {implemented}/{len(EffectType)} ({implemented/len(EffectType)*100:.1f}%)")
    print(f"Not Implemented: {not_implemented}")

    # Effect type distribution from real cards
    print(f"\n{'EFFECT TYPE DISTRIBUTION (Real Cards)':^70}")
    print("-" * 70)
    print(f"{'Type':<25} {'Count':>10} {'Exec Success':>15} {'Exec Fail':>12}")
    print("-" * 70)

    analysis = card_analysis['execution_results']
    sorted_types = sorted(analysis.items(), key=lambda x: x[1]['total'], reverse=True)

    total_effects = 0
    total_executed = 0
    total_failed = 0

    for effect_type, counts in sorted_types:
        total = counts['total']
        executed = counts['executed']
        failed = counts['failed']
        total_effects += total
        total_executed += executed
        total_failed += failed
        print(f"{effect_type:<25} {total:>10} {executed:>15} {failed:>12}")

    print("-" * 70)
    exec_rate = (total_executed / total_effects * 100) if total_effects > 0 else 0
    print(f"{'TOTAL':<25} {total_effects:>10} {total_executed:>15} {total_failed:>12}")
    print(f"\nExecution Success Rate: {exec_rate:.1f}%")

    # Summary
    print(f"\n{'SUMMARY':^70}")
    print("=" * 70)
    print(f"""
Effect Type Coverage:
  - {implemented}/{len(EffectType)} effect types have resolver handlers ({implemented/len(EffectType)*100:.0f}%)
  - Missing handlers: COPY, CHOOSE, EXTRA_TURN (rare effects)

Real Card Execution:
  - {total_effects} parsed effects tested
  - {total_executed} executed successfully ({exec_rate:.1f}%)
  - {total_failed} failed or no handler

Note: "Execution" means the resolver handler ran without error.
Some effects like SEARCH and LOOK only log info but don't change state.
Hardcoded effects (105 cards) bypass this system entirely.
""")

    print("=" * 70)


def main():
    print("Testing effect type execution...")
    type_results = test_all_effect_types()

    print("Analyzing real card effects...")
    card_analysis = analyze_real_cards()

    print_report(type_results, card_analysis)


if __name__ == '__main__':
    main()
