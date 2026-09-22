"""Headless coverage for the PySide6 custom R/check-R operator workflow."""

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

from PySide6.QtWidgets import QApplication

from src.desktop import CustomMatrixWorkflow, DesktopMainWindow
from src.desktop.custom_matrix_workflow import _CustomMatrixRequest, _ServiceWorker
from src.services import (
    build_custom_braid_word,
    build_custom_rmatrix_model,
    evaluate_custom_braid_operator,
    validate_custom_matrix,
)


IDENTITY_4 = "[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]"


def _application() -> QApplication:
    return QApplication.instance() or QApplication([])


def _configured_widget() -> CustomMatrixWorkflow:
    _application()
    widget = CustomMatrixWorkflow()
    widget.matrix_input.setPlainText(IDENTITY_4)
    widget.input_kind_combo.setCurrentIndex(2)
    widget.strand_count_spin.setValue(2)
    widget.generator_input.setText("1 -1")
    return widget


def test_main_window_switches_to_the_dedicated_custom_matrix_mode() -> None:
    _application()
    window = DesktopMainWindow()

    assert window.workflow_tabs.count() == 2
    assert window.workflow_tabs.tabText(1) == "Custom R/check-R operator"
    window.workflow_tabs.setCurrentIndex(1)
    assert window.workflow_tabs.currentWidget() is window.custom_matrix_workflow
    window.close()


def test_input_kind_must_be_selected_explicitly_and_ybe_is_raw_r_only() -> None:
    widget = _configured_widget()
    widget.input_kind_combo.setCurrentIndex(0)

    assert widget._selected_input_kind() is None
    assert widget._request_snapshot() is None
    assert "never guesses" in widget.status_label.text()

    widget.input_kind_combo.setCurrentIndex(1)
    assert widget._selected_input_kind() == "R"
    assert widget.ybe_check.isEnabled()
    widget.input_kind_combo.setCurrentIndex(2)
    assert widget._selected_input_kind() == "check-R"
    assert not widget.ybe_check.isEnabled()
    widget.close()


def test_valid_4x4_validation_and_result_rendering() -> None:
    widget = _configured_widget()
    validation = validate_custom_matrix(IDENTITY_4, input_kind="check-R", check_braid_relation=True)
    widget._service_succeeded("validate", validation)

    assert "Valid braid representation input: True" in widget.validation_output.toPlainText()
    assert "Projected operator dimension: 2^2 = 4." in widget.growth_warning.text()

    model = build_custom_rmatrix_model(IDENTITY_4, input_kind="check-R")
    result = evaluate_custom_braid_operator(model, build_custom_braid_word(2, "1 -1"))
    widget._service_succeeded("evaluate", result)

    rendered = widget.result_output.toPlainText()
    assert "Operator dimensions: (4, 4)" in rendered
    assert "no trace, Markov normalization" in rendered
    assert widget.copy_button.isEnabled()
    assert widget.export_button.isEnabled()
    widget.close()


def test_invalid_dimension_is_rendered_as_structured_validation() -> None:
    widget = _configured_widget()
    widget.local_dimension_spin.setValue(3)
    validation = validate_custom_matrix(IDENTITY_4, input_kind="check-R", local_dimension=3)
    widget._service_succeeded("validate", validation)

    rendered = widget.validation_output.toPlainText()
    assert "Valid braid representation input: False" in rendered
    assert "Local dimension consistent: False" in rendered
    widget.close()


def test_negative_generator_warns_about_invertibility_before_evaluation() -> None:
    widget = _configured_widget()
    widget.generator_input.setText("-1")

    assert "inverse check-R" in widget.status_label.text()
    widget.close()


def test_background_worker_wires_validation_through_service_facade() -> None:
    request = _CustomMatrixRequest(
        matrix_text=IDENTITY_4,
        input_kind="check-R",
        local_dimension=None,
        check_braid_relation=True,
        check_standard_r_ybe=False,
        num_strands=2,
        generator_text="1",
    )
    validation = validate_custom_matrix(IDENTITY_4, input_kind="check-R", check_braid_relation=True)
    received: list[tuple[str, object]] = []
    worker = _ServiceWorker("validate", request)
    worker.succeeded.connect(lambda operation, result: received.append((operation, result)))

    with patch("src.desktop.custom_matrix_workflow.validate_custom_matrix", return_value=validation) as service_call:
        worker.run()

    service_call.assert_called_once_with(
        IDENTITY_4,
        input_kind="check-R",
        local_dimension=None,
        check_braid_relation=True,
        check_standard_r_ybe=False,
    )
    assert received == [("validate", validation)]


def test_background_worker_reports_a_singular_negative_generator_cleanly() -> None:
    request = _CustomMatrixRequest(
        matrix_text="[[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]",
        input_kind="check-R",
        local_dimension=None,
        check_braid_relation=False,
        check_standard_r_ybe=False,
        num_strands=2,
        generator_text="-1",
    )
    received: list[tuple[str, str]] = []
    worker = _ServiceWorker("evaluate", request)
    worker.failed.connect(lambda operation, message: received.append((operation, message)))

    worker.run()

    assert received
    assert received[0][0] == "evaluate"
    assert "invertible" in received[0][1]
