"""Redis client for caching and pub/sub progress events."""

from __future__ import annotations

import json
import logging

import redis as redis_lib

from gtm.config import Settings

logger = logging.getLogger(__name__)

_redis: redis_lib.Redis | None = None


def init_redis(settings: Settings) -> None:
    """Initialize the Redis connection."""
    global _redis
    _redis = redis_lib.from_url(settings.redis_url, decode_responses=True)


def get_redis() -> redis_lib.Redis:
    """Get the Redis client."""
    if _redis is None:
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    return _redis


# --- Cache helpers ---


def cache_set(key: str, value: dict, ttl_seconds: int = 86400) -> None:
    """Cache a JSON-serializable value with TTL."""
    r = get_redis()
    r.setex(key, ttl_seconds, json.dumps(value))


def cache_get(key: str) -> dict | None:
    """Get a cached value, or None if missing/expired."""
    r = get_redis()
    raw = r.get(key)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


# --- Progress pub/sub ---


def publish_progress(job_id: str, event: str, payload: dict) -> None:
    """Publish a progress event for SSE consumers."""
    r = get_redis()
    message = json.dumps({"event": event, "payload": payload})
    r.publish(f"job:{job_id}:progress", message)
