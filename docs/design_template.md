# Design Template

## Problem

Build a research assistant that can take an open-ended question, gather supporting
material, analyze the evidence, write a polished answer, and produce benchmark
artifacts that compare a single-agent baseline against a multi-agent workflow.

## Why multi-agent?

A single-agent baseline is fast, but it tends to mix retrieval, reasoning, writing,
and self-review in one step. That makes the system harder to debug and harder to
benchmark. The multi-agent version separates those responsibilities so each stage can
be traced, evaluated, and improved independently.

## Agent roles

| Agent | Responsibility | Input | Output | Failure mode |
|---|---|---|---|---|
| Supervisor | Decide which agent should run next and when to stop | Request + shared state | Next route | Routes too early to `writer` or loops too long |
| Researcher | Collect sources and produce research notes | Query + source budget | `sources`, `research_notes` | Weak retrieval, stale sources, or empty notes |
| Analyst | Turn notes into findings, limitations, and recommendations | `research_notes` | `analysis_notes` | Shallow analysis or missed disagreements |
| Writer | Produce the final response with source references | `research_notes`, `analysis_notes`, `sources` | `final_answer` | Over-generalized writing or weak citation usage |
| Critic | Review the answer for unsupported claims and missing nuance | `final_answer`, `sources` | `critique_notes` | Detects issues but cannot fully repair them |

## Shared state

- `request`: original user query and runtime options.
- `iteration`: loop counter used for guardrails.
- `route_history`: audit trail of the workflow path.
- `next_agent`: explicit routing decision from the supervisor.
- `is_complete`: stop condition for the workflow.
- `sources`: retrieved evidence used by downstream agents.
- `research_notes`: condensed retrieval summary for handoff.
- `analysis_notes`: structured reasoning output.
- `final_answer`: user-facing answer.
- `critique_notes`: reviewer feedback on answer quality.
- `agent_results`: normalized per-agent outputs.
- `trace`: span-style events for debugging and reporting.
- `errors`: collected failures for fallback and benchmark reporting.
- `input_tokens`, `output_tokens`, `estimated_cost_usd`: lightweight usage metrics.

## Routing policy

```text
start
  -> supervisor
      -> researcher   if sources or research notes are missing
      -> analyst      if analysis notes are missing
      -> writer       if final answer is missing
      -> critic       if critique notes are missing
      -> done         if all major fields are present or max iterations is reached
```

## Guardrails

- Max iterations: stop after `MAX_ITERATIONS` to avoid infinite loops.
- Timeout: each provider call uses `TIMEOUT_SECONDS`.
- Retry: LLM calls retry with exponential backoff through `tenacity`.
- Fallback: if OpenAI or Tavily is unavailable, use local offline fallbacks.
- Validation: Pydantic schemas validate requests, sources, agent results, and metrics.

## Benchmark plan

| Query | Metrics | Expected outcome |
|---|---|---|
| Explain multi-agent systems | Latency, cost, quality, citation coverage, failure rate | Multi-agent should be slower but more grounded |
| Research GraphRAG state-of-the-art | Same metrics + route trace | Multi-agent should cite more sources and expose reasoning steps |
| Summarize tradeoffs of agent orchestration | Same metrics + critique notes | Critic should surface unsupported claims or missing caveats |
