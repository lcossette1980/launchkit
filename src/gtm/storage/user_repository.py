"""Repository for user, session, magic token, and usage CRUD."""

from __future__ import annotations

import hashlib
import logging
import secrets
import uuid
from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session

from gtm.config import Settings
from gtm.models.billing import UsageRecord, get_plan_limits
from gtm.models.user import MagicToken, User, UserSession

logger = logging.getLogger(__name__)


class UserRepository:
    """CRUD for users and auth tokens."""

    def __init__(self, session: Session) -> None:
        self.session = session

    # ── Users ──────────────────────────────────────────────

    def get_user(self, user_id: str) -> User | None:
        return self.session.query(User).filter_by(id=user_id).first()

    def get_user_by_email(self, email: str) -> User | None:
        return self.session.query(User).filter_by(email=email.lower().strip()).first()

    def get_or_create_user(self, email: str) -> tuple[User, bool]:
        """Get existing user or create a new one. Returns (user, is_new)."""
        email = email.lower().strip()
        user = self.get_user_by_email(email)
        if user:
            return user, False

        user = User(
            id=str(uuid.uuid4()),
            email=email,
            name=email.split("@")[0],
            plan="free",
            is_active=True,
            email_verified=False,
        )
        self.session.add(user)
        self.session.commit()
        logger.info("Created new user %s (%s)", user.id, email)
        return user, True

    # ── Magic Tokens ──────────────────────────────────────

    def create_magic_token(self, user_id: str, settings: Settings) -> str:
        """Create a magic link token. Returns the raw token (shown once)."""
        raw_token = secrets.token_urlsafe(48)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        magic = MagicToken(
            id=str(uuid.uuid4()),
            user_id=user_id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc)
            + timedelta(minutes=settings.magic_link_expiry_minutes),
            used=False,
        )
        self.session.add(magic)
        self.session.commit()
        return raw_token

    def validate_magic_token(self, raw_token: str) -> User | None:
        """Validate and consume a magic token. Returns the user or None."""
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        magic = (
            self.session.query(MagicToken)
            .filter_by(token_hash=token_hash, used=False)
            .first()
        )
        if not magic:
            return None

        if magic.expires_at < datetime.now(timezone.utc):
            return None

        # Mark as used
        magic.used = True

        # Mark user as email-verified
        user = self.get_user(magic.user_id)
        if user:
            user.email_verified = True
            self.session.commit()

        return user

    # ── Sessions ──────────────────────────────────────────

    def create_session(self, user_id: str, settings: Settings) -> str:
        """Create a login session. Returns the raw session token."""
        raw_token = secrets.token_urlsafe(48)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        sess = UserSession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=settings.session_expiry_days),
        )
        self.session.add(sess)
        self.session.commit()
        return raw_token

    def get_user_by_session(self, raw_token: str) -> User | None:
        """Look up a user by their session cookie value."""
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        sess = (
            self.session.query(UserSession)
            .filter_by(token_hash=token_hash)
            .first()
        )
        if not sess:
            return None

        if sess.expires_at < datetime.now(timezone.utc):
            # Expired — clean it up
            self.session.delete(sess)
            self.session.commit()
            return None

        return self.get_user(sess.user_id)

    def delete_session(self, raw_token: str) -> None:
        """Invalidate a session (logout)."""
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        sess = (
            self.session.query(UserSession)
            .filter_by(token_hash=token_hash)
            .first()
        )
        if sess:
            self.session.delete(sess)
            self.session.commit()

    # ── Usage Tracking ────────────────────────────────────

    def _current_period(self) -> tuple[date, date]:
        """Get current billing period (1st of month to 1st of next)."""
        today = date.today()
        start = today.replace(day=1)
        if today.month == 12:
            end = date(today.year + 1, 1, 1)
        else:
            end = date(today.year, today.month + 1, 1)
        return start, end

    def get_or_create_usage(self, user_id: str) -> UsageRecord:
        """Get or create usage record for current billing period."""
        start, end = self._current_period()

        record = (
            self.session.query(UsageRecord)
            .filter_by(user_id=user_id, period_start=start)
            .first()
        )
        if record:
            return record

        record = UsageRecord(
            id=str(uuid.uuid4()),
            user_id=user_id,
            period_start=start,
            period_end=end,
            analyses_used=0,
        )
        self.session.add(record)
        self.session.commit()
        return record

    def check_quota(self, user: User) -> dict:
        """Check if user has remaining analysis quota.

        Returns dict with: allowed, used, limit, plan
        """
        limits = get_plan_limits(user.plan)
        usage = self.get_or_create_usage(user.id)
        limit = limits["analyses_per_month"]

        return {
            "allowed": usage.analyses_used < limit,
            "used": usage.analyses_used,
            "limit": limit,
            "plan": user.plan,
            "max_pages": limits["max_pages"],
            "max_competitors": limits["max_competitors"],
        }

    def increment_usage(self, user_id: str) -> None:
        """Increment the analysis count for the current period."""
        usage = self.get_or_create_usage(user_id)
        usage.analyses_used += 1
        self.session.commit()
