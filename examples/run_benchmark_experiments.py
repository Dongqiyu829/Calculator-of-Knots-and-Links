"""Run the benchmark experiment layer on a CSV or JSON benchmark registry."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.experiments.benchmark_registry import load_benchmark_registry
from src.experiments.profile_runner import run_benchmark_experiment
from src.experiments.profile_summary import build_benchmark_summary
from src.workbench.specs import parse_workbench_q_parameter_value


def main() -> int:
    parser = argparse.ArgumentParser(description="Run reproducible benchmark/profile experiments on the ordinary/mainline branches.")
    parser.add_argument("--input", required=True, help="Path to a benchmark CSV or JSON file.")
    parser.add_argument("--q", required=True, help="q mode, e.g. 2, 3, 5, or q.")
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "artifacts" / "benchmark_experiments"),
        help="Directory where pair-level and summary exports will be written.",
    )
    args = parser.parse_args()

    q_expr, q_text = parse_workbench_q_parameter_value(args.q)
    benchmark_pairs = load_benchmark_registry(args.input)
    run = run_benchmark_experiment(
        benchmark_pairs,
        q_parameter_expr=q_expr,
        q_parameter_text=q_text,
        input_path=args.input,
    )
    summary = build_benchmark_summary(run.pair_results, q_mode=q_text)

    input_path = Path(args.input)
    output_dir = Path(args.output_dir) / f"{input_path.stem}_q_{_safe_q_label(q_text)}"
    output_dir.mkdir(parents=True, exist_ok=True)

    pair_csv_path = output_dir / "pair_level_results.csv"
    pair_json_path = output_dir / "pair_level_results.json"
    summary_csv_path = output_dir / "summary.csv"
    summary_json_path = output_dir / "summary.json"
    summary_md_path = output_dir / "summary.md"

    pair_csv_path.write_text(run.to_pair_level_csv_text(), encoding="utf-8")
    pair_json_path.write_text(run.to_pair_level_json_text(), encoding="utf-8")
    summary_csv_path.write_text(summary.to_csv_text(), encoding="utf-8")
    summary_json_path.write_text(summary.to_json_text(), encoding="utf-8")
    summary_md_path.write_text(summary.to_markdown_text(), encoding="utf-8")

    print("Pair-level result table:")
    print(run.to_pair_level_markdown())
    print()
    print("Summary table:")
    print(summary.to_markdown_text())
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


def _safe_q_label(q_text: str) -> str:
    return q_text.replace("^", "pow").replace("-", "neg").replace("/", "div")


if __name__ == "__main__":
    raise SystemExit(main())
