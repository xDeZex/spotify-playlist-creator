## ADDED Requirements

### Requirement: Apply differentiated proactive delay based on HTTP method
`api_request` SHALL sleep before sending each request: 0.2 s when no body is provided (GET) and 1.0 s when a body is provided (POST). The delay SHALL be applied on every call, including retried requests after a 429.

#### Scenario: GET request receives read delay
- **WHEN** `api_request` is called with no body and the request succeeds
- **THEN** a 0.2 s sleep occurs before the request is sent

#### Scenario: POST request receives write delay
- **WHEN** `api_request` is called with a non-None body and the request succeeds
- **THEN** a 1.0 s sleep occurs before the request is sent

#### Scenario: GET request does not receive write delay
- **WHEN** `api_request` is called with no body
- **THEN** the sleep duration is 0.2 s, not 1.0 s

#### Scenario: sleep called with correct duration
- **WHEN** `api_request` is called with no body
- **THEN** `time.sleep` is called with `0.2` before the HTTP call is made
- **WHEN** `api_request` is called with a non-None body
- **THEN** `time.sleep` is called with `1.0` before the HTTP call is made
