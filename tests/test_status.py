from __future__ import annotations

import importlib
from typing import Any

import spotify_playlist_creator.status as status

# ---------------------------------------------------------------------------
# Task 1.1: write() assembles \r\033[2K{msg} and calls the callable
# ---------------------------------------------------------------------------


def test_write_emits_erase_and_message_with_no_context() -> None:
    received: list[str] = []
    status.configure(received.append)
    status.write("fetching releases (1/3)...")
    assert received == ["\r\033[2Kfetching releases (1/3)..."]


# ---------------------------------------------------------------------------
# Task 1.2: set_context() causes write() to prepend {ctx} —
# ---------------------------------------------------------------------------


def test_write_with_context_prepends_context_and_separator() -> None:
    received: list[str] = []
    status.configure(received.append)
    status.set_context("[3/10] Radiohead")
    status.write("fetching releases (2/4)...")
    assert received == ["\r\033[2K[3/10] Radiohead — fetching releases (2/4)..."]


# ---------------------------------------------------------------------------
# Task 1.3: Empty context produces no prefix separator
# ---------------------------------------------------------------------------


def test_write_with_empty_context_omits_separator() -> None:
    received: list[str] = []
    status.configure(received.append)
    status.set_context("")
    status.write("msg")
    assert received == ["\r\033[2Kmsg"]


# ---------------------------------------------------------------------------
# Task 1.4: clear() emits \r\033[2K to stdout, flushes, resets context
# ---------------------------------------------------------------------------


def test_clear_writes_erase_sequence_and_resets_context(capsys: Any) -> None:
    status.set_context("[1/5] Artist")
    status.clear()
    captured = capsys.readouterr()
    assert captured.out == "\r\033[2K"
    # After clear, context must be empty — write should carry no separator
    received: list[str] = []
    status.configure(received.append)
    status.write("next")
    assert received == ["\r\033[2Knext"]


def test_clear_is_safe_with_no_prior_writes(capsys: Any) -> None:
    status.clear()
    captured = capsys.readouterr()
    assert captured.out == "\r\033[2K"


# ---------------------------------------------------------------------------
# Task 1.5: configure() replaces the callable; write() invokes the new one
# ---------------------------------------------------------------------------


def test_configure_replaces_callable() -> None:
    calls_fn1: list[str] = []
    calls_fn2: list[str] = []
    status.configure(calls_fn1.append)
    status.configure(calls_fn2.append)
    status.write("x")
    assert calls_fn1 == []
    assert calls_fn2 == ["\r\033[2Kx"]


def test_configure_callable_receives_assembled_line_with_escape_codes() -> None:
    received: list[str] = []
    status.configure(received.append)
    status.write("hello")
    assert len(received) == 1
    assert received[0] == "\r\033[2Khello"


# ---------------------------------------------------------------------------
# Task 1.6: Default callable is no-op — write() before configure() does not raise
# ---------------------------------------------------------------------------


def test_write_before_configure_does_not_raise() -> None:
    importlib.reload(status)
    status.write("anything")  # no-op default — must not raise
