from __future__ import annotations

from unittest.mock import patch

import pytest

from spotify_playlist_creator.create_playlists import CreatedPlaylist
from spotify_playlist_creator.folder_prompt import prompt_for_folder

# ---------------------------------------------------------------------------
# Group 3: prompt_for_folder
# ---------------------------------------------------------------------------


def test_prompt_for_folder_prints_artist_and_playlist_names(
    capsys: pytest.CaptureFixture[str],
) -> None:
    playlists = [
        CreatedPlaylist(name="Debut Album", id="p1"),
        CreatedPlaylist(name="Second Album", id="p2"),
    ]

    with patch("builtins.input", return_value=""):
        prompt_for_folder("Artist Name", playlists)

    out = capsys.readouterr().out
    assert "Artist Name" in out
    assert "Debut Album" in out
    assert "Second Album" in out


def test_prompt_for_folder_blocks_on_input(capsys: pytest.CaptureFixture[str]) -> None:
    playlists = [CreatedPlaylist(name="Some Album", id="p1")]
    input_called = [False]

    def fake_input(prompt: str = "") -> str:
        input_called[0] = True
        return ""

    with patch("builtins.input", side_effect=fake_input):
        prompt_for_folder("Artist", playlists)

    assert input_called[0]
    out = capsys.readouterr().out
    assert "Artist Folder" in out
    assert "Some Album" in out


def test_prompt_for_folder_no_output_for_empty_list(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with patch("builtins.input") as mock_input:
        prompt_for_folder("Artist", [])

    mock_input.assert_not_called()
    assert capsys.readouterr().out == ""
