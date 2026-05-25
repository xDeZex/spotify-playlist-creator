## Why

The core feature of the app requires reading the user's Spotify library, but no code yet fetches saved albums. Without this, the rest of the playlist-organization logic has no data to work with.

## What Changes

- Add a `fetch_saved_albums()` function that calls `GET /me/albums` and follows pagination until all albums are returned.
- Expose the result as a typed list of domain objects (`SavedAlbum`) for downstream use.

## Capabilities

### New Capabilities

- `saved-albums`: Fetches the authenticated user's full list of saved albums from the Spotify Web API, handling pagination transparently.

### Modified Capabilities

## Impact

- New module inside `spotify_playlist_creator/` implementing the fetch logic.
- Depends on the authenticated HTTP client already provided by the `spotify-auth` and `token-persistence` capabilities.
- No changes to existing modules or public API surface.
