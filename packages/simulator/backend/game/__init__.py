# Game logic module for OPTCG Simulator

# Import from unified optcg_engine
import sys
from pathlib import Path
game_engine_path = Path(__file__).parent.parent.parent.parent / "game-engine"
sys.path.insert(0, str(game_engine_path))
from optcg_engine.game_engine import GameState, Player

from .models import Card, GamePhase, CardType, Color
from .card_loader import load_card_database, get_card_by_id
from .deck_loader import load_deck, get_available_decks

__all__ = [
    'GameState',
    'Player',
    'Card',
    'GamePhase',
    'CardType',
    'Color',
    'load_card_database',
    'get_card_by_id',
    'load_deck',
    'get_available_decks',
]
