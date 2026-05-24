from __future__ import annotations

import http.client
import io
import json
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from spotify_playlist_creator import run
from spotify_playlist_creator.auth import (
    _CALLBACK_HOST,
    _CALLBACK_PORT,
    _REDIRECT_URI,
    SpotifyToken,
    authenticate,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _send_callback(state: str, code: str = "test_code") -> None:
    time.sleep(0.05)
    try:
        conn = http.client.HTTPConnection(_CALLBACK_HOST, _CALLBACK_PORT, timeout=5)
        path = (
            f"/callback"
            f"?code={urllib.parse.quote(code)}"
            f"&state={urllib.parse.quote(state)}"
        )
        conn.request("GET", path)
        conn.getresponse()
    except (OSError, http.client.HTTPException):
        pass


def _send_error_callback(state: str, error: str = "access_denied") -> None:
    time.sleep(0.05)
    try:
        conn = http.client.HTTPConnection(_CALLBACK_HOST, _CALLBACK_PORT, timeout=5)
        path = (
            f"/callback"
            f"?error={urllib.parse.quote(error)}"
            f"&state={urllib.parse.quote(state)}"
        )
        conn.request("GET", path)
        conn.getresponse()
    except (OSError, http.client.HTTPException):
        pass


def _send_bad_state_callback() -> None:
    time.sleep(0.05)
    try:
        conn = http.client.HTTPConnection(_CALLBACK_HOST, _CALLBACK_PORT, timeout=5)
        conn.request("GET", "/callback?code=abc&state=wrong_state")
        conn.getresponse()
    except (OSError, http.client.HTTPException):
        pass


def _fake_token_response(
    access_token: str = "test_access_token", token_type: str = "Bearer"
) -> Any:
    class _Response:
        def read(self) -> bytes:
            payload = {"access_token": access_token, "token_type": token_type}
            return json.dumps(payload).encode()

        def __enter__(self) -> _Response:
            return self

        def __exit__(self, *args: Any) -> None:
            pass

    return _Response()


def _browser_mock(*, error: str | None = None, bad_state: bool = False) -> Any:
    """Returns a fake webbrowser.open that triggers the OAuth callback immediately."""

    def fake_open(url: str) -> None:
        parsed = urllib.parse.urlparse(url)
        state = dict(urllib.parse.parse_qsl(parsed.query)).get("state", "")
        if bad_state:
            threading.Thread(target=_send_bad_state_callback, daemon=True).start()
        elif error is not None:
            threading.Thread(
                target=_send_error_callback, args=(state, error), daemon=True
            ).start()
        else:
            threading.Thread(target=_send_callback, args=(state,), daemon=True).start()

    return fake_open


# ---------------------------------------------------------------------------
# Group 1: SpotifyToken type and auth module skeleton
# ---------------------------------------------------------------------------


def test_spotify_token_has_access_token_and_token_type() -> None:
    token = SpotifyToken(access_token="abc123", token_type="Bearer")
    assert token.access_token == "abc123"
    assert token.token_type == "Bearer"


def test_authenticate_raises_for_missing_client_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("SPOTIFY_CLIENT_ID", raising=False)
    monkeypatch.delenv("SPOTIFY_CLIENT_SECRET", raising=False)
    with pytest.raises(ValueError, match="SPOTIFY_CLIENT_ID"):
        authenticate()


def test_authenticate_raises_for_missing_client_secret(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_id")
    monkeypatch.delenv("SPOTIFY_CLIENT_SECRET", raising=False)
    with pytest.raises(ValueError, match="SPOTIFY_CLIENT_SECRET"):
        authenticate()


def test_authenticate_has_no_side_effects_when_env_vars_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("SPOTIFY_CLIENT_ID", raising=False)
    monkeypatch.delenv("SPOTIFY_CLIENT_SECRET", raising=False)
    with patch("urllib.request.urlopen") as mock_urlopen:
        with patch("webbrowser.open") as mock_browser:
            with pytest.raises(ValueError):
                authenticate()
    mock_urlopen.assert_not_called()
    mock_browser.assert_not_called()


# ---------------------------------------------------------------------------
# Group 2: Browser-based authorization
# ---------------------------------------------------------------------------


def test_authenticate_opens_browser(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_secret")
    opened: list[str] = []

    def capturing_open(url: str) -> None:
        opened.append(url)
        _browser_mock()(url)

    with patch("webbrowser.open", side_effect=capturing_open):
        with patch("urllib.request.urlopen", return_value=_fake_token_response()):
            authenticate()

    assert len(opened) == 1


def test_authenticate_auth_url_has_required_params(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "my_client_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "my_secret")
    captured: list[str] = []

    def capturing_open(url: str) -> None:
        captured.append(url)
        _browser_mock()(url)

    with patch("webbrowser.open", side_effect=capturing_open):
        with patch("urllib.request.urlopen", return_value=_fake_token_response()):
            authenticate()

    assert captured, "webbrowser.open was not called"
    params = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(captured[0]).query))
    assert params["client_id"] == "my_client_id"
    assert params["redirect_uri"] == _REDIRECT_URI
    assert params["response_type"] == "code"
    assert params.get("state"), "state nonce missing"
    assert params.get("scope"), "scope missing"


def test_authenticate_prints_auth_url_to_stdout(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_secret")

    with patch("webbrowser.open", side_effect=_browser_mock()):
        with patch("urllib.request.urlopen", return_value=_fake_token_response()):
            authenticate()

    assert "accounts.spotify.com/authorize" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Group 3: Local callback server
# ---------------------------------------------------------------------------


def test_callback_server_extracts_code(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_secret")
    exchanged_codes: list[str] = []
    original_urlopen = urllib.request.urlopen

    def intercept_urlopen(req: Any, *args: Any, **kwargs: Any) -> Any:
        url: str = req.full_url if hasattr(req, "full_url") else str(req)
        if "accounts.spotify.com/api/token" in url:
            data = req.data.decode() if req.data else ""
            params = dict(urllib.parse.parse_qsl(data))
            exchanged_codes.append(params.get("code", ""))
            return _fake_token_response()
        return original_urlopen(req, *args, **kwargs)

    def capturing_open(url: str) -> None:
        parsed = urllib.parse.urlparse(url)
        state = dict(urllib.parse.parse_qsl(parsed.query)).get("state", "")
        threading.Thread(
            target=_send_callback, args=(state, "specific_code"), daemon=True
        ).start()

    with patch("webbrowser.open", side_effect=capturing_open):
        with patch("urllib.request.urlopen", side_effect=intercept_urlopen):
            authenticate()

    assert exchanged_codes == ["specific_code"]


def test_authenticate_raises_on_oauth_error_callback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_secret")

    with patch("webbrowser.open", side_effect=_browser_mock(error="access_denied")):
        with pytest.raises(RuntimeError, match="access_denied"):
            authenticate()


def test_authenticate_raises_on_state_mismatch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_secret")

    with patch("webbrowser.open", side_effect=_browser_mock(bad_state=True)):
        with pytest.raises(ValueError, match="[Ss]tate"):
            authenticate()


def test_authenticate_state_mismatch_takes_priority_over_oauth_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_secret")

    def send_error_with_bad_state(url: str) -> None:
        def send() -> None:
            time.sleep(0.05)
            try:
                conn = http.client.HTTPConnection(
                    _CALLBACK_HOST, _CALLBACK_PORT, timeout=5
                )
                conn.request("GET", "/callback?error=access_denied&state=wrong_state")
                conn.getresponse()
            except (OSError, http.client.HTTPException):
                pass

        threading.Thread(target=send, daemon=True).start()

    with patch("webbrowser.open", side_effect=send_error_with_bad_state):
        with pytest.raises(ValueError, match="[Ss]tate"):
            authenticate()


def test_authenticate_raises_when_callback_has_no_code_or_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_secret")

    def bare_state_callback(url: str) -> None:
        parsed = urllib.parse.urlparse(url)
        state = dict(urllib.parse.parse_qsl(parsed.query)).get("state", "")

        def send() -> None:
            time.sleep(0.05)
            try:
                conn = http.client.HTTPConnection(
                    _CALLBACK_HOST, _CALLBACK_PORT, timeout=5
                )
                conn.request("GET", f"/callback?state={urllib.parse.quote(state)}")
                conn.getresponse()
            except Exception:
                pass

        threading.Thread(target=send, daemon=True).start()

    with patch("webbrowser.open", side_effect=bare_state_callback):
        with pytest.raises(RuntimeError, match="no authorization code"):
            authenticate()


def test_authenticate_raises_timeout_when_no_callback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_secret")

    with patch("webbrowser.open"):  # no-op — no callback sent
        with pytest.raises(TimeoutError):
            authenticate(_timeout=0.1)


def test_callback_server_shuts_down_after_authenticate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_secret")

    with patch("webbrowser.open", side_effect=_browser_mock()):
        with patch("urllib.request.urlopen", return_value=_fake_token_response()):
            authenticate()

    time.sleep(0.05)  # let OS close the socket
    try:
        conn = http.client.HTTPConnection(_CALLBACK_HOST, _CALLBACK_PORT, timeout=1)
        conn.request("GET", "/")
        conn.getresponse()
        pytest.fail(f"Port {_CALLBACK_PORT} still open after authenticate() returned")
    except (ConnectionRefusedError, OSError):
        pass  # expected — server has shut down


# ---------------------------------------------------------------------------
# Group 4: Token exchange
# ---------------------------------------------------------------------------


def test_authenticate_returns_spotify_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_secret")

    with patch("webbrowser.open", side_effect=_browser_mock()):
        with patch(
            "urllib.request.urlopen",
            return_value=_fake_token_response("real_token", "Bearer"),
        ):
            token = authenticate()

    assert token.access_token == "real_token"
    assert token.token_type == "Bearer"


def test_authenticate_raises_on_token_exchange_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_secret")

    def failing_urlopen(req: Any, *args: Any, **kwargs: Any) -> Any:
        raise urllib.error.HTTPError(
            url="https://accounts.spotify.com/api/token",
            code=400,
            msg="Bad Request",
            hdrs=MagicMock(),
            fp=io.BytesIO(b"invalid_client"),
        )

    with patch("webbrowser.open", side_effect=_browser_mock()):
        with patch("urllib.request.urlopen", side_effect=failing_urlopen):
            with pytest.raises(RuntimeError, match="400"):
                authenticate()


def test_authenticate_raises_on_token_exchange_url_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_secret")

    def failing_urlopen(req: Any, *args: Any, **kwargs: Any) -> Any:
        raise urllib.error.URLError("connection refused")

    with patch("webbrowser.open", side_effect=_browser_mock()):
        with patch("urllib.request.urlopen", side_effect=failing_urlopen):
            with pytest.raises(RuntimeError, match="connection refused"):
                authenticate()


# ---------------------------------------------------------------------------
# Group 5: Integration with run()
# ---------------------------------------------------------------------------


def test_run_calls_authenticate(monkeypatch: pytest.MonkeyPatch) -> None:
    call_count = [0]

    def mock_authenticate(**kwargs: Any) -> SpotifyToken:
        call_count[0] += 1
        return SpotifyToken(access_token="tok", token_type="Bearer")

    monkeypatch.setattr("spotify_playlist_creator.authenticate", mock_authenticate)
    run()

    assert call_count[0] == 1


def test_run_token_available_for_downstream(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        "spotify_playlist_creator.authenticate",
        lambda **kwargs: SpotifyToken(
            access_token="downstream_tok", token_type="Bearer"
        ),
    )
    run()
    assert "Bearer" in capsys.readouterr().out
