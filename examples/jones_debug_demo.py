"""Run the sl2 fundamental Jones-debug comparison on the default reference scaffold."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.invariants.jones_debug import compare_current_p2_with_jones
from src.invariants.jones_reference_cases import get_default_jones_reference_cases


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
            if len(cast_diffs) < 2 and candidate.difference_expression is not None:
                cast_diffs.append(str(candidate.difference_expression))
    return summary


def print_candidate_summary(title: str, candidates: tuple) -> None:
    print(title)
    if not candidates:
        print("  none")
        return
    grouped = summarize_candidates(candidates)
    for mode, bucket in grouped.items():
        print(f"  - mode={mode}, tested={bucket['tested']}")
        if bucket["missing_target"]:
            print("    target missing: monomial search skipped")
            continue
        exact_factors = bucket["exact_factors"]
        sample_differences = bucket["sample_differences"]
        print("    exact factors: none" if not exact_factors else f"    exact factors: {exact_factors}")
        if sample_differences:
            print(f"    sample differences: {sample_differences}")


def print_match_list(title: str, candidates: tuple) -> None:
    print(title)
    if not candidates:
        print("  none")
        return
    for candidate in candidates:
        print(f"  - mode={candidate.variable_map_label}, factor={candidate.monomial_factor}")
        if candidate.notes:
            print(f"    notes={candidate.notes}")


def main() -> None:
    print("=== Jones debug demo for current sl2 fundamental P2-type output ===")
    print("This demo diagnoses structural relations to editable Jones-reference slots.")
    print()

    for case in get_default_jones_reference_cases():
        result = compare_current_p2_with_jones(case)

        print(f"########## {result.example_label} ##########")
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

        print_candidate_summary("tried variable substitutions and monomial shifts on the reduced layer:", result.tried_candidates)
        print()
        print_match_list("exact matches on the reduced layer:", result.exact_matches)
        print()
        print_match_list("near matches on the reduced layer:", result.near_matches)
        print()
        print("diagnosis summary:")
        print(result.diagnosis_summary)
        print("notes:")
        print(result.notes)
        print()


if __name__ == "__main__":
    main()