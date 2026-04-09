"""
Socket.IO event handlers for real-time gameplay.
"""

import re
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
    # Per-SID effect test sessions (set_code → EffectTestSession)
    _test_sessions: dict = {}

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
        deck_data = data.get("deck_data")  # Custom deck: {leader: str, cards: {id: count}}

        game = game_manager.create_ai_game(
            player_sid=sid,
            player_name=player_name,
            deck_id=deck_id,
            deck_data=deck_data,
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

    @sio.event
    async def start_playtest(sid, data):
        """Start a solo playtest game (one player controls both sides)."""
        player_name = data.get("player_name", "Player")
        deck_id = data.get("deck_id", "red_luffy")
        deck_data = data.get("deck_data")  # Custom deck: {leader: str, cards: {id: count}}

        game = game_manager.create_playtest_game(
            player_sid=sid,
            player_name=player_name,
            deck_id=deck_id,
            deck_data=deck_data,
        )

        if not game:
            await sio.emit("error", {"message": "Failed to create playtest game"}, to=sid)
            return

        # Auto-mulligan both players (keep their hands) and start the game
        gs = game.game_state
        if not gs.player1.has_mulliganed:
            gs.player1.mulligan([])  # Keep hand
        if not gs.player2.has_mulliganed:
            gs.player2.mulligan([])  # Keep hand
        gs.start_game()

        state = gs.to_dict(for_player=sid)

        await sio.emit(
            "game_started",
            {
                "game_id": game.game_id,
                "mode": "playtest",
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

        # For pure VS_AI games, auto-resolve all combat steps (AI has no UI).
        # Test/playtest games: every step is an explicit player prompt.
        if game.mode == GameMode.VS_AI:
            gs = game.game_state
            # Auto-skip leader effect step (AI doesn't use it)
            if gs.awaiting_response == "leader_effect":
                game_manager.process_leader_effect_response(game.game_id, "ai", False)
                await send_game_state(sio, game_manager, game)
            gs = game.game_state
            if gs.awaiting_response == "blocker":
                game_manager.process_blocker_response(game.game_id, "ai", None)
                await send_game_state(sio, game_manager, game)
            gs = game.game_state
            if gs.awaiting_response == "counter":
                game_manager.process_counter_response(game.game_id, "ai", [])
                await send_game_state(sio, game_manager, game)
            # After damage, a trigger prompt may appear — auto-decline for AI
            gs = game.game_state
            if gs.awaiting_response == "trigger":
                game_manager.process_trigger_response(game.game_id, "ai", False)
                await send_game_state(sio, game_manager, game)
            # Double attack may produce a second trigger
            gs = game.game_state
            if gs.awaiting_response == "trigger":
                game_manager.process_trigger_response(game.game_id, "ai", False)
                await send_game_state(sio, game_manager, game)

    @sio.event
    async def leader_effect_response(sid, data):
        """Respond to the leader effect step (use or decline the leader's combat ability)."""
        game = game_manager.get_player_game(sid)
        if not game:
            await sio.emit("error", {"message": "Not in a game"}, to=sid)
            return

        use_effect = bool(data.get("use_effect", False))
        success = game_manager.process_leader_effect_response(game.game_id, sid, use_effect)
        if not success:
            await sio.emit("error", {"message": "Cannot respond to leader effect step"}, to=sid)
            return
        await send_game_state(sio, game_manager, game)

    @sio.event
    async def trigger_response(sid, data):
        """Respond to a trigger prompt — activate or decline."""
        game = game_manager.get_player_game(sid)
        if not game:
            await sio.emit("error", {"message": "Not in a game"}, to=sid)
            return

        activate = bool(data.get("activate", False))
        success = game_manager.process_trigger_response(game.game_id, sid, activate)
        if not success:
            await sio.emit("error", {"message": "Cannot respond to trigger"}, to=sid)
            return
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
    async def activate_effect(sid, data):
        """Activate a card's [Activate: Main] effect."""
        game = game_manager.get_player_game(sid)
        if not game:
            await sio.emit("error", {"message": "Not in a game"}, to=sid)
            return

        card_index = data.get("card_index")
        if card_index is None:
            await sio.emit("error", {"message": "Card index required"}, to=sid)
            return

        success = game_manager.process_activate_effect(game.game_id, sid, card_index)
        if not success:
            await sio.emit("error", {"message": "Cannot activate effect"}, to=sid)
            return

        await send_game_state(sio, game_manager, game)

    @sio.event
    async def effect_choice_response(sid, data):
        """Handle player response to an effect choice."""
        print(f"[DEBUG] effect_choice_response: sid={sid}, data={data}")
        game = game_manager.get_player_game(sid)
        if not game:
            print(f"[DEBUG] effect_choice_response: no game for sid={sid}")
            await sio.emit("error", {"message": "Not in a game"}, to=sid)
            return

        choice_id = data.get("choice_id")
        selected = data.get("selected", [])

        if not choice_id:
            await sio.emit("error", {"message": "Choice ID required"}, to=sid)
            return

        success = game_manager.process_effect_choice(game.game_id, sid, choice_id, selected)
        if not success:
            print(f"[DEBUG] effect_choice_response: FAILED for choice_id={choice_id}, selected={selected}")
            await sio.emit("error", {"message": "Invalid choice response"}, to=sid)
            return

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

    @sio.event
    async def debug_scenario(sid, data):
        """Debug: Mutate game state directly for effect testing.

        Expected data keys (all optional):
          player_index      int   Which player to modify (0 or 1). Default 0.
          life              int   Set player's life count to this value.
          opponent_life     int   Set opponent's life count to this value.
          don_active        int   Set player's active DON count.
          add_to_hand       list  Card IDs to add to player's hand.
          add_to_field      list  Card IDs to add directly to player's field.
          add_to_opp_field  list  Card IDs to add directly to opponent's field.
          clear_hand        bool  Remove all cards from player's hand.
          clear_field       bool  Move all player's field cards to trash.
          clear_opp_field   bool  Move all opponent's field cards to trash.
        """
        game = game_manager.get_player_game(sid)
        if not game:
            await sio.emit("error", {"message": "Not in a game"}, to=sid)
            return

        gs = game.game_state
        player_idx = data.get("player_index", 0)
        player = gs.player1 if player_idx == 0 else gs.player2
        opponent = gs.player2 if player_idx == 0 else gs.player1

        # --- Life counts ---
        if "life" in data:
            target = int(data["life"])
            while len(player.life_cards) > target:
                card = player.life_cards.pop()
                player.trash.append(card)
            while len(player.life_cards) < target and player.deck:
                player.life_cards.append(player.deck.pop(0))

        if "opponent_life" in data:
            target = int(data["opponent_life"])
            while len(opponent.life_cards) > target:
                card = opponent.life_cards.pop()
                opponent.trash.append(card)
            while len(opponent.life_cards) < target and opponent.deck:
                opponent.life_cards.append(opponent.deck.pop(0))

        # --- DON ---
        if "don_active" in data:
            target = int(data["don_active"])
            current_active = player.don_pool.count("active")
            diff = target - current_active
            if diff > 0:
                for _ in range(diff):
                    player.don_pool.append("active")
            elif diff < 0:
                removed = 0
                for i in range(len(player.don_pool) - 1, -1, -1):
                    if player.don_pool[i] == "active" and removed < abs(diff):
                        player.don_pool[i] = "rested"
                        removed += 1

        # --- Clear zones ---
        if data.get("clear_hand"):
            player.trash.extend(player.hand)
            player.hand.clear()

        if data.get("clear_field"):
            player.trash.extend(player.cards_in_play)
            player.cards_in_play.clear()

        if data.get("clear_opp_field"):
            opponent.trash.extend(opponent.cards_in_play)
            opponent.cards_in_play.clear()

        # --- Add cards ---
        from game.card_loader import get_card_by_id

        for card_id in data.get("add_to_hand", []):
            card = get_card_by_id(game_manager.card_db, card_id)
            if card:
                player.hand.append(card)

        for card_id in data.get("add_to_field", []):
            card = get_card_by_id(game_manager.card_db, card_id)
            if card:
                player.cards_in_play.append(card)

        for card_id in data.get("add_to_opp_field", []):
            card = get_card_by_id(game_manager.card_db, card_id)
            if card:
                opponent.cards_in_play.append(card)

        # Re-apply continuous effects so newly added cards (e.g. OP03-088 Fukurou)
        # have their continuous flags (cannot_be_ko_by_effects, etc.) set correctly
        gs._apply_continuous_effects()

        await send_game_state(sio, game_manager, game)

    @sio.event
    async def simulate_ko(sid, data):
        """KO a character on P1's field to trigger On K.O. effects (test games only)."""
        game = game_manager.get_player_game(sid)
        if not game or not game.is_test_game:
            return
        card_index = data.get("card_index")
        gs = game.game_state
        player = gs.player1
        if card_index is not None and 0 <= card_index < len(player.cards_in_play):
            card = player.cards_in_play[card_index]
            player.cards_in_play.remove(card)
            player.trash.append(card)
            gs._log(f"{card.name} was KO'd (simulated)")
            from optcg_engine.effects.manager import get_effect_manager
            effect_manager = get_effect_manager()
            effect_manager.on_ko(gs, player, card)
            await send_game_state(sio, game_manager, game)

    # ========================================================================
    # Effect Tester Events
    # ========================================================================

    @sio.event
    async def start_test_game(sid, data):
        """Create an interactive playtest game pre-configured for a specific card.

        Sets up a real GameState with:
          - Test card in P1's hand (or as P1's leader if it's a LEADER)
          - 3 P1 characters on field (so continuous effects like Zoro's are visible)
          - 3 P2 characters on field (rested, for attack/KO targeting tests)
          - P1 has 10 active DON

        data keys:
          card_id   str   e.g. "OP01-001"
        """
        import copy
        import random
        import string
        from pathlib import Path
        from game.manager import ActiveGame, GameMode, PlayerSession
        from game.deck_loader import load_deck

        card_id = (data.get("card_id") or "").upper()
        if not card_id:
            await sio.emit("error", {"message": "card_id required"}, to=sid)
            return

        card = game_manager._find_card_by_id(card_id)
        if not card:
            await sio.emit("error", {"message": f"Card {card_id} not found"}, to=sid)
            return

        decks_path = Path(__file__).parent.parent / "data" / "decks"
        try:
            p1_cards, default_p1_leader = load_deck(
                str(decks_path / "red_luffy.json"), game_manager.card_db
            )
            p2_cards, p2_leader = load_deck(
                str(decks_path / "green_yamato.json"), game_manager.card_db
            )
        except Exception as e:
            await sio.emit("error", {"message": f"Failed to load test deck: {e}"}, to=sid)
            return

        # Use test card as leader if it IS a leader; otherwise keep default.
        # If the effect requires a specific leader, find that leader in card_db
        # so the condition fires during testing.
        _et_early = (card.effect or '').lower()
        _leader_name_m = re.search(r'if your leader is \[([^\]]+)\]', _et_early)
        _leader_type_m = (
            re.search(r'if your leader has the \{([^}]+)\} type', _et_early)
            or re.search(r"leader'?s? type includes [\"']([^\"']+)[\"']", _et_early)
        )
        # Hard-coded set for cards that reference Whitebeard Pirates via patterns
        # the regex can't reliably catch (e.g. "[Edward.Newgate]", trait checks
        # on other cards, or no explicit leader text at all).
        _WB_LEADER_CARDS = {
            "OP02-001", "OP02-002", "OP02-003", "OP02-004", "OP02-005",
            "OP02-008", "OP02-009", "OP02-013", "OP02-018", "OP02-021",
            "OP02-023", "OP02-024", "OP02-047",
        }
        _required_leader = None
        if card.card_type != "LEADER":
            if card_id in _WB_LEADER_CARDS:
                for _lc in game_manager.card_db.values():
                    if _lc.card_type == "LEADER" and _lc.id == "OP02-001":
                        _required_leader = copy.deepcopy(_lc)
                        break
            elif _leader_name_m:
                _needed = _leader_name_m.group(1).lower()
                for _lc in game_manager.card_db.values():
                    if _lc.card_type == "LEADER" and _needed in (_lc.name or '').lower():
                        _required_leader = copy.deepcopy(_lc)
                        break
            elif _leader_type_m:
                _needed = _leader_type_m.group(1).lower()
                for _lc in game_manager.card_db.values():
                    if _lc.card_type == "LEADER" and _needed in (_lc.card_origin or '').lower():
                        _required_leader = copy.deepcopy(_lc)
                        break
        p1_leader = (
            copy.deepcopy(card) if card.card_type == "LEADER"
            else _required_leader if _required_leader
            else default_p1_leader
        )

        # Build players — Player.__init__ auto-builds life pile, shuffles deck, draws 5 cards
        # Both players use the same SID so to_dict(for_player=sid) shows both hands (playtest mode)
        from optcg_engine.game_engine import GameState, Player
        player1 = Player("Tester", p1_cards, p1_leader, sid)
        player2 = Player("Opponent", p2_cards, p2_leader, sid)

        gs = GameState(player1, player2)
        gs.player1.has_mulliganed = True
        gs.player2.has_mulliganed = True
        gs.start_game()

        # Give P1 plenty of DON for testing (override the 1 DON set by GameState.__init__)
        gs.player1.don_pool = ["active"] * 10
        # Give P2 DON so they can pay for counter events during combat
        gs.player2.don_pool = ["active"] * 3

        # For cards that check life count (e.g. "2 or fewer Life"), reduce P1 life so the
        # condition is met during testing.
        effect_text_raw = (card.effect or '').lower()
        if any(phrase in effect_text_raw for phrase in [
            '2 or fewer life', '2 or less life',
            '1 or fewer life', '1 or less life',
        ]):
            while len(gs.player1.life_cards) > 2:
                gs.player1.trash.append(gs.player1.life_cards.pop())

        # For DON-adding effects (e.g. Kaido OP01-061), set P1 DON to 5 instead of 10
        # so the effect can be observed (DON going from 5 → 6).
        if any(phrase in effect_text_raw for phrase in ['add up to 1 don', 'add 1 don']):
            gs.player1.don_pool = ["active"] * 5

        # Detect cards whose effect fires when the OPPONENT does something during YOUR turn
        # (e.g. Usopp OP01-004: draw when opponent activates Event). These need to be on P2's
        # field so the user (controlling P1) can trigger them by playing events as a counter.
        effect_text = (card.effect or '').lower()
        # Cards that react when the opponent plays an event during YOUR turn.
        # e.g. Usopp OP01-004: "[DON!! x1] [Your Turn] Draw 1 when opponent activates Event"
        # Setup: card stays on P1's field with 1 DON attached, P2 gets counter events.
        is_opponent_event_reactive = (
            card.card_type == "CHARACTER"
            and '[your turn]' in effect_text
            and 'opponent' in effect_text
            and any(kw in effect_text for kw in ('activates', 'plays', 'uses'))
            and 'event' in effect_text
        )

        # Check if test card has a Trigger effect — seed into opponent's life
        has_trigger_effect = bool(
            (card.trigger and card.trigger.strip())
            or (card.effect and '[Trigger]' in card.effect)
        )

        # Placement rule:
        #   [Trigger] cards  → opponent's life (user attacks to reveal and test the trigger)
        #   [On Play] cards  → hand (user plays them to trigger the effect)
        #   EVENT cards      → hand (events are activated by playing from hand)
        #   All other CHARACTER/STAGE cards → field (ready to activate/attack/use)
        #   LEADER           → already set above, skip
        has_on_play = '[on play]' in effect_text
        test_card_goes_to_hand = (
            card.card_type == "EVENT"
            or (card.card_type == "CHARACTER" and has_on_play)
            or (card.card_type == "STAGE" and has_on_play)
        )

        if card.card_type != "LEADER":
            # Trigger cards: always seed a copy into opponent's life (top) for testing
            if has_trigger_effect:
                trigger_copy = copy.deepcopy(card)
                gs.player2.life_cards.append(trigger_copy)  # append = top of life pile

            if is_opponent_event_reactive:
                # Put on P1's field with 1 DON already attached.
                test_card_copy = copy.deepcopy(card)
                setattr(test_card_copy, 'attached_don', 1)
                if gs.player1.don_pool:
                    gs.player1.don_pool[-1] = "rested"
                gs.player1.cards_in_play.append(test_card_copy)
                gs._apply_keywords(test_card_copy)
            elif test_card_goes_to_hand:
                # On Play / Events → hand so user can trigger on play
                gs.player1.hand.insert(0, copy.deepcopy(card))
            else:
                # All other effects (activate, when attacking, continuous, on ko, etc.) → field
                test_card_copy = copy.deepcopy(card)
                gs.player1.cards_in_play.append(test_card_copy)
                gs._apply_keywords(test_card_copy)

        # Move up to 3 P1 characters from hand to field so continuous/conditional effects
        # are visible. Cap at 3 (not 5) so there are always enough hand cards for on_play
        # effects that discard/bounce from hand (e.g. Gordon OP01-011).
        # Exclude the test card itself so it stays in hand.
        p1_chars = [c for c in list(gs.player1.hand)
                    if c.card_type == "CHARACTER" and c.id != card.id][:3]
        for c in p1_chars:
            gs.player1.hand.remove(c)
            gs.player1.cards_in_play.append(c)
            gs._apply_keywords(c)

        # Move up to 5 P2 characters from hand to field.
        # Rest the first 3 so they can be attacked normally.
        # Leave the last 2 active so cards that target active characters (e.g. Franky) can be tested.
        # Also ensure at least one P2 char has low power (≤3000) for effects like Robin's KO.
        p2_chars = [c for c in list(gs.player2.hand) if c.card_type == "CHARACTER"][:5]
        for i, c in enumerate(p2_chars):
            gs.player2.hand.remove(c)
            c.is_resting = (i < 3)  # First 3 rested, last 2 active
            gs.player2.cards_in_play.append(c)
            gs._apply_keywords(c)

        # If test card KOs low-power opponents, seed a weak char onto P2's field if none present.
        if any(kw in effect_text for kw in ('3000 power or less', '2000 power or less', '4000 power or less')):
            has_low_power = any(
                (getattr(c, 'power', 0) or 0) <= 4000
                for c in gs.player2.cards_in_play
            )
            if not has_low_power:
                weak_chars = sorted(
                    [c for c in game_manager.card_db.values()
                     if c.card_type == "CHARACTER" and (c.power or 0) <= 3000
                     and not any(c.id.endswith(s) for s in ('_p1', '_p2', '_p3'))],
                    key=lambda c: c.power or 0,
                )
                if weak_chars:
                    weak = copy.deepcopy(weak_chars[0])
                    weak.is_resting = True
                    gs.player2.cards_in_play.append(weak)

        # For opponent-event-reactive cards: give P2 counter event cards so that when
        # P1 attacks and P2 responds with a counter event, the effect triggers.
        if is_opponent_event_reactive:
            counter_events = sorted(
                [c for c in game_manager.card_db.values()
                 if c.card_type == "EVENT"
                 and c.effect and '[Counter]' in (c.effect or '')
                 and (c.cost or 0) <= 2
                 and not any(c.id.endswith(s) for s in ('_p1', '_p2', '_p3'))],
                key=lambda c: c.cost or 0,
            )
            for ev in counter_events[:3]:
                gs.player2.hand.append(copy.deepcopy(ev))

        # Seed P1's trash with character cards so effects that search trash
        # (e.g. Uta: "add red cost 3 or less Character from trash") have targets.
        # Include a diverse mix: low-cost red, green, blue characters from card DB.
        trash_seeds = []
        seen_ids = set()
        for color in ['Red', 'Green', 'Blue', 'Purple', 'Black']:
            color_chars = sorted(
                [c for c in game_manager.card_db.values()
                 if c.card_type == "CHARACTER"
                 and color in (c.colors or [])
                 and (c.cost or 0) <= 3
                 and c.id not in seen_ids
                 and not any(c.id.endswith(s) for s in ('_p1', '_p2', '_p3'))],
                key=lambda c: c.cost or 0,
            )
            for ch in color_chars[:2]:
                trash_seeds.append(ch)
                seen_ids.add(ch.id)
        for seed in trash_seeds:
            gs.player1.trash.append(copy.deepcopy(seed))

        # Extra trash seeding: if the test card effect references a specific type/origin,
        # add matching cards so the effect has targets.
        # e.g. Chopper OP01-015: "Straw Hat Crew" characters cost 4 or less from trash.
        if 'straw hat crew' in effect_text:
            shc_seeds = sorted(
                [c for c in game_manager.card_db.values()
                 if c.card_type == "CHARACTER"
                 and 'straw hat crew' in (c.card_origin or '').lower()
                 and (c.cost or 0) <= 4
                 and c.id != card.id
                 and c.id not in seen_ids
                 and not any(c.id.endswith(s) for s in ('_p1', '_p2', '_p3'))],
                key=lambda c: c.cost or 0,
            )
            for shc in shc_seeds[:2]:
                gs.player1.trash.append(copy.deepcopy(shc))
                seen_ids.add(shc.id)

        # Seed named cards into P1's deck for "Play up to 1 [Name] from your deck" effects.
        # e.g. Caesar OP01-069: "[On K.O.] Play up to 1 [Smiley] from your deck"
        for _named in re.findall(r'play up to \d+ \[([^\]]+)\] from your deck', effect_text):
            _target_name = _named.lower()
            if not any(_target_name in (c.name or '').lower() for c in gs.player1.deck):
                _named_candidates = sorted(
                    [c for c in game_manager.card_db.values()
                     if _target_name in (c.name or '').lower()
                     and c.card_type == "CHARACTER"
                     and not any(c.id.endswith(s) for s in ('_p1', '_p2', '_p3'))],
                    key=lambda c: c.id,
                )
                for _nc in _named_candidates[:2]:
                    gs.player1.deck.insert(0, copy.deepcopy(_nc))

        # Seed P1's deck (top) with type-specific cards for searcher effects that look
        # at top N cards of the deck. e.g. Momonosuke OP01-041: "Look at 5, add Land of Wano".
        # Detect origin types referenced in the effect text and seed 2 matching cards at top.
        _origin_types = ['land of wano', 'straw hat crew', 'animal kingdom pirates',
                         'seven warlords of the sea', 'baroque works', 'heart pirates',
                         'dressrosa', 'donquixote pirates', 'big mom pirates',
                         'whitebeard pirates', 'impel down', 'fish-man', 'revolutionary army']
        if any(kw in effect_text for kw in ['look at', 'top of your deck', 'reveal the top']):
            for _otype in _origin_types:
                if _otype in effect_text:
                    has_in_top = any(_otype in (c.card_origin or '').lower()
                                     for c in gs.player1.deck[:5])
                    if not has_in_top:
                        _ot_candidates = sorted(
                            [c for c in game_manager.card_db.values()
                             if _otype in (c.card_origin or '').lower()
                             and c.card_type == "CHARACTER"
                             and (c.cost or 0) <= 5
                             and c.id != card.id
                             and not any(c.id.endswith(s) for s in ('_p1', '_p2', '_p3'))],
                            key=lambda c: c.cost or 0,
                        )
                        for _oc in _ot_candidates[:2]:
                            gs.player1.deck.insert(0, copy.deepcopy(_oc))

        # Seed P1's hand with type-specific cards needed to activate effects.
        # e.g. Kouzuki Oden OP01-031: needs {Land of Wano} card in hand to trash.
        # e.g. BE-BENG!! OP01-059: needs {Land of Wano} card in hand to trash + rested Wano on field.
        if 'land of wano' in effect_text:
            has_wano_in_hand = any('land of wano' in (c.card_origin or '').lower()
                                   for c in gs.player1.hand)
            if not has_wano_in_hand:
                wano_candidates = sorted(
                    [c for c in game_manager.card_db.values()
                     if 'land of wano' in (c.card_origin or '').lower()
                     and c.card_type == "CHARACTER"
                     and (c.cost or 0) <= 4
                     and not any(c.id.endswith(s) for s in ('_p1', '_p2', '_p3'))],
                    key=lambda c: c.cost or 0,
                )
                for wc in wano_candidates[:2]:
                    gs.player1.hand.append(copy.deepcopy(wc))
            # Also seed rested Land of Wano characters on P1's field if effect sets characters active
            if 'active' in effect_text or 'set' in effect_text:
                wano_on_field = any('land of wano' in (c.card_origin or '').lower()
                                    and getattr(c, 'is_resting', False)
                                    for c in gs.player1.cards_in_play)
                if not wano_on_field:
                    wano_field_cands = sorted(
                        [c for c in game_manager.card_db.values()
                         if 'land of wano' in (c.card_origin or '').lower()
                         and c.card_type == "CHARACTER"
                         and (c.cost or 0) <= 3
                         and not any(c.id.endswith(s) for s in ('_p1', '_p2', '_p3'))],
                        key=lambda c: c.cost or 0,
                    )
                    for wfc in wano_field_cands[:2]:
                        wfc_copy = copy.deepcopy(wfc)
                        wfc_copy.is_resting = True
                        gs.player1.cards_in_play.append(wfc_copy)
                        gs._apply_keywords(wfc_copy)

        # OP03-specific frontend test setup overrides from pending fixes.
        if card.id == "OP03-033":
            for _lc in game_manager.card_db.values():
                if _lc.card_type == "LEADER" and 'east blue' in (_lc.card_origin or '').lower():
                    gs.player2.leader = copy.deepcopy(_lc)
                    break

        if card.id == "OP03-040":
            while len(gs.player1.deck) > 4:
                gs.player1.trash.append(gs.player1.deck.pop())

        if card.id in {"OP03-045", "OP03-049", "OP03-053"}:
            while len(gs.player1.deck) > 20:
                gs.player1.trash.append(gs.player1.deck.pop())

        # For cards that check opponent's attribute (e.g. Luffy OP01-024 vs Strike attribute),
        # seed P2's field with matching attribute characters.
        _attribute_types = ['strike', 'ranged', 'wisdom', 'special', 'slash']
        for _attr in _attribute_types:
            if _attr in effect_text:
                has_attr = any(_attr == (getattr(c, 'attribute', '') or '').lower()
                               for c in gs.player2.cards_in_play)
                if not has_attr:
                    _attr_cands = sorted(
                        [c for c in game_manager.card_db.values()
                         if c.card_type == "CHARACTER"
                         and (c.attribute or '').lower() == _attr
                         and (c.power or 0) >= 4000
                         and not any(c.id.endswith(s) for s in ('_p1', '_p2', '_p3'))],
                        key=lambda c: c.power or 0,
                    )
                    for _ac in _attr_cands[:2]:
                        ac_copy = copy.deepcopy(_ac)
                        ac_copy.is_resting = True
                        gs.player2.cards_in_play.append(ac_copy)
                        gs._apply_keywords(ac_copy)

        # For cost-reduction effects on events (e.g. Crocodile OP01-067 blue events -1 cost),
        # seed blue events in P1's hand so the effect can be tested.
        if 'event' in effect_text and 'cost' in effect_text:
            for color_name in ['blue', 'red', 'green', 'purple', 'black']:
                if color_name in effect_text:
                    has_color_event = any(
                        getattr(c, 'card_type', '') == 'EVENT'
                        and color_name.capitalize() in (getattr(c, 'colors', []) or [])
                        for c in gs.player1.hand
                    )
                    if not has_color_event:
                        _ev_cands = sorted(
                            [c for c in game_manager.card_db.values()
                             if c.card_type == "EVENT"
                             and color_name.capitalize() in (c.colors or [])
                             and (c.cost or 0) >= 1
                             and not any(c.id.endswith(s) for s in ('_p1', '_p2', '_p3'))],
                            key=lambda c: c.cost or 0,
                        )
                        for _ev in _ev_cands[:3]:
                            gs.player1.hand.append(copy.deepcopy(_ev))

        # For multicolor leaders, ensure P1 has 2+ cards of each leader color in hand.
        # e.g. Law (Red/Green) needs green characters so his swap-play effect has valid targets.
        if card.card_type == "LEADER" and len(card.colors) > 1:
            for color in card.colors:
                hand_count = sum(1 for c in gs.player1.hand if color in (c.colors or []))
                if hand_count < 2:
                    candidates = sorted(
                        [c for c in game_manager.card_db.values()
                         if c.card_type == "CHARACTER"
                         and color in (c.colors or [])
                         and (c.cost or 0) <= 4
                         and not any(c.id.endswith(s) for s in ('_p1', '_p2', '_p3'))],
                        key=lambda c: c.cost or 0,
                    )
                    for cand in candidates[:2]:
                        gs.player1.hand.append(copy.deepcopy(cand))

        # Apply continuous effects now that the field is set up
        gs._apply_continuous_effects()

        # Clean up any existing game for this session
        existing = game_manager.get_player_game(sid)
        if existing:
            game_manager.end_game(existing.game_id)

        game_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=12))
        p1_session = PlayerSession(sid=sid, name="Tester", player_index=0)
        p2_session = PlayerSession(sid=sid, name="Opponent", player_index=1)
        game = ActiveGame(
            game_id=game_id,
            mode=GameMode.PLAYTEST,
            sessions=[p1_session, p2_session],
            game_state=gs,
            is_test_game=True,
            auto_resolve_counter=not is_opponent_event_reactive,
        )
        game_manager.games[game_id] = game
        game_manager.player_to_game[sid] = game_id

        state = gs.to_dict(for_player=sid)
        await sio.emit(
            "game_started",
            {"game_id": game_id, "mode": "test", "player_index": 0, "game_state": state},
            to=sid,
        )
        print(f"[TEST] Game {game_id} created for {card_id} ({card.card_type})")

    @sio.event
    async def start_effect_test(sid, data):
        """Start an effect-testing session.

        data keys:
          set_code   str   e.g. "OP01" (default)
          filter     str   "todo" | "needsfix" | "all" (default "todo")
          card_id    str   Test a single card (overrides set_code/filter)
        """
        from game.effect_test_session import EffectTestSession, load_status_entries, get_timings

        card_id  = data.get("card_id")
        set_code = (data.get("set_code") or "OP01").upper()
        filt     = data.get("filter", "todo")

        all_entries = load_status_entries(set_code)
        if not all_entries:
            await sio.emit("error", {"message": f"No CARD_STATUS.md entries for {set_code}"}, to=sid)
            return

        if card_id:
            entries = [e for e in all_entries if e["id"] == card_id.upper()]
        elif filt == "needsfix":
            entries = [e for e in all_entries if e["status"] in ("🔲 To Do", "⚠ Needs Fix")]
        elif filt == "all":
            entries = [e for e in all_entries if e["status"] not in ("⬜ No Effect", "⬜ Keywords")]
        else:
            entries = [e for e in all_entries if e["status"] == "🔲 To Do"]

        if not entries:
            await sio.emit("error", {"message": f"No cards to test in {set_code} with filter '{filt}'"}, to=sid)
            return

        # Build raw card_db dict (id_normal → raw JSON entry) for the session
        raw_json_path = __import__("pathlib").Path(__file__).parent.parent / "data" / "cards.json"
        import json as _json
        raw_cards = _json.loads(raw_json_path.read_text(encoding="utf-8"))
        card_db = {}
        for c in raw_cards:
            cid = c.get("id_normal") or c.get("id", "")
            if cid and cid not in card_db:
                card_db[cid] = c

        session = EffectTestSession(entries, card_db)
        _test_sessions[sid] = session

        payload = session.build_payload()
        await sio.emit("effect_test_update", payload, to=sid)

    @sio.event
    async def effect_test_navigate(sid, data):
        """Navigate within the current effect-testing session.

        data keys:
          direction   str   "next" | "prev" | "rerun"
        """
        session = _test_sessions.get(sid)
        if not session:
            await sio.emit("error", {"message": "No active test session"}, to=sid)
            return

        direction = data.get("direction", "next")
        if direction == "next":
            session.advance()
        elif direction == "prev":
            session.go_back()
        # "rerun" → stay at same index, just rebuild

        payload = session.build_payload()
        await sio.emit("effect_test_update", payload, to=sid)

    @sio.event
    async def effect_test_verdict(sid, data):
        """Record a pass/fail/skip verdict for the current card.

        data keys:
          card_id   str   The card being judged (for safety check)
          verdict   str   "pass" | "fail" | "skip"
          note      str   Optional note (used for fail)
        """
        from game.effect_test_session import update_card_status

        session = _test_sessions.get(sid)
        if not session:
            await sio.emit("error", {"message": "No active test session"}, to=sid)
            return

        card_id = data.get("card_id", "")
        verdict = data.get("verdict", "skip")
        note    = data.get("note", "").strip() or None

        if verdict == "pass":
            update_card_status(card_id, "✅ Verified")
        elif verdict == "fail":
            update_card_status(card_id, "⚠ Needs Fix", note)

        # Update the in-memory entry so progress reflects immediately
        entry = session.current_entry
        if entry and entry["id"] == card_id:
            if verdict == "pass":
                entry["status"] = "✅ Verified"
            elif verdict == "fail":
                entry["status"] = "⚠ Needs Fix"
                if note:
                    entry["notes"] = note

        # Advance to next card automatically
        session.advance()
        payload = session.build_payload()
        await sio.emit("effect_test_update", payload, to=sid)


async def send_game_state(sio: socketio.AsyncServer, game_manager: GameManager, game):
    """Send updated game state to all players in a game."""
    gs = game.game_state
    # Use action_logs directly since get_logs may not exist in cached module
    logs = getattr(gs, 'action_logs', []).copy() if hasattr(gs, 'action_logs') else []

    # Deduplicate SIDs (in playtest mode, both sessions share the same SID)
    sent_sids = set()
    for session in game.sessions:
        if session.is_ai or session.sid in sent_sids:
            continue
        sent_sids.add(session.sid)

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
        sent_sids = set()
        for session in game.sessions:
            if not session.is_ai and session.sid not in sent_sids:
                sent_sids.add(session.sid)
                await sio.emit(
                    "game_over",
                    {
                        "winner": winner,
                        "reason": "victory",
                        "winner_name": gs.winner.name,
                    },
                    to=session.sid,
                )
