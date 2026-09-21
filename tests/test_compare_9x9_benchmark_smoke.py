"""Smoke tests for the 9x9-vs-9x9 discriminating-power benchmark."""

from __future__ import annotations

import unittest

import sympy as sp

from src.invariants.compare_9x9_benchmark import (
    DEFAULT_9X9_COMPARISON_PAIRS,
    NineByNineComparisonSummary,
    classify_9x9_pair,
    evaluate_default_9x9_discriminating_power,
    evaluate_9x9_pair,
)


FAST_Q = sp.Integer(2)


class TestCompare9x9BenchmarkSmoke(unittest.TestCase):
    def test_classification_helper_covers_all_cases(self) -> None:
        self.assertEqual(classify_9x9_pair(True, True), "both_distinguish")
        self.assertEqual(classify_9x9_pair(False, False), "neither_distinguishes")
        self.assertEqual(classify_9x9_pair(True, False), "only_sl2_3d_distinguishes")
        self.assertEqual(classify_9x9_pair(False, True), "only_sl3_distinguishes")

    def test_default_benchmark_returns_structured_summary(self) -> None:
        summary = evaluate_default_9x9_discriminating_power(q=FAST_Q)
        self.assertIsInstance(summary, NineByNineComparisonSummary)
        self.assertEqual(len(summary.pair_results), len(DEFAULT_9X9_COMPARISON_PAIRS))
        counts = summary.classification_counts()
        self.assertEqual(sum(counts.values()), len(summary.pair_results))

    def test_known_pairs_cover_multiple_classifications(self) -> None:
        benchmark_map = {
            pair_result.pair.label: pair_result
            for pair_result in evaluate_default_9x9_discriminating_power(q=FAST_Q).pair_results
        }
        self.assertEqual(benchmark_map["unknot_presentation_pair"].classification, "only_sl2_3d_distinguishes")
        self.assertEqual(benchmark_map["trefoil_vs_figure_eight"].classification, "both_distinguish")

    def test_individual_pair_report_has_branch_outputs(self) -> None:
        pair_result = evaluate_9x9_pair(DEFAULT_9X9_COMPARISON_PAIRS[0], q=FAST_Q)
        summary = pair_result.summary()
        self.assertIn("sl2 3D left", summary)
        self.assertIn("sl3 left", summary)