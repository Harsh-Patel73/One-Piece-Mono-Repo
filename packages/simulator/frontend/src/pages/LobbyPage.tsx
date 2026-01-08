import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Copy, Check, ArrowLeft, Users, Loader2 } from 'lucide-react'
import { useSocket } from '../hooks/useSocket'

export function LobbyPage() {
  const { roomCode: urlRoomCode } = useParams()
  const navigate = useNavigate()
  const { socket, connected } = useSocket()

  const [playerName, setPlayerName] = useState('')
  const [roomCode, setRoomCode] = useState(urlRoomCode || '')
  const [joinCode, setJoinCode] = useState('')
  const [copied, setCopied] = useState(false)
  const [players, setPlayers] = useState<Array<{name: string, is_host: boolean, ready: boolean}>>([])
  const [inRoom, setInRoom] = useState(false)
  const [isHost, setIsHost] = useState(false)

  useEffect(() => {
    if (!socket) return

    socket.on('room_created', (data) => {
      setRoomCode(data.room_code)
      setPlayers(data.players)
      setInRoom(true)
      setIsHost(true)
    })

    socket.on('player_joined', (data) => {
      setPlayers(data.players)
    })

    socket.on('player_ready', (data) => {
      setPlayers(data.players)
    })

    socket.on('player_left', () => {
      // Handle player leaving
    })

    socket.on('game_started', (data) => {
      navigate(`/game/${data.game_id}`)
    })

    socket.on('error', (data) => {
      alert(data.message)
    })

    return () => {
      socket.off('room_created')
      socket.off('player_joined')
      socket.off('player_ready')
      socket.off('player_left')
      socket.off('game_started')
      socket.off('error')
    }
  }, [socket, navigate])

  const createRoom = () => {
    if (!socket || !playerName.trim()) return
    socket.emit('create_room', { player_name: playerName })
  }

  const joinRoom = () => {
    if (!socket || !playerName.trim() || !joinCode.trim()) return
    socket.emit('join_room', { room_code: joinCode.toUpperCase(), player_name: playerName })
    setInRoom(true)
    setRoomCode(joinCode.toUpperCase())
  }

  const copyCode = () => {
    navigator.clipboard.writeText(roomCode)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const startGame = () => {
    if (!socket || !isHost) return
    socket.emit('start_game', {})
  }

  if (!connected) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-op-blue animate-spin mx-auto mb-4" />
          <p className="text-slate-400">Connecting to server...</p>
        </div>
      </div>
    )
  }

  if (!inRoom) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-8">
        <button
          onClick={() => navigate('/')}
          className="absolute top-8 left-8 flex items-center gap-2 text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          Back
        </button>

        <h1 className="font-display text-4xl text-white mb-8">Multiplayer Lobby</h1>

        <div className="w-full max-w-md space-y-6">
          {/* Player Name */}
          <div>
            <label className="block text-sm text-slate-400 mb-2">Your Name</label>
            <input
              type="text"
              value={playerName}
              onChange={(e) => setPlayerName(e.target.value)}
              placeholder="Enter your name"
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:border-op-blue focus:outline-none"
            />
          </div>

          {/* Create Room */}
          <button
            onClick={createRoom}
            disabled={!playerName.trim()}
            className="w-full bg-gradient-to-r from-op-blue to-blue-600 hover:from-blue-600 hover:to-op-blue disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-lg transition-all"
          >
            Create New Room
          </button>

          <div className="flex items-center gap-4">
            <div className="flex-1 h-px bg-slate-700" />
            <span className="text-slate-500">or</span>
            <div className="flex-1 h-px bg-slate-700" />
          </div>

          {/* Join Room */}
          <div>
            <label className="block text-sm text-slate-400 mb-2">Room Code</label>
            <input
              type="text"
              value={joinCode}
              onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
              placeholder="Enter 6-character code"
              maxLength={6}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:border-op-green focus:outline-none uppercase tracking-widest text-center text-xl"
            />
          </div>

          <button
            onClick={joinRoom}
            disabled={!playerName.trim() || joinCode.length !== 6}
            className="w-full bg-gradient-to-r from-op-green to-green-600 hover:from-green-600 hover:to-op-green disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-lg transition-all"
          >
            Join Room
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8">
      <h1 className="font-display text-4xl text-white mb-4">Room Lobby</h1>

      {/* Room Code Display */}
      <div className="bg-slate-800 rounded-xl p-6 mb-8 text-center">
        <p className="text-slate-400 text-sm mb-2">Share this code with your friend:</p>
        <div className="flex items-center justify-center gap-4">
          <span className="font-mono text-4xl text-white tracking-widest">{roomCode}</span>
          <button
            onClick={copyCode}
            className="p-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors"
          >
            {copied ? (
              <Check className="w-6 h-6 text-green-400" />
            ) : (
              <Copy className="w-6 h-6 text-slate-400" />
            )}
          </button>
        </div>
      </div>

      {/* Players */}
      <div className="w-full max-w-md bg-slate-800 rounded-xl p-6 mb-8">
        <div className="flex items-center gap-2 mb-4">
          <Users className="w-5 h-5 text-slate-400" />
          <h2 className="text-lg font-semibold text-white">Players ({players.length}/2)</h2>
        </div>
        <div className="space-y-3">
          {players.map((player, idx) => (
            <div
              key={idx}
              className="flex items-center justify-between bg-slate-700/50 rounded-lg px-4 py-3"
            >
              <div className="flex items-center gap-3">
                <div className={`w-3 h-3 rounded-full ${player.ready ? 'bg-green-400' : 'bg-slate-500'}`} />
                <span className="text-white">{player.name}</span>
                {player.is_host && (
                  <span className="px-2 py-0.5 bg-op-yellow/20 text-op-yellow rounded text-xs">
                    Host
                  </span>
                )}
              </div>
            </div>
          ))}
          {players.length < 2 && (
            <div className="flex items-center justify-center bg-slate-700/30 rounded-lg px-4 py-3 border-2 border-dashed border-slate-600">
              <span className="text-slate-500">Waiting for opponent...</span>
            </div>
          )}
        </div>
      </div>

      {/* Start Button (Host Only) */}
      {isHost && (
        <button
          onClick={startGame}
          disabled={players.length < 2}
          className="bg-gradient-to-r from-op-red to-red-600 hover:from-red-600 hover:to-op-red disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold text-xl px-12 py-4 rounded-xl transition-all"
        >
          Start Game
        </button>
      )}
      {!isHost && players.length === 2 && (
        <p className="text-slate-400">Waiting for host to start the game...</p>
      )}
    </div>
  )
}
