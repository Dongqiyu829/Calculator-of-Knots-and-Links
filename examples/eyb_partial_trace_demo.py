"""Run partial-trace diagnostics for the current EYB conventions."""

from __future__ import annotations

import sys
from pathlib import Path

import sympy as sp

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.invariants.eyb_diagnostics import diagnose_partial_trace
from src.invariants.eyb_invariant import build_sl2_fundamental_eyb_data, build_sl3_fundamental_eyb_data
from src.rmatrix.sl2_rmatrix import build_sl2_fundamental_rmatrix
from src.rmatrix.sl3_rmatrix import build_sl3_fundamental_rmatrix


def print_diagnostic_block(title: str, diagnostic) -> None:
    """Print one formatted diagnostic block."""

    print(f"=== {title} ===")
    print(diagnostic.summary())
    print()


def main() -> None:
    """Print the requested partial-trace diagnostics for sl2 and sl3 fundamentals."""

    q = sp.Symbol("q", nonzero=True)

    for label, rbuilder, ebuilder in [
        ("sl2 fundamental", build_sl2_fundamental_rmatrix, build_sl2_fundamental_eyb_data),
        ("sl3 fundamental", build_sl3_fundamental_rmatrix, build_sl3_fundamental_eyb_data),
    ]:
        print(f"########## {label} ##########")
        print()
        print_diagnostic_block(
            "current braid-side choice with mu_kron_mu vs alpha_beta_mu",
            diagnose_partial_trace(
                rmatrix_builder=rbuilder,
                eyb_builder=ebuilder,
                local_object_label="braid_matrix",
                weight_mode="mu_kron_mu",
                target_label="alpha_beta_mu",
                q=q,
            ),
        )
        print_diagnostic_block(
            "current braid inverse with mu_kron_mu vs alpha_inverse_beta_mu",
            diagnose_partial_trace(
                rmatrix_builder=rbuilder,
                eyb_builder=ebuilder,
                local_object_label="braid_matrix_inverse",
                weight_mode="mu_kron_mu",
                target_label="alpha_inverse_beta_mu",
                q=q,
            ),
        )
        print_diagnostic_block(
            "raw matrix with mu_kron_identity vs mu",
            diagnose_partial_trace(
                rmatrix_builder=rbuilder,
                eyb_builder=ebuilder,
                local_object_label="raw_matrix",
                weight_mode="mu_kron_identity",
                target_label="mu",
                q=q,
            ),
        )
        print_diagnostic_block(
            "swap_right_raw with mu_kron_identity vs mu",
            diagnose_partial_trace(
                rmatrix_builder=rbuilder,
                eyb_builder=ebuilder,
                local_object_label="swap_right_raw",
                weight_mode="mu_kron_identity",
                target_label="mu",
                q=q,
            ),
        )


if __name__ == "__main__":
    main()