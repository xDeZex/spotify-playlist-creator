## 1. CLI argument parsing

- [x] 1.1 `--limit 5` is accepted and `run()` is called with `limit=5`
- [x] 1.2 Omitting `--limit` calls `run()` with `limit=None`
- [x] 1.3 `--limit 0` exits with a non-zero status before any API calls
- [x] 1.4 `--limit -1` exits with a non-zero status before any API calls

## 2. Artist Limit applied in sync loop

- [x] 2.1 `run()` accepts `limit: int | None = None`
- [x] 2.2 With `limit=2` and 5 artists, only the 2 least-recently-saved artists are processed
- [x] 2.3 With `limit=None`, all artists are processed (no regression)
- [x] 2.4 With `limit` greater than the number of artists, all artists are processed
