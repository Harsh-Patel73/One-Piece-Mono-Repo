"""
OPTCG Simulator - One Piece Trading Card Game Simulator
Play against AI or other players in real-time.
"""

import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio

from api.routes import router as api_router
from game.manager import GameManager
from realtime.socket_handlers import setup_socket_handlers

# Create FastAPI app
app = FastAPI(
    title="OPTCG Simulator",
    description="One Piece Trading Card Game Simulator - Play against AI or friends",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Socket.IO for real-time gameplay
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
)

# Game manager (singleton)
game_manager = GameManager()

# Setup socket handlers
setup_socket_handlers(sio, game_manager)

# Mount Socket.IO
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

# Include API routes
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "name": "OPTCG Simulator",
        "version": "1.0.0",
        "status": "online",
        "features": [
            "Play vs AI",
            "Play vs Friends (Room Codes)",
            "Deck Builder",
            "All Cards Supported",
        ],
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "active_games": game_manager.active_game_count,
        "active_rooms": game_manager.active_room_count,
    }


if __name__ == "__main__":
    port = int(os.getenv("OPTCG_SIMULATOR_BACKEND_PORT", "8000"))
    reload_enabled = os.getenv("OPTCG_SIMULATOR_BACKEND_RELOAD", "").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    uvicorn.run("main:socket_app", host="0.0.0.0", port=port, reload=reload_enabled)
