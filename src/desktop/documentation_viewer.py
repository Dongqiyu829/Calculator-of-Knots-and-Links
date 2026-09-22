"""Offline Markdown documentation viewer for the maintained desktop app."""

from __future__ import annotations

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QTextBrowser, QVBoxLayout, QWidget

from src.services import DocumentationResource, read_documentation


class DocumentationDialog(QDialog):
    """Show one bundled documentation resource without requiring the network."""

    def __init__(self, resource: DocumentationResource, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName(f"documentationDialog_{resource.resource_id}")
        self.setWindowTitle(resource.title)
        self.resize(860, 640)
        title = QLabel(resource.title, self)
        title.setStyleSheet("font-size: 16px; font-weight: 600;")
        viewer = QTextBrowser(self)
        viewer.setObjectName(f"documentationText_{resource.resource_id}")
        viewer.setOpenExternalLinks(False)
        viewer.setReadOnly(True)
        try:
            viewer.setMarkdown(read_documentation(resource.resource_id))
        except (OSError, KeyError) as exc:
            viewer.setPlainText(f"Documentation is unavailable in this build: {exc}")
        close = QDialogButtonBox(QDialogButtonBox.StandardButton.Close, self)
        close.rejected.connect(self.reject)
        close.accepted.connect(self.accept)
        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(viewer, 1)
        layout.addWidget(close)


__all__ = ["DocumentationDialog"]
