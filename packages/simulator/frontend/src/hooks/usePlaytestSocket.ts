/**
 * Socket-based playtest hook that connects to the backend game engine.
 *
 * This hook replaces the local playtestStore with backend communication,
 * ensuring effects are processed by the shared game-engine package.
 */

import { useEffect, useState, useCallback, useRef } from 'react'
import { io, Socket } from 'socket.io-client'

// Connect via the Vite dev-server proxy so the URL works in all environments.
// The vite.config.ts proxy forwards /socket.io → http://localhost:8080.
const SOCKET_URL = '/'

// Types matching backend serialization
interface BackendCard {
  id: string
  name: string
  card_type: string
  cost: number | null
  power: number | null
  counter: number | null
  effect: string | null
  trigger: string | null
  attribute: string | null
  image_url: string | null
  image_link: string | null  // Backend sends image_link
  is_resting: boolean
  attached_don: number
  has_attacked: boolean
  can_attack_active: boolean
}

interface BackendPlayer {
  player_id: string
  name: string
  leader: BackendCard
  life_count: number
  hand_count: number
  hand: BackendCard[]
  deck_count: number
  field: BackendCard[]
  trash_count: number
  trash: BackendCard[]
  don_active: number
  don_total: number
  has_mulliganed: boolean
}

interface BackendPendingChoice {
  choice_id: string
  choice_type: string  // "select_cards", "choose_option", "select_target"
  prompt: string
  options: Array<{
    id: string
    label: string
    card_id?: string
    card_name?: string
  }>
  min_selections: number
  max_selections: number
  source_card_id: string | null
  source_card_name: string | null
}

interface BackendPendingAttack {
  attacker_name: string
  attacker_power: number
  attacker_index: number
  target_name: string
  target_power: number
  target_index: number
  is_leader: boolean
  leader_has_effect: boolean
  available_blockers: Array<{
    index: number
    name: string
    power: number
  }>
  available_counters: Array<{
    index: number
    name: string
    counter_value: number
    cost: number
    is_event: boolean
  }>
  counter_power: number
  pending_trigger: {
    card_id: string
    card_name: string
    trigger_text: string
    player_id: string
  } | null
}

interface BackendGameState {
  game_id: string
  turn: number
  phase: string
  active_player: number
  players: BackendPlayer[]
  is_terminal: boolean
  winner: number | null
  awaiting_response: string | null
  pending_attack: BackendPendingAttack | null
  pending_choice: BackendPendingChoice | null
}

// Frontend-compatible types (matching PlaytestPage expectations)
export interface PlaytestCard {
  instanceId: string
  id: string
  name: string
  cardType: string
  cost: number | null
  baseCost: number | null
  power: number | null
  basePower: number | null
  counter: number | null
  effect: string | null
  trigger: string | null
  attribute: string | null
  imageUrl: string | null
  traits?: string
  isResting: boolean
  attachedDon: number
  hasAttacked: boolean
  canAttackActive: boolean
}

export interface PlaytestPlayer {
  name: string
  leader: PlaytestCard | null
  lifeCards: PlaytestCard[]
  hand: PlaytestCard[]
  deck: PlaytestCard[]
  field: PlaytestCard[]
  trash: PlaytestCard[]
  donActive: number
  donRested: number
  donDeck: number
  donPool: ('active' | 'rested')[]
}

export interface PendingChoice {
  choiceId: string
  choiceType: string
  prompt: string
  options: Array<{
    id: string
    label: string
    cardId?: string
    cardName?: string
  }>
  minSelections: number
  maxSelections: number
  sourceCardId: string | null
  sourceCardName: string | null
}

export interface PendingAttack {
  attackerName: string
  attackerPower: number
  attackerIndex: number
  targetName: string
  targetPower: number
  targetIndex: number
  isLeader: boolean
  leaderHasEffect: boolean
  availableBlockers: Array<{
    index: number
    name: string
    power: number
  }>
  availableCounters: Array<{
    index: number
    name: string
    counterValue: number
    cost: number
    isEvent: boolean
  }>
  counterPower: number
  pendingTrigger: {
    cardId: string
    cardName: string
    triggerText: string
    playerId: string
  } | null
}

export interface PlaytestState {
  isActive: boolean
  isConnected: boolean
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
  error: string | null
}

// Convert backend card to frontend card
function convertCard(card: BackendCard, index: number): PlaytestCard {
  return {
    instanceId: `${card.id}-${index}-${Date.now()}`,
    id: card.id,
    name: card.name,
    cardType: card.card_type,
    cost: card.cost,
    baseCost: card.base_cost ?? card.cost,
    power: card.power,
    basePower: card.base_power ?? card.power,
    counter: card.counter,
    effect: card.effect,
    trigger: card.trigger,
    attribute: card.attribute,
    imageUrl: card.image_url || card.image_link,  // Backend sends image_link
    isResting: card.is_resting,
    attachedDon: card.attached_don,
    hasAttacked: card.has_attacked,
    canAttackActive: card.can_attack_active ?? false,
  }
}

// Convert backend player to frontend player
function convertPlayer(player: BackendPlayer): PlaytestPlayer {
  return {
    name: player.name,
    leader: player.leader ? convertCard(player.leader, 0) : null,
    lifeCards: Array(player.life_count).fill(null).map((_, i) => ({
      instanceId: `life-${i}`,
      id: 'hidden',
      name: 'Life Card',
      cardType: 'HIDDEN',
      cost: null,
      baseCost: null,
      power: null,
      basePower: null,
      counter: null,
      effect: null,
      trigger: null,
      attribute: null,
      imageUrl: null,
      isResting: false,
      attachedDon: 0,
      hasAttacked: false,
      canAttackActive: false,
    })),
    hand: player.hand.map((c, i) => convertCard(c, i)),
    deck: Array(player.deck_count).fill(null).map((_, i) => ({
      instanceId: `deck-${i}`,
      id: 'hidden',
      name: 'Card',
      cardType: 'HIDDEN',
      cost: null,
      baseCost: null,
      power: null,
      basePower: null,
      counter: null,
      effect: null,
      trigger: null,
      attribute: null,
      imageUrl: null,
      isResting: false,
      attachedDon: 0,
      hasAttacked: false,
      canAttackActive: false,
    })),
    field: player.field.map((c, i) => convertCard(c, i)),
    trash: (player.trash || []).map((c, i) => convertCard(c, i)),
    donActive: player.don_active,
    donRested: player.don_total - player.don_active,
    donDeck: Math.max(0, 10 - player.don_total),
    donPool: player.don_pool || [],
  }
}

// Initial empty state
function createEmptyPlayer(name: string): PlaytestPlayer {
  return {
    name,
    leader: null,
    lifeCards: [],
    hand: [],
    deck: [],
    field: [],
    trash: [],
    donActive: 0,
    donRested: 0,
    donDeck: 10,
    donPool: [],
  }
}

const initialState: PlaytestState = {
  isActive: false,
  isConnected: false,
  gameId: null,
  turn: 0,
  activePlayer: 0,
  phase: 'WAITING',
  player1: createEmptyPlayer('Player 1'),
  player2: createEmptyPlayer('Player 2'),
  logs: [],
  gameOver: false,
  winner: null,
  awaitingResponse: null,
  pendingAttack: null,
  pendingChoice: null,
  error: null,
}

export function usePlaytestSocket() {
  const [state, setState] = useState<PlaytestState>(initialState)
  const socketRef = useRef<Socket | null>(null)
  const logsRef = useRef<string[]>([])

  // Connect to socket
  useEffect(() => {
    const socket = io(SOCKET_URL, {
      path: '/socket.io',
      transports: ['websocket', 'polling'],
      autoConnect: true,
    })

    socket.on('connect', () => {
      console.log('Playtest socket connected:', socket.id)
      setState(prev => ({ ...prev, isConnected: true }))
    })

    socket.on('disconnect', () => {
      console.log('Playtest socket disconnected')
      // Clear pending state on disconnect to prevent stale modals
      setState(prev => ({ ...prev, isConnected: false, pendingChoice: null, pendingAttack: null }))
    })

    socket.on('connect_error', (error) => {
      console.error('Playtest socket error:', error)
      setState(prev => ({ ...prev, error: 'Connection failed', isConnected: false }))
    })

    // Game started event
    socket.on('game_started', (data: { game_id: string; player_index: number; game_state: BackendGameState }) => {
      console.log('Game started:', data)
      const gs = data.game_state
      logsRef.current = ['Game started!']
      setState(prev => ({
        ...prev,
        isActive: true,
        gameId: data.game_id,
        turn: gs.turn,
        activePlayer: gs.active_player as 0 | 1,
        phase: gs.phase,
        player1: convertPlayer(gs.players[0]),
        player2: convertPlayer(gs.players[1]),
        logs: logsRef.current,
        gameOver: false,
        winner: null,
        error: null,
        // Clear any stale pending state from previous games
        pendingChoice: null,
        pendingAttack: null,
        awaitingResponse: null,
      }))
    })

    // Game state update event
    socket.on('game_update', (data: { game_state: BackendGameState; logs: string[] }) => {
      console.log('Game update:', data)
      const gs = data.game_state

      // Append new logs
      if (data.logs) {
        logsRef.current = [...logsRef.current, ...data.logs]
      }

      setState(prev => ({
        ...prev,
        turn: gs.turn,
        activePlayer: gs.active_player as 0 | 1,
        phase: gs.phase,
        player1: convertPlayer(gs.players[0]),
        player2: convertPlayer(gs.players[1]),
        logs: logsRef.current,
        awaitingResponse: gs.awaiting_response,
        pendingAttack: gs.pending_attack ? {
          attackerName: gs.pending_attack.attacker_name,
          attackerPower: gs.pending_attack.attacker_power,
          attackerIndex: gs.pending_attack.attacker_index,
          targetName: gs.pending_attack.target_name,
          targetPower: gs.pending_attack.target_power,
          targetIndex: gs.pending_attack.target_index,
          isLeader: gs.pending_attack.is_leader,
          leaderHasEffect: gs.pending_attack.leader_has_effect ?? false,
          availableBlockers: gs.pending_attack.available_blockers || [],
          availableCounters: (gs.pending_attack.available_counters || []).map(c => ({
            index: c.index,
            name: c.name,
            counterValue: c.counter_value,
            cost: c.cost,
            isEvent: c.is_event,
          })),
          counterPower: gs.pending_attack.counter_power,
          pendingTrigger: gs.pending_attack.pending_trigger ? {
            cardId: gs.pending_attack.pending_trigger.card_id,
            cardName: gs.pending_attack.pending_trigger.card_name,
            triggerText: gs.pending_attack.pending_trigger.trigger_text,
            playerId: gs.pending_attack.pending_trigger.player_id,
          } : null,
        } : null,
        pendingChoice: gs.pending_choice ? {
          choiceId: gs.pending_choice.choice_id,
          choiceType: gs.pending_choice.choice_type,
          prompt: gs.pending_choice.prompt,
          options: gs.pending_choice.options.map(opt => ({
            id: opt.id,
            label: opt.label,
            cardId: opt.card_id,
            cardName: opt.card_name,
          })),
          minSelections: gs.pending_choice.min_selections,
          maxSelections: gs.pending_choice.max_selections,
          sourceCardId: gs.pending_choice.source_card_id,
          sourceCardName: gs.pending_choice.source_card_name,
        } : null,
      }))
    })

    // Game over event
    socket.on('game_over', (data: { winner: number; reason: string; winner_name?: string }) => {
      console.log('Game over:', data)
      logsRef.current = [...logsRef.current, `Game over! ${data.winner_name || `Player ${data.winner + 1}`} wins!`]
      setState(prev => ({
        ...prev,
        gameOver: true,
        winner: data.winner as 0 | 1,
        logs: logsRef.current,
      }))
    })

    // Error event
    socket.on('error', (data: { message: string }) => {
      console.error('Game error:', data.message)
      logsRef.current = [...logsRef.current, `Error: ${data.message}`]
      setState(prev => ({
        ...prev,
        error: data.message,
        logs: logsRef.current,
        // Clear pending choice on error to dismiss stale modals
        pendingChoice: null,
      }))
    })

    socketRef.current = socket

    return () => {
      socket.disconnect()
      socketRef.current = null
    }
  }, [])

  // Start a pre-configured test game for a specific card
  const startTestGame = useCallback((cardId: string) => {
    if (!socketRef.current?.connected) {
      setState(prev => ({ ...prev, error: 'Not connected to server' }))
      return
    }
    logsRef.current = []
    setState(prev => ({ ...prev, isActive: false, gameId: null, pendingChoice: null, pendingAttack: null }))
    socketRef.current.emit('start_test_game', { card_id: cardId })
  }, [])

  // Start a new playtest game
  const startGame = useCallback((
    playerName: string = 'Player',
    deckId: string = 'red_luffy',
    deckData?: { leader: string; cards: Record<string, number> }
  ) => {
    if (!socketRef.current?.connected) {
      setState(prev => ({ ...prev, error: 'Not connected to server' }))
      return
    }

    logsRef.current = []
    socketRef.current.emit('start_playtest', {
      player_name: playerName,
      deck_id: deckId,
      deck_data: deckData,  // Send actual deck data if available
    })
  }, [])

  // Play a card from hand
  const playCard = useCallback((cardIndex: number) => {
    if (!socketRef.current?.connected) return
    socketRef.current.emit('play_card', { card_index: cardIndex })
  }, [])

  // Attach DON to a card
  const attachDon = useCallback((cardIndex: number, amount: number = 1) => {
    if (!socketRef.current?.connected) return
    socketRef.current.emit('attach_don', { card_index: cardIndex, amount })
  }, [])

  // Declare an attack
  const declareAttack = useCallback((attackerIndex: number, targetIndex: number) => {
    if (!socketRef.current?.connected) return
    socketRef.current.emit('attack', { attacker_index: attackerIndex, target_index: targetIndex })
  }, [])

  // Respond to trigger prompt (activate or decline)
  const triggerResponse = useCallback((activate: boolean) => {
    if (!socketRef.current?.connected) return
    socketRef.current.emit('trigger_response', { activate })
  }, [])

  // Respond to leader effect step
  const leaderEffectResponse = useCallback((useEffect: boolean) => {
    if (!socketRef.current?.connected) return
    socketRef.current.emit('leader_effect_response', { use_effect: useEffect })
  }, [])

  // Respond with blocker
  const blockerResponse = useCallback((blockerIndex: number | null) => {
    if (!socketRef.current?.connected) return
    socketRef.current.emit('blocker_response', { blocker_index: blockerIndex })
  }, [])

  // Use counter cards
  const counterResponse = useCallback((counterIndices: number[]) => {
    if (!socketRef.current?.connected) return
    socketRef.current.emit('counter_response', { counter_indices: counterIndices })
  }, [])

  // Activate a card's [Activate: Main] effect
  const activateEffect = useCallback((cardIndex: number) => {
    if (!socketRef.current?.connected) return
    socketRef.current.emit('activate_effect', { card_index: cardIndex })
  }, [])

  // End turn
  const endTurn = useCallback(() => {
    if (!socketRef.current?.connected) return
    socketRef.current.emit('end_turn', {})
  }, [])

  // Surrender
  const surrender = useCallback(() => {
    if (!socketRef.current?.connected) return
    socketRef.current.emit('surrender', {})
  }, [])

  // Submit effect choice response
  const submitEffectChoice = useCallback((choiceId: string, selected: string[]) => {
    if (!socketRef.current?.connected) return
    socketRef.current.emit('effect_choice_response', {
      choice_id: choiceId,
      selected: selected,
    })
  }, [])

  // Simulate a KO on one of P1's field cards (for testing On K.O. effects)
  const simulateKo = useCallback((cardIndex: number) => {
    if (!socketRef.current?.connected) return
    socketRef.current.emit('simulate_ko', { card_index: cardIndex })
  }, [])

  // Debug: mutate game state for effect testing
  const debugSetScenario = useCallback((scenario: {
    playerIndex?: number
    life?: number
    opponentLife?: number
    donActive?: number
    addToHand?: string[]
    addToField?: string[]
    addToOppField?: string[]
    clearHand?: boolean
    clearField?: boolean
    clearOppField?: boolean
  }) => {
    if (!socketRef.current?.connected) return
    socketRef.current.emit('debug_scenario', {
      player_index: scenario.playerIndex ?? 0,
      life: scenario.life,
      opponent_life: scenario.opponentLife,
      don_active: scenario.donActive,
      add_to_hand: scenario.addToHand,
      add_to_field: scenario.addToField,
      add_to_opp_field: scenario.addToOppField,
      clear_hand: scenario.clearHand,
      clear_field: scenario.clearField,
      clear_opp_field: scenario.clearOppField,
    })
  }, [])

  // Reset game (disconnect and reconnect)
  const resetGame = useCallback(() => {
    logsRef.current = []
    setState(initialState)
  }, [])

  return {
    // State
    ...state,

    // Actions
    startTestGame,
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
    surrender,
    submitEffectChoice,
    simulateKo,
    debugSetScenario,
    resetGame,
  }
}
