"""Registry-style evaluators for the current invariant program branches."""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any

import sympy as sp

from src.braid.braid_operator import BraidOperatorBuilder
from src.braid.braid_word import BraidWord
from src.catalog.braid_examples import BraidExample
from src.rmatrix.sl2_rmatrix import build_sl2_fundamental_rmatrix, build_sl2_spin1_rmatrix
from src.rmatrix.sl3_rmatrix import build_sl3_fundamental_rmatrix
from src.rmatrix.rmatrix_base import RMatrixData

from .branch_results import InvariantBranchResult
from .eyb_invariant import build_sl3_fundamental_eyb_data, compute_eyb_invariant
from .jones_invariant import compute_sl2_jones_compatible_output
from .quantum_trace import compute_raw_closure_trace
from .sl2_3d_colored_jones_candidate import (
    SL2_3D_KNOT_ATLAS_BRANCH_NOTE,
    SL2_3D_USER_FACING_NAME,
    compute_sl2_3d_candidate_output,
)


@lru_cache(maxsize=32)
def _cached_builtin_rmatrix(branch_id: str, q: sp.Expr) -> RMatrixData:
    """Cache local data by exact branch and q; never hand out the mutable master."""

    if branch_id == "sl2_fundamental":
        return build_sl2_fundamental_rmatrix(q, diagnostics=False)
    if branch_id == "sl3_fundamental":
        return build_sl3_fundamental_rmatrix(q, diagnostics=False)
    if branch_id == "sl2_spin1":
        # The candidate branch exposes projector checks in its public metadata.
        return build_sl2_spin1_rmatrix(q)
    raise ValueError(f"Unknown built-in branch: {branch_id}")


def _builtin_rmatrix(branch_id: str, q: sp.Expr) -> RMatrixData:
    return deepcopy(_cached_builtin_rmatrix(branch_id, q))


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


def evaluate_sl2_fundamental_branch(
    target: BraidWord | BraidExample,
    *,
    q: sp.Expr | None = None,
) -> InvariantBranchResult:
    """Evaluate the formal sl2 Jones-compatible branch in the unified branch format."""

    braid_word, source_metadata = _coerce_braid_word(target)
    parameter = q if q is not None else sp.Symbol("q", nonzero=True)
    operator_data = BraidOperatorBuilder(braid_word, _builtin_rmatrix("sl2_fundamental", parameter)).build()
    result = compute_sl2_jones_compatible_output(operator_data, q=parameter)
    return InvariantBranchResult(
        branch_id="sl2_fundamental",
        representation_name=result.representation_name,
        braid_word=result.braid_word,
        status="formal",
        raw_trace=result.raw_trace,
        primary_output=result.jones_compatible_output,
        primary_output_label="Jones-compatible output",
        normalization_label="reduced P2 by current unknot value",
        variable_convention=result.variable_convention,
        notes=result.notes,
        metadata={
            **source_metadata,
            "unreduced_p2_output": str(sp.simplify(result.unreduced_p2_output)),
            "unknot_normalization": str(sp.simplify(result.unknot_normalization)),
            "reduced_p2_output": str(sp.simplify(result.reduced_p2_output)),
            "jones_compatible_output": str(sp.simplify(result.jones_compatible_output)),
            "normalization_kind": "current P2 reduced by current unknot value",
        },
    )


def evaluate_sl3_fundamental_branch(
    target: BraidWord | BraidExample,
    *,
    q: sp.Expr | None = None,
) -> InvariantBranchResult:
    """Evaluate the formal sl3 P3-type EYB branch in the unified branch format."""

    parameter = q if q is not None else sp.Symbol("q", nonzero=True)
    braid_word, source_metadata = _coerce_braid_word(target)
    operator_data = BraidOperatorBuilder(
        braid_word=braid_word,
        rmatrix=_builtin_rmatrix("sl3_fundamental", parameter),
    ).build()
    result = compute_eyb_invariant(operator_data, eyb_data=build_sl3_fundamental_eyb_data(parameter))
    primary_output = sp.simplify(result.eyb_normalized_expression)
    return InvariantBranchResult(
        branch_id="sl3_fundamental",
        representation_name=result.representation.name(),
        braid_word=result.braid_word,
        status="formal",
        raw_trace=sp.simplify(result.raw_closure_trace),
        primary_output=primary_output,
        primary_output_label="P3-type EYB output",
        normalization_label="current braid-side EYB normalization",
        variable_convention="Uses q as the current braid-side EYB branch variable.",
        notes=result.convention_notes,
        metadata={
            **source_metadata,
            "trace_mode": result.trace_mode,
            "eyb_output": str(primary_output),
            "framing_notes": result.framing_notes,
        },
    )


def evaluate_sl2_spin1_branch(
    target: BraidWord | BraidExample,
    *,
    q: sp.Expr | None = None,
) -> InvariantBranchResult:
    """Evaluate the sl2 3-dimensional 9x9 candidate branch."""

    parameter = q if q is not None else sp.Symbol("q", nonzero=True)
    braid_word, source_metadata = _coerce_braid_word(target)
    rmatrix = _builtin_rmatrix("sl2_spin1", parameter)
    operator_data = BraidOperatorBuilder(braid_word, rmatrix).build()
    result = compute_sl2_3d_candidate_output(operator_data, q=parameter)
    return InvariantBranchResult(
        branch_id="sl2_spin1",
        representation_name=result.representation_name,
        braid_word=result.braid_word,
        status=result.status,
        raw_trace=sp.simplify(result.raw_trace),
        primary_output=sp.simplify(result.reduced_candidate_output),
        primary_output_label="Colored Jones candidate output",
        normalization_label="RT / quantum-trace candidate normalization",
        variable_convention=result.variable_convention,
        notes=result.notes,
        metadata={
            **source_metadata,
            **result.metadata,
            "user_facing_branch_name": SL2_3D_USER_FACING_NAME,
            "quantum_trace_before_normalization": str(sp.simplify(result.quantum_trace_before_normalization)),
            "unreduced_candidate_output": str(sp.simplify(result.unreduced_candidate_output)),
            "unknot_normalization": str(sp.simplify(result.unknot_normalization)),
            "reduced_candidate_output": str(sp.simplify(result.reduced_candidate_output)),
            "candidate_output_label": result.candidate_output_label,
            "projector_checks": rmatrix.validation_data.get("projector_checks"),
            "branch_note": SL2_3D_KNOT_ATLAS_BRANCH_NOTE,
        },
    )


def evaluate_all_current_branches(
    target: BraidWord | BraidExample,
    *,
    q: sp.Expr | None = None,
) -> list[InvariantBranchResult]:
    """Evaluate all current program branches for one braid input."""

    return evaluate_current_branches(target, q=q)


def evaluate_current_branches(
    target: BraidWord | BraidExample,
    *,
    branch_ids: tuple[str, ...] | list[str] | None = None,
    q: sp.Expr | None = None,
) -> list[InvariantBranchResult]:
    """Evaluate the selected current program branches for one braid input."""

    if branch_ids is None:
        selected_branch_ids = {branch_id for branch_id, _evaluator in CURRENT_BRANCH_EVALUATORS}
    else:
        selected_branch_ids = set(branch_ids)

    return [
        evaluator(target, q=q)
        for branch_id, evaluator in CURRENT_BRANCH_EVALUATORS
        if branch_id in selected_branch_ids
    ]


CURRENT_BRANCH_EVALUATORS = (
    ("sl2_fundamental", evaluate_sl2_fundamental_branch),
    ("sl3_fundamental", evaluate_sl3_fundamental_branch),
    ("sl2_spin1", evaluate_sl2_spin1_branch),
)
