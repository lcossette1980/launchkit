"""Analysis endpoints — start, status, results, list, rerun."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from gtm.api.deps import get_current_tenant, get_current_user_or_dev, get_db, get_repo
from gtm.api.filters import filter_report_by_plan
from gtm.models.job import AnalysisJob, JobStatus
from gtm.models.user import User
from gtm.schemas.config import AnalysisRequest
from gtm.storage.repository import JobRepository
from gtm.storage.user_repository import UserRepository

router = APIRouter(prefix="/analyses", tags=["analyses"])


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class JobCreatedResponse(BaseModel):
    job_id: str
    status: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress_pct: int
    current_step: str
    brand: str
    site_url: str
    error_message: str | None = None
    quick_results: dict | None = None


class JobListItem(BaseModel):
    job_id: str
    status: str
    brand: str
    site_url: str
    progress_pct: int
    created_at: str | None = None
    completed_at: str | None = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_job_for_tenant(repo: JobRepository, job_id: str, tenant_id: str) -> AnalysisJob:
    """Fetch a job and verify tenant ownership. Raises 404 on mismatch."""
    job = repo.get_job(job_id)
    if not job or job.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("", status_code=status.HTTP_202_ACCEPTED, response_model=JobCreatedResponse)
async def start_analysis(
    request: AnalysisRequest,
    user: User = Depends(get_current_user_or_dev),
    tenant_id: str = Depends(get_current_tenant),
    repo: JobRepository = Depends(get_repo),
    db: Session = Depends(get_db),
):
    """Start a new GTM analysis.

    Checks usage quota before creating job.
    Returns 202 with the job_id.
    """
    # Check usage quota
    user_repo = UserRepository(db)
    quota = user_repo.check_quota(user)

    if not quota["allowed"]:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": "Monthly analysis limit reached",
                "used": quota["used"],
                "limit": quota["limit"],
                "plan": quota["plan"],
                "upgrade_url": "/api/v1/billing/checkout",
            },
        )

    # Enforce plan limits on pages/competitors
    config = request.model_dump(mode="json")
    config["site_url"] = str(request.site_url)

    max_pages = config.get("max_pages_to_scan", 50)
    max_comp = config.get("max_competitors", 5)
    config["max_pages_to_scan"] = min(max_pages, quota["max_pages"])
    config["max_competitors"] = min(max_comp, quota["max_competitors"])

    job = repo.create_job(
        tenant_id=tenant_id,
        site_url=config["site_url"],
        brand=request.brand,
        config=config,
    )

    # Increment usage
    user_repo.increment_usage(user.id)

    # Dispatch to Celery
    from gtm.tasks.analysis import run_analysis_task

    run_analysis_task.delay(job.id)

    return JobCreatedResponse(job_id=job.id, status="pending")


@router.get("/{job_id}", response_model=dict)
async def get_analysis(
    job_id: str,
    user: User = Depends(get_current_user_or_dev),
    tenant_id: str = Depends(get_current_tenant),
    repo: JobRepository = Depends(get_repo),
):
    """Get analysis results, filtered by user's plan tier."""
    job = _get_job_for_tenant(repo, job_id, tenant_id)

    if job.status == JobStatus.COMPLETED:
        results = repo.get_results(job_id)
        if results:
            return filter_report_by_plan(results, user.plan)
        raise HTTPException(status_code=404, detail="Results not found")

    if job.status == JobStatus.FAILED:
        raise HTTPException(status_code=422, detail=job.error_message or "Analysis failed")

    # Return quick results if available while analysis is still running
    resp: dict = {
        "status": job.status.value,
        "progress_pct": job.progress_pct,
        "current_step": job.current_step,
    }
    if job.status == JobStatus.RUNNING and job.quick_results:
        resp["quick_results"] = job.quick_results

    return resp


@router.get("/{job_id}/status", response_model=JobStatusResponse)
async def get_status(
    job_id: str,
    tenant_id: str = Depends(get_current_tenant),
    repo: JobRepository = Depends(get_repo),
):
    """Get job status and progress."""
    job = _get_job_for_tenant(repo, job_id, tenant_id)

    return JobStatusResponse(
        job_id=job.id,
        status=job.status.value,
        progress_pct=job.progress_pct,
        current_step=job.current_step,
        brand=job.brand,
        site_url=job.site_url,
        error_message=job.error_message,
        quick_results=job.quick_results,
    )


@router.get("/{job_id}/stream")
async def stream_status(
    job_id: str,
    tenant_id: str = Depends(get_current_tenant),
    repo: JobRepository = Depends(get_repo),
):
    """SSE stream of analysis progress events."""
    from fastapi.responses import StreamingResponse

    from gtm.api.sse import stream_progress

    job = _get_job_for_tenant(repo, job_id, tenant_id)

    return StreamingResponse(
        stream_progress(job_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/{job_id}/rerun", status_code=status.HTTP_202_ACCEPTED, response_model=JobCreatedResponse)
async def rerun_analysis(
    job_id: str,
    user: User = Depends(get_current_user_or_dev),
    tenant_id: str = Depends(get_current_tenant),
    repo: JobRepository = Depends(get_repo),
    db: Session = Depends(get_db),
):
    """Re-run an analysis with the same config."""
    job = _get_job_for_tenant(repo, job_id, tenant_id)

    # Check quota
    user_repo = UserRepository(db)
    quota = user_repo.check_quota(user)
    if not quota["allowed"]:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": "Monthly analysis limit reached",
                "used": quota["used"],
                "limit": quota["limit"],
                "plan": quota["plan"],
            },
        )

    new_job = repo.create_job(
        tenant_id=tenant_id,
        site_url=job.site_url,
        brand=job.brand,
        config=job.config if isinstance(job.config, dict) else {},
    )

    user_repo.increment_usage(user.id)

    from gtm.tasks.analysis import run_analysis_task

    run_analysis_task.delay(new_job.id)

    return JobCreatedResponse(job_id=new_job.id, status="pending")


@router.get("", response_model=list[JobListItem])
async def list_analyses(
    tenant_id: str = Depends(get_current_tenant),
    repo: JobRepository = Depends(get_repo),
    limit: int = 20,
    offset: int = 0,
):
    """List analyses for the authenticated tenant."""
    jobs = repo.list_jobs(tenant_id, limit=limit, offset=offset)
    return [
        JobListItem(
            job_id=j.id,
            status=j.status.value,
            brand=j.brand,
            site_url=j.site_url,
            progress_pct=j.progress_pct,
            created_at=j.created_at.isoformat() if j.created_at else None,
            completed_at=j.completed_at.isoformat() if j.completed_at else None,
        )
        for j in jobs
    ]
