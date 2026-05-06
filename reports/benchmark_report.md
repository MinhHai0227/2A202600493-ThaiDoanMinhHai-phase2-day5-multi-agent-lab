# Benchmark Report

| Run | Latency (s) | Cost (USD) | Quality | Citation Coverage | Failure Rate | Tokens In | Tokens Out | Notes |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| baseline | 7.30 | 0.0002 | 6.0 | 0% | 0% | 50 | 385 | routes: direct; sources: 0 |
| multi-agent | 23.23 | 0.0013 | 10.0 | 80% | 0% | 2193 | 1671 | routes: researcher -> analyst -> writer -> critic -> done; sources: 5 |

## Summary

- Fastest run: `baseline` at 7.30s
- Highest quality score: `multi-agent` at 10.0/10
- Quality score is heuristic and should be paired with manual peer review.

## Query

Explain multi-agent systems

## Qualitative Review

### baseline

- Route: direct
- Source count: 0
- Errors: 0
- Main failure mode: No external retrieval, so the answer depends heavily on model priors.

### multi-agent

- Route: researcher -> analyst -> writer -> critic -> done
- Source count: 5
- Errors: 0
- Main failure mode: The answer provides a comprehensive overview of multi-agent systems (MAS) but contains several unsupported claims and lacks citations for key concepts. Here are the main points of critique: 1. **Unsupported Claims**: - T...
- Critic summary: The answer provides a comprehensive overview of multi-agent systems (MAS) but contains several unsupported claims and lacks citations for key concepts. Here are the main points of critique: 1. **Unsupported Claims**: - T...

