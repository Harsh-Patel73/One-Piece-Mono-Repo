import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from optcg_engine.game_engine import GameState, PendingChoice, Player
from optcg_engine.models.cards import Card
from optcg_engine.effects.effect_registry import (
    create_play_from_hand_choice,
    create_play_from_trash_choice,
    register_effect,
    search_top_cards,
)


def make_card(card_id, name, *, card_type="CHARACTER", cost=1, power=1000, effect=""):
    return Card(
        id=card_id,
        id_normal=card_id,
        name=name,
        card_type=card_type,
        cost=cost,
        power=power,
        counter=0,
        colors=["Red"],
        life=0,
        effect=effect,
        image_link="",
        attribute="Strike",
        card_origin="Test",
        trigger="",
    )


def make_player(name, prefix):
    leader = make_card(f"{prefix}-leader", f"{name} Leader", card_type="LEADER", cost=0, power=5000)
    player = Player(name, [], leader, player_id=f"{prefix}-pid")
    player.hand = []
    player.deck = []
    player.cards_in_play = []
    player.life_cards = []
    player.trash = []
    player.don_pool = []
    return player


@register_effect("TEST-PLAY-ONPLAY", "on_play", "Mark that this card's On Play resolved")
def _test_play_on_play(game_state, player, card):
    card.test_on_play_count = getattr(card, "test_on_play_count", 0) + 1
    card.test_on_play_player = player.name
    return True


@register_effect("TEST-PLAY-ONPLAY", "trigger", "Play this card from trigger")
def _test_trigger_play_this_card(game_state, player, card):
    game_state.play_card_to_field_by_effect(
        player,
        card,
        log_message=f"{player.name} played {card.name} from trigger",
    )
    return True


@register_effect("TEST-TRIGGER-PLAY-FROM-HAND", "trigger", "Play a character from hand")
def _test_trigger_play_from_hand(game_state, player, card):
    targets = [
        hand_card
        for hand_card in player.hand
        if hand_card.id == "TEST-PLAY-ONPLAY"
    ]
    return create_play_from_hand_choice(
        game_state,
        player,
        targets,
        source_card=card,
        prompt="Trigger: play a test character from hand",
    )


def prime_trigger_response(game, player, life_card):
    attacker_player = game.player2 if player is game.player1 else game.player1
    game.pending_attack = {
        "attacker": attacker_player.leader,
        "attacker_player": attacker_player,
        "defender_player": player,
        "has_double_attack": False,
        "double_attack_processed": False,
        "has_banish": False,
        "pending_trigger": {
            "life_card": life_card,
            "life_card_id": life_card.id,
            "life_card_name": life_card.name,
            "trigger_text": life_card.trigger,
            "player_id": player.player_id,
            "player_index": 0 if player is game.player1 else 1,
        },
    }
    game.awaiting_response = "trigger"


class EffectPlayOnPlayTests(unittest.TestCase):
    def setUp(self):
        self.player1 = make_player("P1", "p1")
        self.player2 = make_player("P2", "p2")
        self.game = GameState(self.player1, self.player2)

    def test_play_from_hand_choice_triggers_on_play(self):
        played = make_card("TEST-PLAY-ONPLAY", "On Play Target", cost=3)
        self.player1.hand = [played]

        self.assertTrue(create_play_from_hand_choice(self.game, self.player1, [played]))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertIn(played, self.player1.cards_in_play)
        self.assertEqual(1, getattr(played, "test_on_play_count", 0))
        self.assertEqual("P1", played.test_on_play_player)

    def test_play_from_trash_choice_triggers_on_play(self):
        played = make_card("TEST-PLAY-ONPLAY", "On Play Target", cost=3)
        self.player1.trash = [played]

        self.assertTrue(create_play_from_trash_choice(self.game, self.player1, [played], rest_on_play=False))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertIn(played, self.player1.cards_in_play)
        self.assertEqual(1, getattr(played, "test_on_play_count", 0))

    def test_search_play_to_field_triggers_on_play(self):
        played = make_card("TEST-PLAY-ONPLAY", "On Play Target", cost=3)
        self.player1.deck = [played]

        self.assertTrue(
            search_top_cards(
                self.game,
                self.player1,
                1,
                filter_fn=lambda c: c.card_type == "CHARACTER",
                play_to_field=True,
            )
        )
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertIn(played, self.player1.cards_in_play)
        self.assertEqual(1, getattr(played, "test_on_play_count", 0))

    def test_legacy_play_from_hand_or_trash_dispatch_triggers_on_play(self):
        played = make_card("TEST-PLAY-ONPLAY", "On Play Target", cost=3)
        self.player1.hand = [played]
        self.game.pending_choice = PendingChoice(
            choice_id="legacy-play",
            choice_type="select_cards",
            prompt="Play a card",
            options=[{"id": "0", "label": played.name, "card_id": played.id, "card_name": played.name}],
            callback_action="play_from_hand_or_trash",
            callback_data={
                "player_index": 0,
                "target_cards": [{"id": played.id, "name": played.name}],
            },
        )

        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertIn(played, self.player1.cards_in_play)
        self.assertEqual(1, getattr(played, "test_on_play_count", 0))

    def test_effect_play_uses_controller_context_for_on_play(self):
        played = make_card("TEST-PLAY-ONPLAY", "Opponent On Play Target", cost=3)

        self.game.play_card_to_field_by_effect(self.player2, played)

        self.assertIn(played, self.player2.cards_in_play)
        self.assertEqual(1, getattr(played, "test_on_play_count", 0))
        self.assertEqual("P2", played.test_on_play_player)
        self.assertIs(self.game.current_player, self.player1)
        self.assertIs(self.game.opponent_player, self.player2)

    def test_trigger_play_this_card_triggers_on_play(self):
        life_card = make_card(
            "TEST-PLAY-ONPLAY",
            "Trigger On Play Target",
            cost=3,
        )
        life_card.trigger = "[Trigger] Play this card."
        prime_trigger_response(self.game, self.player1, life_card)

        self.assertTrue(self.game.respond_trigger(True))

        self.assertIn(life_card, self.player1.cards_in_play)
        self.assertNotIn(life_card, self.player1.trash)
        self.assertEqual(1, getattr(life_card, "test_on_play_count", 0))
        self.assertEqual("P1", life_card.test_on_play_player)

    def test_trigger_play_from_hand_choice_triggers_on_play(self):
        trigger_card = make_card(
            "TEST-TRIGGER-PLAY-FROM-HAND",
            "Trigger Source",
            card_type="EVENT",
            cost=1,
            power=0,
        )
        trigger_card.trigger = "[Trigger] Play up to 1 Character from your hand."
        played = make_card("TEST-PLAY-ONPLAY", "On Play Target", cost=3)
        self.player1.hand = [played]
        prime_trigger_response(self.game, self.player1, trigger_card)

        self.assertTrue(self.game.respond_trigger(True))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertIn(played, self.player1.cards_in_play)
        self.assertNotIn(played, self.player1.hand)
        self.assertEqual(1, getattr(played, "test_on_play_count", 0))
        self.assertEqual("P1", played.test_on_play_player)


if __name__ == "__main__":
    unittest.main()
