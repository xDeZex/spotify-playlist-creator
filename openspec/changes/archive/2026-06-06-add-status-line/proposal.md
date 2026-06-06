## Why

The script runs silently — users see nothing until it finishes or crashes, and the 429 rate-limit waits are invisible. A rewriting single-line status bar gives continuous feedback without scrolling output.

## What Changes

- New `status.py` module provides a module-level callable used by all phases to write a rewriting status line via `\r\033[2K`
- `run()` sets the status function, writes per-artist context (`[i/total]` prefix), and clears the line on exit
- All paginated fetches report `(page X/N)` progress
- `classify_releases` reports per-single progress while checking EP eligibility
- `create_album_playlists` reports per-playlist creation progress
- `api_request` emits a status message while sleeping on a 429 retry (only when `Retry-After` is present)
- Bug fix: `fetch_album_tracks` in `classify_releases.py` switched from raw `urlopen` to `api_request` (was missing 429 retry logic entirely)
- Status bar is active in both live and Dry Sync mode

## Capabilities

### New Capabilities
- `status-line`: Module-level status reporting — a single rewriting terminal line driven by a callable set at the start of `run()`

### Modified Capabilities
- `sync-loop`: `run()` now emits status output; the existing requirement "run() SHALL produce no output of its own" is superseded
- `api-request`: 429 retry now emits a status message while waiting for `Retry-After` to elapse
- `album-classification`: `fetch_album_tracks` now uses `api_request`; `classify_releases` now emits per-single progress

## Impact

- New file: `spotify_playlist_creator/status.py`
- Modified: `spotify_playlist_creator/__init__.py`, `api.py`, `saved_albums.py`, `artist_releases.py`, `create_playlists.py`, `classify_releases.py`
- No new dependencies; no changes to public API or CLI interface
