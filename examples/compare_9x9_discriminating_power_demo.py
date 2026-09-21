"""Compare the current discriminating behavior of the two 9x9 invariant branches."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import sympy as sp

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.invariants.compare_9x9_benchmark import evaluate_default_9x9_discriminating_power


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare the current sl2 3D and sl3 9x9 branch discriminating behavior.")
    parser.add_argument(
        "--symbolic",
        action="store_true",
        help="Use symbolic q instead of the faster default q = 2 demo mode.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args = _build_arg_parser().parse_args(argv)
    q = sp.Symbol("q", nonzero=True) if args.symbolic else sp.Integer(2)
    summary = evaluate_default_9x9_discriminating_power(q=q)
    print(f"Running 9x9 discriminating-power benchmark with q = {q}")
    print(summary.summary())
    print()
    print("Detailed pair reports:")
    for pair_result in summary.pair_results:
        print()
        print(pair_result.summary())


if __name__ == "__main__":
    main()