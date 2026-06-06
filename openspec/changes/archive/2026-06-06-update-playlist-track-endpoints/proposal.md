## Why

Spotify deprecated the `/playlists/{id}/tracks` endpoint family in February 2026; Development Mode apps now receive `403 Forbidden` on those endpoints. The two functions that call them must be migrated to `/playlists/{id}/items` so the script works again.

## What Changes

- `fetch_first_track_album_id` URL: `GET /playlists/{id}/tracks?limit=1` → `GET /playlists/{id}/items?limit=1`
- `fetch_first_track_album_id` response key: `items[0]["track"]` → `items[0]["item"]`
- `add_tracks_to_playlist` URL: `POST /playlists/{id}/tracks` → `POST /playlists/{id}/items`
- Tests referencing the old URL pattern updated to match new endpoint

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `create-album-playlists`: The first-track fingerprint scenario and the playlist populate scenario now use `/playlists/{id}/items` instead of `/playlists/{id}/tracks`, and the response field is `item` instead of `track`.

## Impact

- `spotify_playlist_creator/create_playlists.py` — two functions affected
- `tests/test_create_playlists.py` — mock URLs and error-message patterns referencing the old endpoint
