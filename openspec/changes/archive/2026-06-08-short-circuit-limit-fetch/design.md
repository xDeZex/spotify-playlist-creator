## Context

`fetch_saved_albums` in `saved_albums.py` currently fetches all pages of `GET /v1/me/albums` before returning. The `--limit` flag is applied afterwards in `run()` via `derive_artists(saved_albums)[:limit]`. For a 750-album library (15 pages), `--limit 4` still triggers 15 API calls.

Spotify returns albums newest-first. `derive_artists` orders artists by their oldest saved album's `added_at`, so the N artists we actually want are at the tail of Spotify's response. Fetching backward from the last page and stopping early is both correct and efficient.

See [ADR-0013](../../../docs/adr/0013-limit-fetch-uses-backward-pagination.md) for the correctness argument.

## Goals / Non-Goals

**Goals:**
- Reduce API calls from O(all pages) to O(pages needed) when `--limit` is set
- Preserve identical output for all call sites (no behaviour change when `limit=None`)
- Keep `fetch_saved_albums` as the single function; no new public API

**Non-Goals:**
- Smarter fetching for unlimited runs
- Caching or persistence of fetched pages
- Changes to `derive_artists`, `run()` beyond threading `limit` through

## Decisions

### Backward pagination over forward-and-stop

Forward-fetch-and-stop returns the wrong artists: stopping early on Spotify's newest-first stream yields the most recently saved artists, not the oldest. The `derive_artists` contract requires the oldest albums. Backward pagination is the only correct short-circuit strategy.

### Single function with `limit: int | None = None`

Adding an optional keyword-only parameter keeps the signature backward-compatible. No new helper, no factory, no strategy object. The branch `if limit is None` preserves the existing forward-fetch path exactly.

### Probe call at offset=0

One call to `offset=0` learns `total` cheaply. Without it, we'd have to guess the last-page offset (fragile) or start from a sentinel offset and rely on the API returning `total` even for out-of-range offsets (undocumented behaviour). The probe cost is one extra read call per `--limit` run — acceptable.

### Probe items held, not refetched

The probe's items (newest albums) are stored in memory. If the backward sweep exhausts all pages without collecting N distinct artists, probe items are appended to the result. This avoids refetching `offset=0` and prevents a broken status counter (which would show `(total_pages+1)/total_pages`).

### Stopping condition on backward items only

Only albums collected during the backward sweep count toward the stopping condition. If probe items were included, the function might stop before fetching any backward page — returning only the newest artists, which is wrong.

## Risks / Trade-offs

**Probe items appended silently** → No status write for probe items when used as fallback. The display shows `(1/N)` ... `(N/N)` correctly; the probe-as-fallback is invisible. Acceptable: the user sees accurate call counts for all calls made.

**One extra call vs no `--limit`** → The probe call doesn't exist in the unlimited path, so there's zero regression there. For the limited path, the probe is one of the ~2 total calls — well within budget.

**Edge case: `total=0`** → Probe returns empty items, `total=0`. Function returns `[]` immediately. No backward sweep.

**Edge case: `total <= 50`** → Only one page exists. Probe items are the complete result; returned directly without a backward sweep.
