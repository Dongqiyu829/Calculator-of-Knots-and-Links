"""Shared data structures and validation helpers for R-matrices.

The project distinguishes between two related but different objects:

1. matrix: the raw matrix-form object closest to the literature formula.
2. braid_matrix: the local braiding operator that represents a braid generator.

Later braid code should only consume braid_matrix. This module keeps the two
objects explicit so no later stage needs to guess which convention is in use.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product
from typing import Any, Literal

import sympy as sp

from src.algebra.representations import RepresentationSpec
from .projectors import ChannelProjectorData


ValidationTarget = Literal["matrix", "braid_matrix"]


@dataclass(frozen=True, slots=True)
class RMatrixData:
    """Store one local R-matrix model together with its braiding operator.

    Parameters
    ----------
    rep:
        Representation supporting the local operator.
    matrix:
        Raw matrix-form object closest to the literature formula.
    braid_matrix:
        Local braiding operator that should act as a braid generator.
    dim:
        Dimension of the local operator, equal to dim(V tensor V).
    basis_order:
        Ordered basis for V tensor V.
    eigenvalues:
        Eigenvalues of braid_matrix, listed with multiplicity removed.
    minimal_polynomial:
        Minimal polynomial of braid_matrix, computed from the distinct
        eigenvalues in the current MVP implementation.
    notes:
        Free-form mathematical or implementation notes.
    convention_notes:
        Notes clarifying which object is used where.
    validation_data:
        Cached validation information such as Yang-Baxter checks.
    """

    rep: RepresentationSpec
    matrix: sp.Matrix
    braid_matrix: sp.Matrix
    dim: int
    basis_order: tuple[str, ...]
    eigenvalues: list[sp.Expr]
    minimal_polynomial: sp.Expr | None
    notes: str
    convention_notes: str
    validation_data: dict[str, Any] = field(default_factory=dict)
    matrix_eigenvalues: list[sp.Expr] = field(default_factory=list)
    factorized_minimal_polynomial: sp.Expr | None = None
    eigenvalue_channels: list[dict[str, str]] = field(default_factory=list)
    channel_projectors: list[ChannelProjectorData] = field(default_factory=list)

    def summary(self) -> str:
        """Return a readable summary of the local operator data."""

        lines = [
            f"Representation: {self.rep.name()}",
            f"Local operator dimension: {self.dim}",
            f"Basis order: ({', '.join(self.basis_order)})",
            f"Raw matrix shape: {self.matrix.shape}",
            f"Braiding matrix shape: {self.braid_matrix.shape}",
            f"Braiding eigenvalues: {self.eigenvalues}",
        ]
        if self.matrix_eigenvalues:
            lines.append(f"Raw matrix eigenvalues: {self.matrix_eigenvalues}")
        if self.minimal_polynomial is not None:
            lines.append(f"Braiding minimal polynomial: {sp.expand(self.minimal_polynomial)}")
        if self.factorized_minimal_polynomial is not None:
            lines.append(
                "Braiding minimal polynomial (factorized): "
                f"{self.factorized_minimal_polynomial}"
            )
        if self.eigenvalue_channels:
            lines.append(f"Braiding eigenvalue channels: {self.eigenvalue_channels}")
        if self.channel_projectors:
            lines.append(f"Channel projector count: {len(self.channel_projectors)}")

        braid_ybe = self.validation_data.get("braid_ybe")
        if braid_ybe is not None:
            lines.append(f"Braiding Yang-Baxter check: {braid_ybe}")

        raw_ybe = self.validation_data.get("raw_ybe")
        if raw_ybe is not None:
            lines.append(f"Raw Yang-Baxter check: {raw_ybe}")

        lines.append(f"Convention notes: {self.convention_notes}")
        lines.append(f"Notes: {self.notes}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Return a structured form suitable for CLI, tests, or future GUI use."""

        return {
            "representation": self.rep.to_dict(),
            "dim": self.dim,
            "basis_order": list(self.basis_order),
            "matrix_shape": list(self.matrix.shape),
            "braid_matrix_shape": list(self.braid_matrix.shape),
            "matrix": _matrix_to_string_grid(self.matrix),
            "braid_matrix": _matrix_to_string_grid(self.braid_matrix),
            "eigenvalues": [str(value) for value in self.eigenvalues],
            "matrix_eigenvalues": [str(value) for value in self.matrix_eigenvalues],
            "minimal_polynomial": None
            if self.minimal_polynomial is None
            else str(sp.expand(self.minimal_polynomial)),
            "factorized_minimal_polynomial": None
            if self.factorized_minimal_polynomial is None
            else str(self.factorized_minimal_polynomial),
            "eigenvalue_channels": [dict(channel) for channel in self.eigenvalue_channels],
            "channel_projectors": [projector.to_dict() for projector in self.channel_projectors],
            "notes": self.notes,
            "convention_notes": self.convention_notes,
            "validation_data": dict(self.validation_data),
        }

    def to_string(self) -> str:
        """Return a string form aligned with the summary output."""

        return self.summary()

    def pretty_print(self) -> str:
        """Return a more detailed printable report including matrix entries."""

        lines = [self.summary(), "Raw matrix:", str(self.matrix), "Braiding matrix:", str(self.braid_matrix)]
        return "\n".join(lines)


def swap_operator(local_dim: int) -> sp.Matrix:
    """Return the tensor-factor swap operator on V tensor V.

    Parameters
    ----------
    local_dim:
        Dimension of V.
    """

    size = local_dim * local_dim
    permutation = sp.zeros(size, size)
    for left in range(local_dim):
        for right in range(local_dim):
            source = left * local_dim + right
            target = right * local_dim + left
            permutation[target, source] = 1
    return permutation


def _matrix_to_string_grid(matrix: sp.Matrix) -> list[list[str]]:
    """Convert a SymPy matrix into a nested list of string entries."""

    return [[str(matrix[row, col]) for col in range(matrix.cols)] for row in range(matrix.rows)]


def build_local_braiding_from_raw(raw_matrix: sp.Matrix, local_dim: int) -> sp.Matrix:
    """Convert a raw matrix-form object into the braid generator operator."""

    return swap_operator(local_dim) * raw_matrix


def compute_eigen_data(matrix: sp.Matrix) -> list[sp.Expr]:
    """Return the distinct eigenvalues of a matrix in simplified form."""

    eigenvalues = matrix.eigenvals()
    simplified = [sp.simplify(value) for value in eigenvalues]
    return sorted(simplified, key=sp.default_sort_key)


def compute_minimal_polynomial(
    matrix: sp.Matrix,
    variable: sp.Symbol | None = None,
) -> sp.Expr | None:
    """Return a minimal-polynomial candidate from distinct eigenvalues.

    Notes
    -----
    The current MVP implementation multiplies the distinct linear factors from
    the symbolic eigenvalue set. This is exact for the sl2 fundamental case and
    for the semisimple Hecke-type examples planned next. A future extension may
    add Jordan-block detection if needed.
    """

    symbol = variable or sp.Symbol("x")
    eigenvalues = compute_eigen_data(matrix)
    if not eigenvalues:
        return None

    polynomial = sp.Integer(1)
    for eigenvalue in eigenvalues:
        polynomial *= symbol - eigenvalue
    return sp.expand(polynomial)


def _embed_adjacent_operator(
    operator: sp.Matrix,
    local_dim: int,
    num_factors: int,
    start: int,
) -> sp.Matrix:
    """Embed a local operator on adjacent tensor factors.

    Parameters
    ----------
    operator:
        Matrix acting on V tensor V.
    local_dim:
        Dimension of V.
    num_factors:
        Number of tensor factors in the global space.
    start:
        Zero-based index of the first tensor leg acted on by the local operator.
    """

    if num_factors < 2:
        raise ValueError("num_factors must be at least 2")
    if start < 0 or start + 1 >= num_factors:
        raise ValueError("start must identify a valid adjacent tensor pair")

    left = sp.eye(local_dim ** start)
    right = sp.eye(local_dim ** (num_factors - start - 2))
    return sp.kronecker_product(left, operator, right)


def _encode_tensor_state(state: tuple[int, ...], local_dim: int) -> int:
    """Encode a tensor-product basis state into a matrix index."""

    index = 0
    for value in state:
        index = index * local_dim + value
    return index


def _embed_two_factor_operator(
    operator: sp.Matrix,
    local_dim: int,
    num_factors: int,
    positions: tuple[int, int],
) -> sp.Matrix:
    """Embed a two-factor operator on arbitrary tensor legs.

    This helper is used for the ordinary Yang-Baxter equation, where the raw
    matrix must act on the factor pairs (1, 2), (1, 3), and (2, 3).
    """

    left_pos, right_pos = positions
    if left_pos < 0 or right_pos < 0 or left_pos >= num_factors or right_pos >= num_factors:
        raise ValueError("operator positions must lie inside the tensor product")
    if left_pos == right_pos:
        raise ValueError("operator positions must be distinct")

    global_dim = local_dim ** num_factors
    result = sp.zeros(global_dim, global_dim)

    for input_state in product(range(local_dim), repeat=num_factors):
        global_col = _encode_tensor_state(input_state, local_dim)
        local_col = input_state[left_pos] * local_dim + input_state[right_pos]

        for local_row in range(local_dim * local_dim):
            coefficient = operator[local_row, local_col]
            if coefficient == 0:
                continue

            output_state = list(input_state)
            output_state[left_pos] = local_row // local_dim
            output_state[right_pos] = local_row % local_dim
            global_row = _encode_tensor_state(tuple(output_state), local_dim)
            result[global_row, global_col] += coefficient

    return result


def check_yang_baxter(
    rmatrix: RMatrixData,
    target: ValidationTarget = "braid_matrix",
) -> bool:
    """Check the Yang-Baxter relation for the chosen local operator.

    Parameters
    ----------
    rmatrix:
        Local R-matrix data.
    target:
        "braid_matrix" checks the braid-form Yang-Baxter relation on the local
        braiding operator. "matrix" checks the same tensor-placement equation on
        the raw matrix object. For the current sl2 fundamental implementation,
        the braid-form check is the primary validation signal.
    """

    local_dim = rmatrix.rep.dimension
    if target == "braid_matrix":
        operator = rmatrix.braid_matrix
        operator_12 = _embed_adjacent_operator(operator, local_dim, 3, 0)
        operator_23 = _embed_adjacent_operator(operator, local_dim, 3, 1)
        left = sp.simplify(operator_12 * operator_23 * operator_12)
        right = sp.simplify(operator_23 * operator_12 * operator_23)
    else:
        operator = rmatrix.matrix
        operator_12 = _embed_two_factor_operator(operator, local_dim, 3, (0, 1))
        operator_13 = _embed_two_factor_operator(operator, local_dim, 3, (0, 2))
        operator_23 = _embed_two_factor_operator(operator, local_dim, 3, (1, 2))
        left = sp.simplify(operator_12 * operator_13 * operator_23)
        right = sp.simplify(operator_23 * operator_13 * operator_12)

    difference = sp.simplify(left - right)
    return difference == sp.zeros(*difference.shape)
