# API module - FastAPI web server
from .main import app
from .game_manager import GameManager, get_game_manager

__all__ = ['app', 'GameManager', 'get_game_manager']
