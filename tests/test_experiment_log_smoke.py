"""Smoke tests for the workbench experiment-log export helpers."""

from __future__ import annotations

import unittest

import sympy as sp

from src.catalog.braid_examples import get_braid_example
from src.workbench.comparison import evaluate_workbench_pair
from src.workbench.experiment_log import EXPERIMENT_LOG_FIELD_NAMES, ExperimentLog


FAST_Q = sp.Integer(2)


class TestExperimentLogSmoke(unittest.TestCase):
    def test_experiment_log_record_contains_requested_fields(self) -> None:
        comparison = evaluate_workbench_pair(
            get_braid_example("trefoil").to_braid_word(),
            get_braid_example("figure_eight").to_braid_word(),
            q=FAST_Q,
        )
        experiment_log = ExperimentLog()
        record = experiment_log.add_comparison_result(comparison, label="trefoil_vs_figure_eight", notes="smoke")
        record_dict = record.to_dict()

        self.assertEqual(set(record_dict), set(EXPERIMENT_LOG_FIELD_NAMES))
        self.assertEqual(record.label, "trefoil_vs_figure_eight")
        self.assertEqual(record.input_source, "manual")
        self.assertEqual(record.classification, comparison.classification)

    def test_experiment_log_exports_csv_json_and_markdown(self) -> None:
        comparison = evaluate_workbench_pair(
            get_braid_example("trefoil").to_braid_word(),
            get_braid_example("figure_eight").to_braid_word(),
            q=FAST_Q,
        )
        experiment_log = ExperimentLog()
        experiment_log.add_comparison_result(comparison, label="pair_1")

        csv_text = experiment_log.to_csv_text()
        json_text = experiment_log.to_json_text()
        markdown_text = experiment_log.to_markdown_table()

        self.assertIn("record_id,timestamp,label,input_source", csv_text)
        self.assertIn('"record_count": 1', json_text)
        self.assertIn("| record_id | timestamp | label | input_source | classification |", markdown_text)

    def test_experiment_log_filtering_can_narrow_records(self) -> None:
        experiment_log = ExperimentLog()
        experiment_log.add_comparison_result(
            evaluate_workbench_pair(
                get_braid_example("trefoil").to_braid_word(),
                get_braid_example("figure_eight").to_braid_word(),
                q=FAST_Q,
            ),
            label="trefoil_vs_figure_eight",
        )
        experiment_log.add_comparison_result(
            evaluate_workbench_pair(
                get_braid_example("trefoil").to_braid_word(),
                get_braid_example("trefoil").to_braid_word(),
                q=FAST_Q,
            ),
            label="trefoil_self",
        )

        filtered = experiment_log.filter_records(label_query="self", classification="all_same")
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].label, "trefoil_self")
        self.assertIn('"record_count": 1', experiment_log.to_json_text(filtered))
