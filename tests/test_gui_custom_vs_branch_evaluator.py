"""Consistency checks between GUI custom braid helpers and the formal branch evaluators."""

from __future__ import annotations

import unittest

import sympy as sp

from src.braid.braid_word import BraidWord
from src.gui.demo_launcher_legacy import legacy_evaluate_gui_custom_braid
from src.invariants.branch_registry import evaluate_sl2_fundamental_branch


Q = sp.Symbol("q", nonzero=True)


def _assert_sl2_outputs_match(
    test_case: unittest.TestCase,
    *,
    num_strands: int,
    generators: tuple[int, ...],
    label: str,
) -> None:
    braid_word = BraidWord.from_iterable(num_strands=num_strands, generators=generators, label=label)
    formal_result = evaluate_sl2_fundamental_branch(braid_word, q=Q)
    legacy_entry = legacy_evaluate_gui_custom_braid(
        num_strands,
        " ".join(str(item) for item in generators),
        branch_ids=("sl2_fundamental",),
        q=Q,
    )
    legacy_result = legacy_entry.branch_results[0]
    difference = sp.simplify(formal_result.primary_output - legacy_result.primary_output)
    test_case.assertEqual(
        difference,
        0,
        msg=(
            f"sl2 fundamental mismatch for {label}: "
            f"formal={sp.simplify(formal_result.primary_output)}, "
            f"legacy={sp.simplify(legacy_result.primary_output)}, "
            f"difference={difference}"
        ),
    )


class TestGuiCustomVsBranchEvaluator(unittest.TestCase):
    def test_simple_custom_braid_matches_formal_sl2_branch(self) -> None:
        _assert_sl2_outputs_match(
            self,
            num_strands=2,
            generators=(1, 1, 1),
            label="simple_trefoil_word",
        )

    def test_10_22_custom_braid_matches_formal_sl2_branch(self) -> None:
        _assert_sl2_outputs_match(
            self,
            num_strands=4,
            generators=(1, -3, -3, 2, 2, 2, -3, 2, 1, -2, -3),
            label="10_22",
        )

    def test_10_35_custom_braid_matches_formal_sl2_branch(self) -> None:
        _assert_sl2_outputs_match(
            self,
            num_strands=6,
            generators=(1, -2, -3, 2, 4, -3, -5, 4, -5, 1, -2),
            label="10_35",
        )