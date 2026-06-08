# Hard fail on missing LASTFM_API_KEY

If `LASTFM_API_KEY` is not set at startup, the script raises immediately rather than degrading gracefully to genre-less output. This is a single-user script where the key is always expected to be present; a missing key means misconfiguration, not an optional feature being skipped. Silent degradation would mask setup errors.
