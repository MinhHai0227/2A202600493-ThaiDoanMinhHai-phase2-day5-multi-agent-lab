"""LangGraph workflow skeleton."""

from multi_agent_research_lab.agents import (
    AnalystAgent,
    CriticAgent,
    ResearcherAgent,
    SupervisorAgent,
    WriterAgent,
)
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.observability.tracing import trace_span


class MultiAgentWorkflow:
    """Builds and runs the multi-agent graph.

    Keep orchestration here; keep agent internals in `agents/`.
    """

    def __init__(
        self,
        supervisor: SupervisorAgent | None = None,
        researcher: ResearcherAgent | None = None,
        analyst: AnalystAgent | None = None,
        writer: WriterAgent | None = None,
        critic: CriticAgent | None = None,
    ) -> None:
        self.supervisor = supervisor or SupervisorAgent()
        self.researcher = researcher or ResearcherAgent()
        self.analyst = analyst or AnalystAgent()
        self.writer = writer or WriterAgent()
        self.critic = critic or CriticAgent()

    def build(self) -> object:
        """Create a simple workflow map."""

        return {
            "supervisor": self.supervisor,
            "researcher": self.researcher,
            "analyst": self.analyst,
            "writer": self.writer,
            "critic": self.critic,
        }

    def run(self, state: ResearchState) -> ResearchState:
        """Execute the workflow and return the final state."""

        agents = self.build()
        while not state.is_complete:
            with trace_span("supervisor", {"iteration": state.iteration + 1}) as span:
                state = self.supervisor.run(state)
            state.add_trace_event("span.supervisor", span)
            if state.next_agent == "done":
                break
            agent = agents[state.next_agent]
            with trace_span(f"agent.{state.next_agent}", {"route": state.next_agent}) as span:
                state = agent.run(state)
            state.add_trace_event(f"span.{state.next_agent}", span)

        state.is_complete = True
        if state.next_agent != "done":
            state.next_agent = "done"
        return state
