from __future__ import annotations

import io
import json
import urllib.error
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

import spotify_playlist_creator.status as status
from spotify_playlist_creator.auth import SpotifyToken
from spotify_playlist_creator.classify_releases import (
    classify_releases,
    fetch_album_tracks,
)
from spotify_playlist_creator.models import Album, RawRelease

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


def _make_tracks_response(
    items: list[dict[str, Any]], next_url: str | None = None
) -> Any:
    class _Response:
        def read(self) -> bytes:
            return json.dumps({"items": items, "next": next_url}).encode()

        def __enter__(self) -> _Response:
            return self

        def __exit__(self, *args: Any) -> None:
            pass

    return _Response()


def _track_item(duration_ms: int) -> dict[str, Any]:
    return {"duration_ms": duration_ms}


# ---------------------------------------------------------------------------
# Group 2: fetch_album_tracks behaviour
# ---------------------------------------------------------------------------


def test_fetch_album_tracks_raises_for_empty_token() -> None:
    with patch("urllib.request.urlopen") as mock_urlopen:
        with pytest.raises(ValueError):
            fetch_album_tracks(_EMPTY_TOKEN, "alb1")
    mock_urlopen.assert_not_called()


def test_fetch_album_tracks_calls_correct_endpoint() -> None:
    captured: list[Any] = []

    def capturing_urlopen(req: Any) -> Any:
        captured.append(req)
        return _make_tracks_response([])

    with patch("urllib.request.urlopen", side_effect=capturing_urlopen):
        fetch_album_tracks(_VALID_TOKEN, "alb123")

    assert len(captured) == 1
    assert "albums/alb123/tracks" in captured[0].full_url
    assert captured[0].get_header("Authorization") == "Bearer test_access_token"


def test_fetch_album_tracks_returns_durations_single_page() -> None:
    items = [_track_item(180_000), _track_item(240_000), _track_item(210_000)]
    with patch("urllib.request.urlopen", return_value=_make_tracks_response(items)):
        result = fetch_album_tracks(_VALID_TOKEN, "alb1")

    assert result == [180_000, 240_000, 210_000]


def test_fetch_album_tracks_follows_pagination() -> None:
    page1 = [_track_item(180_000), _track_item(200_000)]
    page2 = [_track_item(220_000)]

    responses = [
        _make_tracks_response(
            page1,
            next_url="https://api.spotify.com/v1/albums/alb1/tracks?offset=2",
        ),
        _make_tracks_response(page2, next_url=None),
    ]
    response_iter = iter(responses)
    captured: list[Any] = []

    def capturing_urlopen(req: Any) -> Any:
        captured.append(req)
        return next(response_iter)

    with patch("urllib.request.urlopen", side_effect=capturing_urlopen):
        result = fetch_album_tracks(_VALID_TOKEN, "alb1")

    assert result == [180_000, 200_000, 220_000]
    assert len(captured) == 2
    for req in captured:
        assert req.get_header("Authorization") == "Bearer test_access_token"


def test_fetch_album_tracks_retries_on_429_with_retry_after() -> None:
    call_count = [0]
    items = [_track_item(120_000)]

    def flaky_urlopen(_req: Any) -> Any:
        call_count[0] += 1
        if call_count[0] == 1:
            hdrs: MagicMock = MagicMock()
            hdrs.get = lambda key, default=None: (
                "1" if key == "Retry-After" else default
            )
            raise urllib.error.HTTPError(
                url="https://api.spotify.com/v1/albums/alb1/tracks",
                code=429,
                msg="Too Many Requests",
                hdrs=hdrs,
                fp=io.BytesIO(b"{}"),
            )
        return _make_tracks_response(items)

    with patch("urllib.request.urlopen", side_effect=flaky_urlopen):
        with patch("time.sleep"):
            result = fetch_album_tracks(_VALID_TOKEN, "alb1")

    assert result == [120_000]
    assert call_count[0] == 2


# ---------------------------------------------------------------------------
# Shared helpers for classify_releases tests
# ---------------------------------------------------------------------------


def _raw(
    album_id: str = "alb1",
    name: str = "Album",
    album_type: str = "album",
    release_date: str = "2021-01-01",
) -> RawRelease:
    return RawRelease(
        id=album_id,
        name=name,
        album_type=album_type,
        release_date=release_date,
    )


# ---------------------------------------------------------------------------
# Group 3: EP classification rules (via classify_releases)
# ---------------------------------------------------------------------------


def test_classify_ep_4_to_6_tracks_short_total_is_included() -> None:
    # 5 tracks, ~5 min each → total 25 min ≤ 30 min → EP → included
    raw = _raw(album_id="ep1", album_type="single")
    with patch(
        "urllib.request.urlopen",
        return_value=_make_tracks_response([_track_item(5 * 60_000)] * 5),
    ):
        result = classify_releases(_VALID_TOKEN, [raw])
    assert len(result) == 1 and result[0].id == "ep1"


def test_classify_ep_4_to_6_tracks_long_total_is_excluded() -> None:
    # 5 tracks, ~7 min each → total 35 min > 30 min → not EP → excluded
    raw = _raw(album_id="s1", album_type="single")
    with patch(
        "urllib.request.urlopen",
        return_value=_make_tracks_response([_track_item(7 * 60_000)] * 5),
    ):
        result = classify_releases(_VALID_TOKEN, [raw])
    assert result == []


def test_classify_ep_4_to_6_tracks_exactly_30_min_is_included() -> None:
    # 4 tracks × 7.5 min = exactly 30 min → ≤ 30 min → EP → included
    raw = _raw(album_id="ep2", album_type="single")
    with patch(
        "urllib.request.urlopen",
        return_value=_make_tracks_response([_track_item(450_000)] * 4),
    ):
        result = classify_releases(_VALID_TOKEN, [raw])
    assert len(result) == 1 and result[0].id == "ep2"


def test_classify_ep_1_to_3_tracks_one_long_track_long_total_is_included() -> None:
    # 2 tracks: one 20 min, one 15 min → total 35 min > 30 min, one > 10 min → EP
    raw = _raw(album_id="ep3", album_type="single")
    with patch(
        "urllib.request.urlopen",
        return_value=_make_tracks_response(
            [_track_item(20 * 60_000), _track_item(15 * 60_000)]
        ),
    ):
        result = classify_releases(_VALID_TOKEN, [raw])
    assert len(result) == 1 and result[0].id == "ep3"


def test_classify_ep_1_to_3_tracks_one_long_track_short_total_is_excluded() -> None:
    # 1 track: 11 min → one track > 10 min but total 11 min ≤ 30 min → not EP
    raw = _raw(album_id="s2", album_type="single")
    with patch(
        "urllib.request.urlopen",
        return_value=_make_tracks_response([_track_item(11 * 60_000)]),
    ):
        result = classify_releases(_VALID_TOKEN, [raw])
    assert result == []


def test_classify_ep_1_to_3_tracks_one_long_track_total_exactly_30_min_is_excluded() -> (
    None
):
    # 2 tracks: 11 min + 19 min = exactly 30 min → not strictly > 30 min → not EP
    raw = _raw(album_id="s3", album_type="single")
    with patch(
        "urllib.request.urlopen",
        return_value=_make_tracks_response(
            [_track_item(11 * 60_000), _track_item(19 * 60_000)]
        ),
    ):
        result = classify_releases(_VALID_TOKEN, [raw])
    assert result == []


def test_classify_ep_1_to_3_tracks_no_long_track_is_excluded() -> None:
    # 3 tracks, all ≤ 10 min → not EP regardless of total
    raw = _raw(album_id="s4", album_type="single")
    with patch(
        "urllib.request.urlopen",
        return_value=_make_tracks_response(
            [_track_item(8 * 60_000), _track_item(9 * 60_000), _track_item(7 * 60_000)]
        ),
    ):
        result = classify_releases(_VALID_TOKEN, [raw])
    assert result == []


def test_classify_ep_7_or_more_tracks_is_excluded() -> None:
    # 8 tracks, short total → track count alone disqualifies
    raw = _raw(album_id="s5", album_type="single")
    with patch(
        "urllib.request.urlopen",
        return_value=_make_tracks_response([_track_item(3 * 60_000)] * 8),
    ):
        result = classify_releases(_VALID_TOKEN, [raw])
    assert result == []


def test_classify_ep_zero_tracks_is_excluded() -> None:
    # tracks endpoint returns no items → not an EP → excluded
    raw = _raw(album_id="s6", album_type="single")
    with patch(
        "urllib.request.urlopen",
        return_value=_make_tracks_response([]),
    ):
        result = classify_releases(_VALID_TOKEN, [raw])
    assert result == []


# ---------------------------------------------------------------------------
# Group 4: classify_releases orchestration
# ---------------------------------------------------------------------------


def test_classify_releases_album_type_included_without_track_fetch() -> None:
    raw = _raw(album_id="a1", album_type="album")
    with patch("urllib.request.urlopen") as mock_urlopen:
        result = classify_releases(_VALID_TOKEN, [raw])
    mock_urlopen.assert_not_called()
    assert len(result) == 1
    assert result[0].id == "a1"


def test_classify_releases_single_qualifying_as_ep_is_included() -> None:
    # 5 tracks, 5 min each → 25 min total → qualifies as EP
    raw = _raw(album_id="ep1", album_type="single")
    track_items = [_track_item(5 * 60_000)] * 5
    with patch(
        "urllib.request.urlopen", return_value=_make_tracks_response(track_items)
    ):
        result = classify_releases(_VALID_TOKEN, [raw])
    assert len(result) == 1
    assert result[0].id == "ep1"


def test_classify_releases_single_not_qualifying_as_ep_is_excluded() -> None:
    # 1 track, 3 min → does not meet either EP rule
    raw = _raw(album_id="s1", album_type="single")
    track_items = [_track_item(3 * 60_000)]
    with patch(
        "urllib.request.urlopen", return_value=_make_tracks_response(track_items)
    ):
        result = classify_releases(_VALID_TOKEN, [raw])
    assert result == []


def test_classify_releases_compilation_excluded_without_track_fetch() -> None:
    raw = _raw(album_id="c1", album_type="compilation")
    with patch("urllib.request.urlopen") as mock_urlopen:
        result = classify_releases(_VALID_TOKEN, [raw])
    mock_urlopen.assert_not_called()
    assert result == []


def test_classify_releases_empty_input_returns_empty() -> None:
    result = classify_releases(_VALID_TOKEN, [])
    assert result == []


def test_classify_releases_output_preserves_id_name_release_date() -> None:
    raw = _raw(
        album_id="a1", name="Great Album", album_type="album", release_date="2020-03"
    )
    result = classify_releases(_VALID_TOKEN, [raw])
    assert result[0] == Album(id="a1", name="Great Album", release_date="2020-03")


def test_classify_releases_output_order_matches_input_order() -> None:
    # album, ep-qualifying single, another album
    raw_album1 = _raw(album_id="a1", album_type="album", release_date="2019-01-01")
    raw_ep = _raw(album_id="ep1", album_type="single", release_date="2020-06-01")
    raw_album2 = _raw(album_id="a2", album_type="album", release_date="2021-03-01")

    ep_tracks = [_track_item(5 * 60_000)] * 5
    call_count = 0

    def side_effect(req: Any) -> Any:
        nonlocal call_count
        call_count += 1
        return _make_tracks_response(ep_tracks)

    with patch("urllib.request.urlopen", side_effect=side_effect):
        result = classify_releases(_VALID_TOKEN, [raw_album1, raw_ep, raw_album2])

    assert call_count == 1  # only the single/EP triggers a fetch; albums do not
    assert [r.id for r in result] == ["a1", "ep1", "a2"]


# ---------------------------------------------------------------------------
# Task 5.2: classify_releases writes per-single progress
# ---------------------------------------------------------------------------


def test_classify_releases_writes_progress_for_each_single() -> None:
    received: list[str] = []
    status.configure(received.append)

    # Adversarial: 3 singles mixed with albums; progress must count only singles
    raw_album = _raw(album_id="a1", album_type="album")
    raw_singles = [_raw(album_id=f"s{i}", album_type="single") for i in range(1, 4)]
    ep_tracks = [_track_item(5 * 60_000)] * 5  # qualifies as EP

    with patch(
        "urllib.request.urlopen",
        return_value=_make_tracks_response(ep_tracks),
    ):
        classify_releases(_VALID_TOKEN, [raw_album, *raw_singles])

    assert "\r\033[2Kclassifying singles (1/3)..." in received
    assert "\r\033[2Kclassifying singles (2/3)..." in received
    assert "\r\033[2Kclassifying singles (3/3)..." in received


def test_classify_releases_no_progress_when_no_singles() -> None:
    received: list[str] = []
    status.configure(received.append)

    raw_albums = [_raw(album_id=f"a{i}", album_type="album") for i in range(3)]
    classify_releases(_VALID_TOKEN, raw_albums)

    assert not any("classifying singles" in msg for msg in received)
