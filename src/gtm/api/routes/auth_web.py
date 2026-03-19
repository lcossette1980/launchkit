"""Web authentication routes — magic link login flow."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Cookie, Depends, HTTPException, status
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from gtm.api.deps import get_current_user, get_db
from gtm.config import Settings, get_settings
from gtm.models.user import User
from gtm.services.email import send_magic_link
from gtm.storage.user_repository import UserRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

SESSION_COOKIE = "lk_session"


class LoginRequest(BaseModel):
    email: EmailStr


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    plan: str
    email_verified: bool


@router.post("/login")
async def login(
    body: LoginRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """Send a magic link to the given email. Creates account if new."""
    repo = UserRepository(db)
    user, is_new = repo.get_or_create_user(body.email)

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    raw_token = repo.create_magic_token(user.id, settings)
    send_magic_link(settings, user.email, raw_token)

    return {
        "message": "Magic link sent! Check your email.",
        "is_new": is_new,
    }


@router.get("/verify")
async def verify(
    token: str,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """Verify magic link token, create session, redirect to app."""
    repo = UserRepository(db)
    user = repo.validate_magic_token(token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired magic link",
        )

    # Create a session
    session_token = repo.create_session(user.id, settings)

    # Redirect to app with session cookie
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(
        key=SESSION_COOKIE,
        value=session_token,
        httponly=True,
        secure=settings.environment != "development",
        samesite="lax",
        max_age=settings.session_expiry_days * 86400,
        path="/",
    )
    return response


@router.post("/logout")
async def logout(
    lk_session: str | None = Cookie(None),
    db: Session = Depends(get_db),
):
    """Clear the session cookie and invalidate the session."""
    if lk_session:
        repo = UserRepository(db)
        repo.delete_session(lk_session)

    response = JSONResponse({"message": "Logged out"})
    response.delete_cookie(SESSION_COOKIE, path="/")
    return response


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)):
    """Get the current authenticated user's profile."""
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        plan=user.plan,
        email_verified=user.email_verified,
    )
