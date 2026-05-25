from __future__ import annotations

import json
import urllib.request
from typing import Any
from unittest.mock import patch

import pytest

from spotify_playlist_creator.auth import SpotifyToken
from spotify_playlist_creator.saved_albums import SavedAlbum, fetch_saved_albums

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_VALID_TOKEN = SpotifyToken(
    access_token="test_access_token",
    token_type="Bearer",
    refresh_token="test_refresh_token",
    expires_at=9_999_999_999.0,
)

_EMPTY_TOKEN = SpotifyToken(
    access_token="",
    token_type="Bearer",
    refresh_token="test_refresh_token",
    expires_at=9_999_999_999.0,
)


def _make_response(items: list[dict[str, Any]], next_url: str | None = None) -> Any:
    class _Response:
        def read(self) -> bytes:
            return json.dumps({"items": items, "next": next_url}).encode()

        def __enter__(self) -> _Response:
            return self

        def __exit__(self, *args: Any) -> None:
            pass

    return _Response()


def _album_item(album_id: str, name: str, artists: list[str]) -> dict[str, Any]:
    return {
        "album": {
            "id": album_id,
            "name": name,
            "artists": [{"name": a} for a in artists],
        }
    }


# ---------------------------------------------------------------------------
# Group 1: fetch_saved_albums behaviour
# ---------------------------------------------------------------------------


def test_fetch_saved_albums_empty_library() -> None:
    with patch("urllib.request.urlopen", return_value=_make_response([])):
        result = fetch_saved_albums(_VALID_TOKEN)
    assert result == []


def test_fetch_saved_albums_single_page() -> None:
    items = [
        _album_item("id1", "Album One", ["Artist A"]),
        _album_item("id2", "Album Two", ["Artist B", "Artist C"]),
    ]
    with patch("urllib.request.urlopen", return_value=_make_response(items)):
        result = fetch_saved_albums(_VALID_TOKEN)

    assert len(result) == 2
    assert result[0] == SavedAlbum(
        id="id1", name="Album One", artist_names=["Artist A"]
    )
    assert result[1] == SavedAlbum(
        id="id2", name="Album Two", artist_names=["Artist B", "Artist C"]
    )


def test_fetch_saved_albums_sends_authorization_header() -> None:
    captured: list[urllib.request.Request] = []

    def capturing_urlopen(req: urllib.request.Request) -> Any:
        captured.append(req)
        return _make_response([])

    with patch("urllib.request.urlopen", side_effect=capturing_urlopen):
        fetch_saved_albums(_VALID_TOKEN)

    assert captured[0].get_header("Authorization") == "Bearer test_access_token"


def test_fetch_saved_albums_multi_page() -> None:
    page1_items = [_album_item("id1", "Album One", ["Artist A"])]
    page2_items = [_album_item("id2", "Album Two", ["Artist B"])]

    responses = iter(
        [
            _make_response(
                page1_items,
                next_url="https://api.spotify.com/v1/me/albums?offset=50",
            ),
            _make_response(page2_items, next_url=None),
        ]
    )

    with patch("urllib.request.urlopen", side_effect=lambda _req: next(responses)):
        result = fetch_saved_albums(_VALID_TOKEN)

    assert len(result) == 2
    assert result[0].id == "id1"
    assert result[1].id == "id2"


def test_fetch_saved_albums_raises_for_missing_token() -> None:
    with patch("urllib.request.urlopen") as mock_urlopen:
        with pytest.raises(ValueError):
            fetch_saved_albums(_EMPTY_TOKEN)
    mock_urlopen.assert_not_called()
