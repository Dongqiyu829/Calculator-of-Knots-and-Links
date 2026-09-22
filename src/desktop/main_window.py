"""Maintained PySide6 shell with built-in and custom calculation workflows."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QDockWidget,
    QFileDialog,
    QMessageBox,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.services import (
    ApplicationCatalogExample,
    ApplicationServiceError,
    CUSTOM_RMATRIX_WORKFLOW,
    build_custom_rmatrix_explanation,
    get_documentation_resource,
    INVARIANT_WORKFLOW,
    load_project_file,
    save_project_file,
)
from src.version import __version__

from .custom_matrix_workflow import CustomMatrixWorkflow
from .documentation_viewer import DocumentationDialog
from .explanation_panel import ExplanationPanel
from .invariant_workflow import InvariantCalculationWorkflow
from .example_browser import CuratedExampleBrowser


APPLICATION_TITLE = "Calculator of Knots and Links"


class DesktopMainWindow(QMainWindow):
    """Service-driven desktop window with normal and advanced calculation modes."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APPLICATION_TITLE)
        self.resize(1100, 700)
        self._project_path: Path | None = None
        self._build_menu()
        self._build_central_widget()
        self.setStatusBar(QStatusBar(self))
        self.statusBar().showMessage("Ready. Invariant calculations and custom R/check-R operators run in separate tabs.")

    @property
    def examples(self) -> tuple[ApplicationCatalogExample, ...]:
        """Expose the loaded service snapshots for shell smoke tests and presenters."""

        return self.invariant_workflow.examples

    @property
    def branches(self):
        """Expose the loaded service branch descriptors without evaluating them."""

        return self.invariant_workflow.branches

    def _build_menu(self) -> None:
        file_menu = self.menuBar().addMenu("&File")
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        file_menu.addSeparator()
        open_action = QAction("Open Project…", self)
        open_action.setObjectName("openProject")
        open_action.triggered.connect(self._open_project_dialog)
        file_menu.addAction(open_action)
        save_action = QAction("Save Project", self)
        save_action.setObjectName("saveProject")
        save_action.triggered.connect(self._save_project)
        file_menu.addAction(save_action)
        save_as_action = QAction("Save Project As…", self)
        save_as_action.setObjectName("saveProjectAs")
        save_as_action.triggered.connect(self._save_project_as_dialog)
        file_menu.addAction(save_as_action)

        export_menu = file_menu.addMenu("Export")
        self.export_text_action = QAction("Calculation result as text…", self)
        self.export_text_action.setObjectName("exportActiveResultText")
        self.export_text_action.triggered.connect(lambda: self._export_active_result("text"))
        export_menu.addAction(self.export_text_action)
        self.export_json_action = QAction("Calculation/operator result as JSON…", self)
        self.export_json_action.setObjectName("exportActiveResultJson")
        self.export_json_action.triggered.connect(lambda: self._export_active_result("json"))
        export_menu.addAction(self.export_json_action)
        export_menu.addSeparator()
        self.export_svg_action = QAction("Braid preview as SVG…", self)
        self.export_svg_action.setObjectName("exportActiveBraidSvg")
        self.export_svg_action.triggered.connect(lambda: self._export_active_preview("svg"))
        export_menu.addAction(self.export_svg_action)
        self.export_png_action = QAction("Braid preview as PNG…", self)
        self.export_png_action.setObjectName("exportActiveBraidPng")
        self.export_png_action.triggered.connect(lambda: self._export_active_preview("png"))
        export_menu.addAction(self.export_png_action)

        help_menu = self.menuBar().addMenu("&Help")
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        user_guide_action = QAction("User Guide / 用户指南", self)
        user_guide_action.setObjectName("openUserGuide")
        user_guide_action.triggered.connect(lambda: self._show_documentation("user_guide"))
        help_menu.addAction(user_guide_action)
        math_guide_action = QAction("Mathematical Implementation", self)
        math_guide_action.setObjectName("openMathematicalImplementation")
        math_guide_action.triggered.connect(lambda: self._show_documentation("mathematical_implementation"))
        help_menu.addAction(math_guide_action)

    def _build_central_widget(self) -> None:
        root = QWidget(self)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(20, 20, 20, 20)
        root_layout.setSpacing(16)

        title = QLabel(APPLICATION_TITLE)
        title.setObjectName("applicationTitle")
        title.setStyleSheet("font-size: 22px; font-weight: 600;")
        root_layout.addWidget(title)
        subtitle = QLabel("Desktop calculation workspace — service-driven application boundary")
        subtitle.setStyleSheet("color: #555;")
        root_layout.addWidget(subtitle)

        tabs = QTabWidget(root)
        tabs.setObjectName("desktopWorkflowTabs")
        self.invariant_workflow = InvariantCalculationWorkflow(tabs)
        tabs.addTab(self.invariant_workflow, "Invariant calculation")
        self.example_combo = self.invariant_workflow.example_combo
        self.custom_matrix_workflow = CustomMatrixWorkflow(tabs)
        tabs.addTab(self.custom_matrix_workflow, "Custom R/check-R operator")
        tabs.currentChanged.connect(self._workflow_tab_changed)
        root_layout.addWidget(tabs, 1)
        self.workflow_tabs = tabs
        self.setCentralWidget(root)

        self.example_browser = CuratedExampleBrowser(self)
        self.example_browser.exampleLoaded.connect(self._load_curated_example)
        dock = QDockWidget("Curated examples", self)
        dock.setObjectName("curatedExamplesDock")
        dock.setWidget(self.example_browser)
        dock.setMinimumWidth(320)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)

        self.explanation_panel = ExplanationPanel(self)
        self.explanation_panel_dock = QDockWidget("Mathematics / How it works", self)
        self.explanation_panel_dock.setObjectName("mathematicalExplanationDock")
        self.explanation_panel_dock.setWidget(self.explanation_panel)
        self.explanation_panel_dock.setMinimumHeight(180)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.explanation_panel_dock)
        self.invariant_workflow.explanationChanged.connect(self.explanation_panel.set_explanation)
        self.custom_matrix_workflow.explanationChanged.connect(self.explanation_panel.set_explanation)
        self.invariant_workflow.resultChanged.connect(lambda _result: self._update_export_actions())
        self.custom_matrix_workflow.resultChanged.connect(lambda _result: self._update_export_actions())
        self.invariant_workflow.braid_preview.geometryChanged.connect(lambda _geometry: self._update_export_actions())
        self.custom_matrix_workflow.braid_preview.geometryChanged.connect(lambda _geometry: self._update_export_actions())
        self._workflow_tab_changed(self.workflow_tabs.currentIndex())

    def _load_curated_example(self, example: object) -> None:
        try:
            if getattr(example, "workflow", None) == INVARIANT_WORKFLOW:
                self.invariant_workflow.load_curated_example(example)
                self.workflow_tabs.setCurrentWidget(self.invariant_workflow)
            elif getattr(example, "workflow", None) == CUSTOM_RMATRIX_WORKFLOW:
                self.custom_matrix_workflow.load_curated_example(example)
                self.workflow_tabs.setCurrentWidget(self.custom_matrix_workflow)
            else:
                raise ApplicationServiceError(f"Unsupported curated example workflow '{getattr(example, 'workflow', None)}'.")
            self._project_path = None
            self._update_export_actions()
            self.statusBar().showMessage(f"Loaded example '{getattr(example, 'display_name', 'example')}'. No calculation was started.")
        except ApplicationServiceError as exc:
            self.statusBar().showMessage(f"Could not load example: {exc}")

    def save_project_to_path(self, path: str | Path) -> Path:
        workflow = self.invariant_workflow if self.workflow_tabs.currentWidget() is self.invariant_workflow else self.custom_matrix_workflow
        document = workflow.current_project_document()
        target = save_project_file(path, document)
        self._project_path = target
        self.statusBar().showMessage(f"Saved project setup to {target}.")
        return target

    def load_project_from_path(self, path: str | Path) -> None:
        document = load_project_file(path)
        if document.workflow == INVARIANT_WORKFLOW:
            self.invariant_workflow.apply_project_document(document)
            self.workflow_tabs.setCurrentWidget(self.invariant_workflow)
        elif document.workflow == CUSTOM_RMATRIX_WORKFLOW:
            self.custom_matrix_workflow.apply_project_document(document)
            self.workflow_tabs.setCurrentWidget(self.custom_matrix_workflow)
        else:  # pragma: no cover - service validation rejects this first.
            raise ApplicationServiceError(f"Unsupported project workflow '{document.workflow}'.")
        self._project_path = Path(path)
        suffix = " (application version differs)" if document.application_version_mismatch else ""
        self.statusBar().showMessage(f"Loaded project setup from {path}; no calculation was started{suffix}.")

    def _open_project_dialog(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Open project", "", "Knot calculation projects (*.knotcalc.json);;JSON files (*.json)")
        if not path:
            return
        try:
            self.load_project_from_path(path)
        except ApplicationServiceError as exc:
            self.statusBar().showMessage(f"Could not open project: {exc}")

    def _save_project(self) -> None:
        if self._project_path is None:
            self._save_project_as_dialog()
            return
        try:
            self.save_project_to_path(self._project_path)
        except ApplicationServiceError as exc:
            self.statusBar().showMessage(f"Could not save project: {exc}")

    def _save_project_as_dialog(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save project", "calculation.knotcalc.json", "Knot calculation projects (*.knotcalc.json);;JSON files (*.json)")
        if not path:
            return
        if not path.endswith(".knotcalc.json"):
            path += ".knotcalc.json"
        try:
            self.save_project_to_path(path)
        except ApplicationServiceError as exc:
            self.statusBar().showMessage(f"Could not save project: {exc}")

    def _show_about(self) -> None:
        operator_boundary = build_custom_rmatrix_explanation(None).summary
        QMessageBox.about(
            self,
            f"About {APPLICATION_TITLE}",
            f"PySide6 desktop application, version {__version__}. Invariant calculations use the frozen application service contract and run only on request. "
            f"{operator_boundary}",
        )

    def _active_workflow(self):
        return self.invariant_workflow if self.workflow_tabs.currentWidget() is self.invariant_workflow else self.custom_matrix_workflow

    def _workflow_tab_changed(self, _index: int) -> None:
        workflow = self._active_workflow()
        self.explanation_panel.set_explanation(workflow.current_explanation())
        self._update_export_actions()

    def _update_export_actions(self) -> None:
        workflow = self._active_workflow()
        has_result = getattr(workflow, "_last_result", None) is not None
        has_preview = workflow.braid_preview.geometry is not None
        self.export_text_action.setEnabled(workflow is self.invariant_workflow and has_result)
        self.export_json_action.setEnabled(has_result)
        self.export_svg_action.setEnabled(has_preview)
        self.export_png_action.setEnabled(has_preview)

    def _export_active_result(self, file_format: str) -> None:
        workflow = self._active_workflow()
        if getattr(workflow, "_last_result", None) is None:
            return
        if file_format == "text":
            default_name = "invariant_result.txt"
            file_filter = "Text files (*.txt)"
        elif workflow is self.custom_matrix_workflow:
            default_name = "custom_braid_operator.json"
            file_filter = "JSON files (*.json)"
        else:
            default_name = "invariant_result.json"
            file_filter = "JSON files (*.json)"
        path, _selected = QFileDialog.getSaveFileName(self, "Export result", default_name, file_filter)
        if not path:
            return
        try:
            workflow.export_result_to_path(path, file_format)
        except (ApplicationServiceError, OSError) as exc:
            self.statusBar().showMessage(f"Could not export result: {exc}")
            return
        self.statusBar().showMessage(f"Exported result to {path}.")

    def _export_active_preview(self, file_format: str) -> None:
        workflow = self._active_workflow()
        if workflow.braid_preview.geometry is None:
            return
        if file_format == "svg":
            default_name, file_filter = "braid_preview.svg", "SVG files (*.svg)"
        else:
            default_name, file_filter = "braid_preview.png", "PNG files (*.png)"
        path, _selected = QFileDialog.getSaveFileName(self, "Export braid preview", default_name, file_filter)
        if not path:
            return
        try:
            if file_format == "svg":
                workflow.braid_preview.export_svg(path)
            else:
                workflow.braid_preview.export_png(path)
        except (OSError, ValueError) as exc:
            self.statusBar().showMessage(f"Could not export braid preview: {exc}")
            return
        self.statusBar().showMessage(f"Exported braid preview to {path}.")

    def _show_documentation(self, resource_id: str) -> None:
        try:
            resource = get_documentation_resource(resource_id)
            dialog = DocumentationDialog(resource, self)
            dialog.exec()
        except (OSError, KeyError) as exc:
            self.statusBar().showMessage(f"Documentation is unavailable: {exc}")


def launch_desktop_application(argv: list[str] | None = None) -> int:
    """Create, show, and run the maintained PySide6 desktop application."""

    app = QApplication.instance() or QApplication(argv if argv is not None else sys.argv)
    window = DesktopMainWindow()
    window.show()
    return app.exec()
