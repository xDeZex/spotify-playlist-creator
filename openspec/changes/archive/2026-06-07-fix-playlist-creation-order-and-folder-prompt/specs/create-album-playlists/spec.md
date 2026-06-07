## MODIFIED Requirements

### Requirement: Create missing Album Playlists for an artist
For a given artist and their list of Albums, the system SHALL identify which Albums do not already have a matching playlist owned by the current user, and return them as a `list[Album]`. An Album has a matching playlist when a same-named playlist owned by the current user exists whose first track belongs to that Album (determined by comparing the track's Spotify Album ID with the Album's ID). Followed playlists owned by other users SHALL be excluded from consideration before any fingerprinting occurs. When multiple owned playlists share the same name, each is checked; if any matches, the Album is excluded from the result. An empty same-named playlist (no tracks) SHALL be treated as a non-match — the Album is included in the result. The returned list SHALL be sorted in ascending release-date order (oldest first). Already-matched playlists SHALL be left untouched.

#### Scenario: All Albums are new
- **WHEN** none of the artist's Albums have a matching playlist in the user's library
- **THEN** all Albums are returned, in ascending release-date order (oldest first)

#### Scenario: All Albums already have playlists
- **WHEN** every one of the artist's Albums already has a matching playlist in the user's library
- **THEN** an empty list is returned

#### Scenario: (no external I/O contract — sort order is local)
