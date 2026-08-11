# 🔑 How to Get & Configure Your Resend API Key (`RESEND_API_KEY`)

This step-by-step guide explains how to create, retrieve, and configure your **Resend API Key** (`RESEND_API_KEY`) and delivery recipient email to power email dispatches in the Graph Engineering Market Intelligence Pipeline.

> **Why Resend?** Unlike personal email providers (such as Gmail), Resend uses scoped, revokable API keys and standard HTTP dispatches without exposing personal account credentials or requiring Google App Passwords.

---

## 📌 Prerequisites

- An active email address.
- **No credit card required** to start (includes **3,000 emails/month free**, far exceeding the ~30 emails/month needed for daily brief dispatches).

---

## 🚀 Step-by-Step Setup Guide

### Step 1: Sign Up / Log In to Resend
1. Open your browser and navigate to **[resend.com](https://resend.com)**.
2. Click **Sign Up** to create a free account or **Log In** if you already have one.

---

### Step 2: Generate an API Key
1. In your Resend dashboard, navigate to **[API Keys](https://resend.com/api-keys)** in the left sidebar.
2. Click **Create API Key**.
3. Set the details:
   - **Name**: `market-intelligence-brief`
   - **Permission**: `Full access` (or `Sending access` restricted to your domain)
   - **Domain**: `All domains` (or select your specific domain)
4. Click **Add**.

---

### Step 3: Copy & Secure Your API Key
1. Copy the generated API key immediately. Resend API keys follow this format:
   ```text
   re_123456789_xxxx...xxxx
   ```
   > ⚠️ **IMPORTANT**: Save this key in a secure password manager. Resend only displays the secret key once upon creation.

---

### Step 4: Sender Email & Testing Setup
- **Testing Sender (Default)**: You can start immediately without domain configuration by using Resend's default onboarding address:
  `Founder Intelligence <onboarding@resend.dev>`
  *(Note: Resend's free `onboarding@resend.dev` sender delivers to the email address registered to your Resend account).*
- **Custom Domain (Optional)**: If you own a domain (e.g. `yourdomain.com`), navigate to **[Domains](https://resend.com/domains)** in Resend, add your domain, configure the DNS records (SPF, DKIM), and use a custom sender like `Founder Intelligence <intel@yourdomain.com>`.

---

## 🛠️ Where to Add Your Credentials

### 1. GitHub Actions (Production Workflow)
For daily automated dispatches at 07:30 UTC:

1. Open your GitHub repository in your browser.
2. Go to **Settings ➔ Secrets and variables ➔ Actions**.
3. Under **Repository secrets**, click **New repository secret** and add:

| Secret Name | Value | Description |
| :--- | :--- | :--- |
| `RESEND_API_KEY` | `re_123456789...` | Scoped API token from Resend |
| `RESEND_RECIPIENT_EMAIL` | `recipient@example.com` | Email address to receive the daily brief |
| `SENDER_EMAIL` *(optional)* | `Founder Intelligence <onboarding@resend.dev>` | Custom sender address |

---

### 2. Local Environment (`.env`)
For testing the pipeline on your local machine:

1. Open `.env` (or copy `.env.example` to `.env`).
2. Add your Resend credentials:
   ```env
   RESEND_API_KEY=re_123456789...
   RESEND_RECIPIENT_EMAIL=your-email@example.com
   SENDER_EMAIL="Founder Intelligence <onboarding@resend.dev>"
   ```
3. Run a local execution or dry-run:
   ```bash
   python main.py --dry-run
   ```

---

## ❓ Troubleshooting

- **Error: `validation_error: Can only send to your own email address`**:
  When using `onboarding@resend.dev`, Resend only allows sending to the email address associated with your Resend account. To send to other addresses, add and verify your custom domain in Resend.
- **Email not appearing in inbox**:
  Check your Spam or Junk folder. If using a custom domain, ensure SPF, DKIM, and DMARC records have fully propagated in Resend's **Domains** tab.
