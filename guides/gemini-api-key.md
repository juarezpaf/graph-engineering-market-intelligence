# 🔑 How to Get & Configure Your Google Gemini API Key (`GEMINI_API_KEY`)

This guide walks through creating a **free** Google AI Studio API key to power the **Skeptic Audit** and **Chief-of-Staff Synthesis** passes (Nodes 3 and 4) of the Graph Engineering Market Intelligence Pipeline.

> **Why Gemini is the default:** this pipeline makes two LLM calls per day. Google AI Studio's free tier allows roughly 1,500 requests/day at no cost and requires no credit card, so a daily brief runs comfortably inside it forever.

---

## 📌 Prerequisites

- A Google account.
- **No credit card required.** The free tier does not need billing enabled.

---

## 🚀 Step-by-Step Setup Guide

### Step 1: Open Google AI Studio
Navigate to **[aistudio.google.com](https://aistudio.google.com/)** and sign in with your Google account.

### Step 2: Create an API Key
1. Click **Get API key** (top-left sidebar, or visit [aistudio.google.com/apikey](https://aistudio.google.com/apikey)).
2. Click **Create API key**.
3. Select an existing Google Cloud project, or let AI Studio create one for you.

### Step 3: Copy & Secure Your Key
Copy the generated key immediately. It looks like:

```text
AIzaSy...
```

> ⚠️ Store it in a password manager. Treat it like a password — anyone with this key can spend your quota.

---

## 🛠️ Where to Add Your API Key

### 1. Local Testing (`.env`)
```env
GEMINI_API_KEY=AIzaSy-your-actual-key-here
```

### 2. GitHub Actions Automated Pipeline
1. Open `https://github.com/[GITHUB_USER]/[REPO_NAME]/settings/secrets/actions`
   *(or **Settings** ➔ **Secrets and variables** ➔ **Actions**)*
2. Click **New repository secret**.
3. Set **Name** to `GEMINI_API_KEY` and **Secret** to your key.
4. Click **Add secret**.

---

## 🤖 Which Model to Use

| Model | API model string | Notes |
| :--- | :--- | :--- |
| Gemini 3.6 Flash | `gemini-3.6-flash` | **Default.** Best free-tier balance of quality and quota |
| Gemini 3.5 Flash | `gemini-3.5-flash` | Previous generation — use if you hit a 3.6 availability issue |
| Gemini 3.5 Flash-Lite | `gemini-3.5-flash-lite` | Lowest latency and cost; noticeably weaker synthesis prose |

Override the default by setting `LLM_MODEL` (locally in `.env`, or as a GitHub Actions **variable**, not a secret).

Model availability changes — check [ai.google.dev/gemini-api/docs/models](https://ai.google.dev/gemini-api/docs/models) before pinning a new one.

---

## 🔒 Security Best Practices

- **Never commit secrets to Git.** `.env` is already in `.gitignore`.
- **Restrict the key** in Google Cloud Console → **APIs & Services → Credentials** if you want to limit it to the Generative Language API.
- **Rotate on leak**: delete the key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey) and create a replacement.

---

## ❓ Troubleshooting

| Issue / Error | Cause | Fix |
| :--- | :--- | :--- |
| `400 API key not valid` | Key is misspelled or revoked | Re-copy the full `AIzaSy...` string with no trailing whitespace. |
| `429 RESOURCE_EXHAUSTED` | Free-tier quota exceeded | The pipeline uses 2 requests/day — if you hit this, another workload shares the key. Check quota at [aistudio.google.com/rate-limit](https://aistudio.google.com/rate-limit). |
| `LLMEmptyResponseError` | A safety filter blocked the response | The pipeline deliberately fails rather than deliver an empty brief. Inspect the scout queries in `config.py` for terms that may be tripping filters. |
| `LLMConfigError: Multiple provider keys are set` | Both `GEMINI_API_KEY` and `ANTHROPIC_API_KEY` present | Set `LLM_PROVIDER=gemini` (or `anthropic`) to choose explicitly. |
| `404 model not found` | `LLM_MODEL` names a retired model | Check the model table above and [ai.google.dev/gemini-api/docs/models](https://ai.google.dev/gemini-api/docs/models). |
