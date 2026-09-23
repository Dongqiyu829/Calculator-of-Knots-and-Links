"""Release documentation and workflow contracts for v0.1.4."""

from __future__ import annotations

from pathlib import Path

from src.version import __version__


ROOT = Path(__file__).resolve().parents[1]


def test_release_version_and_notes_are_bilingual_and_conservative() -> None:
    notes = (ROOT / "docs" / "RELEASE_NOTES_0.1.4.md").read_text(encoding="utf-8")
    historical = (ROOT / "docs" / "RELEASE_NOTES_0.1.3.md").read_text(encoding="utf-8")
    assert __version__ == "0.1.4"
    assert "## English" in notes
    assert "## 中文" in notes
    for phrase in (
        "Fast scalar",
        "Temperley–Lieb",
        "Qt GUI",
        "Custom R/check-R operator",
        "No mathematical convention",
    ):
        assert phrase in notes
    assert "v0.1.3" in historical


def test_readme_and_distribution_describe_maintained_release_line_and_stable_assets() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    distribution = (ROOT / "docs" / "DISTRIBUTION.md").read_text(encoding="utf-8")
    assert "maintained application version is **v0.1.4**" in readme
    assert "当前维护版本为 v0.1.4" in readme
    assert "maintained application version is `0.1.4`" in distribution
    for asset in (
        "Calculator-of-Knots-and-Links-Windows-x64-Setup.exe",
        "Calculator-of-Knots-and-Links-Windows-x64-Portable.zip",
        "SHA256SUMS.txt",
    ):
        assert f"releases/latest/download/{asset}" in readme


def test_manual_release_dispatch_is_non_publishing_and_tag_publish_uses_notes_file() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    assert "non-publishing dry run, e.g. v0.1.4" in workflow
    assert "if: github.event_name == 'workflow_dispatch'" in workflow
    assert "if: github.event_name == 'push' && startsWith(github.ref, 'refs/tags/v')" in workflow
    assert "RELEASE_NOTES_$env:RELEASE_VERSION.md" in workflow
    assert "gh release create" in workflow
    assert "gh release upload" in workflow
    assert "--clobber" in workflow
