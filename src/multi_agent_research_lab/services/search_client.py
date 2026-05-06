"""Search client abstraction for ResearcherAgent."""

from __future__ import annotations

import json
import logging
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from multi_agent_research_lab.core.config import Settings, get_settings
from multi_agent_research_lab.core.schemas import SourceDocument

logger = logging.getLogger(__name__)


class SearchClient:
    """Small search client with Tavily support and an offline fallback."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Search for documents relevant to a query."""

        if self.settings.tavily_api_key:
            try:
                return self._tavily_search(query=query, max_results=max_results)
            except (HTTPError, URLError, TimeoutError, ValueError) as exc:
                logger.warning("Tavily search failed, using offline sources: %s", exc)
        return self._offline_search(query=query, max_results=max_results)

    def _tavily_search(self, query: str, max_results: int) -> list[SourceDocument]:
        payload = {
            "api_key": self.settings.tavily_api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": "advanced",
            "include_answer": False,
        }
        request = Request(
            url="https://api.tavily.com/search",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=self.settings.timeout_seconds) as response:
            raw = json.loads(response.read().decode("utf-8"))

        results = raw.get("results", [])
        documents = [
            SourceDocument(
                title=item.get("title", "Untitled source"),
                url=item.get("url"),
                snippet=item.get("content", "")[:500],
                metadata={"score": item.get("score")},
            )
            for item in results[:max_results]
        ]
        if documents:
            return documents
        return self._offline_search(query=query, max_results=max_results)

    def _offline_search(self, query: str, max_results: int) -> list[SourceDocument]:
        library = [
            SourceDocument(
                title="OpenAI - Orchestrating multiple agents",
                url="https://platform.openai.com/docs/guides/agents",
                snippet=(
                    "Use a planner or supervisor to break a task into smaller steps, then hand work "
                    "to specialist agents with explicit responsibilities and shared context."
                ),
                metadata={"source_type": "reference"},
            ),
            SourceDocument(
                title="Anthropic - Building effective agents",
                url="https://www.anthropic.com/engineering/building-effective-agents",
                snippet=(
                    "Effective agent systems keep tools narrow, preserve state carefully, and add "
                    "guardrails such as retries, budgets, and review stages."
                ),
                metadata={"source_type": "reference"},
            ),
            SourceDocument(
                title="LangGraph concepts",
                url="https://langchain-ai.github.io/langgraph/concepts/",
                snippet=(
                    "Graph-based orchestration helps define loops, branches, and durable workflow state "
                    "for multi-step LLM systems."
                ),
                metadata={"source_type": "reference"},
            ),
            SourceDocument(
                title="Research engineering note",
                snippet=(
                    "A good research answer should separate source collection, reasoning, writing, and "
                    "review so that each stage can be evaluated independently."
                ),
                metadata={"source_type": "internal"},
            ),
            SourceDocument(
                title=f"Query focus: {query}",
                snippet=(
                    "Prioritize recent, trustworthy sources, summarize key claims, note disagreements, "
                    "and end with actionable recommendations for the requested audience."
                ),
                metadata={"source_type": "query_guidance"},
            ),
        ]
        return library[:max_results]
