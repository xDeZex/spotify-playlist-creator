from __future__ import annotations

import math
from datetime import datetime
from typing import Any

from spotify_playlist_creator import status
from spotify_playlist_creator.api import api_request
from spotify_playlist_creator.auth import SpotifyToken
from spotify_playlist_creator.models import Artist, SavedAlbum

_SAVED_ALBUMS_URL = "https://api.spotify.com/v1/me/albums"


def _parse_items(body: dict[str, Any]) -> list[SavedAlbum]:
    result: list[SavedAlbum] = []
    for item in body.get("items", []):
        album = item["album"]
        result.append(
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
    return result


def _distinct_primary_artist_ids(albums: list[SavedAlbum]) -> set[str]:
    return {a.artists[0].id for a in albums if a.artists}


def fetch_saved_albums(
    token: SpotifyToken, *, limit: int | None = None
) -> list[SavedAlbum]:
    if not token.access_token:
        raise ValueError("No valid token provided")

    if limit is None:
        return _fetch_all(token)
    return _fetch_limited(token, limit)


def _fetch_all(token: SpotifyToken) -> list[SavedAlbum]:
    results: list[SavedAlbum] = []
    url: str | None = f"{_SAVED_ALBUMS_URL}?limit=50"
    page = 0
    total_pages: int | None = None

    while url is not None:
        body: dict[str, Any] = api_request(url, token)
        page += 1
        if total_pages is None:
            total = int(body.get("total", 0))
            limit_val = int(body.get("limit", 1)) or 1
            total_pages = max(1, math.ceil(total / limit_val))
        status.write(f"fetching saved albums ({page}/{total_pages})...")
        results.extend(_parse_items(body))
        url = body.get("next")

    return results


def _fetch_limited(token: SpotifyToken, limit: int) -> list[SavedAlbum]:
    # Probe at offset=0 to learn total.
    probe_url = f"{_SAVED_ALBUMS_URL}?limit=50"
    probe_body: dict[str, Any] = api_request(probe_url, token)
    total = int(probe_body.get("total", 0))
    limit_val = int(probe_body.get("limit", 1)) or 1
    total_pages = max(1, math.ceil(total / limit_val))

    status.write(f"fetching saved albums (1/{total_pages})...")
    probe_items = _parse_items(probe_body)

    if total <= 50:
        # last_offset would be 0 for total <= 50, which the loop (offset >= 50) can't reach.
        return probe_items

    # Backward sweep: last page first, then decreasing offsets toward offset=50.
    last_offset = ((total - 1) // 50) * 50
    backward_results: list[SavedAlbum] = []
    call_number = 1  # probe was call 1

    offset = last_offset
    while offset >= 50:
        call_number += 1
        url = f"{_SAVED_ALBUMS_URL}?limit=50&offset={offset}"
        body: dict[str, Any] = api_request(url, token)
        status.write(f"fetching saved albums ({call_number}/{total_pages})...")
        backward_results.extend(_parse_items(body))

        if len(_distinct_primary_artist_ids(backward_results)) >= limit:
            return backward_results

        offset -= 50

    # Backward sweep exhausted all pages without reaching limit — include probe items.
    return backward_results + probe_items


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
