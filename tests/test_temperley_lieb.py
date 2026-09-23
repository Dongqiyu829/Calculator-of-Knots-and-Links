"""Source-derived TL relations and exact Jones parity before service routing."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import sympy as sp

from src.braid.braid_word import BraidWord
from src.invariants.branch_registry import evaluate_sl2_fundamental_branch
from src.invariants.temperley_lieb import (
    closure_loops,
    evaluate_temperley_lieb_jones,
    generator_diagram,
    identity_diagram,
    multiply_diagrams,
)
from src.rmatrix.sl2_rmatrix import build_sl2_fundamental_rmatrix
from src.services import build_application_branch_presentation, evaluate_catalog_result


Q = sp.Symbol("q", nonzero=True)
ROOT = Path(__file__).resolve().parents[1]


def test_project_local_hecke_and_tl_relations_follow_from_check_r() -> None:
    check_r = build_sl2_fundamental_rmatrix(Q, diagnostics=False).braid_matrix
    identity = sp.eye(4)
    e = Q * identity - check_r
    delta = Q + Q**-1
    mu = sp.diag(Q**-1, Q)
    assert sp.simplify((check_r - Q * identity) * (check_r + Q**-1 * identity)) == sp.zeros(4)
    assert sp.simplify(e * e - delta * e) == sp.zeros(4)
    assert sp.simplify(check_r.inv() - (Q**-1 * identity - e)) == sp.zeros(4)
    e1 = sp.kronecker_product(e, sp.eye(2))
    e2 = sp.kronecker_product(sp.eye(2), e)
    assert sp.simplify(e1 * e2 * e1 - e1) == sp.zeros(8)
    assert sp.simplify(e2 * e1 * e2 - e2) == sp.zeros(8)
    assert sp.trace(mu) == delta
    assert sp.simplify(sp.trace(e * sp.kronecker_product(mu, mu)) - delta) == 0


def test_planar_diagrams_obey_source_derived_multiplication_and_closure() -> None:
    identity = identity_diagram(3)
    e1 = generator_diagram(3, 1)
    e2 = generator_diagram(3, 2)
    assert multiply_diagrams(identity, e1) == (e1, 0)
    assert multiply_diagrams(e1, identity) == (e1, 0)
    assert multiply_diagrams(e1, e1) == (e1, 1)
    product, loops = multiply_diagrams(e1, e2)
    assert loops == 0
    assert multiply_diagrams(product, e1) == (e1, 0)
    assert closure_loops(identity) == 3
    assert closure_loops(e1) == 2


@pytest.mark.parametrize("q", (Q, sp.Integer(2), sp.Integer(3), sp.Integer(5)))
@pytest.mark.parametrize(
    "strands,generators",
    (
        (1, ()),
        (2, ()),
        (2, (1,)),
        (2, (-1,)),
        (2, (1, 1, 1)),
        (3, (1, -2, 1, -2)),
        (3, (1, 2, 1, 2)),
        (3, (-1, 2, -1, 2)),
        (4, (1, -2, 3, -1, 2)),
        (5, (1, 2, 3, 4)),
    ),
)
def test_tl_primary_matches_explicit_reference_exactly(strands, generators, q) -> None:
    word = BraidWord.from_iterable(strands, generators)
    tl = evaluate_temperley_lieb_jones(word, q=q)
    reference = evaluate_sl2_fundamental_branch(word, q=q)
    assert sp.simplify(tl.reduced_expression - reference.primary_output) == 0
    assert tl.unknot_normalization == sp.simplify(q + q**-1)


def test_tl_all_representative_sl2_fixtures() -> None:
    fixture = json.loads((ROOT / "tests" / "fixtures" / "representative_invariant_regressions.json").read_text(encoding="utf-8"))
    for case in fixture["cases"]:
        if case["branch"] != "sl2_fundamental":
            continue
        q = Q if case["q_mode"] == "symbolic_q" else sp.Integer(case["q_mode"])
        word = BraidWord.from_iterable(case["num_strands"], case["generators"])
        actual = evaluate_temperley_lieb_jones(word, q=q).reduced_expression
        expected = sp.sympify(case["expected_expression"], locals={"q": Q})
        assert sp.simplify(actual - expected) == 0


def test_tl_complete_offline_jones_oracle_set() -> None:
    fixture = json.loads((ROOT / "tests" / "fixtures" / "knot_atlas_oracles.json").read_text(encoding="utf-8"))
    q_atlas = sp.Symbol("q_atlas", nonzero=True)
    for case in fixture["cases"]:
        braid = case["project_braid"]
        word = BraidWord.from_iterable(braid["num_strands"], braid["generators"])
        actual = evaluate_temperley_lieb_jones(word, q=Q).reduced_expression
        expected = sp.sympify(case["jones"], locals={"q_atlas": q_atlas}).subs(q_atlas, Q**2)
        assert sp.simplify(actual - expected) == 0, case["knot"]


def test_tl_plain_integer_q_remains_exact() -> None:
    word = BraidWord.from_iterable(2, (1, 1, 1))
    actual = evaluate_temperley_lieb_jones(word, q=2).reduced_expression
    reference = evaluate_sl2_fundamental_branch(word, q=sp.Integer(2)).primary_output
    assert actual == reference
    assert not actual.has(sp.Float)


@pytest.mark.parametrize("q", (Q, sp.Integer(2), sp.Integer(3), sp.Integer(5)))
@pytest.mark.parametrize("strands,generators", ((2, (1, 1, 1)), (3, (1, -2, 1, -2))))
def test_tl_positive_and_negative_stabilization_match_reference(strands, generators, q) -> None:
    base = BraidWord.from_iterable(strands, generators)
    reference = evaluate_sl2_fundamental_branch(base, q=q).primary_output
    for sign in (1, -1):
        stabilized = BraidWord.from_iterable(strands + 1, (*generators, sign * strands))
        actual = evaluate_temperley_lieb_jones(stabilized, q=q).reduced_expression
        assert sp.simplify(actual - reference) == 0


@pytest.mark.parametrize("strands,generators", ((4, (1, 2, -3, 2, 1)), (5, (1, -2, 3, -4, 2)), (6, (1, 2, 3, 4, 5))))
def test_tl_higher_strand_numeric_parity(strands, generators) -> None:
    word = BraidWord.from_iterable(strands, generators)
    actual = evaluate_temperley_lieb_jones(word, q=sp.Integer(2)).reduced_expression
    reference = evaluate_sl2_fundamental_branch(word, q=sp.Integer(2)).primary_output
    assert actual == reference


@pytest.mark.parametrize("generators", ((1, 2, 3, 4, 5, 6, 7) * 2, (1,) * 40))
def test_tl_eight_strand_cyclic_and_long_local_parity(generators) -> None:
    word = BraidWord.from_iterable(8, generators)
    q = sp.Integer(2)
    actual = evaluate_temperley_lieb_jones(word, q=q).reduced_expression
    reference = evaluate_sl2_fundamental_branch(word, q=q).primary_output
    assert actual == reference


@pytest.mark.slow
@pytest.mark.parametrize("q_text", ("2", "3", "5"))
def test_tl_p03_matches_archived_numeric_sl2_outputs(q_text) -> None:
    pairs = json.loads((ROOT / "data" / "benchmark_lab" / "benchmark_pairs_template.json").read_text(encoding="utf-8"))
    case = next(item for item in pairs["benchmarks"] if item["pair_id"] == "P03")
    baseline = json.loads((ROOT / "tests" / "fixtures" / "recovered_benchmark_baselines.json").read_text(encoding="utf-8"))
    q = sp.Integer(q_text)
    outputs = [
        str(evaluate_temperley_lieb_jones(BraidWord.from_iterable(case[f"num_strands_{side}"], case[f"generators_{side}"]), q=q).reduced_expression)
        for side in ("A", "B")
    ]
    assert outputs == baseline["p03_numeric_outputs"][q_text]["sl2_fundamental"]


@pytest.mark.slow
def test_tl_p03_matches_archived_symbolic_sl2_difference() -> None:
    pairs = json.loads((ROOT / "data" / "benchmark_lab" / "benchmark_pairs_template.json").read_text(encoding="utf-8"))
    case = next(item for item in pairs["benchmarks"] if item["pair_id"] == "P03")
    baseline = json.loads((ROOT / "tests" / "fixtures" / "recovered_benchmark_baselines.json").read_text(encoding="utf-8"))
    outputs = [
        evaluate_temperley_lieb_jones(BraidWord.from_iterable(case[f"num_strands_{side}"], case[f"generators_{side}"]), q=Q).reduced_expression
        for side in ("A", "B")
    ]
    expected = sp.sympify(baseline["p03_symbolic_differences"]["sl2_fundamental"], locals={"q": Q})
    assert sp.simplify(outputs[0] - outputs[1] - expected) == 0


@pytest.mark.parametrize("q", (Q, sp.Integer(2), sp.Integer(3), sp.Integer(5)))
@pytest.mark.parametrize("label", ("unknot_1", "unlink_2", "trefoil", "three_strand_trefoil", "figure_eight"))
def test_service_tl_matches_both_existing_backends_without_raw_trace(label, q) -> None:
    selected = ("sl2_fundamental",)
    explicit = evaluate_catalog_result(label, branch_ids=selected, q=q).branch_results[0]
    matrix_free = evaluate_catalog_result(label, branch_ids=selected, q=q, backend="matrix_free").branch_results[0]
    tl = evaluate_catalog_result(label, branch_ids=selected, q=q, backend="temperley_lieb").branch_results[0]
    assert tl.status == matrix_free.status == explicit.status == "formal"
    assert tl.primary_output == matrix_free.primary_output == explicit.primary_output
    assert explicit.raw_trace is not None
    assert matrix_free.raw_trace is None
    assert tl.raw_trace is None
    assert tl.metadata["evaluation_backend"] == "temperley_lieb"
    assert tl.variable_convention == explicit.variable_convention


@pytest.mark.parametrize("label", ("trefoil", "figure_eight"))
def test_tl_preserves_exact_standard_jones_variable_presentation(label) -> None:
    selected = ("sl2_fundamental",)
    explicit = evaluate_catalog_result(label, branch_ids=selected, q=Q).branch_results[0]
    tl = evaluate_catalog_result(label, branch_ids=selected, q=Q, backend="temperley_lieb").branch_results[0]
    reference_presentation = build_application_branch_presentation(explicit, q_parameter=Q, q_parameter_text="q")
    tl_presentation = build_application_branch_presentation(tl, q_parameter=Q, q_parameter_text="q")
    assert tl_presentation.polynomial.conversion_status == "exact"
    assert tl_presentation.polynomial.standard_polynomial_expression == reference_presentation.polynomial.standard_polynomial_expression
    assert tl_presentation.polynomial.atlas_comparable_expression == reference_presentation.polynomial.atlas_comparable_expression
    assert "t = q_project^-2" in tl_presentation.concise_variable_label


def test_tl_selector_rejects_other_branches_instead_of_silently_routing() -> None:
    for selected in (("sl3_fundamental",), ("sl2_spin1",), ("sl2_fundamental", "sl3_fundamental")):
        with pytest.raises(ValueError, match="supports sl2_fundamental only"):
            evaluate_catalog_result("trefoil", branch_ids=selected, q=sp.Integer(2), backend="temperley_lieb")


def test_tl_service_does_not_build_tensor_space_operator(monkeypatch) -> None:
    from src.invariants import branch_registry

    def forbidden(*_args, **_kwargs):
        raise AssertionError("TL backend constructed the quantum-group reference operator")

    monkeypatch.setattr(branch_registry, "BraidOperatorBuilder", forbidden)
    monkeypatch.setattr(branch_registry, "_builtin_rmatrix", forbidden)
    result = evaluate_catalog_result("trefoil", branch_ids=("sl2_fundamental",), q=sp.Integer(2), backend="temperley_lieb")
    assert result.branch_results[0].primary_output == "67/256"
