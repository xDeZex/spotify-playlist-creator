from __future__ import annotations

from datetime import datetime
from unittest.mock import patch

from spotify_playlist_creator import run
from spotify_playlist_creator.auth import SpotifyToken
from spotify_playlist_creator.create_playlists import CreatedPlaylist
from spotify_playlist_creator.models import Album, Artist, RawRelease, SavedAlbum

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_TOKEN = SpotifyToken(
    access_token="test_tok",
    token_type="Bearer",
    refresh_token="rtoken",
    expires_at=9_999_999_999.0,
)

_ARTIST_A = Artist(id="artist_a", name="Artist A")
_ARTIST_B = Artist(id="artist_b", name="Artist B")

_ALBUM_A1 = Album(id="alb_a1", name="Album A1", release_date="2023-01-01")
_ALBUM_A2 = Album(id="alb_a2", name="Album A2", release_date="2022-01-01")
_ALBUM_B1 = Album(id="alb_b1", name="Album B1", release_date="2021-06-01")

_SAVED_A = SavedAlbum(
    id="alb_a1",
    name="Album A1",
    artists=[_ARTIST_A],
    added_at=datetime(2023, 1, 1),
)
_SAVED_B = SavedAlbum(
    id="alb_b1",
    name="Album B1",
    artists=[_ARTIST_B],
    added_at=datetime(2021, 6, 1),
)

_CREATED_A1 = CreatedPlaylist(name="Album A1", id="pl_a1")
_CREATED_A2 = CreatedPlaylist(name="Album A2", id="pl_a2")
_CREATED_B1 = CreatedPlaylist(name="Album B1", id="pl_b1")

_RAW_A: list[RawRelease] = [
    RawRelease(
        id="alb_a1", name="Album A1", album_type="album", release_date="2023-01-01"
    ),
    RawRelease(
        id="alb_a2", name="Album A2", album_type="album", release_date="2022-01-01"
    ),
]
_RAW_B: list[RawRelease] = [
    RawRelease(
        id="alb_b1", name="Album B1", album_type="album", release_date="2021-06-01"
    ),
]
_RAW_SINGLES: list[RawRelease] = [
    RawRelease(
        id="s1", name="Single 1", album_type="single", release_date="2023-05-01"
    ),
]

_EXISTING_EMPTY: dict[str, list[str]] = {}


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------


def test_run_calls_authenticate_exactly_once() -> None:
    with (
        patch(
            "spotify_playlist_creator.authenticate", return_value=_TOKEN
        ) as mock_auth,
        patch("spotify_playlist_creator.fetch_saved_albums", return_value=[]),
        patch("spotify_playlist_creator.derive_artists", return_value=[]),
        patch("spotify_playlist_creator.fetch_user_playlists", return_value={}),
    ):
        run()

    mock_auth.assert_called_once()


def test_run_forwards_token_to_fetch_saved_albums() -> None:
    with (
        patch("spotify_playlist_creator.authenticate", return_value=_TOKEN),
        patch(
            "spotify_playlist_creator.fetch_saved_albums", return_value=[]
        ) as mock_fetch,
        patch("spotify_playlist_creator.derive_artists", return_value=[]),
        patch("spotify_playlist_creator.fetch_user_playlists", return_value={}),
    ):
        run()

    mock_fetch.assert_called_once_with(_TOKEN)


# ---------------------------------------------------------------------------
# Task 2.1: Happy path — two artists both with new albums
# ---------------------------------------------------------------------------


def test_run_calls_prompt_for_folder_for_each_artist_with_new_playlists() -> None:
    with (
        patch("spotify_playlist_creator.authenticate", return_value=_TOKEN),
        patch(
            "spotify_playlist_creator.fetch_saved_albums",
            return_value=[_SAVED_A, _SAVED_B],
        ),
        patch(
            "spotify_playlist_creator.derive_artists",
            return_value=[_ARTIST_A, _ARTIST_B],
        ),
        patch(
            "spotify_playlist_creator.fetch_user_playlists",
            return_value=_EXISTING_EMPTY,
        ),
        patch(
            "spotify_playlist_creator.fetch_artist_releases",
            side_effect=lambda tok, artist_id: (
                _RAW_A if artist_id == "artist_a" else _RAW_B
            ),
        ),
        patch(
            "spotify_playlist_creator.classify_releases",
            side_effect=lambda tok, releases: (
                [_ALBUM_A1, _ALBUM_A2] if releases == _RAW_A else [_ALBUM_B1]
            ),
        ),
        patch(
            "spotify_playlist_creator.create_album_playlists",
            side_effect=lambda tok, albums, existing: (
                [_CREATED_A1, _CREATED_A2]
                if albums == [_ALBUM_A1, _ALBUM_A2]
                else [_CREATED_B1]
            ),
        ),
        patch("spotify_playlist_creator.prompt_for_folder") as mock_prompt,
    ):
        run()

    assert mock_prompt.call_count == 2
    mock_prompt.assert_any_call("Artist A", [_CREATED_A1, _CREATED_A2])
    mock_prompt.assert_any_call("Artist B", [_CREATED_B1])


# ---------------------------------------------------------------------------
# Task 2.2: All albums already exist — prompt_for_folder never called
# ---------------------------------------------------------------------------


def test_run_does_not_call_prompt_when_no_new_playlists() -> None:
    with (
        patch("spotify_playlist_creator.authenticate", return_value=_TOKEN),
        patch(
            "spotify_playlist_creator.fetch_saved_albums",
            return_value=[_SAVED_A],
        ),
        patch(
            "spotify_playlist_creator.derive_artists",
            return_value=[_ARTIST_A],
        ),
        patch(
            "spotify_playlist_creator.fetch_user_playlists",
            return_value={"Album A1": ["pid1"], "Album A2": ["pid2"]},
        ),
        patch(
            "spotify_playlist_creator.fetch_artist_releases",
            return_value=_RAW_A,
        ),
        patch(
            "spotify_playlist_creator.classify_releases",
            return_value=[_ALBUM_A1, _ALBUM_A2],
        ),
        patch(
            "spotify_playlist_creator.create_album_playlists",
            return_value=[],
        ),
        patch("spotify_playlist_creator.prompt_for_folder") as mock_prompt,
    ):
        run()

    mock_prompt.assert_not_called()


# ---------------------------------------------------------------------------
# Task 2.3: Mixed — one artist with new albums, one without
# ---------------------------------------------------------------------------


def test_run_calls_prompt_only_for_artists_with_new_playlists() -> None:
    with (
        patch("spotify_playlist_creator.authenticate", return_value=_TOKEN),
        patch(
            "spotify_playlist_creator.fetch_saved_albums",
            return_value=[_SAVED_A, _SAVED_B],
        ),
        patch(
            "spotify_playlist_creator.derive_artists",
            return_value=[_ARTIST_A, _ARTIST_B],
        ),
        patch(
            "spotify_playlist_creator.fetch_user_playlists",
            return_value=_EXISTING_EMPTY,
        ),
        patch(
            "spotify_playlist_creator.fetch_artist_releases",
            side_effect=lambda tok, artist_id: (
                _RAW_A if artist_id == "artist_a" else _RAW_B
            ),
        ),
        patch(
            "spotify_playlist_creator.classify_releases",
            side_effect=lambda tok, releases: (
                [_ALBUM_A1, _ALBUM_A2] if releases == _RAW_A else [_ALBUM_B1]
            ),
        ),
        patch(
            "spotify_playlist_creator.create_album_playlists",
            side_effect=lambda tok, albums, existing: (
                [_CREATED_A1, _CREATED_A2] if albums == [_ALBUM_A1, _ALBUM_A2] else []
            ),
        ),
        patch("spotify_playlist_creator.prompt_for_folder") as mock_prompt,
    ):
        run()

    assert mock_prompt.call_count == 1
    mock_prompt.assert_called_once_with("Artist A", [_CREATED_A1, _CREATED_A2])


# ---------------------------------------------------------------------------
# Task 2.4: No saved albums — artist loop never runs
# ---------------------------------------------------------------------------


def test_run_does_nothing_when_no_saved_albums() -> None:
    with (
        patch("spotify_playlist_creator.authenticate", return_value=_TOKEN),
        patch("spotify_playlist_creator.fetch_saved_albums", return_value=[]),
        patch(
            "spotify_playlist_creator.derive_artists", return_value=[]
        ) as mock_derive,
        patch(
            "spotify_playlist_creator.fetch_user_playlists",
            return_value=_EXISTING_EMPTY,
        ),
        patch("spotify_playlist_creator.fetch_artist_releases") as mock_releases,
        patch("spotify_playlist_creator.classify_releases") as mock_classify,
        patch("spotify_playlist_creator.create_album_playlists") as mock_create,
        patch("spotify_playlist_creator.prompt_for_folder") as mock_prompt,
    ):
        run()

    mock_derive.assert_called_once_with([])
    mock_releases.assert_not_called()
    mock_classify.assert_not_called()
    mock_create.assert_not_called()
    mock_prompt.assert_not_called()


# ---------------------------------------------------------------------------
# Task 2.5: Artist with only singles
# ---------------------------------------------------------------------------


def test_run_skips_prompt_for_artist_with_no_qualifying_releases() -> None:
    with (
        patch("spotify_playlist_creator.authenticate", return_value=_TOKEN),
        patch(
            "spotify_playlist_creator.fetch_saved_albums",
            return_value=[_SAVED_A],
        ),
        patch(
            "spotify_playlist_creator.derive_artists",
            return_value=[_ARTIST_A],
        ),
        patch(
            "spotify_playlist_creator.fetch_user_playlists",
            return_value=_EXISTING_EMPTY,
        ),
        patch(
            "spotify_playlist_creator.fetch_artist_releases",
            return_value=_RAW_SINGLES,
        ),
        patch(
            "spotify_playlist_creator.classify_releases",
            return_value=[],
        ),
        patch(
            "spotify_playlist_creator.create_album_playlists",
            return_value=[],
        ),
        patch("spotify_playlist_creator.prompt_for_folder") as mock_prompt,
    ):
        run()

    mock_prompt.assert_not_called()


def test_run_skips_prompt_for_artist_with_no_releases_at_all() -> None:
    with (
        patch("spotify_playlist_creator.authenticate", return_value=_TOKEN),
        patch(
            "spotify_playlist_creator.fetch_saved_albums",
            return_value=[_SAVED_A],
        ),
        patch(
            "spotify_playlist_creator.derive_artists",
            return_value=[_ARTIST_A],
        ),
        patch(
            "spotify_playlist_creator.fetch_user_playlists",
            return_value=_EXISTING_EMPTY,
        ),
        patch(
            "spotify_playlist_creator.fetch_artist_releases",
            return_value=[],
        ),
        patch(
            "spotify_playlist_creator.classify_releases",
            return_value=[],
        ) as mock_classify,
        patch(
            "spotify_playlist_creator.create_album_playlists",
            return_value=[],
        ),
        patch("spotify_playlist_creator.prompt_for_folder") as mock_prompt,
    ):
        run()

    mock_classify.assert_called_once_with(_TOKEN, [])
    mock_prompt.assert_not_called()


# ---------------------------------------------------------------------------
# Task 2.6: fetch_user_playlists called exactly once; token forwarded
# ---------------------------------------------------------------------------


def test_run_fetches_existing_playlists_once_regardless_of_artist_count() -> None:
    with (
        patch("spotify_playlist_creator.authenticate", return_value=_TOKEN),
        patch(
            "spotify_playlist_creator.fetch_saved_albums",
            return_value=[_SAVED_A, _SAVED_B],
        ),
        patch(
            "spotify_playlist_creator.derive_artists",
            return_value=[_ARTIST_A, _ARTIST_B],
        ),
        patch(
            "spotify_playlist_creator.fetch_user_playlists",
            return_value=_EXISTING_EMPTY,
        ) as mock_fetch_playlists,
        patch(
            "spotify_playlist_creator.fetch_artist_releases",
            return_value=[],
        ),
        patch(
            "spotify_playlist_creator.classify_releases",
            return_value=[],
        ),
        patch(
            "spotify_playlist_creator.create_album_playlists",
            return_value=[],
        ),
        patch("spotify_playlist_creator.prompt_for_folder"),
    ):
        run()

    mock_fetch_playlists.assert_called_once_with(_TOKEN)


def test_run_forwards_token_to_fetch_artist_releases_classify_and_create() -> None:
    # Also covers spec scenario: "empty existing playlists → create_album_playlists receives {}"
    with (
        patch("spotify_playlist_creator.authenticate", return_value=_TOKEN),
        patch(
            "spotify_playlist_creator.fetch_saved_albums",
            return_value=[_SAVED_A],
        ),
        patch(
            "spotify_playlist_creator.derive_artists",
            return_value=[_ARTIST_A],
        ),
        patch(
            "spotify_playlist_creator.fetch_user_playlists",
            return_value=_EXISTING_EMPTY,
        ),
        patch(
            "spotify_playlist_creator.fetch_artist_releases",
            return_value=_RAW_A,
        ) as mock_releases,
        patch(
            "spotify_playlist_creator.classify_releases",
            return_value=[_ALBUM_A1],
        ) as mock_classify,
        patch(
            "spotify_playlist_creator.create_album_playlists",
            return_value=[],
        ) as mock_create,
        patch("spotify_playlist_creator.prompt_for_folder"),
    ):
        run()

    mock_releases.assert_called_once_with(_TOKEN, "artist_a")
    mock_classify.assert_called_once_with(_TOKEN, _RAW_A)
    mock_create.assert_called_once_with(_TOKEN, [_ALBUM_A1], _EXISTING_EMPTY)
