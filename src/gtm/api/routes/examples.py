"""Public examples endpoint — serves sample report gallery data."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from gtm.api.deps import get_db
from gtm.models.job import AnalysisJob, JobStatus

router = APIRouter(tags=["examples"])


@router.get("/examples")
async def list_examples(db: Session = Depends(get_db)):
    """Return publicly shared reports for the examples gallery.

    No authentication required. Returns a curated list of shared reports
    with summary data for preview cards.
    """
    # Exclude our own site from the gallery
    EXCLUDED_BRANDS = {"vclaunchkit", "vc launchkit"}

    jobs = (
        db.query(AnalysisJob)
        .filter_by(status=JobStatus.COMPLETED, is_public=True)
        .filter(AnalysisJob.share_token.isnot(None))
        .filter(~AnalysisJob.site_url.ilike("%vclaunchkit%"))
        .order_by(AnalysisJob.completed_at.desc())
        .limit(10)
        .all()
    )

    examples = []
    for job in jobs:
        results = job.results if isinstance(job.results, dict) else {}
        website = results.get("website_analysis", {})
        scores = website.get("overall_scores", {})
        exec_summary = results.get("executive_summary", {})
        overview = exec_summary.get("overview", "")

        # Determine industry tag from brand/URL
        brand_lower = job.brand.lower()
        url_lower = job.site_url.lower()
        combined = brand_lower + " " + url_lower
        if any(w in combined for w in ["dissertation", "scholarly", "academic", "research"]):
            industry = "EdTech"
        elif any(w in combined for w in ["consult", "agency", "service", "cossette"]):
            industry = "Consulting"
        elif any(w in combined for w in ["launch", "gtm", "market", "growth"]):
            industry = "MarTech"
        elif any(w in combined for w in ["clarity", "coach", "mentor", "wellness"]):
            industry = "Coaching"
        elif any(w in combined for w in ["dev", "api", "code", "linear", "github"]):
            industry = "Developer Tools"
        elif any(w in combined for w in ["mail", "email", "send", "resend"]):
            industry = "Email / SaaS"
        elif any(w in combined for w in ["data", "db", "planet", "scale"]):
            industry = "Infrastructure"
        elif any(w in combined for w in ["cal", "schedule", "meet"]):
            industry = "Scheduling"
        else:
            industry = "SaaS"

        # Truncate at sentence boundary to avoid mid-word cuts
        if len(overview) > 300:
            snippet = overview[:300]
            # Find the last sentence end within the snippet
            for sep in [". ", "! ", "? "]:
                last = snippet.rfind(sep)
                if last > 100:  # Ensure we keep a meaningful chunk
                    snippet = snippet[:last + 1]
                    break
            else:
                # No sentence break found; fall back to last space
                last_space = snippet.rfind(" ")
                if last_space > 100:
                    snippet = snippet[:last_space] + "..."
                else:
                    snippet = snippet + "..."
        else:
            snippet = overview

        examples.append({
            "brand": job.brand,
            "site_url": job.site_url,
            "share_token": job.share_token,
            "industry": industry,
            "scores": scores,
            "summary_snippet": snippet,
        })

    return examples
