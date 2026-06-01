## Context

`create_album_playlists` currently combines two concerns in one function: identifying which Albums are missing a playlist (read-only dedup check) and creating those playlists (writes). Dry Sync needs to run the first step without the second. The existing `prompt_for_folder` handles per-artist output for normal Sync and is named around the folder-placement interaction — that concept does not exist in Dry Sync.

## Goals / Non-Goals

**Goals:**
- Add `--dry-run` flag that activates a read-only traversal
- Show a per-artist preview of what would be created, including already-up-to-date artists
- Split `create_album_playlists` into a planning step and an execute step (see ADR-0005)
- Keep `prompt_for_folder` unchanged

**Non-Goals:**
- Caching or offline mode (reads still hit the Spotify API)
- Machine-readable output (e.g. JSON)
- Partial dry run (all writes are skipped, not just some)

## Decisions

### Split `create_album_playlists` into two functions

`find_missing_album_playlists(token, albums, existing_playlists) -> list[Album]` performs the dedup check and returns the Albums that need a new playlist, sorted by descending release date. `create_album_playlists(token, new_albums) -> list[CreatedPlaylist]` takes that pre-filtered list and executes the writes.

`run()` calls both in sequence for normal Sync; only `find_missing_album_playlists` for Dry Sync. This is cleaner than threading a `dry_run: bool` flag through the existing function, which would entangle the dedup and write logic. See ADR-0005.

### New module `dry_sync.py` for `report_dry_sync_artist`

`report_dry_sync_artist` is parallel in shape to `prompt_for_folder` but its concern (printing a preview) is distinct from the folder-placement interaction. A separate module keeps the boundary clear and avoids adding a mode flag to `prompt_for_folder`.

### `run()` signature: `dry_run: bool = False` added alongside existing `limit`

`argparse` in `main.py` maps `--dry-run` to `dry_run=True`. Both parameters are orthogonal and can be combined freely (e.g. `--dry-run --limit 3`).

## Risks / Trade-offs

- **Dry Sync consumes read quota** — it still calls `fetch_user_playlists`, `fetch_artist_releases`, `classify_releases`, and `fetch_first_track_album_id` for every artist. For large libraries this is the same API load as a normal Sync read pass. Acceptable given the goal is accuracy, not zero API calls.
- **Snapshot staleness** — the existing-playlists snapshot is taken once at the start of the loop (unchanged behaviour). A playlist created mid-run by another client won't be visible. This is a pre-existing limitation, not introduced by this change.
