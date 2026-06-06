## MODIFIED Requirements

### Requirement: Create missing Album Playlists for an artist
For a given artist and their list of Albums, the system SHALL identify which Albums do not already have a matching playlist owned by the current user, and return them as a `list[Album]`. An Album has a matching playlist when a same-named playlist owned by the current user exists whose first track belongs to that Album (determined by comparing the track's Spotify Album ID with the Album's ID). Followed playlists owned by other users SHALL be excluded from consideration before any fingerprinting occurs. When multiple owned playlists share the same name, each is checked; if any matches, the Album is excluded from the result. An empty same-named playlist (no tracks) SHALL be treated as a non-match — the Album is included in the result. The returned list SHALL be sorted in descending release-date order (newest first). Already-matched playlists SHALL be left untouched.

#### Scenario: All Albums are new
- **WHEN** none of the artist's Albums have a matching playlist in the user's library
- **THEN** all Albums are returned, in descending release-date order

#### Scenario: Some Albums already have playlists
- **WHEN** a subset of the artist's Albums already have matching playlists in the user's library
- **THEN** only the Albums without a matching playlist are returned

#### Scenario: All Albums already have playlists
- **WHEN** every one of the artist's Albums already has a matching playlist in the user's library
- **THEN** an empty list is returned

#### Scenario: Empty Album list
- **WHEN** an empty album list is passed in
- **THEN** an empty list is returned

#### Scenario: Name collision — different album
- **WHEN** a playlist with the same name exists but its first track belongs to a different Album
- **THEN** the Album is included in the returned list

#### Scenario: Name collision — same album
- **WHEN** a playlist with the same name exists and its first track belongs to the same Album
- **THEN** the Album is excluded from the returned list

#### Scenario: Name collision — empty playlist
- **WHEN** a playlist with the same name exists but contains no tracks
- **THEN** the Album is included in the returned list (empty playlist cannot be fingerprinted)

#### Scenario: First-track fingerprint API call
- **WHEN** a same-named playlist is found for an Album
- **THEN** the system fetches the first item of that playlist using `GET /playlists/{id}/items?limit=1` and reads the item's `album.id` field via `items[0]["item"]["album"]["id"]` to determine the match

#### Scenario: Followed playlist with same name is ignored
- **WHEN** a followed playlist (owned by another user) has the same name as an Album
- **THEN** it is not fingerprinted and the Album is included in the returned list as if no same-named playlist existed

#### Scenario: Owned playlist with same name is fingerprinted
- **WHEN** a playlist owned by the current user has the same name as an Album
- **THEN** it is fingerprinted and the Album is excluded if the fingerprint matches

#### Scenario: Fetching owned playlists calls GET /me first
- **WHEN** the system fetches the candidate playlist set
- **THEN** it calls `GET /me` to obtain the current user's ID, then filters `GET /me/playlists` results to only those where `owner.id` equals the current user's ID

### Requirement: Execute step creates and populates playlists for pre-identified missing albums
Given a list of Albums already identified as missing (output of the planning step), the system SHALL create a Spotify playlist for each Album, populate it with all tracks from that Album, and return a `list[CreatedPlaylist]` in the order albums were processed. The playlist name SHALL match the Album name exactly as returned by Spotify. Track order SHALL match the order returned by Spotify. When an album has more than 100 tracks, tracks SHALL be added in batches of 100, in order.

#### Scenario: Albums with tracks
- **WHEN** the execute step is called with a non-empty list of Albums
- **THEN** a playlist is created and populated for each Album, in the order provided

#### Scenario: Album with more than 100 tracks
- **WHEN** the execute step processes an Album with more than 100 tracks
- **THEN** all tracks are added across multiple requests, each containing at most 100 tracks, in order

#### Scenario: Album with no tracks
- **WHEN** the execute step processes an Album that has no tracks
- **THEN** the playlist is created and no track-add request is made

#### Scenario: Empty list
- **WHEN** the execute step is called with an empty list
- **THEN** no API calls are made and an empty list is returned

#### Scenario: Playlist creation API call
- **WHEN** the execute step creates a playlist
- **THEN** it calls `POST /me/playlists` with the album name and `public: true`

#### Scenario: Track addition API call
- **WHEN** the execute step adds tracks to a playlist
- **THEN** it calls `POST /playlists/{id}/items` with the batch of track URIs
