"""Writer agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = "writer"

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate the final answer."""

        source_list = "\n".join(
            f"- {source.title}{f' ({source.url})' if source.url else ''}"
            for source in state.sources
        )
        response = self.llm_client.complete(
            system_prompt=(
                "You are a writing agent. Produce a clear, polished answer for the user. "
                "Use the research and analysis notes, mention limitations, and end with a "
                "short Sources section."
            ),
            user_prompt=(
                f"Query: {state.request.query}\n"
                f"Audience: {state.request.audience}\n"
                f"Research notes:\n{state.research_notes or 'N/A'}\n\n"
                f"Analysis notes:\n{state.analysis_notes or 'N/A'}\n\n"
                f"Sources:\n{source_list or 'No external sources available.'}"
            ),
        )
        state.final_answer = response.content
        state.record_usage(response.input_tokens, response.output_tokens, response.cost_usd)
        state.add_result(AgentName.WRITER, response.content)
        state.add_trace_event("writer.completed", {"answer_length": len(response.content)})
        return state
