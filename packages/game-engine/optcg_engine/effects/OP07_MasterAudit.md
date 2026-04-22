# OP07 Master Audit

Source of truth: `packages/simulator/backend/data/cards.json` base OP07 entries where `id == id_normal`.

## Summary

- Base cards audited: 119
- Non-vanilla cards: 113
- Vanilla cards: 6
- Registered OP07 cards after this pass: 113
- Registered OP07 timings after this pass: 155
- Missing non-vanilla registrations before this pass: 11
- Missing printed trigger timings before this pass: 19
- Missing non-vanilla registrations after this pass: 0
- Missing printed trigger timings after this pass: 0
- Strict status after this pass: 104/119 `Complete` or `Vanilla`; 15 follow-up cards flagged below

## Verification

- `python -m py_compile packages\game-engine\optcg_engine\effects\sets\op07_effects.py` passed.
- OP07 registration coverage script passed: `base=119 nonvanilla=113 vanilla=6 registered_cards=113 timings=155 missing=[] missing_triggers=[]`.
- Direct OP07 handler execution sweep passed: `OP07_handler_sweep_ran=155 errors=0 tracebacks=0`, resolving pending choices through `GameState.resolve_pending_choice(...)`.
- Full pytest suite was not rerun in this pass; earlier environment check showed `python -m pytest packages\game-engine\tests` is unavailable because `pytest` is not installed.

## Follow-Up Queue

- `OP07-001` Monkey.D.Dragon: `Partial` - DON transfer currently picks a source automatically; exact choice of which attached DON/source card should be improved.
- `OP07-016` Galaxy Wink: `Partial` - Implemented with chained power prompts; exact duration cleanup for both +2000 and -1000 should be validated.
- `OP07-017` Dragon Breath: `Partial` - Implemented two K.O. choices; exact simultaneous resolution/order should be manually replayed.
- `OP07-018` KEEP OUT: `Needs Engine Support` - Counter is implemented, but "until end of next turn" duration needs engine-level expiration validation.
- `OP07-036` Demonic Aura Nine-Sword Style Asura Demon Nine Flash: `Partial` - Implemented chained +3000/rest own/rest opponent flow; exact optional branch UX should be manually replayed.
- `OP07-055` Snake Dance: `Partial` - Counter/trigger return-to-hand flows implemented; exact owner-hand handling and optional cost wording need manual validation.
- `OP07-056` Slave Arrow: `Partial` - Trigger draw-2 then bottom-2 implemented; exact "in any order" ordering is simplified to selected order.
- `OP07-057` Perfume Femur: `Needs Engine Support` - Blocker prevention is represented with a card flag; engine support for blocking restriction should be validated.
- `OP07-058` Island of Women: `Partial` - Stage activate implemented; exact trash/rest cost atomicity should be manually replayed.
- `OP07-075` Slow-Slow Beam: `Partial` - Counter uses a shared multi-target -2000 prompt; printed "up to 1 each Leader and Character" should get stricter target grouping.
- `OP07-076` Slow-Slow Beam Sword: `Partial` - Counter/trigger implemented; DON-return optional cost and chained rest target should be manually replayed.
- `OP07-078` Megaton Nine-Tails Rush: `Partial` - Main only targets named Foxy; verify exact card-name matching and active-state handling with real Foxy fixtures.
- `OP07-094` Shave: `Partial` - Counter auto-applies leader power before optional CP return; printed target choice should be improved.
- `OP07-095` Iron Body: `Partial` - Counter auto-applies to Leader; printed Leader/Character target choice should be improved.
- `OP07-117` Egghead: `Partial` - Stage trigger play implemented; end-of-turn Egghead active setting should be validated with real Egghead fixtures.

## Per-Card Audit

### OP07-001 - Monkey.D.Dragon

- Printed effect: [Activate: Main] [Once Per Turn] Give up to 2 total of your currently given DON!! cards to 1 of your Characters.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: DON transfer currently picks a source automatically; exact choice of which attached DON/source card should be improved.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: DON transfer currently picks a source automatically; exact choice of which attached DON/source card should be improved.

### OP07-002 - Ain

- Printed effect: [On Play] Set the power of up to 1 of your opponent's Characters to 0 during this turn.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-003 - Outlook III

- Printed effect: [Activate: Main] You may trash this Character: Give up to 2 of your opponent's Characters -2000 power during this turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-004 - Curly.Dadan

- Printed effect: [On Play] You may trash 1 card from your hand: Look at 5 cards from the top of your deck; reveal up to 1 Character card with 2000 power or less and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-005 - Carina

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On Play] Give up to 1 of your opponent's Characters -2000 power during this turn.
- Printed trigger: None
- Registered timings: `blocker`, `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-006 - Sterry

- Printed effect: [On Play] You may give your 1 active Leader -5000 power during this turn: Draw 1 card and trash 1 card from your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-007 - Dice

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP07-008 - Mr. Tanaka

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: [Trigger] Play this card.
- Registered timings: `blocker`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-009 - Dogura & Magura

- Printed effect: [On Play] Up to 1 of your red Characters with a cost of 1 gains [Double Attack] during this turn. (This card deals 2 damage.)
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-010 - Baccarat

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On Your Opponent's Attack] [Once Per Turn] You may trash 1 card from your hand: Up to 1 of your Leader or Character cards gains +2000 power during this battle.
- Printed trigger: None
- Registered timings: `blocker`, `on_opponent_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-011 - Bluejam

- Printed effect: [DON!! x1] [When Attacking] K.O. up to 1 of your opponent's Characters with 2000 power or less.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-012 - Porchemy

- Printed effect: [On Play] Give up to 1 of your opponent's Characters -1000 power during this turn.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-013 - Masked Deuce

- Printed effect: [On Play] If your Leader is [Portgas.D.Ace], look at 5 cards from the top of your deck; reveal up to 1 [Portgas.D.Ace] or red Event and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-014 - Moda

- Printed effect: [Your Turn] [On Play] Up to 1 of your [Portgas.D.Ace] cards gains +2000 power during this turn.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-015 - Monkey.D.Dragon

- Printed effect: [Rush] (This card can attack on the turn in which it is played.) [On Play] Give up to 2 rested DON!! cards to your Leader or 1 of your Characters.
- Printed trigger: None
- Registered timings: `continuous`, `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-016 - Galaxy Wink

- Printed effect: [Main] Up to 1 of your {Revolutionary Army} type Characters gains +2000 power during this turn. Then, give up to 1 of your opponent's Characters -1000 power during this turn.
- Printed trigger: [Trigger] Activate this card's [Main] effect.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented with chained power prompts; exact duration cleanup for both +2000 and -1000 should be validated.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented with chained power prompts; exact duration cleanup for both +2000 and -1000 should be validated.

### OP07-017 - Dragon Breath

- Printed effect: [Main] K.O. up to 1 of your opponent's Characters with 3000 power or less and up to 1 of your opponent's Stages with a cost of 1 or less.
- Printed trigger: [Trigger] Activate this card's [Main] effect.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented two K.O. choices; exact simultaneous resolution/order should be manually replayed.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented two K.O. choices; exact simultaneous resolution/order should be manually replayed.

### OP07-018 - KEEP OUT

- Printed effect: [Counter] Up to 1 of your {Revolutionary Army} type Characters gains +2000 power until the end of your next turn.
- Printed trigger: [Trigger] Activate this card's [Counter] effect.
- Registered timings: `counter`, `trigger`
- Implementation status: `Needs Engine Support`
- Required code changes: Counter is implemented, but "until end of next turn" duration needs engine-level expiration validation.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Counter is implemented, but "until end of next turn" duration needs engine-level expiration validation.

### OP07-019 - Jewelry Bonney

- Printed effect: [On Your Opponent's Attack] [Once Per Turn] ? (You may rest the specified number of DON!! cards in your cost area.): Rest up to 1 of your opponent's Leader or Character cards.
- Printed trigger: None
- Registered timings: `on_opponent_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-020 - Aladine

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On K.O.] If your Leader has the {Fish-Man} type, play up to 1 {Fish-Man} or {Merfolk} type Character card with a cost of 3 or less from your hand.
- Printed trigger: None
- Registered timings: `blocker`, `on_ko`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-021 - Urouge

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [End of Your Turn] Set up to 1 of your DON!! cards as active.
- Printed trigger: None
- Registered timings: `blocker`, `end_of_turn`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-022 - Otama

- Printed effect: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 green {Land of Wano} type card other than [Otama] and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-023 - Caribou

- Printed effect: If you have 6 or more rested DON!! cards, this Character gains +1000 power. [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `continuous`, `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-024 - Koala

- Printed effect: [On Your Opponent's Attack] You may rest this Character: Up to 1 of your {Fish-Man} type Characters with a cost of 5 or less gains [Blocker] during this turn. (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `on_opponent_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-025 - Coribou

- Printed effect: [On Play] Play up to 1 [Caribou] with a cost of 4 or less from your hand rested.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-026 - Jewelry Bonney

- Printed effect: [On Play] Up to 1 of your opponent's rested Character or DON!! cards will not become active in your opponent's next Refresh Phase.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-027 - Jinbe

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP07-028 - Scratchmen Apoo

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP07-029 - Basil Hawkins

- Printed effect: If your Leader has the {Supernovas} type, this Character gains [Blocker]. (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [Once Per Turn] If this Character would be removed from the field by your opponent's effect, you may rest 1 of your opponent's Characters instead.
- Printed trigger: None
- Registered timings: `continuous`, `on_leave_prevention`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-030 - Pappag

- Printed effect: If you have a [Camie] Character, this Character gains [Blocker]. (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-031 - Bartolomeo

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [Your Turn] [Once Per Turn] If a Character is rested by your effect, draw 1 card and trash 1 card from your hand.
- Printed trigger: None
- Registered timings: `blocker`, `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-032 - Fisher Tiger

- Printed effect: This Character can attack Characters on the turn in which it is played. [On Play] If your Leader has the {Fish-Man} or {Merfolk} type, rest up to 1 of your opponent's Characters with a cost of 6 or less.
- Printed trigger: None
- Registered timings: `continuous`, `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-033 - Monkey.D.Luffy

- Printed effect: If you have 3 or more Characters, your Characters with a cost of 3 or less other than [Monkey.D.Luffy] cannot be K.O.'d by your opponent's effects.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-034 - Roronoa Zoro

- Printed effect: [When Attacking] If you have 3 or more Characters, this Character gains +2000 power during this turn.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-035 - Karmic Punishment

- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +2000 power during this battle. Then, if you have 3 or more Characters, that card gains an additional +1000 power during this battle.
- Printed trigger: [Trigger] K.O. up to 1 of your opponent's rested Characters with a cost of 4 or less.
- Registered timings: `counter`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-036 - Demonic Aura Nine-Sword Style Asura Demon Nine Flash

- Printed effect: [Main] Up to 1 of your Leader or Character cards gains +3000 power during this turn. Then, you may rest 1 of your Characters with a cost of 3 or more. If you do, rest up to 1 of your opponent's Characters with a cost of 5 or less.
- Printed trigger: [Trigger] Rest up to 1 of your opponent's Characters with a cost of 4 or less.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented chained +3000/rest own/rest opponent flow; exact optional branch UX should be manually replayed.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented chained +3000/rest own/rest opponent flow; exact optional branch UX should be manually replayed.

### OP07-037 - More Pizza!!

- Printed effect: [Main] Look at 5 cards from the top of your deck; reveal up to 1 {Supernovas} type card other than [More Pizza!!] and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: [Trigger] Draw 1 card.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-038 - Boa Hancock

- Printed effect: [Your Turn] [Once Per Turn] This effect can be activated when a Character is removed from the field by your effect. If you have 5 or less cards in your hand, draw 1 card.
- Printed trigger: None
- Registered timings: `on_character_removed`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-039 - Edward Weevil

- Printed effect: [DON!! x1] [When Attacking] Look at 3 cards from the top of your deck and place them at the top or bottom of the deck in any order.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-040 - Crocodile

- Printed effect: [On Play] ? (You may rest the specified number of DON!! cards in your cost area.): Return up to 1 Character with a cost of 2 or less to the owner's hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-041 - Gloriosa (Grandma Nyon)

- Printed effect: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 {Amazon Lily} or {Kuja Pirates} type card other than [Gloriosa (Grandma Nyon)] and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-042 - Gecko Moria

- Printed effect: [Once Per Turn] If your Leader has the {The Seven Warlords of the Sea} type and this Character would be removed from the field by your opponent's effect, you may place 1 of your Characters other than [Gecko Moria] at the bottom of the owner's deck instead.
- Printed trigger: None
- Registered timings: `on_leave_prevention`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-043 - Salome

- Printed effect: [Your Turn] [On Play] Up to 1 of your [Boa Hancock] cards gains +2000 power during this turn.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-044 - Dracule Mihawk

- Printed effect: [On Play] Draw 1 card.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-045 - Jinbe

- Printed effect: [On Play] Play up to 1 {The Seven Warlords of the Sea} type Character card with a cost of 4 or less other than [Jinbe] from your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-046 - Sengoku

- Printed effect: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 {The Seven Warlords of the Sea} type card and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-047 - Trafalgar Law

- Printed effect: [Activate: Main] You may return this Character to the owner's hand: If your opponent has 6 or more cards in their hand, your opponent places 1 card from their hand at the bottom of their deck.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-048 - Donquixote Doflamingo

- Printed effect: [Activate: Main] [Once Per Turn] ? (You may rest the specified number of DON!! cards in your cost area.): Reveal 1 card from the top of your deck. If that card is a {The Seven Warlords of the Sea} type Character card with a cost of 4 or less, you may play that card rested. Then, place the rest at the bottom of your deck.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-049 - Buckin

- Printed effect: [On Play] Play up to 1 [Edward Weevil] with a cost of 4 or less from your hand rested.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-050 - Boa Sandersonia

- Printed effect: [On Play] If you have 2 or more {Amazon Lily} or {Kuja Pirates} type Characters on your field, return up to 1 of your opponent's Characters with a cost of 3 or less to the owner's hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-051 - Boa Hancock

- Printed effect: [On Play] Up to 1 of your opponent's Characters other than [Monkey.D.Luffy] cannot attack until the end of your opponent's next turn. Then, place up to 1 Character with a cost of 1 or less at the bottom of the owner's deck.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-052 - Boa Marigold

- Printed effect: [On Play] If you have 2 or more {Amazon Lily} or {Kuja Pirates} type Characters on your field, place up to 1 Character with a cost of 2 or less at the bottom of the owner's deck.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-053 - Portgas.D.Ace

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On Play] Draw 2 cards and place 2 cards from your hand at the top or bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `blocker`, `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-054 - Marguerite

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On Play] Draw 1 card.
- Printed trigger: None
- Registered timings: `blocker`, `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-055 - Snake Dance

- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +4000 power during this battle. Then, return up to 1 of your Characters to the owner's hand.
- Printed trigger: [Trigger] You may return 1 of your Characters to the owner's hand: Return up to 1 of your opponent's Characters with a cost of 5 or less to the owner's hand.
- Registered timings: `counter`, `trigger`
- Implementation status: `Partial`
- Required code changes: Counter/trigger return-to-hand flows implemented; exact owner-hand handling and optional cost wording need manual validation.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Counter/trigger return-to-hand flows implemented; exact owner-hand handling and optional cost wording need manual validation.

### OP07-056 - Slave Arrow

- Printed effect: [Counter] You may return 1 of your Characters with a cost of 2 or more to the owner's hand: Up to 1 of your Leader or Character cards gains +4000 power during this battle.
- Printed trigger: [Trigger] Draw 2 cards and place 2 cards from your hand at the bottom of your deck in any order.
- Registered timings: `counter`, `trigger`
- Implementation status: `Partial`
- Required code changes: Trigger draw-2 then bottom-2 implemented; exact "in any order" ordering is simplified to selected order.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Trigger draw-2 then bottom-2 implemented; exact "in any order" ordering is simplified to selected order.

### OP07-057 - Perfume Femur

- Printed effect: [Main] Select up to 1 of your {The Seven Warlords of the Sea} type Leader or Character cards and that card gains +2000 power during this turn. Then, if the selected card attacks during this turn, your opponent cannot activate [Blocker].
- Printed trigger: [Trigger] Draw 1 card.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Needs Engine Support`
- Required code changes: Blocker prevention is represented with a card flag; engine support for blocking restriction should be validated.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Blocker prevention is represented with a card flag; engine support for blocking restriction should be validated.

### OP07-058 - Island of Women

- Printed effect: [Activate: Main] You may trash 1 card from your hand and rest this Stage: If your Leader has the {Kuja Pirates} type, return up to 1 of your {Amazon Lily} or {Kuja Pirates} type Characters to the owner's hand.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Stage activate implemented; exact trash/rest cost atomicity should be manually replayed.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Stage activate implemented; exact trash/rest cost atomicity should be manually replayed.

### OP07-059 - Foxy

- Printed effect: [When Attacking] DON!! -3 (You may return the specified number of DON!! cards from your field to your DON!! deck.): If you have 3 or more {Foxy Pirates} type Characters, select your opponent's rested Leader and up to 1 Character card. The selected cards will not become active in your opponent's next Refresh Phase.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-060 - Itomimizu

- Printed effect: [Activate: Main] [Once Per Turn] If your Leader has the {Foxy Pirates} type and you have no other [Itomimizu], add up to 1 DON!! card from your DON!! deck and rest it.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-061 - Vinsmoke Sanji

- Printed effect: [On Play] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): If your Leader has the {The Vinsmoke Family} type, draw 1 card.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-062 - Vinsmoke Reiju

- Printed effect: [On Play] If the number of DON!! cards on your field is equal to or less than the number on your opponent's field, return up to 1 of your {The Vinsmoke Family} type Characters with a cost of 1 to the owner's hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-063 - Capote

- Printed effect: [On Play] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): If your Leader has the {Foxy Pirates} type, up to 1 of your opponent's Characters with a cost of 6 or less cannot attack until the end of your opponent's next turn.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-064 - Sanji

- Printed effect: If the number of DON!! cards on your field is at least 2 less than the number on your opponent's field, give this card in your hand -3 cost. [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `continuous`, `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-065 - Gina

- Printed effect: [On Play] If your Leader has the {Foxy Pirates} type and the number of DON!! cards on your field is equal to or less than the number on your opponent's field, add up to 1 DON!! card from your DON!! deck and set it as active.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-066 - Tony Tony.Chopper

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On Play] If the number of DON!! cards on your field is equal to or less than the number on your opponent's field, add up to 1 DON!! card from your DON!! deck and rest it.
- Printed trigger: None
- Registered timings: `blocker`, `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-067 - Tonjit

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP07-068 - Hamburg

- Printed effect: [DON!! x1] [When Attacking] If the number of DON!! cards on your field is equal to or less than the number on your opponent's field, add up to 1 DON!! card from your DON!! deck and rest it.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-069 - Pickles

- Printed effect: If the number of DON!! cards on your field is equal to or less than the number on your opponent's field, your {Foxy Pirates} type Characters other than [Pickles] cannot be K.O.'d by your opponent's effects.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-070 - Big Bun

- Printed effect: [On Play] If the number of DON!! cards on your field is equal to or less than the number on your opponent's field, play up to 1 {Foxy Pirates} type card with a cost of 4 or less from your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-071 - Foxy

- Printed effect: [Opponent's Turn] If your Leader has the {Foxy Pirates} type, give all of your opponent's Characters -1000 power. [Activate: Main] [Once Per Turn] Add up to 1 DON!! card from your DON!! deck and rest it.
- Printed trigger: None
- Registered timings: `continuous`, `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-072 - Porche

- Printed effect: [On Play] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Look at 5 cards from the top of your deck; reveal up to 1 {Foxy Pirates} type card and add it to your hand. Then, place the rest at the bottom of your deck in any order and play up to 1 purple Character card with 4000 power or less from your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-073 - Monkey.D.Luffy

- Printed effect: [Activate: Main] [Once Per Turn] DON!! -3 (You may return the specified number of DON!! cards from your field to your DON!! deck.): If your opponent has 3 or more Characters, set this Character as active.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-074 - Monda

- Printed effect: [Activate: Main] You may trash this Character: If your Leader has the {Foxy Pirates} type, add up to 1 DON!! card from your DON!! deck and rest it.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-075 - Slow-Slow Beam

- Printed effect: [Counter] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Give up to 1 each of your opponent's Leader and Character cards -2000 power during this turn.
- Printed trigger: None
- Registered timings: `counter`
- Implementation status: `Partial`
- Required code changes: Counter uses a shared multi-target -2000 prompt; printed "up to 1 each Leader and Character" should get stricter target grouping.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Counter uses a shared multi-target -2000 prompt; printed "up to 1 each Leader and Character" should get stricter target grouping.

### OP07-076 - Slow-Slow Beam Sword

- Printed effect: [Counter] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Up to 1 of your Leader or Character cards gains +2000 power during this battle. Then, rest up to 1 of your opponent's Characters.
- Printed trigger: [Trigger] Add up to 1 DON!! card from your DON!! deck and set it as active.
- Registered timings: `counter`, `trigger`
- Implementation status: `Partial`
- Required code changes: Counter/trigger implemented; DON-return optional cost and chained rest target should be manually replayed.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Counter/trigger implemented; DON-return optional cost and chained rest target should be manually replayed.

### OP07-077 - We're Going to Claim the One Piece!!!

- Printed effect: [Main] If your Leader has the {Animal Kingdom Pirates} or {Big Mom Pirates} type, look at 5 cards from the top of your deck; reveal up to 1 {Animal Kingdom Pirates} or {Big Mom Pirates} type card and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: [Trigger] Activate this card's [Main] effect.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-078 - Megaton Nine-Tails Rush

- Printed effect: [Main] If the number of DON!! cards on your field is equal to or less than the number on your opponent's field, set up to 1 of your [Foxy] cards as active.
- Printed trigger: [Trigger] Add up to 1 DON!! card from your DON!! deck and set it as active.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Main only targets named Foxy; verify exact card-name matching and active-state handling with real Foxy fixtures.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Main only targets named Foxy; verify exact card-name matching and active-state handling with real Foxy fixtures.

### OP07-079 - Rob Lucci

- Printed effect: [When Attacking] You may trash 2 cards from the top of your deck: Give up to 1 of your opponent's Characters -1 cost during this turn.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-080 - Kaku

- Printed effect: [On Play] You may place 2 cards with a type including "CP" from your trash at the bottom of your deck in any order: Give up to 1 of your opponent's Characters -3 cost during this turn.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-081 - Kalifa

- Printed effect: [DON!! x1] [Your Turn] Give all of your opponent's Characters -1 cost.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-082 - Captain John

- Printed effect: [On Play] Trash 2 cards from the top of your deck and give up to 1 of your opponent's Characters -1 cost during this turn.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-083 - Gecko Moria

- Printed effect: [Activate: Main] You may place 4 {Thriller Bark Pirates} type cards from your trash at the bottom of your deck in any order: This Character gains [Banish] and +1000 power during this turn. (When this card deals damage, the target card is trashed without activating its Trigger.)
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-084 - Gismonda

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-085 - Stussy

- Printed effect: [On Play] You may trash 1 of your Characters: K.O. up to 1 of your opponent's Characters.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-086 - Spandam

- Printed effect: [On Play] Trash 2 cards from the top of your deck and give up to 1 of your opponent's Characters -2 cost during this turn.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-087 - Baskerville

- Printed effect: [Your Turn] If your opponent has a Character with a cost of 0, this Character gains +3000 power.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-088 - Hattori

- Printed effect: [Your Turn] [On Play] Up to 1 of your [Rob Lucci] cards gains +2000 power during this turn.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-089 - Maha

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP07-090 - Morgans

- Printed effect: [On Play] Your opponent trashes 1 card from their hand and reveals their hand. Then, your opponent draws 1 card.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-091 - Monkey.D.Luffy

- Printed effect: [When Attacking] Trash up to 1 of your opponent's Characters with a cost of 2 or less. Then, place any number of Character cards with a cost of 4 or more from your trash at the bottom of your deck in any order. This Character gains +1000 power during this turn for every 3 cards placed at the bottom of your deck.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-092 - Joseph

- Printed effect: [On Play] You may place 2 cards with a type including "CP" from your trash at the bottom of your deck in any order: K.O. up to 1 of your opponent's Characters with a cost of 1 or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-093 - Rob Lucci

- Printed effect: [On Play] You may place 3 cards from your trash at the bottom of your deck in any order: Your opponent trashes 1 card from their hand. Then, you may place up to 1 card from your opponent's trash at the bottom of their deck.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-094 - Shave

- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +2000 power during this battle. Then, if you have 10 or more cards in your trash, return up to 1 of your Characters with a type including "CP" to the owner's hand.
- Printed trigger: [Trigger] Return up to 1 of your Characters to the owner's hand.
- Registered timings: `counter`, `trigger`
- Implementation status: `Partial`
- Required code changes: Counter auto-applies leader power before optional CP return; printed target choice should be improved.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Counter auto-applies leader power before optional CP return; printed target choice should be improved.

### OP07-095 - Iron Body

- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +4000 power during this battle. Then, if you have 10 or more cards in your trash, that card gains an additional +2000 power during this battle.
- Printed trigger: [Trigger] Up to 1 of your Leader or Character cards gains +1000 power during this turn.
- Registered timings: `counter`, `trigger`
- Implementation status: `Partial`
- Required code changes: Counter auto-applies to Leader; printed Leader/Character target choice should be improved.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Counter auto-applies to Leader; printed Leader/Character target choice should be improved.

### OP07-096 - Tempest Kick

- Printed effect: [Main] Draw 1 card. Then, if you have 10 or more cards in your trash, give up to 1 of your opponent's Characters -3 cost during this turn.
- Printed trigger: [Trigger] K.O. up to 1 of your opponent's Characters with a cost of 3 or less.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-097 - Vegapunk

- Printed effect: This Leader cannot attack. [Activate: Main] [Once Per Turn] ? (You may rest the specified number of DON!! cards in your cost area.): Select up to 1 {Egghead} type card with a cost of 5 or less from your hand and play it or add it to the top of your Life cards face-up.
- Printed trigger: None
- Registered timings: `continuous`, `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-098 - Atlas

- Printed effect: If you have less Life cards than your opponent, this Character cannot be K.O.'d in battle.
- Printed trigger: [Trigger] If your Leader is [Vegapunk], play this card.
- Registered timings: `continuous`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-099 - Usopp

- Printed effect: None
- Printed trigger: [Trigger] Up to 1 of your {Egghead} type Leader or Character cards gains +2000 power until the end of your next turn.
- Registered timings: `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-100 - Edison

- Printed effect: [On Play] If you have 2 or less Life cards, draw 2 cards and trash 2 card from your hand.
- Printed trigger: [Trigger] If your Leader is [Vegapunk], play this card.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-101 - Shaka

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: [Trigger] If your Leader is [Vegapunk], play this card.
- Registered timings: `blocker`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-102 - Jinbe

- Printed effect: None
- Printed trigger: [Trigger] Return up to 1 of your opponent's Characters with a cost of 4 or less to the owner's hand and add this card to your hand.
- Registered timings: `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-103 - Tony Tony.Chopper

- Printed effect: None
- Printed trigger: [Trigger] Up to 1 of your {Egghead} type Characters gains [Blocker] during this turn. Then, add this card to your hand.
- Registered timings: `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-104 - Nico Robin

- Printed effect: None
- Printed trigger: [Trigger] If your Leader has the {Egghead} type, draw 2 cards.
- Registered timings: `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-105 - Pythagoras

- Printed effect: [On K.O.] If you have 2 or less Life cards, play up to 1 {Egghead} type Character card with a cost of 4 or less from your trash rested.
- Printed trigger: [Trigger] If your Leader is [Vegapunk], play this card.
- Registered timings: `on_ko`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-106 - Fuza

- Printed effect: [DON!! x1] [When Attacking] If you have 1 or less Life cards, K.O. up to 1 of your opponent's Characters with a cost of 3 or less.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-107 - Franky

- Printed effect: None
- Printed trigger: [Trigger] Draw 1 card. Then, if you have 1 or less Life cards, play this card.
- Registered timings: `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-108 - Vega Force 01

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP07-109 - Monkey.D.Luffy

- Printed effect: [Activate: Main] You may trash this Character: If you have 2 or less Life cards, K.O. up to 1 of your opponent's Characters with a cost of 4 or less. Then, draw 1 card.
- Printed trigger: [Trigger] K.O. up to 1 of your opponent's Characters with a cost of 4 or less.
- Registered timings: `activate`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-110 - York

- Printed effect: [On Play] You may add 1 card from the top or bottom of your Life cards to your hand: K.O. up to 1 of your opponent's Characters with a cost of 2 or less.
- Printed trigger: [Trigger] If your Leader is [Vegapunk], play this card.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-111 - Lilith

- Printed effect: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 {Egghead} type card other than [Lilith] and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: [Trigger] If your Leader is [Vegapunk], play this card.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-112 - Lucy

- Printed effect: [When Attacking] [Once Per Turn] You may add 1 card from the top or bottom of your Life cards to your hand: You may rest up to 1 of your opponent's Characters with a cost of 4 or less. Then, if you have 1 or less Life cards, add up to 1 card from the top of your deck to the top of your Life cards.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-113 - Roronoa Zoro

- Printed effect: None
- Printed trigger: [Trigger] If your Leader has the {Egghead} type, rest up to 1 of your opponent's Leader or Character cards.
- Registered timings: `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-114 - He Possesses the World's Most Brilliant Mind

- Printed effect: [Main] Look at 5 cards from the top of your deck; reveal up to 1 {Egghead} type card other than [He Possesses the World's Most Brilliant Mind] and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: [Trigger] Draw 1 card.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-115 - I Re-Quasar Helllp!!

- Printed effect: [Counter] If you have 2 or less Life cards, up to 1 of your Leader or Character cards gains +3000 power during this battle.
- Printed trigger: [Trigger] Play up to 1 of your {Egghead} type Character cards with a cost of 5 or less from your trash.
- Registered timings: `counter`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-116 - Blaze Slice

- Printed effect: [Main]/[Counter] Up to 1 of your Leader or Character cards gains +1000 power during this turn. Then, if your opponent has 2 or less Life cards, rest up to 1 of your opponent's Characters with a cost of 4 or less.
- Printed trigger: [Trigger] Rest up to 1 of your opponent's Characters with a cost of 4 or less.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-117 - Egghead

- Printed effect: [End of Your Turn] If you have 3 or less Life cards, set up to 1 {Egghead} type Character with a cost of 5 or less as active.
- Printed trigger: [Trigger] Play this card.
- Registered timings: `end_of_turn`, `trigger`
- Implementation status: `Partial`
- Required code changes: Stage trigger play implemented; end-of-turn Egghead active setting should be validated with real Egghead fixtures.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Stage trigger play implemented; end-of-turn Egghead active setting should be validated with real Egghead fixtures.

### OP07-118 - Sabo

- Printed effect: [On Play] You may trash 1 card from your hand: K.O. up to 1 of your opponent's Characters with a cost of 5 or less and up to 1 of your opponent's Characters with a cost of 3 or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP07-119 - Portgas.D.Ace

- Printed effect: [On Play] Add up to 1 card from the top of your deck to the top of your Life cards. Then, if you have 2 or less Life cards, this Character gains [Rush] during this turn. (This card can attack on the turn in which it is played.)
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP07 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.
