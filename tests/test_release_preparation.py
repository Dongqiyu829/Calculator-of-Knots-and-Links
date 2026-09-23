"""Release-candidate documentation and workflow contracts for v0.1.2."""

from __future__ import annotations

from pathlib import Path

from src.version import __version__


ROOT = Path(__file__).resolve().parents[1]


def test_release_candidate_version_and_notes_are_bilingual_and_conservative() -> None:
    notes = (ROOT / "docs" / "RELEASE_NOTES_0.1.2.md").read_text(encoding="utf-8")
    assert __version__ == "0.1.2"
    assert "## English" in notes
    assert "## 中文" in notes
    for phrase in (
        "desktop usability hotfix release candidate",
        "Braid setup / preview",
        "Calculation / results",
        "Manual braid input",
        "tabified on the right and closed by default",
        "No mathematical behavior changes",
    ):
        assert phrase in notes
    assert "v0.1.1" not in notes


def test_readme_and_distribution_describe_published_state_and_stable_assets() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    distribution = (ROOT / "docs" / "DISTRIBUTION.md").read_text(encoding="utf-8")
    assert "v0.1.1 is the latest published release" in readme
    assert "source tree is prepared as the `0.1.2` release candidate" in readme
    assert "`v0.1.1` tag and GitHub Release remain" in distribution
    assert "maintained application version is `0.1.2`" in distribution
    for asset in (
        "Calculator-of-Knots-and-Links-Windows-x64-Setup.exe",
        "Calculator-of-Knots-and-Links-Windows-x64-Portable.zip",
        "SHA256SUMS.txt",
    ):
        assert f"releases/latest/download/{asset}" in readme


def test_manual_release_dispatch_is_non_publishing_and_uses_candidate_example() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    assert "non-publishing dry run, e.g. v0.1.2" in workflow
    assert "if: github.event_name == 'workflow_dispatch'" in workflow
    assert "if: github.event_name == 'push' && startsWith(github.ref, 'refs/tags/v')" in workflow
    assert "gh release create" in workflow
