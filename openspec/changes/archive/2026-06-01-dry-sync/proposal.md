## Why

Running the script against a real Spotify account is the only way to verify its behaviour, but every run creates playlists. A Dry Sync mode lets users inspect exactly what the script would do without making any changes to their library.

## What Changes

- Add `--dry-run` CLI flag to `main.py`
- Thread `dry_run: bool = False` into `run()`
- Split `create_album_playlists` into a read-only planning step and a write step
- Add `report_dry_sync_artist` function that prints a per-artist summary (albums that would be created, or "already up to date") without blocking on user input
- In Dry Sync mode: run the planning step only, call `report_dry_sync_artist` instead of `prompt_for_folder`

## Capabilities

### New Capabilities

- `dry-sync`: A read-only run mode that traverses the full Sync logic — fetching Saved Albums, deriving Artists, checking existing Album Playlists — but skips all writes and prints a per-artist preview instead

### Modified Capabilities

- `sync-loop`: `run()` gains a `dry_run` parameter; the sync loop branches on it to skip writes and use the dry output path
- `create-album-playlists`: Split into a dedup/planning step and a write step to support Dry Sync without a mode flag inside a single function

## Impact

- `main.py`: new `--dry-run` flag
- `spotify_playlist_creator/__init__.py`: `run()` signature change
- `spotify_playlist_creator/create_playlists.py`: function split
- New function `report_dry_sync_artist` (new module alongside `folder_prompt.py`)
