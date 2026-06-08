## 1. fetch_saved_albums accepts limit parameter

- [x] 1.1 `fetch_saved_albums(token)` called without `limit` returns the same result as before
- [x] 1.2 `fetch_saved_albums(token, limit=N)` is accepted without error
- [x] 1.3 Existing call sites that omit `limit` continue to work without modification

## 2. Probe call when limit is set

- [x] 2.1 When `limit` is set, the first API call is always to `offset=0` (the probe)
- [x] 2.2 When `total <= 50`, the probe items are returned directly and no further requests are made
- [x] 2.3 When `total == 0`, an empty list is returned immediately

## 3. Backward pagination stops early

- [x] 3.1 When `limit=N` and the last page contains ≥ N distinct primary artists, no pages before it are fetched
- [x] 3.2 When the last page alone is insufficient, additional pages are fetched in decreasing offset order until N distinct primary artists are collected
- [x] 3.3 When the backward sweep exhausts all pages (offset=50 reached) without N distinct artists, probe items are appended and the full result is returned

## 4. Stopping condition excludes probe items

- [x] 4.1 Distinct primary artists from probe items do not count toward the stopping condition
- [x] 4.2 The function does not stop the backward sweep early based solely on artists seen in the probe page

## 5. Status messages reflect actual calls made

- [x] 5.1 When `limit` is set, status emits `fetching saved albums (1/total_pages)...` for the probe call
- [x] 5.2 Each subsequent backward page emits `fetching saved albums (N/total_pages)...` with N incrementing
- [x] 5.3 When `total <= 50`, exactly one status message `(1/1)` is emitted

## 6. run() threads limit through to fetch_saved_albums

- [x] 6.1 `run(limit=N)` calls `fetch_saved_albums(token, limit=N)`
- [x] 6.2 `run(limit=None)` calls `fetch_saved_albums(token, limit=None)` (or equivalent)
- [x] 6.3 `derive_artists(saved_albums)[:limit]` in `run()` still produces the correct N oldest artists
