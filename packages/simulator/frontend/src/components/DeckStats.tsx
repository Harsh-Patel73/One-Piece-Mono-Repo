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
  counter?: number
  color: string[]
  trigger?: string
  imageUrl?: string
}

interface DeckStatsProps {
  deckCards: DeckCard[]
  cardDatabase: Map<string, CardData>
}

interface DeckStatsResult {
  typeCount: Record<string, number>
  costCurve: Record<number, number>
  powerDist: Record<number, number>
  counterCount: Record<number, number>
  triggerCount: number
  totalCards: number
}

function calculateDeckStats(deckCards: DeckCard[], cardDatabase: Map<string, CardData>): DeckStatsResult {
  const stats: DeckStatsResult = {
    typeCount: { CHARACTER: 0, EVENT: 0, STAGE: 0 },
    costCurve: { 0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 },
    powerDist: {},
    counterCount: { 0: 0, 1000: 0, 2000: 0 },
    triggerCount: 0,
    totalCards: 0,
  }

  for (const deckCard of deckCards) {
    const card = cardDatabase.get(deckCard.cardId)
    if (!card) continue

    const count = deckCard.count
    stats.totalCards += count

    // Type count
    if (card.type in stats.typeCount) {
      stats.typeCount[card.type] += count
    }

    // Cost curve (group 5+ together)
    const costKey = Math.min(card.cost ?? 0, 5)
    stats.costCurve[costKey] = (stats.costCurve[costKey] || 0) + count

    // Power distribution
    if (card.power) {
      stats.powerDist[card.power] = (stats.powerDist[card.power] || 0) + count
    }

    // Counter breakdown
    const counterKey = card.counter ?? 0
    if (counterKey in stats.counterCount) {
      stats.counterCount[counterKey] += count
    } else {
      stats.counterCount[0] += count
    }

    // Trigger count
    if (card.trigger && card.trigger.trim()) {
      stats.triggerCount += count
    }
  }

  return stats
}

function StatBadge({ label, value, highlight = false }: { label: string; value: number; highlight?: boolean }) {
  return (
    <div className={`rounded px-3 py-2 text-center ${highlight ? 'bg-yellow-500/20 border border-yellow-500/30' : 'bg-stone-700/50'}`}>
      <div className={`text-xl font-bold ${highlight ? 'text-yellow-400' : 'text-white'}`}>{value}</div>
      <div className="text-xs text-amber-200/50">{label}</div>
    </div>
  )
}

function CostBar({ cost, count, maxCount }: { cost: string; count: number; maxCount: number }) {
  const height = maxCount > 0 ? Math.max((count / maxCount) * 100, 8) : 8

  return (
    <div className="flex flex-col items-center flex-1">
      <div className="w-full h-24 flex items-end justify-center">
        <div
          className="w-6 bg-gradient-to-t from-amber-700 to-amber-500 rounded-t transition-all duration-300"
          style={{ height: `${height}%` }}
        />
      </div>
      <div className="text-sm font-bold text-white mt-1">{count}</div>
      <div className="text-xs text-amber-200/40">{cost}</div>
    </div>
  )
}

export function DeckStats({ deckCards, cardDatabase }: DeckStatsProps) {
  const stats = calculateDeckStats(deckCards, cardDatabase)
  const maxCostCount = Math.max(...Object.values(stats.costCurve), 1)

  // Sort power distribution
  const sortedPowers = Object.entries(stats.powerDist)
    .sort(([a], [b]) => Number(a) - Number(b))

  return (
    <div className="space-y-4">
      {/* Card Types */}
      <div className="bg-stone-800/50 rounded-lg p-4">
        <h4 className="text-xs font-semibold text-amber-200/60 mb-3 uppercase tracking-wide">Card Types</h4>
        <div className="grid grid-cols-3 gap-2">
          <StatBadge label="Character" value={stats.typeCount.CHARACTER} />
          <StatBadge label="Event" value={stats.typeCount.EVENT} />
          <StatBadge label="Stage" value={stats.typeCount.STAGE} />
        </div>
      </div>

      {/* Cost Curve */}
      <div className="bg-stone-800/50 rounded-lg p-4">
        <h4 className="text-xs font-semibold text-amber-200/60 mb-3 uppercase tracking-wide">Cost Curve</h4>
        <div className="flex gap-1">
          {[0, 1, 2, 3, 4, 5].map(cost => (
            <CostBar
              key={cost}
              cost={cost === 5 ? '5+' : String(cost)}
              count={stats.costCurve[cost] || 0}
              maxCount={maxCostCount}
            />
          ))}
        </div>
      </div>

      {/* Power Distribution */}
      <div className="bg-stone-800/50 rounded-lg p-4">
        <h4 className="text-xs font-semibold text-amber-200/60 mb-3 uppercase tracking-wide">Power Distribution</h4>
        {sortedPowers.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {sortedPowers.map(([power, count]) => (
              <div key={power} className="bg-stone-700/50 rounded px-2 py-1 text-center min-w-[50px]">
                <div className="text-sm font-bold text-white">{count}</div>
                <div className="text-xs text-amber-200/50">{Number(power) / 1000}K</div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-sm text-amber-200/40">No power cards in deck</div>
        )}
      </div>

      {/* Counter & Triggers */}
      <div className="grid grid-cols-2 gap-4">
        {/* Counter Breakdown */}
        <div className="bg-stone-800/50 rounded-lg p-4">
          <h4 className="text-xs font-semibold text-amber-200/60 mb-3 uppercase tracking-wide">Counter</h4>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm text-amber-100/80">+2000</span>
              <span className="text-sm font-bold text-green-400">{stats.counterCount[2000]}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-amber-100/80">+1000</span>
              <span className="text-sm font-bold text-amber-400">{stats.counterCount[1000]}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-amber-100/80">None</span>
              <span className="text-sm font-bold text-amber-200/40">{stats.counterCount[0]}</span>
            </div>
          </div>
        </div>

        {/* Triggers */}
        <div className="bg-stone-800/50 rounded-lg p-4">
          <h4 className="text-xs font-semibold text-amber-200/60 mb-3 uppercase tracking-wide">Triggers</h4>
          <StatBadge label="Trigger Cards" value={stats.triggerCount} highlight={stats.triggerCount > 0} />
        </div>
      </div>
    </div>
  )
}
