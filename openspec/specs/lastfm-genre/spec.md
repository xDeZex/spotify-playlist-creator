## ADDED Requirements

### Requirement: get_api_key reads the Last.fm API key from the environment
`get_api_key` SHALL read the `LASTFM_API_KEY` environment variable and return its value as a string. If the variable is not set or is empty, it SHALL raise a descriptive error indicating that the key is missing.

#### Scenario: Key present
- **WHEN** `LASTFM_API_KEY` is set to a non-empty string
- **THEN** `get_api_key` returns that string

#### Scenario: Key missing
- **WHEN** `LASTFM_API_KEY` is not set
- **THEN** `get_api_key` raises an error with a message indicating the key is missing

#### Scenario: Key empty
- **WHEN** `LASTFM_API_KEY` is set to an empty string
- **THEN** `get_api_key` raises an error with a message indicating the key is missing

### Requirement: fetch_artist_genre returns the top three genre tags by score
`fetch_artist_genre` SHALL accept an artist name and a Last.fm API key, call the Last.fm `artist.gettoptags` endpoint for that artist, and return a `list[str]` of the top three tag names sorted by count descending, each lowercased. If the artist has no tags or is not found (Last.fm error code 6), it SHALL return an empty list. It SHALL raise `RuntimeError` on HTTP errors or network failures.

#### Scenario: Artist has tags — top three returned in order
- **WHEN** `fetch_artist_genre` is called and the Last.fm response contains one or more tags
- **THEN** up to three tags are returned as a list, sorted by count descending, each lowercased

#### Scenario: Artist has no tags
- **WHEN** the Last.fm response contains an empty tag list or error code 6 (artist not found)
- **THEN** an empty list is returned

#### Scenario: HTTP error or network failure propagates
- **WHEN** the Last.fm API returns an HTTP error status or a network exception occurs
- **THEN** `fetch_artist_genre` raises `RuntimeError`
