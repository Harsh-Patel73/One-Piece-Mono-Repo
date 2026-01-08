"""
Training API routes for watching AI learn in real-time.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import subprocess
import threading
import time
import json
import psutil
from pathlib import Path
from dataclasses import dataclass, asdict

router = APIRouter()

# Global training state
training_process: Optional[subprocess.Popen] = None
training_lock = threading.Lock()
log_files: Dict[str, Any] = {}  # Store file handles

# Get paths
BACKEND_DIR = Path(__file__).parent.parent.parent
TRAINING_PROGRESS_PATH = BACKEND_DIR / "training_progress.json"
CHECKPOINTS_DIR = BACKEND_DIR / "checkpoints"


class TrainingConfig(BaseModel):
    workers: int = 8
    mcts: int = 10  # Lower = faster training. 10-25 is good balance, 100+ for evaluation
    games_per_iter: int = 1000
    target: Optional[int] = None
    deck1: Optional[str] = None
    deck2: Optional[str] = None
    resume: bool = True


def read_training_progress() -> Dict[str, Any]:
    """Read current training progress from file."""
    try:
        if TRAINING_PROGRESS_PATH.exists():
            with open(TRAINING_PROGRESS_PATH, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error reading training progress: {e}")
    return {"total_games": 0, "start_time": time.time()}


def get_checkpoint_count() -> int:
    """Get number of checkpoint files."""
    try:
        if CHECKPOINTS_DIR.exists():
            checkpoints = list(CHECKPOINTS_DIR.glob("checkpoint_*.pt"))
            return len(checkpoints)
    except Exception:
        return 0
    return 0


def calculate_training_rate(progress: Dict[str, Any]) -> float:
    """Calculate games per second."""
    try:
        start_time = progress.get("start_time", time.time())
        total_games = progress.get("total_games", 0)
        elapsed = time.time() - start_time
        if elapsed > 0 and total_games > 0:
            return total_games / elapsed
    except Exception:
        pass
    return 0.0


def is_training_running() -> bool:
    """Check if training process is actually running."""
    global training_process

    # First check tracked process
    if training_process is not None:
        try:
            if training_process.poll() is None:
                return True
        except Exception:
            pass

    # Also check for any train_parallel processes (started externally)
    try:
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


def start_training_process(config: TrainingConfig) -> subprocess.Popen:
    """Start the actual train_parallel.py process."""
    global training_process, log_files

    # Build command
    cmd = [
        "python",
        str(BACKEND_DIR / "train_parallel.py"),
        "--workers", str(config.workers),
        "--mcts", str(config.mcts),
        "--games-per-iter", str(config.games_per_iter),
    ]

    if config.resume:
        cmd.append("--resume")

    if config.target:
        cmd.extend(["--target", str(config.target)])

    if config.deck1:
        cmd.extend(["--deck1", config.deck1])

    if config.deck2:
        cmd.extend(["--deck2", config.deck2])

    # Create log files for output
    log_dir = BACKEND_DIR / "logs"
    log_dir.mkdir(exist_ok=True)

    stdout_log = log_dir / "training_stdout.log"
    stderr_log = log_dir / "training_stderr.log"

    # Open log files
    stdout_file = open(stdout_log, 'w', buffering=1)
    stderr_file = open(stderr_log, 'w', buffering=1)

    # Store file handles so we can close them later
    log_files['stdout'] = stdout_file
    log_files['stderr'] = stderr_file

    # Start process with output redirected to log files
    training_process = subprocess.Popen(
        cmd,
        cwd=str(BACKEND_DIR),
        stdout=stdout_file,
        stderr=stderr_file,
        text=True
    )

    return training_process


@router.post("/start")
async def start_training(config: TrainingConfig):
    """Start the parallel training process."""
    global training_process

    with training_lock:
        if is_training_running():
            raise HTTPException(400, "Training already in progress")

        try:
            start_training_process(config)
            return {
                "status": "started",
                "config": config.dict(),
                "pid": training_process.pid if training_process else None
            }
        except Exception as e:
            raise HTTPException(500, f"Failed to start training: {str(e)}")


def find_and_kill_training_processes() -> int:
    """Find and kill any orphaned training processes."""
    killed = 0
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'python' not in proc.info['name'].lower():
                    continue
                cmdline = proc.info.get('cmdline') or []
                cmdline_str = ' '.join(cmdline)

                # Kill train_parallel.py processes
                if 'train_parallel' in cmdline_str:
                    # Kill children first
                    for child in proc.children():
                        try:
                            child.kill()
                            killed += 1
                        except Exception:
                            pass
                    proc.kill()
                    killed += 1
                # Kill orphaned multiprocessing workers from training
                elif 'multiprocessing.spawn' in cmdline_str:
                    # Check if parent is dead (orphaned)
                    try:
                        parent_pid = None
                        for part in cmdline:
                            if 'parent_pid=' in part:
                                parent_pid = int(part.split('=')[1].rstrip(',)'))
                                break
                        if parent_pid and not psutil.pid_exists(parent_pid):
                            proc.kill()
                            killed += 1
                    except Exception:
                        pass
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except Exception:
        pass
    return killed


@router.post("/stop")
async def stop_training_endpoint():
    """Stop the training process."""
    global training_process, log_files

    with training_lock:
        killed_count = 0

        # First, try to stop the tracked process
        if training_process:
            try:
                training_process.terminate()
                try:
                    training_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    training_process.kill()
                    training_process.wait()
                killed_count += 1
            except Exception:
                pass
            training_process = None

        # Also find and kill any orphaned training processes
        killed_count += find_and_kill_training_processes()

        # Close log files
        if 'stdout' in log_files:
            try:
                log_files['stdout'].close()
            except Exception:
                pass
        if 'stderr' in log_files:
            try:
                log_files['stderr'].close()
            except Exception:
                pass
        log_files.clear()

        if killed_count > 0:
            return {"status": "stopped", "processes_killed": killed_count}
        else:
            return {"status": "not_running"}


@router.get("/status")
async def get_training_status():
    """Get current training status from the actual training progress."""
    is_running = is_training_running()
    progress = read_training_progress()

    total_games = progress.get("total_games", 0)
    start_time = progress.get("start_time", time.time())
    games_per_second = calculate_training_rate(progress)
    checkpoint_count = get_checkpoint_count()

    return {
        "is_training": is_running,
        "total_games": total_games,
        "games_per_second": games_per_second,
        "checkpoint_count": checkpoint_count,
        "start_time": start_time,
        "elapsed_time": time.time() - start_time if start_time else 0,
        # Actual loss values from training
        "loss": progress.get("loss", 0.0),
        "policy_loss": progress.get("policy_loss", 0.0),
        "value_loss": progress.get("value_loss", 0.0),
        # Additional metrics
        "workers": progress.get("workers", 0),
        "buffer_size": progress.get("buffer_size", 0),
        # Legacy fields for compatibility
        "current_iteration": checkpoint_count,
        "games_per_iteration": 1000,
        "mcts_simulations": 100,
        "current_game": None,
        "recent_games": [],
        "training_history": [],
    }


@router.get("/decks")
async def get_available_decks():
    """Get list of available deck files."""
    try:
        decks_dir = BACKEND_DIR / "decks"
        deck_files = list(decks_dir.glob("*.json"))
        decks = [f.stem for f in deck_files]
        return {"decks": decks}
    except Exception as e:
        raise HTTPException(500, f"Failed to list decks: {str(e)}")


@router.get("/progress-history")
async def get_progress_history():
    """Get historical training progress data."""
    try:
        # Check if there's a history file or aggregate from checkpoints
        checkpoints = []
        if CHECKPOINTS_DIR.exists():
            checkpoint_files = sorted(CHECKPOINTS_DIR.glob("checkpoint_*.pt"))
            for cp in checkpoint_files:
                # Extract game count from filename (checkpoint_XXXX.pt)
                try:
                    game_num = int(cp.stem.split('_')[1])
                    checkpoints.append({"games": game_num, "checkpoint": cp.name})
                except Exception:
                    pass

        return {
            "checkpoints": checkpoints,
            "current_progress": read_training_progress()
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to get progress history: {str(e)}")


@router.get("/logs")
async def get_training_logs(lines: int = 50):
    """Get recent training log output."""
    try:
        log_dir = BACKEND_DIR / "logs"
        stdout_log = log_dir / "training_stdout.log"
        stderr_log = log_dir / "training_stderr.log"

        stdout_lines = []
        stderr_lines = []

        if stdout_log.exists():
            with open(stdout_log, 'r') as f:
                stdout_lines = f.readlines()[-lines:]

        if stderr_log.exists():
            with open(stderr_log, 'r') as f:
                stderr_lines = f.readlines()[-lines:]

        return {
            "stdout": "".join(stdout_lines),
            "stderr": "".join(stderr_lines)
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to read logs: {str(e)}")
