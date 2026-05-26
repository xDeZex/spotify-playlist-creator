## MODIFIED Requirements

### Requirement: Return typed SavedAlbum objects
The system SHALL represent each saved album as a `SavedAlbum` dataclass in `models.py` containing: `id` (Spotify album ID), `name` (album title), `artists` (list of `Artist` objects, one per artist in Spotify's artist array), and `added_at` (timezone-naive UTC `datetime` of when the album was saved).

#### Scenario: Valid API album item
- **WHEN** an album item is received from the API
- **THEN** it is mapped to a `SavedAlbum` with the correct `id`, `name`, `artists`, and `added_at` fields populated

#### Scenario: Album with multiple artists
- **WHEN** an album item contains multiple artists in Spotify's artist array
- **THEN** all artists are stored in `SavedAlbum.artists` in the original order
