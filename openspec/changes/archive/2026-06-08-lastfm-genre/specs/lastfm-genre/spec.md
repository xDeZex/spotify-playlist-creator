## ADDED Requirements

### Requirement: get_api_key reads LASTFM_API_KEY from environment and fails fast if missing
`get_api_key()` SHALL read the `LASTFM_API_KEY` environment variable and return it as a string. If the variable is not set, it SHALL raise a `RuntimeError` with a clear message before any network calls are made.

#### Scenario: Key is set
- **WHEN** `LASTFM_API_KEY` is present in the environment
- **THEN** `get_api_key()` returns its string value

#### Scenario: Key is missing
- **WHEN** `LASTFM_API_KEY` is not set in the environment
- **THEN** `get_api_key()` raises `RuntimeError` immediately

### Requirement: fetch_artist_genre returns the top genre tag by score or None
`fetch_artist_genre(artist_name, api_key)` SHALL call Last.fm's `artist.gettoptags` endpoint with the artist name and API key as query parameters. It SHALL return the tag with the highest count as a lowercase string. If the response contains no tags or the artist is not found (Last.fm error code 6), it SHALL return `None`. It SHALL raise `RuntimeError` on HTTP errors or network failures.

#### Scenario: Tags returned — top tag selected
- **WHEN** Last.fm returns a non-empty tag list for the artist
- **THEN** `fetch_artist_genre` returns the tag with the highest count as a string

#### Scenario: No tags or artist not found
- **WHEN** Last.fm returns an empty tag list or error code 6 (artist not found)
- **THEN** `fetch_artist_genre` returns `None`

#### Scenario: HTTP error propagates
- **WHEN** Last.fm returns an HTTP error status
- **THEN** `fetch_artist_genre` raises `RuntimeError`

#### Scenario: Correct query parameters forwarded to Last.fm
- **WHEN** `fetch_artist_genre("Tomoyo Harada", "mykey")` is called
- **THEN** the HTTP request targets `https://ws.audioscrobbler.com/2.0/` with `method=artist.gettoptags`, `artist=Tomoyo+Harada`, `api_key=mykey`, and `format=json`
