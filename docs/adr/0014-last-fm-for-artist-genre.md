# Last.fm as the source for artist genre

Spotify's `artists.genres` field is deprecated and increasingly returns empty data, making it unreliable as a genre source. We use Last.fm's `artist.gettoptags` endpoint instead, taking the top tag by score as the Genre for each Artist. This requires a `LASTFM_API_KEY` environment variable (free, read-only, no OAuth).
