from __future__ import annotations

from unittest.mock import patch

import pytest

from spotify_playlist_creator.create_playlists import CreatedPlaylist
from spotify_playlist_creator.folder_prompt import (
    print_final_folder_message,
    prompt_for_folder,
)

# ---------------------------------------------------------------------------
# Group 3: prompt_for_folder — pre-creation blocking prompt
# ---------------------------------------------------------------------------


def test_prompt_for_folder_first_artist_shows_upcoming_folder_instruction(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Adversarial: previous_artist=None so only upcoming folder instruction shown
    with patch("builtins.input", return_value=""):
        prompt_for_folder("Upcoming Artist", None, [])

    out = capsys.readouterr().out
    assert "Upcoming Artist" in out
    assert "Artist Folder" in out


def test_prompt_for_folder_first_artist_blocks_on_input() -> None:
    input_called = [False]

    def fake_input(prompt: str = "") -> str:
        input_called[0] = True
        return ""

    with patch("builtins.input", side_effect=fake_input):
        prompt_for_folder("Artist", None, [])

    assert input_called[0]


def test_prompt_for_folder_subsequent_artist_lists_previous_playlists_newest_first(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Adversarial: playlists given oldest-first; output must be newest-first
    previous_playlists = [
        CreatedPlaylist(name="Older Album", id="p1"),
        CreatedPlaylist(name="Newer Album", id="p2"),
    ]
    with patch("builtins.input", return_value=""):
        prompt_for_folder("Next Artist", "Prev Artist", previous_playlists)

    out = capsys.readouterr().out
    older_pos = out.index("Older Album")
    newer_pos = out.index("Newer Album")
    assert newer_pos < older_pos, "Newer Album must appear before Older Album"


def test_prompt_for_folder_subsequent_artist_shows_drag_and_upcoming_folder_instructions(
    capsys: pytest.CaptureFixture[str],
) -> None:
    previous_playlists = [
        CreatedPlaylist(name="Old Album", id="p1"),
        CreatedPlaylist(name="New Album", id="p2"),
    ]
    with patch("builtins.input", return_value=""):
        prompt_for_folder("Next Artist", "Prev Artist", previous_playlists)

    out = capsys.readouterr().out
    assert "Prev Artist" in out
    assert "Next Artist" in out


def test_prompt_for_folder_subsequent_artist_blocks_on_input() -> None:
    input_called = [False]

    def fake_input(prompt: str = "") -> str:
        input_called[0] = True
        return ""

    previous_playlists = [CreatedPlaylist(name="Album", id="p1")]
    with patch("builtins.input", side_effect=fake_input):
        prompt_for_folder("Next Artist", "Prev Artist", previous_playlists)

    assert input_called[0]


# ---------------------------------------------------------------------------
# Group 4: print_final_folder_message — non-blocking
# ---------------------------------------------------------------------------


def test_print_final_folder_message_lists_playlists_newest_first(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Adversarial: playlists given oldest-first; output must be newest-first
    playlists = [
        CreatedPlaylist(name="Older Album", id="p1"),
        CreatedPlaylist(name="Newer Album", id="p2"),
    ]
    print_final_folder_message("Some Artist", playlists)

    out = capsys.readouterr().out
    older_pos = out.index("Older Album")
    newer_pos = out.index("Newer Album")
    assert newer_pos < older_pos, "Newer Album must appear before Older Album"


def test_print_final_folder_message_does_not_block() -> None:
    # Adversarial: input must never be called
    playlists = [CreatedPlaylist(name="Album", id="p1")]
    with patch("builtins.input") as mock_input:
        print_final_folder_message("Artist", playlists)

    mock_input.assert_not_called()


def test_print_final_folder_message_shows_artist_and_drag_instruction(
    capsys: pytest.CaptureFixture[str],
) -> None:
    playlists = [CreatedPlaylist(name="My Album", id="p1")]
    print_final_folder_message("My Artist", playlists)

    out = capsys.readouterr().out
    assert "My Artist" in out
    assert "My Album" in out


def test_prompt_for_folder_suppresses_previous_section_when_previous_playlists_empty(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Adversarial: previous_artist set but previous_playlists empty — must not show
    # a misleading "drag into folder" section with no playlists listed
    with patch("builtins.input", return_value=""):
        prompt_for_folder("Next Artist", "Prev Artist", [])

    out = capsys.readouterr().out
    assert "Prev Artist" not in out
