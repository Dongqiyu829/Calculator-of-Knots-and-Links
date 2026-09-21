"""Structured audits comparing raw-side and braid-side normalization conventions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

import sympy as sp

from src.catalog.braid_examples import get_braid_example
from src.rmatrix.rmatrix_base import RMatrixData

from .eyb_diagnostics import diagnose_partial_trace, diagnose_stabilization
from .eyb_invariant import EYBData


RMatrixBuilder = Callable[[sp.Expr | None], RMatrixData]
EYBBuilder = Callable[[sp.Expr | None], EYBData]


@dataclass(frozen=True, slots=True)
class RawSideConventionData:
    """Store one raw-side partial-trace candidate convention."""

    representation_name: str
    local_object: str
    mu: sp.Matrix
    alpha_candidate: sp.Expr | None
    beta_candidate: sp.Expr | None
    weight_mode: str
    partial_trace_result: sp.Matrix
    target_matrix: sp.Matrix
    notes: str
    matches_target: bool = False
    scalar_multiple_of_mu: sp.Expr | None = None
    scalar_multiple_of_target: sp.Expr | None = None
    can_recover_braid_alpha_directly: bool = False
    candidate_conversion_rule: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        """Return a readable summary of the raw-side convention candidate."""

        lines = [
            f"Representation: {self.representation_name}",
            f"Local object: {self.local_object}",
            f"Weight mode: {self.weight_mode}",
            f"mu: {self.mu}",
            "alpha candidate: unavailable"
            if self.alpha_candidate is None
            else f"alpha candidate: {sp.simplify(self.alpha_candidate)}",
            "beta candidate: unavailable"
            if self.beta_candidate is None
            else f"beta candidate: {sp.simplify(self.beta_candidate)}",
            f"Partial trace result: {self.partial_trace_result}",
            f"Target matrix: {self.target_matrix}",
            f"Matches target: {self.matches_target}",
            f"Scalar multiple of mu: {self.scalar_multiple_of_mu}",
            f"Scalar multiple of target: {self.scalar_multiple_of_target}",
            f"Can recover braid alpha directly: {self.can_recover_braid_alpha_directly}",
            f"Candidate conversion rule: {self.candidate_conversion_rule or 'none'}",
            f"Notes: {self.notes}",
        ]
        if self.metadata:
            lines.append(f"Metadata: {self.metadata}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Return a structured representation suitable for serialization."""

        return {
            "representation_name": self.representation_name,
            "local_object": self.local_object,
            "mu": [[str(self.mu[row, col]) for col in range(self.mu.cols)] for row in range(self.mu.rows)],
            "alpha_candidate": None if self.alpha_candidate is None else str(sp.simplify(self.alpha_candidate)),
            "beta_candidate": None if self.beta_candidate is None else str(sp.simplify(self.beta_candidate)),
            "weight_mode": self.weight_mode,
            "partial_trace_result": [
                [str(self.partial_trace_result[row, col]) for col in range(self.partial_trace_result.cols)]
                for row in range(self.partial_trace_result.rows)
            ],
            "target_matrix": [
                [str(self.target_matrix[row, col]) for col in range(self.target_matrix.cols)]
                for row in range(self.target_matrix.rows)
            ],
            "notes": self.notes,
            "matches_target": self.matches_target,
            "scalar_multiple_of_mu": None
            if self.scalar_multiple_of_mu is None
            else str(sp.simplify(self.scalar_multiple_of_mu)),
            "scalar_multiple_of_target": None
            if self.scalar_multiple_of_target is None
            else str(sp.simplify(self.scalar_multiple_of_target)),
            "can_recover_braid_alpha_directly": self.can_recover_braid_alpha_directly,
            "candidate_conversion_rule": self.candidate_conversion_rule,
            "metadata": dict(self.metadata),
        }

    def to_string(self) -> str:
        """Return a string form aligned with the summary output."""

        return self.summary()


@dataclass(frozen=True, slots=True)
class BraidSideConventionData:
    """Store the current working braid-side convention."""

    representation_name: str
    local_object: str
    mu: sp.Matrix
    alpha: sp.Expr
    beta: sp.Expr
    stabilization_verified: bool
    notes: str
    checked_examples: tuple[str, ...] = ()
    positive_ratios: dict[str, str] = field(default_factory=dict)
    negative_ratios: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        """Return a readable summary of the braid-side convention."""

        lines = [
            f"Representation: {self.representation_name}",
            f"Local object: {self.local_object}",
            f"mu: {self.mu}",
            f"alpha: {sp.simplify(self.alpha)}",
            f"beta: {sp.simplify(self.beta)}",
            f"Stabilization verified: {self.stabilization_verified}",
            f"Checked examples: {list(self.checked_examples)}",
            f"Positive ratios: {self.positive_ratios}",
            f"Negative ratios: {self.negative_ratios}",
            f"Notes: {self.notes}",
        ]
        if self.metadata:
            lines.append(f"Metadata: {self.metadata}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Return a structured representation suitable for serialization."""

        return {
            "representation_name": self.representation_name,
            "local_object": self.local_object,
            "mu": [[str(self.mu[row, col]) for col in range(self.mu.cols)] for row in range(self.mu.rows)],
            "alpha": str(sp.simplify(self.alpha)),
            "beta": str(sp.simplify(self.beta)),
            "stabilization_verified": self.stabilization_verified,
            "checked_examples": list(self.checked_examples),
            "positive_ratios": dict(self.positive_ratios),
            "negative_ratios": dict(self.negative_ratios),
            "notes": self.notes,
            "metadata": dict(self.metadata),
        }

    def to_string(self) -> str:
        """Return a string form aligned with the summary output."""

        return self.summary()


@dataclass(frozen=True, slots=True)
class ConventionComparisonResult:
    """Store the comparison between raw-side and braid-side conventions."""

    representation_name: str
    raw_side_summary: str
    braid_side_summary: str
    do_they_match_directly: bool
    difference_explanation: str
    candidate_conversion_rule: str
    notes: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        """Return a readable summary of the convention comparison."""

        lines = [
            f"Representation: {self.representation_name}",
            f"Do they match directly: {self.do_they_match_directly}",
            f"Difference explanation: {self.difference_explanation}",
            f"Candidate conversion rule: {self.candidate_conversion_rule or 'none'}",
            f"Notes: {self.notes}",
            "Raw-side summary:",
            self.raw_side_summary,
            "Braid-side summary:",
            self.braid_side_summary,
        ]
        if self.metadata:
            lines.append(f"Metadata: {self.metadata}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Return a structured representation suitable for serialization."""

        return {
            "representation_name": self.representation_name,
            "raw_side_summary": self.raw_side_summary,
            "braid_side_summary": self.braid_side_summary,
            "do_they_match_directly": self.do_they_match_directly,
            "difference_explanation": self.difference_explanation,
            "candidate_conversion_rule": self.candidate_conversion_rule,
            "notes": self.notes,
            "metadata": dict(self.metadata),
        }

    def to_string(self) -> str:
        """Return a string form aligned with the summary output."""

        return self.summary()


def build_raw_side_convention_data(
    *,
    rmatrix_builder: RMatrixBuilder,
    eyb_builder: EYBBuilder,
    local_object: str,
    weight_mode: str,
    q: sp.Expr | None = None,
) -> RawSideConventionData:
    """Build one raw-side convention candidate from a partial-trace diagnostic."""

    diagnostic = diagnose_partial_trace(
        rmatrix_builder=rmatrix_builder,
        eyb_builder=eyb_builder,
        local_object_label=local_object,
        weight_mode=weight_mode,
        target_label="mu",
        q=q,
    )
    rmatrix = rmatrix_builder(q)
    eyb_data = eyb_builder(q)

    if diagnostic.scalar_multiple_of_mu is not None:
        alpha_candidate = sp.simplify(diagnostic.scalar_multiple_of_mu)
        candidate_conversion_rule = (
            "raw partial trace gives scalar(q) * mu with scalar(q) = q + dim(V) - 1; "
            "this is a Hecke-type raw-side trace scalar, not the current braid-side alpha directly."
            if sp.simplify(alpha_candidate - (sp.Symbol("q", nonzero=True) + rmatrix.rep.dimension - 1)) == 0
            else "raw partial trace gives a scalar multiple of mu, but it does not directly coincide with braid-side alpha."
        )
    else:
        alpha_candidate = None
        candidate_conversion_rule = "No scalar-times-mu rule is visible for this raw-side combination."

    can_recover_braid_alpha_directly = (
        alpha_candidate is not None and sp.simplify(alpha_candidate - eyb_data.alpha) == 0
    )
    notes = (
        "This object records one raw-side candidate convention based on partial trace. "
        "It does not assume direct equality with the current braid-side normalization."
    )
    return RawSideConventionData(
        representation_name=diagnostic.representation_name,
        local_object=local_object,
        mu=diagnostic.mu,
        alpha_candidate=alpha_candidate,
        beta_candidate=sp.Integer(1) if alpha_candidate is not None else None,
        weight_mode=weight_mode,
        partial_trace_result=diagnostic.partial_trace_matrix,
        target_matrix=diagnostic.target_matrix,
        notes=notes,
        matches_target=diagnostic.matches_target,
        scalar_multiple_of_mu=diagnostic.scalar_multiple_of_mu,
        scalar_multiple_of_target=diagnostic.scalar_multiple_of_target,
        can_recover_braid_alpha_directly=can_recover_braid_alpha_directly,
        candidate_conversion_rule=candidate_conversion_rule,
        metadata={
            "partial_trace_difference": diagnostic.to_dict()["difference_matrix"],
            "raw_diagnostic_metadata": diagnostic.metadata,
        },
    )


def build_braid_side_convention_data(
    *,
    rmatrix_builder: RMatrixBuilder,
    eyb_builder: EYBBuilder,
    local_object: str = "braid_matrix",
    example_labels: tuple[str, ...] = ("unknot_1", "trefoil", "figure_eight"),
    q: sp.Expr | None = None,
) -> BraidSideConventionData:
    """Build the current working braid-side convention summary."""

    eyb_data = eyb_builder(q)
    diagnostics = [
        diagnose_stabilization(
            get_braid_example(label),
            rmatrix_builder=rmatrix_builder,
            eyb_builder=eyb_builder,
            local_object_label=local_object,
            q=q,
        )
        for label in example_labels
    ]
    stabilization_verified = all(item.positive_is_one and item.negative_is_one for item in diagnostics)
    return BraidSideConventionData(
        representation_name=diagnostics[0].representation_name,
        local_object=local_object,
        mu=eyb_data.mu,
        alpha=eyb_data.alpha,
        beta=eyb_data.beta,
        stabilization_verified=stabilization_verified,
        notes=(
            "This is the current braid-side working convention. Its role is implementation-facing: it is the "
            "normalization that has been empirically verified against conjugation and stabilization regression tests."
        ),
        checked_examples=example_labels,
        positive_ratios={item.example_label: str(sp.simplify(item.positive_ratio)) for item in diagnostics},
        negative_ratios={item.example_label: str(sp.simplify(item.negative_ratio)) for item in diagnostics},
        metadata={"stabilization_diagnostics": [item.to_dict() for item in diagnostics]},
    )


def compare_raw_and_braid_side_conventions(
    *,
    rmatrix_builder: RMatrixBuilder,
    eyb_builder: EYBBuilder,
    q: sp.Expr | None = None,
) -> ConventionComparisonResult:
    """Compare the best raw-side candidate against the current braid-side convention."""

    q_parameter = q if q is not None else sp.Symbol("q", nonzero=True)
    raw_candidates = [
        build_raw_side_convention_data(
            rmatrix_builder=rmatrix_builder,
            eyb_builder=eyb_builder,
            local_object=local_object,
            weight_mode=weight_mode,
            q=q_parameter,
        )
        for local_object, weight_mode in [
            ("raw_matrix", "mu_kron_identity"),
            ("raw_matrix", "identity_kron_mu"),
            ("raw_matrix", "mu_kron_mu"),
            ("braid_matrix", "mu_kron_mu"),
            ("braid_matrix_inverse", "mu_kron_mu"),
        ]
    ]
    braid_side = build_braid_side_convention_data(
        rmatrix_builder=rmatrix_builder,
        eyb_builder=eyb_builder,
        local_object="braid_matrix",
        q=q_parameter,
    )

    best_raw = next((candidate for candidate in raw_candidates if candidate.scalar_multiple_of_mu is not None), raw_candidates[0])
    direct_match = best_raw.alpha_candidate is not None and sp.simplify(best_raw.alpha_candidate - braid_side.alpha) == 0
    difference_explanation = (
        "The raw-side best candidate is scalar(q) * mu with scalar(q) = q + dim(V) - 1, while the braid-side "
        "working alpha is q^dim(V). They use the same deformation parameter q but are not the same scalar."
        if best_raw.scalar_multiple_of_mu is not None
        else "No raw-side candidate among the audited combinations produced a scalar multiple of mu."
    )
    candidate_conversion_rule = (
        "No direct equality alpha_raw = alpha_braid is present in the current audit. The most reasonable current "
        "interpretation is that raw-side partial trace records a Hecke-type trace scalar q + dim(V) - 1, whereas "
        "braid-side alpha is a separately calibrated monomial q^dim(V) chosen to make the implemented stabilization "
        "ratios equal 1."
        if best_raw.scalar_multiple_of_mu is not None
        else "No candidate conversion rule is visible from the audited combinations."
    )
    return ConventionComparisonResult(
        representation_name=braid_side.representation_name,
        raw_side_summary=best_raw.summary(),
        braid_side_summary=braid_side.summary(),
        do_they_match_directly=direct_match,
        difference_explanation=difference_explanation,
        candidate_conversion_rule=candidate_conversion_rule,
        notes=(
            "This comparison is intentionally layered: the current braid-side normalization is treated as the "
            "project's formal working convention, while the raw-side partial-trace data is retained as a separate "
            "theoretical audit trail."
        ),
        metadata={
            "all_raw_candidates": [candidate.to_dict() for candidate in raw_candidates],
            "best_raw_candidate_local_object": best_raw.local_object,
            "best_raw_candidate_weight_mode": best_raw.weight_mode,
            "braid_side_data": braid_side.to_dict(),
        },
    )