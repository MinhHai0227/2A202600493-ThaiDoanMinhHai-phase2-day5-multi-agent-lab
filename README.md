# Multi-Agent Research Lab

A production-style Python project for comparing a single-agent baseline against a
multi-agent research workflow powered by OpenAI.

The system supports:

- `baseline`: one LLM answers the whole query directly
- `multi-agent`: `supervisor -> researcher -> analyst -> writer -> critic`
- `benchmark`: runs both modes and exports a markdown report plus trace JSON

## Features

- OpenAI-backed LLM client with retry, timeout, and offline fallback
- Search client with Tavily support and offline fallback sources
- Shared state for handoff between agents
- Local trace events with span metadata
- Benchmark metrics for latency, estimated cost, quality, citation coverage, and failure rate
- CLI workflow for baseline, multi-agent, and benchmark runs
- Unit tests for config, state, workflow behavior, and report rendering

## Architecture

```text
User Query
   |
   v
Supervisor
   |
   +--> Researcher -> sources + research_notes
   +--> Analyst    -> analysis_notes
   +--> Writer     -> final_answer
   +--> Critic     -> critique_notes
   |
   v
Trace + Benchmark Report
```

## Project Structure

```text
.
|-- src/multi_agent_research_lab/
|   |-- agents/
|   |-- core/
|   |-- evaluation/
|   |-- graph/
|   |-- observability/
|   |-- services/
|   `-- cli.py
|-- configs/
|-- docs/
|-- reports/
|-- tests/
|-- .env.example
`-- pyproject.toml
```

## Requirements

- Python `>=3.11`
- Windows PowerShell, Command Prompt, or any shell that can activate the virtual environment
- `OPENAI_API_KEY` in `.env` if you want real model calls
- Optional: `TAVILY_API_KEY` for real search results

## Setup

### Windows PowerShell

```powershell
python -m venv venv
venv\Scripts\activate
venv\Scripts\python -m pip install -e .[dev]
Copy-Item .env.example .env
```

### Linux / macOS

```bash
python -m venv venv
source venv/bin/activate
python -m pip install -e ".[dev]"
cp .env.example .env
```

## Environment Variables

Edit `.env` and fill in the values you need:

```env
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
OPENAI_INPUT_COST_PER_1M_TOKENS=0.15
OPENAI_OUTPUT_COST_PER_1M_TOKENS=0.60

LANGSMITH_API_KEY=
LANGSMITH_PROJECT=multi-agent-research-lab
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_HOST=https://cloud.langfuse.com

TAVILY_API_KEY=

APP_ENV=local
LOG_LEVEL=INFO
MAX_ITERATIONS=6
TIMEOUT_SECONDS=60
```

Notes:

- If `OPENAI_API_KEY` is missing or provider calls fail, the project falls back to a local offline summarizer.
- If `TAVILY_API_KEY` is missing, the project falls back to built-in reference sources.

## Run the Project

### Show CLI help

```powershell
venv\Scripts\python -m multi_agent_research_lab.cli --help
```

### Run the single-agent baseline

```powershell
venv\Scripts\python -m multi_agent_research_lab.cli baseline --query "Explain multi-agent systems"
```

### Run the multi-agent workflow

```powershell
venv\Scripts\python -m multi_agent_research_lab.cli multi-agent --query "Explain multi-agent systems"
```

### Run the benchmark

```powershell
venv\Scripts\python -m multi_agent_research_lab.cli benchmark --query "Explain multi-agent systems"
```

## Outputs

The benchmark command writes:

- `reports/benchmark_report.md`
- `reports/traces/latest_run.json`

The report includes:

- latency
- estimated cost
- heuristic quality score
- citation coverage
- failure rate
- token usage
- qualitative review of each run

## Testing

Run the test suite with:

```powershell
venv\Scripts\python -m pytest
```

## Current Workflow Logic

- `SupervisorAgent` decides which agent runs next based on missing fields in shared state.
- `ResearcherAgent` retrieves sources and writes research notes.
- `AnalystAgent` extracts findings, limitations, and recommendations.
- `WriterAgent` produces the final answer.
- `CriticAgent` reviews the answer for unsupported claims and missing nuance.

## Guardrails

- maximum iteration limit through `MAX_ITERATIONS`
- per-request timeout through `TIMEOUT_SECONDS`
- retry with exponential backoff in the LLM client
- fallback behavior for LLM and search providers
- schema validation with Pydantic

## Documentation

Supporting documents are available in:

- [docs/design_template.md](docs/design_template.md)
- [docs/lab_guide.md](docs/lab_guide.md)
- [docs/peer_review_rubric.md](docs/peer_review_rubric.md)

## Example Result

Recent benchmark output in this repo showed:

- baseline faster than multi-agent
- multi-agent produced higher quality and better citation coverage
- both runs completed with `0` recorded errors

See [reports/benchmark_report.md](reports/benchmark_report.md) for the latest exported result.

## References

- OpenAI Agents and orchestration: https://platform.openai.com/docs/guides/agents
- Anthropic, Building effective agents: https://www.anthropic.com/engineering/building-effective-agents
- LangGraph concepts: https://langchain-ai.github.io/langgraph/concepts/
- LangSmith: https://docs.smith.langchain.com/
- Langfuse: https://langfuse.com/docs
