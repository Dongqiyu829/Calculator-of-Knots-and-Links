"""Compute raw closure traces for a few braid-word examples.

Run this script from the project root with:

    C:/Users/dongqiyu/anaconda3/python.exe examples/raw_trace_demo.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import sympy as sp

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.braid.braid_operator import BraidOperatorBuilder
from src.braid.braid_word import BraidWord
from src.invariants.quantum_trace import compute_raw_closure_trace
from src.rmatrix.sl2_rmatrix import build_sl2_fundamental_rmatrix


def run_example(title: str, braid_word: BraidWord) -> None:
    """Build the braid operator and print the raw trace report for one example."""

    q = sp.Symbol("q", nonzero=True)
    local_data = build_sl2_fundamental_rmatrix(q)
    operator_data = BraidOperatorBuilder(braid_word=braid_word, rmatrix=local_data).build()
    result = compute_raw_closure_trace(operator_data)

    print(f"=== {title} ===")
    print("-- Braid Word Summary --")
    print(braid_word.summary())
    print()
    print("-- Global Braid Operator Summary --")
    print(operator_data.summary())
    print()
    print("-- Raw Trace Result Summary --")
    print(result.summary())
    print()
    print(f"Raw expression: {result.raw_expression}")
    print(f"Convention warning: {result.convention_notes}")
    print(f"Framing warning: {result.framing_notes}")
    print()


def main() -> None:
    """Run the first-stage raw trace demo on two braid words."""

    example_one = BraidWord.from_iterable(
        num_strands=2,
        generators=[1, 1, 1],
        label="2-strand cubic braid",
        notes="Trefoil-style braid word used for the first raw trace experiment.",
    )
    example_two = BraidWord.from_iterable(
        num_strands=3,
        generators=[1, -2, 1],
        label="3-strand mixed-sign braid",
        notes="Three-strand example used to test mixed positive and negative generators.",
    )

    run_example("Example 1: sl2 fundamental with [1, 1, 1]", example_one)
    run_example("Example 2: sl2 fundamental with [1, -2, 1]", example_two)


if __name__ == "__main__":
    main()