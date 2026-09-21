"""CLI entrypoint for the independent benchmark-lab audit flow."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.benchmark_lab.audit import audit_pair
from src.benchmark_lab.branch_adapter import parse_q_parameter
from src.benchmark_lab.io_utils import data_to_json_text, ensure_audit_output_dir, write_text
from src.benchmark_lab.registry import find_pair_by_id, load_registry


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit one benchmark-lab pair without touching the mainline runner.")
    parser.add_argument("--input", required=True, help="Path to benchmark_lab CSV or JSON input.")
    parser.add_argument("--pair", required=True, help="Stable pair id, e.g. P01 or P04.")
    parser.add_argument("--q", required=True, help="q mode, e.g. 2, 3, 5, or q.")
    args = parser.parse_args()

    q_parameter, q_mode = parse_q_parameter(args.q)
    registry = load_registry(args.input)
    pair = find_pair_by_id(registry, args.pair)
    audit_record = audit_pair(pair, q_parameter=q_parameter, q_mode=q_mode)

    output_dir = ensure_audit_output_dir(args.input, q_mode)
    audit_md_path = write_text(output_dir / f"audit_{pair.pair_id}_q_{q_mode}.md", audit_record.to_markdown())
    audit_json_path = write_text(output_dir / f"audit_{pair.pair_id}_q_{q_mode}.json", data_to_json_text(audit_record.to_dict()))

    print(audit_record.to_markdown())
    print()
    print("Exported files:")
    print(f"- {audit_md_path}")
    print(f"- {audit_json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
