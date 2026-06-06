from __future__ import annotations

import math
from typing import Any

from spotify_playlist_creator import status
from spotify_playlist_creator.api import api_request
from spotify_playlist_creator.auth import SpotifyToken
from spotify_playlist_creator.models import RawRelease

_ARTIST_ALBUMS_URL = "https://api.spotify.com/v1/artists/{artist_id}/albums"


def fetch_artist_releases(token: SpotifyToken, artist_id: str) -> list[RawRelease]:
    if not token.access_token:
        raise ValueError("No valid token provided")

    results: list[RawRelease] = []
    url: str | None = (
        f"{_ARTIST_ALBUMS_URL.format(artist_id=artist_id)}"
        f"?include_groups=album,single&limit=10"
    )
    page = 0
    total_pages: int | None = None

    while url is not None:
        body: dict[str, Any] = api_request(url, token)
        page += 1
        if total_pages is None:
            total = int(body.get("total", 0))
            limit_val = int(body.get("limit", 1)) or 1
            total_pages = max(1, math.ceil(total / limit_val))
        status.write(f"fetching releases ({page}/{total_pages})...")

        for item in body.get("items", []):
            results.append(
                RawRelease(
                    id=str(item["id"]),
                    name=str(item["name"]),
                    album_type=str(item["album_type"]),
                    release_date=str(item["release_date"]),
                )
            )

        url = body.get("next")

    return results
