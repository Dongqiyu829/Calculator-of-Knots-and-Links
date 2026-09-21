"""Smoke tests for the ordinary braid workbench GUI helpers."""

from __future__ import annotations

import json
import unittest

import sympy as sp
import tkinter as tk

from src.catalog.braid_examples import get_braid_example
from src.gui.braid_workbench import (
    BraidWorkbenchApp,
    evaluate_single_workbench_braid,
    get_workbench_example_labels,
    parse_workbench_q_parameter,
)


class TestBraidWorkbenchGuiSmoke(unittest.TestCase):
    def _create_tk_root(self) -> tk.Tk:
        try:
            return tk.Tk()
        except tk.TclError as exc:
            self.skipTest(f"Tk is unavailable in this test environment: {exc}")

    def test_workbench_example_labels_include_standard_examples(self) -> None:
        labels = get_workbench_example_labels()
        self.assertIn("trefoil", labels)
        self.assertIn("figure_eight", labels)
        self.assertIn("unknot_1", labels)

    def test_workbench_q_parser_supports_fast_numeric_and_symbolic_modes(self) -> None:
        self.assertEqual(parse_workbench_q_parameter("2"), sp.Integer(2))
        self.assertEqual(str(parse_workbench_q_parameter("q")), "q")

    def test_single_workbench_evaluator_runs_all_three_branches(self) -> None:
        entry = evaluate_single_workbench_braid(get_braid_example("trefoil").to_braid_word(), q=sp.Integer(2))
        self.assertEqual(len(entry.branch_results), 3)
        self.assertEqual({result.branch_id for result in entry.branch_results}, {"sl2_fundamental", "sl3_fundamental", "sl2_spin1"})

    def test_workbench_gui_class_exposes_primary_actions(self) -> None:
        self.assertTrue(hasattr(BraidWorkbenchApp, "_run_manual_batch"))
        self.assertTrue(hasattr(BraidWorkbenchApp, "_run_json_batch"))
        self.assertTrue(hasattr(BraidWorkbenchApp, "_append_current_results_to_log"))

    def test_loading_builtin_example_updates_manual_card(self) -> None:
        root = self._create_tk_root()
        root.withdraw()
        try:
            app = BraidWorkbenchApp(root)
            card = app.manual_cards[0]
            card.example_var.set("figure_eight")
            app._load_example_into_manual_card(card)
            self.assertEqual(card.label_var.get(), "figure_eight")
            self.assertEqual(card.num_strands_var.get(), 3)
            self.assertEqual(card.generators_var.get(), "1 -2 1 -2")
        finally:
            root.destroy()

    def test_manual_batch_run_populates_unified_results_tables(self) -> None:
        root = self._create_tk_root()
        root.withdraw()
        try:
            app = BraidWorkbenchApp(root)
            app.manual_comparison_mode_var.set("all")
            app._run_manual_batch()
            self.assertIsNotNone(app.current_run_result)
            self.assertEqual(app.current_run_result.run_spec.input_source, "manual")
            self.assertEqual(len(app.current_run_result.table_rows("single")), 2)
            self.assertEqual(len(app.current_run_result.table_rows("pairwise")), 1)
            self.assertEqual(len(app.current_run_result.table_rows("summary")), 1)
        finally:
            root.destroy()

    def test_json_batch_run_uses_same_results_pipeline(self) -> None:
        root = self._create_tk_root()
        root.withdraw()
        try:
            app = BraidWorkbenchApp(root)
            payload = {
                "q_parameter": "2",
                "models": ["sl2_fundamental", "sl2_3d_9x9", "sl3_fundamental"],
                "comparison_mode": "pairwise",
                "braids": [
                    {"label": "A", "num_strands": 3, "generators": [1, 2, 1]},
                    {"label": "B", "num_strands": 3, "generators": [2, 1, 2]},
                ],
            }
            app.json_text.delete("1.0", tk.END)
            app.json_text.insert(tk.END, json.dumps(payload))
            app._load_json_input()
            app._run_json_batch()
            self.assertIsNotNone(app.current_run_result)
            self.assertEqual(app.current_run_result.run_spec.input_source, "json")
            self.assertEqual(len(app.current_run_result.table_rows("single")), 2)
            self.assertEqual(len(app.current_run_result.table_rows("pairwise")), 1)
        finally:
            root.destroy()

    def test_current_results_can_be_added_to_log_with_manual_source(self) -> None:
        root = self._create_tk_root()
        root.withdraw()
        try:
            app = BraidWorkbenchApp(root)
            app.manual_comparison_mode_var.set("pairwise")
            app._run_manual_batch()
            app._append_current_results_to_log()
            self.assertEqual(len(app.experiment_log.records), 1)
            self.assertEqual(app.experiment_log.records[0].input_source, "manual")
        finally:
            root.destroy()

    def test_display_mode_switch_keeps_manual_preview_renderable(self) -> None:
        root = self._create_tk_root()
        root.withdraw()
        try:
            app = BraidWorkbenchApp(root)
            app.display_mode_var.set("presentation")
            app._refresh_all_manual_previews()
            self.assertGreater(len(app.manual_cards[0].preview_canvas.find_all()), 0)
        finally:
            root.destroy()
