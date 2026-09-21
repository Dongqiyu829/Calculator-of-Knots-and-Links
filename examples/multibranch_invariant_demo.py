"""Show the current program as a multi-branch invariant system rather than a single-branch calculator."""

from __future__ import annotations

import sys
from pathlib import Path

import sympy as sp

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.catalog.braid_examples import get_braid_example
from src.invariants.branch_formatter import format_catalog_benchmark
from src.invariants.multibranch_benchmark import evaluate_catalog_across_branches


def main() -> None:
    q = sp.Symbol("q", nonzero=True)
    examples = tuple(get_braid_example(label) for label in ("unknot_1", "trefoil", "figure_eight"))
    entries = evaluate_catalog_across_branches(examples, q=q)

    print("=== Multi-branch invariant demo ===")
    print("This is the current top-level program view: one braid example evaluated across multiple invariant branches through the shared formatter layer.")
    print(format_catalog_benchmark(entries))


if __name__ == "__main__":
    main()