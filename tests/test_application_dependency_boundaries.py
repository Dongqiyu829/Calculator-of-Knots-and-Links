"""Architecture checks for the UI-independent application boundary."""

from __future__ import annotations

import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _imports_gui_module(source_path: Path) -> bool:
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(alias.name == "src.gui" or alias.name.startswith("src.gui.") for alias in node.names):
                return True
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module == "src.gui" or node.module.startswith("src.gui."):
                return True
    return False


def test_workbench_and_services_do_not_depend_on_gui() -> None:
    checked_paths = sorted(
        list((PROJECT_ROOT / "src" / "workbench").glob("*.py"))
        + list((PROJECT_ROOT / "src" / "services").glob("*.py"))
    )
    assert checked_paths
    violations = [path.relative_to(PROJECT_ROOT).as_posix() for path in checked_paths if _imports_gui_module(path)]
    assert violations == []


def test_maintained_frontends_do_not_import_invariant_result_implementation() -> None:
    frontend_paths = (
        PROJECT_ROOT / "src" / "gui" / "demo_launcher.py",
        PROJECT_ROOT / "src" / "gui" / "braid_workbench_app.py",
        PROJECT_ROOT / "src" / "workbench" / "runner.py",
    )
    violations = []
    for path in frontend_paths:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("src.invariants"):
                violations.append(path.relative_to(PROJECT_ROOT).as_posix())
    assert violations == []


def test_workbench_modules_do_not_import_branch_evaluators() -> None:
    evaluator_names = {
        "evaluate_sl2_fundamental_branch",
        "evaluate_sl2_spin1_branch",
        "evaluate_sl3_fundamental_branch",
    }
    violations = []
    for path in sorted((PROJECT_ROOT / "src" / "workbench").glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "src.invariants.branch_registry":
                imported_evaluators = evaluator_names.intersection(alias.name for alias in node.names)
                if imported_evaluators:
                    violations.append(f"{path.relative_to(PROJECT_ROOT).as_posix()}: {sorted(imported_evaluators)}")
    assert violations == []
