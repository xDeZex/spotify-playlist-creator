## Context

The project has no automated quality enforcement. All code (including AI-generated commits) enters git history unchecked. The codebase is currently empty scaffolding, making this the ideal time to add strict quality gates — zero retrofitting cost.

## Goals / Non-Goals

**Goals:**
- Block commits that fail lint, format, or type checks locally
- Block merges that fail any check or break tests remotely
- Keep all configuration in git with a single source of truth

**Non-Goals:**
- Security scanning (low signal for this codebase type)
- Coverage enforcement (too early in the project lifecycle)
- Multi-machine hook distribution (single developer)

## Decisions

### pre-commit framework over raw shell hooks

Raw `.git/hooks/` scripts are not tracked by git. Alternatives: symlink a tracked script into `.git/hooks/`, or use the `pre-commit` framework.

The `pre-commit` framework stores everything in `.pre-commit-config.yaml` (tracked), pins hook versions, and requires only `pre-commit install` once. The one-time install cost is negligible vs. the maintenance simplicity. **Decision: use pre-commit framework.**

### ruff over black + flake8 + isort

Three tools vs. one. Ruff covers formatting, linting, and import sorting in a single fast binary with one config block in `pyproject.toml`. **Decision: ruff only.**

### mypy --strict from day one

Applying strict mode to an existing codebase creates a large backlog of type errors. Applied to an empty codebase, it costs nothing and ensures all future code is fully typed. **Decision: strict = true in pyproject.toml.**

### CI reuses pre-commit config via `pre-commit run --all-files`

Duplicating check definitions in the CI workflow creates drift — the local hook and CI could diverge silently. Running `pre-commit run --all-files` in CI means the workflow always enforces exactly the same checks as the local hook. **Decision: CI delegates to pre-commit, not separate tool invocations.**

### pytest runs in CI only, not as a pre-commit hook

Tests may require network, fixtures, or take seconds to minutes. Pre-commit hooks must be fast enough not to interrupt the commit flow. **Decision: pytest in CI only.**

## Risks / Trade-offs

- **pre-commit install is manual** → Document in CLAUDE.md. Not a real risk on a single-developer project.
- **mypy strict may need per-file ignores for third-party stubs** → Accept as-needed; `# type: ignore[import-untyped]` on stub-less dependencies is standard.
- **Hook version pinning requires periodic bumps** → `pre-commit autoupdate` handles this; low maintenance burden.

## Migration Plan

1. Add dev dependencies to `pyproject.toml`
2. Add ruff and mypy config to `pyproject.toml`
3. Create `.pre-commit-config.yaml`
4. Create `.github/workflows/ci.yml`
5. Run `pre-commit install` locally
6. Run `pre-commit run --all-files` to verify existing code passes

No rollback strategy needed — all changes are additive config files.
