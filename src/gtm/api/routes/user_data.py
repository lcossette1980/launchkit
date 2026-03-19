"""User data management — export and deletion (GDPR/CCPA compliance)."""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from gtm.api.deps import get_current_user_or_dev as get_current_user, get_db
from gtm.models.analytics import ScoreSnapshot
from gtm.models.billing import Subscription, UsageRecord
from gtm.models.job import AnalysisJob
from gtm.models.user import APIKey, MagicToken, User, UserSession

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/export")
async def export_user_data(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Export all user data as JSON (GDPR Article 20 — data portability)."""
    jobs = db.query(AnalysisJob).filter_by(tenant_id=user.id).all()
    snapshots = db.query(ScoreSnapshot).filter_by(user_id=user.id).all()
    usage = db.query(UsageRecord).filter_by(user_id=user.id).all()

    data = {
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "plan": user.plan,
            "created_at": str(user.created_at) if user.created_at else None,
        },
        "analyses": [
            {
                "id": j.id,
                "brand": j.brand,
                "site_url": j.site_url,
                "status": j.status.value if j.status else None,
                "created_at": str(j.created_at) if j.created_at else None,
                "results": j.results,
            }
            for j in jobs
        ],
        "score_history": [
            {
                "job_id": s.job_id,
                "site_url": s.site_url,
                "scores": {
                    "clarity": s.clarity,
                    "audience_fit": s.audience_fit,
                    "conversion": s.conversion,
                    "seo": s.seo,
                    "ux": s.ux,
                },
                "overall_avg": s.overall_avg,
                "date": str(s.snapshot_at),
            }
            for s in snapshots
        ],
        "usage_history": [
            {
                "period": f"{u.period_start} to {u.period_end}",
                "analyses_used": u.analyses_used,
            }
            for u in usage
        ],
    }

    from fastapi.responses import Response

    return Response(
        content=json.dumps(data, indent=2, default=str),
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="vclaunchkit-data-export-{user.id[:8]}.json"'
        },
    )


@router.delete("/delete")
async def delete_user_data(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete all user data (GDPR Article 17 — right to erasure).

    This permanently deletes:
    - All analyses and results
    - Score snapshots
    - Usage records
    - API keys
    - Sessions and tokens
    - Subscription records
    - The user account itself

    This action cannot be undone.
    """
    user_id = user.id
    email = user.email

    # Delete in dependency order
    deleted = {
        "score_snapshots": db.query(ScoreSnapshot).filter_by(user_id=user_id).delete(),
        "analyses": db.query(AnalysisJob).filter_by(tenant_id=user_id).delete(),
        "usage_records": db.query(UsageRecord).filter_by(user_id=user_id).delete(),
        "api_keys": db.query(APIKey).filter_by(user_id=user_id).delete(),
        "sessions": db.query(UserSession).filter_by(user_id=user_id).delete(),
        "magic_tokens": db.query(MagicToken).filter_by(user_id=user_id).delete(),
        "subscriptions": db.query(Subscription).filter_by(user_id=user_id).delete(),
    }

    # Delete user last
    db.query(User).filter_by(id=user_id).delete()
    db.commit()

    # Redact email for logging
    masked = email[:2] + "***" if email else "***"
    logger.info(
        "User data deleted: %s — %s",
        masked,
        {k: v for k, v in deleted.items() if v > 0},
    )

    return {
        "message": "All data has been permanently deleted",
        "deleted": deleted,
    }
