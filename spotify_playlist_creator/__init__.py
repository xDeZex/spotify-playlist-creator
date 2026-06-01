from spotify_playlist_creator.artist_releases import fetch_artist_releases
from spotify_playlist_creator.auth import SpotifyToken, authenticate
from spotify_playlist_creator.classify_releases import classify_releases
from spotify_playlist_creator.create_playlists import (
    create_album_playlists,
    fetch_user_playlists,
)
from spotify_playlist_creator.folder_prompt import prompt_for_folder
from spotify_playlist_creator.models import Artist, SavedAlbum
from spotify_playlist_creator.saved_albums import derive_artists, fetch_saved_albums

# __all__ declares the public API; the remaining imports are internal to run()
# and are at module level so tests can patch them at spotify_playlist_creator.<name>.
__all__ = [
    "SpotifyToken",
    "authenticate",
    "Artist",
    "SavedAlbum",
    "fetch_saved_albums",
]


def run() -> None:
    token: SpotifyToken = authenticate()
    saved_albums = fetch_saved_albums(token)
    artists = derive_artists(saved_albums)
    existing_playlists = fetch_user_playlists(token)
    for artist in artists:
        raw_releases = fetch_artist_releases(token, artist.id)
        albums = classify_releases(token, raw_releases)
        created = create_album_playlists(token, albums, existing_playlists)
        if created:
            prompt_for_folder(artist.name, created)
