"""Diagnostic helpers for EYB convention audits and stabilization checks."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Callable

import sympy as sp

from src.braid.braid_operator import BraidOperatorBuilder
from src.catalog.braid_examples import BraidExample
from src.rmatrix.rmatrix_base import RMatrixData, swap_operator

from .eyb_invariant import EYBData, compute_eyb_invariant


RMatrixBuilder = Callable[[sp.Expr | None], RMatrixData]
EYBBuilder = Callable[[sp.Expr | None], EYBData]


def _matrix_to_string_grid(matrix: sp.Matrix) -> list[list[str]]:
    """Convert a SymPy matrix into a nested list of string entries."""

    return [[str(matrix[row, col]) for col in range(matrix.cols)] for row in range(matrix.rows)]


def partial_trace_second(matrix: sp.Matrix, local_dim: int) -> sp.Matrix:
    """Return the partial trace over the second tensor factor."""

    output = sp.zeros(local_dim)
    for row in range(local_dim):
        for col in range(local_dim):
            entry = sp.Integer(0)
            for traced_index in range(local_dim):
                entry += matrix[row * local_dim + traced_index, col * local_dim + traced_index]
            output[row, col] = sp.simplify(entry)
    return sp.simplify(output)


def scalar_multiple_if_any(left: sp.Matrix, right: sp.Matrix) -> sp.Expr | None:
    """Return the scalar c such that left = c right when such c exists."""

    for row in range(right.rows):
        for col in range(right.cols):
            if sp.simplify(right[row, col]) != 0:
                candidate = sp.simplify(left[row, col] / right[row, col])
                if sp.simplify(left - candidate * right) == sp.zeros(*left.shape):
                    return candidate
                return None
    return None


def _clone_eyb_data(
    eyb_data: EYBData,
    *,
    alpha_factor: sp.Expr = sp.Integer(1),
    beta_factor: sp.Expr = sp.Integer(1),
) -> EYBData:
    """Return a copy of EYBData with optional alpha and beta rescaling."""

    return EYBData(
        representation_name=eyb_data.representation_name,
        mu=eyb_data.mu,
        alpha=sp.simplify(alpha_factor * eyb_data.alpha),
        beta=sp.simplify(beta_factor * eyb_data.beta),
        output_label=eyb_data.output_label,
        convention_notes=eyb_data.convention_notes,
        notes=eyb_data.notes,
        metadata=dict(eyb_data.metadata),
    )


def _select_local_object(rmatrix: RMatrixData, local_object_label: str) -> sp.Matrix:
    """Return the requested local operator candidate."""

    swap = swap_operator(rmatrix.rep.dimension)
    if local_object_label == "braid_matrix":
        return rmatrix.braid_matrix
    if local_object_label == "braid_matrix_inverse":
        return sp.simplify(rmatrix.braid_matrix.inv())
    if local_object_label == "raw_matrix":
        return rmatrix.matrix
    if local_object_label == "raw_matrix_inverse":
        return sp.simplify(rmatrix.matrix.inv())
    if local_object_label == "swap_left_raw":
        return sp.simplify(swap * rmatrix.matrix)
    if local_object_label == "swap_right_raw":
        return sp.simplify(rmatrix.matrix * swap)
    raise ValueError(f"Unknown local object label: {local_object_label}")


def _select_weight_matrix(mu: sp.Matrix, weight_mode: str) -> sp.Matrix:
    """Return the requested weight insertion on V tensor V."""

    identity = sp.eye(mu.rows)
    if weight_mode == "identity_kron_mu":
        return sp.kronecker_product(identity, mu)
    if weight_mode == "mu_kron_identity":
        return sp.kronecker_product(mu, identity)
    if weight_mode == "mu_kron_mu":
        return sp.kronecker_product(mu, mu)
    raise ValueError(f"Unknown weight mode: {weight_mode}")


def _target_matrix(eyb_data: EYBData, target_label: str) -> sp.Matrix:
    """Return the requested target matrix for partial-trace comparison."""

    if target_label == "alpha_beta_mu":
        return sp.simplify(eyb_data.alpha * eyb_data.beta * eyb_data.mu)
    if target_label == "alpha_inverse_beta_mu":
        return sp.simplify(eyb_data.alpha ** -1 * eyb_data.beta * eyb_data.mu)
    if target_label == "mu":
        return sp.simplify(eyb_data.mu)
    raise ValueError(f"Unknown target label: {target_label}")


@dataclass(frozen=True, slots=True)
class PartialTraceDiagnostic:
    """Store one structured EYB partial-trace diagnostic result."""

    representation_name: str
    local_object_label: str
    weight_mode: str
    target_label: str
    mu: sp.Matrix
    alpha: sp.Expr
    beta: sp.Expr
    partial_trace_matrix: sp.Matrix
    target_matrix: sp.Matrix
    difference_matrix: sp.Matrix
    matches_target: bool
    scalar_multiple_of_target: sp.Expr | None
    scalar_multiple_of_mu: sp.Expr | None
    scalar_multiple_of_identity: sp.Expr | None
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        """Return a readable summary of the diagnostic."""

        lines = [
            f"Representation: {self.representation_name}",
            f"Chosen local object: {self.local_object_label}",
            f"Weight mode: {self.weight_mode}",
            f"Target label: {self.target_label}",
            f"mu: {self.mu}",
            f"alpha: {sp.simplify(self.alpha)}",
            f"beta: {sp.simplify(self.beta)}",
            f"Partial trace matrix: {self.partial_trace_matrix}",
            f"Target matrix: {self.target_matrix}",
            f"Matches target: {self.matches_target}",
            f"Difference matrix: {self.difference_matrix}",
            f"Scalar multiple of target: {self.scalar_multiple_of_target}",
            f"Scalar multiple of mu: {self.scalar_multiple_of_mu}",
            f"Scalar multiple of identity: {self.scalar_multiple_of_identity}",
        ]
        if self.notes:
            lines.append(f"Notes: {self.notes}")
        if self.metadata:
            lines.append(f"Metadata: {self.metadata}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Return a structured representation suitable for serialization."""

        return {
            "representation_name": self.representation_name,
            "local_object_label": self.local_object_label,
            "weight_mode": self.weight_mode,
            "target_label": self.target_label,
            "mu": _matrix_to_string_grid(self.mu),
            "alpha": str(sp.simplify(self.alpha)),
            "beta": str(sp.simplify(self.beta)),
            "partial_trace_matrix": _matrix_to_string_grid(self.partial_trace_matrix),
            "target_matrix": _matrix_to_string_grid(self.target_matrix),
            "difference_matrix": _matrix_to_string_grid(self.difference_matrix),
            "matches_target": self.matches_target,
            "scalar_multiple_of_target": None
            if self.scalar_multiple_of_target is None
            else str(sp.simplify(self.scalar_multiple_of_target)),
            "scalar_multiple_of_mu": None
            if self.scalar_multiple_of_mu is None
            else str(sp.simplify(self.scalar_multiple_of_mu)),
            "scalar_multiple_of_identity": None
            if self.scalar_multiple_of_identity is None
            else str(sp.simplify(self.scalar_multiple_of_identity)),
            "notes": self.notes,
            "metadata": dict(self.metadata),
        }

    def to_string(self) -> str:
        """Return a string form aligned with the summary output."""

        return self.summary()


@dataclass(frozen=True, slots=True)
class StabilizationDiagnostic:
    """Store one structured stabilization-ratio diagnostic result."""

    example_label: str
    representation_name: str
    local_object_label: str
    alpha: sp.Expr
    beta: sp.Expr
    braid_word: str
    t_beta: sp.Expr
    t_positive: sp.Expr
    t_negative: sp.Expr
    positive_ratio: sp.Expr
    negative_ratio: sp.Expr
    positive_is_one: bool
    negative_is_one: bool
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        """Return a readable summary of the stabilization diagnostic."""

        lines = [
            f"Example label: {self.example_label}",
            f"Representation: {self.representation_name}",
            f"Chosen local object: {self.local_object_label}",
            f"Braid word: {self.braid_word}",
            f"alpha: {sp.simplify(self.alpha)}",
            f"beta: {sp.simplify(self.beta)}",
            f"T(beta): {sp.simplify(self.t_beta)}",
            f"T(beta sigma_n): {sp.simplify(self.t_positive)}",
            f"T(beta sigma_n^-1): {sp.simplify(self.t_negative)}",
            f"Positive ratio: {sp.simplify(self.positive_ratio)}",
            f"Negative ratio: {sp.simplify(self.negative_ratio)}",
            f"Positive ratio equals 1: {self.positive_is_one}",
            f"Negative ratio equals 1: {self.negative_is_one}",
        ]
        if self.notes:
            lines.append(f"Notes: {self.notes}")
        if self.metadata:
            lines.append(f"Metadata: {self.metadata}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Return a structured representation suitable for serialization."""

        return {
            "example_label": self.example_label,
            "representation_name": self.representation_name,
            "local_object_label": self.local_object_label,
            "alpha": str(sp.simplify(self.alpha)),
            "beta": str(sp.simplify(self.beta)),
            "braid_word": self.braid_word,
            "t_beta": str(sp.simplify(self.t_beta)),
            "t_positive": str(sp.simplify(self.t_positive)),
            "t_negative": str(sp.simplify(self.t_negative)),
            "positive_ratio": str(sp.simplify(self.positive_ratio)),
            "negative_ratio": str(sp.simplify(self.negative_ratio)),
            "positive_is_one": self.positive_is_one,
            "negative_is_one": self.negative_is_one,
            "notes": self.notes,
            "metadata": dict(self.metadata),
        }

    def to_string(self) -> str:
        """Return a string form aligned with the summary output."""

        return self.summary()


def make_local_object_variant(rmatrix: RMatrixData, local_object_label: str) -> RMatrixData:
    """Return an RMatrixData copy whose braid generator uses the requested local object."""

    local_object = _select_local_object(rmatrix, local_object_label)
    return replace(
        rmatrix,
        braid_matrix=sp.simplify(local_object),
        convention_notes=f"{rmatrix.convention_notes} local_object_variant={local_object_label}",
    )


def diagnose_partial_trace(
    *,
    rmatrix_builder: RMatrixBuilder,
    eyb_builder: EYBBuilder,
    local_object_label: str = "braid_matrix",
    weight_mode: str = "mu_kron_mu",
    target_label: str = "alpha_beta_mu",
    alpha_factor: sp.Expr = sp.Integer(1),
    beta_factor: sp.Expr = sp.Integer(1),
    q: sp.Expr | None = None,
) -> PartialTraceDiagnostic:
    """Compute one structured partial-trace diagnostic."""

    parameter = q if q is not None else sp.Symbol("q", nonzero=True)
    rmatrix = rmatrix_builder(parameter)
    eyb_data = _clone_eyb_data(eyb_builder(parameter), alpha_factor=alpha_factor, beta_factor=beta_factor)
    local_object = _select_local_object(rmatrix, local_object_label)
    weight = _select_weight_matrix(eyb_data.mu, weight_mode)
    lhs = partial_trace_second(sp.simplify(local_object * weight), rmatrix.rep.dimension)
    target = _target_matrix(eyb_data, target_label)
    difference = sp.simplify(lhs - target)
    swap = swap_operator(rmatrix.rep.dimension)

    notes = (
        "Full-trace placement of mu^(tensor n) on the left or right is not a source of mismatch here, because "
        "trace(AB) = trace(BA) by cyclicity. The nontrivial diagnostic signal comes from the partial-trace side."
    )
    return PartialTraceDiagnostic(
        representation_name=rmatrix.rep.name(),
        local_object_label=local_object_label,
        weight_mode=weight_mode,
        target_label=target_label,
        mu=eyb_data.mu,
        alpha=eyb_data.alpha,
        beta=eyb_data.beta,
        partial_trace_matrix=lhs,
        target_matrix=target,
        difference_matrix=difference,
        matches_target=difference == sp.zeros(*difference.shape),
        scalar_multiple_of_target=scalar_multiple_if_any(lhs, target),
        scalar_multiple_of_mu=scalar_multiple_if_any(lhs, eyb_data.mu),
        scalar_multiple_of_identity=scalar_multiple_if_any(lhs, sp.eye(rmatrix.rep.dimension)),
        notes=notes,
        metadata={
            "local_object_shape": list(local_object.shape),
            "swap_left_equals_braid_matrix": sp.simplify(swap * rmatrix.matrix - rmatrix.braid_matrix)
            == sp.zeros(*rmatrix.braid_matrix.shape),
            "swap_right_equals_braid_matrix": sp.simplify(rmatrix.matrix * swap - rmatrix.braid_matrix)
            == sp.zeros(*rmatrix.braid_matrix.shape),
        },
    )


def diagnose_stabilization(
    example: BraidExample,
    *,
    rmatrix_builder: RMatrixBuilder,
    eyb_builder: EYBBuilder,
    local_object_label: str = "braid_matrix",
    alpha_factor: sp.Expr = sp.Integer(1),
    beta_factor: sp.Expr = sp.Integer(1),
    q: sp.Expr | None = None,
) -> StabilizationDiagnostic:
    """Compute the positive and negative stabilization ratios for one example."""

    parameter = q if q is not None else sp.Symbol("q", nonzero=True)
    base_rmatrix = rmatrix_builder(parameter)
    rmatrix = make_local_object_variant(base_rmatrix, local_object_label)
    eyb_data = _clone_eyb_data(eyb_builder(parameter), alpha_factor=alpha_factor, beta_factor=beta_factor)

    braid_word = example.to_braid_word()
    positive = example.to_braid_word().from_iterable(
        num_strands=braid_word.num_strands + 1,
        generators=list(braid_word.generators) + [braid_word.num_strands],
        label=f"{example.label} positive stabilization",
        notes="Positive Markov stabilization used in EYB diagnostics.",
    )
    negative = example.to_braid_word().from_iterable(
        num_strands=braid_word.num_strands + 1,
        generators=list(braid_word.generators) + [-braid_word.num_strands],
        label=f"{example.label} negative stabilization",
        notes="Negative Markov stabilization used in EYB diagnostics.",
    )

    t_beta = compute_eyb_invariant(BraidOperatorBuilder(braid_word=braid_word, rmatrix=rmatrix).build(), eyb_data=eyb_data)
    t_positive = compute_eyb_invariant(BraidOperatorBuilder(braid_word=positive, rmatrix=rmatrix).build(), eyb_data=eyb_data)
    t_negative = compute_eyb_invariant(BraidOperatorBuilder(braid_word=negative, rmatrix=rmatrix).build(), eyb_data=eyb_data)

    positive_ratio = sp.simplify(t_positive.eyb_normalized_expression / t_beta.eyb_normalized_expression)
    negative_ratio = sp.simplify(t_negative.eyb_normalized_expression / t_beta.eyb_normalized_expression)
    return StabilizationDiagnostic(
        example_label=example.label,
        representation_name=rmatrix.rep.name(),
        local_object_label=local_object_label,
        alpha=eyb_data.alpha,
        beta=eyb_data.beta,
        braid_word=braid_word.word_string(),
        t_beta=t_beta.eyb_normalized_expression,
        t_positive=t_positive.eyb_normalized_expression,
        t_negative=t_negative.eyb_normalized_expression,
        positive_ratio=positive_ratio,
        negative_ratio=negative_ratio,
        positive_is_one=sp.simplify(positive_ratio - 1) == 0,
        negative_is_one=sp.simplify(negative_ratio - 1) == 0,
        notes=(
            "If both ratios equal 1, the current EYB data is empirically compatible with Markov stabilization for "
            "this local-object choice."
        ),
        metadata={
            "trace_left_right_equal_for_beta": True,
            "trace_left_right_equal_for_positive": True,
            "trace_left_right_equal_for_negative": True,
        },
    )
