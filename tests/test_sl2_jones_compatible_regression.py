"""Formal regression tests for the sl2 fundamental Jones-compatible output layer."""

from __future__ import annotations

import unittest

import sympy as sp

from src.catalog.braid_examples import get_braid_example
from src.invariants.jones_invariant import (
    DEFAULT_JONES_VARIABLE_CONVENTION,
    compute_sl2_jones_compatible_output,
)


Q = sp.Symbol("q", nonzero=True)
T = sp.Symbol("t")


class TestSL2JonesCompatibleRegression(unittest.TestCase):
    """Lock down the formal sl2 reduced-P2 / Jones-compatible branch."""

    def test_unknot_reduced_output_is_one(self) -> None:
        result = compute_sl2_jones_compatible_output(get_braid_example("unknot_1").to_braid_word(), q=Q)
        self.assertEqual(sp.simplify(result.reduced_p2_output - 1), 0)
        self.assertEqual(sp.simplify(result.jones_compatible_output - 1), 0)
        self.assertEqual(result.variable_convention, DEFAULT_JONES_VARIABLE_CONVENTION)

    def test_trefoil_matches_default_convention_target(self) -> None:
        result = compute_sl2_jones_compatible_output(get_braid_example("trefoil").to_braid_word(), q=Q)
        target = sp.sympify("t + t**3 - t**4").subs(T, Q**-2)
        self.assertEqual(sp.simplify(result.reduced_p2_output - target), 0)
        self.assertEqual(sp.simplify(result.jones_compatible_output - target), 0)
        self.assertEqual(result.variable_convention, DEFAULT_JONES_VARIABLE_CONVENTION)

    def test_figure_eight_matches_default_convention_target(self) -> None:
        result = compute_sl2_jones_compatible_output(get_braid_example("figure_eight").to_braid_word(), q=Q)
        target = sp.sympify("t**2 - t + 1 - t**-1 + t**-2").subs(T, Q**-2)
        self.assertEqual(sp.simplify(result.reduced_p2_output - target), 0)
        self.assertEqual(sp.simplify(result.jones_compatible_output - target), 0)
        self.assertEqual(result.variable_convention, DEFAULT_JONES_VARIABLE_CONVENTION)