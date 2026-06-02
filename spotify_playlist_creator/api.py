from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from spotify_playlist_creator.auth import SpotifyToken

_MAX_RETRIES = 3


def api_request(
    url: str, token: SpotifyToken, *, body: dict[str, Any] | None = None
) -> dict[str, Any]:
    path = urllib.parse.urlparse(url).path
    headers: dict[str, str] = {"Authorization": f"Bearer {token.access_token}"}
    data: bytes | None = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"

    for attempt in range(_MAX_RETRIES):
        req = urllib.request.Request(url, data=data, headers=headers)
        try:
            with urllib.request.urlopen(req) as response:
                result: dict[str, Any] = json.loads(response.read())
                return result
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and attempt < _MAX_RETRIES - 1:
                retry_after = exc.headers.get("Retry-After")
                if retry_after is not None:
                    time.sleep(float(retry_after))
                    continue
            raw = exc.read().decode(errors="replace")
            raise RuntimeError(
                f"Spotify API error ({exc.code} {path}): {_parse_error_message(raw)}"
            ) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Network error: {exc.reason}") from exc

    raise AssertionError("unreachable")  # mypy: range(_MAX_RETRIES) is never empty


def _parse_error_message(raw: str) -> str:
    try:
        body = json.loads(raw)
        return str(body["error"]["message"])
    except (json.JSONDecodeError, KeyError, TypeError):
        return raw
