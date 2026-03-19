"""FastAPI dependency injection."""

from __future__ import annotations

import hashlib
from collections.abc import Generator
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Cookie, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from gtm.config import Settings, get_settings
from gtm.models.user import APIKey, User
from gtm.storage.database import get_session
from gtm.storage.repository import JobRepository
from gtm.storage.user_repository import UserRepository


def get_db() -> Generator[Session, None, None]:
    """Yield a DB session."""
    yield from get_session()


def get_repo(db: Annotated[Session, Depends(get_db)]) -> JobRepository:
    """Yield a job repository bound to the current session."""
    return JobRepository(db)


def get_user_repo(db: Annotated[Session, Depends(get_db)]) -> UserRepository:
    """Yield a user repository bound to the current session."""
    return UserRepository(db)


def _authenticate(
    authorization: str | None,
    lk_session: str | None,
    db: Session,
) -> User | None:
    """Try to authenticate via session cookie or API key. Returns User or None."""
    user_repo = UserRepository(db)

    # 1. Try session cookie
    if lk_session:
        user = user_repo.get_user_by_session(lk_session)
        if user and user.is_active:
            return user

    # 2. Try API key bearer token
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        key_hash = hashlib.sha256(token.encode()).hexdigest()
        api_key = db.query(APIKey).filter_by(key_hash=key_hash, is_active=True).first()
        if api_key:
            api_key.last_used_at = datetime.now(timezone.utc)
            db.commit()
            user = user_repo.get_user(api_key.user_id)
            if user and user.is_active:
                return user

    return None


def _get_or_create_dev_user(db: Session) -> User:
    """Get or create the dev-mode auto-login user."""
    user_repo = UserRepository(db)
    dev_user = user_repo.get_user_by_email("dev@vclaunchkit.com")
    if not dev_user:
        dev_user = User(
            id="dev-tenant",
            email="dev@vclaunchkit.com",
            name="Dev User",
            plan="agency",
            is_active=True,
            email_verified=True,
        )
        db.add(dev_user)
        db.commit()
    return dev_user


def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    lk_session: str | None = Cookie(None),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> User:
    """Authenticate via session cookie or API key. No dev fallback.

    Used by /auth/me — must return 401 if not authenticated so the
    frontend can show the landing page to unauthenticated visitors.
    """
    user = _authenticate(authorization, lk_session, db)
    if user:
        return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )


def get_current_user_or_dev(
    authorization: Annotated[str | None, Header()] = None,
    lk_session: str | None = Cookie(None),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> User:
    """Authenticate with dev-mode fallback.

    Used by API endpoints (analyses, billing, etc.) where the dev
    fallback provides a convenient default user for local development.
    """
    user = _authenticate(authorization, lk_session, db)
    if user:
        return user

    # Dev fallback
    if settings.environment == "development" and not authorization and not lk_session:
        return _get_or_create_dev_user(db)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )


def get_current_tenant(
    user: User = Depends(get_current_user_or_dev),
) -> str:
    """Return the current user's ID as tenant_id (backward compat)."""
    return user.id
