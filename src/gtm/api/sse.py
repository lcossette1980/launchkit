"""Server-Sent Events (SSE) streaming via Redis pub/sub."""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncGenerator

from gtm.storage.redis_client import get_redis

logger = logging.getLogger(__name__)

# How long to wait between checking for messages (seconds)
_POLL_INTERVAL = 0.5
# Send a keepalive comment every N seconds to prevent proxy timeouts
_KEEPALIVE_INTERVAL = 15.0


async def stream_progress(job_id: str) -> AsyncGenerator[str, None]:
    """Subscribe to Redis pub/sub and yield SSE-formatted events.

    Yields lines in the format:
        event: progress
        data: {"step": "crawl", "pct": 15, "message": "Crawling page 2 of 10"}

    Terminates when a "complete" or "error" event is received,
    or after 15 minutes (safety timeout).
    """
    r = get_redis()
    pubsub = r.pubsub()
    channel = f"job:{job_id}:progress"
    pubsub.subscribe(channel)

    try:
        deadline = asyncio.get_event_loop().time() + 900  # 15 min timeout
        last_keepalive = asyncio.get_event_loop().time()

        while asyncio.get_event_loop().time() < deadline:
            message = pubsub.get_message(ignore_subscribe_messages=True)

            if message and message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                except json.JSONDecodeError:
                    continue

                event_type = data.get("event", "progress")
                payload = data.get("payload", data)

                yield f"event: {event_type}\ndata: {json.dumps(payload)}\n\n"

                # Terminate on final events
                if event_type in ("complete", "error"):
                    return

            else:
                # Send keepalive comment to prevent connection timeout
                now = asyncio.get_event_loop().time()
                if now - last_keepalive > _KEEPALIVE_INTERVAL:
                    yield ": keepalive\n\n"
                    last_keepalive = now

                await asyncio.sleep(_POLL_INTERVAL)

        # Safety timeout reached
        yield f"event: error\ndata: {json.dumps({'message': 'Stream timeout'})}\n\n"

    finally:
        pubsub.unsubscribe(channel)
        pubsub.close()
