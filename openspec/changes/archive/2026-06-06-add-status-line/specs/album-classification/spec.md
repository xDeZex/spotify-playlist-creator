## MODIFIED Requirements

### Requirement: Fetch track durations for a release
The system SHALL fetch per-track duration data for a given album ID by calling `GET /albums/{id}/tracks` via `api_request` (not raw `urlopen`), with pagination, returning a flat list of `duration_ms` integers — one per track, in API order.

#### Scenario: Single page of tracks
- **WHEN** the Spotify API returns one page of tracks with no `next` URL
- **THEN** the `duration_ms` of each track is collected and returned as a list

#### Scenario: Missing token
- **WHEN** the function is called with an empty access token
- **THEN** a `ValueError` is raised and no HTTP request is made

#### Scenario: 429 on track fetch is retried
- **WHEN** `api_request` raises a 429 retry internally while fetching tracks
- **THEN** the retry is handled by `api_request` and the caller receives the eventual successful result

## ADDED Requirements

### Requirement: classify_releases emits per-single progress
When classifying singles (releases with `album_type == "single"`), `classify_releases` SHALL call `status.write(f"classifying singles ({i}/{total})...")` before fetching track durations for each single, where `i` is the 1-based index of the current single being checked and `total` is the total number of singles in the input list.

#### Scenario: Progress written for each single
- **WHEN** a list of 3 singles is classified
- **THEN** `status.write("classifying singles (1/3)...")`, `status.write("classifying singles (2/3)...")`, and `status.write("classifying singles (3/3)...")` are each called in order

#### Scenario: No singles — no progress written
- **WHEN** the input contains only full albums and no singles
- **THEN** no `status.write` call is made by `classify_releases`

#### Scenario: (no external I/O contract — status calls are fire-and-forget)
