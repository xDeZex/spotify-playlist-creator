## ADDED Requirements

### Requirement: Prompt user to place new playlists into Artist Folder
After processing an artist, if one or more Album Playlists were newly created, the system SHALL print the artist name and the names of the newly created playlists, instruct the user to place them in the Artist Folder in Spotify, and block until the user presses Enter.

#### Scenario: New playlists created
- **WHEN** one or more Album Playlists were created for an artist
- **THEN** the artist name is printed, the names of the new playlists are printed, an instruction to create or update the Artist Folder is displayed, and execution blocks until the user presses Enter

#### Scenario: Multiple new playlists created
- **WHEN** several Album Playlists were created for an artist
- **THEN** all of their names are listed in the prompt output, one per line

#### Scenario: Exactly one new playlist created
- **WHEN** exactly one Album Playlist was created for an artist
- **THEN** the prompt is shown with that single playlist name

### Requirement: Skip prompt when no new playlists were created
If no Album Playlists were created for an artist (all Albums already had playlists), the system SHALL produce no output and SHALL NOT block for user input.

#### Scenario: No new playlists
- **WHEN** zero Album Playlists were created for an artist
- **THEN** nothing is printed and execution continues immediately to the next artist
