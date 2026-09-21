"""Enhanced Yang-Baxter normalized invariants for the current MVP stage."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import sympy as sp

from src.algebra.representations import (
    build_sl2_fundamental_representation,
    build_sl3_fundamental_representation,
)
from src.braid.braid_operator import BraidOperatorData
from src.rmatrix.rmatrix_base import RMatrixData

from .polynomial_result import InvariantResult


def _matrix_to_string_grid(matrix: sp.Matrix) -> list[list[str]]:
    """Convert a SymPy matrix into a nested list of string entries."""

    return [[str(matrix[row, col]) for col in range(matrix.cols)] for row in range(matrix.rows)]


def _tensor_power(matrix: sp.Matrix, power: int) -> sp.Matrix:
    """Return the Kronecker power matrix tensor^power."""

    if power < 1:
        raise ValueError("Tensor power is only defined here for positive integers")

    result = matrix
    for _ in range(1, power):
        result = sp.kronecker_product(result, matrix)
    return result


@dataclass(frozen=True, slots=True)
class EYBData:
    """Store the EYB normalization data attached to one representation."""

    representation_name: str
    mu: sp.Matrix
    alpha: sp.Expr
    beta: sp.Expr
    output_label: str
    convention_notes: str
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        """Return a human-readable summary of the EYB data."""

        lines = [
            f"Output label: {self.output_label}",
            f"Representation: {self.representation_name}",
            f"mu: {self.mu}",
            f"alpha: {sp.simplify(self.alpha)}",
            f"beta: {sp.simplify(self.beta)}",
            f"Convention notes: {self.convention_notes}",
        ]
        if self.notes:
            lines.append(f"Notes: {self.notes}")
        if self.metadata:
            lines.append(f"Metadata: {self.metadata}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Return a structured representation suitable for serialization."""

        return {
            "output_label": self.output_label,
            "representation_name": self.representation_name,
            "mu": _matrix_to_string_grid(self.mu),
            "alpha": str(sp.simplify(self.alpha)),
            "beta": str(sp.simplify(self.beta)),
            "convention_notes": self.convention_notes,
            "notes": self.notes,
            "metadata": dict(self.metadata),
        }

    def to_string(self) -> str:
        """Return a string form aligned with the summary output."""

        return self.summary()


def build_sl2_fundamental_eyb_data(q: sp.Expr | None = None) -> EYBData:
    """Return the EYB normalization data for the sl2 fundamental branch."""

    parameter = q if q is not None else sp.Symbol("q", nonzero=True)
    rep = build_sl2_fundamental_representation()
    return EYBData(
        representation_name=rep.name(),
        mu=sp.diag(parameter**-1, parameter),
        alpha=parameter**2,
        beta=sp.Integer(1),
        output_label="P2-type EYB output",
        convention_notes=(
            "This is the current braid-matrix-calibrated A-type fundamental EYB normalization for the sl2 branch "
            "with mu = diag(q^-1, q), alpha = q^2, beta = 1. The alpha sign is chosen to match the present "
            "stabilization convention of the implemented braid_matrix pipeline. It is not being presented here "
            "under a stronger literature name than EYB-normalized output."
        ),
    )


def build_sl3_fundamental_eyb_data(q: sp.Expr | None = None) -> EYBData:
    """Return the EYB normalization data for the sl3 fundamental branch."""

    parameter = q if q is not None else sp.Symbol("q", nonzero=True)
    rep = build_sl3_fundamental_representation()
    return EYBData(
        representation_name=rep.name(),
        mu=sp.diag(parameter**-2, sp.Integer(1), parameter**2),
        alpha=parameter**3,
        beta=sp.Integer(1),
        output_label="P3-type EYB output",
        convention_notes=(
            "This is the current braid-matrix-calibrated A-type fundamental EYB normalization for the sl3 branch "
            "with mu = diag(q^-2, 1, q^2), alpha = q^3, beta = 1. The alpha sign is chosen to match the present "
            "stabilization convention of the implemented braid_matrix pipeline. It is not being presented here "
            "under a stronger literature name than EYB-normalized output."
        ),
    )


def compute_eyb_invariant(
    braid_operator: BraidOperatorData,
    *,
    rmatrix: RMatrixData | None = None,
    mu: sp.Matrix | None = None,
    alpha: sp.Expr | None = None,
    beta: sp.Expr | None = None,
    eyb_data: EYBData | None = None,
) -> InvariantResult:
    """Compute the EYB-normalized invariant for a braid operator.

    The implemented formula is

        alpha^(-writhe) beta^(-num_strands) Tr(b(beta) mu^(tensor num_strands)).
    """

    effective_rmatrix = braid_operator.rmatrix if rmatrix is None else rmatrix
    if effective_rmatrix.rep.name() != braid_operator.rmatrix.rep.name():
        raise ValueError("The supplied RMatrixData must match the braid operator representation")

    if eyb_data is not None:
        effective_mu = eyb_data.mu
        effective_alpha = eyb_data.alpha
        effective_beta = eyb_data.beta
        eyb_metadata = eyb_data.to_dict()
        output_label = eyb_data.output_label
        eyb_convention_notes = eyb_data.convention_notes
    else:
        if mu is None or alpha is None or beta is None:
            raise ValueError("Provide either eyb_data or explicit mu, alpha, and beta")
        effective_mu = mu
        effective_alpha = alpha
        effective_beta = beta
        eyb_metadata = {
            "mu": _matrix_to_string_grid(effective_mu),
            "alpha": str(sp.simplify(effective_alpha)),
            "beta": str(sp.simplify(effective_beta)),
        }
        output_label = "Custom EYB output"
        eyb_convention_notes = "Custom EYB data provided explicitly by the caller."

    if effective_mu.shape[0] != effective_rmatrix.rep.dimension or effective_mu.shape[1] != effective_rmatrix.rep.dimension:
        raise ValueError("mu must be a square matrix compatible with the underlying representation dimension")

    mu_tensor_power = _tensor_power(effective_mu, braid_operator.num_strands)
    raw_trace = sp.simplify(sp.trace(braid_operator.operator))
    weighted_trace = sp.simplify(sp.trace(braid_operator.operator * mu_tensor_power))
    normalized = sp.simplify(
        effective_alpha ** (-braid_operator.writhe)
        * effective_beta ** (-braid_operator.num_strands)
        * weighted_trace
    )

    return InvariantResult(
        representation=braid_operator.rmatrix.rep,
        braid_word=braid_operator.braid_word,
        operator_dimension=braid_operator.total_dimension,
        raw_closure_trace=raw_trace,
        eyb_normalized_expression=normalized,
        future_rt_quantum_trace_expression=None,
        trace_mode="ordinary_trace + eyb_weighted_trace",
        convention_notes=(
            f"{output_label}. Raw closure trace is retained separately. The EYB-normalized expression uses the "
            "enhanced Yang-Baxter formula alpha^(-w) beta^(-n) Tr(b(beta) mu^(tensor n)). "
            f"{eyb_convention_notes}"
        ),
        framing_notes=(
            "The EYB-normalized output is stronger than the raw closure trace, but this project still keeps it "
            "separate from any future RT quantum-trace normalization layer."
        ),
        metadata={
            "output_label": output_label,
            "eyb_data": eyb_metadata,
            "weighted_trace_before_normalization": str(weighted_trace),
            "mu_tensor_power_shape": list(mu_tensor_power.shape),
        },
    )
