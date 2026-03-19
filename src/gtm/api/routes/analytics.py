"""Analytics endpoints — score trends, diffs, and summaries."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

from gtm.api.deps import get_current_tenant, get_db
from gtm.models.analytics import ScoreSnapshot

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/trends")
async def score_trends(
    site_url: str = Query(..., description="Site URL to get trends for"),
    tenant_id: str = Depends(get_current_tenant),
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50),
):
    """Get score history for a specific site over time."""
    snapshots = (
        db.query(ScoreSnapshot)
        .filter_by(user_id=tenant_id, site_url=site_url)
        .order_by(desc(ScoreSnapshot.snapshot_at))
        .limit(limit)
        .all()
    )

    return [
        {
            "job_id": s.job_id,
            "brand": s.brand,
            "scores": {
                "clarity": s.clarity,
                "audience_fit": s.audience_fit,
                "conversion": s.conversion,
                "seo": s.seo,
                "ux": s.ux,
            },
            "overall_avg": s.overall_avg,
            "snapshot_at": s.snapshot_at.isoformat(),
        }
        for s in reversed(snapshots)  # Chronological order
    ]


@router.get("/diff")
async def score_diff(
    job_id: str = Query(...),
    compare_to: str = Query(..., description="Job ID to compare against"),
    tenant_id: str = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Compare scores between two analyses."""
    current = (
        db.query(ScoreSnapshot)
        .filter_by(job_id=job_id, user_id=tenant_id)
        .first()
    )
    previous = (
        db.query(ScoreSnapshot)
        .filter_by(job_id=compare_to, user_id=tenant_id)
        .first()
    )

    if not current or not previous:
        raise HTTPException(status_code=404, detail="One or both snapshots not found")

    metrics = ["clarity", "audience_fit", "conversion", "seo", "ux"]
    diff = {}
    for m in metrics:
        cur_val = getattr(current, m, 0)
        prev_val = getattr(previous, m, 0)
        diff[m] = {
            "current": cur_val,
            "previous": prev_val,
            "change": cur_val - prev_val,
        }

    return {
        "current_job": job_id,
        "previous_job": compare_to,
        "current_date": current.snapshot_at.isoformat(),
        "previous_date": previous.snapshot_at.isoformat(),
        "overall_change": current.overall_avg - previous.overall_avg,
        "metrics": diff,
    }


@router.get("/summary")
async def analytics_summary(
    tenant_id: str = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Get overall analytics summary for the user."""
    snapshots = (
        db.query(ScoreSnapshot)
        .filter_by(user_id=tenant_id)
        .order_by(desc(ScoreSnapshot.snapshot_at))
        .all()
    )

    if not snapshots:
        return {"total_analyses": 0, "sites_tracked": 0, "avg_score": 0, "sites": []}

    # Group by site
    sites: dict[str, list] = {}
    for s in snapshots:
        sites.setdefault(s.site_url, []).append(s)

    site_summaries = []
    for url, snaps in sites.items():
        latest = snaps[0]
        first = snaps[-1]
        site_summaries.append({
            "site_url": url,
            "brand": latest.brand,
            "analyses_count": len(snaps),
            "latest_score": latest.overall_avg,
            "first_score": first.overall_avg,
            "improvement": latest.overall_avg - first.overall_avg,
            "last_analyzed": latest.snapshot_at.isoformat(),
        })

    return {
        "total_analyses": len(snapshots),
        "sites_tracked": len(sites),
        "avg_score": round(sum(s.overall_avg for s in snapshots) / len(snapshots)),
        "sites": sorted(site_summaries, key=lambda x: x["last_analyzed"], reverse=True),
    }
