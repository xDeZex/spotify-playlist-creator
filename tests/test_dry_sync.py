from __future__ import annotations

from unittest.mock import patch

import pytest

from spotify_playlist_creator.dry_sync import report_dry_sync_artist
from spotify_playlist_creator.models import Album

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ALBUM_A = Album(id="a1", name="Chromakopia", release_date="2024-10-25")
_ALBUM_B = Album(id="a2", name="Call Me If You Get Lost", release_date="2021-06-25")
_ALBUM_C = Album(id="a3", name="Igor", release_date="2019-05-17")


# ---------------------------------------------------------------------------
# Group 1: report_dry_sync_artist — non-empty album list
# ---------------------------------------------------------------------------


def test_report_dry_sync_artist_prints_artist_name(
    capsys: pytest.CaptureFixture[str],
) -> None:
    report_dry_sync_artist("Tyler, the Creator", [_ALBUM_A])
    out = capsys.readouterr().out
    assert "Tyler, the Creator" in out


def test_report_dry_sync_artist_prints_would_create_for_each_album(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Adversarial: two albums so we verify both lines are printed, not just one
    report_dry_sync_artist("Tyler, the Creator", [_ALBUM_A, _ALBUM_B])
    out = capsys.readouterr().out
    assert "Would create: Chromakopia" in out
    assert "Would create: Call Me If You Get Lost" in out


def test_report_dry_sync_artist_would_create_prefix_exact(
    capsys: pytest.CaptureFixture[str],
) -> None:
    report_dry_sync_artist("Tyler, the Creator", [_ALBUM_A])
    out = capsys.readouterr().out
    assert "Would create: Chromakopia" in out


# ---------------------------------------------------------------------------
# Group 2: report_dry_sync_artist — empty album list
# ---------------------------------------------------------------------------


def test_report_dry_sync_artist_prints_already_up_to_date_for_empty_list(
    capsys: pytest.CaptureFixture[str],
) -> None:
    report_dry_sync_artist("Tyler, the Creator", [])
    out = capsys.readouterr().out
    assert "already up to date" in out


def test_report_dry_sync_artist_prints_artist_name_even_when_up_to_date(
    capsys: pytest.CaptureFixture[str],
) -> None:
    report_dry_sync_artist("Tyler, the Creator", [])
    out = capsys.readouterr().out
    assert "Tyler, the Creator" in out


def test_report_dry_sync_artist_does_not_print_would_create_when_up_to_date(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Adversarial: empty list — must NOT print Would create
    report_dry_sync_artist("Tyler, the Creator", [])
    out = capsys.readouterr().out
    assert "Would create" not in out


# ---------------------------------------------------------------------------
# Group 3: report_dry_sync_artist — never blocks on input()
# ---------------------------------------------------------------------------


def test_report_dry_sync_artist_never_calls_input_with_albums() -> None:
    with patch("builtins.input") as mock_input:
        report_dry_sync_artist("Tyler, the Creator", [_ALBUM_A, _ALBUM_B, _ALBUM_C])
    mock_input.assert_not_called()


def test_report_dry_sync_artist_never_calls_input_when_up_to_date() -> None:
    with patch("builtins.input") as mock_input:
        report_dry_sync_artist("Tyler, the Creator", [])
    mock_input.assert_not_called()


# ---------------------------------------------------------------------------
# Group 4: genre in report_dry_sync_artist
# ---------------------------------------------------------------------------


def test_report_dry_sync_artist_shows_genre_tag_on_artist_line(
    capsys: pytest.CaptureFixture[str],
) -> None:
    report_dry_sync_artist("Tyler, the Creator", [_ALBUM_A], genre=["hip-hop"])
    out = capsys.readouterr().out
    assert "[hip-hop]" in out


def test_report_dry_sync_artist_shows_multiple_genre_tags(
    capsys: pytest.CaptureFixture[str],
) -> None:
    report_dry_sync_artist(
        "Tyler, the Creator", [_ALBUM_A], genre=["hip-hop", "rap", "alternative"]
    )
    out = capsys.readouterr().out
    assert "[hip-hop, rap, alternative]" in out


def test_report_dry_sync_artist_shows_genre_not_found_when_empty_list(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Adversarial: genre=[] (no tags found) must show [genre not found]
    report_dry_sync_artist("Tyler, the Creator", [], genre=[])
    out = capsys.readouterr().out
    assert "[genre not found]" in out


def test_report_dry_sync_artist_shows_failed_to_get_genre_when_none(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Adversarial: genre=None (fetch error) must show [failed to get genre]
    report_dry_sync_artist("Tyler, the Creator", [], genre=None)
    out = capsys.readouterr().out
    assert "[failed to get genre]" in out
