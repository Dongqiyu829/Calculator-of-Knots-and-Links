"""Reproducible, non-CI timing and cProfile harness for built-in branches.

Run ``python -m tools.profile_invariants --case all`` from the repository root.
Each case runs in this process; use ``--case NAME`` for cold-start comparisons.
No timing threshold is asserted, and the mathematical evaluator is not replaced.
"""

from __future__ import annotations

import argparse
import cProfile
import io
import json
import platform
import pstats
import sys
from dataclasses import dataclass
from time import perf_counter

import sympy as sp

from src.braid.braid_word import BraidWord
from src.invariants.branch_registry import (
    evaluate_sl2_fundamental_branch,
    evaluate_sl2_spin1_branch,
    evaluate_sl3_fundamental_branch,
)


@dataclass(frozen=True)
class Case:
    name: str
    branch: str
    strands: int
    generators: tuple[int, ...]
    symbolic: bool


CASES = tuple(
    Case(f"{branch}_{braid}_{mode}", branch, strands, word, mode == "symbolic")
    for branch, braid, strands, word in (
        ("sl2_fundamental", "trefoil", 2, (1, 1, 1)),
        ("sl2_fundamental", "figure_eight", 3, (1, -2, 1, -2)),
        ("sl3_fundamental", "trefoil", 2, (1, 1, 1)),
        ("sl2_spin1", "trefoil", 2, (1, 1, 1)),
        ("sl2_fundamental", "five_strand", 5, (1, 2, 3, 4)),
    )
    for mode in ("symbolic", "q2")
) + (
    Case("sl3_fundamental_figure_eight_q2", "sl3_fundamental", 3, (1, -2, 1, -2), False),
    Case("sl2_spin1_figure_eight_q2", "sl2_spin1", 3, (1, -2, 1, -2), False),
)
EVALUATORS = {
    "sl2_fundamental": evaluate_sl2_fundamental_branch,
    "sl3_fundamental": evaluate_sl3_fundamental_branch,
    "sl2_spin1": evaluate_sl2_spin1_branch,
}


def run_case(case: Case, *, profile: bool = False, repeat: int = 1, backend: str = "explicit") -> dict[str, object]:
    q = sp.Symbol("q", nonzero=True) if case.symbolic else sp.Integer(2)
    braid = BraidWord.from_iterable(case.strands, case.generators, label=case.name)
    profiler = cProfile.Profile() if profile else None
    elapsed_samples: list[float] = []
    outputs: list[str] = []
    result = None
    for _ in range(repeat):
        start = perf_counter()
        if profiler is not None:
            profiler.enable()
        result = EVALUATORS[case.branch](braid, q=q, backend=backend)
        if profiler is not None:
            profiler.disable()
        elapsed_samples.append(perf_counter() - start)
        outputs.append(str(result.primary_output))
    assert result is not None
    if len(set(outputs)) != 1:
        raise AssertionError(f"Repeated evaluations of {case.name} differed")
    record: dict[str, object] = {
        "case": case.name,
        "backend": backend,
        "branch": case.branch,
        "q": "symbolic" if case.symbolic else "2",
        "matrix_dimension": (2 if case.branch == "sl2_fundamental" else 3) ** case.strands,
        "strands": case.strands,
        "generators": list(case.generators),
        "generator_count": len(case.generators),
        "wall_seconds": round(elapsed_samples[0], 6),
        "repeat_wall_seconds": [round(value, 6) for value in elapsed_samples],
        "status": result.status,
        "primary_output": str(result.primary_output),
    }
    if profiler is not None:
        report = io.StringIO()
        pstats.Stats(profiler, stream=report).sort_stats("cumulative").print_stats(35)
        record["cprofile_top_cumulative"] = report.getvalue()
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", default="all", choices=("all", *(case.name for case in CASES)))
    parser.add_argument("--profile", action="store_true", help="include top cumulative cProfile functions")
    parser.add_argument("--repeat", type=int, default=1, help="repeat within one process to show warm-cache behavior")
    parser.add_argument("--backend", choices=("explicit", "matrix_free"), default="explicit")
    args = parser.parse_args()
    if args.repeat < 1:
        parser.error("--repeat must be at least 1")
    selected = CASES if args.case == "all" else tuple(case for case in CASES if case.name == args.case)
    payload = {
        "python": platform.python_version(),
        "sympy": sp.__version__,
        "platform": platform.platform(),
        "cases": [run_case(case, profile=args.profile, repeat=args.repeat, backend=args.backend) for case in selected],
    }
    json.dump(payload, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
