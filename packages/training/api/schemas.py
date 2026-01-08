"""
Pydantic schemas for the Vinsmoke Engine API.

Defines request/response models for all API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class GamePhaseSchema(str, Enum):
    """Game phase for API responses."""
    MULLIGAN = "MULLIGAN"
    REFRESH = "REFRESH"
    DRAW = "DRAW"
    DON = "DON"
    MAIN = "MAIN"
    END = "END"
    ATTACK_DECLARATION = "ATTACK_DECLARATION"
    BLOCKER_STEP = "BLOCKER_STEP"
    COUNTER_STEP = "COUNTER_STEP"
    DAMAGE_STEP = "DAMAGE_STEP"
    GAME_OVER = "GAME_OVER"


class ActionTypeSchema(str, Enum):
    """Action types for API requests."""
    PASS = "PASS"
    PASS_TURN = "PASS_TURN"
    MULLIGAN = "MULLIGAN"
    KEEP_HAND = "KEEP_HAND"
    PLAY_CARD = "PLAY_CARD"
    ATTACH_DON = "ATTACH_DON"
    ATTACK = "ATTACK"
    ACTIVATE_BLOCKER = "ACTIVATE_BLOCKER"
    USE_COUNTER = "USE_COUNTER"
    DECLINE_BLOCK = "DECLINE_BLOCK"
    DISCARD = "DISCARD"
    ACTIVATE_EFFECT = "ACTIVATE_EFFECT"


class PlayerType(str, Enum):
    """Player type for game creation."""
    HUMAN = "HUMAN"
    AI = "AI"


# ============================================================================
# Card Schemas
# ============================================================================

class CardSchema(BaseModel):
    """Card data for API responses."""
    id: str
    name: str
    card_type: str
    cost: Optional[int] = None
    power: Optional[int] = None
    counter: Optional[int] = None
    colors: List[str] = []
    life: Optional[int] = None
    effect: Optional[str] = None
    trigger: Optional[str] = None
    image_link: Optional[str] = None
    attribute: Optional[str] = None
    card_origin: Optional[str] = None

    class Config:
        from_attributes = True


class CardInstanceSchema(BaseModel):
    """Card instance with runtime state."""
    card: CardSchema
    instance_id: int
    is_resting: bool = False
    has_attacked: bool = False
    attached_don: int = 0
    played_turn: Optional[int] = None
    power_modifier: int = 0

    # Keywords
    has_rush: bool = False
    has_blocker: bool = False
    has_banish: bool = False
    has_double_attack: bool = False

    @property
    def total_power(self) -> int:
        base = self.card.power or 0
        return base + (self.attached_don * 1000) + self.power_modifier


# ============================================================================
# Player Schemas
# ============================================================================

class PlayerStateSchema(BaseModel):
    """Player state for API responses."""
    player_index: int
    name: str
    leader: Dict[str, Any]  # Card data as dict for flexibility
    life_count: int
    hand_count: int
    deck_count: int
    field: List[Dict[str, Any]] = []  # Card data as dicts
    trash_count: int
    don_active: int
    don_rested: int
    total_don: int

    # Only included for the requesting player
    hand: Optional[List[Dict[str, Any]]] = None
    life_cards: Optional[List[Dict[str, Any]]] = None

    class Config:
        extra = "allow"


class PlayerCreateSchema(BaseModel):
    """Schema for creating a player in a game."""
    name: str
    player_type: PlayerType = PlayerType.AI
    deck_id: Optional[str] = None  # Use a predefined deck
    leader_id: Optional[str] = None
    deck_cards: Optional[List[str]] = None  # Custom deck card IDs


# ============================================================================
# Game Schemas
# ============================================================================

class GameCreateRequest(BaseModel):
    """Request to create a new game."""
    player1: PlayerCreateSchema
    player2: PlayerCreateSchema
    auto_play: bool = False  # If True, AI will play automatically


class GameStateSchema(BaseModel):
    """Complete game state for API responses."""
    game_id: str
    turn: int
    phase: GamePhaseSchema
    active_player: int
    players: List[PlayerStateSchema]
    is_terminal: bool
    winner: Optional[int] = None
    last_action: Optional[str] = None
    valid_actions: Optional[List['ActionSchema']] = None


class GameSummarySchema(BaseModel):
    """Summary of a game for listing."""
    game_id: str
    player1_name: str
    player2_name: str
    turn: int
    phase: GamePhaseSchema
    is_terminal: bool
    winner: Optional[str] = None
    created_at: str


# ============================================================================
# Action Schemas
# ============================================================================

class ActionSchema(BaseModel):
    """Action request schema."""
    action_type: ActionTypeSchema
    player_index: int

    # Optional parameters based on action type
    card_index: Optional[int] = None
    target_index: Optional[int] = None
    don_amount: Optional[int] = None
    card_indices: Optional[List[int]] = None
    effect_index: Optional[int] = None
    target_indices: Optional[List[int]] = None


class ActionResultSchema(BaseModel):
    """Result of an action."""
    success: bool
    message: str = ""
    game_state: Optional[GameStateSchema] = None
    events: List[str] = []  # List of events that occurred


# ============================================================================
# Deck Schemas
# ============================================================================

class DeckSchema(BaseModel):
    """Deck data."""
    id: str
    name: str
    leader_id: str
    leader_name: str
    card_count: int
    colors: List[str]


class DeckDetailSchema(BaseModel):
    """Detailed deck with card list."""
    id: str
    name: str
    leader: CardSchema
    cards: List[CardSchema]
    card_counts: Dict[str, int]  # card_id -> count


class DeckCreateRequest(BaseModel):
    """Request to create a custom deck."""
    name: str
    leader_id: str
    cards: Dict[str, int]  # card_id -> count


# ============================================================================
# WebSocket Schemas
# ============================================================================

class WSMessageType(str, Enum):
    """WebSocket message types."""
    GAME_STATE = "GAME_STATE"
    ACTION = "ACTION"
    ACTION_RESULT = "ACTION_RESULT"
    ERROR = "ERROR"
    PLAYER_JOINED = "PLAYER_JOINED"
    PLAYER_LEFT = "PLAYER_LEFT"
    GAME_STARTED = "GAME_STARTED"
    GAME_ENDED = "GAME_ENDED"
    TURN_CHANGED = "TURN_CHANGED"
    PHASE_CHANGED = "PHASE_CHANGED"


class WSMessage(BaseModel):
    """WebSocket message wrapper."""
    type: WSMessageType
    data: Dict[str, Any]
    timestamp: Optional[str] = None


# ============================================================================
# AI Schemas
# ============================================================================

class AIConfigSchema(BaseModel):
    """AI configuration."""
    model_path: Optional[str] = None  # Path to trained model
    mcts_simulations: int = 100
    temperature: float = 1.0
    use_random: bool = False  # Use random AI instead of trained


class TrainingConfigSchema(BaseModel):
    """Training configuration."""
    num_games: int = 100
    batch_size: int = 32
    learning_rate: float = 0.001
    mcts_simulations: int = 50
    checkpoint_interval: int = 10


class TrainingStatusSchema(BaseModel):
    """Training status."""
    is_training: bool
    games_completed: int
    total_games: int
    current_loss: Optional[float] = None
    best_model_path: Optional[str] = None


# ============================================================================
# Response Wrappers
# ============================================================================

class APIResponse(BaseModel):
    """Standard API response wrapper."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Paginated response for lists."""
    items: List[Any]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_prev: bool


# Update forward references
GameStateSchema.model_rebuild()
