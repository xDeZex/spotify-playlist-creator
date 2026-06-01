## Why

`create_album_playlists` takes a `user_id: str` parameter solely to build the `POST /users/{user_id}/playlists` URL. Spotify exposes an equivalent endpoint — `POST /me/playlists` — that creates a playlist for the authenticated user without requiring a user ID. Removing `user_id` eliminates an unnecessary parameter and aligns playlist creation with how playlist fetching (`fetch_user_playlists`) already works.

## What Changes

- Replace `POST /v1/users/{user_id}/playlists` with `POST /v1/me/playlists` in `create_playlists.py`
- Remove the `user_id: str` parameter from `create_album_playlists`
- Remove corresponding test fixture `_USER_ID` and update all test call sites

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
<!-- none — the behavioral requirements for create-album-playlists are unchanged; this is a pure implementation swap -->

## Impact

- `spotify_playlist_creator/create_playlists.py`: signature and URL change in `create_album_playlists`
- `tests/test_create_playlists.py`: ~15 call sites and one unused fixture
