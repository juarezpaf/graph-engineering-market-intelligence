import os
import glob
import sys
import json
import argparse
import asyncio
import httpx
import markdown
import resend
from tavily import TavilyClient
from src.llm import get_llm_client
from src import config

# Environment Variables
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")
RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
RESEND_RECIPIENT_EMAIL = os.environ.get("RESEND_RECIPIENT_EMAIL")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "Founder Intelligence <onboarding@resend.dev>")


def read_last_brief() -> str:
    """Reads the most recent brief from intel_archive for state continuity."""
    files = sorted(glob.glob("intel_archive/*.md"), reverse=True)
    if files:
        with open(files[0], "r", encoding="utf-8") as f:
            return f.read()
    return "No previous brief found."

async def execute_scout(tavily: TavilyClient, scout_info: dict) -> dict:
    """Executes search terms for a scout using Tavily best practices."""
    scout_id = scout_info["id"]
    name = scout_info["name"]
    queries = scout_info.get("queries", [scout_info.get("query", name)])
    time_range = scout_info.get("time_range", "week")
    topic = scout_info.get("topic", "general")

    combined_results = []
    seen_urls = set()

    for q in queries:
        print(f"  🔍 Fetching scout [{name}] query: '{q}' (time_range={time_range})")
        try:
            search_res = await asyncio.to_thread(
                tavily.search,
                query=q,
                search_depth="advanced",
                time_range=time_range,
                topic=topic,
                max_results=5,
            )
            for item in search_res.get("results", []):
                url = item.get("url")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    combined_results.append(item)
        except Exception as e:
            print(f"  ⚠️ Error fetching query '{q}' for [{name}]: {e}")

    return {"id": scout_id, "name": name, "results": {"results": combined_results}}

def send_resend_digest(subject: str, md_content: str):
    """Converts markdown to responsive HTML and dispatches via Resend API."""
    if not (RESEND_API_KEY and RESEND_RECIPIENT_EMAIL):
        print("⚠️ RESEND_API_KEY or RESEND_RECIPIENT_EMAIL not set. Skipping email dispatch.")
        return

    resend.api_key = RESEND_API_KEY
    html_body = markdown.markdown(md_content, extensions=['extra'])

    styled_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #1e293b;
            background-color: #f8fafc;
            padding: 16px;
            margin: 0;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: #ffffff;
            padding: 24px;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        h1 {{ font-size: 20px; color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; }}
        h2 {{ font-size: 16px; color: #2563eb; margin-top: 20px; }}
        strong {{ color: #0f172a; }}
        ul {{ padding-left: 20px; }}
        li {{ margin-bottom: 8px; }}
    </style>
</head>
<body>
    <div class="container">
        {html_body}
    </div>
</body>
</html>"""

    params: resend.Emails.SendParams = {
        "from": SENDER_EMAIL,
        "to": [RESEND_RECIPIENT_EMAIL],
        "subject": subject,
        "html": styled_html,
        "text": md_content,
    }

    try:
        print(f"📧 Dispatching email brief via Resend API to {RESEND_RECIPIENT_EMAIL}...")
        email = resend.Emails.send(params)
        print(f"✅ Email brief successfully delivered! Resend ID: {email.get('id')}")
    except Exception as e:
        print(f"❌ Resend API delivery failed: {e}")


import re

def markdown_to_slack_mrkdwn(text: str) -> str:
    """Converts standard Markdown into Slack's mrkdwn format."""
    # 1. Convert Markdown links [label](url) -> <url|label>
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<\2|\1>', text)

    # 2. Convert headers (# Header -> *Header*)
    text = re.sub(r'^#+\s+(.*)$', r'__BOLD__\1__BOLD__', text, flags=re.MULTILINE)

    # 3. Convert horizontal rules (--- -> divider line)
    text = re.sub(r'^\s*---\s*$', r'───────────────', text, flags=re.MULTILINE)

    # 4. Convert bold (**text** -> __BOLD__text__BOLD__)
    text = re.sub(r'\*\*(.*?)\*\*', r'__BOLD__\1__BOLD__', text, flags=re.DOTALL)

    # 5. Convert italics (*text* -> _text_)
    text = re.sub(r'(?<!\*)\*([^\*\n]+)\*(?!\*)', r'_\1_', text)

    # 6. Restore bold placeholder (__BOLD__ -> *)
    text = text.replace('__BOLD__', '*')

    # 7. Convert bullet points (- item or * item -> • item)
    text = re.sub(r'^(\s*)[-*]\s+', r'\1• ', text, flags=re.MULTILINE)

    return text

async def send_slack_digest(final_brief_md: str, human_date: str):
    """Sends the formatted brief to Slack Webhook."""
    if not SLACK_WEBHOOK_URL:
        print("⚠️ SLACK_WEBHOOK_URL not set. Skipping Slack delivery.")
        return

    print("📲 Delivering brief to Slack...")
    formatted_slack_text = markdown_to_slack_mrkdwn(final_brief_md)
    slack_payload = {
        "text": formatted_slack_text
    }
    async with httpx.AsyncClient() as client:
        res = await client.post(SLACK_WEBHOOK_URL, json=slack_payload)
        if res.status_code == 200:
            print("✅ Slack delivery successful.")
        else:
            print(f"❌ Slack delivery failed: {res.status_code} - {res.text}")

async def run_pipeline(dry_run: bool = False, no_delivery: bool = False):
    iso_date = config.get_iso_date()
    human_date = config.get_human_date()
    print(f"🚀 Starting Founder Intelligence Pipeline for {human_date} ({iso_date})...")

    if dry_run:
        print("🧪 RUNNING IN MOCK / DRY-RUN MODE (No live API calls will be made)")
        last_brief_context = read_last_brief()
        print("📡 Simulating parallel web scouts...")
        await asyncio.sleep(0.5)
        
        scout_results = [
            {
                "id": "competitor_product_changes",
                "name": "Competitor Product Changes Scout",
                "results": {"results": [{"title": "Linear AI Triage Integration", "url": "https://linear.app/changelog"}]}
            },
            {
                "id": "customer_complaints_and_unmet_needs",
                "name": "Customer Complaints and Unmet Needs Scout",
                "results": {"results": [{"title": "Feedback Fragmentation Tax", "url": "https://www.reforge.com/blog/feedback-fragmentation"}]}
            }
        ]

        verified_research = f"""
## Confirmed findings

### Linear AI Triage Integration
- **Claim:** Linear announced AI triage automation for customer feedback.
- **Company:** Linear
- **Source:** [Linear Changelog](https://linear.app/changelog)
- **Confidence:** High
- **Why it may matter:** Increases customer expectation for native workflow integration.
"""
        print("🧐 Simulating Skeptic quality pass...")
        await asyncio.sleep(0.5)
        
        print("📝 Simulating Chief of Staff Brief Synthesis...")
        await asyncio.sleep(0.5)
        
        final_brief_md = f"""# Founder Intelligence Brief — {human_date}

## Signal of the week

Major product management tools are expanding AI capabilities from basic text summarization into automated issue clustering and feedback routing.

## Confirmed developments

### Linear AI Triage Integration
Linear announced enhanced AI triage features for customer feedback linking directly to issue backlogs.  
**Why it matters:** Increases customer expectation for native workflow integration.

### Jira Product Discovery API Expansion
Jira Product Discovery expanded API support for custom insight sources.  
**Why it matters:** Makes it easier to build bi-directional integrations as an ecosystem partner.

## Ties to product & market decisions

- Sharpens our positioning around zero-friction setup: sitting alongside Linear and Jira Product Discovery rather than replacing them.
- Validates prioritizing automated interview transcript tagging over generic survey builders.

## Possible product or engineering quick win

Build a light, single-click Linear webhook integration to test auto-linking customer feedback snippets to existing Linear issues.

## Treat with skepticism

Press releases from legacy enterprise suites claiming "fully autonomous product management" without showing concrete human-in-the-loop controls.

## Watch list

Emerging open-source feedback collection widgets on GitHub.

## Top 5 resource links

1. [Linear Changelog: Customer Feedback Triage](https://linear.app/changelog) - Official release notes on feedback triage.
2. [Jira Product Discovery REST API Reference](https://developer.atlassian.com/cloud/jira/platform) - New endpoints for custom insight sources.
3. [Productboard Feedback Portal](https://www.productboard.com) - Reference architecture for customer feedback syncing.
4. [Plane Open Source Release Notes](https://github.com/makeplane/plane) - Modern open-source project management updates.
5. [GitHub Projects Automation API Updates](https://github.blog) - Developer workflow and issue tracking announcements.
"""
    else:
        if not TAVILY_API_KEY:
            print("❌ TAVILY_API_KEY is missing. Pipeline requires TAVILY_API_KEY (or use --dry-run).")
            return

        llm = get_llm_client()
        tavily = TavilyClient(api_key=TAVILY_API_KEY)
        print(f"🤖 LLM provider: {type(llm).__name__} (model: {llm.model})")

        # Node 1: Context & Continuity Pass
        last_brief_context = read_last_brief()

        # Node 2: Execute Parallel Scouts
        print("📡 Executing parallel web scouts...")
        scout_tasks = [execute_scout(tavily, scout) for scout in config.SCOUT_QUERIES]
        scout_results = await asyncio.gather(*scout_tasks)

        raw_research_blocks = []
        for res in scout_results:
            raw_research_blocks.append(f"=== {res['name'].upper()} ===\n{res['results']}")
        raw_research_block = "\n\n".join(raw_research_blocks)

        # Node 3: The Skeptic (Adversarial Quality Pass)
        print("🧐 Running Skeptic quality pass...")
        verified_research = llm.complete(
            system=config.SKEPTIC_SYSTEM_PROMPT,
            user=(
                f"Audit this raw daily research against previous state.\n\n"
                f"LAST BRIEF STATE:\n{last_brief_context[:1000]}\n\n"
                f"NEW RAW RESEARCH:\n{raw_research_block}"
            ),
            max_tokens=8192,
        )

        # Node 4: The Merger (Synthesis Pass)
        print("📝 Synthesizing Founder Intelligence Brief...")
        formatted_system_prompt = config.SYNTHESIS_SYSTEM_PROMPT.replace(
            "{{HUMAN_DATE}}", human_date
        )

        final_brief_md = llm.complete(
            system=formatted_system_prompt,
            user=(
                f"Product Context:\n{config.PRODUCT_CONTEXT}\n\n"
                f"Verified Market Evidence:\n{verified_research}"
            ),
            max_tokens=8192,
        )

    if not final_brief_md.strip():
        raise RuntimeError(
            "Synthesis produced an empty brief — refusing to archive or deliver."
        )


    # Node 5A: Save to Archive
    os.makedirs("intel_archive", exist_ok=True)
    archive_path = f"intel_archive/{iso_date}-founder-brief.md"
    with open(archive_path, "w", encoding="utf-8") as f:
        f.write(final_brief_md)

    scouts_raw_path = f"intel_archive/{iso_date}-scouts-raw.json"
    with open(scouts_raw_path, "w", encoding="utf-8") as f:
        json.dump(scout_results, f, indent=2)

    skeptic_path = f"intel_archive/{iso_date}-skeptic-audit.md"
    with open(skeptic_path, "w", encoding="utf-8") as f:
        f.write(verified_research)

    print(f"💾 Saved brief to {archive_path}")
    print(f"💾 Saved raw scout results to {scouts_raw_path}")
    print(f"💾 Saved skeptic audit to {skeptic_path}")

    if no_delivery:
        print("🚫 --no-delivery specified. Skipping Slack and Email notifications.")
    else:
        # Node 5B: Deliver to Slack Webhook
        await send_slack_digest(final_brief_md, human_date)

        # Node 5C: Deliver via Resend API
        email_subject = f"⚡ Founder Intelligence Brief — {human_date}"
        send_resend_digest(subject=email_subject, md_content=final_brief_md)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Founder Market Intelligence Pipeline")
    parser.add_argument("--dry-run", "--mock", action="store_true", help="Run in mock mode without calling external APIs")
    parser.add_argument("--no-delivery", action="store_true", help="Run live API calls (Tavily + LLM) and save archive, but skip sending Slack and Email notifications")
    args = parser.parse_args()
    
    asyncio.run(run_pipeline(dry_run=args.dry_run, no_delivery=args.no_delivery))

