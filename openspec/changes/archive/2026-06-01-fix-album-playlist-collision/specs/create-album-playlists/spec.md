## MODIFIED Requirements

### Requirement: Create missing Album Playlists for an artist
For a given artist and their list of Albums, the system SHALL create a Spotify playlist for each Album that does not already have a matching playlist in the user's library. An Album has a matching playlist when a same-named playlist exists in the user's library whose first track belongs to that Album (determined by comparing the track's Spotify Album ID with the Album's ID). When multiple playlists share the same name, each is checked; if any matches, the Album is skipped. An empty same-named playlist (no tracks) SHALL be treated as a non-match — a new playlist is created. Albums are processed in descending release-date order (newest first). The playlist name SHALL match the Album name exactly as returned by Spotify. Already-matched playlists SHALL be left untouched.

#### Scenario: All Albums are new
- **WHEN** none of the artist's Albums have a matching playlist in the user's library
- **THEN** a playlist is created for every Album, in descending release-date order

#### Scenario: Empty Album list
- **WHEN** the artist has no qualifying Albums (empty list passed in)
- **THEN** no playlists are created and an empty list is returned

#### Scenario: Name collision — different album
- **WHEN** a playlist with the same name exists but its first track belongs to a different Album (Album ID does not match)
- **THEN** a new playlist is created for the Album regardless of the name collision

#### Scenario: Name collision — same album
- **WHEN** a playlist with the same name exists and its first track belongs to the same Album (Album ID matches)
- **THEN** the Album is skipped and no new playlist is created

#### Scenario: Name collision — empty playlist
- **WHEN** a playlist with the same name exists but contains no tracks
- **THEN** a new playlist is created for the Album (empty playlist cannot be fingerprinted)

#### Scenario: First-track fingerprint API call
- **WHEN** a same-named playlist is found for an Album
- **THEN** the system fetches the first track of that playlist using `GET /playlists/{id}/tracks?limit=1` and reads the track's `album.id` field to determine the match
