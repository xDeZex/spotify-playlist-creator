## Why

The script's `run()` entry point only authenticates — all the capabilities built to date (fetch saved albums, derive artists, classify releases, create playlists, prompt for folders) are dead code from the user's perspective. Wiring them together completes the product's core loop.

## What Changes

- `run()` in `spotify_playlist_creator/__init__.py` is extended to orchestrate the full sync flow
- A new `test_run.py` test module is added covering the orchestration logic at the function boundary

## Capabilities

### New Capabilities

- `sync-loop`: Orchestrates the full sync: fetch saved albums → derive artists → for each artist fetch releases, classify, create missing Album Playlists, prompt for folder placement

### Modified Capabilities

## Impact

- `spotify_playlist_creator/__init__.py` — `run()` body changes; new imports added
- `tests/test_run.py` — new test file
