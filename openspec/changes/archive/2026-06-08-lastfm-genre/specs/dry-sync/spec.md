## MODIFIED Requirements

### Requirement: report_dry_sync_artist prints a per-artist Dry Sync summary
`report_dry_sync_artist` SHALL accept an artist name, a list of Albums that would be created, and a `genre: str | None` parameter. The artist name line SHALL include the genre as `[{genre}]`; if `genre` is `None` it SHALL display `[genre not found]`. When the album list is non-empty, it SHALL print the artist name (with genre) followed by each album name prefixed with "Would create:". When the list is empty, it SHALL print the artist name (with genre) followed by "already up to date". It SHALL NOT block on user input.

#### Scenario: Albums would be created — genre known
- **WHEN** `report_dry_sync_artist` is called with a non-empty album list and `genre="j-pop"`
- **THEN** the artist name line includes `[j-pop]`, followed by one "Would create: <album name>" line per album

#### Scenario: Artist already up to date — no genre
- **WHEN** `report_dry_sync_artist` is called with an empty album list and `genre=None`
- **THEN** the artist name line includes `[genre not found]`, followed by "already up to date"

#### Scenario: (no external I/O contract — output is local only)
