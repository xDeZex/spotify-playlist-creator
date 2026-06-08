# Limit fetch uses backward pagination

When `--limit` is set, `fetch_saved_albums` paginates backwards — starting from the last page (oldest albums) and working toward page 1 — stopping once N distinct primary artists have been seen.

The naive alternative (fetch forward and stop at N distinct artists) is incorrect: Spotify returns albums newest-first, so stopping early on a forward sweep yields the *newest* artists, not the oldest. `derive_artists` orders artists by their earliest saved album, so the correct N artists are found at the tail of Spotify's response, not the head.

## Considered options

**Forward fetch, stop early** — simpler to implement, but produces the wrong artists: the N most-recently-saved, not the N oldest.

**Fetch all, slice afterwards** — correct, but defeats the purpose of `--limit` as a performance optimisation (15 API calls for a 4-artist test run).

**Backward fetch, stop early** — correct and efficient. Requires one probe call to page 1 to learn `total`, then pages from the last offset toward offset=50. Probe items are held in memory and appended only if the backward sweep exhausts all pages without reaching N distinct artists.
