from __future__ import annotations

from typing import Any

from spotify_playlist_creator import status
from spotify_playlist_creator.api import api_request
from spotify_playlist_creator.auth import SpotifyToken
from spotify_playlist_creator.models import Album, RawRelease

_ALBUM_TRACKS_URL = "https://api.spotify.com/v1/albums/{album_id}/tracks"

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
    total_singles = sum(1 for r in raw_releases if r.album_type == "single")
    single_idx = 0
    results: list[Album] = []
    for release in raw_releases:
        if release.album_type == "album":
            results.append(
                Album(
                    id=release.id, name=release.name, release_date=release.release_date
                )
            )
        elif release.album_type == "single":
            single_idx += 1
            status.write(f"classifying singles ({single_idx}/{total_singles})...")
            durations = fetch_album_tracks(token, release.id)
            if _is_ep(durations):
                results.append(
                    Album(
                        id=release.id,
                        name=release.name,
                        release_date=release.release_date,
                    )
                )
        # compilations are silently dropped
    return results


def fetch_album_tracks(token: SpotifyToken, album_id: str) -> list[int]:
    """Fetch all track durations (ms) for *album_id*, following pagination."""
    if not token.access_token:
        raise ValueError("No valid token provided")

    durations: list[int] = []
    url: str | None = _ALBUM_TRACKS_URL.format(album_id=album_id)

    while url is not None:
        body: dict[str, Any] = api_request(url, token)

        for item in body.get("items", []):
            durations.append(int(item["duration_ms"]))

        url = body.get("next")

    return durations
