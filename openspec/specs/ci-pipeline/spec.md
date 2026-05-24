# ci-pipeline Specification

## Purpose
TBD - created by archiving change quality-gate-pipeline. Update Purpose after archive.
## Requirements
### Requirement: CI runs on every push and pull request
The project SHALL have a GitHub Actions workflow that triggers on every push to any branch and on every pull request targeting `main`.

#### Scenario: Push triggers CI
- **WHEN** a commit is pushed to any branch
- **THEN** the GitHub Actions workflow runs automatically

#### Scenario: Pull request triggers CI
- **WHEN** a pull request is opened or updated targeting `main`
- **THEN** the GitHub Actions workflow runs automatically

### Requirement: CI runs pre-commit checks against all files
The CI workflow SHALL run `pre-commit run --all-files`, reusing the same hook definitions as the local pre-commit config.

#### Scenario: Lint or type failure fails CI
- **WHEN** any file fails a ruff or mypy check
- **THEN** the CI workflow exits non-zero and the check is marked failed on the PR

#### Scenario: All checks pass
- **WHEN** all files pass ruff and mypy
- **THEN** the pre-commit step exits 0

### Requirement: CI runs the test suite
The CI workflow SHALL run `python -m pytest` after the pre-commit step.

#### Scenario: Test failure fails CI
- **WHEN** any test fails
- **THEN** the CI workflow exits non-zero and the check is marked failed

#### Scenario: All tests pass
- **WHEN** all tests pass
- **THEN** the pytest step exits 0 and the workflow succeeds

### Requirement: CI installs dependencies before running checks
The CI workflow SHALL install all project dependencies (including dev dependencies) before running pre-commit or pytest.

#### Scenario: Dependencies are available during checks
- **WHEN** the CI workflow runs
- **THEN** `pre-commit`, `ruff`, `mypy`, and `pytest` are available in the environment
