"""Celery task for running the analysis pipeline.

The pipeline runs in two phases:

1. **Quick scan** (plan + crawl + analyze_pages)  ~3 minutes
   - Produces website scores and page analysis
   - Saved as ``quick_results`` on the job so users get early feedback

2. **Deep scan** (market_researcher ... synthesizer)  ~10-15 minutes
   - Continues from the quick-scan state
   - Produces the full report stored in ``results``
"""

from __future__ import annotations

import asyncio
import json
import logging

from gtm.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


def _extract_quick_results(state: dict) -> dict:
    """Distil the quick-scan state into a compact results dict."""
    website = state.get("website_analysis", {})
    return {
        "website_analysis": {
            "overall_scores": website.get("overall_scores", {}),
            "top_strengths": (website.get("top_strengths") or [])[:5],
            "top_weaknesses": (website.get("top_weaknesses") or [])[:5],
            "quick_wins": (website.get("quick_wins") or [])[:5],
        },
        "_quick": True,
    }


@celery_app.task(bind=True, name="gtm.tasks.run_analysis")
def run_analysis_task(self, job_id: str) -> None:
    """Run the analysis pipeline in two phases (quick then deep).

    Uses asyncio.run() for async execution inside the sync Celery task.
    """
    logger.info("Starting analysis task for job %s", job_id)

    from gtm.config import get_settings
    from gtm.models.job import JobStatus
    from gtm.storage.database import init_db
    from gtm.storage.redis_client import init_redis, publish_progress
    from gtm.storage.repository import JobRepository
    from gtm.storage.s3 import init_s3, save_job_artifacts

    settings = get_settings()

    # Initialize storage in worker process
    init_db(settings)
    init_redis(settings)
    init_s3(settings)

    from gtm.storage.database import get_session

    session_gen = get_session()
    session = next(session_gen)

    try:
        repo = JobRepository(session)
        job = repo.get_job(job_id)

        if not job:
            logger.error("Job %s not found", job_id)
            return

        # Mark as running
        repo.update_status(job_id, JobStatus.RUNNING, current_step="starting")

        config = job.config if isinstance(job.config, dict) else json.loads(job.config)

        # ── Phase 1: Quick scan (plan + crawl + analyze_pages) ────────
        quick_state = asyncio.run(
            _run_quick(settings, job_id, config)
        )

        # Extract and persist quick results so the API can serve them
        quick_report = _extract_quick_results(quick_state)
        safe_quick = json.loads(json.dumps(quick_report, default=str))
        repo.save_quick_results(job_id, safe_quick)

        publish_progress(
            job_id,
            event="quick_results",
            payload={
                "results": safe_quick,
                "pct": 35,
                "message": "Website analysis complete — scores available",
            },
        )
        logger.info("Quick scan results saved for job %s", job_id)

        # ── Phase 2: Deep scan (remaining steps) ─────────────────────
        full_state = asyncio.run(
            _run_deep(settings, job_id, config, quick_state)
        )

        # Extract report and sanitize (datetime objects break json.dumps)
        raw_report = full_state.get("report", {})
        report = json.loads(json.dumps(raw_report, default=str))

        # Store results in DB (critical)
        repo.complete_job(job_id, report)

        # Store artifacts in S3 (non-fatal)
        try:
            save_job_artifacts(job_id, report)
        except Exception:
            logger.warning("Failed to save S3 artifacts for job %s", job_id)

        # Save score snapshot for change tracking (non-fatal)
        try:
            _save_score_snapshot(session, job, report)
        except Exception:
            logger.warning("Failed to save score snapshot for job %s", job_id)

        publish_progress(
            job_id,
            event="complete",
            payload={"message": "Analysis complete", "pct": 100},
        )

        logger.info("Analysis task completed for job %s", job_id)

    except Exception as e:
        logger.exception("Analysis task failed for job %s", job_id)
        try:
            # Only mark failed if not already completed
            job = repo.get_job(job_id)
            if job and job.status != JobStatus.COMPLETED:
                repo.fail_job(job_id, str(e))
                publish_progress(
                    job_id,
                    event="error",
                    payload={"message": str(e)},
                )
        except Exception:
            logger.exception("Failed to update job status after error")

    finally:
        try:
            next(session_gen, None)
        except StopIteration:
            pass


def _save_score_snapshot(session, job, report: dict) -> None:
    """Save a score snapshot for change tracking."""
    import uuid
    from datetime import datetime, timezone

    from gtm.models.analytics import ScoreSnapshot

    scores = report.get("website_analysis", {}).get("overall_scores", {})
    if not scores:
        return

    vals = [v for v in scores.values() if isinstance(v, (int, float))]
    avg = round(sum(vals) / len(vals)) if vals else 0

    snapshot = ScoreSnapshot(
        id=str(uuid.uuid4()),
        user_id=job.tenant_id,
        job_id=job.id,
        site_url=job.site_url,
        brand=job.brand,
        clarity=scores.get("clarity", 0),
        audience_fit=scores.get("audience_fit", 0),
        conversion=scores.get("conversion", 0),
        seo=scores.get("seo", 0),
        ux=scores.get("ux", 0),
        overall_avg=avg,
        snapshot_at=datetime.now(timezone.utc),
    )
    session.add(snapshot)
    session.commit()


async def _run_quick(settings, job_id: str, config: dict) -> dict:
    """Run Phase 1: plan -> crawl -> analyze_pages."""
    from gtm.agents.workflow import run_quick_scan

    return await run_quick_scan(settings, job_id=job_id, config=config)


async def _run_deep(settings, job_id: str, config: dict, quick_state: dict) -> dict:
    """Run Phase 2: market_researcher -> ... -> synthesizer."""
    from gtm.agents.workflow import run_deep_scan

    return await run_deep_scan(
        settings, job_id=job_id, config=config, quick_state=quick_state
    )
