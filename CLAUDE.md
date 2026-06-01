# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A script that reads a user's Saved Albums and organizes them inside Spotify — creating one Artist Folder per artist, each containing one Album Playlist per Release. See `CONTEXT.md` for the full domain vocabulary.

## General rules

Never `git push` unless explicitly told to.

When starting brand-new work — a new OpenSpec change or any fresh implementation — create a new branch with a fitting name (`git checkout -b <name>`), then run `git fetch origin && git rebase origin/main` to ensure it is up to date with main. For continuing work on an existing branch, just rebase.

### Commit and review workflow

Each OpenSpec task produces one commit, called `task X.Y: <short description>`. After each task commit, run the `code-review` skill, fix any findings in a single `fix: review finding — <short description>` commit, then move on. Fix commits at this stage do not trigger another review.

Any other `code-review` run — end of OpenSpec, user-triggered, or ad-hoc — uses the full branch diff (`git diff origin/main`) and loops: review → fix (`fix: review finding`) → review again, until no inline-fixable findings remain. Filed-only findings do not keep the loop running.

Each PR must have exactly one commit and must target `main`. Before creating a PR, confirm with the user that they want to squash, then squash all commits into one: `git reset --soft origin/main`, recommit with the final message. If the branch contains multiple unrelated commits, first fetch and check whether any earlier PRs have already merged into `main` (`git fetch origin && git log origin/main..HEAD`) — the branch may look clean once main is up to date. Only if genuinely unrelated commits remain should you create a separate PR for each by cherry-picking onto a fresh branch from `main`.

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
