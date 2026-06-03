from __future__ import annotations

import dataclasses
from typing import Any

from spotify_playlist_creator.api import api_request
from spotify_playlist_creator.auth import SpotifyToken
from spotify_playlist_creator.models import Album

_API_BASE = "https://api.spotify.com/v1"


@dataclasses.dataclass(frozen=True)
class CreatedPlaylist:
    name: str
    id: str


def _fetch_current_user_id(token: SpotifyToken) -> str:
    if not token.access_token:
        raise ValueError("No valid token provided")
    body: dict[str, Any] = api_request(f"{_API_BASE}/me", token)
    return str(body["id"])


def fetch_owned_playlists(token: SpotifyToken) -> dict[str, list[str]]:
    if not token.access_token:
        raise ValueError("No valid token provided")

    user_id = _fetch_current_user_id(token)
    result: dict[str, list[str]] = {}
    url: str | None = f"{_API_BASE}/me/playlists?limit=10"

    while url is not None:
        body: dict[str, Any] = api_request(url, token)

        for item in body.get("items", []):
            if item.get("owner", {}).get("id") != user_id:
                continue
            name = str(item["name"])
            playlist_id = str(item["id"])
            result.setdefault(name, []).append(playlist_id)

        url = body.get("next")

    return result


def fetch_first_track_album_id(token: SpotifyToken, playlist_id: str) -> str | None:
    if not token.access_token:
        raise ValueError("No valid token provided")

    body: dict[str, Any] = api_request(
        f"{_API_BASE}/playlists/{playlist_id}/tracks?limit=1", token
    )
    items = body.get("items", [])
    if not items:
        return None
    return str(items[0]["track"]["album"]["id"])


def fetch_album_track_uris(token: SpotifyToken, album_id: str) -> list[str]:
    if not token.access_token:
        raise ValueError("No valid token provided")

    uris: list[str] = []
    url: str | None = f"{_API_BASE}/albums/{album_id}/tracks?limit=10"

    while url is not None:
        body: dict[str, Any] = api_request(url, token)

        for item in body.get("items", []):
            uris.append(str(item["uri"]))

        url = body.get("next")

    return uris


def add_tracks_to_playlist(
    token: SpotifyToken, playlist_id: str, uris: list[str]
) -> None:
    if not token.access_token:
        raise ValueError("No valid token provided")
    for i in range(0, len(uris), 100):
        batch = uris[i : i + 100]
        api_request(
            f"{_API_BASE}/playlists/{playlist_id}/tracks",
            token,
            body={"uris": batch},
        )


def find_missing_album_playlists(
    token: SpotifyToken,
    albums: list[Album],
    existing_playlists: dict[str, list[str]],
) -> list[Album]:
    if not token.access_token:
        raise ValueError("No valid token provided")

    def _already_exists(album: Album) -> bool:
        for pid in existing_playlists.get(album.name, []):
            if fetch_first_track_album_id(token, pid) == album.id:
                return True
        return False

    new_albums = [a for a in albums if not _already_exists(a)]
    new_albums.sort(key=lambda a: a.release_date, reverse=True)
    return new_albums


def create_album_playlists(
    token: SpotifyToken,
    new_albums: list[Album],
) -> list[CreatedPlaylist]:
    created: list[CreatedPlaylist] = []
    for album in new_albums:
        body: dict[str, Any] = api_request(
            f"{_API_BASE}/me/playlists",
            token,
            body={"name": album.name, "public": True},
        )
        playlist_id = str(body["id"])
        uris = fetch_album_track_uris(token, album.id)
        if uris:
            add_tracks_to_playlist(token, playlist_id, uris)

        created.append(CreatedPlaylist(name=album.name, id=playlist_id))

    return created
