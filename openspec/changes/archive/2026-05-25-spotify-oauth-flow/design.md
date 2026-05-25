## Context

The script currently has no Spotify authentication. The Spotify Web API requires an OAuth 2.0 access token for all user-scoped endpoints. This change adds the Authorization Code flow — the only Spotify-supported flow that grants access to a user's private library without requiring a backend server to store long-lived refresh tokens.

Python's standard library has everything needed: `http.server` for the callback server, `webbrowser` to open the auth URL, `urllib` for HTTP requests, and `secrets` for the state/PKCE nonce.

## Goals / Non-Goals

**Goals:**
- Implement the full Authorization Code flow (open browser → capture callback → exchange code for token)
- No new third-party dependencies
- Clear errors when env vars are missing

**Non-Goals:**
- Token persistence / refresh — tokens live for the duration of a single script run only
- PKCE — the Authorization Code flow with client secret is sufficient and simpler; PKCE is for public clients without a secret
- Multi-user or server scenarios
- Retry / backoff on network errors (handled elsewhere when API calls are added)

## Decisions

### Use a randomly selected ephemeral port (not a fixed port)
Binding to port 0 lets the OS assign a free port. The redirect URI registered in the Spotify developer dashboard must match exactly, so we register `http://localhost:8888/callback` as the fixed redirect URI and always bind to port 8888.

_Alternative_: dynamic port — cleaner but requires the user to register a wildcard or update the dashboard on each run. Fixed port is simpler to document.

### Use threading to run the callback server without blocking
`http.server.HTTPServer.serve_forever()` blocks. We run it in a `threading.Thread` with `daemon=True` so it shuts down when the main thread exits. The handler signals completion via a `threading.Event`, which the main thread waits on with a timeout.

_Alternative_: `asyncio` — would require an event loop and is heavier than needed for a one-shot server.

### State parameter for CSRF protection
We generate a random `state` string with `secrets.token_urlsafe(16)` and verify it on the callback. This prevents CSRF attacks against the local server even though the attack surface is a single-user desktop script — it costs nothing and is correct practice.

### Module boundary: `spotify_playlist_creator/auth.py`
All auth logic lives in one module exposing a single public function `authenticate() -> SpotifyToken`. `run()` in `__init__.py` calls it at startup and passes the token downstream. This keeps auth isolated and easy to stub in tests.

### `SpotifyToken` as a dataclass
A `@dataclass` with `access_token: str` and `token_type: str` is typed, lightweight, and avoids a dict with string keys throughout the codebase. Fields can be extended when refresh tokens are added later.

## Risks / Trade-offs

- **Port conflict on 8888** → The script will fail with `OSError: [Errno 98] Address already in use`. Mitigation: print a clear error message telling the user to free the port. This is a known, rare edge case for a single-user tool.
- **Browser doesn't open** → `webbrowser.open()` fails silently on headless systems. Mitigation: print the auth URL to stdout as a fallback so the user can open it manually.
- **Callback server timeout** → If the user never approves (closes tab, network error), the thread blocks until the `Event` timeout. Mitigation: set a 120-second timeout and raise a clear `TimeoutError`.
- **No token refresh** → Access tokens expire in 1 hour. Mitigation: acceptable for now; the script is expected to run in under an hour. Token persistence is deferred to a future change.
