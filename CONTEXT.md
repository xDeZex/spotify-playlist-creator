# Spotify Playlist Creator

A script that reads a user's Spotify saved albums and organizes them inside Spotify itself — creating one Album Playlist per Album per artist, then prompting the user to place them into an Artist Folder.

## Language

**Saved Album**:
An album the user has saved to their Spotify library. Used only to determine which artists to include — not as the full set of albums to organize.
_Avoid_: Liked album, followed album, favorited album

**Artist Folder**:
A Spotify playlist folder named after a Spotify artist, containing Album Playlists for every Album by that artist. Two artists with the same name but different Spotify IDs produce two separate folders.
_Avoid_: Artist directory, artist group

**Artist**:
A Spotify artist identified by their Spotify ID. Two artists with the same name are distinct if their IDs differ.
_Avoid_: Band, musician

**Genre**:
A musical style tag sourced from Last.fm for an Artist. Displayed during a Sync to guide the user when placing an Artist Folder into the correct genre folder.
_Avoid_: Tag, category, style

**Primary Artist**:
The first artist listed in Spotify's artist array for an album. Determines which Artist Folder an album belongs to.
_Avoid_: Main artist, lead artist

**Album Playlist**:
A Spotify playlist owned by the current user, representing one Album — contains all tracks from that Album — living inside an Artist Folder.
_Avoid_: Album copy, album mirror

**Album**:
A release from an artist's discography that qualifies for organisation: either a full album (Spotify `album_type: "album"`) or an EP. EPs are identified using Spotify's own classification rules: 4–6 tracks with ≤30 min total, or 1–3 tracks where at least one exceeds 10 min and total exceeds 30 min. Actual singles are excluded.
_Avoid_: Release

**Sync**:
The script's run mode — for each artist in scope (respecting the Artist Limit), ensures every Album has an Album Playlist. "Has" is determined by Album identity (Spotify Album ID), not by playlist name — two Albums with the same name are distinct. Artists with no new playlists are skipped silently. Additive only: existing playlists are never deleted, but new Albums from known artists are picked up on each run. All names taken from Spotify as-is. See [ADR-0002](./docs/adr/0002-sync-is-additive-only.md). When an artist has new Albums: the script first prompts the user to create and position the Artist Folder in Spotify, then creates Album Playlists oldest-release-date first (so the newest Album lands at the top of Spotify's "recently added" view). The prompt for each subsequent artist also lists the previous artist's new playlists newest-first, letting the user drag them into the folder before continuing. After the final artist the script prints the last batch and exits without blocking.
_Avoid_: Refresh, rebuild, recreate

**Dry Sync**:
A read-only run of the script that performs the same traversal as a Sync — fetching Saved Albums, deriving Artists, checking existing Album Playlists — but skips all writes. Prints what Album Playlists would be created without creating them. Does not pause to prompt the user.
_Avoid_: Preview, test run, simulation

**Artist Limit**:
An optional cap on how many artists are processed in a single Sync. When set, the N artists whose albums were saved least recently are processed. Running with the same limit twice processes the same N artists — it is not a progress cursor.
_Avoid_: Batch size, chunk

## Example dialogue

> "I saved three Radiohead albums. Does the script create playlists only for those three?"

No — the Saved Albums tell the script *which artists* to include. Once Radiohead is discovered, the script fetches all of Radiohead's Albums from Spotify and creates an Album Playlist for each one, then prompts you to place them in the Radiohead Artist Folder.

> "What about the EP they released? Is that included?"

Yes — EPs qualify as Albums. If it meets Spotify's EP rules (4–6 tracks ≤30 min, or 1–3 tracks with one over 10 min and total over 30 min), it gets an Album Playlist just like a full album would.

> "I un-saved one of those albums last week. Will its playlist be deleted next time I sync?"

No. Sync is additive only — it creates what's missing, never removes what's there.

> "Does the script put the playlists into the folder for me?"

No — but the flow is designed around you doing it. Before creating playlists for an artist, the script pauses and asks you to create and position the Artist Folder in Spotify. Once you press Enter, it creates the Album Playlists oldest-first so the newest album sits at the top of "recently added." The prompt for the next artist lists the previous batch newest-first so you know what to drag in before moving on. After the last artist, the script prints the final list and exits — no extra wait.
