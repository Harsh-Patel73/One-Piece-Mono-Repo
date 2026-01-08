"""
Vinsmoke Engine - FastAPI Application

Main entry point for the web API.
Provides REST endpoints and WebSocket support for the OPTCG game engine.
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from .game_manager import get_game_manager
from .routes import games, cards, training
from .metrics import get_metrics_response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print("Starting Vinsmoke Engine API...")
    manager = get_game_manager()
    print(f"Card database loaded: {len(manager.card_database)} cards")
    yield
    # Shutdown
    print("Shutting down Vinsmoke Engine API...")


# Create FastAPI app
app = FastAPI(
    title="Vinsmoke Engine API",
    description="One Piece Trading Card Game AI Engine",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # React dev server
        "http://localhost:5173",      # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(games.router, prefix="/api/games", tags=["games"])
app.include_router(cards.router, prefix="/api", tags=["cards"])
app.include_router(training.router, prefix="/api/training", tags=["training"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Vinsmoke Engine",
        "version": "0.1.0",
        "description": "One Piece TCG AI Engine API",
        "docs": "/docs",
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    manager = get_game_manager()
    return {
        "status": "healthy",
        "cards_loaded": len(manager.card_database),
        "active_games": len(manager.games),
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return get_metrics_response()


# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, game_id: str):
        """Connect a client to a game."""
        await websocket.accept()
        if game_id not in self.active_connections:
            self.active_connections[game_id] = []
        self.active_connections[game_id].append(websocket)

    def disconnect(self, websocket: WebSocket, game_id: str):
        """Disconnect a client from a game."""
        if game_id in self.active_connections:
            if websocket in self.active_connections[game_id]:
                self.active_connections[game_id].remove(websocket)
            if not self.active_connections[game_id]:
                del self.active_connections[game_id]

    async def broadcast(self, game_id: str, message: dict):
        """Broadcast a message to all clients in a game."""
        if game_id in self.active_connections:
            for connection in self.active_connections[game_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass  # Handle disconnected clients


ws_manager = ConnectionManager()


@app.websocket("/ws/games/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    """
    WebSocket endpoint for real-time game updates.

    Clients connect to receive:
    - Game state updates
    - Action notifications
    - Turn changes
    """
    await ws_manager.connect(websocket, game_id)

    manager = get_game_manager()
    session = manager.get_game(game_id)

    if not session:
        await websocket.send_json({
            "type": "ERROR",
            "data": {"message": "Game not found"}
        })
        ws_manager.disconnect(websocket, game_id)
        return

    # Send initial game state
    state = manager.serialize_game_state(session)
    await websocket.send_json({
        "type": "GAME_STATE",
        "data": state
    })

    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_json()

            if data.get("type") == "ACTION":
                action = data.get("data", {})
                success, message, events = manager.process_action(
                    game_id=game_id,
                    action_type=action.get("action_type"),
                    player_index=action.get("player_index", 0),
                    card_index=action.get("card_index"),
                    target_index=action.get("target_index"),
                    don_amount=action.get("don_amount"),
                    card_indices=action.get("card_indices"),
                )

                # Send result to requesting client
                await websocket.send_json({
                    "type": "ACTION_RESULT",
                    "data": {
                        "success": success,
                        "message": message,
                        "events": events,
                    }
                })

                # Broadcast updated state to all clients
                session = manager.get_game(game_id)
                if session:
                    state = manager.serialize_game_state(session)
                    await ws_manager.broadcast(game_id, {
                        "type": "GAME_STATE",
                        "data": state
                    })

            elif data.get("type") == "GET_STATE":
                session = manager.get_game(game_id)
                if session:
                    state = manager.serialize_game_state(session)
                    await websocket.send_json({
                        "type": "GAME_STATE",
                        "data": state
                    })

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, game_id)


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the API server."""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
