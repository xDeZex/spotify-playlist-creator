from __future__ import annotations

import json
import urllib.request
from typing import Any
from unittest.mock import patch

import pytest

from spotify_playlist_creator.artist_releases import fetch_artist_releases
from spotify_playlist_creator.auth import SpotifyToken
from spotify_playlist_creator.models import RawRelease

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


def _release_item(
    album_id: str = "alb1",
    name: str = "Album One",
    album_type: str = "album",
    total_tracks: int = 10,
    release_date: str = "2021-05-14",
) -> dict[str, Any]:
    return {
        "id": album_id,
        "name": name,
        "album_type": album_type,
        "total_tracks": total_tracks,
        "release_date": release_date,
    }


# ---------------------------------------------------------------------------
# Group 1: RawRelease model
# ---------------------------------------------------------------------------


def test_raw_release_construction() -> None:
    r = RawRelease(
        id="alb1",
        name="Album One",
        album_type="album",
        total_tracks=10,
        release_date="2021-05-14",
    )
    assert r.id == "alb1"
    assert r.name == "Album One"
    assert r.album_type == "album"
    assert r.total_tracks == 10
    assert r.release_date == "2021-05-14"


def test_raw_release_release_date_stored_as_string() -> None:
    r = RawRelease(
        id="a", name="X", album_type="album", total_tracks=1, release_date="1997"
    )
    assert r.release_date == "1997"


def test_raw_releases_sort_chronologically_by_release_date() -> None:
    releases = [
        RawRelease(
            id="c",
            name="C",
            album_type="album",
            total_tracks=10,
            release_date="2021-05-14",
        ),
        RawRelease(
            id="a", name="A", album_type="album", total_tracks=10, release_date="1997"
        ),
        RawRelease(
            id="b",
            name="B",
            album_type="album",
            total_tracks=10,
            release_date="2021-03",
        ),
    ]
    sorted_releases = sorted(releases, key=lambda r: r.release_date)
    assert [r.id for r in sorted_releases] == ["a", "b", "c"]


# ---------------------------------------------------------------------------
# Group 2: fetch_artist_releases behaviour
# ---------------------------------------------------------------------------


def test_fetch_artist_releases_raises_for_missing_token() -> None:
    with patch("urllib.request.urlopen") as mock_urlopen:
        with pytest.raises(ValueError):
            fetch_artist_releases(_EMPTY_TOKEN, "artist-id")
    mock_urlopen.assert_not_called()


def test_fetch_artist_releases_calls_correct_url() -> None:
    captured: list[urllib.request.Request] = []

    def capturing_urlopen(req: urllib.request.Request) -> Any:
        captured.append(req)
        return _make_response([])

    with patch("urllib.request.urlopen", side_effect=capturing_urlopen):
        fetch_artist_releases(_VALID_TOKEN, "artist123")

    assert len(captured) == 1
    assert "artists/artist123/albums" in captured[0].full_url
    assert "include_groups=album,single" in captured[0].full_url


def test_fetch_artist_releases_sends_authorization_header() -> None:
    captured: list[urllib.request.Request] = []

    def capturing_urlopen(req: urllib.request.Request) -> Any:
        captured.append(req)
        return _make_response([])

    with patch("urllib.request.urlopen", side_effect=capturing_urlopen):
        fetch_artist_releases(_VALID_TOKEN, "artist123")

    assert captured[0].get_header("Authorization") == "Bearer test_access_token"


def test_fetch_artist_releases_empty_discography() -> None:
    with patch("urllib.request.urlopen", return_value=_make_response([])):
        result = fetch_artist_releases(_VALID_TOKEN, "artist123")
    assert result == []


def test_fetch_artist_releases_single_page() -> None:
    items = [
        _release_item("alb1", "Album One", "album", 12, "2020-03-01"),
        _release_item("alb2", "Single One", "single", 1, "2021-06-15"),
    ]
    with patch("urllib.request.urlopen", return_value=_make_response(items)):
        result = fetch_artist_releases(_VALID_TOKEN, "artist123")

    assert len(result) == 2
    assert result[0] == RawRelease(
        id="alb1",
        name="Album One",
        album_type="album",
        total_tracks=12,
        release_date="2020-03-01",
    )
    assert result[1] == RawRelease(
        id="alb2",
        name="Single One",
        album_type="single",
        total_tracks=1,
        release_date="2021-06-15",
    )


def test_fetch_artist_releases_multi_page() -> None:
    page1 = [_release_item("alb1", "Album One", "album", 10, "2019-01-01")]
    page2 = [_release_item("alb2", "Album Two", "album", 11, "2021-05-14")]

    page_responses = [
        _make_response(
            page1,
            next_url="https://api.spotify.com/v1/artists/artist123/albums?offset=50",
        ),
        _make_response(page2, next_url=None),
    ]
    response_iter = iter(page_responses)
    captured: list[urllib.request.Request] = []

    def capturing_urlopen(req: urllib.request.Request) -> Any:
        captured.append(req)
        return next(response_iter)

    with patch("urllib.request.urlopen", side_effect=capturing_urlopen):
        result = fetch_artist_releases(_VALID_TOKEN, "artist123")

    assert len(result) == 2
    assert result[0].id == "alb1"
    assert result[1].id == "alb2"
    assert len(captured) == 2
    for req in captured:
        assert req.get_header("Authorization") == "Bearer test_access_token"
