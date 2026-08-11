"""Provider-agnostic LLM client layer for the intelligence graph nodes.

Nodes 3 (Skeptic) and 4 (Merger) are single-shot: one system prompt, one user
message, text out. This module is deliberately no wider than that.
"""
import os
from typing import Mapping, Protocol


class LLMError(RuntimeError):
    """Base class for provider-layer failures."""


class LLMConfigError(LLMError):
    """Raised when provider configuration is missing, unknown, or ambiguous."""


class LLMEmptyResponseError(LLMError):
    """Raised when a provider returns no usable text (e.g. a safety filter trip)."""


class LLMClient(Protocol):
    def complete(self, *, system: str, user: str, max_tokens: int) -> str: ...


# Provider name -> environment variable holding its API key.
PROVIDER_KEY_ENV = {
    "gemini": "GEMINI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
}

# Provider name -> model used when nothing overrides it.
PROVIDER_DEFAULT_MODEL = {
    "gemini": "gemini-3.6-flash",
    "anthropic": "claude-haiku-4-5-20251001",
}


def resolve_provider(env: Mapping[str, str]) -> str:
    """Determines the provider deterministically. Ambiguity is an error, not a coin flip."""
    explicit = (env.get("LLM_PROVIDER") or "").strip().lower()
    if explicit:
        if explicit not in PROVIDER_KEY_ENV:
            valid = ", ".join(sorted(PROVIDER_KEY_ENV))
            raise LLMConfigError(
                f"Unknown LLM_PROVIDER '{explicit}'. Valid providers: {valid}."
            )
        return explicit

    present = sorted(
        provider
        for provider, key in PROVIDER_KEY_ENV.items()
        if (env.get(key) or "").strip()
    )

    if len(present) == 1:
        return present[0]

    if len(present) > 1:
        raise LLMConfigError(
            f"Multiple provider keys are set ({', '.join(present)}). "
            "Set LLM_PROVIDER to choose one explicitly."
        )

    raise LLMConfigError(
        "No LLM provider configured. Set GEMINI_API_KEY to run for free "
        "(see guides/gemini-api-key.md), or set ANTHROPIC_API_KEY "
        "(see guides/anthropic-api-key.md)."
    )


def resolve_model(provider: str, env: Mapping[str, str]) -> str:
    """LLM_MODEL wins, then the deprecated ANTHROPIC_MODEL, then the provider default."""
    override = (env.get("LLM_MODEL") or "").strip()
    if override:
        return override

    if provider == "anthropic":
        legacy = (env.get("ANTHROPIC_MODEL") or "").strip()
        if legacy:
            return legacy

    return PROVIDER_DEFAULT_MODEL[provider]


def _require_text(text: str | None, provider: str, model: str) -> str:
    """Guards against silently archiving and emailing an empty brief."""
    if not (text or "").strip():
        raise LLMEmptyResponseError(
            f"{provider} ({model}) returned no text. This is often a safety filter "
            "or a truncated response — refusing to continue with an empty brief."
        )
    return text


class GeminiClient:
    """Google Gemini adapter — the free-tier default."""

    def __init__(self, api_key: str, model: str):
        from google import genai

        self._client = genai.Client(api_key=api_key)
        self.model = model

    def complete(self, *, system: str, user: str, max_tokens: int) -> str:
        import time
        from google.genai import types

        last_error = None
        for attempt in range(4):
            try:
                response = self._client.models.generate_content(
                    model=self.model,
                    contents=user,
                    config=types.GenerateContentConfig(
                        system_instruction=system,
                        max_output_tokens=max_tokens,
                    ),
                )
                return _require_text(response.text, "gemini", self.model)
            except Exception as e:
                last_error = e
                if attempt == 3:
                    raise last_error
                time.sleep(2 ** (attempt + 1))
        raise last_error or LLMError("Failed to complete Gemini request.")


class AnthropicClient:
    """Anthropic Claude adapter."""

    def __init__(self, api_key: str, model: str):
        from anthropic import Anthropic

        self._client = Anthropic(api_key=api_key)
        self.model = model

    def complete(self, *, system: str, user: str, max_tokens: int) -> str:
        import time

        last_error = None
        for attempt in range(4):
            try:
                response = self._client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    system=system,
                    messages=[{"role": "user", "content": user}],
                )
                text = "".join(
                    block.text for block in response.content if block.type == "text"
                )
                return _require_text(text, "anthropic", self.model)
            except Exception as e:
                last_error = e
                if attempt == 3:
                    raise last_error
                time.sleep(2 ** (attempt + 1))
        raise last_error or LLMError("Failed to complete Anthropic request.")


# Provider name -> adapter class. Adding a provider means adding one class
# and one entry here; main.py does not change.
PROVIDER_CLIENTS = {
    "gemini": GeminiClient,
    "anthropic": AnthropicClient,
}


def get_llm_client(env: Mapping[str, str] | None = None) -> LLMClient:
    """Builds the configured provider's client, or raises LLMConfigError explaining why not."""
    env = os.environ if env is None else env

    provider = resolve_provider(env)
    model = resolve_model(provider, env)

    key_name = PROVIDER_KEY_ENV[provider]
    api_key = (env.get(key_name) or "").strip()
    if not api_key:
        raise LLMConfigError(
            f"LLM provider '{provider}' was selected but {key_name} is not set."
        )

    return PROVIDER_CLIENTS[provider](api_key=api_key, model=model)
