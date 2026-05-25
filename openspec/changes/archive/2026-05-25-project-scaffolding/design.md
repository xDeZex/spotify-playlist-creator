# Design: Project Scaffolding

## Overview

Sets up the foundational project structure for `spotify-playlist-creator`: package layout, dependency management, test infrastructure, linting, type-checking, pre-commit hooks, and CI pipeline.

## Key Decisions

- **Single package layout** — `spotify_playlist_creator/` with `main.py` as the entry point keeps the structure simple and importable.
- **`pyproject.toml` as single config file** — ruff, mypy, pytest, and project metadata all live here; no separate config files.
- **`ruff` for lint + format** — replaces flake8/black with one tool; configured with strict rules.
- **`mypy --strict`** — enforces full type annotations across the package and tests.
- **`pre-commit`** — runs ruff and mypy on every commit so CI mirrors local checks.
- **GitHub Actions CI** — runs pre-commit hooks plus pytest on every push and PR against `main`.
