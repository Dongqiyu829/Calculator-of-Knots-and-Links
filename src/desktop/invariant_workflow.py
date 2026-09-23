"""PySide6 built-in invariant workflow using only the public service facade."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, QThread, Qt, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.services import (
    ApplicationBraidResult,
    ApplicationBranchResult,
    ApplicationCatalogExample,
    ApplicationProjectDocument,
    ApplicationServiceError,
    build_catalog_braid_input,
    build_custom_braid_input,
    build_custom_braid_word,
    build_invariant_explanation,
    build_invariant_project,
    evaluate_braid_result,
    evaluate_catalog_result,
    format_application_braid_compact_result,
    format_application_braid_result,
    format_application_branch_compact,
    format_application_branch_result,
    get_branch_explanation,
    list_catalog_examples,
    list_evaluation_branches,
    parse_q_text,
    serialize_application_braid_result,
    validate_project_document,
)

from .braid_preview import BraidPreviewWidget


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
    q_text: str


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

    explanationChanged = Signal(object)
    resultChanged = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("invariantCalculationWorkflow")
        self._examples = list_catalog_examples()
        self._branches = list_evaluation_branches()
        self._active_jobs: list[tuple[QThread, _InvariantWorker]] = []
        self._last_result: ApplicationBraidResult | None = None
        self._last_q_text = "2"
        self._last_q_parameter: Any = parse_q_text("2")
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
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        self.page_tabs = QTabWidget(self)
        self.page_tabs.setObjectName("invariantPageTabs")
        self.setup_page = QWidget(self.page_tabs)
        self.calculation_page = QWidget(self.page_tabs)
        self.page_tabs.addTab(self.setup_page, "Braid setup / preview")
        self.page_tabs.addTab(self.calculation_page, "Calculation / results")
        layout.addWidget(self.page_tabs, 1)

        setup_layout = QVBoxLayout(self.setup_page)
        setup_layout.setContentsMargins(4, 8, 4, 4)
        setup_layout.setSpacing(8)
        setup_intro = QLabel("Choose a built-in example or switch to Manual braid input. The diagram updates as you edit; calculation starts only when requested.", self.setup_page)
        setup_intro.setWordWrap(True)
        setup_layout.addWidget(setup_intro)

        self.setup_splitter = QSplitter(Qt.Orientation.Horizontal, self.setup_page)
        self.setup_splitter.setObjectName("invariantSetupSplitter")
        self.setup_splitter.setChildrenCollapsible(False)
        input_scroll = QScrollArea(self.setup_splitter)
        input_scroll.setObjectName("invariantInputScroll")
        input_scroll.setWidgetResizable(True)
        input_scroll.setFrameShape(QFrame.Shape.NoFrame)
        input_scroll.setMinimumWidth(245)
        input_panel = QWidget(input_scroll)
        input_panel_layout = QVBoxLayout(input_panel)
        input_panel_layout.setContentsMargins(0, 0, 6, 0)
        input_group = QGroupBox("Braid input", input_panel)
        input_layout = QFormLayout(input_group)
        self.source_combo = QComboBox(input_group)
        self.source_combo.setObjectName("invariantSourceMode")
        self.source_combo.addItem("Built-in example", "catalog")
        self.source_combo.addItem("Manual braid input", "custom")
        self.source_combo.currentIndexChanged.connect(self._source_changed)
        input_layout.addRow("Input mode:", self.source_combo)

        self.source_stack = QStackedWidget(input_group)
        self.source_stack.addWidget(self._build_catalog_source())
        self.source_stack.addWidget(self._build_custom_source())
        input_layout.addRow(self.source_stack)
        input_panel_layout.addWidget(input_group)
        input_panel_layout.addStretch(1)
        input_scroll.setWidget(input_panel)
        self.setup_splitter.addWidget(input_scroll)

        preview_group = QGroupBox("Braid diagram — wheel to zoom, drag to pan", self.setup_splitter)
        preview_layout = QVBoxLayout(preview_group)
        self.braid_preview = BraidPreviewWidget(preview_group)
        self.braid_preview.setMinimumHeight(380)
        self.braid_preview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        preview_layout.addWidget(self.braid_preview)
        self.setup_splitter.addWidget(preview_group)
        self.setup_splitter.setStretchFactor(0, 0)
        self.setup_splitter.setStretchFactor(1, 1)
        self.setup_splitter.setSizes([310, 680])
        setup_layout.addWidget(self.setup_splitter, 1)

        calculation_layout = QVBoxLayout(self.calculation_page)
        calculation_layout.setContentsMargins(4, 8, 4, 4)
        calculation_layout.setSpacing(8)
        calculation_intro = QLabel("Select invariant branches and q, then Calculate. The current braid comes from the Braid setup / preview page.", self.calculation_page)
        calculation_intro.setWordWrap(True)
        calculation_layout.addWidget(calculation_intro)
        self.calculation_splitter = QSplitter(Qt.Orientation.Vertical, self.calculation_page)
        self.calculation_splitter.setObjectName("invariantCalculationSplitter")
        self.calculation_splitter.setChildrenCollapsible(False)
        controls = QWidget(self.calculation_splitter)
        controls_layout = QVBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(8)
        self.branch_splitter = QSplitter(Qt.Orientation.Horizontal, controls)
        self.branch_splitter.setObjectName("invariantBranchSplitter")
        self.branch_splitter.setChildrenCollapsible(False)

        branch_group = QGroupBox("Invariant branches — select one or more", self.branch_splitter)
        branch_layout = QVBoxLayout(branch_group)
        branch_scroll = QScrollArea(branch_group)
        branch_scroll.setObjectName("invariantBranchScroll")
        branch_scroll.setWidgetResizable(True)
        branch_scroll.setMinimumHeight(145)
        branch_list = QWidget(branch_scroll)
        branch_list_layout = QVBoxLayout(branch_list)
        self._branch_checks: list[tuple[QCheckBox, Any]] = []
        for descriptor in self._branches:
            check = QCheckBox(f"{descriptor.display_name} ({descriptor.status})", branch_list)
            check.setObjectName(f"branch_{descriptor.model_id}")
            check.setChecked(True)
            check.setToolTip(descriptor.user_note)
            branch_list_layout.addWidget(check)
            self._branch_checks.append((check, descriptor))
            check.stateChanged.connect(lambda _state: self._emit_explanation())
            check.clicked.connect(lambda _checked, branch=descriptor: self._show_branch_details(branch.branch_id))
        branch_list_layout.addStretch(1)
        branch_scroll.setWidget(branch_list)
        branch_layout.addWidget(branch_scroll)
        self.branch_splitter.addWidget(branch_group)

        detail_group = QGroupBox("Branch details", self.branch_splitter)
        detail_layout = QVBoxLayout(detail_group)
        self.branch_details = QPlainTextEdit(detail_group)
        self.branch_details.setObjectName("invariantBranchDetails")
        self.branch_details.setReadOnly(True)
        detail_layout.addWidget(self.branch_details)
        self.branch_splitter.addWidget(detail_group)
        self.branch_splitter.setSizes([300, 420])
        controls_layout.addWidget(self.branch_splitter, 1)
        if self._branches:
            self._show_branch_details(self._branches[0].branch_id)

        execution_group = QGroupBox("Calculation", controls)
        execution_layout = QFormLayout(execution_group)
        self.q_input = QLineEdit("2", execution_group)
        self.q_input.setObjectName("invariantQInput")
        self.q_input.setPlaceholderText("2, 3/2, q, or another SymPy-compatible expression")
        self.q_input.textChanged.connect(lambda _text: self._emit_explanation())
        execution_layout.addRow("q:", self.q_input)
        self.result_mode_combo = QComboBox(execution_group)
        self.result_mode_combo.setObjectName("invariantResultMode")
        self.result_mode_combo.addItem("Compact", "compact")
        self.result_mode_combo.addItem("Detailed", "detailed")
        self.result_mode_combo.currentIndexChanged.connect(self._result_mode_changed)
        execution_layout.addRow("Result view:", self.result_mode_combo)
        calculation_row = QWidget(execution_group)
        action_layout = QHBoxLayout(calculation_row)
        action_layout.setContentsMargins(0, 0, 0, 0)
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
        action_layout.addWidget(self.calculate_button)
        action_layout.addStretch(1)
        action_layout.addWidget(self.copy_selected_button)
        action_layout.addWidget(self.copy_all_button)
        action_layout.addWidget(self.copy_json_button)
        action_layout.addWidget(self.export_button)
        execution_layout.addRow(calculation_row)
        controls_layout.addWidget(execution_group)
        self.calculation_splitter.addWidget(controls)

        results_panel = QWidget(self.calculation_splitter)
        results_layout = QVBoxLayout(results_panel)
        results_layout.setContentsMargins(0, 0, 0, 0)
        self.status_label = QLabel("Ready. Choose an input, branches, and q; calculation runs outside the UI thread.", results_panel)
        self.status_label.setObjectName("invariantCalculationStatus")
        self.status_label.setWordWrap(True)
        results_layout.addWidget(self.status_label)

        self.result_tabs = QTabWidget(results_panel)
        self.result_tabs.setObjectName("invariantResultTabs")
        self.result_tabs.currentChanged.connect(self._result_tab_changed)
        self._placeholder_result = QPlainTextEdit(self.result_tabs)
        self._placeholder_result.setReadOnly(True)
        self._placeholder_result.setPlainText("No calculation has been run.")
        self.result_tabs.addTab(self._placeholder_result, "Results")
        results_layout.addWidget(self.result_tabs, 1)
        self.calculation_splitter.addWidget(results_panel)
        self.calculation_splitter.setStretchFactor(0, 0)
        self.calculation_splitter.setStretchFactor(1, 1)
        self.calculation_splitter.setSizes([300, 360])
        calculation_layout.addWidget(self.calculation_splitter, 1)
        self._update_catalog_preview()
        self._emit_explanation()

    def _show_branch_details(self, branch_id: str) -> None:
        explanation = get_branch_explanation(branch_id)
        descriptor = next(branch for branch in self._branches if branch.branch_id == branch_id)
        self.branch_details.setPlainText(
            f"{descriptor.display_name} ({descriptor.status})\n\n"
            f"{explanation.summary}\n\n{descriptor.user_note}\n\n"
            f"Output: {explanation.output_name}\n"
            f"Normalization: {explanation.normalization}\n"
            f"Variable: {explanation.variable_convention}"
        )

    def _build_catalog_source(self) -> QWidget:
        source = QWidget(self)
        layout = QFormLayout(source)
        heading = QLabel("Built-in example", source)
        heading.setStyleSheet("font-weight: 600;")
        layout.addRow(heading)
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
        heading = QLabel("Manual braid input", source)
        heading.setStyleSheet("font-weight: 600;")
        layout.addRow(heading)
        convention = QLabel("Enter a signed Artin word in order: +i = σᵢ, −i = σᵢ⁻¹. Example: 1 -2 1.", source)
        convention.setWordWrap(True)
        layout.addRow(convention)
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
        self.custom_strands_spin.valueChanged.connect(self._update_braid_preview)
        self.custom_generators_input.textChanged.connect(self._update_braid_preview)
        self.custom_strands_spin.valueChanged.connect(lambda _value: self._emit_explanation())
        self.custom_generators_input.textChanged.connect(lambda _text: self._emit_explanation())
        layout.addRow("Strands:", self.custom_strands_spin)
        layout.addRow("Generators:", self.custom_generators_input)
        layout.addRow("Label:", self.custom_label_input)
        layout.addRow("Notes:", self.custom_notes_input)
        return source

    def _source_changed(self) -> None:
        self.source_stack.setCurrentIndex(self.source_combo.currentIndex())
        self._update_braid_preview()
        self._emit_explanation()

    def _update_catalog_preview(self) -> None:
        index = self.example_combo.currentIndex()
        if index < 0 or index >= len(self._examples):
            self.example_preview.clear()
            self._emit_explanation()
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
        self._update_braid_preview()
        self._emit_explanation()

    def _update_braid_preview(self) -> None:
        """Refresh the vector preview from the service-owned input model."""

        try:
            if str(self.source_combo.currentData()) == "catalog":
                braid_input = build_catalog_braid_input(self.example_combo.currentText())
            else:
                braid_input = build_custom_braid_input(self.custom_strands_spin.value(), self.custom_generators_input.text())
        except ApplicationServiceError as exc:
            self.braid_preview.set_message(f"Preview unavailable: {exc}")
            self.explanationChanged.emit(None)
            return
        self.braid_preview.set_braid_word(braid_input.braid_word)
        self._emit_explanation(braid_input)

    def current_explanation(self):
        """Return contextual service-owned guidance without evaluating anything."""

        try:
            if str(self.source_combo.currentData()) == "catalog":
                braid_input = build_catalog_braid_input(self.example_combo.currentText())
            else:
                braid_input = build_custom_braid_input(self.custom_strands_spin.value(), self.custom_generators_input.text())
        except ApplicationServiceError:
            return None
        return build_invariant_explanation(
            braid_input.braid_word,
            branch_ids=self._selected_branch_ids(),
            source_label=braid_input.source_label,
        )

    def _emit_explanation(self, braid_input: Any | None = None) -> None:
        if braid_input is None:
            try:
                if str(self.source_combo.currentData()) == "catalog":
                    braid_input = build_catalog_braid_input(self.example_combo.currentText())
                else:
                    braid_input = build_custom_braid_input(self.custom_strands_spin.value(), self.custom_generators_input.text())
            except ApplicationServiceError:
                self.explanationChanged.emit(None)
                return
        self.explanationChanged.emit(
            build_invariant_explanation(
                braid_input.braid_word,
                branch_ids=self._selected_branch_ids(),
                source_label=braid_input.source_label,
            )
        )

    def _selected_branch_ids(self) -> tuple[str, ...]:
        return tuple(descriptor.branch_id for check, descriptor in self._branch_checks if check.isChecked())

    def current_project_document(self) -> ApplicationProjectDocument:
        """Capture setup only; no invariant evaluation is performed."""

        return build_invariant_project(
            source_mode=str(self.source_combo.currentData()),
            example_label=self.example_combo.currentText(),
            num_strands=self.custom_strands_spin.value(),
            generator_text=self.custom_generators_input.text(),
            custom_label=self.custom_label_input.text(),
            custom_notes=self.custom_notes_input.text(),
            q_text=self.q_input.text(),
            branch_ids=self._selected_branch_ids(),
            ui_state={"source_index": self.source_combo.currentIndex()},
        )

    def apply_project_document(self, document: ApplicationProjectDocument) -> None:
        """Populate controls from a validated project without starting a worker."""

        document = validate_project_document(document)
        if document.workflow != "invariant":
            raise ApplicationServiceError("This project belongs to the custom R/check-R workflow.")
        data = document.input_data
        source_mode = str(data["source_mode"])
        self.source_combo.setCurrentIndex(0 if source_mode == "catalog" else 1)
        if source_mode == "catalog":
            index = self.example_combo.findText(str(data["example_label"]))
            if index < 0:
                raise ApplicationServiceError(f"Catalog example '{data['example_label']}' is not available in this application.")
            self.example_combo.setCurrentIndex(index)
        self.custom_strands_spin.setValue(int(data["num_strands"]))
        self.custom_generators_input.setText(str(data["generator_text"]))
        self.custom_label_input.setText(str(data["custom_label"]))
        self.custom_notes_input.setText(str(data["custom_notes"]))
        self.q_input.setText(str(data["q_text"]))
        selected = set(data["branch_ids"])
        for check, descriptor in self._branch_checks:
            check.setChecked(descriptor.branch_id in selected)
        self._update_braid_preview()
        self.page_tabs.setCurrentWidget(self.setup_page)

    def load_curated_example(self, example: Any) -> None:
        document = example.build_project()
        self.apply_project_document(document)

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
            q_text=self.q_input.text(),
        )
        self._start_worker(request)

    def _start_worker(self, request: _InvariantRequest) -> None:
        self._set_busy(True, "Calculation running outside the UI thread…")
        thread = QThread(self)
        worker = _InvariantWorker(request)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.succeeded.connect(lambda result, submitted_request=request: self._calculation_succeeded(result, submitted_request))
        worker.failed.connect(self._calculation_failed)
        worker.succeeded.connect(lambda _result, active_thread=thread: active_thread.quit())
        worker.failed.connect(lambda _message, active_thread=thread: active_thread.quit())
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(lambda active_thread=thread, active_worker=worker: self._job_finished(active_thread, active_worker))
        self._active_jobs.append((thread, worker))
        thread.start()

    def _calculation_succeeded(self, result: object, request: _InvariantRequest | None = None) -> None:
        assert isinstance(result, ApplicationBraidResult)
        self._last_result = result
        if request is not None:
            self._last_q_text = request.q_text
            self._last_q_parameter = request.q_parameter
        self.resultChanged.emit(result)
        self._render_result(result)
        self.copy_selected_button.setEnabled(True)
        self.copy_all_button.setEnabled(True)
        self.copy_json_button.setEnabled(True)
        self.export_button.setEnabled(True)
        self.status_label.setText("Calculation complete. Formal and candidate branch statuses are shown in the result tabs.")
        self.page_tabs.setCurrentWidget(self.calculation_page)

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
        current_index = self.result_tabs.currentIndex()
        self._clear_result_tabs()
        summary = QPlainTextEdit(self.result_tabs)
        summary.setReadOnly(True)
        if self._result_view_mode() == "compact":
            summary.setPlainText(
                format_application_braid_compact_result(
                    result,
                    q_parameter=self._last_q_parameter,
                    q_parameter_text=self._last_q_text,
                )
            )
        else:
            summary.setPlainText(format_application_braid_result(result))
        self.result_tabs.addTab(summary, "All results")
        for branch in result.branch_results:
            card = QPlainTextEdit(self.result_tabs)
            card.setReadOnly(True)
            card.setPlainText(self._format_branch_card(branch, result))
            label = f"{branch.display_name} ({branch.status})"
            self.result_tabs.addTab(card, label)
        self.result_tabs.setCurrentIndex(min(max(current_index, 0), self.result_tabs.count() - 1))

    def _format_branch_card(self, branch: ApplicationBranchResult, result: ApplicationBraidResult) -> str:
        if self._result_view_mode() == "compact":
            return format_application_branch_compact(branch, q_parameter=self._last_q_parameter, q_parameter_text=self._last_q_text)
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
            lines.extend(get_branch_explanation(branch.branch_id).warnings)
        return "\n".join(lines)

    def _result_view_mode(self) -> str:
        return str(self.result_mode_combo.currentData() or "compact")

    @Slot()
    def _result_mode_changed(self) -> None:
        if self._last_result is not None:
            self._render_result(self._last_result)

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
        try:
            self.export_result_to_path(file_name, "text" if "Text" in selected_filter else "json")
        except (ApplicationServiceError, OSError) as exc:
            self._set_error(f"Could not export result: {exc}")
            return
        self.status_label.setText(f"Exported result to {file_name}.")

    def export_result_to_path(self, path: str | Path, file_format: str = "json") -> Path:
        """Write the selected result using the maintained service serializers."""

        if self._last_result is None:
            raise ApplicationServiceError("No invariant calculation result is available to export.")
        if file_format not in {"text", "json"}:
            raise ApplicationServiceError(f"Unsupported invariant export format '{file_format}'.")
        content = format_application_braid_result(self._last_result) if file_format == "text" else serialize_application_braid_result(self._last_result)
        target = Path(path)
        target.write_text(content, encoding="utf-8", newline="\n")
        return target

    def _result_tab_changed(self, _index: int) -> None:
        self.copy_selected_button.setEnabled(self._last_result is not None)
