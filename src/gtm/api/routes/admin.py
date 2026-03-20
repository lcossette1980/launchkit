"""Admin routes — users, reports, stats, system overview."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from gtm.api.deps import get_db, require_admin
from gtm.models.billing import Subscription, UsageRecord
from gtm.models.job import AnalysisJob, JobStatus
from gtm.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


# ---------------------------------------------------------------------------
# Dashboard / Stats
# ---------------------------------------------------------------------------


@router.get("/stats")
async def admin_stats(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """High-level platform stats for the admin dashboard."""
    total_users = db.query(func.count(User.id)).scalar() or 0
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0

    # Plan breakdown
    plan_counts = dict(
        db.query(User.plan, func.count(User.id))
        .group_by(User.plan)
        .all()
    )

    # Analysis stats
    total_analyses = db.query(func.count(AnalysisJob.id)).scalar() or 0
    completed_analyses = (
        db.query(func.count(AnalysisJob.id))
        .filter(AnalysisJob.status == JobStatus.COMPLETED)
        .scalar() or 0
    )
    failed_analyses = (
        db.query(func.count(AnalysisJob.id))
        .filter(AnalysisJob.status == JobStatus.FAILED)
        .scalar() or 0
    )
    running_analyses = (
        db.query(func.count(AnalysisJob.id))
        .filter(AnalysisJob.status == JobStatus.RUNNING)
        .scalar() or 0
    )

    # Subscription stats
    active_subs = (
        db.query(func.count(Subscription.id))
        .filter(Subscription.status == "active")
        .scalar() or 0
    )

    # Usage this month
    from gtm.storage.user_repository import UserRepository
    repo = UserRepository(db)
    period_start, period_end = repo._current_period()
    month_analyses = (
        db.query(func.sum(UsageRecord.analyses_used))
        .filter(UsageRecord.period_start == period_start)
        .scalar() or 0
    )

    # Estimated cost (rough: $0.80 per analysis)
    est_cost_month = round(month_analyses * 0.80, 2)

    # Revenue estimate (active subs * avg price)
    pro_count = (
        db.query(func.count(Subscription.id))
        .filter(Subscription.status == "active", Subscription.plan == "pro")
        .scalar() or 0
    )
    agency_count = (
        db.query(func.count(Subscription.id))
        .filter(Subscription.status == "active", Subscription.plan == "agency")
        .scalar() or 0
    )
    est_mrr = (pro_count * 29) + (agency_count * 79)

    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "by_plan": plan_counts,
        },
        "analyses": {
            "total": total_analyses,
            "completed": completed_analyses,
            "failed": failed_analyses,
            "running": running_analyses,
            "this_month": month_analyses,
        },
        "billing": {
            "active_subscriptions": active_subs,
            "pro_subscribers": pro_count,
            "agency_subscribers": agency_count,
            "estimated_mrr": est_mrr,
        },
        "costs": {
            "analyses_this_month": month_analyses,
            "estimated_cost": est_cost_month,
            "cost_per_analysis": 0.80,
        },
    }


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------


@router.get("/users")
async def list_users(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
):
    """List all users with plan and usage info."""
    users = (
        db.query(User)
        .order_by(User.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    result = []
    for u in users:
        # Get usage for this user
        usage = (
            db.query(UsageRecord)
            .filter_by(user_id=u.id)
            .order_by(UsageRecord.period_start.desc())
            .first()
        )
        # Get total analyses count
        total = (
            db.query(func.count(AnalysisJob.id))
            .filter_by(tenant_id=u.id)
            .scalar() or 0
        )
        sub = db.query(Subscription).filter_by(user_id=u.id).first()

        result.append({
            "id": u.id,
            "email": u.email,
            "name": u.name,
            "plan": u.plan,
            "is_admin": u.is_admin,
            "is_active": u.is_active,
            "email_verified": u.email_verified,
            "stripe_customer_id": u.stripe_customer_id,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "analyses_total": total,
            "analyses_this_month": usage.analyses_used if usage else 0,
            "subscription_status": sub.status if sub else None,
        })

    return result


@router.post("/users/{user_id}/toggle-admin")
async def toggle_admin(
    user_id: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Toggle admin status for a user."""
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_admin = not user.is_admin
    db.commit()
    return {"email": user.email, "is_admin": user.is_admin}


@router.post("/users/{user_id}/set-plan")
async def set_plan(
    user_id: str,
    plan: str = Query(...),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Manually set a user's plan (admin override)."""
    if plan not in ("free", "pro", "agency"):
        raise HTTPException(status_code=400, detail="Invalid plan")
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.plan = plan
    db.commit()
    return {"email": user.email, "plan": user.plan}


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------


@router.get("/reports")
async def list_all_reports(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    status_filter: str | None = Query(None, alias="status"),
):
    """List all analyses across all users."""
    q = db.query(AnalysisJob)
    if status_filter:
        q = q.filter(AnalysisJob.status == status_filter)
    jobs = q.order_by(AnalysisJob.created_at.desc()).offset(offset).limit(limit).all()

    result = []
    for j in jobs:
        # Get the user email
        user = db.query(User).filter_by(id=j.tenant_id).first()
        scores = {}
        if j.results and isinstance(j.results, dict):
            scores = j.results.get("website_analysis", {}).get("overall_scores", {}) or {}

        result.append({
            "id": j.id,
            "brand": j.brand,
            "site_url": j.site_url,
            "status": j.status.value if hasattr(j.status, "value") else str(j.status),
            "progress_pct": j.progress_pct,
            "current_step": j.current_step,
            "user_email": user.email if user else "unknown",
            "user_plan": user.plan if user else "unknown",
            "scores": scores,
            "has_results": j.results is not None,
            "share_token": j.share_token,
            "is_public": j.is_public,
            "error_message": j.error_message,
            "created_at": j.created_at.isoformat() if j.created_at else None,
            "completed_at": j.completed_at.isoformat() if j.completed_at else None,
        })

    return result


@router.post("/reports/{job_id}/toggle-public")
async def toggle_public(
    job_id: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Toggle public/example status of a report."""
    job = db.query(AnalysisJob).filter_by(id=job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Report not found")
    job.is_public = not job.is_public
    db.commit()
    return {"id": job.id, "brand": job.brand, "is_public": job.is_public}


@router.post("/reports/{job_id}/rerun")
async def admin_rerun(
    job_id: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Re-run any analysis as admin (no quota check)."""
    from gtm.storage.repository import JobRepository
    repo = JobRepository(db)
    job = repo.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Report not found")

    new_job = repo.create_job(
        tenant_id=job.tenant_id,
        site_url=job.site_url,
        brand=job.brand,
        config=job.config if isinstance(job.config, dict) else {},
    )

    from gtm.tasks.analysis import run_analysis_task
    run_analysis_task.delay(new_job.id)

    return {"job_id": new_job.id, "status": "pending", "brand": job.brand}
