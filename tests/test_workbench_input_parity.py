"""Parity tests for manual and JSON workbench input modes."""

from __future__ import annotations

import json
import unittest

from src.workbench.experiment_log import ExperimentLog
from src.workbench.runner import evaluate_workbench_run
from src.workbench.specs import (
    WorkbenchBraidSpec,
    build_manual_input_spec,
    normalize_input_spec,
    parse_json_input_spec,
)


class TestWorkbenchInputParity(unittest.TestCase):
    def _manual_run_result(self):
        manual_spec = build_manual_input_spec(
            q_parameter="2",
            models=("sl2_fundamental", "sl2_3d_9x9", "sl3_fundamental"),
            comparison_mode="all",
            braids=(
                WorkbenchBraidSpec(label="A", num_strands=3, generators=(1, 2, 1), notes="manual"),
                WorkbenchBraidSpec(label="B", num_strands=3, generators=(2, 1, 2), notes="manual"),
                WorkbenchBraidSpec(label="C", num_strands=3, generators=(1, -2, 1, -2), notes="manual"),
            ),
        )
        return evaluate_workbench_run(normalize_input_spec(manual_spec))

    def _json_run_result(self):
        payload = {
            "q_parameter": "2",
            "models": ["sl2_fundamental", "sl2_3d_9x9", "sl3_fundamental"],
            "comparison_mode": "all",
            "braids": [
                {"label": "A", "num_strands": 3, "generators": [1, 2, 1], "notes": "json"},
                {"label": "B", "num_strands": 3, "generators": [2, 1, 2], "notes": "json"},
                {"label": "C", "num_strands": 3, "generators": [1, -2, 1, -2], "notes": "json"},
            ],
        }
        return evaluate_workbench_run(normalize_input_spec(parse_json_input_spec(json.dumps(payload))))

    def test_manual_and_json_modes_produce_identical_tables(self) -> None:
        manual_result = self._manual_run_result()
        json_result = self._json_run_result()

        manual_single = [{key: value for key, value in row.items() if key != "notes"} for row in manual_result.table_rows("single")]
        json_single = [{key: value for key, value in row.items() if key != "notes"} for row in json_result.table_rows("single")]

        self.assertEqual(manual_single, json_single)
        self.assertEqual(manual_result.table_rows("pairwise"), json_result.table_rows("pairwise"))
        self.assertEqual(manual_result.table_rows("summary"), json_result.table_rows("summary"))

    def test_experiment_log_records_keep_structure_and_source_for_both_modes(self) -> None:
        manual_result = self._manual_run_result()
        json_result = self._json_run_result()

        experiment_log = ExperimentLog()
        manual_records = experiment_log.add_batch_run_result(manual_result)
        json_records = experiment_log.add_batch_run_result(json_result)

        self.assertTrue(manual_records)
        self.assertTrue(json_records)
        self.assertTrue(all(record.input_source == "manual" for record in manual_records))
        self.assertTrue(all(record.input_source == "json" for record in json_records))
        self.assertEqual(
            [{key: value for key, value in record.to_dict().items() if key not in {"record_id", "timestamp", "input_source"}} for record in manual_records],
            [{key: value for key, value in record.to_dict().items() if key not in {"record_id", "timestamp", "input_source"}} for record in json_records],
        )
