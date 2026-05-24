# test-infrastructure Specification

## Purpose
TBD - created by archiving change project-scaffolding. Update Purpose after archive.
## Requirements
### Requirement: pytest runs with python -m pytest
The project SHALL be configured so that `python -m pytest` discovers and runs all tests without additional arguments.

#### Scenario: Test suite runs from repo root
- **WHEN** a developer runs `python -m pytest` from the repository root
- **THEN** pytest discovers tests and exits 0 (or reports collected test count if no tests exist)

### Requirement: Tests directory exists with placeholder
The project SHALL have a `tests/` directory containing an `__init__.py` and at least one placeholder test file (`test_placeholder.py`) with a trivially passing test.

#### Scenario: Placeholder test passes
- **WHEN** `python -m pytest` is run
- **THEN** the placeholder test is collected and passes

### Requirement: pytest configuration is declared
The project SHALL declare pytest configuration in `pyproject.toml` under `[tool.pytest.ini_options]`, setting `testpaths = ["tests"]`.

#### Scenario: pytest uses declared test path
- **WHEN** `python -m pytest` is run
- **THEN** pytest searches `tests/` as the test root, not the entire project

