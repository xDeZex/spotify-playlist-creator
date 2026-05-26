# Spotify Playlist Creator

A script that reads a user's Spotify saved albums and organizes them inside Spotify itself — creating one folder per artist, each containing one playlist per album.

## Language

**Saved Album**:
An album the user has saved to their Spotify library. Used only to determine which artists to include — not as the full set of albums to organize.
_Avoid_: Liked album, followed album, favorited album

**Artist Folder**:
A Spotify playlist folder named after a Spotify artist, containing Album Playlists for every Release by that artist. Two artists with the same name but different Spotify IDs produce two separate folders.
_Avoid_: Artist directory, artist group

**Artist**:
A Spotify artist identified by their Spotify ID. Two artists with the same name are distinct if their IDs differ.
_Avoid_: Band, musician

**Primary Artist**:
The first artist listed in Spotify's artist array for an album. Determines which Artist Folder an album belongs to.
_Avoid_: Main artist, lead artist

**Album Playlist**:
A Spotify playlist representing one album or EP — contains all tracks from that release — living inside an Artist Folder.
_Avoid_: Album copy, album mirror

**Release**:
A full album or EP by an artist. Singles and compilations are excluded. EPs are identified using Spotify's own classification rules: 4–6 tracks with ≤30 min total, or 1–3 tracks where at least one exceeds 10 min and total exceeds 30 min.
_Avoid_: Album (when the distinction between full albums and EPs matters)

**Sync**:
The script's run mode — for each artist in scope (respecting the Artist Limit), ensures every Release has an Album Playlist inside the artist's Artist Folder. Additive only: existing playlists and folders are never deleted, but new releases from known artists are picked up on each run. All names taken from Spotify as-is. See [ADR-0002](./docs/adr/0002-sync-is-additive-only.md).
_Avoid_: Refresh, rebuild, recreate

**Artist Limit**:
An optional cap on how many artists are processed in a single Sync. When set, the N artists whose albums were saved least recently are processed. Running with the same limit twice processes the same N artists — it is not a progress cursor.
_Avoid_: Batch size, chunk

## Example dialogue

> "I saved three Radiohead albums. Does the script create playlists only for those three?"

No — the Saved Albums tell the script *which artists* to include. Once Radiohead is discovered, the script fetches all of Radiohead's Releases from Spotify and creates an Album Playlist for each one inside the Radiohead Artist Folder.

> "What about the EP they released? Is that included?"

Yes, if it qualifies as a Release — meaning it meets Spotify's EP classification rules (4–6 tracks ≤30 min, or 1–3 tracks with one over 10 min and total over 30 min). Actual singles are excluded.

> "I un-saved one of those albums last week. Will its playlist be deleted next time I sync?"

No. Sync is additive only — it creates what's missing, never removes what's there.
