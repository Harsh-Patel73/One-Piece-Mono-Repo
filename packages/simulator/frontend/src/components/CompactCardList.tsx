import { motion } from 'framer-motion'
import { CardPreview } from './CardPreview'

interface DeckCard {
  cardId: string
  count: number
}

interface CardData {
  id: string
  name: string
  type: string
  cost?: number
  power?: number
  color: string[]
  imageUrl?: string
}

interface CompactCardListProps {
  deckCards: DeckCard[]
  cardDatabase: Map<string, CardData>
  onRemoveCard: (cardId: string) => void
}

export function CompactCardList({ deckCards, cardDatabase, onRemoveCard }: CompactCardListProps) {
  // Sort cards by cost, then by name
  const sortedCards = [...deckCards].sort((a, b) => {
    const cardA = cardDatabase.get(a.cardId)
    const cardB = cardDatabase.get(b.cardId)
    if (!cardA || !cardB) return 0

    const costDiff = (cardA.cost ?? 0) - (cardB.cost ?? 0)
    if (costDiff !== 0) return costDiff
    return cardA.name.localeCompare(cardB.name)
  })

  if (sortedCards.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-16 text-amber-200/40">
        <p className="text-xs">No cards in deck - click cards below to add</p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-8 lg:grid-cols-10 xl:grid-cols-12 gap-1">
      {sortedCards.map(deckCard => {
        const card = cardDatabase.get(deckCard.cardId)
        if (!card) return null

        return (
          <CardPreview
            key={deckCard.cardId}
            imageUrl={card.imageUrl}
            name={card.name}
            id={card.id}
          >
            <motion.div
              className="relative group cursor-pointer"
              whileTap={{ scale: 0.98 }}
              onClick={() => onRemoveCard(deckCard.cardId)}
            >
              {/* Card Image */}
              <div className="aspect-[2.5/3.5] rounded overflow-hidden border border-amber-900/50 group-hover:border-red-500 transition-colors">
                {card.imageUrl ? (
                  <img
                    src={card.imageUrl}
                    alt={card.name}
                    className="w-full h-full object-cover"
                    loading="lazy"
                  />
                ) : (
                  <div className="w-full h-full bg-gradient-to-br from-stone-600 to-stone-800 flex flex-col items-center justify-center p-0.5">
                    <div className="text-[6px] text-amber-200/50">{card.id}</div>
                    <div className="text-[6px] text-white text-center font-medium truncate w-full">{card.name}</div>
                  </div>
                )}
              </div>

              {/* Count Badge */}
              <div className="absolute -top-0.5 -right-0.5 bg-amber-600 text-white text-[8px] font-bold w-4 h-4 rounded-full flex items-center justify-center shadow border border-stone-900">
                {deckCard.count}
              </div>

              {/* Hover Overlay */}
              <div className="absolute inset-0 bg-red-500/60 rounded opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center pointer-events-none">
                <span className="text-white text-[8px] font-bold">-</span>
              </div>
            </motion.div>
          </CardPreview>
        )
      })}
    </div>
  )
}
