## Context

The pipeline so far produces a list of artists (ordered by least-recently saved) and their qualifying Albums. This change adds the next step: creating Album Playlists in Spotify and handing off to the user for folder organisation.

Spotify's public API has no endpoint for creating or managing playlist folders. The only programmatic alternative (the undocumented spclient API) was rejected in ADR-0003. Album Playlists are created via `POST /v1/users/{user_id}/playlists`. Existing-playlist detection uses `GET /v1/me/playlists` (paginated).

## Goals / Non-Goals

**Goals:**
- Create missing Album Playlists for an artist via the official Spotify API
- Populate each newly created playlist with all tracks from the corresponding Album
- Skip playlists that already exist (additive-only, per ADR-0002)
- Prompt the user to create/update the Artist Folder when new playlists are created
- Produce no output and no blocking when nothing new was created

**Non-Goals:**
- Creating the Artist Folder programmatically
- Detecting or reordering existing folder contents
- Deduplicating across artists with the same name (out of scope for this change)

## Decisions

### Existing-playlist detection by name
Detect existing playlists by fetching the user's full playlist library (`GET /v1/me/playlists`, paginated, 50 per page) at the start of each artist's processing and matching by playlist name.

**Why name, not ID:** The script has no persistent store mapping Album IDs to playlist IDs. Name is the only available signal. Matching is case-sensitive and exact to stay consistent with Spotify's naming.

**Risk of false positives:** A user might already own a playlist named identically to an Album but unrelated. Accepted — the alternative (creating a duplicate) is worse, and the name collision is rare enough not to warrant a local state file at this stage.

### Fetch all playlists once per artist
Fetch the full playlist list once at the start of each artist's turn, collect into a `set[str]` of names, then check against it for each Album. Avoids repeated API calls during the create loop.

**Why not fetch once for the whole Sync run:** The user might create playlists between artists during a run (while responding to prompts). Fetching per artist keeps the check current.

### New module: `create_playlists.py`
Four public functions:

```
fetch_user_playlist_names(token) -> set[str]
    Fetches all playlist names from the user's library (paginated).

create_album_playlists(token, user_id, albums, existing_names) -> list[CreatedPlaylist]
    Creates playlists for Albums not in existing_names, in descending
    release-date order, and populates each with its tracks.
    Returns list of (name, id) for created playlists.

fetch_album_track_uris(token, album_id) -> list[str]
    Fetches all track URIs for an album, following pagination.

add_tracks_to_playlist(token, playlist_id, uris) -> None
    Adds track URIs to a playlist in batches of 100.
```

A `CreatedPlaylist` named-tuple or dataclass carries `name` and `id` for use by the prompt.

### Track population strategy
After creating a playlist, immediately fetch its album's track URIs via `GET /v1/albums/{album_id}/tracks` and add them via `POST /v1/playlists/{playlist_id}/tracks`.

**Batching:** The add-tracks endpoint accepts at most 100 URIs per request. `add_tracks_to_playlist` slices the URI list into chunks of 100 and sends one request per chunk. Most albums are well under this limit; double albums or large compilations may require two requests.

**Re-fetching tracks for EPs:** `classify_releases` already hits `GET /v1/albums/{album_id}/tracks` for EP candidates (to check duration), but only retains `duration_ms`. Track URIs are fetched a second time here. The duplication is accepted to keep classification and playlist creation as independent concerns — storing URIs on `Album` would couple the data model to a downstream need that classification doesn't share.

### New module: `folder_prompt.py`
One public function:

```
prompt_for_folder(artist_name, created_playlists) -> None
    If created_playlists is non-empty: prints artist name, lists playlist
    names, displays instruction, and blocks on input().
    If empty: returns immediately with no output.
```

Isolation keeps I/O out of the playlist-creation logic and makes both independently testable (creation logic tested with mock API; prompt logic tested with captured stdout and mocked input).

### OAuth scope
`playlist-modify-public` is required to create public playlists. The existing auth flow must request this scope. Private playlists would require `playlist-modify-private` instead. Public is the right default — Album Playlists are organisational, not personal/private.

### User ID acquisition
`POST /v1/users/{user_id}/playlists` requires the current user's Spotify user ID. This is fetched once via `GET /v1/me` and passed through to the creation function.

## Risks / Trade-offs

**Name collision (false positive skip)** → Accepted. Rare, and the alternative (duplicate playlists) is more disruptive to the user's library.

**Playlist name collision between artists** → Out of scope. Two artists can have albums with the same name; the existing-names set is scoped per artist call, so this is unlikely to cause cross-artist skips in practice.

**Prompt is blocking** → Intentional. The user must act before the script continues, ensuring playlists are in place before the next artist's playlists are created (which would otherwise all pile up at the top of the library together).

**`input()` cannot be tested without mocking** → Mitigated by isolating prompt logic in `folder_prompt.py`. Tests mock `builtins.input`.

**Track re-fetch for EPs** → Accepted. See "Track population strategy" above.
