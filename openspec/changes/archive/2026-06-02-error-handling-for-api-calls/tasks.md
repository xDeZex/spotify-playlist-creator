## 1. api_request helper

- [x] 1.1 GET request succeeds and returns parsed JSON body
- [x] 1.2 POST request with body sends JSON and returns parsed response
- [x] 1.3 Authorization header is forwarded correctly
- [x] 1.4 HTTP error with structured Spotify body raises RuntimeError with status, path, and message
- [x] 1.5 HTTP error with non-JSON body raises RuntimeError with raw body text
- [x] 1.6 URLError raises RuntimeError describing the network failure
- [x] 1.7 429 with Retry-After retries and succeeds on second attempt
- [x] 1.8 429 with Retry-After three times in a row raises RuntimeError after third attempt
- [x] 1.9 429 without Retry-After raises RuntimeError immediately with no retry

## 2. saved_albums uses api_request

- [x] 2.1 fetch_saved_albums uses api_request for all HTTP calls
- [x] 2.2 API error during saved albums fetch propagates as RuntimeError

## 3. artist_releases uses api_request

- [x] 3.1 fetch_artist_releases uses api_request for all HTTP calls
- [x] 3.2 API error during artist releases fetch propagates as RuntimeError

## 4. create_playlists uses api_request

- [x] 4.1 fetch_user_playlists uses api_request for all HTTP calls
- [x] 4.2 fetch_first_track_album_id uses api_request
- [x] 4.3 fetch_album_track_uris uses api_request for all HTTP calls
- [x] 4.4 add_tracks_to_playlist uses api_request for all batch requests
- [x] 4.5 create_album_playlists uses api_request for playlist creation
- [x] 4.6 API error during any create_playlists operation propagates as RuntimeError
