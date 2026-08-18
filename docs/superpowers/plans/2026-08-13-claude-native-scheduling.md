# Claude-native execution path Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a second, optional way to run the intelligence graph — entirely inside Claude (Claude Code or Cowork), using Claude's own web search and its own scheduled-task delivery — so a non-technical founder can run and schedule the weekly brief without GitHub Actions, API keys, or code.

**Architecture:** Three thin Claude Code subagents (`research-scout`, `skeptic`, `synthesizer`), each reading the existing `nodes/*.md` / `scouts/*.md` files as its instructions rather than duplicating them, orchestrated by one slash command (`/market-intel`) that dispatches scouts in parallel, then the skeptic, then the synthesizer, and archives the result to the same `intel_archive/` folder the existing GitHub Actions path uses. A setup guide documents running it manually once and then scheduling it via the platform's `schedule` skill.

**Tech Stack:** Claude Code subagent/slash-command markdown files (`.claude/agents/`, `.claude/commands/`), Markdown documentation. No Python, no new dependencies.

**Spec:** [docs/superpowers/specs/2026-08-13-claude-native-scheduling-design.md](../specs/2026-08-13-claude-native-scheduling-design.md)

## Global Constraints

- No changes to `main.py`, `src/`, `.github/workflows/`, or the Python test suite — the existing path stays exactly as-is.
- Archive filenames must be `{ISO date}-founder-brief.md`, `{ISO date}-scouts-raw.md`, `{ISO date}-skeptic-audit.md` inside `intel_archive/`, so the archive is one continuous history no matter which path produced a given week's entry.
- `nodes/context.md`, `nodes/skeptic.md`, `nodes/synthesis.md`, and `scouts/*.md` are the single source of truth for behavior in both paths. Claude-native agents must read those files at runtime — never copy their instructions into agent files.
- The orchestrating command is named `/market-intel` (not `/founder-brief`).
- The Claude-native path must not depend on Tavily, Gemini, the Anthropic API, Resend, or Slack — it uses Claude's own WebSearch/WebFetch tools and reports its result as its own final chat message.

---

### Task 1: `research-scout` subagent

**Files:**
- Create: `.claude/agents/research-scout.md`

**Interfaces:**
- Consumes: nothing from other tasks. Reads a scout file path given to it at dispatch time (any file under `scouts/`, e.g. `scouts/competitor_product_changes.md`), and that file's own `## Search terms` / `## Queries` / `## Search queries`, `## Time range`, `## Topic` sections (format already established by `src/config.py`'s `load_scouts()`).
- Produces: a Claude Code subagent named `research-scout` (tools: `Read, WebSearch, WebFetch`, model: `haiku`) that Task 4 dispatches once per scout file, in parallel.

- [ ] **Step 1: Write the verification check (expect fail)**

Run:
```bash
test -f .claude/agents/research-scout.md && echo "FOUND (unexpected)" || echo "MISSING (expected)"
```
Expected: `MISSING (expected)` — the file doesn't exist yet.

- [ ] **Step 2: Create the agent file**

Write `.claude/agents/research-scout.md`:

````markdown
---
name: research-scout
description: Runs the research for exactly one scout brief from scouts/*.md using web search, and returns raw unfiltered findings. Dispatch one instance per scout file, in parallel, from the /market-intel command.
tools: Read, WebSearch, WebFetch
model: haiku
---

You are a research scout in a graph-engineered market intelligence pipeline.

You will be given the path to exactly one file under `scouts/` (for example `scouts/competitor_product_changes.md`).

1. Read that file. It defines your objective, time range, topic, and search terms (listed under a `## Search terms`, `## Queries`, or `## Search queries` heading).
2. Run each search term with WebSearch, biasing toward results published within the file's stated time range.
3. For any especially promising or ambiguous result, use WebFetch on its URL to confirm the specific claim and publication date before reporting it.
4. Deduplicate results by URL.

Return raw findings only. Do not judge credibility, relevance, or quality — that happens downstream in the skeptic pass. Do not pad your output with weak results just to have something to show: if a search term returns nothing useful, say so and move on.

For each finding, report:

- **Title**
- **URL**
- **Date** (publication or last-updated date, or `unknown` if the source does not state one)
- **Snippet** — one to two sentences of what the source actually says, in your own words

Output format:

```md
## Scout: [scout file name, e.g. Competitor Product Changes Scout]

### [Finding title]
- **URL:** [url]
- **Date:** [date or "unknown"]
- **Snippet:** [what it says]
```

Repeat the finding block for each result. If nothing useful was found for this scout, say so plainly instead of returning an empty or padded section.
````

- [ ] **Step 3: Run the verification checks (expect pass)**

Run:
```bash
grep -q '^name: research-scout$' .claude/agents/research-scout.md && \
grep -q '^tools: Read, WebSearch, WebFetch$' .claude/agents/research-scout.md && \
grep -q '^model: haiku$' .claude/agents/research-scout.md && \
echo "PASS"
```
Expected: `PASS`.

- [ ] **Step 4: Commit**

```bash
git add .claude/agents/research-scout.md
git commit -m "feat: add research-scout Claude-native subagent"
```

---

### Task 2: `skeptic` subagent

**Files:**
- Create: `.claude/agents/skeptic.md`

**Interfaces:**
- Consumes: nothing from other tasks. Reads `nodes/skeptic.md` at runtime for its actual operating rules.
- Produces: a Claude Code subagent named `skeptic` (tools: `Read`, model: `sonnet`) that Task 4 dispatches once, after all `research-scout` agents return.

- [ ] **Step 1: Write the verification check (expect fail)**

Run:
```bash
test -f .claude/agents/skeptic.md && echo "FOUND (unexpected)" || echo "MISSING (expected)"
```
Expected: `MISSING (expected)`.

- [ ] **Step 2: Create the agent file**

Write `.claude/agents/skeptic.md`:

```markdown
---
name: skeptic
description: Adversarial quality pass over combined raw scout findings. Removes PR language, stale information, unsupported claims, and duplicated reporting, and grades what survives. Dispatch once, after all research-scout agents have returned, from the /market-intel command.
tools: Read
model: sonnet
---

You are the skeptic node in a graph-engineered market intelligence pipeline.

Read `nodes/skeptic.md` from the repository root and follow its instructions exactly. That file defines your full operating rules: evidence standards, what to remove or downgrade, competitor and customer-evidence handling, confidence classification, and the required output format. Do not deviate from the output format it specifies.

Your task prompt will contain:

- The combined raw findings from this run's research scouts, labeled by scout.
- The most recent previous brief, if one exists, for continuity — so you can tell a genuinely new development from an old story being re-reported.

Apply `nodes/skeptic.md` to that input and return only the audited findings, in the format that file specifies. Do not add commentary outside that format.
```

- [ ] **Step 3: Run the verification checks (expect pass)**

Run:
```bash
grep -q '^name: skeptic$' .claude/agents/skeptic.md && \
grep -q '^tools: Read$' .claude/agents/skeptic.md && \
grep -q '^model: sonnet$' .claude/agents/skeptic.md && \
grep -q 'nodes/skeptic.md' .claude/agents/skeptic.md && \
echo "PASS"
```
Expected: `PASS`.

- [ ] **Step 4: Commit**

```bash
git add .claude/agents/skeptic.md
git commit -m "feat: add skeptic Claude-native subagent"
```

---

### Task 3: `synthesizer` subagent

**Files:**
- Create: `.claude/agents/synthesizer.md`

**Interfaces:**
- Consumes: nothing from other tasks. Reads `nodes/synthesis.md` and `nodes/context.md` at runtime.
- Produces: a Claude Code subagent named `synthesizer` (tools: `Read`, model: `sonnet`) that Task 4 dispatches once, after `skeptic` returns.

- [ ] **Step 1: Write the verification check (expect fail)**

Run:
```bash
test -f .claude/agents/synthesizer.md && echo "FOUND (unexpected)" || echo "MISSING (expected)"
```
Expected: `MISSING (expected)`.

- [ ] **Step 2: Create the agent file**

Write `.claude/agents/synthesizer.md`:

```markdown
---
name: synthesizer
description: Writes the final market intelligence brief from the skeptic's audited findings. Dispatch once, after the skeptic agent has returned, from the /market-intel command.
tools: Read
model: sonnet
---

You are the synthesis node in a graph-engineered market intelligence pipeline.

Read `nodes/synthesis.md` from the repository root and follow its instructions exactly. That file defines the required brief structure, tone, source-handling rules, date formatting, and final quality checks. Also read `nodes/context.md` for the standing business and product context the brief must connect findings to.

Your task prompt will contain:

- The audited findings returned by the skeptic agent.
- The human-readable date to use in the brief title, already formatted as `D MMM YYYY` (e.g. `5 Aug 2026`).

Apply `nodes/synthesis.md` to that input, using the given date wherever it specifies `{{HUMAN_DATE}}`. Return only the final brief in the exact format `nodes/synthesis.md` specifies — your entire response becomes the archived and delivered brief, so include no commentary before or after it.
```

- [ ] **Step 3: Run the verification checks (expect pass)**

Run:
```bash
grep -q '^name: synthesizer$' .claude/agents/synthesizer.md && \
grep -q '^tools: Read$' .claude/agents/synthesizer.md && \
grep -q '^model: sonnet$' .claude/agents/synthesizer.md && \
grep -q 'nodes/synthesis.md' .claude/agents/synthesizer.md && \
grep -q 'nodes/context.md' .claude/agents/synthesizer.md && \
echo "PASS"
```
Expected: `PASS`.

- [ ] **Step 4: Commit**

```bash
git add .claude/agents/synthesizer.md
git commit -m "feat: add synthesizer Claude-native subagent"
```

---

### Task 4: `/market-intel` orchestrating command

**Files:**
- Create: `.claude/commands/market-intel.md`

**Interfaces:**
- Consumes: subagent names `research-scout` (Task 1), `skeptic` (Task 2), `synthesizer` (Task 3).
- Produces: a slash command invocable as `/market-intel` that writes `intel_archive/{ISO date}-founder-brief.md`, `intel_archive/{ISO date}-scouts-raw.md`, `intel_archive/{ISO date}-skeptic-audit.md`, and reports the final brief as its own last message. Task 5 (the guide) and Task 6 (README) both reference this command by name.

- [ ] **Step 1: Write the verification check (expect fail)**

Run:
```bash
test -f .claude/commands/market-intel.md && echo "FOUND (unexpected)" || echo "MISSING (expected)"
```
Expected: `MISSING (expected)`.

- [ ] **Step 2: Create the command file**

Write `.claude/commands/market-intel.md`:

```markdown
---
description: Run the full graph-engineered market intelligence pipeline (parallel research scouts, adversarial skeptic pass, synthesis) using Claude's own subagents, then archive and report the brief.
---

Run the market intelligence graph pipeline end to end using this repository's node and scout definitions. Follow these steps in order and do not skip any of them.

## 1. Load context and continuity

- Read `nodes/context.md`.
- Find the most recent file matching `intel_archive/*-founder-brief.md`, if any (the ISO-date filename prefix sorts correctly, so the lexicographically last match is the most recent). Read it for continuity. If none exists, proceed with no prior brief and note that this is the first run.

## 2. Run parallel research scouts

- List every file in `scouts/`.
- For each scout file, dispatch a `research-scout` subagent and give it the path to that one file. Dispatch all of them together, in parallel, in a single batch of Task calls — do not run them one at a time.
- Wait for all of them to return. If any scout errors or returns nothing useful, note that in the combined output and continue with the rest — one bad scout must not abort the run.
- Combine every scout's raw findings into one block, clearly labeled by scout name.

## 3. Run the skeptic pass

Dispatch the `skeptic` subagent once. Give it:

- The combined raw findings from step 2.
- The previous brief from step 1, or the text `No previous brief found.` if there wasn't one.

Wait for it to return the audited findings.

## 4. Run the synthesis pass

- Compute today's date in two forms:
  - ISO date `YYYY-MM-DD`, used for filenames.
  - Human date `D MMM YYYY` — no leading zero on the day, 3-letter month, no comma (e.g. `5 Aug 2026`) — used inside the brief.
- Dispatch the `synthesizer` subagent once. Give it the audited findings from step 3 and the human date.
- Wait for it to return the final brief.
- If the returned brief is empty or only whitespace, stop here. Report that synthesis produced an empty brief and do not proceed to archiving or step 6.

## 5. Archive

Create the `intel_archive/` directory if it doesn't already exist. Using the ISO date from step 4, write:

- `intel_archive/{ISO date}-founder-brief.md` — the final brief from step 4, written exactly as returned.
- `intel_archive/{ISO date}-scouts-raw.md` — the combined raw findings from step 2.
- `intel_archive/{ISO date}-skeptic-audit.md` — the audited findings from step 3.

If this directory is inside a git repository and you have write access, stage and commit these three files with the message `chore: archive market intelligence brief [claude-native]`. If committing fails, or there is no git access, do not treat that as a failure of the run — the files on disk are what matters, and step 6 is the actual delivery.

## 6. Report

Reply with the final brief from step 4, verbatim, as your entire final message — no preamble, no summary of what you did, nothing after it. When this command runs as a scheduled task, this message is what reaches the user.
```

- [ ] **Step 3: Run the verification checks (expect pass)**

Run:
```bash
grep -q '^description:' .claude/commands/market-intel.md && \
grep -q 'research-scout' .claude/commands/market-intel.md && \
grep -q 'skeptic' .claude/commands/market-intel.md && \
grep -q 'synthesizer' .claude/commands/market-intel.md && \
grep -q 'intel_archive/{ISO date}-founder-brief.md' .claude/commands/market-intel.md && \
grep -q 'nodes/context.md' .claude/commands/market-intel.md && \
echo "PASS"
```
Expected: `PASS`.

Also confirm every file it reads by name actually exists in the repo:
```bash
test -f nodes/context.md && test -d scouts && echo "PASS"
```
Expected: `PASS`.

- [ ] **Step 4: Commit**

```bash
git add .claude/commands/market-intel.md
git commit -m "feat: add /market-intel orchestrating command"
```

---

### Task 5: Setup guide

**Files:**
- Create: `guides/claude-native-setup.md`

**Interfaces:**
- Consumes: command name `/market-intel` (Task 4), agent-to-model mapping (Tasks 1–3: `research-scout`→haiku, `skeptic`→sonnet, `synthesizer`→sonnet).
- Produces: `guides/claude-native-setup.md`, referenced by Task 6's README update.

- [ ] **Step 1: Write the verification check (expect fail)**

Run:
```bash
test -f guides/claude-native-setup.md && echo "FOUND (unexpected)" || echo "MISSING (expected)"
```
Expected: `MISSING (expected)`.

- [ ] **Step 2: Create the guide**

Write `guides/claude-native-setup.md`:

````markdown
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
````

- [ ] **Step 3: Run the verification checks (expect pass)**

Run:
```bash
grep -q '/market-intel' guides/claude-native-setup.md && \
grep -q 'research-scout' guides/claude-native-setup.md && \
grep -q 'Haiku' guides/claude-native-setup.md && \
grep -q 'schedule skill' guides/claude-native-setup.md && \
grep -q '## Customizing' guides/claude-native-setup.md && \
echo "PASS"
```
Expected: `PASS`.

- [ ] **Step 4: Commit**

```bash
git add guides/claude-native-setup.md
git commit -m "docs: add Claude-native setup guide"
```

---

### Task 6: README updates

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: guide path `guides/claude-native-setup.md` (Task 5), new file paths from Tasks 1–5.
- Produces: an updated README with a pointer to the Claude-native path and an accurate repository structure tree. No other file depends on this one.

- [ ] **Step 1: Write the verification check (expect fail)**

Run:
```bash
grep -q 'claude-native-setup.md' README.md && echo "FOUND (unexpected)" || echo "MISSING (expected)"
```
Expected: `MISSING (expected)`.

- [ ] **Step 2: Add the new section**

In `README.md`, insert a new section immediately before the `## Quick start` heading (i.e. right after the `## Requirements` section ends):

```markdown
## Run without GitHub Actions (Claude-native)

If you don't want to manage GitHub Actions secrets or sign up for Tavily, Gemini/Anthropic, and Resend, there's a second way to run this: entirely inside Claude, using Claude's own web search and Claude's own scheduled tasks. No API keys, no `.env` file, no code changes — just this repository and a Claude account.

See [guides/claude-native-setup.md](guides/claude-native-setup.md) for the full walkthrough. Both paths read the same `nodes/` and `scouts/` files and write to the same `intel_archive/` folder, so you can use either one — or both — without maintaining two configurations.

The rest of this README describes the original GitHub Actions path.

```

- [ ] **Step 3: Update the repository structure tree**

In the `## Repository structure` section, replace the existing tree:

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

with:

```text
.
├── .claude/
│   ├── agents/
│   │   ├── research-scout.md
│   │   ├── skeptic.md
│   │   └── synthesizer.md
│   └── commands/
│       └── market-intel.md
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
│   ├── tavily-api-key.md
│   └── claude-native-setup.md
├── main.py
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── LICENSE
└── README.md
```

- [ ] **Step 4: Run the verification checks (expect pass)**

Run:
```bash
grep -q '## Run without GitHub Actions (Claude-native)' README.md && \
grep -q 'guides/claude-native-setup.md' README.md && \
grep -q '.claude/agents/research-scout.md' README.md && \
grep -q '.claude/commands/market-intel.md' README.md && \
grep -q 'claude-native-setup.md' README.md && \
echo "PASS"
```
Expected: `PASS`.

- [ ] **Step 5: Commit**

```bash
git add README.md
git commit -m "docs: point README at the Claude-native path"
```

---

### Task 7: Cross-file integration check

**Files:**
- No new files. Verifies the wiring across all files from Tasks 1–6.

**Interfaces:**
- Consumes: every file produced by Tasks 1–6.
- Produces: a pass/fail confirmation that the pieces are correctly cross-referenced. No later task depends on this one — it is the final gate before handing off to the user for the live end-to-end test described in the spec's Testing section (which requires a real Claude Code/Cowork environment with WebSearch access, and is therefore run by the user via `guides/claude-native-setup.md` Step 2, not by this plan).

- [ ] **Step 1: Run the full integration check**

Run:
```bash
set -e

# All three agent files exist with matching names.
for f in research-scout skeptic synthesizer; do
  test -f ".claude/agents/${f}.md"
  grep -q "^name: ${f}\$" ".claude/agents/${f}.md"
done

# The command references all three agents by name and the correct archive paths.
test -f .claude/commands/market-intel.md
grep -q 'research-scout' .claude/commands/market-intel.md
grep -q 'skeptic' .claude/commands/market-intel.md
grep -q 'synthesizer' .claude/commands/market-intel.md

# Every file the agents/command claim to read actually exists.
test -f nodes/context.md
test -f nodes/skeptic.md
test -f nodes/synthesis.md
test -d scouts

# The guide references the actual command name and exists where the README points.
test -f guides/claude-native-setup.md
grep -q '/market-intel' guides/claude-native-setup.md

# README points at the guide with a working relative path.
grep -q 'guides/claude-native-setup.md' README.md
test -f "$(dirname README.md)/guides/claude-native-setup.md"

echo "ALL INTEGRATION CHECKS PASSED"
```
Expected: `ALL INTEGRATION CHECKS PASSED`, with no assertion failures above it.

- [ ] **Step 2: If anything failed, fix it in the relevant task's file and re-run Step 1**

Do not commit a fix here without re-running the full check — this task's only job is to catch cross-file drift between Tasks 1–6.

- [ ] **Step 3: Confirm nothing outside the intended scope changed**

Run:
```bash
git status --porcelain
git diff --stat main.py src/ .github/workflows/ tests/ 2>/dev/null || true
```
Expected: `git status` shows only files from Tasks 1–6 (already committed) and no unexpected modifications; the `git diff --stat` on the protected paths produces no output, confirming the Global Constraint that those files are untouched.

No commit needed for this task unless Step 2 required a fix — in that case, commit the fix with a message describing what cross-reference was broken.
