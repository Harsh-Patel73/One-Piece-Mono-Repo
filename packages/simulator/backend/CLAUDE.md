# OPTCG Simulator Backend - Claude Code Context

## Project Overview
This is the backend for the One Piece Trading Card Game (OPTCG) Simulator. It's a FastAPI + Socket.IO application providing the game engine, API, and real-time multiplayer functionality.

## Tech Stack
- **Framework:** FastAPI 0.104
- **Real-time:** python-socketio 5.10
- **ASGI Server:** Uvicorn 0.24
- **Validation:** Pydantic 2.5
- **ML (optional):** PyTorch 2.x, NumPy

## Directory Structure
```
backend/
├── main.py              # FastAPI app entry point, Socket.IO setup
├── api/
│   ├── __init__.py
│   └── routes.py        # REST API endpoints (/api/cards, /api/decks, etc.)
├── game/
│   ├── __init__.py
│   ├── engine.py        # Core game logic (Player, GameState classes)
│   ├── manager.py       # GameManager - room/game session management
│   ├── card_loader.py   # Load cards from JSON database
│   ├── deck_loader.py   # Load deck definitions
│   ├── effects.py       # Effect parsing and types
│   ├── resolver.py      # Effect resolution engine
│   ├── hardcoded.py     # Complex card effects with custom logic
│   └── models/
│       ├── __init__.py
│       ├── cards.py     # Card data model
│       └── enums.py     # GamePhase, CardType enums
├── realtime/
│   ├── __init__.py
│   └── socket_handlers.py  # Socket.IO event handlers
├── data/
│   ├── cards.json       # Full card database
│   └── decks/           # Pre-built deck definitions
│       ├── red_luffy.json
│       └── green_yamato.json
├── requirements.txt
└── Dockerfile
```

## Key Commands
```bash
# Development server (port 8080)
python -m uvicorn main:socket_app --host 0.0.0.0 --port 8080 --reload

# Or using the default in main.py (port 8001)
python main.py
```

## Game Engine Architecture

### Core Classes (game/engine.py)

**Player**
- Manages deck, hand, field, life cards, DON pool, trash
- Handles mulligan, drawing, blocking, DON spending
- Key methods: `draw_card()`, `spend_don()`, `attach_don_to_card()`, `reset_for_turn()`

**GameState**
- Manages turn flow, phases, combat resolution
- Tracks current/opponent player, pending attacks
- Key methods: `play_card()`, `declare_attack()`, `respond_blocker()`, `respond_counter()`

### Game Phases (game/models/enums.py)
```
MULLIGAN → REFRESH → DRAW → DON → MAIN → BLOCKER_STEP → COUNTER_STEP → DAMAGE_STEP → GAME_OVER
```

### Combat Flow
1. `declare_attack(attacker_idx, target_idx)` - Start attack, enter BLOCKER_STEP
2. `respond_blocker(blocker_idx)` - Defender may activate blocker, enter COUNTER_STEP
3. `respond_counter(counter_indices)` - Defender uses counter cards from hand
4. `_resolve_attack()` - Compare power, deal damage/KO, handle triggers

### Game Constants
```python
MAX_DON = 10
DON_PER_TURN = 2
STARTING_DON_P1 = 1
STARTING_DON_P2 = 2
MAX_FIELD_CHARACTERS = 5
```

### Card Keywords
The engine recognizes these keywords in card effect text:
- `[Rush]` - Can attack the turn it's played
- `[Blocker]` - Can intercept attacks when active
- `[Banish]` - Life damage goes to trash instead of hand
- `[Double Attack]` - Deals 2 life damage on successful leader hit

## GameManager (game/manager.py)

Manages multiplayer sessions:
- **Rooms:** Lobby system with room codes
- **Games:** Active game instances with player sessions
- **AI Games:** Single-player vs AI opponent

Key tracking dictionaries:
- `rooms: Dict[str, Room]` - Active lobbies
- `games: Dict[str, ActiveGame]` - Active games
- `player_to_room: Dict[str, str]` - Socket ID → Room code
- `player_to_game: Dict[str, str]` - Socket ID → Game ID

## API Endpoints (api/routes.py)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/cards` | GET | List all cards (paginated) |
| `/api/cards/{id}` | GET | Get single card |
| `/api/decks` | GET | List saved decks |
| `/api/decks` | POST | Save a deck |
| `/api/decks/{id}` | GET | Load a deck |

## Socket.IO Events (realtime/socket_handlers.py)

**Client → Server:**
- `join_room` - Join multiplayer lobby
- `create_room` - Create new lobby
- `start_game` - Begin game from lobby
- `game_action` - Play card, attack, etc.

**Server → Client:**
- `room_update` - Lobby state changed
- `game_state` - Full game state update
- `game_logs` - Action log messages

## Effect System

### Effect Timing (game/effects.py)
- `ON_PLAY` - When card enters play
- `WHEN_ATTACKING` - When declaring attack
- `ON_KO` - When card is KO'd
- `ACTIVATE_MAIN` - Manual activation during main phase

### Effect Resolution
1. **Hardcoded effects** (game/hardcoded.py) - Complex cards with custom Python logic
2. **Parsed effects** (game/resolver.py) - Standard effects parsed from card text

## Card Data Model (game/models/cards.py)

```python
class Card:
    id: str
    name: str
    card_type: str  # LEADER, CHARACTER, EVENT, STAGE
    cost: int
    power: int
    counter: int
    life: int  # Leaders only
    colors: List[str]
    effect: str
    trigger: str
    image_link: str

    # Runtime state
    is_resting: bool
    has_attacked: bool
    attached_don: int
    played_turn: int
```

## Common Development Tasks

### Adding a new card effect
1. For simple effects: Parse in `game/effects.py`, resolve in `game/resolver.py`
2. For complex effects: Add to `game/hardcoded.py` with card ID mapping

### Adding a new API endpoint
1. Add route in `api/routes.py`
2. Include router is already done in `main.py`

### Adding a new Socket.IO event
1. Add handler in `realtime/socket_handlers.py`
2. Use `@sio.event` decorator

## Testing
The backend can be tested via:
- REST API: `curl http://localhost:8080/api/cards`
- Health check: `curl http://localhost:8080/health`
- Socket.IO: Connect from frontend or test client

## Known Engine Bugs & Fixes

### Zero-cost card DON spending (fixed 2026-03-31)
**File:** `packages/game-engine/optcg_engine/game_engine.py` — `play_card()` DON spending loop  
**Symptom:** Playing a card whose cost was reduced to 0 by a `cost_modifier` (e.g. Crocodile OP01-067 giving Blue Events -1 cost) would rest ALL active DON instead of none.  
**Root cause:** The loop used `if used == cost: break` as the exit condition. When `cost=0`, `used` starts at 0 but only increments after spending DON — so `used == 0` is only true before any DON is spent, and the break never fires inside the loop body.  
**Fix:** Changed to `if used >= cost: break` at the TOP of the loop (before spending), so cost=0 exits immediately.  
**Pattern to watch:** Any DON spending loop must guard with `used >= cost` (not `==`) before spending, or wrap the entire loop in `if cost > 0:`.

## Dependencies
- FastAPI + Uvicorn for HTTP/WebSocket
- python-socketio for real-time game events
- Pydantic for data validation
- PyTorch (optional) for AI training integration
