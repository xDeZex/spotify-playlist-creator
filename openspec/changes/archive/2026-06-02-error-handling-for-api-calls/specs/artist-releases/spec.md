## MODIFIED Requirements

### Requirement: Fetch artist releases from Spotify
The system SHALL fetch all albums and singles for a given artist by calling `GET /artists/{id}/albums` with `include_groups=album,single` via `api_request`. Both album types are fetched because Spotify classifies EPs as `single`; downstream classification determines which are true Releases. Errors from the Spotify API surface as `RuntimeError` with a structured message (see `api-request` spec).

#### Scenario: Single page of results
- **WHEN** the Spotify API returns one page with no `next` URL
- **THEN** all items from that page are returned as `RawRelease` objects

#### Scenario: Multiple pages of results
- **WHEN** the Spotify API returns a `next` URL on the first page
- **THEN** subsequent pages are fetched until `next` is null, and all items are combined

#### Scenario: Empty discography
- **WHEN** the Spotify API returns zero items
- **THEN** an empty list is returned

#### Scenario: Authorization header sent
- **WHEN** the function is called with a valid token
- **THEN** every request includes an `Authorization: Bearer <token>` header

#### Scenario: Missing token
- **WHEN** the function is called with an empty access token
- **THEN** a `ValueError` is raised and no HTTP request is made

#### Scenario: API returns an error
- **WHEN** the Spotify API returns a 4xx or 5xx response
- **THEN** a `RuntimeError` with a structured message is raised and propagated to the caller
