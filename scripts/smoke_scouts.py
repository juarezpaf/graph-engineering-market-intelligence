"""Live smoke test for all research Scouts — makes real Tavily API calls for each scout.

Usage: .venv/bin/python scripts/smoke_scouts.py
"""
import os
import sys
import pathlib
import asyncio

# Add project root to sys.path
REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from tavily import TavilyClient
from src import config

TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")

async def test_single_scout(tavily: TavilyClient, scout: dict):
    print(f"🔍 [Scout: {scout['name']}] (ID: {scout['id']})")
    queries = scout.get("queries", [scout.get("query")])
    time_range = scout.get("time_range", "week")
    topic = scout.get("topic", "general")
    print(f"   Queries ({len(queries)}): {queries[:2]} | time_range: {time_range} | topic: {topic}")
    
    seen_urls = set()
    combined_items = []
    for q in queries:
        try:
            results = await asyncio.to_thread(
                tavily.search,
                query=q,
                search_depth="advanced",
                time_range=time_range,
                topic=topic,
                max_results=5,
            )
            items = results.get("results", [])
            for item in items:
                url = item.get("url")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    combined_items.append(item)
        except Exception as e:
            print(f"   ❌ Error on query '{q}': {e}")
            
    print(f"   ✅ Returned {len(combined_items)} deduplicated search results across queries:")
    for idx, item in enumerate(combined_items[:3], 1):
        print(f"      {idx}. {item.get('title')} ({item.get('url')})")
    print()

async def main():
    if not TAVILY_API_KEY:
        print("❌ TAVILY_API_KEY environment variable is not set in .env.")
        return
    
    scouts = config.load_scouts()
    print(f"📡 Loaded {len(scouts)} Scouts from scouts/*.md\n")
    tavily = TavilyClient(api_key=TAVILY_API_KEY)
    
    tasks = [test_single_scout(tavily, s) for s in scouts]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
