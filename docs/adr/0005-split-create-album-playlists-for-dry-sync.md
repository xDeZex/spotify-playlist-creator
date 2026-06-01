# Split create_album_playlists into plan and execute steps for Dry Sync

`create_album_playlists` was split into two functions: one that identifies which Albums are missing a playlist (read-only), and one that performs the actual writes. This makes Dry Sync possible — the read step runs in both modes, the write step is skipped in Dry Sync. The alternative was threading a `dry_run: bool` flag through the existing function, but that mixes the dedup logic and the write logic in a single function with a mode switch, making both harder to test and reason about independently.
