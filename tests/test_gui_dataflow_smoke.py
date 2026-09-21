"""Smoke tests for the GUI data flow that connects the Tkinter frontend to the invariant skeleton."""

from __future__ import annotations

import unittest

import sympy as sp
import tkinter as tk

from src.gui.demo_launcher import (
    DemoLauncherApp,
    build_custom_braid_word,
    build_entry_summary,
    build_program_status_text,
    evaluate_gui_example,
    evaluate_gui_custom_braid,
    filter_entry_by_branch_ids,
    get_default_gui_example_label,
    get_gui_branch_specs,
    get_gui_example_labels,
    get_gui_view_modes,
    parse_generator_text,
    render_entry_report,
)


Q = sp.Symbol("q", nonzero=True)
FAST_Q = sp.Integer(2)


class TestGuiDataflowSmoke(unittest.TestCase):
    def _create_tk_root(self) -> tk.Tk:
        try:
            return tk.Tk()
        except tk.TclError as exc:
            self.skipTest(f"Tk is unavailable in this test environment: {exc}")

    def test_default_gui_example_is_trefoil(self) -> None:
        self.assertEqual(get_default_gui_example_label(), "trefoil")
        self.assertEqual(get_gui_example_labels(), ("unknot_1", "trefoil", "figure_eight"))
        self.assertEqual(get_gui_view_modes(), ("formatter", "raw"))

    def test_parse_and_build_custom_braid_word(self) -> None:
        self.assertEqual(parse_generator_text("1, -2 1 -2"), (1, -2, 1, -2))
        braid_word = build_custom_braid_word(3, "1 -2 1 -2")
        self.assertEqual(braid_word.num_strands, 3)
        self.assertEqual(braid_word.generators, (1, -2, 1, -2))

        larger_braid_word = build_custom_braid_word(6, "1 -2 3 -4 5")
        self.assertEqual(larger_braid_word.num_strands, 6)
        self.assertEqual(larger_braid_word.generators, (1, -2, 3, -4, 5))

    def test_evaluate_gui_example_returns_multibranch_entry(self) -> None:
        entry = evaluate_gui_example("trefoil", q=Q)
        self.assertEqual(entry.example_label, "trefoil")
        self.assertEqual(len(entry.branch_results), 3)
        self.assertEqual(
            {result.branch_id for result in entry.branch_results},
            {"sl2_fundamental", "sl3_fundamental", "sl2_spin1"},
        )

    def test_evaluate_gui_custom_braid_returns_multibranch_entry(self) -> None:
        entry = evaluate_gui_custom_braid(3, "1 -2 1 -2", q=Q)
        self.assertEqual(entry.example_label, "custom_braid")
        self.assertEqual(len(entry.branch_results), 3)
        self.assertEqual(entry.metadata["input_mode"], "custom")

    def test_evaluate_gui_custom_braid_can_limit_selected_branches(self) -> None:
        entry = evaluate_gui_custom_braid(
            4,
            "2 2 2 1 -3 -2 -2 1 -2 1 -3",
            branch_ids=("sl2_fundamental",),
            q=FAST_Q,
        )
        self.assertEqual([result.branch_id for result in entry.branch_results], ["sl2_fundamental"])
        self.assertEqual(entry.metadata["selected_branch_ids"], ["sl2_fundamental"])

    def test_filter_entry_by_branch_ids_respects_toggle_selection(self) -> None:
        entry = evaluate_gui_example("figure_eight", q=Q)
        filtered = filter_entry_by_branch_ids(entry, ["sl2_fundamental", "sl2_spin1"])
        self.assertEqual(filtered.example_label, "figure_eight")
        self.assertEqual(len(filtered.branch_results), 2)
        self.assertEqual(
            [result.branch_id for result in filtered.branch_results],
            ["sl2_fundamental", "sl2_spin1"],
        )

    def test_report_views_and_summary_support_custom_and_catalog_entries(self) -> None:
        catalog_entry = evaluate_gui_example("trefoil", q=Q)
        custom_entry = evaluate_gui_custom_braid(2, "1 1 1", q=Q)
        formatter_report = render_entry_report(catalog_entry, view_mode="formatter")
        raw_report = render_entry_report(custom_entry, view_mode="raw")
        summary = build_entry_summary(custom_entry)

        self.assertIn("sl2_fundamental", formatter_report)
        self.assertIn('"branch_results"', raw_report)
        self.assertIn("Source mode: custom", summary)
        self.assertIn("Generators: [1, 1, 1]", summary)
        self.assertIn("Jones-compatible polynomial", summary)

    def test_program_status_text_matches_current_branch_contract(self) -> None:
        status_text = build_program_status_text()
        self.assertIn("Quick start:", status_text)
        self.assertIn("Jones / sl2 fundamental", status_text)
        self.assertIn("sl3 fundamental", status_text)
        self.assertIn("sl2 的3维表示下的9x9矩阵", status_text)
        self.assertIn("colored Jones candidate branch", status_text)
        self.assertIn("Knot Atlas", status_text)
        self.assertIn("n=2", status_text)
        self.assertIn("q^6 J_2(3_1; q^2)", status_text)
        self.assertEqual(len(get_gui_branch_specs()), 3)

    def test_branch_specs_expose_user_guidance_metadata(self) -> None:
        branch_specs = get_gui_branch_specs()
        self.assertEqual(branch_specs[0].title, "Jones / sl2 fundamental")
        self.assertIn("Jones-compatible", branch_specs[0].subtitle)
        self.assertEqual(branch_specs[2].title, "sl2 的3维表示下的9x9矩阵")
        self.assertIn("colored Jones candidate", branch_specs[2].subtitle)
        self.assertIn("Knot Atlas", branch_specs[2].subtitle)
        self.assertIn("q^6 J_2(3_1; q^2)", branch_specs[2].user_hint)

    def test_gui_class_exposes_explicit_apply_handlers(self) -> None:
        self.assertTrue(hasattr(DemoLauncherApp, "_apply_catalog_example"))
        self.assertTrue(hasattr(DemoLauncherApp, "_apply_custom_braid"))

    def test_catalog_selection_updates_pending_preview_state(self) -> None:
        root = self._create_tk_root()
        root.withdraw()
        try:
            app = DemoLauncherApp(root)
            app.input_mode_var.set("catalog")
            app.example_var.set("figure_eight")
            app._on_example_changed(None)
            self.assertIsNotNone(app.current_active_braid)
            self.assertEqual(app.current_active_braid.source_mode, "catalog")
            self.assertEqual(app.current_active_braid.source_label, "figure_eight")
            summary_text = app.summary_text.get("1.0", tk.END)
            self.assertIn("Label: figure_eight", summary_text)
            self.assertIn("Status: pending evaluation.", summary_text)
        finally:
            root.destroy()

    def test_loading_builtin_example_into_custom_updates_pending_preview_state(self) -> None:
        root = self._create_tk_root()
        root.withdraw()
        try:
            app = DemoLauncherApp(root)
            app.example_var.set("trefoil")
            app._load_example_into_custom()
            self.assertEqual(app.input_mode_var.get(), "custom")
            self.assertIsNotNone(app.current_active_braid)
            self.assertEqual(app.current_active_braid.source_mode, "custom")
            self.assertEqual(app.current_active_braid.braid_word.generators, (1, 1, 1))
            report_text = app.report_text.get("1.0", tk.END)
            self.assertIn("No report available yet.", report_text)
            self.assertIn("Word: sigma_1 sigma_1 sigma_1", report_text)
        finally:
            root.destroy()
