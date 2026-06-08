## ADDED Requirements

### Requirement: --dry-run CLI flag activates Dry Sync mode
The script SHALL accept a `--dry-run` boolean flag. When present, `run()` SHALL be called with `dry_run=True`. When absent, `run()` SHALL be called with `dry_run=False` (normal Sync).

#### Scenario: Flag present
- **WHEN** the script is invoked with `--dry-run`
- **THEN** `run()` is called with `dry_run=True`

#### Scenario: Flag absent
- **WHEN** the script is invoked without `--dry-run`
- **THEN** `run()` is called with `dry_run=False`

#### Scenario: (no external I/O contract — flag parsing is local to main.py)

### Requirement: report_dry_sync_artist prints a per-artist Dry Sync summary
`report_dry_sync_artist` SHALL accept an artist name, a list of Albums that would be created, and a `genre: list[str] | None` parameter. The artist name line SHALL display the genre using the same rules as `prompt_for_folder`: non-empty list → `[tag1, tag2, ...]`, empty list → `[genre not found]`, `None` → `[failed to get genre]`. When the album list is non-empty, it SHALL print the artist name line followed by each album name prefixed with "Would create:". When the list is empty, it SHALL print the artist name line followed by "already up to date". It SHALL NOT block on user input.

#### Scenario: Albums would be created
- **WHEN** `report_dry_sync_artist` is called with a non-empty album list and a non-empty genre list
- **THEN** the artist name with genre tags is printed, followed by one "Would create: <album name>" line per album

#### Scenario: Artist already up to date
- **WHEN** `report_dry_sync_artist` is called with an empty album list and a genre
- **THEN** the artist name with genre tag is printed followed by "already up to date", and no blocking input call is made

#### Scenario: Genre not found
- **WHEN** `report_dry_sync_artist` is called with `genre=[]`
- **THEN** the artist name is printed with `[genre not found]` appended

#### Scenario: Genre fetch failed
- **WHEN** `report_dry_sync_artist` is called with `genre=None`
- **THEN** the artist name is printed with `[failed to get genre]` appended

#### Scenario: (no external I/O contract — output is local only)
