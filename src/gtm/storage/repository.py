"""Job repository — CRUD operations for analysis jobs."""

from __future__ import annotations

import json
import logging
import secrets
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from gtm.models.job import AnalysisJob, JobStatus
from gtm.storage.redis_client import cache_get, cache_set

logger = logging.getLogger(__name__)


class JobRepository:
    """CRUD for analysis jobs with Redis caching."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create_job(
        self,
        tenant_id: str,
        site_url: str,
        brand: str,
        config: dict,
    ) -> AnalysisJob:
        """Create a new pending analysis job."""
        job = AnalysisJob(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            site_url=site_url,
            brand=brand,
            status=JobStatus.PENDING,
            config=config,
        )
        self.session.add(job)
        self.session.commit()
        return job

    def get_job(self, job_id: str) -> AnalysisJob | None:
        """Get a job by ID."""
        return self.session.query(AnalysisJob).filter_by(id=job_id).first()

    def get_results(self, job_id: str) -> dict | None:
        """Get job results — Redis cache first, then DB."""
        # Check cache
        cached = cache_get(f"job:{job_id}")
        if cached:
            return cached

        # Check DB
        job = self.get_job(job_id)
        if job and job.results:
            results = job.results if isinstance(job.results, dict) else json.loads(job.results)
            cache_set(f"job:{job_id}", results)
            return results

        return None

    def update_status(
        self,
        job_id: str,
        status: JobStatus,
        *,
        progress_pct: int | None = None,
        current_step: str | None = None,
    ) -> None:
        """Update job status and optional progress."""
        job = self.get_job(job_id)
        if not job:
            return
        job.status = status
        if progress_pct is not None:
            job.progress_pct = progress_pct
        if current_step is not None:
            job.current_step = current_step
        self.session.commit()

    def complete_job(self, job_id: str, results: dict) -> None:
        """Mark a job as completed with results."""
        job = self.get_job(job_id)
        if not job:
            return
        job.status = JobStatus.COMPLETED
        # Round-trip through JSON to ensure all values are serializable
        safe_results = json.loads(json.dumps(results, default=str))
        job.results = safe_results
        job.progress_pct = 100
        job.current_step = "completed"
        job.completed_at = datetime.now(timezone.utc)
        self.session.commit()

        # Cache results (non-fatal)
        try:
            cache_set(f"job:{job_id}", safe_results)
        except Exception:
            logger.warning("Failed to cache results for job %s", job_id)

    def save_quick_results(self, job_id: str, results: dict) -> None:
        """Persist partial quick-scan results so the API can serve them early."""
        job = self.get_job(job_id)
        if not job:
            return
        safe = json.loads(json.dumps(results, default=str))
        job.quick_results = safe
        job.progress_pct = 35
        job.current_step = "analyze_pages"
        self.session.commit()

    def fail_job(self, job_id: str, error_message: str) -> None:
        """Mark a job as failed."""
        job = self.get_job(job_id)
        if not job:
            return
        job.status = JobStatus.FAILED
        job.error_message = error_message
        job.current_step = "failed"
        self.session.commit()

    def list_jobs(
        self,
        tenant_id: str,
        *,
        status: JobStatus | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[AnalysisJob]:
        """List jobs for a tenant with optional status filter."""
        query = self.session.query(AnalysisJob).filter_by(tenant_id=tenant_id)
        if status:
            query = query.filter_by(status=status)
        return (
            query.order_by(AnalysisJob.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    # ── Share tokens ──────────────────────────────────────

    def create_share_token(self, job_id: str, tenant_id: str) -> str | None:
        """Generate a share token for a job. Returns the token or None if job not found."""
        job = self.get_job(job_id)
        if not job or job.tenant_id != tenant_id:
            return None

        if job.share_token:
            return job.share_token

        token = secrets.token_urlsafe(32)
        job.share_token = token
        job.is_public = True
        self.session.commit()
        return token

    def revoke_share_token(self, job_id: str, tenant_id: str) -> bool:
        """Remove share token from a job."""
        job = self.get_job(job_id)
        if not job or job.tenant_id != tenant_id:
            return False
        job.share_token = None
        job.is_public = False
        self.session.commit()
        return True

    def get_job_by_share_token(self, token: str) -> AnalysisJob | None:
        """Get a job by its public share token."""
        return (
            self.session.query(AnalysisJob)
            .filter_by(share_token=token, is_public=True)
            .first()
        )
