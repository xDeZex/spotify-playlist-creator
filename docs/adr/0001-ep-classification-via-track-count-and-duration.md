# EP classification via track count and duration

The Spotify Web API does not expose "ep" as a distinct `album_type` — both singles and EPs are returned as `"single"`. To correctly include EPs while excluding actual singles, the script replicates Spotify's own internal classification rules: a release is treated as an EP if it has 4–6 tracks with ≤30 min total duration, or 1–3 tracks where at least one exceeds 10 min and the total exceeds 30 min. This matches what Spotify labels as "EP" in its UI, at the cost of one extra API call to fetch track durations.

## Considered Options

- Include all `single`-type releases — gets EPs but clutters folders with actual singles
- Track count threshold alone (≥4 tracks) — heuristic, doesn't match Spotify's own logic
- Albums only — avoids the problem but drops EPs entirely
