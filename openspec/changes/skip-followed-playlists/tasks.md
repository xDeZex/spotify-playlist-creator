## 1. Private user-ID helper

- [x] 1.1 `_fetch_current_user_id(token)` calls `GET /me` and returns the `id` field as a string
- [x] 1.2 `_fetch_current_user_id` raises `ValueError` for an empty token without making an API call
- [x] 1.3 `_fetch_current_user_id` propagates API errors as `RuntimeError` via `api_request`

## 2. Rename and filter `fetch_user_playlists`

- [x] 2.1 `fetch_user_playlists` is renamed to `fetch_owned_playlists` everywhere (implementation + imports + tests)
- [x] 2.2 `fetch_owned_playlists` calls `_fetch_current_user_id` before paginating `/me/playlists`
- [x] 2.3 `fetch_owned_playlists` excludes any playlist item where `owner.id` differs from the current user's ID
- [x] 2.4 `fetch_owned_playlists` still collects all owned playlists across pagination pages

## 3. Test coverage — `fetch_owned_playlists`

- [x] 3.1 Followed playlists (mismatched `owner.id`) are absent from the returned map
- [x] 3.2 Owned playlists (matching `owner.id`) are present in the returned map
- [x] 3.3 Auth-header test verifies both `GET /me` and `GET /me/playlists` requests carry `Authorization: Bearer <token>`
- [x] 3.4 Empty-token guard raises `ValueError` without calling `urlopen`
- [x] 3.5 Pagination still collects all owned playlists across pages

## 4. Test coverage — `find_missing_album_playlists` and integration

- [x] 4.1 Existing `find_missing_album_playlists` tests pass unchanged (they mock `fetch_first_track_album_id` directly, so no update needed)
- [x] 4.2 `test_run.py` mock target updated from `fetch_user_playlists` to `fetch_owned_playlists`
