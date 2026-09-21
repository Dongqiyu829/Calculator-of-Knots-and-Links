"""Thin adapter layer that only imports and calls existing branch evaluators."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import sympy as sp

from src.braid.braid_word import BraidWord
from src.invariants.branch_registry import (
    evaluate_sl2_fundamental_branch,
    evaluate_sl2_spin1_branch,
    evaluate_sl3_fundamental_branch,
)
from src.invariants.branch_results import InvariantBranchResult


BENCHMARK_MODEL_ORDER = ("sl2_fundamental", "sl2_3d_9x9", "sl3_fundamental")


@dataclass(frozen=True, slots=True)
class BenchmarkModelSpec:
    """Describe one model exposed by the benchmark lab."""

    model_id: str
    branch_id: str
    display_name: str
    evaluator: Callable[[BraidWord], InvariantBranchResult]


BENCHMARK_MODEL_SPECS = {
    "sl2_fundamental": BenchmarkModelSpec(
        model_id="sl2_fundamental",
        branch_id="sl2_fundamental",
        display_name="Jones / sl2 fundamental",
        evaluator=evaluate_sl2_fundamental_branch,
    ),
    "sl2_3d_9x9": BenchmarkModelSpec(
        model_id="sl2_3d_9x9",
        branch_id="sl2_spin1",
        display_name="sl2 的3维表示下的9x9矩阵",
        evaluator=evaluate_sl2_spin1_branch,
    ),
    "sl3_fundamental": BenchmarkModelSpec(
        model_id="sl3_fundamental",
        branch_id="sl3_fundamental",
        display_name="sl3 fundamental",
        evaluator=evaluate_sl3_fundamental_branch,
    ),
}


def parse_q_parameter(q_value: str) -> tuple[sp.Expr, str]:
    """Parse q mode locally inside the benchmark lab without relying on old workbench code."""

    cleaned = q_value.strip()
    if not cleaned:
        raise ValueError("q parameter cannot be empty.")
    try:
        return sp.sympify(cleaned), cleaned
    except Exception as exc:
        raise ValueError(f"Invalid q parameter: {q_value}") from exc


def evaluate_models_for_braid(braid_word: BraidWord, *, q_parameter: sp.Expr) -> dict[str, InvariantBranchResult]:
    """Evaluate the three benchmark-lab models on one braid word."""

    results: dict[str, InvariantBranchResult] = {}
    for model_id in BENCHMARK_MODEL_ORDER:
        spec = BENCHMARK_MODEL_SPECS[model_id]
        results[model_id] = spec.evaluator(braid_word, q=q_parameter)
    return results
