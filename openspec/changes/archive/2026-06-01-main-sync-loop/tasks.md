## 1. Wire run() — production code

- [x] 1.1 `run()` fetches saved albums, derives artists, fetches existing playlists once, then for each artist fetches releases, classifies, creates playlists, and calls `prompt_for_folder` when new playlists were created

## 2. Test run() — function-boundary tests

- [x] 2.1 Happy path: two artists both with new albums — `prompt_for_folder` called for both
- [x] 2.2 All albums already exist — `prompt_for_folder` never called
- [x] 2.3 Mixed: one artist with new albums, one without — `prompt_for_folder` called exactly once
- [x] 2.4 No saved albums — artist loop never runs
- [x] 2.5 Artist with only singles — `classify_releases` returns `[]`, `prompt_for_folder` not called
- [x] 2.6 `fetch_user_playlists` is called exactly once regardless of how many artists are processed
