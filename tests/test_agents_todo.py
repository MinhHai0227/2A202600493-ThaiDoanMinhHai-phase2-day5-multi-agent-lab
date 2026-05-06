from multi_agent_research_lab.agents import SupervisorAgent
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow


def test_supervisor_routes_to_researcher_first() -> None:
    state = ResearchState(request=ResearchQuery(query="Explain multi-agent systems"))
    result = SupervisorAgent().run(state)
    assert result.next_agent == "researcher"
    assert result.route_history == ["researcher"]


def test_workflow_completes_and_generates_answer() -> None:
    state = ResearchState(request=ResearchQuery(query="Explain multi-agent systems"))
    result = MultiAgentWorkflow().run(state)
    assert result.is_complete is True
    assert result.final_answer
    assert "writer" in result.route_history
