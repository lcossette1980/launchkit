"""LangGraph workflow — wires all agents into a sequential pipeline.

Flow:
  plan → crawl → analyze_pages → research_market → analyze_competitors
  → generate_strategy → create_experiments → produce_copy → synthesize → END
"""

from __future__ import annotations

import logging
from typing import Any

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from gtm.agents.competitor_analyzer import CompetitorAnalyzerAgent
from gtm.agents.copywriter import CopywriterAgent
from gtm.agents.crawler import CrawlerAgent
from gtm.agents.experimenter import ExperimenterAgent
from gtm.agents.market_researcher import MarketResearcherAgent
from gtm.agents.page_analyzer import PageAnalyzerAgent
from gtm.agents.planner import PlannerAgent
from gtm.agents.strategist import StrategistAgent
from gtm.agents.synthesizer import SynthesizerAgent
from gtm.config import Settings

logger = logging.getLogger(__name__)

# Node names (order matters for the linear chain)
STEPS = [
    "plan",
    "crawl",
    "analyze_pages",
    "research_market",
    "analyze_competitors",
    "generate_strategy",
    "create_experiments",
    "produce_copy",
    "synthesize",
]

# Map node name → agent class
AGENT_CLASSES = {
    "plan": PlannerAgent,
    "crawl": CrawlerAgent,
    "analyze_pages": PageAnalyzerAgent,
    "research_market": MarketResearcherAgent,
    "analyze_competitors": CompetitorAnalyzerAgent,
    "generate_strategy": StrategistAgent,
    "create_experiments": ExperimenterAgent,
    "produce_copy": CopywriterAgent,
    "synthesize": SynthesizerAgent,
}


def _save_quick_results(state: dict[str, Any]) -> None:
    """After page_analyzer, save partial results so users see scores early."""
    job_id = state.get("job_id")
    if not job_id:
        return

    try:
        from gtm.storage.redis_client import publish_progress

        website = state.get("website_analysis", {})
        quick = {
            "website_analysis": {
                "overall_scores": website.get("overall_scores", {}),
                "top_strengths": (website.get("top_strengths") or [])[:5],
                "top_weaknesses": (website.get("top_weaknesses") or [])[:5],
                "quick_wins": (website.get("quick_wins") or [])[:5],
            },
            "_quick": True,
        }

        # Publish as a special progress event the frontend can render
        publish_progress(
            job_id,
            event="quick_results",
            payload={"results": quick, "message": "Website analysis complete — scores available"},
        )
        logger.info("Published quick results for job %s", job_id)
    except Exception:
        logger.warning("Failed to publish quick results for job %s", job_id)


# Progress percentages per step
STEP_PROGRESS = {
    "plan": 5,
    "crawl": 15,
    "analyze_pages": 35,
    "research_market": 50,
    "analyze_competitors": 65,
    "generate_strategy": 75,
    "create_experiments": 82,
    "produce_copy": 90,
    "synthesize": 97,
}


def _make_node(agent_cls: type, settings: Settings, step_name: str):
    """Return an async node function that runs the given agent."""
    agent = agent_cls(settings)

    async def node_fn(state: dict[str, Any]) -> dict[str, Any]:
        logger.info("Running step: %s", agent.name)

        # Publish progress update
        try:
            from gtm.storage.redis_client import publish_progress

            job_id = state.get("job_id")
            pct = STEP_PROGRESS.get(step_name, 0)
            if job_id:
                publish_progress(job_id, event="progress", payload={
                    "step": step_name,
                    "pct": pct,
                    "message": f"Running: {agent.name}",
                })
        except Exception:
            pass

        try:
            result = await agent.run(state)

            # After page analysis, publish quick results
            if step_name == "analyze_pages":
                _save_quick_results(result)

            return result
        except Exception:
            logger.exception("Step %s failed", agent.name)
            state.setdefault("errors", []).append(agent.name)
            return state

    node_fn.__name__ = agent_cls.name
    return node_fn


def build_workflow(settings: Settings) -> StateGraph:
    """Build and return the compiled LangGraph workflow.

    The graph is a simple linear chain:
        plan → crawl → analyze_pages → ... → synthesize → END

    Each node receives the full state dict, mutates it, and passes it on.
    A MemorySaver checkpointer allows resuming from the last successful step.
    """
    graph = StateGraph(dict)

    # Register nodes
    for step_name in STEPS:
        agent_cls = AGENT_CLASSES[step_name]
        graph.add_node(step_name, _make_node(agent_cls, settings, step_name))

    # Set entry point
    graph.set_entry_point(STEPS[0])

    # Chain edges: each step flows to the next
    for i in range(len(STEPS) - 1):
        graph.add_edge(STEPS[i], STEPS[i + 1])

    # Final step → END
    graph.add_edge(STEPS[-1], END)

    return graph


def compile_workflow(settings: Settings):
    """Build, compile, and return the runnable workflow with checkpointing."""
    graph = build_workflow(settings)
    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)


async def run_analysis(
    settings: Settings,
    *,
    job_id: str,
    config: dict[str, Any],
) -> dict[str, Any]:
    """Run the full analysis pipeline.

    Args:
        settings: Application settings.
        job_id: Unique job identifier for progress tracking.
        config: Analysis configuration dict containing at minimum:
            - site_url: str
            - brand: str
            - audience_primary: str
            And optionally: audience_secondary, main_offers, usp_key,
            business_size, monthly_budget, max_pages_to_scan, max_competitors,
            analysis_depth.

    Returns:
        The final state dict with the assembled report under state["report"].
    """
    workflow = compile_workflow(settings)

    initial_state: dict[str, Any] = {
        "config": config,
        "job_id": job_id,
        "errors": [],
    }

    thread_config = {"configurable": {"thread_id": job_id}}

    logger.info("Starting analysis pipeline for job %s (%s)", job_id, config.get("brand"))
    result = await workflow.ainvoke(initial_state, config=thread_config)
    logger.info("Analysis pipeline complete for job %s", job_id)

    return result


# ---------------------------------------------------------------------------
# Quick / Deep split — used by the Celery task for two-phase execution
# ---------------------------------------------------------------------------

# Steps included in the quick scan (first 3 pipeline nodes)
QUICK_STEPS = STEPS[:3]  # plan, crawl, analyze_pages
# Steps for the deep scan (remaining 6 nodes)
DEEP_STEPS = STEPS[3:]   # market_researcher … synthesizer


def _build_partial_workflow(
    settings: Settings,
    step_names: list[str],
) -> StateGraph:
    """Build a LangGraph sub-workflow containing only the given steps."""
    graph = StateGraph(dict)

    for step_name in step_names:
        agent_cls = AGENT_CLASSES[step_name]
        graph.add_node(step_name, _make_node(agent_cls, settings, step_name))

    graph.set_entry_point(step_names[0])

    for i in range(len(step_names) - 1):
        graph.add_edge(step_names[i], step_names[i + 1])

    graph.add_edge(step_names[-1], END)

    return graph


async def run_quick_scan(
    settings: Settings,
    *,
    job_id: str,
    config: dict[str, Any],
) -> dict[str, Any]:
    """Run the first 3 pipeline steps (plan, crawl, analyze_pages).

    Returns the intermediate state dict with website analysis data available
    for early display to the user.
    """
    graph = _build_partial_workflow(settings, QUICK_STEPS)
    checkpointer = MemorySaver()
    workflow = graph.compile(checkpointer=checkpointer)

    initial_state: dict[str, Any] = {
        "config": config,
        "job_id": job_id,
        "errors": [],
    }
    thread_config = {"configurable": {"thread_id": f"{job_id}-quick"}}

    logger.info("Starting quick scan for job %s", job_id)
    result = await workflow.ainvoke(initial_state, config=thread_config)
    logger.info("Quick scan complete for job %s", job_id)

    return result


async def run_deep_scan(
    settings: Settings,
    *,
    job_id: str,
    config: dict[str, Any],
    quick_state: dict[str, Any],
) -> dict[str, Any]:
    """Continue from quick-scan state through the remaining 6 steps.

    Takes the state dict produced by run_quick_scan and feeds it into the
    deep-scan sub-workflow (market_researcher through synthesizer).
    """
    graph = _build_partial_workflow(settings, DEEP_STEPS)
    checkpointer = MemorySaver()
    workflow = graph.compile(checkpointer=checkpointer)

    thread_config = {"configurable": {"thread_id": f"{job_id}-deep"}}

    logger.info("Starting deep scan for job %s", job_id)
    result = await workflow.ainvoke(quick_state, config=thread_config)
    logger.info("Deep scan complete for job %s", job_id)

    return result
