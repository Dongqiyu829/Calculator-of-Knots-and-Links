"""Print the current raw-side versus braid-side convention audit summary."""

from __future__ import annotations

import sys
from pathlib import Path

import sympy as sp

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.invariants.convention_audit import (
    build_braid_side_convention_data,
    build_raw_side_convention_data,
    compare_raw_and_braid_side_conventions,
)
from src.invariants.eyb_invariant import build_sl2_fundamental_eyb_data, build_sl3_fundamental_eyb_data
from src.rmatrix.sl2_rmatrix import build_sl2_fundamental_rmatrix
from src.rmatrix.sl3_rmatrix import build_sl3_fundamental_rmatrix


def print_section(title: str) -> None:
    """Print a simple section title."""

    print(f"=== {title} ===")


def main() -> None:
    """Print the final raw-side versus braid-side convention audit for sl2 and sl3 fundamentals."""

    q = sp.Symbol("q", nonzero=True)
    combos = [
        ("raw_matrix", "mu_kron_identity"),
        ("raw_matrix", "identity_kron_mu"),
        ("raw_matrix", "mu_kron_mu"),
        ("braid_matrix", "mu_kron_mu"),
        ("braid_matrix_inverse", "mu_kron_mu"),
    ]

    for label, rbuilder, ebuilder in [
        ("sl2 fundamental", build_sl2_fundamental_rmatrix, build_sl2_fundamental_eyb_data),
        ("sl3 fundamental", build_sl3_fundamental_rmatrix, build_sl3_fundamental_eyb_data),
    ]:
        print(f"########## {label} ##########")
        print()

        print_section("current braid-side working convention")
        braid_side = build_braid_side_convention_data(
            rmatrix_builder=rbuilder,
            eyb_builder=ebuilder,
            q=q,
        )
        print(braid_side.summary())
        print()

        print_section("raw-side candidates")
        for local_object, weight_mode in combos:
            raw_side = build_raw_side_convention_data(
                rmatrix_builder=rbuilder,
                eyb_builder=ebuilder,
                local_object=local_object,
                weight_mode=weight_mode,
                q=q,
            )
            print(raw_side.summary())
            print()

        print_section("final comparison")
        comparison = compare_raw_and_braid_side_conventions(
            rmatrix_builder=rbuilder,
            eyb_builder=ebuilder,
            q=q,
        )
        print(comparison.summary())
        print()


if __name__ == "__main__":
    main()