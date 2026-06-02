# 429 retry requires Retry-After header

When `api_request` receives a 429 response, it retries up to 3 times — but only if Spotify includes a `Retry-After` header. If the header is absent, the request fails immediately with a `RuntimeError`. A default backoff was considered and rejected: guessing a wait time masks whether the rate limit is real or a transient anomaly, and Spotify virtually always sends the header in practice.
