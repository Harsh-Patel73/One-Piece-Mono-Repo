# Effects module - Card effect parsing and resolution

from .effects import (
    Effect, EffectType, EffectTiming, TargetType, Duration,
    TargetRestriction, EffectCost, ParsedCard
)
from .parser import EffectParser, parse_effect, get_parser
from .resolver import EffectResolver, resolve_effect, get_resolver, EffectContext, EffectResult
from .tokenizer import Tokenizer, extract_keywords
from .manager import (
    CardEffectManager, get_effect_manager, parse_card_effects,
    get_effects_by_timing, check_don_requirement, clear_effect_cache
)
from .hardcoded import (
    has_hardcoded_effect, execute_hardcoded_effect, register_effect,
    get_all_hardcoded_cards, get_hardcoded_effect_count
)

__all__ = [
    # Effect classes
    'Effect', 'EffectType', 'EffectTiming', 'TargetType', 'Duration',
    'TargetRestriction', 'EffectCost', 'ParsedCard',
    # Parser
    'EffectParser', 'parse_effect', 'get_parser',
    # Resolver
    'EffectResolver', 'resolve_effect', 'get_resolver', 'EffectContext', 'EffectResult',
    # Manager
    'CardEffectManager', 'get_effect_manager', 'parse_card_effects',
    'get_effects_by_timing', 'check_don_requirement', 'clear_effect_cache',
    # Tokenizer
    'Tokenizer', 'extract_keywords',
    # Hardcoded effects
    'has_hardcoded_effect', 'execute_hardcoded_effect', 'register_effect',
    'get_all_hardcoded_cards', 'get_hardcoded_effect_count',
]
