## MODIFIED Requirements

### Requirement: Fetch all saved albums
The system SHALL retrieve saved albums from the authenticated user's Spotify library by calling `GET /me/albums`. When `limit` is `None`, the function follows the `next` cursor until all pages are exhausted and returns the full list. When `limit` is set to N, the function MAY stop before exhausting all pages, provided the returned albums contain at least N distinct primary artists (or all albums if the library has fewer than N distinct primary artists).

#### Scenario: No limit — full fetch
- **WHEN** `fetch_saved_albums` is called with `limit=None` and the library spans multiple pages
- **THEN** the function follows every `next` cursor and returns all saved albums

#### Scenario: Limit set — stops early
- **WHEN** `fetch_saved_albums` is called with `limit=N` and the library contains more than N distinct primary artists across multiple pages
- **THEN** the function returns without fetching all pages, and the returned albums contain at least N distinct primary artists

#### Scenario: Limit set but library is empty
- **WHEN** `fetch_saved_albums` is called with `limit=N` and the user has no saved albums
- **THEN** the function returns an empty list

## ADDED Requirements

### Requirement: fetch_saved_albums accepts an optional limit parameter
`fetch_saved_albums` SHALL accept a keyword-only argument `limit: int | None = None`. When `limit` is `None`, behaviour is identical to the previous implementation. When `limit` is a positive integer, the function uses a backward-pagination strategy to minimise API calls.

#### Scenario: Calling without limit
- **WHEN** `fetch_saved_albums(token)` is called with no `limit` argument
- **THEN** the function behaves as before: all pages are fetched in forward order

#### Scenario: Calling with limit
- **WHEN** `fetch_saved_albums(token, limit=4)` is called
- **THEN** the function uses backward pagination and returns once at least 4 distinct primary artists are found

#### Scenario: Signature is backward-compatible
- **WHEN** existing call sites that omit `limit` are not modified
- **THEN** they continue to work without error

### Requirement: Backward pagination probe
When `limit` is set and `total > 50`, `fetch_saved_albums` SHALL make one probe request at `offset=0` to determine `total`, then fetch pages from the last-page offset backwards toward `offset=50`, stopping as soon as the collected albums contain at least N distinct primary artists. If the backward sweep exhausts all pages without reaching N distinct artists, the probe page's items SHALL be included in the result.

#### Scenario: Probe reveals single page
- **WHEN** `fetch_saved_albums` is called with `limit=N` and `total <= 50`
- **THEN** the probe's items are returned directly without any further requests

#### Scenario: Backward sweep reaches stopping condition
- **WHEN** the backward sweep collects albums from the last page and distinct primary artists ≥ N
- **THEN** no further pages are fetched and the collected albums are returned

#### Scenario: Probe request is always first
- **WHEN** `fetch_saved_albums` is called with `limit=N` and `total > 50`
- **THEN** the first API call is always to `offset=0` (the probe), and subsequent calls use decreasing offsets

### Requirement: Pagination status reflects actual calls made
When `limit` is set, `fetch_saved_albums` SHALL emit status messages in the same format as the unlimited case — `fetching saved albums (N/total_pages)...` — where N increments once per API call made (probe counts as call 1, each backward page increments N further).

#### Scenario: Status during limit fetch
- **WHEN** `fetch_saved_albums` is called with `limit=4` and 15 total pages exist, stopping after 3 calls
- **THEN** status messages `(1/15)`, `(2/15)`, `(3/15)` are emitted in order

#### Scenario: Status for single-page library with limit
- **WHEN** `fetch_saved_albums` is called with `limit=N` and `total <= 50`
- **THEN** exactly one status message `(1/1)` is emitted
