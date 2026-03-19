"""Anthropic Claude LLM provider."""

from __future__ import annotations

import logging

from anthropic import AsyncAnthropic
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class AnthropicProvider:
    """Anthropic Messages API implementation."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: str = "text",
    ) -> str:
        """Generate a completion via Anthropic Messages API."""

        # Separate system prompt from conversation messages
        system_prompt = ""
        user_messages: list[dict[str, str]] = []

        for msg in messages:
            if msg["role"] == "system":
                system_prompt += msg["content"] + "\n"
            else:
                user_messages.append({"role": msg["role"], "content": msg["content"]})

        # Ensure at least one user message
        if not user_messages:
            user_messages = [{"role": "user", "content": "Please proceed."}]

        if response_format == "json":
            # Append JSON instruction to last user message
            user_messages[-1]["content"] += (
                "\n\nIMPORTANT: Return ONLY valid JSON. No markdown, no explanation."
            )

        try:
            response = await self.client.messages.create(
                model=self.model,
                system=system_prompt.strip(),
                messages=user_messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        except Exception:
            logger.exception("Anthropic messages.create failed (model=%s)", self.model)
            raise

        return response.content[0].text
