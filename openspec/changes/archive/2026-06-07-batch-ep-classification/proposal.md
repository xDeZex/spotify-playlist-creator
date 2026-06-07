## Why

`classify_releases` calls `GET /v1/albums/{id}/tracks` once per single, producing ~2,000 API calls for a typical library and being the primary driver of rate-limit exhaustion (see issue #63). The batch endpoint `GET /v1/albums?ids=...` returns track durations inline for up to 20 albums per call, reducing the call count to ~100.

## What Changes

- **New**: `fetch_singles_durations(token, ids: list[str]) -> dict[str, list[int]]` in `classify_releases.py` — calls `GET /v1/albums?ids=...` (up to 20 IDs), extracts `tracks.items[*].duration_ms` from each album object, skips null entries silently
- **Removed**: `fetch_album_tracks` — deleted entirely; no longer called anywhere
- **Modified**: `classify_releases` — pre-collects all single IDs, chunks them into batches of 20, calls `fetch_singles_durations` per batch (writing status after each), then classifies using the pre-fetched dict
- **Modified**: Status message remains `"classifying singles (N/total)..."` but N now increments by batch size (up to 20) rather than by 1

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `album-classification`: fetch strategy changes from per-single `GET /albums/{id}/tracks` to batched `GET /albums?ids=...`; status reporting moves from per-single to per-batch; null-album handling added; `fetch_album_tracks` removed

## Impact

- `spotify_playlist_creator/classify_releases.py` — primary change site
- `tests/test_classify_releases.py` — 5 `fetch_album_tracks` tests deleted; new tests for `fetch_singles_durations` and updated `classify_releases` integration tests using batch response shape
- `docs/adr/0009-batch-ep-classification-via-albums-endpoint.md` — already written
