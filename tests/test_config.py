"""Node prompt loading behaviour for config.py."""
import os
import pathlib
import subprocess
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import src.config as config  # noqa: E402


def test_skeptic_prompt_loads_from_disk():
    assert "adversarial" in config.SKEPTIC_SYSTEM_PROMPT.lower()


def test_synthesis_prompt_keeps_the_date_placeholder():
    assert "{{HUMAN_DATE}}" in config.SYNTHESIS_SYSTEM_PROMPT


def test_synthesis_prompt_keeps_the_cheap_word_guardrail():
    assert "cheap" in config.SYNTHESIS_SYSTEM_PROMPT.lower()


def test_product_context_loads_from_disk():
    assert "AI customer-research" in config.PRODUCT_CONTEXT


def test_load_node_raises_for_unknown_name():
    with pytest.raises(FileNotFoundError):
        config.load_node("does_not_exist")


def test_scouts_load_from_disk():
    scouts = config.load_scouts()
    assert len(scouts) == 6
    ids = [s["id"] for s in scouts]
    assert "competitor_product_changes" in ids
    assert "customer_complaints_and_unmet_needs" in ids
    assert "ai_and_agentic_product_management" in ids

    competitor_scout = next(s for s in scouts if s["id"] == "competitor_product_changes")
    assert competitor_scout["name"] == "Competitor Product Changes Scout"
    assert competitor_scout["time_range"] == "week"
    assert len(competitor_scout["queries"]) >= 1
    assert any("Linear" in q for q in competitor_scout["queries"])


def test_nodes_load_from_any_working_directory():
    """Nodes resolve against the module dir, not os.getcwd()."""
    result = subprocess.run(
        [sys.executable, "-c", "from src import config; print(len(config.SKEPTIC_SYSTEM_PROMPT)); print(len(config.SCOUT_QUERIES))"],
        cwd="/tmp",
        env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    lines = result.stdout.strip().splitlines()
    assert int(lines[0]) > 0
    assert int(lines[1]) >= 3

