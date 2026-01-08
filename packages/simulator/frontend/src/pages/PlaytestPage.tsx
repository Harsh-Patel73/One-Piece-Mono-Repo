import { useState, useEffect, useMemo, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, RotateCcw, Shuffle, Trash2, Heart, Layers, Sparkles, Eye, Search, X, Swords, Shield, Target } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { usePlaytestStore, PlaytestCard, PlaytestPlayer, EffectResolutionState, CombatState } from '../store/playtestStore'
import { useDeckStore } from '../store/deckStore'
import { useCardStore } from '../store/cardStore'

export function PlaytestPage() {
  const navigate = useNavigate()
  const { currentDeck } = useDeckStore()
  const { cards, fetchCards } = useCardStore()
  const {
    isActive,
    turn,
    activePlayer,
    isFirstTurn,
    player1,
    player2,
    logs,
    selectedCard,
    effectResolution,
    combat,
    gameOver,
    winner,
    handLimitPending,
    initGame,
    playCard,
    attachDon,
    restCard,
    activateCard,
    sendToTrash,
    shuffleDeck,
    endTurn,
    selectCard,
    clearSelection,
    lookAtTopCards,
    searchDeck,
    selectFromRevealed,
    cancelEffectResolution,
    declareAttack,
    activateBlocker,
    skipBlock,
    useCounter,
    skipCounter,
    resolveDamage,
    cancelCombat,
    discardForHandLimit,
    canAttack,
    getValidTargets,
    resetGame,
  } = usePlaytestStore()

  // Build card database
  const cardDatabase = useMemo(() => {
    const map = new Map()
    cards.forEach(card => map.set(card.id, card))
    return map
  }, [cards])

  // Fetch cards and init game on mount
  useEffect(() => {
    fetchCards()
  }, [fetchCards])

  useEffect(() => {
    if (currentDeck && cards.length > 0 && !isActive) {
      initGame(currentDeck, cardDatabase)
    }
  }, [currentDeck, cards, cardDatabase, isActive, initGame])

  const handleRestart = useCallback(() => {
    resetGame()
    if (currentDeck && cards.length > 0) {
      setTimeout(() => initGame(currentDeck, cardDatabase), 50)
    }
  }, [currentDeck, cards, cardDatabase, resetGame, initGame])

  const handleBack = useCallback(() => {
    resetGame()
    navigate('/deck-builder')
  }, [resetGame, navigate])

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

  if (!isActive) {
    return (
      <div className="h-screen flex items-center justify-center bg-stone-900">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-amber-400"></div>
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col bg-stone-900 overflow-hidden">
      {/* Top Bar */}
      <div className="flex-shrink-0 bg-stone-800/90 border-b border-amber-900/50 px-4 py-2 flex items-center justify-between">
        <button
          onClick={handleBack}
          className="flex items-center gap-2 text-amber-200/70 hover:text-amber-100 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          Exit Playtest
        </button>
        <div className="flex items-center gap-4">
          <span className="text-amber-200/60">Turn {turn}</span>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
            activePlayer === 0 ? 'bg-blue-500/20 text-blue-400' : 'bg-red-500/20 text-red-400'
          }`}>
            {activePlayer === 0 ? 'Player 1' : 'Player 2'}'s Turn
          </span>
          {isFirstTurn && (
            <span className="px-2 py-1 bg-yellow-500/20 text-yellow-400 text-xs rounded">
              First Turn (No Draw)
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
        {/* Player 2 Area (Top) */}
        <PlayerArea
          player={player2}
          playerIndex={1}
          isActivePlayer={activePlayer === 1}
          onPlayCard={(idx) => playCard(1, idx)}
          onAttachDon={(zone, idx) => attachDon(1, zone, idx)}
          onRestCard={(zone, idx) => restCard(1, zone, idx)}
          onActivateCard={(zone, idx) => activateCard(1, zone, idx)}
          onSendToTrash={(zone, idx) => sendToTrash(1, zone, idx)}
          onShuffleDeck={() => shuffleDeck(1)}
          onEndTurn={endTurn}
          selectedCard={selectedCard}
          onSelectCard={(zone, idx) => selectCard(1, zone, idx)}
          onClearSelection={clearSelection}
          onLookAtTopCards={(count, filter, filterDesc) => lookAtTopCards(1, count, filter, filterDesc)}
          onSearchDeck={(filter, filterDesc) => searchDeck(1, filter, filterDesc)}
          onDeclareAttack={declareAttack}
          canAttack={canAttack}
          getValidTargets={getValidTargets}
          combat={combat}
        />

        {/* Center Divider */}
        <div className="flex-shrink-0 h-1 bg-amber-900/30" />

        {/* Player 1 Area (Bottom) */}
        <PlayerArea
          player={player1}
          playerIndex={0}
          isActivePlayer={activePlayer === 0}
          onPlayCard={(idx) => playCard(0, idx)}
          onAttachDon={(zone, idx) => attachDon(0, zone, idx)}
          onRestCard={(zone, idx) => restCard(0, zone, idx)}
          onActivateCard={(zone, idx) => activateCard(0, zone, idx)}
          onSendToTrash={(zone, idx) => sendToTrash(0, zone, idx)}
          onShuffleDeck={() => shuffleDeck(0)}
          onEndTurn={endTurn}
          selectedCard={selectedCard}
          onSelectCard={(zone, idx) => selectCard(0, zone, idx)}
          onClearSelection={clearSelection}
          onLookAtTopCards={(count, filter, filterDesc) => lookAtTopCards(0, count, filter, filterDesc)}
          onSearchDeck={(filter, filterDesc) => searchDeck(0, filter, filterDesc)}
          onDeclareAttack={declareAttack}
          canAttack={canAttack}
          getValidTargets={getValidTargets}
          combat={combat}
        />
      </div>

      {/* Effect Resolution Modal */}
      {effectResolution && (
        <EffectResolutionModal
          resolution={effectResolution}
          onSelect={selectFromRevealed}
          onCancel={cancelEffectResolution}
        />
      )}

      {/* Combat Modal */}
      {combat && (
        <CombatModal
          combat={combat}
          player1={player1}
          player2={player2}
          onActivateBlocker={activateBlocker}
          onSkipBlock={skipBlock}
          onUseCounter={useCounter}
          onSkipCounter={skipCounter}
          onResolveDamage={resolveDamage}
          onCancel={cancelCombat}
        />
      )}

      {/* Hand Limit Modal */}
      {handLimitPending && (
        <HandLimitModal
          player={handLimitPending.player === 0 ? player1 : player2}
          excessCount={handLimitPending.excessCount}
          onDiscard={discardForHandLimit}
        />
      )}

      {/* Game Over Modal */}
      {gameOver && (
        <GameOverModal
          winner={winner}
          player1={player1}
          player2={player2}
          onRestart={handleRestart}
          onExit={handleBack}
        />
      )}

      {/* Game Log (bottom right corner) */}
      <div className="fixed right-2 bottom-2 w-56 h-36 bg-stone-800/90 backdrop-blur rounded-lg border border-amber-900/50 overflow-hidden flex flex-col z-50">
        <div className="px-2 py-1 bg-stone-700/50 text-xs font-medium text-amber-200/80 border-b border-amber-900/30">
          Game Log
        </div>
        <div className="flex-1 p-1.5 overflow-y-auto text-[10px] text-amber-200/60 space-y-0.5">
          {logs.slice(-15).map((log, idx) => (
            <div key={idx} className={`py-0.5 ${log.startsWith('---') ? 'text-amber-400 font-medium mt-1' : ''}`}>
              {log}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Player Area Component
function PlayerArea({
  player,
  playerIndex,
  isActivePlayer,
  onPlayCard,
  onAttachDon,
  onRestCard,
  onActivateCard,
  onSendToTrash,
  onShuffleDeck,
  onEndTurn,
  selectedCard,
  onSelectCard,
  onClearSelection,
  onLookAtTopCards,
  onSearchDeck,
  onDeclareAttack,
  canAttack,
  getValidTargets,
  combat,
}: {
  player: PlaytestPlayer
  playerIndex: 0 | 1
  isActivePlayer: boolean
  onPlayCard: (idx: number) => void
  onAttachDon: (zone: 'leader' | 'field', idx?: number) => void
  onRestCard: (zone: 'leader' | 'field', idx?: number) => void
  onActivateCard: (zone: 'leader' | 'field', idx?: number) => void
  onSendToTrash: (zone: string, idx: number) => void
  onShuffleDeck: () => void
  onEndTurn: () => void
  selectedCard: { player: 0 | 1, zone: string, index: number } | null
  onSelectCard: (zone: string, idx: number) => void
  onClearSelection: () => void
  onLookAtTopCards: (count: number, filter?: { minCost?: number, maxCost?: number, type?: string }, filterDesc?: string) => void
  onSearchDeck: (filter?: { minCost?: number, maxCost?: number, type?: string }, filterDesc?: string) => void
  onDeclareAttack: (attackerZone: 'leader' | 'field', attackerIndex: number, targetZone: 'leader' | 'field', targetIndex: number) => void
  canAttack: (attackerZone: 'leader' | 'field', attackerIndex: number) => { canAttack: boolean, reason?: string }
  getValidTargets: () => { zone: 'leader' | 'field', index: number, card: PlaytestCard }[]
  combat: CombatState | null
}) {
  const [showEffectMenu, setShowEffectMenu] = useState(false)
  const [showTargetSelect, setShowTargetSelect] = useState<{ zone: 'leader' | 'field', index: number } | null>(null)
  const isCardSelected = (zone: string, idx: number) =>
    selectedCard?.player === playerIndex && selectedCard?.zone === zone && selectedCard?.index === idx

  const bgColor = playerIndex === 0 ? 'bg-blue-900/20' : 'bg-red-900/20'
  const borderColor = isActivePlayer ? (playerIndex === 0 ? 'border-blue-500' : 'border-red-500') : 'border-amber-900/30'

  // Get selected card info
  const selectedCardData = selectedCard?.player === playerIndex && selectedCard?.zone === 'hand'
    ? player.hand[selectedCard.index]
    : null
  const selectedFieldCard = selectedCard?.player === playerIndex && selectedCard?.zone === 'field'
    ? player.field[selectedCard.index]
    : null
  const selectedLeader = selectedCard?.player === playerIndex && selectedCard?.zone === 'leader'
    ? player.leader
    : null
  const canPlaySelectedCard = isActivePlayer && selectedCardData && (selectedCardData.cost || 0) <= player.donActive

  // Get the current card's effect (hand, field, or leader)
  const currentCardEffect = selectedCardData?.effect || selectedFieldCard?.effect || selectedLeader?.effect

  return (
    <div className={`flex-1 flex flex-col ${bgColor} border-l-4 ${borderColor} overflow-hidden`}>
      {/* Player Info Row */}
      <div className="flex-shrink-0 px-3 py-1.5 flex items-center justify-between bg-stone-800/50 border-b border-amber-900/30">
        <div className="flex items-center gap-3">
          <span className={`font-bold ${playerIndex === 0 ? 'text-blue-400' : 'text-red-400'}`}>
            {player.name}
          </span>
          {isActivePlayer && (
            <span className="px-2 py-0.5 bg-green-500/20 text-green-400 text-xs rounded">Active Turn</span>
          )}
        </div>
        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-1" title="Life Cards">
            <Heart className="w-4 h-4 text-red-400" />
            <span className="text-red-400 font-medium">{player.lifeCards.length}</span>
          </div>
          <div className="flex items-center gap-1" title="Deck">
            <Layers className="w-4 h-4 text-amber-400" />
            <span className="text-amber-200/60">{player.deck.length}</span>
          </div>
          <div className="flex items-center gap-1" title="Trash">
            <Trash2 className="w-4 h-4 text-amber-400/50" />
            <span className="text-amber-200/40">{player.trash.length}</span>
          </div>
          <div className="text-amber-400 font-bold" title="Active DON / Total DON">
            DON: <span className="text-yellow-300">{player.donActive}</span>
            <span className="text-amber-200/40">/{player.donActive + player.donRested + player.donDeck}</span>
            {player.donRested > 0 && <span className="text-amber-200/40 text-xs ml-1">({player.donRested} rested)</span>}
          </div>
        </div>
        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={onShuffleDeck}
            className="px-2 py-1 text-xs bg-stone-600/30 hover:bg-stone-600/50 text-stone-200 rounded transition-colors"
            title="Shuffle Deck"
          >
            <Shuffle className="w-3 h-3" />
          </button>
          {isActivePlayer && (
            <button
              onClick={onEndTurn}
              className="px-3 py-1 text-xs bg-green-600/50 hover:bg-green-600/70 text-white rounded font-medium transition-colors"
            >
              End Turn
            </button>
          )}
        </div>
      </div>

      {/* Field Area */}
      <div className="flex-1 flex gap-3 p-2 overflow-hidden">
        {/* Leader & Life */}
        <div className="flex-shrink-0 flex flex-col items-center gap-1 w-20">
          {/* Leader */}
          {player.leader && (
            <div
              className={`relative cursor-pointer transition-all ${player.leader.isResting ? 'rotate-90' : ''}`}
              onClick={() => onSelectCard('leader', 0)}
            >
              <div className={`w-16 aspect-[2.5/3.5] rounded border-2 ${isCardSelected('leader', 0) ? 'border-yellow-400 shadow-lg shadow-yellow-400/30' : 'border-amber-600'} overflow-hidden`}>
                {player.leader.imageUrl ? (
                  <img src={player.leader.imageUrl} alt={player.leader.name} className="w-full h-full object-cover" />
                ) : (
                  <div className="w-full h-full bg-gradient-to-br from-amber-600 to-amber-800 flex items-center justify-center text-[8px] text-white text-center p-0.5">
                    {player.leader.name}
                  </div>
                )}
              </div>
              {player.leader.attachedDon > 0 && (
                <div className="absolute -bottom-1 -right-1 bg-yellow-500 text-black text-[10px] font-bold w-5 h-5 rounded-full flex items-center justify-center border border-yellow-300">
                  +{player.leader.attachedDon}
                </div>
              )}
              <div className="text-[9px] text-amber-200/80 text-center mt-0.5 font-medium">
                {player.leader.power ? (player.leader.power + (player.leader.attachedDon * 1000)).toLocaleString() : ''}
              </div>
            </div>
          )}
          {/* Life Cards */}
          <div className="flex flex-wrap justify-center gap-0.5 mt-1">
            {player.lifeCards.map((_, idx) => (
              <div key={idx} className="w-3 h-4 bg-red-600 rounded-sm border border-red-400" />
            ))}
          </div>
          <div className="text-[10px] text-red-400 font-medium">LIFE ({player.lifeCards.length})</div>
        </div>

        {/* Field Cards */}
        <div className="flex-1 flex flex-col gap-2 min-w-0">
          {/* Field */}
          <div className="flex-1">
            <div className="text-[10px] text-amber-200/40 mb-1">FIELD ({player.field.length})</div>
            <div className="flex items-center gap-2 overflow-x-auto pb-1">
              <AnimatePresence>
                {player.field.map((card, idx) => (
                  <motion.div
                    key={card.instanceId}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    className={`relative cursor-pointer flex-shrink-0 transition-all ${card.isResting ? 'rotate-90' : ''}`}
                    onClick={() => onSelectCard('field', idx)}
                  >
                    <div className={`w-14 aspect-[2.5/3.5] rounded border-2 ${isCardSelected('field', idx) ? 'border-yellow-400 shadow-lg shadow-yellow-400/30' : 'border-amber-900/50'} overflow-hidden`}>
                      {card.imageUrl ? (
                        <img src={card.imageUrl} alt={card.name} className="w-full h-full object-cover" />
                      ) : (
                        <div className="w-full h-full bg-gradient-to-br from-stone-600 to-stone-800 flex items-center justify-center text-[7px] text-white text-center p-0.5">
                          {card.name}
                        </div>
                      )}
                    </div>
                    {card.attachedDon > 0 && (
                      <div className="absolute -bottom-1 -right-1 bg-yellow-500 text-black text-[9px] font-bold w-4 h-4 rounded-full flex items-center justify-center">
                        +{card.attachedDon}
                      </div>
                    )}
                    <div className="text-[8px] text-amber-200/60 text-center">
                      {card.power ? (card.power + (card.attachedDon * 1000)).toLocaleString() : ''}
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
              {player.field.length === 0 && (
                <div className="text-amber-200/30 text-sm italic">No characters on field</div>
              )}
            </div>
          </div>

          {/* Hand */}
          <div className="flex-shrink-0">
            <div className="text-[10px] text-amber-200/40 mb-1">HAND ({player.hand.length})</div>
            <div className="flex gap-1.5 overflow-x-auto pb-1">
              <AnimatePresence>
                {player.hand.map((card, idx) => {
                  const canAfford = (card.cost || 0) <= player.donActive
                  return (
                    <motion.div
                      key={card.instanceId}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      whileHover={{ y: -8 }}
                      className="flex-shrink-0 cursor-pointer"
                      onClick={() => onSelectCard('hand', idx)}
                    >
                      <div className={`w-12 aspect-[2.5/3.5] rounded border-2 ${
                        isCardSelected('hand', idx)
                          ? 'border-yellow-400 shadow-lg shadow-yellow-400/30'
                          : canAfford
                            ? 'border-green-500/50 hover:border-green-400'
                            : 'border-amber-900/50 hover:border-amber-500'
                      } overflow-hidden transition-colors`}>
                        {card.imageUrl ? (
                          <img src={card.imageUrl} alt={card.name} className="w-full h-full object-cover" />
                        ) : (
                          <div className="w-full h-full bg-gradient-to-br from-stone-600 to-stone-800 flex items-center justify-center text-[6px] text-white text-center p-0.5">
                            {card.name}
                          </div>
                        )}
                      </div>
                      <div className={`text-[9px] text-center font-medium ${canAfford ? 'text-green-400' : 'text-red-400'}`}>
                        {card.cost !== null ? `${card.cost} DON` : ''}
                      </div>
                    </motion.div>
                  )
                })}
              </AnimatePresence>
              {player.hand.length === 0 && (
                <div className="text-amber-200/30 text-sm italic">Empty hand</div>
              )}
            </div>
          </div>
        </div>

        {/* DON Pool & Actions */}
        <div className="flex-shrink-0 flex flex-col items-center gap-2 w-28">
          {/* DON Display */}
          <div className="text-center bg-stone-800/50 rounded-lg p-2 w-full">
            <div className="text-yellow-400 font-bold text-2xl">{player.donActive}</div>
            <div className="text-[10px] text-amber-200/60">Active DON</div>
            {player.donRested > 0 && (
              <div className="text-amber-200/40 text-xs">({player.donRested} rested)</div>
            )}
            <div className="text-amber-200/30 text-xs mt-1">{player.donDeck} in DON deck</div>
          </div>

          {/* Selected Card Actions */}
          {selectedCard?.player === playerIndex && (
            <div className="flex flex-col gap-1 w-full bg-stone-800/50 rounded-lg p-2">
              <div className="text-[10px] text-amber-200/80 text-center mb-1 font-medium">
                {selectedCard.zone === 'hand' && selectedCardData && (
                  <>
                    {selectedCardData.name}
                    <br />
                    <span className={canPlaySelectedCard ? 'text-green-400' : 'text-red-400'}>
                      Cost: {selectedCardData.cost || 0} DON
                    </span>
                  </>
                )}
                {selectedCard.zone === 'field' && player.field[selectedCard.index] && (
                  <>
                    {player.field[selectedCard.index].name}
                    <br />
                    <span className="text-amber-200/60">
                      Power: {((player.field[selectedCard.index].power || 0) + (player.field[selectedCard.index].attachedDon * 1000)).toLocaleString()}
                    </span>
                  </>
                )}
                {selectedCard.zone === 'leader' && 'Leader Actions'}
              </div>

              {selectedCard.zone === 'hand' && (
                <>
                  <button
                    onClick={() => { onPlayCard(selectedCard.index); onClearSelection() }}
                    disabled={!canPlaySelectedCard}
                    className={`px-2 py-1.5 text-xs rounded font-medium transition-colors ${
                      canPlaySelectedCard
                        ? 'bg-green-600 hover:bg-green-500 text-white'
                        : 'bg-stone-700 text-stone-500 cursor-not-allowed'
                    }`}
                  >
                    {canPlaySelectedCard ? 'Play Card' : !isActivePlayer ? "Opponent's Turn" : `Need ${(selectedCardData?.cost || 0) - player.donActive} more DON`}
                  </button>
                  <button
                    onClick={() => { onSendToTrash('hand', selectedCard.index); }}
                    disabled={!isActivePlayer}
                    className="px-2 py-1 text-[10px] bg-red-600/30 hover:bg-red-600/50 text-red-200 rounded disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Discard
                  </button>
                </>
              )}
              {selectedCard.zone === 'field' && (
                <>
                  {isActivePlayer && !combat && (() => {
                    const attackCheck = canAttack('field', selectedCard.index)
                    return (
                      <div className="relative">
                        <button
                          onClick={() => attackCheck.canAttack ? setShowTargetSelect({ zone: 'field', index: selectedCard.index }) : null}
                          disabled={!attackCheck.canAttack}
                          className={`w-full px-2 py-1.5 text-[10px] rounded font-medium flex items-center justify-center gap-1 ${
                            attackCheck.canAttack
                              ? 'bg-red-600 hover:bg-red-500 text-white'
                              : 'bg-stone-700 text-stone-500 cursor-not-allowed'
                          }`}
                          title={attackCheck.reason}
                        >
                          <Swords className="w-3 h-3" />
                          Attack
                        </button>
                        {!attackCheck.canAttack && attackCheck.reason && (
                          <div className="text-[8px] text-red-400 mt-0.5 text-center">{attackCheck.reason}</div>
                        )}
                        {/* Target Selection Dropdown */}
                        {showTargetSelect?.zone === 'field' && showTargetSelect?.index === selectedCard.index && (
                          <TargetSelectDropdown
                            targets={getValidTargets()}
                            onSelect={(targetZone, targetIndex) => {
                              onDeclareAttack('field', selectedCard.index, targetZone, targetIndex)
                              setShowTargetSelect(null)
                              onClearSelection()
                            }}
                            onCancel={() => setShowTargetSelect(null)}
                          />
                        )}
                      </div>
                    )
                  })()}
                  {player.field[selectedCard.index]?.isResting && isActivePlayer ? (
                    <button
                      onClick={() => { onActivateCard('field', selectedCard.index); onClearSelection() }}
                      className="px-2 py-1 text-[10px] bg-blue-600/50 hover:bg-blue-600/70 text-blue-100 rounded"
                    >
                      Activate
                    </button>
                  ) : null}
                  <button
                    onClick={() => onAttachDon('field', selectedCard.index)}
                    disabled={!isActivePlayer || player.donActive === 0}
                    className="px-2 py-1 text-[10px] bg-yellow-600/50 hover:bg-yellow-600/70 text-yellow-100 rounded disabled:opacity-30 disabled:cursor-not-allowed"
                  >
                    Attach DON (+1000)
                  </button>
                </>
              )}
              {selectedCard.zone === 'leader' && (
                <>
                  {isActivePlayer && !combat && (() => {
                    const attackCheck = canAttack('leader', 0)
                    return (
                      <div className="relative">
                        <button
                          onClick={() => attackCheck.canAttack ? setShowTargetSelect({ zone: 'leader', index: 0 }) : null}
                          disabled={!attackCheck.canAttack}
                          className={`w-full px-2 py-1.5 text-[10px] rounded font-medium flex items-center justify-center gap-1 ${
                            attackCheck.canAttack
                              ? 'bg-red-600 hover:bg-red-500 text-white'
                              : 'bg-stone-700 text-stone-500 cursor-not-allowed'
                          }`}
                          title={attackCheck.reason}
                        >
                          <Swords className="w-3 h-3" />
                          Attack
                        </button>
                        {!attackCheck.canAttack && attackCheck.reason && (
                          <div className="text-[8px] text-red-400 mt-0.5 text-center">{attackCheck.reason}</div>
                        )}
                        {/* Target Selection Dropdown */}
                        {showTargetSelect?.zone === 'leader' && (
                          <TargetSelectDropdown
                            targets={getValidTargets()}
                            onSelect={(targetZone, targetIndex) => {
                              onDeclareAttack('leader', 0, targetZone, targetIndex)
                              setShowTargetSelect(null)
                              onClearSelection()
                            }}
                            onCancel={() => setShowTargetSelect(null)}
                          />
                        )}
                      </div>
                    )
                  })()}
                  {player.leader?.isResting && isActivePlayer && (
                    <button
                      onClick={() => { onActivateCard('leader', 0); onClearSelection() }}
                      className="px-2 py-1 text-[10px] bg-blue-600/50 hover:bg-blue-600/70 text-blue-100 rounded"
                    >
                      Activate
                    </button>
                  )}
                  <button
                    onClick={() => onAttachDon('leader', 0)}
                    disabled={!isActivePlayer || player.donActive === 0}
                    className="px-2 py-1 text-[10px] bg-yellow-600/50 hover:bg-yellow-600/70 text-yellow-100 rounded disabled:opacity-30 disabled:cursor-not-allowed"
                  >
                    Attach DON (+1000)
                  </button>
                </>
              )}

              {/* Effect Actions */}
              {currentCardEffect && (
                <div className="relative mt-1 pt-1 border-t border-amber-900/30">
                  <div className="text-[9px] text-amber-200/50 mb-1 max-h-12 overflow-y-auto">
                    {currentCardEffect.length > 80 ? currentCardEffect.slice(0, 80) + '...' : currentCardEffect}
                  </div>
                  <button
                    onClick={() => setShowEffectMenu(!showEffectMenu)}
                    disabled={!isActivePlayer}
                    className="w-full px-2 py-1 text-[10px] bg-purple-600/50 hover:bg-purple-600/70 text-purple-100 rounded flex items-center justify-center gap-1 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Sparkles className="w-3 h-3" />
                    Trigger Effect
                  </button>
                  {showEffectMenu && (
                    <div className="absolute bottom-full left-0 right-0 mb-1 bg-stone-900 rounded border border-amber-900/50 shadow-lg z-10">
                      <button
                        onClick={() => { onLookAtTopCards(4); setShowEffectMenu(false) }}
                        className="w-full px-2 py-1.5 text-[10px] text-left hover:bg-stone-700 flex items-center gap-1 text-amber-200"
                      >
                        <Eye className="w-3 h-3" /> Look at Top 4
                      </button>
                      <button
                        onClick={() => { onLookAtTopCards(5); setShowEffectMenu(false) }}
                        className="w-full px-2 py-1.5 text-[10px] text-left hover:bg-stone-700 flex items-center gap-1 text-amber-200"
                      >
                        <Eye className="w-3 h-3" /> Look at Top 5
                      </button>
                      <button
                        onClick={() => { onLookAtTopCards(4, { minCost: 3 }, 'cost 3+'); setShowEffectMenu(false) }}
                        className="w-full px-2 py-1.5 text-[10px] text-left hover:bg-stone-700 flex items-center gap-1 text-amber-200"
                      >
                        <Eye className="w-3 h-3" /> Top 4 (Cost 3+)
                      </button>
                      <button
                        onClick={() => { onSearchDeck(); setShowEffectMenu(false) }}
                        className="w-full px-2 py-1.5 text-[10px] text-left hover:bg-stone-700 flex items-center gap-1 text-amber-200 border-t border-amber-900/30"
                      >
                        <Search className="w-3 h-3" /> Search Deck
                      </button>
                      <button
                        onClick={() => { onSearchDeck({ type: 'CHARACTER' }, 'Characters'); setShowEffectMenu(false) }}
                        className="w-full px-2 py-1.5 text-[10px] text-left hover:bg-stone-700 flex items-center gap-1 text-amber-200"
                      >
                        <Search className="w-3 h-3" /> Search Characters
                      </button>
                      <button
                        onClick={() => setShowEffectMenu(false)}
                        className="w-full px-2 py-1.5 text-[10px] text-left hover:bg-stone-700 flex items-center gap-1 text-stone-400 border-t border-amber-900/30"
                      >
                        <X className="w-3 h-3" /> Close
                      </button>
                    </div>
                  )}
                </div>
              )}

              <button
                onClick={onClearSelection}
                className="px-2 py-1 text-[10px] bg-stone-700/50 hover:bg-stone-600/50 text-stone-300 rounded mt-1"
              >
                Cancel
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// Effect Resolution Modal
function EffectResolutionModal({
  resolution,
  onSelect,
  onCancel,
}: {
  resolution: EffectResolutionState
  onSelect: (indices: number[]) => void
  onCancel: () => void
}) {
  const [selectedIndices, setSelectedIndices] = useState<number[]>([])
  const isMultiSelect = resolution.selectionCount > 1 || resolution.effectType === 'select_from_revealed'
  const isTrashMode = resolution.onComplete === 'to_trash'

  const handleConfirm = () => {
    onSelect(selectedIndices)
  }

  const toggleSelection = (idx: number) => {
    if (selectedIndices.includes(idx)) {
      setSelectedIndices(selectedIndices.filter(i => i !== idx))
    } else if (!isMultiSelect) {
      setSelectedIndices([idx])
    } else if (selectedIndices.length < resolution.selectionCount) {
      setSelectedIndices([...selectedIndices, idx])
    }
  }

  const isValidSelection = (card: PlaytestCard) => {
    if (!resolution.selectionFilter) return true
    return resolution.selectionFilter(card)
  }

  const getModalTitle = () => {
    if (resolution.effectType === 'look_top') return `Select from Top ${resolution.revealedCards.length} Cards`
    if (resolution.effectType === 'search_deck') return 'Search Deck'
    if (resolution.effectType === 'select_from_revealed' && isTrashMode) return `Select ${resolution.selectionCount} Card(s) to Trash`
    return 'Select Cards'
  }

  const getConfirmText = () => {
    if (isTrashMode) {
      return selectedIndices.length === resolution.selectionCount
        ? `Trash ${selectedIndices.length} Card(s)`
        : `Select ${resolution.selectionCount - selectedIndices.length} more`
    }
    return selectedIndices.length > 0 ? 'Add to Hand' : 'Skip (Select None)'
  }

  const canConfirm = isTrashMode
    ? selectedIndices.length === resolution.selectionCount
    : true

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-[100]">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-stone-800 rounded-xl border border-amber-900/50 p-4 max-w-4xl max-h-[80vh] overflow-hidden flex flex-col"
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-amber-200">
            {getModalTitle()}
          </h3>
          {resolution.filterDescription && (
            <span className="text-sm text-amber-400 bg-amber-900/30 px-2 py-1 rounded">
              {resolution.filterDescription}
            </span>
          )}
        </div>

        <div className="flex-1 overflow-y-auto">
          <div className="grid grid-cols-5 md:grid-cols-8 lg:grid-cols-10 gap-2">
            {resolution.revealedCards.map((card, idx) => {
              const isValid = isValidSelection(card)
              const isSelected = selectedIndices.includes(idx)
              return (
                <motion.div
                  key={card.instanceId}
                  whileHover={isValid ? { scale: 1.05 } : {}}
                  onClick={() => isValid && toggleSelection(idx)}
                  className={`cursor-pointer relative ${!isValid ? 'opacity-40 cursor-not-allowed' : ''}`}
                >
                  <div className={`aspect-[2.5/3.5] rounded border-2 overflow-hidden ${
                    isSelected
                      ? isTrashMode
                        ? 'border-red-400 shadow-lg shadow-red-400/30'
                        : 'border-green-400 shadow-lg shadow-green-400/30'
                      : isValid
                        ? 'border-amber-600 hover:border-amber-400'
                        : 'border-stone-600'
                  }`}>
                    {card.imageUrl ? (
                      <img src={card.imageUrl} alt={card.name} className="w-full h-full object-cover" />
                    ) : (
                      <div className="w-full h-full bg-gradient-to-br from-stone-600 to-stone-800 flex items-center justify-center text-[8px] text-white text-center p-1">
                        {card.name}
                      </div>
                    )}
                  </div>
                  <div className="text-[9px] text-center text-amber-200/80 truncate mt-0.5">
                    {card.name}
                  </div>
                  <div className="text-[8px] text-center text-amber-200/50">
                    {card.cost !== null && `${card.cost} DON`}
                    {card.power && ` | ${card.power}`}
                  </div>
                  {isSelected && (
                    <div className={`absolute top-1 right-1 w-5 h-5 ${isTrashMode ? 'bg-red-500' : 'bg-green-500'} rounded-full flex items-center justify-center`}>
                      <span className="text-white text-xs font-bold">✓</span>
                    </div>
                  )}
                </motion.div>
              )
            })}
          </div>
        </div>

        <div className="flex justify-end gap-3 mt-4 pt-4 border-t border-amber-900/30">
          {!isTrashMode && (
            <button
              onClick={onCancel}
              className="px-4 py-2 text-sm bg-stone-600 hover:bg-stone-500 text-white rounded-lg transition-colors"
            >
              Cancel
            </button>
          )}
          <button
            onClick={handleConfirm}
            disabled={!canConfirm}
            className={`px-4 py-2 text-sm rounded-lg transition-colors ${
              canConfirm
                ? isTrashMode
                  ? 'bg-red-600 hover:bg-red-500 text-white'
                  : 'bg-green-600 hover:bg-green-500 text-white'
                : 'bg-stone-700 text-stone-500 cursor-not-allowed'
            }`}
          >
            {getConfirmText()}
          </button>
        </div>
      </motion.div>
    </div>
  )
}

// Target Selection Dropdown
function TargetSelectDropdown({
  targets,
  onSelect,
  onCancel,
}: {
  targets: { zone: 'leader' | 'field', index: number, card: PlaytestCard }[]
  onSelect: (zone: 'leader' | 'field', index: number) => void
  onCancel: () => void
}) {
  return (
    <div className="absolute top-full left-0 right-0 mt-1 bg-stone-900 rounded border border-amber-900/50 shadow-lg z-20">
      <div className="px-2 py-1 text-[9px] text-amber-200/60 border-b border-amber-900/30">
        Select Target
      </div>
      {targets.map((target, idx) => (
        <button
          key={`${target.zone}-${target.index}`}
          onClick={() => onSelect(target.zone, target.index)}
          className="w-full px-2 py-1.5 text-[10px] text-left hover:bg-stone-700 flex items-center gap-2 text-amber-200"
        >
          <Target className="w-3 h-3" />
          {target.zone === 'leader' ? (
            <span className="text-amber-400">{target.card.name} (Leader)</span>
          ) : (
            <span>{target.card.name} {target.card.isResting ? '(Rested)' : ''}</span>
          )}
          <span className="text-amber-200/50 ml-auto">{target.card.power?.toLocaleString()}</span>
        </button>
      ))}
      {targets.length === 0 && (
        <div className="px-2 py-1.5 text-[10px] text-amber-200/50">No valid targets</div>
      )}
      <button
        onClick={onCancel}
        className="w-full px-2 py-1.5 text-[10px] text-left hover:bg-stone-700 text-stone-400 border-t border-amber-900/30"
      >
        <X className="w-3 h-3 inline mr-1" /> Cancel
      </button>
    </div>
  )
}

// Combat Modal
function CombatModal({
  combat,
  player1,
  player2,
  onActivateBlocker,
  onSkipBlock,
  onUseCounter,
  onSkipCounter,
  onResolveDamage,
  onCancel,
}: {
  combat: CombatState
  player1: PlaytestPlayer
  player2: PlaytestPlayer
  onActivateBlocker: (idx: number) => void
  onSkipBlock: () => void
  onUseCounter: (indices: number[]) => void
  onSkipCounter: () => void
  onResolveDamage: () => void
  onCancel: () => void
}) {
  const [selectedCounters, setSelectedCounters] = useState<number[]>([])
  const defender = combat.defenderPlayer === 0 ? player1 : player2
  const attacker = combat.attackerPlayer === 0 ? player1 : player2

  const totalCounterValue = selectedCounters.reduce((sum, idx) => {
    const card = defender.hand[idx]
    return sum + (card?.counter || 0)
  }, 0)

  const projectedDefense = combat.basePower + combat.counterBonus + totalCounterValue

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-[100]">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-stone-800 rounded-xl border border-amber-900/50 p-4 max-w-2xl w-full max-h-[80vh] overflow-hidden flex flex-col"
      >
        {/* Combat Header */}
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-amber-200 flex items-center gap-2">
            <Swords className="w-5 h-5 text-red-400" />
            Combat
          </h3>
          <span className={`px-3 py-1 rounded text-sm font-medium ${
            combat.phase === 'blocker' ? 'bg-blue-500/20 text-blue-400' :
            combat.phase === 'counter' ? 'bg-purple-500/20 text-purple-400' :
            'bg-red-500/20 text-red-400'
          }`}>
            {combat.phase === 'blocker' && 'Blocker Step'}
            {combat.phase === 'counter' && 'Counter Step'}
            {combat.phase === 'damage' && 'Damage Step'}
          </span>
        </div>

        {/* Combat Info */}
        <div className="grid grid-cols-3 gap-4 mb-4">
          {/* Attacker */}
          <div className="text-center">
            <div className="text-[10px] text-amber-200/60 mb-1">ATTACKER</div>
            <div className="w-20 aspect-[2.5/3.5] mx-auto rounded border-2 border-red-500 overflow-hidden">
              {combat.attacker.imageUrl ? (
                <img src={combat.attacker.imageUrl} alt={combat.attacker.name} className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full bg-red-900/50 flex items-center justify-center text-[8px] text-white p-1">
                  {combat.attacker.name}
                </div>
              )}
            </div>
            <div className="text-sm text-amber-200 font-medium mt-1">{combat.attacker.name}</div>
            <div className="text-lg text-red-400 font-bold">{combat.attackerPower.toLocaleString()}</div>
          </div>

          {/* VS */}
          <div className="flex items-center justify-center">
            <div className="text-2xl font-bold text-amber-400">VS</div>
          </div>

          {/* Defender */}
          <div className="text-center">
            <div className="text-[10px] text-amber-200/60 mb-1">
              {combat.blockerActivated ? 'BLOCKER' : 'DEFENDER'}
            </div>
            <div className={`w-20 aspect-[2.5/3.5] mx-auto rounded border-2 ${combat.blockerActivated ? 'border-blue-500' : 'border-amber-500'} overflow-hidden`}>
              {combat.currentTarget.imageUrl ? (
                <img src={combat.currentTarget.imageUrl} alt={combat.currentTarget.name} className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full bg-amber-900/50 flex items-center justify-center text-[8px] text-white p-1">
                  {combat.currentTarget.name}
                </div>
              )}
            </div>
            <div className="text-sm text-amber-200 font-medium mt-1">{combat.currentTarget.name}</div>
            <div className="text-lg text-amber-400 font-bold">
              {projectedDefense.toLocaleString()}
              {totalCounterValue > 0 && (
                <span className="text-green-400 text-sm ml-1">(+{totalCounterValue})</span>
              )}
            </div>
          </div>
        </div>

        {/* Phase-specific UI */}
        {combat.phase === 'blocker' && (
          <div className="border-t border-amber-900/30 pt-4">
            <div className="text-sm text-amber-200 mb-2 flex items-center gap-2">
              <Shield className="w-4 h-4 text-blue-400" />
              {defender.name} may activate a blocker
            </div>
            {combat.availableBlockers.length > 0 ? (
              <div className="flex gap-2 flex-wrap">
                {combat.availableBlockers.map((blocker) => (
                  <button
                    key={blocker.index}
                    onClick={() => onActivateBlocker(blocker.index)}
                    className="px-3 py-2 bg-blue-600/30 hover:bg-blue-600/50 text-blue-200 rounded flex items-center gap-2"
                  >
                    <Shield className="w-4 h-4" />
                    {blocker.card.name} ({blocker.card.power?.toLocaleString()})
                  </button>
                ))}
              </div>
            ) : (
              <div className="text-amber-200/50 text-sm">No blockers available</div>
            )}
            <button
              onClick={onSkipBlock}
              className="mt-3 px-4 py-2 bg-stone-600 hover:bg-stone-500 text-white rounded"
            >
              Skip Blocker Step
            </button>
          </div>
        )}

        {combat.phase === 'counter' && (
          <div className="border-t border-amber-900/30 pt-4">
            <div className="text-sm text-amber-200 mb-2">
              {defender.name} may use counter cards from hand
            </div>
            {combat.availableCounters.length > 0 ? (
              <>
                <div className="flex gap-2 flex-wrap mb-3">
                  {combat.availableCounters.map((counter) => {
                    const isSelected = selectedCounters.includes(counter.index)
                    return (
                      <button
                        key={counter.index}
                        onClick={() => {
                          if (isSelected) {
                            setSelectedCounters(selectedCounters.filter(i => i !== counter.index))
                          } else {
                            setSelectedCounters([...selectedCounters, counter.index])
                          }
                        }}
                        className={`px-3 py-2 rounded flex items-center gap-2 ${
                          isSelected
                            ? 'bg-green-600 text-white'
                            : 'bg-purple-600/30 hover:bg-purple-600/50 text-purple-200'
                        }`}
                      >
                        {counter.card.name}
                        <span className="text-green-300">+{counter.value}</span>
                      </button>
                    )
                  })}
                </div>
                {selectedCounters.length > 0 && (
                  <div className="text-sm text-green-400 mb-2">
                    Total counter bonus: +{totalCounterValue} (Defense: {projectedDefense.toLocaleString()})
                  </div>
                )}
                <div className="flex gap-2">
                  <button
                    onClick={() => onUseCounter(selectedCounters)}
                    disabled={selectedCounters.length === 0}
                    className="px-4 py-2 bg-green-600 hover:bg-green-500 text-white rounded disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Use Selected Counters
                  </button>
                  <button
                    onClick={onSkipCounter}
                    className="px-4 py-2 bg-stone-600 hover:bg-stone-500 text-white rounded"
                  >
                    Skip Counter Step
                  </button>
                </div>
              </>
            ) : (
              <>
                <div className="text-amber-200/50 text-sm mb-3">No counter cards available</div>
                <button
                  onClick={onSkipCounter}
                  className="px-4 py-2 bg-stone-600 hover:bg-stone-500 text-white rounded"
                >
                  Continue to Damage
                </button>
              </>
            )}
          </div>
        )}

        {combat.phase === 'damage' && (
          <div className="border-t border-amber-900/30 pt-4">
            <div className="text-center mb-4">
              <div className="text-lg font-bold mb-2">
                {combat.attackerPower >= combat.totalDefense ? (
                  <span className="text-red-400">Attack Succeeds!</span>
                ) : (
                  <span className="text-green-400">Attack Defended!</span>
                )}
              </div>
              <div className="text-amber-200/80">
                {combat.attackerPower.toLocaleString()} vs {combat.totalDefense.toLocaleString()}
              </div>
            </div>
            <button
              onClick={onResolveDamage}
              className="w-full px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded font-medium"
            >
              Resolve Damage
            </button>
          </div>
        )}

        {/* Cancel button */}
        <button
          onClick={onCancel}
          className="mt-4 px-4 py-2 bg-stone-700 hover:bg-stone-600 text-stone-300 rounded text-sm"
        >
          Cancel Combat
        </button>
      </motion.div>
    </div>
  )
}

// Hand Limit Modal
function HandLimitModal({
  player,
  excessCount,
  onDiscard,
}: {
  player: PlaytestPlayer
  excessCount: number
  onDiscard: (indices: number[]) => void
}) {
  const [selectedIndices, setSelectedIndices] = useState<number[]>([])

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-[100]">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-stone-800 rounded-xl border border-amber-900/50 p-4 max-w-3xl w-full"
      >
        <h3 className="text-lg font-bold text-amber-200 mb-2">Hand Limit Exceeded</h3>
        <p className="text-amber-200/80 mb-4">
          {player.name} has {player.hand.length} cards in hand. Maximum is 7.
          <br />
          Select {excessCount} card{excessCount > 1 ? 's' : ''} to discard.
        </p>

        <div className="flex gap-2 flex-wrap mb-4">
          {player.hand.map((card, idx) => {
            const isSelected = selectedIndices.includes(idx)
            return (
              <motion.div
                key={card.instanceId}
                whileHover={{ scale: 1.05 }}
                onClick={() => {
                  if (isSelected) {
                    setSelectedIndices(selectedIndices.filter(i => i !== idx))
                  } else if (selectedIndices.length < excessCount) {
                    setSelectedIndices([...selectedIndices, idx])
                  }
                }}
                className={`cursor-pointer relative`}
              >
                <div className={`w-16 aspect-[2.5/3.5] rounded border-2 overflow-hidden ${
                  isSelected ? 'border-red-400 shadow-lg shadow-red-400/30' : 'border-amber-900/50 hover:border-amber-500'
                }`}>
                  {card.imageUrl ? (
                    <img src={card.imageUrl} alt={card.name} className="w-full h-full object-cover" />
                  ) : (
                    <div className="w-full h-full bg-gradient-to-br from-stone-600 to-stone-800 flex items-center justify-center text-[8px] text-white text-center p-1">
                      {card.name}
                    </div>
                  )}
                </div>
                {isSelected && (
                  <div className="absolute top-1 right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center">
                    <Trash2 className="w-3 h-3 text-white" />
                  </div>
                )}
              </motion.div>
            )
          })}
        </div>

        <button
          onClick={() => onDiscard(selectedIndices)}
          disabled={selectedIndices.length !== excessCount}
          className={`w-full px-4 py-2 rounded font-medium ${
            selectedIndices.length === excessCount
              ? 'bg-red-600 hover:bg-red-500 text-white'
              : 'bg-stone-700 text-stone-500 cursor-not-allowed'
          }`}
        >
          Discard {selectedIndices.length}/{excessCount} Cards
        </button>
      </motion.div>
    </div>
  )
}

// Game Over Modal
function GameOverModal({
  winner,
  player1,
  player2,
  onRestart,
  onExit,
}: {
  winner: 0 | 1 | null
  player1: PlaytestPlayer
  player2: PlaytestPlayer
  onRestart: () => void
  onExit: () => void
}) {
  const winnerPlayer = winner === 0 ? player1 : winner === 1 ? player2 : null

  return (
    <div className="fixed inset-0 bg-black/90 flex items-center justify-center z-[100]">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-stone-800 rounded-xl border border-amber-900/50 p-8 text-center"
      >
        <h2 className="text-3xl font-bold text-amber-200 mb-4">Game Over!</h2>
        {winnerPlayer && (
          <p className={`text-2xl font-bold mb-6 ${winner === 0 ? 'text-blue-400' : 'text-red-400'}`}>
            {winnerPlayer.name} Wins!
          </p>
        )}
        <div className="flex gap-4 justify-center">
          <button
            onClick={onRestart}
            className="px-6 py-3 bg-green-600 hover:bg-green-500 text-white rounded-lg font-medium flex items-center gap-2"
          >
            <RotateCcw className="w-5 h-5" />
            Play Again
          </button>
          <button
            onClick={onExit}
            className="px-6 py-3 bg-stone-600 hover:bg-stone-500 text-white rounded-lg font-medium flex items-center gap-2"
          >
            <ArrowLeft className="w-5 h-5" />
            Exit
          </button>
        </div>
      </motion.div>
    </div>
  )
}
