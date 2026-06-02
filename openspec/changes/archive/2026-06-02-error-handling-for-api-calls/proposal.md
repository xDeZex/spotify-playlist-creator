## Why

All Spotify API calls outside `auth.py` are unguarded — a failed request surfaces as a raw Python traceback with an opaque `urllib.error.HTTPError`. Developers get no useful feedback about what went wrong or why.

## What Changes

- New `spotify_playlist_creator/api.py` module with a shared `api_request` function used by all non-auth API callers
- `saved_albums.py`, `artist_releases.py`, and `create_playlists.py` replace bare `urlopen` calls with `api_request`
- Failed requests raise `RuntimeError` with a human-readable message including the HTTP status, URL path, and Spotify's error message
- 429 responses are retried up to 3 times if Spotify sends a `Retry-After` header; if the header is absent, the request fails immediately

## Capabilities

### New Capabilities

- `api-request`: Shared HTTP helper that handles auth headers, 429 retry logic, and structured error messages for all Spotify API calls

### Modified Capabilities

- `saved-albums`: Implementation now delegates HTTP to `api_request`
- `artist-releases`: Implementation now delegates HTTP to `api_request`
- `create-album-playlists`: Implementation now delegates HTTP to `api_request`

## Impact

- `spotify_playlist_creator/api.py` — new file
- `spotify_playlist_creator/saved_albums.py` — `fetch_saved_albums` uses `api_request`
- `spotify_playlist_creator/artist_releases.py` — `fetch_artist_releases` uses `api_request`
- `spotify_playlist_creator/create_playlists.py` — all five `urlopen` call sites use `api_request`
- `auth.py` — untouched (has its own error handling)
- No new dependencies
