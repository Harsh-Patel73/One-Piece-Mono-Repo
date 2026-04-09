import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from optcg_engine.effects.hardcoded import filter_by_cost_range, filter_by_max_cost
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


if __name__ == "__main__":
    unittest.main()
