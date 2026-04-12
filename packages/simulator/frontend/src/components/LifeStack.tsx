import { PlaytestCard } from '../hooks/usePlaytestSocket'

interface LifeStackProps {
  cards: PlaytestCard[]
  compact?: boolean
}

export function LifeStack({ cards, compact = false }: LifeStackProps) {
  const width = compact ? 36 : 44
  const height = compact ? 50 : 62
  const offset = compact ? 5 : 6
  const visibleCards = cards.slice(-Math.min(cards.length, 6))
  const stackWidth = width + Math.max(0, visibleCards.length - 1) * offset

  if (cards.length === 0) {
    return (
      <div
        className="rounded-md border border-red-900/40 bg-stone-800/50 flex items-center justify-center text-[10px] text-stone-500"
        style={{ width, height }}
      >
        0
      </div>
    )
  }

  return (
    <div className="flex items-end gap-2">
      <div className="relative" style={{ width: stackWidth, height }}>
        {visibleCards.map((card, idx) => {
          const left = idx * offset
          const isFaceUp = Boolean(card.isFaceUp)
          return (
            <div
              key={`${card.instanceId}-${idx}`}
              className={`absolute top-0 overflow-hidden rounded-md border shadow-sm ${
                isFaceUp
                  ? 'border-amber-400/70 bg-stone-900'
                  : 'border-red-900/60 bg-gradient-to-br from-red-950 via-stone-900 to-red-900'
              }`}
              style={{ width, height, left, zIndex: idx + 1 }}
              title={isFaceUp ? card.name : 'Face-down Life Card'}
            >
              {isFaceUp ? (
                card.imageUrl ? (
                  <img src={card.imageUrl} alt={card.name} className="h-full w-full object-cover" />
                ) : (
                  <div className="flex h-full w-full flex-col justify-between p-1 text-[8px] text-amber-100">
                    <span className="font-semibold leading-tight">{card.name}</span>
                    <span className="text-[7px] text-amber-200/70">{card.id}</span>
                  </div>
                )
              ) : (
                <div className="flex h-full w-full flex-col items-center justify-center text-[8px] font-black text-red-200/80">
                  <span>LIFE</span>
                </div>
              )}
            </div>
          )
        })}
      </div>
      <div className="text-[10px] text-amber-200/60">{cards.length}</div>
    </div>
  )
}
