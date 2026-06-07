from __future__ import annotations

from typing import Any

from spotify_playlist_creator import status
from spotify_playlist_creator.api import api_request
from spotify_playlist_creator.auth import SpotifyToken
from spotify_playlist_creator.models import Album, RawRelease

_ALBUMS_URL = "https://api.spotify.com/v1/albums"

_30_MIN_MS = 30 * 60 * 1_000
_10_MIN_MS = 10 * 60 * 1_000


def _is_ep(durations: list[int]) -> bool:
    """Return True if the release qualifies as an EP by Spotify classification rules."""
    total_tracks = len(durations)
    total_ms = sum(durations)
    if 4 <= total_tracks <= 6:
        return total_ms <= _30_MIN_MS
    if 1 <= total_tracks <= 3:
        return any(d > _10_MIN_MS for d in durations) and total_ms > _30_MIN_MS
    return False


def classify_releases(
    token: SpotifyToken, raw_releases: list[RawRelease]
) -> list[Album]:
    """Filter raw releases down to qualifying Albums (full albums and EPs)."""
    singles = [r for r in raw_releases if r.album_type == "single"]
    total_singles = len(singles)

    durations_map: dict[str, list[int]] = {}
    for i in range(0, total_singles, 20):
        batch = singles[i : i + 20]
        n = i + len(batch)
        status.write(f"classifying singles ({n}/{total_singles})...")
        durations_map.update(fetch_singles_durations(token, [s.id for s in batch]))

    results: list[Album] = []
    for release in raw_releases:
        if release.album_type == "album":
            results.append(
                Album(
                    id=release.id, name=release.name, release_date=release.release_date
                )
            )
        elif release.album_type == "single":
            if _is_ep(durations_map.get(release.id, [])):
                results.append(
                    Album(
                        id=release.id,
                        name=release.name,
                        release_date=release.release_date,
                    )
                )
        # compilations are silently dropped
    return results


def fetch_singles_durations(
    token: SpotifyToken, ids: list[str]
) -> dict[str, list[int]]:
    """Fetch track durations for up to 20 album IDs via the batch albums endpoint."""
    body: dict[str, Any] = api_request(f"{_ALBUMS_URL}?ids={','.join(ids)}", token)
    result: dict[str, list[int]] = {}
    for album in body.get("albums", []):
        if album is None:
            continue
        album_id: str = album["id"]
        result[album_id] = [
            int(item["duration_ms"]) for item in album["tracks"]["items"]
        ]
    return result
