"""Report endpoints — downloads, share links, public access."""

from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from gtm.api.deps import get_current_tenant, get_db, get_repo
from gtm.models.job import AnalysisJob, JobStatus
from gtm.storage.repository import JobRepository

router = APIRouter(prefix="/analyses", tags=["reports"])


# ── Helpers ──────────────────────────────────────────────────


def _get_completed_job(repo: JobRepository, job_id: str, tenant_id: str) -> AnalysisJob:
    """Get a completed job with tenant ownership check."""
    job = repo.get_job(job_id)
    if not job or job.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(status_code=409, detail="Analysis not complete")
    return job


# ── Authenticated download endpoints ─────────────────────────


@router.get("/{job_id}/report/json")
async def download_json(
    job_id: str,
    tenant_id: Annotated[str, Depends(get_current_tenant)],
    repo: Annotated[JobRepository, Depends(get_repo)],
):
    """Download the full analysis report as JSON."""
    job = _get_completed_job(repo, job_id, tenant_id)

    results = repo.get_results(job_id)
    if not results:
        raise HTTPException(status_code=404, detail="Results not found")

    brand_slug = job.brand.lower().replace(" ", "-")[:30]
    filename = f"launchkit-{brand_slug}-{job_id[:8]}.json"

    return Response(
        content=json.dumps(results, indent=2, default=str),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{job_id}/report/html")
async def download_html(
    job_id: str,
    tenant_id: Annotated[str, Depends(get_current_tenant)],
    repo: Annotated[JobRepository, Depends(get_repo)],
):
    """Download the analysis report as a self-contained HTML file."""
    job = _get_completed_job(repo, job_id, tenant_id)

    results = repo.get_results(job_id)
    if not results:
        raise HTTPException(status_code=404, detail="Results not found")

    from gtm.reports.html_generator import generate_html_report

    html_content = generate_html_report(results)
    brand_slug = job.brand.lower().replace(" ", "-")[:30]
    filename = f"launchkit-{brand_slug}-{job_id[:8]}.html"

    return Response(
        content=html_content,
        media_type="text/html",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{job_id}/report/pdf")
async def download_pdf(
    job_id: str,
    tenant_id: Annotated[str, Depends(get_current_tenant)],
    repo: Annotated[JobRepository, Depends(get_repo)],
):
    """Download the analysis report as a PDF.

    Renders the HTML report via Playwright and converts to PDF.
    """
    job = _get_completed_job(repo, job_id, tenant_id)

    results = repo.get_results(job_id)
    if not results:
        raise HTTPException(status_code=404, detail="Results not found")

    from gtm.reports.html_generator import generate_html_report

    html_content = generate_html_report(results)

    # Render to PDF via Playwright
    import asyncio
    from playwright.async_api import async_playwright

    async def _render_pdf(html: str) -> bytes:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            page = await browser.new_page()
            await page.set_content(html, wait_until="networkidle")
            pdf_bytes = await page.pdf(
                format="A4",
                margin={"top": "0.5in", "right": "0.5in", "bottom": "0.5in", "left": "0.5in"},
                print_background=True,
            )
            await browser.close()
            return pdf_bytes

    pdf_data = await _render_pdf(html_content)

    brand_slug = job.brand.lower().replace(" ", "-")[:30]
    filename = f"launchkit-{brand_slug}-{job_id[:8]}.pdf"

    return Response(
        content=pdf_data,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ── Share link management ────────────────────────────────────


@router.post("/{job_id}/share")
async def create_share_link(
    job_id: str,
    tenant_id: Annotated[str, Depends(get_current_tenant)],
    repo: Annotated[JobRepository, Depends(get_repo)],
):
    """Generate a public share link for a completed analysis."""
    job = repo.get_job(job_id)
    if not job or job.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(status_code=409, detail="Analysis not complete")

    token = repo.create_share_token(job_id, tenant_id)
    if not token:
        raise HTTPException(status_code=500, detail="Failed to create share link")

    return {
        "share_token": token,
        "share_url": f"/share/{token}",
        "is_public": True,
    }


@router.delete("/{job_id}/share")
async def revoke_share_link(
    job_id: str,
    tenant_id: Annotated[str, Depends(get_current_tenant)],
    repo: Annotated[JobRepository, Depends(get_repo)],
):
    """Revoke the public share link for an analysis."""
    success = repo.revoke_share_token(job_id, tenant_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"is_public": False}


# ── Public share endpoint (no auth required) ─────────────────


@router.get("/{job_id}/share-info")
async def get_share_info(
    job_id: str,
    tenant_id: Annotated[str, Depends(get_current_tenant)],
    repo: Annotated[JobRepository, Depends(get_repo)],
):
    """Get current share status for a job."""
    job = repo.get_job(job_id)
    if not job or job.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "is_public": job.is_public,
        "share_token": job.share_token,
        "share_url": f"/share/{job.share_token}" if job.share_token else None,
    }
