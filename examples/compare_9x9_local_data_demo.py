"""Compare the two first-stage 9 x 9 local braiding models."""

from __future__ import annotations

import sys
from pathlib import Path

import sympy as sp

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.rmatrix.sl2_rmatrix import build_sl2_spin1_rmatrix
from src.rmatrix.sl3_rmatrix import build_sl3_fundamental_rmatrix


def print_comparison_block(title: str, rdata) -> None:
    """Print the requested comparison fields for one 9 x 9 local model."""

    decomposition = rdata.rep.tensor_square_decomposition
    print(f"=== {title} ===")
    print(f"Representation name: {rdata.rep.name()}")
    print(f"Local operator dimension: {rdata.dim}")
    print(f"Tensor-square decomposition: {decomposition.decomposition_formula()}")
    print(f"Channel count: {len(decomposition.summands)}")
    print(f"Braiding eigenvalues: {rdata.eigenvalues}")
    print(f"Eigenvalue channels: {rdata.eigenvalue_channels}")
    print(f"Factorized minimal polynomial: {rdata.factorized_minimal_polynomial}")
    print(f"YBE check (braid): {rdata.validation_data.get('braid_ybe')}")
    print(f"YBE check (raw): {rdata.validation_data.get('raw_ybe')}")
    print(f"Basis order: {rdata.basis_order}")
    print()


def main() -> None:
    """Build and compare the sl3 fundamental and sl2 spin-1 9 x 9 models."""

    q = sp.Symbol("q", nonzero=True)
    sl3_data = build_sl3_fundamental_rmatrix(q)
    sl2_spin1_data = build_sl2_spin1_rmatrix(q)

    print_comparison_block("sl3 fundamental", sl3_data)
    print_comparison_block("sl2 spin1", sl2_spin1_data)


if __name__ == "__main__":
    main()
