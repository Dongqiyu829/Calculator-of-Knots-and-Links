"""First PySide6 shell, intentionally limited to lightweight application metadata."""

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
    QVBoxLayout,
    QWidget,
)

from src.services import ApplicationCatalogExample, list_catalog_examples, list_evaluation_branches


APPLICATION_TITLE = "Calculator of Knots and Links"


class DesktopMainWindow(QMainWindow):
    """Static service-driven shell for the future desktop calculation workflow."""

    def __init__(self) -> None:
        super().__init__()
        self._examples = list_catalog_examples()
        self._branches = list_evaluation_branches()
        self.setWindowTitle(APPLICATION_TITLE)
        self.resize(1100, 700)
        self._build_menu()
        self._build_central_widget()
        self.setStatusBar(QStatusBar(self))
        self.statusBar().showMessage("Ready. Select an example and models; evaluation will be added in a later milestone.")

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

        splitter = QSplitter(self)
        splitter.addWidget(self._build_source_panel())
        splitter.addWidget(self._build_workspace_panel())
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        root_layout.addWidget(splitter, 1)
        self.setCentralWidget(root)

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
            "This first desktop shell loads examples and branch status only.\n\n"
            "Braid editing, evaluation, result details, export, and background computation will be added in subsequent M3 tasks."
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
            "PySide6 desktop shell. It uses the frozen application service contract and does not evaluate invariants on startup.",
        )


def launch_desktop_application(argv: list[str] | None = None) -> int:
    """Create, show, and run the maintained PySide6 desktop application."""

    app = QApplication.instance() or QApplication(argv if argv is not None else sys.argv)
    window = DesktopMainWindow()
    window.show()
    return app.exec()
