## ADDED Requirements

### Requirement: Create missing Album Playlists for an artist
For a given artist and their list of Albums, the system SHALL create a Spotify playlist for each Album that does not already have a matching playlist in the user's library. Albums are processed in descending release-date order (newest first) so that after creation the earliest album sits at the top of the Spotify library. The playlist name SHALL match the Album name exactly as returned by Spotify. Already-existing playlists SHALL be left untouched.

#### Scenario: All Albums are new
- **WHEN** none of the artist's Albums have an existing playlist in the user's library
- **THEN** a playlist is created for every Album, in descending release-date order

#### Scenario: Some Albums already have playlists
- **WHEN** a subset of the artist's Albums already have matching playlists in the user's library
- **THEN** only the Albums without a matching playlist have playlists created; existing playlists are unchanged

#### Scenario: All Albums already have playlists
- **WHEN** every one of the artist's Albums already has a matching playlist in the user's library
- **THEN** no playlists are created and an empty list is returned

#### Scenario: Single Album with no existing playlist
- **WHEN** the artist has exactly one Album and no matching playlist exists
- **THEN** exactly one playlist is created

#### Scenario: Empty Album list
- **WHEN** the artist has no qualifying Albums (empty list passed in)
- **THEN** no playlists are created and an empty list is returned

#### Scenario: Playlist name matching
- **WHEN** a playlist in the user's library has a name that exactly matches an Album name
- **THEN** that Album is treated as already having a playlist and is skipped

### Requirement: Populate newly created playlists with tracks
Immediately after creating an Album Playlist, the system SHALL fetch all tracks for the corresponding Album and add them to the playlist. Track order SHALL match the order returned by Spotify. When an album has more than 100 tracks, tracks SHALL be added in batches of 100, in order.

#### Scenario: Album with tracks
- **WHEN** a new Album Playlist is created for an Album with tracks
- **THEN** all tracks from that Album are added to the playlist in Spotify's track order

#### Scenario: Album with more than 100 tracks
- **WHEN** a new Album Playlist is created for an Album with more than 100 tracks
- **THEN** all tracks are added across multiple requests, each containing at most 100 tracks, in order

#### Scenario: Album with no tracks
- **WHEN** a new Album Playlist is created for an Album that has no tracks
- **THEN** the playlist is created and no track-add request is made

### Requirement: Return newly created playlists
The system SHALL return the list of Album Playlists created in the current call, in the order they were created (descending release-date). Already-existing playlists SHALL NOT appear in the returned list.

#### Scenario: Mix of new and existing
- **WHEN** 3 Albums are passed in and 2 already have playlists
- **THEN** the returned list contains exactly 1 entry — the newly created playlist

#### Scenario: Nothing created
- **WHEN** all Albums already have playlists
- **THEN** the returned list is empty
