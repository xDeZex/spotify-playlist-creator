### Requirement: Fetch artist releases from Spotify
The system SHALL fetch all albums and singles for a given artist by calling `GET /artists/{id}/albums` with `include_groups=album,single`. Both album types are fetched because Spotify classifies EPs as `single`; downstream classification determines which are true Releases.

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

### Requirement: RawRelease model
The system SHALL represent each item returned by the artist albums endpoint as a `RawRelease` dataclass with the following fields: `id` (Spotify album ID), `name` (display name), `album_type` (Spotify's classification: `"album"`, `"single"`, or `"compilation"`), `release_date` (partial ISO string as returned by Spotify: `"YYYY"`, `"YYYY-MM"`, or `"YYYY-MM-DD"`).

Note: `total_tracks` is intentionally excluded. Although the Spotify albums endpoint returns it, classification uses the actual track count from the tracks endpoint (`len(durations)`) rather than this metadata field. Carrying it on `RawRelease` would be speculative — no current logic reads it.

#### Scenario: Fields mapped from API response
- **WHEN** the API returns an album object
- **THEN** each field on `RawRelease` is populated directly from the corresponding API field with no transformation

#### Scenario: Release date preserved as string
- **WHEN** the API returns a year-only release date such as `"1997"`
- **THEN** `release_date` is stored as `"1997"` without padding or conversion

#### Scenario: Lexicographic sort order
- **WHEN** a list of `RawRelease` objects is sorted by `release_date`
- **THEN** releases appear in chronological order (year-only dates sort before more specific dates in the same year)
