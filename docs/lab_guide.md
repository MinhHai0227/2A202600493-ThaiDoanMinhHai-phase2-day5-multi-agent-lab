# Lab Guide: Multi-Agent Research System

## Scenario

The project implements a research assistant that can answer long-form questions by
splitting work across multiple agents:

1. `baseline`: one model answers the whole query directly.
2. `multi-agent`: a supervisor coordinates researcher, analyst, writer, and critic.

## Current implementation

### Baseline

- `src/multi_agent_research_lab/cli.py`
- `src/multi_agent_research_lab/services/llm_client.py`

The baseline performs a real LLM call when `OPENAI_API_KEY` is available and falls
back to an offline summarizer if the provider is unavailable.

### Supervisor

- `src/multi_agent_research_lab/agents/supervisor.py`
- `src/multi_agent_research_lab/graph/workflow.py`

Routing policy:

- call `researcher` when sources or research notes are missing
- call `analyst` when analysis notes are missing
- call `writer` when the final answer is missing
- call `critic` when review notes are missing
- stop when all required outputs exist or max iterations is reached

### Worker agents

- `agents/researcher.py`: retrieves sources and builds research notes
- `agents/analyst.py`: extracts findings, limits, and recommendations
- `agents/writer.py`: writes the final answer
- `agents/critic.py`: records likely quality risks and unsupported claims

### Trace and benchmark

- `observability/tracing.py`
- `evaluation/benchmark.py`
- `evaluation/report.py`

The project records local JSON-friendly trace spans and exports benchmark artifacts.
If LangSmith or Langfuse keys are configured, the trace metadata marks the intended
provider even when local JSON export is used as the storage fallback.

## Minimum benchmark metrics

| Metric | How it is measured now |
|---|---|
| Latency | Wall-clock runtime |
| Cost | Estimated from token counts and configurable per-million token prices |
| Quality | Heuristic 0-10 score plus manual peer review recommendation |
| Citation coverage | Estimated from source mentions and citation markers |
| Failure rate | `1.0` when errors are recorded, otherwise `0.0` |

## Commands

```bash
venv\Scripts\python -m multi_agent_research_lab.cli baseline --query "Explain multi-agent systems"
venv\Scripts\python -m multi_agent_research_lab.cli multi-agent --query "Explain multi-agent systems"
venv\Scripts\python -m multi_agent_research_lab.cli benchmark --query "Explain multi-agent systems"
```

## Exit ticket

1. Use multi-agent systems when the task benefits from decomposition, source-aware
   reasoning, or auditability across multiple steps.
2. Avoid multi-agent systems for short factual prompts where a single fast model is
   cheaper, simpler, and easier to maintain.
