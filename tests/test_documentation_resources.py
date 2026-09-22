"""Offline documentation and screenshot-refresh contract checks."""

from __future__ import annotations

from pathlib import Path

from src.services import documentation_resource_path, list_documentation_resources, read_documentation


ROOT = Path(__file__).resolve().parents[1]


def test_help_resources_exist_in_source_and_are_readable() -> None:
    resource_ids = {resource.resource_id for resource in list_documentation_resources()}
    assert {"user_guide", "mathematical_implementation"} <= resource_ids
    assert documentation_resource_path("user_guide").is_file()
    guide = read_documentation("user_guide")
    assert "# User Guide / 用户指南" in guide
    assert "Custom R/check-R workflow" in guide


def test_real_app_screenshot_refresh_path_is_documented() -> None:
    script = ROOT / "tools" / "capture_desktop_screenshots.py"
    notes = ROOT / "docs" / "images" / "README.md"
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert script.is_file()
    assert notes.is_file()
    assert "capture_desktop_screenshots.py" in readme
    assert "real maintained PySide6 application" in notes.read_text(encoding="utf-8")
