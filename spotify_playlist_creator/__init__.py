import sys

from spotify_playlist_creator import status
from spotify_playlist_creator.artist_releases import fetch_artist_releases
from spotify_playlist_creator.auth import SpotifyToken, authenticate
from spotify_playlist_creator.classify_releases import classify_releases
from spotify_playlist_creator.create_playlists import (
    create_album_playlists,
    find_missing_album_playlists,
)
from spotify_playlist_creator.dry_sync import report_dry_sync_artist
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


def run(limit: int | None = None, dry_run: bool = False) -> None:
    def _write_status(msg: str) -> None:
        sys.stdout.write(msg)
        sys.stdout.flush()

    status.configure(_write_status)
    token: SpotifyToken = authenticate()
    saved_albums = fetch_saved_albums(token)
    artists = derive_artists(saved_albums)[:limit]
    n = len(artists)
    existing_playlists: dict[str, list[str]] = {}  # fetch_owned_playlists(token)
    for i, artist in enumerate(artists, 1):
        status.set_context(f"[{i}/{n}] {artist.name}")
        raw_releases = fetch_artist_releases(token, artist.id)
        albums = classify_releases(token, raw_releases)
        new_albums = find_missing_album_playlists(token, albums, existing_playlists)
        if dry_run:
            report_dry_sync_artist(artist.name, new_albums)
        else:
            created = create_album_playlists(token, new_albums)
            if created:
                prompt_for_folder(artist.name, created)
    status.clear()
