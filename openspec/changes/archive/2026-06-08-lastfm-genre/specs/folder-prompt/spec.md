## MODIFIED Requirements

### Requirement: Prompt user to create Artist Folder before playlist creation
Before Album Playlists are created for an upcoming artist, the system SHALL display a blocking prompt and wait for the user to press Enter. `prompt_for_folder` SHALL accept a `genre: str | None` parameter. The "Create the Artist Folder" instruction SHALL include the genre as `[{genre}]` appended after the artist name; if `genre` is `None` it SHALL display `[genre not found]`. If the upcoming artist is the first artist in the sync with new playlists (no previous batch exists), the prompt SHALL instruct the user to create the Artist Folder for that artist only. If a previous artist's newly created playlists exist, the prompt SHALL first list those playlists newest-release-date first, instruct the user to drag them into the previous Artist Folder, then instruct the user to create the upcoming Artist Folder, and then block.

#### Scenario: First artist — genre known
- **WHEN** no playlists have been created yet and the first artist with new albums is about to be processed, and genre is `"j-pop"`
- **THEN** the prompt instructs the user to create the Artist Folder including `[j-pop]` and blocks until Enter is pressed

#### Scenario: Genre not found
- **WHEN** `genre` is `None`
- **THEN** the prompt displays `[genre not found]` after the artist name

#### Scenario: (no external I/O contract)

### Requirement: Print final non-blocking message after last artist's playlists are created
After Album Playlists are created for the last artist in the sync that had new playlists, the system SHALL print those playlists newest-release-date first and instruct the user to drag them into the Artist Folder. `print_final_folder_message` SHALL accept a `genre: str | None` parameter and include the genre tag on the artist name line using the same `[{genre}]` / `[genre not found]` format. The system SHALL NOT block for user input.

#### Scenario: Final message includes genre
- **WHEN** the sync loop has finished and the last artist had genre `"j-pop"`
- **THEN** the final message includes `[j-pop]` on the artist name line and does not block

#### Scenario: Final message with no genre
- **WHEN** `genre` is `None`
- **THEN** the final message displays `[genre not found]` on the artist name line

#### Scenario: (no external I/O contract)
