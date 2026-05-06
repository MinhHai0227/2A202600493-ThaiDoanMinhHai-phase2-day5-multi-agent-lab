"""Analyst agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


class AnalystAgent(BaseAgent):
    """Turns research notes into structured insights."""

    name = "analyst"

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate analysis notes."""

        response = self.llm_client.complete(
            system_prompt=(
                "You are an analysis agent. Extract key findings, disagreements, limitations, "
                "and practical recommendations from research notes."
            ),
            user_prompt=(
                f"Query: {state.request.query}\n"
                f"Research notes:\n{state.research_notes or 'No research notes provided.'}"
            ),
        )
        state.analysis_notes = response.content
        state.record_usage(response.input_tokens, response.output_tokens, response.cost_usd)
        state.add_result(AgentName.ANALYST, response.content)
        state.add_trace_event("analyst.completed", {"has_research_notes": state.research_notes is not None})
        return state
