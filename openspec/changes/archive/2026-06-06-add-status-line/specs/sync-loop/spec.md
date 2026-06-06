## MODIFIED Requirements

### Requirement: run() orchestrates a full sync
`run()` SHALL accept an optional `limit: int | None = None` parameter and an optional `dry_run: bool = False` parameter. It SHALL fetch the user's saved albums, derive the artist list, apply the Artist Limit by slicing `artists[:limit]` (no-op when `limit` is `None`), fetch each artist's releases, and classify them. When `dry_run=False`, it SHALL call the execute step to create missing Album Playlists and call `prompt_for_folder` for each artist that had new playlists created; artists with no new playlists SHALL be skipped silently. When `dry_run=True`, it SHALL call the planning step only (no writes), then call `report_dry_sync_artist` for every artist regardless of whether albums would be created. `run()` SHALL emit status output via the `status` module throughout execution, and SHALL clear the status line before returning.

#### Scenario: Happy path — two artists both with new albums, no limit, normal mode
- **WHEN** the library contains saved albums by two artists, neither has existing Album Playlists, `limit=None`, and `dry_run=False`
- **THEN** `run()` creates Album Playlists for both artists and calls `prompt_for_folder` for both

#### Scenario: Dry Sync — two artists, one already up to date
- **WHEN** `dry_run=True`, one artist has new albums and one is fully up to date
- **THEN** no playlists are created, and `report_dry_sync_artist` is called for both artists

#### Scenario: (no external I/O contract — output via status module)

## ADDED Requirements

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
