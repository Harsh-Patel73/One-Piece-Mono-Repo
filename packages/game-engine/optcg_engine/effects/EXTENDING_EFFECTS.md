# Extending the Effect System

This guide explains how to add support for new card effects when adding cards to the database.

## Architecture Overview

The effect system has three main components:

1. **Parser** (`parser.py`) - Converts card effect text to structured `Effect` objects
2. **Effects** (`effects.py`) - Data structures defining effect types and parameters
3. **Resolver** (`resolver.py`) - Executes effects against the game state

## Adding Support for a New Effect Type

### Step 1: Check if Effect Type Exists

Look in `effects.py` at the `EffectType` enum:

```python
class EffectType(Enum):
    DRAW = auto()           # Draw cards
    KO = auto()             # K.O. a character
    POWER_BOOST = auto()    # +X000 power
    # ... etc
```

If your effect type doesn't exist, add it:

```python
    YOUR_NEW_TYPE = auto()  # Description of what it does
```

### Step 2: Add Parser Pattern

In `parser.py`, add a regex pattern to `_compile_patterns()`:

```python
self.effect_patterns = [
    # ... existing patterns ...

    # Your new pattern
    (r'your\s+regex\s+pattern\s+(\d+)', self._parse_your_effect),
]
```

Regex tips:
- Use `(\d+)` to capture numbers (card count, power amount, etc.)
- Use `(?:...)` for non-capturing groups
- Use `\s+` for whitespace, `\s*` for optional whitespace
- Use `(?:your\s+)?` for optional words
- Test patterns at regex101.com with IGNORECASE flag

### Step 3: Add Parser Method

Add a method to parse the matched effect:

```python
def _parse_your_effect(self, match: re.Match, full_text: str) -> Effect:
    """Parse your new effect."""
    count = int(match.group(1))  # Get captured number
    target_type = self._determine_target_type(full_text)
    restriction = self._parse_target_restriction(full_text)

    return Effect(
        effect_type=EffectType.YOUR_NEW_TYPE,
        timing=EffectTiming.CONTINUOUS,  # Will be set by caller
        target_type=target_type,
        target_count=count,
        target_restriction=restriction,
    )
```

### Step 4: Add Resolver Handler

In `resolver.py`, register the handler in `__init__`:

```python
self.handlers = {
    # ... existing handlers ...
    EffectType.YOUR_NEW_TYPE: self._resolve_your_effect,
}
```

Then add the handler method:

```python
def _resolve_your_effect(self, effect: Effect, context: EffectContext) -> EffectResult:
    """Handle your new effect."""
    targets = context.targets
    affected = 0

    for target in targets:
        # Do something with each target
        # Access game state via context.game_state
        # Access players via context.source_player, context.opponent
        affected += 1
        print(f"{target.name} was affected")

    return EffectResult(
        success=affected > 0,
        message=f"Affected {affected} card(s)",
        state_changed=affected > 0,
        targets_affected=targets[:affected],
    )
```

## Common Patterns Reference

### Card Targeting
```python
# Patterns for targeting
"your Character"           -> TargetType.YOUR_CHARACTER
"opponent's Character"     -> TargetType.OPPONENT_CHARACTER
"your Leader"              -> TargetType.YOUR_LEADER
"your hand"                -> TargetType.YOUR_HAND
"your trash"               -> TargetType.YOUR_TRASH
```

### Restrictions
```python
# Cost restrictions
"cost 3 or less"          -> target_restriction.cost_max = 3
"cost 5 or more"          -> target_restriction.cost_min = 5

# Power restrictions
"3000 or less power"      -> target_restriction.power_max = 3000

# Type restrictions
"{Straw Hat Crew}"        -> target_restriction.types = ["Straw Hat Crew"]
```

### Timing Keywords
```python
"[On Play]"               -> EffectTiming.ON_PLAY
"[Activate: Main]"        -> EffectTiming.MAIN
"[When Attacking]"        -> EffectTiming.WHEN_ATTACKING
"[Counter]"               -> EffectTiming.COUNTER
"[Trigger]"               -> EffectTiming.TRIGGER
"[DON!! x2]"              -> EffectTiming.DON_CONDITION
```

## Testing New Effects

After adding a new effect, test it:

```python
from effects.parser import parse_effect
from effects.effects import EffectTiming, EffectType

# Test parsing
effect_text = "[On Play] Your new effect text here"
effects = parse_effect(effect_text)

for e in effects:
    print(f"Type: {e.effect_type}")
    print(f"Timing: {e.timing}")
    print(f"Value: {e.value}")
    print(f"Target: {e.target_type}")
```

## Current Coverage

As of the latest update:
- **On Play Effects**: ~48% parsed
- **Activate Main Effects**: ~65% parsed

Unparsed effects (NEGATE placeholder) typically involve:
1. Complex conditional logic ("If you have X Life cards...")
2. Look/reveal with selection ("Look at X, reveal up to 1 matching Y...")
3. Specific card name targeting ("Play up to 1 [Card Name]")
4. Multi-step effects with costs

## Future Improvements

For better coverage, consider:
1. Adding more specific patterns for common card archetypes
2. Implementing a condition parser for "If..." clauses
3. Adding support for card name references [Card Name]
4. Implementing look/reveal with filter and selection
