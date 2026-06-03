## Why

`GET /me/playlists` returns both playlists the user owns and playlists they follow from other users. When `find_missing_album_playlists` fingerprints same-named playlists, it calls `GET /playlists/{id}/tracks` on all of them — including followed playlists owned by others, which return 403 Forbidden and crash the script.

## What Changes

- `fetch_user_playlists` is renamed to `fetch_owned_playlists` and narrowed to return only playlists owned by the current user, by comparing each playlist's `owner.id` against the ID returned by `GET /me`.
- All callers of `fetch_user_playlists` are updated to use `fetch_owned_playlists`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `create-album-playlists`: The requirement's "user's library" is clarified to mean playlists **owned** by the current user — followed playlists are excluded from the candidate set before fingerprinting begins.

## Impact

- `spotify_playlist_creator/create_playlists.py`: rename + filter logic + private helper
- `spotify_playlist_creator/__init__.py`: updated import
- `tests/test_create_playlists.py`: updated helper and tests to include `owner.id`
- `tests/test_run.py`: updated mock target name
- One additional API call (`GET /me`) per Sync run
