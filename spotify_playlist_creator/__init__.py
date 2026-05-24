from spotify_playlist_creator.auth import SpotifyToken, authenticate


def run() -> None:
    token: SpotifyToken = authenticate()
    print(f"Spotify Playlist Creator - authenticated ({token.token_type})")
