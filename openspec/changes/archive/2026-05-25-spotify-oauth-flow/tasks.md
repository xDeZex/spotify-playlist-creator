## 1. SpotifyToken type and auth module skeleton

- [x] 1.1 `SpotifyToken` dataclass exists with `access_token: str` and `token_type: str` fields
- [x] 1.2 `authenticate()` function is importable from `spotify_playlist_creator.auth`
- [x] 1.3 `authenticate()` raises `ValueError` with the variable name when `SPOTIFY_CLIENT_ID` is missing
- [x] 1.4 `authenticate()` raises `ValueError` with the variable name when `SPOTIFY_CLIENT_SECRET` is missing

## 2. Browser-based authorization

- [x] 2.1 `authenticate()` opens the Spotify authorization URL in the default browser
- [x] 2.2 Authorization URL includes `client_id`, `redirect_uri`, `response_type=code`, required scopes, and a `state` nonce
- [x] 2.3 Auth URL is also printed to stdout as a fallback if the browser cannot open

## 3. Local callback server

- [x] 3.1 A local HTTP server starts on port 8888 and listens at `/callback`
- [x] 3.2 On a successful callback, the server extracts the `code` query parameter and signals completion
- [x] 3.3 On a callback containing `error`, the server raises an exception with the OAuth error message
- [x] 3.4 The state parameter in the callback is verified against the generated nonce; mismatch raises an exception
- [x] 3.5 If no callback is received within 120 seconds, `authenticate()` raises `TimeoutError`
- [x] 3.6 The server shuts down after receiving any callback (success or error)

## 4. Token exchange

- [x] 4.1 After a successful callback, the authorization code is exchanged with the Spotify token endpoint
- [x] 4.2 A successful exchange returns a `SpotifyToken` with the `access_token` and `token_type` populated
- [x] 4.3 A non-2xx response from the token endpoint raises an exception with the HTTP status and body

## 5. Integration with run()

- [x] 5.1 `run()` calls `authenticate()` before any other Spotify API calls
- [x] 5.2 The `SpotifyToken` returned by `authenticate()` is available for downstream use inside `run()`
