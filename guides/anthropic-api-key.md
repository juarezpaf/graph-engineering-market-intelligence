# 🔑 How to Get & Configure Your Anthropic API Key (`ANTHROPIC_API_KEY`)

This step-by-step guide explains how to create, retrieve, and configure your **Anthropic API Key** to power the **Skeptic Audit** and **Chief-of-Staff Synthesis** passes in the Graph Engineering Market Intelligence Pipeline (using Claude Haiku 4.5 / Sonnet 5 or newer).

> **Note on model availability (added Aug 2026):** Anthropic's frontier lineup can change quickly — in June 2026, its newest models (Fable 5 / Mythos 5) were briefly suspended worldwide for three weeks due to a U.S. export-control order, then restored. Always sanity-check the model list below against [platform.claude.com/docs/en/about-claude/models/overview](https://platform.claude.com/docs/en/about-claude/models/overview) before deploying.

---

## 📌 Prerequisites

- An active email address or Google account.
- A credit/debit card to fund your Anthropic Console billing account (typical daily cost for this pipeline is **~$0.03 – $0.05/day**).

---

## 🚀 Step-by-Step Setup Guide

### Step 1: Sign Up / Log In to the Anthropic Platform
1. Open your browser and navigate to **[platform.claude.com](https://platform.claude.com/)**.
2. Sign in with your existing account or click **Sign Up** to create a new account.

> The old `console.anthropic.com` address now redirects here. Note that this developer console and its billing are **separate** from any `claude.ai` Pro/Max subscription — a subscription does not include API credits.

---

### Step 2: Add Credits / Setup Billing
Go to **[platform.claude.com/settings/billing](https://platform.claude.com/settings/billing)** (Settings → Billing) and click the **Buy credits** button.

Add a minimum credit deposit (e.g., $5.00 – $10.00). This will cover several months of daily brief synthesis runs.

> Credits expire one year from purchase and purchases are non-refundable, per Anthropic's billing terms.

---

### Step 3: Generate a New API Key
There are two ways to reach the API Keys page:
- From the **Dashboard**: click the **Get API key** button in the top-right corner of **[platform.claude.com/dashboard](https://platform.claude.com/dashboard)**.
- From the **left sidebar**: go to **Settings → API Keys** (direct link: [platform.claude.com/settings/keys](https://platform.claude.com/settings/keys)).

Once on the API Keys page:
1. Click the **Create Key** button.
2. Enter a descriptive name for your key (e.g., `market-intelligence-brief-prod`).
3. Click **Create Key**.

---

### Step 4: Copy & Secure Your API Key
1. Copy the generated secret key immediately. It will look like:
   ```text
   sk-ant-api03-xxxx...xxxx
   ```
   > ⚠️ **IMPORTANT**: Save this key in a secure location (like 1Password or Bitwarden). Anthropic will only show you the secret key once.

   > Note: if you're using a first-party tool like Claude Code, you may also see `sk-ant-oat01-...` OAuth tokens — these bill against a Pro/Max subscription, not API credits, and are not interchangeable with the `sk-ant-api03-` key this guide covers.

---

## 🛠️ Where to Add Your API Key

### 1. Local Testing (`.env`)
If you are running the pipeline locally on your Mac:
1. Open your local `.env` file in the root of `graph-engineering-market-intelligence`.
2. Set the `ANTHROPIC_API_KEY` variable:
   ```env
   ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
   ```

### 2. GitHub Actions Automated Pipeline
To allow GitHub Actions to run the daily morning brief automatically:
1. Open your repository's **Actions secrets** page directly:
   `https://github.com/[GITHUB_USER]/[REPO_NAME]/settings/secrets/actions`
   *(or navigate there via **Settings** ➔ **Secrets and variables** ➔ **Actions**)*
2. Click **New repository secret**.
3. Set:
   - **Name**: `ANTHROPIC_API_KEY`
   - **Secret**: `sk-ant-api03-your-actual-key-here`
4. Click **Add secret**.

---

## 🤖 Which Model to Use (updated Aug 2026)

As of August 2026, Anthropic's current lineup and API model IDs are:

| Model | API model string | Notes |
| :--- | :--- | :--- |
| Claude Haiku 4.5 | `claude-haiku-4-5-20251001` (alias `claude-haiku-4-5`) | Fastest, cheapest — good fit for the Skeptic Audit pass |
| Claude Sonnet 5 | `claude-sonnet-5` | Best speed/intelligence balance — good default for Chief-of-Staff Synthesis |
| Claude Opus 5 | `claude-opus-5` | Highest capability, higher cost — use only if synthesis quality needs it |
| Claude Fable 5 | `claude-fable-5` | Mythos-tier, most capable widely-released model; availability has been suspended before (see note above) |

Model IDs without a date (e.g. `claude-sonnet-5`) are **pinned snapshots**, not evergreen "latest" pointers — they won't silently change out from under your pipeline, but you'll need to update the string yourself when a new generation ships.

---

## 🔒 Security Best Practices

- **Never Commit Secrets to Git**: Ensure `.env` is listed in your `.gitignore` file.
- **Set Spend Limits**: Go to **Manage ➔ Limits** (`https://platform.claude.com/settings/limits`), scroll down to the **Spend limits** section, and click **Adjust limit** to set a monthly cap (e.g. $10.00/mo) to prevent unexpected usage spikes.
- **Key Rotation**: If you suspect your API key was leaked, immediately go to `platform.claude.com/settings/keys` and click **Delete / Revoke**, then create a replacement key.

---

## ❓ Troubleshooting

| Issue / Error | Cause | Fix |
| :--- | :--- | :--- |
| `401 Unauthorized` | API key is invalid or misspelled | Check that you copied the complete `sk-ant-api03-...` string without trailing spaces, and that it's sent as the `x-api-key` header (not `Authorization`). |
| `400 invalid_request_error` ("Your credit balance is too low") | Account out of credits | Go to **Settings → Billing** at [platform.claude.com](https://platform.claude.com/settings/billing) and click **Buy credits**. |
| `429 Rate Limit Exceeded` | Too many concurrent requests | The pipeline runs sequentially; ensure you don't have duplicate parallel workflows executing at once. |
| `529 Overloaded` | Anthropic's API is temporarily over capacity | Retry with backoff; this is on Anthropic's side, not a config issue on yours. Check [status.anthropic.com](https://status.anthropic.com) if it persists. |
