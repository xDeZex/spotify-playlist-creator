## ADDED Requirements

### Requirement: run() orchestrates a full sync
`run()` SHALL fetch the user's saved albums, derive the artist list, fetch each artist's releases, classify them, create missing Album Playlists, and call `prompt_for_folder` for each artist that had new playlists created. Artists with no new playlists SHALL be skipped silently. `run()` SHALL produce no output of its own — all user-visible output comes from `prompt_for_folder`.

#### Scenario: Happy path — two artists both with new albums
- **WHEN** the library contains saved albums by two artists, and neither artist has any existing Album Playlists
- **THEN** `run()` calls `create_album_playlists` for both artists and calls `prompt_for_folder` for both

#### Scenario: No saved albums
- **WHEN** the library is empty (`fetch_saved_albums` returns `[]`)
- **THEN** `run()` calls neither `create_album_playlists` nor `prompt_for_folder`

#### Scenario: Correct token forwarded to each domain function
- **WHEN** `run()` is called after successful authentication
- **THEN** the same `SpotifyToken` returned by `authenticate()` is forwarded to every subsequent API call

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
