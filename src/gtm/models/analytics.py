"""Analytics models: score snapshots for change tracking."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from gtm.models.base import Base


class ScoreSnapshot(Base):
    """Historical score snapshot for tracking changes over time."""

    __tablename__ = "score_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    job_id: Mapped[str] = mapped_column(String(36), index=True)
    site_url: Mapped[str] = mapped_column(String(2048))
    brand: Mapped[str] = mapped_column(String(200))
    clarity: Mapped[int] = mapped_column(Integer, default=0)
    audience_fit: Mapped[int] = mapped_column(Integer, default=0)
    conversion: Mapped[int] = mapped_column(Integer, default=0)
    seo: Mapped[int] = mapped_column(Integer, default=0)
    ux: Mapped[int] = mapped_column(Integer, default=0)
    overall_avg: Mapped[int] = mapped_column(Integer, default=0)
    snapshot_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()"
    )
