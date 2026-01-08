import { motion } from 'framer-motion'

interface CardProps {
  id?: string
  name?: string
  imageUrl?: string
  power?: number
  cost?: number
  color?: string[]
  rested?: boolean
  selected?: boolean
  highlighted?: boolean
  onClick?: () => void
  onRightClick?: () => void
  size?: 'sm' | 'md' | 'lg'
  showDetails?: boolean
}

const sizeClasses = {
  sm: 'w-16 h-24',
  md: 'w-24 h-32',
  lg: 'w-32 h-44',
}

export function Card({
  id,
  name,
  imageUrl,
  power,
  cost,
  color = [],
  rested = false,
  selected = false,
  highlighted = false,
  onClick,
  onRightClick,
  size = 'md',
  showDetails = false,
}: CardProps) {
  const primaryColor = color[0]?.toLowerCase() || 'slate'

  const colorClasses: Record<string, string> = {
    red: 'from-red-600 to-red-800 border-red-500',
    blue: 'from-blue-600 to-blue-800 border-blue-500',
    green: 'from-green-600 to-green-800 border-green-500',
    purple: 'from-purple-600 to-purple-800 border-purple-500',
    yellow: 'from-yellow-500 to-yellow-700 border-yellow-400',
    black: 'from-gray-700 to-gray-900 border-gray-500',
    slate: 'from-slate-600 to-slate-800 border-slate-500',
  }

  const bgClass = colorClasses[primaryColor] || colorClasses.slate

  return (
    <motion.div
      className={`
        ${sizeClasses[size]}
        rounded-lg border-2 cursor-pointer
        bg-gradient-to-br ${bgClass}
        flex flex-col items-center justify-center
        transition-all duration-200
        ${rested ? 'rotate-90' : ''}
        ${selected ? 'ring-2 ring-yellow-400 ring-offset-2 ring-offset-slate-900' : ''}
        ${highlighted ? 'ring-2 ring-blue-400 ring-offset-1 ring-offset-slate-900' : ''}
      `}
      onClick={onClick}
      onContextMenu={(e) => {
        e.preventDefault()
        onRightClick?.()
      }}
      whileHover={{ scale: 1.05, y: -4 }}
      whileTap={{ scale: 0.98 }}
    >
      {imageUrl ? (
        <img
          src={imageUrl}
          alt={name}
          className="w-full h-full object-cover rounded-md"
        />
      ) : (
        <div className="text-center p-1">
          {cost !== undefined && (
            <div className="text-xs font-bold text-white bg-black/30 rounded px-1 mb-1">
              {cost}
            </div>
          )}
          <div className="text-white text-xs font-medium truncate w-full px-1">
            {name || id || 'Card'}
          </div>
          {power !== undefined && (
            <div className="text-xs font-bold text-yellow-300 mt-1">
              {power}
            </div>
          )}
        </div>
      )}
    </motion.div>
  )
}

export function CardPlaceholder({
  size = 'md',
  label,
  onClick,
}: {
  size?: 'sm' | 'md' | 'lg'
  label?: string
  onClick?: () => void
}) {
  return (
    <div
      className={`
        ${sizeClasses[size]}
        rounded-lg border-2 border-dashed border-slate-600
        bg-slate-800/30 flex items-center justify-center
        hover:border-slate-500 hover:bg-slate-700/30
        transition-colors cursor-pointer
      `}
      onClick={onClick}
    >
      {label && <span className="text-slate-500 text-xs">{label}</span>}
    </div>
  )
}
