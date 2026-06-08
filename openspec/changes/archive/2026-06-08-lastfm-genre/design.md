## Context

The script currently has no genre information for artists — Spotify's `genres` field is deprecated and unreliable. Genre is needed as a display hint during the folder prompt so the user knows which genre folder to place the Artist Folder into. Last.fm's `artist.gettoptags` endpoint provides reliable, crowd-sourced genre tags via a free, read-only API key.

## Goals / Non-Goals

**Goals:**
- Fetch top genre tag per artist from Last.fm during the sync loop
- Display genre in folder prompts and dry sync output
- Fail fast at startup if `LASTFM_API_KEY` is not set

**Non-Goals:**
- Caching genre results across runs
- Using genre to organise artists automatically (folder creation is always manual)
- Normalising or fuzzy-matching artist names between Spotify and Last.fm

## Decisions

### New `lastfm.py` module, not extending `api.py`
`api.py` is coupled to `SpotifyToken` (Bearer auth). Last.fm uses a plain API key in query parameters — no token. Adding Last.fm calls to `api.py` would require leaking non-Spotify auth concepts into a Spotify-specific module. A separate `lastfm.py` keeps auth concerns isolated.

### Plain `str | None` threading — no model changes
Genre is only needed at the display layer (folder prompt, dry sync). Adding `genre` to the `Artist` dataclass would mix Last.fm data into a Spotify-derived model. Passing `genre: str | None` as a plain argument to `prompt_for_folder`, `print_final_folder_message`, and `report_dry_sync_artist` keeps the models clean.

### Catch HTTP errors in `run()`, not in `lastfm.py`
`fetch_artist_genre` raises on HTTP/network error so callers know something went wrong. `run()` catches and substitutes `"failed to get genre"` — this keeps the fallback display logic in one place (the orchestration layer) and keeps `lastfm.py` focused on HTTP semantics only.

### No explicit rate-limit delay in `lastfm.py`
Last.fm's limit is 2 req/s. Genre is fetched once per artist, with several Spotify API calls in between. The natural inter-artist gap far exceeds 0.5s, so no proactive sleep is needed.

## Risks / Trade-offs

- **Artist name mismatch** (Spotify vs Last.fm): Passed as-is. Niche or non-Latin-script artists may return `None`. Accepted — `[genre not found]` is a graceful fallback.
- **Last.fm availability**: If Last.fm is down, `run()` catches and uses `"failed to get genre"`. The sync continues normally; only the genre hint is missing.
- **Hard fail on missing key**: A user without `LASTFM_API_KEY` cannot run the script at all. Accepted — single-user script, key is always expected.
