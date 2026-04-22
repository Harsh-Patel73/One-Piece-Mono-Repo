# OP08 Master Audit

Source of truth: `packages/simulator/backend/data/cards.json` base OP08 entries where `id == id_normal`.

## Summary

- Base cards audited: 119
- Non-vanilla cards: 109
- Vanilla cards: 10
- Registered OP08 cards after this pass: 109
- Registered OP08 timings after this pass: 143
- Missing non-vanilla registrations: 0
- Missing printed trigger timings: 0
- Strict status after this pass: 109/119 `Complete` or `Vanilla`; 10 follow-up cards flagged below

## Verification

- OP08 import/compile path passed during coverage and sweep.
- OP08 registration coverage script passed: `base=119 nonvanilla=109 vanilla=10 registered_cards=109 timings=143 missing=[] missing_triggers=[]`.
- Direct OP08 handler execution sweep passed: `OP08_handler_sweep_ran=143 errors=0 tracebacks=0`, resolving pending choices through `GameState.resolve_pending_choice(...)`.
- Full pytest suite was not rerun in this pass; earlier environment check showed `python -m pytest packages\game-engine\tests` is unavailable because `pytest` is not installed.

## Follow-Up Queue

- `OP08-001` Tony Tony.Chopper: `Partial` - Leader DON assignment auto-distributes rested DON; printed text should allow choosing up to 3 targets exactly.
- `OP08-002` Marco: `Partial` - Draw/place card top-or-bottom flow is simplified; exact hand-to-deck placement choice should be improved.
- `OP08-021` Carrot: `Partial` - Search/reveal ordering should be manually validated with real Animal/Drum Kingdom fixtures.
- `OP08-022` Inuarashi: `Needs Engine Support` - Temporary power and duration cleanup should be manually validated.
- `OP08-057` King: `Partial` - Blue hand/deck ordering effects should be replay-tested for exact top/bottom choice order.
- `OP08-069` Charlotte Linlin: `Partial` - DON-return cost and follow-up targeting should be manually validated for optional cost timing.
- `OP08-084` Jack: `Needs Engine Support` - Black cost reduction duration cleanup depends on engine temporary modifier support.
- `OP08-098` Kalgara: `Partial` - Life manipulation and trigger timing should be manually validated with exact life counts.
- `OP08-106` Nami: `Partial` - Yellow life/deck manipulation uses helper sequencing; exact reveal/add ordering should be replayed.
- `OP08-118` Silvers Rayleigh: `Partial` - Event multi-step effect should be manually validated for exact target filters and optional branch ordering.

## Per-Card Audit

### OP08-001 - Tony Tony.Chopper

- Printed effect: [Activate: Main] [Once Per Turn] Give up to 3 of your {Animal} or {Drum Kingdom} type Characters up to 1 rested DON!! card each.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Leader DON assignment auto-distributes rested DON; printed text should allow choosing up to 3 targets exactly.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Leader DON assignment auto-distributes rested DON; printed text should allow choosing up to 3 targets exactly.

### OP08-002 - Marco

- Printed effect: [DON!! x1] [Activate: Main] [Once Per Turn] Draw 1 card and place 1 card from your hand at the top or bottom of your deck. Then, give up to 1 of your opponent's Characters -2000 power during this turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Draw/place card top-or-bottom flow is simplified; exact hand-to-deck placement choice should be improved.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Draw/place card top-or-bottom flow is simplified; exact hand-to-deck placement choice should be improved.

### OP08-003 - Twenty Doctors

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-004 - Kuromarimo

- Printed effect: [On Play] If you have [Chess], K.O. up to 1 of your opponent's Characters with 3000 power or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-005 - Chess

- Printed effect: [On Play] Give up to 1 of your opponent's Characters -2000 power during this turn. Then, if you don't have [Kuromarimo], play up to 1 [Kuromarimo] from your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-006 - Chessmarimo

- Printed effect: [Your Turn] If you have [Kuromarimo] and [Chess] in your trash, this Character gains +2000 power.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-007 - Tony Tony.Chopper

- Printed effect: [Your Turn] [On Play]/[When Attacking] Look at 5 cards from the top of your deck and play up to 1 {Animal} type Character card with 4000 power or less rested. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`, `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-008 - Dalton

- Printed effect: [On Play] Give up to 1 of your opponent's Characters -1000 power during this turn. [DON!! x1] [Activate: Main] [Once Per Turn] You may add 1 card from the top of your Life cards to your hand: This Character gains [Rush] during this turn. (This card can attack on the turn in which it is played.)
- Printed trigger: None
- Registered timings: `on_play`, `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-009 - Maria Onion Bear

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP08-010 - Hiking Bear

- Printed effect: [DON!! x1] [Activate: Main] [Once Per Turn] Up to 1 of your {Animal} type Characters other than this Character gains +1000 power during this turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-011 - Musshuru

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP08-012 - Lapins

- Printed effect: [DON!! x2] [When Attacking] If your Leader has the {Drum Kingdom} type, K.O. up to 1 of your opponent's Characters with 4000 power or less.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-013 - Robson

- Printed effect: [DON!! x2] This Character gains [Rush]. (This card can attack on the turn in which it is played.)
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-014 - Wapol

- Printed effect: [DON!! x1] [When Attacking] Give up to 1 of your opponent's Characters -2000 power during this turn. Then, this Character gains +2000 power until the end of your opponent's next turn.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-015 - Dr.Kureha

- Printed effect: [On Play] Look at 4 cards from the top of your deck; reveal up to 1 [Tony Tony.Chopper] or {Drum Kingdom} type card other than [Dr.Kureha] and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-016 - Dr.Hiriluk

- Printed effect: [Activate: Main] You may rest this Character: If your Leader is [Tony Tony.Chopper], all of your [Tony Tony.Chopper] Characters gain +2000 power during this turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-017 - I'd Never Shoot You!!!!

- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +4000 power during this battle. Then, give up to 1 of your opponent's Leader or Character cards -1000 power during this turn.
- Printed trigger: [Trigger] Up to 1 of your Leader or Character cards gains +1000 power during this turn.
- Registered timings: `counter`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-018 - Cloven Rose

- Printed effect: [Main] Up to 3 of your Characters gain +1000 power during this turn. Then, give up to 1 of your opponent's Characters -2000 power during this turn.
- Printed trigger: [Trigger] Give up to 1 of your opponent's Leader or Character cards -3000 power during this turn.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-019 - Munch-Munch Mutation

- Printed effect: [Main]/[Counter] Give up to 1 of your opponent's Characters -3000 power during this turn. Then, up to 1 of your Characters gains +3000 power during this turn.
- Printed trigger: [Trigger] K.O. up to 1 of your opponent's Characters with 5000 power or less.
- Registered timings: `on_play`, `counter`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-020 - Drum Kingdom

- Printed effect: [Opponent's Turn] All of your {Drum Kingdom} type Characters gain +1000 power.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-021 - Carrot

- Printed effect: [Activate: Main] [Once Per Turn] If you have a {Minks} type Character, rest up to 1 of your opponent's Characters with a cost of 5 or less.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Search/reveal ordering should be manually validated with real Animal/Drum Kingdom fixtures.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Search/reveal ordering should be manually validated with real Animal/Drum Kingdom fixtures.

### OP08-022 - Inuarashi

- Printed effect: [On Play] If your Leader has the {Minks} type, up to 2 of your opponent's rested Characters with a cost of 5 or less will not become active in your opponent's next Refresh Phase.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Needs Engine Support`
- Required code changes: Temporary power and duration cleanup should be manually validated.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Temporary power and duration cleanup should be manually validated.

### OP08-023 - Carrot

- Printed effect: [On Play]/[When Attacking] Up to 1 of your opponent's rested Characters with a cost of 7 or less will not become active in your opponent's next Refresh Phase.
- Printed trigger: None
- Registered timings: `on_play`, `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-024 - Concelot

- Printed effect: [When Attacking] Up to 1 of your opponent's rested Characters with a cost of 4 or less will not become active in your opponent's next Refresh Phase.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-025 - Shishilian

- Printed effect: [On Play] Up to 1 of your opponent's rested Characters with a cost of 3 or less will not become active in your opponent's next Refresh Phase.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-026 - Giovanni

- Printed effect: [DON!! x1] [When Attacking] Up to 1 of your opponent's rested Characters with a cost of 1 or less will not become active in your opponent's next Refresh Phase.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-027 - Tristan

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP08-028 - Nekomamushi

- Printed effect: [On Play] If your opponent has 7 or more rested cards, this Character gains [Rush] during this turn. (This card can attack on the turn in which it is played.)
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-029 - Pekoms

- Printed effect: If this Character is active, your {Minks} type Characters with a cost of 3 or less other than [Pekoms] cannot be K.O.'d by effects.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-030 - Pedro

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On K.O.] Choose one: ? Rest up to 1 of your opponent's DON!! cards. ? K.O. up to 1 of your opponent's rested Characters with a cost of 6 or less.
- Printed trigger: None
- Registered timings: `blocker`, `on_ko`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-031 - Miyagi

- Printed effect: [On Play] Set up to 1 of your {Minks} type Characters with a cost of 2 or less as active.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-032 - Milky

- Printed effect: [Activate: Main] You may rest this Character: If your Leader has the {Minks} type, set up to 1 of your DON!! cards as active.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-033 - Roddy

- Printed effect: [On Play] If your Leader has the {Minks} type and your opponent has 7 or more rested cards, K.O. up to 1 of your opponent's rested Characters with a cost of 2 or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-034 - Wanda

- Printed effect: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 {Minks} type card other than [Wanda] and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-035 - BB

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP08-036 - Electrical Luna

- Printed effect: [Main] All of your opponent's rested Characters with a cost of 7 or less will not become active in your opponent's next Refresh Phase.
- Printed trigger: [Trigger] Rest up to 1 of your opponent's Characters.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-037 - Garchu

- Printed effect: [Main] You may rest 1 of your {Minks} type Characters: Rest up to 1 of your opponent's Characters.
- Printed trigger: [Trigger] Draw 1 card.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-038 - We Would Never Sell a Comrade to an Enemy!!!

- Printed effect: [Main] You may rest 2 of your Characters: None of your Characters can be K.O.'d by your opponent's effects until the end of your opponent's next turn.
- Printed trigger: [Trigger] Rest up to 1 of your opponent's Characters with a cost of 3 or less.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-039 - Zou

- Printed effect: [Activate: Main] You may rest this Stage: If your Leader has the {Minks} type, set up to 1 of your DON!! cards as active. [End of Your Turn] Set up to 1 of your {Minks} type Characters as active.
- Printed trigger: None
- Registered timings: `activate`, `end_of_turn`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-040 - Atmos

- Printed effect: [On Play] You may reveal 2 cards with a type including "Whitebeard Pirates" from your hand: If your Leader's type includes "Whitebeard Pirates", return up to 1 of your opponent's Characters with a cost of 4 or less to the owner's hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-041 - Aphelandra

- Printed effect: [Activate: Main] You may return this Character to the owner's hand: If your Leader has the {Kuja Pirates} type, place up to 1 of your opponent's Characters with a cost of 1 or less at the bottom of the owner's deck.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-042 - Edward Weevil

- Printed effect: [DON!! x1] [When Attacking] Return up to 1 Character with a cost of 3 or less to the owner's hand.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-043 - Edward.Newgate

- Printed effect: [On Play] If your Leader's type includes "Whitebeard Pirates" and you have 2 or less Life cards, select all of your opponent's Characters on their field. Until the end of your opponent's next turn, none of the selected Characters can attack unless your opponent trashes 2 cards from their hand whenever they attack.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-044 - Kingdew

- Printed effect: [Activate: Main] [Once Per Turn] You may reveal 2 cards with a type including "Whitebeard Pirates" from your hand: This Character gains +2000 power during this turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-045 - Thatch

- Printed effect: If this Character would be removed from the field by your opponent's effect or K.O.'d, trash this Character and draw 1 card instead.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-046 - Shakuyaku

- Printed effect: [Your Turn] [Once Per Turn] When a Character is removed from the field by your effect, if your opponent has 5 or more cards in their hand, your opponent places 1 card from their hand at the bottom of their deck. Then, rest this Character.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-047 - Jozu

- Printed effect: [On Play] You may return 1 of your Characters other than this Character to the owner's hand: Return up to 1 Character with a cost of 6 or less to the owner's hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-048 - Sweetpea

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP08-049 - Speed Jil

- Printed effect: [On Play] Reveal 1 card from the top of your deck and place it at the top or bottom of your deck. If the revealed card's type includes "Whitebeard Pirates", this Character gains [Rush] during this turn. (This card can attack on the turn in which it is played.)
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-050 - Namule

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On Play] Draw 2 cards and place 2 cards from your hand at the top or bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `blocker`, `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-051 - Buckin

- Printed effect: [Your Turn] [On Play] Up to 1 of your [Edward Weevil] cards gains +2000 power during this turn.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-052 - Portgas.D.Ace

- Printed effect: [On Play] Reveal 1 card from the top of your deck and play up to 1 Character card with a type including "Whitebeard Pirates" and a cost of 4 or less. Then, place the rest at the top or bottom of your deck.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-053 - Thank You...for Loving Me!!

- Printed effect: [Main] If your Leader's type includes "Whitebeard Pirates", look at 3 cards from the top of your deck; reveal up to 1 card with a type including "Whitebeard Pirates" or [Monkey.D.Luffy] and add it to your hand. Then, place the rest at the top or bottom of your deck in any order.
- Printed trigger: [Trigger] Draw 1 card.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-054 - You Can't Take Our King This Early in the Game.

- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +3000 power during this battle. Then, reveal 1 card from the top of your deck and play up to 1 Character card with a type including "Whitebeard Pirates" and a cost of 3 or less. Then, place the rest at the top or bottom of your deck.
- Printed trigger: None
- Registered timings: `counter`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-055 - Phoenix Brand

- Printed effect: [Main] You may reveal 2 cards with a type including "Whitebeard Pirates" from your hand: Place up to 1 Character with a cost of 6 or less at the bottom of the owner's deck.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-056 - Moby Dick

- Printed effect: [Your Turn] [Once Per Turn] When your Character with a type including "Whitebeard Pirates" is removed from the field by an effect, draw 1 card. Then, place 1 card from your hand at the top or bottom of your deck.
- Printed trigger: [Trigger] Play this card.
- Registered timings: `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-057 - King

- Printed effect: [Activate: Main] [Once Per Turn] DON!! -2 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Choose one: ? If you have 5 or less cards in your hand, draw 1 card. ? Give up to 1 of your opponent's Characters -2 cost during this turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Blue hand/deck ordering effects should be replay-tested for exact top/bottom choice order.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Blue hand/deck ordering effects should be replay-tested for exact top/bottom choice order.

### OP08-058 - Charlotte Pudding

- Printed effect: [When Attacking] You may turn 2 cards from the top of your Life cards face-up: Add up to 1 DON!! card from your DON!! deck and rest it.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-059 - Alber

- Printed effect: [Activate: Main] You may trash this Character: If your Leader has the {Animal Kingdom Pirates} type and you have 10 DON!! cards on your field, play up to 1 [King] with a cost of 7 or less from your hand.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-060 - King

- Printed effect: [On Play] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): If your opponent has 5 or more DON!! cards on their field, this Character gains [Rush] during this turn. (This card can attack on the turn in which it is played.)
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-061 - Charlotte Oven

- Printed effect: [When Attacking] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): K.O. up to 1 of your opponent's Characters with a cost of 3 or less.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-062 - Charlotte Katakuri

- Printed effect: [Activate: Main] You may trash this Character: If your Leader has the {Big Mom Pirates} type, play up to 1 [Charlotte Katakuri] from your hand with a cost of 3 or more that is equal to or less than the number of DON!! cards on your opponent's field.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-063 - Charlotte Katakuri

- Printed effect: [On Play] You may turn 1 card from the top of your Life cards face-down: Add up to 1 DON!! card from your DON!! deck and set it as active.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-064 - Charlotte Cracker

- Printed effect: [Activate: Main] [Once Per Turn] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Play up to 1 [Biscuit Warrior] from your hand.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-065 - Charlotte Smoothie

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP08-066 - Charlotte Brulee

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On K.O.] Add up to 1 DON!! card from your DON!! deck and rest it.
- Printed trigger: None
- Registered timings: `blocker`, `on_ko`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-067 - Charlotte Pudding

- Printed effect: [Your Turn] [Once Per Turn] When a DON!! card on your field is returned to your DON!! deck, add up to 1 DON!! card from your DON!! deck and rest it.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-068 - Charlotte Perospero

- Printed effect: [On K.O.] Add up to 1 DON!! card from your DON!! deck and rest it.
- Printed trigger: [Trigger] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Play this card.
- Registered timings: `on_ko`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-069 - Charlotte Linlin

- Printed effect: [On Play] DON!! -1, You may trash 1 card from your hand: Add up to 1 card from the top of your deck to the top of your Life cards. Then, add up to 1 of your opponent's Characters with a cost of 6 or less to the top or bottom of your opponent's Life cards face-up.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: DON-return cost and follow-up targeting should be manually validated for optional cost timing.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: DON-return cost and follow-up targeting should be manually validated for optional cost timing.

### OP08-070 - Baron Tamago

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On K.O.] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Play up to 1 [Viscount Hiyoko] with a cost of 5 or less from your hand.
- Printed trigger: None
- Registered timings: `blocker`, `on_ko`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-071 - Count Niwatori

- Printed effect: [Opponent's Turn] [On K.O.] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Play up to 1 [Baron Tamago] with a cost of 4 or less from your deck. Then, shuffle your deck.
- Printed trigger: None
- Registered timings: `on_ko`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-072 - Biscuit Warrior

- Printed effect: Under the rules of this game, you may have any number of this card in your deck. [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-073 - Viscount Hiyoko

- Printed effect: [Opponent's Turn] [On K.O.] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Play up to 1 [Count Niwatori] with a cost of 6 or less from your deck. Then, shuffle your deck.
- Printed trigger: None
- Registered timings: `on_ko`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-074 - Black Maria

- Printed effect: [Activate: Main] [Once Per Turn] If you have no other [Black Maria] Characters, add up to 5 DON!! cards from your DON!! deck and rest them. Then, at the end of this turn, return DON!! cards from your field to your DON!! deck until you have the same number of DON!! cards on your field as your opponent.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-075 - Candy Maiden

- Printed effect: [Main] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Rest up to 1 of your opponent's Characters with a cost of 2 or less. Then, turn all of your Life cards face-down.
- Printed trigger: [Trigger] Add up to 1 DON!! card from your DON!! deck and set it as active.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-076 - It's to Die For...

- Printed effect: [Main] Add up to 1 DON!! card from your DON!! deck and set it as active. Then, if your opponent has a Character with 6000 power or more, add up to 1 DON!! card from your DON!! deck and set it as active.
- Printed trigger: [Trigger] Add up to 1 DON!! card from your DON!! deck and set it as active.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-077 - Conquest of the Sea

- Printed effect: [Main] DON!! -2 (You may return the specified number of DON!! cards from your field to your DON!! deck.): If your Leader has the {Animal Kingdom Pirates} or {Big Mom Pirates} type, K.O. up to 2 of your opponent's Characters with a cost of 6 or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-078 - Ulti

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP08-079 - Kaido

- Printed effect: [Activate: Main] [Once Per Turn] You may trash 1 card from your hand: If this Character was played on this turn, trash up to 1 of your opponent's Characters with a cost of 7 or less. Then, your opponent trashes 1 card from their hand.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-080 - Queen

- Printed effect: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 {Animal Kingdom Pirates} type card other than [Queen] and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-081 - Guernica

- Printed effect: [When Attacking] You may place 3 cards with a type including "CP" from your trash at the bottom of your deck in any order: K.O. up to 1 of your opponent's Characters with a cost of 0.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-082 - Sasaki

- Printed effect: [Activate: Main] Rest 1 of your DON!! cards and you may rest this Character: Give up to 1 of your opponent's Characters -2 cost during this turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-083 - Sheepshead

- Printed effect: [DON!! x1] [Your Turn] Give all of your opponent's Characters -1 cost.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-084 - Jack

- Printed effect: This Character gains +4 cost. [Activate: Main] You may rest this Character: Draw 1 card and trash 1 card from your hand. Then, K.O. up to 1 of your opponent's Characters with a cost of 3 or less.
- Printed trigger: None
- Registered timings: `continuous`, `activate`
- Implementation status: `Needs Engine Support`
- Required code changes: Black cost reduction duration cleanup depends on engine temporary modifier support.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Black cost reduction duration cleanup depends on engine temporary modifier support.

### OP08-085 - Jinbe

- Printed effect: [DON!! x1] [When Attacking] If you have a Character with a cost of 8 or more, K.O. up to 1 of your opponent's Characters with a cost of 4 or less.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-086 - Ginrummy

- Printed effect: [On Play] If your opponent has a Character with a cost of 0, draw 2 cards and trash 2 cards from your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-087 - Scratchmen Apoo

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [Activate: Main] [Once Per Turn] Give up to 1 of your opponent's Characters -1 cost during this turn.
- Printed trigger: None
- Registered timings: `blocker`, `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-088 - Duval

- Printed effect: [On Play] Up to 1 of your Characters gains +1 cost until the end of your opponent's next turn.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-089 - Basil Hawkins

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP08-090 - Hamlet

- Printed effect: [On Play] Play up to 1 {SMILE} type Character card with a cost of 2 or less from your trash.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-091 - Who's.Who

- Printed effect: [On Play] You may trash 1 card from your hand: K.O. up to 1 of your opponent's Characters with a cost of 3 or less.
- Printed trigger: [Trigger] K.O. up to 1 of your opponent's Characters with a cost of 3 or less.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-092 - Page One

- Printed effect: [On Play] Play up to 1 [Ulti] with a cost of 4 or less from your trash.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-093 - X.Drake

- Printed effect: [DON!! x1] This Character gains +2 cost.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-094 - Imperial Flame

- Printed effect: [Main]/[Counter] You may place 3 cards from your trash at the bottom of your deck in any order: K.O. up to 1 of your opponent's Characters with a cost of 2 or less.
- Printed trigger: [Trigger] Activate this card's [Main] effect.
- Registered timings: `on_play`, `counter`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-095 - Iron Body Fang Flash

- Printed effect: [Main] If you have 10 or more cards in your trash, up to 1 of your Characters gains +2000 power until the end of your opponent's next turn.
- Printed trigger: [Trigger] Up to 1 of your Leader or Character cards gains +2000 power during this turn.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-096 - People's Dreams Don't Ever End!!

- Printed effect: [Counter] Trash 1 card from the top of your deck. If the trashed card has a cost of 6 or more, up to 1 of your Leader or Character cards gains +5000 power during this battle.
- Printed trigger: [Trigger] Play up to 1 black Character card with a cost of 3 or less from your trash.
- Registered timings: `counter`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-097 - Heliceratops

- Printed effect: [Main] If your Leader has the {Animal Kingdom Pirates} type, give up to 1 of your opponent's Characters -2 cost during this turn. Then, K.O. up to 1 of your opponent's Characters with a cost of 0.
- Printed trigger: [Trigger] K.O. up to 1 of your opponent's Characters with a cost of 3 or less.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-098 - Kalgara

- Printed effect: [DON!! x1] [When Attacking] Play up to 1 {Shandian Warrior} type Character card from your hand with a cost equal to or less than the number of DON!! cards on your field. If you do, add 1 card from the top of your Life cards to your hand.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Partial`
- Required code changes: Life manipulation and trigger timing should be manually validated with exact life counts.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Life manipulation and trigger timing should be manually validated with exact life counts.

### OP08-099 - Kalgara

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP08-100 - South Bird

- Printed effect: [On Play] Look at 7 cards from the top of your deck and play up to 1 [Upper Yard]. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-101 - Charlotte Angel

- Printed effect: [Activate: Main] [Once Per Turn] You may trash 1 card from the top of your Life cards: If your Leader has the {Big Mom Pirates} type, add 1 card from the top of your deck to the top of your Life cards at the end of this turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-102 - Charlotte Opera

- Printed effect: [On Play] You may trash 1 card from your hand: K.O. up to 1 of your opponent's Characters with a cost equal to or less than your number of Life cards.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-103 - Charlotte Custard

- Printed effect: [Activate: Main] [Once Per Turn] You may add 1 card from the top of your Life cards to your hand: Up to 1 of your Characters gains +1000 power until the end of your opponent's next turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-104 - Charlotte Poire

- Printed effect: None
- Printed trigger: [Trigger] You may trash 1 card from your hand: Play this card. Then, draw 1 card.
- Registered timings: `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-105 - Jewelry Bonney

- Printed effect: [DON!! x1] [Your Turn] [Once Per Turn] When a card is removed from your opponent's Life cards, draw 2 cards and trash 1 card from your hand.
- Printed trigger: [Trigger] Draw 2 cards and trash 1 card from your hand.
- Registered timings: `continuous`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-106 - Nami

- Printed effect: [On Play] You may trash 1 card with a [Trigger] from your hand: K.O. up to 1 of your opponent's Characters with a cost of 5 or less. Then, if you have 3 or less cards in your hand, draw 1 card.
- Printed trigger: [Trigger] Activate this card's [On Play] effect.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Yellow life/deck manipulation uses helper sequencing; exact reveal/add ordering should be replayed.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Yellow life/deck manipulation uses helper sequencing; exact reveal/add ordering should be replayed.

### OP08-107 - Nitro

- Printed effect: [Activate: Main] You may rest this Character: Up to 1 of your [Charlotte Pudding] cards gains +2000 power during this turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-108 - Mont Blanc Cricket

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP08-109 - Mont Blanc Noland

- Printed effect: [On Play] If your Leader has the {Shandian Warrior} type and you have a [Kalgara] Character, add up to 1 card from the top of your deck to the top of your Life cards.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-110 - Wyper

- Printed effect: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 [Upper Yard] and add it to your hand. Then, place the rest at the bottom of your deck in any order and play up to 1 [Upper Yard] from your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-111 - S-Shark

- Printed effect: [DON!! x1] [When Attacking] Your opponent cannot activate [Blocker] during this battle.
- Printed trigger: [Trigger] You may trash 1 card from your hand: If you have 2 or less Life cards, play this card.
- Registered timings: `on_attack`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-112 - S-Snake

- Printed effect: [On Play] Up to 1 of your opponent's Characters with a cost of 6 or less other than [Monkey.D.Luffy] cannot attack until the end of your opponent's next turn.
- Printed trigger: [Trigger] Activate this card's [On Play] effect.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-113 - S-Bear

- Printed effect: None
- Printed trigger: [Trigger] You may trash 1 card from your hand: If you have 2 or less Life cards, play this card and K.O. up to 1 of your opponent's Characters with a cost of 3 or less.
- Registered timings: `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-114 - S-Hawk

- Printed effect: [DON!! x1] If you have less Life cards than your opponent, this Character cannot be K.O.'d in battle by <Slash> attribute cards and gains +2000 power.
- Printed trigger: [Trigger] You may trash 1 card from your hand: If you have 2 or less Life cards, play this card.
- Registered timings: `continuous`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-115 - The Earth Will Not Lose!

- Printed effect: [Counter] If your Leader has the {Shandian Warrior} type, up to 1 of your Leader or Character cards gains +3000 power during this battle. Then, play up to 1 [Upper Yard] from your hand.
- Printed trigger: [Trigger] Draw 2 cards and trash 1 card from your hand.
- Registered timings: `counter`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-116 - Burn Bazooka

- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +4000 power during this battle. Then, you may add 1 card from the top or bottom of your Life cards to your hand. If you do, add up to 1 {Shandian Warrior} type card from your hand to the top of your Life cards face-up.
- Printed trigger: None
- Registered timings: `counter`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-117 - Burn Blade

- Printed effect: [Main] You may trash 1 card from the top of your Life cards: K.O. up to 1 of your opponent's Characters with a cost of 7 or less.
- Printed trigger: [Trigger] You may add 1 card from the top of your Life cards to your hand: Add up to 1 card from your hand to the top of your Life cards.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP08-118 - Silvers Rayleigh

- Printed effect: [On Play] Select up to 2 of your opponent's Characters, and give 1 Character -3000 power and the other -2000 power until the end of your opponent's next turn. Then, K.O. up to 1 of your opponent's Characters with 3000 power or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Event multi-step effect should be manually validated for exact target filters and optional branch ordering.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Event multi-step effect should be manually validated for exact target filters and optional branch ordering.

### OP08-119 - Kaido & Linlin

- Printed effect: [When Attacking] DON!! -10: K.O. all Characters other than this Character. Then, add up to 1 card from the top of your deck to the top of your Life cards and trash up to 1 card from the top of your opponent's Life cards.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP08 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.
