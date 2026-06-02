from __future__ import annotations

import io
import json
import urllib.error
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from spotify_playlist_creator.api import api_request
from spotify_playlist_creator.auth import SpotifyToken

_TOKEN = SpotifyToken(
    access_token="tok",
    token_type="Bearer",
    refresh_token="rtok",
    expires_at=9_999_999_999.0,
)


def _ok_response(body: dict[str, Any]) -> Any:
    class _Response:
        def read(self) -> bytes:
            return json.dumps(body).encode()

        def __enter__(self) -> _Response:
            return self

        def __exit__(self, *args: Any) -> None:
            pass

    return _Response()


def _http_error(
    code: int, body: str, retry_after: str | None = None
) -> urllib.error.HTTPError:
    hdrs: MagicMock = MagicMock()
    hdrs.get = lambda key, default=None: (
        retry_after if key == "Retry-After" else default
    )
    return urllib.error.HTTPError(
        url="https://api.spotify.com/v1/me/albums",
        code=code,
        msg="Error",
        hdrs=hdrs,
        fp=io.BytesIO(body.encode()),
    )


# ---------------------------------------------------------------------------
# Task 1.1: GET request succeeds and returns parsed JSON body
# ---------------------------------------------------------------------------


def test_api_request_get_returns_parsed_body() -> None:
    expected = {"items": [{"id": "1"}], "next": None}
    with patch("urllib.request.urlopen", return_value=_ok_response(expected)):
        result = api_request("https://api.spotify.com/v1/me/albums", _TOKEN)
    assert result == expected


# ---------------------------------------------------------------------------
# Task 1.2: POST request with body sends JSON and returns parsed response
# ---------------------------------------------------------------------------


def test_api_request_post_sends_json_body() -> None:
    captured: list[Any] = []
    expected = {"id": "pl1"}

    def capturing_urlopen(req: Any) -> Any:
        captured.append(req)
        return _ok_response(expected)

    post_body = {"name": "My Playlist", "public": True}
    with patch("urllib.request.urlopen", side_effect=capturing_urlopen):
        result = api_request(
            "https://api.spotify.com/v1/me/playlists", _TOKEN, body=post_body
        )

    assert result == expected
    assert captured[0].data == json.dumps(post_body).encode()
    assert captured[0].get_header("Content-type") == "application/json"


# ---------------------------------------------------------------------------
# Task 1.3: Authorization header is forwarded correctly
# ---------------------------------------------------------------------------


def test_api_request_forwards_authorization_header() -> None:
    captured: list[Any] = []

    def capturing_urlopen(req: Any) -> Any:
        captured.append(req)
        return _ok_response({})

    with patch("urllib.request.urlopen", side_effect=capturing_urlopen):
        result = api_request("https://api.spotify.com/v1/me/albums", _TOKEN)

    assert captured[0].get_header("Authorization") == "Bearer tok"
    assert captured[0].data is None
    assert result == {}


# ---------------------------------------------------------------------------
# Task 1.4: HTTP error with structured Spotify body raises RuntimeError
# ---------------------------------------------------------------------------


def test_api_request_structured_error_raises_runtime_error() -> None:
    error_body = json.dumps(
        {"error": {"status": 403, "message": "Insufficient client scope"}}
    )
    with patch(
        "urllib.request.urlopen",
        side_effect=_http_error(403, error_body),
    ):
        with pytest.raises(
            RuntimeError,
            match=r"Spotify API error \(403 /v1/me/albums\): Insufficient client scope",
        ):
            api_request("https://api.spotify.com/v1/me/albums", _TOKEN)


# ---------------------------------------------------------------------------
# Task 1.5: HTTP error with non-JSON body raises RuntimeError with raw text
# ---------------------------------------------------------------------------


def test_api_request_non_json_error_uses_raw_body_text() -> None:
    with patch(
        "urllib.request.urlopen",
        side_effect=_http_error(503, "Service Unavailable"),
    ):
        with pytest.raises(
            RuntimeError,
            match=r"Spotify API error \(503 /v1/me/albums\): Service Unavailable",
        ):
            api_request("https://api.spotify.com/v1/me/albums", _TOKEN)


# ---------------------------------------------------------------------------
# Task 1.6: URLError raises RuntimeError describing the network failure
# ---------------------------------------------------------------------------


def test_api_request_url_error_raises_runtime_error() -> None:
    with patch(
        "urllib.request.urlopen",
        side_effect=urllib.error.URLError("connection refused"),
    ):
        with pytest.raises(RuntimeError, match="connection refused"):
            api_request("https://api.spotify.com/v1/me/albums", _TOKEN)


# ---------------------------------------------------------------------------
# Task 1.7: 429 with Retry-After retries and succeeds on second attempt
# ---------------------------------------------------------------------------


def test_api_request_429_with_retry_after_retries_and_succeeds() -> None:
    call_count = [0]

    def flaky_urlopen(_req: Any) -> Any:
        call_count[0] += 1
        if call_count[0] == 1:
            raise _http_error(
                429,
                json.dumps({"error": {"status": 429, "message": "Rate limited"}}),
                retry_after="2",
            )
        return _ok_response({"result": "ok"})

    with patch("urllib.request.urlopen", side_effect=flaky_urlopen):
        with patch("time.sleep") as mock_sleep:
            result = api_request("https://api.spotify.com/v1/me/albums", _TOKEN)

    assert result == {"result": "ok"}
    assert call_count[0] == 2
    mock_sleep.assert_called_once_with(2.0)


def test_api_request_429_sleep_duration_matches_retry_after_header() -> None:
    call_count = [0]

    def once_429(_req: Any) -> Any:
        call_count[0] += 1
        if call_count[0] == 1:
            raise _http_error(429, "{}", retry_after="5")
        return _ok_response({})

    with patch("urllib.request.urlopen", side_effect=once_429):
        with patch("time.sleep") as mock_sleep:
            api_request("https://api.spotify.com/v1/me/albums", _TOKEN)

    mock_sleep.assert_called_once_with(5.0)


# ---------------------------------------------------------------------------
# Task 1.8: 429 with Retry-After three times in a row raises after third attempt
# ---------------------------------------------------------------------------


def test_api_request_429_three_times_raises_after_third_attempt() -> None:
    call_count = [0]

    def always_429(_req: Any) -> Any:
        call_count[0] += 1
        raise _http_error(
            429,
            json.dumps({"error": {"status": 429, "message": "Rate limited"}}),
            retry_after="1",
        )

    with patch("urllib.request.urlopen", side_effect=always_429):
        with patch("time.sleep") as mock_sleep:
            with pytest.raises(RuntimeError, match=r"Spotify API error \(429"):
                api_request("https://api.spotify.com/v1/me/albums", _TOKEN)

    assert call_count[0] == 3
    assert mock_sleep.call_count == 2


# ---------------------------------------------------------------------------
# Task 1.9: 429 without Retry-After raises RuntimeError immediately, no retry
# ---------------------------------------------------------------------------


def test_api_request_429_without_retry_after_raises_immediately() -> None:
    call_count = [0]

    def counting_429(_req: Any) -> Any:
        call_count[0] += 1
        raise _http_error(
            429,
            json.dumps({"error": {"status": 429, "message": "Rate limited"}}),
            retry_after=None,
        )

    with patch("urllib.request.urlopen", side_effect=counting_429):
        with patch("time.sleep") as mock_sleep:
            with pytest.raises(RuntimeError, match=r"Spotify API error \(429"):
                api_request("https://api.spotify.com/v1/me/albums", _TOKEN)

    assert call_count[0] == 1
    mock_sleep.assert_not_called()
