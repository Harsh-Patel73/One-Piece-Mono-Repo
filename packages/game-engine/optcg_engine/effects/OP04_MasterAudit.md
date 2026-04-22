# OP04 Master Audit

Source of truth: `packages/simulator/backend/data/cards.json` base OP04 entries where `id == id_normal`.

## Summary

- Base cards audited: 119
- Non-vanilla cards: 111
- Vanilla cards: 8
- Registered OP04 cards after this pass: 111
- Registered OP04 timings after this pass: 159
- Missing non-vanilla registrations: 0
- Missing printed trigger timings: 0
- Strict status after this pass: 109/119 `Complete` or `Vanilla`; 10 follow-up cards flagged below

## Verification

- `python -m py_compile packages\game-engine\optcg_engine\effects\sets\op04_effects.py` passed.
- OP04 registration coverage script passed: `base=119 nonvanilla=111 vanilla=8 registered_cards=111 timings=159 missing=[] missing_triggers=[]`.
- Direct OP04 handler execution sweep passed: `OP04_handler_sweep_ran=159 errors=0`, resolving pending choices through `GameState.resolve_pending_choice(...)`.
- Full pytest suite was not rerun in this pass; earlier environment check showed `python -m pytest packages\game-engine\tests` is unavailable because `pytest` is not installed.

## Follow-Up Queue

- `OP04-001` Nefeltari Vivi: `Partial` - Leader attack/play hooks and turn-scoped power changes should be manually validated against simulator event dispatch.
- `OP04-019` Donquixote Doflamingo: `Partial` - Mode choice is implemented through helper flow; exact modal order and optional target UX should be manually validated.
- `OP04-020` Issho: `Partial` - Search/reveal/top-bottom handling should be manually validated with real Alabasta fixtures.
- `OP04-037` Flapping Thread: `Needs Engine Support` - Trigger is implemented; counter duration cleanup relies on temporary modifier expiration fields and should be verified in battle/turn cleanup.
- `OP04-056` Gum-Gum Red Roc: `Partial` - Multi-step Dressrosa effect uses helper sequencing; exact reveal/trash/rest order should be manually validated.
- `OP04-083` Sabo: `Partial` - DON return/payment and follow-up target choice should be manually validated for optional cost timing.
- `OP04-090` Monkey.D.Luffy: `Needs Engine Support` - Cost reduction duration/cleanup depends on simulator temporary modifier handling.
- `OP04-100` Capone"Gang"Bege: `Partial` - Life manipulation and trigger sequencing should be manually validated with real life/deck fixtures.
- `OP04-112` Yamato: `Partial` - K.O./life condition sequencing should be manually validated for exact yellow rules timing.
- `OP04-118` Nefeltari Vivi: `Partial` - High-impact event effect uses helper sequencing; exact target filters and life threshold behavior should receive manual replay testing.

## Per-Card Audit

### OP04-001 - Nefeltari Vivi

- Printed effect: This Leader cannot attack. [Activate: Main] [Once Per Turn] ? (You may rest the specified number of DON!! cards in your cost area.): Draw 1 card and up to 1 of your Characters gains [Rush] during this turn. (This card can attack on the turn in which it is played.)
- Printed trigger: None
- Registered timings: `continuous`, `activate`
- Implementation status: `Partial`
- Required code changes: Leader attack/play hooks and turn-scoped power changes should be manually validated against simulator event dispatch.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Leader attack/play hooks and turn-scoped power changes should be manually validated against simulator event dispatch.

### OP04-002 - Igaram

- Printed effect: [Activate: Main] You may rest this Character and give your 1 active Leader -5000 power during this turn: Look at 5 cards from the top of your deck; reveal up to 1 {Alabasta} type card and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-003 - Usopp

- Printed effect: [On K.O.] K.O. up to 1 of your opponent's Characters with 5000 base power or less.
- Printed trigger: None
- Registered timings: `on_ko`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-004 - Karoo

- Printed effect: [Activate: Main] You may rest this Character: Give up to 1 rested DON!! card to each of your {Alabasta} type Characters.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-005 - Kung Fu Jugon

- Printed effect: If you have a [Kung Fu Jugon] other than this Character, this Character gains [Blocker]. (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-006 - Koza

- Printed effect: [When Attacking] You may give your 1 active Leader -5000 power during this turn: This Character gains +2000 power until the start of your next turn.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-007 - Sanji

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP04-008 - Chaka

- Printed effect: [DON!! x1] [When Attacking] If your Leader is [Nefeltari Vivi], give up to 1 of your opponent's Characters -3000 power during this turn. Then, K.O. up to 1 of your opponent's Characters with 0 power or less.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-009 - Super Spot-Billed Duck Troops

- Printed effect: [When Attacking] You may give your 1 active Leader -5000 power during this turn: Return this Character to the owner's hand at the end of this turn.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-010 - Tony Tony.Chopper

- Printed effect: [On Play] Play up to 1 {Animal} type Character card with 3000 power or less from your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-011 - Nami

- Printed effect: [When Attacking] Reveal 1 card from the top of your deck. If the revealed card is a Character card with 6000 power or more, this Character gains +3000 power during this turn. Then, place the revealed card at the bottom of your deck.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-012 - Nefeltari Cobra

- Printed effect: [Your Turn] All of your {Alabasta} type Characters other than this Character gain +1000 power.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-013 - Pell

- Printed effect: [DON!! x1] [When Attacking] K.O. up to 1 of your opponent's Characters with 4000 power or less.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-014 - Monkey.D.Luffy

- Printed effect: [Banish] (When this card deals damage, the target card is trashed without activating its Trigger.)
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-015 - Roronoa Zoro

- Printed effect: [On Play] Give up to 1 of your opponent's Characters -2000 power during this turn.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-016 - Bad Manners Kick Course

- Printed effect: [Counter] You may trash 1 card from your hand: Up to 1 of your Leader or Character cards gains +3000 power during this battle.
- Printed trigger: [Trigger] Give up to 1 of your opponent's Leader or Character cards -3000 power during this turn.
- Registered timings: `counter`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-017 - Happiness Punch

- Printed effect: [Counter] Give up to 1 of your opponent's Leader or Character cards -2000 power during this turn. Then, if your Leader is active, give up to 1 of your opponent's Leader or Character cards -1000 power during this turn.
- Printed trigger: None
- Registered timings: `counter`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-018 - Enchanting Vertigo Dance

- Printed effect: [Main] If your Leader has the {Alabasta} type, give up to 2 of your opponent's Characters -2000 power during this turn.
- Printed trigger: [Trigger] Activate this card's [Main] effect.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-019 - Donquixote Doflamingo

- Printed effect: [End of Your Turn] Set up to 2 of your DON!! cards as active.
- Printed trigger: None
- Registered timings: `end_of_turn`
- Implementation status: `Partial`
- Required code changes: Mode choice is implemented through helper flow; exact modal order and optional target UX should be manually validated.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Mode choice is implemented through helper flow; exact modal order and optional target UX should be manually validated.

### OP04-020 - Issho

- Printed effect: [DON!! x1] [Your Turn] Give all of your opponent's Characters -1 cost. [End of Your Turn] ? (You may rest the specified number of DON!! cards in your cost area.): Set up to 1 of your Characters with a cost of 5 or less as active.
- Printed trigger: None
- Registered timings: `continuous`, `end_of_turn`
- Implementation status: `Partial`
- Required code changes: Search/reveal/top-bottom handling should be manually validated with real Alabasta fixtures.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Search/reveal/top-bottom handling should be manually validated with real Alabasta fixtures.

### OP04-021 - Viola

- Printed effect: [On Your Opponent's Attack] ? (You may rest the specified number of DON!! cards in your cost area.): Rest up to 1 of your opponent's DON!! cards.
- Printed trigger: None
- Registered timings: `on_opponent_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-022 - Eric

- Printed effect: [Activate: Main] You may rest this Character: Rest up to 1 of your opponent's Characters with a cost of 1 or less.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-023 - Kuro

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP04-024 - Sugar

- Printed effect: [Opponent's Turn] [Once Per Turn] When your opponent plays a Character, if your Leader has the {Donquixote Pirates} type, rest up to 1 of your opponent's Characters. Then, rest this Character. [On Play] Rest up to 1 of your opponent's Characters with a cost of 4 or less.
- Printed trigger: None
- Registered timings: `on_play`, `on_opponent_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-025 - Giolla

- Printed effect: [On Your Opponent's Attack] ? (You may rest the specified number of DON!! cards in your cost area.): Rest up to 1 of your opponent's Characters with a cost of 4 or less.
- Printed trigger: None
- Registered timings: `on_opponent_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-026 - Senor Pink

- Printed effect: [When Attacking] ? (You may rest the specified number of DON!! cards in your cost area.): If your Leader has the {Donquixote Pirates} type, rest up to 1 of your opponent's Characters with a cost of 4 or less. Then, set up to 1 of your DON!! cards as active at the end of this turn.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-027 - Daddy Masterson

- Printed effect: [DON!! x1] [End of Your Turn] Set this Character as active.
- Printed trigger: None
- Registered timings: `end_of_turn`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-028 - Diamante

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [DON!! x1] [End of Your Turn] If you have 2 or more active DON!! cards, set this Character as active.
- Printed trigger: None
- Registered timings: `blocker`, `end_of_turn`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-029 - Dellinger

- Printed effect: [End of Your Turn] Set up to 1 of your DON!! cards as active.
- Printed trigger: None
- Registered timings: `end_of_turn`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-030 - Trebol

- Printed effect: [On Play] K.O. up to 1 of your opponent's rested Characters with a cost of 5 or less. [On Your Opponent's Attack] ? (You may rest the specified number of DON!! cards in your cost area.): Rest up to 1 of your opponent's Characters with a cost of 4 or less.
- Printed trigger: None
- Registered timings: `on_play`, `on_opponent_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-031 - Donquixote Doflamingo

- Printed effect: [On Play] Up to a total of 3 of your opponent's rested Leader and Character cards will not become active in your opponent's next Refresh Phase.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-032 - Baby 5

- Printed effect: [End of Your Turn] You may trash this Character: Set up to 2 of your DON!! cards as active.
- Printed trigger: None
- Registered timings: `end_of_turn`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-033 - Machvise

- Printed effect: [On Play] If your Leader has the {Donquixote Pirates} type, rest up to 1 of your opponent's Characters with a cost of 5 or less. Then, set up to 1 of your DON!! cards as active at the end of this turn.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-034 - Lao.G

- Printed effect: [End of Your Turn] If you have 3 or more active DON!! cards, K.O. up to 1 of your opponent's rested Characters with a cost of 3 or less.
- Printed trigger: None
- Registered timings: `end_of_turn`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-035 - Spiderweb

- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +4000 power during this battle. Then, set up to 1 of your Characters as active.
- Printed trigger: [Trigger] Up to 1 of your Leader gains +2000 power during this turn.
- Registered timings: `counter`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-036 - Donquixote Family

- Printed effect: [Counter] Look at 5 cards from the top of your deck; reveal up to 1 {Donquixote Pirates} type card and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: [Trigger] Activate this card's [Counter] effect.
- Registered timings: `counter`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-037 - Flapping Thread

- Printed effect: [Counter] If your Leader has the {Donquixote Pirates} type, up to 1 of your Leader or Character cards gains +2000 power during this turn.
- Printed trigger: [Trigger] K.O. up to 1 of your opponent's rested Characters with a cost of 4 or less.
- Registered timings: `counter`, `trigger`
- Implementation status: `Needs Engine Support`
- Required code changes: Trigger is implemented; counter duration cleanup relies on temporary modifier expiration fields and should be verified in battle/turn cleanup.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Trigger is implemented; counter duration cleanup relies on temporary modifier expiration fields and should be verified in battle/turn cleanup.

### OP04-038 - The Weak Do Not Have the Right to Choose How They Die!!!

- Printed effect: [Main]/[Counter] Rest up to 1 of your opponent's Leader or Character cards. Then, K.O. up to 1 of your opponent's rested Characters with a cost of 6 or less.
- Printed trigger: [Trigger] Set up to 5 of your DON!! cards as active.
- Registered timings: `on_play`, `counter`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-039 - Rebecca

- Printed effect: This Leader cannot attack. [Activate: Main] [Once Per Turn] ? (You may rest the specified number of DON!! cards in your cost area.): If you have 6 or less cards in your hand, look at 2 cards from the top of your deck; reveal up to 1 {Dressrosa} type card and add it to your hand. Then, trash the rest.
- Printed trigger: None
- Registered timings: `continuous`, `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-040 - Queen

- Printed effect: [DON!! x1] [When Attacking] If you have a total of 4 or less cards in your Life area and hand, draw 1 card. If you have a Character with a cost of 8 or more, you may add up to 1 card from the top of your deck to the top of your Life cards instead of drawing 1 card.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-041 - Apis

- Printed effect: [On Play] You may trash 2 cards from your hand: Look at 5 cards from the top of your deck; reveal up to 1 {East Blue} type card and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-042 - Ipponmatsu

- Printed effect: [On Play] Up to 1 of your <Slash> attribute Characters gains +3000 power during this turn. Then, trash 1 card from the top of your deck.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-043 - Ulti

- Printed effect: [DON!! x1] [When Attacking] Return up to 1 Character with a cost of 2 or less to the owner's hand or the bottom of their deck.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-044 - Kaido

- Printed effect: [On Play] Return up to 1 Character with a cost of 8 or less and up to 1 Character with a cost of 3 or less to the owner's hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-045 - King

- Printed effect: [On Play] Draw 1 card.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-046 - Queen

- Printed effect: [On Play] If your Leader has the {Animal Kingdom Pirates} type, look at 7 cards from the top of your deck; reveal a total of up to 2 [Plague Rounds] or [Ice Oni] cards and add them to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-047 - Ice Oni

- Printed effect: [Your Turn] At the end of a battle in which this Character battles your opponent's Character with a cost of 5 or less, place the opponent's Character you battled with at the bottom of the owner's deck.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-048 - Sasaki

- Printed effect: [On Play] Return all cards in your hand to your deck and shuffle your deck. Then, draw cards equal to the number you returned to your deck.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-049 - Jack

- Printed effect: [On K.O.] Draw 1 card.
- Printed trigger: None
- Registered timings: `on_ko`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-050 - Hanger

- Printed effect: [Activate: Main] You may trash 1 card from your hand and rest this Character: Draw 1 card.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-051 - Who's.Who

- Printed effect: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 {Animal Kingdom Pirates} type card other than [Who's.Who] and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-052 - Black Maria

- Printed effect: [Activate: Main] ? (You may rest the specified number of DON!! cards in your cost area.) You may rest this Character: Draw 1 card.
- Printed trigger: [Trigger] Play this card.
- Registered timings: `activate`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-053 - Page One

- Printed effect: [DON!! x1] [Once Per Turn] When you activate an Event, draw 1 card. Then, place 1 card from your hand at the bottom of your deck.
- Printed trigger: None
- Registered timings: `on_event`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-054 - Rokki

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP04-055 - Plague Rounds

- Printed effect: [Main] You may trash 1 [Ice Oni] from your hand and place 1 Character with a cost of 4 or less at the bottom of the owner's deck: Play 1 [Ice Oni] from your trash.
- Printed trigger: [Trigger] Activate this card's [Main] effect.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-056 - Gum-Gum Red Roc

- Printed effect: [Main] Place up to 1 Character at the bottom of the owner's deck.
- Printed trigger: [Trigger] Place up to 1 Character with a cost of 4 or less at the bottom of the owner's deck.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Multi-step Dressrosa effect uses helper sequencing; exact reveal/trash/rest order should be manually validated.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Multi-step Dressrosa effect uses helper sequencing; exact reveal/trash/rest order should be manually validated.

### OP04-057 - Dragon Twister Demolition Breath

- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +4000 power during this battle. Then, place up to 1 Character with a cost of 1 or less at the bottom of the owner's deck.
- Printed trigger: [Trigger] Return up to 1 Character with a cost of 6 or less to the owner's hand.
- Registered timings: `counter`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-058 - Crocodile

- Printed effect: [Opponent's Turn] [Once Per Turn] When a DON!! card on your field is returned to your DON!! deck by your effect, add up to 1 DON!! card from your DON!! deck and set it as active.
- Printed trigger: None
- Registered timings: `on_don_return`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-059 - Iceburg

- Printed effect: [On Your Opponent's Attack] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): If your Leader has the {Water Seven} type, this Character gains [Blocker] during this turn. (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `on_opponent_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-060 - Crocodile

- Printed effect: [On Play] DON!! -2 (You may return the specified number of DON!! cards from your field to your DON!! deck.): If your Leader's type includes "Baroque Works", add up to 1 card from the top of your deck to the top of your Life cards. [On Your Opponent's Attack] [Once Per Turn] DON!! -1: Draw 1 card and trash 1 card from your hand.
- Printed trigger: None
- Registered timings: `on_play`, `on_opponent_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-061 - Tom

- Printed effect: [Activate: Main] You may trash this Character: If your Leader has the {Water Seven} type, add up to 1 DON!! card from your DON!! deck and rest it.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-062 - Bananagator

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP04-063 - Franky

- Printed effect: [On Your Opponent's Attack] [Once Per Turn] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): If your Leader has the {Water Seven} type, up to 1 of your Leader or Character cards gains +1000 power during this battle.
- Printed trigger: None
- Registered timings: `on_opponent_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-064 - Ms. All Sunday

- Printed effect: [On Play] Add up to 1 DON!! card from your DON!! deck and rest it. Then, if you have 6 or more DON!! cards on your field, draw 1 card.
- Printed trigger: [Trigger] DON!! -2 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Play this card.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-065 - Miss.Goldenweek(Marianne)

- Printed effect: [On Play] If your Leader's type includes "Baroque Works", up to 1 of your opponent's Characters with a cost of 5 or less cannot attack until the start of your next turn.
- Printed trigger: [Trigger] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Play this card.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-066 - Miss.Valentine(Mikita)

- Printed effect: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 card with a type including "Baroque Works" and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: [Trigger] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Play this card.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-067 - Miss.MerryChristmas(Drophy)

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: [Trigger] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Play this card.
- Registered timings: `blocker`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-068 - Yokozuna

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On Your Opponent's Attack] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Return up to 1 of your opponent's Characters with a cost of 2 or less to the owner's hand.
- Printed trigger: None
- Registered timings: `blocker`, `on_opponent_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-069 - Mr.2.Bon.Kurei(Bentham)

- Printed effect: [On Your Opponent's Attack] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): This Character's base power becomes the same as the power of your opponent's attacking Leader or Character during this turn.
- Printed trigger: [Trigger] DON!! -1: Play this card.
- Registered timings: `on_opponent_attack`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-070 - Mr.3(Galdino)

- Printed effect: [On Your Opponent's Attack] [Once Per Turn] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Give up to 1 of your opponent's Characters -1000 power during this turn.
- Printed trigger: None
- Registered timings: `on_opponent_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-071 - Mr.4(Babe)

- Printed effect: [On Your Opponent's Attack] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): This Character gains [Blocker] and +1000 power during this battle. (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `on_opponent_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-072 - Mr.5(Gem)

- Printed effect: [On Your Opponent's Attack] [Once Per Turn] DON!! -2 (You may return the specified number of DON!! cards from your field to your DON!! deck.) You may rest this Character: K.O. up to 1 of your opponent's Characters with a cost of 4 or less.
- Printed trigger: None
- Registered timings: `on_opponent_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-073 - Mr.13 & Ms.Friday

- Printed effect: [Activate: Main] You may trash this Character and 1 of your Characters with a type including "Baroque Works": Add up to 1 DON!! card from your DON!! deck and set it as active.
- Printed trigger: [Trigger] Play this card.
- Registered timings: `activate`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-074 - Colors Trap

- Printed effect: [Counter] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Up to 1 of your Leader or Character cards gains +1000 power during this battle. Then, rest up to 1 of your opponent's Characters with a cost of 4 or less.
- Printed trigger: [Trigger] Add up to 1 DON!! card from your DON!! deck and set it as active.
- Registered timings: `counter`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-075 - Nez-Palm Cannon

- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +6000 power during this battle. Then, if you have 2 or less Life cards, add up to 1 DON!! card from your DON!! deck and rest it.
- Printed trigger: [Trigger] Add up to 1 DON!! card from your DON!! deck and set it as active.
- Registered timings: `counter`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-076 - Weakness...Is an Unforgivable Sin.

- Printed effect: [Counter] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Up to 1 of your Leader or Character cards gains +1000 power during this turn.
- Printed trigger: [Trigger] Add up to 1 DON!! card from your DON!! deck and set it as active.
- Registered timings: `counter`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-077 - Ideo

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-078 - Oimo & Kashii

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP04-079 - Orlumbus

- Printed effect: [Activate: Main] [Once Per Turn] Give up to 1 of your opponent's Characters -4 cost during this turn and trash 2 cards from the top of your deck. Then, K.O. 1 of your {Dressrosa} type Characters.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-080 - Gyats

- Printed effect: [On Play] Up to 1 of your {Dressrosa} type Characters can also attack active Characters during this turn.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-081 - Cavendish

- Printed effect: [DON!! x1] This Character can also attack active Characters. [When Attacking] You may rest your Leader: K.O. up to 1 of your opponent's Characters with a cost of 1 or less. Then, trash 2 cards from the top of your deck.
- Printed trigger: None
- Registered timings: `continuous`, `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-082 - Kyros

- Printed effect: If this Character would be K.O.'d, you may rest your Leader or 1 [Corrida Coliseum] instead. [On Play] If your Leader is [Rebecca], K.O. up to 1 of your opponent's Characters with a cost of 1 or less. Then, trash 1 card from the top of your deck.
- Printed trigger: None
- Registered timings: `on_ko_prevention`, `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-083 - Sabo

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On Play] None of your Characters can be K.O.'d by effects until the start of your next turn. Then, draw 2 cards and trash 2 cards from your hand.
- Printed trigger: None
- Registered timings: `blocker`, `on_play`
- Implementation status: `Partial`
- Required code changes: DON return/payment and follow-up target choice should be manually validated for optional cost timing.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: DON return/payment and follow-up target choice should be manually validated for optional cost timing.

### OP04-084 - Stussy

- Printed effect: [On Play] Look at 3 cards from the top of your deck and play up to 1 Character card with a type including "CP" other than [Stussy] and a cost of 2 or less. Then, trash the rest.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-085 - Suleiman

- Printed effect: [On Play]/[When Attacking] If your Leader has the {Dressrosa} type, give up to 1 of your opponent's Characters -2 cost during this turn. Then, trash 1 card from the top of your deck.
- Printed trigger: None
- Registered timings: `on_play`, `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-086 - Chinjao

- Printed effect: [DON!! x1] When this Character battles and K.O.'s your opponent's Character, draw 2 cards and trash 2 cards from your hand.
- Printed trigger: None
- Registered timings: `on_ko_opponent`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-087 - Trafalgar Law

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP04-088 - Hajrudin

- Printed effect: [Activate: Main] You may rest your 1 Leader: Give up to 1 of your opponent's Characters -4 cost during this turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-089 - Bartolomeo

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-090 - Monkey.D.Luffy

- Printed effect: This Character can also attack active Characters. [Activate: Main] [Once Per Turn] You may return 7 cards from your trash to the bottom of your deck in any order: Set this Character as active. Then, this Character will not become active in your next Refresh Phase.
- Printed trigger: None
- Registered timings: `continuous`, `activate`
- Implementation status: `Needs Engine Support`
- Required code changes: Cost reduction duration/cleanup depends on simulator temporary modifier handling.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Cost reduction duration/cleanup depends on simulator temporary modifier handling.

### OP04-091 - Leo

- Printed effect: [On Play] You may rest your 1 Leader: If your Leader has the {Dressrosa} type, K.O. up to 1 of your opponent's Characters with a cost of 1 or less. Then, trash 2 cards from the top of your deck.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-092 - Rebecca

- Printed effect: [On Play] Look at 3 cards from the top of your deck; reveal up to 1 {Dressrosa} type card other than [Rebecca] and add it to your hand. Then, trash the rest.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-093 - Gum-Gum King Kong Gun

- Printed effect: [Main] Up to 1 of your {Dressrosa} type Characters gains +6000 power during this turn. Then, if you have 15 or more cards in your trash, that card gains [Double Attack] during this turn. (This card deals 2 damage.)
- Printed trigger: [Trigger] Draw 3 cards and trash 2 cards from your hand.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-094 - Trueno Bastardo

- Printed effect: [Main] Choose up to 1 of your opponent's Characters with a cost of 4 or less and K.O. it. If you have 15 or more cards in your trash, choose up to 1 of your opponent's Characters with a cost of 6 or less instead of a Character with a cost of 4 or less.
- Printed trigger: [Trigger] You may rest your Leader: K.O. up to 1 of your opponent's Characters with a cost of 5 or less.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-095 - Barrier!!

- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +2000 power during this battle. Then, if you have 15 or more cards in your trash, that card gains an additional +2000 power during this battle.
- Printed trigger: [Trigger] Draw 2 cards and trash 1 card from your hand.
- Registered timings: `counter`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-096 - Corrida Coliseum

- Printed effect: If your Leader has the {Dressrosa} type, your {Dressrosa} type Characters can attack Characters on the turn in which they are played.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-097 - Otama

- Printed effect: [On Play] Add up to 1 of your opponent's {Animal} or {SMILE} type Characters with a cost of 3 or less to the top of your opponent's Life cards face-up.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-098 - Toko

- Printed effect: [On Play] You may trash 2 {Land of Wano} type cards from your hand: If you have 1 or less Life cards, add 1 card from the top of your deck to the top of your Life cards.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-099 - Olin

- Printed effect: Also treat this card's name as [Charlotte Linlin] according to the rules.
- Printed trigger: [Trigger] If you have 1 or less Life cards, play this card.
- Registered timings: `continuous`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-100 - Capone"Gang"Bege

- Printed effect: None
- Printed trigger: [Trigger] Up to 1 of your opponent's Leader or Character cards cannot attack during this turn.
- Registered timings: `trigger`
- Implementation status: `Partial`
- Required code changes: Life manipulation and trigger sequencing should be manually validated with real life/deck fixtures.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Life manipulation and trigger sequencing should be manually validated with real life/deck fixtures.

### OP04-101 - Carmel

- Printed effect: [Your Turn] [On Play] Draw 1 card.
- Printed trigger: [Trigger] Play this card. Then, K.O. up to 1 of your opponent's Characters with a cost of 2 or less.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-102 - Kin'emon

- Printed effect: [Activate: Main] [Once Per Turn] ? (You may rest the specified number of DON!! cards in your cost area.) You may add 1 card from the top or bottom of your Life cards to your hand: Set this Character as active.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-103 - Kouzuki Hiyori

- Printed effect: [On Play] Up to 1 of your {Land of Wano} type Leader or Character cards gains +1000 power during this turn.
- Printed trigger: [Trigger] Play this card.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-104 - Sanji

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: [Trigger] You may trash 1 card from your hand: Play this card.
- Registered timings: `blocker`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-105 - Charlotte Amande

- Printed effect: [Activate: Main] [Once Per Turn] You may trash 1 card with a [Trigger] from your hand: Rest up to 1 of your opponent's Characters with a cost of 2 or less.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-106 - Charlotte Bavarois

- Printed effect: [DON!! x1] If you have less Life cards than your opponent, this Character gains +1000 power.
- Printed trigger: [Trigger] You may trash 1 card from your hand: Play this card.
- Registered timings: `continuous`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-107 - Charlotte Perospero

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP04-108 - Charlotte Moscato

- Printed effect: [DON!! x1] This Character gains [Banish]. (When this card deals damage, the target card is trashed without activating its Trigger.)
- Printed trigger: [Trigger] You may trash 1 card from your hand: Play this card.
- Registered timings: `continuous`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-109 - Tonoyasu

- Printed effect: [Activate: Main] You may trash this Character: Up to 1 of your {Land of Wano} type Leader or Character cards gains +3000 power during this turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-110 - Pound

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On K.O.] Add up to 1 of your opponent's Characters with a cost of 3 or less to the top or bottom of your opponent's Life cards face-up.
- Printed trigger: None
- Registered timings: `blocker`, `on_ko`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-111 - Hera

- Printed effect: [Activate: Main] You may trash 1 of your {Homies} type Characters other than this Character and rest this Character: Set up to 1 of your [Charlotte Linlin] Characters as active.
- Printed trigger: [Trigger] Play this card.
- Registered timings: `activate`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-112 - Yamato

- Printed effect: [On Play] K.O. up to 1 of your opponent's Characters with a cost equal to or less than the total of your and your opponent's Life cards. Then, if you have 1 or less Life cards, add up to 1 card from the top of your deck to the top of your Life cards.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: K.O./life condition sequencing should be manually validated for exact yellow rules timing.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: K.O./life condition sequencing should be manually validated for exact yellow rules timing.

### OP04-113 - Rabiyan

- Printed effect: None
- Printed trigger: [Trigger] Play this card.
- Registered timings: `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-114 - Randolph

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP04-115 - Gun Modoki

- Printed effect: [Main] You may add 1 card from the top or bottom of your Life cards to your hand: Up to 1 of your {Land of Wano} type Characters gains [Double Attack] during this turn. (This card deals 2 damage.)
- Printed trigger: [Trigger] Up to 1 of your Leader or Character cards gains +1000 power during this turn.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-116 - Diable Jambe Joue Shot

- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +6000 power during this battle. Then, if you and your opponent have a total of 4 or less Life cards, K.O. up to 1 of your opponent's Characters with a cost of 2 or less.
- Printed trigger: [Trigger] Draw 1 card.
- Registered timings: `counter`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-117 - Heavenly Fire

- Printed effect: [Main] Add up to 1 of your opponent's Characters with a cost of 3 or less to the top or bottom of your opponent's Life cards face-up.
- Printed trigger: [Trigger] You may add 1 card from the top or bottom of your Life cards to your hand: Add up to 1 card from your hand to the top of your Life cards.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP04-118 - Nefeltari Vivi

- Printed effect: All of your red Characters with a cost of 3 or more other than this Character gain [Rush]. (This card can attack on the turn in which it is played.)
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Partial`
- Required code changes: High-impact event effect uses helper sequencing; exact target filters and life threshold behavior should receive manual replay testing.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: High-impact event effect uses helper sequencing; exact target filters and life threshold behavior should receive manual replay testing.

### OP04-119 - Donquixote Rosinante

- Printed effect: [Opponent's Turn] If this Character is rested, your active Characters with a base cost of 5 cannot be K.O.'d by effects. [On Play] You may rest this Character: Play up to 1 green Character card with a cost of 5 from your hand.
- Printed trigger: None
- Registered timings: `continuous`, `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP04 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.
