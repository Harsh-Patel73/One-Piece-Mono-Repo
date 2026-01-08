"""
Prometheus metrics for Vinsmoke Engine training monitoring.
"""

from prometheus_client import Gauge, Counter, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time
import json
from pathlib import Path

# Get paths
BACKEND_DIR = Path(__file__).parent.parent
TRAINING_PROGRESS_PATH = BACKEND_DIR / "training_progress.json"
CHECKPOINTS_DIR = BACKEND_DIR / "checkpoints"

# Define Prometheus metrics
training_games_total = Gauge(
    'vinsmoke_training_games_total',
    'Total number of games completed in training'
)

training_games_per_second = Gauge(
    'vinsmoke_training_games_per_second',
    'Current training throughput (games per second)'
)

training_loss_total = Gauge(
    'vinsmoke_training_loss_total',
    'Combined loss value from training'
)

training_loss_policy = Gauge(
    'vinsmoke_training_loss_policy',
    'Policy head loss from training'
)

training_loss_value = Gauge(
    'vinsmoke_training_loss_value',
    'Value head loss from training'
)

training_checkpoints_total = Gauge(
    'vinsmoke_training_checkpoints_total',
    'Number of checkpoints saved'
)

training_elapsed_seconds = Gauge(
    'vinsmoke_training_elapsed_seconds',
    'Total elapsed training time in seconds'
)

training_active = Gauge(
    'vinsmoke_training_active',
    'Whether training is currently running (1=yes, 0=no)'
)

training_workers = Gauge(
    'vinsmoke_training_workers',
    'Number of parallel training workers'
)

training_buffer_size = Gauge(
    'vinsmoke_training_buffer_size',
    'Number of experiences in replay buffer'
)


def read_training_progress():
    """Read current training progress from file."""
    try:
        if TRAINING_PROGRESS_PATH.exists():
            with open(TRAINING_PROGRESS_PATH, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return {"total_games": 0, "start_time": time.time()}


def get_checkpoint_count():
    """Get number of checkpoint files."""
    try:
        if CHECKPOINTS_DIR.exists():
            # Count both checkpoint_*.pt and parallel_*.pt files
            checkpoints = list(CHECKPOINTS_DIR.glob("*.pt"))
            # Exclude latest.pt from count
            return len([c for c in checkpoints if c.name != "latest.pt"])
    except Exception:
        pass
    return 0


def is_training_running():
    """Check if training process is running."""
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'python' not in proc.info['name'].lower():
                    continue
                cmdline = proc.info.get('cmdline') or []
                if any('train_parallel' in arg for arg in cmdline):
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except Exception:
        pass
    return False


def update_metrics():
    """Update all Prometheus metrics with current values."""
    progress = read_training_progress()

    # Basic metrics
    total_games = progress.get("total_games", 0)
    start_time = progress.get("start_time", time.time())
    elapsed = time.time() - start_time

    training_games_total.set(total_games)
    training_elapsed_seconds.set(elapsed)

    # Calculate rate
    if elapsed > 0 and total_games > 0:
        rate = total_games / elapsed
        training_games_per_second.set(rate)
    else:
        training_games_per_second.set(0)

    # Loss metrics (from progress file)
    training_loss_total.set(progress.get("loss", 0.0))
    training_loss_policy.set(progress.get("policy_loss", 0.0))
    training_loss_value.set(progress.get("value_loss", 0.0))

    # Checkpoint count
    training_checkpoints_total.set(get_checkpoint_count())

    # Training status
    training_active.set(1 if is_training_running() else 0)

    # Workers and buffer (from progress file)
    training_workers.set(progress.get("workers", 0))
    training_buffer_size.set(progress.get("buffer_size", 0))


def get_metrics_response():
    """Generate Prometheus metrics response."""
    update_metrics()
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
