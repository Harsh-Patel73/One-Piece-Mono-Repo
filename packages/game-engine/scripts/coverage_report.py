#!/usr/bin/env python3
"""
Effect Coverage Report Generator

This script analyzes all OPTCG cards and generates a report showing:
- Which cards have hardcoded effect implementations
- Which cards have effects that can be parsed by the pattern-based parser
- Which cards have effects that need attention (not covered)
"""

import json
import sys
import os
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Optional, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from optcg_engine.effects.hardcoded import (
    _hardcoded_effects,
    has_hardcoded_effect,
    get_all_hardcoded_cards,
    get_hardcoded_effect_count,
)
from optcg_engine.effects.parser import EffectParser


def load_cards(cards_path: str) -> List[Dict]:
    """Load all cards from the JSON file."""
    with open(cards_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_effect_timing(effect_text: str) -> List[str]:
    """Extract effect timings from effect text."""
    timings = []
    timing_patterns = [
        ('[On Play]', 'ON_PLAY'),
        ('[When Attacking]', 'WHEN_ATTACKING'),
        ('[Activate: Main]', 'ACTIVATE_MAIN'),
        ('[On K.O.]', 'ON_KO'),
        ('[Counter]', 'COUNTER'),
        ('[Trigger]', 'TRIGGER'),
        ('[On Block]', 'ON_BLOCK'),
        ('[DON!! x', 'DON_REQUIREMENT'),
        ('[Your Turn]', 'YOUR_TURN'),
        ('[Opponent\'s Turn]', 'OPPONENT_TURN'),
        ('[Once Per Turn]', 'ONCE_PER_TURN'),
        ('[End of Your Turn]', 'END_OF_TURN'),
        ('[Start of Your Turn]', 'START_OF_TURN'),
    ]
    for pattern, timing in timing_patterns:
        if pattern in effect_text:
            timings.append(timing)

    # Check for keywords
    keywords = ['[Rush]', '[Blocker]', '[Banish]', '[Double Attack]']
    for kw in keywords:
        if kw in effect_text:
            timings.append(kw.strip('[]').upper())

    return timings if timings else ['NO_TIMING']


def analyze_card(card: Dict, parser: EffectParser) -> Dict[str, Any]:
    """Analyze a single card's effect coverage."""
    card_id = card.get('id', 'UNKNOWN')
    card_name = card.get('name', 'Unknown')
    effect_text = card.get('Effect', '')
    card_type = card.get('cardType', 'UNKNOWN')

    result = {
        'id': card_id,
        'name': card_name,
        'card_type': card_type,
        'effect_text': effect_text,
        'has_effect': bool(effect_text),
        'timings': [],
        'has_hardcoded': False,
        'hardcoded_timings': [],
        'parser_success': False,
        'parsed_effects': [],
        'coverage_status': 'NO_EFFECT',
        'needs_attention': False,
    }

    if not effect_text:
        return result

    # Get timings from effect text
    result['timings'] = get_effect_timing(effect_text)

    # Check for hardcoded implementation
    base_id = card_id.split('_')[0] if '_p' in card_id or '_r' in card_id else card_id
    if has_hardcoded_effect(base_id):
        result['has_hardcoded'] = True
        if base_id in _hardcoded_effects:
            result['hardcoded_timings'] = [e.timing for e in _hardcoded_effects[base_id]]
        elif card_id in _hardcoded_effects:
            result['hardcoded_timings'] = [e.timing for e in _hardcoded_effects[card_id]]

    # Try parsing with pattern-based parser
    try:
        parsed = parser.parse(effect_text)
        if parsed:
            result['parser_success'] = True
            if isinstance(parsed, list):
                result['parsed_effects'] = [str(e.effect_type) if hasattr(e, 'effect_type') else str(e) for e in parsed]
            else:
                result['parsed_effects'] = [str(parsed.effect_type) if hasattr(parsed, 'effect_type') else str(parsed)]
    except Exception as e:
        result['parser_error'] = str(e)

    # Determine coverage status
    if result['has_hardcoded']:
        result['coverage_status'] = 'HARDCODED'
    elif result['parser_success']:
        result['coverage_status'] = 'PARSED'
    else:
        result['coverage_status'] = 'UNCOVERED'
        result['needs_attention'] = True

    return result


def generate_report(cards: List[Dict]) -> Dict[str, Any]:
    """Generate comprehensive coverage report."""
    parser = EffectParser()

    report = {
        'summary': {
            'total_cards': len(cards),
            'cards_with_effects': 0,
            'hardcoded_count': 0,
            'parsed_count': 0,
            'uncovered_count': 0,
        },
        'by_timing': defaultdict(lambda: {'total': 0, 'hardcoded': 0, 'parsed': 0, 'uncovered': 0}),
        'by_card_type': defaultdict(lambda: {'total': 0, 'with_effects': 0, 'covered': 0}),
        'hardcoded_cards': [],
        'parsed_cards': [],
        'uncovered_cards': [],
        'all_results': [],
    }

    for card in cards:
        result = analyze_card(card, parser)
        report['all_results'].append(result)

        card_type = result['card_type']
        report['by_card_type'][card_type]['total'] += 1

        if result['has_effect']:
            report['summary']['cards_with_effects'] += 1
            report['by_card_type'][card_type]['with_effects'] += 1

            # Count by timing
            for timing in result['timings']:
                report['by_timing'][timing]['total'] += 1
                if result['has_hardcoded']:
                    report['by_timing'][timing]['hardcoded'] += 1
                elif result['parser_success']:
                    report['by_timing'][timing]['parsed'] += 1
                else:
                    report['by_timing'][timing]['uncovered'] += 1

            # Categorize
            if result['has_hardcoded']:
                report['summary']['hardcoded_count'] += 1
                report['hardcoded_cards'].append(result)
                report['by_card_type'][card_type]['covered'] += 1
            elif result['parser_success']:
                report['summary']['parsed_count'] += 1
                report['parsed_cards'].append(result)
                report['by_card_type'][card_type]['covered'] += 1
            else:
                report['summary']['uncovered_count'] += 1
                report['uncovered_cards'].append(result)

    return report


def sanitize_text(text: str) -> str:
    """Sanitize text for console output by replacing problematic characters."""
    # Replace Unicode minus with ASCII minus
    text = text.replace('\u2212', '-')
    # Replace other common Unicode characters
    text = text.replace('\u2019', "'")
    text = text.replace('\u2018', "'")
    text = text.replace('\u201c', '"')
    text = text.replace('\u201d', '"')
    text = text.replace('\u2013', '-')
    text = text.replace('\u2014', '-')
    return text


def print_report(report: Dict[str, Any], verbose: bool = False):
    """Print formatted coverage report."""
    summary = report['summary']

    print("=" * 70)
    print("OPTCG EFFECT COVERAGE REPORT")
    print("=" * 70)

    total_with_effects = summary['cards_with_effects']
    covered = summary['hardcoded_count'] + summary['parsed_count']
    coverage_pct = (covered / total_with_effects * 100) if total_with_effects > 0 else 0

    print(f"\n{'SUMMARY':^70}")
    print("-" * 70)
    print(f"Total Cards:           {summary['total_cards']:>6}")
    print(f"Cards with Effects:    {summary['cards_with_effects']:>6}")
    print(f"  - Hardcoded:         {summary['hardcoded_count']:>6} ({summary['hardcoded_count']/total_with_effects*100:.1f}%)")
    print(f"  - Parser Handled:    {summary['parsed_count']:>6} ({summary['parsed_count']/total_with_effects*100:.1f}%)")
    print(f"  - Uncovered:         {summary['uncovered_count']:>6} ({summary['uncovered_count']/total_with_effects*100:.1f}%)")
    print(f"\nTOTAL COVERAGE:        {coverage_pct:>5.1f}%")

    print(f"\n{'BY EFFECT TIMING':^70}")
    print("-" * 70)
    print(f"{'Timing':<25} {'Total':>8} {'Hardcoded':>10} {'Parsed':>10} {'Uncovered':>10}")
    print("-" * 70)

    for timing in sorted(report['by_timing'].keys(), key=lambda x: -report['by_timing'][x]['total']):
        data = report['by_timing'][timing]
        print(f"{timing:<25} {data['total']:>8} {data['hardcoded']:>10} {data['parsed']:>10} {data['uncovered']:>10}")

    print(f"\n{'BY CARD TYPE':^70}")
    print("-" * 70)
    print(f"{'Type':<20} {'Total':>10} {'With Effects':>15} {'Covered':>12} {'Coverage %':>12}")
    print("-" * 70)

    for ctype in sorted(report['by_card_type'].keys()):
        data = report['by_card_type'][ctype]
        pct = (data['covered'] / data['with_effects'] * 100) if data['with_effects'] > 0 else 100
        print(f"{ctype:<20} {data['total']:>10} {data['with_effects']:>15} {data['covered']:>12} {pct:>11.1f}%")

    print(f"\n{'HARDCODED EFFECTS':^70}")
    print("-" * 70)
    print(f"Total hardcoded effects: {get_hardcoded_effect_count()}")
    print(f"Cards with hardcoded:    {len(get_all_hardcoded_cards())}")

    if verbose:
        print("\nHardcoded card IDs:")
        for card_id in sorted(get_all_hardcoded_cards()):
            effects = _hardcoded_effects.get(card_id, [])
            timings = [e.timing for e in effects]
            print(f"  {card_id}: {', '.join(timings)}")

    # Show sample of uncovered cards
    print(f"\n{'SAMPLE UNCOVERED CARDS (first 20)':^70}")
    print("-" * 70)

    uncovered = report['uncovered_cards'][:20]
    for card in uncovered:
        effect_text = sanitize_text(card['effect_text'])
        effect_preview = (effect_text[:60] + '...') if len(effect_text) > 60 else effect_text
        print(f"\n{sanitize_text(card['id'])} - {sanitize_text(card['name'])}")
        print(f"  Timings: {', '.join(card['timings'])}")
        print(f"  Effect: {effect_preview}")

    if len(report['uncovered_cards']) > 20:
        print(f"\n... and {len(report['uncovered_cards']) - 20} more uncovered cards")

    print("\n" + "=" * 70)


def export_uncovered_csv(report: Dict[str, Any], output_path: str):
    """Export uncovered cards to CSV for further analysis."""
    import csv

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Name', 'Card Type', 'Timings', 'Effect Text'])

        for card in report['uncovered_cards']:
            writer.writerow([
                card['id'],
                card['name'],
                card['card_type'],
                '; '.join(card['timings']),
                card['effect_text'],
            ])

    print(f"\nExported {len(report['uncovered_cards'])} uncovered cards to {output_path}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate OPTCG effect coverage report')
    parser.add_argument('--cards', '-c', default='../../simulator/backend/data/cards.json',
                       help='Path to cards.json file')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show detailed output')
    parser.add_argument('--export-csv', '-e', default='uncovered_cards.csv',
                       help='Export uncovered cards to CSV')
    parser.add_argument('--export-json', '-j', default=None,
                       help='Export full report to JSON')

    args = parser.parse_args()

    # Resolve paths relative to script location
    script_dir = Path(__file__).parent
    cards_path = script_dir / args.cards

    if not cards_path.exists():
        print(f"Error: Cards file not found at {cards_path}")
        sys.exit(1)

    print(f"Loading cards from {cards_path}...")
    cards = load_cards(str(cards_path))

    print(f"Analyzing {len(cards)} cards...")
    report = generate_report(cards)

    print_report(report, verbose=args.verbose)

    # Export CSV
    csv_path = script_dir / args.export_csv
    export_uncovered_csv(report, str(csv_path))

    # Export JSON if requested
    if args.export_json:
        json_path = script_dir / args.export_json
        # Convert defaultdicts to regular dicts for JSON serialization
        report_json = {
            'summary': report['summary'],
            'by_timing': dict(report['by_timing']),
            'by_card_type': dict(report['by_card_type']),
            'hardcoded_cards': [{'id': c['id'], 'name': c['name'], 'timings': c['timings']} for c in report['hardcoded_cards']],
            'uncovered_cards': [{'id': c['id'], 'name': c['name'], 'timings': c['timings'], 'effect': c['effect_text']} for c in report['uncovered_cards']],
        }
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report_json, f, indent=2)
        print(f"Exported full report to {json_path}")


if __name__ == '__main__':
    main()
