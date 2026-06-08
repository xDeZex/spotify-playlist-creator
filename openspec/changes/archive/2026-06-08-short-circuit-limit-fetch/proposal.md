## Why

`fetch_saved_albums` always fetches every page of the user's library before `--limit` is applied. With 750 albums across 15 pages, a `--limit 4` test run still makes 15 API calls just to discard most of the result. Since Spotify returns albums newest-first and `derive_artists` selects the N oldest artists, the albums we actually need are at the tail of the response — we can stop early as soon as N distinct primary artists have been seen.

## What Changes

- `fetch_saved_albums` gains an optional keyword argument `limit: int | None = None`
- When `limit` is set, the function fetches one probe page (to learn `total`), then paginates backwards from the last page, stopping once N distinct primary artists have been collected
- When `limit` is `None`, behaviour is unchanged (full forward fetch)
- `run()` passes `limit` through to `fetch_saved_albums`; the `derive_artists(saved_albums)[:limit]` slice in `run()` is unchanged

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `saved-albums`: the "fetch all pages" requirement changes — when `limit` is set, the function MAY stop before exhausting all pages

## Impact

- `spotify_playlist_creator/saved_albums.py` — `fetch_saved_albums` signature and pagination logic
- `spotify_playlist_creator/__init__.py` — `run()` call site passes `limit`
- `tests/test_saved_albums.py` — new test cases for limit-aware fetch
