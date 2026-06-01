## 1. Playlist fetching returns name-to-IDs map

- [x] 1.1 `fetch_user_playlists` returns `dict[str, list[str]]` mapping each playlist name to all its IDs
- [x] 1.2 Multiple playlists with the same name are collected in the same bucket
- [x] 1.3 Pagination fetches all playlists across multiple pages

## 2. First-track fingerprinting

- [x] 2.1 `fetch_first_track_album_id` fetches `GET /playlists/{id}/tracks?limit=1` and returns the track's `album.id`
- [x] 2.2 `fetch_first_track_album_id` returns `None` when the playlist contains no tracks

## 3. Collision-aware Album Playlist creation

- [x] 3.1 An Album with no same-named playlist is created normally
- [x] 3.2 An Album whose name matches a playlist whose first track's Album ID matches is skipped
- [x] 3.3 An Album whose name matches a playlist whose first track's Album ID does not match is created
- [x] 3.4 An Album whose name matches an empty playlist is created
- [x] 3.5 `create_album_playlists` accepts `dict[str, list[str]]` instead of `set[str]`
