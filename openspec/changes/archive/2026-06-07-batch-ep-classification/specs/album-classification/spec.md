## ADDED Requirements

### Requirement: Batch-fetch track durations for multiple singles
The system SHALL provide a `fetch_singles_durations(token, ids: list[str]) -> dict[str, list[int]]` function that calls `GET /v1/albums?ids=<comma-separated-ids>` via `api_request`, extracts `tracks.items[*].duration_ms` from each album object in the response, and returns a dict mapping each album ID to its list of duration_ms integers. Albums returned as `null` in the response (unavailable in the user's market) SHALL be omitted from the returned dict silently. The function accepts up to 20 IDs per call; the caller is responsible for chunking.

#### Scenario: Durations extracted for all returned albums
- **WHEN** `fetch_singles_durations` is called with a list of IDs and the API returns album objects with inline tracks
- **THEN** the returned dict maps each album ID to a list of `duration_ms` integers in API order

#### Scenario: Null album in response is skipped silently
- **WHEN** the API returns `null` at a position in the `albums` array (album unavailable in market)
- **THEN** that album ID is absent from the returned dict and no error is raised

#### Scenario: Correct URL and Authorization header sent
- **WHEN** `fetch_singles_durations` is called with IDs `["a1", "a2"]` and a valid token
- **THEN** a single request is made to `GET /v1/albums?ids=a1,a2` with `Authorization: Bearer <token>`

## MODIFIED Requirements

### Requirement: classify_releases emits per-single progress
When classifying singles (releases with `album_type == "single"`), `classify_releases` SHALL call `status.write(f"classifying singles ({n}/{total})...")` after fetching each batch of durations, where `n` is the count of singles processed so far (capped at `total`) and `total` is the total number of singles in the input list. The message SHALL be written once per batch (up to 20 singles per batch), not once per individual single.

#### Scenario: Progress written once per batch
- **WHEN** a list of 25 singles is classified (2 batches: 20 then 5)
- **THEN** `status.write("classifying singles (20/25)...")` is called after the first batch and `status.write("classifying singles (25/25)...")` is called after the second batch

#### Scenario: No singles — no progress written
- **WHEN** the input contains only full albums and no singles
- **THEN** no `status.write` call is made by `classify_releases`

#### Scenario: (no external I/O contract — status calls are fire-and-forget)

## REMOVED Requirements

### Requirement: Fetch track durations for a release
**Reason**: Replaced by `fetch_singles_durations`, which uses the batch `GET /v1/albums?ids=...` endpoint to fetch durations for up to 20 singles per call, reducing API call volume ~20×.
**Migration**: Call `fetch_singles_durations(token, ids)` with a list of album IDs (max 20); it returns a `dict[str, list[int]]` keyed by album ID.
