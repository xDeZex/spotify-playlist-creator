## Why

AI-generated commits can introduce style inconsistencies, type errors, and broken behaviour that slip through without automated gates. Adding a quality pipeline now — while the codebase is empty — costs nothing to retrofit and ensures every future commit meets a consistent bar from day one.

## What Changes

- Add `pre-commit` framework with `.pre-commit-config.yaml` (stored in git) running `ruff` and `mypy --strict` as pre-commit hooks
- Add GitHub Actions CI workflow (`.github/workflows/ci.yml`) that runs `pre-commit run --all-files` and `pytest` on every push and PR
- Add `ruff` and `mypy` as dev dependencies in `pyproject.toml`
- Configure `ruff` and `mypy` in `pyproject.toml` (strict mypy, ruff as lint + formatter)

## Capabilities

### New Capabilities

- `pre-commit-hooks`: Local git hooks that block commits failing ruff lint/format or mypy type checks
- `ci-pipeline`: GitHub Actions workflow that enforces the same checks remotely and runs the test suite

### Modified Capabilities

- `test-infrastructure`: Dev dependencies expand to include `pre-commit`, `ruff`, and `mypy`

## Impact

- New files: `.pre-commit-config.yaml`, `.github/workflows/ci.yml`
- Modified files: `pyproject.toml` (dev deps + tool config)
- No application code changes
- Requires one-time `pre-commit install` on the developer's machine
- Closes issue #14
