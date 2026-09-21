"""Extended symbolic fixture-backed regressions for the formal sl2 branch."""

from __future__ import annotations

import json
from pathlib import Path

import sympy as sp

from src.catalog.braid_examples import get_braid_example
from src.invariants.branch_registry import evaluate_sl2_fundamental_branch


MANIFEST_PATH = Path(__file__).parent / "fixtures" / "representative_invariant_regressions.json"
Q = sp.Symbol("q", nonzero=True)


def test_symbolic_sl2_cases_match_recovered_program_contract() -> None:
    """Keep the established symbolic Jones-compatible expressions auditable."""

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    cases = [case for case in manifest["cases"] if case["q_mode"] == "symbolic_q"]
    assert {case["example_label"] for case in cases} == {"unknot_1", "trefoil", "figure_eight"}
    for case in cases:
        example = get_braid_example(case["example_label"])
        result = evaluate_sl2_fundamental_branch(example, q=Q)
        expected = sp.sympify(case["expected_expression"], locals={"q": Q})
        assert result.status == case["branch_status"] == "formal"
        assert sp.simplify(result.primary_output - expected) == 0
