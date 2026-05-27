## ADDED Requirements

### Requirement: Album model
The system SHALL represent a classified, qualifying release as an `Album` dataclass with the following fields: `id` (Spotify album ID), `name` (display name), `release_date` (partial ISO string as returned by Spotify: `"YYYY"`, `"YYYY-MM"`, or `"YYYY-MM-DD"`). The dataclass SHALL be frozen.

#### Scenario: Fields populated from classification
- **WHEN** a `RawRelease` passes classification
- **THEN** an `Album` is constructed with `id`, `name`, and `release_date` copied directly from the `RawRelease`

### Requirement: Fetch track durations for a release
The system SHALL fetch per-track duration data for a given album ID by calling `GET /albums/{id}/tracks` with pagination, returning a flat list of `duration_ms` integers — one per track, in API order.

#### Scenario: Single page of tracks
- **WHEN** the Spotify API returns one page of tracks with no `next` URL
- **THEN** the `duration_ms` of each track is collected and returned as a list

#### Scenario: Multiple pages of tracks
- **WHEN** the Spotify API returns a `next` URL on the first page
- **THEN** subsequent pages are fetched until `next` is null and all durations are combined

#### Scenario: Authorization header sent
- **WHEN** the function is called with a valid token
- **THEN** every request includes an `Authorization: Bearer <token>` header

#### Scenario: Missing token
- **WHEN** the function is called with an empty access token
- **THEN** a `ValueError` is raised and no HTTP request is made

### Requirement: Classify a list of raw releases into Albums
The system SHALL provide a `classify_releases` function that accepts a `SpotifyToken` and a `list[RawRelease]` and returns a `list[Album]` containing only qualifying releases, in the same relative order as the input.

#### Scenario: Full album passes without fetching tracks
- **WHEN** a `RawRelease` has `album_type` of `"album"`
- **THEN** it is included as an `Album` and no track-duration fetch is performed for it

#### Scenario: Single with 4–6 tracks and short total duration qualifies as EP
- **WHEN** a `RawRelease` has `album_type` of `"single"`, the tracks endpoint returns between 4 and 6 tracks, and their total duration is 30 minutes or less
- **THEN** it is included as an `Album`

#### Scenario: Single with 1–3 tracks qualifies as EP when one track exceeds 10 minutes and total exceeds 30 minutes
- **WHEN** a `RawRelease` has `album_type` of `"single"`, the tracks endpoint returns between 1 and 3 tracks, at least one track duration exceeds 10 minutes, and the sum of all track durations exceeds 30 minutes
- **THEN** it is included as an `Album`

#### Scenario: Actual single is dropped
- **WHEN** a `RawRelease` has `album_type` of `"single"` and does not meet either EP rule
- **THEN** it is excluded from the result

#### Scenario: Compilation is dropped
- **WHEN** a `RawRelease` has `album_type` of `"compilation"`
- **THEN** it is excluded from the result and no track-duration fetch is performed for it

#### Scenario: Empty input
- **WHEN** an empty list of `RawRelease` objects is passed
- **THEN** an empty list is returned
