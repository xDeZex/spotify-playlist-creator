## 1. status.py module

- [x] 1.1 `status.write(msg)` emits `\r\033[2K{msg}` to stdout with no newline and flushes
- [x] 1.2 `status.set_context(ctx)` causes subsequent `write()` calls to prepend `{ctx} — `
- [x] 1.3 Empty context produces no prefix separator
- [x] 1.4 `status.clear()` emits `\r\033[2K`, flushes, and resets context to `""`
- [x] 1.5 `status.set(fn)` replaces the callable; subsequent `write()` calls invoke `fn` with the assembled line
- [x] 1.6 Default callable is a no-op lambda; `write()` before `set()` raises no exception

## 2. api_request: rate-limit status message

- [x] 2.1 On 429 retry, `status.write(f"rate limited, waiting {retry_after}s...")` is called before sleeping

## 3. fetch_album_tracks bug fix

- [x] 3.1 `fetch_album_tracks` in `classify_releases.py` uses `api_request` instead of raw `urlopen`

## 4. Pagination status in pre-loop fetches

- [x] 4.1 `fetch_saved_albums` writes `"fetching saved albums ({page}/{total_pages})..."` for each page
- [x] 4.2 `fetch_owned_playlists` writes `"fetching owned playlists ({page}/{total_pages})..."` for each page

## 5. Per-artist status in the artist loop

- [x] 5.1 `fetch_artist_releases` writes `"fetching releases ({page}/{total_pages})..."` for each page
- [x] 5.2 `classify_releases` writes `"classifying singles ({i}/{total})..."` before each single track fetch
- [x] 5.3 `find_missing_album_playlists` writes `"checking existing playlists..."` (no count — not paginated)
- [x] 5.4 `create_album_playlists` writes `"creating playlists ({i}/{total})..."` before creating each playlist

## 6. run() orchestration

- [x] 6.1 `run()` calls `status.set(...)` with a stdout-writing function before any sub-function is called
- [x] 6.2 `run()` calls `status.set_context(f"[{i}/{n}] {artist.name}")` before each artist, where `n` is post-limit count
- [x] 6.3 `run()` calls `status.clear()` after all artists are processed
- [x] 6.4 Status and context are active in Dry Sync mode (same behaviour as live mode)
