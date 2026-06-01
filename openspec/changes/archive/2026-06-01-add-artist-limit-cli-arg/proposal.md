## Why

Running a full sync against a large library takes time and API calls. An Artist Limit lets the user process a predictable subset — useful for testing, incremental rollout, or rate-limit-conscious runs.

## What Changes

- `main.py` gains a `--limit N` CLI argument (argparse); values ≤0 are rejected with a CLI error
- `run()` gains an optional `limit: int | None = None` parameter
- `run()` slices `artists[:limit]` after `derive_artists()` to enforce the Artist Limit

## Capabilities

### New Capabilities

- `artist-limit`: Optional CLI argument that caps how many artists are processed in a single Sync, selecting the N artists whose albums were saved least recently

### Modified Capabilities

- `sync-loop`: `run()` signature changes to accept `limit`; slicing is applied before the per-artist loop

## Impact

- `main.py` — adds argparse, passes `limit` to `run()`
- `spotify_playlist_creator/__init__.py` — `run()` signature and body
- No new dependencies
