"""Compare the A-type EYB outputs for the sl2 and sl3 fundamental branches."""

from __future__ import annotations

import sys
from pathlib import Path

import sympy as sp

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.braid.braid_operator import BraidOperatorBuilder
from src.braid.braid_word import BraidWord
from src.invariants.eyb_invariant import (
    build_sl2_fundamental_eyb_data,
    build_sl3_fundamental_eyb_data,
    compute_eyb_invariant,
)
from src.rmatrix.sl2_rmatrix import build_sl2_fundamental_rmatrix
from src.rmatrix.sl3_rmatrix import build_sl3_fundamental_rmatrix


def print_result_block(title: str, braid_word: BraidWord, rdata, eyb_data) -> None:
    """Compute and print one A-type EYB result block."""

    operator_data = BraidOperatorBuilder(braid_word=braid_word, rmatrix=rdata).build()
    result = compute_eyb_invariant(operator_data, eyb_data=eyb_data)

    print(f"=== {title} ===")
    print(f"Braid word: {braid_word.word_string()}")
    print(f"Raw trace: {result.raw_closure_trace}")
    print(f"EYB-normalized expression: {result.eyb_normalized_expression}")
    print(f"alpha: {eyb_data.alpha}")
    print(f"beta: {eyb_data.beta}")
    print(f"mu: {eyb_data.mu}")
    print(f"Convention notes: {result.convention_notes}")
    print()


def main() -> None:
    """Compare P2-type and P3-type EYB outputs on the same braid word."""

    q = sp.Symbol("q", nonzero=True)
    braid_word = BraidWord.from_iterable(
        num_strands=2,
        generators=[1, 1, 1],
        label="2-strand cubic braid",
        notes="Shared braid word for comparing the P2-type and P3-type EYB outputs.",
    )

    print_result_block(
        "P2-type EYB output",
        braid_word,
        build_sl2_fundamental_rmatrix(q),
        build_sl2_fundamental_eyb_data(q),
    )
    print_result_block(
        "P3-type EYB output",
        braid_word,
        build_sl3_fundamental_rmatrix(q),
        build_sl3_fundamental_eyb_data(q),
    )


if __name__ == "__main__":
    main()