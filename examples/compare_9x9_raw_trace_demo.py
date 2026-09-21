"""Compare raw closure traces for the two first-stage 9 x 9 local models."""

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
from src.rmatrix.sl2_rmatrix import build_sl2_spin1_rmatrix
from src.rmatrix.sl3_rmatrix import build_sl3_fundamental_rmatrix


def print_result_block(title: str, rdata, braid_word: BraidWord) -> None:
    """Build one raw closure trace and print the comparison fields."""

    operator_data = BraidOperatorBuilder(braid_word=braid_word, rmatrix=rdata).build()
    result = compute_raw_closure_trace(operator_data)

    print(f"=== {title} ===")
    print(f"Braid word: {braid_word.word_string()}")
    print(f"Representation: {rdata.rep.name()}")
    print(f"Total operator dimension: {operator_data.total_dimension}")
    print(f"Raw expression: {result.raw_expression}")
    print(f"Convention warning: {result.convention_notes}")
    print()


def main() -> None:
    """Run one small raw-trace comparison for the two 9 x 9 local models."""

    q = sp.Symbol("q", nonzero=True)
    braid_word = BraidWord.from_iterable(
        num_strands=2,
        generators=[1, 1],
        label="2-strand square braid",
        notes="Used only for a first raw-trace comparison between the two 9 x 9 local models.",
    )

    print_result_block("sl3 fundamental", build_sl3_fundamental_rmatrix(q), braid_word)
    print_result_block("sl2 spin1", build_sl2_spin1_rmatrix(q), braid_word)


if __name__ == "__main__":
    main()