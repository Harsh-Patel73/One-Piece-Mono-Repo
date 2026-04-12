# OP05 Master Audit

Generated from `english_cards.json`, `op05_effects.py`, and the current OP05 rows in `CARD_STATUS.md`.

## Queue Summary

- OP05 base cards: 119
- Currently verified: 32
- Already marked Needs Fix: 8
- Untracked base cards: 79
- Implementation queue: 87

## First Lane

- `OP05-001` Sabo
- `OP05-003` Inazuma
- `OP05-004` Emporio.Ivankov
- `OP05-005` Karasu
- `OP05-007` Sabo
- `OP05-023` Vergo
- `OP05-026` Sarquiss
- `OP05-030` Donquixote Rosinante

## Master Worklist

### OP05-001 Sabo
- Printed: [DON!! x1] [Opponent's Turn] [Once Per Turn] If your Character with 5000 power or more would be K.O.'d, you may give that Character −1000 power during this turn instead of that ...
- Current state: existing handler and mismatch. Registered timings: `on_ko_prevention`.
- Missing behavior: This card is a little tricky, when there is a DON!! on this leader, if a character that is on this player's field would be KOd, whether by effects OR battle on the OPPONENTS TURN only, then ONCE PER TURN, we can just give that character -1000 power instead. The prompt to use leader effect should show up when a character loses a battle.
- Required engine/helper support: DON cost / DON state helper; KO replacement / prevention hook
- Required test seeding: Default board state is likely enough.
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-002 Belo Betty
- Printed: [Activate: Main] [Once Per Turn] You may trash 1 {Revolutionary Army} type card from your hand: Up to 3 of your {Revolutionary Army} type Characters or Characters with a [Trigge...
- Current state: existing handler, untracked. Registered timings: `activate`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: None expected beyond the existing effect helpers.
- Required test seeding: Revolutionary Army leader / hand / field; trash count / trash contents
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-003 Inazuma
- Printed: If you have a Character with 7000 power or more other than this Character, this Character gains [Rush]. / (This card can attack on the turn in which it is played.)
- Current state: existing handler and mismatch. Registered timings: `continuous`.
- Missing behavior: When another character on the player's field has a power of 7000 or more, OTHER than this character. Then this character would gain rush.
- Required engine/helper support: None expected beyond the existing effect helpers.
- Required test seeding: 7000+ power setup
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-004 Emporio.Ivankov
- Printed: [Activate: Main] [Once Per Turn] If this Character has 7000 power or more, play up to 1 {Revolutionary Army} type Character card with 5000 power or less other than [Emporio.Ivan...
- Current state: existing handler and mismatch. Registered timings: `activate`.
- Missing behavior: When this character has a power of 7000 or more (this includes when it is given DON!!), I should be prompted to select a Revolutionary Army type character with 5000 power or less in my hand to play out.
- Required engine/helper support: None expected beyond the existing effect helpers.
- Required test seeding: Revolutionary Army leader / hand / field; 7000+ power setup; exact cost / power breakpoints
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-005 Karasu
- Printed: [On Play] If your Leader has the {Revolutionary Army} type, give up to 1 of your opponent's Leader or Character cards −1000 power during this turn. / [When Attacking] If this Ch...
- Current state: existing handler and mismatch. Registered timings: `on_play, on_attack`.
- Missing behavior: This card should be able to target leaders as well to reduce their power.
- Required engine/helper support: Leader-or-Character target prompt
- Required test seeding: Revolutionary Army leader / hand / field; 7000+ power setup
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-007 Sabo
- Printed: [On Play] K.O. up to 2 of your opponent's Characters with a total power of 4000 or less.
- Current state: existing handler and mismatch. Registered timings: `on_play`.
- Missing behavior: This card currently KOs automatically, there should be a prompt to select 2 cards that combined have a power of 4000 or less. i.e, 0 power and 4000 power, 1000 power and 3000 power, etc.
- Required engine/helper support: multi-target selection helper; sum-constrained KO selection
- Required test seeding: Default board state is likely enough.
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-009 Toh-Toh
- Printed: [On Play] Draw 1 card if your Leader has 0 power or less.
- Current state: existing handler, untracked. Registered timings: `on_play`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: None expected beyond the existing effect helpers.
- Required test seeding: exact cost / power breakpoints
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-015 Belo Betty
- Printed: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 {Revolutionary Army} type card other than [Belo Betty] and add it to your hand. Then, place the rest at the b...
- Current state: existing handler, untracked. Registered timings: `on_play`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: search / reorder helper
- Required test seeding: Revolutionary Army leader / hand / field
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-016 Morley
- Printed: [When Attacking] If this Character has 7000 power or more, your opponent cannot activate [Blocker] during this battle. Trigger: [Trigger] You may trash 1 card from your hand: If...
- Current state: existing handler, untracked. Registered timings: `on_attack, trigger`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: None expected beyond the existing effect helpers.
- Required test seeding: multicolor leader; 7000+ power setup; trash count / trash contents
- Acceptance: Printed main / trigger text resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-017 Lindbergh
- Printed: [When Attacking] If this Character has 7000 power or more, K.O. up to 1 of your opponent's Characters with 3000 power or less. Trigger: [Trigger] You may trash 1 card from your ...
- Current state: existing handler, untracked. Registered timings: `on_attack, trigger`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: None expected beyond the existing effect helpers.
- Required test seeding: multicolor leader; 7000+ power setup; trash count / trash contents; exact cost / power breakpoints
- Acceptance: Printed main / trigger text resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-019 Fire Fist
- Printed: [Main] Give up to 1 of your opponent's Characters −4000 power during this turn. Then, if you have 2 or less Life cards, K.O. up to 1 of your opponent's Characters with 0 power o...
- Current state: partial handler. Registered timings: `MAIN`.
- Missing behavior: Add the missing timing hook(s): trigger. Then audit the full printed branches against the current code.
- Required engine/helper support: Life-area helper
- Required test seeding: life count / life pile setup; exact cost / power breakpoints
- Acceptance: Printed main / trigger text resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-020 Four Thousand-Brick Fist
- Printed: [Main] Up to 1 of your Leader or Character cards gains +2000 power during this turn. Then, K.O. up to 1 of your opponent's Characters with 2000 power or less. Trigger: [Trigger]...
- Current state: existing handler, untracked. Registered timings: `main, trigger`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: Leader-or-Character target prompt
- Required test seeding: exact cost / power breakpoints
- Acceptance: Printed main / trigger text resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-022 Donquixote Rosinante
- Printed: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) / [End of Your Turn] If you have 6 or less cards in your hand...
- Current state: existing handler, untracked. Registered timings: `blocker, end_of_turn`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: None expected beyond the existing effect helpers.
- Required test seeding: Default board state is likely enough.
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-023 Vergo
- Printed: [DON!! x1] [When Attacking] K.O. up to 1 of your opponent's rested Characters with a cost of 3 or less.
- Current state: existing handler and mismatch. Registered timings: `on_attack`.
- Missing behavior: I select a rested character with cost 3 or less but it does not actually KO it.
- Required engine/helper support: DON cost / DON state helper
- Required test seeding: rested targets; exact cost / power breakpoints
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-026 Sarquiss
- Printed: [DON!! x1] [When Attacking] [Once Per Turn] You may rest 1 of your Characters with a cost of 3 or more: Set this Character as active.
- Current state: existing handler and mismatch. Registered timings: `on_attack`.
- Missing behavior: When this card uses it's effect to become active again it should once again be able to attack.
- Required engine/helper support: DON cost / DON state helper
- Required test seeding: exact cost / power breakpoints
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-029 Donquixote Doflamingo
- Printed: [On Your Opponent's Attack] [Once Per Turn] ➀ (You may rest the specified number of DON!! cards in your cost area.): Rest up to 1 of your opponent's Characters with a cost of 6 ...
- Current state: existing handler, untracked. Registered timings: `on_opponent_attack`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: DON cost / DON state helper
- Required test seeding: specific DON threshold; exact cost / power breakpoints
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-030 Donquixote Rosinante
- Printed: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) / [Opponent's Turn] If your rested Character would be K.O.'d,...
- Current state: existing handler and mismatch. Registered timings: `blocker, on_ko_prevention`.
- Missing behavior: When a rested character is KOd, there should be a prompt to trash this card instead and protect that card that was KOd.
- Required engine/helper support: KO replacement / prevention hook
- Required test seeding: trash count / trash contents; rested targets
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-032 Pica
- Printed: [End of Your Turn] ①: Set this Character as active. / [Once Per Turn] If this Character would be K.O.'d, you may rest up to 1 of your Characters with a cost of 3 or more other t...
- Current state: existing handler, untracked. Registered timings: `end_of_turn, on_ko_prevention`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: KO replacement / prevention hook
- Required test seeding: exact cost / power breakpoints
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-033 Baby 5
- Printed: [Activate: Main] ➀ (You may rest the specified number of DON!! cards in your cost area.) You may rest this Character: Play up to 1 {Donquixote Pirates} type Character card with ...
- Current state: existing handler, untracked. Registered timings: `activate`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: DON cost / DON state helper
- Required test seeding: Donquixote Pirates field / hand; specific DON threshold; exact cost / power breakpoints
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-034 Baby 5
- Printed: [Activate: Main] ➀ (You may rest the specified number of DON!! cards in your cost area.) You may rest this Character: Look at 5 cards from the top of your deck; reveal up to 1 {...
- Current state: existing handler, untracked. Registered timings: `activate`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: DON cost / DON state helper; search / reorder helper
- Required test seeding: Donquixote Pirates field / hand; specific DON threshold
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-037 Because the Side of Justice Will Be Whichever Side Wins!!
- Printed: [Counter] You may trash 1 card from your hand: Up to 1 of your Leader or Character cards gains +3000 power during this battle. Trigger: [Trigger] Rest up to 1 of your opponent's...
- Current state: existing handler, untracked. Registered timings: `counter, trigger`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: Leader-or-Character target prompt
- Required test seeding: trash count / trash contents; exact cost / power breakpoints
- Acceptance: Printed main / trigger text resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-038 Charlestone
- Printed: [Counter] Up to 1 of your Leader or Character cards gains +4000 power during this battle. Then, you may trash 1 card from your hand. If you do, set up to 3 of your DON!! cards a...
- Current state: existing handler, untracked. Registered timings: `counter, trigger`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: Leader-or-Character target prompt; multi-target selection helper; DON cost / DON state helper
- Required test seeding: trash count / trash contents; exact cost / power breakpoints
- Acceptance: Printed main / trigger text resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-039 Stick-Stickem Meteora
- Printed: [Counter] Up to 1 of your Leader or Character cards gains +4000 power during this battle. Then, K.O. up to 1 of your opponent's rested Characters with a cost of 3 or less. Trigg...
- Current state: existing handler, untracked. Registered timings: `counter, trigger`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: Leader-or-Character target prompt
- Required test seeding: rested targets; exact cost / power breakpoints
- Acceptance: Printed main / trigger text resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-040 Birdcage
- Printed: If your Leader is [Donquixote Doflamingo], all Characters with a cost of 5 or less do not become active in your and your opponent's Refresh Phases. / [End of Your Turn] If you h...
- Current state: existing handler, untracked. Registered timings: `END_OF_TURN`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: DON cost / DON state helper
- Required test seeding: specific DON threshold; trash count / trash contents; rested targets; exact cost / power breakpoints
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-041 Sakazuki
- Printed: [Activate: Main] [Once Per Turn] You may trash 1 card from your hand: Draw 1 card. / [When Attacking] Give up to 1 of your opponent's Characters −1 cost during this turn.
- Current state: existing handler, untracked. Registered timings: `activate, on_attack`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: None expected beyond the existing effect helpers.
- Required test seeding: trash count / trash contents
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-042 Issho
- Printed: [On Play] Up to 1 of your opponent's Characters with a cost of 7 or less cannot attack until the start of your next turn.
- Current state: existing handler, untracked. Registered timings: `on_play`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: None expected beyond the existing effect helpers.
- Required test seeding: exact cost / power breakpoints
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-043 Ulti
- Printed: [On Play] If your Leader is multicolored, look at 3 cards from the top of your deck and add up to 1 card to your hand. Then, place the rest at the top or bottom of the deck in a...
- Current state: existing handler, untracked. Registered timings: `on_play`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: search / reorder helper
- Required test seeding: multicolor leader
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-045 Stainless
- Printed: [Activate: Main] You may trash 1 card from your hand and rest this Character: Place up to 1 Character with a cost of 2 or less at the bottom of the owner's deck.
- Current state: existing handler, untracked. Registered timings: `activate`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: None expected beyond the existing effect helpers.
- Required test seeding: trash count / trash contents; exact cost / power breakpoints
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-046 Dalmatian
- Printed: [On K.O.] Draw 1 card and place 1 card from your hand at the bottom of your deck.
- Current state: existing handler, untracked. Registered timings: `on_ko`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: None expected beyond the existing effect helpers.
- Required test seeding: Default board state is likely enough.
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-053 Mozambia
- Printed: [Your Turn] [Once Per Turn] When you draw a card outside of your Draw Phase, this Character gains +2000 power during this turn.
- Current state: partial handler. Registered timings: `on_draw`.
- Missing behavior: Add the missing timing hook(s): continuous. Then audit the full printed branches against the current code.
- Required engine/helper support: None expected beyond the existing effect helpers.
- Required test seeding: Default board state is likely enough.
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-054 Monkey.D.Garp
- Printed: [On Play] Draw 2 cards and place 2 cards from your hand at the bottom of your deck in any order.
- Current state: existing handler, untracked. Registered timings: `on_play`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: None expected beyond the existing effect helpers.
- Required test seeding: Default board state is likely enough.
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-055 X.Drake
- Printed: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) / [On Play] Look at 5 cards from the top of your deck and pla...
- Current state: existing handler, untracked. Registered timings: `blocker, on_play`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: search / reorder helper
- Required test seeding: Default board state is likely enough.
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-056 X.Barrels
- Printed: [On Play] You may place 1 of your Characters other than this Character at the bottom of your deck: Draw 1 card.
- Current state: existing handler, untracked. Registered timings: `on_play`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: None expected beyond the existing effect helpers.
- Required test seeding: Default board state is likely enough.
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-057 Hound Blaze
- Printed: [Main] Up to 1 of your Leader or Character cards gains +3000 power during this turn. Then, place up to 1 Character with a cost of 2 or less at the bottom of the owner's deck. Tr...
- Current state: existing handler, untracked. Registered timings: `main, trigger`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: Leader-or-Character target prompt
- Required test seeding: exact cost / power breakpoints
- Acceptance: Printed main / trigger text resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-058 It's a Waste of Human Life!!
- Printed: [Main] Place all Characters with a cost of 3 or less at the bottom of the owner's deck. Then, you and your opponent trash cards from your hands until you each have 5 cards in yo...
- Current state: existing handler, untracked. Registered timings: `main, trigger`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: None expected beyond the existing effect helpers.
- Required test seeding: trash count / trash contents; exact cost / power breakpoints
- Acceptance: Printed main / trigger text resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-059 Let Us Begin the World of Violence!!!
- Printed: [Main] If your Leader is multicolored, draw 1 card. Then, return up to 1 Character with a cost of 5 or less to the owner's hand. Trigger: [Trigger] If your Leader is multicolore...
- Current state: existing handler, untracked. Registered timings: `main, trigger`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: None expected beyond the existing effect helpers.
- Required test seeding: multicolor leader; exact cost / power breakpoints
- Acceptance: Printed main / trigger text resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-060 Monkey.D.Luffy
- Printed: [Activate: Main] [Once Per Turn] You may add 1 card from the top of your Life cards to your hand: If you have 0 or 3 or more DON!! cards on your field, add up to 1 DON!! card fr...
- Current state: existing handler, untracked. Registered timings: `activate`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: DON cost / DON state helper; Life-area helper
- Required test seeding: life count / life pile setup
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-064 Killer
- Printed: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 {Kid Pirates} type card other than [Killer] and add it to your hand. Then, place the rest at the bottom of yo...
- Current state: existing handler, untracked. Registered timings: `on_play`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: search / reorder helper
- Required test seeding: Kid Pirates leader / field
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-066 Jinbe
- Printed: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) / [Opponent's Turn] If you have 10 DON!! cards on your field,...
- Current state: existing handler, untracked. Registered timings: `blocker, continuous`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: DON cost / DON state helper
- Required test seeding: specific DON threshold
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-067 Zoro-Juurou
- Printed: [When Attacking] If you have 3 or less Life cards, add up to 1 DON!! card from your DON!! deck and set it as active.
- Current state: existing handler, untracked. Registered timings: `on_attack`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: DON cost / DON state helper; Life-area helper
- Required test seeding: life count / life pile setup
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-068 Chopa-Emon
- Printed: [On Play] If you have 8 or more DON!! cards on your field, set up to 1 of your purple {Straw Hat Crew} type Characters with 6000 power or less as active.
- Current state: existing handler, untracked. Registered timings: `on_play`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: DON cost / DON state helper
- Required test seeding: specific DON threshold; exact cost / power breakpoints
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-069 Trafalgar Law
- Printed: [When Attacking] If your opponent has more DON!! cards on their field than you, look at 5 cards from the top of your deck; reveal up to 1 {Heart Pirates} type card and add it to...
- Current state: existing handler, untracked. Registered timings: `on_attack`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: DON cost / DON state helper; search / reorder helper
- Required test seeding: Default board state is likely enough.
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-071 Bepo
- Printed: [When Attacking] If your opponent has more DON!! cards on their field than you, give up to 1 of your opponent's Characters −2000 power during this turn.
- Current state: existing handler, untracked. Registered timings: `on_attack`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: DON cost / DON state helper
- Required test seeding: Default board state is likely enough.
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-072 Hone-Kichi
- Printed: [On Play] If you have 8 or more DON!! cards on your field, give up to 2 of your opponent's Characters −2000 power during this turn.
- Current state: existing handler, untracked. Registered timings: `on_play`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: multi-target selection helper; DON cost / DON state helper
- Required test seeding: specific DON threshold
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-073 Miss Doublefinger(Zala)
- Printed: [On Play] You may trash 1 card from your hand: Add up to 1 DON!! card from your DON!! deck and rest it. Trigger: [Trigger] DON!! −1 (You may return the specified number of DON!!...
- Current state: existing handler, untracked. Registered timings: `on_play, trigger`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: DON cost / DON state helper
- Required test seeding: specific DON threshold; trash count / trash contents
- Acceptance: Printed main / trigger text resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-074 Eustass"Captain"Kid
- Printed: [Blocker] / [Your Turn] [Once Per Turn] When a DON!! card on your field is returned to your DON!! deck, add up to 1 DON!! card from your DON!! deck and set it as active.
- Current state: partial handler. Registered timings: `blocker, on_don_return`.
- Missing behavior: Add the missing timing hook(s): continuous. Then audit the full printed branches against the current code.
- Required engine/helper support: DON cost / DON state helper
- Required test seeding: Default board state is likely enough.
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-075 Mr.1(Daz.Bonez)
- Printed: [On Your Opponent's Attack] [Once Per Turn] DON!! −1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Play up to 1 {Baroque Works} type ...
- Current state: existing handler, untracked. Registered timings: `on_opponent_attack`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: DON cost / DON state helper
- Required test seeding: specific DON threshold; exact cost / power breakpoints
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-077 Gamma Knife
- Printed: [Main] DON!! −1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Give up to 1 of your opponent's Characters −5000 power during this turn...
- Current state: existing handler, untracked. Registered timings: `main, trigger`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: DON cost / DON state helper
- Required test seeding: specific DON threshold
- Acceptance: Printed main / trigger text resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-078 Punk Rotten
- Printed: [Main] DON!! −1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Up to 1 of your {Kid Pirates} type Leader or Character cards gains +500...
- Current state: existing handler, untracked. Registered timings: `main, trigger`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: Leader-or-Character target prompt; DON cost / DON state helper
- Required test seeding: Kid Pirates leader / field; specific DON threshold
- Acceptance: Printed main / trigger text resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-079 Viola
- Printed: [On Play] Your opponent places 3 cards from their trash at the bottom of their deck in any order.
- Current state: existing handler, untracked. Registered timings: `on_play`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: None expected beyond the existing effect helpers.
- Required test seeding: trash count / trash contents
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-080 Elizabello II
- Printed: [When Attacking] [Once Per Turn] You may return 20 cards from your trash to your deck and shuffle it: This Character gains [Double Attack] and +10000 power during this battle. /...
- Current state: existing handler, untracked. Registered timings: `on_attack`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: None expected beyond the existing effect helpers.
- Required test seeding: trash count / trash contents
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-081 One-Legged Toy Soldier
- Printed: [Activate: Main] You may trash this Character: Give up to 1 of your opponent's Characters −3 cost during this turn.
- Current state: existing handler, untracked. Registered timings: `activate`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: None expected beyond the existing effect helpers.
- Required test seeding: trash count / trash contents
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-082 Shirahoshi
- Printed: [Activate: Main] You may rest this Character and place 2 cards from your trash at the bottom of your deck in any order: If your opponent has 6 or more cards in their hand, your ...
- Current state: existing handler, untracked. Registered timings: `activate`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: None expected beyond the existing effect helpers.
- Required test seeding: trash count / trash contents
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-084 Saint Charlos
- Printed: [Your Turn] If the only Characters on your field are {Celestial Dragons} type Characters, give all of your opponent's Characters −4 cost.
- Current state: existing handler, untracked. Registered timings: `continuous`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: None expected beyond the existing effect helpers.
- Required test seeding: Celestial Dragons field / hand
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-087 Hakuba
- Printed: [DON!! x1] [When Attacking] You may K.O. 1 of your Characters other than this Character: Give up to 1 of your opponent's Characters −5 cost during this turn.
- Current state: existing handler, untracked. Registered timings: `on_attack`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: DON cost / DON state helper
- Required test seeding: Default board state is likely enough.
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-088 Mansherry
- Printed: [Activate: Main] ➀ (You may rest the specified number of DON!! cards in your cost area.) You may rest this Character and place 2 cards from your trash at the bottom of your deck...
- Current state: existing handler, untracked. Registered timings: `activate`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: DON cost / DON state helper
- Required test seeding: specific DON threshold; trash count / trash contents; exact cost / power breakpoints
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-089 Saint Mjosgard
- Printed: [Activate: Main] ➀ (You may rest the specified number of DON!! cards in your cost area.) You may rest this Character and 1 of your Characters: Add up to 1 black Character card w...
- Current state: existing handler, untracked. Registered timings: `activate`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: DON cost / DON state helper
- Required test seeding: specific DON threshold; trash count / trash contents; exact cost / power breakpoints
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-090 Riku Doldo III
- Printed: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) / [On Play]/[On K.O.] Up to 1 of your {Dressrosa} type Charac...
- Current state: existing handler, untracked. Registered timings: `blocker, on_play, on_ko`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: None expected beyond the existing effect helpers.
- Required test seeding: Default board state is likely enough.
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-091 Rebecca
- Printed: [Blocker] / [On Play] Add up to 1 black Character card with a cost of 3 to 7 other than [Rebecca] from your trash to your hand. Then, play up to 1 black Character card with a co...
- Current state: existing handler, untracked. Registered timings: `blocker, on_play`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: None expected beyond the existing effect helpers.
- Required test seeding: trash count / trash contents; rested targets; exact cost / power breakpoints
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-092 Saint Rosward
- Printed: [Your Turn] If the only Characters on your field are {Celestial Dragons} type Characters, give all of your opponent's Characters −6 cost.
- Current state: existing handler, untracked. Registered timings: `continuous`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: None expected beyond the existing effect helpers.
- Required test seeding: Celestial Dragons field / hand
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-093 Rob Lucci
- Printed: [On Play] You may place 3 cards from your trash at the bottom of your deck in any order: K.O. up to 1 of your opponent's Characters with a cost of 2 or less and up to 1 of your ...
- Current state: existing handler, untracked. Registered timings: `on_play`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: None expected beyond the existing effect helpers.
- Required test seeding: trash count / trash contents; exact cost / power breakpoints
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-094 Haute Couture Patch★Work
- Printed: [Main] Give up to 1 of your opponent's Characters −3 cost during this turn. Then, up to 1 of your opponent's Characters with a cost of 0 will not become active in the next Refre...
- Current state: existing handler, untracked. Registered timings: `main, trigger`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: None expected beyond the existing effect helpers.
- Required test seeding: trash count / trash contents; exact cost / power breakpoints
- Acceptance: Printed main / trigger text resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-095 Dragon Claw
- Printed: [Counter] Up to 1 of your Leader or Character cards gains +4000 power during this battle. Then, if you have 15 or more cards in your trash, K.O. up to 1 of your opponent's Chara...
- Current state: existing handler, untracked. Registered timings: `COUNTER`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: Leader-or-Character target prompt
- Required test seeding: trash count / trash contents; exact cost / power breakpoints
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-096 I Bid 500 Million!!
- Printed: [Main] Choose one: / • K.O. up to 1 of your opponent's Characters with a cost of 1 or less. / • Return up to 1 of your opponent's Characters with a cost of 1 or less to the owne...
- Current state: existing handler, untracked. Registered timings: `MAIN, trigger`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: Life-area helper
- Required test seeding: Celestial Dragons field / hand; life count / life pile setup; exact cost / power breakpoints
- Acceptance: Printed main / trigger text resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-097 Mary Geoise
- Printed: [Your Turn] The cost of playing {Celestial Dragons} type Character cards with a cost of 2 or more from your hand will be reduced by 1.
- Current state: existing handler, untracked. Registered timings: `continuous`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: None expected beyond the existing effect helpers.
- Required test seeding: Celestial Dragons field / hand; exact cost / power breakpoints
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-098 Enel
- Printed: [Opponent's Turn] [Once Per Turn] When your number of Life cards becomes 0, add 1 card from the top of your deck to the top of your Life cards. Then, trash 1 card from your hand.
- Current state: partial handler. Registered timings: `on_life_zero`.
- Missing behavior: Add the missing timing hook(s): continuous. Then audit the full printed branches against the current code.
- Required engine/helper support: search / reorder helper; Life-area helper
- Required test seeding: trash count / trash contents; life count / life pile setup
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-099 Amazon
- Printed: [On Your Opponent's Attack] You may rest this Character: Your opponent may trash 1 card from the top of their Life cards. If they do not, give up to 1 of your opponent's Leader ...
- Current state: existing handler, untracked. Registered timings: `on_opponent_attack`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: Leader-or-Character target prompt; Life-area helper
- Required test seeding: trash count / trash contents; life count / life pile setup
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-100 Enel
- Printed: [Rush] / [Once Per Turn] If this Character would leave the field, you may trash 1 card from the top of your Life cards instead. If there is a [Monkey.D.Luffy] Character, this ef...
- Current state: existing handler, untracked. Registered timings: `continuous, on_leave_prevention`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: KO replacement / prevention hook; Life-area helper
- Required test seeding: trash count / trash contents; life count / life pile setup
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-101 Ohm
- Printed: If you have 2 or less Life cards, this Character gains +1000 power. / [On Play] Look at 5 cards from the top of your deck; reveal up to 1 [Holly] and add it to your hand. Then, ...
- Current state: existing handler, untracked. Registered timings: `continuous, on_play`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: search / reorder helper; Life-area helper
- Required test seeding: life count / life pile setup
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-102 Gedatsu
- Printed: [On Play] K.O. up to 1 of your opponent's Characters with a cost equal to or less than the number of your opponent's Life cards.
- Current state: existing handler, untracked. Registered timings: `on_play`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: Life-area helper
- Required test seeding: life count / life pile setup
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-103 Kotori
- Printed: [On Play] If you have [Hotori], K.O. up to 1 of your opponent's Characters with a cost equal to or less than the number of your opponent's Life cards.
- Current state: existing handler, untracked. Registered timings: `on_play`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: Life-area helper
- Required test seeding: life count / life pile setup
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-104 Conis
- Printed: [On Play] You may place 1 of your Stages at the bottom of your deck: Draw 1 card and trash 1 card from your hand.
- Current state: existing handler, untracked. Registered timings: `on_play`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: None expected beyond the existing effect helpers.
- Required test seeding: trash count / trash contents
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-105 Satori
- Printed: [Trigger] You may trash 1 card from your hand: Play this card.
- Current state: existing handler, untracked. Registered timings: `trigger`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: None expected beyond the existing effect helpers.
- Required test seeding: trash count / trash contents
- Acceptance: Printed main / trigger text resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-106 Shura
- Printed: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 {Sky Island} type card other than [Shura] and add it to your hand. Then, place the rest at the bottom of your...
- Current state: existing handler, untracked. Registered timings: `on_play, trigger`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: search / reorder helper
- Required test seeding: Sky Island deck / field
- Acceptance: Printed main / trigger text resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-107 Lieutenant Spacey
- Printed: [Your Turn] [Once Per Turn] When a card is added to your hand from your Life, this Character gains +2000 power during this turn.
- Current state: partial handler. Registered timings: `on_life_add`.
- Missing behavior: Add the missing timing hook(s): continuous. Then audit the full printed branches against the current code.
- Required engine/helper support: Life-area helper
- Required test seeding: life count / life pile setup
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-108 Nola
- Printed: No printed custom effect or trigger text.
- Current state: no custom code actually needed. Registered timings: `none`.
- Missing behavior: Add tracker coverage and verify the simulator does not need card-specific logic.
- Required engine/helper support: None expected.
- Required test seeding: Default board state is likely enough.
- Acceptance: Tracker row exists and the card plays correctly with baseline keyword / core engine behavior only.

### OP05-109 Pagaya
- Printed: [Once Per Turn] When a [Trigger] activates, draw 2 cards and trash 2 cards from your hand.
- Current state: existing handler, untracked. Registered timings: `on_trigger`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: None expected beyond the existing effect helpers.
- Required test seeding: trash count / trash contents
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-110 Holly
- Printed: No printed custom effect or trigger text.
- Current state: no custom code actually needed. Registered timings: `none`.
- Missing behavior: Add tracker coverage and verify the simulator does not need card-specific logic.
- Required engine/helper support: None expected.
- Required test seeding: Default board state is likely enough.
- Acceptance: Tracker row exists and the card plays correctly with baseline keyword / core engine behavior only.

### OP05-111 Hotori
- Printed: [On Play] You may play 1 [Kotori] from your hand: Add up to 1 of your opponent's Characters with a cost of 3 or less to the top or bottom of your opponent's Life cards face-up.
- Current state: existing handler, untracked. Registered timings: `on_play`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: Life-area helper
- Required test seeding: life count / life pile setup; exact cost / power breakpoints
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-112 Captain McKinley
- Printed: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) / [On K.O.] Play up to 1 {Sky Island} type Character card wit...
- Current state: existing handler, untracked. Registered timings: `blocker, on_ko`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: None expected beyond the existing effect helpers.
- Required test seeding: Sky Island deck / field; exact cost / power breakpoints
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-113 Yama
- Printed: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Current state: existing handler, untracked. Registered timings: `blocker`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: None expected beyond the existing effect helpers.
- Required test seeding: Default board state is likely enough.
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-114 El Thor
- Printed: [Counter] Up to 1 of your Leader or Character cards gains +2000 power during this battle. Then, if your opponent has 2 or less Life cards, that card gains an additional +2000 po...
- Current state: existing handler, untracked. Registered timings: `COUNTER, trigger`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: Leader-or-Character target prompt; Life-area helper
- Required test seeding: life count / life pile setup
- Acceptance: Printed main / trigger text resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-115 Two-Hundred Million Volts Amaru
- Printed: [Main] Up to 1 of your Leader or Character cards gains +3000 power during this turn. Then, if you have 1 or less Life cards, rest up to 1 of your opponent's Characters with a co...
- Current state: existing handler, untracked. Registered timings: `MAIN, trigger`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: Leader-or-Character target prompt; search / reorder helper; Life-area helper
- Required test seeding: trash count / trash contents; life count / life pile setup; exact cost / power breakpoints
- Acceptance: Printed main / trigger text resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-116 Hino Bird Zap
- Printed: [Main] K.O. up to 1 of your opponent's Characters with a cost equal to or less than the number of your opponent's Life cards. Trigger: [Trigger] Activate this card's [Main] effect.
- Current state: existing handler, untracked. Registered timings: `main, trigger`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: Life-area helper
- Required test seeding: life count / life pile setup
- Acceptance: Printed main / trigger text resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-117 Upper Yard
- Printed: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 {Sky Island} type card and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Current state: existing handler, untracked. Registered timings: `on_play`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: search / reorder helper
- Required test seeding: Sky Island deck / field
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-118 Kaido
- Printed: [On Play] Draw 4 cards if your opponent has 3 or less Life cards.
- Current state: existing handler, untracked. Registered timings: `on_play`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: Life-area helper
- Required test seeding: life count / life pile setup
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.

### OP05-119 Monkey.D.Luffy
- Printed: [On Play] DON!! −10: Place all of your Characters except this Character at the bottom of your deck in any order. Then, take an extra turn after this one. / [Activate: Main] [Onc...
- Current state: existing handler, untracked. Registered timings: `ACTIVATE_MAIN, on_play, activate`.
- Missing behavior: Audit the current handler against printed text and tighten prompts, optional branches, ordering, and duration where needed.
- Required engine/helper support: DON cost / DON state helper
- Required test seeding: specific DON threshold
- Acceptance: Printed effect resolves with the correct timing, prompts, costs, zone moves, and no exceptions.
