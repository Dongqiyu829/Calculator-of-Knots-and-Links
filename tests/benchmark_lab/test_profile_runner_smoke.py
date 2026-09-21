"""Smoke tests for benchmark_lab.profile_runner and summary."""

from __future__ import annotations

import unittest

import sympy as sp

from src.benchmark_lab.profile_runner import build_observed_profile, run_pair_profile
from src.benchmark_lab.profile_summary import build_profile_summary
from src.benchmark_lab.registry import BenchmarkBraidSide, BenchmarkPairDefinition


FAST_Q = sp.Integer(2)


def _control_pair() -> BenchmarkPairDefinition:
    return BenchmarkPairDefinition(
        pair_id="P01",
        group="control",
        braid_a=BenchmarkBraidSide(label="5_1", source="control A", num_strands=2, generators=(1, 1, 1, 1, 1)),
        braid_b=BenchmarkBraidSide(label="5_1_stabilized", source="control B", num_strands=3, generators=(1, 1, 1, 1, 1, -2)),
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


def _placeholder_pair() -> BenchmarkPairDefinition:
    return BenchmarkPairDefinition(
        pair_id="P05",
        group="mutation_placeholder",
        braid_a=BenchmarkBraidSide(label="K11n34", source="placeholder", num_strands=0, generators=()),
        braid_b=BenchmarkBraidSide(label="K11n42", source="placeholder", num_strands=0, generators=()),
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


class TestBenchmarkLabProfileRunnerSmoke(unittest.TestCase):
    def test_observed_profile_uses_fixed_model_order(self) -> None:
        self.assertEqual(
            build_observed_profile(
                {
                    "sl2_fundamental": "same",
                    "sl2_3d_9x9": "different",
                    "sl3_fundamental": "different",
                }
            ),
            "(0,1,1)",
        )

    def test_control_pair_reports_actual_mismatch_without_hiding_it(self) -> None:
        result = run_pair_profile(_control_pair(), q_parameter=FAST_Q, q_mode="2")
        self.assertEqual(result.status, "completed")
        self.assertEqual(result.observed_profile, "(0,1,0)")
        self.assertEqual(result.match_expected, "no")
        self.assertEqual(result.branch_record("sl2_fundamental").relation, "same")
        self.assertEqual(result.branch_record("sl2_3d_9x9").relation, "different")

    def test_placeholder_pair_warns_and_skips(self) -> None:
        result = run_pair_profile(_placeholder_pair(), q_parameter=FAST_Q, q_mode="2")
        self.assertEqual(result.status, "skipped")
        self.assertEqual(result.observed_profile, "skipped")
        self.assertEqual(result.match_expected, "partial")

    def test_summary_counts_observed_profiles_and_skips(self) -> None:
        summary = build_profile_summary(
            [
                run_pair_profile(_control_pair(), q_parameter=FAST_Q, q_mode="2"),
                run_pair_profile(_placeholder_pair(), q_parameter=FAST_Q, q_mode="2"),
            ],
            q_mode="2",
        )
        self.assertEqual(summary.profile_counts["(0,1,0)"], 1)
        self.assertEqual(summary.skipped_count, 1)
        self.assertEqual(summary.match_expected_counts["no"], 1)
        self.assertEqual(summary.match_expected_counts["partial"], 1)
