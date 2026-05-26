## 1. Artist model

- [x] 1.1 `Artist` dataclass exists in `models.py` with `id: str` and `name: str`
- [x] 1.2 `SavedAlbum` dataclass moved to `models.py` with `artists: list[Artist]` and `added_at: datetime` replacing `artist_names: list[str]`

## 2. Fetch saved albums

- [x] 2.1 `fetch_saved_albums()` populates `SavedAlbum.artists` from Spotify's artist array
- [x] 2.2 `fetch_saved_albums()` populates `SavedAlbum.added_at` from the `added_at` field in the API response

## 3. Derive artist list

- [x] 3.1 `derive_artists([])` returns an empty list
- [x] 3.2 `derive_artists()` returns only the primary artist (`artists[0]`) from each album
- [x] 3.3 `derive_artists()` deduplicates artists by Spotify ID
- [x] 3.4 `derive_artists()` orders artists by oldest `added_at` first
- [x] 3.5 An artist with multiple saved albums is ordered by their earliest `added_at`
