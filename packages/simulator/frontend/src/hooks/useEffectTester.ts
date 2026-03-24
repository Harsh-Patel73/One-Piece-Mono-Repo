/**
 * useEffectTester — Socket.IO hook for the web-based card effect tester.
 *
 * Manages both:
 *  1. The effect test queue (card list, navigation, verdicts)
 *  2. An interactive playtest game that auto-starts for each card being tested
 */

import { useState, useEffect, useRef, useCallback } from 'react'
import { io, Socket } from 'socket.io-client'
import type { PlaytestCard, PlaytestPlayer, PendingChoice, PendingAttack } from './usePlaytestSocket'

// ── Effect test queue types ────────────────────────────────────────────────

export interface EffectTestState {
  done: boolean
  card_id: string
  card_name: string
  card_type: string
  current_status: string
  notes: string
  effect_text: string
  trigger_text: string
  timings: string[]
  index: number
  total: number
}

// ── Game state types (mirrors usePlaytestSocket) ───────────────────────────

export interface GameState {
  isActive: boolean
  gameId: string | null
  turn: number
  activePlayer: 0 | 1
  phase: string
  player1: PlaytestPlayer
  player2: PlaytestPlayer
  logs: string[]
  gameOver: boolean
  winner: 0 | 1 | null
  awaitingResponse: string | null
  pendingAttack: PendingAttack | null
  pendingChoice: PendingChoice | null
}

// ── Backend response types ─────────────────────────────────────────────────

interface BackendCard {
  id: string; name: string; card_type: string
  cost: number | null; power: number | null; counter: number | null
  effect: string | null; trigger: string | null; attribute: string | null
  image_url: string | null; image_link: string | null
  is_resting: boolean; attached_don: number; has_attacked: boolean
}
interface BackendPlayer {
  player_id: string; name: string; leader: BackendCard
  life_count: number; hand_count: number; hand: BackendCard[]
  deck_count: number; field: BackendCard[]
  trash_count: number; don_active: number; don_total: number
  has_mulliganed: boolean
}
interface BackendPendingChoice {
  choice_id: string; choice_type: string; prompt: string
  options: Array<{ id: string; label: string; card_id?: string; card_name?: string }>
  min_selections: number; max_selections: number
  source_card_id: string | null; source_card_name: string | null
}
interface BackendGameState {
  game_id: string; turn: number; phase: string; active_player: number
  players: BackendPlayer[]
  is_terminal: boolean; winner: number | null; awaiting_response: string | null
  pending_attack: any | null; pending_choice: BackendPendingChoice | null
}

function convertCard(card: BackendCard, index: number): PlaytestCard {
  return {
    instanceId: `${card.id}-${index}-${Date.now()}`,
    id: card.id, name: card.name, cardType: card.card_type,
    cost: card.cost, power: card.power, counter: card.counter,
    effect: card.effect, trigger: card.trigger, attribute: card.attribute,
    imageUrl: card.image_url || card.image_link,
    isResting: card.is_resting, attachedDon: card.attached_don, hasAttacked: card.has_attacked,
  }
}

function convertPlayer(player: BackendPlayer): PlaytestPlayer {
  return {
    name: player.name,
    leader: player.leader ? convertCard(player.leader, 0) : null,
    lifeCards: Array(player.life_count).fill(null).map((_, i) => ({
      instanceId: `life-${i}`, id: 'hidden', name: 'Life Card', cardType: 'HIDDEN',
      cost: null, power: null, counter: null, effect: null, trigger: null, attribute: null,
      imageUrl: null, isResting: false, attachedDon: 0, hasAttacked: false,
    })),
    hand: player.hand.map((c, i) => convertCard(c, i)),
    deck: Array(player.deck_count).fill(null).map((_, i) => ({
      instanceId: `deck-${i}`, id: 'hidden', name: 'Card', cardType: 'HIDDEN',
      cost: null, power: null, counter: null, effect: null, trigger: null, attribute: null,
      imageUrl: null, isResting: false, attachedDon: 0, hasAttacked: false,
    })),
    field: player.field.map((c, i) => convertCard(c, i)),
    trash: [],
    donActive: player.don_active,
    donRested: player.don_total - player.don_active,
    donDeck: Math.max(0, 10 - player.don_total),
  }
}

function emptyPlayer(name: string): PlaytestPlayer {
  return {
    name, leader: null, lifeCards: [], hand: [], deck: [], field: [], trash: [],
    donActive: 0, donRested: 0, donDeck: 10,
  }
}

const initialGameState: GameState = {
  isActive: false, gameId: null, turn: 0, activePlayer: 0, phase: 'WAITING',
  player1: emptyPlayer('Tester'), player2: emptyPlayer('Opponent'),
  logs: [], gameOver: false, winner: null,
  awaitingResponse: null, pendingAttack: null, pendingChoice: null,
}

// ── Hook ──────────────────────────────────────────────────────────────────

export function useEffectTester() {
  const socketRef = useRef<Socket | null>(null)
  const logsRef   = useRef<string[]>([])

  const [isConnected, setIsConnected] = useState(false)
  const [queueState, setQueueState]   = useState<EffectTestState | null>(null)
  const [gameState, setGameState]     = useState<GameState>(initialGameState)
  const [isLoading, setIsLoading]     = useState(false)
  const [error, setError]             = useState<string | null>(null)

  // Connect on mount
  useEffect(() => {
    const socket = io('/', { path: '/socket.io', transports: ['websocket', 'polling'] })
    socketRef.current = socket

    socket.on('connect',    () => setIsConnected(true))
    socket.on('disconnect', () => {
      setIsConnected(false)
      setGameState(g => ({ ...g, pendingChoice: null, pendingAttack: null }))
    })
    socket.on('error', (d: { message: string }) => {
      setError(d.message)
      setIsLoading(false)
      setGameState(g => ({ ...g, pendingChoice: null }))
    })

    // ── Queue events ──────────────────────────────────────────────
    socket.on('effect_test_update', (payload: EffectTestState & { done: boolean }) => {
      setIsLoading(false)
      setQueueState(payload)
      setError(null)
      // Auto-start interactive game for the new card
      if (!payload.done && payload.card_id) {
        socket.emit('start_test_game', { card_id: payload.card_id })
      }
    })

    // ── Game events ───────────────────────────────────────────────
    socket.on('game_started', (data: { game_id: string; game_state: BackendGameState }) => {
      const gs = data.game_state
      logsRef.current = ['Test game started']
      setGameState({
        isActive: true, gameId: data.game_id,
        turn: gs.turn, activePlayer: gs.active_player as 0 | 1, phase: gs.phase,
        player1: convertPlayer(gs.players[0]),
        player2: convertPlayer(gs.players[1]),
        logs: logsRef.current,
        gameOver: false, winner: null, error: null,
        awaitingResponse: null, pendingAttack: null, pendingChoice: null,
      } as any)
    })

    socket.on('game_update', (data: { game_state: BackendGameState; logs: string[] }) => {
      const gs = data.game_state
      if (data.logs?.length) {
        logsRef.current = [...logsRef.current, ...data.logs]
      }
      setGameState(prev => ({
        ...prev,
        turn: gs.turn, activePlayer: gs.active_player as 0 | 1, phase: gs.phase,
        player1: convertPlayer(gs.players[0]),
        player2: convertPlayer(gs.players[1]),
        logs: logsRef.current,
        awaitingResponse: gs.awaiting_response,
        pendingAttack: gs.pending_attack ? gs.pending_attack : null,
        pendingChoice: gs.pending_choice ? {
          choiceId: gs.pending_choice.choice_id,
          choiceType: gs.pending_choice.choice_type,
          prompt: gs.pending_choice.prompt,
          options: gs.pending_choice.options.map(o => ({
            id: o.id, label: o.label, cardId: o.card_id, cardName: o.card_name,
          })),
          minSelections: gs.pending_choice.min_selections,
          maxSelections: gs.pending_choice.max_selections,
          sourceCardId: gs.pending_choice.source_card_id,
          sourceCardName: gs.pending_choice.source_card_name,
        } : null,
      }))
    })

    socket.on('game_over', () => {
      setGameState(prev => ({ ...prev, gameOver: true }))
    })

    return () => { socket.disconnect() }
  }, [])

  // ── Queue actions ──────────────────────────────────────────────

  const startTest = useCallback((opts: {
    setCode?: string
    filter?: 'todo' | 'needsfix' | 'all'
    cardId?: string
  }) => {
    setIsLoading(true)
    setError(null)
    socketRef.current?.emit('start_effect_test', {
      set_code: opts.setCode ?? 'OP01',
      filter:   opts.filter  ?? 'todo',
      card_id:  opts.cardId,
    })
  }, [])

  const navigate = useCallback((direction: 'next' | 'prev' | 'rerun') => {
    setIsLoading(true)
    socketRef.current?.emit('effect_test_navigate', { direction })
  }, [])

  const submitVerdict = useCallback((
    cardId: string,
    verdict: 'pass' | 'fail' | 'skip',
    note?: string,
  ) => {
    setIsLoading(true)
    socketRef.current?.emit('effect_test_verdict', { card_id: cardId, verdict, note: note ?? '' })
  }, [])

  // ── Game actions ───────────────────────────────────────────────

  const startTestGame = useCallback((cardId: string, timing?: string) => {
    socketRef.current?.emit('start_test_game', { card_id: cardId, timing })
  }, [])

  const playCard = useCallback((index: number) => {
    socketRef.current?.emit('play_card', { card_index: index })
  }, [])

  const attachDon = useCallback((index: number, amount = 1) => {
    socketRef.current?.emit('attach_don', { card_index: index, amount })
  }, [])

  const declareAttack = useCallback((attackerIdx: number, targetIdx: number) => {
    socketRef.current?.emit('attack', { attacker_index: attackerIdx, target_index: targetIdx })
  }, [])

  const blockerResponse = useCallback((blockerIndex: number | null) => {
    socketRef.current?.emit('blocker_response', { blocker_index: blockerIndex })
  }, [])

  const counterResponse = useCallback((counterIndices: number[]) => {
    socketRef.current?.emit('counter_response', { counter_indices: counterIndices })
  }, [])

  const activateEffect = useCallback((index: number) => {
    socketRef.current?.emit('activate_effect', { card_index: index })
  }, [])

  const endTurn = useCallback(() => {
    socketRef.current?.emit('end_turn', {})
  }, [])

  const submitEffectChoice = useCallback((choiceId: string, selected: string[]) => {
    socketRef.current?.emit('effect_choice_response', { choice_id: choiceId, selected })
  }, [])

  const debugSetScenario = useCallback((scenario: {
    life?: number; opponentLife?: number; donActive?: number
    addToHand?: string[]; addToField?: string[]; addToOppField?: string[]
    clearHand?: boolean; clearField?: boolean; clearOppField?: boolean
  }) => {
    socketRef.current?.emit('debug_scenario', {
      player_index: 0,
      life: scenario.life, opponent_life: scenario.opponentLife,
      don_active: scenario.donActive,
      add_to_hand: scenario.addToHand, add_to_field: scenario.addToField,
      add_to_opp_field: scenario.addToOppField,
      clear_hand: scenario.clearHand, clear_field: scenario.clearField,
      clear_opp_field: scenario.clearOppField,
    })
  }, [])

  return {
    isConnected, isLoading, error,
    queueState, gameState,
    // Queue
    startTest, navigate, submitVerdict,
    // Game
    startTestGame, playCard, attachDon, declareAttack,
    blockerResponse, counterResponse, activateEffect,
    endTurn, submitEffectChoice, debugSetScenario,
  }
}
