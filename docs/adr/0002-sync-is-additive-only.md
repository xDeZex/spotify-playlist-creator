# Sync is additive-only

When the script runs, it only creates Artist Folders and Album Playlists that don't yet exist — it never deletes anything. If an album is un-saved from the library after a sync, its playlist remains. The rationale is that the user's intent is to build up an organised library over time; destructive sync behaviour would risk losing playlists the user has already curated or reordered.

## Consequences

Album Playlists are created in descending release-date order (newest first). Spotify's library shows most-recently-added items at the top, so after creation the earliest album sits at the top of the list — the first one the user grabs when filling the Artist Folder, landing it first (and therefore topmost) inside the folder. Chronological order inside the folder is only guaranteed after the first Sync for an artist; newly created playlists on subsequent Syncs appear at the top of the library and must be inserted into the folder manually at the correct position.
