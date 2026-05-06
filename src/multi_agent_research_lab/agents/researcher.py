"""Researcher agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.services.search_client import SearchClient


class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = "researcher"

    def __init__(
        self,
        search_client: SearchClient | None = None,
        llm_client: LLMClient | None = None,
    ) -> None:
        self.search_client = search_client or SearchClient()
        self.llm_client = llm_client or LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate sources and research notes."""

        sources = self.search_client.search(
            query=state.request.query,
            max_results=state.request.max_sources,
        )
        state.sources = sources

        source_context = "\n".join(
            f"[{index}] {source.title}: {source.snippet}"
            for index, source in enumerate(sources, start=1)
        )
        response = self.llm_client.complete(
            system_prompt=(
                "You are a research agent. Turn raw sources into concise research notes with "
                "themes, evidence, and citation markers like [1], [2]."
            ),
            user_prompt=(
                f"Query: {state.request.query}\n"
                f"Audience: {state.request.audience}\n"
                f"Sources:\n{source_context}"
            ),
        )
        state.research_notes = response.content
        state.record_usage(response.input_tokens, response.output_tokens, response.cost_usd)
        state.add_result(
            AgentName.RESEARCHER,
            response.content,
            metadata={"source_count": len(sources)},
        )
        state.add_trace_event(
            "researcher.completed",
            {"source_count": len(sources), "used_llm": response.input_tokens is not None},
        )
        return state
