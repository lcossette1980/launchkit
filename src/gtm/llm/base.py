"""LLM provider protocol and shared types."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMProvider(Protocol):
    """Interface that all LLM providers must implement."""

    async def generate(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: str = "text",
    ) -> str:
        """Generate a completion. Always returns raw string.

        Args:
            messages: List of {"role": "system"|"user", "content": "..."} dicts.
            temperature: Sampling temperature.
            max_tokens: Maximum output tokens.
            response_format: "text" or "json" — provider may add hints.

        Returns:
            Raw text response from the model.
        """
        ...
