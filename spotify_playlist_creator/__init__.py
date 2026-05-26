from spotify_playlist_creator.auth import SpotifyToken, authenticate
from spotify_playlist_creator.models import Artist, SavedAlbum
from spotify_playlist_creator.saved_albums import fetch_saved_albums

__all__ = ["SpotifyToken", "authenticate", "Artist", "SavedAlbum", "fetch_saved_albums"]


def run() -> None:
    token: SpotifyToken = authenticate()
    print(f"Spotify Playlist Creator - authenticated ({token.token_type})")
