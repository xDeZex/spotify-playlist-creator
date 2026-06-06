## MODIFIED Requirements

### Requirement: Retry on 429 when Retry-After header is present
When the API returns 429 and the response includes a `Retry-After` header, `api_request` SHALL call `status.write(f"rate limited, waiting {retry_after}s...")` before sleeping, then wait the specified number of seconds and retry the request. This SHALL repeat up to 3 total attempts. If all 3 attempts return 429, the final 429 SHALL be raised as a `RuntimeError` using the structured error message format.

#### Scenario: Single 429 then success — status message emitted
- **WHEN** the first attempt returns 429 with `Retry-After: 2` and the second attempt succeeds
- **THEN** `status.write("rate limited, waiting 2s...")` is called, then the function waits 2 seconds, retries, and returns the successful response body

#### Scenario: Three consecutive 429 responses
- **WHEN** all 3 attempts return 429 with a `Retry-After` header
- **THEN** a `RuntimeError` is raised after the third attempt

#### Scenario: Retry-After value respected
- **WHEN** a 429 response includes `Retry-After: 5`
- **THEN** the function waits 5 seconds before retrying
