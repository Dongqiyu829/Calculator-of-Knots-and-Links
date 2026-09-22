"""Frontend-neutral mathematical explanation descriptors.

The maintained desktop frontend renders these descriptors; it does not carry
its own copy of branch claims, normalization facts, or operator boundaries.
This module is deliberately descriptive only.  It never evaluates an
invariant, constructs a matrix, or changes a mathematical convention.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

from src.braid.braid_word import BraidWord

from .branch_catalog import get_evaluation_branch


@dataclass(frozen=True, slots=True)
class MathematicalExplanation:
    """A small, deterministic explanation payload for a maintained workflow."""

    explanation_id: str
    workflow: str
    title: str
    status: str
    summary: str
    formula_lines: tuple[str, ...] = ()
    normalization: str = ""
    variable_convention: str = ""
    output_name: str = ""
    representation_dimension: int | None = None
    warnings: tuple[str, ...] = ()
    documentation_refs: tuple[str, ...] = ()
    branch_statuses: tuple[tuple[str, str], ...] = ()
    details: tuple[str, ...] = ()
    operator_only: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "explanation_id": self.explanation_id,
            "workflow": self.workflow,
            "title": self.title,
            "status": self.status,
            "summary": self.summary,
            "formula_lines": list(self.formula_lines),
            "normalization": self.normalization,
            "variable_convention": self.variable_convention,
            "output_name": self.output_name,
            "representation_dimension": self.representation_dimension,
            "warnings": list(self.warnings),
            "documentation_refs": list(self.documentation_refs),
            "branch_statuses": [list(item) for item in self.branch_statuses],
            "details": list(self.details),
            "operator_only": self.operator_only,
            "metadata": dict(self.metadata),
        }


_COMMON_FORMULAS = (
    "Project Artin convention: +i = sigma_i; -i = sigma_i^-1",
    "check-R = P R",
    "rho(sigma_i) = I^(tensor i-1) tensor check-R tensor I^(tensor n-i-1)",
    "F_EYB = alpha^(-w) beta0^(-n) Tr(rho(beta) mu^(tensor n))",
)


def _branch_explanation(branch_id: str) -> MathematicalExplanation:
    descriptor = get_evaluation_branch(branch_id)
    if branch_id == "sl2_fundamental":
        return MathematicalExplanation(
            explanation_id="branch.sl2_fundamental",
            workflow="invariant",
            title=descriptor.display_name,
            status=descriptor.status,
            summary="The formal Jones-compatible path for the fundamental U_q(sl2) representation.",
            formula_lines=(
                "check-R = P R",
                "rho(sigma_i) = I^(tensor i-1) tensor check-R tensor I^(tensor n-i-1)",
                "J_project(beta;q) = F_EYB(beta;q) / F_EYB(unknot;q)",
            ),
            normalization="Dimension 2; mu = diag(q^-1, q), alpha = q^2, beta0 = 1; reduced by the current one-strand unknot value.",
            variable_convention="The maintained project relation is t = q^-2. For the independent Knot Atlas comparison, q_atlas = q_project^2.",
            output_name="Jones-compatible output",
            representation_dimension=2,
            documentation_refs=("docs/MATHEMATICAL_IMPLEMENTATION.md §13", "docs/MATH_CONVENTIONS.md §6"),
            branch_statuses=((descriptor.branch_id, descriptor.status),),
            details=(
                "The closure uses the enhanced trace rather than an ordinary trace alone.",
                "Formal is the maintained project status; it does not claim a new theorem.",
            ),
            metadata={"representation_dimension": 2, "output_name": "Jones-compatible output"},
        )
    if branch_id == "sl3_fundamental":
        return MathematicalExplanation(
            explanation_id="branch.sl3_fundamental",
            workflow="invariant",
            title=descriptor.display_name,
            status=descriptor.status,
            summary="The formal A2/sl3 fundamental path with two tensor channels.",
            formula_lines=(
                "3 tensor 3 = 6 plus 3-bar",
                "rho(sigma_i) = I^(tensor i-1) tensor check-R tensor I^(tensor n-i-1)",
                "F_EYB = alpha^(-w) beta0^(-n) Tr(rho(beta) mu^(tensor n))",
            ),
            normalization="Dimension 3; mu = diag(q^-2, 1, q^2), alpha = q^3, beta0 = 1; current P3-type EYB normalization is exposed without one-strand reduction.",
            variable_convention="The project variable is q. The external A2 comparison uses q_atlas = q_project^-1.",
            output_name="P3-type EYB output",
            representation_dimension=3,
            documentation_refs=("docs/MATHEMATICAL_IMPLEMENTATION.md §16", "docs/MATH_CONVENTIONS.md §6"),
            branch_statuses=((descriptor.branch_id, descriptor.status),),
            details=(
                "The 6 and 3-bar channels describe the local tensor-square decomposition.",
                "Current normalization is intentionally named P3-type EYB output.",
            ),
            metadata={"representation_dimension": 3, "output_name": "P3-type EYB output"},
        )
    if branch_id == "sl2_spin1":
        return MathematicalExplanation(
            explanation_id="branch.sl2_spin1",
            workflow="invariant",
            title=descriptor.display_name,
            status=descriptor.status,
            summary="The maintained 3-dimensional sl2 spin-1 path, shown explicitly as a candidate branch.",
            formula_lines=(
                "3 tensor 3 = 5 plus 3 plus 1",
                "check-R channel eigenvalues: q^4, -1, q^-2",
                "rho(sigma_i) = I^(tensor i-1) tensor check-R tensor I^(tensor n-i-1)",
            ),
            normalization="Dimension 3; mu = diag(q^-2, 1, q^2), alpha = q^4, beta0 = 1; reduced by the one-strand candidate unknot value.",
            variable_convention="The project variable is q. Current external checks inspect Knot Atlas n=2 data via q -> q^2; no final global substitution is fixed.",
            output_name="Colored Jones candidate output",
            representation_dimension=3,
            warnings=(
                "Candidate normalization: not presented as theorem-level formal normalization; this branch is not promoted to a final literature identification or theorem-level claim.",
            ),
            documentation_refs=("docs/MATHEMATICAL_IMPLEMENTATION.md §17", "docs/EXTERNAL_VALIDATION.md §4"),
            branch_statuses=((descriptor.branch_id, descriptor.status),),
            details=(
                "Projector-aware local data and the three spectral channels remain useful diagnostic evidence.",
                "External mismatch is retained as evidence; it does not trigger a silent normalization change.",
            ),
            metadata={"representation_dimension": 3, "output_name": "Colored Jones candidate output"},
        )
    raise ValueError(f"Unsupported explanation branch '{branch_id}'.")


def get_branch_explanation(branch_id: str) -> MathematicalExplanation:
    """Return the maintained explanation for one service branch."""

    return _branch_explanation(branch_id)


def _status_for(statuses: Iterable[str]) -> str:
    unique = tuple(dict.fromkeys(statuses))
    if not unique:
        return "none selected"
    return unique[0] if len(unique) == 1 else "mixed"


def build_invariant_explanation(
    braid_word: BraidWord,
    *,
    branch_ids: tuple[str, ...] | list[str] | None = None,
    source_label: str | None = None,
) -> MathematicalExplanation:
    """Build contextual invariant guidance from the current validated input."""

    selected_ids = (
        ("sl2_fundamental", "sl3_fundamental", "sl2_spin1")
        if branch_ids is None
        else tuple(branch_ids)
    )
    branches = tuple(_branch_explanation(branch_id) for branch_id in selected_ids)
    statuses = tuple(branch.status for branch in branches)
    label = source_label or braid_word.label or "custom braid"
    branch_statuses = tuple(item for branch in branches for item in branch.branch_statuses)
    warnings = tuple(item for branch in branches for item in branch.warnings)
    details = tuple(
        item
        for item in dict.fromkeys(
            (
                f"Current input: {label}; {braid_word.num_strands} strands; generators {list(braid_word.generators)}.",
                f"Writhe w = {braid_word.writhe()}; generator order is preserved exactly in rho(beta).",
                "Negative generators use the inverse local check-R operator.",
                "No invariant branch is currently selected; choose at least one branch before Calculate."
                if not branches
                else "",
                *[f"{branch.title}: {branch.summary}" for branch in branches],
                *[
                    f"{branch.title}: representation dimension {branch.representation_dimension}."
                    for branch in branches
                    if branch.representation_dimension is not None
                ],
                *[detail for branch in branches for detail in branch.details],
            )
        )
        if item
    )
    references = tuple(dict.fromkeys(ref for branch in branches for ref in branch.documentation_refs))
    return MathematicalExplanation(
        explanation_id="workflow.invariant",
        workflow="invariant",
        title=f"How this invariant calculation is formed — {label}",
        status=_status_for(statuses),
        summary=(
            f"The maintained service will interpret this as an ordered {braid_word.num_strands}-strand Artin braid "
            "and apply only the selected branch definitions when Calculate is requested."
        ),
        formula_lines=_COMMON_FORMULAS,
        normalization="Selected branch normalization is listed below; no normalization is inferred from the preview.",
        variable_convention="q is kept exact or symbolic through the service boundary; no floating-point coercion is introduced.",
        output_name=", ".join(dict.fromkeys(branch.output_name for branch in branches if branch.output_name)) or "No branch output selected",
        representation_dimension=(
            next(iter({branch.representation_dimension for branch in branches if branch.representation_dimension}), None)
            if len({branch.representation_dimension for branch in branches if branch.representation_dimension}) == 1
            else None
        ),
        warnings=warnings,
        documentation_refs=references,
        branch_statuses=branch_statuses,
        details=details,
        metadata={
            "strand_count": braid_word.num_strands,
            "writhe": braid_word.writhe(),
            "generators": list(braid_word.generators),
            "source_label": label,
        },
    )


def build_custom_rmatrix_explanation(
    input_kind: str | None,
    *,
    relation_status: str = "not_checked",
) -> MathematicalExplanation:
    """Build operator-only guidance for the custom R/check-R workflow."""

    kind = input_kind if input_kind in {"R", "check-R"} else "R/check-R"
    relation_line = {
        "verified": "Current check-R braid-relation evidence: verified.",
        "failed": "Current check-R braid-relation evidence: failed; this is not a validated braid-group representation.",
        "undecidable": "Current check-R braid-relation evidence: symbolically undecidable.",
        "not_checked": "Current check-R braid-relation evidence: not checked.",
    }.get(relation_status, f"Current check-R braid-relation evidence: {relation_status}.")
    return MathematicalExplanation(
        explanation_id="workflow.custom_rmatrix",
        workflow="custom_rmatrix",
        title=f"How the custom {kind} operator workflow works",
        status="operator-only",
        summary="This workflow constructs and validates braid operators. It never turns an arbitrary matrix into a knot/link invariant.",
        formula_lines=(
            "check-R = P R (for raw R input)",
            "B_i = I^(tensor i-1) tensor check-R tensor I^(tensor n-i-1)",
            "negative generator: B_i^-1",
            "check-R braid relation: B_1 B_2 B_1 = B_2 B_1 B_2",
            "raw-R YBE is a separate test from the check-R braid relation",
        ),
        normalization="None in this workflow: no enhanced trace, Markov/framing correction, or polynomial normalization is applied.",
        variable_convention="Matrix entries are parsed exactly as supplied; this operator workflow does not define an invariant q-variable.",
        output_name="Constructed braid operator matrix (operator-only)",
        warnings=(
            "Operator-only boundary: structural matrix validity and a verified braid relation do not by themselves establish a knot invariant.",
            relation_line,
        ),
        documentation_refs=("docs/CUSTOM_RMATRIX_ENGINE.md", "docs/MATHEMATICAL_IMPLEMENTATION.md §20"),
        branch_statuses=(("custom_rmatrix", "operator-only"),),
        details=(
            "Additional enhancement, weighted trace, Markov normalization, and framing data would be required for an invariant claim.",
            "Input kind is explicit; the UI never guesses whether entries are raw R or check-R.",
        ),
        operator_only=True,
        metadata={"input_kind": input_kind, "relation_status": relation_status},
    )


def get_custom_rmatrix_explanation(input_kind: str | None = None) -> MathematicalExplanation:
    """Compatibility-friendly alias for the custom operator explanation."""

    return build_custom_rmatrix_explanation(input_kind)


__all__ = [
    "MathematicalExplanation",
    "build_custom_rmatrix_explanation",
    "build_invariant_explanation",
    "get_branch_explanation",
    "get_custom_rmatrix_explanation",
]
