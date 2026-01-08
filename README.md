# OPTCG Monorepo

Unified platform for One Piece TCG AI training and web simulation.

## Architecture

```
optcg-monorepo/
├── packages/
│   ├── game-engine/    # Shared game logic (Python package)
│   ├── training/       # AI training with MCTS + neural networks
│   └── simulator/      # Multiplayer web app (React + FastAPI)
├── monitoring/         # Prometheus + Grafana configuration
├── checkpoints/        # AI model checkpoints
└── logs/               # Centralized logging
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- NVIDIA GPU + Container Toolkit (for training)

### Full Stack (All Services)
```bash
docker compose up -d
```

Access:
- **Simulator**: http://localhost:3000
- **Training API**: http://localhost:8000
- **Grafana**: http://localhost:3001 (admin/optcg)
- **Prometheus**: http://localhost:9090

### Training Only
```bash
docker compose -f docker-compose.train.yml up -d
```

### Development Mode (Hot Reload)
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

## Training Commands

### Start Training
```bash
curl -X POST "http://localhost:8000/api/training/start" \
  -H "Content-Type: application/json" \
  -d '{"num_workers": 8, "games_per_iteration": 100}'
```

### Check Status
```bash
curl http://localhost:8000/api/training/status
```

### Stop Training
```bash
curl -X POST http://localhost:8000/api/training/stop
```

## Project Structure

### Game Engine (`packages/game-engine/`)
Shared Python package with core game logic:
- `optcg_engine/core/` - Immutable game state, actions, phases
- `optcg_engine/models/` - Card, Player data models
- `optcg_engine/effects/` - Effect parsing and resolution
- `optcg_engine/adapters/` - Mutable wrappers for API compatibility

### Training (`packages/training/`)
AI training pipeline:
- `ai/` - Neural network (AlphaZero-style) and MCTS
- `api/` - FastAPI server with Prometheus metrics
- `train_parallel.py` - Multi-worker training script

### Simulator (`packages/simulator/`)
Web application:
- `backend/` - FastAPI + Socket.IO for real-time multiplayer
- `frontend/` - React + TypeScript + Vite + TailwindCSS

## Monitoring

### Grafana Dashboards
Pre-configured dashboards for:
- Training progress (iterations, loss, win rate)
- Container resources (CPU, memory, GPU)
- System health (disk, network)

### Prometheus Alerts
Automatic alerts for:
- Service down
- Training stalled
- High resource usage
- Low disk space

## GCP Deployment

1. Create VM with GPU:
```bash
gcloud compute instances create optcg-train \
  --zone=us-central1-a \
  --machine-type=n1-standard-8 \
  --accelerator=type=nvidia-tesla-t4,count=1 \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=100GB \
  --preemptible
```

2. Install Docker and NVIDIA Container Toolkit

3. Clone and run:
```bash
git clone <repo> && cd optcg-monorepo
docker compose -f docker-compose.train.yml up -d
```

## Configuration

### Environment Variables
Copy `.env.example` to `.env` and customize:
- `GRAFANA_USER` / `GRAFANA_PASSWORD` - Dashboard credentials
- `LOG_LEVEL` - Logging verbosity (DEBUG, INFO, WARNING, ERROR)

### Training Parameters
Configured via API:
- `num_workers` - Parallel game workers (default: 8)
- `games_per_iteration` - Games per training batch (default: 100)
- `mcts_simulations` - MCTS simulations per move (default: 100)

## Development

### Install Game Engine Locally
```bash
cd packages/game-engine
pip install -e .
```

### Run Tests
```bash
cd packages/game-engine
python -m pytest tests/
```

### Build Individual Containers
```bash
docker compose build training
docker compose build simulator-backend
docker compose build simulator-frontend
```

## License

Private project - All rights reserved
