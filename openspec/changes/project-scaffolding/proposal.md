## Why

The project has no package configuration, dependency management, gitignore, or test infrastructure. Without this foundation, development cannot proceed reliably — dependencies are untracked, secrets could be accidentally committed, and tests have no runner configuration.

## What Changes

- Add `pyproject.toml` with project metadata and dependencies (spotipy, python-dotenv)
- Add `requirements.txt` for pip-installable dependencies
- Add `.gitignore` covering token files, `.env`, `__pycache__`, `.pytest_cache`, and virtualenv directories
- Add `pytest.ini` or `[tool.pytest.ini_options]` configuration block
- Establish basic module layout: `main.py` entry point, `spotify_playlist_creator/` package directory with `__init__.py`
- Add `tests/` directory with `__init__.py` and a placeholder test

## Capabilities

### New Capabilities

- `project-structure`: Top-level file layout, package directory, and entry point that all future modules will live under
- `dependency-management`: Declared dependencies via pyproject.toml/requirements.txt so the project is installable and reproducible
- `test-infrastructure`: pytest configuration and test directory structure enabling `python -m pytest` to run

### Modified Capabilities

## Impact

- No existing code is modified (project is currently empty)
- Affects all future development: every subsequent feature depends on this scaffold
- `.gitignore` prevents accidental commits of `.env`, token cache files, and bytecode
