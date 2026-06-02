## MODIFIED Requirements

### Requirement: Authenticated requests
The system SHALL use the persisted OAuth access token when calling the Spotify API and SHALL raise a clear error if no valid token is available. All HTTP calls SHALL be made via `api_request`; errors from the Spotify API surface as `RuntimeError` with a structured message (see `api-request` spec).

#### Scenario: No token present
- **WHEN** `fetch_saved_albums()` is called and no token is stored on disk
- **THEN** the function raises an exception before making any API call

#### Scenario: API returns an error
- **WHEN** the Spotify API returns a 4xx or 5xx response during album fetching
- **THEN** a `RuntimeError` with a structured message is raised and propagated to the caller

#### Scenario: Authorization header forwarded
- **WHEN** `fetch_saved_albums()` is called with a valid token
- **THEN** every request includes an `Authorization: Bearer <token>` header
