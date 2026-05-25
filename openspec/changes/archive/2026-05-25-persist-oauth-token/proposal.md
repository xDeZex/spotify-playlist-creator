## Why

Every run of the script forces the user to re-authenticate in the browser, even though Spotify issues refresh tokens that can silently renew access. Persisting the token to disk eliminates the friction of repeated logins for the overwhelmingly common case where credentials are still valid.

## What Changes

- `SpotifyToken` gains `refresh_token` and `expires_at` fields captured during the initial token exchange.
- A token cache file (`.spotify_token.json`, gitignored) is written after every successful auth or refresh.
- On startup, `authenticate()` loads the cached token; if valid, it returns immediately without opening the browser; if expired, it silently refreshes using the refresh token; only if no cache exists or the refresh fails does it fall back to the full browser flow.
- A new `_refresh_access_token` helper handles the refresh-token grant type against the Spotify token endpoint.

## Capabilities

### New Capabilities

- `token-persistence`: Read/write the token cache from `.spotify_token.json`; determine whether a cached token is still valid; silently refresh an expired token before falling back to the browser flow.

### Modified Capabilities

- `spotify-auth`: Token exchange must additionally capture `refresh_token` and `expires_in` from the Spotify response; `SpotifyToken` must expose these fields so the persistence layer can store and act on them.

## Impact

- `spotify_playlist_creator/auth.py` — extended `SpotifyToken` dataclass; new `_save_token`, `_load_token`, `_refresh_access_token` helpers; `authenticate()` gains pre-check logic.
- `.gitignore` — `.spotify_token.json` added.
- `tests/test_auth.py` — new test groups covering persistence read/write, expiry detection, silent refresh, and fallback to browser.
- No new third-party dependencies.
