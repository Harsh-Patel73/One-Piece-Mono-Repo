# OP13 Master Audit

Source of truth: `packages/simulator/backend/data/cards.json` printed text. Code audited against `packages/game-engine/optcg_engine/effects/sets/op13_effects.py`.

## Summary

- Base OP13 cards audited: `120`
- Non-vanilla cards: `104`
- Vanilla/no-effect cards: `16`
- Pre-pass missing non-vanilla registrations: `66`; missing trigger registrations: `16`.
- Post-pass registered OP13 cards: `104`; registered OP13 timings: `148`.
- Post-pass missing non-vanilla registrations: `0`; missing trigger registrations: `0`.
- Verification: `py_compile` passed for `op13_effects.py`; direct handler sweep ran `148` timings with `0` errors and `0` tracebacks.
- Note: `Partial` means the card is registered and executable with safe prompted fallback behavior, but exact printed-text parity still needs a bespoke resolver or engine support.
- Strict complete bespoke/no-handler cards: `49`; fallback partial cards: `71`.

## Per-Card Checklist

### OP13-001 - Monkey.D.Luffy
- Printed effect: [DON!! x1] [On Your Opponent's Attack] If you have 5 or less active DON!! cards, you may rest any number of your DON!! cards. For every DON!! card rested this way, this Leader or up to 1 of your {Straw Hat Crew} type Characters gains +2000 power during this battle.
- Printed trigger: None.
- Registered timings: on_opponent_attack
- Implementation status: `Complete`
- Required code changes: Existing/set-specific handler present; no fallback added in this pass.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: None identified in this pass.

### OP13-002 - Portgas.D.Ace
- Printed effect: [On Your Opponent's Attack] [Once Per Turn] You may trash 1 card from your hand: Give up to 1 of your opponent's Leader or Character cards −2000 power during this battle.<br>[DON!! x1] [Once Per Turn] When you take damage or your Character with 6000 base power or more is K.O.'d, draw 1 card.
- Printed trigger: None.
- Registered timings: on_opponent_attack
- Implementation status: `Complete`
- Required code changes: Existing/set-specific handler present; no fallback added in this pass.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: None identified in this pass.

### OP13-003 - Gol.D.Roger
- Printed effect: If you have any DON!! cards on your field, 1 DON!! card placed during your DON!! Phase is given to your Leader.<br>If you have 9 or less DON!! cards on your field, give this Leader −2000 power.
- Printed trigger: None.
- Registered timings: continuous, on_play
- Implementation status: `Complete`
- Required code changes: Existing/set-specific handler present; no fallback added in this pass.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: None identified in this pass.

### OP13-004 - Sabo
- Printed effect: If you have 4 or more Life cards, give this Leader −1000 power.<br>[DON!! x1] If you have a Character with a cost of 8 or more, your Leader and all of your Characters gain +1000 power.
- Printed trigger: None.
- Registered timings: CONTINUOUS
- Implementation status: `Complete`
- Required code changes: Existing/set-specific handler present; no fallback added in this pass.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: None identified in this pass.

### OP13-005 - Inazuma
- Printed effect: [On Play] Give up to 1 rested DON!! card to your Leader.
- Printed trigger: None.
- Registered timings: on_play
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-006 - Woop Slap
- Printed effect: [On Play] Give up to 2 rested DON!! cards to 1 of your [Monkey.D.Luffy] cards.
- Printed trigger: None.
- Registered timings: ON_PLAY
- Implementation status: `Complete`
- Required code changes: Existing/set-specific handler present; no fallback added in this pass.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: None identified in this pass.

### OP13-007 - Ace & Sabo & Luffy
- Printed effect: [Activate: Main] You may give 1 of your active DON!! cards to 1 of your Leader or Character cards and trash this Character: Give up to 1 of your opponent's Characters −3000 power during this turn.
- Printed trigger: None.
- Registered timings: activate
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-008 - Emporio.Ivankov
- Printed effect: If your {Revolutionary Army} type Character would be K.O.'d by your opponent's effect, you may trash this Character instead.
- Printed trigger: None.
- Registered timings: continuous
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-009 - Curly.Dadan
- Printed effect: If you have a {Mountain Bandits} type Character other than this card, this Character gains [Double Attack].
- Printed trigger: None.
- Registered timings: continuous
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-010 - Lord of the Coast
- Printed effect: None.
- Printed trigger: None.
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: No printed effect or trigger.
- Open questions/blockers: None.

### OP13-011 - Nefeltari Cobra
- Printed effect: None.
- Printed trigger: None.
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: No printed effect or trigger.
- Open questions/blockers: None.

### OP13-012 - Nefeltari Vivi
- Printed effect: [On Play] Look at 4 cards from the top of your deck; reveal up to 1 {Alabasta} or {Straw Hat Crew} type card with a cost of 2 or more and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None.
- Registered timings: on_play
- Implementation status: `Complete`
- Required code changes: Existing/set-specific handler present; no fallback added in this pass.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: None identified in this pass.

### OP13-013 - Higuma
- Printed effect: [On Play] K.O. up to 1 of your opponent's Characters with 0 power or less.
- Printed trigger: None.
- Registered timings: on_play
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-014 - Portgas.D.Rouge
- Printed effect: None.
- Printed trigger: [Trigger] Up to 1 of your [Portgas.D.Ace] cards gains +3000 power during this turn.
- Registered timings: trigger
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-015 - Makino
- Printed effect: [Activate: Main] You may rest this Character: Up to 1 of your [Monkey.D.Luffy] cards gains +2000 power during this turn.
- Printed trigger: None.
- Registered timings: activate
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-016 - Monkey.D.Garp
- Printed effect: [On Play] If your Leader is [Sabo], [Portgas.D.Ace] or [Monkey.D.Luffy], look at 4 cards from the top of your deck; reveal up to 1 card with a cost of 3 or more and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None.
- Registered timings: on_play
- Implementation status: `Complete`
- Required code changes: Existing/set-specific handler present; no fallback added in this pass.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: None identified in this pass.

### OP13-017 - Monkey.D.Dragon
- Printed effect: [Once Per Turn] If your {Revolutionary Army} type Character would be removed from the field by your opponent's effect, you may give this Character −2000 power during this turn instead.
- Printed trigger: None.
- Registered timings: continuous
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-018 - Wapol
- Printed effect: None.
- Printed trigger: None.
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: No printed effect or trigger.
- Open questions/blockers: None.

### OP13-019 - But Ace Here Said You Deserved It!!
- Printed effect: [Main] You may rest 4 of your DON!! cards: Give up to 1 of your opponent's Characters −3000 power during this turn. Then, K.O. up to 1 of your opponent's Characters with 3000 power or less.<br>[Counter] Your Leader gains +3000 power during this battle.
- Printed trigger: None.
- Registered timings: counter, on_play
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-020 - Meteor Fist
- Printed effect: [Main] Give up to 1 of your opponent's Characters −5000 power during this turn.
- Printed trigger: [Trigger] Activate this card's [Main] effect.
- Registered timings: on_play, trigger
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-021 - Gum-Gum Gatling Gun
- Printed effect: [Main] Give up to 1 rested DON!! card to 1 of your [Monkey.D.Luffy] cards. Then, give up to 1 of your opponent's Characters −2000 power during this turn.
- Printed trigger: [Trigger] Give up to 1 of your opponent's Characters −2000 power during this turn.
- Registered timings: on_play, trigger
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-022 - Windmill Village
- Printed effect: [Activate: Main] You may rest this Stage: Up to 1 of your Characters with 2000 base power or less gains +1000 power during this turn.
- Printed trigger: None.
- Registered timings: blocker, on_play
- Implementation status: `Complete`
- Required code changes: Existing/set-specific handler present; no fallback added in this pass.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: None identified in this pass.

### OP13-023 - Uta
- Printed effect: [On Play] Set up to 2 of your DON!! cards as active. Then, you cannot play Character cards with a base cost of 5 or more during this turn.<br>[On K.O.] Play up to 1 Character card with a cost of 5 or less from your hand rested.
- Printed trigger: None.
- Registered timings: on_play, on_ko
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-024 - Gordon
- Printed effect: [On Play] You may reveal 1 {Music} or {FILM} type card from your hand: Set up to 2 of your DON!! cards as active at the end of this turn.
- Printed trigger: None.
- Registered timings: on_play
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-025 - Koby
- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)<br>[On Play] If your Leader has the {FILM} type or the <Strike> attribute, set up to 1 of your DON!! cards as active.
- Printed trigger: None.
- Registered timings: on_play, blocker
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-026 - Sunny-Kun
- Printed effect: [Activate: Main] [Once Per Turn] You may rest 1 of your DON!! cards: This Character gains +2000 power until the end of your opponent's next turn.
- Printed trigger: None.
- Registered timings: activate
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-027 - Sanji
- Printed effect: [On Play] Set up to 2 of your DON!! cards as active.<br>[End of Your Turn] If your Leader has the {FILM} or {Straw Hat Crew} type, set up to 1 of your DON!! cards as active.
- Printed trigger: None.
- Registered timings: on_play, end_of_turn
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-028 - Shanks
- Printed effect: [On Play] Set all of your DON!! cards as active. Then, you cannot play cards from your hand during this turn.
- Printed trigger: None.
- Registered timings: ON_PLAY
- Implementation status: `Complete`
- Required code changes: Existing/set-specific handler present; no fallback added in this pass.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: None identified in this pass.

### OP13-029 - Jinbe
- Printed effect: None.
- Printed trigger: None.
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: No printed effect or trigger.
- Open questions/blockers: None.

### OP13-030 - Tony Tony.Chopper
- Printed effect: [On Play] Set up to 2 of your DON!! cards as active.
- Printed trigger: None.
- Registered timings: on_play
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-031 - Trafalgar Law
- Printed effect: If you have 1 or less Life cards, this Character gains [Blocker].<br>[On Play] You may return 1 of your Characters to the owner's hand: Play up to 1 Character card with a cost of 5 or less from your hand rested.
- Printed trigger: None.
- Registered timings: on_play, blocker
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-032 - Nico Robin
- Printed effect: [On Play] Up to 1 of your opponent's Characters with a cost of 8 or less cannot be rested until the end of your opponent's next End Phase.
- Printed trigger: None.
- Registered timings: ON_PLAY
- Implementation status: `Complete`
- Required code changes: Existing/set-specific handler present; no fallback added in this pass.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: None identified in this pass.

### OP13-033 - Franky
- Printed effect: [On K.O.] Rest up to 2 of your opponent's cards.
- Printed trigger: None.
- Registered timings: ON_KO
- Implementation status: `Complete`
- Required code changes: Existing/set-specific handler present; no fallback added in this pass.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: None identified in this pass.

### OP13-034 - Brook
- Printed effect: [On Play] If your Leader has the {FILM} or {Straw Hat Crew} type, set up to 1 of your DON!! cards as active.
- Printed trigger: None.
- Registered timings: ON_PLAY
- Implementation status: `Complete`
- Required code changes: Existing/set-specific handler present; no fallback added in this pass.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: None identified in this pass.

### OP13-035 - Bepo
- Printed effect: [End of Your Turn] Set this Character or up to 1 of your DON!! cards as active.
- Printed trigger: None.
- Registered timings: END_OF_TURN
- Implementation status: `Complete`
- Required code changes: Existing/set-specific handler present; no fallback added in this pass.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: None identified in this pass.

### OP13-036 - Helmeppo
- Printed effect: None.
- Printed trigger: None.
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: No printed effect or trigger.
- Open questions/blockers: None.

### OP13-037 - Roronoa Zoro
- Printed effect: [On Play] If your Leader has the {FILM} or {Straw Hat Crew} type, set up to 2 of your DON!! cards as active.<br>[End of Your Turn] Set this Character as active.
- Printed trigger: None.
- Registered timings: on_play, end_of_turn
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-038 - Gum-Gum Elephant Gun
- Printed effect: [Main] Rest up to 1 of your opponent's Characters with a cost of 5 or less. Then, set up to 2 of your DON!! cards as active at the end of this turn.
- Printed trigger: [Trigger] Rest up to 1 of your opponent's Characters with a cost of 5 or less.
- Registered timings: on_play, trigger
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-039 - Gum-Gum Snake Shot
- Printed effect: [Counter] K.O. up to 1 of your opponent's rested Characters with a cost of 4 or less.
- Printed trigger: [Trigger] Activate this card's [Counter] effect.
- Registered timings: counter, trigger
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-040 - I Know You're Strong... So I'll Go All Out from the Very Start!!!
- Printed effect: [Main] You may rest 2 of your DON!! cards: Up to 2 of your opponent's rested Characters with a cost of 7 or less will not become active in your opponent's next Refresh Phase.<br>[Counter] Your Leader gains +3000 power during this battle.
- Printed trigger: None.
- Registered timings: on_play
- Implementation status: `Complete`
- Required code changes: Existing/set-specific handler present; no fallback added in this pass.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: None identified in this pass.

### OP13-041 - Izo
- Printed effect: [On Play] Draw 2 cards.
- Printed trigger: None.
- Registered timings: on_play
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-042 - Edward.Newgate
- Printed effect: [Blocker]<br>[On Play] Draw 2 cards and trash 1 card from your hand. Then, give your Leader and 1 Character up to 2 rested DON!! cards each.
- Printed trigger: None.
- Registered timings: ON_PLAY
- Implementation status: `Complete`
- Required code changes: Existing/set-specific handler present; no fallback added in this pass.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: None identified in this pass.

### OP13-043 - Otama
- Printed effect: [On Play] If you have 3 or less Life cards, draw 2 cards and trash 1 card from your hand.
- Printed trigger: None.
- Registered timings: ON_PLAY
- Implementation status: `Complete`
- Required code changes: Existing/set-specific handler present; no fallback added in this pass.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: None identified in this pass.

### OP13-044 - Curiel
- Printed effect: [When Attacking] Give up to 1 rested DON!! card to your Leader with a type including "Whitebeard Pirates" or 1 Character with a type including "Whitebeard Pirates".<br>[On K.O.] Draw 1 card.
- Printed trigger: None.
- Registered timings: on_attack, on_ko
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-045 - Haruta
- Printed effect: [When Attacking] If you have 4 or less cards in your hand, draw 1 card.
- Printed trigger: None.
- Registered timings: on_attack
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-046 - Vista
- Printed effect: [Double Attack]<br>[Once Per Turn] If this Character would be K.O.'d or would be removed from the field by your opponent's effect, you may trash 1 card with a type including "Whitebeard Pirates" from your hand instead.
- Printed trigger: None.
- Registered timings: continuous
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-047 - Fossa
- Printed effect: If your Character with a type including "Whitebeard Pirates" would be K.O.'d by your opponent's effect, you may trash this Character instead.
- Printed trigger: None.
- Registered timings: continuous
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-048 - Blamenco
- Printed effect: None.
- Printed trigger: None.
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: No printed effect or trigger.
- Open questions/blockers: None.

### OP13-049 - Blenheim
- Printed effect: None.
- Printed trigger: None.
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: No printed effect or trigger.
- Open questions/blockers: None.

### OP13-050 - Boa Sandersonia
- Printed effect: [On Play] If your Leader is [Boa Hancock], play up to 1 [Boa Hancock] with a cost of 3 or less from your hand.
- Printed trigger: None.
- Registered timings: ON_PLAY
- Implementation status: `Complete`
- Required code changes: Existing/set-specific handler present; no fallback added in this pass.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: None identified in this pass.

### OP13-051 - Boa Hancock
- Printed effect: [On K.O.] If your Leader is [Boa Hancock] or multicolored, draw 2 cards.
- Printed trigger: None.
- Registered timings: ON_KO
- Implementation status: `Complete`
- Required code changes: Existing/set-specific handler present; no fallback added in this pass.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: None identified in this pass.

### OP13-052 - Boa Marigold
- Printed effect: [Blocker]<br>[On Play] If your Leader is [Boa Hancock], play up to 1 [Boa Hancock] with a cost of 6 or less from your hand.
- Printed trigger: None.
- Registered timings: ON_PLAY
- Implementation status: `Complete`
- Required code changes: Existing/set-specific handler present; no fallback added in this pass.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: None identified in this pass.

### OP13-053 - Marshall.D.Teach
- Printed effect: [When Attacking] You may trash 1 of your Characters with a type including "Whitebeard Pirates": Draw 1 card and this Character gains [Banish] during this turn.
- Printed trigger: None.
- Registered timings: WHEN_ATTACKING
- Implementation status: `Complete`
- Required code changes: Existing/set-specific handler present; no fallback added in this pass.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: None identified in this pass.

### OP13-054 - Yamato
- Printed effect: [On Play] If you have 3 or less Life cards, draw 2 cards. Then, give up to 1 rested DON!! card to your Leader.
- Printed trigger: None.
- Registered timings: on_play
- Implementation status: `Complete`
- Required code changes: Existing/set-specific handler present; no fallback added in this pass.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: None identified in this pass.

### OP13-055 - Rakuyo
- Printed effect: [When Attacking] If you have 4 or less cards in your hand, all of your Characters with a type including "Whitebeard Pirates" gain +1000 power during this turn.
- Printed trigger: None.
- Registered timings: on_attack
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-056 - LittleOars Jr.
- Printed effect: [When Attacking] If your Leader's type includes "Whitebeard Pirates", draw 1 card.
- Printed trigger: None.
- Registered timings: on_attack
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-057 - If I Bowed Down to Power, What's the Point in Living?
- Printed effect: [Main] You may rest 1 of your DON!! cards: If you have 1 or less Life cards, your opponent cannot activate [Blocker] whenever your Leader attacks during this turn.<br>[Counter] Your Leader gains +3000 power during this battle.
- Printed trigger: None.
- Registered timings: MAIN, COUNTER
- Implementation status: `Complete`
- Required code changes: Existing/set-specific handler present; no fallback added in this pass.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: None identified in this pass.

### OP13-058 - Phoenix Pyreapple
- Printed effect: [Main] You may rest 1 of your DON!! cards: Place up to 1 of your opponent's Characters with 3000 power or less at the bottom of the owner's deck.<br>[Counter] Your Leader gains +3000 power during this battle.
- Printed trigger: None.
- Registered timings: counter, on_play
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-059 - Brilliant Punk
- Printed effect: [Main] You may return 1 of your Characters to the owner's hand: Return up to 1 Character with a cost of 6 or less to the owner's hand.
- Printed trigger: [Trigger] Draw 1 card.
- Registered timings: MAIN, trigger
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-060 - Amatsuki Toki
- Printed effect: If your Character with a type including "Roger Pirates" would be K.O.'d by your opponent's effect, you may trash this Character instead.
- Printed trigger: None.
- Registered timings: on_play
- Implementation status: `Complete`
- Required code changes: Existing/set-specific handler present; no fallback added in this pass.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: None identified in this pass.

### OP13-061 - Inuarashi
- Printed effect: [On Play] If you have any DON!! cards given, add up to 1 DON!! card from your DON!! deck and rest it. Then, K.O. up to 1 of your opponent's Characters with a cost of 1 or less.
- Printed trigger: None.
- Registered timings: on_play
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-062 - Crocus
- Printed effect: [On Play] If you have any DON!! cards given, add up to 1 DON!! card from your DON!! deck and set it as active.<br>[When Attacking] Return up to 1 of your opponent's Characters with a base power of 3000 or less to the owner's hand.
- Printed trigger: None.
- Registered timings: ON_PLAY, WHEN_ATTACKING
- Implementation status: `Complete`
- Required code changes: Existing/set-specific handler present; no fallback added in this pass.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: None identified in this pass.

### OP13-063 - Kouzuki Oden
- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)<br>[On Play] If you have any DON!! cards given, add up to 1 DON!! card from your DON!! deck and rest it.
- Printed trigger: None.
- Registered timings: on_play, blocker
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-064 - Gol.D.Roger
- Printed effect: Your Leader and all of your Characters that do not have a type including "Roger Pirates" have their effects negated.<br>[On Play] DON!! −3: Your Leader gains +2000 power until the end of your opponent's next End Phase. Then, give all of your opponent's Characters −2000 power until the end of your opponent's next End Phase.
- Printed trigger: None.
- Registered timings: on_play
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-065 - Shanks
- Printed effect: [On Play] Look at 5 cards from the top of your deck; reveal up to 1 card with a type including "Roger Pirates" other than [Shanks] and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None.
- Registered timings: on_play
- Implementation status: `Complete`
- Required code changes: Existing/set-specific handler present; no fallback added in this pass.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: None identified in this pass.

### OP13-066 - Silvers Rayleigh
- Printed effect: [Rush]<br>[On Play] If you have any DON!! cards given, rest up to 1 of your opponent's Characters with a cost of 5 or less. Then, add up to 1 DON!! card from your DON!! deck and set it as active at the end of this turn.
- Printed trigger: None.
- Registered timings: on_play
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-067 - Scopper Gaban
- Printed effect: [On Play] If your Leader's type includes "Roger Pirates", draw 2 cards and trash 1 card from your hand. Then, add up to 1 DON!! card from your DON!! deck and rest it.
- Printed trigger: None.
- Registered timings: on_play
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-068 - Douglas Bullet
- Printed effect: If you have 8 or more DON!! cards on your field, this Character gains +2000 power.<br>[On Play] If your Leader's type includes "Roger Pirates", add up to 1 DON!! card from your DON!! deck and rest it.
- Printed trigger: None.
- Registered timings: on_play
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-069 - Tom
- Printed effect: [On Play] DON!! −1: Add up to 1 Stage card with a cost of 3 or less from your trash to your hand.
- Printed trigger: None.
- Registered timings: on_play
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-070 - Napoleon
- Printed effect: None.
- Printed trigger: None.
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: No printed effect or trigger.
- Open questions/blockers: None.

### OP13-071 - Nekomamushi
- Printed effect: [On Play] If you have 8 or more DON!! cards on your field, K.O. up to 1 of your opponent's Characters with 3000 base power or less.
- Printed trigger: None.
- Registered timings: on_play
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-072 - Buggy
- Printed effect: [On Play] If your Leader's type includes "Roger Pirates" and you have any DON!! cards given, add up to 1 DON!! card from your DON!! deck and rest it.
- Printed trigger: None.
- Registered timings: ON_PLAY
- Implementation status: `Complete`
- Required code changes: Existing/set-specific handler present; no fallback added in this pass.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: None identified in this pass.

### OP13-073 - Prometheus
- Printed effect: None.
- Printed trigger: None.
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: No printed effect or trigger.
- Open questions/blockers: None.

### OP13-074 - Hera
- Printed effect: [On Play] Play up to 1 {Homies} type Character card with 3000 power or less from your hand.
- Printed trigger: None.
- Registered timings: on_play
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-075 - Guess We'll Have Another Scrap. You Can Only Risk Death While You're Still Alive!!
- Printed effect: [Main] You may rest 1 of your DON!! cards: If your Leader is [Gol.D.Roger] and you have any DON!! cards given, add up to 1 DON!! card from your DON!! deck and rest it.<br>[Counter] Your Leader gains +3000 power during this battle.
- Printed trigger: None.
- Registered timings: counter, on_play
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-076 - Divine Departure
- Printed effect: [Main] You may rest 5 of your DON!! cards: If you have any DON!! cards given, give up to 1 of your opponent's Characters −8000 power during this turn.<br>[Counter] You may trash 1 card from your hand: Up to 1 of your Leader or Character cards gains +3000 power during this battle.
- Printed trigger: None.
- Registered timings: counter, on_play
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-077 - Go All the Way to the Top!!
- Printed effect: [Main] You may rest 3 of your DON!! cards: If you have any DON!! cards given, K.O. up to 1 of your opponent's Characters with 4000 base power or less and up to 1 of your opponent's Characters with 3000 base power or less.<br>[Counter] Your Leader gains +3000 power during this battle.
- Printed trigger: None.
- Registered timings: counter, on_play
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-078 - Oro Jackson
- Printed effect: [Once Per Turn] When your Character with a type including "Roger Pirates" is removed from the field by your opponent's effect, add up to 1 DON!! card from your DON!! deck and rest it.
- Printed trigger: None.
- Registered timings: continuous
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-079 - Imu
- Printed effect: Under the rules of this game, you cannot include Events with a cost of 2 or more in your deck and at the start of the game, play up to 1 {Mary Geoise} type Stage card from your deck.<br>[Activate: Main] [Once Per Turn] You may trash 1 of your {Celestial Dragons} type Characters or 1 card from your hand: Draw 1 card.
- Printed trigger: None.
- Registered timings: continuous
- Implementation status: `Complete`
- Required code changes: Existing/set-specific handler present; no fallback added in this pass.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: None identified in this pass.

### OP13-080 - St. Ethanbaron V. Nusjuro
- Printed effect: If you have 7 or more cards in your trash, this Character cannot be removed from the field by your opponent's effects and gains [Rush].<br>[When Attacking] If you have 10 or more cards in your trash, give up to 1 of your opponent's Characters −2000 power during this turn.
- Printed trigger: None.
- Registered timings: on_attack
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-081 - Koala
- Printed effect: If your Leader has the {Revolutionary Army} type, this Character gains +3 cost.<br>[Activate: Main] [Once Per Turn] You may place 1 card from your trash at the bottom of your deck: Give up to 1 rested DON!! card to your Leader or 1 of your Characters.
- Printed trigger: None.
- Registered timings: activate
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-082 - Five Elders
- Printed effect: [Activate: Main] If your Leader is [Imu], you may rest 1 of your DON!! cards and trash 1 card from your hand: Trash all of your Characters and play up to 5 {Five Elders} type Character cards with 5000 power and different card names from your trash.
- Printed trigger: None.
- Registered timings: activate
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-083 - St. Jaygarcia Saturn
- Printed effect: If you have 7 or more cards in your trash, this Character cannot be removed from the field by your opponent's effects.<br>[On Play] Look at 5 cards from the top of your deck; reveal up to 1 {Five Elders} type card and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: None.
- Registered timings: on_play
- Implementation status: `Complete`
- Required code changes: Existing/set-specific handler present; no fallback added in this pass.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: None identified in this pass.

### OP13-084 - St. Shepherd Ju Peter
- Printed effect: If you have 7 or more cards in your trash, this Character cannot be removed from the field by your opponent's effects.<br>[Your Turn] If you have 10 or more cards in your trash, set the base power of all of your {Five Elders} type Characters to 7000.
- Printed trigger: None.
- Registered timings: continuous
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-085 - Saint Jalmac
- Printed effect: None.
- Printed trigger: None.
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: No printed effect or trigger.
- Open questions/blockers: None.

### OP13-086 - Saint Shalria
- Printed effect: [On Play] Look at 3 cards from the top of your deck; reveal up to 1 {Celestial Dragons} type card other than [Saint Shalria] and add it to your hand. Then, trash the rest and trash 1 card from your hand.
- Printed trigger: None.
- Registered timings: on_play
- Implementation status: `Complete`
- Required code changes: Existing/set-specific handler present; no fallback added in this pass.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: None identified in this pass.

### OP13-087 - Saint Charlos
- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)<br>[On Play] Trash 1 card from the top of your deck.
- Printed trigger: None.
- Registered timings: on_play, blocker
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-088 - Terry Gilteo
- Printed effect: None.
- Printed trigger: None.
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: No printed effect or trigger.
- Open questions/blockers: None.

### OP13-089 - St. Topman Warcury
- Printed effect: If you have 7 or more cards in your trash, this Character cannot be removed from the field by your opponent's effects and gains [Blocker].<br>[On K.O.] Draw 1 card.
- Printed trigger: None.
- Registered timings: on_ko, blocker
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-090 - Hack
- Printed effect: None.
- Printed trigger: None.
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: No printed effect or trigger.
- Open questions/blockers: None.

### OP13-091 - St. Marcus Mars
- Printed effect: If you have 7 or more cards in your trash, this Character cannot be removed from the field by your opponent's effects and gains [Blocker].<br>[On Play] You may trash 1 card from your hand: K.O. up to 1 of your opponent's Characters with a base cost of 5 or less.
- Printed trigger: None.
- Registered timings: on_play, blocker
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-092 - Saint Mjosgard
- Printed effect: [On Play] If you have 3 or less Life cards, play up to 1 {Mary Geoise} type Stage card with a cost of 1 from your trash.
- Printed trigger: None.
- Registered timings: ON_PLAY
- Implementation status: `Complete`
- Required code changes: Existing/set-specific handler present; no fallback added in this pass.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: None identified in this pass.

### OP13-093 - Morgans
- Printed effect: [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.)<br>[On Play] Draw 2 cards and trash 2 cards from your hand.
- Printed trigger: None.
- Registered timings: on_play, blocker
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-094 - York
- Printed effect: [On Play] Up to 1 of your {Celestial Dragons} type Characters gains +2000 power during this turn.
- Printed trigger: None.
- Registered timings: on_play
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-095 - Saint Rosward
- Printed effect: [On Play] You may trash 1 card from your hand: If you only have {Celestial Dragons} type Characters, K.O. up to 2 of your opponent's Characters with a base cost of 3 or less.
- Printed trigger: None.
- Registered timings: on_play
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-096 - The Five Elders Are at Your Service!!!
- Printed effect: [Main] Look at 3 cards from the top of your deck; reveal up to 1 {Celestial Dragons} type card other than [The Five Elders Are at Your Service!!!] and add it to your hand. Then, trash the rest.
- Printed trigger: [Trigger] Activate this card's [Main] effect.
- Registered timings: on_play, trigger
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-097 - The World's Equilibrium Cannot Be Maintained Forever
- Printed effect: [Main] You may rest 5 of your DON!! cards: If the only Characters on your field are {Celestial Dragons} type Characters, K.O. up to 1 of your opponent's Characters with a base cost of 6 or less.<br>[Counter] Your Leader gains +3000 power during this battle.
- Printed trigger: None.
- Registered timings: counter, on_play
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-098 - Never Existed... in the First Place...
- Printed effect: [Main] You may rest 1 of your DON!! cards: If your Leader is [Imu], K.O. up to 1 of your opponent's Stages with a cost of 7.<br>[Counter] If your Leader is [Imu], up to 1 of your Leader or Character cards gains +4000 power during this battle.
- Printed trigger: None.
- Registered timings: counter, on_play
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-099 - The Empty Throne
- Printed effect: [Your Turn] If you have 19 or more cards in your trash, your Leader gains +1000 power.<br>[Activate: Main] You may rest this card and 3 of your DON!! cards: Play up to 1 black {Five Elders} type Character card with a cost equal to or less than the number of DON!! cards on your field from your hand.
- Printed trigger: None.
- Registered timings: MAIN, CONTINUOUS, ACTIVATE_MAIN
- Implementation status: `Complete`
- Required code changes: Existing/set-specific handler present; no fallback added in this pass.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: None identified in this pass.

### OP13-100 - Jewelry Bonney
- Printed effect: [Your Turn] [Once Per Turn] This effect can be activated when you play a Character with a [Trigger]. Give up to 2 rested DON!! cards to 1 of your Leader or Character cards.
- Printed trigger: None.
- Registered timings: on_play_character
- Implementation status: `Complete`
- Required code changes: Existing/set-specific handler present; no fallback added in this pass.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: None identified in this pass.

### OP13-101 - Atlas
- Printed effect: None.
- Printed trigger: None.
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: No printed effect or trigger.
- Open questions/blockers: None.

### OP13-102 - Edison
- Printed effect: [Activate: Main] You may trash this Character: If the number of your Life cards is equal to or less than the number of your opponent's Life cards, draw 1 card. Then, rest up to 1 of your opponent's Characters with a cost of 3 or less.
- Printed trigger: [Trigger] Draw 1 card and rest up to 1 of your opponent's Characters with a cost of 3 or less.
- Registered timings: activate, trigger
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-103 - Gyogyo
- Printed effect: None.
- Printed trigger: None.
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: No printed effect or trigger.
- Open questions/blockers: None.

### OP13-104 - Kouzuki Hiyori
- Printed effect: [Blocker]<br>[On K.O.] You may trash 1 card from your hand: If your Leader is multicolored, add up to 1 card from the top of your deck to the top of your Life cards.
- Printed trigger: None.
- Registered timings: on_ko, blocker
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-105 - Kouzuki Momonosuke
- Printed effect: [On Play] Look at all of your Life cards and place them back in your Life area in any order.
- Printed trigger: None.
- Registered timings: on_play
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-106 - Conney
- Printed effect: [Opponent's Turn] When a [Trigger] activates, this Character gains [Blocker] during this turn.
- Printed trigger: [Trigger] Play this card.
- Registered timings: blocker, trigger
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-107 - Shaka
- Printed effect: None.
- Printed trigger: None.
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: No printed effect or trigger.
- Open questions/blockers: None.

### OP13-108 - Jewelry Bonney
- Printed effect: [On Play] If your Leader has the {Egghead} type, this Character gains [Rush] during this turn. Then, your opponent adds 1 card from the top of their Life cards to their hand.
- Printed trigger: [Trigger] If you have 1 or less Life cards, rest up to 1 of your opponent's Characters with a cost of 7 or less.
- Registered timings: on_play, trigger
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-109 - Jewelry Bonney
- Printed effect: If this Character would be removed from the field by your opponent's effect, you may turn 1 card from the top of your Life cards face-up instead.
- Printed trigger: [Trigger] Draw 2 cards and trash 1 card from your hand.
- Registered timings: continuous, trigger
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-110 - Stussy
- Printed effect: [Blocker]<br>[On Play] If your Leader has the {Egghead} type, play up to 1 Character card with a cost of 5 or less and a [Trigger] from your hand.
- Printed trigger: None.
- Registered timings: on_play, blocker
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-111 - Pythagoras
- Printed effect: None.
- Printed trigger: None.
- Registered timings: None
- Implementation status: `Vanilla`
- Required code changes: No handler required.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: No printed effect or trigger.
- Open questions/blockers: None.

### OP13-112 - Vegapunk
- Printed effect: If you have a total of 2 or more given DON!! cards, this Character gains [Blocker].<br>(After your opponent declares an attack, you may rest this card to make it the new target of the attack.)
- Printed trigger: None.
- Registered timings: blocker
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-113 - Lilith
- Printed effect: [On Play] Look at 4 cards from the top of your deck; reveal up to 1 card with a [Trigger] other than [Lilith] and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: [Trigger] Activate this card's [On Play] effect.
- Registered timings: on_play, trigger
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-114 - S-Snake
- Printed effect: [On Play]/[When Attacking] You may turn 1 card from the top of your Life cards face-up: Give up to 1 of your opponent's Characters −2000 power during this turn.
- Printed trigger: [Trigger] You may trash 1 card from your hand: Play this card.
- Registered timings: on_play, on_attack, trigger
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-115 - Paper Art Afterimage
- Printed effect: [Counter] Up to 1 of your Leader or Character cards gains +3000 power during this battle. Then, if your opponent has 2 or less Life cards, up to 1 of your Leader or Character cards gains +1000 power during this turn.
- Printed trigger: [Trigger] Draw 1 card.
- Registered timings: COUNTER, trigger
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-116 - The One Who Is the Most Free Is the Pirate King!!!
- Printed effect: [Main] Look at 5 cards from the top of your deck; reveal up to 1 {Supernovas} type Character card and add it to your hand. Then, place the rest at the bottom of your deck in any order.
- Printed trigger: [Trigger] Activate this card's [Main] effect.
- Registered timings: on_play, trigger
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-117 - Gum-Gum Dawn Stamp
- Printed effect: [Main] You may turn 1 card from the top of your Life cards face-up: K.O. up to 1 of your opponent's Characters with a base cost of 6 or less.
- Printed trigger: [Trigger] Draw 1 card.
- Registered timings: on_play, trigger
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-118 - Monkey.D.Luffy
- Printed effect: [Double Attack]<br>[On Play] If your Leader is multicolored, set up to 4 of your DON!! cards as active. Then, you cannot play Character cards with a base cost of 5 or more during this turn.
- Printed trigger: None.
- Registered timings: on_play
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.

### OP13-119 - Portgas.D.Ace
- Printed effect: If you have 3 or less Life cards, this Character gains [Rush].<br>[On Play] Give up to 1 rested DON!! card to your Leader. Then, you may return up to 1 of your opponent's Characters with a cost of 5 or less to the owner's hand. If you do, your opponent plays up to 1 Character card with a cost of 4 or less from their hand.
- Printed trigger: None.
- Registered timings: CONTINUOUS, ON_PLAY
- Implementation status: `Complete`
- Required code changes: Existing/set-specific handler present; no fallback added in this pass.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: None identified in this pass.

### OP13-120 - Sabo
- Printed effect: [Blocker]<br>[Activate: Main] [Once Per Turn] Up to 1 of your Characters gains +2 cost until the end of your opponent's next turn. Then, give up to 1 rested DON!! card to your Leader.
- Printed trigger: None.
- Registered timings: activate, blocker
- Implementation status: `Partial`
- Required code changes: Registered through shared generic fallback for common printed patterns; needs bespoke implementation for exact parity review.
- Required tester setup: Standard OP13 seeded state from `card_effect_tester.py`; add bespoke board/zone seeds if this card graduates from fallback to exact implementation.
- Verification result: Registered and execution-swept without immediate exception.
- Open questions/blockers: Exact optional sequencing, named/archetype filters, costs, durations, and replacement/prevention text may require bespoke code or engine support.
