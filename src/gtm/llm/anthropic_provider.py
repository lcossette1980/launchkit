"""Anthropic Claude LLM provider."""

from __future__ import annotations

import base64
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

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_with_image(
        self,
        messages: list[dict],
        image_data: bytes,
        *,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        media_type: str = "image/png",
    ) -> str:
        """Generate a completion with an image attachment (vision)."""
        system_prompt = ""
        user_content_parts: list[dict] = []

        for msg in messages:
            if msg["role"] == "system":
                system_prompt += msg["content"] + "\n"
            elif msg["role"] == "user":
                user_content_parts.append({"type": "text", "text": msg["content"]})

        # Add the image as the first content block
        b64 = base64.standard_b64encode(image_data).decode("utf-8")
        image_block = {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": b64,
            },
        }

        try:
            response = await self.client.messages.create(
                model=self.model,
                system=system_prompt.strip(),
                messages=[{
                    "role": "user",
                    "content": [image_block] + user_content_parts,
                }],
                max_tokens=max_tokens,
                temperature=temperature,
            )
        except Exception:
            logger.exception("Anthropic vision call failed (model=%s)", self.model)
            raise

        return response.content[0].text
