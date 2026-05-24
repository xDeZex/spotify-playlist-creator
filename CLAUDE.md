# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A script that reads a user's Spotify liked albums and creates an organized local folder structure — one folder per artist, containing all of that artist's albums.

## General rules

Never `git push` unless explicitly told to.

Before starting any work, run `git fetch origin && git rebase origin/main` to ensure the branch is up to date.

Before committing, do a quick self-review of `git diff HEAD`. Catch surface-level issues yourself so the reviewer only sees substantive ones.

**Every commit must be followed by a `code-review` skill run before anything else happens.** Do not respond to the user, start the next task, or take any other action until the review is complete and all findings are resolved.

For each reviewer finding, fix it — via amend if introduced by this commit, inline otherwise. Only file a GitHub issue when the fix is too large or too risky to do now.

Each PR must have exactly one commit and must target `main`. All fixes and follow-ups go into the same commit via `git commit --amend`.

Before pushing, if there is an active OpenSpec change: run `openspec archive <name>` (which syncs specs automatically) and include the resulting changes — archived change directory and updated `openspec/specs/` — in the commit via amend.

## Commands

```bash
python main.py                  # run the script
python -m pytest                # run all tests
python -m pytest tests/test_foo.py::test_bar  # single test
```

## Architecture

_To be filled in once the project structure is established._
