"""Catalog regression checks for the sl2 3-dimensional 9x9 candidate branch."""

from __future__ import annotations

import unittest

import sympy as sp

from src.catalog.braid_examples import get_braid_example
from src.invariants.branch_formatter import format_branch_result
from src.invariants.branch_registry import evaluate_current_branches, evaluate_sl2_spin1_branch
from src.invariants.sl2_3d_colored_jones_candidate import (
    SL2_3D_BRANCH_STATUS,
    SL2_3D_CANDIDATE_OUTPUT_LABEL,
    compute_sl2_3d_candidate_output,
)


Q = sp.Symbol("q", nonzero=True)
FAST_Q = sp.Integer(2)


class TestSl2ThreeDimCandidateCatalogRegression(unittest.TestCase):
    def test_unknot_candidate_branch_reduces_to_one_across_layers(self) -> None:
        example = get_braid_example("unknot_1")
        evaluator_result = compute_sl2_3d_candidate_output(example.to_braid_word(), q=Q)
        branch_result = evaluate_sl2_spin1_branch(example, q=Q)
        registry_result = evaluate_current_branches(example, branch_ids=("sl2_spin1",), q=Q)[0]
        formatted = format_branch_result(registry_result)

        self.assertEqual(sp.simplify(evaluator_result.reduced_candidate_output), sp.Integer(1))
        self.assertEqual(sp.simplify(branch_result.primary_output), sp.Integer(1))
        self.assertEqual(sp.simplify(registry_result.primary_output), sp.Integer(1))
        self.assertEqual(branch_result.status, SL2_3D_BRANCH_STATUS)
        self.assertEqual(branch_result.primary_output_label, SL2_3D_CANDIDATE_OUTPUT_LABEL)
        self.assertIn("Primary output label: Colored Jones candidate output", formatted)
        self.assertIn("Reduced candidate output: 1", formatted)

    def test_trefoil_candidate_branch_is_consistent_across_evaluator_registry_and_formatter(self) -> None:
        self._assert_nontrivial_candidate_branch("trefoil")

    def test_figure_eight_candidate_branch_is_consistent_across_evaluator_registry_and_formatter(self) -> None:
        self._assert_nontrivial_candidate_branch("figure_eight")

    def _assert_nontrivial_candidate_branch(self, example_label: str) -> None:
        example = get_braid_example(example_label)
        evaluator_result = compute_sl2_3d_candidate_output(example.to_braid_word(), q=FAST_Q)
        branch_result = evaluate_sl2_spin1_branch(example, q=FAST_Q)
        registry_result = evaluate_current_branches(example, branch_ids=("sl2_spin1",), q=FAST_Q)[0]
        formatted = format_branch_result(registry_result)

        self.assertEqual(branch_result.status, SL2_3D_BRANCH_STATUS)
        self.assertEqual(registry_result.status, SL2_3D_BRANCH_STATUS)
        self.assertEqual(branch_result.primary_output_label, SL2_3D_CANDIDATE_OUTPUT_LABEL)
        self.assertEqual(registry_result.primary_output_label, SL2_3D_CANDIDATE_OUTPUT_LABEL)
        self.assertEqual(
            sp.simplify(branch_result.primary_output),
            sp.simplify(evaluator_result.reduced_candidate_output),
        )
        self.assertEqual(
            sp.simplify(registry_result.primary_output),
            sp.simplify(evaluator_result.reduced_candidate_output),
        )
        self.assertNotEqual(
            sp.simplify(branch_result.primary_output - branch_result.raw_trace),
            sp.Integer(0),
        )
        self.assertIn("Status: candidate", formatted)
        self.assertIn("Primary output label: Colored Jones candidate output", formatted)
        self.assertIn("Reduced candidate output:", formatted)
        self.assertIn(str(sp.simplify(branch_result.primary_output)), formatted)
