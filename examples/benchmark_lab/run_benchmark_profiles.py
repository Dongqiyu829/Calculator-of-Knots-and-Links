"""CLI entrypoint for the independent benchmark-lab profile runner."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.benchmark_lab.branch_adapter import parse_q_parameter
from src.benchmark_lab.io_utils import (
    data_to_json_text,
    ensure_profile_output_dir,
    rows_to_csv_text,
    rows_to_markdown_text,
    write_text,
)
from src.benchmark_lab.profile_runner import run_profile_experiment
from src.benchmark_lab.profile_summary import build_profile_summary
from src.benchmark_lab.registry import load_registry


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the independent benchmark-lab profile experiment suite.")
    parser.add_argument("--input", required=True, help="Path to benchmark_lab CSV or JSON input.")
    parser.add_argument("--q", required=True, help="q mode, e.g. 2, 3, 5, or q.")
    args = parser.parse_args()

    q_parameter, q_mode = parse_q_parameter(args.q)
    registry = load_registry(args.input)
    run = run_profile_experiment(registry, q_parameter=q_parameter, q_mode=q_mode, input_path=args.input)
    summary = build_profile_summary(run.pair_results, q_mode=q_mode)

    output_dir = ensure_profile_output_dir(args.input, q_mode)
    pair_csv_path = write_text(output_dir / "pair_level_results.csv", rows_to_csv_text(run.pair_level_rows()))
    pair_json_path = write_text(output_dir / "pair_level_results.json", data_to_json_text(run.to_dict()))
    summary_csv_path = write_text(output_dir / "summary.csv", rows_to_csv_text(summary.to_rows()))
    summary_json_path = write_text(output_dir / "summary.json", data_to_json_text(summary.to_dict()))
    summary_md_path = write_text(output_dir / "summary.md", rows_to_markdown_text(summary.to_rows()))

    print("Pair-level result table:")
    print(rows_to_markdown_text(run.pair_level_rows()))
    print()
    print("Summary table:")
    print(rows_to_markdown_text(summary.to_rows()))
    print()
    if run.warnings:
        print("Warnings:")
        for warning in run.warnings:
            print(f"- {warning}")
        print()
    print("Exported files:")
    print(f"- {pair_csv_path}")
    print(f"- {pair_json_path}")
    print(f"- {summary_csv_path}")
    print(f"- {summary_json_path}")
    print(f"- {summary_md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
