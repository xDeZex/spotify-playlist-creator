## 1. Dev dependencies and tool config

- [x] 1.1 `pyproject.toml` declares `pre-commit`, `ruff`, and `mypy` under `[project.optional-dependencies] dev`
- [x] 1.2 `pyproject.toml` has a `[tool.ruff]` section with line length and enabled rule sets
- [x] 1.3 `pyproject.toml` has a `[tool.mypy]` section with `strict = true`
- [x] 1.4 Running `pip install -e ".[dev]"` installs `pre-commit`, `ruff`, `mypy`, and `pytest`

## 2. Pre-commit hooks

- [x] 2.1 `.pre-commit-config.yaml` exists at the repository root with pinned revisions
- [x] 2.2 `ruff` (lint) and `ruff-format` (format check) hooks are configured
- [x] 2.3 `mypy` hook is configured with `--strict` flag
- [x] 2.4 `pre-commit run --all-files` exits 0 against the current codebase
- [x] 2.5 `pre-commit install` activates hooks so `git commit` triggers them automatically

## 3. GitHub Actions CI workflow

- [x] 3.1 `.github/workflows/ci.yml` exists and triggers on push and on pull_request targeting `main`
- [x] 3.2 Workflow installs Python, installs dev dependencies, and runs `pre-commit run --all-files`
- [x] 3.3 Workflow runs `python -m pytest` after the pre-commit step
- [x] 3.4 A lint or type violation in any file causes the workflow to fail
- [x] 3.5 A failing test causes the workflow to fail
