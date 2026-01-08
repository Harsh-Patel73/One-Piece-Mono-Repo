"""
Game session manager for Vinsmoke Engine.

Manages active games, handles game creation, and coordinates
between API requests and game state.
"""

import uuid
from datetime import datetime
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass, field
import asyncio

from pathlib import Path
from game_engine import GameState, Player
from models.cards import Card
from data.card_loader import load_card_database
from decks.deck_loader import load_deck


@dataclass
class GameSession:
    """Represents an active game session."""
    game_id: str
    game_state: GameState
    player1_type: str  # "HUMAN" or "AI"
    player2_type: str
    created_at: datetime
    last_activity: datetime
    auto_play: bool = False
    websocket_clients: List = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            "game_id": self.game_id,
            "player1_name": self.game_state.player1.name,
            "player2_name": self.game_state.player2.name,
            "turn": self.game_state.turn_count,
            "phase": self.game_state.phase.name,
            "is_terminal": self.game_state.game_over,
            "winner": self.game_state.winner.name if self.game_state.winner else None,
            "created_at": self.created_at.isoformat(),
        }


class GameManager:
    """
    Manages all active game sessions.

    Handles:
    - Game creation with different player types
    - Action processing
    - Game state serialization
    - WebSocket client management
    """

    def __init__(self):
        self.games: Dict[str, GameSession] = {}
        self.card_database: Dict[str, Card] = {}
        self._load_card_database()

    def _load_card_database(self):
        """Load the card database on initialization."""
        try:
            # Get path to card database
            db_path = Path(__file__).parent.parent / "data" / "english_cards.json"
            self.card_database = load_card_database(str(db_path))
            print(f"Loaded {len(self.card_database)} cards")
        except Exception as e:
            print(f"Warning: Could not load card database: {e}")
            self.card_database = {}

    def create_game(
        self,
        player1_name: str,
        player1_type: str,
        player1_deck_id: Optional[str],
        player2_name: str,
        player2_type: str,
        player2_deck_id: Optional[str],
        auto_play: bool = False,
    ) -> GameSession:
        """
        Create a new game session.

        Args:
            player1_name: Name for player 1
            player1_type: "HUMAN" or "AI"
            player1_deck_id: Deck ID for player 1
            player2_name: Name for player 2
            player2_type: "HUMAN" or "AI"
            player2_deck_id: Deck ID for player 2
            auto_play: If True, AI moves automatically

        Returns:
            New GameSession
        """
        game_id = str(uuid.uuid4())[:8]

        # Load decks
        p1_leader, p1_deck = self._load_deck(player1_deck_id or "red_luffy")
        p2_leader, p2_deck = self._load_deck(player2_deck_id or "green_yamato")

        # Create players
        player1 = Player(player1_name, p1_deck, p1_leader)
        player2 = Player(player2_name, p2_deck, p2_leader)

        # Create game state
        game_state = GameState(player1, player2)

        # Create session
        session = GameSession(
            game_id=game_id,
            game_state=game_state,
            player1_type=player1_type,
            player2_type=player2_type,
            created_at=datetime.now(),
            last_activity=datetime.now(),
            auto_play=auto_play,
        )

        self.games[game_id] = session
        print(f"Created game {game_id}: {player1_name} vs {player2_name}")

        return session

    def _load_deck(self, deck_id: str) -> Tuple[Card, List[Card]]:
        """Load a deck by ID."""
        try:
            # Construct the full path to the deck file
            deck_path = Path(__file__).parent.parent / "decks" / f"{deck_id}.json"
            # load_deck now returns (deck_cards, leader) with proper deep copies
            deck_cards, leader = load_deck(str(deck_path), self.card_database)

            if leader is None:
                raise ValueError(f"No leader found in deck {deck_id}")

            return leader, deck_cards
        except Exception as e:
            print(f"Error loading deck {deck_id}: {e}")
            # Return a default deck
            return self._get_default_deck()

    def _get_default_deck(self) -> Tuple[Card, List[Card]]:
        """Get a default deck if loading fails."""
        # Find any leader in the database
        leader = None
        cards = []

        for card_id, card in self.card_database.items():
            if card.card_type == 'LEADER' and leader is None:
                leader = card
            elif card.card_type == 'CHARACTER' and len(cards) < 50:
                cards.append(card)

        if leader is None:
            # Create a minimal card for testing
            leader = Card(
                id="TEST-001",
                id_normal="TEST-001",
                name="Test Leader",
                card_type="LEADER",
                cost=None,
                power=5000,
                counter=None,
                colors=["Red"],
                life=5,
                effect="",
                image_link=None,
                attribute=None,
                card_origin=None,
                trigger=None,
            )

        # Pad deck to 50 cards
        while len(cards) < 50:
            cards.append(cards[0] if cards else leader)

        return leader, cards

    def get_game(self, game_id: str) -> Optional[GameSession]:
        """Get a game session by ID."""
        return self.games.get(game_id)

    def get_all_games(self) -> List[GameSession]:
        """Get all active game sessions."""
        return list(self.games.values())

    def delete_game(self, game_id: str) -> bool:
        """Delete a game session."""
        if game_id in self.games:
            del self.games[game_id]
            return True
        return False

    def process_action(
        self,
        game_id: str,
        action_type: str,
        player_index: int,
        card_index: Optional[int] = None,
        target_index: Optional[int] = None,
        don_amount: Optional[int] = None,
        card_indices: Optional[List[int]] = None,
    ) -> Tuple[bool, str, List[str]]:
        """
        Process a player action.

        Returns:
            Tuple of (success, message, events)
        """
        session = self.get_game(game_id)
        if not session:
            return False, "Game not found", []

        game = session.game_state
        events = []

        # Validate it's the player's turn
        current_player_idx = 0 if game.current_player == game.player1 else 1
        if player_index != current_player_idx:
            return False, "Not your turn", []

        try:
            if action_type == "PASS_TURN":
                game.next_turn()
                events.append(f"Turn {game.turn_count}: {game.current_player.name}")

            elif action_type == "PLAY_CARD":
                if card_index is None:
                    return False, "Card index required", []
                if card_index >= len(game.current_player.hand):
                    return False, "Invalid card index", []

                card = game.current_player.hand[card_index]
                game.play_card(card)
                events.append(f"{game.current_player.name} plays {card.name}")

            elif action_type == "ATTACK":
                if card_index is None:
                    return False, "Attacker index required", []

                # -1 means leader attacks
                if card_index == -1:
                    attacker = game.current_player.leader
                else:
                    if card_index >= len(game.current_player.cards_in_play):
                        return False, "Invalid attacker index", []
                    attacker = game.current_player.cards_in_play[card_index]

                target_idx = target_index if target_index is not None else -1
                game.attack_with_card(attacker, target_idx)
                events.append(f"{attacker.name} attacks!")

            elif action_type == "ATTACH_DON":
                if card_index is None or don_amount is None:
                    return False, "Card index and DON amount required", []

                if card_index == -1:
                    card = game.current_player.leader
                else:
                    if card_index >= len(game.current_player.cards_in_play):
                        return False, "Invalid card index", []
                    card = game.current_player.cards_in_play[card_index]

                game.current_player.assign_don_to_card(card, don_amount)
                events.append(f"Attached {don_amount} DON to {card.name}")

            elif action_type == "USE_COUNTER":
                if card_index is None:
                    return False, "Counter card index required", []
                # Counter logic would go here
                events.append("Counter used")

            elif action_type == "ACTIVATE_BLOCKER":
                if card_index is None:
                    return False, "Blocker index required", []

                blocker = game.opponent_player.activate_blocker(card_index)
                if blocker:
                    events.append(f"{blocker.name} blocks!")
                else:
                    return False, "Invalid blocker", []

            elif action_type == "MULLIGAN":
                if card_indices is None:
                    return False, "Card indices required for mulligan", []
                game.current_player.mulligan(card_indices)
                events.append(f"Mulliganed {len(card_indices)} cards")

            elif action_type == "KEEP_HAND":
                events.append("Kept hand")

            elif action_type == "PASS":
                events.append("Passed")

            else:
                return False, f"Unknown action type: {action_type}", []

            session.last_activity = datetime.now()
            return True, "Action processed", events

        except Exception as e:
            return False, str(e), []

    def serialize_game_state(
        self,
        session: GameSession,
        for_player: Optional[int] = None
    ) -> dict:
        """
        Serialize game state for API response.

        Args:
            session: Game session
            for_player: If set, include hidden info only for this player

        Returns:
            Serialized game state dict
        """
        game = session.game_state

        def serialize_card(card: Card) -> dict:
            return {
                "id": card.id,
                "name": card.name,
                "card_type": card.card_type,
                "cost": card.cost,
                "power": card.power,
                "counter": card.counter,
                "colors": card.colors,
                "life": card.life,
                "effect": card.effect,
                "trigger": card.trigger,
                "image_link": card.image_link,
                "attribute": card.attribute,
                "card_origin": card.card_origin,
                "is_resting": getattr(card, 'is_resting', False),
                "has_attacked": getattr(card, 'has_attacked', False),
                "attached_don": getattr(card, 'attached_don', 0),
                "played_turn": getattr(card, 'played_turn', None),
            }

        def serialize_player(player: Player, idx: int, show_hidden: bool) -> dict:
            result = {
                "player_index": idx,
                "name": player.name,
                "leader": serialize_card(player.leader),
                "life_count": len(player.life_cards),
                "hand_count": len(player.hand),
                "deck_count": len(player.deck),
                "field": [serialize_card(c) for c in player.cards_in_play],
                "trash_count": len(player.trash),
                "don_active": player.don_pool.count("active"),
                "don_rested": player.don_pool.count("rested"),
                "total_don": len(player.don_pool),
            }

            if show_hidden:
                result["hand"] = [serialize_card(c) for c in player.hand]
                result["life_cards"] = [serialize_card(c) for c in player.life_cards]

            return result

        current_idx = 0 if game.current_player == game.player1 else 1

        return {
            "game_id": session.game_id,
            "turn": game.turn_count,
            "phase": game.phase.name,
            "active_player": current_idx,
            "players": [
                serialize_player(game.player1, 0, for_player == 0 or for_player is None),
                serialize_player(game.player2, 1, for_player == 1 or for_player is None),
            ],
            "is_terminal": game.game_over,
            "winner": (0 if game.winner == game.player1 else 1) if game.winner else None,
            "last_action": game.phase.name,
        }

    def get_valid_actions(self, game_id: str, player_index: int) -> List[dict]:
        """Get valid actions for a player."""
        session = self.get_game(game_id)
        if not session:
            return []

        game = session.game_state
        current_idx = 0 if game.current_player == game.player1 else 1

        if player_index != current_idx:
            return []  # Not this player's turn

        actions = []
        player = game.current_player

        # Pass turn is always valid in main phase
        if game.phase.name == "MAIN":
            actions.append({"action_type": "PASS_TURN", "player_index": player_index})

            # Play card actions
            char_count = sum(1 for c in player.cards_in_play if c.card_type == "CHARACTER")
            for i, card in enumerate(player.hand):
                cost = card.cost or 0
                if cost <= game.available_don():
                    # Check field limit for characters (max 5)
                    if card.card_type == "CHARACTER" and char_count >= 5:
                        continue
                    actions.append({
                        "action_type": "PLAY_CARD",
                        "player_index": player_index,
                        "card_index": i,
                    })

            # Attack actions
            if game.can_attack_with_leader() and not player.leader.is_resting:
                actions.append({
                    "action_type": "ATTACK",
                    "player_index": player_index,
                    "card_index": -1,  # Leader
                    "target_index": -1,  # Opponent leader
                })

            for i, card in enumerate(player.cards_in_play):
                if not card.is_resting and not card.has_attacked:
                    rush = getattr(card, 'has_rush', False)
                    played_turn = getattr(card, 'played_turn', None)
                    if rush or played_turn != game.turn_count:
                        actions.append({
                            "action_type": "ATTACK",
                            "player_index": player_index,
                            "card_index": i,
                            "target_index": -1,
                        })

            # Attach DON actions
            if player.available_don() > 0:
                actions.append({
                    "action_type": "ATTACH_DON",
                    "player_index": player_index,
                    "card_index": -1,  # Leader
                    "don_amount": 1,
                })
                for i in range(len(player.cards_in_play)):
                    actions.append({
                        "action_type": "ATTACH_DON",
                        "player_index": player_index,
                        "card_index": i,
                        "don_amount": 1,
                    })

        return actions


# Singleton instance
_game_manager: Optional[GameManager] = None


def get_game_manager() -> GameManager:
    """Get the singleton game manager instance."""
    global _game_manager
    if _game_manager is None:
        _game_manager = GameManager()
    return _game_manager
