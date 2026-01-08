# OPTCG Monorepo - Context for Claude Sessions

This document captures the architectural decisions, history, and implementation details for this project. Use this to quickly understand the codebase.

---

## Project History

This monorepo was created by combining two separate projects:

1. **Vinsmoke Engine** (`A:\Programming Projects\Vinsmoke Engine`)
   - Purpose: AI training for One Piece TCG using MCTS + neural networks
   - Tech: Python, PyTorch, FastAPI
   - Key feature: Immutable game state design (optimal for RL training)

2. **OPTCG Simulator** (`A:\Programming Projects\OPTCG Simulator`)
   - Purpose: Multiplayer web game with room system
   - Tech: React + TypeScript + Vite (frontend), FastAPI + Socket.IO (backend)
   - Key feature: Real-time multiplayer via WebSockets

---

## Key Finding: 95% Game Logic Overlap

Analysis revealed both projects implement nearly identical game rules:
- DON pool management (MAX_DON=10, DON_PER_TURN=2)
- Life damage & trigger system
- Combat phases (BLOCKER_STEP → COUNTER_STEP → DAMAGE_STEP)
- Phase transitions (REFRESH → DRAW → DON → MAIN → END)
- Card effects and keywords (Rush, Blocker, Banish, Double Attack)

The main architectural difference:
- **Vinsmoke**: Immutable state (returns new objects) - better for AI/MCTS
- **OPTCG Simulator**: Mutable state (modifies in-place) - easier for API

**Solution**: Created `optcg_engine` package with adapters for both use cases.

---

## Architecture Overview

```
optcg-monorepo/
├── packages/
│   ├── game-engine/          # Shared Python package
│   │   └── optcg_engine/
│   │       ├── core/         # Immutable GameState, Actions, Phases
│   │       ├── models/       # Card, Player models
│   │       ├── effects/      # Effect parsing & resolution
│   │       └── adapters/     # MutableGameState wrapper for API
│   │
│   ├── training/             # AI Training Service
│   │   ├── ai/               # Neural network, MCTS, state encoder
│   │   ├── api/              # FastAPI + Prometheus metrics
│   │   └── train_parallel.py # Multi-worker training script
│   │
│   └── simulator/            # Web Application
│       ├── backend/          # FastAPI + Socket.IO
│       └── frontend/         # React + Vite + Zustand
│
├── monitoring/               # Prometheus + Grafana configs
├── checkpoints/              # AI model checkpoints
└── docker-compose*.yml       # Container orchestration
```

---

## Container Architecture

### Network Segmentation
- `frontend-net`: Public-facing (simulator frontend/backend)
- `backend-net`: Internal only (no external access)
- `monitoring-net`: Prometheus/Grafana isolated

### Services
| Service | Port | Description |
|---------|------|-------------|
| training | 8000 | AI training API + metrics |
| simulator-backend | 8001 | Game server + WebSocket |
| simulator-frontend | 3000 (dev) / 80 (prod) | React app |
| prometheus | 9090 | Metrics collection |
| grafana | 3001 | Dashboards (admin/optcg) |
| cadvisor | - | Container metrics |
| node-exporter | - | Host metrics |

### Best Practices Applied
1. **Multi-stage Docker builds** - Separate builder/dev/prod stages
2. **Non-root users** - `trainer` and `simulator` users in containers
3. **Health checks** - All services have `/health` endpoints
4. **Resource limits** - Memory and CPU limits on all containers
5. **Read-only mounts** - Config files mounted as `:ro`

---

## Key Files

### Game Engine
- `packages/game-engine/optcg_engine/game_engine.py` - Core game logic, Player class
- `packages/game-engine/optcg_engine/core/game_state.py` - Immutable state
- `packages/game-engine/optcg_engine/core/actions.py` - Action validation
- `packages/game-engine/optcg_engine/effects/` - Effect system (parser, resolver, hardcoded)

### Training
- `packages/training/ai/network.py` - AlphaZero-style neural network
- `packages/training/ai/mcts.py` - Monte Carlo Tree Search
- `packages/training/ai/state_encoder.py` - Game state → tensor encoding
- `packages/training/train_parallel.py` - Multi-worker training loop
- `packages/training/api/routes/training.py` - Training control API

### Simulator
- `packages/simulator/backend/main.py` - FastAPI + Socket.IO app
- `packages/simulator/backend/game/engine.py` - Mutable game engine (TO BE REPLACED with shared)
- `packages/simulator/backend/game/manager.py` - Room/game management
- `packages/simulator/backend/realtime/socket_handlers.py` - WebSocket events
- `packages/simulator/frontend/src/store/` - Zustand state stores

---

## Commands Reference

### Start Services
```bash
# Full stack
docker compose up -d

# Training only
docker compose -f docker-compose.train.yml up -d

# Development mode (hot reload)
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### Training API
```bash
# Start training
curl -X POST "http://localhost:8000/api/training/start" \
  -H "Content-Type: application/json" \
  -d '{"num_workers": 8, "games_per_iteration": 100}'

# Check status
curl http://localhost:8000/api/training/status

# Stop training
curl -X POST http://localhost:8000/api/training/stop
```

### Development
```bash
# Install game engine locally
cd packages/game-engine && pip install -e .

# Build specific container
docker compose build training
```

---

## Future Work / TODOs

1. **Unify game engines**: Replace `packages/simulator/backend/game/engine.py` with imports from `optcg_engine`
2. **Update simulator imports**: Change simulator backend to use `from optcg_engine import ...`
3. **Add adapter usage**: Use `MutableGameState` adapter in simulator for API compatibility
4. **Shared effect system**: Ensure both training and simulator use same effect resolution
5. **GCP deployment**: Set up Cloud Run or GKE for production deployment

---

## Important Constants

```python
# Game rules (shared across both engines)
MAX_DON = 10
DON_PER_TURN = 2
STARTING_DON_P1 = 1
STARTING_DON_P2 = 2
HAND_LIMIT = 7
MAX_FIELD_CHARACTERS = 5

# Leader attack restrictions
# P1 can attack with leader starting turn 3
# P2 can attack with leader starting turn 4
```

---

## Original Project Locations

The original projects still exist at:
- `A:\Programming Projects\Vinsmoke Engine` - Can be deleted after monorepo is verified
- `A:\Programming Projects\OPTCG Simulator` - Can be deleted after monorepo is verified

The Vinsmoke Engine was cleaned up and Dockerized in a previous session before this merge.

---

## Session Context

This monorepo was created during a Claude Code session that:
1. Explored both codebases to understand structure
2. Identified 95% game logic overlap between projects
3. Designed containerized architecture with best practices
4. Created shared game engine package with adapters
5. Set up production-ready monitoring stack
6. Migrated all code and created Docker configurations

The plan file used: `C:\Users\harsh\.claude\plans\groovy-wiggling-galaxy.md`
