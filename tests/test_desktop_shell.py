"""Offscreen smoke coverage for the maintained PySide6 desktop shell."""

from __future__ import annotations

import os
import subprocess
import sys
from unittest.mock import patch

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

QtWidgets = pytest.importorskip("PySide6.QtWidgets", reason="PySide6 Qt runtime is unavailable")
QApplication = QtWidgets.QApplication
QCheckBox = QtWidgets.QCheckBox

from src.desktop import DesktopMainWindow
from src.desktop.__main__ import main
from src.services import list_catalog_examples, list_evaluation_branches


def _application() -> QApplication:
    return QApplication.instance() or QApplication([])


def test_desktop_window_constructs_from_service_catalogs_without_evaluation() -> None:
    _application()
    window = DesktopMainWindow()

    assert window.windowTitle() == "Calculator of Knots and Links"
    assert window.examples == list_catalog_examples()
    assert window.branches == list_evaluation_branches()
    assert window.example_combo.count() == len(window.examples)
    assert any("candidate" in selector.text() for selector in window.findChildren(QCheckBox))
    assert "evaluation will be added" in window.statusBar().currentMessage().lower()
    window.close()


def test_desktop_entrypoint_dispatches_to_launcher() -> None:
    with patch("src.desktop.__main__.launch_desktop_application", return_value=0) as launch:
        assert main(["desktop"]) == 0
    launch.assert_called_once_with(["desktop"])
