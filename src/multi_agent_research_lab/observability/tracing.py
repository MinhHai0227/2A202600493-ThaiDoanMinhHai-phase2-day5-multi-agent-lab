"""Tracing hooks.

This file intentionally avoids binding to one provider. Students can plug in LangSmith,
Langfuse, OpenTelemetry, or simple JSON traces.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from time import perf_counter
from typing import Any
from uuid import uuid4

from multi_agent_research_lab.core.config import get_settings


@contextmanager
def trace_span(name: str, attributes: dict[str, Any] | None = None) -> Iterator[dict[str, Any]]:
    """Create a trace span with provider metadata and duration."""

    started = perf_counter()
    span: dict[str, Any] = {
        "name": name,
        "attributes": attributes or {},
        "duration_seconds": None,
        "span_id": str(uuid4()),
        "trace_provider": _detect_trace_provider(),
    }
    try:
        yield span
    finally:
        span["duration_seconds"] = perf_counter() - started


def _detect_trace_provider() -> str:
    settings = get_settings()
    if settings.langsmith_api_key:
        return "langsmith"
    if settings.langfuse_public_key and settings.langfuse_secret_key:
        return "langfuse"
    return "local_json"
