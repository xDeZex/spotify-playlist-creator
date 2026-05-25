## Why

The script needs to authenticate with Spotify before it can read a user's library or modify their playlists. There is currently no auth mechanism — without one, no real work can happen, making this the most fundamental unblocked task.

## What Changes

- New auth module that opens the Spotify authorization page in the user's default browser
- Temporary local HTTP server listens for the OAuth callback and captures the authorization code
- Authorization code is exchanged for an access token (no manual copy-paste)
- Token is available to the rest of the script as a typed credential object

## Capabilities

### New Capabilities

- `spotify-auth`: Browser-based OAuth 2.0 Authorization Code flow — opens browser, starts local callback server, captures auth code, exchanges it for an access token

### Modified Capabilities

<!-- No existing spec-level requirements are changing -->

## Impact

- New module `spotify_playlist_creator/auth.py` (and matching test file)
- `main.py` / `run()` gains an auth step before any Spotify API calls
- No new third-party dependencies — uses Python stdlib (`http.server`, `webbrowser`, `urllib`, `secrets`)
- Requires `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` env vars (and a registered redirect URI pointing to `localhost`)
