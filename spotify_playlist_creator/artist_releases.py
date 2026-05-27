from __future__ import annotations

import json
import urllib.request
from typing import Any

from spotify_playlist_creator.auth import SpotifyToken
from spotify_playlist_creator.models import RawRelease

_ARTIST_ALBUMS_URL = "https://api.spotify.com/v1/artists/{artist_id}/albums"


def fetch_artist_releases(token: SpotifyToken, artist_id: str) -> list[RawRelease]:
    if not token.access_token:
        raise ValueError("No valid token provided")

    results: list[RawRelease] = []
    url: str | None = (
        f"{_ARTIST_ALBUMS_URL.format(artist_id=artist_id)}?include_groups=album,single&limit=50"
    )

    while url is not None:
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {token.access_token}"},
        )
        with urllib.request.urlopen(req) as response:
            body: dict[str, Any] = json.loads(response.read())

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
