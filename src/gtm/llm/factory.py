"""LLM provider factory."""

from __future__ import annotations

from functools import lru_cache

from gtm.config import Settings
from gtm.llm.anthropic_provider import AnthropicProvider
from gtm.llm.base import LLMProvider
from gtm.llm.openai_provider import OpenAIProvider


def get_provider(settings: Settings, role: str = "analyst") -> LLMProvider:
    """Create an LLM provider for the given role.

    Model selection:
    1. Check settings.role_models for a role-specific override
    2. Fall back to settings.default_model
    """
    model = settings.role_models.get(role, settings.default_model)

    if settings.llm_provider == "anthropic":
        return AnthropicProvider(api_key=settings.anthropic_api_key, model=model)

    return OpenAIProvider(api_key=settings.openai_api_key, model=model)


@lru_cache(maxsize=16)
def _cached_provider(provider_type: str, api_key: str, model: str) -> LLMProvider:
    """Cache provider instances to avoid re-creating clients per call."""
    if provider_type == "anthropic":
        return AnthropicProvider(api_key=api_key, model=model)
    return OpenAIProvider(api_key=api_key, model=model)


def get_cached_provider(settings: Settings, role: str = "analyst") -> LLMProvider:
    """Get a cached provider instance."""
    model = settings.role_models.get(role, settings.default_model)
    return _cached_provider(settings.llm_provider, settings.openai_api_key, model)
