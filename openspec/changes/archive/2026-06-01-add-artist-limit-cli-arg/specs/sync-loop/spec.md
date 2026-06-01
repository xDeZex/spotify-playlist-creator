## MODIFIED Requirements

### Requirement: run() orchestrates a full sync
`run()` SHALL accept an optional `limit: int | None = None` parameter. It SHALL fetch the user's saved albums, derive the artist list, apply the Artist Limit by slicing `artists[:limit]` (no-op when `limit` is `None`), fetch each artist's releases, classify them, create missing Album Playlists, and call `prompt_for_folder` for each artist that had new playlists created. Artists with no new playlists SHALL be skipped silently. `run()` SHALL produce no output of its own — all user-visible output comes from `prompt_for_folder`.

#### Scenario: Happy path — two artists both with new albums, no limit
- **WHEN** the library contains saved albums by two artists, neither has existing Album Playlists, and `limit=None`
- **THEN** `run()` calls `create_album_playlists` for both artists and calls `prompt_for_folder` for both

#### Scenario: Artist Limit applied — limit fewer than total artists
- **WHEN** the library contains saved albums by five artists and `limit=2`
- **THEN** only the 2 artists whose albums were saved least recently are processed; the other 3 are not touched

#### Scenario: Correct token forwarded to each domain function
- **WHEN** `run()` is called after successful authentication
- **THEN** the same `SpotifyToken` returned by `authenticate()` is forwarded to every subsequent API call
