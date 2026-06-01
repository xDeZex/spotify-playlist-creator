# Album Playlist detection via first-track fingerprint

When checking whether an Album Playlist already exists for a given Album, name matching alone is insufficient — two Albums from different artists can share the same name. We detect existing Album Playlists by name first, then resolve collisions by fetching the first track of each same-named playlist and comparing its Spotify Album ID against the candidate Album's ID. A match means the playlist represents that Album; no match means a new playlist should be created.

## Considered Options

- **Name prefix (`{artist} - {album name}`)** — guarantees uniqueness but is a breaking change for existing playlists and clutters playlist names.
- **Local mapping file (album ID → playlist ID)** — exact, but introduces stateful file that can drift out of sync with Spotify (manual deletions, lost file).
- **Playlist description field** — embed album ID in the description; exact and stateless, but the ID is visible to the user inside Spotify.
- **First-track fingerprint (chosen)** — uses existing playlist content as a proxy for album identity; no naming changes, no local state, no user-visible metadata, zero extra API calls in the common case (no collision).

## Consequences

An empty playlist (no tracks) cannot be fingerprinted. In that case the script treats it as a non-match and creates a new playlist.
