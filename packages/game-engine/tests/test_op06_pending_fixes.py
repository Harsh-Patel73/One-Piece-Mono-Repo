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
from optcg_engine.effects.effect_registry import return_don_to_deck
from optcg_engine.effects.sets.op06_effects import (
    op06_028_zeo,
    op06_044_gion,
    op06_056_murakumo,
    op06_057_tears,
    op06_065_niji_5,
    op06_074_zephyr,
    op06_080_moria_leader,
    op06_092_brook,
    op06_095_shadows_asgard,
    op06_096_nothing_at_all,
    op06_101_onami,
    op06_103_kawamatsu,
    op06_112_raizo,
)
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
    trigger="",
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
        trigger=trigger,
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

    def test_op06_044_gion_is_once_per_turn(self):
        gion = make_card("OP06-044", "Gion", cost=4, power=5000)
        first = make_card("hand-1", "First Hand")
        second = make_card("hand-2", "Second Hand")
        self.player1.cards_in_play = [gion]
        self.player2.hand = [first, second]

        self.assertTrue(op06_044_gion(self.game, self.player1, gion))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertNotIn(first, self.player2.hand)
        self.assertIn(first, self.player2.deck)

        self.assertFalse(op06_044_gion(self.game, self.player1, gion))
        self.assertIsNone(self.game.pending_choice)
        self.assertEqual([second], self.player2.hand)

    def test_op06_056_prompts_for_cost_1_after_cost_2(self):
        cost2 = make_card("cost2", "Cost 2", cost=2)
        cost1 = make_card("cost1", "Cost 1", cost=1)
        self.player2.cards_in_play = [cost2, cost1]

        self.assertTrue(op06_056_murakumo(self.game, self.player1, make_card("OP06-056", "Murakumo", card_type="EVENT")))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertIn("cost 2", self.game.pending_choice.prompt)

        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertNotIn(cost2, self.player2.cards_in_play)
        self.assertIsNotNone(self.game.pending_choice)
        self.assertIn("cost 1", self.game.pending_choice.prompt)

        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertNotIn(cost1, self.player2.cards_in_play)
        self.assertEqual([cost2, cost1], self.player2.deck)

    def test_op06_057_can_play_cost_2_from_hand_after_reveal(self):
        revealed = make_card("revealed", "Revealed Event", card_type="EVENT", cost=1)
        from_hand = make_card("hand-play", "Hand Cost 2", card_type="CHARACTER", cost=2)
        self.player1.deck = [revealed]
        self.player1.hand = [from_hand]

        self.assertTrue(op06_057_tears(self.game, self.player1, make_card("OP06-057", "Tears", card_type="EVENT")))
        self.assertTrue(self.game.resolve_pending_choice([]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertIn("from hand", " ".join(opt["label"] for opt in self.game.pending_choice.options))

        hand_option = next(opt["id"] for opt in self.game.pending_choice.options if "from hand" in opt["label"])
        self.assertTrue(self.game.resolve_pending_choice([hand_option]))
        self.assertIn(from_hand, self.player1.cards_in_play)
        self.assertIsNotNone(self.game.pending_choice)
        self.assertIn("top or bottom", self.game.pending_choice.prompt.lower())

        self.assertTrue(self.game.resolve_pending_choice(["top"]))
        self.assertEqual([revealed], self.player1.deck)

    def test_op06_065_prompts_for_both_modes_when_don_counts_qualify(self):
        ko_target = make_card("ko-target", "KO Target", cost=2)
        return_target = make_card("return-target", "Return Target", cost=4)
        self.player1.don_pool = ["active"] * 5
        self.player2.don_pool = ["active"] * 5
        self.player2.cards_in_play = [ko_target, return_target]

        self.assertTrue(op06_065_niji_5(self.game, self.player1, make_card("OP06-065", "Niji", cost=5)))

        self.assertIsNotNone(self.game.pending_choice)
        self.assertEqual({"ko", "rth"}, {opt["id"] for opt in self.game.pending_choice.options})

    def test_op06_074_accepts_numeric_don_choice_and_koes_target(self):
        zephyr = make_card("OP06-074", "Zephyr", cost=7)
        target = make_card("target", "Small Target", cost=3, power=5000)
        self.player1.don_pool = ["active", "active"]
        self.player2.cards_in_play = [target]

        self.assertTrue(op06_074_zephyr(self.game, self.player1, zephyr))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertIn("DON", self.game.pending_choice.prompt)

        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertEqual(["active"], self.player1.don_pool)
        self.assertIsNotNone(self.game.pending_choice)

        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertNotIn(target, self.player2.cards_in_play)
        self.assertIn(target, self.player2.trash)
        self.assertTrue(getattr(target, "effects_negated_this_turn", False))

    def test_op06_076_field_character_triggers_when_don_is_returned(self):
        kamazo = make_card("OP06-076", "Hitokiri Kamazo", cost=4)
        target = make_card("target", "Cost 2 Target", cost=2)
        self.player1.cards_in_play = [kamazo]
        self.player1.don_pool = ["active", "active"]
        self.player2.cards_in_play = [target]

        self.assertFalse(return_don_to_deck(self.game, self.player1, 1, source_card=kamazo))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertIn("Kamazo", self.game.pending_choice.prompt)

        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIn(target, self.player2.trash)

    def test_op06_076_prompt_is_not_overwritten_by_don_minus_effect_followup(self):
        zephyr = make_card("OP06-074", "Zephyr", cost=7)
        kamazo = make_card("OP06-076", "Hitokiri Kamazo", cost=4)
        kamazo_target = make_card("kamazo-target", "Kamazo Target", cost=2, power=6000)
        zephyr_target = make_card("zephyr-target", "Zephyr Target", cost=3, power=5000)
        self.player1.cards_in_play = [kamazo]
        self.player1.don_pool = ["active", "active"]
        self.player2.cards_in_play = [kamazo_target, zephyr_target]

        self.assertTrue(op06_074_zephyr(self.game, self.player1, zephyr))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertIn("Kamazo", self.game.pending_choice.prompt)

        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIn(kamazo_target, self.player2.trash)
        self.assertIsNotNone(self.game.pending_choice)
        self.assertIn("negate", self.game.pending_choice.prompt.lower())

        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIn(zephyr_target, self.player2.trash)

    def test_op06_080_leader_effect_is_optional_before_resting_don(self):
        self.player1.leader.id = "OP06-080"
        self.player1.leader.name = "Gecko Moria"
        self.player1.leader.attached_don = 1
        self.player1.don_pool = ["active", "active", "active"]
        self.player1.hand = [make_card("discard", "Discard")]

        self.assertTrue(op06_080_moria_leader(self.game, self.player1, self.player1.leader))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertIn("Use Gecko Moria", self.game.pending_choice.prompt)
        self.assertEqual(["active", "active", "active"], self.player1.don_pool)

        self.assertTrue(self.game.resolve_pending_choice(["no"]))
        self.assertEqual(["active", "active", "active"], self.player1.don_pool)
        self.assertEqual(1, len(self.player1.hand))

    def test_op06_092_prompts_for_trash_character_or_trash_bottom(self):
        self.player2.cards_in_play = [make_card("opp", "Opponent Cost 4", cost=4)]
        self.player2.trash = [make_card(f"trash-{i}", f"Trash {i}") for i in range(3)]

        self.assertTrue(op06_092_brook(self.game, self.player1, make_card("OP06-092", "Brook", cost=4)))

        self.assertIsNotNone(self.game.pending_choice)
        self.assertEqual({"trash_char", "trash_bottom"}, {opt["id"] for opt in self.game.pending_choice.options})

    def test_op06_095_gives_default_power_and_extra_per_actual_ko(self):
        tb1 = make_card("tb1", "Thriller Bark 1", cost=1, card_origin="Thriller Bark Pirates")
        tb2 = make_card("tb2", "Thriller Bark 2", cost=2, card_origin="Thriller Bark Pirates")
        self.player1.cards_in_play = [tb1, tb2]

        self.assertTrue(op06_095_shadows_asgard(self.game, self.player1, make_card("OP06-095", "Shadows Asgard", card_type="EVENT")))
        self.assertEqual(1000, getattr(self.player1.leader, "power_modifier", 0))

        self.assertTrue(self.game.resolve_pending_choice(["0", "1"]))
        self.assertEqual(3000, getattr(self.player1.leader, "power_modifier", 0))
        self.assertIn(tb1, self.player1.trash)
        self.assertIn(tb2, self.player1.trash)

    def test_op06_096_life_payment_protects_cost_7_or_less_characters(self):
        protected = make_card("protected", "Protected", cost=7)
        too_big = make_card("too-big", "Too Big", cost=8)
        life = make_card("life", "Life")
        self.player1.cards_in_play = [protected, too_big]
        self.player1.life_cards = [life]

        self.assertTrue(op06_096_nothing_at_all(self.game, self.player1, make_card("OP06-096", "Nothing At All", card_type="EVENT")))
        self.assertTrue(self.game.resolve_pending_choice(["pay"]))

        self.assertIn(life, self.player1.hand)
        self.assertTrue(getattr(protected, "cannot_be_ko_in_battle", False))
        self.assertFalse(getattr(too_big, "cannot_be_ko_in_battle", False))

    def test_op06_101_grants_banish_and_banished_life_skips_trigger(self):
        trigger_life = make_card("trig", "Trigger Life", trigger="Trigger")

        self.assertTrue(op06_101_onami(self.game, self.player1, make_card("OP06-101", "O-Nami", cost=1)))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertTrue(getattr(self.player1.leader, "has_banish", False))

        paused = self.game._handle_life_card(self.player2, trigger_life, True, True, self.player1.leader)

        self.assertFalse(paused)
        self.assertIn(trigger_life, self.player2.trash)
        self.assertNotIn(trigger_life, self.player2.hand)

    def test_op06_103_targets_opponent_zero_power_character_to_their_life(self):
        kawamatsu = make_card("OP06-103", "Kawamatsu", cost=3)
        zero = make_card("zero", "Zero Power", power=0)
        discard1 = make_card("discard-1", "Discard 1")
        discard2 = make_card("discard-2", "Discard 2")
        self.player1.hand = [discard1, discard2]
        self.player2.cards_in_play = [zero]

        self.assertTrue(op06_103_kawamatsu(self.game, self.player1, kawamatsu))
        self.assertTrue(self.game.resolve_pending_choice(["0", "1"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertIn("opponent", self.game.pending_choice.prompt.lower())

        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["top"]))

        self.assertNotIn(zero, self.player2.cards_in_play)
        self.assertEqual(zero, self.player2.life_cards[-1])
        self.assertTrue(getattr(zero, "is_face_up", False))
        self.assertEqual([], self.player1.life_cards)

    def test_op06_112_prompts_for_zero_or_one_don_after_discard(self):
        raizo = make_card("OP06-112", "Raizo", cost=3)
        discard = make_card("discard", "Discard")
        self.player1.hand = [discard]
        self.player2.don_pool = ["active", "rested"]

        self.assertTrue(op06_112_raizo(self.game, self.player1, raizo))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertEqual(0, self.game.pending_choice.min_selections)

        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertIn("up to 1", self.game.pending_choice.prompt)
        self.assertEqual(0, self.game.pending_choice.min_selections)
        self.assertEqual(["active", "rested"], self.player2.don_pool)

        self.assertTrue(self.game.resolve_pending_choice([]))
        self.assertEqual(["active", "rested"], self.player2.don_pool)


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
        self.assertIs(tc, player.life_cards[-1])
        self.assertNotIn(tc, player.hand)
        self.assertTrue(any(c.name == "Arlong" and c.cost == 3 for c in player.hand))

    def test_cli_tester_seeds_four_valid_germa_trash_targets_for_op06_062(self):
        judge = make_card("OP06-062", "Vinsmoke Judge", cost=8, power=8000)

        _, player, _ = build_game_state(judge, "on_play")

        valid = [
            c for c in player.trash
            if "GERMA 66" in (c.card_origin or "")
            and c.card_type == "CHARACTER"
            and (c.power or 0) <= 4000
        ]
        self.assertGreaterEqual(len({c.name for c in valid}), 4)


if __name__ == "__main__":
    unittest.main()
