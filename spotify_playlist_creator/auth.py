from __future__ import annotations

import base64
import dataclasses
import http.server
import json
import os
import secrets
import threading
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


@dataclasses.dataclass(frozen=True)
class SpotifyToken:
    access_token: str
    token_type: str


def authenticate(*, _timeout: float = 120.0) -> SpotifyToken:
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    if client_id is None:
        raise ValueError("Missing environment variable: SPOTIFY_CLIENT_ID")

    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    if client_secret is None:
        raise ValueError("Missing environment variable: SPOTIFY_CLIENT_SECRET")

    state = secrets.token_urlsafe(16)
    auth_url = _build_auth_url(client_id, state)
    code = _run_local_auth_flow(auth_url, state, timeout=_timeout)
    return _exchange_code(client_id, client_secret, code)


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
            return SpotifyToken(
                access_token=str(body["access_token"]),
                token_type=str(body["token_type"]),
            )
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode()
        raise RuntimeError(
            f"Token exchange failed: HTTP {exc.code} {body_text}"
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Token exchange failed: {exc.reason}") from exc
