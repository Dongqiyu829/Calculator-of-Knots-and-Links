"""Regression tests for the current braid-side EYB stabilization normalization.

These tests lock down the current braid-side normalization as an implementation
target. Passing these tests does not by itself imply that the raw-side
partial-trace theorem has been fully unified with the braid-side convention.
"""

from __future__ import annotations

import unittest

import sympy as sp

from src.catalog.braid_examples import get_braid_example
from src.invariants.convention_audit import build_braid_side_convention_data
from src.invariants.eyb_diagnostics import diagnose_stabilization
from src.invariants.eyb_invariant import build_sl2_fundamental_eyb_data, build_sl3_fundamental_eyb_data
from src.rmatrix.sl2_rmatrix import build_sl2_fundamental_rmatrix
from src.rmatrix.sl3_rmatrix import build_sl3_fundamental_rmatrix


Q = sp.Symbol("q", nonzero=True)
EXAMPLE_LABELS = ("unknot_1", "trefoil", "figure_eight")


class TestEYBStabilizationRegression(unittest.TestCase):
    """Check that the current braid-side EYB normalization keeps stabilization ratios at 1."""

    def test_sl2_fundamental_stabilization_ratios(self) -> None:
        """Current braid-side P2-type normalization should pass stabilization regression."""

        convention = build_braid_side_convention_data(
            rmatrix_builder=build_sl2_fundamental_rmatrix,
            eyb_builder=build_sl2_fundamental_eyb_data,
            q=Q,
        )
        self.assertTrue(convention.stabilization_verified)

        for label in EXAMPLE_LABELS:
            with self.subTest(representation="sl2 fundamental", example=label):
                diagnostic = diagnose_stabilization(
                    get_braid_example(label),
                    rmatrix_builder=build_sl2_fundamental_rmatrix,
                    eyb_builder=build_sl2_fundamental_eyb_data,
                    local_object_label="braid_matrix",
                    q=Q,
                )
                self.assertTrue(diagnostic.positive_is_one)
                self.assertTrue(diagnostic.negative_is_one)

    def test_sl3_fundamental_stabilization_ratios(self) -> None:
        """Current braid-side P3-type normalization should pass stabilization regression."""

        convention = build_braid_side_convention_data(
            rmatrix_builder=build_sl3_fundamental_rmatrix,
            eyb_builder=build_sl3_fundamental_eyb_data,
            q=Q,
        )
        self.assertTrue(convention.stabilization_verified)

        for label in EXAMPLE_LABELS:
            with self.subTest(representation="sl3 fundamental", example=label):
                diagnostic = diagnose_stabilization(
                    get_braid_example(label),
                    rmatrix_builder=build_sl3_fundamental_rmatrix,
                    eyb_builder=build_sl3_fundamental_eyb_data,
                    local_object_label="braid_matrix",
                    q=Q,
                )
                self.assertTrue(diagnostic.positive_is_one)
                self.assertTrue(diagnostic.negative_is_one)