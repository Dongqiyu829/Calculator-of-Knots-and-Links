"""Integrity and regression checks for the recovered report snapshot.

The mathematical evaluators referenced by ``benchmark_lab`` were not included
in ``report_bundle.zip``. These tests therefore preserve what can be verified:
the byte-for-byte recovered inputs/source and the stored known-good outputs.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_PATH = PROJECT_ROOT / "archive" / "report_bundle.zip"
BASELINE_PATH = PROJECT_ROOT / "tests" / "fixtures" / "recovered_benchmark_baselines.json"
ARCHIVE_PREFIX = "report_bundle/"

RECOVERED_FILES = (
    "src/benchmark_lab/__init__.py",
    "src/benchmark_lab/audit.py",
    "src/benchmark_lab/branch_adapter.py",
    "src/benchmark_lab/io_utils.py",
    "src/benchmark_lab/profile_runner.py",
    "src/benchmark_lab/profile_summary.py",
    "src/benchmark_lab/registry.py",
    "examples/benchmark_lab/run_benchmark_audit.py",
    "examples/benchmark_lab/run_benchmark_profiles.py",
    "data/benchmark_lab/benchmark_pairs_template.csv",
    "data/benchmark_lab/benchmark_pairs_template.json",
)


def _baseline() -> dict[str, object]:
    return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))


def _archive_json(archive: ZipFile, relative_path: str) -> dict[str, object]:
    return json.loads(archive.read(ARCHIVE_PREFIX + relative_path).decode("utf-8"))


def test_archived_snapshot_has_recorded_hash() -> None:
    expected = _baseline()["archive_sha256"]
    assert hashlib.sha256(ARCHIVE_PATH.read_bytes()).hexdigest() == expected


@pytest.mark.parametrize("relative_path", RECOVERED_FILES)
def test_recovered_file_matches_archived_snapshot(relative_path: str) -> None:
    with ZipFile(ARCHIVE_PATH) as archive:
        archived = archive.read(ARCHIVE_PREFIX + relative_path)
    assert (PROJECT_ROOT / relative_path).read_bytes() == archived


@pytest.mark.parametrize("relative_path", [path for path in RECOVERED_FILES if path.endswith(".py")])
def test_recovered_python_source_compiles(relative_path: str) -> None:
    source = (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")
    compile(source, relative_path, "exec")


def test_csv_and_json_registries_describe_the_same_pairs() -> None:
    csv_path = PROJECT_ROOT / "data" / "benchmark_lab" / "benchmark_pairs_template.csv"
    json_path = PROJECT_ROOT / "data" / "benchmark_lab" / "benchmark_pairs_template.json"

    with csv_path.open(encoding="utf-8-sig", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    json_rows = json.loads(json_path.read_text(encoding="utf-8"))["benchmarks"]

    assert [row["pair_id"] for row in csv_rows] == [row["pair_id"] for row in json_rows]
    assert [row["expected_profile"] for row in csv_rows] == [row["expected_profile"] for row in json_rows]


@pytest.mark.parametrize("q_mode", ("2", "3", "5"))
def test_stored_numeric_profiles_and_p03_outputs_match_baseline(q_mode: str) -> None:
    baseline = _baseline()
    relative_path = f"artifacts/benchmark_lab/benchmark_pairs_template_q_{q_mode}/pair_level_results.json"
    with ZipFile(ARCHIVE_PATH) as archive:
        result = _archive_json(archive, relative_path)

    pair_results = {pair["pair_id"]: pair for pair in result["pair_results"]}
    assert {pair_id: pair["observed_profile"] for pair_id, pair in pair_results.items()} == baseline["profiles"][q_mode]

    p03_outputs = {
        branch["model_id"]: [branch["output_a"], branch["output_b"]]
        for branch in pair_results["P03"]["branch_records"]
    }
    assert p03_outputs == baseline["p03_numeric_outputs"][q_mode]


def test_stored_symbolic_p03_differences_match_baseline() -> None:
    relative_path = "artifacts/benchmark_lab/benchmark_pairs_template_q_q/audit_P03_q_q.json"
    with ZipFile(ARCHIVE_PATH) as archive:
        result = _archive_json(archive, relative_path)

    differences = {
        branch["model_id"]: branch["symbolic_difference"]
        for branch in result["branch_audits"]
    }
    assert differences == _baseline()["p03_symbolic_differences"]
