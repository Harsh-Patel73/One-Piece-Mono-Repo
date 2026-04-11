import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SIM_BACKEND = ROOT.parent / "simulator" / "backend"
if str(SIM_BACKEND) not in sys.path:
    sys.path.insert(0, str(SIM_BACKEND))

from game.effect_test_session import build_game_state
from optcg_engine.effects.effect_registry import filter_by_cost_range, filter_by_max_cost
from optcg_engine.effects.sets.op01_effects import op01_003_luffy_leader
from optcg_engine.effects.sets.op04_effects import (
    op04_001_vivi_activate,
    op04_005_kungfu_jugon,
    op04_004_karoo,
    op04_006_koza,
    op04_009_duck_troops,
    op04_010_chopper,
    op04_011_nami,
    op04_021_viola,
    op04_024_sugar_play,
    op04_024_sugar_opp_turn,
    op04_025_giolla,
    op04_026_senor_pink,
    op04_029_dellinger,
    op04_030_trebol_defense,
    op04_032_baby5,
    op04_033_machvise,
    op04_035_spiderweb_counter,
    op04_035_spiderweb_trigger,
    op04_037_flapping_thread,
    op04_038_the_weak_main,
    op04_038_the_weak_trigger,
    op04_020_issho_eot,
    op04_039_rebecca_activate,
    op04_040_queen_leader,
    op04_041_apis,
    op04_042_ipponmatsu,
    op04_050_hanger,
    op04_053_page_one,
    op04_055_plague_rounds,
    op04_056_red_roc,
    op04_057_dragon_twister_counter,
    op04_057_dragon_twister_trigger,
    op04_066_valentine,
    op04_069_bon_kurei,
    op04_071_mr4,
    op04_073_mr13_friday,
    op04_074_colors_trap,
    op04_074_colors_trap_trigger,
    op04_075_nez_palm_cannon,
    op04_075_nez_palm_cannon_trigger,
    op04_076_weakness_unforgivable,
    op04_076_weakness_unforgivable_trigger,
    op04_086_chinjao,
    op04_093_king_kong_gun,
    op04_093_king_kong_gun_trigger,
    op04_094_trueno_bastardo,
    op04_094_trueno_bastardo_trigger,
    op04_095_barrier_counter,
    op04_095_barrier_trigger,
    op04_096_corrida_coliseum,
    op04_083_sabo_play,
    op04_084_stussy,
    op04_090_luffy_activate,
    op04_112_yamato,
    op04_115_gun_modoki,
    op04_117_heavenly_fire,
    op04_117_heavenly_fire_trigger,
    op04_098_toko,
    op04_100_bege,
    op04_111_hera,
    op04_110_pound_ko,
    op04_016_bad_manners,
    op04_017_happiness_punch,
    op04_018_vertigo_dance,
    op04_019_doffy_leader,
    op04_020_issho_continuous,
    op04_119_rosinante_play,
)
from optcg_engine.game_engine import GamePhase, GameState, PendingChoice, Player
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


def make_effect_test_card_data(
    card_id: str,
    name: str,
    *,
    card_type: str = "CHARACTER",
    cost: int = 1,
    power: int = 1000,
    color: str = "Red",
    card_origin: str = "Test",
    effect: str = "",
    trigger: str = "",
) -> dict:
    return {
        "id": card_id,
        "id_normal": card_id,
        "name": name,
        "cardType": card_type,
        "Cost": cost,
        "Power": power,
        "Counter": 0,
        "Color": color,
        "Life": "",
        "Effect": effect,
        "Type": card_origin,
        "Trigger": trigger,
    }


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
        self.assertEqual(["rested", "rested"], self.player1.don_pool)
        player_state = self.game._player_to_dict(self.player1, is_viewer=True)
        self.assertEqual(1, player_state["don_total"])
        self.assertEqual(["rested"], player_state["don_pool"])

    def test_op04_006_koza_buff_last_until_next_turn(self) -> None:
        koza = make_card("OP04-006", "Koza", cost=3, power=5000)
        self.assertTrue(op04_006_koza(self.game, self.player1, koza))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["yes"]))
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
        self.assertIsNotNone(self.game.pending_choice)
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

    def test_op04_040_queen_auto_draws_when_life_mode_is_unavailable(self) -> None:
        self.player1.leader.id = "OP04-040"
        self.player1.leader.attached_don = 1
        draw_card = make_card("draw-card", "Draw Card", cost=1)
        self.player1.hand = [make_card("p1-hand", "Hand Card")]
        self.player1.life_cards = [make_card("p1-life-1", "Life 1"), make_card("p1-life-2", "Life 2")]
        self.player1.deck = [draw_card]

        self.assertTrue(op04_040_queen_leader(self.game, self.player1, self.player1.leader))
        self.assertIsNone(self.game.pending_choice)
        self.assertEqual(draw_card, self.player1.hand[-1])
        self.assertEqual(0, len(self.player1.deck))

    def test_op04_011_nami_reveals_and_bottom_decks_card(self) -> None:
        nami = make_card("OP04-011", "Nami", cost=3)
        strong_char = make_card("p1-deck-strong", "Strong Character", card_type="CHARACTER", cost=6, power=7000)
        second = make_card("p1-deck-second", "Second Card", cost=2)
        self.player1.deck = [strong_char, second]

        self.assertTrue(op04_011_nami(self.game, self.player1, nami))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertEqual("p1-deck-strong", self.game.pending_choice.options[0]["card_id"])
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertEqual(3000, getattr(nami, "power_modifier", 0))
        self.assertEqual(["p1-deck-second", "p1-deck-strong"], [card.id for card in self.player1.deck])

    def test_op04_021_viola_rests_two_own_don_and_one_opponent_don(self) -> None:
        viola = make_card("OP04-021", "Viola", cost=2)
        self.player1.don_pool = ["active", "active", "rested"]
        self.player2.don_pool = ["active", "rested"]

        self.assertTrue(op04_021_viola(self.game, self.player1, viola))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["yes"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0", "1"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertEqual(["rested", "rested", "rested"], self.player1.don_pool)
        self.assertEqual(["rested", "rested"], self.player2.don_pool)

    def test_declare_attack_triggers_defender_on_opponent_attack_choice(self) -> None:
        attacker = make_card("attacker", "Attacker", cost=4, power=6000)
        attacker.played_turn = 0
        viola = make_card("OP04-021", "Viola", cost=2)
        self.player1.cards_in_play = [attacker]
        self.player1.don_pool = ["active"]
        self.player2.cards_in_play = [viola]
        self.player2.don_pool = ["active", "active"]

        self.assertTrue(self.game.declare_attack(0, -1))
        self.assertIsNotNone(self.game.pending_attack)
        self.assertIsNotNone(self.game.pending_choice)
        self.assertEqual("OP04-021", self.game.pending_choice.source_card_id)

        self.assertTrue(self.game.resolve_pending_choice(["yes"]))
        self.assertTrue(self.game.resolve_pending_choice(["0", "1"]))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertEqual("blocker", self.game.awaiting_response)
        self.assertEqual(["rested"], self.player1.don_pool)
        self.assertEqual(["rested", "rested"], self.player2.don_pool)

    def test_on_opponent_attack_effects_queue_in_order_and_refresh_blockers(self) -> None:
        attacker = make_card("attacker", "Attacker", cost=4, power=6000)
        attacker.played_turn = 0
        viola = make_card("OP04-021", "Viola", cost=2)
        mr4 = make_card("OP04-071", "Mr.4", cost=3, power=5000)
        self.player1.cards_in_play = [attacker]
        self.player1.don_pool = ["active"]
        self.player2.cards_in_play = [viola, mr4]
        self.player2.don_pool = ["active", "active", "active"]

        self.assertTrue(self.game.declare_attack(0, -1))
        self.assertEqual("OP04-021", self.game.pending_choice.source_card_id)

        self.assertTrue(self.game.resolve_pending_choice(["yes"]))
        self.assertTrue(self.game.resolve_pending_choice(["0", "1"]))
        self.assertTrue(self.game.resolve_pending_choice([]))

        self.assertIsNotNone(self.game.pending_choice)
        self.assertEqual("OP04-071", self.game.pending_choice.source_card_id)
        self.assertTrue(self.game.resolve_pending_choice(["yes"]))
        self.assertTrue(self.game.resolve_pending_choice(["2"]))

        self.assertEqual("blocker", self.game.awaiting_response)
        self.assertTrue(mr4.has_blocker)
        self.assertEqual(1000, getattr(mr4, "power_modifier", 0))
        self.assertEqual(
            ["Mr.4"],
            [entry["name"] for entry in self.game.pending_attack["available_blockers"]],
        )

    def test_on_event_effects_fire_for_field_characters(self) -> None:
        page_one = make_card("OP04-053", "Page One", cost=4, power=6000)
        page_one.attached_don = 1
        bottom_card = make_card("bottom-card", "Bottom Card", cost=2)
        draw_card = make_card("draw-card", "Draw Card", cost=3)
        event = make_card("event", "Test Event", card_type="EVENT", cost=0)
        self.player1.cards_in_play = [page_one]
        self.player1.hand = [event, bottom_card]
        self.player1.deck = [draw_card]

        self.assertTrue(self.game.play_card(0))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertEqual([draw_card], self.player1.hand)
        self.assertEqual([bottom_card], self.player1.deck)

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
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["yes"]))

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

    def test_op04_005_second_jugon_updates_both_blockers_when_played(self) -> None:
        first = make_card("OP04-005", "Kung Fu Jugon", cost=3)
        second = make_card("OP04-005", "Kung Fu Jugon", cost=3)
        self.player1.cards_in_play = [first]
        self.player1.hand = [second]
        op04_005_kungfu_jugon(self.game, self.player1, first)

        self.game.pending_choice = PendingChoice(
            choice_id="play-jugon",
            choice_type="select_target",
            prompt="Play Jugon",
            callback_action="play_from_hand",
            callback_data={"player_index": 0, "target_cards": [{"id": second.id}], "rest_on_play": False},
        )
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertTrue(first.has_blocker)
        self.assertTrue(second.has_blocker)

    def test_op04_009_duck_troops_prompts_for_leader_cost_and_returns_active(self) -> None:
        duck = make_card("OP04-009", "Duck Troops", cost=2)
        self.player1.cards_in_play = [duck]

        self.assertTrue(op04_009_duck_troops(self.game, self.player1, duck))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["yes"]))
        self.assertTrue(getattr(duck, "return_to_hand_eot", False))

        duck.is_resting = True
        self.game._end_phase()

        self.assertIn(duck, self.player1.hand)
        self.assertFalse(duck.is_resting)

    def test_op04_024_sugar_only_offers_active_targets_and_only_rests_self_if_used(self) -> None:
        sugar = make_card("OP04-024", "Sugar", cost=2)
        self.player1.leader.card_origin = "Donquixote Pirates"
        active_target = make_card("opp-active", "Opp Active", cost=4)
        rested_target = make_card("opp-rested", "Opp Rested", cost=4)
        rested_target.is_resting = True
        self.player2.cards_in_play = [active_target, rested_target]

        self.assertTrue(op04_024_sugar_play(self.game, self.player1, sugar))
        self.assertEqual(1, len(self.game.pending_choice.options))
        self.assertEqual("opp-active", self.game.pending_choice.options[0]["card_id"])
        self.assertTrue(self.game.resolve_pending_choice([]))

        self.assertTrue(op04_024_sugar_opp_turn(self.game, self.player1, sugar))
        self.assertEqual(1, len(self.game.pending_choice.options))
        self.assertTrue(self.game.resolve_pending_choice([]))
        self.assertTrue(sugar.is_resting)

        sugar.op04_024_used = False
        sugar.is_resting = False
        self.assertTrue(op04_024_sugar_opp_turn(self.game, self.player1, sugar))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertTrue(sugar.is_resting)
        self.assertTrue(active_target.is_resting)

    def test_playing_character_triggers_sugar_opponent_play_prompt(self) -> None:
        sugar = make_card("OP04-024", "Sugar", cost=2)
        self.player1.leader.card_origin = "Donquixote Pirates"
        self.player1.cards_in_play = [sugar]
        played_char = make_card("opp-played", "Opp Played", cost=1)
        self.player2.hand = [played_char]
        self.player2.don_pool = ["active"]
        self.game.current_player = self.player2
        self.game.opponent_player = self.player1

        self.assertTrue(self.game.play_card(0))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertEqual("OP04-024", self.game.pending_choice.source_card_id)
        self.assertTrue(self.game.resolve_pending_choice([]))

        self.assertIn(played_char, self.player2.cards_in_play)
        self.assertTrue(sugar.is_resting)
        self.assertFalse(played_char.is_resting)

    def test_op04_025_giolla_prompts_for_don_then_target(self) -> None:
        giolla = make_card("OP04-025", "Giolla", cost=3)
        target = make_card("opp-active", "Opp Active", cost=4)
        self.player1.don_pool = ["active", "active", "rested"]
        self.player2.cards_in_play = [target]

        self.assertTrue(op04_025_giolla(self.game, self.player1, giolla))
        self.assertTrue(self.game.resolve_pending_choice(["yes"]))
        self.assertTrue(self.game.resolve_pending_choice(["0", "1"]))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertEqual(["rested", "rested", "rested"], self.player1.don_pool)
        self.assertTrue(target.is_resting)

    def test_op04_026_senor_pink_filters_rested_targets_and_prompts_eot_don(self) -> None:
        pink = make_card("OP04-026", "Senor Pink", cost=4)
        active_target = make_card("opp-active", "Opp Active", cost=4)
        rested_target = make_card("opp-rested", "Opp Rested", cost=4)
        rested_target.is_resting = True
        self.player1.leader.card_origin = "Donquixote Pirates"
        self.player1.don_pool = ["active", "rested"]
        self.player2.cards_in_play = [active_target, rested_target]

        self.assertTrue(op04_026_senor_pink(self.game, self.player1, pink))
        self.assertTrue(self.game.resolve_pending_choice(["yes"]))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertEqual(1, len(self.game.pending_choice.options))
        self.assertEqual("opp-active", self.game.pending_choice.options[0]["card_id"])
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.game._end_phase()
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["1"]))
        self.assertEqual(["rested", "active"], self.player1.don_pool)

    def test_op04_030_trebol_defense_prompts_for_don_then_target(self) -> None:
        trebol = make_card("OP04-030", "Trebol", cost=4)
        target = make_card("opp-active", "Opp Active", cost=4)
        self.player1.don_pool = ["active", "active"]
        self.player2.cards_in_play = [target]

        self.assertTrue(op04_030_trebol_defense(self.game, self.player1, trebol))
        self.assertTrue(self.game.resolve_pending_choice(["yes"]))
        self.assertTrue(self.game.resolve_pending_choice(["0", "1"]))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertEqual(["rested", "rested"], self.player1.don_pool)
        self.assertTrue(target.is_resting)

    def test_op04_032_baby5_prompts_for_specific_don_after_trashing(self) -> None:
        baby5 = make_card("OP04-032", "Baby 5", cost=3)
        self.player1.cards_in_play = [baby5]
        self.player1.don_pool = ["rested", "active", "rested"]
        self.game.phase = GamePhase.END

        self.assertTrue(op04_032_baby5(self.game, self.player1, baby5))
        self.assertTrue(self.game.resolve_pending_choice(["yes"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertIn(baby5, self.player1.trash)
        self.assertEqual(["active", "active", "rested"], self.player1.don_pool)

    def test_op04_033_machvise_filters_rested_targets(self) -> None:
        machvise = make_card("OP04-033", "Machvise", cost=4)
        active_target = make_card("opp-active", "Opp Active", cost=5)
        rested_target = make_card("opp-rested", "Opp Rested", cost=5)
        rested_target.is_resting = True
        self.player1.leader.card_origin = "Donquixote Pirates"
        self.player2.cards_in_play = [active_target, rested_target]

        self.assertTrue(op04_033_machvise(self.game, self.player1, machvise))
        self.assertEqual(1, len(self.game.pending_choice.options))
        self.assertEqual("opp-active", self.game.pending_choice.options[0]["card_id"])

    def test_op04_032_end_of_turn_prompt_excludes_attached_don_from_cost_area(self) -> None:
        baby5 = make_card("OP04-032", "Baby 5", cost=3)
        carrier = make_card("carrier", "Carrier", cost=3)
        self.player1.cards_in_play = [baby5, carrier]
        self.player1.don_pool = ["active", "rested", "rested"]
        self.player1.assign_don_to_card(carrier, 1)
        self.game.phase = GamePhase.END

        player_state = self.game._player_to_dict(self.player1, is_viewer=True)
        self.assertEqual(2, player_state["don_total"])
        self.assertEqual(["rested", "rested"], player_state["don_pool"])

        self.assertTrue(op04_032_baby5(self.game, self.player1, baby5))
        self.assertTrue(self.game.resolve_pending_choice(["yes"]))
        self.assertEqual(["0", "1"], [opt["id"] for opt in self.game.pending_choice.options])
        self.assertTrue(self.game.resolve_pending_choice(["0", "1"]))

        self.assertEqual(["active", "active", "rested"], self.player1.don_pool)
        self.assertEqual(1, carrier.attached_don)

    def test_op04_035_spiderweb_counter_and_trigger_prompt_for_set_active(self) -> None:
        event = make_card("OP04-035", "Spiderweb", card_type="EVENT", cost=1)
        rested_char = make_card("rested-char", "Rested Char", cost=3)
        self.player1.leader.is_resting = True
        rested_char.is_resting = True
        self.player1.cards_in_play = [rested_char]

        self.assertTrue(op04_035_spiderweb_trigger(self.game, self.player1, event))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertEqual(2000, getattr(self.player1.leader, "power_modifier", 0))

        rested_char.is_resting = True
        self.assertTrue(op04_035_spiderweb_counter(self.game, self.player1, event))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertEqual(4000, getattr(self.player1.leader, "_battle_power_modifier", 0))
        self.assertFalse(rested_char.is_resting)

    def test_op04_038_trigger_sets_only_selected_rested_don_active(self) -> None:
        event = make_card("OP04-038", "The Weak Do Not Have the Right to Choose How They Die!!!", card_type="EVENT", cost=5)
        self.player1.don_pool = ["rested", "rested", "active"]

        self.assertTrue(op04_038_the_weak_trigger(self.game, self.player1, event))
        self.assertTrue(self.game.resolve_pending_choice(["1"]))

        self.assertEqual(["rested", "active", "active"], self.player1.don_pool)

    def test_op04_055_plague_rounds_trashes_ice_oni_then_bottom_decks_and_plays_from_trash(self) -> None:
        event = make_card("OP04-055", "Plague Rounds", card_type="EVENT", cost=2)
        ice_oni = make_card("OP04-047", "Ice Oni", cost=2)
        filler = make_card("filler", "Filler", cost=3)
        target = make_card("target", "Target", cost=4)
        self.player1.hand = [ice_oni, filler]
        self.player2.cards_in_play = [target]

        self.assertTrue(op04_055_plague_rounds(self.game, self.player1, event))
        self.assertTrue(self.game.resolve_pending_choice(["yes"]))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertNotIn(target, self.player2.cards_in_play)
        self.assertIn(target, self.player2.deck)
        self.assertIn(ice_oni, self.player1.cards_in_play)
        self.assertNotIn(ice_oni, self.player1.trash)

    def test_op04_056_and_057_event_followups_prompt_for_targets(self) -> None:
        red_roc = make_card("OP04-056", "Gum-Gum Red Roc", card_type="EVENT", cost=6)
        demolition = make_card("OP04-057", "Dragon Twister Demolition Breath", card_type="EVENT", cost=2)
        low_char = make_card("low-char", "Low Char", cost=1)
        big_char = make_card("big-char", "Big Char", cost=6)
        self.player1.cards_in_play = [low_char]
        self.player2.cards_in_play = [big_char]

        self.assertTrue(op04_056_red_roc(self.game, self.player1, red_roc))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIn(low_char, self.player1.deck)

        self.player1.cards_in_play = [make_card("ally", "Ally", cost=3)]
        self.player2.cards_in_play = [big_char]
        self.assertTrue(op04_057_dragon_twister_counter(self.game, self.player1, demolition))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertEqual(4000, getattr(self.player1.leader, "_battle_power_modifier", 0))
        self.assertIsNone(self.game.pending_choice)

        self.player1.cards_in_play = [make_card("small", "Small", cost=2)]
        self.player2.cards_in_play = [big_char]
        self.assertTrue(op04_057_dragon_twister_trigger(self.game, self.player1, demolition))
        self.assertTrue(self.game.resolve_pending_choice(["1"]))
        self.assertIn(big_char, self.player2.hand)

    def test_op04_074_075_and_076_counters_use_prompted_followups(self) -> None:
        colors_trap = make_card("OP04-074", "Colors Trap", card_type="EVENT", cost=1)
        nez_palm = make_card("OP04-075", "Nez-Palm Cannon", card_type="EVENT", cost=2)
        weakness = make_card("OP04-076", "Weakness...Is an Unforgivable Sin.", card_type="EVENT", cost=1)
        rest_target = make_card("rest-target", "Rest Target", cost=4)
        self.player1.don_pool = ["active"]
        self.player2.cards_in_play = [rest_target]

        self.assertTrue(op04_074_colors_trap(self.game, self.player1, colors_trap))
        self.assertTrue(self.game.resolve_pending_choice(["yes"]))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertTrue(rest_target.is_resting)

        self.player1.life_cards = [make_card("life-1", "Life 1", cost=1), make_card("life-2", "Life 2", cost=1)]
        self.assertTrue(op04_075_nez_palm_cannon(self.game, self.player1, nez_palm))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIn("rested", self.player1.don_pool)

        self.player1.don_pool = ["active"]
        self.assertTrue(op04_076_weakness_unforgivable(self.game, self.player1, weakness))
        self.assertTrue(self.game.resolve_pending_choice(["yes"]))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertEqual(self.game.turn_count, getattr(self.player1.leader, "power_modifier_expires_on_turn", -1))

        self.assertTrue(op04_074_colors_trap_trigger(self.game, self.player1, colors_trap))
        self.assertIn("active", self.player1.don_pool)

    def test_op04_037_flapping_thread_targets_selected_card_for_turn(self) -> None:
        event = make_card("OP04-037", "Flapping Thread", card_type="EVENT", cost=1)
        target = make_card("target", "Target", cost=4)
        other = make_card("other", "Other", cost=4)
        self.player1.leader.card_origin = "Donquixote Pirates"
        self.player1.cards_in_play = [target, other]

        self.assertTrue(op04_037_flapping_thread(self.game, self.player1, event))
        self.assertTrue(self.game.resolve_pending_choice(["1"]))

        self.assertEqual(2000, getattr(target, "power_modifier", 0))
        self.assertEqual(self.game.turn_count, getattr(target, "power_modifier_expires_on_turn", -1))
        self.assertEqual(0, getattr(other, "power_modifier", 0))

    def test_op04_038_the_weak_chains_rest_then_ko(self) -> None:
        event = make_card("OP04-038", "The Weak Do Not Have the Right to Choose How They Die!!!", card_type="EVENT", cost=3)
        leader = self.player2.leader
        target = make_card("opp-char", "Opp Char", cost=6)
        self.player2.cards_in_play = [target]

        self.assertTrue(op04_038_the_weak_main(self.game, self.player1, event))
        self.assertEqual(2, len(self.game.pending_choice.options))
        self.assertTrue(self.game.resolve_pending_choice(["1"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertTrue(target.is_resting)
        self.assertNotIn(target, self.player2.cards_in_play)
        self.assertIn(target, self.player2.trash)

    def test_op04_041_apis_prompts_for_exact_two_discards_even_with_two_cards(self) -> None:
        apis = make_card("OP04-041", "Apis", cost=2)
        first = make_card("first", "First", cost=1)
        second = make_card("second", "Second", cost=2)
        match = make_card("match", "East Blue Match", cost=1)
        match.card_origin = "East Blue"
        self.player1.hand = [first, second]
        self.player1.deck = [match]

        self.assertTrue(op04_041_apis(self.game, self.player1, apis))
        self.assertTrue(self.game.resolve_pending_choice(["yes"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertEqual(2, self.game.pending_choice.min_selections)
        self.assertTrue(self.game.resolve_pending_choice(["0", "1"]))

        self.assertIn(first, self.player1.trash)
        self.assertIn(second, self.player1.trash)

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

    def test_op04_063_franky_only_gives_plus_1000_during_live_attack_flow(self) -> None:
        franky = make_card("OP04-063", "Franky", cost=4, power=5000)
        franky.card_origin = "Water Seven"
        self.player1.leader.card_origin = "Water Seven"
        attacker = make_card("opp-attacker", "Opp Attacker", cost=4, power=5000)
        self.player1.cards_in_play = [franky]
        self.player1.don_pool = ["active"]
        self.player2.cards_in_play = [attacker]
        self.game.current_player = self.player2
        self.game.opponent_player = self.player1

        self.assertTrue(self.game.declare_attack(0, -1))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["yes"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertEqual(1000, getattr(self.player1.leader, "power_modifier", 0))
        self.assertEqual([], self.player1.don_pool)

    def test_op04_071_mr4_only_gives_plus_1000_during_live_attack_flow(self) -> None:
        mr4 = make_card("OP04-071", "Mr. 4", cost=4, power=5000)
        attacker = make_card("opp-attacker", "Opp Attacker", cost=4, power=5000)
        self.player1.cards_in_play = [mr4]
        self.player1.don_pool = ["active"]
        self.player2.cards_in_play = [attacker]
        self.game.current_player = self.player2
        self.game.opponent_player = self.player1

        self.assertTrue(self.game.declare_attack(0, -1))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["yes"]))

        self.assertTrue(mr4.has_blocker)
        self.assertEqual(1000, getattr(mr4, "power_modifier", 0))
        self.assertEqual([], self.player1.don_pool)

    def test_op04_090_activate_resets_attack_state(self) -> None:
        luffy = make_card("OP04-090", "Monkey.D.Luffy", cost=7, power=7000)
        luffy.is_resting = True
        luffy.has_attacked = True
        self.player1.trash = [make_card(f"trash-{idx}", f"Trash {idx}", cost=1) for idx in range(7)]

        self.assertTrue(op04_090_luffy_activate(self.game, self.player1, luffy))
        self.assertTrue(self.game.resolve_pending_choice([str(i) for i in range(7)]))

        self.assertFalse(luffy.is_resting)
        self.assertFalse(luffy.has_attacked)

    def test_op04_111_hera_trashes_other_homies_and_then_sets_linlin_active(self) -> None:
        hera = make_card("OP04-111", "Hera", cost=5, power=3000)
        hera.card_origin = "Big Mom Pirates/Homies"
        homie = make_card("homie", "Other Homie", cost=3, power=3000)
        homie.card_origin = "Homies"
        linlin = make_card("linlin", "Charlotte Linlin", cost=10, power=12000)
        linlin.is_resting = True
        linlin.has_attacked = True
        self.player1.cards_in_play = [hera, homie, linlin]

        self.assertTrue(op04_111_hera(self.game, self.player1, hera))
        self.assertFalse(hera.is_resting)
        self.assertEqual(["homie"], [opt["card_id"] for opt in self.game.pending_choice.options])
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertTrue(hera.is_resting)
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertIn(homie, self.player1.trash)
        self.assertFalse(linlin.is_resting)
        self.assertFalse(linlin.has_attacked)

    def test_op04_111_activate_main_uses_activate_flow_without_trigger_side_effects(self) -> None:
        hera = make_card("OP04-111", "Hera", cost=5, power=3000)
        hera.card_origin = "Big Mom Pirates/Homies"
        other_homie = make_card("homie", "Other Homie", cost=3, power=3000)
        other_homie.card_origin = "Homies"
        linlin = make_card("linlin", "Charlotte Linlin", cost=10, power=12000)
        linlin.is_resting = True
        self.player1.cards_in_play = [hera, other_homie, linlin]

        self.assertTrue(self.game.activate_main_effect(0))
        self.assertEqual(["homie"], [opt["card_id"] for opt in self.game.pending_choice.options])
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertIn(other_homie, self.player1.trash)
        self.assertIn(hera, self.player1.cards_in_play)
        self.assertTrue(hera.is_resting)
        self.assertFalse(linlin.is_resting)

    def test_activate_main_does_not_fall_back_to_parser_for_unusable_hardcoded_activate(self) -> None:
        hera = make_card("OP04-111", "Hera", cost=5, power=3000)
        hera.card_origin = "Big Mom Pirates/Homies"
        hera.effect = "[Activate: Main] You may trash 1 {Homies} type Character: Set up to 1 [Charlotte Linlin] Character as active."
        self.player1.cards_in_play = [hera]

        with patch("optcg_engine.effects.manager.get_effect_manager") as get_effect_manager:
            self.assertFalse(self.game.activate_main_effect(0))

        get_effect_manager.assert_not_called()

    def test_op04_073_activate_main_prompts_and_adds_one_active_don(self) -> None:
        mr13 = make_card("OP04-073", "Mr.13 & Ms.Friday", cost=1, power=2000)
        partner = make_card("OP04-067", "Baroque Partner", cost=2, power=3000)
        partner.card_origin = "Baroque Works"
        mr13.card_origin = "Baroque Works"
        self.player1.cards_in_play = [mr13, partner]
        self.player1.don_pool = ["active"]

        self.assertTrue(self.game.activate_main_effect(0))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertEqual("OP04-073", self.game.pending_choice.source_card_id)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertIn(mr13, self.player1.trash)
        self.assertIn(partner, self.player1.trash)
        self.assertEqual(["active", "active"], self.player1.don_pool)

    def test_op04_119_rosinante_does_not_auto_rest_or_auto_play(self) -> None:
        rosinante = make_card("OP04-119", "Donquixote Rosinante", cost=2)
        green_five = make_card("p1-hand-green5", "Green Five", cost=5)
        green_five.colors = ["Green"]
        self.player1.hand = [green_five]

        self.assertTrue(op04_119_rosinante_play(self.game, self.player1, rosinante))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertFalse(rosinante.is_resting)
        self.assertIn(green_five, self.player1.hand)

        self.assertEqual(["yes", "no"], [option["id"] for option in self.game.pending_choice.options])
        self.assertTrue(self.game.resolve_pending_choice(["yes"]))
        self.assertTrue(rosinante.is_resting)
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertTrue(rosinante.is_resting)
        self.assertIn(green_five, self.player1.cards_in_play)
        self.assertNotIn(green_five, self.player1.hand)

    def test_op04_119_rosinante_can_decline_the_optional_rest_and_play_effect(self) -> None:
        rosinante = make_card("OP04-119", "Donquixote Rosinante", cost=2)
        green_five = make_card("p1-hand-green5", "Green Five", cost=5)
        green_five.colors = ["Green"]
        self.player1.hand = [green_five]

        self.assertTrue(op04_119_rosinante_play(self.game, self.player1, rosinante))
        self.assertTrue(self.game.resolve_pending_choice(["no"]))

        self.assertFalse(rosinante.is_resting)
        self.assertIsNone(self.game.pending_choice)
        self.assertIn(green_five, self.player1.hand)
        self.assertNotIn(green_five, self.player1.cards_in_play)

    def test_op04_119_rosinante_rests_before_prompting_for_the_green_five(self) -> None:
        rosinante = make_card("OP04-119", "Donquixote Rosinante", cost=2)
        self.player1.cards_in_play = [rosinante]
        green_five = make_card("p1-hand-green5", "Green Five", cost=5)
        green_five.colors = ["Green"]
        self.player1.hand = [green_five]

        self.assertTrue(op04_119_rosinante_play(self.game, self.player1, rosinante))
        self.assertTrue(self.game.resolve_pending_choice(["yes"]))

        self.assertTrue(rosinante.is_resting)
        self.assertEqual(["p1-hand-green5"], [opt["card_id"] for opt in self.game.pending_choice.options])

    def test_op04_018_noop_without_alabasta_leader_still_counts_as_handled(self) -> None:
        event = make_card("OP04-018", "Vertigo Dance", card_type="EVENT", cost=1)
        self.player1.leader.card_origin = "Dressrosa"

        self.assertTrue(op04_018_vertigo_dance(self.game, self.player1, event))
        self.assertIsNone(self.game.pending_choice)

    def test_op04_098_toko_prompts_for_optional_wano_cost(self) -> None:
        toko = make_card("OP04-098", "Toko", cost=2)
        wano_one = make_card("wano-1", "Wano 1", cost=1)
        wano_one.card_origin = "Land of Wano"
        wano_two = make_card("wano-2", "Wano 2", cost=2)
        wano_two.card_origin = "Land of Wano"
        top_life = make_card("deck-life", "Deck Life", cost=1)
        self.player1.hand = [wano_one, wano_two]
        self.player1.life_cards = [make_card("life", "Life", cost=1)]
        self.player1.deck = [top_life]

        self.assertTrue(op04_098_toko(self.game, self.player1, toko))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertEqual("select_mode", self.game.pending_choice.choice_type)
        self.assertTrue(self.game.resolve_pending_choice(["no"]))

        self.assertIn(wano_one, self.player1.hand)
        self.assertIn(wano_two, self.player1.hand)
        self.assertEqual([top_life], self.player1.deck)
        self.assertEqual(1, len(self.player1.life_cards))

    def test_op04_100_bege_only_lasts_for_current_turn(self) -> None:
        bege = make_card("OP04-100", 'Capone "Gang" Bege', card_type="EVENT", cost=0)
        leader = self.player2.leader

        self.assertTrue(op04_100_bege(self.game, self.player1, bege))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertTrue(leader.cannot_attack)
        self.assertEqual(self.game.turn_count, getattr(leader, "cannot_attack_until_turn", -1))

        self.game._clear_temporary_effects(self.player2)

        self.assertFalse(leader.cannot_attack)

class OP04EngineRegressionTests(unittest.TestCase):
    def test_op04_086_chinjao_draws_then_prompts_to_trash_two(self) -> None:
        chinjao = make_card("OP04-086", "Chinjao", cost=5)
        chinjao.attached_don = 1
        keep = make_card("keep", "Keep", cost=1)
        draw_one = make_card("draw-one", "Draw One", cost=2)
        draw_two = make_card("draw-two", "Draw Two", cost=3)
        self.player1.hand = [keep]
        self.player1.deck = [draw_one, draw_two]

        self.assertTrue(op04_086_chinjao(self.game, self.player1, chinjao))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0", "1"]))
        self.assertEqual([draw_two], self.player1.hand)

    def test_op04_093_094_and_095_use_trash_threshold_correctly(self) -> None:
        king_kong = make_card("OP04-093", "Gum-Gum King Kong Gun", card_type="EVENT", cost=3)
        trueno = make_card("OP04-094", "Trueno Bastardo", card_type="EVENT", cost=4)
        barrier = make_card("OP04-095", "Barrier!!", card_type="EVENT", cost=1)
        dressrosa = make_card("dressrosa", "Dressrosa", cost=5, power=6000)
        dressrosa.card_origin = "Dressrosa"
        opp_six = make_card("opp-six", "Opp Six", cost=6, power=6000)
        self.player1.cards_in_play = [dressrosa]
        self.player2.cards_in_play = [opp_six]
        self.player1.trash = [make_card(f"trash-{idx}", f"Trash {idx}", cost=1) for idx in range(15)]

        self.assertTrue(op04_093_king_kong_gun(self.game, self.player1, king_kong))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertEqual(6000, getattr(dressrosa, "power_modifier", 0))
        self.assertTrue(dressrosa.has_doubleattack)

        self.assertTrue(op04_094_trueno_bastardo(self.game, self.player1, trueno))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIn(opp_six, self.player2.trash)

        self.assertTrue(op04_095_barrier_counter(self.game, self.player1, barrier))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertEqual(4000, getattr(self.player1.leader, "_battle_power_modifier", 0))

    def test_op04_093_counts_the_event_itself_toward_the_trash_threshold(self) -> None:
        king_kong = make_card("OP04-093", "Gum-Gum King Kong Gun", card_type="EVENT", cost=3)
        dressrosa = make_card("dressrosa", "Dressrosa", cost=5, power=6000)
        dressrosa.card_origin = "Dressrosa"
        self.player1.cards_in_play = [dressrosa]
        self.player1.trash = [make_card(f"trash-{idx}", f"Trash {idx}", cost=1) for idx in range(14)]

        self.assertTrue(op04_093_king_kong_gun(self.game, self.player1, king_kong))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertEqual(6000, getattr(dressrosa, "power_modifier", 0))
        self.assertTrue(dressrosa.has_doubleattack)
        self.assertTrue(self.game._card_to_dict(dressrosa)["has_double_attack"])

    def test_op04_093_power_modifier_applies_to_real_battle_damage(self) -> None:
        king_kong = make_card("OP04-093", "Gum-Gum King Kong Gun", card_type="EVENT", cost=3)
        attacker = make_card("dressrosa-attacker", "Dressrosa Attacker", cost=5, power=5000)
        attacker.card_origin = "Dressrosa"
        defender = make_card("defender", "Defender", cost=4, power=10000)
        self.player1.cards_in_play = [attacker]
        self.player2.cards_in_play = [defender]
        self.player1.trash = [make_card(f"trash-{idx}", f"Trash {idx}", cost=1) for idx in range(15)]

        self.assertTrue(op04_093_king_kong_gun(self.game, self.player1, king_kong))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.game.pending_attack = {
            "attacker": attacker,
            "current_target": defender,
            "counter_power": 0,
            "attacker_player": self.player1,
            "defender_player": self.player2,
        }

        self.game._resolve_attack_damage()

        self.assertIn(defender, self.player2.trash)
        self.assertTrue(attacker.has_doubleattack)

    def test_op04_093_and_095_triggers_prompt_for_hand_trash(self) -> None:
        king_kong = make_card("OP04-093", "Gum-Gum King Kong Gun", card_type="EVENT", cost=3)
        barrier = make_card("OP04-095", "Barrier!!", card_type="EVENT", cost=1)
        self.player1.hand = [make_card("h1", "H1", cost=1)]
        self.player1.deck = [make_card("d1", "D1", cost=1), make_card("d2", "D2", cost=1), make_card("d3", "D3", cost=1)]

        self.assertTrue(op04_093_king_kong_gun_trigger(self.game, self.player1, king_kong))
        self.assertTrue(self.game.resolve_pending_choice(["0", "1"]))
        self.assertEqual(2, len(self.player1.trash))

        self.player1.hand = [make_card("h2", "H2", cost=1)]
        self.player1.deck = [make_card("d4", "D4", cost=1), make_card("d5", "D5", cost=1)]
        self.assertTrue(op04_095_barrier_trigger(self.game, self.player1, barrier))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertEqual(3, len(self.player1.trash))

    def test_op04_112_yamato_prompts_before_adding_life(self) -> None:
        yamato = make_card("OP04-112", "Yamato", cost=9, power=9000)
        target = make_card("opp-target", "Opp Target", cost=2)
        life_gain = make_card("life-gain", "Life Gain", cost=1)
        self.player1.life_cards = [make_card("only-life", "Only Life", cost=1)]
        self.player2.life_cards = [make_card("opp-life", "Opp Life", cost=1)]
        self.player2.cards_in_play = [target]
        self.player1.deck = [life_gain]

        self.assertTrue(op04_112_yamato(self.game, self.player1, yamato))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["yes"]))
        self.assertEqual(life_gain, self.player1.life_cards[-1])
        self.assertFalse(any("Life Gain" in log for log in self.game.action_logs))

    def test_op04_115_and_117_life_effects_follow_the_selected_order(self) -> None:
        gun_modoki = make_card("OP04-115", "Gun Modoki", card_type="EVENT", cost=1)
        heavenly_fire = make_card("OP04-117", "Heavenly Fire", card_type="EVENT", cost=1)
        wano = make_card("wano", "Wano Target", cost=3)
        wano.card_origin = "Land of Wano"
        opp_target = make_card("opp-target", "Opp Target", cost=3)
        top_life = make_card("top-life", "Top Life", cost=1)
        bottom_life = make_card("bottom-life", "Bottom Life", cost=1)
        self.player1.cards_in_play = [wano]
        self.player1.life_cards = [bottom_life, top_life]
        self.player2.cards_in_play = [opp_target]

        self.assertTrue(op04_115_gun_modoki(self.game, self.player1, gun_modoki))
        self.assertTrue(self.game.resolve_pending_choice(["yes"]))
        self.assertEqual(
            ["Top of Life", "Bottom of Life"],
            [option["label"] for option in self.game.pending_choice.options],
        )
        self.assertTrue(self.game.resolve_pending_choice(["bottom"]))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIn(bottom_life, self.player1.hand)
        self.assertTrue(wano.has_doubleattack)
        self.assertTrue(self.game._card_to_dict(wano)["has_double_attack"])

        self.assertTrue(op04_117_heavenly_fire(self.game, self.player1, heavenly_fire))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertTrue(self.game.resolve_pending_choice(["bottom"]))
        self.assertEqual(opp_target, self.player2.life_cards[0])
        self.assertTrue(getattr(opp_target, "is_face_up", False))

    def test_op04_117_trigger_can_take_life_and_put_hand_back(self) -> None:
        heavenly_fire = make_card("OP04-117", "Heavenly Fire", card_type="EVENT", cost=1)
        top_life = make_card("top-life", "Top Life", cost=1)
        bottom_life = make_card("bottom-life", "Bottom Life", cost=1)
        hand_card = make_card("hand-card", "Hand Card", cost=2)
        self.player1.life_cards = [bottom_life, top_life]
        self.player1.hand = [hand_card]

        self.assertTrue(op04_117_heavenly_fire_trigger(self.game, self.player1, heavenly_fire))
        self.assertTrue(self.game.resolve_pending_choice(["yes"]))
        self.assertTrue(self.game.resolve_pending_choice(["top"]))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertIn(top_life, self.player1.hand)
        self.assertEqual(hand_card, self.player1.life_cards[-1])


class OP04EngineRegressionTests(unittest.TestCase):
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
        self.player1.leader.card_type = "LEADER"
        self.player2.leader.card_type = "LEADER"

    def _resolve_leader_attack(self, attacker: Card) -> None:
        self.game.attack_with_card(attacker, -1)
        self.assertIsNotNone(self.game.pending_attack)
        self.assertTrue(self.game.respond_blocker(None))
        self.assertTrue(self.game.respond_counter([]))
        while self.game.awaiting_response == "trigger":
            self.assertTrue(self.game.respond_trigger(False))

    def _resolve_leader_attack_with_trigger_activation(self, attacker_index: int, *, activate: bool = True) -> None:
        self.assertTrue(self.game.declare_attack(attacker_index, -1))
        self.assertIsNotNone(self.game.pending_attack)
        self.assertTrue(self.game.respond_blocker(None))
        self.assertTrue(self.game.respond_counter([]))
        self.assertEqual("trigger", self.game.awaiting_response)
        self.assertTrue(self.game.respond_trigger(activate))

    def test_end_phase_prompts_for_deferred_don_activation(self) -> None:
        self.player1.don_pool = ["rested", "active", "rested"]
        self.player1.activate_don_eot_count = 2

        self.game._end_phase()
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0", "2"]))

        self.assertEqual(["active", "active", "active"], self.player1.don_pool)
        self.assertEqual(0, getattr(self.player1, "activate_don_eot_count", 0))

    def test_trigger_play_this_card_plays_each_identical_copy_from_life(self) -> None:
        attacker_one = make_card("opp-attacker-1", "Opp Attacker 1", card_type="CHARACTER", power=6000)
        attacker_two = make_card("opp-attacker-2", "Opp Attacker 2", card_type="CHARACTER", power=6000)
        attacker_one.played_turn = 0
        attacker_two.played_turn = 0
        self.player2.cards_in_play = [attacker_one, attacker_two]
        self.game.current_player = self.player2
        self.game.opponent_player = self.player1

        first_copy = make_card("ST01-002", "Usopp", card_type="CHARACTER", cost=2, power=3000)
        first_copy.trigger = "[Trigger] Play this card."
        second_copy = make_card("ST01-002", "Usopp", card_type="CHARACTER", cost=2, power=3000)
        second_copy.trigger = "[Trigger] Play this card."
        self.player1.life_cards = [first_copy, second_copy]

        self._resolve_leader_attack_with_trigger_activation(0)
        self.assertEqual(1, len(self.player1.cards_in_play))
        self.assertTrue(any(card is second_copy for card in self.player1.cards_in_play))
        self.assertEqual([], self.player1.trash)

        self._resolve_leader_attack_with_trigger_activation(1)
        self.assertEqual(2, len(self.player1.cards_in_play))
        self.assertTrue(any(card is first_copy for card in self.player1.cards_in_play))
        self.assertTrue(any(card is second_copy for card in self.player1.cards_in_play))
        self.assertEqual([], self.player1.trash)

    def test_next_turn_waits_for_baby5_end_of_turn_prompt_before_switching_players(self) -> None:
        baby5 = make_card("OP04-032", "Baby 5", cost=3)
        self.player1.cards_in_play = [baby5]
        self.player1.don_pool = ["rested", "rested", "rested"]
        self.player2.deck = [make_card("p2-deck", "P2 Deck", cost=1)]

        self.game.next_turn()

        self.assertIs(self.game.current_player, self.player1)
        self.assertIsNotNone(self.game.pending_choice)
        self.assertEqual("OP04-032", self.game.pending_choice.source_card_id)
        self.assertTrue(self.game.resolve_pending_choice(["yes"]))
        self.assertIs(self.game.current_player, self.player1)
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0", "1"]))

        self.assertEqual(["active", "active", "rested"], self.player1.don_pool)
        self.assertIn(baby5, self.player1.trash)
        self.assertIs(self.game.current_player, self.player2)

    def test_next_turn_waits_for_machvise_end_of_turn_don_prompt_before_switching_players(self) -> None:
        machvise = make_card("OP04-033", "Machvise", cost=4)
        active_target = make_card("opp-active", "Opp Active", cost=5)
        self.player1.leader.card_origin = "Donquixote Pirates"
        self.player2.cards_in_play = [active_target]
        self.player1.don_pool = ["rested", "rested"]
        self.player2.deck = [make_card("p2-deck", "P2 Deck", cost=1)]

        self.assertTrue(op04_033_machvise(self.game, self.player1, machvise))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertTrue(active_target.is_resting)

        self.game.next_turn()

        self.assertIs(self.game.current_player, self.player1)
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["1"]))

        self.assertEqual(["rested", "active"], self.player1.don_pool)
        self.assertIs(self.game.current_player, self.player2)

    def test_end_phase_rejects_too_many_don_selection_before_accepting_valid_choice(self) -> None:
        self.player1.don_pool = ["rested", "rested", "rested"]
        self.player1.activate_don_eot_count = 2
        self.game.phase = GamePhase.END

        self.assertTrue(self.game._queue_end_of_turn_don_activation_choice())
        self.assertFalse(self.game.resolve_pending_choice(["0", "1", "2"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertEqual(["rested", "rested", "rested"], self.player1.don_pool)
        self.assertTrue(self.game.resolve_pending_choice(["0", "2"]))
        self.assertEqual(["active", "rested", "active"], self.player1.don_pool)

    def test_skip_next_refresh_keeps_character_rested_once(self) -> None:
        luffy = make_card("OP04-090", "Luffy", cost=8)
        luffy.is_resting = True
        luffy.skip_next_refresh = True
        self.player1.cards_in_play = [luffy]

        self.player1.reset_for_new_turn()

        self.assertTrue(luffy.is_resting)
        self.assertFalse(getattr(luffy, "skip_next_refresh", False))

    def test_sabo_protection_applies_to_new_character_and_expires(self) -> None:
        sabo = make_card("OP04-083", "Sabo", cost=5)
        discard_one = make_card("discard-1", "Discard 1", cost=1)
        discard_two = make_card("discard-2", "Discard 2", cost=2)
        new_char = make_card("new-char", "New Character", cost=4)
        self.player1.cards_in_play = [sabo]
        self.player1.hand = [discard_one, discard_two]

        self.assertTrue(op04_083_sabo_play(self.game, self.player1, sabo))
        self.assertTrue(sabo.cannot_be_ko_by_effects)

        self.player1.cards_in_play.append(new_char)
        self.game._apply_keywords(new_char)
        self.assertTrue(new_char.cannot_be_ko_by_effects)

        self.game._clear_temporary_effects(self.player1)
        self.assertTrue(new_char.cannot_be_ko_by_effects)

        self.game.turn_count += 1
        self.game._clear_temporary_effects(self.player1)
        self.assertFalse(new_char.cannot_be_ko_by_effects)

    def test_kyros_effect_ko_prompts_for_replacement_and_can_prevent_ko(self) -> None:
        kyros = make_card("OP04-082", "Kyros", cost=3, power=5000)
        corrida = make_card("OP04-096", "Corrida Coliseum", card_type="STAGE", cost=1)
        self.player2.cards_in_play = [kyros, corrida]

        self.assertEqual("pending", self.game._attempt_character_ko(kyros, by_effect=True))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["1"]))

        self.assertIn(kyros, self.player2.cards_in_play)
        self.assertTrue(corrida.is_resting)
        self.assertNotIn(kyros, self.player2.trash)

    def test_kyros_decline_or_no_replacement_allows_ko(self) -> None:
        kyros = make_card("OP04-082", "Kyros", cost=3, power=5000)
        self.player2.cards_in_play = [kyros]
        self.player2.leader.is_resting = True

        self.assertEqual("ko", self.game._attempt_character_ko(kyros, by_effect=True))
        self.assertIn(kyros, self.player2.trash)

    def test_corrida_coliseum_allows_dressrosa_character_to_attack_character_on_play_turn(self) -> None:
        stage = make_card("OP04-096", "Corrida Coliseum", card_type="STAGE", cost=1)
        attacker = make_card("dressrosa-attacker", "Dressrosa Attacker", cost=4, power=5000)
        defender = make_card("defender", "Defender", cost=3, power=1000)
        attacker.card_origin = "Dressrosa"
        defender.is_resting = True
        attacker.played_turn = self.game.turn_count
        self.player1.leader.card_origin = "Dressrosa"
        self.player1.cards_in_play = [stage, attacker]
        self.player2.cards_in_play = [defender]

        self.assertTrue(op04_096_corrida_coliseum(self.game, self.player1, stage))
        self.assertTrue(self.game.declare_attack(1, 0))

    def test_corrida_coliseum_does_not_let_new_character_attack_leader(self) -> None:
        stage = make_card("OP04-096", "Corrida Coliseum", card_type="STAGE", cost=1)
        attacker = make_card("dressrosa-attacker", "Dressrosa Attacker", cost=4, power=5000)
        attacker.card_origin = "Dressrosa"
        attacker.played_turn = self.game.turn_count
        self.player1.leader.card_origin = "Dressrosa"
        self.player1.cards_in_play = [stage, attacker]

        self.assertTrue(op04_096_corrida_coliseum(self.game, self.player1, stage))
        self.assertFalse(self.game.declare_attack(1, -1))

    def test_ice_oni_bottom_decks_cost_five_or_less_target_after_battle(self) -> None:
        attacker = make_card("OP04-047", "Ice Oni", cost=4, power=5000)
        attacker.ice_oni_effect = True
        defender = make_card("defender", "Defender", cost=5, power=4000)
        self.player1.cards_in_play = [attacker]
        self.player2.cards_in_play = [defender]
        self.game.pending_attack = {
            "attacker": attacker,
            "attacker_player": self.player1,
            "current_target": defender,
            "defender_player": self.player2,
        }

        self.game._finish_attack()

        self.assertNotIn(defender, self.player2.cards_in_play)
        self.assertEqual([defender], self.player2.deck)

    def test_chinjao_on_ko_opponent_triggers_after_battle(self) -> None:
        attacker = make_card("OP04-086", "Chinjao", cost=5, power=6000)
        attacker.attached_don = 1
        defender = make_card("defender", "Defender", cost=3, power=3000)
        keep = make_card("keep", "Keep", cost=1)
        draw_one = make_card("draw-one", "Draw One", cost=2)
        draw_two = make_card("draw-two", "Draw Two", cost=3)
        self.player1.cards_in_play = [attacker]
        self.player2.cards_in_play = [defender]
        self.player1.hand = [keep]
        self.player1.deck = [draw_one, draw_two]
        self.game.pending_attack = {
            "attacker": attacker,
            "current_target": defender,
            "counter_power": 0,
            "attacker_player": self.player1,
            "defender_player": self.player2,
        }

        self.game._resolve_attack_damage()

        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0", "1"]))
        self.assertIn(defender, self.player2.trash)
        self.assertEqual([draw_two], self.player1.hand)

    def test_op04_093_double_attack_removes_two_life_in_live_attack_flow(self) -> None:
        king_kong = make_card("OP04-093", "Gum-Gum King Kong Gun", card_type="EVENT", cost=3)
        attacker = make_card("dressrosa-attacker", "Dressrosa Attacker", card_type="CHARACTER", cost=5, power=5000)
        attacker.card_origin = "Dressrosa"
        self.player1.cards_in_play = [attacker]
        self.player1.trash = [make_card(f"trash-{idx}", f"Trash {idx}", cost=1) for idx in range(14)]
        self.player2.life_cards = [
            make_card("life-1", "Life 1"),
            make_card("life-2", "Life 2"),
            make_card("life-3", "Life 3"),
        ]

        self.assertTrue(op04_093_king_kong_gun(self.game, self.player1, king_kong))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self._resolve_leader_attack(attacker)

        self.assertEqual(1, len(self.player2.life_cards))
        self.assertTrue(attacker.has_doubleattack)

    def test_op04_115_double_attack_removes_two_life_in_live_attack_flow(self) -> None:
        gun_modoki = make_card("OP04-115", "Gun Modoki", card_type="EVENT", cost=1)
        yamato = make_card("yamato", "Yamato", card_type="CHARACTER", cost=9, power=9000)
        yamato.card_origin = "Land of Wano"
        self.player1.cards_in_play = [yamato]
        self.player1.life_cards = [make_card("bottom-life", "Bottom Life"), make_card("top-life", "Top Life")]
        self.player2.life_cards = [
            make_card("life-1", "Life 1"),
            make_card("life-2", "Life 2"),
            make_card("life-3", "Life 3"),
        ]

        self.assertTrue(op04_115_gun_modoki(self.game, self.player1, gun_modoki))
        self.assertTrue(self.game.resolve_pending_choice(["yes"]))
        self.assertTrue(self.game.resolve_pending_choice(["top"]))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self._resolve_leader_attack(yamato)

        self.assertEqual(1, len(self.player2.life_cards))
        self.assertTrue(yamato.has_doubleattack)

    def test_yokozuna_returns_only_the_selected_same_id_character(self) -> None:
        yokozuna = make_card("OP04-068", "Yokozuna", cost=2, power=3000)
        streusen_one = make_card("OP03-123", "Streusen", cost=2, power=2000)
        streusen_two = make_card("OP03-123", "Streusen", cost=2, power=2000)
        self.player1.don_pool = ["active"]
        self.player2.cards_in_play = [streusen_one, streusen_two]

        from optcg_engine.effects.sets.op04_effects import op04_068_yokozuna_defense

        self.assertTrue(op04_068_yokozuna_defense(self.game, self.player1, yokozuna))
        self.assertTrue(self.game.resolve_pending_choice(["yes"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["1"]))

        self.assertEqual(1, len(self.player2.hand))
        self.assertEqual(1, len(self.player2.cards_in_play))
        self.assertIs(self.player2.hand[0], streusen_two)
        self.assertIs(self.player2.cards_in_play[0], streusen_one)


class EffectTesterSeedTests(unittest.TestCase):
    def test_op04_046_preview_setup_seeds_two_plague_rounds_and_two_ice_oni(self) -> None:
        card_data = make_effect_test_card_data(
            "OP04-046",
            "Queen",
            card_type="CHARACTER",
            color="Blue",
            card_origin="Animal Kingdom Pirates",
            effect="[On Play] Look at 7 cards from the top of your deck and reveal up to 2 [Plague Rounds] or [Ice Oni] and add them to your hand.",
        )
        _, player, _ = build_game_state(card_data, "on_play")
        top_seven = player.deck[:7]

        self.assertEqual(7, len(top_seven))
        self.assertEqual(2, sum(card.name == "Plague Rounds" for card in top_seven))
        self.assertEqual(2, sum(card.name == "Ice Oni" for card in top_seven))

    def test_op04_066_preview_setup_places_card_on_top_of_both_life_stacks(self) -> None:
        card_data = make_effect_test_card_data(
            "OP04-066",
            "Miss Valentine",
            card_type="CHARACTER",
            color="Blue",
            card_origin="Baroque Works",
            trigger="[Trigger] DON!! -1: Play this card.",
        )
        game_state, player, _ = build_game_state(card_data, "trigger")

        self.assertEqual("OP04-066", player.life_cards[-1].id)
        self.assertEqual("OP04-066", game_state.player2.life_cards[-1].id)

    def test_op04_084_preview_setup_seeds_literal_cp_target_in_top_three(self) -> None:
        card_data = make_effect_test_card_data(
            "OP04-084",
            "Stussy",
            card_type="CHARACTER",
            cost=4,
            power=5000,
            color="Black",
            card_origin="Cipher Pol",
            effect="[On Play] Look at 3 cards from the top of your deck; play up to 1 type {CP} Character card with a cost of 2 or less other than [Stussy].",
        )
        _, player, _ = build_game_state(card_data, "on_play")
        top_three = player.deck[:3]

        self.assertTrue(any((card.card_origin or "") == "CP" and (card.cost or 0) <= 2 for card in top_three))

    def test_op04_119_preview_setup_seeds_a_green_cost_five_in_hand(self) -> None:
        card_data = make_effect_test_card_data(
            "OP04-119",
            "Donquixote Rosinante",
            card_type="CHARACTER",
            cost=2,
            power=2000,
            color="Green",
            card_origin="Donquixote Pirates",
            effect="[On Play] You may rest this Character: Play up to 1 green Character card with a cost of 5 from your hand.",
        )
        _, player, _ = build_game_state(card_data, "on_play")

        self.assertTrue(any("Green" in (card.colors or []) and (card.cost or 0) == 5 for card in player.hand))


if __name__ == "__main__":
    unittest.main()
