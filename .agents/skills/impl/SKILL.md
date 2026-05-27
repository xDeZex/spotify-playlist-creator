---
name: impl
description: Implementation skill for shorter tasks that don't need full OpenSpec. Use this whenever the user points at work to be done — an issue, a bug, a feature request, "work on this", "fix this", "implement X". The user should not have to specify anything beyond what the task is. This skill investigates silently, forms its own understanding, and presents a crisp summary before implementing. Always use this skill for concrete implementation tasks that aren't going through OpenSpec.
---

# impl

The user just pointed at something to build or fix. Your job is to figure it out, not ask them to.

## 0. Pre-triage (task description only — no code exploration yet)

Read the task description. If it describes only a symptom or desired end-state with no diagnosis and no identified approach — stop immediately and tell the user this needs OpenSpec. Do not open any files. The signal is: you cannot tell from the description alone *why* something is broken or *how* to approach it, only *what* the problem or goal is.

If the description contains a diagnosis, a recommended approach, or a clear description of what code needs to change, proceed to step 1.

## 1. Investigate silently

Read the issue or task description. Explore the codebase — find the relevant files, understand the existing patterns, identify what already exists and what's missing. Do all of this without saying anything.

## 2. Present one crisp summary

After investigating, present a short brief — not a plan document, just a clear statement of what you understood and what you decided:

- **What this is**: one sentence on the behavior being added or fixed
- **What this is NOT**: the scope boundary — what you're explicitly not changing
- **Files**: the specific files you'll touch
- **Assumptions**: decisions you made that the task didn't specify — stated as facts, not questions ("I'm treating X as Y based on the existing pattern")
- **Size**: assess against these criteria and state your verdict clearly:
  - **Use Haiku** — small: 1-2 production files, no new interfaces, no architectural decisions. Say so and wait for the go-ahead to switch.
  - **Use impl as-is** — medium: 3-4 files, no new abstractions, change is self-contained.
  - **Stop and redirect to OpenSpec** — too big: any of the following apply: new interface or abstraction needed, data layer changes (new Room entity, new repository, new API shape), multiple screens affected, navigation changes, or the approach requires an architectural decision. In this case, do not implement — tell the user this needs OpenSpec and briefly say why.

Wait for a go-ahead or a correction. If the user says nothing is wrong, proceed.

## 3. Implement

Work through the change. TDD and commit discipline are handled by project conventions — follow them.

---

The key principle: be opinionated, not inquisitive. Investigate, decide, tell the user what you decided. Only surface something to the user when you genuinely cannot determine it from the task and codebase.
