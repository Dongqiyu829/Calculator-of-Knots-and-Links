"""Maintained PySide6 shell and custom braid-operator workflow."""

from __future__ import annotations

import sys

from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.services import ApplicationCatalogExample, list_catalog_examples, list_evaluation_branches

from .custom_matrix_workflow import CustomMatrixWorkflow


APPLICATION_TITLE = "Calculator of Knots and Links"


class DesktopMainWindow(QMainWindow):
    """Service-driven desktop shell with an explicit custom R/check-R mode."""

    def __init__(self) -> None:
        super().__init__()
        self._examples = list_catalog_examples()
        self._branches = list_evaluation_branches()
        self.setWindowTitle(APPLICATION_TITLE)
        self.resize(1100, 700)
        self._build_menu()
        self._build_central_widget()
        self.setStatusBar(QStatusBar(self))
        self.statusBar().showMessage("Ready. Catalog evaluation is pending; custom R/check-R operators are available in their own tab.")

    @property
    def examples(self) -> tuple[ApplicationCatalogExample, ...]:
        """Expose the loaded service snapshots for shell smoke tests and presenters."""

        return self._examples

    @property
    def branches(self):
        """Expose the loaded service branch descriptors without evaluating them."""

        return self._branches

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
        subtitle = QLabel("Desktop calculation workspace — service-driven shell")
        subtitle.setStyleSheet("color: #555;")
        root_layout.addWidget(subtitle)

        tabs = QTabWidget(root)
        tabs.setObjectName("desktopWorkflowTabs")
        tabs.addTab(self._build_catalog_shell(), "Built-in preview")
        self.custom_matrix_workflow = CustomMatrixWorkflow(tabs)
        tabs.addTab(self.custom_matrix_workflow, "Custom R/check-R operator")
        root_layout.addWidget(tabs, 1)
        self.workflow_tabs = tabs
        self.setCentralWidget(root)

    def _build_catalog_shell(self) -> QWidget:
        """Retain the original metadata-only catalog shell without evaluating it."""

        catalog_shell = QWidget(self)
        layout = QVBoxLayout(catalog_shell)
        layout.setContentsMargins(0, 0, 0, 0)
        splitter = QSplitter(catalog_shell)
        splitter.addWidget(self._build_source_panel())
        splitter.addWidget(self._build_workspace_panel())
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter)
        return catalog_shell

    def _build_source_panel(self) -> QWidget:
        panel = QWidget(self)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        source_group = QGroupBox("Input source", panel)
        source_layout = QFormLayout(source_group)
        self.example_combo = QComboBox(source_group)
        for example in self._examples:
            self.example_combo.addItem(example.label, example)
        self.example_combo.currentIndexChanged.connect(self._update_example_preview)
        source_layout.addRow("Built-in example:", self.example_combo)
        self.example_details = QLabel(source_group)
        self.example_details.setWordWrap(True)
        source_layout.addRow("Preview:", self.example_details)
        layout.addWidget(source_group)

        branch_group = QGroupBox("Invariant branches", panel)
        branch_layout = QVBoxLayout(branch_group)
        for branch in self._branches:
            selector = QCheckBox(f"{branch.display_name} ({branch.status})", branch_group)
            selector.setChecked(True)
            selector.setToolTip(branch.user_note)
            branch_layout.addWidget(selector)
        layout.addWidget(branch_group)
        layout.addStretch(1)
        self._update_example_preview(self.example_combo.currentIndex())
        return panel

    def _build_workspace_panel(self) -> QWidget:
        workspace = QGroupBox("Preview and results", self)
        layout = QVBoxLayout(workspace)
        placeholder = QLabel(
            "This built-in preview loads examples and branch status only.\n\n"
            "The Custom R/check-R operator tab separately supports explicit matrix validation and background braid-operator construction. "
            "Built-in invariant evaluation remains a later M3 task."
        )
        placeholder.setWordWrap(True)
        placeholder.setStyleSheet("padding: 24px; color: #444;")
        layout.addWidget(placeholder)
        layout.addStretch(1)
        return workspace

    def _update_example_preview(self, index: int) -> None:
        if index < 0 or index >= len(self._examples):
            self.example_details.clear()
            return
        example = self._examples[index]
        self.example_details.setText(
            f"{example.word_string}\n{example.num_strands} strands; generators {list(example.generators)}\n{example.notes}"
        )

    def _show_about(self) -> None:
        QMessageBox.about(
            self,
            f"About {APPLICATION_TITLE}",
            "PySide6 desktop shell. It uses the frozen application service contract and does not evaluate invariants on startup. "
            "The custom R/check-R tab constructs operators only, not knot/link invariants.",
        )


def launch_desktop_application(argv: list[str] | None = None) -> int:
    """Create, show, and run the maintained PySide6 desktop application."""

    app = QApplication.instance() or QApplication(argv if argv is not None else sys.argv)
    window = DesktopMainWindow()
    window.show()
    return app.exec()
