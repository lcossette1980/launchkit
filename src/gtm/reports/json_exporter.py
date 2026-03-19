"""Schema-validated JSON export."""

from __future__ import annotations

import json
from typing import Any

from gtm.schemas.report import FullReportSchema


def validate_and_export(results: dict[str, Any]) -> str:
    """Validate results against FullReportSchema and return formatted JSON.

    If validation fails, returns the raw results as-is (best effort).
    """
    try:
        report = FullReportSchema.model_validate(results)
        return report.model_dump_json(indent=2, by_alias=True)
    except Exception:
        return json.dumps(results, indent=2, default=str)


def export_section(results: dict[str, Any], section: str) -> str:
    """Export a single section of the report as JSON."""
    data = results.get(section, {})
    return json.dumps(data, indent=2, default=str)
