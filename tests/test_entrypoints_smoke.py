"""Non-interactive smoke coverage for the maintained executable entrypoints."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _run_entrypoint(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *arguments],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_gui_launchers_list_catalog_without_opening_a_window() -> None:
    for script in (
        "examples/demo_launcher_gui.py",
        "examples/demo_launcher_gui_legacy.py",
        "examples/braid_workbench_gui.py",
    ):
        result = _run_entrypoint(script, "--list")
        assert result.returncode == 0, result.stderr
        assert "trefoil" in result.stdout
        assert "figure_eight" in result.stdout


def test_benchmark_entrypoints_expose_cli_help() -> None:
    for script in (
        "examples/run_benchmark_experiments.py",
        "examples/benchmark_lab/run_benchmark_profiles.py",
        "examples/benchmark_lab/run_benchmark_audit.py",
    ):
        result = _run_entrypoint(script, "--help")
        assert result.returncode == 0, result.stderr
        assert "usage:" in result.stdout
