"""Headless checks for the maintained PySide6 invariant calculation workflow."""

from __future__ import annotations

import os
import subprocess
import sys
from unittest.mock import patch

import pytest
import sympy as sp

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

from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

from src.desktop import InvariantCalculationWorkflow
from src.desktop.invariant_workflow import _InvariantRequest, _InvariantWorker
from src.services import evaluate_catalog_result, parse_q_text


def _application() -> QApplication:
    return QApplication.instance() or QApplication([])


def _workflow() -> InvariantCalculationWorkflow:
    _application()
    workflow = InvariantCalculationWorkflow()
    workflow.q_input.setText("2")
    return workflow


def _sl2_only(workflow: InvariantCalculationWorkflow) -> None:
    for check, descriptor in workflow._branch_checks:
        check.setChecked(descriptor.branch_id == "sl2_fundamental")


def _catalog_request(example_label: str, branch_ids: tuple[str, ...], q_text: str) -> _InvariantRequest:
    return _InvariantRequest(
        source_mode="catalog",
        example_label=example_label,
        num_strands=1,
        generator_text="",
        custom_label="",
        custom_notes="",
        branch_ids=branch_ids,
        q_parameter=parse_q_text(q_text),
        q_text=q_text,
    )


def test_catalog_selection_shows_project_native_braid_metadata() -> None:
    workflow = _workflow()
    index = workflow.example_combo.findText("trefoil")
    workflow.example_combo.setCurrentIndex(index)

    preview = workflow.example_preview.text()
    assert "sigma_1 sigma_1 sigma_1" in preview
    assert "2 strands; generators [1, 1, 1]" in preview
    workflow.close()


def test_custom_braid_source_uses_service_validation_worker() -> None:
    request = _InvariantRequest(
        source_mode="custom",
        example_label="",
        num_strands=1,
        generator_text="1",
        custom_label="bad_one_strand",
        custom_notes="",
        branch_ids=("sl2_fundamental",),
        q_parameter=sp.Integer(2),
        q_text="2",
    )
    received: list[str] = []
    worker = _InvariantWorker(request)
    worker.failed.connect(received.append)

    worker.run()

    assert received
    assert "1-strand braid can only be the identity" in received[0]


def test_valid_custom_braid_evaluates_through_the_service_worker() -> None:
    request = _InvariantRequest(
        source_mode="custom",
        example_label="",
        num_strands=2,
        generator_text="1",
        custom_label="custom_unknot",
        custom_notes="service-only custom input",
        branch_ids=("sl2_fundamental",),
        q_parameter=sp.Integer(2),
        q_text="2",
    )
    received: list[object] = []
    worker = _InvariantWorker(request)
    worker.succeeded.connect(received.append)

    worker.run()

    assert len(received) == 1
    assert received[0].source_mode == "custom"
    assert received[0].generators == (1,)


def test_branch_descriptors_and_candidate_status_come_from_service_data() -> None:
    workflow = _workflow()

    labels = [check.text() for check, _descriptor in workflow._branch_checks]
    descriptors = workflow.branches
    assert [descriptor.branch_id for _check, descriptor in workflow._branch_checks] == [
        descriptor.branch_id for descriptor in descriptors
    ]
    assert any("candidate" in label for label in labels)
    candidate_check = next(check for check, descriptor in workflow._branch_checks if descriptor.branch_id == "sl2_spin1")
    candidate_check.click()
    assert "Knot Atlas" in workflow.branch_details.toPlainText()
    workflow.close()


def test_q_2_and_symbolic_q_results_render_through_application_dtos() -> None:
    workflow = _workflow()
    _sl2_only(workflow)
    numeric = evaluate_catalog_result("unknot_1", branch_ids=("sl2_fundamental",), q=parse_q_text("2"))
    workflow._calculation_succeeded(numeric, _catalog_request("unknot_1", ("sl2_fundamental",), "2"))

    assert "Primary output: 1" in workflow.result_tabs.widget(0).toPlainText()
    assert workflow.result_mode_combo.currentData() == "compact"
    assert "Status: formal" in workflow.result_tabs.widget(1).toPlainText()
    assert "Standard Jones variable t" in workflow.result_tabs.widget(1).toPlainText()

    workflow.q_input.setText("q")
    symbolic = evaluate_catalog_result("unknot_1", branch_ids=("sl2_fundamental",), q=parse_q_text("q"))
    workflow._calculation_succeeded(symbolic, _catalog_request("unknot_1", ("sl2_fundamental",), "q"))
    assert "Project q expression:" in workflow.result_tabs.widget(1).toPlainText()
    workflow.close()


def test_multiple_branch_result_cards_preserve_candidate_status() -> None:
    workflow = _workflow()
    result = evaluate_catalog_result(
        "unknot_1",
        branch_ids=("sl2_fundamental", "sl2_spin1"),
        q=sp.Integer(2),
    )
    workflow._calculation_succeeded(result, _catalog_request("unknot_1", ("sl2_fundamental", "sl2_spin1"), "2"))

    assert workflow.result_tabs.count() == 3
    candidate_card = workflow.result_tabs.widget(2).toPlainText()
    assert "CANDIDATE" in candidate_card
    assert "not presented as theorem-level formal normalization" in candidate_card
    workflow.close()


def test_worker_calls_catalog_result_service_facade() -> None:
    request = _InvariantRequest(
        source_mode="catalog",
        example_label="unknot_1",
        num_strands=1,
        generator_text="",
        custom_label="",
        custom_notes="",
        branch_ids=("sl2_fundamental",),
        q_parameter=sp.Integer(2),
        q_text="2",
    )
    expected = evaluate_catalog_result("unknot_1", branch_ids=("sl2_fundamental",), q=sp.Integer(2))
    received: list[object] = []
    worker = _InvariantWorker(request)
    worker.succeeded.connect(received.append)

    with patch("src.desktop.invariant_workflow.evaluate_catalog_result", return_value=expected) as service_call:
        worker.run()

    service_call.assert_called_once_with("unknot_1", branch_ids=("sl2_fundamental",), q=sp.Integer(2))
    assert received == [expected]


def test_copy_text_json_and_export_use_service_reporting_serialization(tmp_path) -> None:
    workflow = _workflow()
    result = evaluate_catalog_result("unknot_1", branch_ids=("sl2_fundamental",), q=sp.Integer(2))
    workflow._calculation_succeeded(result, _catalog_request("unknot_1", ("sl2_fundamental",), "2"))
    workflow.result_mode_combo.setCurrentIndex(workflow.result_mode_combo.findData("compact"))

    workflow._copy_all_text()
    assert "########## unknot_1 ##########" in QGuiApplication.clipboard().text()
    workflow._copy_json()
    assert '"source_mode": "catalog"' in QGuiApplication.clipboard().text()
    export_path = tmp_path / "invariant_result.json"
    with patch(
        "src.desktop.invariant_workflow.QFileDialog.getSaveFileName",
        return_value=(str(export_path), "JSON files (*.json)"),
    ):
        workflow._export_result()
    assert '"source_mode": "catalog"' in export_path.read_text(encoding="utf-8")
    workflow.close()


def test_result_mode_switch_uses_cached_result_without_recalculation() -> None:
    workflow = _workflow()
    workflow.q_input.setText("q")
    result = evaluate_catalog_result("trefoil", branch_ids=("sl2_fundamental",), q=parse_q_text("q"))
    workflow._calculation_succeeded(result, _catalog_request("trefoil", ("sl2_fundamental",), "q"))
    assert workflow._last_result is result
    compact_text = workflow.result_tabs.widget(1).toPlainText()
    assert "Standard Jones variable t" in compact_text

    with patch("src.desktop.invariant_workflow.evaluate_catalog_result") as catalog_evaluation:
        with patch("src.desktop.invariant_workflow.evaluate_braid_result") as braid_evaluation:
            workflow.result_mode_combo.setCurrentIndex(workflow.result_mode_combo.findData("detailed"))

    assert not catalog_evaluation.called
    assert not braid_evaluation.called
    detailed_text = workflow.result_tabs.widget(1).toPlainText()
    assert "Model id:" in detailed_text
    assert workflow._last_result is result
    workflow.close()


def test_invalid_q_and_empty_branch_selection_are_user_visible() -> None:
    workflow = _workflow()
    workflow.q_input.setText("[")
    workflow._request_calculation()
    assert "q must" in workflow.status_label.text()

    workflow.q_input.setText("2")
    for check, _descriptor in workflow._branch_checks:
        check.setChecked(False)
    workflow._request_calculation()
    assert "Select at least one" in workflow.status_label.text()
    workflow.close()


def test_startup_does_not_evaluate_invariants() -> None:
    _application()
    with patch("src.desktop.invariant_workflow.evaluate_catalog_result") as catalog_evaluation:
        with patch("src.desktop.invariant_workflow.evaluate_braid_result") as braid_evaluation:
            workflow = InvariantCalculationWorkflow()
    catalog_evaluation.assert_not_called()
    braid_evaluation.assert_not_called()
    workflow.close()
