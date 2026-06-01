## Context

`create_album_playlists` currently receives an `existing_names: set[str]` and skips any Album whose name appears in that set. This name-only check causes silent data loss when two Albums from different artists share a name. See ADR-0004 for the full decision record and alternatives considered.

## Goals / Non-Goals

**Goals:**
- Detect existing Album Playlists by Album identity (Spotify Album ID) rather than name alone
- Zero extra API calls in the common case (no name collision)
- No change to playlist names or descriptions visible to the user

**Non-Goals:**
- Handling playlists created outside this script
- Detecting renamed or manually edited playlists
- Modifying or cleaning up existing playlists

## Decisions

### Replace `set[str]` with `dict[str, list[str]]`

`fetch_user_playlist_names` returns a flat `set[str]`. This is replaced by a function returning `dict[str, list[str]]` — mapping each playlist name to all playlist IDs that carry that name. The list (bucket) handles the case where the user already has multiple playlists with the same name from prior runs.

### Fingerprint via first track's Album ID

On a name collision, fetch `GET /playlists/{id}/tracks?limit=1` for each same-named playlist and read `items[0].track.album.id`. If any bucket entry matches the candidate Album's ID, skip. If none match (or a playlist is empty), create. This is the cheapest unambiguous signal available without adding local state or mutating playlist metadata. See ADR-0004.

### Empty playlist → create

A playlist with no tracks cannot be fingerprinted. Treating it as a non-match means a new playlist is created. The old empty playlist is left untouched (additive-only, per ADR-0002). This is a safe fallback: worst case is a duplicate empty playlist, not missing data.

## Risks / Trade-offs

- **User manually cleared a playlist's tracks** → fingerprint fails → duplicate playlist created. Low probability; acceptable given the no-local-state constraint.
- **Multiple same-named playlists** → one extra API call per bucket entry on collision. Collision itself is rare; multiple same-named entries even rarer. Not a performance concern.
