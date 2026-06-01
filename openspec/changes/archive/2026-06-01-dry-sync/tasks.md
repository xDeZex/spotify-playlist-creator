## 1. Split create_album_playlists into plan and execute steps

- [x] 1.1 `find_missing_album_playlists(token, albums, existing_playlists)` returns Albums without a matching playlist, sorted by descending release date
- [x] 1.2 `create_album_playlists(token, new_albums)` takes the pre-filtered list and creates + populates playlists, returning `list[CreatedPlaylist]`
- [x] 1.3 All existing `create_album_playlists` tests pass against the new split interface

## 2. report_dry_sync_artist

- [x] 2.1 `report_dry_sync_artist(artist_name, albums)` prints "Would create: <name>" for each album when the list is non-empty
- [x] 2.2 `report_dry_sync_artist` prints "already up to date" when the album list is empty
- [x] 2.3 `report_dry_sync_artist` never calls `input()`

## 3. run() Dry Sync mode

- [x] 3.1 `run(dry_run=True)` calls `find_missing_album_playlists` but not `create_album_playlists`
- [x] 3.2 `run(dry_run=True)` calls `report_dry_sync_artist` for every artist, including those already up to date
- [x] 3.3 `run(dry_run=False)` (default) behaviour is unchanged: calls both plan and execute steps, calls `prompt_for_folder` only for artists with new playlists

## 4. CLI --dry-run flag

- [x] 4.1 `python main.py --dry-run` calls `run(dry_run=True)`
- [x] 4.2 `python main.py` (no flag) calls `run(dry_run=False)`
- [x] 4.3 `--dry-run` and `--limit` can be combined freely
