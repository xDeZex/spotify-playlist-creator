### Requirement: Send authenticated request and return parsed body
The system SHALL provide an `api_request(url, token, *, body=None)` function in `spotify_playlist_creator/api.py` that attaches a `Bearer` token to an HTTP request, executes it, and returns the parsed JSON response body as a dict. When `body` is provided, the request SHALL use POST with `Content-Type: application/json`; otherwise GET.

#### Scenario: Successful GET request
- **WHEN** `api_request` is called with a URL and a valid token and no body
- **THEN** it returns the parsed JSON response body as a dict

#### Scenario: Successful POST request
- **WHEN** `api_request` is called with a URL, a valid token, and a non-None body
- **THEN** it sends a POST request with the body serialised as JSON and returns the parsed response

#### Scenario: Authorization header forwarded
- **WHEN** `api_request` is called with a token whose access_token is `"tok"`
- **THEN** the outgoing request includes the header `Authorization: Bearer tok`

### Requirement: Raise structured RuntimeError on HTTP errors
When the Spotify API returns an HTTP error (4xx or 5xx), `api_request` SHALL raise `RuntimeError` with the message `Spotify API error (STATUS /path): <message>`, where `STATUS` is the HTTP status code, `/path` is the path portion of the URL, and `<message>` is the `message` field from Spotify's `{"error": {"status": N, "message": "..."}}` response body. If the body cannot be parsed as that shape, the raw response text SHALL be used in place of `<message>`.

#### Scenario: Structured Spotify error body
- **WHEN** the API returns a 403 with body `{"error": {"status": 403, "message": "Insufficient client scope"}}`
- **THEN** `RuntimeError("Spotify API error (403 /v1/me/albums): Insufficient client scope")` is raised

#### Scenario: Non-JSON or unexpected error body
- **WHEN** the API returns a 503 with a plain-text body `"Service Unavailable"`
- **THEN** `RuntimeError("Spotify API error (503 /v1/me/albums): Service Unavailable")` is raised

#### Scenario: Network failure
- **WHEN** the HTTP call fails with a `URLError` (e.g. no network)
- **THEN** a `RuntimeError` describing the network failure is raised

### Requirement: Retry on 429 when Retry-After header is present
When the API returns 429 and the response includes a `Retry-After` header, `api_request` SHALL wait the specified number of seconds and retry the request. This SHALL repeat up to 3 total attempts. If all 3 attempts return 429, the final 429 SHALL be raised as a `RuntimeError` using the structured error message format.

#### Scenario: Single 429 then success
- **WHEN** the first attempt returns 429 with `Retry-After: 1` and the second attempt succeeds
- **THEN** the function waits 1 second, retries, and returns the successful response body

#### Scenario: Three consecutive 429 responses
- **WHEN** all 3 attempts return 429 with a `Retry-After` header
- **THEN** a `RuntimeError` is raised after the third attempt

#### Scenario: Retry-After value respected
- **WHEN** a 429 response includes `Retry-After: 5`
- **THEN** the function waits 5 seconds before retrying

### Requirement: Fail immediately on 429 without Retry-After header
When the API returns 429 and the response does NOT include a `Retry-After` header, `api_request` SHALL raise `RuntimeError` immediately without retrying.

#### Scenario: 429 with no Retry-After
- **WHEN** the API returns 429 and no `Retry-After` header is present
- **THEN** a `RuntimeError` is raised immediately with no retry attempted
