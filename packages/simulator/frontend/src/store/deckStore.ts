import { create } from 'zustand'
import { persist } from 'zustand/middleware'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface DeckCard {
  cardId: string
  count: number
}

interface Deck {
  id: string
  name: string
  leaderId: string
  cards: DeckCard[]
  createdAt: string
  updatedAt: string
}

interface DeckStore {
  decks: Deck[]
  currentDeck: Deck | null
  loading: boolean
  error: string | null

  // Actions
  fetchDecks: () => Promise<void>
  createDeck: (name: string, leaderId: string) => Promise<Deck | null>
  updateDeck: (deck: Deck) => Promise<void>
  deleteDeck: (id: string) => Promise<void>
  setCurrentDeck: (deck: Deck | null) => void
  addCardToDeck: (cardId: string) => void
  removeCardFromDeck: (cardId: string) => void
  getDeckCardCount: () => number
}

export const useDeckStore = create<DeckStore>()(
  persist(
    (set, get) => ({
      decks: [],
      currentDeck: null,
      loading: false,
      error: null,

      fetchDecks: async () => {
        set({ loading: true, error: null })
        try {
          const response = await fetch(`${API_BASE}/api/decks`)
          if (!response.ok) throw new Error('Failed to fetch decks')
          const decks = await response.json()
          set({ decks, loading: false })
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Unknown error',
            loading: false,
          })
        }
      },

      createDeck: async (name, leaderId) => {
        set({ loading: true, error: null })
        try {
          const newDeck: Deck = {
            id: crypto.randomUUID(),
            name,
            leaderId,
            cards: [],
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          }
          set((state) => ({
            decks: [...state.decks, newDeck],
            currentDeck: newDeck,
            loading: false,
          }))
          return newDeck
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Unknown error',
            loading: false,
          })
          return null
        }
      },

      updateDeck: async (deck) => {
        const updatedDeck = { ...deck, updatedAt: new Date().toISOString() }
        set((state) => ({
          decks: state.decks.map((d) => (d.id === deck.id ? updatedDeck : d)),
          currentDeck: state.currentDeck?.id === deck.id ? updatedDeck : state.currentDeck,
        }))
      },

      deleteDeck: async (id) => {
        set((state) => ({
          decks: state.decks.filter((d) => d.id !== id),
          currentDeck: state.currentDeck?.id === id ? null : state.currentDeck,
        }))
      },

      setCurrentDeck: (deck) => set({ currentDeck: deck }),

      addCardToDeck: (cardId) => {
        const { currentDeck, getDeckCardCount } = get()
        if (!currentDeck) return

        // Check 50 card limit
        if (getDeckCardCount() >= 50) return

        const existingCard = currentDeck.cards.find((c) => c.cardId === cardId)

        // Check 4 card limit per card
        if (existingCard && existingCard.count >= 4) return

        const newCards = existingCard
          ? currentDeck.cards.map((c) =>
              c.cardId === cardId ? { ...c, count: c.count + 1 } : c
            )
          : [...currentDeck.cards, { cardId, count: 1 }]

        const updatedDeck = { ...currentDeck, cards: newCards, updatedAt: new Date().toISOString() }

        set((state) => ({
          currentDeck: updatedDeck,
          decks: state.decks.map((d) => (d.id === currentDeck.id ? updatedDeck : d)),
        }))
      },

      removeCardFromDeck: (cardId) => {
        const { currentDeck } = get()
        if (!currentDeck) return

        const existingCard = currentDeck.cards.find((c) => c.cardId === cardId)
        if (!existingCard) return

        const newCards =
          existingCard.count > 1
            ? currentDeck.cards.map((c) =>
                c.cardId === cardId ? { ...c, count: c.count - 1 } : c
              )
            : currentDeck.cards.filter((c) => c.cardId !== cardId)

        const updatedDeck = { ...currentDeck, cards: newCards, updatedAt: new Date().toISOString() }

        set((state) => ({
          currentDeck: updatedDeck,
          decks: state.decks.map((d) => (d.id === currentDeck.id ? updatedDeck : d)),
        }))
      },

      getDeckCardCount: () => {
        const { currentDeck } = get()
        if (!currentDeck) return 0
        return currentDeck.cards.reduce((sum, c) => sum + c.count, 0)
      },
    }),
    {
      name: 'optcg-decks',
      partialize: (state) => ({ decks: state.decks }),
    }
  )
)
