from __future__ import annotations

from datetime import datetime
from unittest.mock import patch

from pytest import mark

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
_ARTIST_C = Artist(id="artist_c", name="Artist C")
_ARTIST_D = Artist(id="artist_d", name="Artist D")
_ARTIST_E = Artist(id="artist_e", name="Artist E")

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
        # patch("spotify_playlist_creator.fetch_owned_playlists", return_value={}),
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
        # patch("spotify_playlist_creator.fetch_owned_playlists", return_value={}),
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
        # patch(
        #    "spotify_playlist_creator.fetch_owned_playlists",
        #    return_value=_EXISTING_EMPTY,
        # ),
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
            "spotify_playlist_creator.find_missing_album_playlists",
            side_effect=lambda tok, albums, existing: albums,
        ),
        patch(
            "spotify_playlist_creator.create_album_playlists",
            side_effect=lambda tok, albums: (
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
        # patch(
        #    "spotify_playlist_creator.fetch_owned_playlists",
        #    return_value={"Album A1": ["pid1"], "Album A2": ["pid2"]},
        # ),
        patch(
            "spotify_playlist_creator.fetch_artist_releases",
            return_value=_RAW_A,
        ),
        patch(
            "spotify_playlist_creator.classify_releases",
            return_value=[_ALBUM_A1, _ALBUM_A2],
        ),
        patch(
            "spotify_playlist_creator.find_missing_album_playlists",
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
        # patch(
        #    "spotify_playlist_creator.fetch_owned_playlists",
        #    return_value=_EXISTING_EMPTY,
        # ),
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
            "spotify_playlist_creator.find_missing_album_playlists",
            side_effect=lambda tok, albums, existing: albums,
        ),
        patch(
            "spotify_playlist_creator.create_album_playlists",
            side_effect=lambda tok, albums: (
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
        # patch(
        #    "spotify_playlist_creator.fetch_owned_playlists",
        #    return_value=_EXISTING_EMPTY,
        # ),
        patch("spotify_playlist_creator.fetch_artist_releases") as mock_releases,
        patch("spotify_playlist_creator.classify_releases") as mock_classify,
        patch(
            "spotify_playlist_creator.find_missing_album_playlists"
        ) as mock_find_missing,
        patch("spotify_playlist_creator.create_album_playlists") as mock_create,
        patch("spotify_playlist_creator.prompt_for_folder") as mock_prompt,
    ):
        run()

    mock_derive.assert_called_once_with([])
    mock_releases.assert_not_called()
    mock_classify.assert_not_called()
    mock_find_missing.assert_not_called()
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
        # patch(
        #    "spotify_playlist_creator.fetch_owned_playlists",
        #    return_value=_EXISTING_EMPTY,
        # ),
        patch(
            "spotify_playlist_creator.fetch_artist_releases",
            return_value=_RAW_SINGLES,
        ),
        patch(
            "spotify_playlist_creator.classify_releases",
            return_value=[],
        ),
        patch(
            "spotify_playlist_creator.find_missing_album_playlists",
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
        # patch(
        #    "spotify_playlist_creator.fetch_owned_playlists",
        #    return_value=_EXISTING_EMPTY,
        # ),
        patch(
            "spotify_playlist_creator.fetch_artist_releases",
            return_value=[],
        ),
        patch(
            "spotify_playlist_creator.classify_releases",
            return_value=[],
        ) as mock_classify,
        patch(
            "spotify_playlist_creator.find_missing_album_playlists",
            return_value=[],
        ),
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


@mark.skip(reason="fetch_owned_playlists function not used now")
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
            "spotify_playlist_creator.fetch_owned_playlists",
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
            "spotify_playlist_creator.find_missing_album_playlists",
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
        # patch(
        #    "spotify_playlist_creator.fetch_owned_playlists",
        #    return_value=_EXISTING_EMPTY,
        # ),
        patch(
            "spotify_playlist_creator.fetch_artist_releases",
            return_value=_RAW_A,
        ) as mock_releases,
        patch(
            "spotify_playlist_creator.classify_releases",
            return_value=[_ALBUM_A1],
        ) as mock_classify,
        patch(
            "spotify_playlist_creator.find_missing_album_playlists",
            return_value=[],
        ) as mock_find_missing,
        patch(
            "spotify_playlist_creator.create_album_playlists",
            return_value=[],
        ) as mock_create,
        patch("spotify_playlist_creator.prompt_for_folder"),
    ):
        run()

    mock_releases.assert_called_once_with(_TOKEN, "artist_a")
    mock_classify.assert_called_once_with(_TOKEN, _RAW_A)
    mock_find_missing.assert_called_once_with(_TOKEN, [_ALBUM_A1], _EXISTING_EMPTY)
    mock_create.assert_called_once_with(_TOKEN, [])


# ---------------------------------------------------------------------------
# Artist Limit (tasks 2.1–2.4)
# ---------------------------------------------------------------------------


def test_run_applies_artist_limit() -> None:
    five_artists = [_ARTIST_A, _ARTIST_B, _ARTIST_C, _ARTIST_D, _ARTIST_E]
    with (
        patch("spotify_playlist_creator.authenticate", return_value=_TOKEN),
        patch("spotify_playlist_creator.fetch_saved_albums", return_value=[]),
        patch("spotify_playlist_creator.derive_artists", return_value=five_artists),
        # patch("spotify_playlist_creator.fetch_owned_playlists", return_value={}),
        patch(
            "spotify_playlist_creator.fetch_artist_releases", return_value=[]
        ) as mock_releases,
        patch("spotify_playlist_creator.classify_releases", return_value=[]),
        patch("spotify_playlist_creator.find_missing_album_playlists", return_value=[]),
        patch("spotify_playlist_creator.create_album_playlists", return_value=[]),
        patch("spotify_playlist_creator.prompt_for_folder"),
    ):
        run(limit=2)

    assert mock_releases.call_count == 2
    mock_releases.assert_any_call(_TOKEN, "artist_a")
    mock_releases.assert_any_call(_TOKEN, "artist_b")


def test_run_with_no_limit_processes_all_artists() -> None:
    three_artists = [_ARTIST_A, _ARTIST_B, _ARTIST_C]
    with (
        patch("spotify_playlist_creator.authenticate", return_value=_TOKEN),
        patch("spotify_playlist_creator.fetch_saved_albums", return_value=[]),
        patch("spotify_playlist_creator.derive_artists", return_value=three_artists),
        # patch("spotify_playlist_creator.fetch_owned_playlists", return_value={}),
        patch(
            "spotify_playlist_creator.fetch_artist_releases", return_value=[]
        ) as mock_releases,
        patch("spotify_playlist_creator.classify_releases", return_value=[]),
        patch("spotify_playlist_creator.find_missing_album_playlists", return_value=[]),
        patch("spotify_playlist_creator.create_album_playlists", return_value=[]),
        patch("spotify_playlist_creator.prompt_for_folder"),
    ):
        run(limit=None)

    assert mock_releases.call_count == 3


def test_run_with_limit_exceeding_artist_count_processes_all() -> None:
    two_artists = [_ARTIST_A, _ARTIST_B]
    with (
        patch("spotify_playlist_creator.authenticate", return_value=_TOKEN),
        patch("spotify_playlist_creator.fetch_saved_albums", return_value=[]),
        patch("spotify_playlist_creator.derive_artists", return_value=two_artists),
        # patch("spotify_playlist_creator.fetch_owned_playlists", return_value={}),
        patch(
            "spotify_playlist_creator.fetch_artist_releases", return_value=[]
        ) as mock_releases,
        patch("spotify_playlist_creator.classify_releases", return_value=[]),
        patch("spotify_playlist_creator.find_missing_album_playlists", return_value=[]),
        patch("spotify_playlist_creator.create_album_playlists", return_value=[]),
        patch("spotify_playlist_creator.prompt_for_folder"),
    ):
        run(limit=10)

    assert mock_releases.call_count == 2


# ---------------------------------------------------------------------------
# Dry Sync mode — tasks 3.1–3.3
# ---------------------------------------------------------------------------


def test_run_dry_run_calls_find_missing_but_not_create() -> None:
    # Adversarial: artist has albums so create would be called in normal mode
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
        # patch(
        #    "spotify_playlist_creator.fetch_owned_playlists",
        #    return_value=_EXISTING_EMPTY,
        # ),
        patch(
            "spotify_playlist_creator.fetch_artist_releases",
            return_value=_RAW_A,
        ),
        patch(
            "spotify_playlist_creator.classify_releases",
            return_value=[_ALBUM_A1, _ALBUM_A2],
        ),
        patch(
            "spotify_playlist_creator.find_missing_album_playlists",
            return_value=[_ALBUM_A1],
        ) as mock_find_missing,
        patch(
            "spotify_playlist_creator.create_album_playlists",
        ) as mock_create,
        patch("spotify_playlist_creator.report_dry_sync_artist"),
    ):
        run(dry_run=True)

    mock_find_missing.assert_called_once()
    mock_create.assert_not_called()


def test_run_dry_run_calls_report_for_every_artist_including_up_to_date() -> None:
    # Adversarial: one artist has new albums, one is already up to date;
    # both must get a report_dry_sync_artist call
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
        # patch(
        #    "spotify_playlist_creator.fetch_owned_playlists",
        #    return_value=_EXISTING_EMPTY,
        # ),
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
            "spotify_playlist_creator.find_missing_album_playlists",
            side_effect=lambda tok, albums, existing: (
                [_ALBUM_A1] if albums == [_ALBUM_A1, _ALBUM_A2] else []
            ),
        ),
        patch(
            "spotify_playlist_creator.report_dry_sync_artist",
        ) as mock_report,
    ):
        run(dry_run=True)

    assert mock_report.call_count == 2
    mock_report.assert_any_call("Artist A", [_ALBUM_A1])
    mock_report.assert_any_call("Artist B", [])


def test_run_normal_mode_behaviour_unchanged() -> None:
    # dry_run=False (default): calls both plan and execute steps,
    # prompt_for_folder only for artists with new playlists, never report
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
        # patch(
        #    "spotify_playlist_creator.fetch_owned_playlists",
        #    return_value=_EXISTING_EMPTY,
        # ),
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
            "spotify_playlist_creator.find_missing_album_playlists",
            side_effect=lambda tok, albums, existing: albums,
        ) as mock_find_missing,
        patch(
            "spotify_playlist_creator.create_album_playlists",
            side_effect=lambda tok, albums: (
                [_CREATED_A1, _CREATED_A2] if albums == [_ALBUM_A1, _ALBUM_A2] else []
            ),
        ) as mock_create,
        patch("spotify_playlist_creator.prompt_for_folder") as mock_prompt,
        patch("spotify_playlist_creator.report_dry_sync_artist") as mock_report,
    ):
        run(dry_run=False)

    assert mock_find_missing.call_count == 2
    assert mock_create.call_count == 2
    mock_prompt.assert_called_once_with("Artist A", [_CREATED_A1, _CREATED_A2])
    mock_report.assert_not_called()


# ---------------------------------------------------------------------------
# Tasks 6.1-6.4: run() status orchestration
# ---------------------------------------------------------------------------

_COMMON_PATCHES: dict[str, object] = dict(
    fetch_saved_albums=lambda tok: [],
    derive_artists=lambda albums: [],
    fetch_owned_playlists=lambda tok: {},
)


def test_run_sets_status_before_fetch_saved_albums() -> None:
    call_log: list[str] = []

    def recording_configure(fn: object) -> None:
        call_log.append("status.configure")

    def recording_fetch(tok: object) -> list[object]:
        call_log.append("fetch_saved_albums")
        return []

    with (
        patch("spotify_playlist_creator.authenticate", return_value=_TOKEN),
        patch(
            "spotify_playlist_creator.status.configure", side_effect=recording_configure
        ),
        patch(
            "spotify_playlist_creator.fetch_saved_albums",
            side_effect=recording_fetch,
        ),
        patch("spotify_playlist_creator.derive_artists", return_value=[]),
        # patch("spotify_playlist_creator.fetch_owned_playlists", return_value={}),
        patch("spotify_playlist_creator.status.clear"),
    ):
        run()

    assert call_log.index("status.configure") < call_log.index("fetch_saved_albums")


def test_run_sets_context_per_artist_with_post_limit_count() -> None:
    contexts: list[str] = []

    def recording_set_context(ctx: str) -> None:
        contexts.append(ctx)

    five_artists = [_ARTIST_A, _ARTIST_B, _ARTIST_C, _ARTIST_D, _ARTIST_E]

    with (
        patch("spotify_playlist_creator.authenticate", return_value=_TOKEN),
        patch("spotify_playlist_creator.fetch_saved_albums", return_value=[]),
        patch("spotify_playlist_creator.derive_artists", return_value=five_artists),
        # patch("spotify_playlist_creator.fetch_owned_playlists", return_value={}),
        patch("spotify_playlist_creator.fetch_artist_releases", return_value=[]),
        patch("spotify_playlist_creator.classify_releases", return_value=[]),
        patch("spotify_playlist_creator.find_missing_album_playlists", return_value=[]),
        patch("spotify_playlist_creator.create_album_playlists", return_value=[]),
        patch("spotify_playlist_creator.prompt_for_folder"),
        patch("spotify_playlist_creator.status.configure"),
        patch(
            "spotify_playlist_creator.status.set_context",
            side_effect=recording_set_context,
        ),
        patch("spotify_playlist_creator.status.clear"),
    ):
        run(limit=3)

    assert contexts == ["[1/3] Artist A", "[2/3] Artist B", "[3/3] Artist C"]


def test_run_clears_status_after_processing() -> None:
    clear_calls: list[int] = []

    with (
        patch("spotify_playlist_creator.authenticate", return_value=_TOKEN),
        patch("spotify_playlist_creator.fetch_saved_albums", return_value=[]),
        patch("spotify_playlist_creator.derive_artists", return_value=[]),
        # patch("spotify_playlist_creator.fetch_owned_playlists", return_value={}),
        patch("spotify_playlist_creator.status.configure"),
        patch(
            "spotify_playlist_creator.status.clear",
            side_effect=lambda: clear_calls.append(1),
        ),
    ):
        run()

    assert len(clear_calls) == 1


def test_run_status_active_in_dry_run_mode() -> None:
    contexts: list[str] = []
    clear_calls: list[int] = []

    with (
        patch("spotify_playlist_creator.authenticate", return_value=_TOKEN),
        patch("spotify_playlist_creator.fetch_saved_albums", return_value=[_SAVED_A]),
        patch("spotify_playlist_creator.derive_artists", return_value=[_ARTIST_A]),
        # patch("spotify_playlist_creator.fetch_owned_playlists", return_value={}),
        patch("spotify_playlist_creator.fetch_artist_releases", return_value=[]),
        patch("spotify_playlist_creator.classify_releases", return_value=[]),
        patch("spotify_playlist_creator.find_missing_album_playlists", return_value=[]),
        patch("spotify_playlist_creator.report_dry_sync_artist"),
        patch("spotify_playlist_creator.status.configure"),
        patch(
            "spotify_playlist_creator.status.set_context",
            side_effect=contexts.append,
        ),
        patch(
            "spotify_playlist_creator.status.clear",
            side_effect=lambda: clear_calls.append(1),
        ),
    ):
        run(dry_run=True)

    assert contexts == ["[1/1] Artist A"]
    assert len(clear_calls) == 1
