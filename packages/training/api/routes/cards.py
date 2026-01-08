"""
Card and deck routes for Vinsmoke Engine API.

Handles card database queries and deck management.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pathlib import Path
import json

from ..schemas import CardSchema, DeckSchema, DeckDetailSchema, PaginatedResponse
from ..game_manager import get_game_manager

router = APIRouter()


@router.get("/cards", response_model=PaginatedResponse)
async def list_cards(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    card_type: Optional[str] = Query(None, description="Filter by card type"),
    color: Optional[str] = Query(None, description="Filter by color"),
    search: Optional[str] = Query(None, description="Search by name"),
    cost_min: Optional[int] = Query(None, description="Minimum cost"),
    cost_max: Optional[int] = Query(None, description="Maximum cost"),
):
    """
    List cards with pagination and filtering.

    Args:
        page: Page number (1-indexed)
        page_size: Number of cards per page
        card_type: Filter by card type (LEADER, CHARACTER, EVENT, STAGE)
        color: Filter by color
        search: Search by card name
        cost_min: Minimum cost filter
        cost_max: Maximum cost filter

    Returns:
        Paginated list of cards
    """
    manager = get_game_manager()

    # Filter cards
    cards = list(manager.card_database.values())

    if card_type:
        cards = [c for c in cards if c.card_type.upper() == card_type.upper()]

    if color:
        cards = [c for c in cards if color.upper() in [col.upper() for col in (c.colors or [])]]

    if search:
        search_lower = search.lower()
        cards = [c for c in cards if search_lower in c.name.lower()]

    if cost_min is not None:
        cards = [c for c in cards if (c.cost or 0) >= cost_min]

    if cost_max is not None:
        cards = [c for c in cards if (c.cost or 0) <= cost_max]

    # Sort by ID
    cards.sort(key=lambda c: c.id)

    # Paginate
    total = len(cards)
    start = (page - 1) * page_size
    end = start + page_size
    page_cards = cards[start:end]

    return PaginatedResponse(
        items=[
            CardSchema(
                id=c.id,
                name=c.name,
                card_type=c.card_type,
                cost=c.cost,
                power=c.power,
                counter=c.counter,
                colors=c.colors or [],
                life=c.life,
                effect=c.effect,
                trigger=c.trigger,
                image_link=c.image_link,
                attribute=c.attribute,
                card_origin=c.card_origin,
            )
            for c in page_cards
        ],
        total=total,
        page=page,
        page_size=page_size,
        has_next=end < total,
        has_prev=page > 1,
    )


@router.get("/cards/{card_id}", response_model=CardSchema)
async def get_card(card_id: str):
    """
    Get a specific card by ID.

    Args:
        card_id: Card ID

    Returns:
        Card details
    """
    manager = get_game_manager()
    card = manager.card_database.get(card_id)

    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    return CardSchema(
        id=card.id,
        name=card.name,
        card_type=card.card_type,
        cost=card.cost,
        power=card.power,
        counter=card.counter,
        colors=card.colors or [],
        life=card.life,
        effect=card.effect,
        trigger=card.trigger,
        image_link=card.image_link,
        attribute=card.attribute,
        card_origin=card.card_origin,
    )


@router.get("/cards/search/{query}")
async def search_cards(
    query: str,
    limit: int = Query(20, ge=1, le=100),
):
    """
    Search cards by name.

    Args:
        query: Search query
        limit: Maximum results to return

    Returns:
        List of matching cards
    """
    manager = get_game_manager()
    query_lower = query.lower()

    matches = []
    for card in manager.card_database.values():
        if query_lower in card.name.lower():
            matches.append(CardSchema(
                id=card.id,
                name=card.name,
                card_type=card.card_type,
                cost=card.cost,
                power=card.power,
                counter=card.counter,
                colors=card.colors or [],
                life=card.life,
                effect=card.effect,
                trigger=card.trigger,
                image_link=card.image_link,
                attribute=card.attribute,
                card_origin=card.card_origin,
            ))
            if len(matches) >= limit:
                break

    return matches


@router.get("/decks", response_model=List[DeckSchema])
async def list_decks():
    """
    List available decks.

    Returns:
        List of deck summaries
    """
    decks_dir = Path(__file__).parent.parent.parent / "decks"
    decks = []

    manager = get_game_manager()

    for deck_file in decks_dir.glob("*.json"):
        if deck_file.name.startswith("__"):
            continue

        try:
            with open(deck_file, 'r', encoding='utf-8') as f:
                deck_data = json.load(f)

            leader_id = deck_data.get("leader")
            leader = manager.card_database.get(leader_id)

            card_count = sum(deck_data.get("cards", {}).values())

            # Get colors from leader
            colors = leader.colors if leader else []

            decks.append(DeckSchema(
                id=deck_file.stem,
                name=deck_file.stem.replace("_", " ").title(),
                leader_id=leader_id,
                leader_name=leader.name if leader else "Unknown",
                card_count=card_count,
                colors=colors,
            ))
        except Exception as e:
            print(f"Error loading deck {deck_file}: {e}")

    return decks


@router.get("/decks/{deck_id}", response_model=DeckDetailSchema)
async def get_deck(deck_id: str):
    """
    Get detailed deck information.

    Args:
        deck_id: Deck ID (filename without extension)

    Returns:
        Detailed deck info with card list
    """
    deck_file = Path(__file__).parent.parent.parent / "decks" / f"{deck_id}.json"

    if not deck_file.exists():
        raise HTTPException(status_code=404, detail="Deck not found")

    manager = get_game_manager()

    try:
        with open(deck_file, 'r', encoding='utf-8') as f:
            deck_data = json.load(f)

        leader_id = deck_data.get("leader")
        leader = manager.card_database.get(leader_id)

        if not leader:
            raise HTTPException(status_code=404, detail="Leader card not found")

        # Get all cards
        cards = []
        card_counts = deck_data.get("cards", {})

        for card_id, count in card_counts.items():
            card = manager.card_database.get(card_id)
            if card:
                for _ in range(count):
                    cards.append(CardSchema(
                        id=card.id,
                        name=card.name,
                        card_type=card.card_type,
                        cost=card.cost,
                        power=card.power,
                        counter=card.counter,
                        colors=card.colors or [],
                        life=card.life,
                        effect=card.effect,
                        trigger=card.trigger,
                        image_link=card.image_link,
                        attribute=card.attribute,
                        card_origin=card.card_origin,
                    ))

        return DeckDetailSchema(
            id=deck_id,
            name=deck_id.replace("_", " ").title(),
            leader=CardSchema(
                id=leader.id,
                name=leader.name,
                card_type=leader.card_type,
                cost=leader.cost,
                power=leader.power,
                counter=leader.counter,
                colors=leader.colors or [],
                life=leader.life,
                effect=leader.effect,
                trigger=leader.trigger,
                image_link=leader.image_link,
                attribute=leader.attribute,
                card_origin=leader.card_origin,
            ),
            cards=cards,
            card_counts=card_counts,
        )
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid deck file")


@router.get("/leaders", response_model=List[CardSchema])
async def list_leaders():
    """
    List all leader cards.

    Returns:
        List of leader cards
    """
    manager = get_game_manager()

    leaders = [
        CardSchema(
            id=card.id,
            name=card.name,
            card_type=card.card_type,
            cost=card.cost,
            power=card.power,
            counter=card.counter,
            colors=card.colors or [],
            life=card.life,
            effect=card.effect,
            trigger=card.trigger,
            image_link=card.image_link,
            attribute=card.attribute,
            card_origin=card.card_origin,
        )
        for card in manager.card_database.values()
        if card.card_type.upper() == 'LEADER'
    ]

    # Sort by name
    leaders.sort(key=lambda c: c.name)

    return leaders


@router.get("/stats")
async def get_stats():
    """
    Get card database statistics.

    Returns:
        Statistics about the card database
    """
    manager = get_game_manager()

    cards = list(manager.card_database.values())

    # Count by type
    type_counts = {}
    for card in cards:
        card_type = card.card_type.upper()
        type_counts[card_type] = type_counts.get(card_type, 0) + 1

    # Count by color
    color_counts = {}
    for card in cards:
        for color in (card.colors or []):
            color_counts[color] = color_counts.get(color, 0) + 1

    return {
        "total_cards": len(cards),
        "by_type": type_counts,
        "by_color": color_counts,
    }
