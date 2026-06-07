## Why

Spotify rate-limits write endpoints far more aggressively than read endpoints — playlist creation has produced Retry-After values of ~80,000 s (~22 hours). The current uniform 0.2 s proactive delay offers no protection against this.

## What Changes

- `api_request` applies a 1 s proactive delay before POST requests and retains the 0.2 s delay for GET requests, detected automatically via body presence
- `_REQUEST_DELAY` constant renamed to `_READ_DELAY`; new `_WRITE_DELAY = 1.0` constant added
- `_proactive_delay` signature updated to accept `is_write: bool`
- Conftest fixture updated to match new signature

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `api-request`: adds proactive delay requirements — differentiated by HTTP method (GET vs POST)

## Impact

- `spotify_playlist_creator/api.py` — constants, `_proactive_delay`, `api_request`
- `tests/conftest.py` — `_no_proactive_delay` fixture lambda
- `tests/test_api.py` — any tests that assert on proactive delay behaviour
