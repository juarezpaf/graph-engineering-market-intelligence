# 🔑 How to Get & Configure Your Slack Webhook URL (`SLACK_WEBHOOK_URL`)

This step-by-step guide explains how to create, retrieve, and configure your **Slack Webhook URL** to post formatted intelligence briefs and alert notifications directly to your team's Slack channel in the Graph Engineering Market Intelligence Pipeline.

> **Note on Slack Webhooks (updated Aug 2026):** Incoming Webhooks provide a lightweight, secure HTTP POST endpoint to publish messages directly into Slack channels using Slack's `mrkdwn` format or rich Block Kit layouts. Always check [api.slack.com/messaging/webhooks](https://api.slack.com/messaging/webhooks) for current API limits and documentation.

---

## 📌 Prerequisites

- An active Slack account and access to a Slack workspace.
- Permissions to install apps or manage integrations in your workspace (or admin approval).
- **100% free of charge** (Slack Incoming Webhooks are supported across all Slack tiers, including Free workspaces).

---

## 🚀 Step-by-Step Setup Guide

### Step 1: Create or Choose a Slack Channel
1. Open your Slack workspace desktop app or browser interface.
2. Select an existing channel (e.g., `#general`) or create a dedicated channel for pipeline briefs (e.g., `#daily-briefs` or `#intel-feed`).

---

### Step 2: Create a Slack App / Webhook Integration
There are two ways to generate an Incoming Webhook URL:

#### Option A: Create a Custom Slack App (Recommended)
1. Navigate to the Slack API portal at **[api.slack.com/apps](https://api.slack.com/apps)**.
2. Click the **Create New App** button.
3. In the modal under **Or start your own way**, select **Blank app** and click **Continue**.
4. Set an **App Name** (e.g., `Market Intelligence Bot`), select your target **Slack Workspace**, and click **Create App**.

#### Option B: Legacy Webhook Directory (Quick Setup)
If your workspace permits legacy incoming webhooks, navigate directly to:
**[slack.com/services/new/incoming-webhook](https://slack.com/services/new/incoming-webhook)**.

---

### Step 3: Activate Incoming Webhooks, Add to Channel & Copy URL
1. In your app settings, click **Incoming Webhooks** in the left sidebar under *Features*.
2. Toggle the switch from **Off** to **On** (top-right corner of the **Activate Incoming Webhooks** card).
3. Once activated, scroll down to the **Webhook URLs for Your Workspace** section and click the **Add New Webhook** button.
4. You'll be taken to an authorization page titled **Allow the "[App Name]" app to access Slack**. Confirm your **Workspace**, then under **Channel for webhook** use the search dropdown to select your target channel (e.g., `#daily-briefs`). Click **Allow**.
5. You'll be redirected back to the Incoming Webhooks page. Your newly generated URL will appear under the **Webhook URLs for Your Workspace** section — it will look like:
   ```text
   https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX
   ```
6. Click **Copy** next to the URL. That's your `SLACK_WEBHOOK_URL`.
   > ⚠️ **IMPORTANT**: Save this Webhook URL in a secure location (like 1Password or Bitwarden). Anyone with access to this URL can post messages to your destination Slack channel.

---

## 🛠️ Where to Add Your Webhook URL

### 1. Local Testing (`.env`)
If you are running the pipeline locally on your Mac:
1. Open your local `.env` file in the root of `graph-engineering-market-intelligence`.
2. Set the `SLACK_WEBHOOK_URL` variable:
   ```env
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX
   ```

### 2. GitHub Actions Automated Pipeline
To allow GitHub Actions to dispatch the morning intel brief to Slack automatically:
1. Open your repository's **Actions secrets** page directly:
   `https://github.com/[GITHUB_USER]/[REPO_NAME]/settings/secrets/actions`
   *(or navigate there via **Settings** ➔ **Secrets and variables** ➔ **Actions**)*
2. Click **New repository secret**.
3. Set:
   - **Name**: `SLACK_WEBHOOK_URL`
   - **Secret**: `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX`
4. Click **Add secret**.

---

## 💬 Payload Formatting & Capabilities (updated Aug 2026)

As of August 2026, Slack Incoming Webhooks support the following specs and formatting rules:

| Feature / Field | Specification | Notes & Best Practice |
| :--- | :--- | :--- |
| **Simple Markdown (`text`)** | Standard Slack `mrkdwn` (`*bold*`, `_italic_`, `~strike~`, `` `code` ``, `> quote`) | Default payload format used by `send_slack_digest()` |
| **Rich Layouts (`blocks`)** | Slack Block Kit UI components | Useful for dividing sections, adding buttons, or header banners |
| **Message Body Limit** | 4,000 characters per text block (40KB total JSON payload) | Extremely long daily briefs will be truncated if they exceed Slack's payload ceiling |
| **Rate Limit** | 1 message / second per webhook | Single-shot delivery in daily runs stays far below Slack's rate cap |
| **Bot Display Identity** | Customizable name & avatar | Configure custom app icon & display name under **Basic Information ➔ Display Information** |

---

## 🔒 Security Best Practices

- **Never Commit Secrets to Git**: Ensure `.env` is listed in your `.gitignore` file.
- **Channel Scoping**: Assign webhooks strictly to the intended channel to prevent unintended broadcasts across public workspace channels.
- **Revocation / Rotation**: If a Webhook URL is accidentally committed to a public repository or exposed in build logs, revoke it immediately at [api.slack.com/apps](https://api.slack.com/apps) under **Incoming Webhooks** and generate a replacement.

---

## ❓ Troubleshooting

| Issue / Error | Cause | Fix |
| :--- | :--- | :--- |
| `404 Not Found` (`no_service` / `channel_not_found`) | Webhook URL was revoked, or the target channel was deleted/archived | Generate a new Incoming Webhook for an active channel via [api.slack.com/apps](https://api.slack.com/apps). |
| `403 Forbidden` (`action_prohibited` / `app_disabled`) | Workspace admin restricted external integrations or disabled the app | Request admin approval to authorize custom apps and incoming webhooks in your workspace. |
| `400 Bad Request` (`invalid_payload` / `msg_too_long`) | Payload JSON is malformed or message body exceeds the 4,000 char / 40KB limit | Verify `text` formatting and ensure payload body size remains under 40KB. |
| `429 Too Many Requests` | Exceeded Slack's 1 msg/sec rate limit | The pipeline dispatches a single notification per run; ensure parallel job loops aren't flooding the webhook. |
