"""Smoke tests for the benchmark experiment registry layer."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.experiments.benchmark_registry import (
    BENCHMARK_CSV_HEADERS,
    BenchmarkRegistryError,
    load_benchmark_registry,
    safe_parse_generator_string,
)


class TestBenchmarkRegistrySmoke(unittest.TestCase):
    def test_safe_parse_generator_string_accepts_json_arrays_and_plain_text(self) -> None:
        self.assertEqual(safe_parse_generator_string("[1, 1, -2]"), (1, 1, -2))
        self.assertEqual(safe_parse_generator_string("1 1 -2"), (1, 1, -2))
        self.assertEqual(safe_parse_generator_string(""), ())

    def test_safe_parse_generator_string_rejects_non_integer_tokens(self) -> None:
        with self.assertRaises(BenchmarkRegistryError):
            safe_parse_generator_string("1 foo -2")

    def test_csv_placeholder_pair_loads_and_is_marked_skipped(self) -> None:
        csv_text = ",".join(BENCHMARK_CSV_HEADERS) + "\n" + ",".join(
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
            path = Path(temp_dir) / "benchmark.csv"
            path.write_text(csv_text, encoding="utf-8")
            rows = load_benchmark_registry(path)

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
                    "notes": "control pair",
                }
            ]
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "benchmark.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            rows = load_benchmark_registry(path)

        self.assertEqual(len(rows), 1)
        self.assertFalse(rows[0].should_skip)
        self.assertEqual(rows[0].braid_a.generators, (1, 1, 1, 1, 1))
