"""Demonstrate empirical conjugation and stabilization checks on small catalog examples."""

from __future__ import annotations

import sys
from pathlib import Path

import sympy as sp

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.catalog.braid_examples import get_braid_example
from src.invariants.markov_checks import check_conjugation_invariance, check_stabilization_invariance
from src.invariants.eyb_invariant import build_sl2_fundamental_eyb_data, build_sl3_fundamental_eyb_data
from src.rmatrix.sl2_rmatrix import build_sl2_fundamental_rmatrix
from src.rmatrix.sl3_rmatrix import build_sl3_fundamental_rmatrix


def print_block(title: str) -> None:
    """Print a simple title separator."""

    print(f"=== {title} ===")


def main() -> None:
    """Run empirical Markov regression checks on one 2-strand and one 3-strand example."""

    q = sp.Symbol("q", nonzero=True)

    two_strand_example = get_braid_example("trefoil")
    two_strand_braid = two_strand_example.to_braid_word()
    print_block("2-strand Markov checks on the P2-type branch")
    print(two_strand_example.summary())
    print()
    conjugation_two = check_conjugation_invariance(
        two_strand_braid,
        eta_generators=(1,),
        rmatrix_builder=build_sl2_fundamental_rmatrix,
        eyb_builder=build_sl2_fundamental_eyb_data,
        q=q,
    )
    stabilization_two = check_stabilization_invariance(
        two_strand_braid,
        rmatrix_builder=build_sl2_fundamental_rmatrix,
        eyb_builder=build_sl2_fundamental_eyb_data,
        q=q,
    )
    print(conjugation_two.summary())
    print()
    print(conjugation_two.raw_trace_comparison.summary())
    print()
    print(conjugation_two.eyb_comparison.summary())
    print()
    print(stabilization_two.summary())
    print()
    print(stabilization_two.raw_positive_comparison.summary())
    print()
    print(stabilization_two.raw_negative_comparison.summary())
    print()
    print(stabilization_two.eyb_positive_comparison.summary())
    print()
    print(stabilization_two.eyb_negative_comparison.summary())
    print()

    three_strand_example = get_braid_example("figure_eight")
    three_strand_braid = three_strand_example.to_braid_word()
    print_block("3-strand Markov checks on the P3-type branch")
    print(three_strand_example.summary())
    print()
    conjugation_three = check_conjugation_invariance(
        three_strand_braid,
        eta_generators=(1, 2),
        rmatrix_builder=build_sl3_fundamental_rmatrix,
        eyb_builder=build_sl3_fundamental_eyb_data,
        q=q,
    )
    stabilization_three = check_stabilization_invariance(
        three_strand_braid,
        rmatrix_builder=build_sl3_fundamental_rmatrix,
        eyb_builder=build_sl3_fundamental_eyb_data,
        q=q,
    )
    print(conjugation_three.summary())
    print()
    print(conjugation_three.raw_trace_comparison.summary())
    print()
    print(conjugation_three.eyb_comparison.summary())
    print()
    print(stabilization_three.summary())
    print()
    print(stabilization_three.raw_positive_comparison.summary())
    print()
    print(stabilization_three.raw_negative_comparison.summary())
    print()
    print(stabilization_three.eyb_positive_comparison.summary())
    print()
    print(stabilization_three.eyb_negative_comparison.summary())


if __name__ == "__main__":
    main()