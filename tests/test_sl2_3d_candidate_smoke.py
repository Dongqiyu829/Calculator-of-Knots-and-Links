"""Smoke tests for the sl2 3-dimensional 9x9 colored-Jones candidate branch."""

from __future__ import annotations

import unittest

import sympy as sp

from src.catalog.braid_examples import get_braid_example
from src.invariants.branch_formatter import format_branch_result
from src.invariants.branch_registry import evaluate_all_current_branches, evaluate_sl2_spin1_branch
from src.invariants.sl2_3d_candidate_benchmark import evaluate_default_sl2_3d_candidate_benchmark
from src.invariants.sl2_3d_colored_jones_candidate import (
    SL2_3D_BRANCH_STATUS,
    SL2_3D_CANDIDATE_OUTPUT_LABEL,
    SL2_3D_USER_FACING_NAME,
    compute_sl2_3d_candidate_output,
)


Q = sp.Symbol("q", nonzero=True)
FAST_Q = sp.Integer(2)


class TestSl2ThreeDimCandidateSmoke(unittest.TestCase):
    def test_candidate_result_object_is_created(self) -> None:
        result = compute_sl2_3d_candidate_output(get_braid_example("trefoil").to_braid_word(), q=Q)
        self.assertEqual(result.representation_name, SL2_3D_USER_FACING_NAME)
        self.assertEqual(result.status, SL2_3D_BRANCH_STATUS)
        self.assertEqual(result.candidate_output_label, SL2_3D_CANDIDATE_OUTPUT_LABEL)

    def test_unknot_reduced_candidate_output_is_one(self) -> None:
        result = compute_sl2_3d_candidate_output(get_braid_example("unknot_1").to_braid_word(), q=Q)
        self.assertEqual(sp.simplify(result.reduced_candidate_output), sp.Integer(1))

    def test_trefoil_and_figure_eight_have_stable_reduced_candidate_outputs(self) -> None:
        trefoil = compute_sl2_3d_candidate_output(get_braid_example("trefoil").to_braid_word(), q=FAST_Q)
        figure_eight = compute_sl2_3d_candidate_output(get_braid_example("figure_eight").to_braid_word(), q=FAST_Q)
        self.assertNotEqual(sp.simplify(trefoil.reduced_candidate_output), sp.Integer(0))
        self.assertNotEqual(sp.simplify(figure_eight.reduced_candidate_output), sp.Integer(0))

    def test_default_candidate_benchmark_runs(self) -> None:
        benchmark_entries = evaluate_default_sl2_3d_candidate_benchmark(q=FAST_Q)
        self.assertEqual([entry.example_label for entry in benchmark_entries], ["unknot_1", "trefoil", "figure_eight"])
        self.assertTrue(all(entry.result.status == "candidate" for entry in benchmark_entries))

    def test_branch_registry_and_formatter_expose_candidate_branch(self) -> None:
        branch_result = evaluate_sl2_spin1_branch(get_braid_example("trefoil"), q=FAST_Q)
        formatted = format_branch_result(branch_result)
        self.assertEqual(branch_result.status, "candidate")
        self.assertEqual(branch_result.primary_output_label, "Colored Jones candidate output")
        self.assertIn("Reduced candidate output", formatted)

    def test_multibranch_registry_keeps_candidate_branch_stable(self) -> None:
        branch_results = evaluate_all_current_branches(get_braid_example("figure_eight"), q=FAST_Q)
        branch_map = {result.branch_id: result for result in branch_results}
        self.assertIn("sl2_spin1", branch_map)
        self.assertEqual(branch_map["sl2_spin1"].status, "candidate")
        self.assertEqual(branch_map["sl2_spin1"].representation_name, SL2_3D_USER_FACING_NAME)