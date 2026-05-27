## Why

The script knows which artists to process (from saved albums) but has no way to fetch their discographies. Fetching an artist's releases from Spotify is the next pipeline step before classification and playlist creation can happen.

## What Changes

- New `RawRelease` dataclass in `models.py` with fields: `id`, `name`, `album_type`, `total_tracks`, `release_date`
- New `fetch_artist_releases(token, artist_id)` function in a new `artist_releases.py` module
- Calls `GET /artists/{id}/albums?include_groups=album,single&limit=50`, follows pagination via `next` URL

## Capabilities

### New Capabilities

- `artist-releases`: Fetch all albums and singles for a given artist from Spotify, returning a list of raw (unclassified) release objects with enough data for downstream EP classification and release-date ordering

### Modified Capabilities

- `artist-list`: No requirement changes — `Artist` model and `derive_artists` are unchanged

## Impact

- New file: `spotify_playlist_creator/artist_releases.py`
- Modified file: `spotify_playlist_creator/models.py` (adds `RawRelease`)
- New test file: `tests/test_artist_releases.py`
- No changes to existing modules or public interfaces
