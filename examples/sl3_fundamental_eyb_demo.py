"""Compute one EYB-normalized output for the sl3 fundamental branch."""

from __future__ import annotations

import sys
from pathlib import Path

import sympy as sp

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.braid.braid_operator import BraidOperatorBuilder
from src.braid.braid_word import BraidWord
from src.invariants.eyb_invariant import build_sl3_fundamental_eyb_data, compute_eyb_invariant
from src.rmatrix.sl3_rmatrix import build_sl3_fundamental_rmatrix


def main() -> None:
    """Compute and print one sl3 fundamental EYB-normalized example."""

    q = sp.Symbol("q", nonzero=True)
    braid_word = BraidWord.from_iterable(num_strands=2, generators=[1, 1, 1], label="2-strand cubic braid")
    rdata = build_sl3_fundamental_rmatrix(q)
    eyb_data = build_sl3_fundamental_eyb_data(q)
    operator_data = BraidOperatorBuilder(braid_word=braid_word, rmatrix=rdata).build()
    result = compute_eyb_invariant(operator_data, eyb_data=eyb_data)

    print("=== sl3 fundamental EYB demo ===")
    print(braid_word.summary())
    print()
    print(eyb_data.summary())
    print()
    print(result.summary())


if __name__ == "__main__":
    main()
