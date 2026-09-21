"""Smoke tests for benchmark_lab.registry."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.benchmark_lab.registry import CSV_HEADERS, RegistryError, load_registry, safe_parse_generators


class TestBenchmarkLabRegistrySmoke(unittest.TestCase):
    def test_safe_parse_generators_accepts_json_and_plain_text(self) -> None:
        self.assertEqual(safe_parse_generators("[1, 1, -2]"), (1, 1, -2))
        self.assertEqual(safe_parse_generators("1 1 -2"), (1, 1, -2))
        self.assertEqual(safe_parse_generators(""), ())

    def test_safe_parse_generators_rejects_non_integer_tokens(self) -> None:
        with self.assertRaises(RegistryError):
            safe_parse_generators("1 foo -2")

    def test_csv_placeholder_pair_loads_and_is_marked_for_skip(self) -> None:
        csv_text = ",".join(CSV_HEADERS) + "\n" + ",".join(
            [
                "P05",
                "mutation_placeholder",
                "K11n34",
                "K11n42",
                "placeholder A",
                "placeholder B",
                "0",
                "[]",
                "0",
                "[]",
                "yes",
                "yes",
                "yes",
                "needs_audit",
                "same",
                "same",
                "same",
                "(0,0,0)",
                "high",
                "placeholder row",
            ]
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "benchmark_lab.csv"
            path.write_text(csv_text, encoding="utf-8")
            rows = load_registry(path)
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0].should_skip)
        self.assertEqual(rows[0].skip_reason, "needs_audit")

    def test_json_registry_loads_safe_pair(self) -> None:
        payload = {
            "benchmarks": [
                {
                    "pair_id": "P01",
                    "group": "control",
                    "label_A": "5_1",
                    "label_B": "5_1_stabilized",
                    "source_A": "manual",
                    "source_B": "manual",
                    "num_strands_A": 2,
                    "generators_A": [1, 1, 1, 1, 1],
                    "num_strands_B": 3,
                    "generators_B": [1, 1, 1, 1, 1, -2],
                    "same_jones": "yes",
                    "same_alexander_or_conway": "yes",
                    "mutant": "no",
                    "status_of_braid_source": "safe",
                    "expected_sl2_fundamental": "same",
                    "expected_sl2_3d_9x9": "same",
                    "expected_sl3_fundamental": "same",
                    "expected_profile": "(0,0,0)",
                    "priority": "high",
                    "notes": "control pair"
                }
            ]
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "benchmark_lab.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            rows = load_registry(path)
        self.assertEqual(len(rows), 1)
        self.assertFalse(rows[0].should_skip)
        self.assertEqual(rows[0].braid_a.generators, (1, 1, 1, 1, 1))
