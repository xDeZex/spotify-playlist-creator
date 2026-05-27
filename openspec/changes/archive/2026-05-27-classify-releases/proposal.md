## Why

The script fetches all releases for each artist but has no way to distinguish qualifying Albums (full albums and EPs) from singles. Without classification, every release — including promotional singles — would end up as an Album Playlist, which is not the intended behaviour.

## What Changes

- Introduce a new `Album` model representing a classified, qualifying release (full album or EP)
- Add a `classify_releases` function that filters a list of `RawRelease` objects down to `list[Album]`, fetching track durations from Spotify where needed
- Add a `fetch_album_tracks` function that retrieves per-track durations for a single release via the Spotify API

## Capabilities

### New Capabilities

- `album-classification`: Classify a list of `RawRelease` objects into qualifying Albums — trusting Spotify's `album_type: "album"` label directly, and applying EP rules (track count + duration) to `album_type: "single"` releases; actual singles are dropped

### Modified Capabilities

- `artist-releases`: Now produces `list[RawRelease]` as input to classification rather than a final output; no requirement changes to the fetch behaviour itself

## Impact

- New `Album` dataclass added to `models.py`
- New `classify_releases.py` module
- `artist-releases` spec unchanged in behaviour; its output is now consumed by the new classification step
- No new third-party dependencies — track durations fetched via the existing `urllib.request` pattern
