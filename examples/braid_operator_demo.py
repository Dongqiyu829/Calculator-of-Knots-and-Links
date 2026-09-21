"""Build and print a global braid operator for a small braid word.

Run this script from the project root with:

    C:/Users/dongqiyu/anaconda3/python.exe examples/braid_operator_demo.py
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
from src.rmatrix.sl2_rmatrix import build_sl2_fundamental_rmatrix


def main() -> None:
    """Construct and print a small braid operator report."""

    q = sp.Symbol("q", nonzero=True)
    local_data = build_sl2_fundamental_rmatrix(q)
    braid_word = BraidWord.from_iterable(
        num_strands=2,
        generators=[1, 1, 1],
        label="trefoil-style braid word",
        notes="This demo only builds the braid operator; it does not yet compute a normalized invariant.",
    )
    operator_data = BraidOperatorBuilder(braid_word=braid_word, rmatrix=local_data).build()

    print("=== Local Braiding Data ===")
    print(local_data.summary())
    print()
    print("=== Braid Word ===")
    print(braid_word.summary())
    print()
    print("=== Global Braid Operator ===")
    print(operator_data.pretty_print())


if __name__ == "__main__":
    main()