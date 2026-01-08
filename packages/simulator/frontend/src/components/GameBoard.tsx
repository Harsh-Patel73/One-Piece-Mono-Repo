import { Card, CardPlaceholder } from './Card'
import { useGameStore } from '../store/gameStore'

interface GameBoardProps {
  onEndTurn: () => void
  onSurrender: () => void
}

export function GameBoard({ onEndTurn, onSurrender }: GameBoardProps) {
  const { players, playerIndex, activePlayer, turn, phase } = useGameStore()

  if (!players) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-slate-400">Waiting for game to start...</div>
      </div>
    )
  }

  const player = players[playerIndex]
  const opponent = players[1 - playerIndex]
  const isMyTurn = activePlayer === playerIndex

  return (
    <div className="flex flex-col h-full">
      {/* Opponent Area */}
      <div className="flex-1 flex flex-col p-4">
        <OpponentInfo opponent={opponent} />
        <div className="flex-1 flex items-center justify-center gap-2">
          <FieldSlot label="Leader" card={opponent.leader} isOpponent />
          {[0, 1, 2, 3, 4].map((i) => (
            <FieldSlot
              key={i}
              card={opponent.field[i]}
              isOpponent
            />
          ))}
        </div>
      </div>

      {/* Center - DON and Actions */}
      <div className="h-24 flex items-center justify-center gap-8 border-y border-slate-700 bg-slate-800/50">
        <div className="text-center">
          <div className="text-3xl font-bold text-yellow-400">
            {player.activeDon}
          </div>
          <div className="text-xs text-slate-400">Active DON!!</div>
        </div>
        <div className="w-px h-12 bg-slate-600" />
        <div className="text-center">
          <div className="text-sm text-slate-400">Turn {turn}</div>
          <div className={`text-sm font-semibold ${isMyTurn ? 'text-green-400' : 'text-slate-400'}`}>
            {isMyTurn ? 'Your Turn' : "Opponent's Turn"}
          </div>
        </div>
        <div className="w-px h-12 bg-slate-600" />
        <button
          onClick={onEndTurn}
          disabled={!isMyTurn}
          className={`
            px-6 py-2 rounded-lg font-bold transition-all
            ${isMyTurn
              ? 'bg-gradient-to-r from-red-600 to-red-700 hover:from-red-500 hover:to-red-600 text-white'
              : 'bg-slate-700 text-slate-500 cursor-not-allowed'
            }
          `}
        >
          End Turn
        </button>
      </div>

      {/* Player Area */}
      <div className="flex-1 flex flex-col p-4">
        <div className="flex-1 flex items-center justify-center gap-2">
          <FieldSlot label="Leader" card={player.leader} />
          {[0, 1, 2, 3, 4].map((i) => (
            <FieldSlot key={i} card={player.field[i]} />
          ))}
        </div>
        <PlayerInfo player={player} />
        <Hand cards={player.hand} />
      </div>
    </div>
  )
}

function OpponentInfo({ opponent }: { opponent: any }) {
  return (
    <div className="flex items-center justify-between px-4 py-2">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-slate-700 rounded-full flex items-center justify-center">
          🤖
        </div>
        <div>
          <div className="text-white font-semibold">{opponent.name}</div>
          <div className="text-xs text-slate-400">Deck: {opponent.deck}</div>
        </div>
      </div>
      <div className="flex items-center gap-6">
        <Stat label="Life" value={opponent.life} color="red" />
        <Stat label="Hand" value={opponent.hand.length} />
        <Stat label="DON" value={opponent.don} color="yellow" />
      </div>
    </div>
  )
}

function PlayerInfo({ player }: { player: any }) {
  return (
    <div className="flex items-center justify-between px-4 py-2">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
          👤
        </div>
        <div>
          <div className="text-white font-semibold">{player.name}</div>
          <div className="text-xs text-slate-400">Deck: {player.deck}</div>
        </div>
      </div>
      <div className="flex items-center gap-6">
        <Stat label="Life" value={player.life} color="red" />
        <Stat label="DON" value={player.don} color="yellow" />
      </div>
    </div>
  )
}

function Stat({ label, value, color }: { label: string; value: number; color?: string }) {
  const colorClass = color === 'red' ? 'text-red-400' : color === 'yellow' ? 'text-yellow-400' : 'text-white'
  return (
    <div className="text-center">
      <div className={`text-xl font-bold ${colorClass}`}>{value}</div>
      <div className="text-xs text-slate-400">{label}</div>
    </div>
  )
}

function FieldSlot({ card, label, isOpponent }: { card?: any; label?: string; isOpponent?: boolean }) {
  if (card) {
    return (
      <Card
        id={card.instanceId}
        name={card.card?.name}
        power={card.card?.power}
        cost={card.card?.cost}
        color={card.card?.color}
        rested={card.rested}
        size="md"
      />
    )
  }

  return (
    <CardPlaceholder size="md" label={label} />
  )
}

function Hand({ cards }: { cards: any[] }) {
  return (
    <div className="flex justify-center gap-1 overflow-x-auto py-2">
      {cards.map((card, i) => (
        <Card
          key={card.instanceId || i}
          id={card.instanceId}
          name={card.card?.name}
          power={card.card?.power}
          cost={card.card?.cost}
          color={card.card?.color}
          size="sm"
        />
      ))}
    </div>
  )
}
