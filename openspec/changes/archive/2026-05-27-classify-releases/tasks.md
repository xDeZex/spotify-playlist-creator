## 1. Album model

- [x] 1.1 `Album` dataclass exists in `models.py` with `id`, `name`, and `release_date` fields and is frozen

## 2. Fetch track durations

- [x] 2.1 `fetch_album_tracks` raises `ValueError` for an empty token without making any HTTP request
- [x] 2.2 `fetch_album_tracks` calls `GET /albums/{id}/tracks` with an `Authorization: Bearer` header
- [x] 2.3 `fetch_album_tracks` returns a flat list of `duration_ms` integers for a single-page response
- [x] 2.4 `fetch_album_tracks` follows pagination and combines durations across all pages

## 3. EP classification logic

- [x] 3.1 A release with 4–6 tracks and total duration ≤ 30 min is classified as an EP
- [x] 3.2 A release with 4–6 tracks and total duration > 30 min is not classified as an EP
- [x] 3.3 A release with 1–3 tracks where one exceeds 10 min and total exceeds 30 min is classified as an EP
- [x] 3.4 A release with 1–3 tracks where no track exceeds 10 min is not classified as an EP
- [x] 3.5 A release with 7 or more tracks is not classified as an EP (it is an album by track count alone)

## 4. classify_releases orchestration

- [x] 4.1 A `RawRelease` with `album_type: "album"` is included as an `Album` with no track fetch
- [x] 4.2 A `RawRelease` with `album_type: "single"` that meets EP rules is included as an `Album`
- [x] 4.3 A `RawRelease` with `album_type: "single"` that does not meet EP rules is excluded
- [x] 4.4 A `RawRelease` with `album_type: "compilation"` is excluded with no track fetch
- [x] 4.5 An empty input list returns an empty list
- [x] 4.6 Output `Album` objects preserve `id`, `name`, and `release_date` from their source `RawRelease`
- [x] 4.7 Output order matches the relative order of qualifying releases in the input
