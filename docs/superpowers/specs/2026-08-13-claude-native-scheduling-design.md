# Claude-native execution path — design

Date: 2026-08-13
Status: approved

## Problem

The repository currently ships one way to run the intelligence graph: a Python
script (`main.py`) triggered by a GitHub Actions cron schedule, calling
Tavily for search and Gemini/Anthropic for the skeptic and synthesis passes,
delivering via Slack webhook and Resend email. That path requires a GitHub
repo with Actions enabled, four external API keys, and comfort editing
workflow YAML and repo secrets.

The repository's actual audience — founders and product builders, not
necessarily engineers — should be able to run the same graph-engineered
pipeline (parallel research → adversarial skeptic pass → synthesis) with
nothing but a Claude account: no API keys, no GitHub Actions, no code, and no
need to keep a computer open for the weekly run.

## Goals

- Add a second, independent way to run the pipeline, entirely inside Claude
  (Claude Code or Cowork), using Claude's own web search and its own
  scheduled-task delivery instead of Tavily/Gemini/Anthropic-API/Resend/Slack.
- Reuse `nodes/context.md`, `nodes/skeptic.md`, `nodes/synthesis.md`, and
  `scouts/*.md` as the single source of truth for both paths — no duplicated
  prompt text that can drift.
- Preserve the "multiple agents, different models, adversarial skeptic
  removes noise, synthesizer writes the brief" shape the user described,
  using real Claude Code subagents rather than one LLM called twice.
- Make setup something a non-technical founder can complete by cloning/
  downloading the repo and asking Claude, in plain English, to provision the
  schedule — following a guide checked into the repo.
- Change nothing about the existing GitHub Actions / `main.py` path. It stays
  the default, documented, working option.

## Non-goals

- No changes to `main.py`, `src/`, `.github/workflows/`, or the Python test
  suite.
- No renaming of `intel_archive/` artifact filenames — both paths write to
  the same archive using the same naming convention so continuity
  (reading the last brief) works regardless of which path produced it.
- No attempt to replicate Slack/Resend delivery inside the Claude-native
  path. Delivery is whatever the scheduled task's own reporting mechanism
  provides (visible in Claude's task history/notifications).

## Architecture

Two independent run paths, sharing the same node/scout markdown files and
the same `intel_archive/` folder:

1. **Existing path** (unchanged): GitHub Actions → `main.py` → Tavily +
   Gemini/Anthropic → Slack + Resend.
2. **New path**: a Claude Code/Cowork slash command dispatches Claude
   subagents that do the research (via Claude's built-in web search), the
   skeptic pass, and the synthesis pass, then archives the result. Run
   manually, or scheduled as a recurring cloud agent so it runs weekly
   without any machine needing to be open.

## Components

### Subagents (`.claude/agents/`)

Each is a thin wrapper: frontmatter (name, description, allowed tools,
model) plus a body that tells the agent to read the existing node file and
follow it — the node files stay the single source of truth, used by both
the Python pipeline and these subagents.

- **`research-scout.md`** — tools: Read, WebSearch, WebFetch. Model: a fast/
  cheap tier (Haiku), since this is a simple search-and-report job and the
  orchestrator runs several of these concurrently. Given the path to one
  `scouts/*.md` file, it reads that file's objective/search terms/time range/
  topic and runs the research, returning raw findings (title, URL, date,
  snippet) without filtering for quality — filtering is the skeptic's job.
- **`skeptic.md`** — tools: Read. Model: a mid tier (Sonnet). Body instructs
  it to read `nodes/skeptic.md` and apply it exactly to the raw findings it's
  given, removing PR language, stale info, unsupported claims, duplicates.
- **`synthesizer.md`** — tools: Read. Model: a mid/high tier (Sonnet,
  adjustable to Opus in frontmatter). Body instructs it to read
  `nodes/synthesis.md` and apply it exactly to the audited findings plus
  `nodes/context.md`, producing the final brief.

### Orchestrating command — `.claude/commands/market-intel.md`

This is the thing that gets scheduled. On invocation it:

1. Reads `nodes/context.md` and the most recent
   `intel_archive/*-founder-brief.md` (same continuity idea as `main.py`'s
   `read_last_brief()`).
2. Lists `scouts/*.md` and dispatches one `research-scout` subagent per file,
   in parallel (this is the "parallel deep research" the user asked for).
3. Combines the raw findings from all scouts and passes them, plus the last
   brief for continuity, to the `skeptic` subagent.
4. Passes the audited findings plus `nodes/context.md` to the `synthesizer`
   subagent.
5. Writes the same three artifacts `main.py` writes today —
   `{date}-founder-brief.md`, `{date}-scouts-raw.md`, `{date}-skeptic-audit.md`
   — into `intel_archive/`, and commits them if git write access is
   available in the running environment.
6. Ends its final message with the full brief. When this command runs as a
   scheduled cloud agent, that final message is the delivery — it shows up
   in the user's Claude task history/notifications. No Slack/Resend
   dependency.

### Setup guide — `guides/claude-native-setup.md`

Plain-language walkthrough for a non-technical founder:

1. Clone or download the repository, open it in Claude Code or a Claude
   Cowork session with repo access.
2. Run `/market-intel` once manually to confirm it works and inspect the
   output in `intel_archive/`.
3. Ask Claude to schedule it — e.g. "using the schedule skill, run
   `/market-intel` every Friday at 8am UTC" — so Claude provisions the
   recurring cloud agent itself. No separate custom scheduling command is
   built for this; it defers to the platform's existing scheduling
   capability.
4. Customize the same way as the existing path: edit `nodes/context.md`,
   `nodes/skeptic.md`, `nodes/synthesis.md`, add/edit files in `scouts/`.
   Nothing here is Claude-native-specific.

The guide's own data-flow diagram (mirroring the one below) must label each
agent with the model it runs on, so a reader can see the cost/quality
tradeoff at a glance and knows which frontmatter `model:` line to edit if
they want to change it.

### README update

A short new section, "Run without GitHub Actions (Claude-native)," pointing
at the guide and framed as: prefer this path if you don't want to manage
API keys or GitHub Actions secrets. Repository structure listing gains
`.claude/agents/`, `.claude/commands/`, and `guides/claude-native-setup.md`.

## Data flow

```text
nodes/context.md ──────────────┐
scouts/*.md (N files) ──▶ research-scout ×N [Haiku] (parallel, WebSearch) ──▶ raw findings
                                          │
                                          ▼
                    skeptic [Sonnet] (reads nodes/skeptic.md) ──▶ audited findings
                                          │
                                          ▼
       synthesizer [Sonnet, Opus-adjustable] (reads nodes/synthesis.md + context)
                                          │
                                          ▼
                                    final brief
                                          │
                       ┌──────────────────┼──────────────────┐
                       ▼                  ▼                  ▼
              intel_archive/*.md   git commit (best-effort)   final chat
                                                               message =
                                                               delivery
```

| Agent | Model | Why |
| --- | --- | --- |
| `research-scout` | Haiku | Simple search-and-report job, run several times per pipeline execution in parallel — cheapest tier keeps a weekly run inexpensive. |
| `skeptic` | Sonnet | Needs real judgment to separate evidence from PR language and grade confidence — worth the mid tier. |
| `synthesizer` | Sonnet (swap to Opus in frontmatter for more weight on the final brief) | Produces the one artifact the founder actually reads; quality matters most here, and it only runs once per week. |

This table (or an equivalent one) is reproduced in `guides/claude-native-setup.md` so a reader can see the cost/quality tradeoff without opening the agent files.

## Error handling

- A `research-scout` returning no results or erroring: the orchestrator
  notes it and continues with the remaining scouts, mirroring `main.py`'s
  per-query try/except (one bad scout shouldn't kill the run).
- Empty synthesis output: the command refuses to archive or report a brief,
  matching `main.py`'s `RuntimeError` guard against archiving/emailing
  nothing.
- No git write access in the running environment: the command still writes
  the three files to `intel_archive/` and still reports the brief in its
  final message. Archiving to git is best-effort, not required for
  successful delivery.

## Testing / verification

No Python code changes, so the existing test suite is unaffected. Validation
is a live manual run: invoke `/market-intel` once, confirm the three archive
files are written correctly and the final message is a well-formed brief,
before provisioning the recurring schedule.
