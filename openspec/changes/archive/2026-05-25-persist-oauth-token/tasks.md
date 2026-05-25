## 1. Extend SpotifyToken with refresh and expiry fields

- [x] 1.1 `SpotifyToken` has `refresh_token` (str) and `expires_at` (float) fields
- [x] 1.2 `_exchange_code` captures `refresh_token` and `expires_in` from the Spotify response and populates the new fields
- [x] 1.3 Existing tests that construct or assert on `SpotifyToken` pass after the dataclass change

## 2. Token persistence helpers

- [x] 2.1 `_save_token(token)` writes `.spotify_token.json` with all four token fields
- [x] 2.2 `_load_token()` returns a `SpotifyToken` when a valid `.spotify_token.json` exists
- [x] 2.3 `_load_token()` returns `None` when the file is absent, corrupt, or missing required fields

## 3. Expiry detection and silent refresh

- [x] 3.1 `authenticate()` returns a cached token directly when `expires_at` is more than 60 seconds in the future (no browser, no network call)
- [x] 3.2 `_refresh_access_token(client_id, client_secret, refresh_token)` POSTs a `refresh_token` grant and returns an updated `SpotifyToken`
- [x] 3.3 `authenticate()` calls `_refresh_access_token` when the cached token is expired and saves the result
- [x] 3.4 `authenticate()` falls through to the full browser flow when the refresh grant returns a non-2xx response

## 4. Save on successful auth

- [x] 4.1 `authenticate()` calls `_save_token` after a successful browser flow
- [x] 4.2 `authenticate()` calls `_save_token` after a successful silent refresh

## 5. Gitignore

- [x] 5.1 `.spotify_token.json` is listed in `.gitignore`
