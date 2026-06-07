## 1. Sort order: albums created oldest-first

- [x] 1.1 `find_missing_album_playlists` returns albums in ascending release-date order (oldest first)
- [x] 1.2 Existing tests for descending sort order are updated to expect ascending order

## 2. Pre-creation folder prompt

- [x] 2.1 `prompt_for_folder` accepts `(upcoming_artist, previous_artist, previous_playlists)` and blocks on `input()`
- [x] 2.2 When `previous_artist` is None, prompt shows only the upcoming Artist Folder instruction
- [x] 2.3 When `previous_artist` is set, prompt lists previous playlists newest-first, instructs drag into previous folder, then instructs creation of upcoming folder
- [x] 2.4 Existing `prompt_for_folder` tests are updated or replaced to cover the new signature and both display modes

## 3. Final non-blocking message

- [x] 3.1 `print_final_folder_message(artist_name, playlists)` prints playlists newest-first with a drag instruction and does not block
- [x] 3.2 `print_final_folder_message` is tested: output lists playlists newest-first, no `input()` call

## 4. Sync loop orchestration

- [x] 4.1 `run()` calls `prompt_for_folder` before `create_album_playlists` for each artist with new albums
- [x] 4.2 `run()` tracks previous artist state across iterations and passes it to `prompt_for_folder`
- [x] 4.3 After the loop, `run()` calls `print_final_folder_message` for the last artist that had new playlists
- [x] 4.4 Artists with no new albums produce no prompt output and no final message
- [x] 4.5 Sync loop tests updated to assert prompt fires before creation and final message fires after last artist
