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
| OP02-004 | ⚠ Needs Fix | CHARACTER | The when attacking with 2 don works as inteded. But it is not giving the leader +2000 power until the start of the players next turn.  |
| OP02-005 | ✅ Verified | CHARACTER | on_play: look 5, reveal red cost 1 char |
| OP02-006 | ✅ Verified | CHARACTER |  |
| OP02-007 | ✅ Verified | CHARACTER |  |
| OP02-008 | ⚠ Needs Fix | CHARACTER | This card has conditional rush, when given don and when the leader's type is "Whitebeard Pirates", but he has rush regardless. Fix this, and make the leader edward newgate so we can test.  |
| OP02-009 | ⚠ Needs Fix | CHARACTER | Make the leader edward newgate in the simulation so we can test.  |
| OP02-010 | ✅ Verified | CHARACTER | activate: rest self → play red cost 1 from hand |
| OP02-011 | ✅ Verified | CHARACTER | on_play: KO opp ≤3000 power |
| OP02-012 | ✅ Verified | CHARACTER | blocker |
| OP02-013 | ⚠ Needs Fix | CHARACTER | It shows that Katakuri had -3000 power but in the battle on the front end it showed that he was still at his default power.  |
| OP02-014 | ✅ Verified | CHARACTER | continuous: DON x1, attack active chars |
| OP02-015 | ✅ Verified | CHARACTER | activate: rest self → red cost 1 char +3000 |
| OP02-016 | ✅ Verified | CHARACTER | on_play: red cost 1 char +3000 |
| OP02-017 | ✅ Verified | CHARACTER | on_attack: DON x2, KO opp ≤2000 power |
| OP02-018 | ⚠ Needs Fix | CHARACTER | When this card dies, I should be able to trash a card with "Whitebeard Pirates" in it to play the card from the trash.  |
| OP02-019 | ✅ Verified | CHARACTER | continuous: DON x1, WB chars +1000 |
| OP02-020 | ✅ Verified | CHARACTER |  |
| OP02-021 | ⚠ Needs Fix | EVENT | Leader needs to be Edward Newgate so I can test.  |
| OP02-022 | ✅ Verified | EVENT | on_play: look 5, reveal WB char; trigger |
| OP02-023 | ⚠ Needs Fix | EVENT | Leader needs to be Edward Newgate so I can test.  |
| OP02-024 | ⚠ Needs Fix | STAGE | Leader needs to be Edward Newgate so I can test.  |
| OP02-025 | 🔲 To Do | LEADER | activate: if ≤1 char, next Land of Wano cost 3+ costs -1 |
| OP02-026 | 🔲 To Do | LEADER | on_play_character: if ≤3 chars, set 2 DON active |
| OP02-027 | 🔲 To Do | CHARACTER | continuous: if all DON rested, immune to opp removal |
| OP02-028 | ✅ Verified | CHARACTER |  |
| OP02-029 | ⚠ Needs Fix | CHARACTER | At the end of the turn 1 DON!! should be restanded |
| OP02-030 | ⚠ Needs Fix | CHARACTER | It let's me activate but I should have to rest 3 don to activate. Also, when the character is active again the can_attack should be set to true again. There is also no option to play a green land of wano card with a cost of 3 or less from the deck.   |
| OP02-031 | ⚠ Needs Fix | CHARACTER | This card should only have blocker if there is a Kozuki Oden character on the field. It has blocker by default.  |
| OP02-032 | ⚠ Needs Fix | CHARACTER | When this card is played I should be prompted to rest 2 DON!! and set 1 minks type character with a cost of 5 or less as active.  |
| OP02-033 | ✅ Verified | CHARACTER |  |
| OP02-034 | ✅ Verified | CHARACTER | on_attack: DON x1, rest opp cost 2 or less |
| OP02-035 | ⚠ Needs Fix | CHARACTER | It should rest 1 DON when I activate to return this card to the owners hand and then prompt me to play a 3 cost or less from hand.  |
| OP02-036 | ⚠ Needs Fix | CHARACTER | This card should search top 3 for a film type card other than nami and add it to hand.  I should be prompted if I want to rest 1 DON and use that search effect though. I should only be able to search if you rest 1 DON!! |
| OP02-037 | ✅ Verified | CHARACTER | on_play: play FILM/SHC cost 2 or less from hand |
| OP02-038 | ✅ Verified | CHARACTER | blocker |
| OP02-039 | ✅ Verified | CHARACTER |  |
| OP02-040 | ✅ Verified | CHARACTER | on_play: play FILM/SHC cost 3 or less from hand |
| OP02-041 | ✅ Verified | CHARACTER | blocker; on_play: play FILM/SHC cost 4 or less from hand |
| OP02-042 | ✅ Verified | CHARACTER | on_play: rest opp cost 6 or less (treated as Oden) |
| OP02-043 | ✅ Verified | CHARACTER |  |
| OP02-044 | ⚠ Needs Fix | CHARACTER | It should prompt me to play up to 1 Minks type not do it automatically. I should have the option to choose 0.  |
| OP02-045 | 🔲 To Do | EVENT | counter: +6000 to leader; play vanilla char cost 3 or less |
| OP02-046 | ✅ Verified | EVENT | on_play: KO opp rested char cost 4 or less |
| OP02-047 | ✅ Verified | EVENT | on_play: rest opp char cost 4 or less |
| OP02-048 | ⚠ Needs Fix | STAGE | It should prompt me if I want to trash 1 Land of Wano type card from hand and rest the stage. If I do, then it should set up to 1 DON!! cards as active.  |
| OP02-049 | ✅ Verified | LEADER | end_of_turn: if 0 hand, draw 2 |
| OP02-050 | ✅ Verified | CHARACTER | continuous: if ≤1 hand, +2000; blocker |
| OP02-051 | ✅ Verified | CHARACTER | on_play: draw to 3, play blue Impel Down cost 6 or less |
| OP02-052 | ✅ Verified | CHARACTER | on_play: if Mohji in play, draw 2 trash 1 |
| OP02-053 | ✅ Verified | CHARACTER |  |
| OP02-054 | ✅ Verified | CHARACTER |  |
| OP02-055 | ✅ Verified | CHARACTER |  |
| OP02-056 | ✅ Verified | CHARACTER | Does not search the top 3, the when attacking effect is coded correctly. |
| OP02-057 | ✅ Verified | CHARACTER | on_play: look 2, reveal Seven Warlords card |
| OP02-058 | ⚠ Needs Fix | CHARACTER | It does not let me add Impel Down characters other than Buggy to my hand it just immediately lets me start placing them at bottom of deck.  |
| OP02-059 | ⚠ Needs Fix | CHARACTER | WHen it says trash up to 3 cards from hand, I should be able to select how many cards I want to trash. This also gives me to option to trash 0 cards, so I can choose to trash none.  |
| OP02-060 | ✅ Verified | CHARACTER |  |
| OP02-061 | ⚠ Needs Fix | CHARACTER | Blockers with a cost of 5 or less should not be able to block when this card and ONLY this card attacks and the player has less than 1 card in hand. Currently they can still block with characters cost 5 or less.  |
| OP02-062 | ⚠ Needs Fix | CHARACTER | I should be prompted to select which 2 cards I want to trash in order to use the effect, and then I get to select a 4 cost or less to return to hand.  |
| OP02-063 | ⚠ Needs Fix | CHARACTER | We need a blue event card with cost of 1 or less in the trash so we can test.  |
| OP02-064 | ⚠ Needs Fix | CHARACTER | It does do what the effect says, but it should prompt me to choose a card to trash from hand. Also, this card should get sent to the bottom of the deck at the end of the battle.  |
| OP02-065 | ⚠ Needs Fix | CHARACTER | When I end turn it should prompt and ask me if I want to trash a card from hand and set this character back as active.  |
| OP02-066 | ⚠ Needs Fix | EVENT | This card's effect is not programmed. It does nothing when I select it.  |
| OP02-067 | ✅ Verified | EVENT | on_play: return opp char cost 4 or less to hand |
| OP02-068 | ⚠ Needs Fix | EVENT | It should prompt me to select a card to trash to use the effect of this card.  |
| OP02-069 | 🔲 To Do | EVENT | counter: +6000 to leader; draw to 2 |
| OP02-070 | 🔲 To Do | STAGE | activate: rest stage; if Ivankov: draw 1, trash 1, trash up to 3 more |
| OP02-071 | 🔲 To Do | LEADER | on_don_return: +1000 power this turn |
| OP02-072 | 🔲 To Do | LEADER | on_attack: DON -4 → KO opp ≤3 cost + leader +1000 |
| OP02-073 | 🔲 To Do | CHARACTER | on_play: play Jailer Beast from hand |
| OP02-074 | 🔲 To Do | CHARACTER | continuous: Blugori gains Blocker |
| OP02-075 | ⬜ No Effect | CHARACTER | |
| OP02-076 | 🔲 To Do | CHARACTER | on_play: DON -1 → KO opp cost 1 or less |
| OP02-077 | ✅ Verified | CHARACTER |  |
| OP02-078 | 🔲 To Do | CHARACTER | on_play: DON -2 → play SMILE cost 3 or less from hand |
| OP02-079 | 🔲 To Do | CHARACTER | on_play: DON -1 → rest opp cost 4 or less |
| OP02-080 | ✅ Verified | CHARACTER |  |
| OP02-081 | ✅ Verified | CHARACTER | blocker |
| OP02-082 | 🔲 To Do | CHARACTER | activate: DON -8 → +792000 power |
| OP02-083 | ✅ Verified | CHARACTER | on_play: look 5, reveal purple Impel Down card |
| OP02-084 | ✅ Verified | CHARACTER |  |
| OP02-085 | 🔲 To Do | CHARACTER | on_play: DON -1 → opp returns 1 DON; on_ko: opp returns 2 DON; your_turn: if opp ≤1 life, +1000 |
| OP02-086 | 🔲 To Do | CHARACTER | blocker; on_ko: if Impel Down leader, add 1 DON rested |
| OP02-087 | 🔲 To Do | CHARACTER | Double Attack; on_ko: if Impel Down leader, add 1 DON rested |
| OP02-088 | ⬜ No Effect | CHARACTER | |
| OP02-089 | 🔲 To Do | EVENT | counter: DON -1; give up to 2 opp leader/chars -2000 each |
| OP02-090 | 🔲 To Do | EVENT | on_play: DON -1; return opp char to hand |
| OP02-091 | 🔲 To Do | EVENT | on_play: add 1 DON from deck, set active |
| OP02-092 | 🔲 To Do | STAGE | activate: trash 1 + rest stage → look 3, reveal Impel Down card |
| OP02-093 | 🔲 To Do | LEADER | activate: DON x1; opp char -1 cost; if cost 0 exists, +1000 |
| OP02-094 | 🔲 To Do | CHARACTER | on_attack: DON x1; once per turn: if KO opp, set self active |
| OP02-095 | 🔲 To Do | CHARACTER | continuous: if cost 0 char exists, gain Banish |
| OP02-096 | ✅ Verified | CHARACTER | on_play: draw 1; on_attack: opp char -4 cost |
| OP02-097 | ✅ Verified | CHARACTER |  |
| OP02-098 | 🔲 To Do | CHARACTER | on_play: may trash 1 → KO opp cost 3 or less |
| OP02-099 | 🔲 To Do | CHARACTER | on_play: may trash 1 → KO opp cost 5 or less |
| OP02-100 | 🔲 To Do | CHARACTER | continuous: if Fullbody in play, can't be KO in battle |
| OP02-101 | 🔲 To Do | CHARACTER | on_attack: if cost 0 char exists, opp can't Blocker cost 5 or less |
| OP02-102 | 🔲 To Do | CHARACTER | continuous: can't be KO by effects; on_attack: if cost 0, +2000 |
| OP02-103 | ✅ Verified | CHARACTER | on_attack: DON x1; opp char -2 cost |
| OP02-104 | ⬜ No Effect | CHARACTER | |
| OP02-105 | ✅ Verified | CHARACTER | on_attack: DON x1; opp char -3 cost |
| OP02-106 | ✅ Verified | CHARACTER | on_play: opp char -2 cost |
| OP02-107 | ✅ Verified | CHARACTER |  |
| OP02-108 | ✅ Verified | CHARACTER | blocker |
| OP02-109 | ✅ Verified | CHARACTER |  |
| OP02-110 | 🔲 To Do | CHARACTER | blocker; on_block: opp cost 6 or less can't attack this turn |
| OP02-111 | 🔲 To Do | CHARACTER | on_attack: if Jango in play, +3000 power |
| OP02-112 | 🔲 To Do | CHARACTER | activate: rest self → opp char -1 cost + own leader/char +1000 |
| OP02-113 | 🔲 To Do | CHARACTER | on_attack: opp char -2 cost; if cost 0, +2000; trigger |
| OP02-114 | 🔲 To Do | CHARACTER | continuous (opp turn): +1000 + can't KO by effects; blocker |
| OP02-115 | 🔲 To Do | CHARACTER | on_attack: DON x2; KO opp cost 0 char |
| OP02-116 | ✅ Verified | CHARACTER |  |
| OP02-117 | ✅ Verified | EVENT | on_play: opp char -5 cost |
| OP02-118 | 🔲 To Do | EVENT | counter: may trash 1 → chosen char can't be KO in battle |
| OP02-119 | ✅ Verified | EVENT | on_play: KO opp char cost 1 or less |
| OP02-120 | 🔲 To Do | CHARACTER | on_play: DON -2 → leader and all chars +1000 until next turn |
| OP02-121 | 🔲 To Do | CHARACTER | continuous: all opp chars -5 cost; on_play: KO opp cost 0 char |
