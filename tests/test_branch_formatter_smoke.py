"""Smoke tests for the shared branch formatter/report layer."""

from __future__ import annotations

import unittest

import sympy as sp

from src.catalog.braid_examples import get_braid_example
from src.invariants.branch_formatter import (
    format_branch_result,
    format_catalog_benchmark,
    format_multibranch_entry,
)
from src.invariants.branch_registry import evaluate_all_current_branches
from src.invariants.multibranch_benchmark import (
    evaluate_catalog_across_branches,
    evaluate_example_across_branches,
)


Q = sp.Symbol("q", nonzero=True)


class TestBranchFormatterSmoke(unittest.TestCase):
    def test_format_branch_result_handles_all_current_branches(self) -> None:
        branch_results = evaluate_all_current_branches(get_braid_example("trefoil"), q=Q)
        for branch_result in branch_results:
            formatted = format_branch_result(branch_result)
            self.assertIn(branch_result.branch_id, formatted)
            self.assertIn(branch_result.status, formatted)
            self.assertIn(branch_result.primary_output_label, formatted)
            self.assertIn(str(sp.simplify(branch_result.primary_output)), formatted)

    def test_format_multibranch_entry_handles_complete_entry(self) -> None:
        entry = evaluate_example_across_branches(get_braid_example("unknot_1"), q=Q)
        formatted = format_multibranch_entry(entry)
        self.assertIn(entry.example_label, formatted)
        self.assertIn("sl2_fundamental", formatted)
        self.assertIn("sl3_fundamental", formatted)
        self.assertIn("sl2_spin1", formatted)

    def test_format_catalog_benchmark_handles_multiple_entries(self) -> None:
        entries = evaluate_catalog_across_branches(
            [get_braid_example("unknot_1"), get_braid_example("figure_eight")],
            q=Q,
        )
        formatted = format_catalog_benchmark(entries)
        self.assertIn("Multi-branch invariant report", formatted)
        self.assertIn("unknot_1", formatted)
        self.assertIn("figure_eight", formatted)