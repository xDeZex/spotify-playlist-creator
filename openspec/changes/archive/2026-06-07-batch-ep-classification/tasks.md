## 1. fetch_singles_durations — happy path

- [x] 1.1 `fetch_singles_durations` returns a dict mapping each album ID to its list of `duration_ms` integers extracted from `tracks.items`
- [x] 1.2 `fetch_singles_durations` makes exactly one request when called with up to 20 IDs, with IDs joined as a comma-separated `?ids=` query parameter
- [x] 1.3 Every request includes `Authorization: Bearer <token>`

## 2. fetch_singles_durations — null and edge cases

- [x] 2.1 Albums returned as `null` in the response are absent from the returned dict and no error is raised
- [x] 2.2 An album with zero tracks in `tracks.items` is mapped to an empty list

## 3. classify_releases — batch fetch integration

- [x] 3.1 `classify_releases` pre-fetches durations for all singles before the classification loop, calling `fetch_singles_durations` in batches of at most 20 IDs
- [x] 3.2 `classify_releases` uses the pre-fetched dict (via `.get(id, [])`) instead of a per-single API call during classification
- [x] 3.3 EP classification results are unchanged: full albums pass, qualifying singles are included, non-qualifying singles are excluded, compilations are dropped

## 4. classify_releases — per-batch status reporting

- [x] 4.1 `classify_releases` calls `status.write("classifying singles (N/total)...")` once per batch, where N is the cumulative count of singles fetched so far
- [x] 4.2 No `status.write` call is made when the input contains no singles

## 5. Cleanup

- [x] 5.1 `fetch_album_tracks` is removed from `classify_releases.py`
- [x] 5.2 All tests directly testing `fetch_album_tracks` are removed from `test_classify_releases.py`
