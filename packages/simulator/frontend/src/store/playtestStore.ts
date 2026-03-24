import { create } from 'zustand'

// Constants from Vinsmoke Engine
const MAX_DON = 10
// Note: One Piece TCG has NO hand limit
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
  traits: string | string[] | null  // Card trait/type like "Navy", "Straw Hat Crew", etc.
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

// Check if card has an [On K.O.] effect
const hasOnKOEffect = (card: PlaytestCard): boolean => {
  const effect = card.effect || ''
  return effect.includes('[On K.O.]')
}

// Check if card has a [When Attacking] effect
const hasWhenAttackingEffect = (card: PlaytestCard): boolean => {
  const effect = card.effect || ''
  return effect.includes('[When Attacking]')
}

// Check DON requirement for effect (e.g., [DON!! x1], [DON!! x2])
const getDonRequirement = (effect: string, timing: string): number => {
  // Look for DON requirement before the timing keyword
  const pattern = new RegExp(`\\[DON!!\\s*x(\\d+)\\]\\s*\\[${timing}\\]`, 'i')
  const match = effect.match(pattern)
  return match ? parseInt(match[1]) : 0
}

// Check if card has an [Activate: Main] effect
const hasActivateMainEffect = (card: PlaytestCard): boolean => {
  const effect = card.effect || ''
  return effect.includes('[Activate: Main]')
}

// Parse [Activate: Main] effect
interface ActivateMainEffectInfo {
  type: 'draw' | 'search' | 'ko_opponent' | 'power_boost' | 'power_reduce' | 'return_to_hand' | 'bottom_deck' | 'play_character' | 'unknown'
  // Costs
  restSelf: boolean
  trashSelf: boolean
  trashFromHand: number
  restDonCount: number
  // Once per turn
  oncePerTurn: boolean
  // Effect params
  drawCount?: number
  lookCount?: number
  powerChange?: number
  costMax?: number
  powerMax?: number
  traitFilter?: string
  condition?: string
}

const parseActivateMainEffect = (effect: string): ActivateMainEffectInfo => {
  // Extract just the [Activate: Main] portion
  const mainMatch = effect.match(/\[Activate: Main\](.*?)(?:<br>|$)/is)
  if (!mainMatch) return { type: 'unknown', restSelf: false, trashSelf: false, trashFromHand: 0, restDonCount: 0, oncePerTurn: false }

  const mainEffect = mainMatch[1]

  // Check for Once Per Turn
  const oncePerTurn = /\[Once Per Turn\]/i.test(mainEffect)

  // Parse costs
  const restSelf = /(?:rest|Rest) this (?:Character|card)/i.test(mainEffect)
  const trashSelf = /(?:trash|Trash) this (?:Character|card)/i.test(mainEffect)

  let trashFromHand = 0
  const trashHandMatch = mainEffect.match(/trash (\d+) cards? from your hand/i)
  if (trashHandMatch) trashFromHand = parseInt(trashHandMatch[1])

  let restDonCount = 0
  const restDonMatch = mainEffect.match(/[➀①]|rest (\d+) (?:of your )?DON/i)
  if (restDonMatch) restDonCount = restDonMatch[1] ? parseInt(restDonMatch[1]) : 1

  // Parse condition (leader type requirement)
  let condition: string | undefined
  const leaderMatch = mainEffect.match(/If your Leader (?:has the |is )\{?([^}]+)\}? type/i)
  if (leaderMatch) condition = `leader_${leaderMatch[1]}`

  // Parse effect type
  // Draw
  const drawMatch = mainEffect.match(/[Dd]raw (\d+) cards?/i)
  if (drawMatch) {
    return {
      type: 'draw',
      restSelf, trashSelf, trashFromHand, restDonCount, oncePerTurn,
      drawCount: parseInt(drawMatch[1]),
      condition
    }
  }

  // Look at deck / Search
  const lookMatch = mainEffect.match(/[Ll]ook at (\d+) cards? from (?:the top of )?your deck/i)
  if (lookMatch) {
    let traitFilter: string | undefined
    const traitMatch = mainEffect.match(/\{([^}]+)\}/)
    if (traitMatch) traitFilter = traitMatch[1]

    return {
      type: 'search',
      restSelf, trashSelf, trashFromHand, restDonCount, oncePerTurn,
      lookCount: parseInt(lookMatch[1]),
      traitFilter,
      condition
    }
  }

  // K.O. opponent's character
  const koMatch = mainEffect.match(/K\.?O\.? (?:up to )?(\d+) (?:of )?your opponent'?s.*Characters? with (?:a )?cost (?:of )?(\d+) or less/i)
  if (koMatch) {
    return {
      type: 'ko_opponent',
      restSelf, trashSelf, trashFromHand, restDonCount, oncePerTurn,
      costMax: parseInt(koMatch[2]),
      condition
    }
  }

  // Power boost self "gains +X000 power"
  const powerBoostMatch = mainEffect.match(/(?:this Character|gains) \+(\d+) power/i)
  if (powerBoostMatch) {
    return {
      type: 'power_boost',
      restSelf, trashSelf, trashFromHand, restDonCount, oncePerTurn,
      powerChange: parseInt(powerBoostMatch[1]),
      condition
    }
  }

  // Power reduce opponent
  const powerReduceMatch = mainEffect.match(/[Gg]ive (?:up to )?(\d+) (?:of )?your opponent'?s Characters? [−\-](\d+)/i)
  if (powerReduceMatch) {
    return {
      type: 'power_reduce',
      restSelf, trashSelf, trashFromHand, restDonCount, oncePerTurn,
      powerChange: -parseInt(powerReduceMatch[2]),
      condition
    }
  }

  // Bottom deck opponent
  const bottomMatch = mainEffect.match(/[Pp]lace (?:up to )?(\d+) (?:of )?(?:your opponent'?s )?Characters? with (?:a )?cost (?:of )?(\d+) or less at the bottom/i)
  if (bottomMatch) {
    return {
      type: 'bottom_deck',
      restSelf, trashSelf, trashFromHand, restDonCount, oncePerTurn,
      costMax: parseInt(bottomMatch[2]),
      condition
    }
  }

  // Play character from hand
  if (/[Pp]lay (?:up to )?\d+ .* Character/i.test(mainEffect)) {
    let traitFilter: string | undefined
    const traitMatch = mainEffect.match(/\{([^}]+)\}/)
    if (traitMatch) traitFilter = traitMatch[1]

    const costMatch = mainEffect.match(/cost (?:of )?(\d+) or less/i)

    return {
      type: 'play_character',
      restSelf, trashSelf, trashFromHand, restDonCount, oncePerTurn,
      costMax: costMatch ? parseInt(costMatch[1]) : undefined,
      traitFilter,
      condition
    }
  }

  return { type: 'unknown', restSelf, trashSelf, trashFromHand, restDonCount, oncePerTurn }
}

// Parse [When Attacking] effect
interface WhenAttackingEffectInfo {
  type: 'draw' | 'draw_trash' | 'ko_opponent' | 'return_to_hand' | 'power_boost' | 'power_reduce' | 'bottom_deck' | 'disable_blocker' | 'give_don' | 'add_don' | 'rest_opponent' | 'unknown'
  donRequirement: number
  drawCount?: number
  trashCount?: number
  powerChange?: number
  costMax?: number
  powerMax?: number
  condition?: string
  targetSelf?: boolean
}

const parseWhenAttackingEffect = (effect: string): WhenAttackingEffectInfo => {
  const donRequirement = getDonRequirement(effect, 'When Attacking')

  // Extract just the [When Attacking] portion
  const attackMatch = effect.match(/\[When Attacking\](.*?)(?:\[|<br>|$)/is)
  if (!attackMatch) return { type: 'unknown', donRequirement }

  const attackEffect = attackMatch[1]

  // Parse condition
  let condition: string | undefined
  const lifeCondition = attackEffect.match(/If you have (\d+) or (?:more|less) Life/i)
  if (lifeCondition) {
    condition = attackEffect.includes('or more') ? `life_gte_${lifeCondition[1]}` : `life_lte_${lifeCondition[1]}`
  }
  const handCondition = attackEffect.match(/if you have (\d+) or less cards in your hand/i)
  if (handCondition) {
    condition = `hand_lte_${handCondition[1]}`
  }

  // Pattern 1: Draw and trash "Draw X card(s) and trash Y card(s)"
  const drawTrashMatch = attackEffect.match(/[Dd]raw (\d+) cards? and trash (\d+) cards?/i)
  if (drawTrashMatch) {
    return {
      type: 'draw_trash',
      donRequirement,
      drawCount: parseInt(drawTrashMatch[1]),
      trashCount: parseInt(drawTrashMatch[2]),
      condition
    }
  }

  // Pattern 2: Simple draw "Draw X card(s)"
  const drawMatch = attackEffect.match(/[Dd]raw (\d+) cards?/i)
  if (drawMatch) {
    return {
      type: 'draw',
      donRequirement,
      drawCount: parseInt(drawMatch[1]),
      condition
    }
  }

  // Pattern 3: K.O. opponent's character with power condition
  const koPowerMatch = attackEffect.match(/K\.?O\.? (?:up to )?(\d+) (?:of )?your opponent'?s Characters? with (\d+) power or less/i)
  if (koPowerMatch) {
    return {
      type: 'ko_opponent',
      donRequirement,
      powerMax: parseInt(koPowerMatch[2]),
      condition
    }
  }

  // Pattern 4: K.O. with cost condition
  const koCostMatch = attackEffect.match(/K\.?O\.? (?:up to )?(\d+) (?:of )?your opponent'?s Characters? with (?:a )?cost (?:of )?(\d+) or less/i)
  if (koCostMatch) {
    return {
      type: 'ko_opponent',
      donRequirement,
      costMax: parseInt(koCostMatch[2]),
      condition
    }
  }

  // Pattern 5: Return to hand
  const returnMatch = attackEffect.match(/[Rr]eturn (?:up to )?(\d+) (?:of )?your opponent'?s Characters? with (?:a )?cost (?:of )?(\d+) or less to (?:the )?owner'?s hand/i)
  if (returnMatch) {
    return {
      type: 'return_to_hand',
      donRequirement,
      costMax: parseInt(returnMatch[2]),
      condition
    }
  }

  // Pattern 6: Power boost to self "This Character gains +X000 power"
  const selfPowerMatch = attackEffect.match(/[Tt]his Character gains \+(\d+) power/i)
  if (selfPowerMatch) {
    return {
      type: 'power_boost',
      donRequirement,
      powerChange: parseInt(selfPowerMatch[1]),
      targetSelf: true,
      condition
    }
  }

  // Pattern 7: Power reduce opponent "Give up to 1 of your opponent's Characters −X000 power"
  const powerReduceMatch = attackEffect.match(/[Gg]ive (?:up to )?(\d+) (?:of )?your opponent'?s Characters? [−\-](\d+) power/i)
  if (powerReduceMatch) {
    return {
      type: 'power_reduce',
      donRequirement,
      powerChange: -parseInt(powerReduceMatch[2]),
      condition
    }
  }

  // Pattern 8: Bottom deck opponent's character
  const bottomMatch = attackEffect.match(/[Pp]lace (?:up to )?(\d+) (?:of )?(?:your opponent'?s )?Characters? with (?:a )?cost (?:of )?(\d+) or less at the bottom/i)
  if (bottomMatch) {
    return {
      type: 'bottom_deck',
      donRequirement,
      costMax: parseInt(bottomMatch[2]),
      condition
    }
  }

  // Pattern 9: Disable blocker "cannot activate a [Blocker]"
  if (/cannot activate.*\[?Blocker\]?/i.test(attackEffect)) {
    const powerLimit = attackEffect.match(/(\d+) or less power/i)
    return {
      type: 'disable_blocker',
      donRequirement,
      powerMax: powerLimit ? parseInt(powerLimit[1]) : undefined,
      condition
    }
  }

  // Pattern 10: Give DON to leader/character
  const giveDonMatch = attackEffect.match(/give (?:up to )?(\d+) (?:rested )?DON/i)
  if (giveDonMatch) {
    return {
      type: 'give_don',
      donRequirement,
      drawCount: parseInt(giveDonMatch[1]),  // reusing for DON count
      condition
    }
  }

  // Pattern 11: Add DON from deck
  const addDonMatch = attackEffect.match(/add (?:up to )?(\d+) DON/i)
  if (addDonMatch) {
    return {
      type: 'add_don',
      donRequirement,
      drawCount: parseInt(addDonMatch[1]),
      condition
    }
  }

  // Pattern 12: Rest opponent's character
  const restMatch = attackEffect.match(/rest (?:up to )?(\d+) (?:of )?your opponent'?s Characters?/i)
  if (restMatch) {
    return {
      type: 'rest_opponent',
      donRequirement,
      costMax: 99,  // Default no cost limit
      condition
    }
  }

  return { type: 'unknown', donRequirement }
}

// Parse [On K.O.] effect
interface OnKOEffectInfo {
  type: 'draw' | 'return_to_hand' | 'play_from_trash' | 'rest_opponent' | 'unknown'
  drawCount?: number
  condition?: string
  leaderCondition?: string  // e.g., "[Boa Hancock]" or "multicolored"
  traitFilter?: string
  costMax?: number
}

const parseOnKOEffect = (effect: string): OnKOEffectInfo => {
  // Extract just the [On K.O.] portion of the effect
  const koMatch = effect.match(/\[On K\.O\.\](.*?)(?:\[|<br>|$)/is)
  if (!koMatch) return { type: 'unknown' }

  const koEffect = koMatch[1]

  // Parse condition for leader name/multicolored
  let condition: string | undefined
  let leaderCondition: string | undefined

  // Check for leader condition like "If your Leader is [Boa Hancock] or multicolored"
  const leaderMatch = koEffect.match(/If your Leader is \[([^\]]+)\] or (\w+)/i)
  if (leaderMatch) {
    leaderCondition = leaderMatch[1]
    condition = leaderMatch[2]  // e.g., "multicolored"
  }

  // Check for life condition
  const lifeCondition = koEffect.match(/If you have (\d+) or less Life/i)
  if (lifeCondition) {
    condition = `life_lte_${lifeCondition[1]}`
  }

  // Pattern 1: Draw cards "[On K.O.] Draw X card(s)"
  const drawMatch = koEffect.match(/draw (\d+) cards?/i)
  if (drawMatch) {
    return {
      type: 'draw',
      drawCount: parseInt(drawMatch[1]),
      condition,
      leaderCondition,
    }
  }

  // Pattern 2: Return to hand (self) "[On K.O.] Return this card to hand"
  if (/return this card to (?:your )?hand/i.test(koEffect)) {
    return {
      type: 'return_to_hand',
      condition,
    }
  }

  // Pattern 3: Play from trash "[On K.O.] ...play this Character...from your trash"
  if (/play this Character.*from your trash/i.test(koEffect)) {
    return {
      type: 'play_from_trash',
      condition,
    }
  }

  // Pattern 4: Rest opponent's cards
  const restMatch = koEffect.match(/[Rr]est (?:up to )?(\d+)(?: of)? (?:your )?opponent'?s/i)
  if (restMatch) {
    return {
      type: 'rest_opponent',
      drawCount: parseInt(restMatch[1]),  // reusing drawCount for count
      condition,
    }
  }

  return { type: 'unknown' }
}

// Parse [On Play] effect to determine its type
interface OnPlayEffectInfo {
  type: 'draw' | 'draw_trash' | 'look_top' | 'search' | 'draw_give_don' | 'add_don' | 'set_don_active' | 'give_power' | 'ko_opponent' | 'bottom_deck_opponent' | 'return_to_hand' | 'unknown'
  drawCount?: number
  trashCount?: number
  lookCount?: number
  condition?: string
  filterType?: string
  // Filter constraints for searcher cards
  costMax?: number
  costMin?: number
  powerMax?: number
  powerMin?: number
  cardType?: string  // CHARACTER, EVENT, etc.
  traitFilter?: string  // e.g., "Straw Hat Crew", "Land of Wano"
  // DON effects
  giveDonCount?: number
  giveDonRested?: boolean
  addDonCount?: number
  addDonRested?: boolean  // true = rest the DON, false = set active
  setDonActiveCount?: number
  // Power modification
  powerChange?: number  // negative for -power
  // Target selection
  targetOpponent?: boolean
  // Return to hand effects
  returnCount?: number
  // Leader type condition
  leaderTypeCondition?: string
}

// Parse conditions like "If you have X or less Life cards"
const parseCondition = (effect: string): string | undefined => {
  const lifeCondition = effect.match(/(?:If you have |have )(\d+) or less Life/i)
  if (lifeCondition) return `life_lte_${lifeCondition[1]}`

  const lifeMinCondition = effect.match(/(?:If you have |have )(\d+) or more Life/i)
  if (lifeMinCondition) return `life_gte_${lifeMinCondition[1]}`

  const leaderCondition = effect.match(/If your Leader (?:has the |is )\{?([^}]+)\}?/i)
  if (leaderCondition) return `leader_${leaderCondition[1].replace(/[\[\]]/g, '')}`

  return undefined
}

const parseOnPlayEffect = (effect: string): OnPlayEffectInfo => {
  const condition = parseCondition(effect)

  // Pattern 1: "draw X cards and trash Y card(s)"
  const drawTrashMatch = effect.match(/draw (\d+) cards? and trash (\d+) cards?/i)
  if (drawTrashMatch) {
    return {
      type: 'draw_trash',
      drawCount: parseInt(drawTrashMatch[1]),
      trashCount: parseInt(drawTrashMatch[2]),
      condition
    }
  }

  // Pattern 2: Yamato-style "draw X cards...give up to Y rested DON"
  const drawGiveDonMatch = effect.match(/draw (\d+) cards?.*give (?:up to )?(\d+) rested DON/i)
  if (drawGiveDonMatch) {
    return {
      type: 'draw_give_don',
      drawCount: parseInt(drawGiveDonMatch[1]),
      giveDonCount: parseInt(drawGiveDonMatch[2]),
      giveDonRested: true,
      condition
    }
  }

  // Pattern 3: "Add up to X DON!! card from your DON!! deck and [rest it/set it as active]"
  const addDonMatch = effect.match(/[Aa]dd (?:up to )?(\d+) DON!* cards? from your DON!* deck(?: and (rest|set)(?: it)?)?/i)
  if (addDonMatch) {
    const count = parseInt(addDonMatch[1])
    const restOrActive = addDonMatch[2]?.toLowerCase()
    return {
      type: 'add_don',
      addDonCount: count,
      addDonRested: restOrActive !== 'set',  // default to rested unless "set as active"
      condition
    }
  }

  // Pattern 4: "set up to X of your DON!! cards as active"
  const setDonActiveMatch = effect.match(/set (?:up to )?(\d+) of your DON!* cards? as active/i)
  if (setDonActiveMatch) {
    return {
      type: 'set_don_active',
      setDonActiveCount: parseInt(setDonActiveMatch[1]),
      condition
    }
  }

  // Pattern 5: "K.O. up to 1 of your opponent's Characters with X [cost/power] or less"
  const koOpponentMatch = effect.match(/K\.?O\.? (?:up to )?(\d+) of your opponent'?s Characters? with (?:a )?(?:base )?(?:cost|power) (?:of )?(\d+) or less/i)
  if (koOpponentMatch) {
    const isCost = /cost/i.test(effect)
    return {
      type: 'ko_opponent',
      targetOpponent: true,
      costMax: isCost ? parseInt(koOpponentMatch[2]) : undefined,
      powerMax: !isCost ? parseInt(koOpponentMatch[2]) : undefined,
      condition
    }
  }

  // Pattern 5b: "Trash up to 1 of your opponent's Characters with X power or less"
  const trashOpponentMatch = effect.match(/[Tt]rash (?:up to )?(\d+) of your opponent'?s Characters? with (?:a )?(\d+) power or less/i)
  if (trashOpponentMatch) {
    return {
      type: 'ko_opponent',  // treat same as KO for playtest
      targetOpponent: true,
      powerMax: parseInt(trashOpponentMatch[2]),
      condition
    }
  }

  // Pattern 6: "Place up to 1 of your opponent's Characters with a cost of X or less at the bottom"
  const bottomDeckMatch = effect.match(/[Pp]lace (?:up to )?(\d+) (?:of )?your opponent'?s Characters? with (?:a )?(?:base )?cost (?:of )?(\d+) or less at the bottom/i)
  if (bottomDeckMatch) {
    return {
      type: 'bottom_deck_opponent',
      targetOpponent: true,
      costMax: parseInt(bottomDeckMatch[2]),
      condition
    }
  }

  // Pattern 7: "Give up to 1 of your opponent's Characters −X000 power"
  const powerModMatch = effect.match(/[Gg]ive (?:up to )?(\d+) (?:of )?your opponent'?s Characters? [−\-](\d+) power/i)
  if (powerModMatch) {
    return {
      type: 'give_power',
      targetOpponent: true,
      powerChange: -parseInt(powerModMatch[2]),
      condition
    }
  }

  // Pattern 7b: "Return up to X of your opponent's Characters with a cost of Y or less to the owner's hand"
  const returnToHandMatch = effect.match(/[Rr]eturn (?:up to )?(\d+) (?:of )?your opponent'?s Characters? with (?:a )?cost (?:of )?(\d+) or less to (?:the )?owner'?s hand/i)
  if (returnToHandMatch) {
    // Check for leader type condition like "If your Leader's type includes..."
    let leaderTypeCondition: string | undefined
    const leaderTypeMatch = effect.match(/If your Leader'?s type includes ['"]?([^'"]+)['"]?/i)
    if (leaderTypeMatch) leaderTypeCondition = leaderTypeMatch[1]

    return {
      type: 'return_to_hand',
      targetOpponent: true,
      returnCount: parseInt(returnToHandMatch[1]),
      costMax: parseInt(returnToHandMatch[2]),
      leaderTypeCondition,
      condition
    }
  }

  // Pattern 8: "Look at X cards from the top of your deck" or "Look at the top X cards of your deck"
  const lookMatch = effect.match(/[Ll]ook at (\d+) cards? from the top of your deck/i)
    || effect.match(/[Ll]ook at the top (\d+) cards? of your deck/i)
  if (lookMatch) {
    const lookCount = parseInt(lookMatch[1])

    // Parse cost restrictions
    let costMax: number | undefined
    let costMin: number | undefined
    const costMaxMatch = effect.match(/cost (?:of )?(\d+) or less/i)
    const costMinMatch = effect.match(/cost (?:of )?(\d+) or (?:higher|more)/i)
    if (costMaxMatch) costMax = parseInt(costMaxMatch[1])
    if (costMinMatch) costMin = parseInt(costMinMatch[1])

    // Parse type filter (CHARACTER, EVENT) - be specific about the context
    // Look for patterns like "reveal up to 1 Character" NOT just "Character" anywhere
    let cardType: string | undefined
    const characterSelectMatch = effect.match(/(?:reveal|add|choose|search).*?(?:up to )?\d+\s+Character/i)
    const eventSelectMatch = effect.match(/(?:reveal|add|choose|search).*?(?:up to )?\d+\s+Event/i)
    const genericCardMatch = effect.match(/(?:reveal|add|choose).*?(?:up to )?\d+\s+card(?!.*(?:Character|Event))/i)

    // Only set cardType if explicitly selecting that type, not just mentioning it
    if (characterSelectMatch && !genericCardMatch) cardType = 'CHARACTER'
    else if (eventSelectMatch && !genericCardMatch) cardType = 'EVENT'
    // If it says "card" without specifying type, leave cardType undefined (any type allowed)

    // Parse trait filter (e.g., "{Straw Hat Crew}", "[Whitebeard Pirates] type", or 'type including "Whitebeard Pirates"')
    let traitFilter: string | undefined
    const traitMatch = effect.match(/\{([^}]+)\}/i)
      || effect.match(/\[([^\]]+)\] type/i)  // [Whitebeard Pirates] type
      || effect.match(/type including ['"]?([^'"]+)['"]?/i)
    if (traitMatch) traitFilter = traitMatch[1]

    return {
      type: 'look_top',
      lookCount,
      costMax,
      costMin,
      cardType,
      traitFilter,
      filterType: traitFilter,
      condition
    }
  }

  // Pattern 9: Simple "draw X cards" (without trash)
  const simpleDrawMatch = effect.match(/\[On Play\].*?draw (\d+) cards?/i)
  if (simpleDrawMatch && !effect.match(/trash/i)) {
    return {
      type: 'draw',
      drawCount: parseInt(simpleDrawMatch[1]),
      condition
    }
  }

  // Pattern 10: Search/reveal deck
  if (effect.toLowerCase().includes('search') || (effect.toLowerCase().includes('reveal') && effect.toLowerCase().includes('deck'))) {
    const lookCount = effect.match(/(\d+) cards?/i)

    let costMax: number | undefined
    let costMin: number | undefined
    const costMaxMatch = effect.match(/cost (?:of )?(\d+) or less/i)
    const costMinMatch = effect.match(/cost (?:of )?(\d+) or (?:higher|more)/i)
    if (costMaxMatch) costMax = parseInt(costMaxMatch[1])
    if (costMinMatch) costMin = parseInt(costMinMatch[1])

    // Parse type filter - be specific about context
    let cardType: string | undefined
    const characterSelectMatch = effect.match(/(?:reveal|add|choose|search).*?(?:up to )?\d+\s+Character/i)
    const eventSelectMatch = effect.match(/(?:reveal|add|choose|search).*?(?:up to )?\d+\s+Event/i)
    const genericCardMatch = effect.match(/(?:reveal|add|choose).*?(?:up to )?\d+\s+card(?!.*(?:Character|Event))/i)

    if (characterSelectMatch && !genericCardMatch) cardType = 'CHARACTER'
    else if (eventSelectMatch && !genericCardMatch) cardType = 'EVENT'

    let traitFilter: string | undefined
    const traitMatch = effect.match(/\{([^}]+)\}/i) || effect.match(/type including ['"]?([^'"]+)['"]?/i)
    if (traitMatch) traitFilter = traitMatch[1]

    return {
      type: 'search',
      lookCount: lookCount ? parseInt(lookCount[1]) : 5,
      costMax,
      costMin,
      cardType,
      traitFilter,
      condition
    }
  }

  return { type: 'unknown' }
}

// Check if condition is met
const checkCondition = (condition: string | undefined, player: PlaytestPlayer): boolean => {
  if (!condition) return true

  if (condition.startsWith('life_lte_')) {
    const threshold = parseInt(condition.split('_')[2])
    return player.lifeCards.length <= threshold
  }
  if (condition.startsWith('life_gte_')) {
    const threshold = parseInt(condition.split('_')[2])
    return player.lifeCards.length >= threshold
  }
  // Leader conditions - for now, always pass (would need leader type data)
  if (condition.startsWith('leader_')) {
    return true  // TODO: Check leader type when data is available
  }

  return true
}

// Create a filter function from effect info
const createSelectionFilter = (effectInfo: OnPlayEffectInfo): ((card: PlaytestCard) => boolean) | undefined => {
  const { costMax, costMin, powerMax, powerMin, cardType, traitFilter } = effectInfo

  // If no filter constraints, return undefined (allow all)
  if (costMax === undefined && costMin === undefined && powerMax === undefined && powerMin === undefined && !cardType && !traitFilter) {
    return undefined
  }

  return (card: PlaytestCard) => {
    // Cost max check
    if (costMax !== undefined && (card.cost === null || card.cost > costMax)) return false
    // Cost min check
    if (costMin !== undefined && (card.cost === null || card.cost < costMin)) return false
    // Power max check
    if (powerMax !== undefined && (card.power === null || card.power > powerMax)) return false
    // Power min check
    if (powerMin !== undefined && (card.power === null || card.power < powerMin)) return false
    // Card type check (CHARACTER, EVENT, STAGE)
    if (cardType && card.type !== cardType) return false
    // Trait filter check - check card's trait field, effect text, and name
    if (traitFilter) {
      // Normalize the trait filter (remove quotes, extra spaces)
      const traitLower = traitFilter.toLowerCase().replace(/['"]/g, '').trim()

      // Handle traits field - could be string or array
      let cardTraitsNormalized = ''
      if (card.traits) {
        if (Array.isArray(card.traits)) {
          // If array, join with / separator
          cardTraitsNormalized = (card.traits as string[]).join('/').toLowerCase()
        } else {
          cardTraitsNormalized = String(card.traits).toLowerCase()
        }
      }

      const effectText = (card.effect || '').toLowerCase()
      const cardName = card.name.toLowerCase()

      // For trait matching, split the card's traits by "/" and check each one
      // This handles "The Four Emperors/Whitebeard Pirates" matching "Whitebeard Pirates"
      const traitParts = cardTraitsNormalized.split('/').map(t => t.trim())
      const hasTraitInField = traitParts.some(part => part.includes(traitLower) || traitLower.includes(part))

      // Also check if the trait appears as a substring anywhere in the traits string
      const hasTraitAsSubstring = cardTraitsNormalized.includes(traitLower)

      const hasTraitInEffect = effectText.includes(traitLower)
      const hasTraitInName = cardName.includes(traitLower)

      // Must match trait in at least one place
      if (!hasTraitInField && !hasTraitAsSubstring && !hasTraitInEffect && !hasTraitInName) {
        return false
      }
    }
    return true
  }
}

// Create filter description from effect info
const createFilterDescription = (effectInfo: OnPlayEffectInfo): string | undefined => {
  const parts: string[] = []

  if (effectInfo.cardType) parts.push(effectInfo.cardType)
  if (effectInfo.costMax !== undefined) parts.push(`cost ${effectInfo.costMax} or less`)
  if (effectInfo.costMin !== undefined) parts.push(`cost ${effectInfo.costMin} or more`)
  if (effectInfo.traitFilter) parts.push(`{${effectInfo.traitFilter}}`)

  return parts.length > 0 ? parts.join(', ') : undefined
}

// Get counter value from a character card
const getCounterValue = (card: PlaytestCard): number => {
  if (card.type !== 'CHARACTER') return 0
  return card.counter || 0
}

// Check if leader matches condition for On KO effects
const checkLeaderCondition = (leader: PlaytestCard | null, leaderCondition: string | undefined, condition: string | undefined): boolean => {
  if (!leaderCondition && !condition) return true
  if (!leader) return false

  // Check for specific leader name
  if (leaderCondition) {
    const leaderName = leader.name.toLowerCase()
    if (leaderName.includes(leaderCondition.toLowerCase())) return true
  }

  // Check for multicolored leader
  if (condition === 'multicolored') {
    const colors = leader.colors || []
    if (colors.length > 1) return true
  }

  // If we have a leader condition but didn't match, check if condition alone passes
  if (leaderCondition && condition === 'multicolored') {
    // Either leader name OR multicolored
    const colors = leader.colors || []
    return colors.length > 1
  }

  return false
}

// Execute On KO effect and return updated state parts
interface OnKOResult {
  drawnCards: PlaytestCard[]
  returnToHand: boolean
  playFromTrash: boolean
  logs: string[]
}

const executeOnKOEffect = (
  koCard: PlaytestCard,
  owner: PlaytestPlayer,
  opponent: PlaytestPlayer,
): OnKOResult => {
  const result: OnKOResult = {
    drawnCards: [],
    returnToHand: false,
    playFromTrash: false,
    logs: [],
  }

  if (!hasOnKOEffect(koCard)) return result

  const effectInfo = parseOnKOEffect(koCard.effect || '')
  if (effectInfo.type === 'unknown') return result

  result.logs.push(`  [On K.O.] ${koCard.name} effect triggered!`)

  // Check conditions
  if (effectInfo.condition?.startsWith('life_lte_')) {
    const threshold = parseInt(effectInfo.condition.split('_')[2])
    if (owner.lifeCards.length > threshold) {
      result.logs.push(`    Condition not met (need ${threshold} or less life, have ${owner.lifeCards.length})`)
      return result
    }
  }

  // Check leader condition
  if (effectInfo.leaderCondition || effectInfo.condition === 'multicolored') {
    if (!checkLeaderCondition(owner.leader, effectInfo.leaderCondition, effectInfo.condition)) {
      result.logs.push(`    Leader condition not met`)
      return result
    }
  }

  // Execute based on effect type
  switch (effectInfo.type) {
    case 'draw':
      const drawCount = effectInfo.drawCount || 1
      for (let i = 0; i < drawCount && owner.deck.length > 0; i++) {
        const drawnCard = owner.deck.shift()!
        result.drawnCards.push(drawnCard)
      }
      result.logs.push(`    Drew ${result.drawnCards.length} card(s)`)
      break

    case 'return_to_hand':
      result.returnToHand = true
      result.logs.push(`    ${koCard.name} returns to hand`)
      break

    case 'play_from_trash':
      result.playFromTrash = true
      result.logs.push(`    ${koCard.name} can be played from trash (rested)`)
      break

    case 'rest_opponent':
      const restCount = effectInfo.drawCount || 1
      let rested = 0
      for (const card of opponent.field) {
        if (!card.isResting && rested < restCount) {
          card.isResting = true
          rested++
          result.logs.push(`    Rested opponent's ${card.name}`)
        }
      }
      break
  }

  return result
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
  activatedAbilitiesThisTurn: string[]  // Track card instanceIds that used Once Per Turn abilities
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
  activateAbility: (player: 0 | 1, zone: 'leader' | 'field', index: number) => void

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
  traits: cardData.traits || cardData.cardTraits || null,  // Card trait like "Navy", "Straw Hat Crew"
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
  activatedAbilitiesThisTurn: [],
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
        const selectionFilter = createSelectionFilter(effectInfo)
        const filterDescription = createFilterDescription(effectInfo)

        logs.push(`  Looking at top ${lookCount} cards...`)
        if (filterDescription) {
          logs.push(`  Filter: ${filterDescription}`)
        }

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
            selectionFilter,
            filterDescription,
            onComplete: 'to_hand',
          },
        })
        return
      }

      // Handle draw_give_don effect (like OP13-054 Yamato)
      if (effectInfo.type === 'draw_give_don') {
        // Check life condition if present
        let conditionMet = true
        if (effectInfo.condition?.startsWith('life_lte_')) {
          const lifeThreshold = parseInt(effectInfo.condition.split('_')[2])
          conditionMet = p.lifeCards.length <= lifeThreshold
        }

        if (conditionMet) {
          const drawCount = effectInfo.drawCount || 0
          const giveDonCount = effectInfo.giveDonCount || 0

          // Draw cards
          const drawnCards: PlaytestCard[] = []
          const remainingDeck = [...p.deck]
          for (let i = 0; i < drawCount && remainingDeck.length > 0; i++) {
            drawnCards.push(remainingDeck.shift()!)
          }

          logs.push(`  Drew ${drawnCards.length} card(s).`)

          // Give rested DON to leader
          // After paying cost, DON becomes rested. We can give up to giveDonCount of that to leader.
          let donGiven = 0
          let newLeader = p.leader
          // Calculate rested DON AFTER cost payment (cost becomes rested)
          const restedDonAfterCost = p.donRested + cost
          if (giveDonCount > 0 && restedDonAfterCost > 0 && p.leader) {
            // Give up to giveDonCount rested DON to leader
            const actualDonToGive = Math.min(giveDonCount, restedDonAfterCost)
            if (actualDonToGive > 0) {
              newLeader = { ...p.leader, attachedDon: p.leader.attachedDon + actualDonToGive }
              donGiven = actualDonToGive
              logs.push(`  Gave ${donGiven} rested DON to ${p.leader.name}. (+${donGiven * 1000} power)`)
            }
          }

          set({
            [playerKey]: {
              ...p,
              leader: newLeader,
              hand: [...newHand, ...drawnCards],
              deck: remainingDeck,
              field: [...p.field, playedCard],
              donActive: p.donActive - cost,
              donRested: p.donRested + cost - donGiven,  // Some rested DON went to leader
            },
            logs,
            selectedCard: null,
          })
          return
        } else {
          logs.push(`  Condition not met (need ${effectInfo.condition?.replace('life_lte_', '')} or less life).`)
        }
      }

      // Handle simple draw effect
      if (effectInfo.type === 'draw') {
        const conditionMet = checkCondition(effectInfo.condition, p)

        if (conditionMet) {
          const drawCount = effectInfo.drawCount || 0
          const drawnCards: PlaytestCard[] = []
          const remainingDeck = [...p.deck]
          for (let i = 0; i < drawCount && remainingDeck.length > 0; i++) {
            drawnCards.push(remainingDeck.shift()!)
          }

          logs.push(`  Drew ${drawnCards.length} card(s).`)

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
          logs.push(`  Condition not met.`)
        }
      }

      // Handle add DON from DON deck
      if (effectInfo.type === 'add_don') {
        const conditionMet = checkCondition(effectInfo.condition, p)

        if (conditionMet) {
          const addCount = effectInfo.addDonCount || 0
          const actualAdd = Math.min(addCount, p.donDeck)

          if (actualAdd > 0) {
            const newDonDeck = p.donDeck - actualAdd
            const addToActive = !effectInfo.addDonRested
            const newDonActive = addToActive ? p.donActive - cost + actualAdd : p.donActive - cost
            const newDonRested = addToActive ? p.donRested + cost : p.donRested + cost + actualAdd

            logs.push(`  Added ${actualAdd} DON from DON deck${effectInfo.addDonRested ? ' (rested)' : ' (active)'}.`)

            set({
              [playerKey]: {
                ...p,
                hand: newHand,
                field: [...p.field, playedCard],
                donDeck: newDonDeck,
                donActive: newDonActive,
                donRested: newDonRested,
              },
              logs,
              selectedCard: null,
            })
            return
          }
        } else {
          logs.push(`  Condition not met.`)
        }
      }

      // Handle set DON as active
      if (effectInfo.type === 'set_don_active') {
        const conditionMet = checkCondition(effectInfo.condition, p)

        if (conditionMet) {
          const setActiveCount = effectInfo.setDonActiveCount || 0
          // After paying cost, we have some rested DON
          const restedAfterCost = p.donRested + cost
          const actualSetActive = Math.min(setActiveCount, restedAfterCost)

          if (actualSetActive > 0) {
            const newDonActive = p.donActive - cost + actualSetActive
            const newDonRested = restedAfterCost - actualSetActive

            logs.push(`  Set ${actualSetActive} DON as active.`)

            set({
              [playerKey]: {
                ...p,
                hand: newHand,
                field: [...p.field, playedCard],
                donActive: newDonActive,
                donRested: newDonRested,
              },
              logs,
              selectedCard: null,
            })
            return
          }
        } else {
          logs.push(`  Condition not met.`)
        }
      }

      // Handle return to hand effect (like Atmos OP08-040)
      if (effectInfo.type === 'return_to_hand') {
        // Check leader type condition if present
        let conditionMet = true
        if (effectInfo.leaderTypeCondition && p.leader) {
          // Check if leader's type includes the required trait
          const leaderTraits = (p.leader.traits || '').toString().toLowerCase()
          const requiredTrait = effectInfo.leaderTypeCondition.toLowerCase()
          conditionMet = leaderTraits.includes(requiredTrait)
        }

        if (conditionMet) {
          const costMax = effectInfo.costMax || 99
          const returnCount = effectInfo.returnCount || 1
          const opponent = player === 0 ? state.player2 : state.player1
          const opponentKey = player === 0 ? 'player2' : 'player1'

          // Find valid targets (opponent's characters with cost <= costMax)
          const validTargets = opponent.field.filter(c => (c.cost || 0) <= costMax)

          if (validTargets.length > 0) {
            logs.push(`  Return to hand effect: Select up to ${returnCount} of opponent's Characters (cost ${costMax} or less)`)

            // For now, auto-select the first valid target(s)
            // In a full implementation, this would trigger a selection UI
            const targetsToReturn = validTargets.slice(0, returnCount)
            const newOpponentField = opponent.field.filter(c => !targetsToReturn.includes(c))
            const newOpponentHand = [...opponent.hand, ...targetsToReturn.map(c => ({ ...c, attachedDon: 0, isResting: false }))]

            for (const target of targetsToReturn) {
              logs.push(`  ${target.name} returned to opponent's hand!`)
            }

            set({
              [playerKey]: {
                ...p,
                hand: newHand,
                field: [...p.field, playedCard],
                donActive: p.donActive - cost,
                donRested: p.donRested + cost,
              },
              [opponentKey]: {
                ...opponent,
                field: newOpponentField,
                hand: newOpponentHand,
              },
              logs,
              selectedCard: null,
            })
            return
          } else {
            logs.push(`  No valid targets for return to hand effect.`)
          }
        } else {
          logs.push(`  Leader type condition not met.`)
        }
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

    const currentPlayerKey = state.activePlayer === 0 ? 'player1' : 'player2'
    const currentP = state[currentPlayerKey]

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

    // Update turn number (increments every time a player ends their turn)
    // Turn 1 = P1's first turn, Turn 2 = P2's first turn, Turn 3 = P1's second turn, etc.
    const newTurn = state.turn + 1

    const logs = [
      ...state.logs,
      `--- ${currentP.name} ends turn ---`,
      `  DON returned: ${leaderDon} from leader, ${fieldDon} from field, ${currentP.donRested} rested, ${currentP.donActive} active = ${totalDonReturned} total`,
      `--- Turn ${newTurn} - ${nextP.name}'s turn ---`,
      `Refresh: All ${nextP.name}'s cards activated, DON returned to active (${nextTotalDon} DON).`,
      `DON Phase: ${nextP.name} draws ${actualDonDraw} DON. (Total: ${nextTotalDon + actualDonDraw})`,
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
      activatedAbilitiesThisTurn: [],  // Reset Once Per Turn abilities
      logs,
      selectedCard: null,
    })

    // Draw phase: Draw 1 card (happens after the first turn)
    get().drawCard(nextPlayer as 0 | 1)
  },

  activateAbility: (player, zone, index) => {
    set(state => {
      if (state.gameOver) return { logs: [...state.logs, 'Game is over!'] }
      if (player !== state.activePlayer) return { logs: [...state.logs, 'Not your turn!'] }

      const playerKey = player === 0 ? 'player1' : 'player2'
      const opponentKey = player === 0 ? 'player2' : 'player1'
      const p = state[playerKey]
      const opponent = state[opponentKey]

      // Get the card
      const card = zone === 'leader' ? p.leader : p.field[index]
      if (!card) return { logs: [...state.logs, 'Card not found!'] }

      // Check if card has [Activate: Main] effect
      if (!hasActivateMainEffect(card)) {
        return { logs: [...state.logs, `${card.name} has no [Activate: Main] ability.`] }
      }

      const effectInfo = parseActivateMainEffect(card.effect || '')

      // Check Once Per Turn
      if (effectInfo.oncePerTurn && state.activatedAbilitiesThisTurn.includes(card.instanceId)) {
        return { logs: [...state.logs, `${card.name}'s ability can only be used once per turn.`] }
      }

      // Check if card is already rested (for abilities that require resting self)
      if (effectInfo.restSelf && card.isResting) {
        return { logs: [...state.logs, `${card.name} is already rested.`] }
      }

      // Check DON cost
      if (effectInfo.restDonCount > p.donActive) {
        return { logs: [...state.logs, `Not enough active DON! Need ${effectInfo.restDonCount}, have ${p.donActive}.`] }
      }

      const logs = [...state.logs, `${p.name} activates ${card.name}'s [Activate: Main] ability!`]

      // Pay costs
      let newField = [...p.field]
      let newHand = [...p.hand]
      let newTrash = [...p.trash]
      let newDeck = [...p.deck]
      let newDonActive = p.donActive
      let newDonRested = p.donRested
      let newOpponentField = [...opponent.field]
      let newOpponentHand = [...opponent.hand]
      let newOpponentDeck = [...opponent.deck]

      // Rest self
      if (effectInfo.restSelf && zone === 'field') {
        newField[index] = { ...newField[index], isResting: true }
        logs.push(`  Rested ${card.name}.`)
      }

      // Trash self
      if (effectInfo.trashSelf && zone === 'field') {
        const trashed = newField.splice(index, 1)[0]
        newTrash.push({ ...trashed, attachedDon: 0 })
        logs.push(`  Trashed ${card.name}.`)
      }

      // Rest DON
      if (effectInfo.restDonCount > 0) {
        newDonActive -= effectInfo.restDonCount
        newDonRested += effectInfo.restDonCount
        logs.push(`  Rested ${effectInfo.restDonCount} DON.`)
      }

      // Trash from hand (auto-select lowest cost for now)
      if (effectInfo.trashFromHand > 0) {
        const sorted = [...newHand].sort((a, b) => (a.cost || 0) - (b.cost || 0))
        for (let i = 0; i < effectInfo.trashFromHand && sorted.length > 0; i++) {
          const toTrash = sorted.shift()!
          const idx = newHand.findIndex(c => c.instanceId === toTrash.instanceId)
          if (idx >= 0) {
            newHand.splice(idx, 1)
            newTrash.push(toTrash)
            logs.push(`  Trashed ${toTrash.name} from hand.`)
          }
        }
      }

      // Execute effect
      switch (effectInfo.type) {
        case 'draw':
          const drawCount = effectInfo.drawCount || 1
          for (let i = 0; i < drawCount && newDeck.length > 0; i++) {
            const drawn = newDeck.shift()!
            newHand.push(drawn)
          }
          logs.push(`  Drew ${drawCount} card(s).`)
          break

        case 'ko_opponent':
          const koTargets = newOpponentField.filter(c => (c.cost || 0) <= (effectInfo.costMax || 99))
          if (koTargets.length > 0) {
            const target = koTargets[0]
            const idx = newOpponentField.findIndex(c => c.instanceId === target.instanceId)
            if (idx >= 0) {
              newOpponentField.splice(idx, 1)
              logs.push(`  K.O.'d opponent's ${target.name}!`)
            }
          } else {
            logs.push(`  No valid K.O. targets.`)
          }
          break

        case 'power_boost':
          if (zone === 'field' && !effectInfo.trashSelf) {
            // Would need to track power modifiers - for now just log
            logs.push(`  ${card.name} gains +${effectInfo.powerChange} power this turn.`)
          }
          break

        case 'power_reduce':
          if (newOpponentField.length > 0) {
            logs.push(`  Gave opponent's ${newOpponentField[0].name} ${effectInfo.powerChange} power this turn.`)
          }
          break

        case 'bottom_deck':
          const bottomTargets = newOpponentField.filter(c => (c.cost || 0) <= (effectInfo.costMax || 99))
          if (bottomTargets.length > 0) {
            const target = bottomTargets[0]
            const idx = newOpponentField.findIndex(c => c.instanceId === target.instanceId)
            if (idx >= 0) {
              newOpponentField.splice(idx, 1)
              newOpponentDeck.push({ ...target, attachedDon: 0, isResting: false })
              logs.push(`  Placed ${target.name} at the bottom of opponent's deck!`)
            }
          } else {
            logs.push(`  No valid targets.`)
          }
          break

        case 'search':
          // Would need UI for selection - for now auto-select
          if (effectInfo.lookCount && newDeck.length > 0) {
            const lookCount = Math.min(effectInfo.lookCount, newDeck.length)
            logs.push(`  Looking at top ${lookCount} cards...`)
            // For now, just draw the first matching card
            if (effectInfo.traitFilter) {
              const topCards = newDeck.slice(0, lookCount)
              const match = topCards.find(c => {
                const traits = (c.traits || '').toString().toLowerCase()
                return traits.includes(effectInfo.traitFilter!.toLowerCase())
              })
              if (match) {
                const idx = newDeck.findIndex(c => c.instanceId === match.instanceId)
                if (idx >= 0) {
                  newDeck.splice(idx, 1)
                  newHand.push(match)
                  logs.push(`  Added ${match.name} to hand.`)
                }
              } else {
                logs.push(`  No matching card found.`)
              }
            }
          }
          break

        default:
          logs.push(`  Effect type '${effectInfo.type}' not fully implemented yet.`)
      }

      // Track Once Per Turn usage
      const newActivated = effectInfo.oncePerTurn
        ? [...state.activatedAbilitiesThisTurn, card.instanceId]
        : state.activatedAbilitiesThisTurn

      return {
        [playerKey]: {
          ...p,
          field: newField,
          hand: newHand,
          deck: newDeck,
          trash: newTrash,
          donActive: newDonActive,
          donRested: newDonRested,
        },
        [opponentKey]: {
          ...opponent,
          field: newOpponentField,
          hand: newOpponentHand,
          deck: newOpponentDeck,
        },
        activatedAbilitiesThisTurn: newActivated,
        logs,
      }
    })
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

      const { player, effectType, revealedCards, onComplete, selectionCount, selectionFilter, filterDescription } = state.effectResolution
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

      // Validate selection against filter (for searcher effects)
      if (selectionFilter && selectedCards.length > 0) {
        const invalidCards = selectedCards.filter(card => !selectionFilter(card))
        if (invalidCards.length > 0) {
          return {
            logs: [...state.logs, `Invalid selection: ${invalidCards.map(c => c.name).join(', ')} does not match filter${filterDescription ? ` (${filterDescription})` : ''}.`],
          }
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
      if (state.activePlayer === 1 && state.turn < 4) {
        return { canAttack: false, reason: 'Leader cannot attack until turn 4' }
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
      let attackerPower = (attacker.power || 0) + (attacker.attachedDon * 1000)
      // DON is NOT active for defender (it's not their turn)
      const defenderBasePower = target.power || 0

      const logs = [...state.logs]

      // Track state changes from When Attacking effects
      let newAttackerField = [...attacker_p.field]
      let newDefenderField = [...defender_p.field]
      let newAttackerHand = [...attacker_p.hand]
      let newAttackerDeck = [...attacker_p.deck]
      let newAttackerTrash = [...attacker_p.trash]
      let newDefenderHand = [...defender_p.hand]
      let newDefenderDeck = [...defender_p.deck]
      let blockerDisabledPower: number | undefined = undefined

      // Execute [When Attacking] effect if present
      if (hasWhenAttackingEffect(attacker)) {
        const effectInfo = parseWhenAttackingEffect(attacker.effect || '')

        // Check DON requirement
        const hasEnoughDon = attacker.attachedDon >= effectInfo.donRequirement

        if (hasEnoughDon && effectInfo.type !== 'unknown') {
          logs.push(`  [When Attacking] ${attacker.name} effect triggered!`)

          // Check conditions
          let conditionMet = true
          if (effectInfo.condition?.startsWith('life_gte_')) {
            const threshold = parseInt(effectInfo.condition.split('_')[2])
            conditionMet = attacker_p.lifeCards.length >= threshold
          } else if (effectInfo.condition?.startsWith('life_lte_')) {
            const threshold = parseInt(effectInfo.condition.split('_')[2])
            conditionMet = attacker_p.lifeCards.length <= threshold
          } else if (effectInfo.condition?.startsWith('hand_lte_')) {
            const threshold = parseInt(effectInfo.condition.split('_')[2])
            conditionMet = attacker_p.hand.length <= threshold
          }

          if (!conditionMet) {
            logs.push(`    Condition not met.`)
          } else {
            // Execute effect based on type
            switch (effectInfo.type) {
              case 'draw':
                const drawCount = effectInfo.drawCount || 1
                for (let i = 0; i < drawCount && newAttackerDeck.length > 0; i++) {
                  const drawn = newAttackerDeck.shift()!
                  newAttackerHand.push(drawn)
                }
                logs.push(`    Drew ${drawCount} card(s).`)
                break

              case 'draw_trash':
                // Draw first
                const dCount = effectInfo.drawCount || 1
                for (let i = 0; i < dCount && newAttackerDeck.length > 0; i++) {
                  const drawn = newAttackerDeck.shift()!
                  newAttackerHand.push(drawn)
                }
                logs.push(`    Drew ${dCount} card(s).`)
                // Then trash (auto-select lowest cost for now)
                const tCount = effectInfo.trashCount || 1
                const sortedHand = [...newAttackerHand].sort((a, b) => (a.cost || 0) - (b.cost || 0))
                for (let i = 0; i < tCount && sortedHand.length > 0; i++) {
                  const toTrash = sortedHand.shift()!
                  const idx = newAttackerHand.findIndex(c => c.instanceId === toTrash.instanceId)
                  if (idx >= 0) {
                    newAttackerHand.splice(idx, 1)
                    newAttackerTrash.push(toTrash)
                    logs.push(`    Trashed ${toTrash.name}.`)
                  }
                }
                break

              case 'ko_opponent':
                // Find valid targets
                const koTargets = newDefenderField.filter(c => {
                  if (effectInfo.powerMax !== undefined && (c.power || 0) > effectInfo.powerMax) return false
                  if (effectInfo.costMax !== undefined && (c.cost || 0) > effectInfo.costMax) return false
                  return true
                })
                if (koTargets.length > 0) {
                  const koTarget = koTargets[0]
                  const idx = newDefenderField.findIndex(c => c.instanceId === koTarget.instanceId)
                  if (idx >= 0) {
                    newDefenderField.splice(idx, 1)
                    logs.push(`    K.O.'d opponent's ${koTarget.name}!`)
                  }
                } else {
                  logs.push(`    No valid K.O. targets.`)
                }
                break

              case 'return_to_hand':
                const returnTargets = newDefenderField.filter(c => (c.cost || 0) <= (effectInfo.costMax || 99))
                if (returnTargets.length > 0) {
                  const returnTarget = returnTargets[0]
                  const idx = newDefenderField.findIndex(c => c.instanceId === returnTarget.instanceId)
                  if (idx >= 0) {
                    newDefenderField.splice(idx, 1)
                    newDefenderHand.push({ ...returnTarget, attachedDon: 0, isResting: false })
                    logs.push(`    Returned ${returnTarget.name} to opponent's hand!`)
                  }
                } else {
                  logs.push(`    No valid targets to return.`)
                }
                break

              case 'power_boost':
                const boost = effectInfo.powerChange || 0
                attackerPower += boost
                logs.push(`    ${attacker.name} gains +${boost} power this battle! (Now: ${attackerPower})`)
                break

              case 'power_reduce':
                // Apply to first opponent character for now
                if (newDefenderField.length > 0) {
                  logs.push(`    Gave opponent's ${newDefenderField[0].name} ${effectInfo.powerChange} power this turn.`)
                }
                break

              case 'bottom_deck':
                const bottomTargets = newDefenderField.filter(c => (c.cost || 0) <= (effectInfo.costMax || 99))
                if (bottomTargets.length > 0) {
                  const bottomTarget = bottomTargets[0]
                  const idx = newDefenderField.findIndex(c => c.instanceId === bottomTarget.instanceId)
                  if (idx >= 0) {
                    newDefenderField.splice(idx, 1)
                    newDefenderDeck.push({ ...bottomTarget, attachedDon: 0, isResting: false })
                    logs.push(`    Placed ${bottomTarget.name} at the bottom of opponent's deck!`)
                  }
                } else {
                  logs.push(`    No valid targets.`)
                }
                break

              case 'disable_blocker':
                blockerDisabledPower = effectInfo.powerMax
                logs.push(`    Opponent cannot activate Blocker${effectInfo.powerMax ? ` with ${effectInfo.powerMax} or less power` : ''} this battle.`)
                break

              case 'rest_opponent':
                const activeOpponentCards = newDefenderField.filter(c => !c.isResting)
                if (activeOpponentCards.length > 0) {
                  const toRest = activeOpponentCards[0]
                  const idx = newDefenderField.findIndex(c => c.instanceId === toRest.instanceId)
                  if (idx >= 0) {
                    newDefenderField[idx] = { ...toRest, isResting: true }
                    logs.push(`    Rested opponent's ${toRest.name}!`)
                  }
                }
                break
            }
          }
        } else if (!hasEnoughDon && effectInfo.donRequirement > 0) {
          logs.push(`  [When Attacking] ${attacker.name} needs ${effectInfo.donRequirement} DON attached (has ${attacker.attachedDon}).`)
        }
      }

      logs.push(`${attacker_p.name}'s ${attacker.name} (Power: ${attackerPower}) attacks ${target.name}!`)

      // Find available blockers (defender's active characters with [Blocker])
      // Apply blocker disable effect if active
      const availableBlockers: { index: number, card: PlaytestCard }[] = []
      newDefenderField.forEach((card, index) => {
        if (hasBlocker(card) && !card.isResting) {
          // Check if blocker is disabled by When Attacking effect
          if (blockerDisabledPower !== undefined && (card.power || 0) <= blockerDisabledPower) {
            // Blocker is disabled, don't add to available blockers
            return
          }
          availableBlockers.push({ index, card })
        }
      })

      // Find available counter cards in defender's hand
      const availableCounters: { index: number, card: PlaytestCard, value: number }[] = []
      newDefenderHand.forEach((card, index) => {
        const counterValue = getCounterValue(card)
        if (counterValue > 0) {
          availableCounters.push({ index, card, value: counterValue })
        }
      })

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

      // Return updated state including When Attacking effect changes
      return {
        [activePlayerKey]: {
          ...attacker_p,
          hand: newAttackerHand,
          deck: newAttackerDeck,
          trash: newAttackerTrash,
        },
        [defenderKey]: {
          ...defender_p,
          field: newDefenderField,
          hand: newDefenderHand,
          deck: newDefenderDeck,
        },
        combat,
        logs
      }
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
          logs.push(`${attacker.name} KO's ${currentTarget.name}!`)

          // Check for On K.O. effects on the KO'd card
          const koResult = executeOnKOEffect(koCard, defender_p, attacker_p)
          logs.push(...koResult.logs)

          // Handle On K.O. results
          if (koResult.returnToHand) {
            // Card returns to hand instead of trash
            newDefenderHand.push({ ...koCard, attachedDon: 0, isResting: false })
          } else if (koResult.playFromTrash) {
            // Card goes to trash, then gets played rested (for Marco-style effects)
            // For now, add to field rested - in actual game this has more conditions
            newDefenderField.push({ ...koCard, attachedDon: 0, isResting: true })
            logs.push(`  ${koCard.name} played from trash (rested)`)
          } else {
            // Normal KO - card goes to trash
            newDefenderTrash.push({ ...koCard, attachedDon: 0 })
          }

          // Add drawn cards to defender's hand
          if (koResult.drawnCards.length > 0) {
            newDefenderHand.push(...koResult.drawnCards)
          }

          // Return attached DON to active
          // Note: Defender's DON stays rested (it's not their turn)
        }
      } else {
        logs.push(`Attack is defended! (${attackerPower} vs ${totalDefense})`)
      }

      // Update defender's deck if cards were drawn by On K.O. effect
      const newDefenderDeck = [...defender_p.deck]

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
          deck: newDefenderDeck,
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

  addLog: (message) => {
    set(state => ({ logs: [...state.logs, message] }))
  },

  resetGame: () => {
    set(initialState)
  },
}))
