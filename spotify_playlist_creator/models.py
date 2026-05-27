from __future__ import annotations

import dataclasses
from datetime import datetime


@dataclasses.dataclass
class Artist:
    id: str
    name: str


@dataclasses.dataclass(frozen=True)
class RawRelease:
    id: str
    name: str
    album_type: str
    release_date: str


@dataclasses.dataclass(frozen=True)
class Album:
    id: str
    name: str
    release_date: str


@dataclasses.dataclass
class SavedAlbum:
    id: str
    name: str
    artists: list[Artist]
    added_at: datetime
