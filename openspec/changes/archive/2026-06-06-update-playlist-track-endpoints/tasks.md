## 1. Update fetch_first_track_album_id

- [x] 1.1 `fetch_first_track_album_id` calls `GET /playlists/{id}/items?limit=1`
- [x] 1.2 `fetch_first_track_album_id` reads the album ID from `items[0]["item"]["album"]["id"]`

## 2. Update add_tracks_to_playlist

- [x] 2.1 `add_tracks_to_playlist` calls `POST /playlists/{id}/items`

## 3. Update tests

- [x] 3.1 Test mock URLs referencing `/playlists/{id}/tracks` updated to `/playlists/{id}/items`
- [x] 3.2 Test error-message patterns referencing the old endpoint updated to match new endpoint
