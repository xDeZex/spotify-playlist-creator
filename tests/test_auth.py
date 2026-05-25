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

import spotify_playlist_creator.auth as _auth
from spotify_playlist_creator import run
from spotify_playlist_creator.auth import (
    _CALLBACK_HOST,
    _CALLBACK_PORT,
    _REDIRECT_URI,
    _TOKEN_URL,
    SpotifyToken,
    _load_token,
    _save_token,
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
    access_token: str = "test_access_token",
    token_type: str = "Bearer",
    refresh_token: str = "test_refresh_token",
    expires_in: int = 3600,
) -> Any:
    class _Response:
        def read(self) -> bytes:
            payload = {
                "access_token": access_token,
                "token_type": token_type,
                "refresh_token": refresh_token,
                "expires_in": expires_in,
            }
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


def test_spotify_token_fields() -> None:
    token = SpotifyToken(
        access_token="abc123",
        token_type="Bearer",
        refresh_token="rtoken123",
        expires_at=9999999999.0,
    )
    assert token.access_token == "abc123"
    assert token.token_type == "Bearer"
    assert token.refresh_token == "rtoken123"
    assert token.expires_at == 9999999999.0


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
            except (OSError, http.client.HTTPException):
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

    time.sleep(0.2)  # let OS close the socket
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
    assert token.refresh_token == "test_refresh_token"
    assert token.expires_at > 0


def test_exchange_code_captures_refresh_token_and_expires_at(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_secret")

    with patch("webbrowser.open", side_effect=_browser_mock()):
        with patch(
            "urllib.request.urlopen",
            return_value=_fake_token_response(
                refresh_token="real_rtoken", expires_in=3600
            ),
        ):
            token = authenticate()

    assert token.refresh_token == "real_rtoken"
    assert pytest.approx(token.expires_at, abs=5) == time.time() + 3600


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
# Group 5: Token persistence helpers
# ---------------------------------------------------------------------------

_SAMPLE_TOKEN = SpotifyToken(
    access_token="atok",
    token_type="Bearer",
    refresh_token="rtok",
    expires_at=12345.0,
)


def test_save_token_writes_all_fields() -> None:
    _save_token(_SAMPLE_TOKEN)
    data = json.loads(_auth._TOKEN_PATH.read_text())
    assert data["access_token"] == "atok"
    assert data["token_type"] == "Bearer"
    assert data["refresh_token"] == "rtok"
    assert data["expires_at"] == 12345.0


def test_load_token_returns_token_from_valid_file() -> None:
    _save_token(_SAMPLE_TOKEN)
    assert _load_token() == _SAMPLE_TOKEN


def test_load_token_returns_none_when_file_absent() -> None:
    _auth._TOKEN_PATH.unlink(missing_ok=True)
    assert _load_token() is None


def test_load_token_returns_none_for_corrupt_json() -> None:
    _auth._TOKEN_PATH.write_text("not valid json{{{", encoding="utf-8")
    assert _load_token() is None


def test_load_token_returns_none_when_field_missing() -> None:
    _auth._TOKEN_PATH.write_text(
        json.dumps({"access_token": "atok", "token_type": "Bearer"}),
        encoding="utf-8",
    )
    assert _load_token() is None


def test_load_token_returns_none_for_non_utf8_content() -> None:
    _auth._TOKEN_PATH.write_bytes(b"\xff\xfe invalid bytes")
    assert _load_token() is None


# ---------------------------------------------------------------------------
# Group 6: authenticate() caching, refresh, and save
# ---------------------------------------------------------------------------


def test_authenticate_returns_cached_token_when_valid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_secret")
    _save_token(
        SpotifyToken(
            access_token="cached_tok",
            token_type="Bearer",
            refresh_token="cached_rtoken",
            expires_at=time.time() + 3600,
        )
    )

    with patch("webbrowser.open") as mock_browser:
        with patch("urllib.request.urlopen") as mock_urlopen:
            token = authenticate()

    mock_browser.assert_not_called()
    mock_urlopen.assert_not_called()
    assert token.access_token == "cached_tok"


def test_authenticate_falls_through_when_cache_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_secret")

    with patch("webbrowser.open", side_effect=_browser_mock()):
        with patch(
            "urllib.request.urlopen",
            return_value=_fake_token_response(),
        ):
            token = authenticate()

    assert token.access_token == "test_access_token"


def test_authenticate_refreshes_expired_token_silently(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_secret")
    _save_token(
        SpotifyToken(
            access_token="old_tok",
            token_type="Bearer",
            refresh_token="refresh_me",
            expires_at=time.time() - 10,
        )
    )

    with patch("webbrowser.open") as mock_browser:
        with patch(
            "urllib.request.urlopen",
            return_value=_fake_token_response(
                access_token="new_tok", refresh_token="new_rtoken"
            ),
        ):
            token = authenticate()

    mock_browser.assert_not_called()
    assert token.access_token == "new_tok"


def test_authenticate_refreshes_token_expiring_within_60s_buffer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_secret")
    _save_token(
        SpotifyToken(
            access_token="old_tok",
            token_type="Bearer",
            refresh_token="refresh_me",
            expires_at=time.time() + 30,
        )
    )

    with patch("webbrowser.open") as mock_browser:
        with patch(
            "urllib.request.urlopen",
            return_value=_fake_token_response(access_token="refreshed_tok"),
        ):
            token = authenticate()

    mock_browser.assert_not_called()
    assert token.access_token == "refreshed_tok"


def test_authenticate_falls_through_to_browser_when_refresh_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_secret")
    _save_token(
        SpotifyToken(
            access_token="old_tok",
            token_type="Bearer",
            refresh_token="bad_refresh",
            expires_at=time.time() - 10,
        )
    )

    def grant_type_aware_urlopen(req: Any, *args: Any, **kwargs: Any) -> Any:
        params = dict(urllib.parse.parse_qsl(req.data.decode()))
        if params.get("grant_type") == "refresh_token":
            raise urllib.error.HTTPError(
                url=_TOKEN_URL,
                code=400,
                msg="Bad Request",
                hdrs=MagicMock(),
                fp=io.BytesIO(b"invalid_grant"),
            )
        return _fake_token_response(access_token="browser_tok")

    browser_called = [False]

    def recording_browser(url: str) -> None:
        browser_called[0] = True
        _browser_mock()(url)

    with patch("webbrowser.open", side_effect=recording_browser):
        with patch("urllib.request.urlopen", side_effect=grant_type_aware_urlopen):
            token = authenticate()

    assert browser_called[0]
    assert token.access_token == "browser_tok"


def test_authenticate_saves_token_after_browser_flow(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_secret")

    with patch("webbrowser.open", side_effect=_browser_mock()):
        with patch(
            "urllib.request.urlopen",
            return_value=_fake_token_response(access_token="saved_tok"),
        ):
            authenticate()

    assert _auth._TOKEN_PATH.exists()
    data = json.loads(_auth._TOKEN_PATH.read_text())
    assert data["access_token"] == "saved_tok"


def test_authenticate_saves_new_token_after_refresh_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_secret")
    _save_token(
        SpotifyToken(
            access_token="old_tok",
            token_type="Bearer",
            refresh_token="bad_refresh",
            expires_at=time.time() - 10,
        )
    )

    def grant_type_aware_urlopen(req: Any, *args: Any, **kwargs: Any) -> Any:
        params = dict(urllib.parse.parse_qsl(req.data.decode()))
        if params.get("grant_type") == "refresh_token":
            raise urllib.error.HTTPError(
                url=_TOKEN_URL,
                code=400,
                msg="Bad Request",
                hdrs=MagicMock(),
                fp=io.BytesIO(b"invalid_grant"),
            )
        return _fake_token_response(access_token="browser_tok")

    with patch("webbrowser.open", side_effect=_browser_mock()):
        with patch("urllib.request.urlopen", side_effect=grant_type_aware_urlopen):
            authenticate()

    data = json.loads(_auth._TOKEN_PATH.read_text())
    assert data["access_token"] == "browser_tok"


def test_authenticate_saves_token_after_silent_refresh(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_secret")
    _save_token(
        SpotifyToken(
            access_token="old_tok",
            token_type="Bearer",
            refresh_token="refresh_me",
            expires_at=time.time() - 10,
        )
    )

    with patch("webbrowser.open"):
        with patch(
            "urllib.request.urlopen",
            return_value=_fake_token_response(
                access_token="refreshed_tok", refresh_token="new_rtoken"
            ),
        ):
            authenticate()

    data = json.loads(_auth._TOKEN_PATH.read_text())
    assert data["access_token"] == "refreshed_tok"
    assert data["refresh_token"] == "new_rtoken"


def test_refresh_access_token_preserves_old_refresh_token_when_omitted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_secret")
    _save_token(
        SpotifyToken(
            access_token="old_tok",
            token_type="Bearer",
            refresh_token="original_rtoken",
            expires_at=time.time() - 10,
        )
    )

    class _ResponseWithoutRefreshToken:
        def read(self) -> bytes:
            return json.dumps(
                {"access_token": "new_tok", "token_type": "Bearer", "expires_in": 3600}
            ).encode()

        def __enter__(self) -> _ResponseWithoutRefreshToken:
            return self

        def __exit__(self, *args: Any) -> None:
            pass

    with patch("webbrowser.open"):
        with patch(
            "urllib.request.urlopen",
            return_value=_ResponseWithoutRefreshToken(),
        ):
            token = authenticate()

    assert token.refresh_token == "original_rtoken"


def test_refresh_access_token_preserves_old_refresh_token_when_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_secret")
    _save_token(
        SpotifyToken(
            access_token="old_tok",
            token_type="Bearer",
            refresh_token="original_rtoken",
            expires_at=time.time() - 10,
        )
    )

    class _ResponseWithEmptyRefreshToken:
        def read(self) -> bytes:
            return json.dumps(
                {
                    "access_token": "new_tok",
                    "token_type": "Bearer",
                    "refresh_token": "",
                    "expires_in": 3600,
                }
            ).encode()

        def __enter__(self) -> _ResponseWithEmptyRefreshToken:
            return self

        def __exit__(self, *args: Any) -> None:
            pass

    with patch("webbrowser.open"):
        with patch(
            "urllib.request.urlopen",
            return_value=_ResponseWithEmptyRefreshToken(),
        ):
            token = authenticate()

    assert token.refresh_token == "original_rtoken"


def test_authenticate_falls_through_to_browser_when_refresh_raises_url_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_secret")
    _save_token(
        SpotifyToken(
            access_token="old_tok",
            token_type="Bearer",
            refresh_token="refresh_me",
            expires_at=time.time() - 10,
        )
    )

    def url_error_on_refresh_urlopen(req: Any, *args: Any, **kwargs: Any) -> Any:
        params = dict(urllib.parse.parse_qsl(req.data.decode()))
        if params.get("grant_type") == "refresh_token":
            raise urllib.error.URLError("connection refused")
        return _fake_token_response(access_token="browser_tok")

    browser_called = [False]

    def recording_browser(url: str) -> None:
        browser_called[0] = True
        _browser_mock()(url)

    with patch("webbrowser.open", side_effect=recording_browser):
        with patch("urllib.request.urlopen", side_effect=url_error_on_refresh_urlopen):
            token = authenticate()

    assert browser_called[0]
    assert token.access_token == "browser_tok"


# ---------------------------------------------------------------------------
# Group 7: Integration with run()
# ---------------------------------------------------------------------------


def test_run_calls_authenticate(monkeypatch: pytest.MonkeyPatch) -> None:
    call_count = [0]

    def mock_authenticate(**kwargs: Any) -> SpotifyToken:
        call_count[0] += 1
        return SpotifyToken(
            access_token="tok",
            token_type="Bearer",
            refresh_token="rtoken",
            expires_at=9999999999.0,
        )

    monkeypatch.setattr("spotify_playlist_creator.authenticate", mock_authenticate)
    run()

    assert call_count[0] == 1


def test_run_token_available_for_downstream(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        "spotify_playlist_creator.authenticate",
        lambda **kwargs: SpotifyToken(
            access_token="downstream_tok",
            token_type="Bearer",
            refresh_token="rtoken",
            expires_at=9999999999.0,
        ),
    )
    run()
    assert "Bearer" in capsys.readouterr().out
