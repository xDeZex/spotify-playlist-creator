## Requirements

### Requirement: run() orchestrates a full sync
`run()` SHALL accept an optional `limit: int | None = None` parameter and an optional `dry_run: bool = False` parameter. At startup, it SHALL call `get_api_key()` to retrieve the Last.fm API key. It SHALL fetch the user's saved albums, derive the artist list, apply the Artist Limit by slicing `artists[:limit]` (no-op when `limit` is `None`), fetch each artist's releases, and classify them. For each artist, `run()` SHALL call `fetch_artist_genre(artist.name, api_key)` to retrieve the genre as a `list[str]`; if `fetch_artist_genre` raises `RuntimeError`, `run()` SHALL catch the error and use `None` as the genre value (signalling a fetch failure to display functions). When `dry_run=False`, for each artist it SHALL first call the planning step to identify missing albums; if any are missing, it SHALL call the pre-creation folder prompt (passing the genre) before creating any playlists, then call the execute step to create them; artists with no new playlists SHALL be skipped silently. After the main loop, if any artist had new playlists created, `run()` SHALL call the final non-blocking folder message for the last such artist (passing the genre). When `dry_run=True`, it SHALL call the planning step only (no writes), then call `report_dry_sync_artist` (passing the genre) for every artist regardless of whether albums would be created. `run()` SHALL emit status output via the `status` module throughout execution, and SHALL clear the status line before returning.

#### Scenario: Happy path — two artists both with new albums, no limit, normal mode
- **WHEN** the library contains saved albums by two artists, neither has existing Album Playlists, `limit=None`, and `dry_run=False`
- **THEN** `run()` fetches the genre for each artist, calls the pre-creation folder prompt (with genre) before creating playlists for each artist, creates Album Playlists for both, and calls the final non-blocking message (with genre) after the last artist's playlists are created

#### Scenario: Only one artist has new albums
- **WHEN** `dry_run=False` and only one artist has new albums
- **THEN** the genre is fetched for that artist, the first-artist pre-creation prompt (with genre) is shown before creation, playlists are created, and the final non-blocking message (with genre) is shown after creation — no post-creation blocking occurs

#### Scenario: Dry Sync — two artists, one already up to date
- **WHEN** `dry_run=True`, one artist has new albums and one is fully up to date
- **THEN** no playlists are created and no folder prompts are shown; the genre is fetched for each artist and `report_dry_sync_artist` is called for both artists with their respective genres

#### Scenario: Genre fetch raises — None passed to display functions
- **WHEN** `fetch_artist_genre` raises `RuntimeError` for an artist
- **THEN** `run()` catches the error and passes `genre=None` to `prompt_for_folder`, `print_final_folder_message`, or `report_dry_sync_artist` as appropriate, causing `[failed to get genre]` to be displayed

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

### Requirement: In Dry Sync mode, report_dry_sync_artist is called for every artist
When `dry_run=True`, `report_dry_sync_artist` SHALL be called for every artist in scope, including artists whose albums all already have playlists.

#### Scenario: All artists already up to date
- **WHEN** `dry_run=True` and every album for every artist already has an Album Playlist
- **THEN** `report_dry_sync_artist` is called once per artist with an empty album list

#### Scenario: Mixed — one artist with new albums, one without, dry mode
- **WHEN** `dry_run=True`, Artist A has one new album, Artist B has no new albums
- **THEN** `report_dry_sync_artist` is called for both Artist A and Artist B

### Requirement: Artist with no qualifying releases is skipped silently
If `classify_releases` returns an empty list for an artist, `find_missing_album_playlists` returns an empty list, and `run()` SHALL skip that artist without calling `prompt_for_folder` or `create_album_playlists`.

#### Scenario: Artist has only singles
- **WHEN** an artist's releases are all singles that do not qualify as EPs
- **THEN** `classify_releases` returns `[]` and no folder prompt or playlist creation occurs for that artist

#### Scenario: Artist with no releases at all
- **WHEN** `fetch_artist_releases` returns `[]` for an artist
- **THEN** `classify_releases` receives `[]`, returns `[]`, and no folder prompt or playlist creation occurs

### Requirement: run() initialises status reporting and clears on exit
At entry, `run()` SHALL configure `status` with a function that writes to stdout and flushes. At exit (including after all artists are processed), `run()` SHALL call `status.clear()`.

#### Scenario: Status line is cleared after a normal run
- **WHEN** `run()` completes successfully
- **THEN** `status.clear()` has been called and the terminal line is blank

#### Scenario: Status is set before any sub-function is called
- **WHEN** `run()` is entered
- **THEN** status is configured before `fetch_saved_albums` is invoked

### Requirement: run() emits per-artist status context
Before processing each artist, `run()` SHALL call `status.set_context(f"[{i}/{n}] {artist.name}")` where `i` is the 1-based index and `n` is the total number of artists in scope (after the Artist Limit is applied).

#### Scenario: Context reflects post-limit artist count
- **WHEN** 87 artists are derived but `limit=10`
- **THEN** the context strings read `[1/10]`, `[2/10]`, … `[10/10]`

#### Scenario: No limit — context uses full artist count
- **WHEN** `limit=None` and 5 artists are derived
- **THEN** the context strings read `[1/5]` through `[5/5]`
