## Why

The script needs to know which artists to process before it can create any folders or playlists. This change derives an ordered, deduplicated list of artists from the user's saved albums — the first step after fetching albums.

## What Changes

- Introduce a shared `models.py` module with the `Artist` dataclass (`id`, `name`)
- Update `SavedAlbum` to store `artists: list[Artist]` and `added_at: datetime` instead of `artist_names: list[str]`
- Add `derive_artists()` to `saved_albums.py` — takes `list[SavedAlbum]`, returns `list[Artist]` ordered oldest-saved first, deduplicated by artist ID, using the primary artist only

## Capabilities

### New Capabilities

- `artist-list`: Derive an ordered, deduplicated list of `Artist` entities from saved albums, using the primary artist of each album, keyed by Spotify artist ID

### Modified Capabilities

- `saved-albums`: `SavedAlbum` gains `artists: list[Artist]` (replaces `artist_names: list[str]`) and `added_at: datetime`; fetch function updated to populate both fields

## Impact

- New file: `spotify_playlist_creator/models.py`
- Modified: `spotify_playlist_creator/saved_albums.py`
- **BREAKING**: `SavedAlbum.artist_names` removed; callers must use `SavedAlbum.artists`
- Test updates required for `SavedAlbum` construction
