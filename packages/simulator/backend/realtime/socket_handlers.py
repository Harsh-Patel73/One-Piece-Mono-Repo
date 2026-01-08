"""
Socket.IO event handlers for real-time gameplay.
"""

import socketio
from game.manager import GameManager, GameMode
import random
import string
import asyncio


def generate_game_id() -> str:
    """Generate a unique game ID."""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=12))


def generate_room_code() -> str:
    """Generate a 6-character room code."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


def setup_socket_handlers(sio: socketio.AsyncServer, game_manager: GameManager):
    """Setup all Socket.IO event handlers."""

    # ========================================================================
    # Connection Events
    # ========================================================================

    @sio.event
    async def connect(sid, environ):
        print(f"Client connected: {sid}")
        await sio.emit("connected", {"sid": sid}, to=sid)

    @sio.event
    async def disconnect(sid):
        print(f"Client disconnected: {sid}")
        room_code = game_manager.leave_room(sid)
        if room_code:
            await sio.emit(
                "player_left",
                {"message": "Opponent disconnected"},
                room=room_code,
            )

    # ========================================================================
    # Room Events
    # ========================================================================

    @sio.event
    async def create_room(sid, data):
        """Create a new room."""
        player_name = data.get("player_name", "Player 1")
        room_code = generate_room_code()

        room = game_manager.create_room(room_code, sid, player_name)
        await sio.enter_room(sid, room_code)

        await sio.emit(
            "room_created",
            {
                "room_code": room_code,
                "players": [{"name": p.name, "is_host": p.sid == room.host_sid} for p in room.players],
            },
            to=sid,
        )

    @sio.event
    async def join_room(sid, data):
        """Join an existing room."""
        room_code = data.get("room_code", "").upper()
        player_name = data.get("player_name", "Player 2")

        room = game_manager.join_room(room_code, sid, player_name)

        if not room:
            await sio.emit("error", {"message": "Room not found or full"}, to=sid)
            return

        await sio.enter_room(sid, room_code)

        await sio.emit(
            "player_joined",
            {
                "room_code": room_code,
                "players": [{"name": p.name, "is_host": p.sid == room.host_sid} for p in room.players],
                "status": room.status.value,
            },
            room=room_code,
        )

    @sio.event
    async def leave_room(sid, data):
        """Leave current room."""
        room_code = game_manager.leave_room(sid)
        if room_code:
            await sio.leave_room(sid, room_code)
            await sio.emit("player_left", {"message": "A player left the room"}, room=room_code)

    @sio.event
    async def set_ready(sid, data):
        """Set player ready status."""
        room = game_manager.get_player_room(sid)
        if not room:
            return

        for player in room.players:
            if player.sid == sid:
                player.is_ready = data.get("ready", True)
                break

        await sio.emit(
            "player_ready",
            {
                "players": [
                    {"name": p.name, "ready": p.is_ready, "is_host": p.sid == room.host_sid}
                    for p in room.players
                ],
            },
            room=room.code,
        )

    @sio.event
    async def start_game(sid, data):
        """Start the game (host only)."""
        room = game_manager.get_player_room(sid)
        if not room or room.host_sid != sid:
            await sio.emit("error", {"message": "Only host can start the game"}, to=sid)
            return

        if len(room.players) < 2:
            await sio.emit("error", {"message": "Need 2 players to start"}, to=sid)
            return

        # Create the actual game with game state
        game = game_manager.create_game_from_room(room)
        if not game:
            await sio.emit("error", {"message": "Failed to create game"}, to=sid)
            return

        # Send initial game state to all players
        for session in game.sessions:
            state = game.game_state.to_dict(for_player=session.sid)
            await sio.emit(
                "game_started",
                {
                    "game_id": game.game_id,
                    "player_index": game_manager.get_player_index(game, session.sid),
                    "game_state": state,
                },
                to=session.sid,
            )

    # ========================================================================
    # AI Game Events
    # ========================================================================

    @sio.event
    async def start_ai_game(sid, data):
        """Start a game against AI."""
        player_name = data.get("player_name", "Player")
        difficulty = data.get("difficulty", "medium")
        deck_id = data.get("deck_id", "red_luffy")

        game = game_manager.create_ai_game(
            player_sid=sid,
            player_name=player_name,
            deck_id=deck_id,
            difficulty=difficulty,
        )

        if not game:
            await sio.emit("error", {"message": "Failed to create game"}, to=sid)
            return

        state = game.game_state.to_dict(for_player=sid)

        await sio.emit(
            "game_started",
            {
                "game_id": game.game_id,
                "mode": "vs_ai",
                "player_index": 0,
                "game_state": state,
            },
            to=sid,
        )

    # ========================================================================
    # Game Action Events
    # ========================================================================

    @sio.event
    async def mulligan(sid, data):
        """Handle mulligan action."""
        game = game_manager.get_player_game(sid)
        if not game:
            await sio.emit("error", {"message": "Not in a game"}, to=sid)
            return

        card_indices = data.get("card_indices", [])
        game_manager.process_mulligan(game.game_id, sid, card_indices)

        # Send updated state
        await send_game_state(sio, game_manager, game)

        # If AI game and AI needs to mulligan, do it automatically
        if game.mode == GameMode.VS_AI and not game.game_state.player2.has_mulliganed:
            game.game_state.player2.mulligan([])  # AI keeps hand
            game.game_state.start_game()
            await send_game_state(sio, game_manager, game)

    @sio.event
    async def play_card(sid, data):
        """Play a card from hand."""
        game = game_manager.get_player_game(sid)
        if not game:
            await sio.emit("error", {"message": "Not in a game"}, to=sid)
            return

        card_index = data.get("card_index")
        if card_index is None:
            await sio.emit("error", {"message": "Card index required"}, to=sid)
            return

        success = game_manager.process_play_card(game.game_id, sid, card_index)
        if not success:
            await sio.emit("error", {"message": "Cannot play that card"}, to=sid)
            return

        await send_game_state(sio, game_manager, game)

    @sio.event
    async def attack(sid, data):
        """Declare an attack."""
        game = game_manager.get_player_game(sid)
        if not game:
            await sio.emit("error", {"message": "Not in a game"}, to=sid)
            return

        attacker_index = data.get("attacker_index")
        target_index = data.get("target_index", -1)

        success = game_manager.process_attack(game.game_id, sid, attacker_index, target_index)
        if not success:
            await sio.emit("error", {"message": "Cannot attack with that card"}, to=sid)
            return

        await send_game_state(sio, game_manager, game)

        # If AI game and awaiting AI response, auto-respond
        if game.mode == GameMode.VS_AI:
            gs = game.game_state
            if gs.awaiting_response == "blocker":
                game_manager.process_blocker_response(game.game_id, "ai", None)
                await send_game_state(sio, game_manager, game)
            if gs.awaiting_response == "counter":
                game_manager.process_counter_response(game.game_id, "ai", [])
                await send_game_state(sio, game_manager, game)

    @sio.event
    async def blocker_response(sid, data):
        """Respond with blocker or pass."""
        game = game_manager.get_player_game(sid)
        if not game:
            await sio.emit("error", {"message": "Not in a game"}, to=sid)
            return

        blocker_index = data.get("blocker_index")  # None means pass
        game_manager.process_blocker_response(game.game_id, sid, blocker_index)
        await send_game_state(sio, game_manager, game)

    @sio.event
    async def counter_response(sid, data):
        """Use counter cards or pass."""
        game = game_manager.get_player_game(sid)
        if not game:
            await sio.emit("error", {"message": "Not in a game"}, to=sid)
            return

        counter_indices = data.get("counter_indices", [])
        game_manager.process_counter_response(game.game_id, sid, counter_indices)
        await send_game_state(sio, game_manager, game)

    @sio.event
    async def attach_don(sid, data):
        """Attach DON to a card."""
        game = game_manager.get_player_game(sid)
        if not game:
            await sio.emit("error", {"message": "Not in a game"}, to=sid)
            return

        card_index = data.get("card_index")
        amount = data.get("amount", 1)

        success = game_manager.process_attach_don(game.game_id, sid, card_index, amount)
        if not success:
            await sio.emit("error", {"message": "Cannot attach DON"}, to=sid)
            return

        await send_game_state(sio, game_manager, game)

    @sio.event
    async def end_turn(sid, data):
        """End the current player's turn."""
        game = game_manager.get_player_game(sid)
        if not game:
            return

        success = game_manager.process_end_turn(game.game_id, sid)
        if not success:
            await sio.emit("error", {"message": "Cannot end turn"}, to=sid)
            return

        await send_game_state(sio, game_manager, game)

        # If AI game and it's AI's turn, run AI turn
        if game.mode == GameMode.VS_AI:
            gs = game.game_state
            current_idx = 0 if gs.current_player == gs.player1 else 1
            if game.sessions[current_idx].is_ai and not gs.game_over:
                # Add small delay for visibility
                await asyncio.sleep(1)
                game_manager.run_ai_turn(game)
                await send_game_state(sio, game_manager, game)

    @sio.event
    async def surrender(sid, data):
        """Surrender the game."""
        game = game_manager.get_player_game(sid)
        if not game:
            return

        player_idx = game_manager.get_player_index(game, sid)
        winner = 1 if player_idx == 0 else 0

        if game.room_code:
            await sio.emit(
                "game_over",
                {"winner": winner, "reason": "surrender"},
                room=game.room_code,
            )
        else:
            await sio.emit(
                "game_over",
                {"winner": winner, "reason": "surrender"},
                to=sid,
            )

        game_manager.end_game(game.game_id)


async def send_game_state(sio: socketio.AsyncServer, game_manager: GameManager, game):
    """Send updated game state to all players in a game."""
    gs = game.game_state
    logs = gs.get_logs()

    for session in game.sessions:
        if session.is_ai:
            continue

        state = gs.to_dict(for_player=session.sid)

        await sio.emit(
            "game_update",
            {
                "game_state": state,
                "logs": logs,
            },
            to=session.sid,
        )

    # Check for game over
    if gs.game_over:
        winner = 0 if gs.winner == gs.player1 else 1
        for session in game.sessions:
            if not session.is_ai:
                await sio.emit(
                    "game_over",
                    {
                        "winner": winner,
                        "reason": "victory",
                        "winner_name": gs.winner.name,
                    },
                    to=session.sid,
                )
