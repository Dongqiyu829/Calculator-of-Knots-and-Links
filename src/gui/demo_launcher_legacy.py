"""Legacy fast GUI entrypoint preserved alongside the newer candidate multibranch GUI."""

from __future__ import annotations

import argparse
from dataclasses import dataclass

import sympy as sp
import tkinter as tk

from src.braid.braid_word import BraidWord
from src.catalog.braid_examples import get_braid_example
from src.invariants.branch_formatter import format_catalog_benchmark
from src.invariants.legacy_branch_registry import (
    LEGACY_SL2_3D_USER_FACING_NAME,
    evaluate_legacy_branches,
)
from src.invariants.legacy_multibranch_benchmark import (
    LegacyMultiBranchBenchmarkEntry,
    evaluate_legacy_example_across_branches,
)

from . import demo_launcher as current_gui


LEGACY_PROGRAM_STATUS_TEXT = (
    "Quick start (legacy fast mode):\n"
    "1. Choose a built-in example or switch to Custom braid.\n"
    "2. Click Evaluate example or Apply custom braid to compute invariants.\n\n"
    "This preserved program keeps the older fast raw/projector-aware behavior for the sl2 3D 9x9 branch.\n"
    "Use this mode when the newer colored Jones candidate branch is too slow for quick checks."
)


LEGACY_GUI_BRANCH_SPECS = (
    current_gui.GuiBranchSpec(
        branch_id="sl2_fundamental",
        title="Jones / sl2 fundamental",
        subtitle="Use this branch when you want the current Jones-compatible polynomial.",
        accent_color=current_gui.ACCENT_COLOR,
        user_hint="Primary output here = current Jones-compatible comparison output.",
    ),
    current_gui.GuiBranchSpec(
        branch_id="sl3_fundamental",
        title="sl3 fundamental",
        subtitle="Current formal sl3 branch for cross-Lie-algebra comparison.",
        accent_color=current_gui.SUCCESS_COLOR,
        user_hint="Primary output here = current formal sl3 comparison branch.",
    ),
    current_gui.GuiBranchSpec(
        branch_id="sl2_spin1",
        title=LEGACY_SL2_3D_USER_FACING_NAME,
        subtitle="Legacy fast raw/projector-aware mode for the sl2 3D 9x9 branch, preserved as a backup program.",
        accent_color=current_gui.EXPLORATORY_COLOR,
        user_hint="Primary output here = raw trace in legacy fast mode. Use this path for quicker exploratory checks.",
    ),
)


def legacy_evaluate_gui_example(
    example_label: str,
    *,
    branch_ids: tuple[str, ...] | list[str] | None = None,
    q: sp.Expr | None = None,
) -> LegacyMultiBranchBenchmarkEntry:
    example = get_braid_example(example_label)
    return LegacyMultiBranchBenchmarkEntry(
        example_label=example.label,
        branch_results=tuple(evaluate_legacy_branches(example, branch_ids=branch_ids, q=q)),
        notes=example.notes,
        metadata={
            "expected_components": example.expected_components,
            "expected_crossing_count": example.expected_crossing_count,
            "example_metadata": dict(example.metadata),
            "program_mode": "legacy_fast",
            "selected_branch_ids": list(branch_ids) if branch_ids is not None else None,
        },
    )


def legacy_evaluate_gui_braid_word(
    braid_word: BraidWord,
    *,
    branch_ids: tuple[str, ...] | list[str] | None = None,
    q: sp.Expr | None = None,
) -> LegacyMultiBranchBenchmarkEntry:
    return LegacyMultiBranchBenchmarkEntry(
        example_label=braid_word.label or "custom_braid",
        branch_results=tuple(evaluate_legacy_branches(braid_word, branch_ids=branch_ids, q=q)),
        notes=braid_word.notes,
        metadata={
            "input_mode": "custom",
            "braid_word": braid_word.to_dict(),
            "program_mode": "legacy_fast",
            "selected_branch_ids": list(branch_ids) if branch_ids is not None else None,
        },
    )


def legacy_evaluate_gui_custom_braid(
    num_strands: int,
    generator_text: str,
    *,
    branch_ids: tuple[str, ...] | list[str] | None = None,
    q: sp.Expr | None = None,
) -> LegacyMultiBranchBenchmarkEntry:
    braid_word = current_gui.build_custom_braid_word(num_strands, generator_text)
    return legacy_evaluate_gui_braid_word(braid_word, branch_ids=branch_ids, q=q)


def legacy_build_entry_summary(entry: LegacyMultiBranchBenchmarkEntry) -> str:
    braid_word = entry.branch_results[0].braid_word
    lines = [
        f"Source mode: {entry.metadata.get('input_mode', 'catalog')}",
        f"Program mode: {entry.metadata.get('program_mode', 'legacy_fast')}",
        f"Label: {entry.example_label}",
        f"Number of strands: {braid_word.num_strands}",
        f"Generators: {list(braid_word.generators)}",
        f"Word: {braid_word.word_string()}",
        f"Writhe: {braid_word.writhe()}",
    ]
    if entry.notes:
        lines.append(f"Notes: {entry.notes}")
    lines.extend(
        (
            "",
            "How to read the current outputs:",
            "- Jones-compatible polynomial: read the primary output in Jones / sl2 fundamental.",
            "- sl3 comparison output: read the primary output in sl3 fundamental.",
            f"- Legacy sl2 3D raw output: read the primary output in {LEGACY_SL2_3D_USER_FACING_NAME}.",
        )
    )
    return "\n".join(lines)


def _apply_legacy_overrides() -> None:
    current_gui.GUI_BRANCH_SPECS = LEGACY_GUI_BRANCH_SPECS
    current_gui.PROGRAM_STATUS_TEXT = LEGACY_PROGRAM_STATUS_TEXT
    current_gui.get_gui_branch_specs = lambda: LEGACY_GUI_BRANCH_SPECS
    current_gui.build_program_status_text = lambda: LEGACY_PROGRAM_STATUS_TEXT
    current_gui.evaluate_gui_example = legacy_evaluate_gui_example
    current_gui.evaluate_gui_braid_word = legacy_evaluate_gui_braid_word
    current_gui.evaluate_gui_custom_braid = legacy_evaluate_gui_custom_braid
    current_gui.build_entry_summary = legacy_build_entry_summary


class LegacyDemoLauncherApp(current_gui.DemoLauncherApp):
    def __init__(self, root: tk.Tk) -> None:
        _apply_legacy_overrides()
        super().__init__(root)
        self.root.title("Quantum Group Knot Legacy Fast GUI")
        self.status_var.set("Legacy fast GUI ready. This mode keeps the older raw/projector-aware sl2 3D branch.")


def launch_legacy_demo_gui() -> None:
    root = tk.Tk()
    LegacyDemoLauncherApp(root)
    root.mainloop()


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Launch or inspect the legacy fast multibranch GUI entrypoint.")
    parser.add_argument("--list", action="store_true", help="List the built-in catalog examples shown by the legacy GUI.")
    parser.add_argument("--run", metavar="EXAMPLE_LABEL", help="Print one built-in multibranch report in legacy CLI mode.")
    parser.add_argument("--custom-strands", type=int, help="Evaluate one custom braid word in legacy CLI mode.")
    parser.add_argument("--custom-generators", default="", help="Space- or comma-separated Artin generators for --custom-strands.")
    parser.add_argument(
        "--view",
        choices=current_gui.get_gui_view_modes(),
        default="formatter",
        help="Choose formatter or raw report output for legacy CLI inspection.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)

    if args.list:
        for label in current_gui.get_gui_example_labels():
            print(label)
        return 0

    if args.run and args.custom_strands is not None:
        raise SystemExit("Use either --run for a built-in example or --custom-strands/--custom-generators for a custom braid.")

    if args.run:
        entry = legacy_evaluate_gui_example(args.run, q=sp.Symbol("q", nonzero=True))
        print(current_gui.render_entry_report(entry, view_mode=args.view))
        return 0

    if args.custom_strands is not None:
        entry = legacy_evaluate_gui_custom_braid(args.custom_strands, args.custom_generators, q=sp.Symbol("q", nonzero=True))
        print(current_gui.render_entry_report(entry, view_mode=args.view))
        return 0

    launch_legacy_demo_gui()
    return 0