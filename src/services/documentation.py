"""Offline documentation resources shared by source and frozen builds."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class DocumentationResource:
    resource_id: str
    title: str
    relative_path: str
    summary: str


DOCUMENTATION_RESOURCES: tuple[DocumentationResource, ...] = (
    DocumentationResource(
        resource_id="user_guide",
        title="User Guide / 用户指南",
        relative_path="docs/USER_GUIDE.md",
        summary="Installation, workflows, validation, projects, exports, and uninstall guidance.",
    ),
    DocumentationResource(
        resource_id="mathematical_implementation",
        title="Mathematical Implementation",
        relative_path="docs/MATHEMATICAL_IMPLEMENTATION.md",
        summary="The maintained end-to-end implementation and convention record.",
    ),
)


def list_documentation_resources() -> tuple[DocumentationResource, ...]:
    return DOCUMENTATION_RESOURCES


def get_documentation_resource(resource_id: str) -> DocumentationResource:
    for resource in DOCUMENTATION_RESOURCES:
        if resource.resource_id == resource_id:
            return resource
    raise KeyError(f"Unknown documentation resource '{resource_id}'.")


def _resource_root() -> Path:
    frozen_root = getattr(sys, "_MEIPASS", None)
    if frozen_root:
        return Path(frozen_root)
    return Path(__file__).resolve().parents[2]


def documentation_resource_path(resource_id: str) -> Path:
    """Resolve a bundled documentation path without network access."""

    resource = get_documentation_resource(resource_id)
    root = _resource_root()
    path = root / resource.relative_path
    if path.is_file():
        return path
    raise FileNotFoundError(f"Documentation resource is not bundled: {resource.relative_path}")


def read_documentation(resource_id: str) -> str:
    return documentation_resource_path(resource_id).read_text(encoding="utf-8")


__all__ = [
    "DOCUMENTATION_RESOURCES",
    "DocumentationResource",
    "documentation_resource_path",
    "get_documentation_resource",
    "list_documentation_resources",
    "read_documentation",
]
