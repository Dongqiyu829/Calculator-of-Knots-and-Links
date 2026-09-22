"""Release-candidate documentation and workflow contracts for v0.1.1."""

from __future__ import annotations

from pathlib import Path

from src.version import __version__


ROOT = Path(__file__).resolve().parents[1]


def test_release_candidate_version_and_notes_are_bilingual_and_conservative() -> None:
    notes = (ROOT / "docs" / "RELEASE_NOTES_0.1.1.md").read_text(encoding="utf-8")
    assert __version__ == "0.1.1"
    assert "## English" in notes
    assert "## 中文" in notes
    for phrase in (
        "redesigned Qt-native braid visualization",
        "curated examples",
        "deterministic `.knotcalc.json`",
        "Mathematics / How it works",
        "bilingual offline User Guide",
        "sl2 fundamental remains the formal Jones-compatible branch",
        "sl3 fundamental remains the formal P3/A2-style branch",
        "sl2 spin-1 remains a candidate branch",
        "operator-only",
    ):
        assert phrase in notes
    assert "tag is created" in notes


def test_readme_and_distribution_describe_pre_tag_state_and_stable_assets() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    distribution = (ROOT / "docs" / "DISTRIBUTION.md").read_text(encoding="utf-8")
    assert "0.1.1` release candidate" in readme
    assert "latest published release remains **v0.1.0**" in readme
    assert "`v0.1.1` tag or publish" in distribution
    assert "latest published release remains `v0.1.0`" in distribution
    for asset in (
        "Calculator-of-Knots-and-Links-Windows-x64-Setup.exe",
        "Calculator-of-Knots-and-Links-Windows-x64-Portable.zip",
        "SHA256SUMS.txt",
    ):
        assert f"releases/latest/download/{asset}" in readme


def test_manual_release_dispatch_is_non_publishing_and_uses_candidate_example() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    assert "non-publishing dry run, e.g. v0.1.1" in workflow
    assert "if: github.event_name == 'workflow_dispatch'" in workflow
    assert "if: github.event_name == 'push' && startsWith(github.ref, 'refs/tags/v')" in workflow
    assert "gh release create" in workflow
