import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from optcg_engine.effects.effect_registry import create_ko_choice, register_effect
from optcg_engine.effects.effects import Effect, EffectTiming, EffectType, TargetType
from optcg_engine.effects.resolver import EffectContext, get_resolver
from optcg_engine.effects.sets.op14_effects import op14_080_moria_leader
from optcg_engine.game_engine import GameState, PendingChoice, Player
from optcg_engine.models.cards import Card


def make_card(card_id, name, *, card_type="CHARACTER", cost=1, power=1000, effect="", card_origin="Test"):
    return Card(
        id=card_id,
        id_normal=card_id,
        name=name,
        card_type=card_type,
        cost=cost,
        power=power,
        counter=0,
        colors=["Black"],
        life=0,
        effect=effect,
        image_link="",
        attribute="Strike",
        card_origin=card_origin,
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


@register_effect("TEST-ON-KO", "on_ko", "Mark that this card's On K.O. resolved")
def _test_on_ko(game_state, player, card):
    card.test_on_ko_count = getattr(card, "test_on_ko_count", 0) + 1
    card.test_on_ko_player = player.name
    return True


class EffectKoOnKoTests(unittest.TestCase):
    def setUp(self):
        self.player1 = make_player("P1", "p1")
        self.player2 = make_player("P2", "p2")
        self.game = GameState(self.player1, self.player2)

    def test_create_ko_choice_triggers_on_ko_for_own_character(self):
        target = make_card("TEST-ON-KO", "Own On KO Target", cost=2)
        self.player1.cards_in_play = [target]

        self.assertTrue(create_ko_choice(self.game, self.player1, [target]))
        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertIn(target, self.player1.trash)
        self.assertNotIn(target, self.player1.cards_in_play)
        self.assertEqual(1, getattr(target, "test_on_ko_count", 0))
        self.assertEqual("P1", target.test_on_ko_player)

    def test_legacy_ko_target_dispatch_triggers_on_ko(self):
        target = make_card("TEST-ON-KO", "Legacy On KO Target", cost=2)
        self.player2.cards_in_play = [target]
        self.game.pending_choice = PendingChoice(
            choice_id="legacy-ko",
            choice_type="select_target",
            prompt="K.O. a character",
            options=[{"id": "0", "label": target.name, "card_id": target.id, "card_name": target.name}],
            callback_action="ko_target",
            callback_data={
                "player_index": 0,
                "target_cards": [{"id": target.id, "name": target.name, "unique_id": id(target)}],
            },
        )

        self.assertTrue(self.game.resolve_pending_choice(["0"]))

        self.assertIn(target, self.player2.trash)
        self.assertEqual(1, getattr(target, "test_on_ko_count", 0))
        self.assertEqual("P2", target.test_on_ko_player)

    def test_parser_ko_resolver_triggers_on_ko(self):
        source = make_card("source", "Source", cost=1)
        target = make_card("TEST-ON-KO", "Parser On KO Target", cost=2)
        self.player1.cards_in_play = [source, target]
        effect = Effect(
            effect_type=EffectType.KO,
            timing=EffectTiming.ON_PLAY,
            target_type=TargetType.YOUR_CHARACTER,
        )
        context = EffectContext(
            game_state=self.game,
            source_card=source,
            source_player=self.player1,
            opponent=self.player2,
            targets=[target],
        )

        result = get_resolver().resolve(effect, context, chosen_targets=[target])

        self.assertTrue(result.success)
        self.assertIn(target, self.player1.trash)
        self.assertEqual(1, getattr(target, "test_on_ko_count", 0))

    def test_op14_moria_thriller_bark_ko_triggers_on_ko(self):
        moria = make_card("OP14-080", "Gecko Moria", card_type="LEADER", cost=0, power=5000)
        target = make_card(
            "TEST-ON-KO",
            "Thriller Bark On KO Target",
            cost=2,
            card_origin="Thriller Bark Pirates",
        )
        ally = make_card("ally", "Ally", cost=3)
        self.player1.leader = moria
        self.player1.cards_in_play = [target, ally]

        self.assertTrue(op14_080_moria_leader(self.game, self.player1, moria))

        self.assertIn(target, self.player1.trash)
        self.assertEqual(1, getattr(target, "test_on_ko_count", 0))
        self.assertEqual(1000, getattr(moria, "power_modifier", 0))
        self.assertEqual(1000, getattr(ally, "power_modifier", 0))


if __name__ == "__main__":
    unittest.main()
