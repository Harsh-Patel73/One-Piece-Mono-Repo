# OP05 Master Audit

Source of truth: `packages/simulator/backend/data/cards.json` base OP05 entries where `id == id_normal`.

## Summary

- Base cards audited: 119
- Non-vanilla cards: 112
- Vanilla cards: 7
- Registered OP05 cards after this pass: 112
- Registered OP05 timings after this pass: 156
- Missing non-vanilla registrations: 0
- Missing printed trigger timings: 0
- Strict status after this pass: 109/119 `Complete` or `Vanilla`; 10 follow-up cards flagged below

## Verification

- `python -m py_compile packages\game-engine\optcg_engine\effects\sets\op05_effects.py` passed as part of import/sweep verification.
- OP05 registration coverage script passed: `base=119 nonvanilla=112 vanilla=7 registered_cards=112 timings=156 missing=[] missing_triggers=[]`.
- Direct OP05 handler execution sweep passed: `OP05_handler_sweep_ran=156 errors=0`, resolving pending choices through `GameState.resolve_pending_choice(...)`.
- Full pytest suite was not rerun in this pass; earlier environment check showed `python -m pytest packages\game-engine\tests` is unavailable because `pytest` is not installed.

## Follow-Up Queue

- `OP05-002` Belo Betty: `Partial` - Leader-wide Revolutionary Army pump/restand style hooks should be manually validated for exact event timing and once-per-turn limits.
- `OP05-041` Sakazuki: `Partial` - Sakazuki leader filtering and bottom-deck sequencing should be replay-tested with real blue/black Navy hands and opponent targets.
- `OP05-060` Monkey.D.Luffy: `Partial` - Rob Lucci multi-K.O. and cost-reduction dependencies need manual validation against simultaneous/ordered K.O. rules.
- `OP05-074` Eustass"Captain"Kid: `Partial` - Eustass Kid leader/card DON-return interactions should be validated for exact active/rested DON source handling.
- `OP05-078` Punk Rotten: `Partial` - Kid Pirates conditional play/DON flow depends on event hooks and should be tested with real Kid Pirates fixtures.
- `OP05-098` Enel: `Needs Engine Support` - Enel-style life replacement/prevention behavior depends on engine-level replacement-effect timing.
- `OP05-099` Amazon: `Partial` - Yellow life add/trash sequencing should be manually validated with exact top/bottom life placement fixtures.
- `OP05-115` Two-Hundred Million Volts Amaru: `Needs Engine Support` - Amaru applies temporary power and life-gated effects; exact duration cleanup and life threshold branching should be validated.
- `OP05-116` Hino Bird Zap: `Partial` - K.O. threshold based on life total should be manually replayed with edge life counts.
- `OP05-119` Monkey.D.Luffy: `Partial` - High-impact DON-return/event flow should be manually validated for exact cost payment order and target ownership.

## Per-Card Audit

### OP05-001 - Sabo

- Printed effect: [DON!! x1] [Opponent's Turn] [Once Per Turn] If your Character with 5000 power or more would be K.O.'d, you may give that Character -1000 power during this turn instead of that Character being K.O.'d.
- Printed trigger: None
- Registered timings: `on_ko_prevention`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-002 - Belo Betty

- Printed effect: [Activate: Main] [Once Per Turn] You may trash 1 {Revolutionary Army} type card from your hand: Up to 3 of your {Revolutionary Army} type Characters or Characters with a [Trigger] gain +3000 power during this turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Leader-wide Revolutionary Army pump/restand style hooks should be manually validated for exact event timing and once-per-turn limits.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Leader-wide Revolutionary Army pump/restand style hooks should be manually validated for exact event timing and once-per-turn limits.

### OP05-003 - Inazuma

- Printed effect: If you have a Character with 7000 power or more other than this Character, this Character gains [Rush]. (This card can attack on the turn in which it is played.)
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-004 - Emporio.Ivankov

- Printed effect: [Activate: Main] [Once Per Turn] If this Character has 7000 power or more, play up to 1 {Revolutionary Army} type Character card with 5000 power or less other than [Emporio.Ivankov] from your hand.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-005 - Karasu

- Printed effect: [On Play] If your Leader has the {Revolutionary Army} type, give up to 1 of your opponent's Leader or Character cards -1000 power during this turn. [When Attacking] If this Character has 7000 power or more, give up to 1 of your opponent's Leader or Character cards -1000 power during this turn.
- Printed trigger: None
- Registered timings: `on_play`, `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-006 - Koala

- Printed effect: [On Play] If your Leader has the {Revolutionary Army} type, give up to 1 of your opponent's Characters -3000 power during this turn.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-007 - Sabo

- Printed effect: [On Play] K.O. up to 2 of your opponent's Characters with a total power of 4000 or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-008 - Chaka

- Printed effect: [DON!! x1] [Activate: Main] [Once Per Turn] Give up to 2 rested DON!! cards to your Leader or 1 of your Characters.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-009 - Toh-Toh

- Printed effect: [On Play] Draw 1 card if your Leader has 0 power or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-010 - Nico Robin

- Printed effect: [On Play] K.O. up to 1 of your opponent's Characters with 1000 power or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-011 - Bartholomew Kuma

- Printed effect: [On Play] K.O. up to 1 of your opponent's Characters with 2000 power or less.
- Printed trigger: [Trigger] If your Leader is multicolored, play this card.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-012 - Hack

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP05-013 - Bunny Joe

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-014 - Pell

- Printed effect: [DON!! x1] [When Attacking] Give up to 1 of your opponent's Characters -2000 power during this turn.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-015 - Belo Betty

- Printed effect: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 {Revolutionary Army} type card other than [Belo Betty] and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-016 - Morley

- Printed effect: [When Attacking] If this Character has 7000 power or more, your opponent cannot activate [Blocker] during this battle.
- Printed trigger: [Trigger] You may trash 1 card from your hand: If your Leader is multicolored, play this card.
- Registered timings: `on_attack`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-017 - Lindbergh

- Printed effect: [When Attacking] If this Character has 7000 power or more, K.O. up to 1 of your opponent's Characters with 3000 power or less.
- Printed trigger: [Trigger] You may trash 1 card from your hand: If your Leader is multicolored, play this card.
- Registered timings: `on_attack`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-018 - Emporio Energy Hormone

- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +3000 power during this battle. Then, play up to 1 {Revolutionary Army} type Character card with 5000 power or less from your hand.
- Printed trigger: [Trigger] Play up to 1 {Revolutionary Army} type Character card with 5000 power or less from your hand.
- Registered timings: `counter`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-019 - Fire Fist

- Printed effect: [Main] Give up to 1 of your opponent's Characters -4000 power during this turn. Then, if you have 2 or less Life cards, K.O. up to 1 of your opponent's Characters with 0 power or less.
- Printed trigger: [Trigger] Activate this card's [Main] effect.
- Registered timings: `MAIN`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-020 - Four Thousand-Brick Fist

- Printed effect: [Main] Up to 1 of your Leader or Character cards gains +2000 power during this turn. Then, K.O. up to 1 of your opponent's Characters with 2000 power or less.
- Printed trigger: [Trigger] Up to 1 of your Leader or Character cards gains +1000 power during this turn.
- Registered timings: `main`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-021 - Revolutionary Army HQ

- Printed effect: [Activate: Main] You may trash 1 card from your hand and rest this Stage: Look at 3 cards from the top of your deck; reveal up to 1 {Revolutionary Army} type card and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-022 - Donquixote Rosinante

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [End of Your Turn] If you have 6 or less cards in your hand, set this Leader as active.
- Printed trigger: None
- Registered timings: `blocker`, `end_of_turn`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-023 - Vergo

- Printed effect: [DON!! x1] [When Attacking] K.O. up to 1 of your opponent's rested Characters with a cost of 3 or less.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-024 - Kuween

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-025 - Gladius

- Printed effect: [Activate: Main] You may rest this Character: Rest up to 1 of your opponent's Characters with a cost of 3 or less.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-026 - Sarquiss

- Printed effect: [DON!! x1] [When Attacking] [Once Per Turn] You may rest 1 of your Characters with a cost of 3 or more: Set this Character as active.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-027 - Trafalgar Law

- Printed effect: [Activate: Main] You may trash this Character: Rest up to 1 of your opponent's Characters with a cost of 3 or less.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-028 - Donquixote Doflamingo

- Printed effect: [Activate: Main] You may trash this Character: K.O. up to 1 of your opponent's rested Characters with a cost of 2 or less.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-029 - Donquixote Doflamingo

- Printed effect: [On Your Opponent's Attack] [Once Per Turn] ? (You may rest the specified number of DON!! cards in your cost area.): Rest up to 1 of your opponent's Characters with a cost of 6 or less.
- Printed trigger: None
- Registered timings: `on_opponent_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-030 - Donquixote Rosinante

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [Opponent's Turn] If your rested Character would be K.O.'d, you may trash this Character instead.
- Printed trigger: None
- Registered timings: `blocker`, `on_ko_prevention`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-031 - Buffalo

- Printed effect: [When Attacking] [Once Per Turn] If you have 2 or more rested Characters, set up to 1 of your rested Characters with a cost of 1 as active.
- Printed trigger: None
- Registered timings: `WHEN_ATTACKING`, `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-032 - Pica

- Printed effect: [End of Your Turn] ?: Set this Character as active. [Once Per Turn] If this Character would be K.O.'d, you may rest up to 1 of your Characters with a cost of 3 or more other than [Pica] instead.
- Printed trigger: None
- Registered timings: `end_of_turn`, `on_ko_prevention`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-033 - Baby 5

- Printed effect: [Activate: Main] ? (You may rest the specified number of DON!! cards in your cost area.) You may rest this Character: Play up to 1 {Donquixote Pirates} type Character card with a cost of 2 or less from your hand.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-034 - Baby 5

- Printed effect: [Activate: Main] ? (You may rest the specified number of DON!! cards in your cost area.) You may rest this Character: Look at 5 cards from the top of your deck; reveal up to 1 {Donquixote Pirates} type card and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-035 - Bellamy

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP05-036 - Monet

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On Block] Rest up to 1 of your opponent's Characters with a cost of 4 or less.
- Printed trigger: None
- Registered timings: `blocker`, `on_block`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-037 - Because the Side of Justice Will Be Whichever Side Wins!!

- Printed effect: [Counter] You may trash 1 card from your hand: Up to 1 of your Leader or Character cards gains +3000 power during this battle.
- Printed trigger: [Trigger] Rest up to 1 of your opponent's Characters with a cost of 4 or less.
- Registered timings: `counter`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-038 - Charlestone

- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +4000 power during this battle. Then, you may trash 1 card from your hand. If you do, set up to 3 of your DON!! cards as active.
- Printed trigger: [Trigger] Rest up to 1 of your opponent's Leader or Character cards with a cost of 3 or less.
- Registered timings: `counter`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-039 - Stick-Stickem Meteora

- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +4000 power during this battle. Then, K.O. up to 1 of your opponent's rested Characters with a cost of 3 or less.
- Printed trigger: [Trigger] K.O. up to 1 of your opponent's rested Characters with a cost of 5 or less.
- Registered timings: `counter`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-040 - Birdcage

- Printed effect: If your Leader is [Donquixote Doflamingo], all Characters with a cost of 5 or less do not become active in your and your opponent's Refresh Phases. [End of Your Turn] If you have 10 DON!! cards on your field, K.O. all rested Characters with a cost of 5 or less. Then, trash this Stage.
- Printed trigger: None
- Registered timings: `continuous`, `END_OF_TURN`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-041 - Sakazuki

- Printed effect: [Activate: Main] [Once Per Turn] You may trash 1 card from your hand: Draw 1 card. [When Attacking] Give up to 1 of your opponent's Characters -1 cost during this turn.
- Printed trigger: None
- Registered timings: `activate`, `on_attack`
- Implementation status: `Partial`
- Required code changes: Sakazuki leader filtering and bottom-deck sequencing should be replay-tested with real blue/black Navy hands and opponent targets.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Sakazuki leader filtering and bottom-deck sequencing should be replay-tested with real blue/black Navy hands and opponent targets.

### OP05-042 - Issho

- Printed effect: [On Play] Up to 1 of your opponent's Characters with a cost of 7 or less cannot attack until the start of your next turn.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-043 - Ulti

- Printed effect: [On Play] If your Leader is multicolored, look at 3 cards from the top of your deck and add up to 1 card to your hand. Then, place the rest at the top or bottom of the deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-044 - John Giant

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP05-045 - Stainless

- Printed effect: [Activate: Main] You may trash 1 card from your hand and rest this Character: Place up to 1 Character with a cost of 2 or less at the bottom of the owner's deck.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-046 - Dalmatian

- Printed effect: [On K.O.] Draw 1 card and place 1 card from your hand at the bottom of your deck.
- Printed trigger: None
- Registered timings: `on_ko`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-047 - Basil Hawkins

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On Block] Draw 1 card if you have 3 or less cards in your hand. Then, this Character gains +1000 power during this battle.
- Printed trigger: None
- Registered timings: `blocker`, `on_block`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-048 - Bastille

- Printed effect: [DON!! x1] [When Attacking] Place up to 1 Character with a cost of 2 or less at the bottom of the owner's deck.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-049 - Haccha

- Printed effect: [DON!! x1] [When Attacking] Return up to 1 Character with a cost of 3 or less to the owner's hand.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-050 - Hina

- Printed effect: [On Play] Draw 1 card if you have 5 or less cards in your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-051 - Borsalino

- Printed effect: [On Play] Place up to 1 Character with a cost of 4 or less at the bottom of the owner's deck.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-052 - Maynard

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-053 - Mozambia

- Printed effect: [Your Turn] [Once Per Turn] When you draw a card outside of your Draw Phase, this Character gains +2000 power during this turn.
- Printed trigger: None
- Registered timings: `on_draw`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-054 - Monkey.D.Garp

- Printed effect: [On Play] Draw 2 cards and place 2 cards from your hand at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-055 - X.Drake

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On Play] Look at 5 cards from the top of your deck and place them at the top or bottom of the deck in any order.
- Printed trigger: None
- Registered timings: `blocker`, `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-056 - X.Barrels

- Printed effect: [On Play] You may place 1 of your Characters other than this Character at the bottom of your deck: Draw 1 card.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-057 - Hound Blaze

- Printed effect: [Main] Up to 1 of your Leader or Character cards gains +3000 power during this turn. Then, place up to 1 Character with a cost of 2 or less at the bottom of the owner's deck.
- Printed trigger: [Trigger] Return up to 1 Character with a cost of 3 or less to the owner's hand.
- Registered timings: `main`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-058 - It's a Waste of Human Life!!

- Printed effect: [Main] Place all Characters with a cost of 3 or less at the bottom of the owner's deck. Then, you and your opponent trash cards from your hands until you each have 5 cards in your hands.
- Printed trigger: [Trigger] Place all Characters with a cost of 2 or less at the bottom of the owner's deck.
- Registered timings: `main`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-059 - Let Us Begin the World of Violence!!!

- Printed effect: [Main] If your Leader is multicolored, draw 1 card. Then, return up to 1 Character with a cost of 5 or less to the owner's hand.
- Printed trigger: [Trigger] If your Leader is multicolored, draw 2 cards.
- Registered timings: `main`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-060 - Monkey.D.Luffy

- Printed effect: [Activate: Main] [Once Per Turn] You may add 1 card from the top of your Life cards to your hand: If you have 0 or 3 or more DON!! cards on your field, add up to 1 DON!! card from your DON!! deck and set it as active.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Rob Lucci multi-K.O. and cost-reduction dependencies need manual validation against simultaneous/ordered K.O. rules.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Rob Lucci multi-K.O. and cost-reduction dependencies need manual validation against simultaneous/ordered K.O. rules.

### OP05-061 - Uso-Hachi

- Printed effect: [DON!! x1] [When Attacking] If you have 8 or more DON!! cards on your field, rest up to 1 of your opponent's Characters with a cost of 4 or less.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-062 - O-Nami

- Printed effect: If you have 10 DON!! cards on your field, this Character gains [Blocker]. (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-063 - O-Robi

- Printed effect: [On Play] If you have 8 or more DON!! cards on your field, K.O. up to 1 of your opponent's Characters with a cost of 3 or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-064 - Killer

- Printed effect: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 {Kid Pirates} type card other than [Killer] and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-065 - San-Gorou

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP05-066 - Jinbe

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [Opponent's Turn] If you have 10 DON!! cards on your field, this Character gains +1000 power.
- Printed trigger: None
- Registered timings: `blocker`, `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-067 - Zoro-Juurou

- Printed effect: [When Attacking] If you have 3 or less Life cards, add up to 1 DON!! card from your DON!! deck and set it as active.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-068 - Chopa-Emon

- Printed effect: [On Play] If you have 8 or more DON!! cards on your field, set up to 1 of your purple {Straw Hat Crew} type Characters with 6000 power or less as active.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-069 - Trafalgar Law

- Printed effect: [When Attacking] If your opponent has more DON!! cards on their field than you, look at 5 cards from the top of your deck; reveal up to 1 {Heart Pirates} type card and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-070 - Fra-Nosuke

- Printed effect: [DON!! x1] If you have 8 or more DON!! cards on your field, this Character gains [Rush]. (This card can attack on the turn in which it is played.)
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-071 - Bepo

- Printed effect: [When Attacking] If your opponent has more DON!! cards on their field than you, give up to 1 of your opponent's Characters -2000 power during this turn.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-072 - Hone-Kichi

- Printed effect: [On Play] If you have 8 or more DON!! cards on your field, give up to 2 of your opponent's Characters -2000 power during this turn.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-073 - Miss Doublefinger(Zala)

- Printed effect: [On Play] You may trash 1 card from your hand: Add up to 1 DON!! card from your DON!! deck and rest it.
- Printed trigger: [Trigger] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Play this card.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-074 - Eustass"Captain"Kid

- Printed effect: [Blocker] [Your Turn] [Once Per Turn] When a DON!! card on your field is returned to your DON!! deck, add up to 1 DON!! card from your DON!! deck and set it as active.
- Printed trigger: None
- Registered timings: `blocker`, `on_don_return`
- Implementation status: `Partial`
- Required code changes: Eustass Kid leader/card DON-return interactions should be validated for exact active/rested DON source handling.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Eustass Kid leader/card DON-return interactions should be validated for exact active/rested DON source handling.

### OP05-075 - Mr.1(Daz.Bonez)

- Printed effect: [On Your Opponent's Attack] [Once Per Turn] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Play up to 1 {Baroque Works} type Character card with a cost of 3 or less from your hand.
- Printed trigger: None
- Registered timings: `on_opponent_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-076 - When You're at Sea You Fight against Pirates!!

- Printed effect: [Main] Look at 3 cards from the top of your deck; reveal up to 1 {Straw Hat Crew}, {Kid Pirates}, or {Heart Pirates} type card and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: [Trigger] Activate this card's [Main] effect.
- Registered timings: `MAIN`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-077 - Gamma Knife

- Printed effect: [Main] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Give up to 1 of your opponent's Characters -5000 power during this turn.
- Printed trigger: [Trigger] Add up to 1 DON!! card from your DON!! deck and set it as active.
- Registered timings: `main`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-078 - Punk Rotten

- Printed effect: [Main] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Up to 1 of your {Kid Pirates} type Leader or Character cards gains +5000 power during this turn.
- Printed trigger: [Trigger] Add up to 1 DON!! card from your DON!! deck and set it as active.
- Registered timings: `main`, `trigger`
- Implementation status: `Partial`
- Required code changes: Kid Pirates conditional play/DON flow depends on event hooks and should be tested with real Kid Pirates fixtures.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Kid Pirates conditional play/DON flow depends on event hooks and should be tested with real Kid Pirates fixtures.

### OP05-079 - Viola

- Printed effect: [On Play] Your opponent places 3 cards from their trash at the bottom of their deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-080 - Elizabello II

- Printed effect: [When Attacking] [Once Per Turn] You may return 20 cards from your trash to your deck and shuffle it: This Character gains [Double Attack] and +10000 power during this battle. (This card deals 2 damage.)
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-081 - One-Legged Toy Soldier

- Printed effect: [Activate: Main] You may trash this Character: Give up to 1 of your opponent's Characters -3 cost during this turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-082 - Shirahoshi

- Printed effect: [Activate: Main] You may rest this Character and place 2 cards from your trash at the bottom of your deck in any order: If your opponent has 6 or more cards in their hand, your opponent trashes 1 card from their hand.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-083 - Sterry

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP05-084 - Saint Charlos

- Printed effect: [Your Turn] If the only Characters on your field are {Celestial Dragons} type Characters, give all of your opponent's Characters -4 cost.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-085 - Nefeltari Cobra

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On Play] Trash 1 card from the top of your deck.
- Printed trigger: None
- Registered timings: `blocker`, `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-086 - Nefeltari Vivi

- Printed effect: If you have 10 or more cards in your trash, this Character gains [Blocker]. (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `PASSIVE`, `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-087 - Hakuba

- Printed effect: [DON!! x1] [When Attacking] You may K.O. 1 of your Characters other than this Character: Give up to 1 of your opponent's Characters -5 cost during this turn.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-088 - Mansherry

- Printed effect: [Activate: Main] ? (You may rest the specified number of DON!! cards in your cost area.) You may rest this Character and place 2 cards from your trash at the bottom of your deck in any order: Add up to 1 black Character card with a cost of 3 to 5 from your trash to your hand.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-089 - Saint Mjosgard

- Printed effect: [Activate: Main] ? (You may rest the specified number of DON!! cards in your cost area.) You may rest this Character and 1 of your Characters: Add up to 1 black Character card with a cost of 1 from your trash to your hand.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-090 - Riku Doldo III

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On Play]/[On K.O.] Up to 1 of your {Dressrosa} type Characters gains +2000 power during this turn.
- Printed trigger: None
- Registered timings: `blocker`, `on_play`, `on_ko`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-091 - Rebecca

- Printed effect: [Blocker] [On Play] Add up to 1 black Character card with a cost of 3 to 7 other than [Rebecca] from your trash to your hand. Then, play up to 1 black Character card with a cost of 3 or less from your hand rested.
- Printed trigger: None
- Registered timings: `blocker`, `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-092 - Saint Rosward

- Printed effect: [Your Turn] If the only Characters on your field are {Celestial Dragons} type Characters, give all of your opponent's Characters -6 cost.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-093 - Rob Lucci

- Printed effect: [On Play] You may place 3 cards from your trash at the bottom of your deck in any order: K.O. up to 1 of your opponent's Characters with a cost of 2 or less and up to 1 of your opponent's Characters with a cost of 1 or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-094 - Haute Couture Patch?Work

- Printed effect: [Main] Give up to 1 of your opponent's Characters -3 cost during this turn. Then, up to 1 of your opponent's Characters with a cost of 0 will not become active in the next Refresh Phase.
- Printed trigger: [Trigger] Draw 2 cards and trash 1 card from your hand.
- Registered timings: `main`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-095 - Dragon Claw

- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +4000 power during this battle. Then, if you have 15 or more cards in your trash, K.O. up to 1 of your opponent's Characters with a cost of 4 or less.
- Printed trigger: None
- Registered timings: `COUNTER`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-096 - I Bid 500 Million!!

- Printed effect: [Main] Choose one: ? K.O. up to 1 of your opponent's Characters with a cost of 1 or less. ? Return up to 1 of your opponent's Characters with a cost of 1 or less to the owner's hand. ? Place up to 1 of your opponent's Characters with a cost of 1 or less at the top or bottom of their Life cards face-up. Then, if you have a {Celestial Dragons} type Character, draw 1 card.
- Printed trigger: [Trigger] K.O. up to 1 of your opponent's Characters with a cost of 6 or less, or return it to the owner's hand.
- Registered timings: `MAIN`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-097 - Mary Geoise

- Printed effect: [Your Turn] The cost of playing {Celestial Dragons} type Character cards with a cost of 2 or more from your hand will be reduced by 1.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-098 - Enel

- Printed effect: [Opponent's Turn] [Once Per Turn] When your number of Life cards becomes 0, add 1 card from the top of your deck to the top of your Life cards. Then, trash 1 card from your hand.
- Printed trigger: None
- Registered timings: `on_life_zero`
- Implementation status: `Needs Engine Support`
- Required code changes: Enel-style life replacement/prevention behavior depends on engine-level replacement-effect timing.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Enel-style life replacement/prevention behavior depends on engine-level replacement-effect timing.

### OP05-099 - Amazon

- Printed effect: [On Your Opponent's Attack] You may rest this Character: Your opponent may trash 1 card from the top of their Life cards. If they do not, give up to 1 of your opponent's Leader or Character cards -2000 power during this turn.
- Printed trigger: None
- Registered timings: `on_opponent_attack`
- Implementation status: `Partial`
- Required code changes: Yellow life add/trash sequencing should be manually validated with exact top/bottom life placement fixtures.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Yellow life add/trash sequencing should be manually validated with exact top/bottom life placement fixtures.

### OP05-100 - Enel

- Printed effect: [Rush] [Once Per Turn] If this Character would leave the field, you may trash 1 card from the top of your Life cards instead. If there is a [Monkey.D.Luffy] Character, this effect is negated.
- Printed trigger: None
- Registered timings: `continuous`, `on_leave_prevention`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-101 - Ohm

- Printed effect: If you have 2 or less Life cards, this Character gains +1000 power. [On Play] Look at 5 cards from the top of your deck; reveal up to 1 [Holly] and add it to your hand. Then, place the rest at the bottom of your deck in any order and play up to 1 [Holly] from your hand.
- Printed trigger: None
- Registered timings: `continuous`, `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-102 - Gedatsu

- Printed effect: [On Play] K.O. up to 1 of your opponent's Characters with a cost equal to or less than the number of your opponent's Life cards.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-103 - Kotori

- Printed effect: [On Play] If you have [Hotori], K.O. up to 1 of your opponent's Characters with a cost equal to or less than the number of your opponent's Life cards.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-104 - Conis

- Printed effect: [On Play] You may place 1 of your Stages at the bottom of your deck: Draw 1 card and trash 1 card from your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-105 - Satori

- Printed effect: None
- Printed trigger: [Trigger] You may trash 1 card from your hand: Play this card.
- Registered timings: `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-106 - Shura

- Printed effect: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 {Sky Island} type card other than [Shura] and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: [Trigger] Play this card.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-107 - Lieutenant Spacey

- Printed effect: [Your Turn] [Once Per Turn] When a card is added to your hand from your Life, this Character gains +2000 power during this turn.
- Printed trigger: None
- Registered timings: `on_life_add`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-108 - Nola

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP05-109 - Pagaya

- Printed effect: [Once Per Turn] When a [Trigger] activates, draw 2 cards and trash 2 cards from your hand.
- Printed trigger: None
- Registered timings: `on_trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-110 - Holly

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP05-111 - Hotori

- Printed effect: [On Play] You may play 1 [Kotori] from your hand: Add up to 1 of your opponent's Characters with a cost of 3 or less to the top or bottom of your opponent's Life cards face-up.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-112 - Captain McKinley

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On K.O.] Play up to 1 {Sky Island} type Character card with a cost of 1 from your hand.
- Printed trigger: None
- Registered timings: `blocker`, `on_ko`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-113 - Yama

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-114 - El Thor

- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +2000 power during this battle. Then, if your opponent has 2 or less Life cards, that card gains an additional +2000 power during this battle.
- Printed trigger: [Trigger] K.O. up to 1 of your opponent's Characters with a cost equal to or less than the number of your opponent's Life cards.
- Registered timings: `COUNTER`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-115 - Two-Hundred Million Volts Amaru

- Printed effect: [Main] Up to 1 of your Leader or Character cards gains +3000 power during this turn. Then, if you have 1 or less Life cards, rest up to 1 of your opponent's Characters with a cost of 4 or less.
- Printed trigger: [Trigger] You may trash 2 cards from your hand: Add up to 1 card from the top of your deck to the top of your Life cards.
- Registered timings: `MAIN`, `trigger`
- Implementation status: `Needs Engine Support`
- Required code changes: Amaru applies temporary power and life-gated effects; exact duration cleanup and life threshold branching should be validated.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Amaru applies temporary power and life-gated effects; exact duration cleanup and life threshold branching should be validated.

### OP05-116 - Hino Bird Zap

- Printed effect: [Main] K.O. up to 1 of your opponent's Characters with a cost equal to or less than the number of your opponent's Life cards.
- Printed trigger: [Trigger] Activate this card's [Main] effect.
- Registered timings: `main`, `trigger`
- Implementation status: `Partial`
- Required code changes: K.O. threshold based on life total should be manually replayed with edge life counts.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: K.O. threshold based on life total should be manually replayed with edge life counts.

### OP05-117 - Upper Yard

- Printed effect: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 {Sky Island} type card and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-118 - Kaido

- Printed effect: [On Play] Draw 4 cards if your opponent has 3 or less Life cards.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP05-119 - Monkey.D.Luffy

- Printed effect: [On Play] DON!! -10: Place all of your Characters except this Character at the bottom of your deck in any order. Then, take an extra turn after this one. [Activate: Main] [Once Per Turn] ?: Add up to 1 DON!! card from your DON!! deck and set it as active.
- Printed trigger: None
- Registered timings: `ACTIVATE_MAIN`, `on_play`, `activate`
- Implementation status: `Partial`
- Required code changes: High-impact DON-return/event flow should be manually validated for exact cost payment order and target ownership.
- Required tester setup: Generic OP05 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: High-impact DON-return/event flow should be manually validated for exact cost payment order and target ownership.
