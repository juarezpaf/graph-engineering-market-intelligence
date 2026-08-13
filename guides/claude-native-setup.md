# Run your weekly market intelligence brief with just Claude

This is the no-code path. If you don't want to touch GitHub Actions, API keys, or Python, use this instead. Everything below runs inside Claude — Claude Code or a Claude Cowork session — using Claude's own web search and its own scheduling. You don't need a Tavily, Gemini, Anthropic API, Resend, or Slack account for this path.

## What you need

- A Claude account with access to Claude Code or Claude Cowork, and to scheduled/recurring tasks.
- A copy of this repository (clone it with git, or download it as a ZIP and unzip it — either works).

That's the entire requirement list.

## Step 1: Open the repository in Claude

Open this folder in Claude Code, or start a Claude Cowork session with access to this folder. You don't need to install any Python packages or configure a `.env` file for this path — that's only needed for the GitHub Actions path.

## Step 2: Run it once, manually

Type:

```text
/market-intel
```

Claude will run the whole pipeline — research, the skeptic pass, and the final brief — and reply with the finished brief. It also saves three files into `intel_archive/`:

- `{date}-founder-brief.md` — the brief itself.
- `{date}-scouts-raw.md` — everything the research found, unfiltered.
- `{date}-skeptic-audit.md` — what survived the skeptic's review, and why the rest didn't.

Read the brief. If it looks right, move on to scheduling it. If something looks off, see "Customizing" below — it's the same customization surface as the GitHub Actions path.

## Step 3: Schedule it to run weekly

Ask Claude, in plain language:

```text
Using the schedule skill, run /market-intel every Friday at 8am.
```

Claude will provision a recurring cloud agent that runs on Anthropic's infrastructure — it runs on schedule whether or not your computer is on. The finished brief will show up wherever your scheduled tasks report back to you (your Claude task history, and a notification if you've enabled them).

You can ask Claude to list, change, or cancel this schedule at any time — it's the same schedule skill you used to create it.

## How the pipeline works

Three kinds of Claude agents do the work, each running on a different model — a cheaper, faster model for the repetitive research work, and stronger models for the judgment calls:

```text
nodes/context.md ──────────────┐
scouts/*.md (N files) ──▶ research-scout ×N [Haiku] (parallel, web search) ──▶ raw findings
                                          │
                                          ▼
                    skeptic [Sonnet] (reads nodes/skeptic.md) ──▶ audited findings
                                          │
                                          ▼
       synthesizer [Sonnet] (reads nodes/synthesis.md + context) ──▶ final brief
                                          │
                       ┌──────────────────┼──────────────────┐
                       ▼                  ▼                  ▼
              intel_archive/*.md   git commit (best-effort)   reply to you =
                                                               delivery
```

| Agent | Model | Why |
| --- | --- | --- |
| `research-scout` | Haiku | One instance runs per scout file, all in parallel, every week. It's a simple search-and-report job, so the cheapest model keeps a weekly run inexpensive. |
| `skeptic` | Sonnet | Deciding what counts as real evidence versus PR language takes real judgment, so it runs on a stronger model. |
| `synthesizer` | Sonnet | Writes the one document you actually read. Quality matters most here, and it only runs once a week — you can change this to Opus in `.claude/agents/synthesizer.md` if you want even more weight on the final brief. |

To change any of these, open the agent's file under `.claude/agents/` and edit the `model:` line in its frontmatter.

## Customizing

Identical to the GitHub Actions path — this is the whole point of sharing the same files:

- Edit `nodes/context.md` to change the founder, market, and decisions the brief should inform.
- Edit `nodes/skeptic.md` to change how evidence is judged.
- Edit `nodes/synthesis.md` to change the brief's structure or tone.
- Add, remove, or rewrite files in `scouts/` to change what gets researched. Every file there becomes a parallel research agent automatically — nothing else needs to change.

## Differences from the GitHub Actions path

- No API keys, no `.env` file, no GitHub Actions secrets.
- Research uses Claude's own web search instead of Tavily.
- Delivery is Claude's own scheduled-task reporting instead of Slack and email. If you want Slack or email delivery specifically, use the GitHub Actions path (see the main [README](../README.md)) instead, or run both paths side by side — they share the same `intel_archive/` folder.
- Both paths write to the same `intel_archive/` folder using the same filenames, so the archive stays a single continuous history no matter which path produced any given week's brief.
