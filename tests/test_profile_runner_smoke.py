"""Smoke tests for the benchmark experiment runner and summary layers."""

from __future__ import annotations

import unittest

import sympy as sp

from src.experiments.benchmark_registry import BenchmarkBraidSpec, BenchmarkPairDefinition
from src.experiments.profile_runner import observed_profile_from_relations, run_benchmark_pair
from src.experiments.profile_summary import build_benchmark_summary


FAST_Q = sp.Integer(2)


def _build_control_pair() -> BenchmarkPairDefinition:
    return BenchmarkPairDefinition(
        pair_id="P01",
        group="control",
        braid_a=BenchmarkBraidSpec(label="5_1", source="control A", num_strands=2, generators=(1, 1, 1, 1, 1)),
        braid_b=BenchmarkBraidSpec(label="5_1_stabilized", source="control B", num_strands=3, generators=(1, 1, 1, 1, 1, -2)),
        same_jones="yes",
        same_alexander_or_conway="yes",
        mutant="no",
        status_of_braid_source="safe",
        expected_sl2_fundamental="same",
        expected_sl2_3d_9x9="same",
        expected_sl3_fundamental="same",
        expected_profile="(0,0,0)",
        priority="high",
        notes="control pair",
    )


def _build_placeholder_pair() -> BenchmarkPairDefinition:
    return BenchmarkPairDefinition(
        pair_id="P05",
        group="mutation_placeholder",
        braid_a=BenchmarkBraidSpec(label="K11n34", source="placeholder", num_strands=0, generators=()),
        braid_b=BenchmarkBraidSpec(label="K11n42", source="placeholder", num_strands=0, generators=()),
        same_jones="yes",
        same_alexander_or_conway="yes",
        mutant="yes",
        status_of_braid_source="needs_audit",
        expected_sl2_fundamental="same",
        expected_sl2_3d_9x9="same",
        expected_sl3_fundamental="same",
        expected_profile="(0,0,0)",
        priority="high",
        notes="placeholder pair",
        warnings=("needs audit",),
    )


class TestProfileRunnerSmoke(unittest.TestCase):
    def test_observed_profile_helper_uses_fixed_branch_order(self) -> None:
        self.assertEqual(
            observed_profile_from_relations(
                {
                    "sl2_fundamental": "same",
                    "sl2_3d_9x9": "different",
                    "sl3_fundamental": "different",
                }
            ),
            "(0,1,1)",
        )

    def test_safe_control_pair_runs_and_reports_mismatch_when_metadata_is_not_realized(self) -> None:
        result = run_benchmark_pair(_build_control_pair(), q_parameter_expr=FAST_Q, q_parameter_text="2")

        self.assertEqual(result.status, "completed")
        self.assertEqual(result.observed_profile, "(0,1,0)")
        self.assertEqual(result.match_expected, "no")
        self.assertEqual(result.branch_result("sl2_fundamental").relation, "same")
        self.assertEqual(result.branch_result("sl2_3d_9x9").relation, "different")

    def test_needs_audit_placeholder_is_warned_and_skipped(self) -> None:
        result = run_benchmark_pair(_build_placeholder_pair(), q_parameter_expr=FAST_Q, q_parameter_text="2")

        self.assertEqual(result.status, "skipped")
        self.assertEqual(result.observed_profile, "skipped")
        self.assertEqual(result.match_expected, "partial")
        self.assertTrue(any(branch_result.relation == "skipped" for branch_result in result.branch_results))

    def test_summary_counts_profiles_skips_and_expected_match_states(self) -> None:
        summary = build_benchmark_summary(
            [
                run_benchmark_pair(_build_control_pair(), q_parameter_expr=FAST_Q, q_parameter_text="2"),
                run_benchmark_pair(_build_placeholder_pair(), q_parameter_expr=FAST_Q, q_parameter_text="2"),
            ],
            q_mode="2",
        )

        self.assertEqual(summary.profile_counts["(0,1,0)"], 1)
        self.assertEqual(summary.skipped_count, 1)
        self.assertEqual(summary.match_expected_counts["no"], 1)
        self.assertEqual(summary.match_expected_counts["partial"], 1)
