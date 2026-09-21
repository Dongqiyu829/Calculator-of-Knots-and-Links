"""Projector data and spectral-projector helpers for local braiding models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import sympy as sp


def _matrix_to_string_grid(matrix: sp.Matrix) -> list[list[str]]:
    """Convert a SymPy matrix into a nested list of string entries."""

    return [[str(matrix[row, col]) for col in range(matrix.cols)] for row in range(matrix.rows)]


def _is_zero_matrix(matrix: sp.Matrix) -> bool:
    """Return True when a symbolic matrix simplifies to the zero matrix."""

    return sp.simplify(matrix) == sp.zeros(*matrix.shape)


@dataclass(frozen=True, slots=True)
class ChannelProjectorData:
    """Store one explicit channel projector for a local braiding model.

    Parameters
    ----------
    channel_label:
        Short channel identifier such as "sym", "antisym", or "J=2".
    summand_label:
        Human-readable summand name.
    dimension:
        Expected rank / trace of the projector.
    eigenvalue:
        Braiding eigenvalue attached to the channel.
    projector_matrix:
        Explicit projector matrix on V tensor V.
    notes:
        Free-form comments about the projector construction.
    validation_data:
        Structured validation results such as idempotency checks.
    """

    channel_label: str
    summand_label: str
    dimension: int
    eigenvalue: sp.Expr
    projector_matrix: sp.Matrix
    notes: str = ""
    validation_data: dict[str, Any] = field(default_factory=dict)

    def trace_value(self) -> sp.Expr:
        """Return the symbolic trace of the projector."""

        return sp.simplify(sp.trace(self.projector_matrix))

    def summary(self) -> str:
        """Return a human-readable summary of the projector."""

        lines = [
            f"Channel: {self.channel_label}",
            f"Summand: {self.summand_label}",
            f"Expected dimension: {self.dimension}",
            f"Eigenvalue: {sp.simplify(self.eigenvalue)}",
            f"Projector shape: {self.projector_matrix.shape}",
            f"Projector trace: {self.trace_value()}",
        ]
        if self.validation_data:
            lines.append(f"Validation data: {self.validation_data}")
        if self.notes:
            lines.append(f"Notes: {self.notes}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Return a structured representation suitable for serialization."""

        return {
            "channel_label": self.channel_label,
            "summand_label": self.summand_label,
            "dimension": self.dimension,
            "eigenvalue": str(sp.simplify(self.eigenvalue)),
            "projector_shape": list(self.projector_matrix.shape),
            "projector_trace": str(self.trace_value()),
            "projector_matrix": _matrix_to_string_grid(self.projector_matrix),
            "validation_data": dict(self.validation_data),
            "notes": self.notes,
        }

    def to_string(self) -> str:
        """Return a string form aligned with the summary output."""

        return self.summary()


def spectral_projector(
    braid_matrix: sp.Matrix,
    target_eigenvalue: sp.Expr,
    all_eigenvalues: list[sp.Expr],
) -> sp.Matrix:
    """Build the spectral projector for one simple eigenvalue channel."""

    identity = sp.eye(braid_matrix.rows)
    projector = identity
    for other_eigenvalue in all_eigenvalues:
        if sp.simplify(other_eigenvalue - target_eigenvalue) == 0:
            continue
        projector = sp.simplify(
            projector * (braid_matrix - other_eigenvalue * identity) / (target_eigenvalue - other_eigenvalue)
        )
    return sp.simplify(projector)


def build_channel_projector_data(
    *,
    channel_label: str,
    summand_label: str,
    dimension: int,
    eigenvalue: sp.Expr,
    braid_matrix: sp.Matrix,
    all_eigenvalues: list[sp.Expr],
    notes: str = "",
) -> ChannelProjectorData:
    """Construct one explicit channel projector with validation metadata."""

    projector_matrix = spectral_projector(braid_matrix, eigenvalue, all_eigenvalues)
    trace_value = sp.simplify(sp.trace(projector_matrix))
    validation = {
        "idempotent": _is_zero_matrix(projector_matrix * projector_matrix - projector_matrix),
        "trace_matches_dimension": sp.simplify(trace_value - dimension) == 0,
        "trace": str(trace_value),
    }
    return ChannelProjectorData(
        channel_label=channel_label,
        summand_label=summand_label,
        dimension=dimension,
        eigenvalue=eigenvalue,
        projector_matrix=projector_matrix,
        notes=notes,
        validation_data=validation,
    )


def validate_projector_family(
    projectors: list[ChannelProjectorData],
    braid_matrix: sp.Matrix,
) -> dict[str, Any]:
    """Validate a family of projectors against one local braiding matrix."""

    if not projectors:
        return {}

    size = braid_matrix.rows
    identity = sp.eye(size)
    projector_sum = sp.zeros(size)
    orthogonality: list[dict[str, Any]] = []
    reconstruction = sp.zeros(size)

    for projector in projectors:
        projector_sum += projector.projector_matrix
        reconstruction += projector.eigenvalue * projector.projector_matrix

    for index, left in enumerate(projectors):
        for right in projectors[index + 1 :]:
            orthogonality.append(
                {
                    "left": left.channel_label,
                    "right": right.channel_label,
                    "orthogonal": _is_zero_matrix(left.projector_matrix * right.projector_matrix),
                }
            )

    return {
        "sum_identity": _is_zero_matrix(projector_sum - identity),
        "pairwise_orthogonality": orthogonality,
        "reconstruction": _is_zero_matrix(reconstruction - braid_matrix),
    }
