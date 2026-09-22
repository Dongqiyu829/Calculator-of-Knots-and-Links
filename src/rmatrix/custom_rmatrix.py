"""Convention-explicit custom R/check-R braid-operator support.

This module constructs braid-group operators only.  It does not add a trace,
enhancement, framing correction, or claim that arbitrary input defines a link
invariant.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isqrt
from typing import Literal

import sympy as sp

from src.braid.braid_word import BraidWord

from .rmatrix_base import _embed_adjacent_operator, _embed_two_factor_operator, swap_operator


CustomMatrixInputKind = Literal["R", "check-R"]


def _zero_matrix(matrix: sp.Matrix, *, simplify: bool) -> bool:
    entries = (sp.simplify(value) for value in matrix) if simplify else iter(matrix)
    return all(value == 0 for value in entries)


@dataclass(frozen=True, slots=True)
class CustomMatrixValidation:
    """Structured validation for one explicitly identified R/check-R input."""

    input_kind: str
    matrix_shape: tuple[int, int]
    square: bool
    inferred_local_dimension: int | None
    requested_local_dimension: int | None
    local_dimension_consistent: bool
    invertible: bool | None
    braid_relation_satisfied: bool | None
    standard_r_ybe_satisfied: bool | None
    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    @property
    def is_valid(self) -> bool:
        return not self.errors


def validate_custom_matrix(
    matrix: sp.Matrix,
    *,
    input_kind: CustomMatrixInputKind,
    local_dimension: int | None = None,
    check_braid_relation: bool = False,
    check_standard_r_ybe: bool = False,
    simplify: bool = True,
) -> CustomMatrixValidation:
    """Validate shape, dimension, invertibility, and requested relations."""

    errors: list[str] = []
    warnings: list[str] = []
    rows, cols = matrix.shape
    square = rows == cols
    inferred = isqrt(rows) if square and isqrt(rows) ** 2 == rows else None
    dimension_consistent = inferred is not None and (
        local_dimension is None or local_dimension == inferred
    )
    if input_kind not in ("R", "check-R"):
        errors.append("input_kind must be exactly 'R' or 'check-R'; it is never inferred from entries.")
    if not square:
        errors.append(f"Matrix must be square; received shape {rows} x {cols}.")
    elif inferred is None:
        errors.append(f"Matrix size {rows} is not a tensor-square dimension d^2.")
    if local_dimension is not None and local_dimension < 1:
        errors.append("local_dimension must be a positive integer.")
    elif inferred is not None and local_dimension is not None and local_dimension != inferred:
        errors.append(
            f"Explicit local_dimension={local_dimension} is inconsistent with matrix size {rows}={inferred}^2."
        )

    invertible: bool | None = None
    braid_relation: bool | None = None
    standard_ybe: bool | None = None
    if square and inferred is not None and dimension_consistent and input_kind in ("R", "check-R"):
        determinant = sp.simplify(matrix.det()) if simplify else matrix.det()
        zero_status = determinant.equals(0)
        invertible = None if zero_status is None else not zero_status
        if invertible is None:
            warnings.append("Invertibility is symbolically undecidable for the supplied assumptions.")

        check_r = matrix if input_kind == "check-R" else swap_operator(inferred) * matrix
        if check_braid_relation:
            check_12 = _embed_adjacent_operator(check_r, inferred, 3, 0)
            check_23 = _embed_adjacent_operator(check_r, inferred, 3, 1)
            braid_relation = _zero_matrix(
                check_12 * check_23 * check_12 - check_23 * check_12 * check_23,
                simplify=simplify,
            )
        if check_standard_r_ybe:
            if input_kind != "R":
                warnings.append("Standard R-matrix YBE was not checked because the input kind is check-R.")
            else:
                r_12 = _embed_two_factor_operator(matrix, inferred, 3, (0, 1))
                r_13 = _embed_two_factor_operator(matrix, inferred, 3, (0, 2))
                r_23 = _embed_two_factor_operator(matrix, inferred, 3, (1, 2))
                standard_ybe = _zero_matrix(
                    r_12 * r_13 * r_23 - r_23 * r_13 * r_12,
                    simplify=simplify,
                )

    return CustomMatrixValidation(
        input_kind=input_kind,
        matrix_shape=matrix.shape,
        square=square,
        inferred_local_dimension=inferred,
        requested_local_dimension=local_dimension,
        local_dimension_consistent=dimension_consistent,
        invertible=invertible,
        braid_relation_satisfied=braid_relation,
        standard_r_ybe_satisfied=standard_ybe,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


@dataclass(frozen=True, slots=True)
class CustomBraidOperatorStep:
    step_index: int
    generator: int
    strand_pair: tuple[int, int]
    used_inverse: bool
    embedded_shape: tuple[int, int]


@dataclass(frozen=True, slots=True)
class CustomBraidOperatorData:
    braid_word: BraidWord
    operator: sp.Matrix
    steps: tuple[CustomBraidOperatorStep, ...]
    total_dimension: int
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CustomRMatrixProvider:
    """Local braid provider with an explicit R versus check-R input contract."""

    label: str
    input_kind: CustomMatrixInputKind
    input_matrix: sp.Matrix
    check_r_matrix: sp.Matrix
    local_dimension: int

    @classmethod
    def create(
        cls,
        matrix: sp.Matrix,
        *,
        input_kind: CustomMatrixInputKind,
        local_dimension: int | None = None,
        label: str = "custom_matrix",
    ) -> "CustomRMatrixProvider":
        validation = validate_custom_matrix(
            matrix,
            input_kind=input_kind,
            local_dimension=local_dimension,
        )
        if not validation.is_valid or validation.inferred_local_dimension is None:
            raise ValueError("; ".join(validation.errors))
        dimension = validation.inferred_local_dimension
        check_r = matrix if input_kind == "check-R" else swap_operator(dimension) * matrix
        return cls(
            label=label,
            input_kind=input_kind,
            input_matrix=sp.Matrix(matrix),
            check_r_matrix=sp.Matrix(check_r),
            local_dimension=dimension,
        )

    def operator_for_generator(self, num_strands: int, generator: int) -> sp.Matrix:
        if num_strands < 2:
            raise ValueError("A braid generator requires at least two strands.")
        if generator == 0 or abs(generator) >= num_strands:
            raise ValueError(f"Generator {generator} is invalid for {num_strands} strands.")
        local_operator = self.check_r_matrix
        if generator < 0:
            try:
                local_operator = local_operator.inv()
            except Exception as exc:
                raise ValueError("Negative generators require an invertible check-R matrix.") from exc
        return _embed_adjacent_operator(
            local_operator,
            self.local_dimension,
            num_strands,
            abs(generator) - 1,
        )

    def evaluate_braid_word(self, braid_word: BraidWord, *, simplify: bool = False) -> CustomBraidOperatorData:
        total_dimension = self.local_dimension ** braid_word.num_strands
        warnings = []
        if total_dimension > 1024:
            warnings.append(
                f"Operator dimension {total_dimension} may require substantial memory and symbolic computation time."
            )
        operator = sp.eye(total_dimension)
        steps: list[CustomBraidOperatorStep] = []
        for step_index, generator in enumerate(braid_word.generators, start=1):
            embedded = self.operator_for_generator(braid_word.num_strands, generator)
            operator = operator * embedded
            if simplify:
                operator = operator.applyfunc(sp.simplify)
            generator_index = abs(generator)
            steps.append(
                CustomBraidOperatorStep(
                    step_index=step_index,
                    generator=generator,
                    strand_pair=(generator_index, generator_index + 1),
                    used_inverse=generator < 0,
                    embedded_shape=embedded.shape,
                )
            )
        return CustomBraidOperatorData(
            braid_word=braid_word,
            operator=operator,
            steps=tuple(steps),
            total_dimension=total_dimension,
            warnings=tuple(warnings),
        )
