from __future__ import annotations

from spotify_playlist_creator.models import Album


def report_dry_sync_artist(
    artist_name: str, albums: list[Album], *, genre: list[str] | None = None
) -> None:
    if genre is None:
        genre_tag = "[failed to get genre]"
    elif not genre:
        genre_tag = "[genre not found]"
    else:
        genre_tag = f"[{', '.join(genre)}]"
    print(f"{artist_name} {genre_tag}")
    if albums:
        for album in albums:
            print(f"  Would create: {album.name}")
    else:
        print("  already up to date")
