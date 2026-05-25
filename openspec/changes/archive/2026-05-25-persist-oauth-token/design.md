## Context

`authenticate()` in `auth.py` currently always runs the full browser OAuth flow — every invocation opens a browser tab and waits for the user to approve access. Spotify's token endpoint returns a `refresh_token` alongside the access token, which allows silent renewal without user interaction. The existing `SpotifyToken` dataclass discards both the refresh token and the expiry information, making persistence impossible without a redesign.

## Goals / Non-Goals

**Goals:**
- Eliminate repeated browser prompts on consecutive runs.
- Silently refresh expired tokens using the stored refresh token.
- Fall back to the browser flow gracefully when the cache is absent, corrupt, or the refresh is rejected.
- Keep the implementation within the standard library (no new dependencies).

**Non-Goals:**
- Encrypting the token file — `.gitignore` is the only protection mechanism here; file-system permissions are the user's responsibility.
- Supporting multiple Spotify accounts or token-file locations configurable at runtime.
- Cross-platform keychain integration.

## Decisions

### Extend `SpotifyToken` with `refresh_token` and `expires_at`

`SpotifyToken` becomes a four-field frozen dataclass: `access_token`, `token_type`, `refresh_token`, and `expires_at` (a `float` UTC timestamp from `time.time() + expires_in`). A `float` timestamp is chosen over `datetime` to avoid timezone complexity and because `time.time()` comparisons are trivially correct.

*Alternative considered*: store raw `expires_in` seconds and record a `fetched_at` timestamp separately. Rejected — combining them at parse time removes the two-field mental overhead everywhere else.

### Token file is `.spotify_token.json` in the working directory

The file path is a module-level constant (`_TOKEN_PATH`). JSON is used because the token payload is already JSON from Spotify; no serialization library is needed. The file is written atomically via `pathlib.Path.write_text` (a single call — no partial writes on common platforms).

*Alternative considered*: use `~/.config/spotify-playlist-creator/token.json` (XDG-style). Rejected — this is a single-project script run from its own directory; working-directory placement is simpler and matches where `.env` files would live.

### Expiry check uses a 60-second buffer

A token is considered expired when `time.time() >= token.expires_at - 60`. The 60-second margin prevents using a token that expires while a downstream API call is in flight.

### Silent refresh failure silently falls through to the browser flow

If the refresh grant fails (network error, revoked token), `authenticate()` logs a brief message and re-runs the full browser flow rather than propagating the error. Rationale: the user can always fix the situation by re-authenticating; a hard crash on a revoked token would be confusing.

### `_save_token` / `_load_token` are module-private helpers; `authenticate()` orchestrates

No new public surface area. The persistence logic is encapsulated in two small private functions: `_save_token(token)` and `_load_token() -> SpotifyToken | None`. `authenticate()` calls them in the sequence: load → check expiry → maybe refresh → maybe browser flow → save.

## Risks / Trade-offs

- **Token file readable by other local users** → the file lives in the project directory; on shared machines this is a credential exposure risk. Mitigation: document in README that the file should have restrictive permissions; this is consistent with how `.env` files are typically handled.
- **Clock skew** → if the system clock is significantly wrong, the expiry buffer may not help. Mitigation: the 60-second buffer covers typical skew; no further mitigation planned.
- **Corrupt cache causes silent fallback** → a user who accidentally corrupts `.spotify_token.json` will be prompted to re-authenticate without explanation. Mitigation: acceptable UX for a CLI tool; the behavior is a recoverable no-op.
