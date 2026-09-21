"""Print the explicit projector data for the sl2 spin-1 9 x 9 braiding model."""

from __future__ import annotations

import sys
from pathlib import Path

import sympy as sp

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.rmatrix.sl2_rmatrix import build_sl2_spin1_rmatrix


def main() -> None:
    """Construct and print the explicit projector data for sl2 spin-1."""

    q = sp.Symbol("q", nonzero=True)
    rdata = build_sl2_spin1_rmatrix(q)
    print("=== sl2 spin1 projector data ===")
    for projector in rdata.channel_projectors:
        print(projector.summary())
        print()
    print("Projector family checks:")
    print(rdata.validation_data.get("projector_checks"))


if __name__ == "__main__":
    main()
