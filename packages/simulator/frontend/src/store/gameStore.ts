import { create } from 'zustand'

// Card type matching backend serialization
export interface GameCard {
  id: string
  name: string
  card_type: string
  cost: number | null
  power: number | null
  counter: number | null
  colors: string[]
  life: number | null
  effect: string | null
  trigger: string | null
  image_link: string | null
  attribute: string | null
  card_origin: string | null
  is_resting: boolean
  has_attacked: boolean
  attached_don: number
  played_turn: number | null
  instance_id: string
}

// Player state from backend
export interface PlayerState {
  player_index: number
  name: string
  leader: GameCard
  life_count: number
  hand_count: number
  deck_count: number
  field: GameCard[]
  trash_count: number
  don_active: number
  don_rested: number
  total_don: number
  has_mulliganed: boolean
  // Hidden info - only available for own player
  hand?: GameCard[]
  life_cards?: GameCard[]
}

// Full game state from backend
export interface BackendGameState {
  game_id: string
  turn: number
  phase: string
  active_player: number
  player1: PlayerState
  player2: PlayerState
  is_terminal: boolean
  winner: number | null
  awaiting_response: string | null
  pending_attack: {
    attacker: GameCard
    original_target: GameCard
    current_target: GameCard
  } | null
  last_action: string
}

// Local UI state
interface GameUIState {
  gameId: string | null
  playerIndex: number
  gameState: BackendGameState | null
  selectedCardIndex: number | null
  selectedCardZone: 'hand' | 'field' | 'leader' | null
  targetMode: 'none' | 'attack' | 'play' | 'attach_don'
  logs: string[]
  isLoading: boolean
  error: string | null
}

interface GameStore extends GameUIState {
  // Actions
  setGameId: (id: string) => void
  setPlayerIndex: (index: number) => void
  setGameState: (state: BackendGameState) => void
  setLogs: (logs: string[]) => void
  selectCard: (index: number | null, zone: 'hand' | 'field' | 'leader' | null) => void
  setTargetMode: (mode: GameUIState['targetMode']) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearSelection: () => void
  resetGame: () => void
}

const initialState: GameUIState = {
  gameId: null,
  playerIndex: 0,
  gameState: null,
  selectedCardIndex: null,
  selectedCardZone: null,
  targetMode: 'none',
  logs: [],
  isLoading: false,
  error: null,
}

export const useGameStore = create<GameStore>((set) => ({
  ...initialState,

  setGameId: (id) => set({ gameId: id }),

  setPlayerIndex: (index) => set({ playerIndex: index }),

  setGameState: (state) => set({ gameState: state }),

  setLogs: (logs) => set({ logs }),

  selectCard: (index, zone) => set({ selectedCardIndex: index, selectedCardZone: zone }),

  setTargetMode: (mode) => set({ targetMode: mode }),

  setLoading: (loading) => set({ isLoading: loading }),

  setError: (error) => set({ error }),

  clearSelection: () => set({
    selectedCardIndex: null,
    selectedCardZone: null,
    targetMode: 'none'
  }),

  resetGame: () => set(initialState),
}))

// Helper to get current player's data
export function getMyPlayer(state: BackendGameState, playerIndex: number): PlayerState {
  return playerIndex === 0 ? state.player1 : state.player2
}

// Helper to get opponent's data
export function getOpponentPlayer(state: BackendGameState, playerIndex: number): PlayerState {
  return playerIndex === 0 ? state.player2 : state.player1
}

// Check if it's my turn
export function isMyTurn(state: BackendGameState, playerIndex: number): boolean {
  return state.active_player === playerIndex
}
