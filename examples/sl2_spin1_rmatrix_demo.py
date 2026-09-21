"""Print the first-stage sl2 spin-1 R-matrix report."""

from __future__ import annotations

import sys
from pathlib import Path

import sympy as sp

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.rmatrix.sl2_rmatrix import build_sl2_spin1_rmatrix


def main() -> None:
    """Construct and print the sl2 spin-1 raw matrix and braid operator."""

    q = sp.Symbol("q", nonzero=True)
    rmatrix = build_sl2_spin1_rmatrix(q)
    print(rmatrix.pretty_print())


if __name__ == "__main__":
    main()
