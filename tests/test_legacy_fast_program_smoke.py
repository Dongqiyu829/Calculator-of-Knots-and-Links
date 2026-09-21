"""Smoke tests for the preserved legacy fast backup program."""

from __future__ import annotations

import unittest

import sympy as sp

from src.catalog.braid_examples import get_braid_example
from src.gui.demo_launcher_legacy import legacy_evaluate_gui_example
from src.invariants.legacy_branch_registry import (
    LEGACY_SL2_3D_USER_FACING_NAME,
    evaluate_all_legacy_branches,
    evaluate_sl2_3d_legacy_raw_branch,
)
from src.invariants.legacy_multibranch_benchmark import LegacyMultiBranchBenchmarkEntry


FAST_Q = sp.Integer(2)


class TestLegacyFastProgramSmoke(unittest.TestCase):
    def test_legacy_sl2_3d_branch_keeps_raw_mode(self) -> None:
        result = evaluate_sl2_3d_legacy_raw_branch(get_braid_example("figure_eight"), q=FAST_Q)
        self.assertEqual(result.branch_id, "sl2_spin1")
        self.assertEqual(result.representation_name, LEGACY_SL2_3D_USER_FACING_NAME)
        self.assertEqual(result.status, "exploratory")
        self.assertEqual(result.primary_output_label, "Raw trace (legacy fast mode)")
        self.assertEqual(sp.simplify(result.primary_output - result.raw_trace), 0)

    def test_evaluate_all_legacy_branches_runs(self) -> None:
        results = evaluate_all_legacy_branches(get_braid_example("trefoil"), q=FAST_Q)
        self.assertEqual(len(results), 3)
        self.assertEqual({item.branch_id for item in results}, {"sl2_fundamental", "sl3_fundamental", "sl2_spin1"})

    def test_legacy_gui_entry_uses_legacy_program_mode(self) -> None:
        entry = legacy_evaluate_gui_example("unknot_1", q=FAST_Q)
        self.assertIsInstance(entry, LegacyMultiBranchBenchmarkEntry)
        self.assertEqual(entry.metadata.get("program_mode"), "legacy_fast")
        self.assertEqual(entry.branch_results[2].primary_output_label, "Raw trace (legacy fast mode)")