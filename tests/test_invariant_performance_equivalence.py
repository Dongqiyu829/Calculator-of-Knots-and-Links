"""Exact, untimed checks for the profiled built-in evaluation fast paths."""

from __future__ import annotations

import sympy as sp

from src.braid.braid_operator import BraidOperatorBuilder
from src.catalog.braid_examples import get_braid_example
from src.invariants.branch_registry import (
    _builtin_rmatrix,
    evaluate_sl2_fundamental_branch,
    evaluate_sl2_spin1_branch,
    evaluate_sl3_fundamental_branch,
)
from src.invariants.eyb_invariant import (
    build_sl2_fundamental_eyb_data,
    compute_eyb_invariant,
)
from src.invariants.jones_invariant import current_sl2_unknot_normalization
from src.invariants.sl2_3d_colored_jones_candidate import (
    compute_sl2_3d_candidate_unreduced_output,
    current_sl2_3d_unknot_normalization,
)
from src.rmatrix.sl2_rmatrix import build_sl2_fundamental_rmatrix, build_sl2_spin1_rmatrix
from src.rmatrix.sl3_rmatrix import build_sl3_fundamental_rmatrix


def test_runtime_local_matrices_match_validated_construction() -> None:
    for q in (sp.Integer(2), sp.Symbol("q", nonzero=True)):
        for branch, builder in (
            ("sl2_fundamental", build_sl2_fundamental_rmatrix),
            ("sl3_fundamental", build_sl3_fundamental_rmatrix),
        ):
            validated = builder(q)
            runtime = _builtin_rmatrix(branch, q)
            assert runtime.matrix == validated.matrix
            assert runtime.braid_matrix == validated.braid_matrix
            assert runtime.basis_order == validated.basis_order
            assert validated.validation_data["braid_ybe"] is True
            assert runtime.validation_data == {}
        spin1_validated = build_sl2_spin1_rmatrix(q)
        spin1_runtime = build_sl2_spin1_rmatrix(q, diagnostics=False)
        assert spin1_runtime.matrix == spin1_validated.matrix
        assert spin1_runtime.braid_matrix == spin1_validated.braid_matrix
        assert spin1_runtime.validation_data == {}


def test_cached_local_data_cannot_be_mutated_by_a_caller() -> None:
    q = sp.Integer(2)
    first = _builtin_rmatrix("sl2_fundamental", q)
    original = first.braid_matrix[0, 0]
    first.validation_data["tampered"] = True
    first.eigenvalue_channels[0]["channel_label"] = "tampered"
    second = _builtin_rmatrix("sl2_fundamental", q)
    assert second.braid_matrix[0, 0] == original
    assert second.validation_data == {}
    assert second.eigenvalue_channels[0]["channel_label"] == "J=1"


def test_unknot_scalar_fast_paths_equal_original_one_strand_pipelines() -> None:
    unknot = get_braid_example("unknot_1").to_braid_word()
    for q in (sp.Integer(2), sp.Symbol("q", nonzero=True)):
        sl2 = BraidOperatorBuilder(unknot, build_sl2_fundamental_rmatrix(q)).build()
        original_sl2 = compute_eyb_invariant(sl2, eyb_data=build_sl2_fundamental_eyb_data(q))
        assert current_sl2_unknot_normalization(q) == sp.simplify(original_sl2.eyb_normalized_expression)

        spin1 = BraidOperatorBuilder(unknot, build_sl2_spin1_rmatrix(q)).build()
        _data, _raw, _weighted, original_spin1 = compute_sl2_3d_candidate_unreduced_output(spin1, q=q)
        assert current_sl2_3d_unknot_normalization(q) == original_spin1


def test_candidate_branch_retains_validated_projector_metadata() -> None:
    q = sp.Integer(2)
    expected = build_sl2_spin1_rmatrix(q).validation_data["projector_checks"]
    result = evaluate_sl2_spin1_branch(get_braid_example("trefoil"), q=q)
    assert result.status == "candidate"
    assert result.metadata["projector_checks"] == expected


def test_reference_primary_outputs_remain_exact() -> None:
    trefoil = get_braid_example("trefoil")
    assert evaluate_sl2_fundamental_branch(trefoil, q=sp.Integer(2)).primary_output == sp.Rational(67, 256)
    assert evaluate_sl3_fundamental_branch(trefoil, q=sp.Integer(2)).primary_output == sp.Rational(5691, 16384)
    assert evaluate_sl2_spin1_branch(trefoil, q=sp.Integer(2)).primary_output == sp.Rational(266029, 65536)
