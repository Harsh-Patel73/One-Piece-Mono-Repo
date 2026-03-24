# OPTCG Simulator Frontend - Claude Code Context

## Project Overview
This is the frontend for the One Piece Trading Card Game (OPTCG) Simulator. It's a React + TypeScript application built with Vite.

## Tech Stack
- **Framework:** React 18.2.0 with React Router v6
- **Build Tool:** Vite 5.x
- **Language:** TypeScript 5.2
- **Styling:** TailwindCSS 3.3 with custom One Piece themed colors
- **State Management:** Zustand 4.4
- **Real-time:** Socket.IO Client 4.7
- **Animations:** Framer Motion 10.x

## Directory Structure
```
src/
├── components/     # Reusable UI components (Card, GameBoard, DeckSelector, etc.)
├── hooks/          # Custom React hooks (useSocket for WebSocket connections)
├── pages/          # Route pages (HomePage, LobbyPage, GamePage, DeckBuilderPage, PlaytestPage)
├── store/          # Zustand state stores
│   ├── cardStore.ts      # Card data from API
│   ├── deckStore.ts      # Deck building state
│   ├── gameStore.ts      # Active game state
│   ├── lobbyStore.ts     # Multiplayer lobby
│   └── playtestStore.ts  # Local playtest mode
├── App.tsx         # Root component with routing
├── main.tsx        # Entry point
└── index.css       # Global styles + Tailwind imports
```

## Key Commands
```bash
# Development server (port 3000)
npm run dev

# Production build
npm run build

# Preview production build
npm run preview
```

## API Configuration
- Vite dev server proxies `/api` and `/socket.io` to `http://localhost:8080` (backend)
- The `cardStore.ts` uses `VITE_API_URL` env var or defaults to `http://localhost:8000`
- **Note:** There's currently a port mismatch - proxy uses 8080, cardStore defaults to 8000

## Routes
| Path | Page | Description |
|------|------|-------------|
| `/` | HomePage | Landing page |
| `/lobby` | LobbyPage | Multiplayer lobby with room codes |
| `/lobby/:roomCode` | LobbyPage | Join specific room |
| `/game/:gameId` | GamePage | Active multiplayer game |
| `/deck-builder` | DeckBuilderPage | Build and save decks |
| `/playtest` | PlaytestPage | Solo playtest mode |

## State Stores (Zustand)

### cardStore
- Fetches all card data from backend API
- Provides filtering (by color, type, cost, power, search)
- Used by DeckBuilder and Playtest

### deckStore
- Manages deck building (add/remove cards, save/load)
- Persists to localStorage and backend

### playtestStore
- Full game state for solo playtesting
- Manages both players, combat, effects, DON system
- Purely client-side, no backend needed once cards loaded

### gameStore
- Multiplayer game state synced via Socket.IO

### lobbyStore
- Room creation, joining, player management

## Styling Conventions
- Use Tailwind utility classes
- Custom One Piece color palette: `op-red`, `op-blue`, `op-green`, `op-purple`, `op-yellow`, `op-black`
- Dark theme using `stone-*` shades for backgrounds
- Amber accents for card game theming

## Common Tasks

### Adding a new page
1. Create component in `src/pages/`
2. Add route in `src/App.tsx`

### Adding state
1. Create or modify store in `src/store/`
2. Use `create` from Zustand
3. Import store hook in components

### Working with cards
- Card images come from `imageUrl` / `image_link` field
- Card data structure defined in `cardStore.ts`
- PlaytestCard extends with `instanceId`, `isResting`, `attachedDon`

## Dependencies on Backend
The frontend requires the backend for:
- Card data fetching (`/api/cards`)
- Deck save/load (`/api/decks`)
- Multiplayer games (Socket.IO)

Playtest mode works offline once card data is cached.
