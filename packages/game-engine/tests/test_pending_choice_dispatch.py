import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from optcg_engine.effects.effect_registry import filter_by_cost_range, filter_by_max_cost
from optcg_engine.effects.sets.op01_effects import op01_003_luffy_leader
from optcg_engine.effects.sets.op04_effects import (
    op04_001_vivi_activate,
    op04_004_karoo,
    op04_006_koza,
    op04_009_duck_troops,
    op04_010_chopper,
    op04_011_nami,
    op04_021_viola,
    op04_020_issho_eot,
    op04_039_rebecca_activate,
    op04_040_queen_leader,
    op04_042_ipponmatsu,
    op04_050_hanger,
    op04_053_page_one,
    op04_066_valentine,
    op04_069_bon_kurei,
    op04_084_stussy,
    op04_090_luffy_activate,
    op04_110_pound_ko,
    op04_016_bad_manners,
    op04_017_happiness_punch,
    op04_018_vertigo_dance,
    op04_019_doffy_leader,
    op04_020_issho_continuous,
    op04_119_rosinante_play,
)
from optcg_engine.game_engine import GameState, PendingChoice, Player
from optcg_engine.models.cards import Card


def make_card(card_id: str, name: str, *, card_type: str = "Character", cost: int = 1, power: int = 1000, life: int = 0) -> Card:
    return Card(
        id=card_id,
        id_normal=card_id,
        name=name,
        card_type=card_type,
        cost=cost,
        power=power,
        counter=0,
        colors=["Red"],
        life=life,
        effect="",
        image_link="",
        attribute="Slash",
        card_origin="Test",
        trigger="",
    )


def make_player(name: str, prefix: str) -> Player:
    leader = make_card(f"{prefix}-leader", f"{name} Leader", card_type="Leader", cost=0, power=5000, life=0)
    deck = [make_card(f"{prefix}-deck-{idx}", f"{name} Deck {idx}", cost=idx % 6) for idx in range(12)]
    return Player(name, deck, leader, player_id=f"{prefix}-pid")


class PendingChoiceDispatchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.player1 = make_player("P1", "p1")
        self.player2 = make_player("P2", "p2")
        self.game = GameState(self.player1, self.player2)

    def make_choice(self, action: str, **data) -> PendingChoice:
        return PendingChoice(
            choice_id=f"choice-{action}",
            choice_type="select_target",
            prompt="Test",
            callback_action=action,
            callback_data={"player_index": 0, **data},
        )

    def test_callback_precedence_preserves_chained_choice(self) -> None:
        def callback(selected):
            self.game.pending_choice = PendingChoice(
                choice_id="follow-up",
                choice_type="choose_option",
                prompt="Follow-up",
                callback_action="choose_option",
                callback_data={"player_index": 0},
            )

        self.game.pending_choice = PendingChoice(
            choice_id="initial",
            choice_type="choose_option",
            prompt="Initial",
            callback=callback,
            callback_data={"player_index": 0},
        )

        self.assertTrue(self.game.resolve_pending_choice(["x"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertEqual("follow-up", self.game.pending_choice.choice_id)

    def test_unknown_action_raises_in_strict_mode(self) -> None:
        self.game.pending_choice = self.make_choice("unknown_action")
        with patch.dict(os.environ, {"OPTCG_STRICT_PENDING_CHOICE": "1"}, clear=False):
            with self.assertRaises(ValueError):
                self.game.resolve_pending_choice(["0"])

    def test_invalid_index_logs_and_does_not_mutate(self) -> None:
        target = make_card("opp-1", "Opponent Character", cost=3)
        self.player2.cards_in_play.append(target)
        self.game.pending_choice = self.make_choice("ko_target", target_cards=[{"id": target.id}])

        self.assertTrue(self.game.resolve_pending_choice(["9"]))
        self.assertIn(target, self.player2.cards_in_play)
        self.assertIn("Invalid selection for ko_target", self.game.action_logs)

    def test_trash_from_hand(self) -> None:
        card = self.player1.hand[0]
        self.game.pending_choice = self.make_choice("trash_from_hand")

        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertNotIn(card, self.player1.hand)
        self.assertIn(card, self.player1.trash)

    def test_assign_don(self) -> None:
        target = make_card("p1-field-1", "Field Character")
        self.player1.cards_in_play.append(target)
        self.player1.don_pool = ["rested", "active"]
        self.game.pending_choice = self.make_choice("assign_don", target_cards=[{"id": target.id}], don_count=1, rested_only=True)

        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertEqual(1, target.attached_don)

    def test_apply_power(self) -> None:
        target = make_card("p1-field-2", "Buff Target")
        self.player1.cards_in_play.append(target)
        self.game.pending_choice = self.make_choice("apply_power", target_cards=[{"id": target.id}], power_amount=2000)

        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertEqual(2000, getattr(target, "power_modifier", 0))

    def test_ko_target(self) -> None:
        target = make_card("opp-2", "KO Target")
        self.player2.cards_in_play.append(target)
        self.game.pending_choice = self.make_choice("ko_target", target_cards=[{"id": target.id}])

        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertNotIn(target, self.player2.cards_in_play)
        self.assertIn(target, self.player2.trash)

    def test_rest_target(self) -> None:
        target = make_card("opp-3", "Rest Target")
        self.player2.cards_in_play.append(target)
        self.game.pending_choice = self.make_choice("rest_target", target_cards=[{"id": target.id}])

        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertTrue(target.is_resting)

    def test_play_from_hand(self) -> None:
        card = make_card("hand-play", "Play Me")
        self.player1.hand.append(card)
        self.game.pending_choice = self.make_choice("play_from_hand", target_cards=[{"id": card.id}], rest_on_play=False)

        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIn(card, self.player1.cards_in_play)
        self.assertNotIn(card, self.player1.hand)

    def test_play_from_trash(self) -> None:
        card = make_card("trash-play", "Trash Me")
        self.player1.trash.append(card)
        self.game.pending_choice = self.make_choice("play_from_trash", target_cards=[{"id": card.id}], rest_on_play=True)

        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIn(card, self.player1.cards_in_play)
        self.assertNotIn(card, self.player1.trash)
        self.assertTrue(card.is_resting)

    def test_return_to_hand(self) -> None:
        target = make_card("opp-4", "Bounce Target")
        self.player2.cards_in_play.append(target)
        self.game.pending_choice = self.make_choice("return_to_hand", target_cards=[{"id": target.id}])

        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIn(target, self.player2.hand)
        self.assertNotIn(target, self.player2.cards_in_play)

    def test_apply_cost_reduction(self) -> None:
        target = make_card("opp-5", "Cost Target", cost=5)
        self.player2.cards_in_play.append(target)
        self.game.pending_choice = self.make_choice("apply_cost_reduction", target_cards=[{"id": target.id}], cost_reduction=-2)

        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertEqual(-2, getattr(target, "cost_modifier", 0))

    def test_set_active(self) -> None:
        target = make_card("p1-field-3", "Set Active")
        target.is_resting = True
        target.has_attacked = True
        self.player1.cards_in_play.append(target)
        self.game.pending_choice = self.make_choice("set_active", target_cards=[{"id": target.id}])

        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertFalse(target.is_resting)
        self.assertFalse(target.has_attacked)


class HardcodedFilterTests(unittest.TestCase):
    def test_filter_by_max_cost(self) -> None:
        cards = [
            make_card("c1", "One", cost=1),
            make_card("c2", "Two", cost=2),
            make_card("c3", "Five", cost=5),
        ]

        filtered = filter_by_max_cost(cards, 2)
        self.assertEqual(["c1", "c2"], [card.id for card in filtered])

    def test_filter_by_cost_range(self) -> None:
        cards = [
            make_card("c1", "One", cost=1),
            make_card("c2", "Three", cost=3),
            make_card("c3", "Five", cost=5),
        ]

        filtered = filter_by_cost_range(cards, min_cost=2, max_cost=4)
        self.assertEqual(["c2"], [card.id for card in filtered])


class OP01LeaderBuffTests(unittest.TestCase):
    def test_op01_003_buff_survives_mid_turn_recalc(self) -> None:
        player1 = make_player("P1", "p1")
        player2 = make_player("P2", "p2")
        player1.leader.id = "OP01-003"
        target = make_card("p1-strawhat", "Straw Hat", cost=5)
        target.card_origin = "Straw Hat Crew"
        target.is_resting = True
        player1.cards_in_play.append(target)

        game = GameState(player1, player2)
        player1.don_pool = ["active", "active", "active", "active"]

        self.assertTrue(op01_003_luffy_leader(game, player1, player1.leader))
        self.assertIsNotNone(game.pending_choice)
        self.assertTrue(game.resolve_pending_choice(["0"]))
        self.assertEqual(1000, getattr(target, "power_modifier", 0))

        game._recalc_continuous_effects()

        self.assertEqual(1000, getattr(target, "power_modifier", 0))
        self.assertEqual(1000, getattr(target, "_sticky_power_modifier", 0))
        self.assertEqual(game.turn_count, getattr(target, "power_modifier_expires_on_turn", -1))


class OP04RegressionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.player1 = make_player("P1", "p1")
        self.player2 = make_player("P2", "p2")
        self.game = GameState(self.player1, self.player2)
        self.player1.hand = []
        self.player2.hand = []
        self.player1.cards_in_play = []
        self.player2.cards_in_play = []
        self.player1.life_cards = []
        self.player2.life_cards = []
        self.player1.deck = []
        self.player2.deck = []
        self.player1.don_pool = []
        self.player2.don_pool = []

    def test_op04_001_vivi_gives_rush_instead_of_trashing_hand(self) -> None:
        self.player1.leader.id = "OP04-001"
        target = make_card("p1-field-rush", "Rush Target", cost=3)
        draw_card = make_card("p1-draw-1", "Draw Card", cost=2)
        opp_hand = make_card("p2-hand-1", "Opponent Hand", cost=2)
        self.player1.cards_in_play.append(target)
        self.player1.deck = [draw_card]
        self.player1.don_pool = ["active", "active"]
        self.player2.hand = [opp_hand]

        self.assertTrue(op04_001_vivi_activate(self.game, self.player1, self.player1.leader))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0", "1"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertTrue(target.has_rush)
        self.assertEqual(self.game.turn_count, getattr(target, "_temporary_rush_until_turn", -1))
        self.assertIn(opp_hand, self.player2.hand)
        self.assertEqual(1, len(self.player1.hand))

    def test_op04_004_karoo_prompts_for_alabasta_targets(self) -> None:
        karoo = make_card("OP04-004", "Karoo", cost=1)
        a1 = make_card("a1", "Alabasta 1", cost=2)
        a1.card_origin = "Alabasta"
        a2 = make_card("a2", "Alabasta 2", cost=2)
        a2.card_origin = "Alabasta"
        self.player1.cards_in_play = [karoo, a1, a2]
        self.player1.don_pool = ["rested", "rested"]

        self.assertTrue(op04_004_karoo(self.game, self.player1, karoo))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertEqual(1, a1.attached_don)
        self.assertEqual(0, a2.attached_don)
        self.assertEqual(["rested"], self.player1.don_pool)

    def test_op04_006_koza_buff_last_until_next_turn(self) -> None:
        koza = make_card("OP04-006", "Koza", cost=3, power=5000)
        self.assertTrue(op04_006_koza(self.game, self.player1, koza))
        self.assertEqual(2000, getattr(koza, "power_modifier", 0))
        self.assertEqual(self.game.turn_count + 1, getattr(koza, "power_modifier_expires_on_turn", -1))

    def test_op04_010_chopper_prompts_for_animal_play(self) -> None:
        chopper = make_card("OP04-010", "Chopper", cost=3)
        animal = make_card("animal", "Animal", cost=2, power=3000)
        animal.card_origin = "Animal"
        self.player1.hand = [animal]

        self.assertTrue(op04_010_chopper(self.game, self.player1, chopper))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertIn(animal, self.player1.cards_in_play)
        self.assertNotIn(animal, self.player1.hand)

    def test_op04_020_issho_sets_own_character_active(self) -> None:
        self.player1.leader.id = "OP04-020"
        rested_valid = make_card("p1-field-1", "Rested Valid", cost=5)
        rested_valid.is_resting = True
        rested_invalid = make_card("p1-field-2", "Rested Invalid", cost=6)
        rested_invalid.is_resting = True
        opponent_char = make_card("p2-field-1", "Opponent", cost=0)
        opponent_char.is_resting = True
        self.player1.cards_in_play.extend([rested_valid, rested_invalid])
        self.player2.cards_in_play.append(opponent_char)
        self.player1.don_pool = ["active"]

        self.assertTrue(op04_020_issho_eot(self.game, self.player1, self.player1.leader))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertEqual(1, len(self.game.pending_choice.options))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertFalse(rested_valid.is_resting)
        self.assertTrue(rested_invalid.is_resting)
        self.assertIn(opponent_char, self.player2.cards_in_play)

    def test_op04_039_rebecca_searches_dressrosa_and_trashes_rest(self) -> None:
        self.player1.leader.id = "OP04-039"
        dressrosa = make_card("p1-deck-1", "Dressrosa Search", cost=2)
        dressrosa.card_origin = "Dressrosa"
        non_match = make_card("p1-deck-2", "Non Match", cost=3)
        non_match.card_origin = "Navy"
        self.player1.deck = [dressrosa, non_match]
        self.player1.hand = [make_card("p1-hand-1", "Hand 1")]
        self.player1.don_pool = ["active"]

        self.assertTrue(op04_039_rebecca_activate(self.game, self.player1, self.player1.leader))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertIn(dressrosa, self.player1.hand)
        self.assertIn(non_match, self.player1.trash)
        self.assertEqual([], self.player1.deck)

    def test_op04_040_queen_can_add_top_card_to_life_instead_of_drawing(self) -> None:
        self.player1.leader.id = "OP04-040"
        self.player1.leader.attached_don = 1
        big_body = make_card("p1-field-big", "Big Body", cost=8)
        top_deck = make_card("p1-deck-life", "Life Card", cost=1)
        self.player1.cards_in_play.append(big_body)
        self.player1.deck = [top_deck]
        self.player1.life_cards = [make_card("p1-life-1", "Life 1"), make_card("p1-life-2", "Life 2")]
        self.player1.hand = [make_card("p1-hand-1", "Only Hand")]

        self.assertTrue(op04_040_queen_leader(self.game, self.player1, self.player1.leader))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["life"]))

        self.assertEqual(0, len(self.player1.deck))
        self.assertEqual(3, len(self.player1.life_cards))
        self.assertIs(self.player1.life_cards[-1], top_deck)
        self.assertEqual(1, len(self.player1.hand))

    def test_op04_011_nami_reveals_and_bottom_decks_card(self) -> None:
        nami = make_card("OP04-011", "Nami", cost=3)
        strong_char = make_card("p1-deck-strong", "Strong Character", card_type="CHARACTER", cost=6, power=7000)
        second = make_card("p1-deck-second", "Second Card", cost=2)
        self.player1.deck = [strong_char, second]

        self.assertTrue(op04_011_nami(self.game, self.player1, nami))

        self.assertEqual(3000, getattr(nami, "power_modifier", 0))
        self.assertEqual(["p1-deck-second", "p1-deck-strong"], [card.id for card in self.player1.deck])

    def test_op04_021_viola_rests_two_own_don_and_one_opponent_don(self) -> None:
        viola = make_card("OP04-021", "Viola", cost=2)
        self.player1.don_pool = ["active", "active", "rested"]
        self.player2.don_pool = ["active", "rested"]

        self.assertTrue(op04_021_viola(self.game, self.player1, viola))

        self.assertEqual(["rested", "rested", "rested"], self.player1.don_pool)
        self.assertEqual(["rested", "rested"], self.player2.don_pool)

    def test_op04_016_bad_manners_discards_then_buffs_for_battle(self) -> None:
        event = make_card("OP04-016", "Bad Manners", card_type="EVENT", cost=0)
        discard = make_card("discard", "Discard", cost=1)
        target = make_card("target", "Target", cost=3)
        self.player1.hand = [discard]
        self.player1.cards_in_play = [target]

        self.assertTrue(op04_016_bad_manners(self.game, self.player1, event))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["1"]))

        self.assertIn(discard, self.player1.trash)
        self.assertEqual(3000, getattr(target, "_battle_power_modifier", 0))

    def test_op04_017_happiness_punch_can_chain_second_debuff(self) -> None:
        event = make_card("OP04-017", "Happiness Punch", card_type="EVENT", cost=0)
        opp_leader = self.player2.leader
        opp_char = make_card("opp-char", "Opp Char", cost=3)
        self.player2.cards_in_play = [opp_char]
        self.player1.leader.is_resting = False

        self.assertTrue(op04_017_happiness_punch(self.game, self.player1, event))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["1"]))

        self.assertEqual(-2000, getattr(opp_leader, "power_modifier", 0))
        self.assertEqual(-1000, getattr(opp_char, "power_modifier", 0))

    def test_op04_018_vertigo_dance_can_hit_two_targets(self) -> None:
        event = make_card("OP04-018", "Vertigo Dance", card_type="EVENT", cost=1)
        self.player1.leader.card_origin = "Alabasta"
        c1 = make_card("c1", "C1", cost=2)
        c2 = make_card("c2", "C2", cost=3)
        self.player2.cards_in_play = [c1, c2]

        self.assertTrue(op04_018_vertigo_dance(self.game, self.player1, event))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0", "1"]))

        self.assertEqual(-2000, getattr(c1, "power_modifier", 0))
        self.assertEqual(-2000, getattr(c2, "power_modifier", 0))

    def test_op04_042_ipponmatsu_prompts_for_slash_target(self) -> None:
        ipponmatsu = make_card("OP04-042", "Ipponmatsu", cost=2)
        slash = make_card("p1-field-slash", "Slash Guy", cost=3)
        slash.attribute = "Slash"
        other = make_card("p1-field-other", "Other Guy", cost=3)
        other.attribute = "Strike"
        deck_card = make_card("p1-deck-trash", "Deck Trash", cost=1)
        self.player1.cards_in_play.extend([slash, other])
        self.player1.deck = [deck_card]

        self.assertTrue(op04_042_ipponmatsu(self.game, self.player1, ipponmatsu))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertEqual(3000, getattr(slash, "power_modifier", 0))
        self.assertEqual(0, getattr(other, "power_modifier", 0))
        self.assertIn(deck_card, self.player1.trash)

    def test_op04_050_hanger_draws_after_discard_choice(self) -> None:
        hanger = make_card("OP04-050", "Hanger", cost=2)
        discard = make_card("p1-hand-discard", "Discard Me", cost=1)
        draw = make_card("p1-deck-draw", "Draw Me", cost=2)
        self.player1.hand = [discard]
        self.player1.deck = [draw]

        self.assertTrue(op04_050_hanger(self.game, self.player1, hanger))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertIn(discard, self.player1.trash)
        self.assertIn(draw, self.player1.hand)

    def test_op04_053_page_one_chooses_bottom_deck_card(self) -> None:
        page_one = make_card("OP04-053", "Page One", cost=4)
        page_one.attached_don = 1
        keep = make_card("p1-hand-keep", "Keep", cost=1)
        bottom = make_card("p1-hand-bottom", "Bottom", cost=2)
        draw = make_card("p1-deck-draw", "Drawn", cost=3)
        self.player1.hand = [keep, bottom]
        self.player1.deck = [draw]

        self.assertTrue(op04_053_page_one(self.game, self.player1, page_one))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["1"]))

        self.assertIn(keep, self.player1.hand)
        self.assertIn(draw, self.player1.hand)
        self.assertEqual("p1-hand-bottom", self.player1.deck[-1].id)

    def test_op04_019_doffy_prompts_to_set_don_active(self) -> None:
        self.player1.don_pool = ["rested", "rested", "active"]
        self.assertTrue(op04_019_doffy_leader(self.game, self.player1, self.player1.leader))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0", "1"]))
        self.assertEqual(["active", "active", "active"], self.player1.don_pool)

    def test_op04_020_issho_continuous_only_on_own_turn(self) -> None:
        self.player1.leader.id = "OP04-020"
        self.player1.leader.attached_don = 1
        target = make_card("opp", "Opponent", cost=4)
        self.player2.cards_in_play = [target]

        self.game.current_player = self.player1
        self.assertTrue(op04_020_issho_continuous(self.game, self.player1, self.player1.leader))
        self.assertEqual(-1, getattr(target, "cost_modifier", 0))

        target.cost_modifier = 0
        self.game.current_player = self.player2
        self.assertFalse(op04_020_issho_continuous(self.game, self.player1, self.player1.leader))
        self.assertEqual(0, getattr(target, "cost_modifier", 0))

    def test_op04_069_bon_kurei_uses_pending_attack_power(self) -> None:
        bon = make_card("OP04-069", "Bon Kurei", cost=4, power=4000)
        attacker = make_card("opp-attacker", "Attacker", cost=5, power=5000)
        attacker.power_modifier = 2000
        self.game.pending_attack = {"attacker": attacker}
        self.player1.don_pool = ["active"]
        self.player1.don_deck = []

        self.assertTrue(op04_069_bon_kurei(self.game, self.player1, bon))

        self.assertEqual(3000, getattr(bon, "power_modifier", 0))
        self.assertEqual(self.game.turn_count, getattr(bon, "power_modifier_expires_on_turn", -1))

    def test_op04_090_luffy_requires_selecting_seven_trash_cards(self) -> None:
        luffy = make_card("OP04-090", "Luffy", cost=8)
        luffy.is_resting = True
        self.player1.trash = [make_card(f"trash-{i}", f"Trash {i}", cost=1) for i in range(7)]

        self.assertTrue(op04_090_luffy_activate(self.game, self.player1, luffy))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice([str(i) for i in range(7)]))

        self.assertFalse(luffy.is_resting)
        self.assertTrue(luffy.skip_next_refresh)
        self.assertEqual(0, len(self.player1.trash))
        self.assertEqual(7, len(self.player1.deck))

    def test_op04_009_duck_troops_returns_to_hand_at_end_of_turn(self) -> None:
        duck = make_card("OP04-009", "Duck Troops", cost=2)
        self.player1.cards_in_play = [duck]
        duck.return_to_hand_eot = True

        self.game._end_phase()

        self.assertIn(duck, self.player1.hand)
        self.assertNotIn(duck, self.player1.cards_in_play)

    def test_op04_110_pound_can_add_target_to_bottom_of_life(self) -> None:
        pound = make_card("OP04-110", "Pound", cost=3)
        target = make_card("opp-target", "Target", cost=3)
        existing_top = make_card("opp-life-top", "Life Top", cost=1)
        self.player2.cards_in_play = [target]
        self.player2.life_cards = [existing_top]

        self.assertTrue(op04_110_pound_ko(self.game, self.player1, pound))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["bottom"]))

        self.assertNotIn(target, self.player2.cards_in_play)
        self.assertEqual(["opp-target", "opp-life-top"], [card.id for card in self.player2.life_cards])

    def test_op04_066_valentine_uses_search_choice_flow(self) -> None:
        valentine = make_card("OP04-066", "Miss Valentine", cost=2)
        match = make_card("p1-deck-bw", "BW Card", cost=1)
        match.card_origin = "Baroque Works"
        miss = make_card("p1-deck-other", "Other Card", cost=3)
        miss.card_origin = "Navy"
        self.player1.deck = [match, miss]

        self.assertTrue(op04_066_valentine(self.game, self.player1, valentine))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertIn(match, self.player1.hand)
        self.assertEqual(["p1-deck-other"], [card.id for card in self.player1.deck])

    def test_op04_084_stussy_can_play_matching_cp_character(self) -> None:
        stussy = make_card("OP04-084", "Stussy", cost=4)
        cp = make_card("p1-deck-cp", "CP Agent", cost=2)
        cp.card_origin = "CP"
        filler1 = make_card("p1-deck-fill-1", "Filler 1", cost=3)
        filler2 = make_card("p1-deck-fill-2", "Filler 2", cost=4)
        self.player1.deck = [cp, filler1, filler2]

        self.assertTrue(op04_084_stussy(self.game, self.player1, stussy))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertIn(cp, self.player1.cards_in_play)
        self.assertIn(filler1, self.player1.trash)
        self.assertIn(filler2, self.player1.trash)
        self.assertEqual([], self.player1.deck)

    def test_op04_119_rosinante_does_not_auto_rest_or_auto_play(self) -> None:
        rosinante = make_card("OP04-119", "Donquixote Rosinante", cost=2)
        green_five = make_card("p1-hand-green5", "Green Five", cost=5)
        green_five.colors = ["Green"]
        self.player1.hand = [green_five]

        self.assertTrue(op04_119_rosinante_play(self.game, self.player1, rosinante))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertFalse(rosinante.is_resting)
        self.assertIn(green_five, self.player1.hand)

        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertTrue(rosinante.is_resting)
        self.assertIn(green_five, self.player1.cards_in_play)
        self.assertNotIn(green_five, self.player1.hand)


if __name__ == "__main__":
    unittest.main()
