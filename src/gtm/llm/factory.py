"""LLM provider factory."""

from __future__ import annotations

from functools import lru_cache

from gtm.config import Settings
from gtm.llm.anthropic_provider import AnthropicProvider
from gtm.llm.base import LLMProvider
from gtm.llm.openai_provider import OpenAIProvider


@lru_cache(maxsize=16)
def _cached_provider(provider_type: str, api_key: str, model: str) -> LLMProvider:
    """Cache provider instances to avoid re-creating clients per call."""
    if provider_type == "anthropic":
        return AnthropicProvider(api_key=api_key, model=model)
    return OpenAIProvider(api_key=api_key, model=model)


def get_provider(settings: Settings, role: str = "analyst") -> LLMProvider:
    """Get a cached LLM provider for the given role.

    Model selection:
    1. Check settings.role_models for a role-specific override
    2. Fall back to settings.default_model

    Uses provider-specific API key based on settings.llm_provider.
    """
    model = settings.role_models.get(role, settings.default_model)
    api_key = (
        settings.anthropic_api_key
        if settings.llm_provider == "anthropic"
        else settings.openai_api_key
    )
    return _cached_provider(settings.llm_provider, api_key, model)


# Keep backward-compatible alias
get_cached_provider = get_provider
