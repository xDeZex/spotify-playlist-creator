### Requirement: run() orchestrates a full sync
`run()` SHALL accept an optional `limit: int | None = None` parameter and an optional `dry_run: bool = False` parameter. It SHALL fetch the user's saved albums, derive the artist list, apply the Artist Limit by slicing `artists[:limit]` (no-op when `limit` is `None`), fetch each artist's releases, and classify them. When `dry_run=False`, it SHALL call the execute step to create missing Album Playlists and call `prompt_for_folder` for each artist that had new playlists created; artists with no new playlists SHALL be skipped silently. When `dry_run=True`, it SHALL call the planning step only (no writes), then call `report_dry_sync_artist` for every artist regardless of whether albums would be created. `run()` SHALL emit status output via the `status` module throughout execution, and SHALL clear the status line before returning.

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

### Requirement: run() initialises status reporting and clears on exit
At entry, `run()` SHALL call `status.set()` with a function that writes `\r\033[2K{msg}` to stdout and flushes. At exit (including after all artists are processed), `run()` SHALL call `status.clear()`.

#### Scenario: Status line is cleared after a normal run
- **WHEN** `run()` completes successfully
- **THEN** `status.clear()` has been called and the terminal line is blank

#### Scenario: Status is set before any sub-function is called
- **WHEN** `run()` is entered
- **THEN** `status.set(...)` is called before `fetch_saved_albums` is invoked

#### Scenario: (no external I/O contract)

### Requirement: run() emits per-artist status context
Before processing each artist, `run()` SHALL call `status.set_context(f"[{i}/{n}] {artist.name}")` where `i` is the 1-based index and `n` is the total number of artists in scope (after the Artist Limit is applied).

#### Scenario: Context reflects post-limit artist count
- **WHEN** 87 artists are derived but `limit=10`
- **THEN** the context strings read `[1/10]`, `[2/10]`, … `[10/10]`

#### Scenario: No limit — context uses full artist count
- **WHEN** `limit=None` and 5 artists are derived
- **THEN** the context strings read `[1/5]` through `[5/5]`

#### Scenario: (no external I/O contract)

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

### Requirement: prompt_for_folder is called only for artists with new playlists
`prompt_for_folder` SHALL be called once per artist that had at least one Album Playlist created in this sync. It SHALL NOT be called for artists whose albums all already existed.

#### Scenario: Mixed — one artist with new albums, one without
- **WHEN** Artist A has one new album and Artist B has no new albums
- **THEN** `prompt_for_folder` is called exactly once (for Artist A only)

#### Scenario: All albums already exist
- **WHEN** every album for every artist already has an Album Playlist
- **THEN** `prompt_for_folder` is never called

#### Scenario: (no external I/O contract — prompt_for_folder is local output only)

### Requirement: Existing playlists snapshot is taken once before the artist loop
The user's existing playlists SHALL be fetched once before iterating over artists, and the same snapshot SHALL be passed to `create_album_playlists` for every artist.

#### Scenario: Snapshot used for all artists
- **WHEN** two artists are processed in sequence
- **THEN** `fetch_user_playlists` is called exactly once, not once per artist

#### Scenario: Empty existing playlists
- **WHEN** the user has no existing playlists
- **THEN** `fetch_user_playlists` returns `{}` and `create_album_playlists` receives `{}`

#### Scenario: Correct token forwarded to fetch_user_playlists
- **WHEN** `run()` is called
- **THEN** the token from `authenticate()` is passed to `fetch_user_playlists`

### Requirement: Artist with no qualifying releases is skipped silently
If `classify_releases` returns an empty list for an artist, `run()` SHALL call `create_album_playlists` with an empty album list, and since no playlists are created, `prompt_for_folder` SHALL NOT be called for that artist.

#### Scenario: Artist has only singles
- **WHEN** an artist's releases are all singles that do not qualify as EPs
- **THEN** `classify_releases` returns `[]`, `create_album_playlists` returns `[]`, and `prompt_for_folder` is not called

#### Scenario: Artist with no releases at all
- **WHEN** `fetch_artist_releases` returns `[]` for an artist
- **THEN** `classify_releases` receives `[]`, returns `[]`, and `prompt_for_folder` is not called

#### Scenario: (no external I/O contract — classification is already tested in its own module)
