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
from optcg_engine.effects.effect_registry import draw_cards, filter_by_cost_range, filter_by_max_cost, has_hardcoded_effect
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
from optcg_engine.effects.sets.op05_effects import (
    birdcage_effect,
    op05_029_doflamingo,
    op05_032_pica_eot,
    op05_032_pica_protection,
    op05_033_baby5,
    op05_034_baby5,
    op05_037_because_justice,
    op05_037_because_justice_trigger,
    op05_038_charlestone,
    op05_038_charlestone_trigger,
    op05_039_stick_stickem_meteora,
    op05_039_stick_stickem_meteora_trigger,
    op05_040_birdcage_continuous,
    op05_041_sakazuki_activate,
    op05_041_sakazuki_attack,
    op05_042_issho,
    op05_043_ulti,
    op05_045_stainless,
    op05_046_dalmatian,
    op05_047_hawkins_block,
    op05_048_bastille,
    op05_049_haccha,
    op05_050_hina,
    op05_051_borsalino,
    op05_052_maynard,
    op05_053_mozambia,
    op05_054_garp,
    op05_055_drake_play,
    op05_056_barrels,
    op05_057_hound_blaze,
    op05_057_hound_blaze_trigger,
    op05_058_waste_of_human_life,
    op05_058_waste_of_human_life_trigger,
    op05_059_world_of_violence,
    op05_059_world_of_violence_trigger,
    op05_060_luffy_leader,
    op05_061_usohachi,
    op05_062_onami,
    op05_063_orobi,
    op05_064_killer,
    op05_066_jinbe_continuous,
    op05_067_zorojuurou,
    op05_068_chopaemon,
    op05_069_law,
    op05_070_franosuke,
    op05_071_bepo,
    op05_072_honekichi,
    op05_073_doublefinger_play,
    op05_073_doublefinger_trigger,
    op05_074_kid_don_return,
    op05_075_mr1,
    op05_077_gamma_knife,
    op05_078_punk_rotten,
    op05_079_viola,
    op05_080_elizabello,
    op05_082_shirahoshi,
    op05_090_riku_play,
    op05_090_riku_ko,
    op05_091_rebecca_play,
    op05_093_lucci,
    op05_096_500_million,
    op05_100_enel_protection,
    op05_101_ohm_play,
    op05_104_conis,
    op05_105_satori,
    op05_109_pagaya,
    op05_111_hotori,
    op05_112_mckinley_ko,
    op05_115_amaru_trigger,
    op05_119_luffy_play,
    op05_009_tohtoh,
    op05_015_betty,
    op05_016_morley,
    op05_016_morley_trigger,
    op05_017_lindbergh,
    op05_017_lindbergh_trigger,
    op05_021_revolutionary_army_hq,
    op05_019_fire_fist,
    op05_019_fire_fist_trigger,
    op05_020_four_thousand_brick_fist,
    op05_020_four_thousand_brick_fist_trigger,
    op05_022_rosinante_eot,
    op05_024_kuween,
    op05_025_gladius,
    op05_003_inazuma,
    op05_004_ivankov,
    op05_005_karasu_attack,
    op05_007_sabo,
    op05_023_vergo,
    op05_027_law,
    op05_028_doflamingo,
    op05_026_sarquiss,
    op05_031_buffalo,
    op05_036_monet_block,
    op05_002_betty_leader,
    op05_006_koala,
    op05_008_chaka,
    op05_010_robin,
    op05_011_kuma_play,
    op05_011_kuma_trigger,
    op05_013_bunny_joe,
    op05_014_pell,
    op05_018_emporio_energy_hormone,
    op05_018_emporio_energy_hormone_trigger,
    op05_076_when_youre_at_sea,
    op05_076_when_youre_at_sea_trigger,
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

    def test_op05_001_sabo_leader_prompts_and_prevents_ko(self) -> None:
        sabo = make_card("OP05-001", "Sabo", card_type="LEADER", power=5000, life=4)
        protected = make_card("p1-protected", "Protected", card_type="CHARACTER", power=5000)
        attacker = make_card("p2-attacker", "Attacker", card_type="CHARACTER", power=7000)
        self.player1.leader = sabo
        self.player1.cards_in_play = [protected]
        self.player2.cards_in_play = [attacker]
        self.player1.don_pool = ["rested"]
        sabo.attached_don = 1
        self.game.current_player = self.player2
        self.game.opponent_player = self.player1

        self.assertEqual("pending", self.game._attempt_character_ko(protected, by_effect=False, attacker=attacker, controller=self.player2))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["use"]))

        self.assertIn(protected, self.player1.cards_in_play)
        self.assertEqual(-1000, getattr(protected, "power_modifier", 0))
        self.assertTrue(getattr(sabo, "op05_001_used", False))

    def test_op05_002_belo_betty_trashes_cost_and_buffs_up_to_three_for_turn(self) -> None:
        leader = make_card("OP05-002", "Belo Betty", card_type="LEADER", power=5000, life=4)
        cost_card = make_card("betty-cost", "Betty Cost", card_type="CHARACTER", power=2000)
        cost_card.card_origin = "Revolutionary Army"
        rev_one = make_card("rev-1", "Rev One", card_type="CHARACTER", power=4000)
        rev_one.card_origin = "Revolutionary Army"
        rev_two = make_card("rev-2", "Rev Two", card_type="CHARACTER", power=4000)
        rev_two.trigger = "[Trigger] Draw 1."
        rev_three = make_card("rev-3", "Rev Three", card_type="CHARACTER", power=5000)
        rev_three.card_origin = "Revolutionary Army"
        self.player1.leader = leader
        self.player1.hand = [cost_card]
        self.player1.cards_in_play = [rev_one, rev_two, rev_three]

        self.assertTrue(op05_002_betty_leader(self.game, self.player1, leader))
        self.assertTrue(self.game.resolve_pending_choice(["pay"]))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertTrue(self.game.resolve_pending_choice(["0", "1", "2"]))

        self.assertIn(cost_card, self.player1.trash)
        self.assertEqual(3000, getattr(rev_one, "power_modifier", 0))
        self.assertEqual(3000, getattr(rev_two, "power_modifier", 0))
        self.assertEqual(3000, getattr(rev_three, "power_modifier", 0))
        self.assertEqual(self.game.turn_count, getattr(rev_one, "power_modifier_expires_on_turn", -1))

    def test_op05_003_inazuma_gains_rush_from_other_7000_character(self) -> None:
        inazuma = make_card("OP05-003", "Inazuma", card_type="CHARACTER", power=5000)
        ally = make_card("ally-7000", "Ally", card_type="CHARACTER", power=6000)
        ally.attached_don = 1
        self.player1.cards_in_play = [inazuma, ally]

        self.assertTrue(op05_003_inazuma(self.game, self.player1, inazuma))
        self.assertTrue(inazuma.has_rush)

    def test_op05_004_ivankov_prompts_for_revolutionary_army_play(self) -> None:
        ivankov = make_card("OP05-004", "Emporio.Ivankov", card_type="CHARACTER", power=5000)
        ivankov.attached_don = 2
        rev_target = make_card("rev-target", "Morley", card_type="CHARACTER", power=5000)
        rev_target.card_origin = "Revolutionary Army"
        other_ivankov = make_card("rev-same-name", "Emporio.Ivankov", card_type="CHARACTER", power=5000)
        other_ivankov.card_origin = "Revolutionary Army"
        self.player1.hand = [rev_target, other_ivankov]

        self.assertTrue(op05_004_ivankov(self.game, self.player1, ivankov))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertIn(rev_target, self.player1.cards_in_play)
        self.assertNotIn(rev_target, self.player1.hand)
        self.assertTrue(getattr(ivankov, "op05_004_used", False))

    def test_op05_006_008_010_011_013_014_018_batch(self) -> None:
        koala = make_card("OP05-006", "Koala", card_type="CHARACTER", power=4000)
        chaka = make_card("OP05-008", "Chaka", card_type="CHARACTER", power=5000)
        robin = make_card("OP05-010", "Nico Robin", card_type="CHARACTER", power=3000)
        kuma = make_card("OP05-011", "Bartholomew Kuma", card_type="CHARACTER", power=4000)
        bunny = make_card("OP05-013", "Bunny Joe", card_type="CHARACTER", power=1000)
        pell = make_card("OP05-014", "Pell", card_type="CHARACTER", power=5000)
        hormone = make_card("OP05-018", "Emporio Energy Hormone", card_type="EVENT", cost=1)

        self.player1.leader.card_origin = "Revolutionary Army"
        koala_target = make_card("koala-target", "Koala Target", card_type="CHARACTER", power=4000)
        low_one = make_card("low-one", "Low One", card_type="CHARACTER", power=1000)
        low_two = make_card("low-two", "Low Two", card_type="CHARACTER", power=2000)
        pell_target = make_card("pell-target", "Pell Target", card_type="CHARACTER", power=5000)
        self.player2.cards_in_play = [koala_target, low_one, low_two, pell_target]

        self.assertTrue(op05_006_koala(self.game, self.player1, koala))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertEqual(-3000, getattr(koala_target, "power_modifier", 0))
        self.assertEqual(self.game.turn_count, getattr(koala_target, "power_modifier_expires_on_turn", -1))

        leader_target = self.player1.leader
        chaka.attached_don = 1
        self.player1.don_pool = ["rested", "rested", "active"]
        self.assertTrue(op05_008_chaka(self.game, self.player1, chaka))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertEqual(2, getattr(leader_target, "attached_don", 0))

        self.assertTrue(op05_010_robin(self.game, self.player1, robin))
        self.assertTrue(self.game.resolve_pending_choice(["1"]))
        self.assertIn(low_one, self.player2.trash)

        boosted_low = make_card("boosted-low", "Boosted Low", card_type="CHARACTER", power=1000)
        boosted_low.power_modifier = 1000
        self.player2.cards_in_play = [boosted_low, low_two]
        self.assertTrue(op05_011_kuma_play(self.game, self.player1, kuma))
        self.assertTrue(self.game.resolve_pending_choice(["1"]))
        self.assertIn(low_two, self.player2.trash)
        self.assertNotIn(boosted_low, self.player2.trash)

        self.player1.leader.colors = ["Red", "Blue"]
        self.assertTrue(op05_011_kuma_trigger(self.game, self.player1, kuma))
        self.assertIn(kuma, self.player1.cards_in_play)
        self.assertEqual(self.game.turn_count, getattr(kuma, "played_turn", -1))

        self.assertTrue(op05_013_bunny_joe(self.game, self.player1, bunny))
        self.assertTrue(bunny.has_blocker)

        pell.attached_don = 1
        self.player2.cards_in_play = [pell_target]
        self.assertTrue(op05_014_pell(self.game, self.player1, pell))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertEqual(-2000, getattr(pell_target, "power_modifier", 0))
        self.assertEqual(self.game.turn_count, getattr(pell_target, "power_modifier_expires_on_turn", -1))

        counter_target = make_card("counter-target", "Counter Target", card_type="CHARACTER", power=5000)
        rev_play = make_card("rev-play", "Rev Play", card_type="CHARACTER", power=5000)
        rev_play.card_origin = "Revolutionary Army"
        self.player1.cards_in_play = [counter_target]
        self.player1.hand = [rev_play]
        self.assertTrue(op05_018_emporio_energy_hormone(self.game, self.player1, hormone))
        self.assertTrue(self.game.resolve_pending_choice(["1"]))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertEqual(3000, getattr(counter_target, "_battle_power_modifier", 0))
        self.assertIn(rev_play, self.player1.cards_in_play)

        trigger_rev = make_card("trigger-rev", "Trigger Rev", card_type="CHARACTER", power=4000)
        trigger_rev.card_origin = "Revolutionary Army"
        self.player1.hand = [trigger_rev]
        self.assertTrue(op05_018_emporio_energy_hormone_trigger(self.game, self.player1, hormone))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIn(trigger_rev, self.player1.cards_in_play)

    def test_op05_005_karasu_attack_can_target_leader(self) -> None:
        karasu = make_card("OP05-005", "Karasu", card_type="CHARACTER", power=6000)
        karasu.attached_don = 1
        self.player2.cards_in_play = [make_card("opp-char", "Opp Char", card_type="CHARACTER", power=3000)]

        self.assertTrue(op05_005_karasu_attack(self.game, self.player1, karasu))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertEqual(self.player2.leader.id, self.game.pending_choice.options[0]["card_id"])
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertEqual(-1000, getattr(self.player2.leader, "power_modifier", 0))

    def test_op05_007_sabo_reprompts_on_invalid_total_power_and_kos_valid_targets(self) -> None:
        sabo = make_card("OP05-007", "Sabo", card_type="CHARACTER", power=7000)
        low = make_card("opp-low", "Low", card_type="CHARACTER", power=1000)
        mid = make_card("opp-mid", "Mid", card_type="CHARACTER", power=3000)
        high = make_card("opp-high", "High", card_type="CHARACTER", power=2000)
        self.player2.cards_in_play = [low, mid, high]

        self.assertTrue(op05_007_sabo(self.game, self.player1, sabo))
        self.assertTrue(self.game.resolve_pending_choice(["1", "2"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertIn("total power of 4000 or less", self.game.pending_choice.prompt)

        self.assertTrue(self.game.resolve_pending_choice(["0", "2"]))
        self.assertNotIn(low, self.player2.cards_in_play)
        self.assertNotIn(mid, self.player2.cards_in_play)
        self.assertIn(high, self.player2.cards_in_play)

    def test_op05_023_vergo_kos_selected_target(self) -> None:
        vergo = make_card("OP05-023", "Vergo", card_type="CHARACTER", power=5000)
        vergo.attached_don = 1
        target = make_card("opp-rested", "Rested", card_type="CHARACTER", cost=3, power=4000)
        target.is_resting = True
        self.player2.cards_in_play = [target]

        self.assertTrue(op05_023_vergo(self.game, self.player1, vergo))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertNotIn(target, self.player2.cards_in_play)
        self.assertIn(target, self.player2.trash)

    def test_op05_026_sarquiss_prompts_optional_cost_and_sets_active(self) -> None:
        sarquiss = make_card("OP05-026", "Sarquiss", card_type="CHARACTER", cost=4, power=5000)
        fodder = make_card("p1-fodder", "Fodder", card_type="CHARACTER", cost=3, power=3000)
        sarquiss.attached_don = 1
        sarquiss.is_resting = True
        sarquiss.has_attacked = True
        self.player1.cards_in_play = [sarquiss, fodder]

        self.assertTrue(op05_026_sarquiss(self.game, self.player1, sarquiss))
        self.assertTrue(self.game.resolve_pending_choice(["use"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertTrue(fodder.is_resting)
        self.assertFalse(sarquiss.is_resting)
        self.assertFalse(sarquiss.has_attacked)
        self.assertTrue(getattr(sarquiss, "op05_026_used", False))

    def test_op05_030_rosinante_trashes_self_to_save_rested_character(self) -> None:
        rosinante = make_card("OP05-030", "Donquixote Rosinante", card_type="CHARACTER", power=2000)
        protected = make_card("protected", "Protected", card_type="CHARACTER", power=5000)
        protected.is_resting = True
        self.player1.cards_in_play = [rosinante, protected]
        self.game.current_player = self.player2
        self.game.opponent_player = self.player1

        self.assertEqual("pending", self.game._attempt_character_ko(protected, by_effect=True, controller=self.player2))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["use"]))

        self.assertIn(protected, self.player1.cards_in_play)
        self.assertNotIn(rosinante, self.player1.cards_in_play)
        self.assertIn(rosinante, self.player1.trash)

    def test_op05_009_toh_toh_uses_effective_leader_power(self) -> None:
        toh_toh = make_card("OP05-009", "Toh-Toh", card_type="CHARACTER", power=2000)
        self.player1.leader.power = 0
        self.player1.leader.power_modifier = -1000
        draw = make_card("draw-card", "Draw Card", card_type="CHARACTER")
        self.player1.deck = [draw]

        self.assertTrue(op05_009_tohtoh(self.game, self.player1, toh_toh))
        self.assertIn(draw, self.player1.hand)

        self.player1.hand = []
        self.player1.deck = [draw]
        self.player1.leader.power_modifier = -1000
        self.player1.leader.attached_don = 2
        self.assertTrue(op05_009_tohtoh(self.game, self.player1, toh_toh))
        self.assertNotIn(draw, self.player1.hand)

    def test_op05_015_belo_betty_searches_top_five_and_orders_remaining_bottom(self) -> None:
        betty = make_card("OP05-015", "Belo Betty", card_type="CHARACTER", power=5000)
        target = make_card("target", "Target", card_type="CHARACTER", cost=2)
        target.card_origin = "Revolutionary Army"
        filler = [make_card(f"fill-{i}", f"Fill {i}", card_type="CHARACTER", cost=i + 1) for i in range(4)]
        self.player1.deck = [target, *filler, make_card("tail", "Tail", card_type="CHARACTER")]

        self.assertTrue(op05_015_betty(self.game, self.player1, betty))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        while self.game.pending_choice is not None:
            self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertIn(target, self.player1.hand)
        self.assertEqual(["Tail", "Fill 0", "Fill 1", "Fill 2", "Fill 3"], [card.name for card in self.player1.deck])

    def test_op05_016_morley_attack_disables_blockers_and_trigger_prompts_to_play(self) -> None:
        morley = make_card("OP05-016", "Morley", card_type="CHARACTER", power=6000)
        blocker = make_card("opp-blocker", "Blocker", card_type="CHARACTER", power=5000)
        blocker.has_blocker = True
        morley.attached_don = 1
        self.player2.cards_in_play = [blocker]

        self.assertTrue(op05_016_morley(self.game, self.player1, morley))
        self.assertTrue(blocker.blocker_disabled)

        trigger_card = make_card("OP05-016", "Morley", card_type="CHARACTER", power=5000)
        trigger_card.trigger = "[Trigger] You may trash 1 card from your hand: If your Leader is multicolored, play this card."
        discard = make_card("discard", "Discard", card_type="CHARACTER", power=1000)
        attacker = make_card("opp-attacker", "Opp Attacker", card_type="CHARACTER", power=6000)
        attacker.played_turn = 0
        self.player1.leader.colors = ["Red", "Blue"]
        self.player1.hand = [discard]
        self.player1.life_cards = [trigger_card]
        self.player2.cards_in_play = [attacker]
        self.game.current_player = self.player2
        self.game.opponent_player = self.player1

        self._resolve_leader_attack_with_trigger_activation(0, activate=True)
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["use"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertIn(trigger_card, self.player1.cards_in_play)
        self.assertIn(discard, self.player1.trash)
        self.assertIsNone(getattr(self.game, "_pending_trigger_followup", None))

    def test_op05_017_lindbergh_attack_and_trigger_use_prompts(self) -> None:
        lindbergh = make_card("OP05-017", "Lindbergh", card_type="CHARACTER", power=6000)
        lindbergh.attached_don = 1
        low = make_card("opp-low", "Low", card_type="CHARACTER", power=3000)
        high = make_card("opp-high", "High", card_type="CHARACTER", power=4000)
        self.player2.cards_in_play = [low, high]

        self.assertTrue(op05_017_lindbergh(self.game, self.player1, lindbergh))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertNotIn(low, self.player2.cards_in_play)
        self.assertIn(high, self.player2.cards_in_play)

        trigger_card = make_card("OP05-017", "Lindbergh", card_type="CHARACTER", power=5000)
        discard = make_card("discard-2", "Discard 2", card_type="CHARACTER", power=1000)
        self.player1.leader.colors = ["Green", "Blue"]
        self.player1.hand = [discard]

        self.assertTrue(op05_017_lindbergh_trigger(self.game, self.player1, trigger_card))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["use"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertIn(trigger_card, self.player1.cards_in_play)
        self.assertIn(discard, self.player1.trash)

    def test_op05_019_fire_fist_main_and_trigger_prompt_for_followup_ko(self) -> None:
        fire_fist = make_card("OP05-019", "Fire Fist", card_type="EVENT", cost=1)
        target = make_card("opp-target", "Target", card_type="CHARACTER", power=3000)
        other = make_card("opp-other", "Other", card_type="CHARACTER", power=1000)
        self.player2.cards_in_play = [target, other]
        self.player1.life_cards = [make_card("life", "Life", card_type="CHARACTER")]

        self.assertTrue(op05_019_fire_fist(self.game, self.player1, fire_fist))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertNotIn(target, self.player2.cards_in_play)
        self.assertIn(other, self.player2.cards_in_play)

        trigger_target = make_card("opp-trigger-target", "Trigger Target", card_type="CHARACTER", power=4000)
        self.player2.cards_in_play = [trigger_target]
        self.player1.life_cards = [make_card("life-a", "Life A", card_type="CHARACTER"), make_card("life-b", "Life B", card_type="CHARACTER")]

        self.assertTrue(op05_019_fire_fist_trigger(self.game, self.player1, fire_fist))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertNotIn(trigger_target, self.player2.cards_in_play)

    def test_op05_020_four_thousand_brick_fist_main_and_trigger(self) -> None:
        brick_fist = make_card("OP05-020", "Four Thousand-Brick Fist", card_type="EVENT", cost=1)
        own = make_card("own-char", "Own Char", card_type="CHARACTER", power=4000)
        target = make_card("opp-char", "Opp Char", card_type="CHARACTER", power=2000)
        self.player1.cards_in_play = [own]
        self.player2.cards_in_play = [target]

        self.assertTrue(op05_020_four_thousand_brick_fist(self.game, self.player1, brick_fist))
        self.assertTrue(self.game.resolve_pending_choice(["1"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertEqual(2000, getattr(own, "power_modifier", 0))
        self.assertNotIn(target, self.player2.cards_in_play)

        self.assertTrue(op05_020_four_thousand_brick_fist_trigger(self.game, self.player1, brick_fist))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertEqual(1000, getattr(self.player1.leader, "power_modifier", 0))

    def test_op05_022_rosinante_sets_leader_active_with_six_or_fewer_cards(self) -> None:
        leader = make_card("OP05-022", "Donquixote Rosinante", card_type="LEADER", power=5000, life=4)
        leader.is_resting = True
        self.player1.leader = leader
        self.player1.hand = [make_card(f"hand-{i}", f"Hand {i}", card_type="CHARACTER") for i in range(6)]

        self.assertTrue(op05_022_rosinante_eot(self.game, self.player1, leader))
        self.assertFalse(leader.is_resting)

        leader.is_resting = True
        self.player1.hand.append(make_card("hand-6", "Hand 6", card_type="CHARACTER"))
        self.assertFalse(op05_022_rosinante_eot(self.game, self.player1, leader))
        self.assertTrue(leader.is_resting)

    def test_op05_021_revolutionary_army_hq_prompts_before_paying_cost_and_searches(self) -> None:
        stage = make_card("OP05-021", "Revolutionary Army HQ", card_type="STAGE", cost=2)
        discard = make_card("discard", "Discard", card_type="CHARACTER", power=1000)
        target = make_card("rev-target", "Rev Target", card_type="CHARACTER", cost=3, power=5000)
        target.card_origin = "Revolutionary Army"
        filler_one = make_card("filler-one", "Filler One", card_type="CHARACTER", cost=1)
        filler_two = make_card("filler-two", "Filler Two", card_type="CHARACTER", cost=2)
        tail = make_card("tail", "Tail", card_type="CHARACTER", cost=4)
        self.player1.hand = [discard]
        self.player1.deck = [target, filler_one, filler_two, tail]

        self.assertTrue(op05_021_revolutionary_army_hq(self.game, self.player1, stage))
        self.assertFalse(stage.is_resting)
        self.assertFalse(getattr(stage, "main_activated_this_turn", False))
        self.assertTrue(self.game.resolve_pending_choice(["use"]))
        self.assertFalse(stage.is_resting)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertTrue(stage.is_resting)
        self.assertTrue(getattr(stage, "main_activated_this_turn", False))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        while self.game.pending_choice is not None:
            self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertIn(discard, self.player1.trash)
        self.assertIn(target, self.player1.hand)
        self.assertEqual(["Tail", "Filler One", "Filler Two"], [card.name for card in self.player1.deck])

    def test_op05_024_025_027_028_031_036_076_batch(self) -> None:
        kuween = make_card("OP05-024", "Kuween", card_type="CHARACTER", cost=2, power=3000)
        self.assertTrue(op05_024_kuween(self.game, self.player1, kuween))
        self.assertTrue(kuween.has_blocker)

        gladius = make_card("OP05-025", "Gladius", card_type="CHARACTER", cost=4, power=5000)
        rest_target = make_card("rest-target", "Rest Target", card_type="CHARACTER", cost=4, power=4000)
        rest_target.cost_modifier = -1
        self.player2.cards_in_play = [rest_target, make_card("opp-stage", "Opp Stage", card_type="STAGE", cost=1)]
        self.assertTrue(op05_025_gladius(self.game, self.player1, gladius))
        self.assertTrue(self.game.resolve_pending_choice(["use"]))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertTrue(gladius.is_resting)
        self.assertTrue(rest_target.is_resting)

        law = make_card("OP05-027", "Trafalgar Law", card_type="CHARACTER", cost=3, power=4000)
        law_target = make_card("law-target", "Law Target", card_type="CHARACTER", cost=4, power=4000)
        law_target.cost_modifier = -1
        self.player1.cards_in_play = [law]
        self.player2.cards_in_play = [law_target]
        self.assertTrue(op05_027_law(self.game, self.player1, law))
        self.assertTrue(self.game.resolve_pending_choice(["use"]))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIn(law, self.player1.trash)
        self.assertTrue(law_target.is_resting)

        doflamingo = make_card("OP05-028", "Donquixote Doflamingo", card_type="CHARACTER", cost=3, power=5000)
        ko_target = make_card("ko-target", "KO Target", card_type="CHARACTER", cost=3, power=4000)
        ko_target.cost_modifier = -1
        ko_target.is_resting = True
        self.player1.cards_in_play = [doflamingo]
        self.player2.cards_in_play = [ko_target]
        self.assertTrue(op05_028_doflamingo(self.game, self.player1, doflamingo))
        self.assertTrue(self.game.resolve_pending_choice(["use"]))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIn(doflamingo, self.player1.trash)
        self.assertIn(ko_target, self.player2.trash)

        buffalo = make_card("OP05-031", "Buffalo", card_type="CHARACTER", cost=2, power=4000)
        rested_cost_one = make_card("rested-1", "Rested One", card_type="CHARACTER", cost=1, power=1000)
        rested_cost_two = make_card("rested-2", "Rested Two", card_type="CHARACTER", cost=2, power=3000)
        rested_cost_one.is_resting = True
        rested_cost_two.is_resting = True
        self.player1.cards_in_play = [buffalo, rested_cost_one, rested_cost_two]
        self.assertTrue(op05_031_buffalo(self.game, self.player1, buffalo))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertFalse(rested_cost_one.is_resting)
        self.assertTrue(getattr(buffalo, "op05_031_used", False))

        buffalo_no_target = make_card("OP05-031", "Buffalo", card_type="CHARACTER", cost=2, power=4000)
        rested_a = make_card("rested-a", "Rested A", card_type="CHARACTER", cost=2, power=3000)
        rested_b = make_card("rested-b", "Rested B", card_type="CHARACTER", cost=3, power=3000)
        rested_a.is_resting = True
        rested_b.is_resting = True
        self.player1.cards_in_play = [buffalo_no_target, rested_a, rested_b]
        self.game.pending_choice = None
        self.assertTrue(op05_031_buffalo(self.game, self.player1, buffalo_no_target))
        self.assertIsNone(self.game.pending_choice)
        self.assertFalse(getattr(buffalo_no_target, "op05_031_used", False))

        monet = make_card("OP05-036", "Monet", card_type="CHARACTER", cost=4, power=5000)
        monet_target = make_card("monet-target", "Monet Target", card_type="CHARACTER", cost=5, power=4000)
        monet_target.cost_modifier = -1
        self.player2.cards_in_play = [monet_target]
        self.assertTrue(op05_036_monet_block(self.game, self.player1, monet))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertTrue(monet_target.is_resting)

        event = make_card("OP05-076", "When You're at Sea You Fight against Pirates!!", card_type="EVENT", cost=1)
        search_target = make_card("sea-target", "Sea Target", card_type="CHARACTER", cost=3, power=4000)
        search_target.card_origin = "Heart Pirates"
        sea_fill_one = make_card("sea-fill-one", "Sea Fill One", card_type="CHARACTER", cost=2)
        sea_fill_two = make_card("sea-fill-two", "Sea Fill Two", card_type="CHARACTER", cost=1)
        sea_tail = make_card("sea-tail", "Sea Tail", card_type="CHARACTER", cost=5)
        self.player1.hand = []
        self.player1.deck = [search_target, sea_fill_one, sea_fill_two, sea_tail]
        self.assertTrue(has_hardcoded_effect("OP05-076", "main"))
        self.assertFalse(has_hardcoded_effect("OP05-076", "on_play"))
        self.assertTrue(op05_076_when_youre_at_sea(self.game, self.player1, event))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        while self.game.pending_choice is not None:
            self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIn(search_target, self.player1.hand)

        trigger_target = make_card("trigger-sea-target", "Trigger Sea Target", card_type="CHARACTER", cost=4, power=5000)
        trigger_target.card_origin = "Kid Pirates"
        trigger_fill_one = make_card("trigger-fill-one", "Trigger Fill One", card_type="CHARACTER", cost=2)
        trigger_fill_two = make_card("trigger-fill-two", "Trigger Fill Two", card_type="CHARACTER", cost=1)
        self.player1.hand = []
        self.player1.deck = [trigger_target, trigger_fill_one, trigger_fill_two]
        self.assertTrue(op05_076_when_youre_at_sea_trigger(self.game, self.player1, event))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        while self.game.pending_choice is not None:
            self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIn(trigger_target, self.player1.hand)

    def test_op05_029_doflamingo_prompts_optional_don_then_rests_target(self) -> None:
        doffy = make_card("OP05-029", "Donquixote Doflamingo", card_type="CHARACTER", power=5000)
        target = make_card("opp-target", "Opp Target", card_type="CHARACTER", cost=6, power=5000)
        self.player1.don_pool = ["active"]
        self.player2.cards_in_play = [target]

        self.assertTrue(op05_029_doflamingo(self.game, self.player1, doffy))
        self.assertTrue(self.game.resolve_pending_choice(["use"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertTrue(target.is_resting)
        self.assertEqual(["rested"], self.player1.don_pool)
        self.assertTrue(getattr(doffy, "op05_029_used", False))

    def test_op05_032_pica_end_of_turn_and_ko_protection_prompt(self) -> None:
        pica = make_card("OP05-032", "Pica", card_type="CHARACTER", cost=5, power=6000)
        pica.is_resting = True
        self.player1.don_pool = ["active"]

        self.assertTrue(op05_032_pica_eot(self.game, self.player1, pica))
        self.assertTrue(self.game.resolve_pending_choice(["use"]))
        self.assertFalse(pica.is_resting)
        self.assertEqual(["rested"], self.player1.don_pool)

        ally = make_card("pica-ally", "Pica Ally", card_type="CHARACTER", cost=3, power=4000)
        self.player1.cards_in_play = [pica, ally]
        self.game.current_player = self.player2
        self.game.opponent_player = self.player1

        self.assertEqual("pending", self.game._attempt_character_ko(pica, by_effect=True, controller=self.player2))
        self.assertTrue(self.game.resolve_pending_choice(["use"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertIn(pica, self.player1.cards_in_play)
        self.assertTrue(ally.is_resting)
        self.assertTrue(getattr(pica, "op05_032_ko_used", False))

    def test_op05_033_baby5_prompts_optional_cost_and_plays_target(self) -> None:
        baby5 = make_card("OP05-033", "Baby 5", card_type="CHARACTER", cost=2, power=2000)
        target = make_card("donquixote-target", "Target", card_type="CHARACTER", cost=2, power=3000)
        target.card_origin = "Donquixote Pirates"
        self.player1.don_pool = ["active"]
        self.player1.hand = [target]

        self.assertTrue(op05_033_baby5(self.game, self.player1, baby5))
        self.assertTrue(self.game.resolve_pending_choice(["use"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertTrue(baby5.is_resting)
        self.assertEqual(["rested"], self.player1.don_pool)
        self.assertIn(target, self.player1.cards_in_play)

    def test_op05_034_baby5_prompts_optional_cost_and_searches(self) -> None:
        baby5 = make_card("OP05-034", "Baby 5", card_type="CHARACTER", cost=2, power=2000)
        target = make_card("search-target", "Search Target", card_type="CHARACTER", cost=4, power=5000)
        target.card_origin = "Donquixote Pirates"
        filler = [make_card(f"fill-b5-{i}", f"Fill B5 {i}", card_type="CHARACTER", cost=1) for i in range(4)]
        self.player1.don_pool = ["active"]
        self.player1.deck = [target, *filler]

        self.assertTrue(op05_034_baby5(self.game, self.player1, baby5))
        self.assertTrue(self.game.resolve_pending_choice(["use"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        while self.game.pending_choice is not None:
            self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertTrue(baby5.is_resting)
        self.assertEqual(["rested"], self.player1.don_pool)
        self.assertIn(target, self.player1.hand)

    def test_op05_037_counter_and_trigger(self) -> None:
        event = make_card("OP05-037", "Because the Side of Justice Will Be Whichever Side Wins!!", card_type="EVENT", cost=1)
        own = make_card("own-counter", "Own Counter", card_type="CHARACTER", power=4000)
        discard = make_card("discard-counter", "Discard Counter", card_type="CHARACTER", power=1000)
        target = make_card("opp-rest", "Opp Rest", card_type="CHARACTER", cost=4, power=3000)
        self.player1.cards_in_play = [own]
        self.player1.hand = [discard]
        self.player2.cards_in_play = [target]

        self.assertTrue(op05_037_because_justice(self.game, self.player1, event))
        self.assertTrue(self.game.resolve_pending_choice(["pay"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["1"]))

        self.assertEqual(3000, getattr(own, "_battle_power_modifier", 0))
        self.assertIn(discard, self.player1.trash)

        self.assertTrue(op05_037_because_justice_trigger(self.game, self.player1, event))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertTrue(target.is_resting)

    def test_op05_038_counter_and_trigger(self) -> None:
        event = make_card("OP05-038", "Charlestone", card_type="EVENT", cost=1)
        own = make_card("own-charlestone", "Own Charlestone", card_type="CHARACTER", power=4000)
        discard = make_card("discard-charlestone", "Discard Charlestone", card_type="CHARACTER", power=1000)
        self.player1.cards_in_play = [own]
        self.player1.hand = [discard]
        self.player1.don_pool = ["rested", "rested", "rested", "active"]

        self.assertTrue(op05_038_charlestone(self.game, self.player1, event))
        self.assertTrue(self.game.resolve_pending_choice(["1"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["pay"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertEqual(4000, getattr(own, "_battle_power_modifier", 0))
        self.assertEqual(4, self.player1.don_pool.count("active"))

        opp_leader = self.player2.leader
        self.assertTrue(op05_038_charlestone_trigger(self.game, self.player1, event))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertTrue(opp_leader.is_resting)

    def test_op05_039_counter_and_trigger(self) -> None:
        event = make_card("OP05-039", "Stick-Stickem Meteora", card_type="EVENT", cost=1)
        own = make_card("own-meteora", "Own Meteora", card_type="CHARACTER", power=4000)
        target = make_card("opp-meteora", "Opp Meteora", card_type="CHARACTER", cost=3, power=3000)
        trigger_target = make_card("opp-trigger-meteora", "Opp Trigger Meteora", card_type="CHARACTER", cost=5, power=4000)
        target.is_resting = True
        trigger_target.is_resting = True
        self.player1.cards_in_play = [own]
        self.player2.cards_in_play = [target]

        self.assertTrue(op05_039_stick_stickem_meteora(self.game, self.player1, event))
        self.assertTrue(self.game.resolve_pending_choice(["1"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertEqual(4000, getattr(own, "_battle_power_modifier", 0))
        self.assertNotIn(target, self.player2.cards_in_play)

        self.player2.cards_in_play = [trigger_target]
        self.assertTrue(op05_039_stick_stickem_meteora_trigger(self.game, self.player1, event))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertNotIn(trigger_target, self.player2.cards_in_play)

    def test_op05_040_birdcage_continuous_and_end_of_turn_ko(self) -> None:
        stage = make_card("OP05-040", "Birdcage", card_type="STAGE", cost=3)
        self.player1.leader.name = "Donquixote Doflamingo"
        low_own = make_card("bird-own", "Bird Own", card_type="CHARACTER", cost=5, power=5000)
        low_opp = make_card("bird-opp", "Bird Opp", card_type="CHARACTER", cost=5, power=5000)
        high_opp = make_card("bird-high", "Bird High", card_type="CHARACTER", cost=6, power=6000)
        low_own.is_resting = True
        low_opp.is_resting = True
        high_opp.is_resting = True
        self.player1.cards_in_play = [stage, low_own]
        self.player2.cards_in_play = [low_opp, high_opp]

        self.assertTrue(op05_040_birdcage_continuous(self.game, self.player1, stage))
        self.assertTrue(getattr(low_own, "birdcage_lock", False))
        self.assertTrue(getattr(low_opp, "birdcage_lock", False))
        self.assertFalse(getattr(high_opp, "birdcage_lock", False))

        self.player2.reset_for_new_turn()
        self.assertTrue(low_opp.is_resting)
        self.assertFalse(high_opp.is_resting)

        pica = make_card("OP05-032", "Pica", card_type="CHARACTER", cost=5, power=6000)
        ally = make_card("bird-ally", "Bird Ally", card_type="CHARACTER", cost=3, power=4000)
        pica.is_resting = True
        low_opp.is_resting = True
        self.player1.cards_in_play = [stage, pica, ally]
        self.player2.cards_in_play = [low_opp]
        self.player1.don_pool = ["active"] * 10

        self.assertTrue(birdcage_effect(self.game, self.player1, stage))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["use"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertIn(pica, self.player1.cards_in_play)
        self.assertTrue(ally.is_resting)
        self.assertNotIn(low_opp, self.player2.cards_in_play)
        self.assertIn(stage, self.player1.trash)

    def test_op05_041_sakazuki_activate_and_attack(self) -> None:
        leader = self.player1.leader
        leader.id = "OP05-041"
        leader.name = "Sakazuki"
        discard = make_card("sak-discard", "Sak Discard", card_type="CHARACTER", cost=2, power=3000)
        draw_card = make_card("sak-draw", "Sak Draw", card_type="EVENT", cost=1, power=0)
        target = make_card("sak-target", "Sak Target", card_type="CHARACTER", cost=5, power=6000)
        self.player1.hand = [discard]
        self.player1.deck = [draw_card]
        self.player2.cards_in_play = [target]

        self.assertTrue(op05_041_sakazuki_activate(self.game, self.player1, leader))
        self.assertTrue(self.game.resolve_pending_choice(["use"]))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIn(discard, self.player1.trash)
        self.assertIn(draw_card, self.player1.hand)
        self.assertFalse(op05_041_sakazuki_activate(self.game, self.player1, leader))

        self.assertTrue(op05_041_sakazuki_attack(self.game, self.player1, leader))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertEqual(-1, getattr(target, "cost_modifier", 0))

    def test_op05_042_issho_applies_next_turn_attack_lock(self) -> None:
        card = make_card("OP05-042", "Issho", card_type="CHARACTER", cost=6, power=6000)
        target = make_card("issho-target", "Issho Target", card_type="CHARACTER", cost=7, power=7000)
        self.player2.cards_in_play = [target]

        self.assertTrue(op05_042_issho(self.game, self.player1, card))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertTrue(target.cannot_attack)
        self.assertEqual(self.game.turn_count + 1, getattr(target, "cannot_attack_until_turn", -1))

    def test_op05_043_ulti_prompts_add_and_top_bottom_order(self) -> None:
        ulti = make_card("OP05-043", "Ulti", card_type="CHARACTER", cost=4, power=5000)
        self.player1.leader.colors = ["Blue", "Black"]
        card_a = make_card("ulti-a", "Ulti A", card_type="CHARACTER", cost=1, power=1000)
        card_b = make_card("ulti-b", "Ulti B", card_type="EVENT", cost=2, power=0)
        card_c = make_card("ulti-c", "Ulti C", card_type="CHARACTER", cost=3, power=3000)
        tail = make_card("ulti-tail", "Ulti Tail", card_type="CHARACTER", cost=4, power=4000)
        self.player1.deck = [card_a, card_b, card_c, tail]

        self.assertTrue(op05_043_ulti(self.game, self.player1, ulti))
        self.assertTrue(self.game.resolve_pending_choice(["1"]))
        self.assertIn(card_b, self.player1.hand)
        self.assertTrue(self.game.resolve_pending_choice(["1"]))
        self.assertTrue(self.game.resolve_pending_choice(["top"]))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertTrue(self.game.resolve_pending_choice(["bottom"]))
        self.assertEqual(card_c, self.player1.deck[0])
        self.assertEqual(tail, self.player1.deck[1])
        self.assertEqual(card_a, self.player1.deck[-1])

    def test_op05_045_stainless_prompts_optional_cost_and_targets_any_character(self) -> None:
        stainless = make_card("OP05-045", "Stainless", card_type="CHARACTER", cost=4, power=5000)
        discard = make_card("stainless-discard", "Stainless Discard", card_type="EVENT", cost=1, power=0)
        own_target = make_card("stainless-own", "Stainless Own", card_type="CHARACTER", cost=2, power=3000)
        opp_target = make_card("stainless-opp", "Stainless Opp", card_type="CHARACTER", cost=2, power=3000)
        self.player1.hand = [discard]
        self.player1.cards_in_play = [stainless, own_target]
        self.player2.cards_in_play = [opp_target]

        self.assertTrue(op05_045_stainless(self.game, self.player1, stainless))
        self.assertTrue(self.game.resolve_pending_choice(["use"]))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertTrue(stainless.is_resting)
        self.assertIn(discard, self.player1.trash)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertNotIn(own_target, self.player1.cards_in_play)
        self.assertEqual(own_target, self.player1.deck[-1])

    def test_op05_046_dalmatian_draws_then_bottom_decks_chosen_hand_card(self) -> None:
        dalmatian = make_card("OP05-046", "Dalmatian", card_type="CHARACTER", cost=4, power=5000)
        keep = make_card("dal-keep", "Dal Keep", card_type="CHARACTER", cost=2, power=2000)
        bottom = make_card("dal-bottom", "Dal Bottom", card_type="EVENT", cost=1, power=0)
        drawn = make_card("dal-drawn", "Dal Drawn", card_type="CHARACTER", cost=3, power=3000)
        self.player1.hand = [bottom, keep]
        self.player1.deck = [drawn]

        self.assertTrue(op05_046_dalmatian(self.game, self.player1, dalmatian))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIn(drawn, self.player1.hand)
        self.assertIn(keep, self.player1.hand)
        self.assertNotIn(bottom, self.player1.hand)
        self.assertEqual(bottom, self.player1.deck[-1])

    def test_op05_047_hawkins_draws_and_gains_battle_power(self) -> None:
        hawkins = make_card("OP05-047", "Basil Hawkins", card_type="CHARACTER", cost=4, power=5000)
        self.player1.hand = [make_card("h1", "H1"), make_card("h2", "H2"), make_card("h3", "H3")]
        drawn = make_card("hawkins-draw", "Hawkins Draw", card_type="EVENT", cost=1, power=0)
        self.player1.deck = [drawn]

        self.assertTrue(op05_047_hawkins_block(self.game, self.player1, hawkins))
        self.assertIn(drawn, self.player1.hand)
        self.assertEqual(1000, getattr(hawkins, "_battle_power_modifier", 0))

    def test_op05_048_bastille_can_bottom_deck_any_owner_character(self) -> None:
        bastille = make_card("OP05-048", "Bastille", card_type="CHARACTER", cost=5, power=6000)
        bastille.attached_don = 1
        own_target = make_card("bastille-own", "Bastille Own", card_type="CHARACTER", cost=2, power=3000)
        opp_target = make_card("bastille-opp", "Bastille Opp", card_type="CHARACTER", cost=2, power=3000)
        self.player1.cards_in_play = [own_target]
        self.player2.cards_in_play = [opp_target]

        self.assertTrue(op05_048_bastille(self.game, self.player1, bastille))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertNotIn(own_target, self.player1.cards_in_play)
        self.assertEqual(own_target, self.player1.deck[-1])

    def test_op05_049_haccha_can_return_any_owner_character(self) -> None:
        haccha = make_card("OP05-049", "Haccha", card_type="CHARACTER", cost=6, power=7000)
        haccha.attached_don = 1
        own_target = make_card("haccha-own", "Haccha Own", card_type="CHARACTER", cost=3, power=3000)
        opp_target = make_card("haccha-opp", "Haccha Opp", card_type="CHARACTER", cost=3, power=3000)
        self.player1.cards_in_play = [own_target]
        self.player2.cards_in_play = [opp_target]

        self.assertTrue(op05_049_haccha(self.game, self.player1, haccha))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertNotIn(own_target, self.player1.cards_in_play)
        self.assertIn(own_target, self.player1.hand)

    def test_op05_050_hina_draws_if_five_or_less_cards_in_hand(self) -> None:
        hina = make_card("OP05-050", "Hina", card_type="CHARACTER", cost=3, power=4000)
        self.player1.hand = [make_card(f"hina-{idx}", f"Hina {idx}") for idx in range(5)]
        drawn = make_card("hina-draw", "Hina Draw", card_type="EVENT", cost=1, power=0)
        self.player1.deck = [drawn]

        self.assertTrue(op05_050_hina(self.game, self.player1, hina))
        self.assertIn(drawn, self.player1.hand)

    def test_op05_051_borsalino_can_bottom_deck_any_owner_character(self) -> None:
        borsalino = make_card("OP05-051", "Borsalino", card_type="CHARACTER", cost=7, power=8000)
        own_target = make_card("bors-own", "Bors Own", card_type="CHARACTER", cost=4, power=4000)
        opp_target = make_card("bors-opp", "Bors Opp", card_type="CHARACTER", cost=4, power=4000)
        self.player1.cards_in_play = [own_target]
        self.player2.cards_in_play = [opp_target]

        self.assertTrue(op05_051_borsalino(self.game, self.player1, borsalino))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertNotIn(own_target, self.player1.cards_in_play)
        self.assertEqual(own_target, self.player1.deck[-1])

    def test_op05_052_maynard_sets_blocker_flag(self) -> None:
        maynard = make_card("OP05-052", "Maynard", card_type="CHARACTER", cost=2, power=2000)
        self.assertTrue(op05_052_maynard(self.game, self.player1, maynard))
        self.assertTrue(maynard.has_blocker)

    def test_op05_053_mozambia_triggers_once_per_turn_on_draw_outside_draw_phase(self) -> None:
        mozambia = make_card("OP05-053", "Mozambia", card_type="CHARACTER", cost=1, power=2000)
        first = make_card("moz-draw-1", "Moz Draw 1", card_type="EVENT", cost=1, power=0)
        second = make_card("moz-draw-2", "Moz Draw 2", card_type="EVENT", cost=1, power=0)
        self.player1.cards_in_play = [mozambia]
        self.player1.deck = [first, second]
        self.game.phase = GamePhase.MAIN

        draw_cards(self.player1, 1, game_state=self.game)
        self.assertEqual(2000, getattr(mozambia, "power_modifier", 0))
        self.assertTrue(getattr(mozambia, "op05_053_used", False))

        draw_cards(self.player1, 1, game_state=self.game)
        self.assertEqual(2000, getattr(mozambia, "power_modifier", 0))

    def test_op05_054_garp_draws_two_then_bottom_decks_two_in_order(self) -> None:
        garp = make_card("OP05-054", "Monkey.D.Garp", card_type="CHARACTER", cost=3, power=3000)
        hand_a = make_card("garp-a", "Garp A", card_type="CHARACTER", cost=1, power=1000)
        hand_b = make_card("garp-b", "Garp B", card_type="CHARACTER", cost=2, power=2000)
        draw_c = make_card("garp-c", "Garp C", card_type="EVENT", cost=3, power=0)
        draw_d = make_card("garp-d", "Garp D", card_type="CHARACTER", cost=4, power=4000)
        self.player1.hand = [hand_a, hand_b]
        self.player1.deck = [draw_c, draw_d]

        self.assertTrue(op05_054_garp(self.game, self.player1, garp))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertTrue(self.game.resolve_pending_choice(["2"]))
        self.assertIn(hand_b, self.player1.hand)
        self.assertIn(draw_c, self.player1.hand)
        self.assertNotIn(hand_a, self.player1.hand)
        self.assertNotIn(draw_d, self.player1.hand)
        self.assertEqual(draw_d, self.player1.deck[-2])
        self.assertEqual(hand_a, self.player1.deck[-1])

    def test_op05_055_drake_reorders_top_cards_top_or_bottom(self) -> None:
        drake = make_card("OP05-055", "X.Drake", card_type="CHARACTER", cost=5, power=6000)
        card_a = make_card("drake-a", "Drake A", card_type="CHARACTER", cost=1, power=1000)
        card_b = make_card("drake-b", "Drake B", card_type="CHARACTER", cost=2, power=2000)
        card_c = make_card("drake-c", "Drake C", card_type="EVENT", cost=3, power=0)
        tail = make_card("drake-tail", "Drake Tail", card_type="CHARACTER", cost=4, power=4000)
        self.player1.deck = [card_a, card_b, card_c, tail]

        self.assertTrue(op05_055_drake_play(self.game, self.player1, drake))
        self.assertTrue(self.game.resolve_pending_choice(["top"]))
        self.assertTrue(self.game.resolve_pending_choice(["1"]))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertEqual(card_b, self.player1.deck[0])
        self.assertEqual(card_a, self.player1.deck[1])
        self.assertEqual(card_c, self.player1.deck[2])
        self.assertEqual(tail, self.player1.deck[3])

    def test_op05_056_barrels_only_targets_other_characters_and_draws(self) -> None:
        barrels = make_card("OP05-056", "X.Barrels", card_type="CHARACTER", cost=2, power=2000)
        own_char = make_card("barrels-own", "Barrels Own", card_type="CHARACTER", cost=2, power=3000)
        own_stage = make_card("barrels-stage", "Barrels Stage", card_type="STAGE", cost=2, power=0)
        drawn = make_card("barrels-draw", "Barrels Draw", card_type="EVENT", cost=1, power=0)
        self.player1.cards_in_play = [barrels, own_char, own_stage]
        self.player1.deck = [drawn]

        self.assertTrue(op05_056_barrels(self.game, self.player1, barrels))
        self.assertEqual(1, len(self.game.pending_choice.options))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertNotIn(own_char, self.player1.cards_in_play)
        self.assertIn(own_stage, self.player1.cards_in_play)
        self.assertIn(drawn, self.player1.hand)

    def test_op05_057_hound_blaze_main_and_trigger(self) -> None:
        event = make_card("OP05-057", "Hound Blaze", card_type="EVENT", cost=2, power=0)
        own = make_card("hound-own", "Hound Own", card_type="CHARACTER", cost=4, power=5000)
        own_low = make_card("hound-low", "Hound Low", card_type="CHARACTER", cost=2, power=2000)
        opp_low = make_card("hound-opp-low", "Hound Opp Low", card_type="CHARACTER", cost=2, power=2000)
        trigger_target = make_card("hound-trigger", "Hound Trigger", card_type="CHARACTER", cost=3, power=3000)
        self.player1.cards_in_play = [own, own_low]
        self.player2.cards_in_play = [opp_low]

        self.assertTrue(op05_057_hound_blaze(self.game, self.player1, event))
        self.assertTrue(self.game.resolve_pending_choice(["1"]))
        self.assertEqual(3000, getattr(own, "power_modifier", 0))
        self.assertEqual(self.game.turn_count, getattr(own, "power_modifier_expires_on_turn", -1))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertNotIn(own_low, self.player1.cards_in_play)
        self.assertEqual(own_low, self.player1.deck[-1])

        self.player1.cards_in_play = [own]
        self.player2.cards_in_play = [trigger_target]
        self.assertTrue(op05_057_hound_blaze_trigger(self.game, self.player1, event))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertNotIn(trigger_target, self.player2.cards_in_play)
        self.assertIn(trigger_target, self.player2.hand)

    def test_op05_058_waste_of_human_life_main_and_trigger(self) -> None:
        event = make_card("OP05-058", "It's a Waste of Human Life!!", card_type="EVENT", cost=8, power=0)
        p1_low = make_card("waste-p1-low", "Waste P1 Low", card_type="CHARACTER", cost=3, power=3000)
        p1_high = make_card("waste-p1-high", "Waste P1 High", card_type="CHARACTER", cost=4, power=4000)
        p2_low = make_card("waste-p2-low", "Waste P2 Low", card_type="CHARACTER", cost=2, power=2000)
        p2_high = make_card("waste-p2-high", "Waste P2 High", card_type="CHARACTER", cost=4, power=4000)
        self.player1.cards_in_play = [p1_low, p1_high]
        self.player2.cards_in_play = [p2_low, p2_high]
        self.player1.hand = [make_card(f"waste-p1-{i}", f"Waste P1 {i}") for i in range(7)]
        self.player2.hand = [make_card(f"waste-p2-{i}", f"Waste P2 {i}") for i in range(6)]

        self.assertTrue(op05_058_waste_of_human_life(self.game, self.player1, event))
        self.assertNotIn(p1_low, self.player1.cards_in_play)
        self.assertNotIn(p2_low, self.player2.cards_in_play)
        self.assertIn(p1_high, self.player1.cards_in_play)
        self.assertIn(p2_high, self.player2.cards_in_play)
        self.assertTrue(self.game.resolve_pending_choice(["0", "1"]))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertEqual(5, len(self.player1.hand))
        self.assertEqual(5, len(self.player2.hand))

        trig_p1 = make_card("waste-trig-p1", "Waste Trigger P1", card_type="CHARACTER", cost=2, power=2000)
        trig_p2 = make_card("waste-trig-p2", "Waste Trigger P2", card_type="CHARACTER", cost=2, power=2000)
        self.player1.cards_in_play = [trig_p1]
        self.player2.cards_in_play = [trig_p2]
        self.assertTrue(op05_058_waste_of_human_life_trigger(self.game, self.player1, event))
        self.assertNotIn(trig_p1, self.player1.cards_in_play)
        self.assertNotIn(trig_p2, self.player2.cards_in_play)

    def test_op05_059_world_of_violence_main_and_trigger(self) -> None:
        event = make_card("OP05-059", "Let Us Begin the World of Violence!!!", card_type="EVENT", cost=5, power=0)
        self.player1.leader.colors = ["Blue", "Black"]
        draw_one = make_card("violence-draw-1", "Violence Draw 1", card_type="EVENT", cost=1, power=0)
        draw_two = make_card("violence-draw-2", "Violence Draw 2", card_type="EVENT", cost=1, power=0)
        draw_three = make_card("violence-draw-3", "Violence Draw 3", card_type="EVENT", cost=1, power=0)
        own_target = make_card("violence-own", "Violence Own", card_type="CHARACTER", cost=5, power=5000)
        self.player1.deck = [draw_one, draw_two, draw_three]
        self.player1.cards_in_play = [own_target]

        self.assertTrue(op05_059_world_of_violence(self.game, self.player1, event))
        self.assertIn(draw_one, self.player1.hand)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertNotIn(own_target, self.player1.cards_in_play)
        self.assertIn(own_target, self.player1.hand)

        self.assertTrue(op05_059_world_of_violence_trigger(self.game, self.player1, event))
        self.assertIn(draw_two, self.player1.hand)
        self.assertIn(draw_three, self.player1.hand)

    def test_op05_060_luffy_leader_prompts_and_adds_one_active_don(self) -> None:
        leader = self.player1.leader
        life_one = make_card("luffy-life-1", "Luffy Life 1", card_type="EVENT", cost=1, power=0)
        life_two = make_card("luffy-life-2", "Luffy Life 2", card_type="CHARACTER", cost=2, power=2000)
        self.player1.life_cards = [life_one, life_two]
        self.player1.don_pool = ["rested", "active", "rested"]

        self.assertTrue(op05_060_luffy_leader(self.game, self.player1, leader))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["use"]))
        self.assertIn(life_two, self.player1.hand)
        self.assertEqual([life_one], self.player1.life_cards)
        self.assertEqual(4, len(self.player1.don_pool))
        self.assertEqual("active", self.player1.don_pool[-1])
        self.assertTrue(getattr(leader, "op05_060_used", False))
        self.assertFalse(op05_060_luffy_leader(self.game, self.player1, leader))

    def test_op05_061_usohachi_prompts_up_to_one_cost_four_or_less(self) -> None:
        usohachi = make_card("OP05-061", "Uso-Hachi", card_type="CHARACTER", cost=3, power=4000)
        target = make_card("usohachi-target", "Uso-Hachi Target", card_type="CHARACTER", cost=4, power=5000)
        too_large = make_card("usohachi-large", "Uso-Hachi Large", card_type="CHARACTER", cost=5, power=6000)
        usohachi.attached_don = 1
        self.player1.don_pool = ["active"] * 8
        self.player2.cards_in_play = [target, too_large]

        self.assertTrue(op05_061_usohachi(self.game, self.player1, usohachi))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertEqual(0, self.game.pending_choice.min_selections)
        self.assertEqual(1, len(self.game.pending_choice.options))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertTrue(target.is_resting)
        self.assertFalse(too_large.is_resting)

    def test_op05_062_onami_gains_blocker_only_at_ten_don(self) -> None:
        onami = make_card("OP05-062", "O-Nami", card_type="CHARACTER", cost=1, power=1000)
        self.player1.don_pool = ["active"] * 9

        self.assertTrue(op05_062_onami(self.game, self.player1, onami))
        self.assertFalse(onami.has_blocker)
        self.assertFalse(getattr(onami, "_continuous_blocker", False))

        self.player1.don_pool = ["active"] * 10
        self.assertTrue(op05_062_onami(self.game, self.player1, onami))
        self.assertTrue(onami.has_blocker)
        self.assertTrue(getattr(onami, "_continuous_blocker", False))

    def test_op05_063_orobi_prompts_optional_ko_for_cost_three_or_less(self) -> None:
        orobi = make_card("OP05-063", "O-Robi", card_type="CHARACTER", cost=4, power=5000)
        target = make_card("orobi-target", "O-Robi Target", card_type="CHARACTER", cost=3, power=3000)
        too_large = make_card("orobi-large", "O-Robi Large", card_type="CHARACTER", cost=4, power=4000)
        self.player1.don_pool = ["active"] * 8
        self.player2.cards_in_play = [target, too_large]

        self.assertTrue(op05_063_orobi(self.game, self.player1, orobi))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertEqual(0, self.game.pending_choice.min_selections)
        self.assertEqual(1, len(self.game.pending_choice.options))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertNotIn(target, self.player2.cards_in_play)
        self.assertIn(target, self.player2.trash)
        self.assertIn(too_large, self.player2.cards_in_play)

    def test_op05_064_killer_searches_top_five_and_bottom_decks_rest_in_order(self) -> None:
        killer = make_card("OP05-064", "Killer", card_type="CHARACTER", cost=1, power=2000)
        junk = make_card("killer-junk", "Killer Junk", card_type="EVENT", cost=1, power=0)
        kid_target = make_card("killer-kid", "Kid Target", card_type="CHARACTER", cost=2, power=3000)
        kid_target.card_origin = "Kid Pirates"
        same_name = make_card("killer-copy", "Killer", card_type="CHARACTER", cost=1, power=2000)
        same_name.card_origin = "Kid Pirates"
        tail = make_card("killer-tail", "Killer Tail", card_type="CHARACTER", cost=3, power=4000)
        self.player1.deck = [junk, kid_target, same_name, tail]

        self.assertTrue(op05_064_killer(self.game, self.player1, killer))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["1"]))
        self.assertIn(kid_target, self.player1.hand)
        self.assertTrue(self.game.resolve_pending_choice(["2"]))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertEqual([tail, junk, same_name], self.player1.deck)

    def test_op05_066_jinbe_only_gains_opponent_turn_power_at_ten_don(self) -> None:
        jinbe = make_card("OP05-066", "Jinbe", card_type="CHARACTER", cost=5, power=6000)
        jinbe._sticky_power_modifier = 500

        self.player1.don_pool = ["active"] * 10
        self.game.current_player = self.player1
        self.assertTrue(op05_066_jinbe_continuous(self.game, self.player1, jinbe))
        self.assertEqual(500, getattr(jinbe, "power_modifier", 0))

        self.game.current_player = self.player2
        self.assertTrue(op05_066_jinbe_continuous(self.game, self.player1, jinbe))
        self.assertEqual(1500, getattr(jinbe, "power_modifier", 0))

        self.player1.don_pool = ["active"] * 9
        self.assertTrue(op05_066_jinbe_continuous(self.game, self.player1, jinbe))
        self.assertEqual(500, getattr(jinbe, "power_modifier", 0))

    def test_op05_067_zorojuurou_adds_one_active_don_at_three_life_or_less(self) -> None:
        zoro = make_card("OP05-067", "Zoro-Juurou", card_type="CHARACTER", cost=3, power=4000)
        self.player1.life_cards = [
            make_card("zoro-life-1", "Zoro Life 1", card_type="EVENT", cost=1, power=0),
            make_card("zoro-life-2", "Zoro Life 2", card_type="EVENT", cost=1, power=0),
            make_card("zoro-life-3", "Zoro Life 3", card_type="EVENT", cost=1, power=0),
        ]
        self.player1.don_pool = ["rested", "active"]

        self.assertTrue(op05_067_zorojuurou(self.game, self.player1, zoro))
        self.assertEqual(3, len(self.player1.don_pool))
        self.assertEqual("active", self.player1.don_pool[-1])

    def test_op05_068_chopaemon_prompts_optional_restand_for_valid_targets(self) -> None:
        chopa = make_card("OP05-068", "Chopa-Emon", card_type="CHARACTER", cost=2, power=3000)
        valid = make_card("chopa-valid", "Chopa Valid", card_type="CHARACTER", cost=4, power=6000)
        valid.colors = ["Purple"]
        valid.card_origin = "Straw Hat Crew"
        valid.is_resting = True
        wrong_color = make_card("chopa-color", "Chopa Color", card_type="CHARACTER", cost=4, power=6000)
        wrong_color.colors = ["Blue"]
        wrong_color.card_origin = "Straw Hat Crew"
        wrong_color.is_resting = True
        too_big = make_card("chopa-big", "Chopa Big", card_type="CHARACTER", cost=4, power=7000)
        too_big.colors = ["Purple"]
        too_big.card_origin = "Straw Hat Crew"
        too_big.is_resting = True
        self.player1.cards_in_play = [chopa, valid, wrong_color, too_big]
        self.player1.don_pool = ["active"] * 8

        self.assertTrue(op05_068_chopaemon(self.game, self.player1, chopa))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertEqual(0, self.game.pending_choice.min_selections)
        self.assertEqual(1, len(self.game.pending_choice.options))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertFalse(valid.is_resting)
        self.assertTrue(wrong_color.is_resting)
        self.assertTrue(too_big.is_resting)

    def test_op05_069_law_searches_top_five_for_heart_pirates(self) -> None:
        law = make_card("OP05-069", "Trafalgar Law", card_type="CHARACTER", cost=3, power=5000)
        junk = make_card("law-junk", "Law Junk", card_type="EVENT", cost=1, power=0)
        heart_target = make_card("law-heart", "Law Heart", card_type="CHARACTER", cost=2, power=2000)
        heart_target.card_origin = "Heart Pirates"
        off_type = make_card("law-off", "Law Off", card_type="CHARACTER", cost=2, power=2000)
        off_type.card_origin = "Test"
        tail = make_card("law-tail", "Law Tail", card_type="CHARACTER", cost=4, power=4000)
        self.player1.deck = [junk, heart_target, off_type, tail]
        self.player1.don_pool = ["active"] * 2
        self.player2.don_pool = ["active"] * 3

        self.assertTrue(op05_069_law(self.game, self.player1, law))
        self.assertTrue(self.game.resolve_pending_choice(["1"]))
        self.assertIn(heart_target, self.player1.hand)
        self.assertTrue(self.game.resolve_pending_choice(["2"]))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertEqual([tail, junk, off_type], self.player1.deck)

    def test_op05_070_franosuke_gains_and_loses_rush_with_condition(self) -> None:
        franosuke = make_card("OP05-070", "Fra-Nosuke", card_type="CHARACTER", cost=5, power=4000)

        franosuke.attached_don = 1
        self.player1.don_pool = ["active"] * 8
        self.assertTrue(op05_070_franosuke(self.game, self.player1, franosuke))
        self.assertTrue(franosuke.has_rush)

        self.player1.don_pool = ["active"] * 7
        self.assertTrue(op05_070_franosuke(self.game, self.player1, franosuke))
        self.assertFalse(franosuke.has_rush)

    def test_op05_071_bepo_applies_turn_limited_optional_minus_two_thousand(self) -> None:
        bepo = make_card("OP05-071", "Bepo", card_type="CHARACTER", cost=3, power=5000)
        target = make_card("bepo-target", "Bepo Target", card_type="CHARACTER", cost=4, power=6000)
        self.player1.don_pool = ["active"] * 2
        self.player2.don_pool = ["active"] * 4
        self.player2.cards_in_play = [target]

        self.assertTrue(op05_071_bepo(self.game, self.player1, bepo))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertEqual(0, self.game.pending_choice.min_selections)
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertEqual(-2000, getattr(target, "power_modifier", 0))
        self.assertEqual(self.game.turn_count, getattr(target, "power_modifier_expires_on_turn", -1))

    def test_op05_072_honekichi_prompts_up_to_two_targets(self) -> None:
        honekichi = make_card("OP05-072", "Hone-Kichi", card_type="CHARACTER", cost=4, power=6000)
        target_one = make_card("hk-1", "HK One", card_type="CHARACTER", cost=3, power=5000)
        target_two = make_card("hk-2", "HK Two", card_type="CHARACTER", cost=4, power=6000)
        self.player1.don_pool = ["active"] * 8
        self.player2.cards_in_play = [target_one, target_two]

        self.assertTrue(op05_072_honekichi(self.game, self.player1, honekichi))
        self.assertTrue(self.game.resolve_pending_choice(["0", "1"]))

        self.assertEqual(-2000, getattr(target_one, "power_modifier", 0))
        self.assertEqual(-2000, getattr(target_two, "power_modifier", 0))

    def test_op05_073_doublefinger_on_play_and_trigger(self) -> None:
        doublefinger = make_card("OP05-073", "Miss Doublefinger(Zala)", card_type="CHARACTER", cost=4, power=4000)
        discard = make_card("df-discard", "Discard", card_type="CHARACTER", cost=1)
        self.player1.hand = [discard]
        self.player1.don_pool = ["active"]

        self.assertTrue(op05_073_doublefinger_play(self.game, self.player1, doublefinger))
        self.assertTrue(self.game.resolve_pending_choice(["use"]))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIn(discard, self.player1.trash)
        self.assertIn("rested", self.player1.don_pool)

        self.player1.cards_in_play = []
        self.player1.don_pool = ["active", "rested"]
        self.assertTrue(op05_073_doublefinger_trigger(self.game, self.player1, doublefinger))
        if self.game.pending_choice is not None:
            self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIn(doublefinger, self.player1.cards_in_play)

    def test_op05_074_and_075_don_return_and_play_prompt(self) -> None:
        kid = make_card("OP05-074", 'Eustass"Captain"Kid', card_type="CHARACTER", cost=5, power=6000)
        mr1 = make_card("OP05-075", "Mr.1(Daz.Bonez)", card_type="CHARACTER", cost=1, power=1000)
        baroque = make_card("bw-1", "Baroque", card_type="CHARACTER", cost=3, power=4000)
        baroque.card_origin = "Baroque Works"
        self.player1.hand = [baroque]
        self.player1.don_pool = ["active", "active"]
        self.game.current_player = self.player2
        self.game.opponent_player = self.player1

        self.assertTrue(op05_075_mr1(self.game, self.player1, mr1))
        self.assertTrue(self.game.resolve_pending_choice(["use"]))
        while self.game.pending_choice is not None:
            self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIn(baroque, self.player1.cards_in_play)

        self.game.current_player = self.player1
        self.game.opponent_player = self.player2
        before = len(self.player1.don_pool)
        self.assertTrue(op05_074_kid_don_return(self.game, self.player1, kid))
        self.assertGreaterEqual(len(self.player1.don_pool), before)

    def test_op05_077_and_078_apply_turn_limited_power_changes(self) -> None:
        gamma = make_card("OP05-077", "Gamma Knife", card_type="EVENT", cost=2)
        rotten = make_card("OP05-078", "Punk Rotten", card_type="EVENT", cost=2)
        opp_target = make_card("gamma-target", "Gamma Target", card_type="CHARACTER", cost=5, power=7000)
        kid_target = make_card("kid-target", "Kid Target", card_type="CHARACTER", cost=5, power=6000)
        kid_target.card_origin = "Kid Pirates"
        self.player1.don_pool = ["active", "active"]
        self.player2.cards_in_play = [opp_target]
        self.player1.cards_in_play = [kid_target]

        self.assertTrue(op05_077_gamma_knife(self.game, self.player1, gamma))
        while self.game.pending_choice is not None:
            self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertEqual(-5000, getattr(opp_target, "power_modifier", 0))

        self.player1.don_pool = ["active", "active"]
        self.assertTrue(op05_078_punk_rotten(self.game, self.player1, rotten))
        while self.game.pending_choice is not None:
            self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertEqual(5000, getattr(kid_target, "power_modifier", 0))

    def test_op05_079_and_082_bottom_trash_effects_chain_correctly(self) -> None:
        viola = make_card("OP05-079", "Viola", card_type="CHARACTER", cost=2, power=3000)
        shirahoshi = make_card("OP05-082", "Shirahoshi", card_type="CHARACTER", cost=1, power=0)
        opp_t1 = make_card("opp-t1", "Opp T1", cost=1)
        opp_t2 = make_card("opp-t2", "Opp T2", cost=1)
        opp_t3 = make_card("opp-t3", "Opp T3", cost=1)
        self.player2.trash = [opp_t1, opp_t2, opp_t3]

        self.assertTrue(op05_079_viola(self.game, self.player1, viola))
        while self.game.pending_choice is not None:
            self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertEqual([], self.player2.trash)
        self.assertEqual(["opp-t3", "opp-t2", "opp-t1"], [card.id for card in self.player2.deck[-3:]])

        own_t1 = make_card("own-t1", "Own T1", cost=1)
        own_t2 = make_card("own-t2", "Own T2", cost=1)
        discard_target = make_card("opp-hand", "Opp Hand", cost=1)
        self.player1.trash = [own_t1, own_t2]
        self.player2.hand = [discard_target] + [make_card(f"opp-h{idx}", f"Opp H{idx}", cost=1) for idx in range(5)]
        self.assertTrue(op05_082_shirahoshi(self.game, self.player1, shirahoshi))
        self.assertTrue(self.game.resolve_pending_choice(["use"]))
        while self.game.pending_choice is not None:
            self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertEqual(5, len(self.player2.hand))

    def test_op05_080_elizabello_and_090_riku_apply_battle_and_turn_power(self) -> None:
        elizabello = make_card("OP05-080", "Elizabello II", card_type="CHARACTER", cost=4, power=5000)
        riku = make_card("OP05-090", "Riku Doldo III", card_type="CHARACTER", cost=4, power=5000)
        dressrosa = make_card("dressrosa", "Dressrosa", card_type="CHARACTER", cost=3, power=4000)
        dressrosa.card_origin = "Dressrosa"
        self.player1.trash = [make_card(f"trash-{idx}", f"Trash {idx}", cost=1) for idx in range(20)]
        self.player1.cards_in_play = [dressrosa]

        self.assertTrue(op05_080_elizabello(self.game, self.player1, elizabello))
        self.assertTrue(self.game.resolve_pending_choice(["use"]))
        self.assertTrue(getattr(elizabello, "has_doubleattack", False))
        self.assertEqual(10000, getattr(elizabello, "_battle_power_modifier", 0))

        self.assertTrue(op05_090_riku_play(self.game, self.player1, riku))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertEqual(2000, getattr(dressrosa, "power_modifier", 0))

        dressrosa.power_modifier = 0
        self.assertTrue(op05_090_riku_ko(self.game, self.player1, riku))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertEqual(2000, getattr(dressrosa, "power_modifier", 0))

    def test_op05_091_rebecca_and_093_lucci_chain_their_followups(self) -> None:
        rebecca = make_card("OP05-091", "Rebecca", card_type="CHARACTER", cost=4, power=0)
        lucci = make_card("OP05-093", "Rob Lucci", card_type="CHARACTER", cost=4, power=6000)
        trash_target = make_card("reb-trash", "Trash Black", card_type="CHARACTER", cost=3, power=3000)
        hand_target = make_card("reb-hand", "Hand Black", card_type="CHARACTER", cost=2, power=2000)
        trash_target.colors = ["Black"]
        hand_target.colors = ["Black"]
        self.player1.trash = [trash_target] + [make_card(f"lucci-trash-{idx}", f"Lucci Trash {idx}", cost=1) for idx in range(3)]
        self.player1.hand = [hand_target]

        self.assertTrue(op05_091_rebecca_play(self.game, self.player1, rebecca))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertTrue(hand_target.is_resting)
        self.assertIn(hand_target, self.player1.cards_in_play)

        cost2 = make_card("cost2", "Cost 2", card_type="CHARACTER", cost=2, power=2000)
        cost1 = make_card("cost1", "Cost 1", card_type="CHARACTER", cost=1, power=1000)
        self.player2.cards_in_play = [cost2, cost1]

        self.assertTrue(op05_093_lucci(self.game, self.player1, lucci))
        self.assertTrue(self.game.resolve_pending_choice(["use"]))
        while self.game.pending_choice is not None:
            self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIn(cost2, self.player2.trash)
        self.assertIn(cost1, self.player2.trash)

    def test_op05_096_100_and_101_use_prompted_followups(self) -> None:
        five_hundred = make_card("OP05-096", "I Bid 500 Million!!", card_type="EVENT", cost=3)
        enel = make_card("OP05-100", "Enel", card_type="CHARACTER", cost=7, power=7000)
        ohm = make_card("OP05-101", "Ohm", card_type="CHARACTER", cost=4, power=5000)
        celestial = make_card("celestial", "Saint Charlos", card_type="CHARACTER", cost=3, power=0)
        celestial.card_origin = "Celestial Dragons"
        opp_target = make_card("opp-cost1", "Opp Cost1", card_type="CHARACTER", cost=1, power=2000)
        draw_card = make_card("draw-card", "Draw Card", card_type="CHARACTER", cost=1)
        holly = make_card("holly", "Holly", card_type="CHARACTER", cost=2, power=3000)
        self.player1.cards_in_play = [celestial]
        self.player1.deck = [draw_card, holly, make_card("ohm-2", "Ohm 2"), make_card("ohm-3", "Ohm 3"), make_card("ohm-4", "Ohm 4"), make_card("ohm-5", "Ohm 5")]
        self.player2.cards_in_play = [opp_target]

        self.assertTrue(op05_096_500_million(self.game, self.player1, five_hundred))
        self.assertTrue(self.game.resolve_pending_choice(["life_bottom"]))
        while self.game.pending_choice is not None:
            self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIs(opp_target, self.player2.life_cards[0])
        self.assertTrue(getattr(opp_target, "is_face_up", False))
        self.assertIn(draw_card, self.player1.hand)

        self.player1.life_cards = [make_card("life-1", "Life 1", cost=1)]
        self.assertTrue(op05_100_enel_protection(self.game, self.player1, enel))
        self.assertTrue(self.game.resolve_pending_choice(["use"]))
        self.assertEqual(1, len(self.player1.trash))

        self.player1.hand = []
        self.player1.deck = [holly, make_card("ohm-a", "Ohm A"), make_card("ohm-b", "Ohm B"), make_card("ohm-c", "Ohm C"), make_card("ohm-d", "Ohm D")]
        self.assertTrue(op05_101_ohm_play(self.game, self.player1, ohm))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        while self.game.pending_choice is not None:
            self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIn(holly, self.player1.cards_in_play)

    def test_op05_104_105_109_and_112_resolve_card_flow_prompts(self) -> None:
        conis = make_card("OP05-104", "Conis", card_type="CHARACTER", cost=1, power=0)
        satori = make_card("OP05-105", "Satori", card_type="CHARACTER", cost=5, power=5000)
        pagaya = make_card("OP05-109", "Pagaya", card_type="CHARACTER", cost=1, power=1000)
        mckinley = make_card("OP05-112", "Captain McKinley", card_type="CHARACTER", cost=3, power=3000)
        stage = make_card("stage", "Stage", card_type="STAGE", cost=1)
        hand_one = make_card("h1", "H1", cost=1)
        hand_two = make_card("h2", "H2", cost=1)
        sky = make_card("sky", "Sky", card_type="CHARACTER", cost=1, power=1000)
        sky.card_origin = "Sky Island"
        self.player1.stage = stage
        self.player1.hand = [hand_one, hand_two, sky]
        self.player1.deck = [make_card("draw-1", "Draw 1", cost=1), make_card("draw-2", "Draw 2", cost=1)]

        self.assertTrue(op05_104_conis(self.game, self.player1, conis))
        self.assertTrue(self.game.resolve_pending_choice(["use"]))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIsNone(self.player1.stage)

        self.player1.hand = [make_card("satori-cost", "Cost", cost=1)]
        self.assertTrue(op05_105_satori(self.game, self.player1, satori))
        self.assertTrue(self.game.resolve_pending_choice(["use"]))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIn(satori, self.player1.cards_in_play)

        self.player1.hand = [make_card("p1", "P1", cost=1), make_card("p2", "P2", cost=1)]
        self.player1.deck = [make_card("p3", "P3", cost=1), make_card("p4", "P4", cost=1)]
        self.assertTrue(op05_109_pagaya(self.game, self.player1, pagaya))
        self.assertIsNotNone(self.game.pending_choice)
        self.assertTrue(self.game.resolve_pending_choice(["0", "1"]))
        self.assertEqual(2, len(self.player1.trash))

        self.player1.hand = [sky]
        self.assertTrue(op05_112_mckinley_ko(self.game, self.player1, mckinley))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIn(sky, self.player1.cards_in_play)

    def test_op05_111_115_and_119_follow_ordered_resolution(self) -> None:
        hotori = make_card("OP05-111", "Hotori", card_type="CHARACTER", cost=3, power=3000)
        kotori = make_card("kotori", "Kotori", card_type="CHARACTER", cost=3, power=3000)
        amaru = make_card("OP05-115", "Two-Hundred Million Volts Amaru", card_type="EVENT", cost=2)
        luffy = make_card("OP05-119", "Monkey.D.Luffy", card_type="CHARACTER", cost=10, power=12000)
        opp_target = make_card("opp-low", "Opp Low", card_type="CHARACTER", cost=3, power=3000)
        extra_one = make_card("extra-1", "Extra 1", card_type="CHARACTER", cost=2, power=2000)
        extra_two = make_card("extra-2", "Extra 2", card_type="CHARACTER", cost=3, power=3000)
        self.player1.hand = [kotori, make_card("a1", "A1", cost=1), make_card("a2", "A2", cost=1)]
        self.player2.cards_in_play = [opp_target]

        self.assertTrue(op05_111_hotori(self.game, self.player1, hotori))
        self.assertTrue(self.game.resolve_pending_choice(["use"]))
        self.assertTrue(self.game.resolve_pending_choice(["bottom"]))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertIn(kotori, self.player1.cards_in_play)
        self.assertIs(opp_target, self.player2.life_cards[0])

        self.player1.deck = [make_card("life-add", "Life Add", cost=1)]
        self.assertTrue(op05_115_amaru_trigger(self.game, self.player1, amaru))
        self.assertTrue(self.game.resolve_pending_choice(["pay"]))
        self.assertTrue(self.game.resolve_pending_choice(["0", "1"]))
        self.assertEqual("life-add", self.player1.life_cards[-1].id)

        self.player1.cards_in_play = [luffy, extra_one, extra_two]
        self.player1.don_pool = ["active"] * 10
        self.assertTrue(op05_119_luffy_play(self.game, self.player1, luffy))
        self.assertTrue(self.game.resolve_pending_choice([str(i) for i in range(10)]))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))
        self.assertTrue(self.player1.extra_turn)
        self.assertNotIn(extra_one, self.player1.cards_in_play)
        self.assertNotIn(extra_two, self.player1.cards_in_play)


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
