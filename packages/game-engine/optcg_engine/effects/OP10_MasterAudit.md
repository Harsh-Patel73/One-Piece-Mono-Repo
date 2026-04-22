# OP10 Master Audit

Source of truth: `packages/simulator/backend/data/cards.json` base OP10 entries where `id == id_normal`.

## Summary

- Base cards audited: 119
- Non-vanilla cards: 108
- Vanilla cards: 11
- Registered OP10 cards after this pass: 108
- Registered OP10 timings after this pass: 144
- Missing non-vanilla registrations before this pass: 70
- Missing printed trigger timings before this pass: 18
- Missing non-vanilla registrations after this pass: 0
- Missing printed trigger timings after this pass: 0
- Strict status after this pass: 47/119 `Complete` or `Vanilla`; 72 generic follow-up cards flagged below
- Note: OP10 uses a broad generic fallback for many previously missing cards; those are intentionally flagged for exact bespoke follow-up.

## Verification

- `python -m py_compile packages\game-engine\optcg_engine\effects\sets\op10_effects.py` passed.
- OP10 registration coverage script passed: `base=119 nonvanilla=108 vanilla=11 registered_cards=108 timings=144 missing=[] missing_triggers=[]`.
- Direct OP10 handler execution sweep passed: `OP10_handler_sweep_ran=144 errors=0 tracebacks=0`, resolving pending choices through `GameState.resolve_pending_choice(...)`.
- Full pytest suite was not rerun in this pass; earlier environment check showed `python -m pytest packages\game-engine\tests` is unavailable because `pytest` is not installed.

## Follow-Up Queue

- `OP10-009` Smiley: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-010` Chadros.Higelyges (Brownbeard): `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-015` Mocha: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-016` Monet: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-017` Rock: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-018` Ten-Layer Igloo: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-019` Divine Departure: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-020` Gum-Gum UFO: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-021` Punk Hazard: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-023` Issho: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-025` Enel: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-026` Kin'emon: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-027` Kin'emon: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-030` Smoker: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-032` Tashigi: `Needs Engine Support` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-033` Nami: `Needs Engine Support` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-034` Franky: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-035` Brook: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-036` Perona: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-037` Lim: `Needs Engine Support` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-038` Roronoa Zoro: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-039` Gum-Gum Dragon Fire Pistol Twister Star: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-041` Radio Knife: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-044` Cub: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-045` Cavendish: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-046` Kyros: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-048` Sai: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-049` Sabo: `Needs Engine Support` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-052` Bartolomeo: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-055` Marco: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-056` Mansherry: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-058` Rebecca: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-060` Barrier-Barrier Pistol: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-061` Special Long-Range Attack!! Bagworm: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-062` Violet: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-063` Vinsmoke Sanji: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-066` Giolla: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-067` Senor Pink: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-069` Fighting Fish: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-070` Trebol: `Needs Engine Support` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-071` Donquixote Doflamingo: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-072` Donquixote Rosinante: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-075` Foxy: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-079` God Thread: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-080` Little Black Bears: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-081` Usopp: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-082` Kuzan: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-083` Kouzuki Momonosuke: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-086` Shiryu: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-087` Tony Tony.Chopper: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-088` Nami: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-090` Franky: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-091` Brook: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-092` Perona: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-093` Saint Homing: `Needs Engine Support` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-094` Ryuma: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-095` Roronoa Zoro: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-096` There's No Longer Any Need for the Seven Warlords of the Sea!!!: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-097` Gum-Gum Rhino Schneider: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-098` Liberation: `Needs Engine Support` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-100` Inazuma: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-102` Emporio.Ivankov: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-104` Caribou: `Needs Engine Support` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-109` Basil Hawkins: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-110` Heat & Wire: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-113` Roronoa Zoro: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-114` X.Drake: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-115` Let's Meet Again in the New World: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-116` Damned Punk: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-117` ROOM: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-118` Monkey.D.Luffy: `Needs Engine Support` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP10-119` Trafalgar Law: `Partial` - Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

## Per-Card Audit

### OP10-001 - Smoker

- Printed effect: [Opponent's Turn] All of your {Navy} or {Punk Hazard} type Characters gain +1000 power. [Activate: Main] [Once Per Turn] If you have a Character with 7000 power or more, set up to 2 of your DON!! cards as active.
- Printed trigger: None
- Registered timings: `opponent_turn`, `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-002 - Caesar Clown

- Printed effect: [DON!! x2] [When Attacking] You may return 1 of your {Punk Hazard} type Characters with a cost of 2 or more to the owner's hand: K.O. up to 1 of your opponent's Characters with 4000 power or less.
- Printed trigger: None
- Registered timings: `WHEN_ATTACKING`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-003 - Sugar

- Printed effect: [End of Your Turn] If you have a {Donquixote Pirates} type Character with 6000 power or more, set up to 1 of your DON!! cards as active. [Opponent's Turn] [Once Per Turn] When you activate an Event, add up to 1 DON!! card from your DON!! deck and set it as active.
- Printed trigger: None
- Registered timings: `end_of_turn`, `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-004 - Vergo

- Printed effect: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 {Punk Hazard} type card other than [Vergo] and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-005 - Sanji

- Printed effect: [Your Turn] This Character gains +3000 power. [On K.O.] Draw 1 card.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-006 - Caesar Clown

- Printed effect: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 [Smiley] and add it to your hand. Then, place the rest at the bottom of your deck in any order and play up to 1 [Smiley] from your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-007 - Ceaser Soldier

- Printed effect: [On Play] Play up to 1 {Punk Hazard} type Character card with a cost of 2 or less from your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-008 - Scotch

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On Play] If you don't have [Rock], play up to 1 [Rock] from your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-009 - Smiley

- Printed effect: [On Play] If your Leader has the {Punk Hazard} type, give up to 1 of your opponent's Characters -3000 power during this turn.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-010 - Chadros.Higelyges (Brownbeard)

- Printed effect: [When Attacking] If you have 1 or less Characters with 6000 power or more, this Character gains +1000 power during this turn.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-011 - Tony Tony.Chopper

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [Opponent's Turn] This Character gains +2000 power.
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-012 - Dragon Number Thirteen

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-013 - Nami

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP10-014 - Franky

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP10-015 - Mocha

- Printed effect: [On Play] Give up to 1 of your opponent's Characters -1000 power during this turn.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-016 - Monet

- Printed effect: [Activate: Main] You may rest this Character: Give up to 2 rested DON!! cards to your Leader or 1 of your Characters. Then, give up to 1 of your opponent's Characters -1000 power during this turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-017 - Rock

- Printed effect: [On Play] If you don't have [Scotch], play up to 1 [Scotch] from your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-018 - Ten-Layer Igloo

- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +3000 power during this battle. Then, give up to 1 of your opponent's Leader or Character cards -2000 power during this turn.
- Printed trigger: [Trigger] Up to 1 of your Leader or Character cards gains +1000 power during this turn.
- Registered timings: `counter`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-019 - Divine Departure

- Printed effect: [Main] You may rest 5 of your DON!! cards: K.O. up to 1 of your opponent's Characters with 8000 power or less. [Counter] Up to 1 of your Leader gains +3000 power during this battle.
- Printed trigger: None
- Registered timings: `counter`, `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-020 - Gum-Gum UFO

- Printed effect: [Main] Give up to 1 of your opponent's Characters -4000 power during this turn. Then, if you have 2 or less Life cards, up to 1 of your Leader or Character cards gains +1000 power during this turn.
- Printed trigger: [Trigger] K.O. up to 1 of your opponent's Characters with 3000 power or less.
- Registered timings: `MAIN`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-021 - Punk Hazard

- Printed effect: [Activate: Main] You may rest this Stage: If your Leader is [Caesar Clown], give up to 1 rested DON!! card to your Leader or 1 of your Characters.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-022 - Trafalgar Law

- Printed effect: [DON!! x1] [Activate: Main] [Once Per Turn] If the total cost of your Characters is 5 or more, you may return 1 of your Characters to the owner's hand: Reveal 1 card from the top of your Life cards. If that card is a {Supernovas} type Character card with a cost of 5 or less, you may play that card.
- Printed trigger: None
- Registered timings: `activate`, `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-023 - Issho

- Printed effect: [On Play] If your Leader has the {Navy} type, rest up to 2 of your opponent's Characters with a cost of 5 or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-024 - Edward.Newgate

- Printed effect: [On Play] If you have 2 or more rested Characters, rest up to 1 of your opponent's Characters with a cost of 5 or less. Then, K.O. up to 1 of your opponent's rested Characters with a cost of 3 or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-025 - Enel

- Printed effect: [On Play] If you have 2 or more rested Characters, draw 3 cards and trash 2 cards from your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-026 - Kin'emon

- Printed effect: [Activate: Main] You may place this Character and 1 [Kin'emon] with 0 power from your trash at the bottom of your deck in any order: Play up to 1 [Kin'emon] with a cost of 6 from your hand.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-027 - Kin'emon

- Printed effect: [Activate: Main] You may place this Character and 1 [Kin'emon] with 1000 power from your trash at the bottom of your deck in any order: Play up to 1 [Kin'emon] with a cost of 6 from your hand.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-028 - Kouzuki Momonosuke

- Printed effect: [Activate: Main] You may rest 2 of your DON!! cards and trash this Character: Look at 5 cards from the top of your deck; reveal up to 2 {The Akazaya Nine} type cards and add them to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-029 - Dracule Mihawk

- Printed effect: [On Play] If you have 2 or more rested Characters, set up to 1 of your rested {ODYSSEY} type Characters with a cost of 5 or less as active.
- Printed trigger: None
- Registered timings: `ON_PLAY`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-030 - Smoker

- Printed effect: [Banish] (When this card deals damage, the target card is trashed without activating its Trigger.) [Activate: Main] Set up to 1 of your DON!! cards as active. Then, you cannot set DON!! cards as active using Character effects during this turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-031 - Sengoku

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP10-032 - Tashigi

- Printed effect: If you have a green Character other than [Tashigi] that would be removed from the field by your opponent's effect, you may rest this Character instead.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Needs Engine Support`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-033 - Nami

- Printed effect: [On Play] If you have 2 or more rested {ODYSSEY} type Characters, up to 1 of your opponent's rested DON!! cards will not become active in your opponent's next Refresh Phase.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Needs Engine Support`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-034 - Franky

- Printed effect: [Once Per Turn] If this Character would be K.O.'d in battle, you may add 1 card from the top of your Life cards to your hand instead.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-035 - Brook

- Printed effect: [On K.O.] Rest up to 1 of your opponent's Leader or Character cards with a cost of 5 or less.
- Printed trigger: None
- Registered timings: `on_ko`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-036 - Perona

- Printed effect: [Your Turn] [Once Per Turn] If a Character is rested by your effect, set up to 1 of your DON!! cards as active.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-037 - Lim

- Printed effect: [Once Per Turn] If this Character would be removed from the field by your opponent's effect, you may rest 1 of your {ODYSSEY} type Characters instead. [End of Your Turn] Set up to 1 of your {ODYSSEY} type Characters as active.
- Printed trigger: None
- Registered timings: `end_of_turn`
- Implementation status: `Needs Engine Support`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-038 - Roronoa Zoro

- Printed effect: [Opponent's Turn] If you have 2 or more rested Characters, this Character gains +2000 power.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-039 - Gum-Gum Dragon Fire Pistol Twister Star

- Printed effect: [Main] If your Leader has the {ODYSSEY} type, look at 5 cards from the top of your deck; reveal up to 2 {ODYSSEY} type Character cards and add them to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: [Trigger] Rest up to 1 of your opponent's Characters with a cost of 5 or less.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-040 - The Weak Do Not Have the Right to Choose How They Die

- Printed effect: [Main]/[Counter] K.O. up to 1 of your opponent's rested Characters with a cost of 7 or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-041 - Radio Knife

- Printed effect: [Main] Rest up to 1 of your opponent's Characters with a cost of 6 or less. Then, K.O. up to 1 of your opponent's rested Characters with a cost of 5 or less.
- Printed trigger: [Trigger] Rest up to 1 of your opponent's Characters with a cost of 4 or less.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-042 - Usopp

- Printed effect: All of your {Dressrosa} type Characters with a cost of 2 or more gain +1 cost. [Opponent's Turn] [Once Per Turn] This effect can be activated when your {Dressrosa} type Character is removed from the field by your opponent's effect or K.O.'d. If you have 5 or less cards in your hand, draw 1 card.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-043 - Moocy

- Printed effect: [On Play] You may rest 1 of your {Dressrosa} type Leader or Stage cards: Up to 1 of your [Monkey.D.Luffy] Characters gains [Banish] during this turn.
- Printed trigger: None
- Registered timings: `blocker`, `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-044 - Cub

- Printed effect: [On Play] You may rest 1 of your {Dressrosa} type Leader or Stage cards: Return up to 1 of your opponent's Characters with a cost of 1 or less to the owner's hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-045 - Cavendish

- Printed effect: [When Attacking] [Once Per Turn] Draw 2 cards and trash 1 card from your hand.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-046 - Kyros

- Printed effect: [On Play] Return up to 1 Character with a cost of 5 or less to the owner's hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-047 - Koala

- Printed effect: [When Attacking] You may return 1 of your {Revolutionary Army} type Characters with a cost of 3 or more to the owner's hand: This Character gains +3000 power during this turn.
- Printed trigger: None
- Registered timings: `WHEN_ATTACKING`, `blocker`, `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-048 - Sai

- Printed effect: [On Play] You may rest 1 of your {Dressrosa} type Leader or Stage cards: Return up to 1 of your opponent's Characters with a cost of 1 or less to the owner's hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-049 - Sabo

- Printed effect: If your Character with a base cost of 7 or less other than [Sabo] would be removed from the field by your opponent's effect, you may return this Character to the owner's hand instead.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Needs Engine Support`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-050 - Hajrudin

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP10-051 - Hack

- Printed effect: [DON!! x1] [When Attacking] Look at 3 cards from the top of your deck; reveal up to 1 {Revolutionary Army} type Character card and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-052 - Bartolomeo

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On Play] Place up to 1 Character with a cost of 1 or less at the bottom of the owner's deck.
- Printed trigger: None
- Registered timings: `on_play`, `blocker`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-053 - Bian

- Printed effect: If you have a {The Tontattas} type Character other than [Bian], this Character gains [Blocker].
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-054 - Blue Gilly

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP10-055 - Marco

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On K.O.] Return up to 1 of your opponent's Characters with a cost of 4 or less to the owner's hand.
- Printed trigger: None
- Registered timings: `on_ko`, `blocker`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-056 - Mansherry

- Printed effect: [On Play] You may rest 1 of your {Dressrosa} type Leader or Stage cards, and return 1 of your {Dressrosa} type Characters with a cost of 4 or more to the owner's hand: Return up to 1 of your opponent's Characters with a cost of 4 or less to the owner's hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-057 - Leo

- Printed effect: [On Play] You may rest your Leader or 1 of your Stage cards: If your Leader is [Usopp], look at 5 cards from the top of your deck; reveal up to 2 {Dressrosa} type cards other than [Leo] and add them to your hand. Then, place the rest at the bottom of your deck in any order, and trash 1 card from your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-058 - Rebecca

- Printed effect: [On Play] If there is a Character with a cost of 8 or more, draw 1 card. Then, reveal up to 2 {Dressrosa} type Character cards with a cost of 7 or less other than [Rebecca] from your hand. Play 1 of the revealed cards and play the other card rested if it has a cost of 4 or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-059 - Fo...llow...Me...and...I...Will...Gui...de...You

- Printed effect: [Main] Look at 5 cards from the top of your deck; reveal up to 1 {Dressrosa} type Character card and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: [Trigger] Activate this card's [Main] effect.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-060 - Barrier-Barrier Pistol

- Printed effect: [Main] Place up to 1 of your opponent's Characters with 6000 power or less at the bottom of the owner's deck.
- Printed trigger: [Trigger] Activate this card's [Main] effect.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-061 - Special Long-Range Attack!! Bagworm

- Printed effect: [Main] Draw 1 card. Then, return up to 1 of your opponent's Characters with a cost of 2 or less to the owner's hand.
- Printed trigger: [Trigger] Return up to 1 Character with a cost of 2 or less to the owner's hand.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-062 - Violet

- Printed effect: [Blocker] [On K.O.] DON!! -1: If your Leader has the {Donquixote Pirates} type, add up to 1 purple Event from your trash to your hand.
- Printed trigger: None
- Registered timings: `on_ko`, `blocker`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-063 - Vinsmoke Sanji

- Printed effect: [On Play] If your Leader's type includes "GERMA", look at 5 cards from the top of your deck; reveal up to 1 card with a type including "GERMA" and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-064 - Clone Soldier

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-065 - Sugar

- Printed effect: [Activate: Main] You may rest 1 of your DON!! cards and this Character: Look at 5 cards from the top of your deck; reveal up to 1 {Donquixote Pirates} type card and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-066 - Giolla

- Printed effect: [On Your Opponent's Attack] [Once Per Turn] You may rest 2 of your DON!! cards: Rest up to 1 of your opponent's Characters with a cost of 4 or less.
- Printed trigger: None
- Registered timings: `on_opponent_attack`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-067 - Senor Pink

- Printed effect: [On Play] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Add up to 1 purple Event with a cost of 5 or less from your trash to your hand. Then, set up to 1 of your DON!! cards as active.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-068 - Diamante

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP10-069 - Fighting Fish

- Printed effect: [DON!! x1] [When Attacking] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): K.O. up to 1 of your opponent's Characters with a cost of 1 or less.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-070 - Trebol

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On Play] All of your Characters with 1000 base power or less cannot be K.O.'d by your opponent's effects until the end of your opponent's next turn.
- Printed trigger: None
- Registered timings: `on_play`, `blocker`
- Implementation status: `Needs Engine Support`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-071 - Donquixote Doflamingo

- Printed effect: [On Play] DON!! -1: Play up to 1 {Donquixote Pirates} type Character card with a cost of 5 or less from your hand. [On Your Opponent's Attack] [Once Per Turn] You may rest 1 of your DON!! cards: Add up to 1 DON!! card from your DON!! deck and set it as active.
- Printed trigger: None
- Registered timings: `on_play`, `on_opponent_attack`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-072 - Donquixote Rosinante

- Printed effect: [On Play] You may trash 1 Event from your hand: Draw 2 cards. [End of Your Turn] If you have 7 or more DON!! cards on your field, set up to 2 of your DON!! cards as active.
- Printed trigger: None
- Registered timings: `on_play`, `end_of_turn`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-073 - Buffalo

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP10-074 - Pica

- Printed effect: [Once Per Turn] If this Character would be K.O.'d by your opponent's effect, you may rest 2 of your active DON!! cards instead.
- Printed trigger: None
- Registered timings: `ON_WOULD_BE_KO`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-075 - Foxy

- Printed effect: [Activate: Main] You may trash this Character: If the number of DON!! cards on your field is equal to or less than the number on your opponent's field, draw 1 card.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-076 - Baby 5

- Printed effect: [On Play] You may trash 1 card from your hand: If your Leader has the {Donquixote Pirates} type, add up to 1 DON!! card from your DON!! deck and set it as active.
- Printed trigger: None
- Registered timings: `ON_PLAY`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-077 - Bellamy

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On Block] You may rest 2 of your DON!! cards: Add up to 1 DON!! card from your DON!! deck and set it as active.
- Printed trigger: None
- Registered timings: `on_block`, `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-078 - I Do Not Forgive Those Who Laugh at My Family!!!

- Printed effect: [Main]/[Counter] Look at 3 cards from the top of your deck; reveal up to 1 {Donquixote Pirates} type card other than [I Do Not Forgive Those Who Laugh at My Family!!!] and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`, `counter`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-079 - God Thread

- Printed effect: [Main] K.O. up to 1 of your opponent's Characters with a cost 5 or less. Then, add up to 1 DON!! card from your DON!! deck and set it as active.
- Printed trigger: [Trigger] Add up to 1 DON!! card from your DON!! deck and set it as active.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-080 - Little Black Bears

- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +4000 power during this battle. Then, if you have 7 or more DON!! cards on your field and 5 or less cards in your hand, draw 1 card.
- Printed trigger: [Trigger] Add up to 1 DON!! card from your DON!! deck and set it as active.
- Registered timings: `counter`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-081 - Usopp

- Printed effect: [On Play] You may rest 1 of your {Dressrosa} type Leader or Stage cards: K.O. up to 1 of your opponent's Characters with a cost of 2 or less. Then, trash 2 cards from the top of your deck.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-082 - Kuzan

- Printed effect: This Character cannot be removed from the field by your opponent's effects. [Activate: Main] You may trash this Character: Draw 1 card. Then, play up to 1 {Blackbeard Pirates} type Character card with a cost of 5 or less other than [Kuzan] from your trash.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-083 - Kouzuki Momonosuke

- Printed effect: [Activate: Main] You may rest this Character and 1 of your {Dressrosa} type Leader or Stage cards: Give up to 1 of your opponent's Characters -2 cost during this turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-084 - Sanjuan.Wolf

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP10-085 - Jesus Burgess

- Printed effect: [DON!! x1] If you have 8 or more cards in your trash, this Character gains [Rush].
- Printed trigger: None
- Registered timings: `CONTINUOUS`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-086 - Shiryu

- Printed effect: [Opponent's Turn] This Character gains +2000 power. [Activate: Main] [Once Per Turn] If your Leader has the {Blackbeard Pirates} type, and this Character was played on this turn, K.O. up to 1 of your opponent's Characters with a base cost of 3 or less.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-087 - Tony Tony.Chopper

- Printed effect: [Activate: Main] You may rest this Character and 1 of your {Dressrosa} type Leader or Stage cards: If your opponent has 5 or more cards in their hand, your opponent trashes 1 card from their hand. Then, trash 2 cards from the top of your deck.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-088 - Nami

- Printed effect: [Activate: Main] You may rest this Character and 1 of your {Dressrosa} type Leader or Stage cards: Draw 1 card. Then, trash 2 cards from the top of your deck.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-089 - Nico Robin

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP10-090 - Franky

- Printed effect: [Blocker] [On K.O.] Play up to 1 {Dressrosa} type Character card with a cost of 3 or less from your trash rested.
- Printed trigger: None
- Registered timings: `on_ko`, `blocker`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-091 - Brook

- Printed effect: [Activate: Main] You may rest this Character and 1 of your {Dressrosa} type Leader or Stage cards: K.O. up to 1 of your opponent's Characters with a cost of 1 or less. Then, trash 2 cards from the top of your deck.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-092 - Perona

- Printed effect: [Activate: Main] [Once Per Turn] You may place 2 {Thriller Bark Pirates} type cards from your trash at the bottom of your deck in any order: Up to 1 of your Characters other than [Perona] gains +2000 power during this turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-093 - Saint Homing

- Printed effect: [Activate: Main] You may trash this Character: Up to 1 of your black Characters gains +3 cost until the end of your opponent's next turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Needs Engine Support`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-094 - Ryuma

- Printed effect: [DON!! x1] This Character gains [Double Attack].
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-095 - Roronoa Zoro

- Printed effect: [On Play] You may rest 1 of your {Dressrosa} type Leader or Stage cards: K.O. up to 1 of your opponent's Characters with a cost of 4 or less. Then, trash 2 cards from the top of your deck.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-096 - There's No Longer Any Need for the Seven Warlords of the Sea!!!

- Printed effect: [Main] K.O. up to 1 of your opponent's {The Seven Warlords of the Sea} type Characters with a cost of 8 or less.
- Printed trigger: [Trigger] K.O. up to 1 of your opponent's {The Seven Warlords of the Sea} type Characters with a cost of 4 or less.
- Registered timings: `MAIN`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-097 - Gum-Gum Rhino Schneider

- Printed effect: [Main] Up to 1 of your {Dressrosa} type Characters gains +2000 power during this turn. Then, if you have 10 or more cards in your trash, that card gains [Banish] during this turn.
- Printed trigger: [Trigger] Draw 2 cards and trash 1 card from your hand.
- Registered timings: `MAIN`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-098 - Liberation

- Printed effect: [Main] If the number of your Characters is at least 2 less than the number of your opponent's Characters, K.O. up to 1 of your opponent's Characters with a base cost of 6 or less and up to 1 of your opponent's Characters with a base cost of 4 or less.
- Printed trigger: [Trigger] Negate the effect of up to 1 of each of your opponent's Leader and Character cards during this turn.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Needs Engine Support`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-099 - Eustass"Captain"Kid

- Printed effect: [End of Your Turn] You may turn 1 card from the top of your Life cards face-up: Set up to 1 of your {Supernovas} type Characters with a cost of 3 to 8 as active. That Character gains [Blocker] until the end of your opponent's next turn.
- Printed trigger: None
- Registered timings: `end_of_turn`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-100 - Inazuma

- Printed effect: [DON!! x1] [When Attacking] Rest up to 1 of your opponent's Characters with a cost equal to or less than the total of your and your opponent's Life cards.
- Printed trigger: [Trigger] If your Leader has the {Revolutionary Army} type and you and your opponent have a total of 5 or less Life cards, play this card.
- Registered timings: `on_attack`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-101 - Urouge

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP10-102 - Emporio.Ivankov

- Printed effect: [Activate: Main] [Once Per Turn] Up to 3 of your {Revolutionary Army} type Characters gain +1000 power during this turn. Then, add 1 card from the top of your Life cards to your hand.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-103 - Capone"Gang"Bege

- Printed effect: [On Play] You may add 1 card from the top or bottom of your Life cards to your hand: Add up to 1 {Supernovas} type Character card from your hand to the top of your Life cards face-up.
- Printed trigger: None
- Registered timings: `ON_PLAY`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-104 - Caribou

- Printed effect: [DON!! x1] If your Leader has the {Supernovas} type and your opponent has 3 or more Life cards, this Character cannot be K.O.'d in battle.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Needs Engine Support`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-105 - Cavendish

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP10-106 - Killer

- Printed effect: [On K.O.] If your Leader has the {Supernovas} type, look at 3 cards from the top of your deck; reveal up to 1 {Supernovas} or {Kid Pirates} type card and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_ko`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-107 - Jewelry Bonney

- Printed effect: [Blocker] [On Play] You may add 1 card from the top or bottom of your Life cards to your hand: Add up to 1 {Supernovas} type Character card with a cost of 5 from your hand to the top of your Life cards face-up.
- Printed trigger: None
- Registered timings: `ON_PLAY`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-108 - Scratchmen Apoo

- Printed effect: If you have a yellow {Supernovas} type Character other than [Scratchmen Apoo], this Character gains [Blocker].
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-109 - Basil Hawkins

- Printed effect: [On K.O.] Trash up to 1 card from the top of your opponent's Life cards.
- Printed trigger: [Trigger] Draw 2 cards and trash 1 card from your hand.
- Registered timings: `on_ko`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-110 - Heat & Wire

- Printed effect: [On Play] Rest up to 1 of your opponent's Characters with a cost equal to or less than the number of your opponent's Life cards.
- Printed trigger: [Trigger] If you have 2 or less Life cards, play this card.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-111 - Monkey.D.Luffy

- Printed effect: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 {Supernovas} type card other than [Monkey.D.Luffy] and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-112 - Eustass"Captain"Kid

- Printed effect: [On Play] You may rest this Character: Trash up to 1 card from the top of your opponent's Life cards. [End of Your Turn] If your opponent has 2 or less Life cards, draw 1 card and trash 1 card from your hand.
- Printed trigger: None
- Registered timings: `ON_PLAY`, `END_OF_TURN`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP10-113 - Roronoa Zoro

- Printed effect: If you have less Life cards than your opponent, this Character gains [Rush].
- Printed trigger: [Trigger] You may trash 1 card from your hand: If your Leader has the {Supernovas} type, play this card.
- Registered timings: `continuous`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-114 - X.Drake

- Printed effect: [Activate: Main] You may rest this Character: If the number of your Life cards is equal to or less than the number of your opponent's Life cards, rest up to 1 of your opponent's Characters with a cost of 4 or less.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-115 - Let's Meet Again in the New World

- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +4000 power during this battle. Then, if you have 0 Life cards, draw 1 card.
- Printed trigger: [Trigger] K.O. up to 1 of your opponent's Characters with a cost equal to or less than the number of your opponent's Life cards.
- Registered timings: `counter`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-116 - Damned Punk

- Printed effect: [Main] Look at up to 1 card from the top of your or your opponent's Life cards and place it at the top or bottom of the Life cards. Then, K.O. up to 1 of your opponent's Characters with a cost of 5 or less.
- Printed trigger: [Trigger] Draw 2 cards and trash 1 card from your hand.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-117 - ROOM

- Printed effect: [Counter] If you have 1 or less Life cards, up to 1 of your Leader or Character cards gains +3000 power during this battle. Then, set up to 1 of your Characters with a cost of 5 or less as active.
- Printed trigger: [Trigger] Draw 1 card.
- Registered timings: `COUNTER`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-118 - Monkey.D.Luffy

- Printed effect: Once per turn, this Character cannot be K.O.'d by your opponent's effects. [When Attacking] You may place 3 cards from your trash at the bottom of your deck in any order: If your opponent has 5 or more cards in their hand, your opponent trashes 1 card from their hand.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Needs Engine Support`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP10-119 - Trafalgar Law

- Printed effect: [On Play] Reveal up to 1 {Supernovas} type Character card from your hand and add it to the top of your Life cards face-down. Then, give up to 1 rested DON!! card to 1 of your {Supernovas} type Leader.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP10 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the OP10 generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
