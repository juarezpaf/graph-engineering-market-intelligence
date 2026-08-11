"""Provider and model resolution — pure logic, no SDKs, no network."""
import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import src.llm as llm  # noqa: E402


# --- Rule 1: explicit LLM_PROVIDER wins ---

def test_explicit_provider_is_used():
    env = {"LLM_PROVIDER": "gemini", "ANTHROPIC_API_KEY": "sk-ant-x"}
    assert llm.resolve_provider(env) == "gemini"


def test_explicit_provider_is_case_insensitive():
    assert llm.resolve_provider({"LLM_PROVIDER": "  Anthropic  "}) == "anthropic"


def test_unknown_explicit_provider_raises_and_names_valid_options():
    with pytest.raises(llm.LLMConfigError) as exc:
        llm.resolve_provider({"LLM_PROVIDER": "openai"})
    assert "openai" in str(exc.value)
    assert "anthropic" in str(exc.value)
    assert "gemini" in str(exc.value)


# --- Rule 2: exactly one key present ---

def test_single_gemini_key_selects_gemini():
    assert llm.resolve_provider({"GEMINI_API_KEY": "AIza-x"}) == "gemini"


def test_single_anthropic_key_selects_anthropic():
    assert llm.resolve_provider({"ANTHROPIC_API_KEY": "sk-ant-x"}) == "anthropic"


def test_blank_key_does_not_count_as_present():
    with pytest.raises(llm.LLMConfigError):
        llm.resolve_provider({"GEMINI_API_KEY": "   "})


# --- Rule 3: ambiguity is an error, never a precedence winner ---

def test_multiple_keys_without_explicit_provider_raises():
    env = {"GEMINI_API_KEY": "AIza-x", "ANTHROPIC_API_KEY": "sk-ant-x"}
    with pytest.raises(llm.LLMConfigError) as exc:
        llm.resolve_provider(env)
    assert "LLM_PROVIDER" in str(exc.value)


# --- Rule 4: nothing configured ---

def test_no_keys_raises_and_mentions_the_free_option_first():
    with pytest.raises(llm.LLMConfigError) as exc:
        llm.resolve_provider({})
    message = str(exc.value)
    assert message.index("GEMINI_API_KEY") < message.index("ANTHROPIC_API_KEY")


# --- Model resolution ---

def test_model_defaults_per_provider():
    assert llm.resolve_model("gemini", {}) == "gemini-3.6-flash"
    assert llm.resolve_model("anthropic", {}) == "claude-haiku-4-5-20251001"


def test_llm_model_overrides_the_default():
    assert llm.resolve_model("gemini", {"LLM_MODEL": "gemini-3.5-flash"}) == "gemini-3.5-flash"


def test_legacy_anthropic_model_still_honored():
    env = {"ANTHROPIC_MODEL": "claude-sonnet-5"}
    assert llm.resolve_model("anthropic", env) == "claude-sonnet-5"


def test_legacy_anthropic_model_ignored_for_other_providers():
    env = {"ANTHROPIC_MODEL": "claude-sonnet-5"}
    assert llm.resolve_model("gemini", env) == "gemini-3.6-flash"


def test_llm_model_beats_legacy_anthropic_model():
    env = {"LLM_MODEL": "claude-opus-5", "ANTHROPIC_MODEL": "claude-sonnet-5"}
    assert llm.resolve_model("anthropic", env) == "claude-opus-5"


# --- Empty response guard ---

def test_require_text_returns_text_unchanged():
    assert llm._require_text("a brief", "gemini", "gemini-3.6-flash") == "a brief"


@pytest.mark.parametrize("empty", [None, "", "   \n  "])
def test_require_text_raises_on_empty_output(empty):
    with pytest.raises(llm.LLMEmptyResponseError) as exc:
        llm._require_text(empty, "gemini", "gemini-3.6-flash")
    assert "gemini-3.6-flash" in str(exc.value)
