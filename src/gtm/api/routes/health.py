"""Health check and observability endpoints."""

from __future__ import annotations

import logging

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from sqlalchemy import text

from gtm.storage.database import get_engine
from gtm.storage.redis_client import get_redis

router = APIRouter(tags=["health"])
logger = logging.getLogger(__name__)


@router.get("/health")
async def liveness():
    """Liveness probe — always returns 200 if the process is up."""
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness():
    """Readiness probe — checks DB + Redis connectivity."""
    checks: dict[str, str] = {}

    # Database
    try:
        engine = get_engine()
        if engine is None:
            checks["database"] = "not_initialized"
        else:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {e}"
        logger.warning("Health check: database unhealthy: %s", e)

    # Redis
    try:
        r = get_redis()
        r.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {e}"
        logger.warning("Health check: redis unhealthy: %s", e)

    all_ok = all(v == "ok" for v in checks.values())
    return {"status": "ready" if all_ok else "degraded", "checks": checks}


@router.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint for scraping."""
    try:
        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
        return PlainTextResponse(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST,
        )
    except ImportError:
        return PlainTextResponse(
            content="# prometheus_client not installed\n",
            media_type="text/plain",
        )
