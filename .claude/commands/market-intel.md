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
