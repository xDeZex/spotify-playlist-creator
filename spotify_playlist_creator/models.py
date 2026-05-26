from __future__ import annotations

import dataclasses
from datetime import datetime


@dataclasses.dataclass
class Artist:
    id: str
    name: str


@dataclasses.dataclass
class SavedAlbum:
    id: str
    name: str
    artists: list[Artist]
    added_at: datetime
