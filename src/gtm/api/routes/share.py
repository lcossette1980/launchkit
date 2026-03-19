"""Public share routes — no authentication required."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from gtm.api.deps import get_db
from gtm.models.job import JobStatus
from gtm.storage.repository import JobRepository

router = APIRouter(prefix="/share", tags=["share"])


@router.get("/{token}")
async def get_shared_report(
    token: str,
    db: Session = Depends(get_db),
):
    """Get a publicly shared report by share token.

    No authentication required. Returns full report data
    with a watermark flag for the frontend.
    """
    repo = JobRepository(db)
    job = repo.get_job_by_share_token(token)

    if not job:
        raise HTTPException(status_code=404, detail="Report not found or link expired")

    if job.status != JobStatus.COMPLETED:
        raise HTTPException(status_code=409, detail="Analysis not complete")

    results = repo.get_results(job.id)
    if not results:
        raise HTTPException(status_code=404, detail="Results not found")

    return {
        "brand": job.brand,
        "site_url": job.site_url,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "results": results,
        "_shared": True,  # Frontend uses this to show watermark + CTA
    }
