"""Report filtering by plan tier."""

from __future__ import annotations


def filter_report_by_plan(results: dict, plan: str) -> dict:
    """Return full report for paid plans, teaser for free.

    Free teaser includes:
    - Executive summary overview
    - Top 3 priorities
    - Overall website scores
    - Brand info
    - Metadata
    - _teaser flag for frontend to show upgrade CTAs
    """
    if plan in ("pro", "agency"):
        return results

    exec_summary = results.get("executive_summary", {})

    return {
        "brand_info": results.get("brand_info"),
        "executive_summary": {
            "overview": exec_summary.get("overview"),
            "top_priorities": exec_summary.get("top_priorities", [])[:3],
            # key_findings deliberately omitted
        },
        "website_analysis": {
            "overall_scores": results.get("website_analysis", {}).get(
                "overall_scores"
            ),
            # pages_analyzed, top_strengths, etc. omitted
        },
        "metadata": results.get("metadata"),
        "_teaser": True,
    }
