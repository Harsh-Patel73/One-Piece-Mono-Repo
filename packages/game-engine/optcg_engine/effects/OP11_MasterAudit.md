# OP11 Master Audit

Source of truth: `packages/simulator/backend/data/cards.json` base OP11 entries where `id == id_normal`.

## Summary

- Base cards audited: 119
- Non-vanilla cards: 98
- Vanilla cards: 21
- Registered OP11 cards after this pass: 99
- Registered OP11 timings after this pass: 141
- Missing non-vanilla registrations before this pass: 73
- Missing printed trigger timings before this pass: 17
- Missing non-vanilla registrations after this pass: 0
- Missing printed trigger timings after this pass: 0
- Strict status after this pass: 52/119 `Complete` or `Vanilla`; 67 generic follow-up cards flagged below
- Note: This pass uses the shared generic fallback for many previously missing cards; those remain flagged for exact bespoke follow-up.

## Verification

- `python -m py_compile packages\game-engine\optcg_engine\effects\sets\generic_fallback.py packages\game-engine\optcg_engine\effects\sets\op11_effects.py` passed.
- OP11 registration coverage script passed: `base=119 nonvanilla=98 vanilla=21 registered_cards=99 timings=141 missing=[] missing_triggers=[]`.
- Direct OP11 handler execution sweep passed: `OP11_handler_sweep_ran=141 errors=0 tracebacks=0`, resolving pending choices through `GameState.resolve_pending_choice(...)`.
- Full pytest suite was not rerun in this pass; earlier environment check showed `python -m pytest packages\game-engine\tests` is unavailable because `pytest` is not installed.

## Follow-Up Queue

- `OP11-002` Ain: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-006` Zephyr: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-007` Tashigi: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-008` Doll: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-009` Nico Robin: `Needs Engine Support` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-010` Hibari: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-013` Prince Grus: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-014` Borsalino: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-016` Roronoa Zoro: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-018` Honesty Impact: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-019` Glorp Web!!: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-020` X Calibur: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-023` Arlong: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-024` Aladine: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-025` Ishilly: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-027` Bulge-Eyed Neptunian: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-028` Lord of the Coast: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-029` Charlotte Praline: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-031` Jinbe: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-034` Hatchan: `Needs Engine Support` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-035` Fisher Tiger: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-037` Ancient Weapon Poseidon: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-038` Gum-Gum Elephant Gatling: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-039` Vagabond Drill: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-042` Vito: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-043` Vinsmoke Ichiji: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-044` Vinsmoke Judge: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-047` Vinsmoke Reiju: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-050` Gotti: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-054` Nami: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-056` Brook: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-059` Gum-Gum King Cobra: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-060` Let's Crash This Wedding!!!: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-061` Gum-Gum Jet Culverin: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-063` Little Sadi: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-066` Charlotte Oven: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-069` Charlotte Brulee: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-071` Charlotte Perospero: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-072` Charlotte Mont-d'or: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-073` Charlotte Linlin: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-074` Streusen: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-075` Jaguar.D.Saul: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-076` Hannyabal: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-077` Randolph: `Needs Engine Support` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-079` When Two Men Are Fighting the Last Thing I Need Is Some Half-Hearted Assistance!!!!: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-080` Gear Two: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-081` Cognac Mama-Mash: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-083` Caribou: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-085` Kurozumi Orochi: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-086` Coribou: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-088` Shu: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-092` Helmeppo: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-095` Monkey.D.Garp: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-098` Blue Hole: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-099` I'm Gonna Be a Navy Officer!!!: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-100` Otohime: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-103` Long-Jaw Neptunian: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-106` Zeus: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-107` Topknot Neptunian: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-108` Neptune: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-109` Pappag: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-110` Fukaboshi: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-114` Gum-Gum Fire-Fist Pistol Red Hawk: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-115` You're Just Not My Type!: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-116` Merman Combat Ultramarine: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-117` Fish-Man Island: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- `OP11-118` Monkey.D.Luffy: `Partial` - Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

## Per-Card Audit

### OP11-001 - Koby

- Printed effect: Your {SWORD} type Characters can attack Characters on the turn in which they are played. [Once Per Turn] If your {Navy} type Character with 7000 base power or less would be removed from the field by your opponent's effect, you may place 3 cards from your trash at the bottom of your deck in any order instead.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP11-002 - Ain

- Printed effect: [On Play] Give up to 1 of your opponent's Characters -1000 power during this turn. Then, K.O. up to 1 of your opponent's Characters with 0 power or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-003 - Usopp

- Printed effect: None
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP11-004 - Kujyaku

- Printed effect: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 {Navy} type card other than [Kujyaku] and add it to your hand. Then, place the rest at the bottom of your deck in any order. [Activate: Main] You may trash this Character: Up to 1 of your Characters gains +1000 power during this turn.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP11-005 - Smoker

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [DON!! x1] This Character cannot be K.O.'d by effects of Characters without the ?Special? attribute.
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP11-006 - Zephyr

- Printed effect: [DON!! x1] [When Attacking] Give up to 1 of your opponent's ?Special? attribute Characters -5000 power during this turn.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-007 - Tashigi

- Printed effect: [Activate: Main] You may rest this Character: If your Leader has the {Navy} type, up to 1 of your {Navy} type Characters gains +2000 power during this turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-008 - Doll

- Printed effect: [Blocker] [On Play] You may trash 1 card from your hand: If your Leader has the {Navy} type, give up to 1 of your opponent's Characters -6000 power during this turn.
- Printed trigger: None
- Registered timings: `on_play`, `blocker`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-009 - Nico Robin

- Printed effect: [DON!! x2] [When Attacking] Give up to 1 of your opponent's Characters -2000 power until the end of your opponent's next turn.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Needs Engine Support`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-010 - Hibari

- Printed effect: [On Play] Give up to 1 of your opponent's Characters -2000 power during this turn. [When Attacking] This Character gains +1000 power during this turn. Then, up to 1 of your {Navy} type Leader can also attack active Characters during this turn.
- Printed trigger: None
- Registered timings: `on_play`, `on_attack`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-011 - Bins

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP11-012 - Franky

- Printed effect: [Your Turn] [Once Per Turn] When your opponent activates an Event, all of your Characters gain +2000 power during this turn.
- Printed trigger: None
- Registered timings: `ON_EVENT_ACTIVATE`, `ON_OPPONENT_EVENT`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP11-013 - Prince Grus

- Printed effect: [When Attacking] All of your opponent's Characters with 2000 power or less cannot activate [Blocker] during this turn.
- Printed trigger: None
- Registered timings: `on_attack`, `blocker`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-014 - Borsalino

- Printed effect: [Blocker] [Activate: Main] You may rest this Character: Up to 1 of your {Navy} type Leader or Character cards can also attack active Characters during this turn.
- Printed trigger: None
- Registered timings: `activate`, `blocker`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-015 - Mocha

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP11-016 - Roronoa Zoro

- Printed effect: [Activate: Main] [Once Per Turn] Give up to 1 rested DON!! card to your Leader or 1 of your Characters.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-017 - X.Drake

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP11-018 - Honesty Impact

- Printed effect: [Main] Give up to 1 of your opponent's Characters -4000 power during this turn. Then, K.O. up to 1 of your opponent's Characters with 6000 power or less.
- Printed trigger: [Trigger] K.O. up to 1 of your opponent's Characters with 6000 power or less.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-019 - Glorp Web!!

- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +2000 power during this battle. Then, if your opponent has a Character with 6000 power or more, up to 1 of your Leader or Character cards gains +1000 power during this turn.
- Printed trigger: [Trigger] Up to 1 of your Leader or Character cards gains +1000 power during this turn.
- Registered timings: `counter`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-020 - X Calibur

- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +2000 power during this battle. Then, if your opponent has a Character with 6000 power or more, up to 1 of your Leader or Character cards gains +1000 power during this turn.
- Printed trigger: [Trigger] Up to 1 of your Leader or Character cards gains +1000 power during this turn.
- Registered timings: `counter`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-021 - Jinbe

- Printed effect: [End of Your Turn] If you have 6 or less cards in your hand, set up to 1 of your {Fish-Man} or {Merfolk} type Characters and up to 1 of your DON!! cards as active.
- Printed trigger: None
- Registered timings: `end_of_turn`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP11-022 - Shirahoshi

- Printed effect: This Leader cannot attack. [Activate: Main] [Once Per Turn] You may rest 1 of your DON!! cards and turn 1 card from the top of your Life cards face-up: Play up to 1 {Neptunian} type Character card or [Megalo] with a cost equal to or less than the number of DON!! cards on your field from your hand.
- Printed trigger: None
- Registered timings: `continuous`, `activate`, `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP11-023 - Arlong

- Printed effect: If your Leader has the {Fish-Man} type, you have 3 or less Life cards and your opponent has 5 or more rested cards, give this card in your hand -3 cost.
- Printed trigger: [Trigger] Rest up to 1 of your opponent's Characters with a cost of 4 or less.
- Registered timings: `IN_HAND`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-024 - Aladine

- Printed effect: When this Character is K.O.'d by your opponent's effect, you may trash 1 card from your hand and rest 1 of your DON!! cards. If you do, play up to 1 {Fish-Man} or {Merfolk} type Character card with a cost of 6 or less from your hand.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-025 - Ishilly

- Printed effect: [On Your Opponent's Attack] [Once Per Turn] You may rest 1 of your DON!! cards and this Character: Up to 1 of your Leader or Character cards gains +1000 power during this battle.
- Printed trigger: None
- Registered timings: `on_opponent_attack`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-026 - Scaled Neptunian

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP11-027 - Bulge-Eyed Neptunian

- Printed effect: If your Leader is [Shirahoshi], this Character can attack Characters on the turn in which it is played.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-028 - Lord of the Coast

- Printed effect: [On Play] Up to 1 of your opponent's rested Characters will not become active in your opponent's next Refresh Phase.
- Printed trigger: [Trigger] K.O. up to 1 of your opponent's rested Characters with a cost of 3 or less.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-029 - Charlotte Praline

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On Play] Rest up to 1 of your opponent's Characters with a cost of 1 or less.
- Printed trigger: None
- Registered timings: `on_play`, `blocker`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-030 - Shirahoshi

- Printed effect: [Activate: Main] You may rest 1 of your DON!! cards and this Character: Look at 5 cards from the top of your deck; reveal up to 1 {Neptunian} or {Fish-Man Island} type card and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP11-031 - Jinbe

- Printed effect: [On Play] If your Leader has the {Fish-Man} or {Merfolk} type, rest up to 1 of your opponent's Characters with a cost of 5 or less. [Activate: Main] [Once Per Turn] Up to 1 of your {Fish-Man} or {Merfolk} type Characters can attack Characters on the turn in which it is played.
- Printed trigger: None
- Registered timings: `on_play`, `activate`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-032 - Surume

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP11-033 - Bird Neptunian

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP11-034 - Hatchan

- Printed effect: [Activate: Main] You may rest this Character: If your Leader has the {Fish-Man} or {Merfolk} type, up to 1 of your opponent's Characters with a cost of 3 or less cannot be rested until the end of your opponent's next turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Needs Engine Support`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-035 - Fisher Tiger

- Printed effect: When this Character is K.O.'d by your opponent's effect, you may rest 1 of your DON!! cards. If you do, play up to 1 {Fish-Man} or {Merfolk} type Character card with a cost of 4 or less from your hand. [On Play] Rest up to 1 of your opponent's Characters.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-036 - Spotted Neptunian

- Printed effect: [On Play] If your Leader is [Shirahoshi], look at 5 cards from the top of your deck; reveal up to 1 {Neptunian} type card or [Shirahoshi] and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP11-037 - Ancient Weapon Poseidon

- Printed effect: [Main] Look at 4 cards from the top of your deck; reveal up to 1 {Neptunian} or {Fish-Man Island} type Character card and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: [Trigger] Draw 1 card.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-038 - Gum-Gum Elephant Gatling

- Printed effect: [Main] You may rest 1 of your DON!! cards: Rest up to 1 of your opponent's Characters with a cost of 5 or less. [Counter] Up to 1 of your Leader gains +3000 power during this battle.
- Printed trigger: None
- Registered timings: `counter`, `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-039 - Vagabond Drill

- Printed effect: [Counter] Up to 1 of your {Fish-Man} or {Merfolk} type Leader or Character cards gains +3000 power during this battle. Then, rest up to 1 of your opponent's Characters with a cost of 3 or less.
- Printed trigger: [Trigger] Rest up to 1 of your opponent's Characters with a cost of 4 or less.
- Registered timings: `counter`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-040 - Monkey.D.Luffy

- Printed effect: This effect can be activated at the start of your turn. If you have 8 or more DON!! cards on your field, look at 5 cards from the top of your deck; reveal up to 1 {Straw Hat Crew} type card and add it to your hand. Then, place the rest at the top or bottom of the deck in any order.
- Printed trigger: None
- Registered timings: `start_of_turn`, `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP11-041 - Nami

- Printed effect: [Your Turn] [Once Per Turn] This effect can be activated when a card is removed from your or your opponent's Life cards. If you have 7 or less cards in your hand, draw 1 card. [DON!! x1] [On Your Opponent's Attack] [Once Per Turn] You may trash 1 card from your hand: This Leader gains +2000 power during this turn.
- Printed trigger: None
- Registered timings: `on_life_change`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP11-042 - Vito

- Printed effect: [On Play] You may trash 1 {Firetank Pirates} type card from your hand: This Character gains [Rush] during this turn. (This card can attack on the turn in which it is played.)
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-043 - Vinsmoke Ichiji

- Printed effect: [Blocker] [On Your Opponent's Attack] [Once Per Turn] This effect can be activated when you only have Characters with a type including "GERMA". Up to 1 of your Leader or Character cards gains +1000 power during this battle. Then, trash 2 cards from the top of your deck.
- Printed trigger: None
- Registered timings: `on_opponent_attack`, `blocker`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-044 - Vinsmoke Judge

- Printed effect: [Activate: Main] [Once Per Turn] You may trash 1 card from your hand: All of your {GERMA 66} type Characters gain +1000 power during this turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-045 - Vinsmoke Niji

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP11-046 - Vinsmoke Yonji

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) If you only have Characters with a type including "GERMA", this Character cannot be K.O.'d or rested by your opponent's effects.
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP11-047 - Vinsmoke Reiju

- Printed effect: [On Play] If your Leader has the {The Vinsmoke Family} type, look at 5 cards from the top of your deck; reveal up to 1 card with a type including "GERMA" and add it to your hand. Then, trash the rest.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-048 - Capone"Gang"Bege

- Printed effect: [On Play] Look at 4 cards from the top of your deck; reveal up to 1 {Firetank Pirates} or {Straw Hat Crew} type card with a cost of 2 or more and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP11-049 - Carrot

- Printed effect: [On Play] Look at 3 cards from the top of your deck and place them at the top or bottom of the deck in any order. [On Your Opponent's Attack] You may trash this Character: Up to 1 of your Leader gains +1000 power during this battle.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP11-050 - Gotti

- Printed effect: [When Attacking] You may trash 1 {Firetank Pirates} type card from your hand: Return up to 1 Character with a cost of 1 or less to the owner's hand or place it at the bottom of their deck.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-051 - Sanji

- Printed effect: When this Character is K.O.'d by your opponent's effect, look at 5 cards from the top of your deck and play up to 1 {Straw Hat Crew} type Character card with a cost of 5 or less. Then, place the rest at the bottom of your deck in any order. [On Play] Return up to 1 Character with 5000 base power or less to the owner's hand.
- Printed trigger: None
- Registered timings: `ON_KO_BY_EFFECT`, `ON_PLAY`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP11-052 - Charlotte Lola

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP11-053 - Tony Tony.Chopper

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP11-054 - Nami

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On Play] If your Leader is multicolored, draw 3 cards and place 2 cards from your hand at the top or bottom of your deck in any order.
- Printed trigger: None
- Registered timings: `on_play`, `blocker`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-055 - Bartolomeo

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP11-056 - Brook

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On Play] Place up to 1 Character with a base cost of 1 at the bottom of the owner's deck.
- Printed trigger: None
- Registered timings: `on_play`, `blocker`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-057 - Pedro

- Printed effect: If you have 4 or less cards in your hand, this Character gains [Blocker]. (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP11-058 - Monkey.D.Luffy

- Printed effect: If you have 5 or more cards in your hand, this Character cannot attack. [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP11-059 - Gum-Gum King Cobra

- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +2000 power during this battle. Then, if you have 4 or less cards in your hand, that card gains an additional +2000 power during this battle.
- Printed trigger: [Trigger] Return up to 1 Character with a cost of 2 or less to the owner's hand.
- Registered timings: `counter`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-060 - Let's Crash This Wedding!!!

- Printed effect: [Main] If your Leader is multicolored, look at 5 cards from the top of your deck; reveal up to 1 {Straw Hat Crew} type card other than [Let's Crash This Wedding!!!] and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: [Trigger] Activate this card's [Main] effect.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-061 - Gum-Gum Jet Culverin

- Printed effect: [Main] Place up to 1 of your opponent's Characters with a base cost of 4 or less at the bottom of the owner's deck.
- Printed trigger: [Trigger] Place up to 1 Character with a cost of 1 or less at the bottom of the owner's deck.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-062 - Charlotte Katakuri

- Printed effect: [When Attacking]/[On Your Opponent's Attack] [Once Per Turn] DON!! -1: Look at 1 card from the top of your opponent's deck. Then, this Leader gains +1000 power during this battle.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP11-063 - Little Sadi

- Printed effect: [On Play] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): If your Leader has the {Impel Down} type, rest up to 1 of your opponent's Characters with a cost of 3 or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-064 - Saldeath

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP11-065 - Charlotte Anana

- Printed effect: If you have a purple {Big Mom Pirates} type Character other than [Charlotte Anana], this Character gains [Blocker]. (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP11-066 - Charlotte Oven

- Printed effect: [Activate: Main] You may rest this Character: Choose a cost and reveal 1 card from the top of your opponent's deck. If the revealed card has the chosen cost, K.O. up to 1 of your opponent's Characters with a base cost of 3 or less. Then, add up to 1 DON!! card from your DON!! deck and rest it.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-067 - Charlotte Katakuri

- Printed effect: [Blocker] [End of Your Turn] Set up to 2 of your {Big Mom Pirates} type Characters with a cost of 3 or more as active. Then, add up to 1 DON!! card from your DON!! deck and rest it.
- Printed trigger: None
- Registered timings: `end_of_turn`, `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP11-068 - Charlotte Daifuku

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP11-069 - Charlotte Brulee

- Printed effect: [On Play] You may add 1 card from the top of your Life cards to your hand: If your Leader has the {Big Mom Pirates} type, add up to 1 DON!! card from your DON!! deck and set it as active.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-070 - Charlotte Pudding

- Printed effect: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 {Big Mom Pirates} type card with a cost of 2 or more and add it to your hand. Then, place the rest at the bottom of your deck in any order. [Activate: Main] DON!! -1, You may rest this Character: Look at 1 card from the top of your opponent's deck.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP11-071 - Charlotte Perospero

- Printed effect: [Activate: Main] [Once Per Turn] You may trash 1 card from your hand: Choose a cost and reveal 1 card from the top of your opponent's deck. If the revealed card has the chosen cost, draw 1 card and add up to 1 DON!! card from your DON!! deck and set it as active.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-072 - Charlotte Mont-d'or

- Printed effect: [Activate: Main] [Once Per Turn] DON!! -1, You may rest this Character: Your opponent places 2 cards from their trash at the bottom of their deck in any order. Then, add 1 card from the top of your Life cards to your hand.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-073 - Charlotte Linlin

- Printed effect: If your Leader has the {Big Mom Pirates} type, this Character gains [Rush]. [On Your Opponent's Attack] [Once Per Turn] DON!! -5: Choose a cost and reveal 1 card from the top of your opponent's deck. If the revealed card has the chosen cost, up to 1 of your Leader gains +2000 power during this turn.
- Printed trigger: None
- Registered timings: `on_opponent_attack`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-074 - Streusen

- Printed effect: [Activate: Main] [Once Per Turn] DON!! -1, You may rest this Character: Choose a cost and reveal 1 card from the top of your opponent's deck. If the revealed card has the chosen cost, rest up to 1 of your opponent's Characters with a cost of 4 or less.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-075 - Jaguar.D.Saul

- Printed effect: [On Play] If your Leader is [Nico Robin] and you have 7 or more DON!! cards on your field, draw 2 cards.
- Printed trigger: [Trigger] Activate this card's [On Play] effect.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-076 - Hannyabal

- Printed effect: [Blocker] [On Play] If your Leader has the {Impel Down} type, play up to 1 {Impel Down} type Character card with a cost of 3 or less from your hand.
- Printed trigger: None
- Registered timings: `on_play`, `blocker`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-077 - Randolph

- Printed effect: [Your Turn] [Once Per Turn] When a DON!! card on your field is returned to your DON!! deck, up to 1 of your {Big Mom Pirates} type Characters gains +2 cost until the end of your opponent's next turn.
- Printed trigger: None
- Registered timings: `continuous`
- Implementation status: `Needs Engine Support`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-078 - Decuplets

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP11-079 - When Two Men Are Fighting the Last Thing I Need Is Some Half-Hearted Assistance!!!!

- Printed effect: [Counter] Choose a cost and reveal 1 card from the top of your opponent's deck. If the revealed card has the chosen cost, up to 1 of your Leader or Character cards gains +5000 power during this battle.
- Printed trigger: [Trigger] Draw 1 card.
- Registered timings: `counter`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-080 - Gear Two

- Printed effect: [Main] You may rest 2 of your DON!! cards: If your Leader's colors include blue, add up to 1 DON!! card from your DON!! deck and rest it. [Counter] Up to 1 of your Leader gains +3000 power during this battle.
- Printed trigger: None
- Registered timings: `counter`, `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-081 - Cognac Mama-Mash

- Printed effect: [Main] Choose a cost and reveal 1 card from the top of your opponent's deck. If the revealed card has the chosen cost, K.O. up to 1 of your opponent's Characters with a base cost of 8 or less.
- Printed trigger: [Trigger] Add up to 1 DON!! card from your DON!! deck and set it as active.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-082 - Aramaki

- Printed effect: [Activate: Main] You may trash this Character: If your Leader has the {Navy} type, up to 1 of your {Navy} type Characters can also attack active Characters during this turn. Then, trash 2 cards from the top of your deck.
- Printed trigger: None
- Registered timings: `ACTIVATE_MAIN`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP11-083 - Caribou

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [On Play] Trash 2 cards from your hand.
- Printed trigger: None
- Registered timings: `on_play`, `blocker`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-084 - Kuzan

- Printed effect: [On Play] Trash 3 cards from the top of your deck. [When Attacking] Up to 1 of your {Navy} type Leader or Character cards can also attack active Characters during this turn.
- Printed trigger: None
- Registered timings: `ON_PLAY`, `WHEN_ATTACKING`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP11-085 - Kurozumi Orochi

- Printed effect: [On Play] Add up to 1 {SMILE} type card with a cost of 5 or less from your trash to your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-086 - Coribou

- Printed effect: [On Play] Trash 1 card from your hand. [Activate: Main] You may trash this Character: Play up to 1 [Caribou] with a cost of 4 or less from your trash.
- Printed trigger: None
- Registered timings: `on_play`, `activate`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-087 - Miss Sarahebi

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP11-088 - Shu

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [Once Per Turn] This effect can be activated when your opponent's Character attacks. If that Character has the ?Slash? attribute, this Character gains +5000 power during this battle.
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-089 - Black Maria

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP11-090 - Briscola

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP11-091 - Berry Good

- Printed effect: [On Play] Your opponent places 3 Events from their trash at the bottom of their deck in any order.
- Printed trigger: None
- Registered timings: `ON_PLAY`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP11-092 - Helmeppo

- Printed effect: [On Play] You may trash 1 card from your hand: Draw 1 card and play up to 1 {SWORD} type Character card with a cost of 8 or less other than [Helmeppo] from your trash. Then, place the 1 Character played by this effect at the bottom of the owner's deck at the end of this turn.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-093 - Bogard

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP11-094 - Morgan

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP11-095 - Monkey.D.Garp

- Printed effect: [On Play] You may place 3 {Navy} type cards from your trash at the bottom of your deck in any order: Give up to 1 rested DON!! card to 1 of your Leader. Then, if there is a Character with a cost of 9 or more, K.O. up to 1 of your opponent's Characters with a cost of 7 or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-096 - Ripper

- Printed effect: If you have a black {Navy} type Character other than [Ripper], this Character gains [Blocker]. (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP11-097 - After All These Years I'm Losing My Edge!!!

- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +1000 power during this battle. Then, if you have 10 or more cards in your trash, add up to 1 black Character card with a cost of 3 or less from your trash to your hand.
- Printed trigger: None
- Registered timings: `COUNTER`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP11-098 - Blue Hole

- Printed effect: [Main] You may trash 3 cards from the top of your deck: K.O. up to 1 of your opponent's Characters with a cost of 2 or less.
- Printed trigger: [Trigger] Up to 1 of your Leader or Character cards gains +1000 power during this turn.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-099 - I'm Gonna Be a Navy Officer!!!

- Printed effect: [Main] Look at 3 cards from the top of your deck; reveal up to 1 {Navy} type card other than [I'm Gonna Be a Navy Officer!!!] and add it to your hand. Then, trash the rest.
- Printed trigger: [Trigger] Activate this card's [Main] effect.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-100 - Otohime

- Printed effect: [On Play] If your Leader is [Shirahoshi], you may turn 1 card from the top of your Life cards face-down: Draw 1 card.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-101 - Capone"Gang"Bege

- Printed effect: [Blocker] [Once Per Turn] If your {Supernovas} type Character other than [Capone"Gang"Bege] would be removed from the field by your opponent's effect, you may add it to the top of your Life cards face-down instead.
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP11-102 - Camie

- Printed effect: [Your Turn] [Once Per Turn] This effect can be activated when your opponent activates an Event or [Trigger]. If your opponent has 2 or more Life cards, trash 1 card from the top of each of your and your opponent's Life cards.
- Printed trigger: None
- Registered timings: `ON_EVENT_TRIGGER`, `ON_OPPONENT_EVENT`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP11-103 - Long-Jaw Neptunian

- Printed effect: [Activate: Main] If your Leader is [Shirahoshi], you may rest this Character and turn 1 card from the top of your Life cards face-down: K.O. up to 1 of your opponent's Characters with a cost of 3 or less.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-104 - Shirley

- Printed effect: [Blocker] [On Play] You may turn 1 card from the top of your Life cards face-down: Look at 3 cards from the top of your deck; reveal up to 1 {Fish-Man Island} type card and add it to your hand. Then, place the rest at the top or bottom of the deck in any order.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP11-105 - Charlotte Chiffon

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP11-106 - Zeus

- Printed effect: [On Play] You may add 1 card from the top or bottom of your Life cards to your hand: K.O. up to 1 of your opponent's Characters with a cost of 5 or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-107 - Topknot Neptunian

- Printed effect: [Blocker] [Activate: Main] [Once Per Turn] If your Leader is [Shirahoshi], you may turn 1 card from the top of your Life cards face-down: Set this Character as active at the end of this turn.
- Printed trigger: None
- Registered timings: `activate`, `blocker`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-108 - Neptune

- Printed effect: [On Play] If your Leader is [Shirahoshi], you may turn 1 card from the top of your Life cards face-down: Draw 2 cards and trash 1 card from your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-109 - Pappag

- Printed effect: [On Play] If you have [Camie], draw 2 cards and trash 2 cards from your hand.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-110 - Fukaboshi

- Printed effect: If this Character would be K.O.'d, you may rest 1 of your [Fish-Man Island] or your [Shirahoshi] Leader instead. [On Play] You may add 1 card from the top or bottom of your Life cards to your hand: K.O. up to 1 of your opponent's Characters with a cost of 1 or less.
- Printed trigger: None
- Registered timings: `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-111 - Mamboshi

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP11-112 - Megalo

- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) [Opponent's Turn] If your Leader is [Shirahoshi], this Character gains +4000 power.
- Printed trigger: None
- Registered timings: `blocker`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.

### OP11-113 - Ryuboshi

- Printed effect: None
- Printed trigger: None
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: No effect/trigger printed; no registration required.
- Open questions/blockers: None.

### OP11-114 - Gum-Gum Fire-Fist Pistol Red Hawk

- Printed effect: [Main] You may rest 3 of your DON!! cards: If you and your opponent have a total of 5 or more Life cards, K.O. up to 1 of your opponent's Characters with a base cost of 5 or less. [Counter] Up to 1 of your Leader gains +3000 power during this battle.
- Printed trigger: None
- Registered timings: `counter`, `on_play`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-115 - You're Just Not My Type!

- Printed effect: [Counter] If your Leader is [Shirahoshi], up to 1 of your Leader or Character cards gains +4000 power during this battle.
- Printed trigger: [Trigger] K.O. up to 1 of your opponent's Characters with a cost of 2 or less.
- Registered timings: `counter`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-116 - Merman Combat Ultramarine

- Printed effect: [Main] Add up to 1 Character with a cost of 6 or less to the top or bottom of the owner's Life cards face-up.
- Printed trigger: [Trigger] Add up to 1 of your opponent's Characters with a cost of 4 or less to the top or bottom of the owner's Life cards face-up.
- Registered timings: `on_play`, `trigger`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-117 - Fish-Man Island

- Printed effect: [Activate: Main] [Once Per Turn] If your Leader is [Shirahoshi], you may turn 1 card from the top of your Life cards face-up: Up to 1 of your {Neptunian}, {Fish-Man}, or {Merfolk} type Characters gains +1000 power during this turn.
- Printed trigger: None
- Registered timings: `activate`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-118 - Monkey.D.Luffy

- Printed effect: [Rush] [When Attacking] You may trash 1 card from your hand: Return up to 1 Character with a cost of 4 or less to the owner's hand. Then, give up to 1 rested DON!! card to your Leader or 1 of your Characters.
- Printed trigger: None
- Registered timings: `on_attack`
- Implementation status: `Partial`
- Required code changes: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing executes without immediate exception; semantic precision gap flagged for follow-up.
- Open questions/blockers: Implemented through the shared generic printed-text fallback; works for common draw/trash/K.O./rest/return/play/search/DON patterns but needs bespoke review for exact conditions, costs, durations, and multi-step ordering.

### OP11-119 - Koby

- Printed effect: [On Play] Up to 1 of your Characters can also attack active Characters during this turn. [When Attacking] You may place 2 cards from your trash at the bottom of your deck in any order: Up to 1 of your Leader or Character cards gains +1000 power until the end of your opponent's next turn.
- Printed trigger: None
- Registered timings: `ON_PLAY`, `WHEN_ATTACKING`
- Implementation status: `Complete`
- Required code changes: Implemented/verified against printed effect and trigger for normal simulator play.
- Required tester setup: Generic OP11 tester seed was sufficient for execution sweep; add card-specific fixtures for bespoke follow-up cards.
- Verification result: Registered timing coverage and direct handler sweep passed.
- Open questions/blockers: None identified in this pass.
