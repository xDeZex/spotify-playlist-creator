from __future__ import annotations

import json
from typing import Any
from unittest.mock import patch

import spotify_playlist_creator.status as status
from spotify_playlist_creator.auth import SpotifyToken
from spotify_playlist_creator.classify_releases import (
    classify_releases,
    fetch_singles_durations,
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


def _make_albums_response(albums: list[dict[str, Any] | None]) -> Any:
    class _Response:
        def read(self) -> bytes:
            return json.dumps({"albums": albums}).encode()

        def __enter__(self) -> _Response:
            return self

        def __exit__(self, *args: Any) -> None:
            pass

    return _Response()


def _album_item(album_id: str, track_durations: list[int]) -> dict[str, Any]:
    return {
        "id": album_id,
        "tracks": {"items": [{"duration_ms": d} for d in track_durations]},
    }


# ---------------------------------------------------------------------------
# Group 1: fetch_singles_durations behaviour
# ---------------------------------------------------------------------------


def test_fetch_singles_durations_returns_durations_dict() -> None:
    # Two albums with different track counts — both must appear in the dict, separately
    response = _make_albums_response(
        [
            _album_item("alb1", [180_000, 240_000, 210_000]),
            _album_item("alb2", [120_000]),
        ]
    )
    with patch("urllib.request.urlopen", return_value=response):
        result = fetch_singles_durations(_VALID_TOKEN, ["alb1", "alb2"])
    assert result == {"alb1": [180_000, 240_000, 210_000], "alb2": [120_000]}


def test_fetch_singles_durations_makes_one_request_with_ids_param() -> None:
    # Three IDs — must be joined with commas in a single ?ids= call
    captured: list[Any] = []

    def capturing_urlopen(req: Any) -> Any:
        captured.append(req)
        return _make_albums_response(
            [_album_item("a1", []), _album_item("a2", []), _album_item("a3", [])]
        )

    with patch("urllib.request.urlopen", side_effect=capturing_urlopen):
        fetch_singles_durations(_VALID_TOKEN, ["a1", "a2", "a3"])

    assert len(captured) == 1
    assert "ids=a1,a2,a3" in captured[0].full_url
    assert captured[0].get_header("Authorization") == "Bearer test_access_token"


def test_fetch_singles_durations_zero_tracks_mapped_to_empty_list() -> None:
    # Album present in response but with no tracks — must appear in dict with []
    response = _make_albums_response([_album_item("alb1", [])])
    with patch("urllib.request.urlopen", return_value=response):
        result = fetch_singles_durations(_VALID_TOKEN, ["alb1"])
    assert result == {"alb1": []}


def test_fetch_singles_durations_null_album_skipped_silently() -> None:
    # null in the middle — only the two valid albums must appear; no error raised
    response = _make_albums_response(
        [
            _album_item("alb1", [180_000]),
            None,
            _album_item("alb3", [240_000, 210_000]),
        ]
    )
    with patch("urllib.request.urlopen", return_value=response):
        result = fetch_singles_durations(_VALID_TOKEN, ["alb1", "alb2", "alb3"])
    assert result == {"alb1": [180_000], "alb3": [240_000, 210_000]}
    assert "alb2" not in result


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
        return_value=_make_albums_response([_album_item("ep1", [5 * 60_000] * 5)]),
    ):
        result = classify_releases(_VALID_TOKEN, [raw])
    assert len(result) == 1 and result[0].id == "ep1"


def test_classify_ep_4_to_6_tracks_long_total_is_excluded() -> None:
    # 5 tracks, ~7 min each → total 35 min > 30 min → not EP → excluded
    raw = _raw(album_id="s1", album_type="single")
    with patch(
        "urllib.request.urlopen",
        return_value=_make_albums_response([_album_item("s1", [7 * 60_000] * 5)]),
    ):
        result = classify_releases(_VALID_TOKEN, [raw])
    assert result == []


def test_classify_ep_4_to_6_tracks_exactly_30_min_is_included() -> None:
    # 4 tracks × 7.5 min = exactly 30 min → ≤ 30 min → EP → included
    raw = _raw(album_id="ep2", album_type="single")
    with patch(
        "urllib.request.urlopen",
        return_value=_make_albums_response([_album_item("ep2", [450_000] * 4)]),
    ):
        result = classify_releases(_VALID_TOKEN, [raw])
    assert len(result) == 1 and result[0].id == "ep2"


def test_classify_ep_exactly_4_tracks_short_total_is_included() -> None:
    # 4 tracks, 5 min each → total 20 min ≤ 30 min → first EP rule applies → included
    # Guards the 4-track lower bound of rule 1 (4 ≤ tracks ≤ 6)
    raw = _raw(album_id="ep_4t", album_type="single")
    with patch(
        "urllib.request.urlopen",
        return_value=_make_albums_response([_album_item("ep_4t", [5 * 60_000] * 4)]),
    ):
        result = classify_releases(_VALID_TOKEN, [raw])
    assert len(result) == 1 and result[0].id == "ep_4t"


def test_classify_ep_exactly_3_tracks_short_total_no_long_track_is_excluded() -> None:
    # 3 tracks, 5 min each → doesn't meet rule 1 (needs ≥4) and doesn't meet rule 2
    # (needs one track >10 min) → excluded; guards the 3-vs-4 boundary
    raw = _raw(album_id="s_3t", album_type="single")
    with patch(
        "urllib.request.urlopen",
        return_value=_make_albums_response([_album_item("s_3t", [5 * 60_000] * 3)]),
    ):
        result = classify_releases(_VALID_TOKEN, [raw])
    assert result == []


def test_classify_ep_exactly_6_tracks_short_total_is_included() -> None:
    # 6 tracks, 5 min each → total 30 min ≤ 30 min → rule 1 applies → included
    # Guards the 6-track upper bound of rule 1 (4 ≤ tracks ≤ 6)
    raw = _raw(album_id="ep_6t", album_type="single")
    with patch(
        "urllib.request.urlopen",
        return_value=_make_albums_response([_album_item("ep_6t", [5 * 60_000] * 6)]),
    ):
        result = classify_releases(_VALID_TOKEN, [raw])
    assert len(result) == 1 and result[0].id == "ep_6t"


def test_classify_ep_1_to_3_tracks_one_long_track_long_total_is_included() -> None:
    # 2 tracks: one 20 min, one 15 min → total 35 min > 30 min, one > 10 min → EP
    raw = _raw(album_id="ep3", album_type="single")
    with patch(
        "urllib.request.urlopen",
        return_value=_make_albums_response(
            [_album_item("ep3", [20 * 60_000, 15 * 60_000])]
        ),
    ):
        result = classify_releases(_VALID_TOKEN, [raw])
    assert len(result) == 1 and result[0].id == "ep3"


def test_classify_ep_1_to_3_tracks_one_long_track_short_total_is_excluded() -> None:
    # 1 track: 11 min → one track > 10 min but total 11 min ≤ 30 min → not EP
    raw = _raw(album_id="s2", album_type="single")
    with patch(
        "urllib.request.urlopen",
        return_value=_make_albums_response([_album_item("s2", [11 * 60_000])]),
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
        return_value=_make_albums_response(
            [_album_item("s3", [11 * 60_000, 19 * 60_000])]
        ),
    ):
        result = classify_releases(_VALID_TOKEN, [raw])
    assert result == []


def test_classify_ep_1_to_3_tracks_no_long_track_is_excluded() -> None:
    # 3 tracks, all ≤ 10 min → not EP regardless of total
    raw = _raw(album_id="s4", album_type="single")
    with patch(
        "urllib.request.urlopen",
        return_value=_make_albums_response(
            [_album_item("s4", [8 * 60_000, 9 * 60_000, 7 * 60_000])]
        ),
    ):
        result = classify_releases(_VALID_TOKEN, [raw])
    assert result == []


def test_classify_ep_7_or_more_tracks_is_excluded() -> None:
    # 8 tracks, short total → track count alone disqualifies
    raw = _raw(album_id="s5", album_type="single")
    with patch(
        "urllib.request.urlopen",
        return_value=_make_albums_response([_album_item("s5", [3 * 60_000] * 8)]),
    ):
        result = classify_releases(_VALID_TOKEN, [raw])
    assert result == []


def test_classify_ep_zero_tracks_is_excluded() -> None:
    # batch response returns album with empty tracks → not an EP → excluded
    raw = _raw(album_id="s6", album_type="single")
    with patch(
        "urllib.request.urlopen",
        return_value=_make_albums_response([_album_item("s6", [])]),
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
    with patch(
        "urllib.request.urlopen",
        return_value=_make_albums_response([_album_item("ep1", [5 * 60_000] * 5)]),
    ):
        result = classify_releases(_VALID_TOKEN, [raw])
    assert len(result) == 1
    assert result[0].id == "ep1"


def test_classify_releases_single_not_qualifying_as_ep_is_excluded() -> None:
    # 1 track, 3 min → does not meet either EP rule
    raw = _raw(album_id="s1", album_type="single")
    with patch(
        "urllib.request.urlopen",
        return_value=_make_albums_response([_album_item("s1", [3 * 60_000])]),
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

    captured_urls: list[str] = []

    def capturing_urlopen(req: Any) -> Any:
        captured_urls.append(req.full_url)
        ids = req.full_url.split("ids=")[1].split(",")
        return _make_albums_response(
            [_album_item(aid, [5 * 60_000] * 5) for aid in ids]
        )

    with patch("urllib.request.urlopen", side_effect=capturing_urlopen):
        result = classify_releases(_VALID_TOKEN, [raw_album1, raw_ep, raw_album2])

    assert len(captured_urls) == 1  # one batch call for the single
    assert [r.id for r in result] == ["a1", "ep1", "a2"]


def test_classify_releases_batches_singles_in_groups_of_20() -> None:
    # 25 singles → must produce exactly 2 batch calls (20 then 5)
    singles = [_raw(album_id=f"s{i}", album_type="single") for i in range(25)]
    captured_urls: list[str] = []

    def capturing_urlopen(req: Any) -> Any:
        captured_urls.append(req.full_url)
        ids = req.full_url.split("ids=")[1].split(",")
        return _make_albums_response([_album_item(aid, [3 * 60_000]) for aid in ids])

    with patch("urllib.request.urlopen", side_effect=capturing_urlopen):
        classify_releases(_VALID_TOKEN, singles)

    assert len(captured_urls) == 2
    assert len(captured_urls[0].split("ids=")[1].split(",")) == 20
    assert len(captured_urls[1].split("ids=")[1].split(",")) == 5


# ---------------------------------------------------------------------------
# Task 5.2: classify_releases writes per-single progress
# ---------------------------------------------------------------------------


def test_classify_releases_writes_progress_per_batch() -> None:
    received: list[str] = []
    status.configure(received.append)

    # 25 singles mixed with an album → 2 batches (20 then 5); progress written once per batch
    raw_album = _raw(album_id="a1", album_type="album")
    raw_singles = [_raw(album_id=f"s{i}", album_type="single") for i in range(25)]

    def side_effect(req: Any) -> Any:
        ids = req.full_url.split("ids=")[1].split(",")
        return _make_albums_response([_album_item(aid, [3 * 60_000]) for aid in ids])

    with patch("urllib.request.urlopen", side_effect=side_effect):
        classify_releases(_VALID_TOKEN, [raw_album, *raw_singles])

    assert "\r\033[2Kclassifying singles (20/25)..." in received
    assert "\r\033[2Kclassifying singles (25/25)..." in received
    assert len([m for m in received if "classifying singles" in m]) == 2


def test_classify_releases_no_progress_when_no_singles() -> None:
    received: list[str] = []
    status.configure(received.append)

    raw_albums = [_raw(album_id=f"a{i}", album_type="album") for i in range(3)]
    classify_releases(_VALID_TOKEN, raw_albums)

    assert not any("classifying singles" in msg for msg in received)
