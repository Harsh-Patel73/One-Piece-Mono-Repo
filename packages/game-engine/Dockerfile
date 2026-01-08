# OPTCG Game Engine - Shared Python Package
# This Dockerfile builds wheels for the game engine package
# Other containers copy these wheels to install the shared library

FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy package files
COPY requirements.txt setup.py ./
COPY optcg_engine/ ./optcg_engine/
COPY data/ ./data/
COPY decks/ ./decks/

# Build wheels for all dependencies
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt
RUN pip wheel --no-cache-dir --wheel-dir /wheels .

# Final stage - just the wheels for other images to copy
FROM scratch
COPY --from=builder /wheels /wheels
COPY --from=builder /app/data /data
COPY --from=builder /app/decks /decks
