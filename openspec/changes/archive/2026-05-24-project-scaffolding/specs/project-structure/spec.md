## ADDED Requirements

### Requirement: Top-level entry point exists
The project SHALL have a `main.py` at the repository root that serves as the runnable entry point (`python main.py`).

#### Scenario: Entry point is present
- **WHEN** a developer clones the repo
- **THEN** `main.py` exists at the root and is runnable with `python main.py`

### Requirement: Package directory exists
The project SHALL have a `spotify_playlist_creator/` package directory with an `__init__.py`, making it importable as a Python package.

#### Scenario: Package is importable
- **WHEN** the project is installed or the root is on the Python path
- **THEN** `import spotify_playlist_creator` succeeds without errors

### Requirement: Gitignore covers sensitive and generated files
The project SHALL have a `.gitignore` that excludes `.env`, token/cache files (e.g., `.cache`, `*.token`), `__pycache__/`, `.pytest_cache/`, and common virtualenv directories (`venv/`, `.venv/`, `env/`).

#### Scenario: .env is not tracked
- **WHEN** a `.env` file exists at the root
- **THEN** `git status` does not show it as an untracked or modified file

#### Scenario: Python bytecode is not tracked
- **WHEN** `__pycache__` directories are generated
- **THEN** `git status` does not show them
