"""Base agent with LLM generation and validation."""

from __future__ import annotations

import json
import logging
from typing import Any

from gtm.config import Settings
from gtm.llm.base import LLMProvider
from gtm.llm.factory import get_provider
from gtm.llm.json_parser import extract_json
from gtm.llm.roles import build_system_prompt, get_role_config
from gtm.storage.redis_client import publish_progress


class BaseAgent:
    """Base class for all specialized agents."""

    name: str = "base"
    role: str = "analyst"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.logger = logging.getLogger(f"gtm.agents.{self.name}")

    def _get_provider(self) -> LLMProvider:
        return get_provider(self.settings, self.role)

    async def _generate(
        self,
        prompt: str,
        *,
        context: dict | None = None,
        response_format: str = "text",
        brand: str = "",
        audience: str = "",
    ) -> str:
        """Generate a response from the LLM."""
        role_cfg = get_role_config(self.role)
        system_prompt = build_system_prompt(self.role, brand=brand, audience=audience)

        messages: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt},
        ]

        if context:
            # Truncate context to avoid token limits
            ctx_str = json.dumps(context, indent=2, default=str)
            if len(ctx_str) > 6000:
                ctx_str = ctx_str[:6000] + "\n... (truncated)"
            messages.append({"role": "user", "content": f"Context:\n{ctx_str}"})

        messages.append({"role": "user", "content": prompt})

        provider = self._get_provider()
        max_tokens = (
            self.settings.max_tokens_analysis
            if self.role in ("analyst", "researcher", "orchestrator")
            else self.settings.max_tokens_generation
        )

        return await provider.generate(
            messages,
            temperature=role_cfg.temperature,
            max_tokens=max_tokens,
            response_format=response_format,
        )

    async def _generate_json(
        self,
        prompt: str,
        *,
        context: dict | None = None,
        required_keys: list[str] | None = None,
        min_counts: dict[str, int] | None = None,
        brand: str = "",
        audience: str = "",
    ) -> dict:
        """Generate JSON with validation and one retry on failure.

        If validation fails after retry, returns the best result available
        rather than discarding partial data (e.g., 3 experiments is better
        than 0 experiments).
        """
        required_keys = required_keys or []
        min_counts = min_counts or {}

        def _ok(d: Any) -> bool:
            if not isinstance(d, dict):
                return False
            for k in required_keys:
                if k not in d:
                    return False
            for k, n in min_counts.items():
                val = d.get(k)
                if isinstance(val, list) and len(val) < n:
                    return False
            return True

        def _has_keys(d: Any) -> bool:
            """Check if result has the required keys (ignoring min_counts)."""
            if not isinstance(d, dict):
                return False
            return all(k in d for k in required_keys)

        raw = await self._generate(
            prompt,
            context=context,
            response_format="json",
            brand=brand,
            audience=audience,
        )
        first_result = extract_json(raw)

        if _ok(first_result):
            return first_result

        # Log what we got on first attempt
        if isinstance(first_result, dict):
            counts = {k: len(v) for k, v in first_result.items() if isinstance(v, list)}
            self.logger.warning(
                "%s: first attempt incomplete (counts=%s, needed=%s) — retrying",
                self.name, counts, min_counts,
            )
        else:
            self.logger.warning("%s: first attempt returned non-dict — retrying", self.name)

        # Retry with explicit instruction
        retry_prompt = (
            prompt
            + "\n\nIMPORTANT: Your previous response did not meet requirements. "
            "Ensure ALL required keys are present and lists have enough items. "
            "Return ONLY the JSON object."
        )
        raw = await self._generate(
            retry_prompt,
            context=context,
            response_format="json",
            brand=brand,
            audience=audience,
        )
        retry_result = extract_json(raw)

        if _ok(retry_result):
            return retry_result

        # Return the BEST result we have — prefer retry if it has keys, else first
        # This ensures partial data (e.g., 3 experiments) is kept, not discarded
        if isinstance(retry_result, dict) and _has_keys(retry_result):
            self.logger.warning(
                "%s: retry still incomplete but has data — using partial result",
                self.name,
            )
            return retry_result
        if isinstance(first_result, dict) and _has_keys(first_result):
            self.logger.warning(
                "%s: using first attempt partial result",
                self.name,
            )
            return first_result

        self.logger.error("%s: both attempts failed to produce valid JSON", self.name)
        return retry_result if isinstance(retry_result, dict) else (first_result if isinstance(first_result, dict) else {})

    async def _report_progress(
        self, job_id: str, pct: int, message: str
    ) -> None:
        """Publish progress event via Redis."""
        try:
            publish_progress(
                job_id,
                event="progress",
                payload={
                    "step": self.name,
                    "pct": pct,
                    "message": message,
                },
            )
        except Exception:
            self.logger.debug("Could not publish progress (Redis may not be available)")

    async def run(self, state: dict) -> dict:
        """Execute this agent's step. Subclasses must override."""
        raise NotImplementedError
