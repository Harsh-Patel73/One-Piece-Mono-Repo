# Card Effect Status — OP01

## Status Legend
- `✅ Verified` — Implemented and confirmed correct in simulator
- `⚠ Needs Fix` — Implementation exists but has a bug or mismatch
- `🔲 To Do` — Hardcoded impl exists, needs audit/verification
- `❌ Missing` — No implementation, needs writing
- `⬜ No Effect` / `⬜ Keywords` — No custom code needed

| ID | Name | Type | Status | Effect (summary) | Notes |
|----|----|------|--------|-----------------|-------|
| OP01-001 | ✅ Verified | LEADER | I also, need to check if the "Your Turn" tag works correctly. So the character should gain the power on MY turn but when I end my turn their power should go back down to what it was before. | [DON!! x1] [Your Turn] All of your Characters gain +1000 power. | Impl exists: continuous |
| OP01-002 | ✅ Verified | LEADER | Picking up the character works as expected, it does not prompt me to choose a character with cost 5 or less of different color to play out though. Good progress. | [Activate: Main] [Once Per Turn] ➁ (You may rest the specified number … | Impl exists: activate |
| OP01-003 | ✅ Verified | LEADER | ATTACKING STILL DOES NOT REST THE FUCKING CHARACTER. I THEREFORE CANNOT TEST | [Activate: Main] [Once Per Turn] ➃ (You may rest the specified number … | Impl exists: activate |
| OP01-004 | ✅ Verified | CHARACTER | I am attacking, but opponent is not using an event so I cannot test. | [DON!! x1] [Your Turn] [Once Per Turn] Draw 1 card when your opponent … | Impl exists: on_event_activated |
| OP01-005 | ✅ Verified | CHARACTER | This card is aso close to being completed correctly. The options are great, and accurate but the card does not get added to hand when I select it. | [On Play] Add up to 1 red Character card other than [Uta] with a cost … | Impl exists: on_play |
| OP01-006 | ✅ Verified | CHARACTER | When combat happens, after playing Otama to give Katakuri -2000 power, it is not reflecting the -2000 debuff. He is still at 6000 in combat. | [On Play] Give up to 1 of your opponent's Characters −2000 power durin… | Impl exists: on_play |
| OP01-007 | ✅ Verified | CHARACTER | I cannot test, there is no way to KO my Caribou to see if it lets me KO an opponents character with 4000 power or less. | [On K.O.] K.O. up to 1 of your opponent's Characters with 4000 power o… | Impl exists: on_ko |
| OP01-008 | ✅ Verified | CHARACTER | 🔲 To Do | [On Play] You may add 1 card from your Life area to your hand: This Ch… | Impl exists: on_play |
| OP01-009 | ✅ Verified | CHARACTER | The trigger activates correctly, but when I attack the opponents life THEY should be getting the trigger. So, Opponent would play out the carrot in this testing. (I know it should not be allowed regularly since the color does not match the leader) | [Trigger] Play this card. | Impl exists: trigger |
| OP01-010 | ✅ Verified | CHARACTER | ⬜ No Effect |  |  |
| OP01-011 | ✅ Verified | CHARACTER | Player should be prompted for which card they walk to place at bottom of deck. | [On Play] You may place 1 card from your hand at the bottom of your de… | Impl exists: on_play |
| OP01-012 | ✅ Verified | CHARACTER | ⬜ No Effect |  |  |
| OP01-013 | ✅ Verified | CHARACTER | 🔲 To Do | [Activate: Main] [Once Per Turn] You may add 1 card from your Life are… | Impl exists: activate |
| OP01-014 | ✅ Verified | CHARACTER | Effect works as intended. A change to remember for the remainder of the project though is that when a character blocks it should become rested. It will refresh when we enter refresh phase (Start of turn) UNLESS there is an effect preventing it from restanding to active. | [Blocker] (After your opponent declares an attack, you may rest this c… | Impl exists: blocker, on_block |
| OP01-015 | ✅ Verified | CHARACTER | Only seeing Error: Invalid choice response in Game Log, I am at least being prompted which is good, but not the correct effect at the end. The card I choose to trash is not being trashed and the card I am taking from trash to hand is not working either. | [DON!! x1] [When Attacking] You may trash 1 card from your hand: Add u… | Impl exists: on_attack |
| OP01-016 | ✅ Verified | CHARACTER | Still cannot choose the order that I want to send the cards to the bottom of the deck in. | [On Play] Look at 5 cards from the top of your deck; reveal up to 1 {S… | Impl exists: on_play |
| OP01-017 | ✅ Verified | CHARACTER | For testing this card needs to be in play already and opponent should have a 3000 power character. | [DON!! x1] [When Attacking] K.O. up to 1 of your opponent's Characters… | Impl exists: on_attack |
| OP01-018 | ✅ Verified | CHARACTER | ⬜ No Effect |  |  |
| OP01-019 | ✅ Verified | CHARACTER | The card effect is working as intended, somehow your dumbass has not figured out that DON should only give extra power when it is that card's owner's turn. When they pass the buff from Don cards goes away. | [Blocker] (After your opponent declares an attack, you may rest this c… | Impl exists: blocker, continuous |
| OP01-020 | ✅ Verified | CHARACTER | 🔲 To Do | [Activate: Main] You may rest this Character: Up to 1 of your Leader o… | Impl exists: activate |
| OP01-021 | ✅ Verified | CHARACTER | This card should be able to attack ACTIVE characters when he has a Don on him, however this is not the case. Only the leader is an option to attack. | [DON!! x1] This Character can also attack your opponent's active Chara… | Impl exists: continuous |
| OP01-022 | ✅ Verified | CHARACTER | The player should be prompted and allowed to select who to give -2000 to. But other than that it works. | [DON!! x1] [When Attacking] Give up to 2 of your opponent's Characters… | Impl exists: on_attack |
| OP01-023 | ✅ Verified | CHARACTER | ⬜ No Effect |  |  |
| OP01-024 | ✅ Verified | CHARACTER | This card can still be KOd in battle by Strike Attribute Characters. | [DON!! x2] This Character cannot be K.O.'d in battle by ＜Strike＞ attri… | Impl exists: continuous, activate |
| OP01-025 | ✅ Verified | CHARACTER | 🔲 To Do | [Rush] (This card can attack on the turn in which it is played.) | Impl exists: continuous |
| OP01-026 | ✅ Verified | EVENT | The coutner part of this card worked correctly. There was no prompt given to KO the character with 4000 power or less though. | [Counter] Up to 1 of your Leader or Character cards gains +4000 power … | Impl exists: counter |
| OP01-027 | ✅ Verified | EVENT | 🔲 To Do | [Main] Give up to 1 of your opponent's Characters −10000 power during … | Impl exists: on_play |
| OP01-028 | ✅ Verified | EVENT | === Turn 2: Opponent (DON: 5) === Opponent's Atlas (Power: 6000) attacks Monkey.D.Luffy! [COUNTER EVENT] Tester plays Green Star Rafflesia (Cost 1 DON, +0) Atlas gets -2000 power Karoo added to hand. This is the game log, I should not be taking damage in this interaction, I gave the Atlas -2000 power. | [Counter] Give up to 1 of your opponent's Leader or Character cards −2… | Impl exists: counter |
| OP01-029 | ✅ Verified | EVENT | Why is this being buffed to 11000? It should not give +2000 then +4000 it should be +2000 then another +2000 when the player has 2 or less life. | [Counter] Up to 1 of your Leader or Character cards gains +2000 power … | Impl exists: counter |
| OP01-030 | ✅ Verified | EVENT | For some reason it only shows the top 4 cards not 5. But that part does work fine. | [Main] Look at 5 cards from the top of your deck; reveal up to 1 {Stra… | Impl exists: on_play |
| OP01-031 | ✅ Verified | LEADER | Leader works, but again the player should have the option to select which card they want to trash. | [Activate: Main] [Once Per Turn] You can trash 1 {Land of Wano} type c… | Impl exists: activate |
| OP01-032 | ✅ Verified | CHARACTER | The +2000 power should be IMMEDIATE when there is a 2nd rested character. The issue I am seeing is that when a 5000 power character attacks Ashura Doji he is not getting the +2000 to help him defend. | [DON!! x1] If your opponent has 2 or more rested Characters, this Char… | Impl exists: continuous |
| OP01-033 | ✅ Verified | CHARACTER | 🔲 To Do | [On Play] Rest up to 1 of your opponent's Characters with a cost of 4 … | Impl exists: on_play |
| OP01-034 | ✅ Verified | CHARACTER | 🔲 To Do | [DON!! x2] [When Attacking] Set up to 1 of your DON!! cards as active. | Impl exists: on_attack |
| OP01-035 | ✅ Verified | CHARACTER | 🔲 To Do | [DON!! x1] [When Attacking] [Once Per Turn] Rest up to 1 of your oppon… | Impl exists: on_attack |
| OP01-036 | ✅ Verified | CHARACTER | ⬜ No Effect |  |  |
| OP01-037 | ✅ Verified | CHARACTER | 🔲 To Do |  | Impl exists: trigger |
| OP01-038 | ✅ Verified | CHARACTER | The effect works as intended, 1 slight problem. The opponent should not see the hand, they should have to choose the card to trash without knowing what it is. | [DON!! x1] [When Attacking] K.O. up to 1 of your opponent's rested Cha… | Impl exists: on_attack, on_ko |
| OP01-039 | ✅ Verified | CHARACTER | On Block there is no additional draw even though there are 3 or more characters on field. Also keep in mind IMMEDIATELY when the block is done is when that effect should take place. | [Blocker] (After your opponent declares an attack, you may rest this c… | Impl exists: blocker, on_block |
| OP01-040 | ✅ Verified | CHARACTER | 🔲 To Do | [On Play] If your Leader is [Kouzuki Oden], play up to 1 {The Akazaya … | Impl exists: on_play, on_attack |
| OP01-041 | ✅ Verified | CHARACTER | For this testing make it so that the search has Land of Wano type cards in it. | [Activate: Main] ➀ (You may rest the specified number of DON!! cards i… | Impl exists: activate |
| OP01-042 | ✅ Verified | CHARACTER | Card effect is working, but the player should be prompted to choose a character to restand (set as active again). | [On Play] ③ (You may rest the specified number of DON!! cards in your … | Impl exists: on_play |
| OP01-043 | ✅ Verified | CHARACTER | ⬜ No Effect |  |  |
| OP01-044 | ✅ Verified | CHARACTER | 🔲 To Do | [Blocker] (After your opponent declares an attack, you may rest this c… | Impl exists: blocker, on_play |
| OP01-045 | ✅ Verified | CHARACTER | ⬜ No Effect |  |  |
| OP01-046 | ✅ Verified | CHARACTER | Effect did not work at all. | [DON!! x1] [When Attacking] If your Leader is [Kouzuki Oden], set up t… | Impl exists: on_attack |
| OP01-047 | ✅ Verified | CHARACTER | It is letting me pick up a character but it wont let me do the 2nd part where I get to play a 3 cost or less from hand. Also when I pick up the card to hand it is not coming to hand it jsut disappears. | [Blocker] (After your opponent declares an attack, you may rest this c… | Impl exists: blocker, on_play |
| OP01-048 | ✅ Verified | CHARACTER | 🔲 To Do | [On Play] Rest up to 1 of your opponent's Characters with a cost of 3 … | Impl exists: on_play |
| OP01-049 | ✅ Verified | CHARACTER | 🔲 To Do | [DON!! x1] [When Attacking] Play up to 1 {Heart Pirates} type Characte… | Impl exists: on_attack |
| OP01-050 | ✅ Verified | CHARACTER | 🔲 To Do | [Blocker] (After your opponent declares an attack, you may rest this c… | Impl exists: blocker, on_play |
| OP01-051 | ✅ Verified | CHARACTER | When this character has a DON attached to it, the enemy can ONLY attack this card but it still let's me choose other targets. | [DON!! x1] [Opponent's Turn] If this Character is rested, your opponen… | Impl exists: continuous, activate |
| OP01-052 | ✅ Verified | CHARACTER | 🔲 To Do | [When Attacking] [Once Per Turn] If you have 2 or more rested Characte… | Impl exists: on_attack |
| OP01-053 | ✅ Verified | CHARACTER | ⬜ No Effect |  |  |
| OP01-054 | ✅ Verified | CHARACTER | 🔲 To Do | [On Play] K.O. up to 1 of your opponent's rested Characters with a cos… | Impl exists: on_play |
| OP01-055 | ✅ Verified | EVENT | No effect at all | [Main] You may rest 2 of your Characters: Draw 2 cards. | Impl exists: on_play |
| OP01-056 | ✅ Verified | EVENT | 🔲 To Do | [Main] K.O. up to 2 of your opponent's rested Characters with a cost o… | Impl exists: on_play |
| OP01-057 | ✅ Verified | EVENT | At least in this instance the counter effect is being counted twice: Opponent's Charlotte Cracker (Power: 5000) attacks Sanji! [COUNTER EVENT] Tester plays Paradise Waterfall (Cost 1 DON, +2000) Paradise Waterfall: Sanji gains +2000 power Sanji was set active Charlotte Cracker's attack is defended (Defense: 8000). This should not be the case now and I hope this is not an issue with the other events. Please let me know if it is an issue across multiple effects or jsut with this card. | [Counter] Up to 1 of your Leader or Character cards gains +2000 power … | Impl exists: counter |
| OP01-058 | ✅ Verified | EVENT | Player is not prompted to rest a 4 cost or less when using this counter. But the +4000 is working as expected. | [Counter] Up to 1 of your Leader or Character cards gains +4000 power … | Impl exists: counter |
| OP01-059 | ✅ Verified | EVENT | Put Land of Wano characters in this board so I can test this card. | [Main] You may trash 1 {Land of Wano} type card from your hand: Set up… | Impl exists: on_play |
| OP01-060 | ✅ Verified | LEADER | If the top card is NOT valid, it should still show what card is at the top. And it does not get put to the bottom of the deck it just remains there and cannot be played out. There should not be any bottom decking with this leader effect. | [DON!! x2] [When Attacking] ➀ (You may rest the specified number of DO… | Impl exists: on_attack |
| OP01-061 | ✅ Verified | LEADER | I am KOing a character with DON on leader, and the DON is not being added as active still. | [DON!! x1] [Your Turn] [Once Per Turn] When your opponent's Character … | Impl exists: on_opponent_ko |
| OP01-062 | ✅ Verified | LEADER | Even on the opponents turn if I use a counter event, I should still draw 1 card if I have less than 4 in hand. | [DON!! x1] When you activate an Event, you may draw 1 card if you have… | Impl exists: on_event |
| OP01-063 | ✅ Verified | CHARACTER | The game log says: "=== Turn 1: Tester (DON: 1) === Both players ready. Game starting! Tester attaches 1 DON to Arlong. Arlong: Opponent reveals Thunder Bolt (EVENT) Arlong: Placed 1 of Tester's Life at bottom of deck" but the life is not actually being placed to the bottom of the deck, the opponent still has 4 life. | [DON!! x1] [Activate: Main] You may rest this Character: Choose 1 card… | Impl exists: activate |
| OP01-064 | ✅ Verified | CHARACTER | Effect does nothing at all | [DON!! x1] [When Attacking] You may trash 1 card from your hand: Retur… | Impl exists: on_attack |
| OP01-065 | ✅ Verified | CHARACTER | ⬜ No Effect |  |  |
| OP01-066 | ✅ Verified | CHARACTER | ⬜ No Effect |  |  |
| OP01-067 | ✅ Verified | CHARACTER | Fixed: cost=0 DON spending loop bug was already fixed but server needed restart (uvicorn --reload only watches backend dir, not game-engine package). | [Banish] (When this card deals damage, the target card is trashed with… | Impl exists: continuous |
| OP01-068 | ✅ Verified | CHARACTER | This card is still dealing double attack even with less than 5 cards in hand. | [Your Turn] This Character gains [Double Attack] if you have 5 or more… | Impl exists: continuous |
| OP01-069 | ✅ Verified | CHARACTER | On KO effect is not doing anything | [On K.O.] Play up to 1 [Smiley] from your deck, then shuffle your deck… | Impl exists: on_ko |
| OP01-070 | ✅ Verified | CHARACTER | 🔲 To Do | [On Play] Place up to 1 Character with a cost of 7 or less at the bott… | Impl exists: on_play |
| OP01-071 | ✅ Verified | CHARACTER | 🔲 To Do | [On Play] Place up to 1 Character with a cost of 3 or less at the bott… | Impl exists: on_play |
| OP01-072 | ✅ Verified | CHARACTER | Effect for the card works great, problem is with core game engine. Don only gives the card power on Your Turn, when the player passes power from Don goes away. i.e, Smiley has 1000 power, on his turn if DON is attached he gets power from the don. When turn is passed that DON no longer gives power. | [DON!! x1] [Your Turn] This Character gains +1000 power for every card… | Impl exists: continuous |
| OP01-073 | ✅ Verified | CHARACTER | I can now choose the top or bottom but I cannot choose the order that I want to rearrange them to. | [Blocker] (After your opponent declares an attack, you may rest this c… | Impl exists: blocker, on_play |
| OP01-074 | ✅ Verified | CHARACTER | The on KO is working, but this card is not being detected as a blocker. | [Blocker] (After your opponent declares an attack, you may rest this c… | Impl exists: blocker, on_ko |
| OP01-075 | ✅ Verified | CHARACTER | This blocker is not being detected as a blocker. | Under the rules of this game, you may have any number of this card in … | Impl exists: blocker |
| OP01-076 | ✅ Verified | CHARACTER | ⬜ No Effect |  |  |
| OP01-077 | ✅ Verified | CHARACTER | I can now choose the top or bottom of the deck but I cannot choose the order to rearrange them to now. | [On Play] Look at 5 cards from the top of your deck and place them at … | Impl exists: on_play |
| OP01-078 | ✅ Verified | CHARACTER | Two problems I am noticing so far. 1: WHen I attack while having DON attached I should draw 1 card but it is drawing 2. 2: This card is not being detected as a blocker. | [Blocker] (After your opponent declares an attack, you may rest this c… | Impl exists: on_play |
| OP01-079 | ✅ Verified | CHARACTER | 1. We need to ensure that there is an event card in trash so I can test that effect.  Also, when I block this card has the wrong effect, it is making me trash 2 cards for some reason. | [Blocker] (After your opponent declares an attack, you may rest this c… | Impl exists: blocker, on_block |
| OP01-080 | ✅ Verified | CHARACTER | 🔲 To Do | [On K.O.] Draw 1 card. | Impl exists: on_ko |
| OP01-081 | ✅ Verified | CHARACTER | ⬜ No Effect |  |  |
| OP01-082 | ✅ Verified | CHARACTER | 🔲 To Do |  | Impl exists: trigger |
| OP01-083 | ✅ Verified | CHARACTER | Make it so that only events are in trash so I can test this card. | [DON!! x1] [Your Turn] If your Leader has the {Baroque Works} type, th… | Impl exists: continuous |
| OP01-084 | ✅ Verified | CHARACTER | Ensure that there is a Baroque Works type event in the top 5 so I can test this card correctly. | [DON!! x1] [When Attacking] Look at 5 cards from the top of your deck;… | Impl exists: on_attack |
| OP01-085 | ✅ Verified | CHARACTER | I am choosing the character that cannot attack, but it is still allowing that character to attack when I pass the turn. | [On Play] If your Leader has the {Baroque Works} type, select up to 1 … | Impl exists: on_play |
| OP01-086 | ✅ Verified | EVENT | This effect works almost as intended. It let's me return an OPPONENTS cost of 3 or less to hand if it is active  - this is correct. I should also be given the option to return one of my OWN characters that are active with 3 cost or less as well. | [Counter] Up to 1 of your Leader or Character cards gains +4000 power … | Impl exists: counter |
| OP01-087 | ✅ Verified | EVENT | 🔲 To Do | [Counter] Play up to 1 {Baroque Works} type Character card with a cost… | Impl exists: counter |
| OP01-088 | ✅ Verified | EVENT | I can now choose the top or bottom but I cannot choose the order that I want to rearrange them to. | [Counter] Up to 1 of your Leader or Character cards gains +2000 power … | Impl exists: counter |
| OP01-089 | ✅ Verified | EVENT | 🔲 To Do | [Counter] If your Leader has the {The Seven Warlords of the Sea} type,… | Impl exists: counter |
| OP01-090 | ✅ Verified | EVENT | 🔲 To Do | [Main] Look at 5 cards from the top of your deck; reveal up to 1 {Baro… | Impl exists: on_play |
| OP01-091 | ✅ Verified | LEADER | 🔲 To Do | [Your Turn] If you have 10 DON!! cards on your field, give all of your… | Impl exists: continuous |
| OP01-092 | ✅ Verified | CHARACTER | ⬜ No Effect |  |  |
| OP01-093 | ✅ Verified | CHARACTER | This card automatically chooses to rest 1 more DON for the on play effect, I should be prompted if I want to do this. If I do I should gain 1 DON card rested. I am not gaining the extra don. | [On Play] ① (You may rest the specified number of DON!! cards in your … | Impl exists: on_play |
| OP01-094 | ✅ Verified | CHARACTER | Effect seems to be working, but cannot tell for sure, for testing the leader needs to be an Animal Kingdom Pirates type. | [On Play] DON!! −6 (You may return the specified number of DON!! cards… | Impl exists: on_play |
| OP01-095 | ✅ Verified | CHARACTER | 🔲 To Do | [On Play] Draw 1 card if you have 8 or more DON!! cards on your field. | Impl exists: on_play |
| OP01-096 | ✅ Verified | CHARACTER | I am not being given the option to choose which don I want to return so it is automatically returning the active don. | [On Play] DON!! −2 (You may return the specified number of DON!! cards… | Impl exists: on_play |
| OP01-097 | ✅ Verified | CHARACTER | 🔲 To Do | [On Play] DON!! −1 (You may return the specified number of DON!! cards… | Impl exists: on_play |
| OP01-098 | ✅ Verified | CHARACTER | Fixed: was searching deck by card name instead of card_origin (Type field) for SMILE. Changed to check card_origin for 'smile'. | [On Play] Reveal up to 1 [Artificial Devil Fruit SMILE] from your deck… | Impl exists: on_play |
| OP01-099 | ✅ Verified | CHARACTER | Kurozumi Clan characters other than Kurozumi Semimaru can still get KOd in battle. This should not be the case with Kurozumi Semimaru is in play. | {Kurozumi Clan} type Characters other than your [Kurozumi Semimaru] ca… | Impl exists: on_play |
| OP01-100 | ✅ Verified | CHARACTER | 🔲 To Do | [Blocker] (After your opponent declares an attack, you may rest this c… | Impl exists: on_attack |
| OP01-101 | ✅ Verified | CHARACTER | The card is letting me trash 1 from hand but I am not gaining the 1 DON!! card from the DON!! deck rested. | [DON!! x1] [When Attacking] You may trash 1 card from your hand: Add u… | Impl exists: on_attack |
| OP01-102 | ✅ Verified | CHARACTER | When I attack I am not prompted to DON!! -1 if I want to. So I do not know if the opponent is prompted to trash 1 card from their hand. | [When Attacking] DON!! −1 (You may return the specified number of DON!… | Impl exists: on_play |
| OP01-103 | ✅ Verified | CHARACTER | ⬜ No Effect |  |  |
| OP01-104 | ✅ Verified | CHARACTER | The card is a trigger and it is prompting me to use trigger, but when I select to play the card and activate the trigger it is not playing onto the field. |  | Impl exists: blocker |
| OP01-105 | ✅ Verified | CHARACTER | This card is revealing MY own hand when it should reveal the opponents. | [On Play] Choose 2 cards from your opponent's hand; your opponent reve… | Impl exists: on_play |
| OP01-106 | ✅ Verified | CHARACTER | When I play the card I am not gaining 1 DON!! card from the DON!! deck. | [On Play] Add up to 1 DON!! card from your DON!! deck and rest it. | Impl exists: on_play |
| OP01-107 | ✅ Verified | CHARACTER | ⬜ No Effect |  |  |
| OP01-108 | ✅ Verified | CHARACTER | 🔲 To Do | [On K.O.] DON!! −1 (You may return the specified number of DON!! cards… | Impl exists: on_ko |
| OP01-109 | ✅ Verified | CHARACTER | 🔲 To Do | [DON!! x1] [Your Turn] If you have 8 or more DON!! cards on your field… | Impl exists: blocker, continuous |
| OP01-110 | ✅ Verified | CHARACTER | ⬜ No Effect |  |  |
| OP01-111 | ✅ Verified | CHARACTER | I should be prompted if I want to use the DON -1 effect, it works as intended but is automatic. | [Blocker] (After your opponent declares an attack, you may rest this c… | Impl exists: blocker, on_block |
| OP01-112 | ✅ Verified | CHARACTER | 🔲 To Do | [Activate: Main] [Once Per Turn] DON!! −1 (You may return the specifie… | Impl exists: activate |
| OP01-113 | ✅ Verified | CHARACTER | ON KO I am not adding the DON!! card. | [On K.O.] Add up to 1 DON!! card from your DON!! deck and rest it. | Impl exists: on_ko |
| OP01-114 | ✅ Verified | CHARACTER | I am not prompted to DON!! -1 so the rest of the effect is not working either. | [On Play] DON!! −1 (You may return the specified number of DON!! cards… | Impl exists: continuous |
| OP01-115 | ✅ Verified | EVENT | I am prompted to KO a 2 cost or less, this works correctly. But I should also be able to add 1 DON!! card as active. | [Main] K.O. up to 1 of your opponent's Characters with a cost of 2 or … | Impl exists: on_play |
| OP01-116 | ✅ Verified | EVENT | Fixed: rewrote to use search_top_cards helper which always shows all top cards and handles deck ordering, even when no valid SMILE target exists. | [Main] Look at 5 cards from the top of your deck; play up to 1 {SMILE}… | Impl exists: on_play |
| OP01-117 | ✅ Verified | EVENT | 🔲 To Do | [Main] DON!! −1 (You may return the specified number of DON!! cards fr… | Impl exists: on_play |
| OP01-118 | ✅ Verified | EVENT | Fixed: DON return callback used wrong keyword arg `power_change=2000` instead of positional `power_amount`. TypeError left game stuck in counter stage. | [Counter] DON!! −2 (You may return the specified number of DON!! cards… | Impl exists: counter |
| OP01-119 | ✅ Verified | EVENT | 🔲 To Do | [Counter] Up to 1 of your Leader or Character cards gains +4000 power … | Impl exists: counter |
| OP01-120 | ✅ Verified | CHARACTER | The game is still allowing blockers with a power of 2000 or less to be activated. | [Rush] (This card can attack on the turn in which it is played.) [When… | Impl exists: on_attack |
| OP01-121 | ✅ Verified | CHARACTER | 🔲 To Do | Also treat this card's name as [Kouzuki Oden] according to the rules. … | Impl exists: continuous |

**Total:** 121 cards
**Missing:** 0
**Needs Fix:** 10
**To Do (audit):** 88
**Verified:** 23

---

# Card Effect Status — OP02

> 15 new effects added: OP02-021, 045, 046, 047, 048, 067, 068, 069, 070, 089, 090, 091, 117, 118, 119
> All others were pre-existing in op02_effects.py or have no effect (vanilla).

| ID | Status | Type | Notes |
|----|--------|------|-------|
| OP02-001 | ✅ Verified | LEADER | Every time the turn is ended a card from top of life should be added to the hand. |
| OP02-002 | ✅ Verified | LEADER | I should be able to give -1 DON!! to a 7 cost or less. It currently does not prompt me to do this. |
| OP02-003 | ✅ Verified | CHARACTER |  |
| OP02-004 | ✅ Verified | CHARACTER | The "then you cannot add life cards to your hand using your own effects during this turn" means that Newgate's leader effect or any other card that would take a life from the life pile and add it to hand cannot be done anymore during this turn. So for example Edward Newgate's leader effect states that at the end of the turn take a life card to hand. This essentially stops that from happening. |
| OP02-005 | ✅ Verified | CHARACTER | on_play: look 5, reveal red cost 1 char |
| OP02-006 | ✅ Verified | CHARACTER |  |
| OP02-007 | ✅ Verified | CHARACTER |  |
| OP02-008 | ✅ Verified | CHARACTER | Change the leader to edward newgate so I can test. |
| OP02-009 | ✅ Verified | CHARACTER | Change the leader to edward newgate so I can test. |
| OP02-010 | ✅ Verified | CHARACTER | activate: rest self → play red cost 1 from hand |
| OP02-011 | ✅ Verified | CHARACTER | on_play: KO opp ≤3000 power |
| OP02-012 | ✅ Verified | CHARACTER | blocker |
| OP02-013 | ✅ Verified | CHARACTER | If the leader's type includes "Whitebeard Pirates" this card should be given rush. The leader is Edward Newgate but he still does not have rush. |
| OP02-014 | ✅ Verified | CHARACTER | continuous: DON x1, attack active chars |
| OP02-015 | ✅ Verified | CHARACTER | activate: rest self → red cost 1 char +3000 |
| OP02-016 | ✅ Verified | CHARACTER | on_play: red cost 1 char +3000 |
| OP02-017 | ✅ Verified | CHARACTER | on_attack: DON x2, KO opp ≤2000 power |
| OP02-018 | ✅ Verified | CHARACTER | When this card dies, I should be able to trash a card with "Whitebeard Pirates" in it to play the card from the trash. |
| OP02-019 | ✅ Verified | CHARACTER | continuous: DON x1, WB chars +1000 |
| OP02-020 | ✅ Verified | CHARACTER |  |
| OP02-021 | ✅ Verified | EVENT | Make the leader edward newgate |
| OP02-022 | ✅ Verified | EVENT | on_play: look 5, reveal WB char; trigger |
| OP02-023 | ✅ Verified | EVENT | Currently, this card is taking a life and adding it to hand. It should simply prevent the user from taking cards from life to hand by EFFECTS on their turn. So Newgate's leader effect would not let him take the life since you can no longer take life by effects when you have 3 life or less. |
| OP02-024 | ✅ Verified | STAGE | This stage should give "Edward Newgate" and ALL Whitebeard Pirates type cards +2000 power if they have 1 life or less. |
| OP02-025 | ⚠ Needs Fix | LEADER | Still getting "Error: Cannot activate effect" error.  |
| OP02-026 | ✅ Verified | LEADER | When a character with no base effect so no on play, no activate main, no when attacking, there should be NO description on the card.  When that card is played, I should be prompted to set UP TO 2 DON!! cards as active. |
| OP02-027 | 🔲 To Do | CHARACTER | continuous: if all DON rested, immune to opp removal |
| OP02-028 | ✅ Verified | CHARACTER |  |
| OP02-029 | ✅ Verified | CHARACTER | Carrot is automatically setting 1 DON as active, I should be prompted since it says up to 1, if I want to set 0 DON! as active or 1. |
| OP02-030 | ⚠ Needs Fix | CHARACTER | I do not think the Once Per Turn is coded correctly, it is letting me restand a 2nd time.  |
| OP02-031 | ✅ Verified | CHARACTER | The card OP02-042 has the effect "Treat this cards name as ALSO Kozuki Oden", so when this card is in play Toki should also gain blocker. |
| OP02-032 | ✅ Verified | CHARACTER | When this card is played I should be prompted to rest 2 DON!! and set 1 minks type character with a cost of 5 or less as active. |
| OP02-033 | ✅ Verified | CHARACTER |  |
| OP02-034 | ✅ Verified | CHARACTER | on_attack: DON x1, rest opp cost 2 or less |
| OP02-035 | ✅ Verified | CHARACTER | It should rest 1 DON when I activate to return this card to the owners hand and then prompt me to play a 3 cost or less from hand. |
| OP02-036 | ✅ Verified | CHARACTER | The on play is coded correctly, it should also prompt me to use the effect when the card attacks. |
| OP02-037 | ✅ Verified | CHARACTER | on_play: play FILM/SHC cost 2 or less from hand |
| OP02-038 | ✅ Verified | CHARACTER | blocker |
| OP02-039 | ✅ Verified | CHARACTER |  |
| OP02-040 | ✅ Verified | CHARACTER | on_play: play FILM/SHC cost 3 or less from hand |
| OP02-041 | ✅ Verified | CHARACTER | blocker; on_play: play FILM/SHC cost 4 or less from hand |
| OP02-042 | ✅ Verified | CHARACTER | on_play: rest opp cost 6 or less (treated as Oden) |
| OP02-043 | ✅ Verified | CHARACTER |  |
| OP02-044 | ✅ Verified | CHARACTER | It should prompt me to play up to 1 Minks type not do it automatically. I should have the option to choose 0. |
| OP02-045 | ✅ Verified | EVENT | counter: +6000 to leader; play vanilla char cost 3 or less |
| OP02-046 | ✅ Verified | EVENT | on_play: KO opp rested char cost 4 or less |
| OP02-047 | ✅ Verified | EVENT | on_play: rest opp char cost 4 or less |
| OP02-048 | ✅ Verified | STAGE | It should prompt me if I want to trash 1 Land of Wano type card from hand and rest the stage. If I do, then it should set up to 1 DON!! cards as active. |
| OP02-049 | ✅ Verified | LEADER | end_of_turn: if 0 hand, draw 2 |
| OP02-050 | ✅ Verified | CHARACTER | continuous: if ≤1 hand, +2000; blocker |
| OP02-051 | ✅ Verified | CHARACTER | on_play: draw to 3, play blue Impel Down cost 6 or less |
| OP02-052 | ✅ Verified | CHARACTER | on_play: if Mohji in play, draw 2 trash 1 |
| OP02-053 | ✅ Verified | CHARACTER |  |
| OP02-054 | ✅ Verified | CHARACTER |  |
| OP02-055 | ✅ Verified | CHARACTER |  |
| OP02-056 | ✅ Verified | CHARACTER | Does not search the top 3, the when attacking effect is coded correctly. |
| OP02-057 | ✅ Verified | CHARACTER | on_play: look 2, reveal Seven Warlords card |
| OP02-058 | ✅ Verified | CHARACTER | It does not let me add Impel Down characters other than Buggy to my hand it just immediately lets me start placing them at bottom of deck. |
| OP02-059 | ✅ Verified | CHARACTER | It should prompt me if I want to trash up to 3 cards from hand after I do the draw 1 trash 1 effect. |
| OP02-060 | ✅ Verified | CHARACTER |  |
| OP02-061 | ✅ Verified | CHARACTER | Blockers with a cost of 5 or less should not be able to block when this card and ONLY this card attacks and the player has less than 1 card in hand. Currently they can still block with characters cost 5 or less. |
| OP02-062 | ✅ Verified | CHARACTER | I should also have the option to NOT trash 2 cards and not use his effect. Right now it makes me select 2 cards to trash there is no skip option. |
| OP02-063 | ✅ Verified | CHARACTER | The effect is not working, it does correctly show me the blue 1 cost events in the trash, but when I go to add one to hand it is not being added to the hand |
| OP02-064 | ✅ Verified | CHARACTER | It does do what the effect says, but it should prompt me to choose a card to trash from hand. Also, this card should get sent to the bottom of the deck at the end of the battle. |
| OP02-065 | ✅ Verified | CHARACTER | When I end turn it should prompt and ask me if I want to trash a card from hand and set this character back as active. |
| OP02-066 | ✅ Verified | EVENT | This card's effect is not programmed. It does nothing when I select it. |
| OP02-067 | ✅ Verified | EVENT | on_play: return opp char cost 4 or less to hand |
| OP02-068 | ✅ Verified | EVENT | It should prompt me to select a card to trash to use the effect of this card. |
| OP02-069 | ✅ Verified | EVENT | counter: +6000 to leader; draw to 2 |
| OP02-070 | ✅ Verified | STAGE | After I do the draw 1 and trash 1. It should prompt me to trash up to 3 cards from hand, so I can choose to trash 0, 1, 2, or 3 cards. |
| OP02-071 | ✅ Verified | LEADER | On the players turn, ONCE per turn if a DON card is returned to the DON!! deck, the Magellan leader should gain +1000 power for the turn. Currently nothing is happening when a don is returned. |
| OP02-072 | ✅ Verified | LEADER | on_attack: DON -4 → KO opp ≤3 cost + leader +1000 |
| OP02-073 | ✅ Verified | CHARACTER | on_play: play Jailer Beast from hand |
| OP02-074 | ✅ Verified | CHARACTER | This card should not have blocker. It only gives "Blugori" Blocker when it is also on the field with him. |
| OP02-075 | ⚠ Needs Fix | CHARACTER | This card should be in life so we can test.  |
| OP02-076 | ✅ Verified | CHARACTER | on_play: DON -1 → KO opp cost 1 or less |
| OP02-077 | ✅ Verified | CHARACTER |  |
| OP02-078 | ✅ Verified | CHARACTER | on_play: DON -2 → play SMILE cost 3 or less from hand |
| OP02-079 | ✅ Verified | CHARACTER | on_play: DON -1 → rest opp cost 4 or less |
| OP02-080 | ✅ Verified | CHARACTER |  |
| OP02-081 | ✅ Verified | CHARACTER | blocker |
| OP02-082 | ✅ Verified | CHARACTER | This card should increase the power by 792000, only if the player returns 8 DON!! to their don deck. |
| OP02-083 | ✅ Verified | CHARACTER | on_play: look 5, reveal purple Impel Down card |
| OP02-084 | ✅ Verified | CHARACTER |  |
| OP02-085 | ✅ Verified | CHARACTER | Right now if I use KO to KO Magellan on my turn it still makes the opponent return 2 DON!! to their DON deck, this should only be activated on the OPPONENTS TURN. |
| OP02-086 | ✅ Verified | CHARACTER | This card says "Add UP TO 1 DON!! card" so I should be prompted to add 0 or 1 DON!! cards from the don deck rested. |
| OP02-087 | ✅ Verified | CHARACTER | This card says \"Add UP TO 1 DON!! card\" so I should be prompted to add 0 or 1 DON!! cards from the don deck rested. |
| OP02-088 | ✅ Verified | CHARACTER |  |
| OP02-089 | ✅ Verified | EVENT | This card SHOULD give -3000 power to either a leader and character or two characters, right now when I select 2 cards it only gives one of them -4000 power.  Also, since it says up to I should be given the option to give 0, 1 or 2 targets the -3000. If I choose only one they still only get -3000, it does not stack. |
| OP02-090 | ✅ Verified | EVENT | This card currently returns an opponents card to their hand, it should not do that. It should allow me to give 1 of my opponent's characters -3000 power for the remainder of the turn. |
| OP02-091 | ✅ Verified | EVENT | on_play: add 1 DON from deck, set active |
| OP02-092 | ✅ Verified | STAGE | activate: trash 1 + rest stage → look 3, reveal Impel Down card |
| OP02-093 | ✅ Verified | LEADER | I do not think the leader effect is checking to see if the opponent has a 0 cost character AFTER the -1 cost is given. So for example, let's say the opponent has a 1 cost character, if I add a don to Smoker and use his leader effect then give that 1 cost -1 cost. It is now a 0 cost character so I should gain +1000 power for the turn. I should also have the option NOT to give -1 cost to an opponents character since it says up to. Then the check should still take place to see if there is a Character with a cost of 0. |
| OP02-094 | ✅ Verified | CHARACTER | When this character battles and KOs an opponents character if it has a DON on it, then it should automatically be set back as active. |
| OP02-095 | ⚠ Needs Fix | CHARACTER | This card has banish even with no 0 cost on the opponents board, this should not be the case.   |
| OP02-096 | ✅ Verified | CHARACTER | on_play: draw 1; on_attack: opp char -4 cost |
| OP02-097 | ✅ Verified | CHARACTER |  |
| OP02-098 | ✅ Verified | CHARACTER | I should only be able to use Koby's effect to KO a opponent's character if I trash 1 card from hand. I should also be prompted if I want to use that effect. If I choose not to trash the card from hand then I do not get to KO an opponents 3 cost character or less. |
| OP02-099 | ✅ Verified | CHARACTER | Same as the Koby card before, I need to pay the cost of trashing 1 card from hand to get access to the KO up to 1 opponents character with cost of 5 or less. |
| OP02-100 | ✅ Verified | CHARACTER | continuous: if Fullbody in play, can't be KO in battle |
| OP02-101 | ✅ Verified | CHARACTER | Even though there is a character with a cost of 0, the opponent can still activate blockers with a cost of 5 or less during the battle - this should not be the case. |
| OP02-102 | ✅ Verified | CHARACTER | Smoker needs to be the leader to test this card. |
| OP02-103 | ✅ Verified | CHARACTER | on_attack: DON x1; opp char -2 cost |
| OP02-104 | ✅ Verified | CHARACTER | The trigger for this card is "Play this card" but when I use the trigger the card is sent to the trash. |
| OP02-105 | ✅ Verified | CHARACTER | on_attack: DON x1; opp char -3 cost |
| OP02-106 | ✅ Verified | CHARACTER | on_play: opp char -2 cost |
| OP02-107 | ✅ Verified | CHARACTER |  |
| OP02-108 | ✅ Verified | CHARACTER | blocker |
| OP02-109 | ✅ Verified | CHARACTER |  |
| OP02-110 | ✅ Verified | CHARACTER | Even though I chose a character to not let them be able to attack per Hina's effect it still allows them to attack. |
| OP02-111 | ✅ Verified | CHARACTER | on_attack: if Jango in play, +3000 power |
| OP02-112 | ✅ Verified | CHARACTER | When I activate this character's effect it lets me give an opponents character -1 cost but it does not let me choose a leader or character to give +1000 power to. |
| OP02-113 | ⚠ Needs Fix | CHARACTER | The power gain should only last for the battle, so once the combat is done it shuld return to it's base power.  |
| OP02-114 | ⚠ Needs Fix | CHARACTER | This card should only gain +1000 power on the opponents turn, he is currently getting it on my turn too.  |
| OP02-115 | ✅ Verified | CHARACTER | on_attack: DON x2; KO opp cost 0 char |
| OP02-116 | ✅ Verified | CHARACTER |  |
| OP02-117 | ✅ Verified | EVENT | on_play: opp char -5 cost |
| OP02-118 | ✅ Verified | EVENT | I am using the effect on a card that is being targeted by an attack, the attack is big enough to kill and it is killing the character EVEN though the counter card says that the selected character cannot be KOd during THIS battle. |
| OP02-119 | ✅ Verified | EVENT | on_play: KO opp char cost 1 or less |
| OP02-120 | ✅ Verified | CHARACTER | They lose the +1000 power when I end my turn, they should keep that buff until my NEXT turn begins. |
| OP02-121 | ⚠ Needs Fix | CHARACTER | There is still no prompt to KO a 0 cost, after he gives all the opponents characters -5 cost.  |

---

# Card Effect Status — OP03

| ID | Status | Type | Notes |
|----|--------|------|-------|
| OP03-001 | ⚠ Needs Fix | LEADER | I should be prompted to select which cards I want to trash from hand. Currently it is happening automatically.  |
| OP03-002 | ✅ Verified | CHARACTER | DON x1: opp can't use Blocker 2000 or less |
| OP03-003 | ✅ Verified | CHARACTER | on_play: look 5, reveal Whitebeard Pirates card |
| OP03-004 | ⚠ Needs Fix | CHARACTER | When I attach the DON!! he gets rush as he should. However, it should not let me attack the leader with rush when I use the effect. It states that the leader cannot be attacked on the turn that this card is played.  |
| OP03-005 | ⚠ Needs Fix | CHARACTER | When I activate his effect, this card should get sent to the trash at the end of the turn.  |
| OP03-006 | ✅ Verified | CHARACTER |  |
| OP03-007 | ✅ Verified | CHARACTER |  |
| OP03-008 | ⚠ Needs Fix | CHARACTER | If the card attacking this card has the slash attribute, even if they win the combat he should not be able to be KOd.  |
| OP03-009 | ⚠ Needs Fix | CHARACTER | It seems he is giving the rested don card to a leader or character, but that character/leader is not gaining +1000 power when the rested DON is attached to them.  |
| OP03-010 | ✅ Verified | CHARACTER | blocker |
| OP03-011 | ⚠ Needs Fix | CHARACTER | When I attach DON!! and attack wtih this character I should be prompted to give -2000 power to 1 of the opponents character.  |
| OP03-012 | ⚠ Needs Fix | CHARACTER | This card should let me select from my hand as well for the trash option. Also, after I trash I am not drawing the 1 card.  Also, the card is not being sent to the trash.  |
| OP03-013 | ⚠ Needs Fix | CHARACTER | I should be prompted to select the card to trash from hand to use his effect, otherwise the effect works great.  |
| OP03-014 | ✅ Verified | CHARACTER | on_attack: play red cost 1 from hand |
| OP03-015 | ⚠ Needs Fix | CHARACTER | I should be given the option to select the leader as well when this character is KOd.  |
| OP03-016 | ⚠ Needs Fix | EVENT | Currently it let's me kill 8000 power and above, it should be 8000 power or less. Also, it is not indicating that my leader is gaining +3000 power and double attack.  |
| OP03-017 | ⚠ Needs Fix | EVENT | This card should give -4000 power, it is only giving -2000 power.  |
| OP03-018 | ⚠ Needs Fix | EVENT | It let's me KO 1 of the opponent's characters with 5000 power or less, but it should also let me KO a 4000 power or less.  |
| OP03-019 | ⚠ Needs Fix | EVENT | It is not increasing my leader's power by 4000.  |
| OP03-020 | ✅ Verified | STAGE | activate: DON -2, if Ace leader, look 5 add Event |
| OP03-021 | 🔲 To Do | LEADER | activate: rest 3 DON + 2 East Blue, set active, rest opp 5- |
| OP03-022 | 🔲 To Do | LEADER | DON x2 on_attack: DON -1, play cost 4 with Trigger |
| OP03-023 | ✅ Verified | CHARACTER |  |
| OP03-024 | ⚠ Needs Fix | CHARACTER | It should prompt me to select which 2 of my opponent's 4 cost or less characters to rest.  |
| OP03-025 | ⚠ Needs Fix | CHARACTER | I should have to trash 1 card from hand, which is correct and prompts so that is good. The problem is I should only be able to KO 2 rested 4 costs or less IF I trash the card. It is doing that automatically. I also should be prompted to select which rested 4 costs or less I want to KO.  |
| OP03-026 | ✅ Verified | CHARACTER | on_play: if East Blue leader, rest opp char; trigger |
| OP03-027 | ⚠ Needs Fix | CHARACTER | Also, when Buchi is played out via Sham's effect, it should still activate his on play.  |
| OP03-028 | 🔲 To Do | CHARACTER | on_play: set East Blue cost 6- active OR rest opp |
| OP03-029 | ✅ Verified | CHARACTER | on_play: KO rested cost 4-; trigger |
| OP03-030 | ✅ Verified | CHARACTER | on_play: look 5, reveal green East Blue; trigger |
| OP03-031 | ✅ Verified | CHARACTER | blocker |
| OP03-032 | ⚠ Needs Fix | CHARACTER | If the card attacking this card (leader or character) has the slash attribute, regardless of if they win the combat this character should not be able to be KOd.  |
| OP03-033 | ⚠ Needs Fix | CHARACTER | Make the opponent's leader have the East Blue type. I believe OP03-021 will work.  |
| OP03-034 | ✅ Verified | CHARACTER | on_play: KO rested cost 2- |
| OP03-035 | ✅ Verified | CHARACTER |  |
| OP03-036 | 🔲 To Do | EVENT | on_play: rest East Blue, set Kuro active |
| OP03-037 | 🔲 To Do | EVENT | on_play: rest East Blue, KO rested cost 4- |
| OP03-038 | ⚠ Needs Fix | EVENT | I should be given the option to select 2 characters with a cost of 2 or less, currently it only lets me choose 1.  |
| OP03-039 | ⚠ Needs Fix | EVENT | I should be prompted to select which 1 cost I want to rest. 0 should also be an option, then I should be prompted to select which character to give +1000 power to for the turn.  |
| OP03-040 | ⚠ Needs Fix | LEADER | Move 36 cards to the trash. I want the deck size to be 4 for this leader.  |
| OP03-041 | ⚠ Needs Fix | CHARACTER | When this character deal's damage (by attacking leader), the top 7 cards from the deck should be added to the trash.  |
| OP03-042 | ⚠ Needs Fix | CHARACTER | It should prompt me to select which card to add to hand.  |
| OP03-043 | ⚠ Needs Fix | CHARACTER | If any of my cards, leader or character deals damage to the opponent, I should be promtped per Gaimon effect to choose if I want to trash 3 cards from the top of my deck. If I choose to do so, trash the gaimon.  |
| OP03-044 | ✅ Verified | CHARACTER | on_play: draw 2, trash 2 |
| OP03-045 | ⚠ Needs Fix | CHARACTER | Make the deck size 20, so I can test this card.  |
| OP03-046 | ✅ Verified | CHARACTER |  |
| OP03-047 | ⚠ Needs Fix | CHARACTER | I should be able to choose the opponents 3 costs or less as well, for the on play effect. And then be given the option to trash 2 cards from the top of my deck.  |
| OP03-048 | ✅ Verified | CHARACTER | on_play: if Nami leader, return opp cost 5- |
| OP03-049 | ⚠ Needs Fix | CHARACTER | Set my deck to 20 cards so I can test this card.  |
| OP03-050 | ⚠ Needs Fix | CHARACTER | I should be given the option if I want to trash 1 card from the top of the deck.  |
| OP03-051 | ⚠ Needs Fix | CHARACTER | The On KO works, but I should be given to option to trash 7 cards from the top of my deck when I deal damage and there is don attached to this card.  |
| OP03-052 | ✅ Verified | CHARACTER |  |
| OP03-053 | ⚠ Needs Fix | CHARACTER | Set my deck to 20 cards so I can test this card.  |
| OP03-054 | ⚠ Needs Fix | EVENT | I should be given the option to select which leader or character gains +2000 power for the battle, also I should have the option to trash the 1 card from the top of the deck.  |
| OP03-055 | 🔲 To Do | EVENT | counter: trash 1, leader +4000 |
| OP03-056 | 🔲 To Do | EVENT | on_play: draw 2 |
| OP03-057 | 🔲 To Do | EVENT | on_play: place cost 5- at bottom |
| OP03-058 | 🔲 To Do | LEADER | continuous: cannot attack; activate: DON -1, play Galley-La 5- |
| OP03-059 | 🔲 To Do | CHARACTER | on_attack: DON -1, gain Banish |
| OP03-060 | 🔲 To Do | CHARACTER | on_attack: DON -1, draw 2, trash 1 |
| OP03-061 | ⬜ No Effect | CHARACTER |  |
| OP03-062 | 🔲 To Do | CHARACTER | on_play: look 5, reveal Water Seven card |
| OP03-063 | 🔲 To Do | CHARACTER | blocker; on_play: DON -1, if Water Seven leader draw 1 |
| OP03-064 | 🔲 To Do | CHARACTER | on_ko: if Galley-La leader, add 1 DON rested |
| OP03-065 | 🔲 To Do | CHARACTER | blocker |
| OP03-066 | 🔲 To Do | CHARACTER | on_play: rest 2 DON, add 1 active; if 8+ DON KO cost 4- |
| OP03-067 | 🔲 To Do | CHARACTER | DON x1 on_attack: if Galley-La leader, add 1 DON rested |
| OP03-068 | 🔲 To Do | CHARACTER | Banish; on_ko: if Impel Down leader, add 1 DON rested |
| OP03-069 | 🔲 To Do | CHARACTER | on_ko: if Impel Down leader, draw 2 trash 1 |
| OP03-070 | 🔲 To Do | CHARACTER | on_play: DON -1, trash cost 5, gain Rush |
| OP03-071 | 🔲 To Do | CHARACTER | on_attack: DON -1, rest opp cost 5- |
| OP03-072 | 🔲 To Do | EVENT | counter: trash 1, +3000 |
| OP03-073 | 🔲 To Do | EVENT | on_play: DON -1, draw 1 |
| OP03-074 | 🔲 To Do | EVENT | on_play: DON -2, place opp cost 4- at bottom |
| OP03-075 | 🔲 To Do | STAGE | activate: rest, if Iceburg leader add DON |
| OP03-076 | 🔲 To Do | LEADER | on_opponent_ko: trash 2, set leader active |
| OP03-077 | 🔲 To Do | LEADER | DON x2 on_attack: DON -1, if 1- life add deck to life |
| OP03-078 | 🔲 To Do | CHARACTER | DON x1 continuous: opp chars -3 cost; on_play: if opp 6+ hand trash 2 |
| OP03-079 | 🔲 To Do | CHARACTER | DON x1 continuous: can't be KO in battle |
| OP03-080 | 🔲 To Do | CHARACTER | on_play: place 2 CP from trash at bottom, KO cost 3- |
| OP03-081 | 🔲 To Do | CHARACTER | on_play: draw 2, trash 2, opp -2 cost |
| OP03-082 | ⬜ No Effect | CHARACTER |  |
| OP03-083 | 🔲 To Do | CHARACTER | on_play: look 5, trash up to 2, rest at bottom |
| OP03-084 | ⬜ No Effect | CHARACTER |  |
| OP03-085 | ⬜ No Effect | CHARACTER |  |
| OP03-086 | 🔲 To Do | CHARACTER | on_play: if CP leader, look 3, reveal CP card |
| OP03-087 | ⬜ No Effect | CHARACTER |  |
| OP03-088 | 🔲 To Do | CHARACTER | continuous: immune to KO by effects; blocker |
| OP03-089 | 🔲 To Do | CHARACTER | on_play: look 3, reveal Navy card |
| OP03-090 | 🔲 To Do | CHARACTER | DON x1 continuous: Blocker; on_ko: play CP cost 4- from trash |
| OP03-091 | 🔲 To Do | CHARACTER | on_play: set opp no-effect char cost to 0 |
| OP03-092 | 🔲 To Do | CHARACTER | on_play: place 2 CP from trash at bottom, gain Rush |
| OP03-093 | 🔲 To Do | CHARACTER | on_play: trash 1, if CP leader KO cost 1- |
| OP03-094 | 🔲 To Do | EVENT | on_play: if CP leader, look 5, play CP cost 5- |
| OP03-095 | 🔲 To Do | EVENT | on_play: give 2 opp chars -2 cost |
| OP03-096 | 🔲 To Do | EVENT | on_play: KO opp cost 0 or Stage |
| OP03-097 | 🔲 To Do | EVENT | counter: trash 1, +3000 |
| OP03-098 | 🔲 To Do | STAGE | activate: rest, if CP leader opp -2 cost |
| OP03-099 | 🔲 To Do | LEADER | DON x1 on_attack: look 1 life, place top/bottom, +1000 |
| OP03-100 | 🔲 To Do | CHARACTER | trigger: trash 1 life, play this |
| OP03-101 | ⬜ No Effect | CHARACTER |  |
| OP03-102 | 🔲 To Do | CHARACTER | DON x2 on_attack: add 1 life to hand, add deck to life |
| OP03-103 | ⬜ No Effect | CHARACTER |  |
| OP03-104 | 🔲 To Do | CHARACTER | blocker; on_play: look 1 life, place top/bottom |
| OP03-105 | 🔲 To Do | CHARACTER | DON x1 on_attack: trash Trigger, +3000 |
| OP03-106 | ⬜ No Effect | CHARACTER |  |
| OP03-107 | 🔲 To Do | CHARACTER | blocker |
| OP03-108 | 🔲 To Do | CHARACTER | DON x1 continuous: if less life, Double Attack +1000 |
| OP03-109 | 🔲 To Do | CHARACTER | on_play: trash 1 life, add deck card to life |
| OP03-110 | 🔲 To Do | CHARACTER | on_attack: add 1 life to hand, +2000 |
| OP03-111 | ⬜ No Effect | CHARACTER |  |
| OP03-112 | 🔲 To Do | CHARACTER | on_play: look 4, reveal Sanji or Big Mom Pirates card |
| OP03-113 | 🔲 To Do | CHARACTER | on_ko: look 3, reveal Big Mom Pirates card |
| OP03-114 | 🔲 To Do | CHARACTER | on_play: if BM leader, add deck to life, trash opp life |
| OP03-115 | 🔲 To Do | CHARACTER | on_play: trash Trigger, KO cost 1- |
| OP03-116 | 🔲 To Do | CHARACTER | on_play: draw 3, trash 2; trigger |
| OP03-117 | 🔲 To Do | CHARACTER | activate: rest, Charlotte Linlin +1000; trigger |
| OP03-118 | 🔲 To Do | EVENT | counter: +5000 |
| OP03-119 | 🔲 To Do | EVENT | on_play: if less life, KO opp cost 6- |
| OP03-120 | 🔲 To Do | EVENT | on_play: if opp 4+ life, trash opp life |
| OP03-121 | 🔲 To Do | EVENT | on_play: trash 1 life, KO opp cost 5- |
| OP03-122 | 🔲 To Do | CHARACTER | on_play: return cost 6- to hand, draw 2, trash 2 |
| OP03-123 | 🔲 To Do | CHARACTER | on_play: add cost 8- char to life top/bottom |

# Card Effect Status — OP14

| ID | Status | Type | Notes |
|----|--------|------|-------|
| OP14-073 | ✅ Verified | CHARACTER |  |
