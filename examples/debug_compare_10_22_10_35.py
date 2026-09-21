"""Diagnose consistency between formal branch evaluators and the legacy GUI custom path."""

from __future__ import annotations

import sys
from pathlib import Path

import sympy as sp

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.braid.braid_word import BraidWord
from src.gui.demo_launcher import build_custom_braid_word
from src.gui.demo_launcher_legacy import legacy_evaluate_gui_custom_braid
from src.invariants.branch_registry import evaluate_sl2_fundamental_branch, evaluate_sl3_fundamental_branch
from src.invariants.jones_invariant import compute_sl2_jones_compatible_output


Q = sp.Symbol("q", nonzero=True)
CASES = {
    "10_35": {
        "num_strands": 6,
        "generators": (1, -2, -3, 2, 4, -3, -5, 4, -5, 1, -2),
    },
    "10_22": {
        "num_strands": 4,
        "generators": (1, -3, -3, 2, 2, 2, -3, 2, 1, -2, -3),
    },
}


def _format_expr(expr: sp.Expr) -> str:
    return str(expr)


def _build_braid_word(label: str) -> BraidWord:
    case = CASES[label]
    return BraidWord.from_iterable(
        num_strands=case["num_strands"],
        generators=case["generators"],
        label=label,
        notes=f"Debug comparison input for {label}.",
    )


def _build_legacy_custom_braid_word(label: str) -> BraidWord:
    case = CASES[label]
    generator_text = " ".join(str(item) for item in case["generators"])
    return build_custom_braid_word(
        case["num_strands"],
        generator_text,
        label=label,
        notes=f"Legacy GUI custom input for {label}.",
    )


def _print_case_report(label: str) -> dict[str, sp.Expr]:
    braid_word = _build_braid_word(label)
    legacy_braid_word = _build_legacy_custom_braid_word(label)
    strands_match = braid_word.num_strands == legacy_braid_word.num_strands
    generators_match = braid_word.generators == legacy_braid_word.generators
    writhe_match = braid_word.writhe() == legacy_braid_word.writhe()
    sl2_result = compute_sl2_jones_compatible_output(braid_word, q=Q)
    sl3_result = evaluate_sl3_fundamental_branch(braid_word, q=Q)
    legacy_entry = legacy_evaluate_gui_custom_braid(
        braid_word.num_strands,
        " ".join(str(item) for item in braid_word.generators),
        branch_ids=("sl2_fundamental", "sl3_fundamental"),
        q=Q,
    )
    legacy_branch_map = {branch_result.branch_id: branch_result for branch_result in legacy_entry.branch_results}
    formal_sl2_branch = evaluate_sl2_fundamental_branch(braid_word, q=Q)

    print(f"===== {label} =====")
    print(f"Formal braid word: num_strands={braid_word.num_strands}, generators={list(braid_word.generators)}")
    print(f"Legacy GUI braid word: num_strands={legacy_braid_word.num_strands}, generators={list(legacy_braid_word.generators)}")
    print(f"num_strands match: {strands_match}")
    print(f"generators match: {generators_match}")
    print(f"writhe match: {writhe_match}")
    print(f"Writhe values: formal={braid_word.writhe()}, legacy={legacy_braid_word.writhe()}")
    print("sl2 raw trace (exact):", _format_expr(sl2_result.raw_trace))
    print("sl2 raw trace (simplified):", _format_expr(sp.simplify(sl2_result.raw_trace)))
    print("sl2 unreduced P2 (exact):", _format_expr(sl2_result.unreduced_p2_output))
    print("sl2 unreduced P2 (simplified):", _format_expr(sp.simplify(sl2_result.unreduced_p2_output)))
    print("sl2 reduced P2 (exact):", _format_expr(sl2_result.reduced_p2_output))
    print("sl2 reduced P2 (simplified):", _format_expr(sp.simplify(sl2_result.reduced_p2_output)))
    print("sl2 Jones-compatible output (exact):", _format_expr(sl2_result.jones_compatible_output))
    print("sl2 Jones-compatible output (simplified):", _format_expr(sp.simplify(sl2_result.jones_compatible_output)))
    print("sl3 P3-type EYB output (exact):", _format_expr(sl3_result.primary_output))
    print("sl3 P3-type EYB output (simplified):", _format_expr(sp.simplify(sl3_result.primary_output)))
    print(
        "Formal branch evaluator sl2 vs direct Jones layer equal:",
        sp.simplify(formal_sl2_branch.primary_output - sl2_result.jones_compatible_output) == 0,
    )
    print(
        "Path A vs Path B on sl2 fundamental equal:",
        sp.simplify(formal_sl2_branch.primary_output - legacy_branch_map["sl2_fundamental"].primary_output) == 0,
    )
    print(
        "Path A vs Path B on sl3 fundamental equal:",
        sp.simplify(sl3_result.primary_output - legacy_branch_map["sl3_fundamental"].primary_output) == 0,
    )
    print(
        "Legacy custom metadata:",
        legacy_entry.metadata,
    )
    print(
        "Legacy sl2 branch normalization label:",
        legacy_branch_map["sl2_fundamental"].normalization_label,
    )
    print(
        "Legacy sl2 branch primary output label:",
        legacy_branch_map["sl2_fundamental"].primary_output_label,
    )
    print()

    return {
        "sl2": sp.simplify(sl2_result.jones_compatible_output),
        "sl3": sp.simplify(sl3_result.primary_output),
        "legacy_sl2": sp.simplify(legacy_branch_map["sl2_fundamental"].primary_output),
    }


def main() -> int:
    results = {label: _print_case_report(label) for label in ("10_35", "10_22")}

    print("===== Pairwise equality =====")
    print(
        "Formal sl2 Jones-compatible output equal:",
        sp.simplify(results["10_35"]["sl2"] - results["10_22"]["sl2"]) == 0,
    )
    print(
        "Formal sl3 P3-type EYB output equal:",
        sp.simplify(results["10_35"]["sl3"] - results["10_22"]["sl3"]) == 0,
    )
    print(
        "Legacy GUI custom sl2 output equal:",
        sp.simplify(results["10_35"]["legacy_sl2"] - results["10_22"]["legacy_sl2"]) == 0,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())