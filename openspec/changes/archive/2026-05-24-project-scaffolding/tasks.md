## 1. Project structure

- [x] 1.1 `main.py` exists at repo root and runs without errors with `python main.py`
- [x] 1.2 `spotify_playlist_creator/__init__.py` exists, making the directory an importable package
- [x] 1.3 `.gitignore` excludes `.env`, token/cache files, `__pycache__/`, `.pytest_cache/`, and virtualenv directories

## 2. Dependency management

- [x] 2.1 `pyproject.toml` exists with `[project]` metadata (name, version, requires-python >= 3.10, description)
- [x] 2.2 `pyproject.toml` declares runtime dependencies: `spotipy` and `python-dotenv`
- [x] 2.3 `requirements.txt` exists listing the same runtime dependencies
- [x] 2.4 `pip install -e .` completes without errors

## 3. Test infrastructure

- [x] 3.1 `pyproject.toml` includes `[tool.pytest.ini_options]` with `testpaths = ["tests"]`
- [x] 3.2 `tests/__init__.py` exists
- [x] 3.3 `tests/test_placeholder.py` contains a trivially passing test
- [x] 3.4 `python -m pytest` runs from repo root and exits 0
