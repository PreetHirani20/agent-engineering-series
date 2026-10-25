"""A thin wrapper around any OpenAI-compatible chat API.

Gemini, Groq, OpenRouter, OpenAI and a local Ollama server all speak the same
`/chat/completions` protocol, so one client covers all of them. Which one you
use is decided by three settings in `.env`: LLM_BASE_URL, LLM_API_KEY, LLM_MODEL.
"""

from __future__ import annotations

import os
import random
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

from openai import APIConnectionError, APIStatusError, OpenAI, RateLimitError

PROVIDER_URLS = {
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/",
    "groq": "https://api.groq.com/openai/v1",
    "openrouter": "https://openrouter.ai/api/v1",
    "openai": "https://api.openai.com/v1",
    "ollama": "http://localhost:11434/v1",
}


def load_env(path: Path) -> None:
    """Read KEY=VALUE lines from a .env file into os.environ (no extra package needed)."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


@dataclass
class Usage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    calls: int = 0


@dataclass
class LLM:
    model: str
    base_url: str
    api_key: str
    temperature: float = 0.0
    max_tokens: int = 8192
    min_interval: float = 0.0  # seconds between calls, for free-tier rate limits
    _client: OpenAI = field(init=False, repr=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)
    _last_call: float = field(default=0.0, init=False, repr=False)

    def __post_init__(self) -> None:
        self._client = OpenAI(base_url=self.base_url, api_key=self.api_key or "none", timeout=180)

    @classmethod
    def from_env(cls) -> "LLM":
        provider = os.environ.get("LLM_PROVIDER", "").lower()
        base_url = os.environ.get("LLM_BASE_URL") or PROVIDER_URLS.get(provider, "")
        model = os.environ.get("LLM_MODEL", "")
        if not base_url or not model:
            raise SystemExit(
                "Set LLM_PROVIDER (or LLM_BASE_URL) and LLM_MODEL in .env. See .env.example."
            )
        return cls(
            model=model,
            base_url=base_url,
            api_key=os.environ.get("LLM_API_KEY", ""),
            temperature=float(os.environ.get("LLM_TEMPERATURE", "0")),
            max_tokens=int(os.environ.get("LLM_MAX_TOKENS", "8192")),
            min_interval=float(os.environ.get("LLM_MIN_SECONDS_BETWEEN_CALLS", "0")),
        )

    def list_models(self) -> list[str]:
        return sorted(m.id for m in self._client.models.list())

    def _wait_for_slot(self) -> None:
        if self.min_interval <= 0:
            return
        with self._lock:
            wait = self._last_call + self.min_interval - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            self._last_call = time.monotonic()

    def chat(self, messages: list[dict], tools: list[dict], usage: Usage) -> dict:
        """One model call. Returns the assistant message as a plain dict."""
        attempts = int(os.environ.get("LLM_MAX_RETRIES", "8"))
        for attempt in range(attempts):
            self._wait_for_slot()
            try:
                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools or None,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                break
            except (RateLimitError, APIConnectionError) as exc:
                delay = min(90, 2 ** attempt * 3) + random.random()
                print(f"    [llm] {type(exc).__name__}, retrying in {delay:.0f}s")
                time.sleep(delay)
            except APIStatusError as exc:
                if exc.status_code < 500:
                    raise
                delay = min(90, 2 ** attempt * 3) + random.random()
                print(f"    [llm] server error {exc.status_code}, retrying in {delay:.0f}s")
                time.sleep(delay)
        else:
            raise RuntimeError(f"LLM call failed after {attempts} attempts")

        usage.calls += 1
        if response.usage:
            usage.prompt_tokens += response.usage.prompt_tokens or 0
            usage.completion_tokens += response.usage.completion_tokens or 0

        msg = response.choices[0].message
        out: dict = {"role": "assistant", "content": msg.content or ""}
        if msg.tool_calls:
            # Keep every field the provider sent (Gemini puts a "thought signature" in
            # extra_content that must be echoed back on the next turn).
            out["tool_calls"] = []
            for i, tc in enumerate(msg.tool_calls):
                call = tc.model_dump(exclude_none=True)
                call["id"] = tc.id or f"call_{i}"
                call["type"] = "function"
                call["function"]["arguments"] = tc.function.arguments or "{}"
                out["tool_calls"].append(call)
        out["_finish_reason"] = response.choices[0].finish_reason
        return out
