"""FastAPI application factory with lifespan management."""

from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from gtm.config import get_settings
from gtm.monitoring.logging_config import configure_logging

logger = logging.getLogger(__name__)

# ── Required settings per environment ────────────────────────
REQUIRED_IN_PRODUCTION = [
    "database_url",
    "redis_url",
    "secret_key",
    "stripe_api_key",
    "stripe_webhook_secret",
    "stripe_pro_price_id",
    "stripe_agency_price_id",
    "openai_api_key",
]


def _validate_settings_for_production(settings) -> None:
    """Fail fast if required production settings are missing."""
    if settings.environment == "development":
        return

    missing = []
    for key in REQUIRED_IN_PRODUCTION:
        val = getattr(settings, key, "")
        if not val or val in ("change-me-in-production", "change-me"):
            missing.append(key.upper())

    if missing:
        logger.critical("Missing required production settings: %s", ", ".join(missing))
        sys.exit(1)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize services on startup, clean up on shutdown."""
    settings = get_settings()

    configure_logging(settings)
    logger.info("Starting VCLaunchKit API (%s)", settings.environment)

    # Fail fast on missing production config
    _validate_settings_for_production(settings)

    # Initialize storage backends
    from gtm.storage.database import init_db
    from gtm.storage.redis_client import init_redis
    from gtm.storage.s3 import init_s3

    init_db(settings)
    init_redis(settings)
    init_s3(settings)

    # Initialize Stripe
    from gtm.services.stripe_service import init_stripe

    init_stripe(settings)

    logger.info("All services initialized")
    yield

    logger.info("Shutting down VCLaunchKit API")


def create_app() -> FastAPI:
    """Build the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="VCLaunchKit",
        description="AI-powered GTM playbooks for builders",
        version="0.3.0",
        lifespan=lifespan,
        # Disable docs in production
        docs_url="/docs" if settings.environment == "development" else None,
        redoc_url=None,
    )

    # ── Security middleware ──────────────────────────────
    from gtm.api.middleware import RateLimitMiddleware, SecurityHeadersMiddleware

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RateLimitMiddleware)

    # CORS — strict origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )

    # ── Register routes ─────────────────────────────────
    from gtm.api.routes.analysis import router as analysis_router
    from gtm.api.routes.analytics import router as analytics_router
    from gtm.api.routes.auth import router as auth_router
    from gtm.api.routes.auth_web import router as auth_web_router
    from gtm.api.routes.billing import router as billing_router
    from gtm.api.routes.examples import router as examples_router
    from gtm.api.routes.health import router as health_router
    from gtm.api.routes.reports import router as reports_router
    from gtm.api.routes.share import router as share_router
    from gtm.api.routes.user_data import router as user_data_router

    app.include_router(health_router)
    app.include_router(analysis_router, prefix="/api/v1")
    app.include_router(reports_router, prefix="/api/v1")
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(auth_web_router, prefix="/api/v1")
    app.include_router(billing_router, prefix="/api/v1")
    app.include_router(share_router, prefix="/api/v1")
    app.include_router(examples_router, prefix="/api/v1")
    app.include_router(analytics_router, prefix="/api/v1")
    app.include_router(user_data_router, prefix="/api/v1")

    # ── Serve frontend ──────────────────────────────────
    from fastapi.staticfiles import StaticFiles

    _project_root = Path(__file__).resolve().parent.parent.parent.parent
    _frontend_dist = _project_root / "frontend" / "dist"
    _legacy_html = Path(__file__).parent / "static" / "index.html"

    if _frontend_dist.exists() and (_frontend_dist / "index.html").exists():
        # Serve built React SPA
        _assets = _frontend_dist / "assets"
        if _assets.exists():
            app.mount("/assets", StaticFiles(directory=str(_assets)), name="assets")

        _spa_index = _frontend_dist / "index.html"

        # Social crawlers need server-rendered OG tags for shared reports
        SOCIAL_BOTS = ("twitterbot", "facebookexternalhit", "linkedinbot",
                       "slackbot", "discordbot", "telegrambot", "whatsapp")

        @app.get("/{path:path}")
        async def spa_fallback(path: str, request: Request):
            from fastapi.responses import HTMLResponse

            # Serve dynamic OG tags for shared report links when social bots visit
            if path.startswith("share/") and any(
                bot in (request.headers.get("user-agent", "").lower())
                for bot in SOCIAL_BOTS
            ):
                token = path.split("/", 1)[1] if "/" in path else path[6:]
                if token:
                    try:
                        from gtm.storage.database import get_session
                        from gtm.storage.repository import JobRepository
                        sess = next(get_session())
                        repo = JobRepository(sess)
                        job = repo.get_job_by_share_token(token)
                        if job and job.results:
                            scores = job.results.get("website_analysis", {}).get("overall_scores", {})
                            avg = round(sum(scores.values()) / len(scores)) if scores else 0
                            desc = f"GTM Playbook for {job.brand} — Overall score: {avg}/100. Page-by-page audit, competitor analysis, copy kit, and 30/60/90 roadmap."
                            return HTMLResponse(f"""<!doctype html>
<html><head>
<meta property="og:type" content="article"/>
<meta property="og:site_name" content="VCLaunchKit"/>
<meta property="og:title" content="{job.brand} — GTM Playbook by VCLaunchKit"/>
<meta property="og:description" content="{desc}"/>
<meta property="og:url" content="https://vclaunchkit.com/share/{token}"/>
<meta property="og:image" content="https://vclaunchkit.com/og-image.png"/>
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:title" content="{job.brand} — GTM Playbook"/>
<meta name="twitter:description" content="{desc}"/>
<meta http-equiv="refresh" content="0;url=https://vclaunchkit.com/share/{token}"/>
</head><body></body></html>""")
                    except Exception:
                        pass

            candidate = _frontend_dist / path
            if path and candidate.exists() and candidate.is_file():
                return FileResponse(str(candidate))
            return FileResponse(str(_spa_index), media_type="text/html")

        logger.info("Serving React SPA from %s", _frontend_dist)
    else:
        @app.get("/")
        async def index():
            return FileResponse(str(_legacy_html), media_type="text/html")

        logger.info("Serving legacy HTML (React build not found at %s)", _frontend_dist)

    return app
