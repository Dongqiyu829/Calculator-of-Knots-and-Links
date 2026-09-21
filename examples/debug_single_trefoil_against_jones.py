"""Run one focused Jones-debug comparison on the 2-strand cubic braid."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.invariants.jones_debug import compare_current_p2_with_jones
from src.invariants.jones_reference_cases import get_jones_reference_case


def summarize_candidates(candidates: tuple) -> dict[str, dict[str, object]]:
    summary: dict[str, dict[str, object]] = {}
    for candidate in candidates:
        mode = candidate.variable_map_label or "unlabeled"
        if mode not in summary:
            summary[mode] = {
                "tested": 0,
                "exact_factors": [],
                "sample_differences": [],
                "missing_target": False,
            }
        bucket = summary[mode]
        bucket["tested"] = int(bucket["tested"]) + 1
        if candidate.monomial_factor is None:
            bucket["missing_target"] = True
        elif candidate.matched_exactly:
            cast_list = bucket["exact_factors"]
            assert isinstance(cast_list, list)
            cast_list.append(str(candidate.monomial_factor))
        else:
            cast_diffs = bucket["sample_differences"]
            assert isinstance(cast_diffs, list)
            if len(cast_diffs) < 3 and candidate.difference_expression is not None:
                cast_diffs.append(str(candidate.difference_expression))
    return summary


def main() -> None:
    case = get_jones_reference_case("trefoil")
    result = compare_current_p2_with_jones(case)

    print("=== Single-case Jones debug: trefoil ===")
    print(f"example label: {result.example_label}")
    print(f"braid word: {case.braid_word.word_string()}")
    print(f"raw trace: {result.current_raw_trace}")
    print(f"current P2-type EYB output (unreduced): {result.current_p2_output}")
    print(f"current P2 unknot normalization: {result.current_p2_unknot_normalization}")
    print(f"current reduced P2-type output: {result.current_reduced_p2_output}")
    print("support signature of current unreduced output:")
    print(result.support_current.summary())
    print()
    print("support signature of current reduced output:")
    print(result.support_current_reduced.summary())
    print()
    print(
        "target Jones expression: missing reference slot"
        if result.target_expression is None
        else f"target Jones expression: {result.target_expression}"
    )
    print(
        "target Jones expression in q: unavailable"
        if result.target_expression_in_q is None
        else f"target Jones expression in q: {result.target_expression_in_q}"
    )
    if result.support_target is None:
        print("support signature of target: unavailable")
    else:
        print("support signature of target:")
        print(result.support_target.summary())
    print()
    print("tried substitutions / monomial shifts on the reduced layer:")
    for mode, bucket in summarize_candidates(result.tried_candidates).items():
        print(f"- mode={mode}, tested={bucket['tested']}")
        if bucket["missing_target"]:
            print("  target missing: monomial search skipped")
        else:
            print("  exact factors: none" if not bucket["exact_factors"] else f"  exact factors: {bucket['exact_factors']}")
            if bucket["sample_differences"]:
                print(f"  sample differences: {bucket['sample_differences']}")
    print()
    print("exact matches on the reduced layer:")
    if result.exact_matches:
        for candidate in result.exact_matches:
            print(candidate.summary())
            print()
    else:
        print("none")
    print()
    print("diagnosis summary:")
    print(result.diagnosis_summary)
    print("notes:")
    print(result.notes)


if __name__ == "__main__":
    main()