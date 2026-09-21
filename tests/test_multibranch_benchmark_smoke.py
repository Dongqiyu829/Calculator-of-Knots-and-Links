"""Smoke tests for the unified multi-branch invariant program skeleton."""

from __future__ import annotations

import unittest

import sympy as sp

from src.catalog.braid_examples import get_braid_example
from src.invariants.branch_registry import (
    evaluate_all_current_branches,
    evaluate_sl2_fundamental_branch,
    evaluate_sl2_spin1_branch,
    evaluate_sl3_fundamental_branch,
)
from src.invariants.branch_results import InvariantBranchResult
from src.invariants.jones_invariant import DEFAULT_JONES_VARIABLE_CONVENTION
from src.invariants.multibranch_benchmark import (
    MultiBranchBenchmarkEntry,
    evaluate_catalog_across_branches,
)


Q = sp.Symbol("q", nonzero=True)
T = sp.Symbol("t")


class TestMultiBranchBenchmarkSmoke(unittest.TestCase):
    def test_branch_evaluators_create_unified_results(self) -> None:
        example = get_braid_example("unknot_1")
        results = [
            evaluate_sl2_fundamental_branch(example, q=Q),
            evaluate_sl3_fundamental_branch(example, q=Q),
            evaluate_sl2_spin1_branch(example, q=Q),
        ]
        for result in results:
            self.assertIsInstance(result, InvariantBranchResult)
            self.assertEqual(result.braid_word.label, "unknot_1")

    def test_evaluate_all_current_branches_runs(self) -> None:
        results = evaluate_all_current_branches(get_braid_example("trefoil"), q=Q)
        self.assertEqual(len(results), 3)
        self.assertEqual({item.branch_id for item in results}, {"sl2_fundamental", "sl3_fundamental", "sl2_spin1"})

    def test_evaluate_catalog_across_branches_runs(self) -> None:
        entries = evaluate_catalog_across_branches(
            [get_braid_example("unknot_1"), get_braid_example("trefoil")],
            q=Q,
        )
        self.assertEqual(len(entries), 2)
        self.assertTrue(all(isinstance(entry, MultiBranchBenchmarkEntry) for entry in entries))

    def test_sl2_fundamental_branch_keeps_jones_regression(self) -> None:
        unknot = evaluate_sl2_fundamental_branch(get_braid_example("unknot_1"), q=Q)
        trefoil = evaluate_sl2_fundamental_branch(get_braid_example("trefoil"), q=Q)
        figure_eight = evaluate_sl2_fundamental_branch(get_braid_example("figure_eight"), q=Q)
        trefoil_target = sp.sympify("t + t**3 - t**4").subs(T, Q**-2)
        figure_eight_target = sp.sympify("t**2 - t + 1 - t**-1 + t**-2").subs(T, Q**-2)

        self.assertEqual(sp.simplify(unknot.primary_output - 1), 0)
        self.assertEqual(sp.simplify(trefoil.primary_output - trefoil_target), 0)
        self.assertEqual(sp.simplify(figure_eight.primary_output - figure_eight_target), 0)
        self.assertEqual(trefoil.variable_convention, DEFAULT_JONES_VARIABLE_CONVENTION)

    def test_sl3_fundamental_branch_smoke(self) -> None:
        result = evaluate_sl3_fundamental_branch(get_braid_example("figure_eight"), q=Q)
        self.assertEqual(result.status, "formal")
        self.assertEqual(result.primary_output_label, "P3-type EYB output")
        self.assertIsNotNone(result.primary_output)

    def test_sl2_spin1_branch_smoke(self) -> None:
        result = evaluate_sl2_spin1_branch(get_braid_example("figure_eight"), q=Q)
        self.assertEqual(result.status, "candidate")
        self.assertEqual(result.primary_output_label, "Colored Jones candidate output")
        self.assertEqual(result.representation_name, "sl2 的3维表示下的9x9矩阵")
        self.assertIn("reduced_candidate_output", result.metadata)
        self.assertIsNotNone(result.primary_output)