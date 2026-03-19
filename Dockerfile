# ── Stage 1: Build frontend ──────────────────────────────────
FROM node:20-alpine AS frontend-builder
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit
COPY frontend/ .
RUN npm run build

# ── Stage 2: Production image ───────────────────────────────
FROM mcr.microsoft.com/playwright/python:v1.55.0-jammy

WORKDIR /app

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install production dependencies only (no [dev], no editable install)
COPY pyproject.toml .
COPY src/ src/
RUN pip install --no-cache-dir .

# Gunicorn config
COPY gunicorn.conf.py .

# Alembic config
COPY alembic.ini .
COPY alembic/ alembic/

# Copy built frontend
COPY --from=frontend-builder /build/dist /app/frontend/dist

# Create directories with proper ownership
RUN mkdir -p /app/data /app/logs /app/exports

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /bin/bash appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Use gunicorn with uvicorn workers for production
CMD ["gunicorn", "gtm.api.app:create_app()", "--config", "gunicorn.conf.py"]
