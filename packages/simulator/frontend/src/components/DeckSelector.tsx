import { Trash2, FolderOpen } from 'lucide-react'
import { motion } from 'framer-motion'

interface Deck {
  id: string
  name: string
  leaderId: string
  cards: { cardId: string; count: number }[]
  createdAt: string
  updatedAt: string
}

interface DeckSelectorProps {
  decks: Deck[]
  currentDeckId?: string
  onSelectDeck: (deck: Deck) => void
  onDeleteDeck: (deckId: string) => void
  onNewDeck: () => void
}

export function DeckSelector({ decks, currentDeckId, onSelectDeck, onDeleteDeck, onNewDeck }: DeckSelectorProps) {
  const getCardCount = (deck: Deck) => {
    return deck.cards.reduce((sum, c) => sum + c.count, 0)
  }

  return (
    <div className="space-y-3">
      {/* New Deck Button */}
      <button
        onClick={onNewDeck}
        className="w-full px-4 py-3 bg-stone-700/50 hover:bg-stone-700 border-2 border-dashed border-amber-900/50 hover:border-yellow-500 rounded-lg text-amber-200/60 hover:text-white transition-colors text-sm font-medium"
      >
        + New Deck
      </button>

      {/* Saved Decks */}
      {decks.length === 0 ? (
        <div className="text-center py-6 text-amber-200/40 text-sm">
          <FolderOpen className="w-8 h-8 mx-auto mb-2 opacity-50" />
          <p>No saved decks</p>
        </div>
      ) : (
        <div className="space-y-2">
          {decks.map((deck) => {
            const isActive = deck.id === currentDeckId
            const cardCount = getCardCount(deck)

            return (
              <motion.div
                key={deck.id}
                whileHover={{ scale: 1.01 }}
                className={`relative group rounded-lg border-2 transition-colors cursor-pointer ${
                  isActive
                    ? 'bg-stone-700 border-yellow-500'
                    : 'bg-stone-800/50 border-amber-900/30 hover:border-amber-700/50'
                }`}
                onClick={() => onSelectDeck(deck)}
              >
                <div className="p-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h4 className={`font-medium truncate ${isActive ? 'text-yellow-400' : 'text-white'}`}>
                        {deck.name}
                      </h4>
                      <p className="text-xs text-amber-200/50 mt-1">
                        {cardCount}/50 cards
                      </p>
                    </div>

                    {/* Delete Button */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        onDeleteDeck(deck.id)
                      }}
                      className="p-1.5 text-amber-200/40 hover:text-red-400 hover:bg-red-500/10 rounded transition-colors opacity-0 group-hover:opacity-100"
                      title="Delete deck"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Active Indicator */}
                {isActive && (
                  <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-yellow-500 rounded-r" />
                )}
              </motion.div>
            )
          })}
        </div>
      )}
    </div>
  )
}
