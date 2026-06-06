from __future__ import annotations

import sys
from collections.abc import Callable


def _noop(_: str) -> None:
    pass


_fn: Callable[[str], None] = _noop
_ctx: str = ""


def write(msg: str) -> None:
    line = f"\r\033[2K{_ctx} — {msg}" if _ctx else f"\r\033[2K{msg}"
    _fn(line)


def set_context(ctx: str) -> None:
    global _ctx
    _ctx = ctx


def clear() -> None:
    global _ctx
    sys.stdout.write("\r\033[2K")
    sys.stdout.flush()
    _ctx = ""


def configure(fn: Callable[[str], None]) -> None:
    global _fn
    _fn = fn
