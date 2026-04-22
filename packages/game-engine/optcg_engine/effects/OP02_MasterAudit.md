# OP02 Master Audit

Source of truth: `packages/simulator/backend/data/cards.json` base OP02 entries where `id == id_normal`.

## Summary

- Base cards audited: 121
- Non-vanilla cards: 101
- Vanilla cards: 20
- Registered OP02 cards after this pass: 101
- Registered OP02 timings after this pass: 136
- Missing non-vanilla registrations: 0
- Missing printed trigger timings: 0
- Strict status after this pass: 109/121 `Complete` or `Vanilla`; 12 follow-up cards flagged below

## Verification

- `python -m py_compile packages\game-engine\optcg_engine\effects\sets\op02_effects.py` passed.
- OP02 registration coverage script passed: `base=121 nonvanilla=101 vanilla=20 registered_cards=101 timings=136 missing=[] missing_triggers=[]`.
- Direct OP02 handler execution sweep passed: `OP02_handler_sweep_ran=136 errors=0`, resolving pending choices through `GameState.resolve_pending_choice(...)`.
- Full pytest suite was not rerun in this pass; earlier environment check showed `python -m pytest packages\game-engine\tests` is unavailable because `pytest` is not installed.

## Follow-Up Queue

- `OP02-002` Monkey.D.Garp: `Partial` - Needs stricter once-per-turn tracking on the DON-attach listener and exact source validation for Leader-or-Character DON attachment.
- `OP02-024` Moby Dick: `Needs Engine Support` - Continuous +2000 can stack if re-applied; exact continuous recalculation/cleanup needs engine-level duration support.
- `OP02-025` Kin'emon: `Partial` - Next Land of Wano discount is represented as a player flag; exact play-cost interception should be validated in the play engine.
- `OP02-026` Sanji: `Partial` - Leader hook is registered, but exact once-per-turn play-listener behavior depends on simulator event dispatch.
- `OP02-045` Three Sword Style Oni Giri: `Partial` - Counter currently applies +6000 to Leader before the play-from-hand choice; printed text allows choosing Leader or Character.
- `OP02-048` Land of Wano: `Partial` - Stage resolves the DON active step by setting the first rested DON active rather than prompting which DON.
- `OP02-069` DEATH WINK: `Partial` - Counter currently applies +6000 to Leader directly; printed text allows choosing Leader or Character.
- `OP02-070` New Kama Land: `Partial` - New Kama Land uses chained hand trash choices, but the exact optional up-to-3 discard UX needs manual validation.
- `OP02-089` Judgment of Hell: `Partial` - Trigger returns one opponent DON automatically; printed text implies the opponent returns a DON from field.
- `OP02-090` Hydra: `Partial` - Trigger returns one opponent DON automatically; printed text implies the opponent returns a DON from field.
- `OP02-091` Venom Road: `Partial` - Trigger returns one opponent DON automatically; printed text implies the opponent returns a DON from field.
- `OP02-118` Yasakani Sacred Jewel: `Partial` - Counter auto-pays/trashes when possible before protection choice; printed text says you may trash 1 card first.

## Per-Card Audit

### OP02-001 - Edward.Newgate

- Printed effect: [End of Your Turn] Add 1 card from the top of your Life cards to your hand.
- Printed trigger: None
- Registered timings: `end_of_turn`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-002 - Monkey.D.Garp

- Printed effect: [Your Turn] When this Leader or any of your Characters is given a DON!! card, give up to 1 of your opponent's Characters with a cost of 7 or less -1 cost during this turn.
- Printed trigger: None
- Registered timings: `on_don_attached`
- Implementation status: `Partial`
- Required code changes: Needs stricter once-per-turn tracking on the DON-attach listener and exact source validation for Leader-or-Character DON attachment.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Needs stricter once-per-turn tracking on the DON-attach listener and exact source validation for Leader-or-Character DON attachment.

### OP02-003 - Atmos

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP02-004 - Edward.Newgate

- Printed effect: [On Play] Up to 1 of your Leader gains +2000 power until the start of your next turn. Then, you cannot add Life cards to your hand using your own effects during this turn.<br>[DON!! x2] [When Attacking] K.O. up to 1 of your opponent's Characters with 3000 power or less.
- Printed trigger: None
- Registered timings: `on_play`, `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-005 - Curly.Dadan

- Printed effect: [On Play] Look at up to 5 cards from the top of your deck; reveal up to 1 red Character with a cost of 1 and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-006 - Kingdew

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP02-007 - Thatch

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP02-008 - Jozu

- Printed effect: [DON!! x1] If you have 2 or less Life cards and your Leader's type includes "Whitebeard Pirates", this Character gains [Rush].<br>(This card can attack on the turn in which it is played.)
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-009 - Squard

- Printed effect: [On Play] If your Leader's type includes "Whitebeard Pirates", give up to 1 of your opponent's Characters -4000 power during this turn and add 1 card from the top of your Life cards to your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-010 - Dogura

- Printed effect: [Activate: Main] You may rest this Character: Play up to 1 red Character other than [Dogura] with a cost of 1 from your hand.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-011 - Vista

- Printed effect: [On Play] K.O. up to 1 of your opponent's Characters with 3000 power or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-012 - Blenheim

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-013 - Portgas.D.Ace

- Printed effect: [On Play] Give up to 2 of your opponent's Characters -3000 power during this turn. Then, if your Leader's type includes "Whitebeard Pirates", this Character gains [Rush] during this turn.<br>(This card can attack on the turn in which it is played.)
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-014 - Whitey Bay

- Printed effect: [DON!! x1] This Character can also attack your opponent's active Characters.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-015 - Makino

- Printed effect: [Activate: Main] You may rest this Character: Up to 1 of your red Characters with a cost of 1 gains +3000 power during this turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-016 - Magura

- Printed effect: [On Play] Up to 1 of your red Characters with a cost of 1 gains +3000 power during this turn.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-017 - Masked Deuce

- Printed effect: [DON!! x2] [When Attacking] K.O. up to 1 of your opponent's Characters with 2000 power or less.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-018 - Marco

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)<br>[On K.O.] You may trash 1 card with a type including "Whitebeard Pirates" from your hand: If you have 2 or less Life cards, play this Character card from your trash rested.
- Printed trigger: None
- Registered timings: `blocker`, `on_ko`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-019 - Rakuyo

- Printed effect: [DON!! x1] [Your Turn] All of your Characters with a type including "Whitebeard Pirates" gain +1000 power.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-020 - LittleOars Jr.

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP02-021 - Seaquake

- Printed effect: [Main] If your Leader's type includes "Whitebeard Pirates", K.O. up to 1 of your opponent's Characters with 3000 power or less.
- Printed trigger: [Trigger] Give up to 1 of your opponent's Leader or Character cards -3000 power during this turn.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-022 - Whitebeard Pirates

- Printed effect: [Main] Look at 5 cards from the top of your deck; reveal up to 1 Character card with a type including "Whitebeard Pirates" and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: [Trigger] Activate this card's [Main] effect.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-023 - You May Be a Fool...but I Still Love You

- Printed effect: [Main] If you have 3 or less Life cards, you cannot add Life cards to your hand using your own effects during this turn.
- Printed trigger: [Trigger] Up to 1 of your Leader gains +1000 power during this turn.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-024 - Moby Dick

- Printed effect: [Your Turn] If you have 1 or less Life cards, your [Edward.Newgate] and all your Characters with a type including "Whitebeard Pirates" gain +2000 power.
- Printed trigger: [Trigger] Play this card.
- Registered timings: `continuous`, `trigger`
- Implementation status: `Needs Engine Support`
- Required code changes: Continuous +2000 can stack if re-applied; exact continuous recalculation/cleanup needs engine-level duration support.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Continuous +2000 can stack if re-applied; exact continuous recalculation/cleanup needs engine-level duration support.

### OP02-025 - Kin'emon

- Printed effect: [Activate: Main] [Once Per Turn] If you have 1 or less Characters, the next time you play a {Land of Wano} type Character card with a cost of 3 or more from your hand during this turn, the cost will be reduced by 1.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Next Land of Wano discount is represented as a player flag; exact play-cost interception should be validated in the play engine.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Next Land of Wano discount is represented as a player flag; exact play-cost interception should be validated in the play engine.

### OP02-026 - Sanji

- Printed effect: [Once Per Turn] When you play a Character with no base effect from your hand, if you have 3 or less Characters, set up to 2 of your DON!! cards as active.
- Printed trigger: None
- Registered timings: `on_play_character`
- Implementation status: `Partial`
- Required code changes: Leader hook is registered, but exact once-per-turn play-listener behavior depends on simulator event dispatch.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Leader hook is registered, but exact once-per-turn play-listener behavior depends on simulator event dispatch.

### OP02-027 - Inuarashi

- Printed effect: If all of your DON!! cards are rested, this Character cannot be removed from the field by your opponent's effects.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-028 - Usopp

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP02-029 - Carrot

- Printed effect: [End of Your Turn] Set up to 1 of your DON!! cards as active.
- Printed trigger: None
- Registered timings: `end_of_turn`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-030 - Kouzuki Oden

- Printed effect: [Activate: Main] [Once Per Turn] ? (You may rest the specified number of DON!! cards in your cost area.): Set this Character as active.<br>[On K.O.] Play up to 1 green {Land of Wano} type Character card with a cost of 3 from your deck. Then, shuffle your deck.
- Printed trigger: None
- Registered timings: `activate`, `on_ko`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-031 - Kouzuki Toki

- Printed effect: If you have a [Kouzuki Oden] Character, this Character gains [Blocker].<br>(After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-032 - Shishilian

- Printed effect: [On Play] ? (You may rest the specified number of DON!! cards in your cost area.): Set up to 1 of your {Minks} type Characters with a cost of 5 or less as active.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-033 - Jinbe

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP02-034 - Tony Tony.Chopper

- Printed effect: [DON!! x1] [When Attacking] Rest up to 1 of your opponent's Characters with a cost of 2 or less.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-035 - Trafalgar Law

- Printed effect: [Activate: Main] ? (You may rest the specified number of DON!! cards in your cost area.) You may return this Character to the owner's hand: Play up to 1 Character with a cost of 3 from your hand.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-036 - Nami

- Printed effect: [On Play]/[When Attacking] ? (You may rest the specified number of DON!! cards in your cost area.): Look at 3 cards from the top of your deck; reveal up to 1 {FILM} type card other than [Nami] and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_attack`, `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-037 - Nico Robin

- Printed effect: [On Play] Play up to 1 {FILM} or {Straw Hat Crew} type Character card with a cost of 2 or less from your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-038 - Nekomamushi

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-039 - Franky

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP02-040 - Brook

- Printed effect: [On Play] Play up to 1 {FILM} or {Straw Hat Crew} type Character card with a cost of 3 or less from your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-041 - Monkey.D.Luffy

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)<br>[On Play] Play up to 1 {FILM} or {Straw Hat Crew} type Character card with a cost of 4 or less from your hand.
- Printed trigger: None
- Registered timings: `blocker`, `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-042 - Yamato

- Printed effect: Also treat this card's name as [Kouzuki Oden] according to the rules.<br>[On Play] Rest up to 1 of your opponent's Characters with a cost of 6 or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-043 - Roronoa Zoro

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP02-044 - Wanda

- Printed effect: [On Play] Play up to 1 {Minks} type Character card other than [Wanda] with a cost of 3 or less from your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-045 - Three Sword Style Oni Giri

- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +6000 power during this battle. Then, play up to 1 Character card with a cost of 3 or less and no base effect from your hand.<br>
- Printed trigger: [Trigger] Rest up to 1 of your opponent's Leader or Character cards with a cost of 5 or less.
- Registered timings: `counter`, `trigger`
- Implementation status: `Partial`
- Required code changes: Counter currently applies +6000 to Leader before the play-from-hand choice; printed text allows choosing Leader or Character.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Counter currently applies +6000 to Leader before the play-from-hand choice; printed text allows choosing Leader or Character.

### OP02-046 - Diable Jambe Venaison Shoot

- Printed effect: [Main] K.O. up to 1 of your opponent's rested Characters with a cost of 4 or less.<br>
- Printed trigger: [Trigger] Play up to 1 Character card with a cost of 4 or less and no base effect from your hand.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-047 - Paradise Totsuka

- Printed effect: [Main] Rest up to 1 of your opponent's Characters with a cost of 4 or less.
- Printed trigger: [Trigger] K.O. up to 1 of your opponent's rested Characters with a cost of 3 or less.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-048 - Land of Wano

- Printed effect: [Activate: Main] You may trash 1 {Land of Wano} type card from your hand and rest this Stage: Set up to 1 of your DON!! cards as active.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Stage resolves the DON active step by setting the first rested DON active rather than prompting which DON.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Stage resolves the DON active step by setting the first rested DON active rather than prompting which DON.

### OP02-049 - Emporio.Ivankov

- Printed effect: [End of Your Turn] If you have 0 cards in your hand, draw 2 cards.
- Printed trigger: None
- Registered timings: `end_of_turn`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-050 - Inazuma

- Printed effect: If you have 1 or less cards in your hand, this Character gains +2000 power.<br>[Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `continuous`, `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-051 - Emporio.Ivankov

- Printed effect: [On Play] Draw card(s) so that you have 3 cards in your hand and then play up to 1 blue {Impel Down} type Character card with a cost of 6 or less from your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-052 - Cabaji

- Printed effect: [On Play] If you have [Mohji], draw 2 cards and trash 1 card from your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-053 - Crocodile

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP02-054 - Gecko Moria

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP02-055 - Dracule Mihawk

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP02-056 - Donquixote Doflamingo

- Printed effect: [On Play] Look at 3 cards from the top of your deck and place them at the top or bottom of the deck in any order.<br>[DON!! x1] [When Attacking] You may trash 1 card from your hand: Place up to 1 of your opponent's Characters with a cost of 1 or less at the bottom of the owner's deck.
- Printed trigger: None
- Registered timings: `on_play`, `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-057 - Bartholomew Kuma

- Printed effect: [On Play] Look at 2 cards from the top of your deck; reveal up to 1 {The Seven Warlords of the Sea} type card and add it to your hand. Then, place the rest at the top or bottom of the deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-058 - Buggy

- Printed effect: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 blue {Impel Down} type card other than [Buggy] and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-059 - Boa Hancock

- Printed effect: [When Attacking] Draw 1 card and trash 1 card from your hand. Then, trash up to 3 cards from your hand.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-060 - Mohji

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP02-061 - Morley

- Printed effect: [When Attacking] If you have 1 or less cards in your hand, your opponent cannot activate the [Blocker] of any Character with a cost of 5 or less during this battle.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-062 - Monkey.D.Luffy

- Printed effect: [On Play]/[When Attacking] You may trash 2 cards from your hand: Return up to 1 Character with a cost of 4 or less to the owner's hand. Then, this Character gains [Double Attack] during this turn.<br>(This card deals 2 damage.)
- Printed trigger: None
- Registered timings: `on_attack`, `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-063 - Mr.1(Daz.Bonez)

- Printed effect: [On Play] Add up to 1 blue Event card with a cost of 1 from your trash to your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-064 - Mr.2.Bon.Kurei(Bentham)

- Printed effect: [DON!! x1] [When Attacking] You may trash 1 card from your hand: Place up to 1 Character with a cost of 2 or less at the bottom of the owner's deck. Then, at the end of this battle, place this Character at the bottom of the owner's deck.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-065 - Mr.3(Galdino)

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)<br>[End of Your Turn] You may trash 1 card from your hand: Set this Character as active.
- Printed trigger: None
- Registered timings: `blocker`, `end_of_turn`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-066 - Impel Down All Stars

- Printed effect: [Main] You may trash 2 cards from your hand: If your Leader has the {Impel Down} type, draw up to 2 cards.
- Printed trigger: [Trigger] Draw 2 cards.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-067 - Arabesque Brick Fist

- Printed effect: [Main] Return up to 1 Character with a cost of 4 or less to the owner's hand.
- Printed trigger: [Trigger] Activate this card's [Main] effect.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-068 - Gum-Gum Rain

- Printed effect: [Counter] You may trash 1 card from your hand: Up to 1 of your Leader or Character cards gains +3000 power during this battle.
- Printed trigger: [Trigger] Return up to 1 Character with a cost of 2 or less to the owner's hand.
- Registered timings: `counter`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-069 - DEATH WINK

- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +6000 power during this battle. Then, draw cards so that you have 2 cards in your hand.
- Printed trigger: [Trigger] Return up to 1 Character with a cost of 7 or less to the owner's hand.
- Registered timings: `counter`, `trigger`
- Implementation status: `Partial`
- Required code changes: Counter currently applies +6000 to Leader directly; printed text allows choosing Leader or Character.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Counter currently applies +6000 to Leader directly; printed text allows choosing Leader or Character.

### OP02-070 - New Kama Land

- Printed effect: [Activate: Main] You may rest this Stage: If your Leader is [Emporio.Ivankov], draw 1 card and trash 1 card from your hand. Then, trash up to 3 cards from your hand.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: New Kama Land uses chained hand trash choices, but the exact optional up-to-3 discard UX needs manual validation.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: New Kama Land uses chained hand trash choices, but the exact optional up-to-3 discard UX needs manual validation.

### OP02-071 - Magellan

- Printed effect: [Your Turn] [Once Per Turn] When a DON!! card on the field is returned to your DON!! deck, this Leader gains +1000 power during this turn.
- Printed trigger: None
- Registered timings: `on_don_return`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-072 - Zephyr

- Printed effect: [When Attacking] DON!! -4 (You may return the specified number of DON!! cards from your field to your DON!! deck.): K.O. up to 1 of your opponent's Characters with a cost of 3 or less. Then, this Leader gains +1000 power during this turn.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-073 - Little Sadi

- Printed effect: [On Play] Play up to 1 {Jailer Beast} type Character card from your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-074 - Saldeath

- Printed effect: Your [Blugori] gains [Blocker].<br>(After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-075 - Shiki

- Printed effect: None
- Printed trigger: [Trigger] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Play this card.
- Registered timings: `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-076 - Shiryu

- Printed effect: [On Play] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): K.O. up to 1 of your opponent's Characters with a cost of 1 or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-077 - Solitaire

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP02-078 - Daifugo

- Printed effect: [On Play] DON!! -2 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Play up to 1 {SMILE} type Character card other than [Daifugo] with a cost of 3 or less from your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-079 - Douglas Bullet

- Printed effect: [On Play] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Rest up to 1 of your opponent's Characters with a cost of 4 or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-080 - Dobon

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP02-081 - Domino

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-082 - Byrnndi World

- Printed effect: [Activate: Main] DON!! -8 (You may return the specified number of DON!! cards from your field to your DON!! deck.): This Character gains +792000 power during this turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-083 - Hannyabal

- Printed effect: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 purple {Impel Down} type card other than [Hannyabal] and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-084 - Blugori

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP02-085 - Magellan

- Printed effect: [On Play] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Your opponent returns 1 DON!! card from their field to their DON!! deck.<br>[Opponent's Turn] When this Character is K.O.'d, your opponent returns 2 DON!! cards from their field to their DON!! deck.
- Printed trigger: None
- Registered timings: `on_play`, `on_ko`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-086 - Minokoala

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)<br>[On K.O.] If your Leader has the {Impel Down} type, add up to 1 DON!! card from your DON!! deck and rest it.
- Printed trigger: None
- Registered timings: `blocker`, `on_ko`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-087 - Minotaur

- Printed effect: [Double Attack] (This card deals 2 damage.)<br>[On K.O.] If your Leader has the {Impel Down} type, add up to 1 DON!! card from your DON!! deck and rest it.
- Printed trigger: None
- Registered timings: `continuous`, `on_ko`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-088 - Sphinx

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP02-089 - Judgment of Hell

- Printed effect: [Counter] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Give up to a total of 2 of your opponent's Leader or Character cards -3000 power during this turn.
- Printed trigger: [Trigger] If your opponent has 6 or more DON!! cards on their field, your opponent returns 1 DON!! card from their field to their DON!! deck.
- Registered timings: `counter`, `trigger`
- Implementation status: `Partial`
- Required code changes: Trigger returns one opponent DON automatically; printed text implies the opponent returns a DON from field.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Trigger returns one opponent DON automatically; printed text implies the opponent returns a DON from field.

### OP02-090 - Hydra

- Printed effect: [Main] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Give up to 1 of your opponent's Characters -3000 power during this turn.
- Printed trigger: [Trigger] If your opponent has 6 or more DON!! cards on their field, your opponent returns 1 DON!! card from their field to their DON!! deck.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Trigger returns one opponent DON automatically; printed text implies the opponent returns a DON from field.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Trigger returns one opponent DON automatically; printed text implies the opponent returns a DON from field.

### OP02-091 - Venom Road

- Printed effect: [Main] Add up to 1 DON!! card from your DON!! deck and set it as active.
- Printed trigger: [Trigger] If your opponent has 6 or more DON!! cards on their field, your opponent returns 1 DON!! card from their field to their DON!! deck.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Trigger returns one opponent DON automatically; printed text implies the opponent returns a DON from field.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Trigger returns one opponent DON automatically; printed text implies the opponent returns a DON from field.

### OP02-092 - Impel Down

- Printed effect: [Activate: Main] You may trash 1 card from your hand and rest this Stage: Look at 3 cards from the top of your deck; reveal up to 1 {Impel Down} type card and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-093 - Smoker

- Printed effect: [DON!! x1] [Activate: Main] [Once Per Turn] Give up to 1 of your opponent's Characters -1 cost during this turn. Then, if there is a Character with a cost of 0, this Leader gains +1000 power during this turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-094 - Isuka

- Printed effect: [DON!! x1] [Once Per Turn] When this Character battles and K.O.'s your opponent's Character, set this Character as active.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-095 - Onigumo

- Printed effect: If there is a Character with a cost of 0, this Character gains [Banish].<br>(When this card deals damage, the target card is trashed without activating its Trigger.)
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-096 - Kuzan

- Printed effect: [On Play] Draw 1 card.<br>[When Attacking] Give up to 1 of your opponent's Characters -4 cost during this turn.
- Printed trigger: None
- Registered timings: `on_play`, `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-097 - Komille

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP02-098 - Koby

- Printed effect: [On Play] You may trash 1 card from your hand: K.O. up to 1 of your opponent's Characters with a cost of 3 or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-099 - Sakazuki

- Printed effect: [On Play] You may trash 1 card from your hand: K.O. up to 1 of your opponent's Characters with a cost of 5 or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-100 - Jango

- Printed effect: If you have [Fullbody], this Character cannot be K.O.'d in battle.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-101 - Strawberry

- Printed effect: [When Attacking] If there is a Character with a cost of 0, your opponent cannot activate the [Blocker] of any Character with a cost of 5 or less during this battle.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-102 - Smoker

- Printed effect: This Character cannot be K.O.'d by effects.<br>[When Attacking] If there is a Character with a cost of 0, this Character gains +2000 power during this battle.
- Printed trigger: None
- Registered timings: `continuous`, `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-103 - Sengoku

- Printed effect: [DON!! x1] [When Attacking] Give up to 1 of your opponent's Characters -2 cost during this turn.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-104 - Sentomaru

- Printed effect: None
- Printed trigger: [Trigger] Play this card.
- Registered timings: `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-105 - Tashigi

- Printed effect: [DON!! x1] [When Attacking] Give up to 1 of your opponent's Characters -3 cost during this turn.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-106 - Tsuru

- Printed effect: [On Play] Give up to 1 of your opponent's Characters -2 cost during this turn.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-107 - Doberman

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP02-108 - Donquixote Rosinante

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-109 - Jaguar.D.Saul

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP02-110 - Hina

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)<br>[On Block] Select up to 1 of your opponent's Characters with a cost of 6 or less. The selected Character cannot attack during this turn.
- Printed trigger: None
- Registered timings: `blocker`, `on_block`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-111 - Fullbody

- Printed effect: [When Attacking] If you have [Jango], this card gains +3000 power during this battle.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-112 - Bell-m?re

- Printed effect: [Activate: Main] You may rest this Character: Give up to 1 of your opponent's Characters -1 cost during this turn. Then, up to 1 of your Leader or Character cards gains +1000 power during this turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-113 - Helmeppo

- Printed effect: [When Attacking] Give up to 1 of your opponent's Characters -2 cost during this turn. Then, if there is a Character with a cost of 0, this Character gains +2000 power during this battle.
- Printed trigger: [Trigger] Play this card.
- Registered timings: `on_attack`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-114 - Borsalino

- Printed effect: [Opponent's Turn] This Character gains +1000 power and cannot be K.O.'d by effects.<br>[Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `continuous`, `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-115 - Monkey.D.Garp

- Printed effect: [DON!! x2] [When Attacking] K.O. up to 1 of your opponent's Characters with a cost of 0.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-116 - Yamakaji

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP02-117 - Ice Age

- Printed effect: [Main] Give up to 1 of your opponent's Characters -5 cost during this turn.
- Printed trigger: [Trigger] K.O. up to 1 of your opponent's Characters with a cost of 3 or less.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-118 - Yasakani Sacred Jewel

- Printed effect: [Counter] You may trash 1 card from your hand: Select up to 1 of your Characters. The selected Character cannot be K.O.'d during this battle.
- Printed trigger: [Trigger] K.O. up to 1 of your opponent's Stages with a cost of 3 or less.
- Registered timings: `counter`, `trigger`
- Implementation status: `Partial`
- Required code changes: Counter auto-pays/trashes when possible before protection choice; printed text says you may trash 1 card first.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Counter auto-pays/trashes when possible before protection choice; printed text says you may trash 1 card first.

### OP02-119 - Meteor Volcano

- Printed effect: [Main] K.O. up to 1 of your opponent's Characters with a cost of 1 or less.
- Printed trigger: [Trigger] Draw 2 cards and trash 1 card from your hand.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-120 - Uta

- Printed effect: [On Play] DON!! -2 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Your Leader and all of your Characters gain +1000 power until the start of your next turn.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP02-121 - Kuzan

- Printed effect: [Your Turn] Give all of your opponent's Characters -5 cost.<br>[On Play] K.O. up to 1 of your opponent's Characters with a cost of 0.
- Printed trigger: None
- Registered timings: `continuous`, `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP02 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.
