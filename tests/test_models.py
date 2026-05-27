from __future__ import annotations

import dataclasses
from datetime import datetime

import pytest

from spotify_playlist_creator.models import Album, Artist, SavedAlbum


def test_artist_construction() -> None:
    artist = Artist(id="a1", name="Artist A")
    assert artist.id == "a1"
    assert artist.name == "Artist A"


def test_artist_same_name_different_id_are_distinct() -> None:
    assert Artist(id="x", name="Same") != Artist(id="y", name="Same")


def test_artist_same_id_and_name_are_equal() -> None:
    assert Artist(id="x", name="A") == Artist(id="x", name="A")


def test_saved_album_construction() -> None:
    artist = Artist(id="a1", name="Artist A")
    album = SavedAlbum(
        id="alb1",
        name="Album One",
        artists=[artist],
        added_at=datetime(2024, 1, 15),
    )
    assert album.id == "alb1"
    assert album.name == "Album One"
    assert album.artists == [artist]
    assert album.added_at == datetime(2024, 1, 15)


def test_saved_album_preserves_artist_order() -> None:
    a1 = Artist(id="a1", name="Primary")
    a2 = Artist(id="a2", name="Feature")
    album = SavedAlbum(
        id="alb1", name="Collab", artists=[a1, a2], added_at=datetime(2024, 1, 1)
    )
    assert album.artists[0] == a1
    assert album.artists[1] == a2


# ---------------------------------------------------------------------------
# Album model
# ---------------------------------------------------------------------------


def test_album_construction() -> None:
    album = Album(id="alb1", name="Album One", release_date="2021-05-14")
    assert album.id == "alb1"
    assert album.name == "Album One"
    assert album.release_date == "2021-05-14"


def test_album_is_frozen() -> None:
    album = Album(id="alb1", name="Album One", release_date="2021-05-14")
    with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
        album.name = "other"  # type: ignore[misc]
