"""Smoke tests for the ordinary workbench JSON input schema."""

from __future__ import annotations

import unittest

from src.workbench.specs import (
  AI_JSON_TEMPLATE,
  WorkbenchInputValidationError,
  get_workbench_model_descriptions,
  normalize_input_spec,
  parse_json_input_spec,
)


class TestWorkbenchInputSchemaSmoke(unittest.TestCase):
    def test_valid_json_schema_passes(self) -> None:
        input_spec = parse_json_input_spec(AI_JSON_TEMPLATE)
        run_spec = normalize_input_spec(input_spec)
        self.assertEqual(run_spec.input_source, "json")
        self.assertEqual(run_spec.comparison_mode, "pairwise")
        self.assertEqual(run_spec.models, ("sl2_fundamental", "sl2_3d_9x9", "sl3_fundamental"))
        self.assertEqual([braid.label for braid in run_spec.batch.braids], ["A", "B"])

    def test_model_descriptions_expose_shared_knot_atlas_wording_for_sl2_3d(self) -> None:
      descriptions = get_workbench_model_descriptions()
      sl2_3d_description = next(description for description in descriptions if description.startswith("sl2_3d_9x9"))
      self.assertIn("Knot Atlas n=2", sl2_3d_description)
      self.assertIn("q^6 J_2(3_1; q^2)", sl2_3d_description)
      self.assertIn("5_2 remains under verification", sl2_3d_description)

    def test_out_of_range_generator_raises_clear_error(self) -> None:
        bad_json = """
        {
          "q_parameter": "2",
          "models": ["sl2_fundamental"],
          "comparison_mode": "single",
          "braids": [
            {"label": "A", "num_strands": 3, "generators": [3]}
          ]
        }
        """
        with self.assertRaisesRegex(WorkbenchInputValidationError, "out of range"):
            parse_json_input_spec(bad_json)

    def test_invalid_comparison_mode_raises_clear_error(self) -> None:
        bad_json = """
        {
          "q_parameter": "2",
          "models": ["sl2_fundamental"],
          "comparison_mode": "bad_mode",
          "braids": [
            {"label": "A", "num_strands": 3, "generators": [1]}
          ]
        }
        """
        with self.assertRaisesRegex(WorkbenchInputValidationError, "comparison_mode"):
            normalize_input_spec(parse_json_input_spec(bad_json))

    def test_invalid_model_raises_clear_error(self) -> None:
        bad_json = """
        {
          "q_parameter": "2",
          "models": ["sl2_fundamental", "bad_model"],
          "comparison_mode": "single",
          "braids": [
            {"label": "A", "num_strands": 3, "generators": [1]}
          ]
        }
        """
        with self.assertRaisesRegex(WorkbenchInputValidationError, "Invalid model id"):
            normalize_input_spec(parse_json_input_spec(bad_json))
