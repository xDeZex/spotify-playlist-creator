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


# ---------------------------------------------------------------------------
# Group 3: limit parameter — signature and backward compatibility
# ---------------------------------------------------------------------------


def test_fetch_saved_albums_accepts_limit_keyword_arg() -> None:
    """fetch_saved_albums(token, limit=N) must not raise TypeError."""
    items = [
        _album_item("id1", "A1", ["Artist A"], added_at="2023-01-01T00:00:00Z"),
        _album_item("id2", "A2", ["Artist B"], added_at="2023-02-01T00:00:00Z"),
        _album_item("id3", "A3", ["Artist C"], added_at="2023-03-01T00:00:00Z"),
    ]
    with patch(
        "urllib.request.urlopen",
        return_value=_make_response(items, total=3, limit=50),
    ):
        result = fetch_saved_albums(_VALID_TOKEN, limit=2)
    assert [r.id for r in result] == ["id1", "id2", "id3"]


# ---------------------------------------------------------------------------
# Group 4: probe call behaviour (tasks 2.1, 2.2, 2.3)
# ---------------------------------------------------------------------------


def test_fetch_saved_albums_limit_first_call_is_probe_at_offset_zero() -> None:
    """When limit is set and total > 50, the first request must be offset=0."""
    captured_urls: list[str] = []

    def side_effect(req: urllib.request.Request) -> Any:
        captured_urls.append(req.full_url)
        # Probe: total=100 (2 pages).  Backward page: just one album.
        if not captured_urls or len(captured_urls) == 1:
            return _make_response(
                [
                    _album_item(
                        "newest",
                        "Newest",
                        ["Artist X"],
                        added_at="2024-12-01T00:00:00Z",
                    )
                ],
                total=100,
                limit=50,
            )
        return _make_response(
            [
                _album_item(
                    "oldest", "Oldest", ["Artist Y"], added_at="2023-01-01T00:00:00Z"
                )
            ],
            total=100,
            limit=50,
        )

    with patch("urllib.request.urlopen", side_effect=side_effect):
        fetch_saved_albums(_VALID_TOKEN, limit=1)

    assert "offset=" not in captured_urls[0] or "offset=0" in captured_urls[0]


def test_fetch_saved_albums_limit_single_page_returns_probe_only() -> None:
    """When total <= 50, probe items are returned directly; no further requests."""
    probe_items = [
        _album_item("id1", "A1", ["Artist A"], added_at="2023-01-01T00:00:00Z"),
        _album_item("id2", "A2", ["Artist B"], added_at="2023-06-01T00:00:00Z"),
    ]
    call_count = [0]

    def side_effect(_req: Any) -> Any:
        call_count[0] += 1
        return _make_response(probe_items, total=2, limit=50)

    with patch("urllib.request.urlopen", side_effect=side_effect):
        result = fetch_saved_albums(_VALID_TOKEN, limit=2)

    assert call_count[0] == 1
    assert [r.id for r in result] == ["id1", "id2"]


def test_fetch_saved_albums_limit_empty_library_returns_empty() -> None:
    """When total == 0, return [] immediately after the probe."""
    call_count = [0]

    def side_effect(_req: Any) -> Any:
        call_count[0] += 1
        return _make_response([], total=0, limit=50)

    with patch("urllib.request.urlopen", side_effect=side_effect):
        result = fetch_saved_albums(_VALID_TOKEN, limit=4)

    assert result == []
    assert call_count[0] == 1


# ---------------------------------------------------------------------------
# Group 5: backward pagination stops early (tasks 3.1, 3.2, 3.3)
# ---------------------------------------------------------------------------


def test_fetch_saved_albums_limit_stops_after_last_page_when_sufficient() -> None:
    """When the last page has >= N distinct primary artists, no earlier pages are fetched."""
    # Library: 100 albums across 2 pages. Last page (offset=50) has 2 distinct artists.
    # limit=1 → must stop after fetching last page only (no page at offset=0 beyond probe).
    probe = [
        _album_item("new1", "Newest", ["Artist X"], added_at="2024-06-01T00:00:00Z"),
    ]
    last_page = [
        _album_item("old1", "Oldest1", ["Artist A"], added_at="2023-01-01T00:00:00Z"),
        _album_item("old2", "Oldest2", ["Artist B"], added_at="2023-02-01T00:00:00Z"),
    ]
    captured_urls: list[str] = []

    def side_effect(req: urllib.request.Request) -> Any:
        captured_urls.append(req.full_url)
        if len(captured_urls) == 1:
            return _make_response(probe, total=100, limit=50)
        return _make_response(last_page, total=100, limit=50)

    with patch("urllib.request.urlopen", side_effect=side_effect):
        result = fetch_saved_albums(_VALID_TOKEN, limit=2)

    # Only 2 calls: probe + last page — must not fetch offset=0 again as backward page.
    assert len(captured_urls) == 2
    assert "offset=50" in captured_urls[1]
    assert len({r.artists[0].id for r in result if r.artists}) >= 2


def test_fetch_saved_albums_limit_fetches_additional_pages_when_needed() -> None:
    """When last page alone isn't enough, additional pages are fetched in decreasing offset order."""
    # 3 pages (150 items). Last page has 1 artist. Second-to-last has another. limit=2.
    probe = [
        _album_item("p1n", "Newest", ["Artist Z"], added_at="2024-06-01T00:00:00Z")
    ]
    page_at_100 = [
        _album_item("p100", "Old1", ["Artist A"], added_at="2023-01-01T00:00:00Z")
    ]
    page_at_50 = [
        _album_item("p50", "Old2", ["Artist B"], added_at="2023-06-01T00:00:00Z")
    ]
    captured_urls: list[str] = []

    def side_effect(req: urllib.request.Request) -> Any:
        captured_urls.append(req.full_url)
        if len(captured_urls) == 1:
            return _make_response(probe, total=150, limit=50)
        if "offset=100" in req.full_url:
            return _make_response(page_at_100, total=150, limit=50)
        return _make_response(page_at_50, total=150, limit=50)

    with patch("urllib.request.urlopen", side_effect=side_effect):
        result = fetch_saved_albums(_VALID_TOKEN, limit=2)

    offsets = [u for u in captured_urls if "offset=" in u]
    # offset=100 must come before offset=50 (decreasing order)
    assert "offset=100" in offsets[0]
    assert "offset=50" in offsets[1]
    assert len({r.artists[0].id for r in result if r.artists}) >= 2


def test_fetch_saved_albums_limit_appends_probe_items_when_sweep_exhausted() -> None:
    """When backward sweep exhausts all pages without N distinct artists, probe items are appended."""
    # 2 pages. Last page (offset=50) has only 1 artist. limit=3.
    # Only 2 distinct artists total → function must return all albums including probe items.
    probe = [
        _album_item("newest", "Newest", ["Artist X"], added_at="2024-06-01T00:00:00Z")
    ]
    last_page = [
        _album_item("oldest", "Oldest", ["Artist Y"], added_at="2023-01-01T00:00:00Z")
    ]

    responses = iter(
        [
            _make_response(probe, total=100, limit=50),
            _make_response(last_page, total=100, limit=50),
        ]
    )

    with patch("urllib.request.urlopen", side_effect=lambda _req: next(responses)):
        result = fetch_saved_albums(_VALID_TOKEN, limit=3)

    ids = {r.id for r in result}
    assert "newest" in ids
    assert "oldest" in ids


# ---------------------------------------------------------------------------
# Group 6: stopping condition excludes probe items (tasks 4.1, 4.2)
# ---------------------------------------------------------------------------


def test_fetch_saved_albums_limit_probe_artists_not_counted_toward_stop() -> None:
    """Artists seen in probe items must NOT count toward the stopping condition."""
    # Probe has 5 distinct artists (already >= limit=3). If probe counted, we'd stop immediately.
    # But the function must still fetch at least one backward page.
    probe = [
        _album_item(
            f"p{i}", f"New{i}", [f"Artist {i}"], added_at=f"2024-0{i + 1}-01T00:00:00Z"
        )
        for i in range(1, 6)  # 5 distinct artists in probe
    ]
    last_page = [
        _album_item("old1", "Old1", ["Artist Old"], added_at="2023-01-01T00:00:00Z"),
    ]
    call_count = [0]

    def side_effect(req: urllib.request.Request) -> Any:
        call_count[0] += 1
        if call_count[0] == 1:
            return _make_response(probe, total=100, limit=50)
        return _make_response(last_page, total=100, limit=50)

    with patch("urllib.request.urlopen", side_effect=side_effect):
        fetch_saved_albums(_VALID_TOKEN, limit=3)

    # Must have made at least 2 calls (probe + at least one backward page)
    assert call_count[0] >= 2


# ---------------------------------------------------------------------------
# Group 7: status messages with limit (tasks 5.1, 5.2, 5.3)
# ---------------------------------------------------------------------------


def test_fetch_saved_albums_limit_probe_emits_status_1_of_total_pages() -> None:
    """Probe call emits status (1/total_pages)..."""
    received: list[str] = []
    status.configure(received.append)

    probe = [_album_item("newest", "N", ["Artist X"], added_at="2024-01-01T00:00:00Z")]
    last_page = [
        _album_item("oldest", "O", ["Artist Y"], added_at="2023-01-01T00:00:00Z")
    ]

    responses = iter(
        [
            _make_response(probe, total=100, limit=50),
            _make_response(last_page, total=100, limit=50),
        ]
    )

    with patch("urllib.request.urlopen", side_effect=lambda _req: next(responses)):
        fetch_saved_albums(_VALID_TOKEN, limit=1)

    assert any("(1/2)" in msg for msg in received)


def test_fetch_saved_albums_limit_backward_pages_increment_status_counter() -> None:
    """Each backward page increments N in the (N/total_pages) status message."""
    received: list[str] = []
    status.configure(received.append)

    probe = [_album_item("n1", "New", ["Artist Z"], added_at="2024-01-01T00:00:00Z")]
    page_100 = [
        _album_item("o1", "Old1", ["Artist A"], added_at="2023-01-01T00:00:00Z")
    ]
    page_50 = [_album_item("o2", "Old2", ["Artist B"], added_at="2023-06-01T00:00:00Z")]

    call_count = [0]

    def side_effect(req: urllib.request.Request) -> Any:
        call_count[0] += 1
        if call_count[0] == 1:
            return _make_response(probe, total=150, limit=50)
        if "offset=100" in req.full_url:
            return _make_response(page_100, total=150, limit=50)
        return _make_response(page_50, total=150, limit=50)

    with patch("urllib.request.urlopen", side_effect=side_effect):
        fetch_saved_albums(_VALID_TOKEN, limit=2)

    assert any("(1/3)" in msg for msg in received)
    assert any("(2/3)" in msg for msg in received)
    assert any("(3/3)" in msg for msg in received)


def test_fetch_saved_albums_limit_single_page_emits_exactly_one_status() -> None:
    """When total <= 50, exactly one status message (1/1) is emitted."""
    received: list[str] = []
    status.configure(received.append)

    with patch(
        "urllib.request.urlopen",
        return_value=_make_response(
            [_album_item("id1", "A", ["Artist A"], added_at="2023-01-01T00:00:00Z")],
            total=1,
            limit=50,
        ),
    ):
        fetch_saved_albums(_VALID_TOKEN, limit=4)

    status_msgs = [m for m in received if "fetching saved albums" in m]
    assert len(status_msgs) == 1
    assert "(1/1)" in status_msgs[0]
