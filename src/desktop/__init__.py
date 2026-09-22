"""Maintained desktop package with lazy UI imports for lightweight CLI paths."""

from __future__ import annotations

from typing import Any


__all__ = ["BraidPreviewWidget", "CustomMatrixWorkflow", "DesktopMainWindow", "InvariantCalculationWorkflow", "launch_desktop_application"]


def __getattr__(name: str) -> Any:
    if name == "BraidPreviewWidget":
        from .braid_preview import BraidPreviewWidget

        return BraidPreviewWidget
    if name == "DesktopMainWindow" or name == "launch_desktop_application":
        from .main_window import DesktopMainWindow, launch_desktop_application

        return {"DesktopMainWindow": DesktopMainWindow, "launch_desktop_application": launch_desktop_application}[name]
    if name == "CustomMatrixWorkflow":
        from .custom_matrix_workflow import CustomMatrixWorkflow

        return CustomMatrixWorkflow
    if name == "InvariantCalculationWorkflow":
        from .invariant_workflow import InvariantCalculationWorkflow

        return InvariantCalculationWorkflow
    raise AttributeError(name)
