"""Optional critic agent skeleton for bonus work."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient


class CriticAgent(BaseAgent):
    """Optional fact-checking and safety-review agent."""

    name = "critic"

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Review the answer for coverage and obvious gaps."""

        response = self.llm_client.complete(
            system_prompt=(
                "You are a critic agent. Review the answer for unsupported claims, missing "
                "citations, and overlooked limitations. Be concise."
            ),
            user_prompt=(
                f"Query: {state.request.query}\n"
                f"Final answer:\n{state.final_answer or 'No answer.'}\n\n"
                f"Sources available: {len(state.sources)}"
            ),
        )
        state.critique_notes = response.content
        state.record_usage(response.input_tokens, response.output_tokens, response.cost_usd)
        state.add_result(AgentName.CRITIC, response.content)
        state.add_trace_event("critic.completed", {"has_final_answer": state.final_answer is not None})
        return state
