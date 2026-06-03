## MODIFIED Requirements

### Requirement: Create missing Album Playlists for an artist
For a given artist and their list of Albums, the system SHALL identify which Albums do not already have a matching playlist owned by the current user, and return them as a `list[Album]`. An Album has a matching playlist when a same-named playlist owned by the current user exists whose first track belongs to that Album (determined by comparing the track's Spotify Album ID with the Album's ID). Followed playlists owned by other users SHALL be excluded from consideration before any fingerprinting occurs. When multiple owned playlists share the same name, each is checked; if any matches, the Album is excluded from the result. An empty same-named playlist (no tracks) SHALL be treated as a non-match — the Album is included in the result. The returned list SHALL be sorted in descending release-date order (newest first). Already-matched playlists SHALL be left untouched.

#### Scenario: Followed playlist with same name is ignored
- **WHEN** a followed playlist (owned by another user) has the same name as an Album
- **THEN** it is not fingerprinted and the Album is included in the returned list as if no same-named playlist existed

#### Scenario: Owned playlist with same name is fingerprinted
- **WHEN** a playlist owned by the current user has the same name as an Album
- **THEN** it is fingerprinted and the Album is excluded if the fingerprint matches

#### Scenario: Fetching owned playlists calls GET /me first
- **WHEN** the system fetches the candidate playlist set
- **THEN** it calls `GET /me` to obtain the current user's ID, then filters `GET /me/playlists` results to only those where `owner.id` equals the current user's ID
