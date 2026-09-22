"""Independent Knot Atlas oracle checks; these fixtures do not define project mathematics."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import pytest
import sympy as sp

from src.braid import BraidWord
from src.braid.braid_operator import BraidOperatorBuilder
from src.catalog.braid_examples import get_braid_example
from src.invariants.branch_registry import (
    evaluate_sl2_fundamental_branch,
    evaluate_sl2_spin1_branch,
    evaluate_sl3_fundamental_branch,
)
from src.rmatrix.sl2_rmatrix import build_sl2_fundamental_rmatrix
from src.services import build_custom_rmatrix_model, evaluate_custom_braid_operator, validate_custom_matrix


Q = sp.Symbol("q", nonzero=True)
Q_ATLAS = sp.Symbol("q_atlas", nonzero=True)
FIXTURE_PATH = Path(__file__).parent / "fixtures" / "knot_atlas_oracles.json"
FIXTURE = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
CASES = {case["knot"]: case for case in FIXTURE["cases"]}


def _expression(text: str) -> sp.Expr:
    return sp.sympify(text, locals={"q_atlas": Q_ATLAS})


def _braid(case: dict[str, object], key: str = "project_braid") -> BraidWord:
    braid = case[key]
    assert isinstance(braid, dict)
    return BraidWord.from_iterable(braid["num_strands"], braid["generators"], label=str(case["knot"]))


@lru_cache(maxsize=None)
def _jones(knot: str, parameter: sp.Expr) -> sp.Expr:
    return sp.expand(evaluate_sl2_fundamental_branch(_braid(CASES[knot]), q=parameter).primary_output)


def _matrix_from_grid(grid: tuple[tuple[str, ...], ...]) -> sp.Matrix:
    return sp.Matrix([[sp.sympify(value, locals={"q": Q}) for value in row] for row in grid])


def _pure_monomial_shift(left: sp.Expr, right: sp.Expr) -> int | None:
    left_poly = sp.Poly(sp.expand(sp.cancel(left) * Q ** 100), Q)
    right_poly = sp.Poly(sp.expand(sp.cancel(right) * Q ** 100), Q)
    if left_poly.coeffs() != right_poly.coeffs() or len(left_poly.monoms()) != len(right_poly.monoms()):
        return None
    shifts = {a[0] - b[0] for a, b in zip(left_poly.monoms(), right_poly.monoms(), strict=True)}
    return shifts.pop() if len(shifts) == 1 else None


def test_fixture_provenance_and_calibration_are_explicit() -> None:
    assert FIXTURE["retrieved_on"] == "2026-09-22"
    assert FIXTURE["source"]["manual_url"] == "https://katlas.org/wiki/Printable_Manual"
    assert FIXTURE["calibration"]["braid_sign_map"] == "project_generator = -atlas_generator"
    assert FIXTURE["calibration"]["evidence_knots"] == ["3_1", "4_1", "5_1", "5_2"]
    assert set(CASES) == {"3_1", "4_1", "5_1", "5_2", "6_1"}
    for case in CASES.values():
        assert case["source_url"].startswith("https://katlas.org/wiki/")
        assert case["retrieval_date"] == FIXTURE["retrieved_on"]
        assert case["project_braid"]["generators"] == [-g for g in case["atlas_braid"]["generators"]]


@pytest.mark.parametrize("knot", ["3_1", "4_1", "5_1", "5_2", "6_1"])
def test_jones_symbolic_oracles(knot: str) -> None:
    expected = sp.expand(_expression(CASES[knot]["jones"]).subs(Q_ATLAS, Q**2))
    assert sp.simplify(_jones(knot, Q) - expected) == 0


@pytest.mark.parametrize("knot", ["3_1", "4_1", "5_2"])
@pytest.mark.parametrize("parameter", [sp.Integer(2), sp.Integer(3)])
def test_jones_numeric_spot_checks(knot: str, parameter: sp.Integer) -> None:
    expected = _expression(CASES[knot]["jones"]).subs(Q_ATLAS, parameter**2)
    assert sp.simplify(_jones(knot, parameter) - expected) == 0


def test_global_sign_negation_is_calibrated_across_chiral_knots() -> None:
    failures = []
    for knot in FIXTURE["calibration"]["evidence_knots"]:
        case = CASES[knot]
        expected = _expression(case["jones"]).subs(Q_ATLAS, Q**2)
        identity_word = _braid({**case, "project_braid": case["atlas_braid"]})
        identity_output = evaluate_sl2_fundamental_branch(identity_word, q=Q).primary_output
        if sp.simplify(identity_output - expected) != 0:
            failures.append(knot)
    assert failures == FIXTURE["calibration"]["identity_map_negative_control_fails_for"]


def test_catalog_presentations_agree_with_atlas_calibration() -> None:
    atlas_trefoil = _jones("3_1", Q)
    atlas_figure_eight = _jones("4_1", Q)
    assert sp.simplify(evaluate_sl2_fundamental_branch(get_braid_example("trefoil"), q=Q).primary_output - atlas_trefoil) == 0
    assert sp.simplify(evaluate_sl2_fundamental_branch(get_braid_example("three_strand_trefoil"), q=Q).primary_output - atlas_trefoil) == 0
    assert sp.simplify(evaluate_sl2_fundamental_branch(get_braid_example("figure_eight"), q=Q).primary_output - atlas_figure_eight) == 0


@pytest.mark.parametrize("knot", ["3_1", "4_1", "5_1", "5_2"])
def test_a2_fundamental_has_one_global_variable_rule(knot: str) -> None:
    expected = sp.expand(_expression(CASES[knot]["a2_fundamental"]).subs(Q_ATLAS, Q**-1))
    actual = evaluate_sl3_fundamental_branch(_braid(CASES[knot]), q=Q).primary_output
    assert sp.simplify(actual - expected) == 0


@pytest.mark.slow
def test_a1_weight_2_remains_diagnostic_without_a_coherent_global_rule() -> None:
    substitutions = (Q, Q**-1, Q**2, Q**-2)
    per_case_matches: dict[str, list[tuple[str, int]]] = {}
    for knot in ("3_1", "5_1", "5_2"):
        candidate = sp.expand(evaluate_sl2_spin1_branch(_braid(CASES[knot]), q=Q).primary_output)
        atlas = _expression(CASES[knot]["a1_weight_2"])
        matches = []
        for substitution in substitutions:
            shift = _pure_monomial_shift(candidate, sp.expand(atlas.subs(Q_ATLAS, substitution)))
            if shift is not None:
                matches.append((str(substitution), shift))
        per_case_matches[knot] = matches
    assert per_case_matches == {"3_1": [], "5_1": [], "5_2": []}


@pytest.mark.parametrize("knot", ["3_1", "4_1", "5_2"])
def test_custom_check_r_matches_builtin_braid_operator_at_q_2(knot: str) -> None:
    braid = _braid(CASES[knot])
    rmatrix = build_sl2_fundamental_rmatrix(sp.Integer(2))
    builtin = BraidOperatorBuilder(braid, rmatrix).build().operator
    model = build_custom_rmatrix_model(rmatrix.braid_matrix, input_kind="check-R")
    custom = _matrix_from_grid(evaluate_custom_braid_operator(model, braid).operator_matrix)
    assert custom == builtin


def test_custom_check_r_matches_builtin_symbolically_for_trefoil() -> None:
    braid = _braid(CASES["3_1"])
    rmatrix = build_sl2_fundamental_rmatrix(Q)
    builtin = BraidOperatorBuilder(braid, rmatrix).build().operator
    model = build_custom_rmatrix_model(rmatrix.braid_matrix, input_kind="check-R")
    custom = _matrix_from_grid(evaluate_custom_braid_operator(model, braid).operator_matrix)
    assert sp.simplify(custom - builtin) == sp.zeros(4)


def test_square_invertible_bad_check_r_fails_braid_relation() -> None:
    bad_check_r = sp.diag(1, 2, 3, 4)
    validation = validate_custom_matrix(
        bad_check_r,
        input_kind="check-R",
        local_dimension=2,
        check_braid_relation=True,
    )
    assert validation.square is True
    assert validation.local_dimension_consistent is True
    assert validation.invertible is True
    assert validation.check_r_braid_relation_satisfied is False


def test_altered_jones_coefficient_is_rejected() -> None:
    expected = _expression(CASES["3_1"]["jones"]).subs(Q_ATLAS, Q**2)
    altered = expected + Q**-8
    assert sp.simplify(_jones("3_1", Q) - altered) != 0
