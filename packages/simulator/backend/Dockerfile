# OPTCG Simulator Backend - FastAPI + Socket.IO Server
# Multi-stage build for development and production

#==========================================
# Stage 1: Builder
#==========================================
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

#==========================================
# Stage 2: Development
#==========================================
FROM python:3.11-slim AS development

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*.whl

COPY . .

RUN useradd -m -u 1000 simulator && chown -R simulator:simulator /app
USER simulator

EXPOSE 8001
CMD ["python", "-m", "uvicorn", "main:socket_app", "--host", "0.0.0.0", "--port", "8001", "--reload"]

#==========================================
# Stage 3: Production
#==========================================
FROM python:3.11-slim AS production

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*.whl && rm -rf /wheels

# Copy application files
COPY main.py .
COPY api/ ./api/
COPY realtime/ ./realtime/
COPY game/ ./game/
COPY data/ ./data/

RUN useradd -m -u 1000 simulator \
    && mkdir -p /app/logs \
    && chown -R simulator:simulator /app

USER simulator

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

EXPOSE 8001
CMD ["python", "-m", "uvicorn", "main:socket_app", "--host", "0.0.0.0", "--port", "8001"]
