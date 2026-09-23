"""Exact local-contraction parity against the historical explicit operator."""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path

import pytest
import sympy as sp

from src.braid.braid_operator import BraidOperatorBuilder
from src.braid.braid_word import BraidWord
from src.invariants.eyb_invariant import (
    build_sl2_fundamental_eyb_data,
    build_sl3_fundamental_eyb_data,
    compute_eyb_invariant,
)
from src.invariants.matrix_free_eyb import compute_matrix_free_eyb_scalar
from src.invariants.branch_registry import evaluate_current_branches
from src.invariants.sl2_3d_colored_jones_candidate import (
    current_sl2_3d_candidate_alpha,
    current_sl2_3d_candidate_beta,
    current_sl2_3d_candidate_mu,
)
from src.rmatrix.sl2_rmatrix import build_sl2_fundamental_rmatrix, build_sl2_spin1_rmatrix
from src.rmatrix.sl3_rmatrix import build_sl3_fundamental_rmatrix
from src.services import build_custom_braid_input, evaluate_braid_input_result, evaluate_catalog_result


Q = sp.Symbol("q", nonzero=True)


@lru_cache(maxsize=12)
def _local_data(branch: str, q: sp.Expr):
    if branch == "sl2_fundamental":
        rmatrix = build_sl2_fundamental_rmatrix(q, diagnostics=False)
        eyb = build_sl2_fundamental_eyb_data(q)
        return rmatrix, eyb.mu, eyb.alpha, eyb.beta
    if branch == "sl3_fundamental":
        rmatrix = build_sl3_fundamental_rmatrix(q, diagnostics=False)
        eyb = build_sl3_fundamental_eyb_data(q)
        return rmatrix, eyb.mu, eyb.alpha, eyb.beta
    rmatrix = build_sl2_spin1_rmatrix(q)
    return (
        rmatrix,
        current_sl2_3d_candidate_mu(q),
        current_sl2_3d_candidate_alpha(q),
        current_sl2_3d_candidate_beta(q),
    )


@pytest.mark.parametrize("branch", ("sl2_fundamental", "sl3_fundamental", "sl2_spin1"))
@pytest.mark.parametrize("q", (Q, sp.Integer(2), sp.Integer(3), sp.Integer(5)))
@pytest.mark.parametrize("strands,generators", ((1, ()), (2, (1, -1)), (3, (1, -2)), (3, (-1, 2))))
def test_matrix_free_weighted_and_normalized_parity(branch, q, strands, generators) -> None:
    braid = BraidWord.from_iterable(strands, generators)
    rmatrix, mu, alpha, beta = _local_data(branch, q)
    explicit = BraidOperatorBuilder(braid, rmatrix).build()
    weight = mu
    for _ in range(1, strands):
        weight = sp.kronecker_product(weight, mu)
    expected_weighted = sp.simplify(sp.trace(explicit.operator * weight))
    candidate = compute_matrix_free_eyb_scalar(braid, rmatrix, mu=mu, alpha=alpha, beta=beta)
    assert candidate.operator_dimension == rmatrix.rep.dimension**strands
    assert sp.simplify(candidate.weighted_trace - expected_weighted) == 0
    assert sp.simplify(
        candidate.normalized_expression
        - alpha ** (-braid.writhe()) * beta ** (-strands) * expected_weighted
    ) == 0
    if branch != "sl2_spin1":
        eyb = (
            build_sl2_fundamental_eyb_data(q)
            if branch == "sl2_fundamental"
            else build_sl3_fundamental_eyb_data(q)
        )
        assert sp.simplify(
            candidate.normalized_expression
            - compute_eyb_invariant(explicit, eyb_data=eyb).eyb_normalized_expression
        ) == 0


def test_matrix_free_rejects_nondiagonal_weight() -> None:
    rmatrix, _mu, alpha, beta = _local_data("sl2_fundamental", sp.Integer(2))
    braid = BraidWord.from_iterable(1, ())
    with pytest.raises(ValueError, match="diagonal mu"):
        compute_matrix_free_eyb_scalar(braid, rmatrix, mu=sp.Matrix([[1, 1], [0, 1]]), alpha=alpha, beta=beta)


def test_matrix_free_service_matches_all_numeric_representative_fixtures() -> None:
    path = Path(__file__).parent / "fixtures" / "representative_invariant_regressions.json"
    cases = json.loads(path.read_text(encoding="utf-8"))["cases"]
    for case in cases:
        if case["q_mode"] != "2":
            continue
        branch = case["branch"]
        explicit = evaluate_catalog_result(case["example_label"], branch_ids=(branch,), q=sp.Integer(2))
        matrix_free = evaluate_catalog_result(
            case["example_label"], branch_ids=(branch,), q=sp.Integer(2), backend="matrix_free"
        )
        reference = explicit.branch_results[0]
        scalar = matrix_free.branch_results[0]
        assert scalar.status == reference.status == case["branch_status"]
        assert scalar.primary_output == reference.primary_output
        assert scalar.raw_trace is None
        assert reference.raw_trace is not None
        assert scalar.metadata["evaluation_backend"] == "matrix_free"
        assert sp.simplify(sp.sympify(scalar.primary_output) - sp.sympify(case["expected_expression"])) == 0


def test_matrix_free_service_matches_symbolic_representative_fixtures() -> None:
    path = Path(__file__).parent / "fixtures" / "representative_invariant_regressions.json"
    cases = json.loads(path.read_text(encoding="utf-8"))["cases"]
    for case in cases:
        if case["q_mode"] != "symbolic_q":
            continue
        branch = case["branch"]
        scalar = evaluate_catalog_result(
            case["example_label"], branch_ids=(branch,), q=Q, backend="matrix_free"
        ).branch_results[0]
        assert scalar.status == case["branch_status"]
        assert sp.simplify(
            sp.sympify(scalar.primary_output, locals={"q": Q})
            - sp.sympify(case["expected_expression"], locals={"q": Q})
        ) == 0


def test_matrix_free_manual_input_preserves_order_and_has_no_raw_trace() -> None:
    braid_input = build_custom_braid_input(3, "1, -2, 1, -2")
    explicit = evaluate_braid_input_result(braid_input, branch_ids=("sl2_fundamental",), q=Q)
    scalar = evaluate_braid_input_result(
        braid_input, branch_ids=("sl2_fundamental",), q=Q, backend="matrix_free"
    )
    assert scalar.generators == (1, -2, 1, -2)
    assert scalar.branch_results[0].primary_output == explicit.branch_results[0].primary_output
    assert scalar.branch_results[0].raw_trace is None


@pytest.mark.parametrize("q", (Q, sp.Integer(3), sp.Integer(5)))
@pytest.mark.parametrize("branch", ("sl2_fundamental", "sl3_fundamental", "sl2_spin1"))
def test_matrix_free_trefoil_service_primary_matches_explicit_exactly(branch, q) -> None:
    reference = evaluate_catalog_result("trefoil", branch_ids=(branch,), q=q).branch_results[0]
    scalar = evaluate_catalog_result("trefoil", branch_ids=(branch,), q=q, backend="matrix_free").branch_results[0]
    assert scalar.primary_output == reference.primary_output
    assert scalar.status == reference.status
    assert scalar.raw_trace is None


@pytest.mark.parametrize("q", (Q, sp.Integer(2)))
def test_matrix_free_five_strand_control_matches_explicit(q) -> None:
    word = BraidWord.from_iterable(5, (1, 2, 3, 4))
    reference = evaluate_current_branches(word, branch_ids=("sl2_fundamental",), q=q)[0]
    scalar = evaluate_current_branches(word, branch_ids=("sl2_fundamental",), q=q, backend="matrix_free")[0]
    assert scalar.primary_output == reference.primary_output == 1


def test_matrix_free_does_not_call_global_builder(monkeypatch) -> None:
    from src.invariants import branch_registry

    class ForbiddenBuilder:
        def __init__(self, *args, **kwargs):
            raise AssertionError("matrix-free scalar constructed a global operator")

    monkeypatch.setattr(branch_registry, "BraidOperatorBuilder", ForbiddenBuilder)
    word = BraidWord.from_iterable(2, (1, -1))
    results = evaluate_current_branches(word, q=sp.Integer(2), backend="matrix_free")
    assert {result.branch_id for result in results} == {"sl2_fundamental", "sl3_fundamental", "sl2_spin1"}
    assert all(result.raw_trace is None for result in results)
    assert results[0].primary_output == sp.Rational(5, 2)


def test_backend_selector_rejects_unknown_mode() -> None:
    with pytest.raises(ValueError, match="backend must"):
        evaluate_current_branches(BraidWord.from_iterable(1, ()), backend="unknown")


def _archived_p03():
    root = Path(__file__).resolve().parents[1]
    pairs = json.loads((root / "data" / "benchmark_lab" / "benchmark_pairs_template.json").read_text(encoding="utf-8"))
    case = next(item for item in pairs["benchmarks"] if item["pair_id"] == "P03")
    baseline = json.loads((root / "tests" / "fixtures" / "recovered_benchmark_baselines.json").read_text(encoding="utf-8"))
    words = (
        BraidWord.from_iterable(case["num_strands_A"], case["generators_A"]),
        BraidWord.from_iterable(case["num_strands_B"], case["generators_B"]),
    )
    return words, baseline


@pytest.mark.slow
@pytest.mark.parametrize("q_text", ("2", "3", "5"))
def test_matrix_free_p03_matches_archived_numeric_outputs(q_text) -> None:
    words, baseline = _archived_p03()
    branch_map = {
        "sl2_fundamental": "sl2_fundamental",
        "sl2_3d_9x9": "sl2_spin1",
        "sl3_fundamental": "sl3_fundamental",
    }
    for archived_branch, branch in branch_map.items():
        outputs = [
            evaluate_current_branches(word, branch_ids=(branch,), q=sp.Integer(q_text), backend="matrix_free")[0]
            for word in words
        ]
        assert [str(result.primary_output) for result in outputs] == baseline["p03_numeric_outputs"][q_text][archived_branch]
        assert all(result.raw_trace is None for result in outputs)


@pytest.mark.slow
def test_matrix_free_p03_matches_archived_symbolic_differences() -> None:
    words, baseline = _archived_p03()
    branch_map = {
        "sl2_fundamental": "sl2_fundamental",
        "sl2_3d_9x9": "sl2_spin1",
        "sl3_fundamental": "sl3_fundamental",
    }
    for archived_branch, branch in branch_map.items():
        outputs = [
            evaluate_current_branches(word, branch_ids=(branch,), q=Q, backend="matrix_free")[0].primary_output
            for word in words
        ]
        expected = sp.sympify(baseline["p03_symbolic_differences"][archived_branch], locals={"q": Q})
        assert sp.simplify(outputs[0] - outputs[1] - expected) == 0
