## Why

Spotify's `genres` field on artists is deprecated and increasingly returns empty data, leaving no reliable way to know an artist's genre. The genre is useful during a Sync — it tells the user which genre folder to place the Artist Folder into.

## What Changes

- New `lastfm.py` module: reads `LASTFM_API_KEY` from the environment (hard fail at startup if missing), fetches the top genre tag for an artist from Last.fm's `artist.gettoptags` endpoint
- `run()` reads the Last.fm API key at startup and fetches genre per artist in the sync loop
- Folder prompt and final message now include the genre tag (e.g. `[j-pop]`, `[genre not found]`, or `[failed to get genre]`)
- Dry sync output now includes the genre tag on the artist name line

## Capabilities

### New Capabilities

- `lastfm-genre`: Fetch the top genre tag for a Spotify artist by name from Last.fm's `artist.gettoptags` endpoint. Reads and validates `LASTFM_API_KEY` at startup. Returns the top tag by score as a string, `None` if no tags or artist not found, or raises on HTTP/network error.

### Modified Capabilities

- `folder-prompt`: Genre (`str | None`) is now passed to both `prompt_for_folder` and `print_final_folder_message`. The artist name line includes `[{genre}]`, `[genre not found]` when `None`.
- `dry-sync`: `report_dry_sync_artist` now accepts genre (`str | None`) and includes it on the artist name line.
- `sync-loop`: `run()` reads the Last.fm API key at startup (before any network calls) and fetches genre per artist in the loop; HTTP errors are caught and displayed as `[failed to get genre]`.

## Impact

- New module: `spotify_playlist_creator/lastfm.py`
- Modified: `spotify_playlist_creator/__init__.py`, `spotify_playlist_creator/folder_prompt.py`, `spotify_playlist_creator/dry_sync.py`
- New dependency: Last.fm API (no library — plain HTTP, same pattern as existing Spotify calls)
- New env var: `LASTFM_API_KEY`
