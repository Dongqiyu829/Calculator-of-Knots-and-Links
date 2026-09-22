"""Low-clutter Qt renderer for service-owned mathematical explanations."""

from __future__ import annotations

from html import escape

from PySide6.QtWidgets import QLabel, QTextBrowser, QVBoxLayout, QWidget

from src.services import MathematicalExplanation


class ExplanationPanel(QWidget):
    """Render one :class:`MathematicalExplanation` without owning its claims."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("mathematicalExplanationPanel")
        self._explanation: MathematicalExplanation | None = None
        self.title_label = QLabel("Mathematics", self)
        self.title_label.setObjectName("mathematicalExplanationTitle")
        self.title_label.setStyleSheet("font-size: 15px; font-weight: 600;")
        self.viewer = QTextBrowser(self)
        self.viewer.setObjectName("mathematicalExplanationText")
        self.viewer.setOpenExternalLinks(False)
        self.viewer.setReadOnly(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(self.title_label)
        layout.addWidget(self.viewer, 1)
        self.set_explanation(None)

    @property
    def explanation(self) -> MathematicalExplanation | None:
        return self._explanation

    def set_explanation(self, explanation: MathematicalExplanation | None) -> None:
        self._explanation = explanation
        if explanation is None:
            self.title_label.setText("Mathematics")
            self.viewer.setPlainText("Select a workflow or example to see the maintained explanation.")
            return
        self.title_label.setText(explanation.title)
        status = explanation.status
        status_line = f"<p><b>Status:</b> {escape(status)}</p>"
        summary = f"<p>{escape(explanation.summary)}</p>"
        sections: list[str] = [status_line, summary]
        if explanation.branch_statuses:
            rows = "".join(
                f"<li><b>{escape(branch_id)}</b>: {escape(branch_status)}</li>"
                for branch_id, branch_status in explanation.branch_statuses
            )
            sections.append(f"<p><b>Selected branch/status:</b></p><ul>{rows}</ul>")
        if explanation.formula_lines:
            formulas = "".join(f"<code>{escape(line)}</code><br>" for line in explanation.formula_lines)
            sections.append(f"<p><b>Formula / construction:</b><br>{formulas}</p>")
        if explanation.normalization:
            sections.append(f"<p><b>Normalization:</b> {escape(explanation.normalization)}</p>")
        if explanation.variable_convention:
            sections.append(f"<p><b>Variable convention:</b> {escape(explanation.variable_convention)}</p>")
        if explanation.output_name:
            sections.append(f"<p><b>Final output:</b> {escape(explanation.output_name)}</p>")
        if explanation.representation_dimension is not None:
            sections.append(f"<p><b>Representation dimension:</b> {explanation.representation_dimension}</p>")
        if explanation.details:
            sections.append("<p><b>Context:</b></p><ul>" + "".join(f"<li>{escape(item)}</li>" for item in explanation.details) + "</ul>")
        if explanation.warnings:
            sections.append(
                '<p><b style="color:#8a4b00">Warnings / boundaries:</b></p><ul>'
                + "".join(f"<li>{escape(item)}</li>" for item in explanation.warnings)
                + "</ul>"
            )
        if explanation.documentation_refs:
            sections.append(
                "<p><b>Read more:</b> "
                + "; ".join(escape(item) for item in explanation.documentation_refs)
                + "</p>"
            )
        self.viewer.setHtml("".join(sections))


__all__ = ["ExplanationPanel"]
