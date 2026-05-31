from __future__ import annotations

import dataclasses
import json
import urllib.request
from typing import Any

from spotify_playlist_creator.auth import SpotifyToken
from spotify_playlist_creator.models import Album

_API_BASE = "https://api.spotify.com/v1"


@dataclasses.dataclass(frozen=True)
class CreatedPlaylist:
    name: str
    id: str


def fetch_user_playlist_names(token: SpotifyToken) -> set[str]:
    if not token.access_token:
        raise ValueError("No valid token provided")

    names: set[str] = set()
    url: str | None = f"{_API_BASE}/me/playlists?limit=50"

    while url is not None:
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {token.access_token}"},
        )
        with urllib.request.urlopen(req) as response:
            body: dict[str, Any] = json.loads(response.read())

        for item in body.get("items", []):
            names.add(str(item["name"]))

        url = body.get("next")

    return names


def fetch_album_track_uris(token: SpotifyToken, album_id: str) -> list[str]:
    if not token.access_token:
        raise ValueError("No valid token provided")

    uris: list[str] = []
    url: str | None = f"{_API_BASE}/albums/{album_id}/tracks?limit=50"

    while url is not None:
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {token.access_token}"},
        )
        with urllib.request.urlopen(req) as response:
            body: dict[str, Any] = json.loads(response.read())

        for item in body.get("items", []):
            uris.append(str(item["uri"]))

        url = body.get("next")

    return uris


def add_tracks_to_playlist(
    token: SpotifyToken, playlist_id: str, uris: list[str]
) -> None:
    for i in range(0, len(uris), 100):
        batch = uris[i : i + 100]
        data = json.dumps({"uris": batch}).encode()
        req = urllib.request.Request(
            f"{_API_BASE}/playlists/{playlist_id}/tracks",
            data=data,
            headers={
                "Authorization": f"Bearer {token.access_token}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req) as response:
            response.read()


def create_album_playlists(
    token: SpotifyToken,
    user_id: str,
    albums: list[Album],
    existing_names: set[str],
) -> list[CreatedPlaylist]:
    new_albums = [a for a in albums if a.name not in existing_names]
    new_albums.sort(key=lambda a: a.release_date, reverse=True)

    created: list[CreatedPlaylist] = []
    for album in new_albums:
        data = json.dumps({"name": album.name, "public": True}).encode()
        req = urllib.request.Request(
            f"{_API_BASE}/users/{user_id}/playlists",
            data=data,
            headers={
                "Authorization": f"Bearer {token.access_token}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req) as response:
            body: dict[str, Any] = json.loads(response.read())

        playlist_id = str(body["id"])
        uris = fetch_album_track_uris(token, album.id)
        if uris:
            add_tracks_to_playlist(token, playlist_id, uris)

        created.append(CreatedPlaylist(name=album.name, id=playlist_id))

    return created
