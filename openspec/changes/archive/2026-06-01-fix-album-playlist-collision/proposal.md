## Why

`create_album_playlists` detects existing playlists by name, using a flat `set[str]`. When two Albums from different artists share a name (e.g. both have a self-titled album), the second is silently skipped — it looks like it already exists when it doesn't.

## What Changes

- `fetch_user_playlist_names` is replaced by a richer function returning `dict[str, list[str]]` — a map of playlist name to all playlist IDs with that name.
- A new helper fetches the first track of a playlist and returns its Spotify Album ID.
- The collision-check logic in `create_album_playlists` is updated: on a name match, each same-named playlist is fingerprinted by its first track's Album ID. If one matches, the Album is skipped; if none match, the playlist is created. An empty playlist (no tracks) is treated as a non-match — a new playlist is created.

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `create-album-playlists`: The "matching playlist" requirement changes — a playlist matches an Album when its first track's Spotify Album ID matches the Album's ID, not when its name matches. Name equality alone is no longer sufficient.

## Impact

- `spotify_playlist_creator/create_playlists.py` — detection logic and playlist-fetching function
- `tests/test_create_playlists.py` — existing name-match scenarios updated; new collision scenarios added
