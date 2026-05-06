"""Command-line entrypoint for the lab starter."""

import json
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.evaluation.benchmark import run_benchmark
from multi_agent_research_lab.evaluation.report import render_markdown_report
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.observability.logging import configure_logging
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.services.storage import LocalArtifactStore

app = typer.Typer(help="Multi-Agent Research Lab starter CLI")
console = Console()


def _init() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)


def _run_baseline(query: str) -> ResearchState:
    settings = get_settings()
    request = ResearchQuery(query=query)
    state = ResearchState(request=request)
    client = LLMClient(settings=settings)
    response = client.complete(
        system_prompt=(
            "You are a strong single-agent research assistant. Answer the query clearly, "
            "mention tradeoffs, and include a short list of practical next steps."
        ),
        user_prompt=f"Query: {query}\nAudience: {request.audience}",
    )
    state.final_answer = response.content
    state.record_usage(response.input_tokens, response.output_tokens, response.cost_usd)
    state.add_result("writer", response.content, metadata={"mode": "baseline"})
    state.add_trace_event("baseline.completed", {"used_llm": response.input_tokens is not None})
    state.is_complete = True
    state.next_agent = "done"
    return state


def _run_multi_agent(query: str) -> ResearchState:
    state = ResearchState(request=ResearchQuery(query=query))
    workflow = MultiAgentWorkflow()
    return workflow.run(state)


@app.command()
def baseline(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run a single-agent baseline."""

    _init()
    state = _run_baseline(query)
    console.print(Panel.fit(state.final_answer or "", title="Single-Agent Baseline"))


@app.command("multi-agent")
def multi_agent(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run the multi-agent workflow."""

    _init()
    result = _run_multi_agent(query)
    console.print(Panel.fit(result.final_answer or "", title="Multi-Agent Answer"))
    console.print(
        Panel.fit(
            "\n".join(
                [
                    f"Route: {' -> '.join(result.route_history)}",
                    f"Sources: {len(result.sources)}",
                    f"Errors: {len(result.errors)}",
                ]
            ),
            title="Run Summary",
        )
    )


@app.command()
def benchmark(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Benchmark baseline and multi-agent runs and write a markdown report."""

    _init()
    store = LocalArtifactStore()
    baseline_state, baseline_metrics = run_benchmark("baseline", query, _run_baseline)
    multi_state, multi_metrics = run_benchmark("multi-agent", query, _run_multi_agent)
    report = render_markdown_report(
        [baseline_metrics, multi_metrics],
        states={"baseline": baseline_state, "multi-agent": multi_state},
        query=query,
    )
    report_path = store.write_text("benchmark_report.md", report)
    traces_path = store.write_text(
        "traces/latest_run.json",
        json.dumps(
            {
                "baseline": baseline_state.model_dump(),
                "multi_agent": multi_state.model_dump(),
            },
            indent=2,
        ),
    )
    console.print(
        Panel.fit(
            f"Report: {report_path}\nTrace export: {traces_path}",
            title="Benchmark Artifacts",
        )
    )


if __name__ == "__main__":
    app()
