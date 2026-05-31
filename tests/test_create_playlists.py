from __future__ import annotations

import json
import urllib.request as urllib_request
from typing import Any
from unittest.mock import patch

import pytest

from spotify_playlist_creator.auth import SpotifyToken
from spotify_playlist_creator.create_playlists import (
    add_tracks_to_playlist,
    create_album_playlists,
    fetch_album_track_uris,
    fetch_user_playlist_names,
)
from spotify_playlist_creator.models import Album

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TOKEN = SpotifyToken(
    access_token="test_tok",
    token_type="Bearer",
    refresh_token="rtoken",
    expires_at=9_999_999_999.0,
)

_EMPTY_TOKEN = SpotifyToken(
    access_token="",
    token_type="Bearer",
    refresh_token="rtoken",
    expires_at=9_999_999_999.0,
)

_USER_ID = "user123"


def _playlist_page(names: list[str], next_url: str | None = None) -> Any:
    class _Response:
        def read(self) -> bytes:
            return json.dumps(
                {"items": [{"name": n} for n in names], "next": next_url}
            ).encode()

        def __enter__(self) -> _Response:
            return self

        def __exit__(self, *args: Any) -> None:
            pass

    return _Response()


def _create_playlist_response(playlist_id: str, name: str) -> Any:
    class _Response:
        def read(self) -> bytes:
            return json.dumps({"id": playlist_id, "name": name}).encode()

        def __enter__(self) -> _Response:
            return self

        def __exit__(self, *args: Any) -> None:
            pass

    return _Response()


def _tracks_page(uris: list[str], next_url: str | None = None) -> Any:
    class _Response:
        def read(self) -> bytes:
            return json.dumps(
                {"items": [{"uri": u} for u in uris], "next": next_url}
            ).encode()

        def __enter__(self) -> _Response:
            return self

        def __exit__(self, *args: Any) -> None:
            pass

    return _Response()


def _add_tracks_response() -> Any:
    class _Response:
        def read(self) -> bytes:
            return json.dumps({"snapshot_id": "snap1"}).encode()

        def __enter__(self) -> _Response:
            return self

        def __exit__(self, *args: Any) -> None:
            pass

    return _Response()


def _album(album_id: str, name: str, release_date: str) -> Album:
    return Album(id=album_id, name=name, release_date=release_date)


# ---------------------------------------------------------------------------
# Group 1: fetch_user_playlist_names
# ---------------------------------------------------------------------------


def test_fetch_user_playlist_names_returns_all_names() -> None:
    with patch(
        "urllib.request.urlopen",
        return_value=_playlist_page(["Alpha", "Beta", "Gamma"]),
    ):
        result = fetch_user_playlist_names(_TOKEN)

    assert result == {"Alpha", "Beta", "Gamma"}


# ---------------------------------------------------------------------------
# Group 1.2: fetch_user_playlist_names follows pagination
# ---------------------------------------------------------------------------


def test_fetch_user_playlist_names_follows_pagination() -> None:
    responses = [
        _playlist_page(
            ["Alpha", "Beta"],
            next_url="https://api.spotify.com/v1/me/playlists?offset=50",
        ),
        _playlist_page(["Gamma"], next_url=None),
    ]
    resp_iter = iter(responses)

    with patch("urllib.request.urlopen", side_effect=lambda _req: next(resp_iter)):
        result = fetch_user_playlist_names(_TOKEN)

    assert result == {"Alpha", "Beta", "Gamma"}


# ---------------------------------------------------------------------------
# Group 1.3: fetch_user_playlist_names returns empty set when no playlists
# ---------------------------------------------------------------------------


def test_fetch_user_playlist_names_empty_library() -> None:
    with patch("urllib.request.urlopen", return_value=_playlist_page([])):
        result = fetch_user_playlist_names(_TOKEN)

    assert result == set()


def test_fetch_user_playlist_names_deduplicates_names() -> None:
    with patch("urllib.request.urlopen", return_value=_playlist_page(["X", "X", "Y"])):
        result = fetch_user_playlist_names(_TOKEN)

    assert result == {"X", "Y"}


def test_fetch_user_playlist_names_sends_auth_header() -> None:
    captured: list[urllib_request.Request] = []

    def capturing_urlopen(req: urllib_request.Request) -> Any:
        captured.append(req)
        return _playlist_page([])

    with patch("urllib.request.urlopen", side_effect=capturing_urlopen):
        fetch_user_playlist_names(_TOKEN)

    assert len(captured) == 1
    assert captured[0].get_header("Authorization") == "Bearer test_tok"


def test_fetch_user_playlist_names_raises_for_empty_token() -> None:
    with patch("urllib.request.urlopen") as mock_urlopen:
        with pytest.raises(ValueError):
            fetch_user_playlist_names(_EMPTY_TOKEN)
    mock_urlopen.assert_not_called()


def test_fetch_album_track_uris_raises_for_empty_token() -> None:
    with patch("urllib.request.urlopen") as mock_urlopen:
        with pytest.raises(ValueError):
            fetch_album_track_uris(_EMPTY_TOKEN, "alb1")
    mock_urlopen.assert_not_called()


# ---------------------------------------------------------------------------
# Group 2: create_album_playlists — create and skip logic
# ---------------------------------------------------------------------------


def test_create_album_playlists_creates_playlist_for_each_new_album() -> None:
    # Albums ordered newest-first so response sequence matches descending sort
    albums = [
        _album("a1", "Album One", "2021-06-15"),
        _album("a2", "Album Two", "2020-01-01"),
    ]
    existing: set[str] = set()

    responses = [
        _create_playlist_response("p1", "Album One"),
        _tracks_page([]),
        _create_playlist_response("p2", "Album Two"),
        _tracks_page([]),
    ]
    resp_iter = iter(responses)

    with patch("urllib.request.urlopen", side_effect=lambda _req: next(resp_iter)):
        result = create_album_playlists(_TOKEN, _USER_ID, albums, existing)

    assert len(result) == 2
    assert {r.name for r in result} == {"Album One", "Album Two"}


def test_create_album_playlists_processes_in_descending_release_date_order() -> None:
    albums = [
        _album("a1", "Oldest", "2019-03-01"),
        _album("a2", "Newest", "2023-11-01"),
        _album("a3", "Middle", "2021-07-01"),
    ]
    created_order: list[str] = []

    def fake_urlopen(req: Any) -> Any:
        url = req.full_url if hasattr(req, "full_url") else str(req)
        if "users" in url:
            name = json.loads(req.data.decode())["name"]
            created_order.append(name)
            return _create_playlist_response("pid", name)
        return _tracks_page([])

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        create_album_playlists(_TOKEN, _USER_ID, albums, set())

    assert created_order == ["Newest", "Middle", "Oldest"]


def test_create_album_playlists_returns_in_descending_release_date_order() -> None:
    albums = [
        _album("a1", "Oldest", "2019-03-01"),
        _album("a2", "Newest", "2023-11-01"),
        _album("a3", "Middle", "2021-07-01"),
    ]

    def fake_urlopen(req: Any) -> Any:
        url = req.full_url if hasattr(req, "full_url") else str(req)
        if "users" in url:
            name = json.loads(req.data.decode())["name"]
            return _create_playlist_response("pid", name)
        return _tracks_page([])

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        result = create_album_playlists(_TOKEN, _USER_ID, albums, set())

    assert [r.name for r in result] == ["Newest", "Middle", "Oldest"]


def test_create_album_playlists_sort_handles_mixed_date_precision() -> None:
    albums = [
        _album("a1", "Year Only", "2021"),
        _album("a2", "Full Date", "2021-06-15"),
        _album("a3", "Month Only", "2021-03"),
    ]
    created_order: list[str] = []

    def fake_urlopen(req: Any) -> Any:
        url = req.full_url if hasattr(req, "full_url") else str(req)
        if "users" in url:
            name = json.loads(req.data.decode())["name"]
            created_order.append(name)
            return _create_playlist_response("pid", name)
        return _tracks_page([])

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        create_album_playlists(_TOKEN, _USER_ID, albums, set())

    assert created_order == ["Full Date", "Month Only", "Year Only"]


def test_create_album_playlists_skips_albums_in_existing_names() -> None:
    albums = [
        _album("a1", "Existing", "2020-01-01"),
        _album("a2", "New One", "2021-01-01"),
    ]
    existing = {"Existing"}

    responses = [
        _create_playlist_response("p2", "New One"),
        _tracks_page([]),
    ]
    resp_iter = iter(responses)

    with patch("urllib.request.urlopen", side_effect=lambda _req: next(resp_iter)):
        result = create_album_playlists(_TOKEN, _USER_ID, albums, existing)

    assert len(result) == 1
    assert result[0].name == "New One"


def test_create_album_playlists_returns_empty_when_all_exist() -> None:
    albums = [
        _album("a1", "Already Here", "2020-01-01"),
    ]
    existing = {"Already Here"}

    with patch("urllib.request.urlopen") as mock_urlopen:
        result = create_album_playlists(_TOKEN, _USER_ID, albums, existing)

    mock_urlopen.assert_not_called()
    assert result == []


def test_create_album_playlists_returns_empty_for_empty_album_list() -> None:
    with patch("urllib.request.urlopen") as mock_urlopen:
        result = create_album_playlists(_TOKEN, _USER_ID, [], set())

    mock_urlopen.assert_not_called()
    assert result == []


def test_create_album_playlists_skips_track_add_for_album_with_no_tracks() -> None:
    albums = [_album("a1", "Silent Album", "2021-01-01")]
    create_calls: list[str] = []
    add_track_calls: list[str] = []

    def fake_urlopen(req: Any) -> Any:
        url = req.full_url if hasattr(req, "full_url") else str(req)
        if "users" in url:
            create_calls.append(url)
            return _create_playlist_response("p1", "Silent Album")
        if "albums" in url:
            return _tracks_page([])
        if "playlists" in url and req.data:
            add_track_calls.append(url)
            return _add_tracks_response()
        raise AssertionError(f"Unexpected URL: {url}")

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        result = create_album_playlists(_TOKEN, _USER_ID, albums, set())

    assert len(result) == 1
    assert result[0].name == "Silent Album"
    assert len(create_calls) == 1
    assert len(add_track_calls) == 0


def test_create_album_playlists_returns_only_newly_created() -> None:
    albums = [
        _album("a1", "Pre-existing", "2019-01-01"),
        _album("a2", "Brand New", "2022-05-01"),
        _album("a3", "Also Pre-existing", "2020-06-01"),
    ]
    existing = {"Pre-existing", "Also Pre-existing"}

    responses = [
        _create_playlist_response("p2", "Brand New"),
        _tracks_page([]),
    ]
    resp_iter = iter(responses)

    with patch("urllib.request.urlopen", side_effect=lambda _req: next(resp_iter)):
        result = create_album_playlists(_TOKEN, _USER_ID, albums, existing)

    assert len(result) == 1
    assert result[0].name == "Brand New"


# ---------------------------------------------------------------------------
# Group 3: prompt_for_folder is tested in test_folder_prompt.py
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Group 4: OAuth scope — covered in test_auth.py
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Group 5: fetch_album_track_uris
# ---------------------------------------------------------------------------


def test_fetch_album_track_uris_returns_all_uris() -> None:
    uris = ["spotify:track:t1", "spotify:track:t2", "spotify:track:t3"]
    with patch("urllib.request.urlopen", return_value=_tracks_page(uris)):
        result = fetch_album_track_uris(_TOKEN, "alb1")

    assert result == uris


def test_fetch_album_track_uris_follows_pagination() -> None:
    responses = [
        _tracks_page(
            ["spotify:track:t1", "spotify:track:t2"],
            next_url="https://api.spotify.com/v1/albums/alb1/tracks?offset=2",
        ),
        _tracks_page(["spotify:track:t3"], next_url=None),
    ]
    resp_iter = iter(responses)

    with patch("urllib.request.urlopen", side_effect=lambda _req: next(resp_iter)):
        result = fetch_album_track_uris(_TOKEN, "alb1")

    assert result == ["spotify:track:t1", "spotify:track:t2", "spotify:track:t3"]


def test_fetch_album_track_uris_returns_empty_for_no_tracks() -> None:
    with patch("urllib.request.urlopen", return_value=_tracks_page([])):
        result = fetch_album_track_uris(_TOKEN, "alb1")

    assert result == []


def test_fetch_album_track_uris_sends_auth_header() -> None:
    captured: list[urllib_request.Request] = []

    def capturing_urlopen(req: urllib_request.Request) -> Any:
        captured.append(req)
        return _tracks_page([])

    with patch("urllib.request.urlopen", side_effect=capturing_urlopen):
        fetch_album_track_uris(_TOKEN, "alb99")

    assert len(captured) == 1
    assert captured[0].get_header("Authorization") == "Bearer test_tok"
    assert "alb99" in captured[0].full_url


# ---------------------------------------------------------------------------
# Group 5: add_tracks_to_playlist
# ---------------------------------------------------------------------------


def test_add_tracks_to_playlist_does_nothing_for_empty_list() -> None:
    with patch("urllib.request.urlopen") as mock_urlopen:
        add_tracks_to_playlist(_TOKEN, "playlist1", [])

    mock_urlopen.assert_not_called()


def test_add_tracks_to_playlist_single_request_for_100_or_fewer() -> None:
    uris = [f"spotify:track:t{i}" for i in range(50)]

    with patch(
        "urllib.request.urlopen", return_value=_add_tracks_response()
    ) as mock_urlopen:
        add_tracks_to_playlist(_TOKEN, "playlist1", uris)

    assert mock_urlopen.call_count == 1
    sent_body = json.loads(mock_urlopen.call_args[0][0].data.decode())
    assert sent_body["uris"] == uris


def test_add_tracks_to_playlist_batches_over_100() -> None:
    uris = [f"spotify:track:t{i}" for i in range(150)]

    captured_batches: list[list[str]] = []

    def fake_urlopen(req: Any) -> Any:
        body = json.loads(req.data.decode())
        captured_batches.append(body["uris"])
        return _add_tracks_response()

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        add_tracks_to_playlist(_TOKEN, "playlist1", uris)

    assert len(captured_batches) == 2
    assert captured_batches[0] == uris[:100]
    assert captured_batches[1] == uris[100:]


# ---------------------------------------------------------------------------
# Group 5.6: create_album_playlists populates tracks before returning
# ---------------------------------------------------------------------------


def test_create_album_playlists_populates_tracks_before_returning() -> None:
    albums = [_album("a1", "Tracks Album", "2022-01-01")]
    existing: set[str] = set()
    track_uris = ["spotify:track:u1", "spotify:track:u2"]

    call_log: list[str] = []

    def fake_urlopen(req: Any) -> Any:
        url = req.full_url if hasattr(req, "full_url") else str(req)
        if "users" in url:
            call_log.append("create")
            return _create_playlist_response("pl1", "Tracks Album")
        if "albums" in url:
            call_log.append("fetch_tracks")
            return _tracks_page(track_uris)
        if "playlists" in url and req.data:
            call_log.append("add_tracks")
            return _add_tracks_response()
        raise AssertionError(f"Unexpected URL: {url}")

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        result = create_album_playlists(_TOKEN, _USER_ID, albums, existing)

    assert result[0].name == "Tracks Album"
    assert "create" in call_log
    assert "fetch_tracks" in call_log
    assert "add_tracks" in call_log
    assert call_log.index("create") < call_log.index("fetch_tracks")
    assert call_log.index("fetch_tracks") < call_log.index("add_tracks")
