"""Offscreen behavior checks for the invariant workflow's resizable pages."""

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

from PySide6.QtWidgets import QApplication, QScrollArea, QSplitter

from src.desktop import DesktopMainWindow, InvariantCalculationWorkflow
from src.services import get_curated_example


def _application() -> QApplication:
    return QApplication.instance() or QApplication([])


def test_setup_page_exposes_manual_mode_and_large_preview_without_evaluation() -> None:
    _application()
    workflow = InvariantCalculationWorkflow()
    workflow.resize(960, 660)
    workflow.show()
    QApplication.processEvents()

    assert workflow.page_tabs.count() == 2
    assert workflow.page_tabs.tabText(0) == "Braid setup / preview"
    assert workflow.page_tabs.tabText(1) == "Calculation / results"
    assert workflow.page_tabs.currentWidget() is workflow.setup_page
    assert isinstance(workflow.setup_splitter, QSplitter)
    assert workflow.braid_preview.minimumHeight() >= 380
    assert workflow.braid_preview.height() >= 380
    assert workflow.source_combo.itemText(1) == "Manual braid input"
    workflow.source_combo.setCurrentIndex(1)
    workflow.custom_generators_input.setText("1 -2 1")
    workflow.custom_strands_spin.setValue(3)
    assert workflow.source_stack.currentIndex() == 1
    assert workflow.braid_preview.geometry is not None
    assert workflow.braid_preview.geometry.generators == (1, -2, 1)
    assert workflow._last_result is None
    workflow.close()


def test_calculation_page_has_scrollable_branches_and_independent_details() -> None:
    _application()
    workflow = InvariantCalculationWorkflow()
    workflow.page_tabs.setCurrentWidget(workflow.calculation_page)
    assert isinstance(workflow.calculation_splitter, QSplitter)
    assert isinstance(workflow.findChild(QScrollArea, "invariantBranchScroll"), QScrollArea)
    assert workflow.branch_details.isReadOnly()
    candidate_check = next(check for check, descriptor in workflow._branch_checks if descriptor.branch_id == "sl2_spin1")
    candidate_check.click()
    assert "candidate" in workflow.branch_details.toPlainText().lower()
    assert "Knot Atlas" in workflow.branch_details.toPlainText()
    assert workflow._last_result is None
    workflow.close()


def test_side_panels_share_one_dock_area_and_project_load_returns_to_setup(tmp_path) -> None:
    _application()
    window = DesktopMainWindow()
    window.show()
    QApplication.processEvents()
    assert not window.example_browser_dock.isVisible()
    assert not window.explanation_panel_dock.isVisible()
    window.example_browser_dock.show()
    window.explanation_panel_dock.show()
    QApplication.processEvents()
    assert window.example_browser_dock in window.tabifiedDockWidgets(window.explanation_panel_dock)
    window.example_browser_dock.raise_()
    QApplication.processEvents()
    assert window.example_browser_dock.isVisible()
    assert window.invariant_workflow.braid_preview.height() >= 380

    workflow = window.invariant_workflow
    workflow.page_tabs.setCurrentWidget(workflow.calculation_page)
    window._load_curated_example(get_curated_example("catalog.trefoil"))
    assert workflow.page_tabs.currentWidget() is workflow.setup_page
    path = tmp_path / "braid.knotcalc.json"
    window.save_project_to_path(path)
    workflow.page_tabs.setCurrentWidget(workflow.calculation_page)
    window.load_project_from_path(path)
    assert workflow.page_tabs.currentWidget() is workflow.setup_page
    window.close()
