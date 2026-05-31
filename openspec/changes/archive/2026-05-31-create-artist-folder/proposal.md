## Why

With artists discovered and their Albums classified, the script needs to create Album Playlists and surface them for the user to organise into Artist Folders. Spotify's public API has no endpoint for creating playlist folders, and the only alternative (the undocumented spclient internal API) is fragile and likely violates Spotify's ToS — so folder placement is done manually by the user.

## What Changes

- Given an artist and their list of Albums, create a Spotify playlist for each Album that does not already exist
- Each newly created playlist is immediately populated with all tracks from the corresponding Album
- Album Playlists are created in descending release-date order so the earliest album ends up at the top of the Spotify library, ready to be dragged into the folder first
- After creating playlists for an artist, print the artist name and the newly created playlist names, then pause and wait for the user to create the Artist Folder in Spotify and place the playlists inside it
- If no new playlists were created for an artist (all Albums already have playlists), skip silently — no pause, no prompt

## Capabilities

### New Capabilities

- `create-album-playlists`: Create missing Album Playlists for an artist via the Spotify API, in descending release-date order, and populate each with all tracks from the corresponding Album
- `folder-prompt`: After creating playlists for an artist, print a summary and pause for the user to create the Artist Folder and place the playlists inside it

### Modified Capabilities

_(none)_

## Impact

- New module(s) under `spotify_playlist_creator/` for playlist creation and the interactive prompt
- Requires `playlist-modify-public` or `playlist-modify-private` OAuth scope
- Calls `POST /v1/users/{user_id}/playlists` (create) — one request per missing Album Playlist
- Calls `GET /v1/albums/{album_id}/tracks` (paginated) — one request-chain per newly created playlist
- Calls `POST /v1/playlists/{playlist_id}/tracks` (add tracks) — one request per 100 tracks, per newly created playlist
- No new external dependencies; continues using `urllib.request`
