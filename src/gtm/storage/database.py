"""Database engine and session management."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from gtm.config import Settings

_engine = None
_SessionLocal: sessionmaker | None = None


def init_db(settings: Settings) -> None:
    """Initialize the database engine and session factory."""
    global _engine, _SessionLocal
    _engine = create_engine(
        settings.database_url,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
    )
    _SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False)


def get_session() -> Generator[Session, None, None]:
    """Yield a DB session — use as a FastAPI dependency."""
    if _SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    session = _SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_engine():
    """Get the current engine (for Alembic, health checks, etc.)."""
    return _engine
