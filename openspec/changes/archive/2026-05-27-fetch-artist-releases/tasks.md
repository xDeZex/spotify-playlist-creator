## 1. RawRelease model

- [x] 1.1 `RawRelease` dataclass exists in `models.py` with fields `id`, `name`, `album_type`, `total_tracks`, `release_date`
- [x] 1.2 All fields map directly from the Spotify API response with no transformation
- [x] 1.3 `release_date` is stored as a string exactly as returned by the API (e.g. `"1997"`, `"2021-05"`, `"2021-05-14"`)
- [x] 1.4 A list of `RawRelease` objects sorted by `release_date` is in chronological order

## 2. fetch_artist_releases function

- [x] 2.1 `fetch_artist_releases(token, artist_id)` exists in `artist_releases.py` and returns `list[RawRelease]`
- [x] 2.2 Raises `ValueError` immediately when `token.access_token` is empty, without making any HTTP request
- [x] 2.3 Calls `GET /artists/{id}/albums?include_groups=album,single&limit=50`
- [x] 2.4 Every request includes an `Authorization: Bearer <token>` header
- [x] 2.5 Follows `next` URLs until pagination is exhausted and returns all items combined
- [x] 2.6 Returns an empty list when the API returns zero items
