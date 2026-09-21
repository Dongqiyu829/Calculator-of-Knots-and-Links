"""Smoke tests for the Jones debug tooling.

These tests only check that the debug layer is structurally usable. They do not
assert that the current P2-type output has already been aligned with a standard
Jones convention.
"""

from __future__ import annotations

import unittest

import sympy as sp

from src.invariants.jones_debug import (
    compare_current_p2_with_jones,
    convert_target_to_q,
    current_p2_unknot_normalization,
    reduce_current_p2_output,
    support_signature,
)
from src.invariants.jones_reference_cases import JonesReferenceCase, get_jones_reference_case


Q = sp.Symbol("q", nonzero=True)


class TestJonesDebugSmoke(unittest.TestCase):
    """Check that the Jones debug layer runs and handles missing targets safely."""

    def test_support_signature_runs(self) -> None:
        signature = support_signature(Q**3 + 2 * Q**-1 + 1, Q)
        self.assertEqual(signature.term_count, 3)
        self.assertEqual(signature.exponents, (-1, 0, 3))

    def test_convert_target_to_q_runs(self) -> None:
        converted = convert_target_to_q("t**2 + t + 1", "t", "t=q**-2")
        self.assertEqual(sp.simplify(converted - (Q**-4 + Q**-2 + 1)), 0)

    def test_comparison_object_can_be_created(self) -> None:
        result = compare_current_p2_with_jones(get_jones_reference_case("unknot_1"))
        self.assertEqual(result.example_label, "unknot_1")
        self.assertGreaterEqual(result.term_count_current, 1)
        self.assertEqual(sp.simplify(result.current_reduced_p2_output - 1), 0)
        self.assertGreaterEqual(result.term_count_current_reduced, 1)

    def test_current_unknot_reduction_factor(self) -> None:
        normalization = current_p2_unknot_normalization(Q)
        self.assertEqual(sp.simplify(normalization - (Q + Q**-1)), 0)

    def test_reduce_current_p2_output_runs(self) -> None:
        reduced = reduce_current_p2_output(Q + Q**-1, Q)
        self.assertEqual(sp.simplify(reduced - 1), 0)

    def test_missing_target_does_not_crash(self) -> None:
        case = get_jones_reference_case("trefoil")
        result = compare_current_p2_with_jones(case)
        self.assertIsNone(result.target_expression)
        self.assertEqual(len(result.exact_matches), 0)
        self.assertIn("Target Jones reference is missing", result.diagnosis_summary)

    def test_manual_placeholder_case_is_allowed(self) -> None:
        case = JonesReferenceCase(
            label="manual",
            braid_word=get_jones_reference_case("unknot_1").braid_word,
            target_expression=None,
            variable_name="t",
            convention_label="manual placeholder",
        )
        result = compare_current_p2_with_jones(case)
        self.assertEqual(result.example_label, "manual")