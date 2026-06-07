## Why

Album Playlists are currently created newest-first, so the oldest album ends up at the top of Spotify's "recently added" view — the reverse of what users expect. The folder prompt fires after creation, which means the Artist Folder doesn't exist yet when the playlists appear in the library, making drag-and-drop organisation awkward.

## What Changes

- Album Playlists are created oldest-release-date first so the newest album lands at the top of "recently added" (see ADR-0011)
- The folder prompt moves to before playlist creation so the user can position the Artist Folder before playlists appear (see ADR-0012)
- The prompt for each subsequent artist also lists the previous artist's new playlists (newest-first) so the user knows what to drag in before continuing
- After the final artist, the script prints the last batch and exits without blocking

## Capabilities

### New Capabilities

_(none — this change modifies existing capabilities only)_

### Modified Capabilities

- `create-album-playlists`: sort order changes from descending (newest first) to ascending (oldest first)
- `folder-prompt`: prompt moves to pre-creation; gains two-part content (previous batch + next artist); last-artist variant is non-blocking
- `sync-loop`: orchestration changes so `prompt_for_folder` is called before `create_album_playlists`, not after; first artist and last artist each have distinct prompt behaviour

## Impact

- `spotify_playlist_creator/create_playlists.py` — sort direction in `find_missing_album_playlists`
- `spotify_playlist_creator/folder_prompt.py` — prompt content and blocking behaviour
- `spotify_playlist_creator/__init__.py` — call order of `prompt_for_folder` and `create_album_playlists`; first/last artist handling
- Existing tests for `folder-prompt` and `sync-loop` will need updating
