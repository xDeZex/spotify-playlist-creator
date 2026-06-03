## Context

`GET /me/playlists` returns owned and followed playlists. The fingerprinting step calls `GET /playlists/{id}/tracks` on same-named playlists, which returns 403 Forbidden for playlists owned by other users. The fix filters the candidate set to owned playlists only before any fingerprinting occurs.

## Goals / Non-Goals

**Goals:**
- Exclude followed playlists from the candidate set before fingerprinting
- Rename `fetch_user_playlists` to `fetch_owned_playlists` to reflect its narrowed contract

**Non-Goals:**
- Catching or recovering from 403 errors at the fingerprint step
- Caching the current user's ID across function calls

## Decisions

### Filter inside `fetch_owned_playlists`, not at the call site

The user ID fetch (`GET /me`) is encapsulated inside `fetch_owned_playlists` via a private helper `_fetch_current_user_id`. The caller passes only the token; the function is self-contained.

**Alternative considered:** Accept `user_id` as a parameter so the caller fetches it separately.

**Rejected because:** The user ID is only needed here. Exposing it as a parameter leaks an implementation detail and requires every caller to know about it. If it's needed elsewhere later, the helper can be promoted to public at that point.

### Filter by `owner.id`, not by catching 403

The playlist items from `GET /me/playlists` include an `owner.id` field. Comparing it against the current user's ID filters out followed playlists before any track-fetching occurs.

**Alternative considered:** Catch `RuntimeError` with "403" in the message inside `fetch_first_track_album_id` and treat it as a non-match.

**Rejected because:** Swallowing 403s hides real permission errors on playlists the user does own (e.g., collaborative playlists with revoked access). Proactive filtering is precise and doesn't require interpreting error messages.

## Risks / Trade-offs

- **One extra API call per Sync** (`GET /me`) → Negligible: single non-paginated call, no retry loop needed.
- **Test surface change** → All `fetch_owned_playlists` tests need `owner.id` in mock playlist items and a `GET /me` mock response; the auth-header test must assert both requests carry the token.
