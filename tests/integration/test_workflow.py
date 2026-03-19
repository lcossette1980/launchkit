"""Integration tests for the workflow graph construction.

Verifies that the LangGraph StateGraph builds and compiles correctly.
Does NOT run actual LLM calls.
"""

from gtm.config import Settings


class TestWorkflowConstruction:
    def test_build_workflow(self):
        from gtm.agents.workflow import build_workflow

        settings = Settings(openai_api_key="test", redis_url="redis://localhost:6379")
        graph = build_workflow(settings)
        # Should have 9 nodes
        assert len(graph.nodes) == 9

    def test_compile_workflow(self):
        from gtm.agents.workflow import compile_workflow

        settings = Settings(openai_api_key="test", redis_url="redis://localhost:6379")
        compiled = compile_workflow(settings)
        # Should be a runnable
        assert hasattr(compiled, "ainvoke")
