import { create } from 'zustand'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface Card {
  id: string
  name: string
  type: string
  cost: number
  power?: number
  counter?: number
  life?: number
  color: string[]
  attributes?: string[]
  traits?: string[]
  effect?: string
  trigger?: string
  imageUrl?: string
  setId?: string
}

interface CardFilters {
  search: string
  colors: string[]
  types: string[]
  costMin?: number
  costMax?: number
  powerMin?: number
  powerMax?: number
}

interface CardStore {
  cards: Card[]
  loading: boolean
  error: string | null
  filters: CardFilters

  // Actions
  fetchCards: () => Promise<void>
  setFilters: (filters: Partial<CardFilters>) => void
  resetFilters: () => void
  getFilteredCards: () => Card[]
}

const defaultFilters: CardFilters = {
  search: '',
  colors: [],
  types: [],
  costMin: undefined,
  costMax: undefined,
  powerMin: undefined,
  powerMax: undefined,
}

export const useCardStore = create<CardStore>((set, get) => ({
  cards: [],
  loading: false,
  error: null,
  filters: defaultFilters,

  fetchCards: async () => {
    set({ loading: true, error: null })
    try {
      const response = await fetch(`${API_BASE}/api/cards?limit=5000`)
      if (!response.ok) throw new Error('Failed to fetch cards')
      const data = await response.json()
      // Transform backend fields to frontend format
      const cards = (data.cards || []).map((card: any) => ({
        id: card.id,
        name: card.name,
        type: card.card_type || 'CHARACTER',
        cost: card.cost ?? 0,
        power: card.power,
        counter: card.counter,
        life: card.life,
        color: card.colors || [],
        effect: card.effect,
        trigger: card.trigger,
        imageUrl: card.image_link,
      }))
      set({ cards, loading: false })
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Unknown error',
        loading: false
      })
    }
  },

  setFilters: (newFilters) => set((state) => ({
    filters: { ...state.filters, ...newFilters }
  })),

  resetFilters: () => set({ filters: defaultFilters }),

  getFilteredCards: () => {
    const { cards, filters } = get()

    return cards.filter((card) => {
      // Search filter
      if (filters.search) {
        const searchLower = filters.search.toLowerCase()
        const matchesSearch =
          card.name.toLowerCase().includes(searchLower) ||
          card.id.toLowerCase().includes(searchLower) ||
          card.effect?.toLowerCase().includes(searchLower)
        if (!matchesSearch) return false
      }

      // Color filter
      if (filters.colors.length > 0) {
        const hasColor = filters.colors.some(c => card.color.includes(c))
        if (!hasColor) return false
      }

      // Type filter
      if (filters.types.length > 0) {
        if (!filters.types.includes(card.type)) return false
      }

      // Cost filter
      if (filters.costMin !== undefined && card.cost < filters.costMin) return false
      if (filters.costMax !== undefined && card.cost > filters.costMax) return false

      // Power filter
      if (filters.powerMin !== undefined && (card.power ?? 0) < filters.powerMin) return false
      if (filters.powerMax !== undefined && (card.power ?? 0) > filters.powerMax) return false

      return true
    })
  },
}))
