from __future__ import annotations

import inspect
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
    fetch_first_track_album_id,
    fetch_user_playlists,
    find_missing_album_playlists,
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


def _playlist_page_with_ids(
    entries: list[tuple[str, str]], next_url: str | None = None
) -> Any:
    class _Response:
        def read(self) -> bytes:
            return json.dumps(
                {
                    "items": [{"name": n, "id": pid} for n, pid in entries],
                    "next": next_url,
                }
            ).encode()

        def __enter__(self) -> _Response:
            return self

        def __exit__(self, *args: Any) -> None:
            pass

    return _Response()


def _first_track_response(album_id: str | None) -> Any:
    class _Response:
        def read(self) -> bytes:
            if album_id is None:
                body: dict[str, Any] = {"items": []}
            else:
                body = {"items": [{"track": {"album": {"id": album_id}}}]}
            return json.dumps(body).encode()

        def __enter__(self) -> _Response:
            return self

        def __exit__(self, *args: Any) -> None:
            pass

    return _Response()


def _album(album_id: str, name: str, release_date: str) -> Album:
    return Album(id=album_id, name=name, release_date=release_date)


def test_fetch_album_track_uris_raises_for_empty_token() -> None:
    with patch("urllib.request.urlopen") as mock_urlopen:
        with pytest.raises(ValueError):
            fetch_album_track_uris(_EMPTY_TOKEN, "alb1")
    mock_urlopen.assert_not_called()


# ---------------------------------------------------------------------------
# Group 1a: fetch_user_playlists — name-to-IDs map
# ---------------------------------------------------------------------------


def test_fetch_user_playlists_returns_name_to_ids_map() -> None:
    with patch(
        "urllib.request.urlopen",
        return_value=_playlist_page_with_ids(
            [("Alpha", "id1"), ("Beta", "id2"), ("Gamma", "id3")]
        ),
    ):
        result = fetch_user_playlists(_TOKEN)

    assert result == {"Alpha": ["id1"], "Beta": ["id2"], "Gamma": ["id3"]}


def test_fetch_user_playlists_raises_for_empty_token() -> None:
    with patch("urllib.request.urlopen") as mock_urlopen:
        with pytest.raises(ValueError):
            fetch_user_playlists(_EMPTY_TOKEN)
    mock_urlopen.assert_not_called()


def test_fetch_user_playlists_sends_auth_header() -> None:
    captured: list[urllib_request.Request] = []

    def capturing_urlopen(req: urllib_request.Request) -> Any:
        captured.append(req)
        return _playlist_page_with_ids([])

    with patch("urllib.request.urlopen", side_effect=capturing_urlopen):
        fetch_user_playlists(_TOKEN)

    assert len(captured) == 1
    assert captured[0].get_header("Authorization") == "Bearer test_tok"


def test_fetch_user_playlists_returns_empty_for_no_playlists() -> None:
    with patch("urllib.request.urlopen", return_value=_playlist_page_with_ids([])):
        result = fetch_user_playlists(_TOKEN)

    assert result == {}


def test_fetch_user_playlists_collects_duplicate_names_into_same_bucket() -> None:
    with patch(
        "urllib.request.urlopen",
        return_value=_playlist_page_with_ids(
            [("Self Titled", "pid1"), ("Other", "pid2"), ("Self Titled", "pid3")]
        ),
    ):
        result = fetch_user_playlists(_TOKEN)

    assert result["Self Titled"] == ["pid1", "pid3"]
    assert result["Other"] == ["pid2"]


def test_fetch_user_playlists_follows_pagination() -> None:
    responses = [
        _playlist_page_with_ids(
            [("Alpha", "id1"), ("Beta", "id2")],
            next_url="https://api.spotify.com/v1/me/playlists?offset=50",
        ),
        _playlist_page_with_ids([("Gamma", "id3")], next_url=None),
    ]
    resp_iter = iter(responses)

    with patch("urllib.request.urlopen", side_effect=lambda _req: next(resp_iter)):
        result = fetch_user_playlists(_TOKEN)

    assert result == {"Alpha": ["id1"], "Beta": ["id2"], "Gamma": ["id3"]}


# ---------------------------------------------------------------------------
# Group 1b: fetch_first_track_album_id — fingerprinting helper
# ---------------------------------------------------------------------------


def test_fetch_first_track_album_id_returns_album_id_of_first_track() -> None:
    with patch(
        "urllib.request.urlopen",
        return_value=_first_track_response("album_abc"),
    ):
        result = fetch_first_track_album_id(_TOKEN, "playlist_xyz")

    assert result == "album_abc"


def test_fetch_first_track_album_id_raises_for_empty_token() -> None:
    with patch("urllib.request.urlopen") as mock_urlopen:
        with pytest.raises(ValueError):
            fetch_first_track_album_id(_EMPTY_TOKEN, "playlist_xyz")
    mock_urlopen.assert_not_called()


def test_fetch_first_track_album_id_sends_auth_header_with_limit_1() -> None:
    captured: list[urllib_request.Request] = []

    def capturing_urlopen(req: urllib_request.Request) -> Any:
        captured.append(req)
        return _first_track_response("alb1")

    with patch("urllib.request.urlopen", side_effect=capturing_urlopen):
        fetch_first_track_album_id(_TOKEN, "pl1")

    assert len(captured) == 1
    assert captured[0].get_header("Authorization") == "Bearer test_tok"
    assert "pl1" in captured[0].full_url
    assert "limit=1" in captured[0].full_url


def test_fetch_first_track_album_id_returns_none_for_empty_playlist() -> None:
    with patch(
        "urllib.request.urlopen",
        return_value=_first_track_response(None),
    ):
        result = fetch_first_track_album_id(_TOKEN, "empty_playlist")

    assert result is None


# ---------------------------------------------------------------------------
# Group 2: create_album_playlists — create and skip logic
# ---------------------------------------------------------------------------


def test_create_album_playlists_creates_playlist_for_each_new_album() -> None:
    albums = [
        _album("a1", "Album One", "2021-06-15"),
        _album("a2", "Album Two", "2020-01-01"),
    ]
    responses = [
        _create_playlist_response("p1", "Album One"),
        _tracks_page([]),
        _create_playlist_response("p2", "Album Two"),
        _tracks_page([]),
    ]
    resp_iter = iter(responses)

    with patch("urllib.request.urlopen", side_effect=lambda _req: next(resp_iter)):
        result = create_album_playlists(_TOKEN, albums)

    assert len(result) == 2
    assert {r.name for r in result} == {"Album One", "Album Two"}


def test_create_album_playlists_returns_empty_for_empty_album_list() -> None:
    with patch("urllib.request.urlopen") as mock_urlopen:
        result = create_album_playlists(_TOKEN, [])

    mock_urlopen.assert_not_called()
    assert result == []


def test_create_album_playlists_skips_track_add_for_album_with_no_tracks() -> None:
    albums = [_album("a1", "Silent Album", "2021-01-01")]
    create_calls: list[str] = []
    add_track_calls: list[str] = []

    def fake_urlopen(req: Any) -> Any:
        url = req.full_url if hasattr(req, "full_url") else str(req)
        if "/me/playlists" in url:
            create_calls.append(url)
            return _create_playlist_response("p1", "Silent Album")
        if "albums" in url:
            return _tracks_page([])
        if "playlists" in url and req.data:
            add_track_calls.append(url)
            return _add_tracks_response()
        raise AssertionError(f"Unexpected URL: {url}")

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        result = create_album_playlists(_TOKEN, albums)

    assert len(result) == 1
    assert result[0].name == "Silent Album"
    assert len(create_calls) == 1
    assert len(add_track_calls) == 0


def test_create_album_playlists_posts_to_me_playlists_endpoint() -> None:
    albums = [_album("a1", "My Album", "2022-05-01")]
    captured: list[urllib_request.Request] = []

    def capturing_urlopen(req: urllib_request.Request) -> Any:
        captured.append(req)
        if "albums/" in req.full_url:
            return _tracks_page([])
        return _create_playlist_response("pl1", "My Album")

    with patch("urllib.request.urlopen", side_effect=capturing_urlopen):
        create_album_playlists(_TOKEN, albums)

    assert "user_id" not in inspect.signature(create_album_playlists).parameters
    assert "/me/playlists" in captured[0].full_url
    assert "/users/" not in captured[0].full_url


# ---------------------------------------------------------------------------
# Group 3: find_missing_album_playlists — collision-aware dedup
# ---------------------------------------------------------------------------


def test_find_missing_album_playlists_checks_all_same_named_playlists() -> None:
    # Adversarial: two playlists, neither matches — verifies both are checked
    album = _album("a1", "Self Titled", "2023-01-01")
    existing: dict[str, list[str]] = {"Self Titled": ["pid1", "pid2"]}
    fingerprint_calls: list[str] = []

    def fake_fingerprint(_tok: SpotifyToken, pid: str) -> str | None:
        fingerprint_calls.append(pid)
        return "other_album_id"

    with patch(
        "spotify_playlist_creator.create_playlists.fetch_first_track_album_id",
        side_effect=fake_fingerprint,
    ):
        result = find_missing_album_playlists(_TOKEN, [album], existing)

    assert fingerprint_calls == ["pid1", "pid2"]
    assert result == [album]


# ---------------------------------------------------------------------------
# Group 3b: find_missing_album_playlists — planning step
# ---------------------------------------------------------------------------


def test_find_missing_album_playlists_raises_for_empty_token() -> None:
    with patch("urllib.request.urlopen") as mock_urlopen:
        with pytest.raises(ValueError):
            find_missing_album_playlists(_EMPTY_TOKEN, [], {})
    mock_urlopen.assert_not_called()


def test_find_missing_album_playlists_returns_empty_for_empty_input() -> None:
    with patch("urllib.request.urlopen") as mock_urlopen:
        result = find_missing_album_playlists(_TOKEN, [], {})
    mock_urlopen.assert_not_called()
    assert result == []


def test_find_missing_album_playlists_returns_all_sorted_desc_when_no_existing() -> (
    None
):
    # Adversarial: input is ascending order; output must be descending
    albums = [
        _album("a1", "Oldest", "2019-01-01"),
        _album("a2", "Newest", "2023-06-01"),
        _album("a3", "Middle", "2021-03-15"),
    ]
    with patch("urllib.request.urlopen") as mock_urlopen:
        result = find_missing_album_playlists(_TOKEN, albums, {})
    mock_urlopen.assert_not_called()
    assert result == [
        _album("a2", "Newest", "2023-06-01"),
        _album("a3", "Middle", "2021-03-15"),
        _album("a1", "Oldest", "2019-01-01"),
    ]


def test_find_missing_album_playlists_excludes_album_with_matching_fingerprint() -> (
    None
):
    # Adversarial: both albums present but only one has a match
    albums = [
        _album("a1", "Existing", "2021-01-01"),
        _album("a2", "New", "2022-01-01"),
    ]
    existing: dict[str, list[str]] = {"Existing": ["pid1"]}
    with patch(
        "spotify_playlist_creator.create_playlists.fetch_first_track_album_id",
        return_value="a1",
    ):
        result = find_missing_album_playlists(_TOKEN, albums, existing)
    assert result == [_album("a2", "New", "2022-01-01")]


def test_find_missing_album_playlists_returns_empty_when_all_have_matching_playlists() -> (
    None
):
    albums = [_album("a1", "Present", "2020-06-01")]
    existing: dict[str, list[str]] = {"Present": ["pid1"]}
    with patch(
        "spotify_playlist_creator.create_playlists.fetch_first_track_album_id",
        return_value="a1",
    ):
        result = find_missing_album_playlists(_TOKEN, albums, existing)
    assert result == []


def test_find_missing_album_playlists_includes_album_when_fingerprint_differs() -> None:
    album = _album("a1", "Self Titled", "2023-01-01")
    existing: dict[str, list[str]] = {"Self Titled": ["pid_other"]}
    with patch(
        "spotify_playlist_creator.create_playlists.fetch_first_track_album_id",
        return_value="other_album_id",
    ):
        result = find_missing_album_playlists(_TOKEN, [album], existing)
    assert result == [album]


def test_find_missing_album_playlists_includes_album_for_empty_playlist() -> None:
    album = _album("a1", "Self Titled", "2023-01-01")
    existing: dict[str, list[str]] = {"Self Titled": ["empty_pid"]}
    with patch(
        "spotify_playlist_creator.create_playlists.fetch_first_track_album_id",
        return_value=None,
    ):
        result = find_missing_album_playlists(_TOKEN, [album], existing)
    assert result == [album]


def test_find_missing_album_playlists_excludes_when_second_of_two_playlists_matches() -> (
    None
):
    # Adversarial: two playlists — first doesn't match, second does
    album = _album("a1", "Self Titled", "2023-01-01")
    existing: dict[str, list[str]] = {"Self Titled": ["pid_no_match", "pid_match"]}
    fingerprint_map = {"pid_no_match": "other_id", "pid_match": "a1"}
    with patch(
        "spotify_playlist_creator.create_playlists.fetch_first_track_album_id",
        side_effect=lambda _tok, pid: fingerprint_map[pid],
    ):
        result = find_missing_album_playlists(_TOKEN, [album], existing)
    assert result == []


def test_find_missing_album_playlists_sort_handles_mixed_date_precision() -> None:
    # Adversarial: input ordered differently from expected descending output
    albums = [
        _album("a1", "Year Only", "2021"),
        _album("a3", "Month Only", "2021-03"),
        _album("a2", "Full Date", "2021-06-15"),
    ]
    with patch("urllib.request.urlopen") as mock_urlopen:
        result = find_missing_album_playlists(_TOKEN, albums, {})
    mock_urlopen.assert_not_called()
    assert [a.name for a in result] == ["Full Date", "Month Only", "Year Only"]


# ---------------------------------------------------------------------------
# Group 3c: create_album_playlists execute step — new 2-arg signature
# ---------------------------------------------------------------------------


def test_create_album_playlists_creates_all_pre_filtered_albums_in_order() -> None:
    # Execute step trusts input is pre-filtered; processes all albums in order given
    # Adversarial: input is oldest-first so we can verify order is preserved
    albums = [
        _album("a1", "Oldest", "2019-01-01"),
        _album("a2", "Newest", "2023-06-01"),
    ]
    created_order: list[str] = []

    def fake_urlopen(req: Any) -> Any:
        url = req.full_url if hasattr(req, "full_url") else str(req)
        if "/me/playlists" in url:
            name = json.loads(req.data.decode())["name"]
            created_order.append(name)
            return _create_playlist_response("pid", name)
        return _tracks_page([])

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        result = create_album_playlists(_TOKEN, albums)

    assert [r.name for r in result] == ["Oldest", "Newest"]
    assert created_order == ["Oldest", "Newest"]


# ---------------------------------------------------------------------------
# Group 4: prompt_for_folder is tested in test_folder_prompt.py
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
    track_uris = ["spotify:track:u1", "spotify:track:u2"]

    call_log: list[str] = []

    def fake_urlopen(req: Any) -> Any:
        url = req.full_url if hasattr(req, "full_url") else str(req)
        if "/me/playlists" in url:
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
        result = create_album_playlists(_TOKEN, albums)

    assert result[0].name == "Tracks Album"
    assert "create" in call_log
    assert "fetch_tracks" in call_log
    assert "add_tracks" in call_log
    assert call_log.index("create") < call_log.index("fetch_tracks")
    assert call_log.index("fetch_tracks") < call_log.index("add_tracks")
