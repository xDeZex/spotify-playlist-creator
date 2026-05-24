# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A script that reads a user's Saved Albums and organizes them inside Spotify — creating one Artist Folder per artist, each containing one Album Playlist per Release. See `CONTEXT.md` for the full domain vocabulary.

## General rules

Never `git push` unless explicitly told to.

Before starting any work, run `git fetch origin && git rebase origin/main` to ensure the branch is up to date.

Before committing, do a quick self-review of `git diff HEAD`. Catch surface-level issues yourself so the reviewer only sees substantive ones.

**Every commit and every amend must be followed by a `code-review` skill run before anything else happens.** Invoke it with `git show HEAD` immediately after `git commit` or `git commit --amend`. Do not respond to the user, start the next task, or take any other action until the review is complete and all findings are resolved. The only exception: an amend whose entire diff is pure style or naming (import order, test rename, comment wording) — skip the re-review only in that case. When in doubt, run it.

For each reviewer finding, fix it — via amend if introduced by this commit, inline otherwise. Only file a GitHub issue when the fix is too large or too risky to do now. Default to fixing, not filing.

Each PR must have exactly one commit and must target `main`. All fixes and follow-ups go into the same commit via `git commit --amend`, not as new commits. If the branch contains multiple unrelated commits, first fetch and check whether any earlier PRs have already merged into `main` (`git fetch origin && git log origin/main..HEAD`) — the branch may look clean once main is up to date. Only if genuinely unrelated commits remain should you create a separate PR for each by cherry-picking onto a fresh branch from `main`.

When asked to "automerge": fetch origin, check `git log origin/main..HEAD` and open PRs (`gh pr list`) to understand the current state. If the commit implements an OpenSpec change, archive it first (`/opsx:archive`) and amend the commit to include the archived change. Then create a PR for the latest commit and enable automerge (`gh pr merge --auto --rebase`).

## Commands

```bash
python main.py                              # run the script
python -m pytest                            # run all tests
python -m pytest tests/test_foo.py::test_bar  # single test
ruff check .                                # lint
ruff format .                               # format
mypy spotify_playlist_creator tests         # type-check (strict)
pre-commit run --all-files                  # run all hooks against every file
```

One-time setup: `pre-commit install` (activates hooks so `git commit` triggers them automatically).

## Architecture

Single entry-point script backed by one package:

- `main.py` — entry point; imports and calls `run()`
- `spotify_playlist_creator/__init__.py` — exposes `run()`, the top-level orchestration function
- `tests/` — pytest test suite (`python -m pytest`)

All tool configuration (ruff, mypy, pytest) lives in `pyproject.toml`. Pre-commit hooks run ruff and mypy on every commit; GitHub Actions CI runs the same hooks plus pytest on every push and PR.
