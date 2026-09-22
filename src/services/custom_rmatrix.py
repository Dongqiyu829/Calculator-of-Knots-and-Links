"""Application facade for convention-explicit custom R/check-R operators."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

import sympy as sp

from src.braid.braid_word import BraidWord
from src.rmatrix.custom_rmatrix import (
    CustomMatrixInputKind,
    CustomMatrixValidation,
    CustomRMatrixProvider,
    validate_custom_matrix as validate_core_custom_matrix,
)

from .errors import CustomBraidOperatorError, CustomMatrixInputError


def _matrix_grid(matrix: sp.Matrix) -> tuple[tuple[str, ...], ...]:
    return tuple(tuple(str(matrix[row, col]) for col in range(matrix.cols)) for row in range(matrix.rows))


@dataclass(frozen=True, slots=True)
class ApplicationCustomMatrixValidation:
    """Frontend-facing custom input validation and optional relation evidence.

    ``is_valid`` remains the backward-compatible structural/application-input
    status. It must not be read as proof that the matrix supplies a braid-group
    representation: that claim requires an explicitly requested and verified
    check-R braid relation.
    """

    input_kind: str
    matrix_shape: tuple[int, int]
    square: bool
    inferred_local_dimension: int | None
    requested_local_dimension: int | None
    local_dimension_consistent: bool
    invertible: bool | None
    check_r_braid_relation_satisfied: bool | None
    standard_r_ybe_satisfied: bool | None
    check_r_braid_relation_requested: bool
    standard_r_ybe_requested: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    @property
    def is_valid(self) -> bool:
        """Return structural/application-input validity, not relation verification."""

        return not self.errors

    @property
    def is_structurally_valid(self) -> bool:
        """Explicit alias for the backward-compatible ``is_valid`` meaning."""

        return self.is_valid

    @staticmethod
    def _requested_relation_status(*, requested: bool, satisfied: bool | None) -> str:
        if not requested:
            return "not_checked"
        if satisfied is True:
            return "verified"
        if satisfied is False:
            return "failed"
        return "undecidable"

    @property
    def check_r_braid_relation_status(self) -> str:
        """Return ``not_checked``, ``verified``, ``failed``, or ``undecidable``."""

        return self._requested_relation_status(
            requested=self.check_r_braid_relation_requested,
            satisfied=self.check_r_braid_relation_satisfied,
        )

    @property
    def standard_r_ybe_status(self) -> str:
        """Return the raw-R YBE status while preserving check-R non-applicability."""

        if self.input_kind != "R" and self.standard_r_ybe_requested:
            return "not_applicable"
        return self._requested_relation_status(
            requested=self.standard_r_ybe_requested,
            satisfied=self.standard_r_ybe_satisfied,
        )

    @property
    def braid_representation_status(self) -> str:
        """Describe whether available evidence supports a braid-representation claim."""

        if not self.is_structurally_valid:
            return "invalid_input"
        return self.check_r_braid_relation_status

    def to_dict(self) -> dict[str, Any]:
        return {
            "input_kind": self.input_kind,
            "matrix_shape": list(self.matrix_shape),
            "square": self.square,
            "inferred_local_dimension": self.inferred_local_dimension,
            "requested_local_dimension": self.requested_local_dimension,
            "local_dimension_consistent": self.local_dimension_consistent,
            "invertible": self.invertible,
            "check_r_braid_relation_satisfied": self.check_r_braid_relation_satisfied,
            "standard_r_ybe_satisfied": self.standard_r_ybe_satisfied,
            "check_r_braid_relation_requested": self.check_r_braid_relation_requested,
            "standard_r_ybe_requested": self.standard_r_ybe_requested,
            "check_r_braid_relation_status": self.check_r_braid_relation_status,
            "standard_r_ybe_status": self.standard_r_ybe_status,
            "braid_representation_status": self.braid_representation_status,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "is_valid": self.is_valid,
            "is_structurally_valid": self.is_structurally_valid,
        }


def _application_validation(
    result: CustomMatrixValidation,
    *,
    check_braid_relation_requested: bool,
    check_standard_r_ybe_requested: bool,
) -> ApplicationCustomMatrixValidation:
    return ApplicationCustomMatrixValidation(
        input_kind=result.input_kind,
        matrix_shape=result.matrix_shape,
        square=result.square,
        inferred_local_dimension=result.inferred_local_dimension,
        requested_local_dimension=result.requested_local_dimension,
        local_dimension_consistent=result.local_dimension_consistent,
        invertible=result.invertible,
        check_r_braid_relation_satisfied=result.braid_relation_satisfied,
        standard_r_ybe_satisfied=result.standard_r_ybe_satisfied,
        check_r_braid_relation_requested=check_braid_relation_requested,
        standard_r_ybe_requested=check_standard_r_ybe_requested,
        errors=result.errors,
        warnings=result.warnings,
    )


@dataclass(frozen=True, slots=True)
class ApplicationCustomRMatrixModel:
    """Validated application model that keeps the core provider behind services."""

    label: str
    input_kind: str
    local_dimension: int
    input_matrix: tuple[tuple[str, ...], ...]
    check_r_matrix: tuple[tuple[str, ...], ...]
    validation: ApplicationCustomMatrixValidation
    _provider: CustomRMatrixProvider = field(repr=False, compare=False)


@dataclass(frozen=True, slots=True)
class ApplicationCustomBraidOperatorResult:
    """Deterministic frontend result for a custom braid-group operator."""

    model_label: str
    input_kind: str
    local_dimension: int
    braid_label: str
    braid_strand_count: int
    braid_generators: tuple[int, ...]
    operator_dimensions: tuple[int, int]
    operator_matrix: tuple[tuple[str, ...], ...]
    operator_text: str
    validation: ApplicationCustomMatrixValidation
    ordered_generator_diagnostics: tuple[dict[str, Any], ...]
    notes: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_label": self.model_label,
            "input_kind": self.input_kind,
            "local_dimension": self.local_dimension,
            "braid": {
                "label": self.braid_label,
                "num_strands": self.braid_strand_count,
                "generators": list(self.braid_generators),
            },
            "operator_dimensions": list(self.operator_dimensions),
            "operator_matrix": [list(row) for row in self.operator_matrix],
            "operator_text": self.operator_text,
            "validation": self.validation.to_dict(),
            "ordered_generator_diagnostics": [dict(item) for item in self.ordered_generator_diagnostics],
            "notes": list(self.notes),
            "warnings": list(self.warnings),
        }


def parse_custom_matrix(matrix_data: object) -> sp.Matrix:
    """Parse nested numeric/SymPy data or SymPy-compatible matrix text exactly."""

    try:
        if isinstance(matrix_data, sp.MatrixBase):
            return sp.Matrix(matrix_data)
        parsed = sp.sympify(matrix_data, locals={"Matrix": sp.Matrix}) if isinstance(matrix_data, str) else matrix_data
        return sp.Matrix(parsed)
    except Exception as exc:
        raise CustomMatrixInputError("Custom matrix input must be valid rectangular SymPy-compatible data.") from exc


def validate_custom_matrix(
    matrix_data: object,
    *,
    input_kind: CustomMatrixInputKind,
    local_dimension: int | None = None,
    check_braid_relation: bool = False,
    check_standard_r_ybe: bool = False,
    simplify: bool = True,
) -> ApplicationCustomMatrixValidation:
    matrix = parse_custom_matrix(matrix_data)
    return _application_validation(
        validate_core_custom_matrix(
            matrix,
            input_kind=input_kind,
            local_dimension=local_dimension,
            check_braid_relation=check_braid_relation,
            check_standard_r_ybe=check_standard_r_ybe,
            simplify=simplify,
        ),
        check_braid_relation_requested=check_braid_relation,
        check_standard_r_ybe_requested=check_standard_r_ybe,
    )


def build_custom_rmatrix_model(
    matrix_data: object,
    *,
    input_kind: CustomMatrixInputKind,
    local_dimension: int | None = None,
    label: str = "custom_matrix",
    check_braid_relation: bool = False,
    check_standard_r_ybe: bool = False,
    simplify_validation: bool = True,
) -> ApplicationCustomRMatrixModel:
    matrix = parse_custom_matrix(matrix_data)
    validation = validate_custom_matrix(
        matrix,
        input_kind=input_kind,
        local_dimension=local_dimension,
        check_braid_relation=check_braid_relation,
        check_standard_r_ybe=check_standard_r_ybe,
        simplify=simplify_validation,
    )
    if not validation.is_valid:
        raise CustomMatrixInputError("; ".join(validation.errors))
    try:
        provider = CustomRMatrixProvider.create(
            matrix,
            input_kind=input_kind,
            local_dimension=local_dimension,
            label=label,
        )
    except ValueError as exc:
        raise CustomMatrixInputError(str(exc)) from exc
    return ApplicationCustomRMatrixModel(
        label=label,
        input_kind=input_kind,
        local_dimension=provider.local_dimension,
        input_matrix=_matrix_grid(provider.input_matrix),
        check_r_matrix=_matrix_grid(provider.check_r_matrix),
        validation=validation,
        _provider=provider,
    )


def evaluate_custom_braid_operator(
    model: ApplicationCustomRMatrixModel,
    braid_word: BraidWord,
    *,
    simplify: bool = False,
) -> ApplicationCustomBraidOperatorResult:
    try:
        data = model._provider.evaluate_braid_word(braid_word, simplify=simplify)
    except ValueError as exc:
        raise CustomBraidOperatorError(str(exc)) from exc
    diagnostics = tuple(
        {
            "step_index": step.step_index,
            "generator": step.generator,
            "strand_pair": list(step.strand_pair),
            "used_inverse": step.used_inverse,
            "embedded_shape": list(step.embedded_shape),
        }
        for step in data.steps
    )
    notes = (
        "Input kind is explicit; R inputs use check-R = P R and check-R inputs are used directly.",
        "Tensor bases are lexicographic and embedded generators multiply left-to-right in braid-word order.",
        "This operator result has no trace, Markov normalization, framing correction, or link-invariant claim.",
    )
    return ApplicationCustomBraidOperatorResult(
        model_label=model.label,
        input_kind=model.input_kind,
        local_dimension=model.local_dimension,
        braid_label=braid_word.label,
        braid_strand_count=braid_word.num_strands,
        braid_generators=tuple(braid_word.generators),
        operator_dimensions=data.operator.shape,
        operator_matrix=_matrix_grid(data.operator),
        operator_text=str(data.operator),
        validation=model.validation,
        ordered_generator_diagnostics=diagnostics,
        notes=notes,
        warnings=data.warnings,
    )


def serialize_custom_braid_operator_result(result: ApplicationCustomBraidOperatorResult) -> str:
    return json.dumps(result.to_dict(), indent=2, ensure_ascii=False, sort_keys=True)
