import { useNavigate } from 'react-router-dom'
import { Swords, Users, Bot, Layers, Play } from 'lucide-react'

export function HomePage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h1 className="font-display text-6xl md:text-8xl text-white mb-4 tracking-wider">
          OPTCG
          <span className="text-op-red"> SIMULATOR</span>
        </h1>
        <p className="text-xl text-slate-400 max-w-2xl mx-auto">
          Play the One Piece Trading Card Game online against AI trained on millions of games,
          or challenge your friends in real-time matches.
        </p>
      </div>

      {/* Game Mode Cards */}
      <div className="grid md:grid-cols-2 gap-6 max-w-4xl w-full">
        {/* VS AI */}
        <button
          onClick={() => navigate('/game/new-ai')}
          className="group relative bg-gradient-to-br from-slate-800 to-slate-900 p-8 rounded-2xl border border-slate-700 hover:border-op-red transition-all duration-300 text-left"
        >
          <div className="absolute inset-0 bg-gradient-to-br from-op-red/10 to-transparent rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity" />
          <Bot className="w-12 h-12 text-op-red mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">Play vs AI</h2>
          <p className="text-slate-400">
            Challenge the Vinsmoke AI, trained on 1M+ self-play games using AlphaZero techniques.
          </p>
          <div className="mt-4 flex gap-2">
            <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm">Easy</span>
            <span className="px-3 py-1 bg-yellow-500/20 text-yellow-400 rounded-full text-sm">Medium</span>
            <span className="px-3 py-1 bg-red-500/20 text-red-400 rounded-full text-sm">Hard</span>
          </div>
        </button>

        {/* VS Player */}
        <button
          onClick={() => navigate('/lobby')}
          className="group relative bg-gradient-to-br from-slate-800 to-slate-900 p-8 rounded-2xl border border-slate-700 hover:border-op-blue transition-all duration-300 text-left"
        >
          <div className="absolute inset-0 bg-gradient-to-br from-op-blue/10 to-transparent rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity" />
          <Users className="w-12 h-12 text-op-blue mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">Play vs Friend</h2>
          <p className="text-slate-400">
            Create a room and share the code with a friend to play together in real-time.
          </p>
          <div className="mt-4">
            <span className="px-3 py-1 bg-op-blue/20 text-op-blue rounded-full text-sm">
              Room Codes
            </span>
          </div>
        </button>

        {/* Deck Builder */}
        <button
          onClick={() => navigate('/deck-builder')}
          className="group relative bg-gradient-to-br from-slate-800 to-slate-900 p-8 rounded-2xl border border-slate-700 hover:border-op-purple transition-all duration-300 text-left"
        >
          <div className="absolute inset-0 bg-gradient-to-br from-op-purple/10 to-transparent rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity" />
          <Layers className="w-12 h-12 text-op-purple mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">Deck Builder</h2>
          <p className="text-slate-400">
            Build and customize your deck from the complete card database.
          </p>
          <div className="mt-4">
            <span className="px-3 py-1 bg-op-purple/20 text-op-purple rounded-full text-sm">
              4000+ Cards
            </span>
          </div>
        </button>

        {/* Playtest */}
        <button
          onClick={() => navigate('/playtest')}
          className="group relative bg-gradient-to-br from-slate-800 to-slate-900 p-8 rounded-2xl border border-slate-700 hover:border-op-green transition-all duration-300 text-left"
        >
          <div className="absolute inset-0 bg-gradient-to-br from-op-green/10 to-transparent rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity" />
          <Play className="w-12 h-12 text-op-green mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">Playtest</h2>
          <p className="text-slate-400">
            Practice with your deck by playing both sides. Perfect for testing strategies.
          </p>
          <div className="mt-4">
            <span className="px-3 py-1 bg-op-green/20 text-op-green rounded-full text-sm">
              Solo Practice
            </span>
          </div>
        </button>
      </div>

      {/* Footer */}
      <div className="mt-12 text-center text-slate-500 text-sm">
        <p>Powered by Vinsmoke Engine - AI trained with AlphaZero self-play</p>
        <p className="mt-1">Not affiliated with Bandai or One Piece</p>
      </div>
    </div>
  )
}
