"""Run stabilization-ratio diagnostics for the current EYB conventions."""

from __future__ import annotations

import sys
from pathlib import Path

import sympy as sp

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.catalog.braid_examples import get_braid_example
from src.invariants.eyb_diagnostics import diagnose_stabilization
from src.invariants.eyb_invariant import build_sl2_fundamental_eyb_data, build_sl3_fundamental_eyb_data
from src.rmatrix.sl2_rmatrix import build_sl2_fundamental_rmatrix
from src.rmatrix.sl3_rmatrix import build_sl3_fundamental_rmatrix


def main() -> None:
    """Print stabilization-ratio diagnostics for selected benchmark examples."""

    q = sp.Symbol("q", nonzero=True)
    example_labels = ["unknot_1", "trefoil", "figure_eight"]

    for representation_label, rbuilder, ebuilder in [
        ("sl2 fundamental", build_sl2_fundamental_rmatrix, build_sl2_fundamental_eyb_data),
        ("sl3 fundamental", build_sl3_fundamental_rmatrix, build_sl3_fundamental_eyb_data),
    ]:
        print(f"########## {representation_label} ##########")
        print()
        for example_label in example_labels:
            diagnostic = diagnose_stabilization(
                get_braid_example(example_label),
                rmatrix_builder=rbuilder,
                eyb_builder=ebuilder,
                local_object_label="braid_matrix",
                q=q,
            )
            print(diagnostic.summary())
            print()


if __name__ == "__main__":
    main()