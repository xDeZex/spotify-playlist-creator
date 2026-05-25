## 1. SavedAlbum domain type

- [x] 1.1 `SavedAlbum` dataclass exists with `id: str`, `name: str`, and `artist_names: list[str]` fields
- [x] 1.2 `SavedAlbum` is exported from the `spotify_playlist_creator` package

## 2. Fetch saved albums function

- [x] 2.1 `fetch_saved_albums(token: str) -> list[SavedAlbum]` exists and returns an empty list when the library is empty
- [x] 2.2 Function returns all albums when results fit in a single page
- [x] 2.3 Function follows pagination and returns the full concatenated list when multiple pages exist
- [x] 2.4 Each returned `SavedAlbum` has `id`, `name`, and `artist_names` correctly populated from the API response

## 3. Token validation

- [x] 3.1 Calling `fetch_saved_albums` without a valid token raises an appropriate exception before any API call is made

## 4. Tests

- [x] 4.1 Unit test: empty library returns `[]`
- [x] 4.2 Unit test: single-page response returns correct `SavedAlbum` list
- [x] 4.3 Unit test: multi-page response returns all albums concatenated
- [x] 4.4 Unit test: missing token raises expected exception
