# ==============================================================================
# FraudShield Production Backend Dockerfile
# Multi-stage secure build for Python 3.13 FastAPI and ML Inference Service
# ==============================================================================

# Stage 1: Build & Dependencies
FROM python:3.13-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --default-timeout=1000 --user -r requirements.txt

# Stage 2: Final Runtime Image
FROM python:3.13-slim AS runtime

WORKDIR /app

# Install runtime shared libraries for XGBoost & OpenMP
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root system user for security compliance
RUN groupadd -g 1001 fraudshield && \
    useradd -u 1001 -g fraudshield -s /bin/bash -m fraudshield

# Copy installed wheels and dependencies from builder
COPY --from=builder /root/.local /home/fraudshield/.local
ENV PATH=/home/fraudshield/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Memory optimization for cloud container runtimes (Render free tier 512MB RAM cap)
# Restricts OpenMP and BLAS from allocating massive thread pools on multi-core host nodes
ENV OMP_NUM_THREADS=1
ENV OPENBLAS_NUM_THREADS=1
ENV MKL_NUM_THREADS=1
ENV VECLIB_MAXIMUM_THREADS=1
ENV NUMEXPR_NUM_THREADS=1

# Copy source code and ML artifacts
COPY backend /app/backend
COPY ml /app/ml

# Set permissions
RUN chown -R fraudshield:fraudshield /app
USER fraudshield

EXPOSE 8000

# Health check probe
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Start Uvicorn ASGI Server: reads $PORT from cloud provider (e.g. Render :10000)
# and limits worker concurrency to 1 by default to stay well under 512MB RAM
CMD ["sh", "-c", "exec python -m uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers ${WEB_CONCURRENCY:-1}"]
