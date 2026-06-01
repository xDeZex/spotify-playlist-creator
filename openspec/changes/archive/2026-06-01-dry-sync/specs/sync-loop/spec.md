## MODIFIED Requirements

### Requirement: run() orchestrates a full sync
`run()` SHALL accept an optional `limit: int | None = None` parameter and an optional `dry_run: bool = False` parameter. It SHALL fetch the user's saved albums, derive the artist list, apply the Artist Limit by slicing `artists[:limit]` (no-op when `limit` is `None`), fetch each artist's releases, and classify them. When `dry_run=False`, it SHALL call the execute step to create missing Album Playlists and call `prompt_for_folder` for each artist that had new playlists created; artists with no new playlists SHALL be skipped silently. When `dry_run=True`, it SHALL call the planning step only (no writes), then call `report_dry_sync_artist` for every artist regardless of whether albums would be created. `run()` SHALL produce no output of its own — all user-visible output comes from `prompt_for_folder` (normal mode) or `report_dry_sync_artist` (Dry Sync mode).

#### Scenario: Happy path — two artists both with new albums, no limit, normal mode
- **WHEN** the library contains saved albums by two artists, neither has existing Album Playlists, `limit=None`, and `dry_run=False`
- **THEN** `run()` creates Album Playlists for both artists and calls `prompt_for_folder` for both

#### Scenario: Dry Sync — two artists, one already up to date
- **WHEN** `dry_run=True`, one artist has new albums and one is fully up to date
- **THEN** no playlists are created, and `report_dry_sync_artist` is called for both artists

#### Scenario: Artist Limit applied — limit fewer than total artists
- **WHEN** the library contains saved albums by five artists and `limit=2`
- **THEN** only the 2 artists whose albums were saved least recently are processed; the other 3 are not touched

#### Scenario: Correct token forwarded to each domain function
- **WHEN** `run()` is called after successful authentication
- **THEN** the same `SpotifyToken` returned by `authenticate()` is forwarded to every subsequent API call

## ADDED Requirements

### Requirement: In Dry Sync mode, report_dry_sync_artist is called for every artist
When `dry_run=True`, `report_dry_sync_artist` SHALL be called for every artist in scope, including artists whose albums all already have playlists.

#### Scenario: All artists already up to date
- **WHEN** `dry_run=True` and every album for every artist already has an Album Playlist
- **THEN** `report_dry_sync_artist` is called once per artist with an empty album list

#### Scenario: Mixed — one artist with new albums, one without, dry mode
- **WHEN** `dry_run=True`, Artist A has one new album, Artist B has no new albums
- **THEN** `report_dry_sync_artist` is called for both Artist A and Artist B

#### Scenario: (no external I/O contract — report_dry_sync_artist is local output only)
