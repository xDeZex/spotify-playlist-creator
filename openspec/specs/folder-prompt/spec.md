## Requirements

### Requirement: Prompt user to create Artist Folder before playlist creation
`prompt_for_folder` SHALL accept a `genre: list[str] | None` parameter in addition to the artist name and playlist batch arguments. Before Album Playlists are created for an upcoming artist, the system SHALL display a blocking prompt and wait for the user to press Enter. If `genre` is a non-empty list, the artist name SHALL be displayed with `[tag1, tag2, ...]` appended; if `genre` is an empty list (no tags found), it SHALL display `[genre not found]`; if `genre` is `None` (fetch failed), it SHALL display `[failed to get genre]`. If the upcoming artist is the first artist in the sync with new playlists (no previous batch exists), the prompt SHALL instruct the user to create the Artist Folder for that artist only. If a previous artist's newly created playlists exist, the prompt SHALL first list those playlists newest-release-date first, instruct the user to drag them into the previous Artist Folder, then instruct the user to create the upcoming Artist Folder, and then block.

#### Scenario: First artist — no previous batch
- **WHEN** no playlists have been created yet in this sync and the first artist with new albums is about to be processed
- **THEN** a prompt is displayed instructing the user to create the Artist Folder for that artist, and execution blocks until the user presses Enter

#### Scenario: Subsequent artist — previous batch present
- **WHEN** playlists were created for a previous artist and a new artist with new albums is about to be processed
- **THEN** the previous artist's new playlists are listed newest-first, the user is instructed to drag them into the previous Artist Folder, the user is instructed to create the upcoming Artist Folder, and execution blocks until the user presses Enter

#### Scenario: Previous artist state empty playlists suppressed
- **WHEN** a previous artist is tracked but their created playlists list is empty
- **THEN** no previous-batch section is shown in the prompt

### Requirement: Print final non-blocking message after last artist's playlists are created
`print_final_folder_message` SHALL accept a `genre: list[str] | None` parameter in addition to the artist name and playlist batch arguments. After Album Playlists are created for the last artist in the sync that had new playlists, the system SHALL print those playlists newest-release-date first and instruct the user to drag them into the Artist Folder. The genre tag follows the same display rules as `prompt_for_folder`: non-empty list → `[tag1, tag2, ...]`, empty list → `[genre not found]`, `None` → `[failed to get genre]`. The system SHALL NOT block for user input.

#### Scenario: Final artist playlists created
- **WHEN** the sync loop has finished creating playlists for the last artist with new albums
- **THEN** those playlists are printed newest-first with an instruction to drag them into the folder, and execution continues (does not block)

#### Scenario: Only one artist had new playlists
- **WHEN** only one artist in the sync had new albums, making it both first and last
- **THEN** the pre-creation prompt (first-artist form) blocks before creation, and the non-blocking final message is printed after creation
