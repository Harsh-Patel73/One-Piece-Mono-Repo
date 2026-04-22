import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from optcg_engine.game_engine import GameState, Player
from optcg_engine.models.cards import Card
from optcg_engine.effects.sets.op06_effects import op06_028_zeo, op06_057_tears
from card_effect_tester import build_game_state


def make_card(
    card_id,
    name,
    *,
    card_type="CHARACTER",
    cost=1,
    power=1000,
    life=0,
    effect="",
    card_origin="Test",
):
    return Card(
        id=card_id,
        id_normal=card_id,
        name=name,
        card_type=card_type,
        cost=cost,
        power=power,
        counter=0,
        colors=["Blue"],
        life=life,
        effect=effect,
        image_link="",
        attribute="Slash",
        card_origin=card_origin,
        trigger="",
    )


def make_player(name, prefix):
    leader = make_card(
        f"{prefix}-leader",
        f"{name} Leader",
        card_type="LEADER",
        cost=0,
        power=5000,
        life=0,
    )
    player = Player(name, [], leader, player_id=f"{prefix}-pid")
    player.hand = []
    player.deck = []
    player.cards_in_play = []
    player.life_cards = []
    player.trash = []
    player.don_pool = []
    return player


class OP06PendingFixTests(unittest.TestCase):
    def setUp(self):
        self.player1 = make_player("P1", "p1")
        self.player2 = make_player("P2", "p2")
        self.game = GameState(self.player1, self.player2)

    def test_op06_028_resolves_power_and_life_without_rested_don(self):
        self.player1.leader.card_origin = "New Fish-Man Pirates"
        zeo = make_card("OP06-028", "Zeo", cost=3, power=4000)
        zeo.attached_don = 1
        self.player1.cards_in_play = [zeo]
        self.player1.don_pool = ["active"]
        life_card = make_card("life", "Life Card")
        self.player1.life_cards = [life_card]

        self.assertTrue(op06_028_zeo(self.game, self.player1, zeo))

        self.assertIsNone(self.game.pending_choice)
        self.assertEqual(1000, getattr(zeo, "power_modifier", 0))
        self.assertIn(life_card, self.player1.hand)
        self.assertEqual([], self.player1.life_cards)

    def test_op06_028_rested_don_choice_is_optional(self):
        self.player1.leader.card_origin = "New Fish-Man Pirates"
        zeo = make_card("OP06-028", "Zeo", cost=3, power=4000)
        zeo.attached_don = 1
        self.player1.cards_in_play = [zeo]
        self.player1.don_pool = ["rested", "active"]
        life_card = make_card("life", "Life Card")
        self.player1.life_cards = [life_card]

        self.assertTrue(op06_028_zeo(self.game, self.player1, zeo))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertEqual(0, self.game.pending_choice.min_selections)

        self.assertTrue(self.game.resolve_pending_choice([]))
        self.assertEqual(["rested", "active"], self.player1.don_pool)
        self.assertEqual(1000, getattr(zeo, "power_modifier", 0))
        self.assertIn(life_card, self.player1.hand)

    def test_op06_028_selected_rested_don_becomes_active(self):
        self.player1.leader.card_origin = "New Fish-Man Pirates"
        zeo = make_card("OP06-028", "Zeo", cost=3, power=4000)
        zeo.attached_don = 1
        self.player1.cards_in_play = [zeo]
        self.player1.don_pool = ["rested", "active"]

        self.assertTrue(op06_028_zeo(self.game, self.player1, zeo))
        self.assertIsNotNone(self.game.pending_choice)

        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertEqual(["active", "active"], self.player1.don_pool)
        self.assertEqual(1000, getattr(zeo, "power_modifier", 0))

    def test_op06_057_invalid_top_card_prompts_for_top_or_bottom(self):
        bad_top = make_card("bad-top", "Not a Character", card_type="EVENT", cost=1)
        self.player1.deck = [bad_top]

        self.assertTrue(op06_057_tears(self.game, self.player1, make_card("OP06-057", "Tears", card_type="EVENT")))
        self.assertIsNotNone(self.game.pending_choice)

        self.assertTrue(self.game.resolve_pending_choice([]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertIn("top or bottom", self.game.pending_choice.prompt.lower())
        self.assertEqual({"top", "bottom"}, {opt["id"] for opt in self.game.pending_choice.options})

        self.assertTrue(self.game.resolve_pending_choice(["top"]))
        self.assertEqual([bad_top], self.player1.deck)

    def test_op06_057_valid_top_card_prompts_to_play(self):
        playable = make_card("playable", "Cost 2 Character", card_type="CHARACTER", cost=2)
        self.player1.deck = [playable]

        self.assertTrue(op06_057_tears(self.game, self.player1, make_card("OP06-057", "Tears", card_type="EVENT")))
        self.assertTrue(self.game.resolve_pending_choice([]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertIn("play", self.game.pending_choice.prompt.lower())

        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIn(playable, self.player1.cards_in_play)
        self.assertEqual([], self.player1.deck)
        self.assertEqual(self.game.turn_count, getattr(playable, "played_turn", None))


class OP06TesterSeedTests(unittest.TestCase):
    def test_cli_tester_seeds_uta_leader_for_op06_011(self):
        tot_musica = make_card("OP06-011", "Tot Musica", cost=5, power=6000)

        _, player, _ = build_game_state(tot_musica, "activate")

        self.assertEqual("OP06-001", player.leader.id)
        self.assertEqual("Uta", player.leader.name)
        self.assertTrue(any(c.name == "Uta" and not c.is_resting for c in player.cards_in_play))

    def test_cli_tester_places_op06_031_in_life_for_trigger(self):
        hatchan = make_card("OP06-031", "Hatchan", cost=3, power=4000)

        _, player, tc = build_game_state(hatchan, "trigger")

        self.assertIn(tc, player.life_cards)
        self.assertNotIn(tc, player.hand)
        self.assertTrue(any(c.name == "Arlong" and c.cost == 3 for c in player.hand))


if __name__ == "__main__":
    unittest.main()
