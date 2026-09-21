"""Logic-level synchronization tests for built-in example preview state in the GUI."""

from __future__ import annotations

import unittest

import sympy as sp

from src.gui.demo_launcher import (
    build_active_braid_preview_metadata,
    build_active_braid_state_from_entry,
    build_catalog_active_braid_state,
    build_entry_summary,
    evaluate_gui_active_braid,
)


FAST_Q = sp.Integer(2)


class TestGuiBuiltinPreviewSync(unittest.TestCase):
    def test_trefoil_builtin_active_braid_is_not_identity(self) -> None:
        active_braid = build_catalog_active_braid_state("trefoil")
        self.assertEqual(active_braid.source_mode, "catalog")
        self.assertNotEqual(active_braid.braid_word.word_string(), "identity")

    def test_figure_eight_builtin_active_braid_is_not_identity(self) -> None:
        active_braid = build_catalog_active_braid_state("figure_eight")
        self.assertEqual(active_braid.source_mode, "catalog")
        self.assertNotEqual(active_braid.braid_word.word_string(), "identity")

    def test_preview_metadata_matches_evaluator_input_for_trefoil_and_figure_eight(self) -> None:
        for example_label in ("trefoil", "figure_eight"):
            with self.subTest(example_label=example_label):
                active_braid = build_catalog_active_braid_state(example_label)
                preview_metadata = build_active_braid_preview_metadata(active_braid)
                entry = evaluate_gui_active_braid(active_braid, branch_ids=("sl2_fundamental", "sl2_spin1"), q=FAST_Q)
                evaluated_braid = build_active_braid_state_from_entry(entry)

                self.assertEqual(entry.example_label, example_label)
                self.assertTrue(all(result.braid_word == active_braid.braid_word for result in entry.branch_results))
                self.assertEqual(build_active_braid_preview_metadata(evaluated_braid), preview_metadata)

    def test_summary_tracks_the_same_active_braid_as_the_evaluator(self) -> None:
        active_braid = build_catalog_active_braid_state("figure_eight")
        entry = evaluate_gui_active_braid(active_braid, branch_ids=("sl2_fundamental", "sl3_fundamental"), q=FAST_Q)
        summary = build_entry_summary(entry)

        self.assertIn("Source mode: catalog", summary)
        self.assertIn("Label: figure_eight", summary)
        self.assertIn(f"Crossings: {len(active_braid.braid_word.generators)}", summary)
        self.assertIn(f"Word: {active_braid.braid_word.word_string()}", summary)
        self.assertIn(f"Writhe: {active_braid.braid_word.writhe()}", summary)
