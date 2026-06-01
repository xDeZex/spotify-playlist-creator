### Requirement: CLI accepts optional --limit argument
`main.py` SHALL accept an optional `--limit N` integer argument via argparse. When provided, it SHALL be passed to `run()` as the `limit` parameter. When omitted, `run()` SHALL be called with `limit=None`.

#### Scenario: --limit provided
- **WHEN** the script is invoked with `--limit 5`
- **THEN** `run()` is called with `limit=5`

#### Scenario: --limit omitted
- **WHEN** the script is invoked with no arguments
- **THEN** `run()` is called with `limit=None`

#### Scenario: --limit forwarded correctly
- **WHEN** the script is invoked with `--limit 3`
- **THEN** argparse parses the value as integer `3` and passes it to `run()`

### Requirement: --limit rejects values ≤0
`main.py` SHALL reject `--limit` values of 0 or below with an `argparse.ArgumentTypeError`, causing the script to exit with a non-zero status and a human-readable error message before any API calls are made.

#### Scenario: Zero is rejected
- **WHEN** the script is invoked with `--limit 0`
- **THEN** the script exits with a non-zero status and prints an error message; no API calls are made

#### Scenario: Negative value is rejected
- **WHEN** the script is invoked with `--limit -1`
- **THEN** the script exits with a non-zero status and prints an error message; no API calls are made

#### Scenario: (no external I/O — rejection happens before authentication)
