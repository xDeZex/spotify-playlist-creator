### Requirement: Represent artists as typed objects
The system SHALL represent each Spotify artist as an `Artist` dataclass in `models.py` containing `id` (Spotify artist ID) and `name` (artist name string). Two artists with the same name but different IDs are distinct.

#### Scenario: Artist construction
- **WHEN** an artist ID and name are provided
- **THEN** an `Artist` instance is created with those exact values

### Requirement: Derive ordered artist list from saved albums
The system SHALL provide a `derive_artists(albums: list[SavedAlbum]) -> list[Artist]` function in `saved_albums.py` that extracts the primary artist from each saved album, deduplicates by Spotify artist ID, and returns the list ordered by oldest `added_at` first (the artist's position is determined by the earliest `added_at` among their saved albums).

#### Scenario: Empty album list
- **WHEN** `derive_artists()` is called with an empty list
- **THEN** it returns an empty list

#### Scenario: Single album
- **WHEN** a single saved album is provided
- **THEN** the function returns a list containing only the primary artist of that album

#### Scenario: Multiple albums by the same artist
- **WHEN** multiple saved albums share the same primary artist ID
- **THEN** the artist appears exactly once in the result

#### Scenario: Ordering by oldest saved album
- **WHEN** albums by different artists are provided with different `added_at` values
- **THEN** the artist whose album was saved earliest appears first in the result

#### Scenario: Artist with multiple albums uses earliest date for ordering
- **WHEN** an artist has multiple saved albums with different `added_at` values
- **THEN** their position in the result is determined by their earliest `added_at`

#### Scenario: Primary artist only
- **WHEN** a saved album has multiple artists
- **THEN** only the first artist (`artists[0]`) is used; the remaining artists are ignored
