"""PySide6 built-in invariant workflow using only the public service facade."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

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
    QStackedWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.services import (
    ApplicationBraidResult,
    ApplicationBranchResult,
    ApplicationCatalogExample,
    ApplicationServiceError,
    build_custom_braid_word,
    evaluate_braid_result,
    evaluate_catalog_result,
    format_application_braid_result,
    format_application_branch_result,
    list_catalog_examples,
    list_evaluation_branches,
    parse_q_text,
    serialize_application_braid_result,
)


@dataclass(frozen=True, slots=True)
class _InvariantRequest:
    """One immutable request passed from the UI to a worker thread."""

    source_mode: str
    example_label: str
    num_strands: int
    generator_text: str
    custom_label: str
    custom_notes: str
    branch_ids: tuple[str, ...]
    q_parameter: Any


class _InvariantWorker(QObject):
    """Evaluate one service request away from the Qt UI thread."""

    succeeded = Signal(object)
    failed = Signal(str)

    def __init__(self, request: _InvariantRequest) -> None:
        super().__init__()
        self._request = request

    @Slot()
    def run(self) -> None:
        try:
            if self._request.source_mode == "catalog":
                result = evaluate_catalog_result(
                    self._request.example_label,
                    branch_ids=self._request.branch_ids,
                    q=self._request.q_parameter,
                )
            else:
                braid_word = build_custom_braid_word(
                    self._request.num_strands,
                    self._request.generator_text,
                    label=self._request.custom_label or "desktop_custom_braid",
                    notes=self._request.custom_notes or "Custom braid created by the PySide6 invariant workflow.",
                )
                result = evaluate_braid_result(
                    braid_word,
                    branch_ids=self._request.branch_ids,
                    q=self._request.q_parameter,
                )
        except ApplicationServiceError as exc:
            self.failed.emit(str(exc))
        except Exception as exc:  # Surface unexpected failures separately from input errors.
            self.failed.emit(f"Unexpected evaluation failure: {exc}")
        else:
            self.succeeded.emit(result)


class InvariantCalculationWorkflow(QWidget):
    """Normal catalog/custom-braid calculation flow for maintained branches."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("invariantCalculationWorkflow")
        self._examples = list_catalog_examples()
        self._branches = list_evaluation_branches()
        self._active_jobs: list[tuple[QThread, _InvariantWorker]] = []
        self._last_result: ApplicationBraidResult | None = None
        self._build_widget()

    @property
    def examples(self) -> tuple[ApplicationCatalogExample, ...]:
        """Expose the service-owned catalog snapshots without evaluating them."""

        return self._examples

    @property
    def branches(self):
        """Expose the service-owned descriptors without duplicating status facts."""

        return self._branches

    def _build_widget(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        title = QLabel("Built-in invariant calculation")
        title.setStyleSheet("font-size: 18px; font-weight: 600;")
        layout.addWidget(title)
        oracle_note = QLabel(
            "Project-native braid conventions are used exactly as entered. Offline external-oracle coverage exists for "
            "the formal Jones/sl3 branches; the sl2 spin-1 branch remains candidate."
        )
        oracle_note.setWordWrap(True)
        oracle_note.setStyleSheet("color: #555;")
        layout.addWidget(oracle_note)

        input_group = QGroupBox("Input", self)
        input_layout = QFormLayout(input_group)
        self.source_combo = QComboBox(input_group)
        self.source_combo.setObjectName("invariantSourceMode")
        self.source_combo.addItem("Built-in example", "catalog")
        self.source_combo.addItem("Custom braid", "custom")
        self.source_combo.currentIndexChanged.connect(self._source_changed)
        input_layout.addRow("Source:", self.source_combo)

        self.source_stack = QStackedWidget(input_group)
        self.source_stack.addWidget(self._build_catalog_source())
        self.source_stack.addWidget(self._build_custom_source())
        input_layout.addRow(self.source_stack)
        layout.addWidget(input_group)

        branch_group = QGroupBox("Invariant branches", self)
        branch_layout = QVBoxLayout(branch_group)
        self._branch_checks: list[tuple[QCheckBox, Any]] = []
        for descriptor in self._branches:
            check = QCheckBox(f"{descriptor.display_name} ({descriptor.status})", branch_group)
            check.setObjectName(f"branch_{descriptor.model_id}")
            check.setChecked(True)
            check.setToolTip(descriptor.user_note)
            branch_layout.addWidget(check)
            note = QLabel(descriptor.user_note, branch_group)
            note.setWordWrap(True)
            note.setStyleSheet("margin-left: 24px; color: #555;")
            if descriptor.status == "candidate":
                note.setStyleSheet("margin-left: 24px; color: #805000;")
            branch_layout.addWidget(note)
            self._branch_checks.append((check, descriptor))
        layout.addWidget(branch_group)

        execution_group = QGroupBox("Calculation", self)
        execution_layout = QFormLayout(execution_group)
        self.q_input = QLineEdit("2", execution_group)
        self.q_input.setObjectName("invariantQInput")
        self.q_input.setPlaceholderText("2, 3/2, q, or another SymPy-compatible expression")
        execution_layout.addRow("q:", self.q_input)
        calculation_row = QWidget(execution_group)
        calculation_layout = QHBoxLayout(calculation_row)
        calculation_layout.setContentsMargins(0, 0, 0, 0)
        self.calculate_button = QPushButton("Calculate", calculation_row)
        self.calculate_button.setObjectName("calculateInvariants")
        self.calculate_button.clicked.connect(self._request_calculation)
        self.copy_selected_button = QPushButton("Copy selected text", calculation_row)
        self.copy_selected_button.setObjectName("copySelectedInvariantText")
        self.copy_selected_button.setEnabled(False)
        self.copy_selected_button.clicked.connect(self._copy_selected_text)
        self.copy_all_button = QPushButton("Copy all text", calculation_row)
        self.copy_all_button.setObjectName("copyAllInvariantText")
        self.copy_all_button.setEnabled(False)
        self.copy_all_button.clicked.connect(self._copy_all_text)
        self.copy_json_button = QPushButton("Copy JSON", calculation_row)
        self.copy_json_button.setObjectName("copyInvariantJson")
        self.copy_json_button.setEnabled(False)
        self.copy_json_button.clicked.connect(self._copy_json)
        self.export_button = QPushButton("Export…", calculation_row)
        self.export_button.setObjectName("exportInvariantResult")
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self._export_result)
        calculation_layout.addWidget(self.calculate_button)
        calculation_layout.addStretch(1)
        calculation_layout.addWidget(self.copy_selected_button)
        calculation_layout.addWidget(self.copy_all_button)
        calculation_layout.addWidget(self.copy_json_button)
        calculation_layout.addWidget(self.export_button)
        execution_layout.addRow(calculation_row)
        layout.addWidget(execution_group)

        self.status_label = QLabel("Ready. Choose an input, branches, and q; calculation runs outside the UI thread.", self)
        self.status_label.setObjectName("invariantCalculationStatus")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        self.result_tabs = QTabWidget(self)
        self.result_tabs.setObjectName("invariantResultTabs")
        self.result_tabs.currentChanged.connect(self._result_tab_changed)
        self._placeholder_result = QPlainTextEdit(self.result_tabs)
        self._placeholder_result.setReadOnly(True)
        self._placeholder_result.setPlainText("No calculation has been run.")
        self.result_tabs.addTab(self._placeholder_result, "Results")
        layout.addWidget(self.result_tabs, 1)
        self._update_catalog_preview()

    def _build_catalog_source(self) -> QWidget:
        source = QWidget(self)
        layout = QFormLayout(source)
        self.example_combo = QComboBox(source)
        self.example_combo.setObjectName("invariantCatalogExample")
        for example in self._examples:
            self.example_combo.addItem(example.label, example)
        self.example_combo.currentIndexChanged.connect(self._update_catalog_preview)
        self.example_preview = QLabel(source)
        self.example_preview.setObjectName("invariantCatalogPreview")
        self.example_preview.setWordWrap(True)
        layout.addRow("Example:", self.example_combo)
        layout.addRow("Project-native braid:", self.example_preview)
        return source

    def _build_custom_source(self) -> QWidget:
        source = QWidget(self)
        layout = QFormLayout(source)
        self.custom_strands_spin = QSpinBox(source)
        self.custom_strands_spin.setObjectName("invariantCustomStrands")
        self.custom_strands_spin.setRange(1, 12)
        self.custom_strands_spin.setValue(2)
        self.custom_generators_input = QLineEdit(source)
        self.custom_generators_input.setObjectName("invariantCustomGenerators")
        self.custom_generators_input.setPlaceholderText("Signed project Artin generators, e.g. 1 -2 1")
        self.custom_label_input = QLineEdit("custom_braid", source)
        self.custom_label_input.setObjectName("invariantCustomLabel")
        self.custom_notes_input = QLineEdit(source)
        self.custom_notes_input.setObjectName("invariantCustomNotes")
        self.custom_notes_input.setPlaceholderText("Optional note")
        convention = QLabel(
            "Positive i means project sigma_i; negative -i means its inverse. No external braid-sign conversion is applied.",
            source,
        )
        convention.setWordWrap(True)
        convention.setStyleSheet("color: #555;")
        layout.addRow("Strands:", self.custom_strands_spin)
        layout.addRow("Generators:", self.custom_generators_input)
        layout.addRow("Label:", self.custom_label_input)
        layout.addRow("Notes:", self.custom_notes_input)
        layout.addRow("Convention:", convention)
        return source

    def _source_changed(self) -> None:
        self.source_stack.setCurrentIndex(self.source_combo.currentIndex())

    def _update_catalog_preview(self) -> None:
        index = self.example_combo.currentIndex()
        if index < 0 or index >= len(self._examples):
            self.example_preview.clear()
            return
        example = self._examples[index]
        metadata = []
        if example.expected_components is not None:
            metadata.append(f"components: {example.expected_components}")
        if example.expected_crossing_count is not None:
            metadata.append(f"crossings: {example.expected_crossing_count}")
        metadata_text = "; ".join(metadata) or "no recovered component/crossing metadata"
        self.example_preview.setText(
            f"{example.word_string}\n{example.num_strands} strands; generators {list(example.generators)}\n"
            f"{metadata_text}\n{example.notes}"
        )

    def _selected_branch_ids(self) -> tuple[str, ...]:
        return tuple(descriptor.branch_id for check, descriptor in self._branch_checks if check.isChecked())

    def _request_calculation(self) -> None:
        branch_ids = self._selected_branch_ids()
        if not branch_ids:
            self._set_error("Select at least one invariant branch before calculating.")
            return
        try:
            parameter = parse_q_text(self.q_input.text())
        except ApplicationServiceError as exc:
            self._set_error(str(exc))
            return
        source_mode = str(self.source_combo.currentData())
        request = _InvariantRequest(
            source_mode=source_mode,
            example_label=self.example_combo.currentText(),
            num_strands=self.custom_strands_spin.value(),
            generator_text=self.custom_generators_input.text(),
            custom_label=self.custom_label_input.text().strip(),
            custom_notes=self.custom_notes_input.text().strip(),
            branch_ids=branch_ids,
            q_parameter=parameter,
        )
        self._start_worker(request)

    def _start_worker(self, request: _InvariantRequest) -> None:
        self._set_busy(True, "Calculation running outside the UI thread…")
        thread = QThread(self)
        worker = _InvariantWorker(request)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.succeeded.connect(self._calculation_succeeded)
        worker.failed.connect(self._calculation_failed)
        worker.succeeded.connect(lambda _result, active_thread=thread: active_thread.quit())
        worker.failed.connect(lambda _message, active_thread=thread: active_thread.quit())
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(lambda active_thread=thread, active_worker=worker: self._job_finished(active_thread, active_worker))
        self._active_jobs.append((thread, worker))
        thread.start()

    @Slot(object)
    def _calculation_succeeded(self, result: object) -> None:
        assert isinstance(result, ApplicationBraidResult)
        self._last_result = result
        self._render_result(result)
        self.copy_selected_button.setEnabled(True)
        self.copy_all_button.setEnabled(True)
        self.copy_json_button.setEnabled(True)
        self.export_button.setEnabled(True)
        self.status_label.setText("Calculation complete. Formal and candidate branch statuses are shown in the result tabs.")

    @Slot(str)
    def _calculation_failed(self, message: str) -> None:
        self._set_error(message)

    def _job_finished(self, thread: QThread, worker: _InvariantWorker) -> None:
        self._active_jobs = [job for job in self._active_jobs if job != (thread, worker)]
        self._set_busy(False)
        thread.deleteLater()

    def _set_busy(self, busy: bool, message: str | None = None) -> None:
        for control in (
            self.source_combo,
            self.example_combo,
            self.custom_strands_spin,
            self.custom_generators_input,
            self.custom_label_input,
            self.custom_notes_input,
            self.q_input,
            self.calculate_button,
        ):
            control.setEnabled(not busy)
        for check, _descriptor in self._branch_checks:
            check.setEnabled(not busy)
        if message is not None:
            self.status_label.setText(message)

    def _set_error(self, message: str) -> None:
        self.status_label.setText(f"Input or service error: {message}")

    def _clear_result_tabs(self) -> None:
        self.result_tabs.clear()

    def _render_result(self, result: ApplicationBraidResult) -> None:
        self._clear_result_tabs()
        summary = QPlainTextEdit(self.result_tabs)
        summary.setReadOnly(True)
        summary.setPlainText(format_application_braid_result(result))
        self.result_tabs.addTab(summary, "All results")
        for branch in result.branch_results:
            card = QPlainTextEdit(self.result_tabs)
            card.setReadOnly(True)
            card.setPlainText(self._format_branch_card(branch, result))
            label = f"{branch.display_name} ({branch.status})"
            self.result_tabs.addTab(card, label)

    @staticmethod
    def _format_branch_card(branch: ApplicationBranchResult, result: ApplicationBraidResult) -> str:
        status_prefix = "CANDIDATE — " if branch.status == "candidate" else ""
        lines = [
            f"{status_prefix}{branch.display_name}",
            f"Model id: {branch.model_id}",
            f"Branch id: {branch.branch_id}",
            f"Status: {branch.status}",
            f"Input: {result.example_label}; {result.num_strands} strands; generators {list(result.generators)}",
            f"Braid word: {result.word_string}",
            f"Result metadata: {result.metadata}",
            "",
            format_application_branch_result(branch),
        ]
        if branch.status == "candidate":
            lines.append("Candidate status is preserved: this output is not presented as theorem-level formal normalization.")
        return "\n".join(lines)

    def _current_result_text(self) -> str | None:
        widget = self.result_tabs.currentWidget()
        return widget.toPlainText() if isinstance(widget, QPlainTextEdit) and self._last_result is not None else None

    def _copy_selected_text(self) -> None:
        text = self._current_result_text()
        if text is None:
            return
        QGuiApplication.clipboard().setText(text)
        self.status_label.setText("Selected result text copied to the clipboard.")

    def _copy_all_text(self) -> None:
        if self._last_result is None:
            return
        QGuiApplication.clipboard().setText(format_application_braid_result(self._last_result))
        self.status_label.setText("All result text copied to the clipboard.")

    def _copy_json(self) -> None:
        if self._last_result is None:
            return
        QGuiApplication.clipboard().setText(serialize_application_braid_result(self._last_result))
        self.status_label.setText("Deterministic result JSON copied to the clipboard.")

    def _export_result(self) -> None:
        if self._last_result is None:
            return
        file_name, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export invariant result",
            "invariant_result.json",
            "JSON files (*.json);;Text files (*.txt)",
        )
        if not file_name:
            return
        content = format_application_braid_result(self._last_result) if "Text" in selected_filter else serialize_application_braid_result(self._last_result)
        try:
            Path(file_name).write_text(content, encoding="utf-8")
        except OSError as exc:
            self._set_error(f"Could not export result: {exc}")
            return
        self.status_label.setText(f"Exported result to {file_name}.")

    def _result_tab_changed(self, _index: int) -> None:
        self.copy_selected_button.setEnabled(self._last_result is not None)
