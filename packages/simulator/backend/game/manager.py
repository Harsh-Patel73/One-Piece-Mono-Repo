"""
Game Manager - Handles all active games and rooms with actual game logic.
"""

from typing import Dict, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import time

from .engine import GameState, Player
from .card_loader import load_card_database
from .deck_loader import load_deck
from .models import Card


class GameMode(Enum):
    VS_AI = "vs_ai"
    VS_PLAYER = "vs_player"


class RoomStatus(Enum):
    WAITING = "waiting"
    READY = "ready"
    IN_GAME = "in_game"
    FINISHED = "finished"


@dataclass
class PlayerSession:
    """Represents a player session in a game."""
    sid: str  # Socket ID
    name: str
    deck_id: Optional[str] = None
    player_index: int = 0
    is_ready: bool = False
    is_ai: bool = False


@dataclass
class Room:
    """Represents a game room."""
    code: str
    host_sid: str
    players: List[PlayerSession] = field(default_factory=list)
    status: RoomStatus = RoomStatus.WAITING
    game_id: Optional[str] = None
    created_at: float = field(default_factory=time.time)


@dataclass
class ActiveGame:
    """Represents an active game with full state."""
    game_id: str
    mode: GameMode
    sessions: List[PlayerSession]
    game_state: GameState
    room_code: Optional[str] = None
    created_at: float = field(default_factory=time.time)


class GameManager:
    """Manages all active games, rooms, and player sessions."""

    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.games: Dict[str, ActiveGame] = {}
        self.player_to_room: Dict[str, str] = {}  # sid -> room_code
        self.player_to_game: Dict[str, str] = {}  # sid -> game_id

        # Load card database
        self.card_db: Dict[str, Card] = {}
        self._load_cards()

    def _load_cards(self):
        """Load the card database."""
        try:
            db_path = Path(__file__).parent.parent / "data" / "cards.json"
            self.card_db = load_card_database(str(db_path))
        except Exception as e:
            print(f"[ERROR] Could not load card database: {e}")

    @property
    def active_room_count(self) -> int:
        return len(self.rooms)

    @property
    def active_game_count(self) -> int:
        return len(self.games)

    # ========================================================================
    # Room Management
    # ========================================================================

    def create_room(self, code: str, host_sid: str, host_name: str) -> Room:
        """Create a new room."""
        host = PlayerSession(sid=host_sid, name=host_name, player_index=0)
        room = Room(code=code, host_sid=host_sid, players=[host])
        self.rooms[code] = room
        self.player_to_room[host_sid] = code
        return room

    def join_room(self, code: str, player_sid: str, player_name: str) -> Optional[Room]:
        """Join an existing room."""
        room = self.rooms.get(code)
        if not room or len(room.players) >= 2:
            return None

        player = PlayerSession(sid=player_sid, name=player_name, player_index=1)
        room.players.append(player)
        self.player_to_room[player_sid] = code

        if len(room.players) == 2:
            room.status = RoomStatus.READY

        return room

    def leave_room(self, player_sid: str) -> Optional[str]:
        """Remove a player from their room."""
        code = self.player_to_room.get(player_sid)
        if not code:
            return None

        room = self.rooms.get(code)
        if room:
            room.players = [p for p in room.players if p.sid != player_sid]
            if len(room.players) == 0:
                del self.rooms[code]
            elif room.host_sid == player_sid and room.players:
                room.host_sid = room.players[0].sid

        del self.player_to_room[player_sid]
        return code

    def get_room(self, code: str) -> Optional[Room]:
        return self.rooms.get(code)

    def get_player_room(self, player_sid: str) -> Optional[Room]:
        code = self.player_to_room.get(player_sid)
        return self.rooms.get(code) if code else None

    # ========================================================================
    # Game Management
    # ========================================================================

    def create_game_from_room(self, room: Room) -> Optional[ActiveGame]:
        """Create a game from a room."""
        if len(room.players) < 2:
            return None

        decks_path = Path(__file__).parent.parent / "data" / "decks"

        p1_session = room.players[0]
        p2_session = room.players[1]

        p1_deck_id = p1_session.deck_id or "red_luffy"
        p2_deck_id = p2_session.deck_id or "green_yamato"

        try:
            p1_cards, p1_leader = load_deck(str(decks_path / f"{p1_deck_id}.json"), self.card_db)
            p2_cards, p2_leader = load_deck(str(decks_path / f"{p2_deck_id}.json"), self.card_db)
        except Exception as e:
            print(f"[ERROR] Failed to load decks: {e}")
            return None

        player1 = Player(p1_session.name, p1_cards, p1_leader, p1_session.sid)
        player2 = Player(p2_session.name, p2_cards, p2_leader, p2_session.sid)

        game_state = GameState(player1, player2)

        game = ActiveGame(
            game_id=game_state.game_id,
            mode=GameMode.VS_PLAYER,
            sessions=room.players.copy(),
            game_state=game_state,
            room_code=room.code,
        )

        self.games[game.game_id] = game
        for session in room.players:
            self.player_to_game[session.sid] = game.game_id

        room.game_id = game.game_id
        room.status = RoomStatus.IN_GAME

        return game

    def create_ai_game(
        self,
        player_sid: str,
        player_name: str,
        deck_id: str = "red_luffy",
        ai_deck_id: str = "green_yamato",
        difficulty: str = "medium",
    ) -> Optional[ActiveGame]:
        """Create a game against AI."""
        decks_path = Path(__file__).parent.parent / "data" / "decks"

        try:
            p_cards, p_leader = load_deck(str(decks_path / f"{deck_id}.json"), self.card_db)
            ai_cards, ai_leader = load_deck(str(decks_path / f"{ai_deck_id}.json"), self.card_db)
        except Exception as e:
            print(f"[ERROR] Failed to load decks: {e}")
            return None

        player = Player(player_name, p_cards, p_leader, player_sid)
        ai_player = Player(f"Vinsmoke AI ({difficulty.capitalize()})", ai_cards, ai_leader, "ai")

        game_state = GameState(player, ai_player)

        player_session = PlayerSession(sid=player_sid, name=player_name, player_index=0)
        ai_session = PlayerSession(sid="ai", name=ai_player.name, player_index=1, is_ai=True)

        game = ActiveGame(
            game_id=game_state.game_id,
            mode=GameMode.VS_AI,
            sessions=[player_session, ai_session],
            game_state=game_state,
        )

        self.games[game.game_id] = game
        self.player_to_game[player_sid] = game.game_id

        return game

    def get_game(self, game_id: str) -> Optional[ActiveGame]:
        return self.games.get(game_id)

    def get_player_game(self, player_sid: str) -> Optional[ActiveGame]:
        game_id = self.player_to_game.get(player_sid)
        return self.games.get(game_id) if game_id else None

    def end_game(self, game_id: str) -> None:
        """End and clean up a game."""
        game = self.games.get(game_id)
        if not game:
            return

        for session in game.sessions:
            if not session.is_ai and session.sid in self.player_to_game:
                del self.player_to_game[session.sid]

        del self.games[game_id]

    def get_player_index(self, game: ActiveGame, player_sid: str) -> int:
        """Get player index for a socket ID."""
        for i, session in enumerate(game.sessions):
            if session.sid == player_sid:
                return i
        return -1

    # ========================================================================
    # Game Actions
    # ========================================================================

    def process_mulligan(self, game_id: str, player_sid: str, card_indices: List[int]) -> bool:
        """Process mulligan action."""
        game = self.get_game(game_id)
        if not game:
            return False

        player_idx = self.get_player_index(game, player_sid)
        player = game.game_state.player1 if player_idx == 0 else game.game_state.player2

        player.mulligan(card_indices)

        # Check if both have mulliganed
        if game.game_state.player1.has_mulliganed and game.game_state.player2.has_mulliganed:
            game.game_state.start_game()

        return True

    def process_play_card(self, game_id: str, player_sid: str, card_index: int) -> bool:
        """Process play card action."""
        game = self.get_game(game_id)
        if not game:
            return False

        player_idx = self.get_player_index(game, player_sid)
        gs = game.game_state
        current_idx = 0 if gs.current_player == gs.player1 else 1

        if player_idx != current_idx:
            return False

        return gs.play_card(card_index)

    def process_attack(self, game_id: str, player_sid: str, attacker_index: int, target_index: int) -> bool:
        """Process attack declaration."""
        game = self.get_game(game_id)
        if not game:
            return False

        player_idx = self.get_player_index(game, player_sid)
        gs = game.game_state
        current_idx = 0 if gs.current_player == gs.player1 else 1

        if player_idx != current_idx:
            return False

        return gs.declare_attack(attacker_index, target_index)

    def process_blocker_response(self, game_id: str, player_sid: str, blocker_index: Optional[int]) -> bool:
        """Process blocker response."""
        game = self.get_game(game_id)
        if not game:
            return False

        return game.game_state.respond_blocker(blocker_index)

    def process_counter_response(self, game_id: str, player_sid: str, counter_indices: List[int]) -> bool:
        """Process counter response."""
        game = self.get_game(game_id)
        if not game:
            return False

        return game.game_state.respond_counter(counter_indices)

    def process_attach_don(self, game_id: str, player_sid: str, card_index: int, amount: int = 1) -> bool:
        """Process DON attachment."""
        game = self.get_game(game_id)
        if not game:
            return False

        player_idx = self.get_player_index(game, player_sid)
        gs = game.game_state
        current_idx = 0 if gs.current_player == gs.player1 else 1

        if player_idx != current_idx:
            return False

        return gs.attach_don(card_index, amount)

    def process_end_turn(self, game_id: str, player_sid: str) -> bool:
        """Process end turn action."""
        game = self.get_game(game_id)
        if not game:
            return False

        player_idx = self.get_player_index(game, player_sid)
        gs = game.game_state
        current_idx = 0 if gs.current_player == gs.player1 else 1

        if player_idx != current_idx:
            return False

        gs.next_turn()
        return True

    # ========================================================================
    # AI Actions
    # ========================================================================

    def run_ai_turn(self, game: ActiveGame) -> List[str]:
        """Run a simple AI turn."""
        gs = game.game_state

        if gs.game_over:
            return gs.get_logs()

        current_idx = 0 if gs.current_player == gs.player1 else 1
        if not game.sessions[current_idx].is_ai:
            return []

        # Play cards
        for i, card in enumerate(list(gs.current_player.hand)):
            if gs.can_play_card(card):
                idx = gs.current_player.hand.index(card)
                gs.play_card(idx)

        # Attack with characters
        for i, card in enumerate(gs.current_player.cards_in_play):
            if gs.can_attack(card):
                gs.declare_attack(i, -1)
                gs.respond_blocker(None)
                gs.respond_counter([])

        # Attack with leader
        if gs.can_attack_with_leader() and not gs.current_player.leader.is_resting:
            gs.declare_attack(-1, -1)
            gs.respond_blocker(None)
            gs.respond_counter([])

        # End turn
        gs.next_turn()

        return gs.get_logs()

    # ========================================================================
    # Cleanup
    # ========================================================================

    async def cleanup_stale_rooms(self, max_age_seconds: int = 3600) -> int:
        """Remove rooms older than max_age_seconds."""
        now = time.time()
        stale_codes = [
            code
            for code, room in self.rooms.items()
            if now - room.created_at > max_age_seconds
        ]

        for code in stale_codes:
            room = self.rooms[code]
            for player in room.players:
                if player.sid in self.player_to_room:
                    del self.player_to_room[player.sid]
            del self.rooms[code]

        return len(stale_codes)
