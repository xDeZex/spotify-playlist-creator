## Context

All Spotify API calls outside `auth.py` use bare `urllib.request.urlopen` with no error handling. `auth.py` already handles its own errors inline (token endpoint calls). The three affected modules — `saved_albums.py`, `artist_releases.py`, `create_playlists.py` — share the same request pattern: build a `Request` with a `Bearer` header, call `urlopen`, parse JSON. There are 7 such call sites across these modules.

## Goals / Non-Goals

**Goals:**
- Replace all bare `urlopen` calls in non-auth modules with a shared `api_request` helper
- Surface HTTP errors as `RuntimeError` with status code, URL path, and Spotify's error message
- Retry 429 responses up to 3 times when Spotify sends a `Retry-After` header

**Non-Goals:**
- Modifying `auth.py` (already has error handling, different error domain)
- Retry logic for non-429 errors (5xx, network timeouts)
- Exposing `api_request` as part of the public API (`__init__.py`)

## Decisions

### Single `api_request` function, not `api_get`/`api_post`

A single function with an optional `body` parameter covers both GET and POST. `urllib.request.Request` already uses the presence of `data=` to determine method, so the split is natural. Two separate functions would add a naming decision at every call site with no benefit.

### `api_request` lives in `api.py`, not inlined per module

Seven call sites across three modules share identical logic. A central helper avoids divergence and is the only place to change retry or error format policy. See ADR-0006 for the retry policy.

### `RuntimeError` not a custom exception type

This is a script, not a library. No caller needs to catch and distinguish `SpotifyAPIError` from other errors. `auth.py` uses `RuntimeError` for its own error paths; consistency matters more than a named type here.

### Error message format: `Spotify API error (STATUS /path): message`

The path identifies the endpoint without the redundant `api.spotify.com` host. The status code lets the developer look up the Spotify docs directly. Spotify's own error message is the most useful text to surface.

### 429 without `Retry-After` fails immediately

Guessing a backoff duration would mask whether the rate limit is real or a transient anomaly. If Spotify doesn't tell us how long to wait, we don't wait. See ADR-0006.

## Risks / Trade-offs

- `api_request` returns `dict[str, Any]` but `add_tracks_to_playlist` discards the response body — the return value is ignored at that call site. No risk; just a minor mismatch in usage pattern.
- All 7 call sites change in one PR. Low blast radius (the change is mechanical), but worth testing each module's error paths explicitly.
