from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from spotify_playlist_creator.lastfm import fetch_artist_genre, get_api_key

# ---------------------------------------------------------------------------
# Group 1: get_api_key
# ---------------------------------------------------------------------------


def test_get_api_key_returns_key_when_set() -> None:
    with patch.dict("os.environ", {"LASTFM_API_KEY": "mykey"}):
        assert get_api_key() == "mykey"


def test_get_api_key_raises_when_key_not_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LASTFM_API_KEY", raising=False)
    with pytest.raises(RuntimeError):
        get_api_key()


# ---------------------------------------------------------------------------
# Group 2: fetch_artist_genre
# ---------------------------------------------------------------------------


def _mock_response(body: dict[str, Any]) -> MagicMock:
    mock = MagicMock()
    mock.read.return_value = json.dumps(body).encode()
    mock.__enter__ = lambda s: s
    mock.__exit__ = MagicMock(return_value=False)
    return mock


def test_fetch_artist_genre_returns_top_tags_by_count() -> None:
    # Adversarial: lower-count tag listed first; must be sorted highest-count first
    body = {
        "toptags": {
            "tag": [
                {"name": "japanese", "count": 50},
                {"name": "j-pop", "count": 100},
            ]
        }
    }
    with patch("urllib.request.urlopen", return_value=_mock_response(body)):
        result = fetch_artist_genre("Tomoyo Harada", "mykey")
    assert result == ["j-pop", "japanese"]


def test_fetch_artist_genre_returns_at_most_three_tags() -> None:
    # Adversarial: 4 tags available; must return only the top 3
    body = {
        "toptags": {
            "tag": [
                {"name": "rock", "count": 10},
                {"name": "j-pop", "count": 100},
                {"name": "japanese", "count": 80},
                {"name": "female vocalists", "count": 60},
            ]
        }
    }
    with patch("urllib.request.urlopen", return_value=_mock_response(body)):
        result = fetch_artist_genre("Tomoyo Harada", "mykey")
    assert result == ["j-pop", "japanese", "female vocalists"]


def test_fetch_artist_genre_returns_empty_list_when_no_tags() -> None:
    body: dict[str, Any] = {"toptags": {"tag": []}}
    with patch("urllib.request.urlopen", return_value=_mock_response(body)):
        result = fetch_artist_genre("Unknown Artist", "mykey")
    assert result == []


def test_fetch_artist_genre_returns_empty_list_for_artist_not_found() -> None:
    body = {"error": 6, "message": "The artist you supplied could not be found"}
    with patch("urllib.request.urlopen", return_value=_mock_response(body)):
        result = fetch_artist_genre("Ghost Artist", "mykey")
    assert result == []


def test_fetch_artist_genre_raises_on_http_error() -> None:
    http_error = urllib.error.HTTPError(
        url="https://ws.audioscrobbler.com/2.0/",
        code=403,
        msg="Forbidden",
        hdrs=MagicMock(),
        fp=None,
    )
    with patch("urllib.request.urlopen", side_effect=http_error):
        with pytest.raises(RuntimeError):
            fetch_artist_genre("Some Artist", "badkey")


def test_fetch_artist_genre_returns_tags_in_lowercase() -> None:
    # Adversarial: Last.fm returns mixed-case tags; spec requires lowercase
    body = {"toptags": {"tag": [{"name": "Hip-Hop", "count": 100}]}}
    with patch("urllib.request.urlopen", return_value=_mock_response(body)):
        result = fetch_artist_genre("Some Artist", "mykey")
    assert result == ["hip-hop"]


def test_fetch_artist_genre_raises_for_non_artist_not_found_error() -> None:
    # Adversarial: only error code 6 should return None; other codes must raise
    body = {"error": 10, "message": "Invalid API key - You must be granted a valid key"}
    with patch("urllib.request.urlopen", return_value=_mock_response(body)):
        with pytest.raises(RuntimeError):
            fetch_artist_genre("Some Artist", "badkey")


def test_fetch_artist_genre_raises_on_network_error() -> None:
    network_error = urllib.error.URLError("Name or service not known")
    with patch("urllib.request.urlopen", side_effect=network_error):
        with pytest.raises(RuntimeError):
            fetch_artist_genre("Some Artist", "mykey")


def test_fetch_artist_genre_sends_correct_query_params() -> None:
    body: dict[str, Any] = {"toptags": {"tag": [{"name": "j-pop", "count": 100}]}}
    captured_urls: list[str] = []

    def capturing_urlopen(req: urllib.request.Request) -> MagicMock:
        captured_urls.append(req.full_url)
        return _mock_response(body)

    with patch("urllib.request.urlopen", side_effect=capturing_urlopen):
        fetch_artist_genre("Tomoyo Harada", "mykey")

    assert len(captured_urls) == 1
    parsed = urllib.parse.urlparse(captured_urls[0])
    params = urllib.parse.parse_qs(parsed.query)
    assert (
        parsed.scheme + "://" + parsed.netloc + parsed.path
        == "https://ws.audioscrobbler.com/2.0/"
    )
    assert params["method"] == ["artist.gettoptags"]
    assert params["artist"] == ["Tomoyo Harada"]
    assert params["api_key"] == ["mykey"]
    assert params["format"] == ["json"]
