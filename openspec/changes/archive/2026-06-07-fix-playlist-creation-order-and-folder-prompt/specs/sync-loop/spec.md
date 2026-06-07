## MODIFIED Requirements

### Requirement: run() orchestrates a full sync
`run()` SHALL accept an optional `limit: int | None = None` parameter and an optional `dry_run: bool = False` parameter. It SHALL fetch the user's saved albums, derive the artist list, apply the Artist Limit by slicing `artists[:limit]` (no-op when `limit` is `None`), fetch each artist's releases, and classify them. When `dry_run=False`, for each artist it SHALL first call the planning step to identify missing albums; if any are missing, it SHALL call the pre-creation folder prompt before creating any playlists, then call the execute step to create them; artists with no new playlists SHALL be skipped silently. After the main loop, if any artist had new playlists created, `run()` SHALL call the final non-blocking folder message for the last such artist. When `dry_run=True`, it SHALL call the planning step only (no writes), then call `report_dry_sync_artist` for every artist regardless of whether albums would be created. `run()` SHALL emit status output via the `status` module throughout execution, and SHALL clear the status line before returning.

#### Scenario: Happy path — two artists both with new albums, no limit, normal mode
- **WHEN** the library contains saved albums by two artists, neither has existing Album Playlists, `limit=None`, and `dry_run=False`
- **THEN** `run()` calls the pre-creation folder prompt before creating playlists for each artist, creates Album Playlists for both, and calls the final non-blocking message after the last artist's playlists are created

#### Scenario: Only one artist has new albums
- **WHEN** `dry_run=False` and only one artist has new albums
- **THEN** the first-artist pre-creation prompt is shown before creation, playlists are created, and the final non-blocking message is shown after creation — no post-creation blocking occurs

#### Scenario: Dry Sync — two artists, one already up to date
- **WHEN** `dry_run=True`, one artist has new albums and one is fully up to date
- **THEN** no playlists are created and no folder prompts are shown; `report_dry_sync_artist` is called for both artists

#### Scenario: Correct token forwarded to each domain function
- **WHEN** `run()` is called after successful authentication
- **THEN** the same `SpotifyToken` returned by `authenticate()` is forwarded to every subsequent API call

### Requirement: prompt_for_folder is called before playlist creation, not after
The pre-creation folder prompt SHALL be called immediately before `create_album_playlists` for each artist with new albums. It SHALL NOT be called after playlist creation.

#### Scenario: Prompt precedes creation
- **WHEN** an artist has new albums in a normal sync
- **THEN** the pre-creation prompt is shown and blocks before any playlists are created for that artist

#### Scenario: No prompt for artists with no new albums
- **WHEN** an artist has no new albums (all Albums already have playlists)
- **THEN** neither the pre-creation prompt nor any other output is produced for that artist

#### Scenario: (no external I/O contract — prompt_for_folder is local output only)
