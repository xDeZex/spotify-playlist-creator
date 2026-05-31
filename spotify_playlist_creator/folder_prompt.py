from __future__ import annotations

from spotify_playlist_creator.create_playlists import CreatedPlaylist


def prompt_for_folder(
    artist_name: str, created_playlists: list[CreatedPlaylist]
) -> None:
    if not created_playlists:
        return

    print(f"\nArtist: {artist_name}")
    print("New playlists created:")
    for playlist in created_playlists:
        print(f"  - {playlist.name}")
    print(
        "Please create or update the Artist Folder in Spotify and place the playlists inside it."
    )
    input("Press Enter when done...")
