"""Untimed-by-CI service benchmark for the desktop's trefoil calculation shape.

Run each backend in a fresh process with ``--backend NAME``. The maintained
desktop worker passes these same branch ids, q, and backend to ``src.services``.
"""

from __future__ import annotations

import argparse
import json
import platform
from time import perf_counter

import sympy as sp

from src.services import evaluate_catalog_result, list_evaluation_branches


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", required=True, choices=("explicit", "matrix_free", "temperley_lieb"))
    parser.add_argument("--repeat", type=int, default=2)
    args = parser.parse_args()
    if args.repeat < 1:
        parser.error("--repeat must be at least 1")
    branch_ids = (
        ("sl2_fundamental",)
        if args.backend == "temperley_lieb"
        else tuple(descriptor.branch_id for descriptor in list_evaluation_branches())
    )
    elapsed: list[float] = []
    outputs: list[tuple[tuple[str, str], ...]] = []
    raw_trace_present: list[tuple[tuple[str, bool], ...]] = []
    for _ in range(args.repeat):
        started = perf_counter()
        result = evaluate_catalog_result("trefoil", branch_ids=branch_ids, q=sp.Integer(2), backend=args.backend)
        elapsed.append(round(perf_counter() - started, 6))
        outputs.append(tuple((item.branch_id, item.primary_output) for item in result.branch_results))
        raw_trace_present.append(tuple((item.branch_id, item.raw_trace is not None) for item in result.branch_results))
    if len(set(outputs)) != 1 or len(set(raw_trace_present)) != 1:
        raise AssertionError("Repeated desktop-shaped evaluations differed")
    print(json.dumps({
        "python": platform.python_version(),
        "sympy": sp.__version__,
        "platform": platform.platform(),
        "backend": args.backend,
        "example": "trefoil",
        "branch_ids": branch_ids,
        "q": "2",
        "seconds": elapsed,
        "primary_outputs": dict(outputs[0]),
        "raw_trace_present": dict(raw_trace_present[0]),
    }, indent=2))


if __name__ == "__main__":
    main()
