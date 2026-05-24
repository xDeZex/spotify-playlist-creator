---
name: code-review
description: Spawn a focused code review subagent. Use after every RED/GREEN/REFACTOR cycle (pass the files changed in that cycle), after a commit, or whenever the user asks for a review. Always use this skill for reviews — it ensures the review lens is test-first and findings are fix-oriented.
---

Spawn a code review subagent with the right context and instructions.

## Determine scope

- **Per-behavior cycle** (during openspec apply): the files changed in this RED/GREEN/REFACTOR cycle only — not the full diff
- **Post-commit**: run `git show HEAD` to get the diff
- **Ad-hoc**: whatever the user points at

## Steps

1. **Gather the code to review**
   - Commit review: run `git show HEAD` to get the diff
   - Cycle review: run `git diff HEAD` scoped to the changed files
   
   In both cases the diff tells the reviewer which lines changed. Pass it verbatim — the reviewer reads the full files itself for context.

   **If OpenSpec context will be gathered (step 2):** strip `openspec/changes/**` file sections from the diff before passing it. Those files are already provided as structured context; including them in the diff is redundant.

2. **Gather OpenSpec context** (skip if no active change)

   Run `openspec list --json` to check for an active change. If one exists:

   a. Read `openspec/changes/<name>/proposal.md` and extract the capability names
      listed under **New Capabilities** and **Modified Capabilities**.

   b. For each capability, read:
      - The global spec: `openspec/specs/<capability>/spec.md` — the full current requirements
      - The delta spec: `openspec/changes/<name>/specs/<capability>/spec.md` — what this change declared it would add or modify

   c. Read `openspec/changes/<name>/tasks.md` to know which behavior is currently
      in scope (the task being reviewed).

   Only load specs for capabilities named in the proposal. If the code touches
   something not listed there, note it — undeclared impact is itself a finding.

3. **Read the appropriate reviewer reference** — both files live inside the skill's own directory (`<skill-base-dir>/references/`):
   - Per-cycle review: read `references/reviewer-light.md`
   - Post-commit review: read `references/reviewer.md`

4. **Spawn a subagent** — model and file-reading depth differ by scope:

   **Per-cycle (Haiku):**
   - model: haiku
   - Opening instructions: full content of `references/reviewer-light.md`
   - The diff (verbatim), labelled "Changed lines"
   - An instruction to read ±30 lines of context around each changed hunk only — not the full file
   - If OpenSpec context was gathered: global specs, delta specs, current task description (same as below)
   - A note that this is a per-cycle review

   **Post-commit (Sonnet):**
   - model: sonnet
   - Opening instructions: full content of `references/reviewer.md`
   - The diff (verbatim), labelled "Changed lines"
   - An instruction to read each changed file in full before reviewing
   - If OpenSpec context was gathered:
     - The global specs for each capability, labelled "Requirements (global spec)"
     - The delta specs, labelled "Requirements (this change)"
     - The current task description, labelled "Behavior in scope"
   - A note that this is a post-commit review

5. **Print the full report to the user NOW, before doing anything else.** Output the subagent's report verbatim as a text message. Do not skip ahead to fixing — the user must see the findings first.

6. **Act on findings** — only after printing the report. The subagent reports only; the main Claude acts.

   For each finding:
   - **Fix now** — apply the fix inline immediately (amend if post-commit, in-place if mid-cycle). No confirmation needed.
   - **Needs filing** — present to the user and explain why it can't be fixed inline. Only file after the user confirms.
