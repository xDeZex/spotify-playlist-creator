### Requirement: Fetch all saved albums
The system SHALL retrieve every album saved in the authenticated user's Spotify library by calling `GET /me/albums` and following the `next` cursor until all pages are exhausted.

#### Scenario: Single page of results
- **WHEN** the API response contains fewer than the page limit and `next` is null
- **THEN** the function returns all items from that single response

#### Scenario: Multiple pages of results
- **WHEN** the API response contains a non-null `next` URL
- **THEN** the function fetches subsequent pages until `next` is null and returns the concatenated list

#### Scenario: Empty library
- **WHEN** the user has no saved albums
- **THEN** the function returns an empty list

### Requirement: Return typed SavedAlbum objects
The system SHALL represent each saved album as a `SavedAlbum` dataclass in `models.py` containing: `id` (Spotify album ID), `name` (album title), `artists` (list of `Artist` objects, one per artist in Spotify's artist array), and `added_at` (timezone-naive UTC `datetime` of when the album was saved).

#### Scenario: Valid API album item
- **WHEN** an album item is received from the API
- **THEN** it is mapped to a `SavedAlbum` with the correct `id`, `name`, `artists`, and `added_at` fields populated

#### Scenario: Album with multiple artists
- **WHEN** an album item contains multiple artists in Spotify's artist array
- **THEN** all artists are stored in `SavedAlbum.artists` in the original order

### Requirement: Authenticated requests
The system SHALL use the persisted OAuth access token when calling the Spotify API and SHALL raise a clear error if no valid token is available.

#### Scenario: No token present
- **WHEN** `fetch_saved_albums()` is called and no token is stored on disk
- **THEN** the function raises an exception before making any API call
