"""Prometheus metrics for observability."""

from __future__ import annotations

try:
    from prometheus_client import Counter, Histogram

    analyses_started = Counter(
        "gtm_analyses_started_total",
        "Total analysis jobs started",
    )
    analyses_completed = Counter(
        "gtm_analyses_completed_total",
        "Total analysis jobs completed successfully",
    )
    analyses_failed = Counter(
        "gtm_analyses_failed_total",
        "Total analysis jobs that failed",
    )
    analysis_duration = Histogram(
        "gtm_analysis_duration_seconds",
        "Time to complete an analysis",
        buckets=[60, 120, 300, 600, 900, 1200],
    )
    llm_request_duration = Histogram(
        "gtm_llm_request_duration_seconds",
        "Time for a single LLM API call",
        labelnames=["provider", "role"],
        buckets=[1, 2, 5, 10, 20, 30, 60],
    )
    llm_errors = Counter(
        "gtm_llm_errors_total",
        "Total LLM API errors",
        labelnames=["provider", "role"],
    )

except ImportError:
    # prometheus_client is optional — provide no-op fallbacks
    class _NoOp:
        def inc(self, *a, **kw): pass
        def observe(self, *a, **kw): pass
        def labels(self, *a, **kw): return self

    analyses_started = _NoOp()  # type: ignore[assignment]
    analyses_completed = _NoOp()  # type: ignore[assignment]
    analyses_failed = _NoOp()  # type: ignore[assignment]
    analysis_duration = _NoOp()  # type: ignore[assignment]
    llm_request_duration = _NoOp()  # type: ignore[assignment]
    llm_errors = _NoOp()  # type: ignore[assignment]
