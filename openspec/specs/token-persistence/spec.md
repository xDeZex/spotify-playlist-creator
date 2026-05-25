# token-persistence Specification

## Purpose
TBD - created by archiving change persist-oauth-token. Update Purpose after archive.
## Requirements
### Requirement: Token is saved to disk after successful authentication or refresh
After any successful full-browser auth or silent refresh, the script SHALL serialize the token (access token, refresh token, token type, and expiry timestamp) to `.spotify_token.json` in the working directory.

#### Scenario: Token written after browser auth
- **WHEN** the full OAuth browser flow completes successfully
- **THEN** `.spotify_token.json` is created (or overwritten) with the token fields serialized as JSON

#### Scenario: Token written after silent refresh
- **WHEN** a cached token is refreshed silently using the refresh token
- **THEN** `.spotify_token.json` is updated with the new access token and expiry

### Requirement: Token is loaded from disk on startup
On each invocation, `authenticate()` SHALL attempt to load a token from `.spotify_token.json` before opening the browser.

#### Scenario: Valid cached token used directly
- **WHEN** `.spotify_token.json` exists and the `expires_at` timestamp is in the future
- **THEN** `authenticate()` returns the cached token without opening the browser and without calling the token endpoint

#### Scenario: No cache file present
- **WHEN** `.spotify_token.json` does not exist
- **THEN** `authenticate()` falls through to the full browser flow

#### Scenario: Cache file is corrupt or unreadable
- **WHEN** `.spotify_token.json` exists but cannot be parsed as valid JSON or is missing required fields
- **THEN** `authenticate()` falls through to the full browser flow without raising an error to the user

### Requirement: Expired token is silently refreshed using the refresh token
When the loaded token is expired, the script SHALL attempt a silent refresh via Spotify's token endpoint before falling back to the browser flow.

#### Scenario: Expired token successfully refreshed
- **WHEN** the cached token's `expires_at` is in the past and a `refresh_token` is present
- **THEN** `authenticate()` POSTs a refresh-token grant to `https://accounts.spotify.com/api/token` and returns a new valid token without opening the browser

#### Scenario: Refresh token rejected by Spotify
- **WHEN** the refresh token grant returns a non-2xx response
- **THEN** `authenticate()` falls through to the full browser flow

### Requirement: Token cache file is excluded from version control
The `.spotify_token.json` file SHALL be listed in `.gitignore` so that credentials are never committed.

#### Scenario: File is gitignored
- **WHEN** `.gitignore` is inspected
- **THEN** `.spotify_token.json` appears as an entry

