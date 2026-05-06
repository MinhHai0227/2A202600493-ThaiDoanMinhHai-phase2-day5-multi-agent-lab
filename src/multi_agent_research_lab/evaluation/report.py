"""Benchmark report rendering."""

from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState


def render_markdown_report(
    metrics: list[BenchmarkMetrics],
    states: dict[str, ResearchState] | None = None,
    query: str | None = None,
) -> str:
    """Render benchmark metrics to markdown."""

    lines = [
        "# Benchmark Report",
        "",
        "| Run | Latency (s) | Cost (USD) | Quality | Citation Coverage | Failure Rate | Tokens In | Tokens Out | Notes |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for item in metrics:
        cost = "" if item.estimated_cost_usd is None else f"{item.estimated_cost_usd:.4f}"
        quality = "" if item.quality_score is None else f"{item.quality_score:.1f}"
        citation_coverage = "" if item.citation_coverage is None else f"{item.citation_coverage:.0%}"
        failure_rate = f"{item.failure_rate:.0%}"
        input_tokens = "" if item.input_tokens is None else str(item.input_tokens)
        output_tokens = "" if item.output_tokens is None else str(item.output_tokens)
        lines.append(
            f"| {item.run_name} | {item.latency_seconds:.2f} | {cost} | {quality} | "
            f"{citation_coverage} | {failure_rate} | {input_tokens} | {output_tokens} | {item.notes} |"
        )
    if len(metrics) >= 2:
        fastest = min(metrics, key=lambda item: item.latency_seconds)
        strongest = max(metrics, key=lambda item: item.quality_score or 0.0)
        lines.extend(
            [
                "",
                "## Summary",
                "",
                f"- Fastest run: `{fastest.run_name}` at {fastest.latency_seconds:.2f}s",
                f"- Highest quality score: `{strongest.run_name}` at {strongest.quality_score or 0.0:.1f}/10",
                "- Quality score is heuristic and should be paired with manual peer review.",
            ]
        )
    if query:
        lines.extend(["", "## Query", "", query])
    if states:
        lines.extend(["", "## Qualitative Review", ""])
        for run_name, state in states.items():
            lines.append(f"### {run_name}")
            lines.append("")
            lines.append(f"- Route: {' -> '.join(state.route_history) if state.route_history else 'direct'}")
            lines.append(f"- Source count: {len(state.sources)}")
            lines.append(f"- Errors: {len(state.errors)}")
            lines.append(f"- Main failure mode: {_describe_failure_mode(state)}")
            if state.critique_notes:
                lines.append(f"- Critic summary: {_one_line(state.critique_notes)}")
            lines.append("")
    return "\n".join(lines) + "\n"


def _describe_failure_mode(state: ResearchState) -> str:
    if state.errors:
        return f"Execution errors recorded: {', '.join(state.errors)}"
    if not state.sources:
        return "No external retrieval, so the answer depends heavily on model priors."
    if state.critique_notes:
        return _one_line(state.critique_notes)
    return "No major runtime failure detected; remaining risk is answer quality drift."


def _one_line(text: str) -> str:
    compact = " ".join(text.split())
    return compact[:220] + ("..." if len(compact) > 220 else "")
