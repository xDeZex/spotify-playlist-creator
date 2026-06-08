## 1. lastfm.py — API key and genre fetch

- [x] 1.1 `get_api_key()` returns `LASTFM_API_KEY` when set
- [x] 1.2 `get_api_key()` raises `RuntimeError` when `LASTFM_API_KEY` is not set
- [x] 1.3 `fetch_artist_genre` returns the top tag by count when Last.fm returns tags
- [x] 1.4 `fetch_artist_genre` returns `None` when Last.fm returns no tags
- [x] 1.5 `fetch_artist_genre` returns `None` when Last.fm returns artist-not-found (error code 6)
- [x] 1.6 `fetch_artist_genre` raises `RuntimeError` on HTTP error
- [x] 1.7 `fetch_artist_genre` sends correct query parameters to Last.fm endpoint

## 2. folder_prompt.py — genre in prompt and final message

- [x] 2.1 `prompt_for_folder` displays `[j-pop]` when `genre="j-pop"`
- [x] 2.2 `prompt_for_folder` displays `[genre not found]` when `genre=None`
- [x] 2.3 `print_final_folder_message` displays `[j-pop]` when `genre="j-pop"`
- [x] 2.4 `print_final_folder_message` displays `[genre not found]` when `genre=None`

## 3. dry_sync.py — genre in dry sync output

- [x] 3.1 `report_dry_sync_artist` includes `[j-pop]` on the artist name line when genre is known
- [x] 3.2 `report_dry_sync_artist` includes `[genre not found]` on the artist name line when `genre=None`

## 4. sync-loop — genre wired into run()

- [x] 4.1 `run()` calls `get_api_key()` before `fetch_saved_albums`
- [x] 4.2 `run()` propagates `RuntimeError` from `get_api_key()` immediately
- [x] 4.3 `run()` passes genre to `prompt_for_folder` for each artist in normal mode
- [x] 4.4 `run()` passes genre to `print_final_folder_message` for the last artist
- [x] 4.5 `run()` passes genre to `report_dry_sync_artist` in dry sync mode
- [x] 4.6 `run()` catches `RuntimeError` from `fetch_artist_genre` and uses `"failed to get genre"`
