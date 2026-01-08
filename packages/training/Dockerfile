# OPTCG Training Service - AI Model Training with Monitoring
# Multi-stage build for development and production

#==========================================
# Stage 1: Builder
#==========================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy game engine wheels from base image (built separately)
# COPY --from=optcg-engine:latest /wheels /wheels

# Install dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# Install PyTorch with CUDA support
RUN pip wheel --no-cache-dir --wheel-dir /wheels \
    torch --index-url https://download.pytorch.org/whl/cu118

#==========================================
# Stage 2: Development
#==========================================
FROM python:3.11-slim AS development

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install wheels
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*.whl

# Copy source code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 trainer && chown -R trainer:trainer /app
USER trainer

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

#==========================================
# Stage 3: Production
#==========================================
FROM python:3.11-slim AS production

WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy and install wheels
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*.whl && rm -rf /wheels

# Copy only necessary files
COPY api/ ./api/
COPY ai/ ./ai/
COPY handlers/ ./handlers/
COPY train_parallel.py .

# Create non-root user and directories
RUN useradd -m -u 1000 trainer \
    && mkdir -p /app/checkpoints /app/logs \
    && chown -R trainer:trainer /app

USER trainer

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
