## Context

`fetch_artist_releases` already returns a `list[RawRelease]` containing both `album_type: "album"` and `album_type: "single"` releases. Spotify does not expose `"ep"` as a distinct `album_type` — EPs are lumped with singles. The classification step is the bridge between raw API data and the domain concept of an Album (qualifying release). See [ADR-0001](../../docs/adr/0001-ep-classification-via-track-count-and-duration.md).

## Goals / Non-Goals

**Goals:**
- Filter a `list[RawRelease]` down to a `list[Album]` using Spotify's EP classification rules
- Add the `Album` model to `models.py`
- Keep the new module (`classify_releases.py`) consistent with the existing fetch-module pattern

**Non-Goals:**
- Batching track-duration requests across multiple releases (single-release fetches are sufficient at this scale)
- Caching track durations between runs
- Changing `fetch_artist_releases` in any way

## Decisions

### New module: `classify_releases.py`

Classification lives in its own file alongside `artist_releases.py` and `saved_albums.py`. The file contains three functions:

- `fetch_album_tracks(token, album_id) -> list[int]` — network; returns `duration_ms` per track
- `_is_ep(total_tracks, durations) -> bool` — pure logic; applies the two EP rules
- `classify_releases(token, raw_releases) -> list[Album]` — orchestrates; public entry point

Keeping network and logic in one file follows the existing pattern and keeps the surface area small. The pure `_is_ep` function is still directly unit-testable without mocking HTTP.

### Trust `album_type: "album"` directly

Releases with `album_type: "album"` are passed through as Albums without fetching track durations. The EP classification rules (track count + duration) are applied only to `album_type: "single"` releases. Compilations (`album_type: "compilation"`) are dropped without fetching. See ADR-0001 for the rationale and rejected alternatives.

### `Album` model in `models.py`

```python
@dataclasses.dataclass(frozen=True)
class Album:
    id: str
    name: str
    release_date: str
```

`total_tracks` is intentionally excluded — it was needed only during classification. Downstream steps (playlist creation) will fetch the full track list independently.

### `fetch_album_tracks` uses the same `urllib.request` pattern

Consistent with `fetch_artist_releases` and `fetch_saved_albums` — no new dependencies, same pagination loop, same auth header approach.

## Risks / Trade-offs

- **Spotify mislabels an album as `"single"`** → The EP rules would classify it correctly if it qualifies, or drop it if it doesn't. This is the expected fallback.
- **Spotify mislabels a `"single"` as `"album"`** → It passes through without the EP gate, potentially including a single-track promo. Accepted per ADR-0001: we trust Spotify's `"album"` label.
- **Track fetch per `"single"` release** → For artists with many singles this adds API calls. Acceptable at current scale; batching can be added later if rate limits become a concern.
