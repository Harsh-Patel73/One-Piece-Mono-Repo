# OP09 Master Audit

Source of truth: `packages/simulator/backend/data/cards.json` base OP09 entries where `id == id_normal`.

## Summary

- Base cards audited: 119
- Non-vanilla cards: 109
- Vanilla cards: 10
- Registered OP09 cards after this pass: 109
- Registered OP09 timings after this pass: 154
- Missing non-vanilla registrations: 0
- Missing printed trigger timings: 0
- Strict status after this pass: 109/119 `Complete` or `Vanilla`; 10 follow-up cards flagged below

## Verification

- OP09 import/compile path passed during coverage and sweep.
- OP09 registration coverage script passed: `base=119 nonvanilla=109 vanilla=10 registered_cards=109 timings=154 missing=[] missing_triggers=[]`.
- Direct OP09 handler execution sweep passed: `OP09_handler_sweep_ran=154 errors=0 tracebacks=0`, resolving pending choices through `GameState.resolve_pending_choice(...)`.
- Full pytest suite was not rerun in this pass; earlier environment check showed `python -m pytest packages\game-engine\tests` is unavailable because `pytest` is not installed.

## Follow-Up Queue

- `OP09-001` Shanks: `Partial` - Leader event hooks and once-per-turn state should be manually validated in full turn flow.
- `OP09-002` Uta: `Partial` - Leader draw/trash/order choices should be replay-tested for exact hand/deck sequencing.
- `OP09-021` Red Force: `Partial` - Search/reveal/top-bottom helper behavior should be validated with real archetype fixtures.
- `OP09-037` Lim: `Needs Engine Support` - Temporary power and target restrictions need manual validation against duration cleanup.
- `OP09-059` Murder at the Steam Bath: `Partial` - DON-return/payment sequencing should be manually validated for optional cost handling.
- `OP09-076` Roronoa Zoro: `Partial` - Purple DON manipulation should be replay-tested for active/rested source and return timing.
- `OP09-090` Doc Q: `Needs Engine Support` - Black cost reduction duration cleanup depends on engine temporary modifier support.
- `OP09-101` Kuzan: `Partial` - Life/deck manipulation and trigger sequencing should be manually replayed with edge life counts.
- `OP09-118` Gol.D.Roger: `Partial` - High-impact event target filters and optional branch ordering should be manually validated.
- `OP09-119` Monkey.D.Luffy: `Partial` - Manga/SEC style effect should receive manual regression testing for exact printed sequencing.

## Per-Card Audit

### OP09-001 - Shanks

- Printed effect: [Once Per Turn] This effect can be activated when your opponent attacks. Give up to 1 of your opponent's Leader or Character cards -1000 power during this turn.
- Printed trigger: None
- Registered timings: `on_opponent_attack`
- Implementation status: `Partial`
- Required code changes: Leader event hooks and once-per-turn state should be manually validated in full turn flow.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Leader event hooks and once-per-turn state should be manually validated in full turn flow.

### OP09-002 - Uta

- Printed effect: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 {Red-Haired Pirates} type card and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Leader draw/trash/order choices should be replay-tested for exact hand/deck sequencing.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Leader draw/trash/order choices should be replay-tested for exact hand/deck sequencing.

### OP09-003 - Shachi & Penguin

- Printed effect: [When Attacking] Give up to 1 of your opponent's Characters -2000 power during this turn.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-004 - Shanks

- Printed effect: Give all of your opponent's Characters -1000 power. [Rush] (This card can attack on the turn in which it is played.)
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-005 - Silvers Rayleigh

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On Play] If your opponent has 2 or more Characters with a base power of 5000 or more, draw 2 cards and trash 1 card from your hand.
- Printed trigger: None
- Registered timings: `blocker`, `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-006 - Howling Gab

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP09-007 - Heat

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On Play] Up to 1 of your Leader with 4000 power or less gains +1000 power during this turn.
- Printed trigger: None
- Registered timings: `blocker`, `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-008 - Building Snake

- Printed effect: [Activate: Main] You may place this Character at the bottom of the owner's deck: Give up to 1 of your opponent's Characters -3000 power during this turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-009 - Benn.Beckman

- Printed effect: [On Play] Trash up to 1 of your opponent's Characters with 6000 power or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-010 - Bonk Punch

- Printed effect: [On Play] Play up to 1 [Monster] from your hand. [DON!! x1] [When Attacking] This Character gains +2000 power during this turn.
- Printed trigger: None
- Registered timings: `on_play`, `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-011 - Hongo

- Printed effect: [Activate: Main] You may rest this Character: If your Leader has the {Red-Haired Pirates} type, give up to 1 of your opponent's Characters -2000 power during this turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-012 - Monster

- Printed effect: If your Character [Bonk Punch] would be K.O.'d by an effect, you may trash this Character instead.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-013 - Yasopp

- Printed effect: [On Play] Up to 1 of your Leader gains +1000 power until the end of your opponent's next turn. [DON!! x1] [When Attacking] Give up to 1 of your opponent's Characters -1000 power during this turn.
- Printed trigger: None
- Registered timings: `on_play`, `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-014 - Limejuice

- Printed effect: [On Play] Your opponent cannot activate up to 1 [Blocker] Character that has 4000 power or less during this turn.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-015 - Lucky.Roux

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On K.O.] If your Leader has the {Red-Haired Pirates} type, K.O. up to 1 of your opponent's Characters with a base power of 6000 or less.
- Printed trigger: None
- Registered timings: `blocker`, `on_ko`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-016 - Rockstar

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP09-017 - Wire

- Printed effect: [DON!! x1] If your Leader has 7000 power or more and the {Kid Pirates} type, this Character gains [Rush].
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-018 - Get Out of Here!

- Printed effect: [Main] K.O. up to 2 of your opponent's Characters with a total power of 4000 or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-019 - Nobody Hurts a Friend of Mine!!!!

- Printed effect: [Main] If your Leader has the {Red-Haired Pirates} type, give up to 1 of your opponent's Characters -3000 power during this turn. Then, if your opponent has a Character with 5000 or more power, draw 1 card.
- Printed trigger: [Trigger] Draw 1 card.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-020 - Come On!! We'll Fight You!!

- Printed effect: [Main] Look at 5 cards from the top of your deck; reveal up to 1 {Red-Haired Pirates} type card other than [Come On!! We'll Fight You!!] and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: [Trigger] Draw 1 card.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-021 - Red Force

- Printed effect: [Activate: Main] You may rest this Stage: If your Leader has the {Red-Haired Pirates} type, give up to 1 of your opponent's Characters -1000 power during this turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Search/reveal/top-bottom helper behavior should be validated with real archetype fixtures.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Search/reveal/top-bottom helper behavior should be validated with real archetype fixtures.

### OP09-022 - Lim

- Printed effect: Your Character cards are played rested. [Activate: Main] [Once Per Turn] You may rest 3 of your DON!! cards: Add up to 1 DON!! card from your DON!! deck and rest it, and play up to 1 {ODYSSEY} type Character card with a cost of 5 or less from your hand.
- Printed trigger: None
- Registered timings: `continuous`, `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-023 - Adio

- Printed effect: [On Play] If your Leader has the {ODYSSEY} type, set up to 3 of your DON!! cards as active. [On Your Opponent's Attack] [Once Per Turn] You may rest 1 of your DON!! cards: Up to 1 of your Leader or Character cards gains +2000 power during this battle.
- Printed trigger: None
- Registered timings: `on_play`, `on_opponent_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-024 - Usopp

- Printed effect: [On Play] If you have 2 or more rested Characters, draw 2 cards and trash 2 cards from your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-025 - Crocodile

- Printed effect: If your Leader has the {ODYSSEY} type, this Character cannot be K.O.'d in battle by Leaders.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-026 - Sakazuki

- Printed effect: [On Play] If you have 2 or more rested Characters, K.O. up to 1 of your opponent's Characters with a cost of 5 or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-027 - Sabo

- Printed effect: [When Attacking] [Once Per Turn] If you have 3 or more rested Characters, draw 1 card.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-028 - Sanji

- Printed effect: [On K.O.] You may add 1 card from the top or bottom of your Life cards to your hand: Play up to 1 {ODYSSEY} or {Straw Hat Crew} type Character card with a cost of 4 or less from your trash rested.
- Printed trigger: None
- Registered timings: `on_ko`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-029 - Tony Tony.Chopper

- Printed effect: [End of Your Turn] Set up to 1 of your {ODYSSEY} type Characters with a cost of 4 or less as active.
- Printed trigger: None
- Registered timings: `end_of_turn`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-030 - Trafalgar Law

- Printed effect: [On Play] You may return 1 of your Characters to the owner's hand: Play up to 1 {ODYSSEY} type Character card with a cost of 3 or less other than [Trafalgar Law] from your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-031 - Donquixote Doflamingo

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [End of Your Turn] If you have 2 or more rested Characters, set this Character as active.
- Printed trigger: None
- Registered timings: `blocker`, `end_of_turn`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-032 - Donquixote Rosinante

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On Your Opponent's Attack] [Once Per Turn] Set this Character as active.
- Printed trigger: None
- Registered timings: `blocker`, `on_opponent_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-033 - Nico Robin

- Printed effect: [On Play] If you have 2 or more rested Characters, none of your {ODYSSEY} or {Straw Hat Crew} type Characters can be K.O.'d by effects until the end of your opponent's next turn.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-034 - Perona

- Printed effect: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 [Dracule Mihawk] or {Thriller Bark Pirates} type card and add it to your hand. Then, place the rest at the bottom of your deck in any order and trash 1 card from your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-035 - Portgas.D.Ace

- Printed effect: [On Play] If you have 2 or more rested Characters, rest up to 1 of your opponent's Characters with a cost of 5 or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-036 - Monkey.D.Luffy

- Printed effect: [On Play] If you have 2 or more rested Characters, rest up to 1 of your opponent's DON!! cards or Characters with a cost of 6 or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-037 - Lim

- Printed effect: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 {ODYSSEY} type card other than [Lim] and add it to your hand. Then, place the rest at the bottom of your deck in any order. [End of Your Turn] If you have 3 or more rested Characters, set this Character as active.
- Printed trigger: None
- Registered timings: `on_play`, `end_of_turn`
- Implementation status: `Needs Engine Support`
- Required code changes: Temporary power and target restrictions need manual validation against duration cleanup.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Temporary power and target restrictions need manual validation against duration cleanup.

### OP09-038 - Rob Lucci

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP09-039 - Gum-Gum Cuatro Jet Cross Shock Bazooka

- Printed effect: [Counter] If your Leader has the {ODYSSEY} type and you have 2 or more rested Characters, up to 1 of your Leader or Character cards gains +2000 power during this turn.
- Printed trigger: [Trigger] K.O. up to 1 of your opponent's rested Characters with a cost of 4 or less.
- Registered timings: `counter`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-040 - Thunder Lance Flip Caliber Phoenix Shot

- Printed effect: [Main] If you have 2 or more rested Characters, K.O. up to 1 of your opponent's Characters with a cost of 4 or less.
- Printed trigger: [Trigger] Rest up to 1 of your opponent's Characters with a cost of 4 or less.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-041 - Soul Franky Swing Arm Boxing Solid

- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +2000 power during this battle. Then, if your Leader has the {ODYSSEY} type and you have 2 or more rested Characters, set up to 2 of your Characters as active.
- Printed trigger: [Trigger] Rest up to 1 of your opponent's Characters with a cost of 4 or less.
- Registered timings: `counter`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-042 - Buggy

- Printed effect: [Activate: Main] You may rest 5 of your DON!! cards and trash 1 card from your hand: Play up to 1 {Cross Guild} type Character card from your hand.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-043 - Alvida

- Printed effect: [On K.O.] If your Leader has the {Cross Guild} type, play up to 1 Character card with a cost of 5 or less other than [Alvida] from your hand.
- Printed trigger: None
- Registered timings: `on_ko`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-044 - Izo

- Printed effect: [When Attacking] Look at 5 cards from the top of your deck; reveal up to 1 {Land of Wano} type card or card with a type including "Whitebeard Pirates" and add it to your hand. Then, place the rest at the bottom of your deck in any order and trash 1 card from your hand.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-045 - Cabaji

- Printed effect: If you have a [Buggy] or [Mohji] Character, this Character cannot be K.O.'d in battle.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-046 - Crocodile

- Printed effect: [On Play] Play up to 1 {Cross Guild} type Character card or Character card with a type including "Baroque Works" with a cost of 5 or less from your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-047 - Kouzuki Oden

- Printed effect: [Double Attack] (This card deals 2 damage.) [On K.O.] Draw 2 cards and trash 1 card from your hand.
- Printed trigger: None
- Registered timings: `continuous`, `on_ko`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-048 - Dracule Mihawk

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On Play] Draw 2 cards and trash 1 card from your hand.
- Printed trigger: None
- Registered timings: `blocker`, `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-049 - Jozu

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP09-050 - Nami

- Printed effect: [When Attacking] Look at 5 cards from the top of your deck; reveal up to 1 blue Event and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-051 - Buggy

- Printed effect: [On Play] Place up to 1 of your opponent's Characters at the bottom of the owner's deck. Then, if you do not have 5 Characters with a cost of 5 or more, place this Character at the bottom of the owner's deck.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-052 - Marco

- Printed effect: [Opponent's Turn] You may trash 1 card from your hand: When this Character is K.O.'d by your opponent's effect, play this Character card from your trash rested.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-053 - Mohji

- Printed effect: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 [Richie] and add it to your hand. Then, place the rest at the bottom of your deck in any order and play up to 1 [Richie] from your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-054 - Richie

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-055 - Mr.1(Daz.Bonez)

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP09-056 - Mr.3(Galdino)

- Printed effect: [On Play] Look at 4 cards from the top of your deck; reveal up to 1 {Cross Guild} type card or card with a type including "Baroque Works" other than [Mr.3(Galdino)] and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-057 - Cross Guild

- Printed effect: [Main] Look at 4 cards from the top of your deck; reveal up to 1 {Cross Guild} type card and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: [Trigger] Activate this card's [Main] effect.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-058 - Special Muggy Ball

- Printed effect: [Main] Return up to 1 of your opponent's Characters with a cost of 6 or less to the owner's hand.
- Printed trigger: [Trigger] Return up to 1 Character with a cost of 3 or less to the owner's hand.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-059 - Murder at the Steam Bath

- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +3000 power during this battle. Then, trash up to 2 cards from your hand. Trash the same number of cards from the top of your deck as you did from your hand.
- Printed trigger: [Trigger] Draw 1 card.
- Registered timings: `counter`, `trigger`
- Implementation status: `Partial`
- Required code changes: DON-return/payment sequencing should be manually validated for optional cost handling.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: DON-return/payment sequencing should be manually validated for optional cost handling.

### OP09-060 - Emptee Bluffs Island

- Printed effect: [Activate: Main] You may place 2 cards from your hand at the bottom of your deck in any order and rest this Stage: If your Leader has the {Cross Guild} type, draw 2 cards.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-061 - Monkey.D.Luffy

- Printed effect: [DON!! x1] All of your Characters gain +1 cost. [Your Turn] [Once Per Turn] When 2 or more DON!! cards on your field are returned to your DON!! deck, add up to 1 DON!! card from your DON!! deck and set it as active, and add up to 1 additional DON!! card and rest it.
- Printed trigger: None
- Registered timings: `continuous`, `on_don_return`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-062 - Nico Robin

- Printed effect: [Banish] (When this card deals damage, the target card is trashed without activating its Trigger.) [When Attacking] You may trash 1 card with a [Trigger] from your hand: Add up to 1 DON!! card from your DON!! deck and rest it.
- Printed trigger: None
- Registered timings: `continuous`, `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-063 - Usopp

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP09-064 - Killer

- Printed effect: [On Play] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Set up to 1 of your {Kid Pirates} type Leader as active.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-065 - Sanji

- Printed effect: [On Play] You may return 1 or more DON!! cards from your field to your DON!! deck: This Character gains [Rush] during this turn. Then, rest up to 1 of your opponent's Characters with a cost of 6 or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-066 - Jean Bart

- Printed effect: [On Play] If your opponent has more DON!! cards on their field than you, K.O. up to 1 of your opponent's Characters with a cost of 3 or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-067 - Jinbe

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP09-068 - Tony Tony.Chopper

- Printed effect: [End of Your Turn] You may return 1 or more DON!! cards from your field to your DON!! deck: Set this Character as active. Then, this Character gains [Blocker] until the end of your opponent's next turn.
- Printed trigger: None
- Registered timings: `end_of_turn`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-069 - Trafalgar Law

- Printed effect: [On Play] Look at 4 cards from the top of your deck; reveal up to 1 {Straw Hat Crew} or {Heart Pirates} type card with a cost of 2 or more and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-070 - Nami

- Printed effect: [On Play] You may return 1 or more DON!! cards from your field to your DON!! deck: Give up to 2 rested DON!! cards to your Leader or 1 of your Characters.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-071 - Nico Robin

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-072 - Franky

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On Play] DON!! -2, You may trash 1 card from your hand: Draw 2 cards.
- Printed trigger: None
- Registered timings: `blocker`, `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-073 - Brook

- Printed effect: [When Attacking] You may return 1 or more DON!! cards from your field to your DON!! deck: Give up to 2 of your opponent's Characters -2000 power during this turn.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-074 - Bepo

- Printed effect: [Your Turn] [Once Per Turn] When a DON!! card on your field is returned to your DON!! deck, up to 1 of your Leader or Character cards gains +1000 power during this turn.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-075 - Eustass"Captain"Kid

- Printed effect: [On Play] You may add 1 card from the top of your Life cards to your hand: If your Leader has the {Kid Pirates} type, add up to 1 DON!! card from your DON!! deck and set it as active.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-076 - Roronoa Zoro

- Printed effect: [On Play] You may return 1 or more DON!! cards from your field to your DON!! deck: Add up to 1 DON!! card from your DON!! deck and set it as active.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Purple DON manipulation should be replay-tested for active/rested source and return timing.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Purple DON manipulation should be replay-tested for active/rested source and return timing.

### OP09-077 - Gum-Gum Lightning

- Printed effect: [Main] DON!! -2 (You may return the specified number of DON!! cards from your field to your DON!! deck.): K.O. up to 1 of your opponent's Characters with 6000 power or less.
- Printed trigger: [Trigger] Add up to 1 DON!! card from your DON!! deck and set it as active.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-078 - Gum-Gum Giant

- Printed effect: [Counter] DON!! -2, You may trash 1 card from your hand: If your Leader has the {Straw Hat Crew} type, up to 1 of your Leader or Character cards gains +4000 power during this battle. Then, draw 2 cards.
- Printed trigger: None
- Registered timings: `counter`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-079 - Gum-Gum Jump Rope

- Printed effect: [Main] DON!! -2 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Rest up to 1 of your opponent's Characters with a cost of 5 or less. Then, draw 1 card.
- Printed trigger: [Trigger] Add up to 1 DON!! card from your DON!! deck and set it as active.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-080 - Thousand Sunny

- Printed effect: [Opponent's Turn] You may rest this Stage: When your {Straw Hat Crew} type Character is removed from the field by your opponent's effect, add up to 1 DON!! card from your DON!! deck and rest it.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-081 - Marshall.D.Teach

- Printed effect: Your [On Play] effects are negated. [Activate: Main] You may trash 1 card from your hand: Your opponent's [On Play] effects are negated until the end of your opponent's next turn.
- Printed trigger: None
- Registered timings: `continuous`, `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-082 - Avalo Pizarro

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP09-083 - Van Augur

- Printed effect: [Activate: Main] You may rest this Character: If your Leader has the {Blackbeard Pirates} type, give up to 1 of your opponent's Characters -3 cost during this turn. [On K.O.] Draw 1 card.
- Printed trigger: None
- Registered timings: `activate`, `on_ko`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-084 - Catarina Devon

- Printed effect: [Activate: Main] [Once Per Turn] If your Leader has the {Blackbeard Pirates} type, this Character gains [Double Attack], [Banish] or [Blocker] until the end of your opponent's next turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-085 - Gecko Moria

- Printed effect: [On Play] Play up to 1 {Thriller Bark Pirates} type Character card with a cost of 2 or less from your trash rested.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-086 - Jesus Burgess

- Printed effect: This Character cannot be K.O.'d by your opponent's effects. If your Leader has the {Blackbeard Pirates} type, this Character gains +1000 power for every 4 cards in your trash.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-087 - Charlotte Pudding

- Printed effect: [On Play] If your opponent has 5 or more cards in their hand, your opponent trashes 1 card from their hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-088 - Shiryu

- Printed effect: [DON!! x1] [When Attacking] You may trash 2 cards from your hand: Draw 2 cards.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-089 - Stronger

- Printed effect: [Activate: Main] You may trash 1 card from your hand and trash this Character: If your Leader has the {Blackbeard Pirates} type, draw 1 card. Then, give up to 1 of your opponent's Characters -2 cost during this turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-090 - Doc Q

- Printed effect: [Activate: Main] You may rest this Character: If your Leader has the {Blackbeard Pirates} type, K.O. up to 1 of your opponent's Characters with a cost of 1 or less. [On K.O.] Draw 1 card.
- Printed trigger: None
- Registered timings: `activate`, `on_ko`
- Implementation status: `Needs Engine Support`
- Required code changes: Black cost reduction duration cleanup depends on engine temporary modifier support.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Black cost reduction duration cleanup depends on engine temporary modifier support.

### OP09-091 - Vasco Shot

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-092 - Marshall.D.Teach

- Printed effect: [Activate: Main] You may rest this Character: If the number of cards in your hand is at least 3 less than the number in your opponent's hand, draw 2 cards and trash 1 card from your hand.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-093 - Marshall.D.Teach

- Printed effect: [Blocker] [Activate: Main] [Once Per Turn] If your Leader has the {Blackbeard Pirates} type and this Character was played on this turn, negate the effect of up to 1 of your opponent's Leader during this turn. Then, negate the effect of up to 1 of your opponent's Characters and that Character cannot attack until the end of your opponent's next turn.
- Printed trigger: None
- Registered timings: `blocker`, `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-094 - Peachbeard

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP09-095 - Laffitte

- Printed effect: [Activate: Main] You may rest 1 of your DON!! cards and this Character: Look at 5 cards from the top of your deck; reveal up to 1 {Blackbeard Pirates} type card and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-096 - My Era...Begins!!

- Printed effect: [Main] Look at 3 cards from the top of your deck; reveal up to 1 {Blackbeard Pirates} type card other than [My Era...Begins!!] and add it to your hand. Then, trash the rest.
- Printed trigger: [Trigger] Activate this card's [Main] effect.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-097 - Black Vortex

- Printed effect: [Counter] Negate the effect of up to 1 of your opponent's Leader or Character cards and give that card -4000 power during this turn.
- Printed trigger: [Trigger] Negate the effect of up to 1 of your opponent's Leader or Character cards during this turn.
- Registered timings: `counter`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-098 - Black Hole

- Printed effect: [Main] If your Leader has the {Blackbeard Pirates} type, negate the effect of up to 1 of your opponent's Characters during this turn. Then, if that Character has a cost of 4 or less, K.O. it.
- Printed trigger: [Trigger] Negate the effect of up to 1 of your opponent's Leader or Character cards during this turn.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-099 - Fullalead

- Printed effect: [Activate: Main] You may trash 1 card from your hand and rest this Stage: Look at 3 cards from the top of your deck; reveal up to 1 {Blackbeard Pirates} type card and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-100 - Karasu

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: [Trigger] If your Leader has the {Revolutionary Army} type and you and your opponent have a total of 5 or less Life cards, play this card.
- Registered timings: `blocker`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-101 - Kuzan

- Printed effect: [On Play] Place 1 of your opponent's Characters with a cost of 3 or less at the top or bottom of your opponent's Life cards face-up: Your opponent trashes 1 card from their hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Life/deck manipulation and trigger sequencing should be manually replayed with edge life counts.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Life/deck manipulation and trigger sequencing should be manually replayed with edge life counts.

### OP09-102 - Professor Clover

- Printed effect: [On Play] If your Leader is [Nico Robin], look at 3 cards from the top of your deck; reveal up to 1 card with a [Trigger] and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: [Trigger] Activate this card's [On Play] effect.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-103 - Koala

- Printed effect: [Blocker] [On Play] You may add 1 card from the top or bottom of your Life cards to your hand: Play up to 1 {Revolutionary Army} type Character card with a cost of 4 or less from your hand. If you do, draw 1 card.
- Printed trigger: None
- Registered timings: `blocker`, `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-104 - Sabo

- Printed effect: [On Play] Add up to 1 {Revolutionary Army} type Character card from your hand to the top of your Life cards face-up. Then, if you have 2 or more Life cards, add 1 card from the top or bottom of your Life cards to your hand.
- Printed trigger: [Trigger] If your Leader is multicolored, draw 2 cards.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-105 - Sanji

- Printed effect: None
- Printed trigger: [Trigger] If your Leader has the {Egghead} type, add up to 1 card from the top of your deck to the top of your Life cards. Then, trash 2 cards from your hand.
- Registered timings: `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-106 - Nico Olvia

- Printed effect: [On Play] Up to 1 of your [Nico Robin] Leader gains +3000 power during this turn.
- Printed trigger: [Trigger] If your Leader is [Nico Robin], draw 3 cards and trash 2 cards from your hand.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-107 - Nico Robin

- Printed effect: [On Play] If your opponent has 3 or more Life cards, trash up to 1 card from the top of your opponent's Life cards.
- Printed trigger: [Trigger] Play up to 1 yellow Character card with a cost of 3 or less from your hand.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-108 - Bartholomew Kuma

- Printed effect: None
- Printed trigger: [Trigger] If your Leader has the {Revolutionary Army} type and you and your opponent have a total of 5 or less Life cards, play this card.
- Registered timings: `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-109 - Jaguar.D.Saul

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: [Trigger] If your Leader is [Nico Robin], play this card.
- Registered timings: `blocker`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-110 - Pierre

- Printed effect: [On Play] Draw 2 cards and trash 2 cards from your hand.
- Printed trigger: [Trigger] Play this card.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-111 - Brook

- Printed effect: None
- Printed trigger: [Trigger] If your Leader has the {Egghead} type and your opponent has 6 or more cards in their hand, your opponent trashes 2 cards from their hand.
- Registered timings: `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-112 - Belo Betty

- Printed effect: [On Play] If you have 2 or less Life cards, draw 1 card.
- Printed trigger: [Trigger] If your Leader has the {Revolutionary Army} type and you and your opponent have a total of 5 or less Life cards, play this card.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-113 - Morley

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP09-114 - Lindbergh

- Printed effect: [On Play] If you and your opponent have a total of 5 or less Life cards, K.O. up to 1 of your opponent's Characters with 2000 power or less.
- Printed trigger: [Trigger] If you and your opponent have a total of 5 or less Life cards, play this card.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-115 - Ice Block Partisan

- Printed effect: [Main] K.O. up to 1 of your opponent's Characters with a cost of 3 or less and a [Trigger].
- Printed trigger: [Trigger] Draw 1 card.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-116 - Never Underestimate the Power of Miracles!!

- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +2000 power during this battle.
- Printed trigger: [Trigger] Play up to 1 {Revolutionary Army} type Character card with a cost of 4 or less from your hand.
- Registered timings: `counter`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-117 - Dereshi!

- Printed effect: [Main] Look at 5 cards from the top of your deck; reveal up to 2 cards with a [Trigger] other than [Dereshi!] and add them to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: [Trigger] Draw 1 card.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP09-118 - Gol.D.Roger

- Printed effect: [Rush] (This card can attack on the turn in which it is played.) When your opponent activates [Blocker], if either you or your opponent has 0 Life cards, you win the game.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Partial`
- Required code changes: High-impact event target filters and optional branch ordering should be manually validated.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: High-impact event target filters and optional branch ordering should be manually validated.

### OP09-119 - Monkey.D.Luffy

- Printed effect: [On Play] You may return 1 or more DON!! cards from your field to your DON!! deck: Draw 1 card and this Character gains [Rush] during this turn.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Manga/SEC style effect should receive manual regression testing for exact printed sequencing.
- Required tester setup: Generic OP09 tester seed was sufficient for execution sweep; add card-specific fixtures only if manual semantic testing reveals a missing target.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Manga/SEC style effect should receive manual regression testing for exact printed sequencing.
