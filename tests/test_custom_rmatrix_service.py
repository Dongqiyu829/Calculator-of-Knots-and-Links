"""Contract tests for the convention-explicit custom R/check-R service."""

from __future__ import annotations

import json

import pytest
import sympy as sp

from src.braid import BraidWord
from src.rmatrix.sl2_rmatrix import build_sl2_fundamental_rmatrix
from src.services import (
    CustomBraidOperatorError,
    CustomMatrixInputError,
    build_custom_rmatrix_model,
    evaluate_custom_braid_operator,
    parse_custom_matrix,
    serialize_custom_braid_operator_result,
    validate_custom_matrix,
)


def _matrix_from_grid(grid: tuple[tuple[str, ...], ...]) -> sp.Matrix:
    return sp.Matrix([[sp.sympify(value) for value in row] for row in grid])


def test_recovered_sl2_fixture_supports_explicit_r_and_check_r_modes() -> None:
    recovered = build_sl2_fundamental_rmatrix(sp.Integer(2))
    check_model = build_custom_rmatrix_model(
        recovered.braid_matrix,
        input_kind="check-R",
        label="sl2-check-fixture",
        check_braid_relation=True,
    )
    raw_model = build_custom_rmatrix_model(
        recovered.matrix,
        input_kind="R",
        label="sl2-r-fixture",
        check_braid_relation=True,
        check_standard_r_ybe=True,
    )

    assert check_model.local_dimension == raw_model.local_dimension == 2
    assert check_model.validation.check_r_braid_relation_satisfied is True
    assert raw_model.validation.check_r_braid_relation_satisfied is True
    assert raw_model.validation.standard_r_ybe_satisfied is True
    assert _matrix_from_grid(raw_model.check_r_matrix) == recovered.braid_matrix
    assert _matrix_from_grid(check_model.check_r_matrix) == recovered.braid_matrix


def test_positive_negative_generator_round_trip_is_identity() -> None:
    recovered = build_sl2_fundamental_rmatrix(sp.Integer(2))
    model = build_custom_rmatrix_model(recovered.braid_matrix, input_kind="check-R")
    braid = BraidWord.from_iterable(2, (1, -1), label="round_trip")

    result = evaluate_custom_braid_operator(model, braid)

    assert _matrix_from_grid(result.operator_matrix) == sp.eye(4)
    assert [item["generator"] for item in result.ordered_generator_diagnostics] == [1, -1]
    assert result.ordered_generator_diagnostics[1]["used_inverse"] is True


def test_short_word_matches_direct_left_to_right_tensor_multiplication() -> None:
    recovered = build_sl2_fundamental_rmatrix(sp.Integer(2))
    model = build_custom_rmatrix_model(recovered.braid_matrix, input_kind="check-R")
    braid = BraidWord.from_iterable(3, (1, 2, -1), label="direct_product")
    result = evaluate_custom_braid_operator(model, braid)

    check_r = recovered.braid_matrix
    sigma_1 = sp.kronecker_product(check_r, sp.eye(2))
    sigma_2 = sp.kronecker_product(sp.eye(2), check_r)
    expected = sigma_1 * sigma_2 * sigma_1.inv()
    assert _matrix_from_grid(result.operator_matrix) == expected
    assert result.braid_generators == (1, 2, -1)
    assert result.operator_dimensions == (8, 8)


def test_validation_reports_invalid_shape_wrong_dimension_and_singular_inverse() -> None:
    nonsquare = validate_custom_matrix([[1, 0, 0], [0, 1, 0]], input_kind="check-R")
    wrong_dimension = validate_custom_matrix(sp.eye(4), input_kind="check-R", local_dimension=3)

    assert nonsquare.is_valid is False
    assert nonsquare.square is False
    assert "square" in nonsquare.errors[0]
    assert wrong_dimension.is_valid is False
    assert wrong_dimension.local_dimension_consistent is False
    with pytest.raises(CustomMatrixInputError, match="inconsistent"):
        build_custom_rmatrix_model(sp.eye(4), input_kind="check-R", local_dimension=3)

    singular_model = build_custom_rmatrix_model(sp.zeros(4), input_kind="check-R")
    with pytest.raises(CustomBraidOperatorError, match="invertible"):
        evaluate_custom_braid_operator(singular_model, BraidWord.from_iterable(2, (-1,)))


def test_symbolic_text_preserves_exact_arithmetic_and_serializes_deterministically() -> None:
    matrix_text = "[[q,0,0,0],[0,q,0,0],[0,0,q,0],[0,0,0,q]]"
    parsed = parse_custom_matrix(matrix_text)
    q = sp.Symbol("q")
    assert parsed == q * sp.eye(4)

    model = build_custom_rmatrix_model(
        matrix_text,
        input_kind="check-R",
        check_braid_relation=True,
    )
    result = evaluate_custom_braid_operator(model, BraidWord.from_iterable(2, (1,)), simplify=False)
    serialized = serialize_custom_braid_operator_result(result)

    assert _matrix_from_grid(result.operator_matrix) == q * sp.eye(4)
    assert result.validation.check_r_braid_relation_satisfied is True
    assert json.loads(serialized)["input_kind"] == "check-R"
    assert serialized == serialize_custom_braid_operator_result(result)
    assert any("no trace" in note.lower() for note in result.notes)


def test_relation_names_remain_mathematically_distinct() -> None:
    validation = validate_custom_matrix(
        sp.eye(4),
        input_kind="check-R",
        check_braid_relation=True,
        check_standard_r_ybe=True,
    )
    assert validation.check_r_braid_relation_satisfied is True
    assert validation.standard_r_ybe_satisfied is None
    assert any("input kind is check-R" in warning for warning in validation.warnings)
