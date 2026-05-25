from __future__ import annotations

import dataclasses
import json
import urllib.request
from typing import Any

from spotify_playlist_creator.auth import SpotifyToken

_SAVED_ALBUMS_URL = "https://api.spotify.com/v1/me/albums"


@dataclasses.dataclass
class SavedAlbum:
    id: str
    name: str
    artist_names: list[str]


def fetch_saved_albums(token: SpotifyToken) -> list[SavedAlbum]:
    if not token.access_token:
        raise ValueError("No valid token provided")

    results: list[SavedAlbum] = []
    url: str | None = f"{_SAVED_ALBUMS_URL}?limit=50"

    while url is not None:
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {token.access_token}"},
        )
        with urllib.request.urlopen(req) as response:
            body: dict[str, Any] = json.loads(response.read())

        for item in body.get("items", []):
            album = item["album"]
            results.append(
                SavedAlbum(
                    id=str(album["id"]),
                    name=str(album["name"]),
                    artist_names=[str(a["name"]) for a in album.get("artists", [])],
                )
            )

        url = body.get("next")

    return results
