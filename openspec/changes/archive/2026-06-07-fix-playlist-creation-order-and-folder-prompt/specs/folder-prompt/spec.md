## MODIFIED Requirements

### Requirement: Prompt user to create Artist Folder before playlist creation
Before Album Playlists are created for an upcoming artist, the system SHALL display a blocking prompt and wait for the user to press Enter. If the upcoming artist is the first artist in the sync with new playlists (no previous batch exists), the prompt SHALL instruct the user to create the Artist Folder for that artist only. If a previous artist's newly created playlists exist, the prompt SHALL first list those playlists newest-release-date first, instruct the user to drag them into the previous Artist Folder, then instruct the user to create the upcoming Artist Folder, and then block.

#### Scenario: First artist — no previous batch
- **WHEN** no playlists have been created yet in this sync and the first artist with new albums is about to be processed
- **THEN** a prompt is displayed instructing the user to create the Artist Folder for that artist, and execution blocks until the user presses Enter

#### Scenario: Subsequent artist — previous batch present
- **WHEN** playlists were created for a previous artist and a new artist with new albums is about to be processed
- **THEN** the previous artist's new playlists are listed newest-first, the user is instructed to drag them into the previous Artist Folder, the user is instructed to create the upcoming Artist Folder, and execution blocks until the user presses Enter

#### Scenario: (no external I/O contract)

### Requirement: Print final non-blocking message after last artist's playlists are created
After Album Playlists are created for the last artist in the sync that had new playlists, the system SHALL print those playlists newest-release-date first and instruct the user to drag them into the Artist Folder. The system SHALL NOT block for user input.

#### Scenario: Final artist playlists created
- **WHEN** the sync loop has finished creating playlists for the last artist with new albums
- **THEN** those playlists are printed newest-first with an instruction to drag them into the folder, and execution continues (does not block)

#### Scenario: Only one artist had new playlists
- **WHEN** only one artist in the sync had new albums, making it both first and last
- **THEN** the pre-creation prompt (first-artist form) blocks before creation, and the non-blocking final message is printed after creation

#### Scenario: (no external I/O contract)

## REMOVED Requirements

### Requirement: Prompt user to place new playlists into Artist Folder
**Reason**: Replaced by pre-creation prompt — the folder must exist before playlists are created so the user can position it correctly for drag-and-drop (see ADR-0012).
**Migration**: The post-creation blocking prompt is replaced by a pre-creation blocking prompt (`Requirement: Prompt user to create Artist Folder before playlist creation`) and a post-creation non-blocking message (`Requirement: Print final non-blocking message after last artist's playlists are created`).
