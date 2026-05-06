"""Shared state for the multi-agent workflow.

Students should extend this file when adding new agents, outputs, or evaluation metrics.
"""

from typing import Any

from pydantic import BaseModel, Field

from multi_agent_research_lab.core.schemas import AgentName, AgentResult, ResearchQuery, SourceDocument


class ResearchState(BaseModel):
    """Single source of truth passed through the workflow."""

    request: ResearchQuery
    iteration: int = 0
    route_history: list[str] = Field(default_factory=list)
    next_agent: str | None = None
    is_complete: bool = False

    sources: list[SourceDocument] = Field(default_factory=list)
    research_notes: str | None = None
    analysis_notes: str | None = None
    final_answer: str | None = None
    critique_notes: str | None = None

    agent_results: list[AgentResult] = Field(default_factory=list)
    trace: list[dict[str, Any]] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost_usd: float = 0.0

    def record_route(self, route: str) -> None:
        self.route_history.append(route)
        self.next_agent = route
        self.iteration += 1
        if route == "done":
            self.is_complete = True

    def add_trace_event(self, name: str, payload: dict[str, Any]) -> None:
        self.trace.append({"name": name, "payload": payload})

    def add_result(
        self,
        agent: AgentName | str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        agent_name = agent if isinstance(agent, AgentName) else AgentName(agent)
        self.agent_results.append(
            AgentResult(agent=agent_name, content=content, metadata=metadata or {})
        )

    def add_error(self, message: str) -> None:
        self.errors.append(message)

    def record_usage(
        self,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        cost_usd: float | None = None,
    ) -> None:
        self.input_tokens += input_tokens or 0
        self.output_tokens += output_tokens or 0
        self.estimated_cost_usd += cost_usd or 0.0
