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
`report_dry_sync_artist` SHALL accept an artist name and a list of Albums that would be created. When the list is non-empty, it SHALL print the artist name followed by each album name prefixed with "Would create:". When the list is empty, it SHALL print the artist name followed by "already up to date". It SHALL NOT block on user input.

#### Scenario: Albums would be created
- **WHEN** `report_dry_sync_artist` is called with an artist name and a non-empty album list
- **THEN** the artist name is printed, followed by one "Would create: <album name>" line per album

#### Scenario: Artist already up to date
- **WHEN** `report_dry_sync_artist` is called with an artist name and an empty album list
- **THEN** the artist name is printed followed by "already up to date", and no blocking input call is made

#### Scenario: (no external I/O contract — output is local only)
