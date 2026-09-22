"""Maintained PySide6 shell with built-in and custom calculation workflows."""

from __future__ import annotations

import sys

from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.services import ApplicationCatalogExample
from src.version import __version__

from .custom_matrix_workflow import CustomMatrixWorkflow
from .invariant_workflow import InvariantCalculationWorkflow


APPLICATION_TITLE = "Calculator of Knots and Links"


class DesktopMainWindow(QMainWindow):
    """Service-driven desktop window with normal and advanced calculation modes."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APPLICATION_TITLE)
        self.resize(1100, 700)
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
