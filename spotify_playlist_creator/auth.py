from __future__ import annotations

import base64
import dataclasses
import http.server
import json
import os
import pathlib
import secrets
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from typing import Any

_CALLBACK_HOST = "127.0.0.1"
_CALLBACK_PORT = 8888
_REDIRECT_URI = f"http://{_CALLBACK_HOST}:{_CALLBACK_PORT}/callback"
_TOKEN_URL = "https://accounts.spotify.com/api/token"
_AUTH_BASE_URL = "https://accounts.spotify.com/authorize"
_SCOPES = (
    "user-library-read playlist-read-private "
    "playlist-modify-public playlist-modify-private"
)
_TOKEN_PATH = pathlib.Path(".spotify_token.json")


@dataclasses.dataclass(frozen=True)
class SpotifyToken:
    """Immutable token grant returned by the Spotify token endpoint."""

    access_token: str
    token_type: str
    refresh_token: str
    expires_at: float


def _save_token(token: SpotifyToken) -> None:
    _TOKEN_PATH.write_text(
        json.dumps(
            {
                "access_token": token.access_token,
                "token_type": token.token_type,
                "refresh_token": token.refresh_token,
                "expires_at": token.expires_at,
            }
        ),
        encoding="utf-8",
    )


def _load_token() -> SpotifyToken | None:
    try:
        data: dict[str, Any] = json.loads(_TOKEN_PATH.read_text(encoding="utf-8"))
        return SpotifyToken(
            access_token=str(data["access_token"]),
            token_type=str(data["token_type"]),
            refresh_token=str(data["refresh_token"]),
            expires_at=float(data["expires_at"]),
        )
    except (
        FileNotFoundError,
        UnicodeDecodeError,
        json.JSONDecodeError,
        KeyError,
        ValueError,
        TypeError,
    ):
        return None


def authenticate(*, _timeout: float = 120.0) -> SpotifyToken:
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    if client_id is None:
        raise ValueError("Missing environment variable: SPOTIFY_CLIENT_ID")

    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    if client_secret is None:
        raise ValueError("Missing environment variable: SPOTIFY_CLIENT_SECRET")

    cached = _load_token()
    if cached is not None:
        if time.time() < cached.expires_at - 60:
            return cached
        try:
            token = _refresh_access_token(
                client_id, client_secret, cached.refresh_token
            )
            _save_token(token)
            return token
        except RuntimeError:
            pass

    state = secrets.token_urlsafe(16)
    auth_url = _build_auth_url(client_id, state)
    code = _run_local_auth_flow(auth_url, state, timeout=_timeout)
    token = _exchange_code(client_id, client_secret, code)
    _save_token(token)
    return token


def _refresh_access_token(
    client_id: str, client_secret: str, refresh_token: str
) -> SpotifyToken:
    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    data = urllib.parse.urlencode(
        {"grant_type": "refresh_token", "refresh_token": refresh_token}
    ).encode()
    req = urllib.request.Request(
        _TOKEN_URL,
        data=data,
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    try:
        with urllib.request.urlopen(req) as response:
            body: dict[str, Any] = json.loads(response.read())
            new_refresh = (
                str(body["refresh_token"])
                if body.get("refresh_token")
                else refresh_token
            )
            try:
                return SpotifyToken(
                    access_token=str(body["access_token"]),
                    token_type=str(body["token_type"]),
                    refresh_token=new_refresh,
                    expires_at=time.time() + float(body["expires_in"]),
                )
            except (KeyError, ValueError, TypeError) as exc:
                raise RuntimeError(
                    f"Token refresh response missing expected fields: {exc}"
                ) from exc
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode()
        raise RuntimeError(
            f"Token refresh failed: HTTP {exc.code} {body_text}"
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Token refresh failed: {exc.reason}") from exc


def _build_auth_url(client_id: str, state: str) -> str:
    params = urllib.parse.urlencode(
        {
            "client_id": client_id,
            "redirect_uri": _REDIRECT_URI,
            "response_type": "code",
            "scope": _SCOPES,
            "state": state,
        }
    )
    return f"{_AUTH_BASE_URL}?{params}"


class _CallbackResult:
    def __init__(self) -> None:
        self.code: str | None = None
        self.error: str | None = None
        self.received_state: str | None = None
        self._event = threading.Event()

    def signal(self, *, code: str | None, error: str | None, state: str | None) -> None:
        self.code = code
        self.error = error
        self.received_state = state
        self._event.set()

    def wait(self, timeout: float) -> bool:
        return self._event.wait(timeout=timeout)


def _run_local_auth_flow(auth_url: str, expected_state: str, timeout: float) -> str:
    result = _CallbackResult()

    class _Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path != "/callback":
                self.send_response(404)
                self.end_headers()
                return
            params = dict(urllib.parse.parse_qsl(parsed.query))
            self.send_response(200)
            self.end_headers()
            if params.get("error"):
                self.wfile.write(
                    f"Authentication failed: {params['error']}. You can close this tab.".encode()
                )
            else:
                self.wfile.write(b"Authentication complete. You can close this tab.")
            result.signal(
                code=params.get("code"),
                error=params.get("error"),
                state=params.get("state"),
            )

        def log_message(self, format: str, *args: Any) -> None:
            pass

    server = http.server.HTTPServer((_CALLBACK_HOST, _CALLBACK_PORT), _Handler)
    thread = threading.Thread(
        target=lambda: server.serve_forever(poll_interval=0.05), daemon=True
    )
    thread.start()

    print(f"Opening Spotify auth page: {auth_url}")
    webbrowser.open(auth_url)

    try:
        completed = result.wait(timeout=timeout)
        if not completed:
            raise TimeoutError(
                f"Spotify authentication timed out after {timeout} seconds"
            )

        if result.received_state != expected_state:
            raise ValueError(
                f"OAuth state mismatch: expected {expected_state!r}, "
                f"got {result.received_state!r}"
            )

        if result.error is not None:
            raise RuntimeError(f"Spotify auth error: {result.error}")

        if result.code is None:
            raise RuntimeError("OAuth callback received no authorization code")

        return result.code
    finally:
        server.shutdown()
        server.server_close()


def _exchange_code(client_id: str, client_secret: str, code: str) -> SpotifyToken:
    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    data = urllib.parse.urlencode(
        {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": _REDIRECT_URI,
        }
    ).encode()
    req = urllib.request.Request(
        _TOKEN_URL,
        data=data,
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    try:
        with urllib.request.urlopen(req) as response:
            body: dict[str, Any] = json.loads(response.read())
            try:
                return SpotifyToken(
                    access_token=str(body["access_token"]),
                    token_type=str(body["token_type"]),
                    refresh_token=str(body["refresh_token"]),
                    expires_at=time.time() + float(body["expires_in"]),
                )
            except (KeyError, ValueError, TypeError) as exc:
                raise RuntimeError(
                    f"Token exchange response missing expected fields: {exc}"
                ) from exc
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode()
        raise RuntimeError(
            f"Token exchange failed: HTTP {exc.code} {body_text}"
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Token exchange failed: {exc.reason}") from exc
