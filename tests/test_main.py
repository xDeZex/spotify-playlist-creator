from __future__ import annotations

import sys
from unittest.mock import patch

import pytest

import main as main_module
from main import main


def test_main_passes_limit_to_run() -> None:
    with (
        patch.object(sys, "argv", ["main.py", "--limit", "5"]),
        patch.object(main_module, "run") as mock_run,
    ):
        main()
    mock_run.assert_called_once_with(limit=5, dry_run=False)


def test_main_passes_none_when_limit_omitted() -> None:
    with (
        patch.object(sys, "argv", ["main.py"]),
        patch.object(main_module, "run") as mock_run,
    ):
        main()
    mock_run.assert_called_once_with(limit=None, dry_run=False)


def test_main_rejects_limit_zero() -> None:
    with (
        patch.object(sys, "argv", ["main.py", "--limit", "0"]),
        patch.object(main_module, "run") as mock_run,
    ):
        with pytest.raises(SystemExit) as exc_info:
            main()
    assert exc_info.value.code != 0
    mock_run.assert_not_called()


def test_main_rejects_negative_limit() -> None:
    with (
        patch.object(sys, "argv", ["main.py", "--limit", "-1"]),
        patch.object(main_module, "run") as mock_run,
    ):
        with pytest.raises(SystemExit) as exc_info:
            main()
    assert exc_info.value.code != 0
    mock_run.assert_not_called()


def test_main_passes_dry_run_true_when_flag_present() -> None:
    with (
        patch.object(sys, "argv", ["main.py", "--dry-run"]),
        patch.object(main_module, "run") as mock_run,
    ):
        main()
    mock_run.assert_called_once_with(limit=None, dry_run=True)


def test_main_can_combine_dry_run_and_limit() -> None:
    with (
        patch.object(sys, "argv", ["main.py", "--dry-run", "--limit", "3"]),
        patch.object(main_module, "run") as mock_run,
    ):
        main()
    mock_run.assert_called_once_with(limit=3, dry_run=True)


def test_main_rejects_invalid_limit_even_with_dry_run() -> None:
    with (
        patch.object(sys, "argv", ["main.py", "--dry-run", "--limit", "-1"]),
        patch.object(main_module, "run") as mock_run,
    ):
        with pytest.raises(SystemExit) as exc_info:
            main()
    assert exc_info.value.code != 0
    mock_run.assert_not_called()
