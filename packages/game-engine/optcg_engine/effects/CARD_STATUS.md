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
| OP01-008 | ✅ Verified | CHARACTER | ⚠ Needs Fix | [On Play] You may add 1 card from your Life area to your hand: This Ch… | I should be prompted if I want to take 1 card from my life to my hand, if I choose to do so then this card should get rush.  |
| OP01-009 | ✅ Verified | CHARACTER | The trigger activates correctly, but when I attack the opponents life THEY should be getting the trigger. So, Opponent would play out the carrot in this testing. (I know it should not be allowed regularly since the color does not match the leader) | [Trigger] Play this card. | Impl exists: trigger |
| OP01-010 | ✅ Verified | CHARACTER | ✅ Verified |  |  |
| OP01-011 | ✅ Verified | CHARACTER | Player should be prompted for which card they walk to place at bottom of deck. | [On Play] You may place 1 card from your hand at the bottom of your de… | Impl exists: on_play |
| OP01-012 | ✅ Verified | CHARACTER | ✅ Verified |  |  |
| OP01-013 | ✅ Verified | CHARACTER | ⚠ Needs Fix | [Activate: Main] [Once Per Turn] You may add 1 card from your Life are… | This effect should only be able to be done once per turn, it currently let's me do it as much as I want.  |
| OP01-014 | ✅ Verified | CHARACTER | Effect works as intended. A change to remember for the remainder of the project though is that when a character blocks it should become rested. It will refresh when we enter refresh phase (Start of turn) UNLESS there is an effect preventing it from restanding to active. | [Blocker] (After your opponent declares an attack, you may rest this c… | Impl exists: blocker, on_block |
| OP01-015 | ✅ Verified | CHARACTER | Only seeing Error: Invalid choice response in Game Log, I am at least being prompted which is good, but not the correct effect at the end. The card I choose to trash is not being trashed and the card I am taking from trash to hand is not working either. | [DON!! x1] [When Attacking] You may trash 1 card from your hand: Add u… | Impl exists: on_attack |
| OP01-016 | ✅ Verified | CHARACTER | Still cannot choose the order that I want to send the cards to the bottom of the deck in. | [On Play] Look at 5 cards from the top of your deck; reveal up to 1 {S… | Impl exists: on_play |
| OP01-017 | ✅ Verified | CHARACTER | For testing this card needs to be in play already and opponent should have a 3000 power character. | [DON!! x1] [When Attacking] K.O. up to 1 of your opponent's Characters… | Impl exists: on_attack |
| OP01-018 | ✅ Verified | CHARACTER | ✅ Verified |  |  |
| OP01-019 | ✅ Verified | CHARACTER | The card effect is working as intended, somehow your dumbass has not figured out that DON should only give extra power when it is that card's owner's turn. When they pass the buff from Don cards goes away. | [Blocker] (After your opponent declares an attack, you may rest this c… | Impl exists: blocker, continuous |
| OP01-020 | ✅ Verified | CHARACTER | ✅ Verified | [Activate: Main] You may rest this Character: Up to 1 of your Leader o… | Impl exists: activate |
| OP01-021 | ✅ Verified | CHARACTER | This card should be able to attack ACTIVE characters when he has a Don on him, however this is not the case. Only the leader is an option to attack. | [DON!! x1] This Character can also attack your opponent's active Chara… | Impl exists: continuous |
| OP01-022 | ✅ Verified | CHARACTER | The player should be prompted and allowed to select who to give -2000 to. But other than that it works. | [DON!! x1] [When Attacking] Give up to 2 of your opponent's Characters… | Impl exists: on_attack |
| OP01-023 | ✅ Verified | CHARACTER | ✅ Verified |  |  |
| OP01-024 | ✅ Verified | CHARACTER | This card can still be KOd in battle by Strike Attribute Characters. | [DON!! x2] This Character cannot be K.O.'d in battle by ＜Strike＞ attri… | Impl exists: continuous, activate |
| OP01-025 | ✅ Verified | CHARACTER | ✅ Verified | [Rush] (This card can attack on the turn in which it is played.) | Impl exists: continuous |
| OP01-026 | ✅ Verified | EVENT | The coutner part of this card worked correctly. There was no prompt given to KO the character with 4000 power or less though. | [Counter] Up to 1 of your Leader or Character cards gains +4000 power … | Impl exists: counter |
| OP01-027 | ✅ Verified | EVENT | ✅ Verified | [Main] Give up to 1 of your opponent's Characters −10000 power during … | Impl exists: on_play |
| OP01-028 | ✅ Verified | EVENT | === Turn 2: Opponent (DON: 5) === Opponent's Atlas (Power: 6000) attacks Monkey.D.Luffy! [COUNTER EVENT] Tester plays Green Star Rafflesia (Cost 1 DON, +0) Atlas gets -2000 power Karoo added to hand. This is the game log, I should not be taking damage in this interaction, I gave the Atlas -2000 power. | [Counter] Give up to 1 of your opponent's Leader or Character cards −2… | Impl exists: counter |
| OP01-029 | ✅ Verified | EVENT | Why is this being buffed to 11000? It should not give +2000 then +4000 it should be +2000 then another +2000 when the player has 2 or less life. | [Counter] Up to 1 of your Leader or Character cards gains +2000 power … | Impl exists: counter |
| OP01-030 | ✅ Verified | EVENT | For some reason it only shows the top 4 cards not 5. But that part does work fine. | [Main] Look at 5 cards from the top of your deck; reveal up to 1 {Stra… | Impl exists: on_play |
| OP01-031 | ✅ Verified | LEADER | Leader works, but again the player should have the option to select which card they want to trash. | [Activate: Main] [Once Per Turn] You can trash 1 {Land of Wano} type c… | Impl exists: activate |
| OP01-032 | ✅ Verified | CHARACTER | The +2000 power should be IMMEDIATE when there is a 2nd rested character. The issue I am seeing is that when a 5000 power character attacks Ashura Doji he is not getting the +2000 to help him defend. | [DON!! x1] If your opponent has 2 or more rested Characters, this Char… | Impl exists: continuous |
| OP01-033 | ✅ Verified | CHARACTER | ✅ Verified | [On Play] Rest up to 1 of your opponent's Characters with a cost of 4 … | Impl exists: on_play |
| OP01-034 | ✅ Verified | CHARACTER | ✅ Verified | [DON!! x2] [When Attacking] Set up to 1 of your DON!! cards as active. | Impl exists: on_attack |
| OP01-035 | ✅ Verified | CHARACTER | ✅ Verified | [DON!! x1] [When Attacking] [Once Per Turn] Rest up to 1 of your oppon… | Impl exists: on_attack |
| OP01-036 | ✅ Verified | CHARACTER | ✅ Verified |  |  |
| OP01-037 | ✅ Verified | CHARACTER | ✅ Verified |  | Impl exists: trigger |
| OP01-038 | ✅ Verified | CHARACTER | The effect works as intended, 1 slight problem. The opponent should not see the hand, they should have to choose the card to trash without knowing what it is. | [DON!! x1] [When Attacking] K.O. up to 1 of your opponent's rested Cha… | Impl exists: on_attack, on_ko |
| OP01-039 | ✅ Verified | CHARACTER | On Block there is no additional draw even though there are 3 or more characters on field. Also keep in mind IMMEDIATELY when the block is done is when that effect should take place. | [Blocker] (After your opponent declares an attack, you may rest this c… | Impl exists: blocker, on_block |
| OP01-040 | ✅ Verified | CHARACTER | ✅ Verified | [On Play] If your Leader is [Kouzuki Oden], play up to 1 {The Akazaya … | Impl exists: on_play, on_attack |
| OP01-041 | ✅ Verified | CHARACTER | For this testing make it so that the search has Land of Wano type cards in it. | [Activate: Main] ➀ (You may rest the specified number of DON!! cards i… | Impl exists: activate |
| OP01-042 | ✅ Verified | CHARACTER | Card effect is working, but the player should be prompted to choose a character to restand (set as active again). | [On Play] ③ (You may rest the specified number of DON!! cards in your … | Impl exists: on_play |
| OP01-043 | ✅ Verified | CHARACTER | ✅ Verified |  |  |
| OP01-044 | ✅ Verified | CHARACTER | ✅ Verified | [Blocker] (After your opponent declares an attack, you may rest this c… | Impl exists: blocker, on_play |
| OP01-045 | ✅ Verified | CHARACTER | ✅ Verified |  |  |
| OP01-046 | ✅ Verified | CHARACTER | Effect did not work at all. | [DON!! x1] [When Attacking] If your Leader is [Kouzuki Oden], set up t… | Impl exists: on_attack |
| OP01-047 | ✅ Verified | CHARACTER | It is letting me pick up a character but it wont let me do the 2nd part where I get to play a 3 cost or less from hand. Also when I pick up the card to hand it is not coming to hand it jsut disappears. | [Blocker] (After your opponent declares an attack, you may rest this c… | Impl exists: blocker, on_play |
| OP01-048 | ✅ Verified | CHARACTER | ✅ Verified | [On Play] Rest up to 1 of your opponent's Characters with a cost of 3 … | Impl exists: on_play |
| OP01-049 | ✅ Verified | CHARACTER | ✅ Verified | [DON!! x1] [When Attacking] Play up to 1 {Heart Pirates} type Characte… | Impl exists: on_attack |
| OP01-050 | ✅ Verified | CHARACTER | ✅ Verified | [Blocker] (After your opponent declares an attack, you may rest this c… | Impl exists: blocker, on_play |
| OP01-051 | ✅ Verified | CHARACTER | When this character has a DON attached to it, the enemy can ONLY attack this card but it still let's me choose other targets. | [DON!! x1] [Opponent's Turn] If this Character is rested, your opponen… | Impl exists: continuous, activate |
| OP01-052 | ✅ Verified | CHARACTER | ✅ Verified | [When Attacking] [Once Per Turn] If you have 2 or more rested Characte… | Impl exists: on_attack |
| OP01-053 | ✅ Verified | CHARACTER | ✅ Verified |  |  |
| OP01-054 | ✅ Verified | CHARACTER | ✅ Verified | [On Play] K.O. up to 1 of your opponent's rested Characters with a cos… | Impl exists: on_play |
| OP01-055 | ✅ Verified | EVENT | No effect at all | [Main] You may rest 2 of your Characters: Draw 2 cards. | Impl exists: on_play |
| OP01-056 | ✅ Verified | EVENT | ✅ Verified | [Main] K.O. up to 2 of your opponent's rested Characters with a cost o… | Impl exists: on_play |
| OP01-057 | ✅ Verified | EVENT | At least in this instance the counter effect is being counted twice: Opponent's Charlotte Cracker (Power: 5000) attacks Sanji! [COUNTER EVENT] Tester plays Paradise Waterfall (Cost 1 DON, +2000) Paradise Waterfall: Sanji gains +2000 power Sanji was set active Charlotte Cracker's attack is defended (Defense: 8000). This should not be the case now and I hope this is not an issue with the other events. Please let me know if it is an issue across multiple effects or jsut with this card. | [Counter] Up to 1 of your Leader or Character cards gains +2000 power … | Impl exists: counter |
| OP01-058 | ✅ Verified | EVENT | Player is not prompted to rest a 4 cost or less when using this counter. But the +4000 is working as expected. | [Counter] Up to 1 of your Leader or Character cards gains +4000 power … | Impl exists: counter |
| OP01-059 | ✅ Verified | EVENT | Put Land of Wano characters in this board so I can test this card. | [Main] You may trash 1 {Land of Wano} type card from your hand: Set up… | Impl exists: on_play |
| OP01-060 | ✅ Verified | LEADER | If the top card is NOT valid, it should still show what card is at the top. And it does not get put to the bottom of the deck it just remains there and cannot be played out. There should not be any bottom decking with this leader effect. | [DON!! x2] [When Attacking] ➀ (You may rest the specified number of DO… | Impl exists: on_attack |
| OP01-061 | ✅ Verified | LEADER | I am KOing a character with DON on leader, and the DON is not being added as active still. | [DON!! x1] [Your Turn] [Once Per Turn] When your opponent's Character … | Impl exists: on_opponent_ko |
| OP01-062 | ✅ Verified | LEADER | Even on the opponents turn if I use a counter event, I should still draw 1 card if I have less than 4 in hand. | [DON!! x1] When you activate an Event, you may draw 1 card if you have… | Impl exists: on_event |
| OP01-063 | ✅ Verified | CHARACTER | The game log says: "=== Turn 1: Tester (DON: 1) === Both players ready. Game starting! Tester attaches 1 DON to Arlong. Arlong: Opponent reveals Thunder Bolt (EVENT) Arlong: Placed 1 of Tester's Life at bottom of deck" but the life is not actually being placed to the bottom of the deck, the opponent still has 4 life. | [DON!! x1] [Activate: Main] You may rest this Character: Choose 1 card… | Impl exists: activate |
| OP01-064 | ✅ Verified | CHARACTER | Effect does nothing at all | [DON!! x1] [When Attacking] You may trash 1 card from your hand: Retur… | Impl exists: on_attack |
| OP01-065 | ✅ Verified | CHARACTER | ✅ Verified |  |  |
| OP01-066 | ✅ Verified | CHARACTER | ✅ Verified |  |  |
| OP01-067 | ✅ Verified | CHARACTER | Fixed: cost=0 DON spending loop bug was already fixed but server needed restart (uvicorn --reload only watches backend dir, not game-engine package). | [Banish] (When this card deals damage, the target card is trashed with… | Impl exists: continuous |
| OP01-068 | ✅ Verified | CHARACTER | This card is still dealing double attack even with less than 5 cards in hand. | [Your Turn] This Character gains [Double Attack] if you have 5 or more… | Impl exists: continuous |
| OP01-069 | ✅ Verified | CHARACTER | On KO effect is not doing anything | [On K.O.] Play up to 1 [Smiley] from your deck, then shuffle your deck… | Impl exists: on_ko |
| OP01-070 | ✅ Verified | CHARACTER | ✅ Verified | [On Play] Place up to 1 Character with a cost of 7 or less at the bott… | Impl exists: on_play |
| OP01-071 | ✅ Verified | CHARACTER | ✅ Verified | [On Play] Place up to 1 Character with a cost of 3 or less at the bott… | Impl exists: on_play |
| OP01-072 | ✅ Verified | CHARACTER | Effect for the card works great, problem is with core game engine. Don only gives the card power on Your Turn, when the player passes power from Don goes away. i.e, Smiley has 1000 power, on his turn if DON is attached he gets power from the don. When turn is passed that DON no longer gives power. | [DON!! x1] [Your Turn] This Character gains +1000 power for every card… | Impl exists: continuous |
| OP01-073 | ✅ Verified | CHARACTER | I can now choose the top or bottom but I cannot choose the order that I want to rearrange them to. | [Blocker] (After your opponent declares an attack, you may rest this c… | Impl exists: blocker, on_play |
| OP01-074 | ✅ Verified | CHARACTER | The on KO is working, but this card is not being detected as a blocker. | [Blocker] (After your opponent declares an attack, you may rest this c… | Impl exists: blocker, on_ko |
| OP01-075 | ✅ Verified | CHARACTER | This blocker is not being detected as a blocker. | Under the rules of this game, you may have any number of this card in … | Impl exists: blocker |
| OP01-076 | ✅ Verified | CHARACTER | ✅ Verified |  |  |
| OP01-077 | ✅ Verified | CHARACTER | I can now choose the top or bottom of the deck but I cannot choose the order to rearrange them to now. | [On Play] Look at 5 cards from the top of your deck and place them at … | Impl exists: on_play |
| OP01-078 | ✅ Verified | CHARACTER | Two problems I am noticing so far. 1: WHen I attack while having DON attached I should draw 1 card but it is drawing 2. 2: This card is not being detected as a blocker. | [Blocker] (After your opponent declares an attack, you may rest this c… | Impl exists: on_play |
| OP01-079 | ✅ Verified | CHARACTER | 1. We need to ensure that there is an event card in trash so I can test that effect.  Also, when I block this card has the wrong effect, it is making me trash 2 cards for some reason. | [Blocker] (After your opponent declares an attack, you may rest this c… | Impl exists: blocker, on_block |
| OP01-080 | ✅ Verified | CHARACTER | ✅ Verified | [On K.O.] Draw 1 card. | Impl exists: on_ko |
| OP01-081 | ✅ Verified | CHARACTER | ✅ Verified |  |  |
| OP01-082 | ✅ Verified | CHARACTER | ✅ Verified |  | Impl exists: trigger |
| OP01-083 | ✅ Verified | CHARACTER | Make it so that only events are in trash so I can test this card. | [DON!! x1] [Your Turn] If your Leader has the {Baroque Works} type, th… | Impl exists: continuous |
| OP01-084 | ✅ Verified | CHARACTER | Ensure that there is a Baroque Works type event in the top 5 so I can test this card correctly. | [DON!! x1] [When Attacking] Look at 5 cards from the top of your deck;… | Impl exists: on_attack |
| OP01-085 | ✅ Verified | CHARACTER | I am choosing the character that cannot attack, but it is still allowing that character to attack when I pass the turn. | [On Play] If your Leader has the {Baroque Works} type, select up to 1 … | Impl exists: on_play |
| OP01-086 | ✅ Verified | EVENT | This effect works almost as intended. It let's me return an OPPONENTS cost of 3 or less to hand if it is active  - this is correct. I should also be given the option to return one of my OWN characters that are active with 3 cost or less as well. | [Counter] Up to 1 of your Leader or Character cards gains +4000 power … | Impl exists: counter |
| OP01-087 | ✅ Verified | EVENT | ✅ Verified | [Counter] Play up to 1 {Baroque Works} type Character card with a cost… | Impl exists: counter |
| OP01-088 | ✅ Verified | EVENT | I can now choose the top or bottom but I cannot choose the order that I want to rearrange them to. | [Counter] Up to 1 of your Leader or Character cards gains +2000 power … | Impl exists: counter |
| OP01-089 | ✅ Verified | EVENT | ✅ Verified | [Counter] If your Leader has the {The Seven Warlords of the Sea} type,… | Impl exists: counter |
| OP01-090 | ✅ Verified | EVENT | ✅ Verified | [Main] Look at 5 cards from the top of your deck; reveal up to 1 {Baro… | Impl exists: on_play |
| OP01-091 | ✅ Verified | LEADER | ✅ Verified | [Your Turn] If you have 10 DON!! cards on your field, give all of your… | Impl exists: continuous |
| OP01-092 | ✅ Verified | CHARACTER | ✅ Verified |  |  |
| OP01-093 | ✅ Verified | CHARACTER | This card automatically chooses to rest 1 more DON for the on play effect, I should be prompted if I want to do this. If I do I should gain 1 DON card rested. I am not gaining the extra don. | [On Play] ① (You may rest the specified number of DON!! cards in your … | Impl exists: on_play |
| OP01-094 | ✅ Verified | CHARACTER | Effect seems to be working, but cannot tell for sure, for testing the leader needs to be an Animal Kingdom Pirates type. | [On Play] DON!! −6 (You may return the specified number of DON!! cards… | Impl exists: on_play |
| OP01-095 | ✅ Verified | CHARACTER | ✅ Verified | [On Play] Draw 1 card if you have 8 or more DON!! cards on your field. | Impl exists: on_play |
| OP01-096 | ✅ Verified | CHARACTER | I am not being given the option to choose which don I want to return so it is automatically returning the active don. | [On Play] DON!! −2 (You may return the specified number of DON!! cards… | Impl exists: on_play |
| OP01-097 | ✅ Verified | CHARACTER | ✅ Verified | [On Play] DON!! −1 (You may return the specified number of DON!! cards… | Impl exists: on_play |
| OP01-098 | ✅ Verified | CHARACTER | Fixed: was searching deck by card name instead of card_origin (Type field) for SMILE. Changed to check card_origin for 'smile'. | [On Play] Reveal up to 1 [Artificial Devil Fruit SMILE] from your deck… | Impl exists: on_play |
| OP01-099 | ✅ Verified | CHARACTER | Kurozumi Clan characters other than Kurozumi Semimaru can still get KOd in battle. This should not be the case with Kurozumi Semimaru is in play. | {Kurozumi Clan} type Characters other than your [Kurozumi Semimaru] ca… | Impl exists: on_play |
| OP01-100 | ✅ Verified | CHARACTER | ✅ Verified | [Blocker] (After your opponent declares an attack, you may rest this c… | Impl exists: on_attack |
| OP01-101 | ✅ Verified | CHARACTER | The card is letting me trash 1 from hand but I am not gaining the 1 DON!! card from the DON!! deck rested. | [DON!! x1] [When Attacking] You may trash 1 card from your hand: Add u… | Impl exists: on_attack |
| OP01-102 | ✅ Verified | CHARACTER | When I attack I am not prompted to DON!! -1 if I want to. So I do not know if the opponent is prompted to trash 1 card from their hand. | [When Attacking] DON!! −1 (You may return the specified number of DON!… | Impl exists: on_play |
| OP01-103 | ✅ Verified | CHARACTER | ✅ Verified |  |  |
| OP01-104 | ✅ Verified | CHARACTER | The card is a trigger and it is prompting me to use trigger, but when I select to play the card and activate the trigger it is not playing onto the field. |  | Impl exists: blocker |
| OP01-105 | ✅ Verified | CHARACTER | This card is revealing MY own hand when it should reveal the opponents. | [On Play] Choose 2 cards from your opponent's hand; your opponent reve… | Impl exists: on_play |
| OP01-106 | ✅ Verified | CHARACTER | When I play the card I am not gaining 1 DON!! card from the DON!! deck. | [On Play] Add up to 1 DON!! card from your DON!! deck and rest it. | Impl exists: on_play |
| OP01-107 | ✅ Verified | CHARACTER | ✅ Verified |  |  |
| OP01-108 | ✅ Verified | CHARACTER | ✅ Verified | [On K.O.] DON!! −1 (You may return the specified number of DON!! cards… | Impl exists: on_ko |
| OP01-109 | ✅ Verified | CHARACTER | ✅ Verified | [DON!! x1] [Your Turn] If you have 8 or more DON!! cards on your field… | Impl exists: blocker, continuous |
| OP01-110 | ✅ Verified | CHARACTER | ✅ Verified |  |  |
| OP01-111 | ✅ Verified | CHARACTER | I should be prompted if I want to use the DON -1 effect, it works as intended but is automatic. | [Blocker] (After your opponent declares an attack, you may rest this c… | Impl exists: blocker, on_block |
| OP01-112 | ✅ Verified | CHARACTER | ✅ Verified | [Activate: Main] [Once Per Turn] DON!! −1 (You may return the specifie… | Impl exists: activate |
| OP01-113 | ✅ Verified | CHARACTER | ON KO I am not adding the DON!! card. | [On K.O.] Add up to 1 DON!! card from your DON!! deck and rest it. | Impl exists: on_ko |
| OP01-114 | ✅ Verified | CHARACTER | I am not prompted to DON!! -1 so the rest of the effect is not working either. | [On Play] DON!! −1 (You may return the specified number of DON!! cards… | Impl exists: continuous |
| OP01-115 | ✅ Verified | EVENT | I am prompted to KO a 2 cost or less, this works correctly. But I should also be able to add 1 DON!! card as active. | [Main] K.O. up to 1 of your opponent's Characters with a cost of 2 or … | Impl exists: on_play |
| OP01-116 | ✅ Verified | EVENT | Fixed: rewrote to use search_top_cards helper which always shows all top cards and handles deck ordering, even when no valid SMILE target exists. | [Main] Look at 5 cards from the top of your deck; play up to 1 {SMILE}… | Impl exists: on_play |
| OP01-117 | ✅ Verified | EVENT | ✅ Verified | [Main] DON!! −1 (You may return the specified number of DON!! cards fr… | Impl exists: on_play |
| OP01-118 | ✅ Verified | EVENT | Fixed: DON return callback used wrong keyword arg `power_change=2000` instead of positional `power_amount`. TypeError left game stuck in counter stage. | [Counter] DON!! −2 (You may return the specified number of DON!! cards… | Impl exists: counter |
| OP01-119 | ✅ Verified | EVENT | ⚠ Needs Fix | [Counter] Up to 1 of your Leader or Character cards gains +4000 power … | When I use the counter, the card should gain +4000 power as well. It seems that is not taking place when this card is used.  |
| OP01-120 | ✅ Verified | CHARACTER | The game is still allowing blockers with a power of 2000 or less to be activated. | [Rush] (This card can attack on the turn in which it is played.) [When… | Impl exists: on_attack |
| OP01-121 | ✅ Verified | CHARACTER | ✅ Verified | Also treat this card's name as [Kouzuki Oden] according to the rules. … | Impl exists: continuous |

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
| OP02-025 | ⚠ Needs Fix | LEADER | If I have 1 or less characters on the field, then I should be able to reduce the cost of all my land of wano characters with a cost of 3 or less by 1 in my hand. Currently says "Error: Cannot activate effect" |
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
| OP02-113 | ✅ Verified | CHARACTER | The power gain should only last for the battle, so once the combat is done it shuld return to it's base power. |
| OP02-114 | ✅ Verified | CHARACTER | This card should only gain +1000 power on the opponents turn, he is currently getting it on my turn too. |
| OP02-115 | ✅ Verified | CHARACTER | on_attack: DON x2; KO opp cost 0 char |
| OP02-116 | ✅ Verified | CHARACTER |  |
| OP02-117 | ✅ Verified | EVENT | on_play: opp char -5 cost |
| OP02-118 | ✅ Verified | EVENT | I am using the effect on a card that is being targeted by an attack, the attack is big enough to kill and it is killing the character EVEN though the counter card says that the selected character cannot be KOd during THIS battle. |
| OP02-119 | ✅ Verified | EVENT | on_play: KO opp char cost 1 or less |
| OP02-120 | ✅ Verified | CHARACTER | They lose the +1000 power when I end my turn, they should keep that buff until my NEXT turn begins. |
| OP02-121 | ✅ Verified | CHARACTER | There is still no prompt to KO a 0 cost, after he gives all the opponents characters -5 cost. |

---

# Card Effect Status — OP03

| ID | Status | Type | Notes |
|----|--------|------|-------|
| OP03-001 | ✅ Verified | LEADER | I should be prompted to select which cards I want to trash from hand. Currently it is happening automatically. |
| OP03-002 | ✅ Verified | CHARACTER | DON x1: opp can't use Blocker 2000 or less |
| OP03-003 | ✅ Verified | CHARACTER | on_play: look 5, reveal Whitebeard Pirates card |
| OP03-004 | ✅ Verified | CHARACTER | When I attach the DON!! he gets rush as he should. However, it should not let me attack the leader with rush when I use the effect. It states that the leader cannot be attacked on the turn that this card is played. |
| OP03-005 | ✅ Verified | CHARACTER | When I activate his effect, this card should get sent to the trash at the end of the turn. |
| OP03-006 | ✅ Verified | CHARACTER |  |
| OP03-007 | ✅ Verified | CHARACTER |  |
| OP03-008 | ✅ Verified | CHARACTER | If the card attacking this card has the slash attribute, even if they win the combat he should not be able to be KOd. |
| OP03-009 | ✅ Verified | CHARACTER | It seems he is giving the rested don card to a leader or character, but that character/leader is not gaining +1000 power when the rested DON is attached to them. |
| OP03-010 | ✅ Verified | CHARACTER | blocker |
| OP03-011 | ✅ Verified | CHARACTER | When I attach DON!! and attack wtih this character I should be prompted to give -2000 power to 1 of the opponents character. |
| OP03-012 | ✅ Verified | CHARACTER | This card should let me select from my hand as well for the trash option. Also, after I trash I am not drawing the 1 card.  Also, the card is not being sent to the trash. |
| OP03-013 | ✅ Verified | CHARACTER | I am not being prompted to play this character from the trash rested now. |
| OP03-014 | ✅ Verified | CHARACTER | on_attack: play red cost 1 from hand |
| OP03-015 | ✅ Verified | CHARACTER | If this card is KOd I should only be able to give an opponent's leader or character -2000 power if it is the opponents turn. |
| OP03-016 | ✅ Verified | EVENT | Currently it let's me kill 8000 power and above, it should be 8000 power or less. Also, it is not indicating that my leader is gaining +3000 power and double attack. |
| OP03-017 | ✅ Verified | EVENT | This card is allowing me to select the opponents leader to give minus power, it should only be characters. |
| OP03-018 | ✅ Verified | EVENT | If I have 2 copies of Fire Fist OP03-018 in my hand, I should be able to trash the other one to use this cards effect. Right now it does not let me do that. |
| OP03-019 | ✅ Verified | EVENT | It is not increasing my leader's power by 4000. |
| OP03-020 | ✅ Verified | STAGE | activate: DON -2, if Ace leader, look 5 add Event |
| OP03-021 | ✅ Verified | LEADER | Claude you dumbass fucking retard, I SHOULD BE ABLE TO CHOOSE WHICH 2 EAST BLUE TYPE CHARACTERS TO REST. IT SHOULD BE A PROMPT NOT AUTOMATIC. |
| OP03-022 | ✅ Verified | LEADER | This leader should not return 1 DON!! to the DON!! deck, it should just rest 1 DON!! to use the effect. But the rest of it is working great. |
| OP03-023 | ✅ Verified | CHARACTER |  |
| OP03-024 | ✅ Verified | CHARACTER | It should prompt me to select which 2 of my opponent's 4 cost or less characters to rest. |
| OP03-025 | ✅ Verified | CHARACTER | I get "Invalid Choice response" when trying to use this effect. |
| OP03-026 | ✅ Verified | CHARACTER | on_play: if East Blue leader, rest opp char; trigger |
| OP03-027 | ✅ Verified | CHARACTER | Also, when Buchi is played out via Sham's effect, it should still activate his on play. |
| OP03-028 | ✅ Verified | CHARACTER | This card has 2 effects, and I should be prompted to select which one I want to use, either the set a East Blue Leader or Character as active, OR rest this character and 1 of the opponents characters. |
| OP03-029 | ✅ Verified | CHARACTER | on_play: KO rested cost 4-; trigger |
| OP03-030 | ✅ Verified | CHARACTER | on_play: look 5, reveal green East Blue; trigger |
| OP03-031 | ✅ Verified | CHARACTER | blocker |
| OP03-032 | ✅ Verified | CHARACTER | If the card attacking this card (leader or character) has the slash attribute, regardless of if they win the combat this character should not be able to be KOd. |
| OP03-033 | ✅ Verified | CHARACTER | Leader needs to be an East Blue Type in the simulation to test. |
| OP03-034 | ✅ Verified | CHARACTER | on_play: KO rested cost 2- |
| OP03-035 | ✅ Verified | CHARACTER |  |
| OP03-036 | ⚠ Needs Fix | EVENT | When I use this card, and my Kuro leader is rested it should let me set it as active, but it does not do that.  |
| OP03-037 | ✅ Verified | EVENT | I should be prompted to select which East Blue Type character I want to rest. |
| OP03-038 | ✅ Verified | EVENT | I should be given the option to select 2 characters with a cost of 2 or less, currently it only lets me choose 1. |
| OP03-039 | ✅ Verified | EVENT | The leader is an option to give +1000 power, it should ONLY let me select characters. |
| OP03-040 | ⚠ Needs Fix | LEADER | Move 36 cards to the trash. I want the deck size to be 4 for this leader.  |
| OP03-041 | ✅ Verified | CHARACTER | When this character deal's damage (by attacking leader), the top 7 cards from the deck should be added to the trash. |
| OP03-042 | ✅ Verified | CHARACTER | It should prompt me to select which card to add to hand. |
| OP03-043 | ✅ Verified | CHARACTER | If any of my cards, leader or character deals damage to the opponent, I should be promtped per Gaimon effect to choose if I want to trash 3 cards from the top of my deck. If I choose to do so, trash the gaimon. |
| OP03-044 | ✅ Verified | CHARACTER | on_play: draw 2, trash 2 |
| OP03-045 | ✅ Verified | CHARACTER | The +3000 power when there are 20 or less cards in deck should only be on the opponents turn. |
| OP03-046 | ✅ Verified | CHARACTER |  |
| OP03-047 | ✅ Verified | CHARACTER | When this card deals damage I should be prompted if I want to trash the top 7 cards of my deck. This is ONLY if I have a DON!! on the card. |
| OP03-048 | ✅ Verified | CHARACTER | on_play: if Nami leader, return opp cost 5- |
| OP03-049 | ✅ Verified | CHARACTER | Set my deck to 20 cards so I can test this card. |
| OP03-050 | ✅ Verified | CHARACTER | I should be given the option if I want to trash 1 card from the top of the deck. |
| OP03-051 | ✅ Verified | CHARACTER | I should be prompted similarly to when I deal damage, when the card is KOd, if I want to trash the top 3 cards from the deck. |
| OP03-052 | ✅ Verified | CHARACTER |  |
| OP03-053 | ✅ Verified | CHARACTER | Set my deck to 20 cards so I can test this card. |
| OP03-054 | ✅ Verified | EVENT | I should be given the option to select which leader or character gains +2000 power for the battle, also I should have the option to trash the 1 card from the top of the deck. |
| OP03-055 | ✅ Verified | EVENT | I still need to be prompted if I want to trash 2 cards from the top of the deck when I use this card. |
| OP03-056 | ✅ Verified | EVENT | on_play: draw 2 |
| OP03-057 | ✅ Verified | EVENT | on_play: place cost 5- at bottom |
| OP03-058 | ✅ Verified | LEADER | continuous: cannot attack; activate: DON -1, play Galley-La 5- |
| OP03-059 | ✅ Verified | CHARACTER | on_attack: DON -1, gain Banish |
| OP03-060 | ✅ Verified | CHARACTER | on_attack: DON -1, draw 2, trash 1 |
| OP03-061 | ✅ Verified | CHARACTER |  |
| OP03-062 | ✅ Verified | CHARACTER | on_play: look 5, reveal Water Seven card |
| OP03-063 | ✅ Verified | CHARACTER | blocker; on_play: DON -1, if Water Seven leader draw 1 |
| OP03-064 | ✅ Verified | CHARACTER | This card is not prompting me if I want to add 1 DON!! card from my DON!! deck and rest it when KOd. |
| OP03-065 | ✅ Verified | CHARACTER | blocker |
| OP03-066 | ✅ Verified | CHARACTER | I should be prompted at every stage of this effect. The first prompt should be if I want to rest 2 DON!! to use the effect. If I say yes, then I should be prompted if I want to Add up to 1 DON!! deck and set it as active, even if I choose NOT to do this or CANNOT do this then I should still be prompted to KO 1 of my opponents characters with a cost of 4 or less GRANTED I have 8 or more DON!! cards on my field. |
| OP03-067 | ✅ Verified | CHARACTER | When attacking I should be prompted if I want to add up to 1 DON! card from my DON!! deck and rest it. Granted there is a DON!! on this card. |
| OP03-068 | ✅ Verified | CHARACTER | The On KO effect is not coded for this card. Or I am not prompted to do it. |
| OP03-069 | ✅ Verified | CHARACTER | on_ko: if Impel Down leader, draw 2 trash 1 |
| OP03-070 | ✅ Verified | CHARACTER | I am using the DON -1 On play effect and trashing a 5 cost from hand but this card is not getting rush. It should if and only if I do the DON -1 and trash the card. |
| OP03-071 | ✅ Verified | CHARACTER | I do the DON -1 effect and choose a character of cost 5 or less to rest, but it does not actually rest that character. |
| OP03-072 | ✅ Verified | EVENT | counter: trash 1, +3000 |
| OP03-073 | ✅ Verified | EVENT | I am not prompted to KO the 2 cost or less after I return the DON as I should be. |
| OP03-074 | ✅ Verified | EVENT | on_play: DON -2, place opp cost 4- at bottom |
| OP03-075 | ✅ Verified | STAGE | Idiot this is adding ACTIVE don not RESTED. |
| OP03-076 | ✅ Verified | LEADER | When this card get's set as active again it should be able to attack again. |
| OP03-077 | ✅ Verified | LEADER | I dont know how many fucking times I need to tell you this, IT IS NOT SUPPOSED TO RETURN 2 DON TO DON DECK, The prompt should be to REST 2 DON!!. If I do rest the 2 DON!! then I should be prompted to trash 1 card from hand, if I choose to do so and I have 1 or less life THEN add the top card of the deck to the top of the life. |
| OP03-078 | ✅ Verified | CHARACTER | When this card is given a DON!! the opponents cards should ONLY get -3 Cost on MY TURN IF IAM THE ONE WHO PLAYED THIS CARD. WHEN IT IS THE OPPONENTS TURN THAT GOES AWAY |
| OP03-079 | ✅ Verified | CHARACTER | DON x1 continuous: can't be KO in battle |
| OP03-080 | ✅ Verified | CHARACTER | This card should only be able to KO an opponents character with cost of 3 or less IF I return 2 cards from my trash that have the CP type to the bottom of the deck in an order I choose. |
| OP03-081 | ✅ Verified | CHARACTER | I have to Draw 2 cards and Select which 2 cards I want to trash before I can give the -2 cost. |
| OP03-082 | ✅ Verified | CHARACTER |  |
| OP03-083 | ✅ Verified | CHARACTER | on_play: look 5, trash up to 2, rest at bottom |
| OP03-084 | ✅ Verified | CHARACTER |  |
| OP03-085 | ✅ Verified | CHARACTER |  |
| OP03-086 | ✅ Verified | CHARACTER | SHOW ME THE FUCKING TOP 3 CARDS BEFORE THEY GET TRASHED RETARD |
| OP03-087 | ✅ Verified | CHARACTER |  |
| OP03-088 | ⚠ Needs Fix | CHARACTER | When I add this card to the opponent's field, it is not detecting it. So I cannot test effectively. |
| OP03-089 | ✅ Verified | CHARACTER | SHOW ME THE FUCKING TOP 3 CARDS BEFORE THEY GET TRASHED RETARD |
| OP03-090 | ✅ Verified | CHARACTER | DON x1 continuous: Blocker; on_ko: play CP cost 4- from trash |
| OP03-091 | ✅ Verified | CHARACTER | "Error: Invalid Choice Response" when selected a valid card. |
| OP03-092 | ✅ Verified | CHARACTER | I should be prompted to select 2 cards with type "CP" in the trash to add back to the bottom of the deck. And then this character should have rush if I do this. |
| OP03-093 | ✅ Verified | CHARACTER | I need to trash 1 card from my hand first to be able to use this effect. |
| OP03-094 | ✅ Verified | EVENT | Add a fucking CP type card in the top 5 of the deck so I can test. |
| OP03-095 | ✅ Verified | EVENT | It only let's me select 1 card right now. |
| OP03-096 | ✅ Verified | EVENT | on_play: KO opp cost 0 or Stage |
| OP03-097 | ✅ Verified | EVENT | counter: trash 1, +3000 |
| OP03-098 | ✅ Verified | STAGE | activate: rest, if CP leader opp -2 cost |
| OP03-099 | ✅ Verified | LEADER | I should be able to see the top of the opponent's life cards when attacking with DON on this card. I can currently see nothing. Then I should have the option to place it at the bottom of their life or keep it at the top. THEN the leader should gain +1000 power. |
| OP03-100 | ✅ Verified | CHARACTER | This card is not being played out after trashing a card from life. |
| OP03-101 | ✅ Verified | CHARACTER |  |
| OP03-102 | ✅ Verified | CHARACTER | When this card attacks and is giving 2 DON!! cards, then they should be able to choose if they want to add the top or bottom of their life cards to their hand. If they choose to do this, then 1 card from the top of the deck should be added to the top of the life cards from the top of the deck. |
| OP03-103 | ✅ Verified | CHARACTER |  |
| OP03-104 | ✅ Verified | CHARACTER | When this card is played, we should be able to see the top of the opponent's life cards, and then we should be prompted if we want to leave it at the top, or add it to the BOTTOM of their life cards. |
| OP03-105 | ⚠ Needs Fix | CHARACTER | This card is being read as having a trigger, this card does not have a trigger. This needs to be fixed.  |
| OP03-106 | ✅ Verified | CHARACTER |  |
| OP03-107 | ✅ Verified | CHARACTER | blocker |
| OP03-108 | ⚠ Needs Fix | CHARACTER | This card has a trigger that says "You may trash 1 card from your hand: Play this card" This means that if the player that took damage and had this trigger chooses a card to trash from hand then this card should be played onto the field.  |
| OP03-109 | ✅ Verified | CHARACTER | I should be prompted when playing this card if I want to trash the top or bottom of my life cards. If I choose 1 of them THEN I should be prompted if I want to add up to 1 OR 0 cards from the top of the deck to the top of my life cards. |
| OP03-110 | ✅ Verified | CHARACTER | This cards trigger says: "You may trash 1 card from hand: Play this card" if the opponent who TOOK the damage and triggered this card, they can trash 1 card from THEIR hand and play this card to the field. The when attacking effect works as intended though. |
| OP03-111 | ✅ Verified | CHARACTER |  |
| OP03-112 | ✅ Verified | CHARACTER | on_play: look 4, reveal Sanji or Big Mom Pirates card |
| OP03-113 | ✅ Verified | CHARACTER | on_ko: look 3, reveal Big Mom Pirates card |
| OP03-114 | ✅ Verified | CHARACTER | on_play: if BM leader, add deck to life, trash opp life |
| OP03-115 | ⚠ Needs Fix | CHARACTER | I should only be able to choose 1 of the opponent's characters to KO. Right now it lets me choose my own.  |
| OP03-116 | ✅ Verified | CHARACTER | on_play: draw 3, trash 2; trigger |
| OP03-117 | ✅ Verified | CHARACTER | I need to be prompted to select which Charlotte Linlin I want to give 1000 power to, or if I even want to do this effect. |
| OP03-118 | ✅ Verified | EVENT | counter: +5000 |
| OP03-119 | ✅ Verified | EVENT | Currently this lets me KO a 6 cost or less, it should be 4 cost or less. |
| OP03-120 | ✅ Verified | EVENT | on_play: if opp 4+ life, trash opp life |
| OP03-121 | ✅ Verified | EVENT | on_play: trash 1 life, KO opp cost 5- |
| OP03-122 | ⚠ Needs Fix | CHARACTER | Currently it is prompting me to return a 6 cost or less to the owners hand which is correct, then the draw 2 trash 2 which is also correct. But then it prompts me again to return a character with cost of 6 or less AGAIN. This should not happen |
| OP03-123 | 🔲 To Do | CHARACTER | on_play: add cost 8- char to life top/bottom |

# Card Effect Status — OP14

| ID | Status | Type | Notes |
|----|--------|------|-------|
| OP14-073 | ✅ Verified | CHARACTER |  |

# Card Effect Status — OP15

## Status Legend
- `✅ Verified` — Implemented and confirmed correct in simulator
- `⚠ Needs Fix` — Implementation exists but has a bug or mismatch
- `🔲 To Do` — Hardcoded impl exists, needs audit/verification
- `❌ Missing` — No implementation, needs writing
- `⬜ No Effect` / `⬜ Keywords` — No custom code needed

| ID | Name | Type | Status | Effect (summary) | Notes |
|----|----|------|--------|-----------------|-------|
| OP15-001 | Krieg | LEADER | ❌ Missing | [DON!! x1] [Opponent's Turn] If the only Characters on your field are … |  |
| OP15-002 | Lucy | LEADER | ❌ Missing | [When Attacking]/[On Your Opponent's Attack] You may trash any number … |  |
| OP15-003 | Alvida | CHARACTER | ❌ Missing | If this Character would be K.O.'d, you may trash 1 Character card with… |  |
| OP15-004 | Sea Cat | CHARACTER | ❌ Missing | [On Play] If your Leader has 0 power or less, give up to 1 of your opp… |  |
| OP15-005 | Cabaji | CHARACTER | ❌ Missing | [When Attacking] If your opponent has any DON!! cards given, this Char… |  |
| OP15-006 | Cavendish | CHARACTER | ❌ Missing | If you have 4 or more Events in your trash, this Character gains +2000… |  |
| OP15-007 | Gin | CHARACTER | ❌ Missing | [On Play] If your Leader has the {East Blue} type, play up to 1 Charac… |  |
| OP15-008 | Krieg | CHARACTER | ❌ Missing | [On Play] Give up to 3 of your opponent's rested DON!! cards to 1 of y… |  |
| OP15-009 | Koby | CHARACTER | ❌ Missing | If your Character with 7000 base power or less would be removed from t… |  |
| OP15-010 | Nezumi | CHARACTER | ❌ Missing | [Activate: Main] [Once Per Turn] Give up to 1 rested DON!! card to its… |  |
| OP15-011 | Pearl | CHARACTER | ❌ Missing | [Opponent's Turn] If your Leader has the {East Blue} type, this Charac… |  |
| OP15-012 | Buggy | CHARACTER | ❌ Missing | [When Attacking] Give up to 1 rested DON!! card to its owner's Leader … |  |
| OP15-013 | Pincers | CHARACTER | ❌ Missing | If your Leader has 0 power or less, give this card in your hand −2 cos… |  |
| OP15-014 | Bartolomeo | CHARACTER | ❌ Missing | If this Character would be K.O.'d, you may trash 1 Event from your han… |  |
| OP15-015 | Higuma | CHARACTER | ❌ Missing | [On Play] Give up to 1 of your opponent's rested DON!! cards to 1 of y… |  |
| OP15-016 | Fullbody | CHARACTER | ⬜ No Effect |  |  |
| OP15-017 | Morgan | CHARACTER | ❌ Missing | [Blocker] [Activate: Main] [Once Per Turn] You may give 1 of your oppo… |  |
| OP15-018 | Mohji | CHARACTER | ❌ Missing | [When Attacking] K.O. up to 1 of your opponent's Characters with 3000 … |  |
| OP15-019 | Barrier Bulls | EVENT | ❌ Missing | [Main] Draw 1 card and your Leader gains +1000 power until the end of … |  |
| OP15-020 | Fire Fist | EVENT | ❌ Missing | [Main] Your Leader gains +3000 power during this turn and give up to 1… |  |
| OP15-021 | Just Watch Me, Ace!!! | EVENT | ❌ Missing | If you have 4 or more Events in your trash, give this card in your han… |  |
| OP15-022 | Brook | LEADER | ❌ Missing | Under the rules of this game, you do not lose when your deck has 0 car… |  |
| OP15-023 | Arlong | CHARACTER | ❌ Missing | [On K.O.] Up to 2 of your opponent's rested cards will not become acti… |  |
| OP15-024 | Usopp | CHARACTER | ❌ Missing | [Opponent's Turn] This Character cannot be rested by your opponent's L… |  |
| OP15-025 | Kuro | CHARACTER | ❌ Missing | [Blocker] [On Play] Give up to 2 DON!! cards from your opponent's cost… |  |
| OP15-026 | Jango | CHARACTER | ❌ Missing | [On Play] Look at 3 cards from the top of your deck; reveal up to 1 {E… |  |
| OP15-027 | Dracule Mihawk | CHARACTER | ❌ Missing | [On Play] Rest up to 1 of your opponent's Characters with a DON!! card… |  |
| OP15-028 | Meowban Brothers | CHARACTER | ❌ Missing | [On Play] If your Leader has the {East Blue} type, give up to 1 DON!! … |  |
| OP15-029 | Bartholomew Kuma | CHARACTER | ❌ Missing | [On Play] Up to 1 of your opponent's Characters with a cost of 5 or le… |  |
| OP15-030 | Hyouzou | CHARACTER | ⬜ No Effect |  |  |
| OP15-031 | Purinpurin | CHARACTER | ❌ Missing | [On Play] Select up to 1 of your opponent's rested Characters. If the … |  |
| OP15-032 | Brook | CHARACTER | ❌ Missing | [On Play] Rest up to 1 of your opponent's cards. [Activate: Main] You … |  |
| OP15-033 | Hody Jones | CHARACTER | ❌ Missing | [On Play] Set your {Fish-Man} type Leader as active. Then, add 1 card … |  |
| OP15-034 | Yorki | CHARACTER | ❌ Missing | [Your Turn] [On Play] Up to 1 of your [Brook] cards gains +2000 power … |  |
| OP15-035 | Laboon | CHARACTER | ❌ Missing | If your Character with 7000 base power or less would be removed from t… |  |
| OP15-036 | Ryuma | CHARACTER | ❌ Missing | [On Play]/[When Attacking] K.O. up to 1 of your opponent's rested Char… |  |
| OP15-037 | The Outcome Will Tell Us Who's Strong and Who's Weak | EVENT | ❌ Missing | [Main] Look at 5 cards from the top of your deck; reveal up to 1 {East… |  |
| OP15-038 | It's an Order! Do Not Defy Me!!! | EVENT | ❌ Missing | [Main] Up to 1 of your opponent's rested Characters with a cost of 8 o… |  |
| OP15-039 | Rebecca | LEADER | ❌ Missing | This Leader cannot attack. [Activate: Main] You may rest this Leader a… |  |
| OP15-040 | Viola | CHARACTER | ❌ Missing | [On Play] Look at 3 cards from the top of your deck; reveal up to 1 {D… |  |
| OP15-041 | Orlumbus | CHARACTER | ❌ Missing | [On K.O.] Draw 1 card. [Activate: Main] [Once Per Turn] You may place … |  |
| OP15-042 | Kyros | CHARACTER | ❌ Missing | [On Play] You may trash 1 card from your hand: If your Leader is [Rebe… |  |
| OP15-043 | Kelly Funk | CHARACTER | ❌ Missing | [On Play] Play up to 1 [Bobby Funk] from your hand. |  |
| OP15-044 | Koala | CHARACTER | ❌ Missing | [Blocker] [On K.O.] Look at 3 cards from the top of your deck; reveal … |  |
| OP15-045 | Sai | CHARACTER | ❌ Missing | [Blocker] (After your opponent declares an attack, you may rest this c… |  |
| OP15-046 | Sabo | CHARACTER | ❌ Missing | [Blocker] [On Play] If your Leader has the {Dressrosa} type, activate … |  |
| OP15-047 | Sanji | CHARACTER | ❌ Missing | [Blocker] (After your opponent declares an attack, you may rest this c… |  |
| OP15-048 | Chinjao | CHARACTER | ❌ Missing | [On Play] You may trash 1 Event from your hand: Draw 2 cards. [Opponen… |  |
| OP15-049 | Hajrudin | CHARACTER | ⬜ No Effect |  |  |
| OP15-050 | Bobby Funk | CHARACTER | ❌ Missing | If you have [Kelly Funk], this Character gains +3000 power. |  |
| OP15-051 | Monkey.D.Luffy | CHARACTER | ❌ Missing | [Opponent's Turn] If your Leader has the {Dressrosa} type, this Charac… |  |
| OP15-052 | Leo | CHARACTER | ❌ Missing | If your Character with 7000 base power or less would be removed from t… |  |
| OP15-053 | Rebecca | CHARACTER | ❌ Missing | [DON!! x1] This Character gains [Blocker]. [On Play] Look at 3 cards f… |  |
| OP15-054 | And No One Else Can Have It! It's Our Memento of Him | EVENT | ❌ Missing | [Main] If your Leader is [Lucy], choose one: • Draw 2 cards and trash … |  |
| OP15-055 | Go Ahead and Use 'Em, Mr. Luffy!!! | EVENT | ❌ Missing | [Main] Choose one: • Draw 2 cards. • Up to 1 of your {Dressrosa} type … |  |
| OP15-056 | Would You Let Me Eat the Flame-Flame Fruit? | EVENT | ❌ Missing | [Main] Draw 2 cards. Then, your [Lucy] Leader gains [Double Attack] an… |  |
| OP15-057 | Dressrosa Kingdom | STAGE | ❌ Missing | [On Play] If your Leader has the {Dressrosa} type, draw 1 card. [On Yo… |  |
| OP15-058 | Enel | LEADER | ❌ Missing | Under the rules of this game, your DON!! deck consists of 6 cards. [Ac… |  |
| OP15-059 | Amazon | CHARACTER | ❌ Missing | [On Your Opponent's Attack] You may rest this Character: Your opponent… |  |
| OP15-060 | Enel | CHARACTER | ❌ Missing | If you have 6 or less DON!! cards on your field, this Character cannot… |  |
| OP15-061 | Ohm | CHARACTER | ❌ Missing | [On Play] DON!! −1: Draw 1 card. [When Attacking] If you have 6 or les… |  |
| OP15-062 | Captain Seamars | CHARACTER | ⬜ No Effect |  |  |
| OP15-063 | Gedatsu | CHARACTER | ❌ Missing | [On Play] DON!! −1: Draw 1 card. [On K.O.] If you have 6 or less DON!!… |  |
| OP15-064 | Kotori | CHARACTER | ❌ Missing | [Activate: Main] DON!! −2, You may rest this Character: If you have [S… |  |
| OP15-065 | Goro | CHARACTER | ❌ Missing | [On Play] Reveal 1 card from the top of your deck. If the revealed car… |  |
| OP15-066 | Satori | CHARACTER | ❌ Missing | [On Play] DON!! −1: Draw 1 card. [When Attacking] If you have 6 or les… |  |
| OP15-067 | Shura | CHARACTER | ❌ Missing | If you have 6 or less DON!! cards on your field, this Character gains … |  |
| OP15-068 | Heavenly Warriors | CHARACTER | ❌ Missing | If you have 6 or less DON!! cards on your field, this Character gains … |  |
| OP15-069 | Nola | CHARACTER | ❌ Missing | If your Character with 7000 base power or less would be removed from t… |  |
| OP15-070 | Fuza | CHARACTER | ❌ Missing | All of your [Shura] cards and this Character gain [Unblockable]. (This… |  |
| OP15-071 | Holly | CHARACTER | ❌ Missing | All of your [Ohm] cards and this Character gain [Double Attack]. (This… |  |
| OP15-072 | Hotori | CHARACTER | ❌ Missing | [Activate: Main] DON!! −2, You may rest this Character: If you have [K… |  |
| OP15-073 | Yama | CHARACTER | ❌ Missing | [Blocker] (After your opponent declares an attack, you may rest this c… |  |
| OP15-074 | Varie | EVENT | ❌ Missing | [Main] DON!! −1: If your Leader is [Enel], draw 1 card. Then, up to 1 … |  |
| OP15-075 | El Thor | EVENT | ❌ Missing | [Main] DON!! −1: If your Leader is [Enel], up to 1 of your Leader or C… |  |
| OP15-076 | Lightning Beast Kiten | EVENT | ❌ Missing | [Main] DON!! −1: If your Leader is [Enel], draw 1 card. Then, give up … |  |
| OP15-077 | Lightning Dragon | EVENT | ❌ Missing | [Main] DON!! −1: Draw 1 card. Then, up to 1 of your opponent's rested … |  |
| OP15-078 | Mamaragan | EVENT | ❌ Missing | [Main] DON!! −2: Draw 1 card. Then, rest up to 1 of your opponent's Ch… |  |
| OP15-079 | Absalom | CHARACTER | ❌ Missing | [On K.O.] Add up to 1 {Thriller Bark Pirates} type card from your tras… |  |
| OP15-080 | Oars | CHARACTER | ❌ Missing | If you have [Gecko Moria] with 10000 power or more on your field and t… |  |
| OP15-081 | Sanji | CHARACTER | ❌ Missing | [On Play] If your Leader has the {Straw Hat Crew} type, trash 5 cards … |  |
| OP15-082 | Charlotte Lola | CHARACTER | ❌ Missing | [On Play] Trash 3 cards from the top of your deck. [On K.O.] Add up to… |  |
| OP15-083 | Spoil | CHARACTER | ❌ Missing | [On Play] Trash 3 cards from the top of your deck. [Activate: Main] Yo… |  |
| OP15-084 | Dr. Hogback | CHARACTER | ❌ Missing | [On Play] If your Leader has the {Thriller Bark Pirates} type, trash 5… |  |
| OP15-085 | Tony Tony.Chopper | CHARACTER | ❌ Missing | [On Play] Trash 3 cards from the top of your deck. [Activate: Main] Yo… |  |
| OP15-086 | Nami | CHARACTER | ❌ Missing | [On Play] If your Leader has the {Straw Hat Crew} type, play up to 1 {… |  |
| OP15-087 | Nico Robin | CHARACTER | ❌ Missing | If you have 10 or more cards in your trash, this Character gains [Bloc… |  |
| OP15-088 | Pirates Docking Six | CHARACTER | ❌ Missing | This Character gains +6 cost. [On Play] You may trash 3 cards from the… |  |
| OP15-089 | Franky | CHARACTER | ⬜ No Effect |  |  |
| OP15-090 | Perona | CHARACTER | ❌ Missing | If your Character with 7000 base power or less would be removed from t… |  |
| OP15-091 | Margarita | CHARACTER | ❌ Missing | [On Play] Place up to 1 card from your opponent's trash at the bottom … |  |
| OP15-092 | Monkey.D.Luffy | CHARACTER | ❌ Missing | Apply each of the following effects based on the number of cards in yo… |  |
| OP15-093 | The Risky Brothers | CHARACTER | ❌ Missing | [Activate: Main] You may trash this Character: If you have 15 or more … |  |
| OP15-094 | Roronoa Zoro | CHARACTER | ❌ Missing | If your {Straw Hat Crew} type Character other than this Character woul… |  |
| OP15-095 | Gum-Gum Storm | EVENT | ❌ Missing | [Main] You may rest 1 of your DON!! cards: If you have 15 or more card… |  |
| OP15-096 | Swallow Bond en Avant | EVENT | ❌ Missing | [Main] You may rest 1 of your DON!! cards: If your Leader has the {Str… |  |
| OP15-097 | I Find It Embarrassing as a Human Being | EVENT | ❌ Missing | [Main] If you have 10 or more cards in your trash, up to 1 of your opp… |  |
| OP15-098 | Monkey.D.Luffy | LEADER | ❌ Missing | If your {Sky Island} type Character with 6000 base power or more would… |  |
| OP15-099 | Urouge | CHARACTER | ❌ Missing | [On Play] You may trash 1 {Supernovas} type card from your hand: This … |  |
| OP15-100 | Kamakiri | CHARACTER | ❌ Missing | [On Play] You may trash this Character and add 1 card from the top of … |  |
| OP15-101 | Kalgara | CHARACTER | ❌ Missing | [On Play] You may trash 1 card from your hand: Look at 5 cards from th… |  |
| OP15-102 | Gan.Fall | CHARACTER | ❌ Missing | If you have a {Sky Island} type Character with 7000 power or more, giv… |  |
| OP15-103 | Genbo | CHARACTER | ❌ Missing |  |  |
| OP15-104 | Conis | CHARACTER | ❌ Missing | [On Play] If you have less Life cards than your opponent, draw 2 cards… |  |
| OP15-105 | Jewelry Bonney | CHARACTER | ❌ Missing | If your Character with 7000 base power or less would be removed from t… |  |
| OP15-106 | Octoballoon | CHARACTER | ❌ Missing |  |  |
| OP15-107 | Tony Tony.Chopper | CHARACTER | ⬜ No Effect |  |  |
| OP15-108 | Nami | CHARACTER | ❌ Missing | [On Play] Look at 3 cards from the top of your deck; reveal up to 1 {S… |  |
| OP15-109 | Nico Robin | CHARACTER | ❌ Missing | [On Play] You may add 1 card from the top of your Life cards to your h… |  |
| OP15-110 | Braham | CHARACTER | ❌ Missing | [On K.O.] If your Leader has the {Shandian Warrior} type, add up to 1 … |  |
| OP15-111 | Mont Blanc Noland | CHARACTER | ❌ Missing | [DON!! x1] [When Attacking] Up to 1 of your [Kalgara] cards gains [Rus… |  |
| OP15-112 | Raki | CHARACTER | ❌ Missing | [Blocker] (After your opponent declares an attack, you may rest this c… |  |
| OP15-113 | Roronoa Zoro | CHARACTER | ❌ Missing | [On Play] You may trash 1 card from your hand: Add up to 1 card from t… |  |
| OP15-114 | Wyper | CHARACTER | ❌ Missing | [On Play] You may turn 1 card from the top of your Life cards face-up:… |  |
| OP15-115 | Impact Dial | EVENT | ❌ Missing | [Main] K.O. up to 1 of your opponent's Characters with a cost of 4 or … |  |
| OP15-116 | Gum-Gum Golden Rifle | EVENT | ❌ Missing | [Main] If your Leader has the {Straw Hat Crew} type, trash 1 card from… |  |
| OP15-117 | Heso!! | EVENT | ❌ Missing | [Main] Draw 1 card. Then, give up to 1 rested DON!! card to 1 of your … |  |
| OP15-118 | Enel | CHARACTER | ❌ Missing | If you have 6 or less DON!! cards on your field, this Character cannot… |  |
| OP15-119 | Monkey.D.Luffy | CHARACTER | ❌ Missing | If you have 6 or more DON!! cards on your field, this Character gains … |  |

**Total:** 119 cards
**Missing:** 113
**To Do (audit):** 0
**Verified:** 0


# Card Effect Status — OP04
| OP04-002 | Igaram | CHARACTER | ✅ Verified | [Activate: Main] You may rest this Character and give your 1 active Le… | Currently, this card is just giving leader -5000 power, if i choose to give the leader -5000 power I should be able to look at the top 5 cards of the deck and reveal up to 1 Alabasta type card and add it to my hand. |
| OP04-003 | Usopp | CHARACTER | ✅ Verified | [On K.O.] K.O. up to 1 of your opponent's Characters with 5000 base po… |  |
| OP04-006 | Koza | CHARACTER | ✅ Verified | [When Attacking] You may give your 1 active Leader −5000 power during … | This effect works but there should be a prompt if I want to give my active leader -5000 power first. |
| OP04-007 | Sanji | CHARACTER | ✅ Verified |  |  |
| OP04-004 | Karoo | CHARACTER | ✅ Verified | [Activate: Main] You may rest this Character: Give up to 1 rested DON!… | When I activate this character, it should become rested (like it currently does) and then I should be able to choose Alabasta type characters that I want to give a rested DON!! to. |
| OP04-005 | Kung Fu Jugon | CHARACTER | ✅ Verified | If you have a [Kung Fu Jugon] other than this Character, this Characte… | Even when I add another Kung Fu Jugon they do not gain blocker still. |
| OP04-008 | Chaka | CHARACTER | ✅ Verified | [DON!! x1] [When Attacking] If your Leader is [Nefeltari Vivi], give u… | When there is a DON!! on this character and I attack I should be prompted to give -3000 power to one of the opponents characters. Then I should be prompted to select a 0 power character to KO. |
| OP04-009 | Super Spot-Billed Duck Troops | CHARACTER | ✅ Verified | [When Attacking] You may give your 1 active Leader −5000 power during … | The card should not be rested when returned to the hand. |
| OP04-010 | Tony Tony.Chopper | CHARACTER | ✅ Verified | [On Play] Play up to 1 {Animal} type Character card with 3000 power or… | It currently automatically chooses an animal type character with 3000 power or less to play out, it should prompt me to select one. |
| OP04-011 | Nami | CHARACTER | ✅ Verified | [When Attacking] Reveal 1 card from the top of your deck. If the revea… | Whatever the top card is should show as a prompt, show the image of the card. |
| OP04-012 | Nefeltari Cobra | CHARACTER | ✅ Verified | [Your Turn] All of your {Alabasta} type Characters other than this Cha… | This effect should only be on the players (who controls this card) turn. |
| OP04-013 | Pell | CHARACTER | ✅ Verified | [DON!! x1] [When Attacking] K.O. up to 1 of your opponent's Characters… |  |
| OP04-014 | Monkey.D.Luffy | CHARACTER | ✅ Verified | [Banish] (When this card deals damage, the target card is trashed with… |  |
| OP04-015 | Roronoa Zoro | CHARACTER | ✅ Verified | [On Play] Give up to 1 of your opponent's Characters −2000 power durin… | I should be prompted to select the card I want to give -2000 to. |
| OP04-016 | Bad Manners Kick Course | EVENT | ✅ Verified | [Counter] You may trash 1 card from your hand: Up to 1 of your Leader … | I should be prompted to select which card I want to trash from my hand. Once it is selected, the character I select should gain +3000 power for the battle. |
| OP04-017 | Happiness Punch | EVENT | ✅ Verified | [Counter] Give up to 1 of your opponent's Leader or Character cards −2… | When I use this card I should be prompted to give a leader or character -2000 power for the opponents entire turn. In addition, if the defending player's leader is active, then I should be able to select another character or leader to give -1000 power to. This can stack with the original -2000. |
| OP04-018 | Enchanting Vertigo Dance | EVENT | ✅ Verified | [Main] If your Leader has the {Alabasta} type, give up to 2 of your op… | I should be able to choose 2 characters to give -2000 power to this turn. |
| OP04-019 | Donquixote Doflamingo | LEADER | ✅ Verified | [End of Your Turn] Set up to 2 of your DON!! cards as active. | When I end my turn I should be prompted to select 2 don to set back to active. |
| OP04-020 | Issho | LEADER | ✅ Verified | [DON!! x1] [Your Turn] Give all of your opponent's Characters −1 cost.… | When 1 DON!! is attached it should give all opponents characters -1 cost BUT ONLY ON THE PLAYER'S TURN, it currently does both turns. Also, when the turn is ended it should prompt to select a 5 cost or less to set back as active. |
| OP04-021 | Viola | CHARACTER | ✅ Verified | [On Your Opponent's Attack] ➁ (You may rest the specified number of DO… | When the opponent attacks and this card is on the field there should be a prompt if I want to rest 2 of my DON. If I choose to do so, I should be prompted if I want to rest up to 1 of my opponents DON!! cards. |
| OP04-022 | Eric | CHARACTER | ✅ Verified | [Activate: Main] You may rest this Character: Rest up to 1 of your opp… |  |
| OP04-023 | Kuro | CHARACTER | ✅ Verified |  |  |
| OP04-024 | Sugar | CHARACTER | ✅ Verified | [Opponent's Turn] [Once Per Turn] When your opponent plays a Character… | When the opponent plays a character and this card is on the field, I should be prompted to rest up 1 of  my opponents characters. If I do so, then this character gets rested as well. |
| OP04-025 | Giolla | CHARACTER | ✅ Verified | [On Your Opponent's Attack] ➁ (You may rest the specified number of DO… | If this card is on the field and the opponent attacks, the controller of this card should be prompted to rest 2 DON!! if the choice is yes to rest 2 DON!! There should be an option to rest up to 1 of the opponents characters with a cost of 4 or less. |
| OP04-026 | Senor Pink | CHARACTER | ✅ Verified | [When Attacking] ➀ (You may rest the specified number of DON!! cards i… | When I attack, I should be prompted if I want to rest 1 DON!! If I rest the DON!! and my leader is a Donquixote Pirate then I should be prompted to rest up to 1 of the opponents characters with a cost of 4 or less. This effect works, but it is showing me cards that are already rested. When I end the turn I should also be prompted to set up to 1 DON!! card as active. |
| OP04-027 | Daddy Masterson | CHARACTER | ✅ Verified | [DON!! x1] [End of Your Turn] Set this Character as active. |  |
| OP04-028 | Diamante | CHARACTER | ✅ Verified | [Blocker] (After your opponent declares an attack, you may rest this c… |  |
| OP04-029 | Dellinger | CHARACTER | ✅ Verified | [End of Your Turn] Set up to 1 of your DON!! cards as active. | Player should be prompted if they want to set 1 DON!! as active. |
| OP04-030 | Trebol | CHARACTER | ✅ Verified | [On Play] K.O. up to 1 of your opponent's rested Characters with a cos… | When the opponent attacks, the controller of this card should be prompted if they want to rest 2 DON!! if they do so then they should be prompted to rest one of the opponents 4 costs or less. |
| OP04-031 | Donquixote Doflamingo | CHARACTER | ✅ Verified | [On Play] Up to a total of 3 of your opponent's rested Leader and Char… | The characters selected by this card should not become active on the next turn, they should remain rested. |
| OP04-032 | Baby 5 | CHARACTER | ✅ Verified | [End of Your Turn] You may trash this Character: Set up to 2 of your D… | When I press End Turn and it prompts me to use the Baby 5 effect, it should still pass the turn to the opponent after the effect takes place. |
| OP04-033 | Machvise | CHARACTER | ✅ Verified | [On Play] If your Leader has the {Donquixote Pirates} type, rest up to… | When I press End Turn it should still pass the turn to the opponent, after the DON is set back to active. I currently have to press it again. |
| OP04-034 | Lao.G | CHARACTER | ✅ Verified | [End of Your Turn] If you have 3 or more active DON!! cards, K.O. up t… |  |
| OP04-035 | Spiderweb | EVENT | ✅ Verified | [Counter] Up to 1 of your Leader or Character cards gains +4000 power … | When the card is used as a trigger, only the TRIGGER text at the bottom should be activated unless it says otherwise. This card's trigger only gives +2000 power to a leader for the TURN. |
| OP04-036 | Donquixote Family | EVENT | ✅ Verified | [Counter] Look at 5 cards from the top of your deck; reveal up to 1 {D… |  |
| OP04-037 | Flapping Thread | EVENT | ✅ Verified | [Counter] If your Leader has the {Donquixote Pirates} type, up to 1 of… | I should be prompted to select a leader or character to give +2000 power to for the TURN. It currently is doing it automatically for the attacked character and doing it only for the battle. |
| OP04-038 | The Weak Do Not Have the Right to Choose How They Die!!! | EVENT | ✅ Verified | [Main]/[Counter] Rest up to 1 of your opponent's Leader or Character c… | The card works as it should when using it on my turn as a main. But when I use it as a counter it only let's me rest an opponent's leader or character cards - I should also be able to KO up to 1 of the opponent's 6 cost or less cards. |
| OP04-039 | Rebecca | LEADER | ✅ Verified | This Leader cannot attack. [Activate: Main] [Once Per Turn] ➀ (You may… |  |
| OP04-040 | Queen | LEADER | ✅ Verified | [DON!! x1] [When Attacking] If you have a total of 4 or less cards in … | Currently, when I attach DON! to this leader and attack nothing is happening. It should be letting me draw 1 card, if there is a character with cost of 8 or more on the board, then I should be prompted if I want to draw 1 card or add 1 card from the top of the deck to the top of the life. Granted I have 4 or less life cards still. |
| OP04-041 | Apis | CHARACTER | ✅ Verified | [On Play] You may trash 2 cards from your hand: Look at 5 cards from t… | It should prompt me to select which 2 cards I want to trash. |
| OP04-042 | Ipponmatsu | CHARACTER | ✅ Verified | [On Play] Up to 1 of your <Slash> attribute Characters gains +3000 pow… |  |
| OP04-043 | Ulti | CHARACTER | ✅ Verified | [DON!! x1] [When Attacking] Return up to 1 Character with a cost of 2 … |  |
| OP04-044 | Kaido | CHARACTER | ✅ Verified | [On Play] Return up to 1 Character with a cost of 8 or less and up to … |  |
| OP04-045 | King | CHARACTER | ✅ Verified | [On Play] Draw 1 card. |  |
| OP04-046 | Queen | CHARACTER | ✅ Verified | [On Play] If your Leader has the {Animal Kingdom Pirates} type, look a… | Add 2 Plague Rounds and 2 Ice Oni cards in the top 7 cards of the deck. |
| OP04-047 | Ice Oni | CHARACTER | ✅ Verified | [Your Turn] At the end of a battle in which this Character battles you… |  |
| OP04-048 | Sasaki | CHARACTER | ✅ Verified | [On Play] Return all cards in your hand to your deck and shuffle your … | This card should add all the cards in hand back into the deck, and then shuffle the deck. Then based on how many cards you had in hand that you returned, you draw that same amount of cards. |
| OP04-049 | Jack | CHARACTER | ✅ Verified | [On K.O.] Draw 1 card. |  |
| OP04-050 | Hanger | CHARACTER | ✅ Verified | [Activate: Main] You may trash 1 card from your hand and rest this Cha… |  |
| OP04-051 | Who's.Who | CHARACTER | ✅ Verified | [On Play] Look at 5 cards from the top of your deck; reveal up to 1 {A… |  |
| OP04-052 | Black Maria | CHARACTER | ✅ Verified | [Activate: Main] ➁ (You may rest the specified number of DON!! cards i… |  |
| OP04-054 | Rokki | CHARACTER | ✅ Verified |  |  |
| OP04-055 | Plague Rounds | EVENT | ✅ Verified | [Main] You may trash 1 [Ice Oni] from your hand and place 1 Character … | When I play this card I should be prompted to select an Ice Oni (OP04-047) to trash from my hand. On top of this I must return a cost 4 or lower character to the bottom of the owner's deck. If I do both of these things, then I should be prompted to select a [Ice Oni] from the trash to play to the field. |
| OP04-056 | Gum-Gum Red Roc | EVENT | ✅ Verified | [Main] Place up to 1 Character at the bottom of the owner's deck. | I should be prompted to select a character to return to the bottom of the owners deck. |
| OP04-057 | Dragon Twister Demolition Breath | EVENT | ✅ Verified | [Counter] Up to 1 of your Leader or Character cards gains +4000 power … | I do get the +4000 power when this card is used as a counter, but I should also be prompted to select a character with cost of 1 or less to send to the bottom of the owner's deck. |
| OP04-061 | Tom | CHARACTER | ✅ Verified | [Activate: Main] You may trash this Character: If your Leader has the … |  |
| OP04-062 | Bananagator | CHARACTER | ✅ Verified |  |  |
| OP04-064 | Ms. All Sunday | CHARACTER | ✅ Verified | [On Play] Add up to 1 DON!! card from your DON!! deck and rest it. The… |  |
| OP04-065 | Miss.Goldenweek(Marianne) | CHARACTER | ✅ Verified | [On Play] If your Leader's type includes "Baroque Works", up to 1 of y… |  |
| OP04-066 | Miss.Valentine(Mikita) | CHARACTER | ⚠ Needs Fix | [On Play] Look at 5 cards from the top of your deck; reveal up to 1 ca… | This card is still not in the fucking life, so I cant test the trigger. Add this card to the top of both players life.  |
| OP04-067 | Miss.MerryChristmas(Drophy) | CHARACTER | ✅ Verified | [Blocker] (After your opponent declares an attack, you may rest this c… |  |
| OP04-077 | Ideo | CHARACTER | ✅ Verified | [Blocker] (After your opponent declares an attack, you may rest this c… |  |
| OP04-078 | Oimo & Kashii | CHARACTER | ✅ Verified |  |  |
| OP04-079 | Orlumbus | CHARACTER | ✅ Verified | [Activate: Main] [Once Per Turn] Give up to 1 of your opponent's Chara… |  |
| OP04-081 | Cavendish | CHARACTER | ✅ Verified | [DON!! x1] This Character can also attack active Characters. [When Att… |  |
| OP04-082 | Kyros | CHARACTER | ✅ Verified | If this Character would be K.O.'d, you may rest your Leader or 1 [Corr… | The On Play works great, there is an issue with the first part of the effect. If this character would EVER be KOd, I should be prompted if I want to rest my leader or corrida coliseum instead. Now if there is no leader to rest (it is already rested), and there is no corida coliseum, then this character would die. |
| OP04-084 | Stussy | CHARACTER | ✅ Verified | [On Play] Look at 3 cards from the top of your deck and play up to 1 C… | Add a fucking CP type to the top 3 you fucking retard. |
| OP04-085 | Suleiman | CHARACTER | ✅ Verified | [On Play]/[When Attacking] If your Leader has the {Dressrosa} type, gi… |  |
| OP04-086 | Chinjao | CHARACTER | ✅ Verified | [DON!! x1] When this Character battles and K.O.'s your opponent's Char… | When this character KOs an opponents character and has DON!! attached, it should draw 2 and then prompt me to trash 2. |
| OP04-087 | Trafalgar Law | CHARACTER | ✅ Verified |  |  |
| OP04-088 | Hajrudin | CHARACTER | ✅ Verified | [Activate: Main] You may rest your 1 Leader: Give up to 1 of your oppo… |  |
| OP04-089 | Bartolomeo | CHARACTER | ✅ Verified | [Blocker] (After your opponent declares an attack, you may rest this c… |  |
| OP04-090 | Monkey.D.Luffy | CHARACTER | ✅ Verified | This Character can also attack active Characters. [Activate: Main] [On… | When this card gets set back to active by using the activate main, it should be able to attack again. Currently it says "Error: Cannot attack with that card". |
| OP04-091 | Leo | CHARACTER | ✅ Verified | [On Play] You may rest your 1 Leader: If your Leader has the {Dressros… |  |
| OP04-092 | Rebecca | CHARACTER | ✅ Verified | [On Play] Look at 3 cards from the top of your deck; reveal up to 1 {D… |  |
| OP04-093 | Gum-Gum King Kong Gun | EVENT | ✅ Verified | [Main] Up to 1 of your {Dressrosa} type Characters gains +6000 power d… | When I give a character double attack, it STILL is not working. They only gain the power increase no DOUBLE ATTACK. |
| OP04-094 | Trueno Bastardo | EVENT | ✅ Verified | [Main] Choose up to 1 of your opponent's Characters with a cost of 4 o… | I should be prompted to choose up to 1 of my opponents characters with a cost or 4 or less to KO. If I have more than 15 cards in my trash, I should be able to choose a character with a cost of 6 or less instead. |
| OP04-095 | Barrier!! | EVENT | ✅ Verified | [Counter] Up to 1 of your Leader or Character cards gains +2000 power … | This card is not giving an additional +2000 power if I have 15 or more cards in trash. |
| OP04-096 | Corrida Coliseum | STAGE | ✅ Verified | If your Leader has the {Dressrosa} type, your {Dressrosa} type Charact… | When the stage is out and leader is dressrosa type, it should allow ALL dressrosa type characters to attack ONLY characters on the turn they are played. |
| OP04-098 | Toko | CHARACTER | ✅ Verified | [On Play] You may trash 2 {Land of Wano} type cards from your hand: If… |  |
| OP04-099 | Olin | CHARACTER | ✅ Verified | Also treat this card's name as [Charlotte Linlin] according to the rul… | This cards name should also be treated as" [Charlotte Linlin]" |
| OP04-100 | Capone"Gang"Bege | CHARACTER | ✅ Verified | [Trigger] Up to 1 of your opponent&#039;s Leader or Character cards ca… |  |
| OP04-101 | Carmel | CHARACTER | ✅ Verified | [Your Turn] [On Play] Draw 1 card. |  |
| OP04-102 | Kin'emon | CHARACTER | ✅ Verified | [Activate: Main] [Once Per Turn] ➀ (You may rest the specified number … |  |
| OP04-103 | Kouzuki Hiyori | CHARACTER | ✅ Verified | [On Play] Up to 1 of your {Land of Wano} type Leader or Character card… |  |
| OP04-104 | Sanji | CHARACTER | ✅ Verified | [Blocker] (After your opponent declares an attack, you may rest this c… |  |
| OP04-105 | Charlotte Amande | CHARACTER | ✅ Verified | [Activate: Main] [Once Per Turn] You may trash 1 card with a [Trigger]… |  |
| OP04-106 | Charlotte Bavarois | CHARACTER | ✅ Verified | [DON!! x1] If you have less Life cards than your opponent, this Charac… | Put this card in life so we can test the trigger. |
| OP04-107 | Charlotte Perospero | CHARACTER | ✅ Verified |  |  |
| OP04-108 | Charlotte Moscato | CHARACTER | ✅ Verified | [DON!! x1] This Character gains [Banish]. (When this card deals damage… |  |
| OP04-109 | Tonoyasu | CHARACTER | ✅ Verified | [Activate: Main] You may trash this Character: Up to 1 of your {Land o… |  |
| OP04-110 | Pound | CHARACTER | ✅ Verified | [Blocker] (After your opponent declares an attack, you may rest this c… |  |
| OP04-112 | Yamato | CHARACTER | ✅ Verified | [On Play] K.O. up to 1 of your opponent's Characters with a cost equal… | The player should not be told what card was added to life. |
| OP04-113 | Rabiyan | CHARACTER | ✅ Verified | [Trigger] Play this card. |  |
| OP04-114 | Randolph | CHARACTER | ✅ Verified |  |  |
| OP04-115 | Gun Modoki | EVENT | ✅ Verified | [Main] You may add 1 card from the top or bottom of your Life cards to… | I am giving double attack to Yamato but when she deals damage it only does 1 damage. |
| OP04-116 | Diable Jambe Joue Shot | EVENT | ✅ Verified | [Counter] Up to 1 of your Leader or Character cards gains +6000 power … | If the opponent and the player have a combined total of 4 or less life cards, the player should be prompted if they want to KO up to 1 of the opponents 2 costs or less. |
| OP04-117 | Heavenly Fire | EVENT | ✅ Verified | [Main] Add up to 1 of your opponent's Characters with a cost of 3 or l… | Card not coded. |
| OP04-118 | Nefeltari Vivi | CHARACTER | ✅ Verified | All of your red Characters with a cost of 3 or more other than this Ch… |  |
| OP04-119 | Donquixote Rosinante | CHARACTER | ✅ Verified | [Opponent's Turn] If this Character is rested, your active Characters … | This card should prompt me first if I want to use the effect. |
| OP04-053 | Page One | CHARACTER | ✅ Verified | [DON!! x1] [Once Per Turn] When you activate an Event, draw 1 card. Th… | I should be prompted to select which card I want to add to the bottom of the deck after the draw. |
| OP04-060 | Crocodile | CHARACTER | ✅ Verified | [On Play] DON!! −2 (You may return the specified number of DON!! cards… |  |
| OP04-063 | Franky | CHARACTER | ✅ Verified | [On Your Opponent's Attack] [Once Per Turn] DON!! −1 (You may return t… | This card is boosting by 2000 instead of 1000 |
| OP04-068 | Yokozuna | CHARACTER | ✅ Verified | [Blocker] (After your opponent declares an attack, you may rest this c… | When I select a card to return to hand, if they have the same name it returns both. I.e, I chose to return Streusen to hand, and instead of returning 1 it returned both. |
| OP04-069 | Mr.2.Bon.Kurei(Bentham) | CHARACTER | ✅ Verified | [On Your Opponent's Attack] DON!! −1 (You may return the specified num… |  |
| OP04-070 | Mr.3(Galdino) | CHARACTER | ✅ Verified | [On Your Opponent's Attack] [Once Per Turn] DON!! −1 (You may return t… |  |
| OP04-071 | Mr.4(Babe) | CHARACTER | ✅ Verified | [On Your Opponent's Attack] DON!! −1 (You may return the specified num… | This character is gaining +2000 power instead of +1000 power. |
| OP04-072 | Mr.5(Gem) | CHARACTER | ✅ Verified | [On Your Opponent's Attack] [Once Per Turn] DON!! −2 (You may return t… |  |
| OP04-073 | Mr.13 & Ms.Friday | CHARACTER | ✅ Verified | [Activate: Main] You may trash this Character and 1 of your Characters… | This card is adding 3 DON!! as rested, it should add 1 DON as active. Also, it is not trashing this character and the character with type "Baroque Works" |
| OP04-074 | Colors Trap | EVENT | ✅ Verified | [Counter] DON!! −1 (You may return the specified number of DON!! cards… |  |
| OP04-075 | Nez-Palm Cannon | EVENT | ✅ Verified | [Counter] Up to 1 of your Leader or Character cards gains +6000 power … |  |
| OP04-076 | Weakness...Is an Unforgivable Sin. | EVENT | ✅ Verified | [Counter] DON!! −1 (You may return the specified number of DON!! cards… |  |
| OP04-080 | Gyats | CHARACTER | ✅ Verified | [On Play] Up to 1 of your {Dressrosa} type Characters can also attack … |  |
| OP04-111 | Hera | CHARACTER | ✅ Verified | [Activate: Main] You may trash 1 of your {Homies} type Characters othe… | [TRIGGER] Hera: Activating trigger — [Trigger] Play this card. Activating is still using the FUCKING TRIGGER U DUMB SHIT. IT SHOULD PROMPT ME TO TRASH 1 HOMIES TYPE CHARACTER, THEN REST THIS CHARACTER. IF I DO THIS THEN SET A CHARLOTTE LINLIN AS ACTIVE. |
| OP04-059 | Iceburg | CHARACTER | ✅ Verified | [On Your Opponent's Attack] DON!! −1 (You may return the specified num… |  |

| ID | Status | Type | Notes |
|----|--------|------|-------|
| OP04-001 | Nefeltari Vivi | LEADER | ✅ Verified | This Leader cannot attack. [Activate: Main] [Once Per Turn] ➁ (You may… | Currently, this card is just drawing 1 card, what it SHOULD do is prompt me to select which 2 DON!! to rest when I active it's effect. Then if I rest 2 DON!! I should draw 1 card, and then I should select either 0 or 1 characters to give Rush for the turn. |

# Card Effect Status — OP05
| OP05-011 | Bartholomew Kuma | CHARACTER | ✅ Verified | [On Play] K.O. up to 1 of your opponent's Characters with 2000 power o… |  |
| OP05-012 | Hack | CHARACTER | ✅ Verified |  |  |
| OP05-013 | Bunny Joe | CHARACTER | ✅ Verified | [Blocker] (After your opponent declares an attack, you may rest this c… |  |
| OP05-021 | Revolutionary Army HQ | STAGE | ✅ Verified | [Activate: Main] You may trash 1 card from your hand and rest this Sta… |  |
| OP05-024 | Kuween | CHARACTER | ✅ Verified | [Blocker] (After your opponent declares an attack, you may rest this c… |  |
| OP05-025 | Gladius | CHARACTER | ✅ Verified | [Activate: Main] You may rest this Character: Rest up to 1 of your opp… |  |
| OP05-027 | Trafalgar Law | CHARACTER | ✅ Verified | [Activate: Main] You may trash this Character: Rest up to 1 of your op… |  |
| OP05-028 | Donquixote Doflamingo | CHARACTER | ✅ Verified | [Activate: Main] You may trash this Character: K.O. up to 1 of your op… |  |
| OP05-031 | Buffalo | CHARACTER | ✅ Verified | [When Attacking] [Once Per Turn] If you have 2 or more rested Characte… |  |
| OP05-035 | Bellamy | CHARACTER | ✅ Verified |  |  |
| OP05-036 | Monet | CHARACTER | ✅ Verified | [Blocker] (After your opponent declares an attack, you may rest this c… |  |
| OP05-044 | John Giant | CHARACTER | ✅ Verified |  |  |
| OP05-047 | Basil Hawkins | CHARACTER | ✅ Verified | [Blocker] (After your opponent declares an attack, you may rest this c… |  |
| OP05-048 | Bastille | CHARACTER | ✅ Verified | [DON!! x1] [When Attacking] Place up to 1 Character with a cost of 2 o… |  |
| OP05-049 | Haccha | CHARACTER | ✅ Verified | [DON!! x1] [When Attacking] Return up to 1 Character with a cost of 3 … |  |
| OP05-050 | Hina | CHARACTER | ✅ Verified | [On Play] Draw 1 card if you have 5 or less cards in your hand. |  |
| OP05-051 | Borsalino | CHARACTER | ✅ Verified | [On Play] Place up to 1 Character with a cost of 4 or less at the bott… |  |
| OP05-052 | Maynard | CHARACTER | ✅ Verified | [Blocker] (After your opponent declares an attack, you may rest this c… |  |
| OP05-061 | Uso-Hachi | CHARACTER | ✅ Verified | [DON!! x1] [When Attacking] If you have 8 or more DON!! cards on your … |  |
| OP05-062 | O-Nami | CHARACTER | ✅ Verified | If you have 10 DON!! cards on your field, this Character gains [Blocke… |  |
| OP05-063 | O-Robi | CHARACTER | ✅ Verified | [On Play] If you have 8 or more DON!! cards on your field, K.O. up to … |  |
| OP05-065 | San-Gorou | CHARACTER | ✅ Verified |  |  |
| OP05-070 | Fra-Nosuke | CHARACTER | ✅ Verified | [DON!! x1] If you have 8 or more DON!! cards on your field, this Chara… |  |
| OP05-076 | When You're at Sea You Fight against Pirates!! | EVENT | ✅ Verified | [Main] Look at 3 cards from the top of your deck; reveal up to 1 {Stra… |  |
| OP05-083 | Sterry | CHARACTER | ✅ Verified |  |  |
| OP05-085 | Nefeltari Cobra | CHARACTER | ✅ Verified | [Blocker] (After your opponent declares an attack, you may rest this c… |  |
| OP05-086 | Nefeltari Vivi | CHARACTER | ✅ Verified | If you have 10 or more cards in your trash, this Character gains [Bloc… |  |
| OP05-001 | Sabo | LEADER | ✅ Verified | [DON!! x1] [Opponent's Turn] [Once Per Turn] If your Character with 50… | This card is a little tricky, when there is a DON!! on this leader, if a character that is on this player's field would be KOd, whether by effects OR battle on the OPPONENTS TURN only, then ONCE PER TURN, we can just give that character -1000 power instead. The prompt to use leader effect should show up when a character loses a battle. |
| OP05-003 | Inazuma | CHARACTER | ✅ Verified | If you have a Character with 7000 power or more other than this Charac… | When another character on the player's field has a power of 7000 or more, OTHER than this character. Then this character would gain rush. |
| OP05-004 | Emporio.Ivankov | CHARACTER | ✅ Verified | [Activate: Main] [Once Per Turn] If this Character has 7000 power or m… | When this character has a power of 7000 or more (this includes when it is given DON!!), I should be prompted to select a Revolutionary Army type character with 5000 power or less in my hand to play out. |
| OP05-005 | Karasu | CHARACTER | ✅ Verified | [On Play] If your Leader has the {Revolutionary Army} type, give up to… | This card should be able to target leaders as well to reduce their power. |
| OP05-006 | Koala | CHARACTER | ✅ Verified | [On Play] If your Leader has the {Revolutionary Army} type, give up to… |  |
| OP05-007 | Sabo | CHARACTER | ✅ Verified | [On Play] K.O. up to 2 of your opponent's Characters with a total powe… | This card currently KOs automatically, there should be a prompt to select 2 cards that combined have a power of 4000 or less. i.e, 0 power and 4000 power, 1000 power and 3000 power, etc. |
| OP05-008 | Chaka | CHARACTER | ✅ Verified | [DON!! x1] [Activate: Main] [Once Per Turn] Give up to 2 rested DON!! … |  |
| OP05-014 | Pell | CHARACTER | ✅ Verified | [DON!! x1] [When Attacking] Give up to 1 of your opponent's Characters… |  |
| OP05-018 | Emporio Energy Hormone | EVENT | ✅ Verified | [Counter] Up to 1 of your Leader or Character cards gains +3000 power … |  |
| OP05-023 | Vergo | CHARACTER | ✅ Verified | [DON!! x1] [When Attacking] K.O. up to 1 of your opponent's rested Cha… | I select a rested character with cost 3 or less but it does not actually KO it. |
| OP05-026 | Sarquiss | CHARACTER | ⚠ Needs Fix | [DON!! x1] [When Attacking] [Once Per Turn] You may rest 1 of your Cha… | When this card is set to active again it should be able to attack again, currently it is not.  |
| OP05-030 | Donquixote Rosinante | CHARACTER | ✅ Verified | [Blocker] (After your opponent declares an attack, you may rest this c… | When a rested character is KOd, there should be a prompt to trash this card instead and protect that card that was KOd. |
| OP05-002 | Belo Betty | LEADER | ✅ Verified | [Activate: Main] [Once Per Turn] You may trash 1 {Revolutionary Army} … |  |
| OP05-015 | Belo Betty | CHARACTER | ✅ Verified | [On Play] Look at 5 cards from the top of your deck; reveal up to 1 {R… |  |
| OP05-016 | Morley | CHARACTER | ✅ Verified | [When Attacking] If this Character has 7000 power or more, your oppone… |  |
| OP05-017 | Lindbergh | CHARACTER | ✅ Verified | [When Attacking] If this Character has 7000 power or more, K.O. up to … |  |
| OP05-032 | Pica | CHARACTER | ✅ Verified | [End of Your Turn] ①: Set this Character as active. [Once Per Turn] If… |  |
| OP05-033 | Baby 5 | CHARACTER | ✅ Verified | [Activate: Main] ➀ (You may rest the specified number of DON!! cards i… |  |
| OP05-034 | Baby 5 | CHARACTER | ✅ Verified | [Activate: Main] ➀ (You may rest the specified number of DON!! cards i… |  |
| OP05-037 | Because the Side of Justice Will Be Whichever Side Wins!! | EVENT | ✅ Verified | [Counter] You may trash 1 card from your hand: Up to 1 of your Leader … |  |
| OP05-040 | Birdcage | STAGE | ✅ Verified | If your Leader is [Donquixote Doflamingo], all Characters with a cost … |  |
| OP05-041 | Sakazuki | LEADER | ✅ Verified | [Activate: Main] [Once Per Turn] You may trash 1 card from your hand: … |  |
| OP05-042 | Issho | CHARACTER | ✅ Verified | [On Play] Up to 1 of your opponent's Characters with a cost of 7 or le… |  |
| OP05-045 | Stainless | CHARACTER | ✅ Verified | [Activate: Main] You may trash 1 card from your hand and rest this Cha… |  |
| OP05-046 | Dalmatian | CHARACTER | ✅ Verified | [On K.O.] Draw 1 card and place 1 card from your hand at the bottom of… |  |
| OP05-053 | Mozambia | CHARACTER | ✅ Verified | [Your Turn] [Once Per Turn] When you draw a card outside of your Draw … |  |
| OP05-054 | Monkey.D.Garp | CHARACTER | ✅ Verified | [On Play] Draw 2 cards and place 2 cards from your hand at the bottom … |  |
| OP05-055 | X.Drake | CHARACTER | ✅ Verified | [Blocker] (After your opponent declares an attack, you may rest this c… |  |
| OP05-056 | X.Barrels | CHARACTER | ✅ Verified | [On Play] You may place 1 of your Characters other than this Character… |  |
| OP05-060 | Monkey.D.Luffy | LEADER | ✅ Verified | [Activate: Main] [Once Per Turn] You may add 1 card from the top of yo… |  |
| OP05-064 | Killer | CHARACTER | ✅ Verified | [On Play] Look at 5 cards from the top of your deck; reveal up to 1 {K… |  |
| OP05-066 | Jinbe | CHARACTER | ✅ Verified | [Blocker] (After your opponent declares an attack, you may rest this c… |  |
| OP05-068 | Chopa-Emon | CHARACTER | ✅ Verified | [On Play] If you have 8 or more DON!! cards on your field, set up to 1… |  |
| OP05-072 | Hone-Kichi | CHARACTER | ✅ Verified | [On Play] If you have 8 or more DON!! cards on your field, give up to … |  |
| OP05-073 | Miss Doublefinger(Zala) | CHARACTER | ✅ Verified | [On Play] You may trash 1 card from your hand: Add up to 1 DON!! card … |  |
| OP05-081 | One-Legged Toy Soldier | CHARACTER | ✅ Verified | [Activate: Main] You may trash this Character: Give up to 1 of your op… |  |
| OP05-082 | Shirahoshi | CHARACTER | ⚠ Needs Fix | [Activate: Main] You may rest this Character and place 2 cards from yo… | Okay for the sake of clarity. Let's say Player 1 (P1) is the owner of shirahoshi, when they activate this card it should prompt P1 to select 2 cards in their trash to send to the bottom of the deck in an order that they choose. if they do this, then P2 needs to select a card from their hand to trash if they have 6 or more cards in their hand.  |
| OP05-084 | Saint Charlos | CHARACTER | ✅ Verified | [Your Turn] If the only Characters on your field are {Celestial Dragon… |  |
| OP05-087 | Hakuba | CHARACTER | ✅ Verified | [DON!! x1] [When Attacking] You may K.O. 1 of your Characters other th… |  |
| OP05-089 | Saint Mjosgard | CHARACTER | ✅ Verified | [Activate: Main] ➀ (You may rest the specified number of DON!! cards i… |  |
| OP05-090 | Riku Doldo III | CHARACTER | ✅ Verified | [Blocker] (After your opponent declares an attack, you may rest this c… |  |
| OP05-091 | Rebecca | CHARACTER | ⚠ Needs Fix | [Blocker] [On Play] Add up to 1 black Character card with a cost of 3 … | When this card is played it should prompt the player to add a black character card with a cost of 3 to 7 other than a card with the name Rebecca to their hand from the trash. Even if they do not do this they should then be prompted to play 1 black character card with a cost of 3 or less from their hand rested.  |
| OP05-092 | Saint Rosward | CHARACTER | ✅ Verified | [Your Turn] If the only Characters on your field are {Celestial Dragon… |  |
| OP05-102 | Gedatsu | CHARACTER | ✅ Verified | [On Play] K.O. up to 1 of your opponent's Characters with a cost equal… |  |
| OP05-105 | Satori | CHARACTER | ✅ Verified | [Trigger] You may trash 1 card from your hand: Play this card. |  |
| OP05-106 | Shura | CHARACTER | ✅ Verified | [On Play] Look at 5 cards from the top of your deck; reveal up to 1 {S… |  |
| OP05-108 | Nola | CHARACTER | ✅ Verified |  |  |
| OP05-110 | Holly | CHARACTER | ✅ Verified |  |  |
| OP05-113 | Yama | CHARACTER | ✅ Verified | [Blocker] (After your opponent declares an attack, you may rest this c… |  |
| OP05-117 | Upper Yard | STAGE | ✅ Verified | [On Play] Look at 5 cards from the top of your deck; reveal up to 1 {S… |  |
| OP05-118 | Kaido | CHARACTER | ✅ Verified | [On Play] Draw 4 cards if your opponent has 3 or less Life cards. |  |
| OP05-009 | Toh-Toh | CHARACTER | ⚠ Needs Fix | [On Play] Draw 1 card if your Leader has 0 power or less. | Give the leader 0 power for the sake of this testing.  |
| OP05-029 | Donquixote Doflamingo | CHARACTER | ⚠ Needs Fix | [On Your Opponent's Attack] [Once Per Turn] ➀ (You may rest the specif… | This card is not coded, when the opponent attacks I am not prompted as I should be to select if I want to rest 1 DON!! and if I do rest the 1 DON!! I should be prompted to select an opponent's character with cost of 6 or less to rest.  |
| OP05-038 | Charlestone | EVENT | ⚠ Needs Fix | [Counter] Up to 1 of your Leader or Character cards gains +4000 power … | Currently it gives the +4000 power, but it should also prompt me to set up to 3 DON!! cards as active if I do trash the card from hand.  |
| OP05-039 | Stick-Stickem Meteora | EVENT | ✅ Verified | [Counter] Up to 1 of your Leader or Character cards gains +4000 power … |  |
| OP05-043 | Ulti | CHARACTER | ⚠ Needs Fix | [On Play] If your Leader is multicolored, look at 3 cards from the top… | Leader needs to be multicolored so I can test this effect.  |
| OP05-057 | Hound Blaze | EVENT | ⚠ Needs Fix | [Main] Up to 1 of your Leader or Character cards gains +3000 power dur… | This card should give a leader or character +3000 power, that should be a prompt to the player. Then I should be prompted to place 1 character with a cost of 2 or less to the bottom of the owner's deck.  |
| OP05-058 | It's a Waste of Human Life!! | EVENT | ⚠ Needs Fix | [Main] Place all Characters with a cost of 3 or less at the bottom of … | When this card is played all characters with acost of 8 or less should be sent to the bottom of the owner's deck. Then both players need to select which cards to trash from their hand until they both have 5 cards each in hand.  |
| OP05-059 | Let Us Begin the World of Violence!!! | EVENT | ⚠ Needs Fix | [Main] If your Leader is multicolored, draw 1 card. Then, return up to… | Leader needs to be multicolored so we can test this card  |
| OP05-067 | Zoro-Juurou | CHARACTER | ✅ Verified | [When Attacking] If you have 3 or less Life cards, add up to 1 DON!! c… |  |
| OP05-069 | Trafalgar Law | CHARACTER | ⚠ Needs Fix | [When Attacking] If your opponent has more DON!! cards on their field … | Opponent needs to have more DON!! so I can test this card.  |
| OP05-071 | Bepo | CHARACTER | ⚠ Needs Fix | [When Attacking] If your opponent has more DON!! cards on their field … | Opponent needs to have more DON!! so I can test this card.  |
| OP05-075 | Mr.1(Daz.Bonez) | CHARACTER | ⚠ Needs Fix | [On Your Opponent's Attack] [Once Per Turn] DON!! −1 (You may return t… | The on your opponent's attack prompt should still pop up even if I do not have a valid target to play. I should just be able to choose not to use the effect. Currently when the opponent attacks there is no prompt at all.  |
| OP05-077 | Gamma Knife | EVENT | ⚠ Needs Fix | [Main] DON!! −1 (You may return the specified number of DON!! cards fr… | I should be prompted when I play this card if I want to DON!! -1. If I do, then I should be prompted to select an opponent's character to give -5000 power for the turn.  |
| OP05-078 | Punk Rotten | EVENT | ⚠ Needs Fix | [Main] DON!! −1 (You may return the specified number of DON!! cards fr… | Make the leader a Kid Pirates type so I can test.  |
| OP05-079 | Viola | CHARACTER | ⚠ Needs Fix | [On Play] Your opponent places 3 cards from their trash at the bottom … | Put cards in the opponent's trash so I can test this card.  |
| OP05-080 | Elizabello II | CHARACTER | ⚠ Needs Fix | [When Attacking] [Once Per Turn] You may return 20 cards from your tra… | Add 20 cards to the trash instead of 10.  |
| OP05-088 | Mansherry | CHARACTER | ⚠ Needs Fix | [Activate: Main] ➀ (You may rest the specified number of DON!! cards i… | This card will not let me activate the effect. But what it should do is: Prompt the player to rest 1 DON!!, if they choose to do so, they can then rest this character and place 2 cards from their trash to the bottom of their deck in an order that they choose. If they do this then they should be prompted to select a black character card with a cost of 3 to 5 from the trash to their hand. Ensure this simulation has all of the relevant cards to do this.  |
| OP05-093 | Rob Lucci | CHARACTER | ⚠ Needs Fix | [On Play] You may place 3 cards from your trash at the bottom of your … | I am only prompted to select 1 card when I am choosign the 3 to send from trash to the bottom of the deck. The KO does work as intended, but the cards are also still in the trash not moved to bottom of the deck.  |
| OP05-094 | Haute Couture Patch★Work | EVENT | ⚠ Needs Fix | [Main] Give up to 1 of your opponent's Characters −3 cost during this … | This card will not even let me play it out.  |
| OP05-095 | Dragon Claw | EVENT | ⚠ Needs Fix | [Counter] Up to 1 of your Leader or Character cards gains +4000 power … | Add 15 cards to the trash in this simulation so I can test.  |
| OP05-097 | Mary Geoise | STAGE | ✅ Verified | [Your Turn] The cost of playing {Celestial Dragons} type Character car… |  |
| OP05-098 | Enel | LEADER | ⚠ Needs Fix | [Opponent's Turn] [Once Per Turn] When your number of Life cards becom… | When this leader reaches 0 life on their opponent's turn they should be prompted if they want to add 1 card from the top of their deck to their life. And then they should be prompted to trash 1 card from hand (if they have a card in hand they HAVE to do this), if they do not have a card in hand this step is skipped.  |

| ID | Status | Type | Notes |
|----|--------|------|-------|
| OP05-010 | Nico Robin | CHARACTER | ✅ Verified | [On Play] K.O. up to 1 of your opponent's Characters with 1000 power o… |  |

# Card Effect Status — OP06
| OP06-008 | Schneider | CHARACTER | ✅ Verified |  |  |
| OP06-010 | Douglas Bullet | CHARACTER | ✅ Verified | If your Leader has the {FILM} type, this Character gains [Blocker]. (A… |  |
| OP06-012 | Bear.King | CHARACTER | ✅ Verified | If your opponent has a Leader or Character with a base power of 6000 o… |  |
| OP06-001 | Uta | LEADER | ✅ Verified | [When Attacking] You may trash 1 {FILM} type card from your hand: Give… |  |
| OP06-002 | Inazuma | CHARACTER | ✅ Verified | If this Character has 7000 power or more, this Character gains [Banish… |  |
| OP06-004 | Baron Omatsuri | CHARACTER | ✅ Verified | [On Play] Play up to 1 [Lily Carnation] from your hand. |  |
| OP06-007 | Shanks | CHARACTER | ✅ Verified | [On Play] K.O. up to 1 of your opponent's Characters with 10000 power … |  |
| OP06-009 | Shuraiya | CHARACTER | ✅ Verified | [Blocker] (After your opponent declares an attack, you may rest this c… |  |
| OP06-013 | Monkey.D.Luffy | CHARACTER | ✅ Verified | [On Play] Look at 3 cards from the top of your deck; reveal up to 1 {F… |  |
| OP06-015 | Lily Carnation | CHARACTER | ✅ Verified | [Activate: Main] [Once Per Turn] You may trash 1 of your Characters wi… |  |
| OP06-016 | Raise Max | CHARACTER | ✅ Verified | [Activate: Main] You may place this Character at the bottom of the own… |  |
| OP06-017 | Meteor-Strike of Love | EVENT | ✅ Verified | [Main]/[Counter] You may add 1 card from the top of your Life cards to… |  |
| OP06-019 | Blue Dragon Seal Water Stream | EVENT | ✅ Verified | [Main] K.O. up to 1 of your opponent's Characters with 5000 power or l… |  |
| OP06-021 | Perona | LEADER | ✅ Verified | [Activate: Main] [Once Per Turn] Choose one: • Rest up to 1 of your op… |  |
| OP06-113 | Raki | CHARACTER | ✅ Verified | If you have a {Shandian Warrior} type Character other than [Raki], thi… |  |
| OP06-110 | Nekomamushi | CHARACTER | ✅ Verified | [DON!! x2] This Character can also attack your opponent's active Chara… |  |
| OP06-105 | Genbo | CHARACTER | ✅ Verified |  |  |
| OP06-104 | Kikunojo | CHARACTER | ✅ Verified | [On K.O.] If your opponent has 3 or less Life cards, add up to 1 card … |  |

| ID | Status | Type | Notes |
|----|--------|------|-------|
| OP06-005 | Gasparde | CHARACTER | ✅ Verified |  |  |

# Card Effect Status — OP07
| OP07-003 | Outlook III | CHARACTER | ✅ Verified | [Activate: Main] You may trash this Character: Give up to 2 of your op… |  |
| OP07-005 | Carina | CHARACTER | ✅ Verified | [Blocker] (After your opponent declares an attack, you may rest this c… |  |
| OP07-007 | Dice | CHARACTER | ✅ Verified |  |  |
| OP07-008 | Mr. Tanaka | CHARACTER | ✅ Verified | [Blocker] (After your opponent declares an attack, you may rest this c… |  |
| OP07-011 | Bluejam | CHARACTER | ✅ Verified | [DON!! x1] [When Attacking] K.O. up to 1 of your opponent's Characters… |  |
| OP07-012 | Porchemy | CHARACTER | ✅ Verified | [On Play] Give up to 1 of your opponent's Characters −1000 power durin… |  |
| OP07-013 | Masked Deuce | CHARACTER | ✅ Verified | [On Play] If your Leader is [Portgas.D.Ace], look at 5 cards from the … |  |
| OP07-014 | Moda | CHARACTER | ⚠ Needs Fix | [Your Turn] [On Play] Up to 1 of your [Portgas.D.Ace] cards gains +200… | Should prompt the player to select which Portgas D. Ace card to give +2000 power for the turn. It currently does it automatically.  |

| ID | Status | Type | Notes |
|----|--------|------|-------|
| OP07-002 | Ain | CHARACTER | ✅ Verified | [On Play] Set the power of up to 1 of your opponent's Characters to 0 … |  |
