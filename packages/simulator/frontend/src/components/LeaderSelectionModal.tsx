import { useState, useEffect } from 'react'
import { Search, X } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

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

interface LeaderSelectionModalProps {
  isOpen: boolean
  onClose: () => void
  onSelectLeader: (leader: LeaderCard) => void
}

export function LeaderSelectionModal({ isOpen, onClose, onSelectLeader }: LeaderSelectionModalProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [leaders, setLeaders] = useState<LeaderCard[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (isOpen) {
      fetchLeaders()
    }
  }, [isOpen])

  const fetchLeaders = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE}/api/cards?card_type=LEADER&limit=500`)
      const data = await response.json()
      setLeaders(data.cards || [])
    } catch (error) {
      console.error('Failed to fetch leaders:', error)
    }
    setLoading(false)
  }

  const filteredLeaders = leaders.filter(leader => {
    if (!searchQuery) return true
    const query = searchQuery.toLowerCase()
    return leader.name.toLowerCase().includes(query) || leader.id.toLowerCase().includes(query)
  })

  const handleSelect = (leader: LeaderCard) => {
    onSelectLeader(leader)
    setSearchQuery('')
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/80 flex items-center justify-center z-50"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="bg-slate-800 rounded-2xl p-6 max-w-5xl w-full mx-4 max-h-[85vh] flex flex-col border border-slate-600 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold text-white">Select Leader</h2>
              <button
                onClick={onClose}
                className="text-slate-400 hover:text-white transition-colors p-1"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Search */}
            <div className="relative mb-4">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by card ID (OP13-096) or name (Ace)..."
                className="w-full bg-slate-700 border border-slate-600 rounded-lg pl-10 pr-4 py-3 text-white placeholder-slate-400 focus:border-blue-500 focus:outline-none"
                autoFocus
              />
            </div>

            {/* Leader Grid */}
            <div className="flex-1 overflow-y-auto">
              {loading ? (
                <div className="flex items-center justify-center h-48">
                  <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-yellow-400"></div>
                </div>
              ) : filteredLeaders.length === 0 ? (
                <div className="flex items-center justify-center h-48 text-slate-400">
                  {searchQuery ? 'No leaders found matching your search' : 'No leaders available'}
                </div>
              ) : (
                <div className="grid grid-cols-4 md:grid-cols-5 lg:grid-cols-6 xl:grid-cols-7 gap-3">
                  {filteredLeaders.map(leader => (
                    <motion.div
                      key={leader.id}
                      whileHover={{ scale: 1.05, y: -4 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => handleSelect(leader)}
                      className="cursor-pointer rounded-lg overflow-hidden border-2 border-transparent hover:border-yellow-400 transition-colors"
                    >
                      {leader.image_link ? (
                        <img
                          src={leader.image_link}
                          alt={leader.name}
                          className="w-full aspect-[2.5/3.5] object-cover"
                          loading="lazy"
                        />
                      ) : (
                        <div className="w-full aspect-[2.5/3.5] bg-gradient-to-br from-slate-600 to-slate-800 flex flex-col items-center justify-center p-2">
                          <div className="text-xs text-slate-400">{leader.id}</div>
                          <div className="text-sm text-white text-center font-medium mt-1">{leader.name}</div>
                          <div className="text-xs text-yellow-400 mt-1">
                            {leader.colors?.join('/')}
                          </div>
                        </div>
                      )}
                    </motion.div>
                  ))}
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="mt-4 pt-4 border-t border-slate-700 text-center text-sm text-slate-400">
              {filteredLeaders.length} leaders available
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
