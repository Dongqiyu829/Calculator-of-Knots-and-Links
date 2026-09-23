"""Headless checks for the maintained PySide6 invariant calculation workflow."""

from __future__ import annotations

import os
import subprocess
import sys
import time
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


def _catalog_request(example_label: str, branch_ids: tuple[str, ...], q_text: str, backend: str = "explicit") -> _InvariantRequest:
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
        backend=backend,
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
        backend="matrix_free",
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
        backend="matrix_free",
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

    assert "Primary output (Jones-compatible output): 1" in workflow.result_tabs.widget(0).toPlainText()
    assert workflow.result_mode_combo.currentData() == "compact"
    numeric_card = workflow.result_tabs.widget(1).toPlainText()
    assert "Status: formal" in numeric_card
    assert "Scalar evaluation at q = 2." in numeric_card
    assert "Standard Jones variable t" not in numeric_card

    workflow.q_input.setText("q")
    symbolic = evaluate_catalog_result("unknot_1", branch_ids=("sl2_fundamental",), q=parse_q_text("q"))
    workflow._calculation_succeeded(symbolic, _catalog_request("unknot_1", ("sl2_fundamental",), "q"))
    symbolic_card = workflow.result_tabs.widget(1).toPlainText()
    assert "Project q expression:" in symbolic_card
    assert "Standard Jones variable t" in symbolic_card
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
    assert "Status: candidate" in candidate_card
    assert "Warning:" in candidate_card
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
        backend="explicit",
    )
    expected = evaluate_catalog_result("unknot_1", branch_ids=("sl2_fundamental",), q=sp.Integer(2))
    received: list[object] = []
    worker = _InvariantWorker(request)
    worker.succeeded.connect(received.append)

    with patch("src.desktop.invariant_workflow.evaluate_catalog_result", return_value=expected) as service_call:
        worker.run()

    service_call.assert_called_once_with("unknot_1", branch_ids=("sl2_fundamental",), q=sp.Integer(2), backend="explicit")
    assert received == [expected]


def test_desktop_default_request_is_matrix_free_and_selection_is_explicit() -> None:
    workflow = _workflow()
    assert workflow.backend_combo.currentData() == "matrix_free"
    requests: list[_InvariantRequest] = []
    workflow._start_worker = requests.append
    workflow._request_calculation()
    assert requests[-1].backend == "matrix_free"
    assert set(requests[-1].branch_ids) == {"sl2_fundamental", "sl2_spin1", "sl3_fundamental"}
    workflow.backend_combo.setCurrentIndex(workflow.backend_combo.findData("explicit"))
    workflow._request_calculation()
    assert requests[-1].backend == "explicit"
    workflow.close()


@pytest.mark.parametrize("backend", ("explicit", "matrix_free", "temperley_lieb"))
@pytest.mark.parametrize("source_mode", ("catalog", "custom"))
def test_worker_passes_selected_backend_to_both_service_routes(source_mode, backend) -> None:
    request = _InvariantRequest(
        source_mode=source_mode,
        example_label="trefoil",
        num_strands=2,
        generator_text="1 1 1",
        custom_label="trefoil",
        custom_notes="",
        branch_ids=("sl2_fundamental",),
        q_parameter=sp.Integer(2),
        q_text="2",
        backend=backend,
    )
    expected = evaluate_catalog_result("trefoil", branch_ids=request.branch_ids, q=request.q_parameter, backend=backend)
    worker = _InvariantWorker(request)
    received: list[object] = []
    worker.succeeded.connect(received.append)
    if source_mode == "catalog":
        with patch("src.desktop.invariant_workflow.evaluate_catalog_result", return_value=expected) as service_call:
            worker.run()
        service_call.assert_called_once_with("trefoil", branch_ids=request.branch_ids, q=request.q_parameter, backend=backend)
    else:
        with patch("src.desktop.invariant_workflow.evaluate_braid_result", return_value=expected) as service_call:
            worker.run()
        assert service_call.call_args.kwargs == {"branch_ids": request.branch_ids, "q": request.q_parameter, "backend": backend}
        assert service_call.call_args.args[0].generators == (1, 1, 1)
    assert received == [expected]


def test_tl_eligibility_resets_visibly_and_invalid_request_is_blocked() -> None:
    workflow = _workflow()
    _sl2_only(workflow)
    tl_index = workflow.backend_combo.findData("temperley_lieb")
    assert workflow.backend_combo.model().item(tl_index).isEnabled()
    workflow.backend_combo.setCurrentIndex(tl_index)
    spin1_check = next(check for check, descriptor in workflow._branch_checks if descriptor.branch_id == "sl2_spin1")
    spin1_check.setChecked(True)
    assert workflow.backend_combo.currentData() == "matrix_free"
    assert not workflow.backend_combo.model().item(tl_index).isEnabled()
    assert "Switched to Fast scalar" in workflow.backend_hint.text()
    workflow.backend_combo.setCurrentIndex(tl_index)  # Simulate a programmatic invalid state.
    workflow._request_calculation()
    assert "temperley_lieb backend supports sl2_fundamental only" in workflow.status_label.text()
    workflow.close()


@pytest.mark.parametrize("q_text", ("2", "q"))
def test_desktop_backend_outputs_and_scalar_detailed_claims(q_text) -> None:
    workflow = _workflow()
    _sl2_only(workflow)
    q = parse_q_text(q_text)
    results = {
        backend: evaluate_catalog_result("trefoil", branch_ids=("sl2_fundamental",), q=q, backend=backend)
        for backend in ("explicit", "matrix_free", "temperley_lieb")
    }
    assert len({result.branch_results[0].primary_output for result in results.values()}) == 1
    assert results["explicit"].branch_results[0].raw_trace is not None
    for backend in ("matrix_free", "temperley_lieb"):
        assert results[backend].branch_results[0].raw_trace is None
        workflow._calculation_succeeded(results[backend], _catalog_request("trefoil", ("sl2_fundamental",), q_text, backend))
        compact = workflow.result_tabs.widget(1).toPlainText()
        assert "Primary output" in compact
        assert "Status: formal" in compact
        workflow.result_mode_combo.setCurrentIndex(workflow.result_mode_combo.findData("detailed"))
        detailed = workflow.result_tabs.widget(1).toPlainText()
        assert "Raw trace: not available" in detailed
        assert "full global operator diagnostics were not computed" in detailed
        assert "Reference / diagnostics" in detailed
        assert backend == workflow._last_backend
    workflow._calculation_succeeded(results["explicit"], _catalog_request("trefoil", ("sl2_fundamental",), q_text, "explicit"))
    reference_detail = workflow.result_tabs.widget(1).toPlainText()
    assert "Computation backend: Reference / diagnostics" in reference_detail
    assert "Raw trace: not available" not in reference_detail
    workflow.close()


def test_matrix_free_worker_serves_all_branches_without_global_builder(monkeypatch) -> None:
    from src.invariants import branch_registry

    def forbidden(*_args, **_kwargs):
        raise AssertionError("Desktop fast scalar path constructed a global braid operator")

    monkeypatch.setattr(branch_registry, "BraidOperatorBuilder", forbidden)
    request = _catalog_request("unknot_1", ("sl2_fundamental", "sl2_spin1", "sl3_fundamental"), "2", "matrix_free")
    received: list[object] = []
    worker = _InvariantWorker(request)
    worker.succeeded.connect(received.append)
    worker.run()
    assert len(received) == 1
    assert {branch.metadata["evaluation_backend"] for branch in received[0].branch_results} == {"matrix_free"}


def test_worker_reports_backend_incompatibility_as_a_service_error() -> None:
    request = _catalog_request("trefoil", ("sl2_fundamental", "sl3_fundamental"), "2", "temperley_lieb")
    failures: list[str] = []
    worker = _InvariantWorker(request)
    worker.failed.connect(failures.append)
    worker.run()
    assert len(failures) == 1
    assert "supports sl2_fundamental only" in failures[0]
    assert not failures[0].startswith("Unexpected evaluation failure")


def test_default_calculation_still_runs_on_a_qt_worker_thread() -> None:
    workflow = _workflow()
    _sl2_only(workflow)
    workflow._request_calculation()
    assert workflow._active_jobs
    thread, worker = workflow._active_jobs[0]
    assert worker.thread() is thread
    assert thread is not QApplication.instance().thread()
    deadline = time.monotonic() + 15
    while workflow._active_jobs and time.monotonic() < deadline:
        QApplication.processEvents()
        time.sleep(0.01)
    assert not workflow._active_jobs
    assert workflow._last_result is not None
    assert workflow._last_result.branch_results[0].metadata["evaluation_backend"] == "matrix_free"
    workflow.close()


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
