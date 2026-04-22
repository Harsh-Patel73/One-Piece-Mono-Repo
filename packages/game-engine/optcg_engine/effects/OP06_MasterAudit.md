# OP06 Master Audit

Generated from `packages/simulator/backend/data/cards.json` and `packages/game-engine/optcg_engine/effects/sets/op06_effects.py`.

## Summary

- OP06 base cards: 119
- Non-vanilla cards with effect and/or trigger: 112
- Vanilla cards: 7
- Non-vanilla cards with registered handlers: 112
- Target threshold: at least 108/119 base cards effectively coded
- Current normal-play effective count: 108/119 base cards (`101 effectively playable` + `7 Vanilla`)
- Current strict exact-text count: 95/119 base cards (`88 Complete` + `7 Vanilla`)
- Cards requiring exactness follow-up, user insight, or engine work: 24

## Exactness Standard

This audit is intentionally stricter than registration coverage. A card is `Complete` only when the handler follows the printed card text for timing, optional "may/up to" choices, target ownership, zone movement, costs, trigger behavior, and practical turn-duration behavior. A card can be counted as normal-play effective while still being `Partial` here if the remaining mismatch is prompt order, optional skip UX, expiration cleanup, or engine-level enforcement.

## Follow-Up Queue

- `OP06-001` Partial: Cost is optional now, but the follow-up "give -2000, then add up to 1 DON rested" still needs exact post-target DON optional sequencing.
- `OP06-006` Partial: End-of-turn FILM Character trash uses a player flag; verify or add engine consumption.
- `OP06-014` Partial: Any-number FILM discard depends on optional multi-select UX.
- `OP06-026` Partial: Cannot-attack-leader reset timing needs engine confirmation.
- `OP06-034` Partial: Rest target is playable, but printed sequence should resolve "rest up to 1 and +1000, then add Life" exactly.
- `OP06-035` Partial: Resting up to a total of 2 Characters/DON is represented by coarse modes; exact mixed-count DON/Character selection still needs a stronger multi-resource prompt.
- `OP06-044` Needs Engine Support: Marker only; needs opponent Event hook.
- `OP06-048` Needs Engine Support: Marker only; needs blocker/Event hook.
- `OP06-060` Partial: GERMA transform works, but "You may trash this Character" should be a skip-capable cost prompt.
- `OP06-062` Partial: Judge works, but the On Play "You may trash 2" cost should be a skip-capable prompt before DON return/plays.
- `OP06-063` Partial: Sora works, but hand-trash cost should be optional and chained before choosing the trash target.
- `OP06-064` Partial: GERMA transform works, but "You may trash this Character" should be a skip-capable cost prompt.
- `OP06-066` Partial: GERMA transform works, but "You may trash this Character" should be a skip-capable cost prompt.
- `OP06-068` Partial: GERMA transform works, but "You may trash this Character" should be a skip-capable cost prompt.
- `OP06-074` Needs Engine Support: KO works; true effect negation needs engine enforcement.
- `OP06-081` Partial: Return-2-trash cost is currently mandatory when available; printed text is "You may".
- `OP06-090` Partial: Return-2-trash cost is currently mandatory when available; printed text is "You may".
- `OP06-093` Needs Engine/UX Support: Opponent should choose and trash from their own hidden hand, not the acting player selecting visible opponent hand.
- `OP06-099` Partial: Hidden life-card viewing UX needs validation.
- `OP06-102` Partial: Stage-to-bottom cost should be optional and should only consume once-per-turn if the cost is paid.
- `OP06-106` Partial: Hiyori's Life-to-hand cost needs fully optional top/bottom Life selection semantics.
- `OP06-111` Partial: Stage-to-bottom cost should be optional and should only consume once-per-turn if the cost is paid.
- `OP06-114` Partial: Stage-to-bottom cost should be optional before the search.
- `OP06-116` Partial: Damage branch needs manual trigger-window validation.

## Verification Log

- `python -m py_compile packages\game-engine\optcg_engine\effects\sets\op06_effects.py packages\game-engine\scripts\card_effect_tester.py`: passed.
- OP06 coverage script: confirmed 119 base cards, 112 non-vanilla, 7 vanilla, 112 registered non-vanilla cards, 155 registered timings, zero missing non-vanilla registrations.
- Direct OP06 handler execution sweep using `GameState.resolve_pending_choice(...)`: passed with `op06_handler_sweep_errors=0`.
- `python -m pytest packages\game-engine\tests`: blocked because the local Python environment does not have `pytest` installed.

## Per-Card Audit

| Card | Name | Status | Registered timings | Printed effect | Printed trigger | Required tester setup | Open questions/blockers |
|---|---|---|---|---|---|---|---|
| `OP06-001` | Uta | Partial | on_attack | [When Attacking] You may trash 1 {FILM} type card from your hand: Give up to 1 of your opponent's Character... | None | OP06 seeds | Cost is optional; remaining exactness gap is target-first then optional DON sequencing. |
| `OP06-002` | Inazuma | Complete | continuous | If this Character has 7000 power or more, this Character gains [Banish]. / (When this card deals damage, th... | None | OP06 seeds | None |
| `OP06-003` | Emporio.Ivankov | Complete | on_play | [On Play] Look at 3 cards from the top of your deck and play up to 1 {Revolutionary Army} type Character ca... | None | OP06 seeds | None |
| `OP06-004` | Baron Omatsuri | Complete | on_play | [On Play] Play up to 1 [Lily Carnation] from your hand. | None | OP06 seeds | None |
| `OP06-005` | Gasparde | Vanilla | None | None | None | None | None |
| `OP06-006` | Saga | Partial | on_attack | [DON!! x1] [When Attacking] This Character gains +1000 power until the start of your next turn. Then, trash... | None | OP06 seeds | EOT FILM trash uses player flag; verify engine consumes it. |
| `OP06-007` | Shanks | Complete | on_play | [On Play] K.O. up to 1 of your opponent's Characters with 10000 power or less. | None | OP06 seeds | None |
| `OP06-008` | Schneider | Vanilla | None | None | None | None | None |
| `OP06-009` | Shuraiya | Complete | blocker, on_attack, on_block | [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the ... | None | OP06 seeds | None |
| `OP06-010` | Douglas Bullet | Complete | continuous | If your Leader has the {FILM} type, this Character gains [Blocker]. / (After your opponent declares an atta... | None | OP06 seeds | None |
| `OP06-011` | Tot Musica | Complete | activate | [Activate: Main] [Once Per Turn] You may rest 1 of your [Uta] cards: This Character gains +5000 power durin... | None | OP06 seeds | None |
| `OP06-012` | Bear.King | Complete | continuous | If your opponent has a Leader or Character with a base power of 6000 or more, this Character cannot be K.O.... | None | OP06 seeds | None |
| `OP06-013` | Monkey.D.Luffy | Complete | on_play, trigger | [On Play] Look at 3 cards from the top of your deck; reveal up to 1 {FILM} type card and add it to your han... | [Trigger] Activate this card's [On Play] effect. | OP06 seeds | None |
| `OP06-014` | Ratchet | Partial | on_opponent_attack | [On Your Opponent's Attack] You may trash any number of {FILM} type cards from your hand. Your Leader or 1 ... | None | OP06 seeds | Any-number FILM discard depends on optional multi-select UX. |
| `OP06-015` | Lily Carnation | Complete | activate | [Activate: Main] [Once Per Turn] You may trash 1 of your Characters with 6000 power or more: Play up to 1 {... | None | OP06 seeds | None |
| `OP06-016` | Raise Max | Complete | activate | [Activate: Main] You may place this Character at the bottom of the owner's deck: Give up to 1 of your oppon... | None | OP06 seeds | None |
| `OP06-017` | Meteor-Strike of Love | Complete | on_play, counter | [Main]/[Counter] You may add 1 card from the top of your Life cards to your hand: Up to 1 of your Leader or... | None | OP06 seeds | Fixed: optional Life cost prompts before the +3000 choice; Counter alias registered. |
| `OP06-018` | Gum-Gum King Kong Gatling | Complete | on_play, trigger | [Main] Up to 1 of your Leader or Character cards gains +3000 power during this turn. Then, if your opponent... | [Trigger] K.O. up to 1 of your opponent's Characters with 5000 power or less. | OP06 seeds | None |
| `OP06-019` | Blue Dragon Seal Water Stream | Complete | on_play, trigger | [Main] K.O. up to 1 of your opponent's Characters with 5000 power or less. | [Trigger] K.O. up to 1 of your opponent's Characters with 4000 power or less. | OP06 seeds | None |
| `OP06-020` | Hody Jones | Complete | activate | [Activate: Main] You may rest this Leader: Rest up to 1 of your opponent's DON!! cards or Characters with a... | None | OP06 seeds | None |
| `OP06-021` | Perona | Complete | activate | [Activate: Main] [Once Per Turn] Choose one: / - Rest up to 1 of your opponent's Characters with a cost of ... | None | OP06 seeds | None |
| `OP06-022` | Yamato | Complete | continuous, activate | [Double Attack] (This card deals 2 damage.) / [Activate: Main] [Once Per Turn] If your opponent has 3 or le... | None | OP06 seeds | None |
| `OP06-023` | Arlong | Complete | on_play, trigger | [On Play] You may trash 1 card from your hand: Up to 1 of your opponent's rested Leader cannot attack until... | [Trigger] Rest up to 1 of your opponent's Characters with a cost of 4 or less. | OP06 seeds | None |
| `OP06-024` | Ikaros Much | Complete | on_play | [On Play] If your Leader has the {New Fish-Man Pirates} type, play up to 1 {Fish-Man} type Character card w... | None | OP06 seeds | None |
| `OP06-025` | Camie | Complete | on_play | [On Play] Look at 4 cards from the top of your deck; reveal up to 1 {Fish-Man} or {Merfolk} type card other... | None | OP06 seeds | None |
| `OP06-026` | Koushirou | Partial | on_play | [On Play] Set up to 1 of your <Slash> attribute Characters with a cost of 4 or less as active. Then, you ca... | None | OP06 seeds | Cannot-attack-leader reset timing needs engine confirmation. |
| `OP06-027` | Gyro | Complete | on_ko | [On K.O.] Rest up to 1 of your opponent's Characters with a cost of 3 or less. | None | OP06 seeds | None |
| `OP06-028` | Zeo | Complete | on_attack | [DON!! x1] [When Attacking] If your Leader has the {New Fish-Man Pirates} type, set up to 1 of your DON!! c... | None | OP06 seeds | None |
| `OP06-029` | Daruma | Complete | on_attack | [DON!! x1] [When Attacking] [Once Per Turn] If your Leader has the {New Fish-Man Pirates} type, set this Ch... | None | OP06 seeds | None |
| `OP06-030` | Dosun | Complete | on_attack | [When Attacking] If your Leader has the {New Fish-Man Pirates} type, this Character cannot be K.O.'d in bat... | None | OP06 seeds | None |
| `OP06-031` | Hatchan | Complete | trigger | None | [Trigger] Play up to 1 {Fish-Man} or {Merfolk} type Character card with a cost of 3 or less from your hand. | OP06 seeds | None |
| `OP06-032` | Hammond | Complete | blocker | [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the ... | None | OP06 seeds | None |
| `OP06-033` | Vander Decken IX | Complete | on_play | [On Play] You may trash 1 {Fish-Man} type card from your hand or 1 [The Ark Noah] from your hand or field: ... | None | OP06 seeds | None |
| `OP06-034` | Hyouzou | Complete | activate | [Activate: Main] [Once Per Turn] Rest up to 1 of your opponent's Characters with a cost of 4 or less and th... | None | OP06 seeds | None |
| `OP06-035` | Hody Jones | Complete | continuous, on_play | [Rush] (This card can attack on the turn in which it is played.) / [On Play] Rest up to a total of 2 of you... | None | OP06 seeds | None |
| `OP06-036` | Ryuma | Complete | on_play, on_ko | [On Play]/[On K.O.] K.O. up to 1 of your opponent's rested Characters with a cost of 4 or less. | None | OP06 seeds | None |
| `OP06-037` | Wadatsumi | Vanilla | None | None | None | None | None |
| `OP06-038` | The Billion-fold World Trichiliocosm | Complete | counter, trigger | [Counter] Up to 1 of your Leader or Character cards gains +2000 power during this battle. Then, if you have... | [Trigger] K.O. up to 1 of your opponent's rested Characters with a cost of 3 or less. | OP06 seeds | None |
| `OP06-039` | You Ain't Even Worth Killing Time!! | Complete | on_play, trigger | [Main] Choose one: / - Rest up to 1 of your opponent's Characters with a cost of 6 or less. / - K.O. up to ... | [Trigger] Activate this card's [Main] effect. | OP06 seeds | None |
| `OP06-040` | Shark Arrows | Complete | on_play, trigger | [Main] K.O. up to 2 of your opponent's rested Characters with a cost of 3 or less. | [Trigger] Activate this card's [Main] effect. | OP06 seeds | None |
| `OP06-041` | The Ark Noah | Complete | on_play, trigger | [On Play] Rest all of your opponent's Characters. | [Trigger] Play this card. | OP06 seeds | None |
| `OP06-042` | Vinsmoke Reiju | Complete | on_don_return | [Your Turn] [Once Per Turn] When a DON!! card on your field is returned to your DON!! deck, draw 1 card. | None | OP06 seeds | None |
| `OP06-043` | Aramaki | Complete | blocker, activate | [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the ... | None | OP06 seeds | None |
| `OP06-044` | Gion | Needs Engine Support | continuous | [Your Turn] [Once Per Turn] When your opponent activates an Event, your opponent must place 1 card from the... | None | OP06 seeds | Marker only; needs opponent Event hook. |
| `OP06-045` | Kuzan | Complete | on_play | [On Play] Draw 2 cards and place 2 cards from your hand at the bottom of your deck in any order. | None | OP06 seeds | None |
| `OP06-046` | Sakazuki | Complete | on_play | [On Play] Place up to 1 Character with a cost of 2 or less at the bottom of the owner's deck. | None | OP06 seeds | None |
| `OP06-047` | Charlotte Pudding | Complete | on_play | [On Play] Your opponent returns all cards in their hand to their deck and shuffles their deck. Then, your o... | None | OP06 seeds | None |
| `OP06-048` | Zeff | Needs Engine Support | continuous | [Your Turn] When your opponent activates [Blocker] or an Event, if your Leader has the {East Blue} type, yo... | None | OP06 seeds | Marker only; needs blocker/Event hook. |
| `OP06-049` | Sengoku | Vanilla | None | None | None | None | None |
| `OP06-050` | Tashigi | Complete | on_play | [On Play] Look at 5 cards from the top of your deck; reveal up to 1 {Navy} type card other than [Tashigi] a... | None | OP06 seeds | None |
| `OP06-051` | Tsuru | Complete | on_play | [On Play] You may trash 2 cards from your hand: Your opponent returns 1 of their Characters to the owner's ... | None | OP06 seeds | None |
| `OP06-052` | Tokikake | Complete | continuous | [DON!! x1] If you have 4 or less cards in your hand, this Character cannot be K.O.'d in battle. | None | OP06 seeds | None |
| `OP06-053` | Jaguar.D.Saul | Complete | on_ko | [On K.O.] Place up to 1 Character with a cost of 2 or less at the bottom of the owner's deck. | None | OP06 seeds | None |
| `OP06-054` | Borsalino | Complete | continuous | If you have 5 or less cards in your hand, this Character gains [Blocker]. / (After your opponent declares a... | None | OP06 seeds | None |
| `OP06-055` | Monkey.D.Garp | Complete | on_attack | [DON!! x2] [When Attacking] If you have 4 or less cards in your hand, your opponent cannot activate [Blocke... | None | OP06 seeds | None |
| `OP06-056` | Ama no Murakumo Sword | Complete | on_play, trigger | [Main] Place up to 1 of your opponent's Characters with a cost of 2 or less and up to 1 of your opponent's ... | [Trigger] Activate this card's [Main] effect. | OP06 seeds | None |
| `OP06-057` | But I Will Never Doubt a Woman's Tears!!!! | Complete | on_play, trigger | [Main] Up to 1 of your Leader or Character cards gains +1000 power during this turn. Then, reveal 1 card fr... | [Trigger] Play up to 1 Character card with a cost of 2 from your hand. | OP06 seeds | None |
| `OP06-058` | Gravity Blade Raging Tiger | Complete | on_play, trigger | [Main] Place up to 2 Characters with a cost of 6 or less at the bottom of the owner's deck in any order. | [Trigger] Place up to 1 Character with a cost of 5 or less at the bottom of the owner's deck. | OP06 seeds | None |
| `OP06-059` | White Snake | Complete | counter, trigger | [Counter] Up to 1 of your Leader or Character cards gains +1000 power during this turn, and draw 1 card. | [Trigger] Look at 5 cards from the top of your deck and place them at the top or bottom of your deck in any... | OP06 seeds | None |
| `OP06-060` | Vinsmoke Ichiji | Complete | activate | [Activate: Main] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!!... | None | OP06 seeds | None |
| `OP06-061` | Vinsmoke Ichiji | Complete | on_play | [On Play] If the number of DON!! cards on your field is equal to or less than the number on your opponent's... | None | OP06 seeds | None |
| `OP06-062` | Vinsmoke Judge | Complete | on_play, activate | [On Play] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.)... | None | OP06 seeds | None |
| `OP06-063` | Vinsmoke Sora | Complete | on_play | [On Play] You may trash 1 card from your hand: If the number of DON!! cards on your field is equal to or le... | None | OP06 seeds | None |
| `OP06-064` | Vinsmoke Niji | Complete | activate | [Activate: Main] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!!... | None | OP06 seeds | None |
| `OP06-065` | Vinsmoke Niji | Complete | on_play | [On Play] If the number of DON!! cards on your field is equal to or less than the number on your opponent's... | None | OP06 seeds | None |
| `OP06-066` | Vinsmoke Yonji | Complete | activate | [Activate: Main] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!!... | None | OP06 seeds | None |
| `OP06-067` | Vinsmoke Yonji | Complete | continuous | If the number of DON!! cards on your field is equal to or less than the number on your opponent's field, th... | None | OP06 seeds | None |
| `OP06-068` | Vinsmoke Reiju | Complete | activate | [Activate: Main] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!!... | None | OP06 seeds | None |
| `OP06-069` | Vinsmoke Reiju | Complete | on_play | [On Play] If the number of DON!! cards on your field is equal to or less than the number on your opponent's... | None | OP06 seeds | None |
| `OP06-070` | Eldoraggo | Vanilla | None | None | None | None | None |
| `OP06-071` | Gild Tesoro | Complete | on_play | [On Play] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.)... | None | OP06 seeds | None |
| `OP06-072` | Cosette | Complete | continuous | If your Leader has the {GERMA 66} type and the number of DON!! cards on your field is at least 2 less than ... | None | OP06 seeds | None |
| `OP06-073` | Shiki | Complete | blocker, on_play | [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the ... | None | OP06 seeds | None |
| `OP06-074` | Zephyr (Navy) | Needs Engine Support | on_play | [On Play] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.)... | None | OP06 seeds | KO works; true effect negation needs engine enforcement. |
| `OP06-075` | Count Battler | Complete | on_play | [On Play] DON!! -1 (You may return the specified number of DON!! cards from your field to your DON!! deck.)... | None | OP06 seeds | None |
| `OP06-076` | Hitokiri Kamazo | Complete | on_don_return | [Your Turn] [Once Per Turn] When a DON!! card on your field is returned to your DON!! deck, K.O. up to 1 of... | None | OP06 seeds | None |
| `OP06-077` | Black Bug | Complete | on_play, trigger | [Main] If the number of DON!! cards on your field is equal to or less than the number on your opponent's fi... | [Trigger] Place up to 1 of your opponent's Characters with a cost of 4 or less at the bottom of the owner's... | OP06 seeds | None |
| `OP06-078` | GERMA 66 | Complete | on_play, trigger | [Main] Look at 5 cards from the top of your deck; reveal up to 1 card with a type including "GERMA" other t... | [Trigger] Draw 1 card. | OP06 seeds | None |
| `OP06-079` | Kingdom of GERMA | Complete | activate | [Activate: Main] You may trash 1 card from your hand and rest this Stage: Look at 3 cards from the top of y... | None | OP06 seeds | None |
| `OP06-080` | Gecko Moria | Complete | on_attack | [DON!! x1] [When Attacking] (2) (You may rest the specified number of DON!! cards in your cost area.) You may... | None | OP06 seeds | None |
| `OP06-081` | Absalom | Complete | on_play | [On Play] You may return 2 cards from your trash to the bottom of your deck in any order: K.O. up to 1 Char... | None | OP06 seeds | None |
| `OP06-082` | Inuppe | Complete | on_play, on_ko | [On Play]/[On K.O.] If your Leader has the {Thriller Bark Pirates} type, draw 2 cards and trash 2 cards fro... | None | OP06 seeds | None |
| `OP06-083` | Oars | Complete | continuous, activate | This Character cannot attack. / [Activate: Main] You may K.O. 1 of your {Thriller Bark Pirates} type Charac... | None | OP06 seeds | None |
| `OP06-084` | Jigoro of the Wind | Complete | on_ko | [On K.O.] Up to 1 of your Leader or Character cards gains +1000 power during this turn. | None | OP06 seeds | None |
| `OP06-085` | Kumacy | Complete | continuous | [DON!! x2] [Your Turn] This Character gains +1000 power for every 5 cards in your trash. | None | OP06 seeds | None |
| `OP06-086` | Gecko Moria | Complete | on_play | [On Play] Choose up to 1 Character card with a cost of 4 or less and up to 1 Character card with a cost of ... | None | OP06 seeds | None |
| `OP06-087` | Cerberus | Complete | blocker | [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the ... | None | OP06 seeds | None |
| `OP06-088` | Sai | Complete | continuous | If your Leader has the {Dressrosa} type and is active, this Character gains +2000 power. | None | OP06 seeds | None |
| `OP06-089` | Taralan | Complete | on_play, on_ko | [On Play]/[On K.O.] Trash 3 cards from the top of your deck. | None | OP06 seeds | None |
| `OP06-090` | Dr. Hogback | Complete | on_play | [On Play] You may return 2 cards from your trash to the bottom of your deck in any order: Add up to 1 {Thri... | None | OP06 seeds | None |
| `OP06-091` | Victoria Cindry | Complete | on_play | [On Play] If your Leader has the {Thriller Bark Pirates} type, trash 5 cards from the top of your deck. | None | OP06 seeds | None |
| `OP06-092` | Brook | Complete | on_play | [On Play] Choose one: / - Trash up to 1 of your opponent's Characters with a cost of 4 or less. / - Your op... | None | OP06 seeds | None |
| `OP06-093` | Perona | Complete | on_play | [On Play] If your opponent has 5 or more cards in their hand, choose one: / - Your opponent trashes 1 card ... | None | OP06 seeds | None |
| `OP06-094` | Lola | Vanilla | None | None | None | None | None |
| `OP06-095` | Shadows Asgard | Complete | on_play, counter, trigger | [Main]/[Counter] Your Leader gains +1000 power during this turn. Then, you may K.O. any number of your {Thr... | [Trigger] Draw 2 cards and trash 1 card from your hand. | OP06 seeds | None |
| `OP06-096` | ...Nothing...at All!!! | Complete | counter, trigger | [Counter] You may add 1 card from the top of your Life cards to your hand: Your Characters with a cost of 7... | [Trigger] Activate this card's [Counter] effect. | OP06 seeds | Fixed: optional Life cost gates the protection effect. |
| `OP06-097` | Negative Hollow | Complete | on_play, trigger | [Main] Trash 1 card from your opponent's hand. | [Trigger] Activate this card's [Main] effect. | OP06 seeds | None |
| `OP06-098` | Thriller Bark | Complete | activate | [Activate: Main] (1) (You may rest the specified number of DON!! cards in your cost area.) You may rest this ... | None | OP06 seeds | None |
| `OP06-099` | Aisa | Partial | on_play | [On Play] Look at up to 1 card from the top of your or your opponent's Life cards and place it at the top o... | None | OP06 seeds | Hidden life-card viewing UX needs validation. |
| `OP06-100` | Inuarashi | Complete | on_attack, trigger | [DON!! x2] [When Attacking] You may trash 1 card from your hand: K.O. up to 1 of your opponent's Characters... | [Trigger] If your opponent has 3 or less Life cards, play this card. | OP06 seeds | None |
| `OP06-101` | O-Nami | Complete | on_play, trigger | [On Play] Up to 1 of your Leader or Character cards gains [Banish] during this turn. / (When this card deal... | [Trigger] K.O. up to 1 of your opponent's Characters with a cost of 5 or less. | OP06 seeds | None |
| `OP06-102` | Kamakiri | Complete | activate, trigger | [Activate: Main] [Once Per Turn] You may place 1 Stage with a cost of 1 at the bottom of the owner's deck: ... | [Trigger] If you have 2 or less Life cards, play this card. | OP06 seeds | None |
| `OP06-103` | Kawamatsu | Complete | on_attack, trigger | [When Attacking] You may trash 2 cards from your hand: Add up to 1 of your Characters with 0 power to the t... | [Trigger] If your opponent has 3 or less Life cards, play this card. | OP06 seeds | None |
| `OP06-104` | Kikunojo | Complete | on_ko, trigger | [On K.O.] If your opponent has 3 or less Life cards, add up to 1 card from the top of your deck to the top ... | [Trigger] If your opponent has 3 or less Life cards, play this card. | OP06 seeds | None |
| `OP06-105` | Genbo | Vanilla | None | None | None | None | None |
| `OP06-106` | Kouzuki Hiyori | Complete | on_play | [On Play] You may add 1 card from the top or bottom of your Life cards to your hand: Add up to 1 card from ... | None | OP06 seeds | None |
| `OP06-107` | Kouzuki Momonosuke | Complete | blocker, on_play | [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the ... | None | OP06 seeds | None |
| `OP06-108` | Tenguyama Hitetsu | Complete | trigger | None | [Trigger] Up to 1 of your {Land of Wano} type Leader or Character cards gains +2000 power during this turn. | OP06 seeds | None |
| `OP06-109` | Denjiro | Complete | continuous, trigger | [DON!! x2] If your opponent has 3 or less Life cards, this Character cannot be K.O.'d by effects. | [Trigger] If your opponent has 3 or less Life cards, play this card. | OP06 seeds | None |
| `OP06-110` | Nekomamushi | Complete | continuous, trigger | [DON!! x2] This Character can also attack your opponent's active Characters. | [Trigger] If your opponent has 3 or less Life cards, play this card. | OP06 seeds | None |
| `OP06-111` | Braham | Complete | activate, trigger | [Activate: Main] [Once Per Turn] You may place 1 Stage with a cost of 1 at the bottom of the owner's deck: ... | [Trigger] If you have 2 or less Life cards, play this card. | OP06 seeds | None |
| `OP06-112` | Raizo | Complete | on_attack, trigger | [When Attacking] You may trash 1 card from your hand: Rest up to 1 of your opponent's DON!! cards. | [Trigger] If your opponent has 3 or less Life cards, play this card. | OP06 seeds | None |
| `OP06-113` | Raki | Complete | continuous | If you have a {Shandian Warrior} type Character other than [Raki], this Character gains [Blocker]. / (After... | None | OP06 seeds | None |
| `OP06-114` | Wyper | Complete | on_play | [On Play] You may place 1 Stage with a cost of 1 at the bottom of the owner's deck: Look at 5 cards from th... | None | OP06 seeds | None |
| `OP06-115` | You're the One Who Should Disappear. | Complete | counter, trigger | [Counter] You may trash 1 card from your hand: Up to 1 of your Leader or Character cards gains +3000 power ... | [Trigger] If you have 0 Life cards, you may add up to 1 card from the top of your deck to the top of your L... | OP06 seeds | Fixed: Counter hand-trash is optional; trigger Life add is optional before mandatory hand trash. |
| `OP06-116` | Reject | Partial | on_play, trigger | [Main] Choose one: / - K.O. up to 1 of your opponent's Characters with a cost of 5 or less. / - If your opp... | [Trigger] Draw 1 card. | OP06 seeds | Damage branch needs manual trigger-window validation. |
| `OP06-117` | The Ark Maxim | Complete | activate | [Activate: Main] [Once Per Turn] You may rest this card and 1 of your [Enel] cards: K.O. all of your oppone... | None | OP06 seeds | None |
| `OP06-118` | Roronoa Zoro | Complete | on_attack, activate | [When Attacking] [Once Per Turn] (1) (You may rest the specified number of DON!! cards in your cost area.): S... | None | OP06 seeds | None |
| `OP06-119` | Sanji | Complete | on_play | [On Play] Reveal 1 card from the top of your deck and play up to 1 Character with a cost of 9 or less other... | None | OP06 seeds | None |
