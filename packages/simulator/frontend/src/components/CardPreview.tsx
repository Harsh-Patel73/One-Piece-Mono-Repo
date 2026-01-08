import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { createPortal } from 'react-dom'

interface CardPreviewProps {
  children: React.ReactNode
  imageUrl?: string
  name?: string
  id?: string
}

const PREVIEW_WIDTH = 280
const PREVIEW_HEIGHT = PREVIEW_WIDTH * (3.5 / 2.5) // Maintain card aspect ratio

export function CardPreview({ children, imageUrl, name, id }: CardPreviewProps) {
  const [isHovered, setIsHovered] = useState(false)
  const [anchorStyle, setAnchorStyle] = useState<React.CSSProperties>({})

  const handleMouseEnter = (e: React.MouseEvent) => {
    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()
    const viewportWidth = window.innerWidth
    const viewportHeight = window.innerHeight

    const cardCenterX = rect.left + rect.width / 2
    const cardCenterY = rect.top + rect.height / 2

    // Determine horizontal position - show on opposite side if near edge
    const isOnLeftHalf = cardCenterX < viewportWidth / 2
    const isNearTop = cardCenterY < viewportHeight / 2

    // Calculate position to keep fully on screen
    let style: React.CSSProperties = {}

    if (isOnLeftHalf) {
      // Card is on left side, show preview to the right
      style.left = Math.min(rect.right + 16, viewportWidth - PREVIEW_WIDTH - 16)
    } else {
      // Card is on right side, show preview to the left
      style.right = Math.min(viewportWidth - rect.left + 16, viewportWidth - PREVIEW_WIDTH - 16)
    }

    if (isNearTop) {
      // Card is near top, align preview top with card top
      style.top = Math.max(16, Math.min(rect.top, viewportHeight - PREVIEW_HEIGHT - 16))
    } else {
      // Card is near bottom, align preview bottom with card bottom
      style.bottom = Math.max(16, Math.min(viewportHeight - rect.bottom, viewportHeight - PREVIEW_HEIGHT - 16))
    }

    setAnchorStyle(style)
    setIsHovered(true)
  }

  return (
    <div
      className="relative"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={() => setIsHovered(false)}
    >
      {children}

      {isHovered && createPortal(
        <AnimatePresence>
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.12 }}
            className="fixed z-[100] pointer-events-none"
            style={{
              ...anchorStyle,
              width: `${PREVIEW_WIDTH}px`
            }}
          >
            <div className="bg-stone-900 rounded-xl shadow-2xl border-2 border-amber-700/50 overflow-hidden">
              {imageUrl ? (
                <img
                  src={imageUrl}
                  alt={name || 'Card preview'}
                  className="w-full aspect-[2.5/3.5] object-cover"
                />
              ) : (
                <div className="w-full aspect-[2.5/3.5] bg-gradient-to-br from-stone-700 to-stone-900 flex flex-col items-center justify-center p-4">
                  <span className="text-amber-200/50 text-sm">{id}</span>
                  <span className="text-white text-lg text-center mt-2 font-medium">{name}</span>
                </div>
              )}
            </div>
          </motion.div>
        </AnimatePresence>,
        document.body
      )}
    </div>
  )
}
