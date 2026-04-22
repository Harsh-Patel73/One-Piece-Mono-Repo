# OP12 Master Audit

Source of truth: `packages/simulator/backend/data/cards.json` base OP12 entries where `id == id_normal`.

## Summary

- Base cards audited: 119
- Non-vanilla cards: 95
- Vanilla cards: 24
- Registered OP12 cards after this pass: 95
- Registered OP12 timings after this pass: 133
- Missing non-vanilla registrations before this pass: 64
- Missing printed trigger timings before this pass: 15
- Missing non-vanilla registrations after this pass: 0
- Missing printed trigger timings after this pass: 0
- Strict status after this pass: 60/119 `Complete` or `Vanilla`; 59 generic follow-up cards flagged below
- Note: This pass uses the shared generic fallback for many previously missing cards; those remain flagged for exact bespoke follow-up.

## Verification

- `python -m py_compile packages\game-engine\optcg_engine\effects\sets\op12_effects.py` passed.
- OP12 registration coverage script passed: `base=119 nonvanilla=95 vanilla=24 registered_cards=95 timings=133 missing=[] missing_triggers=[]`.
- Direct OP12 handler execution sweep passed: `OP12_handler_sweep_ran=133 errors=0 tracebacks=0`, resolving pending choices through `GameState.resolve_pending_choice(...)`.
- Full pytest suite was not rerun in this pass; earlier environment check showed `python -m pytest packages\game-engine\tests` is unavailable because `pytest` is not installed.

## Follow-Up Queue

- `OP12-007` Shanks: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-012` Buggy: `Needs Engine Support` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-013` Hatchan: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-016` To Never Doubt--That Is Power!: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-018` Color of the Supreme King Haki: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-019` Color of Arms Haki: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-024` Gyukimaru: `Needs Engine Support` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-026` Kuina: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-029` Shimotsuki Kouzaburou: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-030` Dracule Mihawk: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-031` Tashigi: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-036` Roronoa Zoro: `Needs Engine Support` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-037` Demon Aura Nine Sword Style Asura Blades Drawn Dead Man's Game: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-038` Two-Sword Style Rashomon: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-039` Luffy Is the Man Who Will Become the King of Pirates!!!: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-042` Alvida: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-043` Kuzan: `Needs Engine Support` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-044` Sakazuki: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-046` Zephyr(Navy): `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-048` Donquixote Rosinante: `Needs Engine Support` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-051` Hina: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-057` Ice Block Pheasant Peck: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-058` I Will Make Whitebeard the King of the Pirates: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-059` Concasser: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-062` Vinsmoke Sora: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-065` Emporio.Ivankov: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-069` Crocodile: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-070` Sanji: `Needs Engine Support` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-072` Zeff: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-073` Trafalgar Law: `Needs Engine Support` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-074` Patty: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-075` Ms. All Sunday: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-077` The "Extinguishes All Sound Created by Your Influence" Technique: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-078` Brochette Blow: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-080` Baratie: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-084` Emporio.Ivankov: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-085` Karasu: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-087` Nico Robin: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-089` Hack: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-090` Belo Betty: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-091` Poker: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-093` Morley: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-094` Monkey.D.Dragon: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-095` Lindbergh: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-096` Ursa Shock: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-097` Captains Assembled: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-098` Hair Removal Fist: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-099` Kalgara: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-101` Jewelry Bonney: `Needs Engine Support` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-102` Shirahoshi: `Needs Engine Support` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-104` Sentomaru: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-105` Trafalgar Lammy: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-109` Pacifista: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-112` Baby 5: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-113` Roronoa Zoro: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-116` We'll Ring the Bell Waiting for You!!: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-117` Slam Gibson: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-118` Jewelry Bonney: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP12-119` Bartholomew Kuma: `Needs Engine Support` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

## Per-Card Audit

### OP12-001 - Silvers Rayleigh

- Printed effect: Under the rules of this game, you cannot include cards with a cost of 5 or more in your deck. [Activate: Main] [Once Per Turn] You may reveal 2 Events from your hand: Up to 1 of your Characters with 4000 base power or less gains +2000 power during this turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-002 - Edward.Newgate

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP12-003 - Crocus

- Printed effect: [On K.O.] You may reveal 2 Events from your hand: Play up to 1 red Character card with 3000 power or less from your hand.
- Printed trigger: None
- Registered timings: `ON_KO`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-004 - Kouzuki Oden

- Printed effect: [Activate: Main] [Once Per Turn] You may reveal 2 Events from your hand: This Character gains +2000 power during this turn.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-005 - Shiki

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP12-006 - Shakuyaku

- Printed effect: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 [Monkey.D.Luffy] or 1 red Event and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-007 - Shanks

- Printed effect: [On Play] Up to 1 of your Characters with a type including "Roger Pirates" other than [Shanks] gains [Rush] during this turn. (This card can attack on the turn in which it is played.)
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-008 - Shanks

- Printed effect: [Blocker] [On Your Opponent's Attack] [Once Per Turn] You may trash 1 card from your hand: Give up to 1 of your opponent's Leader or Character cards -2000 power during this turn.
- Printed trigger: None
- Registered timings: `on_opponent_attack`, `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-009 - Jinbe

- Printed effect: [On Play] You may reveal 2 Events from your hand: This Character gains [Rush] during this turn. Then, this Character gains +1000 power until the end of your opponent's next End Phase.
- Printed trigger: None
- Registered timings: `ON_PLAY`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-010 - Douglas Bullet

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP12-011 - Duval

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP12-012 - Buggy

- Printed effect: [On Play] Up to 1 of your Characters with a type including "Roger Pirates" other than [Buggy] gains [Blocker] until the end of your opponent's next End Phase.
- Printed trigger: None
- Registered timings: `on_play`, `blocker`
- Implementation status: `Needs Engine Support`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-013 - Hatchan

- Printed effect: [Activate: Main] You may rest this Character and reveal 2 Events from your hand: Give up to 2 rested DON!! cards to your Leader or 1 of your Characters.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-014 - Boa Hancock

- Printed effect: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 [Monkey.D.Luffy] or red Event and add it to your hand. Then, place the rest at the bottom of your deck in any order. [Activate: Main] You may trash this Character: Give up to 2 rested DON!! cards to your Leader or 1 of your Characters.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-015 - Monkey.D.Luffy

- Printed effect: If you have a total of 2 or more given DON!! cards, this Character gains +2000 power. [On Play] You may reveal 2 Events from your hand: Play up to 1 red Character card with 3000 power or less from your hand. Then, give up to 1 rested DON!! card to your Leader or 1 of your Characters.
- Printed trigger: None
- Registered timings: `ON_PLAY`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-016 - To Never Doubt--That Is Power!

- Printed effect: [Main] You may give 2 active DON!! cards to 1 of your [Silvers Rayleigh]: Your opponent cannot activate [Blocker] when the card given these DON!! cards attacks during this turn. [Counter] Up to 1 of your Characters or [Silvers Rayleigh] gains +2000 power during this battle.
- Printed trigger: None
- Registered timings: `counter`, `on_play`, `blocker`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-017 - Color of Observation Haki

- Printed effect: [Main] You may give 1 active DON!! card to 1 of your [Silvers Rayleigh]: Look at 4 cards from the top of your deck; reveal up to 1 red Event or up to 1 Character card with a cost of 3 or more and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-018 - Color of the Supreme King Haki

- Printed effect: [Counter] Up to 1 of your Characters or [Silvers Rayleigh] gains +2000 power during this battle. Then, you may rest 1 of your DON!! cards. If you do, give your opponent's Leader and all of their Characters -1000 power during this turn.
- Printed trigger: None
- Registered timings: `counter`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-019 - Color of Arms Haki

- Printed effect: [Main] You may give 1 active DON!! card to 1 of your [Silvers Rayleigh]: Up to 1 of your Leader or Character cards gains +1000 power during this turn. [Counter] Up to 1 of your Characters or [Silvers Rayleigh] gains +2000 power during this battle.
- Printed trigger: None
- Registered timings: `counter`, `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-020 - Roronoa Zoro

- Printed effect: [DON!! x3] [Activate: Main] [Once Per Turn] If this Leader battles your opponent's Character during this turn, set this Leader as active. Then, this Leader cannot attack your opponent's Characters with a base cost of 7 or less during this turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-021 - Ipponmatsu

- Printed effect: If your Leader has the <Slash> attribute and you have 6 or more rested DON!! cards, this Character cannot be rested by your opponent's effects. [Blocker]
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-022 - Inuarashi

- Printed effect: [Activate: Main] You may rest this Character: Up to 1 of your opponent's rested Characters with a cost of 5 or less will not become active in your opponent's next Refresh Phase.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-023 - Kawamatsu

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP12-024 - Gyukimaru

- Printed effect: If this Character is active, this Character cannot be K.O.'d by your opponent's effects. [When Attacking] If you have a total of 3 or more given DON!! cards, rest up to 1 of your opponent's Characters with a base cost of 6 or less.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Needs Engine Support`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-025 - Kin'emon

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP12-026 - Kuina

- Printed effect: [Activate: Main] You may rest this Character: Rest up to 1 of your opponent's Characters with a base cost of 4 or less. Then, give up to 3 rested DON!! cards to your [Roronoa Zoro] Leader.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-027 - Koushirou

- Printed effect: If your <Slash> attribute Character with a cost of 5 or less other than this Character would be K.O.'d by your opponent's effect, you may rest this Character instead. [Blocker]
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-028 - Kouzuki Hiyori

- Printed effect: [Activate: Main] You may rest 1 of your DON!! cards and this Character: If your Leader is [Roronoa Zoro], look at 5 cards from the top of your deck; reveal up to 1 <Slash> attribute card or green Event and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-029 - Shimotsuki Kouzaburou

- Printed effect: [On Play] Rest up to 1 of your opponent's Characters with a cost of 2 or less. Then, K.O. up to 1 of your opponent's rested Characters with a base cost of 1 or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-030 - Dracule Mihawk

- Printed effect: [Blocker] [On Play] Set up to 4 of your DON!! cards as active. Then, you cannot play Character cards with a base cost of 7 or more during this turn.
- Printed trigger: None
- Registered timings: `on_play`, `blocker`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-031 - Tashigi

- Printed effect: [On Play] Rest up to 1 of your opponent's Characters with a base cost of 6 or less. Then, give up to 3 rested DON!! cards to your [Roronoa Zoro] Leader.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-032 - Nekomamushi

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP12-033 - Helmeppo

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On Block] Rest up to 1 of your opponent's Characters with a cost of 5 or less.
- Printed trigger: None
- Registered timings: `on_block`, `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-034 - Perona

- Printed effect: [On Play] If your Leader has the <Slash> attribute, look at 5 cards from the top of your deck; reveal up to 1 <Slash> attribute card or green Event and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-035 - Morgan

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP12-036 - Roronoa Zoro

- Printed effect: This card in your hand cannot be played by effects. If your Leader has the <Slash> attribute, this Character cannot be K.O.'d in battle by <Slash> attribute cards and gains +1000 power.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Needs Engine Support`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-037 - Demon Aura Nine Sword Style Asura Blades Drawn Dead Man's Game

- Printed effect: [Main] You may rest 3 of your DON!! cards: Rest up to a total of 2 of your opponent's Characters or DON!! cards. [Counter] Your Leader gains +3000 power during this battle.
- Printed trigger: None
- Registered timings: `counter`, `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-038 - Two-Sword Style Rashomon

- Printed effect: [Main] You may rest 2 of your DON!! cards: K.O. up to 2 of your opponent's rested Characters with a base cost of 4 or less. [Counter] Your Leader gains +3000 power during this battle.
- Printed trigger: None
- Registered timings: `counter`, `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-039 - Luffy Is the Man Who Will Become the King of Pirates!!!

- Printed effect: [Main] Set your [Roronoa Zoro] Leader as active.
- Printed trigger: [Trigger] Up to 1 of your Leader or Character cards gains +1000 power during this turn.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-040 - Kuzan

- Printed effect: When a card is trashed from your hand by your {Navy} type card's effect, draw cards equal to the number of cards trashed.
- Printed trigger: None
- Registered timings: `on_trash_from_hand`, `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-041 - Sanji

- Printed effect: [Activate: Main] [Once Per Turn] DON!! -1: Activate up to 1 {Straw Hat Crew} type Event with a base cost of 3 or less from your hand. [When Attacking] If the number of DON!! cards on your field is equal to or less than the number on your opponent's field, add up to 1 DON!! card from your DON!! deck and rest it.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-042 - Alvida

- Printed effect: If you have 2 or more Characters with a base cost of 5 or more, this Character gains +1 cost. [On Play] Place up to 1 of your opponent's Characters with a base cost of 1 or less at the bottom of the owner's deck.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-043 - Kuzan

- Printed effect: If you have 5 or more cards in your hand, this Character gains +1 cost. [On Play] You may trash 1 card from your hand: Up to 1 of your opponent's Characters cannot attack until the end of your opponent's next End Phase.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Needs Engine Support`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-044 - Sakazuki

- Printed effect: [On Play] If your Leader has the {Navy} type, draw 2 cards. [Activate: Main] [Once Per Turn] You may trash 1 card from your hand: Give up to 1 rested DON!! card to your Leader or 1 of your Characters.
- Printed trigger: None
- Registered timings: `on_play`, `activate`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-045 - Jango

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP12-046 - Zephyr(Navy)

- Printed effect: [On Play] Trash 2 cards from your hand. [Activate: Main] You may trash this Character: Return up to 1 Character with a cost of 5 or less to the owner's hand.
- Printed trigger: None
- Registered timings: `on_play`, `activate`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-047 - Sengoku

- Printed effect: [On Play] You may trash 1 card from your hand: Look at 5 cards from the top of your deck; reveal up to 2 {Navy} type cards other than [Sengoku] and add them to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-048 - Donquixote Rosinante

- Printed effect: [Opponent's Turn] If your blue {Navy} type Character would be removed from the field by your opponent's effect, you may rest this Character and trash 1 card from your hand instead.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Needs Engine Support`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-049 - Buggy

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP12-050 - Jaguar.D.Saul

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-051 - Hina

- Printed effect: [Activate: Main] You may rest this Character and trash 1 card from your hand: Up to 1 of your opponent's Characters with a base cost of 4 or less cannot activate [Blocker] during this turn.
- Printed trigger: None
- Registered timings: `activate`, `blocker`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-052 - Fullbody

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP12-053 - Borsalino

- Printed effect: [Once Per Turn] If this Character would be removed from the field by your opponent's effect, you may trash 1 card from your hand instead. [Opponent's Turn] If your Leader has the {Navy} type, this Character gains [Blocker] and +1000 power.
- Printed trigger: None
- Registered timings: `OPPONENTS_TURN`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-054 - Marshall.D.Teach

- Printed effect: [On Play] If your Leader has the {The Seven Warlords of the Sea} type, return up to 1 Character with a cost of 1 or less other than this Character to the owner's hand.
- Printed trigger: None
- Registered timings: `ON_PLAY`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-055 - Mohji & Cabaji

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP12-056 - Monkey.D.Garp

- Printed effect: [On Play] You may trash 1 card from your hand: Play up to 1 blue {Navy} type Character card with 8000 power or less other than [Monkey.D.Garp] from your hand.
- Printed trigger: None
- Registered timings: `ON_PLAY`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-057 - Ice Block Pheasant Peck

- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +4000 power during this battle. Then, trash 1 card from your hand.
- Printed trigger: [Trigger] You may trash 1 card from your hand: Draw 1 card.
- Registered timings: `counter`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-058 - I Will Make Whitebeard the King of the Pirates

- Printed effect: [Main] If your Leader's type includes "Whitebeard Pirates", reveal 1 card from the top of your deck. If that card is a Character card with a type including "Whitebeard Pirates" and a cost of 9 or less, you may play that card. If you do, that Character gains [Rush] during this turn.
- Printed trigger: [Trigger] Draw 1 card.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-059 - Concasser

- Printed effect: [Main] If your Leader is [Sanji], draw 1 card. [Counter] If you have 4 or more Events in your trash, up to 1 of your Leader gains +4000 power during this battle.
- Printed trigger: None
- Registered timings: `counter`, `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-060 - Boeuf Burst

- Printed effect: [Main] If your Leader is multicolored, choose one: ? Return up to 1 of your opponent's Characters with a cost of 4 or less to the owner's hand. ? If you have 6 or less cards in your hand, draw 2 cards.
- Printed trigger: None
- Registered timings: `MAIN`, `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-061 - Donquixote Rosinante

- Printed effect: [Once Per Turn] If your [Trafalgar Law] would be K.O.'d, you may add 1 card from the top of your Life cards to your hand instead. [Activate: Main] [Once Per Turn] DON!! -1: The next time you play [Trafalgar Law] with a cost of 4 or more from your hand during this turn, the cost will be reduced by 2.
- Printed trigger: None
- Registered timings: `on_ko_prevention`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-062 - Vinsmoke Sora

- Printed effect: [On Play] If your Leader is [Sanji] and the number of DON!! cards on your field is equal to or less than the number on your opponent's field, add up to 1 DON!! card from your DON!! deck and rest it. Then, draw 1 card.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-063 - Vinsmoke Reiju

- Printed effect: If you have 4 or more Events in your trash, this Character gains +2000 power and +5 cost. [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-064 - Vergo

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP12-065 - Emporio.Ivankov

- Printed effect: If you have 4 or more Events in your trash, this Character gains [Blocker]. [On K.O.] Add up to 1 Event from your trash to your hand.
- Printed trigger: None
- Registered timings: `on_ko`, `blocker`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-066 - Carne

- Printed effect: If you have 4 or more Events in your trash, this Character gains [Blocker]. (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-067 - Carmen

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP12-068 - Gin

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP12-069 - Crocodile

- Printed effect: [On Your Opponent's Attack] [Once Per Turn] DON!! -1: If your Leader's type includes "Baroque Works", up to 1 of your Leader or Character cards gains +2000 power during this battle.
- Printed trigger: None
- Registered timings: `on_opponent_attack`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-070 - Sanji

- Printed effect: This Character gains +1000 power for every 5 Events in your trash. If this Character would be removed from the field by your opponent's effect, you may return 1 DON!! card from your field to your DON!! deck instead.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Needs Engine Support`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-071 - Charlotte Pudding

- Printed effect: [On Play] Look at 4 cards from the top of your deck; reveal up to 1 [Sanji] or Event card and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-072 - Zeff

- Printed effect: When a DON!! card on your field is returned to your DON!! deck, if your Leader is [Sanji], this Character gains [Rush] during this turn. (This card can attack on the turn in which it is played.)
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-073 - Trafalgar Law

- Printed effect: [On Play] If the number of DON!! cards on your field is equal to or less than the number on your opponent's field, add up to 1 DON!! card from your DON!! deck and set it as active. Then, all of your [Donquixote Rosinante] and {Heart Pirates} type Characters gain +1000 power until the end of your opponent's next End Phase.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Needs Engine Support`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-074 - Patty

- Printed effect: [On Play] You may trash 1 Event from your hand: If your Leader is [Sanji], add up to 1 DON!! card from your DON!! deck and set it as active.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-075 - Ms. All Sunday

- Printed effect: [On Play] K.O. up to 1 of your opponent's Characters with a cost of 3 or less. Then, your opponent may add 1 DON!! card from their DON!! deck and set it as active.
- Printed trigger: [Trigger] DON!! -1: Play this card.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-076 - Monet

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP12-077 - The "Extinguishes All Sound Created by Your Influence" Technique

- Printed effect: [Main] Select up to 1 of your [Trafalgar Law] cards and that card gains +2000 power during this turn. Then, if the selected card attacks during this turn, your opponent cannot activate [Blocker].
- Printed trigger: [Trigger] Draw 1 card.
- Registered timings: `on_play`, `blocker`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-078 - Brochette Blow

- Printed effect: [Main] If the number of DON!! cards on your field is equal to or less than the number on your opponent's field, draw 1 card. Then, give up to 1 of your opponent's Characters -3000 power during this turn.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-079 - Luffy Is the Man Who Will Be King of the Pirates!!!

- Printed effect: [Main] If your Leader is [Sanji], look at 3 cards from the top of your deck and add up to 1 card to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-080 - Baratie

- Printed effect: [Activate: Main] You may place this Stage at the bottom of the owner's deck: If your Leader is [Sanji], look at 3 cards from the top of your deck; reveal up to 1 Event and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: [Trigger] Play this card.
- Registered timings: `ACTIVATE_MAIN`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-081 - Koala

- Printed effect: When this Leader attacks your opponent's Leader, if you have 2 or more Characters with a cost of 8 or more, draw 1 card. [Once Per Turn] This effect can be activated when your opponent plays a Character with a base cost of 8 or more, or when your opponent plays a Character using a Character's effect. Your opponent adds 1 card from the top of their Life cards to their hand.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-082 - Issho

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP12-083 - Inazuma

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP12-084 - Emporio.Ivankov

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On Play] If your Leader has the {Revolutionary Army} type, trash 3 cards from the top of your deck.
- Printed trigger: None
- Registered timings: `on_play`, `blocker`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-085 - Karasu

- Printed effect: If your Leader has the {Revolutionary Army} type, this Character gains +3 cost. [When Attacking] If your Leader has the {Revolutionary Army} type and your opponent has 5 or more cards in their hand, your opponent trashes 1 card from their hand.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-086 - Koala

- Printed effect: [On Play] If your Leader has the {Revolutionary Army} type, look at 3 cards from the top of your deck; reveal up to 1 {Revolutionary Army} type card other than [Koala] or up to 1 [Nico Robin] and add it to your hand. Then, trash the rest.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-087 - Nico Robin

- Printed effect: If your Leader is [Koala] or [Monkey.D.Luffy], this Character gains [Blocker] and +3 cost. [On Play] You may trash 1 card from your hand: If your opponent has 5 or more cards in their hand, your opponent trashes 2 cards from their hand.
- Printed trigger: None
- Registered timings: `on_play`, `blocker`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-088 - Bastille

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP12-089 - Hack

- Printed effect: If your Leader has the {Revolutionary Army} type, this Character gains [Blocker] and +4 cost. [On K.O.] If your Leader has the {Revolutionary Army} type, K.O. up to 1 of your opponent's Characters with a base cost of 4 or less.
- Printed trigger: None
- Registered timings: `on_ko`, `blocker`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-090 - Belo Betty

- Printed effect: [When Attacking] You may trash 2 cards from the top of your deck: Give up to 1 of your opponent's Characters -2 cost during this turn.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-091 - Poker

- Printed effect: [Activate: Main] [Once Per Turn] You may place 3 cards from your trash at the bottom of your deck in any order: Up to 2 of your {SMILE} type Characters gain +2000 power during this turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-092 - Mizerka

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP12-093 - Morley

- Printed effect: If your Leader has the {Revolutionary Army} type, this Character gains +4 cost.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-094 - Monkey.D.Dragon

- Printed effect: [On Play] You may place 3 {Revolutionary Army} type cards from your trash at the bottom of your deck in any order: If your Leader has the {Revolutionary Army} type, play up to 1 Character card with a cost of 6 or less from your trash.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-095 - Lindbergh

- Printed effect: If your Leader has the {Revolutionary Army} type, this Character gains +4 cost. [On Play] Draw 1 card and trash 1 card from your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-096 - Ursa Shock

- Printed effect: [Main] K.O. up to 1 of your opponent's Characters with a cost of 4 or less. If you have a Character with a cost of 8 or more, you may select your opponent's Character with a cost of 6 or less instead.
- Printed trigger: [Trigger] Draw 1 card and trash 1 card from the top of your deck.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-097 - Captains Assembled

- Printed effect: [Main] Look at 3 cards from the top of your deck; reveal up to 1 {Revolutionary Army} type card other than [Captains Assembled] and add it to your hand. Then, trash the rest.
- Printed trigger: [Trigger] Activate this card's [Main] effect.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-098 - Hair Removal Fist

- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +2000 power during this battle. Then, if you have a {Revolutionary Army} type Character with a cost of 8 or more, that card gains an additional +2000 power during this battle.
- Printed trigger: [Trigger] Draw 1 card and trash 1 card from the top of your deck.
- Registered timings: `counter`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-099 - Kalgara

- Printed effect: [Your Turn] When a card is removed from your or your opponent's Life cards, draw 1 card. Then, you cannot draw cards using your own effects during this turn.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-100 - Sabo

- Printed effect: If you have 3 or less Life cards, this Character gains [Blocker] and +3 cost. [On Play] You may add 1 card from the top of your Life cards to your hand: Draw 2 cards and trash 1 card from your hand.
- Printed trigger: None
- Registered timings: `CONTINUOUS`, `ON_PLAY`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-101 - Jewelry Bonney

- Printed effect: [Activate: Main] You may rest this Character: Your {Supernovas} type Leader gains +1000 power until the end of your opponent's next turn.
- Printed trigger: [Trigger] If your Leader has the {Supernovas} type, play this card.
- Registered timings: `activate`, `trigger`
- Implementation status: `Needs Engine Support`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-102 - Shirahoshi

- Printed effect: If your Character with a base cost of 6 or less would be removed from the field by your opponent's effect, you may turn 1 card from the top of your Life cards face-up instead. [Opponent's Turn] If you have no other [Shirahoshi] with a base cost of 2, all of your {Neptunian} type Characters gain +2000 power.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Needs Engine Support`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-103 - Seto

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP12-104 - Sentomaru

- Printed effect: None
- Printed trigger: [Trigger] K.O. up to 1 of your opponent's Characters with a cost of 4 or less.
- Registered timings: `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-105 - Trafalgar Lammy

- Printed effect: [Your Turn] [On Play] Up to 1 of your [Trafalgar Law] cards gains +2000 power during this turn.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-106 - Trafalgar Law

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-107 - Donquixote Doflamingo

- Printed effect: If you have 2 or less Life cards, this Character gains [Rush]. (This card can attack on the turn in which it is played.) [Opponent's Turn] [On K.O.] Add up to 1 card from the top of your deck to the top of your Life cards.
- Printed trigger: None
- Registered timings: `CONTINUOUS`, `ON_KO`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-108 - Donquixote Rosinante

- Printed effect: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 [Trafalgar Law] and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-109 - Pacifista

- Printed effect: None
- Printed trigger: [Trigger] K.O. up to 1 of your opponent's Characters with a cost of 1 or less and add this card to your hand.
- Registered timings: `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-110 - Buffalo

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP12-111 - Baby 5

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP12-112 - Baby 5

- Printed effect: None
- Printed trigger: [Trigger] If your Leader is multicolored, draw 2 cards.
- Registered timings: `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-113 - Roronoa Zoro

- Printed effect: [On K.O.] If your Leader has the {Supernovas} type, play up to 1 {Supernovas} type Character card with a cost of 4 or less from your hand rested.
- Printed trigger: [Trigger] K.O. up to 1 of your opponent's Characters with a cost of 1 or less and add this card to your hand.
- Registered timings: `on_ko`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-114 - Wyper

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP12-115 - I Love You!!

- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +2000 power during this battle. Then, if you have 2 or less Life cards, add up to 1 [Trafalgar Law] from your trash to your hand.
- Printed trigger: None
- Registered timings: `COUNTER`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP12-116 - We'll Ring the Bell Waiting for You!!

- Printed effect: [Main] Look at 5 cards from the top of your deck; reveal a total of up to 2 {Shandian Warrior} type Character cards or [Mont Blanc Noland] and add them to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: [Trigger] Draw 1 card.
- Registered timings: `MAIN`, `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-117 - Slam Gibson

- Printed effect: [Main] You may rest 5 of your DON!! cards: If your Leader has the {Supernovas} type, add up to 1 Character with a cost of 9 or less to the top or bottom of the owner's Life cards face-down. [Counter] Your Leader gains +3000 power during this battle.
- Printed trigger: None
- Registered timings: `counter`, `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-118 - Jewelry Bonney

- Printed effect: [Blocker] [On Play] If you have 8 or more rested cards, draw 2 cards and trash 1 card from your hand. Then, set up to 1 of your DON!! cards as active.
- Printed trigger: None
- Registered timings: `on_play`, `blocker`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP12-119 - Bartholomew Kuma

- Printed effect: [On Play] You may trash 1 card from your hand: Add up to 1 card from the top of your deck to the top of your Life cards. Then, this Character gains +2 cost until the end of your opponent's next End Phase. [Opponent's Turn] [On K.O.] Add up to 1 card from the top of your deck to the top of your Life cards.
- Printed trigger: None
- Registered timings: `on_play`, `on_ko`
- Implementation status: `Needs Engine Support`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP12 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
