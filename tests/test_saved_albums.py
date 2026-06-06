from __future__ import annotations

import io
import json
import urllib.error
import urllib.request
from datetime import datetime
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

import spotify_playlist_creator.status as status
from spotify_playlist_creator.auth import SpotifyToken
from spotify_playlist_creator.models import Artist, SavedAlbum
from spotify_playlist_creator.saved_albums import derive_artists, fetch_saved_albums

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


def _make_response(
    items: list[dict[str, Any]],
    next_url: str | None = None,
    total: int | None = None,
    limit: int | None = None,
) -> Any:
    class _Response:
        def read(self) -> bytes:
            body: dict[str, Any] = {"items": items, "next": next_url}
            if total is not None:
                body["total"] = total
            if limit is not None:
                body["limit"] = limit
            return json.dumps(body).encode()

        def __enter__(self) -> _Response:
            return self

        def __exit__(self, *args: Any) -> None:
            pass

    return _Response()


def _album_item(
    album_id: str,
    name: str,
    artists: list[str],
    added_at: str = "2024-01-01T00:00:00Z",
) -> dict[str, Any]:
    return {
        "added_at": added_at,
        "album": {
            "id": album_id,
            "name": name,
            "artists": [
                {"id": a.lower().replace(" ", "-"), "name": a} for a in artists
            ],
        },
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
    assert result[0].id == "id1"
    assert result[0].name == "Album One"
    assert result[0].artists == [Artist(id="artist-a", name="Artist A")]
    assert result[0].added_at == datetime(2024, 1, 1, 0, 0, 0)
    assert result[1].id == "id2"
    assert result[1].name == "Album Two"
    assert result[1].artists == [
        Artist(id="artist-b", name="Artist B"),
        Artist(id="artist-c", name="Artist C"),
    ]


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


# ---------------------------------------------------------------------------
# Group 2: derive_artists behaviour
# ---------------------------------------------------------------------------


def _saved_album(
    album_id: str,
    artists: list[Artist],
    added_at: datetime = datetime(2024, 1, 1),
) -> SavedAlbum:
    return SavedAlbum(id=album_id, name="Album", artists=artists, added_at=added_at)


def test_derive_artists_empty_list() -> None:
    assert derive_artists([]) == []


def test_derive_artists_returns_primary_artist_only() -> None:
    primary = Artist(id="a1", name="Primary")
    feature = Artist(id="a2", name="Feature")
    album = _saved_album("alb1", [primary, feature])
    assert derive_artists([album]) == [primary]


def test_derive_artists_deduplicates_by_id() -> None:
    artist = Artist(id="a1", name="Artist")
    albums = [_saved_album("alb1", [artist]), _saved_album("alb2", [artist])]
    assert derive_artists(albums) == [artist]


def test_derive_artists_orders_by_oldest_added_at() -> None:
    older = Artist(id="a1", name="Older")
    newer = Artist(id="a2", name="Newer")
    albums = [
        _saved_album("alb1", [newer], added_at=datetime(2024, 6, 1)),
        _saved_album("alb2", [older], added_at=datetime(2024, 1, 1)),
    ]
    assert derive_artists(albums) == [older, newer]


def test_derive_artists_uses_earliest_album_for_artist_ordering() -> None:
    # artist_a has an early album (Jan) and a later one (Mar)
    # artist_b has only one album (Feb)
    # artist_a's earliest is Jan → comes before artist_b's Feb
    artist_a = Artist(id="a1", name="Artist A")
    artist_b = Artist(id="a2", name="Artist B")
    albums = [
        _saved_album("alb1", [artist_a], added_at=datetime(2024, 3, 1)),
        _saved_album("alb2", [artist_b], added_at=datetime(2024, 2, 1)),
        _saved_album("alb3", [artist_a], added_at=datetime(2024, 1, 1)),
    ]
    assert derive_artists(albums) == [artist_a, artist_b]


def test_fetch_saved_albums_populates_added_at() -> None:
    items = [
        _album_item("id1", "Album One", ["Artist A"], added_at="2024-03-15T10:30:00Z")
    ]
    with patch("urllib.request.urlopen", return_value=_make_response(items)):
        result = fetch_saved_albums(_VALID_TOKEN)
    assert result[0].added_at == datetime(2024, 3, 15, 10, 30, 0)


def test_fetch_saved_albums_added_at_with_milliseconds() -> None:
    items = [
        _album_item(
            "id1", "Album One", ["Artist A"], added_at="2024-03-15T10:30:00.000Z"
        )
    ]
    with patch("urllib.request.urlopen", return_value=_make_response(items)):
        result = fetch_saved_albums(_VALID_TOKEN)
    assert result[0].added_at == datetime(2024, 3, 15, 10, 30, 0)


# ---------------------------------------------------------------------------
# Group 2.1: fetch_saved_albums uses api_request (propagates RuntimeError)
# ---------------------------------------------------------------------------


def test_fetch_saved_albums_propagates_api_error_as_runtime_error() -> None:
    hdrs: MagicMock = MagicMock()
    hdrs.get = lambda key, default=None: default
    http_err = urllib.error.HTTPError(
        url="https://api.spotify.com/v1/me/albums",
        code=403,
        msg="Forbidden",
        hdrs=hdrs,
        fp=io.BytesIO(
            b'{"error": {"status": 403, "message": "Insufficient client scope"}}'
        ),
    )
    with patch("urllib.request.urlopen", side_effect=http_err):
        with pytest.raises(
            RuntimeError,
            match=r"Spotify API error \(403 /v1/me/albums\): Insufficient client scope",
        ):
            fetch_saved_albums(_VALID_TOKEN)


# ---------------------------------------------------------------------------
# Group 2.2: API error during saved albums fetch propagates as RuntimeError
# ---------------------------------------------------------------------------


def test_fetch_saved_albums_api_error_on_second_page_propagates() -> None:
    page1_items = [_album_item("id1", "Album One", ["Artist A"])]
    call_count = [0]

    def failing_on_second_call(_req: Any) -> Any:
        call_count[0] += 1
        if call_count[0] == 1:
            return _make_response(
                page1_items,
                next_url="https://api.spotify.com/v1/me/albums?offset=10",
            )
        hdrs: MagicMock = MagicMock()
        hdrs.get = lambda key, default=None: default
        raise urllib.error.HTTPError(
            url="https://api.spotify.com/v1/me/albums",
            code=500,
            msg="Internal Server Error",
            hdrs=hdrs,
            fp=io.BytesIO(b'{"error": {"status": 500, "message": "Server error"}}'),
        )

    with patch("urllib.request.urlopen", side_effect=failing_on_second_call):
        with pytest.raises(RuntimeError, match="Spotify API error"):
            fetch_saved_albums(_VALID_TOKEN)


# ---------------------------------------------------------------------------
# Task 4.1: fetch_saved_albums writes pagination status
# ---------------------------------------------------------------------------


def test_fetch_saved_albums_writes_page_progress_for_each_page() -> None:
    received: list[str] = []
    status.configure(received.append)

    page1 = [_album_item("id1", "Album One", ["Artist A"])]
    page2 = [_album_item("id2", "Album Two", ["Artist B"])]

    responses = iter(
        [
            _make_response(
                page1,
                next_url="https://api.spotify.com/v1/me/albums?offset=10",
                total=20,
                limit=10,
            ),
            _make_response(page2, next_url=None, total=20, limit=10),
        ]
    )

    with patch("urllib.request.urlopen", side_effect=lambda _req: next(responses)):
        fetch_saved_albums(_VALID_TOKEN)

    assert "\r\033[2Kfetching saved albums (1/2)..." in received
    assert "\r\033[2Kfetching saved albums (2/2)..." in received


def test_fetch_saved_albums_writes_page_progress_when_total_and_limit_absent() -> None:
    received: list[str] = []
    status.configure(received.append)

    with patch(
        "urllib.request.urlopen",
        return_value=_make_response([]),  # no total or limit fields
    ):
        fetch_saved_albums(_VALID_TOKEN)

    assert "\r\033[2Kfetching saved albums (1/1)..." in received
