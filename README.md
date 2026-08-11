# Graph Engineering Market Intelligence

[![Weekly Market Intelligence](https://github.com/juarezpaf/graph-engineering-market-intelligence/actions/workflows/weekly-intelligence.yml/badge.svg)](https://github.com/juarezpaf/graph-engineering-market-intelligence/actions/workflows/weekly-intelligence.yml)
![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)
![Runtime Cost](https://img.shields.io/badge/runtime_cost-%240.00%2Fmo_(free_tier)-brightgreen)
![Architecture](https://img.shields.io/badge/architecture-Graph--Engineered%20Pipeline-orange)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A free Graph Engineering starter kit for AI-native founders.

This repository turns recurring market research into a structured workflow that runs parallel research Scouts, filters weak evidence through an adversarial skeptic pass, and produces a concise Founder Intelligence Brief.

The included example follows a fictional solo founder evaluating whether to build a new AI customer-research product for product teams. It monitors Linear and adjacent product-management platforms using real public market signals.

## What this solves

Before this workflow, the founder had to manually:

- Check competitor changelogs and product announcements.
- Search for customer complaints and unmet needs.
- Track funding, hiring, acquisitions, and company movements.
- Monitor AI, agentic-workflow, regulatory, and technology developments.
- Decide which signals were meaningful and which were mostly PR.
- Copy findings into a weekly research document.

The Graph Engineering workflow separates those jobs into connected stages. Research runs in parallel, evidence is challenged before synthesis, and the final brief is saved as a reusable Markdown archive.

## What it produces

Every Friday morning, the workflow creates a Founder Intelligence Brief containing:

- The most decision-relevant signal of the week.
- Confirmed developments supported by credible evidence.
- Connections to the fictional founder's product and market decision.
- A possible product or engineering quick win, when justified.
- Claims that should be treated with skepticism.
- Lower-priority items for the watch list.
- A recommended next validation step.

A complete example is available in [`intel_archive/`](intel_archive/).

## Graph architecture

```text
                         ┌─────────────────────┐
                         │  Founder context    │
                         │  + research goal    │
                         └──────────┬──────────┘
                                    │
                                    ▼
        ┌──────────────────────────────────────────────────┐
        │              Parallel research Scouts             │
        ├──────────────────┬──────────────────┬────────────┤
        │ Competitor       │ Customer pain    │ Funding &   │
        │ product changes  │ and unmet needs  │ company     │
        │                  │                  │ movements  │
        ├──────────────────┼──────────────────┼────────────┤
        │ AI and agentic  │ Regulatory and   │ GitHub      │
        │ product work    │ technology      │ Projects &  │
        │                  │ shifts          │ workflows   │
        └──────────────────┴──────────────────┴────────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  Adversarial        │
                         │  skeptic pass       │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  Founder brief      │
                         │  synthesis          │
                         └──────────┬──────────┘
                                    │
                 ┌──────────────────┼──────────────────┐
                 ▼                  ▼                  ▼
          ┌────────────┐     ┌────────────┐     ┌─────────────┐
          │ Slack      │     │ Email      │     │ Git archive │
          │ delivery   │     │ via Resend │     │ Markdown    │
          └────────────┘     └────────────┘     └─────────────┘
```

The Scouts are independent research paths. Every Markdown file placed inside `scouts/` is treated as a Scout and included in the parallel research stage. You can add, remove, or rewrite Scouts without changing the core workflow.

## Included example

The example market is product-management software.

The research context monitors:

- Linear.
- Jira Product Discovery.
- Asana.
- ClickUp.
- Shortcut.
- Plane.
- Height.
- Productboard.
- Notion Projects.
- GitHub Projects.

The products and market signals are real. The founder and business decision are fictional. The example asks:

> Should a solo founder build an AI customer-research product for teams already using modern product-management tools?

This makes the repository useful as a demonstration without exposing private product strategy or implying that the findings represent a particular company.

## Repository structure

```text
.
├── .github/
│   └── workflows/
│       └── weekly-intelligence.yml
├── src/
│   ├── __init__.py
│   ├── config.py
│   └── llm.py
├── scripts/
│   ├── smoke_llm.py
│   ├── smoke_scouts.py
│   └── test_resend.py
├── nodes/
│   ├── context.md
│   ├── skeptic.md
│   └── synthesis.md
├── scouts/
│   ├── competitor_product_changes.md
│   ├── customer_complaints_and_unmet_needs.md
│   ├── funding_hiring_and_company_moves.md
│   ├── ai_and_agentic_product_management.md
│   ├── regulatory_and_technology_shifts.md
│   └── github_projects_and_developer_workflows.md
├── tests/
│   ├── test_config.py
│   ├── test_llm_factory.py
│   └── test_llm_selection.py
├── intel_archive/
│   ├── 2026-08-11-founder-brief.md
│   ├── 2026-08-11-scouts-raw.json
│   └── 2026-08-11-skeptic-audit.md
├── guides/
│   ├── anthropic-api-key.md
│   ├── gemini-api-key.md
│   ├── resend-api-key.md
│   ├── slack-webhook-url.md
│   └── tavily-api-key.md
├── main.py
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── LICENSE
└── README.md
```

The exact Python module names may vary, but the important customization surface is intentionally simple: edit the Markdown context, node, and Scout files.

## Requirements

- A public or private GitHub repository with GitHub Actions enabled.
- A free Gemini API key, or an optional Claude API key.
- A free Tavily account and API key for web search.
- A free Resend account and API key for email delivery.
- A Slack channel with an incoming webhook.
- Python 3.11 or newer for local execution.

The default setup is designed to run without paid services. Claude is an optional alternative for users who prefer Anthropic models and have access to a paid Claude API account.

## Quick start

### 1. Create a new fork

Fork this repository into your own GitHub account:

1. Open the repository on GitHub.
2. Select **Fork**.
3. Choose your GitHub account as the owner.
4. Create the fork with the default repository name, or rename it if you prefer.

Your fork becomes your own working copy. GitHub Actions, the `intel_archive/` history, Scout files, and workflow configuration will all belong to your repository.

### 2. Clone your fork

Replace `YOUR_USERNAME` with your GitHub username:

```bash
git clone https://github.com/YOUR_USERNAME/graph-engineering-market-intelligence.git
cd graph-engineering-market-intelligence
```

If you rename the repository, use the renamed repository URL instead.

### 3. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Configure GitHub Actions secrets

Add the following values under:

```text
Settings → Secrets and variables → Actions
```

Required secrets:

| Secret | Purpose | Guide |
| --- | --- | --- |
| `GEMINI_API_KEY` | Gemini model access for the skeptic and synthesis stages | [Gemini Guide](guides/gemini-api-key.md) |
| `TAVILY_API_KEY` | Real-time web search | [Tavily Guide](guides/tavily-api-key.md) |
| `RESEND_API_KEY` | Email delivery | [Resend Guide](guides/resend-api-key.md) |
| `RESEND_RECIPIENT_EMAIL` | Destination for the weekly brief | [Resend Guide](guides/resend-api-key.md) |
| `SLACK_WEBHOOK_URL` | Slack delivery | [Slack Guide](guides/slack-webhook-url.md) |

Claude is optional. If you use it instead of Gemini, see the [Anthropic Guide](guides/anthropic-api-key.md) and provider settings described in [.env.example](.env.example).

Never commit API keys to the repository. Use GitHub Actions secrets for scheduled runs and a local `.env` file for local testing.

### 5. Configure the weekly schedule

The included GitHub Actions workflow runs every Friday at 08:00 using the schedule configured in the workflow file.

GitHub Actions schedules use UTC. Check the effective UTC time for your GitHub account and adjust the cron expression if necessary. You can also trigger the workflow manually from the Actions tab.

### 6. Run local executions

Copy the example environment file:

```bash
cp .env.example .env
```

Add your local credentials, then choose an execution mode:

| Mode | Command | Description |
| :--- | :--- | :--- |
| **Offline Dry-Run** | `python main.py --dry-run` | Uses mock data to test file writing and notification formatting without calling external APIs or spending credits. |
| **Live (No Delivery)** | `python main.py --no-delivery` | Executes live Tavily web searches and LLM synthesis, saving all artifacts in `intel_archive/` while skipping Slack and Email notifications. |
| **Full Live Execution** | `python main.py` | Executes live Tavily searches and LLM synthesis, saves all artifacts in `intel_archive/`, and dispatches Slack and Email notifications. |

Every run archives three artifacts in `intel_archive/`:
- `{date}-founder-brief.md` (synthesized brief)
- `{date}-scouts-raw.json` (raw Tavily search data)
- `{date}-skeptic-audit.md` (audited Skeptic findings)

### 7. Run the workflow

You can run it in either of these ways:

- Trigger the workflow manually from GitHub Actions.
- Wait for the scheduled Friday execution.

The generated Markdown brief, raw Scout search data, and Skeptic audit are saved in `intel_archive/` and committed back to the repository when the workflow runs.

## Customizing the Scouts

Each Scout is a Markdown file inside `scouts/`.

To add a new research angle, create a new file:

```text
scouts/distribution_and_partnerships.md
```

Describe:

1. What the Scout should investigate.
2. Which companies, products, or topics it should monitor.
3. The search terms it should use.
4. What qualifies as a meaningful signal.
5. What evidence should be ignored.
6. What structured information it should return.

Example:

```md
# Distribution and partnerships Scout

## Objective
Identify partnerships, integrations, marketplaces, and distribution moves that could change how product-management software is adopted.

## Search terms
- Linear partnership integration product management
- Jira Product Discovery partnership integration
- product management software marketplace launch
- AI product management distribution partnership

## Look for
- Announced integrations with meaningful product or distribution implications.
- Partnerships that change access to a customer segment.
- Platform or marketplace launches.
- Evidence that a partnership is being used, not only announced.

## Ignore
- Generic partnership announcements without a product or distribution consequence.
- Repeated press-release coverage of the same event.
- Unverified claims about customer adoption.
```

The next run will automatically include the new Scout.

## Customizing the nodes

### `nodes/context.md`

This defines the founder, market, product hypothesis, competitors, and decisions that the final brief should inform.

Change this file when adapting the repository to another business or market.

### `nodes/skeptic.md`

This defines how raw search findings are challenged. The skeptic should remove PR language, unsupported claims, stale information, duplicated reporting, and speculation presented as fact.

### `nodes/synthesis.md`

This defines the final Founder Intelligence Brief structure, tone, date format, and decision-making output.

## Why Graph Engineering?

A single prompt asks one model to research, interpret, fact-check, and grade its own work. That makes it difficult to understand where weak conclusions entered the process.

Graph Engineering separates those responsibilities into connected nodes:

- Scouts perform focused research in parallel.
- The skeptic evaluates evidence independently.
- The synthesis stage combines the surviving signals.
- The archive preserves the output as reusable context.
- The founder makes the final decision.

The goal is not to add agents for their own sake. The goal is to create the smallest useful graph that improves research quality, reduces repeated manual work, and makes the reasoning process easier to inspect.

## Adapting this to your business

To use this workflow for another market:

1. Replace the example in `nodes/context.md`.
2. Update the companies and topics in the existing Scouts.
3. Add or remove Scout files inside `scouts/`.
4. Adjust the search terms for your market.
5. Update `nodes/synthesis.md` so the brief answers your decisions.
6. Run a local dry run.
7. Review the output before enabling scheduled delivery.

Examples of other uses include:

- Monitoring competitors before launching an MVP.
- Tracking customer complaints in a crowded category.
- Validating whether a market is becoming more attractive.
- Following technology and regulatory changes.
- Building a weekly founder research habit without manually opening dozens of tabs.

## Before and after

### Before

```text
Open many tabs → search manually → copy links → remove duplicates →
judge credibility → write notes → decide what matters → repeat next week
```

### After

```text
Define Scouts → run parallel research → challenge evidence →
synthesize signals → review decision brief → archive the result
```

The automation does not replace founder judgment. It reduces the repetitive research work so the founder can spend more time deciding what to validate next.

## Limitations

- Search results can be incomplete, delayed, or biased toward well-indexed sources.
- A skeptic pass can identify weak evidence but cannot guarantee truth.
- Search snippets are not a substitute for reading important primary sources.
- The workflow should support founder judgment, not make high-stakes business decisions automatically.
- The quality of the brief depends heavily on the specificity of the founder context and Scout instructions.

Always inspect the sources behind important claims before acting on them.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Disclaimer

This repository is an educational starter kit. It does not provide investment, legal, financial, or business advice. The example founder and decision context are fictional, while referenced companies and market information may be real.
