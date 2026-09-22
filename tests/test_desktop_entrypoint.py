"""Smoke coverage for the maintained desktop entry point."""

from __future__ import annotations

import os
import subprocess
import sys

import pytest


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

_qt_import = subprocess.run(
    [sys.executable, "-c", "from PySide6.QtWidgets import QApplication"],
    env=os.environ,
    capture_output=True,
    text=True,
    check=False,
)
if _qt_import.returncode != 0:
    pytest.skip("PySide6 Qt runtime is unavailable", allow_module_level=True)


def test_desktop_smoke_flag_constructs_without_event_loop() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "src.desktop", "--smoke-test"],
        env=os.environ,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout
