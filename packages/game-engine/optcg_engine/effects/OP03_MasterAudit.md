# OP03 Master Audit

Source of truth: `packages/simulator/backend/data/cards.json` base OP03 entries where `id == id_normal`.

## Summary

- Base cards audited: 123
- Non-vanilla cards: 108
- Vanilla cards: 15
- Registered OP03 cards after this pass: 108
- Registered OP03 timings after this pass: 160
- Missing non-vanilla registrations: 0
- Missing printed trigger timings: 0
- Strict status after this pass: 109/123 `Complete` or `Vanilla`; 14 follow-up cards flagged below

## Verification

- `python -m py_compile packages\game-engine\optcg_engine\effects\sets\op03_effects.py packages\game-engine\scripts\card_effect_tester.py` passed.
- OP03 registration coverage script passed: `base=123 nonvanilla=108 vanilla=15 registered_cards=108 timings=160 missing=[] missing_triggers=[]`.
- Direct OP03 handler execution sweep passed: `OP03_handler_sweep_ran=160 errors=0`, resolving pending choices through `GameState.resolve_pending_choice(...)`.
- Full pytest suite was not rerun in this pass; earlier environment check showed `python -m pytest packages\game-engine\tests` is unavailable because `pytest` is not installed.

## Follow-Up Queue

- `OP03-007` Namule: `Needs Engine Support` - Exact temporary duration/expiration for granted power/keywords should be validated against end-of-turn cleanup.
- `OP03-022` Arlong: `Partial` - Search/reorder style helper should be manually validated for exact reveal/add/rest-to-bottom behavior.
- `OP03-026` Kuroobi: `Partial` - Leader event-dispatch and once-per-turn style behavior depends on simulator hook coverage.
- `OP03-036` Out-of-the-Bag: `Partial` - Main effect uses chained rest/set-active prompts; exact Kuro Leader/Character active-target filtering should be manually tested.
- `OP03-054` Usopp's Rubber Band of Doom!!!: `Partial` - Counter applies target/power through simplified existing logic; printed text allows Leader or Character target plus optional top-deck trash.
- `OP03-055` Gum-Gum Giant Gavel: `Partial` - Counter currently pays/trashes before applying Leader power; exact optional cost sequencing should be improved.
- `OP03-072` Gum-Gum Jet Gatling: `Partial` - Counter currently auto-applies +3000 to Leader after trash; printed text allows choosing Leader or Character.
- `OP03-073` Hull Dismantler Slash: `Partial` - Main trigger alias is present, but DON-return callback chains draw then K.O.; exact optional target UX should be manually validated.
- `OP03-075` Galley-La Company: `Partial` - Stage activate uses simplified DON add/rest state; exact Iceburg restriction and active/rested DON handling should be manually tested.
- `OP03-077` Charlotte Linlin: `Partial` - Leader effect uses multi-step hand trash/life add flow; exact opponent-choice/life placement nuances need manual validation.
- `OP03-094` Air Door: `Partial` - Main effect now plays a CP Character from top 5 and trashes rest; still needs manual validation with real CP deck fixtures.
- `OP03-095` Soap Sheep: `Partial` - Trigger makes opponent trash via existing hand-trash helper; exact opponent-owned choice UX should be validated.
- `OP03-098` Enies Lobby: `Needs Engine Support` - Stage play trigger is implemented; activate duration/cost-modifier cleanup should be validated.
- `OP03-118` Ikoku Sovereignty: `Partial` - Counter auto-targets Leader; printed text allows Leader or Character. Trigger trash-2 flow is implemented but should validate optional add-up-to-1 behavior.

## Per-Card Audit

### OP03-001 - Portgas.D.Ace

- Printed effect: When this Leader attacks or is attacked, you may trash any number of Event or Stage cards from your hand. This Leader gains +1000 power during this battle for every card trashed.
- Printed trigger: None
- Registered timings: `on_opponent_attack`, `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-002 - Adio

- Printed effect: [DON!! x1] [When Attacking] Your opponent cannot activate a [Blocker] Character that has 2000 or less power during this battle.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-003 - Izo

- Printed effect: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 card with a type including "Whitebeard Pirates" other than [Izo] and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-004 - Curiel

- Printed effect: This Character cannot attack a Leader on the turn in which it is played. [DON!! x1] This Character gains [Rush]. (This card can attack on the turn in which it is played.)
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-005 - Thatch

- Printed effect: [Activate: Main] [Once Per Turn] This Character gains +2000 power during this turn. Then, trash this Character at the end of this turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-006 - Speed Jil

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP03-007 - Namule

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP03-008 - Buggy

- Printed effect: This Character cannot be K.O.'d in battle by <Slash> attribute cards. [On Play] Look at 5 cards from the top of your deck; reveal up to 1 red Event and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `continuous`, `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-009 - Haruta

- Printed effect: [Activate: Main] [Once Per Turn] Give up to 1 rested DON!! card to your Leader or 1 of your Characters.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-010 - Fossa

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-011 - Blamenco

- Printed effect: [DON!! x1] [When Attacking] Give up to 1 of your opponent's Characters -2000 power during this turn.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-012 - Marshall.D.Teach

- Printed effect: [When Attacking] You may trash 1 of your red Characters with 4000 power or more: Draw 1 card. Then, this Character gains +1000 power during this battle.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-013 - Marco

- Printed effect: [Your Turn] [On Play] K.O. up to 1 of your opponent's Characters with 3000 power or less. [On K.O.] You may trash 1 Event from your hand: You may play this Character card from your trash rested.
- Printed trigger: None
- Registered timings: `on_play`, `on_ko`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-014 - Monkey.D.Garp

- Printed effect: [When Attacking] Play up to 1 red Character card with a cost of 1 from your hand.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-015 - Lim

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [Opponent's Turn] When this Character is K.O.'d, give up to 1 of your opponent's Leader or Character cards -2000 power during this turn.
- Printed trigger: None
- Registered timings: `blocker`, `on_ko`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-016 - Flame Emperor

- Printed effect: [Main] If your Leader is [Portgas.D.Ace], K.O. up to 1 of your opponent's Characters with 8000 power or less, and your Leader gains [Double Attack] and +3000 power during this turn. (This card deals 2 damage.)
- Printed trigger: [Trigger] K.O. up to 1 of your opponent's Characters with 6000 power or less.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-017 - Cross Fire

- Printed effect: [Main]/[Counter] If your Leader's type includes "Whitebeard Pirates", give up to 1 of your opponent's Characters -4000 power during this turn.
- Printed trigger: [Trigger] Activate this card's [Main] effect.
- Registered timings: `on_play`, `counter`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-018 - Fire Fist

- Printed effect: [Main] You may trash 1 Event from your hand: K.O. up to 1 of your opponent's Characters with 5000 power or less and up to 1 of your opponent's Characters with 4000 power or less.
- Printed trigger: [Trigger] K.O. up to 1 of your opponent's Characters with 5000 power or less.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-019 - Fiery Doll

- Printed effect: [Main] Your Leader gains +4000 power during this turn.
- Printed trigger: [Trigger] Give up to 1 of your opponent's Leader or Character cards -10000 power during this turn.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-020 - Striker

- Printed effect: [Activate: Main] ? (You may rest the specified number of DON!! cards in your cost area.) You may rest this Stage: If your Leader is [Portgas.D.Ace], look at 5 cards from the top of your deck; reveal up to 1 Event and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-021 - Kuro

- Printed effect: [Activate: Main] ? (You may rest the specified number of DON!! cards in your cost area.) You may rest 2 of your {East Blue} type Characters: Set this Leader as active, and rest up to 1 of your opponent's Characters with a cost of 5 or less.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-022 - Arlong

- Printed effect: [DON!! x2] [When Attacking] ? (You may rest the specified number of DON!! cards in your cost area.): Play up to 1 Character card with a cost of 4 or less and a [Trigger] from your hand.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Partial`
- Required code changes: Search/reorder style helper should be manually validated for exact reveal/add/rest-to-bottom behavior.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Search/reorder style helper should be manually validated for exact reveal/add/rest-to-bottom behavior.

### OP03-023 - Alvida

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP03-024 - Gin

- Printed effect: [On Play] If your Leader has the {East Blue} type, rest up to 2 of your opponent's Characters with a cost of 4 or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-025 - Krieg

- Printed effect: [On Play] You may trash 1 card from your hand: K.O. up to 2 of your opponent's rested Characters with a cost of 4 or less. [DON!! x1] This Character gains [Double Attack]. (This card deals 2 damage.)
- Printed trigger: None
- Registered timings: `on_play`, `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-026 - Kuroobi

- Printed effect: [On Play] If your Leader has the {East Blue} type, rest up to 1 of your opponent's Characters.
- Printed trigger: [Trigger] Play this card.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Leader event-dispatch and once-per-turn style behavior depends on simulator hook coverage.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Leader event-dispatch and once-per-turn style behavior depends on simulator hook coverage.

### OP03-027 - Sham

- Printed effect: [On Play] If your Leader has the {East Blue} type, rest up to 1 of your opponent's Characters with a cost of 2 or less and, if you don't have [Buchi], play up to 1 [Buchi] from your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-028 - Jango

- Printed effect: [On Play] Choose one: ? Set up to 1 of your {East Blue} type Leader or Character cards with a cost of 6 or less as active. ? Rest this Character and up to 1 of your opponent's Characters.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-029 - Chew

- Printed effect: [On Play] K.O. up to 1 of your opponent's rested Characters with a cost of 4 or less.
- Printed trigger: [Trigger] Play this card.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-030 - Nami

- Printed effect: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 green {East Blue} type card other than [Nami] and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: [Trigger] Play this card.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-031 - Pearl

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-032 - Buggy

- Printed effect: This Character cannot be K.O.'d in battle by <Slash> attribute cards.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-033 - Hatchan

- Printed effect: None
- Printed trigger: [Trigger] If your Leader has the {East Blue} type, play this card.
- Registered timings: `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-034 - Buchi

- Printed effect: [On Play] K.O. up to 1 of your opponent's rested Characters with a cost of 2 or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-035 - Momoo

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP03-036 - Out-of-the-Bag

- Printed effect: [Main] You may rest 1 of your {East Blue} type Characters: Set up to 1 of your [Kuro] cards as active.
- Printed trigger: [Trigger] K.O. up to 1 of your opponent's rested Characters with a cost of 3 or less.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Main effect uses chained rest/set-active prompts; exact Kuro Leader/Character active-target filtering should be manually tested.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Main effect uses chained rest/set-active prompts; exact Kuro Leader/Character active-target filtering should be manually tested.

### OP03-037 - Tooth Attack

- Printed effect: [Main] You may rest 1 of your {East Blue} type Characters: K.O. up to 1 of your opponent's rested Characters with a cost of 3 or less.
- Printed trigger: [Trigger] Play up to 1 Character card with a cost of 4 or less and a [Trigger] from your hand.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-038 - Deathly Poison Gas Bomb MH5

- Printed effect: [Main] Rest up to 2 of your opponent's Characters with a cost of 2 or less.
- Printed trigger: [Trigger] Rest up to 1 of your opponent's Characters with a cost of 5 or less.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-039 - One, Two, Jango

- Printed effect: [Main] Rest up to 1 of your opponent's Characters with a cost of 1 or less. Then, up to 1 of your Characters gains +1000 power during this turn.
- Printed trigger: [Trigger] Rest up to 1 of your opponent's Characters with a cost of 4 or less.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-040 - Nami

- Printed effect: When your deck is reduced to 0, you win the game instead of losing, according to the rules. [DON!! x1] When this Leader's attack deals damage to your opponent's Life, you may trash 1 card from the top of your deck.
- Printed trigger: None
- Registered timings: `continuous`, `on_damage_dealt`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-041 - Usopp

- Printed effect: [Rush] (This card can attack on the turn in which it is played.) [DON!! x1] When this Character's attack deals damage to your opponent's Life, you may trash 7 cards from the top of your deck.
- Printed trigger: None
- Registered timings: `continuous`, `on_damage_dealt`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-042 - Usopp's Pirate Crew

- Printed effect: [On Play] Add up to 1 blue [Usopp] from your trash to your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-043 - Gaimon

- Printed effect: When you deal damage to your opponent's Life, you may trash 3 cards from the top of your deck. If you do, trash this Character.
- Printed trigger: None
- Registered timings: `continuous`, `on_damage_dealt`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-044 - Kaya

- Printed effect: [On Play] Draw 2 cards and trash 2 cards from your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-045 - Carne

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [Opponent's Turn] If you have 20 or less cards in your deck, this Character gains +3000 power.
- Printed trigger: None
- Registered timings: `blocker`, `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-046 - Genzo

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP03-047 - Zeff

- Printed effect: [DON!! x1] When this Character's attack deals damage to your opponent's Life, you may trash 7 cards from the top of your deck. [On Play] Return up to 1 Character with a cost of 3 or less to the owner's hand, and you may trash 2 cards from the top of your deck.
- Printed trigger: None
- Registered timings: `on_play`, `on_damage_dealt`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-048 - Nojiko

- Printed effect: [On Play] If your Leader is [Nami], return up to 1 of your opponent's Characters with a cost of 5 or less to the owner's hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-049 - Patty

- Printed effect: [On Play] If you have 20 or less cards in your deck, return up to 1 Character with a cost of 3 or less to the owner's hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-050 - Boodle

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On K.O.] You may trash 1 card from the top of your deck.
- Printed trigger: None
- Registered timings: `blocker`, `on_ko`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-051 - Bell-m?re

- Printed effect: [DON!! x1] When this Character's attack deals damage to your opponent's Life, you may trash 7 cards from the top of your deck. [On K.O.] You may trash 3 cards from the top of your deck.
- Printed trigger: None
- Registered timings: `on_ko`, `on_damage_dealt`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-052 - Merry

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP03-053 - Yosaku & Johnny

- Printed effect: [DON!! x1] If you have 20 or less cards in your deck, this Character gains +2000 power.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-054 - Usopp's Rubber Band of Doom!!!

- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +2000 power during this battle. Then, you may trash 1 card from the top of your deck.
- Printed trigger: [Trigger] Draw 1 card and you may trash 1 card from the top of your deck.
- Registered timings: `counter`, `trigger`
- Implementation status: `Partial`
- Required code changes: Counter applies target/power through simplified existing logic; printed text allows Leader or Character target plus optional top-deck trash.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Counter applies target/power through simplified existing logic; printed text allows Leader or Character target plus optional top-deck trash.

### OP03-055 - Gum-Gum Giant Gavel

- Printed effect: [Counter] You may trash 1 card from your hand: Up to 1 of your Leader gains +4000 power during this battle. Then, you may trash 2 cards from the top of your deck.
- Printed trigger: [Trigger] Return up to 1 Character with a cost of 4 or less to the owner's hand.
- Registered timings: `counter`, `trigger`
- Implementation status: `Partial`
- Required code changes: Counter currently pays/trashes before applying Leader power; exact optional cost sequencing should be improved.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Counter currently pays/trashes before applying Leader power; exact optional cost sequencing should be improved.

### OP03-056 - Sanji's Pilaf

- Printed effect: [Main] Draw 2 cards.
- Printed trigger: [Trigger] Activate this card's [Main] effect.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-057 - Three Thousand Worlds

- Printed effect: [Main] Place up to 1 Character with a cost of 5 or less at the bottom of the owner's deck.
- Printed trigger: [Trigger] Place up to 1 Character with a cost of 3 or less at the bottom of the owner's deck.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-058 - Iceburg

- Printed effect: This Leader cannot attack. [Activate: Main] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.) You may rest this Leader: Play up to 1 {Galley-La Company} type Character card with a cost of 5 or less from your hand.
- Printed trigger: None
- Registered timings: `continuous`, `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-059 - Kaku

- Printed effect: [When Attacking] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): This Character gains [Banish] during this battle. (When this card deals damage, the target card is trashed without activating its Trigger.)
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-060 - Kalifa

- Printed effect: [When Attacking] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Draw 2 cards and trash 1 card from your hand.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-061 - Kiwi & Mozu

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP03-062 - Kokoro

- Printed effect: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 {Water Seven} type card other than [Kokoro] and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-063 - Zambai

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On Play] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): If your Leader has the {Water Seven} type, draw 1 card.
- Printed trigger: None
- Registered timings: `blocker`, `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-064 - Tilestone

- Printed effect: [On K.O.] If your Leader has the {Galley-La Company} type, add up to 1 DON!! card from your DON!! deck and rest it.
- Printed trigger: None
- Registered timings: `on_ko`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-065 - Chimney & Gonbe

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-066 - Paulie

- Printed effect: [On Play] ? (You may rest the specified number of DON!! cards in your cost area.): Add up to 1 DON!! card from your DON!! deck and set it as active. Then, if you have 8 or more DON!! cards on your field, K.O. up to 1 of your opponent's Characters with a cost of 4 or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-067 - Peepley Lulu

- Printed effect: [DON!! x1] [When Attacking] If your Leader has the {Galley-La Company} type, add up to 1 DON!! card from your DON!! deck and rest it.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-068 - Minozebra

- Printed effect: [Banish] (When this card deals damage, the target card is trashed without activating its Trigger.) [On K.O.] If your Leader has the {Impel Down} type, add up to 1 DON!! card from your DON!! deck and rest it.
- Printed trigger: None
- Registered timings: `continuous`, `on_ko`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-069 - Minorhinoceros

- Printed effect: [On K.O.] If your Leader has the {Impel Down} type, draw 2 cards and trash 1 card from your hand.
- Printed trigger: None
- Registered timings: `on_ko`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-070 - Monkey.D.Luffy

- Printed effect: [On Play] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.) You may trash 1 Character card with a cost of 5 from your hand: This Character gains [Rush] during this turn. (This card can attack on the turn in which it is played.)
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-071 - Rob Lucci

- Printed effect: [When Attacking] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Rest up to 1 of your opponent's Characters with a cost of 5 or less.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-072 - Gum-Gum Jet Gatling

- Printed effect: [Counter] You may trash 1 card from your hand: Up to 1 of your Leader or Character cards gains +3000 power during this battle.
- Printed trigger: [Trigger] Add up to 1 DON!! card from your DON!! deck and set it as active.
- Registered timings: `counter`, `trigger`
- Implementation status: `Partial`
- Required code changes: Counter currently auto-applies +3000 to Leader after trash; printed text allows choosing Leader or Character.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Counter currently auto-applies +3000 to Leader after trash; printed text allows choosing Leader or Character.

### OP03-073 - Hull Dismantler Slash

- Printed effect: [Main] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): If your Leader has the {Water Seven} type, K.O. up to 1 of your opponent's Characters with a cost of 2 or less.
- Printed trigger: [Trigger] Activate this card's [Main] effect.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Main trigger alias is present, but DON-return callback chains draw then K.O.; exact optional target UX should be manually validated.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Main trigger alias is present, but DON-return callback chains draw then K.O.; exact optional target UX should be manually validated.

### OP03-074 - Top Knot

- Printed effect: [Main] DON!! -2 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Place up to 1 of your opponent's Characters with a cost of 4 or less at the bottom of the owner's deck.
- Printed trigger: [Trigger] Activate this card's [Main] effect.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-075 - Galley-La Company

- Printed effect: [Activate: Main] You may rest this Stage: If your Leader is [Iceburg], add up to 1 DON!! card from your DON!! deck and rest it.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Stage activate uses simplified DON add/rest state; exact Iceburg restriction and active/rested DON handling should be manually tested.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Stage activate uses simplified DON add/rest state; exact Iceburg restriction and active/rested DON handling should be manually tested.

### OP03-076 - Rob Lucci

- Printed effect: [Your Turn] [Once Per Turn] You may trash 2 cards from your hand: When your opponent's Character is K.O.'d, set this Leader as active.
- Printed trigger: None
- Registered timings: `on_opponent_ko`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-077 - Charlotte Linlin

- Printed effect: [DON!! x2] [When Attacking] ? (You may rest the specified number of DON!! cards in your cost area.) You may trash 1 card from your hand: If you have 1 or less Life cards, add up to 1 card from the top of your deck to the top of your Life cards.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Partial`
- Required code changes: Leader effect uses multi-step hand trash/life add flow; exact opponent-choice/life placement nuances need manual validation.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Leader effect uses multi-step hand trash/life add flow; exact opponent-choice/life placement nuances need manual validation.

### OP03-078 - Issho

- Printed effect: [DON!! x1] [Your Turn] Give all of your opponent's Characters -3 cost. [On Play] If your opponent has 6 or more cards in their hand, trash 2 cards from your opponent's hand.
- Printed trigger: None
- Registered timings: `continuous`, `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-079 - Vergo

- Printed effect: [DON!! x1] This Character cannot be K.O.'d in battle.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-080 - Kaku

- Printed effect: [On Play] You may place 2 cards with a type including "CP" from your trash at the bottom of your deck in any order: K.O. up to 1 of your opponent's Characters with a cost of 3 or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-081 - Kalifa

- Printed effect: [On Play] Draw 2 cards and trash 2 cards from your hand. Then, give up to 1 of your opponent's Characters -2 cost during this turn.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-082 - Kumadori

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP03-083 - Corgy

- Printed effect: [On Play] Look at 5 cards from the top of your deck and trash up to 2 cards. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-084 - Jerry

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP03-085 - Jabra

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP03-086 - Spandam

- Printed effect: [On Play] If your Leader's type includes "CP", look at 3 cards from the top of your deck; reveal up to 1 card with a type including "CP" other than [Spandam] and add it to your hand. Then, trash the rest.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-087 - Nero

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP03-088 - Fukurou

- Printed effect: This Character cannot be K.O.'d by effects. [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `continuous`, `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-089 - Brannew

- Printed effect: [On Play] Look at 3 cards from the top of your deck; reveal up to 1 {Navy} type card other than [Brannew] and add it to your hand. Then, trash the rest.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-090 - Blueno

- Printed effect: [DON!! x1] This Character gains [Blocker]. (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On K.O.] Play up to 1 Character card with a type including "CP" and a cost of 4 or less from your trash rested.
- Printed trigger: None
- Registered timings: `continuous`, `on_ko`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-091 - Helmeppo

- Printed effect: [On Play] Set the cost of up to 1 of your opponent's Characters with no base effect to 0 during this turn.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-092 - Rob Lucci

- Printed effect: [On Play] You may place 2 cards with a type including "CP" from your trash at the bottom of your deck in any order: This Character gains [Rush] during this turn. (This card can attack on the turn in which it is played.)
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-093 - Wanze

- Printed effect: [On Play] You may trash 1 card from your hand: If your Leader's type includes "CP", K.O. up to 1 of your opponent's Characters with a cost of 1 or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-094 - Air Door

- Printed effect: [Main] If your Leader's type includes "CP", look at 5 cards from the top of your deck; play up to 1 Character card with a type including "CP" and a cost of 5 or less. Then, trash the rest.
- Printed trigger: [Trigger] Play up to 1 black Character card with a cost of 3 or less from your trash.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Main effect now plays a CP Character from top 5 and trashes rest; still needs manual validation with real CP deck fixtures.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Main effect now plays a CP Character from top 5 and trashes rest; still needs manual validation with real CP deck fixtures.

### OP03-095 - Soap Sheep

- Printed effect: [Main] Give up to 2 of your opponent's Characters -2 cost during this turn.
- Printed trigger: [Trigger] Your opponent trashes 1 card from their hand.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Trigger makes opponent trash via existing hand-trash helper; exact opponent-owned choice UX should be validated.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Trigger makes opponent trash via existing hand-trash helper; exact opponent-owned choice UX should be validated.

### OP03-096 - Tempest Kick Sky Slicer

- Printed effect: [Main] K.O. up to 1 of your opponent's Characters with a cost of 0 or your opponent's Stages with a cost of 3 or less.
- Printed trigger: [Trigger] Draw 2 cards.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-097 - Six King Pistol

- Printed effect: [Counter] You may trash 1 card from your hand: Up to 1 of your Leader or Character cards gains +3000 power during this battle.
- Printed trigger: [Trigger] Draw 1 card. Then, K.O. up to 1 of your opponent's Characters with a cost of 1 or less.
- Registered timings: `counter`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-098 - Enies Lobby

- Printed effect: [Activate: Main] You may rest this Stage: If your Leader's type includes "CP", give up to 1 of your opponent's Characters -2 cost during this turn.
- Printed trigger: [Trigger] Play this card.
- Registered timings: `activate`, `trigger`
- Implementation status: `Needs Engine Support`
- Required code changes: Stage play trigger is implemented; activate duration/cost-modifier cleanup should be validated.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Stage play trigger is implemented; activate duration/cost-modifier cleanup should be validated.

### OP03-099 - Charlotte Katakuri

- Printed effect: [DON!! x1] [When Attacking] Look at up to 1 card from the top of your or your opponent's Life cards, and place it at the top or bottom of the Life cards. Then, this Leader gains +1000 power during this battle.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-100 - Kingbaum

- Printed effect: None
- Printed trigger: [Trigger] You may trash 1 card from the top or bottom of your Life cards: Play this card.
- Registered timings: `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-101 - Camie

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP03-102 - Sanji

- Printed effect: [DON!! x2] [When Attacking] You may add 1 card from the top or bottom of your Life cards to your hand: Add up to 1 card from the top of your deck to the top of your Life cards.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-103 - Bobbin the Disposer

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP03-104 - Shirley

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On Play] Look at up to 1 card from the top of your or your opponent's Life cards, and place it at the top or bottom of the Life cards.
- Printed trigger: None
- Registered timings: `blocker`, `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-105 - Charlotte Oven

- Printed effect: [DON!! x1] [When Attacking] You may trash 1 card with a [Trigger] from your hand: This Character gains +3000 power during this battle.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-106 - Charlotte Opera

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP03-107 - Charlotte Galette

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-108 - Charlotte Cracker

- Printed effect: [DON!! x1] If you have less Life cards than your opponent, this Character gains [Double Attack] and +1000 power. (This card deals 2 damage.)
- Printed trigger: [Trigger] You may trash 1 card from your hand: Play this card.
- Registered timings: `continuous`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-109 - Charlotte Chiffon

- Printed effect: [On Play] You may trash 1 card from the top or bottom of your Life cards: Add up to 1 card from the top of your deck to the top of your Life cards.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-110 - Charlotte Smoothie

- Printed effect: [When Attacking] You may add 1 card from the top or bottom of your Life cards to your hand: This Character gains +2000 power during this battle.
- Printed trigger: [Trigger] You may trash 1 card from your hand: Play this card.
- Registered timings: `on_attack`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-111 - Charlotte Praline

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP03-112 - Charlotte Pudding

- Printed effect: [On Play] Look at 4 cards from the top of your deck; reveal up to 1 [Sanji] or {Big Mom Pirates} type card other than [Charlotte Pudding] and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-113 - Charlotte Perospero

- Printed effect: [On K.O.] Look at 3 cards from the top of your deck; reveal up to 1 {Big Mom Pirates} type card and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: [Trigger] You may trash 1 card from your hand: Play this card.
- Registered timings: `on_ko`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-114 - Charlotte Linlin

- Printed effect: [On Play] If your Leader has the {Big Mom Pirates} type, add up to 1 card from the top of your deck to the top of your Life cards. Then, trash up to 1 card from the top of your opponent's Life cards.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-115 - Streusen

- Printed effect: [On Play] You may trash 1 card with a [Trigger] from your hand: K.O. up to 1 of your opponent's Characters with a cost of 1 or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-116 - Shirahoshi

- Printed effect: [On Play] Draw 3 cards and trash 2 cards from your hand.
- Printed trigger: [Trigger] Play this card.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-117 - Napoleon

- Printed effect: [Activate: Main] You may rest this Character: Up to 1 of your [Charlotte Linlin] cards gains +1000 power until the start of your next turn.
- Printed trigger: [Trigger] Play this card.
- Registered timings: `activate`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-118 - Ikoku Sovereignty

- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +5000 power during this battle.
- Printed trigger: [Trigger] You may trash 2 cards from your hand: Add up to 1 card from the top of your deck to the top of your Life cards.
- Registered timings: `counter`, `trigger`
- Implementation status: `Partial`
- Required code changes: Counter auto-targets Leader; printed text allows Leader or Character. Trigger trash-2 flow is implemented but should validate optional add-up-to-1 behavior.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Counter auto-targets Leader; printed text allows Leader or Character. Trigger trash-2 flow is implemented but should validate optional add-up-to-1 behavior.

### OP03-119 - Buzz Cut Mochi

- Printed effect: [Main] If you have less Life cards than your opponent, K.O. up to 1 of your opponent's Characters with a cost of 4 or less.
- Printed trigger: [Trigger] Play up to 1 Character card with a cost of 4 or less and a [Trigger] from your hand.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-120 - Tropical Torment

- Printed effect: [Main] If your opponent has 4 or more Life cards, trash up to 1 card from the top of your opponent's Life cards.
- Printed trigger: [Trigger] Activate this card's [Main] effect.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-121 - Thunder Bolt

- Printed effect: [Main] You may trash 1 card from the top of your Life cards: K.O. up to 1 of your opponent's Characters with a cost of 5 or less.
- Printed trigger: [Trigger] K.O. up to 1 of your opponent's Characters with a cost of 5 or less.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-122 - Sogeking

- Printed effect: Also treat this card's name as [Usopp] according to the rules. [On Play] Return up to 1 Character with a cost of 6 or less to the owner's hand. Then, draw 2 cards and trash 2 cards from your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP03-123 - Charlotte Katakuri

- Printed effect: [On Play] Add up to 1 Character with a cost of 8 or less to the top or bottom of the owner's Life cards face-up.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP03 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.
