# EP classification via track count and duration

The Spotify Web API does not expose "ep" as a distinct `album_type` — both singles and EPs are returned as `"single"`. To correctly include EPs while excluding actual singles, the script replicates Spotify's own internal classification rules for `album_type: "single"` releases: a release is treated as an EP if it has 4–6 tracks with ≤30 min total duration, or 1–3 tracks where at least one exceeds 10 min and the total exceeds 30 min.

Releases with `album_type: "album"` are trusted as-is — Spotify's own label is treated as authoritative and no classification rules are applied. This avoids fetching track durations for full albums, at the cost of not catching any edge case where Spotify mislabels an album.

Track count is derived from the tracks endpoint response (`len(durations)`) rather than the `total_tracks` field returned by the artist albums endpoint. The two can diverge — for example, regional editions may expose fewer tracks than the metadata advertises. Using the actual count keeps the track-count gate and the duration list consistent. As a consequence, `RawRelease` does not carry a `total_tracks` field; no production code reads it.

## Considered Options

- Include all `single`-type releases — gets EPs but clutters folders with actual singles
- Track count threshold alone (≥4 tracks) — heuristic, doesn't match Spotify's own logic
- Albums only — avoids the problem but drops EPs entirely
- Classify all releases uniformly from track data — consistent but fetches durations for full albums unnecessarily
- Use `total_tracks` from album metadata for the track-count gate — simpler but can diverge from the actual tracks response
