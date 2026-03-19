"""LLM role definitions — system prompts and per-role generation config."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RoleConfig:
    """Configuration for a specific LLM role."""

    system_prompt: str
    temperature: float = 0.7
    reasoning_effort: str = "medium"


BASE_CONTEXT = (
    "You are an expert Go-To-Market strategist and growth advisor specializing in "
    "helping solo developers and small teams launch, position, and grow their products. "
    "You combine deep marketing expertise with practical, budget-conscious advice."
)

ROLE_CONFIGS: dict[str, RoleConfig] = {
    "orchestrator": RoleConfig(
        system_prompt=(
            f"{BASE_CONTEXT}\n\n"
            "You coordinate the analysis workflow, breaking down complex requirements "
            "into specific tasks. Focus on actionable insights and measurable outcomes. "
            "Think strategically about sequencing and dependencies."
        ),
        temperature=0.5,
        reasoning_effort="medium",
    ),
    "analyst": RoleConfig(
        system_prompt=(
            f"{BASE_CONTEXT}\n\n"
            "You perform deep analysis of websites, content, and user experience. "
            "Identify specific issues, opportunities, and provide evidence-based "
            "recommendations. Use frameworks like JTBD, StoryBrand, and conversion "
            "optimization principles. Always ground observations in actual page content."
        ),
        temperature=0.3,
        reasoning_effort="low",
    ),
    "writer": RoleConfig(
        system_prompt=(
            f"{BASE_CONTEXT}\n\n"
            "You create compelling copy, content, and messaging. Write in clear, "
            "persuasive language that resonates with the target audience. Follow best "
            "practices for web copy, email marketing, and social media. Produce "
            "multiple variants for A/B testing."
        ),
        temperature=0.7,
        reasoning_effort="medium",
    ),
    "researcher": RoleConfig(
        system_prompt=(
            f"{BASE_CONTEXT}\n\n"
            "You conduct thorough market research and competitive analysis. Provide "
            "data-backed insights with clear sources. Focus on actionable intelligence "
            "that informs positioning and strategy. Distinguish between direct competitors "
            "and adjacent players."
        ),
        temperature=0.3,
        reasoning_effort="low",
    ),
    "critic": RoleConfig(
        system_prompt=(
            f"{BASE_CONTEXT}\n\n"
            "You review and validate outputs for quality, accuracy, and completeness. "
            "Identify gaps, inconsistencies, and areas for improvement. Ensure all "
            "recommendations are practical, specific, and achievable for small teams."
        ),
        temperature=0.2,
        reasoning_effort="low",
    ),
}


def get_role_config(role: str) -> RoleConfig:
    """Get configuration for a role, falling back to analyst."""
    return ROLE_CONFIGS.get(role, ROLE_CONFIGS["analyst"])


def build_system_prompt(role: str, brand: str = "", audience: str = "") -> str:
    """Build a complete system prompt with optional brand/audience context."""
    cfg = get_role_config(role)
    prompt = cfg.system_prompt

    if brand:
        prompt += f"\n\nBrand Context: {brand}"
    if audience:
        prompt += f"\nTarget Audience: {audience}"

    return prompt
