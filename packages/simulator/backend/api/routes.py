"""
REST API routes for the OPTCG Simulator.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import random
import string
from pathlib import Path

from game.card_loader import load_card_database

router = APIRouter()

# Load card database at startup
CARD_DB_PATH = Path(__file__).parent.parent / "data" / "cards.json"
CARD_DB = {}

try:
    CARD_DB = load_card_database(str(CARD_DB_PATH))
except Exception as e:
    print(f"[ERROR] Failed to load card database: {e}")


class CreateRoomRequest(BaseModel):
    player_name: str
    deck_id: Optional[str] = None


class JoinRoomRequest(BaseModel):
    room_code: str
    player_name: str
    deck_id: Optional[str] = None


class StartAIGameRequest(BaseModel):
    player_name: str
    deck_id: Optional[str] = None
    ai_difficulty: str = "medium"  # easy, medium, hard


def generate_room_code() -> str:
    """Generate a 6-character room code."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


# ============================================================================
# Room Management
# ============================================================================

@router.post("/rooms/create")
async def create_room(request: CreateRoomRequest):
    """Create a new game room and get a room code."""
    room_code = generate_room_code()
    return {
        "room_code": room_code,
        "player_name": request.player_name,
        "status": "waiting",
        "message": f"Room created! Share code {room_code} with your opponent.",
    }


@router.post("/rooms/join")
async def join_room(request: JoinRoomRequest):
    """Join an existing room with a code."""
    # TODO: Validate room exists
    return {
        "room_code": request.room_code,
        "player_name": request.player_name,
        "status": "joined",
        "message": "Successfully joined the room!",
    }


@router.get("/rooms/{room_code}")
async def get_room_status(room_code: str):
    """Get the status of a room."""
    # TODO: Get actual room status from GameManager
    return {
        "room_code": room_code,
        "players": [],
        "status": "waiting",
    }


# ============================================================================
# AI Games
# ============================================================================

@router.post("/game/vs-ai")
async def start_ai_game(request: StartAIGameRequest):
    """Start a game against the AI."""
    game_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=12))
    return {
        "game_id": game_id,
        "player_name": request.player_name,
        "opponent": "Vinsmoke AI",
        "difficulty": request.ai_difficulty,
        "status": "starting",
    }


# ============================================================================
# Decks
# ============================================================================

@router.get("/decks")
async def list_decks():
    """List available pre-built decks."""
    return {
        "decks": [
            {"id": "starter_luffy", "name": "Straw Hat Pirates", "leader": "Monkey D. Luffy"},
            {"id": "starter_law", "name": "Heart Pirates", "leader": "Trafalgar Law"},
            {"id": "starter_kid", "name": "Kid Pirates", "leader": "Eustass Kid"},
            {"id": "starter_kaido", "name": "Beast Pirates", "leader": "Kaido"},
        ]
    }


@router.get("/decks/{deck_id}")
async def get_deck(deck_id: str):
    """Get a specific deck's card list."""
    # TODO: Return actual deck data
    return {
        "id": deck_id,
        "name": "Sample Deck",
        "cards": [],
    }


# ============================================================================
# Cards
# ============================================================================

@router.get("/cards")
async def list_cards(
    color: Optional[str] = None,
    card_type: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 500,
    offset: int = 0,
):
    """Search and filter cards."""
    cards = list(CARD_DB.values())

    # Filter by card_type (LEADER, CHARACTER, EVENT, STAGE)
    if card_type:
        cards = [c for c in cards if c.card_type.upper() == card_type.upper()]

    # Filter by color (supports comma-separated for multiple colors)
    if color:
        color_list = [c.strip().capitalize() for c in color.split(",")]
        cards = [c for c in cards if any(col in c.colors for col in color_list)]

    # Search by ID or name
    if search:
        search_lower = search.lower()
        cards = [c for c in cards if search_lower in c.name.lower() or search_lower in c.id.lower()]

    total = len(cards)

    # Apply pagination
    paginated_cards = cards[offset:offset + limit]

    return {
        "cards": [c.to_dict() for c in paginated_cards],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/cards/{card_id}")
async def get_card(card_id: str):
    """Get a specific card's details."""
    # Try direct lookup by id_normal first
    card = CARD_DB.get(card_id)

    # If not found, try to find by full id (with variant suffix like _p1)
    if not card:
        for c in CARD_DB.values():
            if c.id == card_id:
                card = c
                break

    if not card:
        raise HTTPException(404, "Card not found")
    return card.to_dict()
