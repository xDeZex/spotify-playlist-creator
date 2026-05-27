# Sync is additive-only

When the script runs, it only creates Artist Folders and Album Playlists that don't yet exist — it never deletes anything. If an album is un-saved from the library after a sync, its playlist remains. The rationale is that the user's intent is to build up an organised library over time; destructive sync behaviour would risk losing playlists the user has already curated or reordered.

## Consequences

Album Playlists are created in ascending release-date order so that the initial folder display matches chronological order (Spotify orders playlists within a folder by insertion time, with no API to reorder them). On subsequent Syncs, newly discovered releases are appended to the end of the folder regardless of where they fall chronologically — folder order is only guaranteed to be chronological after the very first Sync for an artist.
