"""Qt-native, deterministic braid preview widget for the maintained desktop app."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt, QRectF, Signal
from PySide6.QtGui import QColor, QFont, QImage, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QFileDialog,
    QGraphicsPathItem,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.services.braid_preview import BraidPreviewGeometry, build_braid_preview_geometry, render_braid_preview_svg

class BraidPreviewGraphicsView(QGraphicsView):
    """Vector scene view with wheel zoom and hand-drag panning."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setBackgroundBrush(QColor("#fbfcfe"))
        self.setMinimumHeight(235)

    def wheelEvent(self, event) -> None:  # noqa: N802 - Qt API
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.scale(factor, factor)
        event.accept()

    def fit_to_scene(self) -> None:
        scene = self.scene()
        if scene is None or scene.sceneRect().isNull():
            return
        self.fitInView(scene.sceneRect().adjusted(-12, -12, 12, 12), Qt.AspectRatioMode.KeepAspectRatio)


class BraidPreviewWidget(QWidget):
    """Reusable braid diagram plus metadata and vector export controls."""

    geometryChanged = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("braidPreviewWidget")
        self._geometry: BraidPreviewGeometry | None = None
        self.metadata_label = QLabel("No braid selected. Choose a catalog example or enter a custom word.", self)
        self.metadata_label.setObjectName("braidPreviewMetadata")
        self.metadata_label.setWordWrap(True)
        self.metadata_label.setStyleSheet("color: #475569; padding: 3px 0;")

        self.view = BraidPreviewGraphicsView(self)
        self.view.setObjectName("braidPreviewView")
        self.preview_view = self.view
        self.scene = self.view.scene()
        self.fit_button = QPushButton("Fit", self)
        self.fit_button.setObjectName("fitBraidPreview")
        self.fit_button.clicked.connect(self.fit_to_view)
        self.export_svg_button = QPushButton("SVG…", self)
        self.export_svg_button.setObjectName("exportBraidPreviewSvg")
        self.export_svg_button.clicked.connect(self._choose_svg_path)
        self.export_png_button = QPushButton("PNG…", self)
        self.export_png_button.setObjectName("exportBraidPreviewPng")
        self.export_png_button.clicked.connect(self._choose_png_path)
        controls = QHBoxLayout()
        controls.setContentsMargins(0, 0, 0, 0)
        controls.addWidget(self.fit_button)
        controls.addStretch(1)
        controls.addWidget(self.export_svg_button)
        controls.addWidget(self.export_png_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        layout.addWidget(self.metadata_label)
        layout.addWidget(self.view, 1)
        layout.addLayout(controls)
        self._set_export_enabled(False)

    @property
    def geometry(self) -> BraidPreviewGeometry | None:
        return self._geometry

    def set_message(self, message: str) -> None:
        self._geometry = None
        self.view.scene().clear()
        self.view.scene().setSceneRect(QRectF())
        self.metadata_label.setText(message)
        self._set_export_enabled(False)

    def set_braid_word(self, braid_word: Any, *, viewport_width: int | None = None, viewport_height: int | None = None) -> BraidPreviewGeometry:
        width = viewport_width or max(self.view.viewport().width(), 620)
        height = viewport_height or max(self.view.viewport().height(), 245)
        geometry = build_braid_preview_geometry(braid_word, viewport_width=width, viewport_height=height)
        self._geometry = geometry
        self.metadata_label.setText(f"<b>{braid_word.label or 'Braid preview'}</b> — {geometry.metadata_text}")
        self._populate_scene(geometry)
        self._set_export_enabled(True)
        self.geometryChanged.emit(geometry)
        self.fit_to_view()
        return geometry

    def fit_to_view(self) -> None:
        self.view.fit_to_scene()

    def export_svg(self, path: str | Path) -> Path:
        if self._geometry is None:
            raise ValueError("No braid preview is available to export")
        target = Path(path)
        target.write_text(render_braid_preview_svg(self._geometry), encoding="utf-8")
        return target

    def export_png(self, path: str | Path) -> Path:
        if self._geometry is None:
            raise ValueError("No braid preview is available to export")
        target = Path(path)
        rect = self.view.scene().sceneRect().toRect()
        image = QImage(max(rect.width(), 1), max(rect.height(), 1), QImage.Format.Format_ARGB32)
        image.fill(QColor("#fbfcfe"))
        painter = QPainter(image)
        self.view.scene().render(painter, QRectF(image.rect()), self.view.scene().sceneRect())
        painter.end()
        if not image.save(str(target), "PNG"):
            raise OSError(f"Could not write PNG preview to {target}")
        return target

    def _choose_svg_path(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Export braid preview as SVG", "braid_preview.svg", "SVG files (*.svg)")
        if path:
            self.export_svg(path)

    def _choose_png_path(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Export braid preview as PNG", "braid_preview.png", "PNG files (*.png)")
        if path:
            self.export_png(path)

    def _set_export_enabled(self, enabled: bool) -> None:
        self.fit_button.setEnabled(enabled)
        self.export_svg_button.setEnabled(enabled)
        self.export_png_button.setEnabled(enabled)

    def _populate_scene(self, geometry: BraidPreviewGeometry) -> None:
        scene = self.view.scene()
        scene.clear()
        scene.setSceneRect(0, 0, geometry.width, geometry.height)
        lane_region_right = geometry.width - 180.0
        spacing = (lane_region_right - 56.0) / max(geometry.strand_count - 1, 1)
        guide_pen = QPen(QColor("#cbd5e1"), 1, Qt.PenStyle.DashLine)
        for index in range(geometry.strand_count):
            x = 56.0 + index * spacing
            scene.addLine(x, 52.0, x, geometry.height - 48.0, guide_pen)
            label = scene.addText(str(index + 1))
            label.setDefaultTextColor(QColor("#334155"))
            label.setFont(QFont("Segoe UI", 10))
            label.setPos(x - 4, 16)
            terminal = scene.addText(str(geometry.final_permutation[index]))
            terminal.setDefaultTextColor(QColor("#334155"))
            terminal.setFont(QFont("Segoe UI", 10))
            terminal.setPos(x - 4, geometry.height - 38)

        # Under strokes are inserted first.  The over stroke receives a white
        # halo, making the gap deterministic on every platform.
        for segment in geometry.segments:
            path = QPainterPath()
            first_x, first_y = segment.points[0]
            path.moveTo(first_x, first_y)
            for x, y in segment.points[1:]:
                path.lineTo(x, y)
            item = QGraphicsPathItem(path)
            item.setPen(QPen(QColor(segment.color), 4.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            item.setData(0, segment.role)
            item.setData(1, segment.strand_identity)
            if segment.over:
                halo = QGraphicsPathItem(path)
                halo.setPen(QPen(QColor("#fbfcfe"), 10.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
                scene.addItem(halo)
            scene.addItem(item)

        for crossing in geometry.crossings:
            suffix = "⁻¹" if crossing.generator < 0 else ""
            text = scene.addText(f"{crossing.step_index}: σ{abs(crossing.generator)}{suffix}")
            text.setDefaultTextColor(QColor("#475569"))
            text.setFont(QFont("Segoe UI", 9))
            text.setPos(geometry.width - 160.0, crossing.y - 9)
        if geometry.is_identity:
            text = scene.addText("identity braid")
            text.setDefaultTextColor(QColor("#475569"))
            text.setPos(geometry.width / 2 - 42, geometry.height - 34)


# Descriptive alias for callers that prefer a view-oriented name.
BraidPreviewView = BraidPreviewWidget

__all__ = ["BraidPreviewGraphicsView", "BraidPreviewView", "BraidPreviewWidget"]
