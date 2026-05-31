## 1. Fetch user playlist names

- [x] 1.1 `fetch_user_playlist_names` returns the names of all playlists in the user's library
- [x] 1.2 `fetch_user_playlist_names` follows pagination and returns all pages
- [x] 1.3 `fetch_user_playlist_names` returns an empty set when the user has no playlists

## 2. Create missing Album Playlists

- [x] 2.1 `create_album_playlists` creates a playlist for each Album whose name is not in `existing_names`
- [x] 2.2 `create_album_playlists` processes Albums in descending release-date order
- [x] 2.3 `create_album_playlists` skips Albums whose name is already in `existing_names`
- [x] 2.4 `create_album_playlists` returns an empty list when all Albums already have playlists
- [x] 2.5 `create_album_playlists` returns an empty list when given an empty Album list
- [x] 2.6 `create_album_playlists` returns only the newly created playlists, not pre-existing ones

## 3. Folder prompt

- [x] 3.1 `prompt_for_folder` prints the artist name and all new playlist names when given a non-empty list
- [x] 3.2 `prompt_for_folder` blocks on user input when given a non-empty list
- [x] 3.3 `prompt_for_folder` produces no output and does not block when given an empty list

## 4. OAuth scope

- [x] 4.1 The auth flow requests the `playlist-modify-public` scope
- [x] 4.2 Authenticated token grants permission to create playlists (integration smoke-test)

## 5. Populate Album Playlists with tracks

- [x] 5.1 `fetch_album_track_uris` returns all track URIs for an album
- [x] 5.2 `fetch_album_track_uris` follows pagination and returns URIs from all pages
- [x] 5.3 `fetch_album_track_uris` returns an empty list when the album has no tracks
- [x] 5.4 `add_tracks_to_playlist` sends all URIs to the playlist in a single request when ≤100 tracks
- [x] 5.5 `add_tracks_to_playlist` batches into multiple requests of 100 when >100 tracks
- [x] 5.6 `create_album_playlists` populates each newly created playlist with its tracks before returning
