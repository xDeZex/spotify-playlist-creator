## 1. Swap endpoint and remove user_id parameter

- [x] 1.1 `create_album_playlists` uses `POST /v1/me/playlists` instead of `POST /v1/users/{user_id}/playlists`
- [x] 1.2 `create_album_playlists` no longer accepts a `user_id` parameter

## 2. Update tests

- [x] 2.1 All test call sites pass `(token, albums, existing_playlists)` — no `user_id` argument
- [x] 2.2 The `_USER_ID` test fixture is removed
