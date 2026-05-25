# spotify-auth Specification

## Purpose
TBD - created by archiving change spotify-oauth-flow. Update Purpose after archive.
## Requirements
### Requirement: Script opens Spotify authorization URL in the browser
When auth is initiated, the script SHALL construct a Spotify authorization URL with the required parameters (client ID, redirect URI, response type, scopes, and a PKCE code challenge or state parameter) and open it in the user's default browser automatically.

#### Scenario: Browser opens on auth start
- **WHEN** `run()` starts and no valid token is present
- **THEN** the Spotify authorization URL is opened in the default browser without any manual step from the user

### Requirement: Script captures the authorization code via local callback server
The script SHALL start a temporary HTTP server on localhost that listens for the Spotify OAuth callback, extracts the authorization code from the redirect URL, and shuts down after receiving the callback.

#### Scenario: Callback received successfully
- **WHEN** the user approves access in the browser and Spotify redirects to `http://localhost:<port>/callback`
- **THEN** the local server captures the `code` query parameter and stops listening

#### Scenario: Callback contains error
- **WHEN** Spotify redirects with an `error` query parameter instead of `code`
- **THEN** the script raises an exception with a message describing the OAuth error

### Requirement: Script exchanges authorization code for access token
After receiving the authorization code, the script SHALL send a token exchange request to the Spotify token endpoint and return a typed access token object.

#### Scenario: Successful token exchange
- **WHEN** a valid authorization code is received
- **THEN** the script POSTs to `https://accounts.spotify.com/api/token` and returns a token object containing at minimum the `access_token` string and `token_type`

#### Scenario: Token exchange fails
- **WHEN** the Spotify token endpoint returns a non-2xx response
- **THEN** the script raises an exception with the HTTP status and response body

### Requirement: Auth requires no third-party dependencies
The OAuth flow SHALL be implemented using only Python standard library modules (`http.server`, `webbrowser`, `urllib`, `secrets`, `threading`). No new packages may be added to the dependency manifest.

#### Scenario: Dependency check
- **WHEN** the auth module is imported
- **THEN** no third-party packages beyond those already in `pyproject.toml` are required

### Requirement: Client credentials are read from environment variables
The script SHALL read `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` from environment variables. If either is missing, the script SHALL raise a clear error before opening the browser.

#### Scenario: Missing client ID
- **WHEN** `SPOTIFY_CLIENT_ID` is not set in the environment
- **THEN** the script raises a `ValueError` with a message naming the missing variable before any network request is made

#### Scenario: Missing client secret
- **WHEN** `SPOTIFY_CLIENT_SECRET` is not set in the environment
- **THEN** the script raises a `ValueError` with a message naming the missing variable before any network request is made

