"""Legacy fast branch registry preserved alongside the newer candidate branch pipeline."""

from __future__ import annotations

from typing import Any

import sympy as sp

from src.braid.braid_operator import BraidOperatorBuilder
from src.braid.braid_word import BraidWord
from src.catalog.braid_examples import BraidExample
from src.rmatrix.sl2_rmatrix import build_sl2_spin1_rmatrix

from .branch_registry import evaluate_sl2_fundamental_branch, evaluate_sl3_fundamental_branch
from .branch_results import InvariantBranchResult
from .quantum_trace import compute_raw_closure_trace


LEGACY_SL2_3D_USER_FACING_NAME = "sl2 的3维表示下的9x9矩阵"


def _coerce_braid_word(target: BraidWord | BraidExample) -> tuple[BraidWord, dict[str, Any]]:
    if isinstance(target, BraidExample):
        return target.to_braid_word(), {
            "example_label": target.label,
            "example_notes": target.notes,
            "example_metadata": dict(target.metadata),
        }
    return target, {
        "example_label": target.label,
        "example_notes": target.notes,
        "example_metadata": dict(target.metadata),
    }


def evaluate_sl2_3d_legacy_raw_branch(
    target: BraidWord | BraidExample,
    *,
    q: sp.Expr | None = None,
) -> InvariantBranchResult:
    """Evaluate the legacy fast raw/projector-aware sl2 3-dimensional 9x9 branch."""

    parameter = q if q is not None else sp.Symbol("q", nonzero=True)
    braid_word, source_metadata = _coerce_braid_word(target)
    rmatrix = build_sl2_spin1_rmatrix(parameter)
    operator_data = BraidOperatorBuilder(braid_word=braid_word, rmatrix=rmatrix).build()
    result = compute_raw_closure_trace(operator_data)
    return InvariantBranchResult(
        branch_id="sl2_spin1",
        representation_name=LEGACY_SL2_3D_USER_FACING_NAME,
        braid_word=result.braid_word,
        status="exploratory",
        raw_trace=sp.simplify(result.raw_closure_trace),
        primary_output=sp.simplify(result.raw_closure_trace),
        primary_output_label="Raw trace (legacy fast mode)",
        normalization_label="Legacy projector-aware raw branch",
        variable_convention=(
            "Legacy fast mode keeps the ordinary trace / projector-aware layer only. "
            "No candidate quantum-trace normalization is applied here."
        ),
        notes=(
            "This preserved legacy branch keeps the older fast raw/projector-aware behavior as a backup program. "
            "It is useful when the newer candidate normalization branch is too slow for quick experimentation."
        ),
        metadata={
            **source_metadata,
            "user_facing_branch_name": LEGACY_SL2_3D_USER_FACING_NAME,
            "projector_checks": rmatrix.validation_data.get("projector_checks"),
            "branch_note": (
                "Legacy fast backup mode: projector-aware local data retained, but no candidate RT / quantum-trace "
                "normalization layer is applied."
            ),
            "legacy_mode": True,
        },
    )


def evaluate_all_legacy_branches(
    target: BraidWord | BraidExample,
    *,
    q: sp.Expr | None = None,
) -> list[InvariantBranchResult]:
    """Evaluate the preserved legacy branch set."""

    return evaluate_legacy_branches(target, q=q)


def evaluate_legacy_branches(
    target: BraidWord | BraidExample,
    *,
    branch_ids: tuple[str, ...] | list[str] | None = None,
    q: sp.Expr | None = None,
) -> list[InvariantBranchResult]:
    """Evaluate the selected preserved legacy branch set."""

    if branch_ids is None:
        selected_branch_ids = {branch_id for branch_id, _evaluator in LEGACY_BRANCH_EVALUATORS}
    else:
        selected_branch_ids = set(branch_ids)

    return [
        evaluator(target, q=q)
        for branch_id, evaluator in LEGACY_BRANCH_EVALUATORS
        if branch_id in selected_branch_ids
    ]


LEGACY_BRANCH_EVALUATORS = (
    ("sl2_fundamental", evaluate_sl2_fundamental_branch),
    ("sl3_fundamental", evaluate_sl3_fundamental_branch),
    ("sl2_spin1", evaluate_sl2_3d_legacy_raw_branch),
)