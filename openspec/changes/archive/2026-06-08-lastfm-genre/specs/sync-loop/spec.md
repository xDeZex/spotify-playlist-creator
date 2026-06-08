## MODIFIED Requirements

### Requirement: run() orchestrates a full sync
`run()` SHALL accept an optional `limit: int | None = None` parameter and an optional `dry_run: bool = False` parameter. At startup, before any network calls, it SHALL call `get_api_key()` to read `LASTFM_API_KEY` — if the key is missing, `get_api_key()` raises and `run()` propagates immediately. It SHALL fetch the user's saved albums, derive the artist list, apply the Artist Limit by slicing `artists[:limit]` (no-op when `limit` is `None`), fetch each artist's releases, and classify them. For each artist, it SHALL call `fetch_artist_genre(artist.name, api_key)` to obtain the genre; if `fetch_artist_genre` raises, `run()` SHALL catch the error and use the string `"failed to get genre"` as the genre value. When `dry_run=False`, for each artist it SHALL first call the planning step to identify missing albums; if any are missing, it SHALL call the pre-creation folder prompt (passing genre) before creating any playlists, then call the execute step to create them; artists with no new playlists SHALL be skipped silently. After the main loop, if any artist had new playlists created, `run()` SHALL call the final non-blocking folder message for the last such artist (passing genre). When `dry_run=True`, it SHALL call the planning step only (no writes), then call `report_dry_sync_artist` (passing genre) for every artist regardless of whether albums would be created. `run()` SHALL emit status output via the `status` module throughout execution, and SHALL clear the status line before returning.

#### Scenario: Happy path — genre fetched and passed to prompt
- **WHEN** the library contains saved albums by one artist, `dry_run=False`, and Last.fm returns `"j-pop"` for that artist
- **THEN** `prompt_for_folder` is called with `genre="j-pop"` before playlist creation

#### Scenario: Last.fm HTTP error — fallback string used
- **WHEN** `fetch_artist_genre` raises `RuntimeError` for an artist
- **THEN** `run()` catches the error and passes `genre="failed to get genre"` to the folder prompt or dry sync report

#### Scenario: Missing LASTFM_API_KEY — fails before any network calls
- **WHEN** `LASTFM_API_KEY` is not set and `run()` is called
- **THEN** `get_api_key()` raises before `fetch_saved_albums` is called

#### Scenario: Correct token forwarded to each domain function
- **WHEN** `run()` is called after successful authentication
- **THEN** the same `SpotifyToken` returned by `authenticate()` is forwarded to every subsequent Spotify API call
