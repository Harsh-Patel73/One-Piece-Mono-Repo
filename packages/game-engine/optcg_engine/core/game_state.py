"""
Immutable game state for One Piece TCG.

This module defines immutable state classes that are suitable for:
1. Neural network input encoding
2. MCTS tree search
3. Game replay/history

All state modifications return new state objects rather than mutating.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, FrozenSet
from copy import deepcopy
import random

from models.enums import GamePhase, CardType
from models.cards import Card


@dataclass
class CardInstance:
    """
    Runtime instance of a card with game state.

    Wraps a Card definition with instance-specific state
    (resting, DON attached, etc.)
    """
    card: Card
    instance_id: int  # Unique ID for this instance

    # Runtime state
    is_resting: bool = False
    has_attacked: bool = False
    attached_don: int = 0
    played_turn: Optional[int] = None
    power_modifier: int = 0  # Temporary power changes

    # Parsed keywords (cached from effect text)
    has_rush: bool = False
    has_blocker: bool = False
    has_banish: bool = False
    has_double_attack: bool = False

    def __post_init__(self):
        """Parse keywords from card effect."""
        effect = self.card.effect or ''
        self.has_rush = '[Rush]' in effect
        self.has_blocker = '[Blocker]' in effect
        self.has_banish = '[Banish]' in effect
        self.has_double_attack = '[Double Attack]' in effect

    @property
    def total_power(self) -> int:
        """
        Calculate total power including DON and modifiers.

        NOTE: This always includes DON bonus regardless of turn.
        For accurate combat power, use get_power() with active_turn parameter.
        """
        base = self.card.power or 0
        don_bonus = self.attached_don * 1000
        return base + don_bonus + self.power_modifier

    def get_power(self, is_active_turn: bool = True) -> int:
        """
        Calculate power with proper DON activation rules.

        DON attached to a card only provides power during the controller's turn.

        Args:
            is_active_turn: True if this card's controller is the active player

        Returns:
            Total power including DON (if active) and modifiers
        """
        base = self.card.power or 0
        don_bonus = (self.attached_don * 1000) if is_active_turn else 0
        return base + don_bonus + self.power_modifier

    @property
    def name(self) -> str:
        return self.card.name

    @property
    def cost(self) -> Optional[int]:
        return self.card.cost

    @property
    def counter(self) -> Optional[int]:
        return self.card.counter

    @property
    def card_type(self) -> str:
        return self.card.card_type

    def copy(self, **changes) -> 'CardInstance':
        """Create a copy with optional changes."""
        return CardInstance(
            card=self.card,
            instance_id=self.instance_id,
            is_resting=changes.get('is_resting', self.is_resting),
            has_attacked=changes.get('has_attacked', self.has_attacked),
            attached_don=changes.get('attached_don', self.attached_don),
            played_turn=changes.get('played_turn', self.played_turn),
            power_modifier=changes.get('power_modifier', self.power_modifier),
            has_rush=self.has_rush,
            has_blocker=self.has_blocker,
            has_banish=self.has_banish,
            has_double_attack=self.has_double_attack,
        )


@dataclass
class PlayerState:
    """
    Immutable state for a single player.
    """
    player_index: int  # 0 or 1
    name: str

    # Cards
    leader: CardInstance
    life_cards: Tuple[CardInstance, ...]
    hand: Tuple[CardInstance, ...]
    field: Tuple[CardInstance, ...]  # Characters in play (max 5)
    trash: Tuple[CardInstance, ...]
    deck_size: int  # Don't expose deck contents (hidden info)

    # DON pool
    don_active: int = 0
    don_rested: int = 0

    # Mulligan tracking
    has_mulliganed: bool = False

    @property
    def total_don(self) -> int:
        """Total DON in pool (active + rested)."""
        return self.don_active + self.don_rested

    @property
    def life_count(self) -> int:
        """Number of life cards remaining."""
        return len(self.life_cards)

    def available_don(self) -> int:
        """DON available to spend."""
        return self.don_active

    def copy(self, **changes) -> 'PlayerState':
        """Create a copy with optional changes."""
        return PlayerState(
            player_index=self.player_index,
            name=changes.get('name', self.name),
            leader=changes.get('leader', self.leader),
            life_cards=changes.get('life_cards', self.life_cards),
            hand=changes.get('hand', self.hand),
            field=changes.get('field', self.field),
            trash=changes.get('trash', self.trash),
            deck_size=changes.get('deck_size', self.deck_size),
            don_active=changes.get('don_active', self.don_active),
            don_rested=changes.get('don_rested', self.don_rested),
            has_mulliganed=changes.get('has_mulliganed', self.has_mulliganed),
        )


@dataclass
class CombatContext:
    """
    Context for an ongoing combat.
    """
    attacker_player: int
    attacker_index: int  # -1 for leader
    target_index: int    # -1 for leader
    attacker_power: int
    original_target_index: int

    blocker_index: Optional[int] = None
    counter_total: int = 0
    counters_used: Tuple[int, ...] = ()  # Hand indices of used counters


@dataclass
class GameState:
    """
    Complete immutable game state.

    This is the primary state object used for:
    - Game logic
    - AI state encoding
    - MCTS simulation
    """
    # Players
    players: Tuple[PlayerState, PlayerState]

    # Turn tracking
    turn: int = 1
    active_player: int = 0  # 0 or 1
    phase: GamePhase = GamePhase.MULLIGAN

    # Combat state (only set during combat phases)
    combat: Optional[CombatContext] = None

    # Game result
    is_terminal: bool = False
    winner: Optional[int] = None

    # History (for debugging/replay)
    last_action: Optional[str] = None

    # Instance ID counter (for creating new CardInstances)
    next_instance_id: int = 0

    # Track activated effects this turn (for [Once Per Turn] effects)
    activated_effects_this_turn: Tuple[int, ...] = ()

    @property
    def current_player(self) -> PlayerState:
        """Get the current active player."""
        return self.players[self.active_player]

    @property
    def opponent_player(self) -> PlayerState:
        """Get the opponent of the active player."""
        return self.players[1 - self.active_player]

    def copy(self, **changes) -> 'GameState':
        """Create a copy with optional changes."""
        return GameState(
            players=changes.get('players', self.players),
            turn=changes.get('turn', self.turn),
            active_player=changes.get('active_player', self.active_player),
            phase=changes.get('phase', self.phase),
            combat=changes.get('combat', self.combat),
            is_terminal=changes.get('is_terminal', self.is_terminal),
            winner=changes.get('winner', self.winner),
            last_action=changes.get('last_action', self.last_action),
            next_instance_id=changes.get('next_instance_id', self.next_instance_id),
            activated_effects_this_turn=changes.get('activated_effects_this_turn', self.activated_effects_this_turn),
        )

    def with_player(self, player_index: int, new_player: PlayerState) -> 'GameState':
        """Create a new state with one player replaced."""
        if player_index == 0:
            new_players = (new_player, self.players[1])
        else:
            new_players = (self.players[0], new_player)
        return self.copy(players=new_players)


# ============================================================================
# State Transition Functions
# ============================================================================

def create_initial_state(
    player1_name: str,
    player1_leader: Card,
    player1_deck: List[Card],
    player2_name: str,
    player2_leader: Card,
    player2_deck: List[Card],
) -> GameState:
    """
    Create initial game state.

    Args:
        player1_name: Name for player 1
        player1_leader: Leader card for player 1
        player1_deck: 50-card deck for player 1
        player2_name: Name for player 2
        player2_leader: Leader card for player 2
        player2_deck: 50-card deck for player 2

    Returns:
        Initial GameState ready for mulligan phase
    """
    instance_id = 0

    # Create player 1
    p1_leader_inst = CardInstance(player1_leader, instance_id)
    instance_id += 1

    # Shuffle deck and draw hand
    p1_deck = list(player1_deck)
    random.shuffle(p1_deck)

    # Set up life cards (based on leader life value)
    p1_life_count = player1_leader.life or 5
    p1_life = []
    for i in range(p1_life_count):
        card_inst = CardInstance(p1_deck.pop(), instance_id)
        instance_id += 1
        p1_life.append(card_inst)

    # Draw initial hand
    p1_hand = []
    for i in range(5):
        card_inst = CardInstance(p1_deck.pop(), instance_id)
        instance_id += 1
        p1_hand.append(card_inst)

    player1 = PlayerState(
        player_index=0,
        name=player1_name,
        leader=p1_leader_inst,
        life_cards=tuple(p1_life),
        hand=tuple(p1_hand),
        field=(),
        trash=(),
        deck_size=len(p1_deck),
        don_active=0,  # Will be set after mulligan
        don_rested=0,
    )

    # Create player 2
    p2_leader_inst = CardInstance(player2_leader, instance_id)
    instance_id += 1

    p2_deck = list(player2_deck)
    random.shuffle(p2_deck)

    p2_life_count = player2_leader.life or 5
    p2_life = []
    for i in range(p2_life_count):
        card_inst = CardInstance(p2_deck.pop(), instance_id)
        instance_id += 1
        p2_life.append(card_inst)

    p2_hand = []
    for i in range(5):
        card_inst = CardInstance(p2_deck.pop(), instance_id)
        instance_id += 1
        p2_hand.append(card_inst)

    player2 = PlayerState(
        player_index=1,
        name=player2_name,
        leader=p2_leader_inst,
        life_cards=tuple(p2_life),
        hand=tuple(p2_hand),
        field=(),
        trash=(),
        deck_size=len(p2_deck),
        don_active=0,
        don_rested=0,
    )

    return GameState(
        players=(player1, player2),
        turn=0,  # Mulligan phase before turn 1
        active_player=0,
        phase=GamePhase.MULLIGAN,
        next_instance_id=instance_id,
    )


def advance_to_turn_1(state: GameState) -> GameState:
    """
    Advance from mulligan phase to turn 1.

    Sets initial DON:
    - Player 1: 1 DON
    - Player 2: 2 DON
    """
    p1 = state.players[0].copy(don_active=1)
    p2 = state.players[1].copy(don_active=2)

    return state.copy(
        players=(p1, p2),
        turn=1,
        active_player=0,
        phase=GamePhase.MAIN,  # Skip refresh/draw/DON for turn 1
    )


def start_new_turn(state: GameState) -> GameState:
    """
    Start a new turn for the active player.

    Handles:
    1. Refresh Phase - Unrest all cards, refresh DON
    2. Draw Phase - Draw 1 card (except P1 turn 1)
    3. DON Phase - Add 2 DON (max 10)
    """
    player = state.current_player

    # Refresh: Unrest all cards
    new_leader = player.leader.copy(is_resting=False, has_attacked=False)

    new_field = tuple(
        card.copy(is_resting=False, has_attacked=False)
        for card in player.field
    )

    # Refresh DON
    total_don = player.total_don

    # Add 2 DON (max 10)
    new_don = min(total_don + 2, 10)

    new_player = player.copy(
        leader=new_leader,
        field=new_field,
        don_active=new_don,
        don_rested=0,
    )

    # Note: Draw card is handled separately (needs deck access)

    return state.with_player(state.active_player, new_player).copy(
        phase=GamePhase.MAIN
    )


def end_turn(state: GameState) -> GameState:
    """
    End the current turn and switch to opponent.
    """
    # Check hand limit (7 cards)
    # This is handled by the END phase actions

    new_turn = state.turn + 1
    new_active = 1 - state.active_player

    return state.copy(
        turn=new_turn,
        active_player=new_active,
        phase=GamePhase.REFRESH,
        combat=None,
    )


def check_game_over(state: GameState, damaged_player: int) -> GameState:
    """
    Check if the game is over after damage.

    Win condition: Opponent has 0 life cards.
    """
    player = state.players[damaged_player]

    if player.life_count == 0:
        winner = 1 - damaged_player
        return state.copy(
            is_terminal=True,
            winner=winner,
            phase=GamePhase.GAME_OVER,
        )

    return state
