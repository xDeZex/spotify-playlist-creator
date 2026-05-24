## MODIFIED Requirements

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

## ADDED Requirements

### Requirement: dev dependencies include quality gate tools
The project SHALL declare `pre-commit`, `ruff`, and `mypy` as dev dependencies in `pyproject.toml` under `[project.optional-dependencies] dev`.

#### Scenario: Dev tools install with one command
- **WHEN** a developer runs `pip install -e ".[dev]"`
- **THEN** `pre-commit`, `ruff`, `mypy`, and `pytest` are all available

### Requirement: ruff is configured in pyproject.toml
The project SHALL declare ruff configuration in `pyproject.toml` under `[tool.ruff]` and `[tool.ruff.lint]`, covering line length and enabled rule sets.

#### Scenario: ruff uses project config
- **WHEN** `ruff check .` or `ruff format --check .` is run
- **THEN** ruff applies the settings from `pyproject.toml` rather than defaults

### Requirement: mypy is configured in pyproject.toml with strict mode
The project SHALL declare mypy configuration in `pyproject.toml` under `[tool.mypy]` with `strict = true`.

#### Scenario: mypy runs in strict mode
- **WHEN** `mypy .` is run
- **THEN** mypy applies strict checking, requiring full type annotations
