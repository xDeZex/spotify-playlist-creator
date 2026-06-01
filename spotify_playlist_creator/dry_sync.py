from __future__ import annotations

from spotify_playlist_creator.models import Album


def report_dry_sync_artist(artist_name: str, albums: list[Album]) -> None:
    print(artist_name)
    if albums:
        for album in albums:
            print(f"  Would create: {album.name}")
    else:
        print("  already up to date")
