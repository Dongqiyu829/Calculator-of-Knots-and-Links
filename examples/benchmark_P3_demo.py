"""Run the standard braid benchmark catalog on the sl3 fundamental A-type branch."""

from __future__ import annotations

import sys
from pathlib import Path

import sympy as sp

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.catalog.braid_examples import get_default_benchmark_examples
from src.invariants.benchmark import evaluate_catalog
from src.invariants.eyb_invariant import build_sl3_fundamental_eyb_data
from src.rmatrix.sl3_rmatrix import build_sl3_fundamental_rmatrix


def main() -> None:
    """Evaluate the default benchmark catalog on the P3-type branch."""

    q = sp.Symbol("q", nonzero=True)
    entries = evaluate_catalog(
        get_default_benchmark_examples(),
        rmatrix_builder=build_sl3_fundamental_rmatrix,
        eyb_builder=build_sl3_fundamental_eyb_data,
        q=q,
    )

    print("=== P3-type benchmark demo ===")
    for entry in entries:
        print(entry.summary())
        print()


if __name__ == "__main__":
    main()