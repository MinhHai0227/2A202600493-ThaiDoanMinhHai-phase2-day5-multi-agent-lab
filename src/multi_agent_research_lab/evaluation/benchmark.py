"""Benchmark skeleton for single-agent vs multi-agent."""

from time import perf_counter
from typing import Callable

from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState


Runner = Callable[[str], ResearchState]


def run_benchmark(run_name: str, query: str, runner: Runner) -> tuple[ResearchState, BenchmarkMetrics]:
    """Measure latency and derive lightweight benchmark metrics."""

    started = perf_counter()
    state = runner(query)
    latency = perf_counter() - started
    metrics = BenchmarkMetrics(
        run_name=run_name,
        latency_seconds=latency,
        estimated_cost_usd=state.estimated_cost_usd or None,
        quality_score=_score_state(state),
        citation_coverage=_estimate_citation_coverage(state),
        failure_rate=1.0 if state.errors else 0.0,
        input_tokens=state.input_tokens,
        output_tokens=state.output_tokens,
        notes=_summarize_state(state),
    )
    return state, metrics


def _score_state(state: ResearchState) -> float:
    answer_words = len((state.final_answer or "").split())
    source_bonus = min(len(state.sources), 5) * 0.6
    error_penalty = len(state.errors) * 0.75
    coverage_bonus = 1.0 if state.analysis_notes else 0.0
    base = 3.0 if state.final_answer else 0.0
    score = base + min(answer_words / 80, 3.0) + source_bonus + coverage_bonus - error_penalty
    return round(max(0.0, min(score, 10.0)), 1)


def _summarize_state(state: ResearchState) -> str:
    routes = " -> ".join(state.route_history) if state.route_history else "direct"
    notes: list[str] = [f"routes: {routes}", f"sources: {len(state.sources)}"]
    if state.errors:
        notes.append(f"errors: {len(state.errors)}")
    return "; ".join(notes)


def _estimate_citation_coverage(state: ResearchState) -> float:
    answer = state.final_answer or ""
    if not answer.strip():
        return 0.0
    source_hits = sum(1 for source in state.sources if source.title and source.title in answer)
    bracket_hits = answer.count("[")
    if not state.sources:
        return 0.0
    coverage = max(source_hits, bracket_hits) / len(state.sources)
    return round(min(coverage, 1.0), 2)
