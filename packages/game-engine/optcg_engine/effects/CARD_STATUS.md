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

| ID | Name | Type | Status | Notes |
|----|------|------|--------|-------|
| OP02-001 | Edward.Newgate | LEADER | 🔲 To Do | end_of_turn: add 1 life to hand |
| OP02-002 | Monkey.D.Garp | LEADER | 🔲 To Do | on_don_attached: opp char -1 cost |
| OP02-003 | Atmos | CHARACTER | ⬜ No Effect | |
| OP02-004 | Edward.Newgate | CHARACTER | 🔲 To Do | on_play: leader +2000 / on_attack: DON x2 KO ≤3000 |
| OP02-005 | Curly.Dadan | CHARACTER | 🔲 To Do | on_play: look 5, reveal red cost 1 char |
| OP02-006 | Kingdew | CHARACTER | ⬜ No Effect | |
| OP02-007 | Thatch | CHARACTER | ⬜ No Effect | |
| OP02-008 | Jozu | CHARACTER | 🔲 To Do | continuous: DON x1 + WB leader + ≤2 life → Rush |
| OP02-009 | Squard | CHARACTER | 🔲 To Do | on_play: if WB leader, -4000 opp + add life to hand |
| OP02-010 | Dogura | CHARACTER | 🔲 To Do | activate: rest self → play red cost 1 from hand |
| OP02-011 | Vista | CHARACTER | 🔲 To Do | on_play: KO opp ≤3000 power |
| OP02-012 | Blenheim | CHARACTER | 🔲 To Do | blocker |
| OP02-013 | Portgas.D.Ace | CHARACTER | 🔲 To Do | on_play: -3000 to 2 opp chars; Rush if WB leader |
| OP02-014 | Whitey Bay | CHARACTER | 🔲 To Do | continuous: DON x1, attack active chars |
| OP02-015 | Makino | CHARACTER | 🔲 To Do | activate: rest self → red cost 1 char +3000 |
| OP02-016 | Magura | CHARACTER | 🔲 To Do | on_play: red cost 1 char +3000 |
| OP02-017 | Masked Deuce | CHARACTER | 🔲 To Do | on_attack: DON x2, KO opp ≤2000 power |
| OP02-018 | Marco | CHARACTER | 🔲 To Do | blocker; on_ko: trash WB card → play self rested if ≤2 life |
| OP02-019 | Rakuyo | CHARACTER | 🔲 To Do | continuous: DON x1, WB chars +1000 |
| OP02-020 | LittleOars Jr. | CHARACTER | ⬜ No Effect | |
| OP02-021 | Seaquake | EVENT | 🔲 To Do | on_play: if WB leader, KO opp ≤3000 power |
| OP02-022 | Whitebeard Pirates | EVENT | 🔲 To Do | on_play: look 5, reveal WB char; trigger |
| OP02-023 | You May Be a Fool | EVENT | 🔲 To Do | on_play: if ≤3 life, can't add life to hand |
| OP02-024 | Moby Dick | STAGE | 🔲 To Do | continuous: if ≤1 life, WB chars +2000 |
| OP02-025 | Kin'emon | LEADER | 🔲 To Do | activate: if ≤1 char, next Land of Wano cost 3+ costs -1 |
| OP02-026 | Sanji | LEADER | 🔲 To Do | on_play_character: if ≤3 chars, set 2 DON active |
| OP02-027 | Inuarashi | CHARACTER | 🔲 To Do | continuous: if all DON rested, immune to opp removal |
| OP02-028 | Usopp | CHARACTER | ⬜ No Effect | |
| OP02-029 | Carrot | CHARACTER | 🔲 To Do | end_of_turn: set 1 DON active |
| OP02-030 | Kouzuki Oden | CHARACTER | 🔲 To Do | activate: rest 3 DON → set active; on_ko: play green LoW cost 3 |
| OP02-031 | Kouzuki Toki | CHARACTER | 🔲 To Do | continuous: if Oden char, gain Blocker |
| OP02-032 | Shishilian | CHARACTER | 🔲 To Do | on_play: rest 2 DON → set Minks ≤5 active |
| OP02-033 | Jinbe | CHARACTER | ⬜ No Effect | |
| OP02-034 | Tony Tony.Chopper | CHARACTER | 🔲 To Do | on_attack: DON x1, rest opp cost 2 or less |
| OP02-035 | Trafalgar Law | CHARACTER | 🔲 To Do | activate: rest 1 DON, return self → play cost 3 from hand |
| OP02-036 | Nami | CHARACTER | 🔲 To Do | on_play/on_attack: rest 1 DON → look 3, reveal FILM card |
| OP02-037 | Nico Robin | CHARACTER | 🔲 To Do | on_play: play FILM/SHC cost 2 or less from hand |
| OP02-038 | Nekomamushi | CHARACTER | 🔲 To Do | blocker |
| OP02-039 | Franky | CHARACTER | ⬜ No Effect | |
| OP02-040 | Brook | CHARACTER | 🔲 To Do | on_play: play FILM/SHC cost 3 or less from hand |
| OP02-041 | Monkey.D.Luffy | CHARACTER | 🔲 To Do | blocker; on_play: play FILM/SHC cost 4 or less from hand |
| OP02-042 | Yamato | CHARACTER | 🔲 To Do | on_play: rest opp cost 6 or less (treated as Oden) |
| OP02-043 | Roronoa Zoro | CHARACTER | ⬜ No Effect | |
| OP02-044 | Wanda | CHARACTER | 🔲 To Do | on_play: play Minks cost 3 or less from hand |
| OP02-045 | Three Sword Style Oni Giri | EVENT | 🔲 To Do | counter: +6000 to leader; play vanilla char cost 3 or less |
| OP02-046 | Diable Jambe Venaison Shoot | EVENT | 🔲 To Do | on_play: KO opp rested char cost 4 or less |
| OP02-047 | Paradise Totsuka | EVENT | 🔲 To Do | on_play: rest opp char cost 4 or less |
| OP02-048 | Land of Wano | STAGE | 🔲 To Do | activate: trash LoW from hand + rest stage → set 1 DON active |
| OP02-049 | Emporio.Ivankov | LEADER | 🔲 To Do | end_of_turn: if 0 hand, draw 2 |
| OP02-050 | Inazuma | CHARACTER | 🔲 To Do | continuous: if ≤1 hand, +2000; blocker |
| OP02-051 | Emporio.Ivankov | CHARACTER | 🔲 To Do | on_play: draw to 3, play blue Impel Down cost 6 or less |
| OP02-052 | Cabaji | CHARACTER | 🔲 To Do | on_play: if Mohji in play, draw 2 trash 1 |
| OP02-053 | Crocodile | CHARACTER | ⬜ No Effect | |
| OP02-054 | Gecko Moria | CHARACTER | ⬜ No Effect | |
| OP02-055 | Dracule Mihawk | CHARACTER | ⬜ No Effect | |
| OP02-056 | Donquixote Doflamingo | CHARACTER | 🔲 To Do | on_play: look 3 arrange; on_attack: DON x1, trash 1 → place opp ≤1 at bottom |
| OP02-057 | Bartholomew Kuma | CHARACTER | 🔲 To Do | on_play: look 2, reveal Seven Warlords card |
| OP02-058 | Buggy | CHARACTER | 🔲 To Do | on_play: look 5, reveal blue Impel Down card |
| OP02-059 | Boa Hancock | CHARACTER | 🔲 To Do | on_attack: draw 1, trash 1, trash up to 3 more |
| OP02-060 | Mohji | CHARACTER | ⬜ No Effect | |
| OP02-061 | Morley | CHARACTER | 🔲 To Do | on_attack: if ≤1 hand, opp can't use Blocker cost 5 or less |
| OP02-062 | Monkey.D.Luffy | CHARACTER | 🔲 To Do | on_play/on_attack: trash 2 → return cost 4 or less + Double Attack |
| OP02-063 | Mr.1(Daz.Bonez) | CHARACTER | 🔲 To Do | on_play: add blue Event cost 1 from trash |
| OP02-064 | Mr.2.Bon.Kurei | CHARACTER | 🔲 To Do | on_attack: DON x1, trash 1 → place opp ≤2 at bottom; self to bottom |
| OP02-065 | Mr.3(Galdino) | CHARACTER | 🔲 To Do | blocker; end_of_turn: trash 1 → set self active |
| OP02-066 | Impel Down All Stars | EVENT | 🔲 To Do | on_play: trash 2; if Impel Down leader, draw 2 |
| OP02-067 | Arabesque Brick Fist | EVENT | 🔲 To Do | on_play: return opp char cost 4 or less to hand |
| OP02-068 | Gum-Gum Rain | EVENT | 🔲 To Do | counter: may trash 1 → +3000 power |
| OP02-069 | DEATH WINK | EVENT | 🔲 To Do | counter: +6000 to leader; draw to 2 |
| OP02-070 | New Kama Land | STAGE | 🔲 To Do | activate: rest stage; if Ivankov: draw 1, trash 1, trash up to 3 more |
| OP02-071 | Magellan | LEADER | 🔲 To Do | on_don_return: +1000 power this turn |
| OP02-072 | Zephyr | LEADER | 🔲 To Do | on_attack: DON -4 → KO opp ≤3 cost + leader +1000 |
| OP02-073 | Little Sadi | CHARACTER | 🔲 To Do | on_play: play Jailer Beast from hand |
| OP02-074 | Saldeath | CHARACTER | 🔲 To Do | continuous: Blugori gains Blocker |
| OP02-075 | Shiki | CHARACTER | ⬜ No Effect | |
| OP02-076 | Shiryu | CHARACTER | 🔲 To Do | on_play: DON -1 → KO opp cost 1 or less |
| OP02-077 | Solitaire | CHARACTER | ⬜ No Effect | |
| OP02-078 | Daifugo | CHARACTER | 🔲 To Do | on_play: DON -2 → play SMILE cost 3 or less from hand |
| OP02-079 | Douglas Bullet | CHARACTER | 🔲 To Do | on_play: DON -1 → rest opp cost 4 or less |
| OP02-080 | Dobon | CHARACTER | ⬜ No Effect | |
| OP02-081 | Domino | CHARACTER | 🔲 To Do | blocker |
| OP02-082 | Byrnndi World | CHARACTER | 🔲 To Do | activate: DON -8 → +792000 power |
| OP02-083 | Hannyabal | CHARACTER | 🔲 To Do | on_play: look 5, reveal purple Impel Down card |
| OP02-084 | Blugori | CHARACTER | ⬜ No Effect | |
| OP02-085 | Magellan | CHARACTER | 🔲 To Do | on_play: DON -1 → opp returns 1 DON; on_ko: opp returns 2 DON; your_turn: if opp ≤1 life, +1000 |
| OP02-086 | Minokoala | CHARACTER | 🔲 To Do | blocker; on_ko: if Impel Down leader, add 1 DON rested |
| OP02-087 | Minotaur | CHARACTER | 🔲 To Do | Double Attack; on_ko: if Impel Down leader, add 1 DON rested |
| OP02-088 | Sphinx | CHARACTER | ⬜ No Effect | |
| OP02-089 | Judgment of Hell | EVENT | 🔲 To Do | counter: DON -1; give up to 2 opp leader/chars -2000 each |
| OP02-090 | Hydra | EVENT | 🔲 To Do | on_play: DON -1; return opp char to hand |
| OP02-091 | Venom Road | EVENT | 🔲 To Do | on_play: add 1 DON from deck, set active |
| OP02-092 | Impel Down | STAGE | 🔲 To Do | activate: trash 1 + rest stage → look 3, reveal Impel Down card |
| OP02-093 | Smoker | LEADER | 🔲 To Do | activate: DON x1; opp char -1 cost; if cost 0 exists, +1000 |
| OP02-094 | Isuka | CHARACTER | 🔲 To Do | on_attack: DON x1; once per turn: if KO opp, set self active |
| OP02-095 | Onigumo | CHARACTER | 🔲 To Do | continuous: if cost 0 char exists, gain Banish |
| OP02-096 | Kuzan | CHARACTER | 🔲 To Do | on_play: draw 1; on_attack: opp char -4 cost |
| OP02-097 | Komille | CHARACTER | ⬜ No Effect | |
| OP02-098 | Koby | CHARACTER | 🔲 To Do | on_play: may trash 1 → KO opp cost 3 or less |
| OP02-099 | Sakazuki | CHARACTER | 🔲 To Do | on_play: may trash 1 → KO opp cost 5 or less |
| OP02-100 | Jango | CHARACTER | 🔲 To Do | continuous: if Fullbody in play, can't be KO in battle |
| OP02-101 | Strawberry | CHARACTER | 🔲 To Do | on_attack: if cost 0 char exists, opp can't Blocker cost 5 or less |
| OP02-102 | Smoker | CHARACTER | 🔲 To Do | continuous: can't be KO by effects; on_attack: if cost 0, +2000 |
| OP02-103 | Sengoku | CHARACTER | 🔲 To Do | on_attack: DON x1; opp char -2 cost |
| OP02-104 | Sentomaru | CHARACTER | ⬜ No Effect | |
| OP02-105 | Tashigi | CHARACTER | 🔲 To Do | on_attack: DON x1; opp char -3 cost |
| OP02-106 | Tsuru | CHARACTER | 🔲 To Do | on_play: opp char -2 cost |
| OP02-107 | Doberman | CHARACTER | ⬜ No Effect | |
| OP02-108 | Donquixote Rosinante | CHARACTER | 🔲 To Do | blocker |
| OP02-109 | Jaguar.D.Saul | CHARACTER | ⬜ No Effect | |
| OP02-110 | Hina | CHARACTER | 🔲 To Do | blocker; on_block: opp cost 6 or less can't attack this turn |
| OP02-111 | Fullbody | CHARACTER | 🔲 To Do | on_attack: if Jango in play, +3000 power |
| OP02-112 | Bell-mere | CHARACTER | 🔲 To Do | activate: rest self → opp char -1 cost + own leader/char +1000 |
| OP02-113 | Helmeppo | CHARACTER | 🔲 To Do | on_attack: opp char -2 cost; if cost 0, +2000; trigger |
| OP02-114 | Borsalino | CHARACTER | 🔲 To Do | continuous (opp turn): +1000 + can't KO by effects; blocker |
| OP02-115 | Monkey.D.Garp | CHARACTER | 🔲 To Do | on_attack: DON x2; KO opp cost 0 char |
| OP02-116 | Yamakaji | CHARACTER | ⬜ No Effect | |
| OP02-117 | Ice Age | EVENT | 🔲 To Do | on_play: opp char -5 cost |
| OP02-118 | Yasakani Sacred Jewel | EVENT | 🔲 To Do | counter: may trash 1 → chosen char can't be KO in battle |
| OP02-119 | Meteor Volcano | EVENT | 🔲 To Do | on_play: KO opp char cost 1 or less |
| OP02-120 | Uta | CHARACTER | 🔲 To Do | on_play: DON -2 → leader and all chars +1000 until next turn |
| OP02-121 | Kuzan | CHARACTER | 🔲 To Do | continuous: all opp chars -5 cost; on_play: KO opp cost 0 char |
