import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Flag, Zap, Swords, RotateCcw, Hand } from 'lucide-react'
import { useSocket } from '../hooks/useSocket'
import { useGameStore, getMyPlayer, getOpponentPlayer, isMyTurn, GameCard, BackendGameState } from '../store/gameStore'
import { Card, CardPlaceholder } from '../components/Card'

export function GamePage() {
  const { gameId } = useParams()
  const navigate = useNavigate()
  const { socket, connected } = useSocket()

  const {
    gameState,
    playerIndex,
    selectedCardIndex,
    selectedCardZone,
    targetMode,
    logs,
    isLoading,
    setGameId,
    setPlayerIndex,
    setGameState,
    setLogs,
    selectCard,
    setTargetMode,
    clearSelection,
    setLoading,
    setError,
    resetGame,
  } = useGameStore()

  const [showMulligan, setShowMulligan] = useState(false)
  const [mulliganSelection, setMulliganSelection] = useState<number[]>([])

  // Start AI game if this is the special new-ai route
  useEffect(() => {
    if (!socket || !connected) return

    if (gameId === 'new-ai') {
      console.log('Starting AI game...')
      setLoading(true)
      socket.emit('start_ai_game', {
        player_name: 'Player',
        difficulty: 'medium',
        deck_id: 'red_luffy',
      })
    }
  }, [socket, connected, gameId, setLoading])

  // Socket event handlers
  useEffect(() => {
    if (!socket) return

    const handleGameStarted = (data: {
      game_id: string
      player_index: number
      game_state: BackendGameState
    }) => {
      console.log('Game started:', data)
      setGameId(data.game_id)
      setPlayerIndex(data.player_index)
      setGameState(data.game_state)
      setLoading(false)

      // Check if we need to mulligan
      const myPlayer = data.player_index === 0 ? data.game_state.player1 : data.game_state.player2
      if (!myPlayer.has_mulliganed) {
        setShowMulligan(true)
      }
    }

    const handleGameUpdate = (data: {
      game_state: BackendGameState
      logs: string[]
    }) => {
      console.log('Game update:', data)
      setGameState(data.game_state)
      if (data.logs) {
        setLogs(data.logs)
      }
      clearSelection()
    }

    const handleGameOver = (data: {
      winner: number
      reason: string
      winner_name?: string
    }) => {
      const isWinner = data.winner === playerIndex
      alert(`Game Over! ${isWinner ? 'You Won!' : 'You Lost!'}\n${data.winner_name || 'Winner'} wins by ${data.reason}`)
      resetGame()
      navigate('/')
    }

    const handleError = (data: { message: string }) => {
      console.error('Game error:', data.message)
      setError(data.message)
    }

    socket.on('game_started', handleGameStarted)
    socket.on('game_update', handleGameUpdate)
    socket.on('game_over', handleGameOver)
    socket.on('error', handleError)

    return () => {
      socket.off('game_started', handleGameStarted)
      socket.off('game_update', handleGameUpdate)
      socket.off('game_over', handleGameOver)
      socket.off('error', handleError)
    }
  }, [socket, playerIndex, setGameId, setPlayerIndex, setGameState, setLogs, clearSelection, setLoading, setError, resetGame, navigate])

  // Game action handlers
  const handleMulligan = useCallback(() => {
    if (!socket) return
    socket.emit('mulligan', { card_indices: mulliganSelection })
    setShowMulligan(false)
    setMulliganSelection([])
  }, [socket, mulliganSelection])

  const handlePlayCard = useCallback((cardIndex: number) => {
    if (!socket || !gameState) return
    if (!isMyTurn(gameState, playerIndex)) return

    socket.emit('play_card', { card_index: cardIndex })
    clearSelection()
  }, [socket, gameState, playerIndex, clearSelection])

  const handleAttack = useCallback((attackerIndex: number, targetIndex: number) => {
    if (!socket || !gameState) return
    if (!isMyTurn(gameState, playerIndex)) return

    socket.emit('attack', {
      attacker_index: attackerIndex,
      target_index: targetIndex,
    })
    clearSelection()
  }, [socket, gameState, playerIndex, clearSelection])

  const handleBlockerResponse = useCallback((blockerIndex: number | null) => {
    if (!socket) return
    socket.emit('blocker_response', { blocker_index: blockerIndex })
  }, [socket])

  const handleCounterResponse = useCallback((counterIndices: number[]) => {
    if (!socket) return
    socket.emit('counter_response', { counter_indices: counterIndices })
  }, [socket])

  const handleAttachDon = useCallback((cardIndex: number, amount: number = 1) => {
    if (!socket || !gameState) return
    if (!isMyTurn(gameState, playerIndex)) return

    socket.emit('attach_don', { card_index: cardIndex, amount })
    clearSelection()
  }, [socket, gameState, playerIndex, clearSelection])

  const handleEndTurn = useCallback(() => {
    if (!socket || !gameState) return
    if (!isMyTurn(gameState, playerIndex)) return

    socket.emit('end_turn', {})
    clearSelection()
  }, [socket, gameState, playerIndex, clearSelection])

  const handleSurrender = useCallback(() => {
    if (!socket) return
    if (confirm('Are you sure you want to surrender?')) {
      socket.emit('surrender', {})
    }
  }, [socket])

  // Card click handlers
  const handleHandCardClick = useCallback((index: number) => {
    if (!gameState || !isMyTurn(gameState, playerIndex)) return

    if (selectedCardZone === 'hand' && selectedCardIndex === index) {
      // Click same card - play it if possible
      handlePlayCard(index)
    } else {
      // Select the card
      selectCard(index, 'hand')
    }
  }, [gameState, playerIndex, selectedCardZone, selectedCardIndex, selectCard, handlePlayCard])

  const handleFieldCardClick = useCallback((index: number, isOpponent: boolean) => {
    if (!gameState) return

    if (isOpponent) {
      // Clicking opponent field - attack target
      if (targetMode === 'attack' && selectedCardIndex !== null) {
        handleAttack(selectedCardIndex, index)
      }
    } else {
      // Clicking own field
      if (targetMode === 'attach_don' && selectedCardIndex !== null) {
        handleAttachDon(index)
      } else if (isMyTurn(gameState, playerIndex)) {
        const myPlayer = getMyPlayer(gameState, playerIndex)
        const card = myPlayer.field[index]
        if (card && !card.is_resting && !card.has_attacked) {
          selectCard(index, 'field')
          setTargetMode('attack')
        }
      }
    }
  }, [gameState, playerIndex, targetMode, selectedCardIndex, selectCard, setTargetMode, handleAttack, handleAttachDon])

  const handleLeaderClick = useCallback((isOpponent: boolean) => {
    if (!gameState) return

    if (isOpponent) {
      // Attacking opponent leader
      if (targetMode === 'attack' && selectedCardIndex !== null) {
        handleAttack(selectedCardIndex, -1)  // -1 = leader target
      }
    } else {
      // Clicking own leader
      if (targetMode === 'attach_don') {
        handleAttachDon(-1)  // -1 = leader
      } else if (isMyTurn(gameState, playerIndex)) {
        const myPlayer = getMyPlayer(gameState, playerIndex)
        if (!myPlayer.leader.is_resting) {
          selectCard(-1, 'leader')
          setTargetMode('attack')
        }
      }
    }
  }, [gameState, playerIndex, targetMode, selectedCardIndex, selectCard, setTargetMode, handleAttack, handleAttachDon])

  const handleDonPoolClick = useCallback(() => {
    if (!gameState || !isMyTurn(gameState, playerIndex)) return
    const myPlayer = getMyPlayer(gameState, playerIndex)
    if (myPlayer.don_active > 0) {
      setTargetMode('attach_don')
    }
  }, [gameState, playerIndex, setTargetMode])

  // Render loading state
  if (isLoading || !gameState) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-op-yellow mx-auto mb-4"></div>
          <p className="text-white text-xl">Starting game...</p>
          <p className="text-slate-400 mt-2">Connecting to Vinsmoke AI</p>
        </div>
      </div>
    )
  }

  const myPlayer = getMyPlayer(gameState, playerIndex)
  const opponent = getOpponentPlayer(gameState, playerIndex)
  const myTurn = isMyTurn(gameState, playerIndex)

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900">
      {/* Top Bar */}
      <div className="fixed top-0 left-0 right-0 bg-slate-900/90 backdrop-blur-sm border-b border-slate-700 px-4 py-2 flex items-center justify-between z-50">
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          Leave
        </button>
        <div className="flex items-center gap-4">
          <span className="text-slate-400">Turn {gameState.turn}</span>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
            myTurn ? 'bg-green-500/20 text-green-400' : 'bg-slate-600/50 text-slate-400'
          }`}>
            {myTurn ? 'Your Turn' : 'Opponent Turn'}
          </span>
        </div>
        <button
          onClick={handleSurrender}
          className="flex items-center gap-2 text-red-400 hover:text-red-300 transition-colors"
        >
          <Flag className="w-5 h-5" />
          Surrender
        </button>
      </div>

      {/* Mulligan Modal */}
      {showMulligan && myPlayer.hand && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-2xl p-8 max-w-4xl w-full mx-4 border border-slate-600">
            <h2 className="text-2xl font-bold text-white mb-2">Mulligan Phase</h2>
            <p className="text-slate-400 mb-6">Select cards to return to your deck (click to toggle)</p>

            <div className="flex justify-center gap-4 mb-8">
              {myPlayer.hand.map((card, idx) => (
                <div
                  key={card.instance_id}
                  onClick={() => {
                    setMulliganSelection(prev =>
                      prev.includes(idx) ? prev.filter(i => i !== idx) : [...prev, idx]
                    )
                  }}
                  className={`transition-transform ${mulliganSelection.includes(idx) ? '-translate-y-4' : ''}`}
                >
                  <Card
                    id={card.id}
                    name={card.name}
                    power={card.power ?? undefined}
                    cost={card.cost ?? undefined}
                    color={card.colors}
                    imageUrl={card.image_link ?? undefined}
                    size="lg"
                    selected={mulliganSelection.includes(idx)}
                  />
                </div>
              ))}
            </div>

            <div className="flex justify-center gap-4">
              <button
                onClick={handleMulligan}
                className="bg-gradient-to-r from-op-red to-red-600 text-white font-bold px-8 py-3 rounded-lg"
              >
                {mulliganSelection.length > 0 ? `Mulligan ${mulliganSelection.length} cards` : 'Keep Hand'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Game Board */}
      <div className="pt-16 pb-4 px-4 flex flex-col min-h-screen">
        {/* Opponent Area */}
        <div className="flex-1 flex flex-col py-4">
          <OpponentArea
            player={opponent}
            onLeaderClick={() => handleLeaderClick(true)}
            onFieldCardClick={(idx) => handleFieldCardClick(idx, true)}
            targetMode={targetMode}
            gameState={gameState}
          />
        </div>

        {/* Center Area - DON and Controls */}
        <div className="h-24 flex items-center justify-center gap-8 my-4">
          <div
            className={`text-center cursor-pointer transition-all ${
              targetMode === 'attach_don' ? 'ring-2 ring-op-yellow rounded-lg p-2' : ''
            }`}
            onClick={handleDonPoolClick}
          >
            <div className="text-3xl font-bold text-op-yellow">{myPlayer.don_active}</div>
            <div className="text-xs text-slate-400">Active DON</div>
          </div>
          <div className="text-center">
            <div className="text-xl text-slate-500">/</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-slate-500">{myPlayer.total_don}</div>
            <div className="text-xs text-slate-400">Total DON</div>
          </div>
          <div className="w-px h-12 bg-slate-700 mx-4" />
          <button
            onClick={handleEndTurn}
            disabled={!myTurn}
            className={`font-bold px-8 py-3 rounded-lg transition-all ${
              myTurn
                ? 'bg-gradient-to-r from-op-red to-red-600 hover:from-red-600 hover:to-op-red text-white'
                : 'bg-slate-700 text-slate-500 cursor-not-allowed'
            }`}
          >
            End Turn
          </button>
          {targetMode !== 'none' && (
            <button
              onClick={clearSelection}
              className="text-slate-400 hover:text-white transition-colors"
            >
              Cancel
            </button>
          )}
        </div>

        {/* Player Area */}
        <div className="flex-1 flex flex-col py-4">
          <PlayerArea
            player={myPlayer}
            playerIndex={playerIndex}
            isMyTurn={myTurn}
            selectedCardIndex={selectedCardIndex}
            selectedCardZone={selectedCardZone}
            targetMode={targetMode}
            onHandCardClick={handleHandCardClick}
            onFieldCardClick={(idx) => handleFieldCardClick(idx, false)}
            onLeaderClick={() => handleLeaderClick(false)}
            gameState={gameState}
          />
        </div>
      </div>

      {/* Game Log Sidebar */}
      <div className="fixed right-4 bottom-4 w-64 max-h-48 bg-slate-800/90 backdrop-blur rounded-lg border border-slate-700 overflow-hidden">
        <div className="px-3 py-2 bg-slate-700/50 text-sm font-medium text-slate-300">
          Game Log
        </div>
        <div className="p-2 overflow-y-auto max-h-36 text-xs text-slate-400 space-y-1">
          {logs.slice(-10).map((log, idx) => (
            <div key={idx} className="py-0.5">{log}</div>
          ))}
          {logs.length === 0 && <div className="text-slate-500">No actions yet</div>}
        </div>
      </div>

      {/* Response Prompts */}
      {gameState.awaiting_response === 'blocker' && !myTurn && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-40">
          <div className="bg-slate-800 rounded-xl p-6 border border-slate-600">
            <h3 className="text-lg font-bold text-white mb-4">Block the Attack?</h3>
            <p className="text-slate-400 mb-4">Select a character with Blocker or pass</p>
            <button
              onClick={() => handleBlockerResponse(null)}
              className="bg-slate-700 text-white px-6 py-2 rounded-lg hover:bg-slate-600"
            >
              Don't Block
            </button>
          </div>
        </div>
      )}

      {gameState.awaiting_response === 'counter' && !myTurn && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-40">
          <div className="bg-slate-800 rounded-xl p-6 border border-slate-600">
            <h3 className="text-lg font-bold text-white mb-4">Use Counter?</h3>
            <p className="text-slate-400 mb-4">Select counter cards from hand or pass</p>
            <button
              onClick={() => handleCounterResponse([])}
              className="bg-slate-700 text-white px-6 py-2 rounded-lg hover:bg-slate-600"
            >
              No Counter
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

// Opponent Area Component
function OpponentArea({
  player,
  onLeaderClick,
  onFieldCardClick,
  targetMode,
  gameState,
}: {
  player: ReturnType<typeof getOpponentPlayer>
  onLeaderClick: () => void
  onFieldCardClick: (idx: number) => void
  targetMode: string
  gameState: BackendGameState
}) {
  const isValidTarget = targetMode === 'attack'

  return (
    <div className="flex-1 flex flex-col">
      {/* Opponent Info */}
      <div className="flex items-center justify-between px-4 py-2">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-slate-700 rounded-full flex items-center justify-center">
            <span className="text-xl">&#129302;</span>
          </div>
          <div>
            <div className="text-white font-semibold">{player.name}</div>
            <div className="text-sm text-slate-400">
              {gameState.active_player !== 0 && gameState.active_player !== 1 ? '' :
               gameState.active_player === (player.player_index) ? 'Their Turn' : ''}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-red-400">{player.life_count}</div>
            <div className="text-xs text-slate-400">Life</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-slate-400">{player.hand_count}</div>
            <div className="text-xs text-slate-400">Hand</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-op-yellow">{player.don_active}/{player.total_don}</div>
            <div className="text-xs text-slate-400">DON</div>
          </div>
        </div>
      </div>

      {/* Opponent Field */}
      <div className="flex-1 flex items-center justify-center gap-3 px-4">
        {/* Leader */}
        <div onClick={onLeaderClick} className={isValidTarget ? 'cursor-pointer' : ''}>
          <Card
            id={player.leader.id}
            name={player.leader.name}
            power={player.leader.power ?? undefined}
            color={player.leader.colors}
            imageUrl={player.leader.image_link ?? undefined}
            rested={player.leader.is_resting}
            highlighted={isValidTarget}
            size="md"
          />
          {player.leader.attached_don > 0 && (
            <div className="text-center text-xs text-op-yellow mt-1">
              +{player.leader.attached_don} DON
            </div>
          )}
        </div>

        {/* Field Cards */}
        {player.field.map((card, idx) => (
          <div
            key={card.instance_id}
            onClick={() => onFieldCardClick(idx)}
            className={isValidTarget ? 'cursor-pointer' : ''}
          >
            <Card
              id={card.id}
              name={card.name}
              power={card.power ?? undefined}
              cost={card.cost ?? undefined}
              color={card.colors}
              imageUrl={card.image_link ?? undefined}
              rested={card.is_resting}
              highlighted={isValidTarget}
              size="md"
            />
            {card.attached_don > 0 && (
              <div className="text-center text-xs text-op-yellow mt-1">
                +{card.attached_don} DON
              </div>
            )}
          </div>
        ))}

        {/* Empty slots */}
        {[...Array(Math.max(0, 5 - player.field.length))].map((_, i) => (
          <CardPlaceholder key={`empty-${i}`} size="md" />
        ))}
      </div>
    </div>
  )
}

// Player Area Component
function PlayerArea({
  player,
  playerIndex,
  isMyTurn,
  selectedCardIndex,
  selectedCardZone,
  targetMode,
  onHandCardClick,
  onFieldCardClick,
  onLeaderClick,
  gameState,
}: {
  player: ReturnType<typeof getMyPlayer>
  playerIndex: number
  isMyTurn: boolean
  selectedCardIndex: number | null
  selectedCardZone: string | null
  targetMode: string
  onHandCardClick: (idx: number) => void
  onFieldCardClick: (idx: number) => void
  onLeaderClick: () => void
  gameState: BackendGameState
}) {
  const isAttachDonTarget = targetMode === 'attach_don'

  return (
    <div className="flex-1 flex flex-col">
      {/* Player Field */}
      <div className="flex-1 flex items-center justify-center gap-3 px-4">
        {/* Leader */}
        <div onClick={onLeaderClick} className="cursor-pointer">
          <Card
            id={player.leader.id}
            name={player.leader.name}
            power={player.leader.power ?? undefined}
            color={player.leader.colors}
            imageUrl={player.leader.image_link ?? undefined}
            rested={player.leader.is_resting}
            selected={selectedCardZone === 'leader'}
            highlighted={isAttachDonTarget}
            size="md"
          />
          {player.leader.attached_don > 0 && (
            <div className="text-center text-xs text-op-yellow mt-1">
              +{player.leader.attached_don} DON
            </div>
          )}
        </div>

        {/* Field Cards */}
        {player.field.map((card, idx) => (
          <div key={card.instance_id} onClick={() => onFieldCardClick(idx)} className="cursor-pointer">
            <Card
              id={card.id}
              name={card.name}
              power={card.power ?? undefined}
              cost={card.cost ?? undefined}
              color={card.colors}
              imageUrl={card.image_link ?? undefined}
              rested={card.is_resting}
              selected={selectedCardZone === 'field' && selectedCardIndex === idx}
              highlighted={isAttachDonTarget}
              size="md"
            />
            {card.attached_don > 0 && (
              <div className="text-center text-xs text-op-yellow mt-1">
                +{card.attached_don} DON
              </div>
            )}
          </div>
        ))}

        {/* Empty slots */}
        {[...Array(Math.max(0, 5 - player.field.length))].map((_, i) => (
          <CardPlaceholder key={`empty-${i}`} size="md" />
        ))}
      </div>

      {/* Player Info & Hand */}
      <div className="px-4 py-2">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-op-blue rounded-full flex items-center justify-center">
              <span className="text-xl">&#128100;</span>
            </div>
            <div>
              <div className="text-white font-semibold">{player.name}</div>
              <div className={`text-sm ${isMyTurn ? 'text-green-400' : 'text-slate-400'}`}>
                {isMyTurn ? 'Your Turn' : 'Waiting...'}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-red-400">{player.life_count}</div>
              <div className="text-xs text-slate-400">Life</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-slate-300">{player.deck_count}</div>
              <div className="text-xs text-slate-400">Deck</div>
            </div>
          </div>
        </div>

        {/* Hand */}
        <div className="flex justify-center gap-2 overflow-x-auto pb-2 min-h-[120px]">
          {player.hand?.map((card, idx) => {
            const canPlay = isMyTurn && player.don_active >= (card.cost ?? 0)
            return (
              <div
                key={card.instance_id}
                onClick={() => onHandCardClick(idx)}
                className={`transition-transform flex-shrink-0 ${
                  canPlay ? 'cursor-pointer hover:-translate-y-2' : 'opacity-70'
                }`}
              >
                <Card
                  id={card.id}
                  name={card.name}
                  power={card.power ?? undefined}
                  cost={card.cost ?? undefined}
                  color={card.colors}
                  imageUrl={card.image_link ?? undefined}
                  selected={selectedCardZone === 'hand' && selectedCardIndex === idx}
                  size="md"
                />
              </div>
            )
          })}
          {(!player.hand || player.hand.length === 0) && (
            <div className="flex items-center justify-center text-slate-500">
              No cards in hand
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
