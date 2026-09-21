"""Fast fixture-backed regressions for representative recovered program outputs."""

from __future__ import annotations

import json
from pathlib import Path

import sympy as sp

from src.catalog.braid_examples import get_braid_example
from src.invariants.branch_registry import (
    evaluate_sl2_fundamental_branch,
    evaluate_sl2_spin1_branch,
    evaluate_sl3_fundamental_branch,
)


MANIFEST_PATH = Path(__file__).parent / "fixtures" / "representative_invariant_regressions.json"
EVALUATORS = {
    "sl2_fundamental": evaluate_sl2_fundamental_branch,
    "sl2_spin1": evaluate_sl2_spin1_branch,
    "sl3_fundamental": evaluate_sl3_fundamental_branch,
}


def _manifest() -> dict[str, object]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _numeric_cases() -> list[dict[str, object]]:
    return [case for case in _manifest()["cases"] if case["q_mode"] == "2"]


def test_numeric_cases_match_recovered_program_contract() -> None:
    """Recompute compact q=2 examples across all current branches."""

    for case in _numeric_cases():
        example = get_braid_example(str(case["example_label"]))
        assert example.num_strands == case["num_strands"]
        assert list(example.generators) == case["generators"]
        result = EVALUATORS[str(case["branch"])](example, q=sp.Integer(2))
        expected = sp.sympify(str(case["expected_expression"]))
        assert result.status == case["branch_status"]
        assert sp.simplify(result.primary_output - expected) == 0
        assert case["provenance"] == "authoritative recovered implementation regression"


def test_supported_trefoil_presentations_have_the_same_formal_outputs() -> None:
    """Keep the recovered formal presentation-equivalence behavior explicit."""

    for case in _manifest()["equivalence_cases"]:
        evaluator = EVALUATORS[str(case["branch"])]
        left = evaluator(get_braid_example(str(case["left_example_label"])), q=sp.Integer(2))
        right = evaluator(get_braid_example(str(case["right_example_label"])), q=sp.Integer(2))
        assert left.status == right.status == case["branch_status"]
        assert sp.simplify(left.primary_output - right.primary_output) == 0
