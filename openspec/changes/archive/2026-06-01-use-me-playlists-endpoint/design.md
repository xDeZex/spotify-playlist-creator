## Context

`create_album_playlists` in `create_playlists.py` currently accepts a `user_id: str`
parameter and uses it to build `POST /v1/users/{user_id}/playlists`. The user ID is
only needed for this URL — it is not used anywhere else in the function. Spotify's
`POST /v1/me/playlists` endpoint is functionally identical but authenticates via the
bearer token instead, removing the need to pass a user ID at all.

## Goals / Non-Goals

**Goals:**
- Swap the playlist creation endpoint from `/users/{user_id}/playlists` to `/me/playlists`
- Remove `user_id` from `create_album_playlists`' signature

**Non-Goals:**
- Changing any playlist-creation behavior
- Touching `fetch_user_playlists` (already uses `/me/playlists`)
- Adding retry logic or error handling

## Decisions

**Use `/me/playlists` over `/users/{user_id}/playlists`**

Both endpoints create a playlist for the authenticated user. The `/me/` variant
requires no extra ID resolution and is consistent with how all other endpoints in
this codebase are already written (`/me/albums`, `/me/playlists` for fetching).
No alternative is worth considering — this is a straight drop-in.

## Risks / Trade-offs

- No known risks. Both endpoints have identical behavior and the same OAuth scopes.
