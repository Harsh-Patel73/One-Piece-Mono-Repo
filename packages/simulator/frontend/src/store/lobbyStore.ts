import { create } from 'zustand'

interface Room {
  code: string
  hostId: string
  hostName: string
  guestId?: string
  guestName?: string
  status: 'waiting' | 'ready' | 'playing'
  createdAt: string
}

interface LobbyState {
  currentRoom: Room | null
  isHost: boolean
  playerName: string
  deckId: string | null
  isReady: boolean
  error: string | null
}

interface LobbyStore extends LobbyState {
  setPlayerName: (name: string) => void
  setDeckId: (id: string | null) => void
  setRoom: (room: Room | null) => void
  setIsHost: (isHost: boolean) => void
  setIsReady: (ready: boolean) => void
  setError: (error: string | null) => void
  reset: () => void
}

const initialState: LobbyState = {
  currentRoom: null,
  isHost: false,
  playerName: '',
  deckId: null,
  isReady: false,
  error: null,
}

export const useLobbyStore = create<LobbyStore>((set) => ({
  ...initialState,

  setPlayerName: (name) => set({ playerName: name }),

  setDeckId: (id) => set({ deckId: id }),

  setRoom: (room) => set({ currentRoom: room }),

  setIsHost: (isHost) => set({ isHost }),

  setIsReady: (ready) => set({ isReady: ready }),

  setError: (error) => set({ error }),

  reset: () => set(initialState),
}))
