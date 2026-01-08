import { Routes, Route } from 'react-router-dom'
import { HomePage } from './pages/HomePage'
import { LobbyPage } from './pages/LobbyPage'
import { GamePage } from './pages/GamePage'
import { DeckBuilderPage } from './pages/DeckBuilderPage'
import { PlaytestPage } from './pages/PlaytestPage'

function App() {
  return (
    <div className="min-h-screen bg-slate-900">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/lobby" element={<LobbyPage />} />
        <Route path="/lobby/:roomCode" element={<LobbyPage />} />
        <Route path="/game/:gameId" element={<GamePage />} />
        <Route path="/deck-builder" element={<DeckBuilderPage />} />
        <Route path="/playtest" element={<PlaytestPage />} />
      </Routes>
    </div>
  )
}

export default App
