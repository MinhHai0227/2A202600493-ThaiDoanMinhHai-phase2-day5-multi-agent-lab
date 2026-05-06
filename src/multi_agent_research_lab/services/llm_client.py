"""LLM client abstraction.

Production note: agents should depend on this interface instead of importing an SDK directly.
"""

from dataclasses import dataclass
import logging
from typing import Any

from tenacity import retry, stop_after_attempt, wait_exponential

from multi_agent_research_lab.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LLMResponse:
    content: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None


class LLMClient:
    """Small OpenAI-backed client with an offline fallback."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._client: Any | None = None
        if self.settings.openai_api_key:
            try:
                from openai import OpenAI
            except ImportError:
                logger.warning("OpenAI SDK is not installed. Falling back to offline completion.")
            else:
                self._client = OpenAI(api_key=self.settings.openai_api_key)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Return a completion, preferring OpenAI when configured."""

        if self._client is None:
            return self._offline_complete(system_prompt=system_prompt, user_prompt=user_prompt)

        try:
            response = self._client.chat.completions.create(
                model=self.settings.openai_model,
                temperature=0.2,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                timeout=self.settings.timeout_seconds,
            )
        except Exception as exc:
            logger.warning("OpenAI completion failed, using offline fallback: %s", exc)
            return self._offline_complete(system_prompt=system_prompt, user_prompt=user_prompt)

        content = response.choices[0].message.content or ""
        usage = getattr(response, "usage", None)
        input_tokens = getattr(usage, "prompt_tokens", None)
        output_tokens = getattr(usage, "completion_tokens", None)
        return LLMResponse(
            content=content.strip(),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=self._estimate_cost(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            ),
        )

    def _offline_complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        prompt = user_prompt.strip()
        system = system_prompt.lower()
        if "research" in system:
            content = self._summarize_prompt(prompt, prefix="Research notes")
        elif "analysis" in system or "analyst" in system:
            content = self._summarize_prompt(prompt, prefix="Analysis")
        elif "critic" in system or "review" in system:
            content = "Review: the answer is concise, but external verification is recommended."
        else:
            content = self._summarize_prompt(prompt, prefix="Answer")
        input_tokens = max(1, len((system_prompt + "\n" + user_prompt).split()))
        output_tokens = max(1, len(content.split()))
        return LLMResponse(
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=self._estimate_cost(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            ),
        )

    def _summarize_prompt(self, prompt: str, prefix: str) -> str:
        lines = [line.strip() for line in prompt.splitlines() if line.strip()]
        excerpt = " ".join(lines[:6])[:900]
        return f"{prefix}: {excerpt}"

    def _estimate_cost(
        self,
        input_tokens: int | None,
        output_tokens: int | None,
    ) -> float | None:
        if input_tokens is None and output_tokens is None:
            return None
        input_cost = (input_tokens or 0) / 1_000_000 * self.settings.openai_input_cost_per_1m_tokens
        output_cost = (output_tokens or 0) / 1_000_000 * self.settings.openai_output_cost_per_1m_tokens
        return round(input_cost + output_cost, 6)
