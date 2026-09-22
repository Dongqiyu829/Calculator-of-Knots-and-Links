"""Headless maintained-desktop checks for example/project setup flow."""

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


def test_loading_curated_invariant_example_populates_without_starting_worker(tmp_path) -> None:
    _application()
    window = DesktopMainWindow()
    window.invariant_workflow._start_worker = lambda *_args: pytest.fail("loading an example must not evaluate")
    window._load_curated_example(get_curated_example("knot.5_2"))
    assert window.workflow_tabs.currentWidget() is window.invariant_workflow
    assert window.invariant_workflow.source_combo.currentData() == "custom"
    assert window.invariant_workflow.custom_generators_input.text() == "1 1 1 2 -1 2"
    path = tmp_path / "saved.knotcalc.json"
    window.save_project_to_path(path)
    window.load_project_from_path(path)
    assert window.invariant_workflow.custom_generators_input.text() == "1 1 1 2 -1 2"
    window.close()


def test_loading_custom_rmatrix_example_selects_custom_tab_without_evaluation() -> None:
    _application()
    window = DesktopMainWindow()
    window.custom_matrix_workflow._start_worker = lambda *_args: pytest.fail("loading an example must not evaluate")
    window._load_curated_example(get_curated_example("rmatrix.diagonal_negative_control"))
    assert window.workflow_tabs.currentWidget() is window.custom_matrix_workflow
    assert window.custom_matrix_workflow.input_kind_combo.currentData() == "check-R"
    assert "[0,2,0,0]" in window.custom_matrix_workflow.matrix_input.toPlainText()
    window.close()
