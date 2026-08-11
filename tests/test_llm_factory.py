"""Factory wiring — verifies the right adapter is built with the right model."""
import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import src.llm as llm  # noqa: E402


def test_factory_builds_a_gemini_client():
    client = llm.get_llm_client({"GEMINI_API_KEY": "AIza-fake"})
    assert isinstance(client, llm.GeminiClient)
    assert client.model == "gemini-3.6-flash"


def test_factory_builds_an_anthropic_client():
    client = llm.get_llm_client({"ANTHROPIC_API_KEY": "sk-ant-fake"})
    assert isinstance(client, llm.AnthropicClient)
    assert client.model == "claude-haiku-4-5-20251001"


def test_factory_honors_the_model_override():
    env = {"GEMINI_API_KEY": "AIza-fake", "LLM_MODEL": "gemini-3.5-flash"}
    assert llm.get_llm_client(env).model == "gemini-3.5-flash"


def test_factory_raises_when_selected_provider_has_no_key():
    with pytest.raises(llm.LLMConfigError) as exc:
        llm.get_llm_client({"LLM_PROVIDER": "gemini"})
    assert "GEMINI_API_KEY" in str(exc.value)


def test_adapters_satisfy_the_protocol():
    for client_cls in (llm.GeminiClient, llm.AnthropicClient):
        assert hasattr(client_cls, "complete")
