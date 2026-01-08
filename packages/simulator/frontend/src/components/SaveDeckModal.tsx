import { useState } from 'react'
import { X } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

interface SaveDeckModalProps {
  isOpen: boolean
  onClose: () => void
  onSave: (name: string) => void
  currentName?: string
}

export function SaveDeckModal({ isOpen, onClose, onSave, currentName = '' }: SaveDeckModalProps) {
  const [deckName, setDeckName] = useState(currentName || '')

  const handleSave = () => {
    const name = deckName.trim() || 'Untitled Deck'
    onSave(name)
    setDeckName('')
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSave()
    }
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
            className="bg-stone-800 rounded-xl p-6 w-full max-w-md mx-4 border border-amber-900/50 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-white">Save Deck</h2>
              <button
                onClick={onClose}
                className="text-amber-200/60 hover:text-white transition-colors p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="mb-6">
              <label className="block text-sm text-amber-200/60 mb-2">Deck Name</label>
              <input
                type="text"
                value={deckName}
                onChange={(e) => setDeckName(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Enter deck name..."
                className="w-full bg-stone-700 border border-amber-900/50 rounded-lg px-4 py-3 text-white placeholder-amber-200/40 focus:border-amber-500 focus:outline-none"
                autoFocus
              />
            </div>

            <div className="flex gap-3">
              <button
                onClick={onClose}
                className="flex-1 px-4 py-2 bg-stone-700 hover:bg-stone-600 text-white rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                className="flex-1 px-4 py-2 bg-amber-700 hover:bg-amber-600 text-white rounded-lg transition-colors font-medium"
              >
                Save Deck
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
