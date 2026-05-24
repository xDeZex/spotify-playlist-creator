# pre-commit-hooks Specification

## Purpose
TBD - created by archiving change quality-gate-pipeline. Update Purpose after archive.
## Requirements
### Requirement: pre-commit config is stored in git
The project SHALL contain a `.pre-commit-config.yaml` at the repository root, version-controlled alongside the code, with pinned hook revisions.

#### Scenario: Config file is tracked
- **WHEN** a developer clones the repository
- **THEN** `.pre-commit-config.yaml` is present and specifies exact hook revisions

### Requirement: ruff runs as a pre-commit hook
The pre-commit config SHALL include the `ruff` hook (lint) and `ruff-format` hook (format check) from the `astral-sh/ruff-pre-commit` repository.

#### Scenario: Lint violation blocks commit
- **WHEN** staged code contains a ruff lint violation
- **THEN** the pre-commit hook exits non-zero and the commit is aborted

#### Scenario: Format violation blocks commit
- **WHEN** staged code is not formatted according to ruff's formatter
- **THEN** the pre-commit hook exits non-zero and the commit is aborted

#### Scenario: Clean code passes
- **WHEN** staged code has no lint or format violations
- **THEN** both ruff hooks exit 0 and the commit proceeds

### Requirement: mypy runs as a pre-commit hook
The pre-commit config SHALL include a `mypy` hook configured with `--strict` mode.

#### Scenario: Type error blocks commit
- **WHEN** staged code contains a mypy type error under `--strict`
- **THEN** the mypy hook exits non-zero and the commit is aborted

#### Scenario: Type-correct code passes
- **WHEN** staged code has no mypy errors under `--strict`
- **THEN** the mypy hook exits 0 and the commit proceeds

### Requirement: hooks install with a single command
A developer SHALL be able to activate all hooks by running `pre-commit install` once in the repository root.

#### Scenario: Hooks activate after install
- **WHEN** a developer runs `pre-commit install`
- **THEN** subsequent `git commit` invocations trigger the configured hooks automatically
