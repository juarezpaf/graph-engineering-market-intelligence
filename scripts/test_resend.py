"""
Quick Resend email test — sends the latest founder brief in intel_archive.
Usage: .venv/bin/python scripts/test_resend.py
"""
import os
import sys
import pathlib
import markdown
import resend

# Add project root to sys.path
REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

resend.api_key = os.environ["RESEND_API_KEY"]
recipient = os.environ["RESEND_RECIPIENT_EMAIL"]
sender = os.environ.get("SENDER_EMAIL", "Founder Intelligence <onboarding@resend.dev>")

# Read the brief relative to REPO_ROOT
archive_dir = REPO_ROOT / "intel_archive"
briefs = sorted(archive_dir.glob("*-founder-brief.md"), reverse=True) or sorted(archive_dir.glob("*.md"), reverse=True)
if not briefs:
    raise FileNotFoundError("No markdown briefs found in intel_archive/")

brief_path = briefs[0]
with open(brief_path, "r", encoding="utf-8") as f:
    md_content = f.read()

# Convert to HTML
html_body = markdown.markdown(md_content, extensions=["extra"])

styled_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6; color: #1e293b; background-color: #f8fafc; padding: 16px; margin: 0;
        }}
        .container {{
            max-width: 600px; margin: 0 auto; background: #ffffff; padding: 24px;
            border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        h1 {{ font-size: 20px; color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; }}
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
    "from": sender,
    "to": [recipient],
    "subject": f"⚡ [TEST] Founder Intelligence Brief ({brief_path.stem})",
    "html": styled_html,
    "text": md_content,
}

print(f"📧 Sending test email to {recipient} via Resend using {brief_path.name}...")
email = resend.Emails.send(params)
print(f"✅ Sent! Resend ID: {email.get('id')}")
