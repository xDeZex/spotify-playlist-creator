from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request

_BASE_URL = "https://ws.audioscrobbler.com/2.0/"


def get_api_key() -> str:
    key = os.environ.get("LASTFM_API_KEY")
    if key is None:
        raise RuntimeError("LASTFM_API_KEY environment variable is not set")
    return key


def fetch_artist_genre(artist_name: str, api_key: str) -> list[str]:
    params = urllib.parse.urlencode(
        {
            "method": "artist.gettoptags",
            "artist": artist_name,
            "api_key": api_key,
            "format": "json",
        }
    )
    url = f"{_BASE_URL}?{params}"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req) as response:
            body: dict[str, object] = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Last.fm API error ({exc.code})") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Last.fm network error: {exc.reason}") from exc

    if "error" in body:
        if body.get("error") == 6:
            return []
        raise RuntimeError(f"Last.fm error: {body.get('message', body['error'])}")

    tags = body.get("toptags", {})
    tag_list = tags.get("tag", []) if isinstance(tags, dict) else []
    if not tag_list:
        return []

    sorted_tags = sorted(tag_list, key=lambda t: int(t["count"]), reverse=True)
    return [str(t["name"]).lower() for t in sorted_tags[:3]]
