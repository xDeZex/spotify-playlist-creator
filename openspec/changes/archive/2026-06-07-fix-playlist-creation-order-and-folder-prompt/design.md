## Context

Three modules need to change: `create_playlists.py` (sort order), `folder_prompt.py` (prompt content and blocking), and `__init__.py` (call order and loop state). The changes are tightly coordinated — the sync loop must track per-iteration state to drive the prompt correctly.

## Goals / Non-Goals

**Goals:**
- Albums created oldest-first so newest lands at top of Spotify's "recently added"
- Pre-creation folder prompt blocks before playlist creation, not after
- Prompt references the previous artist's batch so the user knows what to drag before continuing
- Final non-blocking message after the last artist's batch

**Non-Goals:**
- Automatic folder placement (still manual drag-and-drop)
- Any change to Dry Sync behaviour

## Decisions

### Sort order flip
Change `reverse=True` to `reverse=False` in `find_missing_album_playlists`. One line. The execute step already creates in the order provided, so no further change needed there.

### sync loop carries previous-artist state
The loop in `run()` tracks `previous_artist: str | None` and `previous_created: list[CreatedPlaylist]` across iterations. After each artist's playlists are created, these are updated. After the loop, if any artist had new playlists, the final non-blocking message is printed.

```
previous_artist = None
previous_created = []

for artist in artists:
    new_albums = find_missing(...)
    if not new_albums:
        continue
    prompt_for_folder(artist.name, previous_artist, previous_created)
    created = create_album_playlists(...)
    previous_artist = artist.name
    previous_created = created

if previous_artist:
    print_final_folder_message(previous_artist, previous_created)
```

### prompt_for_folder signature changes
The existing signature `(artist_name, created_playlists)` is replaced by `(upcoming_artist, previous_artist, previous_playlists)`. When `previous_artist` is None (first artist), only the upcoming folder instruction is shown. When it is set, the previous batch is listed newest-first before the folder instruction.

### New print_final_folder_message function
A separate non-blocking function in `folder_prompt.py` prints the final batch (newest-first) with a drag instruction and returns immediately. This keeps the blocking/non-blocking distinction explicit rather than encoding it as a mode flag on `prompt_for_folder`.

### Playlist display order in prompts
Both prompt functions list playlists newest-release-date first (reverse of creation order) to match what the user sees in Spotify's "recently added" view.

## Risks / Trade-offs

- **Tests break at the interface boundary** — all tests patching `prompt_for_folder` or asserting on its call site need updating. Expected: moderate churn across `test_folder_prompt.py` and `test___init__.py`.
- **Single-artist sync** — the first-artist pre-creation prompt fires, then creation runs, then the final non-blocking message fires. No blocking after creation. Verified by spec scenario "Only one artist had new playlists."
