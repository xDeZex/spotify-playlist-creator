# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A script that reads a user's Saved Albums and organizes them inside Spotify — creating one Artist Folder per artist, each containing one Album Playlist per Release. See `CONTEXT.md` for the full domain vocabulary.

## General rules

Never `git push` unless explicitly told to.

After every commit, run `git status` and check for leftover uncommitted changes. If any exist, warn the user and ask whether they should be included before proceeding.

Before running `/opsx:explore`, `/opsx:propose`, or `/opsx:apply` — or starting any other fresh implementation — create a new branch (`git checkout -b <name>`), then run `git fetch origin && git rebase origin/main` to ensure it is up to date with main. For continuing work on an existing branch, just rebase. Never explore, propose, or apply on `main`.

### Commit and review workflow

OpenSpec apply commits are marked `[temporary]` in their message. These are expected to be squashed before a PR.

Each PR must have exactly one commit and must target `main`. Before creating a PR, confirm with the user that they want to squash, then squash all commits into one: `git reset --soft origin/main`, recommit with the final message. If the branch contains multiple unrelated commits, first fetch and check whether any earlier PRs have already merged into `main` (`git fetch origin && git log origin/main..HEAD`) — the branch may look clean once main is up to date. Only if genuinely unrelated commits remain should you create a separate PR for each by cherry-picking onto a fresh branch from `main`.

When asked to "automerge": fetch origin, check `git log origin/main..HEAD` and open PRs (`gh pr list`) to understand the current state. If the branch contains an OpenSpec change, ensure it has been archived before squashing. Then create a PR for the latest commit and enable automerge (`gh pr merge --auto --rebase`).

## Spotify API

Always consult the official Spotify Web API reference at https://developer.spotify.com/documentation/web-api/reference/ before making any decisions about API behaviour — endpoint parameters, response shape, pagination limits, batch sizes, rate limits, or anything else. Do not infer from existing code or general knowledge; the docs are authoritative.

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
