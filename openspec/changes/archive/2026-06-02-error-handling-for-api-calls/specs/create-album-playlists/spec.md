## ADDED Requirements

### Requirement: API errors propagate as structured RuntimeError
All HTTP calls within `create_playlists.py` SHALL be made via `api_request`. Errors from the Spotify API SHALL surface as `RuntimeError` with a structured message (see `api-request` spec) and propagate to the caller without wrapping or swallowing.

#### Scenario: API error during playlist fetch
- **WHEN** the Spotify API returns an error while fetching existing playlists
- **THEN** a `RuntimeError` with a structured message is raised and propagated

#### Scenario: API error during playlist creation
- **WHEN** the Spotify API returns an error while creating a playlist
- **THEN** a `RuntimeError` with a structured message is raised and propagated

#### Scenario: API error during track fetch or add
- **WHEN** the Spotify API returns an error while fetching album tracks or adding tracks to a playlist
- **THEN** a `RuntimeError` with a structured message is raised and propagated
