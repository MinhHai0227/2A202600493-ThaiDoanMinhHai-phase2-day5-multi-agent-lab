"""Supervisor / router skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.config import Settings, get_settings
from multi_agent_research_lab.core.state import ResearchState


class SupervisorAgent(BaseAgent):
    """Decides which worker should run next and when to stop."""

    name = "supervisor"

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def run(self, state: ResearchState) -> ResearchState:
        """Choose the next agent based on missing state."""

        next_agent = self._choose_next_agent(state)
        state.record_route(next_agent)
        state.add_trace_event(
            "supervisor.route",
            {
                "next_agent": next_agent,
                "iteration": state.iteration,
                "errors": len(state.errors),
            },
        )
        return state

    def _choose_next_agent(self, state: ResearchState) -> str:
        if state.is_complete:
            return "done"
        if state.iteration >= self.settings.max_iterations:
            return "done" if state.final_answer else "writer"
        if not state.sources or not state.research_notes:
            return "researcher"
        if not state.analysis_notes:
            return "analyst"
        if not state.final_answer:
            return "writer"
        if not state.critique_notes:
            return "critic"
        return "done"
