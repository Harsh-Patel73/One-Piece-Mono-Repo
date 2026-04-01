/**
 * Effect Tester Page
 *
 * Interactive game-based effect tester.
 * - Left panel:  card list for a set (OP01, OP02, …) with Pass/Fail/Skip badges
 * - Main area:   full playtest game board pre-configured for the selected card
 * - Bottom bar:  Pass / Fail / Skip verdict buttons that update CARD_STATUS.md
 *
 * Usage:
 *   1. Pick a set code (default OP01) and click a card in the left panel.
 *   2. The game resets with that card in P1's hand (or as P1's leader if it's a LEADER).
 *      P1 starts with 10 DON, 3 characters already on field, opponent has 3 rested chars.
 *   3. Interact with the game normally (play card, attach DON, attack, activate effects).
 *   4. Click Pass / Fail / Skip to record your verdict.
 */

import { useState, useEffect, useCallback, useRef } from 'react'
import { createPortal } from 'react-dom'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, RotateCcw, Swords, Heart, Layers, Trash2, CheckCircle2, XCircle, SkipForward } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { usePlaytestSocket, PlaytestCard, PlaytestPlayer } from '../hooks/usePlaytestSocket'

// ── Types ──────────────────────────────────────────────────────────────────

interface QueueCard {
  id: string
  name: string
  card_type: string
  cost: number | null
  power: number | null
  status: string
  notes: string
  effect: string | null
  trigger: string | null
}

const STATUS_COLOR: Record<string, string> = {
  '✅ Verified':  'text-green-400',
  '⚠ Needs Fix': 'text-yellow-400',
  '🔲 To Do':     'text-stone-400',
  '❌ Missing':   'text-red-500',
  '⬜ No Effect': 'text-stone-600',
  '⬜ Keywords':  'text-stone-600',
}

// ── Main Page ──────────────────────────────────────────────────────────────

export function EffectTesterPage() {
  const navigate = useNavigate()
  const {
    isActive, isConnected,
    turn, activePlayer, phase,
    player1, player2,
    logs, gameOver, winner,
    awaitingResponse, pendingAttack, pendingChoice, error,
    startTestGame, playCard, attachDon, declareAttack,
    blockerResponse, counterResponse, triggerResponse, activateEffect,
    endTurn, submitEffectChoice, simulateKo, debugSetScenario, resetGame,
  } = usePlaytestSocket()

  // Card queue state
  const [setCode, setSetCode]             = useState('OP01')
  const [cards, setCards]                 = useState<QueueCard[]>([])
  const [activeCard, setActiveCard]       = useState<QueueCard | null>(null)
  const [localStatuses, setLocalStatuses] = useState<Record<string, string>>({})
  const [queueLoading, setQueueLoading]   = useState(false)

  // Game board interaction state
  const [selectedHandIndex, setSelectedHandIndex]   = useState<number | null>(null)
  const [selectedFieldIndex, setSelectedFieldIndex] = useState<number | null>(null)
  const [attackMode, setAttackMode]                 = useState(false)
  const [selectedCounterIndices, setSelectedCounterIndices] = useState<number[]>([])
  const [debugOpen, setDebugOpen]                   = useState(false)
  const [debugCardInput, setDebugCardInput]         = useState('')

  // Verdict UI state
  const [failNoteOpen, setFailNoteOpen] = useState(false)
  const [failNote, setFailNote]         = useState('')
  const [verdictSaving, setVerdictSaving] = useState(false)

  // Multi-select choice state
  const [selectedChoiceIds, setSelectedChoiceIds] = useState<string[]>([])

  // Clear selection when active player changes
  useEffect(() => {
    setSelectedHandIndex(null)
    setSelectedFieldIndex(null)
    setAttackMode(false)
  }, [activePlayer])

  // Reset multi-select when a new choice appears
  useEffect(() => {
    setSelectedChoiceIds([])
  }, [pendingChoice?.choiceId])

  // ── Load card queue ──────────────────────────────────────────────────────

  useEffect(() => {
    setQueueLoading(true)
    fetch(`/api/effect-test/queue?set_code=${setCode}`)
      .then(r => r.json())
      .then(d => {
        setCards(d.cards || [])
        setQueueLoading(false)
      })
      .catch(() => setQueueLoading(false))
  }, [setCode])

  // ── Card selection ────────────────────────────────────────────────────────

  const handleSelectCard = useCallback((card: QueueCard) => {
    setActiveCard(card)
    setSelectedHandIndex(null)
    setSelectedFieldIndex(null)
    setAttackMode(false)
    setFailNoteOpen(false)
    setFailNote('')
    if (isConnected) {
      startTestGame(card.id)
    }
  }, [isConnected, startTestGame])

  // Auto-start when connection arrives and a card is already selected
  useEffect(() => {
    if (isConnected && activeCard && !isActive) {
      startTestGame(activeCard.id)
    }
  }, [isConnected]) // eslint-disable-line react-hooks/exhaustive-deps

  // ── Verdict submission ────────────────────────────────────────────────────

  const submitVerdict = useCallback(async (verdict: 'pass' | 'fail' | 'skip', note = '') => {
    if (!activeCard) return
    setVerdictSaving(true)
    try {
      const res = await fetch('/api/effect-test/verdict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ card_id: activeCard.id, verdict, note }),
      })
      const d = await res.json()
      if (d.ok) {
        setLocalStatuses(prev => ({ ...prev, [activeCard.id]: d.new_status }))
        setCards(prev => prev.map(c =>
          c.id === activeCard.id ? { ...c, status: d.new_status } : c
        ))
      }
    } finally {
      setVerdictSaving(false)
      setFailNoteOpen(false)
      setFailNote('')
    }
  }, [activeCard])

  // ── Game actions ──────────────────────────────────────────────────────────

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

  const currentPlayer = activePlayer === 0 ? player1 : player2

  const effectLabel = activeCard?.card_type === 'LEADER' ? 'leader' : (activeCard?.card_type ?? '').toLowerCase()

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="h-screen flex flex-col bg-stone-900 overflow-hidden">
      {/* ── Top bar ── */}
      <div className="flex-shrink-0 bg-stone-800/90 border-b border-amber-900/50 px-4 py-2 flex items-center justify-between">
        <button
          onClick={() => { resetGame(); navigate('/') }}
          className="flex items-center gap-2 text-amber-200/70 hover:text-amber-100 transition-colors text-sm"
        >
          <ArrowLeft className="w-4 h-4" />
          Home
        </button>

        <div className="flex items-center gap-3 text-sm">
          {isActive && (
            <>
              <span className="text-amber-200/60">Turn {turn}</span>
              <span className="text-amber-200/40">·</span>
              <span className="text-amber-200/60">{phase}</span>
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                activePlayer === 0 ? 'bg-blue-500/20 text-blue-400' : 'bg-red-500/20 text-red-400'
              }`}>
                {activePlayer === 0 ? 'P1 Turn' : 'P2 Turn'}
              </span>
            </>
          )}
          {activeCard && (
            <span className="text-amber-200/80 font-medium">
              {activeCard.id} — {activeCard.name}
              <span className="ml-2 text-amber-200/40 font-normal capitalize">{effectLabel}</span>
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {isActive && activeCard && (
            <button
              onClick={() => startTestGame(activeCard.id)}
              className="flex items-center gap-1 text-amber-200/60 hover:text-amber-100 text-sm"
            >
              <RotateCcw className="w-4 h-4" />
              Reset
            </button>
          )}
          <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-500'}`} />
        </div>
      </div>

      {/* ── Body: sidebar + game board ── */}
      <div className="flex-1 flex overflow-hidden">

        {/* ── Left sidebar: card queue ── */}
        <div className="w-56 flex-shrink-0 border-r border-amber-900/30 flex flex-col bg-stone-900">
          {/* Set selector */}
          <div className="px-2 py-2 border-b border-amber-900/30">
            <select
              value={setCode}
              onChange={e => { setSetCode(e.target.value); setActiveCard(null) }}
              className="w-full bg-stone-800 text-amber-200 text-xs border border-stone-600 rounded px-2 py-1"
            >
              {['OP01','OP02','OP03','OP04','OP05','OP06','OP07','OP08',
                'OP09','OP10','OP11','OP12','OP13','OP14','ST01'].map(s => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>

          {/* Statline */}
          {cards.length > 0 && (() => {
            const counts = cards.reduce((acc, c) => {
              const s = localStatuses[c.id] ?? c.status
              if (s === '✅ Verified') acc.verified++
              else if (s === '⚠ Needs Fix') acc.fail++
              else if (s === '❌ Missing') acc.missing++
              else if (s === '🔲 To Do') acc.todo++
              return acc
            }, { verified: 0, fail: 0, missing: 0, todo: 0 })
            const nonSuccessful = counts.fail + counts.missing
            const total = cards.length
            return (
              <div className="px-2 py-1.5 border-b border-amber-900/30 bg-stone-800/40 text-[9px] space-y-0.5">
                <div className="flex justify-between">
                  <span className="text-stone-400">Total</span>
                  <span className="text-amber-200/70 font-mono">{total}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-green-400">✅ Verified</span>
                  <span className="text-green-400 font-mono">{counts.verified}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-yellow-400">⚠ Needs Fix</span>
                  <span className="text-yellow-400 font-mono">{counts.fail}</span>
                </div>
                {counts.missing > 0 && (
                  <div className="flex justify-between">
                    <span className="text-red-400">❌ Missing</span>
                    <span className="text-red-400 font-mono">{counts.missing}</span>
                  </div>
                )}
                <div className="flex justify-between border-t border-stone-700 pt-0.5 mt-0.5">
                  <span className="text-red-300/80">Non-pass</span>
                  <span className="text-red-300/80 font-mono">{nonSuccessful} / {total}</span>
                </div>
              </div>
            )
          })()}

          {/* Card list */}
          <div className="flex-1 overflow-y-auto">
            {queueLoading ? (
              <div className="p-4 text-amber-200/40 text-xs text-center">Loading…</div>
            ) : cards.length === 0 ? (
              <div className="p-4 text-amber-200/40 text-xs text-center">No cards found</div>
            ) : (
              cards.map(card => {
                const status = localStatuses[card.id] ?? card.status
                const isSelected = activeCard?.id === card.id
                return (
                  <button
                    key={card.id}
                    onClick={() => handleSelectCard(card)}
                    className={`w-full text-left px-2 py-1.5 border-b border-stone-800 hover:bg-stone-800/60 transition-colors ${
                      isSelected ? 'bg-amber-900/30 border-l-2 border-l-amber-400' : ''
                    }`}
                  >
                    <div className="flex items-center justify-between gap-1">
                      <span className="text-[10px] text-stone-500 font-mono">{card.id}</span>
                      <span className={`text-[9px] ${STATUS_COLOR[status] ?? 'text-stone-500'}`}>
                        {status.split(' ')[0]}
                      </span>
                    </div>
                    <div className="text-xs text-amber-200/80 truncate leading-tight">{card.name}</div>
                    <div className="text-[9px] text-stone-500">{card.card_type}</div>
                  </button>
                )
              })
            )}
          </div>
        </div>

        {/* ── Main: game board ── */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {!isConnected ? (
            <div className="flex-1 flex items-center justify-center text-amber-200/40 text-sm">
              Connecting to server…
              {error && <span className="ml-2 text-red-400">{error}</span>}
            </div>
          ) : !activeCard ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center text-amber-200/30">
                <p className="text-lg mb-1">Select a card to begin testing</p>
                <p className="text-sm">Click any card in the left panel</p>
              </div>
            </div>
          ) : !isActive ? (
            <div className="flex-1 flex flex-col items-center justify-center gap-4">
              <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-amber-400" />
              <p className="text-amber-200/60 text-sm">Loading game for {activeCard.name}…</p>
              {error && <p className="text-red-400 text-sm">{error}</p>}
            </div>
          ) : (
            <div className="flex-1 flex flex-col overflow-hidden">
              {/* P2 area */}
              <div className="flex-1 bg-red-900/10 border-l-4 border-red-500/30 p-3 overflow-hidden">
                <PlayerBoard
                  player={player2}
                  isOpponent={activePlayer === 0}
                  isActive={activePlayer === 1}
                  isOwnerTurn={activePlayer === 1}
                  onSelectCard={(zone, idx) => {
                    if (activePlayer === 1) {
                      if (zone === 'hand') { setSelectedHandIndex(idx); setSelectedFieldIndex(null); setAttackMode(false) }
                      else if (zone === 'field') { setSelectedFieldIndex(idx); setSelectedHandIndex(null) }
                    }
                  }}
                  selectedIndex={activePlayer === 1 ? (selectedHandIndex !== null ? selectedHandIndex : selectedFieldIndex) : null}
                  selectedZone={activePlayer === 1 ? (selectedHandIndex !== null ? 'hand' : selectedFieldIndex !== null ? 'field' : undefined) : undefined}
                />
              </div>

              {/* Combat divider */}
              {pendingAttack ? (
                <div className="flex-shrink-0 bg-stone-800/50 border-y border-amber-900/30 px-3 py-2 space-y-2">
                  {/* Attack info */}
                  <div className="flex items-center justify-center gap-4 text-sm">
                    <span className="text-amber-200 flex items-center gap-2">
                      <Swords className="w-4 h-4 text-red-400" />
                      {pendingAttack.attackerPower} vs {pendingAttack.targetName} ({pendingAttack.targetPower})
                    </span>
                  </div>

                  {/* Blocker step */}
                  {awaitingResponse === 'blocker' && (
                    <div className="flex items-center justify-center gap-2 flex-wrap">
                      <span className="text-blue-300 text-xs font-semibold">Blocker:</span>
                      {pendingAttack.availableBlockers?.length > 0 ? (
                        pendingAttack.availableBlockers.map(b => (
                          <button key={b.index}
                            onClick={() => blockerResponse(b.index)}
                            className="px-2 py-0.5 bg-blue-700 hover:bg-blue-600 text-white rounded text-xs">
                            {b.name} ({(b.power).toLocaleString()})
                          </button>
                        ))
                      ) : (
                        <span className="text-stone-400 text-xs">No blockers available</span>
                      )}
                      <button onClick={() => blockerResponse(null)}
                        className="px-3 py-0.5 bg-stone-600 hover:bg-stone-500 text-white rounded text-xs">
                        No Blocker
                      </button>
                    </div>
                  )}

                  {/* Counter step — multi-select */}
                  {awaitingResponse === 'counter' && (
                    <div className="flex items-center justify-center gap-1.5 flex-wrap">
                      <span className="text-green-300 text-xs font-semibold">Counter:</span>
                      {pendingAttack.availableCounters?.map(c => {
                        const isSelected = selectedCounterIndices.includes(c.index)
                        return (
                          <button key={c.index}
                            onClick={() => setSelectedCounterIndices(prev =>
                              isSelected ? prev.filter(i => i !== c.index) : [...prev, c.index]
                            )}
                            className={`px-2 py-0.5 rounded text-xs border transition-colors ${
                              isSelected
                                ? 'bg-green-600 border-green-400 text-white'
                                : 'bg-orange-600 hover:bg-orange-500 border-orange-400 text-white'
                            }`}>
                            {c.name} (+{c.counterValue}) {c.isEvent ? `[${c.cost} DON]` : ''}
                          </button>
                        )
                      })}
                      {selectedCounterIndices.length > 0 && (
                        <button onClick={() => { counterResponse(selectedCounterIndices); setSelectedCounterIndices([]) }}
                          className="px-3 py-0.5 bg-green-600 hover:bg-green-500 text-white rounded text-xs font-medium">
                          Use {selectedCounterIndices.length} Counter{selectedCounterIndices.length > 1 ? 's' : ''}
                        </button>
                      )}
                      <button onClick={() => { counterResponse([]); setSelectedCounterIndices([]) }}
                        className="px-3 py-0.5 bg-stone-600 hover:bg-stone-500 text-white rounded text-xs">
                        No Counter
                      </button>
                    </div>
                  )}

                  {/* Trigger step */}
                  {awaitingResponse === 'trigger' && pendingAttack.pendingTrigger && (
                    <div className="flex items-center justify-center gap-2 flex-wrap">
                      <span className="text-amber-300 text-xs font-semibold">Trigger:</span>
                      <span className="text-white text-xs">{pendingAttack.pendingTrigger.cardName}</span>
                      <span className="text-amber-200/60 text-[10px]">{pendingAttack.pendingTrigger.triggerText}</span>
                      <button onClick={() => triggerResponse(true)}
                        className="px-3 py-0.5 bg-amber-600 hover:bg-amber-500 text-white rounded text-xs font-medium">
                        Activate
                      </button>
                      <button onClick={() => triggerResponse(false)}
                        className="px-3 py-0.5 bg-stone-600 hover:bg-stone-500 text-white rounded text-xs">
                        Decline
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <div className="flex-shrink-0 h-10 bg-stone-800/50 border-y border-amber-900/30" />
              )}

              {/* P1 area */}
              <div className="flex-1 bg-blue-900/10 border-l-4 border-blue-500/30 p-3 overflow-hidden">
                <PlayerBoard
                  player={player1}
                  isOpponent={activePlayer === 1}
                  isActive={activePlayer === 0}
                  isOwnerTurn={activePlayer === 0}
                  onSelectCard={(zone, idx) => {
                    if (activePlayer === 0) {
                      if (zone === 'hand') { setSelectedHandIndex(idx); setSelectedFieldIndex(null); setAttackMode(false) }
                      else if (zone === 'field') { setSelectedFieldIndex(idx); setSelectedHandIndex(null) }
                    }
                  }}
                  selectedIndex={activePlayer === 0 ? (selectedHandIndex !== null ? selectedHandIndex : selectedFieldIndex) : null}
                  selectedZone={activePlayer === 0 ? (selectedHandIndex !== null ? 'hand' : selectedFieldIndex !== null ? 'field' : undefined) : undefined}
                />
              </div>

              {/* Action bar */}
              <div className="flex-shrink-0 bg-stone-800/90 border-t border-amber-900/50 px-3 py-2 flex items-center justify-between gap-2">
                <div className="flex items-center gap-2 flex-wrap">
                  {selectedHandIndex !== null && (
                    <button
                      onClick={() => handlePlayCard(selectedHandIndex)}
                      disabled={(currentPlayer.hand[selectedHandIndex]?.cost ?? 0) > currentPlayer.donActive}
                      className={`px-3 py-1.5 rounded text-sm font-medium ${
                        (currentPlayer.hand[selectedHandIndex]?.cost ?? 0) <= currentPlayer.donActive
                          ? 'bg-green-600 hover:bg-green-500 text-white'
                          : 'bg-stone-700 text-stone-500 cursor-not-allowed'
                      }`}
                    >
                      Play ({currentPlayer.hand[selectedHandIndex]?.cost ?? 0} DON)
                    </button>
                  )}
                  {selectedFieldIndex !== null && currentPlayer.donActive > 0 && (
                    <button onClick={() => handleAttachDon(selectedFieldIndex)}
                      className="px-3 py-1.5 bg-yellow-600 hover:bg-yellow-500 text-white rounded text-sm font-medium">
                      Attach DON
                    </button>
                  )}
                  {/* Attach DON to leader when nothing is selected */}
                  {selectedFieldIndex === null && selectedHandIndex === null && currentPlayer.donActive > 0 && (
                    <button onClick={() => attachDon(-1, 1)}
                      className="px-3 py-1.5 bg-yellow-700 hover:bg-yellow-600 text-white rounded text-sm font-medium">
                      Attach DON → Leader
                    </button>
                  )}
                  {selectedFieldIndex !== null && selectedFieldIndex >= 0 && !attackMode && !awaitingResponse && (
                    <button onClick={() => setAttackMode(true)}
                      className="px-3 py-1.5 bg-red-600 hover:bg-red-500 text-white rounded text-sm font-medium flex items-center gap-1">
                      <Swords className="w-3 h-3" /> Attack
                    </button>
                  )}
                  {attackMode && !awaitingResponse && (() => {
                    const attacker = selectedFieldIndex !== null && selectedFieldIndex >= 0
                      ? currentPlayer.field[selectedFieldIndex] : currentPlayer.leader
                    const attackerCanAttackActive = attacker?.canAttackActive ?? false
                    return (
                    <div className="flex items-center gap-1 flex-wrap">
                      <span className="text-amber-200/60 text-xs">Target:</span>
                      <button onClick={() => handleDeclareAttack(selectedFieldIndex!, -1)}
                        className="px-2 py-1 bg-red-600 hover:bg-red-500 text-white rounded text-xs">Leader</button>
                      {(activePlayer === 0 ? player2 : player1).field.map((card, idx) => {
                        const isTargetable = card.isResting || attackerCanAttackActive
                        return (
                        <button key={idx}
                          onClick={() => handleDeclareAttack(selectedFieldIndex!, idx)}
                          disabled={!isTargetable}
                          className={`px-2 py-1 rounded text-xs ${isTargetable ? 'bg-red-600 hover:bg-red-500 text-white' : 'bg-stone-700 text-stone-500 cursor-not-allowed'}`}>
                          {card.name.slice(0, 8)}
                        </button>
                        )
                      })}
                      <button onClick={() => { setAttackMode(false); if (selectedFieldIndex === -1) setSelectedFieldIndex(null); }}
                        className="px-2 py-1 bg-stone-600 hover:bg-stone-500 text-white rounded text-xs">Cancel</button>
                    </div>
                  )})()}
                  {selectedFieldIndex === null && !selectedHandIndex && turn >= 3 && !currentPlayer.leader?.isResting && !awaitingResponse && !attackMode && (
                    <button onClick={() => { setSelectedFieldIndex(-1); setAttackMode(true); }}
                      className="px-3 py-1.5 bg-red-700 hover:bg-red-600 text-white rounded text-sm flex items-center gap-1">
                      <Swords className="w-3 h-3" /> Leader Attack
                    </button>
                  )}
                  {selectedFieldIndex !== null && selectedFieldIndex >= 0 && (
                    <>
                      <button onClick={() => activateEffect(selectedFieldIndex)}
                        className="px-3 py-1.5 bg-purple-600 hover:bg-purple-500 text-white rounded text-sm">
                        Activate
                      </button>
                      <button onClick={() => simulateKo(selectedFieldIndex)}
                        className="px-3 py-1.5 bg-stone-600 hover:bg-stone-500 text-red-300 rounded text-sm border border-red-500/30">
                        KO
                      </button>
                    </>
                  )}
                  {selectedFieldIndex === null && selectedHandIndex === null &&
                    currentPlayer.leader?.effect?.includes('[Activate: Main]') && (
                    <button onClick={() => activateEffect(-1)}
                      className="px-3 py-1.5 bg-purple-700 hover:bg-purple-600 text-white rounded text-sm">
                      Activate Leader
                    </button>
                  )}
                </div>
                <button onClick={endTurn}
                  className="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded text-sm font-medium flex-shrink-0">
                  End Turn
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ── Bottom verdict bar ── */}
      {activeCard && (
        <div className="flex-shrink-0 bg-stone-900 border-t border-amber-900/50 px-4 py-2 flex items-center gap-3">
          <div className="flex-1 min-w-0">
            <span className="text-xs text-stone-400 font-mono">{activeCard.id}</span>
            <span className="mx-2 text-stone-600">·</span>
            <span className="text-xs text-amber-200/70 line-clamp-1">{activeCard.effect || activeCard.trigger || 'No effect text'}</span>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            {failNoteOpen ? (
              <div className="flex items-center gap-2">
                <input
                  value={failNote}
                  onChange={e => setFailNote(e.target.value)}
                  placeholder="Describe the issue…"
                  className="w-48 px-2 py-1 bg-stone-800 border border-stone-600 rounded text-xs text-white"
                  onKeyDown={e => { if (e.key === 'Enter') submitVerdict('fail', failNote) }}
                  autoFocus
                />
                <button onClick={() => submitVerdict('fail', failNote)} disabled={verdictSaving}
                  className="px-3 py-1 bg-red-600 hover:bg-red-500 text-white rounded text-xs">
                  Confirm Fail
                </button>
                <button onClick={() => setFailNoteOpen(false)}
                  className="px-2 py-1 bg-stone-700 hover:bg-stone-600 text-white rounded text-xs">
                  Cancel
                </button>
              </div>
            ) : (
              <>
                <button onClick={() => submitVerdict('skip')} disabled={verdictSaving}
                  className="flex items-center gap-1 px-3 py-1.5 bg-stone-700 hover:bg-stone-600 text-stone-300 rounded text-xs font-medium">
                  <SkipForward className="w-3 h-3" /> Skip
                </button>
                <button onClick={() => setFailNoteOpen(true)} disabled={verdictSaving}
                  className="flex items-center gap-1 px-3 py-1.5 bg-red-800/80 hover:bg-red-700/80 text-red-300 rounded text-xs font-medium">
                  <XCircle className="w-3 h-3" /> Fail
                </button>
                <button onClick={() => submitVerdict('pass')} disabled={verdictSaving}
                  className="flex items-center gap-1 px-3 py-1.5 bg-green-700 hover:bg-green-600 text-white rounded text-xs font-medium">
                  <CheckCircle2 className="w-3 h-3" /> Pass
                </button>
              </>
            )}
            <span className={`text-xs ml-1 ${STATUS_COLOR[localStatuses[activeCard.id] ?? activeCard.status] ?? 'text-stone-500'}`}>
              {localStatuses[activeCard.id] ?? activeCard.status}
            </span>
          </div>
        </div>
      )}

      {/* ── Debug panel ── */}
      {isActive && (
        <div className="fixed left-2 bottom-20 z-50">
          <button onClick={() => setDebugOpen(o => !o)}
            className="px-2 py-0.5 bg-violet-800/80 hover:bg-violet-700/80 text-violet-200 text-[10px] rounded border border-violet-600/50">
            {debugOpen ? '▲ Debug' : '▼ Debug'}
          </button>
          {debugOpen && (
            <div className="mt-1 w-64 bg-stone-900/95 border border-violet-700/50 rounded p-2 space-y-2 text-xs text-stone-300">
              <div>
                <p className="text-violet-300 text-[10px] font-semibold mb-1">P1 DON</p>
                <div className="flex gap-1">
                  {[0,3,5,7,10].map(n => (
                    <button key={n} onClick={() => debugSetScenario({ donActive: n })}
                      className="px-1.5 py-0.5 bg-stone-700 hover:bg-stone-600 rounded text-[10px]">{n}</button>
                  ))}
                </div>
              </div>
              <div>
                <p className="text-violet-300 text-[10px] font-semibold mb-1">Life</p>
                <div className="flex gap-1">
                  {[0,1,2,3,5].map(n => (
                    <button key={`life-${n}`} onClick={() => debugSetScenario({ life: n })}
                      className="px-1.5 py-0.5 bg-stone-700 hover:bg-stone-600 rounded text-[10px]">P1:{n}</button>
                  ))}
                </div>
              </div>
              <div className="flex gap-1">
                <button onClick={() => debugSetScenario({ clearField: true })}
                  className="px-1.5 py-0.5 bg-red-900/60 hover:bg-red-800/60 rounded text-[10px]">Clear P1 Field</button>
                <button onClick={() => debugSetScenario({ clearOppField: true })}
                  className="px-1.5 py-0.5 bg-red-900/60 hover:bg-red-800/60 rounded text-[10px]">Clear P2 Field</button>
              </div>
              <div>
                <p className="text-violet-300 text-[10px] font-semibold mb-1">Add card by ID</p>
                <input value={debugCardInput} onChange={e => setDebugCardInput(e.target.value)}
                  placeholder="e.g. OP01-007"
                  className="w-full px-1.5 py-0.5 bg-stone-800 border border-stone-600 rounded text-[10px] text-white mb-1" />
                <div className="flex gap-1">
                  <button onClick={() => { debugSetScenario({ addToHand: [debugCardInput] }); setDebugCardInput('') }}
                    className="px-1.5 py-0.5 bg-blue-800/60 hover:bg-blue-700/60 rounded text-[10px]">→ Hand</button>
                  <button onClick={() => { debugSetScenario({ addToField: [debugCardInput] }); setDebugCardInput('') }}
                    className="px-1.5 py-0.5 bg-blue-800/60 hover:bg-blue-700/60 rounded text-[10px]">→ P1 Field</button>
                  <button onClick={() => { debugSetScenario({ addToOppField: [debugCardInput] }); setDebugCardInput('') }}
                    className="px-1.5 py-0.5 bg-orange-800/60 hover:bg-orange-700/60 rounded text-[10px]">→ P2 Field</button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ── Game log ── */}
      {isActive && (
        <div className="fixed right-2 bottom-20 w-52 h-40 bg-stone-800/90 backdrop-blur rounded border border-amber-900/50 overflow-hidden flex flex-col z-50">
          <div className="px-2 py-0.5 bg-stone-700/50 text-[10px] font-medium text-amber-200/80 border-b border-amber-900/30">
            Game Log
          </div>
          <div className="flex-1 p-1.5 overflow-y-auto text-[9px] text-amber-200/60 space-y-0.5">
            {logs.slice(-30).map((log, i) => (
              <div key={i} className={
                log.includes('[EFFECT]') ? 'text-purple-400' :
                log.includes('Turn') ? 'text-amber-400' :
                log.includes('attacks') ? 'text-red-400' : ''
              }>{log}</div>
            ))}
          </div>
        </div>
      )}

      {/* ── Game over modal ── */}
      {gameOver && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-[100]">
          <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}
            className="bg-stone-800 rounded-xl border border-amber-900/50 p-6 text-center">
            <h2 className="text-2xl font-bold text-amber-200 mb-3">Game Over</h2>
            <p className={`text-xl font-bold mb-4 ${winner === 0 ? 'text-blue-400' : 'text-red-400'}`}>
              {winner === 0 ? 'Player 1 Wins' : 'Player 2 Wins'}
            </p>
            {activeCard && (
              <button onClick={() => startTestGame(activeCard.id)}
                className="px-5 py-2 bg-amber-600 hover:bg-amber-500 text-white rounded font-medium flex items-center gap-2 mx-auto">
                <RotateCcw className="w-4 h-4" /> Restart Test
              </button>
            )}
          </motion.div>
        </div>
      )}

      {/* ── Effect choice modal ── */}
      {pendingChoice && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
          <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}
            className="bg-stone-800 rounded-xl border border-amber-900/50 p-5 max-w-sm w-full mx-4">
            <h3 className="text-lg font-bold text-amber-200 mb-1">{pendingChoice.sourceCardName || 'Effect Choice'}</h3>
            <p className="text-stone-300 text-sm mb-3">{pendingChoice.prompt}</p>
            {pendingChoice.maxSelections > 1 ? (
              // Multi-select: checkboxes + confirm button
              <>
                <div className="space-y-1.5 max-h-56 overflow-y-auto mb-3">
                  {pendingChoice.options.map(opt => {
                    const checked = selectedChoiceIds.includes(opt.id)
                    const atMax = selectedChoiceIds.length >= pendingChoice.maxSelections
                    return (
                      <label key={opt.id}
                        className={`flex items-center gap-2 p-2 rounded cursor-pointer border transition-colors ${
                          checked ? 'bg-amber-600/30 border-amber-500' : 'bg-stone-700/50 border-stone-600 hover:border-stone-500'
                        } ${!checked && atMax ? 'opacity-40 cursor-not-allowed' : ''}`}>
                        <input type="checkbox" checked={checked}
                          disabled={!checked && atMax}
                          onChange={() => setSelectedChoiceIds(prev =>
                            prev.includes(opt.id) ? prev.filter(id => id !== opt.id) : [...prev, opt.id]
                          )}
                          className="accent-amber-500" />
                        <span className="text-sm text-white">{opt.label || opt.cardName || opt.id}</span>
                      </label>
                    )
                  })}
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => submitEffectChoice(pendingChoice.choiceId, selectedChoiceIds)}
                    disabled={selectedChoiceIds.length < pendingChoice.minSelections}
                    className={`flex-1 p-2 rounded text-sm font-medium ${
                      selectedChoiceIds.length >= pendingChoice.minSelections
                        ? 'bg-amber-600 hover:bg-amber-500 text-white'
                        : 'bg-stone-700 text-stone-500 cursor-not-allowed'
                    }`}>
                    Confirm ({selectedChoiceIds.length})
                  </button>
                  {pendingChoice.minSelections === 0 && (
                    <button onClick={() => submitEffectChoice(pendingChoice.choiceId, [])}
                      className="px-3 p-2 bg-stone-600 hover:bg-stone-500 text-white rounded text-sm">
                      Skip
                    </button>
                  )}
                </div>
              </>
            ) : (
              // Single-select: click immediately
              <>
                <div className="space-y-1.5 max-h-56 overflow-y-auto">
                  {pendingChoice.options.map(opt => (
                    <button key={opt.id}
                      onClick={() => submitEffectChoice(pendingChoice.choiceId, [opt.id])}
                      className="w-full p-2 bg-amber-600 hover:bg-amber-500 text-white rounded text-sm text-left">
                      {opt.label || opt.cardName || opt.id}
                    </button>
                  ))}
                </div>
                {pendingChoice.minSelections === 0 && (
                  <button onClick={() => submitEffectChoice(pendingChoice.choiceId, [])}
                    className="w-full mt-3 p-2 bg-stone-600 hover:bg-stone-500 text-white rounded text-sm">
                    Skip
                  </button>
                )}
              </>
            )}
          </motion.div>
        </div>
      )}
    </div>
  )
}

// ── PlayerBoard ───────────────────────────────────────────────────────────

function PlayerBoard({
  player, isOpponent, isActive, isOwnerTurn, onSelectCard, selectedIndex, selectedZone,
}: {
  player: PlaytestPlayer
  isOpponent: boolean
  isActive: boolean
  isOwnerTurn: boolean
  onSelectCard: (zone: 'hand' | 'field' | 'leader', index: number) => void
  selectedIndex: number | null
  selectedZone?: 'hand' | 'field' | 'leader'
}) {
  const [trashOpen, setTrashOpen] = useState(false)

  return (
    <div className="h-full flex flex-col gap-1.5">
      {/* Stats */}
      <div className="flex items-center justify-between text-xs">
        <div className="flex items-center gap-3">
          <span className={`font-bold ${isOpponent ? 'text-red-400' : 'text-blue-400'}`}>{player.name}</span>
          {isActive && <span className="px-1.5 py-0.5 bg-green-500/20 text-green-400 text-[10px] rounded">Active</span>}
        </div>
        <div className="flex items-center gap-3 text-amber-200/60">
          <span className="flex items-center gap-1"><Heart className="w-3 h-3 text-red-400" />{player.lifeCards.length}</span>
          <span className="flex items-center gap-1"><Layers className="w-3 h-3" />{player.deck.length}</span>
          <button
            onClick={() => setTrashOpen(o => !o)}
            className={`flex items-center gap-1 hover:text-amber-200 transition-colors ${trashOpen ? 'text-amber-200' : ''}`}
          >
            <Trash2 className="w-3 h-3 text-stone-400" />{player.trash.length}
          </button>
          <span className="text-yellow-400 font-bold">DON: {player.donActive}/{player.donActive + player.donRested}</span>
        </div>
      </div>

      {/* DON!! Pool — visual cards */}
      {player.donPool.length > 0 && (
        <div className="flex items-center gap-0.5 px-1">
          <span className="text-[8px] text-yellow-400/50 mr-1">DON!!</span>
          {player.donPool.map((state, i) => (
            <div
              key={i}
              className={`transition-all duration-300 ${state === 'rested' ? 'rotate-90 mx-1' : ''}`}
              title={`DON #${i + 1} (${state})`}
            >
              <div className={`w-5 h-7 rounded-sm border flex items-center justify-center text-[7px] font-black
                ${state === 'active'
                  ? 'border-yellow-400 bg-gradient-to-b from-yellow-500 to-amber-700 text-yellow-100 shadow-sm shadow-yellow-500/30'
                  : 'border-stone-500 bg-gradient-to-b from-stone-500 to-stone-700 text-stone-300 opacity-60'
                }`}
              >
                D
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Trash viewer */}
      {trashOpen && (
        <div className="bg-stone-800/90 border border-stone-600 rounded p-2 max-h-32 overflow-y-auto">
          <div className="flex items-center justify-between mb-1">
            <span className="text-[10px] text-stone-400 font-semibold">TRASH ({player.trash.length})</span>
            <button onClick={() => setTrashOpen(false)} className="text-[10px] text-stone-500 hover:text-stone-300">Close</button>
          </div>
          {player.trash.length === 0 ? (
            <span className="text-[10px] text-stone-500 italic">Empty</span>
          ) : (
            <div className="flex flex-wrap gap-1">
              {player.trash.map((card, idx) => (
                <span key={card.instanceId || idx}
                  className="px-1.5 py-0.5 bg-stone-700/80 rounded text-[10px] text-amber-200/70 border border-stone-600"
                  title={`${card.name} | ${card.cardType} | Cost: ${card.cost ?? '—'} | Power: ${card.power ?? '—'}`}
                >
                  {card.name}
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Leader + Field */}
      <div className="flex gap-3 flex-1 min-h-0">
        <div className="flex flex-col items-center">
          {player.leader && (
            <CardDisplay card={player.leader} size="large"
              isSelected={selectedZone === 'leader' && selectedIndex === 0}
              onClick={() => !isOpponent && onSelectCard('leader', 0)}
              isOwnerTurn={isOwnerTurn} />
          )}
          <div className="text-[9px] text-amber-200/50 mt-0.5">LEADER</div>
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-[9px] text-amber-200/30 mb-0.5">FIELD ({player.field.length}/5)</div>
          <div className="flex gap-1.5 flex-wrap">
            <AnimatePresence>
              {player.field.map((card, idx) => (
                <motion.div key={card.instanceId}
                  initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.8 }}>
                  <CardDisplay card={card} size="medium"
                    isSelected={selectedZone === 'field' && selectedIndex === idx}
                    onClick={() => !isOpponent && onSelectCard('field', idx)}
                    isOwnerTurn={isOwnerTurn} />
                </motion.div>
              ))}
            </AnimatePresence>
            {player.field.length === 0 && (
              <span className="text-amber-200/20 text-xs italic">Empty</span>
            )}
          </div>
        </div>
      </div>

      {/* Hand (own player only) */}
      {!isOpponent && (
        <div>
          <div className="text-[9px] text-amber-200/30 mb-0.5">HAND ({player.hand.length})</div>
          <div className="flex gap-1.5 overflow-x-auto pb-1">
            <AnimatePresence>
              {player.hand.map((card, idx) => (
                <motion.div key={card.instanceId}
                  initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                  whileHover={{ y: -6 }}>
                  <CardDisplay card={card} size="small"
                    isSelected={selectedZone === 'hand' && selectedIndex === idx}
                    onClick={() => onSelectCard('hand', idx)}
                    showCost canAfford={(card.cost ?? 0) <= player.donActive} />
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>
      )}
      {isOpponent && (
        <div className="text-amber-200/40 text-xs">Hand: {player.hand.length} cards</div>
      )}
    </div>
  )
}

// ── CardHoverPreview ──────────────────────────────────────────────────────

function CardHoverPreview({ card, anchorRect }: { card: PlaytestCard; anchorRect: DOMRect }) {
  // Position the preview so it doesn't go off-screen
  const previewW = 300
  const previewH = 420
  let left = anchorRect.right + 12
  let top = anchorRect.top - 40

  // Flip to left side if it would overflow the right edge
  if (left + previewW > window.innerWidth - 8) {
    left = anchorRect.left - previewW - 12
  }
  // Clamp vertical
  if (top + previewH > window.innerHeight - 8) {
    top = window.innerHeight - previewH - 8
  }
  if (top < 8) top = 8

  return createPortal(
    <div
      className="fixed z-[9999] pointer-events-none"
      style={{ left, top, width: previewW }}
    >
      <div className="bg-stone-900 border-2 border-amber-500 rounded-lg shadow-2xl shadow-black/80 overflow-hidden">
        {card.imageUrl ? (
          <img
            src={card.imageUrl}
            alt={card.name}
            className="w-full object-contain"
            style={{ maxHeight: previewH }}
          />
        ) : (
          <div className="p-4 text-white space-y-2" style={{ minHeight: 200 }}>
            <div className="text-lg font-bold text-amber-300">{card.name}</div>
            {card.cost != null && <div className="text-sm">Cost: {card.cost}</div>}
            {card.power != null && <div className="text-sm">Power: {card.power}</div>}
            <div className="text-xs text-stone-400">{card.id}</div>
          </div>
        )}
      </div>
    </div>,
    document.body
  )
}

// ── CardDisplay ───────────────────────────────────────────────────────────

function CardDisplay({ card, size, isSelected, onClick, showCost, canAfford, isOwnerTurn }: {
  card: PlaytestCard
  size: 'small' | 'medium' | 'large'
  isSelected?: boolean
  onClick?: () => void
  showCost?: boolean
  canAfford?: boolean
  isOwnerTurn?: boolean
}) {
  const widths: Record<string, string> = { small: 'w-11', medium: 'w-14', large: 'w-16' }
  const donBonus = isOwnerTurn ? (card.attachedDon * 1000) : 0
  const power = card.power ? card.power + donBonus : null

  // Detect modified power/cost (effect-based changes, not DON bonus)
  const basePower = card.basePower ?? card.power
  const baseCost = card.baseCost ?? card.cost
  const powerModified = basePower !== null && card.power !== null && card.power !== basePower
  const costModified = baseCost !== null && card.cost !== null && card.cost !== baseCost
  const powerUp = powerModified && (card.power ?? 0) > (basePower ?? 0)
  const powerDown = powerModified && (card.power ?? 0) < (basePower ?? 0)
  const costDown = costModified && (card.cost ?? 0) < (baseCost ?? 0)

  const [hovered, setHovered] = useState(false)
  const ref = useRef<HTMLDivElement>(null)
  const [rect, setRect] = useState<DOMRect | null>(null)

  const onEnter = useCallback(() => {
    if (ref.current) setRect(ref.current.getBoundingClientRect())
    setHovered(true)
  }, [])
  const onLeave = useCallback(() => setHovered(false), [])

  return (
    <div
      ref={ref}
      className={`cursor-pointer ${card.isResting ? 'rotate-90 my-2' : ''}`}
      onClick={onClick}
      onMouseEnter={onEnter}
      onMouseLeave={onLeave}
    >
      <div className={`relative ${widths[size]} aspect-[2.5/3.5] rounded border-2 overflow-hidden transition-all ${
        isSelected ? 'border-yellow-400 shadow-lg shadow-yellow-400/30'
        : canAfford === false ? 'border-red-500/50'
        : canAfford === true ? 'border-green-500/50 hover:border-green-400'
        : 'border-amber-900/50 hover:border-amber-500'
      }`}>
        {card.imageUrl ? (
          <img src={card.imageUrl} alt={card.name} className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-stone-600 to-stone-800 flex items-center justify-center text-[7px] text-white text-center p-0.5 leading-tight">
            {card.name}
          </div>
        )}
        {/* Cost reduction indicator — top-left badge */}
        {costDown && (
          <div className="absolute top-0 left-0 bg-blue-600/90 text-white text-[7px] font-bold px-0.5 rounded-br leading-tight"
            title={`Cost reduced: ${baseCost} → ${card.cost}`}>
            {card.cost}
          </div>
        )}
        {/* Power modification indicator — bottom overlay */}
        {powerModified && (
          <div className={`absolute bottom-0 inset-x-0 text-[7px] font-bold text-center leading-tight py-px
            ${powerUp ? 'bg-green-600/80 text-green-100' : 'bg-red-600/80 text-red-100'}`}
            title={`Power: ${basePower} → ${card.power}`}>
            {powerUp ? '\u25B2' : '\u25BC'}{card.power}
          </div>
        )}
      </div>
      {card.attachedDon > 0 && (
        <div className="text-[9px] text-yellow-400 text-center">+{card.attachedDon}</div>
      )}
      {power !== null && power > 0 && (
        <div className={`text-[9px] font-bold text-center ${
          powerUp ? 'text-green-400' : powerDown ? 'text-red-400' : 'text-amber-300'
        }`}>{power.toLocaleString()}</div>
      )}
      {showCost && card.cost !== null && (
        <div className={`text-[9px] text-center ${
          costDown ? 'text-blue-400 font-bold' : canAfford ? 'text-green-400' : 'text-red-400'
        }`}>{card.cost}{costDown ? ` (was ${baseCost})` : ''}</div>
      )}
      {hovered && rect && <CardHoverPreview card={card} anchorRect={rect} />}
    </div>
  )
}

export default EffectTesterPage
