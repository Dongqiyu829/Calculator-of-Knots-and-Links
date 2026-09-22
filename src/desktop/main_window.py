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
    INVARIANT_WORKFLOW,
    load_project_file,
    save_project_file,
)
from src.version import __version__

from .custom_matrix_workflow import CustomMatrixWorkflow
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

        help_menu = self.menuBar().addMenu("&Help")
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

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
        QMessageBox.about(
            self,
            f"About {APPLICATION_TITLE}",
            f"PySide6 desktop application, version {__version__}. Invariant calculations use the frozen application service contract and run only on request. "
            "The custom R/check-R tab constructs operators only, not knot/link invariants.",
        )


def launch_desktop_application(argv: list[str] | None = None) -> int:
    """Create, show, and run the maintained PySide6 desktop application."""

    app = QApplication.instance() or QApplication(argv if argv is not None else sys.argv)
    window = DesktopMainWindow()
    window.show()
    return app.exec()
