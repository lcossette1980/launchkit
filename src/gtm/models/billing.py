"""Billing models: subscriptions and usage tracking."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from gtm.models.base import Base, TimestampMixin


# ── Plan definitions (single source of truth) ──────────────────

PLAN_LIMITS = {
    "free": {
        "analyses_per_month": 1,
        "max_brands": 1,
        "max_pages": 20,
        "max_competitors": 3,
    },
    "pro": {
        "analyses_per_month": 5,
        "max_brands": 3,
        "max_pages": 50,
        "max_competitors": 5,
    },
    "agency": {
        "analyses_per_month": 25,
        "max_brands": -1,  # unlimited
        "max_pages": 100,
        "max_competitors": 10,
    },
}


def get_plan_limits(plan: str) -> dict:
    """Get limits for a plan. Defaults to free."""
    return PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])


class Subscription(Base, TimestampMixin):
    """Stripe subscription record."""

    __tablename__ = "subscriptions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), unique=True, index=True)
    stripe_subscription_id: Mapped[str] = mapped_column(
        String(255), unique=True, index=True
    )
    stripe_price_id: Mapped[str] = mapped_column(String(255))
    plan: Mapped[str] = mapped_column(String(20))  # "pro" or "agency"
    status: Mapped[str] = mapped_column(
        String(20), default="active"
    )  # active, past_due, canceled, trialing
    current_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    current_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False)


class UsageRecord(Base):
    """Monthly usage tracking per user."""

    __tablename__ = "usage_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    period_start: Mapped[date] = mapped_column(Date)
    period_end: Mapped[date] = mapped_column(Date)
    analyses_used: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()"
    )
