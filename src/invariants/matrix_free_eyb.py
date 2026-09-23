"""Exact scalar contraction of local braid gates without a global operator.

This follows the row-to-column product of ``BraidOperatorBuilder``.  For each
lexicographic input basis state, a sparse row is propagated through the signed
local check-R gates in listed order; only its closing diagonal entry is kept.
The built-in enhancement matrices are diagonal, so their initial-state weight
can be attached at closure.  No ``d**n`` by ``d**n`` matrix is constructed.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

import sympy as sp

from src.braid.braid_word import BraidWord
from src.rmatrix.rmatrix_base import RMatrixData


@dataclass(frozen=True, slots=True)
class MatrixFreeScalarResult:
    """Weighted closure and normalized scalar; no full operator or raw trace."""

    weighted_trace: sp.Expr
    normalized_expression: sp.Expr
    operator_dimension: int


def _row_transitions(local_gate: sp.Matrix) -> tuple[tuple[tuple[int, sp.Expr], ...], ...]:
    """Retain nonzero row-to-column entries of one signed local gate."""

    return tuple(
        tuple((column, local_gate[row, column]) for column in range(local_gate.cols) if local_gate[row, column] != 0)
        for row in range(local_gate.rows)
    )


def compute_matrix_free_eyb_scalar(
    braid_word: BraidWord,
    rmatrix: RMatrixData,
    *,
    mu: sp.Matrix,
    alpha: sp.Expr,
    beta: sp.Expr,
) -> MatrixFreeScalarResult:
    """Contract the established EYB scalar with exact SymPy arithmetic.

    Only diagonal ``mu`` is supported.  This covers the three maintained
    built-in branches; rejecting other weights prevents an incorrect shortcut.
    Negative generators use the inverse of ``rmatrix.braid_matrix`` exactly as
    the explicit builder does.  The raw literature-side R is never used.
    """

    dimension = rmatrix.rep.dimension
    if rmatrix.braid_matrix.shape != (dimension * dimension, dimension * dimension):
        raise ValueError("braid_matrix dimension is inconsistent with the representation")
    if mu.shape != (dimension, dimension) or not mu.is_diagonal():
        raise ValueError("matrix-free EYB scalar requires a diagonal mu of representation dimension")

    gates: dict[int, tuple[tuple[tuple[int, sp.Expr], ...], ...]] = {}
    inverse: sp.Matrix | None = None
    for generator in braid_word.generators:
        if generator not in gates:
            if generator < 0:
                if inverse is None:
                    inverse = sp.simplify(rmatrix.braid_matrix.inv())
                local_gate = inverse
            else:
                local_gate = rmatrix.braid_matrix
            gates[generator] = _row_transitions(local_gate)

    weighted_terms: list[sp.Expr] = []
    for initial in product(range(dimension), repeat=braid_word.num_strands):
        weight = sp.prod(mu[index, index] for index in initial)
        if weight == 0:
            continue
        rows: dict[tuple[int, ...], sp.Expr] = {initial: sp.Integer(1)}
        for generator in braid_word.generators:
            start = abs(generator) - 1
            transitions = gates[generator]
            following: dict[tuple[int, ...], sp.Expr] = {}
            for state, amplitude in rows.items():
                local_row = state[start] * dimension + state[start + 1]
                for local_column, coefficient in transitions[local_row]:
                    new_state = (
                        state[:start]
                        + (local_column // dimension, local_column % dimension)
                        + state[start + 2 :]
                    )
                    following[new_state] = following.get(new_state, sp.Integer(0)) + amplitude * coefficient
            rows = following
            if not rows:
                break
        weighted_terms.append(weight * rows.get(initial, sp.Integer(0)))

    weighted_trace = sp.simplify(sp.Add(*weighted_terms))
    normalized = sp.simplify(
        alpha ** (-braid_word.writhe()) * beta ** (-braid_word.num_strands) * weighted_trace
    )
    return MatrixFreeScalarResult(
        weighted_trace=weighted_trace,
        normalized_expression=normalized,
        operator_dimension=dimension ** braid_word.num_strands,
    )
