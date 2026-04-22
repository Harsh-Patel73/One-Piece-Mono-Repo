# OP01 Master Audit

Generated from `packages/simulator/backend/data/cards.json` and `packages/game-engine/optcg_engine/effects/sets/op01_effects.py`.

## Summary

- OP01 base cards: 121
- Non-vanilla cards with effect and/or trigger: 105
- Vanilla cards: 16
- Non-vanilla cards with registered handlers: 106
- Missing printed trigger timings: 0
- Current strict exact-text count: 101/121 base cards (`85 Complete` + `16 Vanilla`)
- Cards requiring exactness follow-up, user insight, or engine work: 20

## Exactness Standard

A card is `Complete` only when this pass found the printed timing, optional costs, target ownership, zone movement, trigger text, and practical duration behavior represented in `op01_effects.py`. `Partial` cards are playable or covered but still have a known exact-text or engine/UX gap.

## Follow-Up Queue

- `OP01-001` Partial: Continuous power may stack if engine reapplies without clearing modifiers.
- `OP01-003` Partial: Set-active target is still mandatory when a valid rested target exists; printed text says up to 1.
- `OP01-008` Partial: Optional Life cost now prompts, but prompt is represented as selecting Cavendish rather than a dedicated Life-cost UX.
- `OP01-013` Partial: Life cost is auto-paid and rested DON attachment needs exact attached-DON movement/choice.
- `OP01-024` Partial: Activate attaches up to 2 rested DON automatically; exact choice/skip UX should be validated.
- `OP01-031` Partial: Trash cost is required once activated; acceptable in play, but exact optional activation/once flag on skip needs validation.
- `OP01-038` Partial: On K.O. opponent should choose from hidden hand; current UX needs hidden-info ownership validation.
- `OP01-047` Partial: Return-own-character cost needs optional skip and should gate the play choice exactly.
- `OP01-063` Partial: Opponent-hand reveal and opponent-Life choice are approximated/randomized; needs hidden-info choice support.
- `OP01-085` Partial: Cannot-attack duration until end of opponent next turn needs engine reset validation.
- `OP01-094` Partial: DON -6 is optional cost; current flow needs exact yes/no cost prompt and all-character KO validation.
- `OP01-096` Partial: DON -2 optional cost and two independent KO targets need exact target sequencing validation.
- `OP01-097` Partial: DON -1 optional cost should gate Rush and power reduction exactly.
- `OP01-102` Partial: Opponent should trash 1 from their own hidden hand; current hidden-hand UX needs validation.
- `OP01-105` Partial: Opponent hand reveal should be hidden-info compliant.
- `OP01-108` Partial: DON -1 optional cost should gate KO with exact skip semantics.
- `OP01-112` Partial: DON -1 optional cost/once-per-turn skip semantics need validation.
- `OP01-114` Partial: Opponent should trash 1 from their own hidden hand; current flow random/prompts via acting side.
- `OP01-118` Partial: Counter resolves draw before power in current callback; printed text is power then draw.
- `OP01-121` Partial: Name alias support depends on engine consumers checking also_named.

## Verification Log

- `python -m py_compile packages\game-engine\optcg_engine\effects\sets\op01_effects.py`: passed.
- OP01 coverage script: confirmed 121 base cards, 105 non-vanilla, 16 vanilla, zero missing non-vanilla registrations, zero missing printed trigger timings, 140 registered timings.
- Direct OP01 handler execution sweep using `GameState.resolve_pending_choice(...)`: passed with `OP01_handler_sweep_errors=0`.
- `python -m pytest packages\game-engine\tests`: not rerun in this OP01 sub-pass; previous run was blocked because `pytest` is not installed.

## Per-Card Audit

| Card | Name | Status | Registered timings | Printed effect | Printed trigger | Required tester setup | Open questions/blockers |
|---|---|---|---|---|---|---|---|
| `OP01-001` | Roronoa Zoro | Partial | continuous | [DON!! x1] [Your Turn] All of your Characters gain +1000 power. | None | OP01 seeds | Continuous power may stack if engine reapplies without clearing modifiers. |
| `OP01-002` | Trafalgar Law | Complete | activate | [Activate: Main] [Once Per Turn] ➁ (You may rest the specified number of DON!! cards in your cost area.): If you have 5 Charact... | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-003` | Monkey.D.Luffy | Partial | activate | [Activate: Main] [Once Per Turn] ➃ (You may rest the specified number of DON!! cards in your cost area.): Set up to 1 of your {... | None | OP01 seeds | Set-active target is still mandatory when a valid rested target exists; printed text says up to 1. |
| `OP01-004` | Usopp | Complete | on_event_activated | [DON!! x1] [Your Turn] [Once Per Turn] Draw 1 card when your opponent activates an Event. | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-005` | Uta | Complete | on_play | [On Play] Add up to 1 red Character card other than [Uta] with a cost of 3 or less from your trash to your hand. | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-006` | Otama | Complete | on_play | [On Play] Give up to 1 of your opponent's Characters −2000 power during this turn. | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-007` | Caribou | Complete | on_ko | [On K.O.] K.O. up to 1 of your opponent's Characters with 4000 power or less. | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-008` | Cavendish | Partial | on_play | [On Play] You may add 1 card from your Life area to your hand: This Character gains [Rush] during this turn. (This card can att... | None | OP01 seeds | Optional Life cost now prompts, but prompt is represented as selecting Cavendish rather than a dedicated Life-cost UX. |
| `OP01-009` | Carrot | Complete | trigger | [Trigger] Play this card. | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-010` | Komachiyo | Vanilla | None | None | None | OP01 seeds | No handler required. |
| `OP01-011` | Gordon | Complete | on_play | [On Play] You may place 1 card from your hand at the bottom of your deck: Draw 1 card. | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-012` | Sai | Vanilla | None | None | None | OP01 seeds | No handler required. |
| `OP01-013` | Sanji | Partial | activate | [Activate: Main] [Once Per Turn] You may add 1 card from your Life area to your hand: This Character gains +2000 power during t... | None | OP01 seeds | Life cost is auto-paid and rested DON attachment needs exact attached-DON movement/choice. |
| `OP01-014` | Jinbe | Complete | blocker, on_block | [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) / [DON!! x1... | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-015` | Tony Tony.Chopper | Complete | on_attack | [DON!! x1] [When Attacking] You may trash 1 card from your hand: Add up to 1 {Straw Hat Crew} type Character card other than [T... | None | OP01 seeds | Fixed: optional trash cost now gates trash-to-hand payoff. |
| `OP01-016` | Nami | Complete | on_play | [On Play] Look at 5 cards from the top of your deck; reveal up to 1 {Straw Hat Crew} type card other than [Nami] and add it to ... | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-017` | Nico Robin | Complete | on_attack | [DON!! x1] [When Attacking] K.O. up to 1 of your opponent's Characters with 3000 power or less. | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-018` | Hajrudin | Vanilla | None | None | None | OP01 seeds | No handler required. |
| `OP01-019` | Bartolomeo | Complete | blocker, continuous | [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) / [DON!! x2... | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-020` | Hyogoro | Complete | activate | [Activate: Main] You may rest this Character: Up to 1 of your Leader or Character cards gains +2000 power during this turn. | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-021` | Franky | Complete | continuous | [DON!! x1] This Character can also attack your opponent's active Characters. | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-022` | Brook | Complete | on_attack | [DON!! x1] [When Attacking] Give up to 2 of your opponent's Characters −2000 power during this turn. | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-023` | Marco | Vanilla | None | None | None | OP01 seeds | No handler required. |
| `OP01-024` | Monkey.D.Luffy | Partial | continuous, activate | [DON!! x2] This Character cannot be K.O.'d in battle by ＜Strike＞ attribute Characters. / [Activate: Main] [Once Per Turn] Give ... | None | OP01 seeds | Activate attaches up to 2 rested DON automatically; exact choice/skip UX should be validated. |
| `OP01-025` | Roronoa Zoro | Complete | continuous | [Rush] (This card can attack on the turn in which it is played.) | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-026` | Gum-Gum Fire-Fist Pistol Red Hawk | Complete | counter, trigger | [Counter] Up to 1 of your Leader or Character cards gains +4000 power during this battle. Then, K.O. up to 1 of your opponent's... | [Trigger] Give up to 1 of your opponent's Leader or Character cards −10000 power during this turn. | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-027` | Round Table | Complete | on_play | [Main] Give up to 1 of your opponent's Characters −10000 power during this turn. | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-028` | Green Star Rafflesia | Complete | counter, trigger | [Counter] Give up to 1 of your opponent's Leader or Character cards −2000 power during this turn. | [Trigger] Activate this card's [Counter] effect. | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-029` | Radical Beam!! | Complete | counter, trigger | [Counter] Up to 1 of your Leader or Character cards gains +2000 power during this battle. Then, if you have 2 or less Life card... | [Trigger] Up to 1 of your Leader or Character cards gains +1000 power during this turn. | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-030` | In Two Years!! At the Sabaody Archipelago!! | Complete | on_play, trigger | [Main] Look at 5 cards from the top of your deck; reveal up to 1 {Straw Hat Crew} type Character card and add it to your hand. ... | [Trigger] Activate this card's [Main] effect. | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-031` | Kouzuki Oden | Partial | activate | [Activate: Main] [Once Per Turn] You can trash 1 {Land of Wano} type card from your hand: Set up to 2 of your DON!! cards as ac... | None | OP01 seeds | Trash cost is required once activated; acceptable in play, but exact optional activation/once flag on skip needs validation. |
| `OP01-032` | Ashura Doji | Complete | continuous | [DON!! x1] If your opponent has 2 or more rested Characters, this Character gains +2000 power. | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-033` | Izo | Complete | on_play | [On Play] Rest up to 1 of your opponent's Characters with a cost of 4 or less. | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-034` | Inuarashi | Complete | on_attack | [DON!! x2] [When Attacking] Set up to 1 of your DON!! cards as active. | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-035` | Okiku | Complete | on_attack | [DON!! x1] [When Attacking] [Once Per Turn] Rest up to 1 of your opponent's Characters with a cost of 5 or less. | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-036` | Otsuru | Vanilla | None | None | None | OP01 seeds | No handler required. |
| `OP01-037` | Kawamatsu | Complete | trigger | None | [Trigger] Play this card. | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-038` | Kanjuro | Partial | on_attack, on_ko | [DON!! x1] [When Attacking] K.O. up to 1 of your opponent's rested Characters with a cost of 2 or less. / [On K.O.] Your oppone... | None | OP01 seeds | On K.O. opponent should choose from hidden hand; current UX needs hidden-info ownership validation. |
| `OP01-039` | Killer | Complete | blocker, on_block | [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) / [DON!! x1... | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-040` | Kin'emon | Complete | on_play, on_attack | [On Play] If your Leader is [Kouzuki Oden], play up to 1 {The Akazaya Nine} type Character card with a cost of 3 or less from y... | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-041` | Kouzuki Momonosuke | Complete | activate | [Activate: Main] ➀ (You may rest the specified number of DON!! cards in your cost area) You may rest this Character: Look at 5 ... | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-042` | Komurasaki | Complete | on_play | [On Play] ③ (You may rest the specified number of DON!! cards in your cost area.): If your Leader is [Kouzuki Oden], set up to ... | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-043` | Shinobu | Vanilla | None | None | None | OP01 seeds | No handler required. |
| `OP01-044` | Shachi | Complete | blocker, on_play | [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) / [On Play]... | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-045` | Jean Bart | Vanilla | None | None | None | OP01 seeds | No handler required. |
| `OP01-046` | Denjiro | Complete | on_attack | [DON!! x1] [When Attacking] If your Leader is [Kouzuki Oden], set up to 2 of your DON!! cards as active. | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-047` | Trafalgar Law | Partial | blocker, on_play | [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) / [On Play]... | None | OP01 seeds | Return-own-character cost needs optional skip and should gate the play choice exactly. |
| `OP01-048` | Nekomamushi | Complete | on_play | [On Play] Rest up to 1 of your opponent's Characters with a cost of 3 or less. | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-049` | Bepo | Complete | on_attack | [DON!! x1] [When Attacking] Play up to 1 {Heart Pirates} type Character card other than [Bepo] with a cost of 4 or less from yo... | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-050` | Penguin | Complete | blocker, on_play | [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) / [On Play]... | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-051` | Eustass"Captain"Kid | Complete | continuous, activate | [DON!! x1] [Opponent's Turn] If this Character is rested, your opponent cannot attack any card other than the Character [Eustas... | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-052` | Raizo | Complete | on_attack | [When Attacking] [Once Per Turn] If you have 2 or more rested Characters, draw 1 card. | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-053` | Wire | Vanilla | None | None | None | OP01 seeds | No handler required. |
| `OP01-054` | X.Drake | Complete | on_play | [On Play] K.O. up to 1 of your opponent's rested Characters with a cost of 4 or less. | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-055` | You Can Be My Samurai!! | Complete | on_play | [Main] You may rest 2 of your Characters: Draw 2 cards. | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-056` | Demon Face | Complete | on_play | [Main] K.O. up to 2 of your opponent's rested Characters with a cost of 5 or less. | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-057` | Paradise Waterfall | Complete | counter, trigger | [Counter] Up to 1 of your Leader or Character cards gains +2000 power during this battle. Then, set up to 1 of your Characters ... | [Trigger] K.O. up to 1 of your opponent's rested Characters with a cost of 4 or less. | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-058` | Punk Gibson | Complete | counter, trigger | [Counter] Up to 1 of your Leader or Character cards gains +4000 power during this battle. Then, rest up to 1 of your opponent's... | [Trigger] Rest up to 1 of your opponent's Characters. | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-059` | BE-BENG!! | Complete | on_play | [Main] You may trash 1 {Land of Wano} type card from your hand: Set up to 1 of your {Land of Wano} type Character cards with a ... | None | OP01 seeds | Fixed: optional Wano trash now gates set-active payoff. |
| `OP01-060` | Donquixote Doflamingo | Complete | on_attack | [DON!! x2] [When Attacking] ➀ (You may rest the specified number of DON!! cards in your cost area.): Reveal 1 card from the top... | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-061` | Kaido | Complete | on_opponent_ko | [DON!! x1] [Your Turn] [Once Per Turn] When your opponent's Character is K.O.'d, add up to 1 DON!! card from your DON!! deck an... | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-062` | Crocodile | Complete | on_event | [DON!! x1] When you activate an Event, you may draw 1 card if you have 4 or less cards in your hand and haven't drawn a card us... | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-063` | Arlong | Partial | activate | [DON!! x1] [Activate: Main] You may rest this Character: Choose 1 card from your opponent's hand; your opponent reveals that ca... | None | OP01 seeds | Opponent-hand reveal and opponent-Life choice are approximated/randomized; needs hidden-info choice support. |
| `OP01-064` | Alvida | Complete | on_attack | [DON!! x1] [When Attacking] You may trash 1 card from your hand: Return up to 1 of your opponent's Characters with a cost of 3 ... | None | OP01 seeds | Fixed: optional trash cost now gates return-to-hand payoff. |
| `OP01-065` | Vergo | Vanilla | None | None | None | OP01 seeds | No handler required. |
| `OP01-066` | Krieg | Vanilla | None | None | None | OP01 seeds | No handler required. |
| `OP01-067` | Crocodile | Complete | continuous | [Banish] (When this card deals damage, the target card is trashed without activating its Trigger.) / [DON!! x1] Give blue Event... | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-068` | Gecko Moria | Complete | continuous | [Your Turn] This Character gains [Double Attack] if you have 5 or more cards in your hand. / (This card deals 2 damage.) | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-069` | Caesar Clown | Complete | on_ko | [On K.O.] Play up to 1 [Smiley] from your deck, then shuffle your deck. | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-070` | Dracule Mihawk | Complete | on_play | [On Play] Place up to 1 Character with a cost of 7 or less at the bottom of the owner's deck. | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-071` | Jinbe | Complete | on_play, trigger | [On Play] Place up to 1 Character with a cost of 3 or less at the bottom of the owner's deck. | [Trigger] Play this card. | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-072` | Smiley | Complete | continuous | [DON!! x1] [Your Turn] This Character gains +1000 power for every card in your hand. | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-073` | Donquixote Doflamingo | Complete | blocker, on_play | [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) / [On Play]... | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-074` | Bartholomew Kuma | Complete | blocker, on_ko | [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) / [On K.O.]... | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-075` | Pacifista | Complete | blocker | Under the rules of this game, you may have any number of this card in your deck. / [Blocker] (After your opponent declares an a... | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-076` | Bellamy | Vanilla | None | None | None | OP01 seeds | No handler required. |
| `OP01-077` | Perona | Complete | on_play | [On Play] Look at 5 cards from the top of your deck and place them at the top or bottom of the deck in any order. | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-078` | Boa Hancock | Complete | blocker, on_attack, on_block | [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) / [DON!! x1... | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-079` | Ms. All Sunday | Complete | blocker, on_ko, on_block | [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) / [On K.O.]... | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-080` | Miss Doublefinger(Zala) | Complete | on_ko | [On K.O.] Draw 1 card. | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-081` | Mocha | Vanilla | None | None | None | OP01 seeds | No handler required. |
| `OP01-082` | Monet | Complete | trigger | None | [Trigger] Play this card. | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-083` | Mr.1(Daz.Bonez) | Complete | continuous | [DON!! x1] [Your Turn] If your Leader has the {Baroque Works} type, this Character gains +1000 power for every 2 Events in your... | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-084` | Mr.2.Bon.Kurei(Bentham) | Complete | on_attack | [DON!! x1] [When Attacking] Look at 5 cards from the top of your deck; reveal up to 1 {Baroque Works} type Event card and add i... | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-085` | Mr.3(Galdino) | Partial | on_play | [On Play] If your Leader has the {Baroque Works} type, select up to 1 of your opponent's Characters with a cost of 4 or less. T... | None | OP01 seeds | Cannot-attack duration until end of opponent next turn needs engine reset validation. |
| `OP01-086` | Overheat | Complete | counter, trigger | [Counter] Up to 1 of your Leader or Character cards gains +4000 power during this battle. Then, return up to 1 active Character... | [Trigger] Return up to 1 Character with a cost of 4 or less to the owner's hand. | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-087` | Officer Agents | Complete | counter, trigger | [Counter] Play up to 1 {Baroque Works} type Character card with a cost of 3 or less from your hand. | [Trigger] Activate this card's [Counter] effect. | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-088` | Desert Spada | Complete | counter, trigger | [Counter] Up to 1 of your Leader or Character cards gains +2000 power during this battle. Then, look at 3 cards from the top of... | [Trigger] Draw 2 cards and trash 1 card from your hand. | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-089` | Crescent Cutlass | Complete | counter | [Counter] If your Leader has the {The Seven Warlords of the Sea} type, return up to 1 Character with a cost of 5 or less to the... | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-090` | Baroque Works | Complete | on_play | [Main] Look at 5 cards from the top of your deck; reveal up to 1 {Baroque Works} type card other than [Baroque Works] and add i... | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-091` | King | Complete | continuous | [Your Turn] If you have 10 DON!! cards on your field, give all of your opponent's Characters −1000 power. | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-092` | Urashima | Vanilla | on_play | None | None | OP01 seeds | No handler required. |
| `OP01-093` | Ulti | Complete | on_play | [On Play] ① (You may rest the specified number of DON!! cards in your cost area.): Add up to 1 DON!! card from your DON!! deck ... | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-094` | Kaido | Partial | on_play | [On Play] DON!! −6 (You may return the specified number of DON!! cards from your field to your DON!! deck.): If your Leader has... | None | OP01 seeds | DON -6 is optional cost; current flow needs exact yes/no cost prompt and all-character KO validation. |
| `OP01-095` | Kyoshirou | Complete | on_play | [On Play] Draw 1 card if you have 8 or more DON!! cards on your field. | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-096` | King | Partial | on_play | [On Play] DON!! −2 (You may return the specified number of DON!! cards from your field to your DON!! deck.): K.O. up to 1 of yo... | None | OP01 seeds | DON -2 optional cost and two independent KO targets need exact target sequencing validation. |
| `OP01-097` | Queen | Partial | on_play | [On Play] DON!! −1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): This Character gai... | None | OP01 seeds | DON -1 optional cost should gate Rush and power reduction exactly. |
| `OP01-098` | Kurozumi Orochi | Complete | on_play | [On Play] Reveal up to 1 [Artificial Devil Fruit SMILE] from your deck and add it to your hand. Then, shuffle your deck. | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-099` | Kurozumi Semimaru | Complete | continuous | {Kurozumi Clan} type Characters other than your [Kurozumi Semimaru] cannot be K.O.'d in battle. | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-100` | Kurozumi Higurashi | Complete | blocker | [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) | None | OP01 seeds | Fixed: corrected to Blocker timing instead of unrelated Vivi attack effect. |
| `OP01-101` | Sasaki | Complete | on_attack | [DON!! x1] [When Attacking] You may trash 1 card from your hand: Add up to 1 DON!! card from your DON!! deck and rest it. | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-102` | Jack | Partial | on_attack | [When Attacking] DON!! −1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Your oppone... | None | OP01 seeds | Opponent should trash 1 from their own hidden hand; current hidden-hand UX needs validation. |
| `OP01-103` | Scratchmen Apoo | Vanilla | None | None | None | OP01 seeds | No handler required. |
| `OP01-104` | Speed | Complete | blocker, trigger | None | [Trigger] Play this card. | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-105` | Bao Huang | Partial | on_play | [On Play] Choose 2 cards from your opponent's hand; your opponent reveals those cards. | None | OP01 seeds | Opponent hand reveal should be hidden-info compliant. |
| `OP01-106` | Basil Hawkins | Complete | on_play, trigger | [On Play] Add up to 1 DON!! card from your DON!! deck and rest it. | [Trigger] Play this card. | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-107` | Babanuki | Vanilla | None | None | None | OP01 seeds | No handler required. |
| `OP01-108` | Hitokiri Kamazo | Partial | on_ko | [On K.O.] DON!! −1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): K.O. up to 1 of yo... | None | OP01 seeds | DON -1 optional cost should gate KO with exact skip semantics. |
| `OP01-109` | Who's.Who | Complete | blocker, continuous | [DON!! x1] [Your Turn] If you have 8 or more DON!! cards on your field, this Character gains +1000 power. | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-110` | Fukurokuju | Vanilla | None | None | None | OP01 seeds | No handler required. |
| `OP01-111` | Black Maria | Complete | blocker, on_block | [Blocker] (After your opponent declares an attack, you may rest this card to make it the new target of the attack.) / [On Block... | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-112` | Page One | Partial | activate | [Activate: Main] [Once Per Turn] DON!! −1 (You may return the specified number of DON!! cards from your field to your DON!! dec... | None | OP01 seeds | DON -1 optional cost/once-per-turn skip semantics need validation. |
| `OP01-113` | Holedem | Complete | on_ko | [On K.O.] Add up to 1 DON!! card from your DON!! deck and rest it. | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-114` | X.Drake | Partial | on_play | [On Play] DON!! −1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Your opponent tras... | None | OP01 seeds | Opponent should trash 1 from their own hidden hand; current flow random/prompts via acting side. |
| `OP01-115` | Elephant's Marchoo | Complete | on_play, trigger | [Main] K.O. up to 1 of your opponent's Characters with a cost of 2 or less, then add up to 1 DON!! card from your DON!! deck an... | [Trigger] Activate this card's [Main] effect. | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-116` | Artificial Devil Fruit SMILE | Complete | on_play, trigger | [Main] Look at 5 cards from the top of your deck; play up to 1 {SMILE} type Character card with a cost of 3 or less. Then, plac... | [Trigger] Activate this card's [Main] effect. | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-117` | Sheep's Horn | Complete | on_play | [Main] DON!! −1 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Rest up to 1 of your ... | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-118` | Ulti-Mortar | Partial | counter, trigger | [Counter] DON!! −2 (You may return the specified number of DON!! cards from your field to your DON!! deck.): Up to 1 of your Le... | [Trigger] Add up to 1 DON!! card from your DON!! deck and set it as active. | OP01 seeds | Counter resolves draw before power in current callback; printed text is power then draw. |
| `OP01-119` | Thunder Bagua | Complete | counter, trigger | [Counter] Up to 1 of your Leader or Character cards gains +4000 power during this battle. Then, if you have 2 or less Life card... | [Trigger] Add up to 1 DON!! card from your DON!! deck and set it as active. | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-120` | Shanks | Complete | on_attack | [Rush] (This card can attack on the turn in which it is played.) / [When Attacking] Your opponent cannot activate a [Blocker] C... | None | OP01 seeds | No exactness blocker found in this pass. |
| `OP01-121` | Yamato | Partial | continuous | Also treat this card's name as [Kouzuki Oden] according to the rules. / [Double Attack] (This card deals 2 damage.) / [Banish] ... | None | OP01 seeds | Name alias support depends on engine consumers checking also_named. |
