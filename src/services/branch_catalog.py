"""Frontend-neutral descriptors for the current application evaluation branches."""

from __future__ import annotations

from dataclasses import dataclass

from src.invariants.sl2_3d_colored_jones_candidate import (
    SL2_3D_BRANCH_STATUS,
    SL2_3D_KNOT_ATLAS_BRANCH_NOTE,
    SL2_3D_USER_FACING_NAME,
)

from .errors import UnknownEvaluationBranchError, UnknownEvaluationModelError


@dataclass(frozen=True, slots=True)
class EvaluationBranchDescriptor:
    """One supported frontend-facing model and its internal evaluator branch."""

    model_id: str
    branch_id: str
    display_name: str
    status: str
    user_note: str

    @property
    def branch_note(self) -> str:
        """Compatibility alias used by the existing workbench presentation."""

        return self.user_note


EVALUATION_BRANCH_CATALOG: tuple[EvaluationBranchDescriptor, ...] = (
    EvaluationBranchDescriptor(
        model_id="sl2_fundamental",
        branch_id="sl2_fundamental",
        display_name="Jones / sl2 fundamental",
        status="formal",
        user_note="Formal Jones-compatible branch.",
    ),
    EvaluationBranchDescriptor(
        model_id="sl2_3d_9x9",
        branch_id="sl2_spin1",
        display_name=SL2_3D_USER_FACING_NAME,
        status=SL2_3D_BRANCH_STATUS,
        user_note=SL2_3D_KNOT_ATLAS_BRANCH_NOTE,
    ),
    EvaluationBranchDescriptor(
        model_id="sl3_fundamental",
        branch_id="sl3_fundamental",
        display_name="sl3 fundamental",
        status="formal",
        user_note="Formal sl3 branch for cross-Lie-algebra comparison.",
    ),
)
DEFAULT_EVALUATION_MODEL_IDS = tuple(descriptor.model_id for descriptor in EVALUATION_BRANCH_CATALOG)


def list_evaluation_branches() -> tuple[EvaluationBranchDescriptor, ...]:
    """Return the ordered, supported frontend-facing evaluation catalog."""

    return EVALUATION_BRANCH_CATALOG


def get_evaluation_model(model_id: str) -> EvaluationBranchDescriptor:
    """Return one descriptor by frontend-facing model id."""

    for descriptor in EVALUATION_BRANCH_CATALOG:
        if descriptor.model_id == model_id:
            return descriptor
    raise UnknownEvaluationModelError(
        f"Unknown evaluation model '{model_id}'. Allowed values: {', '.join(DEFAULT_EVALUATION_MODEL_IDS)}"
    )


def get_evaluation_branch(branch_id: str) -> EvaluationBranchDescriptor:
    """Return one descriptor by the internal branch id exposed to application callers."""

    for descriptor in EVALUATION_BRANCH_CATALOG:
        if descriptor.branch_id == branch_id:
            return descriptor
    allowed_branch_ids = tuple(descriptor.branch_id for descriptor in EVALUATION_BRANCH_CATALOG)
    raise UnknownEvaluationBranchError(
        f"Unknown evaluation branch '{branch_id}'. Allowed values: {', '.join(allowed_branch_ids)}"
    )


def branch_ids_for_models(model_ids: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    """Translate ordered frontend model ids to their internal evaluator ids."""

    return tuple(get_evaluation_model(model_id).branch_id for model_id in model_ids)


def validate_branch_ids(branch_ids: tuple[str, ...] | list[str] | None) -> tuple[str, ...] | None:
    """Validate selected internal branch ids while preserving caller order."""

    if branch_ids is None:
        return None
    selected = tuple(branch_ids)
    for branch_id in selected:
        get_evaluation_branch(branch_id)
    return selected
