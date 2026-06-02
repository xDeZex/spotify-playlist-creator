from __future__ import annotations

from datetime import datetime
from typing import Any

from spotify_playlist_creator.api import api_request
from spotify_playlist_creator.auth import SpotifyToken
from spotify_playlist_creator.models import Artist, SavedAlbum

_SAVED_ALBUMS_URL = "https://api.spotify.com/v1/me/albums"


def fetch_saved_albums(token: SpotifyToken) -> list[SavedAlbum]:
    if not token.access_token:
        raise ValueError("No valid token provided")

    results: list[SavedAlbum] = []
    url: str | None = f"{_SAVED_ALBUMS_URL}?limit=10"

    while url is not None:
        body: dict[str, Any] = api_request(url, token)

        for item in body.get("items", []):
            album = item["album"]
            results.append(
                SavedAlbum(
                    id=str(album["id"]),
                    name=str(album["name"]),
                    artists=[
                        Artist(id=str(a["id"]), name=str(a["name"]))
                        for a in album.get("artists", [])
                    ],
                    added_at=datetime.fromisoformat(
                        str(item["added_at"]).replace("Z", "+00:00")
                    ).replace(tzinfo=None),
                )
            )

        url = body.get("next")

    return results


def derive_artists(albums: list[SavedAlbum]) -> list[Artist]:
    seen: set[str] = set()
    result: list[Artist] = []
    for album in sorted(albums, key=lambda a: a.added_at):
        if not album.artists:
            continue
        primary = album.artists[0]
        if primary.id not in seen:
            seen.add(primary.id)
            result.append(primary)
    return result
