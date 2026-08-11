"""Live smoke test for the configured LLM provider — makes one real API call.

Usage: .venv/bin/python scripts/smoke_llm.py
"""
import sys
import pathlib

# Add project root to sys.path
REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from src.llm import get_llm_client

client = get_llm_client()
print(f"🤖 Provider: {type(client).__name__}  Model: {client.model}")

reply = client.complete(
    system="You are a terse assistant. Reply with exactly one short sentence.",
    user="Confirm you are reachable and name the model you are running.",
    max_tokens=100,
)

print(f"✅ Reply: {reply.strip()}")
