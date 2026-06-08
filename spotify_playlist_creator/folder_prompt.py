from __future__ import annotations

from spotify_playlist_creator.create_playlists import CreatedPlaylist


def _genre_tag(genre: list[str] | None) -> str:
    if genre is None:
        return "[failed to get genre]"
    if not genre:
        return "[genre not found]"
    return f"[{', '.join(genre)}]"


def prompt_for_folder(
    upcoming_artist: str,
    previous_artist: str | None,
    previous_playlists: list[CreatedPlaylist],
    *,
    genre: list[str] | None = None,
) -> None:
    if previous_artist is not None and previous_playlists:
        print(f"\nNew playlists for {previous_artist} (drag into Artist Folder):")
        for playlist in reversed(previous_playlists):
            print(f"  - {playlist.name}")
        print(f"Drag the playlists above into the '{previous_artist}' Artist Folder.")

    print(
        f"\nCreate the Artist Folder for '{upcoming_artist}' {_genre_tag(genre)} in Spotify."
    )
    input("Press Enter when ready...")


def print_final_folder_message(
    artist_name: str,
    playlists: list[CreatedPlaylist],
    *,
    genre: list[str] | None = None,
) -> None:
    print(
        f"\nNew playlists for {artist_name} {_genre_tag(genre)} (drag into Artist Folder):"
    )
    for playlist in reversed(playlists):
        print(f"  - {playlist.name}")
    print(f"Drag the playlists above into the '{artist_name}' Artist Folder.")
