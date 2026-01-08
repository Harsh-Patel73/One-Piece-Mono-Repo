import { useState, useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Search, Plus, Pencil, Check, X, Play } from 'lucide-react'
import { motion } from 'framer-motion'
import { useCardStore } from '../store/cardStore'
import { useDeckStore } from '../store/deckStore'
import { LeaderSelectionModal } from '../components/LeaderSelectionModal'
import { DeckStats } from '../components/DeckStats'
import { CompactCardList } from '../components/CompactCardList'
import { DeckSelector } from '../components/DeckSelector'
import { CardPreview } from '../components/CardPreview'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface LeaderCard {
  id: string
  id_normal: string
  name: string
  colors: string[]
  power?: number
  life?: number
  effect?: string
  image_link?: string
}

export function DeckBuilderPage() {
  const navigate = useNavigate()

  // Zustand stores
  const { cards, loading: cardsLoading, filters, fetchCards, setFilters, getFilteredCards } = useCardStore()
  const {
    decks,
    currentDeck,
    createDeck,
    updateDeck,
    deleteDeck,
    setCurrentDeck,
    addCardToDeck,
    removeCardFromDeck,
    getDeckCardCount
  } = useDeckStore()

  // Local UI state
  const [showLeaderModal, setShowLeaderModal] = useState(false)
  const [selectedLeader, setSelectedLeader] = useState<LeaderCard | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [isEditingName, setIsEditingName] = useState(false)
  const [editingName, setEditingName] = useState('')

  const colors = ['Red', 'Blue', 'Green', 'Purple', 'Yellow', 'Black']

  // Fetch cards on mount
  useEffect(() => {
    fetchCards()
  }, [fetchCards])

  // Fetch leader data when loading a deck
  const fetchLeaderData = async (leaderId: string): Promise<LeaderCard | null> => {
    try {
      const response = await fetch(`${API_BASE}/api/cards/${leaderId}`)
      if (!response.ok) return null
      const data = await response.json()
      return {
        id: data.id,
        id_normal: data.id_normal,
        name: data.name,
        colors: data.colors || [],
        power: data.power,
        life: data.life,
        effect: data.effect,
        image_link: data.image_link,
      }
    } catch {
      return null
    }
  }

  // Create card database map for quick lookups
  const cardDatabase = useMemo(() => {
    const map = new Map()
    cards.forEach(card => map.set(card.id, card))
    return map
  }, [cards])

  // Get filtered cards (excluding leaders for the main browser)
  const filteredCards = useMemo(() => {
    let result = getFilteredCards().filter(card => card.type !== 'LEADER')

    // Apply local search on top of color filter
    if (searchQuery && searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      result = result.filter(card =>
        card.name.toLowerCase().includes(query) ||
        card.id.toLowerCase().includes(query)
      )
    }

    return result
  }, [getFilteredCards, searchQuery, filters])

  // Handle leader selection
  const handleSelectLeader = (leader: LeaderCard) => {
    setSelectedLeader(leader)
    setShowLeaderModal(false)

    // Extract leader's colors and set filter
    const leaderColors = leader.colors || []
    setFilters({ colors: leaderColors })

    // Create a new deck with this leader if no current deck or different leader
    if (!currentDeck || currentDeck.leaderId !== leader.id) {
      createDeck('New Deck', leader.id)
    }
  }

  // Handle adding card to deck
  const handleAddCard = (cardId: string) => {
    if (!selectedLeader) {
      setShowLeaderModal(true)
      return
    }
    addCardToDeck(cardId)
  }

  // Handle color filter toggle
  const handleColorToggle = (color: string) => {
    const currentColors = filters.colors || []
    const newColors = currentColors.includes(color)
      ? currentColors.filter(c => c !== color)
      : [...currentColors, color]
    setFilters({ colors: newColors })
  }

  // Handle loading a saved deck
  const handleSelectDeck = async (deck: typeof decks[0]) => {
    setCurrentDeck(deck)

    // Fetch and set the leader data
    const leader = await fetchLeaderData(deck.leaderId)
    if (leader) {
      setSelectedLeader(leader)
      setFilters({ colors: leader.colors || [] })
    }
  }

  // Handle creating a new deck
  const handleNewDeck = () => {
    setCurrentDeck(null)
    setSelectedLeader(null)
    setFilters({ colors: [] })
    setShowLeaderModal(true)
  }

  // Handle deleting a deck
  const handleDeleteDeck = (deckId: string) => {
    deleteDeck(deckId)
    if (currentDeck?.id === deckId) {
      setCurrentDeck(null)
      setSelectedLeader(null)
      setFilters({ colors: [] })
    }
  }

  // Handle inline name editing
  const handleStartEditName = () => {
    if (currentDeck) {
      setEditingName(currentDeck.name)
      setIsEditingName(true)
    }
  }

  const handleSaveInlineName = () => {
    if (currentDeck && editingName.trim()) {
      updateDeck({ ...currentDeck, name: editingName.trim() })
    }
    setIsEditingName(false)
  }

  const handleCancelEditName = () => {
    setIsEditingName(false)
    setEditingName('')
  }

  const deckCardCount = getDeckCardCount()

  return (
    <div className="h-screen flex relative overflow-hidden">
      {/* Background Image */}
      <div
        className="fixed inset-0 z-0"
        style={{
          backgroundImage: 'url(/images/water7-bg.png)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          filter: 'blur(9px)',
          opacity: 0.4,
        }}
      />
      {/* Left Sidebar - Decks & Stats */}
      <div className="w-72 bg-stone-800/90 border-r border-amber-900/50 flex flex-col relative z-10 h-full">
        <div className="p-4 border-b border-amber-900/50">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-amber-200/70 hover:text-amber-100 transition-colors mb-4"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to Home
          </button>
          <h1 className="text-xl font-bold text-white">Deck Builder</h1>
        </div>

        {/* Saved Decks */}
        <div className="p-4 border-b border-amber-900/50">
          <h3 className="text-sm font-semibold text-amber-200/60 mb-3">MY DECKS</h3>
          <DeckSelector
            decks={decks}
            currentDeckId={currentDeck?.id}
            onSelectDeck={handleSelectDeck}
            onDeleteDeck={handleDeleteDeck}
            onNewDeck={handleNewDeck}
          />
        </div>

        {/* Deck Stats */}
        <div className="flex-1 overflow-y-auto p-4">
          <h3 className="text-sm font-semibold text-amber-200/60 mb-3">DECK STATS</h3>
          {selectedLeader ? (
            <DeckStats
              deckCards={currentDeck?.cards || []}
              cardDatabase={cardDatabase}
            />
          ) : (
            <div className="text-center text-amber-200/40 py-8 text-sm">
              Select a leader to see deck stats
            </div>
          )}
        </div>
      </div>

      {/* Main Area - Deck Cards with Search */}
      <div className="flex-1 flex flex-col bg-stone-900/90 relative z-10 h-full overflow-hidden">
        {/* Deck Header */}
        <div className="p-4 bg-stone-800/90 border-b border-amber-900/50 flex items-center justify-between">
          <div>
            {isEditingName ? (
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={editingName}
                  onChange={(e) => setEditingName(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleSaveInlineName()
                    if (e.key === 'Escape') handleCancelEditName()
                  }}
                  autoFocus
                  className="text-xl font-bold text-white bg-stone-700 border border-amber-500 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
                <button
                  onClick={handleSaveInlineName}
                  className="p-1 text-green-400 hover:text-green-300 transition-colors"
                >
                  <Check className="w-5 h-5" />
                </button>
                <button
                  onClick={handleCancelEditName}
                  className="p-1 text-red-400 hover:text-red-300 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            ) : (
              <h2
                onClick={handleStartEditName}
                className="text-xl font-bold text-white cursor-pointer hover:text-amber-200 transition-colors flex items-center gap-2 group"
              >
                {currentDeck?.name || 'New Deck'}
                <Pencil className="w-4 h-4 opacity-0 group-hover:opacity-50 transition-opacity" />
              </h2>
            )}
            <p className="text-sm text-amber-200/60">
              {deckCardCount} / 50 cards
            </p>
          </div>
        </div>

        {/* Deck Cards Section */}
        <div className="flex-1 flex flex-col overflow-hidden p-3 gap-3">
          {selectedLeader ? (
            <>
              {/* Deck Cards with Leader - Fixed height section */}
              <div className="flex-shrink-0">
                <div className="flex gap-3 items-start">
                  {/* Leader Card */}
                  <motion.div
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => setShowLeaderModal(true)}
                    className="flex-shrink-0 w-16 cursor-pointer"
                  >
                    <div className="aspect-[2.5/3.5] rounded-lg overflow-hidden border-2 border-yellow-500">
                      {selectedLeader.image_link ? (
                        <div className="w-full h-full relative group">
                          <img
                            src={selectedLeader.image_link}
                            alt={selectedLeader.name}
                            className="w-full h-full object-cover"
                          />
                          <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                            <span className="text-white text-[8px] font-medium">Change</span>
                          </div>
                        </div>
                      ) : (
                        <div className="w-full h-full bg-gradient-to-br from-yellow-600 to-yellow-800 flex flex-col items-center justify-center p-1">
                          <span className="text-yellow-200 text-[8px]">{selectedLeader.id}</span>
                          <span className="text-white text-[8px] text-center font-medium">{selectedLeader.name}</span>
                        </div>
                      )}
                    </div>
                    <div className="text-center mt-0.5 text-[10px] text-yellow-400 font-medium">LEADER</div>
                  </motion.div>

                  {/* Deck Cards */}
                  <div className="flex-1 min-w-0">
                    <CompactCardList
                      deckCards={currentDeck?.cards || []}
                      cardDatabase={cardDatabase}
                      onRemoveCard={removeCardFromDeck}
                    />
                  </div>
                </div>
              </div>

              {/* Card Search & Browser - Flexible height section */}
              <div className="flex-1 flex flex-col overflow-hidden">
                {/* Search */}
                <div className="flex-shrink-0 mb-2">
                  <div className="flex gap-2 items-center">
                    <div className="relative flex-1">
                      <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-4 h-4 text-amber-200/50" />
                      <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="Search by ID or name..."
                        className="w-full bg-stone-700 border border-amber-900/50 rounded-lg pl-8 pr-3 py-1.5 text-sm text-white placeholder-amber-200/40 focus:border-amber-500 focus:outline-none"
                      />
                    </div>
                    {/* Color Filters */}
                    <div className="flex gap-1">
                      {colors.map((color) => {
                        const isSelected = filters.colors?.includes(color) ?? false
                        return (
                          <button
                            key={color}
                            onClick={() => handleColorToggle(color)}
                            className={`px-2 py-1 rounded text-xs transition-colors ${
                              isSelected
                                ? 'text-white'
                                : 'bg-stone-700 text-amber-200/50 hover:text-white'
                            }`}
                            style={{
                              backgroundColor: isSelected ? getColorHex(color) : undefined,
                            }}
                          >
                            {color.charAt(0)}
                          </button>
                        )
                      })}
                    </div>
                  </div>
                </div>

                {/* Card Grid - Scrollable */}
                <div className="flex-1 overflow-y-auto">
                  {cardsLoading ? (
                    <div className="flex items-center justify-center h-32">
                      <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-amber-400"></div>
                    </div>
                  ) : filteredCards.length === 0 ? (
                    <div className="text-center text-amber-200/40 py-8">
                      No cards match your filters
                    </div>
                  ) : (
                    <div className="grid grid-cols-6 md:grid-cols-8 lg:grid-cols-10 xl:grid-cols-12 2xl:grid-cols-14 gap-1.5">
                      {filteredCards.slice(0, 100).map((card) => (
                        <CardPreview
                          key={card.id}
                          imageUrl={card.imageUrl}
                          name={card.name}
                          id={card.id}
                        >
                          <motion.div
                            whileTap={{ scale: 0.98 }}
                            onClick={() => handleAddCard(card.id)}
                            className="aspect-[2.5/3.5] rounded border border-amber-900/50 hover:border-amber-500 cursor-pointer transition-colors overflow-hidden"
                          >
                            {card.imageUrl ? (
                              <img
                                src={card.imageUrl}
                                alt={card.name}
                                className="w-full h-full object-cover"
                                loading="lazy"
                              />
                            ) : (
                              <div className="w-full h-full bg-gradient-to-br from-stone-600 to-stone-800 flex flex-col items-center justify-center p-0.5">
                                <span className="text-amber-200/50 text-[6px]">{card.id}</span>
                                <span className="text-white text-[6px] text-center">{card.name}</span>
                              </div>
                            )}
                          </motion.div>
                        </CardPreview>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </>
          ) : (
            <div className="flex gap-3 items-start">
              {/* Empty Leader Slot */}
              <motion.div
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setShowLeaderModal(true)}
                className="flex-shrink-0 w-16 cursor-pointer"
              >
                <div className="aspect-[2.5/3.5] rounded-lg overflow-hidden border-2 border-dashed border-amber-900/50 hover:border-yellow-500 bg-stone-700/50 flex flex-col items-center justify-center transition-colors">
                  <Plus className="w-5 h-5 text-amber-200/40" />
                  <span className="text-amber-200/40 text-[8px] mt-1">Select</span>
                </div>
                <div className="text-center mt-0.5 text-[10px] text-amber-200/40 font-medium">LEADER</div>
              </motion.div>

              {/* Empty State Message */}
              <div className="flex-1 flex flex-col items-center justify-center py-4 text-amber-200/40">
                <p className="text-sm">Select a leader to start building your deck</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Leader Selection Modal */}
      <LeaderSelectionModal
        isOpen={showLeaderModal}
        onClose={() => setShowLeaderModal(false)}
        onSelectLeader={handleSelectLeader}
      />
    </div>
  )
}

function getColorHex(color: string): string {
  const colors: Record<string, string> = {
    Red: '#E53935',
    Blue: '#1E88E5',
    Green: '#43A047',
    Purple: '#8E24AA',
    Yellow: '#FDD835',
    Black: '#424242',
  }
  return colors[color] || '#666'
}
