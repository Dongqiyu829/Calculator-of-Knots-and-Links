"""Smoke tests for the braid workbench comparison data layer."""

from __future__ import annotations

import unittest

import sympy as sp

from src.catalog.braid_examples import get_braid_example
from src.workbench.comparison import (
    WORKBENCH_CLASSIFICATION_LABELS,
    classify_workbench_pair,
    evaluate_workbench_pair,
)


FAST_Q = sp.Integer(2)


class TestBraidWorkbenchComparisonSmoke(unittest.TestCase):
    def test_classification_function_covers_all_declared_labels(self) -> None:
        observed = {
            classify_workbench_pair(jones_same, sl2_same, sl3_same)
            for jones_same in (True, False)
            for sl2_same in (True, False)
            for sl3_same in (True, False)
        }
        self.assertEqual(observed, set(WORKBENCH_CLASSIFICATION_LABELS))

    def test_same_braid_pair_is_classified_as_all_same(self) -> None:
        braid = get_braid_example("trefoil").to_braid_word()
        comparison = evaluate_workbench_pair(braid, braid, q=FAST_Q)
        self.assertTrue(comparison.jones_same)
        self.assertTrue(comparison.sl2_3d_same)
        self.assertTrue(comparison.sl3_same)
        self.assertEqual(comparison.classification, "all_same")

    def test_trefoil_vs_figure_eight_is_all_different_in_fast_mode(self) -> None:
        comparison = evaluate_workbench_pair(
            get_braid_example("trefoil").to_braid_word(),
            get_braid_example("figure_eight").to_braid_word(),
            q=FAST_Q,
        )
        self.assertFalse(comparison.jones_same)
        self.assertFalse(comparison.sl2_3d_same)
        self.assertFalse(comparison.sl3_same)
        self.assertEqual(comparison.classification, "all_different")
