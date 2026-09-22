"""Headless checks for explanation updates and unified export affordances."""

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

from PySide6.QtWidgets import QApplication

from src.desktop import DesktopMainWindow
from src.services import get_curated_example


def _application() -> QApplication:
    return QApplication.instance() or QApplication([])


def test_explanation_panel_updates_without_evaluation() -> None:
    _application()
    window = DesktopMainWindow()
    window.invariant_workflow._start_worker = lambda *_args: pytest.fail("explanation updates must not evaluate")
    window._load_curated_example(get_curated_example("candidate.trefoil_spin1"))
    assert window.explanation_panel.explanation is not None
    assert any(status == "candidate" for _branch, status in window.explanation_panel.explanation.branch_statuses)
    assert "candidate" in window.explanation_panel.viewer.toPlainText().lower()
    window.close()


def test_unified_export_actions_enable_only_applicable_outputs() -> None:
    _application()
    window = DesktopMainWindow()
    # Loading an example gives a braid diagram but no result.
    assert not window.export_text_action.isEnabled()
    assert not window.export_json_action.isEnabled()
    assert window.export_svg_action.isEnabled()
    assert window.export_png_action.isEnabled()

    window.invariant_workflow._last_result = object()
    window._update_export_actions()
    assert window.export_text_action.isEnabled()
    assert window.export_json_action.isEnabled()

    window.workflow_tabs.setCurrentWidget(window.custom_matrix_workflow)
    window.custom_matrix_workflow._last_result = object()
    window._update_export_actions()
    assert not window.export_text_action.isEnabled()
    assert window.export_json_action.isEnabled()
    window.close()
