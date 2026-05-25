## MODIFIED Requirements

### Requirement: Script exchanges authorization code for access token
After receiving the authorization code, the script SHALL send a token exchange request to the Spotify token endpoint and return a typed access token object that includes the refresh token and expiry information.

#### Scenario: Successful token exchange
- **WHEN** a valid authorization code is received
- **THEN** the script POSTs to `https://accounts.spotify.com/api/token` and returns a token object containing `access_token`, `token_type`, `refresh_token`, and `expires_at` (a UTC timestamp derived from the `expires_in` seconds in the response)

#### Scenario: Token exchange fails
- **WHEN** the Spotify token endpoint returns a non-2xx response
- **THEN** the script raises an exception with the HTTP status and response body
