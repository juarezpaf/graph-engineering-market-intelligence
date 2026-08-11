# 🔑 How to Get & Configure Your Tavily API Key (`TAVILY_API_KEY`)

This step-by-step guide explains how to create, retrieve, and configure your **Tavily API Key** to power web search, live news gathering, and URL content extraction passes in the Graph Engineering Market Intelligence Pipeline.

> **Note on capabilities (updated Aug 2026):** Tavily is built specifically for LLMs and AI agents. Its API supports multiple search depths (`basic` and `advanced`), content extraction (`extract`), mapping, crawling, and multi-step research agents. Always check [docs.tavily.com](https://docs.tavily.com) for current endpoint updates and rate limits.

---

## 📌 Prerequisites

- An active email address, Google account, or GitHub account.
- **No credit card required** for initial signup (includes **1,000 free API credits/month** on the Researcher tier).

---

## 🚀 Step-by-Step Setup Guide

### Step 1: Sign Up / Log In to Tavily
1. Open your browser and navigate to **[tavily.com](https://tavily.com)** or directly to **[app.tavily.com](https://app.tavily.com)**.
2. Sign in with your existing account or click **Sign Up** / **Get Started** to create a new account.

---

### Step 2: Review Credits & Billing
1. Once logged in, check your balance on the **Dashboard Overview** page.
2. New accounts automatically start on the **Researcher (Free)** plan with **1,000 API credits/month**.
3. If your automated pipeline requires higher daily throughput, go to the **Billing / Upgrade** tab to enable Pay-As-You-Go ($0.008/credit) or a monthly subscription plan.

> Free tier credits refresh automatically every month on your billing cycle date. Typical daily cost for the pipeline (6 Scout nodes x 1 basic search/week) is ~25–30 credits/month, well within the free 1,000 credit tier.

---

### Step 3: Generate a New API Key
1. Navigate to the **API Keys** section in your dashboard (or locate your default API key on the main overview screen).
2. Click **Create New Key** (or copy your default key).
3. Enter a descriptive name for your key (e.g., `market-intelligence-brief-prod`).
4. Click **Create**.

---

### Step 4: Copy & Secure Your API Key
1. Copy the generated API key immediately. Tavily API keys follow a prefixed format:
   ```text
   tvly-xxxx...xxxx
   ```
   > ⚠️ **IMPORTANT**: Save this key in a secure location (like 1Password or Bitwarden). Never expose secret keys in public repositories or client-side code.

---

## 🛠️ Where to Add Your API Key

### 1. Local Testing (`.env`)
If you are running the pipeline locally on your Mac:
1. Open your local `.env` file in the root of `graph-engineering-market-intelligence`.
2. Set the `TAVILY_API_KEY` variable:
   ```env
   TAVILY_API_KEY=tvly-your-actual-key-here
   ```

### 2. GitHub Actions Automated Pipeline
To allow GitHub Actions to run web search queries automatically during scheduled runs:
1. Open your repository's **Actions secrets** page directly:
   `https://github.com/[GITHUB_USER]/[REPO_NAME]/settings/secrets/actions`
   *(or navigate there via **Settings** ➔ **Secrets and variables** ➔ **Actions**)*
2. Click **New repository secret**.
3. Set:
   - **Name**: `TAVILY_API_KEY`
   - **Secret**: `tvly-your-actual-key-here`
4. Click **Add secret**.

---

## 🤖 Search Modes & Endpoints (updated Aug 2026)

As of August 2026, Tavily's core capabilities and credit costs include:

| Endpoint / Mode | Credit Cost | Notes & Best Use Case |
| :--- | :--- | :--- |
| **Basic Search** (`depth: "basic"`) | 1 credit / request | Fast, low-latency web retrieval; best for quick news checks and daily delta tracking in Scout nodes |
| **Advanced Search** (`depth: "advanced"`) | 2 credits / request | Deep retrieval; returns comprehensive context chunks for complex synthesis |
| **Basic Extract** (`extract`) | 1 credit per 5 URLs | Parses raw web pages and converts target URL content directly into clean Markdown |
| **Tavily Research** (`research`) | Dynamic (bounded) | Autonomous agentic research pass for generating full structured intelligence reports |

> **Pro Tip for Intelligence Pipelines:** Pass `topic="news"` and specify relative windows like `time_range="day"` or `time_range="week"` in your Tavily search payload to filter out stale context and focus purely on recent changes.

---

## 🔒 Security Best Practices

- **Never Commit Secrets to Git**: Ensure `.env` is listed in your `.gitignore` file.
- **Monitor Usage**: Check your monthly usage bar on the Tavily dashboard to ensure automated daily runs don't prematurely exhaust your monthly credits.
- **Key Rotation**: If you suspect your key was leaked, immediately delete/revoke it in the dashboard and create a replacement key.

---

## ❓ Troubleshooting

| Issue / Error | Cause | Fix |
| :--- | :--- | :--- |
| `401 Unauthorized` | API key is invalid or misspelled | Verify that you copied the complete `tvly-...` key without trailing spaces and pass it as `Bearer tvly-...` in the `Authorization` header or SDK config. |
| `429 Rate Limit Exceeded` / `430 Out of Credits` | Monthly credit limit reached or concurrent request cap hit | Check your remaining credit balance at [app.tavily.com](https://app.tavily.com). Upgrade your plan or purchase additional credits if needed. |
| `400 Bad Request` | Invalid payload or parameter | Verify your request payload (e.g., check that `search_depth` is set to `basic` or `advanced`, and dates follow `YYYY-MM-DD` format). |
| Empty Results | Restrictive domain filters | Check if strict `include_domains` or narrow `time_range` options are accidentally filtering out relevant web results. |
