"""PySide6 workflow for the supported custom R/check-R service API.

The widget deliberately constructs braid operators only.  It never reaches into
the mathematical implementation or adds a trace, framing, or invariant layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from src.services import (
    ApplicationCustomBraidOperatorResult,
    ApplicationCustomMatrixValidation,
    ApplicationServiceError,
    build_custom_braid_input,
    build_custom_braid_word,
    build_custom_rmatrix_model,
    evaluate_custom_braid_operator,
    parse_generator_text,
    serialize_custom_braid_operator_result,
    validate_custom_matrix,
)

from .braid_preview import BraidPreviewWidget


@dataclass(frozen=True, slots=True)
class _CustomMatrixRequest:
    """Immutable UI snapshot consumed by one background service operation."""

    matrix_text: str
    input_kind: str
    local_dimension: int | None
    check_braid_relation: bool
    check_standard_r_ybe: bool
    num_strands: int
    generator_text: str


class _ServiceWorker(QObject):
    """Run one supported application-service request away from the UI thread."""

    succeeded = Signal(str, object)
    failed = Signal(str, str)

    def __init__(self, operation: str, request: _CustomMatrixRequest) -> None:
        super().__init__()
        self._operation = operation
        self._request = request

    @Slot()
    def run(self) -> None:
        try:
            if self._operation == "validate":
                result = validate_custom_matrix(
                    self._request.matrix_text,
                    input_kind=self._request.input_kind,
                    local_dimension=self._request.local_dimension,
                    check_braid_relation=self._request.check_braid_relation,
                    check_standard_r_ybe=self._request.check_standard_r_ybe,
                )
            elif self._operation == "evaluate":
                model = build_custom_rmatrix_model(
                    self._request.matrix_text,
                    input_kind=self._request.input_kind,
                    local_dimension=self._request.local_dimension,
                    check_braid_relation=self._request.check_braid_relation,
                    check_standard_r_ybe=self._request.check_standard_r_ybe,
                )
                braid_word = build_custom_braid_word(
                    self._request.num_strands,
                    self._request.generator_text,
                    label="desktop_custom_braid",
                    notes="Custom braid created by the PySide6 custom R/check-R workflow.",
                )
                result = evaluate_custom_braid_operator(model, braid_word)
            else:  # pragma: no cover - only internal callers supply operations.
                raise RuntimeError(f"Unknown custom-matrix operation '{self._operation}'.")
        except (ApplicationServiceError, ValueError) as exc:
            self.failed.emit(self._operation, str(exc))
        except Exception as exc:  # Keep unexpected worker failures visible to the UI.
            self.failed.emit(self._operation, f"Unexpected service failure: {exc}")
        else:
            self.succeeded.emit(self._operation, result)


class CustomMatrixWorkflow(QWidget):
    """Explicit R/check-R input, validation, and braid-operator workflow."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("customMatrixWorkflow")
        self._active_jobs: list[tuple[QThread, _ServiceWorker]] = []
        self._last_validation: ApplicationCustomMatrixValidation | None = None
        self._last_result: ApplicationCustomBraidOperatorResult | None = None
        self._build_widget()

    def _build_widget(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        boundary = QLabel(
            "Custom matrices build a braid-group operator only. They are not a knot/link invariant recipe: "
            "no quantum trace, Markov normalization, framing correction, or polynomial normalization is added."
        )
        boundary.setObjectName("customMatrixBoundaryNotice")
        boundary.setWordWrap(True)
        boundary.setStyleSheet("padding: 8px; background: #fff4d6; color: #5b4300;")
        layout.addWidget(boundary)

        input_group = QGroupBox("Custom local matrix", self)
        input_layout = QFormLayout(input_group)
        self.matrix_input = QPlainTextEdit(input_group)
        self.matrix_input.setObjectName("customMatrixInput")
        self.matrix_input.setPlaceholderText("Example: [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]")
        self.matrix_input.setMinimumHeight(120)
        input_layout.addRow("Matrix text:", self.matrix_input)

        matrix_file_row = QWidget(input_group)
        matrix_file_layout = QHBoxLayout(matrix_file_row)
        matrix_file_layout.setContentsMargins(0, 0, 0, 0)
        self.load_matrix_button = QPushButton("Load text/JSON…", matrix_file_row)
        self.load_matrix_button.clicked.connect(self._load_matrix_file)
        matrix_file_layout.addWidget(self.load_matrix_button)
        matrix_file_layout.addStretch(1)
        input_layout.addRow("File:", matrix_file_row)

        self.input_kind_combo = QComboBox(input_group)
        self.input_kind_combo.setObjectName("customMatrixInputKind")
        self.input_kind_combo.addItem("Select explicitly…", None)
        self.input_kind_combo.addItem("R (raw R-matrix)", "R")
        self.input_kind_combo.addItem("check-R (braid generator)", "check-R")
        self.input_kind_combo.currentIndexChanged.connect(self._input_kind_changed)
        input_layout.addRow("Input kind:", self.input_kind_combo)

        self.local_dimension_spin = QSpinBox(input_group)
        self.local_dimension_spin.setObjectName("customLocalDimension")
        self.local_dimension_spin.setRange(0, 64)
        self.local_dimension_spin.setSpecialValueText("Auto infer")
        self.local_dimension_spin.setToolTip("0 asks the service to infer a local dimension from the square matrix size.")
        input_layout.addRow("Local dimension:", self.local_dimension_spin)

        self.braid_relation_check = QCheckBox("Check check-R braid relation", input_group)
        self.ybe_check = QCheckBox("Check standard raw-R YBE (R input only)", input_group)
        input_layout.addRow("Optional checks:", self.braid_relation_check)
        input_layout.addRow("", self.ybe_check)
        layout.addWidget(input_group)

        braid_group = QGroupBox("Braid operator", self)
        braid_layout = QFormLayout(braid_group)
        self.strand_count_spin = QSpinBox(braid_group)
        self.strand_count_spin.setObjectName("customBraidStrandCount")
        self.strand_count_spin.setRange(1, 12)
        self.strand_count_spin.setValue(2)
        self.strand_count_spin.valueChanged.connect(self._update_growth_warning)
        braid_layout.addRow("Strands:", self.strand_count_spin)
        self.generator_input = QLineEdit(braid_group)
        self.generator_input.setObjectName("customBraidGenerators")
        self.generator_input.setPlaceholderText("Signed generators, e.g. 1 -2 1")
        self.generator_input.textChanged.connect(self._update_negative_generator_warning)
        self.strand_count_spin.valueChanged.connect(self._update_braid_preview)
        self.generator_input.textChanged.connect(self._update_braid_preview)
        braid_layout.addRow("Generators:", self.generator_input)
        self.growth_warning = QLabel(braid_group)
        self.growth_warning.setObjectName("customDimensionWarning")
        self.growth_warning.setWordWrap(True)
        braid_layout.addRow("Growth:", self.growth_warning)
        layout.addWidget(braid_group)

        preview_group = QGroupBox("Braid diagram", self)
        preview_layout = QVBoxLayout(preview_group)
        self.braid_preview = BraidPreviewWidget(preview_group)
        self.braid_preview.setMinimumHeight(285)
        preview_layout.addWidget(self.braid_preview)
        layout.addWidget(preview_group)

        buttons = QWidget(self)
        buttons_layout = QHBoxLayout(buttons)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.validate_button = QPushButton("Validate matrix", buttons)
        self.validate_button.setObjectName("validateCustomMatrix")
        self.validate_button.clicked.connect(self._request_validation)
        self.evaluate_button = QPushButton("Compute braid operator", buttons)
        self.evaluate_button.setObjectName("evaluateCustomBraid")
        self.evaluate_button.clicked.connect(self._request_evaluation)
        self.copy_button = QPushButton("Copy JSON", buttons)
        self.copy_button.setObjectName("copyCustomResult")
        self.copy_button.setEnabled(False)
        self.copy_button.clicked.connect(self._copy_result)
        self.export_button = QPushButton("Export JSON…", buttons)
        self.export_button.setObjectName("exportCustomResult")
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self._export_result)
        buttons_layout.addWidget(self.validate_button)
        buttons_layout.addWidget(self.evaluate_button)
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.copy_button)
        buttons_layout.addWidget(self.export_button)
        layout.addWidget(buttons)

        self.status_label = QLabel("Choose R or check-R explicitly before validating.", self)
        self.status_label.setObjectName("customMatrixStatus")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        self.validation_output = QPlainTextEdit(self)
        self.validation_output.setObjectName("customValidationOutput")
        self.validation_output.setReadOnly(True)
        self.validation_output.setPlaceholderText("Structured validation status will appear here.")
        self.validation_output.setMaximumBlockCount(1000)
        layout.addWidget(self.validation_output)

        self.result_output = QPlainTextEdit(self)
        self.result_output.setObjectName("customOperatorOutput")
        self.result_output.setReadOnly(True)
        self.result_output.setPlaceholderText("Operator dimensions, matrix, diagnostics, and warnings will appear here.")
        layout.addWidget(self.result_output, 1)
        self._input_kind_changed()
        self._update_growth_warning()
        self._update_braid_preview()

    def _selected_input_kind(self) -> str | None:
        value = self.input_kind_combo.currentData()
        return value if value in {"R", "check-R"} else None

    def _request_snapshot(self) -> _CustomMatrixRequest | None:
        input_kind = self._selected_input_kind()
        if input_kind is None:
            self._set_error("Choose R or check-R explicitly; the application never guesses the convention.")
            return None
        return _CustomMatrixRequest(
            matrix_text=self.matrix_input.toPlainText(),
            input_kind=input_kind,
            local_dimension=self.local_dimension_spin.value() or None,
            check_braid_relation=self.braid_relation_check.isChecked(),
            check_standard_r_ybe=self.ybe_check.isChecked(),
            num_strands=self.strand_count_spin.value(),
            generator_text=self.generator_input.text(),
        )

    def _input_kind_changed(self) -> None:
        raw_r_selected = self._selected_input_kind() == "R"
        self.ybe_check.setEnabled(raw_r_selected)
        if not raw_r_selected:
            self.ybe_check.setChecked(False)

    def _request_validation(self) -> None:
        request = self._request_snapshot()
        if request is not None:
            self._start_worker("validate", request)

    def _request_evaluation(self) -> None:
        request = self._request_snapshot()
        if request is None:
            return
        try:
            generators = parse_generator_text(request.generator_text)
        except ApplicationServiceError as exc:
            self._set_error(str(exc))
            return
        if any(generator < 0 for generator in generators):
            self.status_label.setText(
                "Negative generator requested. The service requires an invertible check-R and will report a clean error "
                "for a singular local operator."
            )
        self._start_worker("evaluate", request)

    def _start_worker(self, operation: str, request: _CustomMatrixRequest) -> None:
        self._set_busy(True, f"{operation.capitalize()} request running outside the UI thread…")
        thread = QThread(self)
        worker = _ServiceWorker(operation, request)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.succeeded.connect(self._service_succeeded)
        worker.failed.connect(self._service_failed)
        worker.succeeded.connect(lambda *_args, active_thread=thread: active_thread.quit())
        worker.failed.connect(lambda *_args, active_thread=thread: active_thread.quit())
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(lambda active_thread=thread, active_worker=worker: self._job_finished(active_thread, active_worker))
        self._active_jobs.append((thread, worker))
        thread.start()

    @Slot(str, object)
    def _service_succeeded(self, operation: str, result: object) -> None:
        if operation == "validate":
            assert isinstance(result, ApplicationCustomMatrixValidation)
            self._last_validation = result
            self.validation_output.setPlainText(self._format_validation(result))
            self._update_growth_warning()
            self.status_label.setText(self._validation_completion_message(result))
        else:
            assert isinstance(result, ApplicationCustomBraidOperatorResult)
            self._last_result = result
            self.result_output.setPlainText(self._format_operator_result(result))
            self.validation_output.setPlainText(self._format_validation(result.validation))
            self.copy_button.setEnabled(True)
            self.export_button.setEnabled(True)
            self.status_label.setText("Braid operator computed. This result is not a knot/link invariant recipe.")
            self._update_growth_warning()

    @Slot(str, str)
    def _service_failed(self, operation: str, message: str) -> None:
        self._set_error(f"{operation.capitalize()} failed: {message}")

    def _job_finished(self, thread: QThread, worker: _ServiceWorker) -> None:
        self._active_jobs = [job for job in self._active_jobs if job != (thread, worker)]
        self._set_busy(False)
        thread.deleteLater()

    def _set_busy(self, busy: bool, message: str | None = None) -> None:
        self.validate_button.setEnabled(not busy)
        self.evaluate_button.setEnabled(not busy)
        self.load_matrix_button.setEnabled(not busy)
        if message is not None:
            self.status_label.setText(message)

    def _set_error(self, message: str) -> None:
        self.status_label.setText(message)
        self.validation_output.setPlainText(message)

    def _update_negative_generator_warning(self) -> None:
        try:
            has_negative = any(generator < 0 for generator in parse_generator_text(self.generator_input.text()))
        except ApplicationServiceError:
            return
        if has_negative:
            self.status_label.setText(
                "Negative generators use the inverse check-R. Validate invertibility before computing this word."
            )

    def _update_growth_warning(self) -> None:
        dimension = None
        if self._last_validation:
            dimension = self._last_validation.inferred_local_dimension or self._last_validation.requested_local_dimension
        if dimension is None:
            dimension = self.local_dimension_spin.value() or None
        if dimension is None:
            self.growth_warning.setText("Validate the matrix to infer local dimension and estimate tensor growth.")
            return
        total_dimension = dimension ** self.strand_count_spin.value()
        text = f"Projected operator dimension: {dimension}^{self.strand_count_spin.value()} = {total_dimension}."
        if total_dimension > 1024:
            text += " Warning: the service flags operators above dimension 1024 as potentially expensive."
        self.growth_warning.setText(text)

    def _update_braid_preview(self) -> None:
        """Render only the validated service braid input, independently of matrix work."""

        try:
            braid_input = build_custom_braid_input(self.strand_count_spin.value(), self.generator_input.text())
        except ApplicationServiceError as exc:
            self.braid_preview.set_message(f"Preview unavailable: {exc}")
            return
        self.braid_preview.set_braid_word(braid_input.braid_word)

    @staticmethod
    def _format_validation(validation: ApplicationCustomMatrixValidation) -> str:
        lines = [
            f"Input kind: {validation.input_kind}",
            f"Matrix shape: {validation.matrix_shape}",
            f"Square: {validation.square}",
            f"Inferred local dimension: {validation.inferred_local_dimension}",
            f"Requested local dimension: {validation.requested_local_dimension}",
            f"Local dimension consistent: {validation.local_dimension_consistent}",
            f"Matrix input is structurally valid: {validation.is_structurally_valid}",
            f"Invertibility: {validation.invertible}",
            f"check-R braid relation: {validation.check_r_braid_relation_status}",
            f"Standard raw-R YBE: {validation.standard_r_ybe_status}",
            f"Braid-representation status: {validation.braid_representation_status}",
        ]
        if validation.braid_representation_status == "not_checked":
            lines.append("Braid-representation relation has not been verified.")
        elif validation.braid_representation_status == "failed":
            lines.append("Braid relation failed; this matrix is not a validated braid-group representation.")
        elif validation.braid_representation_status == "undecidable":
            lines.append("Braid-representation relation could not be decided from the requested symbolic check.")
        if validation.errors:
            lines.extend(["Errors:", *[f"- {error}" for error in validation.errors]])
        if validation.warnings:
            lines.extend(["Warnings:", *[f"- {warning}" for warning in validation.warnings]])
        return "\n".join(lines)

    @staticmethod
    def _validation_completion_message(validation: ApplicationCustomMatrixValidation) -> str:
        if not validation.is_structurally_valid:
            return "Validation complete: matrix input has structural errors."
        if validation.braid_representation_status == "verified":
            return "Validation complete: matrix input is structurally valid and the check-R braid relation is verified."
        if validation.braid_representation_status == "failed":
            return "Validation complete: matrix input is structurally valid, but the check-R braid relation failed."
        if validation.braid_representation_status == "undecidable":
            return "Validation complete: matrix input is structurally valid, but the requested braid relation is undecidable."
        return "Validation complete: matrix input is structurally valid; the check-R braid relation was not checked."

    @staticmethod
    def _format_operator_result(result: ApplicationCustomBraidOperatorResult) -> str:
        lines = [
            f"Input kind: {result.input_kind}",
            f"Local dimension: {result.local_dimension}",
            f"Braid: {result.braid_label}; {result.braid_strand_count} strands; generators {list(result.braid_generators)}",
            f"Operator dimensions: {result.operator_dimensions}",
            f"Braid-representation status: {result.validation.braid_representation_status}",
            "Operator matrix:",
            result.operator_text,
            "Generator diagnostics:",
            *[str(diagnostic) for diagnostic in result.ordered_generator_diagnostics],
            "Boundary: no trace, Markov normalization, framing correction, or invariant claim.",
        ]
        if result.validation.braid_representation_status == "not_checked":
            lines.append("This is a constructed local operator; its braid-representation relation has not been verified.")
        elif result.validation.braid_representation_status == "failed":
            lines.append("This operator was constructed, but its requested braid relation failed validation.")
        if result.warnings:
            lines.extend(["Warnings:", *[f"- {warning}" for warning in result.warnings]])
        return "\n".join(lines)

    def _serialized_result(self) -> str | None:
        return None if self._last_result is None else serialize_custom_braid_operator_result(self._last_result)

    def _copy_result(self) -> None:
        serialized = self._serialized_result()
        if serialized is None:
            return
        QGuiApplication.clipboard().setText(serialized)
        self.status_label.setText("Custom operator JSON copied to the clipboard.")

    def _export_result(self) -> None:
        serialized = self._serialized_result()
        if serialized is None:
            return
        file_name, _selected_filter = QFileDialog.getSaveFileName(self, "Export custom operator JSON", "custom_braid_operator.json", "JSON files (*.json)")
        if not file_name:
            return
        try:
            Path(file_name).write_text(serialized, encoding="utf-8")
        except OSError as exc:
            self._set_error(f"Could not export result: {exc}")
            return
        self.status_label.setText(f"Exported custom operator JSON to {file_name}.")

    def _load_matrix_file(self) -> None:
        file_name, _selected_filter = QFileDialog.getOpenFileName(
            self,
            "Load custom matrix text",
            "",
            "Text or JSON files (*.txt *.json);;All files (*)",
        )
        if not file_name:
            return
        try:
            self.matrix_input.setPlainText(Path(file_name).read_text(encoding="utf-8"))
            self.status_label.setText(f"Loaded matrix text from {file_name}. Choose R or check-R explicitly before validating.")
        except OSError as exc:
            self._set_error(f"Could not load matrix text: {exc}")
