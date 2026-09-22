"""Lightweight searchable browser for curated service-owned examples."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from src.services import CuratedExample, list_curated_examples


class CuratedExampleBrowser(QWidget):
    """Search/filter/load control that never evaluates a selected example."""

    exampleLoaded = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("curatedExampleBrowser")
        self._examples: tuple[CuratedExample, ...] = ()
        self._filtered: tuple[CuratedExample, ...] = ()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        title = QLabel("Curated example library", self)
        title.setStyleSheet("font-size: 16px; font-weight: 600;")
        layout.addWidget(title)
        description = QLabel("Select an evidence-backed setup, inspect its status/provenance, then load it into a workflow. Loading never calculates.", self)
        description.setWordWrap(True)
        description.setStyleSheet("color: #555;")
        layout.addWidget(description)

        form = QFormLayout()
        self.category_combo = QComboBox(self)
        self.category_combo.setObjectName("curatedExampleCategory")
        self.category_combo.addItem("All categories", None)
        self.category_combo.addItem("Knots and links", "knots_links")
        self.category_combo.addItem("Braid demonstrations", "braid_demonstration")
        self.category_combo.addItem("Custom R/check-R", "custom_rmatrix")
        self.category_combo.currentIndexChanged.connect(self._refresh)
        form.addRow("Category:", self.category_combo)
        self.search_input = QLineEdit(self)
        self.search_input.setObjectName("curatedExampleSearch")
        self.search_input.setPlaceholderText("Search name, tags, provenance…")
        self.search_input.textChanged.connect(self._refresh)
        form.addRow("Search:", self.search_input)
        layout.addLayout(form)

        self.example_list = QListWidget(self)
        self.example_list.setObjectName("curatedExampleList")
        self.example_list.currentItemChanged.connect(self._selection_changed)
        layout.addWidget(self.example_list, 1)
        self.details = QTextBrowser(self)
        self.details.setObjectName("curatedExampleDetails")
        self.details.setOpenExternalLinks(True)
        self.details.setMinimumHeight(150)
        layout.addWidget(self.details)
        self.load_button = QPushButton("Load example", self)
        self.load_button.setObjectName("loadCuratedExample")
        self.load_button.setEnabled(False)
        self.load_button.clicked.connect(self._load_selected)
        layout.addWidget(self.load_button)
        self._examples = list_curated_examples()
        self._refresh()

    @property
    def filtered_examples(self) -> tuple[CuratedExample, ...]:
        return self._filtered

    def _refresh(self) -> None:
        category = self.category_combo.currentData()
        self._filtered = list_curated_examples(category=category, search=self.search_input.text())
        self.example_list.blockSignals(True)
        self.example_list.clear()
        for example in self._filtered:
            item = QListWidgetItem(f"{example.display_name}  [{example.mathematical_status}]", self.example_list)
            item.setData(0x0100, example)
        self.example_list.blockSignals(False)
        if self.example_list.count():
            self.example_list.setCurrentRow(0)
        else:
            self.details.clear()
            self.load_button.setEnabled(False)

    def _selection_changed(self, current: QListWidgetItem | None, _previous: QListWidgetItem | None) -> None:
        example = current.data(0x0100) if current is not None else None
        if not isinstance(example, CuratedExample):
            self.details.clear()
            self.load_button.setEnabled(False)
            return
        self.details.setPlainText(
            f"{example.display_name}\n"
            f"Category: {example.category}\n"
            f"Workflow: {example.workflow}\n"
            f"Status: {example.mathematical_status}\n"
            f"\n{example.description}\n\n"
            f"Braid: {example.num_strands} strands; generators {list(example.generators)}\n"
            f"Matrix input: {example.input_kind or 'not applicable'}\n"
            f"Provenance: {example.provenance}\n"
            f"Tags: {', '.join(example.tags)}"
        )
        self.load_button.setEnabled(True)

    def _load_selected(self) -> None:
        current = self.example_list.currentItem()
        example = current.data(0x0100) if current is not None else None
        if isinstance(example, CuratedExample):
            self.exampleLoaded.emit(example)


__all__ = ["CuratedExampleBrowser"]
