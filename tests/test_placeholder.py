def test_package_is_importable() -> None:
    import spotify_playlist_creator

    assert hasattr(spotify_playlist_creator, "run")
