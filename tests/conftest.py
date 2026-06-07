from __future__ import annotations

import pathlib
from collections.abc import Generator
from unittest.mock import patch

import pytest

import spotify_playlist_creator.api as _api
import spotify_playlist_creator.status as _status


def _noop_fn(_: str) -> None:
    pass


@pytest.fixture(autouse=True)
def _reset_status() -> Generator[None, None, None]:
    _status.configure(_noop_fn)
    _status.set_context("")
    yield


@pytest.fixture(autouse=True)
def _no_proactive_delay(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_api, "_proactive_delay", lambda is_write=False: None)


@pytest.fixture(autouse=True)
def _no_token_cache(tmp_path: pathlib.Path) -> Generator[None, None, None]:
    """Patch _TOKEN_PATH so each test starts without a cached token."""
    with patch(
        "spotify_playlist_creator.auth._TOKEN_PATH",
        tmp_path / ".spotify_token.json",
    ):
        yield
