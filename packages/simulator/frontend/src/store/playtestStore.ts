import { create } from 'zustand'

// Constants from Vinsmoke Engine
const MAX_DON = 10
const HAND_LIMIT = 7
const FIELD_LIMIT = 5

export interface PlaytestCard {
  id: string
  instanceId: string
  name: string
  cost: number | null
  power: number | null
  counter: number | null
  colors: string[]
  type: string
  imageUrl: string | null
  effect: string | null
  trigger: string | null
  isResting: boolean
  hasAttacked: boolean
  attachedDon: number
  playedTurn: number | null  // Track when card was played for summoning sickness
}

// Combat state tracking (from Vinsmoke Engine's CombatState)
export interface CombatState {
  phase: 'declare' | 'blocker' | 'counter' | 'damage' | null
  attacker: PlaytestCard
  attackerZone: 'leader' | 'field'
  attackerIndex: number
  attackerPlayer: 0 | 1
  attackerPower: number  // Base power + DON bonus

  originalTarget: PlaytestCard
  originalTargetZone: 'leader' | 'field'
  originalTargetIndex: number

  currentTarget: PlaytestCard  // May change if blocker activates
  currentTargetZone: 'leader' | 'field'
  currentTargetIndex: number
  defenderPlayer: 0 | 1

  basePower: number  // Defender base power
  counterBonus: number  // From counter cards
  totalDefense: number  // basePower + counterBonus

  blockerActivated: boolean
  blockerCard: PlaytestCard | null

  countersUsed: PlaytestCard[]
  availableBlockers: { index: number, card: PlaytestCard }[]
  availableCounters: { index: number, card: PlaytestCard, value: number }[]
}

// Helper functions to parse keywords from effect text
const hasKeyword = (card: PlaytestCard, keyword: string): boolean => {
  const effect = card.effect || ''
  return effect.includes(`[${keyword}]`)
}

const hasRush = (card: PlaytestCard): boolean => hasKeyword(card, 'Rush')
const hasBlocker = (card: PlaytestCard): boolean => hasKeyword(card, 'Blocker')
const hasBanish = (card: PlaytestCard): boolean => hasKeyword(card, 'Banish')
const hasDoubleAttack = (card: PlaytestCard): boolean => hasKeyword(card, 'Double Attack')

// Check if card has an [On Play] effect
const hasOnPlayEffect = (card: PlaytestCard): boolean => {
  const effect = card.effect || ''
  return effect.includes('[On Play]')
}

// Parse [On Play] effect to determine its type
interface OnPlayEffectInfo {
  type: 'draw_trash' | 'look_top' | 'search' | 'unknown'
  drawCount?: number
  trashCount?: number
  lookCount?: number
  condition?: string
  filterType?: string
}

const parseOnPlayEffect = (effect: string): OnPlayEffectInfo => {
  // Pattern for "draw X cards and trash Y card(s)"
  const drawTrashMatch = effect.match(/draw (\d+) cards? and trash (\d+) cards?/i)
  if (drawTrashMatch) {
    // Check for life condition
    const lifeCondition = effect.match(/(\d+) or less Life/i)
    return {
      type: 'draw_trash',
      drawCount: parseInt(drawTrashMatch[1]),
      trashCount: parseInt(drawTrashMatch[2]),
      condition: lifeCondition ? `life_lte_${lifeCondition[1]}` : undefined
    }
  }

  // Pattern for "Look at X cards from the top of your deck"
  const lookMatch = effect.match(/[Ll]ook at (\d+) cards? from the top of your deck/i)
  if (lookMatch) {
    // Check for type filter (e.g., "Whitebeard Pirates")
    const typeMatch = effect.match(/type including ['"]?([^'"]+)['"]?/i)
    return {
      type: 'look_top',
      lookCount: parseInt(lookMatch[1]),
      filterType: typeMatch ? typeMatch[1] : undefined
    }
  }

  // Pattern for search deck
  if (effect.toLowerCase().includes('search') || effect.toLowerCase().includes('reveal')) {
    const lookCount = effect.match(/(\d+) cards?/i)
    return {
      type: 'search',
      lookCount: lookCount ? parseInt(lookCount[1]) : 5
    }
  }

  return { type: 'unknown' }
}

// Get counter value from a character card
const getCounterValue = (card: PlaytestCard): number => {
  if (card.type !== 'CHARACTER') return 0
  return card.counter || 0
}

export interface PlaytestPlayer {
  name: string
  leader: PlaytestCard | null
  hand: PlaytestCard[]
  deck: PlaytestCard[]
  field: PlaytestCard[]
  trash: PlaytestCard[]
  lifeCards: PlaytestCard[]
  donDeck: number  // DON cards remaining in DON deck
  donActive: number  // DON on field (active)
  donRested: number  // DON on field (rested)
}

// Effect resolution state
export interface EffectResolutionState {
  isActive: boolean
  player: 0 | 1
  effectType: 'look_top' | 'search_deck' | 'select_from_revealed' | null
  revealedCards: PlaytestCard[]
  selectionCount: number  // How many cards can be selected
  selectionFilter?: (card: PlaytestCard) => boolean  // Filter for valid selections
  filterDescription?: string  // e.g., "cost 3 or higher"
  onComplete: 'to_hand' | 'to_field' | 'to_trash' | 'to_bottom_deck'
}

interface PlaytestState {
  isActive: boolean
  turn: number
  activePlayer: 0 | 1  // Which player's turn
  phase: 'setup' | 'refresh' | 'draw' | 'don' | 'main' | 'end'
  isFirstTurn: boolean  // Track if this is the very first turn (P1's first turn - no draw)
  player1: PlaytestPlayer
  player2: PlaytestPlayer
  logs: string[]
  selectedCard: { player: 0 | 1, zone: string, index: number } | null
  effectResolution: EffectResolutionState | null
  combat: CombatState | null  // Current combat in progress
  gameOver: boolean
  winner: 0 | 1 | null
  handLimitPending: { player: 0 | 1, excessCount: number } | null  // Pending hand limit discard
}

interface PlaytestStore extends PlaytestState {
  // Setup
  initGame: (deck: { leaderId: string, cards: { cardId: string, count: number }[] }, cardDatabase: Map<string, any>) => void

  // Game actions
  drawCard: (player: 0 | 1) => void
  drawDon: (player: 0 | 1, amount?: number) => void
  playCard: (player: 0 | 1, handIndex: number) => void
  attachDon: (player: 0 | 1, targetZone: 'leader' | 'field', targetIndex?: number) => void
  restCard: (player: 0 | 1, zone: 'leader' | 'field', index?: number) => void
  activateCard: (player: 0 | 1, zone: 'leader' | 'field', index?: number) => void
  sendToTrash: (player: 0 | 1, zone: string, index: number) => void
  shuffleDeck: (player: 0 | 1) => void
  returnToHand: (player: 0 | 1, zone: string, index: number) => void
  takeDamage: (player: 0 | 1) => void
  endTurn: () => void

  // Effect resolution
  lookAtTopCards: (player: 0 | 1, count: number, filter?: { minCost?: number, maxCost?: number, type?: string }, filterDesc?: string) => void
  searchDeck: (player: 0 | 1, filter?: { minCost?: number, maxCost?: number, type?: string }, filterDesc?: string) => void
  selectFromRevealed: (indices: number[]) => void
  cancelEffectResolution: () => void

  // Combat actions (from Vinsmoke Engine)
  declareAttack: (attackerZone: 'leader' | 'field', attackerIndex: number, targetZone: 'leader' | 'field', targetIndex: number) => void
  activateBlocker: (blockerIndex: number) => void
  skipBlock: () => void
  useCounter: (handIndices: number[]) => void
  skipCounter: () => void
  resolveDamage: () => void
  cancelCombat: () => void

  // Hand limit enforcement
  discardForHandLimit: (handIndices: number[]) => void

  // Selection
  selectCard: (player: 0 | 1, zone: string, index: number) => void
  clearSelection: () => void

  // Utils
  addLog: (message: string) => void
  resetGame: () => void

  // Getters for UI
  canAttack: (attackerZone: 'leader' | 'field', attackerIndex: number) => { canAttack: boolean, reason?: string }
  getValidTargets: () => { zone: 'leader' | 'field', index: number, card: PlaytestCard }[]
}

const createEmptyPlayer = (name: string): PlaytestPlayer => ({
  name,
  leader: null,
  hand: [],
  deck: [],
  field: [],
  trash: [],
  lifeCards: [],
  donDeck: 10,
  donActive: 0,
  donRested: 0,
})

const shuffleArray = <T,>(array: T[]): T[] => {
  const shuffled = [...array]
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]]
  }
  return shuffled
}

let instanceCounter = 0
const createCardInstance = (cardData: any): PlaytestCard => ({
  id: cardData.id,
  instanceId: `${cardData.id}-${++instanceCounter}`,
  name: cardData.name,
  cost: cardData.cost ?? null,
  power: cardData.power ?? null,
  counter: cardData.counter ?? null,
  colors: cardData.colors || [],
  type: cardData.type || 'CHARACTER',
  imageUrl: cardData.imageUrl || cardData.image_link || null,
  effect: cardData.effect || null,
  trigger: cardData.trigger || null,
  isResting: false,
  hasAttacked: false,
  attachedDon: 0,
  playedTurn: null,
})

const initialState: PlaytestState = {
  isActive: false,
  turn: 0,
  activePlayer: 0,
  phase: 'setup',
  isFirstTurn: true,
  player1: createEmptyPlayer('Player 1'),
  player2: createEmptyPlayer('Player 2'),
  logs: [],
  selectedCard: null,
  effectResolution: null,
  combat: null,
  gameOver: false,
  winner: null,
  handLimitPending: null,
}

export const usePlaytestStore = create<PlaytestStore>((set, get) => ({
  ...initialState,

  initGame: (deck, cardDatabase) => {
    instanceCounter = 0

    // Get leader card
    const leaderData = cardDatabase.get(deck.leaderId)
    if (!leaderData) {
      console.error('Leader not found:', deck.leaderId)
      return
    }

    // Build deck array with all cards
    const deckCards: PlaytestCard[] = []
    deck.cards.forEach(({ cardId, count }) => {
      const cardData = cardDatabase.get(cardId)
      if (cardData) {
        for (let i = 0; i < count; i++) {
          deckCards.push(createCardInstance(cardData))
        }
      }
    })

    // Shuffle deck
    const shuffledDeck1 = shuffleArray([...deckCards])
    const shuffledDeck2 = shuffleArray(deckCards.map(c => createCardInstance(cardDatabase.get(c.id))))

    // Draw initial hands (5 cards each)
    const hand1 = shuffledDeck1.splice(0, 5)
    const hand2 = shuffledDeck2.splice(0, 5)

    // Set life cards (leader's life value, default 5 if not specified)
    const lifeCount = leaderData.life || 5
    const life1 = shuffledDeck1.splice(0, lifeCount)
    const life2 = shuffledDeck2.splice(0, lifeCount)

    const leader1 = createCardInstance(leaderData)
    const leader2 = createCardInstance(leaderData)

    // Player 1 starts with 1 DON on their first turn (no card draw)
    set({
      isActive: true,
      turn: 1,
      activePlayer: 0,
      phase: 'main',
      isFirstTurn: true,
      player1: {
        name: 'Player 1',
        leader: leader1,
        hand: hand1,
        deck: shuffledDeck1,
        field: [],
        trash: [],
        lifeCards: life1,
        donDeck: 9,  // Started with 10, drew 1
        donActive: 1,  // First turn: 1 DON only
        donRested: 0,
      },
      player2: {
        name: 'Player 2',
        leader: leader2,
        hand: hand2,
        deck: shuffledDeck2,
        field: [],
        trash: [],
        lifeCards: life2,
        donDeck: 10,
        donActive: 0,
        donRested: 0,
      },
      logs: [
        'Game started!',
        'Both players draw 5 cards.',
        'Player 1 goes first.',
        'Turn 1 - Player 1 draws 1 DON (no card draw on first turn).',
      ],
      selectedCard: null,
    })
  },

  drawCard: (player) => {
    set(state => {
      const playerKey = player === 0 ? 'player1' : 'player2'
      const p = state[playerKey]
      if (p.deck.length === 0) {
        return { logs: [...state.logs, `${p.name} has no cards to draw! DECK OUT - ${p.name} loses!`] }
      }
      const [drawnCard, ...remainingDeck] = p.deck
      return {
        [playerKey]: {
          ...p,
          hand: [...p.hand, drawnCard],
          deck: remainingDeck,
        },
        logs: [...state.logs, `${p.name} drew a card.`],
      }
    })
  },

  drawDon: (player, amount = 1) => {
    set(state => {
      const playerKey = player === 0 ? 'player1' : 'player2'
      const p = state[playerKey]
      const actualAmount = Math.min(amount, p.donDeck)
      if (actualAmount === 0) return state
      return {
        [playerKey]: {
          ...p,
          donDeck: p.donDeck - actualAmount,
          donActive: p.donActive + actualAmount,
        },
        logs: [...state.logs, `${p.name} added ${actualAmount} DON.`],
      }
    })
  },

  playCard: (player, handIndex) => {
    const state = get()
    const playerKey = player === 0 ? 'player1' : 'player2'
    const p = state[playerKey]
    if (handIndex < 0 || handIndex >= p.hand.length) return
    const card = p.hand[handIndex]
    const newHand = [...p.hand]
    newHand.splice(handIndex, 1)

    // Pay cost by resting DON
    const cost = card.cost || 0
    if (cost > p.donActive) {
      set({ logs: [...state.logs, `Not enough active DON to play ${card.name}! Need ${cost}, have ${p.donActive}.`] })
      return
    }

    // Check field limit (5 characters max)
    if (card.type === 'CHARACTER' && p.field.length >= FIELD_LIMIT) {
      set({ logs: [...state.logs, `Cannot play ${card.name}: field is full (${FIELD_LIMIT} characters max).`] })
      return
    }

    // Track when card was played for summoning sickness
    const playedCard = { ...card, playedTurn: state.turn }
    const logs = [...state.logs, `${p.name} played ${card.name} (cost ${cost}).`]

    // Check for [On Play] effect
    if (hasOnPlayEffect(card)) {
      const effectInfo = parseOnPlayEffect(card.effect || '')
      logs.push(`  [On Play] effect triggered!`)

      // Handle draw_trash effect (like Otama)
      if (effectInfo.type === 'draw_trash') {
        // Check life condition if present
        let conditionMet = true
        if (effectInfo.condition?.startsWith('life_lte_')) {
          const lifeThreshold = parseInt(effectInfo.condition.split('_')[2])
          conditionMet = p.lifeCards.length <= lifeThreshold
        }

        if (conditionMet) {
          const drawCount = effectInfo.drawCount || 0
          const trashCount = effectInfo.trashCount || 0

          // Draw cards
          const drawnCards: PlaytestCard[] = []
          const remainingDeck = [...p.deck]
          for (let i = 0; i < drawCount && remainingDeck.length > 0; i++) {
            drawnCards.push(remainingDeck.shift()!)
          }

          logs.push(`  Drew ${drawnCards.length} card(s).`)

          // If we need to trash, set up effect resolution
          if (trashCount > 0 && (newHand.length + drawnCards.length) > 0) {
            logs.push(`  Must trash ${trashCount} card(s) from hand.`)

            set({
              [playerKey]: {
                ...p,
                hand: [...newHand, ...drawnCards],
                deck: remainingDeck,
                field: [...p.field, playedCard],
                donActive: p.donActive - cost,
                donRested: p.donRested + cost,
              },
              logs,
              selectedCard: null,
              // Set pending hand discard for the On Play effect
              effectResolution: {
                isActive: true,
                player,
                effectType: 'select_from_revealed',
                revealedCards: [...newHand, ...drawnCards],
                selectionCount: trashCount,
                filterDescription: `Trash ${trashCount} card(s)`,
                onComplete: 'to_trash',
              },
            })
            return
          }

          set({
            [playerKey]: {
              ...p,
              hand: [...newHand, ...drawnCards],
              deck: remainingDeck,
              field: [...p.field, playedCard],
              donActive: p.donActive - cost,
              donRested: p.donRested + cost,
            },
            logs,
            selectedCard: null,
          })
          return
        } else {
          logs.push(`  Condition not met (need ${effectInfo.condition?.replace('life_lte_', '')} or less life).`)
        }
      }

      // Handle look_top effect (like Izo, Garp searchers)
      if (effectInfo.type === 'look_top') {
        const lookCount = effectInfo.lookCount || 5
        const cardsToReveal = p.deck.slice(0, lookCount)
        logs.push(`  Looking at top ${lookCount} cards...`)

        set({
          [playerKey]: {
            ...p,
            hand: newHand,
            field: [...p.field, playedCard],
            donActive: p.donActive - cost,
            donRested: p.donRested + cost,
          },
          logs,
          selectedCard: null,
          effectResolution: {
            isActive: true,
            player,
            effectType: 'look_top',
            revealedCards: cardsToReveal,
            selectionCount: 1,
            filterDescription: effectInfo.filterType ? `Type: ${effectInfo.filterType}` : undefined,
            onComplete: 'to_hand',
          },
        })
        return
      }
    }

    // No On Play effect or effect already handled
    set({
      [playerKey]: {
        ...p,
        hand: newHand,
        field: [...p.field, playedCard],
        donActive: p.donActive - cost,
        donRested: p.donRested + cost,
      },
      logs,
      selectedCard: null,
    })
  },

  attachDon: (player, targetZone, targetIndex = 0) => {
    set(state => {
      const playerKey = player === 0 ? 'player1' : 'player2'
      const p = state[playerKey]
      if (p.donActive === 0) {
        return { logs: [...state.logs, `No active DON to attach!`] }
      }

      if (targetZone === 'leader' && p.leader) {
        return {
          [playerKey]: {
            ...p,
            leader: { ...p.leader, attachedDon: p.leader.attachedDon + 1 },
            donActive: p.donActive - 1,
          },
          logs: [...state.logs, `${p.name} attached 1 DON to ${p.leader.name}. (+1000 power)`],
        }
      } else if (targetZone === 'field' && p.field[targetIndex]) {
        const newField = [...p.field]
        newField[targetIndex] = { ...newField[targetIndex], attachedDon: newField[targetIndex].attachedDon + 1 }
        return {
          [playerKey]: {
            ...p,
            field: newField,
            donActive: p.donActive - 1,
          },
          logs: [...state.logs, `${p.name} attached 1 DON to ${p.field[targetIndex].name}. (+1000 power)`],
        }
      }
      return state
    })
  },

  restCard: (player, zone, index = 0) => {
    set(state => {
      const playerKey = player === 0 ? 'player1' : 'player2'
      const p = state[playerKey]

      if (zone === 'leader' && p.leader) {
        return {
          [playerKey]: {
            ...p,
            leader: { ...p.leader, isResting: true },
          },
          logs: [...state.logs, `${p.name} rested ${p.leader.name}.`],
        }
      } else if (zone === 'field' && p.field[index]) {
        const newField = [...p.field]
        newField[index] = { ...newField[index], isResting: true }
        return {
          [playerKey]: {
            ...p,
            field: newField,
          },
          logs: [...state.logs, `${p.name} rested ${p.field[index].name}.`],
        }
      }
      return state
    })
  },

  activateCard: (player, zone, index = 0) => {
    set(state => {
      const playerKey = player === 0 ? 'player1' : 'player2'
      const p = state[playerKey]

      if (zone === 'leader' && p.leader) {
        return {
          [playerKey]: {
            ...p,
            leader: { ...p.leader, isResting: false },
          },
          logs: [...state.logs, `${p.name} activated ${p.leader.name}.`],
        }
      } else if (zone === 'field' && p.field[index]) {
        const newField = [...p.field]
        newField[index] = { ...newField[index], isResting: false }
        return {
          [playerKey]: {
            ...p,
            field: newField,
          },
          logs: [...state.logs, `${p.name} activated ${p.field[index].name}.`],
        }
      }
      return state
    })
  },

  sendToTrash: (player, zone, index) => {
    set(state => {
      const playerKey = player === 0 ? 'player1' : 'player2'
      const p = state[playerKey]

      if (zone === 'hand') {
        const card = p.hand[index]
        if (!card) return state
        const newHand = [...p.hand]
        newHand.splice(index, 1)
        return {
          [playerKey]: {
            ...p,
            hand: newHand,
            trash: [...p.trash, card],
          },
          logs: [...state.logs, `${p.name} discarded ${card.name}.`],
          selectedCard: null,
        }
      } else if (zone === 'field') {
        const card = p.field[index]
        if (!card) return state
        const newField = [...p.field]
        newField.splice(index, 1)
        // Return attached DON to active pool
        return {
          [playerKey]: {
            ...p,
            field: newField,
            trash: [...p.trash, { ...card, attachedDon: 0 }],
            donActive: p.donActive + card.attachedDon,
          },
          logs: [...state.logs, `${p.name} sent ${card.name} to trash.`],
          selectedCard: null,
        }
      }
      return state
    })
  },

  shuffleDeck: (player) => {
    set(state => {
      const playerKey = player === 0 ? 'player1' : 'player2'
      const p = state[playerKey]
      return {
        [playerKey]: {
          ...p,
          deck: shuffleArray(p.deck),
        },
        logs: [...state.logs, `${p.name} shuffled their deck.`],
      }
    })
  },

  returnToHand: (player, zone, index) => {
    set(state => {
      const playerKey = player === 0 ? 'player1' : 'player2'
      const p = state[playerKey]

      if (zone === 'field') {
        const card = p.field[index]
        if (!card) return state
        const newField = [...p.field]
        newField.splice(index, 1)
        // Remove attached DON back to active
        return {
          [playerKey]: {
            ...p,
            field: newField,
            hand: [...p.hand, { ...card, attachedDon: 0, isResting: false }],
            donActive: p.donActive + card.attachedDon,
          },
          logs: [...state.logs, `${p.name} returned ${card.name} to hand.`],
          selectedCard: null,
        }
      } else if (zone === 'trash') {
        const card = p.trash[index]
        if (!card) return state
        const newTrash = [...p.trash]
        newTrash.splice(index, 1)
        return {
          [playerKey]: {
            ...p,
            trash: newTrash,
            hand: [...p.hand, card],
          },
          logs: [...state.logs, `${p.name} returned ${card.name} from trash to hand.`],
          selectedCard: null,
        }
      }
      return state
    })
  },

  takeDamage: (player) => {
    set(state => {
      const playerKey = player === 0 ? 'player1' : 'player2'
      const p = state[playerKey]
      if (p.lifeCards.length === 0) {
        return { logs: [...state.logs, `${p.name} has no life cards left - GAME OVER! ${p.name} loses!`] }
      }
      const [lifeCard, ...remainingLife] = p.lifeCards
      return {
        [playerKey]: {
          ...p,
          lifeCards: remainingLife,
          hand: [...p.hand, lifeCard],
        },
        logs: [...state.logs, `${p.name} took damage! (Life: ${remainingLife.length}) Added life card to hand.`],
      }
    })
  },

  endTurn: () => {
    const state = get()

    // Check hand limit before ending turn (7 cards max per Vinsmoke Engine rules)
    const currentPlayerKey = state.activePlayer === 0 ? 'player1' : 'player2'
    const currentP = state[currentPlayerKey]

    if (currentP.hand.length > HAND_LIMIT) {
      const excessCount = currentP.hand.length - HAND_LIMIT
      set({
        handLimitPending: { player: state.activePlayer, excessCount },
        logs: [...state.logs, `${currentP.name} has ${currentP.hand.length} cards in hand. Must discard ${excessCount} card(s) to meet hand limit of ${HAND_LIMIT}.`],
      })
      return // Cannot end turn until hand limit is met
    }

    const nextPlayer = state.activePlayer === 0 ? 1 : 0
    const nextPlayerKey = nextPlayer === 0 ? 'player1' : 'player2'
    const nextP = state[nextPlayerKey]

    // Calculate total DON to return (rested + attached to cards)
    const leaderDon = currentP.leader?.attachedDon || 0
    const fieldDon = currentP.field.reduce((sum, c) => sum + c.attachedDon, 0)
    const totalDonReturned = currentP.donRested + leaderDon + fieldDon + currentP.donActive

    // Reset current player's cards (remove attached DON)
    const currentNewField = currentP.field.map(c => ({ ...c, attachedDon: 0 }))
    const currentNewLeader = currentP.leader ? { ...currentP.leader, attachedDon: 0 } : null

    // Next player's turn setup
    // Refresh phase: activate all rested cards, all DON becomes active
    const nextLeaderDon = nextP.leader?.attachedDon || 0
    const nextFieldDon = nextP.field.reduce((sum, c) => sum + c.attachedDon, 0)
    const nextTotalDon = nextP.donActive + nextP.donRested + nextLeaderDon + nextFieldDon

    const nextNewField = nextP.field.map(c => ({ ...c, isResting: false, hasAttacked: false, attachedDon: 0 }))
    const nextNewLeader = nextP.leader ? { ...nextP.leader, isResting: false, attachedDon: 0 } : null

    // DON phase: Draw 2 DON (always 2 after first turn)
    const donToDraw = 2
    const actualDonDraw = Math.min(donToDraw, nextP.donDeck)

    // Update turn number (increments when going back to Player 1)
    const newTurn = nextPlayer === 0 ? state.turn + 1 : state.turn

    const logs = [
      ...state.logs,
      `--- ${currentP.name} ends turn ---`,
      `--- Turn ${newTurn} - ${nextP.name}'s turn ---`,
      `Refresh: All ${nextP.name}'s cards activated, DON returned to active.`,
      `DON Phase: ${nextP.name} draws ${actualDonDraw} DON.`,
    ]

    set({
      [currentPlayerKey]: {
        ...currentP,
        leader: currentNewLeader,
        field: currentNewField,
        donActive: totalDonReturned,
        donRested: 0,
      },
      [nextPlayerKey]: {
        ...nextP,
        leader: nextNewLeader,
        field: nextNewField,
        donDeck: nextP.donDeck - actualDonDraw,
        donActive: nextTotalDon + actualDonDraw,
        donRested: 0,
      },
      activePlayer: nextPlayer as 0 | 1,
      turn: newTurn,
      isFirstTurn: false,
      logs,
      selectedCard: null,
    })

    // Draw phase: Draw 1 card (happens after the first turn)
    get().drawCard(nextPlayer as 0 | 1)
  },

  selectCard: (player, zone, index) => {
    set({ selectedCard: { player, zone, index } })
  },

  clearSelection: () => {
    set({ selectedCard: null })
  },

  // Effect resolution actions
  lookAtTopCards: (player, count, filter, filterDesc) => {
    set(state => {
      const playerKey = player === 0 ? 'player1' : 'player2'
      const p = state[playerKey]
      const cardsToReveal = p.deck.slice(0, count)

      // Create filter function based on filter params
      let filterFn: ((card: PlaytestCard) => boolean) | undefined
      if (filter) {
        filterFn = (card: PlaytestCard) => {
          if (filter.minCost !== undefined && (card.cost === null || card.cost < filter.minCost)) return false
          if (filter.maxCost !== undefined && (card.cost === null || card.cost > filter.maxCost)) return false
          if (filter.type && card.type !== filter.type) return false
          return true
        }
      }

      return {
        effectResolution: {
          isActive: true,
          player,
          effectType: 'look_top',
          revealedCards: cardsToReveal,
          selectionCount: 1,
          selectionFilter: filterFn,
          filterDescription: filterDesc,
          onComplete: 'to_hand',
        },
        logs: [...state.logs, `${p.name} looks at top ${count} cards of deck.`],
      }
    })
  },

  searchDeck: (player, filter, filterDesc) => {
    set(state => {
      const playerKey = player === 0 ? 'player1' : 'player2'
      const p = state[playerKey]

      // Create filter function
      let filterFn: ((card: PlaytestCard) => boolean) | undefined
      if (filter) {
        filterFn = (card: PlaytestCard) => {
          if (filter.minCost !== undefined && (card.cost === null || card.cost < filter.minCost)) return false
          if (filter.maxCost !== undefined && (card.cost === null || card.cost > filter.maxCost)) return false
          if (filter.type && card.type !== filter.type) return false
          return true
        }
      }

      return {
        effectResolution: {
          isActive: true,
          player,
          effectType: 'search_deck',
          revealedCards: [...p.deck],
          selectionCount: 1,
          selectionFilter: filterFn,
          filterDescription: filterDesc,
          onComplete: 'to_hand',
        },
        logs: [...state.logs, `${p.name} searches their deck.`],
      }
    })
  },

  selectFromRevealed: (indices) => {
    set(state => {
      if (!state.effectResolution) return state

      const { player, effectType, revealedCards, onComplete, selectionCount } = state.effectResolution
      const playerKey = player === 0 ? 'player1' : 'player2'
      const p = state[playerKey]

      // Get selected cards
      const selectedCards = indices.map(i => revealedCards[i]).filter(Boolean)
      if (selectedCards.length === 0 && effectType !== 'select_from_revealed') {
        return {
          effectResolution: null,
          logs: [...state.logs, `${p.name} chose no cards.`],
        }
      }

      const logs = [...state.logs]

      // Handle based on effect type and destination
      let newDeck = [...p.deck]
      let newHand = [...p.hand]
      let newField = [...p.field]
      let newTrash = [...p.trash]

      // Handle "select_from_revealed" (trash from hand - like Otama's effect)
      if (effectType === 'select_from_revealed' && onComplete === 'to_trash') {
        // Check if correct number of cards selected
        if (selectedCards.length !== selectionCount) {
          return {
            logs: [...state.logs, `Must select exactly ${selectionCount} card(s) to trash.`],
          }
        }

        // Remove selected cards from hand and add to trash
        for (const card of selectedCards) {
          const handIndex = newHand.findIndex(c => c.instanceId === card.instanceId)
          if (handIndex !== -1) {
            newHand.splice(handIndex, 1)
            newTrash.push(card)
            logs.push(`${p.name} trashed ${card.name}.`)
          }
        }

        return {
          [playerKey]: {
            ...p,
            hand: newHand,
            trash: newTrash,
          },
          effectResolution: null,
          logs,
        }
      }

      const selectedCard = selectedCards[0]

      if (effectType === 'look_top') {
        // Remove selected card from deck (it's from top cards)
        const cardIndex = newDeck.findIndex(c => c.instanceId === selectedCard.instanceId)
        if (cardIndex !== -1) {
          newDeck.splice(cardIndex, 1)
        }
      } else if (effectType === 'search_deck') {
        // Remove selected card from deck
        const cardIndex = newDeck.findIndex(c => c.instanceId === selectedCard.instanceId)
        if (cardIndex !== -1) {
          newDeck.splice(cardIndex, 1)
        }
        // Shuffle deck after search
        newDeck = shuffleArray(newDeck)
        logs.push(`${p.name} shuffles their deck.`)
      }

      // Add to destination
      if (onComplete === 'to_hand') {
        newHand.push(selectedCard)
        logs.push(`${p.name} added ${selectedCard.name} to hand.`)
      } else if (onComplete === 'to_field') {
        newField.push(selectedCard)
        logs.push(`${p.name} played ${selectedCard.name} to field.`)
      } else if (onComplete === 'to_trash') {
        newTrash.push(selectedCard)
        logs.push(`${p.name} sent ${selectedCard.name} to trash.`)
      }

      return {
        [playerKey]: {
          ...p,
          deck: newDeck,
          hand: newHand,
          field: newField,
          trash: newTrash,
        },
        effectResolution: null,
        logs,
      }
    })
  },

  cancelEffectResolution: () => {
    set(state => {
      if (!state.effectResolution) return state
      const { player, effectType } = state.effectResolution
      const playerKey = player === 0 ? 'player1' : 'player2'
      const p = state[playerKey]

      // If it was a search, shuffle the deck back
      if (effectType === 'search_deck') {
        return {
          [playerKey]: {
            ...p,
            deck: shuffleArray(p.deck),
          },
          effectResolution: null,
          logs: [...state.logs, `${p.name} shuffles their deck.`],
        }
      }

      return {
        effectResolution: null,
        logs: [...state.logs, `Effect cancelled.`],
      }
    })
  },

  // Combat actions (ported from Vinsmoke Engine)
  canAttack: (attackerZone, attackerIndex) => {
    const state = get()
    const activePlayerKey = state.activePlayer === 0 ? 'player1' : 'player2'
    const p = state[activePlayerKey]

    // Get attacker card
    const attacker = attackerZone === 'leader' ? p.leader : p.field[attackerIndex]
    if (!attacker) return { canAttack: false, reason: 'No card found' }

    // Check if already resting
    if (attacker.isResting) {
      return { canAttack: false, reason: `${attacker.name} is resting` }
    }

    // Check if already attacked
    if (attacker.hasAttacked) {
      return { canAttack: false, reason: `${attacker.name} has already attacked this turn` }
    }

    // Attack restrictions based on turn (from Vinsmoke Engine rules)
    // P1 cannot attack until turn 3, P2 cannot attack until turn 4
    if (attackerZone === 'leader') {
      if (state.activePlayer === 0 && state.turn < 3) {
        return { canAttack: false, reason: 'Leader cannot attack until turn 3' }
      }
      if (state.activePlayer === 1 && state.turn < 2) {
        return { canAttack: false, reason: 'Leader cannot attack until turn 2' }
      }
    }

    // Summoning sickness check for characters (unless they have Rush)
    if (attackerZone === 'field') {
      const playedThisTurn = attacker.playedTurn === state.turn
      if (playedThisTurn && !hasRush(attacker)) {
        return { canAttack: false, reason: `${attacker.name} has summoning sickness (cannot attack turn played)` }
      }
    }

    return { canAttack: true }
  },

  getValidTargets: () => {
    const state = get()
    const defenderKey = state.activePlayer === 0 ? 'player2' : 'player1'
    const defender = state[defenderKey]
    const targets: { zone: 'leader' | 'field', index: number, card: PlaytestCard }[] = []

    // Leader is always a valid target
    if (defender.leader) {
      targets.push({ zone: 'leader', index: 0, card: defender.leader })
    }

    // Only rested characters can be attacked (from Vinsmoke Engine rules)
    defender.field.forEach((card, index) => {
      if (card.isResting) {
        targets.push({ zone: 'field', index, card })
      }
    })

    return targets
  },

  declareAttack: (attackerZone, attackerIndex, targetZone, targetIndex) => {
    set(state => {
      if (state.gameOver) return { logs: [...state.logs, 'Game is over!'] }
      if (state.combat) return { logs: [...state.logs, 'Combat already in progress!'] }

      const activePlayerKey = state.activePlayer === 0 ? 'player1' : 'player2'
      const defenderKey = state.activePlayer === 0 ? 'player2' : 'player1'
      const attacker_p = state[activePlayerKey]
      const defender_p = state[defenderKey]

      // Get attacker
      const attacker = attackerZone === 'leader' ? attacker_p.leader : attacker_p.field[attackerIndex]
      if (!attacker) return { logs: [...state.logs, 'Invalid attacker!'] }

      // Validate attack (using canAttack logic)
      const { canAttack, reason } = get().canAttack(attackerZone, attackerIndex)
      if (!canAttack) {
        return { logs: [...state.logs, reason || 'Cannot attack'] }
      }

      // Get target
      const target = targetZone === 'leader' ? defender_p.leader : defender_p.field[targetIndex]
      if (!target) return { logs: [...state.logs, 'Invalid target!'] }

      // Validate target (can only attack rested characters, but leader is always valid)
      if (targetZone === 'field' && !target.isResting) {
        return { logs: [...state.logs, `Cannot attack ${target.name} - only rested characters can be attacked`] }
      }

      // Calculate powers
      // DON is ONLY active for attacker (it's their turn) - from Vinsmoke Engine
      const attackerPower = (attacker.power || 0) + (attacker.attachedDon * 1000)
      // DON is NOT active for defender (it's not their turn)
      const defenderBasePower = target.power || 0

      // Find available blockers (defender's active characters with [Blocker])
      const availableBlockers: { index: number, card: PlaytestCard }[] = []
      defender_p.field.forEach((card, index) => {
        if (hasBlocker(card) && !card.isResting) {
          availableBlockers.push({ index, card })
        }
      })

      // Find available counter cards in defender's hand
      const availableCounters: { index: number, card: PlaytestCard, value: number }[] = []
      defender_p.hand.forEach((card, index) => {
        const counterValue = getCounterValue(card)
        if (counterValue > 0) {
          availableCounters.push({ index, card, value: counterValue })
        }
      })

      const logs = [...state.logs, `${attacker_p.name}'s ${attacker.name} (Power: ${attackerPower}) attacks ${target.name}!`]

      // Create combat state
      const combat: CombatState = {
        phase: availableBlockers.length > 0 ? 'blocker' : 'counter',
        attacker,
        attackerZone,
        attackerIndex,
        attackerPlayer: state.activePlayer,
        attackerPower,
        originalTarget: target,
        originalTargetZone: targetZone,
        originalTargetIndex: targetIndex,
        currentTarget: target,
        currentTargetZone: targetZone,
        currentTargetIndex: targetIndex,
        defenderPlayer: state.activePlayer === 0 ? 1 : 0,
        basePower: defenderBasePower,
        counterBonus: 0,
        totalDefense: defenderBasePower,
        blockerActivated: false,
        blockerCard: null,
        countersUsed: [],
        availableBlockers,
        availableCounters,
      }

      if (availableBlockers.length > 0) {
        logs.push(`[BLOCKER STEP] ${defender_p.name} may activate a blocker.`)
      } else if (availableCounters.length > 0) {
        logs.push(`[COUNTER STEP] ${defender_p.name} may use counter cards.`)
      } else {
        // No blockers or counters - go straight to damage
        combat.phase = 'damage'
        logs.push(`[DAMAGE STEP] Resolving combat...`)
      }

      return { combat, logs }
    })
  },

  activateBlocker: (blockerIndex) => {
    set(state => {
      if (!state.combat || state.combat.phase !== 'blocker') return state

      const defenderKey = state.combat.defenderPlayer === 0 ? 'player1' : 'player2'
      const defender_p = state[defenderKey]

      // Validate blocker
      const blocker = defender_p.field[blockerIndex]
      if (!blocker || !hasBlocker(blocker) || blocker.isResting) {
        return { logs: [...state.logs, 'Invalid blocker!'] }
      }

      // Rest the blocker and redirect attack
      const newField = [...defender_p.field]
      newField[blockerIndex] = { ...blocker, isResting: true }

      // Update combat state
      const newCombat: CombatState = {
        ...state.combat,
        phase: 'counter',
        currentTarget: blocker,
        currentTargetZone: 'field',
        currentTargetIndex: blockerIndex,
        basePower: blocker.power || 0,
        totalDefense: blocker.power || 0,
        blockerActivated: true,
        blockerCard: blocker,
      }

      // Update available counters based on new target
      const availableCounters: { index: number, card: PlaytestCard, value: number }[] = []
      defender_p.hand.forEach((card, index) => {
        const counterValue = getCounterValue(card)
        if (counterValue > 0) {
          availableCounters.push({ index, card, value: counterValue })
        }
      })
      newCombat.availableCounters = availableCounters

      const logs = [
        ...state.logs,
        `${defender_p.name} activates ${blocker.name} as a blocker!`,
        `[COUNTER STEP] ${defender_p.name} may use counter cards.`,
      ]

      return {
        [defenderKey]: { ...defender_p, field: newField },
        combat: newCombat,
        logs,
      }
    })
  },

  skipBlock: () => {
    set(state => {
      if (!state.combat || state.combat.phase !== 'blocker') return state

      const defenderKey = state.combat.defenderPlayer === 0 ? 'player1' : 'player2'
      const defender_p = state[defenderKey]

      // Move to counter step or damage if no counters
      const hasCounters = state.combat.availableCounters.length > 0
      const newPhase = hasCounters ? 'counter' : 'damage'

      const logs = [...state.logs, `${defender_p.name} does not activate a blocker.`]
      if (hasCounters) {
        logs.push(`[COUNTER STEP] ${defender_p.name} may use counter cards.`)
      } else {
        logs.push(`[DAMAGE STEP] Resolving combat...`)
      }

      return {
        combat: { ...state.combat, phase: newPhase },
        logs,
      }
    })
  },

  useCounter: (handIndices) => {
    set(state => {
      if (!state.combat || state.combat.phase !== 'counter') return state

      const defenderKey = state.combat.defenderPlayer === 0 ? 'player1' : 'player2'
      const defender_p = state[defenderKey]

      // Get counter cards and calculate bonus
      let counterBonus = 0
      const countersUsed: PlaytestCard[] = []
      const newHand = [...defender_p.hand]
      const newTrash = [...defender_p.trash]
      const logs = [...state.logs]

      // Process indices in reverse order to avoid shifting issues
      const sortedIndices = [...handIndices].sort((a, b) => b - a)
      for (const idx of sortedIndices) {
        const card = defender_p.hand[idx]
        if (card) {
          const value = getCounterValue(card)
          if (value > 0) {
            counterBonus += value
            countersUsed.push(card)
            logs.push(`[COUNTER] ${defender_p.name} uses ${card.name} (+${value})`)
            newHand.splice(idx, 1)
            newTrash.push(card)
          }
        }
      }

      const totalDefense = state.combat.basePower + state.combat.counterBonus + counterBonus
      logs.push(`[DAMAGE STEP] Resolving combat...`)

      return {
        [defenderKey]: { ...defender_p, hand: newHand, trash: newTrash },
        combat: {
          ...state.combat,
          phase: 'damage',
          counterBonus: state.combat.counterBonus + counterBonus,
          totalDefense,
          countersUsed: [...state.combat.countersUsed, ...countersUsed],
        },
        logs,
      }
    })
  },

  skipCounter: () => {
    set(state => {
      if (!state.combat || state.combat.phase !== 'counter') return state

      const defenderKey = state.combat.defenderPlayer === 0 ? 'player1' : 'player2'
      const defender_p = state[defenderKey]

      return {
        combat: { ...state.combat, phase: 'damage' },
        logs: [
          ...state.logs,
          `${defender_p.name} does not use any counter cards.`,
          `[DAMAGE STEP] Resolving combat...`,
        ],
      }
    })
  },

  resolveDamage: () => {
    set(state => {
      if (!state.combat || state.combat.phase !== 'damage') return state

      const attackerKey = state.combat.attackerPlayer === 0 ? 'player1' : 'player2'
      const defenderKey = state.combat.defenderPlayer === 0 ? 'player1' : 'player2'
      const attacker_p = state[attackerKey]
      const defender_p = state[defenderKey]

      const { attackerPower, currentTarget, currentTargetZone, currentTargetIndex, totalDefense, attacker } = state.combat
      const logs = [...state.logs]

      // Rest the attacker
      let newAttackerLeader = attacker_p.leader
      let newAttackerField = [...attacker_p.field]
      if (state.combat.attackerZone === 'leader' && attacker_p.leader) {
        newAttackerLeader = { ...attacker_p.leader, isResting: true, hasAttacked: true }
      } else {
        newAttackerField[state.combat.attackerIndex] = {
          ...newAttackerField[state.combat.attackerIndex],
          isResting: true,
          hasAttacked: true,
        }
      }

      let newDefenderLeader = defender_p.leader
      let newDefenderField = [...defender_p.field]
      let newDefenderLife = [...defender_p.lifeCards]
      let newDefenderHand = [...defender_p.hand]
      let newDefenderTrash = [...defender_p.trash]
      let gameOver = false
      let winner: 0 | 1 | null = null

      // Compare power - attacker wins on ties (from Vinsmoke Engine rules)
      if (attackerPower >= totalDefense) {
        logs.push(`Attack succeeds! (${attackerPower} vs ${totalDefense})`)

        if (currentTargetZone === 'leader') {
          // Deal life damage
          const attackerHasBanish = hasBanish(attacker)
          const attackerHasDoubleAttack = hasDoubleAttack(attacker)

          // First life damage
          if (newDefenderLife.length === 0) {
            logs.push(`${defender_p.name} has no life cards left - GAME OVER! ${attacker_p.name} wins!`)
            gameOver = true
            winner = state.combat.attackerPlayer
          } else {
            const lifeCard = newDefenderLife.shift()!
            const hasTrigger = !!(lifeCard.trigger && lifeCard.trigger.trim())

            logs.push(`${defender_p.name} loses a life card! (${newDefenderLife.length} remaining)`)

            if (hasTrigger && !attackerHasBanish) {
              logs.push(`  [TRIGGER] ${lifeCard.name}: ${lifeCard.trigger}`)
              // Trigger card goes to trash after use
              newDefenderTrash.push(lifeCard)
              logs.push(`  ${lifeCard.name} sent to trash (trigger used)`)
            } else if (attackerHasBanish) {
              newDefenderTrash.push(lifeCard)
              logs.push(`  ${lifeCard.name} is banished to trash`)
            } else {
              // No trigger - life card goes to hand
              newDefenderHand.push(lifeCard)
              logs.push(`  ${lifeCard.name} added to hand`)
            }

            // Check for loss after first damage
            if (newDefenderLife.length === 0) {
              logs.push(`${defender_p.name} has no life cards left - GAME OVER! ${attacker_p.name} wins!`)
              gameOver = true
              winner = state.combat.attackerPlayer
            }

            // Double Attack - deal second damage
            if (!gameOver && attackerHasDoubleAttack) {
              logs.push(`${attacker.name} has [Double Attack] - dealing additional damage!`)
              if (newDefenderLife.length === 0) {
                logs.push(`${defender_p.name} has no life cards left - GAME OVER! ${attacker_p.name} wins!`)
                gameOver = true
                winner = state.combat.attackerPlayer
              } else {
                const lifeCard2 = newDefenderLife.shift()!
                const hasTrigger2 = !!(lifeCard2.trigger && lifeCard2.trigger.trim())

                logs.push(`${defender_p.name} loses a life card! (${newDefenderLife.length} remaining)`)

                if (hasTrigger2 && !attackerHasBanish) {
                  logs.push(`  [TRIGGER] ${lifeCard2.name}: ${lifeCard2.trigger}`)
                  newDefenderTrash.push(lifeCard2)
                  logs.push(`  ${lifeCard2.name} sent to trash (trigger used)`)
                } else if (attackerHasBanish) {
                  newDefenderTrash.push(lifeCard2)
                  logs.push(`  ${lifeCard2.name} is banished to trash`)
                } else {
                  newDefenderHand.push(lifeCard2)
                  logs.push(`  ${lifeCard2.name} added to hand`)
                }

                if (newDefenderLife.length === 0) {
                  logs.push(`${defender_p.name} has no life cards left - GAME OVER! ${attacker_p.name} wins!`)
                  gameOver = true
                  winner = state.combat.attackerPlayer
                }
              }
            }
          }
        } else {
          // KO character
          const koCard = newDefenderField[currentTargetIndex]
          newDefenderField.splice(currentTargetIndex, 1)
          newDefenderTrash.push({ ...koCard, attachedDon: 0 })
          logs.push(`${attacker.name} KO's ${currentTarget.name}!`)
          // Return attached DON to active
          // Note: Defender's DON stays rested (it's not their turn)
        }
      } else {
        logs.push(`Attack is defended! (${attackerPower} vs ${totalDefense})`)
      }

      return {
        [attackerKey]: {
          ...attacker_p,
          leader: newAttackerLeader,
          field: newAttackerField,
        },
        [defenderKey]: {
          ...defender_p,
          leader: newDefenderLeader,
          field: newDefenderField,
          lifeCards: newDefenderLife,
          hand: newDefenderHand,
          trash: newDefenderTrash,
        },
        combat: null,
        gameOver,
        winner,
        logs,
      }
    })
  },

  cancelCombat: () => {
    set(state => ({
      combat: null,
      logs: [...state.logs, 'Combat cancelled.'],
    }))
  },

  discardForHandLimit: (handIndices) => {
    set(state => {
      if (!state.handLimitPending) return state

      const { player, excessCount } = state.handLimitPending
      const playerKey = player === 0 ? 'player1' : 'player2'
      const p = state[playerKey]

      if (handIndices.length !== excessCount) {
        return { logs: [...state.logs, `Must discard exactly ${excessCount} cards.`] }
      }

      const newHand = [...p.hand]
      const newTrash = [...p.trash]
      const logs = [...state.logs]

      // Sort in reverse order to avoid shifting issues
      const sortedIndices = [...handIndices].sort((a, b) => b - a)
      for (const idx of sortedIndices) {
        const card = newHand[idx]
        if (card) {
          newHand.splice(idx, 1)
          newTrash.push(card)
          logs.push(`${p.name} discards ${card.name} (hand limit).`)
        }
      }

      return {
        [playerKey]: { ...p, hand: newHand, trash: newTrash },
        handLimitPending: null,
        logs,
      }
    })
  },

  addLog: (message) => {
    set(state => ({ logs: [...state.logs, message] }))
  },

  resetGame: () => {
    set(initialState)
  },
}))
