"""Smoke tests for benchmark_lab.audit."""

from __future__ import annotations

import unittest

import sympy as sp

from src.benchmark_lab.audit import audit_pair, build_comparison_details
from src.benchmark_lab.registry import BenchmarkBraidSide, BenchmarkPairDefinition


FAST_Q = sp.Integer(2)


def _pair_p01() -> BenchmarkPairDefinition:
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
        notes="audit pair P01",
    )


def _pair_p04() -> BenchmarkPairDefinition:
    return BenchmarkPairDefinition(
        pair_id="P04",
        group="negative",
        braid_a=BenchmarkBraidSide(label="5_1", source="negative A", num_strands=2, generators=(1, 1, 1, 1, 1)),
        braid_b=BenchmarkBraidSide(label="10_132", source="negative B", num_strands=4, generators=(1, 1, 1, -2, -1, -1, -2, -3, 2, -3, -3)),
        same_jones="yes",
        same_alexander_or_conway="yes",
        mutant="no",
        status_of_braid_source="safe",
        expected_sl2_fundamental="same",
        expected_sl2_3d_9x9="same",
        expected_sl3_fundamental="same",
        expected_profile="(0,0,0)",
        priority="high",
        notes="audit pair P04",
    )


class TestBenchmarkLabAuditSmoke(unittest.TestCase):
    def test_symbolic_comparison_details_report_simplified_difference(self) -> None:
        q = sp.Symbol("q", nonzero=True)
        details = build_comparison_details(q + 1, q + 1, q_mode="q")
        self.assertEqual(details["relation"], "same")
        self.assertEqual(details["symbolic_difference"], "0")

    def test_audit_supports_p01_numeric_case(self) -> None:
        record = audit_pair(_pair_p01(), q_parameter=FAST_Q, q_mode="2")
        self.assertEqual(record.status, "completed")
        self.assertEqual(record.pair_id, "P01")
        self.assertEqual(len(record.branch_audits), 3)
        self.assertIn("num_strands", record.to_markdown())

    def test_audit_supports_p04_numeric_case(self) -> None:
        record = audit_pair(_pair_p04(), q_parameter=FAST_Q, q_mode="2")
        self.assertEqual(record.status, "completed")
        self.assertEqual(record.pair_id, "P04")
        self.assertEqual(len(record.branch_audits), 3)
