"""Static contract checks for the Windows installer and release landing page."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSET_NAMES = (
    "Calculator-of-Knots-and-Links-Windows-x64-Setup.exe",
    "Calculator-of-Knots-and-Links-Windows-x64-Portable.zip",
    "SHA256SUMS.txt",
)


def test_inno_setup_is_per_user_and_points_at_verified_onedir_bundle() -> None:
    script = (ROOT / "packaging" / "windows" / "installer.iss").read_text(encoding="utf-8")
    assert "DefaultDirName={localappdata}\\Programs\\{#MyAppName}" in script
    assert "PrivilegesRequired=lowest" in script
    assert "ArchitecturesAllowed=x64compatible" in script
    assert "Source: \"{#MyAppSource}\\*\"" in script
    assert "OutputBaseFilename=Calculator-of-Knots-and-Links-Windows-x64-Setup" in script
    assert "AppPublisherURL=https://github.com/Dongqiyu829/Calculator-of-Knots-and-Links" in script
    assert "AppSupportURL=https://github.com/Dongqiyu829/Calculator-of-Knots-and-Links/issues" in script
    assert "Name: \"{group}\\{#MyAppName}\"" in script
    assert "uninstall" not in script.lower() or "Uninstallable=yes" in script
    assert "skipifsilent" in script


def test_windows_build_workflow_uses_shared_orchestration_and_stable_assets() -> None:
    workflow = (ROOT / ".github" / "workflows" / "windows-build.yml").read_text(encoding="utf-8")
    assert "packaging\\windows\\build.ps1" in workflow
    assert "choco install innosetup" in workflow
    for asset in ASSET_NAMES:
        assert asset in workflow


def test_release_workflow_keeps_dry_run_non_publishing_and_publishes_three_assets() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    assert "python -m src.version --check-tag" in workflow
    assert "packaging\\windows\\build.ps1" in workflow
    assert "if: github.event_name == 'workflow_dispatch'" in workflow
    assert "if: github.event_name == 'push' && startsWith(github.ref, 'refs/tags/v')" in workflow
    assert "non-publishing dry run, e.g. v0.1.2" in workflow
    for asset in ASSET_NAMES:
        assert asset in workflow


def test_readme_has_bilingual_latest_download_contract() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "## Download Windows App / 下载 Windows 应用" in readme
    assert "### 🌟 Download Windows Installer / 下载 Windows 安装版" in readme
    assert "Windows 10/11 x64" in readme
    assert "无需 Python、Conda、Git 或编译器" in readme
    for asset in ASSET_NAMES:
        expected = (
            "https://github.com/Dongqiyu829/Calculator-of-Knots-and-Links/"
            f"releases/latest/download/{asset}"
        )
        assert expected in readme


def test_build_script_covers_packaged_smokes_and_artifact_checks() -> None:
    script = (ROOT / "packaging" / "windows" / "build.ps1").read_text(encoding="utf-8")
    assert "--smoke-test" in script
    assert "--version" in script
    assert "$PackagedVersion -ne $Version" in script
    assert "$PortableVersion -ne $Version" in script
    assert "Expand-Archive" in script
    assert "Get-FileHash" in script
    assert "Missing expected installer artifact" in script
    for asset in ASSET_NAMES:
        assert asset in script


def test_installer_version_is_injected_not_hard_coded() -> None:
    script = (ROOT / "packaging" / "windows" / "installer.iss").read_text(encoding="utf-8")
    build = (ROOT / "packaging" / "windows" / "build.ps1").read_text(encoding="utf-8")
    assert '#define MyAppVersion "0.1.1"' not in script
    assert "AppVersion={#MyAppVersion}" in script
    assert "/DMyAppVersion=$Version" in build
