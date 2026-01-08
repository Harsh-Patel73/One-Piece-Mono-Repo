"""
Game routes for Vinsmoke Engine API.

Handles game creation, state retrieval, and action submission.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List

from ..schemas import (
    GameCreateRequest, GameStateSchema, GameSummarySchema,
    ActionSchema, ActionResultSchema, APIResponse,
    PlayerCreateSchema, PlayerType,
)
from ..game_manager import get_game_manager

router = APIRouter()


@router.post("", response_model=GameStateSchema)
async def create_game(request: GameCreateRequest):
    """
    Create a new game.

    Args:
        request: Game creation parameters including player configs

    Returns:
        Initial game state
    """
    manager = get_game_manager()

    session = manager.create_game(
        player1_name=request.player1.name,
        player1_type=request.player1.player_type.value,
        player1_deck_id=request.player1.deck_id,
        player2_name=request.player2.name,
        player2_type=request.player2.player_type.value,
        player2_deck_id=request.player2.deck_id,
        auto_play=request.auto_play,
    )

    state = manager.serialize_game_state(session)
    return state


@router.get("", response_model=List[GameSummarySchema])
async def list_games():
    """
    List all active games.

    Returns:
        List of game summaries
    """
    manager = get_game_manager()
    games = manager.get_all_games()

    return [
        GameSummarySchema(
            game_id=session.game_id,
            player1_name=session.game_state.player1.name,
            player2_name=session.game_state.player2.name,
            turn=session.game_state.turn_count,
            phase=session.game_state.phase.name,
            is_terminal=session.game_state.game_over,
            winner=session.game_state.winner.name if session.game_state.winner else None,
            created_at=session.created_at.isoformat(),
        )
        for session in games
    ]


@router.get("/{game_id}", response_model=GameStateSchema)
async def get_game(
    game_id: str,
    player: Optional[int] = Query(None, description="Player index to show hidden info for")
):
    """
    Get the current state of a game.

    Args:
        game_id: Game ID
        player: Optional player index to include hidden info (hand, life cards)

    Returns:
        Current game state
    """
    manager = get_game_manager()
    session = manager.get_game(game_id)

    if not session:
        raise HTTPException(status_code=404, detail="Game not found")

    state = manager.serialize_game_state(session, for_player=player)
    return state


@router.post("/{game_id}/action", response_model=ActionResultSchema)
async def submit_action(game_id: str, action: ActionSchema):
    """
    Submit an action for a game.

    Args:
        game_id: Game ID
        action: Action to perform

    Returns:
        Action result with updated game state
    """
    manager = get_game_manager()
    session = manager.get_game(game_id)

    if not session:
        raise HTTPException(status_code=404, detail="Game not found")

    if session.game_state.game_over:
        raise HTTPException(status_code=400, detail="Game is already over")

    success, message, events = manager.process_action(
        game_id=game_id,
        action_type=action.action_type.value,
        player_index=action.player_index,
        card_index=action.card_index,
        target_index=action.target_index,
        don_amount=action.don_amount,
        card_indices=action.card_indices,
    )

    if not success:
        raise HTTPException(status_code=400, detail=message)

    # Get updated state
    session = manager.get_game(game_id)
    state = manager.serialize_game_state(session, for_player=action.player_index)

    return ActionResultSchema(
        success=success,
        message=message,
        game_state=state,
        events=events,
    )


@router.get("/{game_id}/actions", response_model=List[ActionSchema])
async def get_valid_actions(
    game_id: str,
    player: int = Query(..., description="Player index")
):
    """
    Get valid actions for a player.

    Args:
        game_id: Game ID
        player: Player index

    Returns:
        List of valid actions
    """
    manager = get_game_manager()
    session = manager.get_game(game_id)

    if not session:
        raise HTTPException(status_code=404, detail="Game not found")

    actions = manager.get_valid_actions(game_id, player)
    return actions


@router.post("/{game_id}/run-turn")
async def run_turn(game_id: str):
    """
    Run one full turn (AI vs AI games).

    Args:
        game_id: Game ID

    Returns:
        Updated game state after turn with logs
    """
    manager = get_game_manager()
    session = manager.get_game(game_id)

    if not session:
        raise HTTPException(status_code=404, detail="Game not found")

    if session.game_state.game_over:
        raise HTTPException(status_code=400, detail="Game is already over")

    # Run one turn
    session.game_state.run_turn()

    # Get logs from this turn
    logs = session.game_state.get_and_clear_logs()

    state = manager.serialize_game_state(session)
    return {
        "game_state": state,
        "logs": logs,
    }


@router.post("/{game_id}/run-game")
async def run_game(
    game_id: str,
    max_turns: int = Query(50, description="Maximum turns to run")
):
    """
    Run the entire game until completion (AI vs AI).

    Args:
        game_id: Game ID
        max_turns: Maximum number of turns

    Returns:
        Final game state with logs
    """
    manager = get_game_manager()
    session = manager.get_game(game_id)

    if not session:
        raise HTTPException(status_code=404, detail="Game not found")

    # Run until game ends or max turns
    turns_run = 0
    all_logs = []
    while not session.game_state.game_over and turns_run < max_turns:
        session.game_state.run_turn()
        all_logs.extend(session.game_state.get_and_clear_logs())
        turns_run += 1

    state = manager.serialize_game_state(session)
    return {
        "turns_run": turns_run,
        "game_state": state,
        "logs": all_logs,
    }


@router.delete("/{game_id}")
async def delete_game(game_id: str):
    """
    Delete a game.

    Args:
        game_id: Game ID

    Returns:
        Deletion confirmation
    """
    manager = get_game_manager()

    if not manager.delete_game(game_id):
        raise HTTPException(status_code=404, detail="Game not found")

    return {"message": f"Game {game_id} deleted"}


@router.post("/quick-start")
async def quick_start():
    """
    Quick start a new AI vs AI game with default decks.

    Returns:
        New game state
    """
    manager = get_game_manager()

    session = manager.create_game(
        player1_name="AI Player 1",
        player1_type="AI",
        player1_deck_id="red_luffy",
        player2_name="AI Player 2",
        player2_type="AI",
        player2_deck_id="green_yamato",
        auto_play=True,
    )

    state = manager.serialize_game_state(session)
    return state
