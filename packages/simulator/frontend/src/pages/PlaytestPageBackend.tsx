/**
 * Backend-driven Playtest Page
 *
 * This page uses the shared game-engine via Socket.IO for all game logic.
 * Effects are processed server-side, ensuring consistency with the training model.
 */

import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, RotateCcw, Swords, Shield, Zap, Heart, Layers, Trash2 } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { usePlaytestSocket, PlaytestCard, PlaytestPlayer } from '../hooks/usePlaytestSocket'
import { useDeckStore } from '../store/deckStore'

export function PlaytestPageBackend() {
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
    triggerResponse,
    leaderEffectResponse,
    blockerResponse,
    counterResponse,
    activateEffect,
    endTurn,
    resetGame,
    submitEffectChoice,
    debugSetScenario,
  } = usePlaytestSocket()

  const [selectedHandIndex, setSelectedHandIndex] = useState<number | null>(null)
  const [selectedFieldIndex, setSelectedFieldIndex] = useState<number | null>(null)
  const [attackMode, setAttackMode] = useState(false)
  const [debugOpen, setDebugOpen] = useState(false)
  const [debugCardInput, setDebugCardInput] = useState('')
  // Counter step: track which counter cards the defending player is selecting
  const [selectedCounterIndices, setSelectedCounterIndices] = useState<number[]>([])
  // Hovered card preview
  const [hoveredCard, setHoveredCard] = useState<PlaytestCard | null>(null)

  // Clear selection when turn changes (so you don't have wrong player's card selected)
  useEffect(() => {
    setSelectedHandIndex(null)
    setSelectedFieldIndex(null)
    setAttackMode(false)
  }, [activePlayer])

  // Start game when deck is selected and connected
  useEffect(() => {
    if (currentDeck && isConnected && !isActive && !gameOver) {
      // Build deck data from the current deck
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

  const handleBack = useCallback(() => {
    resetGame()
    navigate('/deck-builder')
  }, [resetGame, navigate])

  const handleRestart = useCallback(() => {
    resetGame()
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

  const handlePlayCard = useCallback((index: number) => {
    playCard(index)
    setSelectedHandIndex(null)
  }, [playCard])

  const handleAttachDon = useCallback((index: number) => {
    attachDon(index, 1)
  }, [attachDon])

  const handleDeclareAttack = useCallback((attackerIdx: number, targetIdx: number) => {
    declareAttack(attackerIdx, targetIdx)
    setAttackMode(false)
    setSelectedFieldIndex(null)
  }, [declareAttack])

  // No deck selected
  if (!currentDeck) {
    return (
      <div className="h-screen flex items-center justify-center bg-stone-900">
        <div className="text-center">
          <p className="text-amber-200/60 mb-4">No deck selected</p>
          <button
            onClick={() => navigate('/deck-builder')}
            className="px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-500"
          >
            Go to Deck Builder
          </button>
        </div>
      </div>
    )
  }

  // Connecting
  if (!isConnected) {
    return (
      <div className="h-screen flex flex-col items-center justify-center bg-stone-900 gap-4">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-amber-400"></div>
        <p className="text-amber-200/60">Connecting to game server...</p>
        {error && <p className="text-red-400">{error}</p>}
      </div>
    )
  }

  // Loading game
  if (!isActive && !gameOver) {
    return (
      <div className="h-screen flex flex-col items-center justify-center bg-stone-900 gap-4">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-amber-400"></div>
        <p className="text-amber-200/60">Starting game...</p>
      </div>
    )
  }

  // In playtest mode, user controls BOTH players
  const currentPlayer = activePlayer === 0 ? player1 : player2

  return (
    <div className="h-screen flex flex-col bg-stone-900 overflow-hidden">
      {/* Top Bar */}
      <div className="flex-shrink-0 bg-stone-800/90 border-b border-amber-900/50 px-4 py-2 flex items-center justify-between">
        <button
          onClick={handleBack}
          className="flex items-center gap-2 text-amber-200/70 hover:text-amber-100 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          Exit
        </button>
        <div className="flex items-center gap-4">
          <span className="text-amber-200/60">Turn {turn}</span>
          <span className="text-amber-200/60">Phase: {phase}</span>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
            activePlayer === 0 ? 'bg-blue-500/20 text-blue-400' : 'bg-red-500/20 text-red-400'
          }`}>
            {activePlayer === 0 ? 'Player 1 Turn' : 'Player 2 Turn'}
          </span>
          {awaitingResponse && (
            <span className="px-2 py-1 bg-yellow-500/20 text-yellow-400 text-xs rounded">
              {awaitingResponse === 'trigger' ? 'Trigger Step'
               : awaitingResponse === 'leader_effect' ? 'Leader Effect Step'
               : awaitingResponse === 'blocker' ? 'Blocker Step'
               : 'Counter Step'}
            </span>
          )}
        </div>
        <button
          onClick={handleRestart}
          className="flex items-center gap-2 text-amber-200/70 hover:text-amber-100 transition-colors"
        >
          <RotateCcw className="w-5 h-5" />
          Restart
        </button>
      </div>

      {/* Game Board */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Player 2 Area - Top (user controls this too in playtest!) */}
        <div className="flex-1 bg-red-900/10 border-l-4 border-red-500/30 p-3">
          <PlayerBoard
            player={player2}
            isOpponent={activePlayer === 0}  // Only "opponent" when it's Player 1's turn
            isActive={activePlayer === 1}
            isOwnerTurn={activePlayer === 1}
            onSelectCard={(zone, idx) => {
              if (activePlayer === 1) {  // Allow selecting when it's Player 2's turn
                if (zone === 'hand') {
                  setSelectedHandIndex(idx)
                  setSelectedFieldIndex(null)
                  setAttackMode(false)
                } else if (zone === 'field') {
                  setSelectedFieldIndex(idx)
                  setSelectedHandIndex(null)
                }
              }
            }}
            selectedIndex={activePlayer === 1 ? (selectedHandIndex !== null ? selectedHandIndex : selectedFieldIndex) : null}
            selectedZone={activePlayer === 1 ? (selectedHandIndex !== null ? 'hand' : selectedFieldIndex !== null ? 'field' : undefined) : undefined}
            onHoverCard={setHoveredCard}
          />
        </div>

        {/* Combat Action Panel — replaces simple divider during combat */}
        {pendingAttack ? (
          <div className="flex-shrink-0 bg-stone-900 border-y-2 border-red-700/60 px-4 py-2">
            {/* Attack summary */}
            <div className="flex items-center gap-3 mb-2">
              <Swords className="w-5 h-5 text-red-400 flex-shrink-0" />
              <span className="text-red-300 font-semibold text-sm">
                {pendingAttack.attackerName} ({pendingAttack.attackerPower.toLocaleString()})
                {' → '}
                {pendingAttack.targetName} ({pendingAttack.targetPower.toLocaleString()})
              </span>
              {pendingAttack.counterPower > 0 && (
                <span className="text-green-400 text-xs">+{pendingAttack.counterPower.toLocaleString()} counter</span>
              )}
            </div>

            {/* Step 1 — Leader Effect */}
            {awaitingResponse === 'leader_effect' && (
              <div className="bg-purple-900/40 border border-purple-600/50 rounded-lg p-3">
                <p className="text-purple-300 font-semibold text-sm mb-2">
                  <Shield className="w-4 h-4 inline mr-1" />
                  Leader Effect Stage
                </p>
                {pendingAttack.leaderHasEffect ? (
                  <>
                    <p className="text-stone-300 text-xs mb-2">Your leader has a combat ability. Use it?</p>
                    <div className="flex gap-2">
                      <button onClick={() => leaderEffectResponse(true)}
                        className="px-4 py-1.5 bg-purple-600 hover:bg-purple-500 text-white rounded text-sm font-medium">
                        Use Leader Effect
                      </button>
                      <button onClick={() => leaderEffectResponse(false)}
                        className="px-4 py-1.5 bg-stone-600 hover:bg-stone-500 text-white rounded text-sm">
                        No Leader Effect
                      </button>
                    </div>
                  </>
                ) : (
                  <div className="flex items-center gap-2">
                    <p className="text-stone-400 text-xs">No leader effect available.</p>
                    <button onClick={() => leaderEffectResponse(false)}
                      className="px-4 py-1.5 bg-stone-600 hover:bg-stone-500 text-white rounded text-sm">
                      Continue
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* Step 2 — Blocker */}
            {awaitingResponse === 'blocker' && (
              <div className="bg-blue-900/40 border border-blue-600/50 rounded-lg p-3">
                <p className="text-blue-300 font-semibold text-sm mb-2">
                  <Shield className="w-4 h-4 inline mr-1" />
                  Blocker Step — Defender may activate a blocker
                </p>
                <div className="flex flex-wrap gap-2">
                  {pendingAttack.availableBlockers.length > 0 ? (
                    pendingAttack.availableBlockers.map(b => (
                      <button key={b.index}
                        onClick={() => blockerResponse(b.index)}
                        className="px-3 py-1.5 bg-blue-700 hover:bg-blue-600 text-white rounded text-sm">
                        {b.name} ({(b.power).toLocaleString()})
                      </button>
                    ))
                  ) : (
                    <span className="text-stone-400 text-xs self-center">No blockers available.</span>
                  )}
                  <button onClick={() => blockerResponse(null)}
                    className="px-4 py-1.5 bg-stone-600 hover:bg-stone-500 text-white rounded text-sm font-medium">
                    No Blocker
                  </button>
                </div>
              </div>
            )}

            {/* Step 3 — Counter */}
            {awaitingResponse === 'counter' && (
              <div className="bg-green-900/40 border border-green-600/50 rounded-lg p-3">
                <p className="text-green-300 font-semibold text-sm mb-2">
                  <Shield className="w-4 h-4 inline mr-1" />
                  Counter Step — Defender may use counter cards
                </p>
                {pendingAttack.availableCounters.length > 0 ? (
                  <div className="space-y-2">
                    <div className="flex flex-wrap gap-2">
                      {pendingAttack.availableCounters.map(c => {
                        const isSelected = selectedCounterIndices.includes(c.index)
                        return (
                          <button key={c.index}
                            onClick={() => setSelectedCounterIndices(prev =>
                              isSelected ? prev.filter(i => i !== c.index) : [...prev, c.index]
                            )}
                            className={`px-3 py-1.5 rounded text-sm border transition-colors ${
                              isSelected
                                ? 'bg-green-600 border-green-400 text-white'
                                : 'bg-stone-700 border-stone-500 text-stone-300 hover:border-green-500'
                            }`}>
                            {c.name} (+{c.counterValue.toLocaleString()})
                            {c.isEvent && <span className="text-xs ml-1 text-yellow-400">[{c.cost} DON]</span>}
                          </button>
                        )
                      })}
                    </div>
                    <div className="flex gap-2 items-center">
                      {selectedCounterIndices.length > 0 && (
                        <button onClick={() => { counterResponse(selectedCounterIndices); setSelectedCounterIndices([]) }}
                          className="px-4 py-1.5 bg-green-600 hover:bg-green-500 text-white rounded text-sm font-medium">
                          Use Selected Counters
                        </button>
                      )}
                      <button onClick={() => { counterResponse([]); setSelectedCounterIndices([]) }}
                        className="px-4 py-1.5 bg-stone-600 hover:bg-stone-500 text-white rounded text-sm">
                        No Counter
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <span className="text-stone-400 text-xs">No counter cards available.</span>
                    <button onClick={() => { counterResponse([]); setSelectedCounterIndices([]) }}
                      className="px-4 py-1.5 bg-stone-600 hover:bg-stone-500 text-white rounded text-sm">
                      No Counter
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* Step 4 — Trigger */}
            {awaitingResponse === 'trigger' && pendingAttack.pendingTrigger && (
              <div className="bg-amber-900/40 border border-amber-600/50 rounded-lg p-3">
                <p className="text-amber-300 font-semibold text-sm mb-2">
                  <Shield className="w-4 h-4 inline mr-1" />
                  Trigger Step — Life card has a trigger!
                </p>
                <div className="mb-2">
                  <span className="text-white font-medium text-sm">{pendingAttack.pendingTrigger.cardName}</span>
                  <p className="text-amber-200/80 text-xs mt-1">{pendingAttack.pendingTrigger.triggerText}</p>
                </div>
                <div className="flex gap-2">
                  <button onClick={() => triggerResponse(true)}
                    className="px-4 py-1.5 bg-amber-600 hover:bg-amber-500 text-white rounded text-sm font-medium">
                    Activate Trigger
                  </button>
                  <button onClick={() => triggerResponse(false)}
                    className="px-4 py-1.5 bg-stone-600 hover:bg-stone-500 text-white rounded text-sm">
                    No Trigger (Add to Hand)
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="flex-shrink-0 h-8 bg-stone-800/50 border-y border-amber-900/30" />
        )}

        {/* Player 1 Area - Bottom */}
        <div className="flex-1 bg-blue-900/10 border-l-4 border-blue-500/30 p-3">
          <PlayerBoard
            player={player1}
            isOpponent={activePlayer === 1}  // Only "opponent" when it's Player 2's turn
            isActive={activePlayer === 0}
            isOwnerTurn={activePlayer === 0}
            onSelectCard={(zone, idx) => {
              if (activePlayer === 0) {  // Allow selecting when it's Player 1's turn
                if (zone === 'hand') {
                  setSelectedHandIndex(idx)
                  setSelectedFieldIndex(null)
                  setAttackMode(false)
                } else if (zone === 'field') {
                  setSelectedFieldIndex(idx)
                  setSelectedHandIndex(null)
                }
              }
            }}
            selectedIndex={activePlayer === 0 ? (selectedHandIndex !== null ? selectedHandIndex : selectedFieldIndex) : null}
            selectedZone={activePlayer === 0 ? (selectedHandIndex !== null ? 'hand' : selectedFieldIndex !== null ? 'field' : undefined) : undefined}
            onHoverCard={setHoveredCard}
          />
        </div>
      </div>

      {/* Action Bar - always visible in playtest (user controls both players) */}
      <div className="flex-shrink-0 bg-stone-800/90 border-t border-amber-900/50 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          {/* Play card button */}
          {selectedHandIndex !== null && (
            <button
              onClick={() => handlePlayCard(selectedHandIndex)}
              disabled={currentPlayer.hand[selectedHandIndex]?.cost! > currentPlayer.donActive}
              className={`px-4 py-2 rounded font-medium flex items-center gap-2 ${
                currentPlayer.hand[selectedHandIndex]?.cost! <= currentPlayer.donActive
                  ? 'bg-green-600 hover:bg-green-500 text-white'
                  : 'bg-stone-700 text-stone-500 cursor-not-allowed'
              }`}
            >
              <Zap className="w-4 h-4" />
              Play Card ({currentPlayer.hand[selectedHandIndex]?.cost || 0} DON)
            </button>
          )}

          {/* Attach DON to selected field card */}
          {selectedFieldIndex !== null && currentPlayer.donActive > 0 && (
            <button
              onClick={() => handleAttachDon(selectedFieldIndex)}
              className="px-4 py-2 bg-yellow-600 hover:bg-yellow-500 text-white rounded font-medium"
            >
              Attach DON
            </button>
          )}

          {/* Attack buttons */}
          {selectedFieldIndex !== null && !attackMode && (
            <button
              onClick={() => setAttackMode(true)}
              className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded font-medium flex items-center gap-2"
            >
              <Swords className="w-4 h-4" />
              Attack
            </button>
          )}

          {attackMode && (
            <div className="flex items-center gap-2">
              <span className="text-amber-200/60">Select target:</span>
              <button
                onClick={() => handleDeclareAttack(selectedFieldIndex!, -1)}
                className="px-3 py-1 bg-red-600 hover:bg-red-500 text-white rounded text-sm"
              >
                Leader
              </button>
              {/* Show opponent's field based on whose turn it is */}
              {(() => {
                const attacker = selectedFieldIndex !== null && selectedFieldIndex >= 0
                  ? currentPlayer.field[selectedFieldIndex] : null
                const attackerCanAttackActive = attacker?.canAttackActive ?? false
                return (activePlayer === 0 ? player2 : player1).field.map((card, idx) => {
                  const isTargetable = card.isResting || attackerCanAttackActive
                  return (
                    <button
                      key={idx}
                      onClick={() => handleDeclareAttack(selectedFieldIndex!, idx)}
                      disabled={!isTargetable}
                      className={`px-3 py-1 rounded text-sm ${
                        isTargetable
                          ? 'bg-red-600 hover:bg-red-500 text-white'
                          : 'bg-stone-700 text-stone-500 cursor-not-allowed'
                      }`}
                    >
                      {card.name.slice(0, 10)}
                    </button>
                  )
                })
              })()}
              <button
                onClick={() => setAttackMode(false)}
                className="px-3 py-1 bg-stone-600 hover:bg-stone-500 text-white rounded text-sm"
              >
                Cancel
              </button>
            </div>
          )}

          {/* Leader attack */}
          {!selectedFieldIndex && !selectedHandIndex && turn >= 3 && !currentPlayer.leader?.isResting && (
            <button
              onClick={() => handleDeclareAttack(-1, -1)}
              className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded font-medium flex items-center gap-2"
            >
              <Swords className="w-4 h-4" />
              Leader Attack
            </button>
          )}
        </div>

        <button
          onClick={endTurn}
          className="px-6 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium"
        >
          End Turn
        </button>
      </div>

      {/* Debug Panel — Effect Testing */}
      <div className="fixed left-2 bottom-20 z-50">
        <button
          onClick={() => setDebugOpen(o => !o)}
          className="px-3 py-1 bg-violet-800/80 hover:bg-violet-700/80 text-violet-200 text-xs rounded-lg border border-violet-600/50"
        >
          {debugOpen ? '▲ Debug' : '▼ Debug'}
        </button>
        {debugOpen && (
          <div className="mt-1 w-72 bg-stone-900/95 border border-violet-700/50 rounded-lg p-3 space-y-2 text-xs text-stone-300">
            <p className="text-violet-300 font-semibold text-[11px]">P1 Life</p>
            <div className="flex gap-1">
              {[0, 1, 2, 3, 5].map(n => (
                <button key={n} onClick={() => debugSetScenario({ life: n })}
                  className="px-2 py-0.5 bg-stone-700 hover:bg-stone-600 rounded text-[11px]">{n}</button>
              ))}
            </div>
            <p className="text-violet-300 font-semibold text-[11px]">P2 Life</p>
            <div className="flex gap-1">
              {[0, 1, 2, 3, 5].map(n => (
                <button key={n} onClick={() => debugSetScenario({ opponentLife: n })}
                  className="px-2 py-0.5 bg-stone-700 hover:bg-stone-600 rounded text-[11px]">{n}</button>
              ))}
            </div>
            <p className="text-violet-300 font-semibold text-[11px]">P1 Active DON</p>
            <div className="flex gap-1">
              {[0, 1, 2, 3, 5, 10].map(n => (
                <button key={n} onClick={() => debugSetScenario({ donActive: n })}
                  className="px-2 py-0.5 bg-stone-700 hover:bg-stone-600 rounded text-[11px]">{n}</button>
              ))}
            </div>
            <div className="flex gap-1">
              <button onClick={() => debugSetScenario({ clearField: true })}
                className="px-2 py-0.5 bg-red-900/60 hover:bg-red-800/60 rounded text-[11px]">Clear P1 Field</button>
              <button onClick={() => debugSetScenario({ clearOppField: true })}
                className="px-2 py-0.5 bg-red-900/60 hover:bg-red-800/60 rounded text-[11px]">Clear P2 Field</button>
            </div>
            <p className="text-violet-300 font-semibold text-[11px]">Add Card by ID</p>
            <input
              value={debugCardInput}
              onChange={e => setDebugCardInput(e.target.value)}
              placeholder="e.g. OP01-007"
              className="w-full px-2 py-1 bg-stone-800 border border-stone-600 rounded text-[11px] text-white"
            />
            <div className="flex flex-wrap gap-1">
              <button onClick={() => { debugSetScenario({ addToHand: [debugCardInput] }); setDebugCardInput('') }}
                className="px-2 py-0.5 bg-blue-800/60 hover:bg-blue-700/60 rounded text-[11px]">→ P1 Hand</button>
              <button onClick={() => { debugSetScenario({ addToField: [debugCardInput] }); setDebugCardInput('') }}
                className="px-2 py-0.5 bg-blue-800/60 hover:bg-blue-700/60 rounded text-[11px]">→ P1 Field</button>
              <button onClick={() => { debugSetScenario({ addToOppField: [debugCardInput] }); setDebugCardInput('') }}
                className="px-2 py-0.5 bg-orange-800/60 hover:bg-orange-700/60 rounded text-[11px]">→ P2 Field</button>
            </div>
          </div>
        )}
      </div>

      {/* Game Log */}
      <div className="fixed right-2 bottom-20 w-56 h-48 bg-stone-800/90 backdrop-blur rounded-lg border border-amber-900/50 overflow-hidden flex flex-col z-50">
        <div className="px-2 py-1 bg-stone-700/50 text-xs font-medium text-amber-200/80 border-b border-amber-900/30">
          Game Log
        </div>
        <div className="flex-1 p-1.5 overflow-y-auto text-[10px] text-amber-200/60 space-y-0.5">
          {logs.slice(-20).map((log, idx) => (
            <div key={idx} className={`py-0.5 ${
              log.includes('[EFFECT]') ? 'text-purple-400' :
              log.includes('Turn') ? 'text-amber-400 font-medium' :
              log.includes('attacks') ? 'text-red-400' :
              ''
            }`}>
              {log}
            </div>
          ))}
        </div>
      </div>

      {/* Game Over Modal */}
      {gameOver && (
        <div className="fixed inset-0 bg-black/90 flex items-center justify-center z-[100]">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-stone-800 rounded-xl border border-amber-900/50 p-8 text-center"
          >
            <h2 className="text-3xl font-bold text-amber-200 mb-4">Game Over!</h2>
            <p className={`text-2xl font-bold mb-6 ${winner === 0 ? 'text-blue-400' : 'text-red-400'}`}>
              {winner === 0 ? 'Player 1 Wins!' : 'Player 2 Wins!'}
            </p>
            <div className="flex gap-4 justify-center">
              <button
                onClick={handleRestart}
                className="px-6 py-3 bg-green-600 hover:bg-green-500 text-white rounded-lg font-medium flex items-center gap-2"
              >
                <RotateCcw className="w-5 h-5" />
                Play Again
              </button>
              <button
                onClick={handleBack}
                className="px-6 py-3 bg-stone-600 hover:bg-stone-500 text-white rounded-lg font-medium flex items-center gap-2"
              >
                <ArrowLeft className="w-5 h-5" />
                Exit
              </button>
            </div>
          </motion.div>
        </div>
      )}

      {/* Effect Choice Modal */}
      {pendingChoice && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-stone-800 rounded-xl border border-amber-900/50 p-6 max-w-md w-full mx-4"
          >
            <h3 className="text-xl font-bold text-amber-200 mb-2">
              {pendingChoice.sourceCardName || 'Effect Choice'}
            </h3>
            <p className="text-stone-300 mb-4">{pendingChoice.prompt}</p>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {pendingChoice.options.map((opt) => (
                <button
                  key={opt.id}
                  onClick={() => submitEffectChoice(pendingChoice.choiceId, [opt.id])}
                  className="w-full p-3 bg-amber-600 hover:bg-amber-500 text-white rounded-lg font-medium text-left transition-colors"
                >
                  {opt.label || opt.cardName || `Option ${opt.id}`}
                </button>
              ))}
            </div>
            {pendingChoice.minSelections === 0 && (
              <button
                onClick={() => submitEffectChoice(pendingChoice.choiceId, [])}
                className="w-full mt-4 p-3 bg-stone-600 hover:bg-stone-500 text-white rounded-lg font-medium"
              >
                Skip / Cancel
              </button>
            )}
          </motion.div>
        </div>
      )}

      {/* Hovered card preview */}
      {hoveredCard && <CardPreview card={hoveredCard} />}
    </div>
  )
}

// DON card visual — small card used in the DON cost area and under characters
function DonCardVisual({ state, size = 'normal' }: { state: 'active' | 'rested' | 'deck'; size?: 'normal' | 'small' }) {
  const isSmall = size === 'small'
  const base = isSmall ? 'w-4 h-5' : 'w-6 h-8'
  const text = isSmall ? 'text-[4px]' : 'text-[6px]'
  return (
    <div className={`${base} rounded-sm border flex items-center justify-center ${text} font-extrabold select-none shrink-0 ${
      state === 'active'
        ? 'bg-gradient-to-br from-yellow-300 to-amber-600 border-yellow-200 text-yellow-900'
        : state === 'rested'
          ? 'bg-gradient-to-br from-yellow-300/60 to-amber-600/60 border-yellow-600/50 text-yellow-900/60 rotate-90'
          : 'bg-stone-800 border-stone-600/50 text-stone-500'
    }`}>
      {isSmall ? 'D' : 'DON'}
    </div>
  )
}

// Player board component
function PlayerBoard({
  player,
  isOpponent,
  isActive,
  onSelectCard,
  selectedIndex,
  selectedZone,
  onHoverCard,
  isOwnerTurn = false,
}: {
  player: PlaytestPlayer
  isOpponent: boolean
  isActive: boolean
  onSelectCard: (zone: 'hand' | 'field' | 'leader', index: number) => void
  selectedIndex: number | null
  selectedZone?: 'hand' | 'field' | 'leader'
  onHoverCard?: (card: PlaytestCard | null) => void
  isOwnerTurn?: boolean
}) {
  const [showTrash, setShowTrash] = useState(false)
  return (
    <div className="h-full flex flex-col gap-1.5">
      {/* Stats Row */}
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center gap-4">
          <span className={`font-bold ${isOpponent ? 'text-red-400' : 'text-blue-400'}`}>
            {player.name}
          </span>
          {isActive && (
            <span className="px-2 py-0.5 bg-green-500/20 text-green-400 text-xs rounded">Active</span>
          )}
        </div>
        <div className="flex items-center gap-4 text-amber-200/60">
          <span className="flex items-center gap-1">
            <Heart className="w-4 h-4 text-red-400" />
            {player.lifeCards.length}
          </span>
          <span className="flex items-center gap-1">
            <Layers className="w-4 h-4" />
            {player.deck.length}
          </span>
          <button
            onClick={() => setShowTrash(!showTrash)}
            className={`flex items-center gap-1 px-1.5 py-0.5 rounded transition-colors ${
              showTrash ? 'bg-stone-600 text-white' : 'hover:bg-stone-700/50 text-amber-200/60'
            }`}
            title="Toggle trash view"
          >
            <Trash2 className="w-4 h-4 text-stone-400" />
            {player.trash.length}
          </button>
        </div>
      </div>

      {/* Trash Panel (collapsible) */}
      {showTrash && player.trash.length > 0 && (
        <div className="bg-stone-800/80 border border-stone-600/50 rounded-lg p-2 mb-1">
          <p className="text-stone-400 text-xs mb-1.5 font-semibold">Trash ({player.trash.length})</p>
          <div className="flex flex-wrap gap-1 max-h-24 overflow-y-auto">
            {player.trash.map((card, i) => (
              <div key={`trash-${i}`} className="text-[10px] bg-stone-700/60 border border-stone-600/40 rounded px-1.5 py-0.5 text-stone-300">
                {card.name} {card.cost != null && <span className="text-stone-500">({card.cost})</span>}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Leader and Field */}
      <div className="flex gap-4 flex-1">
        {/* Leader */}
        <div className="flex flex-col items-center">
          {player.leader && (
            <CardDisplay
              card={player.leader}
              size="large"
              isSelected={selectedZone === 'leader' && selectedIndex === 0}
              onClick={() => !isOpponent && onSelectCard('leader', 0)}
              onHover={onHoverCard}
              isOwnerTurn={isOwnerTurn}
            />
          )}
          <div className="text-[10px] text-amber-200/60 mt-1">LEADER</div>
        </div>

        {/* Field */}
        <div className="flex-1">
          <div className="text-[10px] text-amber-200/40 mb-1">FIELD ({player.field.length}/5)</div>
          <div className="flex gap-2 flex-wrap">
            <AnimatePresence>
              {player.field.map((card, idx) => (
                <motion.div
                  key={card.instanceId}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                >
                  <CardDisplay
                    card={card}
                    size="medium"
                    isSelected={selectedZone === 'field' && selectedIndex === idx}
                    onClick={() => !isOpponent && onSelectCard('field', idx)}
                    onHover={onHoverCard}
                    isOwnerTurn={isOwnerTurn}
                  />
                </motion.div>
              ))}
            </AnimatePresence>
            {player.field.length === 0 && (
              <div className="text-amber-200/30 text-sm italic">No characters</div>
            )}
          </div>
        </div>
      </div>

      {/* DON!! Cost Area — physical DON cards */}
      <div className="flex items-center gap-1.5 px-1">
        <span className="text-[9px] text-yellow-400/70 font-bold shrink-0">DON!!</span>
        <div className="flex gap-0.5 items-center flex-wrap">
          {/* Active DON in pool */}
          {Array(player.donActive).fill(null).map((_, i) => (
            <DonCardVisual key={`a-${i}`} state="active" />
          ))}
          {/* Rested DON in pool */}
          {Array(player.donRested).fill(null).map((_, i) => (
            <DonCardVisual key={`r-${i}`} state="rested" />
          ))}
        </div>
        {/* DON deck (remaining cards not yet in play) */}
        {player.donDeck > 0 && (
          <div className="flex items-center gap-0.5 ml-1.5 border-l border-stone-600/50 pl-1.5">
            <DonCardVisual state="deck" />
            <span className="text-[9px] text-stone-500">x{player.donDeck}</span>
          </div>
        )}
        <span className="text-[9px] text-stone-500 ml-auto">
          {player.donActive}/{player.donActive + player.donRested}
        </span>
      </div>

      {/* Hand */}
      {!isOpponent && (
        <div>
          <div className="text-[10px] text-amber-200/40 mb-1">HAND ({player.hand.length})</div>
          <div className="flex gap-2 overflow-x-auto pb-1">
            <AnimatePresence>
              {player.hand.map((card, idx) => (
                <motion.div
                  key={card.instanceId}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  whileHover={{ y: -8 }}
                >
                  <CardDisplay
                    card={card}
                    size="small"
                    isSelected={selectedZone === 'hand' && selectedIndex === idx}
                    onClick={() => onSelectCard('hand', idx)}
                    showCost
                    canAfford={(card.cost || 0) <= player.donActive}
                    onHover={onHoverCard}
                  />
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>
      )}

      {/* Opponent hand count */}
      {isOpponent && (
        <div className="text-amber-200/40 text-sm">
          Hand: {player.hand.length} cards
        </div>
      )}
    </div>
  )
}

// Card display component
function CardDisplay({
  card,
  size,
  isSelected,
  onClick,
  showCost,
  canAfford,
  onHover,
  isOwnerTurn = true,
}: {
  card: PlaytestCard
  size: 'small' | 'medium' | 'large'
  isSelected?: boolean
  onClick?: () => void
  showCost?: boolean
  canAfford?: boolean
  onHover?: (card: PlaytestCard | null) => void
  isOwnerTurn?: boolean
}) {
  const sizeClasses = {
    small: 'w-12',
    medium: 'w-14',
    large: 'w-16',
  }

  // DON only gives +1000 power on the card owner's turn
  const donPower = isOwnerTurn ? card.attachedDon * 1000 : 0
  const power = card.power ? card.power + donPower : null

  return (
    <div
      className={`cursor-pointer ${card.isResting ? 'rotate-90' : ''}`}
      onClick={onClick}
      onMouseEnter={() => onHover?.(card)}
      onMouseLeave={() => onHover?.(null)}
    >
      <div className={`${sizeClasses[size]} aspect-[2.5/3.5] rounded border-2 overflow-hidden transition-all ${
        isSelected
          ? 'border-yellow-400 shadow-lg shadow-yellow-400/30'
          : canAfford === false
            ? 'border-red-500/50'
            : canAfford === true
              ? 'border-green-500/50 hover:border-green-400'
              : 'border-amber-900/50 hover:border-amber-500'
      }`}>
        {card.imageUrl ? (
          <img src={card.imageUrl} alt={card.name} className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-stone-600 to-stone-800 flex items-center justify-center text-[7px] text-white text-center p-0.5">
            {card.name}
          </div>
        )}
      </div>
      {card.attachedDon > 0 && (
        <div className="flex justify-center gap-0.5 mt-0.5">
          {Array(card.attachedDon).fill(null).map((_, i) => (
            <DonCardVisual key={i} state="active" size="small" />
          ))}
        </div>
      )}
      {power && (
        <div className="text-[9px] text-amber-200/60 text-center">{power.toLocaleString()}</div>
      )}
      {showCost && card.cost !== null && (
        <div className={`text-[9px] text-center ${canAfford ? 'text-green-400' : 'text-red-400'}`}>
          {card.cost} DON
        </div>
      )}
    </div>
  )
}

// Enlarged card preview — fixed position overlay shown on hover
function CardPreview({ card }: { card: PlaytestCard }) {
  return (
    <div className="fixed right-4 top-1/2 -translate-y-1/2 z-50 pointer-events-none">
      <div className="w-64 rounded-lg border-2 border-amber-500/60 shadow-2xl shadow-black/60 overflow-hidden bg-stone-900">
        {card.imageUrl ? (
          <img src={card.imageUrl} alt={card.name} className="w-full object-contain" />
        ) : (
          <div className="w-full aspect-[2.5/3.5] bg-gradient-to-br from-stone-600 to-stone-800 flex items-center justify-center text-lg text-white text-center p-4">
            {card.name}
          </div>
        )}
        <div className="p-3 space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="text-amber-200 font-bold text-sm">{card.name}</span>
            {card.cost != null && (
              <span className="text-yellow-400 text-xs font-bold bg-yellow-400/10 px-1.5 py-0.5 rounded">
                {card.cost} Cost
              </span>
            )}
          </div>
          {card.power != null && card.power > 0 && (
            <div className="text-red-400 text-xs font-semibold">
              Power: {card.power.toLocaleString()}
              {card.attachedDon > 0 && (
                <span className="text-yellow-400 ml-1">(+{card.attachedDon * 1000} DON on your turn)</span>
              )}
            </div>
          )}
          {card.counter != null && card.counter > 0 && (
            <div className="text-blue-400 text-xs">Counter: +{card.counter}</div>
          )}
          {card.effect && (
            <div className="text-stone-300 text-xs leading-relaxed border-t border-stone-700 pt-1.5 mt-1.5">
              {card.effect}
            </div>
          )}
          {card.trigger && (
            <div className="text-amber-300 text-xs leading-relaxed border-t border-stone-700 pt-1.5">
              <span className="font-semibold">[Trigger]</span> {card.trigger}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default PlaytestPageBackend
