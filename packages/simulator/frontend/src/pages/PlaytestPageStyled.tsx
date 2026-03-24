import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { usePlaytestSocket, PlaytestCard, PlaytestPlayer } from '../hooks/usePlaytestSocket'
import { useDeckStore } from '../store/deckStore'

// Card back image URL - One Piece card back
const CARD_BACK = 'https://limitlesstcg.nyc3.digitaloceanspaces.com/one-piece/OP09/OP09_071_EN_SR.webp'

export function PlaytestPageStyled() {
  const navigate = useNavigate()
  const { currentDeck } = useDeckStore()
  const {
    isActive,
    isConnected,
    turn,
    activePlayer,
    phase,
    player1,
    player2,
    logs,
    gameOver,
    winner,
    awaitingResponse,
    pendingAttack,
    pendingChoice,
    error,
    startGame,
    playCard,
    attachDon,
    declareAttack,
    blockerResponse,
    counterResponse,
    activateEffect,
    endTurn,
    submitEffectChoice,
    resetGame,
  } = usePlaytestSocket()

  const [mulliganPhase, setMulliganPhase] = useState(true)
  const [selectedHandCard, setSelectedHandCard] = useState<number | null>(null)
  const [selectedFieldCard, setSelectedFieldCard] = useState<{ zone: 'leader' | 'field', index: number } | null>(null)
  const [selectedChoiceOptions, setSelectedChoiceOptions] = useState<string[]>([])
  const [selectedCounters, setSelectedCounters] = useState<number[]>([])

  // Start game when deck is selected and connected
  useEffect(() => {
    if (currentDeck && isConnected && !isActive && !gameOver) {
      const deckData = {
        leader: currentDeck.leaderId || 'ST01-001',
        cards: currentDeck.cards.reduce((acc, card) => {
          acc[card.cardId] = (acc[card.cardId] || 0) + card.count
          return acc
        }, {} as Record<string, number>)
      }
      startGame('Player', 'custom', deckData)
    }
  }, [currentDeck, isConnected, isActive, gameOver, startGame])

  // Reset selected options when pending choice changes
  useEffect(() => {
    setSelectedChoiceOptions([])
  }, [pendingChoice?.choiceId])

  const handleMulligan = () => {
    // Backend handles mulligan via socket
    setMulliganPhase(false)
  }

  const handleKeep = () => {
    setMulliganPhase(false)
  }

  const handleRestart = useCallback(() => {
    resetGame()
    setMulliganPhase(true)
    if (currentDeck && isConnected) {
      const deckData = {
        leader: currentDeck.leaderId || 'ST01-001',
        cards: currentDeck.cards.reduce((acc, card) => {
          acc[card.cardId] = (acc[card.cardId] || 0) + card.count
          return acc
        }, {} as Record<string, number>)
      }
      setTimeout(() => startGame('Player', 'custom', deckData), 100)
    }
  }, [currentDeck, isConnected, resetGame, startGame])

  const handleBack = useCallback(() => {
    resetGame()
    navigate('/deck-builder')
  }, [resetGame, navigate])

  const handlePlayCard = useCallback((index: number) => {
    playCard(index)
    setSelectedHandCard(null)
  }, [playCard])

  const handleAttachDon = useCallback((index: number) => {
    attachDon(index, 1)
  }, [attachDon])

  // Toggle selection for effect choices
  const handleToggleChoiceOption = useCallback((optionId: string) => {
    if (!pendingChoice) return

    setSelectedChoiceOptions(prev => {
      const isSelected = prev.includes(optionId)
      if (isSelected) {
        return prev.filter(id => id !== optionId)
      } else {
        // Check if we can add more selections
        if (prev.length < pendingChoice.maxSelections) {
          return [...prev, optionId]
        }
        // If at max and max is 1, replace the selection
        if (pendingChoice.maxSelections === 1) {
          return [optionId]
        }
        return prev
      }
    })
  }, [pendingChoice])

  // Submit the choice
  const handleSubmitChoice = useCallback(() => {
    if (!pendingChoice) return
    if (selectedChoiceOptions.length < pendingChoice.minSelections) return

    submitEffectChoice(pendingChoice.choiceId, selectedChoiceOptions)
    setSelectedChoiceOptions([])
  }, [pendingChoice, selectedChoiceOptions, submitEffectChoice])

  if (!currentDeck) {
    return (
      <div className="h-screen flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #8B4513 0%, #A0522D 50%, #8B4513 100%)' }}>
        <div className="text-center bg-black/50 p-8 rounded-lg">
          <p className="text-amber-200 mb-4">No deck selected</p>
          <button onClick={() => navigate('/deck-builder')} className="px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-500">
            Go to Deck Builder
          </button>
        </div>
      </div>
    )
  }

  // Connection status
  if (!isConnected) {
    return (
      <div className="h-screen flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #8B4513 0%, #A0522D 50%, #8B4513 100%)' }}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-amber-400 mx-auto mb-4"></div>
          <p className="text-amber-200">Connecting to game server...</p>
          <p className="text-amber-200/60 text-sm mt-2">Make sure backend is running on port 8000</p>
        </div>
      </div>
    )
  }

  if (!isActive) {
    return (
      <div className="h-screen flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #8B4513 0%, #A0522D 50%, #8B4513 100%)' }}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-amber-400 mx-auto mb-4"></div>
          <p className="text-amber-200">Starting game...</p>
          <p className="text-amber-200/60 text-sm mt-2">Deck Leader: {currentDeck?.leaderId || 'none'}</p>
          {error && (
            <div className="mt-4 bg-red-900/50 p-3 rounded">
              <p className="text-red-300 text-sm">{error}</p>
            </div>
          )}
        </div>
      </div>
    )
  }

  // Check if players are initialized
  if (!player1 || !player2 || !player1.leader || !player2.leader) {
    return (
      <div className="h-screen flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #8B4513 0%, #A0522D 50%, #8B4513 100%)' }}>
        <div className="text-center bg-red-900/50 p-6 rounded-lg">
          <p className="text-red-200 font-bold">Error: Game state not initialized</p>
          <p className="text-red-200/60 text-sm mt-2">Player1 Leader: {player1?.leader?.name || 'missing'}</p>
          <p className="text-red-200/60 text-sm">Player2 Leader: {player2?.leader?.name || 'missing'}</p>
          <button onClick={handleBack} className="mt-4 px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-500">
            Go Back
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen w-screen overflow-hidden relative" style={{
      background: 'linear-gradient(135deg, #8B4513 0%, #A0522D 50%, #8B4513 100%)',
      backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23000000' fill-opacity='0.1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
    }}>
      {/* Top Left - Opponent Hand Preview */}
      <div className="absolute left-4 top-4 z-10">
        <div className="bg-stone-900/70 rounded-xl p-3 backdrop-blur border border-stone-700">
          <div className="text-red-400 text-sm font-bold mb-2 text-center">OPPONENT ({player2.hand.length})</div>
          <div className="flex gap-1">
            {player2.hand.slice(0, 7).map((_, idx) => (
              <div key={idx} className="w-12 h-18 rounded-lg border-2 border-stone-600 overflow-hidden shadow-lg">
                <img src={CARD_BACK} alt="Card back" className="w-full h-full object-cover opacity-80" />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Left - Player 1 Hand (Horizontal) */}
      <div className="absolute left-4 bottom-4 z-20">
        <div className="bg-stone-900/70 rounded-xl p-3 backdrop-blur border border-stone-700">
          <div className="flex items-center justify-between mb-2">
            <div className="text-amber-200 text-sm font-bold">YOUR HAND ({player1.hand.length})</div>
            {selectedHandCard !== null && (
              <div className="flex gap-2">
                <button
                  onClick={() => handlePlayCard(selectedHandCard)}
                  className="px-3 py-1 bg-green-600 hover:bg-green-500 text-white rounded text-sm font-bold"
                >
                  Play Card
                </button>
                <button
                  onClick={() => setSelectedHandCard(null)}
                  className="px-3 py-1 bg-stone-600 hover:bg-stone-500 text-white rounded text-sm"
                >
                  Cancel
                </button>
              </div>
            )}
          </div>
          <div className="flex gap-2">
            {player1.hand.map((card, idx) => (
              <motion.div
                key={card.instanceId}
                whileHover={{ y: -10, scale: 1.05 }}
                onClick={() => setSelectedHandCard(idx)}
                className={`cursor-pointer transition-all ${selectedHandCard === idx ? 'ring-4 ring-yellow-400 rounded-lg' : ''}`}
              >
                <div className="w-20 h-28 rounded-lg border-2 border-amber-700 overflow-hidden shadow-xl relative">
                  {card.imageUrl ? (
                    <img src={card.imageUrl} alt={card.name} className="w-full h-full object-cover" />
                  ) : (
                    <div className="w-full h-full bg-gradient-to-br from-stone-600 to-stone-800 flex items-center justify-center text-[10px] text-white p-1 text-center">
                      {card.name}
                    </div>
                  )}
                  {/* Cost badge */}
                  <div className="absolute top-0 left-0 bg-black/70 text-white text-xs font-bold px-1.5 py-0.5 rounded-br">
                    {card.cost ?? 0}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Field Card Action Panel - Shows when a field card is selected */}
      {selectedFieldCard && (
        <div className="absolute bottom-4 right-4 z-30 bg-stone-900/95 rounded-xl p-4 backdrop-blur border border-stone-600 shadow-xl">
          <div className="text-amber-200 text-sm font-bold mb-3">
            {selectedFieldCard.zone === 'leader' ? 'Leader' : 'Character'} Actions
          </div>
          <div className="flex flex-col gap-2">
            <button
              onClick={() => {
                // Socket API: attackerIdx is -1 for leader, otherwise field index
                // targetIdx is -1 for opponent leader
                const attackerIdx = selectedFieldCard.zone === 'leader' ? -1 : selectedFieldCard.index
                declareAttack(attackerIdx, -1)  // -1 = attack opponent's leader
                setSelectedFieldCard(null)
              }}
              className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg text-sm font-bold"
            >
              Attack Leader
            </button>
            {player1.donActive > 0 && (
              <button
                onClick={() => {
                  // Socket API: cardIndex is -1 for leader, otherwise field index
                  const cardIdx = selectedFieldCard.zone === 'leader' ? -1 : selectedFieldCard.index
                  attachDon(cardIdx, 1)
                  setSelectedFieldCard(null)
                }}
                className="px-4 py-2 bg-yellow-600 hover:bg-yellow-500 text-white rounded-lg text-sm font-bold"
              >
                Attach DON (+1)
              </button>
            )}
            <button
              onClick={() => setSelectedFieldCard(null)}
              className="px-4 py-2 bg-stone-600 hover:bg-stone-500 text-white rounded-lg text-sm"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Right Sidebar - Version Info & Controls */}
      <div className="absolute right-4 top-4 z-10 flex flex-col gap-2 w-48">
        <div className="bg-stone-900/90 rounded-lg p-3 text-sm backdrop-blur border border-stone-700">
          <div className="text-amber-200 mb-2 font-bold">Turn {turn} - P{activePlayer + 1}</div>
          <div className="text-stone-300 text-xs space-y-1">
            <div>[You] {player1.leader?.name}</div>
            <div>[Opp] {player2.leader?.name}</div>
          </div>
          <div className="mt-2 max-h-24 overflow-y-auto text-[10px] text-stone-400 space-y-0.5 border-t border-stone-700 pt-2">
            {logs.slice(-8).map((log, idx) => (
              <div key={idx} className={log.startsWith('---') ? 'text-amber-400 font-medium' : ''}>
                {log}
              </div>
            ))}
          </div>
        </div>

        <button onClick={handleBack} className="px-4 py-2 bg-stone-800/90 text-white rounded-lg hover:bg-stone-700 text-sm font-medium">
          Back to Main
        </button>
        <button className="px-4 py-2 bg-stone-800/90 text-white rounded-lg hover:bg-stone-700 text-sm">
          Download Log
        </button>
        <button onClick={handleBack} className="px-4 py-2 bg-red-800/90 text-white rounded-lg hover:bg-red-700 text-sm">
          Cancel Match
        </button>
        <button onClick={handleRestart} className="px-4 py-2 bg-stone-800/90 text-white rounded-lg hover:bg-stone-700 text-sm">
          Restart Turn
        </button>
      </div>

      {/* Main Game Board - Takes up most of the screen */}
      <div className="absolute top-4 bottom-4 left-[280px] right-[200px] flex items-center justify-center">
        <div className="w-full h-full relative">

          {/* ============ OPPONENT SIDE (TOP) ============ */}
          <div className="absolute top-0 left-0 right-0 h-[50%] transform rotate-180">
            <PlayerPlayArea
              player={player2}
              isOpponent={true}
              onCardClick={() => {}}
            />
          </div>

          {/* ============ PLAYER SIDE (BOTTOM) - Touches opponent side ============ */}
          <div className="absolute bottom-0 left-0 right-0 h-[50%]">
            <PlayerPlayArea
              player={player1}
              isOpponent={false}
              selectedFieldCard={selectedFieldCard}
              onCardClick={(zone, index) => {
                setSelectedFieldCard({ zone: zone as 'leader' | 'field', index })
                setSelectedHandCard(null)
              }}
              onPlayCard={(idx) => playCard(0, idx)}
              onAttachDon={(zone, idx) => attachDon(0, zone, idx)}
              onEndTurn={endTurn}
              activePlayer={activePlayer}
            />
          </div>
        </div>
      </div>

      {/* Mulligan Modal */}
      {mulliganPhase && (
        <div className="absolute inset-0 bg-black/60 flex items-center justify-center z-50">
          <div className="absolute right-8 bottom-40 flex flex-col gap-3">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleMulligan}
              className="px-16 py-5 bg-stone-200 text-stone-800 rounded-xl text-2xl font-bold shadow-xl hover:bg-white border-4 border-stone-400"
            >
              Mulligan
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleKeep}
              className="px-16 py-5 bg-stone-200 text-stone-800 rounded-xl text-2xl font-bold shadow-xl hover:bg-white border-4 border-stone-400"
            >
              Keep
            </motion.button>
          </div>
        </div>
      )}

      {/* Effect Choice Modal */}
      {pendingChoice && (
        <div className="absolute inset-0 bg-black/70 flex items-center justify-center z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-stone-900 rounded-xl p-6 max-w-lg w-full mx-4 border-2 border-amber-600 shadow-2xl"
          >
            {/* Header */}
            <div className="text-center mb-4">
              {pendingChoice.sourceCardName && (
                <div className="text-amber-400 text-sm font-medium mb-1">
                  {pendingChoice.sourceCardName}
                </div>
              )}
              <h2 className="text-amber-200 text-xl font-bold">
                {pendingChoice.prompt}
              </h2>
              <div className="text-stone-400 text-sm mt-1">
                Select {pendingChoice.minSelections === pendingChoice.maxSelections
                  ? pendingChoice.minSelections
                  : `${pendingChoice.minSelections}-${pendingChoice.maxSelections}`} option(s)
              </div>
            </div>

            {/* Options */}
            <div className="space-y-2 max-h-64 overflow-y-auto mb-4">
              {pendingChoice.options.map((option) => {
                const isSelected = selectedChoiceOptions.includes(option.id)
                return (
                  <motion.button
                    key={option.id}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleToggleChoiceOption(option.id)}
                    className={`w-full p-3 rounded-lg border-2 text-left transition-all ${
                      isSelected
                        ? 'border-amber-500 bg-amber-900/50 text-amber-100'
                        : 'border-stone-600 bg-stone-800 text-stone-200 hover:border-stone-500'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                        isSelected ? 'border-amber-500 bg-amber-500' : 'border-stone-500'
                      }`}>
                        {isSelected && (
                          <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        )}
                      </div>
                      <span className="font-medium">{option.label}</span>
                    </div>
                  </motion.button>
                )
              })}
            </div>

            {/* Submit Button */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleSubmitChoice}
              disabled={selectedChoiceOptions.length < pendingChoice.minSelections}
              className={`w-full py-3 rounded-lg font-bold text-lg transition-all ${
                selectedChoiceOptions.length >= pendingChoice.minSelections
                  ? 'bg-amber-600 hover:bg-amber-500 text-white'
                  : 'bg-stone-700 text-stone-400 cursor-not-allowed'
              }`}
            >
              Confirm Selection ({selectedChoiceOptions.length}/{pendingChoice.minSelections})
            </motion.button>
          </motion.div>
        </div>
      )}

      {/* Blocker Selection Modal */}
      {awaitingResponse === 'blocker' && pendingAttack && (
        <div className="absolute inset-0 bg-black/70 flex items-center justify-center z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-stone-900 rounded-xl p-6 max-w-lg w-full mx-4 border-2 border-blue-600 shadow-2xl"
          >
            {/* Header */}
            <div className="text-center mb-4">
              <div className="text-blue-400 text-sm font-medium mb-1">
                ⚔️ Attack Incoming!
              </div>
              <h2 className="text-blue-200 text-xl font-bold">
                {pendingAttack.attackerName} (Power: {pendingAttack.attackerPower}) attacks {pendingAttack.targetName}!
              </h2>
              <div className="text-stone-400 text-sm mt-1">
                Choose a blocker or pass
              </div>
            </div>

            {/* Available Blockers */}
            <div className="space-y-2 max-h-48 overflow-y-auto mb-4">
              {pendingAttack.availableBlockers && pendingAttack.availableBlockers.length > 0 ? (
                pendingAttack.availableBlockers.map((blocker) => (
                  <motion.button
                    key={blocker.index}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => {
                      blockerResponse(blocker.index)
                      setSelectedCounters([])
                    }}
                    className="w-full p-3 rounded-lg border-2 border-blue-600 bg-blue-900/50 text-blue-100 hover:bg-blue-800/50 text-left transition-all"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium">🛡️ {blocker.name}</span>
                      <span className="text-blue-300">Power: {blocker.power}</span>
                    </div>
                  </motion.button>
                ))
              ) : (
                <div className="text-stone-400 text-center py-4">
                  No blockers available
                </div>
              )}
            </div>

            {/* Pass Button */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => {
                blockerResponse(null)
                setSelectedCounters([])
              }}
              className="w-full py-3 rounded-lg font-bold text-lg bg-stone-700 hover:bg-stone-600 text-stone-200 transition-all"
            >
              Don't Block (Pass)
            </motion.button>
          </motion.div>
        </div>
      )}

      {/* Counter Selection Modal */}
      {awaitingResponse === 'counter' && pendingAttack && (
        <div className="absolute inset-0 bg-black/70 flex items-center justify-center z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-stone-900 rounded-xl p-6 max-w-lg w-full mx-4 border-2 border-purple-600 shadow-2xl"
          >
            {/* Header */}
            <div className="text-center mb-4">
              <div className="text-purple-400 text-sm font-medium mb-1">
                🛡️ Counter Step
              </div>
              <h2 className="text-purple-200 text-xl font-bold">
                Defending against {pendingAttack.attackerName}
              </h2>
              <div className="text-stone-300 text-sm mt-2">
                Attack Power: <span className="text-red-400 font-bold">{pendingAttack.attackerPower}</span>
                {' vs '}
                Defense: <span className="text-green-400 font-bold">
                  {(pendingAttack.targetPower || 0) + selectedCounters.reduce((sum, idx) => {
                    const counter = pendingAttack.availableCounters?.find(c => c.index === idx)
                    return sum + (counter?.counterValue || 0)
                  }, 0)}
                </span>
              </div>
            </div>

            {/* Available Counters */}
            <div className="space-y-2 max-h-48 overflow-y-auto mb-4">
              {pendingAttack.availableCounters && pendingAttack.availableCounters.length > 0 ? (
                pendingAttack.availableCounters.map((counter) => {
                  const isSelected = selectedCounters.includes(counter.index)
                  return (
                    <motion.button
                      key={counter.index}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => {
                        setSelectedCounters(prev =>
                          isSelected
                            ? prev.filter(i => i !== counter.index)
                            : [...prev, counter.index]
                        )
                      }}
                      className={`w-full p-3 rounded-lg border-2 text-left transition-all ${
                        isSelected
                          ? 'border-purple-500 bg-purple-900/50 text-purple-100'
                          : 'border-stone-600 bg-stone-800 text-stone-200 hover:border-stone-500'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                            isSelected ? 'border-purple-500 bg-purple-500' : 'border-stone-500'
                          }`}>
                            {isSelected && (
                              <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                              </svg>
                            )}
                          </div>
                          <span className="font-medium">{counter.name}</span>
                        </div>
                        <div className="text-right">
                          <span className="text-purple-300">+{counter.counterValue}</span>
                          {counter.cost > 0 && (
                            <span className="text-amber-400 ml-2">({counter.cost} DON)</span>
                          )}
                        </div>
                      </div>
                    </motion.button>
                  )
                })
              ) : (
                <div className="text-stone-400 text-center py-4">
                  No counter cards available
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => {
                  counterResponse([])
                  setSelectedCounters([])
                }}
                className="flex-1 py-3 rounded-lg font-bold text-lg bg-stone-700 hover:bg-stone-600 text-stone-200 transition-all"
              >
                Don't Counter
              </motion.button>
              {selectedCounters.length > 0 && (
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => {
                    counterResponse(selectedCounters)
                    setSelectedCounters([])
                  }}
                  className="flex-1 py-3 rounded-lg font-bold text-lg bg-purple-600 hover:bg-purple-500 text-white transition-all"
                >
                  Use Counters (+{selectedCounters.reduce((sum, idx) => {
                    const counter = pendingAttack.availableCounters?.find(c => c.index === idx)
                    return sum + (counter?.counterValue || 0)
                  }, 0)})
                </motion.button>
              )}
            </div>
          </motion.div>
        </div>
      )}

      {/* Version Watermark */}
      <div className="absolute bottom-2 right-2 text-stone-500 text-xs">
        v1.36
      </div>
    </div>
  )
}

// Stacked Life Cards Component - looks like facedown cards stacked
function LifeCardStack({ count }: { count: number }) {
  return (
    <div className="relative w-16 h-24">
      {/* Create stack effect with offset cards */}
      {Array.from({ length: Math.min(count, 5) }).map((_, idx) => (
        <div
          key={idx}
          className="absolute rounded-lg border-2 border-stone-500 overflow-hidden shadow-md"
          style={{
            width: '64px',
            height: '96px',
            top: `${idx * 3}px`,
            left: `${idx * 2}px`,
            zIndex: count - idx,
          }}
        >
          <div className="w-full h-full bg-gradient-to-br from-red-800 via-red-700 to-red-900 flex items-center justify-center">
            <div className="text-red-300 text-xs font-bold transform -rotate-12">LIFE</div>
          </div>
        </div>
      ))}
      {/* Life count badge */}
      <div className="absolute -bottom-2 -right-2 bg-red-600 text-white text-sm font-bold w-7 h-7 rounded-full flex items-center justify-center border-2 border-red-400 z-20">
        {count}
      </div>
    </div>
  )
}

// Deck Stack Component - looks like facedown One Piece cards
function DeckStack({ count }: { count: number }) {
  return (
    <div className="relative w-16 h-24">
      {/* Stack effect */}
      {Array.from({ length: Math.min(3, Math.ceil(count / 15)) }).map((_, idx) => (
        <div
          key={idx}
          className="absolute rounded-lg border-2 border-stone-600 overflow-hidden shadow-lg"
          style={{
            width: '64px',
            height: '96px',
            top: `${idx * 2}px`,
            left: `${idx * 1}px`,
            zIndex: 3 - idx,
          }}
        >
          <div className="w-full h-full bg-gradient-to-br from-stone-700 via-stone-600 to-stone-800 flex items-center justify-center">
            <div className="text-center">
              <div className="text-amber-400 text-[8px] font-bold">ONE PIECE</div>
              <div className="text-stone-400 text-[6px]">CARD GAME</div>
            </div>
          </div>
        </div>
      ))}
      {/* Deck count badge */}
      <div className="absolute -bottom-2 -right-2 bg-amber-600 text-white text-sm font-bold w-8 h-8 rounded-full flex items-center justify-center border-2 border-amber-400 z-20">
        {count}
      </div>
    </div>
  )
}

// Trash Stack Component
function TrashStack({ count }: { count: number }) {
  return (
    <div className="relative w-14 h-20">
      <div className="w-full h-full rounded-lg border-2 border-dashed border-stone-600 bg-stone-800/50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-stone-500 text-[8px] font-bold">TRASH</div>
          <div className="text-stone-400 text-lg font-bold">{count}</div>
        </div>
      </div>
    </div>
  )
}

// Color mapping for leader colors
const COLOR_MAP: Record<string, { from: string; to: string; border: string; text: string }> = {
  'Red': { from: '#7f1d1d', to: '#991b1b', border: '#dc2626', text: '#fca5a5' },
  'Blue': { from: '#1e3a5f', to: '#1e40af', border: '#3b82f6', text: '#93c5fd' },
  'Green': { from: '#14532d', to: '#166534', border: '#22c55e', text: '#86efac' },
  'Purple': { from: '#4c1d95', to: '#5b21b6', border: '#8b5cf6', text: '#c4b5fd' },
  'Black': { from: '#1c1917', to: '#292524', border: '#57534e', text: '#a8a29e' },
  'Yellow': { from: '#713f12', to: '#854d0e', border: '#eab308', text: '#fef08a' },
}

// Get gradient colors from leader
function getLeaderColors(leader: PlaytestCard | null | undefined): { gradient: string; border: string; text: string } {
  const defaultColors = { gradient: 'linear-gradient(to bottom, #1e1b4b 0%, #312e81 100%)', border: '#4f46e5', text: '#a5b4fc' }

  if (!leader) {
    return defaultColors
  }

  try {
    // Get color from leader - could be in 'color' or 'colors' field (as string or array)
    let colorStr = ''
    const leaderAny = leader as any
    if (Array.isArray(leaderAny.colors)) {
      colorStr = leaderAny.colors.join('/')
    } else if (typeof leaderAny.colors === 'string') {
      colorStr = leaderAny.colors
    } else if (typeof leaderAny.color === 'string') {
      colorStr = leaderAny.color
    }

    const colors = colorStr.split('/').map((c: string) => c.trim()).filter(Boolean)

    if (colors.length === 0) {
      return defaultColors
    }

    if (colors.length === 1) {
      const c = COLOR_MAP[colors[0]] || COLOR_MAP['Blue']
      return {
        gradient: `linear-gradient(to bottom, ${c.from} 0%, ${c.to} 100%)`,
        border: c.border,
        text: c.text
      }
    }

    // Multi-color gradient
    const c1 = COLOR_MAP[colors[0]] || COLOR_MAP['Blue']
    const c2 = COLOR_MAP[colors[1]] || COLOR_MAP['Red']
    return {
      gradient: `linear-gradient(135deg, ${c1.from} 0%, ${c1.to} 50%, ${c2.to} 50%, ${c2.from} 100%)`,
      border: c1.border,
      text: c1.text
    }
  } catch (e) {
    console.error('Error parsing leader colors:', e)
    return defaultColors
  }
}

// Player Play Area Component - New Layout
function PlayerPlayArea({
  player,
  isOpponent,
  selectedFieldCard,
  onCardClick,
  onPlayCard,
  onAttachDon,
  onEndTurn,
  activePlayer,
}: {
  player: PlaytestPlayer
  isOpponent: boolean
  selectedFieldCard?: { zone: 'leader' | 'field', index: number } | null
  onCardClick: (zone: string, index: number) => void
  onPlayCard?: (idx: number) => void
  onAttachDon?: (zone: 'leader' | 'field', idx?: number) => void
  onEndTurn?: () => void
  activePlayer?: number
}) {
  const leaderColors = getLeaderColors(player.leader)

  return (
    <div className="h-full flex flex-col">
      {/* CHARACTER AREA - Top section */}
      <div
        className="flex-1 border-y"
        style={{
          background: leaderColors.gradient,
          borderColor: `${leaderColors.border}50`
        }}
      >
        <div className="text-center text-sm font-bold py-1 opacity-40" style={{ color: leaderColors.text }}>CHARACTER AREA</div>
        <div className="flex items-center justify-center gap-3 px-4">
          {/* Field Cards */}
          {player.field.map((card, idx) => (
            <div
              key={card.instanceId}
              onClick={() => !isOpponent && onCardClick('field', idx)}
              className={`relative cursor-pointer ${selectedFieldCard?.zone === 'field' && selectedFieldCard?.index === idx ? 'ring-4 ring-yellow-400 rounded-lg' : ''}`}
            >
              <div className={`w-16 h-24 rounded-lg border-2 overflow-hidden shadow-lg ${card.isResting ? 'rotate-90' : ''}`} style={{ borderColor: `${leaderColors.border}80` }}>
                {card.imageUrl ? (
                  <img src={card.imageUrl} alt={card.name} className="w-full h-full object-cover" />
                ) : (
                  <div className="w-full h-full bg-gradient-to-br from-stone-600 to-stone-800 flex items-center justify-center text-[8px] text-white">
                    {card.name}
                  </div>
                )}
              </div>
              {card.attachedDon > 0 && (
                <div className="absolute -bottom-1 -right-1 bg-yellow-500 text-black text-[10px] font-bold w-5 h-5 rounded-full flex items-center justify-center border border-yellow-300">
                  +{card.attachedDon}
                </div>
              )}
            </div>
          ))}
          {/* Empty slots */}
          {Array.from({ length: Math.max(0, 5 - player.field.length) }).map((_, i) => (
            <div key={`empty-${i}`} className="w-16 h-24 rounded-lg border-2 border-dashed" style={{ borderColor: `${leaderColors.border}30` }} />
          ))}
        </div>
      </div>

      {/* LEADER ROW - Leader + Stage side by side, with Life on left, Deck/Trash on right */}
      <div
        className="h-32 flex items-center justify-between px-6 border-y"
        style={{
          background: `linear-gradient(to bottom, ${leaderColors.border}20 0%, ${leaderColors.border}10 100%)`,
          borderColor: `${leaderColors.border}30`
        }}
      >
        {/* Left: Life Cards */}
        <div className="flex flex-col items-center">
          <LifeCardStack count={player.lifeCards.length} />
          <div className="text-red-400 text-xs font-bold mt-1">LIFE</div>
        </div>

        {/* Center: Leader + Stage */}
        <div className="flex items-center gap-4">
          {/* Leader Card */}
          <div
            onClick={() => !isOpponent && onCardClick('leader', 0)}
            className={`relative cursor-pointer ${selectedFieldCard?.zone === 'leader' ? 'ring-4 ring-yellow-400 rounded-lg' : ''}`}
          >
            <div className={`w-20 h-28 rounded-lg border-3 border-amber-500 overflow-hidden shadow-xl ${player.leader?.isResting ? 'rotate-90' : ''}`}>
              {player.leader?.imageUrl ? (
                <img src={player.leader.imageUrl} alt={player.leader.name} className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full bg-gradient-to-br from-amber-600 to-amber-800 flex items-center justify-center text-xs text-white font-bold">
                  {player.leader?.name}
                </div>
              )}
            </div>
            {player.leader?.attachedDon > 0 && (
              <div className="absolute -bottom-2 -right-2 bg-yellow-500 text-black text-sm font-bold w-6 h-6 rounded-full flex items-center justify-center border-2 border-yellow-300">
                +{player.leader.attachedDon}
              </div>
            )}
            <div className="text-amber-400 text-[10px] font-bold text-center mt-1">LEADER</div>
          </div>

          {/* Stage Card */}
          <div className="flex flex-col items-center">
            <div className="w-16 h-24 rounded-lg border-2 border-teal-600 bg-teal-900/50 flex items-center justify-center">
              <span className="text-teal-400 text-xs font-bold">STAGE</span>
            </div>
            <div className="text-teal-400 text-[10px] font-bold mt-1">STAGE</div>
          </div>
        </div>

        {/* Right: Deck + Trash stacked */}
        <div className="flex flex-col items-center gap-2">
          <DeckStack count={player.deck.length} />
          <TrashStack count={player.trash.length} />
        </div>
      </div>

      {/* DON AREA - Bottom section */}
      <div
        className="h-16 flex items-center justify-center gap-2 px-4 border-t"
        style={{
          background: `linear-gradient(to right, ${leaderColors.border}40 0%, ${leaderColors.border}30 100%)`,
          borderColor: `${leaderColors.border}50`
        }}
      >
        <div className="text-xs font-bold mr-2" style={{ color: leaderColors.text }}>DON!!</div>
        <div className="flex gap-1">
          {Array.from({ length: Math.min(10, player.donActive + player.donRested) }).map((_, i) => (
            <div
              key={i}
              className={`w-8 h-12 rounded border-2 flex items-center justify-center text-xs font-bold ${
                i < player.donActive
                  ? 'border-yellow-400 bg-yellow-500/30 text-yellow-300'
                  : 'border-stone-500 bg-stone-600/30 text-stone-500'
              }`}
            >
              D
            </div>
          ))}
        </div>
        <div className="text-yellow-300 text-sm font-bold ml-2">
          {player.donActive}/{player.donActive + player.donRested}
        </div>
        {!isOpponent && (
          <button
            onClick={onEndTurn}
            className="ml-4 px-4 py-2 bg-green-600 hover:bg-green-500 text-white rounded-lg text-sm font-bold shadow-lg"
          >
            End Turn
          </button>
        )}
      </div>
    </div>
  )
}

export default PlaytestPageStyled
