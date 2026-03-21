"""OpenAI LLM provider using the Responses API."""

from __future__ import annotations

import base64
import logging

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class OpenAIProvider:
    """OpenAI Responses API implementation."""

    def __init__(self, api_key: str, model: str = "gpt-4.1-mini"):
        self.client = AsyncOpenAI(api_key=api_key)
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
        """Generate a completion via OpenAI Responses API."""

        # Build single input string from message list
        parts: list[str] = []
        for msg in messages:
            role = msg.get("role", "user").upper()
            content = msg.get("content", "")
            parts.append(f"{role}:\n{content}")
        input_text = "\n\n".join(parts)

        if response_format == "json":
            input_text += "\n\nIMPORTANT: Return ONLY valid JSON. No markdown, no explanation."

        # Build kwargs — reasoning/text params only for o-series models
        kwargs: dict = {
            "model": self.model,
            "input": input_text,
            "max_output_tokens": max_tokens,
        }
        is_reasoning_model = self.model.startswith("o")
        if is_reasoning_model:
            effort = "low" if response_format == "json" else "medium"
            kwargs["reasoning"] = {"effort": effort}

        try:
            resp = await self.client.responses.create(**kwargs)
        except Exception:
            logger.exception("OpenAI responses.create failed (model=%s)", self.model)
            raise

        # Extract text from response
        content = getattr(resp, "output_text", None)
        if content is None:
            try:
                content = "".join(
                    seg.get("content", "") if isinstance(seg, dict) else str(seg)
                    for seg in getattr(resp, "output", [])
                )
            except Exception:
                content = ""

        return content or ""

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
        """Generate a completion with an image attachment (vision).

        Uses the Responses API 'message' input type with image_url content.
        """
        # Build system and user text from messages
        system_text = ""
        user_text = ""
        for msg in messages:
            if msg.get("role") == "system":
                system_text += msg.get("content", "") + "\n"
            else:
                user_text += msg.get("content", "") + "\n"

        b64 = base64.standard_b64encode(image_data).decode("utf-8")
        data_url = f"data:{media_type};base64,{b64}"

        # Responses API: use 'message' type with content array for vision
        input_items = []
        if system_text.strip():
            input_items.append({
                "role": "developer",
                "content": system_text.strip(),
            })
        input_items.append({
            "role": "user",
            "content": [
                {"type": "input_image", "image_url": data_url},
                {"type": "input_text", "text": user_text + "\nIMPORTANT: Return ONLY valid JSON. No markdown, no explanation."},
            ],
        })

        try:
            resp = await self.client.responses.create(
                model=self.model,
                input=input_items,
                max_output_tokens=max_tokens,
            )
        except Exception:
            logger.exception("OpenAI vision call failed (model=%s)", self.model)
            raise

        content = getattr(resp, "output_text", None)
        if content is None:
            try:
                content = "".join(
                    seg.get("content", "") if isinstance(seg, dict) else str(seg)
                    for seg in getattr(resp, "output", [])
                )
            except Exception:
                content = ""

        return content or ""
