---
name: parallel-issues
description: Work on multiple tasks simultaneously by spinning up isolated background agents, one per task. Use when the user lists 2+ things to work on at once — issue numbers, bug descriptions, feature requests, or any other work items — and wants them tackled in parallel. Trigger on phrases like "work on these in parallel", "tackle all of these", "run these at the same time", or any time the user hands over a batch of independent tasks.
---

# Parallel Tasks

Spin up one background agent per task, each in its own git worktree, and let them run independently.

## Steps

### 1. Understand the tasks

Each argument is a work item. It could be:
- A GitHub issue number (e.g. `12`) — fetch details with `gh issue view {N} --json number,title,body,state`
- A plain description (e.g. `"fix the login crash"`) — use as-is

For issue numbers, skip any that are already closed or don't exist and tell the user.

### 1b. Triage for OpenSpec

Before creating any worktrees, read each issue's title and body and judge whether it belongs in OpenSpec rather than direct implementation. Flag it as OpenSpec if any of the following are true — judged from the ticket text alone, no code exploration needed:

- Root cause is unclear: the ticket describes a symptom but not why it happens
- A new abstraction or interface will clearly be needed
- Data layer changes are likely (new entity, new repository, new API shape)
- Multiple screens or navigation are affected
- The fix requires an architectural decision

List any flagged issues to the user with a one-line reason and skip them — do not create worktrees or agents for them. Proceed only with the remaining issues.

### 2. Sync and create worktrees

```
git fetch origin
```

For each task, create an isolated worktree off `origin/main`. Derive a short slug for the branch name from the issue number or a few words from the description (e.g. `task/fix-login-crash`):

```
git worktree add .claude/worktrees/{slug} -b {slug} origin/main
```

Resolve the absolute path of each worktree — you'll need it in the agent prompt.

### 3. Spawn background agents

In a single turn, make all Agent tool calls with `run_in_background: true`. Use this prompt for each:

---
Working directory: `{absolute_worktree_path}`
Branch: `{slug}`

Use absolute paths or `git -C {absolute_worktree_path}` for all commands. {task description or "Work on issue #{N}."}

You are running autonomously — do not wait for user input at any point. If you reach a point where you would normally ask the user something, stop and explain what you needed in your final response instead.
---

### 4. Report the launch

```
Launched {N} agents in parallel:

| Task        | Branch             | Worktree                          |
|-------------|--------------------|-----------------------------------|
| #12 - title | fix/issue-12       | .claude/worktrees/fix-issue-12   |
| Fix login   | task/fix-login     | .claude/worktrees/task-fix-login  |

You'll be notified as each one finishes.
```

## Cleanup

Remove each worktree and its local branch as soon as its branch has been pushed — don't wait until all are done:

```
git worktree remove "{absolute_worktree_path}"
git branch -d {slug}
```

This applies whenever a branch gets pushed, including during automerge.
