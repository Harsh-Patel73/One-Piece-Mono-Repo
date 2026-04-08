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


@router.get("/effect-test/queue")
async def effect_test_queue(set_code: str = "OP01"):
    """Return cards for a set with their current CARD_STATUS.md status."""
    from pathlib import Path
    import re

    set_code = set_code.upper()
    status_path = (
        Path(__file__).parent.parent.parent.parent
        / "game-engine"
        / "optcg_engine"
        / "effects"
        / "CARD_STATUS.md"
    )

    statuses: dict[str, dict] = {}
    if status_path.exists():
        text = status_path.read_text(encoding="utf-8")
        for line in text.splitlines():
            if not line.startswith("|"):
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 5:
                continue
            card_id_cell = parts[1]
            if not re.match(r"[A-Z0-9]+-\d+", card_id_cell):
                continue
            statuses[card_id_cell] = {
                "status": parts[2],
                "name": parts[3],
                "notes": parts[4] if len(parts) > 4 else "",
            }

    # Pull cards for the set from the database (search by set prefix)
    prefix = set_code.lower() + "-"
    cards = [
        c for c in CARD_DB.values()
        if (c.id or "").lower().startswith(prefix)
        or (getattr(c, "id_normal", None) or "").lower().startswith(prefix)
    ]
    cards.sort(key=lambda c: c.id or "")

    result = []
    seen = set()
    for c in cards:
        cid = getattr(c, "id_normal", None) or c.id or ""
        if not cid or cid in seen:
            continue
        seen.add(cid)
        info = statuses.get(cid, {})
        result.append({
            "id": cid,
            "name": c.name,
            "card_type": c.card_type,
            "cost": c.cost,
            "power": c.power,
            "status": info.get("status", "🔲 To Do"),
            "notes": info.get("notes", ""),
            "effect": c.effect,
            "trigger": c.trigger,
        })

    return {"cards": result, "set_code": set_code, "total": len(result)}


@router.post("/effect-test/verdict")
async def submit_verdict(data: dict):
    """Update a card's status in CARD_STATUS.md."""
    import re
    from pathlib import Path

    card_id = (data.get("card_id") or "").upper()
    verdict = data.get("verdict", "skip")
    note = data.get("note", "")

    STATUS_MAP = {
        "pass": "✅ Verified",
        "fail": "⚠ Needs Fix",
        "skip": "🔲 To Do",
    }
    new_status = STATUS_MAP.get(verdict, "🔲 To Do")

    status_path = (
        Path(__file__).parent.parent.parent.parent
        / "game-engine"
        / "optcg_engine"
        / "effects"
        / "CARD_STATUS.md"
    )
    if not status_path.exists():
        return {"ok": False, "error": "CARD_STATUS.md not found"}

    text = status_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    updated = False
    for i, line in enumerate(lines):
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 3 and parts[1] == card_id:
            parts[2] = new_status
            if note and len(parts) >= 5:
                parts[4] = note
            lines[i] = "| " + " | ".join(parts[1:-1]) + " |"
            updated = True
            break

    if not updated:
        # Card not in CARD_STATUS.md yet — find or create the set section and add it
        set_code = re.match(r"([A-Z]+\d+)", card_id)
        set_prefix = set_code.group(1) if set_code else ""
        card_type = ""
        card_obj = CARD_DB.get(card_id)
        if card_obj:
            card_type = getattr(card_obj, "card_type", "") or ""
        new_row = f"| {card_id} | {new_status} | {card_type} | {note} |"

        # Find the right section to insert into
        section_header = f"# Card Effect Status — {set_prefix}"
        section_idx = None
        for i, line in enumerate(lines):
            if section_header in line:
                section_idx = i
                break

        if section_idx is not None:
            # Find the last table row in this section
            insert_at = section_idx + 1
            for i in range(section_idx + 1, len(lines)):
                if lines[i].startswith("| "):
                    parts_check = [p.strip() for p in lines[i].split("|")]
                    if len(parts_check) >= 3 and re.match(r"[A-Z0-9]+-\d+", parts_check[1]):
                        insert_at = i + 1
                    elif parts_check[1] in ("ID", "----", "---"):
                        insert_at = i + 1
                elif lines[i].strip() == "" or lines[i].startswith("#") or lines[i].startswith("**") or lines[i].startswith("---"):
                    break
            lines.insert(insert_at, new_row)
        else:
            # No section for this set yet — create one at end of file
            lines.append("")
            lines.append(f"# Card Effect Status — {set_prefix}")
            lines.append("")
            lines.append("| ID | Status | Type | Notes |")
            lines.append("|----|--------|------|-------|")
            lines.append(new_row)
        updated = True

    if updated:
        status_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # For fail verdicts, append to PENDING_FIXES.jsonl so the fix loop can act on it
    if verdict == "fail" and note:
        import json as _json
        import datetime
        fixes_path = (
            Path(__file__).parent.parent.parent.parent
            / "game-engine"
            / "optcg_engine"
            / "effects"
            / "PENDING_FIXES.jsonl"
        )
        entry = {
            "card_id": card_id,
            "note": note,
            "submitted_at": datetime.datetime.utcnow().isoformat(),
            "fixed_at": None,
        }
        with fixes_path.open("a", encoding="utf-8") as f:
            f.write(_json.dumps(entry) + "\n")
        print(f"[FIX NEEDED] {card_id}: {note}")

    return {"ok": updated, "card_id": card_id, "new_status": new_status}


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
